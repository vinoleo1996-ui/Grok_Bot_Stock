import pandas as pd, numpy as np
from pathlib import Path
R=Path("/workspace/QuantLab"); RAW=R/"data/v2/tushare_raw"; MASK=R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
m=pd.read_parquet(MASK,columns=["date","instrument","suspended"],filters=[("date",">=",pd.Timestamp("2018-01-01")),("date","<=",pd.Timestamp("2018-12-31"))])
out=[]
for d,g in m.groupby("date"):
    ds=f"{pd.Timestamp(d):%Y%m%d}"; x=pd.read_parquet(RAW/f"daily/{ds}.parquet",columns=["ts_code","vol"])
    tr=set(x.ts_code[x.vol>0]); n=int((g.suspended.to_numpy()&np.fromiter((i in tr for i in g.instrument),bool,len(g))).sum()); out.append((ds,n))
o=pd.DataFrame(out,columns=["d","n"]); print(o.sort_values("n").tail(8).to_string()); print(o.n.median())
days=sorted(p.stem for p in (RAW/"daily").glob("2018*.parquet")); print(len(days), len(o))
