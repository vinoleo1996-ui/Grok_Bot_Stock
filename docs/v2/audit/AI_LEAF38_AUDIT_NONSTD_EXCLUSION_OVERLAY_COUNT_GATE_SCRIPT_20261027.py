#!/usr/bin/env python3
"""Leaf38 audit non-standard opinion exclusion overlay — HI_LIQ count gate.
NOT X2 / NOT selfcheck / NOT Book-Smoke. No PnL/IC/CAGR. live=false.
PRIMARY: outstanding nonstd audit opinion exclusion overlay (NOT mainline alpha).
PIT state: latest available audit opinion for name is nonstd → exclude from HI_LIQ mask.
Jaccard hard gate vs FAIL negevent AND leaf36 inquiry exclusion (>0.5 reject).
Thickness (write-dead; NOT blind copy median>=300):
  daily_excl_median>=30 AND frac(daily>=10)>=0.60 AND zero_frac<=0.50
"""
from __future__ import annotations

import gc
import hashlib
import json
import resource
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path("/workspace/QuantLab")
X2_START = pd.Timestamp("2024-06-03")
X2_END = pd.Timestamp("2026-10-09")
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
AUD_PATH = ROOT / "data/v2/audit/audit_opinion_pit_tushare.parquet"
ANN_MAIN = ROOT / "data/v2/events/announcements_classified_pit.parquet"
ANN_POST = ROOT / "data/v2/events/announcements_classified_pit_post202406.parquet"
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
NEGEVENT_W = ROOT / "output/ai_factory/g1g5_capacity_adv_negevent_daily_weights_20261014_010218.parquet"
NEGEVENT_META = ROOT / "output/ai_factory/g1g5_capacity_adv_negevent_run_meta_20261014_010218.json"
OUT_JSON = ROOT / "output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json"
BALLAST = "510300.SH"
MECHANISM_TAG = "g1g5_ashare_audit_nonstd_exclusion_overlay_v1"

# leaf36 FIN filter (rebuild for Jaccard only)
FIN_KW = r"年报|半年报|季报|财务|会计|审计|业绩|应收|存货|商誉|收入|利润|信息披露|监管工作函"
REORG_KW = r"重组|重大资产重组|吸收合并|借壳"
REPLY_NOISE_KW = r"回函|回复|核查说明"
ISSUER_KW = r"收到|证券交易所|深圳证券交易所|上海证券交易所|北京证券交易所|监管工作函|问询函的公告|关注函的公告"
ABNORMAL_KW = r"异常波动"
CBOND_KW = r"可转债|可转换公司债券"
TITLE_CORE_KW = r"问询函|关注函"
LEAF36_WIN = 20

COV_MEDIAN_MIN = 30.0
FRAC_GE10_MIN = 0.60
ZERO_FRAC_MAX = 0.50
JACCARD_MAX_HARD = 0.5


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
        return {"median": None, "min": None, "p25": None, "p75": None, "mean": None, "n_days": 0}
    return {
        "median": float(np.median(a)),
        "min": float(np.min(a)),
        "p25": float(np.percentile(a, 25)),
        "p75": float(np.percentile(a, 75)),
        "mean": float(np.mean(a)),
        "n_days": int(len(a)),
    }


def t1_of(cal_full: pd.DatetimeIndex, d) -> pd.Timestamp | None:
    i = int(cal_full.searchsorted(pd.Timestamp(d), side="right"))
    if i >= len(cal_full):
        return None
    return cal_full[i]


def build_leaf38_excl(
    a: pd.DataFrame, cal_full: pd.DatetimeIndex, cal: pd.DatetimeIndex, mask_by: dict
) -> tuple[dict, dict]:
    """PIT: exclude if latest opinion with effective_from=T1(available_at) <= day is nonstd."""
    a = a.sort_values(["instrument", "d"]).copy()
    efs = [t1_of(cal_full, d) for d in a["d"]]
    a["ef"] = efs
    a = a.dropna(subset=["ef"])
    recs: dict[str, list] = defaultdict(list)
    for r in a.itertuples():
        recs[str(r.instrument)].append((r.ef, bool(r.is_non_standard), str(r.audit_result)))

    excl = {d: set() for d in cal}
    n_state_true = 0
    funnel_ns_events = int(a["is_non_standard"].sum())
    for d in cal:
        uni = mask_by[d]
        for inst in uni:
            hist = recs.get(inst)
            if not hist:
                continue
            last_ns = None
            for ef, ns, _ in hist:
                if ef <= d:
                    last_ns = ns
                else:
                    break
            if last_ns is True:
                excl[d].add(inst)
                n_state_true += 1
    meta = {
        "definition_zh": "最新可用审计意见（available_at→T1 生效）为非标则剔除；下一份意见（标准或非标）T1 起改判",
        "n_opinion_rows": int(len(a)),
        "n_nonstd_rows": funnel_ns_events,
        "n_state_true_name_days": n_state_true,
    }
    return excl, meta


