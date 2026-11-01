# V3_LIMITUP_FADE_REV_PREREG — 涨停次日弱→反转（限价制度微观结构）

研究级，**promotion_approved=false**。写于 **2026-10-12 07:35 ET，运行前**。  
批次：`limitup_unlock_smoke`。主线：**个股+ETF**，非 MATPREM+GOLD 主书。残差/压舱 **510300**（非黄金/CB/国债主仓）。  
**勿磨** EVT-DT-INST-STOCK / EVT-ANN-POLARITY-STOCK。

## 独特收益来源（谁付钱）
A 股 **涨跌停制度**下，T 日触板后散户/游资继续追板；若 **T+1 开盘至收盘走弱**，追板盘在弱跟风中退出。本臂在确认「触板→次日弱」之后的下一开盘买入这些回落票，吃的是限价制度下的追逐失败溢价，**不是**教科书 120 日动量/反转截面。付钱的是：打板失败后割肉或被动承压的短线资金。

## ≠（禁近亲 / 禁误解）
| 臂/概念 | 差别 |
|---|---|
| 教科书 120d / 12-1 动量 | **本臂禁止**以中长期动量为主线；信号是 **单日涨停制度事件 + 次日弱确认** |
| EVT-DT-INST-STOCK（已 fail） | 龙虎机构净买选股 |
| IND-RATE / LPR / MATPREM / GOLD 压舱同族 | 已暂停；残差只用 510300（或液态行业 ETF，本版冻结 510300） |

## 股票池
- 主：沪深300 ∪ 中证500。`data/v2/index_members/index_weight_csi300_500_1000.parquet` 中 ≤t 最近快照（`index_code∈{000300.SH,000905.SH}`）。与 `run_stock_etf_smoke.py` 同法。
- **X1（权重表自 20180131）**：流通市值 PIT 当日截面 **top 800**（`float_mktcap_daily_from2015_tushare`）近似中大盘；**禁止** 小盘袖套。
- 过滤：ST（`st_intervals_tushare`）、收盘价 &lt;2、停牌不买。

## 冻结规则（写死，不搜索）
1. **触板日 T**：`close >= 0.998 * limit_up`（panel `limit_up`）；若缺 `limit_up`，则用 `(close/pre_close - 1) >= 9.5%` 代理（创业板/科创 20% 板用 `close >= 0.998 * limit_up` 优先，无 limit 则 `>= 19.5%`）。
2. **次日弱 T+1**：同一标的 `open→close` 收益 **&lt; 0**（冻结；不用分位搜索）。
3. **入场**：T+1 收盘后信息完备 → **T+2 开盘**可交易（`available_at` = T+1 15:00 Asia/Shanghai 之后下一开盘）。**不可前移**。
4. **持有期 HOLD=3** 个交易日（冻结于 [1,5] 内；不网格搜索）。
5. **组合**：每个交易日对仍在持有窗内的标的 **等权**；若当日活跃名 &gt; N=25，按 T+1 跌幅从大到小截 top 25；`w_stock = min(0.70, 0.028 * n)`；余 **510300**。n=0 → 100% 510300。
6. AUM **60万 / 100万**；禁小盘 / IC / CB / 国债 / 黄金主仓。

## 闸门
- HARD GATE：X1 Sharpe≤0 或 avg_names==0 → **fail_precheck**。
- Explore-pass：X2 CAGR≥12% 且 MDD≳−25%；报 vs IND-RATE-DIFF 与 vs MATPREM 日 ρ；|ρ|&gt;0.85 → near_relative，不交接。
- 仅 explore-pass 且非 near_relative 才写入 `handoff_strategy/`。`promotion_approved=false`。

## 产出
`output/v3/limitup_fade_rev/`；批次 json：`output/v3/pretest_batch_20261012_limitup_unlock.json`。
