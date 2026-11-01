#!/usr/bin/env python3
"""Static check: cmc_wrapper_v5 sampler default is /tmp-only (no disk run)."""
from __future__ import annotations
import re
import sys
from pathlib import Path

REQUIRED = [
    r"cmc_wrapper_v5",
    r"/tmp/quantlab_wrapper_sampler",
    r"--sampler-dir",
    r"--sampler-file",
    r"SAMPLER_PATH",
    r"sampler must be under /tmp",
    r"output\*/data\* forbidden",
]
FORBIDDEN = [
    r'S="\$L/\$\{TAG\}_sampler\.txt"',
]

def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else
                "/workspace/QuantLab/docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh")
    text = path.read_text(encoding="utf-8")
    miss = [p for p in REQUIRED if not re.search(p, text)]
    bad = [p for p in FORBIDDEN if re.search(p, text)]
    if miss or bad:
        print("FAIL miss=", miss, "bad=", bad)
        return 1
    print("PASS sampler_tmp_only static", path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
