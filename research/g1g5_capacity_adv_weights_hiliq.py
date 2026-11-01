#!/usr/bin/env python3
"""G1G5 capacity/ADV fillability X2 weights (research-grade).

Mechanism (orthogonal to nine failed packs):
  - Main signal: industry-demeaned log(ADV) liquidity rank (ADV≈float_mktcap×turnover/100)
  - Hard capacity: name w≤4%; w×AUM_1M ≤ k×ADV (k=0.6%); SW L1 sleeve ≤25% (HI_LIQ_V1.1)
  - Hard-exclude known fill-gap megas: 600519.SH, 002371.SZ
  - Universe: HI_LIQ_V1.1 mask (not FULLA); NOT val residual / OCF / momentum / unlock-flow / etf_core / rebal

promotion_approved=false; no orders; no Strategy; no GP; no stub forward-fill.
"""
from __future__ import annotations

import gc
import json
import math
import resource
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa: E402
from research.ai_debate_memory_runner import (  # noqa: E402
    DEFAULT_BENCHMARK,
    DEFAULT_HORIZON_DAYS,
    _load_benchmark_closes,
)
from research.g1g5_wiring import (  # noqa: E402
    COLUMN_CONTRACT_VERSION,
    COLUMN_CONTRACT_VERSION_QM_ALIAS,
    HARD_GATE_VERSION,
    append_g1g5_round,
    build_g1g5_debate,
    settle_pending_g5,
)
from research.g1g5_expand_g6 import (  # noqa: E402
    UNIVERSE_ID as EXPAND_UNIVERSE_ID,
    UNIVERSE_KIND,
    build_daily_weights_expand,
    mid_large_members_on,
    month_end_sessions,
    run_g6_lookahead_proof,
)
from research.g1g5_x2_panel_stitch import clear_caches as clear_x2_caches  # noqa: E402
from research.g1g5_nontextbook_weights import (  # noqa: E402
    _forbid_textbook_tokens,
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402
from research.g1g5_d1_val_resid_weights import (  # noqa: E402
    select_mid_large_topn_light,
    load_pit_member_index_light,
)

MECHANISM_TAG = "g1g5_ashare_capacity_adv_v1"
UNIVERSE_ID = "HI_LIQ_V1_1"  # was EXPAND_UNIVERSE_ID
DEFAULT_SCORE_N = 50
DEFAULT_ACTIVE_N = 25
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
X2_END = "2026-10-09"

STOCK_BUDGET = 0.80
BALLAST_FRAC = 0.20
BALLAST_ETF = "510300.SH"
IND_CAP_STOCK_SLEEVE = 0.25  # HI_LIQ_V1.1 §2: per SW L1 / stock-sleeve sum (510300 excluded)
IND_CAP = IND_CAP_STOCK_SLEEVE * STOCK_BUDGET  # book-weight equivalent (=0.20) used by unchanged greedy/clip code
NAME_CAP = 0.04
AUM_BINDING = 1_000_000.0  # 100万 binding case
ADV_PARTICIPATION_K = 0.006  # HI_LIQ_V1 §3 (was 0.02)  # w×AUM ≤ k×ADV
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})

D1_VALUATION = ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "可成交容量约束下的流动性溢价/冲击成本错误定价对手盘："
    "以D1 asof ADV代理（流通市值×换手）经申万一级行业中性后的流动性分位选股；"
    "单名权重与ADV参与率双硬顶，压百万元端巨头成交/冲击缺口；"
    "明确非估值残差、非OCF兑现、非截面相对强弱主轴；"
    "明确非四臂摩擦/解禁/份额流/调仓流/ETF-core直接持有。"
)



# ---- HI_LIQ_V1.1 variant (2026-10-14): candidate pool = Strategy HI_LIQ mask, PIT per date ----
# NOTE: FULLA_* names are legacy; values point at HI_LIQ_V1.1 (Arch N5). Do not treat as FULLA paper.
FULLA_MASK = ROOT / "output" / "strategy_hiliq" / "universe_mask_hiliq_v1.parquet"  # HI_LIQ_V1.1
_FULLA_CACHE: dict = {}  # HI_LIQ mask cache (legacy name)


def _fulla_mask():  # HI_LIQ_V1.1 mask (legacy name)
    if "m" not in _FULLA_CACHE:
        m = pd.read_parquet(FULLA_MASK, columns=["date", "instrument", "in_universe"])
        m = m[m["in_universe"].astype(bool)]
        m["date"] = pd.to_datetime(m["date"]).dt.normalize()
        _FULLA_CACHE["m"] = m
        _FULLA_CACHE["by"] = {d: set(g["instrument"].astype(str)) for d, g in m.groupby("date")}
        _FULLA_CACHE["dates"] = sorted(_FULLA_CACHE["by"])
    return _FULLA_CACHE["m"]


