# 叶自检 v2 回执（2026-10-14 ET；研究级，live=false，未跑 Book-Smoke，权重文件未改）
模块：research/leaf_selfcheck_common.py（evaluate(weights_path)）；回溯结果 output/ai_factory/leaf_selfcheck_v2_retro_20261014.json；peak RSS 850MB。

## 口径
- (a) 衰减门：直接调用 research/alpha_decay_gate.py evaluate_weights，常量未改（COST 0.00175、WIN 252、TO_MAX 0.20 等）。
- (b) 成本：双边日换手 TO=Σ|Δw|；净日收益 = 毛 − 0.00175×TO。成本来源：docs/v2/ALPHA_DECAY_GATE_PREREG_ZH.md（17.5bp/单位换手）；Strategy wf_screen 用 strategy_v1 近似 0.0016，量级一致。
  - **不可交易**（任一条）：① TO 均值 >20%/日（与衰减门 H1 同）；② 毛超额（vs 510300 hfq）>0 且年化成本拖累 > 毛超额的 50%；③ 毛超额 ≤0 且成本拖累 >1%/年。
- (c) 组合门（vs capacity_adv 单独；conc v2 topN，60万 N=6/100万 N=10，合并单名 ≤6%；复权、毛）：
  - 现行：cap80+叶20，两档 CAGR 更高且 MDD 不更深。
  - A：叶先去 β 再叠加（收益层估计）：r = 0.8·r_cap + 0.2·(r_510300 + r_叶 − β·r_510300)，两档 CAGR 更高且 MDD 不更深。β 为全样本（样本内）。
  - B：原样叠加（同现行组合），两档 Calmar 更高且 MDD ≥ −15%。

## 回溯（2024-01→2026-10-09）
| 叶 | 衰减门 | TO 双边/日 | 毛 CAGR | 净 CAGR | 成本拖累/年 | 毛超额 | 可交易 | 现行 | A | B |
|---|---|---|---|---|---|---|---|---|---|---|
| report_rc_allup | KEEP | 2.09% | 16.65% | 15.58% | 0.92% | +4.31% | 是 | ✗ | ✗ | ✗ |
| analyst_recoverage | DECAY_DOWNGRADE（α<0、TO>20%、净≤510300） | 63.3% | 13.80% | **−13.93%** | 27.9% | +1.46% | **不可交易** | ✗ | ✗ | ✗ |
| stk_surv | DECAY_DOWNGRADE（α<0、净≤510300） | 1.52% | 12.05% | 11.30% | 0.67% | −0.29% | 是 | ✗ | ✗ | ✗ |
| capacity_adv（参照） | KEEP | 2.50% | 17.66% | 16.37% | 1.10% | +5.32% | 是 | — | — | — |

组合门细节（CAGR / MDD / Calmar）：
| 叶 | 档 | cap 单独 | 原样叠加 | A 去β叠加 |
|---|---|---|---|---|
| report_rc_allup | 60万 | 15.11/−13.65/1.108 | 15.56/−14.14/1.101 | 15.44/−14.38/1.073 |
| | 100万 | 18.85/−12.25/1.538 | 20.40/−12.41/1.643 | 18.46/−13.27/1.390 |
| analyst_recoverage | 60万 | 同上 | 12.90/−15.52/0.831 | 14.94/−13.23/1.129 |
| | 100万 | 同上 | 19.62/−12.70/1.546 | 17.94/−12.11/1.482 |
| stk_surv | 60万 | 同上 | 15.32/−13.86/1.105 | 14.69/−14.62/1.004 |
| | 100万 | 同上 | 19.25/−12.47/1.543 | 17.67/−13.51/1.308 |
- report_rc_allup 的 B 门：100万过，60万 Calmar 1.101<1.108 未过 → 两档不同时过。
- 结论与原判定一致：三叶均不过任何组合门；analyst_recoverage 另被成本门判不可交易。
- 注：cap 单独 60万 15.11% 与叶11 回执 14.96% 的差异来自日期对齐（本模块用衰减门的取价与日历）。

## 接入
新叶脚本在写完权重后调用 `from research.leaf_selfcheck_common import evaluate; meta["selfcheck_v2"] = evaluate(wpath)`；单独运行：`python3 research/leaf_selfcheck_common.py <weights.parquet>`。
