#!/usr/bin/env python3
"""G1G5 industry-cap + momentum-exposure-neutral OCF sleeve (research-grade).

Main signal: OCF-to-profit PIT (cash conversion), NOT cross-sectional momentum,
NOT textbook EP/BM, NOT resid×ETF-flow / friction / idx-rebal.

Exposure constraints (from AI_G1G5_EXPAND_EXPOSURE_DEEPENING_ZH.md §5):
  - SW L1 single-industry weight hard cap ≤28%; HHI monitor ≤0.18
  - Portfolio 20d excess-vs-510300 exposure target ≈0±1.5pp
  - Within-universe float_mktcap percentile band [0.35, 0.75]

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
    _load_sw_members,
    sw_code_on,
)
from research.g1g5_low_turnover_weights import estimate_daily_turnover  # noqa: E402

MECHANISM_TAG = "g1g5_ashare_indcap_momneut_ocf_v1"
UNIVERSE_ID = EXPAND_UNIVERSE_ID
DEFAULT_TOP_N = 50
DEFAULT_ACTIVE_N = 20
WEIGHT_START = "2024-01-02"
WEIGHT_END = "2026-10-09"
INDUSTRY_CAP = 0.28
HHI_ALARM = 0.18
MOM_CORRIDOR = 0.015  # ±1.5pp
SIZE_BAND = (0.35, 0.75)
MOM_LOOKBACK = 20
BALLAST_ETF = "510300.SH"
OCF_PIT = ROOT / "data" / "v2" / "financials_pit" / "ocf_to_profit_pit_daily_tushare.parquet"

WHO_PAYS_ZH = (
    "经营现金流相对净利润的兑现落差（OCF/利润PIT）在中大盘液态宇宙内被错误定价的对手盘"
    "支付本叶相对510300的持有窗；"
    "另受申万一级单行业硬顶与相对510300的20日超额强度暴露走廊中性化约束；"
    "明确排除截面相对强弱排序主轴、教科书EP/BM估值主轴、"
    "残差×份额流、ETF-core overlay、四臂摩擦与指数调仓流换皮。"
)


def _rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _forbid_tokens(tag: str, who: str) -> None:
    """Reject textbook mom/value and seven-fail isomorphism tokens in tag/who."""
    tag_l = tag.lower()
    for b in ("momentum", "mom_", "value", "quality", "价值", "动量"):
        if b in tag_l or b in tag:
            raise RuntimeError(f"textbook_token_forbidden_in_mechanism_tag:{b!r}")
    if "动量" in who:
        raise RuntimeError("who_pays_zh must not contain 动量 as main narrative token")
    # soft: who may mention 超额强度暴露 as constraint, not 动量
    for bad in ("残差×份额", "四臂", "调仓流", "etf_core"):
        if bad in tag_l:
            raise RuntimeError(f"failed_pack_token_in_tag:{bad!r}")


def _preload_close_matrix(instruments: Sequence[str]) -> pd.DataFrame:
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


def _load_ocf_panel(
    instruments: Sequence[str],
    sessions: Sequence[str],
) -> pd.DataFrame:
    """Compact OCF panel for universe × rebalance window (RAM-light via pyarrow)."""
    if not OCF_PIT.exists():
        raise RuntimeError(f"missing OCF PIT: {OCF_PIT}")
    import pyarrow.dataset as ds
    import pyarrow.compute as pc

    want = list(instruments)
    s0 = pd.Timestamp(min(str(s)[:10] for s in sessions)) - pd.Timedelta(days=5)
    s1 = pd.Timestamp(max(str(s)[:10] for s in sessions))
    cols = ["trade_date", "ts_code", "ocf_to_profit", "np_negative", "denom_small"]
    dataset = ds.dataset(str(OCF_PIT), format="parquet")
    # push down ts_code + date range when possible
    filt = pc.field("ts_code").isin(want)
    try:
        table = dataset.to_table(columns=cols, filter=filt)
        df = table.to_pandas()
        del table
    except Exception:
        df = pd.read_parquet(OCF_PIT, columns=cols)
        df = df[df["ts_code"].isin(want)]
    df = df.copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.tz_localize(None).dt.normalize()
    df = df[(df["trade_date"] >= s0) & (df["trade_date"] <= s1)]
    df["ocf_to_profit"] = pd.to_numeric(df["ocf_to_profit"], errors="coerce")
    for c in ("np_negative", "denom_small"):
        if c in df.columns:
            df[c] = df[c].fillna(False).astype(bool)
        else:
            df[c] = False
    df = df.sort_values(["ts_code", "trade_date"])
    return df.reset_index(drop=True)


def ocf_score_on(
    session: str,
    instruments: Sequence[str],
    ocf: pd.DataFrame,
) -> dict[str, float]:
    """Latest PIT ocf_to_profit ≤ session for each instrument; skip bad flags."""
    sess = pd.Timestamp(str(session)[:10]).normalize()
    out: dict[str, float] = {}
    if ocf.empty:
        return out
    sub = ocf[ocf["trade_date"] <= sess]
    if sub.empty:
        return out
    # last row per code
    last = sub.groupby("ts_code", sort=False).tail(1)
    for _, row in last.iterrows():
        code = str(row["ts_code"])
        if code not in instruments:
            continue
        if bool(row.get("np_negative")) or bool(row.get("denom_small")):
            continue
        v = float(row["ocf_to_profit"])
        if not np.isfinite(v):
            continue
        out[code] = v
    return out


def trailing_excess_at(
    closes: pd.DataFrame,
    bench: pd.Series,
    instrument: str,
    session: pd.Timestamp,
    lookback: int = MOM_LOOKBACK,
) -> float | None:
    if instrument not in closes.columns:
        return None
    ser = closes[instrument].dropna()
    sess = pd.Timestamp(session).normalize()
    hist = ser[ser.index <= sess]
    bh = bench[bench.index <= sess]
    if len(hist) < lookback + 1 or len(bh) < lookback + 1:
        return None
    if pd.Timestamp(hist.index[-1]).normalize() != sess:
        return None
    # align on common last lookback+1 sessions of instrument
    idx = hist.index[-(lookback + 1) :]
    common = idx.intersection(bh.index)
    if len(common) < lookback + 1:
        # use bench asof last available ≤ each
        px0, px1 = float(hist.iloc[-(lookback + 1)]), float(hist.iloc[-1])
        b_hist = bh.iloc[-(lookback + 1) :]
        if len(b_hist) < lookback + 1:
            return None
        b0, b1 = float(b_hist.iloc[0]), float(b_hist.iloc[-1])
    else:
        h = hist.loc[common]
        b = bh.loc[common]
        px0, px1 = float(h.iloc[0]), float(h.iloc[-1])
        b0, b1 = float(b.iloc[0]), float(b.iloc[-1])
    if min(px0, b0) <= 0 or not all(np.isfinite([px0, px1, b0, b1])):
        return None
    return (px1 / px0 - 1.0) - (b1 / b0 - 1.0)


def size_band_filter(
    mktcaps: dict[str, float],
    eligible: Sequence[str],
    lo: float = SIZE_BAND[0],
    hi: float = SIZE_BAND[1],
) -> list[str]:
    caps = {i: mktcaps[i] for i in eligible if i in mktcaps and mktcaps[i] > 0}
    if len(caps) < 8:
        return list(eligible)
    ser = pd.Series(caps)
    pct = ser.rank(pct=True, method="average")
    return [i for i in eligible if i in pct.index and lo <= float(pct.loc[i]) <= hi]


def greedy_select_with_industry_cap(
    ranked: list[tuple[str, float]],
    *,
    sw_map: dict[str, str],
    active_n: int,
    industry_cap: float = INDUSTRY_CAP,
) -> list[str]:
    """Greedy by score; skip if adding would push final industry EW weight > cap.

    Cap is evaluated vs target active_n (cnt/active_n), NOT progressive fill weight
    (which would reject the first name at 100%).
    """
    selected: list[str] = []
    ind_count: dict[str, int] = {}
    # max names per industry under EW of active_n
    max_per_ind = max(1, int(float(industry_cap) * float(active_n) + 1e-12))
    for inst, _score in ranked:
        if len(selected) >= int(active_n):
            break
        ind = sw_map.get(inst) or "_UNK"
        cnt = ind_count.get(ind, 0) + 1
        if cnt > max_per_ind:
            continue
        # also enforce weight cap if we stop early with n < active_n
        n_after = len(selected) + 1
        if (cnt / float(n_after)) > float(industry_cap) + 1e-12 and n_after >= max_per_ind + 1:
            # only bind progressive when basket already large enough that one more same-ind exceeds cap
            continue
        selected.append(inst)
        ind_count[ind] = cnt
    return selected


def neutralize_mom_exposure(
    weights: dict[str, float],
    excess: dict[str, float],
    *,
    corridor: float = MOM_CORRIDOR,
    max_tilt: float = 0.35,
) -> tuple[dict[str, float], dict[str, Any]]:
    """Tilt within basket so weighted excess ≈0±corridor; preserve sum & non-neg."""
    meta: dict[str, Any] = {"status": "ok", "corridor": corridor}
    names = [k for k, v in weights.items() if v > 0 and k != BALLAST_ETF]
    if not names:
        meta["status"] = "empty"
        return dict(weights), meta
    w = np.array([weights[n] for n in names], dtype=float)
    ex = np.array([float(excess.get(n, 0.0)) for n in names], dtype=float)
    # missing excess → 0
    for i, n in enumerate(names):
        if n not in excess:
            ex[i] = 0.0
    port0 = float(np.dot(w, ex) / max(w.sum(), 1e-12))
    meta["exposure_before"] = port0
    if abs(port0) <= corridor:
        meta["tilted"] = False
        meta["exposure_after"] = port0
        return dict(weights), meta

    # Soft tilt: w' ∝ w * (1 - k * sign(port) * z(ex))
    z = ex - ex.mean()
    sd = float(z.std()) if len(z) > 1 else 0.0
    if sd < 1e-12:
        meta["tilted"] = False
        meta["exposure_after"] = port0
        meta["reason"] = "excess_degenerate"
        return dict(weights), meta
    z = z / sd
    # choose k so exposure moves toward 0; binary search k in [0, max_tilt]
    sign = 1.0 if port0 > 0 else -1.0
    lo_k, hi_k = 0.0, float(max_tilt)
    best = dict(weights)
    best_exp = port0
    for _ in range(16):
        k = 0.5 * (lo_k + hi_k)
        adj = 1.0 - sign * k * z
        adj = np.clip(adj, 0.15, 1.85)
        wn = w * adj
        if wn.sum() <= 0:
            hi_k = k
            continue
        wn = wn / wn.sum() * w.sum()
        exp = float(np.dot(wn, ex) / max(wn.sum(), 1e-12))
        best = {names[i]: float(wn[i]) for i in range(len(names))}
        best_exp = exp
        if abs(exp) <= corridor:
            break
        # if still same sign as port0, increase k; else decrease
        if (exp > 0 and port0 > 0) or (exp < 0 and port0 < 0):
            lo_k = k
        else:
            hi_k = k
    out = dict(weights)
    for n in names:
        out[n] = best.get(n, 0.0)
    # preserve ballast
    if BALLAST_ETF in weights:
        out[BALLAST_ETF] = float(weights[BALLAST_ETF])
    # renormalize all positive to 1
    s = sum(max(0.0, v) for v in out.values())
    if s > 0:
        out = {k: max(0.0, v) / s for k, v in out.items()}
    meta["tilted"] = True
    meta["exposure_after"] = best_exp
    meta["tilt_k"] = float(0.5 * (lo_k + hi_k))
    return out, meta


def industry_hhi(weights: dict[str, float], sw_map: dict[str, str]) -> float:
    by: dict[str, float] = {}
    for k, v in weights.items():
        if v <= 0 or k == BALLAST_ETF:
            continue
        ind = sw_map.get(k) or "_UNK"
        by[ind] = by.get(ind, 0.0) + float(v)
    s = sum(by.values())
    if s <= 0:
        return 0.0
    return float(sum((v / s) ** 2 for v in by.values()))


def build_rebalance_decisions(
    instruments: Sequence[str],
    rebalance_sessions: Sequence[str],
    *,
    closes: pd.DataFrame,
    ocf: pd.DataFrame,
    active_n: int = DEFAULT_ACTIVE_N,
    use_pit_membership: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sw = _load_sw_members()
    mktcap_by_sess = _load_mktcap_on_sessions(instruments, rebalance_sessions)
    member_index = None
    if use_pit_membership:
        member_index = _load_pit_member_index(instruments, rebalance_sessions)
    bench = _load_benchmark_closes("510300")
    bench.index = pd.to_datetime(bench.index).tz_localize(None).normalize()

    arm_logs: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    # track instruments that ever appear (for expand builder) + ballast
    all_names = list(instruments)
    if BALLAST_ETF not in all_names:
        all_names = list(all_names) + [BALLAST_ETF]

    for sess in rebalance_sessions:
        eligible = list(instruments)
        if use_pit_membership:
            present = mid_large_members_on(sess, instruments, member_index=member_index)
            eligible = [i for i in instruments if i in present]

        mcaps = mktcap_by_sess.get(str(sess)[:10], {})
        banded = size_band_filter(mcaps, eligible)
        scores = ocf_score_on(sess, banded, ocf)
        # winsor cross-section
        if scores:
            arr = np.array(list(scores.values()), dtype=float)
            lo_v, hi_v = np.nanpercentile(arr, [2.5, 97.5])
            scores = {k: float(np.clip(v, lo_v, hi_v)) for k, v in scores.items()}

        sess_ts = pd.Timestamp(str(sess)[:10]).normalize()
        sw_map: dict[str, str] = {}
        for inst in banded:
            code = sw_code_on(inst, sess_ts, sw)
            if code:
                sw_map[inst] = code

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected = greedy_select_with_industry_cap(
            ranked, sw_map=sw_map, active_n=active_n, industry_cap=INDUSTRY_CAP
        )

        # fallback if too few scored: fill from banded by mktcap mid (stability, not mom)
        if len(selected) < max(5, active_n // 4):
            rest = [i for i in banded if i not in selected]
            rest_sorted = sorted(rest, key=lambda x: mcaps.get(x, 0.0), reverse=True)
            for inst in rest_sorted:
                if len(selected) >= active_n:
                    break
                # still respect industry cap
                trial = greedy_select_with_industry_cap(
                    [(s, scores.get(s, 0.0)) for s in selected + [inst]],
                    sw_map=sw_map,
                    active_n=active_n,
                    industry_cap=INDUSTRY_CAP,
                )
                if inst in trial:
                    selected = trial

        n = len(selected)
        if n == 0:
            target = {BALLAST_ETF: 1.0}
            mom_meta = {"status": "all_ballast"}
            hhi = 0.0
        else:
            each = 1.0 / float(n)
            target = {inst: each for inst in selected}
            # excess map for selected
            excess: dict[str, float] = {}
            for inst in selected:
                ex = trailing_excess_at(closes, bench, inst, sess_ts, MOM_LOOKBACK)
                if ex is not None:
                    excess[inst] = float(ex)
            target, mom_meta = neutralize_mom_exposure(target, excess, corridor=MOM_CORRIDOR)
            hhi = industry_hhi(target, sw_map)

        arm_logs.append(
            {
                "session": sess,
                "n_eligible": len(eligible),
                "n_banded": len(banded),
                "n_scored": len(scores),
                "n_selected": n,
                "hhi": hhi,
                "hhi_alarm": bool(hhi > HHI_ALARM),
                "mom": mom_meta,
                "top_inds": _top_industries(target, sw_map, 5),
            }
        )

        active_set = {k for k, v in target.items() if v > 0 and k != BALLAST_ETF}
        for inst in all_names:
            if inst == BALLAST_ETF:
                w = float(target.get(BALLAST_ETF, 0.0))
                rating = "Hold" if w > 0 else "Abstain"
            elif inst in active_set:
                w = float(target.get(inst, 0.0))
                rating = "Overweight"
            elif inst in scores:
                w = 0.0
                rating = "Underweight"
            else:
                w = 0.0
                rating = "Abstain"
            decisions.append(
                {
                    "instrument": inst,
                    "session": sess,
                    "rating": rating,
                    "target_weight_override": w,
                    "ocf_score": scores.get(inst),
                    "selection_rule": "ocf_pit_indcap_momneut_ew",
                }
            )

    return decisions, {
        "rebalance_arm_logs": arm_logs,
        "industry_cap": INDUSTRY_CAP,
        "hhi_alarm": HHI_ALARM,
        "mom_corridor": MOM_CORRIDOR,
        "size_band": list(SIZE_BAND),
        "active_n": active_n,
    }


def _top_industries(
    weights: dict[str, float], sw_map: dict[str, str], k: int
) -> list[dict[str, Any]]:
    by: dict[str, float] = {}
    for name, w in weights.items():
        if w <= 0 or name == BALLAST_ETF:
            continue
        ind = sw_map.get(name) or "_UNK"
        by[ind] = by.get(ind, 0.0) + float(w)
    items = sorted(by.items(), key=lambda x: x[1], reverse=True)[:k]
    return [{"sw_code": a, "weight": round(b, 4)} for a, b in items]


def _jaccard_vs_packs(
    weights: pd.DataFrame,
    rebal: Sequence[str],
) -> dict[str, Any]:
    packs = {
        "expand": ROOT / "output" / "intel" / "g1g5_expand_daily_weights_20261012_111354.parquet",
        "nontextbook": ROOT / "output" / "intel" / "g1g5_nontextbook_daily_weights_20261012_111316.parquet",
        "lowturn": ROOT / "output" / "intel" / "g1g5_lowturn_daily_weights_20261012_112301.parquet",
        "resid_etf": ROOT / "output" / "ai_factory" / "g1g5_resid_etf_daily_weights_20261013_002418.parquet",
        "etf_core": ROOT / "output" / "ai_factory" / "g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet",
        "friction_cost": ROOT
        / "output"
        / "ai_factory"
        / "g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet",
        "idx_rebal": ROOT
        / "output"
        / "ai_factory"
        / "g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet",
    }
    sample = [x for x in rebal if x >= "2024-03-01"][:6]
    vs: dict[str, Any] = {}
    for label, path in packs.items():
        entry: dict[str, Any] = {
            "path": str(path.relative_to(ROOT)) if path.exists() else None
        }
        if not path.exists():
            vs[label] = entry
            continue
        old = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
        diffs = []
        jacs = []
        for ss in sample:
            a = set(
                weights[
                    (weights["date"] == ss)
                    & (weights["target_weight"] > 0)
                    & (weights["instrument"] != BALLAST_ETF)
                ]["instrument"]
            )
            b = set(
                old[
                    (old["date"] == ss)
                    & (old["target_weight"] > 0)
                    & (old["instrument"] != BALLAST_ETF)
                    & (~old["instrument"].astype(str).str.startswith("5"))
                ]["instrument"]
            )
            # etf_core is mostly ETFs — compare raw positive set excluding 510300
            if label == "etf_core":
                b = set(
                    old[
                        (old["date"] == ss)
                        & (old["target_weight"] > 0)
                        & (old["instrument"] != BALLAST_ETF)
                    ]["instrument"]
                )
            jac = (len(a & b) / len(a | b)) if (a or b) else None
            if jac is not None:
                jacs.append(jac)
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
        entry["jaccard_mean"] = float(np.mean(jacs)) if jacs else None
        entry["jaccard_max"] = float(np.max(jacs)) if jacs else None
        vs[label] = entry
    return vs


def run_indcap_momneut_ocf(
    *,
    top_n: int = DEFAULT_TOP_N,
    active_n: int = DEFAULT_ACTIVE_N,
    weight_start: str = WEIGHT_START,
    weight_end: str = WEIGHT_END,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    max_debate_rounds: int = 1,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    _forbid_tokens(MECHANISM_TAG, WHO_PAYS_ZH)
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

    ocf = _load_ocf_panel(instruments, rebal)
    decisions, score_meta = build_rebalance_decisions(
        instruments,
        rebal,
        closes=closes,
        ocf=ocf,
        active_n=active_n,
        use_pit_membership=True,
    )
    del ocf  # free

    weights = build_daily_weights_expand(
        decisions,
        start=weight_start,
        end=weight_end,
        mechanism_tag=MECHANISM_TAG,
        who_pays_zh=WHO_PAYS_ZH,
        universe_id=UNIVERSE_ID,
    )
    # drop pure-zero ballast rows? keep contract: all decided instruments
    # ensure daily sum ≈ 1
    daily_sum = weights.groupby("date")["target_weight"].sum()
    if float(daily_sum.min()) < 0.98 or float(daily_sum.max()) > 1.02:
        # renormalize per day
        weights = weights.copy()
        weights["target_weight"] = weights.groupby("date")["target_weight"].transform(
            lambda x: x / x.sum() if float(x.sum()) > 0 else x
        )
        weights["weight"] = weights["target_weight"]
        daily_sum = weights.groupby("date")["target_weight"].sum()

    if weights["who_pays_zh"].astype(str).str.contains("动量").any():
        raise RuntimeError("who_pays contains 动量")
    if weights["mechanism_tag"].astype(str).str.contains(
        "momentum|mom_|value|quality|价值", case=False, regex=True
    ).any():
        raise RuntimeError("mechanism_tag contains textbook token")

    tow = estimate_daily_turnover(weights)
    vs = _jaccard_vs_packs(weights, rebal)

    wpath = out_dir / f"g1g5_indcap_momneut_ocf_daily_weights_{stamp}.parquet"
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

    ledger_path = out_dir / f"debate_ledger_g1g5_indcap_momneut_ocf_{stamp}.jsonl"
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
    peak = _rss_kb()
    cov = coverage_report(list(instruments))
    clear_caches()

    # exposure summary from arm logs
    hhis = [x.get("hhi") for x in score_meta.get("rebalance_arm_logs") or [] if x.get("hhi") is not None]
    mom_after = [
        (x.get("mom") or {}).get("exposure_after")
        for x in score_meta.get("rebalance_arm_logs") or []
        if (x.get("mom") or {}).get("exposure_after") is not None
    ]

    meta = {
        "mode": "g1g5_indcap_momneut_ocf",
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
        "daily_gross_mean": float(daily_sum.mean()) if len(daily_sum) else None,
        "daily_gross_min": float(daily_sum.min()) if len(daily_sum) else None,
        "daily_gross_max": float(daily_sum.max()) if len(daily_sum) else None,
        "turnover_daily": tow,
        "vs_prior_packs": vs,
        "exposure_summary": {
            "hhi_mean": float(np.mean(hhis)) if hhis else None,
            "hhi_max": float(np.max(hhis)) if hhis else None,
            "hhi_alarm_rate": float(np.mean([h > HHI_ALARM for h in hhis])) if hhis else None,
            "mom_exposure_after_mean": float(np.mean(mom_after)) if mom_after else None,
            "mom_exposure_after_abs_mean": float(np.mean(np.abs(mom_after))) if mom_after else None,
            "industry_cap": INDUSTRY_CAP,
            "mom_corridor": MOM_CORRIDOR,
            "size_band": list(SIZE_BAND),
        },
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "column_contract_version_qm_alias": COLUMN_CONTRACT_VERSION_QM_ALIAS,
        "hard_gate_version": HARD_GATE_VERSION,
        "ai_columns": ["date", "instrument", "target_weight"],
        "alpha_authoritative_aliases": ["session", "instrument_id", "weight"],
        "mechanism_tag": MECHANISM_TAG,
        "who_pays_zh": WHO_PAYS_ZH,
        "who_pays_prereg": "docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WHO_PAYS_PREREG_ZH.md",
        "universe_id": UNIVERSE_ID,
        "universe_kind": UNIVERSE_KIND,
        "universe_select": uni,
        "mechanism_definition_zh": {
            "ocf_pit": "ocf_to_profit PIT（排除 np_negative/denom_small；截面 winsor）",
            "industry_cap": f"申万一级单行业硬顶 ≤{INDUSTRY_CAP:.0%}；贪婪选股跳过超顶",
            "mom_neutral": f"篮内倾斜使 20d 超额暴露落入 ±{MOM_CORRIDOR:.1%}；非动量选股",
            "size_band": f"包内 float_mktcap 分位 ∈[{SIZE_BAND[0]}, {SIZE_BAND[1]}]",
            "selection": f"月频 top{active_n}；覆盖不足→510300 压舱",
            "orthogonality_zh": (
                "相对七败：无动量排序、无四臂、无残差×份额、无 ETF-core、无调仓事件主轴"
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

    meta_path = out_dir / f"g1g5_indcap_momneut_ocf_run_meta_{stamp}.json"
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
        "selection_rule": "ocf_pit_indcap_momneut_top20",
        "role_zh": "行业硬顶+动量暴露中性·OCF兑现（研究级）",
        "peak_rss_mb": meta["peak_rss_mb"],
        "g6": (g6_proof or {}).get("G6"),
        "vs_jaccard_mean": {
            k: v.get("jaccard_mean") for k, v in vs.items() if isinstance(v, dict)
        },
        "exposure_summary": meta["exposure_summary"],
    }
    side_path = Path(str(wpath) + ".meta.json")
    side_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    meta["weights_meta_path"] = str(side_path.relative_to(ROOT))
    meta["meta_path"] = str(meta_path.relative_to(ROOT))
    return meta


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="G1G5 indcap+momneut OCF X2 weights")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--active-n", type=int, default=DEFAULT_ACTIVE_N)
    ap.add_argument("--horizon-days", type=int, default=5)
    ap.add_argument("--max-debate-rounds", type=int, default=1)
    ap.add_argument("--weight-start", default=WEIGHT_START)
    ap.add_argument("--weight-end", default=WEIGHT_END)
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        meta = run_indcap_momneut_ocf(
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
    slim["turnover"] = meta.get("turnover_daily")
    slim["exposure_summary"] = meta.get("exposure_summary")
    slim["vs_jaccard"] = {
        k: {"mean": v.get("jaccard_mean"), "max": v.get("jaccard_max")}
        for k, v in (meta.get("vs_prior_packs") or {}).items()
        if isinstance(v, dict)
    }
    print(json.dumps(slim, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
