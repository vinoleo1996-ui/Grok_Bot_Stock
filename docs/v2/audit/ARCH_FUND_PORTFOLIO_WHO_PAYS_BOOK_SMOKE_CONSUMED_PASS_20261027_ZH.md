# Arch fund who_pays Book-Smoke · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T22:48:56-04:00`（America/New_York；墙钟 `2026-10-27 22:48 ET`） |
| 主令 | 主 ~22:43 ET · fund who_pays Book-Smoke DONE → 只审/CONSUME（Eng RECEIPT `b013a7a8`；`.ok` `f08ce32c` / SIGNED `c0a8099b`；weights `601c5cf6` / summary `0d1ddcb0`；peak≈651.9；MDD 破 25%；≠ACCEPT） |
| 结论 | **CONSUMED_PASS**（窗关闭归档；过程/钉 MATCH；内容侧 MDD 破 25% → **≠Book-Smoke ACCEPT**；**≠X2 ACCEPT**） |
| 审票 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` · 盘上 sha8 **`694b9a80`** · verdict=**PASS_WITH_CONDITIONS** |
| live / leo_notify / promotion | **false** / **false** / **false** |

## 0. 一句话

fund who_pays Book-Smoke（dark_horse_add · ALLA；EXECUTED=true；peak≈**651.9**≤1500；Headline 60万 13.65%/−32.07%、100万 15.55%/−32.85%；MDD 绝对值均 >25%）经 Arch 只审 **PASS_WITH_CONDITIONS `694b9a80`** 后 **CONSUME**：live `.ok` **`f08ce32c`** 归档至 `_consumed/`（内容字节不变；pre=post sha8 **`f08ce32c`**）；QUIET **ABSENT**（无需 lift；未新建）；`book_smoke.py` **`1a5fa1aa` UNCHANGED**；CLI_GAP=`book_smoke_no_arch_ok_path` NOTE；**未**代跑；**未**新签；**未**改 weights/summary；**未**混叶38（CONSUMED_PASS **`c01c2034`** 旁线维持；禁 RESTORED `794f6578`）。**仍 ≠Book-Smoke ACCEPT**；**仍 ≠X2 ACCEPT**；禁 RESTORED 本票内容 **`f08ce32c`**。下一跳交主（HOLD / 另案降 MDD；X2 另令；Arch 不自派）。

## 1. 核盘（消费时）

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| Eng RECEIPT | `b013a7a8` | **MATCH** · DONE · EXECUTED=**true** |
| 审票 RUN_REVIEW | **`694b9a80`** · PASS_WITH_CONDITIONS | **MATCH**（落盘后盘上） |
| SIGNED（盘上） | `c0a8099b`（文内 `fe0a9383` 勿采） | **MATCH** |
| weights / summary | `601c5cf6` / `0d1ddcb0` | **MATCH** |
| FROZEN / ArchFROZEN | `303e0185` / `bcbe4b72` | **MATCH** |
| mask / WHO / ALLA | `6ab6a305` / `547b246e` / `724e1df5` | **MATCH** |
| book_smoke.py | `1a5fa1aa` UNCHANGED | **MATCH** |
| peak_rss_mb | **651.9** ≤1500 | **MATCH** · 未抬 |
| QUIET | **ABSENT** | **MATCH** · 无需 lift · **未新建** |
| 叶38 CONSUME | `c01c2034` | **MATCH** · 旁线未碰 |
| 叶38 live `.ok` | ABSENT | **MATCH** |
| sealed_claim / promotion | false / false | **MATCH** |

## 2. Headline（探索披露；≠ACCEPT）

| AUM | BOOK CAGR | BOOK MDD | vs Leo 25% |
|---:|---:|---:|---|
| 60万 | 13.65% | **−32.07%** | **破闸** |
| 100万 | 15.55% | **−32.85%** | **破闸** |

CLI_GAP=`book_smoke_no_arch_ok_path`（wrapper 预核；未改 `1a5fa1aa`）。

## 3. 归档 / QUIET

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_DARK_HORSE_ADD.f08ce32c.CONSUMED_PASS.20261027T2248ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`f08ce32c`** / `f08ce32c5566030e48e941039f09ead5c4a7a4e8828f457ae2f15309cfe63817`（pre=post；内容字节不变；**禁 RESTORED**） |
| live `.ok` | **ABSENT** |
| QUIET | **ABSENT** → 无需 lift；**未新建 QUIET**；未触 `_lifted/` |
| 叶38 | CONSUMED_PASS **`c01c2034` UNTOUCHED**；禁 RESTORED `794f6578`；禁混线 |

## 4. 硬钉

- 本票 fund who_pays Book-Smoke **窗关闭归档**；**仍 ≠Book-Smoke ACCEPT**；**仍 ≠X2 ACCEPT**；本拍**不解阻 ACCEPT**
- 审票 **PASS_WITH_CONDITIONS `694b9a80`**：C1 MDD 破 25%；C2 CLI_GAP NOTE；C3 需降 MDD 再谈；C4 X2 另令 / 禁混叶38
- 禁复跑本票当 ACCEPT；禁抬帽；禁代跑；禁新签；禁改 weights / `1a5fa1aa`
- **禁 RESTORED** 本票内容 **`f08ce32c`**；禁 RESTORED 叶38 `794f6578`+旧票
- **禁混叶38**：旁线 `c01c2034` 维持
- **下一跳交主决策**（HOLD / AI·Eng 另案降 MDD / X2 另令）——**Arch 不自决 ACCEPT、不自派 X2、不自派降 MDD 案**
- **不报 Leo**（leo_notify=false）

## 5. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：HOLD 或令 AI/Eng 另案降 MDD（非本拍 ACCEPT）
      → X2 另令；Arch 不自派；≠Book-Smoke ACCEPT；≠X2 ACCEPT
      → 禁 RESTORED f08ce32c；禁混叶38 c01c2034；禁 QUIET
```

live=false。
