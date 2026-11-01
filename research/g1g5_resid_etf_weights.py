#!/usr/bin/env python3
"""G1G5 resid×ETF X2 weights — industry/size residual Alpha × ETF share-flow.

Mechanism (orthogonal to friction four-arm / expand momentum / lowturn):
  1) Stock trailing return residual vs SW L1 peers (univ) + float_mktcap tercile demean
  2) Industry ETF share-flow (creation/redemption) PIT → constituent inherit
  3) Combine: w_resid * z(resid) + w_etf * z(etf) + w_inter * z(resid)*z(etf)

Forbidden: textbook momentum/value/quality main tokens; CB/gold mainline;
SEAT-SPLIT/UNLOCK arms; stub forward-fill; Yahoo/Reddit.
promotion_approved=false; no orders; no Strategy; no v29 GP.
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
    MID_LARGE_PIT,
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
    score_etf_flow,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_resid_etf_flow_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
RESID_LOOKBACK = 20
W_RESID = 0.55
W_ETF = 0.30
W_INTER = 0.15

WHO_PAYS_ZH = (
    "个股残差×行业ETF申赎份额流："
    "申万一级行业内相对收益残差再经流通市值三分位中性化后的个股定价修正对手盘"
    " + 行业ETF创设/赎回份额流对手盘；"
    "交互项偏好「份额流入行业内的正残差个股」；"
    "明确排除教科书式相对强弱排序、估值排序与质量主线；"
    "相对510300持有窗由上述残差修正与份额流对手盘支付；"
    "非解禁/T+1/涨跌停四臂摩擦包复刻。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _preload_close_matrix(instruments: Sequence[str]) -> pd.DataFrame:
    """Wide close matrix (sessions × instruments); compact vs per-name feature cache."""
    from research.g1g5_x2_panel_stitch import load_equity_closes_x2

    cols: dict[str, pd.Series] = {}
    for inst in instruments:
        ser = load_equity_closes_x2(inst)
        if ser is None or ser.empty:
            continue
        cols[inst] = ser
    if not cols:
        return pd.DataFrame()
    mat = pd.DataFrame(cols).sort_index()
    mat.index = pd.to_datetime(mat.index).tz_localize(None).normalize()
    mat = mat[~mat.index.duplicated(keep="last")]
    return mat


def _load_mktcap_on_sessions(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> dict[str, dict[str, float]]:
    """session → {ts_instrument: float_mktcap_basis} for univ names only."""
    want_pids = {to_panel_id(x): x for x in instruments}
    sess_set = {str(s)[:10] for s in sessions}
    df = pd.read_parquet(
        MID_LARGE_PIT,
        columns=["session", "instrument_id", "float_mktcap_basis"],
    )
    df = df[df["session"].isin(sess_set) & df["instrument_id"].isin(want_pids.keys())]
    out: dict[str, dict[str, float]] = {s: {} for s in sess_set}
    for sess, pid, mc in zip(
        df["session"].astype(str),
        df["instrument_id"].astype(str),
        pd.to_numeric(df["float_mktcap_basis"], errors="coerce"),
    ):
        ts = want_pids.get(pid)
        if ts is None or not np.isfinite(mc):
            continue
        out.setdefault(str(sess)[:10], {})[ts] = float(mc)
    del df
    return out


def trailing_return_at(
    closes: pd.DataFrame,
    instrument: str,
    session: pd.Timestamp,
    lookback: int,
) -> float | None:
    """PIT trailing lookback-session simple return ending AT session (no stub)."""
    if instrument not in closes.columns:
        return None
    ser = closes[instrument].dropna()
    sess = pd.Timestamp(session).normalize()
    hist = ser[ser.index <= sess]
    if len(hist) < lookback + 1:
        return None
    if pd.Timestamp(hist.index[-1]).normalize() != sess:
        return None
    px0, px1 = float(hist.iloc[-(lookback + 1)]), float(hist.iloc[-1])
    if px0 <= 0 or not np.isfinite(px0) or not np.isfinite(px1):
        return None
    return px1 / px0 - 1.0


def score_industry_size_residual(
    session: str,
    instruments: Sequence[str],
    *,
    closes: pd.DataFrame,
    sw: pd.DataFrame,
    mktcaps: dict[str, float],
    lookback: int = RESID_LOOKBACK,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Industry-EW residual then float_mktcap tercile demean → cross-section z."""
    meta: dict[str, Any] = {"arm": "ind_size_resid", "status": "ok", "lookback": lookback}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    raw_ret: dict[str, float] = {}
    inst_sw: dict[str, str] = {}
    for inst in instruments:
        r = trailing_return_at(closes, inst, sess, lookback)
        if r is None:
            continue
        code = sw_code_on(inst, sess, sw)
        if not code:
            continue
        raw_ret[inst] = float(r)
        inst_sw[inst] = code
    meta["n_scored"] = len(raw_ret)
    if len(raw_ret) < max(8, len(instruments) // 5):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计残差名过少 n={len(raw_ret)}"
        return {i: 0.0 for i in instruments}, meta

    # industry EW mean among scored peers
    by_ind: dict[str, list[float]] = {}
    for inst, r in raw_ret.items():
        by_ind.setdefault(inst_sw[inst], []).append(r)
    ind_mean = {k: float(np.mean(v)) for k, v in by_ind.items()}
    ind_resid = {inst: raw_ret[inst] - ind_mean[inst_sw[inst]] for inst in raw_ret}

    # size tercile demean on industry residual (using available mktcaps)
    caps = {i: mktcaps[i] for i in ind_resid if i in mktcaps and mktcaps[i] > 0}
    meta["n_with_mktcap"] = len(caps)
    if len(caps) >= 9:
        cap_ser = pd.Series(caps)
        try:
            terc = pd.qcut(cap_ser.rank(method="first"), 3, labels=[0, 1, 2])
        except ValueError:
            terc = pd.Series(0, index=cap_ser.index)
        bucket_mean: dict[int, float] = {}
        for b in (0, 1, 2):
            members = [i for i in caps if int(terc.loc[i]) == b]
            if members:
                bucket_mean[b] = float(np.mean([ind_resid[i] for i in members]))
        size_resid = {}
        for inst, r in ind_resid.items():
            if inst in caps:
                b = int(terc.loc[inst])
                size_resid[inst] = r - bucket_mean.get(b, 0.0)
            else:
                size_resid[inst] = r
        meta["size_neutral"] = True
    else:
        size_resid = dict(ind_resid)
        meta["size_neutral"] = False
        meta["note_zh"] = "市值覆盖不足；仅行业残差"

    ser = pd.Series({i: float(size_resid.get(i, 0.0)) for i in instruments})
    scored_only = ser[list(raw_ret.keys())]
    mu, sd = float(scored_only.mean()), float(scored_only.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
        z = z.where(ser.index.isin(raw_ret.keys()), 0.0)
    out = {i: float(z.loc[i]) if i in z.index else 0.0 for i in instruments}
    meta["n_industries"] = len(by_ind)
    return out, meta


def combine_resid_etf(
    resid: dict[str, float],
    etf: dict[str, float],
    resid_meta: dict[str, Any],
    etf_meta: dict[str, Any],
    instruments: Sequence[str],
) -> tuple[dict[str, float], dict[str, Any]]:
    """Weighted sum + interaction; drop coverage_gap arms and renormalize linear weights."""
    wr, we, wi = float(W_RESID), float(W_ETF), float(W_INTER)
    if resid_meta.get("status") == "coverage_gap":
        wr = 0.0
        wi = 0.0
    if etf_meta.get("status") == "coverage_gap":
        we = 0.0
        wi = 0.0
    lin = wr + we
    if lin <= 0 and wi <= 0:
        # both gap — equal zero
        return {i: 0.0 for i in instruments}, {
            "arm_weights_effective": {"resid": 0.0, "etf": 0.0, "inter": 0.0},
            "arm_weights_nominal": {"resid": W_RESID, "etf": W_ETF, "inter": W_INTER},
            "status": "coverage_gap",
        }
    # renormalize linear legs if one dropped; keep inter as absolute share of original sum
    if lin > 0 and (wr + we) != (W_RESID + W_ETF):
        # scale remaining linear to fill dropped linear mass (not inter)
        scale = (W_RESID + W_ETF) / lin if lin > 0 else 1.0
        wr *= scale
        we *= scale
    out = {}
    for i in instruments:
        r = float(resid.get(i, 0.0))
        e = float(etf.get(i, 0.0))
        out[i] = wr * r + we * e + wi * (r * e)
    return out, {
        "arm_weights_effective": {"resid": wr, "etf": we, "inter": wi},
        "arm_weights_nominal": {"resid": W_RESID, "etf": W_ETF, "inter": W_INTER},
        "status": "ok",
    }


def build_rebalance_decisions_resid_etf(
    instruments: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    closes: pd.DataFrame,
    active_n: int = DEFAULT_ACTIVE_N,
    lookback: int = RESID_LOOKBACK,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sw = _load_sw_members()
    flow = _load_etf_flow()
    mktcap_by_sess = _load_mktcap_on_sessions(instruments, rebalance_sessions)
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(instruments, rebalance_sessions)

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []

    for sess in rebalance_sessions:
        eligible = list(instruments)
        if use_pit_membership:
            present = mid_large_members_on(sess, instruments, member_index=member_index)
            eligible = [i for i in instruments if i in present]

        resid_s, resid_m = score_industry_size_residual(
            sess,
            eligible,
            closes=closes,
            sw=sw,
            mktcaps=mktcap_by_sess.get(str(sess)[:10], {}),
            lookback=lookback,
        )
        etf_s, etf_m = score_etf_flow(sess, eligible, sw=sw, flow=flow)
        combined, cmeta = combine_resid_etf(resid_s, etf_s, resid_m, etf_m, eligible)
        arm_logs.append(
            {
                "session": sess,
                "arms": {"resid": resid_m, "etf": etf_m},
                "combine": cmeta,
                "n_eligible": len(eligible),
            }
        )

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        # if all zeros (both gap), fall back to equal-weight first active_n eligible
        if ranked and all(abs(v) < 1e-15 for _, v in ranked):
            ranked = [(i, 0.0) for i in eligible[: min(active_n, len(eligible))]]
            cmeta["fallback_ew_eligible"] = True
        active = [i for i, _ in ranked[: min(int(active_n), len(ranked))]]
        active_set = set(active)
        w_active = (1.0 / len(active_set)) if active_set else 0.0
        score_map = dict(combined)

        for inst in instruments:
            if inst in active_set:
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
                    "resid_etf_score": score_map.get(inst),
                    "resid_z": resid_s.get(inst),
                    "etf_z": etf_s.get(inst),
                    "selection_rule": "ind_size_resid_x_etf_flow_topN_ew",
                }
            )

    return decisions, {
        "rebalance_arm_logs": arm_logs,
        "nominal_arm_weights": {"resid": W_RESID, "etf": W_ETF, "inter": W_INTER},
        "resid_lookback": lookback,
    }


def run_resid_etf(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 1,
    lookback: int = RESID_LOOKBACK,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    from research.g1g5_x2_panel_stitch import (
        X2_END,
        clear_caches,
        coverage_report,
        install_equity_close_monkeypatch,
    )

    install_equity_close_monkeypatch()
    out_dir = out_dir or (ROOT / "output" / "ai_factory")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    peak0 = _rss_kb()

    uni = select_mid_large_topn(top_n=top_n)
    instruments = uni["instruments"]
    if len(instruments) < 10:
        raise RuntimeError(f"universe too small: {len(instruments)}")

    closes = _preload_close_matrix(instruments)
    if closes.empty or closes.shape[1] < 10:
        raise RuntimeError(f"close matrix too thin: {closes.shape}")

    rebal = month_end_sessions(weight_start, weight_end)
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    cal0 = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal0):
        first = pd.Timestamp(cal0[0]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + list(rebal)

    decisions, score_meta = build_rebalance_decisions_resid_etf(
        instruments,
        rebal,
        closes=closes,
        active_n=active_n,
        lookback=lookback,
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

    tow = estimate_daily_turnover(weights)

    # overlap vs nontextbook + lowturn (paths under output/intel)
    intel = ROOT / "output" / "intel"
    vs: dict[str, Any] = {}
    for label, fname in (
        ("nontextbook_monthly", "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
    ):
        p = intel / fname
        entry: dict[str, Any] = {"path": str(p.relative_to(ROOT)) if p.exists() else None}
        if p.exists():
            old = pd.read_parquet(p, columns=["date", "instrument", "target_weight"])
            old_tow = estimate_daily_turnover(old)
            entry["old_mean_one_way"] = old_tow.get("mean_one_way")
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
                    }
                )
            entry["active_set_compare_sample"] = diffs
        vs[label] = entry

    wpath = out_dir / f"g1g5_resid_etf_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_resid_etf_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    debates: list[dict[str, Any]] = []
    for inst in list(instruments)[:3]:
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
    daily_sum = weights.groupby("date")["target_weight"].sum()
    peak = _rss_kb()
    cov = coverage_report(list(instruments))
    # free heavy caches before writing meta
    clear_caches()

    meta = {
        "mode": "g1g5_resid_etf_flow",
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
        "active_n": active_n,
        "resid_lookback": lookback,
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "turnover_daily": tow,
        "vs_prior_packs": vs,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
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
            "ind_size_resid": (
                f"个股 trailing {lookback} 交易日收益 − 同申万一级（宇宙内）等权收益 "
                "→ 再按流通市值三分位 demean → 截面 z；非 excess_vs_510300 排序"
            ),
            "etf_share_flow": (
                "行业ETF份额流 PIT（available_at≤session）；trailing 可见 trade_date "
                "flow_est_wan_yuan 行业加总 → 截面z → 成分继承（复用 nontextbook score_etf_flow）"
            ),
            "interaction": "z(resid)×z(etf)：偏好份额流入行业内的正残差个股",
            "selection": f"合成分 top{active_n} 等权；禁 unlock/T+1/limit 四臂；禁 CB/金主",
            "orthogonality_zh": (
                "相对 friction_v1/lowturn：去掉解禁/T+1/涨跌停臂，改残差主轴；"
                "相对 expand：不用 excess_vs_510300 动量排序"
            ),
        },
        "score_meta": score_meta,
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
        "no_v29_gp": True,
        "panel_coverage_x2": cov,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "close_matrix_shape": list(closes.shape),
    }
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }

    meta_path = out_dir / f"g1g5_resid_etf_run_meta_{stamp}.json"
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
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "selection_rule": "ind_size_resid_x_etf_flow_top20_ew",
        "role_zh": "机制正交新权重：个股残差×ETF份额流（研究级）",
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

    ap = argparse.ArgumentParser(description="G1G5 resid×ETF X2 weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--lookback", type=int, default=RESID_LOOKBACK)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_resid_etf(
            top_n=int(args.top_n),
            active_n=int(args.active_n),
            horizon_days=int(args.horizon_days),
            max_debate_rounds=int(args.max_debate_rounds),
            lookback=int(args.lookback),
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
    slim["turnover"] = meta.get("turnover_daily")
    slim["vs_jaccard_head"] = {
        k: [(d.get("session"), d.get("jaccard")) for d in (v.get("active_set_compare_sample") or [])[:3]]
        for k, v in (meta.get("vs_prior_packs") or {}).items()
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
