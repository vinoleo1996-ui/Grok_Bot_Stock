#!/usr/bin/env python3
"""G1G5 non-textbook A-share mechanism daily weights (research-grade).

Mechanism arms (combinable, PIT-defendable) — NOT textbook momentum/value:
  1) ETF industry share-flow (creation/redemption) → SW L1 → constituents
  2) Unlock residual pressure (announced float unlock window)
  3) T+1 sell overhang (prior-day high OC ret + high turnover → locked sellers)
  4) Limit-band crowding / relief (proximity to ±limit_ratio without price-mom sort)

Forbidden as main line: momentum / value / quality textbook factors.
promotion_approved=false; no orders; no Strategy; no Yahoo; no stub forward-fill.
"""
from __future__ import annotations

import json
import resource
import sys
import traceback
from datetime import date, datetime, timedelta
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
    DEFAULT_D0_PANELS,
    DEFAULT_HORIZON_DAYS,
    _load_benchmark_closes,
    to_panel_id,
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

# --- constants ---
MECHANISM_TAG = "g1g5_ashare_inst_friction_v1"  # no momentum/value tokens
UNIVERSE_ID = EXPAND_UNIVERSE_ID  # reuse top50 mid_large
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
WHO_PAYS_ZH = (
    "A股制度摩擦组合：行业ETF申赎份额流对手盘（创设/赎回）"
    " + 解禁公告后供给冲击残差对手盘"
    " + T+1当日买入次日才能卖出的隔夜抛压对手盘"
    " + 涨跌停带宽拥挤/跌停缓解中的限价制度对手盘；"
    "明确排除教科书式相对强弱或估值排序主线；"
    "相对510300持有窗由上述制度与事件对手盘支付。"
)

ETF_FLOW_BY_SW = ROOT / "data" / "v2" / "etf" / "share_pit" / "ind_etf_share_flow_by_sw_l1.parquet"
SW_MEMBERS = ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1_tushare.parquet"
SHARE_FLOAT_PIT = ROOT / "data" / "v2" / "share_float" / "share_float_pit.parquet"

# arm weights (sum≈1); honest if an arm is coverage_gap → zero that arm
W_ETF = 0.40
W_UNLOCK = 0.25
W_T1 = 0.20
W_LIMIT = 0.15

ETF_FLOW_LOOKBACK_SESSIONS = 5
UNLOCK_FORWARD_CAL_DAYS = 20
T1_TURN_Q = 0.70  # within-name hist quantile for "high turnover"
LIMIT_PROX_UP = 0.85
LIMIT_PROX_DN = 0.85


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _forbid_textbook_tokens(tag: str, who: str) -> None:
    """Hard reject textbook main-tag tokens in mechanism_tag / who_pays_zh."""
    tag_l = tag.lower()
    for b in ("momentum", "mom_", "value", "quality", "价值", "动量"):
        if b in tag_l or b in tag:
            raise RuntimeError(f"textbook_token_forbidden_in_mechanism_tag:{b!r}")
    if "动量" in who:
        raise RuntimeError("textbook_token_forbidden: who_pays_zh contains 动量")


_PANEL_CACHE: dict[str, pd.DataFrame] = {}
_SW_CACHE: pd.DataFrame | None = None
_FLOW_CACHE: pd.DataFrame | None = None
_UNLOCK_CACHE: pd.DataFrame | None = None


def _load_panel_features(instrument: str) -> pd.DataFrame:
    """OHLCV + limit_ratio for one name; indexed by session date (D0∪asof_extend X2)."""
    if instrument in _PANEL_CACHE:
        return _PANEL_CACHE[instrument]
    from research.g1g5_x2_panel_stitch import load_panel_features_x2

    df = load_panel_features_x2(instrument)
    _PANEL_CACHE[instrument] = df
    return df


