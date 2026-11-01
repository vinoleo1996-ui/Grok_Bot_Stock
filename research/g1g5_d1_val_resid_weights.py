#!/usr/bin/env python3
"""G1G5 D1 valuation residual X2 weights (research-grade).

Mechanism (orthogonal to seven failed packs):
  - D1 pe_ttm → EP=1/pe_ttm (pe>0); SW L1 industry demean + float_mktcap tercile demean
  - Orthogonalize residual vs 20d excess return vs 510300 (suppress relative-strength exposure)
  - Select undervalued topN EW with industry hard cap ≤30%; ballast 510300
  - NOT naked EP/BM sort; NOT resid×share-flow; NOT friction/rebal/etf_core

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
)
from research.g1g5_x2_panel_stitch import clear_caches as clear_x2_caches  # noqa: E402
from research.g1g5_nontextbook_weights import (  # noqa: E402
    _forbid_textbook_tokens,
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_d1_val_resid_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_SCORE_N = 50  # scoring pool; keep small for peak RSS
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
X2_END = "2026-10-09"

STOCK_BUDGET = 0.80
BALLAST_FRAC = 0.20
BALLAST_ETF = "510300.SH"
IND_CAP = 0.30
MOM_LOOKBACK = 20

D1_VALUATION = ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_D1_VAL_RESID_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "错误定价纠偏："
    "D1 asof 估值倍数经申万一级行业与流通市值中性后的残差修正；"
    "低估侧收敛由边际资金支付相对510300的持有窗；"
    "并对相对宽基20日超额收益暴露做正交化压低；"
    "明确非裸EP/BM/PE截面排序；"
    "明确非残差收益×份额流同构；"
    "明确非四臂摩擦/解禁/调仓流/ETF-core直接持有。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def select_mid_large_topn_light(
    *,
    top_n: int = DEFAULT_SCORE_N,
    anchor: str = "2024-06-28",
) -> dict[str, Any]:
    """Anchor-session-only PIT read (avoid full mid_large pandas materialization)."""
    import pyarrow.compute as pc
    import pyarrow.dataset as ds
    import pyarrow.parquet as pq

    from research.ai_debate_memory_runner import DEFAULT_D0_PANELS, to_panel_id
    from research.g1g5_expand_g6 import MID_LARGE_PIT, panel_id_to_ts

    anchor_s = str(anchor)[:10]
    # Prefer dataset filter; fall back to pandas chunk if needed
    try:
        dataset = ds.dataset(str(MID_LARGE_PIT), format="parquet")
        table = dataset.to_table(
            columns=["session", "instrument_id", "float_mktcap_basis", "universe_id"],
            filter=ds.field("session") == anchor_s,
        )
        sub = table.to_pandas()
        del table
    except Exception:
        # row-group scan with arrow filter on session
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
    """session→ts set; filter sessions in arrow, never full-frame mid_large."""
    import pyarrow.compute as pc
    import pyarrow.dataset as ds

    from research.ai_debate_memory_runner import to_panel_id
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


def _preload_d1_valuation(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Chunked D1 load: only needed RGs + arrow filter before pandas (peak-safe)."""
    import gc

    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if not D1_VALUATION.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    want_set = set(want)
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=45)
    s1 = pd.Timestamp(max(sessions)[:10]) + pd.Timedelta(days=1)
    cols = [
        "ts_code",
        "trade_date",
        "pe_ttm",
        "pb",
        "ps_ttm",
        "float_mktcap",
        "available_at",
    ]
    pf = pq.ParquetFile(str(D1_VALUATION))
    want_arr = pa.array(want, type=pa.string())
    chunks: list[pd.DataFrame] = []
    for i in range(pf.metadata.num_row_groups):
        rg = pf.metadata.row_group(i)
        # skip RGs outside date window via stats
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
        # cast ts_code to string for is_in if large_string
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
    for c in ("pe_ttm", "pb", "ps_ttm", "float_mktcap"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["available_at"].notna()].copy()
    # drop unused cols early
    df = df[["ts_code", "pe_ttm", "pb", "ps_ttm", "float_mktcap", "available_at"]].copy()
    gc.collect()
    return df


