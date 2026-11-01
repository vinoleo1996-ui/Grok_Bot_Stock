"""Settle pending research decisions vs 510300 (A-share book benchmark).

PIT / final-close rules (cand4 CONDITION B box port · FIX_A fence only):
- Decision session date is the as-of cutoff; entry uses first trading bar
  ON OR AFTER session (box caller contract; next_session not default here).
- Instrument **and** benchmark closes pass the same final-close fence:
  drop bars with available_at > now; else drop "today before regular close"
  (A-share 15:00 Asia/Shanghai); future calendar days are not final.
- If the fence removes a benchmark final needed to price entry/exit, stay
  pending (insufficient_benchmark_final_closes) — do not leak a live bar
  into alpha.
- Never writes Strategy NAV or places orders.
- strategy_promotion_approved remains False.
"""
from __future__ import annotations

import json
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .schemas import force_research_flags

PROMOTION_APPROVED = False
LIVE = False

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ETF_DAILY = REPO_ROOT / "data" / "v2" / "etf" / "etf_daily_adj.parquet"
DEFAULT_LOG = REPO_ROOT / "output" / "trading_loop" / "decision_log.jsonl"
BENCHMARK = "510300.SH"

DEFAULT_TZ = "Asia/Shanghai"
DEFAULT_REGULAR_CLOSE = time(15, 0)


def _to_market(value: Any, tz: str = DEFAULT_TZ) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError("invalid_timestamp")
    if ts.tzinfo is None:
        return ts.tz_localize(tz)
    return ts.tz_convert(tz)


def _session_date(value: Any, tz: str = DEFAULT_TZ) -> pd.Timestamp:
    return _to_market(value, tz).normalize()


def _regular_close_at(day: Any, tz: str, regular_close: time) -> pd.Timestamp:
    day = _session_date(day, tz)
    return day + pd.Timedelta(hours=regular_close.hour, minutes=regular_close.minute)


def _is_final_close(
    bar_ts: Any,
    now: Any,
    *,
    available_at: Any = None,
    tz: str = DEFAULT_TZ,
    regular_close: time = DEFAULT_REGULAR_CLOSE,
) -> bool:
    """True iff this bar may be used as a settled final close."""
    now_m = _to_market(now, tz)
    if available_at is not None and pd.notna(available_at):
        return _to_market(available_at, tz) <= now_m
    bar_day = _session_date(bar_ts, tz)
    today = now_m.normalize()
    if bar_day > today:
        return False
    if bar_day == today and now_m < _regular_close_at(today, tz, regular_close):
        return False
    return True


def _load_closes(
    ts_code: str,
    path: Path,
    *,
    now: Any,
    tz: str = DEFAULT_TZ,
    regular_close: time = DEFAULT_REGULAR_CLOSE,
) -> pd.Series:
    """Return trade_date-indexed close for one ts_code after final-close fence.

    Same fence for instrument and benchmark callers (FIX_A / CONDITION B).
    """
    if not path.exists():
        raise FileNotFoundError(f"ETF daily missing: {path}")
    # Prefer available_at when present; tolerate older parquet without it.
    try:
        df = pd.read_parquet(path, columns=["ts_code", "trade_date", "close", "available_at"])
        has_available = True
    except Exception:
        df = pd.read_parquet(path, columns=["ts_code", "trade_date", "close"])
        has_available = False
        df["available_at"] = pd.NaT
    sub = df[df["ts_code"] == ts_code].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["trade_date"] = pd.to_datetime(sub["trade_date"].astype(str), format="%Y%m%d")
    sub = sub.sort_values("trade_date")
    sub = sub[sub["close"].notna() & (sub["close"] > 0)]
    keep_idx: list[Any] = []
    for _, row in sub.iterrows():
        avail = row["available_at"] if has_available else None
        if _is_final_close(
            row["trade_date"],
            now,
            available_at=avail,
            tz=tz,
            regular_close=regular_close,
        ):
            keep_idx.append(row.name)
    if not keep_idx:
        return pd.Series(dtype=float)
    fenced = sub.loc[keep_idx]
    return fenced.set_index("trade_date")["close"]


