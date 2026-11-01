# 10-19 日更时间线（Eng 纸面日历备份 → daily_pull → 比对 → 恢复）

- 作者：QuantLab Data；生成时间 2026-10-18T10:58:15-04:00（ET，date 生成）。新文件，待 Arch 审、主 Agent 定开跑时间。
- 本文只读得出：Read / rg（显式路径）/ ls。没有运行项目代码，没有读 parquet 内容，没有对 data/ 下文件算 sha。
- 依据：Arch 审查 docs/v2/ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md（11cb0690）§5.4；Arch 10:52 补充（主 Agent 书面裁定：日历不做只读开关，一律恢复到 141078fa；Eng 纸面例程启动前要求 trade_cal 全长 sha == 141078fa，恢复晚了纸面就不跑）。
- 相关新脚本（同目录）：cal_compare_v1.py（74093ff3…）、cal_restore_v1.py（181549b8…）；快照 v2：docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py（c930ed5c…）。
- live=false，promotion_approved=false，strategy_promotion=false。

## 1. 硬时间点
| 时间（ET） | 事件 | 出处 |
|---|---|---|
| 06:30 | 纸面把 D=10-19 视为必需交易日（CUTOFF_ET=(6,30)） | quantlab/portfolio/trade_calendar.py L15-16、L57 |
| 约 06:37 | 纸面日常例程开始读 data/v2/tushare_raw/trade_cal.parquet，且要求 sha == 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 | Arch 11cb0690 §5.4；Arch 10:52 |
| 06:30 之前 ≥ 20 分钟 | 「预计恢复完成 + 20 分钟余量」必须早于 06:30，即恢复须在 06:10 前完成 | 主 Agent / Arch 10:52 |
| 06:20 | 硬截止：daily_pull 仍在跑就按确切 PID 终止并立即恢复（§5） | 本文 |
| 16:40–18:40 | 不跑任何东西 | 团队规则 |

## 2. daily_pull 实测耗时（过去几次日更）
每次都只新拉 1 个交易日（5 个接口：daily、daily_basic、adj_factor、stk_limit、suspend_d），其余日子 skip；10-19 也只会新拉 20261019 一天，口径可比。
| 运行 | 开始（ET，日志首行） | 结束（最后一行） | 耗时 | 当晚中转 | 出处 |
|---|---|---|---|---|---|
| 20261014 | 2026-10-14 17:59:51 | 18:01:15 | 约 84 秒（daily 21 秒、daily_basic 40 秒，datahub 响应慢） | 中转通 | logs/nightly/20261014_daily_pull.log L2、L50-54（summary 已被后续 --steps 合并覆盖，无 sec） |
| 20261015 | 2026-10-17 23:55:45 | 23:56:00 | 14 秒（summary sec=14） | 中转宕（sw、cyq 记 RELAY_DOWN），daily_pull 走 datahub 不受影响 | logs/nightly/20261015_summary.json L10-14、L60-70；20261015_daily_pull.log L2、L55-59；20261015_run_2355ET.out L3 |
| 20261016 | 2026-10-18 00:19:01 | 00:19:16 | 16 秒（summary sec=16） | 中转宕（cyq、tier3 记 RELAY_DOWN），daily_pull 不受影响 | logs/nightly/20261016_summary.json L10-14、L70-79；20261016_daily_pull.log L2、L60-64；20261016_run_0019ET.out L3 |
| 参考：20261013 | 日志无日期；06:08:34 开始逐日 | 06:09:38 | 日拉部分 64 秒（cal 刷新时间未记） | 未知 | data/_acquire_logs/tier1_extend_20261013.log L3、L43-47 |

结论：正常情况下 daily_pull 14–84 秒，取 **90 秒** 作计划值。中转宕机本身不影响 daily_pull（它优先走 datahub，scripts/acquire/tier1_pull.py L17-31、L85）。

