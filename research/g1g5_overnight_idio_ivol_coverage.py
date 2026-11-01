"""overnight_idio_ivol coverage gate (NO returns / NO alpha direction peek).
Leaf 18. Counts valid overnight series names per day under HI_LIQ/FULLA masks.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "data/v2/tushare_raw/daily"
CAL = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
MASKS = {
    "HILIQ": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
    "FULLA": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet",
}
IVOL_WIN = 20  # need ≥ this many overnight obs


def sessions(start, end):
    cal = pd.read_parquet(CAL)
    cal["cal_date"] = pd.to_datetime(cal["cal_date"].astype(str))
    s = pd.DatetimeIndex(sorted(cal.loc[cal["is_open"].astype(int) == 1, "cal_date"].unique()))
    return s[(s >= start) & (s <= end)]


def mask_by_day(path, sessions_idx):
    m = pd.read_parquet(path, columns=["date", "instrument", "in_universe"])
    m = m[m["in_universe"].astype(bool)].copy()
    m["date"] = pd.to_datetime(m["date"]).dt.normalize()
    want = set(sessions_idx)
    m = m[m["date"].isin(want)]
    return {d: set(g["instrument"]) for d, g in m.groupby("date", sort=False)}


def coverage(universe: str, start: str, end: str) -> dict:
    sess = sessions(start, end)
    members = mask_by_day(MASKS[universe], sess)
    # rolling count of valid overnight points per name — stream days
    from collections import defaultdict, deque
    hist = defaultdict(lambda: deque(maxlen=IVOL_WIN))  # instrument -> recent valid flags
    daily_valid = []
    for d in sess:
        p = DAILY / f"{d.strftime('%Y%m%d')}.parquet"
        pool = members.get(pd.Timestamp(d).normalize(), set())
        if not p.exists() or not pool:
            daily_valid.append(dict(date=str(d.date()), n_pool=len(pool), n_valid_ivol=0))
            continue
        df = pd.read_parquet(p, columns=["ts_code", "open", "pre_close", "close"])
        df = df[df["ts_code"].isin(pool)]
        ok = (
            df["open"].notna()
            & df["pre_close"].notna()
            & df["close"].notna()
            & (df["pre_close"] > 0)
            & (df["open"] > 0)
        )
        # mark overnight computable (not the return value for selection)
        for code, good in zip(df["ts_code"], ok):
            hist[code].append(1 if bool(good) else 0)
        n_valid = sum(1 for code in pool if sum(hist[code]) >= IVOL_WIN)
        daily_valid.append(dict(date=str(d.date()), n_pool=len(pool), n_valid_ivol=n_valid))
    dv = pd.DataFrame(daily_valid)
    return dict(
        universe=universe,
        span=[start, end],
        n_days=int(len(dv)),
        median_pool=float(dv["n_pool"].median()) if len(dv) else 0,
        median_valid_ivol=float(dv["n_valid_ivol"].median()) if len(dv) else 0,
        min_valid_ivol=int(dv["n_valid_ivol"].min()) if len(dv) else 0,
        frac_days_valid_ge_200=float((dv["n_valid_ivol"] >= 200).mean()) if len(dv) else 0,
        frac_days_valid_ge_500=float((dv["n_valid_ivol"] >= 500).mean()) if len(dv) else 0,
    )


if __name__ == "__main__":
    out = {}
    for u, (a, b) in {
        "HILIQ_sealed": ("2018-01-02", "2024-05-31"),
        "HILIQ_x2": ("2024-06-03", "2026-10-09"),
        "FULLA_x2": ("2024-06-03", "2026-10-09"),
        "FULLA_sealed_overlap": ("2023-09-01", "2024-05-31"),
    }.items():
        uni = u.split("_")[0]
        if uni.startswith("FULLA"):
            uni = "FULLA"
        if uni.startswith("HILIQ"):
            uni = "HILIQ"
        # fix parse
        uni = "HILIQ" if u.startswith("HILIQ") else "FULLA"
        print("running", u, flush=True)
        out[u] = coverage(uni, a, b)
        print(u, out[u], flush=True)
    dest = ROOT / "output/ai_factory/overnight_idio_ivol_coverage_20261014.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", dest)
