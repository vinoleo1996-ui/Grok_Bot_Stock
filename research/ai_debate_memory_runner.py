#!/usr/bin/env python3
"""AI debate + memory settlement research stub (TradingAgents-adapted).

Consumes Eng ``quantlab.intel.debate_ledger`` schema only.
Rule/template theses (no external LLM; no Yahoo/Reddit/StockTwits).
Research-grade: promotion_approved always False; no orders / NAV / Strategy.

Usage:
  cd /workspace/QuantLab
  python research/ai_debate_memory_runner.py --dry-run \\
    --instrument 600519.SH --session 2024-05-31
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantlab.intel.asof_window import session_to_decision_ts
from quantlab.intel.debate_ledger import (
    DEFAULT_DEBATE_LEDGER,
    DebateRoundResult,
    DebateTurn,
    DecisionEntry,
    JsonlDebateLedger,
    RatingLabel,
    SettlementRecord,
    make_pending_decision,
)
from quantlab.intel.messages import load_messages_for_session

PROMOTION_APPROVED = False
STRATEGY_PROMOTION_APPROVED = False
DEFAULT_BENCHMARK = "510300"  # Mandate / New Bot settle: 沪深300 ETF; Eng field = alpha_vs_benchmark
DEFAULT_HORIZON_DAYS = 5
# Research settlement price sources (local D0 panels + ETF adj). Not Yahoo.
DEFAULT_D0_PANELS = ROOT / "data" / "local_market" / "1c85fd9aceaa03c3c4863bec" / "panels"
DEFAULT_ETF_DAILY_ADJ = ROOT / "data" / "v2" / "etf" / "etf_daily_adj.parquet"
BENCHMARK_TS_CODE = "510300.SH"
# QuantMind factor_evolve KPI 权重长表（融合蓝图主路径）；BOOK smoke 仅作兜底引用。
FACTOR_EVOLVE_DIR = ROOT / "output" / "factor_evolve"
FACTOR_EVOLVE_META = FACTOR_EVOLVE_DIR / "latest_meta.json"
FACTOR_EVOLVE_WEIGHTS_PATH_FILE = FACTOR_EVOLVE_DIR / "latest_weights.path"
OPTIONAL_WEIGHT_TABLE = (
    ROOT / "output" / "strategy_mbook_v2_smoke" / "X2" / "BOOK" / "target_weights.parquet"
)


def _ts_iso(session: date | str, asof: datetime | str | None = None) -> str:
    if asof is not None:
        return str(asof) if not isinstance(asof, datetime) else asof.isoformat(sep="T", timespec="seconds")
    d = session if isinstance(session, date) else date.fromisoformat(str(session)[:10])
    return session_to_decision_ts(d).isoformat(sep="T", timespec="seconds")


def _turn_id(session: str, instrument: str, role: str, salt: str = "") -> str:
    raw = f"{session}|{instrument}|{role}|{salt}"
    return "t_" + hashlib.sha1(raw.encode()).hexdigest()[:16]


def _decision_id(session: str, instrument: str) -> str:
    return f"dec_{session}_{instrument.replace('.', '')}_{uuid.uuid4().hex[:8]}"


def settlement_resolved_date(row: Mapping[str, Any]) -> str | None:
    """G6: date when settlement outcome became known (exit bar / resolution).

    Prefer ``resolution_date`` (YYYY-MM-DD), then ``exit_date``, then date part of
    ``settled_at``. Returns None if unparseable — caller may drop or keep per policy.
    """
    for key in ("resolution_date", "exit_date"):
        v = row.get(key)
        if v is None or v == "":
            continue
        s = str(v).strip()[:10]
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s
    settled = row.get("settled_at")
    if settled:
        s = str(settled).strip()[:10]
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return s
    return None


def load_prior_settlements(
    ledger: JsonlDebateLedger,
    *,
    instrument: str | None = None,
    limit: int = 8,
    non_null_only: bool = False,
    as_of: date | str | None = None,
) -> list[dict[str, Any]]:
    """Read prior SettlementRecord rows from Eng JSONL (newest last, return tail).

    When ``non_null_only`` is True, keep only rows with both raw_return and
    alpha_vs_benchmark non-null (usable memory for the next debate).

    G6: when ``as_of`` is set (trade/decision date), keep only settlements whose
    ``resolution_date`` (else exit_date / settled_at date) is ≤ as_of. Blocks
    lookahead lessons from hold windows that resolve after the debate day.
    """
    if not ledger.path.exists():
        return []
    asof_s: str | None = None
    if as_of is not None:
        if isinstance(as_of, date):
            asof_s = as_of.isoformat()
        else:
            asof_s = str(as_of).strip()[:10]
    rows: list[dict[str, Any]] = []
    with ledger.path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") != "settlement":
                continue
            if instrument and str(r.get("instrument")) != str(instrument):
                continue
            if non_null_only:
                if r.get("raw_return") is None or r.get("alpha_vs_benchmark") is None:
                    continue
            if asof_s is not None:
                resolved = settlement_resolved_date(r)
                if resolved is None or resolved > asof_s:
                    continue  # G6: block unresolved / future-resolved memory
            rows.append(r)
    return rows[-limit:]


def format_memory_block(
    priors: Sequence[Mapping[str, Any]],
    *,
    k: int = 3,
    coverage_gaps: list[str] | None = None,
) -> tuple[str, bool]:
    """Build Chinese memory block from newest-K non-null settlements.

    Returns (block_zh, injected). If empty, block explicitly states coverage_gap
    and optionally appends to coverage_gaps.
    """
    tail = list(priors)[-int(k) :]
    if not tail:
        gap = (
            "memory_loop:coverage_gap: 同标的无非 null settlement 可回灌；"
            "bull/bear/research_manager 输入明示无历史记忆。"
        )
        if coverage_gaps is not None:
            coverage_gaps.append(gap)
        return (
            "【记忆回灌】coverage_gap：无同标的非 null settlement（reflection/alpha 不可用）。",
            False,
        )
    lines: list[str] = [
        f"【记忆回灌·最近{len(tail)}条非null结算】每条含 alpha 摘要 + reflection_zh："
    ]
    for i, s in enumerate(tail, 1):
        alpha = s.get("alpha_vs_benchmark")
        raw = s.get("raw_return")
        bench = s.get("benchmark") or "510300"
        sess = s.get("session")
        did = s.get("decision_id")
        refl = str(s.get("reflection_zh") or "").strip()
        if len(refl) > 160:
            refl = refl[:160] + "…"
        try:
            alpha_pct = f"{float(alpha):.4%}"
        except (TypeError, ValueError):
            alpha_pct = str(alpha)
        try:
            raw_pct = f"{float(raw):.4%}"
        except (TypeError, ValueError):
            raw_pct = str(raw)
        lines.append(
            f"  ({i}) session={sess} decision_id={did} "
            f"raw={raw_pct} alpha_vs_{bench}={alpha_pct}；反思：{refl}"
        )
    return "\n".join(lines), True


def resolve_factor_evolve_weight_path() -> tuple[Path | None, dict[str, Any]]:
    """Read-only resolve latest consumable weight long-table via latest_meta.json.

    Returns (path_or_None, meta_dict). Never writes Strategy / never mutates weights.
    """
    meta: dict[str, Any] = {}
    if FACTOR_EVOLVE_META.exists():
        try:
            meta = json.loads(FACTOR_EVOLVE_META.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {"error": "latest_meta_json_decode"}
    # Prefer meta.weight_path; fall back to latest_weights.path pointer.
    candidates: list[Path] = []
    wp = meta.get("weight_path")
    if wp:
        p = Path(str(wp))
        candidates.append(p if p.is_absolute() else ROOT / p)
    if FACTOR_EVOLVE_WEIGHTS_PATH_FILE.exists():
        try:
            line = FACTOR_EVOLVE_WEIGHTS_PATH_FILE.read_text(encoding="utf-8").strip().splitlines()[0]
            p = Path(line)
            candidates.append(p if p.is_absolute() else ROOT / p)
        except (OSError, IndexError):
            pass
    # Glob newest fe_*_weights.parquet as last resort
    if FACTOR_EVOLVE_DIR.exists():
        globs = sorted(FACTOR_EVOLVE_DIR.glob("fe_*_weights.parquet"), key=lambda x: x.stat().st_mtime)
        if globs:
            candidates.append(globs[-1])
    for c in candidates:
        if c.exists():
            return c, meta
    return None, meta


def load_weight_long_table(path: Path | None = None) -> "Any":
    """Load session,instrument_id,weight parquet (WeightLongTableSleeve contract). Read-only."""
    import pandas as pd

    if path is None:
        path, _ = resolve_factor_evolve_weight_path()
    if path is None or not Path(path).exists():
        return pd.DataFrame(columns=["session", "instrument_id", "weight"])
    df = pd.read_parquet(path)
    # Alias normalize (same spirit as WeightLongTableSleeve)
    cols = {c.lower(): c for c in df.columns}
    rename: dict[str, str] = {}
    for canon, aliases in (
        ("session", ("session", "date", "trade_date")),
        ("instrument_id", ("instrument_id", "instrument", "ts_code", "code")),
        ("weight", ("weight", "target_weight")),
    ):
        hit = next((cols[a] for a in aliases if a in cols), None)
        if hit is None:
            return pd.DataFrame(columns=["session", "instrument_id", "weight"])
        rename[hit] = canon
    out = df.rename(columns=rename)[["session", "instrument_id", "weight"]].copy()
    out["session"] = pd.to_datetime(out["session"].astype(str), errors="coerce")
    out["instrument_id"] = out["instrument_id"].astype(str).str.strip()
    out["weight"] = pd.to_numeric(out["weight"], errors="coerce")
    out = out.dropna(subset=["session", "instrument_id", "weight"])
    return out.sort_values(["session", "instrument_id"]).reset_index(drop=True)


def _instrument_id_aliases(instrument: str) -> list[str]:
    """Both panel (sh.600519) and ts (600519.SH) forms."""
    s = str(instrument).strip()
    aliases = {s, s.lower(), s.upper()}
    aliases.add(to_panel_id(s))
    aliases.add(to_ts_style(s))
    # also lower panel / upper ts variants
    aliases.add(to_panel_id(s).lower())
    aliases.add(to_ts_style(s).upper() if "." in to_ts_style(s) else to_ts_style(s))
    return list(aliases)


def lookup_instrument_weight(
    weights: "Any",
    instrument: str,
    session: str | date | None = None,
) -> dict[str, Any] | None:
    """Nearest weight row for instrument on/before session (else latest). Context only."""
    import pandas as pd

    if weights is None or getattr(weights, "empty", True):
        return None
    aliases = set(_instrument_id_aliases(instrument))
    # also match undotted numeric codes if present
    sub = weights[weights["instrument_id"].astype(str).isin(aliases)].copy()
    if sub.empty:
        # try normalizing table ids to panel form for compare
        def _norm(x: str) -> str:
            try:
                return to_panel_id(str(x))
            except Exception:  # noqa: BLE001
                return str(x).lower()
        target = to_panel_id(instrument)
        sub = weights[weights["instrument_id"].map(_norm) == target].copy()
    if sub.empty:
        return None
    if session is not None:
        sess = pd.Timestamp(str(session)[:10])
        on_or_before = sub[sub["session"] <= sess]
        pick = on_or_before if not on_or_before.empty else sub
    else:
        pick = sub
    row = pick.sort_values("session").iloc[-1]
    return {
        "session": pd.Timestamp(row["session"]).strftime("%Y-%m-%d"),
        "instrument_id": str(row["instrument_id"]),
        "weight": float(row["weight"]),
        "query_instrument": instrument,
        "query_session": str(session)[:10] if session is not None else None,
    }


def format_weight_context_block(
    hit: Mapping[str, Any] | None,
    *,
    weight_path: Path | None,
    n_rows: int | None,
    coverage_gaps: list[str] | None = None,
) -> tuple[str, bool]:
    """Chinese weight context for debate input. Never treats weight as fill price."""
    if hit is None:
        gap = (
            "weight_ctx:coverage_gap: 权重长表中无该标的行；"
            "辩论不把缺失权重当成空仓指令。"
        )
        if coverage_gaps is not None:
            coverage_gaps.append(gap)
        path_note = (
            f"path={weight_path.relative_to(ROOT) if weight_path and weight_path.is_relative_to(ROOT) else weight_path}"
            if weight_path
            else "path=None"
        )
        return (
            f"【权重上下文·QuantMind factor_evolve】coverage_gap：无该标的 weight（{path_note}；"
            f"n_rows={n_rows}）。研究引用，非成交价、非 Strategy。",
            False,
        )
    rel = None
    if weight_path is not None:
        try:
            rel = weight_path.relative_to(ROOT)
        except ValueError:
            rel = weight_path
    w = hit["weight"]
    block = (
        f"【权重上下文·QuantMind factor_evolve】"
        f"session={hit['session']} instrument_id={hit['instrument_id']} "
        f"weight={w:.6f}（查询标的={hit.get('query_instrument')}@"
        f"{hit.get('query_session') or 'latest'}）；"
        f"来源={rel}；n_rows={n_rows}。"
        "仅作辩论上下文，**不**当成交价、**不**写 Strategy / Book-Smoke 下单。"
    )
    return block, True


def _evidence_from_messages(df: Any) -> list[str]:
    refs: list[str] = []
    if df is None or getattr(df, "empty", True):
        return refs
    for _, row in df.head(8).iterrows():
        mid = row.get("message_id") or row.get("event_id") or row.get("content_hash")
        if mid is None or (isinstance(mid, float) and mid != mid):
            title = str(row.get("ann_title") or row.get("title") or "")[:40]
            mid = "title:" + hashlib.sha1(title.encode()).hexdigest()[:12]
        refs.append(str(mid))
    return refs


def _summarize_news(df: Any, coverage_gaps: list[str]) -> tuple[str, list[str]]:
    refs = _evidence_from_messages(df)
    if df is None or getattr(df, "empty", True):
        gap = "intel.messages: 窗内无可见公告（或 corpus 缺口）；禁止写成「无利空」。"
        coverage_gaps.append(gap)
        return (
            "【新闻分析师·规则模板】窗内无 PIT 可见公告证据；不做方向主张，仅记录 coverage_gap。",
            refs or ["coverage_gap:messages"],
        )
    titles = []
    for _, row in df.head(3).iterrows():
        t = str(row.get("ann_title") or row.get("title") or "").strip()
        if t:
            titles.append(t[:60])
    pol = None
    if "polarity" in df.columns:
        try:
            pol = float(df["polarity"].astype(float).mean())
        except (TypeError, ValueError):
            pol = None
    pol_zh = f"均值极性≈{pol:.2f}" if pol is not None else "极性不可用"
    thesis = (
        f"【新闻分析师·规则模板】PIT 可见公告 {len(df)} 条；样例：{' / '.join(titles) or '（无标题）'}；"
        f"{pol_zh}。论点可证伪：若后续窗无增量利好/利空落地，则本简报信息含量低。"
    )
    # expose reader attrs coverage_gap if present
    gap_attr = getattr(df, "attrs", {}).get("coverage_gap")
    if gap_attr:
        coverage_gaps.append(str(gap_attr))
    return thesis, refs


def _market_brief(
    instrument: str,
    session: str,
    coverage_gaps: list[str],
    weight_ctx: str | None,
) -> tuple[str, list[str]]:
    """Market analyst: no Yahoo; stock OHLCV reader often absent → coverage_gap."""
    refs: list[str] = []
    # Optional consumable weight long-table as *context only* (not an order).
    if weight_ctx:
        refs.append(weight_ctx)
    # Probe ETF adj only for 510300-style codes; equities typically missing here.
    etf_path = ROOT / "data" / "v2" / "etf" / "etf_daily_adj.parquet"
    has_equity_bar = False
    # Intentionally do not invent a second return engine; mark gap for A-share bars.
    if instrument.endswith((".SH", ".SZ")) and not instrument.startswith("51"):
        coverage_gaps.append(
            "market_ohlcv: 个股日线 PIT 统一 reader 未接线（仅见 etf_daily_adj）；"
            "analyst_market 不做价量编造。"
        )
        thesis = (
            f"【市场分析师·规则模板】{instrument}@{session}：缺个股 OHLCV PIT reader，"
            "不作动量/突破叙事。可证伪：待 Data/Eng 统一收盘 helper 后应能引用 session 前可见量价。"
        )
        refs.append("coverage_gap:market_ohlcv")
    else:
        if etf_path.exists():
            refs.append(f"path:{etf_path.relative_to(ROOT)}")
            thesis = (
                f"【市场分析师·规则模板】{instrument}@{session}：可引用仓内 ETF 复权日线路径作上下文；"
                "本桩不计算收益、不下单。"
            )
        else:
            coverage_gaps.append("market_ohlcv: etf_daily_adj 缺失")
            thesis = f"【市场分析师·规则模板】{instrument}@{session}：行情路径不可用。"
            refs.append("coverage_gap:market_ohlcv")
    if weight_ctx:
        thesis += " 另见可选权重长表上下文（研究引用，非晋级产出）。"
    _ = has_equity_bar
    return thesis, refs


def _optional_weight_ref(instrument: str, session: str | date | None = None) -> str | None:
    """Legacy ref string; prefer format_weight_context_block + lookup_instrument_weight."""
    wpath, meta = resolve_factor_evolve_weight_path()
    if wpath is None:
        if OPTIONAL_WEIGHT_TABLE.exists():
            return f"weight_ctx:{OPTIONAL_WEIGHT_TABLE.relative_to(ROOT)}"
        return None
    try:
        rel = wpath.relative_to(ROOT)
    except ValueError:
        rel = wpath
    n = meta.get("n_weight_rows")
    return f"weight_ctx:{rel}:n_rows={n}:instrument={instrument}:session={session}"


def build_rule_debate(
    *,
    session: date | str,
    instrument: str,
    message_lookback_days: int = 10,
    prior_limit: int = 5,
    ledger: JsonlDebateLedger | None = None,
    synthetic_demo: bool = False,
) -> DebateRoundResult:
    """One round: analyst_news + analyst_market + bull + bear + research_manager."""
    sess = str(session) if not isinstance(session, date) else session.isoformat()
    sess_d = session if isinstance(session, date) else date.fromisoformat(str(session)[:10])
    asof = _ts_iso(sess_d)
    store = ledger or JsonlDebateLedger()
    coverage_gaps: list[str] = []

    # Memory loop: inject recent-K *non-null* settlements into bull/bear/RM.
    # G6: as_of=session → only resolution_date≤asof (no lookahead lessons).
    prior_all = load_prior_settlements(
        store, instrument=instrument, limit=max(prior_limit, 20), as_of=sess_d
    )
    prior = load_prior_settlements(
        store, instrument=instrument, limit=prior_limit, non_null_only=True, as_of=sess_d
    )
    memory_block, memory_injected = format_memory_block(
        prior, k=prior_limit, coverage_gaps=coverage_gaps
    )
    # QuantMind weight long-table context (read-only; not a fill price).
    weight_path, weight_meta = resolve_factor_evolve_weight_path()
    weights_df = load_weight_long_table(weight_path)
    n_weight_rows = int(weight_meta.get("n_weight_rows") or len(weights_df))
    weight_hit = lookup_instrument_weight(weights_df, instrument, sess)
    weight_block, weight_injected = format_weight_context_block(
        weight_hit,
        weight_path=weight_path,
        n_rows=n_weight_rows,
        coverage_gaps=coverage_gaps,
    )
    prior_note = " " + memory_block.replace("\n", " | ") + " | " + weight_block.replace("\n", " | ")
    _ = prior_all  # retained for diagnostics; debate uses non-null only

    # --- news ---
    msg_df = None
    try:
        msg_df = load_messages_for_session(
            sess_d,
            instruments=[instrument],
            lookback_days=message_lookback_days,
            strict_asof=True,
        )
    except Exception as exc:  # noqa: BLE001 — research stub: surface gap
        coverage_gaps.append(f"intel.messages_error:{type(exc).__name__}:{exc}")

    if synthetic_demo and (msg_df is None or getattr(msg_df, "empty", True)):
        coverage_gaps.append("synthetic_demo: 注入合成公告证据（非实盘）")
        news_thesis = (
            "【新闻分析师·synthetic_demo】合成证据：演示用公告摘要「公司例行经营披露」；"
            "非仓内实盘，不可用于晋级。"
        )
        news_refs = ["synthetic_demo:ann_placeholder"]
    else:
        news_thesis, news_refs = _summarize_news(msg_df, coverage_gaps)

    weight_ref = _optional_weight_ref(instrument, sess)
    mkt_thesis, mkt_refs = _market_brief(instrument, sess, coverage_gaps, weight_ref)
    # Append full weight block to market thesis (context only).
    mkt_thesis = mkt_thesis + "\n" + weight_block
    if weight_injected and weight_hit is not None:
        mkt_refs = list(mkt_refs) + [
            f"weight:{weight_hit['instrument_id']}@{weight_hit['session']}={weight_hit['weight']:.6f}"
        ]

    turns: list[DebateTurn] = []

    def add(role: str, thesis: str, refs: Sequence[str], salt: str = "") -> str:
        tid = _turn_id(sess, instrument, role, salt=salt or thesis[:24])
        turns.append(
            DebateTurn(
                turn_id=tid,
                role=role,  # type: ignore[arg-type]
                session=sess,
                instrument=instrument,
                thesis_zh=thesis,
                evidence_refs=list(refs),
                asof_decision_ts=asof,
                promotion_approved=False,
            )
        )
        return tid

    tid_news = add("analyst_news", news_thesis + prior_note, news_refs, "news")
    tid_mkt = add("analyst_market", mkt_thesis, mkt_refs, "mkt")

    has_real_evidence = bool(news_refs) and not all(
        r.startswith("coverage_gap:") or r.startswith("synthetic_demo:") for r in news_refs
    )
    if synthetic_demo and not has_real_evidence:
        has_real_evidence = True  # demo path allowed to debate with labeled synthetic refs

    mem_suffix = "\n" + memory_block + "\n" + weight_block
    mem_refs = (
        [f"memory:{s.get('decision_id')}" for s in prior[-prior_limit:] if s.get("decision_id")]
        if memory_injected
        else ["coverage_gap:memory_non_null"]
    )
    if weight_injected and weight_hit is not None:
        mem_refs = list(mem_refs) + [
            f"weight:{weight_hit['instrument_id']}@{weight_hit['session']}={weight_hit['weight']:.6f}"
        ]
    else:
        mem_refs = list(mem_refs) + ["coverage_gap:weight_ctx"]

    if has_real_evidence:
        bull_thesis = (
            "【多头·规则模板】引用新闻简报证据，主张短窗信息可能降低不确定性；"
            "可证伪：若持有窗相对 510300 alpha≤0，则本主张失败。"
            + mem_suffix
        )
        bear_thesis = (
            "【空头·规则模板】同批证据多为例行/中性，缺乏增量定价；"
            "可证伪：若持有窗相对 510300 alpha>0 且由该信息驱动，则过度悲观。"
            + mem_suffix
        )
        bull_refs = (list(news_refs[:3]) or ["coverage_gap:bull"]) + mem_refs
        bear_refs = (list(news_refs[:3]) or list(mkt_refs[:2]) or ["coverage_gap:bear"]) + mem_refs
        rating: RatingLabel = "Hold"
        rationale = (
            "研究经理：多空均引用同一批 PIT 证据，增量不明确 → Hold；"
            "settlement 以相对 510300 的 alpha_vs_benchmark 复盘。"
            " 已注入同标的非 null 记忆回灌（见 thesis）。"
            if memory_injected
            else
            "研究经理：多空均引用同一批 PIT 证据，增量不明确 → Hold；"
            "settlement 以相对 510300 的 alpha_vs_benchmark 复盘。"
            " 无非 null 记忆（coverage_gap）。"
        )
        if coverage_gaps:
            rationale += " gaps=" + "; ".join(coverage_gaps)[:240]
    else:
        bull_thesis = (
            "【多头·规则模板】无合格 evidence_refs → 不硬编故事；建议 Abstain。"
            + mem_suffix
        )
        bear_thesis = (
            "【空头·规则模板】无合格 evidence_refs → 不硬编故事；建议 Abstain。"
            + mem_suffix
        )
        bull_refs = ["coverage_gap:no_evidence"] + mem_refs
        bear_refs = ["coverage_gap:no_evidence"] + mem_refs
        rating = "Abstain"
        rationale = (
            "研究经理：证据不足，Abstain。"
            + (" 已注入同标的非 null 记忆回灌。" if memory_injected else " 无非 null 记忆（coverage_gap）。")
            + (" gaps=" + "; ".join(coverage_gaps)[:240] if coverage_gaps else "")
        )

    tid_bull = add("bull", bull_thesis, bull_refs, "bull")
    tid_bear = add("bear", bear_thesis, bear_refs, "bear")
    tid_rm = add(
        "research_manager",
        f"【研究经理·规则模板】合成评级 {rating}。" + rationale + mem_suffix,
        [tid_news, tid_mkt, tid_bull, tid_bear] + mem_refs,
        "rm",
    )

    dec_id = _decision_id(sess, instrument)
    decision = make_pending_decision(
        decision_id=dec_id,
        session=sess,
        instrument=instrument,
        rating=rating,
        rationale_zh=rationale,
        debate_turn_ids=[tid_news, tid_mkt, tid_bull, tid_bear, tid_rm],
        asof_decision_ts=asof,
    )
    result = DebateRoundResult(session=sess_d, instrument=instrument, turns=turns, decision=decision)
    # stash gaps / memory flags for callers / receipt
    object.__setattr__(result, "_coverage_gaps", list(coverage_gaps))  # type: ignore[attr-defined]
    object.__setattr__(result, "_memory_injected", bool(memory_injected))  # type: ignore[attr-defined]
    object.__setattr__(result, "_memory_prior_n", len(prior))  # type: ignore[attr-defined]
    object.__setattr__(result, "_memory_block", memory_block)  # type: ignore[attr-defined]
    object.__setattr__(result, "_weight_injected", bool(weight_injected))  # type: ignore[attr-defined]
    object.__setattr__(result, "_weight_block", weight_block)  # type: ignore[attr-defined]
    object.__setattr__(result, "_weight_hit", dict(weight_hit) if weight_hit else None)  # type: ignore[attr-defined]
    object.__setattr__(
        result,
        "_weight_path",
        str(weight_path.relative_to(ROOT) if weight_path and str(weight_path).startswith(str(ROOT)) else weight_path),
    )  # type: ignore[attr-defined]
    object.__setattr__(result, "_weight_n_rows", int(n_weight_rows))  # type: ignore[attr-defined]
    return result


def append_round(ledger: JsonlDebateLedger, result: DebateRoundResult) -> DecisionEntry:
    """Write turns + pending decision; always promotion_approved=false."""
    if not result.decision:
        raise ValueError("DebateRoundResult.decision is required")
    ledger.append_turns(result.turns)
    decision = dict(result.decision)
    decision["promotion_approved"] = False
    decision["status"] = "pending"
    entry = DecisionEntry(**decision)  # type: ignore[misc]
    ledger.append_decision(entry)
    return entry


def to_panel_id(instrument: str) -> str:
    """600519.SH -> sh.600519; sh.600519 unchanged."""
    s = str(instrument).strip()
    if "." in s and s.split(".", 1)[0].lower() in ("sh", "sz", "bj"):
        return s.lower()
    if "." in s:
        code, exch = s.split(".", 1)
        return f"{exch.lower()}.{code}"
    return s.lower()


def to_ts_style(instrument: str) -> str:
    """sh.600519 -> 600519.SH."""
    s = str(instrument).strip()
    if "." in s:
        a, b = s.split(".", 1)
        if a.lower() in ("sh", "sz", "bj"):
            return f"{b}.{a.upper()}"
        return f"{a}.{b.upper()}"
    return s


_EQUITY_CLOSE_CACHE: dict[str, "Any"] = {}


def _load_equity_closes(instrument: str, panels_dir: Path | None = None) -> "Any":
    """Load feature_close (or close) Series from D0 panel; empty if missing."""
    import pandas as pd

    pid = to_panel_id(instrument)
    root = panels_dir or DEFAULT_D0_PANELS
    cache_key = f"{root}|{pid}"
    if cache_key in _EQUITY_CLOSE_CACHE:
        return _EQUITY_CLOSE_CACHE[cache_key]
    p = root / f"{pid}.parquet"
    if not p.exists():
        empty = pd.Series(dtype=float)
        _EQUITY_CLOSE_CACHE[cache_key] = empty
        return empty
    df = pd.read_parquet(p)
    if "feature_close" in df.columns:
        ser = pd.to_numeric(df["feature_close"], errors="coerce")
    elif "close" in df.columns and "factor" in df.columns:
        ser = pd.to_numeric(df["close"], errors="coerce") * pd.to_numeric(df["factor"], errors="coerce")
    elif "close" in df.columns:
        ser = pd.to_numeric(df["close"], errors="coerce")
    else:
        empty = pd.Series(dtype=float)
        _EQUITY_CLOSE_CACHE[cache_key] = empty
        return empty
    idx = pd.to_datetime(df.index)
    out = pd.Series(ser.values, index=idx).dropna()
    out = out[out > 0].sort_index()
    _EQUITY_CLOSE_CACHE[cache_key] = out
    return out


def _load_benchmark_closes(
    benchmark: str = DEFAULT_BENCHMARK,
    etf_path: Path | None = None,
) -> "Any":
    """Load 510300 close from etf_daily_adj (ts_code=510300.SH)."""
    import pandas as pd

    path = etf_path or DEFAULT_ETF_DAILY_ADJ
    if not path.exists():
        return pd.Series(dtype=float)
    code = BENCHMARK_TS_CODE
    b = str(benchmark)
    if b.upper().startswith("510300"):
        code = "510300.SH" if "." not in b or b.endswith("SH") or b == "510300" else b
        if b.upper() in ("510300", "510300.SH", "SH.510300"):
            code = "510300.SH"
    cols = ["ts_code", "trade_date", "close"]
    df = pd.read_parquet(path, columns=cols)
    sub = df[df["ts_code"] == code].copy()
    if sub.empty:
        return pd.Series(dtype=float)
    sub["trade_date"] = pd.to_datetime(sub["trade_date"].astype(str), format="%Y%m%d", errors="coerce")
    sub = sub.dropna(subset=["trade_date"])
    sub = sub[sub["close"].notna() & (sub["close"] > 0)].sort_values("trade_date")
    return sub.set_index("trade_date")["close"].astype(float)


def _load_benchmark_closes_hfq(
    benchmark: str = DEFAULT_BENCHMARK,
    etf_path: "Path | None" = None,
) -> "Any":
    """Self-check-only: 510300 back-adjusted close (close_hfq) from etf_daily_adj.

    _load_benchmark_closes (raw close) is left unchanged because it also feeds calendars,
    G5 settlement returns and some signal code paths.
    """
    import pandas as pd

    path = etf_path or DEFAULT_ETF_DAILY_ADJ
    if not path.exists():
        return pd.Series(dtype=float)
    df = pd.read_parquet(path, columns=["ts_code", "trade_date", "close_hfq"], filters=[("ts_code", "==", "510300.SH")])
    df["trade_date"] = pd.to_datetime(df["trade_date"].astype(str), format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["trade_date"])
    df = df[df["close_hfq"].notna() & (df["close_hfq"] > 0)].sort_values("trade_date")
    return df.set_index("trade_date")["close_hfq"].astype(float)


def compute_ashare_horizon_returns(
    instrument: str,
    session: str | date,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    *,
    benchmark: str = DEFAULT_BENCHMARK,
    panels_dir: Path | None = None,
    etf_path: Path | None = None,
) -> dict[str, Any]:
    """Research ex-post hold-window returns vs 510300 from local panels + ETF adj.

    Entry = first bar on/after session; exit = entry + horizon_days trading bars.
    Does **not** fabricate prices; returns status coverage_gap|pending|settled.
    """
    import pandas as pd

    session_ts = pd.Timestamp(str(session)[:10])
    inst = _load_equity_closes(instrument, panels_dir=panels_dir)
    bench = _load_benchmark_closes(benchmark, etf_path=etf_path)
    if inst.empty:
        return {
            "status": "coverage_gap",
            "settle_source": "d0_panel_missing",
            "raw_return": None,
            "alpha_vs_benchmark": None,
            "reflection_zh": f"coverage_gap: 无 D0 panel {to_panel_id(instrument)}，跳过不伪造。",
        }
    if bench.empty:
        return {
            "status": "coverage_gap",
            "settle_source": "etf_daily_adj_510300_missing",
            "raw_return": None,
            "alpha_vs_benchmark": None,
            "reflection_zh": "coverage_gap: etf_daily_adj 无 510300.SH，跳过不伪造。",
        }
    after = inst[inst.index >= session_ts]
    if len(after) <= horizon_days:
        return {
            "status": "pending",
            "settle_source": "d0_panel+etf_daily_adj",
            "raw_return": None,
            "alpha_vs_benchmark": None,
            "reflection_zh": f"持有窗未走完：session={session} horizon={horizon_days} 可用bar={len(after)}。",
        }
    entry_dt = after.index[0]
    exit_dt = after.index[horizon_days]
    px0 = float(after.iloc[0])
    px1 = float(after.iloc[horizon_days])
    if px0 <= 0:
        return {
            "status": "coverage_gap",
            "settle_source": "d0_panel+etf_daily_adj",
            "raw_return": None,
            "alpha_vs_benchmark": None,
            "reflection_zh": "coverage_gap: 入场价无效。",
        }
    raw = (px1 - px0) / px0
    b0 = bench.asof(entry_dt)
    b1 = bench.asof(exit_dt)
    if b0 is None or b1 is None or (isinstance(b0, float) and b0 != b0) or float(b0) <= 0:
        return {
            "status": "coverage_gap",
            "settle_source": "d0_panel+etf_daily_adj",
            "raw_return": None,
            "alpha_vs_benchmark": None,
            "reflection_zh": "coverage_gap: 基准 asof 价格无效。",
        }
    b0f, b1f = float(b0), float(b1)
    bret = (b1f - b0f) / b0f
    alpha = raw - bret
    return {
        "status": "settled",
        "settle_source": "d0_panel+etf_daily_adj",
        "entry_date": entry_dt.strftime("%Y-%m-%d"),
        "exit_date": exit_dt.strftime("%Y-%m-%d"),
        "raw_return": float(raw),
        "bench_return": float(bret),
        "alpha_vs_benchmark": float(alpha),
        "horizon_days": int(horizon_days),
        "benchmark": "510300",
        "reflection_zh": (
            f"相对 510300 的 {horizon_days} 日窗 alpha={alpha:.4%}；"
            f"标的 {raw:.4%}，基准 {bret:.4%}；"
            f"entry={entry_dt.date()} exit={exit_dt.date()}；"
            f"来源=d0_panel+etf_daily_adj。研究观察结算，非 Strategy NAV。"
        ),
    }



def settle_pending(
    ledger: JsonlDebateLedger,
    *,
    decision_id: str | None = None,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    benchmark: str = DEFAULT_BENCHMARK,
    dry_run: bool = True,
    raw_return: float | None = None,
    alpha_vs_benchmark: float | None = None,
    allow_synthetic_returns: bool = False,
) -> list[SettlementRecord]:
    """Settle pending decisions.

    Default dry_run: if returns not supplied and no price helper, write
    raw_return/alpha=null with reflection explaining coverage_gap — does **not**
    fabricate returns. Benchmark label forced to 510300 family for Mandate alpha.

    Optional ``raw_return`` / ``alpha_vs_benchmark`` inject research-observed
    numbers (caller-supplied). ``allow_synthetic_returns`` marks demo-only fills.
    """
    bench = benchmark if str(benchmark).startswith("510300") else DEFAULT_BENCHMARK
    pending = ledger.pending_decisions()
    if decision_id:
        pending = [p for p in pending if p.get("decision_id") == decision_id]
    out: list[SettlementRecord] = []
    now = datetime.now().isoformat(sep="T", timespec="seconds")

    for p in pending:
        did = str(p.get("decision_id") or "")
        instrument = str(p.get("instrument") or "")
        session = str(p.get("session") or "")
        rr = raw_return
        aa = alpha_vs_benchmark
        source_note = "caller_supplied" if rr is not None or aa is not None else "no_price_reader"
        metrics: dict[str, Any] | None = None
        if rr is None and aa is None and not allow_synthetic_returns:
            metrics = compute_ashare_horizon_returns(
                instrument, session, horizon_days=horizon_days, benchmark=bench
            )
            if metrics.get("status") == "settled":
                rr = metrics.get("raw_return")
                aa = metrics.get("alpha_vs_benchmark")
                source_note = str(metrics.get("settle_source") or "d0_panel+etf_daily_adj")
            elif metrics.get("status") == "pending":
                source_note = "hold_window_incomplete"
            else:
                source_note = str(metrics.get("settle_source") or "coverage_gap")
        if rr is None and aa is None and allow_synthetic_returns:
            # Explicit demo only — never the default path.
            rr, aa = 0.0, 0.0
            source_note = "synthetic_demo"

        # G5: incomplete hold window → stay pending (do NOT write settlement).
        if metrics and metrics.get("status") == "pending" and rr is None and aa is None:
            continue

        if rr is None and aa is None:
            if metrics and metrics.get("reflection_zh"):
                reflection = str(metrics["reflection_zh"])
            else:
                reflection = (
                    f"coverage_gap: 无可用本地收益；dry_run={'true' if dry_run else 'false'}；"
                    f"不伪造收益。持有窗={horizon_days} 交易日，基准={bench}。"
                    f"decision={did} instrument={instrument} session={session}。"
                )
        else:
            reflection = (
                f"研究观察结算 source={source_note}；horizon={horizon_days}；benchmark={bench}；"
                f"raw_return={rr}；alpha_vs_benchmark={aa}。"
                "非 Strategy NAV；promotion_approved=false。"
            )
            if metrics and metrics.get("reflection_zh"):
                reflection = str(metrics["reflection_zh"]) + " promotion_approved=false。"
            if source_note == "synthetic_demo":
                reflection = "【synthetic_demo】" + reflection

        res_date = None
        if metrics and metrics.get("exit_date"):
            res_date = str(metrics.get("exit_date"))[:10]
        rec = SettlementRecord(
            decision_id=did,
            session=session,
            instrument=instrument,
            horizon_days=int(horizon_days),
            benchmark=bench,
            raw_return=rr,
            alpha_vs_benchmark=aa,
            reflection_zh=reflection,
            settled_at=now,
            promotion_approved=False,
        )
        if res_date:
            rec["resolution_date"] = res_date  # type: ignore[typeddict-unknown-key]
            rec["exit_date"] = res_date  # type: ignore[typeddict-unknown-key]
        # dry_run means: do not fabricate returns (handled above). G5: only append
        # when settled or permanent coverage_gap — never for incomplete windows.
        _ = dry_run
        ledger.append_settlement(rec)
        out.append(rec)
    return out


def run_dry_run(
    *,
    instrument: str = "600519.SH",
    session: str = "2024-05-31",
    ledger_path: Path | None = None,
    settle: bool = True,
    synthetic_demo: bool = False,
    allow_synthetic_returns: bool = False,
) -> dict[str, Any]:
    """End-to-end research dry-run: debate → ledger → optional settle stub."""
    path = ledger_path or DEFAULT_DEBATE_LEDGER
    ledger = JsonlDebateLedger(path)
    prior_n = len(load_prior_settlements(ledger, instrument=instrument, limit=100))
    result = build_rule_debate(
        session=session,
        instrument=instrument,
        ledger=ledger,
        synthetic_demo=synthetic_demo,
    )
    entry = append_round(ledger, result)
    settlements: list[SettlementRecord] = []
    if settle:
        settlements = settle_pending(
            ledger,
            decision_id=entry.get("decision_id"),
            dry_run=True,
            allow_synthetic_returns=allow_synthetic_returns,
        )
    gaps = list(getattr(result, "_coverage_gaps", []) or [])
    return {
        "decision_id": entry.get("decision_id"),
        "session": entry.get("session"),
        "instrument": entry.get("instrument"),
        "rating": entry.get("rating"),
        "ledger_path": str(path),
        "turns": len(result.turns),
        "prior_settlements_read": prior_n,
        "settlements": [
            {
                "decision_id": s.get("decision_id"),
                "benchmark": s.get("benchmark"),
                "raw_return": s.get("raw_return"),
                "alpha_vs_benchmark": s.get("alpha_vs_benchmark"),
                "reflection_zh": (s.get("reflection_zh") or "")[:200],
            }
            for s in settlements
        ],
        "coverage_gaps": gaps,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_nav": True,
        "no_strategy_submit": True,
    }


def run_settle_batch(
    pairs: Sequence[tuple[str, str]],
    *,
    ledger_path: Path | None = None,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    synthetic_demo: bool = False,
) -> dict[str, Any]:
    """Debate+pending+real settle for many (instrument, session); research-only."""
    path = ledger_path or DEFAULT_DEBATE_LEDGER
    ledger = JsonlDebateLedger(path)
    debates: list[dict[str, Any]] = []
    settlements_non_null: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    decision_ids: list[str] = []

    for instrument, session in pairs:
        result = build_rule_debate(
            session=session,
            instrument=instrument,
            ledger=ledger,
            synthetic_demo=synthetic_demo,
        )
        entry = append_round(ledger, result)
        did = str(entry.get("decision_id") or "")
        decision_ids.append(did)
        debates.append(
            {
                "decision_id": did,
                "instrument": instrument,
                "session": session,
                "rating": entry.get("rating"),
                "turns": len(result.turns),
                "coverage_gaps": list(getattr(result, "_coverage_gaps", []) or []),
            }
        )
        metrics = compute_ashare_horizon_returns(
            instrument, session, horizon_days=horizon_days
        )
        if metrics.get("status") != "settled":
            # still write settlement with nulls / gap note so ledger is honest
            recs = settle_pending(
                ledger,
                decision_id=did,
                horizon_days=horizon_days,
                dry_run=True,
            )
            skipped.append(
                {
                    "decision_id": did,
                    "instrument": instrument,
                    "session": session,
                    "reason": metrics.get("status"),
                    "detail": metrics.get("reflection_zh"),
                    "settlement_written": bool(recs),
                }
            )
            continue
        recs = settle_pending(
            ledger,
            decision_id=did,
            horizon_days=horizon_days,
            dry_run=True,
            raw_return=float(metrics["raw_return"]),
            alpha_vs_benchmark=float(metrics["alpha_vs_benchmark"]),
        )
        for s in recs:
            settlements_non_null.append(
                {
                    "decision_id": s.get("decision_id"),
                    "instrument": s.get("instrument"),
                    "session": s.get("session"),
                    "horizon_days": s.get("horizon_days"),
                    "benchmark": s.get("benchmark"),
                    "raw_return": s.get("raw_return"),
                    "alpha_vs_benchmark": s.get("alpha_vs_benchmark"),
                    "entry_date": metrics.get("entry_date"),
                    "exit_date": metrics.get("exit_date"),
                    "settle_source": metrics.get("settle_source"),
                }
            )

    return {
        "ledger_path": str(path),
        "horizon_days": horizon_days,
        "benchmark": DEFAULT_BENCHMARK,
        "debate_rounds_added": len(debates),
        "decision_ids": decision_ids,
        "debates": debates,
        "non_null_settlements": settlements_non_null,
        "non_null_n": len(settlements_non_null),
        "skipped": skipped,
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_nav": True,
        "no_strategy_submit": True,
    }



def instruments_with_nonnull_settlement(
    ledger: JsonlDebateLedger,
) -> list[str]:
    """Distinct instruments that already have ≥1 non-null settlement."""
    rows = load_prior_settlements(ledger, non_null_only=True, limit=10_000)
    seen: list[str] = []
    for r in rows:
        inst = str(r.get("instrument") or "")
        if inst and inst not in seen:
            seen.append(inst)
    return seen


def run_memory_loop_batch(
    pairs: Sequence[tuple[str, str]],
    *,
    ledger_path: Path | None = None,
    horizon_days: int = DEFAULT_HORIZON_DAYS,
    prior_limit: int = 3,
    synthetic_demo: bool = False,
) -> dict[str, Any]:
    """New-session debate with memory injection → decision → settle if window full."""
    path = ledger_path or DEFAULT_DEBATE_LEDGER
    ledger = JsonlDebateLedger(path)
    debates: list[dict[str, Any]] = []
    settlements_non_null: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    decision_ids: list[str] = []

    for instrument, session in pairs:
        prior_n = len(
            load_prior_settlements(
                ledger,
                instrument=instrument,
                limit=prior_limit,
                non_null_only=True,
                as_of=session,
            )
        )
        result = build_rule_debate(
            session=session,
            instrument=instrument,
            ledger=ledger,
            prior_limit=prior_limit,
            synthetic_demo=synthetic_demo,
        )
        entry = append_round(ledger, result)
        did = str(entry.get("decision_id") or "")
        decision_ids.append(did)
        mem_ok = bool(getattr(result, "_memory_injected", False))
        # Evidence: bull/bear/RM theses contain memory marker
        role_has_mem = {}
        for t in result.turns:
            role = str(t.get("role"))
            thesis = str(t.get("thesis_zh") or "")
            refs = list(t.get("evidence_refs") or [])
            role_has_mem[role] = (
                "【记忆回灌" in thesis
                or any(str(r).startswith("memory:") for r in refs)
            )
        weight_ok = bool(getattr(result, "_weight_injected", False))
        role_has_wt = {}
        for t in result.turns:
            role = str(t.get("role"))
            thesis = str(t.get("thesis_zh") or "")
            refs = list(t.get("evidence_refs") or [])
            role_has_wt[role] = (
                "【权重上下文" in thesis
                or any(str(r).startswith("weight:") for r in refs)
            )
        debates.append(
            {
                "decision_id": did,
                "instrument": instrument,
                "session": session,
                "rating": entry.get("rating"),
                "turns": len(result.turns),
                "prior_nonnull_n": prior_n,
                "memory_injected": mem_ok,
                "memory_in_bull": role_has_mem.get("bull", False),
                "memory_in_bear": role_has_mem.get("bear", False),
                "memory_in_research_manager": role_has_mem.get("research_manager", False),
                "weight_injected": weight_ok,
                "weight_in_bull": role_has_wt.get("bull", False),
                "weight_in_bear": role_has_wt.get("bear", False),
                "weight_in_research_manager": role_has_wt.get("research_manager", False),
                "weight_in_analyst_market": role_has_wt.get("analyst_market", False),
                "weight_hit": getattr(result, "_weight_hit", None),
                "coverage_gaps": list(getattr(result, "_coverage_gaps", []) or []),
                "memory_block_head": str(getattr(result, "_memory_block", "") or "")[:220],
                "weight_block_head": str(getattr(result, "_weight_block", "") or "")[:220],
            }
        )
        metrics = compute_ashare_horizon_returns(
            instrument, session, horizon_days=horizon_days
        )
        if metrics.get("status") != "settled":
            recs = settle_pending(
                ledger,
                decision_id=did,
                horizon_days=horizon_days,
                dry_run=True,
            )
            skipped.append(
                {
                    "decision_id": did,
                    "instrument": instrument,
                    "session": session,
                    "reason": metrics.get("status"),
                    "detail": metrics.get("reflection_zh"),
                    "settlement_written": bool(recs),
                }
            )
            continue
        recs = settle_pending(
            ledger,
            decision_id=did,
            horizon_days=horizon_days,
            dry_run=True,
            raw_return=float(metrics["raw_return"]),
            alpha_vs_benchmark=float(metrics["alpha_vs_benchmark"]),
        )
        for s in recs:
            settlements_non_null.append(
                {
                    "decision_id": s.get("decision_id"),
                    "instrument": s.get("instrument"),
                    "session": s.get("session"),
                    "horizon_days": s.get("horizon_days"),
                    "benchmark": s.get("benchmark"),
                    "raw_return": s.get("raw_return"),
                    "alpha_vs_benchmark": s.get("alpha_vs_benchmark"),
                    "entry_date": metrics.get("entry_date"),
                    "exit_date": metrics.get("exit_date"),
                    "settle_source": metrics.get("settle_source"),
                }
            )

    injected_n = sum(1 for d in debates if d.get("memory_injected"))
    weight_n = sum(1 for d in debates if d.get("weight_injected"))
    fe_path, fe_meta = resolve_factor_evolve_weight_path()
    fe_rel = None
    if fe_path is not None:
        try:
            fe_rel = str(fe_path.relative_to(ROOT))
        except ValueError:
            fe_rel = str(fe_path)
    return {
        "mode": "memory_loop_weight_context",
        "ledger_path": str(path),
        "horizon_days": horizon_days,
        "benchmark": DEFAULT_BENCHMARK,
        "prior_limit_k": prior_limit,
        "debate_rounds_added": len(debates),
        "decision_ids": decision_ids,
        "debates": debates,
        "memory_injected_rounds": injected_n,
        "memory_injection_ok": injected_n == len(debates) and len(debates) > 0,
        "weight_injected_rounds": weight_n,
        "weight_injection_ok": weight_n == len(debates) and len(debates) > 0,
        "factor_evolve_weight_path": fe_rel,
        "factor_evolve_n_weight_rows": fe_meta.get("n_weight_rows"),
        "factor_evolve_run_id": fe_meta.get("run_id"),
        "non_null_settlements": settlements_non_null,
        "non_null_n": len(settlements_non_null),
        "skipped": skipped,
        "weight_table_cited": fe_rel
        or (
            str(OPTIONAL_WEIGHT_TABLE.relative_to(ROOT))
            if OPTIONAL_WEIGHT_TABLE.exists()
            else None
        ),
        "book_smoke_note": (
            "WeightLongTableSleeve 可解析 session,instrument_id,weight；"
            "本批仅文档对齐，不下单、不跑 Book-Smoke NAV。"
        ),
        "promotion_approved": False,
        "strategy_promotion_approved": False,
        "no_orders": True,
        "no_nav": True,
        "no_strategy_submit": True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AI debate+memory research stub")
    ap.add_argument("--dry-run", action="store_true", help="Run one debate+settle stub")
    ap.add_argument("--instrument", default="600519.SH")
    ap.add_argument("--session", default="2024-05-31")
    ap.add_argument("--ledger", type=Path, default=None)
    ap.add_argument("--no-settle", action="store_true")
    ap.add_argument(
        "--synthetic-demo",
        action="store_true",
        help="Allow labeled synthetic evidence if messages empty",
    )
    ap.add_argument(
        "--allow-synthetic-returns",
        action="store_true",
        help="Demo-only: fill raw/alpha with 0; default leaves null",
    )
    ap.add_argument(
        "--settle-batch",
        action="store_true",
        help="Run multi (instrument,session) debate+real settle vs 510300",
    )
    ap.add_argument(
        "--horizon-days",
        type=int,
        default=DEFAULT_HORIZON_DAYS,
        help="Pre-registered hold window (do not change post-hoc to fish scores)",
    )
    ap.add_argument(
        "--memory-loop",
        action="store_true",
        help="New sessions for instruments with prior non-null settlement; inject memory",
    )
    ap.add_argument(
        "--weight-context",
        action="store_true",
        help="Same as memory-loop plus QuantMind factor_evolve weight context injection",
    )
    ap.add_argument(
        "--g1g5",
        action="store_true",
        help="Run G1-G5 local PIT debate+full-window settle+daily weights",
    )
    ap.add_argument(
        "--prior-limit",
        type=int,
        default=3,
        help="K recent non-null settlements to inject into bull/bear/RM",
    )
    args = ap.parse_args(list(argv) if argv is not None else None)
    if getattr(args, "g1g5", False):
        from research.g1g5_wiring import run_g1g5

        meta = run_g1g5(
            horizon_days=int(args.horizon_days),
            max_debate_rounds=2,
            ledger_path=args.ledger,
        )
        slim = {k: meta[k] for k in meta if k != "debates"}
        slim["debates_n"] = len(meta.get("debates") or [])
        print(json.dumps(slim, ensure_ascii=False, indent=2))
        return 0
    if args.memory_loop or getattr(args, "weight_context", False):
        # Prefer symbols in factor_evolve weights AND/OR prior non-null settlement.
        # New sessions after prior settle windows; weight lookup uses asof ≤ session.
        pairs = [
            ("600519.SH", "2024-11-15"),  # weight+settlement history
            ("601318.SH", "2024-11-15"),
            ("000858.SZ", "2024-11-15"),
            ("600036.SH", "2024-12-20"),
            ("601166.SH", "2024-12-06"),  # in weight table + prior settle
        ]
        meta = run_memory_loop_batch(
            pairs,
            ledger_path=args.ledger,
            horizon_days=int(args.horizon_days),
            prior_limit=int(args.prior_limit),
            synthetic_demo=args.synthetic_demo,
        )
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return 0
    if args.settle_batch:
        # Mid/large CSI300-style names with D0 panel coverage; varied sessions.
        pairs = [
            ("600519.SH", "2024-06-28"),
            ("601318.SH", "2024-06-28"),
            ("000858.SZ", "2024-06-28"),
            ("600036.SH", "2024-09-30"),
            ("000333.SZ", "2024-09-30"),
            ("601166.SH", "2024-11-29"),
            ("002415.SZ", "2025-01-15"),
        ]
        meta = run_settle_batch(
            pairs,
            ledger_path=args.ledger,
            horizon_days=int(args.horizon_days),
            synthetic_demo=args.synthetic_demo,
        )
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return 0
    if not args.dry_run:
        ap.print_help()
        return 2
    meta = run_dry_run(
        instrument=args.instrument,
        session=args.session,
        ledger_path=args.ledger,
        settle=not args.no_settle,
        synthetic_demo=args.synthetic_demo,
        allow_synthetic_returns=args.allow_synthetic_returns,
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
