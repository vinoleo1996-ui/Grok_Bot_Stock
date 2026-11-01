#!/usr/bin/env python3
"""Incrementally extend full-market daily panels as_of past 2026-06-30 via Tencent.

Writes under data/v2/asof_extend_202610/ — does NOT mutate 1c85 originals.
No Mac CopyToBox.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
D0 = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec"
OUT = ROOT / "data/v2/asof_extend_202610"
PANELS_OUT = OUT / "panels"
LOG = ROOT / "data/_acquire_logs"
TZ = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
ASOF_OLD = pd.Timestamp("2026-06-30")
END = "2026-10-09"
URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,2026-07-01,{end},320,"
WORKERS = 24
MAX_RETRIES = 3


def to_tx(instrument_id: str) -> str | None:
    # sh.600000 -> sh600000; sz.000001 -> sz000001; bj.430017 -> bj430017
    if "." not in instrument_id:
        return None
    mkt, code = instrument_id.split(".", 1)
    if mkt not in {"sh", "sz", "bj"}:
        return None
    return f"{mkt}{code}"


def fetch_tx(code: str) -> list[dict]:
    url = URL.format(code=code, end=END)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 QuantLabExtend/1.0"})
    last = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                payload = json.loads(resp.read())
            data = payload.get("data") or {}
            if code not in data:
                return []
            rows = data[code].get("day") or []
            out = []
            for row in rows:
                if len(row) < 6:
                    continue
                item = {
                    "date": row[0],
                    "open": float(row[1]),
                    "close": float(row[2]),
                    "high": float(row[3]),
                    "low": float(row[4]),
                    "volume": float(row[5]),
                }
                if len(row) > 6 and row[6] not in (None, ""):
                    try:
                        item["amount"] = float(row[6])
                    except (TypeError, ValueError):
                        pass
                out.append(item)
            return out
        except Exception as exc:
            last = exc
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"fetch_failed:{code}:{last!r}")


def extend_one(instrument_id: str) -> dict:
    tx = to_tx(instrument_id)
    if not tx:
        return {"instrument_id": instrument_id, "ok": False, "error": "bad_id"}
    try:
        rows = fetch_tx(tx)
    except Exception as exc:
        return {"instrument_id": instrument_id, "ok": False, "error": repr(exc)}
    if not rows:
        return {"instrument_id": instrument_id, "ok": True, "rows": 0, "note": "empty"}
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] > ASOF_OLD].sort_values("date")
    if df.empty:
        return {"instrument_id": instrument_id, "ok": True, "rows": 0, "note": "no_new_after_asof"}
    # Eng-ish panel append schema (partial; amount may be null)
    panel = pd.DataFrame({
        "instrument_id": instrument_id,
        "open": df["open"],
        "high": df["high"],
        "low": df["low"],
        "close": df["close"],
        "volume": df["volume"],
        "amount": df["amount"] if "amount" in df.columns else np.nan,
        "available_at": (df["date"] + pd.Timedelta(hours=18)).dt.tz_localize(SH),
        "quality_status": "ok_incremental_tencent_post_20260630",
        "tradestatus": 1.0,
        "open_status": "derived",
        "open_status_available_at": (df["date"] + pd.Timedelta(hours=18)).dt.tz_localize(SH),
        "limit_up": np.nan,
        "limit_down": np.nan,
        "turnover": np.nan,
        "factor": np.nan,
        "event_time": df["date"].values,
        "source": "tencent_ifzq",
    })
    out_path = PANELS_OUT / f"{instrument_id}.parquet"
    panel.to_parquet(out_path, index=False)
    return {
        "instrument_id": instrument_id,
        "ok": True,
        "rows": int(len(panel)),
        "date_min": str(panel["event_time"].min().date()),
        "date_max": str(panel["event_time"].max().date()),
    }


def build_calendar() -> pd.DataFrame:
    """Extend calendar using akshare trade calendar if available, else from CSI300/ETF."""
    import akshare as ak
    try:
        cal = ak.tool_trade_date_hist_sina()
        cal["trade_date"] = pd.to_datetime(cal["trade_date"])
        cal = cal[(cal["trade_date"] >= "2014-01-01") & (cal["trade_date"] <= END)]
        out = pd.DataFrame({"session": cal["trade_date"].sort_values().unique()})
        return out
    except Exception:
        # fallback: union D0 calendar + 510300 dates
        d0 = pd.read_parquet(D0 / "calendar.parquet")
        etf = pd.read_parquet(ROOT / "data/etf/510300/sh.510300.parquet")
        sessions = pd.to_datetime(d0["session"]).tolist() + pd.to_datetime(etf["event_time"]).tolist()
        out = pd.DataFrame({"session": sorted(set(pd.to_datetime(sessions)))})
        out = out[out["session"] <= END]
        return out


def main():
    NOW = datetime.now(TZ)
    OUT.mkdir(parents=True, exist_ok=True)
    PANELS_OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)

    cal = build_calendar()
    cal_path = OUT / "calendar.parquet"
    cal.to_parquet(cal_path, index=False)
    print(json.dumps({"calendar_rows": len(cal), "min": str(cal["session"].min()), "max": str(cal["session"].max())}, ensure_ascii=False), flush=True)

    # instrument list from D0 panels directory (faster than instruments filter)
    ids = sorted(p.stem for p in (D0 / "panels").glob("*.parquet") if not p.name.startswith("sh.510300"))
    # include 510300 in extend separately already complete — skip
    progress_path = LOG / "asof_extend_progress.jsonl"
    summary_path = LOG / "asof_extend_latest.json"
    # resume: skip already written
    done = {p.stem for p in PANELS_OUT.glob("*.parquet")}
    todo = [i for i in ids if i not in done]
    print(json.dumps({"n_ids": len(ids), "already": len(done), "todo": len(todo), "workers": WORKERS}, ensure_ascii=False), flush=True)

    results = []
    ok_n = fail_n = rows_n = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(extend_one, iid): iid for iid in todo}
        for n, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            results.append(r)
            if r.get("ok") and r.get("rows", 0) >= 0 and "error" not in r:
                ok_n += 1
                rows_n += int(r.get("rows") or 0)
            else:
                fail_n += 1
            with progress_path.open("a") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if n % 200 == 0 or n == len(futs):
                print(json.dumps({"done": n, "todo": len(todo), "ok": ok_n, "fail": fail_n, "rows": rows_n}, ensure_ascii=False), flush=True)
            time.sleep(0.02)  # light pacing at collector side

    # date span summary
    maxima = []
    for p in PANELS_OUT.glob("*.parquet"):
        try:
            t = pd.read_parquet(p, columns=["event_time"])
            if len(t):
                maxima.append(pd.to_datetime(t["event_time"]).max())
        except Exception:
            pass
    as_of_new = str(max(maxima).date()) if maxima else None
    summary = {
        "fetch_time": NOW.isoformat(),
        "d0_as_of": "2026-06-30",
        "extend_end_target": END,
        "as_of_extended": as_of_new,
        "calendar_path": str(cal_path),
        "calendar_max": str(pd.to_datetime(cal["session"]).max().date()),
        "n_instruments_target": len(ids),
        "n_panels_written": len(list(PANELS_OUT.glob("*.parquet"))),
        "ok": ok_n,
        "fail": fail_n,
        "new_rows_total": rows_n,
        "panels_dir": str(PANELS_OUT),
        "promotion_approved": False,
        "notes": [
            "Incremental append only; 1c85 originals untouched",
            "Source=tencent_ifzq; amount often missing on Tencent day kline",
            "open_status=derived; mask cols incomplete vs full D0 panels",
            "Merge strategy for research: concat D0 panel[session<=2026-06-30] + extend panel[session>2026-06-30]",
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (OUT / "manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"done": True, **{k: summary[k] for k in ["as_of_extended", "n_panels_written", "new_rows_total", "fail"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
