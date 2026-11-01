# Beta B1：幸存者偏差检查（capacity_adv / B4 宇宙）（live=false，promotion_approved=false）

更新：2026-10-14 ET · **v1.1 更正**（回应 Arch S4：`docs/v2/audit/ARCH_SURVIVORSHIP_AUDIT_20261014_ZH.md`）

> **更正声明（v1.1）**：v1.0 曾写「幸存者偏差估计为 0 / ≈0」。该表述过度推广。本版收窄为：**纸面 mid_large 持仓路径≈0**；全场（FULLA / IC / 引擎 / 主日线）**不能**采信为零。Arch 专项审计为权威补充。

## 数据
Data 已有退市历史：`data/v2/ref/stock_delisted.parquet`（339 只，含 delist_date / last_trade_date / 退市原因 / 退市价）和 `data/v2/meta/stock_basic_incl_delisted.parquet`（L 5573 / D 339）。**B1 纸面路径检查不被阻塞。**
X2 窗口内（2024-06-03→2026-10-09）退市 **93 只**：强制退市且退市前 1 年内为 ST 的 44 只；进入退市整理期的 41 只；疑似吸收合并或私有化的 8 只。

## 宇宙构建方式
capacity_adv、earnings_event、insider_increase 都调用 `select_mid_large_topn_light`：取 `data/v2/universe/mid_large_members_pit.parquet` 在 **2024-06-28（PIT 锚点）** 的成员，按流通市值降序，保留有 D0 panel 的前 N 只（capacity_adv 用 N=50，事件腿用 top300）。之后每次调仓还会按 PIT 成员资格过滤。

## 检查结果（仅纸面 mid_large）
- 锚点当天的 mid_large 共 2481 只，**只有 1 只缺 panel，前 100 名里没有缺的**，所以不存在「后来退市→没有 panel→被剔除」的路径。
- 在 X2 内退市、且在锚点时属于 mid_large 的有 10 只，最靠前的排名是 **85（601989 中国重工，吸收合并）**，其次是 136（600837 海通证券，吸收合并）。其余 8 只排名都在 551 之后。
- capacity_adv 的 top50 **不含任何 X2 内退市股**。
- 事件腿的 top300 包含上面这 2 只合并退市股，但四个 BOOK（capacity_adv 43 只、earnings 78 只、insider 102 只、B4 143 只）的 target_weights 里**一次都没持有过退市股**。这 2 只属于换股合并，退市本身不是亏损事件。
- X2 期间曾进入 mid_large PIT 的退市股共 17 只，全部不在 top50 宇宙里。
- Arch smoke 交叉确认：纸面 capacity_adv 正权重 ∩ 退市 = 0（`output/loop/audit_smokes/survivorship_20261014.json`）。

## 结论（收窄后）
- **纸面 mid_large 持仓路径 ≈ 0**：X2 内 capacity_adv / B4 等纸面轨未持有退市股；宇宙为锚点时点 PIT，不依赖「今天仍上市」。
- **不是全场结论。** 不得写成「幸存者偏差估计为 0」或「系统无幸存者偏差」。

## 未覆盖项（Arch 审计点名；本检查未量化）
| 缺口 | 为何「持仓=0」推不出「偏差=0」 | Arch 编号 |
|---|---|---|
| **FULLA / all_a 研究掩码** | 历史日明确包含后来退市股；事件腿 FULLA 曾正权重持有退市股（在 last_trade 前卖出） | S4 / §2.1 |
| **IC / leaf_selfcheck 标签丢弃** | `ok=f.notna()` 会丢掉无远期价格的票；退市附近 forward return → NaN → 截面被清洗 | S2 |
| **引擎个股退市清算** | `execution.py:645` 无 terminal_price；退市后 ffill 估值、收益≈0，而非 −50%/−100% | S1 |
| **主日线缺口** | `tushare_raw/daily` 对部分仍应交易的后来退市股缺 bar；`delisted_daily` 未并入主路径 | S3 |
| D0 panel 退市覆盖 | 退市股 81/334 无 panel；扩池/早年锚可能 `skipped_no_panel` | S6 |
| 退市整理期 / 吸收合并换股 | 未建模 | S7 |

## 残留风险（非「持仓路径≈0」所能覆盖）
- 宇宙在 2024-06-28 固定、只取大盘股，退市风险本来就低——这是选样结果，不是偏差为零的证明。扩到 FULLA / 小盘后必须重做。
- 回测引擎在退市日怎么处理（missing_bar_ret≈0、按最后价格清算）**尚未验证**；目前纸面未持有退市股，所以暂时不触发，FULLA 研究轨会触发。
- 宇宙固定在一个锚点，会漏掉后来新进入的股票（另一类偏差，未量化）。
- **FULLA β / 风格暴露重估**：在 FULLA 纸面 NAV 产出之前**阻塞**，不得用 mid_large 纸面数字外推。

引用：`docs/v2/audit/ARCH_SURVIVORSHIP_AUDIT_20261014_ZH.md`（Arch，2026-10-14）。冻结后改动联签提案见 `BETA_BUDGET_MDD25_FOR_COMBO_ZH.md` 附录。

live=false；promotion_approved=false。
