> 【VOID 2026-10-18 Alpha】文中引用的旧 Alpha HI_LIQ capacity_adv 诊断「60万 18.17%/−24.92%、100万 4.52%/−34.82%」已作废，用现有产物无法复现；请以 book-smoke（−0.6%/−29.9%、1.7%/−33.0%）为准，对账见 docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md §7。

# STRATEGY HI_LIQ_V1.1 X2 回执（capacity_adv 单腿 + B4）

> **⚠ 更正注（2026-10-18 00:17 ET，主 Agent 裁定；置顶，原文保留不删）**
> - 本文 B4 数（60万 22.44%/−16.51%，100万 14.90%/−20.19%）使用隔离旧腿 `_rejected_ind_cap`（earnings_event 195336、insider_increase 195433），**作废**。
> - N1 腿（capadv 195620、earnings_event 202822、insider_increase 202928）正确数，X2 样本内扣费：**60万 21.43%/−19.74%，100万 13.77%/−23.28%**。
> - capacity_adv 单腿数不变（−0.58%/−29.93%、1.71%/−32.99%），两套为同一腿。
> - 对照 capadv+510300 50/50：60万 13.61%/−17.18%，100万 9.95%/−20.06%。结论：B4 相对 capadv-only 的领先**主要来自构建方式**（截断+大比例 510300），而非事件腿。
> - 详见 `docs/v2/STRATEGY_B4_HILIQ_LEG_REVIEW_ZH.md`。权重选项 A–D 为 Leo 级决定，拍板前诊断版保持 50/25/25 仅更正数字；纸面 top300 轨未动；live=false。


> **措辞澄清（2026-10-18 00:58 ET，应 Alpha 核对）**：本回执所称「过渡 Top-N」指**选股方式**（按分数截取，非优化器），不指持仓只数。capadv-only 的 BOOK target_weights 在 60万/100万 两档均为 **25 名全腿**（√ADV 加权、单名≤4%），不是 Top-6/10；「Top 6/10」只适用于 B4 组合器从各腿取名。主 Agent 10-18 00:54 裁定该 book-smoke（−0.6%/−29.9%、1.7%/−33.0%）为 HI_LIQ 叶 CMC/GATE_V3 基准。

> **横幅（必读）**：本回执为 **过渡 Top-N** 研究对照。**主路径 = OPTIMIZER_V1 DRAFT**（`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`，等 Leo 确认后冻结）。**未动** FROZEN_CONFIG / 纸面轨；`live=false`；`strategy_promotion=false`。产物仅在 `output/strategy_hiliq/`。

**时间**：2026-10-14 ~08:06 ET  
**窗口**：X2 2024-06-03→2026-10-09（**样本内**）  
**密封窗**：2018-01-02→2024-05-31 → **N/A**（腿权重仅自 2024-01-02；Eng book-smoke 拒绝密封窗；部分重叠 2024-01-02→2024-05-31 **不作密封声明**）  
**引擎**：`quantlab.cli book-smoke --run-nav` / `ExecConfig.strategy_v1` / core=0 stock=1 / 按手取整 / 年化 244  
**预注册**：`docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_ZH.md` + v1.1 修订  
**脚本**：`research/strategy_hiliq_capadv_b4_x2.py`

## 1. capacity_adv 单腿：HI_LIQ vs top300（同引擎）

| AUM | 宇宙 | CAGR | MDD | Calmar | 日胜率 | 月胜率 | 填单率 | 成本/初资 | vs MDD≤25% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 60万 | **HI_LIQ_V1.1** | **−0.58%** | **−29.93%** | −0.02 | 49.7% | 53.6% | 54.7% | 2.54% | **破** |
| 60万 | top300 基线 | 13.82% | −10.07% | 1.37 | — | — | — | — | 未破 |
| 100万 | **HI_LIQ_V1.1** | **1.71%** | **−32.99%** | 0.05 | 50.1% | 50.0% | 61.4% | 2.89% | **破** |
| 100万 | top300 基线 | 12.23% | −11.62% | 1.05 | — | — | — | — | 未破 |

### 风险旗标

- **两档 HI_LIQ capacity_adv 单腿 MDD 均破 25%**（60万 −29.93%，100万 −32.99%）。
- 相对 top300：CAGR 全面恶化、MDD 大幅恶化、填单仅 55–61%。
- Alpha 诊断（不同窗/引擎）曾报 60万 18.17%/−24.92%、100万 4.52%/−34.82%——**100万 MDD 方向与引擎一致（破门）**；book-smoke 成本+按手后 CAGR 更差；**以本表为准**。
- 相对 FULLA 单腿（−2.83%/−27.86% · −1.41%/−31.16%）：HI_LIQ 略好但仍破门，**不能**挂裸腿进纸面。

## 2. B4 合成（过渡 Top-N + 组合层 IND≤25%）

**合成**：capacity_adv / earnings_event / insider_increase **50/25/25**；per-leg topN（60万 N=6，100万 N=10）；组合单名 ≤6%→510300；**组合层迭代压仓**申万一股票袖 ≤25%（AI 提示腿内 PIT 重分类可能到 0.28，合成时重施）。

