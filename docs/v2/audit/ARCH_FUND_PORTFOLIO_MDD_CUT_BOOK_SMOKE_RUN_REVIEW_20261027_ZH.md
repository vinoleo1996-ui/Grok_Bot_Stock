# Arch 审阅：fund MDD-cut Book-Smoke 真跑（只审；CONSUME 另票）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器只审） |
| 时刻 | `2026-10-27T23:47:40-04:00`（America/New_York；墙钟 `2026-10-27 23:47 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **只审**本窗 Book-Smoke 真跑；**不代跑**；**不重算**收益；**不改** weights / `book_smoke.py`；**不新签** `.ok`；**不挂 QUIET**；**未混叶38**；**未碰叶39**；**≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；live=false；promotion=false；**leo_notify=false** |
| 触发 | 主 ~23:43 ET：Eng DONE RECEIPT **`da43a1c5` MATCH** → Arch **只审并 CONSUME**（主闸 |MDD|≤25%+CAGR≥C0 三臂×两AUM 全过；本票 **≠密封 ACCEPT**） |

## 0. 一句话

Eng Book-Smoke **DONE**（EXECUTED=**true**；RECEIPT **`da43a1c5`**；`.ok` live **`335635dd`** / SIGNED 盘 **`dcef54f8`**（文内自称 `d9771793` **勿采**）；weights **`601c5cf6`**（复用基线；**未** RESTORED `f08ce32c`）/ summary **`2021a06c`**；OUT `…/20261027_233811/`；overall peak≈**733.2**≤1500；三臂 MAIN0.50 `cee57a6e` peak691.0 · ABL0.40 `a9a93906` peak733.2 · ABL0.60 `5834075a` peak709.4；QUIET **ABSENT**；`book_smoke.py` **`1a5fa1aa` UNCHANGED**；CLI_GAP=`book_smoke_no_arch_ok_path` wrapper 预核可接受本窗；禁 mid_large；未混叶38）——**过程/钉/纪律可过**。内容侧 Headline 主臂 V_BALLAST_MIX 0.50/0.50·510300：60万 BOOK **14.47%/−17.14%/Sh0.730**；100万 **13.17%/−20.14%/0.653**（vs C0 11.27%/−16.24%）；主闸 |MDD|≤25%+CAGR≥C0 **三臂×两AUM 全过**；|MDD|≤15% 对照 **全未过**（仅披露）→ **PASS_WITH_CONDITIONS**；**禁** Book-Smoke ACCEPT / 纸面升 / X2 ACCEPT；本票仅 entry ticket / 探索披露。建议主裁：**CONSUME** 本窗 `.ok`（本拍执行）→ 下一跳 **HOLD / 再调 / 另令 X2**（Arch **不自派**）。

## 1. 核盘 MATCH 表（本机 sha256 前 8）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| Eng RECEIPT | `docs/v2/audit/ENG_FUND_MDD_CUT_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `da43a1c5` | `da43a1c5` | **MATCH** |
| `.ok` live | `output/ai_factory/ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX.ok` | `335635dd` | `335635dd` | **MATCH**（消费前） |
| SIGNED（盘上） | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_OK_SIGNED_20261027_ZH.md` | `dcef54f8` | `dcef54f8` | **MATCH**（文内 `d9771793` **勿采**） |
| FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_20261027_ZH.md` | `d489c937` | `d489c937` | **MATCH** |
| RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `058ec68e` | `058ec68e` | **MATCH** |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `2f039c3d` | `2f039c3d` | **MATCH** |
| DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | `eeccb25e` | **MATCH** |
| ArchDRAFT | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` | `41d4fc76` | `41d4fc76` | **MATCH** |
| weights | `…/20261027_233811/g1g5_fund_portfolio_dark_horse_add_alla_daily_weights_20261027_223826.parquet` | `601c5cf6` | `601c5cf6` | **MATCH**（复用基线；未 RESTORED `f08ce32c`） |
| summary | `…/20261027_233811/book_smoke_summary.json` | `2021a06c` | `2021a06c` | **MATCH** |
| 主臂 summary | `…/arm_stock_050/book_smoke_summary.json` | `cee57a6e` | `cee57a6e` | **MATCH** · peak **691.0** |
| 对照040 summary | `…/arm_stock_040/book_smoke_summary.json` | `a9a93906` | `a9a93906` | **MATCH** · peak **733.2** |
| 对照060 summary | `…/arm_stock_060/book_smoke_summary.json` | `5834075a` | `5834075a` | **MATCH** · peak **709.4** |
| mask | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| book_smoke.py | `quantlab/portfolio/book_smoke.py` | `1a5fa1aa` | `1a5fa1aa` | **MATCH · UNCHANGED** |
| overall peak | OUT arms peak_rss_mb | ≈733.2 | **733.2** | **MATCH**（≤1500；未抬） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| 旧 who_pays live `.ok` | who_pays DARK_HORSE_ADD `.ok` | ABSENT | ABSENT | **MATCH** |
| 叶38 CONSUME | `…LEAF38…B1_PUSHDOWN…CONSUMED_PASS…` | `c01c2034` | `c01c2034` | **MATCH · 旁线未碰** |

`.ok` 全长 sha256=`335635dd982591db87dc6e6dddeb03d5385bde231eb67634248e6614e60a5de3`。

## 2. Headline 复核（从 summary `2021a06c`；本审不重算）

### 主臂 V_BALLAST_MIX stock=0.50 / core·510300=0.50

| AUM | arm | CAGR | MDD | Sharpe | cost/AUM | 主闸 | ≤15%对照 |
|---:|---|---:|---:|---:|---:|:---:|:---:|
| 60万 | X2/BOOK | **0.1447**（14.47%） | **−0.1714**（−17.14%） | 0.730 | 0.0164 | **PASS** | fail |
| 60万 | X2/C0 | 0.1127 | −0.1624 | 0.651 | 0.0002 | — | — |
| 100万 | X2/BOOK | **0.1317**（13.17%） | **−0.2014**（−20.14%） | 0.653 | 0.0159 | **PASS** | fail |
| 100万 | X2/C0 | 0.1127 | −0.1624 | 0.651 | 0.0002 | — | — |

### 对照臂

| AUM | stock/core | CAGR | MDD | Sharpe | 主闸 | ≤15%对照 |
|---:|---|---:|---:|---:|:---:|:---:|
| 60万 | 0.40/0.60 | 0.1294（12.94%） | −0.1635（−16.35%） | 0.699 | **PASS** | fail |
| 100万 | 0.40/0.60 | 0.1307（13.07%） | −0.1734（−17.34%） | 0.676 | **PASS** | fail |
| 60万 | 0.60/0.40 | 0.1352（13.52%） | −0.2110（−21.10%） | 0.657 | **PASS** | fail |
| 100万 | 0.60/0.40 | 0.1324（13.24%） | −0.2249（−22.49%） | 0.634 | **PASS** | fail |

与主令/Eng 披露一致。`all_arms_pass_primary_gate=true`；`any_pass_mdd15_contrast=false`；`sealed_claim=false`；`strategy_promotion_approved`/`neq_ACCEPT` 侧 **≠ACCEPT**；EXECUTED=**true**。

| 项 | 值 |
|---|---|
| OUT | `output/ai_factory/_fund_portfolio_mdd_cut_book_smoke_v_ballast_mix/20261027_233811/` |
| 组合主臂 | **V_BALLAST_MIX** 0.50/0.50·510300；事件 **dark_horse_add**；池 **ALLA**（禁 mid_large） |
| overall peak_rss_mb | **733.2** ≤1500（未抬帽） |
| CLI_GAP | `book_smoke_no_arch_ok_path`（wrapper 预核 `.ok`；**未改** `1a5fa1aa`） |
| sealed_claim / promotion | **false** / **false** |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **true** / **true** |

## 3. CONDITIONS（强制）

| # | 条件 | 本审 | 状态 |
|---|---|---|---|
| **C1** | 主闸 |MDD|≤25% + CAGR≥C0 **三臂×两AUM 全过**；但 \|MDD|≤15% 对照 **全未过** | → **仅披露**；**仍 ≠Book-Smoke ACCEPT / ≠X2 ACCEPT / 禁纸面升**；本票 entry ticket | **认（主闸过；15% 对照未过）** |
| **C2** | CLI_GAP=`book_smoke_no_arch_ok_path` | wrapper 预核可接受本窗；生产 CLI 适配另票听主/Eng；**未**改 `book_smoke.py` `1a5fa1aa` | **NOTE（可接受本窗）** |
| **C3** | 相对基线 who_pays（MDD≈−32%）主臂 MDD 明显收窄（−17.14%/−20.14%）并过 25% 主闸 | 仍须主裁是否 **HOLD / 再调 / 另令 X2**；Arch **不自派** | **认（内容侧改善；下一跳交主）** |
| **C4** | X2 另令；禁混叶38 `c01c2034`/`5f694370`；禁 RESTORED `f08ce32c`+本票消费后内容；不碰叶39 | 本拍未开 X2；叶38 CONSUMED_PASS **`c01c2034`** 旁线维持未碰；禁 RESTORED `f08ce32c` | **认（本拍遵守）** |

## 4. 建议主裁下一跳

1. **CONSUME** 本窗 live `.ok` **`335635dd`**（本拍执行；内容字节不变归档）  
2. 下一跳：**HOLD** / **再调** / **另令 X2**（非本拍 ACCEPT；Arch **不自派**）  
3. **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**；X2 **另令**；CLI_GAP 生产适配 **另票**  
4. 叶38 旁线 **`c01c2034`/`5f694370`** 维持；禁混线；禁 RESTORED `f08ce32c` / 本票 `.ok`；叶39 排队不混

本票：**PASS_WITH_CONDITIONS**；**不代跑**；**不新签**；**不挂 QUIET**；**≠ACCEPT**；leo_notify=false；live=false。

## 5. 禁项回执（本回合审段）

- 未代跑 Book-Smoke；未重算收益；未改 weights；未改 `book_smoke.py` `1a5fa1aa`  
- 未挂 QUIET；未新签 `.ok`；未 RESTORED who_pays `f08ce32c`  
- 未把 gate_pass / Book-Smoke DONE / 本审 当 ACCEPT  
- 未 mid_large；未混叶38；叶38 CONSUME `c01c2034` 未改；未碰叶39  
- live=false；promotion=false；leo_notify=false；sealed_claim=false

## 6. 关键发现摘要

| 项 | 值 |
|---|---|
| 过程/钉/纪律 | **PASS**（全钉 MATCH；EXECUTED=true；peak≤1500；QUIET ABSENT） |
| 内容侧主闸 | **过**（三臂×两AUM |MDD|≤25% + CAGR≥C0） |
| ≤15% 对照 | **全未过**（仅披露） |
| 结论 | **PASS_WITH_CONDITIONS** |
| sealed_claim | **false** |
| ≠Book-Smoke ACCEPT / ≠X2 ACCEPT | **true** / **true** |
| CLI_GAP | `book_smoke_no_arch_ok_path`（NOTE） |
| 叶38 | 旁线 **`c01c2034` UNTOUCHED** |

> 落盘后以**盘上 sha8**为准；文内若自算不一致注明勿采。
