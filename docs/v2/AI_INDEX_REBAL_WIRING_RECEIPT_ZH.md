# 指数调样叶接线回执（STOCK-INDEX-REBAL / V31）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 代号 | **STOCK-INDEX-REBAL** |
| sleeve | `stock_event_index_rebal` |
| promotion_approved | **false** |
| NAV / 回测 / 冒烟 / GP / v27 | **未跑**（仅接线脚手架） |
| Strategy | **不交** |
| Beta | 主跑**可用段**冒烟（2018-06+）；本侧只交叶定义与包 |

## 叶清单

| 叶 | 定义 |
|---|---|
| `idx_add_flag` | `event=in` ∧ `index_code∈{000300.SH,000905.SH}`；`available_at` 入日；多头候选 |
| `idx_del_flag` | `event=out` ∧ 同上；默认不持/低配，**不做空** |

## 宇宙 / 篮子

- 宇宙：事件涉及的 CSI300∪CSI500（中大盘）；滤 ST / 价&lt;2 / 停牌；**禁小盘**；**排除** 000852.SH
- 持仓：调入 top **N=25** 等权；**K=10**（锚 `effective_date`）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300

## available_at 规则（硬）

- `available_at.normalize()+1d` → `searchsorted(cal, left)`；下一开盘可交易
- 持有窗锚 `effective_date`；K=10 写死
- **不可前移** `available_at`；null `available_at` 行弃用（不回填）

## 覆盖（诚实，真实表计数）

| 窗 | 000300∪000905（avail 非空） |
|---|---|
| 标准 X1 2015-06→2017-12 | **0** → **coverage_blocked_x1** |
| 可用段 2018-06+ | **2180**（in 1090 / out 1090） |
| 表内 earliest `available_at` | 2018-05-25 20:00（审查历自 2018-06） |

勿伪造早年调样。冒烟在可用段报 coverage / avg_names。

## 路径

| 资源 | 路径 |
|---|---|
| 接线模块 | `research/ai_factor_index_rebal_panels.py` |
| 包目录 | `output/ai_factor/stock_index_rebal_v31/` |
| 信号包 | `…/alpha_signal_package.json` |
| JSON 回执 | `…/wiring_receipt.json` |
| BETA_NOTE | `…/BETA_NOTE_ZH.md` |
| README | `…/README_ZH.md` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V31_INDEX_REBAL_ZH.md` |
| 源表 | `data/v2/index_members/index_member_events.parquet` |
| 审查历 | `data/v2/index_members/csi_review_calendar.parquet` |

## 给 Beta 的入口

```text
from research.ai_factor_index_rebal_panels import (
    load_index_rebal_events,
    build_event_leaf_table,
    coverage_report,
    portfolio_rules,
    pit_rules,
)
events = load_index_rebal_events()          # 仅 000300/000905，drop null avail
adds   = build_event_leaf_table(events, event="in",  leaf_name="idx_add_flag")
dels   = build_event_leaf_table(events, event="out", leaf_name="idx_del_flag")
cov    = coverage_report(events)            # x1_events=0, available_segment_*
```

信号包字段见 `alpha_signal_package.json`（N/K/w_stock/ballast/y/禁项）。

## 禁项（本侧已遵守）

- 未开跑 NAV / 冒烟 / 回测；未写假 IC；未伪造 X1 事件
- 不交 Strategy；不启 v27
- 不磨 seat / 解禁 share_type / ETF tercile / 价叶 / 份额流 / LIMITUP