def held_cut_pairs() -> tuple[set, dict]:
    cols = ["date", "instrument", "target_weight"]
    base = pd.read_parquet(CAP_ADV, columns=cols)
    neg = pd.read_parquet(NEGEVENT_W, columns=cols)
    base["date"] = pd.to_datetime(base["date"])
    neg["date"] = pd.to_datetime(neg["date"])
    base = base[(base["date"] >= X2_START) & (base["date"] <= X2_END) & (base["instrument"] != BALLAST)]
    neg = neg[(neg["date"] >= X2_START) & (neg["date"] <= X2_END) & (neg["instrument"] != BALLAST)]
    merged = base.merge(neg, on=["date", "instrument"], how="outer", suffixes=("_b", "_n")).fillna(0.0)
    del base, neg
    gc.collect()
    cut = merged[(merged["target_weight_b"] > 0) & (merged["target_weight_n"] <= 1e-12)]
    pairs = set(zip(cut["date"], cut["instrument"].astype(str)))
    meta = {"held_cut_name_days": int(len(cut)), "held_cut_unique_dates": int(cut["date"].nunique())}
    del merged, cut
    gc.collect()
    return pairs, meta


def rebuild_e234_and_leaf36(
    cal_full: pd.DatetimeIndex, cal: pd.DatetimeIndex, hiliq_names: set
) -> tuple[set, dict, set, dict]:
    frames = []
    for p in (ANN_MAIN, ANN_POST):
        t = pq.read_table(p, columns=["instrument", "event_type", "available_at", "ann_title"])
        frames.append(t.to_pandas())
    a = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    a["instrument"] = a["instrument"].astype(str)
    a["d"] = a["available_at"].dt.tz_localize(None).dt.normalize()
    a = a.drop_duplicates(["instrument", "event_type", "d", "ann_title"])
    title = a["ann_title"].fillna("")

    # E2/E3/E4
    m2 = (a["event_type"] == "insider_decrease") & ~title.str.contains(
        "完毕|结果|终止|可转换公司债券|不减持|未减持|届满|进展", regex=True
    )
    m3 = (a["event_type"] == "earnings_miss") & ~title.str.contains("更正|补充|摘要|英文", regex=True)
    m4 = (
        (
            (a["event_type"] == "penalty")
            & title.str.contains("立案|行政处罚|处罚事先告知|纪律处分", regex=True)
            & ~title.str.contains("不存在", regex=True)
        )
        | (title.str.contains("风险警示|终止上市风险", regex=True) & ~title.str.contains("撤销", regex=True))
    )
    wins = {"E2": 10, "E3": 20, "E4": 20}
    e_pairs: set = set()
    e_counts = {}
    for tag, mk in (("E2", m2), ("E3", m3), ("E4", m4)):
        sub = a.loc[mk, ["instrument", "d"]].drop_duplicates()
        sub = sub[(sub["d"] >= pd.Timestamp("2023-10-01")) & (sub["d"] <= X2_END)]
        n0 = len(e_pairs)
        for r in sub.itertuples():
            if r.instrument not in hiliq_names:
                continue
            s = int(cal_full.searchsorted(pd.Timestamp(r.d), side="right"))
            if s >= len(cal_full):
                continue
            e = min(s + wins[tag] - 1, len(cal_full) - 1)
            for i in range(s, e + 1):
                d = cal_full[i]
                if X2_START <= d <= X2_END:
                    e_pairs.add((d, r.instrument))
        e_counts[tag] = len(e_pairs) - n0
    e_counts["total_pairs"] = len(e_pairs)

    # leaf36 primary
    m_base = (a["event_type"] == "inquiry_letter") & title.str.contains(TITLE_CORE_KW, regex=True)
    m_fin = title.str.contains(FIN_KW, regex=True)
    m_reorg = title.str.contains(REORG_KW, regex=True)
    m_reply = title.str.contains(REPLY_NOISE_KW, regex=True)
    m_issuer = title.str.contains(ISSUER_KW, regex=True)
    m_abn = title.str.contains(ABNORMAL_KW, regex=True)
    m_cb = title.str.contains(CBOND_KW, regex=True)
    primary = m_base & m_fin & ~m_reorg & ~m_abn & ~m_cb & ~(m_reply & ~m_issuer)
    ev = a.loc[primary, ["instrument", "d"]].drop_duplicates()
    ev = ev[(ev["d"] >= pd.Timestamp("2023-10-01")) & (ev["d"] <= X2_END)]
    l36: set = set()
    n_win = 0
    for r in ev.itertuples():
        if r.instrument not in hiliq_names:
            continue
        s = int(cal_full.searchsorted(pd.Timestamp(r.d), side="right"))
        if s >= len(cal_full):
            continue
        e = min(s + LEAF36_WIN - 1, len(cal_full) - 1)
        for i in range(s, e + 1):
            d = cal_full[i]
            if X2_START <= d <= X2_END:
                l36.add((d, r.instrument))
        n_win += 1
    l36_meta = {
        "n_primary_events": int(len(ev)),
        "n_windows_applied": n_win,
        "n_pairs": len(l36),
        "win": LEAF36_WIN,
        "method": "rebuild leaf36 FIN inquiry exclusion (same funnel as leaf36 COUNT)",
    }
    del a
    gc.collect()
    return e_pairs, e_counts, l36, l36_meta


