# 补跑 10-14→10-16 运行 .ok 申请包（草案，未发送）

- 作者：QuantLab Data；起草 2026-10-18 10:20–10:50 ET。新文件。**未发送给 Arch，未申请 .ok，未运行任何补跑命令。**
- 依据：主 Agent 10-18 批准补跑的 6 个条件（①两次连续探测通、其中一次大分页；②与 10-19 同一套 --steps，不带 trade_cal、sw；③先报 Arch 拿运行 .ok，94322 停 T、留 ps 证据、严格串行；④跑前跑后核 sha；⑤16:00 ET 前跑完，绝不碰 16:40–18:40；⑥按实际行数与日期范围判，结果写进 TEAM_STATE）；Arch 10-18 消息（sha 范围扩大、.ok 申请须带的 5 项）。
- 本轮只读：Read / rg（显式路径）/ sha256sum / ls / stat，读了 nightly_update.py 全文与它调用的全部脚本、logs/nightly 下 10-14..10-16 的 summary 与步骤日志、output 下两份状态 JSON、output/relay_outage_backfill_queue.json、tier3 与 cyq 的 manifest。没有读任何 parquet 内容（只对 sha 范围内文件算了 sha256），没有 import 项目代码，没有联网。
- live=false，promotion_approved=false，strategy_promotion=false。

## 0. 结论先行（请 Arch 先看这一节）
1. **按任务原样的 15 步 × 3 次（方案 O）不安全，Data 不建议申请。** 主要原因（详见 §4）：
   - F1 `daily_pull`（tier1_pull.py extend，L83–95）每次都无条件重写 `data/v2/tushare_raw/trade_cal.parquet`（纸面 Eng 日历，MUST_NOT_CHANGE），10-14/15/16 三份日志都写着「cal refreshed」。按条件④它会直接触发停止。**这一条同样适用于 10-19 05:55 ET 日更**（见 §4 F1 与 §14 Q1，需要 Arch 与主 Agent 在今天定）。
   - F2 `daily_basic`（tier1_materialize.materialize_daily_basic(end=日期)）是 2014 起全量重建，只收 ≤ --date 的原始文件：用 --date 20261014 跑会把 daily_basic_full_tushare 从 10-16 **截断到 10-14**，直到第三次才补回；中途按 16:00 规则放弃就停在截断状态。每跑一次还会多一份备份并把 backups/valuation 修剪到 5 份。已测峰值 RSS **2.14GB**（logs/nightly/daily_basic_rebuild_20261014b.log L31：maxrss_kb=2143204），超过 1.5GB 上限。
   - F3 `events` 用 QL_TODAY=--date 重算一年窗口：forecast_1y / express_1y / holder_trade_1y 现在窗口到 20261016，用 20261014 跑会退回到 20261014；forecast_manifest_declare.py 每次还重写三份 forecast manifest 和 docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md。
   - F4 `tier3` 对 10-14、10-15 已有完整快照，重跑会非原子地覆盖（to_parquet 直写），而这两天在队列里已是 done。
   - F5 状态回退：eng_panels 以 target_trade_date=--date 重写 output/daily_update_status.json，前两次运行会把 target 从 2026-10-16 改回 10-14 / 10-15。
   - F6 时长：每次约 53 分钟以上（tier3 一步 25–41 分钟），三次约 2.7–3 小时，加上条件①最早 12:15 才满足，基本赶不上 16:00。
2. **实际缺口只有中转步骤**（§1）：日线核心表已在 10-18 00:19–00:48 ET 的运行里补到 10-16（status ok、freshness ok）。队列里 pending 的是 cyq 10-14/15/16、tier3 10-16，以及 sw 10-14/15/16（sw 按条件②不跑）。
3. **建议改为最小补跑集（方案 R）**：三次串行，`--date 20261014 --steps cyq`、`--date 20261015 --steps cyq`、`--date 20261016 --steps cyq,tier3,bundle,freshness`。方案 R 不写 sha 范围内任何 MUST_NOT_CHANGE 文件，预计 30–50 分钟。它不是「与 10-19 同一套 --steps」，偏离条件②，**须主 Agent 书面同意**后再交 Arch；未获同意就不跑，只保 10-19 05:55 日更。

