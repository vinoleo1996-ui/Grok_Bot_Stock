#!/usr/bin/env python3
"""G1G5 low-turnover X2 weights — quarterly rebalance + hysteresis bandwidth.

Parent of scoring: g1g5_ashare_inst_friction_v1 (nontextbook).
Changes vs month-end top20 EW:
  - rebalance cadence: quarter-end (510300 calendar) + first/last session
  - hysteresis: enter top-ENTER_N; exit only if rank > EXIT_N; sticky otherwise
  - active_n cap with equal weight among held names
No stub forward-fill; promotion_approved=false; no orders; no Strategy.
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
    month_end_sessions,
    run_g6_lookahead_proof,
    select_mid_large_topn,
    _load_pit_member_index,
)
from research.g1g5_nontextbook_weights import (  # noqa: E402
    W_ETF,
    W_LIMIT,
    W_T1,
    W_UNLOCK,
    WHO_PAYS_ZH,
    _forbid_textbook_tokens,
    _load_etf_flow,
    _load_sw_members,
    _load_unlock,
    combine_scores,
    score_etf_flow,
    score_limit_band,
    score_t1_overhang,
    score_unlock,
)

MECHANISM_TAG = "g1g5_ashare_inst_friction_v1_lowturn"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20
DEFAULT_ENTER_N = 12
DEFAULT_EXIT_N = 28
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
WHO_PAYS_LT = (
    WHO_PAYS_ZH
    + "再平衡降频至季末并加带宽粘性（进 top12 / 出 rank>28），以压换手与成本/AUM；"
    "非换皮相对强弱排序，非教科书估值排序。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def quarter_end_sessions(start: str, end: str) -> list[str]:
    """Last 510300 trading day of each calendar quarter in [start, end]."""
    months = month_end_sessions(start, end)
    out: list[str] = []
    for s in months:
        m = int(str(s)[5:7])
        if m in (3, 6, 9, 12):
            out.append(s)
    return out


def build_rebalance_decisions_lowturn(
    instruments: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    enter_n: int = DEFAULT_ENTER_N,
    exit_n: int = DEFAULT_EXIT_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Quarterly scores + hysteresis band → sticky equal-weight sleeve."""
    sw = _load_sw_members()
    flow = _load_etf_flow()
    unlock = _load_unlock(instruments)
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(instruments, rebalance_sessions)

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    nominal_w = {"etf": W_ETF, "unlock": W_UNLOCK, "t1": W_T1, "limit": W_LIMIT}
    held: set[str] = set()
    turnover_events: list[dict[str, Any]] = []

    for sess in rebalance_sessions:
        eligible = list(instruments)
        if use_pit_membership:
            present = mid_large_members_on(sess, instruments, member_index=member_index)
            eligible = [i for i in instruments if i in present]

        etf_s, etf_m = score_etf_flow(sess, eligible, sw=sw, flow=flow)
        un_s, un_m = score_unlock(sess, eligible, unlock=unlock)
        t1_s, t1_m = score_t1_overhang(sess, eligible)
        lim_s, lim_m = score_limit_band(sess, eligible)
        arms = {"etf": etf_s, "unlock": un_s, "t1": t1_s, "limit": lim_s}
        ameta = {"etf": etf_m, "unlock": un_m, "t1": t1_m, "limit": lim_m}
        combined, cmeta = combine_scores(arms, ameta, nominal_w, eligible)
        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        rank_map = {inst: i + 1 for i, (inst, _) in enumerate(ranked)}
        score_map = dict(combined)

        prev = set(held)
        # drop names that fell below exit band or left eligible
        kept = {i for i in held if i in rank_map and rank_map[i] <= int(exit_n)}
        # enter top enter_n
        entrants = {inst for inst, _ in ranked[: min(int(enter_n), len(ranked))]}
        cand = kept | entrants
        # cap to active_n by score
        ordered = sorted(cand, key=lambda x: score_map.get(x, -1e18), reverse=True)
        held = set(ordered[: min(int(active_n), len(ordered))])
        # if empty (cold start), force top active_n
        if not held and ranked:
            held = {inst for inst, _ in ranked[: min(int(active_n), len(ranked))]}

        added = sorted(held - prev)
        removed = sorted(prev - held)
        turnover_events.append(
            {
                "session": sess,
                "n_held": len(held),
                "n_added": len(added),
                "n_removed": len(removed),
                "one_way_name_turnover": (len(added) + len(removed)) / max(1, int(active_n)),
                "added": added[:8],
                "removed": removed[:8],
            }
        )
        arm_logs.append(
            {
                "session": sess,
                "arms": ameta,
                "combine": cmeta,
                "n_eligible": len(eligible),
                "n_held": len(held),
                "enter_n": enter_n,
                "exit_n": exit_n,
            }
        )

        w_active = (1.0 / len(held)) if held else 0.0
        for inst in instruments:
            if inst in held:
                rating, w = "Overweight", float(w_active)
            elif inst in score_map:
                rating, w = "Underweight", 0.0
            else:
                rating, w = "Abstain", 0.0
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": rating,
                    "target_weight_override": w,
                    "nontextbook_score": score_map.get(inst),
                    "rank": rank_map.get(inst),
                    "selection_rule": "ashare_inst_friction_quarterly_hysteresis_ew",
                }
            )

    mean_tow = float(np.mean([x["one_way_name_turnover"] for x in turnover_events])) if turnover_events else None
    return decisions, {
        "rebalance_arm_logs": arm_logs,
        "nominal_arm_weights": nominal_w,
        "turnover_events": turnover_events,
        "mean_one_way_name_turnover_per_rebal": mean_tow,
        "enter_n": enter_n,
        "exit_n": exit_n,
        "active_n": active_n,
        "cadence": "quarter_end",
    }


