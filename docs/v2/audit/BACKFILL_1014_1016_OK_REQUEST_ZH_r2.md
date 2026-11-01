# 补跑 10-14→10-16 运行 .ok 申请包 r2（方案 R 修订版；草案，未发送）

- 作者：QuantLab Data；生成时间 2026-10-18T11:01:01-04:00（ET，date 生成）。新文件，不改 r1（docs/v2/audit/BACKFILL_1014_1016_OK_REQUEST_ZH.md，122277e2）。
- **未发送给 Arch，未申请 .ok，未运行任何补跑命令，未碰 94322。** 本轮只读：Read / rg（显式路径）/ ls；没读 parquet 内容，没对 data/ 文件算 sha，没 import 项目代码。
- 依据：r1；主 Agent 书面同意方案 R（10:44 转达）与补充三点；Arch 审查 docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）§3、§4；Arch 10:52 补充（cyq 只跑一次、RSS 停止线 1484800）。
- live=false，promotion_approved=false，strategy_promotion=false。

## 0. 与 r1 的差异（一览）
| 项 | r1 | r2 | 依据 |
|---|---|---|---|
| 调用次数 | 三次（cyq×3） | **两次**：run1 只跑 cyq，run2 跑 tier3,bundle,freshness | Arch §4.2 / Q3、10:52 |
| cyq 调用 | --date 20261014/15/16 各一次 | **一次，--date 20261016 --steps cyq**（代码依据见 §1） | 本文 §1 |
| RSS 停止线 | 1572864 kB | **1484800 kB** | Arch §4.2 注意 3 |
| 解释器 | python3 | **/usr/bin/python3**（3.13.5，pandas 3.0.6，pyarrow 26.0.0） | Arch §4.2 注意 4 |
| sha 范围 | b24a4a88 | **补跑专用** docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt（579c8605…） | Arch §2 要求 1 |
| 备份 | 无 | cp -p 到 _recovery/data/backfill_1014_1016/ + SHA256SUMS（§4） | Arch §4.3 |
| 判定 | 约数（±3%） | Arch §4.4 精确口径（§6） | Arch §4.4 |
| 快照 | v1 | v1 + 三条补偿（§5） | Arch §3 |

## 1. cyq 正确调用：代码怎么说
- nightly_update.py（ec079d56）L24、L40：cyq 命令是 `cyq_perf_monthly.py <ym> <ym>`，ym = --date 的前 6 位。**--date 只决定月份**，20261014 / 20261015 / 20261016 三者效果相同，都是 `cyq_perf_monthly.py 202610 202610`。
- cyq_perf_monthly.py（6aae6c1b）L15-18 days(m)：取 data/v2/tushare_raw/trade_cal.parquet 中 202610 的开市日，且 `d < 上海今天`（d == 今天只在上海 19 点后计入）。今天 ET 12:00 前上海是 10-18，ET 12:00 后上海是 10-19 00:00 起；两种情况下 20261014、20261015、20261016 都 < 今天，20261019 要到 10-19 07:00 ET（上海 19:00）后才计入，今天补跑不会碰到。
- L43-44：原始文件已存在且 > 10000 字节就跳过。现有 20261008 / 09 / 12 / 13 都约 162 KB（ls），会跳过；20261014 / 15 / 16 不存在，会拉。**所以一次调用预期 new_days=3。**
- L40、L52-58：只重建参数月份 202610；L61-66 manifest 用 update 合并，202601-202609 条目原样保留（但整份文件重写，built 必变）。
- 选 --date 20261016 的原因：日志写到 logs/nightly/20261016_cyq.log（新文件），summary 合并进 20261016_summary.json；**10-14、10-15 的 summary 不被写**（已列为 MUST_NOT_CHANGE）。
- 结论命令（严格串行，前一次退出并判定完再起下一次）：
```
cd /workspace/QuantLab
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq </dev/null >> logs/nightly/backfill_20261018_run1.out 2>&1 &
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps tier3,bundle,freshness </dev/null >> logs/nightly/backfill_20261018_run2.out 2>&1 &
```
  每次后台起，`NPID=$!` 记确切 PID；子进程 PID 从 /proc/$NPID/task/$NPID/children 或 `ps --ppid $NPID` 读，核 args。存活只读 /proc/<pid>/stat 第 3 字段（不存在或 Z = 已退出），不用 kill -0。退出后 `wait $NPID` 取 rc。
