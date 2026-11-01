# V3_MARGIN_PX_DIV_PREREG — 两融余额加速 vs 股价背离 → 中大盘择时
研究级，**promotion_approved=false**。写于 **2026-10-12 05:55 ET，运行前**。
批次：`smoke_evtflow_indetf`。压舱 **511880**（非 GOLD）。

## 独特收益来源（谁付钱）
两融余额 20 日变化率与 510300 同期收益的**背离**刻画脆弱杠杆：余额加速抬升而股价走弱 = 加杠杆接飞刀，随后强制平仓链条付钱；余额减速而股价修复 = 去杠杆出清后的风险溢价回收。付钱的是：顺周期加杠杆的融资客与其强平对手方冲击的被动持有者。

## ≠
| 臂 | 信号 |
|---|---|
| **MARGIN-DELTA**（已 fail_precheck） | 仅 `rzrqye` Δ20 z→削仓 |
| **本臂 MARGIN-PX-DIV** | Δ20 z **且** 与 510300 的 20 日收益符号背离才加减仓 |
| CALL-HEAT / IND-RATE | 非 CB 热度、非份额流 |

## 规则
- 数据：`margin_exchange_daily_merged.parquet`（= `margin_exchange_2014_2017` ∪ `margin_exchange_daily_2018plus`；2014–17 `available_at` backfill=下一交易日 09:00 Asia/Shanghai，`promotion_approved=false`）；沪深合计 `rzrqye`；**保守 T+1**（as-filed 若=T 日傍晚则 shift 下一交易日开盘）。
- `d20=pct_change(20)`；`mz=expanding_z(d20, min=40)`；`px20=510300 后复权 20 日收益`。
- 脆弱：`mz>0 ∧ px20≤0` → w_eq=0.20；健康：`mz<0 ∧ px20>0` → w_eq=0.50；其余 0.35；余 **511880**。
- 月度调仓；AUM 60/100万；禁小盘/IC。

## 闸门
同 hub：X1 Sharpe>0 且信号存活；X2 CAGR≥12%、MDD≲25%。报 vs IND-RATE-DIFF 日相关。
