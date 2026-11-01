# 研究级实时闭环 Dry-Run 命令（Eng · 不下单）

**日期**：2026-10-12（ET）  
**门控**：`promotion_approved` / `strategy_promotion_approved` **恒 false**（本页不改 `promotion_gate`）  
**禁止**：uvicorn / 实盘下单 / 重型 E1 全量对账 / 重物化 NAV（除非显式 `--book-nav`，且 live-dry-run 默认不开）

G1–G5 定义见 `TRADINGAGENTS_DEEP_READ_ZH.md` §6。

| Gate | 含义 | Eng 表面 | 状态 |
|---|---|---|---|
| **G1** | 分析师四报本地 PIT，拒 Yahoo | `asof_text_guard` + `intel.messages` + `assert_available_at_le_decision` | 接线真 / 内容 stub |
| **G2** | A 股情绪源；缺则 `coverage_gap` | `coverage_gap` + `withhold_live_only` | 缺口记账真；S1 主源未齐 |
| **G3** | Bull⇄Bear + RM → ledger | `JsonlDebateLedger` / `ai_debate_memory_runner --dry-run` | stub |
| **G4** | 风险三态 → PM | `trading_loop` 节点 `RISK_REVIEW`→`PM_GATE` | 图真 / 角色薄 stub |
| **G5** | 可配结算窗 + pending 至满窗；相对 510300 | `trading_loop.settle.compute_horizon_returns` | 逻辑真；缺行情可 mock |
| **weights** | 硬闸 → 权重长表 | `factor-evolve --smoke` + `weight_long_table` | 契约真 / 烟数据 stub |
| **smoke** | 主书接线 | `book-smoke` 默认 `--skip-run` | 接线真；默认不跑 NAV |

## 一键（推荐）

```bash
cd /workspace/QuantLab
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli live-dry-run
# 或
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.v2_live_dryrun
```

退出码 0 = G1–G5 表面检查 + factor_evolve 权重 + book-smoke `--skip-run` 全通。  
摘要：`output/v3/live_dryrun/live_dryrun_summary.json`

仅门检查（更轻）：

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -m quantlab.cli live-dry-run --gates-only
```

## 有序分项（无 glue 时也可手跑）

```bash
cd /workspace/QuantLab
export PYTHONPATH=.
PY=/workspace/qlvenv/bin/python

# G1–G3（辩论 + PIT 消息；可选，live-dry-run 已内嵌更轻检查）
$PY research/ai_debate_memory_runner.py --dry-run \
  --session 2024-05-31 --instrument 600519.SH

# G4（状态机含 RISK_REVIEW / PM_GATE）
$PY -m quantlab.cli trading-loop --session 2024-07-01 --instrument 510500.SH

# G5（结算；可选）
$PY -m quantlab.agents.trading_loop.settle_pending --help

# weights
$PY -m quantlab.cli factor-evolve --smoke

# smoke（默认 skip-run，不物化 NAV）
$PY -m quantlab.cli book-smoke

# 旧骨架一键（不含 G1–G5 门标签，仍可用）
$PY -m quantlab.cli skeleton-smoke
```

## 权重覆盖规则（与 Book-Smoke 解读）

**全日更长表须覆盖目标窗、禁止仅前推解读。**

- 引擎在最后一条权重之后会**持仓前推**；那不是「日更策略继续生效」的证据。
- 消费前可用：

```bash
PYTHONPATH=. /workspace/qlvenv/bin/python -c "
from quantlab.platform.weight_long_table import assert_session_coverage_path, schema_handshake
import json
print(json.dumps(schema_handshake()['coverage_rule_zh'], ensure_ascii=False))
# 例：核对是否盖住 X2 尾
# print(assert_session_coverage_path('path/to/weights.parquet', target_end='2026-10-09'))
"
```

## stub vs 真（本闭环）

| 组件 | 状态 |
|---|---|
| G1 asof / PIT 断言 / messages 读取 | **真接线**；Yahoo 路径不存在 |
| G2 S1 情绪主源 | **未齐**；coverage_gap / withhold **真** |
| G3/G4 辩论与风险角色 | **stub**（无 LLM） |
| G5 结算窗 | **真逻辑**；无行情时 mock 标源 |
| weight_long_table 契约 / 覆盖检查 | **真** |
| factor_evolve `--smoke` | **stub** 候选 |
| book-smoke `--skip-run` | **真接线**，不跑 NAV |
| 晋级 / 下单 / uvicorn | **关** |

## 相关

- `SKELETON_ONECLICK_ZH.md` · `TRADINGAGENTS_DEEP_READ_ZH.md` · `OPENSOURCE_ENG_ADOPTION_ZH.md`
- 开源只读：`/workspace/opensource/{TradingAgents,QuantMind}`
