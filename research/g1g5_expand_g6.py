#!/usr/bin/env python3
"""G1G5 expand mid_large pool + G6 memory as_of filter (research-grade).

- Universe: Data mid_large_members_pit top-N by float_mktcap ∩ D0 panels
- Full daily weights 2024 (510300 calendar), NOT 10-day stub
- G6: resolution_date ≤ asof on memory injection; dry-run proves lookahead blocked
- promotion_approved=false; no orders; no Strategy; no Yahoo/Reddit/StockTwits
"""
from __future__ import annotations

import json
import resource
import sys
import traceback
from datetime import date, datetime
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.intel.debate_ledger import JsonlDebateLedger  # noqa: E402
from research.ai_debate_memory_runner import (  # noqa: E402
    DEFAULT_BENCHMARK,
    DEFAULT_D0_PANELS,
    DEFAULT_HORIZON_DAYS,
    _load_benchmark_closes,
    _load_equity_closes,
    load_prior_settlements,
    settlement_resolved_date,
    to_panel_id,
    to_ts_style,
)
from research.g1g5_wiring import (  # noqa: E402
    COLUMN_CONTRACT_VERSION,
    COLUMN_CONTRACT_VERSION_QM_ALIAS,
    HARD_GATE_VERSION,
    RATING_TO_WEIGHT,
    WHO_PAYS_ZH,
    append_g1g5_round,
    build_daily_weights,
    build_g1g5_debate,
    settle_pending_g5,
)

