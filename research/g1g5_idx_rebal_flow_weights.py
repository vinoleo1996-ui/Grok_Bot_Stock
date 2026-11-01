#!/usr/bin/env python3
"""G1G5 index-rebalance flow X2 weights (research-grade, non-momentum).

Orthogonal to six failed packs
(expand / friction / lowturn / resid_etf / etf_core / friction_cost_redesign):
  - Signal: CSI300/CSI500 constituent ADD events (PIT available_at)
  - Hold K=10 trading days after effective_date; trade from next open after avail
  - Long adds only (no short dels); equal-weight top N=25
  - Rank: CSI300 first → float_mktcap capacity → available_at (NOT returns/momentum)
  - Ballast 510300 when n=0 or residual budget
  - NOT textbook mom/value/quality; NOT unlock/seat/share-flow; NOT etf_core 0.70

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
from research.ai_factor_index_rebal_panels import (  # noqa: E402
    ALLOWED_INDEX,
    K_HOLD,
    load_index_rebal_events,
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
    DEFAULT_D0_PANELS,
    MID_LARGE_PIT,
    UNIVERSE_KIND,
    build_daily_weights_expand,
    run_g6_lookahead_proof,
    to_panel_id,
)
from research.g1g5_nontextbook_weights import _forbid_textbook_tokens  # noqa: E402
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_idx_rebal_flow_v1"
UNIVERSE_ID = "g1g5_mid_large_csi_rebal_event"
DEFAULT_TOP_N = 25  # active names in hold window
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
W_PER_NAME = 0.028
W_STOCK_CAP = 0.70
BALLAST_ETF = "510300.SH"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_IDX_REBAL_FLOW_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "指数调仓迁移流："
    "CSI300与CSI500成分调入公告后生效日前后"
    "被动指数跟踪与量化对标的强制再平衡买卖需求"
    "支付相对510300的持有窗；"
    "做多公告已到的调入个股篮；"
    "明确非截面相对强弱排序；"
    "明确非估值或质量主轴；"
    "明确非解禁席位份额流同构；"
    "明确非ETF-core直接持有结构；"
    "明确非摩擦四臂换皮。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _baostock_to_ts(code: str) -> str:
    s = str(code)
    if s.startswith(("sh.", "sz.", "bj.")):
        ex, c = s.split(".", 1)
        return f"{c}.{ex.upper()}"
    return s


def _next_session(cal: pd.DatetimeIndex, day: pd.Timestamp) -> pd.Timestamp | None:
    """First trading session strictly after `day` (normalize)."""
    d = pd.Timestamp(day).normalize()
    # searchsorted left on d+1 calendar day equivalent: sessions > d
    i = int(cal.searchsorted(d + pd.Timedelta(days=1), side="left"))
    if i >= len(cal):
        return None
    return pd.Timestamp(cal[i]).normalize()


def _session_on_or_after(cal: pd.DatetimeIndex, day: pd.Timestamp) -> pd.Timestamp | None:
    d = pd.Timestamp(day).normalize()
    i = int(cal.searchsorted(d, side="left"))
    if i >= len(cal):
        return None
    return pd.Timestamp(cal[i]).normalize()


def _session_plus_k(cal: pd.DatetimeIndex, sess: pd.Timestamp, k: int) -> pd.Timestamp | None:
    """sess itself is day 0; hold through sess+k (inclusive end = index of sess + k)."""
    i = int(cal.searchsorted(pd.Timestamp(sess).normalize(), side="left"))
    if i >= len(cal):
        return None
    j = i + int(k)
    if j >= len(cal):
        return pd.Timestamp(cal[-1]).normalize()
    return pd.Timestamp(cal[j]).normalize()


def _load_mcap_map(instruments: Sequence[str], sessions: Sequence[str]) -> dict[str, dict[str, float]]:
    """session -> {ts_code: float_mktcap_basis} from mid_large PIT (light read)."""
    want_pids = {to_panel_id(x) for x in instruments}
    pid_to_ts = {to_panel_id(x): x for x in instruments}
    sess_set = {str(s)[:10] for s in sessions}
    df = pd.read_parquet(
        MID_LARGE_PIT,
        columns=["session", "instrument_id", "float_mktcap_basis"],
    )
    df = df[df["session"].isin(sess_set) & df["instrument_id"].isin(want_pids)]
    out: dict[str, dict[str, float]] = {}
    for sess, pid, mv in zip(
        df["session"].astype(str),
        df["instrument_id"].astype(str),
        df["float_mktcap_basis"].astype(float),
    ):
        ts = pid_to_ts.get(pid)
        if ts is None:
            continue
        out.setdefault(sess, {})[ts] = float(mv)
    del df
    return out


def _build_event_windows(
    *,
    cal: pd.DatetimeIndex,
    weight_start: str,
    weight_end: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build per-add hold windows with PIT trade_start / hold_end."""
    ev = load_index_rebal_events(require_avail=True, index_codes=ALLOWED_INDEX)
    if ev.empty:
        raise RuntimeError("index_member_events empty after PIT filter")
    adds = ev[ev["event"] == "in"].copy()
    adds["ts"] = adds["instrument"].map(_baostock_to_ts)
    adds["pid"] = adds["ts"].map(to_panel_id)

    s0 = pd.Timestamp(str(weight_start)[:10])
    s1 = pd.Timestamp(str(weight_end)[:10])
    # keep events whose hold could intersect [s0, s1]
    windows: list[dict[str, Any]] = []
    skipped_no_panel = 0
    skipped_no_cal = 0
    for row in adds.itertuples(index=False):
        ts = str(row.ts)
        pid = str(row.pid)
        if not (DEFAULT_D0_PANELS / f"{pid}.parquet").exists():
            skipped_no_panel += 1
            continue
        avail = pd.Timestamp(row.avail_date).normalize()
        eff = pd.Timestamp(row.effective_date).normalize()
        if pd.isna(avail) or pd.isna(eff):
            continue
        trade_start = _next_session(cal, avail)
        eff_sess = _session_on_or_after(cal, eff)
        if trade_start is None or eff_sess is None:
            skipped_no_cal += 1
            continue
        hold_end = _session_plus_k(cal, eff_sess, K_HOLD)
        if hold_end is None:
            skipped_no_cal += 1
            continue
        # drop windows entirely outside weight calendar
        if hold_end < s0 or trade_start > s1:
            continue
        windows.append(
            {
                "instrument": ts,
                "index_code": str(row.index_code),
                "avail_date": avail.strftime("%Y-%m-%d"),
                "effective_date": eff.strftime("%Y-%m-%d"),
                "trade_start": trade_start.strftime("%Y-%m-%d"),
                "hold_end": hold_end.strftime("%Y-%m-%d"),
                "eff_sess": eff_sess.strftime("%Y-%m-%d"),
                "csi300": 1 if str(row.index_code) == "000300.SH" else 0,
                "review": getattr(row, "review", None),
            }
        )

    meta = {
        "n_add_events_raw": int(len(adds)),
        "n_windows": len(windows),
        "skipped_no_panel": skipped_no_panel,
        "skipped_no_cal": skipped_no_cal,
        "k_hold": K_HOLD,
        "allowed_index": list(ALLOWED_INDEX),
        "unique_instruments": sorted({w["instrument"] for w in windows}),
    }
    return windows, meta