def _d1_asof_snapshot(
    d1: pd.DataFrame,
    instruments: Sequence[str],
    session: str,
) -> dict[str, dict[str, float]]:
    """instrument → {ep, pb, ps, float_mktcap} asof available_at.normalize()<=session."""
    if d1 is None or d1.empty:
        return {}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sub = d1[d1["available_at"].dt.normalize() <= sess]
    if sub.empty:
        return {}
    # last available_at per ts_code
    sub = sub.sort_values("available_at").groupby("ts_code", as_index=False).tail(1)
    out: dict[str, dict[str, float]] = {}
    want = set(instruments)
    for _, row in sub.iterrows():
        inst = str(row["ts_code"])
        if inst not in want:
            continue
        pe = float(row["pe_ttm"]) if np.isfinite(row["pe_ttm"]) else np.nan
        pb = float(row["pb"]) if np.isfinite(row["pb"]) else np.nan
        ps = float(row["ps_ttm"]) if np.isfinite(row["ps_ttm"]) else np.nan
        mv = float(row["float_mktcap"]) if np.isfinite(row["float_mktcap"]) else np.nan
        ep = (1.0 / pe) if (np.isfinite(pe) and pe > 0) else np.nan
        out[inst] = {"ep": ep, "pb": pb, "ps": ps, "float_mktcap": mv, "pe_ttm": pe}
    return out


def _trailing_excess_from_closes(
    closes: pd.DataFrame,
    bench: pd.Series,
    instrument: str,
    session: str,
    lookback: int = MOM_LOOKBACK,
) -> float | None:
    if closes is None or closes.empty or instrument not in closes.columns:
        return None
    sess = pd.Timestamp(str(session)[:10]).normalize()
    ser = closes[instrument].dropna()
    hist = ser[ser.index <= sess]
    bh = bench[bench.index <= sess]
    if len(hist) < lookback + 1 or len(bh) < lookback + 1:
        return None
    if pd.Timestamp(hist.index[-1]).normalize() != sess:
        return None
    px0, px1 = float(hist.iloc[-(lookback + 1)]), float(hist.iloc[-1])
    b0, b1 = float(bh.iloc[-(lookback + 1)]), float(bh.iloc[-1])
    if px0 <= 0 or b0 <= 0:
        return None
    return (px1 / px0 - 1.0) - (b1 / b0 - 1.0)


def _preload_close_matrix(instruments: Sequence[str]) -> pd.DataFrame:
    """Compact wide closes; avoids unbounded per-call equity caches."""
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
    clear_x2_caches()
    try:
        import research.ai_debate_memory_runner as m

        m._EQUITY_CLOSE_CACHE.clear()
    except Exception:
        pass
    return mat