## 1. 当前状态（只读核对，10:20–10:30 ET）
| 项 | 值 | 依据 |
|---|---|---|
| 原始日线 | tushare_raw/{daily,daily_basic,adj_factor,stk_limit,suspend_d}/20261014、15、16.parquet 都在 | ls |
| output/daily_update_status.json | target_trade_date 2026-10-16，status ok，各表 last_date 2026-10-16，finished_at 2026-10-18T00:23:31-04:00 | Read |
| output/data_freshness_status.json | expected_trade_date 20261016，overall ok，stale_tables 空，generated_at_et 2026-10-18T00:48:36-04:00 | Read |
| 10-14 summary | cyq partial（RELAY_DOWN），tier3 ok，bundle ok，freshness ok（只剩这 4 步的记录） | logs/nightly/20261014_summary.json |
| 10-15 summary | sw partial、cyq partial，其余 ok（tier3 2434 秒） | 20261015_summary.json |
| 10-16 summary | sw fail rc=-15（04:30 ET 按主 Agent 终止）、cyq partial、tier3 partial，其余 ok | 20261016_summary.json |
| 补拉队列 pending | sw 10-14/15/16、cyq 10-14/15/16、tier3 10-16；hsgt 与 tier3 10-14/15 为 done | output/relay_outage_backfill_queue.json L21–166 |
| cyq 原始 | tushare_raw/cyq_perf 最新 20261013；cyq_perf_202610.parquet：22238 行、4 天、range 20261008–20261013 | ls；data/v2/cyq/manifest.json |
| tier3 | 6 类都有 20261013–20261015，没有 20261016；concept_ths_index 只有 20261013.parquet.sample_stub（中转只回样例） | ls |
| 中转探测 | 10:15:54 ET trade_cal 200、7 行、1.94 秒；大分页接口尚未测 | docs/v2/audit/relay_probe_20261018/probe_log.csv |

## 2. nightly_update.py 行为核对（sha ec079d56…d838636，全文 139 行已读）
- **步骤名**（steps_for L26–43）：trade_cal、daily_pull、index_pull、adj_factor、bars、daily_basic、index、etf_daily_adj、eng_panels、mid_large_universe、events、hsgt、sw、cyq、tier3、bundle、freshness。任务给的 15 个名字全部存在；未知名字会在 L106/L107 的 S[k] 处 KeyError 退出且不写 summary。
- **--date**（L99）：缺省为上海当天。传入后 steps_for(d) 生成命令，并设环境变量 QL_TODAY=YYYY-MM-DD、TOP10_START=(年−1)+月日、TOP10_END=YYYYMMDD、CHUNK_DAYS=30（L44、L102）。
- **--steps**（L101）：逗号分隔，按给定顺序执行，不排序、不去重。
- **不看 --date 的步骤**：index_pull（拉 20140101–20261231 全量）、index（全量物化）、freshness（data_freshness_status.py 用当前上海时间，nightly 不传日期）、cyq 只取 --date 的年月（整月，且只拉「上海今天之前」的开市日），hsgt 只经 TOP10_* 环境变量。daily_pull 的日历刷新与 --date 无关。
- **中转步骤**（L85、L109–112）：hsgt、cyq、tier3、sw 先调 relay_health.relay_up()（缓存 output/relay_health.json 5 分钟，过期即探测并重写该文件）；不通则记 partial 并 register_backfill（只追加不存在的队列项，不会把已有项改成 done）。
- **退出码**（L119–120）：rc 0 或 2 记 ok，3 记 partial，其余 fail；events 另看 light_event_windows_summary.json 的 n_fails（L121–125）。**cyq_perf_monthly.py 与 tier3_daily_snapshot.py 在单日失败或单项 blocked 时仍退出 0**，所以 ok 不代表成功，必须看日志与 manifest（§6）。
- **summary 合并**（L130–137）：带 --steps 且当日 summary 已存在时，读旧 steps 再用本次结果覆盖同名步骤，overall 按合并后全部步骤重算。所以 10-15、10-16 的 overall 会因为 sw 一直是 partial / fail（本次不跑 sw）。**判定只看本次各步，不看 overall。** 若旧 summary 解析失败（L135 except），会静默退化为只写本次步骤；logs/nightly/summary_bak_20261018/ 已有 10-13..10-16 的备份。summary 非原子写（L137 write_text）。
- **日志**：每步追加到 logs/nightly/<日期>_<步骤>.log（L114–117，append），每条命令前写一行「=== <本地时间> <命令>」。判定时只看本次新增的那一段。
- **--dry-run**（L106）：只打印各步命令，不跑子进程、不探测中转、不写 summary（L137 有 if not a.dry_run）；建议作为第 0 步留证据。
- 内存：L113 wait_mem 只在 MemAvailable < 2GB 时暂停，不管 RSS。

