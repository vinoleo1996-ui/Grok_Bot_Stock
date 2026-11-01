"""EOD 18:00 float-cap proxy. The raw file stays without available_at."""
from datetime import date

import pandas as pd
import pytest

from quantlab.data.v2_readers import (
    DEFAULT_FLOAT_MKTCAP_PIT,
    FLOAT_MKTCAP_EOD18_REVISION,
    float_mktcap_lookup_for_session,
    materialize_float_mktcap_daily_pit,
)


def _raw(path):
    pd.DataFrame({
        "instrument_id": ["sh.600000", "sh.600000"],
        "trade_date": ["20240603", "20240604"],
        "float_mktcap": [10.0, 20.0],
        "promotion_approved": [False, False],
    }).to_parquet(path, index=False)


def test_materialize_writes_a_new_file_and_leaves_the_source(tmp_path):
    source = tmp_path / "float_mktcap_daily_tushare.parquet"
    dest = tmp_path / "float_mktcap_daily_tushare_pit.parquet"
    _raw(source)
    written = materialize_float_mktcap_daily_pit(source, dest)
    assert written == dest
    assert "available_at" not in pd.read_parquet(source).columns
    pit = pd.read_parquet(dest)
    assert list(pit["revision"].unique()) == [FLOAT_MKTCAP_EOD18_REVISION]
    assert not bool(pit["promotion_approved"].any())
    stamp = pit["available_at"].iloc[0]
    assert stamp.tzinfo is not None
    assert stamp.tz_convert("Asia/Shanghai").hour == 18
    with pytest.raises(ValueError, match="overwrite"):
        materialize_float_mktcap_daily_pit(source, source)


def test_close_decision_sees_same_day_18_00_and_open_decision_does_not(tmp_path):
    source = tmp_path / "raw.parquet"
    dest = tmp_path / "pit.parquet"
    _raw(source)
    materialize_float_mktcap_daily_pit(source, dest)
    close = float_mktcap_lookup_for_session(date(2024, 6, 4), asof_path=dest, known_by="close")
    opened = float_mktcap_lookup_for_session(date(2024, 6, 4), asof_path=dest, known_by="open")
    assert close.values["sh.600000"] == 20.0
    assert opened.values["sh.600000"] == 10.0
    assert FLOAT_MKTCAP_EOD18_REVISION in close.notes


def test_raw_file_without_available_at_still_fails(tmp_path):
    source = tmp_path / "float_mktcap_daily_tushare.parquet"
    _raw(source)
    with pytest.raises(ValueError, match="available_at_missing"):
        float_mktcap_lookup_for_session(date(2024, 6, 4), asof_path=source)


def test_default_pit_name_is_not_the_raw_file():
    assert DEFAULT_FLOAT_MKTCAP_PIT.name != "float_mktcap_daily_tushare.parquet"


def test_missing_pit_does_not_fall_back_to_the_raw_table(tmp_path, monkeypatch):
    import quantlab.data.v2_readers as readers

    raw = tmp_path / "float_mktcap_daily_tushare.parquet"
    _raw(raw)
    monkeypatch.setattr(readers, "DEFAULT_FLOAT_MKTCAP", raw)
    monkeypatch.setattr(readers, "DEFAULT_FLOAT_MKTCAP_PIT", tmp_path / "float_mktcap_daily_tushare_pit.parquet")
    with pytest.raises(FileNotFoundError, match="float_mktcap_daily_tushare_pit"):
        readers.float_mktcap_lookup_for_session(date(2024, 6, 4))
