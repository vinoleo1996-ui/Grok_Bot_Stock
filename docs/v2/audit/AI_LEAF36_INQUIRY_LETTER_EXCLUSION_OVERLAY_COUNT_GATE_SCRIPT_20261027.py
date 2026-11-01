#!/usr/bin/env python3
"""Leaf36 inquiry-letter / composite landmine exclusion overlay — HI_LIQ count gate.
NOT X2 / NOT selfcheck / NOT Book-Smoke. No PnL/IC/CAGR. live=false.
PRIMARY: financial inquiry_letter / 关注函 exclusion overlay (NOT mainline alpha).
Jaccard hard gate vs FAIL negevent exclusion set (>0.5 reject).
"""
from __future__ import annotations

import gc
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
WIN = 20  # T1起20交易日；对齐 negevent E3/E4；不读收益选窗
REBAL_EVERY = 20
MASK_PATH = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
ANN_MAIN = ROOT / "data/v2/events/announcements_classified_pit.parquet"
ANN_POST = ROOT / "data/v2/events/announcements_classified_pit_post202406.parquet"
# dig 点名主表；post202406 为 X2 窗同伴（inquiry_letter 主表截断于 2024-05-31；同 negevent EVENTS concat）
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
NEGEVENT_W = ROOT / "output/ai_factory/g1g5_capacity_adv_negevent_daily_weights_20261014_010218.parquet"
NEGEVENT_META = ROOT / "output/ai_factory/g1g5_capacity_adv_negevent_run_meta_20261014_010218.json"
OUT_JSON = ROOT / "output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json"
BALLAST = "510300.SH"
MECHANISM_TAG = "g1g5_ashare_inquiry_letter_exclusion_overlay_v1"

FIN_KW = r"年报|半年报|季报|财务|会计|审计|业绩|应收|存货|商誉|收入|利润|信息披露|监管工作函"
REORG_KW = r"重组|重大资产重组|吸收合并|借壳"
REPLY_NOISE_KW = r"回函|回复|核查说明"
ISSUER_KW = r"收到|证券交易所|深圳证券交易所|上海证券交易所|北京证券交易所|监管工作函|问询函的公告|关注函的公告"
ABNORMAL_KW = r"异常波动"
CBOND_KW = r"可转债|可转换公司债券"
TITLE_CORE_KW = r"问询函|关注函"

# 覆盖闸：财务问询稀疏，勿盲抄 leaf34 median≥300
# 写死：X2 全日历日 HI_LIQ 触窗剔除名数 median≥30；zero_frac≤0.50；Jaccard max vs negevent >0.5 硬拒
COV_MEDIAN_MIN = 30.0
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


def load_announcements() -> pd.DataFrame:
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
    return a


