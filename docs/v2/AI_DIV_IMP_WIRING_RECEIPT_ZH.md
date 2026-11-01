# 分红实施短窗叶接线回执（STOCK-DIV-IMP / V33）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 代号 | **STOCK-DIV-IMP** |
| sleeve | `stock_event_div_imp` |
| promotion_approved | **false** |
| NAV / 回测 / 冒烟 / GP / v27 | **未跑**（仅接线脚手架） |
| Strategy | **不交** |
| Beta | 主跑**完整 X1**；本侧只交叶定义与包 |
| V31 | **未触碰** |

## 叶清单

| 叶 | 定义 |
|---|---|
| `div_imp_cash_flag` | `div_proc`含「实施」∧ `cash_div>0`；PIT=`imp_ann_date`∪`ann_date`；排除停止实施；**主仓**事件旗 |
| `div_imp_yield_xsec` | 实施窗内 cash/价 截面（敏感性对照；**非**主仓常驻 DY） |

## 宇宙 / 篮子

- 宇宙：CSI300∪CSI500（中大盘）；X1 缺权用 float **top800**；滤 ST / 价&lt;2 / 停牌；**禁小盘**
- 持仓：入日事件名 top **N=25** 等权（同日过多按 `cash_div` 或流通市值优先）；**K=10**（实施公告入日后 10 交易日，写死）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300

## PIT 规则（硬）

- `pit = coalesce(imp_ann_date, ann_date)`；Asia/Shanghai 当日 23:59 口径 → **下一开盘**可交易
- 持有窗锚 pit 入日；K=10 写死（批后敏感性 ±5，不在批前扫）
- **不可前移**；**不以 `ex_date` 倒推可用日**；null pit 行弃用
- 排除 `div_proc` 含「停止实施」

## 覆盖（诚实，真实表计数）

| 窗 | 实施 ∧ cash_div>0（PIT=imp∪ann） |
|---|---|
| 标准 X1 2015-06→2017-12 | **5884** 行 / **2713** 只 / unique(ts_code,end_date)≈**5695** → **coverage_ok**（非 blocked） |
| 同上按 `ann_date` | **5014** / 2655 只 |
| pit 窗 | 2015-06-01 → 2017-12-26；几乎皆有 `ex_date`/`record_date` |
| 异动/问询/增减持 classified X1 | **0**（自 2018）→ **不采用** |

勿伪造 IC。冒烟在完整 X1 报 coverage / avg_names。

## 路径

| 资源 | 路径 |
|---|---|
| 接线模块 | `research/ai_factor_div_imp_panels.py` |
| 包目录 | `output/ai_factor/stock_div_imp_v33/` |
| 信号包 | `…/alpha_signal_package.json` |
| JSON 回执 | `…/wiring_receipt.json` |
| BETA_NOTE | `…/BETA_NOTE_ZH.md` |
| README | `…/README_ZH.md` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V33_DIV_IMP_ZH.md` |
| 源表 | `data/v2/corporate_actions/dividend_tushare.parquet` |
| float 回退 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` |

## 给 Beta 的入口

```text
from research.ai_factor_div_imp_panels import (
    load_div_imp_events,
    build_event_leaf_table,
    select_names_for_day,
    coverage_report,
    portfolio_rules,
    pit_rules,
)
events = load_div_imp_events()   # 实施∧cash>0；PIT=imp∪ann；drop 停止实施
flag   = build_event_leaf_table(events, leaf_name="div_imp_cash_flag")
sens   = build_event_leaf_table(events, leaf_name="div_imp_yield_xsec")
cov    = coverage_report(events)  # x1_events=5884, coverage_blocked_x1=False
# 同日 top N：select_names_for_day(day_events, n=25, float_mktcap=...)
```

信号包字段见 `alpha_signal_package.json`（N/K/w_stock/ballast/y/禁项）。

## 禁项（本侧已遵守）

- 未开跑 NAV / 冒烟 / 回测；未写假 IC；未伪造 X1 事件
- 不交 Strategy；不启 v27
- 不磨 seat / 解禁 share_type / ETF tercile / 价叶 / 份额流 / LIMITUP / ocf 教材主攻
- **未触碰** V31 `stock_index_rebal_v31` 包
