# g1g5_ashare_industry_etf_rotation_v1 — who_pays 预注册（2026-10-13 ~13:20 ET，跑权重前写定）

状态：research_candidate（不自封）；promotion=false；live=false；禁 GP；不自跑 Book-Smoke。

## who_pays（量价背离：赎回下的残差韧性）
行业 ETF 份额被持续净赎回（申赎资金撤出：散户割肉/机构调出），但该行业去市场β后的残差收益仍为正——
说明赎回带来的卖压被知情/配置型买盘吸收。付钱的是“按份额流出机械赎回/离场”的对手盘：
其卖出被价格吸收后，残差继续兑现。核心条件是**资金流出 + 残差韧性的背离**，不是单纯动量（不买涨幅最大的行业，
资金流入行业一律不入选），也区别于已灭的 etf_core_sleeve（买份额流入行业）与 resid_etf（股票残差×流入加成）。

## 事前固定规则（无收益探针调参）
- 资产：每个申万一级取 PIT 代表 ETF（data/v2/etf/sw_l1_etf_map_pit_daily.parquet 的 etf_ts_code，no_etf=False）；价格用 data/v2/etf/etf_daily_adj.parquet 后复权 close_hfq；基准/压舱 510300.SH。
- 残差：r_i − β_i·r_510300，β_i 为 120 日滚动；resid20 = 近 20 日残差和。
- 资金：行业层 ind_etf_share_flow_by_sw_l1 的 flow_est_wan_yuan 近 20 日和 ÷ 行业 ETF 规模（ind_etf_share_flow_pit 份额×净值求和，取 20 日前），仅用 available_at ≤ 信号日的行。
- 选择：流动性门 amt20 ≥ 2000 万元（数据单位千元，≥20000）；F（20日资金/规模）处于当日可选行业的最低三分位（净赎回最重）且 F<0；其中 resid20>0 者，按 resid20 降序取前 3。
- 权重：每个 ETF 20%（单资产/单行业上限 20%），余量 510300（≥40%）；无入选则 100% 510300。
- 时序：信号用 d−1 收盘及之前可得数据 → 权重记于 d（T+1）；每 5 个交易日调仓一次。
- 窗口：2024-01-02 ~ 2026-10-09。
- 可成交：100万×20%=20万，对 amt20≥2000万元 参与率 ≤1%。

## 自检门
逐日 Jaccard（含 ETF 持仓，vs 已灭各包+capacity_adv+叶1/叶2/叶3）≥0.7∧≥50%日 硬拒；G6；peak≤1.5GB；去β ρ_excess vs capacity_adv<0.5 且 残差α>0；分年 α；毛 CAGR/MDD；换手。

## 事前已知缺口
- 代表 ETF 按名称关键词映射申万一级（research_grade），部分为主题 ETF（如“航空航天”映射交通运输、“消费电子”映射电子），跟踪误差大；代表 ETF 会随 PIT 切换。
- aum_wan 字段大量缺失，规模用份额×净值自算；份额数据 T+1 可得（available_at 次日）。
- 无 IOPV/折溢价数据；ETF 实际冲击未建模。
- 跑前仅检查了数据覆盖（27 行业/日均 26 个有 ETF），未看收益。