- 第 0 步（只打印，不跑子进程，不写 summary，nightly_update.py L106、L137）：
```
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps cyq --dry-run </dev/null
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261016 --steps tier3,bundle,freshness --dry-run </dev/null
```

## 2. 运行 .ok 要钉的 sha（签发时再核，任一不同即作废）
| 文件 | sha256 |
|---|---|
| scripts/nightly_update.py | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| scripts/acquire/relay_health.py | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f |
| scripts/acquire/cyq_perf_monthly.py | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f |
| scripts/acquire/tier3_daily_snapshot.py | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 |
| scripts/acquire/data_freshness_status.py | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 |
| quantlab/data_sources/tushare_proxy.py | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 |
| docs/v2/audit/nightly_sha_scope_snapshot_20261018.py（v1） | 0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37 |
| docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt（补跑专用范围，414 项） | 579c8605266af1724b942fe1f3f2c000e0f97013cb9ff345c184b20c723b54c0 |
| 解释器 | /usr/bin/python3（3.13.5 / pandas 3.0.6 / pyarrow 26.0.0） |

## 3. 前置条件（全部满足才申请 .ok）
1. 主 Agent 书面同意方案 R：已有（10:44 转达）。
2. 两轮中转探测都通，其中至少一次大分页接口返回完整一页（§8）。
3. Arch 审过本文、补跑专用范围（579c8605）。
4. 13:30 ET 前拿到 .ok；拿不到就放弃今天的补跑（§9）。

## 4. 备份（cp -p 保持相对路径，Arch §4.3）
### 4.1 run1 之前
```
cd /workspace/QuantLab
mkdir _recovery/data/backfill_1014_1016            # 不加 -p：目录已存在即报错停下
cp -p --parents data/v2/cyq/cyq_perf_202610.parquet data/v2/cyq/manifest.json \
  logs/nightly/20261014_summary.json logs/nightly/20261015_summary.json logs/nightly/20261016_summary.json \
  output/relay_outage_backfill_queue.json output/relay_health.json output/data_freshness_status.json \
  _recovery/data/backfill_1014_1016/ </dev/null
cd _recovery/data/backfill_1014_1016
set -o noclobber
sha256sum data/v2/cyq/cyq_perf_202610.parquet data/v2/cyq/manifest.json logs/nightly/20261014_summary.json logs/nightly/20261015_summary.json logs/nightly/20261016_summary.json output/relay_outage_backfill_queue.json output/relay_health.json output/data_freshness_status.json </dev/null > SHA256SUMS_pre_run1
cd /workspace/QuantLab
```
- output/data_freshness_status.json 是 Data 增列：freshness 判定要和「跑前 freshness 文件」逐项比（Arch §4.4）。
- 跑前记 cyq 基线：manifest months.202610 的 rows（应 22238）、days（4）、range（20261008–20261013）、codes；cyq_perf_202610.parquet 的 num_rows（只读元数据）。

