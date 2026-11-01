# Eng 回执：fund who_pays Book-Smoke 独立窗 — **BLOCKED_MISSING_AUTH**

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻 | `2026-10-27T22:25:45-04:00`（墙钟 `2026-10-27 22:25 ET`；America/New_York） |
| 主令 | 2026-10-27 ~22:22 ET · fund who_pays Arch FROZEN 只审 **PASS_WC `bcbe4b72` MATCH** → **GO Book-Smoke 独立窗**（本拍先 BS；X2 另令） |
| **结论** | **BLOCKED_MISSING_AUTH** — 缺本窗 `ARCH_RUN_AUTH`；**未**自签；**未**代跑 Book-Smoke / 读收益；**未**混叶38 |
| EXECUTED | **false** |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | 确认 |
| live / promotion / leo_notify | false / false / false |

## 0. 一句话

主 GO Book-Smoke 独立窗已认；上游钉 **12/12 MATCH**（FROZEN **`303e0185`** / RECEIPT **`df153eb9`** / ArchFROZEN **`bcbe4b72`**；WHO **`547b246e`** / ALLA **`724e1df5`** / 掩码 **`6ab6a305`**；主变体 **dark_horse_add**；gate_pass=true；EXECUTED=false）。盘上 **无** fund who_pays / Book-Smoke 专用 `ARCH_RUN_AUTH*.ok`。按主硬钉「若缺 ARCH_RUN_AUTH 先报主，勿自签」→ **停跑报主**，请主令 Arch **另排本窗独立 `.ok` 签窗**（钉 FROZEN `303e0185`；ALLA 掩码 `6ab6a305` 判定日；禁 mid_large；禁混叶38 `794f6578`；rss≤1500 禁抬）。**未**消费 `ARCH_RUN_AUTH_FUNDPORT_STREAM_IMPL_REVIEW_v1_1_r2.ok`（流实现审，≠本 who_pays BS）。

## 1. 上游钉复算

| 件 | 路径 | 期望 | 实测 | 结果 |
|---|---|---|---|---|
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH** |
| FROZEN_RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `df153eb9` | `df153eb9` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH** |
| DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` | `7cfbb3e5` | `7cfbb3e5` | **MATCH** |
| ArchDRAFT | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `985564ee` | `985564ee` | **MATCH** |
| C1C2 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | `5f7ff5a6` | **MATCH** |
| C2_RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| C2_JSON | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| C2_events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| mask | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |

全表 MATCH = **true**

## 2. AUTH / QUIET / 旁线盘证

| 项 | 结果 |
|---|---|
| fund who_pays / Book-Smoke `ARCH_RUN_AUTH*.ok` | **ABSENT**（live 候选：[]） |
| `ARCH_RUN_AUTH_FUNDPORT_STREAM_IMPL_REVIEW_v1_1_r2.ok` | 存在于 `output/data/` — **未消费**（≠本窗；流实现审） |
| 叶38 live `.ok` `794f6578` 路径 | `PRESENT` — **旁线不混**（未打开未消费） |
| `RESEARCH_QUIET.lock` | **ABSENT**（禁挂） |
| 自签 fund `.ok` | **未做** |
| Book-Smoke / 收益读盘 / 计数重跑 | **未做** |
| mid_large 主口径 | **未改回**（仍钉 ALLA） |

## 3. 禁项回执

- 禁改回 mid_large；禁自签 fund `.ok`；禁挂 QUIET；禁混叶38（叶38 真跑中 `.ok` `794f6578`）
- 禁抬 rss；禁把 gate_pass/Book-Smoke 当 ACCEPT；禁 live/晋级
- 本拍：**未**跑 `quantlab/portfolio/book_smoke.py`；**未**读 parquet 收益；**未** git commit

## 4. 请主下一跳

1. 令 Arch **另签**本窗独立 `ARCH_RUN_AUTH`（建议名含 `FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE` / `DARK_HORSE_ADD`；钉 FROZEN `303e0185` + ArchFROZEN `bcbe4b72` + 掩码 `6ab6a305`；主变体 dark_horse_add；ALLA 判定日；rss≤1500；禁 mid_large；禁混叶38）  
2. 主 MATCH `.ok` 后再令 Eng **GO 真跑 Book-Smoke**（X2 仍另令）  
3. Eng 纸面待机维持；cand4 PR#7 HOLD；cand3 仍禁

## 5. 文末钉

| 项 | 值 |
|---|---|
| 本回执 | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_BLOCKED_AUTH_20261027_ZH.md` |
| 结论 | **BLOCKED_MISSING_AUTH** |
| 上游 | FROZEN `303e0185` / RECEIPT `df153eb9` / ArchFROZEN `bcbe4b72` |
| pins_match | true |
| EXECUTED / ≠ACCEPT | false / 确认 |
| leo_notify / live | false / false |
