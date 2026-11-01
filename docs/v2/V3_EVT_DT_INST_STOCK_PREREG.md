# V3_EVT_DT_INST_STOCK_PREREG — 龙虎机构净买 → 中大盘个股袖套
研究级，**promotion_approved=false**。写于 **2026-10-12 07:24 ET，运行前**。
批次：`stock_etf_smoke`。主线：**个股+ETF**，非 MATPREM+GOLD 主书。残差/压舱 **510300**（非黄金主仓）。

## 独特收益来源（谁付钱）
龙虎榜披露后，游资/散户追「机构席位净买」热票；本臂在 **conservative available_at（T+1 15:00）之后下一开盘** 买机构净买强度靠前的中大盘，吃的是披露后追逐盘的过度支付与随后均值回归/信息扩散价差。付钱的是：按龙虎打印追单的游资与散户。

## ≠（禁近亲）
| 臂 | 差别 |
|---|---|
| DT-INST-BREADTH（已 fail） | 机构广度→**加仓 510300**（择时宽基） |
| **本臂 EVT-DT-INST-STOCK** | 机构净买强度→**持中大盘个股篮**；残差 510300 |
| CB/利率/黄金压舱同族 | 已暂停，不碰 |

## 股票池
- 主：沪深300 ∪ 中证500。`index_weight_csi300_500_1000.parquet` 中 ≤t 最近月末快照（`index_code∈{000300.SH,000905.SH}`）。
- **X1（权重表自 20180131）**：用流通市值 PIT 当日截面 **top 800**（`float_mktcap_daily_from2015_tushare`）近似中大盘；文档化；**禁止** 3001–5000 小盘袖套。
- 过滤：ST（`st_intervals_tushare` 覆盖当日）、收盘价 &lt;2（若可得）、停牌不买。

## 规则
- 数据：`top_inst_labeled.parquet`（`is_institution` / `seat_type=institution`，`net_buy`）；金额用 `top_list.amount`。
- PIT：`available_at_alpha_conservative` = T+1 15:00 Asia/Shanghai → **下一交易日开盘**可交易（≈T+2 open）。**不可前移**。
- 信号：universe ∩ 机构席位 `net_buy>0`；得分 = `Σ net_buy / amount`（无 amount 则用 Σ net_buy）；周度调仓取上次调仓后新可用事件。
- 持仓：top **N=25** 等权；权重和 `w_stock=min(0.70, 0.028*n)`；余 **510300**。若 n=0 → 100% 510300。
- AUM 60万/100万；禁小盘/IC/CB/国债/黄金主仓。

## 闸门
X1 Sharpe≤0 或 avg_names==0 → fail_precheck。Explore-pass：X2 CAGR≥12% 且 MDD≳−25%。报 vs IND-RATE-DIFF 与 vs MATPREM 日 ρ；|ρ|&gt;0.85 → near_relative，不交接。仅 pass 且非 near_relative 才 `handoff_strategy/`。
