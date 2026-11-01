"""E1 zero-cost dual-engine reconciliation scaffold (research-grade).

Ready-to-plug wrapper around ``quantlab.platform.execution.reconcile_zero_cost`` /
``cost_ladder`` / ``load_execution_panels``. When Strategy finishes S1 Full D1,
point ``--weights-dir`` (or ``--weights``) at the real portfolio dump — no need
to re-implement the engines. Default file is ``planned_target_weights.parquet``;
undotted Strategy ids (``sh510300``) are normalized to platform form.

Defaults stay OFF: bare ``ExecConfig()`` is untouched; zero-cost reconcile uses
an explicit no-cost config. Research-only: no performance conclusions.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from quantlab.platform.execution import (
    ExecConfig,
    ExecPanels,
    ZERO_COST,
    cost_ladder,
    load_execution_panels,
    reconcile_zero_cost,
    run_weight_schedule,
)

# Files Strategy may leave under an arm / run directory.
# Default schedule input is planned_target_weights (pre-fill); engines simulate fills.
# target_weights is post-fill actual (compare realized weights); arm_b_* is arm B.
WEIGHT_FILE_ALIASES: dict[str, str] = {
    "planned": "planned_target_weights.parquet",
    "actual": "target_weights.parquet",
    "arm_b": "arm_b_target_weights.parquet",
    "planned_target_weights.parquet": "planned_target_weights.parquet",
    "target_weights.parquet": "target_weights.parquet",
    "arm_b_target_weights.parquet": "arm_b_target_weights.parquet",
}

WEIGHT_FILE_CANDIDATES: tuple[str, ...] = (
    "planned_target_weights.parquet",
    "planned_target_weights.csv",
    "target_weights.parquet",
    "target_weights.csv",
    "arm_b_target_weights.parquet",
    "arm_b_target_weights.csv",
    "weights.parquet",
    "weights.csv",
    "signal_weights.parquet",
    "signal_weights.csv",
    "rebalance_weights.parquet",
    "rebalance_weights.csv",
    "schedule.json",
    "schedule.parquet",
    "schedule.csv",
)

DEFAULT_WEIGHTS_FILE = "planned_target_weights.parquet"

ARM_DIR_GLOBS: tuple[str, ...] = (
    "arm_a*",
    "arm_A*",
    "zero_cost*",
    "A_*",
)

PAPER_NAV_CANDIDATES: tuple[str, ...] = (
    "nav.csv",
    "paper_nav.csv",
    "nav.parquet",
)

LONG_COL_ALIASES = {
    "session": ("session", "date", "trade_date", "signal_session", "rebalance_date"),
    "code": ("instrument_id", "code", "symbol", "ts_code", "iid"),
    "weight": ("weight", "w", "target_weight", "target_w", "wgt"),
}

__all__ = [
    "WEIGHT_FILE_CANDIDATES",
    "WEIGHT_FILE_ALIASES",
    "DEFAULT_WEIGHTS_FILE",
    "normalize_instrument_id",
    "resolve_weights_filename",
    "load_schedule",
    "load_paper_nav",
    "ids_from_schedule",
    "discover_weights_path",
    "build_e1_report",
    "write_e1_report",
    "run_e1",
    "synthetic_dry_run",
    "schedule_from_wide",
    "schedule_from_long",
]


# ----------------------------------------------------------------- loaders
def _norm_session(x) -> pd.Timestamp:
    return pd.Timestamp(x).normalize()


def normalize_instrument_id(code: str) -> str:
    """Map Strategy undotted ids to platform form.

    ``sh510300`` → ``sh.510300``, ``sh600000`` → ``sh.600000``,
    ``sz000001`` → ``sz.000001``, ``bj430047`` → ``bj.430047``.
    Already-dotted ids (``sh.510300``) and unrelated strings pass through.
    """
    s = str(code).strip()
    if not s:
        return s
    low = s.lower()
    for pref in ("sh", "sz", "bj"):
        if low.startswith(pref + ".") and len(low) > len(pref) + 1:
            return pref + "." + low[len(pref) + 1 :]
        if low.startswith(pref) and len(low) > len(pref) and low[len(pref)].isdigit():
            return pref + "." + low[len(pref) :]
    return s


def schedule_from_wide(df: pd.DataFrame) -> dict[pd.Timestamp, dict[str, float]]:
    """Wide panel: index = session, columns = codes, values = weights."""
    out: dict[pd.Timestamp, dict[str, float]] = {}
    idx = pd.to_datetime(df.index).normalize()
    for i, sess in enumerate(idx):
        row = df.iloc[i]
        w = {normalize_instrument_id(c): float(v) for c, v in row.items() if pd.notna(v) and abs(float(v)) > 1e-15}
        out[_norm_session(sess)] = w
    return out


def schedule_from_long(df: pd.DataFrame) -> dict[pd.Timestamp, dict[str, float]]:
    """Long format: columns session / instrument_id / weight (aliases accepted)."""
    cols = {c.lower(): c for c in df.columns}

    def pick(aliases: Sequence[str]) -> str:
        for a in aliases:
            if a.lower() in cols:
                return cols[a.lower()]
            if a in df.columns:
                return a
        raise ValueError(f"weights_long_missing_column:{aliases}")

    s_col = pick(LONG_COL_ALIASES["session"])
    c_col = pick(LONG_COL_ALIASES["code"])
    w_col = pick(LONG_COL_ALIASES["weight"])
    out: dict[pd.Timestamp, dict[str, float]] = {}
    for sess, g in df.groupby(pd.to_datetime(df[s_col]).dt.normalize(), sort=True):
        w = {
            normalize_instrument_id(r[c_col]): float(r[w_col])
            for _, r in g.iterrows()
            if pd.notna(r[w_col]) and abs(float(r[w_col])) > 1e-15
        }
        out[_norm_session(sess)] = w
    return out


def schedule_from_json(obj: Any) -> dict[pd.Timestamp, dict[str, float]]:
    """JSON: ``{session: {code: weight}}`` or list of ``{session, instrument_id, weight}``."""
    if isinstance(obj, list):
        return schedule_from_long(pd.DataFrame(obj))
    if not isinstance(obj, Mapping):
        raise ValueError("schedule_json_must_be_object_or_list")
    out: dict[pd.Timestamp, dict[str, float]] = {}
    for k, v in obj.items():
        if not isinstance(v, Mapping):
            raise ValueError(f"schedule_json_bad_entry:{k}")
        out[_norm_session(k)] = {
            normalize_instrument_id(c): float(w)
            for c, w in v.items()
            if w is not None and abs(float(w)) > 1e-15
        }
    return out


def _read_table(path: Path) -> pd.DataFrame | Any:
    suf = path.suffix.lower()
    if suf == ".json":
        return json.loads(path.read_text())
    if suf == ".parquet":
        return pd.read_parquet(path)
    if suf in (".csv", ".tsv"):
        sep = "\t" if suf == ".tsv" else ","
        return pd.read_csv(path, sep=sep)
    raise ValueError(f"unsupported_weights_suffix:{suf}")


def _table_to_schedule(path: Path, raw: Any) -> dict[pd.Timestamp, dict[str, float]]:
    if path.suffix.lower() == ".json" or isinstance(raw, (dict, list)):
        return schedule_from_json(raw)
    assert isinstance(raw, pd.DataFrame)
    cols_l = {c.lower() for c in raw.columns}
    long_hints = {"weight", "w", "target_weight", "target_w", "wgt"} & cols_l
    code_hints = {"instrument_id", "code", "symbol", "ts_code", "iid"} & cols_l
    sess_hints = {"session", "date", "trade_date", "signal_session", "rebalance_date"} & cols_l
    if long_hints and code_hints and sess_hints:
        return schedule_from_long(raw)
    # wide: first column may be the session index written as a column
    if raw.columns[0].lower() in sess_hints or raw.index.name in sess_hints or str(raw.index.dtype).startswith("datetime"):
        df = raw.copy()
        if raw.columns[0].lower() in sess_hints and not str(raw.index.dtype).startswith("datetime"):
            df = df.set_index(raw.columns[0])
        df.index = pd.to_datetime(df.index)
        return schedule_from_wide(df)
    # try index as sessions, remaining numeric cols as codes
    df = raw.copy()
    df.index = pd.to_datetime(df.index)
    return schedule_from_wide(df)


def resolve_weights_filename(
    weights_file: str | None = None,
    *,
    arm: str | None = None,
) -> str:
    """Resolve ``--weights-file`` / ``--arm`` to a concrete filename.

    Default is ``planned_target_weights.parquet`` (pre-fill schedule for engines).
    ``--arm b`` selects ``arm_b_target_weights.parquet``. Short aliases:
    ``planned`` / ``actual`` / ``arm_b``.
    """
    if arm is not None and str(arm).lower() in ("b", "arm_b", "arm-b"):
        return WEIGHT_FILE_ALIASES["arm_b"]
    key = (weights_file or DEFAULT_WEIGHTS_FILE).strip()
    if key in WEIGHT_FILE_ALIASES:
        return WEIGHT_FILE_ALIASES[key]
    # allow bare stem without .parquet
    if key + ".parquet" in WEIGHT_FILE_ALIASES:
        return WEIGHT_FILE_ALIASES[key + ".parquet"]
    return key


def discover_weights_path(
    weights_dir: str | Path,
    *,
    preferred: str | None = None,
) -> Path | None:
    """Find a weights/schedule file under a Strategy run or arm directory.

    Search order: ``preferred`` name (if given) in ``weights_dir`` then one level
    of arm_* / zero_cost_* subdirs; then the full ``WEIGHT_FILE_CANDIDATES`` list
    in the same locations (S1 layout: ``full_d1_fixed_armA/`` or arm subdir).
    """
    root = Path(weights_dir)
    if not root.is_dir():
        return None
    names: list[str] = []
    if preferred:
        names.append(preferred)
    for n in WEIGHT_FILE_CANDIDATES:
        if n not in names:
            names.append(n)

    def _find(names_: list[str]) -> Path | None:
        for name in names_:
            p = root / name
            if p.is_file():
                return p
        for pat in ARM_DIR_GLOBS:
            for sub in sorted(root.glob(pat)):
                if not sub.is_dir():
                    continue
                for name in names_:
                    p = sub / name
                    if p.is_file():
                        return p
        return None

    # If preferred is set, require it when present anywhere; else fall back.
    if preferred:
        hit = _find([preferred])
        if hit is not None:
            return hit
        # preferred missing: fall back only if preferred was the default discovery
        # path without an explicit require — keep fallback for robustness.
    return _find(names)


def load_schedule(
    *,
    weights_dir: str | Path | None = None,
    weights_path: str | Path | None = None,
    weights_file: str | None = None,
    arm: str | None = None,
) -> tuple[dict[pd.Timestamp, dict[str, float]], dict]:
    """Load a signal schedule from (a) dir discovery or (b) explicit panel path.

    Instrument ids are normalized to platform form (``sh510300`` → ``sh.510300``).
    Default file under ``weights_dir`` is ``planned_target_weights.parquet``
    (pre-fill targets; engines simulate fills). Pass ``weights_file='actual'`` /
    ``target_weights.parquet`` for post-fill realized weights, or ``arm='b'`` /
    ``weights_file='arm_b'`` for arm B.

    Returns ``(schedule, meta)`` where schedule maps signal session -> {code: weight}.
    """
    preferred = resolve_weights_filename(weights_file, arm=arm)
    meta: dict[str, Any] = {
        "source": None,
        "path": None,
        "format": None,
        "n_signals": 0,
        "n_codes": 0,
        "weights_file": preferred,
        "arm": arm,
    }
    path: Path | None = None
    if weights_path is not None:
        path = Path(weights_path)
        if not path.is_file():
            raise FileNotFoundError(f"weights_path_missing:{path}")
    elif weights_dir is not None:
        path = discover_weights_path(weights_dir, preferred=preferred)
        if path is None:
            raise FileNotFoundError(
                f"weights_not_found_under:{weights_dir};"
                f"preferred={preferred};"
                f"expected_one_of={list(WEIGHT_FILE_CANDIDATES)};"
                "Strategy should dump planned_target_weights.parquet "
                "(long: session,instrument_id,weight; undotted ids ok) under the arm dir"
            )
    else:
        raise ValueError("weights_dir_or_weights_path_required")
    raw = _read_table(path)
    sched = _table_to_schedule(path, raw)
    codes: set[str] = set()
    for w in sched.values():
        codes.update(w)
    meta.update(
        source="weights_dir" if weights_dir and weights_path is None else "weights_path",
        path=str(path.resolve()),
        format=("json" if path.suffix.lower() == ".json" else "table"),
        n_signals=len(sched),
        n_codes=len(codes),
        sessions=[str(s.date()) for s in sorted(sched)],
        weights_file_resolved=path.name,
    )
    return sched, meta


def load_paper_nav(path: str | Path | None = None, *, weights_dir: str | Path | None = None) -> pd.Series | None:
    """Optional Strategy paper NAV (level or unit). Discovers ``nav.csv`` under dir if path omitted."""
    p: Path | None = Path(path) if path else None
    if p is None and weights_dir is not None:
        root = Path(weights_dir)
        for name in PAPER_NAV_CANDIDATES:
            cand = root / name
            if cand.is_file():
                p = cand
                break
        if p is None:
            for pat in ARM_DIR_GLOBS:
                for sub in sorted(root.glob(pat)):
                    for name in PAPER_NAV_CANDIDATES:
                        cand = sub / name
                        if cand.is_file():
                            p = cand
                            break
                    if p is not None:
                        break
                if p is not None:
                    break
    if p is None:
        return None
    if not p.is_file():
        raise FileNotFoundError(f"paper_nav_missing:{p}")
    if p.suffix.lower() == ".parquet":
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p)
    if isinstance(df, pd.Series):
        s = df
    else:
        cols_l = {c.lower(): c for c in df.columns}
        nav_col = None
        for k in ("nav", "nav_a", "paper_nav", "equity"):
            if k in cols_l:
                nav_col = cols_l[k]
                break
        if nav_col is None:
            # single numeric column
            num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(num) == 1:
                nav_col = num[0]
            else:
                raise ValueError(f"paper_nav_column_ambiguous:{list(df.columns)}")
        date_col = None
        for k in ("date", "session", "trade_date"):
            if k in cols_l:
                date_col = cols_l[k]
                break
        if date_col is not None:
            s = pd.Series(df[nav_col].to_numpy(), index=pd.to_datetime(df[date_col]))
        else:
            s = pd.Series(df[nav_col].to_numpy(), index=pd.to_datetime(df.index))
    s.index = pd.to_datetime(s.index).normalize()
    s = s.astype(float).sort_index()
    s.name = "paper_nav"
    return s


def ids_from_schedule(schedule: Mapping) -> list[str]:
    codes: set[str] = set()
    for w in schedule.values():
        codes.update(map(str, w))
    return sorted(codes)


# ----------------------------------------------------------------- units note
def _units_note_from_eng_ping() -> dict:
    ping = Path(__file__).resolve().parents[2] / "output" / "d1" / "ENG_PING_PATHS.json"
    if not ping.is_file():
        return {"note": "ENG_PING_PATHS.json missing"}
    try:
        data = json.loads(ping.read_text())
    except json.JSONDecodeError:
        return {"note": "ENG_PING_PATHS.json unreadable"}
    return dict(data.get("units_note") or {})


def _execconfig_snapshot(cfg: ExecConfig) -> dict:
    d = asdict(cfg) if is_dataclass(cfg) else dict(cfg.__dict__)
    # frozenset -> list for JSON
    if isinstance(d.get("no_limit_codes"), (set, frozenset)):
        d["no_limit_codes"] = sorted(d["no_limit_codes"])
    return {k: (None if v is None else v) for k, v in d.items()}


# ----------------------------------------------------------------- report
_REQUIRED_SUMMARY_KEYS = (
    "reference",
    "first_divergence",
    "max_abs_diff",
    "max_abs_rel_diff",
    "effective_n_mean",
    "research_only",
    "promotion_approved",
)


def build_e1_report(
    reconcile: dict,
    *,
    schedule_meta: Mapping | None = None,
    panel_diag: Mapping | None = None,
    exec_snapshot: Mapping | None = None,
    cost_ladder_df: pd.DataFrame | None = None,
    impact_bp: float | None = None,
    effective_n_mean: float | None = None,
    root_cause_notes: Sequence[str] | None = None,
    units_note: Mapping | None = None,
) -> dict:
    """Assemble the E1 report dict (JSON-serializable where possible)."""
    navs: pd.DataFrame = reconcile["navs"]
    diffs: dict = reconcile["diffs"]
    ref = reconcile["reference"]
    # aggregate first / max across engines vs reference
    firsts = [d.get("first_divergence") for d in diffs.values() if d.get("first_divergence")]
    first_divergence = min(firsts) if firsts else None
    max_abs = max((float(d.get("max_abs_diff") or 0.0) for d in diffs.values()), default=0.0)
    max_rel = max((float(d.get("max_abs_rel_diff") or 0.0) for d in diffs.values()), default=0.0)
    notes = list(root_cause_notes or [
        "tick: platform/ledger/fastsim zero-cost path use per-code tick (0.01 stocks, 0.001 exchange funds; Ledger rounding)",
        "lot rounding: order_rounding='target' (lot-floor target holding); legacy delta kept as *_delta_rounding columns",
        "valuation: holdings marked to close; halt/limit only block fills",
        "research_only: no strategy performance conclusions",
    ])
    # per-day NAV frame
    nav_df = navs.copy()
    nav_df.index = pd.to_datetime(nav_df.index)
    # per-day diffs vs reference
    per_day = {}
    for name, d in diffs.items():
        s = d.get("per_day_diff")
        if isinstance(s, pd.Series):
            per_day[name] = s
    per_day_df = pd.DataFrame(per_day) if per_day else pd.DataFrame(index=nav_df.index)

    if effective_n_mean is None and "actual_weights" in reconcile:
        pass  # not always present on reconcile output
    summary = {
        "reference": ref,
        "first_divergence": first_divergence,
        "max_abs_diff": max_abs,
        "max_abs_rel_diff": max_rel,
        "effective_n_mean": float(effective_n_mean) if effective_n_mean is not None else None,
        "impact_bp_per_traded": float(impact_bp) if impact_bp is not None else None,
        "research_only": True,
        "promotion_approved": False,
        "engines": list(nav_df.columns),
        "n_sessions": int(len(nav_df)),
        "diffs_summary": {
            k: {
                "first_divergence": v.get("first_divergence"),
                "max_abs_diff": float(v.get("max_abs_diff") or 0.0),
                "max_abs_rel_diff": float(v.get("max_abs_rel_diff") or 0.0),
            }
            for k, v in diffs.items()
        },
        "schedule": dict(schedule_meta or {}),
        "panel_diag": dict(panel_diag or {}),
        "exec_config": dict(exec_snapshot or _execconfig_snapshot(
            ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None,
                       price_tick="auto", order_rounding="target", **ZERO_COST)
        )),
        "units_note": dict(units_note if units_note is not None else _units_note_from_eng_ping()),
        "root_cause_notes": notes,
        "cost_ladder_present": cost_ladder_df is not None,
    }
    return {
        "summary": summary,
        "navs": nav_df,
        "per_day_diffs": per_day_df,
        "cost_ladder": cost_ladder_df,
        "diffs_raw": diffs,
    }


def write_e1_report(report: dict, out_dir: str | Path) -> dict[str, str]:
    """Write JSON + CSV + short ZH markdown under ``out_dir``. Returns written paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    summary = report["summary"]
    (out / "e1_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    paths["summary_json"] = str(out / "e1_summary.json")

    navs: pd.DataFrame = report["navs"]
    navs.to_csv(out / "e1_navs.csv", index_label="session")
    paths["navs_csv"] = str(out / "e1_navs.csv")

    diffs: pd.DataFrame = report["per_day_diffs"]
    if diffs is not None and not diffs.empty:
        diffs.to_csv(out / "e1_per_day_diffs.csv", index_label="session")
        paths["diffs_csv"] = str(out / "e1_per_day_diffs.csv")

    ladder = report.get("cost_ladder")
    if ladder is not None and isinstance(ladder, pd.DataFrame) and not ladder.empty:
        ladder.to_csv(out / "e1_cost_ladder.csv", index=False)
        paths["cost_ladder_csv"] = str(out / "e1_cost_ladder.csv")

    zh = _zh_markdown(summary, ladder if isinstance(ladder, pd.DataFrame) else None)
    (out / "E1_RECONCILE_ZH.md").write_text(zh)
    paths["zh_md"] = str(out / "E1_RECONCILE_ZH.md")
    return paths


def _zh_markdown(summary: Mapping, ladder: pd.DataFrame | None) -> str:
    lines = [
        "# E1 零成本双引擎对账（研究级）",
        "",
        f"- 参考引擎: `{summary.get('reference')}`",
        f"- 首次分歧日: `{summary.get('first_divergence')}`",
        f"- max_abs_diff: `{summary.get('max_abs_diff')}`",
        f"- max_abs_rel_diff: `{summary.get('max_abs_rel_diff')}`",
        f"- effective_n_mean: `{summary.get('effective_n_mean')}`",
        f"- impact_bp_per_traded: `{summary.get('impact_bp_per_traded')}`",
        f"- promotion_approved: `{summary.get('promotion_approved')}`（研究级，恒为 false）",
        f"- 会话数: `{summary.get('n_sessions')}`",
        "",
        "## 引擎差异摘要",
    ]
    for name, d in (summary.get("diffs_summary") or {}).items():
        lines.append(
            f"- **{name}**: first=`{d.get('first_divergence')}`, "
            f"max_abs=`{d.get('max_abs_diff')}`, max_rel=`{d.get('max_abs_rel_diff')}`"
        )
    lines += ["", "## 口径备注"]
    for n in summary.get("root_cause_notes") or []:
        lines.append(f"- {n}")
    units = summary.get("units_note") or {}
    if units:
        lines += ["", "## 单位（ENG_PING units_note）"]
        for k, v in units.items():
            lines.append(f"- `{k}`: {v}")
    if ladder is not None and not ladder.empty:
        lines += ["", "## cost_ladder（逐项加成本）", "", "```", ladder.to_string(index=False), "```"]
    lines += ["", "---", "本报告仅用于引擎对账，不构成策略业绩结论。"]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------- run
def run_e1(
    *,
    schedule: Mapping,
    start,
    end,
    out_dir: str | Path,
    instrument_ids: Sequence[str] | None = None,
    paper_nav: pd.Series | None = None,
    initial_cash: float = 600_000.0,
    with_costs: bool = False,
    max_instruments: int | None = None,
    schedule_meta: Mapping | None = None,
    panels: ExecPanels | None = None,
    panel_diag: Mapping | None = None,
    tol: float = 1e-9,
    corporate_actions: bool = True,
) -> dict:
    """Load panels (unless provided), reconcile zero-cost, optionally cost_ladder, write report."""
    ids = list(instrument_ids) if instrument_ids is not None else ids_from_schedule(schedule)
    if max_instruments is not None and len(ids) > max_instruments:
        ids = ids[: int(max_instruments)]
    if not ids:
        raise ValueError("e1_no_instrument_ids")
    diag: dict
    if panels is None:
        panels, diag = load_execution_panels(ids, start, end, corporate_actions=corporate_actions)
    else:
        diag = dict(panel_diag or {})
    rec = reconcile_zero_cost(panels, schedule, initial_cash=initial_cash, paper_nav=paper_nav, tol=tol,
                              corporate_actions=corporate_actions)
    ladder = None
    impact_bp = None
    eff_n = None
    cost_nav = None
    with_costs_info = None
    if with_costs:
        # cost ladder uses strategy_v1-like next_open base but starts from zero
        ladder = cost_ladder(panels, schedule, initial_cash=initial_cash, base=ExecConfig(
            fill="next_open", enforce_limits=False, participation_cap=None, lots=False,
            corporate_actions=corporate_actions, **ZERO_COST))
        # strategy_v1 full-cost run. Previously only impact_bp/effective_n were kept and its NAV was
        # discarded, so --with-costs outputs showed only zero-cost NAVs. Now kept as a NAV column.
        cfg = ExecConfig.strategy_v1(corporate_actions=corporate_actions)
        r = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=cfg, record_weights=False)
        impact_bp = float(r["impact_bp_per_traded"])
        eff_n = float(r["effective_n_mean"])
        cost_nav = r["nav"].copy(); cost_nav.index = pd.to_datetime(cost_nav.index)
        with_costs_info = dict(final_nav_strategy_v1=float(cost_nav.iloc[-1]),
                               final_nav_platform_zero_cost=float(rec["navs"]["platform"].iloc[-1]),
                               total_cost_cny=float(r.get("total_cost", float("nan"))),
                               fill_ratio=float(r.get("fill_ratio", float("nan"))))
        with_costs_info["delta_vs_zero_cost"] = (with_costs_info["final_nav_strategy_v1"]
                                                 - with_costs_info["final_nav_platform_zero_cost"])
    else:
        # effective_n from zero-cost platform run
        zcfg = ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None,
                          price_tick="auto", order_rounding="target", corporate_actions=corporate_actions, **ZERO_COST)
        zr = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=zcfg, record_weights=False)
        eff_n = float(zr["effective_n_mean"])
    report = build_e1_report(
        rec,
        schedule_meta=schedule_meta,
        panel_diag=diag,
        exec_snapshot=_execconfig_snapshot(
            ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None,
                       price_tick="auto", order_rounding="target", corporate_actions=corporate_actions, **ZERO_COST)
        ),
        cost_ladder_df=ladder,
        impact_bp=impact_bp,
        effective_n_mean=eff_n,
    )
    if cost_nav is not None:
        navs = report["navs"]
        navs["platform_strategy_v1_costs"] = cost_nav.reindex(navs.index)
        report["summary"]["with_costs"] = with_costs_info
        report["summary"]["engines"] = list(navs.columns)
    # Known reconciliation exceptions (Data rule 10-11): events whose implied multiplier differs from the
    # adj_factor change by >1% are 'special_reorg' -> platform & fast sim use the factor, the Ledger
    # cannot represent factor-only adjustments, so they are excluded from its action list.
    if corporate_actions:
        from quantlab.platform.execution import corporate_action_arrays
        sr_flags: list = []
        corporate_action_arrays(panels.aligned(), flags=sr_flags)
        held = set()
        for wts in schedule.values():
            held.update(str(k) for k, v in dict(wts).items() if v)
        exc = [dict(f, held_in_schedule=f["code"] in held) for f in sr_flags]
        report["summary"]["known_exceptions"] = dict(
            rule="special_reorg: |event_multiplier/factor_ratio-1|>1% -> factor used (platform+fastsim), excluded from ledger",
            n_special_reorg=len(exc), n_held=sum(e["held_in_schedule"] for e in exc), events=exc)
    paths = write_e1_report(report, out_dir)
    return {"report": report, "paths": paths, "reconcile": rec, "ids": ids}


