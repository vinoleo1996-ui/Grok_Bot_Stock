# Arch 审阅：fund who_pays Book-Smoke 真跑（只审；CONSUME 另票）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器只审） |
| 时刻 | `2026-10-27T22:48:20-04:00`（America/New_York；墙钟 `2026-10-27 22:48 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **只审**本窗 Book-Smoke 真跑；**不代跑**；**不重算**收益；**不改** weights / `book_smoke.py`；**不新签** `.ok`；**不挂 QUIET**；**未混叶38**；**≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；live=false；promotion=false；**leo_notify=false** |
| 触发 | 主 ~22:43 ET：Eng DONE RECEIPT **`b013a7a8` MATCH** → Arch **只审并 CONSUME**（MDD 破 25%；本票 **≠密封 ACCEPT**） |

## 0. 一句话

Eng Book-Smoke **DONE**（EXECUTED=**true**；RECEIPT **`b013a7a8`**；`.ok` live **`f08ce32c`** / SIGNED 盘 **`c0a8099b`**（文内自称 `fe0a9383` **勿采**）；weights **`601c5cf6`** / summary **`0d1ddcb0`**；OUT `…/20261027_223826/`；peak≈**651.9**≤1500；QUIET **ABSENT**；`book_smoke.py` **`1a5fa1aa` UNCHANGED**；CLI_GAP=`book_smoke_no_arch_ok_path` wrapper 预核可接受本窗；禁 mid_large；未混叶38）——**过程/钉/纪律可过**。内容侧 Headline：60万 BOOK CAGR **13.65%** / MDD **−32.07%**；100万 BOOK CAGR **15.55%** / MDD **−32.85%**（绝对值均 **> Leo 25% 硬闸**）→ **PASS_WITH_CONDITIONS**；**禁** Book-Smoke ACCEPT / 纸面升 / X2 ACCEPT；本票仅 entry ticket / 探索披露。建议主裁：**CONSUME** 本窗 `.ok`（本拍执行）→ 下一跳 **HOLD 或令 AI/Eng 另案降 MDD**（Arch **不自派**）；X2 **另令**。

## 1. 核盘 MATCH 表（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| Eng RECEIPT | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | `b013a7a8` | **MATCH** |
| `.ok` live | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.ok` | `f08ce32c` | `f08ce32c` | **MATCH**（消费前） |
| SIGNED（盘上） | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md` | `c0a8099b` | `c0a8099b` | **MATCH**（文内 `fe0a9383` **勿采**） |
| weights | `…/20261027_223826/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` | `601c5cf6` | `601c5cf6` | **MATCH** |
| summary | `…/20261027_223826/book_smoke_summary.json` | `0d1ddcb0` | `0d1ddcb0` | **MATCH** |
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH** |
| mask | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` | `1a5fa1aa` | `1a5fa1aa` | **MATCH · UNCHANGED** |
| peak_rss_mb.txt | OUT `peak_rss_mb.txt` | ≈651.9 | **651.9** | **MATCH**（≤1500；未抬） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| 叶38 live `.ok` | leaf38 HILIQ `.ok` | ABSENT | ABSENT | **MATCH** |
| 叶38 CONSUME | `…LEAF38…B1_PUSHDOWN…CONSUMED_PASS…` | `c01c2034` | `c01c2034` | **MATCH · 旁线未碰** |

`.ok` 全长 sha256=`f08ce32c5566030e48e941039f09ead5c4a7a4e8828f457ae2f15309cfe63817`。

## 2. Headline 复核（从 summary `0d1ddcb0`；本审不重算）

| AUM | arm | CAGR | MDD | Sharpe | cost/AUM |
|---:|---|---:|---:|---:|---:|
| 60万 | X2/BOOK | **0.1365**（13.65%） | **−0.3207**（−32.07%） | 0.581 | 0.0296 |
| 60万 | X2/C0 | 0.1127 | −0.1624 | 0.651 | 0.0002 |
| 100万 | X2/BOOK | **0.1555**（15.55%） | **−0.3285**（−32.85%） | 0.628 | 0.0336 |
| 100万 | X2/C0 | 0.1127 | −0.1624 | 0.651 | 0.0002 |

