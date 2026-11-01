import json, sys
from datetime import date
import numpy as np, pandas as pd
from quantlab.data.v2_readers import default_v2_roots
from quantlab.factors.p1_factor_lib import load_ohlcv_panels
from quantlab.factors.p1_pipeline import compute_p1_raw_map
roots=default_v2_roots()
d0=roots.d0_root
# instrument ids from D0 directory listing
import os
cands=sorted({p.stem for p in d0.rglob("*.parquet")})[:4000]
rng=np.random.default_rng(7); ids=list(rng.choice(cands, size=min(300,len(cands)), replace=False))
panels,notes=load_ohlcv_panels(ids, d0_root=d0, asof_extend_dir=roots.asof_extend_dir, end_session=date(2026,9,30))
close=panels["close"]; print("close", close.shape, close.index.min(), close.index.max(), file=sys.stderr)
idx=close.index; H=5
sess=[d for d in idx[(idx>=pd.Timestamp("2024-06-01"))][::21][:-1]][:24]
F=("M01_12_1","V01_EP","REV","IVOL","L01_RV60","LIQ01_TOV","LIQ02_AMIHUD","turn_20d")
ics={f:[] for f in F}
for t in sess:
    i=idx.get_loc(t)
    if i+H>=len(idx): break
    fwd=close.iloc[i+H]/close.iloc[i]-1
    sub={k:v.loc[:t] if isinstance(v,pd.DataFrame) and not v.empty else v for k,v in panels.items()}
    raw,_,cov=compute_p1_raw_map(t.date(), ids, {}, panels=sub, factor_ids=F)
    for f in F:
        s=pd.Series(raw.get(f) or {},dtype=float)
        j=pd.concat([s,fwd],axis=1).dropna()
        if len(j)>=30: ics[f].append(j.iloc[:,0].rank().corr(j.iloc[:,1].rank()))
out={"promotion_approved":False,"sample":"real_D0_random300_instruments_monthly_sessions_2024-06+_NOT_Full_D1",
 "method":"raw factor (pre-neutral) rank IC vs 5d fwd close return; process metric only","n_instruments":len(ids)}
for f,v in ics.items():
    a=np.array(v); out[f]={"n_sessions":int(len(a)),"ic_mean":float(a.mean()) if len(a) else None,
      "icir":float(a.mean()/a.std(ddof=1)) if len(a)>2 and a.std()>0 else None}
json.dump(out,open("output/alpha/P1_SINGLE_VAR_PROCESS_IC_SAMPLE.json","w"),indent=2,ensure_ascii=False)
print(json.dumps(out,indent=1))
