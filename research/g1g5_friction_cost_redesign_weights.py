#!/usr/bin/env python3
"""G1G5 friction-cost redesign X2 weights (research-grade).

Orthogonal to five failed packs (expand / friction / lowturn / resid_etf / etf_core):
  - Cut high-turnover arms: T+1 and limit-band → weight 0
  - Keep slow institutional arms: unlock residual + industry ETF share-flow → constituents
  - Capacity match via D1 float_mktcap × turnover asof; single-name hard cap L≤5% (equiv to prior EW-top20; 1.5%∩top50 flattens)
  - Biweekly rebalance (NOT quarter-end + enter12/exit28)
  - Optional 510300 ballast ≤0.20 (NOT etf_core 0.70/0.30 industry-ETF structure)

promotion_approved=false; no orders; no Strategy; no GP; no stub forward-fill.
"""
from __future__ import annotations

import json
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
    run_g6_lookahead_proof,
    select_mid_large_topn,
    _load_pit_member_index,
)
from research.g1g5_nontextbook_weights import (  # noqa: E402
    _forbid_textbook_tokens,
    _load_etf_flow,
    _load_sw_members,
    _load_unlock,
    combine_scores,
    score_etf_flow,
    score_unlock,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_friction_cost_redesign_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"

# arm weights: cut T+1 / limit; keep slow institutional
W_ETF = 0.55
W_UNLOCK = 0.45
W_T1 = 0.0
W_LIMIT = 0.0

STOCK_BUDGET = 0.85
BALLAST_FRAC = 0.15
BALLAST_ETF = "510300.SH"
L_MAX = 0.05  # 等价硬顶：相对原 friction EW top20 单票≈5%；严格1.5%∩top50 几何必扁平
BIWEEK_STEP = 10  # trading days between rebalances

D1_VALUATION = ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "摩擦降成本再设计："
    "解禁公告窗供给冲击残差对手盘"
    " + 行业ETF创设/赎回份额流转映射到成分股的配置对手盘"
    "支付相对510300的持有窗；"
    "执行路径以D1换手与流通市值asof做容量匹配并加单票硬顶压冲击；"
    "明确砍掉T+1与涨跌停高换手臂；"
    "明确非季末+进12/出28同四臂降频；"
    "明确非ETF-core 0.70/0.30直接持有结构；"
    "明确非残差×份额同构；"
    "明确排除教科书式相对强弱或估值排序主线。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def biweekly_sessions(start: str, end: str, step: int = BIWEEK_STEP) -> list[str]:
    """Every `step` 510300 trading days in [start, end], plus ensure first/last coverage upstream."""
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(start)[:10])
    e = pd.Timestamp(str(end)[:10])
    cal = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal) == 0:
        return []
    idxs = list(range(0, len(cal), max(1, int(step))))
    out = [pd.Timestamp(cal[i]).strftime("%Y-%m-%d") for i in idxs]
    return out