def estimate_daily_turnover(weights: pd.DataFrame) -> dict[str, Any]:
    """Mean one-way gross turnover across consecutive sessions (sum |Δw|/2)."""
    piv = weights.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0.0)
    piv = piv.sort_index()
    if len(piv) < 2:
        return {"mean_one_way": None, "n_days": int(len(piv))}
    diff = piv.diff().abs().sum(axis=1) / 2.0
    diff = diff.iloc[1:]
    return {
        "mean_one_way": float(diff.mean()),
        "median_one_way": float(diff.median()),
        "p95_one_way": float(diff.quantile(0.95)),
        "sum_one_way": float(diff.sum()),
        "n_days": int(len(diff)),
        "n_rebalance_days_nonzero": int((diff > 1e-12).sum()),
    }


def run_low_turnover(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    enter_n: int = DEFAULT_ENTER_N,
    exit_n: int = DEFAULT_EXIT_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 1,
    out_dir: Path | None = None,
    also_expand_control: bool = False,
) -> dict[str, Any]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_LT)
    from research.g1g5_x2_panel_stitch import (
        X2_END,
        coverage_report,
        install_equity_close_monkeypatch,
    )

    install_equity_close_monkeypatch()
    out_dir = out_dir or (ROOT / "output" / "intel")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    peak0 = _rss_kb()

    uni = select_mid_large_topn(top_n=top_n)
    instruments = uni["instruments"]
    if len(instruments) < 10:
        raise RuntimeError(f"universe too small: {len(instruments)}")

    rebal = quarter_end_sessions(weight_start, weight_end)
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        last = pd.Timestamp(cal0[-1]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + list(rebal)
        if last not in rebal:
            rebal = list(rebal) + [last]

    decisions, score_meta = build_rebalance_decisions_lowturn(
        instruments,
        rebal,
        active_n=active_n,
        enter_n=enter_n,
        exit_n=exit_n,
        use_pit_membership=True,
    )
    weights = build_daily_weights_expand(
        decisions,
        start=weight_start,
        end=weight_end,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_LT,
        universe_id=UNIVERSE_ID,
    )
    if weights["who_pays_zh"].astype(str).str.contains("动量").any():
        raise RuntimeError("who_pays contains 动量")
    if weights["mechanism_tag"].astype(str).str.contains("momentum|动量|价值", case=False, regex=True).any():
        raise RuntimeError("mechanism_tag contains textbook token")

    tow = estimate_daily_turnover(weights)
    # compare vs prior X2 nontextbook monthly pack if present
    old_path = out_dir / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"
    vs_old: dict[str, Any] = {"old_path": str(old_path.relative_to(ROOT)) if old_path.exists() else None}
    if old_path.exists():
        old = pd.read_parquet(old_path, columns=["date", "instrument", "target_weight"])
        old_tow = estimate_daily_turnover(old)
        vs_old["old_mean_one_way"] = old_tow.get("mean_one_way")
        vs_old["new_mean_one_way"] = tow.get("mean_one_way")
        if old_tow.get("mean_one_way") and tow.get("mean_one_way") is not None:
            vs_old["turnover_reduction_ratio"] = float(
                1.0 - (tow["mean_one_way"] / max(old_tow["mean_one_way"], 1e-12))
            )
        # active-set Jaccard on shared quarter ends
        sample = [x for x in rebal if x >= "2024-03-01"][:6]
        diffs = []
        for ss in sample:
            a = set(weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"])
            b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
            jac = (len(a & b) / len(a | b)) if (a or b) else None
            diffs.append({"session": ss, "n_new": len(a), "n_old": len(b), "jaccard": jac})
        vs_old["active_set_compare_sample"] = diffs

    wpath = out_dir / f"g1g5_lowturn_daily_weights_{stamp}.parquet"
    export_cols = [
        "date", "instrument", "target_weight", "mechanism_tag", "who_pays_zh",
        "universe_id", "session", "instrument_id", "weight",
    ]
    weights[export_cols].to_parquet(wpath, index=False)

    ledger_path = out_dir / f"debate_ledger_g1g5_lowturn_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    # sparse debates (cheap; MEM)
    debates: list[dict[str, Any]] = []
    for inst in list(instruments)[:3]:
        for sess in ["2024-06-28", "2025-06-30", "2026-06-30"]:
            result = build_g1g5_debate(
                session=sess,
                instrument=inst,
                ledger=ledger,
                max_debate_rounds=max_debate_rounds,
                mechanism_tag=MECHANISM_TAG,
                who_pays_zh=WHO_PAYS_LT,
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
    daily_sum = weights.groupby("date")["target_weight"].sum()
    peak = _rss_kb()
    cov = coverage_report(list(instruments))

    meta = {
        "mode": "g1g5_low_turnover_ashare_inst_friction",
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
        "cadence": "quarter_end_plus_edges",
        "active_n": active_n,
        "enter_n": enter_n,
        "exit_n": exit_n,
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "turnover_daily": tow,
        "vs_monthly_nontextbook_x2": vs_old,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_LT,
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "universe_select": uni,
        "score_meta": score_meta,
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
        "not_hard_gates_candidate": True,
        "panel_coverage_x2": cov,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "parent_mechanism": "g1g5_ashare_inst_friction_v1",
        "also_expand_control": also_expand_control,
    }
    meta_path = out_dir / f"g1g5_lowturn_run_meta_{stamp}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    sidecar = {
        "weights_path": str(wpath.relative_to(ROOT)),
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_LT,
        "universe_id": UNIVERSE_ID,
        "n_rows": int(len(weights)),
        "n_distinct_sessions": n_sess,
        "n_instruments": int(weights["instrument"].nunique()),
        "date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "reaches_x2_end": meta["reaches_x2_end"],
        "cadence": "quarter_end_plus_edges",
        "enter_n": enter_n,
        "exit_n": exit_n,
        "active_n": active_n,
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "vs_monthly_mean_one_way": vs_old.get("old_mean_one_way"),
        "turnover_reduction_ratio": vs_old.get("turnover_reduction_ratio"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "role_zh": "主攻降换手（季频+带宽粘性）X2",
        "parent_pack": "output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet",
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 low-turnover X2 weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--enter-n", type=int, default=DEFAULT_ENTER_N)
    ap.add_argument("--exit-n", type=int, default=DEFAULT_EXIT_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_low_turnover(
            top_n=int(args.top_n),
            active_n=int(args.active_n),
            enter_n=int(args.enter_n),
            exit_n=int(args.exit_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            weight_start=args.weight_start,
            weight_end=args.weight_end,
        )
    except Exception as e:
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()[-2500:]}, ensure_ascii=False))
        return 1
    slim = {k: meta[k] for k in meta if k not in ("debates", "universe_select", "score_meta")}
    slim["universe_n"] = (meta.get("universe_select") or {}).get("n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
    slim["turnover"] = meta.get("turnover_daily")
    slim["vs_old"] = {
        k: (meta.get("vs_monthly_nontextbook_x2") or {}).get(k)
        for k in ("old_mean_one_way", "new_mean_one_way", "turnover_reduction_ratio")
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
