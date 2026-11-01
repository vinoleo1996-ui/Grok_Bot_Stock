#!/usr/bin/env python3
"""Research-grade intraday minute-data monitor PROTOTYPE (on demand; no poller; risk flags only; never touches weights/NAV).
Default = dry-run: builds the code list (paper holdings latest session + 510300) and the relay request plan; no network.
--fetch: ONE on-demand relay call per code batch (rt_min 1MIN via quantlab.data_sources.tushare_proxy.relay); needs
Data's quota OK. --bars-csv: offline test with a CSV (ts_code,trade_time,close,pre_close).
Output: output/loop/intraday/plan_<ts>.json and (if bars) flags_<ts>.parquet. live=false."""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
OUT = ROOT / "output/loop/intraday"
TRACKS = {"b4": "output/strategy_paper_b4/FROZEN_CONFIG.json", "s6": "output/strategy_paper_s6/FROZEN_CONFIG.json"}
CAP_FZ = "output/loop/capacity_adv_FROZEN_CONFIG.json"
THR = dict(watch=-0.05, high=-0.08, limit_down=-0.095, etf_watch=-0.02, etf_high=-0.035)


def holdings():
    paths = []
    for t, p in TRACKS.items():
        if (ROOT / p).exists():
            for cap, w in json.loads((ROOT / p).read_text())["weights"].items(): paths.append((f"{t}_{cap}", w["path"]))
    if (ROOT / CAP_FZ).exists():
        lp = json.loads((ROOT / CAP_FZ).read_text()).get("leg_pin")
        if lp: paths.append(("capacity_adv", lp["path"]))
    rows = []
    for name, p in paths:
        w = pd.read_parquet(ROOT / p); k = w.session.astype(str).str[:10]; w = w[(k == k.max()) & (w.weight > 0)]
        col = "instrument" if "instrument" in w else "instrument_id"
        rows += [dict(track=name, ts_code=c, weight=float(x), session=k.max()) for c, x in zip(w[col], w.weight)]
    h = pd.DataFrame(rows)
    return h, sorted(set(h.ts_code) | {"510300.SH"})


def flags(bars, h):
    b = bars.sort_values("trade_time").groupby("ts_code").tail(1).copy()
    b["ret"] = b.close / b.pre_close - 1; etf = b.ts_code.str.startswith(("51", "15"))
    sev = pd.Series("info", index=b.index)
    sev[(~etf) & (b.ret <= THR["watch"])] = "watch"; sev[(~etf) & (b.ret <= THR["high"])] = "high"
    sev[etf & (b.ret <= THR["etf_watch"])] = "watch"; sev[etf & (b.ret <= THR["etf_high"])] = "high"
    b["severity"] = sev; b["near_limit_down"] = (~etf) & (b.ret <= THR["limit_down"])
    b["scope"] = etf.map({True: "market", False: "stock"})
    b = b.merge(h.groupby("ts_code").track.apply(lambda s: ",".join(sorted(set(s)))).rename("tracks"), on="ts_code", how="left")
    b["risk_flag_only"] = True; b["source"] = "rt_min_1MIN_relay"
    return b[["ts_code", "trade_time", "close", "pre_close", "ret", "severity", "near_limit_down", "scope", "tracks", "risk_flag_only", "source"]]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fetch", action="store_true"); ap.add_argument("--bars-csv")
    a = ap.parse_args(); ts = datetime.now().strftime("%Y%m%d_%H%M%S"); OUT.mkdir(parents=True, exist_ok=True)
    h, codes = holdings()
    plan = dict(mode="fetch" if a.fetch else ("offline_csv" if a.bars_csv else "dry_run"), api="rt_min", freq="1MIN", source="relay",
                n_codes=len(codes), codes=codes, batches=[codes[i:i + 50] for i in range(0, len(codes), 50)], thresholds=THR,
                live=False, writes_weights=False, poller=False, holdings_sessions=sorted(h.session.unique().tolist()))
    (OUT / f"plan_{ts}.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    bars = None
    if a.bars_csv: bars = pd.read_csv(a.bars_csv)
    elif a.fetch:
        from quantlab.data_sources.tushare_proxy import relay
        bars = pd.concat([relay("rt_min", ts_code=",".join(b), freq="1MIN") for b in plan["batches"]], ignore_index=True)
    if bars is not None:
        f = flags(bars, h); f.to_parquet(OUT / f"flags_{ts}.parquet", index=False)
        print(f.severity.value_counts().to_dict())
    print(json.dumps({k: plan[k] for k in ("mode", "n_codes", "holdings_sessions")}, ensure_ascii=False), str(OUT / f"plan_{ts}.json"))


if __name__ == "__main__":
    main()