与主令披露一致。`sealed_claim=false`；`strategy_promotion_approved=false`；EXECUTED=**true**（Eng RECEIPT + wrapper_result）。

| 项 | 值 |
|---|---|
| OUT | `output/ai_factory/_fund_portfolio_who_pays_book_smoke_dark_horse_add/20261027_223826/` |
| 主变体 / 池 | **dark_horse_add** / **ALLA**（禁 mid_large 主口径） |
| peak_rss_mb | **651.9** ≤1500（未抬帽） |
| CLI_GAP | `book_smoke_no_arch_ok_path`（wrapper 预核 `.ok`；**未改** `1a5fa1aa`） |
| sealed_claim / promotion | **false** / **false** |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **true** / **true** |

## 3. CONDITIONS（强制）

| # | 条件 | 本审 | 状态 |
|---|---|---|---|
| **C1** | MDD 60万 **−32.07%** / 100万 **−32.85%** 绝对值均 **>25%**（Leo 硬闸） | → **禁** Book-Smoke ACCEPT / 纸面升 / X2 ACCEPT；本票仅 entry ticket / 探索披露 | **认（硬闸未过）** |
| **C2** | CLI_GAP=`book_smoke_no_arch_ok_path` | wrapper 预核可接受本窗；生产 CLI 适配另票听主/Eng；**未**改 `book_smoke.py` `1a5fa1aa` | **NOTE（可接受本窗）** |
| **C3** | CAGR 高于 C0（C0≈11.27% / MDD≈−16.2%）但 BOOK MDD 恶化显著 | 需风控/仓位/约束再设计后才可谈下一窗；Arch **不自派** | **认（内容侧）** |
| **C4** | X2 另令；禁自开；禁混叶38 | 本拍未开 X2；叶38 CONSUMED_PASS **`c01c2034`** 旁线维持未碰；禁 RESTORED 叶38 `794f6578` | **认（本拍遵守）** |

## 4. 建议主裁下一跳

1. **CONSUME** 本窗 live `.ok` **`f08ce32c`**（本拍执行；内容字节不变归档）  
2. 下一跳：**HOLD** 或令 **AI/Eng 另案降 MDD**（非本拍 ACCEPT；Arch **不自派**）  
3. **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；X2 **另令**  
4. 叶38 旁线 **`c01c2034`** 维持；禁混线；禁 RESTORED `f08ce32c` / `794f6578`

本票：**PASS_WITH_CONDITIONS**；**不代跑**；**不新签**；**不挂 QUIET**；**≠ACCEPT**；leo_notify=false；live=false。

## 5. 禁项回执（本回合审段）

- 未代跑 Book-Smoke；未重算收益；未改 weights；未改 `book_smoke.py` `1a5fa1aa`  
- 未挂 QUIET；未新签 `.ok`；未 RESTORED 叶38 `794f6578`  
- 未把 gate_pass / Book-Smoke DONE / 本审 当 ACCEPT  
- 未 mid_large；未混叶38；叶38 CONSUME `c01c2034` 未改  
- live=false；promotion=false；leo_notify=false；sealed_claim=false

## 6. 关键发现摘要

| 项 | 值 |
|---|---|
| 过程/钉/纪律 | **PASS**（全钉 MATCH；EXECUTED=true；peak≤1500；QUIET ABSENT） |
| 内容侧 MDD | **破 25%**（60万 −32.07%；100万 −32.85%） |
| 结论 | **PASS_WITH_CONDITIONS** |
| sealed_claim | **false** |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **true** / **true** |
| CLI_GAP | `book_smoke_no_arch_ok_path`（NOTE） |
| 叶38 | 旁线 **`c01c2034` UNTOUCHED** |

> 落盘后以**盘上 sha8**为准；文内若自算不一致注明勿采。
