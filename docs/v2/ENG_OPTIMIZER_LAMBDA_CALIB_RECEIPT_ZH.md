# Eng 回执：OPTIMIZER_V1 密封窗 λ 标定（Leo Core-concentrate）

- **时间**：2026-10-14 20:28 CST（约）
- **hard_spec**：`leo_core_concentrated_0809`
- **状态**：密封窗标定产物已落盘；**live=false**；**未**改纸面 FROZEN；**未**用 X2 收益选 λ
- **脚本**：`research/optimizer_lambda_calib_sealed.py`
- **产物**：`output/strategy_optimizer/calib/`

## 1. 选用 λ

| 参数 | 值 | 说明 |
|---|---|---|
| λ_risk | **117.213** | 探针解（λ_risk=1, λ_turn=0）隐含比中位数；Σ 已×244 年化 |
| λ_turn 60万 | **0.6** | 命中 ±20% 带：achieved=0.2844 vs target=0.25 |
| λ_turn 100万 | **0.6** | 命中 ±20% 带：achieved=0.2876 vs target=0.25 |

> 注：turn JSON 字段名仍含历史 `target_b4_median_one_way`，实际主目标见 `turn_target_src`。

## 2. turn_target_src（Leo ≈08:20）

| AUM | turn_target_src | 目标单边中位数 |
|---|---|---|
| 60万 | `monthly_two_way_50pct_fallback` | 0.25（月双边≈50%） |
| 100万 | `monthly_two_way_50pct_fallback` | 0.25 |

- **主目标**：同窗同 AUM **capacity_adv** 引擎换手中位数 ±20%。
- **事实**：纸面/现成 capacity_adv 权重密封窗仅 2024-01→2024-05（n_obs=5），**样本不足** → 回退 `monthly_two_way_50pct_fallback`。
- **B4**：仅对照（contrast_only）；未做吃内存的 B4 全窗重建（Arch/主 Agent：控 RSS≤1.5GB）。

## 3. 样本与可行性（Arch N2）

| 项 | 值 |
|---|---|
| 密封窗 | 2018-01-02→2024-05-31 |
| cadence | `month_end_plus_first_last`（禁周频） |
| 再平衡日 | **24**（≥20） |
| INFEASIBLE 率 60万 | 0.0（ok=24） |
| INFEASIBLE 率 100万 | 0.0（ok=24） |
| 掩码 sha | `c5433e80a74ac3ac…`（期望 c5433e80…） |
| 年化 | 244 |
| 求解器 | OSQP / CLARABEL |
| 峰值 RSS（标定进程） | ~1222.953125 MB |
| book-smoke 内存探针 | 见 calib_meta.memory_probe |

## 4. NEW HARD（浓缩 Core）

- 单票：100万 **5%** / 60万 **6%**；Neff **20–30**；两步截断（支撑≥**2.0%**）+ 科创整手 **200**
- 行业 vs wb **±8%** / 绝对≤**20%**；行业 Slack≤**1pp**
- Size/MidCap **±0.35σ**；Slack≤**0.05σ**
- β \|β−1\|≤**0.10** vs wb；仅 L1；ν=0
- wb = HI_LIQ 池内流通市值加权

## 5. 双报告袖 + 三列对照（不选 λ）

**报告袖** `report_sleeves`：

1. `equity_100` — 纯股票
2. `equity80_etf20_510300` — 80% 权益 + 20% 510300（**主对标袖** `primary_benchmark_sleeve`）

**三列 Core 对照** `core_run_compare_columns`（Leo via 主 Agent；**不**用于选 λ；Eng **不**开 X2 终判）：

1. OPTIMIZER Core on HI_LIQ
2. 现行 capacity_adv mid_large + 静态锚（纸面 FROZEN 路径，未改）
3. capacity_adv Top-25 在 HI_LIQ_V1.1 同池重跑（去 static-anchor=2024-06-28 幸存者偏差）

密封窗烟测样本已写出 Sharpe/MDD（见 calib_meta.sleeve_metrics_sealed_smoke）；**明确未用于选 λ**。IR 在烟测路径对 510300 缺列时可能为 null，正式对标须走记分卡/书烟。

## 6. λ_risk 敏感性（±50%，不看收益）

见 `calib_lambda_risk.json` → `sensitivity_pm50pct`。

## 7. 阻塞 / 后续

- capacity_adv 密封窗引擎换手全样本仍缺（权重多自 2024-01 起）→ 已按 Leo 允许回退并打标。
- **Arch N3（P2，已排队未做）**：`quantlab/report/metrics.py` 与 `research/leaf_selfcheck_v3.py:107` 遗留 ×252 → 迁到 `quantlab.metrics`（244）。
- 请 Strategy 写入 DRAFT 修订 + 催 Beta/Arch 按 Core-concentrate + 08:20 频率/换手终签后报 Leo 申请 **FROZEN**。
- Eng **未**跑 X2 优化器正式臂；纸面 FROZEN 未动。

## 8. 文件清单

- `output/strategy_optimizer/calib/calib_lambda_risk.json`
- `output/strategy_optimizer/calib/calib_lambda_turn_60w.json`
- `output/strategy_optimizer/calib/calib_lambda_turn_100w.json`
- `output/strategy_optimizer/calib/calib_meta.json`
- `docs/v2/ENG_OPTIMIZER_LAMBDA_CALIB_RECEIPT_ZH.md`（本文件）