### 2.1 datahub 也不通时（代码推算，没有实测）
- 日历刷新与每个接口都走 pull()：最多重试 8 次（tier1_pull.py L38-45，每次间隔 2·(a+1) 秒，共 72 秒），每次 _call 先试 datahub 再试 relay（L17-31）。
- 连接被立即拒绝（快速失败）：datahub 4 个地址各 _get 重试 2 次（tushare_proxy.py L62-89，L26-47 间隔 2、4 秒），relay 重试 5 次（L57-60，间隔 2–10 秒），单次 _call 约 55–60 秒；日历刷新约 8–9 分钟后打印「cal refresh skip」（L94-95，文件不改）；随后第一个接口 daily 20261019 再耗约 8–9 分钟后抛异常退出（cached_day 不捕获，L64-70）。**合计约 17–18 分钟，rc≠0。**
- 超时型故障（连得上但不返回）：datahub 每次 90 秒超时、relay 每次 180 秒超时（nightly 环境不设 TSPRO_RELAY_TIMEOUT），单次 _call 可达约 25 分钟，8 次重试可达数小时。**只能靠 06:20 硬截止兜底。**
- 数据还没发布时：接口 200 但返回 0 行，save() 仍会写一个 0 行 parquet（L58-62），之后 cached_day 因文件大小 > 0 一律 skip（L66-67），这一天会一直缺。所以 call A 之后必须核 20261019 五个原始文件的 num_rows（只读元数据）：daily / daily_basic / adj_factor / stk_limit ≥ 5000；为 0 即报 P1，**不自行删除**，等 Arch / 主 Agent 定。

## 3. 比对 + 恢复耗时估计（没有实测，按文件大小与步骤数估）
| 步骤 | 估计 |
|---|---|
| call A 前：mkdir、cp -p 备份、两次 sha256sum（95261 字节）、chmod a-w、stat、fa4260b8 / 7ccc911e 前 sha | ≤ 5 秒 |
| call A 前：快照 v2 BEFORE（10-19 专用范围，约 167 个文件、约 145 MB，进程内 hashlib） | ≤ 15 秒 |
| call A 后：cp -p post_daily_pull 副本 + sha | ≤ 2 秒 |
| cal_compare_v1.py（Python 启动 + import pandas / pyarrow + 读两份约 95 KB） | ≤ 15 秒 |
| cal_restore_v1.py（三次哈希 + 复制 + fsync + rename） | ≤ 5 秒 |
| 恢复后 sha256sum + stat + 30 秒后再核一次（防迟到写入） | ≤ 35 秒 |
| 合计 | **约 1.5 分钟，计划取 2 分钟** |

## 4. 开跑时间推算与建议
记 S = 例程实际开始时间。恢复完成 ≈ S + 0.5 分钟（准备）+ 1.5 分钟（daily_pull 计划值）+ 2 分钟（比对恢复）= **S + 4 分钟**。要求 S + 4 + 20 ≤ 06:30，即 **S ≤ 06:06**。
| 方案 | 准点 S | 恢复完成 | +20 分钟 | 晚 15 分钟 S | 恢复完成 | +20 分钟 | 06:20 截止前留给 daily_pull 的时间（晚 15 分钟时） | 结论 |
|---|---|---|---|---|---|---|---|---|
| 05:55（现方案，上海 17:55） | 05:55 | 05:59 | 06:19 ✓ | 06:10 | 06:14 | **06:34 ✗** | 约 9 分钟，不够覆盖 §2.1 快速失败的 17–18 分钟 | 只在准点时成立 |
| **05:30（建议，上海 17:30）** | 05:30 | 05:34 | 05:54 ✓ | 05:45 | 05:49 | 06:09 ✓ | 约 34 分钟，覆盖快速失败 | **建议** |
| 05:15（上海 17:15） | 05:15 | 05:19 | 05:39 ✓ | 05:30 | 05:34 | 05:54 ✓ | 约 49 分钟 | 余量最大，但离 Tushare 公布上限 17:00 只有 15 分钟 |

**建议：call A 在 05:30 ET 开跑**（例程最晚 05:45 起仍满足 20 分钟余量）。call B（其余 14 步，约 50 分钟）随后串行，不碰纸面日历，例程不变。改开跑时间要主 Agent 定、Arch 同意；未改时仍按 05:55，且例程若晚于 06:06 才开始，就按 §5.6 先报主 Agent。

