# QuantLab Data 例程回执：A股日线收盘后更新 D=20261027 — **RERUN**（基线刷新后）

- 角色：QuantLab Data 执行器
- 时区：America/New_York（ET）
- 回执生成时刻（ET）：2026-10-27T06:58:50.872150-04:00
- live=false；promotion_approved=false；未启动 8787；未碰 moneyflow；未跑 trade_cal/sw；≠混叶33
- **outcome=PASS_PARTIAL**
- 前置：Arch 基线刷新回执 `6c1283db` MATCH；基线 `dfdc2555`→**`b7b39c2b`**；主令重跑 D=20261027
- 本文件为新回执；**不覆盖** BLOCKER 回执 `NIGHTLY_RECEIPT_20261027_ZH.md`（sha8 `6c576eb4`）

## 1. 启动前核验

| 项 | 结果 |
|---|---|
| /proc/94322 | **ABSENT** → 跳过 SIGCONT（无 T 态 remaining_after_stk_surv.py） |
| MemAvailable 起步 | ≈12.05 GiB ≥2GB，继续 |
| 冻结日历 trade_cal_sse_pit.parquet | sha=`fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41` **MATCH** |
| SSE 20261027 / 20261028 is_open | 均为 **1** |
| calendar/manifest.json | sha=`7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4` **MATCH** |
| Eng 日历 trade_cal.parquet | sha=`141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086` **MATCH** |
| 快照脚本 nightly_sha_scope_snapshot_20261018.py | sha8 **`0aa6c650`** 全长 `0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37` **MATCH** |
| 基线 nightly_sha_baseline_20261018_1022.txt | 全长 **`b7b39c2b3b7342748af1f00dcee594a9fa07653a5e8b3c8b574596d92638717b`** **MATCH**（新基线） |
| scope 文件 nightly_sha_scope_20261018.txt | 存在（与脚本配套） |
| 跑前快照 | `docs/v2/audit/nightly_20261027/sha_pre_rerun_20261027.txt` sha=`0246f748eba7437389d7296166bf00b1255a4abae93de555610825da06ff2e84` |
| 跑前 vs 基线 b7b39c2b | **RESULT OK**（tee：`sha_pre_rerun_vs_baseline_b7b39c2b.txt` sha=`49182bd5fb649e25565e2730f2663d8cdc5a845876bf969e0086f551c9e6c9d8`）；无 MUST_NOT_CHANGE 漂移 |

## 2. 备份 Eng 日历

- bak 已存在且 sha=**141078fa…** → **复用** `_recovery/data/nightly_20261027/trade_cal.parquet.bak`
- bak sha 全长：`141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086`（== PIN）

## 3. 第一次调用（daily_pull）

- 命令：`python3 scripts/nightly_update.py --date 20261027 --steps daily_pull`
- 日志：`logs/nightly/20261027_daily_pull.log`
- **rc=0**；summary status=ok；sec=**123**
- 开始约 ET 2026-10-27T06:26:32-04:00；结束约 ET 2026-10-27T06:28:35-04:00（盒本地 +0800 显示 18:28）

## 4. 日历比对 + 原子恢复

- 脚本：`docs/v2/audit/nightly_20261027/cal_compare_20261027.py`（MUST_OPEN=[20261027,20261028]）
- 命令：绝对路径 `--current` / `--backup` / `--out .../cal_compare_after_daily_pull.json`
- **RESULT IDENTICAL exit=0**：行数 9862；schema 全同；排序后四列逐格相同；两日 is_open=1
- 注：本次 daily_pull **未改写** Eng 日历（跑后仍为 141078fa…）；仍按规程原子恢复
- 恢复：同目录 tmp + `os.replace`；恢复后目标 sha=**141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086** **MATCH**
- 冻结日历 / calendar manifest 恢复前后均不变：`fa4260b8…` / `7ccc911e…`

## 5. 第二次调用（14 步，不含 daily_pull/trade_cal/sw）

- 命令：`python3 scripts/nightly_update.py --date 20261027 --steps index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness`
- 汇总日志：`logs/nightly/20261027_14steps.log`
- **进程 exit rc=0**；summary overall=**partial**；promotion_approved=false
- 约 ET 2026-10-27T06:28:52-04:00 → 2026-10-27T06:55:16-04:00