def _fulla_members_on(sess) -> set:  # HI_LIQ_V1.1 PIT members (legacy name)
    _fulla_mask()
    t = pd.Timestamp(str(sess)[:10])
    ds_ = [d for d in _FULLA_CACHE["dates"] if d <= t]  # PIT: latest mask date <= session
    return set(_FULLA_CACHE["by"][ds_[-1]]) if ds_ else set()


def _fulla_universe() -> dict:  # HI_LIQ_V1.1 universe (legacy name)
    m = _fulla_mask()
    inst = sorted(m["instrument"].astype(str).unique())
    return {"instruments": inst, "n": len(inst), "source": str(FULLA_MASK.relative_to(ROOT)), "universe": "HI_LIQ_V1_1"}


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _preload_d1_adv(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Chunked D1 load: turnover_rate + float_mktcap only (peak-safe)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if not D1_VALUATION.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    want_set = set(want)
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=45)
    s1 = pd.Timestamp(max(sessions)[:10]) + pd.Timedelta(days=1)
    cols = ["ts_code", "trade_date", "turnover_rate", "float_mktcap", "available_at"]
    pf = pq.ParquetFile(str(D1_VALUATION))
    want_arr = pa.array(want, type=pa.string())
    chunks: list[pd.DataFrame] = []
    for i in range(pf.metadata.num_row_groups):
        rg = pf.metadata.row_group(i)
        td_stats = None
        for j in range(rg.num_columns):
            col = rg.column(j)
            if col.path_in_schema == "trade_date" and col.statistics and col.statistics.has_min_max:
                td_stats = (pd.Timestamp(col.statistics.min), pd.Timestamp(col.statistics.max))
                break
        if td_stats is not None:
            if td_stats[1] < s0 or td_stats[0] > s1:
                continue
        table = pf.read_row_group(i, columns=cols)
        tc = table.column("ts_code")
        if not pa.types.is_string(tc.type):
            table = table.set_column(
                table.schema.get_field_index("ts_code"),
                "ts_code",
                pc.cast(tc, pa.string()),
            )
        table = table.filter(pc.is_in(table.column("ts_code"), value_set=want_arr))
        if table.num_rows == 0:
            del table
            continue
        part = table.to_pandas()
        del table
        part = part[part["ts_code"].isin(want_set)]
        if part.empty:
            del part
            continue
        td = pd.to_datetime(part["trade_date"]).dt.tz_localize(None).dt.normalize()
        part = part[(td >= s0) & (td <= s1)]
        if part.empty:
            del part
            continue
        chunks.append(part)
        del part
        gc.collect()
    if not chunks:
        return pd.DataFrame()
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["turnover_rate"] = pd.to_numeric(df["turnover_rate"], errors="coerce")
    df["float_mktcap"] = pd.to_numeric(df["float_mktcap"], errors="coerce")
    df = df[df["available_at"].notna()].copy()
    df = df[["ts_code", "turnover_rate", "float_mktcap", "available_at"]].copy()
    gc.collect()
    return df


def _d1_adv_snapshot(
    d1: pd.DataFrame,
    instruments: Sequence[str],
    session: str,
) -> dict[str, dict[str, float]]:
    """instrument → {adv_yuan, turnover_rate, float_mktcap} asof available_at≤session."""
    if d1 is None or d1.empty:
        return {}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sub = d1[d1["available_at"].dt.normalize() <= sess]
    if sub.empty:
        return {}
    sub = sub.sort_values("available_at", kind="mergesort").groupby("ts_code", as_index=False).tail(1)  # stable
    out: dict[str, dict[str, float]] = {}
    want = set(instruments)
    for _, row in sub.iterrows():
        inst = str(row["ts_code"])
        if inst not in want:
            continue
        tr = float(row["turnover_rate"]) if np.isfinite(row["turnover_rate"]) else np.nan
        mv = float(row["float_mktcap"]) if np.isfinite(row["float_mktcap"]) else np.nan
        if not (np.isfinite(mv) and mv > 0 and np.isfinite(tr) and tr >= 0):
            continue
        adv = float(mv) * float(tr) / 100.0
        if not (np.isfinite(adv) and adv > 0):
            continue
        out[inst] = {"adv_yuan": adv, "turnover_rate": float(tr), "float_mktcap": float(mv)}
    return out


