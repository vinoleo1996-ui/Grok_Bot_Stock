# 【FROZEN 2026-10-14 09:13:03 ET】G1G5 预注册：现金流应计 + RNOA 改善（g1g5_ashare_cfacc_rnoa_v1，叶19）
状态：**FROZEN**，冻结前未读任何本叶收益。研究级；promotion_approved=false；live=false；禁 GP/高杠杆；不自跑 Book-Smoke；非卖方/调研/金股/一致预期。主 Agent 08:24 方向①；Leo 09:12 指令。

## 机制与谁付钱
利润中现金含量低（高应计）的公司盈利持续性差，市场按"报表利润"定价、对现金流质量反应不足；经营资产回报（RNOA）同比改善的公司被按旧盈利能力定价。付钱的是只看 EPS 增速的交易者。与库内 accrual_quality（资产负债表 WC 应计）区分：本叶用**现金流量表**口径 + RNOA 变化。

## 规则（冻结后不调）
1. 数据：financials_pit_tushare（n_income/operate_profit，YTD）、bs_cf_pit_tushare（total_assets/total_liab/equity_parent/n_cashflow_act）；同一 (ts_code,end_date) 取**最早** available_at 版本（不用后续更正）；available_at 次一交易日起可用。
2. YTD→单季→TTM（4 个连续单季全齐才算）。
3. CFACC = (NI_ttm − OCF_ttm)/平均总资产(本期、去年同期)；RNOA_proxy = OP_ttm / 平均(总资产−0)（无现金/金融负债明细，披露为 ROA_op 代理）；ΔRNOA = RNOA_proxy − 4 季前值。
4. α_raw = rank(−CFACC) + rank(ΔRNOA)（等权，池内百分位）。
5. 正交/中性：池内截面 OLS 对 SW L1 dummy + log 流通市值 + mom20 + mom60 + vol20 + log ADV20（capacity_adv 机制代理）+ 库内 BS 应计（若可得，否则披露缺）取残差；分域（P70/P90：小微/中小/大盘）rank→[-1,1]，再全池行业+市值残差一次 → base-α。
6. 慢 α：财报更新驱动，再平衡每 **20** 交易日。快 gate（1–3 日，不入 α）：近 3 日残差收益最小值落池内最低 5% → gate=0。禁止与 α 加权合成。
7. 评价权重：≤20 名、每名 ≤4%、行业帽 HI_LIQ 25%/FULLA 28%，余额 510300；硬排除 600519/002371；仅 gate=1 按 α 降序。
8. 宇宙：HI_LIQ_V1.1（主，纸面路径）+ FULLA_V1（研究；掩码由 HI_LIQ 掩码列重建：非 ST/非停牌/上市≥60 日/ADV20≥300 万，覆盖密封窗）。
9. 窗口：密封 2018-01-02→2024-05-31；X2 2024-06-03→2026-10-09；60万(Top6)/100万(Top10)；年化 244 主/252 对照；复权、T+1 开盘、17.5bp/单位换手。
10. 主交付：日度 base-α 向量。

## 硬闸
覆盖：HI_LIQ 每再平衡日可算 α 名数 median ≥300；FULLA ≥800。Jaccard ≥0.7 硬拒；ρ_excess >0.5 只作过滤；换手 >20%/日或成本>毛超额一半 → 不可交易；衰减门 v1.1 非 KEEP 不过；Gate A（ρ vs cap<0.5 且残差 α>0）；Gate B（cap80+叶20 两档净 CAGR>cap）；GATE_V3（MDD≤25%，另报 ≤15%）；跑不赢主干即砍（WATCH）。自检走新池 leaf_selfcheck_v3 --universe HI_LIQ_V1.1（含 HAC t，仅披露）。