# --- constants ---
MECHANISM_TAG = "g1g5_pit_debate_rule_v2_expand"
UNIVERSE_ID = "g1g5_mid_large_liquid_top50"
UNIVERSE_KIND = "mid_large_stock"
MID_LARGE_PIT = ROOT / "data" / "v2" / "universe" / "mid_large_members_pit.parquet"
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20  # equal-weight long sleeve on rebalance
ANCHOR_SESSION = "2024-06-28"
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
WHO_PAYS_EXPAND = (
    "扩池辩论规则模板相对 510300 的持有窗 alpha 由错误定价修正对手盘支付；"
    "截面动量 PIT 规则选股；非事件臂、非隔夜因子。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def panel_id_to_ts(pid: str) -> str:
    """sh.600519 → 600519.SH"""
    s = str(pid).strip()
    if "." not in s:
        return s
    a, b = s.split(".", 1)
    if a.lower() in ("sh", "sz", "bj") and b.isdigit():
        return f"{b}.{a.upper()}"
    return to_ts_style(s)


def select_mid_large_topn(
    *,
    top_n: int = DEFAULT_TOP_N,
    anchor: str = ANCHOR_SESSION,
    pit_path: Path = MID_LARGE_PIT,
    panels_dir: Path = DEFAULT_D0_PANELS,
) -> dict[str, Any]:
    """Select top-N by float_mktcap from Data mid_large PIT on anchor session ∩ D0 panel."""
    cols = ["session", "instrument_id", "float_mktcap_basis", "universe_id"]
    # Only read anchor session rows to save RAM
    df = pd.read_parquet(pit_path, columns=cols)
    sub = df[df["session"] == str(anchor)[:10]].copy()
    del df
    sub = sub.sort_values("float_mktcap_basis", ascending=False)
    selected: list[str] = []
    skipped_no_panel: list[str] = []
    mcaps: dict[str, float] = {}
    for _, row in sub.iterrows():
        pid = str(row["instrument_id"])
        p = panels_dir / f"{pid}.parquet"
        ts = panel_id_to_ts(pid)
        if not p.exists():
            skipped_no_panel.append(ts)
            continue
        selected.append(ts)
        mcaps[ts] = float(row["float_mktcap_basis"])
        if len(selected) >= int(top_n):
            break
    return {
        "instruments": selected,
        "n": len(selected),
        "anchor_session": str(anchor)[:10],
        "source_pit": str(pit_path.relative_to(ROOT)),
        "source_universe_id": "mid_large",
        "rule_zh": (
            f"Data mid_large_members_pit @ {anchor} 按 float_mktcap_basis 降序；"
            f"保留有 D0 panel 的前 {top_n}；≠ CSI300 标签；"
            "自研可交易子集，待 Data D3 成员交叉审计（本批已接 PIT 源）。"
        ),
        "mcaps_head": {k: mcaps[k] for k in selected[:5]},
        "skipped_no_panel_n": len(skipped_no_panel),
        "promotion_approved": False,
    }


_PIT_MEMBER_CACHE: dict[str, set[str]] | None = None


def _load_pit_member_index(
    instruments: Sequence[str],
    sessions: Sequence[str],
    *,
    pit_path: Path = MID_LARGE_PIT,
) -> dict[str, set[str]]:
    """session → set of ts-style instruments present in mid_large (filtered)."""
    global _PIT_MEMBER_CACHE
    want_pids = {to_panel_id(x) for x in instruments}
    pid_to_ts = {to_panel_id(x): x for x in instruments}
    sess_set = {str(s)[:10] for s in sessions}
    df = pd.read_parquet(pit_path, columns=["session", "instrument_id"])
    df = df[df["session"].isin(sess_set) & df["instrument_id"].isin(want_pids)]
    out: dict[str, set[str]] = {s: set() for s in sess_set}
    for sess, pid in zip(df["session"].astype(str), df["instrument_id"].astype(str)):
        ts = pid_to_ts.get(pid)
        if ts:
            out.setdefault(str(sess)[:10], set()).add(ts)
    del df
    _PIT_MEMBER_CACHE = out
    return out


def mid_large_members_on(
    session: str,
    instruments: Sequence[str],
    *,
    pit_path: Path = MID_LARGE_PIT,
    member_index: dict[str, set[str]] | None = None,
) -> set[str]:
    """PIT membership check: which of `instruments` are in mid_large on session."""
    idx = member_index
    if idx is None:
        idx = _load_pit_member_index(instruments, [session], pit_path=pit_path)
    present = idx.get(str(session)[:10], set())
    return {i for i in instruments if i in present}


def month_end_sessions(start: str, end: str) -> list[str]:
    """Last 510300 trading day of each calendar month in [start, end]."""
    bench = _load_benchmark_closes("510300")
    if bench.empty:
        raise RuntimeError("510300 calendar missing")
    s = pd.Timestamp(str(start)[:10])
    e = pd.Timestamp(str(end)[:10])
    idx = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(idx) == 0:
        return []
    ser = pd.Series(idx, index=idx)
    # group by YYYY-MM, take last
    keys = ser.index.to_period("M")
    out: list[str] = []
    for _, g in ser.groupby(keys):
        out.append(pd.Timestamp(g.iloc[-1]).strftime("%Y-%m-%d"))
    return out


def excess_return(
    instrument: str,
    session: str,
    *,
    lookback: int = 20,
) -> float | None:
    """PIT excess return vs 510300 over `lookback` trading bars ending at session."""
    from research.g1g5_x2_panel_stitch import load_equity_closes_x2

    inst = load_equity_closes_x2(instrument)
    bench = _load_benchmark_closes("510300")
    if inst.empty or bench.empty:
        return None
    sess = pd.Timestamp(str(session)[:10])
    # refuse stale: last available bar must be the session itself (no stub)
    if sess not in inst.index:
        # allow if session is trading day but name halted — still require last bar == session
        ih_all = inst[inst.index <= sess]
        if ih_all.empty or pd.Timestamp(ih_all.index[-1]).normalize() != sess.normalize():
            return None
        ih = ih_all
    else:
        ih = inst[inst.index <= sess]
    bh = bench[bench.index <= sess]
    if len(ih) < lookback + 1 or len(bh) < lookback + 1:
        return None
    # ensure we are scoring AT session, not a prior stale end
    if pd.Timestamp(ih.index[-1]).normalize() != sess.normalize():
        return None
    px0, px1 = float(ih.iloc[-(lookback + 1)]), float(ih.iloc[-1])
    b0, b1 = float(bh.iloc[-(lookback + 1)]), float(bh.iloc[-1])
    if px0 <= 0 or b0 <= 0:
        return None
    return (px1 / px0 - 1.0) - (b1 / b0 - 1.0)


def score_to_rating(excess: float | None, *, rank_pct: float | None) -> str:
    """Map cross-section rank to rating label."""
    if excess is None or rank_pct is None:
        return "Abstain"
    if rank_pct <= 0.20:  # top 20%
        return "Overweight" if excess > 0 else "Hold"
    if rank_pct <= 0.40:
        return "Hold"
    if rank_pct >= 0.80:
        return "Underweight"
    return "Hold"


def build_rebalance_decisions(
    instruments: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    lookback: int = 20,
    use_pit_membership: bool = True,
) -> list[dict[str, Any]]:
    """Cross-sectional PIT rule: equal-weight top-active_n by excess@lookback.

    Also emits rating labels for ledger compatibility. Weights on rebalance day
    are 1/active_n for selected names, 0 for others (explicit zero decision).
    """
    decisions: list[dict[str, Any]] = []
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(instruments, rebalance_sessions)
    for sess in rebalance_sessions:
        eligible = list(instruments)
        if use_pit_membership:
            present = mid_large_members_on(
                sess, instruments, member_index=member_index
            )
            eligible = [i for i in instruments if i in present]
        scored: list[tuple[str, float]] = []
        for inst in eligible:
            ex = excess_return(inst, sess, lookback=lookback)
            if ex is None:
                continue
            scored.append((inst, float(ex)))
        scored.sort(key=lambda x: x[1], reverse=True)
        n = len(scored)
        active = scored[: min(int(active_n), n)]
        active_set = {i for i, _ in active}
        w_active = (1.0 / len(active_set)) if active_set else 0.0
        # rank pct for rating tags
        rank_map = {inst: (i + 1) / n for i, (inst, _) in enumerate(scored)} if n else {}
        excess_map = {inst: ex for inst, ex in scored}
        for inst in instruments:
            if inst in active_set:
                rating = "Overweight"
                w = float(w_active)
            elif inst in excess_map:
                rp = rank_map.get(inst)
                rating = score_to_rating(excess_map[inst], rank_pct=rp)
                w = float(RATING_TO_WEIGHT.get(rating, 0.0)) * 0.0  # non-active → 0 sleeve
                rating = "Underweight" if rating != "Abstain" else "Abstain"
                w = 0.0
            else:
                rating = "Abstain"
                w = 0.0
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": rating,
                    "target_weight_override": w,
                    "excess_20d": excess_map.get(inst),
                }
            )
    return decisions