### 4.1 上游当日数据在 17:30 上海是否已发布
- 05:30 ET = 17:30 上海（10-19 周一，夏令时 ET = UTC−4，上海 UTC+8，差 12 小时）；上交所 15:00 收盘 = 03:00 ET。
- Tushare 官方文档（10-18 网页检索）：daily「交易日每天 15 点～16 点之间入库」（tushare.pro/document/2?doc_id=27），积分说明页写「15 点～17 点之间更新」（doc_id=108）；daily_basic「交易日每日 15 点～17 点之间」（wctapi/documents/32.md）；adj_factor「盘前 9 点 15～20 分完成当日复权因子入库」（doc_id=28）；stk_limit「交易日 9 点」（doc_id=108）。suspend_d 文档未核。按文档上限，17:30 上海已过最晚的 17:00 半小时；17:15 只过 15 分钟。
- 本地日志证据：能证明「当日拿到非空数据」的只有 data/_acquire_logs/tier1_extend_20261013.log L43「06:08:57 daily 20261013 ok 5561」。如果这是 10-13 当天 ET 06:08（日志无日期，文件 mtime 是 10-18 01:13 恢复时间，**只是推断**），对应上海 10-13 18:08，当日数据已全部到位。10-14 / 15 / 16 三次都在上海次日或更晚跑（10-14 那次是上海 10-15 05:59），不能证明当日时点。
- 结论：05:30 ET 有文档支持，本地只有一条推断证据；05:15 ET 风险偏高。无论哪个时间，call A 之后都按 §2.1 核 20261019 行数，0 行即 P1。
- 附带说明（不因改时间而变化）：freshness 在上海 20:00 前把 expected_trade_date 取前一开市日（scripts/acquire/data_freshness_status.py L3、L61），05:30 或 05:55 跑都会是 20261016。

## 5. 例程写法（call A 段；只写 Data 自己起的进程）
### 5.1 准备（全部在 call A 前，按 Arch §5.4）
```
cd /workspace/QuantLab
date "+%Y-%m-%dT%H:%M:%S%z"
mkdir -p _recovery/data/nightly_20261019 docs/v2/audit/nightly_20261019
cp -p data/v2/tushare_raw/trade_cal.parquet _recovery/data/nightly_20261019/trade_cal.parquet.141078fa
sha256sum data/v2/tushare_raw/trade_cal.parquet _recovery/data/nightly_20261019/trade_cal.parquet.141078fa </dev/null
#   两行都必须是 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，否则不跑，报主 Agent 与 Arch
chmod a-w _recovery/data/nightly_20261019/trade_cal.parquet.141078fa
stat -c "%n %s %Y %Z %i %a" data/v2/tushare_raw/trade_cal.parquet </dev/null
sha256sum data/v2/calendar/trade_cal_sse_pit.parquet data/v2/calendar/manifest.json </dev/null   # 应为 fa4260b8… / 7ccc911e…
#   快照 v2 BEFORE（范围文件与 sha 以 Arch 审过的为准）
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py snap <10-19 范围文件> /tmp/arch1018/nightly_20261019_before.txt --expect-scope-sha <范围 sha> </dev/null
```
### 5.2 起 call A 并拿确切 PID
```
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/nightly_update.py --date 20261019 --steps daily_pull </dev/null >> logs/nightly/nightly_20261019_callA.out 2>&1 &
NPID=$!          # nice 直接 exec python，$! 就是 nightly_update.py 的 PID
sleep 2
cat /proc/$NPID/task/$NPID/children </dev/null     # 子进程 tier1_pull.py 的 PID，记为 CPID
ps -o pid,ppid,stat,etime,rss,args -p $NPID --ppid $NPID </dev/null
```
- CPID 只认 ps 输出中 PPID = NPID 且 args 含「scripts/acquire/tier1_pull.py extend 20261019」的那一个；写进回执。
- 存活判定只读 /proc/<pid>/stat 第 3 字段（取最后一个「)」之后的第一个字段）：文件不存在或状态为 Z 即视为已退出；不用 kill -0。纯 bash 写法：`s=$(</proc/$NPID/stat); s=${s##*) }; st=${s%% *}`。
- 每 5 秒轮询一次 NPID；退出后 `wait $NPID; echo rc=$?` 取 rc（同一个 shell）。

