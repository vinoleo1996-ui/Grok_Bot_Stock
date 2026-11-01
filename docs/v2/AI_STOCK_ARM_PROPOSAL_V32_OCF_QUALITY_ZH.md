# 个股中大盘事件袖套提案：STOCK-OCF-QUALITY（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-OCF-QUALITY** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转；**不磨** seat / 解禁窗·share_type / ETF tercile / 价叶(ind_ret/ind_excess/bm_ret) / 份额流 / LIMITUP 近亲 / CB / 金叶 / overnight* / ind_rel_overnight |

## 1. 机制一句 + 谁付钱

财报 `available_at` 后短窗，中大盘上 **经营现金流/净利润（ocf_to_profit）** 相对同宇宙偏高的名字，应计溢价被质量敏感资金上修；偏低（应计厚）的名字被兑现/回避。臂：在财报入日后持 **高 ocf_to_profit** 中大盘篮，残差 **510300**。付钱：追会计利润、忽略现金转化的短线与被动再平衡；对手方是质量筛查资金。

## 2. 叶 / 规则 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | `ocf_quality_xsec`：报告期版本表 `ocf_to_profit`（`n_cashflow_act/n_income`）在 `available_at` 入日后做中大盘截面 z/rank；滤 `denom_small`；`np_negative` 默认剔除或单独对照叶 `ocf_quality_npneg_flag`（非主仓） |
| sleeve | `stock_event_ocf_quality` |
| 宇宙 | CSI300∪CSI500；X1 缺权用 float **top800**；**禁小盘**；滤 ST / 价&lt;2 / 停牌 |
| PIT | 表内 `available_at`（CF 与利润两侧较晚公告 18:00 Asia/Shanghai）→ **下一开盘**；持有窗锚入日；**不可前移**；重述行按新 `available_at` 再入，不回改历史 |
| 持仓 | 高分 top **N=25** 等权；**K=15**（财报入日后 15 交易日，写死；可批后敏感性±5，不在批前扫）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300 |
| y | 持有期 **fwd excess vs 510300**（财报入日事件驱动个股篮；**非**月频行业 ETF tercile / 非裸 EP 因子） |
| 硬禁 | 小盘 / CB / 金主仓；行业 ETF 时序 tercile；价叶 / 份额流；龙虎 seat；unlock/share_type；LIMITUP；overnight* |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| EVT-ANN-POLARITY-STOCK（X1 blocked） | 分类公告极性（回购/增持/预增） | **现金流质量**（ocf/利润）；源是 financials_pit，不是 ann 分类表 |
| 裸 EP / 价值因子 | 水平 EP 截面常驻 | **事件窗**：仅 `available_at` 后 K 日；去掉「入日事件」塌成常驻应计 → **自拒** |
| UNLOCK / SEAT / INDEX-REBAL | 解禁 / 席位 / 指数调样 | **财报现金转化**；非解禁、非 seat、非调样 |
| ETF tercile / 价叶·份额流（已停） | SW L1 → 行业 ETF | **持液态个股篮**；残差 510300 |

一句话：持**个股中大盘篮**，信号是财报入日后的 **ocf_to_profit 截面质量**，不是 seat、不是解禁、不是 ETF tercile、不是公告问询。

## 4. 失败条件（可证伪）

1. **去掉「入日事件窗」**改常驻月频 ocf 排序后得分同构 / 增量消失 → 无事件维 → **自拒**。
2. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
3. PIT 违规（用未到 `available_at` 的报告 / 前移 ann）→ fail / 停跑。
4. 与裸 EP 或行业 `ind_ret` |ρ| 过高，或塌成价叶/动量同构 → reject。
5. 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP·份额流 → reject。

## 5. 冒烟口径 + X1 覆盖（真实计数）

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；K=15 写死。
- `promotion=false`；**不交 Strategy**；不启 v27。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**。

### X1 覆盖证据（禁止伪造）

| 源 | 窗 | 事件数 / 说明 |
|---|---|---|
| **`data/v2/financials_pit/ocf_to_profit_pit_tushare.parquet`**（主） | **X1 2015-06-01→2017-12-31**（`available_at`） | **38090** 行；**4336** 只；finite ocf **37632**；unique(ts_code,end_date)≈38083；avail 2015-06-05→2017-12-30 |
| 同表全史 | 报告期 2014-03-31→2026-09-30 | 228450 行 / 5867 只（Data 验收 PASS） |
| `announcements_classified_pit` inquiry_letter/reply | X1 | **0**（表自 2018-01-01）→ **换维**（本臂不用 inquiry） |
| `index_member_events` 000300/000905 | X1 | **0**（V31 已标 coverage_blocked；本臂不依赖） |
| `share_float_pit` 解禁 | X1 有数 | **硬禁**（unlock/share_type 不磨） |
| `dragon_tiger` seat | X1 有数 | **硬禁**（seat 不磨） |
| `etf_share_flow_pit_*` | X1 有数 | **硬禁**（份额流 / tercile 不磨） |
| `disclosure_date` 预约披露 | X1 | **0**（自 2018） |
| `dividend_tushare` 实施 cash&gt;0 | X1 ann | 5014 / 2655 只（备选，本页不主推） |

**结论：完整 X1 有事件覆盖成立**（ocf 主源非零）；inquiry 同 blocked → 已换维至财报现金质量。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/financials_pit/ocf_to_profit_pit_tushare.parquet` | **齐**：`ocf_to_profit` / `available_at` / `denom_small` / `np_negative`；PIT 验收 PASS |
| `float_mktcap_daily_from2015_tushare` | X1 宇宙 top800 回退 |
| seat / unlock / ETF tercile / 价叶 / 份额流 / LIMITUP / overnight | **硬禁** |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。**

---

**备选（本页不主推）**：分红实施公告短窗（X1 实施 cash&gt;0≈5014）——若本臂纸拒可再提；仍须避开已禁维。