def synthetic_dry_run(out_dir: str | Path, *, n_days: int = 6, n_codes: int = 2) -> dict:
    """Tiny synthetic schedule proving report fields populate. No full-universe IO."""
    dates = pd.bdate_range("2026-01-05", periods=n_days)
    codes = [f"sh.60000{i+1}" for i in range(n_codes)]
    rng = np.random.default_rng(0)
    close = pd.DataFrame(
        10 * np.cumprod(1 + rng.normal(0, 0.01, (n_days, n_codes)), axis=0),
        index=dates, columns=codes,
    ).round(2)
    open_ = close.shift(1).fillna(close.iloc[0]).round(2)
    vol = pd.DataFrame(1e6, index=dates, columns=codes)
    panels = ExecPanels(
        close=close, open=open_,
        high=pd.concat([close, open_]).groupby(level=0).max() * 1.01,
        low=pd.concat([close, open_]).groupby(level=0).min() * 0.99,
        volume=vol, amount=vol * close,
    )
    # equal-weight first session only
    w = 0.4 / n_codes
    schedule = {dates[0]: {c: w for c in codes}}
    meta = {"source": "synthetic_dry_run", "n_signals": 1, "n_codes": n_codes, "format": "synthetic"}
    return run_e1(
        schedule=schedule,
        start=dates[0],
        end=dates[-1],
        out_dir=out_dir,
        instrument_ids=codes,
        schedule_meta=meta,
        panels=panels,
        panel_diag={"synthetic": True, "n_codes": n_codes},
        with_costs=False,
    )


