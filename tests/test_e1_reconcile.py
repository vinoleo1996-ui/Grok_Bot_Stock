"""E1 reconcile scaffold: loaders + report schema (synthetic only)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quantlab.platform.e1_reconcile import (
    DEFAULT_WEIGHTS_FILE,
    WEIGHT_FILE_ALIASES,
    WEIGHT_FILE_CANDIDATES,
    build_e1_report,
    discover_weights_path,
    ids_from_schedule,
    load_paper_nav,
    load_schedule,
    normalize_instrument_id,
    resolve_weights_filename,
    schedule_from_long,
    schedule_from_wide,
    synthetic_dry_run,
    write_e1_report,
)


def test_normalize_instrument_id_undotted_etf_and_stock():
    assert normalize_instrument_id("sh510300") == "sh.510300"
    assert normalize_instrument_id("sh600000") == "sh.600000"
    assert normalize_instrument_id("sz000001") == "sz.000001"
    assert normalize_instrument_id("bj430047") == "bj.430047"
    # already dotted / mixed case
    assert normalize_instrument_id("sh.510300") == "sh.510300"
    assert normalize_instrument_id("SH510300") == "sh.510300"
    assert normalize_instrument_id("Sz.000002") == "sz.000002"
    # unrelated passes through
    assert normalize_instrument_id("cash") == "cash"


def test_schedule_from_wide_and_long():
    dates = pd.bdate_range("2026-01-05", periods=3)
    wide = pd.DataFrame({"sh.600001": [0.5, np.nan, 0.0], "sz.000002": [0.3, 0.4, 0.2]}, index=dates)
    s_w = schedule_from_wide(wide)
    assert set(s_w[dates[0]]) == {"sh.600001", "sz.000002"}
    assert "sh.600001" not in s_w[dates[1]]  # nan dropped
    long = pd.DataFrame({
        "session": [dates[0], dates[0], dates[1]],
        "instrument_id": ["sh.600001", "sz.000002", "sz.000002"],
        "weight": [0.5, 0.3, 0.4],
    })
    s_l = schedule_from_long(long)
    assert s_l[dates[0]]["sh.600001"] == pytest.approx(0.5)
    assert ids_from_schedule(s_l) == ["sh.600001", "sz.000002"]


def test_schedule_from_long_normalizes_undotted_etf():
    dates = pd.bdate_range("2026-01-05", periods=1)
    long = pd.DataFrame({
        "session": [dates[0], dates[0], dates[0]],
        "instrument_id": ["sh510300", "sh600000", "sz000001"],
        "weight": [0.5, 0.3, 0.2],
    })
    s = schedule_from_long(long)
    assert set(s[dates[0]]) == {"sh.510300", "sh.600000", "sz.000001"}
    assert s[dates[0]]["sh.510300"] == pytest.approx(0.5)


def test_resolve_weights_filename_and_arm():
    assert resolve_weights_filename(None) == "planned_target_weights.parquet"
    assert resolve_weights_filename("planned") == "planned_target_weights.parquet"
    assert resolve_weights_filename("actual") == "target_weights.parquet"
    assert resolve_weights_filename("arm_b") == "arm_b_target_weights.parquet"
    assert resolve_weights_filename("target_weights.parquet") == "target_weights.parquet"
    assert resolve_weights_filename("planned", arm="b") == "arm_b_target_weights.parquet"
    assert resolve_weights_filename(None, arm="B") == "arm_b_target_weights.parquet"
    assert DEFAULT_WEIGHTS_FILE == "planned_target_weights.parquet"
    assert WEIGHT_FILE_ALIASES["actual"] == "target_weights.parquet"


def test_load_schedule_prefers_planned_under_arm_dir(tmp_path: Path):
    arm = tmp_path / "arm_a_baseline_m01_ep"
    arm.mkdir()
    planned = pd.DataFrame({
        "session": ["2026-01-05", "2026-01-05"],
        "instrument_id": ["sh510300", "sh600000"],
        "weight": [0.5, 0.4],
    })
    actual = pd.DataFrame({
        "session": ["2026-01-05"],
        "instrument_id": ["sh510300"],
        "weight": [0.45],
    })
    planned.to_parquet(arm / "planned_target_weights.parquet", index=False)
    actual.to_parquet(arm / "target_weights.parquet", index=False)

    found = discover_weights_path(tmp_path, preferred="planned_target_weights.parquet")
    assert found == arm / "planned_target_weights.parquet"

    sched, meta = load_schedule(weights_dir=tmp_path)
    assert meta["weights_file"] == "planned_target_weights.parquet"
    assert meta["weights_file_resolved"] == "planned_target_weights.parquet"
    assert meta["n_signals"] == 1 and meta["n_codes"] == 2
    row = sched[pd.Timestamp("2026-01-05")]
    assert "sh.510300" in row and "sh.600000" in row
    assert row["sh.510300"] == pytest.approx(0.5)

    # actual file via alias
    sched_a, meta_a = load_schedule(weights_dir=tmp_path, weights_file="actual")
    assert meta_a["weights_file_resolved"] == "target_weights.parquet"
    assert sched_a[pd.Timestamp("2026-01-05")]["sh.510300"] == pytest.approx(0.45)


def test_load_schedule_arm_b_file(tmp_path: Path):
    arm_b = pd.DataFrame({
        "session": ["2026-01-05", "2026-01-05"],
        "instrument_id": ["sh510300", "sz000001"],
        "weight": [0.6, 0.3],
    })
    arm_b.to_parquet(tmp_path / "arm_b_target_weights.parquet", index=False)
    # also plant planned so default discovery would pick it if arm ignored
    pd.DataFrame({
        "session": ["2026-01-05"],
        "instrument_id": ["sh600000"],
        "weight": [1.0],
    }).to_parquet(tmp_path / "planned_target_weights.parquet", index=False)

    sched, meta = load_schedule(weights_dir=tmp_path, arm="b")
    assert meta["weights_file"] == "arm_b_target_weights.parquet"
    assert meta["weights_file_resolved"] == "arm_b_target_weights.parquet"
    row = sched[pd.Timestamp("2026-01-05")]
    assert set(row) == {"sh.510300", "sz.000001"}
    assert row["sh.510300"] == pytest.approx(0.6)


def test_load_schedule_json_and_paper_nav(tmp_path: Path):
    sched_path = tmp_path / "schedule.json"
    sched_path.write_text(json.dumps({"2026-01-05": {"sh510300": 0.5, "sh.600001": 0.3}}))
    sched, meta = load_schedule(weights_path=sched_path)
    assert meta["format"] == "json"
    row = sched[pd.Timestamp("2026-01-05")]
    assert "sh.510300" in row and "sh.600001" in row
    nav = pd.DataFrame({"date": ["2026-01-05", "2026-01-06"], "nav": [1.0, 1.01]})
    nav.to_csv(tmp_path / "nav.csv", index=False)
    s = load_paper_nav(weights_dir=tmp_path)
    assert s is not None and float(s.iloc[0]) == 1.0


def test_report_schema_and_dry_run(tmp_path: Path):
    result = synthetic_dry_run(tmp_path / "dry")
    summary = result["report"]["summary"]
    for k in ("reference", "first_divergence", "max_abs_diff", "max_abs_rel_diff",
              "effective_n_mean", "research_only", "promotion_approved", "exec_config",
              "units_note", "root_cause_notes"):
        assert k in summary
    assert summary["research_only"] is True
    assert summary["promotion_approved"] is False
    assert summary["n_sessions"] >= 1
    paths = result["paths"]
    assert Path(paths["summary_json"]).is_file()
    assert Path(paths["navs_csv"]).is_file()
    assert Path(paths["zh_md"]).is_file()
    # zero-cost engines should agree on synthetic
    assert summary["max_abs_rel_diff"] is not None
    assert float(summary["max_abs_rel_diff"]) < 1e-6 or summary["first_divergence"] is None


def test_weight_candidates_documented():
    assert "planned_target_weights.parquet" in WEIGHT_FILE_CANDIDATES
    assert WEIGHT_FILE_CANDIDATES[0] == "planned_target_weights.parquet"
    assert "target_weights.parquet" in WEIGHT_FILE_CANDIDATES
    assert "arm_b_target_weights.parquet" in WEIGHT_FILE_CANDIDATES
    assert "schedule.json" in WEIGHT_FILE_CANDIDATES


def test_reconcile_zero_cost_corporate_actions_toggle():
    """E1 smoke 2026-10-11: --corporate-actions off must switch all three engines to unadjusted."""
    from quantlab.platform.execution import ExecPanels, reconcile_zero_cost
    from quantlab.platform.e1_reconcile import _build_parser
    idx = pd.bdate_range("2024-06-03", periods=6)
    close = pd.DataFrame({"sz.000001": [10.0, 10.0, 9.5, 9.5, 9.6, 9.6]}, index=idx)
    vol = pd.DataFrame(1e9, index=idx, columns=close.columns)
    cd = pd.DataFrame(0.0, index=idx, columns=close.columns); cd.iloc[2, 0] = 0.5
    p = ExecPanels(close=close, open=close.copy(), volume=vol, amount=vol * close, cash_div=cd)
    sched = {idx[0]: {"sz.000001": 0.9}}
    off = reconcile_zero_cost(p, sched, initial_cash=100_000.0, corporate_actions=False)
    on = reconcile_zero_cost(p, sched, initial_cash=100_000.0, corporate_actions=True)
    for name in ("ledger", "fastsim"):
        assert off["diffs"][name]["max_abs_diff"] < 1e-6
    assert on["navs"]["platform"].iloc[-1] > off["navs"]["platform"].iloc[-1] + 1000
    assert _build_parser().parse_args(["--out", "x", "--corporate-actions", "off"]).corporate_actions == "off"


def test_with_costs_nav_below_zero_cost(tmp_path):
    import numpy as np
    import pandas as pd
    from quantlab.platform.e1_reconcile import run_e1
    from quantlab.platform.execution import ExecPanels
    idx = pd.bdate_range("2024-01-02", periods=30)
    cols = ["sh.600000", "sz.000001"]
    rng = np.random.default_rng(0)
    close = pd.DataFrame(10 * np.exp(np.cumsum(rng.normal(0, 0.01, (30, 2)), 0)), idx, cols)
    vol = pd.DataFrame(1e8, idx, cols)
    panels = ExecPanels(close=close, open=close.shift(1).fillna(close), volume=vol, amount=vol * close)
    sched = {idx[i]: ({cols[0]: 0.9} if i % 2 else {cols[1]: 0.9}) for i in range(0, 28, 3)}
    out = run_e1(schedule=sched, start=idx[0], end=idx[-1], out_dir=tmp_path, panels=panels,
                 with_costs=True, corporate_actions=False)
    navs = pd.read_csv(tmp_path / "e1_navs.csv", index_col=0)
    assert "platform_strategy_v1_costs" in navs.columns
    assert navs["platform_strategy_v1_costs"].iloc[-1] < navs["platform"].iloc[-1]
    wc = out["report"]["summary"]["with_costs"]
    assert wc["delta_vs_zero_cost"] < 0 and wc["total_cost_cny"] > 0


def test_float32_bonus_ratio_ledger_matches_platform():
    import numpy as np
    import pandas as pd
    from quantlab.platform.execution import ExecPanels, reconcile_zero_cost
    idx = pd.bdate_range("2024-01-02", periods=8)
    cols = ["sz.000001"]
    close = pd.DataFrame(10.0, idx, cols); close.iloc[4:] = 10.0 / 1.1 - 0.1
    sr = pd.DataFrame(0.0, idx, cols, dtype="float32"); sr.iloc[4] = np.float32(0.1)
    cd = pd.DataFrame(0.0, idx, cols, dtype="float32"); cd.iloc[4] = np.float32(0.1)
    vol = pd.DataFrame(1e8, idx, cols)
    panels = ExecPanels(close=close, open=close, volume=vol, amount=vol * close, cash_div=cd, share_ratio=sr)
    rec = reconcile_zero_cost(panels, {idx[0]: {cols[0]: 0.9}}, initial_cash=100_000.0, corporate_actions=True)
    n = rec["navs"]
    assert abs(n["ledger"].iloc[-1] - n["platform"].iloc[-1]) < 0.02
    assert abs(n["fastsim"].iloc[-1] - n["platform"].iloc[-1]) < 0.02