def _active_on(
    windows: list[dict[str, Any]],
    session: str,
) -> list[dict[str, Any]]:
    return [w for w in windows if w["trade_start"] <= session <= w["hold_end"]]


def _select_topn(
    active: list[dict[str, Any]],
    *,
    mcap: dict[str, float],
    n: int,
) -> list[str]:
    """Rank: CSI300 first, then float mcap desc, then earlier avail, then code."""
    # dedupe instrument: keep best rank row
    best: dict[str, dict[str, Any]] = {}
    for w in active:
        inst = w["instrument"]
        prev = best.get(inst)
        if prev is None or (w["csi300"], mcap.get(inst, 0.0), w["avail_date"]) > (
            prev["csi300"],
            mcap.get(prev["instrument"], 0.0),
            prev["avail_date"],
        ):
            # Actually for CSI300 we want higher first; for avail earlier is better (smaller)
            best[inst] = w
    ranked = sorted(
        best.values(),
        key=lambda w: (
            -int(w["csi300"]),
            -float(mcap.get(w["instrument"], 0.0)),
            w["avail_date"],
            w["instrument"],
        ),
    )
    return [w["instrument"] for w in ranked[: max(1, int(n))]] if ranked else []


def build_rebalance_decisions_idx_rebal(
    *,
    weight_start: str,
    weight_end: str,
    active_n: int = DEFAULT_TOP_N,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    bench = _load_benchmark_closes("510300")
    s = pd.Timestamp(str(weight_start)[:10])
    e = pd.Timestamp(str(weight_end)[:10])
    # extend cal a bit past end for hold_end mapping of late 2026 events
    cal_full = bench.index[bench.index >= (s - pd.Timedelta(days=40))]
    if len(cal_full) == 0:
        raise RuntimeError("empty 510300 calendar")
    cal = bench.index[(bench.index >= s) & (bench.index <= e)]
    if len(cal) == 0:
        raise RuntimeError("empty weight calendar")

    windows, win_meta = _build_event_windows(
        cal=cal_full, weight_start=weight_start, weight_end=weight_end
    )
    instruments = sorted(set(win_meta["unique_instruments"]) | {BALLAST_ETF})

    # mcap lookup sessions = unique trade_starts + first day (light)
    mcap_sess = sorted({w["trade_start"] for w in windows} | {pd.Timestamp(cal[0]).strftime("%Y-%m-%d")})
    mcap_by = _load_mcap_map([i for i in instruments if i != BALLAST_ETF], mcap_sess)

    # change-point sessions: first day + all trade_starts/hold_end+1 in range
    change: set[str] = {pd.Timestamp(cal[0]).strftime("%Y-%m-%d")}
    cal_set = {pd.Timestamp(x).strftime("%Y-%m-%d") for x in cal}
    cal_list = [pd.Timestamp(x).strftime("%Y-%m-%d") for x in cal]
    cal_index = {d: i for i, d in enumerate(cal_list)}
    for w in windows:
        if w["trade_start"] in cal_set:
            change.add(w["trade_start"])
        # day after hold_end → basket shrinks
        he = w["hold_end"]
        if he in cal_index:
            ni = cal_index[he] + 1
            if ni < len(cal_list):
                change.add(cal_list[ni])
    change_sessions = sorted(change)

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    prev_target: dict[str, float] | None = None

    for sess in change_sessions:
        active = _active_on(windows, sess)
        # nearest mcap session <= sess
        mcap_sess_use = None
        for ms in reversed(mcap_sess):
            if ms <= sess:
                mcap_sess_use = ms
                break
        mcap = mcap_by.get(mcap_sess_use or "", {})
        chosen = _select_topn(active, mcap=mcap, n=active_n)
        n = len(chosen)
        if n == 0:
            target = {BALLAST_ETF: 1.0}
        else:
            w_stock = min(W_STOCK_CAP, W_PER_NAME * n)
            each = w_stock / n
            target = {inst: each for inst in chosen}
            target[BALLAST_ETF] = max(0.0, 1.0 - w_stock)
        # normalize
        ssum = sum(target.values())
        if ssum > 0 and abs(ssum - 1.0) > 1e-9:
            target = {k: v / ssum for k, v in target.items()}

        if prev_target is not None and target == prev_target:
            continue

        arm_logs.append(
            {
                "session": sess,
                "n_active_windows": len(active),
                "n_unique_active": len({a["instrument"] for a in active}),
                "n_selected": n,
                "selected": chosen,
                "w_stock": float(sum(v for k, v in target.items() if k != BALLAST_ETF)),
                "ballast_w": float(target.get(BALLAST_ETF, 0.0)),
                "mcap_session": mcap_sess_use,
                "selection_rule": "idx_rebal_add_topN_ew_csi300_mcap",
            }
        )
        # Sparse emit: ballast + current positives + prior positives zeroed (forward-fill clear)
        emit_set = set(target.keys()) | {BALLAST_ETF}
        if prev_target is not None:
            emit_set |= {k for k, v in prev_target.items() if float(v) > 1e-15}
        for inst in sorted(emit_set):
            w = float(target.get(inst, 0.0))
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": "Overweight" if w > 1e-15 else "Underweight",
                    "target_weight_override": w,
                    "selection_rule": "idx_rebal_add_topN_ew_csi300_mcap",
                    "leg": "ballast" if inst == BALLAST_ETF else "idx_add",
                }
            )
        prev_target = dict(target)

    meta = {
        "windows_meta": win_meta,
        "n_change_sessions": len(arm_logs),
        "change_sessions": [x["session"] for x in arm_logs],
        "rebalance_arm_logs": arm_logs,
        "active_n": active_n,
        "w_per_name": W_PER_NAME,
        "w_stock_cap": W_STOCK_CAP,
        "k_hold": K_HOLD,
        "ballast_etf": BALLAST_ETF,
        "instruments": instruments,
        "universe_note_zh": (
            "调入事件名∩mid_large PIT∩D0 panel；"
            "非 expand mid_large top50 扁平篮（top50∩调入≈0）"
        ),
    }
    return decisions, meta, instruments