## 3. 逐步核对（方案 O 的 15 步；脚本 sha 见 §12）
| 步骤 | 命令（steps_for） | 用不用 --date | 写什么 | 风险 |
|---|---|---|---|---|
| daily_pull | tier1_pull.py extend D | 用（拉 ≤D 缺的日子，已有文件跳过） | tushare_raw/<api>/D.parquet；**无条件重写 tushare_raw/trade_cal.parquet**（L83–95） | **F1，MUST_NOT** |
| index_pull | tier1_pull.py index | 不用（20140101–20261231 全量） | tushare_raw/index_daily_*.parquet | 中，全量重写，与本次缺口无关 |
| adj_factor | adj_factor_incr.py --date D | 用，只追加 | adj/adj_factor_2023h2plus*.parquet 与 manifest | 低，已到 10-16，应为 0 新增 |
| bars | materialize_bars(start=月初, end=D) | 用 | 当月窗口替换 + 约 5582 个 asof_extend_tushare 面板，非原子 | 中高，F7 |
| daily_basic | materialize_daily_basic(end=D) | 用，全量重建到 D | daily_basic_full_tushare + backups/valuation（保留 5 份） | **F2，截断，RSS 2.14GB** |
| index | materialize_index() | 不用 | index/index_daily_pit*.parquet | 中，全量重写 |
| etf_daily_adj | etf_daily_adj_incr.py --date D | 用 | etf/etf_daily_adj.parquet，status.tables.etf_daily_adj | 中，F5 |
| eng_panels | eng_daily_panels.py --date D | 用 | 510300/X2/分红面板；**output/daily_update_status.json target=D** | **F5，状态回退** |
| mid_large_universe | mid_large_universe_incr.py --date D | 用，只追加 | universe/mid_large_members_pit.parquet，status.tables | 中，F5 |
| events | _light_event_windows_pull.py；forecast_manifest_declare.py | 用 QL_TODAY | events 一年窗口表、三份 forecast manifest、docs/v2/DATA_FORECAST_HISTORY_RECEIPT_ZH.md | **F3，窗口回退，改文档** |
| hsgt | fill_hsgt_top10_extend.py | 只经 TOP10_START/END | northbound/hsgt_top10_daily_2018plus.parquet | 低（队列已 done） |
| cyq | cyq_perf_monthly.py 202610 202610 | 只用年月 | tushare_raw/cyq_perf/<日>.parquet，cyq/cyq_perf_202610.parquet，cyq/manifest.json | 低，**真缺口** |
| tier3 | tier3_daily_snapshot.py --date D | 用 | tier3_daily/<6 类>/D.parquet 与 manifests/D.json，非原子 | 10-14/15：F4 覆盖；10-16：**真缺口** |
| bundle | nightly 内部函数 bundle(d)（L67–83） | 只用于 tier3 文件名 | output/data_v2_bundle/ 下小表副本（copy2） | 低（会把旧版 SW L1 PIT 再复制一次，字节不变） |
| freshness | data_freshness_status.py | 不用（当前上海时间） | output/data_freshness_status.json（L9） | 低，EXPECTED_CHANGE |

