# G1G5 report_rc_allup 权重回执：g1g5_ashare_report_rc_allup_v1（研究级，promotion=false，live=false，未跑 Book-Smoke，禁 GP）
- 预注册：docs/v2/AI_G1G5_REPORT_RC_WHO_PAYS_PREREG_ZH.md，**FROZEN 2026-10-14 00:20:59 ET**（盒子 CST 减 12 小时）；00:21 ET 开跑，约 00:23 ET 出结果。冻结前只看计数，未读任何价格或收益。
- 数据：report_rc_2018plus.parquet（1,917,334 行，n_fails=0，至 20261013）；触发 = disclosure_date actual_date（仅定期报告；预告/快报满窗源不在盘上）；机构名未归一。
- 脚本：research/g1g5_report_rc_allup_events.py（事件）、research/g1g5_report_rc_allup_weights.py（权重+自检）；日志 output/ai_factory/g1g5_report_rc_allup_run.log
- 权重：output/ai_factory/g1g5_report_rc_allup_daily_weights_20261014_122118.parquet，sha256 c980c70368b6caedbe1c021db25e6cbe376927a5991a2ce2faefe13ee403e1b2（50,100 行 / 668 日 / 75 名，2024-01-02→2026-10-09）；meta g1g5_report_rc_allup_run_meta_20261014_122118.json

## 计数闸（满窗，只看计数）
- 事件 239 条 / 144 只（2018:8｜2019:26｜2020:35｜2021:32｜2022:23｜2023:20｜2024:27｜2025:34｜2026:34）；X2 相关（触发 ≥2023-10）101 条 / 74 只 → 通过。

## 合规
Σw≡1；无负权；无 stub；单名 max 4%；行业 max 24%（≤28%）；600519/002371 恒 0；mid_large PIT top300（锚 2024-06-28）；T2 入场持有 60 日。
日均 7.8 名；压舱 510300 均值 68.8%（20%–100%），全压舱 130 天；单边日均换手 1.04%。

## 自检（复权：个股 adj_factor×X2 close，510300 close_hfq；w(t−1)×r(t)，毛、无成本，非 Book-Smoke）
- 毛 CAGR **16.65%** / MDD **−17.50%**（510300 12.34% / −16.25%；capacity_adv 17.66% / −13.18%）；β 1.01
- 残差 α **+3.76%/年**；分年：2024 **−0.43%**｜2025 +4.29%｜2026 +6.35%
- 去 β 残差相关：vs capacity_adv 0.038｜earnings_event 0.105｜insider_increase 0.116｜equity_incentive 0.100｜unlock_rebound 0.069｜interim_div_init −0.005｜block_trade −0.075（全部 <0.5）
- 逐日 Jaccard vs 21 个前包：max 0.25（buyback_cancel）；vs earnings_event max 0.167、vs capacity_adv max 0.111 → 无同构硬拒，不属 earnings_event 强度过滤
- G6 pass；peak RSS 1,112 MB（≤1.5GB）

## 组合层（自检估计，非 Book-Smoke；conc v2 topN，60万 N=6、100万 N=10，合并单名 ≤6%）
| 档 | capacity_adv 单独 | cap80+本叶20 | cap70+本叶30 |
|---|---|---|---|
| 60万 | 14.96% / −13.63% / SR 0.86 | 15.41% / −14.12% / 0.88 | 15.62% / −14.37% / 0.88 |
| 100万 | 18.85% / −12.25% / SR 1.12 | 20.40% / −12.41% / 1.19 | 20.73% / −12.88% / 1.19 |
- 两档 CAGR 与 Sharpe 均优于 capacity_adv 单独；**MDD 两档均略差**（−0.16 至 −0.75pt）。按冻结时写入的「CAGR 与 MDD 均优」严格口径 → **未过**；按仅收益口径 → 过。

## 判定
叶层闸门全过（ρ<0.5、α>0、Jaccard、G6、RSS）。注意 2024 残差 α 为负、压舱 69%。组合层收益改善但回撤略深 → 建议送 Alpha 裁定（ACCEPT 与否由 Alpha 判 MDD 条款），本侧不自封 research_candidate。
未做：预注册第 3 条事件层重合（vs earnings_event 事件窗占比）未单独计算，逐日 Jaccard 已覆盖持仓层。
