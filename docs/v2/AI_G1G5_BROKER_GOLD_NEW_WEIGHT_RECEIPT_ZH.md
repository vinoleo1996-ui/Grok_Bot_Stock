# 叶16 broker_gold_new（券商金股同月 ≥2 家新进）X2 权重与自检回执
时间：2026-10-14 07:4x ET（AI）。预注册：AI_G1G5_BROKER_GOLD_NEW_WHO_PAYS_PREREG_ZH.md（FROZEN 06:51:36 ET）+ AI_G1G5_BROKER_GOLD_NEW_ALLA_SUPPLEMENT_PREREG_ZH.md（FROZEN 07:25:11 ET，07:27 追加 Leo 取消禁小盘说明）。主 Agent 07:27 ET 批准 X2。按冻结条款执行，阈值未改。promotion=false；live=false；禁 GP/高杠杆；未跑 Book-Smoke/8787。

## 结论：两池均 WATCH（不过）
- 硬闸 1–2（同构/ρ）：过；硬闸 3（可交易）：**不过**（无毛超额且成本拖累 >1%/年）；硬闸 4（衰减门 v1.1）：**DOWNGRADE**；Gate A：**不过**（残差 α<0）；Gate B：**不过**（两档叠加均低于 capacity_adv）；GATE_V3（MDD≤25%，另报 ≤15%）：**FAIL**（MDD 两档都满足，CAGR 两档都输）。244/252 两口径结论一致。
- 交 Alpha ACCEPT 复核（由主 Agent 转）。

## 产物
| 池 | 权重 | sha256 前12 | run_meta |
|---|---|---|---|
| 全A（主） | output/ai_factory/g1g5_broker_gold_new_alla_daily_weights_20261014_192744.parquet | 7f033b4b10fc | output/ai_factory/g1g5_broker_gold_new_alla_run_meta_20261014_192744.json |
| mid_large（对照） | output/ai_factory/g1g5_broker_gold_new_daily_weights_20261014_192827.parquet | 4da6631255ee | output/ai_factory/g1g5_broker_gold_new_run_meta_20261014_192827.json |
- 脚本 research/g1g5_broker_gold_new_weights.py（sha 0920d0b474bb；BGN_POOL=all_a/mid_large），由 tp_rerate 模板改写；事件口径与计数脚本一致。
- 窗口 2024-01-02→2026-10-09；每日权重和=1（510300 压舱）；600519/002371 恒 0；单名 4%、≤20 名、SW L1 ≤ 28%（实测最大 16%）；峰值 RSS 1.09GB/1.05GB（≤1.5GB）。
- 时序：当月第 1 个交易日收盘后可得；第 2 个交易日写权重 → T2（第 3 个交易日）开盘成交；持有至当月最后一个交易日收盘。
- 实现细节（预注册未写明，已披露，未看收益前定）：同日事件 >20 名时按券商家数降序、代码升序取前 20。

## 关键数字（244 主报；自检估计，非 Book-Smoke）
| 项 | 全A（主） | mid_large（对照） |
|---|---|---|
| 事件 / 日均持股 / 压舱 | 314 / 7.75 / 69% | 221 / 6.19 / 75% |
| 单叶毛 CAGR / MDD | 6.71% / −18.81% | 9.54% / −21.11% |
| 残差 α（去β，年化）总 / 2024 / 2025 / 2026 | −5.36% / −8.10 / +3.70 / −10.91 | −2.81% / −3.46 / +4.99 / −8.85 |
| 双边换手/日 | 6.64% | 5.28% |
| 净 CAGR（T+1 开盘，17.5bp）| 4.44%（毛 6.49%，基准 11.93%） | 7.42%（毛 9.23%） |
| 成本拖累/年；毛超额 | 2.84%；−5.44% → 不可交易 | 2.25%；−2.70% → 不可交易 |
| 衰减门 v1.1 | DOWNGRADE（最新滚动 α −11.3%） | DOWNGRADE（−8.9%） |
| ρ_excess vs capacity_adv | −0.326 | −0.332 |
| ρ_excess vs report_rc_allup | 0.081 | 0.050 |
| ρ_excess vs earnings_event | 0.277 | 0.216 |
| ρ_excess vs analyst_recoverage | 0.172 | 0.069 |
| ρ_excess vs insider/equity_inc/block/tp_rerate | 0.025/0.071/0.065/0.202 | −0.088/−0.049/0.073/0.171 |
| 逐日 Jaccard max | 0.25（earnings_event） | 0.333（earnings_event、tp_rerate） |
| CMC vs B4：ΔIC / ΔICIR / ρ vs B0 | −0.0001 / −0.021 / 0.037 | 0.0004 / −0.010 / 0.039 |
| CMC ΔCAGR 净 60万/100万 | −1.28pp / −1.78pp | −1.41pp / −1.64pp |
| cap80+叶20 vs capacity_adv 60万 CAGR / MDD | 13.29% vs 13.93% / −13.94% vs −14.24% | 13.31% vs 13.93% / −14.02% |
| 同上 100万 | 16.79% vs 17.77% / −12.59% vs −12.47% | 17.03% vs 17.77% / −12.78% |
| 叠加 B4 ΔCAGR 60万/100万 | −1.39 / −2.11pp | −1.36 / −1.85pp |
| 252 对照（cap vs cap80+叶20） | 60万 14.42% vs 13.75%；100万 18.39% vs 17.37% | 60万 13.77%；100万 17.62% |
| 20 日 IC / RankIC / ICIR（resid_z） | 0.0017 / 0.0089 / 0.060 | 0.0023 / 0.0100 / 0.067 |
| 前视检查（截断 2024-12/2025-06/2026-03） | PASS（0 差异） | PASS |
- GATE_V3：两档 MDD 都在 −15% 以内，故 ≤25% 与 ≤15% 两变体结论相同；约束不起作用，CAGR 最大化解为不加本叶（capacity_adv 单独）。

## 披露
- 小盘：全A池含小盘，仅披露；全A 比 mid_large 更差（残差 α −5.4% vs −2.8%）。
- 前视检查的截断方式：broker_recommend 无逐条 available_at，按“月份第 1 个交易日 ≤ T 才可用”截断后重跑，与全量比较 date≤T 的权重。
- 因子报告/summary.json 的 resid_z 与 factor_report 沿用 mid_large 池上下文，全A 版仅作参考。
- 单叶 gross_cagr、残差 α 来自权重脚本内置自检（年化 252 系数）；成本/净收益/组合边际为 leaf_selfcheck（244）。
