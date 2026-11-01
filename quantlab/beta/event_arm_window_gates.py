"""Event-arm dual-track window gates (research; strategy_promotion_approved=false).

Default mode = dual_track: do NOT kill a mechanism solely because full X1
(2015-06→2017-12) has zero events. See docs/v2/EVENT_ARM_WINDOW_GATES_ZH.md.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

import pandas as pd

_CFG_PATH = Path(__file__).resolve().parent / "configs" / "event_arm_window_gates.json"


def load_gates_config(path: Optional[Path] = None) -> dict:
    p = Path(path) if path else _CFG_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def classify_coverage(
    *,
    n_events_x1_full: int,
    n_events_native: int,
    gate_mode: Optional[str] = None,
    cfg: Optional[Mapping[str, Any]] = None,
) -> dict:
    """Return coverage label + whether zero-X1 alone may kill the arm.

    Parameters
    ----------
    n_events_x1_full : events with available_at in full X1 window
    n_events_native : events in the table's native PIT span (or book_window overlap)
    """
    cfg = dict(cfg or load_gates_config())
    mode = gate_mode or cfg.get("gate_mode_default", "dual_track")
    kill_on_x1_zero = bool(
        cfg.get("fail_precheck_rules", {}).get("x1_full_zero_alone", False)
    )
    if mode == "x1_full_hard":
        kill_on_x1_zero = True

    if n_events_native <= 0:
        label = "coverage_blocked"
    elif n_events_x1_full <= 0:
        label = "coverage_shifted"
    else:
        label = "coverage_ok"

    # dual_track: never kill solely on x1_full==0
    kill = False
    if label == "coverage_blocked":
        kill = True
    elif label == "coverage_shifted" and kill_on_x1_zero and mode == "x1_full_hard":
        kill = True

    return {
        "coverage_label": label,
        "gate_mode": mode,
        "n_events_x1_full": int(n_events_x1_full),
        "n_events_native": int(n_events_native),
        "kill_on_this_coverage": kill,
        "x1_full_zero_alone_is_kill": bool(kill_on_x1_zero and mode == "x1_full_hard"),
        "strategy_promotion_approved": False,
        "note": cfg.get("labels", {}).get(label, label),
    }


def window_bounds(name: str, cfg: Optional[Mapping[str, Any]] = None) -> tuple[Optional[str], Optional[str]]:
    cfg = dict(cfg or load_gates_config())
    w = cfg.get("windows", {}).get(name) or {}
    return w.get("start"), w.get("end")


def count_events_in_window(
    available_at: pd.Series,
    start: str,
    end: Optional[str],
) -> int:
    ts = pd.to_datetime(available_at)
    lo = pd.Timestamp(start)
    hi = pd.Timestamp(end) if end else ts.max()
    return int(((ts >= lo) & (ts <= hi)).sum())
