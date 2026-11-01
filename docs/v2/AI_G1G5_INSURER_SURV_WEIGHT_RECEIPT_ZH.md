# G1G5 叶14 权重回执：g1g5_ashare_insurer_surv_v1（研究级，promotion=false，live=false，未跑 Book-Smoke，禁 GP）
- 预注册：docs/v2/AI_G1G5_INSURER_SURV_WHO_PAYS_PREREG_ZH.md，**FROZEN 2026-10-14 05:58:36 ET**（读收益前；候选筛选时已见粗计数，已注明）。05:58 ET 开跑。
- 脚本 research/g1g5_insurer_surv_weights.py；日志 output/ai_factory/g1g5_insurer_surv_run.log；meta g1g5_insurer_surv_run_meta_20261014_175849.json
- 权重：output/ai_factory/g1g5_insurer_surv_daily_weights_20261014_175849.parquet，sha256 1d68e8d3298942ad095ea24aaf2bb92254ee55fc789d61face99d2da42c9ab2f（39,412 行/668 日/59 名）
## 计数与去重
全窗 289 条/85 只（2021:31/2022:63/2023:43/2024:47/2025:59/2026:46）；X2 相关 161 条/66 只。与 stk_surv V1 30 日内重合剔除 16 条（9.9%）→ 145 → 入场 141（2024:48/2025:44/2026:44）。
## 合规
Σw≡1、无负权、单名 4%、行业 max 24%、600519/002371 恒 0；日均 10.2 名；压舱 59.1%。
## 标准自检（复权，毛、无成本）
- 毛 CAGR 17.21% / MDD −16.98%（510300 12.34%/−16.25%；capacity_adv 17.66%/−13.18%）；β 1.08
- 去 β 残差 α +3.78%/年；分年 2024 **−3.95%**｜2025 +15.16%｜2026 **−2.86%**
- 风格中和（510300 + 红利价差 510880 + 大盘价差 510050）：α_style +4.67%/年（红利载荷 −0.09，大盘载荷 −0.42 → 偏小于大盘端，非红利暴露）
- 去 β ρ：stk_surv 0.072｜capacity_adv −0.342｜earnings_event 0.426｜report_rc_allup 0.089｜analyst_recoverage 0.276｜equity_incentive 0.381｜insider −0.010
- 入场落在窗内：stk_surv 2.1%｜report_rc_allup 4.3%｜earnings_event 5.7%
- 逐日 Jaccard vs 24 包 max 0.25（buyback_cancel）；vs stk_surv 0.111；无硬拒
- G6 pass；peak RSS 1,020 MB
## 自检 v2（research/leaf_selfcheck_common.py）
- 衰减门 **DECAY_DOWNGRADE**（H2：近 252 日净 CAGR ≤ 510300 净；最新滚动残差 α +0.07%）
- 双边换手 2.27%/日；净 CAGR 16.04%（全窗）；成本拖累 1.00%/年；毛超额 +4.86% → 可交易
- 组合门（CAGR/MDD/Calmar）：
| 档 | cap 单独 | 原样叠加 | A 去β叠加 |
|---|---|---|---|
| 60万 | 15.11/−13.65/1.108 | 15.68/−14.24/1.102 | 15.45/−13.72/1.126 |
| 100万 | 18.85/−12.25/1.538 | 20.08/−12.07/1.664 | 18.48/−12.61/1.466 |
现行 ✗（60万 MDD 更深）｜A ✗（100万 CAGR 更低）｜B ✗（60万 Calmar 略低）
## 判定
失败条件 5（衰减门 DOWNGRADE）→ **不过**；另触发条件 3（2024、2026 两年残差 α 为负 → WATCH）与条件 4（现行组合门不过）。ρ vs stk_surv 0.072 未触发同构。**登记 WATCH，不送 Alpha ACCEPT**。α 集中在 2025 单年。
