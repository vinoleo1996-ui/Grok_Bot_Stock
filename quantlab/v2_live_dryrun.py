"""Research-grade realtime closed-loop dry-run: G1–G5 → weights → book-smoke.

LIGHT — no uvicorn, no orders, no E1/full NAV, promotion_gate untouched.
Maps TRADINGAGENTS_DEEP_READ §6 G1–G5 to Eng surfaces, then reuses skeleton
weight + book-smoke --skip-run.

Usage::

    cd /workspace/QuantLab
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli live-dry-run
    PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_live_dryrun
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _check_g1() -> dict[str, Any]:
    """G1: local PIT text/asof (reject Yahoo). Eng: asof_text_guard + messages loader."""
    from datetime import date

    from quantlab.factors.ai_factory.asof_text_guard import as_of, as_of_window, coverage_gap
    from quantlab.intel.asof_window import assert_available_at_le_decision, session_to_decision_ts
    from quantlab.intel.messages import default_message_corpus_path, load_messages_for_session

    trade = "2024-05-31"
    trade_d = date.fromisoformat(trade)
    clamped = as_of("2024-06-15", trade)
    win = as_of_window("2024-05-01", "2024-06-15", trade)
    pit_ok = False
    try:
        assert_available_at_le_decision(
            {"available_at": "2024-06-01T18:00:00"},
            session_to_decision_ts(trade_d),
        )
    except Exception:
        pit_ok = True
    gap = coverage_gap([], "2024-05-01", trade, "yahoo_finance", "ohlcv")
    corpus = default_message_corpus_path()
    n_messages = 0
    gaps: list[str] = []
    try:
        df = load_messages_for_session(trade_d, instruments=["600519.SH"])
        n_messages = int(len(df))
        cg = getattr(df, "attrs", {}).get("coverage_gap")
        if cg:
            gaps.append(str(cg))
    except Exception as e:  # noqa: BLE001
        gaps = [f"messages_loader:{e}"]
    ok = clamped == trade and str(win[1])[:10] <= trade and pit_ok and gap is not None
    return {
        "ok": ok,
        "gate": "G1",
        "title": "本地 PIT 分析师文本/行情（拒 Yahoo）",
        "stub": True,
        "real": ["asof_text_guard", "asof_window.assert_available_at_le_decision", "messages loader"],
        "module": "quantlab.factors.ai_factory.asof_text_guard + quantlab.intel.messages",
        "cli": "python research/ai_debate_memory_runner.py --dry-run --session 2024-05-31 --instrument 600519.SH",
        "as_of_clamped": clamped,
        "window": list(win),
        "corpus_path": str(corpus) if corpus else None,
        "n_messages": n_messages,
        "coverage_gaps_sample": (gaps or [gap])[:2],
        "pit_future_rejected": pit_ok,
    }


def _check_g2() -> dict[str, Any]:
    """G2: A-share sentiment S1; missing → explicit coverage_gap (not fake empty)."""
    from quantlab.factors.ai_factory.asof_text_guard import coverage_gap
    from quantlab.intel.asof_window import withhold_live_only

    gap = coverage_gap(
        [],
        "2024-05-01",
        "2024-05-31",
        "s1_xueqiu_sentiment",
        "sentiment",
    )
    notice = withhold_live_only("2024-05-31", label="s1_sentiment", kind="live_profile")
    ok = gap is not None and ("not an absence" in gap or "unavailable" in gap) and bool(notice)
    return {
        "ok": ok,
        "gate": "G2",
        "title": "情绪源 A 股本地；未交付则 coverage_gap",
        "stub": True,
        "real": ["coverage_gap", "withhold_live_only"],
        "module": "quantlab.intel.asof_window / asof_text_guard",
        "cli": "(no dedicated CLI; exercised via live-dry-run + debate dry-run)",
        "coverage_gap": gap,
        "withhold_notice": (notice[:120] + "…") if isinstance(notice, str) and len(notice) > 120 else notice,
        "note": "S1 主源未齐；Eng 只保证缺口可记账，不编造空情绪",
    }


def _check_g3(out: Path) -> dict[str, Any]:
    """G3: Bull⇄Bear + RM → ledger (stub turns)."""
    from quantlab.intel.debate_ledger import DebateTurn, JsonlDebateLedger

    path = out / "g3_debate_ledger.jsonl"
    if path.exists():
        path.unlink()
    ledger = JsonlDebateLedger(path)
    turns: list[DebateTurn] = [
        {
            "turn_id": "t_bull",
            "role": "bull",
            "session": "2024-05-31",
            "instrument": "600519.SH",
            "thesis_zh": "（dry-run）多头桩",
        },
        {
            "turn_id": "t_bear",
            "role": "bear",
            "session": "2024-05-31",
            "instrument": "600519.SH",
            "thesis_zh": "（dry-run）空头桩",
        },
        {
            "turn_id": "t_rm",
            "role": "research_manager",
            "session": "2024-05-31",
            "instrument": "600519.SH",
            "thesis_zh": "（dry-run）RM Abstain/Hold 桩",
            "verdict": "Abstain",
        },
    ]
    ledger.append_turns(turns)
    n = sum(1 for _ in path.open(encoding="utf-8") if _.strip())
    ok = n >= 3 and path.exists()
    return {
        "ok": ok,
        "gate": "G3",
        "title": "Bull⇄Bear + RM 写入 ledger",
        "stub": True,
        "real": ["JsonlDebateLedger.append_turns", "DebateTurn"],
        "module": "quantlab.intel.debate_ledger",
        "cli": "python research/ai_debate_memory_runner.py --dry-run …",
        "ledger": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "n_turns": n,
    }


def _check_g4(out: Path) -> dict[str, Any]:
    """G4: risk three-state path → PM (trading_loop nodes RISK_REVIEW → PM_GATE)."""
    from quantlab.agents.trading_loop.state_machine import LoopNode, stub_run_once

    log = out / "g4_decision_log.jsonl"
    if log.exists():
        log.unlink()
    trace, entry = stub_run_once(
        session="2024-07-01",
        instrument="510500.SH",
        log_path=log,
    )
    need = {LoopNode.RISK_REVIEW.value, LoopNode.PM_GATE.value, LoopNode.DEBATE_BULL_BEAR.value}
    ok = need.issubset(set(trace)) and entry.get("strategy_promotion_approved") is False
    ok = ok and entry.get("pm_verdict") in ("approve_research", "Abstain", "REVIEW", "Hold", "approve")
    return {
        "ok": ok,
        "gate": "G4",
        "title": "风险三态节点→PM（stub 路径含 RISK_REVIEW/PM_GATE）",
        "stub": True,
        "real": ["LoopNode graph", "DecisionLogEntry.pm_verdict"],
        "module": "quantlab.agents.trading_loop.state_machine",
        "cli": "python -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH",
        "trace": trace,
        "pm_verdict": entry.get("pm_verdict"),
        "note": "Aggressive/Conservative/Neutral 角色名在契约；执行仍薄（stub）",
    }


def _check_g5() -> dict[str, Any]:
    """G5: configurable horizon + pending until full window; settle vs 510300."""
    from quantlab.agents.trading_loop.settle import compute_horizon_returns

    pending = compute_horizon_returns(
        "510500.SH",
        "2099-01-02",  # far future → cannot settle → pending/unavailable
        horizon_trading_days=5,
        allow_mock=False,
    )
    settled = compute_horizon_returns(
        "510500.SH",
        "2024-07-01",
        horizon_trading_days=5,
        allow_mock=True,
    )
    ok = pending.get("status") in ("pending", "unavailable") and settled.get("status") == "settled"
    return {
        "ok": ok,
        "gate": "G5",
        "title": "结算窗可配 + 未满窗 pending；满窗相对 510300",
        "stub": settled.get("settle_source") == "mock",
        "real": ["compute_horizon_returns", "horizon_trading_days"],
        "module": "quantlab.agents.trading_loop.settle",
        "cli": "python -m quantlab.agents.trading_loop.settle_pending",
        "pending_status": pending.get("status"),
        "settled_status": settled.get("status"),
        "settle_source": settled.get("settle_source"),
        "horizon_trading_days": 5,
        "benchmark": "510300.SH",
    }


def run_live_dryrun(
    *,
    capital: int = 600_000,
    top_k: int = 5,
    out_dir: str | Path | None = None,
    skip_skeleton_tail: bool = False,
) -> dict[str, Any]:
    """G1–G5 surface checks + factor_evolve weights + book-smoke --skip-run."""
    out = Path(out_dir) if out_dir else ROOT / "output" / "v3" / "live_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "ok": False,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_uvicorn": True,
        "doc": "docs/v2/LIVE_DRYRUN_COMMANDS_ZH.md",
        "gate_spec": "docs/v2/TRADINGAGENTS_DEEP_READ_ZH.md §6 G1–G5",
        "steps": {},
    }

    result["steps"]["G1"] = _check_g1()
    result["steps"]["G2"] = _check_g2()
    result["steps"]["G3"] = _check_g3(out)
    result["steps"]["G4"] = _check_g4(out)
    result["steps"]["G5"] = _check_g5()

    if not skip_skeleton_tail:
        from quantlab.v2_skeleton_smoke import run_skeleton_smoke

        sk_out = out / "skeleton_tail"
        sk = run_skeleton_smoke(
            book_nav=False,
            capital=int(capital),
            top_k=int(top_k),
            out_dir=sk_out,
        )
        result["steps"]["weights"] = {
            "ok": bool(sk.get("steps", {}).get("factor_evolve", {}).get("ok"))
            and bool(sk.get("steps", {}).get("weight_long_table", {}).get("ok")),
            "gate": "weights",
            "title": "factor_evolve --smoke → weight_long_table",
            "stub": True,
            "real": ["weight_long_table contract"],
            "factor_evolve": sk.get("steps", {}).get("factor_evolve"),
            "weight_long_table": sk.get("steps", {}).get("weight_long_table"),
            "cli": "python -m quantlab.cli factor-evolve --smoke",
            "coverage_rule": "全日更长表须覆盖目标窗；禁止仅前推解读",
        }
        result["steps"]["smoke"] = {
            "ok": bool(sk.get("steps", {}).get("book_smoke", {}).get("ok")),
            "gate": "smoke",
            "title": "book-smoke --skip-run（不下单/不物化 NAV）",
            "stub": True,
            "real": ["book_smoke wiring"],
            "book_smoke": sk.get("steps", {}).get("book_smoke"),
            "cli": "python -m quantlab.cli book-smoke",
        }
        result["skeleton_ok"] = bool(sk.get("ok"))
    else:
        result["skeleton_ok"] = None

    result["ok"] = all(s.get("ok") for s in result["steps"].values())
    summary = out / "live_dryrun_summary.json"
    summary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    result["summary_path"] = str(summary)
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--capital", type=int, default=600_000, choices=[600_000, 1_000_000])
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--out", default=None)
    ap.add_argument(
        "--gates-only",
        action="store_true",
        help="only G1–G5 surface checks (skip factor_evolve/book-smoke)",
    )
    a = ap.parse_args(argv)
    status = run_live_dryrun(
        capital=a.capital,
        top_k=a.top_k,
        out_dir=a.out,
        skip_skeleton_tail=a.gates_only,
    )
    print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
