"""Pull Tushare moneyflow by trade_date → raw day files, then build PIT parquet.
Rate-limit friendly: long sleep, small chunks, skip existing. Shares pool with hsgt_top10.
"""
from __future__ import annotations
import json, os, sys, time, pathlib, datetime as dt
ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))
import pandas as pd
from quantlab.data_sources.tushare_proxy import relay, datahub, _to_df

RAW = ROOT / "data/v2/tushare_raw/moneyflow"
OUT = ROOT / "data/v2/moneyflow/moneyflow_stock_daily_pit.parquet"
MAN = ROOT / "data/v2/moneyflow/manifest.json"
PROG = ROOT / "output/d1/moneyflow_pull_progress.json"
LOG = ROOT / "logs/moneyflow_stock_pull.log"
RAW.mkdir(parents=True, exist_ok=True)
(ROOT / "output/d1").mkdir(parents=True, exist_ok=True)
(ROOT / "logs").mkdir(parents=True, exist_ok=True)

SLEEP = float(os.environ.get("MF_SLEEP", "2.5"))
CHUNK = int(os.environ.get("MF_CHUNK", "15"))  # days per invoke
START = os.environ.get("MF_START", "20180102")
END = os.environ.get("MF_END", "")
REBUILD = os.environ.get("MF_REBUILD", "0") == "1"


def log(msg):
    line = f"{dt.datetime.now().isoformat()} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def trade_days(a, b):
    c = pd.read_parquet(ROOT / "data/v2/tushare_raw/trade_cal.parquet")
    c = c[c.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)


def latest_open():
    c = pd.read_parquet(ROOT / "data/v2/tushare_raw/trade_cal.parquet")
    c = c[c.is_open.astype(int) == 1]
    today = pd.Timestamp.now(tz="Asia/Shanghai").strftime("%Y%m%d")
    days = sorted(d for d in c.cal_date.astype(str) if d <= today)
    return days[-1] if days else today


def needs(d, min_ok=50_000):
    f = RAW / f"{d}.parquet"
    return (not f.exists()) or f.stat().st_size < min_ok


def save_day(d, df):
    f = RAW / f"{d}.parquet"
    x = df.replace("", None)
    for c in x.columns:
        if x[c].dtype == object and c not in ("ts_code", "trade_date"):
            n = pd.to_numeric(x[c], errors="coerce")
            if n.notna().sum() >= max(1, int(x[c].notna().sum() * 0.5)):
                x[c] = n
    tmp = f.with_suffix(".tmp.parquet")
    x.to_parquet(tmp, index=False)
    os.replace(tmp, f)
    return len(x)


def _mf_call(api_fn, d, off, page):
    return api_fn("moneyflow", trade_date=d, limit=page, offset=off)

def pull_day(d):
    """Prefer datahub (more stable); fall back to PCD relay. Smaller pages avoid timeouts."""
    page = int(os.environ.get("MF_PAGE", "2000"))
    backends = [("datahub", datahub), ("relay", relay)]
    prefer = os.environ.get("MF_BACKEND", "datahub").strip().lower()
    if prefer == "relay":
        backends = [("relay", relay), ("datahub", datahub)]
    last_err = None
    for bname, bfn in backends:
        out, off = [], 0
        for attempt in range(8):
            try:
                while True:
                    s, raw = _mf_call(bfn, d, off, page)
                    err = ""
                    if isinstance(raw, dict):
                        err = str(raw.get("error") or raw.get("msg") or "")
                    if s in (429, 503, 504) or "pool" in err.lower() or "exhausted" in err.lower() or "busy" in err.lower():
                        raise RuntimeError(f"rate/pool {s} {err[:120]}")
                    if s == 403:
                        raise RuntimeError(f"forbidden {s} {err[:120]}")
                    if s != 200 or (isinstance(raw, dict) and raw.get("code") not in (0, None)):
                        raise RuntimeError(f"bad {s} {err[:120]}")
                    df = _to_df(raw) if isinstance(raw, dict) else pd.DataFrame()
                    out.append(df)
                    if len(df) < page:
                        break
                    off += page
                    time.sleep(0.25)
                if out:
                    log(f"  backend={bname} day={d} pages_ok")
                    df = pd.concat(out, ignore_index=True)
                    df.attrs["backend"] = bname
                    return df
                return pd.DataFrame()
            except Exception as e:
                last_err = e
                wait = min(180, 6 * (2 ** attempt))
                log(f"  retry {d} backend={bname} attempt={attempt} wait={wait}s err={str(e)[:160]}")
                time.sleep(wait)
                out, off = [], 0
        log(f"  backend={bname} exhausted for {d}, trying next")
    log(f"  FAIL {d} last={last_err}")
    return None


def next_open_map(days):
    """Map trade_date YYYYMMDD -> next open day Timestamp for available_at."""
    # days sorted
    nxt = {}
    for i, d in enumerate(days):
        if i + 1 < len(days):
            nxt[d] = days[i + 1]
        else:
            # last: +1 calendar business approx — use same day +1 open unknown; set next cal open if any else d
            nxt[d] = d  # will bump to 09:00 next; for last day use +1 calendar day 09:00
    return nxt


