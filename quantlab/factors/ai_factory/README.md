# AI Factor Factory L1（骨架）

对齐：`/workspace/QuantLab-AI_FACTOR_MINING_PLAN_ZH.md`  
预注册：`docs/prereg/AI_FACTOR_L1.md`

## 本周 KPI
管线通、`output/ai_factor/ledger.jsonl` 计次、Top-K 表达式写出——不是再报公开策略年化。

## 模块
| 路径 | 方案角色 |
|---|---|
| `quantlab/factors/ops.py` | E3 算子库 |
| `quantlab/factors/ai_factory/search.py` | B1 GP |
| `quantlab/factors/ai_factory/ledger.py` | E2 搜索账本 |
| `quantlab/factors/ai_factory/evaluate.py` | 标签对齐 / 折内 IC 桩 |

## 约束
`promotion_approved=false`；禁小盘主线；挖因子不加杠杆；密封窗 2018-01～2024-05 仅 Leo 批准后单次；V3-A1 密封仍等 Leo，本工厂不触发。

```bash
python -m pytest tests/test_ai_factor_factory_smoke.py -q
```


## L1c 开源闭环（2026-10-11）
| 路径 | 角色 |
|---|---|
| `quantmind_loop.py` | QuantMind 五段：preflight→evolve→backtest→explain→export |
| `asof_text_guard.py` | TradingAgents 式文本 PIT |
| `structural_leaves.py` | easy-stock 连板/题材结构叶 |
| CLI | `research/quantmind_min_loop.py --smoke` |

本金元数据：`capital_cny ∈ {600000,1000000}`。禁教科书主结果；禁密封自开。
