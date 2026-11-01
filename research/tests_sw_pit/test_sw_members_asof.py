"""Synthetic tests for research/sw_members_asof.py (PIT fix, r2 per Arch 3f195231 + 主 Agent 10-18 ~05:45 ET gap ruling;
DIFF C: d-1 = previous SSE open day per 主 Agent 06:01 ET / Arch c72f0856 P3-1/P3-2/P3-5;
C r2: window prev_open(d) <= out_date < d, cal required, d must be open, NaT rejected, in_date <= out_date
— Arch c6f97571;
C r3: on_overlap='raise' default / 'count' disclosure (主 Agent 06:49 ET), pure-rule NaT raises, mandatory sw_pit fields,
load_sw_l1 path parameter — Arch 28eabd35; C r3b: CLEAN layout adapter + sw_l1_table_check, synthetic files only;
r3c — Arch 016ae55e P3-1..P3-6: gap-carry multi-candidate raise/count, exact-duplicate drop, in>out count,
key limit + session chunking, key=value allow .ok, lag-only stale disclosure; Arch 11:11 ET: CLEAN lag
threshold 10 (lag > 10 alone -> stale + stale_lag_only, Arch 11:13/11:20), same-in_date conflict, DRAFT .ok
rejected, max_keys parameter; Arch 11:20 ET: Tsh.00018 exact exclusion, [us]/[ns] precision equivalence;
Data §14②: non-A id Tsh.00018; r3d (Arch 11:29 ET ②): manifest n_l1 + available_at_nulls compared).
Fixture O.SZ / T.SZ are DELIBERATE overlaps: tests that query them pass on_overlap="count" explicitly or assert the
default raise.
In-memory frames / tmp ROOT only; no real data (every gap-carry call passes the synthetic CAL explicitly)."""
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research import sw_members_asof as A  # noqa: E402
from research.sw_pit_freshness import SwPitIntegrityError  # noqa: E402


# Verbatim copy of Intel's function from _review/intel_sw_pit_freshness_20261018_r2.diff
# (sha256 0e968759d390490d625c1a7705fd6505e19aeae968710ecbf6a818439c6da4b5, diff lines 90-94), docstring omitted.
def intel_sw_members_asof(sw: pd.DataFrame, d) -> pd.DataFrame:
    d = pd.Timestamp(d).normalize()
    return sw[(sw.in_date < d) & (sw.out_date.isna() | (sw.out_date >= d))]


# Synthetic SSE calendar 2018-01-01..2026-12-31: Mon-Fri open, Sat/Sun closed, plus ONE weekday holiday
# 2025-03-17 (Mon, is_open=0; Arch c6f97571 P3-4). No other test session is 03-17/03-18, so older cases are unaffected.
_DAYS = pd.date_range("2018-01-01", "2026-12-31", freq="D")
HOLIDAY = "20250317"
CAL_DF = pd.DataFrame({"cal_date": _DAYS.strftime("%Y%m%d"),
                       "is_open": ((_DAYS.dayofweek < 5) & (_DAYS.strftime("%Y%m%d") != HOLIDAY)).astype(int)})
CAL = A.TradeCal(CAL_DF, sha256="synthetic")

SW = pd.DataFrame({
    # X: 电子 -> 计算机 (old out 03-10, new in 03-10); Y: 银行 open; Z: out 03-10, no successor
    # O: overlap — stale open 钢铁 row (in 2018) listed AFTER the newer open 农林牧渔 row (in 2021) -> latest in_date wins
    # T: equal in_date, both open; is_new=Y row must win regardless of file order
    # G: gap — old 电子 out 2025-03-10 (Mon), new 计算机 in 2025-03-11 (Tue): 03-11 carries 电子
    # H: no gap carry — old 电子 out 2025-03-09 (Sun), new 计算机 in 2025-03-11 (out == d-2)
    # W (DIFF C): cross-weekend — old 电子 out 2025-03-07 (Fri), new 计算机 in 2025-03-10 (Mon): Mon carries 电子
    # V (C r2): weekday holiday — old 电子 out 2025-03-14 (Fri), Mon 03-17 holiday, new 计算机 in 2025-03-18 (Tue):
    #    Tue carries
    "ts_code": ["X.SZ", "X.SZ", "Y.SH", "Z.SH", "O.SZ", "O.SZ", "T.SZ", "T.SZ", "G.SZ", "G.SZ", "H.SZ", "H.SZ",
                "W.SZ", "W.SZ", "V.SZ", "V.SZ"],
    "l1_name": ["电子", "计算机", "银行", "医药生物", "农林牧渔", "钢铁", "通信", "传媒", "电子", "计算机", "电子", "计算机",
                "电子", "计算机", "电子", "计算机"],
    "in_date": ["20200101", "20250310", "20190101", "20200101", "20210730", "20180101", "20200803", "20200803",
                "20200101", "20250311", "20200101", "20250311", "20200101", "20250310", "20200101", "20250318"],
    "out_date": ["20250310", None, None, "20250310", None, None, None, None, "20250310", None, "20250309", None,
                 "20250307", None, "20250314", None],
    "is_new": ["N", "Y", "Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y", "N", "Y"],
})


def _k(pairs):
    return pd.DataFrame(pairs, columns=["instrument", "session"])


def _q(pairs, carry=False, sw=None, stats=None, on_overlap="raise"):
    sw = A.prep_sw(SW if sw is None else sw)
    if carry:
        return A.sw_l1_asof_with_gap_carry(sw, _k(pairs), stats=stats, cal=CAL, on_overlap=on_overlap).tolist()
    return A.l1_asof(sw, _k(pairs), stats=stats, on_overlap=on_overlap).tolist()


def test_reclassification_mid_period():
    assert _q([("X.SZ", "2025-03-07"), ("X.SZ", "2025-03-11")]) == ["电子", "计算机"]


def test_in_date_eq_d_excluded_out_date_eq_d_included():
    assert _q([("X.SZ", "2025-03-10"), ("Z.SH", "2025-03-10"), ("Z.SH", "2025-03-11")]) == ["电子", "医药生物", None]


def test_null_out_date_member_and_unknown_code():
    assert _q([("Y.SH", "2026-10-09"), ("NOPE.SZ", "2026-10-09"), ("Y.SH", "2019-01-01")]) == ["银行", None, None]


def test_overlap_latest_in_date_wins_and_tie_prefers_is_new():
    # C r3: O/T are deliberate overlaps -> explicit on_overlap="count" (default "raise" asserted in the overlap tests)
    assert _q([("O.SZ", "2025-01-02"), ("T.SZ", "2025-01-02")], on_overlap="count") == ["农林牧渔", "通信"]
    sw2 = A.prep_sw(SW.iloc[::-1].reset_index(drop=True))  # file order reversed -> same answers
    k = pd.DataFrame([("O.SZ", "2025-01-02"), ("T.SZ", "2025-01-02")], columns=["instrument", "session"])
    assert A.l1_asof(sw2, k, on_overlap="count").tolist() == ["农林牧渔", "通信"]
    with pytest.raises(SwPitIntegrityError, match="O.SZ"):
        A.l1_asof(sw2, k)


def test_rowfilter_matches_intel_verbatim_and_vectorized():
    sw = A.prep_sw(SW)
    codes = sorted(SW.ts_code.unique())
    for d in ("2019-06-03", "2025-03-07", "2025-03-10", "2025-03-11", "2025-03-12"):
        mine, intel = A.sw_members_asof(sw, d), intel_sw_members_asof(sw, d)
        assert list(mine["_ord"]) == list(intel["_ord"])  # identical row sets
        pick = intel.sort_values(["in_date", "_pri", "_ord"]).groupby("ts_code").tail(1)
        exp = dict(zip(pick.ts_code, pick.l1_name))
        got = A.l1_asof(sw, pd.DataFrame({"instrument": codes, "session": d}),
                        on_overlap="count").tolist()  # O/T are deliberate overlaps
        assert got == [exp.get(c) for c in codes]
    # documented divergence: Intel intel_common keep="last" (file order) picks the stale 钢铁 row for O.SZ
    ik = intel_sw_members_asof(sw, "2025-01-02").drop_duplicates("ts_code", keep="last")
    assert dict(zip(ik.ts_code, ik.l1_name))["O.SZ"] == "钢铁"
    assert _q([("O.SZ", "2025-01-02")], on_overlap="count") == ["农林牧渔"]


