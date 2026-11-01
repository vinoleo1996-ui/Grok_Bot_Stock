# 个股中大盘事件袖套提案：STOCK-INDEX-REBAL（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-INDEX-REBAL** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转；**不磨** 价叶/份额流/ETF tercile、seat 分歧、unlock/share_type、LIMITUP-FADE |

## 1. 机制一句 + 谁付钱

CSI300/CSI500 **成分调入/调出**公告后、生效日前后，指数基金与量化对标有**强制买卖**；抢跑与接盘短线吃被动流。付钱：被动指数跟踪的强制再平衡需求。臂：持**中大盘个股篮**（调入多头；调出默认低配/不持，**不做空**）。

## 2. 叶 / 规则 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | `idx_add_flag` / `idx_del_flag`：按表内 `available_at` 入日；`event=in`→add，`event=out`→del；**仅** `index_code∈{000300.SH,000905.SH}`（CSI300∪CSI500；**排除** 000852.SH/CSI1000） |
| sleeve | `stock_event_index_rebal` |
| 宇宙 | 事件涉及的 CSI300∪CSI500 成分（本就中大盘）；滤 ST / 价&lt;2 / 停牌；**禁小盘** |
| PIT | 表内 `available_at` → **下一开盘**；持有窗锚 `effective_date`；**不可前移** |
| 持仓 | 调入多头 top **N=25** 等权；**K=10**（公告后至 effective 后 10 交易日，写死）；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300；调出默认不持（不做空） |
| y | 持有期 **fwd excess vs 510300**（事件驱动个股篮；**非**月频行业 ETF tercile） |
| 硬禁 | 小盘 / CB / 金主仓；行业 ETF 时序 tercile；价叶 / 份额流；龙虎 seat；unlock/share_type 解禁窗；LIMITUP-FADE |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| UNLOCK / SHARETYPE（Beta reject） | 解禁窗 / `share_type` 构成 | **指数调样** in/out；非解禁 |
| STOCK-SEAT-SPLIT（Beta reject） | 机构 vs 游资席位分歧 | **无 seat**；信号是成分事件 |
| ETF-DT-SEAT / LU-BREADTH / 价叶·份额流（已停） | SW L1 → **行业 ETF** tercile | **持液态个股篮**；残差 510300 |
| ANN-POLARITY / 动量 | 公告情绪 / 价动量 | 被动调样强制流；非情绪、非动量 |

一句话：持**个股中大盘篮**，信号是 CSI300/500 **成分调入**事件（被动强制买卖），不是 seat、不是解禁、不是 ETF tercile。

## 4. 失败条件（可证伪）

1. **无调样增量**：同日随机抽样同 N 名表现 ≥ 本臂 → 无事件 alpha → **自拒**。
2. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
3. PIT 违规（用未到 `available_at` 的行 / 前移 ann）→ fail / 停跑。
4. 与行业收益 `ind_ret` |ρ| 过高，或塌成动量/价叶同构 → reject。
5. 做成行业 ETF tercile / 引入 seat·解禁·LIMITUP → reject。

## 5. 冒烟口径 + X1 覆盖（诚实）

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；K=10 写死。
- `promotion=false`；**不交 Strategy**；不启 v27。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**。
- **X1 覆盖风险（必读）**：`index_member_events.parquet` 的 `available_at` **最早约 2018-05-25**（审查历自 2018-06）；**X1 窗 2015-06→2017-12 事件数 = 0** → 标准 X1 **coverage_blocked**，**勿伪造**早年调样。冒烟须在 **2018-06 起可用段** 报 coverage / avg_names；若规程仍强制完整 X1 → 标 `coverage_blocked` 并纸拒，不开假回填。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/index_members/index_member_events.parquet` | **齐**：`event` in/out；`available_at` / `effective_date` / `ann_date`；`index_code`∈{000300,000905,000852}；**PIT 可用段 ≈2018-05-25→2026-05-29**（null `available_at` 106 行弃用） |
| `data/v2/index_members/csi_review_calendar.parquet` | 17 次审查（2018-06→2026-06）对齐 |
| seat / unlock / ETF tercile / 价叶 / 份额流 / LIMITUP | **硬禁** |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。**

---

**备选队列（本页不主推）**：ann `inquiry_letter` / `reply`（主表约至 ~20240531，post-202406 须核；2018+ 或有样本，但 **X1 同样可能 coverage_blocked**）——本页主推 **STOCK-INDEX-REBAL**。
