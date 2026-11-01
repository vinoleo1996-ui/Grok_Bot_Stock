# verbatim copy of Data's resume_flags() (sha 8eac523b) to measure 60d-lookback effect; read-only
import pandas as pd, numpy as np, json, resource
from pathlib import Path
R=Path("/workspace/QuantLab"); RAW=R/"data/v2/tushare_raw"; MASK=R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
def resume_flags(y):
    lo=pd.Timestamp(f"{y}-01-01")
    mx=pd.read_parquet(MASK,columns=["date","instrument","in_universe","suspended"],filters=[("date",">=",lo-pd.Timedelta(days=60)),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    vv=[]; ss=[]
    for d in sorted(mx.date.unique()):
        d=pd.Timestamp(d); p=RAW/f"daily/{d:%Y%m%d}.parquet"; s=RAW/f"suspend_d/{d:%Y%m%d}.parquet"
        if p.exists(): x=pd.read_parquet(p,columns=["ts_code","vol"]); x["date"]=d; vv.append(x)
        if s.exists():
            z=pd.read_parquet(s,columns=["ts_code","suspend_type","suspend_timing"]); z=z[z.suspend_type=="S"].copy(); z["date"]=d; ss.append(z)
    V=pd.concat(vv).rename(columns={"ts_code":"instrument"})
    S=pd.concat(ss).rename(columns={"ts_code":"instrument"})
    t=S.suspend_timing.astype("string").str.strip()
    S["intra"]=S.suspend_timing.notna()&t.notna()&~t.isin(["","None","nan"])
    S=S.groupby(["date","instrument"]).intra.min().reset_index()
    f=mx.merge(V,on=["date","instrument"],how="left").merge(S,on=["date","instrument"],how="left")
    traded=f.vol.fillna(0)>0; full=f.intra.eq(False); f["intraday_halt"]=f.intra.eq(True)
    f["is_resume_day"]=f.suspended.astype(bool)&traded&~full
    h=f.in_universe.astype(float).where(traded&~f.is_resume_day)
    hp=h.groupby(f.instrument).ffill(); hp=hp.groupby(f.instrument).shift(1)
    f["hiliq_carry"]=f.is_resume_day&hp.eq(1.0)
    return f[f.date>=lo][["date","instrument","is_resume_day","intraday_halt","hiliq_carry"]]
res={}
for y in range(2018,2027):
    fl=resume_flags(y); res[y]=dict(is_resume_day=int(fl.is_resume_day.sum()),hiliq_carry_60d=int(fl.hiliq_carry.sum()),intraday_halt=int(fl.intraday_halt.sum()))
    fl[fl.hiliq_carry|fl.is_resume_day].to_parquet(f"/workspace/arch_audit/flags_{y}.parquet")
    print(y,res[y],f"rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f}MB",flush=True)
