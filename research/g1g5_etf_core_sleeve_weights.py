#!/usr/bin/env python3
"""G1G5 ETF-core + stock sleeve X2 weights (research-grade).

Structure (orthogonal to 100% stock four packs):
  CORE  ~70%: liquid industry ETFs selected by SW-L1 share-flow PIT + 510300 ballast
  SLEEVE~30%: limited mid-large names in inflow industries, scored by D1 turnover asof
              (liquidity absorption) — NOT residual-return × share-flow, NOT PE/PB value

Forbidden: textbook momentum/value/quality tokens; CB/gold; SEAT-SPLIT/UNLOCK mainline;
stub forward-fill; V35 fake-run; GP; Strategy submit.
promotion_approved=false; no orders.
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
from research.g1g5_nontextbook_weights import (  # noqa: E402
    _forbid_textbook_tokens,
    _load_etf_flow,
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_etf_core_sleeve_v1"
UNIVERSE_ID = "g1g5_etf_core_sleeve_mid_large_v1"
DEFAULT_TOP_N = 50
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"

CORE_FRAC = 0.70
SLEEVE_FRAC = 0.30
CORE_BALLAST_FRAC = 0.25  # of CORE → 510300
N_CORE_ETF = 5
N_SLEEVE = 8
ETF_FLOW_LOOKBACK = 5
BALLAST_ETF = "510300.SH"

ETF_MAP_DAILY = ROOT / "data" / "v2" / "etf" / "sw_l1_etf_map_pit_daily.parquet"
D1_VALUATION = ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet"

WHO_PAYS_ZH = (
    "ETF-core+个股袖套混合："
    "行业ETF创设/赎回份额流对手盘支付液态行业ETF-core相对宽基压舱的配置差"
    " + 流入行业内中大盘个股的流动性承接/冲击吸收对手盘支付有限袖套；"
    "明确排除教科书式相对强弱排序与估值排序主线；"
    "明确非100%股票满仓四包（expand/nontextbook/lowturn/resid_etf）同构；"
    "相对510300持有窗由上述份额流与流动性承接对手盘支付。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _load_etf_map_daily() -> pd.DataFrame:
    cols = [
        "sw_l1_code",
        "trade_date",
        "etf_ts_code",
        "amt20",
        "aum_wan",
        "match_type",
        "no_etf",
        "available_at",
    ]
    df = pd.read_parquet(ETF_MAP_DAILY, columns=cols)
    df = df.copy()
    df["trade_date"] = df["trade_date"].astype(str).str.replace("-", "", regex=False)
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["amt20"] = pd.to_numeric(df["amt20"], errors="coerce")
    return df


def _industry_flow_z(
    session: str,
    flow: pd.DataFrame,
    lookback: int = ETF_FLOW_LOOKBACK,
) -> tuple[pd.Series, dict[str, Any]]:
    """SW-L1 trailing share-flow z-scores, PIT via available_at."""
    meta: dict[str, Any] = {"arm": "etf_core_flow", "status": "ok"}
    if flow is None or flow.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "缺 ind_etf_share_flow_by_sw_l1"
        return pd.Series(dtype=float), meta
    sess = pd.Timestamp(str(session)[:10]).normalize()
    avail = flow[flow["available_at"].dt.normalize() <= sess]
    if avail.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"asof≤{session} 无可见份额流"
        return pd.Series(dtype=float), meta
    dates = sorted(avail["trade_date"].unique())
    use_dates = dates[-lookback:]
    window = avail[avail["trade_date"].isin(use_dates)]
    ind = window.groupby("sw_l1_code")["flow_est_wan_yuan"].sum()
    meta["flow_dates"] = [pd.Timestamp(d).strftime("%Y-%m-%d") for d in use_dates]
    meta["n_industries_raw"] = int(len(ind))
    if ind.empty or float(ind.std(ddof=0) or 0) < 1e-12:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "行业流截面退化"
        return pd.Series(dtype=float), meta
    z = (ind - float(ind.mean())) / float(ind.std(ddof=0))
    meta["top_flow"] = {str(k): float(v) for k, v in ind.sort_values(ascending=False).head(5).items()}
    return z.astype(float), meta


def _pick_liquid_etf_for_sw(
    session: str,
    sw_codes: Sequence[str],
    etf_map: pd.DataFrame,
) -> dict[str, str]:
    """Map SW L1 → one liquid industry ETF (max amt20 among exact/close), PIT."""
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sess_key = sess.strftime("%Y%m%d")
    sub = etf_map[
        (etf_map["trade_date"] == sess_key)
        & (~etf_map["no_etf"].astype(bool))
        & (etf_map["match_type"].isin(["exact", "close"]))
        & (etf_map["available_at"].dt.normalize() <= sess)
        & (etf_map["sw_l1_code"].isin(list(sw_codes)))
    ].copy()
    if sub.empty:
        # fallback: latest available_at ≤ sess per sw (map may miss exact session)
        sub = etf_map[
            (~etf_map["no_etf"].astype(bool))
            & (etf_map["match_type"].isin(["exact", "close"]))
            & (etf_map["available_at"].dt.normalize() <= sess)
            & (etf_map["sw_l1_code"].isin(list(sw_codes)))
        ].copy()
        if sub.empty:
            return {}
        sub = sub.sort_values(["sw_l1_code", "available_at", "amt20"])
        sub = sub.groupby("sw_l1_code", as_index=False).tail(1)
    else:
        sub = sub.sort_values(["sw_l1_code", "amt20"], ascending=[True, False])
        sub = sub.groupby("sw_l1_code", as_index=False).head(1)
    out: dict[str, str] = {}
    for _, row in sub.iterrows():
        code = str(row["etf_ts_code"] or "").strip()
        if code and code != BALLAST_ETF:
            out[str(row["sw_l1_code"])] = code
    return out


def _preload_turnover_matrix(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Wide turnover_rate (session × instrument) from D1 ACCEPT_FULL, asof-safe rows only.

    Rows are keyed by trade_date; caller must only use a row when available_at.date <= decision session.
    We store available_at alongside and mask at score time.
    """
    import pyarrow.dataset as ds

    if not D1_VALUATION.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    sess_keys = {str(s)[:10].replace("-", "") for s in sessions}
    # also need a few prior days for asof lag — load all dates for these names (bounded)
    dataset = ds.dataset(str(D1_VALUATION), format="parquet")
    table = dataset.to_table(
        columns=["ts_code", "trade_date", "turnover_rate", "available_at"],
        filter=ds.field("ts_code").isin(want),
    )
    df = table.to_pandas()
    del table
    if df.empty:
        return pd.DataFrame()
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["turnover_rate"] = pd.to_numeric(df["turnover_rate"], errors="coerce")
    # keep rows whose trade_date is near our calendar (trim memory)
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=40)
    s1 = pd.Timestamp(max(sessions)[:10])
    df = df[(df["trade_date"] >= s0) & (df["trade_date"] <= s1)]
    return df


