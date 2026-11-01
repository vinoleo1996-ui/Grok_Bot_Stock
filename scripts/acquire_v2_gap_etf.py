#!/usr/bin/env python3
"""V2 gap acquire: 510300 + equity ETFs via Tencent + BaoStock; no invented rows."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path("/workspace/QuantLab")
ETF_DIR = ROOT / "data/etf"
BENCH = ROOT / "data/bench"
RAW = ETF_DIR / "raw_tencent"
LOG = ROOT / "data/_acquire_logs"
TZ = ZoneInfo("America/New_York")
NOW = datetime.now(TZ)
FETCH_TIME = NOW.isoformat()
ASOF_TARGET = "2026-10-09"  # last trading day before today (Sat)

URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,{start},{end},640,{fq}"

# Equity A-share ETFs (Mandate beta / liquid universe). Exclude QDII/commodity/bond.
EQUITY_ETFS = {
    "sh510300": "csi300_etf",
    "sh510310": "csi300_etf_efund",
    "sh510330": "csi300_etf_huaan",
    "sh510500": "csi500_etf",
    "sh512100": "csi1000_etf",
    "sh510050": "sse50_etf",
    "sh588000": "star50_etf",
    "sh512880": "securities_etf",
    "sh512480": "semiconductor_etf",
    "sh512660": "defense_etf",
    "sh510880": "dividend_etf",
    "sh512890": "dividend_lowvol_etf",
    "sz159915": "chinext_etf",
    "sz159919": "csi300_etf_sz",
    "sz159922": "csi500_etf_sz",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_tencent(code: str, year: int, fq: str) -> bytes:
    url = URL.format(code=code, start=f"{year}-01-01", end=f"{year}-12-31", fq=fq)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 QuantLabAcquire/1.0"})
    last_err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:
            last_err = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"tencent_fetch_failed:{code}:{year}:{fq}:{last_err!r}")


def parse_tencent(payload: bytes, code: str, fq: str) -> list[dict]:
    data = json.loads(payload).get("data")
    if not isinstance(data, dict) or code not in data:
        return []
    key = {"": "day", "hfq": "hfqday", "qfq": "qfqday"}.get(fq, "day")
    rows = data[code].get(key) or data[code].get("day") or []
    out = []
    for row in rows:
        # Tencent: date, open, close, high, low, volume [, amount?]
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


def collect_tencent_code(code: str, name: str, first_year=2012, last_year=2026) -> pd.DataFrame:
    RAW.mkdir(parents=True, exist_ok=True)
    parts = {}
    errors = []
    for fq in ("", "hfq"):
        rows = []
        for year in range(first_year, last_year + 1):
            tag = fq or "raw"
            archived = sorted(RAW.glob(f"{code}_{tag}_{year}_*.json"))
            try:
                if archived:
                    payload = archived[-1].read_bytes()
                else:
                    payload = fetch_tencent(code, year, fq)
                    digest = hashlib.sha256(payload).hexdigest()[:16]
                    (RAW / f"{code}_{tag}_{year}_{digest}.json").write_bytes(payload)
                    time.sleep(0.35)
                rows.extend(parse_tencent(payload, code, fq))
            except Exception as exc:
                errors.append({"code": code, "year": year, "fq": tag, "error": repr(exc)})
        if not rows:
            parts[fq or "raw"] = pd.DataFrame(columns=["date", "open", "close", "high", "low", "volume"])
        else:
            parts[fq or "raw"] = pd.DataFrame(rows).drop_duplicates("date").set_index("date")
    raw = parts["raw"]
    hfq = parts["hfq"]
    if raw.empty and hfq.empty:
        return pd.DataFrame(), errors
    frame = raw.rename(columns={
        "open": "open_raw", "close": "close_raw", "high": "high_raw",
        "low": "low_raw", "volume": "volume", "amount": "amount",
    })
    if not hfq.empty:
        frame = frame.join(
            hfq[["open", "close", "high", "low"]].rename(columns={
                "open": "open_hfq", "close": "close_hfq", "high": "high_hfq", "low": "low_hfq",
            }),
            how="outer",
        )
    frame["code"] = code
    frame["asset"] = name
    frame["source"] = "tencent_ifzq"
    return frame.reset_index(), errors


def write_manifest(path: Path, meta: dict) -> None:
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    all_errors = []
    summaries = []

    # --- Priority 1: 510300 ---
    code510, name510 = "sh510300", "csi300_etf"
    df510, errs = collect_tencent_code(code510, name510)
    all_errors.extend(errs)
    out510 = ETF_DIR / "510300"
    out510.mkdir(parents=True, exist_ok=True)
    if not df510.empty:
        df510["date"] = pd.to_datetime(df510["date"])
        df510 = df510.sort_values("date")
        pq = out510 / "daily_bars.parquet"
        df510.to_parquet(pq, index=False)
        # also mirror under bench
        BENCH.mkdir(parents=True, exist_ok=True)
        bench_pq = BENCH / "510300_daily.parquet"
        df510.to_parquet(bench_pq, index=False)
        meta = {
            "dataset": "etf_510300_daily",
            "code": "sh510300",
            "source": "tencent_ifzq_fqkline",
            "fetch_time": FETCH_TIME,
            "as_of": str(df510["date"].max().date()),
            "date_min": str(df510["date"].min().date()),
            "date_max": str(df510["date"].max().date()),
            "rows": int(len(df510)),
            "columns": list(df510.columns),
            "sha256": sha256_file(pq),
            "paths": [str(pq), str(bench_pq)],
            "promotion_approved": False,
            "coverage_notes": "OHLCV from Tencent; amount present only if API returned col6; hfq joined where available. Not ledger-grade corp actions.",
        }
        write_manifest(out510 / "manifest.json", meta)
        write_manifest(BENCH / "510300_manifest.json", meta)
        summaries.append(meta)
        print(json.dumps({"ok": "510300", "rows": meta["rows"], "range": [meta["date_min"], meta["date_max"]]}, ensure_ascii=False))
    else:
        summaries.append({"ok": False, "code": "510300", "errors": errs})
        print(json.dumps({"fail": "510300", "errors": errs}, ensure_ascii=False))

    # --- Broader equity ETF panel ---
    frames = []
    for code, name in EQUITY_ETFS.items():
        if code == "sh510300" and not df510.empty:
            frames.append(df510)
            continue
        df, errs = collect_tencent_code(code, name)
        all_errors.extend(errs)
        if df.empty:
            print(json.dumps({"skip": code, "errors": errs[-2:]}, ensure_ascii=False))
            continue
        df["date"] = pd.to_datetime(df["date"])
        frames.append(df)
        print(json.dumps({"ok": code, "rows": len(df), "first": str(df["date"].min().date()), "last": str(df["date"].max().date())}, ensure_ascii=False), flush=True)

    uni_dir = ETF_DIR / "universe"
    uni_dir.mkdir(parents=True, exist_ok=True)
    if frames:
        panel = pd.concat(frames, ignore_index=True)
        panel = panel.sort_values(["code", "date"])
        pq = uni_dir / "equity_etf_daily.parquet"
        panel.to_parquet(pq, index=False)
        by_code = (
            panel.groupby("code")
            .agg(rows=("date", "count"), date_min=("date", "min"), date_max=("date", "max"), asset=("asset", "first"))
            .reset_index()
        )
        by_code["date_min"] = by_code["date_min"].dt.strftime("%Y-%m-%d")
        by_code["date_max"] = by_code["date_max"].dt.strftime("%Y-%m-%d")
        meta = {
            "dataset": "equity_etf_daily_panel",
            "source": "tencent_ifzq_fqkline",
            "fetch_time": FETCH_TIME,
            "as_of": str(panel["date"].max().date()),
            "codes": sorted(panel["code"].unique().tolist()),
            "n_codes": int(panel["code"].nunique()),
            "rows": int(len(panel)),
            "per_code": by_code.to_dict(orient="records"),
            "sha256": sha256_file(pq),
            "path": str(pq),
            "promotion_approved": False,
            "coverage_notes": "Liquid A-share equity ETFs; QDII/commodity/bond excluded from this panel.",
        }
        write_manifest(uni_dir / "manifest.json", meta)
        summaries.append(meta)

    # persist errors + run summary
    run = {
        "fetch_time": FETCH_TIME,
        "summaries": summaries,
        "errors": all_errors,
        "promotion_approved": False,
    }
    write_manifest(LOG / f"etf_tencent_{NOW.strftime('%Y%m%d_%H%M%S')}.json", run)
    write_manifest(LOG / "etf_tencent_latest.json", run)
    print(json.dumps({"done": True, "n_summaries": len(summaries), "n_errors": len(all_errors)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
