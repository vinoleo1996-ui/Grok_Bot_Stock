#!/usr/bin/env python3
"""Leaf 17 tech_qual_cert: base-α vector + fast trade-gate (Leo 07:56/07:58 craft).

Prereg: docs/v2/AI_G1G5_TECH_QUAL_CERT_WHO_PAYS_PREREG_ZH.md
Primary product = daily base-α (NOT Top-N; NOT weighted-sum with fast gate).
Fast 1–3d gate stored separately; eval weights from gated base-α for selfcheck only.
promotion=false; live=false; no Book-Smoke; target peak RSS ≤1.5GB.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.g1g5_tech_qual_cert_events import (  # noqa: E402
    COOL, HOLD, MAX_PER_YEAR, events_for_mask,
)
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa: E402
from research.g1g5_nontextbook_weights import _load_sw_members, sw_code_on  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_tech_qual_cert_v1"
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
NAME_W = 0.04
MAX_NAMES = 20
FAST_GATE_DAYS = 3  # 1–3d trade gate window
MKTCAP = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
DAILY = ROOT / "data/v2/tushare_raw/daily"
OUT_DIR = ROOT / "output/ai_factory/leaf18_tech_qual_cert"

WINDOWS = {
    "sealed": ("2018-01-02", "2024-05-31"),
    "x2": ("2024-06-03", "2026-10-09"),
}
UNIVERSES = {
    "FULLA": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet",
    "HILIQ": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
}
IND_CAP = {"FULLA": 0.28, "HILIQ": 0.25}


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def to_ts(x: str) -> str:
    x = str(x)
    if "." in x and x.split(".")[0] in ("sz", "sh", "bj"):
        mkt, code = x.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return x


def load_mktcap_for(instruments: set[str], start: str, end: str) -> pd.DataFrame:
    """Load float_mktcap only for `instruments` (event names) to cap RSS."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(MKTCAP)
    parts, want = [], set(instruments)
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    for i in range(pf.num_row_groups):
        df = pf.read_row_group(i, columns=["instrument_id", "trade_date", "float_mktcap"]).to_pandas()
        df["instrument"] = df["instrument_id"].map(to_ts)
        df["date"] = pd.to_datetime(df["trade_date"])
        df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts) & df["instrument"].isin(want)]
        if len(df):
            parts.append(df[["date", "instrument", "float_mktcap"]])
        del df
    if not parts:
        return pd.DataFrame(columns=["date", "instrument", "float_mktcap"])
    return pd.concat(parts, ignore_index=True).dropna()