| 臂 | AUM | CAGR | MDD | Calmar | 日胜率 | 月胜率 | 填单率 | 成本/初资 | vs MDD≤25% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **B4 HI_LIQ** | 60万 | **22.44%** | **−16.51%** | 1.36 | 51.7% | — | 73.8% | 6.59% | 未破 |
| **B4 HI_LIQ** | 100万 | **14.90%** | **−20.19%** | 0.74 | 51.1% | — | 74.8% | 5.72% | 未破 |
| B4 top300 conc_v2 | 60万 | 15.11% | −13.85% | — | — | — | — | ~2.5% | 未破 |
| B4 top300 conc_v2 | 100万 | 14.24% | −13.17% | — | — | — | — | ~2.2% | 未破 |
| B4 FULLA（研究） | 60万 | 16.80% | −19.95% | 0.84 | 50.3% | 53.6% | 76.0% | 6.92% | 未破 |
| B4 FULLA（研究） | 100万 | 13.78% | −22.21% | 0.62 | 49.6% | 53.6% | 77.0% | 6.35% | 未破 |

### 解读（过渡对照，非晋级）

- B4 HI_LIQ **两档 MDD 未破 25%**，事件腿 50% 预算显著缓冲了 HI_LIQ 单腿大回撤。
- 相对 B4 top300：60万 CAGR 更高（+7.3pp）但成本更高（~6.6% vs ~2.5%）、MDD 更深（−2.7pp）；100万 CAGR 略高（+0.7pp）、MDD 更深（−7.0pp）。
- **合成后 max 行业袖占比**：60万 0.2505 / 100万 0.2500（迭代 pro-rata→压舱；浮点贴边）。
- **样本内**结果；密封窗 N/A；**不替换**纸面 B4；主路径仍优化器 DRAFT。

![CAGR/MDD](../../output/strategy_hiliq/hiliq_cagr_mdd.png)

![表](../../output/strategy_hiliq/hiliq_table.png)

## 3. 分年 & NAV

| 臂 | AUM | 2024 | 2025 | 2026（至10-09） |
|---|---|---:|---:|---:|
| capadv HI_LIQ | 60万 | −8.81% | 23.87% | −18.53% |
| capadv HI_LIQ | 100万 | −7.07% | 30.93% | −19.61% |
| B4 HI_LIQ | 60万 | 8.66% | 38.91% | 14.68% |
| B4 HI_LIQ | 100万 | 0.38% | 33.05% | 6.39% |

![分年](../../output/strategy_hiliq/hiliq_yearly.png)

![NAV](../../output/strategy_hiliq/hiliq_nav.png)

## 4. 密封窗

**N/A**。腿覆盖 2024-01-02→2026-10-09；密封窗无完整权重；不发明权重；book-smoke 模块拒绝密封窗。

## 5. 小盘归因（仅披露）

定义：PIT `total_mv` 沪深 A 截面**后 30%**（非剔除条件；Leo 07:24 小盘可买）。

| 指标 | capadv | B4 60万 | B4 100万 |
|---|---:|---:|---:|
| 真小盘权重×时间均值 | **0.0** | **0.012%** | **0.011%** |
| 有小盘持仓的交易日占比 | 0% | ~低个位数 | ~低个位数 |
| 低于市值中位数权重均值 | 见 JSON | 见 JSON | 见 JSON |

**解读**：ADV≥1 亿子集 + capacity 排序下几乎不持有真小盘；收益来自中大盘流动性票。旧 top300 外占 capacity_adv 全书 ~28.8%（Alpha check）。

## 6. 申万一级行业（股票袖，权重×时间）+ 焦点四业

![行业 capadv](../../output/strategy_hiliq/hiliq_industry_capadv.png)

![行业 B4 60万](../../output/strategy_hiliq/hiliq_industry_B4_60w.png)

### 焦点行业单列

| 臂 | 电子 | 计算机 | 通信 | 医药生物 |
|---|---:|---:|---:|---:|
| capadv HI_LIQ | **12.8%** | **10.0%** | **11.2%** | **4.9%** |
| B4 HI_LIQ 60万 | **14.5%** | **6.9%** | **12.6%** | **3.6%** |
| B4 HI_LIQ 100万 | **15.4%** | **7.5%** | **11.7%** | **4.3%** |

Top（capadv）：电子、通信、计算机、电力设备、汽车、机械、医药、非银。  
全表：`output/strategy_hiliq/capadv_x2_industry_share.csv`、`output/strategy_hiliq/b4/b4_{60,100}w_industry_share.csv`。

## 7. 产物路径

| 类型 | 路径 |
|---|---|
| capacity_adv 正权 | `output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_pos_weights.parquet` |
| book-smoke capadv | `output/strategy_hiliq/capadv_x2/` |
| B4 权重 | `output/strategy_hiliq/b4/B4_50_25_25_topN_{60,100}w.parquet` |
| book-smoke B4 | `output/strategy_hiliq/b4/smoke_B4_{60,100}w/` |
| summary JSON | `output/strategy_hiliq/capadv_x2_summary.json` |
| 图表 PNG | `output/strategy_hiliq/hiliq_{cagr_mdd,yearly,nav,table,industry_*}.png` |
| 本回执 | `docs/v2/STRATEGY_HILIQ_CAPADV_X2_ZH.md` |

## 8. 红线 / 下一步

1. **过渡 Top-N 对照完成**；**主路径仍 OPTIMIZER_V1 DRAFT**（等 Leo + Beta/Arch 共签）。  
2. HI_LIQ capacity_adv **裸腿两档破 MDD25%** → 勿切纸面到裸 HI_LIQ 单腿。  
3. B4 HI_LIQ 数字好看但是**样本内 Top-N**，按 Leo 07:56 **禁止**作为纸面/研究主路径；仅作优化器落地前的影子对照。  
4. live=false；promotion=false；**未动** FROZEN 纸面轨（top300 capacity_adv + B4）。  
5. 密封窗待腿覆盖延长后再报（当前 N/A）。
