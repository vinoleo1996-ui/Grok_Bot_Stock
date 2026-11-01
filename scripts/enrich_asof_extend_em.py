#!/usr/bin/env python3
"""Enrich asof_extend panels with EastMoney amount/turnover; derive limits/ST/float_mktcap.

Free-only. Research-grade. Does not mutate 1c85.
Writes enriched panels in-place under data/v2/asof_extend_202610/panels/
and daily float_mktcap under data/v2/float_mktcap/.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
EXT = ROOT / "data/v2/asof_extend_202610"
PANELS = EXT / "panels"
D0 = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec"
FM_OUT = ROOT / "data/v2/float_mktcap"
LOG = ROOT / "data/_acquire_logs"
SH = ZoneInfo("Asia/Shanghai")
NY = ZoneInfo("America/New_York")
START, END = "20260701", "20261009"
WORKERS = 4

# EastMoney secid: 1.600000 SH, 0.000001 SZ, 0.430017 BJ?
def secid(instrument_id: str) -> str | None:
    mkt, code = instrument_id.split(".", 1)
    if mkt == "sh":
        return f"1.{code}"
    if mkt == "sz":
        return f"0.{code}"
    if mkt == "bj":
        return f"0.{code}"
    return None


def limit_ratio_for(instrument_id: str, is_st: bool) -> float:
    if is_st:
        return 0.05
    code = instrument_id.split(".", 1)[1]
    mkt = instrument_id.split(".", 1)[0]
    if mkt == "bj" or code.startswith(("300", "301", "688", "689")):
        # ChiNext / STAR often 20%; BJ 30% — research approx
        if mkt == "bj":
            return 0.30
        return 0.20
    return 0.10


def fetch_em_kline(instrument_id: str) -> pd.DataFrame:
    sid = secid(instrument_id)
    if not sid:
        return pd.DataFrame()
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": "101",
        "fqt": "0",  # raw
        "secid": sid,
        "beg": START,
        "end": END,
        "lmt": "1000000",
    }
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                payload = json.loads(resp.read())
            data = (payload.get("data") or {})
            klines = data.get("klines") or []
            name = data.get("name") or ""
            rows = []
            for line in klines:
                parts = line.split(",")
                # date, open, close, high, low, volume, amount, amplitude, pct_chg, chg, turnover
                if len(parts) < 11:
                    continue
                rows.append({
                    "date": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "volume": float(parts[5]),  # 手
                    "amount": float(parts[6]),  # CNY
                    "turnover": float(parts[10]),  # percent
                    "name": name,
                })
            return pd.DataFrame(rows)
        except Exception as exc:
            last = exc
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"em_fail:{instrument_id}:{last!r}")


def enrich_one(path: Path, st_codes: set[str]) -> dict:
    iid = path.stem
    try:
        panel = pd.read_parquet(path)
        em = fetch_em_kline(iid)
    except Exception as exc:
        return {"instrument_id": iid, "ok": False, "error": repr(exc)}
    if em.empty:
        return {"instrument_id": iid, "ok": True, "rows": 0, "note": "em_empty"}
    em["date"] = pd.to_datetime(em["date"])
    panel = panel.copy()
    panel["event_time"] = pd.to_datetime(panel["event_time"])
    # name-based ST
    name = str(em["name"].iloc[-1]) if "name" in em.columns and len(em) else ""
    code = iid.split(".", 1)[1]
    is_st = ("ST" in name.upper()) or (code in st_codes)
    lr = limit_ratio_for(iid, is_st)

    merged = panel.merge(
        em[["date", "amount", "turnover", "close"]].rename(
            columns={"date": "event_time", "amount": "amount_em", "turnover": "turnover_em", "close": "close_em"}
        ),
        on="event_time",
        how="left",
    )
    # fill amount/turnover from EM
    merged["amount"] = merged["amount_em"]
    merged["turnover"] = merged["turnover_em"]
    # limit from prior close * (1±ratio); use EM close series sorted
    em_sorted = em.sort_values("date")
    em_sorted["prev_close"] = em_sorted["close"].shift(1)
    lim = em_sorted[["date", "prev_close"]].rename(columns={"date": "event_time"})
    merged = merged.merge(lim, on="event_time", how="left")
    # tick rounding research approx 0.01
    tick = 0.01
    merged["limit_up"] = (merged["prev_close"] * (1 + lr) / tick).round() * tick
    merged["limit_down"] = (merged["prev_close"] * (1 - lr) / tick).round() * tick
    merged["is_st_at_open"] = float(1.0 if is_st else 0.0)
    merged["limit_ratio_at_open"] = lr
    merged["quality_status"] = "research_not_promotable:tencent_ohlc_em_amount_turnover_derived_limits"
    merged["source"] = "tencent_ifzq+eastmoney_push2his"
    # drop helpers
    merged = merged.drop(columns=[c for c in ["amount_em", "turnover_em", "close_em", "prev_close"] if c in merged.columns])
    merged.to_parquet(path, index=False)

    # float_mktcap rows for this instrument
    fm_rows = []
    for _, r in merged.iterrows():
        amt, turn = r.get("amount"), r.get("turnover")
        fm = np.nan
        if pd.notna(amt) and pd.notna(turn) and float(turn) > 0:
            fm = float(amt) * 100.0 / float(turn)  # turnover percent
        fm_rows.append({
            "instrument_id": iid,
            "session": pd.Timestamp(r["event_time"]).date(),
            "float_mktcap": fm,
            "available_at": datetime.combine(pd.Timestamp(r["event_time"]).date(), dtime(18, 0), tzinfo=SH),
            "source": "derived_amount_over_turnover_percent_em",
            "revision": "asof_extend_em_enrich_v1",
            "quality_status": "research_not_promotable:derived_proxy_not_official_float",
        })
    return {
        "instrument_id": iid,
        "ok": True,
        "rows": int(len(merged)),
        "amount_nn": int(merged["amount"].notna().sum()),
        "turnover_nn": int(merged["turnover"].notna().sum()),
        "is_st": is_st,
        "fm_rows": fm_rows,
    }


def load_st_codes() -> set[str]:
    # From D0 panels: any is_st_at_open==1 on last day; plus name heuristics later
    codes = set()
    try:
        inst = pd.read_parquet(D0 / "instruments.parquet")
        # no reliable is_st column (all null) — skip
    except Exception:
        pass
    # try github/OSS style local if any
    for p in [
        EXT / "st_list_em_snapshot.parquet",
        ROOT / "data/v2/asof_extend_202610/st_codes.txt",
    ]:
        if p.suffix == ".parquet" and p.exists():
            df = pd.read_parquet(p)
            for col in df.columns:
                if "代码" in col or col.lower() in {"code", "symbol", "证券代码"}:
                    codes |= set(df[col].astype(str).str.zfill(6))
        elif p.exists() and p.suffix == ".txt":
            codes |= set(p.read_text().split())
    return codes


def main():
    NOW = datetime.now(NY)
    LOG.mkdir(parents=True, exist_ok=True)
    FM_OUT.mkdir(parents=True, exist_ok=True)
    st_codes = load_st_codes()
    paths = sorted(PANELS.glob("*.parquet"))
    # resume: skip if amount already mostly filled
    todo = []
    for p in paths:
        df = pd.read_parquet(p, columns=["amount"])
        if df["amount"].notna().mean() < 0.5:
            todo.append(p)
    print(json.dumps({"n_panels": len(paths), "todo": len(todo), "st_codes": len(st_codes)}, ensure_ascii=False), flush=True)

    progress = LOG / "asof_enrich_progress.jsonl"
    fm_buffer = []
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(enrich_one, p, st_codes): p for p in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            fm_rows = r.pop("fm_rows", []) if isinstance(r, dict) else []
            if r.get("ok"):
                ok += 1
                fm_buffer.extend(fm_rows)
            else:
                fail += 1
            with progress.open("a") as f:
                f.write(json.dumps({k: v for k, v in r.items() if k != "fm_rows"}, ensure_ascii=False) + "\n")
            if i % 100 == 0 or i == len(futs):
                print(json.dumps({"done": i, "todo": len(todo), "ok": ok, "fail": fail, "fm_buf": len(fm_buffer)}, ensure_ascii=False), flush=True)
            time.sleep(0.15)

    # Write daily float_mktcap for extend window
    if fm_buffer:
        fm = pd.DataFrame(fm_buffer)
        # also append 2026-06-30 snapshot if present
        old = FM_OUT / "float_mktcap_asof_2026-06-30.parquet"
        parts = [fm]
        if old.exists():
            prev = pd.read_parquet(old)
            # normalize session
            prev["session"] = pd.to_datetime(prev["session"]).dt.date
            parts.append(prev)
        all_fm = pd.concat(parts, ignore_index=True)
        all_fm = all_fm.drop_duplicates(["instrument_id", "session"], keep="last")
        # Eng schema columns only
        all_fm = all_fm[["instrument_id", "session", "float_mktcap", "available_at", "source", "revision", "quality_status"]]
        daily_path = FM_OUT / "float_mktcap_daily_20260630_20261009.parquet"
        asof_latest = FM_OUT / "float_mktcap_asof.parquet"
        # latest session snapshot for Eng asof file
        max_sess = max(all_fm["session"])
        latest = all_fm[all_fm["session"] == max_sess].copy()
        all_fm.to_parquet(daily_path, index=False)
        latest.to_parquet(asof_latest, index=False)
        latest.to_parquet(FM_OUT / f"float_mktcap_asof_{max_sess}.parquet", index=False)
        meta = {
            "schema_version": "quantlab.v2.float_mktcap.v1",
            "field": "float_mktcap",
            "unit": "CNY",
            "promotion_approved": False,
            "daily_path": str(daily_path),
            "asof_path": str(asof_latest),
            "session_min": str(min(all_fm["session"])),
            "session_max": str(max_sess),
            "daily_rows": int(len(all_fm)),
            "daily_non_null": int(all_fm["float_mktcap"].notna().sum()),
            "asof_rows": int(len(latest)),
            "asof_non_null": int(latest["float_mktcap"].notna().sum()),
            "formula": "float_mktcap = amount * 100 / turnover  (turnover in percent; amount CNY from EastMoney)",
            "sources": ["eastmoney_push2his_kline", "optional_prior_2026-06-30_d0_derived"],
            "limitations": [
                "research_not_promotable derived proxy — not exchange free-float shares * price",
                "turnover/amount from EM; OHLC on panels may still be Tencent",
                "ST/limit flags research approx",
            ],
            "fetch_time": NOW.isoformat(),
        }
        (FM_OUT / "manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"float_mktcap": meta}, ensure_ascii=False), flush=True)

    summary = {
        "fetch_time": NOW.isoformat(),
        "enriched_ok": ok,
        "enriched_fail": fail,
        "todo": len(todo),
        "promotion_approved": False,
        "panels_dir": str(PANELS),
    }
    (LOG / "asof_enrich_latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (EXT / "enrich_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"done": True, **summary}, ensure_ascii=False))


if __name__ == "__main__":
    main()
