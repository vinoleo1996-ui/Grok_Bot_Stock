"""证据模型 — 参考 easy-stock《新闻事实与资料缺口的判断》政策

核心纪律:
1. 来源类型分离:公司披露 / 可复算数据 / 可追溯报道 / 第三方观点 / 系统推断
2. 可追溯(traceable)只描述出处的可检查性,不是真实性认证
3. 一条可靠报道只能支持一个限定事实;观点与传闻永不升级为事实
4. 口径明确:期间(2026Q3)、同比/环比、归母/扣非、单季/累计不得混用
5. 转载同稿不视为多源独立验证
6. 资料缺口(抓取失败/缺正文)不能单独作为反证或风险项
"""
from __future__ import annotations

import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    DISCLOSURE = "公司披露"      # 公告/财报/预告
    DATA = "可复算数据"          # 行情/K线/宏观读数
    REPORT = "可追溯报道"        # 有媒体、链接、时间的报道
    KOL = "第三方观点"           # 大V/机构观点(非事实)
    INFERENCE = "系统推断"       # 本系统的推理(非事实)


class Traceability(str, Enum):
    FULL = "充分"       # 有原文/完整口径/可复核
    LIMITED = "有限"    # 仅有标题/摘要或单一来源
    INSUFFICIENT = "不足"  # 缺出处/无时间/传闻


Impact = Literal["bull", "bear", "mixed", "neutral"]


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:10])
    source_type: SourceType
    title: str
    detail: str
    url: str | None = None
    publisher: str | None = None
    published_at: str | None = None
    retrieved_at: str
    traceability: Traceability
    impact: Impact = "neutral"
    strength: float = 0.5          # 0-1,证据强度
    sectors: list[str] = Field(default_factory=list)
    instruments: list[str] = Field(default_factory=list)
    caliber: str | None = None     # 口径,如 "2026年9月/同比"
    note: str | None = None
    dedupe_key: str | None = None
    scope: Literal["sector", "shared"] = "sector"   # shared=宏观/政策类,全板块共享

    @property
    def supports_fact(self) -> bool:
        """能否作为事实依据(观点与推断永远不能)"""
        return self.source_type in (SourceType.DISCLOSURE, SourceType.DATA, SourceType.REPORT) and \
            self.traceability in (Traceability.FULL, Traceability.LIMITED)


class EvidencePack(BaseModel):
    subject: str
    generated_at: str
    evidence: list[Evidence] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)   # 资料缺口:不进入反证

    def by_sector(self, sector: str) -> list[Evidence]:
        return [e for e in self.evidence if sector in e.sectors and e.scope == "sector"]

    def bulls(self) -> list[Evidence]:
        return [e for e in self.evidence if e.impact == "bull"]

    def bears(self) -> list[Evidence]:
        return [e for e in self.evidence if e.impact == "bear"]

    def factual(self) -> list[Evidence]:
        return [e for e in self.evidence if e.supports_fact]