def build_daily_weights_expand(
    decisions: Sequence[dict[str, Any]],
    *,
    start: str,
    end: str,
    mechanism_tag: str = MECHANISM_TAG,
    who_pays_zh: str = WHO_PAYS_EXPAND,
    universe_id: str = UNIVERSE_ID,
) -> pd.DataFrame:
    """Full calendar weights; uses target_weight_override when present (equal-weight sleeve)."""
    mech = str(mechanism_tag or "").strip()
    if not mech:
        raise ValueError("missing_mechanism_tag")
    bench = _load_benchmark_closes("510300")
    if bench.empty:
        raise RuntimeError("510300 calendar unavailable")
    s = pd.Timestamp(str(start)[:10])
    e = pd.Timestamp(str(end)[:10])
    cal = bench.index[(bench.index >= s) & (bench.index <= e)]
    by_inst: dict[str, list[tuple[pd.Timestamp, float, str]]] = {}
    for d in decisions:
        inst = str(d.get("instrument") or "")
        if not inst:
            continue
        sess = pd.Timestamp(str(d.get("session") or "")[:10])
        if "target_weight_override" in d and d["target_weight_override"] is not None:
            w = float(d["target_weight_override"])
        else:
            w = float(RATING_TO_WEIGHT.get(str(d.get("rating") or "Abstain"), 0.0))
        rating = str(d.get("rating") or "Abstain")
        by_inst.setdefault(inst, []).append((sess, w, rating))
    for inst in by_inst:
        by_inst[inst].sort(key=lambda x: x[0])

    rows: list[dict[str, Any]] = []
    for dt in cal:
        for inst, events in by_inst.items():
            w = 0.0
            for sess, tw, _rating in events:
                if sess <= dt:
                    w = tw
                else:
                    break
            rows.append(
                {
                    "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                    "instrument": inst,
                    "target_weight": float(w),
                    "mechanism_tag": mech,
                    "who_pays_zh": who_pays_zh,
                    "universe_id": universe_id,
                    "universe_kind": UNIVERSE_KIND,
                    "promotion_approved": False,
                }
            )
    out = pd.DataFrame(rows)
    out["session"] = out["date"]
    out["instrument_id"] = out["instrument"].map(lambda x: to_panel_id(str(x)))
    out["weight"] = out["target_weight"]
    n_sess = int(out["date"].nunique())
    out.attrs["n_distinct_sessions"] = n_sess
    out.attrs["stub_window"] = bool(n_sess <= 10)
    out.attrs["column_contract_version"] = COLUMN_CONTRACT_VERSION
    out.attrs["mechanism_tag"] = mech
    out.attrs["universe_id"] = universe_id
    out.attrs["promotion_approved"] = False
    return out


