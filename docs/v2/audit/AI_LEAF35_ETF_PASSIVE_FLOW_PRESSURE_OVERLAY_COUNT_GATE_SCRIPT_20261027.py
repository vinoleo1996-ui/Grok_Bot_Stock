#!/usr/bin/env python3
"""Leaf35 ETF passive flow pressure overlay — lightweight HI_LIQ count gate.
NOT X2 / NOT selfcheck / NOT Book-Smoke. No PnL/IC/CAGR. live=false.
PRIMARY: form-A soft-penalty / exclusion-tilt overlay (NOT leaf26 full residual alpha).
APPROX: index weights month-end asof WITHOUT available_at; major broad ETFs only.
"""
from __future__ import annotations

import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
X2_START = pd.Timestamp("2024-06-03")
X2_END = pd.Timestamp("2026-10-09")
REBAL_EVERY = 20
TOP_Q = 0.20  # DRAFT: top 20% |pressure| exclusion / soft-penalty

MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
ETF_MAJOR = ROOT / "data/v2/etf/share_pit/etf_share_flow_pit_major.parquet"
IDX_W = ROOT / "data/v2/index_members/index_weight_csi300_500_1000.parquet"
MF_W = ROOT / "output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet"
OUT_JSON = ROOT / "output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json"

# Broad ETF <-> index map (leaf26 DRAFT primary; industry ETF forbidden as main axis)
ETF_INDEX = {
    "510300.SH": "000300.SH",
    "510500.SH": "000905.SH",
    "512100.SH": "000852.SH",
}


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


def load_mask_dates():
    t = pq.read_table(
        MASK_PATH,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", X2_START.to_datetime64()),
            ("date", "<=", X2_END.to_datetime64()),
            ("in_universe", "==", True),
        ],
    )
    df = t.to_pandas()
    df["date"] = pd.to_datetime(df["date"])
    df["instrument"] = df["instrument"].astype(str)
    dates = pd.DatetimeIndex(sorted(df["date"].unique()))
    return dates, df


def pick_rebal(dates: pd.DatetimeIndex):
    if len(dates) == 0:
        return []
    idx = list(range(0, len(dates), REBAL_EVERY))
    if idx[-1] != len(dates) - 1:
        idx.append(len(dates) - 1)
    return [pd.Timestamp(dates[i]) for i in idx]


