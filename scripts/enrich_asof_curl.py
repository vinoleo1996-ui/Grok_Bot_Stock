#!/usr/bin/env python3
"""Sequential EastMoney enrich for asof_extend panels (post-restart resume)."""
from __future__ import annotations
import json, subprocess, time, random
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
PANELS = ROOT / "data/v2/asof_extend_202610/panels"
FM_OUT = ROOT / "data/v2/float_mktcap"
LOG = ROOT / "data/_acquire_logs"
EXT = ROOT / "data/v2/asof_extend_202610"
SH = ZoneInfo("Asia/Shanghai"); NY = ZoneInfo("America/New_York")
START, END = "20260701", "20261009"
SLEEP = 0.45
HARD_STOP_STREAK = 50
CHECKPOINT_EVERY = 100

def secid(iid: str) -> str | None:
    mkt, code = iid.split(".", 1)
    return {"sh": f"1.{code}", "sz": f"0.{code}", "bj": f"0.{code}"}.get(mkt)

def limit_ratio(iid: str, is_st: bool) -> float:
    if is_st: return 0.05
    code, mkt = iid.split(".")[1], iid.split(".")[0]
    if mkt == "bj": return 0.30
    if code.startswith(("300", "301", "688", "689")): return 0.20
    return 0.10

def fetch_em(iid: str) -> pd.DataFrame:
    sid = secid(iid)
    if not sid: return pd.DataFrame()
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
        f"fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&ut=fa5fd1943c7b386f172d6893dbfba10b&klt=101&fqt=0&secid={sid}"
        f"&beg={START}&end={END}&lmt=1000000"
    )
    last = None
    for attempt in range(5):
        try:
            proc = subprocess.run(
                ["curl", "-sS", "-m", "35", "--http1.1", "--retry", "0",
                 "-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 "-e", "https://quote.eastmoney.com/", url],
                capture_output=True, check=False,
            )
            if proc.returncode != 0 or not (proc.stdout or b"").strip():
                last = (proc.stderr or b"").decode(errors="replace")[:160] or f"rc={proc.returncode}"
                time.sleep(2.0 * (attempt + 1) + random.random())
                continue
            payload = json.loads(proc.stdout)
            data = payload.get("data") or {}
            name = data.get("name") or ""
            rows = []
            for line in data.get("klines") or []:
                p = line.split(",")
                if len(p) < 11: continue
                rows.append(dict(date=p[0], close=float(p[2]), amount=float(p[6]),
                                 turnover=float(p[10]), name=name))
            return pd.DataFrame(rows)
        except Exception as e:
            last = repr(e)
            time.sleep(2.0 * (attempt + 1) + random.random())
    raise RuntimeError(f"em_fail:{iid}:{last}")

def enrich_one(path: Path) -> dict:
    iid = path.stem
    try:
        panel = pd.read_parquet(path)
        em = fetch_em(iid)
        if em.empty:
            return {"instrument_id": iid, "ok": True, "amount_nn": 0, "note": "em_empty"}
        em["date"] = pd.to_datetime(em["date"])
        panel = panel.copy()
        panel["event_time"] = pd.to_datetime(panel["event_time"])
        name = str(em["name"].iloc[-1])
        is_st = "ST" in name.upper()
        lr = limit_ratio(iid, is_st)
        m = panel.merge(
            em[["date", "amount", "turnover", "close"]].rename(
                columns={"date": "event_time", "amount": "a_em", "turnover": "t_em", "close": "c_em"}),
            on="event_time", how="left")
        m["amount"] = m["a_em"]
        m["turnover"] = m["t_em"]
        em2 = em.sort_values("date")
        em2["prev_close"] = em2["close"].shift(1)
        m = m.merge(em2[["date", "prev_close"]].rename(columns={"date": "event_time"}),
                    on="event_time", how="left")
        tick = 0.01
        m["limit_up"] = (m["prev_close"] * (1 + lr) / tick).round() * tick
        m["limit_down"] = (m["prev_close"] * (1 - lr) / tick).round() * tick
        m["is_st_at_open"] = float(1.0 if is_st else 0.0)
        m["limit_ratio_at_open"] = lr
        m["quality_status"] = "research_not_promotable:tencent_ohlc_em_amount_turnover_derived_limits"
        m["source"] = "tencent_ifzq+eastmoney_push2his_curl"
        m = m.drop(columns=[c for c in ["a_em", "t_em", "c_em", "prev_close"] if c in m.columns])
        m.to_parquet(path, index=False)
        fm_rows = []
        for _, r in m.iterrows():
            amt, turn = r.get("amount"), r.get("turnover")
            fm = np.nan
            if pd.notna(amt) and pd.notna(turn) and float(turn) > 0:
                fm = float(amt) * 100.0 / float(turn)
            fm_rows.append(dict(
                instrument_id=iid,
                session=pd.Timestamp(r["event_time"]).date(),
                float_mktcap=fm,
                available_at=datetime.combine(pd.Timestamp(r["event_time"]).date(), dtime(18, 0), tzinfo=SH),
                source="derived_amount_over_turnover_percent_em",
                revision="asof_extend_em_curl_post_restart_v1",
                quality_status="research_not_promotable:derived_proxy_not_official_float",
            ))
        return {"instrument_id": iid, "ok": True, "amount_nn": int(m["amount"].notna().sum()),
                "rows": len(m), "is_st": is_st, "fm_rows": fm_rows}
    except Exception as e:
        return {"instrument_id": iid, "ok": False, "error": repr(e), "fm_rows": []}

def checkpoint_fm(fm_buf, NOW):
    if not fm_buf:
        return None
    FM_OUT.mkdir(parents=True, exist_ok=True)
    fm = pd.DataFrame(fm_buf)
    daily = FM_OUT / "float_mktcap_daily_20260630_20261009.parquet"
    parts = [fm]
    if daily.exists():
        old = pd.read_parquet(daily)
        old["session"] = pd.to_datetime(old["session"]).dt.date
        parts.append(old)
    all_fm = pd.concat(parts, ignore_index=True)
    all_fm["_pref"] = all_fm["source"].astype(str).str.contains("turnover").astype(int)
    all_fm = (all_fm.sort_values(["instrument_id", "session", "_pref"])
              .drop_duplicates(["instrument_id", "session"], keep="last")
              .drop(columns=["_pref"]))
    cols = ["instrument_id", "session", "float_mktcap", "available_at", "source", "revision", "quality_status"]
    all_fm = all_fm[cols]
    max_sess = max(all_fm["session"])
    latest = all_fm[all_fm["session"] == max_sess]
    all_fm.to_parquet(daily, index=False)
    latest.to_parquet(FM_OUT / "float_mktcap_asof.parquet", index=False)
    meta = dict(
        schema_version="quantlab.v2.float_mktcap.v1", field="float_mktcap", unit="CNY",
        promotion_approved=False, daily_path=str(daily),
        asof_path=str(FM_OUT / "float_mktcap_asof.parquet"),
        session_min=str(min(all_fm["session"])), session_max=str(max_sess),
        daily_rows=int(len(all_fm)), daily_non_null=int(all_fm["float_mktcap"].notna().sum()),
        asof_non_null=int(latest["float_mktcap"].notna().sum()),
        fetch_time=NOW.isoformat(),
        limitations=["research_not_promotable", "EM enrich partial under SSL limits"],
    )
    (FM_OUT / "manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    return meta

def main():
    NOW = datetime.now(NY)
    LOG.mkdir(parents=True, exist_ok=True)
    progress = LOG / "asof_enrich_curl_progress.jsonl"
    with progress.open("a") as f:
        f.write(json.dumps({"run_start": NOW.isoformat(), "mode": "sequential_post_restart"}) + "\n")
    paths = sorted(PANELS.glob("*.parquet"))
    todo = []
    for p in paths:
        df = pd.read_parquet(p, columns=["amount"])
        if df["amount"].notna().mean() < 0.5:
            todo.append(p)
    print(json.dumps({"todo": len(todo), "total": len(paths), "workers": 1, "sleep": SLEEP,
                      "promotion_approved": False}), flush=True)
    fm_buf = []; ok = fail = streak = 0
    for i, p in enumerate(todo, 1):
        r = enrich_one(p)
        fm_rows = r.pop("fm_rows", [])
        if r.get("ok") and r.get("amount_nn", 0) > 0:
            ok += 1; streak = 0; fm_buf.extend(fm_rows)
        elif r.get("ok"):
            ok += 1; streak = 0
        else:
            fail += 1; streak += 1
        with progress.open("a") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if i <= 10 or i % 20 == 0 or i == len(todo):
            print(json.dumps({"done": i, "todo": len(todo), "ok": ok, "fail": fail,
                              "streak_fail": streak, "last": r.get("instrument_id"),
                              "last_ok": r.get("ok"), "amount_nn": r.get("amount_nn")}), flush=True)
        if i % CHECKPOINT_EVERY == 0:
            meta = checkpoint_fm(fm_buf, NOW)
            if meta:
                print(json.dumps({"checkpoint_fm": {k: meta[k] for k in ["daily_rows", "asof_non_null"]}}), flush=True)
        if streak >= HARD_STOP_STREAK:
            print(json.dumps({"hard_stop": True, "streak": streak, "done": i, "ok": ok, "fail": fail}), flush=True)
            # cool down then continue once more after pause
            time.sleep(30)
            streak = 0
            print(json.dumps({"resume_after_cooldown": True}), flush=True)
            # don't break — keep going after cooldown; only stop if still failing next 50
        time.sleep(SLEEP + random.random() * 0.2)

    meta = checkpoint_fm(fm_buf, NOW)
    nn = sum(1 for p in paths if pd.read_parquet(p, columns=["amount"])["amount"].notna().mean() >= 0.5)
    summary = dict(ok=ok, fail=fail, todo=len(todo), amount_panels=nn, total_panels=len(paths),
                   promotion_approved=False, fetch_time=NOW.isoformat(), method="curl_sequential_post_restart",
                   fm_meta=meta)
    (LOG / "asof_enrich_curl_latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (EXT / "enrich_manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"done": True, "amount_panels": nn, "total": len(paths), "ok": ok, "fail": fail}), flush=True)

if __name__ == "__main__":
    main()
