# 集中化 v2 稳健性检验预注册（B1/B4）（2026-10-13 ~14:25 ET，生成变体前写定）

状态：研究级；promotion=false；live=false；禁 GP；不跑 Book-Smoke（引擎由 Eng 跑）；**不解封、不读密封窗收益**。
基准：output/small_aum_concentration/v2/B_{B1_equal,B4_50_25_25}_topN_{60w,100w}.parquet（N=6/10，全组合单名≤6%）。

## 变体（产出 output/small_aum_concentration/v2_robust/）
1. **N 扰动**：60万 N=5 / N=7；100万 N=9 / N=11；其余规则不变。文件 Nminus_/Nplus_B_{arm}_topN_{tier}.parquet（实际文件名前缀 Nminus/Nplus）。
2. **剔除前 3 只高价股**：在基准集中化权重中，取中位一手金额（前收×100）≥2 万元的个股，按 Σ(日权重)（持仓暴露，**不用收益**）降序取前 3，
   每个（组合×档位）单独确定，从各腿剔除后重新执行前 N 规则（下一名递补）。文件 drop3hp_{arm}_topN_{tier}.parquet；剔除名单写入 SUMMARY.json。
## 交 Eng 的引擎检验（事前写定判读）
- 每个变体与基准在对应 AUM 档跑 X2 Book-Smoke（strategy_v1 成本），报告：CAGR/MDD/夏普、**分年收益**（2024(6/3起)/2025/2026(至10/9)）、**成本×1.5** 下 CAGR。
- 稳健判读：N±1 两个变体 CAGR 与基准差均 ≤1.0pp 且 MDD 不劣于基准 2pp；剔除 3 高价股后 CAGR 下降 ≤1.5pp；成本×1.5 下仍 > capacity_adv 同档同口径。任一不满足→集中化收益判为脆弱。
- 分年：任何一年相对基准反向超过 3pp 须单列说明。

## 2018–2024-05 密封窗口：前提与缺口（只列条件，不解封）
前提：Leo 在本聊天明确授权解封；预注册（含本文件判读）已冻结；各叶规则零改动；一次性跑，结果不回流调参。
数据覆盖（仅查字段时间跨度，未读收益）：
- 行情面板 X2 stitch：2014-01 起 ✓；mid_large PIT：2015-01 起 ✓；daily_basic（市值/换手）2014 起 ✓。
- 公告 PIT（earnings_event / insider_increase 事件源）：2018-01 ~ 2024-05 ✓（_post202406 接续）。
- capacity_adv：现有权重只覆盖 X2，需在密封窗重新生成（规则须冻结）；其所依赖 ADV/容量数据 2014 起，原则上可覆盖。
- earnings_event：分类公告可覆盖；但 forecast_1y/express_1y 幅度数据仅近一年（本叶未用幅度，不阻断）。
- insider_increase：公告可覆盖；holder_trade_1y 仅近一年（本叶未用）。
缺口：股票池锚定 2024-06-28 的实现（select_mid_large_topn_light anchor）在密封窗会造成严重前视，**必须改为逐期 PIT 锚定**后才可跑；
未复权收盘价在长窗口偏差更大，需复权面板；510300 2018 前分红口径需核；SW 行业 PIT 版本切换（SW2014→SW2021）需核；Engine 是否支持 2018 起成本/整手配置需 Eng 确认。

## 执行注记（生成后，非规则修改）
drop3hp 变体：剔除名字后各腿个股预算未回补，归一化把少数名放大到 6.2%–6.4%；已按 v2 规则 3（全组合单名≤6%，超出进 510300）事后削顶，影响见 SUMMARY.json 的 post_cap_cut_mean。
剔除名单（四个组合×档位相同）：300750.SZ 宁德时代、002594.SZ 比亚迪、300760.SZ 迈瑞医疗。