def filter_primary(a: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    title = a["ann_title"].fillna("")
    m_base = (a["event_type"] == "inquiry_letter") & title.str.contains(TITLE_CORE_KW, regex=True)
    m_fin = title.str.contains(FIN_KW, regex=True)
    m_reorg = title.str.contains(REORG_KW, regex=True)
    m_reply = title.str.contains(REPLY_NOISE_KW, regex=True)
    m_issuer = title.str.contains(ISSUER_KW, regex=True)
    m_abn = title.str.contains(ABNORMAL_KW, regex=True)
    m_cb = title.str.contains(CBOND_KW, regex=True)
    # 剔噪声：纯回函/回复/核查说明 且非交易所发出正文 → APPROX（issuer 标题启发式）
    primary = m_base & m_fin & ~m_reorg & ~m_abn & ~m_cb & ~(m_reply & ~m_issuer)
    funnel = {
        "inquiry_letter_rows": int((a["event_type"] == "inquiry_letter").sum()),
        "plus_title_core": int(m_base.sum()),
        "plus_fin_kw": int((m_base & m_fin).sum()),
        "minus_reorg": int((m_base & m_fin & ~m_reorg).sum()),
        "minus_abnormal_cbond": int((m_base & m_fin & ~m_reorg & ~m_abn & ~m_cb).sum()),
        "primary_after_reply_noise": int(primary.sum()),
        "disclosed_abnormal_among_base_fin": int((m_base & m_fin & m_abn).sum()),
        "disclosed_cbond_among_base_fin": int((m_base & m_fin & m_cb).sum()),
        "disclosed_reorg_among_base_fin": int((m_base & m_fin & m_reorg).sum()),
        "fin_keywords": FIN_KW,
        "reorg_keywords": REORG_KW,
        "reply_noise_approx": True,
    }
    ev = a.loc[primary, ["instrument", "d", "ann_title"]].drop_duplicates(["instrument", "d"])
    return ev, funnel


def build_exclusion(ev: pd.DataFrame, cal_full: pd.DatetimeIndex, cal: pd.DatetimeIndex, hiliq_names: set) -> tuple[dict, int]:
    def t1pos(d):
        return int(cal_full.searchsorted(pd.Timestamp(d), side="right"))

    excl = {d: set() for d in cal}
    n_win = 0
    for r in ev.itertuples():
        if r.instrument not in hiliq_names:
            continue
        s = t1pos(r.d)
        if s >= len(cal_full):
            continue
        e = min(s + WIN - 1, len(cal_full) - 1)
        for i in range(s, e + 1):
            d = cal_full[i]
            if d in excl:
                excl[d].add(r.instrument)
        n_win += 1
    return excl, n_win


def rebuild_e234_pairs(a: pd.DataFrame, cal_full: pd.DatetimeIndex, hiliq_names: set) -> set:
    """Rebuild negevent E2/E3/E4 window name-days on HI_LIQ∩X2 (no E1 share_float this pass)."""
    title = a["ann_title"].fillna("")
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
    pairs: set = set()
    counts = {}
    for tag, mk in (("E2", m2), ("E3", m3), ("E4", m4)):
        sub = a.loc[mk, ["instrument", "d"]].drop_duplicates()
        sub = sub[(sub["d"] >= pd.Timestamp("2023-10-01")) & (sub["d"] <= X2_END)]
        n_before = len(pairs)
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
                    pairs.add((d, r.instrument))
        counts[tag] = len(pairs) - n_before
    counts["total_pairs"] = len(pairs)
    return pairs, counts


def held_cut_pairs() -> tuple[set, dict]:
    """APPROX negevent held-cut from capacity_adv vs negevent weight diff."""
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


def main() -> int:
    t0 = time.time()
    peak = rss_mb()
    mem0 = mem_available_gi()
    approx = [
        "announcements = main parquet + post202406 companion (main inquiry_letter truncates 2024-05-31; same concat as research/g1g5_capacity_adv_negevent_weights.py EVENTS)",
        "reply-noise filter APPROX: drop title matching 回函|回复|核查说明 unless issuer-ish heuristics (收到/交易所/问询函的公告…)",
        "negevent exclusion APPROX = held-cut(capacity_adv vs negevent weights) ∪ rebuilt E2/E3/E4 windows from same announcements; E1 share_float NOT rebuilt this pass (memory)",
        "WIN=20 trading days from T1; NOT selected from returns; aligns negevent E3/E4",
        "FIN keyword table frozen in DRAFT; coverage validated by count funnel",
        "no PnL/IC/CAGR; no full overlay parquet land; no .ok",
    ]
    gaps = []

    # HI_LIQ calendar
    t = pq.read_table(
        MASK_PATH,
        columns=["date", "instrument", "in_universe"],
        filters=[
            ("date", ">=", pd.Timestamp("2023-10-01").to_datetime64()),
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

    a = load_announcements()
    peak = max(peak, rss_mb())
    ev, funnel = filter_primary(a)
    ev = ev[(ev["d"] >= pd.Timestamp("2023-10-01")) & (ev["d"] <= X2_END)].copy()
    n_primary_events = int(len(ev))
    n_primary_x2_avail = int(((ev["d"] >= X2_START) & (ev["d"] <= X2_END)).sum())
    by_year = {str(k): int(v) for k, v in ev.groupby(ev["d"].dt.year).size().items()}

    excl, n_win = build_exclusion(ev, cal_full, cal, hiliq_names)
    daily_n = np.asarray([len(excl[d] & mask_by[d]) for d in cal], dtype=float)
    hit = daily_n > 0
    zero_frac = float((~hit).mean()) if len(daily_n) else 1.0
    cov_all = stats(daily_n)
    cov_hit = stats(daily_n[hit]) if hit.any() else stats(np.asarray([], dtype=float))

    # rebal subsample disclosure
    idx = list(range(0, len(cal), REBAL_EVERY))
    if idx[-1] != len(cal) - 1:
        idx.append(len(cal) - 1)
    rebal_n = daily_n[idx]
    cov_rebal = stats(rebal_n)

    # negevent FAIL honesty from run_meta
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
                "better_cagr": bool(sc.get("cagr_neg") is not None and sc.get("cagr_cap") is not None and sc["cagr_neg"] > sc["cagr_cap"]),
                "better_mdd": bool(sc.get("mdd_neg") is not None and sc.get("mdd_cap") is not None and sc["mdd_neg"] > sc["mdd_cap"]),
                "run_meta_sha8": sha256_file(NEGEVENT_META)[:8],
            }
        )
        if negevent_fail["better_cagr"] or negevent_fail["better_mdd"]:
            negevent_fail["status"] = "NOT_STRICT_FAIL_ON_BOTH"
        else:
            negevent_fail["status"] = "FAIL"
    except Exception as e:
        gaps.append(f"negevent_meta:{e}")

    # Jaccard APPROX
    cut_pairs, cut_meta = held_cut_pairs()
    peak = max(peak, rss_mb())
    e234_pairs, e234_counts = rebuild_e234_pairs(a, cal_full, hiliq_names)
    del a
    gc.collect()
    approx_neg = cut_pairs | e234_pairs
    # index approx_neg by date for speed
    neg_by: dict = {}
    for d, inst in approx_neg:
        neg_by.setdefault(d, set()).add(inst)

    j_all = []
    j_hit = []
    for d in cal:
        univ = mask_by[d]
        A = excl[d] & univ
        B = neg_by.get(d, set()) & univ
        if not A and not B:
            continue
        u = A | B
        j = len(A & B) / len(u)
        j_all.append(j)
        if A:
            j_hit.append(j)
    ja = np.asarray(j_all, dtype=float)
    jh = np.asarray(j_hit, dtype=float)
    jaccard = {
        "method": "APPROX held-cut ∪ E2/E3/E4 rebuilt; daily set Jaccard on HI_LIQ∩X2; hard metric=max on leaf36-hit days",
        "all_nonempty_days": {
            "n": int(len(ja)),
            "mean": float(ja.mean()) if len(ja) else None,
            "max": float(ja.max()) if len(ja) else None,
            "median": float(np.median(ja)) if len(ja) else None,
        },
        "leaf36_hit_days": {
            "n": int(len(jh)),
            "mean": float(jh.mean()) if len(jh) else None,
            "max": float(jh.max()) if len(jh) else None,
            "median": float(np.median(jh)) if len(jh) else None,
        },
        "held_cut": cut_meta,
        "e234_rebuild": e234_counts,
        "approx_neg_pairs": int(len(approx_neg)),
        "e1_share_float_rebuilt": False,
    }
    jaccard_max = jaccard["leaf36_hit_days"]["max"]
    jaccard_mean = jaccard["leaf36_hit_days"]["mean"]
    hard_j = bool(jaccard_max is not None and jaccard_max > JACCARD_MAX_HARD)

    masked_median = cov_all["median"]
    gate_cov = bool(
        masked_median is not None
        and masked_median >= COV_MEDIAN_MIN
        and zero_frac <= ZERO_FRAC_MAX
    )
    gate_pass = bool(gate_cov and not hard_j)

    alt_suggest = None
    if not gate_pass:
        alt_suggest = (
            "PRIMARY 计数/同构闸未过：建议主改派备选——(A) IMAX/隔夜彩票剔除（须 vs 叶18/27 overnight-idio 同构闸）；"
            "或 (B) 行业级客户动量（先 IO 表 PIT 可得性）。本拍勿自开备选 who_pays。"
        )

    peak = max(peak, rss_mb())
    out = {
        "mechanism_tag": MECHANISM_TAG,
        "leaf_intent": 36,
        "et_ts": "2026-10-27T16:35:00-04:00",
        "window": {"start": "2024-06-03", "end": "2026-10-09", "exclusion_win_tdays": WIN, "rebal_every_disclose": REBAL_EVERY},
        "delivery": "daily_exclusion_mask_overlay_NOT_mainline_alpha",
        "event_filter_funnel": funnel,
        "n_primary_events_inst_x_d": n_primary_events,
        "n_primary_x2_available_at": n_primary_x2_avail,
        "n_windows_applied_hiliq": int(n_win),
        "primary_events_by_year": by_year,
        "coverage_daily_exclusion_names_hiliq": cov_all,
        "coverage_on_hit_days": cov_hit,
        "coverage_rebal_disclose": cov_rebal,
        "hit_day_frac": float(hit.mean()) if len(daily_n) else 0.0,
        "zero_frac_masked": zero_frac,
        "zero_days": int((~hit).sum()),
        "n_x2_cal_days": int(len(cal)),
        "n_hit_days": int(hit.sum()),
        "hiliq_universe_size": stats(hiliq_sizes),
        "jaccard_vs_negevent": jaccard,
        "jaccard_max_hard_metric": jaccard_max,
        "jaccard_mean_hit_days": jaccard_mean,
        "negevent_prior_fail": negevent_fail,
        "gate_rule": (
            f"daily_excl_median>={COV_MEDIAN_MIN} AND zero_frac<={ZERO_FRAC_MAX} "
            f"AND jaccard_max_vs_negevent<={JACCARD_MAX_HARD} (hard reject if >{JACCARD_MAX_HARD}; metric=max on leaf36-hit days)"
        ),
        "gate_cov_pass": gate_cov,
        "gate_pass": gate_pass,
        "hard_reject_jaccard": hard_j,
        "coverage_threshold_rationale_zh": (
            "财务问询/关注函稀疏，勿盲抄叶34/35 median≥300；本拍写死触窗剔除名数全日 median≥30。"
            "实测 median≈7 → 覆盖闸 FAIL（机制正交 Jaccard 过，但剔除厚度不足支撑独立 overlay 叶）。"
        ),
        "alt_suggest_zh": alt_suggest,
        "approx": approx,
        "gaps": gaps,
        "peak_rss_mb": float(peak),
        "mem_available_gi_start": float(mem0),
        "mem_available_gi_end": float(mem_available_gi()),
        "elapsed_sec": float(time.time() - t0),
        "sha": {
            "ann_main": sha256_file(ANN_MAIN)[:8],
            "ann_post": sha256_file(ANN_POST)[:8] if ANN_POST.exists() else None,
            "hiliq_mask": sha256_file(MASK_PATH)[:8],
            "capacity_adv": sha256_file(CAP_ADV)[:8],
            "negevent_weights": sha256_file(NEGEVENT_W)[:8],
            "negevent_run_meta": sha256_file(NEGEVENT_META)[:8] if NEGEVENT_META.exists() else None,
        },
        "paths": {
            "ann_main": str(ANN_MAIN.relative_to(ROOT)),
            "ann_post": str(ANN_POST.relative_to(ROOT)),
            "hiliq_mask": str(MASK_PATH.relative_to(ROOT)),
            "capacity_adv": str(CAP_ADV.relative_to(ROOT)),
            "negevent_weights": str(NEGEVENT_W.relative_to(ROOT)),
        },
        "EXECUTED_full_alpha": False,
        "ok_requested": False,
        "live": False,
        "leo_notify": False,
        "dig_sha8_expected": "74234fca",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)
    print(
        json.dumps(
            {
                "gate_pass": gate_pass,
                "gate_cov_pass": gate_cov,
                "masked_median": masked_median,
                "zero_frac": zero_frac,
                "hit_days": int(hit.sum()),
                "jaccard_max": jaccard_max,
                "jaccard_mean": jaccard_mean,
                "n_primary_events": n_primary_events,
                "n_primary_x2": n_primary_x2_avail,
                "peak_rss_mb": out["peak_rss_mb"],
                "hard_reject_jaccard": hard_j,
                "alt": alt_suggest,
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
