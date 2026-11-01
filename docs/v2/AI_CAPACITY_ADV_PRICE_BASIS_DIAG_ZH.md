# capacity_adv 价格口径只读诊断（2026-10-13 ~21:05 ET，研究级，未写权重、未重跑回测）
对象：output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet；生成脚本 research/g1g5_capacity_adv_weights.py（MECHANISM_TAG g1g5_ashare_capacity_adv_v1）。窗口：评估窗 2024-01-02→2026-10-09 的 34 个月末调仓日；未碰 2018→2024-05 封存段。诊断脚本 research/capacity_adv_price_basis_diag.py；明细 output/ai_factory/capacity_adv_price_basis_diag_pairs.csv、汇总 capacity_adv_price_basis_diag.json；peak RSS 1002MB。

## 1. 信号用了什么价格派生量
- 唯一主信号：ADV = float_mktcap × turnover_rate / 100（data/v2/valuation/daily_basic_full_tushare.parquet，取 available_at ≤ 调仓日的最新一行），行业内去均值后取 log 排序；单名上限 min(4%, 2%×ADV/100万)。
- **不使用**动量、波动率、收益率、价格水平或 X2 拼接 close 矩阵（脚本 meta 标 no_close_matrix=True、no_momentum_main_axis=True）；510300 价格只用来取交易日历。
- 池子 select_mid_large_topn_light 按 float_mktcap_basis（2024-06-28 锚定快照）取前 50，同样不是价格派生的时序量。
- 判断：float_mktcap = 流通股本 × 未复权收盘价。送转日股本同步增加，市值连续，**没有虚假跳变**；现金除息日市值按派息额真实下降（不是错误，但若视为口径偏差，这是唯一可能受影响的地方）。turnover_rate 是成交量/流通股本，与复权无关。

## 2. 影响估算（影子信号）
影子：若调仓日所用快照当天恰为该票除权除息日，ADV_shadow = ADV × (adj_factor_当日 / adj_factor_前一因子日)，即把除息造成的市值下降加回；其余不变。重新做行业去均值排名，对比原排名。

| 指标 | 数值 |
|---|---|
| 调仓日 × 评分池票 | 34 × 48 = 1632 对 |
| 快照落在除权除息日的对数 | **16 对 / 15 只票 / 12 个调仓日** |
| 这些票在当期持仓中的权重合计 | 均值 0.82%，最大 6.13%（2026-07-31，600809.SH + 002594.SZ） |
| 因子比 | 1.0037–1.0517（除息率 0.4%–5.2%） |
| 排名变化 | 最大 1 位；**前 25 名入选集合变化 0 次** |

结论：capacity_adv 主信号不依赖复权价；未复权口径只在除息日让 ADV 低约 0.4%–5%，评估窗内没有改变任何一期的入选名单，排名最多差 1 位。**选股和权重层面基本不受影响**；单名 ADV 上限理论上同幅下降，但受影响票都是高 ADV 龙头，上限被 4% 约束，未见变化。

## 3. 收益层面
- 本侧（AI）自检 12.07% 用的是未复权收益，低估；复权后 17.66%（见 AI_ADJ_PRICE_RECEIPT_ZH.md）。
- 正式 Book-Smoke（60万 13.82%/−10.07%，100万 12.23%/−11.62%）由引擎显式补回分红和送转（ENG_PRICE_BASIS_AUDIT_RECEIPT_ZH.md），成立，不受本诊断影响。自检 17.66% 与 Smoke 的差来自成本、整手、成交价（次日开盘）等，不应拿来替代 Smoke。

## 4. 后续
不改权重、不改结论。若要以复权口径重新评估 capacity_adv（含信号或收益），须**先重新预注册**再跑。
