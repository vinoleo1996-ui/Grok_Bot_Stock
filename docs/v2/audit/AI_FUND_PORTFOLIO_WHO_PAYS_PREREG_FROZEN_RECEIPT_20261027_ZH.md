# fund_portfolio who_pays · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 22:14 ET（America/New_York；ISO `2026-10-27T22:14:00-04:00`）
- 动作：按主裁 **C2=A · FROZEN GO**（~22:11 ET）+ Arch DRAFT **PASS_WC** `985564ee` 落 **PREREG_FROZEN**（dark_horse_add；ALLA；EXECUTED=false；禁 mid_large 主口径）
- **未实跑** / **未申 `.ok`** / **未挂 QUIET** / **未**自派 X2 / Book-Smoke / **未**重跑计数 / **未**读收益 / **未** git commit / **未**改 WHO/ALLA 条款区 / **未**混叶38
- live=false · ok_requested=false · EXECUTED=false · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 全长 / 备注 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | **`303e0185`** | `303e01850ab2ed3966a823deb1b8ce07e43da2dbff901593134763e89b95f9e0` |
| who_pays DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` | `7cfbb3e5` | MATCH |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `985564ee` | PASS_WC MATCH |
| Arch C1C2 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | MATCH |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | MATCH |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | MATCH |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | MATCH |
| WHO 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | MATCH；条款区未改 |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | MATCH；条款区未改 |
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | MATCH；startswith=True |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | MATCH；startswith=True |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | MATCH |
| 掩码脚本 | `research/all_a_universe_mask.py` | `6ab6a305` | MATCH |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | MATCH |
| AE parquet | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | MATCH |
| Data RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | MATCH |

路径说明：落于 `docs/v2/audit/`（与叶 who_pays PREREG_FROZEN 同目录；**fund 机制**，非叶38 overlay）。

## Arch CONDITIONS / 主裁 C2=A 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | DRAFT ≠ 可签 `.ok` / ≠ X2 ACCEPT | PREREG_FROZEN 仍 ≠ `.ok` / ≠ X2 ACCEPT；须主令另开 Eng 窗 |
| **C2** | 路径 A 或 B | 主裁 **C2=A** → DRAFT 升 FROZEN（本文件）→ Arch 再审 FROZEN → 再开 X2 |
| C3 | Eng 池硬钉 ALLA | mask `6ab6a305` 判定日；禁 mid_large 主口径；禁计数无池滤、X2 再滤 |
| C4 | 过程硬禁 | 禁签 `.ok`；禁 QUIET；禁自派 X2/Book-Smoke；**禁混叶38**；禁抬 rss；live=false |
| C5 | 轻量闸 ≠ 收益验收 | gate_pass 仅放行讨论/开窗；终判 Eng Book-Smoke；本拍未读收益 |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| mechanism | `g1g5_ashare_fund_portfolio_v1` / ALLA `…_v1_allA` |
| 主变体 | **dark_horse_add**（crowd 备选；优先级先 DH 后 crowd） |
| 池 | ALLA 可交易；**mid_large_主口径=false** |
| PIT | ann_date 次一交易日 09:00；判定日=季末后第 16 交易日；加仓≥20%/新进前十大；T2 入场持 60 日 |
| 计数闸（引用 C2） | gate_pass=true；DH X2 股 2835；年 1727/2007/1614；全压舱 1.65%；peak≈249.2≪1500 |
| 硬闸 | Jaccard/ρ/α/组合门/成本·衰减/RSS≤1.5GB（WHO）；≠本票 ACCEPT |
| X2 窗意向 | 2024-01-02 → 2026-10-09 |
| EXECUTED | **false** |

## 盘证（本拍后）

| 项 | 值 |
|---|---|
| live fund `.ok` | **ABSENT**（本拍未申） |
| QUIET `output/loop/RESEARCH_QUIET.lock` | **ABSENT**（未挂） |
| WHO/ALLA 条款区 | **未改**（`547b246e`/`724e1df5`；前缀 startswith 保持） |
| DRAFT / C2 / 前缀 / NOTE | **未改** |
| 叶38 | **旁线未混**（未打开未改 leaf38 产物） |
| X2 / Book-Smoke / 计数重跑 | **未跑** |
| 读收益 | **未读** |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再由主令开 Eng Book-Smoke / X2 独立窗。≠X2 ACCEPT。勿报 Leo。叶38 旁线不夹本票。

live=false · EXECUTED=false · ok_requested=false.