def run_g6_lookahead_proof(ledger: JsonlDebateLedger) -> dict[str, Any]:
    """Prove G6 blocks settlements whose resolution_date > asof."""
    # Fabricate two settlement-shaped rows into a temp side ledger for unit proof
    # without polluting the main expand ledger semantics: write to a proof file.
    proof_path = ledger.path.parent / (ledger.path.stem + "_g6_proof.jsonl")
    if proof_path.exists():
        proof_path.unlink()
    proof = JsonlDebateLedger(proof_path)
    # Past-resolved lesson (OK to inject on 2024-06-28)
    proof.append_settlement(
        {
            "decision_id": "dec_g6_past",
            "session": "2024-03-15",
            "instrument": "600519.SH",
            "horizon_days": 5,
            "benchmark": "510300",
            "raw_return": 0.01,
            "alpha_vs_benchmark": 0.005,
            "reflection_zh": "G6 proof past-resolved lesson",
            "settled_at": "2024-03-22T15:00:00",
            "resolution_date": "2024-03-22",
            "promotion_approved": False,
        }
    )
    # Future-resolved relative to 2024-06-28 (MUST be blocked)
    proof.append_settlement(
        {
            "decision_id": "dec_g6_future",
            "session": "2024-06-28",
            "instrument": "600519.SH",
            "horizon_days": 5,
            "benchmark": "510300",
            "raw_return": 0.99,
            "alpha_vs_benchmark": 0.99,
            "reflection_zh": "G6 proof FUTURE-resolved lookahead bait",
            "settled_at": "2024-07-05T15:00:00",
            "resolution_date": "2024-07-05",
            "promotion_approved": False,
        }
    )
    asof = "2024-06-28"
    with_filter = load_prior_settlements(
        proof, instrument="600519.SH", limit=10, non_null_only=True, as_of=asof
    )
    without = load_prior_settlements(
        proof, instrument="600519.SH", limit=10, non_null_only=True, as_of=None
    )
    ids_f = {r.get("decision_id") for r in with_filter}
    ids_all = {r.get("decision_id") for r in without}
    blocked = "dec_g6_future" not in ids_f and "dec_g6_future" in ids_all
    kept = "dec_g6_past" in ids_f
    # Also verify settlement_resolved_date helper
    future_row = next(r for r in without if r.get("decision_id") == "dec_g6_future")
    past_row = next(r for r in without if r.get("decision_id") == "dec_g6_past")
    ok_dates = (
        settlement_resolved_date(future_row) == "2024-07-05"
        and settlement_resolved_date(past_row) == "2024-03-22"
    )
    status = "pass" if (blocked and kept and ok_dates) else "fail"
    return {
        "G6": status,
        "as_of": asof,
        "with_filter_ids": sorted(ids_f),
        "without_filter_ids": sorted(ids_all),
        "blocked_future": blocked,
        "kept_past": kept,
        "resolved_date_helper_ok": ok_dates,
        "proof_ledger": str(proof_path.relative_to(ROOT)),
        "note_zh": "仅 resolution_date≤asof 的 settlement 可回灌；前视课被挡。",
    }


