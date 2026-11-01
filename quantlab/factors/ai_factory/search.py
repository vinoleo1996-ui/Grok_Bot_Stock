"""B1 genetic programming / symbolic regression (plan §2.3 B1).

Fitness on allowed train/explore labels only — never sealed holdout.
Cost/turnover/complexity penalties enter the fitness.
Emits Top-K expressions and increments ``output/ai_factor/ledger.jsonl``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.ai_factory.fitness import fitness_score, fitness_score_l1b
from quantlab.factors.ai_factory.novelty import is_structural_expr, is_textbook_expr
from quantlab.factors.ai_factory.ledger import append_attempt
from quantlab.factors.ops import (
    LEAF_FEATURES,
    MAX_DEPTH,
    MAX_NODES,
    OPS,
    Expr,
    apply_expr,
    leaf_names_present,
)

PROMOTION_APPROVED = False


@dataclass
class GPConfig:
    population: int = 40
    generations: int = 8
    max_evaluations: int = 280  # MUST be stated in run meta before search
    top_k: int = 20
    lambda_complexity: float = 0.015
    lambda_turnover: float = 1.0
    top_n: int = 50
    seed: int = 20261011
    universe: str = "midlarge_top1500"
    cost: float = 0.0025
    window: str = "explore_20240603_plus"
    ledger_path: Path | None = None
    structural_only: bool = False
    ban_textbook: bool = False
    use_l1b_fitness: bool = False
    public_panels: Mapping | None = None


@dataclass
class Candidate:
    expr: Expr
    train_icir: float
    fitness: float
    n_nodes: int
    metrics: dict = field(default_factory=dict)

    def as_row(self) -> dict:
        return {
            "expr": self.expr.to_str(),
            "tuple": self.expr.to_tuple(),
            "train_icir": self.train_icir,
            "fitness": self.fitness,
            "n_nodes": self.n_nodes,
            "metrics": self.metrics,
            "promotion_approved": False,
        }


@dataclass
class SearchResult:
    promotion_approved: bool = field(default=False, init=False)
    evaluations: int = 0
    max_evaluations: int = 0
    top_k: list[Candidate] = field(default_factory=list)
    ledger_tail_n: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)


def _rand_expr(rng: np.random.Generator, leaves: Sequence[str], depth: int = 1) -> Expr:
    if depth >= MAX_DEPTH or (depth > 1 and rng.random() < 0.45):
        return Expr("leaf", str(rng.choice(list(leaves))))
    names = [n for n in OPS if not n.endswith("_neutral")]
    name = str(rng.choice(names))
    op = OPS[name]
    kids = tuple(_rand_expr(rng, leaves, depth + 1) for _ in range(op.arity))
    return Expr("op", name, kids)


def _mutate(rng: np.random.Generator, expr: Expr, leaves: Sequence[str]) -> Expr:
    if rng.random() < 0.35 or expr.kind == "leaf":
        return _rand_expr(rng, leaves)
    if not expr.children:
        return _rand_expr(rng, leaves)
    kids = list(expr.children)
    i = int(rng.integers(0, len(kids)))
    kids[i] = _mutate(rng, kids[i], leaves)
    return Expr(expr.kind, expr.name, tuple(kids))


def gp_search(
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    config: GPConfig | None = None,
) -> SearchResult:
    cfg = config or GPConfig()
    leaves = leaf_names_present(panels, structural_only=cfg.structural_only)
    if not leaves:
        leaves = [n for n in LEAF_FEATURES if n in panels]
    if not leaves:
        raise ValueError("no leaf panels present")
    rng = np.random.default_rng(cfg.seed)
    out = SearchResult()
    out.max_evaluations = int(cfg.max_evaluations)
    pop = [_rand_expr(rng, leaves) for _ in range(cfg.population)]
    archive: list[Candidate] = []

    def eval_one(expr: Expr) -> Candidate | None:
        if out.evaluations >= cfg.max_evaluations:
            return None
        out.evaluations += 1
        if expr.depth() > MAX_DEPTH or expr.n_nodes() > MAX_NODES:
            append_attempt(
                engine="gp",
                seed=cfg.seed,
                universe=cfg.universe,
                cost=cfg.cost,
                window=cfg.window,
                expr_str=expr.to_str(),
                fitness=None,
                notes="rejected_complexity",
                path=cfg.ledger_path,
            )
            return None
        expr_s = expr.to_str()
        if cfg.ban_textbook and is_textbook_expr(expr_s):
            append_attempt(
                engine="gp",
                seed=cfg.seed,
                universe=cfg.universe,
                cost=cfg.cost,
                window=cfg.window,
                expr_str=expr_s,
                fitness=None,
                notes="rejected_textbook_ban",
                path=cfg.ledger_path,
            )
            return None
        if cfg.structural_only and not is_structural_expr(expr_s, leaves):
            append_attempt(
                engine="gp",
                seed=cfg.seed,
                universe=cfg.universe,
                cost=cfg.cost,
                window=cfg.window,
                expr_str=expr_s,
                fitness=None,
                notes="rejected_non_structural",
                path=cfg.ledger_path,
            )
            return None
        try:
            fac = apply_expr(expr, panels)
        except Exception as exc:  # noqa: BLE001
            append_attempt(
                engine="gp",
                seed=cfg.seed,
                universe=cfg.universe,
                cost=cfg.cost,
                window=cfg.window,
                expr_str=expr.to_str(),
                fitness=None,
                notes=f"eval_error:{type(exc).__name__}",
                path=cfg.ledger_path,
            )
            return None
        if cfg.use_l1b_fitness:
            met = fitness_score_l1b(
                fac,
                label,
                public_panels=cfg.public_panels,
                cost_one_way=cfg.cost,
                top_n=cfg.top_n,
                lambda_complexity=cfg.lambda_complexity,
                n_nodes=expr.n_nodes(),
                lambda_turnover=cfg.lambda_turnover,
            )
        else:
            met = fitness_score(
                fac,
                label,
                cost_one_way=cfg.cost,
                top_n=cfg.top_n,
                lambda_complexity=cfg.lambda_complexity,
                n_nodes=expr.n_nodes(),
                lambda_turnover=cfg.lambda_turnover,
            )
        fit = met["fitness"]
        row = append_attempt(
            engine="gp",
            seed=cfg.seed,
            universe=cfg.universe,
            cost=cfg.cost,
            window=cfg.window,
            expr_str=expr.to_str(),
            fitness=float(fit) if np.isfinite(fit) else None,
            notes=(
                f"icir={met.get('icir')};turn={met.get('turnover')};"
                f"ann_net={met.get('ann_net')};cost_in_fitness;"
                f"novelty_fail={met.get('novelty_fail')};"
                f"max_pub_corr={met.get('max_abs_public_corr')}"
            ),
            path=cfg.ledger_path,
        )
        out.ledger_tail_n = int(row["N"])
        icir = met.get("icir")
        if icir is None or not np.isfinite(icir) or fit <= -1e8:
            return None
        return Candidate(
            expr=expr,
            train_icir=float(icir),
            fitness=float(fit),
            n_nodes=expr.n_nodes(),
            metrics={k: met[k] for k in met if k != "fitness"},
        )

    for _gen in range(cfg.generations):
        scored: list[Candidate] = []
        for e in pop:
            if out.evaluations >= cfg.max_evaluations:
                break
            c = eval_one(e)
            if c is not None:
                scored.append(c)
                archive.append(c)
        if out.evaluations >= cfg.max_evaluations or not scored:
            break
        scored.sort(key=lambda c: c.fitness, reverse=True)
        elite_n = max(2, cfg.population // 4)
        elite = [c.expr for c in scored[:elite_n]]
        # mutate elites + fresh random
        while len(elite) < cfg.population:
            if scored and rng.random() < 0.6:
                parent = scored[int(rng.integers(0, min(len(scored), elite_n)))].expr
                elite.append(_mutate(rng, parent, leaves))
            else:
                elite.append(_rand_expr(rng, leaves))
        pop = elite

    archive.sort(key=lambda c: c.fitness, reverse=True)
    seen: set[str] = set()
    top: list[Candidate] = []
    for c in archive:
        s = c.expr.to_str()
        if s in seen:
            continue
        if cfg.ban_textbook and is_textbook_expr(s):
            continue
        if cfg.use_l1b_fitness and (c.metrics or {}).get("novelty_fail"):
            continue
        if cfg.use_l1b_fitness:
            ann = (c.metrics or {}).get("ann_net")
            if ann is None or not np.isfinite(ann) or ann <= 0:
                continue
        seen.add(s)
        top.append(c)
        if len(top) >= cfg.top_k:
            break
    out.top_k = top
    assert out.promotion_approved is False
    return out