def load_size_breaks(pool_by_day: dict, start: str, end: str) -> dict:
    """date(str)->(p70,p90) from FULL tradable pool, streamed; does not retain panel."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(MKTCAP)
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    # accumulate lists per date — only float values for pool members
    buckets: dict = {}
    want_dates = set(pool_by_day)
    for i in range(pf.num_row_groups):
        df = pf.read_row_group(i, columns=["instrument_id", "trade_date", "float_mktcap"]).to_pandas()
        df["instrument"] = df["instrument_id"].map(to_ts)
        df["date"] = pd.to_datetime(df["trade_date"]).dt.normalize()
        df = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]
        if df.empty:
            del df
            continue
        df["ds"] = df["date"].dt.strftime("%Y-%m-%d")
        df = df[df["ds"].isin(want_dates)]
        for ds, g in df.groupby("ds", sort=False):
            pool = pool_by_day.get(ds)
            if not pool:
                continue
            vals = g.loc[g["instrument"].isin(pool), "float_mktcap"].dropna().to_numpy()
            if len(vals):
                buckets.setdefault(ds, []).append(vals)
        del df
    out = {}
    for ds, arrs in buckets.items():
        import numpy as np
        v = np.concatenate(arrs)
        if len(v) < 20:
            continue
        out[ds] = (float(np.quantile(v, 0.70)), float(np.quantile(v, 0.90)))
    return out


def load_amount_panel(instruments: set[str], cal: pd.DatetimeIndex) -> pd.DataFrame:
    """amount (成交额) panel float32; RSS-conscious day loop."""
    want = set(instruments)
    rows = []
    for d in cal:
        p = DAILY / f"{d.strftime('%Y%m%d')}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p, columns=["ts_code", "amount"])
        df = df[df["ts_code"].isin(want)]
        if df.empty:
            continue
        df = df.assign(date=d)
        rows.append(df.rename(columns={"ts_code": "instrument"})[["date", "instrument", "amount"]])
    if not rows:
        return pd.DataFrame(columns=["date", "instrument", "amount"])
    return pd.concat(rows, ignore_index=True)


def size_domain_for_day(mc: pd.Series) -> pd.Series:
    if len(mc) < 20:
        return pd.Series("中小盘", index=mc.index)
    p70, p90 = float(mc.quantile(0.70)), float(mc.quantile(0.90))
    out = pd.Series("小微", index=mc.index)
    out[mc >= p70] = "中小盘"
    out[mc >= p90] = "大盘"
    return out


def domain_calibrate(x: pd.Series) -> pd.Series:
    """Within-domain rank → [-1, 1]. No market-wide yardstick."""
    if len(x) < 2:
        return pd.Series(0.0, index=x.index)
    r = x.rank(method="average", pct=True)  # (0,1]
    return (r - 0.5) * 2.0


def residualize_ind_size(df: pd.DataFrame, score_col: str = "score_cal") -> pd.Series:
    """Cross-sectional residual vs industry dummies + log float_mktcap. Pool = rows that day."""
    y = df[score_col].astype(float).values
    if len(df) < 30 or df["float_mktcap"].notna().sum() < 30:
        return df[score_col].astype(float)
    logmv = np.log(df["float_mktcap"].clip(lower=1.0).astype(float).values)
    ind = pd.get_dummies(df["ind"].fillna("_UNK"), drop_first=True)
    if ind.shape[1] == 0:
        X = np.column_stack([np.ones(len(df)), logmv])
    else:
        X = np.column_stack([np.ones(len(df)), logmv, ind.values.astype(float)])
    # drop rows with nan y
    ok = np.isfinite(y) & np.isfinite(X).all(axis=1)
    resid = np.full(len(df), np.nan)
    if ok.sum() < 30:
        return df[score_col].astype(float)
    Xo, yo = X[ok], y[ok]
    try:
        beta, *_ = np.linalg.lstsq(Xo, yo, rcond=None)
        resid[ok] = yo - Xo @ beta
    except Exception:
        return df[score_col].astype(float)
    # fill non-ok with calibrated score
    out = pd.Series(resid, index=df.index)
    out = out.fillna(df[score_col].astype(float))
    return out


def member_index_from_mask(mask_path: Path, sessions: list[str]) -> dict:
    m = pd.read_parquet(mask_path, columns=["date", "instrument", "in_universe"])
    m = m[m["in_universe"].astype(bool)].copy()
    m["s"] = pd.to_datetime(m["date"]).dt.strftime("%Y-%m-%d")
    ss = set(sessions)
    m = m[m["s"].isin(ss)]
    out = {s: set() for s in sessions}
    for s, g in m.groupby("s", sort=False):
        if s in out:
            out[s] = set(g["instrument"].tolist())
    return out


def build_products(E: pd.DataFrame, cal: pd.DatetimeIndex, members: dict,
                   mktcap: pd.DataFrame, amount: pd.DataFrame, ind_cap: float,
                   sw, size_breaks: dict | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (base_alpha, fast_gate, eval_weights). Never sums fast into alpha."""
    if E.empty:
        emp = pd.DataFrame(columns=["date", "instrument", "alpha", "size_domain", "event_flag", "ind"])
        gate = pd.DataFrame(columns=["date", "instrument", "gate", "gate_reason"])
        w = pd.DataFrame(columns=["date", "instrument", "target_weight"])
        return emp, gate, w

    pos = {d: i for i, d in enumerate(cal)}
    # event active windows
    slow_rows, fast_rows = [], []
    for r in E.itertuples():
        t0 = pd.Timestamp(r.sess).normalize()
        if t0 not in pos:
            k = int(cal.searchsorted(t0, side="left"))
            if k >= len(cal):
                continue
            t0_i = k
        else:
            t0_i = pos[t0]
        t2_i = t0_i + 2
        if t2_i >= len(cal):
            continue
        # slow base intensity over HOLD from T2
        for i in range(t2_i, min(t2_i + HOLD, len(cal))):
            life = (t2_i + HOLD - i) / HOLD
            slow_rows.append((cal[i], r.instrument, float(life), getattr(r, "ind", None)))
        # fast gate window: T0..T0+FAST (sessions after available) — amount confirmation at T1..T2
        for i in range(t0_i, min(t0_i + FAST_GATE_DAYS, len(cal))):
            fast_rows.append((cal[i], r.instrument, t0_i, i - t0_i))

    slow = pd.DataFrame(slow_rows, columns=["date", "instrument", "raw_slow", "ind"])
    if slow.empty:
        emp = pd.DataFrame(columns=["date", "instrument", "alpha", "size_domain", "event_flag", "ind"])
        return emp, pd.DataFrame(columns=["date", "instrument", "gate", "gate_reason"]), emp.copy()
    slow = slow.groupby(["date", "instrument"], as_index=False).agg(raw_slow=("raw_slow", "max"), ind=("ind", "first"))
    slow["date"] = pd.to_datetime(slow["date"]).dt.normalize()

    mktcap = mktcap.copy()
    mktcap["date"] = pd.to_datetime(mktcap["date"]).dt.normalize()
    amount = amount.copy()
    if len(amount):
        amount["date"] = pd.to_datetime(amount["date"]).dt.normalize()

    # fast gate: on event names, day-0..2 amount vs same-day pool median (in whitelist pool)
    fast = pd.DataFrame(fast_rows, columns=["date", "instrument", "t0_i", "age"])
    if len(fast):
        fast["date"] = pd.to_datetime(fast["date"]).dt.normalize()
        fast = fast.merge(amount, on=["date", "instrument"], how="left")

    alpha_parts, gate_parts, weight_days = [], [], []

    for d, g in slow.groupby("date", sort=True):
        ds = d.strftime("%Y-%m-%d")
        pool = members.get(ds, set())  # tradable universe that day
        g = g[g["instrument"].isin(pool) & ~g["instrument"].isin(HARD_EXCLUDE)].copy()
        if g.empty:
            continue
        # whitelist pool for this leaf = event-active ∩ tradable (already g)
        day_mc = mktcap[mktcap["date"] == d]
        g = g.merge(day_mc[["instrument", "float_mktcap"]], on="instrument", how="left")
        ds = d.strftime("%Y-%m-%d")
        br = (size_breaks or {}).get(ds)
        if br is None:
            # fallback: domain among event-day names with mktcap
            if g["float_mktcap"].notna().sum() >= 20:
                dom = size_domain_for_day(g.set_index("instrument")["float_mktcap"])
                g["size_domain"] = g["instrument"].map(dom).fillna("中小盘")
            else:
                g["size_domain"] = "中小盘"
        else:
            p70, p90 = br
            def _dom(v):
                if not np.isfinite(v):
                    return "中小盘"
                if v >= p90:
                    return "大盘"
                if v >= p70:
                    return "中小盘"
                return "小微"
            g["size_domain"] = g["float_mktcap"].map(lambda v: _dom(float(v) if pd.notna(v) else np.nan))
        # fill ind if missing
        if g["ind"].isna().any():
            g["ind"] = g.apply(
                lambda r: r["ind"] if pd.notna(r["ind"]) else (sw_code_on(r["instrument"], d, sw) or "_UNK"),
                axis=1,
            )

        # (1) domain calibrate raw_slow → score_cal
        g["score_cal"] = 0.0
        for dom, gd in g.groupby("size_domain"):
            g.loc[gd.index, "score_cal"] = domain_calibrate(gd["raw_slow"]).values

        # (3) residualize industry + size within today's whitelist rows
        # Use broader pool for residualization design matrix: all tradable with mktcap that day
        # but score only defined on event names — residualize among event names (whitelist)
        g["alpha"] = residualize_ind_size(g, "score_cal")
        # re-calibrate residual within domain to common scale
        for dom, gd in g.groupby("size_domain"):
            g.loc[gd.index, "alpha"] = domain_calibrate(gd["alpha"]).values
        g["event_flag"] = 1
        alpha_parts.append(g[["date", "instrument", "alpha", "size_domain", "event_flag", "ind"]])

        # (2) fast gate — NOT merged into alpha
        # gate=1 if max amount in age<=2 is ≥ pool median amount that day; else 0
        day_amt = amount[amount["date"] == d] if len(amount) else pd.DataFrame()
        pool_med = float(day_amt.loc[day_amt["instrument"].isin(pool), "amount"].median()) if len(day_amt) else np.nan
        fg = fast[fast["date"] == d] if len(fast) else pd.DataFrame()
        gate_map = {}
        if len(fg) and np.isfinite(pool_med):
            for inst, gi in fg.groupby("instrument"):
                a = gi["amount"].max(skipna=True)
                gate_map[inst] = 1 if (pd.notna(a) and a >= pool_med) else 0
        else:
            # missing amount → pass gate (fail-open conservatively for coverage; disclose)
            gate_map = {i: 1 for i in g["instrument"]}
        for inst in g["instrument"]:
            gt = int(gate_map.get(inst, 1))
            gate_parts.append(dict(date=d, instrument=inst, gate=gt,
                                   gate_reason="amt>=pool_med" if gt else "amt<pool_med"))

        # eval weights from gated base-α only (gate==0 → skip name)
        gg = g.copy()
        gg["gate"] = gg["instrument"].map(lambda i: gate_map.get(i, 1))
        gg = gg[gg["gate"] == 1].sort_values("alpha", ascending=False)
        picked, ind_w = [], {}
        for _, r in gg.iterrows():
            if len(picked) >= MAX_NAMES:
                break
            ind = r["ind"] or "_UNK"
            # ind may be sw_code; cap by code
            if ind_w.get(ind, 0.0) + NAME_W > ind_cap + 1e-12:
                continue
            picked.append(r["instrument"])
            ind_w[ind] = ind_w.get(ind, 0.0) + NAME_W
        if not picked:
            weight_days.append((d, BALLAST, 1.0))
        else:
            for inst in picked:
                weight_days.append((d, inst, NAME_W))
            weight_days.append((d, BALLAST, max(0.0, 1.0 - NAME_W * len(picked))))

    alpha = pd.concat(alpha_parts, ignore_index=True) if alpha_parts else pd.DataFrame(
        columns=["date", "instrument", "alpha", "size_domain", "event_flag", "ind"]
    )
    gate = pd.DataFrame(gate_parts)
    weights = pd.DataFrame(weight_days, columns=["date", "instrument", "target_weight"])
    if len(weights):
        weights["date"] = pd.to_datetime(weights["date"])
        s = weights.groupby("date")["target_weight"].transform("sum").replace(0, np.nan)
        weights["target_weight"] = weights["target_weight"] / s
    return alpha, gate, weights


