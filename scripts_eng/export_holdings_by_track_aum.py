#!/usr/bin/env python3
"""Dashboard-only derived holdings (read-only on paper files; live=false).

Reads <paper_daily>/bridge_X2H/{track}_aum_{aum}/aum_{aum}/X2H/BOOK/actual_weights.parquet — the per-AUM book whose
nav.csv equals the paper NAV ({track}_{aum}_X2H_nav.csv; checked) — and writes
<paper_daily>/bridge_X2H/holdings_by_track_aum.parquet: track, aum, session, instrument, weight, shares, source_path
for the latest session. capacity_adv: the hold-extend weights file is a target schedule (X2_frozen +
extended_weights_gated segments, no AUM); the per-AUM BOOK actual weights are what the paper NAV booked.
shares: not stored by the bridge book (no positions/prices in outputs) -> null.
Cash share = 1 - sum(weight) is reported, not written as a row.

  python3 scripts_eng/export_holdings_by_track_aum.py [--paper-daily output/loop/paper_daily_YYYYMMDD]
"""
import argparse, glob, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--paper-daily", default=None)
ap.add_argument("--tracks", default="capacity_adv,b4,s6")
ap.add_argument("--aums", default="600000,1000000")
a = ap.parse_args()
pd_dir = Path(a.paper_daily) if a.paper_daily else Path(sorted(glob.glob(str(ROOT / "output/loop/paper_daily_2*")))[-1])
pd_dir = pd_dir if pd_dir.is_absolute() else ROOT / pd_dir
B = pd_dir / "bridge_X2H"
rows, bad = [], 0
for t in a.tracks.split(","):
    for aum in map(int, a.aums.split(",")):
        book = B / f"{t}_aum_{aum}" / f"aum_{aum}" / "X2H" / "BOOK"
        src = book / "actual_weights.parquet"
        if not src.exists():
            print(f"MISSING {src}"); bad += 1; continue
        aw = pd.read_parquet(src, columns=["session", "instrument_id", "weight"])
        s = aw.session.max(); last = aw[(aw.session == s) & (aw.weight.abs() > 1e-9)]
        pn = B / f"{t}_{aum}_X2H_nav.csv"
        chk = "n/a"
        if pn.exists():
            p = pd.read_csv(pn).iloc[-1]; b = pd.read_csv(book / "nav.csv").iloc[-1]
            chk = "OK" if str(p.iloc[0])[:10] == str(b.iloc[0])[:10] and abs(float(p.nav) - float(b.nav)) < 0.01 else "MISMATCH"
            bad += chk != "OK"
        for _, r in last.iterrows():
            rows.append(dict(track=t, aum=aum, session=pd.Timestamp(s).date().isoformat(), instrument=r.instrument_id,
                             weight=float(r.weight), shares=None, source_path=str(src.relative_to(ROOT))))
        print(f"{t} {aum} session={pd.Timestamp(s).date()} names={len(last)} sum_w={last.weight.sum():.4f} "
              f"cash={1-last.weight.sum():.4f} nav_vs_paper={chk}")
df = pd.DataFrame(rows, columns=["track", "aum", "session", "instrument", "weight", "shares", "source_path"])
df["shares"] = df["shares"].astype("float64")
out = B / "holdings_by_track_aum.parquet"
df.to_parquet(out, index=False)
print(f"-> {out} rows={len(df)}")
sys.exit(1 if bad else 0)
