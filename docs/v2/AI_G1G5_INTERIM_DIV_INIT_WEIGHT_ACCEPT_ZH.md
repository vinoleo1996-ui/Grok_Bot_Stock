# Alpha 裁定：叶9 g1g5_ashare_interim_div_init_v1（中期分红首次/大幅提升预案）— 研究级 WATCH
日期：2026-10-13 ET。研究级；promotion_approved=false；live=false；handoff=NO；no_gp=true；book_smoke=NOT_DISPATCHED。

## 1. 材料
- 预注册：docs/v2/AI_G1G5_INTERIM_DIV_INIT_WHO_PAYS_PREREG_ZH.md（FROZEN 2026-10-13 20:24:32 ET）
- 回执：docs/v2/AI_G1G5_INTERIM_DIV_INIT_WEIGHT_RECEIPT_ZH.md；复权诊断：docs/v2/AI_ADJ_PRICE_RECEIPT_ZH.md；口径审计：docs/v2/ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md
- 权重：output/ai_factory/g1g5_interim_div_init_daily_weights_20261014_082433.parquet（sha256 7662ffcc…8393）
- Alpha 复核脚本：output/alpha/verify_leaf79_adj_20261013.py → _raw.json（复权口径，research/adj_price.py；基准 510300 close_hfq）

## 2. 价格口径记录（重要）
AI 原自检（毛 CAGR 9.25%、MDD −17.08%、残差 α +0.65%）用的是**未复权**收盘价：持仓期内除息日的跳空被当成亏损，现金股息未计入。本叶按分红预案选股、持有 60 日，常跨除息日，因此**收益被系统性低估**，偏差在各叶中最大。Eng 审计（ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md）确认此前 Alpha 的 verify_*.py 同样用未复权价；烟测引擎已处理除权除息，不受影响。自本裁定起 Alpha 复核一律用 research/adj_price.py。下表为复权口径。

## 3. 硬闸（全过）
| 闸 | 结果 |
|---|---|
| 长表 | 是；119572 行 / 668 日 / 179 名；无重复、无 NaN、缺交易日 0 |
| Σw≡1、无负权、无 stub | 1.0–1.0；最小权 0 |
| 单名 ≤4% | max 4.00% |
| 600519/002371 | 恒 0 |
| 510300 压舱 | 均 64.4%（20%–100%）；**全压舱 123 天**（事件集中在 8–9 月中报季） |
| 逐日 Jaccard vs 30 个前包 | max 0.206（vs moneyflow_resid）<0.7 |
| PIT | 296 次入场，距最近「预案」ann_date 最少 2 个交易日（盘后公告→T2），无前视 |
| 预注册早于权重 | 预注册 mtime 20:24:32 ET，权重 20:26 ET；冻结前只做计数 |
| 同数据前置收益研究 | 同表 dividend_tushare 已有 V33 STOCK-DIV-IMP（实施公告短窗，已 reject）收益研究；H3_dividend_calendar 只登记未跑。事件定义不同，但同源数据已被看过收益 → **按弱样本外处理** |
| G6 / peak RSS | pass / 515MB |

## 4. 复权口径复核（2024-01-03→2026-10-09，毛、无成本）
| | 毛 CAGR | MDD | Sharpe | β | 残差 α | 2024 / 2025 / 2026 α |
|---|---|---|---|---|---|---|
| 叶9（复权） | 12.91% | −14.94% | 0.777 | 0.90 | +1.60% | +2.46% / +2.20% / +1.15% |
| 叶9（未复权，AI 原自检） | 9.25% | −17.08% | — | 0.90 | +0.65% | +0.19 / +0.31 / +2.78 |
| 510300（hfq） | 12.34% | −16.25% | 0.710 | — | — | — |
| capacity_adv（复权） | 17.66% | −13.18% | 1.141 | 0.70 | +8.02% | — |

复权后残差 α +1.0pp 且三年都为正，是本叶唯一的正面变化。

去 β 残差相关：capacity_adv 0.088｜earnings_event 0.057｜insider_increase 0.172｜equity_incentive 0.072｜unlock_rebound 0.067｜block_trade 0.171。ρ_excess vs capacity_adv 0.292。

本地毛组合诊断：
| | CAGR | MDD | Sharpe |
|---|---|---|---|
| capacity_adv 单跑 | 17.66% | −13.18% | 1.141 |
| 70/30 | 16.32% | −13.69% | 1.056 |
| 80/20 | 16.77% | −13.52% | 1.088 |
两种配比都劣于主干单跑。

## 5. 门槛
- 现行门（仍有效）：单叶 CAGR∈[12%,18%] 且 MDD≥−28%，60万∧100万。复权毛 CAGR 12.91% 名义在区间内，但只比 510300（12.34%）高 0.6pp，残差 α +1.6%，过门主要靠 β。
- 组合层面门：**待 Leo 在 Alpha 聊天确认**。即使按该门，本地组合诊断劣于主干，**不值得派组合烟测**。

## 6. 裁定
**WATCH**（硬闸过；复权后 α 转为三年皆正但仅 +1.6%；全压舱 123 天；同源弱样本外；组合无增益）。不派 Book-Smoke；不晋级；不实盘；禁 GP。若要以复权口径正式重评，须重新预注册。

## 7. 缺口
1. 原自检未复权，已在本文记录；AI 台账 AI_LEAF_LEDGER_ZH.md 第 9 行应补复权数字。
2. 全压舱 123 天，季节性集中。
3. 弱样本外（同表 V33 收益研究在先）。