def score_val_resid(
    session: str,
    instruments: Sequence[str],
    *,
    snap: dict[str, dict[str, float]],
    sw: pd.DataFrame,
    closes: pd.DataFrame | None = None,
    bench: pd.Series | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Industry + size neutralized EP residual, then orthogonalize vs 20d excess."""
    meta: dict[str, Any] = {"arm": "d1_val_resid", "status": "ok", "metric": "ep_from_pe_ttm"}
    sess = pd.Timestamp(str(session)[:10]).normalize()

    raw_ep: dict[str, float] = {}
    mcaps: dict[str, float] = {}
    inst_sw: dict[str, str] = {}
    for inst in instruments:
        row = snap.get(inst)
        if not row:
            continue
        ep = row.get("ep")
        mv = row.get("float_mktcap")
        if ep is None or not np.isfinite(ep) or ep <= 0:
            continue
        code = sw_code_on(inst, sess, sw)
        if not code:
            continue
        raw_ep[inst] = float(ep)
        inst_sw[inst] = code
        if mv is not None and np.isfinite(mv) and mv > 0:
            mcaps[inst] = float(mv)

    meta["n_scored_raw"] = len(raw_ep)
    if len(raw_ep) < max(8, len(instruments) // 6):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计EP名过少 n={len(raw_ep)}"
        return {i: 0.0 for i in instruments}, meta

    # industry EW demean
    by_ind: dict[str, list[float]] = {}
    for inst, v in raw_ep.items():
        by_ind.setdefault(inst_sw[inst], []).append(v)
    ind_mean = {k: float(np.mean(vs)) for k, vs in by_ind.items()}
    ind_resid = {inst: raw_ep[inst] - ind_mean[inst_sw[inst]] for inst in raw_ep}
    meta["n_industries"] = len(by_ind)

    # size tercile demean on industry residual
    caps = {i: mcaps[i] for i in ind_resid if i in mcaps}
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
                size_resid[inst] = r - bucket_mean.get(int(terc.loc[inst]), 0.0)
            else:
                size_resid[inst] = r
        meta["size_neutral"] = True
    else:
        size_resid = dict(ind_resid)
        meta["size_neutral"] = False

    # orthogonalize vs 20d excess return (suppress relative-strength exposure)
    mom: dict[str, float] = {}
    if closes is not None and bench is not None and not closes.empty:
        for inst in size_resid:
            ex = _trailing_excess_from_closes(closes, bench, inst, session)
            if ex is not None and np.isfinite(ex):
                mom[inst] = float(ex)
    meta["n_with_mom"] = len(mom)
    if len(mom) >= 8:
        # residualize size_resid on mom via simple OLS
        common = [i for i in size_resid if i in mom]
        y = np.array([size_resid[i] for i in common], dtype=float)
        x = np.array([mom[i] for i in common], dtype=float)
        x = np.column_stack([np.ones(len(x)), x])
        try:
            beta, *_ = np.linalg.lstsq(x, y, rcond=None)
            preds = {common[i]: float(x[i] @ beta) for i in range(len(common))}
            ortho = {
                i: (size_resid[i] - preds[i]) if i in preds else size_resid[i]
                for i in size_resid
            }
            meta["mom_orthogonalized"] = True
            meta["ols_beta_mom"] = float(beta[1]) if len(beta) > 1 else None
        except Exception as e:  # noqa: BLE001
            ortho = dict(size_resid)
            meta["mom_orthogonalized"] = False
            meta["ols_err"] = str(e)[:120]
    else:
        ortho = dict(size_resid)
        meta["mom_orthogonalized"] = False

    ser = pd.Series({i: float(ortho.get(i, 0.0)) for i in instruments})
    scored_only = ser[list(raw_ep.keys())]
    mu, sd = float(scored_only.mean()), float(scored_only.std(ddof=0))
    if sd < 1e-12:
        z = ser * 0.0
    else:
        z = (ser - mu) / sd
        z = z.where(ser.index.isin(raw_ep.keys()), 0.0)
    out = {i: float(z.loc[i]) if i in z.index else 0.0 for i in instruments}
    meta["n_scored"] = len(raw_ep)
    return out, meta


def select_with_industry_cap(
    ranked: list[tuple[str, float]],
    *,
    sw: pd.DataFrame,
    session: str,
    active_n: int,
    ind_cap: float,
    budget: float,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Greedy top by score; fixed EW slot = budget/active_n; industry share ≤ ind_cap.

    Shortfall (fewer than active_n) goes to ballast — do NOT boost remaining names,
    or industry hard-cap would break when n_picked < active_n.
    """
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


def build_rebalance_decisions_val_resid(
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
        member_index = load_pit_member_index_light(stock_universe, rebalance_sessions)

    d1 = _preload_d1_valuation(stock_universe, rebalance_sessions)
    score_meta: dict[str, Any] = {
        "rebalance_arm_logs": [],
        "d1_rows": int(len(d1)),
        "d1_path": str(D1_VALUATION.relative_to(ROOT)),
        "peak_rss_mb_after_d1": round(_rss_kb() / 1024.0, 1),
    }
    # preload closes once then clear panel caches
    closes = _preload_close_matrix(stock_universe)
    bench = _load_benchmark_closes("510300")
    if not bench.empty:
        bench = bench.copy()
        bench.index = pd.to_datetime(bench.index).tz_localize(None).normalize()
    score_meta["peak_rss_mb_after_closes"] = round(_rss_kb() / 1024.0, 1)
    gc.collect()

    decisions: list[dict[str, Any]] = []
    all_instruments = set(stock_universe) | {BALLAST_ETF}

    for sess in rebalance_sessions:
        present = (
            mid_large_members_on(sess, stock_universe, member_index=member_index)
            if use_pit_membership
            else set(stock_universe)
        )
        if len(present) < 8:
            # pure ballast
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

        snap = _d1_asof_snapshot(d1, list(present), sess)
        scores, arm_meta = score_val_resid(
            sess, list(present), snap=snap, sw=sw, closes=closes, bench=bench
        )
        ranked = sorted(
            ((i, scores[i]) for i in present if scores.get(i, 0.0) != 0.0 or i in snap),
            key=lambda x: x[1],
            reverse=True,  # high residual EP = undervalued
        )
        # keep only positive residual preference; if all non-positive, take least-negative head
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

        # emit overrides for all univ + ballast
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
                "top_head": [(i, round(scores.get(i, 0.0), 4)) for i, _ in ranked_use[:8]],
            }
        )
        if cap_meta.get("max_ind_weight", 0) > IND_CAP + 1e-6:
            raise RuntimeError(
                f"industry cap breached @ {sess}: {cap_meta.get('max_ind_weight')}"
            )

    # free heavy frames before weight expansion
    del d1
    del closes
    clear_x2_caches()
    try:
        import research.ai_debate_memory_runner as m

        m._EQUITY_CLOSE_CACHE.clear()
    except Exception:
        pass
    gc.collect()
    score_meta["peak_rss_mb_after_score"] = round(_rss_kb() / 1024.0, 1)
    return decisions, score_meta, sorted(all_instruments)


