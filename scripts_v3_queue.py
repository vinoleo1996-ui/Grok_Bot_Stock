import sys,os,time; sys.path.insert(0,'.')
exec(open("scripts_cb_etf_pull2.py").read().split("cal=call")[0])
import pandas as pd
def P(*a): print(*a,flush=True)
def paged(api,key,code,start="20140101",end="20261011",step_days=900,**kw):
    out=[]; s=pd.Timestamp(start)
    while s<=pd.Timestamp(end):
        e=min(s+pd.Timedelta(days=step_days),pd.Timestamp(end))
        x=call(api,**{key:code},start_date=s.strftime("%Y%m%d"),end_date=e.strftime("%Y%m%d"),**kw)
        if len(x)>=1000 and step_days>30:  # possible cap -> split
            x=paged(api,key,code,s.strftime("%Y%m%d"),e.strftime("%Y%m%d"),step_days//4,**kw)
        out.append(x); s=e+pd.Timedelta(days=1)
    return pd.concat(out,ignore_index=True).drop_duplicates() if out else pd.DataFrame()
E="data/v2/etf/raw/"
fb=pd.read_parquet(E+"fund_basic_E.parquet").drop_duplicates("ts_code")
etfs0=sorted(fb[fb.name.str.contains("ETF",na=False)&~fb.name.str.contains("联接",na=False)].ts_code)
# 拉取顺序：行业 → 主题/其他 → 宽基 → 其余（跨境/债券货币/商品）；已落盘的由下方 exists 跳过
_basic=pd.read_parquet("data/v2/etf/etf_basic.parquet")[["ts_code","category"]].drop_duplicates("ts_code")
_cat=_basic.set_index("ts_code")["category"].to_dict()
_order=["行业","主题/其他","宽基","跨境","债券/货币","商品"]
_buckets={k:[] for k in _order}; _other=[]
for c in etfs0:
    k=_cat.get(c)
    (_buckets[k] if k in _buckets else _other).append(c)
etfs=[c for k in _order for c in sorted(_buckets[k])]+sorted(_other)

M="data/v2/margin/"
if not os.path.exists(M+"margin_exchange_2014_2017.parquet"):
    pd.concat([paged("margin","exchange_id",x,"20140101","20180105",step_days=300) for x in ["SSE","SZSE"]]).to_parquet(M+"margin_exchange_2014_2017.parquet"); P("margin done")
R="data/v2/rates/"; os.makedirs(R,exist_ok=True)
if not os.path.exists(R+"shibor.parquet"):
    o=[];s0=pd.Timestamp("2014-01-01")
    while s0<pd.Timestamp("2026-10-11"):
        e=s0+pd.Timedelta(days=900); o.append(call("shibor",start_date=s0.strftime("%Y%m%d"),end_date=e.strftime("%Y%m%d"))); s0=e+pd.Timedelta(days=1)
    pd.concat(o).drop_duplicates().to_parquet(R+"shibor.parquet"); P("shibor done")
# 4) fund_div
if not os.path.exists(E+"fund_div.parquet"):
    o=[]
    for c in etfs:
        try: o.append(call("fund_div",ts_code=c))
        except Exception as e: P("FAIL fund_div",c,e)
    pd.concat(o,ignore_index=True).to_parquet(E+"fund_div.parquet"); P("fund_div done",len(o))
# 7) futures
F="data/v2/futures/raw/"
if not os.path.exists(F+"fut_basic.parquet"):
    fbx=call("fut_basic",exchange="CFFEX"); fbx.to_parquet(F+"fut_basic.parquet")
fbx=pd.read_parquet(F+"fut_basic.parquet")
fbx=fbx[fbx.fut_code.isin(["IF","IC","IM","IH"])]  # 国债 T/TF/TS/TL 留到份额段后的 catchup
if not os.path.exists(F+"fut_settle_cffex.parquet"):
    try: pd.concat([call("fut_settle",trade_date=d,exchange="CFFEX") for d in []] or [call("fut_settle",exchange="CFFEX",ts_code="IF2312.CFX")]).to_parquet(F+"fut_settle_probe.parquet")
    except Exception as e: P("fut_settle probe fail",str(e)[:80])
os.makedirs(F+"daily",exist_ok=True)
for c in sorted(fbx.ts_code):
    fn=F+f"daily/{c}.parquet"
    if os.path.exists(fn): continue
    try: call("fut_daily",ts_code=c).to_parquet(fn)
    except Exception as e: P("FAIL fut",c,str(e)[:80])
if not os.path.exists(F+"fut_mapping.parquet"):
    pd.concat([paged("fut_mapping","ts_code",c,start="20100101",step_days=1500) for c in ["IF.CFX","IC.CFX","IM.CFX","IH.CFX","T.CFX","TF.CFX","TS.CFX","TL.CFX"]]).to_parquet(F+"fut_mapping.parquet")
if not os.path.exists(F+"index_daily.parquet"):
    pd.concat([paged("index_daily","ts_code",c,start="20100101",step_days=2500) for c in ["000300.SH","000905.SH","000852.SH","000016.SH"]]).to_parquet(F+"index_daily.parquet")
P("futures done")
# 10) global
G="data/v2/index_global/"
if not os.path.exists(G+"index_global_raw.parquet"):
    pd.concat([paged("index_global","ts_code",c,step_days=2500) for c in ["HSI","IXIC","NDX","SPX"]]).to_parquet(G+"index_global_raw.parquet")

# 5/8) fund_share + fund_nav for all equity ETFs (needed for scale/flows)
os.makedirs(E+"fund_share",exist_ok=True); os.makedirs(E+"fund_nav",exist_ok=True)
for i,c in enumerate(etfs):
    for api in ["fund_share","fund_nav"]:
        fn=E+f"{api}/{c}.parquet"
        if os.path.exists(fn): continue
        try: (paged(api,"ts_code",c) if api=="fund_share" else call(api,ts_code=c)).to_parquet(fn)
        except Exception as e: P("FAIL",api,c,str(e)[:80])
    if i%200==0: P("share/nav",i,len(etfs))

P("ALL DONE")

# BOND FUTURES CATCHUP (T/TF/TS/TL) — skip existing; safe after index-futures pass
fbx_all=pd.read_parquet(F+"fut_basic.parquet")
fbx_b=fbx_all[fbx_all.fut_code.isin(["T","TF","TS","TL"])]
os.makedirs(F+"daily",exist_ok=True)
for c in sorted(fbx_b.ts_code):
    fn=F+f"daily/{c}.parquet"
    if os.path.exists(fn): continue
    try: call("fut_daily",ts_code=c).to_parquet(fn)
    except Exception as e: P("FAIL bond fut",c,str(e)[:80])
if not os.path.exists(F+"fut_mapping_bond.parquet"):
    try:
        pd.concat([paged("fut_mapping","ts_code",c,start="20130101",step_days=1500) for c in ["T.CFX","TF.CFX","TS.CFX","TL.CFX"]]).to_parquet(F+"fut_mapping_bond.parquet")
        P("bond mapping done")
    except Exception as e: P("FAIL bond mapping",str(e)[:80])
P("bond futures catchup done")