def compute_horizon_returns(
    instrument: str,
    session: str,
    horizon_trading_days: int,
    *,
    benchmark: str = BENCHMARK,
    etf_path: Path | None = None,
    allow_mock: bool = True,
    now: Any | None = None,
    tz: str = DEFAULT_TZ,
    regular_close: time = DEFAULT_REGULAR_CLOSE,
) -> dict[str, Any]:
    """Score raw & alpha vs 510300 over horizon trading days after session.

    Caller-facing signature unchanged (instrument, session, horizon_trading_days,
    benchmark / etf_path / allow_mock). Optional ``now`` / ``tz`` /
    ``regular_close`` support the final-close fence in tests and live clocks.

    Entry remains first bar ON OR AFTER session (box contract). Returns dict
    with status settled|pending|unavailable and metrics.
    """
    path = etf_path or DEFAULT_ETF_DAILY
    session_ts = pd.Timestamp(session)
    now_m = _to_market(now, tz) if now is not None else pd.Timestamp.now(tz=tz)

    try:
        inst = _load_closes(
            instrument, path, now=now_m, tz=tz, regular_close=regular_close
        )
        bench = _load_closes(
            benchmark, path, now=now_m, tz=tz, regular_close=regular_close
        )
        source = "etf_daily_adj"
    except FileNotFoundError:
        inst = pd.Series(dtype=float)
        bench = pd.Series(dtype=float)
        source = "missing"

    if inst.empty or bench.empty:
        if not allow_mock:
            # Distinguish fence-empty (file exists but no finals) from missing file.
            if source == "etf_daily_adj":
                return {
                    "status": "pending",
                    "settle_source": source,
                    "reason": "insufficient_final_closes",
                    "reflection_zh": "终盘篱笆后无可用收盘，留待下次 settle",
                }
            return {
                "status": "unavailable",
                "settle_source": source or "none",
                "reflection_zh": "无行情：无法结算",
            }
        # Deterministic mock path — labeled clearly for research demos.
        # Mock bars are treated as already-final (no available_at leakage path).
        source = "mock"
        # Cand3 port: SSE open days only (never pd.bdate_range; CN holidays matter).
        from quantlab.portfolio.trade_calendar import open_day_range

        dates = open_day_range(session_ts, horizon_trading_days + 2)
        # instrument drifts +0.2%/day, bench +0.1%/day
        inst = pd.Series(
            [100 * (1.002**i) for i in range(len(dates))], index=dates, dtype=float
        )
        bench = pd.Series(
            [100 * (1.001**i) for i in range(len(dates))], index=dates, dtype=float
        )

    # Entry: first bar ON OR AFTER session (box caller contract).
    inst_after = inst[inst.index >= session_ts]
    if len(inst_after) <= horizon_trading_days:
        return {
            "status": "pending",
            "settle_source": source,
            "reason": "insufficient_final_closes",
            "reflection_zh": "持有窗尚未走完（或终盘不足），留待下次 settle",
        }

    entry_dt = inst_after.index[0]
    exit_dt = inst_after.index[horizon_trading_days]

    # Benchmark uses the SAME entry_dt / exit_dt; fence already applied via
    # _load_closes. If exit-day final is missing → pending (FIX_A).
    bench_days = pd.DatetimeIndex(pd.to_datetime(bench.index)).normalize()
    exit_day = pd.Timestamp(exit_dt).normalize()
    entry_day = pd.Timestamp(entry_dt).normalize()
    if bench.empty or bench_days.max() < exit_day:
        return {
            "status": "pending",
            "settle_source": source,
            "reason": "insufficient_benchmark_final_closes",
            "reflection_zh": "基准终盘不足，暂不结算（防盘中渗入 alpha）",
            "entry_date": entry_dt.strftime("%Y-%m-%d"),
            "exit_date": exit_dt.strftime("%Y-%m-%d"),
        }

    px0 = float(inst_after.iloc[0])
    px1 = float(inst_after.iloc[horizon_trading_days])
    raw = (px1 - px0) / px0
    # Prefer exact session matches; asof only after fence confirmed coverage.
    if entry_day not in set(bench_days) or exit_day not in set(bench_days):
        return {
            "status": "pending",
            "settle_source": source,
            "reason": "insufficient_benchmark_final_closes",
            "reflection_zh": "基准入/出场日终盘缺失，暂不结算",
            "entry_date": entry_dt.strftime("%Y-%m-%d"),
            "exit_date": exit_dt.strftime("%Y-%m-%d"),
        }
    b0 = float(bench.asof(entry_dt))
    b1 = float(bench.asof(exit_dt))
    if b0 is None or b1 is None or pd.isna(b0) or pd.isna(b1) or b0 <= 0:
        return {
            "status": "pending",
            "settle_source": source,
            "reason": "insufficient_benchmark_final_closes",
            "reflection_zh": "基准价格无效或终盘不足",
            "entry_date": entry_dt.strftime("%Y-%m-%d"),
            "exit_date": exit_dt.strftime("%Y-%m-%d"),
        }
    bret = (b1 - b0) / b0
    alpha = raw - bret

    sign = "正" if alpha >= 0 else "负"
    reflection = (
        f"相对 {benchmark} 的 {horizon_trading_days} 日窗口 alpha={alpha:.4%}（{sign}）；"
        f"标的收益 {raw:.4%}，基准 {bret:.4%}；来源={source}。"
        f"仅决策质量记忆，不改主书、不晋级。"
    )
    return {
        "status": "settled",
        "settle_source": source,
        "entry_date": entry_dt.strftime("%Y-%m-%d"),
        "exit_date": exit_dt.strftime("%Y-%m-%d"),
        "raw_return": raw,
        "bench_return": bret,
        "alpha_vs_510300": alpha,
        "reflection_zh": reflection,
    }


