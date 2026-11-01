#!/usr/bin/env python3
"""Book-Smoke strategy_v1 entry for a core_x2 weight parquet (research; live=false; promotion=false).

Wraps quantlab.portfolio.book_smoke (run_weight_schedule + ExecConfig.strategy_v1: next_open fills, sqrt impact k=1,
10% participation cap, lots incl. STAR 200, limit-up/down enforced, unfilled carry). Weight table passed as the
stock sleeve at 100% (an equity80 file carries its own 510300 rows). X2 only: the book module refuses SEALED.
Writes <out>/nav.csv (BOOK arm) + full engine tree; receipt stays inside <out> (no shared receipt overwritten).

  python3 scripts_eng/core_x2_book_smoke.py --weights <parquet> --aum 600000 --sleeve equity80_etf20_510300 --version v1_3

Arch P1-K5: refuses to run unless --out or --version is given explicitly; default out =
core_x2/book_smoke_{version}_{sleeve}_{aum}w/; refuses a non-empty out dir without --overwrite;
run_meta.json records sha256 / rows / date range of the input weights.
"""
import argparse, datetime, hashlib, json, resource, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quantlab.portfolio.book_smoke import run
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ok_runner_pin
PIN = ok_runner_pin.enforce(__file__, [ROOT / "output/strategy_optimizer/core_x2/ARCH_RESIGN_A_v1_3.ok"])  # refuse on runner-sha mismatch

ap = argparse.ArgumentParser()
ap.add_argument("--weights", required=True)
ap.add_argument("--aum", type=int, choices=(600000, 1000000), required=True)
ap.add_argument("--sleeve", choices=("equity_100", "equity80_etf20_510300"), required=True)
ap.add_argument("--out", default=None)
ap.add_argument("--version", default=None, help="version tag, e.g. v1_3 (default v1_3 when used without --out)")
ap.add_argument("--overwrite", action="store_true")
explicit = {x.split("=")[0] for x in sys.argv[1:]}
a = ap.parse_args()
if "--out" not in explicit and "--version" not in explicit:
    sys.exit("REFUSED (Arch P1-K5): pass an explicit --out or --version (e.g. --version v1_3); legacy default dir is retired")
ver = a.version or "v1_3"
out = Path(a.out) if a.out else Path("output/strategy_optimizer/core_x2") / f"book_smoke_{ver}_{a.sleeve}_{a.aum // 10000}w"
out_abs = out if out.is_absolute() else ROOT / out
if out_abs.exists() and any(out_abs.iterdir()) and not a.overwrite:
    sys.exit(f"REFUSED: {out_abs} exists and is non-empty; pass --overwrite or choose another --out/--version")
wp = Path(a.weights); wp = wp if wp.is_absolute() else ROOT / wp
import pandas as pd
_w = pd.read_parquet(wp)
_dc = "session" if "session" in _w.columns else ("date" if "date" in _w.columns else None)
wmeta = {"path": str(a.weights), "sha256": hashlib.sha256(wp.read_bytes()).hexdigest(), "rows": int(len(_w)),
         "date_min": str(pd.to_datetime(_w[_dc]).min().date()) if _dc else None,
         "date_max": str(pd.to_datetime(_w[_dc]).max().date()) if _dc else None,
         "n_dates": int(_w[_dc].nunique()) if _dc else None}
del _w
out_abs.mkdir(parents=True, exist_ok=True)
(out_abs / "run_meta.json").write_text(json.dumps({"version": ver, "aum": a.aum, "sleeve": a.sleeve, "out": str(out),
    "started_et": datetime.datetime.now().isoformat(timespec="seconds"), "weights": wmeta, "status": "RUNNING", "runner_pin": PIN,
    "live": False, "promotion_approved": False}, indent=2))
run(["--windows", "X2", "--capitals", str(a.aum), "--arms", "BOOK,C0",
     "--sleeves", json.dumps({"core": 0, "stock": 1, "alpha_event": 0}),
     "--stock-path", a.weights, "--out", str(out), "--receipt", str(out / "BOOK_SMOKE_RECEIPT_ZH.md")])
src = out_abs / f"aum_{a.aum}" / "X2" / "BOOK" / "nav.csv"
shutil.copyfile(src, out_abs / "nav.csv")
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
(out_abs / "entry_meta.json").write_text(json.dumps({"weights": a.weights, "aum": a.aum, "sleeve": a.sleeve,
    "version": ver, "weights_sha256": wmeta["sha256"], "engine": "ExecConfig.strategy_v1", "window": "X2", "peak_rss_mb": rss, "live": False,
    "promotion_approved": False}, indent=2))
rm = json.loads((out_abs / "run_meta.json").read_text()); rm.update(status="DONE", peak_rss_mb=rss,
    finished_et=datetime.datetime.now().isoformat(timespec="seconds"))
(out_abs / "run_meta.json").write_text(json.dumps(rm, indent=2))
print(f"nav -> {out_abs/'nav.csv'} peak_rss_mb={rss:.0f}")