def score_adv_liquidity(
    session: str,
    instruments: Sequence[str],
    *,
    snap: dict[str, dict[str, float]],
    sw: pd.DataFrame,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Industry-demeaned log(ADV) z-score; higher = more fillable."""
    meta: dict[str, Any] = {"arm": "capacity_adv", "status": "ok", "metric": "log_adv_ind_demean"}
    sess = pd.Timestamp(str(session)[:10]).normalize()

    raw_log: dict[str, float] = {}
    advs: dict[str, float] = {}
    inst_sw: dict[str, str] = {}
    for inst in instruments:
        if inst in HARD_EXCLUDE:
            continue
        row = snap.get(inst)
        if not row:
            continue
        adv = row.get("adv_yuan")
        if adv is None or not np.isfinite(adv) or adv <= 0:
            continue
        code = sw_code_on(inst, sess, sw)
        if not code:
            continue
        raw_log[inst] = float(math.log(adv))
        advs[inst] = float(adv)
        inst_sw[inst] = code

    meta["n_scored_raw"] = len(raw_log)
    meta["n_hard_excluded_present"] = sum(1 for i in instruments if i in HARD_EXCLUDE)
    if len(raw_log) < max(8, len(instruments) // 6):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计ADV名过少 n={len(raw_log)}"
        return {i: 0.0 for i in instruments}, meta

    by_ind: dict[str, list[float]] = {}
    for inst, v in raw_log.items():
        by_ind.setdefault(inst_sw[inst], []).append(v)
    ind_mean = {k: float(np.mean(vs)) for k, vs in by_ind.items()}
    resid = {inst: raw_log[inst] - ind_mean[inst_sw[inst]] for inst in raw_log}
    meta["n_industries"] = len(by_ind)

    ser = pd.Series({i: float(resid.get(i, 0.0)) for i in instruments})
    scored_only = ser[list(raw_log.keys())]
    mu, sd = float(scored_only.mean()), float(scored_only.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
        z = z.where(ser.index.isin(raw_log.keys()), 0.0)
    out = {i: float(z.loc[i]) if i in z.index else 0.0 for i in instruments}
    meta["n_scored"] = len(raw_log)
    meta["adv_p50"] = float(np.median(list(advs.values()))) if advs else None
    meta["adv_p10"] = float(np.percentile(list(advs.values()), 10)) if advs else None
    return out, meta


def _name_cap_from_adv(adv_yuan: float) -> float:
    """Hard name cap = min(NAME_CAP, k×ADV/AUM)."""
    if not (np.isfinite(adv_yuan) and adv_yuan > 0):
        return 0.0
    by_adv = (ADV_PARTICIPATION_K * float(adv_yuan)) / float(AUM_BINDING)
    return float(min(NAME_CAP, max(0.0, by_adv)))


def select_capacity_adv(
    ranked: list[tuple[str, float]],
    *,
    snap: dict[str, dict[str, float]],
    sw: pd.DataFrame,
    session: str,
    active_n: int,
    ind_cap: float,
    budget: float,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Greedy by ADV score; capacity-proportional weights under name+industry caps."""
    sess = pd.Timestamp(str(session)[:10]).normalize()
    picked: list[str] = []
    caps: dict[str, float] = {}
    ind_count: dict[str, int] = {}
    skipped: list[dict[str, Any]] = []

    # rough max names per industry assuming equal NAME_CAP slots
    max_n_ind = max(1, int(np.floor(ind_cap / max(NAME_CAP, 1e-12) + 1e-12)))

    for inst, sc in ranked:
        if inst in HARD_EXCLUDE:
            skipped.append({"inst": inst, "reason": "hard_exclude"})
            continue
        row = snap.get(inst) or {}
        adv = float(row.get("adv_yuan") or 0.0)
        ncap = _name_cap_from_adv(adv)
        if ncap < 1e-4:
            skipped.append({"inst": inst, "reason": "adv_cap_too_small", "adv": adv})
            continue
        code = sw_code_on(inst, sess, sw) or "_UNK"
        if ind_count.get(code, 0) >= max_n_ind:
            skipped.append({"inst": inst, "reason": "ind_count_cap", "sw": code})
            continue
        picked.append(inst)
        caps[inst] = ncap
        ind_count[code] = ind_count.get(code, 0) + 1
        if len(picked) >= active_n:
            break

    meta: dict[str, Any] = {
        "n_picked": len(picked),
        "ind_counts": dict(ind_count),
        "max_n_per_ind": max_n_ind,
        "n_skipped": len(skipped),
        "skipped_head": skipped[:10],
        "name_caps_head": {i: round(caps[i], 4) for i in picked[:8]},
    }
    if not picked:
        return {}, meta

    # capacity-proportional raw ∝ sqrt(ADV) within picked (mild tilt to liquid)
    raw: dict[str, float] = {}
    for inst in picked:
        adv = float((snap.get(inst) or {}).get("adv_yuan") or 0.0)
        raw[inst] = math.sqrt(max(adv, 1.0))
    sraw = sum(raw.values())
    w = {i: budget * (raw[i] / sraw) for i in picked}

    # iterative clip to per-name cap + industry cap
    for _ in range(12):
        # name cap
        w = {i: min(w[i], caps[i]) for i in w}
        # industry cap
        ind_w: dict[str, float] = {}
        ind_members: dict[str, list[str]] = {}
        for inst, wv in w.items():
            code = sw_code_on(inst, sess, sw) or "_UNK"
            ind_w[code] = ind_w.get(code, 0.0) + wv
            ind_members.setdefault(code, []).append(inst)
        scaled = dict(w)
        for code, tw in ind_w.items():
            if tw > ind_cap + 1e-12:
                factor = ind_cap / tw
                for inst in ind_members[code]:
                    scaled[inst] = scaled[inst] * factor
        w = scaled
        # renormalize up toward budget if room under caps
        s2 = sum(w.values())
        if s2 <= 1e-15:
            break
        if s2 < budget - 1e-9:
            # try grow under residual room
            room = {i: max(0.0, caps[i] - w[i]) for i in w}
            # also industry residual room
            ind_w2: dict[str, float] = {}
            for inst, wv in w.items():
                code = sw_code_on(inst, sess, sw) or "_UNK"
                ind_w2[code] = ind_w2.get(code, 0.0) + wv
            grow_budget = budget - s2
            # allocate grow by room
            total_room = sum(room.values())
            if total_room <= 1e-15 or grow_budget <= 1e-15:
                break
            for inst in list(w.keys()):
                if room[inst] <= 0:
                    continue
                share = room[inst] / total_room
                add = min(room[inst], grow_budget * share)
                code = sw_code_on(inst, sess, sw) or "_UNK"
                ind_room = max(0.0, ind_cap - ind_w2.get(code, 0.0))
                add = min(add, ind_room)
                w[inst] += add
                ind_w2[code] = ind_w2.get(code, 0.0) + add
        else:
            # shrink to budget
            w = {i: v * (budget / s2) for i, v in w.items()}
            w = {i: min(v, caps[i]) for i, v in w.items()}

    w = {i: float(max(0.0, v)) for i, v in w.items() if v > 1e-12}
    # drop tiny
    ind_w_final: dict[str, float] = {}
    for inst, wv in w.items():
        code = sw_code_on(inst, sess, sw) or "_UNK"
        ind_w_final[code] = ind_w_final.get(code, 0.0) + wv
    meta["ind_weights"] = {k: round(v, 4) for k, v in ind_w_final.items()}
    meta["max_ind_weight"] = float(max(ind_w_final.values())) if ind_w_final else 0.0
    meta["max_name_weight"] = float(max(w.values())) if w else 0.0
    meta["stock_w_sum"] = float(sum(w.values()))
    meta["n_final"] = len(w)
    return w, meta


def build_rebalance_decisions_capacity_adv(
    stock_universe: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    sw = _load_sw_members()
    member_index = None
    if use_pit_membership:
        member_index = None  # HI_LIQ: PIT membership from mask

    d1 = _preload_d1_adv(stock_universe, rebalance_sessions)
    score_meta: dict[str, Any] = {
        "rebalance_arm_logs": [],
        "d1_rows": int(len(d1)),
        "d1_path": str(D1_VALUATION.relative_to(ROOT)),
        "peak_rss_mb_after_d1": round(_rss_kb() / 1024.0, 1),
        "hard_exclude": sorted(HARD_EXCLUDE),
        "name_cap": NAME_CAP,
        "ind_cap": IND_CAP,
        "aum_binding": AUM_BINDING,
        "adv_participation_k": ADV_PARTICIPATION_K,
        "no_close_matrix": True,
    }
    gc.collect()

    decisions: list[dict[str, Any]] = []
    all_instruments = set(stock_universe) | {BALLAST_ETF}

    for sess in rebalance_sessions:
        present = _fulla_members_on(sess) & set(stock_universe)  # HI_LIQ_V1.1 PIT mask (replaces mid_large top-N pool)
        # determinism fix 2026-10-13: stable code order (was set iteration -> PYTHONHASHSEED dependent)
        present = sorted(i for i in present if i not in HARD_EXCLUDE)
        if len(present) < 8:
            decisions.append(
                {
                    "session": sess,
                    "instrument": BALLAST_ETF,
                    "rating": "Hold",
                    "target_weight_override": 1.0,
                }
            )
            for inst in stock_universe:
                decisions.append(
                    {
                        "session": sess,
                        "instrument": inst,
                        "rating": "Abstain",
                        "target_weight_override": 0.0,
                    }
                )
            score_meta["rebalance_arm_logs"].append(
                {"session": sess, "status": "coverage_gap", "n_present": len(present)}
            )
            continue

        snap = _d1_adv_snapshot(d1, list(present), sess)
        scores, arm_meta = score_adv_liquidity(sess, list(present), snap=snap, sw=sw)
        ranked = sorted(
            ((i, scores[i]) for i in present if i in snap),
            key=lambda x: (-x[1], x[0]),  # tie-break by code (was set order)
        )
        pos = [(i, s) for i, s in ranked if s > 0]
        ranked_use = pos if len(pos) >= max(5, active_n // 2) else ranked

        target, cap_meta = select_capacity_adv(
            ranked_use,
            snap=snap,
            sw=sw,
            session=sess,
            active_n=active_n,
            ind_cap=IND_CAP,
            budget=STOCK_BUDGET,
        )
        # enforce hard exclude zero
        for bad in HARD_EXCLUDE:
            if target.get(bad, 0) > 0:
                raise RuntimeError(f"hard_exclude breached @ {sess}: {bad}")
        stock_w_sum = float(sum(target.values()))
        ballast_w = max(0.0, 1.0 - stock_w_sum)

        decisions.append(
            {
                "session": sess,
                "instrument": BALLAST_ETF,
                "rating": "Hold",
                "target_weight_override": ballast_w,
            }
        )
        for inst in stock_universe:
            w = float(target.get(inst, 0.0))
            decisions.append(
                {
                    "session": sess,
                    "instrument": inst,
                    "rating": "Overweight" if w > 0 else "Abstain",
                    "target_weight_override": w,
                }
            )
        all_instruments |= set(target.keys())
        score_meta["rebalance_arm_logs"].append(
            {
                "session": sess,
                "arm": arm_meta,
                "cap": {k: v for k, v in cap_meta.items() if k not in ("ind_weights",)},
                "max_ind_weight": cap_meta.get("max_ind_weight"),
                "max_name_weight": cap_meta.get("max_name_weight"),
                "n_target": len(target),
                "stock_w_sum": stock_w_sum,
                "ballast_w": ballast_w,
                "top_head": [(i, round(scores.get(i, 0.0), 4)) for i, _ in ranked_use[:8]],
            }
        )
        if cap_meta.get("max_ind_weight", 0) > IND_CAP + 1e-6:
            raise RuntimeError(
                f"industry cap breached @ {sess}: {cap_meta.get('max_ind_weight')}"
            )
        if cap_meta.get("max_name_weight", 0) > NAME_CAP + 1e-6:
            raise RuntimeError(
                f"name cap breached @ {sess}: {cap_meta.get('max_name_weight')}"
            )

    del d1
    clear_x2_caches()
    try:
        import research.ai_debate_memory_runner as m

        m._EQUITY_CLOSE_CACHE.clear()
    except Exception:
        pass
    gc.collect()
    score_meta["peak_rss_mb_after_score"] = round(_rss_kb() / 1024.0, 1)
    return decisions, score_meta, sorted(all_instruments)


def run_capacity_adv(
    *,
    score_n: int = DEFAULT_SCORE_N,
    active_n: int = DEFAULT_ACTIVE_N,
    horizon_days: int = 5,
    max_debate_rounds: int = 1,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    peak0 = _rss_kb()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = out_dir or (ROOT / "output" / "strategy_hiliq" / "legs")
    out_dir.mkdir(parents=True, exist_ok=True)

    uni = _fulla_universe()
    stock_universe = [i for i in uni["instruments"] if i not in HARD_EXCLUDE]
    if len(stock_universe) < 10:
        raise RuntimeError(f"universe too small: {len(stock_universe)}")

    rebal = month_end_sessions(weight_start, weight_end)
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        last = pd.Timestamp(cal0[-1]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + [x for x in rebal if x != first]
        if last not in rebal:
            rebal = list(rebal) + [last]
    del bench
    gc.collect()

    decisions, score_meta, instruments = build_rebalance_decisions_capacity_adv(
        stock_universe,
        rebal,
        active_n=active_n,
        use_pit_membership=True,
    )
    gc.collect()
    weights = build_daily_weights_expand(
        decisions,
        start=weight_start,
        end=weight_end,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_ZH,
        universe_id=UNIVERSE_ID,
    )
    if weights["who_pays_zh"].astype(str).str.contains("动量").any():
        raise RuntimeError("who_pays contains 动量")
    if weights["mechanism_tag"].astype(str).str.contains(
        "momentum|动量|价值|quality", case=False, regex=True
    ).any():
        raise RuntimeError("mechanism_tag contains textbook token")

    daily_sum = weights.groupby("date")["target_weight"].sum()
    if float(daily_sum.min()) < 0.99 or float(daily_sum.max()) > 1.01:
        raise RuntimeError(
            f"daily_gross out of band: min={daily_sum.min()} max={daily_sum.max()}"
        )

    stock_set = set(stock_universe)
    pos = weights[weights["target_weight"] > 1e-15].copy()
    # hard exclude must be zero everywhere
    for bad in HARD_EXCLUDE:
        if ((pos["instrument"] == bad) & (pos["target_weight"] > 1e-15)).any():
            raise RuntimeError(f"hard_exclude present in daily weights: {bad}")

    is_ballast = pos["instrument"] == BALLAST_ETF
    is_stock = pos["instrument"].isin(stock_set) & ~is_ballast
    ballast_share = pos.loc[is_ballast].groupby("date")["target_weight"].sum()
    stock_share = pos.loc[is_stock].groupby("date")["target_weight"].sum()
    all_dates = weights["date"].drop_duplicates()
    mean_ballast = float(ballast_share.reindex(all_dates).fillna(0.0).mean())
    mean_stock = float(stock_share.reindex(all_dates).fillna(0.0).mean())
    if mean_ballast > 0.40 + 1e-9:
        raise RuntimeError(f"ballast share too high (etf_core drift): {mean_ballast:.3f}")


    # name + industry cap checks on sample rebalance days
    sw = _load_sw_members()
    ind_breach = []
    name_breach = []
    for sess in rebal[:: max(1, len(rebal) // 8)][:8]:
        day = pos[pos["date"] == sess]
        stk = day[day["instrument"].isin(stock_set) & (day["instrument"] != BALLAST_ETF)]
        if stk.empty:
            continue
        mx_name = float(stk["target_weight"].max())
        if mx_name > NAME_CAP + 1e-6:
            name_breach.append({"session": sess, "max_name_w": mx_name})
        ind_w: dict[str, float] = {}
        for _, row in stk.iterrows():
            code = sw_code_on(str(row["instrument"]), pd.Timestamp(sess), sw) or "_UNK"
            ind_w[code] = ind_w.get(code, 0.0) + float(row["target_weight"])
        sleeve = float(stk["target_weight"].sum())
        mx = max(ind_w.values()) if ind_w else 0.0
        mx_sleeve = (mx / sleeve) if sleeve > 1e-12 else 0.0
        if mx > IND_CAP + 1e-6 or mx_sleeve > IND_CAP_STOCK_SLEEVE + 1e-6:
            ind_breach.append({"session": sess, "max_ind_w": mx, "max_ind_sleeve_share": round(mx_sleeve, 6), "ind_w": {k: round(v, 4) for k, v in ind_w.items()}})
    if ind_breach:
        raise RuntimeError(f"industry cap breached in daily weights (HI_LIQ sleeve≤{IND_CAP_STOCK_SLEEVE}): {ind_breach[:2]}")
    if name_breach:
        raise RuntimeError(f"name cap breached in daily weights: {name_breach[:2]}")

    tow = estimate_daily_turnover(weights)

    intel = ROOT / "output" / "intel"
    factory = ROOT / "output" / "ai_factory"
    vs: dict[str, Any] = {}
    sample = [x for x in rebal if x >= "2024-03-01"][:8]
    new_sets = {}
    for ss in sample:
        a = set(
            weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"]
        )
        new_sets[ss] = {x for x in a if x in stock_set and x != BALLAST_ETF}
    prior_packs = (
        ("expand", intel / "g1g5_expand_daily_weights_20261012_111354.parquet"),
        ("friction_monthly", intel / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", intel / "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
        ("resid_etf", factory / "g1g5_resid_etf_daily_weights_20261013_002418.parquet"),
        ("etf_core", factory / "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet"),
        ("friction_cost_redesign", factory / "g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet"),
        ("idx_rebal_flow", factory / "g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet"),
        ("indcap_momneut_ocf", factory / "g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet"),
        ("d1_val_resid", factory / "g1g5_d1_val_resid_daily_weights_20261013_110154.parquet"),
    )
    for label, path in prior_packs:
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            entry["new_mean_one_way"] = tow.get("mean_one_way")
            diffs = []
            for ss in sample:
                a_stk = new_sets[ss]
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                b_stk = {x for x in b if ("." in x and x != BALLAST_ETF and not x.startswith("51"))}
                # keep all non-ballast non-pure-ETF-core for stock jaccard; prefer stock-like
                b_stk = {x for x in b if x != BALLAST_ETF and not str(x).startswith("51")}
                jac = (len(a_stk & b_stk) / len(a_stk | b_stk)) if (a_stk or b_stk) else None
                diffs.append(
                    {
                        "session": ss,
                        "n_new_stock": len(a_stk),
                        "n_old_stock": len(b_stk),
                        "jaccard_stock": jac,
                    }
                )
            entry["active_set_compare_sample"] = diffs
            jacs = [d["jaccard_stock"] for d in diffs if d.get("jaccard_stock") is not None]
            entry["jaccard_stock_mean"] = float(np.mean(jacs)) if jacs else None
            entry["jaccard_stock_max"] = float(np.max(jacs)) if jacs else None
            del old
            gc.collect()
        vs[label] = entry
    gc.collect()

    wpath = out_dir / f"g1g5_capacity_adv_hiliq_v1_1_daily_weights_{stamp}.parquet"
    export_cols = [
        "date",
        "instrument",
        "target_weight",
        "mechanism_tag",
        "who_pays_zh",
        "universe_id",
        "session",
        "instrument_id",
        "weight",
    ]
    weights[export_cols].to_parquet(wpath, index=False)

    ledger_path = out_dir / f"debate_ledger_g1g5_capacity_adv_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    debates: list[dict[str, Any]] = []
    sample_insts = [BALLAST_ETF] + [x for x in instruments if x in stock_set][:1]
    for inst in sample_insts:
        for sess in ["2024-06-28", "2026-06-30"]:
            result = build_g1g5_debate(
                session=sess,
                instrument=inst,
                ledger=ledger,
                max_debate_rounds=max_debate_rounds,
                mechanism_tag=MECHANISM_TAG,
                who_pays_zh=WHO_PAYS_ZH,
            )
            if result.decision is not None:
                result.decision["universe_id"] = UNIVERSE_ID  # type: ignore[index]
            entry = append_g1g5_round(ledger, result)
            debates.append(
                {
                    "decision_id": entry.get("decision_id"),
                    "instrument": inst,
                    "session": sess,
                    "rating": entry.get("rating"),
                    "mechanism_tag": MECHANISM_TAG,
                    "promotion_approved": False,
                }
            )
    settle_meta = settle_pending_g5(ledger, horizon_days=horizon_days)

    n_sess = int(weights["date"].nunique())
    clear_x2_caches()
    try:
        import research.ai_debate_memory_runner as m

        m._EQUITY_CLOSE_CACHE.clear()
    except Exception:
        pass
    gc.collect()
    peak = _rss_kb()

    last_day = str(weights["date"].max())
    last_pos = weights[(weights["date"] == last_day) & (weights["target_weight"] > 1e-15)]
    mix_last = {
        "date": last_day,
        "ballast": BALLAST_ETF,
        "ballast_w": float(
            last_pos.loc[last_pos["instrument"] == BALLAST_ETF, "target_weight"].sum()
        ),
        "n_stocks": int(
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF)
            ].shape[0]
        ),
        "stock_w_sum": float(
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF),
                "target_weight",
            ].sum()
        ),
        "stock_head": (
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF)
            ]
            .sort_values("target_weight", ascending=False)
            .head(8)[["instrument", "target_weight"]]
            .values.tolist()
        ),
    }
    mean_active = float(pos.groupby("date")["instrument"].nunique().mean()) if len(pos) else 0.0
    max_name_all = float(
        pos.loc[is_stock].groupby("date")["target_weight"].max().max()
    ) if is_stock.any() else 0.0

    meta: dict[str, Any] = {
        "mode": "g1g5_capacity_adv",
        "ledger_path": str(ledger_path.relative_to(ROOT)),
        "weights_path": str(wpath.relative_to(ROOT)),
        "weights_rows": int(len(weights)),
        "weights_n_distinct_sessions": n_sess,
        "weights_date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "n_instruments": int(weights["instrument"].nunique()),
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "rebalance_sessions": rebal,
        "n_rebalance_sessions": len(rebal),
        "cadence": "month_end_plus_first_last",
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "ind_cap": IND_CAP,
        "name_cap": NAME_CAP,
        "aum_binding": AUM_BINDING,
        "adv_participation_k": ADV_PARTICIPATION_K,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "stock_budget": STOCK_BUDGET,
        "mean_daily_active_names": mean_active,
        "max_name_weight_observed": max_name_all,
        "mix_last_session": mix_last,
        "turnover_daily": tow,
        "vs_prior_packs": vs,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "ai_columns": ["date", "instrument", "target_weight"],
        "alpha_authoritative_aliases": ["session", "instrument_id", "weight"],
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
        "who_pays_prereg": WHO_PAYS_PREREG,
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "stock_universe_select": uni,
        "mechanism_definition_zh": {
            "signal": "D1 ADV=float_mktcap×turnover/100；SW L1 行业 demean log(ADV) 流动性分位",
            "select": (
                f"高可成交 top{active_n}；容量∝√ADV；单名≤{NAME_CAP:.0%}；"
                f"ADV参与率≤{ADV_PARTICIPATION_K:.0%}@{AUM_BINDING:.0f}；行业≤{IND_CAP:.0%}；"
                f"硬排除 {sorted(HARD_EXCLUDE)}"
            ),
            "ballast": f"{BALLAST_ETF} 名义≈{BALLAST_FRAC:.0%}；禁 etf_core 0.70",
            "rebalance": "月频月末 + 首末日",
            "orthogonality_zh": (
                "相对九败：非估值残差、非OCF、非动量、非四臂、非份额流、非ETF-core、非解禁半月、非调仓；"
                "主叙事=容量/冲击可成交"
            ),
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
        "d1_rows_loaded": score_meta.get("d1_rows"),
        "peak_rss_mb_after_d1": score_meta.get("peak_rss_mb_after_d1"),
        "peak_rss_mb_after_score": score_meta.get("peak_rss_mb_after_score"),
        "horizon_days": horizon_days,
        "max_debate_rounds": max_debate_rounds,
        "benchmark": DEFAULT_BENCHMARK,
        "debates_n": len(debates),
        "debates": debates,
        "settle": settle_meta,
        "g6_proof": g6_proof,
        "peak_rss_kb": peak,
        "peak_rss_kb_start": peak0,
        "peak_rss_mb": round(peak / 1024.0, 1),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_strategy_submit": True,
        "no_yahoo": True,
        "zero_yahoo_reddit_stocktwits": True,
        "not_hard_gates_candidate": True,
        "not_mainline_until_beta_and_leo": True,
        "no_gp": True,
        "no_v29_gp": True,
        "no_resid_etf_isomorph": True,
        "no_etf_core_overlay": True,
        "no_idx_rebal_isomorph": True,
        "no_d1_val_resid_isomorph": True,
        "no_ocf_isomorph": True,
        "no_momentum_main_axis": True,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "d1_adv_asof_used": True,
        "d1_valuation_path": str(D1_VALUATION.relative_to(ROOT)),
        "d1_note_zh": "D1 ACCEPT_FULL 仅研究 asof（turnover×mktcap→ADV）；非晋级授权；未用 pe_ttm 排序",
    }
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }

    slim_logs = []
    for log in (score_meta.get("rebalance_arm_logs") or []):
        slim_logs.append({k: v for k, v in log.items() if k not in ("target",)})
    meta["rebalance_arm_logs_slim"] = slim_logs

    meta_path = out_dir / f"g1g5_capacity_adv_run_meta_{stamp}.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    sidecar = {
        "weights_path": str(wpath.relative_to(ROOT)),
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
        "who_pays_prereg": WHO_PAYS_PREREG,
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "n_rows": int(len(weights)),
        "n_distinct_sessions": n_sess,
        "n_instruments": int(weights["instrument"].nunique()),
        "date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "reaches_x2_end": meta["reaches_x2_end"],
        "x2_end_target": X2_END,
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "ind_cap": IND_CAP,
        "name_cap": NAME_CAP,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "cadence": meta["cadence"],
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "no_gp": True,
        "no_etf_core_overlay": True,
        "no_resid_etf_isomorph": True,
        "no_d1_val_resid_isomorph": True,
        "selection_rule": "adv_ind_demean_capacity_cap4_ind28_exclude_mega_fillgap",
        "role_zh": "机制正交新权重：容量/ADV 可成交约束（研究级）",
        "peak_rss_mb": meta["peak_rss_mb"],
        "g6": (g6_proof or {}).get("G6"),
        "vs_jaccard_stock_mean": {
            k: (v.get("jaccard_stock_mean") if isinstance(v, dict) else None)
            for k, v in vs.items()
        },
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(
        json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 capacity/ADV fillability X2 weights")
    ap.add_argument("--score-n", type=int, default=DEFAULT_SCORE_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_capacity_adv(
            score_n=int(args.score_n),
            active_n=int(args.active_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            weight_start=args.weight_start,
            weight_end=args.weight_end,
        )
    except Exception as e:
        print(
            json.dumps(
                {"error": str(e), "trace": traceback.format_exc()[-4000:]},
                ensure_ascii=False,
            )
        )
        return 1
    slim = {
        k: meta[k]
        for k in meta
        if k
        not in (
            "debates",
            "stock_universe_select",
            "rebalance_arm_logs_slim",
            "rebalance_sessions",
            "vs_prior_packs",
        )
    }
    slim["universe_n"] = (meta.get("stock_universe_select") or {}).get("n")
    slim["debates_n"] = meta.get("debates_n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
    slim["n_rebalance_sessions"] = meta.get("n_rebalance_sessions")
    slim["turnover"] = meta.get("turnover_daily")
    slim["vs_jaccard"] = {
        k: {
            "mean": v.get("jaccard_stock_mean"),
            "max": v.get("jaccard_stock_max"),
            "head": [
                (d.get("session"), d.get("jaccard_stock"))
                for d in (v.get("active_set_compare_sample") or [])[:3]
            ],
        }
        for k, v in (meta.get("vs_prior_packs") or {}).items()
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
