# 定期报告早披露短窗叶接线回执（STOCK-DISC-EARLY / V34）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 代号 | **STOCK-DISC-EARLY** |
| sleeve | `stock_event_disc_early` |
| promotion_approved | **false** |
| NAV / 回测 / 冒烟 / GP / v27 | **未跑**（仅接线脚手架） |
| Strategy | **不交** |
| Beta | 主跑**完整 X1**；本侧只交叶定义与包 |
| V31 | **未触碰** |

## 叶清单

| 叶 | 定义 |
|---|---|
| `disc_early_flag` | 每个 `(instrument_id,end_date)` **首次** `available_at`；入日当日中大盘宇宙内，相对 **同 `end_date` 同伴** `available_at` 中位数，`aa < median` → 早披露；**主仓**事件旗 |
| `disc_late_flag` | 同 end_date 同伴 `aa ≥ median`；敏感性对照；**非**主仓 |

## 宇宙 / 篮子

- 宇宙：CSI300∪CSI500（中大盘）；X1 缺权用 float **top800**（lookback≤3 日历日对齐）；滤 ST / 价&lt;2 / 停牌；**禁小盘**
- 持仓：入日早披露事件名 top **N=25** 等权（同日过多按流通市值优先）；**K=10**（披露入日后 10 交易日，写死）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300

## PIT 规则（硬）

- 源：`data/v2/financials_pit/financials_available_at_tushare.parquet` 的 `available_at`（报告日 18:00 Asia/Shanghai）
- 每个 `(instrument_id, end_date)` 取 **首次** `available_at` → normalize → **下一开盘**可交易
- 持有窗锚 pit 入日；K=10 写死（批后敏感性 ±5，不在批前扫）
- **不可前移**；重述行按新 `available_at` 再判，**不回改**历史首次入日
- 早披露判定：`aa < 同 end_date 中大盘（top800）同伴中位`
- null pit 行弃用

## 覆盖（诚实，真实表计数）

| 窗 | 计数 |
|---|---|
| X1 2015-06→2017-12 首次披露 SH/SZ | **39373** 行 / **4279** 只；aa 2015-06-01→2017-12-30 |
| 同上 ∩ float **top800**（lookback≤3） | **8195** 行 / **1254** 只 |
| 同上且 **`aa < 同 end_date 中位`**（早披露叶） | **3664** 行 / **1057** 只；覆盖 **18** 个 end_date 簇 → **coverage_ok**（非 blocked） |
| 增减持/回购/问询/异动 classified X1 | **0**（自 2018）→ **不采用** |
| 停复牌 / 大宗 PIT | X1=0 / 无稳表 → **不采用** |
| 分红实施 / ocf / seat / unlock / tercile / 价叶 | 有数但 **硬禁**（已拒维勿磨） |

勿伪造 IC。冒烟在完整 X1 报 coverage / avg_names。

## 路径

| 资源 | 路径 |
|---|---|
| 接线模块 | `research/ai_factor_disc_early_panels.py` |
| 包目录 | `output/ai_factor/stock_disc_early_v34/` |
| 信号包 | `…/alpha_signal_package.json` |
| JSON 回执 | `…/wiring_receipt.json` |
| BETA_NOTE | `…/BETA_NOTE_ZH.md` |
| README | `…/README_ZH.md` |
| 提案 | `docs/v2/AI_STOCK_ARM_PROPOSAL_V34_DISC_EARLY_ZH.md` |
| 源表 | `data/v2/financials_pit/financials_available_at_tushare.parquet` |
| float 回退 | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` |

## 给 Beta 的入口

```text
from research.ai_factor_disc_early_panels import (
    load_disc_early_events,
    build_event_leaf_table,
    select_names_for_day,
    coverage_report,
    portfolio_rules,
    pit_rules,
)
events = load_disc_early_events()   # 中大盘首次披露 + early/late 旗；PIT=available_at
flag   = build_event_leaf_table(events, leaf_name="disc_early_flag")
sens   = build_event_leaf_table(events, leaf_name="disc_late_flag")
cov    = coverage_report()  # x1_early_events=3664, x1_early_stocks=1057, coverage_blocked_x1=False
# 同日 top N：select_names_for_day(day_events, n=25, float_mktcap=...)
```

信号包字段见 `alpha_signal_package.json`（N/K/w_stock/ballast/y/禁项）。

## 禁项（本侧已遵守）

- 未开跑 NAV / 冒烟 / 回测；未写假 IC；未伪造 X1 事件
- 不交 Strategy；不启 v27
- 不磨 seat / 解禁 share_type / ETF tercile / 价叶 / 份额流 / LIMITUP / ocf 教材主攻 / 分红·DY 同构
- **未触碰** V31 `stock_index_rebal_v31` 包
