# AI G1G5 非教科书机制重生回执（A股制度摩擦日更）

**日期**：2026-10-12 · America/New_York  
**角色**：QuantLab AI（后台执行器）  
**状态**：研究级 · **`promotion_approved=false`** · **`strategy_promotion_approved=false`** · **不下单** · **不交 Strategy** · **不进 hard_gates 晋级**  
**触发**：Leo 确认卡「启动非教科书重生」；New Bot：扩池 Book-Smoke any_pass 但机制=截面动量 → 暂不主攻（**对照包保留备选，未废弃**）  
**对照**：`AI_G1G5_EXPAND_G6_RECEIPT_ZH.md`；`BOOK_SMOKE_G1G5_EXPAND_RECEIPT_ZH.md`；`TRADINGAGENTS_DEEP_READ_ZH.md`；`QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md`

---

## 1. 产物路径

| 产物 | 路径 |
|---|---|
| 全日更权重 | `output/intel/g1g5_nontextbook_daily_weights_20261012_110220.parquet` |
| 权重 sidecar meta | `output/intel/g1g5_nontextbook_daily_weights_20261012_110220.meta.json` |
| 运行 meta | `output/intel/g1g5_nontextbook_run_meta_20261012_110220.json` |
| 辩论账本 | `output/intel/debate_ledger_g1g5_nontextbook_20261012_110220.jsonl` |
| G6 证明账本 | `output/intel/debate_ledger_g1g5_nontextbook_20261012_110220_g6_proof.jsonl` |
| 实现 | `research/g1g5_nontextbook_weights.py`（复用 expand 宇宙/日历/权重落盘 + G6） |
| **扩池动量包（保留·备选/对照，未废弃）** | `output/intel/g1g5_expand_daily_weights_20261012_105459.parquet` |

---

## 2. 机制定义（非教科书）

| 臂 | 权重（名义） | PIT 定义 | who_pays 对手盘 |
|---|---|---|---|
| **ETF 份额流** | 0.40 | `ind_etf_share_flow_by_sw_l1`：`available_at≤session`；trailing 5 个可见 `trade_date` 的 `flow_est_wan_yuan` 行业加总 → 截面 z → SW L1 成分继承 | 行业 ETF **创设/赎回** 对手盘 |
| **解禁残差** | 0.25 | `share_float_pit`：`available_at≤session` 且 `float_date∈(session, session+20d]` 的 `float_ratio` 加总 → 截面 z 后取负（规避供给冲击） | 解禁供给冲击对手盘 |
| **T+1 抛压** | 0.20 | D0 panel：当日 open→close 正收益 × 换手偏高（相对自身历史分位）→ 截面 z 后取负 | T+1「当日买次日才能卖」隔夜抛压对手盘 |
| **涨跌停带宽** | 0.15 | 近 5 日 `day_ret / limit_ratio_at_open`：近涨停带拥挤扣分、近跌停带缓解加分（大盘股触板稀，用带宽邻近度；**非** excess 排序） | 限价制度拥挤 / 跌停缓解对手盘 |

**选股**：四臂加权合成分 → **top20 等权**（日毛敞口=1.0）；月频再平衡（510300 日历）+ 窗首。  
**明确禁止**：`excess_20d vs 510300` 排序；mechanism_tag / who_pays **不含「动量」**；不作 FactorCandidate。

`mechanism_tag` = **`g1g5_ashare_inst_friction_v1`**  
`who_pays_zh` = A股制度摩擦组合：行业ETF申赎…（全文见 meta；已断言无「动量」字样）

本批再平衡 13 次 **无臂 coverage_gap**（四臂均可计）；解禁臂在无公告窗压力=0（诚实，非缺表）。

---

## 3. 宇宙

| 项 | 值 |
|---|---|
| **`universe_id`** | **`g1g5_mid_large_liquid_top50`**（复用扩池包） |
| 源 | Data `mid_large_members_pit` @ 2024-06-28 按 float_mktcap ∩ D0 panel 前 50 |
| 标的数 | **50** |
| 再平衡 | 窗首 + 月末，共 13 次；再平衡日 PIT 成员交叉 |

---

## 4. 权重表摘要（完整日更 · 非 stub）

| 项 | 值 |
|---|---|
| 行数 | **12100**（242 × 50） |
| 日期跨度 | **2024-01-02 → 2024-12-31** |
| `n_distinct_sessions` | **242**（>10 → **非 stub_window**） |
| 日毛敞口 | mean=min=max=**1.0** |
| 活跃名/日 | **20** |
| 列 | `date,instrument,target_weight` + 权威别名 `session,instrument_id,weight` + `mechanism_tag,who_pays_zh,universe_id` |
| 契约 | `column_contract_version=weight_long_v1_20261012`（Eng） |
| `promotion_approved` | **false**（sidecar + run meta） |

---

## 5. 与扩池动量包（备选/对照）差异

> **保留声明**：`output/intel/g1g5_expand_daily_weights_20261012_105459.parquet` **未废弃**，继续作为**备选/对照包**留存（Book-Smoke 数字已过 any_pass；机制因教科书动量暂不主攻）。本批非教科书包为**当前主攻**候选，二者并行可测。

| | 扩池动量包（备选/对照） | 本批 nontextbook（主攻） |
|---|---|---|
| 路径 | `output/intel/g1g5_expand_daily_weights_20261012_105459.parquet` | `output/intel/g1g5_nontextbook_daily_weights_20261012_110220.parquet` |
| 选股 | 截面 **excess_20d vs 510300** top20 | **制度摩擦四臂合成** top20 |
| mechanism_tag | `g1g5_pit_debate_rule_v2_expand` | **`g1g5_ashare_inst_friction_v1`** |
| who_pays | 含「截面动量 PIT 规则选股」 | **禁「动量」字样**；写清制度/事件对手盘 |
| 活跃集 Jaccard（样本月） | — | **0.03–0.25**（与对照包高度不同：典型仅重叠 1–5 名） |
| Book-Smoke | any_pass=true；机制暂不主攻 | **待 Beta 重测**；通过亦不自动交 Strategy |

---

## 6. Ledger / G6

| kind | 条数 |
|---|---|
| `debate_turn` | 247 |
| `decision` | 19 |
| `settlement` | 18（α@510300；含 `resolution_date`） |
| still pending | 1（`2026-06-25` 未满窗） |
| **G6** | **pass**（future settlement 被 as_of 挡） |

---

## 7. 资源 / 禁项

| 项 | 值 |
|---|---|
| 峰 RSS | ≈2134744 KB（~2.04 GiB，**略超 2GB 贴边**；与 expand 同级；未再加压） |
| 结算基准 | **510300** |
| 禁 | Yahoo / Reddit / StockTwits；动量/价值教科书主线；vendor TradingAgents；下单；Strategy；hard_gates 晋级；stub 前推 |

---

## 8. 复跑

```bash
cd /workspace/QuantLab
python research/g1g5_nontextbook_weights.py --top-n 50 --active-n 20 \
  --horizon-days 5 --weight-start 2024-01-02 --weight-end 2024-12-31
```

*End. promotion_approved=false. No orders. No Strategy submit. Not a hard_gates candidate. Awaiting Beta Book-Smoke on this parquet.*