def run_d1_val_resid(
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

    decisions, score_meta, instruments = build_rebalance_decisions_val_resid(
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

    # industry cap check on a sample of sessions (rebalance days)
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
    # precompute new active stock sets once
    sample = [x for x in rebal if x >= "2024-03-01"][:8]
    new_sets = {}
    for ss in sample:
        a = set(
            weights[(weights["date"] == ss) & (weights["target_weight"] > 0)]["instrument"]
        )
        new_sets[ss] = {x for x in a if x in stock_set and x != BALLAST_ETF}
    for label, path in (
        ("expand", intel / "g1g5_expand_daily_weights_20261012_111354.parquet"),
        ("friction_monthly", intel / "g1g5_nontextbook_daily_weights_20261012_111316.parquet"),
        ("lowturn", intel / "g1g5_lowturn_daily_weights_20261012_112301.parquet"),
        ("resid_etf", factory / "g1g5_resid_etf_daily_weights_20261013_002418.parquet"),
        ("etf_core", factory / "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet"),
        ("friction_cost_redesign", factory / "g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet"),
        ("idx_rebal_flow", factory / "g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet"),
    ):
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            entry["new_mean_one_way"] = tow.get("mean_one_way")
            diffs = []
            for ss in sample:
                a_stk = new_sets[ss]
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                b_stk = {x for x in b if x in stock_set}
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

    wpath = out_dir / f"g1g5_d1_val_resid_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_d1_val_resid_{stamp}.jsonl"
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
        "mode": "g1g5_d1_val_resid",
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
            "signal": "D1 pe_ttm→EP；SW L1+市值三分位中性残差；相对宽基20d超额OLS正交",
            "select": f"低估侧 top{active_n} 等权；行业硬顶≤{IND_CAP:.0%}",
            "ballast": f"{BALLAST_ETF} 名义≈{BALLAST_FRAC:.0%}；禁 etf_core 0.70",
            "rebalance": "月频月末 + 首末日",
            "orthogonality_zh": (
                "相对七败：非动量主轴、非四臂、非份额流叠乘、非ETF-core、非解禁半月、非调仓事件；"
                "残差对象=估值倍数非收益×流"
            ),
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
        "d1_rows_loaded": score_meta.get("d1_rows"),
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
        "no_naked_ep_bm_sort": True,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "d1_valuation_asof_used": True,
        "d1_valuation_path": str(D1_VALUATION.relative_to(ROOT)),
        "d1_note_zh": "D1 ACCEPT_FULL 仅研究 asof（估值残差）；非晋级授权",
        "d1_accept_ref": "output/alpha/d1_valuation_full_accept_20261012.json",
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

    meta_path = out_dir / f"g1g5_d1_val_resid_run_meta_{stamp}.json"
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
        "selection_rule": "d1_ep_ind_size_resid_mom_ortho_ew_indcap30",
        "role_zh": "机制正交新权重：D1 估值残差 asof（研究级）",
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

    ap = argparse.ArgumentParser(description="G1G5 D1 valuation residual X2 weights")
    ap.add_argument("--score-n", type=int, default=DEFAULT_SCORE_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_d1_val_resid(
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
