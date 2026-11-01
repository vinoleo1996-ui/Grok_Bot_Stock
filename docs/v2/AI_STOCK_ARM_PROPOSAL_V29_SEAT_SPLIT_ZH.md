# 个股中大盘事件袖套提案：STOCK-SEAT-SPLIT（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **STOCK-SEAT-SPLIT** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |
| 不开 | v27 / 同叶 GP 空转 |

## 1. 机制一句 + 谁付钱

已接线席位叶上，**机构净买相对强、游资/散户席位净买相对弱或负**（`dt_inst_net_*` vs `dt_retail_hot_net_*` 分歧）筛选中大盘；可选与新鲜 `ann_earn|buyback` 或 `lu_streak` 做确认交叉（非单独 lu 反转）。吃的是「追游资热票、忽略机构/游资席位分裂」的短线过度支付；付钱方：按龙虎打印追游资热票的散户与通道资金。

## 2. 叶 / 标签 / 袖套

| 项 | 草案 |
|---|---|
| 信号叶 | 主：`dt_inst_net_5|10`、`dt_retail_hot_net_5|10`（分歧分 = z(inst) − z(retail)，retail≤0 或相对弱为加分）；辅确认（可选、非单独）：`ann_earn`/`ann_buyback` 新鲜窗，或 `lu_streak≥1` |
| sleeve | `stock_event_seat_split` |
| 宇宙 | CSI300∪CSI500；X1 权重缺失段用 float **top800** 近似中大盘；**禁小盘**；滤 ST / 价&lt;2 / 停牌 |
| PIT | `available_at_alpha_conservative`（≈T+1 15:00 SH）→ **T+2 开盘**（与 `AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md` 一致；**不可前移**） |
| 持仓 | top **N=25** 等权；`w_stock=min(0.70, 0.028*n)`；余 **510300**；n=0 → 100% 510300 |
| y | 持有期 **fwd excess vs 510300**（周度再平衡；取上次调仓后新可用席位事件） |
| 硬禁 | 小盘 / CB / 金主仓；行业 ETF 时序 tercile；份额流 / 价叶 |

## 3. ≠ 对照表

| 对照 | 对方 | 本臂 |
|---|---|---|
| EVT-DT-INST-STOCK（已有 prereg） | **仅**机构净买强度 → 中大盘篮 | **机构 vs 游资/散户席位分歧**；去掉 retail 腿即塌成对方 → 自拒 |
| LIMITUP-FADE-REV（fail_precheck） | 触板 T → T+1 弱 → T+2 买该票 HOLD=3 | 席位分裂选股；lu 仅可选确认，**非**触板次日弱反转 |
| ETF-DT-SEAT（已停/纸拒） | seat → SW L1 → **行业 ETF** 月频 tercile | **持液态个股篮**；残差 510300；非行业 ETF 时序 |
| EVT-ANN-POLARITY-STOCK | 粗公告极性合并多头（X1 coverage 问题） | 主信号是席位分歧；ann 仅可选确认交叉，非极性主轴 |

一句话：持**个股中大盘篮**，信号是**席位分裂**（非单腿机构、非 lu 反转、非 ETF 时序、非粗公告极性）。

## 4. 失败条件（可证伪，≥4）

1. **去掉 retail 腿**后得分排序与 EVT-DT-INST-STOCK 同构 / 增量消失 → 无新信息维 → **自拒**。
2. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
3. PIT 违规（用当日未披露席位 / 前移 `available_at`）→ fail / 停跑。
4. 与行业 ETF 时序得分（ETF-DT-SEAT / ind_ret 映射）|ρ| 过高 → 说明做错袖套（应是个股事件，不是行业 ETF）→ reject。
5. （附加）可选确认交叉去掉后仍无席位分歧增量，或 nonempty 过稀致日均名≈0 → fail / 不升 research_observe。

## 5. 冒烟口径

- 资本 **60万∧100万** 同权表；成本 **25bp**；只认 PIT；周度再平衡。
- 禁小盘 / CB / 金；`promotion=false`；**不交 Strategy**；不启 v27。
- X1 Sharpe≤0 | avg_names=0 → **fail_precheck**，不开 X2。
- 通过门槛（一句话）：X1 Sharpe>0 ∧ avg_names>0，且去掉 retail 腿后仍有增量、非 ETF 时序近亲，才可谈 `research_observe`。

## 6. 数据（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/dragon_tiger/top_inst_labeled.parquet` | **齐**（`seat_type` 含 institution / retail_or_hot_money） |
| `research/ai_factor_dt_seat_panels.py` → `dt_inst_net_*` / `dt_retail_hot_net_*` 等 | **已接线**（见 `AI_DT_SEAT_LEAVES_WIRING_RECEIPT_ZH.md`；nonempty 稀，覆盖闸如实） |
| 工厂 `ann_earn`/`ann_buyback`、`lu_streak` | **齐**（仅可选确认；非主轴） |
| ETF-DT-SEAT / 价叶 / 份额流 / LU-BREADTH 行业 ETF 模板 | **硬禁**（非本臂变体） |

**明确：等 New Bot 书面批准本提案后再冒烟；本稿不开跑、不启 v27、不交 Strategy。**