def test_gap_day_carries_old_then_new_active():
    st = {}
    k = pd.DataFrame([("G.SZ", "2025-03-11"), ("G.SZ", "2025-03-12")], columns=["instrument", "session"])
    assert A.sw_l1_asof_with_gap_carry(A.prep_sw(SW), k, stats=st, cal=CAL).tolist() == ["电子", "计算机"]
    assert st["n_rows_gap_carry"] == 1 and st["n_rows_unknown"] == 0
    assert _q([("G.SZ", "2025-03-11")], carry=False) == [None]  # pure rule leaves the gap unknown


def test_no_carry_when_out_date_is_d_minus_2():
    st = {}
    k = pd.DataFrame([("H.SZ", "2025-03-11"), ("Z.SH", "2025-03-12")], columns=["instrument", "session"])
    assert A.sw_l1_asof_with_gap_carry(A.prep_sw(SW), k, stats=st, cal=CAL).tolist() == [None, None]
    assert st["n_rows_gap_carry"] == 0 and st["n_rows_unknown"] == 2
    assert A.prep_sw(SW).attrs["prep_stats"]["n_reclass_gap_rows"] >= 1


def test_gap_with_out_date_parse_failure_raises():
    bad = SW.copy()
    bad.loc[bad.index[8], "out_date"] = "2025-13-45"  # G.SZ old row (the gap row) unparseable
    with pytest.raises(SwPitIntegrityError):
        A.sw_l1_asof_with_gap_carry(bad, pd.DataFrame([("G.SZ", "2025-03-11")], columns=["instrument", "session"]),
                                    cal=CAL)


def test_in_date_parse_failure_counted_never_matches():
    bad = SW.copy()
    bad.loc[bad.index[2], "in_date"] = "garbage"
    sw = A.prep_sw(bad)
    assert sw.attrs["prep_stats"]["n_in_unparsed"] == 1
    assert A.l1_asof(sw, pd.DataFrame([("Y.SH", "2025-01-02")], columns=["instrument", "session"])).tolist() == [None]


def test_by_session_and_reclass_share():
    ia = A.IndustryAsOf(SW, static_map={"X.SZ": "计算机", "Y.SH": "银行", "G.SZ": "计算机"}, cal=CAL)
    rows = pd.DataFrame({"instrument": ["X.SZ", "X.SZ", "Y.SH", "G.SZ"],
                         "session": ["2025-03-07", "2025-03-11", "2025-03-07", "2025-03-11"],
                         "weight": [0.4, 0.2, 0.2, 0.2]})
    bs = ia.by_session(rows)
    assert bs["2025-03-07"] == {"X.SZ": "电子", "Y.SH": "银行"} and bs["2025-03-11"] == {"X.SZ": "计算机", "G.SZ": "电子"}
    r = ia.reclass_share(rows, weight_col="weight")
    assert r["n_rows_diff"] == 2 and r["n_rows_gap_carry"] == 1 and abs(r["share_rows_gap_carry"] - 0.25) < 1e-12
    assert abs(r["share_weight_diff"] - 0.6) < 1e-12 and r["n_rows_asof_missing"] == 0


def test_pitfix_out_dir_guard(tmp_path):
    (tmp_path / "output/strategy_hiliq/b4").mkdir(parents=True)
    (tmp_path / "output/strategy_hiliq/old_run").mkdir()
    ok = A.pitfix_out_dir_guard(tmp_path, "output/strategy_hiliq/pitfix_compare_20261018")
    assert ok == (tmp_path / "output/strategy_hiliq/pitfix_compare_20261018").resolve() and not ok.exists()
    for bad in ("output/strategy_hiliq/b4", "output/strategy_hiliq/b4/x", "output/strategy_hiliq/old_run",
                "output/strategy_hiliq", "output/strategy_fulla/x", "output/strategy_hiliq/paper_x",
                "output/strategy_hiliq/FROZEN_y", "output/strategy_hiliq/../strategy_fulla/z", "/tmp/x"):
        with pytest.raises(SystemExit):
            A.pitfix_out_dir_guard(tmp_path, bad)


# ---- DIFF C (主 Agent 2026-10-18 06:01 ET: d-1 = previous SSE open day; Arch c72f0856 P3-2 / P3-5) ----

def test_cross_weekend_friday_out_monday_in_carries_monday():
    st = {}
    assert _q([("W.SZ", "2025-03-10"), ("W.SZ", "2025-03-11"), ("W.SZ", "2025-03-07")], carry=True,
              stats=st) == ["电子", "计算机", "电子"]
    assert st["n_rows_gap_carry"] == 1 and st["n_rows_gap_carry_no_successor"] == 0 and st["n_rows_unknown"] == 0
    assert st["n_rows_gap_carry_out_on_closed_day"] == 0 and st["trade_cal_sha256"] == "synthetic"
    assert _q([("W.SZ", "2025-03-10")]) == [None]  # pure rule leaves Monday unknown


def test_natural_day_cases_under_tradeday_rule():
    st = {}
    got = _q([("G.SZ", "2025-03-11"), ("H.SZ", "2025-03-11"), ("H.SZ", "2025-03-10"), ("Z.SH", "2025-03-11"),
              ("Z.SH", "2025-03-12"), ("X.SZ", "2025-03-11")], carry=True, stats=st)
    # G: Mon out / Tue in -> carried (same as calendar-day rule); H 03-11: out 03-09 < prev open 03-10 -> None (same);
    # H 03-10: prev open 03-07 <= out 03-09 (Sun) < 03-10 -> carried (C r2 window; calendar-day rule also carries);
    # Z 03-11: out 03-10, no successor -> carried 1 day; Z 03-12 -> None; X: new row active -> 计算机 (no carry)
    assert got == ["电子", None, "电子", "医药生物", None, "计算机"]
    assert st["n_rows_gap_carry"] == 3 and st["n_rows_gap_carry_no_successor"] == 1
    assert st["n_rows_gap_carry_out_on_closed_day"] == 1 and st["n_rows_unknown"] == 2


def test_gap_carry_excludes_unparsed_in_date():
    bad = SW.copy()
    bad.loc[bad.index[8], "in_date"] = "garbage"  # G.SZ old row (out 2025-03-10) with unparseable in_date
    st = {}
    assert _q([("G.SZ", "2025-03-11")], carry=True, sw=bad, stats=st) == [None]
    assert st["n_rows_gap_carry"] == 0 and A.prep_sw(bad).attrs["prep_stats"]["n_in_unparsed"] == 1
    assert _q([("G.SZ", "2025-03-11")], carry=True) == ["电子"]  # control: parsed in_date is carried


def test_session_outside_calendar_raises():
    short = A.TradeCal(CAL_DF[CAL_DF["cal_date"] <= "20251231"], sha256="short")
    sw = A.prep_sw(SW)
    for sess, cal, why in (("2027-01-04", CAL, "outside trade calendar"),
                           ("2026-01-02", short, "outside trade calendar"),
                           ("2017-12-29", CAL, "outside trade calendar"), ("2018-01-01", CAL, "no open day before")):
        with pytest.raises(SwPitIntegrityError, match=why):  # past end / short calendar / before start / start day
            A.sw_l1_asof_with_gap_carry(sw, _k([("Y.SH", "2025-01-02"), ("Y.SH", sess)]), cal=cal)
    assert A.l1_asof(sw, _k([("Y.SH", "2027-01-04")])).tolist() == ["银行"]  # pure rule does not use the calendar
    assert _q([("Y.SH", "2018-01-02")], carry=True) == [None]  # first day with an open day before it: no raise


def test_trade_cal_load_sha_pin_and_validation(tmp_path):
    fp = tmp_path / A.TRADE_CAL_REL
    fp.parent.mkdir(parents=True)
    CAL_DF.to_parquet(fp, index=False)
    sha = hashlib.sha256(fp.read_bytes()).hexdigest()
    with pytest.raises(SwPitIntegrityError):  # default pin fa4260b8... != synthetic file
        A.load_trade_cal(tmp_path)
    cal = A.load_trade_cal(tmp_path, sha_pin=sha)
    assert cal.sha256 == sha and cal.end == pd.Timestamp("2026-12-31") and cal.start == pd.Timestamp("2018-01-01")
    assert str(pd.Timestamp(cal.prev_open(["2025-03-10"])[0]).date()) == "2025-03-07"
    assert str(pd.Timestamp(cal.prev_open(["2025-03-18"])[0]).date()) == "2025-03-14"  # across the Mon holiday
    assert str(pd.Timestamp(cal.prev_open(["2025-03-17"], require_open=False)[0]).date()) == "2025-03-14"
    for bad in (CAL_DF.drop(index=5), CAL_DF.assign(is_open=2), CAL_DF.assign(cal_date="2025-03-10"),
                pd.concat([CAL_DF, CAL_DF.tail(1)]), CAL_DF.iloc[0:0]):
        with pytest.raises(SwPitIntegrityError):  # gap / bad is_open / not YYYYMMDD / duplicate / empty
            A.TradeCal(bad)


