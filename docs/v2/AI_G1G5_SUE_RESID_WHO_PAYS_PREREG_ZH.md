# 【FROZEN 2026-10-14 09:13:03 ET】G1G5 预注册：去敏 SUE 残差（g1g5_ashare_sue_resid_v1，叶20）
状态：**FROZEN**，冻结前未读任何本叶收益。研究级；promotion_approved=false；live=false；禁 GP/高杠杆；不自跑 Book-Smoke；**不用分析师一致预期**（时间序列 SUE）。主 Agent 方向③；Leo 09:12 指令。

## 机制与谁付钱
盈余公告后漂移（PEAD）：投资者对季度盈余意外反应不足。原始 SUE 与规模、行业、动量、流动性（capacity_adv）高度共线；本叶只取**去敏残差**部分——扣掉这些已定价/已在库内的暴露后的"纯意外"。付钱的是公告后锚定旧盈利预期的交易者。

## 规则（冻结后不调）
1. 数据：financials_pit_tushare n_income_attr_p（YTD），同一 (ts_code,end_date) 取最早 available_at 版本，次一交易日起可用。
2. 单季 NI_q；SUE = (NI_q − NI_{q−4}) / std(过去 8 个季度同比差, 至少 6 个)；|SUE| 截尾 ±5。
3. 时效：公告后 ≤60 交易日有效（之后无信号）；同时间仅用最新一季。
4. 去敏：池内截面 OLS，SUE 对 SW L1 dummy + log 流通市值 + mom20 + mom60 + vol20 + log ADV20（capacity_adv 代理）+ 叶19 CFACC rank（若可得）取残差；分域 rank→[-1,1]，再行业+市值残差 → base-α。
5. 慢 α 再平衡每 **20** 交易日（每日 α 向量照常输出）；快 gate 同叶19（近 3 日残差收益最低 5% → 0），不入 α。
6. 评价权重/宇宙/窗口/成本/年化/硬闸：与叶19 预注册完全相同（覆盖闸：HI_LIQ median ≥200；FULLA ≥500）。
7. 与 earnings_event 腿（事件型）必报 Jaccard/ρ；ρ>0.5 只作过滤。
