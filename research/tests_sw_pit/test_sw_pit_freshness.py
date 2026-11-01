"""Minimal synthetic tests for research/sw_pit_freshness.py (Arch c432c912 P3; r5 adds Arch 8d5bc796 P3 cases). tmp ROOT only; no real data."""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research import sw_pit_freshness as m  # noqa: E402

ET = ZoneInfo("America/New_York")
# open days: Mon 2026-10-12 .. Fri 2026-10-16; weekend closed
OPEN = ["20261009", "20261012", "20261013", "20261014", "20261015", "20261016", "20261019"]
ALL = ["20261009", "20261010", "20261011", "20261012", "20261013", "20261014", "20261015",
       "20261016", "20261017", "20261018", "20261019"]


def _root(tmp_path, built="2026-10-14T04:00:19", bad_sha=False, in_date_range=("2020-01-01", "2026-09-24")):
    (tmp_path / "data/v2/calendar").mkdir(parents=True)
    (tmp_path / "data/v2/sw_pit").mkdir(parents=True)
    pd.DataFrame({"cal_date": ALL, "is_open": [1 if d in OPEN else 0 for d in ALL]}).to_parquet(
        tmp_path / "data/v2/calendar/trade_cal_sse_pit.parquet", index=False)
    fp = tmp_path / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"
    pd.DataFrame({"ts_code": ["000001.SZ"], "l1_name": ["银行"], "in_date": ["20200101"],
                  "out_date": [None]}).to_parquet(fp, index=False)
    sha = hashlib.sha256(fp.read_bytes()).hexdigest()
    man = {"l1": {} if in_date_range is None else {"in_date_range": list(in_date_range)},
           "sha256": {"sw_pit/industry_members_sw_l1_pit.parquet": "0" * 64 if bad_sha else sha}}
    if built is not None:
        man["built"] = built
    (tmp_path / "data/v2/sw_pit/manifest.json").write_text(json.dumps(man))
    m._reset_cache_for_tests()
    return tmp_path


NOW = dt.datetime(2026, 10, 18, 5, 0, tzinfo=ET)  # SH Sun 17:00 -> ref 10-16


def test_sha_mismatch_raises(tmp_path):
    with pytest.raises(m.SwPitIntegrityError):
        m.check_sw_pit(_root(tmp_path, bad_sha=True), now_et=NOW)


def test_missing_built_raises(tmp_path):
    with pytest.raises(m.SwPitIntegrityError):
        m.check_sw_pit(_root(tmp_path, built=None), now_et=NOW)


def test_et_0400_covers_previous_tday(tmp_path):
    r = m.check_sw_pit(_root(tmp_path), now_et=NOW)  # ET 10-14 04:00 = SH 16:00 < 18:00
    assert r["coverage_day"] == "2026-10-13"


def test_lag_exactly_3_warns(tmp_path):
    r = m.check_sw_pit(_root(tmp_path), now_et=NOW)  # (10-13, 10-16] = 3 open days
    assert r["lag_tdays"] == 3 and r["stale"] and any(w.startswith("lag_tdays=3") for w in r["warns"])
    r2 = m.check_sw_pit(_root(tmp_path / "b", built="2026-10-14T07:00:00"), now_et=NOW)  # SH 19:00 -> cov 10-14, lag 2
    assert r2["lag_tdays"] == 2 and not r2["stale"]


def test_two_calls_latest_as_of_wins(tmp_path):
    root = _root(tmp_path, built="2026-10-16T07:00:00")  # SH 10-16 19:00 -> cov 10-16, lag 0
    a = m.ensure_checked(root, as_of="2026-10-09", now_et=NOW)
    assert a["as_of"] == "2026-10-09" and not a["stale"]
    b = m.ensure_checked(root, as_of="2026-10-19", now_et=NOW)  # later call, later as_of -> gap must surface
    assert b["as_of"] == "2026-10-19" and b["stale"]
    assert any(w.startswith("coverage_gap") for w in m.last_result(root=root)["warns"])
    c = m.ensure_checked(root, as_of="2026-10-12", now_et=NOW)  # earlier as_of does not roll back
    assert c["as_of"] == "2026-10-19" and c["stale"] and c["n_calls"] == 3


def test_tz_aware_built_is_converted_not_overwritten(tmp_path):
    # 2026-10-14T10:30+08:00 (SH) must stay SH 10:30 -> < 18:00 -> coverage 10-13; replace() would give ET 10:30 = SH 22:30 -> 10-14
    r = m.check_sw_pit(_root(tmp_path, built="2026-10-14T10:30:00+08:00"), now_et=NOW)
    assert r["built_sh"].startswith("2026-10-14T10:30") and r["coverage_day"] == "2026-10-13"


# ---- r5 (Arch 8d5bc796) ----
@pytest.mark.parametrize("rng", [None, ("2020-01-01",), ("2020-01-01", "not-a-date")])
def test_in_date_range_missing_or_invalid_raises(tmp_path, rng):
    with pytest.raises(m.SwPitIntegrityError):
        m.check_sw_pit(_root(tmp_path, in_date_range=rng), now_et=NOW)


def test_built_unparseable_raises(tmp_path):
    with pytest.raises(m.SwPitIntegrityError):
        m.check_sw_pit(_root(tmp_path, built="14/10/2026 04:00"), now_et=NOW)


def test_as_of_default_only_neutral_disclosure(tmp_path):
    root = _root(tmp_path, built="2026-10-16T07:00:00")  # lag 0, no gap
    r = m.ensure_checked(root, as_of="2026-10-16", as_of_defaulted=True, now_et=NOW)
    assert not r["stale"] and r["warns"] == ["as_of 取默认值（调用方未传）"]
    assert r["disclosure_zh"].startswith("【披露】sw_pit 检查：as_of 取默认值") and "可能过期" not in r["disclosure_zh"]
    s = m.check_sw_pit(_root(tmp_path / "s"), now_et=NOW, as_of_defaulted=True)  # stale keeps old prefix
    assert s["stale"] and s["disclosure_zh"].startswith("【披露】申万 sw_pit 表可能过期")


def test_calendar_end_guard_raises(tmp_path):
    with pytest.raises(m.SwPitIntegrityError):  # now SH 2026-10-20 > cal end 2026-10-19
        m.check_sw_pit(_root(tmp_path), now_et=dt.datetime(2026, 10, 20, 9, 0, tzinfo=ET))
    with pytest.raises(m.SwPitIntegrityError):  # built SH 2026-10-20 > cal end
        m.check_sw_pit(_root(tmp_path / "b", built="2026-10-20T01:00:00"), now_et=NOW)
