"""Synthetic-only tests for cand4 CONDITION B box port (final-close fence / FIX_A).

No production market parquet is read. Fixtures live under TemporaryDirectory.
Arch ``.ok`` is not required for these research-grade unit tests.
"""
from __future__ import annotations

import unittest
from datetime import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from quantlab.agents.trading_loop import settle
from quantlab.agents.trading_loop.settle import (
    LIVE,
    PROMOTION_APPROVED,
    compute_horizon_returns,
)


def _write_etf(
    path: Path,
    rows: list[dict],
) -> Path:
    """Write a minimal etf_daily_adj-like parquet (synthetic)."""
    frame = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return path


def _bar(ts_code: str, day: str, close: float, available_at: str | None = None) -> dict:
    ymd = day.replace("-", "")
    row = {
        "ts_code": ts_code,
        "trade_date": ymd,
        "close": close,
    }
    if available_at is not None:
        row["available_at"] = available_at
    else:
        row["available_at"] = pd.NaT
    return row


class Guardrails(unittest.TestCase):
    def test_research_flags_remain_off(self):
        self.assertFalse(LIVE)
        self.assertFalse(PROMOTION_APPROVED)


class FinalCloseFenceBench(unittest.TestCase):
    def test_on_or_after_entry_contract_preserved(self):
        """Box callers depend on ON OR AFTER — session day may be entry."""
        with TemporaryDirectory() as tmp:
            etf = Path(tmp) / "etf.parquet"
            rows = []
            for code, base in (("510500.SH", 100.0), ("510300.SH", 10.0)):
                rows.extend(
                    [
                        _bar(code, "2026-01-05", base),
                        _bar(code, "2026-01-06", base * 1.1),
                        _bar(code, "2026-01-07", base * 1.21),
                        _bar(code, "2026-01-08", base * 1.331),
                    ]
                )
            _write_etf(etf, rows)
            out = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                2,
                etf_path=etf,
                allow_mock=False,
                now="2026-01-09 16:00:00+08:00",
            )
            self.assertEqual(out["status"], "settled")
            self.assertEqual(out["entry_date"], "2026-01-05")
            self.assertEqual(out["exit_date"], "2026-01-07")

    def test_today_still_trading_bench_bar_does_not_change_alpha(self):
        """Intraday fake today bench print must not leak into asof(exit)."""
        with TemporaryDirectory() as tmp:
            etf = Path(tmp) / "etf.parquet"
            rows = [
                _bar("510500.SH", "2026-01-05", 100.0),
                _bar("510500.SH", "2026-01-06", 110.0),
                _bar("510500.SH", "2026-01-07", 121.0),
                _bar("510500.SH", "2026-01-08", 133.1),
                _bar("510300.SH", "2026-01-05", 10.0),
                _bar("510300.SH", "2026-01-06", 10.0),
                _bar("510300.SH", "2026-01-07", 12.0),
                _bar("510300.SH", "2026-01-08", 999.0),  # live junk
            ]
            _write_etf(etf, rows)
            # horizon=1 → entry 01-05, exit 01-06; today 01-08 still trading
            # Actually with ON OR AFTER and horizon=1: entry=01-05, exit=index[1]=01-06
            # For the Origin-style case: entry next day... we keep on_or_after.
            # Use horizon=2: entry 01-05, exit 01-07. Today 01-08 14:00 — today's
            # 999 bench dropped; exit 01-07 priced at 12.
            out = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                2,
                etf_path=etf,
                allow_mock=False,
                now="2026-01-08 14:00:00+08:00",
                regular_close=time(15, 0),
            )
            self.assertEqual(out["status"], "settled")
            self.assertEqual(out["entry_date"], "2026-01-05")
            self.assertEqual(out["exit_date"], "2026-01-07")
            self.assertAlmostEqual(out["raw_return"], 121.0 / 100.0 - 1.0, places=8)
            self.assertAlmostEqual(out["bench_return"], 12.0 / 10.0 - 1.0, places=8)
            self.assertNotAlmostEqual(out["bench_return"], 999.0 / 10.0 - 1.0, places=2)
            self.assertAlmostEqual(
                out["alpha_vs_510300"],
                out["raw_return"] - out["bench_return"],
                places=8,
            )

    def test_available_at_after_now_on_exit_bench_forces_pending(self):
        """FIX_A: exit-day bench available_at > now → pending, no alpha.

        Instrument bars omit available_at so post-15:00 regular-close rule
        marks them final; only the matching bench exit bar is still gated.
        """
        with TemporaryDirectory() as tmp:
            etf = Path(tmp) / "etf.parquet"
            rows = [
                # instrument: no available_at → final after 15:00 regular close
                _bar("510500.SH", "2026-01-05", 100.0),
                _bar("510500.SH", "2026-01-06", 110.0),
                _bar("510500.SH", "2026-01-07", 121.0),
                _bar("510500.SH", "2026-01-08", 133.1),
                _bar("510300.SH", "2026-01-05", 10.0, "2026-01-05 15:05:00+08:00"),
                _bar("510300.SH", "2026-01-06", 10.0, "2026-01-06 15:05:00+08:00"),
                _bar("510300.SH", "2026-01-07", 12.0, "2026-01-07 15:05:00+08:00"),
                _bar("510300.SH", "2026-01-08", 999.0, "2026-01-08 15:05:00+08:00"),
            ]
            _write_etf(etf, rows)
            # horizon=3 → entry 01-05, exit 01-08; now before bench available_at
            early = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                3,
                etf_path=etf,
                allow_mock=False,
                now="2026-01-08 15:01:00+08:00",
            )
            self.assertEqual(early["status"], "pending")
            self.assertEqual(early["reason"], "insufficient_benchmark_final_closes")
            self.assertNotIn("alpha_vs_510300", early)

            later = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                3,
                etf_path=etf,
                allow_mock=False,
                now="2026-01-08 15:06:00+08:00",
            )
            self.assertEqual(later["status"], "settled")
            self.assertEqual(later["exit_date"], "2026-01-08")
            self.assertAlmostEqual(later["bench_return"], 999.0 / 10.0 - 1.0, places=8)

    def test_today_still_trading_without_available_at_is_pending(self):
        with TemporaryDirectory() as tmp:
            etf = Path(tmp) / "etf.parquet"
            rows = []
            for code, base in (("510500.SH", 10.0), ("510300.SH", 10.0)):
                rows.extend(
                    [
                        _bar(code, "2026-01-05", base),
                        _bar(code, "2026-01-06", base + 1),
                        _bar(code, "2026-01-07", base + 2),
                        _bar(code, "2026-01-08", 99.0),
                    ]
                )
            _write_etf(etf, rows)
            # horizon=3 → needs exit 01-08; 14:00 before 15:00 → drop today
            out = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                3,
                etf_path=etf,
                allow_mock=False,
                now="2026-01-08 14:00:00+08:00",
            )
            self.assertEqual(out["status"], "pending")
            self.assertEqual(out["reason"], "insufficient_final_closes")

    def test_api_kwargs_backward_compatible(self):
        """Positional (instrument, session, horizon) + old kwargs still work."""
        with TemporaryDirectory() as tmp:
            etf = Path(tmp) / "etf.parquet"
            rows = []
            for code, base in (("510500.SH", 100.0), ("510300.SH", 10.0)):
                for i, d in enumerate(
                    ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"]
                ):
                    rows.append(_bar(code, d, base * (1.01**i)))
            _write_etf(etf, rows)
            out = compute_horizon_returns(
                "510500.SH",
                "2026-01-05",
                2,
                benchmark="510300.SH",
                etf_path=etf,
                allow_mock=False,
                now="2026-01-09 16:00:00+08:00",
            )
            self.assertEqual(out["status"], "settled")
            self.assertIn("alpha_vs_510300", out)
            self.assertIn("entry_date", out)
            self.assertIn("exit_date", out)


class ModuleSurface(unittest.TestCase):
    def test_not_byte_identical_to_origin_greenfield(self):
        """CONDITION B: behavior port, not wholesale Origin overwrite."""
        text = Path(settle.__file__).read_text(encoding="utf-8")
        self.assertIn("compute_horizon_returns", text)
        self.assertIn("ON OR AFTER", text)
        self.assertIn("_is_final_close", text)
        self.assertIn("insufficient_benchmark_final_closes", text)
        # Origin greenfield signature markers must not replace box API.
        self.assertIn("instrument: str", text)
        self.assertIn("horizon_trading_days", text)
        self.assertIn("allow_mock", text)


if __name__ == "__main__":
    unittest.main()
