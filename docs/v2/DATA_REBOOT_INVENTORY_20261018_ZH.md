# Data 层重启盘点（2026-10-18，QuantLab Data，只读核查）

- 编写：2026-10-18 01:27 ET。box 01:05 ET 重启，工作区由快照恢复。研究级，promotion_approved / live / strategy_promotion 全部 false；未启 8787，未碰 moneyflow。
- 本次只做了三类写入：本清单；`output/HOLD_FUNDPORT_MERGE` 门控（原先不存在，按主 Agent 要求新建）；在 `remaining_after_stk_surv.py` 里加了合并前门控检查（备份为 `.bak_20261018_holdgate`）。没有改任何数据文件，也没有重拉。

## 0. 恢复是否结束
| 时间 (ET) | 文件数 | du（字节） | MemAvailable |
|---|---|---|---|
| 01:12（主 Agent 记录，05:12 UTC） | 145919 → 152161（20 秒内） | — | — |
| 01:14:45 | 181691 | 30,505,350,954 | 12.7 GB |
| 01:16:52 | 181855 | 30,525,900,109 | 11.8 GB |
| 01:18:53 | 181901 | 30,526,622,432 | 11.6 GB |

- 判定：**恢复约在 01:14 ET 结束**。01:16:52 之后，data/、scripts/、docs/v2 下只新增了 4 个文件，都是其他 agent 的正常写入（alerts、LOTFIX/AI 文档、Arch 的 RECOVERY_INVENTORY），不是恢复进程写的。所以没有等到"连续两次完全不变"，01:21 停止了计数。
- 快照时点：文件 mtime 全部是 01:06–01:14 的恢复时间，不能用来判断。git HEAD 为 e7b240d（10-18 00:55:09 ET）。按 Arch 从内容推断，快照约截至 01:04–01:05 ET。Data 层内容与 00:57 ET 时的状态一致（fund_portfolio 20211231 已拉到第 233 页）。

## A. 完整保留（不用恢复）
| 项 | 行数 / 文件数 | 最新日期 | sha256 前缀 | 核对 |
|---|---|---|---|---|
| 日线原始 `data/v2/tushare_raw/daily/` | 2130 个文件 | 20261016 | — | 与主 Agent 01:16 一致 |
| daily_basic_full_tushare | 12,309,945 | 2026-10-16 | f6bbf9e5 | 行数与 manifest 一致（history_diff_rows=0） |
| adj_factor_2023h2plus | 4,090,293 | 20261016 | 4642ca8e | = manifest sha |
| 指数 index_daily_pit（另有 6 个 index_daily） | 18,639 | 2026-10-16 | — | |
| etf/etf_daily_adj | 1,564,839 | 20261016 | 48b21e84 | |
| 510300（fund_daily_tushare_510300 / panels/sh.510300） | 3,495 / 3,495 | 20261016 | 9b62520e / cd90a4fa | |
| asof_extend_tushare_202610/panels | 5582 个（重启前报的是 5578） | 5567 个到 2026-10-16；其余 15 个停在 07-13 到 10-12 | — | 15 个面板疑为停牌或退市；+4 的差异待核对，不影响日更 |
| mid_large_members_pit / top300_monthly | 5,565,449 / 42,600 | session_max 2026-10-16 | 4b82c749 / 05a2f8f7 | = manifest sha |
| trade_cal_sse_pit | 8,035 | 20261231 | fa4260b8 | ✅ = 已知 sha |
| forecast_2024h2_2025 | 7,040 | 20240606→20251015 | d6629a05 | ✅ |
| forecast_2024plus | 11,399 | →20261016 | f1e59284 | ✅ = manifest sha |
| 事件一年窗口（holder_trade_1y / express_1y / forecast_1y / pledge_latest） | summary 的 today=2026-10-16 | ann 到 20261016；pledge 到 20261009 | — | 窗口未退回 10-14 |
| docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md | 在 | | | |
| output/daily_update_status.json | status=ok | target 2026-10-16 | | |
| output/data_freshness_status.json | overall=ok | expected 20261016（00:48 ET 生成） | | |
| ref/stock_delisted | 339 | 退市日到 20260730 | 90c8934d | ✅ = manifest，与 Arch SD1 规格一致 |
| ref/etf_basic / etf/etf_basic | 1,862 / 1,838 | | 99cf9b15 / 3820cb86 | |
| report_rc_2018plus（及 _orgid、org 映射） | 1,917,334 | 20261013 | 2d3a37a7 / b01d5515 | report_rc_orgnorm.DONE 在 |
| equity_incentive_em | 12,975 | | 57c00947 | |
| stk_surv_2018plus | 395,691 | | 57f91377 | = 队列日志 sha |
| broker_recommend 原始缓存 | 106 个（201801–202610） | 202610 | — | 已齐，合并未做 |
| fund_portfolio_dh 分页 | 15 期有 _DONE（20180331–20210930）；20211231 拉到第 233 页 | | — | 断点未丢 |
| v1 cs_panel `output/ai_factory/panel_cache` | 2018–2026 共 9 个文件 + ind_names.csv，合计 9,072,309 行 | 2026-10-14 | 2018:035d1f60 … 2026:4608d8bc | 没有已知原 sha，只记现值；属冻结产物，没动 |
| 脚本 tier1_materialize.py | 带 dupfix（keep='last'，比较函数遇重复键报错） | | e9c89a6c | .bak_20261014_dupfix 在 |
| research/strategy_hiliq_universe_v1.py | | | 8c43e78f | ✅ = HI_LIQ v1.1 预注册 sha |
| research/ai_cs_panel_build.py | | | 66cfcb81 | 没有原 sha |
| relay_outage_backfill.py | QL_TODAY 修复在（取交易日历 ≤ 今天的最后开市日） | | 4db3d9b1 | |
| nightly_update.py | 有 adj_factor 步骤和 summary 合并写修复 | | ec079d56 | |
| relay_health.py / trade_cal_pit.py / data_freshness_status.py / adj_factor_incr.py | 都在 | | 6d3ea9f5 / 90e3df43 / 38e2911c / 723726c5 | |
| remaining_after_stk_surv.py | 在 | | 0d3aca50（加门控前） | |

