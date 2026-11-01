# HI_LIQ_V1.1 五事件腿 §8 补充（AI，2026-10-14 09:11 ET 计算；10-18 00:13 ET 补成文档（按 mtime 更正，原写 00:30））
- 数据：output/ai_factory/hiliq_sec8/sec8_supplement.json（脚本 research/ai_hiliq_sec8_supplement.py，峰值 RSS 1.35GB）。窗口 X2 2024-06-03→2026-10-09，17.5bp，年化 244。只读腿文件；live=false；未派烟。
- **口径说明（重要）**：AI 的风格集为 SW L1 + logmv + mom20 + vol20。这**不是** Alpha 冻结的 §8 风格集（SW L1 + log 流通市值 + β120 + mom(t−120→t−20) + log ADV20）。§8 判定以 Alpha v3（docs/v2/ALPHA_HILIQ_LEGS_ACCEPT_20261014_ZH.md，**NO_ACCEPT**）为准，本表只作交叉参考。equity_incentive 的符号分歧见 docs/v2/AI_EQINC_SEC8_RECONCILE_ZH.md：B 的符号完全由残差风格集决定，没有稳健特质收益。
- 各列定义：
  - 残差 IC：0/1 持仓先对 SW L1 + logmv + cap 持仓 0/1 取残差，与 ε 累计 t+2→t+21 做 Pearson；t_nw 的 lag 为 h−1。
  - 中性净：账簿口径。股票袖约 80%，不归一化；stock_share 的定义见 reconcile 文档第 3.5 条。
  - 正交 α：腿净收益对 510300 和 capacity_adv_hiliq 的回归截距。

| 腿 | 残差 IC(20d) / t_nw | 正交 α / t | 中性净（全/60万/100万） | ρ vs cap | 持有天数 | 单边换手/日 | 60万 cap→80/20 加权和 / 叠加 tilt |
|---|---|---|---|---|---|---|---|
| equity_incentive 202436 | +0.0093 / 3.88 | +17.5% / 2.24 | −6.7% / −4.1% / −8.9% | 0.42 | 25.9 | 3.0% | 30.9%→24.8% / 21.1% |
| earnings_event 202822 | +0.0061 / 2.04 | +12.1% / 1.63 | −6.6% / +9.1% / +0.1% | 0.51 | 19.3 | 4.2% | 30.9%→26.1% / 21.1% |
| insider_increase 202928 | +0.0040 / 1.95 | −4.7% / −0.68 | −18.6% / −30.9% / −17.8% | 0.09 | 8.8 | 9.0% | 30.9%→17.0% / 21.1% |
| insurer_surv 203108 | +0.0018 / 0.65 | +10.1% / 1.22 | −4.2% / −5.6% / −3.7% | 0.58 | 17.1 | 4.6% | 30.9%→23.1% / 21.1% |
| report_rc_allup 203201 | +0.0017 / 0.58 | +3.2% / 0.54 | −7.3% / −9.2% / −9.7% | 0.22 | 28.0 | 2.6% | 30.9%→22.3% / 21.1% |

结论（与 Alpha v3 一致）：五腿在任何一种口径下都没有全过；没有 RESEARCH_ACCEPT；不进 GATE_V3，不派 Eng，不进纸面。注：capacity_adv_hiliq 腿的 60万 Top-6 子集是等权并列下的任意子集（30.9%/MDD −38.1%），不作基准结论。

> **勘误 2026-10-18 01:03 ET（AI）**：本文 AI 风格的 ε 用了当日 logmv（含当日收益，与当日收益截面相关 0.93），所以 AI 风格下的中性化净超额全部作废。修正后（前一日 logmv），equity_incentive 全袖为 +8.80%（t 1.56），与 Alpha 冻结风格同号。正文「符号纯由风格集决定」的结论**撤回**。详见 AI_CAPADV_HILIQ_NEUTRAL_GAP_DIAG_ZH.md。