def test_pitfix_out_dir_guard_symlink_capadv_legs(tmp_path):
    base = tmp_path / "output/strategy_hiliq"
    (base / "b4").mkdir(parents=True)
    os.symlink(base / "b4", base / "lnk_b4")
    for bad, why in (("output/strategy_hiliq/lnk_b4", "inside b4/"), ("output/strategy_hiliq/lnk_b4/new", "inside b4/"),
                     ("output/strategy_hiliq/capadv_x2/new", "inside capadv_x2/"),
                     ("output/strategy_hiliq/legs/new", "inside legs/")):
        with pytest.raises(SystemExit, match=why):
            A.pitfix_out_dir_guard(tmp_path, bad)


# ---- C r2 (2026-10-18 06:16 ET instruction; Arch c6f97571 P3-2 / P3-3 / P3-4 / P3-7) ----

def test_out_on_sunday_carried_on_monday():
    st = {}
    assert _q([("H.SZ", "2025-03-10"), ("H.SZ", "2025-03-11"), ("H.SZ", "2025-03-12")], carry=True,
              stats=st) == ["电子", None, "计算机"]  # Mon carried (out Sun 03-09); Tue: out < prev open 03-10 -> unknown
    assert st["n_rows_gap_carry"] == 1 and st["n_rows_gap_carry_out_on_closed_day"] == 1


def test_weekday_holiday_carry_after_holiday():
    st = {}
    assert _q([("V.SZ", "2025-03-14"), ("V.SZ", "2025-03-18"), ("V.SZ", "2025-03-19")], carry=True,
              stats=st) == ["电子", "电子", "计算机"]  # Fri active; Tue after Mon holiday carried; Wed new row
    assert st["n_rows_gap_carry"] == 1 and st["n_rows_gap_carry_out_on_closed_day"] == 0
    assert _q([("V.SZ", "2025-03-18")]) == [None]  # pure rule leaves it unknown


def test_session_not_open_day_raises():
    sw = A.prep_sw(SW)
    for sess in ("2025-03-15", "2025-03-17"):  # Saturday; weekday holiday
        with pytest.raises(SwPitIntegrityError, match="not an SSE open day"):
            A.sw_l1_asof_with_gap_carry(sw, _k([("W.SZ", "2025-03-10"), ("Y.SH", sess)]), cal=CAL)
    assert A.l1_asof(sw, _k([("Y.SH", "2025-03-15")])).tolist() == ["银行"]  # pure rule does not use the calendar


def test_nat_session_raises():
    sw = A.prep_sw(SW)
    for sess in (pd.NaT, None, "not-a-date"):
        with pytest.raises(SwPitIntegrityError, match="NaT"):
            A.sw_l1_asof_with_gap_carry(sw, _k([("Y.SH", "2025-01-02"), ("Y.SH", sess)]), cal=CAL)


def test_gap_carry_requires_cal():
    sw = A.prep_sw(SW)
    with pytest.raises(SwPitIntegrityError, match="requires cal"):
        A.sw_l1_asof_with_gap_carry(sw, _k([("G.SZ", "2025-03-11")]))
    with pytest.raises(SwPitIntegrityError, match="requires cal"):
        A.l1_asof(sw, _k([("G.SZ", "2025-03-11")]), gap_carry=True)
    with pytest.raises(SwPitIntegrityError, match="requires cal"):
        A.IndustryAsOf(SW, static_map={})
    with pytest.raises(TypeError):  # load_trade_cal has no default root
        A.load_trade_cal()


def test_in_date_after_out_date_not_carried():
    bad = SW.copy()
    bad.loc[bad.index[12], "in_date"] = "20250309"  # W.SZ old row: in 03-09 > out 03-07 (inconsistent row)
    st = {}
    assert _q([("W.SZ", "2025-03-10")], carry=True, sw=bad, stats=st) == [None]
    assert st["n_rows_gap_carry"] == 0


# ---- C r3 (主 Agent 2026-10-18 06:49 ET on_overlap; Arch 28eabd35 P3-r2-1; Arch 06:50 path parameter) ----

def test_overlap_default_raise_message_names_codes():
    sw = A.prep_sw(SW)
    k = _k([("Y.SH", "2025-01-02"), ("O.SZ", "2025-01-02"), ("T.SZ", "2025-01-02")])
    with pytest.raises(SwPitIntegrityError, match=r"2 codes.*'O\.SZ', 'T\.SZ'"):
        A.l1_asof(sw, k)
    with pytest.raises(SwPitIntegrityError, match=r"O\.SZ"):
        A.sw_l1_asof_with_gap_carry(sw, k, cal=CAL)
    ia = A.IndustryAsOf(SW, cal=CAL)  # default on_overlap="raise"
    rows = _k([("O.SZ", "2025-01-02")]).assign(weight=1.0)
    with pytest.raises(SwPitIntegrityError, match=r"O\.SZ"):
        ia.by_session(rows)
    with pytest.raises(SwPitIntegrityError, match=r"O\.SZ"):
        ia.reclass_share(rows, weight_col="weight")
    assert _q([("Y.SH", "2025-01-02"), ("X.SZ", "2025-03-11")]) == ["银行", "计算机"]  # no overlap -> no raise


def test_overlap_count_list_and_pick():
    same = pd.DataFrame({"ts_code": ["S.SZ", "S.SZ"], "l1_name": ["银行", "银行"], "in_date": ["20200101", "20210101"],
                         "out_date": [None, None], "is_new": ["N", "Y"]})  # same-industry overlap (conflict=False)
    sw2 = pd.concat([SW, same], ignore_index=True)
    pairs = [("O.SZ", "2025-01-02"), ("O.SZ", "2025-01-03"), ("T.SZ", "2025-01-02"), ("X.SZ", "2025-03-11"),
             ("S.SZ", "2025-01-02")]
    for carry in (False, True):
        st = {}
        assert _q(pairs, carry=carry, sw=sw2, stats=st, on_overlap="count") == ["农林牧渔", "农林牧渔", "通信", "计算机", "银行"]
        assert st["on_overlap"] == "count" and st["overlap_tiebreak"] == A.OVERLAP_TIEBREAK
        assert st["n_rows_multi_match"] == 4 and st["n_codes_overlap_on_d"] == 3
        assert st["overlap_codes"] == [
            {"code": "O.SZ", "n_days": 2, "first_day": "2025-01-02", "last_day": "2025-01-03",
             "candidates": ["农林牧渔", "钢铁"], "chosen": ["农林牧渔"], "conflict": True},
            {"code": "S.SZ", "n_days": 1, "first_day": "2025-01-02", "last_day": "2025-01-02",
             "candidates": ["银行"], "chosen": ["银行"], "conflict": False},
            {"code": "T.SZ", "n_days": 1, "first_day": "2025-01-02", "last_day": "2025-01-02",
             "candidates": ["传媒", "通信"], "chosen": ["通信"], "conflict": True}]
        if carry:
            assert st["n_rows_gap_carry"] == 0 and st["n_rows_gap_carry_multi_candidate"] == 0


def test_on_overlap_invalid_value_raises():
    sw = A.prep_sw(SW)
    with pytest.raises(ValueError, match="on_overlap"):
        A.l1_asof(sw, _k([("Y.SH", "2025-01-02")]), on_overlap="first")
    with pytest.raises(ValueError, match="on_overlap"):
        A.sw_l1_asof_with_gap_carry(sw, _k([("Y.SH", "2025-01-02")]), cal=CAL, on_overlap=None)
    with pytest.raises(ValueError, match="on_overlap"):
        A.IndustryAsOf(SW, cal=CAL, on_overlap="RAISE")


