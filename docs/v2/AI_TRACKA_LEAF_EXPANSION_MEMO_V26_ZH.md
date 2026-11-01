# TrackA 扩叶备忘（破 v26 新颖性墙）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 对照轮次 | v26 TrackA DONE（GATE_OK=0） |
| promotion_approved | **false** |
| 不交 | Strategy |
| TrackB | 同叶族（份额流 / 价叶 REL-MOM·PXVOL）**继续停** |

目的：列**缺哪些 PIT 新叶**才能破新颖性墙；**勿空跑**同叶集。本文不启动 GP/回测。

---

## 1. 现状（v26）

- **GATE_OK=0**；novelty 杀约 **115**；同叶饱和（New Bot 已核）。
- 种子仍偏 **lu / dt / unlock / ann_earn|buyback** 交叉，骨架近亲多；闸内弱 ICIR 勿指望事后抬升。
- SEARCH 已排除 `ind_rel_intraday` 同构模板；硬禁 `overnight*` / `fsr*` / `ann_insider*` / `idx_w*` 及若干 ACTIVE 近亲（ACTIVE 仍 **v2f_v24=24+8**）。
- 结论：**再开 v27 同叶 GP = 空跑**；须先接线新信息维叶子。

---

## 2. 已有但薄的叶（不够破墙）

| 叶族 | 现状 | 为何不够 |
|---|---|---|
| `dt_net_5/10`、`dt_flag_5` | 工厂已粗聚合净买/上榜旗 | **无 seat_type 分裂**；与已搜骨架同信息面，只换窗仍 novelty 杀 |
| `nb_north_money` | 市场层 moneyflow_hsgt 汇总 | **无个股截面**；再交叉易成市场体制近亲（参见 NB-MARGIN-DIV fail） |
| `ann_*` 粗极性 | 回购/业绩等粗桶 | 与 ACCEPT/已搜 ann_earn\|buyback 近亲；细类未进工厂则仍同叶 |
| `unlock_resid` | 解禁残差粗叶 | holder_type 未细拆时增量有限 |
| lu / ld 族 | 涨跌停相关 | v26 种子已偏此族，同骨架饱和 |

---

## 3. 优先要的 PIT 新叶清单

| 叶名草案 | 机制 | 数据源 path | available_at 规则 | 覆盖缺口 | 立刻接线？ |
|---|---|---|---|---|---|
| **`dt_inst_net_*` / `dt_nb_channel_net_*` / `dt_retail_hot_net_*`** | 按 `seat_type` 拆净买强度（非换窗） | `data/v2/dragon_tiger/top_inst_labeled.parquet`（20150105→20261009；seat_type 四类齐） | trade_date **18:00 SH**；保守 T+1 15:00 → 交易 T+2 开；**不可前移** | 无日期洞（见 `DRAGON_TIGER_COVERAGE.md`） | **是（最高优先）** |
| **`dt_inst_breadth`**（个股侧日广度/占比） | 机构席位净买>0 的广度；相对笼统 dt_net 新维 | 同上 | 同上 | 同上 | **是** |
| **`dt_reason_*`（粗分）** | reason 涨偏/跌偏/换手/振幅等粗桶（字段可用，文案多需规则归一） | `top_inst_labeled` / `top_list` 的 `reason`（nunique 数百，须规则桶） | 同上 | 规则未定则暂缓进 SEARCH | **可接线（次于 seat 拆）** |
| 个股北向持仓Δ / 占比 | 截面北向变化，非市场汇总 | `data/v2/northbound/hk_hold_ashare_daily_2018plus.parquet`（列含 vol/ratio） | trade_date 18:00 SH（见 `HK_HOLD_COVERAGE_GAP.md`） | **日频 A 股约至 20240626；2024-08 后官方停日频披露**，仅季末等稀疏点 | **条件接线**：接受「日频至~2024-08 + 季末」或标样本截断；**不可假装全日频到 2026** |
| `hsgt_top10_*` 续期 | 北向当日买卖额 Top10 结构 | `data/v2/northbound/hsgt_top10_daily_2018plus.parquet` | 表内 available_at；不可前移 | **仅 20180102→20211208**；其后未续 | **BLOCKED**（无续期源前勿开 GP 依赖） |
| 市场层 `nb_north_money` 再交叉 | — | `moneyflow_hsgt_daily_*` | 18:00 SH | 工厂已有；再搜易饱和/近亲 | **不推荐**作破墙主叶 |
| `ann_inquiry_*` / `ann_penalty_case_*` 等细类 | 问询回复/立案 vs 粗 polarity | `data/v2/events/announcements_classified_pit.parquet`（rules_v1 已含问询/处罚等） | 有时钟用时钟；否则 ann_date 23:59 SH → 最早 T+1 开 | 高峰日 5000 截断等（见 `EVENT_FLOW_DATA_STATUS.md`） | **次优先**（避已 ACCEPT penalty 近亲） |
| `unlock_holder_*` | 解禁 holder_type 细化 | share_float 相关表（部分可用；以现网 path 为准） | 以既有 unlock PIT 为准 | 覆盖以 EVENT_FLOW / 解禁文档为准 | **可选次优先** |
| 大宗 PIT | 折溢价/定向 | 若有则再评估 | — | 无稳 PIT 则跳过 | **暂不列为可跑** |

---

## 4. 建议顺序

1. **先接龙虎 seat 细化叶**（Data 已齐：`top_inst_labeled` + seat_type）→ 进工厂后再谈 TrackA 下一轮 SEARCH。  
2. **再评估个股北向**：仅在接受 hk_hold 日频截断（~2024-08）或季末稀疏的前提下；否则标局限，勿当全日频。  
3. **hsgt_top10 续期**：仅在有 2022+ 源并落盘后；当前 **BLOCKED**。  
4. **在新叶未接线前：禁止再开 v27 同叶 GP。**

---

## 5. 结尾约束

- `promotion_approved=false`；**不交 Strategy**。  
- TrackB 份额流 / 价叶同叶族 **继续停**。  
- 等 **New Bot / Data 确认接线** 后再谈 TrackA 下一轮；本稿不空跑、不调参。
