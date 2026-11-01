#!/usr/bin/env python3
"""Leaf 27 on_minus_id idio ivol — LOWMEM v1 DRAFT (research; NOT RUN on real data this turn).

Baseline script sha256 (SUPERSEDED for lowmem path only; factor pins UNCHANGED):
  7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6

MATCH (impl contract / DIFF homepage) — factor definition UNCHANGED:
  Alpha capacity_adv exposure pin sha256:
    5e720335400255fffd1ddff10fc24b6ae1766188c2a3d3a5047aad48149e07b7
  Prereg r1 FROZEN sha256:
    f12965dadde8a9563aee31065698a73b72339bf61d7572ed1afe1be083dafdcf
  Arch contract preview sha256:
    31462908aa15c131fd74b6c378870907713235b975e08d7f026c79cc1707e196
  Data gap align sha256:
    cc85cb34dbaf7dba196e39ec17ce4dfb518302a48ea80769646230305257a745
  Main available_at research waiver sha256:
    b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f
  Impl pin: docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md (a532e6db…)
  Abort evidence: docs/v2/audit/ARCH_LEAF27_HILIQ_ABORT_RSS_20261025_ZH.md (37b63b8f…)

mechanism_tag: g1g5_ashare_on_minus_id_idio_ivol_v1
Main: α_raw = -ivol ; β window=60/min40 on 510300 hfq c2c ; W=20/min15
Residual order (same-day CS; skip none silently):
  1) on_minus_id = r_on - r_id
  2) SW L1 demean
  3) vs log float_mktcap T-1  (SCRIPT_LANDED; available_at RESEARCH_WAIVER_GRANTED)
  4) vs rolling β(510300)
  5) vs capacity_adv target_weight (Alpha pin; miss→0; drop 510300.SH)
  then ivol=std(ε5,W) → α_raw=-ivol → size-domain rank → resid → base-α

LOWMEM v1 (RSS target still ≤1500 unless Arch/主另裁; HI_LIQ only; FULLA GAP):
  - compact day maps (float32 arrays) instead of nested Python float dicts
  - LimitPanelCache keeps only calendar sessions; float32 boards
  - universe mask filtered by date span before materializing sets
  - dtype downcast on day-loop arrays; del+gc after major stages / between windows
  - ops: prefer one --window per process (x2|sealed); --window both frees between legs
  - NO change to α sign / β / W / gate / residual order / HI_LIQ-only auth scope

limit_hit CLOSED: day-align via LimitPanelCache (1c85 event_time / extend trade_date);
  True=hit, False=valid board & not hit, None=missing panel/row/both lu&ld invalid;
  exclude hit OR unknown from same-day CS residual / eps_hist / ivol; BJ empty → None → exclude;
  meta: limit_policy=exclude_hit_or_unknown + limit_hit_n/limit_unknown_n/bj_limit_empty_n.

Exposure column MUST be target_weight (NOT weight-first; NOT adv_fail/adv20).
active_capadv=1{target_weight>0} for Jaccard only.
live=false; promotion_approved=false; no .ok; no Book-Smoke.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import resource
import sys
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MECHANISM_TAG = "g1g5_ashare_on_minus_id_idio_ivol_v1"
LOWMEM_TAG = "leaf27_lowmem_v1"
BALLAST = "510300.SH"
HARD_EXCLUDE = frozenset({"600519.SH", "002371.SZ", BALLAST})
NAME_W = 0.04
MAX_NAMES = 20
IVOL_WIN = 20
MIN_IVOL_OBS = 15
BETA_WIN = 60
MIN_BETA_OBS = 40
REBAL_EVERY = 5

# --- pinned paths / shas (impl pin + Data + Alpha) ---
DAILY = ROOT / "data/v2/tushare_raw/daily"
MKTCAP = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
MKTCAP_SHA = "346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef"
ETF = ROOT / "data/v2/etf/etf_daily_adj.parquet"
ETF_SHA = "48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c"
CAPADV_HILIQ = (
    ROOT
    / "output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
)
CAPADV_HILIQ_SHA = "3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d"
CAPADV_FULLA = (
    ROOT
    / "output/strategy_fulla/legs/g1g5_capacity_adv_fulla_v1_daily_weights_20261014_192953.parquet"
)
SW = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
PANEL_1C85 = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec/panels"
PANEL_EXT = ROOT / "data/v2/asof_extend_tushare_202610/panels"
OUT_DIR = ROOT / "output/ai_factory/leaf27_on_minus_id_idio_ivol"
WINDOWS = {"sealed": ("2018-01-02", "2024-05-31"), "x2": ("2024-06-03", "2026-10-09")}
UNIVERSES = {
    "HILIQ": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
    "FULLA": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet",
}
IND_CAP = {"FULLA": 0.28, "HILIQ": 0.25}
CAPADV_PATH = {"HILIQ": CAPADV_HILIQ, "FULLA": CAPADV_FULLA}


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def assert_pinned_sha(p: Path, expect: str, label: str) -> None:
    got = file_sha(p)
    if got != expect:
        raise RuntimeError(f"sha_mismatch:{label}:expected={expect}:got={got}")


def to_ts(x: str) -> str:
    x = str(x)
    if "." in x and x.split(".")[0] in ("sz", "sh", "bj"):
        mkt, code = x.split(".", 1)
        return f"{code}.{mkt.upper()}"
    return x


def to_panel_name(ts_code: str) -> str:
    """600000.SH -> sh.600000"""
    code, mkt = str(ts_code).split(".")
    return f"{mkt.lower()}.{code}"


def sw_map() -> dict[str, str]:
    sw = pd.read_parquet(SW, columns=["instrument_id", "sw_name", "in_date"])
    sw["instrument"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"].astype(str), errors="coerce")
    sw = sw.sort_values("in_date").drop_duplicates("instrument", keep="last")
    out = dict(zip(sw["instrument"], sw["sw_name"]))
    del sw
    gc.collect()
    return out


def member_and_suspend(mask_path: Path, sessions: list[str]) -> tuple[dict, dict]:
    """Build per-session member/suspend sets; filter mask to session span first."""
    ss = set(sessions)
    if not sessions:
        return {}, {}
    s_min, s_max = sessions[0], sessions[-1]
    m = pd.read_parquet(
        mask_path, columns=["date", "instrument", "in_universe", "suspended"]
    )
    m["s"] = pd.to_datetime(m["date"]).dt.strftime("%Y-%m-%d")
    # date-span filter before materializing sets (avoid holding unused years)
    m = m[(m["s"] >= s_min) & (m["s"] <= s_max) & m["s"].isin(ss)]
    members = {s: set() for s in sessions}
    suspended = {s: set() for s in sessions}
    in_u = m[m["in_universe"].astype(bool)]
    for s, g in in_u.groupby("s", sort=False):
        if s in members:
            members[s] = set(g["instrument"].tolist())
    sus = m[m["suspended"].astype(bool)]
    for s, g in sus.groupby("s", sort=False):
        if s in suspended:
            suspended[s] = set(g["instrument"].tolist())
    del m, in_u, sus
    gc.collect()
    return members, suspended


def load_510300_ret() -> pd.Series:
    """r_510300 = close_hfq[t]/close_hfq[t-1]-1 ; pinned ETF path."""
    assert_pinned_sha(ETF, ETF_SHA, "etf_daily_adj")
    df = pd.read_parquet(ETF, columns=["ts_code", "trade_date", "close_hfq"])
    df = df[df["ts_code"] == "510300.SH"].copy()
    df["ds"] = pd.to_datetime(df["trade_date"].astype(str)).dt.strftime("%Y-%m-%d")
    df = df.sort_values("ds")
    close = df["close_hfq"].astype(np.float64)
    df["r"] = close / close.shift(1) - 1.0
    ser = df.set_index("ds")["r"]
    del df, close
    gc.collect()
    return ser


class DayFloatMap:
    """date -> instrument -> float32, stored as parallel arrays + on-demand dict cache.

    Avoids millions of Python float objects from nested dict[str, dict[str, float]].
    """

    __slots__ = ("_codes", "_vals", "_dict_cache", "_dict_cache_day")

    def __init__(self) -> None:
        self._codes: dict[str, np.ndarray] = {}
        self._vals: dict[str, np.ndarray] = {}
        self._dict_cache: dict[str, float] | None = None
        self._dict_cache_day: str | None = None

    def put_day(self, ds: str, codes: np.ndarray, vals: np.ndarray) -> None:
        if len(codes) == 0:
            return
        self._codes[ds] = np.asarray(codes, dtype=object)
        self._vals[ds] = np.asarray(vals, dtype=np.float32)

    def as_dict(self, ds: str) -> dict[str, float]:
        if self._dict_cache_day == ds and self._dict_cache is not None:
            return self._dict_cache
        codes = self._codes.get(ds)
        if codes is None:
            self._dict_cache = {}
            self._dict_cache_day = ds
            return self._dict_cache
        vals = self._vals[ds]
        # materialize one day only (caller needs O(1) .get)
        self._dict_cache = {str(c): float(v) for c, v in zip(codes, vals)}
        self._dict_cache_day = ds
        return self._dict_cache

    def drop_before(self, keep_from: str) -> None:
        """Drop days strictly before keep_from (string YYYY-MM-DD sortable)."""
        dead = [d for d in self._codes if d < keep_from]
        for d in dead:
            del self._codes[d]
            del self._vals[d]
        if self._dict_cache_day is not None and self._dict_cache_day < keep_from:
            self._dict_cache = None
            self._dict_cache_day = None

    def n_days(self) -> int:
        return len(self._codes)

    def clear(self) -> None:
        self._codes.clear()
        self._vals.clear()
        self._dict_cache = None
        self._dict_cache_day = None


def load_capadv_target_weight(universe: str, sessions: list[str] | None = None) -> DayFloatMap:
    """date -> instrument -> target_weight (Alpha pin). Missing later → 0."""
    path = CAPADV_PATH[universe]
    if universe == "HILIQ":
        assert_pinned_sha(path, CAPADV_HILIQ_SHA, "capadv_hiliq_weights")
    df = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
    df["ds"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[df["instrument"].astype(str) != BALLAST]
    if sessions:
        ss = set(sessions)
        s_min, s_max = sessions[0], sessions[-1]
        df = df[(df["ds"] >= s_min) & (df["ds"] <= s_max) & df["ds"].isin(ss)]
    out = DayFloatMap()
    tw = df["target_weight"].to_numpy(dtype=np.float64)
    inst = df["instrument"].astype(str).to_numpy()
    ds_arr = df["ds"].to_numpy()
    # group without holding giant groupby object long
    order = np.argsort(ds_arr, kind="mergesort")
    ds_arr = ds_arr[order]
    inst = inst[order]
    tw = tw[order]
    if len(ds_arr) == 0:
        del df
        gc.collect()
        return out
    # run-length split by day
    cuts = np.flatnonzero(ds_arr[1:] != ds_arr[:-1]) + 1
    starts = np.concatenate(([0], cuts))
    ends = np.concatenate((cuts, [len(ds_arr)]))
    for a, b in zip(starts, ends):
        d = str(ds_arr[a])
        v = tw[a:b]
        ok = np.isfinite(v)
        out.put_day(d, inst[a:b][ok], v[ok].astype(np.float32))
    del df, tw, inst, ds_arr
    gc.collect()
    return out


def load_mktcap_by_session(dates_needed: set[str]) -> DayFloatMap:
    """trade_date session -> instrument -> float_mktcap (float32 arrays)."""
    import pyarrow.parquet as pq

    assert_pinned_sha(MKTCAP, MKTCAP_SHA, "float_mktcap_from2015")
    pf = pq.ParquetFile(MKTCAP)
    out = DayFloatMap()
    want = set(dates_needed)
    # accumulate per-day lists then compact (row groups may split a day)
    acc_c: dict[str, list] = {d: [] for d in dates_needed}
    acc_v: dict[str, list] = {d: [] for d in dates_needed}
    for i in range(pf.num_row_groups):
        df = pf.read_row_group(
            i, columns=["instrument_id", "trade_date", "float_mktcap"]
        ).to_pandas()
        df["instrument"] = df["instrument_id"].map(to_ts)
        df["ds"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        df = df[df["ds"].isin(want)]
        if len(df) == 0:
            del df
            continue
        v = df["float_mktcap"].to_numpy(dtype=np.float64)
        ok = np.isfinite(v) & (v > 0)
        if ok.any():
            for ds, inst, val in zip(
                df["ds"].to_numpy()[ok],
                df["instrument"].to_numpy()[ok],
                v[ok],
            ):
                acc_c[ds].append(inst)
                acc_v[ds].append(np.float32(val))
        del df
        if i % 3 == 2:
            gc.collect()
    for ds in list(acc_c.keys()):
        if acc_c[ds]:
            out.put_day(ds, np.asarray(acc_c[ds], dtype=object), np.asarray(acc_v[ds], dtype=np.float32))
        acc_c[ds] = []
        acc_v[ds] = []
    del acc_c, acc_v
    gc.collect()
    return out


def mktcap_T_minus_1(
    mktcap: DayFloatMap,
    sessions: list[str],
    di: int,
) -> dict[str, float]:
    """Assert T-1: session T uses prev trading session's float_mktcap."""
    if di < 1:
        return {}
    prev = sessions[di - 1]
    return mktcap.as_dict(prev)


