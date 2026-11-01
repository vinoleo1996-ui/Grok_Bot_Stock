# 10-15 05:20 ET 之后的产出清单（Arch，2026-10-18 00:29 ET）

应主 Agent 要求，只读扫描 `/workspace/QuantLab`（排除 .git）和 `/workspace/quantlab-web`（排除 .git、node_modules），按文件 mtime 统计，时间均为 ET。逐文件清单见 `arch_activity_since_20261015.csv`，脚本 `arch_activity_since_20261015.py`；owner 按路径和文件名前缀推断。

## 核心结论
- **从 10-15 05:20 到 10-17 23:50，两个仓库里没有任何文件被修改（0 个）。** 所有新产出都在 10-17 23:51（主 Agent 巡检 `supervise_patrol_20261017_2350_ET.md`）之后，也就是叫醒之后。所以停摆期间，不论是例程还是 agent，都没有留下产出。「例程停摆，部分 agent 还在产出」只适用于 10-17 23:51 之后。
- 10-15 05:18–05:19 有一次整体恢复，大批文件的 mtime 被重写，不计入本清单。所以早于 05:20 的真实产出时间不能用 mtime 判断（K4 已提过）。
- 截至扫描时（2026-10-18 00:29 ET），一共 13112 个文件。其中 Data 面板刷新占绝大多数，另有约 1.3k 个是 .venv/.pyc 重编译，不算产出。

## 按 agent 汇总
| owner | 文件数 | 最早 | 最晚 | 代表文件 |
|---|---|---|---|---|
| 主 Agent | 2 | 10-17 23:51 | 10-18 00:12 | `output/d1/supervise_patrol_20261018_0011_ET.md`<br>`output/d1/supervise_patrol_20261017_2350_ET.md` |
| Data | 10981 | 10-17 23:55 | 10-18 00:29 | `data/v2/tushare_raw/fund_portfolio_dh/20210630/000460000.parquet`<br>`data/v2/tushare_raw/stk_holdertrade/202608.parquet`<br>`data/v2/tushare_raw/stk_holdertrade/202607.parquet`<br>`data/v2/tushare_raw/fund_portfolio_dh/20210630/000459000.parquet` |
| Eng | 13 | 10-17 23:53 | 10-18 00:08 | `docs/v2/ENG_ARCH_K5_ARCHIVE_RECEIPT_ZH.md`<br>`output/strategy_optimizer/core_x2/c5_feasibility_v1_3.csv`<br>`output/strategy_optimizer/core_x2/c5_cash_dist_v1_3.csv`<br>`output/strategy_optimizer/core_x2/c5_weight_stamp_v1_3.json` |
| Strategy | 484 | 10-17 23:59 | 10-18 00:29 | `output/strategy_hiliq/topn_tie_audit/sens_smoke_B4_ADV_100w/aum_1000000/X2/BOOK/sleeve_weights.csv`<br>`output/strategy_hiliq/topn_tie_audit/sens_smoke_B4_ADV_100w/aum_1000000/X2/BOOK/summary.json`<br>`output/strategy_hiliq/topn_tie_audit/sens_smoke_B4_ADV_100w/aum_1000000/X2/C0/target_weights.parquet`<br>`output/strategy_hiliq/topn_tie_audit/sens_smoke_B4_ADV_100w/aum_1000000/X2/C0/actual_weights.parquet` |
| AI | 54 | 10-17 23:55 | 10-18 00:19 | `research/g1g5_biz_climate_alpha.py`<br>`docs/v2/AI_G1G5_BIZ_CLIMATE_WHO_PAYS_PREREG_ZH.md`<br>`output/ai_factory/prereg_sha_leaf21.txt`<br>`docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_LOWTO_WEIGHT_RECEIPT_ZH.md` |
| Alpha | 20 | 10-17 23:54 | 10-18 00:26 | `output/alpha/recon_eqinc/step_b.log`<br>`research/alpha_s8_errata_sparse_ic.py`<br>`output/alpha/recon_eqinc/step_a.log`<br>`output/alpha/recon_eqinc/_ai_ic20_series.parquet` |
| Beta | 36 | 10-18 00:14 | 10-18 00:24 | `docs/v2/BETA_OPTIMIZER_STAGE2_S2_3_COSIGN_ZH.md`<br>`output/beta/s2_3_band_check/s2_3_band_sim_rows.csv`<br>`output/beta/s2_3_band_check/s2_3_band_sim_summary.csv`<br>`output/beta/s2_3_band_check/cache.log` |
| Intel | 43 | 10-17 23:53 | 10-18 00:26 | `docs/v2/INTEL_EARNINGS_PREANNOUNCE_PREREG_ZH.md`<br>`docs/v2/INTEL_EARNINGS_PREANNOUNCE_PREREG_ZH.md.sha256`<br>`docs/v2/INTEL_HYPERSCALER_CAPEX_DESIGN_ZH.md`<br>`docs/v2/INTEL_HYPERSCALER_CAPEX_DESIGN_ZH.md.sha256` |
| Arch | 21 | 10-18 00:02 | 10-18 00:28 | `docs/v2/audit/arch_activity_since_20261015.csv`<br>`docs/v2/audit/ARCH_K6_INDUSTRY_FULLPOOL_DISCLOSURE_V0_V1_2_ZH.md`<br>`docs/v2/ARCH_INTEL_EARNINGS_PREANNOUNCE_PREREG_REVIEW_ZH.md`<br>`docs/v2/audit/arch_k6_industry_fullpool_summarize.py` |
| Web | 97 | 10-17 23:53 | 10-18 00:29 | `quantlab-web:site/index.html`<br>`quantlab-web:site/holdings.html`<br>`quantlab-web:site/leaves.html`<br>`quantlab-web:site/timeline.html` |
| Web(ql_bus 事件总线，多 agent 写入) | 10 | 10-18 00:00 | 10-18 00:29 | `quantlab-web:events/bus.sqlite-shm`<br>`quantlab-web:events/bus.sqlite-wal`<br>`quantlab-web:events/2026-10-18.jsonl`<br>`quantlab-web:events/inbox/done/QuantLab Strategy.jsonl.1792297620` |
| 共享(TEAM_STATE) | 2 | 10-18 00:03 | 10-18 00:26 | `output/loop/TEAM_STATE_latest.md`<br>`output/loop/TEAM_STATE_latest.md.bak_intel_20261018` |
| 未定 | 9 | 10-17 23:58 | 10-18 00:28 | `output/relay_outage_backfill_queue.json`<br>`output/relay_outage_backfill.pid`<br>`output/remaining_queue_status.json`<br>`scripts/nightly_update.py` |
| 未定(无署名，疑 AI/主 Agent 串行守护) | 1 | 10-17 23:56 | 10-17 23:56 | `research/run_rss_guard.sh` |
| 环境(.pyc 重编译，非产出) | 1339 | 10-17 23:53 | 10-18 00:28 |  |

