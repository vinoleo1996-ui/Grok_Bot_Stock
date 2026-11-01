# AI：叶23 r2.7 X2 运行回执（**停于 stage 02，未完成**）

- 写入：AI（执行代理），2026-10-18 ET。live=false；promotion=false。
- **结论：主口径 stage 01 fund exit 0；stage 02 build --uni HILIQ exit 1（ArrowNotImplementedError），按条件文档 §2.3 立即停下，未重试、未清理目录、未改任何文件。stage 03–20 未启动。** 本 .ok 按 §10 视为已用，续跑需 Arch 新签。
- 94322 仍为 T（05:48:40 ET 复核 `94322 Tsl`）；按 §5「运行在阶段边界停下并报告之后」由 Data 发 SIGCONT（AI 未动 94322）。

## 1. 开跑前核对（05:46:35 ET，全部一致）
```
82d79d23f6cea72b5c4aea546a1dc262af16d481ce26c75f8712088f3ffe205d  output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok
19db13ccdd9c082f4c139283adfd1278500f414284f8694d7553a7791a855658  output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd
3d094e22d3af3e3cfe4d3c6164fc3d817c93cb92edfc339db2a156981933adc1  research/g1g5_sue_desens_cs_alpha.py
e0cdaed9e516365dad3e8ad5aa6addcea893c84e0a6868a06cbe3379df0f2b9f  docs/v2/audit/leaf23_r2_7_run/stop_94322_20261018.md
cc16c59916c2e481ce41f2cc09b337ca8f6d92faddca0f35605eec4d25caa7e1  docs/v2/audit/leaf23_r2_7_run/ARCH_LEAF23_RUN_CONDITIONS_ZH.md
```
- 注：.cmd 只含 CMC 命令；叶23 的 20 条命令按条件文档 §4 原文执行。
- 每阶段前检查 = §6 全部项 + 主 Agent 追加项：扫描 /proc/*/fd 及 fdinfo flags，确认没有进程以写方式打开 data/v2/events 下的文件（box 无 lsof）。
- 执行方式：外层包装脚本 /tmp/l23run/run_stage.sh（bash，不 import 项目代码）在 nice 0 的 shell 中做检查，再以 `( cd /workspace/QuantLab && exec env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py ... )` 启动（与 §4 命令等价，exec 保证 PID 即 python 进程），每 0.5s 采样 /proc/<pid>/status 取 VmPeak/VmHWM 最大值。

## 2. 环境
- 解释器 /workspace/qlvenv/bin/python：sys.version `3.12.14 (main, Sep 24 2026, 17:57:43) [Clang 22.1.3 ]`；numpy 2.5.3；pandas 3.0.6；pyarrow 25.0.1。
- **与叶19/20 不同**：叶19/20 当时用系统 python3 3.13（pyarrow 26.0.0 在 ~/.local）跑；本次用 qlvenv 3.12.14 / pyarrow 25.0.1。

## stage 01
### §6 检查原文
```
### precheck stage 01 primary_fund
2026-10-18T05:47:22-04:00
$ pgrep -af forecast_history_pull
$ sha256sum forecast
f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5  data/v2/events/forecast_2024plus.parquet
0bdabc4760e22e516b24089b339596d30e739b927126d605d245834c3c7f90f3  data/v2/events/forecast_2024plus_manifest.json
$ sha256sum sw_l1
89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c  data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
$ ps -o pid,stat,args -p 94322
    PID STAT COMMAND
  94322 Tsl  python3 scripts/acquire/remaining_after_stk_surv.py
$ pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
547413 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   11325852 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（含运行中 ps -o pid,stat,ni,rss,args 与 pgrep -af python 原文）
```
stage=01 label=primary_fund
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund
pid=559552 start=2026-10-18T05:47:30-04:00 end=2026-10-18T05:47:44-04:00 wall_s=14.8
exit=0 VmPeak_kB=3670456 VmHWM_kB=1271040
--- in-run ps sample
05:47:32-04:00
    PID STAT  NI   RSS COMMAND
 559552 RNl   10 408276 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
547413 [python3] <defunct>
559552 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund
```
### stdout 末尾
```
fund done rss=1241
```

## stage 02
### §6 检查原文
```
### precheck stage 02 primary_build_HILIQ
2026-10-18T05:47:54-04:00
$ pgrep -af forecast_history_pull
$ sha256sum forecast
f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5  data/v2/events/forecast_2024plus.parquet
0bdabc4760e22e516b24089b339596d30e739b927126d605d245834c3c7f90f3  data/v2/events/forecast_2024plus_manifest.json
$ sha256sum sw_l1
89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c  data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
$ ps -o pid,stat,args -p 94322
    PID STAT COMMAND
  94322 Tsl  python3 scripts/acquire/remaining_after_stk_surv.py
$ pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
560307 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   11268328 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（含运行中 ps -o pid,stat,ni,rss,args 与 pgrep -af python 原文）
```
stage=02 label=primary_build_HILIQ
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ
pid=571253 start=2026-10-18T05:48:02-04:00 end=2026-10-18T05:48:05-04:00 wall_s=3.6
exit=1 VmPeak_kB=2593320 VmHWM_kB=443148
--- in-run ps sample
05:48:04-04:00
    PID STAT  NI   RSS COMMAND
 571253 RNl   10 439036 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
560307 [python3] <defunct>
571253 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ
571492 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
```
### stdout 末尾
```
  File "/workspace/qlvenv/lib/python3.12/site-packages/pyarrow/parquet/core.py", line 1590, in read
    table = self._dataset.to_table(
            ^^^^^^^^^^^^^^^^^^^^^^^
  File "pyarrow/_dataset.pyx", line 579, in pyarrow._dataset.Dataset.to_table
  File "pyarrow/_dataset.pyx", line 415, in pyarrow._dataset.Dataset.scanner
  File "pyarrow/_dataset.pyx", line 3706, in pyarrow._dataset.Scanner.from_dataset
  File "pyarrow/_dataset.pyx", line 3619, in pyarrow._dataset.Scanner._make_scan_options
  File "pyarrow/_dataset.pyx", line 3549, in pyarrow._dataset._populate_builder
  File "pyarrow/_compute.pyx", line 2989, in pyarrow._compute._bind
  File "pyarrow/error.pxi", line 155, in pyarrow.lib.pyarrow_internal_check_status
  File "pyarrow/error.pxi", line 92, in pyarrow.lib.check_status
pyarrow.lib.ArrowNotImplementedError: Function 'greater_equal' has no kernel matching input types (large_string, timestamp[s])
```

| stage | 命令 | start / end (ET) | wall | exit | VmPeak | VmHWM | meta peak_rss_mb |
|---|---|---|---|---|---|---|---|
| 01 | primary --stage fund | 05:47:30 / 05:47:44 | 14.8 s | 0 | 3670456 kB | 1271040 kB（≈1241 MB，<1.5GB） | 1241.25 |
| 02 | primary --stage build --uni HILIQ | 05:48:02 / 05:48:05 | 3.6 s | **1** | 2593320 kB | 443148 kB | （未写 meta） |

## 3. 失败原因（只读诊断，未运行额外项目代码）
- 位置：research/g1g5_sue_desens_cs_alpha.py L651–652，build() 读 capacity_adv 腿：
  `pd.read_parquet(CAPLEG, columns=[...], filters=[("date", ">=", (pd.Timestamp(X2S) - pd.Timedelta(days=20)).to_pydatetime())])`
- CAPLEG = output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet（sha 3b288c832b956820af9802f02861af459e215e7d4097a6420724b26cf2d31c4d，= .ok 钉的 3b288c83）。pyarrow.parquet.read_schema 显示 `date: large_string`（取值形如 "2024-01-02" … "2026-10-09"，3,595,176 行），用 datetime 过滤字符串列 → `ArrowNotImplementedError: Function 'greater_equal' has no kernel matching input types (large_string, timestamp[s])`。
- 这是脚本代码问题，与解释器无关（pyarrow 对字符串列与 timestamp 比较本就没有这个 kernel；叶19/20 没读这张表）。r2.3 起只做过 py_compile，未执行过 build 路径，所以之前没暴露。
- 同脚本其它带 date 过滤的输入均为 timestamp[us]，不受影响：leaf19/leaf20 alpha HILIQ/FULLA、cs_panel_2024、universe_mask_hiliq_v1。
- 修复建议（下一版 r2.8，须 Arch 审 + 新 .ok）：L652 改为字符串过滤 `("date", ">=", (pd.Timestamp(X2S) - pd.Timedelta(days=20)).strftime("%Y-%m-%d"))`；或者不带 filters 读入，to_datetime 后再按日期切。结果不变：L653 已做 to_datetime + shift(1)，L654 再截到 X2S。建议交付前在 /tmp 用合成数据把 build 路径跑一遍，前提是 selftest .ok 已签。

## 4. 已有产物 sha（仅主口径 fund；其他目录/权重文件均未生成）
```
b99002f0a4fab80f5b881721767bb64ed9f24596f6b21a424ee554ff1aaecc89  output/ai_factory/leaf23_sue_desens_cs/blackout_pairs.parquet
75238129d08b149ca7c5385bb0ebf59733aa8294e8ab1e03b293a53bea27d302  output/ai_factory/leaf23_sue_desens_cs/event_table.parquet
b883dabbc529a7474d73c3854cbb634355ac95f97eab1f7b635783339a29a541  output/ai_factory/leaf23_sue_desens_cs/event_table_oldsel.parquet
73cbea185d5c11d0804524ad93b54f682c25b0085f1461dd0ce15207c7285bbd  output/ai_factory/leaf23_sue_desens_cs/fund_meta.json
```
- 敏感性目录 leaf23_sue_desens_cs_{sig-sue,denom-daily,nofc,bo40}：不存在。output/ai_factory/g1g5_*sue_desens*_daily_weights_*.parquet 和 run_meta：没有生成（eval 未跑），CMC 不能启动。
- fund_meta：rows 83123；rows_current_d1_nan 3246；rows_oldsel 80088；niceness 10；input_sha.forecast f1e59284…；financials bc0f4c3d…；cs_panel_manifest 5c44019d…。

## 5. 核对项
- 7 只退市股（000416.SZ 000961.SZ 002699.SZ 300116.SZ 300495.SZ 600321.SH 600823.SH）在 X2 内 S=True 的名·日数：**无法核对**。该 diag 由 eval 阶段写出，eval 未跑。
- delisted_master_max_delist_date：diag 未生成。参照 Data 计数 docs/v2/audit/data_delist_count_leaf23_24/out.txt（b54705fd…，第 29 行 max delist_date = 2026-07-30），预期 2026-07-30，留待续跑的 eval diag 核对。
- P3-6（primary_cut_delist_date 与 bench cagr244 对应）：未能核对（eval 未跑）。

## 6. 披露
- 数据截止日 20261014；301139.SZ 有数据缺口。
- 没有任何判定结果：HAC t（lag 19）、CAGR（244 日为主，252 日并列）、MDD 均未产出。

## 7. 现状 / 待决
- 94322：AI 未动。05:48:40 ET 时仍为 T，等 Data 按 §5 发 CONT。
- 本 .ok（82d79d23…）按 §10 归档，不再复用。续跑需要：先出 r2.8 修复，再经 Arch 审，再新签 .ok（重钉 forecast parquet 和它的 manifest；nightly 10-19 05:55 之后 sha 可能变）。主口径目录 output/ai_factory/leaf23_sue_desens_cs 里已有 fund 产物，续跑时是否清空或换目录，由 Arch 决定。