def _load_sw_members() -> pd.DataFrame:
    global _SW_CACHE
    if _SW_CACHE is not None:
        return _SW_CACHE
    sw = pd.read_parquet(SW_MEMBERS)
    sw = sw.copy()
    sw["in_date"] = pd.to_datetime(sw["in_date"])
    sw["out_date"] = pd.to_datetime(sw["out_date"])
    _SW_CACHE = sw
    return sw


def _load_etf_flow() -> pd.DataFrame:
    global _FLOW_CACHE
    if _FLOW_CACHE is not None:
        return _FLOW_CACHE
    if not ETF_FLOW_BY_SW.exists():
        _FLOW_CACHE = pd.DataFrame()
        return _FLOW_CACHE
    flow = pd.read_parquet(ETF_FLOW_BY_SW)
    flow = flow.copy()
    flow["trade_date"] = pd.to_datetime(flow["trade_date"].astype(str))
    flow["available_at"] = pd.to_datetime(flow["available_at"]).dt.tz_localize(None)
    _FLOW_CACHE = flow
    return flow


def _load_unlock(instruments: Sequence[str]) -> pd.DataFrame:
    global _UNLOCK_CACHE
    if _UNLOCK_CACHE is not None:
        return _UNLOCK_CACHE
    if not SHARE_FLOAT_PIT.exists():
        _UNLOCK_CACHE = pd.DataFrame()
        return _UNLOCK_CACHE
    want = set(instruments)
    df = pd.read_parquet(
        SHARE_FLOAT_PIT,
        columns=["ts_code", "float_date", "float_ratio", "available_at", "float_share"],
    )
    df = df[df["ts_code"].isin(want)].copy()
    df["float_date"] = pd.to_datetime(df["float_date"].astype(str))
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["float_ratio"] = pd.to_numeric(df["float_ratio"], errors="coerce").fillna(0.0)
    _UNLOCK_CACHE = df
    return df


def sw_code_on(instrument: str, session: pd.Timestamp, sw: pd.DataFrame) -> str | None:
    pid = to_panel_id(instrument)
    sub = sw[sw["instrument_id"] == pid]
    if sub.empty:
        return None
    sess = pd.Timestamp(session).normalize()
    hit = sub[(sub["in_date"] <= sess) & ((sub["out_date"].isna()) | (sub["out_date"] > sess))]
    if hit.empty:
        return None
    return str(hit.iloc[-1]["sw_code"])


