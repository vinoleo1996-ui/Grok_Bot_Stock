# 个股中大盘事件袖套提案：STOCK-DISC-EARLY（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-DISC-EARLY** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转；**不磨** 分红/DY / ocf·应计·质量教材 / seat / 解禁窗·share_type / ETF tercile / 价叶(ind_ret/ind_excess/bm_ret) / 份额流 / LIMITUP 近亲 / CB·金 / overnight* / ind_rel_overnight / V31 指数调样同构 |

## 0. 维选择说明（相对拒稿与优先候选）

- V33 **STOCK-DIV-IMP** 已拒：Beta D1/D2 fail；self_reject（月频 DY≥事件窗）。**勿磨分红/DY 同构**（含送转实施近亲）。
- V32 **STOCK-OCF-QUALITY** 已拒：教材应计/质量主攻禁。
- 优先核候选（真实计数，禁止伪造）：
  - **增减持/回购/问询 classified**：`announcements_classified_pit` ann 自 **2018-01-01** → **X1=0**
  - **异动/异常波动标题**：同表自 2018 → **X1=0**
  - **停复牌** `suspend_d` raw：自 **20180102** → **X1=0**
  - **大宗交易折溢价**：盘内 **无稳 PIT 表**（V26 备忘已标「暂不列为可跑」；`smallcap_info` 大宗未落地）
  - ST 摘帽 / 审计非标：X1 有数但中大盘 top800 仅约 **13** 名 → 稀疏勿硬推
- 换维至 **A 股定期报告披露制度日历**：同报告期截面上 **早于同伴披露** 的入日短窗（非利润/现金流质量因子、非常驻基本面排序）。

## 1. 机制一句 + 谁付钱

定期报告有法定/交易所披露截止与同伴簇拥披露窗。中大盘里 **同一 `end_date` 下 `available_at` 早于截面中位** 的名字，率先进入基本面桌与主动再定价；晚披露同伴与被动/宽基在季报季仍按旧信息或月末再平衡。臂：在早披露入日后短窗持 **早披露中大盘篮**，残差 **510300**。付钱：信息处理滞后的晚读方与报告季被迫再平衡的被动流。**不是** ocf/应计/ROA 质量截面，也不是 PEAD 用盈余幅度打分。

## 2. 叶 / 规则 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | `disc_early_flag`：每个 `(instrument_id,end_date)` 取 **首次** `available_at`；在入日当日中大盘宇宙内，相对 **同 `end_date` 同伴** `available_at` 中位数，`aa < median` → 早披露；可选对照叶 `disc_late_flag`（仅敏感性，非主仓） |
| sleeve | `stock_event_disc_early` |
| 宇宙 | CSI300∪CSI500；X1 缺权用 float **top800**；**禁小盘**；滤 ST / 价&lt;2 / 停牌 |
| PIT | `data/v2/financials_pit/financials_available_at_tushare.parquet` 的 `available_at`（报告日 18:00 Asia/Shanghai 口径）→ **下一开盘**；**不可前移**；重述行按新 `available_at` 再判，不回改历史首次入日 |
| 持仓 | 早披露事件名 top **N=25** 等权（同日过多则按流通市值优先）；**K=10**（入日后 10 交易日，写死；可批后敏感性±5，不在批前扫）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300 |
| y | 持有期 **fwd excess vs 510300**（披露日历事件驱动个股篮；**非**月频质量因子 / **非**行业 ETF tercile） |
| 硬禁 | 小盘 / CB / 金主仓；ocf/accrual/roa 教材质量主攻；分红/DY/送转实施同构；seat；unlock/share_type；ETF tercile / 价叶 / 份额流；LIMITUP；overnight*；V31 调样同构调参 |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| STOCK-DIV-IMP（已拒） | 现金分红实施窗 → 易塌 DY | **披露早晚日历**；无股息率 |
| STOCK-OCF-QUALITY（已拒） | ocf_to_profit 质量截面 | **不读**现金流/应计字段；只比 `available_at` 早晚 |
| PEAD / 盈余动量教材 | 用盈余惊喜幅度打分 | **幅度叶禁用**；去掉「早于中位」只持全部已披露 → 须自拒 |
| UNLOCK / SEAT / INDEX-REBAL | 解禁 / 席位 / 调样 | **定期报告披露制度**；非解禁、非 seat、非调样 |
| 增减持/大宗/停复牌/异动 | X1=0 或无 PIT | **不用**；已换维 |

一句话：持**个股中大盘篮**，信号是定期报告 **早于同伴披露** 的入日短窗，不是 seat、不是解禁、不是分红/DY、不是 ocf 质量、不是 ETF tercile。

## 4. 失败条件（可证伪）

1. **去掉「早于中位」**、改为持有窗内**全部已披露**中大盘后得分同构 / 增量消失 → 无早披露维 → **自拒**。
2. 用盈余 YoY / ocf_to_profit / 应计打分替代早晚旗后得分同构 → 塌成教材质量/PEAD → **自拒**。
3. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
4. PIT 违规（用未到 `available_at` 的行 / 前移）→ fail / 停跑。
5. 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP·分红·份额流·价叶 → reject。

## 5. 冒烟口径 + X1 覆盖（真实计数）

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；K=10 写死。
- `promotion=false`；**不交 Strategy**；不启 v27；**不触碰 V31**（仍 research_observe）。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**。

### X1 覆盖证据（禁止伪造）

| 源 | 窗 | 事件数 / 说明 |
|---|---|---|
| **`financials_available_at_tushare` 首次披露**（主） | **X1 2015-06-01→2017-12-31**，SH/SZ，每 `(id,end_date)` 首次 `available_at` | **39373** 行 / **4279** 只；aa **2015-06-01→2017-12-30** |
| 同上 ∩ float **top800**（lookback≤3 日历日对齐） | X1 | **8195** 行 / **1254** 只 |
| 同上且 **`aa < 同 end_date 中位`**（早披露叶） | X1 中大盘 | **3664** 行 / **1057** 只；覆盖 **18** 个 end_date 簇 |
| `announcements_classified_pit` 增减持/回购/问询/异动 | X1 | **0**（ann 自 2018-01-01） |
| `suspend_d` | X1 | **0**（raw 自 20180102） |
| 大宗 PIT | — | **无稳表**；不采用 |
| ST 摘帽 / 审计非标 | X1∩top800 | 各约 **13** 名 → 稀疏不主推 |
| `dividend` 实施 cash / 送转 | X1 有数 | **硬禁**（V33 后勿磨分红/DY 同构） |
| `ocf_to_profit` / seat / unlock / 份额流·tercile / 价叶 | X1 有数 | **硬禁** |
| `index_member_events` | X1 | **0**（V31 已标；本臂不依赖、不触碰） |

**结论：完整 X1 有事件覆盖成立**（早披露主源非零）；增减持/大宗/停复牌/异动 X1 缺口已换维。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/financials_pit/financials_available_at_tushare.parquet` | **齐**：`available_at` / `end_date` / `instrument_id` |
| `float_mktcap_daily_from2015_tushare` | X1 宇宙 top800 回退 |
| 分红 / ocf / seat / unlock / ETF tercile / 价叶 / 份额流 / LIMITUP / overnight / V31 调参 | **硬禁** |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。V31 STOCK-INDEX-REBAL 仍仅 research_observe，本页不触碰。**
