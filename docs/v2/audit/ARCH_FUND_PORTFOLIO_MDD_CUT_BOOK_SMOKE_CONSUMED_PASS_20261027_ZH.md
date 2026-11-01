# Arch fund MDD-cut Book-Smoke · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T23:48:30-04:00`（America/New_York；墙钟 `2026-10-27 23:48 ET`） |
| 主令 | 主 ~23:43 ET · fund MDD-cut Book-Smoke DONE → 只审/CONSUME（Eng RECEIPT `da43a1c5`；`.ok` `335635dd` / SIGNED `dcef54f8`；weights `601c5cf6` / summary `2021a06c`；peak≈733.2；主闸三臂×两AUM 全过；≠ACCEPT） |
| 结论 | **CONSUMED_PASS**（窗关闭归档；过程/钉 MATCH；主闸过但 ≤15% 对照未过 → **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**） |
| 审票 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` · 盘上 sha8 **`ba7609af`** · verdict=**PASS_WITH_CONDITIONS** |
| live / leo_notify / promotion | **false** / **false** / **false** |

## 0. 一句话

fund MDD-cut Book-Smoke（V_BALLAST_MIX · dark_horse_add · ALLA；EXECUTED=true；peak≈**733.2**≤1500；主臂 60万 **14.47%/−17.14%/Sh0.730**、100万 **13.17%/−20.14%/0.653**；主闸 |MDD|≤25%+CAGR≥C0 三臂×两AUM 全过；≤15% 对照全未过）经 Arch 只审 **PASS_WITH_CONDITIONS `ba7609af`** 后 **CONSUME**：live `.ok` **`335635dd`** 归档至 `_consumed/`（内容字节不变；pre=post sha8 **`335635dd`**）；QUIET **ABSENT**（无需 lift；未新建）；`book_smoke.py` **`1a5fa1aa` UNCHANGED**；weights **`601c5cf6`** 复用基线（**未** RESTORED `f08ce32c`）；CLI_GAP=`book_smoke_no_arch_ok_path` NOTE；**未**代跑；**未**新签；**未**改 weights/summary；**未**混叶38（CONSUMED_PASS **`c01c2034`** / 构建闸 **`5f694370`** 旁线维持；禁 RESTORED `f08ce32c`）；**未**碰叶39。**仍 ≠Book-Smoke ACCEPT**；**仍 ≠X2 ACCEPT**；禁 RESTORED 本票内容 **`335635dd`**。下一跳交主（HOLD / 再调 / 另令 X2；Arch 不自派）。

## 1. 核盘（消费时）

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| Eng RECEIPT | `da43a1c5` | **MATCH** · DONE · EXECUTED=**true** |
| 审票 RUN_REVIEW | **`ba7609af`** · PASS_WITH_CONDITIONS | **MATCH**（落盘后盘上） |
| SIGNED（盘上） | `dcef54f8`（文内 `d9771793` 勿采） | **MATCH** |
| FROZEN / RECEIPT / ArchFROZEN | `d489c937` / `058ec68e` / `2f039c3d` | **MATCH** |
| DRAFT / ArchDRAFT | `eeccb25e` / `41d4fc76` | **MATCH** |
| weights / summary | `601c5cf6` / `2021a06c` | **MATCH** |
| 三臂 summary | MAIN `cee57a6e` · ABL040 `a9a93906` · ABL060 `5834075a` | **MATCH** |
| mask / WHO / ALLA | `6ab6a305` / `547b246e` / `724e1df5` | **MATCH** |
| book_smoke.py | `1a5fa1aa` UNCHANGED | **MATCH** |
| overall peak_rss_mb | **733.2** ≤1500 | **MATCH** · 未抬 |
| QUIET | **ABSENT** | **MATCH** · 无需 lift · **未新建** |
| 叶38 CONSUME | `c01c2034` | **MATCH** · 旁线未碰 |
| 旧 who_pays live `.ok` | ABSENT | **MATCH** |
| sealed_claim / promotion | false / false | **MATCH** |

## 2. Headline（探索披露；≠ACCEPT）

| AUM | arm | BOOK CAGR | BOOK MDD | Sharpe | 主闸 | ≤15%对照 |
|---:|---|---:|---:|---:|:---:|:---:|
| 60万 | MAIN 0.50/0.50 | **14.47%** | **−17.14%** | 0.730 | **PASS** | fail |
| 100万 | MAIN 0.50/0.50 | **13.17%** | **−20.14%** | 0.653 | **PASS** | fail |
| 60万 | ABL 0.40/0.60 | 12.94% | −16.35% | 0.699 | **PASS** | fail |
| 100万 | ABL 0.40/0.60 | 13.07% | −17.34% | 0.676 | **PASS** | fail |
| 60万 | ABL 0.60/0.40 | 13.52% | −21.10% | 0.657 | **PASS** | fail |
| 100万 | ABL 0.60/0.40 | 13.24% | −22.49% | 0.634 | **PASS** | fail |

vs C0≈11.27%/−16.24%。相对基线 who_pays（MDD≈−32%）主臂 MDD 明显收窄。CLI_GAP=`book_smoke_no_arch_ok_path`（wrapper 预核；未改 `1a5fa1aa`）。

## 3. 归档 / QUIET

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_FUND_PORTFOLIO_MDD_CUT_BOOK_SMOKE_V_BALLAST_MIX.335635dd.CONSUMED_PASS.20261027T2348ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`335635dd`** / `335635dd982591db87dc6e6dddeb03d5385bde231eb67634248e6614e60a5de3`（pre=post；内容字节不变；**禁 RESTORED**） |
| live `.ok` | **ABSENT** |
| QUIET | **ABSENT** → 无需 lift；**未新建 QUIET**；未触 `_lifted/` |
| 叶38 | CONSUMED_PASS **`c01c2034` UNTOUCHED**；构建闸 **`5f694370`** 旁线；禁 RESTORED `f08ce32c`；禁混线 |
| 叶39 | **未碰**（排队旁线） |

## 4. 硬钉

- 本票 fund MDD-cut Book-Smoke **窗关闭归档**；**仍 ≠Book-Smoke ACCEPT**；**仍 ≠X2 ACCEPT**；本拍**不解阻 ACCEPT**
- 审票 **PASS_WITH_CONDITIONS `ba7609af`**：C1 主闸过但 ≤15% 对照未过 → 仅披露/禁纸面升；C2 CLI_GAP NOTE；C3 MDD 收窄仍须主裁 HOLD/再调/另令 X2；C4 X2 另令 / 禁混叶38 / 禁 RESTORED `f08ce32c`
- 禁复跑本票当 ACCEPT；禁抬帽；禁代跑；禁新签；禁改 weights / `1a5fa1aa`
- **禁 RESTORED** 本票内容 **`335635dd`**；禁 RESTORED who_pays `f08ce32c`
- **禁混叶38**：旁线 `c01c2034`/`5f694370` 维持；**不碰叶39**
- **下一跳交主决策**（HOLD / 再调 / 另令 X2）——**Arch 不自决 ACCEPT、不自派 X2、不自派再调案**
- **不报 Leo**（leo_notify=false）

## 5. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：HOLD / 再调 / 另令 X2（非本拍 ACCEPT）
      → X2 另令；Arch 不自派；≠Book-Smoke ACCEPT；≠X2 ACCEPT
      → CLI_GAP 生产适配另票；禁 RESTORED 335635dd / f08ce32c
      → 禁混叶38 c01c2034/5f694370；不碰叶39；禁 QUIET
```

live=false。
