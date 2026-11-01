import pandas as pd, numpy as np, glob, json
P="data/local_market/1c85fd9aceaa03c3c4863bec/panels/"
C=["tradestatus","open_status","is_st_at_open","limit_up","limit_down","amount","turnover"]
fm=pd.read_parquet("data/v2/float_mktcap/float_mktcap_daily_tushare.parquet",columns=["instrument_id","trade_date","float_mktcap"])
fm["trade_date"]=pd.to_datetime(fm.trade_date); fmk=set(zip(fm.instrument_id,fm.trade_date))
dv=pd.read_parquet("data/v2/corporate_actions/dividend_tushare.parquet")
dv=dv[dv.div_proc.str.strip()=="实施"].dropna(subset=["ex_date"]).copy()
dv["iid"]=dv.ts_code.str[-2:].str.lower()+"."+dv.ts_code.str[:6]; dv["ex"]=pd.to_datetime(dv.ex_date)
for c in ["cash_div_tax","stk_div"]: dv[c]=pd.to_numeric(dv[c],errors="coerce").fillna(0)
dv=dv.groupby(["iid","ex"])[["cash_div_tax","stk_div"]].sum()
cov=[];rec=[]
for f in glob.glob(P+"*.parquet"):
    iid=f.split("/")[-1][:-8]; p=pd.read_parquet(f)
    if not isinstance(p.index,pd.DatetimeIndex): continue
    p["prev_close"]=p.close.shift(1)
    u=p[p.unexplained_ex_reference.notna()] if "unexplained_ex_reference" in p else p.iloc[:0]
    for t,r in u.iterrows():
        k=(iid,pd.Timestamp(t).normalize()); 
        if k in dv.index:
            c,s=dv.loc[k]; imp=(r.prev_close-c)/(1+s); st="explained_by_dividend" if abs(imp-r.reference_price)<=max(0.011,0.002*r.reference_price) else "dividend_found_price_mismatch"
        else: imp=np.nan; st="no_tushare_dividend_on_date"
        rec.append((iid,t,r.prev_close,r.reference_price,r.unexplained_ex_reference,imp,st))
    q=p[p.index>="2018-01-01"].copy()
    if q.empty: continue
    q["open_status"]=q.open_status.where(~q.open_status.isin(["unknown",""]))
    q["float_mktcap"]=[ (iid,pd.Timestamp(t).normalize()) in fmk for t in q.index]; q["float_mktcap"]=q.float_mktcap.map({True:1.0,False:np.nan})
    g=q.groupby(q.index.year); r=g[C+["float_mktcap"]].count(); r["rows"]=g.size(); cov.append(r)
t=pd.concat(cov).groupby(level=0).sum()
pct=(t[C+["float_mktcap"]].div(t.rows,axis=0)*100).round(2); pct.insert(0,"rows",t.rows)
R=pd.DataFrame(rec,columns=["instrument_id","session","prev_close","reference_price","unexplained_val","implied_ref_tushare","status"])
R.to_parquet("data/v2/corporate_actions/exrights_unexplained_recheck_tushare.parquet",index=False)
out={"d0_cov_pct":pct.to_dict("index"),"recheck_total":len(R),"recheck_status":R.status.value_counts().to_dict(),
     "recheck_by_year":R.assign(y=pd.to_datetime(R.session).dt.year).groupby(["y","status"]).size().unstack(fill_value=0).to_dict("index")}
json.dump(out,open("output/d1/alpha_d0_checks.json","w"),default=str,ensure_ascii=False,indent=1)
print(pct.to_string()); print(out["recheck_total"],out["recheck_status"])
