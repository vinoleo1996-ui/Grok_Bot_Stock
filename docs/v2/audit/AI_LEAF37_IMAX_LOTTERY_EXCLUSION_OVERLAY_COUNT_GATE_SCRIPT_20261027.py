#!/usr/bin/env python3
"""Leaf37 IMAX/lottery exclusion overlay — lightweight HI_LIQ count gate.
NOT X2 / NOT selfcheck / NOT Book-Smoke. No PnL/IC/CAGR. live=false.
APPROX: IMAX_proxy = mean of largest 5 raw r_id in [t-19,t] (min 15 valid);
NOT full SW+logmv residual e_id (leaf24 prereg path).
Hard reject: Jaccard_max vs leaf18 / leaf27 high-risk tails >= 0.7.
"""
from __future__ import annotations

import gc
import hashlib
import json
import resource
import time
from pathlib import Path

import warnings

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
X2_START = pd.Timestamp("2024-06-03")
X2_END = pd.Timestamp("2026-10-09")
REBAL_EVERY = 20
TOP_Q = 0.20  # DRAFT freeze: top 20% high IMAX excluded; NOT from returns
WIN = 20
K_MAX = 5
MIN_VALID = 15
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
PANEL_DIR = ROOT / "output/ai_factory/panel_cache_v2_resumefix"
L18_ALPHA = ROOT / "output/ai_factory/leaf18_overnight_idio_ivol/alpha_HILIQ_x2_20261014_205327.parquet"
L18V_ALPHA = ROOT / "output/ai_factory/leaf18v_overnight_idio_ivol_lowto/alpha_HILIQ_x2_20261014_212630.parquet"
L27_ALPHA = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet"
L24_DIR = ROOT / "output/ai_factory/leaf24_imax_intraday"
OUT_JSON = ROOT / "output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json"
MECHANISM_TAG = "g1g5_ashare_imax_lottery_exclusion_overlay_v1"

COV_MEDIAN_MIN = 300.0
EXCL_MEDIAN_MIN = 30.0
ZERO_FRAC_MAX = 0.05
JACCARD_HARD = 0.7


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mem_available_gi() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / (1024 * 1024)
    except OSError:
        return float("nan")
    return float("nan")


def stats(a: np.ndarray) -> dict:
    if len(a) == 0:
        return {"median": None, "min": None, "p10": None, "p25": None, "p75": None, "mean": None, "n_days": 0}
    return {
        "median": float(np.median(a)),
        "min": float(np.min(a)),
        "p10": float(np.percentile(a, 10)),
        "p25": float(np.percentile(a, 25)),
        "p75": float(np.percentile(a, 75)),
        "mean": float(np.mean(a)),
        "n_days": int(len(a)),
    }


def rolling_imax(arr: np.ndarray, win: int = WIN, k: int = K_MAX, min_valid: int = MIN_VALID) -> np.ndarray:
    n = len(arr)
    out = np.full(n, np.nan)
    for i in range(n):
        s = max(0, i - win + 1)
        w = arr[s : i + 1]
        w = w[np.isfinite(w)]
        if len(w) < min_valid:
            continue
        out[i] = float(np.mean(np.partition(w, -k)[-k:])) if len(w) >= k else float(np.mean(w))
    return out


def load_alpha_on_dates(path: Path, dates):
    schema = pq.read_schema(path)
    names = [f.name for f in schema]
    date_col = "date" if "date" in names else "trade_date"
    inst_col = "instrument" if "instrument" in names else "ts_code"
    if "alpha" not in names:
        raise ValueError(f"no alpha col in {path}")
    field = schema.field(date_col)
    is_str = pa.types.is_string(field.type) or pa.types.is_large_string(field.type)
    cols = [date_col, inst_col, "alpha"]
    if is_str:
        t = pq.read_table(
            path,
            columns=cols,
            filters=[(date_col, ">=", min(dates).strftime("%Y-%m-%d")), (date_col, "<=", max(dates).strftime("%Y-%m-%d"))],
        )
    else:
        t = pq.read_table(
            path,
            columns=cols,
            filters=[
                (date_col, ">=", min(dates).to_datetime64()),
                (date_col, "<=", max(dates).to_datetime64()),
            ],
        )
    df = t.to_pandas()
    df[date_col] = pd.to_datetime(df[date_col])
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df[date_col].isin(want)].copy()
    df.rename(columns={date_col: "date", inst_col: "instrument"}, inplace=True)
    df["instrument"] = df["instrument"].astype(str)
    return df