### 4.2 run2 之前
```
cd /workspace/QuantLab
cp -p --parents \
  data/v2/tier3_daily/concept_dc_index/20261014.parquet data/v2/tier3_daily/concept_dc_index/20261015.parquet \
  data/v2/tier3_daily/concept_dc_member/20261014.parquet data/v2/tier3_daily/concept_dc_member/20261015.parquet \
  data/v2/tier3_daily/anns/20261014.parquet data/v2/tier3_daily/anns/20261015.parquet \
  data/v2/tier3_daily/news/20261014.parquet data/v2/tier3_daily/news/20261015.parquet \
  data/v2/tier3_daily/research_report/20261014.parquet data/v2/tier3_daily/research_report/20261015.parquet \
  data/v2/tier3_daily/manifests/20261014.json data/v2/tier3_daily/manifests/20261015.json \
  _recovery/data/backfill_1014_1016/ </dev/null
cd _recovery/data/backfill_1014_1016 && set -o noclobber && sha256sum data/v2/tier3_daily/*/2026101[45].parquet data/v2/tier3_daily/manifests/2026101[45].json </dev/null > SHA256SUMS_pre_run2; cd /workspace/QuantLab
ls -l data/v2/tier3_daily/concept_dc_index/20261016.parquet data/v2/tier3_daily/concept_dc_member/20261016.parquet data/v2/tier3_daily/concept_ths_index/20261016.parquet data/v2/tier3_daily/anns/20261016.parquet data/v2/tier3_daily/news/20261016.parquet data/v2/tier3_daily/research_report/20261016.parquet data/v2/tier3_daily/manifests/20261016.json </dev/null
#   7 个都必须是「No such file or directory」，原样记入回执；任一存在就不起 run2，报 Arch
```
- concept_ths_index 下现在只有 20261013.parquet.sample_stub，没有 10-14 / 10-15 文件，无需备份。

## 5. sha 快照（v1 + 三条补偿，Arch §3）
```
mkdir -p /tmp/arch1018
ls -l /tmp/arch1018/backfill_before.txt /tmp/arch1018/backfill_after_run1.txt /tmp/arch1018/backfill_after_run2.txt </dev/null   # 必须都不存在
S=docs/v2/audit/nightly_sha_scope_backfill_1014_1016.txt
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py $S /tmp/arch1018/backfill_before.txt </dev/null
# 每次运行后（runN = run1 / run2）：
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py $S /tmp/arch1018/backfill_after_runN.txt </dev/null
sha256sum $S </dev/null                                                    # 人工：必须是 579c8605…
rg -n "scope_sha256" /tmp/arch1018/backfill_before.txt /tmp/arch1018/backfill_after_runN.txt   # 两份头部都必须是 579c8605…
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_20261018.py --compare $S /tmp/arch1018/backfill_before.txt /tmp/arch1018/backfill_after_runN.txt </dev/null
```
- 补偿 1：输出只写 /tmp/arch1018/backfill_*.txt 全新文件，写前 ls 证明不存在。
- 补偿 2：compare 输出出现任何 META_ONLY_CHANGE 行（MUST 项，含 daily_update_status.json）一律按退出码 1 处理。
- 补偿 3：每次 compare 前人工 sha256sum 范围文件，并与两份快照头部 scope_sha256 比对，三者都是 579c8605… 才看 compare 结果。
- 每次运行后要求：MUST 项零 DIFF、零 META_ONLY；daily_update_status.json 仍为 7991455a06b85d7bca09b8c50e2fc1cfe6f421abe33790b90a125097ab2a4850。
- 快照只在两次运行之间做（一次一个进程）；结束后快照文件作为新文件拷进 docs/v2/audit/backfill_1014_1016/（不改现有文档）。

## 6. 逐步判定（只看本次；status 字样不作数；parquet 行数只读元数据 num_rows）
### 全部运行
94322 全程 T（STOP 前后、每次运行前、CONT 后各一次 `ps -o pid,ppid,stat,etime,rss,args -p 94322` 与 /proc/94322/stat 第 3 字段）；一次一个进程；每次运行后快照 + compare 全过（§5）；RSS 采样 ≤ 1484800 kB；16:00 ET 前结束。