def test_pure_rule_nat_session_raises():
    sw = A.prep_sw(SW)
    for sess in (pd.NaT, None, "not-a-date"):
        with pytest.raises(SwPitIntegrityError, match="NaT"):
            A.l1_asof(sw, _k([("Y.SH", "2025-01-02"), ("Y.SH", sess)]))


def test_sw_pit_required_fields():
    ia = A.IndustryAsOf(SW, cal=CAL, on_overlap="count")
    rows = pd.DataFrame({"instrument": ["O.SZ", "Y.SH", "NOPE.SZ"], "session": ["2025-01-02"] * 3,
                         "weight": [0.4, 0.3, 0.3]})
    rs = ia.reclass_share(rows, weight_col="weight")
    assert not A.sw_pit_required_ok(A.sw_pit_required(ia, rs))  # synthetic frame: no sha -> not OK
    ia.sha256 = "ab" * 32
    req = A.sw_pit_required(ia, rs)
    assert A.sw_pit_required_ok(req) and req["n_unknown_rows"] == 1 and req["n_overlap_codes"] == 1
    assert req["overlap_codes"][0]["code"] == "O.SZ" and req["on_overlap"] == "count"
    assert req["overlap_tiebreak"] == A.OVERLAP_TIEBREAK
    assert A.sw_pit_required(ia, rs, "n_rows_static_missing")["n_unknown_rows"] == rs["n_rows_static_missing"]
    for bad in ({**req, "n_overlap_codes": None}, {**req, "n_unknown_rows": True}, {**req, "sw_pit_sha256": "XYZ"},
                {k: v for k, v in req.items() if k != "n_unknown_rows"}, None):
        assert not A.sw_pit_required_ok(bad)
    assert not A.sw_pit_required_ok(A.sw_pit_required(ia, ia.reclass_share(rows.iloc[0:0])))  # empty -> not OK


def test_load_sw_l1_path_parameter(tmp_path):
    fp = tmp_path / "alt" / "sw.parquet"
    fp.parent.mkdir()
    SW.to_parquet(fp, index=False)
    sha = hashlib.sha256(fp.read_bytes()).hexdigest()
    sw = A.load_sw_l1(tmp_path, path=fp)
    assert sw.attrs["sha256"] == sha and sw.attrs["path"] == str(fp.resolve())
    assert A.load_sw_l1(tmp_path, path="alt/sw.parquet").attrs["sha256"] == sha  # relative to root
    ia = A.IndustryAsOf(sw, cal=CAL)
    assert ia.sha256 == sha and ia.path == str(fp.resolve())
    with pytest.raises(FileNotFoundError):  # default path (root / SW_L1_REL, CLEAN since C r3b) absent in tmp root
        A.load_sw_l1(tmp_path)


# Fixture with 6-digit codes (X.SZ -> 000001.SZ, ...) so the CLEAN adapter can map instrument_id back to ts_code.
_SIX = {c: f"{i + 1:06d}.{c.split('.')[1]}" for i, c in enumerate(sorted(set(SW["ts_code"])))}
SW6 = SW.assign(ts_code=SW["ts_code"].map(_SIX))


def _clean_frame(ids, names, in_dates, out_dates, is_new) -> pd.DataFrame:
    """Synthetic frame with exactly A.SW_L1_CLEAN_COLUMNS (names + pandas 3 dtypes)."""
    n = len(ids)
    ind = pd.to_datetime(pd.Series(list(in_dates))).astype("datetime64[us]")
    return pd.DataFrame({
        "instrument_id": pd.Series(list(ids), dtype="str"),
        "sw_code": pd.Series(["801000.SI"] * n, dtype="str"),
        "sw_name": pd.Series(list(names), dtype="str"),
        "in_date": ind,
        "out_date": pd.to_datetime(pd.Series(list(out_dates))).astype("datetime64[us]"),
        "available_at": (ind + pd.Timedelta(hours=18)).astype("datetime64[us]"),
        "source": pd.Series(["synthetic"] * n, dtype="str"),
        "revision": pd.Series([1] * n, dtype="int64"),
        "quality_status": pd.Series(["research_tushare_candidate"] * n, dtype="str"),
        "schema": pd.Series(["quantlab.v2.industry_members_sw_l1.v1"] * n, dtype="str"),
        "is_new": pd.Series(list(is_new), dtype="str")})


def _clean_layout(sw: pd.DataFrame) -> pd.DataFrame:
    """6-digit fixture rewritten in the CLEAN sw_l1_pit tushare layout (instrument_id sz.000001 / sw_name)."""
    code, mkt = sw["ts_code"].str.split(".").str[0], sw["ts_code"].str.split(".").str[1].str.lower()
    return _clean_frame(mkt + "." + code, sw["l1_name"], sw["in_date"], sw["out_date"], sw["is_new"])


def test_clean_schema_constant_matches_fixture():
    got = tuple((c, str(t)) for c, t in _clean_layout(SW6).dtypes.items())
    assert sorted(got) == sorted(A.SW_L1_CLEAN_COLUMNS)


def test_load_sw_l1_clean_layout_adapter(tmp_path):
    # Data r2 norm_code variants (dot / prefix, any case, surrounding spaces) + the known non-A-share id, exact CLEAN
    # spelling per Data §14② (Tsh.00018)
    ids = ["sz.000001", "SH.600000", "832317.BJ", " 600001.sh ", "Tsh.00018"]
    real = _clean_frame(ids, ["银行", "银行", "国防军工", "银行", "交通运输"], ["2020-01-02"] * 5, [None] * 5, ["Y"] * 5)
    fp = tmp_path / "clean.parquet"
    real.to_parquet(fp, index=False)
    sw = A.load_sw_l1(tmp_path, path=fp)
    assert sw["ts_code"].tolist() == ["000001.SZ", "600000.SH", "832317.BJ", "600001.SH"]
    assert sw["l1_name"].tolist() == ["银行", "银行", "国防军工", "银行"]
    lay = sw.attrs["layout"]
    assert lay["layout"].startswith("sw_l1_pit tushare")
    assert lay["non_a_share_excluded"] == ["Tsh.00018"] and lay["n_rows_non_a_share_excluded"] == 1
    assert lay["raw"] == {"rows": 5, "n_instruments": 5, "in_date_min": "2020-01-02", "in_date_max": "2020-01-02",
                          "n_l1": 1, "available_at_nulls": 0}  # r3d: fixture sw_code is constant 801000.SI
    ia = A.IndustryAsOf(sw, cal=CAL)
    assert ia.layout == lay
    assert A.l1_asof(ia.sw, _k([("000001.SZ", "2025-01-02"), ("Tsh.00018", "2025-01-02")])).tolist() == ["银行", None]
    # same answers as the sw_pit layout on the full fixture (overlap codes in count mode)
    fp2 = tmp_path / "clean_fixture.parquet"
    _clean_layout(SW6).to_parquet(fp2, index=False)
    days = ("2025-03-07", "2025-03-10", "2025-03-11", "2025-03-18")
    pairs = [(c, d) for c in sorted(set(SW6["ts_code"])) for d in days]
    got = A.sw_l1_asof_with_gap_carry(A.load_sw_l1(tmp_path, path=fp2), _k(pairs), cal=CAL, on_overlap="count")
    assert got.tolist() == _q(pairs, carry=True, sw=SW6, on_overlap="count")
    assert sum(v is not None for v in got) >= 30  # non-trivial: most fixture codes are known on these days
    # sw_pit layout wins when both exist (no CLEAN schema check); unknown layout / missing dates raise
    both = SW.assign(instrument_id="xx.000000", sw_name="错误")
    assert A.normalize_sw_l1_layout(both)[0]["l1_name"].tolist() == SW["l1_name"].tolist()
    with pytest.raises(SwPitIntegrityError, match="layout not recognised"):
        A.normalize_sw_l1_layout(SW.rename(columns={"l1_name": "name"}))
    with pytest.raises(SwPitIntegrityError, match="in_date/out_date"):
        A.normalize_sw_l1_layout(SW.drop(columns=["out_date"]))


def test_clean_schema_mismatch_raises():
    ok = _clean_layout(SW6)
    for bad in (ok.drop(columns=["revision"]), ok.assign(extra=1), ok.assign(revision=ok["revision"].astype(str)),
                ok.assign(in_date=ok["in_date"].astype("datetime64[ns]"))):
        with pytest.raises(SwPitIntegrityError, match="schema != expected"):
            A.normalize_sw_l1_layout(bad)


