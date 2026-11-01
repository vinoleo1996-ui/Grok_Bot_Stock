# Arch 内审修正：Strategy 交 Eng/Beta 的修改建议（2026-10-14 07:50 ET）
状态：**建议稿，未实施**。Strategy 没有改任何引擎代码、FROZEN_CONFIG、STATUS 或权重。live=false；promotion=false。
需要 Eng + Beta 共同签字的项目已标出；涉及冻结文件的改动还要按 Arch #14 附理由、经主 Agent 签字。

## A. 旧纸面 v1（Arch #2/#3）——先问 Eng 归属
- 已做（Strategy，只改文档）：48 个引用旧纸面 `v2_strategy_paper` 数字的报告已在文首加「仅参考」标注，清单见 output/strategy_cpcv/ref_only_labeled_files.txt（output/strategy_paper_v1*/、output/strategy_paper_costs/**、TURN_FAILURE_DIAGNOSIS、E1_RECONCILE、S2_LEDGER_COST_ALIGNMENT、STRATEGY_PAPER_FEED、TURN_FULL_D1_MEMORY）。
- Strategy 核实：当前三条纸面轨（capacity_adv/B4/S6）和本轮所有组合都走 book-smoke 主引擎（next_open、T+1、涨跌停、整手），**没有引用 v1 数字**。
- **问 Eng：v2_strategy_paper*.py 的修复归谁？** Strategy 建议：v1 线直接降级为"仅参考/冻结不再维护"，不修；如仍要用，方案是 (1) merged_daily_returns 传 total_return_factor；(2) 改走 run_weight_schedule（next_open+T+1+涨跌停+漂移）；(3) 修复后重跑 strategy_paper_costs/full_d1_fixed_armA 做对照。另注：该模块在盒子上缺 scipy 无法 import（ENG_METRICS_UNIFY 已记）。

## B. 需要 Eng + Beta 共同签字（碰 FROZEN_CONFIG 或 Eng 代码）
| # | 位置 | 现状 | 建议 |
|---|---|---|---|
| B1 | quantlab/portfolio/b4_paper.py:73-79；output/strategy_paper_s6/FROZEN_CONFIG.json（B4 同） | 字段 `N={600000:6,1000000:10}`，实为每腿 topN；实际组合持仓中位 16/24 | 新版配置用 `per_leg_topN`，并加 `realized_names_median`（60万/100万）。**不改已冻结文件的 sha**：建议在 FROZEN_CONFIG 旁加 `FROZEN_CONFIG.annot.json`（注释，不参与哈希），或在下次经批准的重冻结时改名，读取端兼容两种键 |
| B2 | 所有报告/看板/STATUS 文案 | X2 成绩有时未标"样本内" | scorecard/看板/receipt 模板对 X2 窗口统一加后缀「（X2 样本内）」；WINDOW_LABEL["X2"] 改为 "探索窗 X2 2024-06..2026-10-09（样本内）"（v2_multisleeve_book.py:37-38，仅文案） |
| B3 | quantlab/portfolio/v2_multisleeve_book.py:36 | `WINDOWS["X2"]=("2024-06-03","2026-10-09")` 写死；前向依赖权重延展 | X2 保持冻结（历史可比）；**新增** `X2H`/`FWD` 终点由 trade_calendar 最近已收盘交易日驱动；权重末日 < 日历应有日时输出 WAITING 并 emit 看板告警（Arch #17）；单测：终点=日历、权重落后 1 天告警 |
| B4 | b4_paper.py:127,129,198 等 | 年化已统一 244（Eng 回执）| Strategy 本轮全部按 244；旧 strategy_wf_combo/dd_budget 的 dd_screen 筛选用 252（引擎数是 244），报告注明 |

## C. 本轮研究顺带发现（供 Eng 参考）
- book-smoke 在 C3_100w 跑完写出结果后进程退出时 `terminate called without an active exception`（signal 6），结果文件完整，疑为某线程池退出时序问题，建议查。