## 更正（2026-10-14 · Arch P1-T3 / P2-T6）
- **原回执 “INFEASIBLE=0/24” 为虚报**：v0 `two_step_polish` 在 step-2 失败时 `return r1`（回退 step-1 大篮子）仍记 OK，且未检查最终持仓数。原 calib_meta.json 保留，已加 `ARCH_P1_T3_CORRECTION: MISREPORTED` 标记。
- **v1.1 逻辑**（research/optimizer_lambda_calib_sealed.py）：step-2 失败或最终持仓数∉[20,30] → INFEASIBLE，沿用上期权重。λ 未改（λ_risk=117.213，λ_turn=0.6/0.6），仅密封窗，未用 X2 收益。
- **真实可行率**（24 个密封调仓日，output/strategy_optimizer/calib/calib_meta_v1_1.json）：60万 15/24=62.5%（<20 只 8 日、>30 只 1 日即 step-2 失败回退 81 只）；100万 8/24=33.3%（<20 只 12 日、>30 只 4 日为 step-2 失败回退 80–96 只）。越界多为 18–19 只，贴近下限。
- **λ_turn 换手**（沿用上期口径，单边中位，目标 0.25，带 [0.20,0.30]）：60万 0.272 达标；100万 0.000 **不达标**（多数日沿用上期，属退化）。100万档 Core 规格在现 HARD 下不可行，需 Strategy/主 Agent 裁定（如放宽下限或 MIN_KEEP_W），Eng 不自行改。
- **T6**：记分卡 B/C equity_100 已改为原生纯股票 book（去 510300 后归一，同引擎 strategy_v1，仅 X2；单票上限放大 1/0.8）；由 80/20 净值反推的行保留为 `*_derived_ref`，标注“近似，仅参考”。

> 注（08:48 ET，Strategy 裁定）：calib_meta_v1_1.json 为**旧求解器口径诊断**，不代表 v1.1（optimizer_core_v1_1.py：Σw=1、确定性 top-k、禁回退）。INFEASIBLE 正式重报以 Strategy v1.1 逐日清单为准。

## C5 INFEASIBLE 重报（v1.1，08:55 ET）
来源：core_x2/core_v1_1_infeasible_days.csv（Strategy v1.1 输出）；调仓日：密封 77 天，X2 29 天；两种口径逐日一致。
- 60万：密封 0/77 不可行（2018-01-02 首日无数据，沿用）；X2 7/29 不可行（可行率 75.9%），其中 step2 失败 2 天（2025-01-27、2026-06-30），LOT_HARD_FAIL 5 天（2026-03-31、04-30、05-29、07-31、08-31）。
- 100万：密封 1/77（2024-01-31，step2）；X2 1/29（2024-06-28，step2）。
- 没有任何单月 ≥2 天不可行，未触发升级线。
- ⚠️ 风险：60万档 2026-03 到 2026-08 连续 6 个调仓月都不可行（5 天是整手约束失败），持仓基本冻结在 2026-02 的组合。这不是单月 ≥2，但等于半年没调仓，需要 Arch/Strategy 关注。

## C5 重报 v1.2（Eng · 2026-10-14）

来源：`output/strategy_optimizer/core_x2/core_v1_2_disclosure.csv` / `core_v1_2_infeasible_days.csv`（Strategy v1.2 全量；λ 冻结 risk=117.213、turn=0.6；未调参、未改 HARD）。按 AUM 档判定可行性：任一口径失败则该档两口径都沿用上期，所以每档只计一次。`calib_meta_v1_1.json` 仅作旧求解器口径诊断。

| 窗 | AUM | 调仓日 | OK | step2 | LOT_HARD_FAIL | other | 可行率 | 单月≥2天 | 连续不可行月 |
|---|---|---|---|---|---|---|---|---|---|
| SEALED | 60万 | 78 | 76 | 1（2019-12-31） | 0 | 1（2018-01-02 NO_DATA 首日） | 97.4% | 无 | 无 |
| SEALED | 100万 | 78 | 76 | 1（2019-10-31） | 0 | 1（同上） | 97.4% | 无 | 无 |
| X2 | 60万 | 29 | 25 | 1（2026-07-31） | 3（2026-04-30/06-30/09-30） | 0 | 86.2% | 无 | 2026-06→07 |
| X2 | 100万 | 29 | 29 | 0 | 0 | 0 | 100% | 无 | 无 |

- 触发口径：3 个 LOT_HARD_FAIL 都由口径② equity80_etf20_510300 触发（整手后只剩 19 只；同日口径① 20 只、OK）。step2 失败发生在分口径之前，两口径同时失败。
- 整手后 <20 只的月份：仅 60万 口径② 的 2026-04、06、09（这些日已按 INFEASIBLE 沿用上期，落盘权重中各档各口径最少 20 只）。
- 另有 1 天 LOT_CASH_GT2：100万 equity_100 2025-06-30，现金 2.93%，只披露、不算不可行。
- 结论：60万 档有小资金整手的结构性限制，按 Arch 裁定只披露、不调参。A 列等 Arch 复签，book_smoke 暂停。

### calib v1.2 重评（24 个密封窗日，λ 冻结，`calib/calib_meta_v1_2.json`）
| AUM | 可行 | 行业 slack 用到的天数（最大） | Size slack 用到的天数（最大） | 整手后 |β drift| 最大 | K | 单边换手中位数 vs 目标 |
|---|---|---|---|---|---|---|
| 60万 | 24/24 = 100% | 14 天（1.0pp 顶格） | 14 天（0.05σ 顶格） | 0.107（框 0.10） | 21–25 | 0.400 vs 0.25（超） |
| 100万 | 23/24 = 95.8%（1 天 step2） | 21 天（1.0pp） | 21 天（0.05σ） | 0.141 | 21–27 | 0.379 vs 0.25（超） |

注：换手高于目标，按规则只披露、不调 λ。book_smoke X2 已在 Arch 复签后跑完，三列结果见 core_x2/scorecard_three_col.md。