def run_sparse_debates(
    ledger: JsonlDebateLedger,
    instruments: Sequence[str],
    *,
    sessions: Sequence[str] | None = None,
    max_debate_rounds: int = 2,
    n_instruments: int = 6,
) -> list[dict[str, Any]]:
    """Sparse full G1–G5 debates for ledger/G6 evidence (not full universe)."""
    sess_list = list(sessions or ["2024-03-15", "2024-06-28", "2024-09-30"])
    sample = list(instruments)[: int(n_instruments)]
    debates: list[dict[str, Any]] = []
    for inst in sample:
        for sess in sess_list:
            result = build_g1g5_debate(
                session=sess,
                instrument=inst,
                ledger=ledger,
                max_debate_rounds=max_debate_rounds,
                mechanism_tag=MECHANISM_TAG,
                who_pays_zh=WHO_PAYS_EXPAND,
            )
            # Override universe_id on decision
            if result.decision is not None:
                result.decision["universe_id"] = UNIVERSE_ID  # type: ignore[index]
            entry = append_g1g5_round(ledger, result)
            debates.append(
                {
                    "decision_id": entry.get("decision_id"),
                    "instrument": inst,
                    "session": sess,
                    "rating": entry.get("rating"),
                    "turns": len(result.turns),
                    "memory_injected": bool(getattr(result, "_memory_injected", False)),
                    "mechanism_tag": MECHANISM_TAG,
                    "universe_id": UNIVERSE_ID,
                    "promotion_approved": False,
                }
            )
    return debates