## B. 回退到旧版本
- **数据表：无。** 没有发现任何表回退到 10-16 之前。
- `docs/v2/DATA_SUSPEND_RESUME_DELIST_DIAG_ZH.md`：现在的版本是重启后约 01:11 ET 写的"事故后重写版"，比原版精简；01:2x ET 已由 cs_panel 线程加更正注。原版没有恢复回来。sha 现为 02fc06f6，与 Arch 清单记的 cf953ada 不一致，说明 Arch 记录之后这份文件又被改过。成本：低，属本地文档；结论不变。
- `scripts/fix_sd1/`：恢复后只有 D-1 草稿脚本；01:22 ET cs_panel 线程重写了三份脚本（resumefix、suspend_flags_v2、stock_delisted_v2），需要按新 sha 重新送 Arch 审。

## C. 丢失
| 项 | 状态 | 恢复方式 / 成本 |
|---|---|---|
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md（原版） | Arch 清单确认丢失 | **已由 cs_panel 线程 01:23 ET 重写**，同时新写了 DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md。本地，无 API 成本 |
| output/diag/ 诊断明细 | 目录在，内容为空 | 本地只读重算（suspend_d × daily × cs_panel），约 10–20 分钟，无 API |
| output/HOLD_FUNDPORT_MERGE 门控 | 不存在（不确定原来是否落盘） | **已于 01:21 ET 新建**；脚本原来不认这个文件，已加门控检查 |
| 进程 PID 242829（fund_portfolio）、345195（补拉守护） | 已消失 | **已重启**：94322、94403（见下） |
| 需重拉 API 的数据 | **无** | — |

## 重启后的进程（01:22 ET，setsid nohup）
- **94322** `remaining_after_stk_surv.py`：前置条件通过，report_rc 机构名归一跳过（已完成），fund_portfolio 从 **20211231 第 234 页**续拉（注意：不是 20220331，20211231 还没有 _DONE）。01:26 已到第 284 页，大约每分钟 50 页。全部期数拉完后遇到 HOLD 门控就停：只记 `merge_held` 日志，不合并、不写 DONE、不写回执；broker_recommend 合并同样挂起。删除门控文件后重跑脚本即可合并（幂等）。日志：logs/remaining_after_stk_surv_restart_20261018_0122ET.log；状态写在 output/remaining_queue_status.json。
- **94403** `relay_outage_backfill.py`：01:22:25 启动，事件窗口已经完成。当前按队列串行补跑：tier3 的 10-14、10-15、10-16，hsgt 和 sw 的 10-16，cyq 的 10-16（sw 和 cyq 的 10-15 已被 10-16 的整月重拉覆盖），以及 hsgt_top10 窗口。正在跑子进程 94466/94467（tier3 20261014）。这些步骤都不涉及 moneyflow。日志：logs/relay_outage_backfill.log、logs/relay_backfill_*.log。

## 与 Arch RECOVERY_INVENTORY 的出入
1. 诊断文档的 sha：Arch 记 cf953ada，现为 02fc06f6，Arch 记录之后被 cs_panel 线程改过（加了更正注）。
2. 重建方案：Arch 记为"缺失，需 Data 重出"，现在已被重写（01:23 ET），需要 Arch 按新 sha 复审。
3. cs_panel：Arch 未记 sha。本清单补了 9 个文件的现值，作为今后比对的基线。
4. fund_portfolio 续拉起点：主 Agent 说从 20220331，实际是 20211231 第 234 页，见上。

## 建议
- 数据层不用重拉，也不用回滚。
- 剩下的只有本地工作：output/diag 重算，以及按新 sha 把重建方案和三份脚本送 Arch 审。这两项都归 cs_panel 线程。
- 由主 Agent 决定何时删除 HOLD_FUNDPORT_MERGE，然后重跑脚本完成合并和回执。