### 5.3 call A 正常结束后（不论 rc，Arch 条件 3）
```
cp -p data/v2/tushare_raw/trade_cal.parquet _recovery/data/nightly_20261019/trade_cal.parquet.post_daily_pull
sha256sum _recovery/data/nightly_20261019/trade_cal.parquet.post_daily_pull </dev/null
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_20261019/cal_compare_v1.py \
  --current _recovery/data/nightly_20261019/trade_cal.parquet.post_daily_pull \
  --backup  _recovery/data/nightly_20261019/trade_cal.parquet.141078fa \
  --out     /workspace/QuantLab/docs/v2/audit/nightly_20261019/cal_compare_result.txt </dev/null
echo compare_rc=$?
PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 docs/v2/audit/nightly_20261019/cal_restore_v1.py \
  --backup _recovery/data/nightly_20261019/trade_cal.parquet.141078fa \
  --target /workspace/QuantLab/data/v2/tushare_raw/trade_cal.parquet \
  --expect-sha 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 \
  --keep-rewritten-dir /workspace/QuantLab/_recovery/data/nightly_20261019 </dev/null
echo restore_rc=$?
sha256sum data/v2/tushare_raw/trade_cal.parquet </dev/null; sleep 30; sha256sum data/v2/tushare_raw/trade_cal.parquet </dev/null
```
- 比对结果只决定是否报 P1（compare_rc=1：报 P1、差异行 csv 交 Arch；compare_rc=2：比对器出错，同样报），**不决定是否恢复**；恢复一律做。
- restore_rc：0 通过；3 已恢复但被重写文件留存失败（报 Arch，继续）；1 或 2 或两次 sha256sum 任一不是 141078fa：**P0 报警，停 call B**，立刻报主 Agent 与 Arch。
- 恢复核验通过且 20261019、20261020 在备份里都开市（比对结果 C6）后，才起 call B。

### 5.4 06:20 ET 硬截止（call A 仍在跑时）
1. 记证据：`date`；`ps -o pid,ppid,stat,etime,rss,args -p $NPID,$CPID </dev/null`。
2. 每次发信号前核对 /proc/<pid>/cmdline 仍是预期命令（CPID 含 tier1_pull.py、NPID 含 nightly_update.py），且 CPID 的 PPID 仍是 NPID；不符（PID 已复用）就不发信号，直接进第 5 步。
3. **先停子进程**（只停父进程的话，subprocess.call 起的 tier1_pull.py 会成为孤儿继续写日历）：`kill -TERM $CPID`，轮询 /proc/$CPID/stat 最多 10 秒；仍存活（非 Z、文件仍在）则 `kill -KILL $CPID`，再轮询 5 秒。
4. 子进程退出后 nightly 会自己写 summary（fail rc=-15）并退出；轮询 NPID 最多 10 秒，仍存活则 `kill -TERM $NPID`，10 秒后仍存活才 `kill -KILL $NPID`。不用 pkill / killall，不带任何 --force，不碰其他 PID（包括 94322）。
5. 确认 CPID、NPID 都已退出（或为 Z）后，**再**按 §5.3 做 post_daily_pull 副本、比对、cal_restore_v1.py、两次 sha256sum（先确认写入方已不存在，避免恢复后被迟到写入覆盖）。
6. 立即发 priority=true 给主 Agent 与 Arch：截止时间、两个 PID 与信号序列及前后 ps、compare_rc、restore_rc、恢复后 sha、20261019 原始文件现状（ls -l，不读内容）。
7. daily_pull 被截止后 **不重跑**：重跑会再次重写纸面日历，且 06:30 后纸面在读。call B 是否照跑（它不碰日历，但日线会停在 10-16）由主 Agent 定；未收到答复前不起 call B。

### 5.5 回执（Arch 条件 6）
两次调用的完整命令和 rc；NPID / CPID；备份、post_daily_pull、留存副本、恢复后的 sha 与 stat（inode、ctime）；比对结果文件与 csv 的路径和 sha；fa4260b8、7ccc911e 前后 sha；快照 v2 BEFORE / AFTER 与 compare 输出（trade_cal 按 [RESTORED_TO_PIN] 判）；每个时间点用 date 记录。

### 5.6 例程晚开
例程若在 06:06 ET 之后才开始 call A（按 §4 已无 20 分钟余量），先发 priority=true 给主 Agent，照跑 call A 与恢复，06:20 截止不变。

## 6. 待定
- Q1（主 Agent）：call A 改为 05:30 ET 开跑？（Data 建议；05:15 作备选。）
- Q2（Arch）：§5.4 第 7 步「截止后不起 call B，等主 Agent」是否同意，还是恢复核验通过后照起 call B？
- Q3（Arch）：20261019 原始文件出现 0 行时的处理（§2.1）。
