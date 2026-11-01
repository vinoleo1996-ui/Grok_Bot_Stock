"""HI_LIQ_V1.1 industry-cap helpers (Arch N1 / prereg §2).

PIT SW L1 on each hold day (not sticky event-day). Book ≤ IND_CAP (0.25);
sleeve share ≤25% via budget-equivalent book cap = 0.25 * MAX_NAMES * NAME_W
(=0.20 when 20×4%), matching capacity_adv IND_CAP_STOCK_SLEEVE.
Scale-down + redistribute overflow to unsaturated industries by signal order.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np

try:
    import research.hiliq_v1_universe as _FU
except Exception:  # pragma: no cover
    _FU = None


def pick_with_pit_ind_cap(
    candidates: list[str],
    session,
    sw,
    *,
    max_names: int = 20,
    name_w: float = 0.04,
    ind_cap_book: float = 0.25,
    ind_cap_sleeve: float = 0.25,
    industry_on_date=None,
) -> dict[str, float]:
    """Greedy by signal order with PIT industry; scale-down + redistribute.

    candidates: instruments in descending signal order (already unique).
    Returns {instrument: weight} (no ballast).
    """
    if not candidates:
        return {}
    fn = industry_on_date or (_FU.industry_on_date if _FU is not None else None)
    if fn is None:
        raise RuntimeError("industry_on_date required")
    ind_of = fn(candidates, session, sw)
    # sleeve budget at full book: enforces ≤25% sleeve when filled
    sleeve_budget = max_names * name_w
    book_cap = min(ind_cap_book, ind_cap_sleeve * sleeve_budget)
    maxn = max(1, int(np.floor(book_cap / max(name_w, 1e-12) + 1e-12)))

    pick: list[str] = []
    indc: dict[str, int] = {}
    for inst in candidates:
        code = ind_of.get(inst) or "_UNK"
        if indc.get(code, 0) >= maxn:
            continue
        pick.append(inst)
        indc[code] = indc.get(code, 0) + 1
        if len(pick) >= max_names:
            break
    w = {x: float(name_w) for x in pick}
    if not w:
        return {}

    # iterative scale-down + redistribute (prereg §2)
    for _ in range(12):
        ind_w: dict[str, float] = {}
        ind_members: dict[str, list[str]] = {}
        for inst, wv in w.items():
            code = ind_of.get(inst) or "_UNK"
            ind_w[code] = ind_w.get(code, 0.0) + wv
            ind_members.setdefault(code, []).append(inst)
        breached = {c: tw for c, tw in ind_w.items() if tw > book_cap + 1e-12}
        if not breached:
            break
        freed = 0.0
        for code, tw in breached.items():
            factor = book_cap / tw
            for inst in ind_members[code]:
                nw = w[inst] * factor
                freed += w[inst] - nw
                w[inst] = nw
        # redistribute by signal order to unsaturated industries
        for inst in candidates:
            if freed <= 1e-12:
                break
            code = ind_of.get(inst) or "_UNK"
            cur = sum(wv for i2, wv in w.items() if (ind_of.get(i2) or "_UNK") == code)
            room_ind = max(0.0, book_cap - cur)
            room_name = name_w - w.get(inst, 0.0)
            if room_ind <= 1e-12 or room_name <= 1e-12:
                continue
            if inst not in w and len(w) >= max_names:
                continue
            add = min(room_ind, room_name, freed)
            if add <= 1e-12:
                continue
            w[inst] = w.get(inst, 0.0) + add
            freed -= add
        # unplaced freed stays out → ballast absorbs
    return {i: float(v) for i, v in w.items() if v > 1e-12}


def assert_ind_caps(
    stock_df,
    sw,
    *,
    ind_cap_book: float = 0.25,
    ind_cap_sleeve: float = 0.25,
    max_names: int = 20,
    name_w: float = 0.04,
    industry_on_date=None,
    eps: float = 1e-6,
) -> tuple[float, float]:
    """Fail hard if any day breaches book or budget-sleeve industry cap. Returns (max_book, max_sleeve_budget)."""
    fn = industry_on_date or (_FU.industry_on_date if _FU is not None else None)
    if fn is None:
        raise RuntimeError("industry_on_date required")
    sleeve_budget = max_names * name_w
    book_cap_sleeve = ind_cap_sleeve * sleeve_budget
    max_book = 0.0
    for d, g in stock_df.groupby("date"):
        ind_of = fn(g["instrument"].tolist(), d, sw)
        buckets: dict[str, float] = {}
        for inst, tw in zip(g["instrument"], g["target_weight"]):
            code = ind_of.get(inst) or "_UNK"
            buckets[code] = buckets.get(code, 0.0) + float(tw)
        if not buckets:
            continue
        mb = max(buckets.values())
        max_book = max(max_book, mb)
        if mb > ind_cap_book + eps:
            raise AssertionError(f"book industry cap breached @ {d}: {mb} > {ind_cap_book}")
        if mb > book_cap_sleeve + eps:
            raise AssertionError(
                f"sleeve-budget industry cap breached @ {d}: {mb} > {book_cap_sleeve} "
                f"(sleeve≤{ind_cap_sleeve} of {sleeve_budget})"
            )
    return max_book, max_book / sleeve_budget if sleeve_budget else 0.0
