# 个股中大盘事件袖套提案：STOCK-DIV-IMP（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-DIV-IMP** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转；**不磨** seat / 解禁窗·share_type / ETF tercile / 价叶(ind_ret/ind_excess/bm_ret) / 份额流 / LIMITUP 近亲 / CB / 金叶 / overnight* / ind_rel_overnight / 教科书质量应计(ocf/accrual/roa 主攻) |

## 0. 维选择说明（相对拒稿与备选）

- V32 **STOCK-OCF-QUALITY** 已拒：ocf_to_profit 属 crowding 教材应计/质量，禁主攻。
- 优先核「**异动/异常波动公告**」：`announcements_classified_pit` 标题含「异动|异常波动」共 10109 条，**ann_date 最早 2018-01-02** → **X1(2015-06→2017-12)=0**；cninfo 抽样同结论。**异动实施短窗 X1 coverage_blocked**，勿伪造。
- 换维至 V32 纸面备选、且 New Bot 点名的 **「分红实施短窗」**：非公开教材常驻因子，而是 A 股公司行动日历上的 **实施公告→除权短窗** 制度事件流。

## 1. 机制一句 + 谁付钱

现金分红 **实施公告**（`imp_ann_date`，缺则 `ann_date`）入日后，至除权/派息前后短窗，中大盘上有强制公司行动与持仓再配置；抢跑/接盘吃事件流与流动性摩擦。臂：在实施公告入日后持 **有现金实施的中大盘个股篮**，残差 **510300**。付钱：被除权日历与被动/基准约束驱动的再平衡；对手方是事件敏感的短线与制度跟踪资金。**不是**常驻股息率（DY）截面因子。

## 2. 叶 / 规则 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | `div_imp_cash_flag`：`div_proc` 含「实施」且 `cash_div>0`；PIT 锚 `imp_ann_date`（空则 `ann_date`）→ 当日 23:59 Asia/Shanghai 口径 / **下一开盘**可交易；可选对照叶 `div_imp_yield_xsec`（实施窗内 cash/价 截面，仅敏感性，**非主仓常驻 DY**） |
| sleeve | `stock_event_div_imp` |
| 宇宙 | CSI300∪CSI500；X1 缺权用 float **top800**；**禁小盘**；滤 ST / 价&lt;2 / 停牌 |
| PIT | 表 `data/v2/corporate_actions/dividend_tushare.parquet`；**不可前移**；不以 `ex_date` 倒推可用日 |
| 持仓 | 入日事件名 top **N=25** 等权（同日过多则按 `cash_div` 或流通市值优先）；**K=10**（实施公告入日后 10 交易日，写死；可批后敏感性±5，不在批前扫）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300 |
| y | 持有期 **fwd excess vs 510300**（实施公告事件驱动个股篮；**非**月频行业 ETF tercile / **非**常驻 DY） |
| 硬禁 | 小盘 / CB / 金主仓；行业 ETF 时序 tercile；价叶 / 份额流；龙虎 seat；unlock/share_type；LIMITUP；overnight*；ocf/accrual/roa 教材质量主攻；异动标题叶（X1=0 勿硬接） |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| STOCK-OCF-QUALITY（已拒） | 财报 ocf_to_profit 质量 | **分红实施公司行动窗**；非应计教材 |
| 常驻股息率 / 价值因子 | 月频 DY 截面 | **仅**实施公告后 K 日事件窗；去掉入日塌成常驻 DY → **自拒** |
| UNLOCK / SEAT / INDEX-REBAL | 解禁 / 席位 / 指数调样 | **分红实施**；非解禁、非 seat、非调样 |
| 异动/问询/增减持 classified | 表自 2018，X1=0 | **不用**；已换维 |
| ETF tercile / 价叶·份额流（已停） | SW L1 → 行业 ETF | **持液态个股篮**；残差 510300 |

一句话：持**个股中大盘篮**，信号是现金分红 **实施公告** 后的短持有窗，不是 seat、不是解禁、不是 ETF tercile、不是 ocf 质量、不是异动标题（X1 无覆盖）。

## 4. 失败条件（可证伪）

1. **去掉「实施入日事件窗」**改常驻月频 DY 排序后得分同构 / 增量消失 → 无事件维 → **自拒**。
2. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
3. PIT 违规（用未到实施公告日的行 / 用 `ex_date` 前移可用）→ fail / 停跑。
4. 与裸 DY 或行业 `ind_ret` |ρ| 过高，或塌成价叶/动量同构 → reject。
5. 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP·份额流·ocf 教材主攻 → reject。

## 5. 冒烟口径 + X1 覆盖（真实计数）

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；K=10 写死。
- `promotion=false`；**不交 Strategy**；不启 v27。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**。

### X1 覆盖证据（禁止伪造）

| 源 | 窗 | 事件数 / 说明 |
|---|---|---|
| **`data/v2/corporate_actions/dividend_tushare.parquet`**（主） | **X1 2015-06-01→2017-12-31**，`div_proc`含实施 ∧ `cash_div>0`，PIT=`imp_ann_date`填充`ann_date` | **5884** 行；**2713** 只；unique(ts_code,end_date)≈5695；pit **2015-06-01→2017-12-26**；几乎皆有 `ex_date`/`record_date` |
| 同上，按 `ann_date` | X1 实施 cash&gt;0 | **5014** / 2655 只（与 V32 备选口径一致） |
| 异动/异常波动标题（classified） | X1 | **0**（ann 自 2018-01-02；共 10109 条在 2018+）→ **不采用** |
| `insider_increase/decrease` / `inquiry_letter` / buyback | X1 | **0**（表自 2018-01-02） |
| `suspend_d` | X1 | **0**（raw 自 2018-01-02） |
| `index_member_events` 000300/000905 | X1 | **0**（V31 已标；本臂不依赖） |
| `ocf_to_profit` | X1 有数 | **硬禁主攻**（V32 已拒 crowding 教材） |
| seat / unlock / 份额流·tercile / 价叶 | X1 有数 | **硬禁** |

**结论：完整 X1 有事件覆盖成立**（分红实施主源非零）；异动维 X1=0 已换维。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/corporate_actions/dividend_tushare.parquet` | **齐**：`div_proc`/`cash_div`/`imp_ann_date`/`ann_date`/`ex_date`/`record_date` |
| `float_mktcap_daily_from2015_tushare` | X1 宇宙 top800 回退 |
| seat / unlock / ETF tercile / 价叶 / 份额流 / LIMITUP / overnight / ocf 主攻 | **硬禁** |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。V31 STOCK-INDEX-REBAL 可用段继续，本页不触碰。**
