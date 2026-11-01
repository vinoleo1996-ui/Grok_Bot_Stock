# ETF 新臂提案：ETF-IND-LU-BREADTH（待批）

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 ET |
| 作者 | QuantLab AI |
| 代号 | **ETF-IND-LU-BREADTH** |
| promotion_approved | **false** |
| 状态 | **待 New Bot 批**（批前不开跑、不回测、不调参） |
| 不交 | Strategy |

## 1. 机制一句

个股涨跌停 / 连板微观结构在 **申万一级** 截面聚合为行业广度（或净广度），映射液态行业 ETF 时序；吃的是限价制度拥挤在板内扩散到 ETF 的滞后，付钱的是行业内打板失败后的短线资金——**不是**行业相对动量，**不是**龙虎 seat，**不是** ETF 份额流。

## 2. 叶 / 标签

| 项 | 草案 |
|---|---|
| 叶子 | `lu_breadth_sw_5`、`lu_streak_breadth_sw`、`ld_breadth_sw_5`（由个股 `lu_flag` / `lu_streak` / `lu_height` / `ld_*` 在 SW L1 日聚合再滚动；窗名可微调，语义不变） |
| sleeve | `etf_timing_ind_lu_breadth` |
| y | `fwd_1d_excess_vs_510300`（行业 ETF hfq − 510300） |
| PIT | 涨跌停状态 **当日收盘后可知** → Alpha 可用 **T+1 开盘**。**勿用未收盘触板**（盘中临时触板不可当作当日终态）。 |

聚合路径：个股日终涨跌停 / 连板高度 / 连板天数 → 按成分映射 SW L1 → 行业内广度或净广度（涨停占比、连板占比、跌停占比等）→ 对应该 L1 代表液态 ETF。禁份额流叶子（`Δfd_share` / `ind_etf_share_flow*`）；禁价叶（`ind_ret` / `ind_excess` / `bm_ret`）；禁龙虎 `seat_type` 同构；禁 CB / 金主仓。

## 3. 为何非近亲

| 对照 | 对方信号 | 本臂 |
|---|---|---|
| 份额流族（v20–v22 reject） | ETF 自身 `Δfd_share` / 申赎流 | **不用**份额；输入是个股涨跌停微观结构的行业聚合 |
| v23 价叶（REL-MOM / PXVOL reject） | `ind_ret` / `ind_excess` / `bm_ret` 滞后与波动 | **不用**行业价收益/波动叶；映射目标是 ETF，输入不是 ETF/行业收益 |
| ETF-DT-SEAT（已纸拒） | 龙虎 `seat_type` 净买 → SW L1 → 行业 ETF | **不用**龙虎席位；输入是涨跌停 / 连板广度，与 seat 净买正交信息面 |
| LIMITUP-FADE-REV（fail_precheck） | 个股袖套：触板 T → T+1 弱 → T+2 买该票 HOLD=3 | 本臂产物是 **行业 ETF 时序**（行业内触板拥挤广度），非个股触板次日弱反转篮 |
| DT-INST-BREADTH（fail_explore） | 全市场机构净买广度 → 加/减 **510300** | 本臂：涨跌停广度在 **SW L1 截面** → 持行业 ETF tercile；空仓落 510300，不是「席位广度抬仓宽基」 |

一句话：信号是**个股涨跌停/连板在申万一级上的截面广度**，再映射行业 ETF；不是 ETF 价量，不是份额流，不是龙虎 seat，不是个股触板袖套。

## 4. 失败条件（可证伪）

1. 得分与滞后 `ind_ret` / `ind_excess` |ρ| ≥ **0.85**（同窗日频）→ 塌成 REL-MOM 近亲 → **自拒**。
2. 与 ETF-DT-SEAT / 笼统 `dt_*` 行业聚合得分 |ρ| 过高且去掉涨跌停信息后排序无增量 → 无新信息维 → reject。
3. X1@**60万∧100万** Sharpe≤0 或 avg_names=0 → **fail_precheck**（不开 X2）。
4. PIT 违规（用未收盘触板 / 前移 available_at）或液态行业 ETF 覆盖过薄（日均可交易名≈0）→ fail / 停跑。
5. （附加）全样本 PIT ICIR 相对探索窗大幅塌缩且不可解释 → 不升 research_observe。

## 5. 交 Beta 冒烟口径

- **月频**再平衡；得分 → 液态行业 ETF **顶 tercile 等权**；空仓 / 无信号 → **510300**。
- 只认 PIT；成本 **25bp**；资本 **60万∧100万** 同权表；禁 CB/金主仓；`promotion=false`；**不交 Strategy**。
- X1 Sharpe≤0 或 avg_names=0 → fail_precheck，**不开 X2**。
- |ρ(ind_ret)|≥0.85 → 自拒（近亲）。
- **通过门槛（一句话）**：X1 Sharpe>0 ∧ avg_names>0，且全样本 PIT ICIR 不塌缩、非价叶近亲，才可谈 `research_observe`。

## 6. 数据就绪（等批再跑）

| 资源 | 状态 |
|---|---|
| 工厂个股 `lu_flag` / `lu_streak` / `lu_height` / `ld_*` 等 | **齐**（TrackA 已用；本臂仅做 SW L1 截面聚合，不新拉源） |
| `data/v2/etf/sw_l1_etf_map_pit*.parquet` / candidates / first_date | **齐**（映射与上市稀缺约束见 `BETA_X1_EVT_FLOW_COVERAGE.md`） |
| 份额流 / 价叶 / 龙虎 seat 同构 / CB·金 | **硬禁**（本臂不接线） |
| ETF-DT-SEAT | **已停 / 纸拒**；本臂非其变体 |

**明确：等 New Bot 书面批准本提案后再接线冒烟；本稿不开跑、不启 v27 GP、不交 Strategy。**
