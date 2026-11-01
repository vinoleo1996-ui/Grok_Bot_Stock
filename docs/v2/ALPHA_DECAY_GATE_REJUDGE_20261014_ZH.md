# 叶 α 衰减闸门 v1 全台账重判（2026-10-14，研究级）
- 预注册：docs/v2/ALPHA_DECAY_GATE_PREREG_ZH.md，**FROZEN 2026-10-14 05:46:20 ET，sha256 eecc84ba7774939e19a9428f578aec2a72711a6021d4eb6192301ed5be34c13b**（另存 output/alpha/ALPHA_DECAY_GATE_PREREG.sha256.json）。冻结后才写实现、才计算。
- 实现 research/alpha_decay_gate.py；运行器 output/alpha/decay_gate_rejudge_20261014.py；明细 output/alpha/ALPHA_DECAY_GATE_REJUDGE_20261014.json。
- 冻结后唯一改动：实现 bug（numpy datetime64 无 .date()）修正一次，发生在读任何结果之前（首跑全部报错未出数）；规则与参数未动。
- **尝试数**：规则集 1 套，调参 0 次；评估 24 叶，7 项 INSUFFICIENT（无权重文件：expand/lowturn/nontextbook/g1g5_base/x2 三项）。
- 不自动改 capacity_adv 纸面状态与 B4；B4 v1 未计算。live=false；promotion_approved=false；禁 GP。

## 规则摘要
净日收益 = 复权毛收益 − 17.5bp×双边换手；对 510300 OLS 的残差 α，最近 252 日滚动（只用过去）；季末取点（2024Q4 起）+ 最新日。
DECAY_DOWNGRADE：最新 α<0，或季度 α 连降 3 次，或 H1 平均双边换手>20%，或 H2 近 252 日净 CAGR ≤ 510300 买入持有净 CAGR。DECAY_WATCH：最新 α∈[0,1%) 或连降 2 次。否则 KEEP。只降不升；纸面轨只 flag 给 Leo。

## 结果（评估日≈2026-10-09/13；近 252 日 510300 净 CAGR −3.48%）
| 叶 | 现有裁定 | 最新滚动 α | 连降 | 双边换手 | 近1年净 CAGR | 衰减闸 | 动作 |
|---|---|---|---|---|---|---|---|
| **capacity_adv**（纸面 r2） | PAPER_ACTIVE_CONFIRMED | +2.84% | 0 | 3.0% | +1.37% | **KEEP** | 无（不 flag） |
| **earnings_event** | BOOK_SMOKE_PASS/RC | +3.15% | 0 | 2.8% | −0.98% | **KEEP** | 无 |
| **insider_increase** | BOOK_SMOKE_PASS/RC | +11.12% | 0 | 3.5% | +9.12% | **KEEP** | 无 |
| **equity_incentive** | BOOK_SMOKE_PASS/RC | +5.64% | 0 | 2.3% | +2.26% | **KEEP** | 无 |
| report_rc_allup | WATCH | +7.82% | 0 | 2.7% | +4.27% | KEEP | 无（不上调） |
| idx_rebal_predict | WATCH | +2.98% | 0 | 2.5% | −0.86% | KEEP | 无 |
| interim_div_init | WATCH | +1.48% | 0 | 3.8% | −1.75% | KEEP | 无 |
| idx_rebal_flow / indcap / negevent / northbound | DONE_FAIL | +9.27/+1.63/+1.32/+1.16% | 0 | — | — | KEEP | 无 |
| d1_val_resid | DONE_FAIL | +0.25% | 0 | 1.1% | −1.76% | DECAY_WATCH | 无 |
| etf_rotation | REJECT | +0.10% | 0 | 11.0% | −1.88% | DECAY_WATCH | 无 |
| block_trade | WATCH | −0.54% | 2 | 1.0% | −3.85% | DECAY_DOWNGRADE | 已是 WATCH |
| buyback_cancel | WATCH | −2.08% | 1 | 1.0% | −5.01% | DECAY_DOWNGRADE | 已是 WATCH |
| unlock_rebound | WATCH | −4.91% | **5** | 1.2% | −7.68% | DECAY_DOWNGRADE | 已是 WATCH |
| analyst_recoverage | WATCH | −31.3% | 0 | **59.8%** | −29.5% | DECAY_DOWNGRADE | 已是 WATCH |
| stk_surv（叶13） | WATCH | −1.63% | 1 | 2.1% | −4.17% | DECAY_DOWNGRADE | 已是 WATCH |
| accrual_quality / etf_core_sleeve / friction / margin_delta / moneyflow_resid / resid_etf | DONE_FAIL | 均 <0 | — | — | — | DECAY_DOWNGRADE | 不变 |

**结论：本次无任何标签被改动。** 三个 RESEARCH_CANDIDATE 叶与 capacity_adv 主干均 KEEP；被降级的全是已 WATCH/DONE_FAIL 的叶。

## 注意
1. 近 252 日窗口（≈2025-10→2026-10）510300 为负，H2 门相对宽松；earnings_event 净 CAGR 为负但仍胜基准。
2. capacity_adv 滚动 α 在 2026-06-30 曾为 −6.52%、2025-09-30 −0.64%，当前回到 +2.84%：若下季转负将触发 flag_for_leo（不自动改纸面）。
3. 权重文件按预注册取最新时间戳：earnings_event、insider_increase 用 111825 版、equity_incentive 用 135031 版（延至 10-13），与 ACCEPT 当时文件不同版本；残差只对 510300 单因子，未做行业/市值残差。
4. analyst_recoverage 的极端负值来自约 60% 双边日换手的成本，与叶12 已知结论一致。

## QuantLab AI 接入规格
```python
from research.alpha_decay_gate import evaluate_weights, evaluate_returns
r = evaluate_weights("output/ai_factory/<leaf>_daily_weights_<ts>.parquet")
# -> {outcome: KEEP|DECAY_WATCH|DECAY_DOWNGRADE|INSUFFICIENT, reasons:[...], latest_resid_alpha, consecutive_declines,
#     quarterly_alpha:[[date,alpha],...], turnover_mean_2s, net_cagr, bench_net_cagr, beta, window, prereg_sha256}
# 已有日收益时：evaluate_returns(gross: pd.Series, turnover: pd.Series)  # 双边换手，日期索引
```
CLI：`python3 research/alpha_decay_gate.py <weights.parquet>` 输出 JSON。AI 在自检回执中贴 outcome/reasons 即可；常量（252、N=3、20%、17.5bp、1%）不得在调用侧改，改动须走 v2 预注册。
