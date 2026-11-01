"""Back-adjusted (hfq) close = X2-stitch raw close x tushare adj_factor (research-grade).
Factor source: data/v2/tushare_raw/adj_factor_hist (2014-01→2026-06-30) ∪ adj_factor (2026-06-30→), merged
into data/v2/adj/adj_factor_2023h2plus.parquet (built by build_cache(); window limited to >=2023-09-01 so the
sealed 2018→2024-05 window is not touched beyond the evaluation warm-up).
Missing factor days are forward-filled within instrument (factor changes only on ex-dates).
promotion_approved=false.
"""
from __future__ import annotations
import glob
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/v2/adj/adj_factor_2023h2plus.parquet"
START = "20230901"
_F = None


def build_cache() -> Path:
    fs = [f for f in sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/adj_factor_hist/*.parquet")))
          if Path(f).stem >= START]
    fs += sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/adj_factor/*.parquet")))
    d = pd.concat([pd.read_parquet(f, columns=["ts_code", "trade_date", "adj_factor"]) for f in fs], ignore_index=True)
    d = d.drop_duplicates(["ts_code", "trade_date"], keep="last")
    d.to_parquet(CACHE, index=False)
    return CACHE


def _factors() -> pd.DataFrame:
    global _F
    if _F is None:
        if not CACHE.exists():
            build_cache()
        f = pd.read_parquet(CACHE)
        f["d"] = pd.to_datetime(f["trade_date"], format="%Y%m%d")
        _F = f.pivot_table(index="d", columns="ts_code", values="adj_factor", aggfunc="last").sort_index()
    return _F


def adj_close(instrument: str, raw_close: pd.Series) -> pd.Series:
    """raw_close indexed by session (X2 stitch). Returns hfq close; NaN where no factor at all."""
    F = _factors()
    if instrument not in F.columns:
        return raw_close * float("nan")
    fac = F[instrument].reindex(F.index.union(raw_close.index)).ffill().reindex(raw_close.index)
    return raw_close * fac
