"""QuantMind-style five-stage factor loop (self-built minimal).

Stages: preflight → evolve → backtest → explain → export
Wires to existing GP / L1b structural leaves / novelty / ledger.
Never opens sealed windows. promotion_approved always False.

Capital framing: capital_cny ∈ {600_000, 1_000_000} (Leo 本金 60～100 万).
Textbook expressions banned from main Top-K (control arm only).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.factors.ai_factory.fitness import fitness_score_l1b
from quantlab.factors.ai_factory.ledger import append_attempt, read_attempts
from quantlab.factors.ai_factory.novelty import (
    STRUCTURAL_LEAVES,
    is_structural_expr,
    is_textbook_expr,
)
from quantlab.factors.ai_factory.rdagent_min_loop import Hypothesis, run_min_loop
from quantlab.factors.ai_factory.search import GPConfig, gp_search
from quantlab.factors.ai_factory.structural_leaves import who_pays_for_leaf
from quantlab.factors.ops import Expr, apply_expr, leaf_names_present, parse_expr

PROMOTION_APPROVED = False
CAPITAL_CNY_ALLOWED: frozenset[int] = frozenset({600_000, 1_000_000})
MECHANISM_TAGS: frozenset[str] = frozenset(
    {
        "limit_up",
        "consecutive_board",
        "theme",
        "t1",
        "etf_flow",
        "cb_event",
        "ann_embed",
        "sentiment",
        "lockup",
        "basis",
    }
)
TEXTBOOK_DIRECTION_RE = re.compile(
    r"(?<![非不])(反转|动量|低波|低波动|换手率|turnover|momentum|reversal|low[\s\-]?vol|价值因子|成长选股)|(?<![A-Za-z])(EP|BP)(?![A-Za-z])",
    re.I,
)


@dataclass
class Direction:
    """Mechanism hypothesis for evolve stage."""

    direction_id: str
    text_zh: str
    mechanism_tag: str
    who_pays_zh: str
    seed_exprs: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errs: list[str] = []
        if self.mechanism_tag not in MECHANISM_TAGS:
            errs.append(f"bad_mechanism_tag:{self.mechanism_tag}")
        if TEXTBOOK_DIRECTION_RE.search(self.text_zh):
            errs.append("textbook_direction_lexicon")
        if not self.who_pays_zh.strip():
            errs.append("missing_who_pays")
        return errs


@dataclass
class StageArtifact:
    stage: str
    ok: bool
    payload: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@dataclass
class LoopRunResult:
    promotion_approved: bool = field(default=False, init=False)
    direction: Direction | None = None
    capital_cny: int = 600_000
    stages: list[StageArtifact] = field(default_factory=list)
    top_k: list[dict[str, Any]] = field(default_factory=list)
    explain: list[dict[str, Any]] = field(default_factory=list)
    export_paths: dict[str, str] = field(default_factory=dict)
    ledger_N: int = 0
    evaluations: int = 0
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "promotion_approved", False)
        if self.capital_cny not in CAPITAL_CNY_ALLOWED:
            raise ValueError(
                f"capital_cny must be in {sorted(CAPITAL_CNY_ALLOWED)}, got {self.capital_cny}"
            )


def preflight(
    *,
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    direction: Direction,
    capital_cny: int,
    structural_only: bool = True,
) -> StageArtifact:
    errs: list[str] = []
    if capital_cny not in CAPITAL_CNY_ALLOWED:
        errs.append("capital_cny_not_in_{6e5,1e6}")
    errs.extend(direction.validate())
    leaves = leaf_names_present(panels, structural_only=structural_only)
    if structural_only and not leaves:
        errs.append("no_structural_leaves_in_panels")
    if label is None or label.shape[0] < 10:
        errs.append("label_too_short")
    # Reject textbook-only panel sets when structural_only
    if structural_only:
        for name in panels:
            if is_textbook_expr(name) and name not in STRUCTURAL_LEAVES:
                # presence of public panels OK for corr control; not an error
                pass
    return StageArtifact(
        stage="preflight",
        ok=len(errs) == 0,
        payload={
            "errors": errs,
            "n_leaves": len(leaves),
            "leaves": leaves[:40],
            "capital_cny": capital_cny,
            "mechanism_tag": direction.mechanism_tag,
            "promotion_approved": False,
        },
    )


def evolve_from_seeds_and_gp(
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    direction: Direction,
    *,
    cfg: GPConfig,
    public_panels: Mapping[str, pd.DataFrame] | None = None,
) -> StageArtifact:
    """Evolve: seed exprs from direction + optional tiny GP (structural_only)."""
    seeds = list(direction.seed_exprs)
    # Drop textbook seeds immediately
    seeds = [s for s in seeds if not is_textbook_expr(s)]
    gp_top: list[dict[str, Any]] = []
    evaluations = 0
    ledger_n = 0
    if cfg.max_evaluations > 0 and cfg.population > 0:
        local = GPConfig(
            population=cfg.population,
            generations=cfg.generations,
            max_evaluations=cfg.max_evaluations,
            top_k=cfg.top_k,
            seed=cfg.seed,
            universe=cfg.universe,
            cost=cfg.cost,
            window=cfg.window,
            ledger_path=cfg.ledger_path,
            structural_only=True,
            ban_textbook=True,
            use_l1b_fitness=True,
            public_panels=public_panels,
            lambda_complexity=cfg.lambda_complexity,
            lambda_turnover=cfg.lambda_turnover,
            top_n=cfg.top_n,
        )
        res = gp_search(panels, label, local)
        evaluations = res.evaluations
        ledger_n = res.ledger_tail_n
        for c in res.top_k:
            gp_top.append(c.as_row())
    return StageArtifact(
        stage="evolve",
        ok=True,
        payload={
            "seed_exprs": seeds,
            "gp_top": gp_top,
            "evaluations": evaluations,
            "ledger_N": ledger_n,
            "direction_id": direction.direction_id,
            "promotion_approved": False,
        },
    )


def backtest_candidates(
    expr_strs: Sequence[str],
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    *,
    direction: Direction,
    capital_cny: int,
    cost: float,
    top_n: int,
    public_panels: Mapping[str, pd.DataFrame] | None,
    ledger_path: Path | None,
    seed: int,
    window: str,
    universe: str,
) -> StageArtifact:
    rows: list[dict[str, Any]] = []
    last_n = 0
    for expr_s in expr_strs:
        if is_textbook_expr(expr_s):
            append_attempt(
                engine="quantmind_loop",
                seed=seed,
                universe=universe,
                cost=cost,
                window=window,
                expr_str=expr_s,
                fitness=None,
                notes="rejected_textbook_ban",
                path=ledger_path,
            )
            continue
        if not is_structural_expr(expr_s):
            append_attempt(
                engine="quantmind_loop",
                seed=seed,
                universe=universe,
                cost=cost,
                window=window,
                expr_str=expr_s,
                fitness=None,
                notes="rejected_non_structural",
                path=ledger_path,
            )
            continue
        try:
            expr = parse_expr(_expr_str_to_tuple(expr_s, panels))
            fac = apply_expr(expr, panels)
        except Exception as exc:  # noqa: BLE001
            append_attempt(
                engine="quantmind_loop",
                seed=seed,
                universe=universe,
                cost=cost,
                window=window,
                expr_str=expr_s,
                fitness=None,
                notes=f"impl_error:{type(exc).__name__}",
                path=ledger_path,
            )
            continue
        met = fitness_score_l1b(
            fac,
            label,
            public_panels=public_panels,
            cost_one_way=cost,
            top_n=top_n,
            lambda_complexity=0.015,
            n_nodes=expr.n_nodes(),
            lambda_turnover=1.0,
        )
        # Capacity note at Leo capital (no sqrt impact at 60/100万 — almost negligible ADV)
        ann_net = met.get("ann_net")
        fit = met.get("fitness")
        row = append_attempt(
            engine="quantmind_loop",
            seed=seed,
            universe=universe,
            cost=cost,
            window=window,
            expr_str=expr_s,
            fitness=float(fit) if fit is not None and np.isfinite(fit) else None,
            notes=(
                f"icir={met.get('icir')};ann_net={ann_net};"
                f"novelty_fail={met.get('novelty_fail')};"
                f"capital_cny={capital_cny};tag={direction.mechanism_tag}"
            ),
            path=ledger_path,
        )
        last_n = int(row["N"])
        leaves = _leaves_of(expr_s)
        who = direction.who_pays_zh
        if len(leaves) == 1:
            who = who_pays_for_leaf(next(iter(leaves)))
        rows.append(
            {
                "expr": expr_s,
                "metrics": {k: _jsonable(v) for k, v in met.items()},
                "capital_cny": capital_cny,
                "mechanism_tag": direction.mechanism_tag,
                "who_pays_zh": who,
                "promotion_approved": False,
                "ledger_N": last_n,
            }
        )
    # sort by fitness then ann_net
    def key(r: dict) -> float:
        m = r.get("metrics") or {}
        f = m.get("fitness")
        return float(f) if isinstance(f, (int, float)) and np.isfinite(f) else -1e18

    rows.sort(key=key, reverse=True)
    return StageArtifact(
        stage="backtest",
        ok=True,
        payload={"candidates": rows, "ledger_N": last_n, "promotion_approved": False},
    )


def explain_candidates(candidates: Sequence[dict[str, Any]], direction: Direction) -> StageArtifact:
    explained = []
    for c in candidates:
        m = c.get("metrics") or {}
        reasons = []
        if is_textbook_expr(c.get("expr", "")):
            reasons.append("TEXTBOOK_BAN — control only, not main")
        if m.get("novelty_fail"):
            reasons.append("public_factor_corr>0.5")
        ann = m.get("ann_net")
        if ann is None or not isinstance(ann, (int, float)) or not np.isfinite(ann) or ann <= 0:
            reasons.append("ann_net_nonpositive")
        gate_ok = len(reasons) == 0 and not is_textbook_expr(c.get("expr", ""))
        explained.append(
            {
                "expr": c.get("expr"),
                "mechanism_tag": c.get("mechanism_tag") or direction.mechanism_tag,
                "who_pays_zh": c.get("who_pays_zh") or direction.who_pays_zh,
                "direction_zh": direction.text_zh,
                "icir": m.get("icir"),
                "ann_net": ann,
                "turnover": m.get("turnover"),
                "capital_cny": c.get("capital_cny"),
                "gate_ok": gate_ok,
                "fail_reasons": reasons,
                "ask_sealed": False,  # never auto-ask
                "promotion_approved": False,
            }
        )
    return StageArtifact(
        stage="explain",
        ok=True,
        payload={"explain": explained, "promotion_approved": False},
    )


def export_artifacts(
    *,
    out_dir: Path,
    result_stub: dict[str, Any],
    top_k: Sequence[dict[str, Any]],
    explain: Sequence[dict[str, Any]],
) -> StageArtifact:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "run_meta": str(out_dir / "run_meta.json"),
        "top_k": str(out_dir / "top_k.json"),
        "explain": str(out_dir / "explain.json"),
    }
    (out_dir / "run_meta.json").write_text(
        json.dumps(result_stub, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "top_k.json").write_text(
        json.dumps(list(top_k), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "explain.json").write_text(
        json.dumps(list(explain), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Markdown short explain for humans
    lines = [
        "# QuantMind min-loop explain",
        "",
        f"- promotion_approved: false",
        f"- capital_cny: {result_stub.get('capital_cny')}",
        f"- direction: {result_stub.get('direction_id')}",
        f"- ledger_N: {result_stub.get('ledger_N')}",
        "",
        "| expr | icir | ann_net | gate_ok | who_pays |",
        "|---|---|---|---|---|",
    ]
    for e in explain[:20]:
        lines.append(
            f"| `{e.get('expr')}` | {e.get('icir')} | {e.get('ann_net')} | "
            f"{e.get('gate_ok')} | {e.get('who_pays_zh','')[:40]} |"
        )
    md = out_dir / "explain.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    paths["explain_md"] = str(md)
    return StageArtifact(stage="export", ok=True, payload={"paths": paths})


def run_quantmind_loop(
    *,
    panels: Mapping[str, pd.DataFrame],
    label: pd.DataFrame,
    direction: Direction,
    out_dir: Path,
    capital_cny: int = 600_000,
    public_panels: Mapping[str, pd.DataFrame] | None = None,
    gp_config: GPConfig | None = None,
    extra_expr_strs: Sequence[str] | None = None,
) -> LoopRunResult:
    """Full five-stage loop; ledger increments on every attempt."""
    if capital_cny not in CAPITAL_CNY_ALLOWED:
        raise ValueError(f"capital_cny must be in {sorted(CAPITAL_CNY_ALLOWED)}")
    cfg = gp_config or GPConfig(
        population=0,
        generations=0,
        max_evaluations=0,
        top_k=10,
        structural_only=True,
        ban_textbook=True,
        use_l1b_fitness=True,
    )
    result = LoopRunResult(direction=direction, capital_cny=capital_cny)

    pf = preflight(
        panels=panels,
        label=label,
        direction=direction,
        capital_cny=capital_cny,
        structural_only=True,
    )
    result.stages.append(pf)
    if not pf.ok:
        result.notes.append("preflight_failed")
        result.export_paths = export_artifacts(
            out_dir=out_dir,
            result_stub=_stub(result),
            top_k=[],
            explain=[],
        ).payload["paths"]
        return result

    ev = evolve_from_seeds_and_gp(
        panels, label, direction, cfg=cfg, public_panels=public_panels
    )
    result.stages.append(ev)
    result.evaluations = int(ev.payload.get("evaluations") or 0)
    result.ledger_N = int(ev.payload.get("ledger_N") or 0)

    expr_pool: list[str] = []
    expr_pool.extend(ev.payload.get("seed_exprs") or [])
    for row in ev.payload.get("gp_top") or []:
        if row.get("expr"):
            expr_pool.append(row["expr"])
    if extra_expr_strs:
        expr_pool.extend(extra_expr_strs)
    # unique preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for e in expr_pool:
        if e not in seen:
            seen.add(e)
            uniq.append(e)

    bt = backtest_candidates(
        uniq,
        panels,
        label,
        direction=direction,
        capital_cny=capital_cny,
        cost=cfg.cost,
        top_n=cfg.top_n,
        public_panels=public_panels,
        ledger_path=cfg.ledger_path,
        seed=cfg.seed,
        window=cfg.window,
        universe=cfg.universe,
    )
    result.stages.append(bt)
    cands = bt.payload.get("candidates") or []
    if bt.payload.get("ledger_N"):
        result.ledger_N = int(bt.payload["ledger_N"])
    # Main Top-K: ban textbook, require structural
    main = [
        c
        for c in cands
        if not is_textbook_expr(c["expr"]) and is_structural_expr(c["expr"])
    ]
    result.top_k = main[: cfg.top_k]

    ex = explain_candidates(result.top_k, direction)
    result.stages.append(ex)
    result.explain = ex.payload.get("explain") or []

    exp = export_artifacts(
        out_dir=out_dir,
        result_stub=_stub(result),
        top_k=result.top_k,
        explain=result.explain,
    )
    result.stages.append(exp)
    result.export_paths = exp.payload.get("paths") or {}
    assert result.promotion_approved is False
    return result


def _stub(result: LoopRunResult) -> dict[str, Any]:
    return {
        "promotion_approved": False,
        "capital_cny": result.capital_cny,
        "capital_cny_allowed": sorted(CAPITAL_CNY_ALLOWED),
        "direction_id": result.direction.direction_id if result.direction else None,
        "mechanism_tag": result.direction.mechanism_tag if result.direction else None,
        "ledger_N": result.ledger_N,
        "evaluations": result.evaluations,
        "stages": [s.stage for s in result.stages],
        "stage_ok": {s.stage: s.ok for s in result.stages},
        "notes": result.notes,
        "n_top_k": len(result.top_k),
        "sealed": False,
    }


def _jsonable(v: Any) -> Any:
    if isinstance(v, (np.floating, float)):
        x = float(v)
        return x if np.isfinite(x) else None
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v


def _leaves_of(expr_str: str) -> set[str]:
    from quantlab.factors.ai_factory.novelty import leaves_in_expr_str

    return leaves_in_expr_str(expr_str)


def _expr_str_to_tuple(expr_str: str, panels: Mapping[str, pd.DataFrame]) -> tuple:
    """Parse a minimal subset: leaf | op(leaf) | op(a, b) nested.

    For smoke/dry we also accept bare leaf names present in panels.
    """
    s = expr_str.strip()
    if s in panels:
        return ("leaf", s)
    # recursive descent for name(args)
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\((.*)\)", s)
    if not m:
        # unknown bare token → leaf (apply_expr will KeyError if missing)
        return ("leaf", s)
    name, inner = m.group(1), m.group(2)
    if not inner.strip():
        return ("op", name)
    args = _split_args(inner)
    kids = tuple(_expr_str_to_tuple(a.strip(), panels) for a in args)
    return ("op", name, *kids)


def _split_args(inner: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in inner:
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return parts