| 步骤 | status | sec | 备注 |
|---|---|---:|---|
| index_pull | ok | 144 | `20261027_index_pull.log` |
| adj_factor | ok | 1 | last=`20261027`；rows=4129344；rows_added=5580；days_added=[20261027] |
| bars | ok | 53 | `daily_ohlcv_raw_pit` rows=105705；last=`20261027`；**n_20261027=5570** |
| daily_basic | ok | 150 | 方案A 后 incremental 成功；full 表 rows=12348927；last=`20261027`；**n_20261027=5570** |
| index | ok | 0 | rows=18674；date_max=`2026-10-27`；n_20261027=5 |
| etf_daily_adj | ok | 101 | rows=1576797；last=`2026-10-27`；n_etfs_last_day=**1707** |
| eng_panels | ok | 79 | etf510300 last=`2026-10-27` rows=3502；asof_em/ts 延至 D；STATUS 日志记 partial（下游/warn） |
| mid_large_universe | ok | 3 | APPENDED `['2026-10-27']` n_members=**2511**；表 rows=5583027 |
| events | **partial** | 1038 | pledge/holder/express/forecast 有 OK；部分事件窗未齐至 D（可接受 partial） |
| hsgt | **partial** | 0 | skipped **RELAY_DOWN** fast-fail（可接受） |
| cyq | **partial** | 0 | skipped **RELAY_DOWN** fast-fail（可接受） |
| tier3 | **partial** | 0 | skipped **RELAY_DOWN** fast-fail（可接受） |
| bundle | ok | — | 复制既有小表/cyq 月包等 |
| freshness | ok | 2 | overall=ok；stale_tables=[]；warn_list 含 sw_pit/cyq/tier3*；expected_trade_date 字段见日志（SH 日历视角） |

## 6. 跑后快照

- 跑后：`sha_post_rerun_20261027.txt` sha=`85ad91865ba21b5eaf0e0ad154c4a309da1c13819962fe7ad2b0c1f74472f0ac`
- vs 基线 **b7b39c2b**：`sha_post_rerun_vs_baseline_b7b39c2b.txt` → **RESULT OK**
  - EXPECTED_CHANGE：`output/data_freshness_status.json`、`output/daily_update_status.json`
  - META_ONLY_CHANGE：`data/v2/tushare_raw/trade_cal.parquet`（sha 仍 141078fa）
  - **无 MUST_NOT_CHANGE 漂移**
- vs 跑前：`sha_post_vs_pre_rerun_20261027.txt` → **RESULT OK**（同上 EXPECTED/META）
- **fa4260b8…**（冻结日历）跑后不变
- **7ccc911e…**（manifest）跑后不变
- Eng PIN **141078fa…** 跑后不变

## 7. 落盘判定（不看 summary status）

`output/daily_update_status.json`：status=**ok**；target_trade_date=**2026-10-27**；live=false；promotion_approved=false；errors={}

| 表 | last==20261027 | 行数/成员 | 路径摘要 |
|---|---|---|---|
| daily_ohlcv_raw_pit (bars) | **是** | rows=105705；nD=5570 | data/v2/bars/… |
| adj_factor_2023h2plus | **是** | rows=4129344；nD=5580 | data/v2/adj/… |
| daily_basic_full_tushare | **是** | rows=12348927；nD=5570 | data/v2/valuation/… |
| index_daily_pit | **是** | rows=18674；nD=5 | data/v2/index/… |
| etf_daily_adj | **是** | rows=1576797；n_etfs=1707 | data/v2/etf/… |
| etf510300 panel | **是** | rows=3502 | data/v2/etf_510300/panels/sh.510300.parquet |
| asof_em panels | **是** | n_panels=5201；rows_added_this_run=5187 | data/v2/asof_extend_202610/panels |
| asof_ts panels | **是** | n_panels=5585 | data/v2/asof_extend_tushare_202610/panels |
| mid_large_members_pit | **是**（session/available 维；日志 APPENDED 2026-10-27×2511） | rows=5583027；n_members_last=2511 | data/v2/universe/… |
| dividend_by_exdate | **是**（自然日口径） | rows=15540 | corporate_actions/… |

**缺/弱（不阻断 PASS_PARTIAL）：**
- hsgt / cyq / tier3：RELAY_DOWN，未刷新至 D
- events：partial（forecast 等未全部齐到 D）
- `daily_basic_valuation_tushare.parquet` last 仍 20261009（例程主路径用 full 表，已齐）

## 8. 结论

- **outcome=PASS_PARTIAL**
- MUST_NOT_CHANGE vs 新基线 **b7b39c2b**：**OK**（跑前/跑后）
- Eng PIN / 冻结日历 / calendar manifest：**完好**
- 核心 REQUIRED 行情/估值/宇宙/asof/etf510300：**last==20261027 已齐**
- 需报 Leo：**是**（新交易日 20261027 已落盘；relay 侧 hsgt/cyq/tier3 仍 partial）
- live 仍 **false**；未改 TEAM_STATE；未自改基线；未绕 MUST_NOT_CHANGE
