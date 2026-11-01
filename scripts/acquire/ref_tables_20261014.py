#!/usr/bin/env python3
"""只读参考表(研究级 promotion_approved=false; 0 relay 请求): ETF 参考 / 月度 PIT 池锚点 / 个股退市表.
输入 /tmp/fbE_*.parquet /tmp/sbD.parquet 来自 datahub fund_basic(market=E,status=L/D) 与 stock_basic(list_status=D) 2026-10-14."""
import re,json,hashlib,pathlib,datetime,pandas as pd,numpy as np
R=pathlib.Path("/workspace/QuantLab"); NOW=datetime.datetime.now().isoformat(timespec="seconds")
sha=lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def man(p,**kw):
    kw.update(path=str(p.relative_to(R)),sha256=sha(p),built_at_et=NOW,promotion_approved=False)
    json.dump(kw,open(str(p).replace(".parquet","_manifest.json"),"w"),ensure_ascii=False,indent=1,default=str); return kw
out={}
# ---------- 1 ETF ----------
f=pd.concat([pd.read_parquet("/tmp/fbE_L.parquet"),pd.read_parquet("/tmp/fbE_D.parquet")],ignore_index=True).drop_duplicates("ts_code")
code=f.ts_code.str[:6]
f["is_etf"]=f.name.str.contains("ETF",case=False,na=False)|code.str.match(r"^(51|56|58|15|16[0-9]{4}$)")&f.name.str.contains("ETF",na=False)
f=f[f.name.str.contains("ETF",case=False,na=False)].copy()
def cat(r):
    t=f"{r['name']} {r['benchmark'] or ''} {r['invest_type'] or ''} {r['fund_type'] or ''}"
    if r["fund_type"]=="货币型" or "货币" in t: return "货币"
    if r["fund_type"]=="债券型" or re.search(r"债|利率|信用",str(r["name"])): return "债券"
    if re.search(r"黄金|白银|有色金属期货|豆粕|能源化工|原油|商品",t): return "商品"
    if re.search(r"纳斯达克|纳指|标普|日经|德国|法国|恒生|港股|香港|中概|H股|美国|海外|全球|亚太|沙特|东南亚|巴西|QDII|日本|中韩|MSCI中国",t): return "跨境"
    if re.search(r"沪深300|中证500|中证1000|中证800|上证50|上证180|科创50|科创100|创业板|深证100|深证成|中证A50|A500|中证2000|上证综|双创|国证2000|MSCI|中证100|红利|价值|成长|基本面|等权|央企|国企",str(r["name"])):
        return "宽基/策略" if re.search(r"红利|价值|成长|基本面|低波|等权|央企|国企|质量|ESG",str(r["name"])) else "宽基"
    if re.search(r"银行|证券|券商|保险|非银|医药|医疗|生物|酒|消费|食品|家电|汽车|电力|煤炭|钢铁|有色|化工|建材|地产|房地产|军工|传媒|计算机|通信|电子|半导体|芯片|农业|养殖|畜牧|交运|物流|机械|建筑|公用|基建|旅游",str(r["name"])): return "行业"
    return "主题"
f["category"]=f.apply(cat,axis=1)
f["track_index"]=f.benchmark.fillna("").str.replace(r"(收益率)?[×*]\s*\d+(\.\d+)?%.*$","",regex=True).str.strip()
e=f.rename(columns={"management":"manager"})[["ts_code","name","category","track_index","benchmark","manager","custodian","fund_type","invest_type","found_date","list_date","delist_date","status"]].sort_values("ts_code")
e["source"]="datahub fund_basic market=E (status L+D), filtered name~ETF"; e["promotion_approved"]=False
assert (e.ts_code=="510300.SH").any()
P=R/"data/v2/ref"; P.mkdir(exist_ok=True); p=P/"etf_basic.parquet"; e.to_parquet(p,index=False)
out["etf"]=man(p,rows=len(e),n_listed=int((e.status=="L").sum()),category_counts=e.category.value_counts().to_dict(),row_510300=e[e.ts_code=="510300.SH"].iloc[0].to_dict())
# ---------- 3a 月度锚点 ----------
U=R/"data/v2/universe"; d=pd.read_parquet(U/"mid_large_members_pit.parquet",columns=["session","instrument_id","float_mktcap_basis","basis_trade_date","available_at"])
s=pd.Series(sorted(d.session.unique())); me=s.groupby(s.str[:7]).max()
last=s.iloc[-1]; complete=me[me!=last] if last[:7]==me.index[-1] and last<me.iloc[-1] else me
me_df=pd.DataFrame({"month":me.index,"anchor_session":me.values})
me_df["month_complete"]=me_df.anchor_session.map(lambda x: not (x==last and x[:7]==last[:7]))
a=d[d.session.isin(me.values)].merge(me_df,left_on="session",right_on="anchor_session").drop(columns="session")
a["rank_mcap"]=a.groupby("anchor_session").float_mktcap_basis.rank(ascending=False,method="first").astype(int)
a["in_top300"]=a.rank_mcap<=300; a["universe_id"]="mid_large"; a["promotion_approved"]=False
a=a.sort_values(["anchor_session","rank_mcap"])
p1=U/"mid_large_month_end_anchor_pit.parquet"; a.to_parquet(p1,index=False)
out["anchor"]=man(p1,rows=len(a),months=[me.index[0],me.index[-1]],n_months=len(me),last_anchor=last,last_month_partial=bool(not me_df.month_complete.iloc[-1]),
  rule="每月最后一个 mid_large session 的全部成员; rank_mcap 按 float_mktcap_basis(前一交易日) 降序; available_at=锚点 session 09:00 上海")