def to_iid(ts):
    code, mkt = str(ts).split(".")
    return f"{mkt.lower()}.{code}"


def rebuild_pit(end):
    files = sorted(RAW.glob("*.parquet"))
    if not files:
        log("no raw files to rebuild")
        return False
    # all open days for next-open map
    all_days = trade_days("20100101", end)
    nxt = {}
    for i, d in enumerate(all_days):
        nxt[d] = all_days[i + 1] if i + 1 < len(all_days) else None

    parts = []
    for f in files:
        d = f.stem
        if d < START or d > end:
            continue
        df = pd.read_parquet(f)
        if df.empty:
            continue
        # exclude BJ if present
        df = df[~df.ts_code.astype(str).str.endswith(".BJ")].copy()
        df["instrument_id"] = df["ts_code"].map(to_iid)
        df["trade_date"] = df["trade_date"].astype(str)
        nd = nxt.get(d)
        if nd is None:
            # last known: next calendar day 09:00
            avail = pd.Timestamp(d) + pd.Timedelta(days=1)
            avail = avail.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=9)
        else:
            avail = pd.Timestamp(nd).tz_localize("Asia/Shanghai") + pd.Timedelta(hours=9)
        df["available_at"] = avail
        df["session"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        parts.append(df)
    if not parts:
        return False
    out = pd.concat(parts, ignore_index=True)
    # column order
    prefer = [
        "session", "trade_date", "instrument_id", "ts_code",
        "buy_elg_amount", "sell_elg_amount", "buy_lg_amount", "sell_lg_amount",
        "buy_md_amount", "sell_md_amount", "buy_sm_amount", "sell_sm_amount",
        "buy_elg_vol", "sell_elg_vol", "buy_lg_vol", "sell_lg_vol",
        "buy_md_vol", "sell_md_vol", "buy_sm_vol", "sell_sm_vol",
        "net_mf_amount", "net_mf_vol", "available_at",
    ]
    cols = [c for c in prefer if c in out.columns] + [c for c in out.columns if c not in prefer]
    out = out[cols].sort_values(["trade_date", "instrument_id"]).reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp.parquet")
    out.to_parquet(tmp, index=False)
    os.replace(tmp, OUT)
    man = {
        "path": str(OUT),
        "rows": int(len(out)),
        "instruments": int(out.instrument_id.nunique()),
        "trade_date_min": str(out.trade_date.min()),
        "trade_date_max": str(out.trade_date.max()),
        "available_at_min": str(out.available_at.min()),
        "available_at_max": str(out.available_at.max()),
        "available_at_rule": "Tushare moneyflow updates ~19:00 on trade_date; available_at = next A-share open day 09:00 Asia/Shanghai (open decision). Do not join on naked trade_date for same-session signals.",
        "source": "tushare.moneyflow via pcd relay",
        "units": "amount fields in 万元; vol in 手",
        "promotion_approved": False,
        "raw_dir": str(RAW),
        "raw_days": int(len(files)),
        "built_at": dt.datetime.now().astimezone().isoformat(),
    }
    MAN.write_text(json.dumps(man, indent=2, ensure_ascii=False))
    log(f"REBUILD ok rows={len(out)} dates={out.trade_date.min()}..{out.trade_date.max()} instruments={out.instrument_id.nunique()}")
    return True


def main():
    end = END or latest_open()
    days = trade_days(START, end)
    missing = [d for d in days if needs(d)]
    log(f"START moneyflow pull missing={len(missing)}/{len(days)} start={START} end={end} chunk={CHUNK} sleep={SLEEP}")
    PROG.write_text(json.dumps({"missing": len(missing), "total": len(days), "end": end}, indent=2))
    if REBUILD and not missing:
        rebuild_pit(end)
        return 0
    got = 0
    for d in missing[:CHUNK]:
        df = pull_day(d)
        if df is None:
            log(f"FAIL {d}")
            PROG.write_text(json.dumps({"last_fail": d, "got": got, "remaining_est": len(missing) - got}, indent=2))
            return 2
        n = save_day(d, df)
        got += 1
        backend = getattr(df, "attrs", {}).get("backend", os.environ.get("MF_BACKEND", "datahub"))
        log(f"OK {d} rows={n} backend={backend}")
        PROG.write_text(json.dumps({
            "last_ok": d, "got": got, "chunk": CHUNK,
            "remaining_est": max(0, len(missing) - got),
            "end": end,
            "backend_last": backend,
            "backends": "datahub,relay",
            "updated_at": dt.datetime.now().astimezone().isoformat(),
        }, indent=2))
        time.sleep(SLEEP)
    still = [d for d in days if needs(d)]
    if not still:
        rebuild_pit(end)
        log("COMPLETE")
        return 0
    # partial rebuild every chunk so consumers can start
    rebuild_pit(end)
    log(f"MORE remaining={len(still)}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
