"""Single overall promotion gate for the V2 platform (Eng).

THE ONE SWITCH
--------------
``OVERALL_PROMOTION_OVERRIDE`` below is the only place that decides whether
Mandate / paper / eng smoke outputs may carry overall ``promotion_approved=True``.

* ``ENG_PING_PATHS.json`` (Data) reports ``promotion_approved_overall`` — we read
  it via :func:`data_reported_overall` for visibility only.
* While ``OVERALL_PROMOTION_OVERRIDE`` is ``False`` the platform forces overall
  ``False`` regardless of what Data reports. Reason: Leo has not confirmed the
  overall lift in the Eng chat (Data reported approval 2026-10-10 20:51 ET in the
  Data chat only).

To lift later (after Leo confirms in Eng chat): change the line to
``OVERALL_PROMOTION_OVERRIDE: bool | None = None`` (→ follow ENG_PING), then
remove the hard ``must_be_false`` asserts listed in docs/v2/ACCEPTED_DEFAULTS.md.

Per-dataset acceptance (``promotable`` / dataset ``promotion_approved``) is
separate: see :func:`dataset_accepted`. Dataset PASS never implies overall.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ENG_PING_PATH = Path(__file__).resolve().parents[1] / "output" / "d1" / "ENG_PING_PATHS.json"

# >>> ONE-LINE SWITCH: False = force overall False (pending Leo Eng confirmation).
#     None = follow ENG_PING promotion_approved_overall.  <<<
OVERALL_PROMOTION_OVERRIDE: bool | None = None

OVERRIDE_REASON = "lifted: Leo confirmed in Eng chat 2026-10-10 20:52 ET; Data acceptance all PASS"


@lru_cache(maxsize=1)
def _eng_ping() -> dict:
    try:
        return json.loads(ENG_PING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def data_reported_overall() -> bool:
    """What Data's ENG_PING says (informational; not the gate)."""
    return _eng_ping().get("promotion_approved_overall") is True


def overall_promotion_approved() -> bool:
    """THE gate. All overall promotion_approved values must come from here."""
    if OVERALL_PROMOTION_OVERRIDE is not None:
        return bool(OVERALL_PROMOTION_OVERRIDE)
    return data_reported_overall()


def dataset_accepted(key: str) -> bool:
    """Per-dataset acceptance from ENG_PING ``acceptance[key].pass`` (dataset-level only)."""
    block = (_eng_ping().get("acceptance") or {}).get(key) or {}
    return block.get("pass") is True and not block.get("blockers")


def gate_status() -> dict:
    return {
        "overall_promotion_approved": overall_promotion_approved(),
        "data_reported_overall": data_reported_overall(),
        "override": OVERALL_PROMOTION_OVERRIDE,
        "override_reason": OVERRIDE_REASON if OVERALL_PROMOTION_OVERRIDE is False else None,
        "eng_ping": str(ENG_PING_PATH),
    }
