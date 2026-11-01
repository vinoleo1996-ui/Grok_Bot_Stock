"""PIT high-liquidity subset mask HI_LIQ_V1 / V1.1 (Strategy, research helper).

Leo 2026-10-14 07:42 ET dual-track: FULLA=research; paper=high-liquidity subset.
Prereg: docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_ZH.md
Amendment: docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_V1_1_ZH.md (no mcap screen;
stock-sleeve SW L1 IND_CAP=0.25 is a *leg construction* rule, not a mask column).
live=false; strategy_promotion=false. Does NOT touch FROZEN_CONFIG / existing paper tracks.

Universe filters ONLY: tradability (ST / suspend / <60d) + ADV20.
NO market-cap screen. ADV floor = 100,000,000 yuan = 10 × (6% × 1,000,000 / 0.6%).
FULLA research canonical ADV floor remains 3,000,000 (separate mask).
"""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd

ROOT = "/workspace/QuantLab"
RAW = f"{ROOT}/data/v2/tushare_raw"
OUT_DIR = f"{ROOT}/output/strategy_hiliq"
OUT_MASK = f"{OUT_DIR}/universe_mask_hiliq_v1.parquet"

AUM_TIER = 1_000_000.0
NAME_CAP_PORTFOLIO = 0.06  # B4 portfolio single-name cap @ 100万
PARTICIPATION_K = 0.006  # paper participation (tighter than FULLA 0.02)
ADV_FLOOR_FILL = NAME_CAP_PORTFOLIO * AUM_TIER / PARTICIPATION_K  # 10,000,000
IMPACT_BUFFER = 10.0  # paper impact buffer on fill floor
ADV_MIN_YUAN = ADV_FLOOR_FILL * IMPACT_BUFFER  # 100,000,000
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
    return pd.read_parquet(f"{ROOT}/data/v2/st_events/st_events_from_namechange.parquet")


def _norm_code(x: str) -> str:
    x = str(x)
    if x[:3] in ("sh.", "sz.", "bj."):
        return x.split(".")[1] + "." + x.split(".")[0].upper()
    return x


def _st_set(S: pd.Timestamp) -> set:
    st = st_intervals()
    code = "ts_code" if "ts_code" in st.columns else "instrument_id"
    s = pd.to_datetime(st["start_date"].astype(str), errors="coerce")
    e = pd.to_datetime(st["end_date"].astype(str), errors="coerce").fillna(pd.Timestamp("2100-01-01"))
    m = (s <= S) & (e >= S)
    m &= st["name"].astype(str).str.upper().str.contains("ST")
    return {_norm_code(x) for x in st.loc[m, code]}


def _load_amount_panel(days: pd.DatetimeIndex) -> pd.DataFrame:
    """Wide panel amount in yuan: index=ts_code, columns=dates."""
    series = {}
    for d in days:
        p = f"{RAW}/daily/{d:%Y%m%d}.parquet"
        if not os.path.exists(p):
            continue
        x = pd.read_parquet(p, columns=["ts_code", "amount"])
        x = x[x.ts_code.str.endswith((".SH", ".SZ"))]
        series[pd.Timestamp(d)] = x.set_index("ts_code")["amount"] * 1000.0
    if not series:
        return pd.DataFrame()
    return pd.DataFrame(series).fillna(0.0)


def _suspend_set(S: pd.Timestamp) -> set:
    sp = f"{RAW}/suspend_d/{S:%Y%m%d}.parquet"
    if not os.path.exists(sp):
        return set()
    x = pd.read_parquet(sp)
    return set(x.loc[x.suspend_type == "S", "ts_code"].astype(str))


