# Alpha 裁定：叶7 g1g5_ashare_block_trade_v1（大宗交易机构承接）— 研究级 WATCH
日期：2026-10-13 ET。研究级；promotion_approved=false；live=false；handoff=NO；no_gp=true；book_smoke=NOT_DISPATCHED。

## 1. 材料
- 预注册：docs/v2/AI_G1G5_BLOCK_TRADE_WHO_PAYS_PREREG_ZH.md（标 FROZEN 18:58 ET；持有期冻结前由 20 改 40 日，理由为事件计数稀少）
- 回执：docs/v2/AI_G1G5_BLOCK_TRADE_WEIGHT_RECEIPT_ZH.md；复权诊断：docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md；口径审计：docs/v2/ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md
- 权重：output/ai_factory/g1g5_block_trade_daily_weights_20261014_065149.parquet（sha256 02f666f4…bf60）
- Alpha 复核脚本：output/alpha/verify_leaf79_adj_20261013.py → output/alpha/verify_leaf79_adj_20261013_raw.json（**复权口径**：个股 X2 close × adj_factor，用 research/adj_price.py；基准 510300 close_hfq）

## 2. 硬闸（全过）
| 闸 | 结果 |
|---|---|
| 长表 date,instrument,target_weight | 是；36740 行 / 668 日 / 55 名；无重复、无 NaN、缺交易日 0 |
| Σw≡1、无负权、无 stub | 1.0–1.0；最小权 0 |
| 单名 ≤4% | max 4.00% |
| 600519/002371 | 恒 0 |
| 510300 压舱 | 均 79.6%（48%–96%），超 60% 软线（记缺口） |
| 逐日 Jaccard vs 30 个前包 | max 0.333（vs earnings_event）<0.7 |
| PIT（T2 严格晚于 available_at） | 81 次入场：71 次距最近大宗日 2 个交易日（D→available D+1 09:00→T2=D+2），4 次 3 日；6 次为 2024-01-02 窗口起点承接 2023Q4 事件；无早于 T2 的入场 |
| 预注册早于权重 | 文件时间：预注册 mtime 18:51:48 ET，权重 18:53 ET（同一命令紧接）。**缺口**：预注册标注的 18:58 ET 晚于权重落盘，回执又写「约 19:00 运行」，时间戳文字不一致，按 mtime 认定顺序成立 |
| 同数据前置收益研究 | 盘上未见 block_trade 表的收益研究（V26/V34 仅标「无稳 PIT 表」）；不降级为弱样本外，但样本只有 149 条事件 |
| G6 / peak RSS | pass / 646MB |

另：research/g1g5_block_trade_weights.py 文件头仍是 earnings_event 模板文字（与 buyback_cancel 同类问题），请 AI 修正。

## 3. 复权口径复核（2024-01-03→2026-10-09，毛、无成本，Alpha 独立重算，与 AI 复权诊断一致）
| | 毛 CAGR | MDD | Sharpe | β | 残差 α | 2024 / 2025 / 2026 α |
|---|---|---|---|---|---|---|
| 叶7 block_trade | 13.12% | −17.54% | 0.747 | 0.98 | +0.92% | +4.66% / −0.14% / −1.63% |
| 510300（hfq） | 12.34% | −16.25% | 0.710 | — | — | — |
| capacity_adv（复权） | 17.66% | −13.18% | 1.141 | 0.70 | +8.02% | +13.50 / +1.54 / +2.83 |

未复权口径（AI 原自检）10.12%/−17.63%/α +0.80%，复权后残差 α 仅 +0.1pp，结论不变。

去 β 残差相关：capacity_adv 0.063｜earnings_event 0.060｜insider_increase 0.067｜equity_incentive 0.134｜unlock_rebound −0.002｜interim_div_init 0.171。ρ_excess vs capacity_adv 0.106。

本地毛组合诊断（日再平衡、无成本）：
| | CAGR | MDD | Sharpe |
|---|---|---|---|
| capacity_adv 单跑 | 17.66% | −13.18% | 1.141 |
| 70/30 | 16.39% | −14.49% | 1.038 |
| 80/20 | 16.83% | −14.05% | 1.076 |
两种配比 CAGR、MDD、Sharpe 都劣于主干单跑。

## 4. 门槛
- 现行门（仍有效）：单叶 Book-Smoke CAGR∈[12%,18%] 且 MDD≥−28%，60万∧100万 两档。本叶复权毛 CAGR 13.12% 名义上落在区间内，但 510300 本身复权 12.34%，本叶超出基准不到 1pp、β≈1，残差 α 接近 0 且 2025、2026 两年为负，过门主要靠 β，不是 α 证据。
- 组合层面门（主干+卫星两档 CAGR、MDD 都优于 capacity_adv 单跑）：**待 Leo 在 Alpha 聊天确认**。即使按该门，本叶本地组合诊断两档配比都劣于主干，**不值得派组合烟测**。

## 5. 裁定
**WATCH**（研究级硬闸过；α≈0、逐年衰减、压舱 80%；单叶与组合都无派烟价值）。不派 Book-Smoke；不晋级；不实盘；禁 GP。

## 6. 缺口
1. 预注册冻结时间戳文字（18:58）与权重落盘（18:53）、回执「~19:00」不一致，请 AI 更正为真实时间。
2. 压舱 79.6%，超 60% 软线。
3. 2026 年仅 14 条事件，样本过薄。
4. 脚本文件头模板文字未改。