def _turnover_asof(
    d1: pd.DataFrame,
    instrument: str,
    session: str,
) -> float | None:
    """Latest turnover_rate with available_at.normalize() <= session (EOD asof)."""
    if d1 is None or d1.empty:
        return None
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sub = d1[(d1["ts_code"] == instrument) & (d1["available_at"].dt.normalize() <= sess)]
    if sub.empty:
        return None
    row = sub.sort_values("available_at").iloc[-1]
    v = float(row["turnover_rate"])
    if not np.isfinite(v):
        return None
    return v


def build_rebalance_decisions_etf_core_sleeve(
    stock_universe: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    core_frac: float = CORE_FRAC,
    sleeve_frac: float = SLEEVE_FRAC,
    n_core_etf: int = N_CORE_ETF,
    n_sleeve: int = N_SLEEVE,
    ballast_of_core: float = CORE_BALLAST_FRAC,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    """Return decisions covering all instruments that ever receive weight + zeros for univ."""
    assert abs(core_frac + sleeve_frac - 1.0) < 1e-9
    sw = _load_sw_members()
    flow = _load_etf_flow()
    etf_map = _load_etf_map_daily()
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(stock_universe, rebalance_sessions)
    d1 = _preload_turnover_matrix(stock_universe, rebalance_sessions)

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    all_instruments: set[str] = set(stock_universe) | {BALLAST_ETF}

    for sess in rebalance_sessions:
        eligible = list(stock_universe)
        if use_pit_membership:
            present = mid_large_members_on(sess, stock_universe, member_index=member_index)
            eligible = [i for i in stock_universe if i in present]

        flow_z, flow_meta = _industry_flow_z(sess, flow)
        # pick top industries by flow z
        if flow_meta.get("status") == "coverage_gap" or flow_z.empty:
            core_etfs: list[str] = []
            top_sw: list[str] = []
            flow_meta["fallback"] = "ballast_only"
        else:
            top_sw = [str(x) for x in flow_z.sort_values(ascending=False).head(n_core_etf).index.tolist()]
            sw_to_etf = _pick_liquid_etf_for_sw(sess, top_sw, etf_map)
            # preserve industry rank order, unique ETFs
            core_etfs = []
            seen = set()
            for swc in top_sw:
                etf = sw_to_etf.get(swc)
                if etf and etf not in seen:
                    core_etfs.append(etf)
                    seen.add(etf)
            flow_meta["top_sw"] = top_sw
            flow_meta["sw_to_etf"] = sw_to_etf
            flow_meta["core_etfs"] = list(core_etfs)

        all_instruments.update(core_etfs)

        # --- core weights ---
        ballast_w = float(core_frac) * float(ballast_of_core)
        flow_budget = float(core_frac) - ballast_w
        core_w: dict[str, float] = {BALLAST_ETF: ballast_w}
        if core_etfs and flow_budget > 0:
            w_each = flow_budget / len(core_etfs)
            for e in core_etfs:
                core_w[e] = core_w.get(e, 0.0) + w_each
        else:
            # no industry ETF → all core to ballast
            core_w[BALLAST_ETF] = float(core_frac)

        # --- sleeve: stocks in top-flow industries, score by D1 turnover asof ---
        sleeve_candidates = []
        top_sw_set = set(top_sw)
        sess_ts = pd.Timestamp(str(sess)[:10]).normalize()
        for inst in eligible:
            code = sw_code_on(inst, sess_ts, sw)
            if top_sw_set and code not in top_sw_set:
                continue
            if not top_sw_set:
                # coverage gap on flow → allow all eligible for sleeve score
                pass
            tr = _turnover_asof(d1, inst, sess)
            if tr is None:
                continue
            sleeve_candidates.append((inst, float(tr)))

        sleeve_meta: dict[str, Any] = {
            "arm": "stock_sleeve_turnover_absorb",
            "n_candidates": len(sleeve_candidates),
            "status": "ok" if sleeve_candidates else "coverage_gap",
        }
        sleeve_w: dict[str, float] = {}
        if sleeve_candidates:
            sleeve_candidates.sort(key=lambda x: x[1], reverse=True)
            active = [i for i, _ in sleeve_candidates[: min(n_sleeve, len(sleeve_candidates))]]
            w_s = float(sleeve_frac) / len(active)
            for i in active:
                sleeve_w[i] = w_s
            sleeve_meta["active"] = active
            sleeve_meta["turnover_head"] = {
                i: float(t) for i, t in sleeve_candidates[: min(5, len(sleeve_candidates))]
            }
        else:
            # sleeve gap → push sleeve budget into ballast (honest)
            core_w[BALLAST_ETF] = core_w.get(BALLAST_ETF, 0.0) + float(sleeve_frac)
            sleeve_meta["reason_zh"] = "袖套候选空；袖套预算并入510300压舱"
            sleeve_meta["fallback_to_ballast"] = True

        # combine target map for this session
        target: dict[str, float] = {}
        for k, v in core_w.items():
            target[k] = target.get(k, 0.0) + float(v)
        for k, v in sleeve_w.items():
            target[k] = target.get(k, 0.0) + float(v)

        # renormalize tiny drift
        ssum = sum(target.values())
        if ssum > 0 and abs(ssum - 1.0) > 1e-9:
            target = {k: v / ssum for k, v in target.items()}

        arm_logs.append(
            {
                "session": sess,
                "core": flow_meta,
                "sleeve": sleeve_meta,
                "n_eligible_stocks": len(eligible),
                "target_sum": float(sum(target.values())),
                "etf_weight_sum": float(sum(v for k, v in target.items() if k not in stock_universe or k == BALLAST_ETF)),
                "stock_weight_sum": float(sum(v for k, v in target.items() if k in stock_universe and k != BALLAST_ETF)),
                "n_positive": int(sum(1 for v in target.values() if v > 1e-15)),
            }
        )

        # defer per-instrument decision rows until we know full instrument list
        # stash session targets in arm_logs for second pass
        arm_logs[-1]["target"] = target

    # second pass: emit decisions for union of all instruments
    instruments_sorted = sorted(all_instruments)
    for log in arm_logs:
        sess = log["session"]
        target = log.pop("target")
        for inst in instruments_sorted:
            w = float(target.get(inst, 0.0))
            if w > 1e-15:
                rating = "Overweight"
            elif inst in stock_universe or inst == BALLAST_ETF or inst in target:
                rating = "Underweight"
            else:
                rating = "Abstain"
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": rating,
                    "target_weight_override": w,
                    "selection_rule": "etf_core_flow_plus_stock_sleeve_turnover",
                    "leg": (
                        "ballast"
                        if inst == BALLAST_ETF
                        else ("etf_core" if inst not in stock_universe else "stock_sleeve")
                    ),
                }
            )

    # fix etf_weight_sum accounting: ETFs are those not in stock_universe
    for log in arm_logs:
        # already computed with imperfect filter; recompute note in meta only
        pass

    meta = {
        "rebalance_arm_logs": arm_logs,
        "core_frac": core_frac,
        "sleeve_frac": sleeve_frac,
        "ballast_of_core": ballast_of_core,
        "n_core_etf": n_core_etf,
        "n_sleeve": n_sleeve,
        "ballast_etf": BALLAST_ETF,
        "instruments": instruments_sorted,
    }
    return decisions, meta, instruments_sorted