def build_panel(
    start: str = "2017-12-01",
    end: str | None = None,
    out: str = OUT_MASK,
) -> pd.DataFrame:
    """Daily long mask (date, instrument, in_universe + reason flags). Vectorized ADV."""
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    sess = open_sessions()
    end_ts = pd.Timestamp(end) if end else sess[sess <= pd.Timestamp.today().normalize()][-1]
    start_ts = pd.Timestamp(start)
    # need ADV_WIN sessions before first output day
    out_days = sess[(sess >= start_ts) & (sess <= end_ts)]
    if len(out_days) == 0:
        raise ValueError("no sessions in range")
    first_out = out_days[0]
    hist = sess[sess < first_out][-ADV_WIN:]
    load_days = sess[(sess >= hist[0]) & (sess <= end_ts)] if len(hist) else out_days

    print(f"[HI_LIQ] loading amounts {load_days[0].date()}→{load_days[-1].date()} ({len(load_days)} days)", flush=True)
    amt = _load_amount_panel(load_days)
    print(f"[HI_LIQ] amount panel {amt.shape}", flush=True)

    ld = list_dates()
    sess_vals = sess.values
    parts = []
    # rolling window positions in amt columns
    col_index = {c: i for i, c in enumerate(amt.columns)}
    codes = amt.index.to_numpy()
    ld_re = ld.reindex(amt.index)
    ld_vals = ld_re.values.astype("datetime64[ns]")

    for i, S in enumerate(out_days):
        prior = sess[sess < S][-ADV_WIN:]
        if len(prior) < ADV_WIN:
            continue
        cols = [col_index[p] for p in prior if p in col_index]
        if len(cols) < ADV_WIN:
            # missing days → treat as 0 via reindex
            sub = amt.reindex(columns=list(prior), fill_value=0.0)
            adv = sub.mean(axis=1).to_numpy()
            bar_prev = sub.iloc[:, -1].to_numpy() > 0
        else:
            block = amt.iloc[:, cols].to_numpy()
            adv = block.mean(axis=1)
            bar_prev = block[:, -1] > 0

        n_listed = np.searchsorted(sess_vals, S.to_datetime64()) - np.searchsorted(sess_vals, ld_vals)
        listed_sessions = np.where(ld_re.notna().to_numpy(), n_listed, -1)
        susp = _suspend_set(S)
        st_today = _st_set(S)
        suspended = np.fromiter((c in susp for c in codes), dtype=bool, count=len(codes)) | (~bar_prev)
        st = np.fromiter((c in st_today for c in codes), dtype=bool, count=len(codes))
        young = listed_sessions < MIN_LIST_SESSIONS
        adv_fail = adv < ADV_MIN_YUAN
        in_uni = ~(st | suspended | young | adv_fail)

        parts.append(
            pd.DataFrame(
                {
                    "date": S,
                    "instrument": codes,
                    "in_universe": in_uni,
                    "st": st,
                    "suspended": suspended,
                    "young": young,
                    "adv_fail": adv_fail,
                    "adv20_yuan": adv.astype("float32"),
                }
            )
        )
        if (i + 1) % 250 == 0:
            print(f"[HI_LIQ] {i+1}/{len(out_days)} {S.date()} in_uni={int(in_uni.sum())}", flush=True)

    df = pd.concat(parts, ignore_index=True)
    df.to_parquet(out, index=False)
    return df


def sanity(df: pd.DataFrame) -> dict:
    g = df.groupby("date")["in_universe"].sum()
    return {
        "rows": int(len(df)),
        "days": int(df.date.nunique()),
        "date_min": str(pd.Timestamp(df.date.min()).date()),
        "date_max": str(pd.Timestamp(df.date.max()).date()),
        "in_universe_mean": float(g.mean()),
        "in_universe_min": int(g.min()),
        "in_universe_max": int(g.max()),
        "adv_min_yuan": ADV_MIN_YUAN,
        "participation_k": PARTICIPATION_K,
        "impact_buffer": IMPACT_BUFFER,
        "adv_floor_fill": ADV_FLOOR_FILL,
    }


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2017-12-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--out", default=OUT_MASK)
    args = ap.parse_args()
    df = build_panel(start=args.start, end=args.end, out=args.out)
    meta = sanity(df)
    meta["mask_sha256"] = file_sha256(args.out)
    meta["script"] = __file__
    with open(args.out + ".meta.json", "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(json.dumps(meta, indent=2, ensure_ascii=False))