t=a[a.in_top300].copy(); t["universe_id"]="mid_large_top300_monthly"
p2=U/"mid_large_top300_monthly_pit.parquet"; t.to_parquet(p2,index=False)
out["top300"]=man(p2,rows=len(t),n_months=int(t.anchor_session.nunique()),
  rule="复刻 select_mid_large_topn_light(anchor=2024-06-28) 的排序(float_mktcap_basis 降序 top300)但逐月重算; 未做 D0 panel 存在性过滤(该过滤依赖研究侧 panel 目录,由 AI/Arch 在使用端加)",
  check_20240628=dict(in_month_end=bool("2024-06-28" in set(t.anchor_session))))
# ---------- 3b 退市表 ----------
m=pd.read_parquet(R/"data/v2/delisted/delisted_master_tushare.parquet"); sb=pd.read_parquet("/tmp/sbD.parquet")
nc=pd.read_parquet(R/"data/v2/st_events/namechange_all.parquet")
tui=nc[nc.name.str.endswith("退",na=False)].groupby("ts_code").start_date.min().rename("delisting_period_start")
dd=pd.read_parquet(R/"data/v2/delisted/delisted_daily_tushare.parquet",columns=["ts_code","trade_date","close","adj_factor"])
dd["trade_date"]=dd.trade_date.astype(str).str.replace("-","").str[:8]
x=sb[["ts_code","name","market","exchange","list_date","delist_date"]].merge(m[["ts_code","instrument_id","last_trade_date","last_close","last_adj_factor","gap_days_last_trade_to_delist","was_st_within_1y_of_delist","delist_reason_category","last_names"]],on="ts_code",how="left").merge(tui,on="ts_code",how="left")
x["entered_delisting_period"]=x.delisting_period_start.notna()
def ndays(r):
    if not r.entered_delisting_period: return 0
    g=dd[(dd.ts_code==r.ts_code)&(dd.trade_date>=r.delisting_period_start)]; return len(g)
x["delisting_period_trade_days"]=x.apply(ndays,axis=1)
x["delist_price"]=x.last_close; x["delist_price_basis"]="最后交易日不复权收盘价(退市整理期末日收盘即退市价; Tushare 无独立退市价字段)"
x["available_at"]=pd.to_datetime(x.delist_date.astype(str),format="%Y%m%d",errors="coerce")-pd.Timedelta(days=0)
x["promotion_approved"]=False
p3=R/"data/v2/ref/stock_delisted.parquet"; x.to_parquet(p3,index=False)
out["delist"]=man(p3,rows=len(x),n_with_last_trade=int(x.last_trade_date.notna().sum()),n_entered_period=int(x.entered_delisting_period.sum()),
  delist_date_range=[str(x.delist_date.min()),str(x.delist_date.max())],source="datahub stock_basic list_status=D (2026-10-14) + data/v2/delisted 日线/master + namechange(名称以'退'结尾=整理期)")
print(json.dumps({k:{kk:v[kk] for kk in v if kk in("rows","sha256","category_counts","n_months","n_entered_period","n_with_last_trade","last_anchor","last_month_partial","delist_date_range","n_listed")} for k,v in out.items()},ensure_ascii=False,indent=1,default=str))
