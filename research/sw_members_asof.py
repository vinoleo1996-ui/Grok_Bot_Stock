"""SW L1 membership as-of (point-in-time) lookup — fixes static "last known l1_name" look-ahead
(Arch 10-18 P2; r2 per Arch 3f195231).

口径对齐 Intel sw_members_asof (a5b0b633/0e968759)，两边落地后合并为公共函数。
Rule for trading day d: in_date < d AND (out_date is null OR out_date >= d).
  - in_date is published 18:00 Asia/Shanghai -> usable from the NEXT trading day (in_date == d excluded).
  - out_date known only after the close -> still a member on out_date (out_date == d included).
Parsing (Arch P2-1): raw non-null out_date that fails to parse -> SwPitIntegrityError (never silently "still member");
raw non-null in_date that fails to parse -> NaT -> never matches, counted in stats.
Overlap (Arch: adopt "latest in_date"): keep the matching row with latest in_date; equal in_date -> prefer
is_new == "Y" or out_date null (P3-3), then later file row. NOTE Intel's intel_common uses keep="last" (file order)
and its event_study/c1 use keep="first"; on the real table these differ for 4 codes (Arch P3-5, transferred to Intel).
Reclassification-day gap (Arch P3-2) — 主 Agent ruling 2026-10-18 ~05:45 ET (binding) + 06:01 ET (d-1 = previous SSE
trading day; Arch c72f0856 P3-1) + C r2 2026-10-18 06:16 ET instruction (window relaxed; overrides Arch c6f97571 §10-1):
keep in_date < d; ONE exception: on SSE open day d, if a code has NO active row and has an old row with parsed in_date,
in_date <= out_date (Arch c6f97571 P3-7) and prev_open(d) <= out_date < d (prev_open(d) = latest is_open=1 cal_date
< d in the passed SSE calendar), carry that old row's l1_name for day d only. Because d is required to be an open
day, the next session d' has prev_open(d') = d > out_date, so at most 1 trading day is carried. Examples: Fri out /
Mon in -> Mon carried; out on Sun (non-open day) -> next open day carried; out on the last day before a weekday
holiday -> first day after the holiday carried. Rows with unparsed in_date are never carried (Arch c72f0856 P3-2a).
The carry does NOT require a successor row (Arch c72f0856 P3-2b): a code that left SW with no later row is also
carried for that one day; disclosed as stats["n_rows_gap_carry_no_successor"]. Carried rows whose out_date is a
non-open day (out_date > prev_open(d); the ones the literal "out_date == prev_open" rule of DIFF C would not carry)
are disclosed as stats["n_rows_gap_carry_out_on_closed_day"] (real table inside the calendar: 0, Arch c6f97571 §4).
Every other no-active-row case -> unknown industry (None / _UNK_).
Calendar: MUST be passed in as TradeCal (no module default; gap_carry without cal -> SwPitIntegrityError).
load_trade_cal(root) reads data/v2/calendar/trade_cal_sse_pit.parquet with sha pinned TRADE_CAL_SHA_PIN. With gap
carry, every session d must be non-NaT, inside the calendar (start..end, now 20261231), an open day, and have an
open day before it; otherwise SwPitIntegrityError (never falls back to calendar days). Use
sw_l1_asof_with_gap_carry() (shared public function, no hx2 dependency; Intel to call it after landing).
Table-level count (calendar-day definition, unchanged): stats["n_reclass_gap_rows"].
Overlap (主 Agent 2026-10-18 06:49 ET, C r3): every entry point that picks ONE row per (code, d) — l1_asof,
sw_l1_asof_with_gap_carry, IndustryAsOf (by_session / reclass_share) — takes keyword-only on_overlap:
  "raise" (default): any (code, d) with > 1 active row -> SwPitIntegrityError naming the first codes;
  "count": keep the fixed order OVERLAP_TIEBREAK and disclose stats["overlap_codes"] (code, n_days, first/last day,
  candidate l1_names, chosen l1_names, conflict) + stats["overlap_tiebreak"]. Any other value -> ValueError.
Session parsing (Arch 28eabd35 P3-r2-1): null / NaT / unparseable session -> SwPitIntegrityError on BOTH the pure
rule and the gap-carry path (never silently "unknown industry").
Default table (C r3b, Arch 2026-10-18 ~07:00 ET): SW_L1_REL = CLEAN
data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet (sha 89d4afa3, the table leaf 23/24 pin); the old sw_pit
table stays reachable as SW_L1_LEGACY_REL (pitfix before arm).
CLEAN layout (instrument_id "sz.000001" / sw_name) is adapted to ts_code "000001.SZ" / l1_name in load_sw_l1 after a
column/dtype check (SW_L1_CLEAN_COLUMNS, confirmed by Data §14②) and the Data r2 norm_code whitelist (known non-A ids
excluded + disclosed, any other id raises; attrs["layout"]). Freshness:
sw_l1_table_check() runs research.sw_pit_freshness for the legacy sw_pit layout and a CLEAN manifest check
(data/v2/sw_l1_pit/manifest.json "tushare_candidate") for CLEAN; any other table -> disclosed as unchecked.
r3c (Arch 016ae55e P3s, Arch 2026-10-18 11:11 ET rulings ①-④, Data §14② 0a5a5197):
  - gap carry with > 1 candidate on (code, d): on_overlap="raise" -> SwPitIntegrityError; "count" -> same fixed
    OVERLAP_TIEBREAK, disclosed as stats["gap_carry_multi_candidate_codes"] (P3-1);
  - exact duplicate rows are dropped in prep_sw (one copy kept) and counted, n_rows_exact_duplicate_dropped (P3-2);
    same code + same in_date + different l1_name = conflict (raise / overlap_codes; table count, Arch 11:11 ET ②);
  - rows with in_date > out_date are counted, n_rows_in_after_out (never active, kept) (P3-3);
  - l1_asof refuses > max_keys keys (parameter, default MAX_KEYS_PER_CALL): callers split by whole session (rule is
    per (code, d), so chunks are exactly
    equivalent; row counts add up, code lists re-merge by code) — sw_l1_asof_chunked() does this (P3-6);
  - check_allow_ok(): key=value .ok parser for allow_* switches (pitfix) (P3-4);
  - CLEAN manifest lag (P3-5; Arch 11:11 ET ①): stale only if lag_tdays > CLEAN_STALE_LAG_TDAYS (10) or coverage_gap;
    lag <= 10 -> lag_notes only; lag > 10 alone -> stale + stale_lag_only (Arch 11:13 / 11:20); legacy keeps 3.
  - r3d (Arch 11:29 ET ②): CLEAN manifest check also compares n_l1 (nunique sw_code) and available_at_nulls.
  - Arch 11:20 ET: Tsh.00018 excluded only on an exact (stripped) match and never normalised to an A share (①); dates
    and keys cast explicitly to TS_UNIT = datetime64[us] on both sides before any comparison (③; no merge_asof).
r3e (Arch 2026-10-18 12:09 ET; r3d selftest 8 failed / 75 passed, pandas 3.0.6 returned nan for missing):
  - missing l1_name / ts_code is returned as a real None: every public Series exit (_norm_a_share, l1_asof,
    sw_l1_asof_with_gap_carry, sw_l1_asof_chunked, IndustryAsOf via those, CLEAN adapter ts_code / l1_name) goes
    through _none_for_missing (astype(object) then where(notna, None)); non-missing values are unchanged. Root
    cause: pandas 3 infer_string makes pd.Series(<object ndarray of str/None>) a "str" Series (missing = nan), and
    pd.Series(None, index=..., dtype=object) is filled with nan, not None;
  - P2-2: sw_l1_table_check parses as_of to pd.Timestamp (TS_UNIT) before comparing (no string compare);
    '20261009' and '2026-10-09' give the same result; unparseable as_of -> SwPitIntegrityError.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import io
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from research.sw_pit_freshness import SwPitIntegrityError  # (STALE_LAG_TDAYS = 3 stays inside sw_pit_freshness)
from research.sw_pit_freshness import ensure_checked as _sw_pit_ensure_checked

SW_L1_REL = "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"  # C r3b: default = CLEAN (sha 89d4afa3)
SW_L1_LEGACY_REL = "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"  # old sw_pit table (0b1d3432); pitfix only
SW_L1_CLEAN_MANIFEST_REL = "data/v2/sw_l1_pit/manifest.json"
CLEAN_STALE_LAG_TDAYS = 10  # Arch 11:11 ET ①: CLEAN table stale only if lag_tdays > 10 (legacy sw_pit keeps 3)
TRADE_CAL_REL = "data/v2/calendar/trade_cal_sse_pit.parquet"
TRADE_CAL_SHA_PIN = "fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41"
ON_OVERLAP_CHOICES = ("raise", "count")
OVERLAP_TIEBREAK = ("latest in_date -> is_new == 'Y' -> out_date null -> later file row "
                    "(sort by in_date, _pri, _ord ascending; keep last)")
MAX_KEYS_PER_CALL = 1_000_000  # r3c P3-6 / Arch 11:11 ④: DEFAULT of the max_keys parameter (whole-session chunks)
TS_UNIT = "datetime64[us]"  # r3c (Arch 11:20 ET ③): CLEAN dates are [us]; all dates / keys cast to this first


def _none_for_missing(s: pd.Series) -> pd.Series:
    """r3e (Arch 2026-10-18 12:09 ET): single exit normalisation for returned l1_name / ts_code Series: object dtype,
    every missing value (nan / NA / None) is the Python None; non-missing values, index and name are unchanged."""
    s = s.astype(object)
    return s.where(s.notna(), None)


def _check_on_overlap(on_overlap) -> str:
    if not isinstance(on_overlap, str) or on_overlap not in ON_OVERLAP_CHOICES:
        raise ValueError(f"on_overlap must be one of {ON_OVERLAP_CHOICES}, got {on_overlap!r}")
    return on_overlap


class TradeCal:
    """SSE trading calendar (cal_date YYYYMMDD str, is_open 0/1). Validates: non-empty, all cal_date parse, unique,
    contiguous daily coverage start..end, is_open in {0, 1}. Any violation -> SwPitIntegrityError."""

    def __init__(self, cal: pd.DataFrame, sha256: str | None = None):
        if cal is None or len(cal) == 0 or not {"cal_date", "is_open"} <= set(cal.columns):
            raise SwPitIntegrityError("trade calendar empty or missing cal_date/is_open")
        d = pd.to_datetime(cal["cal_date"].astype(str), format="%Y%m%d", errors="coerce")
        if d.isna().any():
            raise SwPitIntegrityError(f"trade calendar: {int(d.isna().sum())} cal_date values not YYYYMMDD")
        if not d.is_unique:
            raise SwPitIntegrityError("trade calendar: duplicate cal_date")
        iso = pd.to_numeric(cal["is_open"], errors="coerce")
        if not iso.isin([0, 1]).all():
            raise SwPitIntegrityError("trade calendar: is_open must be 0/1")
        order = np.argsort(d.to_numpy())
        dd, oo = d.to_numpy()[order], iso.to_numpy()[order].astype(int)
        self.start, self.end = pd.Timestamp(dd[0]), pd.Timestamp(dd[-1])
        if len(dd) != (self.end - self.start).days + 1:
            raise SwPitIntegrityError(f"trade calendar not contiguous {self.start.date()}..{self.end.date()}")
        self.open_days = dd[oo == 1].astype(TS_UNIT)  # r3c (Arch 11:20 ③): explicit [us]
        if len(self.open_days) == 0:
            raise SwPitIntegrityError("trade calendar has no open day")
        self.sha256 = sha256

    def prev_open(self, d, require_open: bool = True) -> np.ndarray:
        """Latest open cal_date strictly before each d (datetime64 array; [us] under pandas 3, same unit as the parsed
        cal_date). Raises SwPitIntegrityError, checked in this order, if any d is NaT (Arch c6f97571 P3-3), before the
        calendar start or after its end, not an open day when require_open (Arch c6f97571 P3-2), or has no open day
        before it. No calendar-day fallback."""
        x = pd.to_datetime(pd.Series(np.asarray(d).ravel())).dt.normalize().astype(TS_UNIT).to_numpy()
        if len(x) == 0:
            return x
        if pd.isna(x).any():
            raise SwPitIntegrityError(f"session is NaT/unparseable ({int(pd.isna(x).sum())} rows); refusing gap carry")
        lo, hi = pd.Timestamp(x.min()), pd.Timestamp(x.max())
        if lo < self.start or hi > self.end:
            raise SwPitIntegrityError(f"session outside trade calendar {self.start.date()}..{self.end.date()}: "
                                      f"min={lo.date()} max={hi.date()}; extend trade_cal_sse_pit")
        j = np.searchsorted(self.open_days, x, side="left")
        if require_open:
            hit = self.open_days[np.minimum(j, len(self.open_days) - 1)] == x
            if not hit.all():
                raise SwPitIntegrityError(f"session not an SSE open day ({int((~hit).sum())} rows, first "
                                          f"{pd.Timestamp(x[~hit].min()).date()})")
        i = j - 1
        if (i < 0).any():
            raise SwPitIntegrityError(f"trade calendar has no open day before {pd.Timestamp(x[i < 0].min()).date()}")
        return self.open_days[i]


def _check_max_keys(max_keys) -> int:
    """r3c (Arch 11:11 ET ④): per-call key limit is a parameter (default MAX_KEYS_PER_CALL); int >= 1, bool rejected."""
    if isinstance(max_keys, bool) or not isinstance(max_keys, (int, np.integer)) or int(max_keys) < 1:
        raise ValueError(f"max_keys must be an int >= 1, got {max_keys!r}")
    return int(max_keys)


def load_trade_cal(root: Path, sha_pin: str | None = TRADE_CAL_SHA_PIN) -> TradeCal:
    """Single read of ROOT/data/v2/calendar/trade_cal_sse_pit.parquet; sha256 of those bytes must equal sha_pin
    (None = record only; production callers must not pass None). root is required (no module default)."""
    raw = (Path(root) / TRADE_CAL_REL).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha_pin is not None and sha != sha_pin:
        raise SwPitIntegrityError(f"trade_cal_sse_pit sha mismatch: actual={sha} pinned={sha_pin}")
    return TradeCal(pd.read_parquet(io.BytesIO(raw), columns=["cal_date", "is_open"]), sha256=sha)


def prep_sw(sw: pd.DataFrame) -> pd.DataFrame:
    """Parse dates with explicit failure accounting; stats in .attrs["prep_stats"].
    r3c (Arch 016ae55e P3-2; Arch 11:11 ET ②): rows identical in ts_code / l1_name / parsed in_date / parsed out_date /
    is_new are exact duplicates: ONE copy is kept (contents are identical), the others are dropped and counted
    (n_rows_exact_duplicate_dropped), so they no longer trip on_overlap="raise". Rows that are NOT identical still
    overlap: in particular same ts_code + same in_date with different l1_name is a CONFLICT — on any d where both are
    active, on_overlap="raise" raises and "count" lists the code in overlap_codes (conflict=True); a gap-carry tie of
    such rows raises / is listed in gap_carry_multi_candidate_codes. Table-level disclosure (all rows, not only the
    queried days): n_codes_same_in_date_conflict + same_in_date_conflict_codes.
    r3c (P3-3): rows with parsed in_date > out_date can never be active; counted as n_rows_in_after_out (kept)."""
    sw = sw.copy()
    raw_in, raw_out = sw["in_date"], sw["out_date"]
    nonnull_in = raw_in.notna() & (raw_in.astype(str).str.strip() != "")
    nonnull_out = raw_out.notna() & (raw_out.astype(str).str.strip() != "")
    sw["in_date"] = pd.to_datetime(raw_in, errors="coerce").dt.normalize().astype(TS_UNIT)
    sw["out_date"] = pd.to_datetime(raw_out, errors="coerce").dt.normalize().astype(TS_UNIT)
    n_out_unparsed = int((nonnull_out & sw["out_date"].isna()).sum())
    n_in_unparsed = int((nonnull_in & sw["in_date"].isna()).sum())
    if n_out_unparsed > 0:
        raise SwPitIntegrityError(f"sw_pit out_date: {n_out_unparsed} non-null values failed to parse "
                                  "(would read as 'still member')")
    n_raw = int(len(sw))
    isnew = sw["is_new"].astype(str).str.upper().eq("Y") if "is_new" in sw.columns else pd.Series(False, index=sw.index)
    sw["_pri"] = 2 * isnew.astype(int) + sw["out_date"].isna().astype(int)  # tie order: is_new=Y, then out null
    sw["_ord"] = np.arange(len(sw))  # file order of the RAW table
    dup_cols = [c for c in ("ts_code", "l1_name", "in_date", "out_date", "is_new") if c in sw.columns]
    dup = sw.duplicated(subset=dup_cols)  # identical contents -> same values; a tie with any OTHER row is a conflict
    n_dup = int(dup.sum())
    sw = sw[~dup].copy()
    n_in_after_out = int((sw["in_date"].notna() & sw["out_date"].notna() & (sw["in_date"] > sw["out_date"])).sum())
    sid = sw[sw["in_date"].notna()].groupby(["ts_code", "in_date"])["l1_name"].nunique()
    sid_codes = sorted({str(c) for c, _ in sid[sid > 1].index})  # same code + in_date, different l1_name
    s = sw.sort_values(["ts_code", "in_date", "_ord"])
    prev_out = s.groupby("ts_code")["out_date"].shift(1)
    gap = int((s["in_date"].notna() & prev_out.notna() & (s["in_date"] == prev_out + pd.Timedelta(days=1))).sum())
    sw.attrs["prep_stats"] = {"n_rows": n_raw, "n_in_unparsed": n_in_unparsed, "n_out_unparsed": 0,
                              "n_out_null": int((~nonnull_out).sum()), "n_reclass_gap_rows": gap,
                              "n_rows_exact_duplicate_dropped": n_dup, "n_rows_in_after_out": n_in_after_out,
                              "n_codes_same_in_date_conflict": len(sid_codes), "same_in_date_conflict_codes": sid_codes,
                              "has_is_new": "is_new" in sw.columns}
    return sw


# C r3b (Arch 07:16 ET item 1): expected CLEAN columns / dtypes (pandas 3 dtype names); any difference ->
# SwPitIntegrityError. r3c: CONFIRMED unchanged by Data §14② (docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt,
# sha256 0a5a51976b516212e492bdbab56f2907063f2769759515587da6b12b63577d2b, lines 13-27: 11 columns, pandas 3.0.6).
SW_L1_CLEAN_COLUMNS = (("instrument_id", "str"), ("sw_code", "str"), ("sw_name", "str"),
                       ("in_date", "datetime64[us]"), ("out_date", "datetime64[us]"),
                       ("available_at", "datetime64[us]"),
                       ("source", "str"), ("revision", "int64"), ("quality_status", "str"), ("schema", "str"),
                       ("is_new", "str"))
# C r3b (Arch 07:16 ET item 2): code whitelist copied from Data r2 norm_code
# (docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r2.md sha256 482d8a2b..., lines 329-330 A_DOT / A_PFX, re.I, after
# strip; lines 362-375 norm_code). Known ids are excluded and disclosed as non_a_share_excluded; any other id outside
# the whitelist (incl. null) -> raise.
A_DOT = r"(\d{6})\.(SH|SZ|BJ)"
A_PFX = r"(SH|SZ|BJ)\.(\d{6})"
# r3c: the ONLY non-whitelisted id in CLEAN 89d4afa3, exact spelling (case-sensitive, after strip), 1 row — Data §14②
# docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt (sha256 0a5a5197...77d2b) lines 31-32 (the non-A-share id
# Data r2 lines 62 / 1016 / 1022 call "T00018"). Other 7919 rows are A_PFX (line 38).
NON_A_SHARE_KNOWN = ("Tsh.00018",)


def _norm_a_share(codes: pd.Series) -> pd.Series:
    """Vectorized Data r2 norm_code -> ts_code "600000.SH"; None where the id is outside the whitelist."""
    s = codes.astype("string").str.strip()
    dot = s.str.extract(A_DOT, flags=re.I)
    pfx = s.str.extract(A_PFX, flags=re.I)
    dot_ok = s.str.fullmatch(A_DOT, flags=re.I).fillna(False).astype(bool)
    pfx_ok = s.str.fullmatch(A_PFX, flags=re.I).fillna(False).astype(bool)
    out = pd.Series(np.full(len(codes), None, dtype=object), index=codes.index, dtype=object)  # r3e: not Series(None)
    out[dot_ok] = (dot[0] + "." + dot[1].str.upper())[dot_ok].astype(object)
    out[pfx_ok] = (pfx[1] + "." + pfx[0].str.upper())[pfx_ok].astype(object)
    return _none_for_missing(out)  # r3e: missing -> None


def normalize_sw_l1_layout(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """C r3b: accept both SW L1 layouts. sw_pit (ts_code / l1_name) is used as-is (preferred when both exist; no
    schema assertion — legacy table). CLEAN sw_l1_pit tushare (instrument_id / sw_name, no ts_code): columns and dtypes
    must equal SW_L1_CLEAN_COLUMNS, else SwPitIntegrityError; instrument_id -> ts_code via the Data r2 norm_code
    whitelist; ids in NON_A_SHARE_KNOWN are dropped and disclosed (non_a_share_excluded); any other non-whitelisted
    id -> SwPitIntegrityError. Raw row / code counts and in_date range (before exclusion) are kept for the manifest
    check. Anything else -> SwPitIntegrityError. in_date / out_date are required in both layouts."""
    cols = set(df.columns)
    if not {"in_date", "out_date"} <= cols:
        raise SwPitIntegrityError(f"SW L1 table has no in_date/out_date: columns {sorted(cols)}")
    if {"ts_code", "l1_name"} <= cols:
        return df, {"layout": "sw_pit (ts_code/l1_name)", "non_a_share_excluded": [], "n_rows_non_a_share_excluded": 0}
    if {"instrument_id", "sw_name"} <= cols:
        got = tuple((c, str(df[c].dtype)) for c in df.columns)
        if sorted(got) != sorted(SW_L1_CLEAN_COLUMNS):
            raise SwPitIntegrityError(f"CLEAN SW L1 schema != expected (Data §14②): got {list(got)}, "
                                      f"expected {list(SW_L1_CLEAN_COLUMNS)}")
        iid = df["instrument_id"]
        ts = _norm_a_share(iid)
        bad = ts.isna()
        known = bad & iid.astype("string").str.strip().isin(NON_A_SHARE_KNOWN).fillna(False).astype(bool)
        unknown = bad & ~known
        if unknown.any():
            ex = sorted(str(x) for x in iid[unknown].unique())[:10]
            raise SwPitIntegrityError(f"CLEAN SW L1: {int(unknown.sum())} rows with instrument_id outside the Data r2 "
                                      f"norm_code whitelist and not in NON_A_SHARE_KNOWN: {ex}")
        ind = pd.to_datetime(df["in_date"], errors="coerce")
        info = {"layout": "sw_l1_pit tushare (instrument_id/sw_name -> ts_code/l1_name)",
                "non_a_share_excluded": sorted(str(x) for x in iid[known].unique()),
                "n_rows_non_a_share_excluded": int(known.sum()),
                "raw": {"rows": int(len(df)), "n_instruments": int(iid.nunique()),
                        "in_date_min": str(ind.min().date()), "in_date_max": str(ind.max().date()),
                        # r3d (Arch 11:29 ET ②), Data §14② L42-49 algorithm, raw table BEFORE the non-A exclusion:
                        # n_l1 = nunique(sw_code); available_at_nulls = available_at null count
                        "n_l1": int(df["sw_code"].nunique()),
                        "available_at_nulls": int(df["available_at"].isna().sum())}}
        keep = ~known
        return df[keep].assign(ts_code=_none_for_missing(ts[keep]),
                               l1_name=_none_for_missing(df.loc[keep, "sw_name"])), info  # r3e: missing -> None
    raise SwPitIntegrityError(f"SW L1 table layout not recognised (need ts_code/l1_name or instrument_id/sw_name): "
                              f"columns {sorted(cols)}")


def load_sw_l1(root: Path, path: Path | str | None = None) -> pd.DataFrame:
    """Single read of the file bytes: sha256 recorded from the same bytes that are parsed (no TOCTOU).
    path: explicit table file (absolute, or relative to root); None -> root / SW_L1_REL (C r3b: CLEAN).
    attrs: sha256 (of the bytes actually read), path (resolved file actually read), layout (normalize_sw_l1_layout)."""
    fp = Path(root) / SW_L1_REL if path is None else Path(path)
    if not fp.is_absolute():
        fp = Path(root) / fp
    raw = fp.read_bytes()
    df = pd.read_parquet(io.BytesIO(raw))  # import surface: stdlib + numpy + pandas (+ sw_pit_freshness)
    df, layout = normalize_sw_l1_layout(df)
    cols = ["ts_code", "l1_name", "in_date", "out_date"] + (["is_new"] if "is_new" in df.columns else [])
    sw = prep_sw(df[cols])
    sw.attrs["sha256"] = hashlib.sha256(raw).hexdigest()
    sw.attrs["path"] = str(fp.resolve())
    sw.attrs["layout"] = layout
    return sw


_ET = ZoneInfo("America/New_York")
_SH = ZoneInfo("Asia/Shanghai")
_TABLE_CHECKS: dict = {}


def _completed_open_day(ts_sh: _dt.datetime, cal: "TradeCal", what: str) -> pd.Timestamp:
    """Latest SSE session completed at ts_sh (same rule as sw_pit_freshness: open day and SH hour >= 18, else the
    last open day before). SH date beyond the calendar end -> SwPitIntegrityError."""
    d = pd.Timestamp(ts_sh.date())
    if d > cal.end:
        raise SwPitIntegrityError(f"trade calendar ends {cal.end.date()} < SH date of {what} {d.date()}")
    od = pd.DatetimeIndex(cal.open_days)
    if d in od and ts_sh.hour >= 18:
        return d
    prev = od[od < d]
    if len(prev) == 0:
        raise SwPitIntegrityError(f"calendar has no open day before {d.date()}")
    return prev[-1]


def _clean_manifest_check(root: Path, sw: pd.DataFrame, cal: "TradeCal", now_et: _dt.datetime) -> dict:
    """CLEAN integrity/coverage from data/v2/sw_l1_pit/manifest.json["tushare_candidate"] (top-level rows/n_instruments
    describe the legacy vote table, not CLEAN). The manifest has NO sha256 and NO "built": integrity = code sha pin
    + manifest metrics rows / n_instruments / in_date_min / in_date_max / n_l1 / available_at_nulls == raw table
    (before non-A exclusion; r3d adds n_l1 + available_at_nulls, Arch 11:29 ET ②; a missing key compares as None ->
    mismatch -> raises, same as the other keys; Data §14② lines 40-49 found manifest == table on all six, 7920 /
    5914 / 31 / 1984-05-09 / 2026-09-24 / 0 — the numbers come from the manifest, not from code); coverage = SSE
    session completed at manifest "fetch_time". Returns None if the manifest does not describe this file."""
    mpath = Path(root) / SW_L1_CLEAN_MANIFEST_REL
    try:
        man = json.loads(mpath.read_text(encoding="utf-8"))
    except Exception as e:
        raise SwPitIntegrityError(f"sw_l1_pit manifest unreadable: {mpath} ({type(e).__name__}: {e})")
    tc = man.get("tushare_candidate") or {}
    if not tc.get("path") or Path(tc["path"]).resolve() != Path(sw.attrs.get("path", "")).resolve():
        return None
    mt = tc.get("metrics") or {}
    raw = (sw.attrs.get("layout") or {}).get("raw")  # counts BEFORE non-A-share exclusion (C r3b)
    if raw is None:
        raise SwPitIntegrityError("CLEAN manifest check needs load_sw_l1(CLEAN) attrs['layout']['raw']")
    got = dict(raw)
    bad = {k: (mt.get(k), v) for k, v in got.items() if str(mt.get(k)) != str(v)}
    if bad:
        raise SwPitIntegrityError(f"sw_l1_pit manifest tushare_candidate.metrics != table: {bad}")
    ft = man.get("fetch_time")
    try:
        f = _dt.datetime.fromisoformat(str(ft))
    except (TypeError, ValueError) as e:
        raise SwPitIntegrityError(f"sw_l1_pit manifest fetch_time missing/unparseable: {ft!r} ({e})")
    f_et = f.replace(tzinfo=_ET) if f.tzinfo is None else f.astimezone(_ET)
    cov = _completed_open_day(f_et.astimezone(_SH), cal, "fetch_time")
    ref = _completed_open_day(now_et.astimezone(_SH), cal, "now")
    od = pd.DatetimeIndex(cal.open_days)
    return {"check": "sw_l1_pit manifest tushare_candidate (no sha256/built in manifest; sha = code pin)",
            "manifest": SW_L1_CLEAN_MANIFEST_REL, "fetch_time_et": f_et.isoformat(timespec="seconds"),
            "coverage_day": str(cov.date()), "ref_day": str(ref.date()),
            "lag_tdays": int(((od > cov) & (od <= ref)).sum()), "metrics": got,
            "promotion_approved": tc.get("promotion_approved")}


def sw_l1_table_check(root: Path, sw: pd.DataFrame, as_of, cal: "TradeCal", *, as_of_defaulted: bool = False,
                      now_et: _dt.datetime | None = None) -> dict:
    """C r3b freshness/integrity dispatch on the table actually read (sw = load_sw_l1 output):
    legacy sw_pit file -> research.sw_pit_freshness.ensure_checked (manifest data/v2/sw_pit; unchanged rules, stale at
    lag >= STALE_LAG_TDAYS = 3); CLEAN -> _clean_manifest_check (integrity raises) and (Arch 11:11 / 11:13 / 11:20 ET):
      lag_tdays <= CLEAN_STALE_LAG_TDAYS (10)  -> stale=False, stale_lag_only=False; days only in lag_notes;
      lag_tdays > 10, no coverage_gap          -> warn, stale=True, stale_lag_only=True (reason "lag");
      as_of > coverage_day                     -> warn, stale=True, stale_lag_only=False (reason "coverage_gap");
    any other file -> warn "no manifest check" (stale=True, reason "no_manifest"). Disclosure only; nothing blocks
    the run.
    Aggregated per path across calls (latest as_of, union of warns / lag_notes); read back with
    sw_l1_table_check_last(path)."""
    p = Path(sw.attrs.get("path", "")).resolve()
    # r3e P2-2 (Arch 2026-10-18 12:09 ET): parse as_of to a TS_UNIT Timestamp before any comparison (the r3d string
    # compare read '20261009' > '2026-10-16' -> false coverage_gap); a = ISO day string for the result / legacy check
    a_ts = None
    if as_of is not None:
        try:
            a_ts = pd.Timestamp(as_of)
        except (TypeError, ValueError) as e:
            raise SwPitIntegrityError(f"sw_l1_table_check: as_of unparseable: {as_of!r} ({e})")
        if pd.isna(a_ts):
            raise SwPitIntegrityError(f"sw_l1_table_check: as_of is NaT/empty: {as_of!r}")
        a_ts = a_ts.normalize().as_unit("us")  # TS_UNIT
    a = None if a_ts is None else a_ts.strftime("%Y-%m-%d")
    if p == (Path(root) / SW_L1_LEGACY_REL).resolve():
        r = dict(_sw_pit_ensure_checked(Path(root), as_of=a, as_of_defaulted=as_of_defaulted),
                 check="research.sw_pit_freshness (manifest data/v2/sw_pit)", path=str(p))
        r.setdefault("stale_lag_only", False)  # legacy keeps its own rule (lag >= 3 -> stale)
        _TABLE_CHECKS[str(p)] = r
        return r
    base = _clean_manifest_check(Path(root), sw, cal, now_et or _dt.datetime.now(_ET))
    warns: list = []
    notes: list = []
    if base is None:
        base = {"check": "none (no manifest describes this file)"}
        warns.append("no manifest check for this table (sha pin only)")
    else:
        lag = base["lag_tdays"]
        if lag > CLEAN_STALE_LAG_TDAYS:
            warns.append(f"lag_tdays={lag}>{CLEAN_STALE_LAG_TDAYS}")
        else:
            notes.append(f"lag_tdays={lag} (<= {CLEAN_STALE_LAG_TDAYS}: not stale)")
        if a_ts is not None and a_ts > pd.Timestamp(base["coverage_day"]).as_unit("us"):  # r3e P2-2: Timestamps
            warns.append(f"coverage_gap: as_of={a} > coverage_day={base['coverage_day']}")
        base = dict(base, stale_lag_tdays=CLEAN_STALE_LAG_TDAYS)
    if as_of_defaulted:
        warns.append("as_of 取默认值（调用方未传）")
    prev = _TABLE_CHECKS.get(str(p))
    r = dict(base, path=str(p), sha256=sw.attrs.get("sha256"), as_of=a, as_of_defaulted=as_of_defaulted,
             checked_at_et=(now_et or _dt.datetime.now(_ET)).isoformat(timespec="seconds"), warns=warns,
             lag_notes=notes, n_calls=1)
    if prev is not None:
        if prev.get("as_of") is not None and (a_ts is None or pd.Timestamp(prev["as_of"]).as_unit("us") > a_ts):
            r["as_of"], r["as_of_defaulted"] = prev["as_of"], prev["as_of_defaulted"]
        r["warns"] = list(dict.fromkeys(prev["warns"] + warns))
        r["lag_notes"] = list(dict.fromkeys(prev.get("lag_notes", []) + notes))
        r["n_calls"] = prev["n_calls"] + 1
    blocking = [w for w in r["warns"] if not w.startswith("as_of 取默认值")]
    r["stale"] = bool(blocking)
    reasons = []
    if any(w.startswith("lag_tdays=") for w in blocking):
        reasons.append("lag")
    if any(w.startswith("coverage_gap") for w in blocking):
        reasons.append("coverage_gap")
    if any(w.startswith("no manifest check") for w in blocking):
        reasons.append("no_manifest")
    r["stale_reasons"] = reasons
    # Arch 11:13 + 11:20 ET (merged reading, pending Arch confirmation): stale_lag_only = stale ONLY because of
    # lag > CLEAN_STALE_LAG_TDAYS (no coverage_gap / no_manifest). lag <= 10 -> stale False, stale_lag_only False.
    r["stale_lag_only"] = reasons == ["lag"]
    if r["stale_lag_only"]:
        r["disclosure_zh"] = (f"【披露】申万 L1 表（{r['check']}）抓取于 {r.get('fetch_time_et')}，覆盖至 "
                              f"{r.get('coverage_day')}，距今 {r.get('lag_tdays')} 个交易日，超过 CLEAN 阈值 "
                              f"{CLEAN_STALE_LAG_TDAYS}，记 stale（stale_lag_only=True：只有滞后）。"
                              + (f"本次查询截至 {r['as_of']}，未超出覆盖日，as-of 行业取值本身不受滞后影响。"
                                 if r.get("as_of") is not None else "未传 as_of，无法确认查询是否超出覆盖日。")
                              + "行业相关结果仅作带披露参考。")
    elif blocking:
        r["disclosure_zh"] = ("【披露】申万 L1 表检查：" + "；".join(r["warns"] + r["lag_notes"]) + f"（{r['check']}）。"
                              + ("查询日晚于表覆盖日，覆盖日之后的行业归属可能缺失或过时；" if "coverage_gap" in reasons else "")
                              + (f"表滞后超过 {CLEAN_STALE_LAG_TDAYS} 个交易日；" if "lag" in reasons else "")
                              + ("该表没有 manifest 校验，仅核 sha pin；" if "no_manifest" in reasons else "")
                              + ("未传 as_of，无法确认查询是否超出覆盖日；" if r.get("as_of") is None else "")
                              + "行业相关结果仅作带披露参考。")
    else:
        r["disclosure_zh"] = ""  # lag <= 10 only: days are disclosed in lag_notes
    _TABLE_CHECKS[str(p)] = r
    return r


def sw_l1_table_check_last(path=None) -> dict | None:
    """Latest aggregated sw_l1_table_check result for `path` (None -> the only / last checked table)."""
    if path is not None:
        return _TABLE_CHECKS.get(str(Path(path).resolve()))
    return list(_TABLE_CHECKS.values())[-1] if _TABLE_CHECKS else None


def _reset_table_checks_for_tests() -> None:
    _TABLE_CHECKS.clear()


def sw_members_asof(sw: pd.DataFrame, d) -> pd.DataFrame:
    """Row filter identical to Intel intel_common.sw_members_asof (expects datetime in_date/out_date)."""
    d = pd.Timestamp(d).normalize()
    return sw[(sw.in_date < d) & (sw.out_date.isna() | (sw.out_date >= d))]


def _overlap_list(mm: pd.DataFrame, picked: pd.DataFrame) -> list:
    """Per code with > 1 active row on some key day: n_days (distinct d), first/last day, sorted candidate l1_names,
    sorted chosen l1_names (after OVERLAP_TIEBREAK), conflict (> 1 distinct candidate name). Sorted by code."""
    if mm.empty:
        return []
    ch = picked[picked["_rid"].isin(mm["_rid"].unique())]
    out = []
    for code, g in mm.groupby("_code", sort=True):
        days = pd.DatetimeIndex(g["_d"].unique()).sort_values()
        cand = sorted(set(g["l1_name"].astype(str)))
        out.append({"code": str(code), "n_days": int(len(days)), "first_day": str(days[0].date()),
                    "last_day": str(days[-1].date()), "candidates": cand,
                    "chosen": sorted(set(ch.loc[ch["_code"] == code, "l1_name"].astype(str))),
                    "conflict": len(cand) > 1})
    return out


def l1_asof(sw: pd.DataFrame, keys: pd.DataFrame, code_col: str = "instrument",
            sess_col: str = "session", stats: dict | None = None, gap_carry: bool = False, *,
            cal: TradeCal | None = None, on_overlap: str = "raise",
            max_keys: int = MAX_KEYS_PER_CALL) -> pd.Series:
    """Vectorized as-of l1_name per (code, session) row of `keys`; index aligned to keys; None if no member.
    gap_carry=False: pure Intel-identical rule (calendar unused). gap_carry=True: 主 Agent 10-18 exception (see module
    doc); `cal` = TradeCal is REQUIRED (None -> SwPitIntegrityError); every session is checked by cal.prev_open.
    If `stats` is a dict, fills n_rows_multi_match / n_codes_overlap_on_d, n_rows_gap_carry,
    n_rows_gap_carry_no_successor, n_rows_gap_carry_out_on_closed_day, n_rows_gap_carry_multi_candidate,
    n_rows_unknown, gap_carry_rule, trade_cal_sha256, on_overlap, overlap_tiebreak, overlap_codes.
    on_overlap: "raise" (default) | "count" (see module doc). Null/NaT/unparseable session -> SwPitIntegrityError.
    r3c: gap-carry keys with > 1 candidate raise in "raise" mode, else n_codes_gap_carry_multi_candidate /
    gap_carry_multi_candidate_codes (same OVERLAP_TIEBREAK). len(keys) > max_keys -> SwPitIntegrityError:
    chunk by session (each (code, d) is independent, so per-chunk results concatenate exactly; row counts add up,
    code counts / *_codes lists are re-merged by code; "raise" mode is decided per chunk) — sw_l1_asof_chunked."""
    _check_on_overlap(on_overlap)
    max_keys = _check_max_keys(max_keys)
    if len(keys) > max_keys:  # r3c P3-6 (memory; Arch 016ae55e §7); limit is a parameter (Arch 11:11 ET ④)
        raise SwPitIntegrityError(f"l1_asof: {len(keys)} keys > max_keys={max_keys}; split the "
                                  "keys by session (sw_l1_asof_chunked; results are identical)")
    if gap_carry and cal is None:
        raise SwPitIntegrityError("gap_carry=True requires cal=TradeCal (no module default; use load_trade_cal(ROOT))")
    if "_ord" not in sw.columns:
        sw = prep_sw(sw)
    # r3c (Arch 11:20 ET ③): both sides of every date comparison are explicitly TS_UNIT ([us]); sw dates via prep_sw
    d_us = pd.to_datetime(keys[sess_col].astype(str).str[:10], errors="coerce").dt.normalize().astype(TS_UNIT).values
    k = pd.DataFrame({"_code": keys[code_col].astype(str).values,
                      # null/unparseable session -> NaT -> raise below, both paths (c6f97571 P3-3, 28eabd35 P3-r2-1)
                      "_d": d_us,
                      "_rid": np.arange(len(keys))})
    if k["_d"].isna().any():
        raise SwPitIntegrityError(f"session is NaT/unparseable ({int(k['_d'].isna().sum())} rows); "
                                  "refusing to map to unknown industry")
    s = sw[["ts_code", "l1_name", "in_date", "out_date", "_pri", "_ord"]].rename(columns={"ts_code": "_code"})
    s = s.assign(in_date=s["in_date"].astype(TS_UNIT), out_date=s["out_date"].astype(TS_UNIT))  # same unit as _d
    m = k.merge(s, on="_code", how="inner")
    m = m[(m["in_date"] < m["_d"]) & (m["out_date"].isna() | (m["out_date"] >= m["_d"]))]
    vc = m["_rid"].value_counts()
    mm = m[m["_rid"].isin(vc.index[vc > 1])]  # all active rows of (code, d) keys with > 1 active row
    if len(mm) and on_overlap == "raise":
        codes = sorted(str(c) for c in mm["_code"].unique())
        raise SwPitIntegrityError(f"SW L1 overlap: {len(codes)} codes / {int(mm['_rid'].nunique())} key rows have > 1 "
                                  f"active row (on_overlap='raise'); first codes: {codes[:10]}")
    if stats is not None:
        stats["n_rows_multi_match"] = int((vc > 1).sum())
        stats["n_codes_overlap_on_d"] = int(mm["_code"].nunique())
    m = m.sort_values(["_rid", "in_date", "_pri", "_ord"]).drop_duplicates("_rid", keep="last")
    if stats is not None:
        stats["on_overlap"] = on_overlap
        stats["overlap_tiebreak"] = OVERLAP_TIEBREAK
        stats["overlap_codes"] = _overlap_list(mm, m)
    out = np.full(len(keys), None, dtype=object)
    out[m["_rid"].to_numpy()] = m["l1_name"].to_numpy()
    n_carry = n_no_succ = n_closed = n_multi_cand = 0
    gap_multi: list = []
    if gap_carry:
        k["_prev"] = cal.prev_open(k["_d"].to_numpy())  # raises: NaT / outside calendar / not open / no prior open day
        miss = k[~k["_rid"].isin(m["_rid"])]
        if len(miss):
            g0 = miss.merge(s, on="_code", how="inner")
            # c72f0856 P3-2a: unparsed in_date never carried; c6f97571 P3-7: in_date <= out_date
            g0 = g0[g0["in_date"].notna() & g0["out_date"].notna() & (g0["in_date"] <= g0["out_date"])]
            g = g0[(g0["out_date"] >= g0["_prev"]) & (g0["out_date"] < g0["_d"])]  # C r2: prev_open(d) <= out < d
            gvc = g["_rid"].value_counts()
            gm = g[g["_rid"].isin(gvc.index[gvc > 1])]  # r3c P3-1: keys with > 1 gap-carry candidate
            n_multi_cand = int((gvc > 1).sum())
            if len(gm) and on_overlap == "raise":
                codes = sorted(str(c) for c in gm["_code"].unique())
                raise SwPitIntegrityError(f"SW L1 gap carry: {len(codes)} codes / {n_multi_cand} key rows have > 1 "
                                          f"carry candidate (on_overlap='raise'); first codes: {codes[:10]}")
            g = g.sort_values(["_rid", "in_date", "_pri", "_ord"]).drop_duplicates("_rid", keep="last")
            gap_multi = _overlap_list(gm, g)  # count mode: same fixed OVERLAP_TIEBREAK, disclosed per code
            out[g["_rid"].to_numpy()] = g["l1_name"].to_numpy()
            n_carry = int(len(g))
            n_closed = int((g["out_date"] > g["_prev"]).sum())  # carried although out_date is a non-open day
            if n_carry:  # P3-2b: successor = another row of the code with parsed in_date >= carried out_date
                sc = g[["_rid", "_code", "out_date", "_ord"]].merge(
                    s[["_code", "in_date", "_ord"]].rename(columns={"_ord": "_ord2"}), on="_code", how="left")
                has = sc[(sc["_ord2"] != sc["_ord"]) & sc["in_date"].notna() & (sc["in_date"] >= sc["out_date"])]
                n_no_succ = int(n_carry - has["_rid"].nunique())
    if stats is not None:
        stats["n_rows_gap_carry"] = n_carry
        if gap_carry:
            stats["n_rows_gap_carry_no_successor"] = n_no_succ
            stats["n_rows_gap_carry_out_on_closed_day"] = n_closed
            stats["n_rows_gap_carry_multi_candidate"] = n_multi_cand
            stats["n_codes_gap_carry_multi_candidate"] = len(gap_multi)
            stats["gap_carry_multi_candidate_codes"] = gap_multi  # r3c P3-1 (count mode only; raise mode raised)
            stats["gap_carry_rule"] = ("prev SSE open day <= out_date < d, d open, 1 day "
                                       "(主 Agent 2026-10-18 06:01 ET; window relaxed C r2 06:16 ET)")
            stats["trade_cal_sha256"] = cal.sha256
        stats["n_rows_unknown"] = int(pd.isna(out).sum())
    return _none_for_missing(pd.Series(out, index=keys.index, name="l1_name", dtype=object))  # r3e: missing -> None


def sw_l1_asof_with_gap_carry(sw: pd.DataFrame, keys: pd.DataFrame, code_col: str = "instrument",
                              sess_col: str = "session", stats: dict | None = None, *,
                              cal: TradeCal | None = None, on_overlap: str = "raise",
                              max_keys: int = MAX_KEYS_PER_CALL) -> pd.Series:
    """SHARED PUBLIC FUNCTION (Strategy + Intel). As-of SW L1 name per (code, session):
    active rows = in_date < d AND (out_date null OR out_date >= d); latest in_date wins (tie: is_new=Y / out null,
    then file order). If no active row and an old row with parsed in_date <= out_date has
    prev_open(d) <= out_date < d (prev_open = latest SSE open day before d, from `cal`; window relaxed C r2),
    carry its l1_name for d only — also when the code has no successor row (disclosed as
    n_rows_gap_carry_no_successor). 主 Agent rulings 2026-10-18 ~05:45 / 06:01 ET. Otherwise None (unknown).
    `cal`: TradeCal, REQUIRED (None -> SwPitIntegrityError). Session NaT / outside the calendar / not open -> raises.
    on_overlap: "raise" (default) | "count" (主 Agent 06:49 ET; see module doc).
    `sw` = prep_sw()/load_sw_l1() output (raises SwPitIntegrityError on unparseable non-null out_date)."""
    return l1_asof(sw, keys, code_col, sess_col, stats=stats, gap_carry=True, cal=cal, on_overlap=on_overlap,
                   max_keys=max_keys)


_CODE_LISTS = {"overlap_codes": "n_codes_overlap_on_d",
               "gap_carry_multi_candidate_codes": "n_codes_gap_carry_multi_candidate"}


def _merge_code_lists(lists: list) -> list:
    """Merge per-chunk _overlap_list outputs by code (chunks hold disjoint sessions, so n_days add up)."""
    by: dict = {}
    for lst in lists:
        for e in lst:
            c = by.get(e["code"])
            if c is None:
                by[e["code"]] = dict(e, candidates=list(e["candidates"]), chosen=list(e["chosen"]))
                continue
            c["n_days"] += e["n_days"]
            c["first_day"], c["last_day"] = min(c["first_day"], e["first_day"]), max(c["last_day"], e["last_day"])
            c["candidates"] = sorted(set(c["candidates"]) | set(e["candidates"]))
            c["chosen"] = sorted(set(c["chosen"]) | set(e["chosen"]))
            c["conflict"] = len(c["candidates"]) > 1
    return [by[k] for k in sorted(by)]


def sw_l1_asof_chunked(sw: pd.DataFrame, keys: pd.DataFrame, code_col: str = "instrument",
                       sess_col: str = "session", stats: dict | None = None, *,
                       cal: TradeCal | None = None, on_overlap: str = "raise",
                       max_keys: int = MAX_KEYS_PER_CALL) -> pd.Series:
    """r3c (Arch 016ae55e P3-6; Arch 11:11 ET ④): sw_l1_asof_with_gap_carry split into chunks of WHOLE sessions
    (a session is never split) of <= max_keys keys; max_keys is a parameter, default MAX_KEYS_PER_CALL = 1_000_000.
    Same values as one call (rule is per (code, d)); stats: n_* row counts summed, overlap_codes /
    gap_carry_multi_candidate_codes re-merged by code (their n_codes_* recomputed), other fields from the chunks
    (identical), plus n_chunks. A single session with > max_keys keys -> SwPitIntegrityError (no partial session).
    Sessions are grouped by the parsed day (same parsing as l1_asof); NaT/unparseable -> SwPitIntegrityError.
    "raise" mode raises on the first chunk that has an overlap / multi-candidate key."""
    lim = _check_max_keys(max_keys)
    sess = pd.to_datetime(keys[sess_col].astype(str).str[:10], errors="coerce").dt.normalize().astype(TS_UNIT)
    if sess.isna().any():
        raise SwPitIntegrityError(f"session is NaT/unparseable ({int(sess.isna().sum())} rows); "
                                  "refusing to map to unknown industry")
    sizes = sess.value_counts(sort=False).sort_index()
    if len(sizes) and int(sizes.max()) > lim:
        raise SwPitIntegrityError(f"sw_l1_asof_chunked: session {sizes.idxmax().date()} alone has {int(sizes.max())} "
                                  f"keys > max_keys={lim} (sessions are never split)")
    if len(keys) <= lim:
        r = sw_l1_asof_with_gap_carry(sw, keys, code_col, sess_col, stats=stats, cal=cal, on_overlap=on_overlap,
                                      max_keys=lim)
        if stats is not None:
            stats["n_chunks"] = 1
        return r
    if "_ord" not in sw.columns:
        sw = prep_sw(sw)
    groups: list = []
    cur: list = []
    n = 0
    for s_, c in sizes.items():
        if cur and n + int(c) > lim:
            groups.append(cur)
            cur, n = [], 0
        cur.append(s_)
        n += int(c)
    groups.append(cur)
    out = np.full(len(keys), None, dtype=object)
    sts: list = []
    for g in groups:
        mask = sess.isin(list(g)).to_numpy()
        st: dict = {}
        out[mask] = sw_l1_asof_with_gap_carry(sw, keys[mask], code_col, sess_col, stats=st, cal=cal,
                                              on_overlap=on_overlap, max_keys=lim).to_numpy()
        sts.append(st)
    if stats is not None:
        for st in sts:
            for k, v in st.items():
                if k in _CODE_LISTS or k in _CODE_LISTS.values():
                    continue
                if k.startswith("n_") and isinstance(v, int) and not isinstance(v, bool):
                    stats[k] = stats.get(k, 0) + v
                else:
                    stats.setdefault(k, v)
        for lk, nk in _CODE_LISTS.items():
            if any(lk in st for st in sts):
                stats[lk] = _merge_code_lists([st.get(lk, []) for st in sts])
                stats[nk] = len(stats[lk])
        stats["n_chunks"] = len(groups)
    return _none_for_missing(pd.Series(out, index=keys.index, name="l1_name", dtype=object))  # r3e: missing -> None


def l1_static_last(sw: pd.DataFrame) -> dict:
    """Static last membership (latest in_date, tie -> is_new/out null, then file order). Disclosure only.
    NOT the legacy hx2 map (that one is kept verbatim in hx2.load_industry_map, Arch P2-4)."""
    if "_ord" not in sw.columns:
        sw = prep_sw(sw)
    last = sw.sort_values(["in_date", "_pri", "_ord"]).groupby("ts_code").tail(1)
    return dict(zip(last["ts_code"], last["l1_name"]))


class IndustryAsOf:
    """Per-session industry map for hx2.build_topn / apply_ind_cap (which take a plain dict per session)."""

    def __init__(self, sw: pd.DataFrame, static_map: dict | None = None, cal: TradeCal | None = None, *,
                 on_overlap: str = "raise", max_keys: int = MAX_KEYS_PER_CALL):
        self.on_overlap = _check_on_overlap(on_overlap)
        self.max_keys = _check_max_keys(max_keys)  # r3c (Arch 11:11 ET ④): per-call key limit, whole-session chunks
        self.sw = sw if "_ord" in sw.columns else prep_sw(sw)
        self.static = static_map if static_map is not None else l1_static_last(self.sw)
        if cal is None:
            raise SwPitIntegrityError("IndustryAsOf requires cal=TradeCal "
                                      "(no module default; use load_trade_cal(ROOT))")
        self.cal = cal
        self.stats = dict(self.sw.attrs.get("prep_stats", {}))
        self.stats["trade_cal_sha256"] = self.cal.sha256
        self.sha256 = self.sw.attrs.get("sha256")
        self.path = self.sw.attrs.get("path")
        self.layout = self.sw.attrs.get("layout")

    def by_session(self, pairs: pd.DataFrame, code_col: str = "instrument",
                   sess_col: str = "session") -> dict:
        """{session: {code: l1_name}} for the given (code, session) pairs (unique-ified first)."""
        p = pairs[[code_col, sess_col]].drop_duplicates().reset_index(drop=True)
        st: dict = {}
        p = p.assign(l1_name=sw_l1_asof_chunked(self.sw, p, code_col, sess_col, stats=st, cal=self.cal,
                                                on_overlap=self.on_overlap, max_keys=self.max_keys).values)
        self.stats.update({f"by_session_{k}": v for k, v in st.items()})
        p = p.dropna(subset=["l1_name"])
        return {s: dict(zip(g[code_col], g["l1_name"])) for s, g in p.groupby(sess_col)}

    def reclass_share(self, rows: pd.DataFrame, code_col: str = "instrument", sess_col: str = "session",
                      weight_col: str | None = None) -> dict:
        """Disclosure only: share of (session, holding) rows whose as-of l1 != static l1 (self.static);
        unknown-industry (_UNK_) rows reported separately (Arch P3-1). Gap-carry disclosure includes
        n_rows_gap_carry_no_successor (carried although the code has no later row; Arch c72f0856 P3-2b) and
        n_rows_gap_carry_out_on_closed_day (carried with out_date on a non-open day; Arch 28eabd35 P3-r2-2).
        Overlap handling follows self.on_overlap; overlap_codes / overlap_tiebreak are passed through."""
        if rows.empty:
            return {"n_rows": 0, "share_rows_diff": None}
        st: dict = {}
        a = sw_l1_asof_chunked(self.sw, rows, code_col, sess_col, stats=st, cal=self.cal,
                               on_overlap=self.on_overlap, max_keys=self.max_keys)
        s = rows[code_col].astype(str).map(self.static)
        diff = (a.fillna("_UNK_") != s.fillna("_UNK_"))
        a_miss, s_miss = a.isna(), s.isna()
        out = {"n_rows": int(len(rows)), "n_rows_diff": int(diff.sum()), "share_rows_diff": float(diff.mean()),
               "n_rows_diff_both_known": int((diff & ~a_miss & ~s_miss).sum()),
               "n_rows_asof_missing": int(a_miss.sum()), "n_rows_static_missing": int(s_miss.sum()),
               "n_rows_asof_missing_static_known": int((a_miss & ~s_miss).sum()),
               "share_rows_asof_missing": float(a_miss.mean()), **st,
               "share_rows_gap_carry": float(st["n_rows_gap_carry"] / len(rows)),
               "n_reclass_gap_rows_table": self.stats.get("n_reclass_gap_rows"),
               "n_in_unparsed_table": self.stats.get("n_in_unparsed"),
               # r3c P3-2 / P3-3: table-level counts (prep_sw), disclosure only
               "n_rows_exact_duplicate_dropped_table": self.stats.get("n_rows_exact_duplicate_dropped"),
               "n_rows_in_after_out_table": self.stats.get("n_rows_in_after_out"),
               "n_codes_same_in_date_conflict_table": self.stats.get("n_codes_same_in_date_conflict")}
        if weight_col:
            w = rows[weight_col].astype(float)
            out["share_weight_diff"] = float(w[diff].sum() / w.sum()) if w.sum() > 0 else None
        return out


SW_PIT_REQUIRED_INT_FIELDS = ("n_unknown_rows", "n_overlap_codes")


def sw_pit_required(ia: "IndustryAsOf", rs: dict, unknown_key: str = "n_rows_asof_missing") -> dict:
    """主 Agent 06:49 ET item 3: mandatory per-arm sw_pit fields. rs = ia.reclass_share(...) on the arm's holdings.
    sw_pit_sha256 = sha of the bytes actually read (ia.sha256); n_unknown_rows = rs[unknown_key] (unknown-industry
    holding rows); n_overlap_codes = codes with > 1 active row on some holding day; plus list / tie order."""
    return {"sw_pit_sha256": ia.sha256, "sw_pit_path": ia.path, "sw_pit_layout": ia.layout, "unknown_key": unknown_key,
            "n_unknown_rows": rs.get(unknown_key), "n_overlap_codes": rs.get("n_codes_overlap_on_d"),
            "n_overlap_key_rows": rs.get("n_rows_multi_match"), "on_overlap": ia.on_overlap,
            "overlap_tiebreak": rs.get("overlap_tiebreak"), "overlap_codes": rs.get("overlap_codes"),
            # r3c (Arch 016ae55e P3-1/2/3): disclosed only, NOT in SW_PIT_REQUIRED_INT_FIELDS (mandatory set unchanged)
            "n_gap_carry_multi_candidate_codes": rs.get("n_codes_gap_carry_multi_candidate"),
            "gap_carry_multi_candidate_codes": rs.get("gap_carry_multi_candidate_codes"),
            "n_rows_exact_duplicate_dropped": ia.stats.get("n_rows_exact_duplicate_dropped"),
            "n_rows_in_after_out": ia.stats.get("n_rows_in_after_out"),
            "n_codes_same_in_date_conflict": ia.stats.get("n_codes_same_in_date_conflict"),
            "same_in_date_conflict_codes": ia.stats.get("same_in_date_conflict_codes")}


def sw_pit_required_ok(d) -> bool:
    """True only if sw_pit_sha256 is a 64-hex string and the int fields are present ints (bool rejected)."""
    if not isinstance(d, dict):
        return False
    sha = d.get("sw_pit_sha256")
    if not (isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha)):
        return False
    return all(isinstance(d.get(f), int) and not isinstance(d.get(f), bool) for f in SW_PIT_REQUIRED_INT_FIELDS)


def pitfix_out_dir_guard(root: Path, out_dir) -> Path:
    """Arch P2-2: out_dir must resolve strictly under ROOT/output/strategy_hiliq/, must not exist, and must not be
    (or sit under) b4 / capadv_x2 / legs or contain paper / frozen in any path part. Call before writing anything."""
    base = (Path(root) / "output/strategy_hiliq").resolve()
    p = Path(out_dir)
    p = (p if p.is_absolute() else Path(root) / p).resolve()
    try:
        rel = p.relative_to(base)
    except ValueError:
        raise SystemExit(f"pitfix out_dir must be under {base}: {p}")
    if not rel.parts:
        raise SystemExit("pitfix out_dir must be a NEW subdirectory, not output/strategy_hiliq itself")
    if rel.parts[0] in ("b4", "capadv_x2", "legs"):
        raise SystemExit(f"pitfix out_dir may not be inside {rel.parts[0]}/: {p}")
    if any(("paper" in x.lower()) or ("frozen" in x.lower()) for x in rel.parts):
        raise SystemExit(f"pitfix out_dir may not contain paper/frozen: {p}")
    if p.exists() or p.is_symlink():
        raise SystemExit(f"pitfix out_dir already exists (no overwrite): {p}")
    return p


_OK_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def check_allow_ok(path, field: str, *, root: Path, now_et: _dt.datetime | None = None,
                   flag: str = "--allow-ok") -> dict:
    """r3c (Arch 016ae55e P3-4): allow-switch .ok check, key=value only (the colon form is NOT accepted).
    `path` absolute or relative to `root`; must be an existing UTF-8 file, not under a `_consumed` directory, and
    neither its file name nor its content may contain "DRAFT" (case-insensitive; e.g. x.ok.draft; Arch 11:11 ET ③).
    Blank lines and lines starting with '#' are ignored; a line `key=value` (key [A-Za-z_][A-Za-z0-9_]*, split at the
    first '=', both sides stripped) is a pair; a key may appear at most once; a line `key: ...` for a required key
    is rejected explicitly. Required: `field`=true, live=false, promotion=false, and expires_et=<ISO 8601 WITH UTC
    offset> strictly later than now (ET). Values are exact lowercase strings. Any failure -> SystemExit.
    Returns ok_path / ok_sha256 / field / expires_et / checked_at_et for the summary."""
    p = Path(path)
    p = p if p.is_absolute() else Path(root) / p
    if not p.is_file():
        raise SystemExit(f"{flag} {p}: not a file")
    if "_consumed" in p.resolve().parts:
        raise SystemExit(f"{flag} {p}: .ok under _consumed/ (already used)")
    if any("DRAFT" in n.upper() for n in (p.name, p.resolve().name)):  # Arch 11:11 ET ③ (incl. *.ok.draft)
        raise SystemExit(f"{flag} {p}: file name contains DRAFT (a draft .ok is not an authorisation)")
    raw = p.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit(f"{flag} {p}: not UTF-8 ({e})")
    if "DRAFT" in text.upper():  # Arch 11:11 ET ③: any DRAFT marker anywhere in the file (comments included)
        raise SystemExit(f"{flag} {p}: content contains DRAFT (a draft .ok is not an authorisation)")
    need = {field: "true", "live": "false", "promotion": "false"}
    req = (*need, "expires_et")
    kv: dict = {}
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        k, sep, v = s.partition("=")
        k = k.strip()
        if not sep or not _OK_KEY.fullmatch(k):
            ck = s.partition(":")[0].strip()
            if ck in req:
                raise SystemExit(f"{flag} {p}: '{ck}: ...' colon form is not accepted; use {ck}=<value>")
            continue
        if k in kv:
            raise SystemExit(f"{flag} {p}: key {k!r} appears more than once")
        kv[k] = v.strip()
    for k, want in need.items():
        if kv.get(k) != want:
            raise SystemExit(f"{flag} {p}: needs {k}={want}, got {kv.get(k)!r}")
    try:
        exp = _dt.datetime.fromisoformat(kv.get("expires_et", ""))
    except ValueError as e:
        raise SystemExit(f"{flag} {p}: expires_et missing/unparseable ({e})")
    if exp.tzinfo is None:
        raise SystemExit(f"{flag} {p}: expires_et must carry a UTC offset, got {kv['expires_et']!r}")
    now = (now_et or _dt.datetime.now(_ET)).astimezone(_ET)
    if exp <= now:
        raise SystemExit(f"{flag} {p}: expired (expires_et={kv['expires_et']}, "
                         f"now {now.isoformat(timespec='seconds')})")
    return {"ok_path": str(p.resolve()), "ok_sha256": hashlib.sha256(raw).hexdigest(), "field": field,
            "expires_et": exp.astimezone(_ET).isoformat(timespec="seconds"),
            "checked_at_et": now.isoformat(timespec="seconds")}