## 4. 使计划不安全的事项（flags）
- **F1 trade_cal.parquet 被 daily_pull 重写（阻断级）**：tier1_pull.py extend 分支 L83–95 每次重拉 trade_cal 并 to_parquet 覆盖 data/v2/tushare_raw/trade_cal.parquet（基线 sha 141078fa…）。即使内容相同，parquet 写出的字节和 mtime 都可能变，按条件④必须停。10-19 05:55 ET 日更默认全步骤，也会写它，**与 Arch「10-19 前任何写入须先报」直接冲突**。Data 的建议（未实施，不改代码）：10-19 日更改用不含 daily_pull 的 --steps，或先由 Arch 定是否给 tier1_pull.py 加只读开关（属代码变更，需单独 .ok）。
- **F2 daily_basic 截断与内存（阻断级）**：见 §0。另外 nightly 的 wait_mem 只看 MemAvailable，不限 RSS。
- **F3 events 窗口回退 + 改现有文档（阻断级）**：违反「不改现有文档」，且 forecast/express/holder/pledge 的窗口终点会退回。
- **F4 tier3 覆盖已完成的 10-14/10-15（高）**：覆盖写非原子；若中转只回部分数据，行数会比现有少（10-14：dc_member 95022 行，news 1776 行）。
- **F5 daily_update_status.json 回退（高）**：Eng 闸门读的是它和 freshness；运行间隙它会显示 target 2026-10-14 / 10-15。
- **F6 时长（高）**：见 §9，方案 O 赶不上 16:00。
- **F7 bars 非原子重写约 5582 个面板（中）**：中途被 16:00 规则打断会留下半写文件。
- **F8 中转步骤静默 ok（中）**：cyq 与 tier3 失败也退出 0，nightly 记 ok；只能按 §6 的日志与 manifest 判。
- **F9 cyq 的日期取自 trade_cal.parquet（中）**：cyq_perf_monthly.py 用 tushare_raw/trade_cal.parquet 的开市日，并只取「上海今天之前」的日子；今天是 10-18（周日），所以 --date 20261014 那一次就会把 10-14、10-15、10-16 三天一起拉。第二、三次的 cyq 预期为 0 新增（已有日跳过）。三次 cyq 是为满足「每个日子一次」的形式，实际上第一次就够；Arch 可以批准只跑一次。
- **F10 summary overall 永远 partial（低）**：sw 不跑，合并后 overall 必为 partial；判定只看本次步骤。
- **F11 94322 停 T 期间（低）**：94322 写 tushare_raw/fund_portfolio_dh/ 与 events 下的 fund_portfolio 表，不在 sha 范围内；停 T 不影响范围内文件。停的时长按 §9 约 1 小时。

## 5. 命令
### 5.1 方案 O（任务原样，**Data 不建议申请**，只为完整列出）
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261014 --steps daily_pull,index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness </dev/null >> logs/nightly/backfill_20261018_run1.out 2>&1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261015 --steps daily_pull,index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness </dev/null >> logs/nightly/backfill_20261018_run2.out 2>&1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261016 --steps daily_pull,index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness </dev/null >> logs/nightly/backfill_20261018_run3.out 2>&1
```
按 F1，第一次运行跑完 daily_pull 后 trade_cal.parquet 就会变化；方案 O 即使获批，也应在 run1 之后的 sha 核对处停下。

### 5.2 方案 R（Data 建议；须主 Agent 同意偏离条件②）
第 0 步（只打印，不跑子进程、不写 summary）：
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261014 --steps cyq --dry-run </dev/null
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261015 --steps cyq --dry-run </dev/null
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261016 --steps cyq,tier3,bundle,freshness --dry-run </dev/null
```
正式三次，严格串行（前一次进程退出、判定完再起下一次）：
```
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261014 --steps cyq </dev/null >> logs/nightly/backfill_20261018_run1.out 2>&1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261015 --steps cyq </dev/null >> logs/nightly/backfill_20261018_run2.out 2>&1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 scripts/nightly_update.py --date 20261016 --steps cyq,tier3,bundle,freshness </dev/null >> logs/nightly/backfill_20261018_run3.out 2>&1
```
每次在后台起，记下 $! 作为本次 nightly 的确切 PID（只有这个 PID 和它的直接子进程可以由 Data 结束，见 §10）。
方案 R 预期改动的文件：tushare_raw/cyq_perf/20261014、15、16.parquet（新增），cyq/cyq_perf_202610.parquet 与 cyq/manifest.json，tier3_daily/<6 类>/20261016.parquet 与 manifests/20261016.json（新增），output/data_v2_bundle/ 下 cyq 与 tier3 副本，output/data_freshness_status.json，output/relay_health.json，logs/nightly/2026101{4,5,6}_summary.json 与对应步骤日志。可能追加 output/relay_outage_backfill_queue.json（只在中转不通时）。**没有一个在 MUST_NOT_CHANGE 范围内。**

