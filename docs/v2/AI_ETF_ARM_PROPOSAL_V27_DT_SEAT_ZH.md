# ETF 新臂提案：ETF-DT-SEAT（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **ETF-DT-SEAT** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |

## 1. 机制一句

个股龙虎席位按 `seat_type` 净买在申万一级截面聚合，映射到液态行业 ETF；吃的是「机构/通道席位已铺开、游资散户仍按热票追」的行业级滞后扩散，付钱的是按龙虎打印追单的游资与散户（非 ETF 自身申赎或价量）。

## 2. 叶 / 标签

| 项 | 草案 |
|---|---|
| 叶子 | `dt_inst_net_sw_5`、`dt_retail_net_sw_5`、`dt_nb_channel_net_sw_5`、`dt_inst_breadth_sw`（SW L1 日聚合后再滚动；窗名可微调，语义不变） |
| sleeve | `etf_timing_dt_seat` |
| y | `fwd_1d_excess_vs_510300`（行业 ETF hfq − 510300） |
| PIT | 源表 `available_at` = 龙虎 `trade_date` **18:00 Asia/Shanghai**；Alpha 保守 `available_at_alpha_conservative` ≈ **T+1 15:00** → 交易 **T+2 开盘**。**不可前移**（见 `docs/v2/DRAGON_TIGER_COVERAGE.md`）。 |

聚合：`top_inst_labeled` 按日×`ts_code`×`seat_type` 汇总 `net_buy` → 经成分/行业映射到 SW L1 → 对应该 L1 代表 ETF。禁份额流叶子（`Δfd_share` / `ind_etf_share_flow*`）。

## 3. 为何非近亲

| 对照 | 对方信号 | 本臂 |
|---|---|---|
| 份额流族（v20–v22 reject） | ETF 自身 `Δfd_share` / 申赎流 | **不用**份额；信号来自个股龙虎 seat 净买 |
| v23 价叶（REL-MOM / PXVOL reject） | `ind_ret` / `ind_excess` / `bm_ret` 滞后与波动 | **不用**行业价收益/波动叶；映射目标是 ETF，输入不是 ETF 价 |
| NB-MARGIN-DIV（fail_precheck） | 市场层 `north_money` × 两融汇总 | **截面** SW L1，非全市场单标量 |
| DT-INST-BREADTH（fail_explore） | 全市场机构净买**广度** → 加/减 **510300** | 本臂：seat 净买/广度在 **SW L1 截面** → 持行业 ETF tercile；空仓落 510300，不是「广度抬仓宽基」 |
| EVT-DT-INST-STOCK | 机构净买 → **个股篮** | 本臂产物是 **行业 ETF 时序**，非个股袖套 |

一句话：信号是**个股龙虎 `seat_type` 净买在申万一级上的截面聚合**，再映射行业 ETF；不是 ETF 价量，不是份额流，不是市场层北向×两融。

## 4. 失败条件（可证伪）

1. 得分与滞后 `ind_ret` / `ind_excess` |ρ| 过高（建议阈 0.85，同窗日频）→ 塌成 REL-MOM 近亲 → reject。
2. 去掉 `seat_type` 分裂、改回笼统 `dt_net_*` 后，截面排序增量消失 → 无新信息维 → reject。
3. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
4. PIT 违规（用当日未披露席位 / 前移 available_at）或液态行业 ETF 覆盖过薄（日均可交易名≈0）→ fail / 停跑。
5. （附加）全样本 PIT ICIR 相对探索窗大幅塌缩且不可解释 → 不升 research_observe。

## 5. 交 Beta 冒烟口径

- 月频再平衡；GP/得分 → 液态行业 ETF **顶 tercile 等权**；空仓 / 无信号 → **510300**。
- 只认 PIT；成本 **25bp**；资本 **60万∧100万** 同权表；禁 CB/金主仓；`promotion=false`；**不交 Strategy**。
- X1 Sharpe≤0 或 avg_names=0 → fail_precheck，**不开 X2**。
- **通过门槛（一句话）**：X1 Sharpe>0 ∧ avg_names>0，且全样本 PIT ICIR 不塌缩，才可谈 `research_observe`。

## 6. 数据就绪（等批再跑）

| 资源 | 状态 |
|---|---|
| `data/v2/dragon_tiger/top_inst_labeled.parquet` | **齐**：20150105→20261009；`seat_type`∈{institution, northbound_channel, broker_prop, retail_or_hot_money}；约 228 万行（见覆盖文档） |
| `data/v2/etf/sw_l1_etf_map_pit*.parquet` / candidates / first_date | **齐**（映射与上市稀缺约束见 `BETA_X1_EVT_FLOW_COVERAGE.md`） |
| 份额流叶子 | **禁**（TrackB 同叶族停） |
| CB / 金叶主候选 | **硬禁** |

**明确：等 New Bot 书面批准本提案后再接线冒烟；本稿不开跑。**