class LimitPanelCache:
    """Per-(ts_code, panel_kind) cache: session_ymd -> (limit_up, limit_down).

    LOWMEM: retain only sessions in `keep_sessions`; store float32 boards.
    """

    def __init__(self, keep_sessions: set[str] | None = None) -> None:
        self._maps: dict[tuple[str, str], dict[str, tuple[float, float]] | None] = {}
        self._keep = keep_sessions

    @staticmethod
    def panel_kind(session_ymd: str) -> str:
        ymd = session_ymd.replace("-", "")
        return "1c85" if ymd <= "20260630" else "ext"

    def _ensure(self, ts_code: str, kind: str) -> dict[str, tuple[float, float]] | None:
        key = (ts_code, kind)
        if key in self._maps:
            return self._maps[key]
        name = to_panel_name(ts_code)
        root = PANEL_1C85 if kind == "1c85" else PANEL_EXT
        p = root / f"{name}.parquet"
        if not p.exists():
            self._maps[key] = None
            return None
        try:
            out: dict[str, tuple[float, float]] = {}
            keep = self._keep
            if kind == "1c85":
                df = pd.read_parquet(p, columns=["limit_up", "limit_down"])
                if not isinstance(df.index, pd.DatetimeIndex):
                    raw = pd.read_parquet(p)
                    if "event_time" in raw.columns:
                        df = raw.set_index(pd.to_datetime(raw["event_time"]))[
                            ["limit_up", "limit_down"]
                        ]
                    else:
                        self._maps[key] = None
                        del raw
                        return None
                    del raw
                ds = pd.to_datetime(df.index).strftime("%Y-%m-%d")
                lu = df["limit_up"].to_numpy(dtype=np.float32)
                ld = df["limit_down"].to_numpy(dtype=np.float32)
                for d, u, dn in zip(ds, lu, ld):
                    d = str(d)
                    if keep is not None and d not in keep:
                        continue
                    out[d] = (float(u), float(dn))
                del df
            else:
                df = pd.read_parquet(
                    p, columns=["trade_date", "limit_up", "limit_down"]
                )
                ds = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
                lu = df["limit_up"].to_numpy(dtype=np.float32)
                ld = df["limit_down"].to_numpy(dtype=np.float32)
                for d, u, dn in zip(ds, lu, ld):
                    d = str(d)
                    if keep is not None and d not in keep:
                        continue
                    out[d] = (float(u), float(dn))
                del df
            self._maps[key] = out
            return out
        except Exception:
            self._maps[key] = None
            return None

    def get_limits(
        self, ts_code: str, session_ymd: str
    ) -> tuple[float, float] | None:
        """Return (lu, ld) for session, or None if panel/file/row missing."""
        kind = self.panel_kind(session_ymd)
        m = self._ensure(ts_code, kind)
        if m is None:
            return None
        return m.get(session_ymd)

    def clear(self) -> None:
        self._maps.clear()


