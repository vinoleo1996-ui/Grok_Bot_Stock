#!/usr/bin/env python3
"""G1G5 northbound hold-change flow X2 weights (research-grade).

Mechanism (orthogonal to nine failed packs):
  - Primary: PIT Δratio of northbound hk_hold (增持侧)
  - Gap-fill after hk_hold asof stall: margin Δrzye (融资余额上升侧)
  - Select topN EW with SW L1 industry hard cap ≤30%; ballast 510300
  - NOT OCF, NOT valuation residual, NOT momentum sort, NOT idx-rebal,
    NOT resid×share-flow, NOT friction/etf_core

promotion_approved=false; no orders; no Strategy; no GP; no stub forward-fill.
"""
from __future__ import annotations

import gc
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
)
from research.g1g5_x2_panel_stitch import clear_caches as clear_x2_caches  # noqa: E402
from research.g1g5_nontextbook_weights import (  # noqa: E402
    _forbid_textbook_tokens,
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_northbound_flow_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_SCORE_N = 50
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
X2_END = "2026-10-09"

STOCK_BUDGET = 0.80
BALLAST_FRAC = 0.20
BALLAST_ETF = "510300.SH"
IND_CAP = 0.30
LOOKBACK_DAYS = 20
HK_STALE_DAYS = 45  # switch to margin if last hk asof older than this

HK_HOLD = ROOT / "data" / "v2" / "northbound" / "hk_hold_ashare_daily_2018plus.parquet"
MARGIN_DETAIL = ROOT / "data" / "v2" / "margin" / "margin_detail_daily_2018plus.parquet"
MONEYFLOW_HSGT = ROOT / "data" / "v2" / "northbound" / "moneyflow_hsgt_daily_2018plus.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_NORTHBOUND_FLOW_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "北向配置流："
    "沪深港通北向对个股的边际增持与持股占比上升由境外配置与被动跟踪资金"
    "支付相对510300的持有窗；"
    "本叶吃持股变化与流入的对手盘；"
    "hk_hold断档后再平衡日以两融融资余额变化作同族补窗；"
    "明确非相对强弱截面排序、非估值残差、非OCF、非调仓事件、非份额流乘残差、非ETF-core直接持有。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def select_mid_large_topn_light(
    *,
    top_n: int = DEFAULT_SCORE_N,
    anchor: str = "2024-06-28",
) -> dict[str, Any]:
    import pyarrow.compute as pc
    import pyarrow.dataset as ds
    import pyarrow.parquet as pq

    from research.ai_debate_memory_runner import DEFAULT_D0_PANELS
    from research.g1g5_expand_g6 import MID_LARGE_PIT, panel_id_to_ts

    anchor_s = str(anchor)[:10]
    try:
        dataset = ds.dataset(str(MID_LARGE_PIT), format="parquet")
        table = dataset.to_table(
            columns=["session", "instrument_id", "float_mktcap_basis", "universe_id"],
            filter=ds.field("session") == anchor_s,
        )
        sub = table.to_pandas()
        del table
    except Exception:
        pf = pq.ParquetFile(str(MID_LARGE_PIT))
        parts = []
        for i in range(pf.metadata.num_row_groups):
            t = pf.read_row_group(
                i, columns=["session", "instrument_id", "float_mktcap_basis", "universe_id"]
            )
            t = t.filter(pc.equal(t.column("session"), anchor_s))
            if t.num_rows:
                parts.append(t.to_pandas())
            del t
        sub = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if sub.empty:
        raise RuntimeError(f"mid_large empty at anchor {anchor_s}")
    sub = sub.sort_values("float_mktcap_basis", ascending=False)
    selected: list[str] = []
    skipped_no_panel: list[str] = []
    mcaps: dict[str, float] = {}
    panels_dir = DEFAULT_D0_PANELS
    for _, row in sub.iterrows():
        pid = str(row["instrument_id"])
        path = panels_dir / f"{pid}.parquet"
        ts = panel_id_to_ts(pid)
        if not path.exists():
            skipped_no_panel.append(ts)
            continue
        selected.append(ts)
        mcaps[ts] = float(row["float_mktcap_basis"])
        if len(selected) >= int(top_n):
            break
    del sub
    gc.collect()
    return {
        "instruments": selected,
        "n": len(selected),
        "anchor_session": anchor_s,
        "source_pit": str(MID_LARGE_PIT.relative_to(ROOT)),
        "source_universe_id": "mid_large",
        "rule_zh": (
            f"Data mid_large_members_pit @ {anchor_s} 按 float_mktcap_basis 降序；"
            f"保留有 D0 panel 的前 {top_n}；轻量 session 过滤读。"
        ),
        "mcaps_head": {k: mcaps[k] for k in selected[:5]},
        "skipped_no_panel_n": len(skipped_no_panel),
        "promotion_approved": False,
        "light_loader": True,
    }