def run_idx_rebal_flow(
    *,
    active_n: int = DEFAULT_TOP_N,
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

    decisions, score_meta, instruments = build_rebalance_decisions_idx_rebal(
        weight_start=weight_start,
        weight_end=weight_end,
        active_n=active_n,
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

    stock_set = {i for i in instruments if i != BALLAST_ETF}
    pos = weights[weights["target_weight"] > 1e-15].copy()
    is_ballast = pos["instrument"] == BALLAST_ETF
    is_stock = pos["instrument"].isin(stock_set) & ~is_ballast
    all_dates = weights["date"].drop_duplicates()
    ballast_share = pos.loc[is_ballast].groupby("date")["target_weight"].sum()
    stock_share = pos.loc[is_stock].groupby("date")["target_weight"].sum()
    mean_ballast = float(ballast_share.reindex(all_dates).fillna(0.0).mean())
    mean_stock = float(stock_share.reindex(all_dates).fillna(0.0).mean())
    max_stock_w = float(pos.loc[is_stock, "target_weight"].max()) if is_stock.any() else 0.0

    # days with active stock sleeve
    stock_days = stock_share[stock_share > 1e-9]
    mean_ballast_active = (
        float(ballast_share.reindex(stock_days.index).fillna(0.0).mean())
        if len(stock_days)
        else None
    )
    n_stock_days = int(len(stock_days))
    n_all_days = int(len(all_dates))

    # Export sparse positives only (Book-Smoke filters |w|>0; cuts peak on downstream)
    weights_export = weights.loc[weights["target_weight"] > 1e-15].copy()
    # re-validate gross on sparse+implied: groupby sum must still be ~1
    sparse_sum = weights_export.groupby("date")["target_weight"].sum()
    if float(sparse_sum.min()) < 0.99 or float(sparse_sum.max()) > 1.01:
        raise RuntimeError(
            f"sparse daily_gross out of band: min={sparse_sum.min()} max={sparse_sum.max()}"
        )

    tow = estimate_daily_turnover(weights_export)

    factory = ROOT / "output" / "ai_factory"
    intel = ROOT / "output" / "intel"
    vs: dict[str, Any] = {}
    for label, path in (
        ("expand", intel / "g1g5_expand_daily_weights_20261012_111354.parquet"),
        ("friction_monthly", intel / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", intel / "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
        ("resid_etf", factory / "g1g5_resid_etf_daily_weights_20261013_002418.parquet"),
        ("etf_core", factory / "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet"),
        (
            "friction_cost",
            factory / "g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet",
        ),
    ):
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            entry["old_mean_one_way"] = estimate_daily_turnover(old).get("mean_one_way")
            entry["new_mean_one_way"] = tow.get("mean_one_way")
            # sample change sessions with stock
            sample = [
                x["session"]
                for x in (score_meta.get("rebalance_arm_logs") or [])
                if x.get("n_selected", 0) > 0
            ][:8]
            diffs = []
            for ss in sample:
                a = set(
                    weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"]
                )
                a_stk = {x for x in a if x in stock_set}
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                # approximate stock set for old: exclude known ETF suffix patterns in factory
                known_etf = {BALLAST_ETF, "510300.SH", "510500.SH", "159915.SZ", "512480.SH"}
                b_stk = {x for x in b if x not in known_etf and not str(x).startswith("51")}
                # better: only compare if old instruments look like stocks
                b_stk = {x for x in b if str(x)[:2].isdigit() or (len(str(x)) >= 9 and str(x)[0].isdigit())}
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
        vs[label] = entry

    wpath = out_dir / f"g1g5_idx_rebal_flow_daily_weights_{stamp}.parquet"
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
    weights_export[export_cols].to_parquet(wpath, index=False)

    ledger_path = out_dir / f"debate_ledger_g1g5_idx_rebal_flow_{stamp}.jsonl"
    ledger = JsonlDebateLedger(ledger_path)
    g6_proof = run_g6_lookahead_proof(ledger)

    debates: list[dict[str, Any]] = []
    sample_insts = [BALLAST_ETF] + [x for x in instruments if x in stock_set][:2]
    for inst in sample_insts:
        for sess in ["2024-06-18", "2025-06-17", "2026-06-16"]:
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
        "ballast_w": float(
            last_pos.loc[last_pos["instrument"] == BALLAST_ETF, "target_weight"].sum()
        ),
        "n_stocks": int(last_pos.loc[last_pos["instrument"].isin(stock_set)].shape[0]),
        "stock_w_sum": float(
            last_pos.loc[last_pos["instrument"].isin(stock_set), "target_weight"].sum()
        ),
        "stock_head": (
            last_pos.loc[last_pos["instrument"].isin(stock_set)]
            .sort_values("target_weight", ascending=False)
            .head(8)[["instrument", "target_weight"]]
            .values.tolist()
        ),
    }

    mean_active = float(pos.groupby("date")["instrument"].nunique().mean()) if len(pos) else 0.0

    meta = {
        "mode": "g1g5_idx_rebal_flow",
        "ledger_path": str(ledger_path.relative_to(ROOT)),
        "weights_path": str(wpath.relative_to(ROOT)),
        "weights_rows": int(len(weights_export)),
        "weights_rows_dense_internal": int(len(weights)),
        "weights_n_distinct_sessions": n_sess,
        "weights_date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "n_instruments": int(weights_export["instrument"].nunique()),
        "n_instruments_ever_in_decisions": int(weights["instrument"].nunique()),
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "n_change_sessions": score_meta.get("n_change_sessions"),
        "change_sessions": score_meta.get("change_sessions"),
        "cadence": f"event_driven_idx_rebal_K{K_HOLD}",
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "mean_ballast_share_on_stock_days": mean_ballast_active,
        "n_stock_active_days": n_stock_days,
        "n_calendar_days": n_all_days,
        "stock_active_day_frac": float(n_stock_days / n_all_days) if n_all_days else 0.0,
        "max_stock_weight_observed": max_stock_w,
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
        "universe_note_zh": score_meta.get("universe_note_zh"),
        "mechanism_definition_zh": {
            "signal": "CSI300/CSI500 event=in；PIT available_at→下一开盘；K=10 after effective",
            "portfolio": f"topN={active_n} EW；w_stock=min({W_STOCK_CAP},{W_PER_NAME}*n)；余510300",
            "rank": "CSI300优先→float_mktcap容量→available_at；非收益/动量",
            "orthogonality_zh": (
                "相对六败：事件调入强制流，非动量/四臂/解禁份额/ETF0.70/半月摩擦再设计"
            ),
        },
        "windows_meta": score_meta.get("windows_meta"),
        "active_n": active_n,
        "k_hold": K_HOLD,
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
        "no_friction_four_arm_reskin": True,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
    }
    if not meta["reaches_x2_end"]:
        meta["coverage_gap"] = {
            "requested_end": str(weight_end),
            "actual_end": str(weights["date"].max()),
            "note_zh": "日历未到 X2 末日；已按可算区间截断，禁 stub 前推。",
        }

    slim_logs = []
    for log in score_meta.get("rebalance_arm_logs") or []:
        slim_logs.append({k: v for k, v in log.items() if k != "selected" or True})
        # keep selected but cap length in slim
        if "selected" in slim_logs[-1] and isinstance(slim_logs[-1]["selected"], list):
            slim_logs[-1]["selected_head"] = slim_logs[-1]["selected"][:8]
            slim_logs[-1]["selected_n"] = len(slim_logs[-1].pop("selected"))
    meta["rebalance_arm_logs_slim"] = slim_logs

    meta_path = out_dir / f"g1g5_idx_rebal_flow_run_meta_{stamp}.json"
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
        "universe_note_zh": score_meta.get("universe_note_zh"),
        "n_rows": int(len(weights_export)),
        "n_distinct_sessions": n_sess,
        "n_instruments": int(weights_export["instrument"].nunique()),
        "date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "stub_window": bool(n_sess <= 10),
        "stub_forward_fill": False,
        "reaches_x2_end": meta["reaches_x2_end"],
        "x2_end_target": X2_END,
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "mean_ballast_share_on_stock_days": mean_ballast_active,
        "n_stock_active_days": n_stock_days,
        "stock_active_day_frac": meta["stock_active_day_frac"],
        "max_stock_weight_observed": max_stock_w,
        "cadence": meta["cadence"],
        "k_hold": K_HOLD,
        "active_n": active_n,
        "turnover_daily_mean_one_way": tow.get("mean_one_way"),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "not_hard_gates_candidate": True,
        "no_orders": True,
        "no_strategy_submit": True,
        "no_gp": True,
        "no_etf_core_overlay": True,
        "selection_rule": "idx_rebal_add_topN_ew_csi300_mcap",
        "role_zh": "机制正交新权重：指数调仓迁移流（研究级·非动量）",
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

    ap = argparse.ArgumentParser(description="G1G5 index-rebalance flow X2 weights")
    ap.add_argument("--active-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_idx_rebal_flow(
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
            "rebalance_arm_logs_slim",
            "change_sessions",
            "vs_prior_packs",
        )
    }
    slim["debates_n"] = meta.get("debates_n")
    slim["g6"] = (meta.get("g6_proof") or {}).get("G6")
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
    slim["n_change_sessions"] = meta.get("n_change_sessions")
    slim["windows_n"] = (meta.get("windows_meta") or {}).get("n_windows")
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
