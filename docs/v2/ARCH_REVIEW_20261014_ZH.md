# QuantLab 架构评审（2026-10-14，研究级）

约束：live=false；禁 GP、禁小盘；不改主干代码（本次只新增这份文档）；资金分 60万 / 100万 两档。
数据口径：下文指标全部引自仓库文件（output/loop/scorecard_latest.md、docs/v2/RESEARCH_LIVE_LOOP_ENG_RECEIPT_ZH.md、docs/v2/AI_LEAF_LEDGER_ZH.md、docs/v2/SYSTEM_ARCH_DIAGRAM_ZH.md）。仓库里没有的数字一律不写。对改进项的影响只做定性方向判断，不给新的数值预测。

## 1. 现状快照（记分卡 X2 段）
| 轨道 | 60万 CAGR/MDD/Calmar | 100万 CAGR/MDD/Calmar | 成本/AUM% (60万/100万) |
|---|---|---|---|
| capacity_adv [PAPER，主干] | 13.82 / −10.07 / 1.37 | 12.23 / −11.62 / 1.05 | 1.72 / 1.71 |
| B4 conc 50/25/25 [PAPER] | 15.11 / −13.85 / 1.09 | 14.24 / −13.17 / 1.08 | 2.48 / 2.22 |
| S6 shadow 50/25/25 [SHADOW] | 17.15 / −11.95 / 1.43 | 16.37 / −12.66 / 1.29 | 2.48 / 2.23 |
| capadv+insinc 80/20 | 11.38 / −10.46 / 1.09 | 13.30 / −11.22 / 1.19 | 1.92 / 1.97 |
| C0 510300 | 11.27 / −16.24 / 0.69 | 同左 | — |

X2H 段太短，FWD 段要到 2026-11-02 才开始，两段都还没有 CAGR。

## 2. 瓶颈诊断
1. **新叶的 α 不持续，叶工厂产出低**：台账 13+ 个叶里，research ACCEPT 只有 earnings_event、insider_increase（equity_incentive 待定），其余都是 WATCH/FAIL。多个叶的残差 α 在 2025–2026 转负：analyst_recoverage 2025 −5.79、2026 −5.70；unlock_rebound 2026 −7.41；buyback_cancel、block_trade 也转负。压舱比例普遍在 64–89%，说明真正持仓的时间很少。
2. **组合层收益和回撤此消彼长**：B4 和 conc_v2 提高了 CAGR，但 MDD 加深（B4 60万 −13.85 vs 主干 −10.07）。卫星组合（70/30、80/20）在 60万档 CAGR 全部低于主干。在仓库现有的组合里，Calmar 能超过主干 60万档 1.37 的只有 S6 shadow（1.43）。
3. **B4 分段表现不稳**：monitor 显示前半段两档都跑输 C0/主干（60万 −3.65/−7.81pp，100万 −3.46/−4.56pp）。
4. **数据和运维链路脆弱**：510300 与 etf_daily_adj 停在 2026-10-09，paper-daily 因此跳过；交易日历没有建模 A 股节假日；没有调度器；没有盘中数据；alerts 为空；approve→evolve 回写停用。
5. **价格口径历史债**：叶表里旧数字是未复权自检口径，10-13 起才统一复权，跨叶比较时口径混用。
6. **成本随集中度上升**：B4/S6 的成本/AUM 约 2.2–2.5%，主干约 1.7%。100万档主干 Calmar（1.05）低于 60万档（1.37），容量是否敏感需要单独确认。

## 3. 外部系统近期亮点（经 WebSearch 核对，均为公开发布说明）
- **microsoft/RD-Agent 1.0.0（2026-09-23）**：新增 Web UI server、LLM-finetune 场景、AutoRL-Bench。0.8.0 起加入 hypo_critic/hypo_rewrite（批判并改写假设）、RAG MCP 辅助选题、improve_mode。RD-Agent(Q) 论文（NeurIPS 2025）用多臂老虎机调度研究方向，把因子和模型放在一起优化。
- **microsoft/qlib v0.9.8（2026-10-08）**：安全加固。可执行 artifact 只有显式 trusted=True 才加载；配置驱动的本地 .py 导入同样需要 trusted；高频缓存路径限制在 artifact 根目录内。v0.9.7 新增几何累计风险分析。
- **vnpy 4.5.0（2026-10-06）**：vnpy.alpha 移除 alphalens-reloaded，改为自研因子/信号绩效分析；cs_rank 改为横截面百分位；回测新增 fill_price 参数和 VWAP 撮合；ts_* 算子大幅提速。4.4.0 新增 register_functions 和 process_* 数据处理函数。
- **alphalens-reloaded**：vnpy 已不再依赖它。原版 alphalens 在 Python 3.12 下不兼容（vnpy issue #3698），选型时只考虑 reloaded 版或自研分析。

## 4. Top5 改进
| # | 改进 | 收益 | 回撤 | 效率 | 工作量 | 负责 agent |
|---|---|---|---|---|---|---|
| 1 | **数据新鲜度和交易日历加固**：补齐 510300/etf_daily_adj 日更，接入 A 股节假日日历，配外部定时调度（不起守护进程），数据过期时出告警 | 间接（让 FWD 段 2026-11-02 能按时起算） | 中性 | 高：消除 SKIPPED_DATA_STALE 和节假日误判 | 小–中（2–3 人日） | Data（日更、日历）+ Eng（新鲜度判定、调度入口） |
| 2 | **叶的 α 衰减闸门**：仿 RD-Agent hypo_critic，预注册时加入「逐年残差 α 不得在最近两年连续为负」和压舱率上限；用多臂老虎机分配研究额度，优先投向高 ACCEPT 率的机制族（事件型：业绩、增持、股权激励） | 中：减少 WATCH 叶占用的研究时间 | 间接：避免把衰减腿放进组合 | 高 | 中（3–5 人日，只改文档和自检脚本外围，不碰主干） | AI（闸门规则）+ Alpha（裁定口径） |
| 3 | **回撤预算化的组合层**：把 S6 shadow 作为主要候选，组合按 MDD/Calmar 约束优化，60万/100万分档设集中度上限，取代单纯追求 CAGR 的集中化 | 维持或略低于 B4 | 目标是 MDD 不劣于主干（60万 −10.07、100万 −11.62） | 中 | 中（4–6 人日，在 shadow 轨验证） | Beta（风险预算）+ Strategy（账本） |
| 4 | **成本和撮合真实性**：参考 vnpy 4.5 的 fill_price/VWAP 撮合，对 B4/S6 做 VWAP vs close 成交的敏感性测试，并按 60万/100万分档做 ADV 容量检查 | 让收益估计更可信（可能下修） | 中性 | 中 | 中（3–4 人日，新增脚本，不改引擎默认） | Eng（撮合选项）+ Strategy（敏感性报告） |
| 5 | **统一价格口径和因子分析**：把台账旧叶全部重算为复权口径，并加一个 IC/分层/换手的标准报告（自研，或用 alphalens-reloaded 只读），写进记分卡附表；同时按 qlib 0.9.8 的思路，对加载可执行 artifact 设 trusted 开关 | 间接：比较更公平 | 中性 | 中：减少口径争议 | 小–中（2–4 人日） | AI（重算）+ Eng（报告/trusted 加固）+ Web（展示） |

Intel：等预警真正有产出（目前 alerts 为空）后，再评估是否作为 Top5 之外的第 6 项接入风险标记。

## 5. 不做的事
GP、小盘方向、改主干 capacity_adv、实盘/下单、引入有守护进程的 UI 服务（RD-Agent web UI 只作为参考，不部署）。
