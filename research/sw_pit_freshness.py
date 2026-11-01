"""SW PIT (data/v2/sw_pit) freshness self-check — 主 Agent 2026-10-18 05:06 ET ruling; Arch ccc7546f + 05:18 unified rules (Intel bc9ef8a1) (r5: Arch 8d5bc796 P3 x3 + calendar guard).

Consumers of sw_pit must check the table themselves; freshness overall=ok does NOT cover sw_pit.
Freshness is judged by manifest `built` only (directory mtimes are unreliable).
- `built` is naive America/New_York (queue_chain datetime.now()); convert to Asia/Shanghai.
  coverage_day = built's SH date if it is an open SSE day and SH time >= 18:00, else the last open day before it.
- ref_day = latest completed SSE session as of now (SH date if open and SH time >= 18:00, else last open day before).
- lag_tdays = open SSE days in (coverage_day, ref_day]; stale (warn) if lag_tdays >= STALE_LAG_TDAYS.
- coverage_gap (warn) if as_of (last rebalance day) > coverage_day.
- Integrity failures RAISE (stop): manifest unreadable, parquet missing, sha256 != manifest, built missing/unparseable,
  in_date_range missing/invalid (same as Intel), SH date of built/now beyond calendar end (r5).
Calendar: data/v2/calendar/trade_cal_sse_pit.parquet (is_open). Read-only; cached per level per process.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

STALE_LAG_TDAYS = 3
SH_AVAIL_HOUR = 18
_ET = ZoneInfo("America/New_York")
_SH = ZoneInfo("Asia/Shanghai")
_CACHE: dict = {}


class SwPitIntegrityError(RuntimeError):
    pass


def _ymd(x: str) -> _dt.date:
    return _dt.date(int(x[:4]), int(x[4:6]), int(x[6:8]))


def _calendar(root: Path) -> tuple[list, _dt.date]:
    """(sorted open days, last cal_date incl. closed days)."""
    cal = pd.read_parquet(root / "data/v2/calendar/trade_cal_sse_pit.parquet", columns=["cal_date", "is_open"])
    if cal.empty:
        raise SwPitIntegrityError("trade_cal_sse_pit is empty")
    days = sorted(_ymd(x) for x in cal.loc[cal["is_open"] == 1, "cal_date"].astype(str))
    return days, max(_ymd(x) for x in cal["cal_date"].astype(str))


def _open_days(root: Path) -> list:
    return _calendar(root)[0]


def _guard_cal(sh_dt: _dt.datetime, cal_end: _dt.date, what: str) -> None:
    # r5 (Arch 8d5bc796): calendar ends 20261231; beyond it lag would be undercounted -> hard stop
    if sh_dt.date() > cal_end:
        raise SwPitIntegrityError(f"trade calendar ends {cal_end.isoformat()} < SH date of {what} {sh_dt.date().isoformat()}; extend trade_cal_sse_pit")


def _completed_session(sh_dt: _dt.datetime, open_days: list) -> _dt.date:
    d = sh_dt.date()
    if d in set(open_days) and sh_dt.hour >= SH_AVAIL_HOUR:
        return d
    prev = [x for x in open_days if x < d]
    if not prev:
        raise SwPitIntegrityError(f"calendar has no open day before {d}")
    return prev[-1]


def _integrity(root: Path, level: str) -> dict:
    """Integrity + built/coverage (as_of independent). Raises SwPitIntegrityError on any integrity failure."""
    mpath = root / "data/v2/sw_pit/manifest.json"
    try:
        man = json.loads(mpath.read_text(encoding="utf-8"))
    except Exception as e:
        raise SwPitIntegrityError(f"sw_pit manifest unreadable: {mpath} ({type(e).__name__}: {e})")
    fpath = root / "data/v2/sw_pit" / f"industry_members_sw_{level}_pit.parquet"
    if not fpath.exists():
        raise SwPitIntegrityError(f"sw_pit parquet missing: {fpath}")
    actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
    listed = (man.get("sha256") or {}).get(f"sw_pit/{fpath.name}")
    if listed != actual:
        raise SwPitIntegrityError(f"sw_pit sha mismatch: actual={actual} manifest={listed}")
    built = man.get("built")
    if not built:
        raise SwPitIntegrityError("sw_pit manifest has no 'built'")
    try:
        b = _dt.datetime.fromisoformat(str(built))
    except (TypeError, ValueError) as e:
        raise SwPitIntegrityError(f"sw_pit manifest 'built' unparseable: {built!r} ({e})")
    # naive -> ET (queue_chain datetime.now()); tz-aware -> convert, never overwrite (Arch 5a64a6f1 P3)
    built_et = b.replace(tzinfo=_ET) if b.tzinfo is None else b.astimezone(_ET)
    built_sh = built_et.astimezone(_SH)
    rng = (man.get(level) or {}).get("in_date_range")
    if not isinstance(rng, (list, tuple)) or len(rng) != 2:
        raise SwPitIntegrityError(f"sw_pit manifest[{level!r}].in_date_range missing/invalid: {rng!r}")
    try:
        [_dt.date.fromisoformat(str(x)[:10]) for x in rng]
    except (TypeError, ValueError) as e:
        raise SwPitIntegrityError(f"sw_pit manifest[{level!r}].in_date_range unparseable: {rng!r} ({e})")
    rng = list(rng)
    days, cal_end = _calendar(root)
    _guard_cal(built_sh, cal_end, "built")
    return {"level": level, "days": days, "cal_end": cal_end, "built_et": built_et, "built_sh": built_sh,
            "coverage": _completed_session(built_sh, days), "in_date_range": rng, "sha256": actual,
            "promotion_approved": man.get("promotion_approved")}


def _evaluate(base: dict, as_of: _dt.date | None, as_of_defaulted: bool, now_et: _dt.datetime) -> dict:
    days, coverage = base["days"], base["coverage"]
    now_sh = now_et.astimezone(_SH)
    _guard_cal(now_sh, base["cal_end"], "now")
    ref = _completed_session(now_sh, days)
    lag = sum(1 for x in days if coverage < x <= ref)
    warns = []
    if lag >= STALE_LAG_TDAYS:
        warns.append(f"lag_tdays={lag}>={STALE_LAG_TDAYS}")
    if as_of is not None and as_of > coverage:
        warns.append(f"coverage_gap: as_of={as_of.isoformat()} > coverage_day={coverage.isoformat()}")
    if as_of_defaulted:
        warns.append("as_of 取默认值（调用方未传）")
    rng = base["in_date_range"]
    return {"manifest": "data/v2/sw_pit/manifest.json", "level": base["level"],
            "checked_at_et": now_et.isoformat(timespec="seconds"),
            "built_et": base["built_et"].isoformat(timespec="seconds"),
            "built_sh": base["built_sh"].isoformat(timespec="seconds"),
            "coverage_day": coverage.isoformat(), "ref_day": ref.isoformat(), "lag_tdays": lag,
            "as_of": None if as_of is None else as_of.isoformat(), "as_of_defaulted": as_of_defaulted,
            "in_date_range": rng, "in_date_max": rng[-1], "sha256": base["sha256"],
            "promotion_approved": base["promotion_approved"], "warns": warns}


def _finalize(r: dict) -> dict:
    blocking = [w for w in r["warns"] if not w.startswith("as_of 取默认值")]
    r["stale"] = bool(blocking)
    tail = (f"（built 上海 {r['built_sh'][:16].replace('T', ' ')}，覆盖至 {r['coverage_day']}，"
            f"in_date 最大 {r['in_date_max']}）")
    if blocking:
        r["disclosure_zh"] = "【披露】申万 sw_pit 表可能过期：" + "；".join(r["warns"]) + tail + "。行业相关结果仅作带披露参考。"
    elif r["warns"]:  # only "as_of 取默认值" -> neutral prefix (Arch 8d5bc796 P3)
        r["disclosure_zh"] = "【披露】sw_pit 检查：as_of 取默认值（调用方未传），未判过期" + tail + "。"
    else:
        r["disclosure_zh"] = ""
    return r


def _d(x) -> _dt.date | None:
    return None if x is None else _dt.date.fromisoformat(str(x)[:10])


def check_sw_pit(root: Path, level: str = "l1", as_of: str | None = None,
                 now_et: _dt.datetime | None = None, as_of_defaulted: bool = False) -> dict:
    """Uncached single check (integrity raises; staleness warns)."""
    r = _finalize(_evaluate(_integrity(root, level), _d(as_of), as_of_defaulted,
                            now_et or _dt.datetime.now(_ET)))
    print("[sw_pit_freshness]", json.dumps(r, ensure_ascii=False))
    return r


def ensure_checked(root: Path, level: str = "l1", as_of: str | None = None,
                   as_of_defaulted: bool = False, now_et: _dt.datetime | None = None) -> dict:
    """Integrity/built cached once per (root, level); coverage_gap re-evaluated on EVERY call.
    Aggregate keeps the latest as_of seen and the union of all warns."""
    key = (str(root), level)
    ent = _CACHE.get(key)
    if ent is None:
        ent = _CACHE[key] = {"base": _integrity(root, level), "agg": None}
    r = _evaluate(ent["base"], _d(as_of), as_of_defaulted, now_et or _dt.datetime.now(_ET))
    agg = ent["agg"]
    if agg is None:
        agg = dict(r, n_calls=0, as_of_all=[])
    agg["n_calls"] += 1
    agg["as_of_all"].append(r["as_of"])
    if r["as_of"] is not None and (agg["as_of"] is None or r["as_of"] > agg["as_of"]):
        agg["as_of"], agg["as_of_defaulted"] = r["as_of"], r["as_of_defaulted"]
    agg["checked_at_et"], agg["ref_day"], agg["lag_tdays"] = r["checked_at_et"], r["ref_day"], r["lag_tdays"]
    agg["warns"] = list(dict.fromkeys(agg["warns"] + r["warns"]))
    ent["agg"] = _finalize(agg)
    print("[sw_pit_freshness]", json.dumps(_finalize(dict(r)), ensure_ascii=False))
    return ent["agg"]


def last_result(level: str = "l1", root: Path | None = None) -> dict | None:
    for (rt, lv), ent in _CACHE.items():
        if lv == level and (root is None or rt == str(root)):
            return ent["agg"]
    return None


def _reset_cache_for_tests() -> None:
    _CACHE.clear()
