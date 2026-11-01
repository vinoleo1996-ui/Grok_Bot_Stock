"""PIT all-A universe mask (research helper, NON-frozen; promotion=false, live=false).

Leo 2026-10-14 07:24 ET 指令：全 A 股，剔除 ST、停牌、上市不满 60 交易日、按 100万档 ADV 不可交易的票。

Rule for session S (decision at S open, available_at = S 09:00 +08):
  1. Base: SSE+SZSE A-shares with a daily bar in tushare_raw/daily within the
     20 open sessions before S (BSE excluded, same as MID_LARGE_RULE.md).
  2. ST: excluded if S falls in an ST/*ST interval from
     data/v2/st_events/st_events_from_namechange.parquet (same source as mid_large).
  3. Suspended: excluded if tushare_raw/suspend_d has suspend_type=='S' on S
     (suspension notices are published before the open), OR no bar on S-1.
  4. Listing age: >= 60 open sessions between list_date (stock_basic L/D/P) and S-1 inclusive.
  5. ADV (100万 tier): ADV20 = mean(amount) over the 20 open sessions S-20..S-1
     (suspended/missing days count as 0, conservative), amount in yuan
     (tushare 千元 ×1000). Tradable iff NAME_CAP × AUM ≤ k × ADV20 with
     k=0.02 (capacity_adv ADV_PARTICIPATION_K), NAME_CAP=0.04, AUM=1,000,000
     → ADV20 ≥ 2,000,000 yuan.
Only data dated < S is used (except the pre-open suspend notice on S).
"""
from __future__ import annotations
import os
from functools import lru_cache
import numpy as np
import pandas as pd

ROOT = "/workspace/QuantLab"
RAW = f"{ROOT}/data/v2/tushare_raw"
AUM_TIER = 1_000_000.0
NAME_CAP = 0.04
ADV_K = 0.02
ADV_MIN_YUAN = NAME_CAP * AUM_TIER / ADV_K  # 2,000,000
ADV_WIN = 20
MIN_LIST_SESSIONS = 60


@lru_cache(1)
def open_sessions() -> pd.DatetimeIndex:
    c = pd.read_parquet(f"{ROOT}/data/v2/calendar/trade_cal_sse_pit.parquet")
    c = c[c.is_open == 1]
    return pd.DatetimeIndex(pd.to_datetime(c.cal_date.astype(str))).sort_values()


@lru_cache(1)
def list_dates() -> pd.Series:
    fs = [pd.read_parquet(f"{RAW}/stock_basic/{x}.parquet") for x in ("L", "D", "P")]
    sb = pd.concat(fs).drop_duplicates("ts_code")
    sb = sb[sb.exchange.isin(["SSE", "SZSE"])]
    return pd.to_datetime(sb.set_index("ts_code").list_date, errors="coerce")


@lru_cache(1)
def st_intervals() -> pd.DataFrame:
    st = pd.read_parquet(f"{ROOT}/data/v2/st_events/st_events_from_namechange.parquet")
    return st


def _daily(d: pd.Timestamp) -> pd.DataFrame:
    p = f"{RAW}/daily/{d:%Y%m%d}.parquet"
    if not os.path.exists(p):
        return pd.DataFrame(columns=["ts_code", "amount"])
    return pd.read_parquet(p, columns=["ts_code", "amount"])


def _st_set(S: pd.Timestamp) -> set:
    st = st_intervals()
    cols = st.columns
    code = "ts_code" if "ts_code" in cols else "instrument_id"
    s = pd.to_datetime(st["start_date"].astype(str), errors="coerce"); e = pd.to_datetime(st["end_date"].astype(str), errors="coerce").fillna(pd.Timestamp("2100-01-01"))
    m = (s <= S) & (e >= S)
    m &= st["name"].astype(str).str.upper().str.contains("ST")
    out = set(st.loc[m, code])
    # normalise sh.600000 -> 600000.SH
    return {(x.split(".")[1] + "." + x.split(".")[0].upper()) if x[:3] in ("sh.", "sz.", "bj.") else x for x in out}


def universe_mask(session) -> pd.DataFrame:
    S = pd.Timestamp(str(session)[:10])
    sess = open_sessions()
    prior = sess[sess < S][-ADV_WIN:]
    if len(prior) < ADV_WIN:
        raise ValueError("not enough history")
    amt = {}
    for d in prior:
        x = _daily(d)
        amt[d] = x.set_index("ts_code")["amount"]
    A = pd.DataFrame(amt).fillna(0.0) * 1000.0
    A = A[A.index.str.endswith((".SH", ".SZ"))]
    df = pd.DataFrame(index=A.index)
    df["adv20_yuan"] = A.mean(axis=1)
    df["bar_prev"] = A.iloc[:, -1] > 0
    ld = list_dates().reindex(df.index)
    n_listed = np.searchsorted(sess.values, S.to_datetime64()) - np.searchsorted(sess.values, ld.values.astype("datetime64[ns]"))
    df["listed_sessions"] = np.where(ld.notna(), n_listed, -1)
    sp = f"{RAW}/suspend_d/{S:%Y%m%d}.parquet"
    susp = set()
    if os.path.exists(sp):
        x = pd.read_parquet(sp); susp = set(x.loc[x.suspend_type == "S", "ts_code"])
    df["suspended"] = df.index.isin(susp) | ~df["bar_prev"]
    df["st"] = df.index.isin(_st_set(S))
    df["young"] = df["listed_sessions"] < MIN_LIST_SESSIONS
    df["adv_fail"] = df["adv20_yuan"] < ADV_MIN_YUAN
    df["in_all_a"] = ~(df.st | df.suspended | df.young | df.adv_fail)
    df["session"] = S
    return df


if __name__ == "__main__":
    import sys
    m = universe_mask(sys.argv[1] if len(sys.argv) > 1 else "2026-10-14")
    print(m[["st", "suspended", "young", "adv_fail", "in_all_a"]].sum().to_dict(), len(m))