# r3c: raw-table spelling T00018 and case variants of Tsh.00018 are NOT known (exact match only) -> raise
@pytest.mark.parametrize("bad_id", ["T00018", "TSH.00018", "tsh.00018", "Tsz.00018", "sh.60000", None, "801010.SI",
                                    "600000.SS"])
def test_clean_unknown_id_format_raises(bad_id):
    d = _clean_frame(["sz.000001", bad_id], ["银行", "银行"], ["2020-01-02"] * 2, [None] * 2, ["Y"] * 2)
    with pytest.raises(SwPitIntegrityError, match="whitelist"):
        A.normalize_sw_l1_layout(d)


def _clean_root(tmp_path, metrics_override=None, fetch_time="2026-10-10T10:01:23.213525-04:00"):
    fp = tmp_path / A.SW_L1_REL
    fp.parent.mkdir(parents=True)
    _clean_layout(SW6).to_parquet(fp, index=False)
    sw = A.load_sw_l1(tmp_path)
    metrics = {"rows": len(SW6), "n_instruments": int(SW6["ts_code"].nunique()), "in_date_min": "2018-01-01",
               "in_date_max": "2025-03-18", "n_l1": 1, "available_at_nulls": 0,  # r3d: constant fixture sw_code
               **(metrics_override or {})}
    man = {"rows": 7115, "fetch_time": fetch_time,
           "tushare_candidate": {"path": str(fp), "promotion_approved": True, "metrics": metrics}}
    (tmp_path / A.SW_L1_CLEAN_MANIFEST_REL).write_text(json.dumps(man), encoding="utf-8")
    return sw


def test_sw_l1_table_check_clean_manifest(tmp_path):
    A._reset_table_checks_for_tests()
    sw = _clean_root(tmp_path)
    now = dt.datetime(2026, 10, 12, 7, 0, tzinfo=A._ET)  # Mon 19:00 SH -> ref 10-12; fetch Sat 22:01 SH -> cov 10-09
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now)
    assert r["coverage_day"] == "2026-10-09" and r["ref_day"] == "2026-10-12" and r["lag_tdays"] == 1
    assert r["warns"] == [] and r["stale"] is False and r["sha256"] == sw.attrs["sha256"]
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-12", CAL, now_et=now + dt.timedelta(days=3))  # Thu: lag 4
    assert r["stale"] and any(w.startswith("coverage_gap") for w in r["warns"])
    assert "lag_tdays=4 (<= 10: not stale)" in r["lag_notes"] and r["stale_lag_only"] is False  # r3c: lag <= 10 = note
    assert r["n_calls"] == 2 and A.sw_l1_table_check_last(sw.attrs["path"]) is r
    other = tmp_path / "other.parquet"  # a file the manifest does not describe -> disclosed as unchecked
    _clean_layout(SW6).to_parquet(other, index=False)
    r = A.sw_l1_table_check(tmp_path, A.load_sw_l1(tmp_path, path=other), "2026-10-09", CAL, now_et=now)
    assert r["stale"] and r["check"].startswith("none")
    A._reset_table_checks_for_tests()


@pytest.mark.parametrize("override, fetch, match", [({"rows": 999}, None, "metrics != table"),
                                                    ({"in_date_max": "2026-09-24"}, None, "metrics != table"),
                                                    (None, "not-a-time", "fetch_time")])
def test_sw_l1_table_check_clean_integrity_raises(tmp_path, override, fetch, match):
    A._reset_table_checks_for_tests()
    sw = _clean_root(tmp_path, override, fetch or "2026-10-10T10:01:23.213525-04:00")
    with pytest.raises(SwPitIntegrityError, match=match):
        A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=dt.datetime(2026, 10, 12, 7, tzinfo=A._ET))
    (tmp_path / A.SW_L1_CLEAN_MANIFEST_REL).write_text("{", encoding="utf-8")
    with pytest.raises(SwPitIntegrityError, match="manifest unreadable"):
        A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=dt.datetime(2026, 10, 12, 7, tzinfo=A._ET))


def _clean_root_frame(tmp_path, frame, metrics):
    fp = tmp_path / A.SW_L1_REL
    fp.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(fp, index=False)
    sw = A.load_sw_l1(tmp_path)
    man = {"rows": 7115, "fetch_time": "2026-10-10T10:01:23.213525-04:00",
           "tushare_candidate": {"path": str(fp), "promotion_approved": True, "metrics": metrics}}
    (tmp_path / A.SW_L1_CLEAN_MANIFEST_REL).write_text(json.dumps(man), encoding="utf-8")
    return sw


@pytest.mark.parametrize("key, bad", [("n_l1", 2), ("available_at_nulls", 0)])
def test_clean_manifest_n_l1_and_available_at_nulls(tmp_path, key, bad):
    # r3d (Arch 11:29 ET ②), Data §14② L42-49: n_l1 = nunique(sw_code), available_at_nulls = null count, both on the
    # raw table BEFORE the non-A exclusion (Tsh.00018 row carries the 3rd sw_code and the only null available_at, so
    # the after-exclusion values 2 / 0 must fail). Values are read from manifest tushare_candidate.metrics.
    d = _clean_frame(["sz.000001", "sh.600000", "sh.600001", "Tsh.00018"], ["银行", "银行", "电子", "综合"],
                     ["2020-01-02"] * 4, [None] * 4, ["Y"] * 4)
    d["sw_code"] = pd.Series(["801780.SI", "801780.SI", "801080.SI", "801230.SI"], dtype="str")
    d["available_at"] = d["available_at"].where(d.index != 3).astype("datetime64[us]")
    good = {"rows": 4, "n_instruments": 4, "in_date_min": "2020-01-02", "in_date_max": "2020-01-02", "n_l1": 3,
            "available_at_nulls": 1}
    now = dt.datetime(2026, 10, 12, 7, tzinfo=A._ET)
    A._reset_table_checks_for_tests()
    sw = _clean_root_frame(tmp_path, d, good)  # consistent -> passes
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now)
    assert r["metrics"]["n_l1"] == 3 and r["metrics"]["available_at_nulls"] == 1 and r["stale"] is False
    A._reset_table_checks_for_tests()
    sw = _clean_root_frame(tmp_path, d, dict(good, **{key: bad}))  # inconsistent -> raises
    with pytest.raises(SwPitIntegrityError, match=f"metrics != table.*{key}"):
        A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now)
    sw = _clean_root_frame(tmp_path, d, {k: v for k, v in good.items() if k != key})  # key missing -> raises too
    with pytest.raises(SwPitIntegrityError, match=f"metrics != table.*{key}"):
        A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now)
    A._reset_table_checks_for_tests()


# ---- r3c (Arch 016ae55e P3s + Arch 11:11 ET rulings) ----
# M: two old rows, both out 2025-03-10 (Mon), no successor -> 2025-03-11 has TWO gap-carry candidates (P3-1)
SW_M = pd.DataFrame({"ts_code": ["M.SZ", "M.SZ"], "l1_name": ["电子", "通信"], "in_date": ["20200101", "20210101"],
                     "out_date": ["20250310", "20250310"], "is_new": ["N", "N"]})


def test_gap_carry_multi_candidate_raise_and_count():
    sw2 = pd.concat([SW, SW_M], ignore_index=True)
    assert _q([("M.SZ", "2025-03-11")], sw=sw2) == [None]  # pure rule: nothing active, no raise
    with pytest.raises(SwPitIntegrityError, match=r"gap carry.*M\.SZ"):
        _q([("M.SZ", "2025-03-11")], carry=True, sw=sw2)  # default on_overlap="raise"
    st = {}
    got = _q([("M.SZ", "2025-03-11"), ("M.SZ", "2025-03-12"), ("G.SZ", "2025-03-11")], carry=True, sw=sw2, stats=st,
             on_overlap="count")
    assert got == ["通信", None, "电子"]  # fixed OVERLAP_TIEBREAK: latest in_date wins
    assert st["n_rows_gap_carry"] == 2 and st["n_rows_gap_carry_multi_candidate"] == 1
    assert st["n_codes_gap_carry_multi_candidate"] == 1
    assert st["gap_carry_multi_candidate_codes"] == [
        {"code": "M.SZ", "n_days": 1, "first_day": "2025-03-11", "last_day": "2025-03-11",
         "candidates": ["电子", "通信"], "chosen": ["通信"], "conflict": True}]
    assert st["n_codes_overlap_on_d"] == 0  # not mixed into the active-row overlap list
    ia = A.IndustryAsOf(sw2, cal=CAL, on_overlap="count")
    req = A.sw_pit_required(ia, ia.reclass_share(_k([("M.SZ", "2025-03-11")])))
    assert req["n_gap_carry_multi_candidate_codes"] == 1 and req["gap_carry_multi_candidate_codes"][0]["code"] == "M.SZ"
    with pytest.raises(SwPitIntegrityError, match="gap carry"):
        A.IndustryAsOf(sw2, cal=CAL).by_session(_k([("M.SZ", "2025-03-11")]))


