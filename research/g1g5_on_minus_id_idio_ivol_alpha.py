#!/usr/bin/env python3
"""Leaf 27 on_minus_id idio ivol — DRAFT (research; NOT RUN on real data this turn).

MATCH (impl contract / DIFF homepage):
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
  Impl pin: docs/v2/AI_LEAF27_IMPL_CONTRACT_PIN_20261025_ZH.md

mechanism_tag: g1g5_ashare_on_minus_id_idio_ivol_v1
Main: α_raw = -ivol ; β window=60/min40 on 510300 hfq c2c ; W=20/min15
Residual order (same-day CS; skip none silently):
  1) on_minus_id = r_on - r_id
  2) SW L1 demean
  3) vs log float_mktcap T-1  (SCRIPT_LANDED; available_at RESEARCH_WAIVER_GRANTED)
  4) vs rolling β(510300)
  5) vs capacity_adv target_weight (Alpha pin; miss→0; drop 510300.SH)
  then ivol=std(ε5,W) → α_raw=-ivol → size-domain rank → resid → base-α

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
    return dict(zip(sw["instrument"], sw["sw_name"]))


def member_and_suspend(mask_path: Path, sessions: list[str]) -> tuple[dict, dict]:
    m = pd.read_parquet(
        mask_path, columns=["date", "instrument", "in_universe", "suspended"]
    )
    m["s"] = pd.to_datetime(m["date"]).dt.strftime("%Y-%m-%d")
    ss = set(sessions)
    m = m[m["s"].isin(ss)]
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
    return members, suspended


def load_510300_ret() -> pd.Series:
    """r_510300 = close_hfq[t]/close_hfq[t-1]-1 ; pinned ETF path."""
    assert_pinned_sha(ETF, ETF_SHA, "etf_daily_adj")
    df = pd.read_parquet(ETF, columns=["ts_code", "trade_date", "close_hfq"])
    df = df[df["ts_code"] == "510300.SH"].copy()
    df["ds"] = pd.to_datetime(df["trade_date"].astype(str)).dt.strftime("%Y-%m-%d")
    df = df.sort_values("ds")
    df["r"] = df["close_hfq"].astype(float) / df["close_hfq"].astype(float).shift(1) - 1.0
    return df.set_index("ds")["r"]


def load_capadv_target_weight(universe: str) -> dict[str, dict[str, float]]:
    """date -> instrument -> target_weight (Alpha pin). Missing later → 0."""
    path = CAPADV_PATH[universe]
    if universe == "HILIQ":
        assert_pinned_sha(path, CAPADV_HILIQ_SHA, "capadv_hiliq_weights")
    df = pd.read_parquet(path, columns=["date", "instrument", "target_weight"])
    df["ds"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    # drop ballast from stock CS exposure universe
    df = df[df["instrument"].astype(str) != BALLAST]
    out: dict[str, dict[str, float]] = {}
    for ds, g in df.groupby("ds", sort=False):
        out[ds] = {
            str(i): float(w)
            for i, w in zip(g["instrument"], g["target_weight"])
            if w == w
        }
    return out


def load_mktcap_by_session(dates_needed: set[str]) -> dict[str, dict[str, float]]:
    """trade_date session -> instrument -> float_mktcap (raw table; T-1 applied by caller)."""
    import pyarrow.parquet as pq

    assert_pinned_sha(MKTCAP, MKTCAP_SHA, "float_mktcap_from2015")
    pf = pq.ParquetFile(MKTCAP)
    out: dict[str, dict[str, float]] = {d: {} for d in dates_needed}
    want = set(dates_needed)
    for i in range(pf.num_row_groups):
        df = pf.read_row_group(
            i, columns=["instrument_id", "trade_date", "float_mktcap"]
        ).to_pandas()
        df["instrument"] = df["instrument_id"].map(to_ts)
        df["ds"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        df = df[df["ds"].isin(want)]
        for ds, g in df.groupby("ds", sort=False):
            bucket = out.setdefault(ds, {})
            for inst, v in zip(g["instrument"].to_numpy(), g["float_mktcap"].to_numpy()):
                if v == v and float(v) > 0:
                    bucket[inst] = float(v)
        del df
    return out


def mktcap_T_minus_1(
    mktcap: dict[str, dict[str, float]],
    sessions: list[str],
    di: int,
) -> dict[str, float]:
    """Assert T-1: session T uses prev trading session's float_mktcap.

    available_at proxy = T-1 session 18:00 Asia/Shanghai (reader convention).
    For open decision at T, T-day EOD mktcap is forbidden — hence T-1 only.
    Missing → omit (caller marks invalid).
    """
    if di < 1:
        return {}
    prev = sessions[di - 1]
    return mktcap.get(prev, {})


class LimitPanelCache:
    """Per-(ts_code, panel_kind) cache: session_ymd -> (limit_up, limit_down).

    Panel facts (schema-checked; no forged available_at):
      - 1c85: index=event_time (DatetimeIndex); cols include limit_up/limit_down (double).
        BJ values often all-null → unknown.
      - asof_extend_tushare: cols trade_date + limit_up/limit_down.
      - Path cut: ymd<=20260630 → PANEL_1C85; else → PANEL_EXT.
    Do NOT re-read whole parquet per (code, day).
    """

    def __init__(self) -> None:
        # (ts_code, "1c85"|"ext") -> session_ymd -> (lu, ld)  OR None if file missing
        self._maps: dict[tuple[str, str], dict[str, tuple[float, float]] | None] = {}

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
            if kind == "1c85":
                # index=event_time preserved when selecting limit cols
                df = pd.read_parquet(p, columns=["limit_up", "limit_down"])
                if not isinstance(df.index, pd.DatetimeIndex):
                    # rare: event_time as column
                    raw = pd.read_parquet(p)
                    if "event_time" in raw.columns:
                        df = raw.set_index(pd.to_datetime(raw["event_time"]))[
                            ["limit_up", "limit_down"]
                        ]
                    else:
                        self._maps[key] = None
                        return None
                ds = pd.to_datetime(df.index).strftime("%Y-%m-%d")
                lu = df["limit_up"].to_numpy(dtype=float)
                ld = df["limit_down"].to_numpy(dtype=float)
                for d, u, dn in zip(ds, lu, ld):
                    out[str(d)] = (float(u), float(dn))
            else:
                df = pd.read_parquet(
                    p, columns=["trade_date", "limit_up", "limit_down"]
                )
                ds = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
                lu = df["limit_up"].to_numpy(dtype=float)
                ld = df["limit_down"].to_numpy(dtype=float)
                for d, u, dn in zip(ds, lu, ld):
                    out[str(d)] = (float(u), float(dn))
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


def limit_hit(
    ts_code: str,
    session_ymd: str,
    close: float,
    cache: LimitPanelCache,
) -> bool | None:
    """True=hit limit, False=board prices valid and not hit, None=unknown.

    Hit: close>=limit_up or close<=limit_down (board price finite and >0).
    Unknown (None): panel missing, session row missing, or both lu&ld invalid
    (NaN or <=0) — includes typical BJ empty boards. Never silently treat as False.
    """
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
    out = np.full(len(y), np.nan)
    ok = np.isfinite(y) & np.isfinite(x)
    if ok.sum() < 30:
        if ok.sum() >= 2:
            out[ok] = y[ok] - np.nanmean(y[ok])
        return out
    X = np.column_stack([np.ones(ok.sum()), x[ok]])
    yo = y[ok]
    beta, *_ = np.linalg.lstsq(X, yo, rcond=None)
    out[ok] = yo - X @ beta
    return out


def sw_demean(y: np.ndarray, ind: np.ndarray) -> np.ndarray:
    s = pd.Series(y)
    return s.groupby(pd.Series(ind)).transform(lambda v: v - v.mean()).to_numpy()


def resid_ind_logmv(y: np.ndarray, ind: np.ndarray, logmv: np.ndarray) -> np.ndarray:
    n = len(y)
    out = np.full(n, np.nan)
    ok = np.isfinite(y) & np.isfinite(logmv)
    if ok.sum() < 30:
        return sw_demean(y, ind)
    ind_ok = ind[ok]
    cats, inv = np.unique(ind_ok, return_inverse=True)
    if len(cats) >= 2:
        dummies = np.eye(len(cats), dtype=float)[inv][:, 1:]
        X = np.column_stack([np.ones(ok.sum()), logmv[ok], dummies])
    else:
        X = np.column_stack([np.ones(ok.sum()), logmv[ok]])
    yo = y[ok]
    try:
        beta, *_ = np.linalg.lstsq(X, yo, rcond=None)
        out[ok] = yo - X @ beta
    except Exception:
        out = sw_demean(y, ind)
    return out


def domain_calibrate_arr(vals: np.ndarray, domains: np.ndarray) -> np.ndarray:
    out = np.zeros(len(vals))
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


def run_one(universe: str, window: str) -> dict:
    """DRAFT runner — structurally complete; intended for Arch review / py_compile.

    This turn: do NOT invoke for real sealed/X2 production runs.
    """
    mask = UNIVERSES[universe]
    start, end = WINDOWS[window]
    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    r_mkt = load_510300_ret()
    cal = sorted([d for d in r_mkt.index if warm_start <= d <= end])
    members, suspended = member_and_suspend(mask, cal)
    swm = sw_map()
    cap = load_capadv_target_weight(universe)
    mktcap = load_mktcap_by_session(set(cal))
    lim_cache = LimitPanelCache()
    limit_hit_n = 0
    limit_unknown_n = 0
    bj_limit_empty_n = 0

    # rolling stock returns for beta (on_minus_id series residualized later)
    ret_hist: dict[str, deque] = defaultdict(lambda: deque(maxlen=BETA_WIN))
    mkt_hist: deque = deque(maxlen=BETA_WIN)
    eps_hist: dict[str, deque] = defaultdict(lambda: deque(maxlen=IVOL_WIN))

    alpha_rows: list[pd.DataFrame] = []
    start_ts = pd.Timestamp(start)

    for di, ds in enumerate(cal):
        pool = members.get(ds, set()) - suspended.get(ds, set()) - HARD_EXCLUDE
        p = DAILY / f"{ds.replace('-', '')}.parquet"
        if not pool or not p.exists():
            continue
        df = pd.read_parquet(p, columns=["ts_code", "open", "pre_close", "close"])
        df = df[df["ts_code"].isin(pool)]
        if len(df) < 30:
            continue

        op = df["open"].to_numpy(float)
        pc = df["pre_close"].to_numpy(float)
        cl = df["close"].to_numpy(float)
        codes = df["ts_code"].to_numpy()
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

        # limit_hit day-align: exclude hit(True) OR unknown(None); only False stays
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
        keep_a = np.asarray(keep_idx, dtype=int)
        codes, op, pc, cl = codes[keep_a], op[keep_a], pc[keep_a], cl[keep_a]
        close_by = {str(c): float(v) for c, v in zip(codes, cl)}

        r_on = op / pc - 1.0
        r_id = cl / op - 1.0
        on_minus_id = r_on - r_id  # step raw

        # update beta histories with simple close-to-close for β (stock raw)
        # DRAFT note: β uses stock close/pre_close-1 vs 510300 hfq; disclose in receipt
        r_stock = cl / pc - 1.0
        rm = float(r_mkt.get(ds, np.nan))
        if np.isfinite(rm):
            mkt_hist.append(rm)
        for c, rs in zip(codes, r_stock):
            if np.isfinite(rs):
                ret_hist[c].append(float(rs))

        # T-1 mktcap assert
        mc_tm1 = mktcap_T_minus_1(mktcap, cal, di)
        ind = np.array([swm.get(c, "_UNK") for c in codes], dtype=object)
        mv = np.array([mc_tm1.get(c, np.nan) for c in codes], dtype=float)
        # invalid if missing T-1 mktcap
        valid_mv = np.isfinite(mv) & (mv > 0)
        logmv = np.full(len(codes), np.nan)
        logmv[valid_mv] = np.log(mv[valid_mv])

        # step2 SW L1 demean
        e2 = sw_demean(on_minus_id, ind)
        # step3 vs log mktcap T-1
        e3 = resid_vs_x(e2, logmv)
        e3[~valid_mv] = np.nan

        # step4 vs rolling β(510300)
        betas = np.full(len(codes), np.nan)
        if len(mkt_hist) >= MIN_BETA_OBS:
            mkt_arr = np.asarray(mkt_hist, float)
            for i, c in enumerate(codes):
                h = ret_hist.get(c)
                if not h or len(h) < MIN_BETA_OBS:
                    continue
                # align last min(len) points
                n = min(len(h), len(mkt_arr))
                if n < MIN_BETA_OBS:
                    continue
                yb = np.asarray(list(h)[-n:], float)
                xb = mkt_arr[-n:]
                okb = np.isfinite(yb) & np.isfinite(xb)
                if okb.sum() < MIN_BETA_OBS:
                    continue
                Xb = np.column_stack([np.ones(okb.sum()), xb[okb]])
                b, *_ = np.linalg.lstsq(Xb, yb[okb], rcond=None)
                betas[i] = float(b[1]) if len(b) > 1 else np.nan
        # residualize e3 on beta exposure (cross-section)
        e4 = resid_vs_x(e3, betas)

        # step5 vs capacity_adv target_weight (Alpha)
        cap_day = cap.get(ds, {})
        xcap = np.array([float(cap_day.get(c, 0.0)) for c in codes], dtype=float)
        e5 = resid_vs_x(e4, xcap)

        for c, e in zip(codes, e5):
            if np.isfinite(e):
                eps_hist[c].append(float(e))

        if pd.Timestamp(ds) < start_ts:
            continue

        # ivol / alpha — touch-limit or unknown today excluded from CS/ivol
        ivol_codes, ivols, mvs, inds = [], [], [], []
        for c in pool:
            if c in HARD_EXCLUDE:
                continue
            cl_c = close_by.get(str(c))
            if cl_c is None:
                continue  # no OHLC today → not in CS
            hit = limit_hit(str(c), ds, float(cl_c), lim_cache)
            if hit is not False:
                continue
            h = eps_hist.get(c)
            if not h or len(h) < MIN_IVOL_OBS:
                continue
            iv = float(np.std(h, ddof=1)) if len(h) >= 2 else np.nan
            if not np.isfinite(iv):
                continue
            mv_c = mc_tm1.get(c, np.nan)
            if not (mv_c == mv_c and mv_c > 0):
                continue  # T-1 missing → invalid
            ivol_codes.append(c)
            ivols.append(iv)
            mvs.append(mv_c)
            inds.append(swm.get(c, "_UNK"))
        if len(ivol_codes) < 50:
            continue

        ivols_a = np.asarray(ivols, float)
        mvs_a = np.asarray(mvs, float)
        inds_a = np.asarray(inds, object)
        alpha_raw = -ivols_a  # FROZEN direction
        domains = size_domain_arr(mvs_a)
        score = domain_calibrate_arr(alpha_raw, domains)
        logmv2 = np.log(np.clip(mvs_a, 1.0, None))
        alpha = resid_ind_logmv(score, inds_a, logmv2)
        alpha = domain_calibrate_arr(alpha, domains)

        alpha_rows.append(
            pd.DataFrame(
                {
                    "date": ds,
                    "instrument": ivol_codes,
                    "alpha": alpha,
                    "alpha_raw": alpha_raw,
                    "ivol": ivols_a,
                    "size_domain": domains,
                    "ind": inds_a,
                }
            )
        )

        if di % 60 == 0:
            print(f"  {ds} n={len(ivol_codes)} rss={rss_mb():.0f}MB", flush=True)

    alpha = (
        pd.concat(alpha_rows, ignore_index=True)
        if alpha_rows
        else pd.DataFrame(
            columns=["date", "instrument", "alpha", "alpha_raw", "ivol", "size_domain", "ind"]
        )
    )
    ap = OUT_DIR / f"alpha_{universe}_{window}_{stamp}.parquet"
    if len(alpha):
        alpha.to_parquet(ap, index=False)
    meta = dict(
        mechanism_tag=MECHANISM_TAG,
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
        note="DRAFT; limit_hit day-align CLOSED; available_at waiver; no .ok this turn",
    )
    mp = OUT_DIR / f"run_meta_{universe}_{window}_{stamp}.json"
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
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
                    "exposure_col": "target_weight",
                    "etf_sha": ETF_SHA,
                    "capadv_hiliq_sha": CAPADV_HILIQ_SHA,
                    "live": False,
                }
            )
        )
        return
    us = ["HILIQ", "FULLA"] if args.universe == "both" else [args.universe]
    ws = ["x2", "sealed"] if args.window == "both" else [args.window]
    results = []
    for u in us:
        for w in ws:
            results.append(run_one(u, w))
    summary = OUT_DIR / f"build_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("SUMMARY", summary)


if __name__ == "__main__":
    main()