def run_expand_g6(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 2,
    out_dir: Path | None = None,
) -> dict[str, Any]:
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

    rebal = month_end_sessions(weight_start, weight_end)
    # Prepend first 510300 session so Jan is not zero-cash until month-end
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + list(rebal)
    decisions = build_rebalance_decisions(
        instruments, rebal, active_n=active_n, lookback=20, use_pit_membership=True
    )

    weights = build_daily_weights_expand(
        decisions,
        start=weight_start,
        end=weight_end,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_EXPAND,
        universe_id=UNIVERSE_ID,
    )
    wpath = out_dir / f"g1g5_expand_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_expand_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)

    g6_proof = run_g6_lookahead_proof(ledger)

    debates = run_sparse_debates(
        ledger,
        instruments,
        sessions=["2024-06-28", "2025-06-30", "2026-06-30"],
        max_debate_rounds=max_debate_rounds,
        n_instruments=min(6, len(instruments)),
    )
    # pending-edge probe for G5 continuity
    edge = build_g1g5_debate(
        session="2026-06-25",
        instrument=instruments[0],
        ledger=ledger,
        max_debate_rounds=max_debate_rounds,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_EXPAND,
    )
    if edge.decision is not None:
        edge.decision["universe_id"] = UNIVERSE_ID  # type: ignore[index]
    append_g1g5_round(ledger, edge)
    debates.append(
        {
            "decision_id": edge.decision.get("decision_id") if edge.decision else None,
            "instrument": instruments[0],
            "session": "2026-06-25",
            "rating": edge.decision.get("rating") if edge.decision else None,
            "pending_edge_probe": True,
            "promotion_approved": False,
        }
    )

    settle_meta = settle_pending_g5(ledger, horizon_days=horizon_days)

    n_sess = int(weights["date"].nunique())
    # daily gross exposure check
    daily_sum = weights.groupby("date")["target_weight"].sum()
    peak = _rss_kb()

    meta = {
        "mode": "g1g5_expand_g6",
        "ledger_path": str(ledger_path.relative_to(ROOT)),
        "weights_path": str(wpath.relative_to(ROOT)),
        "weights_rows": int(len(weights)),
        "weights_n_distinct_sessions": n_sess,
        "weights_date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "weights_instruments": sorted(weights["instrument"].unique().tolist()),
        "n_instruments": int(weights["instrument"].nunique()),
        "stub_window": bool(n_sess <= 10),
        "rebalance_sessions": rebal,
        "active_n": active_n,
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_eng": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "ai_columns": ["date", "instrument", "target_weight"],
        "alpha_authoritative_aliases": ["session", "instrument_id", "weight"],
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_EXPAND,
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "universe_select": uni,
        "data_d3_note_zh": "已接 data/v2/universe/mid_large_members_pit；top50 可交易子集待进一步 D3 交叉审计。",
        "horizon_days": horizon_days,
        "max_debate_rounds": max_debate_rounds,
        "benchmark": DEFAULT_BENCHMARK,
        "debates": debates,
        "debates_n": len(debates),
        "settle": settle_meta,
        "g6_proof": g6_proof,
        "peak_rss_kb": peak,
        "peak_rss_kb_start": peak0,
        "vs_old_pack": {
            "old_weights": "output/intel/g1g5_daily_weights_20261012_104627.parquet",
            "old_n_instruments": 3,
            "old_rows": 726,
            "new_n_instruments": int(weights["instrument"].nunique()),
            "new_rows": int(len(weights)),
            "delta_instruments": int(weights["instrument"].nunique()) - 3,
        },
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_yahoo": True,
        "no_strategy_submit": True,
        "zero_yahoo_reddit_stocktwits": True,
        "not_hard_gates_candidate": True,
    }
    cov = coverage_report(list(instruments))
    meta["panel_coverage_x2"] = cov
    meta["weight_end_requested"] = str(weight_end)
    meta["x2_end_target"] = X2_END
    meta["reaches_x2_end"] = bool(str(weights["date"].max()) >= str(X2_END)[:10])
    meta["stub_forward_fill"] = False
    meta["role_zh"] = "备选/对照（教科书动量截面）X2延伸；非主线"
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }
    meta_path = out_dir / f"g1g5_expand_run_meta_{stamp}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    sidecar = {
        "weights_path": str(wpath.relative_to(ROOT)),
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_EXPAND,
        "universe_id": UNIVERSE_ID,
        "n_rows": int(len(weights)),
        "n_distinct_sessions": n_sess,
        "n_instruments": int(weights["instrument"].nunique()),
        "date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "reaches_x2_end": meta["reaches_x2_end"],
        "x2_end_target": X2_END,
        "panel_coverage_x2": cov,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "role_zh": "备选/对照（动量）X2延伸",
        "not_mainline": True,
        "no_orders": True,
        "no_strategy_submit": True,
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 expand mid_large + G6")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=2)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_expand_g6(
            top_n=int(args.top_n),
            active_n=int(args.active_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            weight_start=args.weight_start,
            weight_end=args.weight_end,
        )
    except Exception as e:
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()[-2000:]}, ensure_ascii=False))
        return 1
    slim = {k: meta[k] for k in meta if k not in ("debates", "universe_select")}
    slim["universe_n"] = (meta.get("universe_select") or {}).get("n")
    slim["debates_n"] = meta.get("debates_n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