def test_exact_duplicate_rows_dropped_and_counted():
    dup = SW[SW["ts_code"] == "Y.SH"]
    sw2 = pd.concat([SW, dup, dup], ignore_index=True)
    p = A.prep_sw(sw2)
    ps = p.attrs["prep_stats"]
    assert ps["n_rows_exact_duplicate_dropped"] == 2 and ps["n_rows"] == len(SW) + 2 and len(p) == len(SW)
    assert int((p["ts_code"] == "Y.SH").sum()) == 1  # one copy kept (identical contents)
    assert A.prep_sw(SW).attrs["prep_stats"]["n_rows_exact_duplicate_dropped"] == 0
    assert _q([("Y.SH", "2025-01-02")], sw=sw2) == ["银行"]  # default raise: exact duplicates no longer raise
    near = dup.assign(is_new="N")  # same l1_name but not identical (is_new differs) -> still an overlap
    with pytest.raises(SwPitIntegrityError, match=r"Y\.SH"):
        _q([("Y.SH", "2025-01-02")], sw=pd.concat([SW, near], ignore_index=True))
    ia = A.IndustryAsOf(sw2, cal=CAL, on_overlap="count")
    rs = ia.reclass_share(_k([("Y.SH", "2025-01-02")]))
    assert rs["n_rows_exact_duplicate_dropped_table"] == 2 and rs["n_codes_overlap_on_d"] == 0
    assert A.sw_pit_required(ia, rs)["n_rows_exact_duplicate_dropped"] == 2


def test_in_after_out_rows_counted_never_active():
    bad = pd.DataFrame({"ts_code": ["R.SZ"], "l1_name": ["电子"], "in_date": ["20250310"], "out_date": ["20250301"],
                        "is_new": ["N"]})
    sw2 = pd.concat([SW, bad], ignore_index=True)
    assert A.prep_sw(sw2).attrs["prep_stats"]["n_rows_in_after_out"] == 1
    assert A.prep_sw(SW).attrs["prep_stats"]["n_rows_in_after_out"] == 0
    assert _q([("R.SZ", "2025-03-05"), ("R.SZ", "2025-03-11")], carry=True, sw=sw2) == [None, None]
    ia = A.IndustryAsOf(sw2, cal=CAL)
    rs = ia.reclass_share(_k([("Y.SH", "2025-01-02")]))
    assert rs["n_rows_in_after_out_table"] == 1 and A.sw_pit_required(ia, rs)["n_rows_in_after_out"] == 1


def test_key_limit_param_and_whole_session_chunking():
    sw = A.prep_sw(SW)
    codes = sorted(set(SW["ts_code"]))  # 9 codes -> 9 keys per session
    days = ("2025-03-07", "2025-03-10", "2025-03-11", "2025-03-18")
    keys = _k([(c, d) for d in days for c in codes])
    assert A.MAX_KEYS_PER_CALL == 1_000_000
    st1 = {}
    one = A.sw_l1_asof_chunked(sw, keys, stats=st1, cal=CAL, on_overlap="count")  # default limit -> 1 chunk
    assert st1["n_chunks"] == 1
    with pytest.raises(SwPitIntegrityError, match="max_keys=10"):
        A.sw_l1_asof_with_gap_carry(sw, keys, cal=CAL, on_overlap="count", max_keys=10)
    with pytest.raises(SwPitIntegrityError, match="max_keys=10"):
        A.l1_asof(sw, keys, on_overlap="count", max_keys=10)
    st2 = {}
    two = A.sw_l1_asof_chunked(sw, keys, stats=st2, cal=CAL, on_overlap="count", max_keys=10)
    assert two.tolist() == one.tolist() and list(two.index) == list(keys.index) and st2["n_chunks"] == 4
    for k in ("n_rows_multi_match", "n_codes_overlap_on_d", "overlap_codes", "n_rows_gap_carry", "n_rows_unknown",
              "n_rows_gap_carry_no_successor", "n_codes_gap_carry_multi_candidate", "gap_carry_multi_candidate_codes",
              "trade_cal_sha256", "on_overlap"):
        assert st2[k] == st1[k], k
    st3 = {}
    assert A.sw_l1_asof_chunked(sw, keys, stats=st3, cal=CAL, on_overlap="count", max_keys=18).tolist() == one.tolist()
    assert st3["n_chunks"] == 2  # two whole sessions per chunk
    # whole sessions by PARSED day: the same day written two ways stays in one chunk (9 keys each -> 4 chunks of 9)
    mixed = keys.assign(session=[s if i % 2 else f"{s} 00:00:00" for i, s in enumerate(keys["session"])])
    st4 = {}
    assert A.sw_l1_asof_chunked(sw, mixed, stats=st4, cal=CAL, on_overlap="count", max_keys=9).tolist() == one.tolist()
    assert st4["n_chunks"] == 4
    with pytest.raises(SwPitIntegrityError, match="alone has 9 keys > max_keys=8"):  # one session over the limit
        A.sw_l1_asof_chunked(sw, keys, cal=CAL, on_overlap="count", max_keys=8)
    with pytest.raises(SwPitIntegrityError, match=r"O\.SZ"):  # "raise" mode decided per chunk
        A.sw_l1_asof_chunked(sw, keys, cal=CAL, max_keys=10)
    for bad in (0, -1, True, 2.5, "10", None):
        with pytest.raises(ValueError, match="max_keys"):
            A.sw_l1_asof_chunked(sw, keys, cal=CAL, max_keys=bad)
        with pytest.raises(ValueError, match="max_keys"):
            A.l1_asof(sw, keys, max_keys=bad)
        with pytest.raises(ValueError, match="max_keys"):
            A.IndustryAsOf(SW, cal=CAL, max_keys=bad)
    ia = A.IndustryAsOf(SW, cal=CAL, on_overlap="count", max_keys=10)
    assert ia.max_keys == 10 and ia.reclass_share(keys)["n_chunks"] == 4
    assert ia.by_session(keys) == A.IndustryAsOf(SW, cal=CAL, on_overlap="count").by_session(keys)


def test_sw_l1_table_check_clean_lag_thresholds(tmp_path):
    # Arch 11:13 + 11:20 ET (merged reading): lag <= 10 -> not stale, not stale_lag_only, days in lag_notes only;
    # lag > 10 without coverage_gap -> stale + stale_lag_only; coverage_gap -> stale, never stale_lag_only.
    assert A.CLEAN_STALE_LAG_TDAYS == 10 and not hasattr(A, "CLEAN_LAG_DISCLOSE_TDAYS")
    A._reset_table_checks_for_tests()
    sw = _clean_root(tmp_path)
    now = dt.datetime(2026, 10, 18, 11, 0, tzinfo=A._ET)  # SH Sun 23:00 -> ref 10-16; cov 10-09: lag 5 (§14②)
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now)
    assert r["lag_tdays"] == 5 and r["stale"] is False and r["stale_lag_only"] is False
    assert r["warns"] == [] and r["stale_reasons"] == [] and r["lag_notes"] == ["lag_tdays=5 (<= 10: not stale)"]
    assert r["disclosure_zh"] == ""
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-12", CAL, now_et=now)  # + coverage gap -> always stale
    assert r["stale"] is True and r["stale_reasons"] == ["coverage_gap"] and r["stale_lag_only"] is False
    assert "查询日晚于表覆盖日" in r["disclosure_zh"] and "lag_tdays=5 (<= 10: not stale)" in r["disclosure_zh"]
    A._reset_table_checks_for_tests()
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL,
                            now_et=dt.datetime(2026, 10, 23, 7, 0, tzinfo=A._ET))  # Fri 19:00 SH -> lag 10
    assert r["lag_tdays"] == 10 and r["stale"] is False and r["stale_lag_only"] is False and r["disclosure_zh"] == ""
    A._reset_table_checks_for_tests()
    now11 = dt.datetime(2026, 10, 26, 7, 0, tzinfo=A._ET)  # Mon 19:00 SH -> lag 11
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-09", CAL, now_et=now11)
    assert r["lag_tdays"] == 11 and r["stale"] is True and r["stale_reasons"] == ["lag"] and r["stale_lag_only"] is True
    assert r["warns"] == ["lag_tdays=11>10"] and r["lag_notes"] == [] and "stale_lag_only=True" in r["disclosure_zh"]
    assert "未超出覆盖日" in r["disclosure_zh"]
    r = A.sw_l1_table_check(tmp_path, sw, "2026-10-12", CAL, now_et=now11)  # lag 11 + coverage gap
    assert r["stale"] is True and r["stale_reasons"] == ["lag", "coverage_gap"] and r["stale_lag_only"] is False
    A._reset_table_checks_for_tests()


