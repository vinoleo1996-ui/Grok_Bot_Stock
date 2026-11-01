"""证据政策 — 充分度、独立来源、评分与评级"""
from __future__ import annotations

from .models import Evidence, EvidencePack, SourceType, Traceability

# 权重:不同来源类型对"方向性结论"的贡献
SOURCE_WEIGHT = {
    SourceType.DISCLOSURE: 1.0,
    SourceType.DATA: 0.9,
    SourceType.REPORT: 0.75,
    SourceType.KOL: 0.25,
    SourceType.INFERENCE: 0.2,
}

TRACE_WEIGHT = {Traceability.FULL: 1.0, Traceability.LIMITED: 0.6, Traceability.INSUFFICIENT: 0.2}


def weighted_score(e: Evidence) -> float:
    return e.strength * SOURCE_WEIGHT[e.source_type] * TRACE_WEIGHT[e.traceability]


def independent_sources(items: list[Evidence]) -> int:
    """独立来源数:按 publisher + dedupe_key 去重(转载同稿不算多源)"""
    events = {}
    for e in items:
        if not e.supports_fact:
            continue
        key=e.dedupe_key or e.title.strip()
        if key not in events or weighted_score(e)>weighted_score(events[key]):events[key]=e
    # Several stories from one publisher do not constitute independent confirmation.
    return len({e.publisher or e.url or e.id for e in events.values()})


def sufficiency(items: list[Evidence]) -> Traceability:
    """证据充分度:
    - 充分:≥2 个独立可追溯来源,且至少一个 FULL
    - 有限:1 个可追溯来源(FULL/LIMITED)
    - 不足:无可用来源(仅观点/推断/传闻)
    """
    factual = [e for e in items if e.supports_fact]
    if not factual:
        return Traceability.INSUFFICIENT
    indep = independent_sources(factual)
    has_full = any(e.traceability == Traceability.FULL for e in factual)
    if indep >= 2 and has_full:
        return Traceability.FULL
    return Traceability.LIMITED


def balance(pack: EvidencePack, sector: str | None = None) -> dict:
    """多空证据平衡度:sector 专属证据 + 共享证据(折价 0.5)"""
    if sector:
        items = list(pack.by_sector(sector)) + [e for e in pack.evidence if e.scope == "shared"]
        weight = lambda e: weighted_score(e) * (0.5 if e.scope == "shared" else 1.0)  # noqa: E731
    else:
        items = pack.evidence
        weight = weighted_score
    unique = {}
    for e in items:
        key = e.dedupe_key or e.title.strip()
        if key not in unique or weight(e) > weight(unique[key]):
            unique[key] = e
    items = list(unique.values())
    bull = sum(weight(e) for e in items if e.impact == "bull")
    bear = sum(weight(e) for e in items if e.impact == "bear")
    total = bull + bear
    return {
        "bull": round(bull, 3),
        "bear": round(bear, 3),
        "net": round(bull - bear, 3),
        "ratio": round(bull / total, 3) if total else 0.5,
        "n_bull": sum(1 for e in items if e.impact == "bull"),
        "n_bear": sum(1 for e in items if e.impact == "bear"),
    }


def rating_from_balance(net: float, total: float) -> tuple[str, str]:
    """信息面五级评级(非投资建议,仅信息面方向):
    强多 / 偏多 / 中性 / 偏空 / 强空
    """
    if total <= 0:
        return "中性", "无有效证据"
    score = net / max(total, 0.001)
    if score >= 0.35:
        return "强多", f"加权证据净值 {net:+.2f}(占比 {score:+.0%})"
    if score >= 0.12:
        return "偏多", f"加权证据净值 {net:+.2f}(占比 {score:+.0%})"
    if score <= -0.35:
        return "强空", f"加权证据净值 {net:+.2f}(占比 {score:+.0%})"
    if score <= -0.12:
        return "偏空", f"加权证据净值 {net:+.2f}(占比 {score:+.0%})"
    return "中性", f"加权证据净值 {net:+.2f}(多空接近平衡)"
