# G1G5 叶13 权重回执：g1g5_ashare_stk_surv_gap1y_v1（研究级，promotion=false，live=false，未跑 Book-Smoke，禁 GP）
- 预注册：docs/v2/AI_G1G5_STK_SURV_WHO_PAYS_PREREG_ZH.md，L=25 已填，**FROZEN 2026-10-14 05:22:55 ET**；约 05:23 ET 开跑。
- 如实说明：变体计数脚本先跑出结果，「主变体=优先级第一个过闸者」这条规则写在看过计数之后、读任何收益之前；优先级按指令顺序，未因计数改动。
- 数据：stk_surv_2018plus.parquet（395,691 行，n_fails=0）；池内记录实际从 2021 起。
- 脚本：research/g1g5_stk_surv_events.py、research/g1g5_stk_surv_weights.py；日志 output/ai_factory/g1g5_stk_surv_run.log
- 权重：output/ai_factory/g1g5_stk_surv_daily_weights_20261014_172311.parquet，sha256 bfdf369bdb911d0a7d0c0baaf0c1d9c2577fcfd5e36a0a16c2a370c6e6e9a499（42,084 行/668 日/63 名）
## 计数（全窗｜X2 相关）
V1 断档≥1年再调研 126/103 只｜108/92 只（主变体）；V2 财报后 5 日 291/99｜176/74；V3 滚动10日≥20家 355/110｜207/90。滚动 10 日机构数 p50 8、p75 25、p90 76.8、p95 162、p99 287.7，≥20 占 30.6%。
## 事件与合规
X2 事件 108 → 反转过滤剔除 33（30.6%）→ PIT 成员等再剔 7 → 入场 68（2023:1/2024:16/2025:21/2026:30）。Σw≡1、无负权、单名 4%、行业 max 12%、600519/002371 恒 0。日均 5.7 名，压舱均值 **77.0%**；换手 0.76%/日。
## 自检（复权，毛、无成本，非 Book-Smoke）
- 毛 CAGR 12.05% / MDD −17.47%（510300 12.34%/−16.25%；capacity_adv 17.66%/−13.18%）；β 0.94
- 残差 α **+0.51%/年**；分年 2024 −3.09%｜2025 +0.08%｜2026 +0.41%
- 去 β ρ：capacity_adv 0.396｜report_rc_allup 0.117｜earnings_event −0.028｜analyst_recoverage 0.251｜insider 0.354｜equity_incentive 0.357｜unlock 0.181｜interim_div −0.073｜block_trade −0.017（全部 <0.5）
- 逐日 Jaccard vs 23 个旧包 max 0.30（block_trade）；无硬拒
- 入场落在 earnings_event 窗内 1.5%（1/68），report_rc_allup 1.5%（1/68）
- G6 pass；peak RSS 999 MB
## 组合层门（cap80+叶20）
| 档 | cap 单独 | cap80+叶20 | cap70+叶30 |
|---|---|---|---|
| 60万 | 14.96%/−13.63% | 15.16%/−13.84% | 15.25%/−13.95% |
| 100万 | 18.85%/−12.25% | 19.25%/−12.47% | 18.94%/−12.96% |
→ CAGR 两档略好，**MDD 两档都更差 → 不过**。
## 判定
**WATCH，不送 ACCEPT**：组合层门 MDD 不过；残差 α 仅 +0.51% 且 2024 为负；毛收益低于 510300；压舱 77%。正交性好（与事件类包几乎不重叠）。