## 按顶层目录 × owner
| 仓库 | 顶层目录 | owner | 文件数 | 最早 | 最晚 |
|---|---|---|---|---|---|
| QuantLab | .venv_opt | 环境(.pyc 重编译，非产出) | 1229 | 10-17 23:54 | 10-17 23:56 |
| QuantLab | backups | 未定 | 1 | 10-17 23:58 | 10-17 23:58 |
| QuantLab | data | Data | 10928 | 10-17 23:55 | 10-18 00:29 |
| QuantLab | docs | AI | 7 | 10-18 00:00 | 10-18 00:18 |
| QuantLab | docs | Alpha | 3 | 10-17 23:54 | 10-18 00:04 |
| QuantLab | docs | Arch | 20 | 10-18 00:02 | 10-18 00:28 |
| QuantLab | docs | Beta | 1 | 10-18 00:24 | 10-18 00:24 |
| QuantLab | docs | Eng | 1 | 10-18 00:08 | 10-18 00:08 |
| QuantLab | docs | Intel | 5 | 10-18 00:08 | 10-18 00:26 |
| QuantLab | docs | Strategy | 8 | 10-18 00:09 | 10-18 00:26 |
| QuantLab | docs | 未定 | 1 | 10-18 00:24 | 10-18 00:24 |
| QuantLab | logs | Data | 33 | 10-17 23:55 | 10-18 00:28 |
| QuantLab | output | AI | 41 | 10-17 23:57 | 10-18 00:18 |
| QuantLab | output | Alpha | 12 | 10-18 00:01 | 10-18 00:26 |
| QuantLab | output | Arch | 1 | 10-18 00:19 | 10-18 00:19 |
| QuantLab | output | Beta | 33 | 10-18 00:14 | 10-18 00:18 |
| QuantLab | output | Data | 18 | 10-18 00:08 | 10-18 00:29 |
| QuantLab | output | Eng | 8 | 10-17 23:53 | 10-18 00:08 |
| QuantLab | output | Intel | 31 | 10-17 23:53 | 10-18 00:08 |
| QuantLab | output | Strategy | 468 | 10-17 23:59 | 10-18 00:29 |
| QuantLab | output | 主 Agent | 2 | 10-17 23:51 | 10-18 00:12 |
| QuantLab | output | 共享(TEAM_STATE) | 2 | 10-18 00:03 | 10-18 00:26 |
| QuantLab | output | 未定 | 5 | 10-18 00:24 | 10-18 00:28 |
| QuantLab | quantlab | 环境(.pyc 重编译，非产出) | 60 | 10-17 23:53 | 10-18 00:24 |
| QuantLab | research | AI | 6 | 10-17 23:55 | 10-18 00:19 |
| QuantLab | research | Alpha | 5 | 10-17 23:54 | 10-18 00:21 |
| QuantLab | research | Beta | 2 | 10-18 00:14 | 10-18 00:15 |
| QuantLab | research | Intel | 7 | 10-17 23:56 | 10-18 00:08 |
| QuantLab | research | Strategy | 8 | 10-18 00:04 | 10-18 00:22 |
| QuantLab | research | 未定(无署名，疑 AI/主 Agent 串行守护) | 1 | 10-17 23:56 | 10-17 23:56 |
| QuantLab | research | 环境(.pyc 重编译，非产出) | 43 | 10-17 23:54 | 10-18 00:24 |
| QuantLab | scripts | Data | 2 | 10-18 00:20 | 10-18 00:28 |
| QuantLab | scripts | 未定 | 2 | 10-18 00:28 | 10-18 00:28 |
| QuantLab | scripts | 环境(.pyc 重编译，非产出) | 7 | 10-17 23:55 | 10-18 00:28 |
| QuantLab | scripts_eng | Eng | 4 | 10-18 00:04 | 10-18 00:08 |
| quantlab-web | (根) | Web | 15 | 10-17 23:53 | 10-18 00:28 |
| quantlab-web | __pycache__ | Web | 5 | 10-17 23:53 | 10-18 00:08 |
| quantlab-web | events | Web(ql_bus 事件总线，多 agent 写入) | 10 | 10-18 00:00 | 10-18 00:29 |
| quantlab-web | export | Web | 53 | 10-17 23:59 | 10-18 00:28 |
| quantlab-web | screenshots | Web | 6 | 10-17 23:55 | 10-18 00:09 |
| quantlab-web | site | Web | 17 | 10-17 23:59 | 10-18 00:29 |
| quantlab-web | static | Web | 1 | 10-18 00:08 | 10-18 00:08 |

