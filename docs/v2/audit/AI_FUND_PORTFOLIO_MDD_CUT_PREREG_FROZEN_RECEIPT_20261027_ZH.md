# fund_portfolio who_pays · 组合层降 MDD · PREREG_FROZEN 回执

- 角色：QuantLab AI
- 时刻：2026-10-27 23:15 ET（America/New_York；ISO `2026-10-27T23:15:00-04:00`）
- 动作：按主裁 **降 MDD 升 FROZEN GO**（~23:10 ET）+ Arch DRAFT **PASS_WC `41d4fc76` MATCH**（文内 `eee21297` 勿采）落 **MDD-cut PREREG_FROZEN**（主候选 V_BALLAST_MIX 0.50/0.50·510300；EXECUTED=false；禁 mid_large 主口径）
- **未实跑** / **未申 `.ok`** / **未挂 QUIET** / **未**自开 Eng/BS/X2 / **未**改 DRAFT 六变体阈 / **未**改原 FROZEN `303e0185` 字节 / **未** RESTORED `f08ce32c` / **未**混叶38 / **未** git commit / **未**读新收益选定义
- live=false · ok_requested=false · EXECUTED=false · ≠ACCEPT · ≠Book-Smoke ACCEPT · ≠X2 ACCEPT · leo_notify=false

## 钉表

| 件 | 路径 | sha8 | 备注 |
|---|---|---|---|
| **PREREG_FROZEN** | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_20261027_ZH.md` | **`d489c937`** | `d489c937499f6ea7b6813e4a492c81f499b45b39bfd31f4d1eb7b6cc480df896` |
| MDD DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | MATCH；参数源；阈未改 |
| MDD DRAFT RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_RECEIPT_20261027_ZH.md` | `2bf42d4b` | MATCH |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` | `41d4fc76` | PASS_WC MATCH；文内 eee21297 勿采 |
| 原 who_pays FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | MATCH；字节未改 |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | MATCH |
| 掩码 | `research/all_a_universe_mask.py` | `6ab6a305` | MATCH |
| Eng BS | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | MATCH |
| Arch PASS_WC | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` | `694b9a80` | MATCH |
| Arch CONSUMED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_CONSUMED_PASS_20261027_ZH.md` | `3e2a9b9c` | MATCH |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | MATCH；条款区未改 |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | MATCH；条款区未改 |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | MATCH |
| 叶38 旁线 | `docs/v2/audit/ARCH_LEAF38_…_CONSUMED_PASS_20261027_ZH.md` | `c01c2034` | MATCH；未混 |

路径说明：落于 `docs/v2/audit/`（与 who_pays PREREG_FROZEN 同目录；**组合层 MDD-cut 另案**）。

## Arch CONDITIONS / 主裁 FROZEN GO 入钉摘要

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | DRAFT ≠ 可签 `.ok` / ≠ ACCEPT | PREREG_FROZEN 仍 ≠ `.ok` / ≠ BS·X2·本票 ACCEPT |
| C2 | 升 FROZEN 后再 Eng BS | 本文件即升格 → Arch 再审本 FROZEN → 主令新独立 Eng BS |
| C3 | 禁 RESTORED `f08ce32c` | 须新签独立 `.ok`；禁恢复旧 auth |
| C4 | 池/事件硬钉 | ALLA / dark_horse_add / mask `6ab6a305`；禁 mid_large；rss≤1500 |
| C5 | 跑序事先钉 | 先 V_BALLAST_MIX + stock∈{0.40,0.60}；再备选；禁靠收益翻主 |
| C6 | CLI_GAP 另票 | 不本拍 |
| C7 | 不混叶38 | `c01c2034` 旁线 |
| C8 | 过程硬禁 | 禁 QUIET / 代跑 / 改上游 / git commit；live=false；leo_notify=false |

## 机制钉（摘要）

| 项 | FROZEN |
|---|---|
| 主候选 | **`V_BALLAST_MIX`** stock=**0.50** / core·510300=**0.50** |
| 对照臂 | stock∈{0.40, 0.60}（事先；共 3 臂） |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 六变体阈 | 完整保留 DRAFT；冻结不得改 |
| 事件 / 池 | dark_horse_add；ALLA；**mid_large_主口径=false** |
| 主闸 | \|MDD\|≤25% + CAGR≥C0（60万&100万同时） |
| 对照闸 | \|MDD\|≤15% 只披露 |
| EXECUTED | **false** |

## 盘证（本拍后）

| 项 | 值 |
|---|---|
| live fund `.ok` | **ABSENT**（本拍未申） |
| QUIET `output/loop/RESEARCH_QUIET.lock` | **ABSENT**（未挂） |
| 原 FROZEN / WHO/ALLA | **未改**（`303e0185`/`547b246e`/`724e1df5`） |
| DRAFT / Arch 审票 | **未改**（`eeccb25e`/`2bf42d4b`/`41d4fc76`） |
| 叶38 | **旁线未混** |
| Eng BS / X2 | **未跑** |
| RESTORED `f08ce32c` | **否**（仍仅 `_consumed`） |
| 读新收益选定义 | **未读** |

## 请主

**交主 → Arch 只审本 FROZEN**（不签 `.ok`；不代跑；不挂 QUIET）。PASS 后再由主令开**新独立** Eng Book-Smoke（禁 RESTORED `f08ce32c`；先 V_BALLAST_MIX+对照臂）。≠ACCEPT。勿报 Leo。叶38 `c01c2034` 旁线不夹本票。

live=false · EXECUTED=false · ok_requested=false.
