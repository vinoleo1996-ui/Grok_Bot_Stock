# 预注册：60万档集中卫星（叶11 80/20）（Strategy，2026-10-14 07:40 ET）— FROZEN
纸面研究；live=false；promotion=false；禁 GP/小盘/高杠杆；不碰密封窗；不替换 B4；不动三轨文件。sha256 记入 output/strategy_conc60w/PREREG_SHA256.txt。
背景：叶11 report_rc_allup 按 80/20 叠加 capacity_adv（topN 版，GATE_V3）在 60万档 13.54% < 同口径 CORE 13.69%，Alpha 判 FAIL/WATCH，原因疑为整手稀释。本研究**不重判 GATE_V3**（叶11 状态不变），只看执行层能否减轻稀释。

## 1. 基线（L0，已有，不重跑）
cap80+rc20，每腿股票取前 N（60万 6、100万 10），单名合并后 >6% 溢出转 510300（research/b4_paper_extend.py build() 同实现）；引擎 output/v3/book_smoke_gatev3_leaf11_cap80_rc20_{60w,100w}。
## 2. 方案（3 个，写死；两档都跑）
| 代号 | 规则 |
|---|---|
| K1 | 叶11 腿只取前 **3** 名（60万）/ 前 **5** 名（100万），腿预算不变；主干腿 topN 不变 |
| K2 | 最小一笔：任一股票目标金额 < max(1.5 万元, 2 手×前收×100) 的从该腿剔除，剩余名字按原权重在腿内重新归一（迭代至无违规）；腿内全剔除则该腿预算转 510300。两条腿都适用 |
| K3 | K1 + K2 |
共同：单名上限 6% 按**全组合**计（合并后），溢出转 510300；权重和=1；不加杠杆。价格=未复权前收（output/strategy_wf_combo/_raw_cache.pkl，已 shift(1)）。
## 3. 引擎
quantlab.cli book-smoke --run-nav，X2，sleeves core=0/stock=1/alpha_event=0，成本开，整手，60万和100万各跑。单进程串行。
## 4. 指标
- 买不进占比：目标权重>0 的股票（名字×日）中，次日实际持仓为 0 的比例（引擎 target_weights vs actual_weights，按调仓后首日对齐）。
- 目标与实际偏离：每日 Σ|实际−目标|/2 的均值；以及叶11 腿名字的目标合计 vs 实际合计。
- 业绩：两档 CAGR/MDD/Calmar（244）、月/日胜率、成本、分年。
## 5. 判定（只出研究结论）
"缓解稀释"=60万档 CAGR ≥ 同口径 CORE 13.69% 且 MDD 不深于 L0 + 1pp，且买不进占比低于 L0。即使满足，也**不改**叶11 的 GATE_V3 终判（那是 Alpha 的，事后发现），只作为后续执行层规则的证据交 Alpha/Eng。累计尝试数 +3。