## 备注
- Data：`data/v2/asof_extend_tushare_202610/panels`、`data/v2/asof_extend_202610/panels` 各约 5.2–5.6k 个分块文件，是 10-15 和 10-16 两天的 nightly 补数（`logs/nightly/20261015_*`）；另有 tushare_raw 的 forecast、express、holdertrade 等，以及 relay_outage_backfill。
- output/loop：`TEAM_STATE_latest.md`（多 agent 共写）、`TEAM_STATE_latest.md.bak_intel_20261018`（Intel）、`alpha_labels.json`（Alpha）、`paper_daily_20261014/bridge_X2H/holdings_by_track_aum.parquet`（Eng）。
- quantlab-web：Web 看板 v4 的读源和新鲜度修复（`kline.py`、`freshness.py`、`snapshot.py`、`apis.py`），export、site 重新导出，截图。`events/`（ql_bus）由多个 agent 写入。
- `output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_v1_3.ok`（00:19，Arch 主会话签发，只授权 v1.3 生成权重）。v1.3 全池 wb 版权重 00:27 落盘（`_ckpt_v1_3_poolind/`）。本执行器没有创建任何标记文件。
- 未定：`backups/valuation/…`、`scripts/nightly_update.py(.bak)`、`output/relay_outage_backfill*`、`output/remaining_queue_status.json`，从内容看疑为 Data；`docs/v2/WEB_RESEARCH_15PCT_PATHS_ZH.md` 署名不明；`research/run_rss_guard.sh` 没有署名。
