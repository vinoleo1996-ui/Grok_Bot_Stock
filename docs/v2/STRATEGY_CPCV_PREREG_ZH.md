# 预注册：CPCV 复核（Strategy，2026-10-14 07:25 ET）— FROZEN
状态：FROZEN（写完即冻结，sha256 记入 output/strategy_cpcv/PREREG_SHA256.txt；冻结后不改，任何偏离写进回执"偏离"一节）。
纸面研究；live=false；promotion=false；禁 GP/小盘/高杠杆；不碰密封窗；不替换 B4；不动三条纸面轨的 STATUS/FROZEN_CONFIG/权重。

## 1. 对象（全部用已有的引擎 book-smoke 日收益，X2 2024-06-03→2026-10-09，core=0/stock=1，成本开，整手，60万/100万）
| 代号 | 说明 | 引擎目录 |
|---|---|---|
| CAP | capacity_adv 主干（基准1）| output/v3/book_smoke_g1g5_capacity_adv_x2 |
| B4 | B4 冻结（基准2）| output/strategy_wf_combo/engine/S0_{60w,100w} |
| S6 | S6 影子，**16 组事后挑选** | output/strategy_wf_combo/engine/S6_* |
| M13 | M7+β≤0.70（WF），**含 S6、事后口径** | output/strategy_dd_budget_combo/engine/M13_* |
| L11 | 叶11 report_rc_allup 80/20 叠加 capacity_adv（topN 版，Alpha GATE_V3 已跑）| output/v3/book_smoke_gatev3_leaf11_cap80_rc20_{60w,100w} |
不新跑引擎；本节没有新组合，L11 是 Alpha 的组合，计入 Strategy 累计尝试 +1（29→30）。

## 2. CPCV 设定（写死）
- 日收益 = BOOK nav.csv 的 nav.pct_change()。按时间切成 **N=10** 个连续等长组，每次取 **k=2** 组做测试 → C(10,2)=**45** 个切分，对应 φ=k/N·C(N,k)=9 条回测路径。
- **purge=5 个交易日**：每个测试组开头（与训练段相邻处）丢掉 5 天；**embargo=5 个交易日**：测试组结束后 5 天不进训练段。五个对象都是固定权重书（不在训练段拟合），所以 purge/embargo 只影响测试段边缘；M13/S6 的权重来自整窗或 F1/F2 拟合，CPCV 不能消除这层事后挑选，回执里照写。
- 每个切分在测试日收益上算：CAGR（244 天年化）、MDD（测试段内拼接净值）、Calmar=CAGR/|MDD|。
- 报：每对象每档三项的分布（均值、中位数、P10、P90、最小）；**P(对象 CAGR < CAP)**、**P(对象 CAGR < B4)**、P(Calmar < CAP)、P(Calmar < B4)，都按 45 个切分逐一配对比较。9 条路径的路径级 CAGR 也报（路径=每组只出现一次的组合拼接）。
## 3. 多重检验修正（写死）
- **PBO（CSCV, Bailey et al. 2015）**：试验矩阵 = Strategy 已跑引擎的 29 组（wf_combo 16 + dd_budget 13），每档单独算；S=16 个连续块，C(16,8)=12870 个划分；样本内按 Sharpe 选最优，看样本外排名 logit；PBO=P(logit≤0)。
- **Deflated Sharpe（Bailey & López de Prado 2014）**：对 B4/S6/M13/L11/CAP，试验数取 **N_trials=37**（29 + L11 1 + 本轮 CDaR 预留 4 + 60万集中预留 3，偏保守），试验间 Sharpe 方差取 29 组的实测方差；报 DSR 概率（>0.95 视为显著）。
## 4. 判定（只出结论，不触发任何轨道变动）
- "CPCV 稳健优于 B4"= 两档 P(CAGR<B4) ≤ 0.3 且 P(Calmar<B4) ≤ 0.3。S6/M13 即使满足，也只能写"事后挑选、待前向"。
- 不改任何纸面轨。产物 output/strategy_cpcv/，回执并入 docs/v2/STRATEGY_CPCV_CDAR_CONC60_ZH.md。
