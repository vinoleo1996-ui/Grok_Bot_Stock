#!/usr/bin/env python3
"""G1G5 balance-sheet accrual quality X2 weights (research-grade).

Mechanism (orthogonal to ten failed + capacity_adv + margin_delta + OCF/val):
  - Primary: PIT Sloan-style WC accrual / total_assets from balancesheet
  - Industry demean (SW L1) + residual vs log(float_mktcap)
  - Prefer LOW residual (low-accrual / high BS-earnings quality); topN EW; ind≤28%; name≤4%
  - Hard-exclude 600519.SH / 002371.SZ; ballast 510300
  - NOT ocf_to_profit; NOT moneyflow; NOT ADV rank; NOT margin/hk_hold; NOT EP/BM; NOT 四臂/rebal/etf_core

promotion_approved=false; no orders; no Strategy; no GP; no stub forward-fill; no Book-Smoke.
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
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_accrual_quality_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_SCORE_N = 80
DEFAULT_ACTIVE_N = 25
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
X2_END = "2026-10-09"

STOCK_BUDGET = 0.80
BALLAST_FRAC = 0.20
BALLAST_ETF = "510300.SH"
IND_CAP = 0.28
NAME_CAP = 0.04
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ"})

BALANCESHEET_PIT = ROOT / "data" / "v2" / "financials_pit" / "balancesheet_pit_tushare.parquet"
D1_VALUATION = ROOT / "data" / "v2" / "valuation" / "daily_basic_full_tushare.parquet"
WHO_PAYS_PREREG = "docs/v2/AI_G1G5_ACCRUAL_QUALITY_WHO_PAYS_PREREG_ZH.md"

WHO_PAYS_ZH = (
    "投资者过度依赖应计盈余、低估低应计/资产负债表盈余的对手盘："
    "以PIT资产负债表营运资本应计/总资产（Sloan代理，缺Dep不加）"
    "经申万一级行业demean+对数流通市值残差分位选股；低应计优先；"
    "主叙事=非OCF应计质量（资产负债表）；"
    "明确非ocf_to_profit、非EP/BM估值残差、非ADV容量分位、"
    "非两融/北向资金流、非相对强弱主轴、非四臂摩擦/解禁/份额流/调仓/ETF-core。"
)

# Tag contains leaf name accrual_quality (Leo-mandated); not textbook quality factor axis.
def _forbid_leaf_tokens(tag: str, who: str) -> None:
    if "动量" in who or "动量" in tag:
        raise RuntimeError("who_pays/tag must not contain 动量")
    tag_l = tag.lower()
    for b in ("momentum", "mom_", "价值"):
        if b in tag_l or b in tag:
            raise RuntimeError(f"textbook_token_forbidden:{b!r}")



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


def _load_balancesheet_pit(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Chunked balancesheet PIT load for universe (peak-safe). report_type=1 only."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if not BALANCESHEET_PIT.exists():
        raise RuntimeError(f"missing balancesheet: {BALANCESHEET_PIT}")
    want = sorted({str(x) for x in instruments})
    want_set = set(want)
    # need prior reports before window → pull from ~2018
    s0 = pd.Timestamp("2018-01-01")
    s1 = pd.Timestamp(max(sessions)[:10]) + pd.Timedelta(days=1)
    cols = [
        "ts_code",
        "end_date",
        "available_at",
        "report_type",
        "total_assets",
        "total_cur_assets",
        "money_cap",
        "total_cur_liab",
        "st_borr",
        "taxes_payable",
    ]
    pf = pq.ParquetFile(str(BALANCESHEET_PIT))
    want_arr = pa.array(want, type=pa.string())
    chunks: list[pd.DataFrame] = []
    for i in range(pf.metadata.num_row_groups):
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
        # report_type consolidated = 1
        rt = part["report_type"].astype(str).str.replace(r"\.0$", "", regex=True)
        part = part[rt.isin(["1"])].copy()
        if part.empty:
            del part
            continue
        part["available_at"] = pd.to_datetime(part["available_at"]).dt.tz_localize(None)
        part["end_date"] = pd.to_datetime(part["end_date"]).dt.tz_localize(None)
        part = part[(part["available_at"] >= s0) & (part["available_at"] <= s1)]
        if part.empty:
            del part
            continue
        for c in (
            "total_assets",
            "total_cur_assets",
            "money_cap",
            "total_cur_liab",
            "st_borr",
            "taxes_payable",
        ):
            part[c] = pd.to_numeric(part[c], errors="coerce")
        chunks.append(
            part[
                [
                    "ts_code",
                    "end_date",
                    "available_at",
                    "total_assets",
                    "total_cur_assets",
                    "money_cap",
                    "total_cur_liab",
                    "st_borr",
                    "taxes_payable",
                ]
            ]
        )
        del part
        if i % 8 == 0:
            gc.collect()
    if not chunks:
        return pd.DataFrame()
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    df = df[df["available_at"].notna() & df["end_date"].notna()].copy()
    # keep latest available_at per (ts_code, end_date)
    df = df.sort_values(["ts_code", "end_date", "available_at"])
    df = df.groupby(["ts_code", "end_date"], as_index=False).tail(1)
    gc.collect()
    return df.reset_index(drop=True)


def _preload_d1_float_mktcap(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Chunked D1 load: float_mktcap only (for residual; NOT ADV selection)."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if not D1_VALUATION.exists():
        return pd.DataFrame()
    want = sorted({str(x) for x in instruments})
    want_set = set(want)
    s0 = pd.Timestamp(min(sessions)[:10]) - pd.Timedelta(days=45)
    s1 = pd.Timestamp(max(sessions)[:10]) + pd.Timedelta(days=1)
    cols = ["ts_code", "trade_date", "float_mktcap", "available_at"]
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
        chunks.append(part[["ts_code", "float_mktcap", "available_at"]])
        del part
        gc.collect()
    if not chunks:
        return pd.DataFrame()
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    df["available_at"] = pd.to_datetime(df["available_at"]).dt.tz_localize(None)
    df["float_mktcap"] = pd.to_numeric(df["float_mktcap"], errors="coerce")
    df = df[df["available_at"].notna()].copy()
    gc.collect()
    return df


def _mcap_snapshot(
    d1: pd.DataFrame,
    instruments: Sequence[str],
    session: str,
) -> dict[str, float]:
    if d1 is None or d1.empty:
        return {}
    sess = pd.Timestamp(str(session)[:10]).normalize()
    sub = d1[d1["available_at"].dt.normalize() <= sess]
    if sub.empty:
        return {}
    sub = sub.sort_values("available_at").groupby("ts_code", as_index=False).tail(1)
    out: dict[str, float] = {}
    want = set(instruments)
    for _, row in sub.iterrows():
        inst = str(row["ts_code"])
        if inst not in want:
            continue
        mv = float(row["float_mktcap"]) if np.isfinite(row["float_mktcap"]) else np.nan
        if np.isfinite(mv) and mv > 0:
            out[inst] = float(mv)
    return out


def score_accrual_resid(
    session: str,
    instruments: Sequence[str],
    bs: pd.DataFrame,
    mcaps: dict[str, float],
    sw: pd.DataFrame,
) -> tuple[dict[str, float], dict[str, Any]]:
    """WC accrual/assets → SW L1 demean → residual vs log(float_mktcap).

    Prefer LOW residual (low accrual). Formula (no Dep — field unavailable):
      WC_ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔTP)
      accrual_ratio = WC_ACC / max(total_assets_t, 1e6)
    """
    meta: dict[str, Any] = {
        "arm": "accrual_wc_bs_ind_mcap_resid",
        "source": "balancesheet_pit_primary",
        "status": "ok",
        "formula": "WC_ACC=(dCA-dCash)-(dCL-dSTD-dTP); ratio=WC_ACC/TA; no_Dep",
        "prefer": "low_accrual",
        "no_ocf_main_axis": True,
        "no_moneyflow_main_leg": True,
    }
    sess = pd.Timestamp(str(session)[:10]).normalize()
    if bs is None or bs.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "balancesheet empty"
        return {}, meta
    sub = bs[bs["available_at"].dt.normalize() <= sess]
    if sub.empty:
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = "no BS asof"
        return {}, meta

    raw: dict[str, float] = {}
    inst_sw: dict[str, str] = {}
    n_pair = 0
    for code, g in sub.groupby("ts_code", sort=False):
        code = str(code)
        if code not in instruments or code in HARD_EXCLUDE:
            continue
        g = g.sort_values(["end_date", "available_at"])
        # latest report asof session
        cur = g.iloc[-1]
        prior = g[g["end_date"] < cur["end_date"]]
        if prior.empty:
            continue
        base = prior.iloc[-1]
        # required fields on current
        ta = float(cur["total_assets"]) if np.isfinite(cur["total_assets"]) else np.nan
        if not (np.isfinite(ta) and ta > 1e6):
            continue

        def _f(row, col, default=0.0):
            v = row[col]
            if v is None or (isinstance(v, float) and not np.isfinite(v)):
                return float(default)
            try:
                fv = float(v)
            except Exception:
                return float(default)
            return fv if np.isfinite(fv) else float(default)

        d_ca = _f(cur, "total_cur_assets", np.nan) - _f(base, "total_cur_assets", np.nan)
        d_cash = _f(cur, "money_cap", np.nan) - _f(base, "money_cap", np.nan)
        d_cl = _f(cur, "total_cur_liab", np.nan) - _f(base, "total_cur_liab", np.nan)
        # STD / taxes: missing → 0 (common for banks/non-reporters of st_borr)
        d_std = _f(cur, "st_borr", 0.0) - _f(base, "st_borr", 0.0)
        d_tp = _f(cur, "taxes_payable", 0.0) - _f(base, "taxes_payable", 0.0)
        if not all(np.isfinite(x) for x in (d_ca, d_cash, d_cl)):
            continue
        wc_acc = (d_ca - d_cash) - (d_cl - d_std - d_tp)
        if not np.isfinite(wc_acc):
            continue
        ratio = float(wc_acc) / max(float(ta), 1e6)
        if not np.isfinite(ratio):
            continue
        swc = sw_code_on(code, sess, sw)
        if not swc:
            continue
        raw[code] = float(ratio)
        inst_sw[code] = swc
        n_pair += 1

    meta["n_scored_raw"] = n_pair
    meta["last_bs_available_at"] = str(sub["available_at"].max())
    if n_pair < max(8, len(instruments) // 6):
        meta["status"] = "coverage_gap"
        meta["reason_zh"] = f"可计应计名过少 n={n_pair}"
        return raw, meta

    by_ind: dict[str, list[float]] = {}
    for inst, v in raw.items():
        by_ind.setdefault(inst_sw[inst], []).append(v)
    ind_mean = {k: float(np.mean(vs)) for k, vs in by_ind.items()}
    demeaned = {inst: raw[inst] - ind_mean[inst_sw[inst]] for inst in raw}
    meta["n_industries"] = len(by_ind)

    xs: list[float] = []
    ys: list[float] = []
    keys: list[str] = []
    for inst, dv in demeaned.items():
        mv = mcaps.get(inst)
        if mv is None or not (np.isfinite(mv) and mv > 0):
            continue
        xs.append(math.log(float(mv)))
        ys.append(float(dv))
        keys.append(inst)
    resid: dict[str, float] = dict(demeaned)
    meta["n_with_mcap"] = len(keys)
    if len(keys) >= 8:
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        x_dm = x - x.mean()
        y_dm = y - y.mean()
        denom = float(np.dot(x_dm, x_dm))
        if denom > 1e-12:
            b = float(np.dot(x_dm, y_dm) / denom)
            a = float(y.mean() - b * x.mean())
            for inst, xi, yi in zip(keys, xs, ys):
                resid[inst] = float(yi - (a + b * xi))
            meta["mcap_ols"] = {"a": a, "b": b, "n": len(keys)}
        else:
            meta["mcap_ols"] = {"skipped": "x_var_too_small"}
    else:
        meta["mcap_ols"] = {"skipped": "too_few_mcap"}

    meta["n_scored"] = len(resid)
    return resid, meta


def select_with_industry_name_cap(
    ranked: list[tuple[str, float]],
    *,
    sw: pd.DataFrame,
    session: str,
    active_n: int,
    ind_cap: float,
    name_cap: float,
    budget: float,
) -> tuple[dict[str, float], dict[str, Any]]:
    sess = pd.Timestamp(str(session)[:10]).normalize()
    w_each = float(budget) / float(max(1, active_n))
    w_each = min(w_each, float(name_cap))
    max_n_ind = max(1, int(np.floor(ind_cap / max(w_each, 1e-12) + 1e-12)))
    picked: list[str] = []
    ind_count: dict[str, int] = {}
    skipped_cap: list[str] = []
    skipped_hard: list[str] = []
    for inst, _sc in ranked:
        if inst in HARD_EXCLUDE:
            skipped_hard.append(inst)
            continue
        code = sw_code_on(inst, sess, sw) or "_UNK"
        if ind_count.get(code, 0) >= max_n_ind:
            skipped_cap.append(inst)
            continue
        picked.append(inst)
        ind_count[code] = ind_count.get(code, 0) + 1
        if len(picked) >= active_n:
            break
    meta: dict[str, Any] = {
        "n_picked": len(picked),
        "ind_counts": dict(ind_count),
        "max_n_per_ind": max_n_ind,
        "w_each": w_each,
        "name_cap": name_cap,
        "n_skipped_ind_cap": len(skipped_cap),
        "n_skipped_hard_exclude": len(skipped_hard),
        "skipped_head": skipped_cap[:8],
    }
    if not picked:
        return {}, meta
    # equal weight then clip name_cap and renormalize toward budget under ind cap
    w = {inst: w_each for inst in picked}
    stock_sum = float(sum(w.values()))
    if stock_sum > budget + 1e-12:
        scale = budget / stock_sum
        w = {i: v * scale for i, v in w.items()}
    # If fewer than active_n scored names, top-up toward budget under name/ind caps
    # (avoid etf_core-like ballast drift when BS CA coverage skips financials).
    stock_sum = float(sum(w.values()))
    if 0 < stock_sum < budget - 1e-9 and picked:
        # greedy equal top-up room
        for _ in range(12):
            room = {}
            ind_w0: dict[str, float] = {}
            for inst, wv in w.items():
                code = sw_code_on(inst, sess, sw) or "_UNK"
                ind_w0[code] = ind_w0.get(code, 0.0) + wv
            for inst, wv in w.items():
                code = sw_code_on(inst, sess, sw) or "_UNK"
                name_room = max(0.0, float(name_cap) - wv)
                ind_room = max(0.0, float(ind_cap) - ind_w0.get(code, 0.0))
                room[inst] = min(name_room, ind_room)
            total_room = float(sum(room.values()))
            need = float(budget) - float(sum(w.values()))
            if total_room <= 1e-12 or need <= 1e-12:
                break
            take = min(need, total_room)
            for inst, r in room.items():
                if r <= 0:
                    continue
                w[inst] += take * (r / total_room)
        w = {i: float(max(0.0, v)) for i, v in w.items()}
    # enforce industry cap by proportional shrink
    for _ in range(6):
        ind_w: dict[str, float] = {}
        ind_members: dict[str, list[str]] = {}
        for inst, wv in w.items():
            code = sw_code_on(inst, sess, sw) or "_UNK"
            ind_w[code] = ind_w.get(code, 0.0) + wv
            ind_members.setdefault(code, []).append(inst)
        changed = False
        for code, tw in ind_w.items():
            if tw > ind_cap + 1e-12:
                factor = ind_cap / tw
                for inst in ind_members[code]:
                    w[inst] *= factor
                changed = True
        for inst in list(w.keys()):
            if w[inst] > name_cap + 1e-12:
                w[inst] = name_cap
                changed = True
        if not changed:
            break
    w = {i: float(max(0.0, v)) for i, v in w.items() if v > 1e-12}
    ind_w_final: dict[str, float] = {}
    for inst, wv in w.items():
        code = sw_code_on(inst, sess, sw) or "_UNK"
        ind_w_final[code] = ind_w_final.get(code, 0.0) + wv
    meta["ind_weights"] = {k: round(v, 4) for k, v in ind_w_final.items()}
    meta["max_ind_weight"] = float(max(ind_w_final.values())) if ind_w_final else 0.0
    meta["max_name_weight"] = float(max(w.values())) if w else 0.0
    meta["stock_w_sum"] = float(sum(w.values()))
    return w, meta


def build_rebalance_decisions_accrual_quality(
    stock_universe: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    active_n: int = DEFAULT_ACTIVE_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    _forbid_leaf_tokens(MECHANISM_TAG, WHO_PAYS_ZH)

    sw = _load_sw_members()
    member_index = None
    if use_pit_membership:
        member_index = load_pit_member_index_light(stock_universe, rebalance_sessions)

    bs = _load_balancesheet_pit(stock_universe, rebalance_sessions)
    score_meta: dict[str, Any] = {
        "rebalance_arm_logs": [],
        "bs_rows": int(len(bs)),
        "bs_path": str(BALANCESHEET_PIT.relative_to(ROOT)),
        "peak_rss_mb_after_bs": round(_rss_kb() / 1024.0, 1),
        "no_hk_hold": True,
        "no_moneyflow_main_leg": True,
        "no_adv_selection": True,
        "no_ocf_main_axis": True,
        "no_margin_main_leg": True,
    }
    d1 = _preload_d1_float_mktcap(stock_universe, rebalance_sessions)
    score_meta["d1_mcap_rows"] = int(len(d1))
    score_meta["peak_rss_mb_after_d1"] = round(_rss_kb() / 1024.0, 1)
    # Precompute mcap snapshots then free D1 (peak-safe)
    mcap_by_sess: dict[str, dict[str, float]] = {}
    for sess in rebalance_sessions:
        mcap_by_sess[str(sess)[:10]] = _mcap_snapshot(d1, list(stock_universe), sess)
    del d1
    gc.collect()
    score_meta["peak_rss_mb_after_mcap_snap"] = round(_rss_kb() / 1024.0, 1)

    decisions: list[dict[str, Any]] = []
    all_instruments = set(stock_universe) | {BALLAST_ETF}

    for sess in rebalance_sessions:
        present = (
            mid_large_members_on(sess, stock_universe, member_index=member_index)
            if use_pit_membership
            else set(stock_universe)
        )
        present = {x for x in present if x not in HARD_EXCLUDE}
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

        mcaps = mcap_by_sess.get(str(sess)[:10], {})
        # restrict to present
        mcaps = {k: v for k, v in mcaps.items() if k in present}
        scores, arm_meta = score_accrual_resid(
            sess, list(present), bs, mcaps, sw
        )
        # LOW accrual residual preferred → ascending sort (always full scored set)
        ranked = sorted(
            ((i, scores[i]) for i in present if i in scores),
            key=lambda x: x[1],
            reverse=False,
        )
        ranked_use = ranked

        target, cap_meta = select_with_industry_name_cap(
            ranked_use,
            sw=sw,
            session=sess,
            active_n=active_n,
            ind_cap=IND_CAP,
            name_cap=NAME_CAP,
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
            if inst in HARD_EXCLUDE:
                w = 0.0
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
                "max_name_weight": cap_meta.get("max_name_weight"),
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
        if cap_meta.get("max_name_weight", 0) > NAME_CAP + 1e-6:
            raise RuntimeError(
                f"name cap breached @ {sess}: {cap_meta.get('max_name_weight')}"
            )

    del bs
    del mcap_by_sess
    gc.collect()
    score_meta["peak_rss_mb_after_score"] = round(_rss_kb() / 1024.0, 1)
    return decisions, score_meta, sorted(all_instruments)


def _jaccard_vs_priors(
    weights: pd.DataFrame,
    stock_set: set[str],
    rebal: Sequence[str],
) -> dict[str, Any]:
    factory = ROOT / "output" / "ai_factory"
    intel = ROOT / "output" / "intel"
    sample = [x for x in rebal if x >= "2024-03-01"]
    # denser sample for key peers
    if len(sample) > 16:
        step = max(1, len(sample) // 16)
        sample = sample[::step][:16]
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
        ("northbound_flow", factory / "g1g5_northbound_flow_daily_weights_20261013_111252.parquet"),
        ("capacity_adv", factory / "g1g5_capacity_adv_daily_weights_20261013_111219.parquet"),
        ("margin_delta", factory / "g1g5_margin_delta_daily_weights_20261013_020825.parquet"),
    )
    vs: dict[str, Any] = {}
    for label, path in prior_packs:
        entry: dict[str, Any] = {"path": str(path.relative_to(ROOT)) if path.exists() else None}
        if path.exists():
            old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
            diffs = []
            for ss in sample:
                a_stk = new_sets[ss]
                b = set(old[(old["date"] == ss) & (old["target_weight"] > 0)]["instrument"])
                b_stk = {
                    x
                    for x in b
                    if isinstance(x, str)
                    and (x.endswith(".SH") or x.endswith(".SZ"))
                    and not x.startswith("5")
                    and not x.startswith("1")
                    and x != BALLAST_ETF
                }
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
            entry["jaccard_frac_ge_0_7"] = (
                float(np.mean([1.0 if j >= 0.7 else 0.0 for j in jacs])) if jacs else None
            )
            entry["hard_reject_isomorph"] = bool(
                entry["jaccard_stock_max"] is not None
                and entry["jaccard_stock_max"] >= 0.7
                and entry["jaccard_frac_ge_0_7"] is not None
                and entry["jaccard_frac_ge_0_7"] >= 0.5
            )
            del old
            gc.collect()
        vs[label] = entry
    return vs


def run_accrual_quality(
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
    stock_universe = [x for x in uni["instruments"] if x not in HARD_EXCLUDE]
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

    decisions, score_meta, instruments = build_rebalance_decisions_accrual_quality(
        stock_universe,
        rebal,
        active_n=active_n,
        use_pit_membership=True,
    )
    clear_x2_caches()
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
        "momentum|动量|价值", case=False, regex=True
    ).any():
        raise RuntimeError("mechanism_tag contains textbook token")
    # allow mandated leaf substring accrual_quality in tag; still ban bare 动量

    daily_sum = weights.groupby("date")["target_weight"].sum()
    if float(daily_sum.min()) < 1.0 - 1e-6 or float(daily_sum.max()) > 1.0 + 1e-6:
        # allow tiny float noise already covered; tighter check
        if float(daily_sum.min()) < 0.99 or float(daily_sum.max()) > 1.01:
            raise RuntimeError(
                f"daily_gross out of band: min={daily_sum.min()} max={daily_sum.max()}"
            )

    # hard exclude must be zero
    for bad in HARD_EXCLUDE:
        bad_w = weights.loc[weights["instrument"] == bad, "target_weight"]
        if len(bad_w) and float(bad_w.max()) > 1e-12:
            raise RuntimeError(f"hard exclude breached: {bad} max_w={bad_w.max()}")

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

    # name cap on daily stock weights
    stock_pos = pos.loc[is_stock]
    if len(stock_pos):
        max_name = float(stock_pos["target_weight"].max())
        if max_name > NAME_CAP + 1e-6:
            raise RuntimeError(f"daily name cap breached: {max_name}")
    else:
        max_name = 0.0

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
    vs = _jaccard_vs_priors(weights, stock_set, rebal)
    # hard reject if any peer looks isomorphic
    for label, entry in vs.items():
        if entry.get("hard_reject_isomorph"):
            raise RuntimeError(
                f"isomorph hard-reject vs {label}: "
                f"max={entry.get('jaccard_stock_max')} frac≥0.7={entry.get('jaccard_frac_ge_0_7')}"
            )
    gc.collect()

    wpath = out_dir / f"g1g5_accrual_quality_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_accrual_quality_{stamp}.jsonl"
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

    # impact/capacity note for RECEIPT (no smoke)
    impact_note = {
        "aum_dual_read_yuan": [600_000, 1_000_000],
        "name_cap": NAME_CAP,
        "hard_exclude": sorted(HARD_EXCLUDE),
        "note_zh": (
            "单名≤4%且硬排除600519/002371；60万∧100万冲击/容量由 Alpha ACCEPT 后 Book-Smoke 双读；"
            "本叶不按ADV分位选股，容量仅为硬约束。"
        ),
    }

    meta: dict[str, Any] = {
        "mode": "g1g5_accrual_quality",
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
        "max_name_weight_daily": max_name,
        "ind_cap": IND_CAP,
        "name_cap": NAME_CAP,
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
            "signal": "PIT BS营运资本应计/总资产 → 申万一级 demean → log流通市值残差；低应计优先；无Dep",
            "select": f"低应计侧 top{active_n} 等权；行业硬顶≤{IND_CAP:.0%}；单名≤{NAME_CAP:.0%}",
            "ballast": f"{BALLAST_ETF} 名义≈{BALLAST_FRAC:.0%}；禁 etf_core 0.70",
            "rebalance": "月频月末 + 首末日",
            "orthogonality_zh": (
                "相对十灭+容量+两融+OCF/估值/北向：非ocf_to_profit、非EP/BM、非ADV分位、"
                "非两融/北向、非相对强弱、非四臂、非份额流、非ETF-core、非调仓；主轴=BS应计"
            ),
            "hard_exclude": sorted(HARD_EXCLUDE),
            "no_moneyflow_main_leg": True,
            "no_ocf_main_axis": True,
            "no_hk_hold": True,
            "no_margin_main_leg": True,
            "accrual_formula": "WC_ACC=(dCA-dCash)-(dCL-dSTD-dTP)/TA; no_Dep",
        },
        "score_meta_keys": list(score_meta.keys()),
        "n_rebalance_logged": len(score_meta.get("rebalance_arm_logs") or []),
        "bs_rows_loaded": score_meta.get("bs_rows"),
        "d1_mcap_rows_loaded": score_meta.get("d1_mcap_rows"),
        "impact_capacity_note": impact_note,
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
        "no_book_smoke_self": True,
        "no_ocf_main_axis": True,
        "no_d1_val_resid_isomorph": True,
        "no_resid_etf_isomorph": True,
        "no_etf_core_overlay": True,
        "no_idx_rebal_isomorph": True,
        "no_northbound_isomorph": True,
        "no_capacity_adv_isomorph": True,
        "no_moneyflow_main_leg": True,
        "no_hk_hold": True,
        "weight_end_requested": str(weight_end),
        "x2_end_target": X2_END,
        "reaches_x2_end": bool(str(weights["date"].max()) >= str(X2_END)[:10]),
        "accrual_primary": True,
        "balancesheet_path": str(BALANCESHEET_PIT.relative_to(ROOT)),
        "hard_exclude_weights": {
            k: float(weights.loc[weights["instrument"] == k, "target_weight"].max())
            if (weights["instrument"] == k).any()
            else 0.0
            for k in HARD_EXCLUDE
        },
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

    meta_path = out_dir / f"g1g5_accrual_quality_run_meta_{stamp}.json"
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
        "no_book_smoke_self": True,
        "peak_rss_mb": meta["peak_rss_mb"],
        "mean_ballast_share": mean_ballast,
        "mean_stock_share": mean_stock,
        "max_name_weight_daily": max_name,
        "ind_cap": IND_CAP,
        "name_cap": NAME_CAP,
        "g6": (g6_proof or {}).get("G6"),
        "jaccard_vs_capacity_adv": {
            "mean": (vs.get("capacity_adv") or {}).get("jaccard_stock_mean"),
            "max": (vs.get("capacity_adv") or {}).get("jaccard_stock_max"),
            "frac_ge_0_7": (vs.get("capacity_adv") or {}).get("jaccard_frac_ge_0_7"),
        },
        "jaccard_vs_northbound": {
            "mean": (vs.get("northbound_flow") or {}).get("jaccard_stock_mean"),
            "max": (vs.get("northbound_flow") or {}).get("jaccard_stock_max"),
            "frac_ge_0_7": (vs.get("northbound_flow") or {}).get("jaccard_frac_ge_0_7"),
        },
        "jaccard_vs_indcap_ocf": {
            "mean": (vs.get("indcap_momneut_ocf") or {}).get("jaccard_stock_mean"),
            "max": (vs.get("indcap_momneut_ocf") or {}).get("jaccard_stock_max"),
            "frac_ge_0_7": (vs.get("indcap_momneut_ocf") or {}).get("jaccard_frac_ge_0_7"),
        },
        "jaccard_vs_d1_val_resid": {
            "mean": (vs.get("d1_val_resid") or {}).get("jaccard_stock_mean"),
            "max": (vs.get("d1_val_resid") or {}).get("jaccard_stock_max"),
            "frac_ge_0_7": (vs.get("d1_val_resid") or {}).get("jaccard_frac_ge_0_7"),
        },
        "jaccard_vs_margin_delta": {
            "mean": (vs.get("margin_delta") or {}).get("jaccard_stock_mean"),
            "max": (vs.get("margin_delta") or {}).get("jaccard_stock_max"),
            "frac_ge_0_7": (vs.get("margin_delta") or {}).get("jaccard_frac_ge_0_7"),
        },
    }
    (out_dir / f"{wpath.name}.meta.json").write_text(
        json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    g6_path = out_dir / f"debate_ledger_g1g5_accrual_quality_{stamp}_g6_proof.jsonl"
    g6_path.write_text(
        json.dumps(g6_proof, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    # verify stats JSON for Alpha
    alpha_dir = ROOT / "output" / "alpha"
    alpha_dir.mkdir(parents=True, exist_ok=True)
    verify = {
        "mechanism_tag": MECHANISM_TAG,
        "weights_path": str(wpath.relative_to(ROOT)),
        "rows": int(len(weights)),
        "n_dates": n_sess,
        "n_instruments": int(weights["instrument"].nunique()),
        "date_span": [str(weights["date"].min()), str(weights["date"].max())],
        "daily_gross_min": meta["daily_gross_min"],
        "daily_gross_max": meta["daily_gross_max"],
        "stub_forward_fill": False,
        "stub_window": meta["stub_window"],
        "reaches_x2_end": meta["reaches_x2_end"],
        "peak_rss_mb": meta["peak_rss_mb"],
        "g6": (g6_proof or {}).get("G6"),
        "max_name_weight_daily": max_name,
        "mean_ballast_share": mean_ballast,
        "hard_exclude_weights": meta["hard_exclude_weights"],
        "vs_jaccard": {
            k: {
                "mean": v.get("jaccard_stock_mean"),
                "max": v.get("jaccard_stock_max"),
                "frac_ge_0_7": v.get("jaccard_frac_ge_0_7"),
                "hard_reject_isomorph": v.get("hard_reject_isomorph"),
            }
            for k, v in vs.items()
        },
        "impact_capacity_note": impact_note,
        "promotion_approved": False,
        "no_gp": True,
        "no_book_smoke_self": True,
    }
    vpath = alpha_dir / f"AI_G1G5_ACCRUAL_QUALITY_WEIGHT_VERIFY_STATS_{stamp}.json"
    vpath.write_text(json.dumps(verify, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["verify_stats_path"] = str(vpath.relative_to(ROOT))
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    return meta


def main() -> int:
    try:
        meta = run_accrual_quality()
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
            "frac_ge_0_7": v.get("jaccard_frac_ge_0_7"),
        }
        for k, v in (meta.get("vs_prior_packs") or {}).items()
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
