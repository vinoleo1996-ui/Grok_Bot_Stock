"""Process-level cache for ``load_merged_panel`` (Full D1 paper speed).

Research-only. Does not change merge semantics — only avoids re-reading the
same instrument parquet repeatedly.

Memory: unbounded cache of full OHLCV frames is a common OOM cause on ~15Gi
boxes. Use ``max_items`` (LRU) — recommended 200–500 for Full D1.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable

_CACHE: "OrderedDict[tuple, Any]" = OrderedDict()
_INSTALLED = False
_ORIG: Callable[..., Any] | None = None
_MAX_ITEMS: int | None = None


def install_merged_panel_cache(*, max_items: int | None = 400) -> None:
    """Wrap ``quantlab.data.v2_readers.load_merged_panel`` with an LRU cache.

    Parameters
    ----------
    max_items:
        Max cached panels. ``None`` = unbounded (legacy; avoid on Full D1).
        Default 400. Re-installing updates the cap.
    """
    global _INSTALLED, _ORIG, _MAX_ITEMS
    _MAX_ITEMS = None if max_items is None else max(1, int(max_items))

    if _INSTALLED:
        # Already wrapped — just tighten/clear to new cap.
        _enforce_max()
        return

    import quantlab.data.v2_readers as readers

    _ORIG = readers.load_merged_panel

    def _cached(instrument_id, *args, **kwargs):
        d0 = kwargs.get("d0_root")
        ext = kwargs.get("asof_extend_dir")
        cut = kwargs.get("d0_asof_cutoff")
        key = (
            str(instrument_id),
            str(d0) if d0 is not None else "",
            str(ext) if ext is not None else "",
            str(cut) if cut is not None else "",
        )
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key]
        view = _ORIG(instrument_id, *args, **kwargs)
        _CACHE[key] = view
        _CACHE.move_to_end(key)
        _enforce_max()
        return view

    readers.load_merged_panel = _cached  # type: ignore[assignment]
    _INSTALLED = True


def _enforce_max() -> None:
    if _MAX_ITEMS is None:
        return
    while len(_CACHE) > _MAX_ITEMS:
        _CACHE.popitem(last=False)


def cache_stats() -> dict[str, int | None]:
    return {
        "n_cached_panels": len(_CACHE),
        "installed": int(_INSTALLED),
        "max_items": _MAX_ITEMS,
    }


def clear_merged_panel_cache() -> None:
    _CACHE.clear()


def set_cache_max_items(max_items: int | None) -> None:
    """Update LRU cap on an already-installed cache (or set for next install)."""
    global _MAX_ITEMS
    _MAX_ITEMS = None if max_items is None else max(1, int(max_items))
    _enforce_max()
