"""HI_LIQ_V1.1 float-mktcap (wb) benchmark daily returns, X2. weights at t-1 close (in_universe at t-1), return close t/t-1. Research only."""
import sys, gc
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "research")); sys.path.insert(0, str(ROOT))
import optimizer_lambda_calib_sealed as C
s0, s1 = pd.Timestamp("2024-05-20"), pd.Timestamp("2026-10-09")
m = pq.read_table(C.MASK_PATH, columns=["date", "instrument", "in_universe"],
                  filters=[("date", ">=", s0), ("date", "<=", s1), ("in_universe", "=", True)]).to_pandas()
m["date"] = pd.to_datetime(m["date"]).dt.normalize()
names = sorted(m.instrument.unique())
b = C.load_daily_basic_window(names, s0, s1); b["trade_date"] = pd.to_datetime(b["trade_date"]).dt.tz_localize(None).dt.normalize()
cl = b.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last").sort_index()
mv = b.pivot_table(index="trade_date", columns="ts_code", values="float_mktcap", aggfunc="last").reindex(cl.index)
del b; gc.collect()
inu = m.assign(v=1.0).pivot_table(index="date", columns="instrument", values="v", aggfunc="last").reindex(index=cl.index, columns=cl.columns).ffill(limit=5)
r = cl.pct_change(fill_method=None)
w = (mv * inu).shift(1); w = w.where(r.notna()); w = w.div(w.sum(axis=1), axis=0)
br = (w * r.clip(-0.5, 1.0)).sum(axis=1, min_count=1).loc["2024-06-03":"2026-10-09"].fillna(0.0)
out = ROOT / "output/strategy_optimizer/core_x2/bench_hiliq_wb_x2.csv"
pd.DataFrame({"date": br.index.strftime("%Y-%m-%d"), "ret": br.values, "n": w.notna().sum(axis=1).reindex(br.index).values}).to_csv(out, index=False)
print(out, len(br), "cum", float((1 + br).prod() - 1), "RSS", C.rss_mb())