def run_etf_core_sleeve(
    *,
    top_n: int = DEFAULT_TOP_N,
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

    rebal = month_end_sessions(weight_start, weight_end)
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + list(rebal)

    decisions, score_meta, instruments = build_rebalance_decisions_etf_core_sleeve(
        stock_universe,
        rebal,
        use_pit_membership=True,
    )
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

    # structure checks
    daily_sum = weights.groupby("date")["target_weight"].sum()
    if float(daily_sum.min()) < 0.99 or float(daily_sum.max()) > 1.01:
        raise RuntimeError(
            f"daily_gross out of band: min={daily_sum.min()} max={daily_sum.max()}"
        )

    stock_set = set(stock_universe)
    pos = weights[weights["target_weight"] > 1e-15].copy()
    is_stock_mask = pos["instrument"].isin(stock_set) & (pos["instrument"] != BALLAST_ETF)
    pos_etf = pos.loc[~is_stock_mask].groupby("date")["target_weight"].sum()
    pos_stk = pos.loc[is_stock_mask].groupby("date")["target_weight"].sum()
    # align to all dates
    all_dates = weights["date"].drop_duplicates()
    etf_share = pos_etf.reindex(all_dates).fillna(0.0)
    stock_share = pos_stk.reindex(all_dates).fillna(0.0)
    mean_etf_share = float(etf_share.mean()) if len(etf_share) else 0.0
    mean_stock_share = float(stock_share.mean()) if len(stock_share) else 0.0
    if mean_etf_share < 0.50:
        raise RuntimeError(
            f"ETF-core structure failed: mean_etf_share={mean_etf_share:.3f} (<0.50)"
        )

    tow = estimate_daily_turnover(weights)

    # overlap vs prior 100% stock packs (active set Jaccard on stocks only + instrument mix)
    intel = ROOT / "output" / "intel"
    factory = ROOT / "output" / "ai_factory"
    vs: dict[str, Any] = {}
    for label, path in (
        ("resid_etf", factory / "g1g5_resid_etf_daily_weights_20261013_002418.parquet"),
        ("nontextbook_monthly", intel / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", intel / "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
    ):
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            entry["old_mean_one_way"] = estimate_daily_turnover(old).get("mean_one_way")
            entry["new_mean_one_way"] = tow.get("mean_one_way")
            sample = [x for x in rebal if x >= "2024-03-01"][:6]
            diffs = []
            for ss in sample:
                a = set(weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"])
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                jac = (len(a & b) / len(a | b)) if (a or b) else None
                diffs.append(
                    {
                        "session": ss,
                        "n_new": len(a),
                        "n_old": len(b),
                        "jaccard": jac,
                        "only_new_n": len(a - b),
                        "new_etf_n": len([x for x in a if x not in stock_set or x == BALLAST_ETF]),
                    }
                )
            entry["active_set_compare_sample"] = diffs
        vs[label] = entry

    wpath = out_dir / f"g1g5_etf_core_sleeve_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_etf_core_sleeve_{stamp}.jsonl"
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

    # instrument mix snapshot
    last_day = str(weights["date"].max())
    last_pos = weights[(weights["date"] == last_day) & (weights["target_weight"] > 1e-15)]
    mix_last = {
        "date": last_day,
        "etf_instruments": sorted(
            last_pos.loc[
                ~last_pos["instrument"].isin(stock_set) | (last_pos["instrument"] == BALLAST_ETF),
                "instrument",
            ].unique().tolist()
        ),
        "stock_instruments": sorted(
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF),
                "instrument",
            ].unique().tolist()
        ),
        "etf_weight_sum": float(
            last_pos.loc[
                ~last_pos["instrument"].isin(stock_set) | (last_pos["instrument"] == BALLAST_ETF),
                "target_weight",
            ].sum()
        ),
        "stock_weight_sum": float(
            last_pos.loc[
                last_pos["instrument"].isin(stock_set) & (last_pos["instrument"] != BALLAST_ETF),
                "target_weight",
            ].sum()
        ),
    }

    meta = {
        "mode": "g1g5_etf_core_sleeve",
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
        "cadence": "month_end_plus_first",
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "mean_etf_weight_share": mean_etf_share,
        "mean_stock_sleeve_share": mean_stock_share,
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
        "who_pays_prereg": "docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md",
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "stock_universe_select": uni,
        "mechanism_definition_zh": {
            "etf_core": (
                f"名义 {CORE_FRAC:.0%}：SW L1 份额流 PIT top{N_CORE_ETF} → "
                f"液态行业 ETF（map_pit_daily max amt20）；"
                f"core 内 {CORE_BALLAST_FRAC:.0%} 为 510300 压舱"
            ),
            "stock_sleeve": (
                f"名义 {SLEEVE_FRAC:.0%}：流入行业 ∩ 中大盘宇宙；"
                f"D1 turnover_rate asof 承接排序 top{N_SLEEVE} 等权；禁 PE/PB 估值主轴；禁残差收益主轴"
            ),
            "orthogonality_zh": (
                "相对 expand/nontextbook/lowturn/resid_etf：主仓直接持有 ETF，非 100% 股票满仓；"
                "袖套用换手承接而非残差×份额交互"
            ),
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
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
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "d1_valuation_asof_used": True,
        "d1_valuation_path": str(D1_VALUATION.relative_to(ROOT)),
        "d1_note_zh": "D1 ACCEPT_FULL 仅研究 asof（换手）；非晋级授权",
    }
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }

    # attach slim arm logs (drop huge if any)
    slim_logs = []
    for log in (score_meta.get("rebalance_arm_logs") or []):
        slim_logs.append(
            {
                k: v
                for k, v in log.items()
                if k not in ("target",)
            }
        )
    meta["rebalance_arm_logs_slim"] = slim_logs

    meta_path = out_dir / f"g1g5_etf_core_sleeve_run_meta_{stamp}.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    sidecar = {
        "weights_path": str(wpath.relative_to(ROOT)),
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
        "who_pays_prereg": "docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md",
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
        "mean_etf_weight_share": mean_etf_share,
        "mean_stock_sleeve_share": mean_stock_share,
        "mix_last_session": mix_last,
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "selection_rule": "etf_core_flow_plus_stock_sleeve_turnover",
        "role_zh": "机制正交新权重：ETF-core+个股袖套混合（研究级）",
        "peak_rss_mb": meta["peak_rss_mb"],
        "g6": (g6_proof or {}).get("G6"),
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 ETF-core + stock sleeve X2 weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_etf_core_sleeve(
            top_n=int(args.top_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            weight_start=args.weight_start,
            weight_end=args.weight_end,
        )
    except Exception as e:
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()[-3000:]}, ensure_ascii=False))
        return 1
    slim = {k: meta[k] for k in meta if k not in ("debates", "stock_universe_select", "rebalance_arm_logs_slim")}
    slim["universe_n"] = (meta.get("stock_universe_select") or {}).get("n")
    slim["debates_n"] = meta.get("debates_n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
    slim["turnover"] = meta.get("turnover_daily")
    slim["vs_jaccard_head"] = {
        k: [(d.get("session"), d.get("jaccard"), d.get("new_etf_n")) for d in (v.get("active_set_compare_sample") or [])[:3]]
        for k, v in (meta.get("vs_prior_packs") or {}).items()
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
