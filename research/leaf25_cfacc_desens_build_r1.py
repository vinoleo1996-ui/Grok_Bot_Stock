#!/usr/bin/env python3
"""Leaf25 CFACC desens build r1 — STUB only (NotImplemented).

NEED_MEM_PROBE package optional minimum. Does NOT implement full-leaf build.
Do not pretend complete. live=false. Ban densify / ban raise RSS.
Await mem_probe calibration + Arch X2 .ok before any real build run.
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Leaf25 CFACC desens build r1 STUB")
    ap.add_argument("--window", choices=("x2", "sealed"), default="x2")
    ap.add_argument("--x2-end", default="20261009")
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk-plan-json", default=None)
    args = ap.parse_args(argv)
    print(
        "STOP: leaf25_cfacc_desens_build_r1 is a stub (NotImplemented); "
        f"window={args.window} x2_end={args.x2_end} out={args.out}",
        file=sys.stderr,
    )
    raise NotImplementedError(
        "full-leaf CFACC/desens build not implemented; complete mem_probe first"
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except NotImplementedError as e:
        print(f"NotImplementedError: {e}", file=sys.stderr)
        raise SystemExit(3)