def test_tsh00018_excluded_exactly_never_normalised():
    # Arch 11:20 ET ①: 'Tsh.00018' (exact, after strip) is excluded + counted; it must not become 600018 / 000018
    d = _clean_frame(["Tsh.00018", "sh.600018", "sz.000018", " Tsh.00018 "], ["综合", "钢铁", "银行", "综合"],
                     ["2020-01-02"] * 4, [None] * 4, ["Y"] * 4)
    out, info = A.normalize_sw_l1_layout(d)
    assert out["ts_code"].tolist() == ["600018.SH", "000018.SZ"] and out["l1_name"].tolist() == ["钢铁", "银行"]
    assert info["n_rows_non_a_share_excluded"] == 2 and sorted(info["non_a_share_excluded"]) == [" Tsh.00018 ",
                                                                                                "Tsh.00018"]
    assert info["raw"]["rows"] == 4 and "综合" not in set(out["l1_name"])
    assert A.NON_A_SHARE_KNOWN == ("Tsh.00018",)
    assert A._norm_a_share(pd.Series(["Tsh.00018"])).tolist() == [None]  # never mapped to any A-share code
    sw = A.prep_sw(out)
    got = A.l1_asof(sw, _k([("600018.SH", "2025-01-02"), ("000018.SZ", "2025-01-02"), ("Tsh.00018", "2025-01-02")]))
    assert got.tolist() == ["钢铁", "银行", None]


def test_us_ns_precision_equivalent():
    # Arch 11:20 ET ③: one side [us], the other [ns] (sw dates and/or keys) -> identical answers; both cast to [us]
    days = ("2025-03-07", "2025-03-10", "2025-03-11", "2025-03-18")
    pairs = [(c, d) for c in sorted(set(SW["ts_code"])) for d in days]
    base_carry = A.sw_l1_asof_with_gap_carry(A.prep_sw(SW), _k(pairs), cal=CAL, on_overlap="count").tolist()
    base_pure = A.l1_asof(A.prep_sw(SW), _k(pairs), on_overlap="count").tolist()
    assert A.TS_UNIT == "datetime64[us]" and str(CAL.open_days.dtype) == "datetime64[us]"
    for unit in ("datetime64[ns]", "datetime64[us]"):
        swu = SW.assign(in_date=pd.to_datetime(SW["in_date"]).astype(unit),
                        out_date=pd.to_datetime(SW["out_date"]).astype(unit))
        p = A.prep_sw(swu)
        assert str(p["in_date"].dtype) == "datetime64[us]" and str(p["out_date"].dtype) == "datetime64[us]"
        for kunit in ("datetime64[ns]", "datetime64[us]"):
            k = _k(pairs)
            k["session"] = pd.to_datetime(k["session"]).astype(kunit)
            assert A.sw_l1_asof_with_gap_carry(p, k, cal=CAL, on_overlap="count").tolist() == base_carry, (unit, kunit)
            assert A.l1_asof(p, k, on_overlap="count").tolist() == base_pure, (unit, kunit)
            assert A.sw_l1_asof_chunked(p, k, cal=CAL, on_overlap="count", max_keys=9).tolist() == base_carry
    pn = A.prep_sw(SW)  # prepared frame whose dates were re-cast to [ns] afterwards: l1_asof casts again
    pn["in_date"], pn["out_date"] = pn["in_date"].astype("datetime64[ns]"), pn["out_date"].astype("datetime64[ns]")
    assert A.sw_l1_asof_with_gap_carry(pn, _k(pairs), cal=CAL, on_overlap="count").tolist() == base_carry
    assert CAL.prev_open(pd.Series(pd.to_datetime(["2025-03-18"])).astype("datetime64[ns]").to_numpy()).dtype == \
        CAL.prev_open(pd.Series(pd.to_datetime(["2025-03-18"])).astype("datetime64[us]").to_numpy()).dtype


# C: same code + same in_date, different l1_name (both out 2025-03-10) — a CONFLICT, never silently picked
SW_C = pd.DataFrame({"ts_code": ["C.SZ", "C.SZ"], "l1_name": ["电子", "通信"], "in_date": ["20200101", "20200101"],
                     "out_date": ["20250310", "20250310"], "is_new": ["N", "N"]})


def test_same_in_date_different_name_is_conflict():
    sw2 = pd.concat([SW, SW_C], ignore_index=True)
    ps = A.prep_sw(sw2).attrs["prep_stats"]
    assert ps["n_codes_same_in_date_conflict"] == 2 and ps["same_in_date_conflict_codes"] == ["C.SZ", "T.SZ"]
    assert A.prep_sw(SW).attrs["prep_stats"]["same_in_date_conflict_codes"] == ["T.SZ"]
    with pytest.raises(SwPitIntegrityError, match=r"C\.SZ"):  # active day, default raise
        _q([("C.SZ", "2025-01-02")], sw=sw2)
    st = {}
    assert _q([("C.SZ", "2025-01-02")], sw=sw2, stats=st, on_overlap="count") == ["通信"]  # fixed tie order
    assert st["overlap_codes"] == [{"code": "C.SZ", "n_days": 1, "first_day": "2025-01-02", "last_day": "2025-01-02",
                                    "candidates": ["电子", "通信"], "chosen": ["通信"], "conflict": True}]
    with pytest.raises(SwPitIntegrityError, match="gap carry"):  # gap-carry day: both rows are candidates
        _q([("C.SZ", "2025-03-11")], carry=True, sw=sw2)
    st = {}
    _q([("C.SZ", "2025-03-11")], carry=True, sw=sw2, stats=st, on_overlap="count")
    g = st["gap_carry_multi_candidate_codes"]
    assert [e["code"] for e in g] == ["C.SZ"] and g[0]["conflict"] is True
    sw3 = pd.concat([SW, SW_C.iloc[[0]], SW_C.iloc[[0]]], ignore_index=True)  # exact duplicate: NOT a conflict
    ps3 = A.prep_sw(sw3).attrs["prep_stats"]
    assert ps3["n_rows_exact_duplicate_dropped"] == 1 and ps3["same_in_date_conflict_codes"] == ["T.SZ"]
    assert _q([("C.SZ", "2025-01-02")], sw=sw3) == ["电子"]
    ia = A.IndustryAsOf(sw2, cal=CAL, on_overlap="count")
    req = A.sw_pit_required(ia, ia.reclass_share(_k([("Y.SH", "2025-01-02")])))
    assert req["n_codes_same_in_date_conflict"] == 2 and req["same_in_date_conflict_codes"] == ["C.SZ", "T.SZ"]


_NOW_OK = dt.datetime(2026, 10, 18, 11, 0, tzinfo=A._ET)
_GOOD_OK = ("# Arch run .ok (synthetic)\nallow_pitfix_compare=true\nlive=false\npromotion = false\n"
            "expires_et=2026-10-19T16:00:00-04:00\nnote: free text is ignored\n")