def load_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def pending_entries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("status", "pending") == "pending"]


def settle_log(
    log_path: Path | None = None,
    *,
    etf_path: Path | None = None,
    allow_mock: bool = True,
    rewrite: bool = True,
    now: Any | None = None,
) -> dict[str, Any]:
    """Settle all pending rows in decision log; rewrite JSONL in place."""
    path = log_path or DEFAULT_LOG
    rows = load_log(path)
    settled: list[dict[str, Any]] = []
    still_pending: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    out_rows: list[dict[str, Any]] = []
    for r in rows:
        r = force_research_flags(r)
        if r.get("status") != "pending":
            out_rows.append(r)
            continue
        metrics = compute_horizon_returns(
            str(r.get("instrument", "")),
            str(r.get("session", "")),
            int(r.get("horizon_trading_days") or 5),
            benchmark=str(r.get("benchmark") or BENCHMARK),
            etf_path=etf_path,
            allow_mock=allow_mock,
            now=now,
        )
        status = metrics["status"]
        if status == "settled":
            r.update(
                {
                    "status": "settled",
                    "entry_date": metrics["entry_date"],
                    "exit_date": metrics["exit_date"],
                    "raw_return": metrics["raw_return"],
                    "bench_return": metrics["bench_return"],
                    "alpha_vs_510300": metrics["alpha_vs_510300"],
                    "reflection_zh": metrics["reflection_zh"],
                    "settled_at": stamp,
                    "settle_source": metrics["settle_source"],
                    "strategy_promotion_approved": False,
                }
            )
            settled.append(r)
        elif status == "pending":
            r["reflection_zh"] = metrics.get("reflection_zh", "")
            if metrics.get("reason"):
                r["pending_reason"] = metrics["reason"]
            still_pending.append(r)
        else:
            r["status"] = "unavailable"
            r["reflection_zh"] = metrics.get("reflection_zh", "")
            r["settle_source"] = metrics.get("settle_source", "")
            unavailable.append(r)
        out_rows.append(r)

    if rewrite:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in out_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "log_path": str(path),
        "settled_n": len(settled),
        "pending_n": len(still_pending),
        "unavailable_n": len(unavailable),
        "settled_ids": [x.get("decision_id") for x in settled],
        "strategy_promotion_approved": False,
    }