def limit_hit(
    ts_code: str,
    session_ymd: str,
    close: float,
    cache: LimitPanelCache,
) -> bool | None:
    """True=hit limit, False=board prices valid and not hit, None=unknown."""
    pair = cache.get_limits(ts_code, session_ymd)
    if pair is None:
        return None
    lu, ld = pair
    lu_ok = lu == lu and float(lu) > 0.0
    ld_ok = ld == ld and float(ld) > 0.0
    if not lu_ok and not ld_ok:
        return None
    if not (close == close):
        return None
    c = float(close)
    if lu_ok and c >= float(lu):
        return True
    if ld_ok and c <= float(ld):
        return True
    return False


def resid_vs_x(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Cross-sectional OLS residual y ~ 1 + x."""
    out = np.full(len(y), np.nan, dtype=np.float64)
    ok = np.isfinite(y) & np.isfinite(x)
    if ok.sum() < 30:
        if ok.sum() >= 2:
            out[ok] = y[ok] - np.nanmean(y[ok])
        return out
    X = np.column_stack([np.ones(ok.sum(), dtype=np.float64), x[ok]])
    yo = y[ok]
    beta, *_ = np.linalg.lstsq(X, yo, rcond=None)
    out[ok] = yo - X @ beta
    return out


def sw_demean(y: np.ndarray, ind: np.ndarray) -> np.ndarray:
    s = pd.Series(y)
    return s.groupby(pd.Series(ind)).transform(lambda v: v - v.mean()).to_numpy()


def resid_ind_logmv(y: np.ndarray, ind: np.ndarray, logmv: np.ndarray) -> np.ndarray:
    n = len(y)
    out = np.full(n, np.nan, dtype=np.float64)
    ok = np.isfinite(y) & np.isfinite(logmv)
    if ok.sum() < 30:
        return sw_demean(y, ind)
    ind_ok = ind[ok]
    cats, inv = np.unique(ind_ok, return_inverse=True)
    if len(cats) >= 2:
        dummies = np.eye(len(cats), dtype=np.float64)[inv][:, 1:]
        X = np.column_stack([np.ones(ok.sum(), dtype=np.float64), logmv[ok], dummies])
    else:
        X = np.column_stack([np.ones(ok.sum(), dtype=np.float64), logmv[ok]])
    yo = y[ok]
    try:
        beta, *_ = np.linalg.lstsq(X, yo, rcond=None)
        out[ok] = yo - X @ beta
    except Exception:
        out = sw_demean(y, ind)
    return out


def domain_calibrate_arr(vals: np.ndarray, domains: np.ndarray) -> np.ndarray:
    out = np.zeros(len(vals), dtype=np.float64)
    for dom in np.unique(domains):
        idx = np.where(domains == dom)[0]
        x = vals[idx]
        if len(x) < 2:
            continue
        order = x.argsort().argsort()
        pct = (order + 1) / len(x)
        out[idx] = (pct - 0.5) * 2.0
    return out


def size_domain_arr(mv: np.ndarray) -> np.ndarray:
    out = np.array(["中小盘"] * len(mv), dtype=object)
    finite = np.isfinite(mv)
    if finite.sum() < 20:
        return out
    p70 = np.nanquantile(mv, 0.70)
    p90 = np.nanquantile(mv, 0.90)
    out[:] = "小微"
    out[mv >= p70] = "中小盘"
    out[mv >= p90] = "大盘"
    out[~finite] = "中小盘"
    return out


def _prune_hist(hist: dict[str, deque], alive: set[str]) -> None:
    """Drop rolling histories for codes not in alive (universe∪recent)."""
    dead = [c for c in hist if c not in alive]
    for c in dead:
        del hist[c]


def run_one(universe: str, window: str) -> dict:
    """LOWMEM runner — factor-identical to baseline; memory layout changed.

    This turn: do NOT invoke for real sealed/X2 production runs (await Arch .ok).
    """
    mask = UNIVERSES[universe]
    start, end = WINDOWS[window]
    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[{LOWMEM_TAG}/{universe}/{window}] begin rss={rss_mb():.0f}MB", flush=True)
    r_mkt = load_510300_ret()
    cal = sorted([d for d in r_mkt.index if warm_start <= d <= end])
    cal_set = set(cal)
    members, suspended = member_and_suspend(mask, cal)
    print(f"  members_loaded days={len(cal)} rss={rss_mb():.0f}MB", flush=True)
    swm = sw_map()
    cap = load_capadv_target_weight(universe, cal)
    print(f"  capadv_days={cap.n_days()} rss={rss_mb():.0f}MB", flush=True)
    mktcap = load_mktcap_by_session(cal_set)
    print(f"  mktcap_days={mktcap.n_days()} rss={rss_mb():.0f}MB", flush=True)
    lim_cache = LimitPanelCache(keep_sessions=cal_set)
    limit_hit_n = 0
    limit_unknown_n = 0
    bj_limit_empty_n = 0

    ret_hist: dict[str, deque] = defaultdict(lambda: deque(maxlen=BETA_WIN))
    mkt_hist: deque = deque(maxlen=BETA_WIN)
    eps_hist: dict[str, deque] = defaultdict(lambda: deque(maxlen=IVOL_WIN))

    # incremental alpha columns (avoid list of DataFrames)
    a_date: list[str] = []
    a_inst: list[str] = []
    a_alpha: list[float] = []
    a_raw: list[float] = []
    a_ivol: list[float] = []
    a_dom: list[str] = []
    a_ind: list[str] = []
    start_ts = pd.Timestamp(start)
    alive_recent: set[str] = set()

    for di, ds in enumerate(cal):
        pool = members.get(ds, set()) - suspended.get(ds, set()) - HARD_EXCLUDE
        p = DAILY / f"{ds.replace('-', '')}.parquet"
        if not pool or not p.exists():
            continue
        df = pd.read_parquet(p, columns=["ts_code", "open", "pre_close", "close"])
        df = df[df["ts_code"].isin(pool)]
        if len(df) < 30:
            del df
            continue

        op = df["open"].to_numpy(dtype=np.float64)
        pc = df["pre_close"].to_numpy(dtype=np.float64)
        cl = df["close"].to_numpy(dtype=np.float64)
        codes = df["ts_code"].to_numpy()
        del df
        good = (
            np.isfinite(op)
            & np.isfinite(pc)
            & np.isfinite(cl)
            & (pc > 0)
            & (op > 0)
        )
        codes, op, pc, cl = codes[good], op[good], pc[good], cl[good]
        if len(codes) < 30:
            continue

        keep_idx: list[int] = []
        for i, (c, close_i) in enumerate(zip(codes, cl)):
            hit = limit_hit(str(c), ds, float(close_i), lim_cache)
            if hit is True:
                limit_hit_n += 1
                continue
            if hit is None:
                limit_unknown_n += 1
                if str(c).endswith(".BJ"):
                    bj_limit_empty_n += 1
                continue
            keep_idx.append(i)
        if len(keep_idx) < 30:
            continue
        keep_a = np.asarray(keep_idx, dtype=np.int32)
        codes, op, pc, cl = codes[keep_a], op[keep_a], pc[keep_a], cl[keep_a]
        close_by = {str(c): float(v) for c, v in zip(codes, cl)}

        r_on = op / pc - 1.0
        r_id = cl / op - 1.0
        on_minus_id = r_on - r_id

        r_stock = cl / pc - 1.0
        rm = float(r_mkt.get(ds, np.nan))
        if np.isfinite(rm):
            mkt_hist.append(rm)
        for c, rs in zip(codes, r_stock):
            if np.isfinite(rs):
                ret_hist[str(c)].append(float(rs))

        mc_tm1 = mktcap_T_minus_1(mktcap, cal, di)
        # drop mktcap days older than T-2 (only T-1 needed going forward)
        if di >= 2:
            mktcap.drop_before(cal[di - 1])

        ind = np.array([swm.get(c, "_UNK") for c in codes], dtype=object)
        mv = np.array([mc_tm1.get(c, np.nan) for c in codes], dtype=np.float64)
        valid_mv = np.isfinite(mv) & (mv > 0)
        logmv = np.full(len(codes), np.nan, dtype=np.float64)
        logmv[valid_mv] = np.log(mv[valid_mv])

        e2 = sw_demean(on_minus_id, ind)
        e3 = resid_vs_x(e2, logmv)
        e3[~valid_mv] = np.nan

        betas = np.full(len(codes), np.nan, dtype=np.float64)
        if len(mkt_hist) >= MIN_BETA_OBS:
            mkt_arr = np.asarray(mkt_hist, dtype=np.float64)
            for i, c in enumerate(codes):
                h = ret_hist.get(str(c))
                if not h or len(h) < MIN_BETA_OBS:
                    continue
                n = min(len(h), len(mkt_arr))
                if n < MIN_BETA_OBS:
                    continue
                yb = np.asarray(list(h)[-n:], dtype=np.float64)
                xb = mkt_arr[-n:]
                okb = np.isfinite(yb) & np.isfinite(xb)
                if okb.sum() < MIN_BETA_OBS:
                    continue
                Xb = np.column_stack(
                    [np.ones(okb.sum(), dtype=np.float64), xb[okb]]
                )
                b, *_ = np.linalg.lstsq(Xb, yb[okb], rcond=None)
                betas[i] = float(b[1]) if len(b) > 1 else np.nan
        e4 = resid_vs_x(e3, betas)

        cap_day = cap.as_dict(ds)
        xcap = np.array([float(cap_day.get(c, 0.0)) for c in codes], dtype=np.float64)
        e5 = resid_vs_x(e4, xcap)

        for c, e in zip(codes, e5):
            if np.isfinite(e):
                eps_hist[str(c)].append(float(e))

        alive_recent.update(str(c) for c in codes)
        if di % 40 == 0 and di > 0:
            # prune rolling hist for names gone from recent window
            _prune_hist(ret_hist, alive_recent)
            _prune_hist(eps_hist, alive_recent)
            alive_recent = set(str(c) for c in codes)
            gc.collect()

        if pd.Timestamp(ds) < start_ts:
            continue

        ivol_codes, ivols, mvs, inds = [], [], [], []
        for c in pool:
            if c in HARD_EXCLUDE:
                continue
            cl_c = close_by.get(str(c))
            if cl_c is None:
                continue
            hit = limit_hit(str(c), ds, float(cl_c), lim_cache)
            if hit is not False:
                continue
            h = eps_hist.get(str(c))
            if not h or len(h) < MIN_IVOL_OBS:
                continue
            iv = float(np.std(h, ddof=1)) if len(h) >= 2 else np.nan
            if not np.isfinite(iv):
                continue
            mv_c = mc_tm1.get(c, np.nan)
            if not (mv_c == mv_c and mv_c > 0):
                continue
            ivol_codes.append(c)
            ivols.append(iv)
            mvs.append(mv_c)
            inds.append(swm.get(c, "_UNK"))
        if len(ivol_codes) < 50:
            continue

        ivols_a = np.asarray(ivols, dtype=np.float64)
        mvs_a = np.asarray(mvs, dtype=np.float64)
        inds_a = np.asarray(inds, dtype=object)
        alpha_raw = -ivols_a  # FROZEN direction
        domains = size_domain_arr(mvs_a)
        score = domain_calibrate_arr(alpha_raw, domains)
        logmv2 = np.log(np.clip(mvs_a, 1.0, None))
        alpha = resid_ind_logmv(score, inds_a, logmv2)
        alpha = domain_calibrate_arr(alpha, domains)

        for i, c in enumerate(ivol_codes):
            a_date.append(ds)
            a_inst.append(c)
            a_alpha.append(float(alpha[i]))
            a_raw.append(float(alpha_raw[i]))
            a_ivol.append(float(ivols_a[i]))
            a_dom.append(str(domains[i]))
            a_ind.append(str(inds_a[i]))

        if di % 60 == 0:
            print(f"  {ds} n={len(ivol_codes)} rss={rss_mb():.0f}MB", flush=True)

    alpha = pd.DataFrame(
        {
            "date": a_date,
            "instrument": a_inst,
            "alpha": np.asarray(a_alpha, dtype=np.float64),
            "alpha_raw": np.asarray(a_raw, dtype=np.float64),
            "ivol": np.asarray(a_ivol, dtype=np.float64),
            "size_domain": a_dom,
            "ind": a_ind,
        }
    )
    ap = OUT_DIR / f"alpha_{universe}_{window}_{stamp}.parquet"
    if len(alpha):
        alpha.to_parquet(ap, index=False)
    meta = dict(
        mechanism_tag=MECHANISM_TAG,
        lowmem_tag=LOWMEM_TAG,
        universe=universe,
        window=window,
        span=[start, end],
        alpha_direction="minus_ivol",
        beta_win=BETA_WIN,
        min_beta_obs=MIN_BETA_OBS,
        ivol_win=IVOL_WIN,
        min_ivol_obs=MIN_IVOL_OBS,
        exposure_col="target_weight",
        capadv_path=str(CAPADV_PATH[universe]),
        capadv_sha256=CAPADV_HILIQ_SHA if universe == "HILIQ" else "see_fulla_file",
        etf_sha256=ETF_SHA,
        mktcap_sha256=MKTCAP_SHA,
        mktcap_rule="T-1_prev_trading_session",
        limit_cols=["limit_up", "limit_down"],
        limit_policy="exclude_hit_or_unknown",
        limit_hit_n=int(limit_hit_n),
        limit_unknown_n=int(limit_unknown_n),
        bj_limit_empty_n=int(bj_limit_empty_n),
        mktcap_available_at="RESEARCH_WAIVER_GRANTED",
        mktcap_available_at_waiver_sha256=(
            "b39954c3ff6ee4c03f904ec9f58660871b1b574bfab6498c57b825878f28ab7f"
        ),
        live=False,
        promotion_approved=False,
        peak_rss_mb=rss_mb(),
        n_alpha_rows=int(len(alpha)),
        alpha_path=str(ap) if len(alpha) else None,
        note=(
            "LOWMEM_v1 DRAFT; factor pins UNCHANGED; "
            "compact DayFloatMap+LimitPanel keep_sessions; no .ok this turn"
        ),
        baseline_script_sha256=(
            "7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6"
        ),
    )
    mp = OUT_DIR / f"run_meta_{universe}_{window}_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # free window-local heaps before next leg
    lim_cache.clear()
    mktcap.clear()
    cap.clear()
    members.clear()
    suspended.clear()
    ret_hist.clear()
    eps_hist.clear()
    mkt_hist.clear()
    del alpha, a_date, a_inst, a_alpha, a_raw, a_ivol, a_dom, a_ind
    del lim_cache, mktcap, cap, members, suspended, ret_hist, eps_hist, r_mkt, swm
    gc.collect()
    print(f"[{LOWMEM_TAG}/{universe}/{window}] done rss={rss_mb():.0f}MB", flush=True)
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", choices=["FULLA", "HILIQ", "both"], default="HILIQ")
    ap.add_argument("--window", choices=["sealed", "x2", "both"], default="x2")
    ap.add_argument(
        "--dry-compile-only",
        action="store_true",
        help="Exit after importing constants (no data run).",
    )
    args = ap.parse_args()
    if args.dry_compile_only:
        print(
            json.dumps(
                {
                    "mechanism_tag": MECHANISM_TAG,
                    "lowmem_tag": LOWMEM_TAG,
                    "exposure_col": "target_weight",
                    "etf_sha": ETF_SHA,
                    "capadv_hiliq_sha": CAPADV_HILIQ_SHA,
                    "baseline_script_sha": (
                        "7a5f756c0a1ab09fb55aa2bc3c17f389bde44d222d7066237e503566c908f8c6"
                    ),
                    "live": False,
                }
            )
        )
        return
    if args.universe == "FULLA" or args.universe == "both":
        raise SystemExit(
            "FULLA_GAP: leaf27 lowmem v1 authorized path is HILIQ-only; "
            "FULLA remains GAP (Arch). Refuse --universe FULLA|both."
        )
    us = ["HILIQ"]
    ws = ["x2", "sealed"] if args.window == "both" else [args.window]
    if args.window == "both":
        print(
            "WARN: --window both runs sealed+x2 sequentially in one process; "
            "ops prefer separate processes under rss_limit=1500",
            flush=True,
        )
    results = []
    for u in us:
        for w in ws:
            results.append(run_one(u, w))
            gc.collect()
    summary = OUT_DIR / f"build_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("SUMMARY", summary, "peak_rss", max(r["peak_rss_mb"] for r in results))


if __name__ == "__main__":
    main()
