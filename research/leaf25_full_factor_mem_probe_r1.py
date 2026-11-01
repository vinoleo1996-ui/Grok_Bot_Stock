#!/usr/bin/env python3
"""Leaf25 full-factor mem_probe r1 — single-chunk HI_LIQ peak-path skeleton.

Arch NEED_MEM_PROBE (ARCH_LEAF25_MEM_CHUNK_REVIEW sha f389c394…):
  implement probe + minimal chunk_plan; static only this turn; DO NOT apply for X2 .ok.

HARD RULES (this file):
  - Default is --dry-run. Real PIT/parquet path requires explicit --allow-real-data.
  - THIS TASK / default invocation MUST NOT read financial or market big tables.
  - Formal peak-path run is ONLY after Arch signs an independent probe .ok and Main
    schedules the short window. Comment below marks the gate.
  - RSS self-check: exit non-zero if observed peak >= 0.85*C4 (1131520 kB) OR >= hard.
  - C4/stop/hard defaults: 1331200 / 1484800 / 1536000 kB. Ban raise RSS cap.
  - Sampler / intermediate sample dirs: /tmp/quantlab_* only.
  - Ban reuse of step_m1 .ok 1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0.

Peak path structure (dry simulates; real gated):
  read PIT → cross-section alpha → write part parquet → del+gc
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import resource
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Optional import of sibling chunk_plan (same research/)
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    import leaf25_full_factor_chunk_plan_r1 as chunk_plan_mod
except ImportError:  # pragma: no cover - allow --help without sibling
    chunk_plan_mod = None  # type: ignore

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[1]

C4_KB = 1331200
STOP_KB = 1484800
HARD_KB = 1536000
SPLIT_THRESH_KB = int(0.85 * C4_KB)  # 1131520
BANNED_OK_SHA = "1c32ab1e5ffb9eb3ddf466f15b0cd778a1579eaca678f2f5fbe1dd1ae00e66f0"

# ---------------------------------------------------------------------------
# FORMAL PEAK PATH GATE (do not remove):
#   Production / calibrated mem_probe that reads real PIT + HI_LIQ cross-section
#   MUST be launched only after:
#     (1) Arch signs an independent probe .ok (NOT X2, NOT step_m1 1c32ab1e…),
#     (2) Main schedules the short probe window,
#     (3) CLI passes --allow-real-data AND --arch-ok-path pointing at that .ok.
#   Until then: --dry-run only (default). live=false. promotion_approved=false.
# ---------------------------------------------------------------------------


def stage(name: str) -> None:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"STAGE {name} ru_maxrss={rss}", file=sys.stderr, flush=True)


def vmhwm_kb() -> int | None:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def peak_kb() -> int:
    """Linux getrusage.ru_maxrss is kB; take max with VmHWM if present."""
    ru = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    hw = vmhwm_kb()
    return max(ru, hw) if hw is not None else ru


def check_rss(label: str, c4_kb: int, hard_kb: int, split_kb: int) -> int:
    pk = peak_kb()
    print(f"RSS_CHECK {label} peak_kb={pk} split={split_kb} c4={c4_kb} hard={hard_kb}", flush=True)
    if pk >= hard_kb:
        print(f"STOP: RSS hard breached peak_kb={pk} >= hard={hard_kb}", file=sys.stderr)
        raise SystemExit(95)
    if pk >= split_kb:
        print(
            f"STOP: RSS >= 0.85*C4 peak_kb={pk} >= split={split_kb}; "
            f"split further — ban raise cap",
            file=sys.stderr,
        )
        raise SystemExit(94)
    return pk


def assert_tmp_quantlab(path: Path, what: str) -> None:
    resolved = path.resolve()
    s = str(resolved)
    if not (s.startswith("/tmp/quantlab_") or s.startswith("/tmp/quantlab/")):
        # allow /tmp/quantlab_xxx or nested under a quantlab_* dir
        ok = False
        parts = resolved.parts
        if len(parts) >= 3 and parts[1] == "tmp":
            # /tmp/<name>/...
            name = parts[2]
            if name.startswith("quantlab"):
                ok = True
        if not ok:
            raise SystemExit(
                f"STOP: {what} must be under /tmp/quantlab_* got={resolved}"
            )


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pick_chunk(plan: dict, chunk_id: int | None) -> dict:
    chunks = plan["chunks"]
    if not chunks:
        raise SystemExit("STOP: empty chunk plan")
    if chunk_id is None:
        return chunks[0]
    for c in chunks:
        if c["chunk_id"] == chunk_id:
            return c
    raise SystemExit(f"STOP: chunk_id={chunk_id} not in plan")


def dry_peak_path(chunk: dict, out_part: Path, universe: str) -> dict:
    """Simulate read PIT → CS alpha → write part → gc without touching big tables."""
    stage("dry_begin")
    # Tiny synthetic cross-section (NOT real data)
    n_names = 32
    rows = [
        {
            "trade_date": chunk["start"].replace("-", ""),
            "ts_code": f"{i:06d}.SZ",
            "universe": universe,
            "alpha": float(i % 7) * 0.01,
            "chunk_id": chunk["chunk_id"],
        }
        for i in range(n_names)
    ]
    stage("dry_cs_alpha")
    out_part.parent.mkdir(parents=True, exist_ok=True)
    # Write a tiny JSON "part" (avoid pyarrow dependency on dry path for parquet)
    part_meta = {
        "format": "dry_json_part",
        "not_real_data": True,
        "n_names": n_names,
        "chunk": chunk,
        "rows_sample": rows[:3],
    }
    tmp = out_part.with_suffix(out_part.suffix + ".tmp")
    tmp.write_text(json.dumps(part_meta, indent=2) + "\n", encoding="utf-8")
    tmp.replace(out_part)
    del rows
    gc.collect()
    stage("dry_after_gc")
    return {
        "path": "dry",
        "n_names": n_names,
        "n_days": chunk.get("n_rebaldays") or chunk.get("n_open_days") or 1,
        "densify": False,
        "part_path": str(out_part),
    }


def real_peak_path_gated(*_a, **_k) -> dict:
    """Real PIT→α→part path.

    Intentionally not implemented for unattended runs. When Arch probe .ok lands,
    fill this with column-projected PIT reads + HI_LIQ CS + float32 part parquet.
    Until then calling this is a hard error even with --allow-real-data, so that
    this package cannot silently densify a full window.
    """
    raise SystemExit(
        "STOP: real peak path not enabled in mem_probe_r1 skeleton; "
        "await Arch probe .ok + implementation fill-in (ban densify)"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Leaf25 full-factor mem_probe r1")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="Default: synthetic peak-path structure only (no big tables)")
    ap.add_argument("--allow-real-data", action="store_true", default=False,
                    help="Required to attempt real PIT path (still gated / unimplemented)")
    ap.add_argument("--no-dry-run", action="store_true",
                    help="Disable dry-run (still needs --allow-real-data)")
    ap.add_argument("--universe", default="HI_LIQ", choices=("HI_LIQ", "FULLA"))
    ap.add_argument("--start", default="2024-06-03")
    ap.add_argument("--end", default="2026-10-09")
    ap.add_argument("--mode", choices=("rebal_days", "month"), default="month",
                    help="Default month ≈ 1 natural month (Arch probe suggestion)")
    ap.add_argument("--max-rebaldays", type=int, default=20)
    ap.add_argument("--chunk-id", type=int, default=None, help="Which chunk to probe (default first)")
    ap.add_argument("--chunk-plan-json", type=Path, default=None,
                    help="Existing plan JSON; else build via chunk_plan module")
    ap.add_argument("--synthetic-calendar", action="store_true",
                    help="Pass through to chunk_plan (no calendar parquet)")
    ap.add_argument("--out", type=Path, required=True, help="Probe out dir (meta + part)")
    ap.add_argument("--sample-dir", type=Path, default=None,
                    help="Optional RSS sample dir; must be /tmp/quantlab_*")
    ap.add_argument("--c4-kb", type=int, default=C4_KB)
    ap.add_argument("--stop-kb", type=int, default=STOP_KB)
    ap.add_argument("--hard-kb", type=int, default=HARD_KB)
    ap.add_argument("--arch-ok-path", type=Path, default=None,
                    help="Path to Arch probe .ok (required with --allow-real-data)")
    args = ap.parse_args(argv)

    # Default ALWAYS dry unless explicit --allow-real-data (formal path gated).
    if args.allow_real_data:
        dry = False
    elif args.no_dry_run:
        print("STOP: --no-dry-run requires --allow-real-data", file=sys.stderr)
        return 2
    else:
        dry = True

    if args.c4_kb != C4_KB or args.stop_kb != STOP_KB or args.hard_kb != HARD_KB:
        # Allow override only downward; ban raise
        if args.c4_kb > C4_KB or args.stop_kb > STOP_KB or args.hard_kb > HARD_KB:
            print("STOP: ban raise RSS cap above 1331200/1484800/1536000", file=sys.stderr)
            return 2

    split_kb = int(0.85 * args.c4_kb)

    if args.sample_dir is not None:
        assert_tmp_quantlab(args.sample_dir, "sample-dir")
        args.sample_dir.mkdir(parents=True, exist_ok=True)

    if not dry:
        if args.arch_ok_path is None or not args.arch_ok_path.is_file():
            print("STOP: --allow-real-data requires existing --arch-ok-path", file=sys.stderr)
            return 2
        ok_sha = sha256_file(args.arch_ok_path)
        if ok_sha == BANNED_OK_SHA:
            print(f"STOP: ban reuse step_m1 .ok {BANNED_OK_SHA}", file=sys.stderr)
            return 2

    stage("start")
    check_rss("start", args.c4_kb, args.hard_kb, split_kb)

    # Chunk plan
    if args.chunk_plan_json is not None:
        plan = json.loads(args.chunk_plan_json.read_text(encoding="utf-8"))
    else:
        if chunk_plan_mod is None:
            print("STOP: chunk_plan module missing", file=sys.stderr)
            return 2
        plan = chunk_plan_mod.build_plan(
            start=args.start,
            end=args.end,
            mode=args.mode,
            max_rebaldays=args.max_rebaldays,
            cal_path=None,
            synthetic=args.synthetic_calendar or dry,  # dry defaults synthetic cal
            pin_sha=not (args.synthetic_calendar or dry),
        )

    chunk = pick_chunk(plan, args.chunk_id)
    if args.universe == "FULLA" and dry:
        print("NOTE: dry-run FULLA allowed for structure; probe priority remains HI_LIQ", flush=True)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    part_path = out / f"alpha_parts/{args.universe}/part_{chunk['start'].replace('-', '')}_{chunk['end'].replace('-', '')}.json"

    if dry:
        path_meta = dry_peak_path(chunk, part_path, args.universe)
    else:
        path_meta = real_peak_path_gated(chunk, part_path, args.universe)

    pk = check_rss("after_chunk", args.c4_kb, args.hard_kb, split_kb)

    meta = {
        "schema": "leaf25_full_factor_mem_probe_r1",
        "live": False,
        "promotion_approved": False,
        "dry_run": dry,
        "allow_real_data": bool(args.allow_real_data),
        "universe": args.universe,
        "chunk": chunk,
        "n_chunks_in_plan": plan.get("n_chunks"),
        "path": path_meta,
        "rss": {
            "peak_kb": pk,
            "c4_kb": args.c4_kb,
            "stop_kb": args.stop_kb,
            "hard_kb": args.hard_kb,
            "split_threshold_kb": split_kb,
            "vmhwm_kb": vmhwm_kb(),
            "ru_maxrss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        },
        "sampler_policy": "/tmp/quantlab_* only",
        "sample_dir": str(args.sample_dir) if args.sample_dir else None,
        "banned_ok_sha": BANNED_OK_SHA,
        "created_et": datetime.now(ET).strftime("%Y-%m-%dT%H:%M:%S%z"),
        "notes": [
            "NEED_MEM_PROBE skeleton; formal real-data peak path awaits probe .ok",
            "Ban raise RSS; if peak>=0.85*C4 exit 94 and split further",
            "Do not apply for X2 .ok from this package alone",
        ],
    }
    meta_path = out / "run_meta.json"
    tmp = meta_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(meta_path)

    # Optional: persist plan alongside
    plan_path = out / "chunk_plan_used.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"OK mem_probe dry={dry} universe={args.universe} chunk_id={chunk['chunk_id']} "
        f"peak_kb={pk} meta={meta_path}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