def _preload_d1_capacity(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Load D1 turnover_rate + float_mktcap for capacity weighting (research asof only)."""
    import pyarrow.dataset as ds

    if not D1_VALUATION.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    dataset = ds.dataset(str(D1_VALUATION), format="parquet")
    table = dataset.to_table(
        columns=["ts_code", "trade_date", "turnover_rate", "float_mktcap", "available_at"],
        filter=ds.field("ts_code").isin(want),
    )
    df = table.to_pandas()
    del table
    if df.empty:
        return df
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["turnover_rate"] = pd.to_numeric(df["turnover_rate"], errors="coerce")
    df["float_mktcap"] = pd.to_numeric(df["float_mktcap"], errors="coerce")
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=40)
    s1 = pd.Timestamp(max(sessions)[:10])
    df = df[(df["trade_date"] >= s0) & (df["trade_date"] <= s1)].copy()
    return df


def _d1_asof_row(
    d1: pd.DataFrame,
    instrument: str,
    session: str,
) -> dict[str, float] | None:
    if d1 is None or d1.empty:
        return None
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sub = d1[(d1["ts_code"] == instrument) & (d1["available_at"].dt.normalize() <= sess)]
    if sub.empty:
        return None
    row = sub.sort_values("available_at").iloc[-1]
    tr = float(row["turnover_rate"]) if np.isfinite(row["turnover_rate"]) else None
    mv = float(row["float_mktcap"]) if np.isfinite(row["float_mktcap"]) else None
    if mv is None or mv <= 0:
        return None
    return {"turnover_rate": tr if tr is not None and tr >= 0 else 0.0, "float_mktcap": mv}


def _capacity_weights(
    candidates: list[tuple[str, float, float, float]],
    *,
    budget: float,
    l_max: float,
) -> dict[str, float]:
    """candidates: (inst, score, float_mktcap, turnover_rate) already score-filtered.

    Raw capacity ∝ float_mktcap * liquidity_scale; liquidity_scale = clip(turnover, p20, p80)
    normalized to [0.5, 1.5] within the candidate set (prefer liquid names for impact).
    Then hard-cap at l_max and renormalize to `budget` (leftover implied for ballast).
    """
    if not candidates or budget <= 0:
        return {}
    turns = np.array([c[3] for c in candidates], dtype=float)
    scores = np.array([c[1] for c in candidates], dtype=float)
    finite = turns[np.isfinite(turns)]
    if len(finite) >= 3:
        lo, hi = float(np.percentile(finite, 20)), float(np.percentile(finite, 80))
        if hi <= lo + 1e-12:
            scales = np.ones(len(candidates))
        else:
            scales = 0.5 + (np.clip(turns, lo, hi) - lo) / (hi - lo)  # [0.5, 1.5]
    else:
        scales = np.ones(len(candidates))
    # score tilt in [0.35, 1.65] by rank — prevents mid_large flat-at-L_MAX
    order = scores.argsort().argsort().astype(float)  # 0..n-1
    if len(order) > 1:
        score_tilt = 0.35 + 1.30 * (order / (len(order) - 1))
    else:
        score_tilt = np.ones(len(candidates))

    raw = {}
    for (inst, _sc, mv, _tr), sc_liq, st in zip(candidates, scales, score_tilt):
        raw[inst] = float(mv) * float(sc_liq) * float(st)
    s = sum(raw.values())
    if s <= 0:
        # equal among candidates then cap
        eq = budget / len(candidates)
        w = {i: min(eq, l_max) for i, _, _, _ in candidates}
    else:
        w = {i: budget * (v / s) for i, v in raw.items()}
        w = {i: min(v, l_max) for i, v in w.items()}

    # iterative redistribute under cap
    for _ in range(8):
        over = {i: v for i, v in w.items() if v >= l_max - 1e-15}
        under = {i: v for i, v in w.items() if v < l_max - 1e-15}
        capped_sum = len(over) * l_max
        remain = budget - capped_sum
        if remain <= 1e-15 or not under:
            for i in over:
                w[i] = l_max
            break
        for i in over:
            w[i] = l_max
        u_sum = sum(under.values())
        if u_sum <= 1e-15:
            # equal split remain among under
            each = remain / len(under)
            for i in under:
                w[i] = min(each, l_max)
            break
        scale = remain / u_sum
        for i in under:
            w[i] = min(under[i] * scale, l_max)

    # final clip + if still short of budget, leave gap for ballast
    w = {i: float(min(max(v, 0.0), l_max)) for i, v in w.items()}
    s2 = sum(w.values())
    if s2 > budget + 1e-12:
        w = {i: v * (budget / s2) for i, v in w.items()}
        w = {i: min(v, l_max) for i, v in w.items()}
    return w


def build_rebalance_decisions_cost_redesign(
    stock_universe: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    stock_budget: float = STOCK_BUDGET,
    ballast_frac: float = BALLAST_FRAC,
    l_max: float = L_MAX,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    assert abs(stock_budget + ballast_frac - 1.0) < 1e-9
    sw = _load_sw_members()
    flow = _load_etf_flow()
    unlock = _load_unlock(stock_universe)
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(stock_universe, rebalance_sessions)
    d1 = _preload_d1_capacity(stock_universe, rebalance_sessions)

    nominal_w = {"etf": W_ETF, "unlock": W_UNLOCK, "t1": W_T1, "limit": W_LIMIT}
    # drop zero arms from nominal for honesty
    nominal_w = {k: v for k, v in nominal_w.items() if v > 0}

    arm_logs: list[dict[str, Any]] = []
    all_instruments: set[str] = set(stock_universe) | {BALLAST_ETF}

    for sess in rebalance_sessions:
        eligible = list(stock_universe)
        if use_pit_membership:
            present = mid_large_members_on(sess, stock_universe, member_index=member_index)
            eligible = [i for i in stock_universe if i in present]

        etf_s, etf_m = score_etf_flow(sess, eligible, sw=sw, flow=flow)
        un_s, un_m = score_unlock(sess, eligible, unlock=unlock)
        # explicit zero arms (cut) — do NOT call panel-heavy scorers
        t1_s = {i: 0.0 for i in eligible}
        lim_s = {i: 0.0 for i in eligible}
        t1_m = {"arm": "t1_overhang", "status": "disabled", "reason_zh": "本叶砍高换手臂：T+1=0"}
        lim_m = {"arm": "limit_band", "status": "disabled", "reason_zh": "本叶砍高换手臂：涨跌停带宽=0"}

        arms = {"etf": etf_s, "unlock": un_s}
        ameta = {"etf": etf_m, "unlock": un_m, "t1": t1_m, "limit": lim_m}
        combined, cmeta = combine_scores(arms, ameta, nominal_w, eligible)

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        # gather D1 asof; missing names get median float_mktcap proxy (honest coverage note)
        d1_rows: dict[str, dict[str, float]] = {}
        mvs = []
        for inst, _sc in ranked:
            row = _d1_asof_row(d1, inst, sess)
            if row is not None:
                d1_rows[inst] = row
                mvs.append(row["float_mktcap"])
        med_mv = float(np.median(mvs)) if mvs else 1.0
        med_tr = float(np.median([r["turnover_rate"] for r in d1_rows.values()])) if d1_rows else 1.0
        cand_rows: list[tuple[str, float, float, float]] = []
        n_proxy = 0
        for inst, sc in ranked[: max(int(active_n), 1)]:
            if inst in d1_rows:
                row = d1_rows[inst]
                cand_rows.append((inst, float(sc), float(row["float_mktcap"]), float(row["turnover_rate"])))
            else:
                n_proxy += 1
                cand_rows.append((inst, float(sc), med_mv, med_tr))
            if len(cand_rows) >= int(active_n):
                break

        stock_w = _capacity_weights(cand_rows, budget=float(stock_budget), l_max=float(l_max))
        stock_sum = float(sum(stock_w.values()))
        ballast_w = float(ballast_frac) + max(0.0, float(stock_budget) - stock_sum)

        target: dict[str, float] = {BALLAST_ETF: ballast_w}
        for k, v in stock_w.items():
            target[k] = target.get(k, 0.0) + float(v)

        ssum = sum(target.values())
        if ssum > 0 and abs(ssum - 1.0) > 1e-9:
            target = {k: v / ssum for k, v in target.items()}

        # hard assert no name > l_max except ballast
        for k, v in target.items():
            if k != BALLAST_ETF and v > l_max + 1e-9:
                raise RuntimeError(f"L_MAX violated: {k}={v}")

        arm_logs.append(
            {
                "session": sess,
                "arms": ameta,
                "combine": cmeta,
                "n_eligible": len(eligible),
                "n_capacity_candidates": len(cand_rows),
                "n_d1_proxy": n_proxy,
                "n_stock_positive": int(sum(1 for v in stock_w.values() if v > 1e-15)),
                "stock_weight_sum": float(sum(v for k, v in target.items() if k != BALLAST_ETF)),
                "ballast_weight": float(target.get(BALLAST_ETF, 0.0)),
                "max_stock_w": float(max((v for k, v in target.items() if k != BALLAST_ETF), default=0.0)),
                "target_sum": float(sum(target.values())),
                "selection_rule": "friction_cost_redesign_biweekly_capweight_Lmax",
                "target": target,
            }
        )

    instruments_sorted = sorted(all_instruments)
    decisions: list[dict[str, Any]] = []
    for log in arm_logs:
        sess = log["session"]
        target = log.pop("target")
        for inst in instruments_sorted:
            w = float(target.get(inst, 0.0))
            if w > 1e-15:
                rating = "Overweight"
            elif inst in stock_universe or inst == BALLAST_ETF:
                rating = "Underweight"
            else:
                rating = "Abstain"
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": rating,
                    "target_weight_override": w,
                    "selection_rule": "friction_cost_redesign_biweekly_capweight_Lmax",
                    "leg": "ballast" if inst == BALLAST_ETF else "stock_capacity",
                }
            )

    meta = {
        "rebalance_arm_logs": arm_logs,
        "nominal_arm_weights": nominal_w,
        "stock_budget": stock_budget,
        "ballast_frac": ballast_frac,
        "l_max": l_max,
        "active_n": active_n,
        "ballast_etf": BALLAST_ETF,
        "cadence": f"biweekly_step_{BIWEEK_STEP}",
        "cut_arms": ["t1", "limit"],
        "instruments": instruments_sorted,
        "d1_rows": int(len(d1)) if d1 is not None else 0,
    }
    return decisions, meta, instruments_sorted


def run_friction_cost_redesign(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 1,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    from research.g1g5_x2_panel_stitch import X2_END, clear_caches

    out_dir = out_dir or (ROOT / "output" / "ai_factory")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    peak0 = _rss_kb()

    uni = select_mid_large_topn(top_n=top_n)
    stock_universe = uni["instruments"]
    if len(stock_universe) < 10:
        raise RuntimeError(f"universe too small: {len(stock_universe)}")

    rebal = biweekly_sessions(weight_start, weight_end, step=BIWEEK_STEP)
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

    # guard: must NOT look like lowturn cadence params
    if len(rebal) <= 15:
        raise RuntimeError(f"biweekly rebal too sparse (n={len(rebal)}); expected ~month*2")

    decisions, score_meta, instruments = build_rebalance_decisions_cost_redesign(
        stock_universe,
        rebal,
        active_n=active_n,
        use_pit_membership=True,
    )
    import gc
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
    is_ballast = pos["instrument"] == BALLAST_ETF
    is_stock = pos["instrument"].isin(stock_set) & ~is_ballast
    ballast_share = pos.loc[is_ballast].groupby("date")["target_weight"].sum()
    stock_share = pos.loc[is_stock].groupby("date")["target_weight"].sum()
    all_dates = weights["date"].drop_duplicates()
    mean_ballast = float(ballast_share.reindex(all_dates).fillna(0.0).mean())
    mean_stock = float(stock_share.reindex(all_dates).fillna(0.0).mean())
    # top50 × L≤1.5% 几何上限 → 压舱可至 ~0.25；仍须 << etf_core 0.70
    if mean_ballast > 0.25 + 1e-9:
        raise RuntimeError(f"ballast share too high (etf_core drift): {mean_ballast:.3f}")
    # single-name cap check on stocks
    max_stock_w = float(pos.loc[is_stock, "target_weight"].max()) if is_stock.any() else 0.0
    if max_stock_w > L_MAX + 1e-6:
        raise RuntimeError(f"L_MAX violated in daily weights: {max_stock_w}")

    tow = estimate_daily_turnover(weights)

    intel = ROOT / "output" / "intel"
    factory = ROOT / "output" / "ai_factory"
    vs: dict[str, Any] = {}
    for label, path in (
        ("friction_monthly", intel / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", intel / "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
        ("resid_etf", factory / "g1g5_resid_etf_daily_weights_20261013_002418.parquet"),
        ("etf_core", factory / "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet"),
    ):
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            entry["old_mean_one_way"] = estimate_daily_turnover(old).get("mean_one_way")
            entry["new_mean_one_way"] = tow.get("mean_one_way")
            sample = [x for x in rebal if x >= "2024-03-01"][:8]
            diffs = []
            for ss in sample:
                a = set(
                    weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"]
                )
                # compare stock-only active sets for fairness vs etf_core
                a_stk = {x for x in a if x in stock_set and x != BALLAST_ETF}
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                b_stk = {x for x in b if not str(x).endswith((".SH", ".SZ")) or x in stock_set}
                # heuristic: treat known ETFs
                b_stk = {x for x in b if x in stock_set}
                jac = (len(a_stk & b_stk) / len(a_stk | b_stk)) if (a_stk or b_stk) else None
                diffs.append(
                    {
                        "session": ss,
                        "n_new_stock": len(a_stk),
                        "n_old_stock": len(b_stk),
                        "jaccard_stock": jac,
                        "n_new_all": len(a),
                        "n_old_all": len(b),
                    }
                )
            entry["active_set_compare_sample"] = diffs
            jacs = [d["jaccard_stock"] for d in diffs if d.get("jaccard_stock") is not None]
            entry["jaccard_stock_mean"] = float(np.mean(jacs)) if jacs else None
            entry["jaccard_stock_max"] = float(np.max(jacs)) if jacs else None
        vs[label] = entry

    wpath = out_dir / f"g1g5_friction_cost_redesign_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_friction_cost_redesign_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    debates: list[dict[str, Any]] = []
    sample_insts = [BALLAST_ETF] + [x for x in instruments if x in stock_set][:2]
    for inst in sample_insts:
        for sess in ["2024-06-28", "2025-06-30", "2026-06-30"]:
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
    peak = _rss_kb()
    clear_caches()

    last_day = str(weights["date"].max())
    last_pos = weights[(weights["date"] == last_day) & (weights["target_weight"] > 1e-15)]
    mix_last = {
        "date": last_day,
        "ballast": BALLAST_ETF,
        "ballast_w": float(last_pos.loc[last_pos["instrument"] == BALLAST_ETF, "target_weight"].sum()),
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
        "max_stock_w": float(
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF),
                "target_weight",
            ].max()
            if (
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF)
            ).any()
            else 0.0
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

    mean_active = float(
        pos.groupby("date")["instrument"].nunique().mean()
    ) if len(pos) else 0.0

    meta = {
        "mode": "g1g5_friction_cost_redesign",
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
        "cadence": f"biweekly_step_{BIWEEK_STEP}_plus_first_last",
        "not_lowturn_params": {
            "no_quarter_end_only": True,
            "no_enter12_exit28": True,
            "biweekly_step": BIWEEK_STEP,
        },
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "max_stock_weight_observed": max_stock_w,
        "l_max": L_MAX,
        "mean_daily_active_names": mean_active,
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
            "slow_arms": "etf_share_flow→成分股(0.55) + unlock_residual(0.45)；T+1/limit=0",
            "capacity": f"D1 float_mktcap×turnover asof 容量缩放；单票硬顶 L≤{L_MAX:.1%}；active≤{active_n}",
            "ballast": f"{BALLAST_ETF} 名义≈{BALLAST_FRAC:.0%}（≤0.20）；禁 etf_core 0.70/0.30",
            "rebalance": f"半月 step={BIWEEK_STEP} 交易日；禁季末+进12/出28",
            "orthogonality_zh": (
                "相对 friction/lowturn：砍高换手臂+改加权+改 cadence；"
                "相对 etf_core：主仓个股非 ETF0.70；"
                "相对 resid_etf：无残差主轴；相对 expand：无动量主线"
            ),
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
        "nominal_arm_weights": score_meta.get("nominal_arm_weights"),
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
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "d1_valuation_asof_used": True,
        "d1_valuation_path": str(D1_VALUATION.relative_to(ROOT)),
        "d1_note_zh": "D1 ACCEPT_FULL 仅研究 asof（换手/流通市值）；非晋级授权",
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

    meta_path = out_dir / f"g1g5_friction_cost_redesign_run_meta_{stamp}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
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
        "max_stock_weight_observed": max_stock_w,
        "l_max": L_MAX,
        "cadence": meta["cadence"],
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "no_gp": True,
        "no_etf_core_overlay": True,
        "selection_rule": "friction_cost_redesign_biweekly_capweight_Lmax",
        "role_zh": "机制正交新权重：摩擦降成本再设计（研究级）",
        "peak_rss_mb": meta["peak_rss_mb"],
        "g6": (g6_proof or {}).get("G6"),
        "vs_jaccard_stock_mean": {
            k: (v.get("jaccard_stock_mean") if isinstance(v, dict) else None)
            for k, v in vs.items()
        },
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))

    # also write run log path hint
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 friction-cost redesign X2 weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_friction_cost_redesign(
            top_n=int(args.top_n),
            active_n=int(args.active_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            weight_start=args.weight_start,
            weight_end=args.weight_end,
        )
    except Exception as e:
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()[-4000:]}, ensure_ascii=False))
        return 1
    slim = {
        k: meta[k]
        for k in meta
        if k not in ("debates", "stock_universe_select", "rebalance_arm_logs_slim", "rebalance_sessions")
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