def spearman_rho(a, b):
    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def jaccard(a: set, b: set) -> float:
    u = a | b
    if not u:
        return float("nan")
    return float(len(a & b) / len(u))


def summarize_overlap(rows):
    js = [r["jaccard"] for r in rows if r.get("jaccard") is not None and np.isfinite(r["jaccard"])]
    rhos = [r["rho"] for r in rows if r.get("rho") is not None and np.isfinite(r["rho"])]
    return {
        "jaccard_mean": float(np.mean(js)) if js else None,
        "jaccard_max": float(np.max(js)) if js else None,
        "rho_mean": float(np.mean(rhos)) if rhos else None,
        "rho_max": float(np.max(rhos)) if rhos else None,
        "n_days_ok": int(len(js)),
        "hard_reject_jaccard_max_ge_0_7": bool(js and float(np.max(js)) >= JACCARD_HARD),
        "strength_filter_rho_mean_gt_0_5": bool(rhos and float(np.mean(rhos)) > 0.5),
        "definition_zh": "剔除集=HI_LIQ top_q high IMAX_proxy；对照高风险尾=α 最低 top_q（α=−ivol/−IMAX 时低α=高风险）；ρ=Spearman(−IMAX_proxy, α)",
        "per_day": rows,
    }


def main() -> int:
    warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
    t0 = time.time()
    peak = rss_mb()
    mem0 = mem_available_gi()
    approx = [
        "IMAX_proxy = mean(largest 5 raw r_id in [t-19,t]) with >=15 valid HI_LIQ days; r_id=(1+ret)/(1+ret_on)-1 from cs_panel_v2_resumefix",
        "NOT full leaf24 path: daily e_id = CS OLS residual of r_id on SW L1 + logmv_{t-1}",
        "top_q=0.20 high-IMAX exclusion FROZEN intent — NOT selected from returns",
        "overlap: exclusion set vs leaf18/18v/27/24 bottom-q alpha (high-risk tail); rho = Spearman(-IMAX_proxy, alpha)",
        "no PnL/IC/CAGR; no full overlay land; no .ok",
    ]
    gaps = []

    # mask
    t = pq.read_table(
        MASK_PATH,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", pd.Timestamp("2023-10-01").to_datetime64()),
            ("date", "<=", X2_END.to_datetime64()),
            ("in_universe", "==", True),
        ],
    )
    mask = t.to_pandas()
    del t
    gc.collect()
    mask["date"] = pd.to_datetime(mask["date"])
    mask["instrument"] = mask["instrument"].astype(str)
    peak = max(peak, rss_mb())

    # panels
    cols = ["date", "instrument", "hiliq", "ret", "ret_on"]
    frames = []
    panel_sha = {}
    for y in (2023, 2024, 2025, 2026):
        p = PANEL_DIR / f"cs_panel_{y}.parquet"
        panel_sha[str(y)] = sha256_file(p)[:8]
        frames.append(pq.read_table(p, columns=cols).to_pandas())
    panel = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    panel["date"] = pd.to_datetime(panel["date"])
    panel["instrument"] = panel["instrument"].astype(str)
    panel = panel[(panel["date"] >= pd.Timestamp("2023-10-01")) & (panel["date"] <= X2_END)].copy()
    key = mask[["date", "instrument"]].drop_duplicates().assign(in_hiliq=True)
    panel = panel.merge(key, on=["date", "instrument"], how="left")
    panel["in_hiliq"] = panel["in_hiliq"].fillna(False)
    if panel["hiliq"].dtype == bool:
        panel["in_hiliq"] = panel["in_hiliq"] & panel["hiliq"].fillna(False)
    ret = panel["ret"].astype(float)
    ron = panel["ret_on"].astype(float)
    panel["r_id"] = (1.0 + ret) / (1.0 + ron) - 1.0
    panel.loc[ret.isna() | ron.isna() | ~np.isfinite(panel["r_id"]), "r_id"] = np.nan
    sub = panel.loc[panel["in_hiliq"] & panel["r_id"].notna(), ["date", "instrument", "r_id"]]
    del panel
    gc.collect()
    peak = max(peak, rss_mb())

    piv = sub.pivot_table(index="date", columns="instrument", values="r_id", aggfunc="last").sort_index()
    del sub
    gc.collect()
    imax_cols = {c: rolling_imax(piv[c].to_numpy(dtype=float)) for c in piv.columns}
    imax = pd.DataFrame(imax_cols, index=piv.index)
    del piv, imax_cols
    gc.collect()
    peak = max(peak, rss_mb())

    cal = pd.DatetimeIndex(sorted([d for d in imax.index if X2_START <= d <= X2_END]))
    idx = list(range(0, len(cal), REBAL_EVERY))
    if not idx:
        gaps.append("no_x2_calendar")
        rebal = []
    else:
        if idx[-1] != len(cal) - 1:
            idx.append(len(cal) - 1)
        rebal = [pd.Timestamp(cal[i]) for i in idx]

    if len(rebal) <= 6:
        sample_days = list(rebal)
    else:
        sample_days = []
        seen = set()
        for i in np.linspace(0, len(rebal) - 1, 6):
            d = rebal[int(round(i))]
            if d not in seen:
                seen.add(d)
                sample_days.append(d)

    mask_by = {d: set(g["instrument"].astype(str)) for d, g in mask.groupby("date")}
    cov = []
    excl_n = []
    zero = 0
    hiliq_sizes = []
    names_any = set()
    for d in rebal:
        univ = mask_by.get(pd.Timestamp(d), set())
        hiliq_sizes.append(len(univ))
        if d not in imax.index:
            cov.append(0)
            excl_n.append(0)
            zero += 1
            continue
        s = imax.loc[d].dropna()
        s = s[s.index.isin(univ)]
        n = int(len(s))
        cov.append(n)
        if n == 0:
            zero += 1
            excl_n.append(0)
        else:
            names_any.update(s.index.tolist())
            thr = float(s.quantile(1.0 - TOP_Q))
            excl_n.append(int((s >= thr).sum()))

    cov_a = np.asarray(cov, dtype=float)
    excl_a = np.asarray(excl_n, dtype=float)
    zero_frac = float(zero / len(cov)) if cov else 1.0

    # load alphas
    overlaps_raw = {"vs_leaf18": [], "vs_leaf18v": [], "vs_leaf27": [], "vs_leaf24": []}
    alphas = {}
    for key_name, path in (("leaf18", L18_ALPHA), ("leaf18v", L18V_ALPHA), ("leaf27", L27_ALPHA)):
        try:
            alphas[key_name] = load_alpha_on_dates(path, sample_days)
        except Exception as e:
            alphas[key_name] = pd.DataFrame()
            gaps.append(f"{key_name}_alpha_load:{e}")
    # leaf24 yearly
    try:
        frames24 = []
        for y in (2024, 2025, 2026):
            p = L24_DIR / f"alpha_HILIQ_{y}.parquet"
            if p.exists():
                frames24.append(load_alpha_on_dates(p, sample_days))
        alphas["leaf24"] = pd.concat(frames24, ignore_index=True) if frames24 else pd.DataFrame()
        if alphas["leaf24"].empty:
            gaps.append("leaf24_alpha_empty")
    except Exception as e:
        alphas["leaf24"] = pd.DataFrame()
        gaps.append(f"leaf24_alpha_load:{e}")
    peak = max(peak, rss_mb())

    # similarity check leaf18 vs 18v
    l18_vs_18v = None
    if len(alphas.get("leaf18", [])) and len(alphas.get("leaf18v", [])):
        mrg = alphas["leaf18"].merge(
            alphas["leaf18v"], on=["date", "instrument"], how="inner", suffixes=("_18", "_18v")
        )
        if len(mrg):
            l18_vs_18v = {
                "n_common_rows": int(len(mrg)),
                "alpha_corr": float(mrg["alpha_18"].corr(mrg["alpha_18v"])),
                "alpha_mae": float((mrg["alpha_18"] - mrg["alpha_18v"]).abs().mean()),
            }

    for d in sample_days:
        univ = mask_by.get(pd.Timestamp(d), set())
        s = imax.loc[d].dropna() if d in imax.index else pd.Series(dtype=float)
        s = s[s.index.isin(univ)]
        if len(s) < 10:
            for k in overlaps_raw:
                overlaps_raw[k].append({"date": str(d.date()), "n_excl": 0, "jaccard": None, "rho": None})
            continue
        thr = float(s.quantile(1.0 - TOP_Q))
        excl = set(s[s >= thr].index)

        def one(vs_key, adf):
            if adf is None or len(adf) == 0:
                overlaps_raw[vs_key].append(
                    {"date": str(d.date()), "n_excl": int(len(excl)), "jaccard": None, "rho": None, "gap": True}
                )
                return
            suba = adf[adf["date"] == pd.Timestamp(d)].dropna(subset=["alpha"])
            suba = suba[suba["instrument"].isin(univ)]
            if len(suba) < 10:
                overlaps_raw[vs_key].append(
                    {"date": str(d.date()), "n_excl": int(len(excl)), "jaccard": None, "rho": None, "n_alpha": int(len(suba))}
                )
                return
            thr_lo = float(suba["alpha"].quantile(TOP_Q))
            hi_risk = set(suba.loc[suba["alpha"] <= thr_lo, "instrument"].astype(str))
            common = sorted(set(s.index) & set(suba["instrument"].astype(str)))
            xa = (-s.reindex(common)).to_numpy(dtype=float)
            xb = suba.set_index("instrument")["alpha"].reindex(common).astype(float).to_numpy()
            m = np.isfinite(xa) & np.isfinite(xb)
            overlaps_raw[vs_key].append(
                {
                    "date": str(d.date()),
                    "n_excl": int(len(excl)),
                    "n_hi_risk_tail": int(len(hi_risk)),
                    "n_intersect": int(len(excl & hi_risk)),
                    "jaccard": jaccard(excl, hi_risk),
                    "rho": spearman_rho(xa[m], xb[m]) if m.sum() >= 5 else None,
                    "n_common_score": int(m.sum()),
                }
            )

        one("vs_leaf18", alphas.get("leaf18"))
        one("vs_leaf18v", alphas.get("leaf18v"))
        one("vs_leaf27", alphas.get("leaf27"))
        one("vs_leaf24", alphas.get("leaf24"))

    sum18 = summarize_overlap(overlaps_raw["vs_leaf18"])
    sum18v = summarize_overlap(overlaps_raw["vs_leaf18v"])
    sum27 = summarize_overlap(overlaps_raw["vs_leaf27"])
    sum24 = summarize_overlap(overlaps_raw["vs_leaf24"])

    masked_median = stats(cov_a)["median"]
    excl_median = stats(excl_a)["median"]
    gate_cov = bool(
        masked_median is not None
        and masked_median >= COV_MEDIAN_MIN
        and excl_median is not None
        and excl_median >= EXCL_MEDIAN_MIN
        and zero_frac <= ZERO_FRAC_MAX
    )
    hard_j = bool(
        sum18.get("hard_reject_jaccard_max_ge_0_7")
        or sum27.get("hard_reject_jaccard_max_ge_0_7")
    )
    # leaf18v same family — also hard if >=0.7
    hard_j_18v = bool(sum18v.get("hard_reject_jaccard_max_ge_0_7"))
    hard_j = bool(hard_j or hard_j_18v)
    gate_pass = bool(gate_cov and not hard_j)

    alt_suggest = None
    if not gate_pass:
        alt_suggest = (
            "PRIMARY 计数/同构闸未过：建议主改派备选 (B) 行业级客户动量（先 IO 表 PIT 可得性）。"
            "本拍勿自开备选 B who_pays。"
        )

    peak = max(peak, rss_mb())
    out = {
        "mechanism_tag": MECHANISM_TAG,
        "leaf_intent": 37,
        "prior_leaf36": "inquiry_letter_exclusion_overlay HOLD CLOSED; redeploy alt A IMAX lottery exclusion",
        "et_ts": "2026-10-27T16:45:00-04:00",
        "window": {"start": "2024-06-03", "end": "2026-10-09", "rebal_every": REBAL_EVERY},
        "top_q_exclusion": TOP_Q,
        "imax_spec": {
            "proxy": "IMAX_proxy=mean(top5 raw r_id in 20d; min_valid=15)",
            "r_id": "(1+ret)/(1+ret_on)-1",
            "full_residual_e_id": False,
            "approx": True,
        },
        "coverage_computable_imax_hiliq": stats(cov_a),
        "coverage_excluded_topq": stats(excl_a),
        "hiliq_universe_size": stats(np.asarray(hiliq_sizes, dtype=float)),
        "zero_frac_masked": zero_frac,
        "zero_days": int(zero),
        "n_rebal": len(rebal),
        "union_names_computable": len(names_any),
        "sample_days": [str(d.date()) for d in sample_days],
        "overlap_vs_leaf18": sum18,
        "overlap_vs_leaf18v": sum18v,
        "overlap_vs_leaf27": sum27,
        "overlap_vs_leaf24_disclose": sum24,
        "leaf18_vs_leaf18v_alpha": l18_vs_18v,
        "gate_rule": (
            f"computable_median>={COV_MEDIAN_MIN} AND excl_median>={EXCL_MEDIAN_MIN} "
            f"AND zero_frac<={ZERO_FRAC_MAX} AND jaccard_max vs leaf18/18v/27 <{JACCARD_HARD} "
            f"(rho>0.5 strength-filter disclose-only; leaf24 disclose-only not hard)"
        ),
        "gate_cov_pass": gate_cov,
        "gate_pass": gate_pass,
        "hard_reject_jaccard": hard_j,
        "strength_filter": {
            "leaf18": sum18.get("strength_filter_rho_mean_gt_0_5"),
            "leaf18v": sum18v.get("strength_filter_rho_mean_gt_0_5"),
            "leaf27": sum27.get("strength_filter_rho_mean_gt_0_5"),
            "leaf24": sum24.get("strength_filter_rho_mean_gt_0_5"),
        },
        "alt_suggest_zh": alt_suggest,
        "approx": approx,
        "gaps": gaps,
        "peak_rss_mb": float(peak),
        "mem_available_gi_start": float(mem0),
        "mem_available_gi_end": float(mem_available_gi()),
        "elapsed_sec": float(time.time() - t0),
        "sha": {
            "hiliq_mask": sha256_file(MASK_PATH)[:8],
            "panel_by_year": panel_sha,
            "leaf18_alpha": sha256_file(L18_ALPHA)[:8] if L18_ALPHA.exists() else None,
            "leaf18v_alpha": sha256_file(L18V_ALPHA)[:8] if L18V_ALPHA.exists() else None,
            "leaf27_alpha": sha256_file(L27_ALPHA)[:8] if L27_ALPHA.exists() else None,
            "leaf24_alpha_2024": sha256_file(L24_DIR / "alpha_HILIQ_2024.parquet")[:8]
            if (L24_DIR / "alpha_HILIQ_2024.parquet").exists()
            else None,
            "leaf24_alpha_2025": sha256_file(L24_DIR / "alpha_HILIQ_2025.parquet")[:8]
            if (L24_DIR / "alpha_HILIQ_2025.parquet").exists()
            else None,
            "leaf24_alpha_2026": sha256_file(L24_DIR / "alpha_HILIQ_2026.parquet")[:8]
            if (L24_DIR / "alpha_HILIQ_2026.parquet").exists()
            else None,
        },
        "paths": {
            "hiliq_mask": str(MASK_PATH.relative_to(ROOT)),
            "panel_dir": str(PANEL_DIR.relative_to(ROOT)),
            "leaf18_alpha": str(L18_ALPHA.relative_to(ROOT)),
            "leaf18v_alpha": str(L18V_ALPHA.relative_to(ROOT)),
            "leaf27_alpha": str(L27_ALPHA.relative_to(ROOT)),
            "leaf24_dir": str(L24_DIR.relative_to(ROOT)),
        },
        "EXECUTED_full_alpha": False,
        "ok_requested": False,
        "live": False,
        "leo_notify": False,
        "dig_sha8": "74234fca",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)
    print(
        json.dumps(
            {
                "gate_pass": gate_pass,
                "masked_median": masked_median,
                "excl_median": excl_median,
                "zero_frac": zero_frac,
                "j18_max": sum18.get("jaccard_max"),
                "j27_max": sum27.get("jaccard_max"),
                "j24_max": sum24.get("jaccard_max"),
                "rho18_mean": sum18.get("rho_mean"),
                "rho27_mean": sum27.get("rho_mean"),
                "hard_reject_jaccard": hard_j,
                "peak_rss_mb": out["peak_rss_mb"],
                "l18_vs_18v": l18_vs_18v,
                "out": str(OUT_JSON),
                "sha": out["sha"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
