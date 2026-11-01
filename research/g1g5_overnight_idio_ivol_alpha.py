#!/usr/bin/env python3
"""Leaf 18 overnight_idio_ivol: base-α = -idio overnight ivol (20d); fast gate = overnight left-tail.
Prereg: docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_WHO_PAYS_PREREG_ZH.md
Primary product = daily base-α vector. live=false; no Book-Smoke; target peak RSS ≤1.5GB.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, resource, sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_overnight_idio_ivol_v1"
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})
NAME_W = 0.04
MAX_NAMES = 20
IVOL_WIN = 20
MIN_OBS = 15
REBAL_EVERY = 5
FAST_GATE_DAYS = 3
LEFT_TAIL_PCT = 0.05
MKTCAP = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
SW = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
DAILY = ROOT / "data/v2/tushare_raw/daily"
OUT_DIR = ROOT / "output/ai_factory/leaf18_overnight_idio_ivol"
WINDOWS = {"sealed": ("2018-01-02", "2024-05-31"), "x2": ("2024-06-03", "2026-10-09")}
UNIVERSES = {
    "HILIQ": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
    "FULLA": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet",
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


def sw_map() -> dict[str, str]:
    sw = pd.read_parquet(SW, columns=["instrument_id", "sw_name", "in_date"])
    sw["instrument"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"].astype(str), errors="coerce")
    sw = sw.sort_values("in_date").drop_duplicates("instrument", keep="last")
    return dict(zip(sw["instrument"], sw["sw_name"]))


def member_index(mask_path: Path, sessions: list[str]) -> dict:
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


def load_mktcap_day(dates_needed: set[str]) -> dict:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(MKTCAP)
    out: dict[str, dict[str, float]] = {d: {} for d in dates_needed}
    want_d = set(dates_needed)
    nrg = pf.num_row_groups
    for i in range(nrg):
        if i % 5 == 0:
            print(f"  mktcap rg {i}/{nrg} rss={rss_mb():.0f}MB", flush=True)
        df = pf.read_row_group(i, columns=["instrument_id", "trade_date", "float_mktcap"]).to_pandas()
        df["instrument"] = df["instrument_id"].map(to_ts)
        df["ds"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        df = df[df["ds"].isin(want_d)]
        for ds, g in df.groupby("ds", sort=False):
            bucket = out.setdefault(ds, {})
            for inst, v in zip(g["instrument"].to_numpy(), g["float_mktcap"].to_numpy()):
                if v == v:  # not nan
                    bucket[inst] = float(v)
        del df
    return out


def resid_cs(y: np.ndarray, ind: np.ndarray, logmv: np.ndarray) -> np.ndarray:
    """Cross-sectional residual vs industry dummies + logmv. Returns array same length."""
    n = len(y)
    out = np.full(n, np.nan)
    ok = np.isfinite(y) & np.isfinite(logmv)
    if ok.sum() < 30:
        # demean by industry
        s = pd.Series(y)
        ind_s = pd.Series(ind)
        dem = s.groupby(ind_s).transform(lambda x: x - x.mean())
        return dem.to_numpy()
    # build design
    ind_ok = ind[ok]
    cats, inv = np.unique(ind_ok, return_inverse=True)
    if len(cats) >= 2:
        dummies = np.eye(len(cats), dtype=float)[inv][:, 1:]  # drop first
        X = np.column_stack([np.ones(ok.sum()), logmv[ok], dummies])
    else:
        X = np.column_stack([np.ones(ok.sum()), logmv[ok]])
    yo = y[ok]
    try:
        beta, *_ = np.linalg.lstsq(X, yo, rcond=None)
        out[ok] = yo - X @ beta
    except Exception:
        s = pd.Series(y)
        out = s.groupby(pd.Series(ind)).transform(lambda x: x - x.mean()).to_numpy()
    return out


def domain_calibrate_arr(vals: np.ndarray, domains: np.ndarray) -> np.ndarray:
    out = np.zeros(len(vals))
    for dom in np.unique(domains):
        idx = np.where(domains == dom)[0]
        x = vals[idx]
        if len(x) < 2:
            continue
        # rank pct
        order = x.argsort().argsort()
        pct = (order + 1) / len(x)
        out[idx] = (pct - 0.5) * 2.0
    return out


def size_domain_arr(mv: np.ndarray) -> np.ndarray:
    out = np.array(["中小盘"] * len(mv), dtype=object)
    finite = np.isfinite(mv)
    if finite.sum() < 20:
        return out
    p70 = np.nanquantile(mv, 0.70)
    p90 = np.nanquantile(mv, 0.90)
    out[:] = "小微"
    out[mv >= p70] = "中小盘"
    out[mv >= p90] = "大盘"
    out[~finite] = "中小盘"
    return out


def run_one(universe: str, window: str) -> dict:
    mask = UNIVERSES[universe]
    start, end = WINDOWS[window]
    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=60)).strftime("%Y-%m-%d")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bench = _load_benchmark_closes("510300")
    cal_full = bench.index[(bench.index >= warm_start) & (bench.index <= end)]
    sessions = [d.strftime("%Y-%m-%d") for d in cal_full]
    members = member_index(mask, sessions)
    swm = sw_map()
    print(f"[{universe}/{window}] days_warm={len(cal_full)} rss={rss_mb():.0f}MB", flush=True)

    mktcap = load_mktcap_day(set(sessions))
    print(f"  mktcap_days={len(mktcap)} rss={rss_mb():.0f}MB", flush=True)

    hist: dict[str, deque] = defaultdict(lambda: deque(maxlen=IVOL_WIN))
    recent_eps: dict[str, deque] = defaultdict(lambda: deque(maxlen=FAST_GATE_DAYS))
    alpha_rows, gate_rows, weight_rows = [], [], []
    rebal_countdown = 0
    last_weights = None
    start_ts = pd.Timestamp(start)

    for di, d in enumerate(cal_full):
        ds = d.strftime("%Y-%m-%d")
        pool = members.get(ds, set())
        p = DAILY / f"{d.strftime('%Y%m%d')}.parquet"
        if not pool or not p.exists():
            continue
        df = pd.read_parquet(p, columns=["ts_code", "open", "pre_close", "close"])
        df = df[df["ts_code"].isin(pool)]
        if len(df) < 30:
            continue
        pc = df["pre_close"].to_numpy(dtype=float)
        op = df["open"].to_numpy(dtype=float)
        codes = df["ts_code"].to_numpy()
        good = np.isfinite(pc) & np.isfinite(op) & (pc > 0) & (op > 0)
        codes, pc, op = codes[good], pc[good], op[good]
        if len(codes) < 30:
            continue
        r_on = op / pc - 1.0
        ind = np.array([swm.get(c, "_UNK") for c in codes], dtype=object)
        mc = mktcap.get(ds, {})
        mv = np.array([mc.get(c, np.nan) for c in codes], dtype=float)
        logmv = np.log(np.clip(mv, 1.0, None))
        eps = resid_cs(r_on, ind, logmv)

        for c, e in zip(codes, eps):
            if np.isfinite(e):
                hist[c].append(float(e))
                recent_eps[c].append(float(e))

        if d < start_ts:
            continue

        thr = float(np.nanquantile(eps, LEFT_TAIL_PCT)) if np.isfinite(eps).sum() >= 50 else -1e9

        # ivol panel for pool
        ivol_codes, ivols, mvs, inds = [], [], [], []
        for c in pool:
            h = hist.get(c)
            if not h or len(h) < MIN_OBS:
                continue
            if c in HARD_EXCLUDE:
                continue
            iv = float(np.std(h, ddof=1)) if len(h) >= 2 else np.nan
            if not np.isfinite(iv):
                continue
            ivol_codes.append(c)
            ivols.append(iv)
            mvs.append(mc.get(c, np.nan))
            inds.append(swm.get(c, "_UNK"))
        if len(ivol_codes) < 50:
            continue

        ivols = np.asarray(ivols, float)
        mvs = np.asarray(mvs, float)
        inds = np.asarray(inds, object)
        alpha_raw = -ivols
        domains = size_domain_arr(mvs)
        score_cal = domain_calibrate_arr(alpha_raw, domains)
        logmv2 = np.log(np.clip(np.where(np.isfinite(mvs), mvs, np.nanmedian(mvs)), 1.0, None))
        alpha = resid_cs(score_cal, inds, logmv2)
        alpha = domain_calibrate_arr(alpha, domains)

        # gates
        gates = []
        for c in ivol_codes:
            rec = recent_eps.get(c)
            bad = any(e <= thr for e in rec) if rec else False
            gates.append(0 if bad else 1)
        gates = np.asarray(gates, int)

        alpha_rows.append(pd.DataFrame({
            "date": d, "instrument": ivol_codes, "alpha": alpha,
            "size_domain": domains, "event_flag": 1, "ind": inds, "ivol": ivols,
        }))
        gate_rows.append(pd.DataFrame({
            "date": d, "instrument": ivol_codes, "gate": gates,
            "gate_reason": np.where(gates == 1, "ok", "on_left_tail"),
        }))

        if rebal_countdown <= 0:
            order = np.argsort(-alpha)  # high alpha first
            picked, ind_w = [], {}
            for j in order:
                if gates[j] != 1:
                    continue
                if len(picked) >= MAX_NAMES:
                    break
                ind = inds[j]
                if ind_w.get(ind, 0.0) + NAME_W > IND_CAP[universe] + 1e-12:
                    continue
                picked.append(ivol_codes[j])
                ind_w[ind] = ind_w.get(ind, 0.0) + NAME_W
            day_w = []
            if not picked:
                day_w.append((d, BALLAST, 1.0))
            else:
                for inst in picked:
                    day_w.append((d, inst, NAME_W))
                day_w.append((d, BALLAST, max(0.0, 1.0 - NAME_W * len(picked))))
            last_weights = day_w
            rebal_countdown = REBAL_EVERY
        rebal_countdown -= 1
        if last_weights is not None:
            for _, inst, w in last_weights:
                weight_rows.append((d, inst, w))

        if di % 60 == 0:
            print(f"  {ds} n={len(ivol_codes)} rss={rss_mb():.0f}MB", flush=True)

    alpha = pd.concat(alpha_rows, ignore_index=True) if alpha_rows else pd.DataFrame(
        columns=["date", "instrument", "alpha", "size_domain", "event_flag", "ind", "ivol"])
    gate = pd.concat(gate_rows, ignore_index=True) if gate_rows else pd.DataFrame(
        columns=["date", "instrument", "gate", "gate_reason"])
    weights = pd.DataFrame(weight_rows, columns=["date", "instrument", "target_weight"])
    if len(weights):
        weights["date"] = pd.to_datetime(weights["date"])
        s = weights.groupby("date")["target_weight"].transform("sum").replace(0, np.nan)
        weights["target_weight"] = weights["target_weight"] / s
        weights = weights[(weights["date"] >= start) & (weights["date"] <= end)]
    if len(alpha):
        alpha = alpha[(alpha["date"] >= start) & (alpha["date"] <= end)]
    if len(gate):
        gate["date"] = pd.to_datetime(gate["date"])
        gate = gate[(gate["date"] >= start) & (gate["date"] <= end)]

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
        alpha_direction="low_idio_overnight_ivol",
        fast_gate_separate=True,
        craft=["domain_calibrate", "slow_base_alpha", "fast_trade_gate", "resid_ind_size"],
        n_alpha_rows=int(len(alpha)),
        n_alpha_names=int(alpha["instrument"].nunique()) if len(alpha) else 0,
        n_gate_pass=int((gate["gate"] == 1).sum()) if len(gate) else 0,
        n_gate_total=int(len(gate)),
        n_weight_days=int(weights["date"].nunique()) if len(weights) else 0,
        alpha_path=str(ap),
        gate_path=str(gp),
        eval_weights_path=str(wp),
        alpha_sha256=hashlib.sha256(ap.read_bytes()).hexdigest(),
        ind_cap=IND_CAP[universe],
        ivol_win=IVOL_WIN,
        rebal_every=REBAL_EVERY,
        live=False,
        promotion_approved=False,
        peak_rss_mb=rss_mb(),
        stamp=stamp,
        arch_todo=["leaf_selfcheck_v3: delist terminal returns",
                   "leaf_selfcheck_v3: acceptance universe FULLA/HI_LIQ not static top300"],
    )
    mp = OUT_DIR / f"run_meta_{universe}_{window}_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if window == "x2":
        tag = "hiliq" if universe == "HILIQ" else "fulla"
        link = ROOT / "output/ai_factory" / f"g1g5_overnight_idio_ivol_{tag}_daily_weights_{stamp}.parquet"
        weights.to_parquet(link, index=False)
        (ROOT / "output/ai_factory" / f"g1g5_overnight_idio_ivol_{tag}_run_meta_{stamp}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        meta["selfcheck_weights_path"] = str(link)
        mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"  wrote {ap.name} n_alpha={meta['n_alpha_rows']} rss={rss_mb():.0f}MB", flush=True)
    gc.collect()
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", choices=["FULLA", "HILIQ", "both"], default="HILIQ")
    ap.add_argument("--window", choices=["sealed", "x2", "both"], default="x2")
    args = ap.parse_args()
    us = ["HILIQ", "FULLA"] if args.universe == "both" else [args.universe]
    ws = ["x2", "sealed"] if args.window == "both" else [args.window]
    results = []
    for u in us:
        for w in ws:
            results.append(run_one(u, w))
    summary = OUT_DIR / f"build_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("SUMMARY", summary, "peak_rss", max(r["peak_rss_mb"] for r in results))


if __name__ == "__main__":
    main()