def spearman_rho(a, b):
    if len(a) < 5:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.nanstd(ra) == 0 or np.nanstd(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def top_jaccard(codes_a, scores_a, codes_b, scores_b, k=20):
    if len(codes_a) == 0 or len(codes_b) == 0:
        return float("nan")
    sa = pd.Series(scores_a, index=codes_a)
    sb = pd.Series(scores_b, index=codes_b)
    ta = set(sa.nlargest(min(k, len(sa))).index)
    tb = set(sb.nlargest(min(k, len(sb))).index)
    u = ta | tb
    if not u:
        return float("nan")
    return float(len(ta & tb) / len(u))


def summarize_overlap(rows):
    rhos = [r["rho"] for r in rows if r.get("rho") is not None and np.isfinite(r["rho"])]
    js = [
        r["jaccard_top20"]
        for r in rows
        if r.get("jaccard_top20") is not None and np.isfinite(r["jaccard_top20"])
    ]
    return {
        "rho_mean": float(np.mean(rhos)) if rhos else None,
        "rho_max": float(np.max(rhos)) if rhos else None,
        "j20_mean": float(np.mean(js)) if js else None,
        "j20_max": float(np.max(js)) if js else None,
        "n_days_ok": len(rhos),
        "strength_filter_rho_mean_gt_0_5": bool(rhos and float(np.mean(rhos)) > 0.5),
        "hard_reject_j20_max_ge_0_7": bool(js and float(np.max(js)) >= 0.7),
        "per_day": rows,
    }


def load_etf_flows(dates):
    t = pq.read_table(
        ETF_MAJOR,
        columns=["ts_code", "trade_date", "d_share_wan", "flow_est_wan_yuan", "available_at"],
    )
    df = t.to_pandas()
    df = df[df["ts_code"].isin(list(ETF_INDEX.keys()))].copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["available_at"] = pd.to_datetime(df["available_at"])
    # PIT: available_at <= session end (use date+1 day 09:00 approx already in table)
    # For rebal day d, keep rows with trade_date==d AND available_at.normalize() <= d+1
    # Practical light gate: trade_date in rebal set; available_at date <= trade_date+1 (schema convention)
    want = set(pd.Timestamp(d) for d in dates)
    df = df[df["trade_date"].isin(want)].copy()
    df["flow"] = df["flow_est_wan_yuan"].astype(float)
    df["d_share"] = df["d_share_wan"].astype(float)
    # prefer flow_est; fallback d_share
    df["z_raw"] = df["flow"].where(df["flow"].notna(), df["d_share"])
    return df


def load_weights_month_end():
    t = pq.read_table(IDX_W)
    w = t.to_pandas()
    w["trade_date"] = pd.to_datetime(w["trade_date"])
    w["index_code"] = w["index_code"].astype(str)
    w["con_code"] = w["con_code"].astype(str)
    w["weight"] = w["weight"].astype(float) / 100.0  # percent -> fraction if needed
    # Detect scale: if typical sum ~100, divide; if ~1, keep
    # Check one month one index
    sample = w[(w["index_code"] == "000300.SH")].groupby("trade_date")["weight"].sum()
    med_sum = float(sample.median()) if len(sample) else 100.0
    if med_sum > 2.0:  # stored as percent 0-100
        pass  # already /100 above — wait we always /100; if was fraction we'd break
    # Re-check: reload raw
    return w, med_sum


def build_asof_weight_lookup(w: pd.DataFrame, med_sum_raw_before_div: float):
    # w.weight already divided by 100 once; if original was fraction, undo
    # Re-read carefully
    pass


def main() -> int:
    t0 = time.time()
    peak = rss_mb()
    mem0 = mem_available_gi()
    approx = [
        "index_weight_csi300_500_1000 has NO available_at; month-end trade_date asof backward (APPROX; leaf26 Data GAP rule A not applied as column)",
        "PRIMARY form-A overlay: top_q=0.20 high |pressure| soft-penalty/exclusion; NOT leaf26 g1g5_ashare_broad_etf_flow_stock_v1 full multi-layer residual alpha",
        "pressure_raw = sum_etf weight(i,index(etf),asof) * flow_est_wan_yuan (fallback d_share_wan); etf in {510300,510500,512100}",
        "leaf26-like raw reconstructed for disclosure; residualized leaf26 alpha ABSENT on disk -> residual Jaccard = GAP (not forged)",
        "leaf8a ind_etf_flow_rev FAIL / trades industry ETF themselves — no stock alpha product; Jaccard GAP",
        "overlap polarity leaf35_pref = -|pressure| (prefer low absolute passive pressure / keep) vs moneyflow_resid stock weights",
        "vs leaf26-like: diagnostic only (pref polarity can collapse when all p<=0); hard reject NOT applied; residual alpha GAP",
        "anti-iso vs leaf26 = delivery form A overlay/soft-penalty NOT full residual alpha; raw pressure magnitude shared by construction",
        "weight scale auto-detected; top_q NOT selected from returns; no PnL/IC/CAGR; no SW+style residual this pass",
    ]
    gaps = []

    dates, mask_df = load_mask_dates()
    peak = max(peak, rss_mb())
    rebal = pick_rebal(dates)
    if len(rebal) < 3:
        gaps.append("too_few_rebal_dates")

    if len(rebal) <= 6:
        sample_days = list(rebal)
    else:
        idxs = np.linspace(0, len(rebal) - 1, 6)
        sample_days = []
        seen = set()
        for i in idxs:
            d = rebal[int(round(i))]
            if d not in seen:
                seen.add(d)
                sample_days.append(d)

    # ETF flows on rebal dates
    etf = load_etf_flows(rebal)
    peak = max(peak, rss_mb())

    # Index weights
    wraw = pq.read_table(IDX_W).to_pandas()
    wraw["trade_date"] = pd.to_datetime(wraw["trade_date"])
    wraw["index_code"] = wraw["index_code"].astype(str)
    wraw["con_code"] = wraw["con_code"].astype(str)
    wraw["weight_raw"] = wraw["weight"].astype(float)
    sample_sum = (
        wraw[wraw["index_code"] == "000300.SH"].groupby("trade_date")["weight_raw"].sum().median()
    )
    if sample_sum > 2.0:
        wraw["w"] = wraw["weight_raw"] / 100.0
        weight_unit = "percent_div100"
    else:
        wraw["w"] = wraw["weight_raw"]
        weight_unit = "fraction"
    # month-end dates per index
    month_ends = sorted(wraw["trade_date"].unique())
    month_ends_ts = pd.DatetimeIndex(month_ends)

    def asof_month(d: pd.Timestamp) -> pd.Timestamp | None:
        # last month-end <= d (APPROX; no available_at lag)
        pos = month_ends_ts.searchsorted(pd.Timestamp(d), side="right") - 1
        if pos < 0:
            return None
        return pd.Timestamp(month_ends_ts[pos])

    mask_by_date = {d: set(g["instrument"].astype(str)) for d, g in mask_df.groupby("date")}

    # Pre-index weights by (index, month_end) -> Series con_code->w
    w_idx = {}
    for (ic, td), g in wraw.groupby(["index_code", "trade_date"]):
        w_idx[(str(ic), pd.Timestamp(td))] = g.set_index("con_code")["w"].astype(float)

    def pressure_on_day(d: pd.Timestamp) -> pd.Series:
        me = asof_month(d)
        if me is None:
            return pd.Series(dtype=float)
        day_etf = etf[etf["trade_date"] == pd.Timestamp(d)]
        if day_etf.empty:
            return pd.Series(dtype=float)
        acc = {}
        for _, row in day_etf.iterrows():
            etf_code = str(row["ts_code"])
            idx = ETF_INDEX.get(etf_code)
            if idx is None:
                continue
            z = row["z_raw"]
            if z is None or (isinstance(z, float) and not np.isfinite(z)):
                continue
            key = (idx, me)
            ws = w_idx.get(key)
            if ws is None:
                continue
            for con, wt in ws.items():
                if not np.isfinite(wt):
                    continue
                acc[con] = acc.get(con, 0.0) + float(wt) * float(z)
        if not acc:
            return pd.Series(dtype=float)
        return pd.Series(acc, dtype=float)

    cov = []
    cov_excl = []
    zero = 0
    names_any = set()
    hiliq_sizes = []
    pressure_cache = {}

    for d in rebal:
        univ = mask_by_date.get(pd.Timestamp(d), set())
        hiliq_sizes.append(len(univ))
        p = pressure_on_day(pd.Timestamp(d))
        pressure_cache[pd.Timestamp(d)] = p
        # mappable = in HI_LIQ and has pressure key (mapped via any index weight asof)
        # Also count names in HI_LIQ that appear in asof weight union even if z=0 all
        me = asof_month(pd.Timestamp(d))
        mapped = set()
        if me is not None:
            for idx in ("000300.SH", "000905.SH", "000852.SH"):
                ws = w_idx.get((idx, me))
                if ws is not None:
                    mapped.update(ws.index.astype(str))
        # Prefer pressure series index; if empty flows, still use mapped ∩ HI_LIQ as coverage
        if len(p) > 0:
            valid = set(p.index.astype(str)) & univ
            # require finite pressure
            valid = {c for c in valid if np.isfinite(p.get(c, np.nan))}
        else:
            valid = mapped & univ
            # no flow that day -> pressure undefined; count mapped as coverage only if we can assign 0
            # Strict: without ETF flow row, pressure not computable → not in valid
            valid = set()
        n = len(valid)
        cov.append(n)
        if n == 0:
            zero += 1
        else:
            names_any.update(valid)
            scores = p.reindex(list(valid)).astype(float).abs()
            thr = scores.quantile(1.0 - TOP_Q)
            n_ex = int((scores >= thr).sum())
            cov_excl.append(n_ex)
        peak = max(peak, rss_mb())

    cov_a = np.asarray(cov, dtype=float)
    excl_a = np.asarray(cov_excl, dtype=float) if cov_excl else np.asarray([], dtype=float)
    zero_frac = float(zero / len(cov)) if cov else 1.0

    def stats(a):
        if len(a) == 0:
            return {"median": None, "min": None, "p10": None, "mean": None, "n_days": 0}
        return {
            "median": float(np.median(a)),
            "min": float(np.min(a)),
            "p10": float(np.percentile(a, 10)),
            "mean": float(np.mean(a)),
            "n_days": int(len(a)),
        }

    # moneyflow_resid weights
    overlaps_raw = {"vs_moneyflow_resid": [], "vs_leaf26_like_raw": []}
    mf = None
    if MF_W.exists():
        try:
            mf = pq.read_table(MF_W, columns=["date", "instrument", "weight"]).to_pandas()
            mf["date"] = pd.to_datetime(mf["date"])
            mf["instrument"] = mf["instrument"].astype(str)
            # stocks only: exclude ETF-like 51xxxx / 15xxxx sleeve legs for fair stock overlap
            def is_stock(code: str) -> bool:
                # A-share stocks: 00/30 SZ, 60/68 SH typically; exclude 51/15/56/58 ETF prefixes
                pref = code.split(".")[0]
                if pref.startswith(("51", "15", "56", "58", "16", "50")) and not pref.startswith(
                    ("00", "30", "60", "68")
                ):
                    # 50xxxx corporate bonds / LOF — treat non 00/30/60/68 as non-stock for this gate
                    if pref.startswith(("00", "30", "60", "68")):
                        return True
                    return False
                return pref.startswith(("00", "30", "60", "68"))

            mf = mf[mf["instrument"].map(is_stock)].copy()
        except Exception as e:
            mf = None
            gaps.append(f"moneyflow_resid_load:{e}")
    else:
        gaps.append("moneyflow_resid_weights_ABSENT")

    gaps.append(
        "leaf26_residual_alpha_ABSENT — only leaf26-like RAW reconstructed; residual Jaccard not forged"
    )
    gaps.append(
        "leaf8a_stock_alpha_ABSENT — ind_etf_flow_rev FAIL / ETF-as-tradable; stock Jaccard GAP"
    )

    for d in sample_days:
        univ = mask_by_date.get(pd.Timestamp(d), set())
        p = pressure_cache.get(pd.Timestamp(d))
        if p is None or len(p) == 0:
            p = pressure_on_day(pd.Timestamp(d))
        valid = sorted(set(p.index.astype(str)) & univ)
        valid = [c for c in valid if np.isfinite(p.get(c, np.nan))]
        if len(valid) < 5:
            overlaps_raw["vs_moneyflow_resid"].append(
                {"date": str(d.date()), "n_common": 0, "rho": None, "jaccard_top20": None}
            )
            overlaps_raw["vs_leaf26_like_raw"].append(
                {"date": str(d.date()), "n_common": 0, "rho": None, "jaccard_top20": None}
            )
            continue
        pref = (-p.reindex(valid).astype(float).abs())  # leaf35 overlay preference
        l26 = p.reindex(valid).astype(float)  # leaf26-like raw (+pressure)

        # vs moneyflow
        if mf is None or len(mf) == 0:
            overlaps_raw["vs_moneyflow_resid"].append(
                {"date": str(d.date()), "n_common": 0, "rho": None, "jaccard_top20": None, "gap": True}
            )
        else:
            sub = mf[mf["date"] == pd.Timestamp(d)].dropna(subset=["weight"])
            # use weight as score; drop zeros for ranking? keep all for rho on common
            common = sorted(set(sub["instrument"]) & set(valid))
            if len(common) < 5:
                overlaps_raw["vs_moneyflow_resid"].append(
                    {
                        "date": str(d.date()),
                        "n_common": int(len(common)),
                        "rho": None,
                        "jaccard_top20": None,
                    }
                )
            else:
                xa = pref.reindex(common).to_numpy()
                xb = sub.set_index("instrument")["weight"].reindex(common).astype(float).to_numpy()
                m = np.isfinite(xa) & np.isfinite(xb)
                xa, xb = xa[m], xb[m]
                codes = [c for c, ok in zip(common, m) if ok]
                overlaps_raw["vs_moneyflow_resid"].append(
                    {
                        "date": str(d.date()),
                        "n_common": int(len(codes)),
                        "rho": spearman_rho(xa, xb),
                        "jaccard_top20": top_jaccard(codes, xa, codes, xb, 20),
                    }
                )

        # vs leaf26-like raw (polarity: overlay pref vs +pressure long intent)
        xa = pref.to_numpy()
        xb = l26.to_numpy()
        m = np.isfinite(xa) & np.isfinite(xb)
        codes = [c for c, ok in zip(valid, m) if ok]
        overlaps_raw["vs_leaf26_like_raw"].append(
            {
                "date": str(d.date()),
                "n_common": int(len(codes)),
                "rho": spearman_rho(xa[m], xb[m]),
                "jaccard_top20": top_jaccard(codes, xa[m], codes, xb[m], 20),
                "note": "leaf35_pref=-|p| vs leaf26_like=+p; raw magnitude shared",
            }
        )
        peak = max(peak, rss_mb())

    sum_mf = summarize_overlap(overlaps_raw["vs_moneyflow_resid"])
    sum_l26 = summarize_overlap(overlaps_raw["vs_leaf26_like_raw"])
    # Also compute exclusion-set vs leaf26-like high-+pressure long book (disclosure)
    excl_vs_l26_long = []
    for d in sample_days:
        univ = mask_by_date.get(pd.Timestamp(d), set())
        pser = pressure_cache.get(pd.Timestamp(d))
        if pser is None or len(pser) == 0:
            continue
        valid = [c for c in (set(pser.index.astype(str)) & univ) if np.isfinite(pser.get(c, np.nan))]
        if len(valid) < 20:
            continue
        abs_p = pser.reindex(valid).astype(float).abs()
        thr = abs_p.quantile(1.0 - TOP_Q)
        excl = set(abs_p[abs_p >= thr].index)
        long26 = set(pser.reindex(valid).astype(float).nlargest(min(20, len(valid))).index)
        # exclusion set size ~20% of univ; compare excl vs top20 long for disclosure Jaccard
        u = excl | long26
        j = float(len(excl & long26) / len(u)) if u else float("nan")
        excl_vs_l26_long.append({"date": str(d.date()), "jaccard_excl_vs_l26_top20": j, "n_excl": len(excl)})

    masked_median = stats(cov_a)["median"]
    gate_cov = masked_median is not None and masked_median >= 300 and zero_frac <= 0.05
    # HARD reject only vs external moneyflow_resid (J20>=0.7).
    # leaf26 residual alpha ABSENT — do NOT forge residual Jaccard.
    # leaf26-like RAW shares magnitude with pressure by construction; anti-iso = delivery form A
    # (overlay/soft-penalty), NOT raw-orthogonal. Preference-polarity J can collapse on all-redemption
    # days (-|p|==p when p<=0) — diagnostic only, NOT hard reject.
    hard_j_mf = bool(sum_mf.get("hard_reject_j20_max_ge_0_7"))
    hard_j = hard_j_mf
    gate_pass = bool(gate_cov and not hard_j)

    out = {
        "mechanism_tag": "g1g5_ashare_etf_passive_flow_pressure_overlay_v1",
        "leaf_intent": 35,
        "primary_choice": 1,
        "et_ts": "2026-10-27T12:42:00-04:00",
        "window": {"start": "2024-06-03", "end": "2026-10-09", "rebal_every": REBAL_EVERY},
        "top_q_exclusion": TOP_Q,
        "proxy": "pressure_raw=sum_etf w(i,idx,asof)*flow_est_wan_yuan; overlay=top_q |pressure| soft-penalty",
        "etf_index_map": ETF_INDEX,
        "weight_unit_detected": weight_unit,
        "weight_month_sum_median_000300": float(sample_sum),
        "coverage_mappable_pressure_hiliq": stats(cov_a),
        "coverage_excluded_topq_abs_pressure": stats(excl_a),
        "hiliq_universe_size": stats(np.asarray(hiliq_sizes, dtype=float)),
        "zero_frac_masked": zero_frac,
        "zero_days": int(zero),
        "n_rebal": len(rebal),
        "union_names_valid": len(names_any),
        "sample_days": [str(d.date()) for d in sample_days],
        "overlap_vs_moneyflow_resid": sum_mf,
        "overlap_vs_leaf26_like_raw": sum_l26,
        "overlap_excl_vs_leaf26_like_top20_long_disclosure": excl_vs_l26_long,
        "overlap_vs_leaf8a": {
            "status": "GAP",
            "reason": "ind_etf_flow_rev FAIL; no stock alpha parquet; Jaccard not forged",
        },
        "overlap_vs_leaf26_residual_alpha": {
            "status": "GAP",
            "reason": "leaf26 full residual alpha parquet ABSENT; raw reconstructed only; Jaccard not forged",
        },
        "gate_rule": (
            "masked_median>=300 AND zero_frac_masked<=0.05 AND "
            "jaccard_top20_max vs moneyflow_resid <0.7 (rho>0.5 strength-only); "
            "leaf26 residual alpha GAP; leaf26-like raw diagnostic-only (shared magnitude); leaf8a GAP"
        ),
        "gate_cov_pass": gate_cov,
        "gate_pass": gate_pass,
        "hard_reject_jaccard": hard_j,
        "hard_reject_moneyflow_only": hard_j_mf,
        "strength_filter": {
            "moneyflow_resid": sum_mf.get("strength_filter_rho_mean_gt_0_5"),
            "leaf26_like_raw_diag": sum_l26.get("strength_filter_rho_mean_gt_0_5"),
        },
        "approx": approx,
        "gaps": gaps,
        "peak_rss_mb": float(max(peak, rss_mb())),
        "mem_available_gi_start": float(mem0),
        "mem_available_gi_end": float(mem_available_gi()),
        "elapsed_sec": float(time.time() - t0),
        "sha": {
            "etf_major": sha256_file(ETF_MAJOR)[:8],
            "index_weight": sha256_file(IDX_W)[:8],
            "hiliq_mask": sha256_file(MASK_PATH)[:8],
            "moneyflow_resid_weights": sha256_file(MF_W)[:8] if MF_W.exists() else None,
        },
        "paths": {
            "etf_major": str(ETF_MAJOR.relative_to(ROOT)),
            "index_weight": str(IDX_W.relative_to(ROOT)),
            "hiliq_mask": str(MASK_PATH.relative_to(ROOT)),
            "moneyflow_resid_weights": str(MF_W.relative_to(ROOT)) if MF_W.exists() else None,
        },
        "dig": {
            "path": "output/d1/DIG_FACTOR_20261027_1235ET.md",
            "pin_in_doc": "814e8a68",
            "disk_sha8": sha256_file(ROOT / "output/d1/DIG_FACTOR_20261027_1235ET.md")[:8],
        },
        "leaf34_hold": {
            "ok": "178e90e9",
            "lift": "3fce510e",
            "receipt": "a37257b9",
            "rho_excess_approx": 0.960841,
            "status": "HOLD_CLOSED",
        },
        "EXECUTED_full_alpha": False,
        "ok_requested": False,
        "live": False,
        "leo_notify": False,
        "promotion_approved": False,
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
                "zero_frac": zero_frac,
                "peak_rss_mb": out["peak_rss_mb"],
                "j_mf_max": sum_mf.get("j20_max"),
                "j_l26_max": sum_l26.get("j20_max"),
                "rho_mf_mean": sum_mf.get("rho_mean"),
                "rho_l26_mean": sum_l26.get("rho_mean"),
                "out": str(OUT_JSON),
                "hard_reject_jaccard": hard_j,
                "sample_days": out["sample_days"],
                "excl_median": stats(excl_a)["median"],
                "sha": out["sha"],
                "weight_unit": weight_unit,
                "n_rebal": len(rebal),
                "etf_rows_rebal": int(len(etf)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
