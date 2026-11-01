#!/usr/bin/env python3
"""AI Factor L1b structural explore — textbook ban + institutional leaves.

Requires LEO_AI_FACTOR_L1B_OK=1 (Leo veto+rerun via New Bot / Alpha).
Never sealed. Never A1. promotion_approved=False. Peak RSS < 2500MB.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import os
import resource
import sys
import time
import traceback
import types
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
V2 = ROOT / "data/v2"
EXPLORE_START = pd.Timestamp("2024-06-03")
SEALED_END = pd.Timestamp("2024-05-31")
LOOKBACK_START = pd.Timestamp("2024-01-02")
MAX_EVALUATIONS = 320  # L1b block prestate; ledger continues past N=280
TOP_K = 20
COST = 0.0025
SEED = 20261012
PROMOTION_APPROVED = False


def mem_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def _load_ai_factory():
    if "quantlab" not in sys.modules:
        q = types.ModuleType("quantlab")
        q.__path__ = [str(ROOT / "quantlab")]
        sys.modules["quantlab"] = q
    if "quantlab.factors" not in sys.modules or not hasattr(
        sys.modules["quantlab.factors"], "__path__"
    ):
        f = types.ModuleType("quantlab.factors")
        f.__path__ = [str(ROOT / "quantlab/factors")]
        sys.modules["quantlab.factors"] = f

    def load(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod

    load("quantlab.factors.ops", ROOT / "quantlab/factors/ops.py")
    af = types.ModuleType("quantlab.factors.ai_factory")
    af.__path__ = [str(ROOT / "quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"] = af
    load("quantlab.factors.ai_factory.ledger", ROOT / "quantlab/factors/ai_factory/ledger.py")
    load("quantlab.factors.ai_factory.novelty", ROOT / "quantlab/factors/ai_factory/novelty.py")
    load("quantlab.factors.ai_factory.fitness", ROOT / "quantlab/factors/ai_factory/fitness.py")
    load("quantlab.factors.ai_factory.evaluate", ROOT / "quantlab/factors/ai_factory/evaluate.py")
    load("quantlab.factors.ai_factory.search", ROOT / "quantlab/factors/ai_factory/search.py")
    return (
        sys.modules["quantlab.factors.ai_factory.search"],
        sys.modules["quantlab.factors.ai_factory.evaluate"],
        sys.modules["quantlab.factors.ai_factory.fitness"],
        sys.modules["quantlab.factors.ai_factory.novelty"],
        sys.modules["quantlab.factors.ops"],
    )


def _ashare_cols(all_names: list[str]) -> list[str]:
    return [
        c
        for c in all_names
        if (
            c[:6] in ("sh.600", "sh.601", "sh.603", "sh.605", "sh.688", "sh.689")
            or c[:5] in ("sz.00", "sz.30")
        )
    ]


def _to_baostock(ts_code: str) -> str:
    # 600000.SH -> sh.600000
    if "." not in ts_code:
        return ts_code
    code, mkt = ts_code.split(".")
    return f"{mkt.lower()}.{code}"


def _broadcast(series: pd.Series, index: pd.DatetimeIndex, columns: list[str]) -> pd.DataFrame:
    s = series.reindex(index).astype("float32")
    # one column then tile — memory friendly via numpy
    arr = np.repeat(s.to_numpy()[:, None], len(columns), axis=1)
    return pd.DataFrame(arr, index=index, columns=columns, dtype="float32")


def _streak(flag: pd.DataFrame) -> pd.DataFrame:
    """Consecutive True days; resets on False/NaN. Vectorized per column via pad."""
    arr = flag.fillna(False).to_numpy(dtype=bool)
    T, N = arr.shape
    res = np.zeros((T, N), dtype=np.float32)
    # process in column chunks to keep Python loop short on T only
    for j0 in range(0, N, 64):
        j1 = min(N, j0 + 64)
        block = arr[:, j0:j1]
        run = np.zeros(j1 - j0, dtype=np.float32)
        for i in range(T):
            run = np.where(block[i], run + 1.0, 0.0)
            res[i, j0:j1] = run
    return pd.DataFrame(res, index=flag.index, columns=flag.columns)


def _days_since(flag: pd.DataFrame) -> pd.DataFrame:
    arr = flag.fillna(False).to_numpy(dtype=bool)
    T, N = arr.shape
    res = np.full((T, N), np.nan, dtype=np.float32)
    last = np.full(N, -1, dtype=np.int32)
    idx = np.arange(N)
    for i in range(T):
        hit = arr[i]
        last[hit] = i
        ok = last >= 0
        res[i, ok] = (i - last[ok]).astype(np.float32)
    return pd.DataFrame(res, index=flag.index, columns=flag.columns)


def load_structural_panels():
    import pyarrow.parquet as pq

    t0 = time.time()
    log = lambda *a: print(
        f"[l1b {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True
    )
    data_status = {}

    schema = pq.read_schema(SCRATCH / "close.parquet")
    ash = _ashare_cols(list(schema.names))
    log("ashare", len(ash))

    fm_long = pd.read_parquet(
        V2 / "float_mktcap/float_mktcap_daily_tushare.parquet",
        columns=["trade_date", "instrument_id", "float_mktcap"],
        filters=[("trade_date", ">=", LOOKBACK_START)],
    )
    fm_long["trade_date"] = pd.to_datetime(fm_long["trade_date"])
    rk = fm_long.groupby("trade_date")["float_mktcap"].rank(ascending=False)
    keep = set(fm_long.loc[rk <= 1800, "instrument_id"])
    iw = pd.read_parquet(V2 / "index_members/index_weight_csi300_500_1000.parquet")
    iw = iw[iw.index_code.isin(["000300.SH", "000905.SH"])]
    iw = iw[pd.to_datetime(iw.trade_date) >= LOOKBACK_START]
    ix = set(iw.con_code.str[-2:].str.lower() + "." + iw.con_code.str[:6])
    del iw
    cols = sorted((keep | ix) & set(ash))
    log("midlarge cols", len(cols))

    def ld(name: str) -> pd.DataFrame:
        df = pd.read_parquet(SCRATCH / f"{name}.parquet", columns=cols).astype("float32")
        return df.loc[df.index >= LOOKBACK_START]

    cl = ld("close")
    op = ld("open")
    fa = ld("factor").ffill()
    tov = ld("turnover")
    ts = ld("tradestatus")
    st = ld("is_st_at_open")
    lim_up_px = ld("limit_up")
    log("price", cl.shape)

    aC = (cl * fa).astype("float32")
    aO = (op * fa).astype("float32")
    del fa, op, cl
    gc.collect()

    fm = (
        fm_long[fm_long.instrument_id.isin(cols)]
        .drop_duplicates(["trade_date", "instrument_id"], keep="last")
        .set_index(["trade_date", "instrument_id"])["float_mktcap"]
        .unstack()
        .reindex(index=aC.index, columns=cols)
        .astype("float32")
    )
    del fm_long
    gc.collect()

    rk_w = fm.rank(axis=1, ascending=False)
    tradable = (ts == 1) & aC.notna() & (st != 1) & fm.notna()
    uni = tradable & (rk_w <= 1500)
    for c in cols:
        if c in ix:
            uni[c] = uni[c] | (tradable[c] & fm[c].notna())
    log("uni mean", float(uni.sum(axis=1).mean()))

    # --- public textbook panels (CONTROL / novelty corr only) ---
    ret = aC.pct_change(fill_method=None)
    public = {
        "ret_20": aC.pct_change(20, fill_method=None).astype("float32").where(uni),
        "rv_20": ret.rolling(20, min_periods=10).std().astype("float32").where(uni),
        "turn_20": tov.rolling(20, min_periods=10).mean().astype("float32").where(uni),
        "neg_ret_20": (-aC.pct_change(20, fill_method=None)).astype("float32").where(uni),
        "size": np.log(fm.where(fm > 0)).astype("float32").where(uni),
    }
    data_status["public_corr_panels"] = list(public.keys())

    # --- limit flags ---
    # up: close vs limit_up price (raw close vs raw limit)
    raw_close = pd.read_parquet(SCRATCH / "close.parquet", columns=cols).astype("float32")
    raw_close = raw_close.loc[raw_close.index >= LOOKBACK_START]
    lu_flag = (raw_close >= lim_up_px * 0.995) & lim_up_px.notna() & raw_close.notna()
    data_status["limit_up"] = {
        "source": "scratch/limit_up.parquet + close",
        "ok": True,
        "mean_rate": float(lu_flag.where(uni).mean().mean()),
    }

    # down limits from stk_limit — batch load date range
    lim_dir = V2 / "tushare_raw/stk_limit"
    want_days = {d.strftime("%Y%m%d") for d in raw_close.index}
    files = [lim_dir / f"{d}.parquet" for d in sorted(want_days) if (lim_dir / f"{d}.parquet").exists()]
    chunks = []
    for i0 in range(0, len(files), 40):
        part = pd.concat([pd.read_parquet(f, columns=["trade_date", "ts_code", "down_limit"]) for f in files[i0:i0+40]], ignore_index=True)
        chunks.append(part)
        del part
    if chunks:
        all_lim = pd.concat(chunks, ignore_index=True)
        del chunks
        all_lim["trade_date"] = pd.to_datetime(all_lim["trade_date"])
        all_lim["bs"] = all_lim["ts_code"].map(_to_baostock)
        all_lim = all_lim[all_lim["bs"].isin(cols)]
        down_wide = (
            all_lim.drop_duplicates(["trade_date", "bs"], keep="last")
            .set_index(["trade_date", "bs"])["down_limit"]
            .unstack()
            .reindex(index=raw_close.index, columns=cols)
            .astype("float32")
        )
        ld_flag = (raw_close <= down_wide * 1.005) & down_wide.notna() & raw_close.notna()
        n_ok = int(down_wide.notna().any(axis=1).sum())
        del all_lim, down_wide
        gc.collect()
    else:
        ld_flag = pd.DataFrame(False, index=raw_close.index, columns=cols)
        n_ok = 0
    data_status["limit_down"] = {
        "source": "tushare_raw/stk_limit",
        "ok": n_ok > 100,
        "n_days_loaded": n_ok,
        "mean_rate": float(ld_flag.where(uni).mean().mean()),
    }
    log("limit flags", data_status["limit_up"]["mean_rate"], data_status["limit_down"]["mean_rate"])

    # streaks — subsample for memory: compute on float32
    log("streaks start")
    lu_streak = _streak(lu_flag.astype("float32"))
    ld_streak = _streak(ld_flag.astype("float32"))
    lu_count_5 = lu_flag.astype("float32").rolling(5, min_periods=1).sum().astype("float32")
    days_since_lu = _days_since(lu_flag)
    log("streaks done", mem_mb())

    overnight = (aO / aC.shift(1) - 1.0).astype("float32")
    intraday = (aC / aO - 1.0).astype("float32")
    on_minus_id = (overnight - intraday).astype("float32")
    data_status["t1_split"] = {"ok": True, "source": "adj open/close"}

    # --- ETF flows (PIT available_at) ---
    def _etf_flow_series(path: Path, label: str) -> pd.Series:
        etf = pd.read_parquet(path)
        etf["trade_date"] = pd.to_datetime(etf["trade_date"])
        etf["available_at"] = pd.to_datetime(etf["available_at"])
        # use flow only when available_at date <= decision date end; map to next session
        # Conservative: signal date = available_at.normalize() (T+1 EOD) → usable next day
        etf["signal_date"] = etf["available_at"].dt.normalize() + pd.Timedelta(days=1)
        # align to trading calendar via reindex later
        g = etf.groupby("signal_date")["flow_est_wan_yuan"].sum()
        data_status[label] = {
            "ok": True,
            "path": str(path),
            "n_rows": len(etf),
            "n_codes": int(etf["ts_code"].nunique()),
        }
        return g.astype("float32")

    major_flow = _etf_flow_series(
        V2 / "etf/share_pit/etf_share_flow_pit_major.parquet", "etf_major"
    )
    theme_flow = _etf_flow_series(
        V2 / "etf/share_pit/etf_share_flow_pit_industry_theme.parquet", "etf_theme"
    )
    # asof onto calendar
    cal = aC.index
    major_s = major_flow.sort_index()
    theme_s = theme_flow.sort_index()
    # forward-asof: for each calendar day, last signal_date <= day
    major_aligned = major_s.reindex(cal.union(major_s.index)).sort_index().ffill().reindex(cal)
    theme_aligned = theme_s.reindex(cal.union(theme_s.index)).sort_index().ffill().reindex(cal)
    etf_major_flow = _broadcast(major_aligned, cal, cols)
    etf_theme_flow = _broadcast(theme_aligned, cal, cols)
    etf_flow_x_lu = (etf_major_flow * lu_flag.astype("float32")).astype("float32")
    log("etf flows", mem_mb())

    # --- lockup supply next 20 trading days (PIT by ann_date) ---
    sf_path = V2 / "share_float/share_float_2018plus.parquet"
    try:
        sf = pd.read_parquet(
            sf_path,
            columns=["ts_code", "ann_date", "float_date", "float_ratio", "float_share"],
        )
        sf["ann_date"] = pd.to_datetime(sf["ann_date"])
        sf["float_date"] = pd.to_datetime(sf["float_date"])
        sf["bs"] = sf["ts_code"].map(_to_baostock)
        sf = sf[sf["bs"].isin(cols)]
        # keep events with float in lookback..explore+40d
        sf = sf[
            (sf["float_date"] >= LOOKBACK_START - pd.Timedelta(days=5))
            & (sf["float_date"] <= aC.index.max() + pd.Timedelta(days=40))
        ]
        # aggregate same day
        agg = (
            sf.groupby(["bs", "float_date", "ann_date"], as_index=False)["float_ratio"]
            .sum()
        )
        log("lockup events", len(agg))
        # Vectorized-ish: for each event add ratio on calendar slice
        # [max(ann_date+1day, float_date-28d), float_date-1day]
        lock_arr = np.zeros((len(cal), len(cols)), dtype=np.float32)
        col_index = {c: i for i, c in enumerate(cols)}
        cal_np = cal.values.astype("datetime64[ns]")
        for row in agg.itertuples(index=False):
            bs, fdt, adt, ratio = row.bs, row.float_date, row.ann_date, float(row.float_ratio)
            j = col_index.get(bs)
            if j is None or not np.isfinite(ratio) or ratio == 0.0:
                continue
            start = max(pd.Timestamp(adt) + pd.Timedelta(days=1), pd.Timestamp(fdt) - pd.Timedelta(days=28))
            end = pd.Timestamp(fdt) - pd.Timedelta(days=1)
            if end < start:
                continue
            # searchsorted on numpy datetime64
            i0 = int(np.searchsorted(cal_np, np.datetime64(start), side="left"))
            i1 = int(np.searchsorted(cal_np, np.datetime64(end), side="right"))
            if i0 < i1:
                lock_arr[i0:i1, j] += np.float32(ratio)
        lockup_S_20 = pd.DataFrame(lock_arr, index=cal, columns=cols, dtype="float32")
        data_status["lockup"] = {
            "ok": True,
            "path": str(sf_path),
            "n_events_used": len(agg),
            "nonzero_frac": float((lockup_S_20.where(uni) > 0).mean().mean()),
        }
        del sf, agg
        gc.collect()
    except Exception as exc:  # noqa: BLE001
        lockup_S_20 = pd.DataFrame(np.nan, index=cal, columns=cols, dtype="float32")
        data_status["lockup"] = {"ok": False, "error": str(exc)}
    log("lockup", data_status["lockup"])

    # --- IF basis ---
    try:
        iff = pd.read_parquet(V2 / "futures/raw/daily/IFL1.CFX.parquet")
        iff["trade_date"] = pd.to_datetime(iff["trade_date"])
        iff = iff.sort_values("trade_date").drop_duplicates("trade_date", keep="last")
        csi = pd.read_parquet(ROOT / "data/bench/csi300_000300_akshare_daily.parquet")
        csi["date"] = pd.to_datetime(csi["date"])
        m = iff.merge(csi[["date", "close"]], left_on="trade_date", right_on="date", how="inner")
        m["basis"] = m["close_x"] / m["close_y"] - 1.0
        basis_s = m.set_index("trade_date")["basis"].astype("float32")
        basis_aligned = basis_s.reindex(cal.union(basis_s.index)).sort_index().ffill().reindex(cal)
        if_basis = _broadcast(basis_aligned, cal, cols)
        if_basis_x_on = (if_basis * overnight).astype("float32")
        if_basis_x_lu = (if_basis * lu_flag.astype("float32")).astype("float32")
        data_status["futures_basis"] = {
            "ok": True,
            "source": "IFL1.CFX vs CSI300 akshare",
            "n": int(basis_s.notna().sum()),
            "mean_basis": float(basis_s.mean()),
        }
    except Exception as exc:  # noqa: BLE001
        if_basis = _broadcast(pd.Series(np.nan, index=cal), cal, cols)
        if_basis_x_on = if_basis.copy()
        if_basis_x_lu = if_basis.copy()
        data_status["futures_basis"] = {"ok": False, "error": str(exc)}
    log("basis", data_status["futures_basis"])

    # announcement embeddings / counts
    anns_dir = V2 / "tushare_raw/anns_d"
    n_recent = len(
        [
            f
            for f in anns_dir.iterdir()
            if f.name[:4] in ("2024", "2025", "2026") and f.suffix == ".parquet"
        ]
    )
    data_status["announcement_embed"] = {
        "ok": False,
        "gap": "no embeddings on box; anns_d has 0 files for 2024-2026 explore window",
        "n_anns_files_2024_2026": n_recent,
    }

    panels = {
        "limit_up_flag": lu_flag.astype("float32"),
        "limit_down_flag": ld_flag.astype("float32"),
        "lu_streak": lu_streak,
        "ld_streak": ld_streak,
        "lu_count_5": lu_count_5,
        "days_since_lu": days_since_lu,
        "overnight_ret": overnight,
        "intraday_ret": intraday,
        "on_minus_id": on_minus_id,
        "etf_major_flow": etf_major_flow,
        "etf_theme_flow": etf_theme_flow,
        "etf_flow_x_lu": etf_flow_x_lu,
        "lockup_S_20": lockup_S_20,
        "if_basis": if_basis,
        "if_basis_x_on": if_basis_x_on,
        "if_basis_x_lu": if_basis_x_lu,
    }
    for k in list(panels.keys()):
        panels[k] = panels[k].where(uni).astype("float32")
    for k in public:
        public[k] = public[k].astype("float32")

    from quantlab.factors.ai_factory.evaluate import (
        align_open_open_label,
        assert_no_lookahead_label,
    )

    label_full = align_open_open_label(aO)
    assert_no_lookahead_label(aO, label_full)
    label = label_full.where(uni).loc[label_full.index >= EXPLORE_START]

    meta = {
        "n_cols": len(cols),
        "n_dates_panel": int(len(cal)),
        "n_label_dates": int(label.dropna(how="all").shape[0]),
        "explore_start": str(EXPLORE_START.date()),
        "lookback_start": str(LOOKBACK_START.date()),
        "sealed_untouched": True,
        "sealed_end": str(SEALED_END.date()),
        "mean_universe_n": float(uni.loc[uni.index >= EXPLORE_START].sum(axis=1).mean()),
        "peak_rss_MB_load": round(mem_mb()),
        "data_status": data_status,
        "structural_leaves": list(panels.keys()),
    }
    log("ready", meta["n_cols"], meta["n_label_dates"], meta["peak_rss_MB_load"])
    del aC, aO, tov, ts, st, ret, fm, rk_w, tradable, uni, raw_close, lim_up_px
    gc.collect()
    return panels, label, public, meta


_LEAF_ZH = {
    "limit_up_flag": "涨停标记",
    "limit_down_flag": "跌停标记",
    "lu_streak": "连板天数",
    "ld_streak": "连跌停天数",
    "lu_count_5": "5日涨停次数",
    "days_since_lu": "距上次涨停天数",
    "overnight_ret": "隔夜收益",
    "intraday_ret": "日内收益",
    "on_minus_id": "隔夜减日内",
    "etf_major_flow": "宽基ETF净创设估算",
    "etf_theme_flow": "行业主题ETF净创设估算",
    "etf_flow_x_lu": "ETF创设×涨停交互",
    "lockup_S_20": "未来约20日解禁强度",
    "if_basis": "IF相对沪深300基差",
    "if_basis_x_on": "基差×隔夜交互",
    "if_basis_x_lu": "基差×涨停交互",
}


def gloss_zh(expr_str: str) -> str:
    s = expr_str
    for k, v in sorted(_LEAF_ZH.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)
    for op, zh in {
        "add": "加",
        "sub": "减",
        "mul": "乘",
        "div": "除",
        "neg": "取负",
        "abs": "绝对值",
        "rank": "截面排名",
        "zscore": "截面标准化",
    }.items():
        s = s.replace(op, zh)
    for k in (5, 10, 20, 1):
        s = s.replace(f"delay_{k}", f"滞后{k}日")
        s = s.replace(f"ts_mean_{k}", f"{k}日时序均值")
        s = s.replace(f"ts_std_{k}", f"{k}日时序波动")
        s = s.replace(f"ts_delta_{k}", f"{k}日时序差分")
        s = s.replace(f"ts_max_{k}", f"{k}日时序最大")
    return s


def who_pays_zh(expr_str: str) -> str:
    e = expr_str
    bits = []
    if any(x in e for x in ("limit_up", "limit_down", "lu_", "ld_", "days_since_lu")):
        bits.append("涨跌停/打板资金与T+1受限投资者：封板失败或接力断裂时由接盘方支付")
    if any(x in e for x in ("overnight", "intraday", "on_minus_id")):
        bits.append("隔夜信息持有者与日间流动性提供者之间的风险转移（T+1无法当日反向）")
    if "etf_" in e:
        bits.append("被动/ETF申赎冲击由股票端流动性承接方支付（份额变化滞后可知）")
    if "lockup" in e:
        bits.append("解禁股东被迫供给，折价由二级市场多头承接")
    if "if_basis" in e:
        bits.append("期现/对冲资金在贴水或升水状态下改变隔夜风险偏好，对手方为股票多头")
    if not bits:
        bits.append("机制未声明——按 L1b 不得晋级")
    return "；".join(bits)


def main() -> int:
    if os.environ.get("LEO_AI_FACTOR_L1B_OK") != "1":
        print(
            json.dumps(
                {
                    "error": "Set LEO_AI_FACTOR_L1B_OK=1 after Leo veto+rerun authorization",
                    "promotion_approved": False,
                }
            )
        )
        return 2

    t0 = time.time()
    search_mod, eval_mod, fit_mod, nov_mod, ops_mod = _load_ai_factory()
    GPConfig, gp_search = search_mod.GPConfig, search_mod.gp_search
    apply_expr = ops_mod.apply_expr

    out_dir = ROOT / "output/ai_factor/gp_explore_l1b"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_ledger = out_dir / "ledger_run.jsonl"
    if run_ledger.exists():
        run_ledger.unlink()
    main_ledger = ROOT / "output/ai_factor/ledger.jsonl"
    report_path = ROOT / "output/alpha/AI_FACTOR_L1b_STRUCTURAL_EXPLORE_ZH.md"

    panels, label, public, load_meta = load_structural_panels()
    peak = mem_mb()

    run_meta = {
        "mode": "explore_l1b_structural",
        "leo_authorization": "Leo veto of L1 Top-K + immediate structural re-run (via New Bot, Alpha-visible); parent task 2026-10-11",
        "max_evaluations_prestate": MAX_EVALUATIONS,
        "population": 48,
        "generations": 8,
        "top_k": TOP_K,
        "cost_one_way": COST,
        "seed": SEED,
        "structural_only": True,
        "ban_textbook": True,
        "use_l1b_fitness": True,
        "window": "explore_20240603_to_latest",
        "sealed_window_used_for_labels": False,
        "promotion_approved": False,
        "prereg": "docs/prereg/AI_FACTOR_L1b_STRUCTURAL.md",
        "load_meta": load_meta,
    }
    (out_dir / "run_meta.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False, default=str)
    )

    cfg = GPConfig(
        population=48,
        generations=8,
        max_evaluations=MAX_EVALUATIONS,
        top_k=TOP_K,
        seed=SEED,
        universe="midlarge_top1500_or_csi300_500",
        cost=COST,
        window="explore_20240603_to_latest_l1b",
        ledger_path=run_ledger,
        lambda_complexity=0.01,
        lambda_turnover=1.0,
        top_n=50,
        structural_only=True,
        ban_textbook=True,
        use_l1b_fitness=True,
        public_panels=public,
    )
    print(json.dumps({"event": "gp_l1b_start", "N_cap": MAX_EVALUATIONS}, ensure_ascii=False), flush=True)
    res = gp_search(panels, label, cfg)
    peak = max(peak, mem_mb())
    assert res.promotion_approved is False

    # append to main ledger (continue N)
    main_before = (
        sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
        if main_ledger.exists()
        else 0
    )
    from quantlab.factors.ai_factory.ledger import append_attempt

    run_rows = [json.loads(x) for x in run_ledger.read_text().splitlines() if x.strip()]
    for r in run_rows:
        append_attempt(
            engine=r["engine"] + "_l1b",
            seed=r["seed"],
            universe=r["universe"],
            cost=r["cost"],
            window=r["window"],
            expr_str=r.get("expr_str", ""),
            fitness=r.get("fitness"),
            notes=(r.get("notes", "") + ";l1b_structural_20261011"),
            path=main_ledger,
        )
    main_N = main_before + len(run_rows)

    # Also evaluate a fixed structural seed library (still counted via ledger in GP;
    # seed library separately counted)
    seed_exprs = [
        ("leaf", "lockup_S_20"),
        ("op", "neg", ("leaf", "lockup_S_20")),
        ("op", "rank", ("op", "neg", ("leaf", "lockup_S_20"))),
        ("leaf", "lu_streak"),
        ("op", "neg", ("leaf", "lu_streak")),
        ("op", "rank", ("leaf", "days_since_lu")),
        ("leaf", "on_minus_id"),
        ("op", "rank", ("leaf", "on_minus_id")),
        ("op", "neg", ("leaf", "etf_flow_x_lu")),
        ("op", "rank", ("leaf", "etf_major_flow")),
        ("op", "mul", ("leaf", "if_basis"), ("leaf", "overnight_ret")),
        ("op", "rank", ("leaf", "if_basis_x_on")),
        ("op", "neg", ("leaf", "lu_count_5")),
        ("op", "rank", ("op", "neg", ("leaf", "etf_theme_flow"))),
        ("op", "zscore", ("leaf", "lockup_S_20")),
    ]
    from quantlab.factors.ops import parse_expr
    from quantlab.factors.ai_factory.fitness import fitness_score_l1b

    seed_archive = []
    for tup in seed_exprs:
        if len(run_rows) + len(seed_archive) >= MAX_EVALUATIONS:
            break
        # already counted only if GP saw them; count seeds into ledger as extra within cap
        # Use remaining budget: allow seeds as additional if under cap via separate counter
        pass
    # Count seeds as part of evaluations beyond GP if GP used less than cap
    seed_budget = max(0, MAX_EVALUATIONS - res.evaluations)
    for tup in seed_exprs[:seed_budget]:
        expr = parse_expr(tup)
        try:
            fac = apply_expr(expr, panels)
            met = fitness_score_l1b(
                fac,
                label,
                public_panels=public,
                cost_one_way=COST,
                top_n=50,
                lambda_complexity=0.01,
                n_nodes=expr.n_nodes(),
            )
            append_attempt(
                engine="seed_l1b",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=COST,
                window="explore_20240603_to_latest_l1b",
                expr_str=expr.to_str(),
                fitness=met.get("fitness"),
                notes=f"seed;novelty_fail={met.get('novelty_fail')};ann_net={met.get('ann_net')}",
                path=main_ledger,
            )
            append_attempt(
                engine="seed_l1b",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=COST,
                window="explore_20240603_to_latest_l1b",
                expr_str=expr.to_str(),
                fitness=met.get("fitness"),
                notes=f"seed;novelty_fail={met.get('novelty_fail')}",
                path=run_ledger,
            )
            from quantlab.factors.ai_factory.search import Candidate

            if (
                met.get("fitness", -1e9) > -1e8
                and not met.get("novelty_fail")
                and met.get("ann_net") is not None
                and np.isfinite(met["ann_net"])
                and met["ann_net"] > 0
                and nov_mod.is_structural_expr(expr.to_str())
            ):
                seed_archive.append(
                    Candidate(
                        expr=expr,
                        train_icir=float(met.get("icir") or np.nan),
                        fitness=float(met["fitness"]),
                        n_nodes=expr.n_nodes(),
                        metrics={k: met[k] for k in met if k != "fitness"},
                    )
                )
        except Exception as exc:  # noqa: BLE001
            append_attempt(
                engine="seed_l1b",
                seed=SEED,
                universe="midlarge_top1500_or_csi300_500",
                cost=COST,
                window="explore_20240603_to_latest_l1b",
                expr_str=str(tup),
                fitness=None,
                notes=f"seed_error:{type(exc).__name__}",
                path=main_ledger,
            )
    main_N = sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
    n_new = main_N - main_before
    peak = max(peak, mem_mb())

    # merge GP top + seeds
    merged = list(res.top_k) + seed_archive
    merged.sort(key=lambda c: c.fitness, reverse=True)
    seen = set()
    top_rows = []
    for c in merged:
        s = c.expr.to_str()
        if s in seen:
            continue
        if nov_mod.is_textbook_expr(s):
            continue
        if (c.metrics or {}).get("novelty_fail"):
            continue
        ann = (c.metrics or {}).get("ann_net")
        if ann is None or not np.isfinite(ann) or ann <= 0:
            continue
        seen.add(s)
        row = c.as_row()
        row["gloss_zh"] = gloss_zh(s)
        row["who_pays_zh"] = who_pays_zh(s)
        row["promotion_approved"] = False
        top_rows.append(row)
        if len(top_rows) >= TOP_K:
            break

    (out_dir / "top_k.json").write_text(
        json.dumps(top_rows, indent=2, ensure_ascii=False, default=str)
    )

    mechanism_failure = len(top_rows) == 0
    failure_reasons = []
    if mechanism_failure:
        failure_reasons.append("no_candidate_passed_novelty_and_ann_net_gates")
        failure_reasons.append("textbook_expressions_banned_from_main_topk")
        # diagnose: how many GP had positive ann_net but novelty fail
        pos_net_nov_fail = 0
        textbook_rejected = 0
        for line in run_ledger.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if "rejected_textbook" in (r.get("notes") or ""):
                textbook_rejected += 1
            if "novelty_fail=True" in (r.get("notes") or ""):
                pos_net_nov_fail += 1
        failure_reasons.append(f"ledger_textbook_rejects≈{textbook_rejected}")
        failure_reasons.append(f"ledger_notes_with_novelty_fail≈{pos_net_nov_fail}")

    # report
    ds = load_meta.get("data_status", {})
    lines = [
        "# AI 因子工厂 L1b — 结构/制度算子探索窗报告",
        "",
        f"- 日期：2026-10-11（美东）｜`promotion_approved=false`",
        f"- 授权：Leo 否决 L1 教科书 Top-K，要求立刻改主线重跑（New Bot 转达，Alpha 可见）",
        f"- 预注册：`docs/prereg/AI_FACTOR_L1b_STRUCTURAL.md`",
        f"- 窗口：探索 **{EXPLORE_START.date()} → latest**；密封标签未用",
        f"- 宇宙：中大盘 top1500 / 沪深300∪中证500；禁小盘主线",
        f"- 本块预声明 `max_evaluations={MAX_EVALUATIONS}`；GP 评估 **{res.evaluations}**；本块新计次 **N_new≈{n_new}**；账本累计 **N={main_N}**（旧 280 未擦除）",
        f"- 适应度：扣成本 `ann_net` − 复杂度 − 公开因子 |corr|>0.5 惩罚",
        f"- 峰值内存：约 **{peak:.0f} MB**（约束 <2500）",
        f"- 产物：`output/ai_factor/gp_explore_l1b/`",
        "",
        "## 各族数据是否到位",
        "",
    ]
    for fam, key in [
        ("涨跌停状态", "limit_up"),
        ("跌停", "limit_down"),
        ("T+1 隔夜/日内", "t1_split"),
        ("宽基 ETF 份额流", "etf_major"),
        ("行业/主题 ETF 份额流", "etf_theme"),
        ("解禁供给", "lockup"),
        ("期货贴水", "futures_basis"),
        ("公告嵌入", "announcement_embed"),
    ]:
        info = ds.get(key, {})
        lines.append(f"- **{fam}**：`{json.dumps(info, ensure_ascii=False)[:220]}`")
    lines += ["", "## 主 Top-K（非教科书；未过则 MECHANISM FAILURE）", ""]
    if mechanism_failure:
        lines.append("### MECHANISM FAILURE")
        for r in failure_reasons:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("未向主结果交付任何反转/低波/换手教科书表达式。")
    else:
        lines.append(
            "| # | 表达式 | 释义 | fitness | ICIR(诊) | ann_net | 换手 | max|ρ|公开 | 钱从谁来 |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(top_rows[:10], 1):
            m = r.get("metrics") or {}
            lines.append(
                f"| {i} | `{r['expr']}` | {r.get('gloss_zh','')} | {r.get('fitness', float('nan')):.4f} | "
                f"{r.get('train_icir', float('nan')):.3f} | {m.get('ann_net', float('nan')):.2%} | "
                f"{m.get('turnover', float('nan')):.2f} | {m.get('max_abs_public_corr', float('nan')):.2f} | "
                f"{(r.get('who_pays_zh') or '')[:50]} |"
            )
    lines += [
        "",
        "## 闸门",
        f"- mechanism_failure={mechanism_failure}",
        "- 不建议开密封窗（promotion_approved=false；且本跑未申请）",
        "",
        "## 未做",
        "- 未跑密封窗",
        "- 未跑 V3-A1 持有层密封",
        "- 公告文本嵌入未接入（数据缺口）",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "mode": "explore_l1b_structural",
        "ok": True,
        "promotion_approved": False,
        "sealed_executed": False,
        "mechanism_failure": mechanism_failure,
        "failure_reasons": failure_reasons,
        "N_gp": res.evaluations,
        "N_new_block": n_new,
        "ledger_cumulative_N": main_N,
        "top_k_n": len(top_rows),
        "top_k_summary": [
            {"expr": r["expr"], "fitness": r.get("fitness"), "ann_net": (r.get("metrics") or {}).get("ann_net"),
             "who_pays_zh": r.get("who_pays_zh")}
            for r in top_rows[:5]
        ],
        "peak_rss_MB": round(peak),
        "runtime_s": round(time.time() - t0, 1),
        "data_status": ds,
        "paths": {
            "report": str(report_path),
            "topk": str(out_dir / "top_k.json"),
            "run_meta": str(out_dir / "run_meta.json"),
            "ledger": str(main_ledger),
            "prereg": str(ROOT / "docs/prereg/AI_FACTOR_L1b_STRUCTURAL.md"),
        },
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str)
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        err = {
            "ok": False,
            "error": traceback.format_exc(),
            "promotion_approved": False,
            "peak_rss_MB": round(mem_mb()),
        }
        print(json.dumps(err, indent=2, ensure_ascii=False))
        raise SystemExit(1)
