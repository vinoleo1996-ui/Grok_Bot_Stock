# a18_s53_year_sorted_content_col_hashes_helper.py
# Side draft ONLY (audit pack). NOT applied to production daily_basic_incremental.py.
# Isomorphic with ref_build_year monthly accumulation (Arch judge 6466c490).
from __future__ import annotations

import hashlib
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

import pandas as pd
import pyarrow as pa


def year_sorted_content_col_hashes_from_sorted_df(
    df: pd.DataFrame,
    out_cols: Sequence[str],
    physical_hash_fn: Callable[[Any], Dict[str, str]],
) -> Tuple[Dict[str, str], Optional[str], int]:
    """Compute year_sorted_content_col_hashes isomorphic with ref_build_year.

    Precondition: ``df`` is the year table after
    ``drop_duplicates(["ts_code","trade_date"], keep="last")`` and
    ``sort_values(["trade_date","ts_code"])``.

    Algorithm (must stay lock-step with ``ref_build_year``):
      - groupby calendar month of trade_date (int 1..12), ascending
      - per month: drop_duplicates keep=last + sort trade_date,ts_code
      - outer header fed once on first non-empty month:
            name + \\0 + arrow_type + \\0  (dtype from that month's from_pandas table)
      - each month: accumulate bytes.fromhex(_row_group_physical_col_hashes(month_tbl)[c])
      - stub: "ts_code,trade_date\\n" then each row "{ts},{td[:10]}\\n" in month order

    Returns: (ysch_dict, stub_hex_or_None, rows)
    """
    if df is None or len(df) == 0:
        return {}, None, 0
    td = pd.to_datetime(df["trade_date"])
    months = td.dt.month.astype(int)
    h_keys = hashlib.sha256()
    h_keys.update(b"ts_code,trade_date\n")
    col_hashes: Dict[str, Any] = {}
    headers_fed = False
    total = 0
    for m in sorted(months.unique()):
        chunk = df.loc[months == m].copy()
        chunk = chunk.drop_duplicates(["ts_code", "trade_date"], keep="last")
        chunk = chunk.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
        for ts, tdv in zip(chunk["ts_code"].astype(str), chunk["trade_date"].astype(str)):
            h_keys.update(f"{ts},{str(tdv)[:10]}\n".encode())
        tbl = pa.Table.from_pandas(chunk, preserve_index=False)
        if not headers_fed:
            for c in out_cols:
                if c in tbl.column_names:
                    col_hashes[c] = hashlib.sha256()
                    col_hashes[c].update(c.encode("utf-8"))
                    col_hashes[c].update(b"\0")
                    col_hashes[c].update(str(tbl.column(c).type).encode("utf-8"))
                    col_hashes[c].update(b"\0")
            headers_fed = True
        ph = physical_hash_fn(tbl)
        for c, dig in ph.items():
            if c not in col_hashes:
                col_hashes[c] = hashlib.sha256()
                col_hashes[c].update(c.encode())
            col_hashes[c].update(bytes.fromhex(dig))
        total += int(len(chunk))
        del chunk, tbl, ph
        try:
            pa.default_memory_pool().release_unused()
        except Exception:
            pass
    ysch = {c: h.hexdigest() for c, h in col_hashes.items()}
    return ysch, h_keys.hexdigest(), total
