# STRATEGY FULLA X2 回执（capacity_adv 单腿）

**时间**：2026-10-14 07:41 ET  
**窗口**：X2 2024-06-03→2026-10-09（**样本内**）  
**引擎**：`quantlab.cli book-smoke --run-nav` / `ExecConfig.strategy_v1` / core=0 stock=1  
**live / promotion**：false（未动 FROZEN_CONFIG / 纸面轨）  
**预注册**：`docs/v2/STRATEGY_FULLA_UNIVERSE_PREREG_ZH.md`  
**权重**：`output/strategy_fulla/legs/g1g5_capacity_adv_fulla_v1_daily_weights_20261014_192953.parquet`（正权精简：`..._pos_weights.parquet`）

## 1. 主表：FULLA vs top300（同引擎）

基线取自 `output/v3/book_smoke_g1g5_capacity_adv_x2`（run `book_smoke_20261013_111418`），与本次 FULLA 同为 Eng book-smoke apples-to-apples。**不以** Alpha leaf_selfcheck 诊断窗（2024-01-04→2026-10-09）作终判对照。

| AUM | 宇宙 | CAGR | MDD | Calmar | 日胜率 | 月胜率 | 填单率 | 成本/初资 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 60万 | **FULLA_V1** | **−2.83%** | **−27.86%** | −0.10 | 48.5% | 46.4% | 62.9% | 2.63% |
| 60万 | top300 基线 | 13.82% | −10.07% | 1.37 | — | — | — | — |
| 100万 | **FULLA_V1** | **−1.41%** | **−31.16%** | −0.05 | 48.3% | 50.0% | 67.5% | 2.83% |
| 100万 | top300 基线 | 12.23% | −11.62% | 1.05 | — | — | — | — |

### 风险旗标（对 Leo MDD≤25%）

- **两档 FULLA 单腿 MDD 均破 25%**（60万 −27.86%，100万 −31.16%）。
- FULLA 相对 top300：**CAGR 全面恶化、MDD 大幅恶化、填单率仅 63–68%**（lot/ADV 约束下大量目标未成交）。
- Alpha 诊断（不同引擎/窗）曾报 60万 15.65%/−27.13%、100万 8.09%/−36.00%——MDD 方向一致，但 book-smoke 成本+按手取整后 CAGR 转负；**以本表为准**。

## 2. 分年年化 & NAV

![分年年化](../output/strategy_fulla/capadv_fulla_vs_top300_yearly.png)

![NAV](../output/strategy_fulla/capadv_fulla_vs_top300_nav.png)

![表图](../output/strategy_fulla/capadv_fulla_vs_top300_table.png)

分年数字见 `output/strategy_fulla/capadv_x2_summary.json` → `yearly_cagr`。

## 3. 小盘归因（仅披露）

定义：PIT `total_mv` 沪深 A 截面**后 30%**（与预注册一致；非剔除条件）。

| 指标 | 值 |
|---|---|
| 持仓中真小盘（后30%）权重×时间均值 | **0.0** |
| 有小盘持仓的交易日占比 | **0.0%** |
| 小盘对收益贡献 | **≈0**（无持仓） |
| 低于全 A 市值中位数的权重均值 | 0.59%（补充） |
| 旧 top300 外权重（全书 / 股票袖） | 31.3% / 39.1%（来自 Alpha check.json） |

**解读**：capacity_adv 按 ADV 流动性排序，几乎不买全 A 市值后 30% 真小盘；约 31% 权重在旧 mid_large top300 外，属中盘/较小大盘，**不能**等同小盘贡献。

## 4. 申万一级行业分布（持仓权重×时间，股票袖）

![行业](../output/strategy_fulla/capadv_fulla_industry_sw_l1.png)

Top：电子 15.3%、汽车 10.3%、机械设备 10.0%、电力设备 8.7%、通信 8.5%、计算机 7.5%、医药生物 6.2%、家用电器 6.1%。全表：`output/strategy_fulla/capadv_x2_industry_share.csv`。

## 5. B4 合成状态

**SKIPPED**。阻塞：AI FULLA 事件腿未落盘。

- `output/strategy_fulla/legs/` 目前**仅有** capacity_adv。
- AI 批处理 `earnings_event / insider_increase / equity_incentive / …` 日志显示 **Terminated exit 143**；叶11/叶14 亦无。
- 待 AI 交付 earnings_event、insider_increase（及 B4 所需第三腿/叶）后，再按 50/25/25 + per-leg topN（60万 N=6，100万 N=10，单名≤6%）合成并跑同窗 X2。

## 6. 产物路径

| 类型 | 路径 |
|---|---|
| book-smoke 输出 | `output/strategy_fulla/capadv_x2/` |
| summary JSON | `output/strategy_fulla/capadv_x2_summary.json` |
| 小盘归因 | `output/strategy_fulla/capadv_x2_smallcap_attr.json` |
| 行业 CSV | `output/strategy_fulla/capadv_x2_industry_share.csv` |
| 图表 PNG | `output/strategy_fulla/capadv_fulla_vs_top300_{yearly,nav,table}.png`、`capadv_fulla_industry_sw_l1.png` |
| 本回执 | `docs/v2/STRATEGY_FULLA_X2_ZH.md` |

## 7. 下一步（研究，非晋级）

1. 等 AI 重跑 FULLA 事件腿 → Strategy 合成 B4 X2。  
2. 主 Agent / Leo：FULLA 单腿两档破 MDD25% + 填单差，是否继续全 A 主报、或改 ADV/名称数/参与率后再试（**须 Leo 级拍板**；本 agent 不改门）。  
3. live/promotion 保持 false。
