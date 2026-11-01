# 预注册：Riskfolio-Lib CDaR 组合层（Strategy，2026-10-14 07:32 ET）— FROZEN
纸面研究；live=false；promotion=false；禁 GP/小盘/高杠杆（权重和=1，不加杠杆，不做空）；不碰密封窗；不替换 B4；不动三轨文件。sha256 记入 output/strategy_cdar/PREREG_SHA256.txt。
工具：riskfolio-lib 7.4.0（已装进 /workspace/qlvenv，求解器 CLARABEL）。

## 1. 资产（6 本书，日收益 = 已有引擎 book-smoke BOOK nav，按档分开）
CAP=capacity_adv；B4（冻结）；S6（**16 组事后挑选**）；四条 KEEP 叶：capacity_adv（即 CAP）、earnings_event(EE)、insider_increase(II)、equity_incentive(EI)。去重后 6 个：CAP/B4/S6/EE/II/EI。单叶引擎目录 output/v3/book_smoke_g1g5_{earnings_event,insider_increase,equity_incentive}_x2。
## 2. 优化（4 个配置，写死，不加网格）
| 代号 | 目标 | 约束 |
|---|---|---|
| C1 | 最大化训练段均值收益 | 训练段 MDD（Riskfolio 非复利口径）≤25% |
| C2 | 同上 | MDD ≤15% |
| C3 | 最小化 CDaR(α=0.05) | — |
| C4 | 最大化 均值/CDaR(α=0.05) | — |
共同：0≤w_i≤1，Σw=1，rf=0，历史估计（method_mu='hist'）。
## 3. Walk-forward（写死，与前两轮一致）
F1：训练 2024-06-03→2024-12-31，验证 2025-01-02→2025-07-31（**在 2025-08 之前**）；F2：训练 2024-06-03→2025-07-31，验证 2025-08-01→2026-10-09。拼接：≤2025-07-31 用 F1 权重，之后用 F2 权重（2024 段为 F1 的训练段，只作全窗参考）。
## 4. 引擎复核
把书级配比展开成个股权重：Σ w_i × 书 i 的日权重（CAP=冻结文件；B4/S6=output/strategy_wf_combo/_w_S0/_w_S6；EE/II/EI=wf_combo 预注册所用叶文件、非集中版）；单名 >6% 溢出转 510300；按档分别生成；跑 quantlab.cli book-smoke --run-nav，X2，sleeves core=0/stock=1/alpha_event=0，成本开（strategy_v1），整手，60万/100万。拼接后权重相同的配置只跑一次（计尝试数时仍按 4 计）。单进程串行。
## 5. 判定
- "验证段优于 B4"=引擎口径下 F1 验证与 F2 验证、60万与100万共 4 格，CAGR ≥ B4 且 MDD 不深于 B4，4 格全过。
- 另报：全窗 CAGR/MDD/Calmar、月/日胜率、换手、分年；C1/C2 的 MDD 门按引擎全窗是否 ≤25%/≤15%。
- 累计尝试数 +4。凡含 S6 的配比都标"事后挑选成分"。不触发任何轨道变动。