def run_one(universe: str, window: str) -> dict:
    mask = UNIVERSES[universe]
    start, end = WINDOWS[window]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    E, st = events_for_mask(mask, growth_only=True)
    if len(E):
        E = E[(E["sess"] >= pd.Timestamp(start) - pd.Timedelta(days=5)) & (E["sess"] <= end)].copy()

    bench = _load_benchmark_closes("510300")
    cal = bench.index[(bench.index >= start) & (bench.index <= end)]
    cal_full = bench.index[(bench.index >= "2017-12-01") & (bench.index <= end)]
    if len(E):
        E = E.copy()
        E["si"] = cal_full.searchsorted(pd.to_datetime(E["sess"]).values, side="left")
        E = E[E["si"] < len(cal_full)]

    sessions = [d.strftime("%Y-%m-%d") for d in cal]
    members = member_index_from_mask(mask, sessions)
    ev_names = set(E["instrument"].unique()) if len(E) else set()

    print(f"[{universe}/{window}] events_in_span≈{len(E)} days={len(cal)} rss={rss_mb():.0f}MB", flush=True)

    mc_start = (pd.Timestamp(start) - pd.Timedelta(days=5)).strftime("%Y-%m-%d")
    # RSS: mktcap only for event names; pool P70/P90 streamed separately
    mktcap = load_mktcap_for(ev_names, mc_start, end)
    print(f"  mktcap_events={len(mktcap)} rss={rss_mb():.0f}MB", flush=True)
    size_breaks = load_size_breaks(members, start, end)
    print(f"  size_breaks_days={len(size_breaks)} rss={rss_mb():.0f}MB", flush=True)
    amount = load_amount_panel(ev_names, cal)
    print(f"  amount={len(amount)} rss={rss_mb():.0f}MB", flush=True)

    sw = _load_sw_members()
    alpha, gate, weights = build_products(E, cal_full, members, mktcap, amount, IND_CAP[universe], sw, size_breaks)
    if len(alpha):
        alpha = alpha[(alpha["date"] >= start) & (alpha["date"] <= end)]
    if len(gate):
        gate = gate[(gate["date"] >= start) & (gate["date"] <= end)]
    if len(weights):
        weights = weights[(weights["date"] >= start) & (weights["date"] <= end)]

    ap = OUT_DIR / f"alpha_{universe}_{window}_{stamp}.parquet"
    gp = OUT_DIR / f"gate_{universe}_{window}_{stamp}.parquet"
    wp = OUT_DIR / f"eval_weights_{universe}_{window}_{stamp}.parquet"
    alpha.to_parquet(ap, index=False)
    gate.to_parquet(gp, index=False)
    weights.to_parquet(wp, index=False)

    meta = dict(
        mechanism_tag=MECHANISM_TAG,
        universe=universe,
        window=window,
        span=[start, end],
        primary_product="base_alpha_vector",
        fast_gate_separate=True,
        fast_gate_days=FAST_GATE_DAYS,
        craft=["domain_calibrate", "slow_base_alpha", "fast_trade_gate", "resid_ind_size"],
        n_events_input=int(len(E)),
        n_alpha_rows=int(len(alpha)),
        n_alpha_names=int(alpha["instrument"].nunique()) if len(alpha) else 0,
        n_gate_pass=int((gate["gate"] == 1).sum()) if len(gate) else 0,
        n_gate_total=int(len(gate)),
        n_weight_days=int(weights["date"].nunique()) if len(weights) else 0,
        alpha_path=str(ap),
        gate_path=str(gp),
        eval_weights_path=str(wp),
        alpha_sha256=hashlib.sha256(ap.read_bytes()).hexdigest(),
        event_stats_mask=st,
        ind_cap=IND_CAP[universe],
        hold=HOLD,
        cool=COOL,
        max_per_year=MAX_PER_YEAR,
        live=False,
        promotion_approved=False,
        peak_rss_mb=rss_mb(),
        stamp=stamp,
        note_orthogonalize="ρ_excess vs existing leaves reported in selfcheck; no weighted-sum with foreign leaf scores",
        arch_todo=["leaf_selfcheck_v3: delist terminal returns", "leaf_selfcheck_v3: acceptance universe FULLA/HI_LIQ not static top300"],
    )
    if len(alpha):
        meta["alpha_domain_counts"] = alpha["size_domain"].value_counts().to_dict()
    mp = OUT_DIR / f"run_meta_{universe}_{window}_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if window == "x2":
        tag = "fulla" if universe == "FULLA" else "hiliq"
        link = ROOT / "output/ai_factory" / f"g1g5_tech_qual_cert_{tag}_daily_weights_{stamp}.parquet"
        weights.to_parquet(link, index=False)
        meta["selfcheck_weights_path"] = str(link)
        mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        (ROOT / "output/ai_factory" / f"g1g5_tech_qual_cert_{tag}_run_meta_{stamp}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
    print(f"  wrote alpha/gate/weights rss={rss_mb():.0f}MB", flush=True)
    gc.collect()
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", choices=["FULLA", "HILIQ", "both"], default="both")
    ap.add_argument("--window", choices=["sealed", "x2", "both"], default="both")
    args = ap.parse_args()
    us = ["FULLA", "HILIQ"] if args.universe == "both" else [args.universe]
    ws = ["sealed", "x2"] if args.window == "both" else [args.window]
    results = []
    for u in us:
        for w in ws:
            results.append(run_one(u, w))
    summary = OUT_DIR / f"build_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("SUMMARY", summary, "peak_rss", max(r["peak_rss_mb"] for r in results))


if __name__ == "__main__":
    main()