def score_etf_flow(
    session: str,
    instruments: Sequence[str],
    *,
    sw: pd.DataFrame,
    flow: pd.DataFrame,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Industry ETF share-flow (PIT via available_at) → name score = industry trailing sum."""
    meta: dict[str, Any] = {"arm": "etf_share_flow", "status": "ok"}
    if flow.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "缺 ind_etf_share_flow_by_sw_l1；本臂跳过"
        return {i: 0.0 for i in instruments}, meta
    sess = pd.Timestamp(str(session)[:10]).normalize()
    # PIT: only rows with available_at.date <= session
    avail = flow[flow["available_at"].dt.normalize() <= sess]
    if avail.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"asof≤{session} 无可见 ETF 份额流"
        return {i: 0.0 for i in instruments}, meta
    # trailing N distinct trade_dates
    dates = sorted(avail["trade_date"].unique())
    if not dates:
        meta["status"] = "coverage_gap"
        return {i: 0.0 for i in instruments}, meta
    use_dates = dates[-ETF_FLOW_LOOKBACK_SESSIONS:]
    window = avail[avail["trade_date"].isin(use_dates)]
    ind = window.groupby("sw_l1_code")["flow_est_wan_yuan"].sum()
    # cross-section z among industries present in univ
    inst_sw: dict[str, str] = {}
    for inst in instruments:
        code = sw_code_on(inst, sess, sw)
        if code:
            inst_sw[inst] = code
    meta["n_mapped"] = len(inst_sw)
    meta["n_industries"] = len(set(inst_sw.values()))
    meta["flow_dates"] = [pd.Timestamp(d).strftime("%Y-%m-%d") for d in use_dates]
    if ind.empty or not inst_sw:
        meta["status"] = "coverage_gap"
        return {i: 0.0 for i in instruments}, meta
    # z-score industries that appear in universe
    used = ind.reindex(sorted(set(inst_sw.values()))).fillna(0.0)
    mu, sd = float(used.mean()), float(used.std(ddof=0))
    if sd < 1e-12:
        z = used * 0.0
    else:
        z = (used - mu) / sd
    out = {i: float(z.get(inst_sw[i], 0.0)) if i in inst_sw else 0.0 for i in instruments}
    meta["ind_flow_sum_head"] = {k: float(v) for k, v in used.sort_values(ascending=False).head(5).items()}
    return out, meta


def score_unlock(
    session: str,
    instruments: Sequence[str],
    *,
    unlock: pd.DataFrame,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Upcoming unlock pressure: sum float_ratio with available_at≤sess and float_date in (sess, sess+N].

    Higher pressure → more negative score (avoid supply shock).
    """
    meta: dict[str, Any] = {"arm": "unlock_residual", "status": "ok"}
    if unlock.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "缺 share_float_pit；本臂跳过"
        return {i: 0.0 for i in instruments}, meta
    sess = pd.Timestamp(str(session)[:10]).normalize()
    end = sess + pd.Timedelta(days=UNLOCK_FORWARD_CAL_DAYS)
    vis = unlock[unlock["available_at"].dt.normalize() <= sess]
    win = vis[(vis["float_date"] > sess) & (vis["float_date"] <= end)]
    pressure = win.groupby("ts_code")["float_ratio"].sum()
    meta["n_names_with_pressure"] = int((pressure > 0).sum())
    meta["events_in_window"] = int(len(win))
    if pressure.empty:
        # honest: sparse is OK — zero pressure, not coverage_gap of table
        meta["note_zh"] = "窗内无已公告解禁；压力=0（非缺表）"
        return {i: 0.0 for i in instruments}, meta
    # cross-section z of pressure among univ, then negate
    ser = pd.Series({i: float(pressure.get(i, 0.0)) for i in instruments})
    mu, sd = float(ser.mean()), float(ser.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
    out = {i: float(-z.loc[i]) for i in instruments}  # high pressure → low score
    return out, meta


def score_t1_overhang(
    session: str,
    instruments: Sequence[str],
) -> tuple[dict[str, float], dict[str, Any]]:
    """T+1 friction: prior session high open→close return + elevated turnover → sell overhang.

    Uses only bars with index ≤ session (PIT). Score is negative overhang (avoid).
    """
    meta: dict[str, Any] = {"arm": "t1_overhang", "status": "ok", "n_scored": 0}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    raw: dict[str, float] = {}
    for inst in instruments:
        df = _load_panel_features(inst)
        if df.empty:
            raw[inst] = 0.0
            continue
        hist = df[df.index <= sess]
        if len(hist) < 22:
            raw[inst] = 0.0
            continue
        # prior completed bar = last row ≤ sess (rebalance after close → same day known)
        # For next-day portfolio we use asof close; overhang is from THIS session's OC+turn
        # relative to its own history — institutional T+1: bought today, can sell tomorrow.
        row = hist.iloc[-1]
        o, c, turn = float(row["open"]), float(row["close"]), float(row.get("turnover") or 0.0)
        if not (o > 0 and np.isfinite(o) and np.isfinite(c)):
            raw[inst] = 0.0
            continue
        oc = c / o - 1.0
        turn_hist = hist["turnover"].iloc[:-1].dropna()
        if len(turn_hist) < 20 or not np.isfinite(turn):
            raw[inst] = 0.0
            continue
        thr = float(turn_hist.quantile(T1_TURN_Q))
        high_turn = turn >= thr and thr > 0
        # overhang intensity: positive OC on high-turn day (buyers locked until T+1)
        overhang = max(oc, 0.0) * (1.0 if high_turn else 0.35)
        raw[inst] = float(overhang)
        meta["n_scored"] = int(meta["n_scored"]) + 1
    ser = pd.Series(raw)
    mu, sd = float(ser.mean()), float(ser.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
    out = {i: float(-z.loc[i]) for i in instruments}
    if meta["n_scored"] < max(5, len(instruments) // 5):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"T+1 可计分名过少 n={meta['n_scored']}"
    return out, meta


def score_limit_band(
    session: str,
    instruments: Sequence[str],
) -> tuple[dict[str, float], dict[str, Any]]:
    """Limit-band friction via proximity = day_ret / limit_ratio (no upper_limit col needed).

    - Near upper band (prox≥0.85): crowding → negative
    - Near lower band (prox≤-0.85): forced-seller relief candidate → positive
    Uses last ≤5 sessions ≤ asof (PIT).
    """
    meta: dict[str, Any] = {"arm": "limit_band", "status": "ok", "n_scored": 0, "n_near_up": 0, "n_near_dn": 0}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    raw: dict[str, float] = {}
    for inst in instruments:
        df = _load_panel_features(inst)
        if df.empty:
            raw[inst] = 0.0
            continue
        hist = df[df.index <= sess]
        if len(hist) < 6:
            raw[inst] = 0.0
            continue
        win = hist.iloc[-5:]
        score = 0.0
        prev = None
        for ts, row in win.iterrows():
            c = float(row["close"]) if np.isfinite(row["close"]) else None
            if c is None or c <= 0:
                continue
            lr = row.get("limit_ratio_at_open")
            lr = float(lr) if lr is not None and np.isfinite(lr) and float(lr) > 0 else 0.10
            if prev is not None and prev > 0:
                ret = c / prev - 1.0
                prox = ret / lr
                if prox >= LIMIT_PROX_UP:
                    score -= 1.0  # crowding
                    meta["n_near_up"] = int(meta["n_near_up"]) + 1
                elif prox <= -LIMIT_PROX_DN:
                    score += 0.75  # relief
                    meta["n_near_dn"] = int(meta["n_near_dn"]) + 1
            prev = c
        raw[inst] = float(score)
        meta["n_scored"] = int(meta["n_scored"]) + 1
    ser = pd.Series(raw)
    mu, sd = float(ser.mean()), float(ser.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
    out = {i: float(z.loc[i]) for i in instruments}
    return out, meta


def combine_scores(
    arms: dict[str, dict[str, float]],
    arm_meta: dict[str, dict[str, Any]],
    weights: dict[str, float],
    instruments: Sequence[str],
) -> tuple[dict[str, float], dict[str, Any]]:
    """Weighted sum; zero weight for coverage_gap arms; renormalize."""
    live: dict[str, float] = {}
    for name, w in weights.items():
        st = (arm_meta.get(name) or {}).get("status", "ok")
        if st == "coverage_gap":
            live[name] = 0.0
        else:
            live[name] = float(w)
    s = sum(live.values())
    if s <= 0:
        # fallback: equal among non-gap if all gap somehow
        for name in weights:
            if (arm_meta.get(name) or {}).get("status") != "coverage_gap":
                live[name] = 1.0
        s = sum(live.values())
    if s > 0:
        live = {k: v / s for k, v in live.items()}
    out = {i: 0.0 for i in instruments}
    for name, w in live.items():
        if w == 0:
            continue
        for i in instruments:
            out[i] += w * float(arms[name].get(i, 0.0))
    return out, {"arm_weights_effective": live, "arm_weights_nominal": dict(weights)}


def build_rebalance_decisions_nontextbook(
    instruments: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sw = _load_sw_members()
    flow = _load_etf_flow()
    unlock = _load_unlock(instruments)
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(instruments, rebalance_sessions)

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    nominal_w = {"etf": W_ETF, "unlock": W_UNLOCK, "t1": W_T1, "limit": W_LIMIT}

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
        arm_logs.append({"session": sess, "arms": ameta, "combine": cmeta, "n_eligible": len(eligible)})

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        active = [i for i, _ in ranked[: min(int(active_n), len(ranked))]]
        active_set = set(active)
        w_active = (1.0 / len(active_set)) if active_set else 0.0
        score_map = dict(combined)

        for inst in instruments:
            if inst in active_set:
                rating = "Overweight"
                w = float(w_active)
            elif inst in score_map:
                rating = "Underweight"
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
                    "nontextbook_score": score_map.get(inst),
                    "selection_rule": "ashare_inst_friction_composite_topN_ew",
                }
            )
    return decisions, {"rebalance_arm_logs": arm_logs, "nominal_arm_weights": nominal_w}


def run_sparse_debates_nt(
    ledger: JsonlDebateLedger,
    instruments: Sequence[str],
    *,
    sessions: Sequence[str] | None = None,
    max_debate_rounds: int = 2,
    n_instruments: int = 6,
) -> list[dict[str, Any]]:
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
                    "turns": len(result.turns),
                    "mechanism_tag": MECHANISM_TAG,
                    "universe_id": UNIVERSE_ID,
                    "promotion_approved": False,
                }
            )
    return debates


def run_nontextbook(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 2,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
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
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + list(rebal)

    decisions, score_meta = build_rebalance_decisions_nontextbook(
        instruments, rebal, active_n=active_n, use_pit_membership=True
    )

    weights = build_daily_weights_expand(
        decisions,
        start=weight_start,
        end=weight_end,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_ZH,
        universe_id=UNIVERSE_ID,
    )
    # hard assert no textbook tokens in exported who_pays / tag
    if weights["mechanism_tag"].isna().any() or (weights["mechanism_tag"].astype(str).str.len() == 0).any():
        raise RuntimeError("mechanism_tag empty")
    if weights["who_pays_zh"].astype(str).str.contains("动量").any():
        raise RuntimeError("who_pays contains 动量")
    if weights["mechanism_tag"].astype(str).str.contains("momentum|动量|价值", case=False, regex=True).any():
        raise RuntimeError("mechanism_tag contains textbook token")

    wpath = out_dir / f"g1g5_nontextbook_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_nontextbook_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    debates = run_sparse_debates_nt(
        ledger,
        instruments,
        sessions=["2024-06-28", "2025-06-30", "2026-06-30"],
        max_debate_rounds=max_debate_rounds,
        n_instruments=min(6, len(instruments)),
    )
    edge = build_g1g5_debate(
        session="2026-06-25",
        instrument=instruments[0],
        ledger=ledger,
        max_debate_rounds=max_debate_rounds,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_ZH,
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
    daily_sum = weights.groupby("date")["target_weight"].sum()
    peak = _rss_kb()

    # overlap with old expand pack (same univ) — selection difference
    old_path = out_dir / "g1g5_expand_daily_weights_20261012_105459.parquet"
    overlap_note: dict[str, Any] = {"old_expand": str(old_path.relative_to(ROOT)) if old_path.exists() else None}
    if old_path.exists():
        old = pd.read_parquet(old_path, columns=["date", "instrument", "target_weight"])
        # compare active sets on shared month-ends
        sample_sess = [x for x in rebal if x >= "2024-01-02"][:6]
        diffs = []
        for ss in sample_sess:
            a = set(weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"])
            b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
            diffs.append(
                {
                    "session": ss,
                    "n_new": len(a),
                    "n_old": len(b),
                    "jaccard": (len(a & b) / len(a | b)) if (a or b) else None,
                    "only_new_n": len(a - b),
                    "only_old_n": len(b - a),
                }
            )
        overlap_note["active_set_compare_sample"] = diffs

    meta = {
        "mode": "g1g5_nontextbook_ashare_inst_friction",
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
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_eng": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "ai_columns": ["date", "instrument", "target_weight"],
        "alpha_authoritative_aliases": ["session", "instrument_id", "weight"],
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "universe_select": uni,
        "mechanism_definition_zh": {
            "etf_share_flow": (
                f"行业ETF份额流 PIT（available_at≤session）；"
                f"trailing {ETF_FLOW_LOOKBACK_SESSIONS} 个可见 trade_date 的 flow_est_wan_yuan 行业加总 → 截面z → 成分继承"
            ),
            "unlock_residual": (
                f"share_float_pit：available_at≤session 且 float_date∈(session, session+{UNLOCK_FORWARD_CAL_DAYS}d] "
                "的 float_ratio 加总为供给压力 → 截面z后取负（规避解禁冲击）"
            ),
            "t1_overhang": (
                "D0 panel：当日 open→close 正收益 × 换手偏高（相对自身历史分位）→ T+1 抛压悬置；截面z后取负"
            ),
            "limit_band": (
                "近5日 day_ret/limit_ratio_at_open：近涨停带拥挤扣分、近跌停带缓解加分；非价格动量排序"
            ),
            "selection": f"四臂加权合成后 top{active_n} 等权；禁 excess_vs_510300 排序",
        },
        "vs_expand_momentum_pack": {
            "old_weights": "output/intel/g1g5_expand_daily_weights_20261012_105459.parquet",
            "old_mechanism": "截面 excess_20d vs 510300 → top20 等权（教科书动量）",
            "new_mechanism": MECHANISM_TAG,
            "old_who_pays_had_momentum": True,
            "new_who_pays_forbids_momentum": True,
            "retained": True,
            "deprecated": False,
            "role_zh": "备选/对照（未废弃）",
            "note_zh": "扩池动量包保留备选/对照；本批为主攻；勿废弃。",
            **overlap_note,
        },
        "score_meta": score_meta,
        "horizon_days": horizon_days,
        "max_debate_rounds": max_debate_rounds,
        "benchmark": DEFAULT_BENCHMARK,
        "debates": debates,
        "debates_n": len(debates),
        "settle": settle_meta,
        "g6_proof": g6_proof,
        "peak_rss_kb": peak,
        "peak_rss_kb_start": peak0,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_yahoo": True,
        "no_strategy_submit": True,
        "zero_yahoo_reddit_stocktwits": True,
        "not_hard_gates_candidate": True,
        "not_mainline_until_beta_and_leo": True,
    }
    # panel coverage honesty (must reach weight_end without stub)
    cov = coverage_report(list(instruments))
    meta["panel_coverage_x2"] = cov
    meta["weight_end_requested"] = str(weight_end)
    meta["x2_end_target"] = X2_END
    meta["reaches_x2_end"] = bool(str(weights["date"].max()) >= str(X2_END)[:10])
    meta["stub_forward_fill"] = False
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }

    meta_path = out_dir / f"g1g5_nontextbook_run_meta_{stamp}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    sidecar = {
        "weights_path": str(wpath.relative_to(ROOT)),
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
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
        "panel_coverage_x2": cov,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "selection_rule": "ashare_inst_friction_composite_top20_ew",
        "role_zh": "主攻候选（非教科书制度摩擦）X2延伸",
        "vs_expand_pack_role": "backup_and_control",
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 non-textbook A-share mechanism weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=2)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_nontextbook(
            top_n=int(args.top_n),
            active_n=int(args.active_n),
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
    slim["debates_n"] = meta.get("debates_n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
    slim["arm_gap_sessions"] = [
        {
            "session": x.get("session"),
            "gaps": [k for k, v in (x.get("arms") or {}).items() if (v or {}).get("status") == "coverage_gap"],
        }
        for x in ((meta.get("score_meta") or {}).get("rebalance_arm_logs") or [])
    ]
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
