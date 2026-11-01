#!/usr/bin/env python3
"""Leaf25 full-factor chunk_plan r1 — rebalance-day / month chunk boundaries → JSON.

NEED_MEM_PROBE impl package (Arch f389c394… NEED_MEM_PROBE). live=false.
Generates chunk boundary JSON from the SSE trade calendar (small table only).
Does NOT read financials / prices / returns panels. No densify path.

Default granularity: ~20 rebalance days OR ~1 calendar month of open sessions
(whichever bound the CLI selects; default mode=rebal_days with max_rebaldays=20).

Usage (examples):
  PYTHONDONTWRITEBYTECODE=1 python research/leaf25_full_factor_chunk_plan_r1.py \\
    --start 2024-06-03 --end 2026-10-09 --out /tmp/quantlab_leaf25_chunks.json
  # month mode:
  ... --mode month --out /tmp/quantlab_leaf25_chunks.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CAL_REL = "data/v2/calendar/trade_cal_sse_pit.parquet"
CAL_SHA_PIN = "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"
ET = ZoneInfo("America/New_York")

# Defaults aligned with leaf25 X2 window / MEM P0
DEFAULT_START = "2024-06-03"
DEFAULT_END = "2026-10-09"
DEFAULT_MAX_REBALDAYS = 20


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_open_sessions(cal_path: Path, start: str, end: str, pin_sha: bool) -> list[pd.Timestamp]:
    if pin_sha:
        actual = sha256_file(cal_path)
        if actual != CAL_SHA_PIN:
            raise SystemExit(
                f"STOP: calendar sha mismatch actual={actual} pinned={CAL_SHA_PIN}"
            )
    tab = pq.read_table(cal_path, columns=["cal_date", "is_open"]).to_pandas()
    tab["d"] = pd.to_datetime(tab["cal_date"].astype(str).str.replace("-", "").str[:8], format="%Y%m%d")
    opens = tab.loc[tab["is_open"].astype(int) == 1, "d"].sort_values()
    lo = pd.Timestamp(start)
    hi = pd.Timestamp(end)
    sess = [pd.Timestamp(x) for x in opens[(opens >= lo) & (opens <= hi)]]
    if not sess:
        raise SystemExit(f"STOP: no open sessions in [{start}, {end}]")
    return sess


def synthetic_sessions(start: str, end: str) -> list[pd.Timestamp]:
    """Weekday-only synthetic calendar (no parquet). For dry / offline unit paths only."""
    days = pd.bdate_range(start=start, end=end, freq="C")
    if len(days) == 0:
        raise SystemExit(f"STOP: synthetic empty range [{start}, {end}]")
    return [pd.Timestamp(x) for x in days]


def month_end_rebals(sess: list[pd.Timestamp]) -> list[pd.Timestamp]:
    """Month-end rebalance = last open session in each calendar month; keep window ends."""
    if not sess:
        return []
    by_ym: dict[tuple[int, int], pd.Timestamp] = {}
    for d in sess:
        by_ym[(d.year, d.month)] = d  # last write wins → month end open
    me = sorted(by_ym.values())
    out = sorted(set([sess[0]] + me + [sess[-1]]))
    return out


def chunk_by_rebal(rebals: list[pd.Timestamp], max_n: int) -> list[dict]:
    chunks = []
    i = 0
    cid = 0
    while i < len(rebals):
        j = min(i + max_n, len(rebals))
        part = rebals[i:j]
        chunks.append(
            {
                "chunk_id": cid,
                "mode": "rebal_days",
                "n_rebaldays": len(part),
                "start": part[0].strftime("%Y-%m-%d"),
                "end": part[-1].strftime("%Y-%m-%d"),
                "rebal_dates": [d.strftime("%Y-%m-%d") for d in part],
            }
        )
        cid += 1
        i = j
    return chunks


def chunk_by_month(sess: list[pd.Timestamp]) -> list[dict]:
    """One chunk per calendar month of open sessions (≈1 natural month)."""
    groups: dict[tuple[int, int], list[pd.Timestamp]] = {}
    for d in sess:
        groups.setdefault((d.year, d.month), []).append(d)
    chunks = []
    for cid, key in enumerate(sorted(groups)):
        part = groups[key]
        chunks.append(
            {
                "chunk_id": cid,
                "mode": "month",
                "year_month": f"{key[0]:04d}-{key[1]:02d}",
                "n_open_days": len(part),
                "start": part[0].strftime("%Y-%m-%d"),
                "end": part[-1].strftime("%Y-%m-%d"),
                "open_dates_head_tail": [
                    part[0].strftime("%Y-%m-%d"),
                    part[-1].strftime("%Y-%m-%d"),
                ],
            }
        )
    return chunks


def build_plan(
    start: str,
    end: str,
    mode: str,
    max_rebaldays: int,
    cal_path: Path | None,
    synthetic: bool,
    pin_sha: bool,
) -> dict:
    if synthetic:
        sess = synthetic_sessions(start, end)
        cal_meta = {"source": "synthetic_bdate", "sha256": None}
    else:
        path = cal_path or (ROOT / CAL_REL)
        sess = load_open_sessions(path, start, end, pin_sha=pin_sha)
        cal_meta = {
            "source": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            "sha256": sha256_file(path),
            "sha_pin": CAL_SHA_PIN,
            "pin_checked": pin_sha,
        }
    rebals = month_end_rebals(sess)
    if mode == "rebal_days":
        chunks = chunk_by_rebal(rebals, max_rebaldays)
    elif mode == "month":
        chunks = chunk_by_month(sess)
    else:
        raise SystemExit(f"STOP: unknown mode={mode}")
    now = datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z")
    return {
        "schema": "leaf25_full_factor_chunk_plan_r1",
        "live": False,
        "promotion_approved": False,
        "created_et": now,
        "window": {"start": start, "end": end},
        "mode": mode,
        "max_rebaldays": max_rebaldays if mode == "rebal_days" else None,
        "calendar": cal_meta,
        "n_open_sessions": len(sess),
        "n_rebaldays": len(rebals),
        "n_chunks": len(chunks),
        "chunks": chunks,
        "notes": [
            "P0 MEM granularity example: ~20 rebal days or ~1 natural month",
            "No financials/prices read; calendar-only (or synthetic)",
            "Ban whole-window densify; each chunk is an independent peak budget unit",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Leaf25 full-factor chunk plan r1")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--mode", choices=("rebal_days", "month"), default="rebal_days")
    ap.add_argument("--max-rebaldays", type=int, default=DEFAULT_MAX_REBALDAYS)
    ap.add_argument("--calendar", type=Path, default=None, help="Override calendar parquet path")
    ap.add_argument("--synthetic", action="store_true", help="No parquet; weekday synthetic calendar")
    ap.add_argument("--no-pin-sha", action="store_true", help="Skip calendar sha pin check")
    ap.add_argument("--out", type=Path, required=True, help="Write chunk plan JSON here")
    args = ap.parse_args(argv)

    if args.max_rebaldays < 1:
        print("STOP: --max-rebaldays must be >= 1", file=sys.stderr)
        return 2

    plan = build_plan(
        start=args.start,
        end=args.end,
        mode=args.mode,
        max_rebaldays=args.max_rebaldays,
        cal_path=args.calendar,
        synthetic=args.synthetic,
        pin_sha=not args.no_pin_sha,
    )
    out = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    text = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out)
    print(
        f"OK wrote {out} n_chunks={plan['n_chunks']} mode={plan['mode']} "
        f"n_open={plan['n_open_sessions']} n_rebal={plan['n_rebaldays']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
