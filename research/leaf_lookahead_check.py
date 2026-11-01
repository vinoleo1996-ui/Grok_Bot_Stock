"""Freqtrade-style lookahead check for G1G5 leaf weight scripts (no writes to output/ai_factory weights).
Usage: python3 research/leaf_lookahead_check.py <leaf> <cut YYYY-MM-DD|full>
Truncates event source tables to rows available by cut T (report_rc/stk_surv: available_at <= T 15:00; disclosure_date:
actual_date <= T), sets WEIGHT_END=T, runs the frozen script's run() up to build_daily_weights_expand, captures weights,
aborts before any file write. Writes output/ai_factory/leaf_reports/<leaf>/lookahead_<cut>.parquet. live=false."""
from __future__ import annotations
import sys, importlib, resource
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
leaf, cut = sys.argv[1], sys.argv[2]
OUT = ROOT / "output/ai_factory/leaf_reports" / leaf; OUT.mkdir(parents=True, exist_ok=True)
_orig = pd.read_parquet


def _rp(path, *a, **k):
    df = _orig(path, *a, **k)
    if cut == "full": return df
    p = str(path); T = pd.Timestamp(cut)
    if ("report_rc_2018plus" in p or "stk_surv_2018plus" in p):
        if "available_at" in df.columns: return df[df["available_at"] <= T + pd.Timedelta(hours=15)]
        av = _orig(path, columns=["available_at"])["available_at"]  # same row order
        return df[(av <= T + pd.Timedelta(hours=15)).values]
    if "disclosure_date" in p and "actual_date" in df.columns:
        ad = pd.to_datetime(df["actual_date"].astype(str), format="%Y%m%d", errors="coerce")
        return df[ad <= T]
    return df


pd.read_parquet = _rp
class Captured(Exception): pass
m = importlib.import_module(f"research.g1g5_{leaf}_weights")
CAP = {}
_bdw = m.build_daily_weights_expand
def _cap(*a, **k):
    CAP["w"] = _bdw(*a, **k); raise Captured()
m.build_daily_weights_expand = _cap
if cut != "full": m.WEIGHT_END = cut
try:
    m.run()
except Captured:
    pass
w = CAP["w"][["date", "instrument", "target_weight"]].copy(); w["date"] = w["date"].astype(str).str[:10]
w.to_parquet(OUT / f"lookahead_{cut}.parquet", index=False)
print(leaf, cut, len(w), w.date.max(), "RSS_MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
