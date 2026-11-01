# OPTIMIZER Core FROZEN_v1.3 程序性复签（Arch，2026-10-18 00:05 ET）

**结论：有条件通过（CONDITIONAL）。放行标记 `core_x2/ARCH_RESIGN_A_v1_3.ok` 本次不创建。** 下文 K1–K5 全部落实、并经主 Agent 确认之后，由 Arch 再创建标记；标记创建之前，v1.3 不得计算收益，也不得运行 book_smoke。

本次是只读审计：没有改代码，没有计算任何收益，live=false，纸面轨没有动。
复算脚本与输出：`docs/v2/audit/arch_core_v1_3_postlot_recheck.py`、`arch_core_v1_3_postlot_recheck_expo.csv`、`arch_core_v1_3_excl_recheck.csv`。

## 1. 已核实通过
- **参数和约束没有改。** λ_risk=117.21317（与 v1.2 的 meta 一致），λ_turn 两档都是 0.6，仍从 calib_*.json 读取。`optimizer_lambda_calib_sealed.py` 中的常量 NAME_CAP 6%/5%、Neff 20–30、行业 ±8%/≤20%、SIZE_BOX 0.35、β 0.10、slack 上限 0.05σ/1pp、ETF 20% 都没有变化。v1.3 的改动全部挂在 `v13` 开关下（`optimizer_core_x2_run.py` 第 205、222–240、244–245、255–256 行）。在没有剔除名单的 43 个档日里，有 41 个的 K 和 Neff 与 v1.2 完全相同；另外 2 个是因为上期持仓不同导致的路径依赖，求解器本身没有变化。
- **剔除名单的规则正确。** 独立复算 3034 条（60万 1992 条，100万 1042 条），漏剔 0 条、多剔 0 条。每条都满足 lot×PIT 收盘价 > 上限×AUM：科创板按 200 股计，其他按 100 股，阈值是 3.6 万和 5 万。可行日的持仓中没有一只一手金额超过上限，单票权重都没有超过 cap×budget。
- **β、Size、MidCap 的 HARD 约束在可行日全部守住。** 独立复算结果与 disclosure 的差异小于 1e-12。380 个可行档日中，|β| 最大 0.0999（限 0.10），|MidCap| 最大 0.400，|Size| 最大 0.400（限 0.35 加 slack 上限 0.05），越界 0 次。持仓数在 20–29 只之间。
- **逐日披露齐全。** disclosure 的字段包括 status、K、tries、slack、size/midcap/β 漂移、行业、现金、持仓数、单边换手、n_excluded 和沿用标记。沿用日的漂移已经写入（carry_drift_disclosed 22/22）。infeasible_days 和 lot_exclusions 也都已落盘。
- **v1.3 没有产生任何收益。** 四个 book_smoke 的 target_weights 与 `_archive_v1_2` 中的 v1.2 权重完全一致（差异为 0），与 v1.3 权重不同（差异最大 6pp）。scorecard 中 A 列仍是 v1.2 的【HARD 违约账本】，A_v1_3 一行全部是 PENDING_ARCH_RESIGN。全仓没有找到 v1.3 的 nav 或回测目录。meta 中记录 returns_computed=false。

## 2. 关键披露数字（X2 / 全窗；行 = 日×档×口径）
- 可行率（OK + LOT_CASH_GT2）：全窗 60万 88.7%、100万 90.6%；X2 两档都是 89.7%（29 个调仓日里 3 天 LOT_HARD_FAIL，原因都是风格超界；没有因整手后不足 20 只而失败的情况，满足 S2-2）。
- 严格可行率（只算 OK）：全窗只有 36–53%。**LOT_CASH_GT2 共 192 行，占 45%；v1.2 只有 1 行。** 现金中位数 2.0–2.4%，p90 4.7–7.0%，最大 17.3%。
- 换手：每个调仓日优化器单边换手的中位数，全窗 0.33–0.35，X2 0.35–0.36（v1.2 为 0.38–0.40，标定目标 0.25）。
- slack 贴上限：60万 27%，100万 47%（X2 分别为 21% 和 38%）。
- 剔除数量：每个调仓日的中位数 60万 14.5 只、100万 7 只，最多 82 只和 50 只（X2 中位数 20 只和 10 只）。
- 沿用日：44 个档日中有 13 个 |β|>0.10（最大 0.244），Size 和 MidCap 各有 4 个超界。另有 8 个持仓实例已经不在当日的 HI_LIQ 池内。

