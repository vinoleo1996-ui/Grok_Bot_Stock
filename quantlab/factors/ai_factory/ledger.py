"""Search ledger (plan E2): every GP/LGBM/NN trial increments N.

Path: output/ai_factor/ledger.jsonl
Fields: attempt_id, N, seed, universe, cost, window, engine, expr_hash, fitness, notes
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_LEDGER = Path(__file__).resolve().parents[3] / "output" / "ai_factor" / "ledger.jsonl"
PROMOTION_APPROVED = False


def _next_n(path: Path) -> int:
    if not path.exists():
        return 1
    n = 0
    with path.open() as f:
        for line in f:
            if line.strip():
                n += 1
    return n + 1


def expr_hash(expr_str: str) -> str:
    return hashlib.sha256(expr_str.encode()).hexdigest()[:16]


def append_attempt(
    *,
    engine: str,
    seed: int,
    universe: str,
    cost: float,
    window: str,
    expr_str: str,
    fitness: float | None,
    notes: str = "",
    path: Path | None = None,
) -> dict[str, Any]:
    path = path or DEFAULT_LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    n = _next_n(path)
    row = {
        "attempt_id": f"{engine}-{n:05d}",
        "N": n,
        "seed": seed,
        "universe": universe,
        "cost": cost,
        "window": window,
        "engine": engine,
        "expr_hash": expr_hash(expr_str),
        "expr_str": expr_str[:500],
        "fitness": fitness,
        "notes": notes,
        "promotion_approved": False,
    }
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_attempts(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or DEFAULT_LEDGER
    if not path.exists():
        return []
    out = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