### run1 cyq（--date 20261016 --steps cyq）
- logs/nightly/20261016_summary.json：steps.cyq.status=ok，且没有 skipped=RELAY_DOWN。
- logs/nightly/20261016_cyq.log 本次段：有 20261014、20261015、20261016 三行「日期 行数」，没有 FAIL；每天行数 ≥ 5000。
- data/v2/tushare_raw/cyq_perf/20261014、20261015、20261016.parquet：存在，各 > 10000 字节，num_rows 等于日志行数。
- data/v2/cyq/manifest.json months.202610：new_days=3、fails=[]、days=7、range=[20261008, 20261016]、rows = 22238 + 三天日志行数之和（精确相等）、codes ≥ 跑前值。
- data/v2/cyq/cyq_perf_202610.parquet num_rows = manifest months.202610.rows。
- manifest 中 202601-202609 条目与备份逐字段相同；顶层 date_range 末端 20261016。
- 202601-202609 月表与 cyq 原始 ≤ 20261013 逐字节不变（范围 MUST）。
- run1 判 FAIL 且 cyq_perf_202610.parquet 行数低于 22238：用备份原子恢复（同目录临时文件 → sync → mv -T），恢复后 sha 等于 SHA256SUMS_pre_run1 中的值；manifest 同样恢复。

### run2 tier3（--date 20261016）
- data/v2/tier3_daily/manifests/20261016.json：concept_dc_index ok 且 rows 900–1200；concept_dc_member ok 且 rows 80000–110000；news ok 且 rows ≥ 1000；anns、research_report 为 ok 或 empty（不算失败）；concept_ths_index blocked 可接受（Q4 已裁）。
- 每个 ok 项的 20261016.parquet num_rows = manifest rows。
- 10-14 / 10-15 文件 sha 与 SHA256SUMS_pre_run2 相同（范围 MUST 同时覆盖 10-13/14/15）。

