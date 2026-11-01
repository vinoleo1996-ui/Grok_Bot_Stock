import pandas as pd, numpy as np, json
from pathlib import Path
R=Path("/workspace/QuantLab"); RAW=R/"data/v2/tushare_raw"; MASK=R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
out={}
for y in range(2018,2027):
    m=pd.read_parquet(MASK,columns=["date","instrument","st","suspended","young","adv20_yuan"],filters=[("date",">=",pd.Timestamp(f"{y}-01-01")),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    c=dict(elig_true_resume=0,true_resume_excl_first_session=0,R_traded=0,R_traded_notfull=0,resume_with_R=0)
    for d,g in m.groupby("date"):
        ds=f"{pd.Timestamp(d):%Y%m%d}"; x=pd.read_parquet(RAW/f"daily/{ds}.parquet",columns=["ts_code","vol"]); tr=set(x.ts_code[x.vol>0])
        sp=RAW/f"suspend_d/{ds}.parquet"; s=pd.read_parquet(sp,columns=["ts_code","suspend_type","suspend_timing"]) if sp.exists() else pd.DataFrame(columns=["ts_code","suspend_type","suspend_timing"])
        t=s.suspend_timing.astype("string").str.strip(); intra=s.suspend_timing.notna()&t.notna()&~t.isin(["","None","nan"])
        full=set(s.ts_code[(s.suspend_type=="S")&~intra]); sS=set(s.ts_code[s.suspend_type=="S"]); Rs=set(s.ts_code[s.suspend_type=="R"])
        inst=g.instrument.to_numpy(); f=lambda S_: np.fromiter((i in S_ for i in inst),bool,len(inst))
        trd=f(tr); susp=g.suspended.to_numpy(); res=susp&trd&~f(full); tru=res&~f(sS)
        el=(~g.st.to_numpy())&(~g.young.to_numpy())&(g.adv20_yuan.to_numpy()>=3e6)
        c["elig_true_resume"]+=int((tru&el).sum())
        if ds!="20180102": c["true_resume_excl_first_session"]+=int(tru.sum())
        c["R_traded"]+=len(Rs&tr); c["R_traded_notfull"]+=len((Rs&tr)-full); c["resume_with_R"]+=int((res&f(Rs)).sum())
    out[y]=c; print(y,c,flush=True)
tot={k:sum(v[k] for v in out.values()) for k in out[2018]}; s24={k:sum(out[y][k] for y in (2024,2025,2026)) for k in out[2018]}
print("total",tot); print("since2024",s24)
json.dump(out,open("variants.json","w"),indent=1)
