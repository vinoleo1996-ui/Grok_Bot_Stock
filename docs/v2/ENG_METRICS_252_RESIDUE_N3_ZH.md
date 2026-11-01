# Eng｜Arch N3 P2：252 年化残留清理回执（2026-10-14）

live=false；promotion=false；未改纸面 FROZEN / capacity_adv 产出；未动 `alpha_decay_gate` 预注册锁定的 WIN=252 窗与 α×252。

## 口径
- 唯一来源：`quantlab/metrics.py`，`PERIODS=244`（A 股）。
- 纸面 / scorecard 此前已走该模块；本次清研究与 report 路径残留。

## 已改
| 文件 | 改动 |
|---|---|
| `quantlab/report/metrics.py` | `TRADING_DAYS=PERIODS(244)`；`ann_*`/`sharpe`/`beta_alpha`/`performance_table` 默认 244；字段 `annual_return_sessions`（244）+ `annual_return_252_legacy`（对照）；不再以 252 为主报 |
| `research/leaf_selfcheck_v3.py:107` | `held_minus_pool_ann`：`*252/h` → `*244/h`（与同行 CAGR/Sharpe 244 一致） |
| `quantlab/comparison.py` | 超额/选择分年化 `*PERIODS` |
| `quantlab/pipeline.py` | OOS/随机试验超额年化 `*PERIODS` |
| `quantlab/report/attribution.py` | 诊断超额年化 `*PERIODS`（顺手） |
| `quantlab/report/research_diagnostics.py` | 双边换手年化 `*PERIODS`（顺手） |

## 未改（有意）
- `research/alpha_decay_gate.py`：WIN=252、α×252 预注册锁定。
- 纸面轨 / FROZEN_CONFIG / capacity_adv 产出。
- `quantlab/webapp/app.py`（自算年化仍 252）、`quantlab/beta/sleeve.py`（波动年化 252）— 非本次清单，记后续。

## 调用方影响
- `performance_table` 调用方（pipeline/comparison/cli/webapp/html 等）继续用同一 API；主字段 `annual_return`（自然日 CAGR）未变；`sharpe`/`annual_vol`/`alpha_ann` 现按 244。
- 旧键 `annual_return_252` 已更名为 `annual_return_252_legacy`；仓库内无 Python 读取该键。HTML 记分卡用的是 `annual_return`，不受影响。
- 本机缺 `scipy`，无法整包 import comparison/pipeline 做端到端跑；已 `ast.parse` + `performance_table` 单测自检通过。未跑全量回测。

## 结论
Arch N3 P2 清单内残留已清；与纸面 244 口径对齐。遗留 webapp/beta 两处可开下一轮。
