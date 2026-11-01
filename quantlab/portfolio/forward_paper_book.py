"""Forward paper-trading job for the multi-sleeve book (Strategy, 2026-10-11). NO real orders.
Research only, promotion_approved=false.

Per as-of session (latest data by default): rebuild every sleeve's signal from the LOCKED start, combine into the book
target, run Eng's engine (next-open fills, futures leg, corporate actions) from the locked start to the as-of date, and
write one ledger record for that date: active sleeve signals, combined target, whether the as-of close is a signal day
(orders fill at the NEXT session's open), simulated fills executed at this session's open, post-close actual weights,
NAV and costs. Idempotent per date: ledger/<date>.json is (re)written; if the content changes for a date already
written (data revision) the old hash is logged to revisions.jsonl. The book has no state other than the locked config,
so re-running any date reproduces it from data.

Seal: the first run writes LOCK.json (config + sha256 of the code files + start date). Every later run recomputes
them and refuses (exit 2) on any mismatch. Change = new forward ledger directory, never an edit.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from quantlab.portfolio import v2_multisleeve_book as B  # noqa: E402

CODE_FILES = ["quantlab/portfolio/forward_paper_book.py", "quantlab/portfolio/v2_multisleeve_book.py",
              "quantlab/platform/execution.py", "quantlab/platform/futures.py"]
# FUT-RP (L3/L6) deliberately NOT wired here — Leo/New Bot 2026-10-11: high-leverage FUT-RP on hold for
# forward paper. Do not add fut_rp / fut_rp_L3 sleeves or MarginConfig borrowing until Leo re-approves.
# DISABLED stub (do not enable):
#   sleeves_fut_rp_L3 = {"fut_rp_L3": 1.0}  # handoff: output/v3/handoff_strategy/fut_rp_L3/ — NOT wired
DEFAULT_CFG = dict(start="2026-11-02", sleeves={"marp": 0.40, "cb": 0.30, "xd": 0.30, "alpha_event": 0.0},
                   cash_target=0.02, collateral_frac=1.0, target_vol=None, leverage=1.0, max_gross=1.5,
                   initial_cash=5e6, e2_pool="sh.510300,sh.510500,sz.159915", alpha_event_path=None, static_ic=0.75)


def _sha_file(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def _cfg_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def lock_or_verify(out: Path, cfg: dict) -> dict:
    cur = dict(config=cfg, config_hash=_cfg_hash(cfg), code_hashes={f: _sha_file(f) for f in CODE_FILES},
               promotion_approved=False, research_only=True)
    lf = out / "LOCK.json"
    if not lf.exists():
        out.mkdir(parents=True, exist_ok=True)
        cur["locked_at"] = pd.Timestamp.now(tz="America/New_York").isoformat()
        json.dump(cur, open(lf, "w"), indent=1)
        return dict(cur, lock_status="created")
    old = json.load(open(lf))
    bad = []
    if old["config_hash"] != cur["config_hash"]: bad.append("config")
    for f, h in cur["code_hashes"].items():
        if old["code_hashes"].get(f) != h: bad.append(f)
    if bad:
        print(f"SEAL BROKEN: {bad} differ from {lf}; refusing. Start a new ledger dir instead.", file=sys.stderr)
        sys.exit(2)
    return dict(old, lock_status="verified")


def run_asof(D, cfg, asof, out: Path, lock: dict):
    a = cfg["start"]; idx = D.HFQ.loc[a:asof].index
    if len(idx) == 0 or idx[-1] != pd.Timestamp(asof):
        raise SystemExit(f"{asof}: not a session with ETF data (last available {D.HFQ.index[-1].date()})")
    ns = argparse.Namespace(**{k: v for k, v in cfg.items() if k != "start"})
    ns.sleeves = cfg["sleeves"]
    ss, sw, notes = B.build_sleeves(D, idx, a, asof, ns)
    final, sf, _ = B.combine(ss, sw, idx, collateral_frac=cfg["collateral_frac"], cash_target=cfg["cash_target"],
                             leverage=cfg.get("leverage", 1.0), max_gross=cfg.get("max_gross", B.MAX_GROSS), D=D)
    t = idx[-1]
    m = B.run_book(D, final, a, asof, None, initial_cash=cfg["initial_cash"], write=False, record_fills=True)
    r = m.pop("_raw")
    last_sig = max(d for d in final if d <= t)
    sleeve_sig = {k: {str(max(d for d in s if d <= t).date()) if s and any(d <= t for d in s) else None:
                      (s[max(d for d in s if d <= t)] if s and any(d <= t for d in s) else {})} for k, s in ss.items()}
    aw = r["actual_weights"].loc[t]; aw = {c: float(v) for c, v in aw.items() if abs(v) > 1e-7}
    day = str(t.date())
    rec = dict(date=day, promotion_approved=False, research_only=True, real_orders=False,
               lock_config_hash=lock["config_hash"], forward_start=a,
               is_signal_day=bool(last_sig == t),
               signal_note="targets locked at this close; simulated fills at next session open (engine next_open)",
               sleeve_signals=sleeve_sig, sleeve_weights=sw,
               combined_target={k: float(v) for k, v in final[last_sig].items()}, combined_target_date=str(last_sig.date()),
               xd_discount_signal=(notes.get("xd", {}).get("signals") or [None])[-1],
               fills_at_open=[f for f in (r.get("fills") or []) if f["date"] == day],
               futures_fills_at_open=[f for f in (r.get("fut_fills") or []) if f["date"] == day],
               actual_weights_close=aw, nav=float(r["nav"].loc[t]), nav_return_day=float(r["nav"].pct_change().loc[t]) if len(idx) > 1 else 0.0,
               cum_costs={k: float(v) for k, v in r["costs"].items()}, fut_total_fees=float(r.get("fut_total_fees") or 0),
               gross_exposure_close=float(sum(abs(v) for v in aw.values()) + abs(float(np.nansum(np.abs(np.asarray(r["fut_exposure"])[-1]))) if r.get("fut_exposure") is not None else 0.0)),
               data_last={"etf": str(D.HFQ.index[-1].date()), "cb": str(D.CB.date.max().date()),
                          "ic": str(D.fut(a, asof).settle.index.max().date())},
               data_hashes={f: B.sha(f) for f in B.HASH_FILES})
    body = json.dumps(rec, indent=1, sort_keys=True, default=str)
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    led = out / "ledger"; led.mkdir(parents=True, exist_ok=True); f = led / f"{day}.json"
    status = "new"
    if f.exists():
        oldh = hashlib.sha256(f.read_text().encode()).hexdigest()[:16]
        if oldh == h: status = "unchanged"
        else:
            status = "revised"
            with open(out / "revisions.jsonl", "a") as fh:
                fh.write(json.dumps(dict(date=day, old_hash=oldh, new_hash=h, at=pd.Timestamp.now(tz="America/New_York").isoformat())) + "\n")
    if status != "unchanged": f.write_text(body)
    # compact index (rebuilt from per-date records -> idempotent)
    rows = [json.loads(x.read_text()) for x in sorted(led.glob("*.json"))]
    pd.DataFrame([dict(date=x["date"], nav=x["nav"], ret=x["nav_return_day"], is_signal_day=x["is_signal_day"],
                       n_fills=len(x["fills_at_open"]) + len(x["futures_fills_at_open"]),
                       gross=x["gross_exposure_close"], promotion_approved=False) for x in rows]).to_csv(out / "ledger_index.csv", index=False)
    return status, h, rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="forward paper book (no real orders)")
    ap.add_argument("--out", default="output/forward_paper/book_v1")
    ap.add_argument("--asof", default=None, help="session date; default = latest ETF session on the box")
    ap.add_argument("--start", default=DEFAULT_CFG["start"], help="forward start (locked on first run)")
    ap.add_argument("--dry-run-last", type=int, default=0,
                    help="DRY RUN: run the last N available sessions into <out>_dryrun with start = session before them")
    a = ap.parse_args(argv)
    D = B.Data(with_cb=True)
    cfg = dict(DEFAULT_CFG, start=a.start)
    out = ROOT / a.out
    if a.dry_run_last:
        sess = list(D.HFQ.index[-(a.dry_run_last + 1):])
        cfg["start"] = str(sess[0].date()); out = ROOT / (a.out + "_dryrun"); dates = [str(x.date()) for x in sess[1:]]
        cfg["dry_run"] = True
    else:
        dates = [a.asof or str(D.HFQ.index[-1].date())]
        if pd.Timestamp(dates[0]) < pd.Timestamp(cfg["start"]):
            raise SystemExit(f"as-of {dates[0]} is before the forward start {cfg['start']}; nothing to do (no backfill into the seal)")
    lock = lock_or_verify(out, cfg)
    print(f"lock {lock['lock_status']} config_hash={lock['config_hash'][:12]} start={cfg['start']} out={out}")
    for d in dates:
        t0 = time.time(); st, h, rec = run_asof(D, cfg, d, out, lock)
        print(f"{d} {st} hash={h} signal_day={rec['is_signal_day']} nav={rec['nav']:,.0f} fills={len(rec['fills_at_open'])}+fut{len(rec['futures_fills_at_open'])} "
              f"gross={rec['gross_exposure_close']:.2f} target={ {k: round(v, 4) for k, v in rec['combined_target'].items() if len(k) < 4 or k.startswith('sh.5')} } ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