def _ok_file(tmp_path, text, rel="a.ok"):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_check_allow_ok_valid(tmp_path):
    p = _ok_file(tmp_path, _GOOD_OK)
    r = A.check_allow_ok(p, "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)
    assert r["ok_sha256"] == hashlib.sha256(p.read_bytes()).hexdigest() and r["field"] == "allow_pitfix_compare"
    assert r["expires_et"] == "2026-10-19T16:00:00-04:00" and r["ok_path"] == str(p.resolve())
    r2 = A.check_allow_ok("a.ok", "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)  # relative to root
    assert r2["ok_path"] == str(p.resolve())


@pytest.mark.parametrize("old, new, match", [
    ("allow_pitfix_compare=true", "allow_pitfix_compare: true", "colon form"),
    ("allow_pitfix_compare=true", "pitfix_compare_allowed=true", "allow_pitfix_compare=true"),
    ("allow_pitfix_compare=true", "allow_pitfix_compare=True", "allow_pitfix_compare=true"),
    ("live=false", "live=true", "live=false"),
    ("promotion = false\n", "", "promotion=false"),
    ("note: free text is ignored\n", "live=false\n", "more than once"),
    ("2026-10-19T16:00:00-04:00", "2026-10-18T10:59:59-04:00", "expired"),
    ("2026-10-19T16:00:00-04:00", "2026-10-19T16:00:00", "UTC offset"),
    ("expires_et=2026-10-19T16:00:00-04:00\n", "", "expires_et"),
    ("expires_et=2026-10-19T16:00:00-04:00", "expires_et: 2026-10-19T16:00:00-04:00", "colon form"),
])
def test_check_allow_ok_rejects(tmp_path, old, new, match):
    assert old in _GOOD_OK
    p = _ok_file(tmp_path, _GOOD_OK.replace(old, new))
    with pytest.raises(SystemExit, match=match):
        A.check_allow_ok(p, "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)


def test_check_allow_ok_file_rules(tmp_path):
    with pytest.raises(SystemExit, match="not a file"):
        A.check_allow_ok(tmp_path / "missing.ok", "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)
    with pytest.raises(SystemExit, match="_consumed"):
        A.check_allow_ok(_ok_file(tmp_path, _GOOD_OK, "_consumed/a.ok"), "allow_pitfix_compare", root=tmp_path,
                         now_et=_NOW_OK)
    bad = tmp_path / "latin1.ok"
    bad.write_bytes(b"allow_pitfix_compare=true\n\xff\n")
    with pytest.raises(SystemExit, match="UTF-8"):
        A.check_allow_ok(bad, "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)


@pytest.mark.parametrize("rel, extra", [("a.ok.draft", None), ("ARCH_PITFIX_DRAFT.ok", None), ("a_Draft.ok", None),
                                        ("a.ok", "# DRAFT — not signed\n"), ("a.ok", "status=draft\n")])
def test_check_allow_ok_rejects_draft(tmp_path, rel, extra):
    # Arch 11:11 ET ③: DRAFT in the file name (incl. .ok.draft) or anywhere in the content -> rejected
    p = _ok_file(tmp_path, _GOOD_OK + (extra or ""), rel)
    with pytest.raises(SystemExit, match="DRAFT"):
        A.check_allow_ok(p, "allow_pitfix_compare", root=tmp_path, now_et=_NOW_OK)


# ---- r3e (Arch 2026-10-18 12:09 ET): missing -> real None on every public exit; P2-2 as_of parsed to Timestamp ----
def _assert_none_missing(s, expected):
    # explicit: object dtype, element-wise `is None` for missing, non-missing values unchanged
    assert isinstance(s, pd.Series) and s.dtype == object, (type(s), getattr(s, "dtype", None))
    got = s.tolist()
    assert len(got) == len(expected)
    for g, e in zip(got, expected):
        if e is None:
            assert g is None, f"missing must be None, got {g!r}"
        else:
            assert isinstance(g, str) and g == e


def test_r3e_missing_is_none_on_every_public_exit():
    _assert_none_missing(A._norm_a_share(pd.Series(["Tsh.00018", "sh.600018", "000001.sz", "bad", None])),
                         [None, "600018.SH", "000001.SZ", None, None])
    _assert_none_missing(A._norm_a_share(pd.Series(["Tsh.00018"])), [None])  # all-missing
    _assert_none_missing(A._none_for_missing(pd.Series(["a", None, float("nan")], dtype="str")), ["a", None, None])
    sw = A.prep_sw(SW)
    k = _k([("X.SZ", "2025-03-10"), ("NOPE.SZ", "2025-03-10"), ("Z.SH", "2025-03-11"), ("H.SZ", "2025-03-11")])
    _assert_none_missing(A.l1_asof(sw, k), ["电子", None, None, None])
    _assert_none_missing(A.l1_asof(sw, _k([("NOPE.SZ", "2025-03-10")])), [None])  # all-missing
    _assert_none_missing(A.l1_asof(sw, _k([])), [])  # empty
    st: dict = {}
    _assert_none_missing(A.sw_l1_asof_with_gap_carry(sw, k, stats=st, cal=CAL), ["电子", None, "医药生物", None])
    assert st["n_rows_unknown"] == 2
    kc = _k([("X.SZ", "2025-03-10"), ("NOPE.SZ", "2025-03-11"), ("H.SZ", "2025-03-11"), ("G.SZ", "2025-03-12"),
             ("NOPE.SZ", "2025-03-12")])
    one = A.sw_l1_asof_with_gap_carry(sw, kc, cal=CAL).tolist()
    st = {}
    ch = A.sw_l1_asof_chunked(sw, kc, stats=st, cal=CAL, max_keys=2)
    assert st["n_chunks"] == 3 and ch.tolist() == one
    _assert_none_missing(ch, ["电子", None, None, "计算机", None])
    st = {}
    _assert_none_missing(A.sw_l1_asof_chunked(sw, kc, stats=st, cal=CAL), ["电子", None, None, "计算机", None])
    assert st["n_chunks"] == 1
    ia = A.IndustryAsOf(SW, cal=CAL)
    bs = ia.by_session(kc)
    assert all(isinstance(v, str) for m in bs.values() for v in m.values())  # missing codes dropped, never nan
    assert bs["2025-03-10"] == {"X.SZ": "电子"} and bs["2025-03-12"] == {"G.SZ": "计算机"}
    rs = ia.reclass_share(kc)
    assert rs["n_rows_asof_missing"] == 3 and rs["n_rows_unknown"] == 3
    d = _clean_frame(["Tsh.00018", "sh.600018", "sz.000018"], ["综合", "钢铁", "银行"], ["2020-01-02"] * 3,
                     [None] * 3, ["Y"] * 3)
    out, _ = A.normalize_sw_l1_layout(d)
    _assert_none_missing(out["ts_code"], ["600018.SH", "000018.SZ"])
    _assert_none_missing(out["l1_name"], ["钢铁", "银行"])


def test_r3e_table_check_as_of_yyyymmdd_equals_iso(tmp_path):
    # P2-2: as_of parsed to a TS_UNIT Timestamp before comparing; r3d compared strings ('20261009' > '2026-10-09')
    sw = _clean_root(tmp_path)
    now = dt.datetime(2026, 10, 12, 7, 0, tzinfo=A._ET)  # coverage_day 2026-10-09 (see test above)
    res = {}
    for a in ("20261009", "2026-10-09", pd.Timestamp("2026-10-09"), dt.date(2026, 10, 9), "2026-10-09 15:00:00"):
        A._reset_table_checks_for_tests()
        r = A.sw_l1_table_check(tmp_path, sw, a, CAL, now_et=now)
        assert r["coverage_day"] == "2026-10-09" and r["as_of"] == "2026-10-09"
        assert r["stale"] is False and r["warns"] == [] and r["stale_reasons"] == []  # no false coverage_gap
        res[str(a)] = {k: v for k, v in r.items() if k != "checked_at_et"}
    assert len({json.dumps(v, sort_keys=True, default=str) for v in res.values()}) == 1  # identical results
    for a in ("20261012", "2026-10-12"):  # a real gap is still reported in both formats
        A._reset_table_checks_for_tests()
        r = A.sw_l1_table_check(tmp_path, sw, a, CAL, now_et=now)
        assert r["as_of"] == "2026-10-12" and r["stale_reasons"] == ["coverage_gap"]
    A._reset_table_checks_for_tests()  # aggregation keeps the LATEST as_of across mixed formats
    A.sw_l1_table_check(tmp_path, sw, "2026-10-12", CAL, now_et=now)
    r = A.sw_l1_table_check(tmp_path, sw, "20261009", CAL, now_et=now)
    assert r["as_of"] == "2026-10-12" and r["n_calls"] == 2
    for bad in ("not-a-date", ""):
        with pytest.raises(SwPitIntegrityError, match="as_of"):
            A.sw_l1_table_check(tmp_path, sw, bad, CAL, now_et=now)
    A._reset_table_checks_for_tests()