def daily_jaccard(excl: dict, other_pairs: set, cal: pd.DatetimeIndex, mask_by: dict) -> dict:
    by = defaultdict(set)
    for d, inst in other_pairs:
        by[d].add(inst)
    js = []
    for d in cal:
        a = excl[d] & mask_by[d]
        b = by[d] & mask_by[d]
        if not a and not b:
            js.append(0.0)
            continue
        inter = len(a & b)
        uni = len(a | b)
        js.append(inter / uni if uni else 0.0)
    arr = np.asarray(js, dtype=float)
    hit = np.asarray([len(excl[d] & mask_by[d]) > 0 for d in cal])
    return {
        "all_days": {
            "n": int(len(arr)),
            "mean": float(arr.mean()) if len(arr) else None,
            "max": float(arr.max()) if len(arr) else None,
            "median": float(np.median(arr)) if len(arr) else None,
        },
        "leaf38_hit_days": {
            "n": int(hit.sum()),
            "mean": float(arr[hit].mean()) if hit.any() else None,
            "max": float(arr[hit].max()) if hit.any() else None,
            "median": float(np.median(arr[hit])) if hit.any() else None,
        },
    }


def main() -> int:
    t0 = time.time()
    peak = rss_mb()
    mem0 = mem_available_gi()
    approx = [
        "PIT state = latest audit opinion effective_from T1(available_at) with is_non_standard=True",
        "instrument map = ts_code (600xxx.SH) matching HI_LIQ mask; instrument_id sh.xxx not used for join",
        "negevent Jaccard APPROX = held-cut ∪ E2/E3/E4 rebuild (no E1 share_float; same as leaf36)",
        "leaf36 Jaccard = rebuild FIN inquiry exclusion WIN=20 (same funnel)",
        "no PnL/IC/CAGR; no full overlay parquet; no .ok; not X2",
        "thickness thresholds write-dead from leaf36 median=6 FAIL lesson; NOT blind copy median>=300",
    ]
    gaps = [
        "未算 vs 叶34/35/37 Jaccard（X2 阶段补）",
        "E1 share_float 未重建进 negevent 对照",
        "软惩罚连续分 + SW+style 未构建",
    ]

    t = pq.read_table(
        MASK_PATH,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", pd.Timestamp("2023-01-01").to_datetime64()),
            ("date", "<=", X2_END.to_datetime64()),
            ("in_universe", "==", True),
        ],
    )
    mask_all = t.to_pandas()
    del t
    gc.collect()
    mask_all["date"] = pd.to_datetime(mask_all["date"])
    mask_all["instrument"] = mask_all["instrument"].astype(str)
    cal_full = pd.DatetimeIndex(sorted(mask_all["date"].unique()))
    cal = cal_full[(cal_full >= X2_START) & (cal_full <= X2_END)]
    mask = mask_all[(mask_all["date"] >= X2_START) & (mask_all["date"] <= X2_END)]
    hiliq_names = set(mask["instrument"].unique())
    mask_by = {d: set(g["instrument"]) for d, g in mask.groupby("date")}
    hiliq_sizes = np.asarray([len(mask_by[d]) for d in cal], dtype=float)
    peak = max(peak, rss_mb())

    aud = pd.read_parquet(
        AUD_PATH, columns=["ts_code", "available_at", "is_non_standard", "audit_result"]
    )
    aud["instrument"] = aud["ts_code"].astype(str)
    aud["d"] = pd.to_datetime(aud["available_at"]).dt.tz_localize(None).dt.normalize()
    n_nonstd = int(aud["is_non_standard"].sum())
    n_nonstd_inst = int(aud.loc[aud["is_non_standard"], "instrument"].nunique())
    by_year = {
        str(k): int(v)
        for k, v in aud.loc[aud["is_non_standard"]].groupby(aud.loc[aud["is_non_standard"], "d"].dt.year).size().items()
    }
    result_breakdown = (
        aud.loc[aud["is_non_standard"], "audit_result"].value_counts().to_dict()
    )
    peak = max(peak, rss_mb())

    excl, excl_meta = build_leaf38_excl(aud, cal_full, cal, mask_by)
    del aud
    gc.collect()
    daily_n = np.asarray([len(excl[d] & mask_by[d]) for d in cal], dtype=float)
    hit = daily_n > 0
    zero_frac = float((~hit).mean()) if len(daily_n) else 1.0
    frac_ge10 = float((daily_n >= 10).mean()) if len(daily_n) else 0.0
    frac_ge30 = float((daily_n >= 30).mean()) if len(daily_n) else 0.0
    cov_all = stats(daily_n)
    cov_hit = stats(daily_n[hit]) if hit.any() else stats(np.asarray([], dtype=float))

    # negevent fail honesty
    negevent_fail = {
        "status": "FAIL",
        "note_zh": "negevent 已 FAIL：CAGR/MDD 未优于主干 capacity_adv（见 run_meta selfcheck）",
    }
    try:
        meta = json.loads(NEGEVENT_META.read_text())
        sc = meta.get("selfcheck", {})
        negevent_fail.update(
            {
                "cagr_cap": sc.get("cagr_cap"),
                "cagr_neg": sc.get("cagr_neg"),
                "mdd_cap": sc.get("mdd_cap"),
                "mdd_neg": sc.get("mdd_neg"),
                "better_cagr": bool(
                    sc.get("cagr_neg") is not None
                    and sc.get("cagr_cap") is not None
                    and sc["cagr_neg"] > sc["cagr_cap"]
                ),
                "better_mdd": bool(
                    sc.get("mdd_neg") is not None
                    and sc.get("mdd_cap") is not None
                    and sc["mdd_neg"] > sc["mdd_cap"]
                ),
                "run_meta_sha8": sha256_file(NEGEVENT_META)[:8],
            }
        )
        if negevent_fail["better_cagr"] or negevent_fail["better_mdd"]:
            negevent_fail["status"] = "NOT_STRICT_FAIL_ON_BOTH"
    except Exception as e:
        gaps.append(f"negevent_meta:{e}")

    cut_pairs, cut_meta = held_cut_pairs()
    peak = max(peak, rss_mb())
    e234_pairs, e234_counts, l36_pairs, l36_meta = rebuild_e234_and_leaf36(
        cal_full, cal, hiliq_names
    )
    approx_neg = cut_pairs | e234_pairs
    j_neg = daily_jaccard(excl, approx_neg, cal, mask_by)
    j_l36 = daily_jaccard(excl, l36_pairs, cal, mask_by)
    peak = max(peak, rss_mb())

    jmax_neg = j_neg["leaf38_hit_days"]["max"] or 0.0
    jmax_l36 = j_l36["leaf38_hit_days"]["max"] or 0.0
    hard_reject = bool(jmax_neg > JACCARD_MAX_HARD or jmax_l36 > JACCARD_MAX_HARD)
    gate_cov = bool(
        cov_all["median"] is not None
        and cov_all["median"] >= COV_MEDIAN_MIN
        and frac_ge10 >= FRAC_GE10_MIN
        and zero_frac <= ZERO_FRAC_MAX
    )
    gate_pass = bool(gate_cov and not hard_reject)

    aud_sha = sha256_file(AUD_PATH)
    mask_sha = sha256_file(MASK_PATH)
    cap_sha = sha256_file(CAP_ADV)
    negw_sha = sha256_file(NEGEVENT_W)
    negm_sha = sha256_file(NEGEVENT_META)
    annm_sha = sha256_file(ANN_MAIN)
    annp_sha = sha256_file(ANN_POST)
    out = {
        "mechanism_tag": MECHANISM_TAG,
        "leaf_intent": 38,
        "et_ts": "2026-10-27T20:40:00-04:00",
        "window": {"start": str(X2_START.date()), "end": str(X2_END.date())},
        "delivery": "daily_exclusion_mask_overlay_NOT_mainline_alpha",
        "exclusion_definition_zh": excl_meta["definition_zh"],
        "source": {
            "path": str(AUD_PATH.relative_to(ROOT)),
            "sha8": aud_sha[:8],
            "sha256": aud_sha,
            "n_rows_total": excl_meta["n_opinion_rows"],
            "n_nonstd_rows": n_nonstd,
            "n_nonstd_instruments": n_nonstd_inst,
            "nonstd_by_year": by_year,
            "audit_result_breakdown_nonstd": {str(k): int(v) for k, v in result_breakdown.items()},
        },
        "n_state_true_name_days_x2_hiliq": excl_meta["n_state_true_name_days"],
        "coverage_daily_exclusion_names_hiliq": cov_all,
        "coverage_on_hit_days": cov_hit,
        "hit_day_frac": float(hit.mean()) if len(hit) else 0.0,
        "zero_frac_masked": zero_frac,
        "frac_days_excl_ge10": frac_ge10,
        "frac_days_excl_ge30": frac_ge30,
        "n_x2_cal_days": int(len(cal)),
        "n_hit_days": int(hit.sum()),
        "hiliq_universe_size": stats(hiliq_sizes),
        "jaccard_vs_negevent": {
            "method": "APPROX held-cut ∪ E2/E3/E4 rebuilt; hard metric=max on leaf38-hit days",
            **j_neg,
            "held_cut": cut_meta,
            "e234_rebuild": e234_counts,
            "approx_neg_pairs": len(approx_neg),
            "e1_share_float_rebuilt": False,
        },
        "jaccard_vs_leaf36": {
            "method": l36_meta["method"],
            **j_l36,
            "leaf36_meta": l36_meta,
        },
        "jaccard_max_vs_negevent": jmax_neg,
        "jaccard_max_vs_leaf36": jmax_l36,
        "negevent_prior_fail": negevent_fail,
        "gate_rule": (
            f"daily_excl_median>={COV_MEDIAN_MIN} AND frac(daily>=10)>={FRAC_GE10_MIN} "
            f"AND zero_frac<={ZERO_FRAC_MAX} AND jaccard_max_vs_negevent<={JACCARD_MAX_HARD} "
            f"AND jaccard_max_vs_leaf36<={JACCARD_MAX_HARD} (hard reject if either >{JACCARD_MAX_HARD}; "
            "metric=max on leaf38-hit days)"
        ),
        "coverage_threshold_rationale_zh": (
            "叶36 问询函剔除 median=6 FAIL；勿盲抄叶34/35 median≥300。"
            "本叶写死：触窗日剔除名全日 median≥30 且 ≥60% 交易日剔除名≥10 且 zero_frac≤0.50。"
            "机制=审计非标 PIT 状态（年报级，厚度天然高于问询函短窗）。"
        ),
        "gate_cov_pass": gate_cov,
        "hard_reject_jaccard": hard_reject,
        "gate_pass": gate_pass,
        "approx": approx,
        "gaps": gaps,
        "input_sha8": {
            "audit": aud_sha[:8],
            "hiliq": mask_sha[:8],
            "capacity_adv": cap_sha[:8],
            "negevent_w": negw_sha[:8],
            "negevent_meta": negm_sha[:8],
            "ann_main": annm_sha[:8],
            "ann_post": annp_sha[:8],
        },
        "peak_rss_mb": peak,
        "mem_available_gi_start": mem0,
        "mem_available_gi_end": mem_available_gi(),
        "elapsed_sec": round(time.time() - t0, 3),
        "dig_sha8": "fa973826",
        "live": False,
        "promotion": False,
        "ok_requested": False,
        "x2_run": False,
        "book_smoke": False,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)
    print(json.dumps({
        "gate_pass": gate_pass,
        "gate_cov_pass": gate_cov,
        "hard_reject_jaccard": hard_reject,
        "median": cov_all["median"],
        "frac_ge10": frac_ge10,
        "jmax_neg": jmax_neg,
        "jmax_l36": jmax_l36,
        "peak_rss_mb": peak,
        "out": str(OUT_JSON),
        "out_sha8": sha256_file(OUT_JSON)[:8],
    }, ensure_ascii=False))
    return 0 if gate_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