def load_pit_member_index_light(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> dict[str, set[str]]:
    import pyarrow.dataset as ds

    from research.g1g5_expand_g6 import MID_LARGE_PIT

    want_pids = {to_panel_id(x): x for x in instruments}
    sess_list = sorted({str(s)[:10] for s in sessions})
    sess_set = set(sess_list)
    dataset = ds.dataset(str(MID_LARGE_PIT), format="parquet")
    table = dataset.to_table(
        columns=["session", "instrument_id"],
        filter=ds.field("session").isin(sess_list)
        & ds.field("instrument_id").isin(list(want_pids.keys())),
    )
    df = table.to_pandas()
    del table
    out: dict[str, set[str]] = {s: set() for s in sess_set}
    for sess, pid in zip(df["session"].astype(str), df["instrument_id"].astype(str)):
        ts = want_pids.get(pid)
        if ts:
            out.setdefault(str(sess)[:10], set()).add(ts)
    del df
    gc.collect()
    return out


def _load_hk_hold(instruments: Sequence[str]) -> pd.DataFrame:
    if not HK_HOLD.exists():
        raise RuntimeError(f"missing hk_hold: {HK_HOLD}")
    want = set(instruments)
    df = pd.read_parquet(
        HK_HOLD, columns=["trade_date", "ts_code", "vol", "ratio", "available_at"]
    )
    df = df[df["ts_code"].isin(want)].copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["ratio"] = pd.to_numeric(df["ratio"], errors="coerce")
    df["vol"] = pd.to_numeric(df["vol"], errors="coerce")
    df = df[df["available_at"].notna()].sort_values(["ts_code", "available_at"])
    gc.collect()
    return df.reset_index(drop=True)


def _load_margin_detail(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Chunked margin load for universe × window (peak-safe)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if not MARGIN_DETAIL.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    want_set = set(want)
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=60)
    s1 = pd.Timestamp(max(sessions)[:10]) + pd.Timedelta(days=1)
    cols = ["trade_date", "ts_code", "rzye", "available_at"]
    pf = pq.ParquetFile(str(MARGIN_DETAIL))
    want_arr = pa.array(want, type=pa.string())
    chunks: list[pd.DataFrame] = []
    for i in range(pf.metadata.num_row_groups):
        rg = pf.metadata.row_group(i)
        td_stats = None
        for j in range(rg.num_columns):
            col = rg.column(j)
            if col.path_in_schema == "trade_date" and col.statistics and col.statistics.has_min_max:
                try:
                    td_stats = (pd.Timestamp(str(col.statistics.min)), pd.Timestamp(str(col.statistics.max)))
                except Exception:
                    td_stats = None
                break
        if td_stats is not None:
            # trade_date may be string YYYYMMDD
            try:
                if td_stats[1] < s0 or td_stats[0] > s1:
                    continue
            except Exception:
                pass
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
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["rzye"] = pd.to_numeric(df["rzye"], errors="coerce")
    df = df[df["available_at"].notna()].sort_values(["ts_code", "available_at"])
    gc.collect()
    return df.reset_index(drop=True)


def _market_north_money_on(session: str) -> float | None:
    """Optional market-level north_money asof (log only)."""
    if not MONEYFLOW_HSGT.exists():
        return None
    try:
        df = pd.read_parquet(MONEYFLOW_HSGT, columns=["trade_date", "north_money", "available_at"])
        df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
        sess = pd.Timestamp(str(session)[:10]).normalize()
        sub = df[df["available_at"].dt.normalize() <= sess]
        if sub.empty:
            return None
        return float(sub.sort_values("available_at").iloc[-1]["north_money"])
    except Exception:
        return None


def score_northbound_delta(
    session: str,
    instruments: Sequence[str],
    hk: pd.DataFrame,
    *,
    lookback_days: int = LOOKBACK_DAYS,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Δratio asof session; prefer ~lookback_days apart, else last two snapshots."""
    meta: dict[str, Any] = {"arm": "northbound_delta_ratio", "source": "hk_hold", "status": "ok"}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    if hk is None or hk.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "hk_hold empty"
        return {}, meta

    sub = hk[hk["available_at"].dt.normalize() <= sess]
    if sub.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "no hk_hold asof"
        return {}, meta

    last_obs = sub["available_at"].max()
    meta["last_hk_available_at"] = str(last_obs)
    meta["hk_staleness_days"] = int((sess - pd.Timestamp(last_obs).normalize()).days)

    target = sess - pd.Timedelta(days=int(lookback_days))
    scores: dict[str, float] = {}
    n_pair = 0
    for code, g in sub.groupby("ts_code", sort=False):
        if code not in instruments:
            continue
        g = g.sort_values("available_at")
        if len(g) < 2:
            continue
        cur = g.iloc[-1]
        # prefer snapshot near target
        earlier = g[g["available_at"].dt.normalize() <= target]
        if not earlier.empty:
            base = earlier.iloc[-1]
        else:
            base = g.iloc[-2]
        r1 = float(cur["ratio"]) if np.isfinite(cur["ratio"]) else np.nan
        r0 = float(base["ratio"]) if np.isfinite(base["ratio"]) else np.nan
        if not (np.isfinite(r1) and np.isfinite(r0)):
            # fallback vol change
            v1 = float(cur["vol"]) if np.isfinite(cur["vol"]) else np.nan
            v0 = float(base["vol"]) if np.isfinite(base["vol"]) else np.nan
            if not (np.isfinite(v1) and np.isfinite(v0) and v0 > 0):
                continue
            delta = (v1 / v0) - 1.0
        else:
            delta = r1 - r0
        if not np.isfinite(delta):
            continue
        scores[str(code)] = float(delta)
        n_pair += 1

    meta["n_scored"] = n_pair
    if n_pair < max(8, len(instruments) // 6):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计Δratio名过少 n={n_pair}"
        return scores, meta
    return scores, meta


def score_margin_delta(
    session: str,
    instruments: Sequence[str],
    margin: pd.DataFrame,
    *,
    lookback_days: int = LOOKBACK_DAYS,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Δrzye / lag_rzye asof; financing balance growth."""
    meta: dict[str, Any] = {"arm": "margin_delta_rzye", "source": "margin_fallback", "status": "ok"}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    if margin is None or margin.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "margin empty"
        return {}, meta
    sub = margin[margin["available_at"].dt.normalize() <= sess]
    if sub.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "no margin asof"
        return {}, meta

    target = sess - pd.Timedelta(days=int(lookback_days))
    scores: dict[str, float] = {}
    n_pair = 0
    for code, g in sub.groupby("ts_code", sort=False):
        if code not in instruments:
            continue
        g = g.sort_values("available_at")
        if len(g) < 2:
            continue
        cur = g.iloc[-1]
        earlier = g[g["available_at"].dt.normalize() <= target]
        base = earlier.iloc[-1] if not earlier.empty else g.iloc[-2]
        y1 = float(cur["rzye"]) if np.isfinite(cur["rzye"]) else np.nan
        y0 = float(base["rzye"]) if np.isfinite(base["rzye"]) else np.nan
        if not (np.isfinite(y1) and np.isfinite(y0)):
            continue
        denom = max(abs(y0), 1.0)
        delta = (y1 - y0) / denom
        if not np.isfinite(delta):
            continue
        scores[str(code)] = float(delta)
        n_pair += 1
    meta["n_scored"] = n_pair
    if n_pair < max(8, len(instruments) // 6):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计Δrzye名过少 n={n_pair}"
        return scores, meta
    return scores, meta


def select_with_industry_cap(
    ranked: list[tuple[str, float]],
    *,
    sw: pd.DataFrame,
    session: str,
    active_n: int,
    ind_cap: float,
    budget: float,
) -> tuple[dict[str, float], dict[str, Any]]:
    sess = pd.Timestamp(str(session)[:10]).normalize()
    w_each = float(budget) / float(max(1, active_n))
    max_n_ind = max(1, int(np.floor(ind_cap / max(w_each, 1e-12) + 1e-12)))
    picked: list[str] = []
    ind_count: dict[str, int] = {}
    skipped_cap: list[str] = []
    for inst, _sc in ranked:
        code = sw_code_on(inst, sess, sw) or "_UNK"
        if ind_count.get(code, 0) >= max_n_ind:
            skipped_cap.append(inst)
            continue
        picked.append(inst)
        ind_count[code] = ind_count.get(code, 0) + 1
        if len(picked) >= active_n:
            break
    meta = {
        "n_picked": len(picked),
        "ind_counts": dict(ind_count),
        "max_n_per_ind": max_n_ind,
        "w_each": w_each,
        "n_skipped_ind_cap": len(skipped_cap),
        "skipped_head": skipped_cap[:8],
    }
    if not picked:
        return {}, meta
    ind_w: dict[str, float] = {}
    for inst in picked:
        code = sw_code_on(inst, sess, sw) or "_UNK"
        ind_w[code] = ind_w.get(code, 0.0) + w_each
    meta["ind_weights"] = ind_w
    meta["max_ind_weight"] = float(max(ind_w.values())) if ind_w else 0.0
    return {inst: w_each for inst in picked}, meta


def build_rebalance_decisions_northbound(
    stock_universe: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    _forbid_textbook_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
    if "动量" in WHO_PAYS_ZH:
        raise RuntimeError("who_pays_zh must not contain 动量")

    sw = _load_sw_members()
    member_index = None
    if use_pit_membership:
        member_index = load_pit_member_index_light(stock_universe, rebalance_sessions)

    hk = _load_hk_hold(stock_universe)
    score_meta: dict[str, Any] = {
        "rebalance_arm_logs": [],
        "hk_rows": int(len(hk)),
        "hk_path": str(HK_HOLD.relative_to(ROOT)),
        "hk_date_span": (
            [str(hk["trade_date"].min())[:10], str(hk["trade_date"].max())[:10]]
            if len(hk)
            else None
        ),
        "peak_rss_mb_after_hk": round(_rss_kb() / 1024.0, 1),
    }

    # Preload margin only if we will need gap-fill (sessions past hk + stale buffer)
    need_margin = True  # always prepare for post-2025-06 gap
    margin = pd.DataFrame()
    if need_margin:
        margin = _load_margin_detail(stock_universe, rebalance_sessions)
    score_meta["margin_rows"] = int(len(margin))
    score_meta["margin_path"] = str(MARGIN_DETAIL.relative_to(ROOT))
    score_meta["peak_rss_mb_after_margin"] = round(_rss_kb() / 1024.0, 1)

    decisions: list[dict[str, Any]] = []
    all_instruments = set(stock_universe) | {BALLAST_ETF}
    n_hk_sess = 0
    n_margin_sess = 0

    for sess in rebalance_sessions:
        present = (
            mid_large_members_on(sess, stock_universe, member_index=member_index)
            if use_pit_membership
            else set(stock_universe)
        )
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

        scores_hk, meta_hk = score_northbound_delta(sess, list(present), hk)
        use_margin = False
        if meta_hk.get("status") != "ok" or int(meta_hk.get("hk_staleness_days") or 0) > HK_STALE_DAYS:
            use_margin = True
        if use_margin:
            scores, arm_meta = score_margin_delta(sess, list(present), margin)
            n_margin_sess += 1
        else:
            scores, arm_meta = scores_hk, meta_hk
            n_hk_sess += 1

        arm_meta["market_north_money"] = _market_north_money_on(sess)

        # prefer positive Δ (增持 / 融资余额上升)
        ranked = sorted(
            ((i, scores[i]) for i in present if i in scores),
            key=lambda x: x[1],
            reverse=True,
        )
        pos = [(i, s) for i, s in ranked if s > 0]
        if len(pos) >= max(5, active_n // 2):
            ranked_use = pos
        else:
            ranked_use = ranked

        target, cap_meta = select_with_industry_cap(
            ranked_use,
            sw=sw,
            session=sess,
            active_n=active_n,
            ind_cap=IND_CAP,
            budget=STOCK_BUDGET,
        )
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
                "cap": {k: v for k, v in cap_meta.items() if k != "ind_weights"},
                "max_ind_weight": cap_meta.get("max_ind_weight"),
                "n_target": len(target),
                "stock_w_sum": stock_w_sum,
                "ballast_w": ballast_w,
                "top_head": [(i, round(scores.get(i, 0.0), 6)) for i, _ in ranked_use[:8]],
            }
        )
        if cap_meta.get("max_ind_weight", 0) > IND_CAP + 1e-6:
            raise RuntimeError(
                f"industry cap breached @ {sess}: {cap_meta.get('max_ind_weight')}"
            )

    del hk
    del margin
    gc.collect()
    score_meta["n_sessions_hk"] = n_hk_sess
    score_meta["n_sessions_margin_fallback"] = n_margin_sess
    score_meta["peak_rss_mb_after_score"] = round(_rss_kb() / 1024.0, 1)
    return decisions, score_meta, sorted(all_instruments)


def run_northbound_flow(
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
    out_dir = out_dir or (ROOT / "output" / "ai_factory")
    out_dir.mkdir(parents=True, exist_ok=True)

    uni = select_mid_large_topn_light(top_n=score_n)
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
        last = pd.Timestamp(cal0[-1]).strftime("%Y-%m-%d")
        if not rebal or rebal[0] != first:
            rebal = [first] + [x for x in rebal if x != first]
        if last not in rebal:
            rebal = list(rebal) + [last]

    decisions, score_meta, instruments = build_rebalance_decisions_northbound(
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
    is_ballast = pos["instrument"] == BALLAST_ETF
    is_stock = pos["instrument"].isin(stock_set) & ~is_ballast
    ballast_share = pos.loc[is_ballast].groupby("date")["target_weight"].sum()
    stock_share = pos.loc[is_stock].groupby("date")["target_weight"].sum()
    all_dates = weights["date"].drop_duplicates()
    mean_ballast = float(ballast_share.reindex(all_dates).fillna(0.0).mean())
    mean_stock = float(stock_share.reindex(all_dates).fillna(0.0).mean())
    if mean_ballast > 0.40 + 1e-9:
        raise RuntimeError(f"ballast share too high (etf_core drift): {mean_ballast:.3f}")

    sw = _load_sw_members()
    ind_breach = []
    for sess in rebal[:: max(1, len(rebal) // 8)][:8]:
        day = pos[pos["date"] == sess]
        stk = day[day["instrument"].isin(stock_set) & (day["instrument"] != BALLAST_ETF)]
        if stk.empty:
            continue
        ind_w: dict[str, float] = {}
        for _, row in stk.iterrows():
            code = sw_code_on(str(row["instrument"]), pd.Timestamp(sess), sw) or "_UNK"
            ind_w[code] = ind_w.get(code, 0.0) + float(row["target_weight"])
        mx = max(ind_w.values()) if ind_w else 0.0
        if mx > IND_CAP + 1e-6:
            ind_breach.append({"session": sess, "max_ind_w": mx, "ind_w": ind_w})
    if ind_breach:
        raise RuntimeError(f"industry cap breached in daily weights: {ind_breach[:2]}")

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
                # old packs may use different universe; compare stock-like codes only
                b_stk = {x for x in b if isinstance(x, str) and (x.endswith(".SH") or x.endswith(".SZ")) and not x.startswith("5") and not x.startswith("1")}
                # refine: exclude known ballast ETF
                b_stk = {x for x in b_stk if x != BALLAST_ETF}
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

    wpath = out_dir / f"g1g5_northbound_flow_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_northbound_flow_{stamp}.jsonl"
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

    meta: dict[str, Any] = {
        "mode": "g1g5_northbound_flow",
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
        "stock_budget": STOCK_BUDGET,
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
            "signal": "北向 hk_hold Δratio（增持侧）；断档>45日→两融 Δrzye 补窗",
            "select": f"增持侧 top{active_n} 等权；行业硬顶≤{IND_CAP:.0%}",
            "ballast": f"{BALLAST_ETF} 名义≈{BALLAST_FRAC:.0%}；禁 etf_core 0.70",
            "rebalance": "月频月末 + 首末日",
            "orthogonality_zh": (
                "相对九败：非OCF、非估值残差、非相对强弱主轴、非四臂、非份额流叠乘、"
                "非ETF-core、非解禁半月、非调仓事件；主轴=北向持股变化/两融补窗"
            ),
            "coverage_zh": (
                f"hk_hold sessions={score_meta.get('n_sessions_hk')}; "
                f"margin_fallback sessions={score_meta.get('n_sessions_margin_fallback')}"
            ),
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
        "hk_rows_loaded": score_meta.get("hk_rows"),
        "hk_date_span": score_meta.get("hk_date_span"),
        "margin_rows_loaded": score_meta.get("margin_rows"),
        "n_sessions_hk": score_meta.get("n_sessions_hk"),
        "n_sessions_margin_fallback": score_meta.get("n_sessions_margin_fallback"),
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
        "no_ocf_main_axis": True,
        "no_d1_val_resid_isomorph": True,
        "no_resid_etf_isomorph": True,
        "no_etf_core_overlay": True,
        "no_idx_rebal_isomorph": True,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "northbound_primary": True,
        "margin_gap_fill": True,
        "hk_hold_path": str(HK_HOLD.relative_to(ROOT)),
        "margin_detail_path": str(MARGIN_DETAIL.relative_to(ROOT)),
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

    meta_path = out_dir / f"g1g5_northbound_flow_run_meta_{stamp}.json"
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
        "reaches_x2_end": meta["reaches_x2_end"],
        "stub_forward_fill": False,
        "promotion_approved": False,
        "no_gp": True,
        "no_strategy_submit": True,
        "peak_rss_mb": meta["peak_rss_mb"],
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "ind_cap": IND_CAP,
        "n_sessions_hk": score_meta.get("n_sessions_hk"),
        "n_sessions_margin_fallback": score_meta.get("n_sessions_margin_fallback"),
        "g6": (g6_proof or {}).get("G6"),
    }
    (out_dir / f"{wpath.name}.meta.json").write_text(
        json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    g6_path = out_dir / f"debate_ledger_g1g5_northbound_flow_{stamp}_g6_proof.jsonl"
    g6_path.write_text(
        json.dumps(g6_proof, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return meta


def main() -> int:
    try:
        meta = run_northbound_flow()
    except Exception as e:  # noqa: BLE001
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
