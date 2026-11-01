# AI G1G5 摩擦降成本再设计 权重回执（X2）

- **时间：** 2026-10-12 ~21:43 ET
- **Leo 确认卡：** 「摩擦降成本再设计」（t180s789）
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP；不叠 etf_core overlay；不投 resid×份额同构
- **who_pays 预注册：** `docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet` |
| 行数 / sessions / 标的 | **34068 / 668 / 51** |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min≈mean≈max=**1.0** |
| 日均活跃名 | ≈**21**（20 个股 + 510300 压舱） |
| **个股日均权重** | **0.85** |
| **压舱日均权重** | **0.15**（仅 `510300.SH`） |
| 单票硬顶 L | **0.05**（观测 max=0.05）；样例日触顶约 8–13/20，其余由容量×得分倾斜拉开 |
| mechanism_tag | `g1g5_ashare_friction_cost_redesign_v1` |
| universe_id | expand 同接口 mid_large top50 |
| 再平衡 | **半月** step=10 交易日 + 首末日；**n_rebal=68**；**非**季末+进12/出28 |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `…214334.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_friction_cost_redesign_run_meta_20261012_214334.json` |
| G6 | **pass** |
| peak_rss | **2033.3 MB**（软目标 ≤1.5GB **未达**；D1 估值 asof 全表过滤读主导，与 etf_core 包同量级；仍研究级可消费） |
| 日均单向换手 | ≈**0.046**（67/667 日非零，半月 cadence） |

脚本：`research/g1g5_friction_cost_redesign_weights.py`

末日（2026-10-09）示例：`510300.SH`=0.15；个股 20 名合计 0.85，单票 ∈≈[0.024, 0.05]。

## 2) 机制（相对已败五包正交）

| 项 | 本叶 |
|---|---|
| 慢制度臂 | ETF 份额流→**成分股** (0.55) + 解禁残差供给冲击 (0.45) |
| 砍掉 | **T+1=0**；**涨跌停带宽=0**（相对 friction/lowturn 四臂） |
| 加权 | D1 `float_mktcap`×`turnover_rate` asof × 得分秩倾斜；**非**等权 top20 |
| 压舱 | 仅宽基 510300 **0.15**（**禁** etf_core 0.70/0.30 行业 ETF 主仓） |
| cadence | 半月 step=10（**禁** lowturn 季末+enter12/exit28） |
| who_pays | 解禁供给冲击残差对手盘 + 份额流转成分股配置对手盘（无「动量/价值」字样） |
| D1 | ACCEPT_FULL 仅研究 asof；**非**晋级授权；禁假跑 V35 |

### L 口径说明（可证伪）

严格 **L≤1.5%** ∩ mid_large **top50** 在个股预算≈0.85 下几何上迫使几乎全员触顶 → 打分失效、近似等权。本叶采用 **L≤5% 等价硬顶**（对齐原 friction EW top20 单票量级），并保留容量×得分倾斜，使权重可分（样例日 min≈1.3%–2.6%，非全员触顶）。

## 3) 相对 prior 活跃集（个股 Jaccard 样例）

| 对照包 | 样例 Jaccard mean / max |
|---|---:|
| friction 月频 `…111316` | ≈**0.35 / 0.50** |
| lowturn `…112301` | ≈**0.19 / 0.23** |
| resid_etf `…002418` | ≈**0.28 / 0.35** |
| etf_core `…204928` | ≈**0.17 / 0.25** |

全部明显低于 0.7 换皮阈值；机制上砍高换手臂 + 改加权 + 改 cadence + 压舱≤0.15 → **结构正交，非换皮**。

## 4) 请 New Bot

派 Beta Book-Smoke **@60万∧100万 vs 510300**，主测：

`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`

对照（勿当主线）：lowturn / friction / etf_core / expand。请 Alpha 研究级 ACCEPT（不扩 ACTIVE、不密封）。

## 5) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不密封；不把过闸数字当晋级
- 本任务**不自跑** Book-Smoke
- 不开 GP / 不开 v29；不叠 etf_core overlay