### run2 bundle
- summary steps.bundle.files 含 cyq/cyq_perf_202610.parquet 与 tier3_daily/*/20261016.parquet。
- 这些副本 sha = 源文件 sha；sw_pit 源 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6 不变。

### run2 freshness
- output/data_freshness_status.json：generated_at_et 落在 run2 时间内；expected_trade_date=20261016；overall=ok；stale_tables=[]。
- tables 各项 last_date 与 sha256 与备份（_recovery/data/backfill_1014_1016/output/data_freshness_status.json）逐项相同；tables.trade_cal.sha256 = fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41。
- warn_tables.cyq_perf_raw.last_date=20261016、lag 0；tier3_*（除 concept_ths_index）last_date=20261016。

### 回执必须标明的 PIT 事项（Arch §4.2 注意 1）
- tier3 manifest 的 available_at 写死为「20261016 20:00 Asia/Shanghai」（tier3_daily_snapshot.py L34），**实际拉取在 10-18 ET（上海 10-18 / 10-19）**；回执记实际拉取时间，tier3 10-16 视为回补快照。
- concept_ths_index 不带日期（L39）：若中转返回真实数据，20261016 文件其实是 10-18 的目录，回执标「非 10-16 时点」，不计为 10-16 快照。tier3 promotion=false，无纸面读者。

## 7. 94322 与内存
- 拿到 .ok 后、run1 前：记 ps → `kill -STOP 94322` → ps 与 /proc/94322/stat 第 3 字段须为 T，否则不跑。
- run2 与跑后快照 / compare 完成后（包括中止）：`kill -CONT 94322` → 状态回到 S 或 R。不碰 94319，不用 pkill / killall。
- RSS：每 15 秒采样 `ps -o pid=,rss=,etimes=,args= -p $NPID --ppid $NPID </dev/null`，写到 /tmp/arch1018/backfill_rss_runN.log（全新文件）。任何进程 > **1484800 kB** 即按 §9 中止。/usr/bin/time 未安装，采样只是近似峰值，回执如实写。
- 估计（未实测）：cyq < 500 MB（202610 整月约 39000 行）；tier3 < 600 MB（dc_member 约 95000 行）；nightly 父进程 < 100 MB。

## 8. 中转探测证据（占位）
记录在 docs/v2/audit/relay_probe_20261018/probe_log.csv（表头 ts_et,api,params,elapsed_s,http_status,rows,error）。截至本文生成时该文件只有 1 行数据：
```
2026-10-18 10:15:54,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261014"",""end_date"":""20261020""}",1.94,200,7,
```
| 次 | 计划时间 ET | 接口 | 参数 | 耗时 | HTTP | 行数 | 结论 |
|---|---|---|---|---|---|---|---|
| 已有 | 10:15:54 | trade_cal | SSE 20261014–20261020 | 1.94 秒 | 200 | 7 | 通（小接口，不计入大分页条件） |
| P1 | 待补 | trade_cal | 同上 | 待补 | 待补 | 待补 | 待补 |
| P1 | 待补 | cyq_perf（或 index_member_all） | 第 1 页 limit=5000 | 待补 | 待补 | 待补（完整一页应为 5000） | 待补 |
| P2 | 待补 | trade_cal | 同上 | 待补 | 待补 | 待补 | 待补 |
| P2 | 待补 | cyq_perf（或 index_member_all） | 第 1 页 | 待补 | 待补 | 待补 | 待补 |
两轮连续都通、至少一次大分页返回完整一页，才申请 .ok；任一失败不申请。探测只读、不落盘到 data/。

## 9. 时间与放弃规则
- 13:30 ET 前还没拿到 .ok：放弃今天的补跑，只保 10-19 日更（主 Agent 希望整个补跑包 13:30 前完成）。
- 最晚开始：run1 14:45 ET 前起；run2（tier3 预计 25–41 分钟：10-14 1502 秒、10-15 2434 秒）15:00 ET 前起；超过就不起，剩余项保持 pending。
- 预计时长：run1 1–5 分钟；run2 30–45 分钟；含三次快照合计约 40–55 分钟。
- 15:55 ET 仍有运行未结束：只对本次 nightly 的确切子进程 PID 先 `kill -TERM`，10 秒后仍存活（非 Z）才 `kill -KILL`；再对 nightly PID 同样处理；每步前核 /proc/<pid>/cmdline，前后留 ps。之后照常跑后快照 / compare，照常 CONT 94322；tier3 半写文件不删，原样报 Arch。
- 中止条件（任一即不起下一次）：compare 退出码非 0 或出现 META_ONLY；范围 sha 不符；本次某步判定不满足（§6）；RSS > 1484800 kB；summary 出现 RELAY_DOWN fast-fail。
- 16:40–18:40 ET 不跑任何东西（含快照）。

## 10. 回执（新文件 docs/v2/audit/BACKFILL_1014_1016_RECEIPT_ZH.md + TEAM_STATE Data 段）
.ok 路径与 sha；两轮探测行；94322 各时点 ps；两次运行的确切 PID、开始 / 结束 ET、rc、§6 每条实测值；备份 SHA256SUMS 两份；三份快照路径与 sha、两次 compare 输出与退出码、人工范围 sha 核对；RSS 最大值；PIT 标注（§6 末）；仍 pending 的项（至少 sw 10-14/15/16；队列文件本次不改，改动另报）。

## 11. 请 Arch 确认
- Q1：两次调用（run1 只 cyq、run2 tier3,bundle,freshness，均 --date 20261016）是否同意？（Arch §4.2 建议的是 run2 取消、run3 去掉 cyq，本文与之等价，只是把 --date 统一为 20261016。）
- Q2：补跑专用范围用了 Arch §2 指定的文件名 nightly_sha_scope_backfill_1014_1016.txt；另增列 10-14 / 10-15 summary 为 MUST、bundle 副本与 10-16 freshness 日志为 EXPECTED，是否同意？
- Q3：freshness 文件的跑前备份（Data 增列）是否同意作为 §6 freshness 的比较基准？