## 3. 问题与条件
| 级别 | 编号 | 内容 | 负责人 |
|---|---|---|---|
| P1 | K1 | **改动范围超出裁定。** 主 Agent 只裁定了 (a)。AMEND ② 还加入了整手后风格感知修复（单手、换仓、卖出）和风格超界判 LOT_HARD_FAIL，等于 (a)+(b)，并把行业基准改为支撑集 wb（wb_raw）。文档写的「主 Agent 与 Arch 批准 v1.3」与裁定记录不符，需要主 Agent 补一次追认，或者明确驳回。 | 主 Agent |
| P1 | K2 | **现金约束。** 条款② 的补手只接受不增加超界量的加仓，结果有 45% 的行现金超过 2%（最大 17.3%），与 FROZEN_v1.1 ①（满仓、现金≤2%）冲突，而且 AMEND 没有事前写明。要么由主 Agent 裁定「风格 HARD 优先于现金≤2%，只披露」，并在记分卡中同时报两种可行率；要么判定违约。 | 主 Agent → Strategy |
| P1 | K3 | **S2-3 尚未冻结。** `STRATEGY_OPTIMIZER_STAGE2_PREREG_DRAFT_ZH.md` 第 3 行仍是 DRAFT，S2-3 写在第 20–22 行（不交易带 0.5%）。没有 Arch/Beta 共签，也没有主 Agent 的冻结记录。目前还没有人看到 v1.3 的收益，所以现在冻结仍然有效；但必须在创建放行标记之前完成。 | Strategy → Beta/Arch → 主 Agent |
| P1 | K4 | **时间戳。** AMEND_v1_3 第 3 行写的是 2026-10-14「≈09:40 ET」，但 09:26 的巡检记录（`output/d1/supervise_patrol_20261014_0926_ET.md` 第 8 行）显示文档 09:24 就已落盘，同一时间运行已经带着 --arch-cosigned 开始了。时间戳没有改，这已经是第二次「先跑后签」。文件 mtime 全部被 10-15 05:18–05:19 的整体恢复覆盖，相关文件也没有 git 提交（仓库最后一次提交是 10-12），先后顺序只能以巡检记录为证。 | Strategy |
| P1 | K5 | **book_smoke 会覆盖 v1.2 的账本。** `core_x2_book_smoke.py` 默认把结果写到 `book_smoke_{sleeve}_{tag}`，而 scorecard 会把这个目录无条件标成 v1.2 违约账本。entry_meta 指向的 core_*.parquet 现在已经是 v1.3 的权重。跑 v1.3 之前，必须先把这四个目录归档到 `_archive_v1_2/`，v1.3 改用单独的目录，scorecard 的 A_v1_3 读取新目录，并且记录权重的 sha256。 | Eng |
| P1 | K6 | **行业基准口径不一致。** 求解器和修复步骤都以支撑集 wb 作为行业基准（这个口径从 v0 就有）。按全池 wb 复核，有 8 个可行档日的行业主动暴露超过 8%+slack（最大 10.2%）。这和 v1.1 风格口径的问题属于同一类，我在 FINAL_COSIGN 时漏掉了。v1.3 只做披露（记分卡标注「行业按支撑集口径」），是否在 Stage2 处理由主 Agent 裁定。 | 主 Agent |
| P2 | — | `WEIGHTS_README.md` 仍然是 v1.2 的内容，需要改成 v1.3。ind_abs 在 disclosure 中按股票仓位归一，在代码中按 NAV 计，两种口径之差会让 21 行被标记（最大 20.9%）。剔除阈值没有区分口径，口径② 实际上限是 0.8×cap×AUM（已事前披露）。HARD_EXCLUDE 去掉了 600519 和 002371，所以它们也不在 wb 里（这是既有口径，需要披露）。沿用日有 8 个持仓实例已经出池，应在 disclosure 中补一列。 | Strategy / Eng |

## 4. 放行标记
- 格式沿用 `ARCH_RESIGN_A_v1_2.ok.retired_v1_3`，内容是一行文本：`Arch cosign: docs/v2/ARCH_OPTIMIZER_CORE_v1_3_PROCEDURAL_COSIGN_ZH.md (...)`。
- 代码实际读取的文件名是 `output/strategy_optimizer/core_x2/ARCH_RESIGN_A_v1_3.ok`（`scripts_eng/core_x2_scorecard.py` 第 25 行）。
- 本次**不创建**。K1–K5 落实后由 Arch 创建；K6 只要求披露，不阻塞放行。

## 更正（2026-10-18 00:06 ET）
- K1 更正：据主 Agent 原文（09:15「①②③ 三条全批」），整手后补手要同时检查风格、β 和行业边界，这本来就在批准范围内。撤回「超出裁定」的说法。
- 行业基准：主 Agent 裁定改回冻结口径，即相对全池的池内基准 wb，相对偏离 ±8%、绝对仓位不超过 20%。现有 v1.3 权重因此作废，要重跑。
- 流程：Strategy 改完代码和 AMEND 后交 Arch 审；审过之后 Arch 写 core_x2/ARCH_RUN_AUTH_v1_3.ok，Strategy 再重跑权重，然后交 Arch 复签，复签通过后建 ARCH_RESIGN_A_v1_3.ok，最后交 Eng。S2-3 冻结仍是建放行标记的前提。

## 补充（2026-10-18 00:07 ET）
- K5 已完成：v1.2 账本已归档，见 _archive_v1_2/MANIFEST.json；book_smoke 改为强制写入新目录。
- 严格可行率改用 Eng 的口径：按资金档算，两个口径都可行才算可行。作废版 v1.3 在 X2 上：60万 17.2%，100万 13.8%；密封窗：60万 47.4%，100万 29.5%。宽口径为 89.7%。之前报的 36–53% 是按行汇总的数字，作废。
- K2 裁定：现金超标只披露、不判失败；记分卡要同时报两种可行率、现金分布和现金拖累。K6 修正后重跑权重，以上数字全部重算。
