# 个股中大盘事件袖套提案：STOCK-UNLOCK-SHARETYPE（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-UNLOCK-SHARETYPE** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转；**不磨** seat 分歧 / 单腿机构 / ETF tercile |

## 1. 机制一句 + 谁付钱

中大盘上，**定增股份**（及「非战略配售 / 非股权激励」大块解禁）在 `available_at` 后、`float_date` 窗内的抛压更偏**财务投资者退出**；相对「首发战略配售 / 股权激励限售」解禁，卖盘动机不同。臂：在解禁窗按 `share_type` 构成筛「定增（及同类）占比/规模高」的中大盘，吃被迫减持流动性折价。付钱：定增接盘方退出与抢解禁窗口的短线。

## 2. 叶 / 标签 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | 主：`unlock_private_place_ratio_20`（窗内定增股份 `float_share` / 总解禁量）、`unlock_private_place_size_20`；对照叶：`unlock_incentive_ratio_20`、`unlock_strategic_ipo_ratio_20`（战略配售）；可选：`unlock_non_strategic_block_ratio_20`（定增+公开增发+首发原始股大块 − 激励 − 战略配售）。**主信号 = share_type 构成，非粗残差** |
| sleeve | `stock_event_unlock_sharetype` |
| 宇宙 | CSI300∪CSI500；X1 权重缺失段用 float **top800**；**禁小盘**；滤 ST / 价&lt;2 / 停牌 |
| PIT | 表内 `available_at`（=`ann_date` 18:00 Asia/Shanghai，`availability_basis=ann_date_18:00_Asia/Shanghai`）→ **下一开盘**；浮窗锚 **`float_date`**；**不可前移** |
| 持仓 | top **N=25** 等权；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300 |
| y | 持有期 **fwd excess vs 510300**（解禁窗事件驱动；非月频 ETF 时序） |
| 硬禁 | 小盘 / CB / 金主仓；行业 ETF 时序 tercile；价叶 / 份额流；龙虎 seat |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| **UNLOCK-WINDOW-RESID**（fail_precheck） | 仅「解禁前 20D 相对 510300 残差&lt;0」；**无 `share_type`**；按 `(ts_code,float_date)` 粗聚合 | 主信号是 **share_type 构成**（定增占比/规模高）；去掉 type 分裂即塌成粗解禁 → **自拒** |
| STOCK-SEAT-SPLIT（Beta reject） | 机构 vs 游资席位分歧 | **解禁 share_type**；禁 seat 再切 / 单腿机构同构 |
| LIMITUP-FADE-REV（fail_precheck） | 触板次日弱反转 | 解禁 type 选股；非 lu 反转 |
| ETF-DT-SEAT / LU-BREADTH / 价叶·份额流（已停） | SW L1 → **行业 ETF** tercile / 价·份额流 | **持液态个股篮**；残差 510300；非 ETF 时序 |

一句话：持**个股中大盘篮**，信号是解禁窗 **`share_type` 构成**（定增抛压 vs 战略/激励），不是粗残差、不是 seat、不是 ETF tercile。

## 4. 失败条件（可证伪，≥4）

1. **去掉 share_type 分裂**后得分与 UNLOCK-WINDOW-RESID 同构 / 增量消失 → 无新信息维 → **自拒**。
2. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
3. PIT 违规（用未到 `available_at` 的解禁行 / 前移 ann）→ fail / 停跑。
4. 主仓滑向小盘 / CB / 金，或做成行业 ETF 时序 tercile → reject。
5. （附加）定增叶 nonempty 过稀致日均名≈0，或与粗 `float_ratio` 单叶 |ρ| 过高说明 type 未提供增量 → fail / 不升 research_observe。

## 5. 冒烟口径

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；事件窗锚定 `float_date`。
- 禁小盘 / CB / 金 / ETF 时序 / seat；`promotion=false`；**不交 Strategy**；不启 v27。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**，不开 X2。
- 通过门槛（一句话）：X1 Sharpe>0 ∧ avg_names>0，且去掉 type 后仍有相对粗解禁的增量，才可谈 `research_observe`。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/share_float/share_float_pit.parquet` | **齐**：`float_date` **20150105→20261030**；列含 `share_type` / `holder_name` / `available_at` / `float_share` / `float_ratio`；观测 type：首发战略配售股份、首发原始股、**定增股份**、股权激励限售流通、公开增发一般股份等 |
| UNLOCK-WINDOW-RESID 粗残差规则 | **已 fail_precheck**（对照基线；本臂不得复用其「仅残差&lt;0」主轴） |
| 龙虎 seat / 行业 ETF tercile / 价叶 / 份额流 | **硬禁**（非本臂变体） |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。**

---

**备选队列（本页不主推）**：ann 细类（`inquiry_letter` / `reply` 等）与 `hsgt_top10` 续满后北向结构；本页主推 **share_type**。