# ----------------------------------------------------------------- CLI
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m quantlab.platform.e1_reconcile",
                                description="E1 zero-cost dual-engine reconcile scaffold (research-only)")
    p.add_argument("--weights-dir", default=None, help="Strategy run/arm dir; discovers weights file")
    p.add_argument("--weights", default=None, help="Explicit weights panel (wide/long csv|parquet) or schedule.json")
    p.add_argument(
        "--weights-file",
        default=DEFAULT_WEIGHTS_FILE,
        help=(
            "Which file under --weights-dir to load (default: planned_target_weights.parquet). "
            "Aliases: planned | actual | arm_b. actual=target_weights.parquet (post-fill)."
        ),
    )
    p.add_argument(
        "--arm",
        default=None,
        choices=("a", "b", "A", "B"),
        help="Arm selector; --arm b loads arm_b_target_weights.parquet (overrides --weights-file)",
    )
    p.add_argument("--paper-nav", default=None, help="Optional paper NAV csv/parquet")
    p.add_argument("--start", default=None, help="Panel start YYYY-MM-DD (required unless --dry-run)")
    p.add_argument("--end", default=None, help="Panel end YYYY-MM-DD (required unless --dry-run)")
    p.add_argument("--out", required=True, help="Output directory for JSON/CSV/ZH md")
    p.add_argument("--ids-from-weights", action="store_true",
                   help="Restrict panels to codes present in the schedule (default behaviour)")
    p.add_argument("--with-costs", action="store_true", help="Also write cost_ladder + strategy_v1 impact_bp")
    p.add_argument("--max-instruments", type=int, default=None, help="Cap id list (memory guard)")
    p.add_argument("--initial-cash", type=float, default=600_000.0)
    p.add_argument("--corporate-actions", choices=("on", "off"), default="on",
                   help="on (default): ex-date cash/bonus handled; off: unadjusted (apples-to-apples vs paper)")
    p.add_argument("--dry-run", action="store_true", help="Synthetic tiny schedule; no market IO")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    out = Path(args.out)
    if args.dry_run:
        result = synthetic_dry_run(out)
        print(json.dumps({"ok": True, "dry_run": True, "paths": result["paths"],
                          "summary": result["report"]["summary"]}, ensure_ascii=False, default=str))
        return 0
    if not args.start or not args.end:
        print("--start and --end required unless --dry-run", file=sys.stderr)
        return 2
    if not args.weights_dir and not args.weights:
        print("--weights-dir or --weights required unless --dry-run", file=sys.stderr)
        return 2
    sched, meta = load_schedule(
        weights_dir=args.weights_dir,
        weights_path=args.weights,
        weights_file=args.weights_file,
        arm=args.arm,
    )
    paper = load_paper_nav(args.paper_nav, weights_dir=args.weights_dir)
    ids = ids_from_schedule(sched)  # --ids-from-weights is the default path
    result = run_e1(
        schedule=sched,
        start=args.start,
        end=args.end,
        out_dir=out,
        instrument_ids=ids,
        paper_nav=paper,
        initial_cash=args.initial_cash,
        with_costs=args.with_costs,
        max_instruments=args.max_instruments,
        schedule_meta=meta,
        corporate_actions=(args.corporate_actions == "on"),
    )
    summ = result["report"]["summary"]
    print(json.dumps({
        "ok": True,
        "paths": result["paths"],
        "first_divergence": summ.get("first_divergence"),
        "max_abs_rel_diff": summ.get("max_abs_rel_diff"),
        "n_ids": len(result["ids"]),
        "n_signals": meta.get("n_signals"),
        "research_only": True,
    }, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
