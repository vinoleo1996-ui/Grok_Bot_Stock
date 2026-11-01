# AI G1G5 指数调仓迁移流 权重回执（X2）

- **时间：** 2026-10-12 ~21:57 ET
- **Leo 指令：** 「全部并行做」→ 本线非动量新叶（t186u）
- **promotion_approved：** false；不下单；不交 Strategy；禁 stub 前推；不开 GP；不叠 etf_core；不投 resid×份额同构；不磨摩擦四臂换皮
- **who_pays 预注册：** `docs/v2/AI_G1G5_IDX_REBAL_FLOW_WHO_PAYS_PREREG_ZH.md`

## 1) 权重产物

| 项 | 值 |
|---|---|
| **路径** | `output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet` |
| 行数 / sessions / 标的 | **3243 / 668 / 121**（稀疏正权重导出） |
| 日期跨度 | 2024-01-02 → **2026-10-09** |
| reaches_x2_end | **true** |
| stub_window / stub_forward_fill | false / false |
| 日权重合计 | min≈mean≈max=**1.0** |
| **个股活跃日** | **103 / 668 ≈15.4%**（5 次审查窗；窗间诚实纯压舱） |
| **活跃日个股权重** | **0.70**（N=25×0.028） |
| **活跃日压舱** | **0.30**（仅 `510300.SH`） |
| 全日均压舱 / 个股 | ≈**0.892 / 0.108**（含窗间 100% 压舱） |
| 单票观测 max | **0.028** |
| mechanism_tag | `g1g5_ashare_idx_rebal_flow_v1` |
| universe_id | `g1g5_mid_large_csi_rebal_event`（调入事件∩mid_large∩D0；**非** expand top50 扁平） |
| 再平衡 | 事件驱动；K=10 after effective；**n_change=11**；非月频/非半月/非季末粘性 |
| 列契约 | `weight_long_v1_20261012` + 别名 `session,instrument_id,weight` |
| meta sidecar | `…215737.parquet.meta.json` |
| run meta | `output/ai_factory/g1g5_idx_rebal_flow_run_meta_20261012_215737.json` |
| G6 | **pass** |
| peak_rss | **2011.5 MB**（软目标 ≤1.5GB **未达**；与 friction_cost / etf_core 同量级；内部仍建 dense 再稀疏导出；研究级可消费） |
| 日均单向换手 | ≈**0.0105**（10/667 日非零；事件稀） |

脚本：`research/g1g5_idx_rebal_flow_weights.py`

末日（2026-10-09）：`510300.SH`=**1.0**（末次审查持有窗已结束；表内最新 `available_at`≈2026-05-29）。

活跃日样例（2024-06-03）：压舱 0.30 + 25 只调入等权各 0.028。

## 2) 机制（相对已败六包正交）

| 项 | 本叶 |
|---|---|
| 信号 | CSI300/CSI500 **成分调入** `event=in`；PIT `available_at`→下一开盘；持有锚 `effective_date`+**K=10** |
| 排序 | CSI300 优先 → mid_large `float_mktcap` 容量 → `available_at`；**非**收益/动量 |
| 持仓 | 窗内 top **N=25** 等权；`w_stock=min(0.70,0.028*n)`；余 510300；**不做空**调出 |
| 宇宙 | 调入事件名∩mid_large PIT∩D0 panel；诚实：expand **top50∩调入≈0**，故不用 top50 扁平篮 |
| who_pays | 被动指数强制再平衡买卖需求（无「动量/价值/quality」字样） |
| 覆盖 | X2 窗 5 次审查（2024-06/12、2025-06/12、2026-06）；314 条 PIT 调入窗 |

### 相对六败 Jaccard（活跃个股样例）

| 对照包 | Jaccard mean / max |
|---|---:|
| expand | **0.0 / 0.0** |
| friction 月频 | **0.0 / 0.0** |
| lowturn | **0.0 / 0.0** |
| resid_etf | **0.0 / 0.0** |
| etf_core | **0.0 / 0.0** |
| friction_cost | **0.0 / 0.0** |

全部远低于 0.7 换皮阈值；机制为指数调样强制流 → **结构正交，非换皮**。

## 3) 正交一句

**被动调入强制流事件袖套，非截面动量、非四臂摩擦、非解禁/份额、非 ETF0.70、非半月摩擦再设计。**

## 4) 请 New Bot

派 Beta Book-Smoke **@60万∧100万 vs 510300**，主测：

`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`

请 Alpha 研究级 ACCEPT（不扩 ACTIVE、不密封）。`promotion_approved=false`。

## 5) 不做

- 不下单；不交 Strategy；不扩 ACTIVE；不密封；不把过闸数字当晋级
- 本任务**不自跑** Book-Smoke
- 不开 GP；不叠 etf_core overlay；不投 resid×份额同构