## 6. 每步成功判定（按实际行数和日期范围，不看 status 字样）
### 6.1 方案 R
| 运行 | 步骤 | 成功（全部满足） | 失败 / 部分 |
|---|---|---|---|
| run1 | cyq | ①本次 summary steps.cyq.status=ok 且没有 skipped=RELAY_DOWN；②logs/nightly/20261014_cyq.log 本次段落里有 20261014、20261015、20261016 三行「日期 行数」，每行 ≥ 5000（现有 4 天平均约 5560 行/天），没有 FAIL，且末尾汇总 fails=[]；③data/v2/cyq/manifest.json months.202610：days=7、range=[20261008, 20261016]、rows 约 38900（22238 + 3×约 5560，允许 ±3%）、codes ≥ 5564；④tushare_raw/cyq_perf/2026101{4,5,6}.parquet 存在且各 > 10000 字节 | 任一天在 fails 里，或 days < 7：记 partial，保留 pending，不重试，写 TEAM_STATE |
| run2 | cyq | 预期 new_days=0（三天已在 run1 拉到）；manifest 202610 与 run1 后一致（days=7，range 不变）；日志无 FAIL | run1 有天失败时，run2 是唯一一次补拉机会；仍失败就停 |
| run3 | cyq | 同 run2 | 同上 |
| run3 | tier3 | data/v2/tier3_daily/manifests/20261016.json：concept_dc_index ok 且 rows 900–1200（10-14：1033，10-15：1035）；concept_dc_member ok 且 rows 80000–110000（95022 / 94515）；news ok 且 rows ≥ 1000（1776 / 1651）；anns 与 research_report 为 ok（10-15 只有 6 行与 11 行，0 行记录但不算失败）；concept_ths_index 允许 blocked（自 10-13 起中转只回样例，已知）；各 kind 的 20261016.parquet 存在，行数与 manifest 相同（读 parquet 元数据核对，不读内容） | dc_index / dc_member / news 任一 blocked 或行数低于下限：记 partial，tier3 10-16 留 pending |
| run3 | bundle | summary steps.bundle.files 含 cyq/cyq_perf_202610.parquet 与 tier3_daily/*/20261016.parquet；副本 sha 等于源文件 | 少文件：记录，不重跑 |
| run3 | freshness | output/data_freshness_status.json：generated_at_et 是本次时间，expected_trade_date=20261016，overall=ok；cyq 行 last_date ≥ 2026-10-16（若脚本有此表） | overall 不是 ok：记录 stale_tables 原样，不改 |
| 全部 | sha | §8 compare 退出码 0（只允许 EXPECTED_CHANGE 两个文件变化） | 退出码 1 或 2：立即停（见 §10） |

### 6.2 方案 O（仅列判定口径，若 Arch 坚持）
| 步骤 | 判定 |
|---|---|
| daily_pull | 日志 EXTEND 列出的日子 ⊆ 已有原始文件（应全部 skip）；**trade_cal.parquet sha 变化即停** |
| index_pull | 日志里每个指数代码的 max 日期 ≥ 20261016，行数不少于跑前 |
| adj_factor | manifest last_date=2026-10-16，rows_added=0 |
| bars | BARS meta date_max=2026-10-16、行数 66723 不变 |
| daily_basic | date_max 必须等于本次 --date；run1、run2 后会截断（F2），只有 run3 后恢复 2026-10-16 |
| index | index_daily_pit date_max ≥ 2026-10-16 |
| etf_daily_adj / eng_panels / mid_large_universe | status.tables.<表>.last_date 等于 --date（F5），run3 后回到 2026-10-16 |
| events | light_event_windows_summary.json n_fails=0；窗口终点等于 --date（F3） |
| hsgt | hsgt_top10 max(trade_date) ≥ 20261016，行数不减 |
| cyq / tier3 / bundle / freshness | 同 §6.1；tier3 10-14、10-15 行数不得低于现有（F4） |

## 7. 94322 停 T 与恢复（任务未授权 Data 碰 94322 以外的任何进程）
- 当前（10:30:04 ET 只读）：`PID 94322 PPID 94319 STAT Ssl ELAPSED 09:06:23 RSS 128504 python3 scripts/acquire/remaining_after_stk_surv.py`。10:22:16 ET 记录为 S。
- 拿到运行 .ok 后，第一次运行前：
```
ps -o pid,ppid,stat,etime,rss,args -p 94322 </dev/null
kill -STOP 94322
ps -o pid,ppid,stat,etime,rss,args -p 94322 </dev/null
cut -d" " -f1-3 /proc/94322/stat
```
  须看到 STAT 为 T（/proc 第 3 列为 T）才继续；不是 T 就不跑，原样记录。STOP 前后输出连同 ET 时间写入回执。
- 第三次运行与跑后 sha 核对完成后（不论成败，也包括 §10 中止的情形）：
```
kill -CONT 94322
ps -o pid,ppid,stat,etime,rss,args -p 94322 </dev/null
cut -d" " -f1-3 /proc/94322/stat
```
  须看到 STAT 回到 S 或 R。
- 不用 pkill / killall，不碰 94319（父进程）。94322 若在停 T 前已自行退出，记录 ps 空输出，不做其他处理。

## 8. sha 跑前 / 跑后核对
- 范围清单：docs/v2/audit/nightly_sha_scope_20261018.txt，sha256 b24a4a88b23efd8d1663238e6e590984afa08c719b5d397f589a87d9fc6319be，11305 字节，167 项（EXPECTED_CHANGE 2 项：两份 output 状态 JSON；MUST_NOT_CHANGE 165 项：calendar/trade_cal_sse_pit.parquet 与 manifest.json、tushare_raw/trade_cal.parquet、两份 announcements parquet、三份 SW L1 表、paper_import_closure.json 及其 156 个文件）。
- 参考基线：docs/v2/audit/nightly_sha_baseline_20261018_1022.txt，sha256 dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c，41921 字节，10:22:07 ET，167 个文件共 144952877 字节，156 个闭包 pin 全部吻合。**它只作参考，运行当天须在 94322 停 T 之后、run1 之前重新取一次 BEFORE。**
- 工具：docs/v2/audit/nightly_sha_scope_snapshot_20261018.py（与 /tmp/arch1018/sha_scope_snapshot.py 同字节，sha256 0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37；只用标准库，内部调用 sha256sum 显式文件列表，不 import 项目代码，不读 data 目录以外的东西，每个文件同时记 size、mtime_ns、ctime_ns、inode）。
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py docs/v2/audit/nightly_sha_scope_20261018.txt /tmp/arch1018/backfill_before.txt </dev/null
# 每次运行之后：
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py docs/v2/audit/nightly_sha_scope_20261018.txt /tmp/arch1018/backfill_after_runN.txt </dev/null
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py --compare docs/v2/audit/nightly_sha_scope_20261018.txt /tmp/arch1018/backfill_before.txt /tmp/arch1018/backfill_after_runN.txt </dev/null
```
- 退出码：0 = 只有 EXPECTED_CHANGE 变化，可进入下一次运行；1 = MUST_NOT_CHANGE 有变化，**立即停，不起下一次运行，94322 照常 CONT，报 Arch**；2 = 文件缺失或用法错误，同样停。
- 每次运行后都核（三次各一次），不是只核最后一次；这样任何一次越界都能定位到具体运行。快照文件结束后作为新文件装进 docs/v2/audit/（不改现有文档）。
- 除 sha 外另核：daily_update_status.json 的 target_trade_date 仍为 2026-10-16（方案 R 不碰它，它在 EXPECTED_CHANGE 里只是保守列入）。

## 9. 内存与时长估计
| 项 | 方案 R | 方案 O | 依据 |
|---|---|---|---|
| nightly 父进程 | < 100MB | 同 | 只调度子进程 |
| cyq | 未实测；估计峰值 < 500MB（202610 整月拼接约 39000 行 × 十余列） | 同 | cyq 自 10-14 起从未成功跑过，没有 RSS 记录 |
| tier3 | 未实测；估计 < 600MB（dc_member 约 95000 行最大） | 同，三次 | 历史日志无 RSS |
| daily_basic | 不跑 | **2.14GB 实测**，超 1.5GB | daily_basic_rebuild_20261014b.log L31 |
| events | 不跑 | 未实测 | — |
| cyq 时长 | run1 约 1–5 分钟（3 天 × 单次调用 + 整月拼接），run2/run3 < 1 分钟 | 同 | 估计 |
| tier3 时长 | 25–41 分钟 | 每次同量级 | 10-15：2434 秒；10-14：1502 秒 |
| 中转探测 | 每个中转步骤 ≤ 8 秒（relay_health 缓存 5 分钟） | 同 | relay_health.py |
| 单次合计 | run1 ≤ 6 分钟，run2 ≤ 2 分钟，run3 30–45 分钟 | 约 53 分钟 + cyq | summary 各步 sec |
| 总计（含三次 sha 快照，每次 < 1 分钟） | **约 40–55 分钟** | **约 2.7–3 小时** | |
- RSS 监控（只读，Data 自己的进程）：每 15 秒记一次 nightly 的直接子进程 `ps --ppid <nightly PID> -o pid=,rss=,etimes=,args= </dev/null`，写到 /tmp/arch1018/backfill_rss_runN.log；任何子进程 RSS > 1.5GB（1572864 KB）即按 §10 中止。/usr/bin/time 未安装，不能拿到子进程 maxrss，采样只是近似峰值，回执里如实写。

## 10. 时间规则与中止
- 前提时间线（例）：约 11:15 ET 第一次探测、约 12:15 ET 第二次探测（§11）→ 两次都过后发 .ok 申请 → Arch .ok 落盘后开始。Data 自己的截止：**13:30 ET 还没拿到 .ok 就放弃今天的补跑**，只保 10-19 05:55。
- **最晚开始**：run3（含 tier3）必须在 **15:00 ET** 前起；run1 必须在 14:45 ET 前起。超过就不起，剩余项保持 pending。
- **16:00 ET 硬中止**：15:55 ET 时若仍有运行未结束，Data 只对自己起的那个 nightly PID 的当前直接子进程（运行时 ps --ppid 记下的确切 PID）发 `kill -TERM <PID>`，再对 nightly PID 本身发 `kill -TERM <PID>`；每一步前后都留 ps 输出。不用 pkill / killall。中止后：照常做跑后 sha 快照与 compare，照常 kill -CONT 94322；tier3 若被打断，20261016 的半写文件不删，原样报 Arch（tier3 是非原子写）。
- 16:40–18:40 ET 绝不运行任何东西（包括 sha 快照）。
- 一次只跑一个重任务：运行期间 Data 不起任何别的 Python 进程（sha 快照在两次运行之间做）。
- 遇到以下任一情况立即停、不起下一次：compare 退出码非 0；本次某步 status 不是 ok；RSS 超限；中转探测失败（summary 里出现 RELAY_DOWN fast-fail）。

## 11. 中转探测证据（占位，待补）
探测记录追加到 docs/v2/audit/relay_probe_20261018/probe_log.csv（表头 ts_et,api,params,elapsed_s,http_status,rows,error），每次探测须用单独的只读探测 .ok。
| 次 | 计划时间 ET | 接口 | 参数 | 耗时 | HTTP | 行数 | 结论 |
|---|---|---|---|---|---|---|---|
| 已有 | 10:15:54 | trade_cal | exchange=SSE 小区间 | 1.94 秒 | 200 | 7 | 通（小接口，不计入条件①） |
| P1 | 约 11:15 | trade_cal | 同上 | 待补 | 待补 | 待补 | 待补 |
| P1 | 约 11:15 | index_member_all | 第 1 页（大分页） | 待补 | 待补 | 待补 | 待补 |
| P2 | 约 12:15 | trade_cal | 同上 | 待补 | 待补 | 待补 | 待补 |
| P2 | 约 12:15 | index_member_all 或 cyq_perf | 第 1 页 | 待补 | 待补 | 待补 | 待补 |
条件①：P1、P2 两次连续都通，且至少一次大分页接口返回完整一页。任一次失败就不申请运行 .ok。注意 index_member_all 属 SW 数据源，只做探测，不落盘到 sw_l1_pit / sw_pit。

## 12. 涉及脚本的 sha256（10:30 ET 读取；运行 .ok 签发时须再核一次，任一不同即作废）
| 文件 | sha256 | 方案 R 会执行 |
|---|---|---|
| scripts/nightly_update.py | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 | 是 |
| scripts/acquire/relay_health.py | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f | 是（import） |
| scripts/acquire/cyq_perf_monthly.py | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f | 是 |
| scripts/acquire/tier3_daily_snapshot.py | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 | 是 |
| scripts/acquire/data_freshness_status.py | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 | 是 |
| quantlab/data_sources/tushare_proxy.py | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 | 是（cyq、tier3 import） |
| scripts/acquire/tier1_pull.py | b630bca24fe7c86a656cf375c4aa1f543d98dac86178ba7ae50881cf4dbeb711 | 否（方案 O） |
| scripts/acquire/adj_factor_incr.py | 723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad | 否 |
| scripts/acquire/tier1_materialize.py | e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb | 否 |
| scripts/acquire/etf_daily_adj_incr.py | ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4 | 否 |
| scripts/acquire/eng_daily_panels.py | a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be | 否 |
| scripts/acquire/mid_large_universe_incr.py | fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b | 否 |
| scripts/acquire/_light_event_windows_pull.py | f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71 | 否 |
| scripts/acquire/forecast_manifest_declare.py | f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731 | 否 |
| scripts/acquire/fill_hsgt_top10_extend.py | 36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918 | 否 |
| scripts/acquire/tushare_relay_pull.py | 0a1d1ce7502989b63dcbcbb2378508627afb5c7eaa0573250d57650680c666d1 | 否 |
| scripts/acquire/trade_cal_pit.py | 90e3df43ca13e9df75e831ae702b5d4c137efa1168ec52133d1b37b841e72f54 | 否（条件②不跑） |
| scripts/acquire/sw_pit_refresh.py | a18684feb3a0816881a81ff1e6d3fe3d60a927e6ff9655c99ca36c50fa2196e9 | 否（条件②不跑） |
| docs/v2/audit/nightly_sha_scope_snapshot_20261018.py | 0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37 | 是（核对工具） |

## 13. 回执内容（运行后由 Data 写新文件 docs/v2/audit/BACKFILL_1014_1016_RECEIPT_ZH.md，并写 TEAM_STATE）
- 运行 .ok 的路径与 sha、归档名；两次探测行；94322 STOP 前后与 CONT 后的 ps 输出与 ET 时间；
- 每次运行的确切 PID、开始/结束 ET、各步 status 与 sec、§6 每条判定的实测值（行数、days、range）；
- BEFORE 与三份 AFTER 快照的路径与 sha、三次 compare 的输出与退出码；RSS 采样最大值；
- 仍为 pending 的项（至少 sw 10-14/15/16），以及队列文件是否需要把 cyq / tier3 改成 done（队列改动另报，本次运行不改）。

## 14. 待 Arch / 主 Agent 定的问题
- **Q1（今天就要定）**：10-19 05:55 ET 日更若照常跑全步骤，daily_pull 会重写 tushare_raw/trade_cal.parquet（F1）。是 (a) 10-19 日更改用不含 daily_pull 的 --steps（日线将停在 10-16，10-19 开盘后再补），(b) 接受该文件变化并把它从 MUST_NOT_CHANGE 改为 EXPECTED_CHANGE（需要 Arch 改范围），还是 (c) 先给 tier1_pull.py 加只读日历开关（代码变更，另走 .ok）？
- Q2：方案 R 偏离条件②（不是 10-19 的同一套 --steps），主 Agent 是否同意？
- Q3：cyq 是否只跑 run1 一次即可（F9）？Data 倾向于保留三次以对齐「逐日」的形式，但 run2/run3 预期无新增。
- Q4：tier3 的 concept_ths_index 在 10-16 预期 blocked，是否接受为「已知缺口」而不算 tier3 失败？
- Q5：sha 范围里 daily_update_status.json 被列为 EXPECTED_CHANGE，方案 R 实际不写它；是否改为本次按 MUST_NOT_CHANGE 核（更严）？Data 建议更严，但工具按范围文件分类，需要 Arch 出一份本次专用范围文件（新文件）。
