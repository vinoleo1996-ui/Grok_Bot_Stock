# 【DRAFT → 判定 FAIL（同构）】G1G5 叶8 候选 R4：行业 ETF 申赎流极值反转（g1g5_ashare_ind_etf_flow_rev_v1）
2026-10-13 ~19:40 ET。未读任何收益，未计数，未跑 X2。研究级；live/promotion=false；禁 GP。

## 谁付钱（拟）
极端净申购时追涨申购的 ETF 投资者形成非信息性买压，随后均值回归；极端净赎回时机械赎回者卖在低位。

## 同构判定
| 维度 | 已 FAIL 的 industry_etf_rotation（research/g1g5_industry_etf_rotation_weights.py） | 本叶 R4 |
|---|---|---|
| 数据 | data/v2/etf/share_pit/ind_etf_share_flow_by_sw_l1.parquet（flow_est_wan_yuan） | **同一文件同一字段** |
| 可交易标的 | SW L1 代表性行业 ETF（sw_l1_etf_map_pit_daily） | **同一组行业 ETF** |
| 信号方向 | 买入「份额净赎回」行业（资金流入行业不入选） | 只做多时，「极端申购后回落」只能表达为：买极端净赎回行业 / 回避极端净申购行业 → **与旧叶同号** |
| 差异 | 旧叶多一个「去β残差仍为正」的背离过滤 | 去掉过滤 = 旧叶的父集合（更粗），不是新信息维 |
- 只做多、不加杠杆、不做空的约束下，R4 无法表达「做空极端申购行业」这一独有的一腿；可交易部分与旧叶同数据、同标的、同信号方向，仅少一个过滤条件。V30 的先例也是「去掉主轴塌成粗版 → 自拒」。
- 被动族：行业 ETF 申赎流与 idx_rebal* 都是被动资金的价格压力，同源。

**结论：判同构，直接记 FAIL，不计数、不冻结、不跑 X2。**转备选：解禁后「利空出尽」反弹（AI_G1G5_UNLOCK_REBOUND_WHO_PAYS_PREREG_ZH.md）。
