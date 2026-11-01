# AI：叶23 r2.9 X2 运行回执（**停于 stage 04 主口径 eval，exit 137 RSS 看门狗；未完成**）

- 写入：AI（执行代理），2026-10-18 ET。live=false；promotion=false。条件文档 docs/v2/audit/leaf23_r2_7_run/ARCH_LEAF23_RUN_CONDITIONS_ZH.md（cc16c599…）继续生效；.ok 改用 r2.9 版。
- **结论**：stage 01–03（主口径 fund / build HILIQ / build FULLA）都 exit 0。stage 04（主口径 eval）在 06:00:22 ET 由脚本 RSS 看门狗以 `os._exit(137)` 杀掉，stdout 原文为 `RSS_GUARD_KILL rss_kb=1536432 (limit 1536000)`。按 §2.3/§8 当失败处理：立即停下，没有重试，没有清理目录，没有改任何文件。stage 05–20 没有启动。
- **红线**：峰值 RSS 超过 1.5GB。包装脚本采样 VmHWM 最大值为 1704112 kB（约 1664 MB）。脚本打印的 `HILIQ eval done rss=1596` 是 ru_maxrss，说明 HILIQ eval 结束时峰值已到约 1596 MB。看门狗每 1 s 取一次 VmRSS（当前值，不是峰值），所以没在 HILIQ 段拦下，直到 FULLA eval 段才触发。
- 94322：AI 没动。06:00:34 ET 复核仍是 `94322 Tsl`。按 §5，在阶段边界停下并报告之后由 Data 决定 CONT。

## 1. 开跑前核对（05:56:53 ET，全部一致）
```
d199b778e6a50c345a761c6f1f1f1b699b461b486479c88cbca880e4e02eabf0  research/g1g5_sue_desens_cs_alpha.py   (HEAD 9b1d234)
b21e995282d8aad0954adb5f28942bd80da3190bb3dad9e4628c080466259abc  output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok   (issued_at 05:55:42, expires_et 2026-10-19T04:30:00-04:00, out_dir=…/leaf23_sue_desens_cs, live/promotion=false)
493cc03c280be625ad96b9c6f26b45f5f78b74f2ccf03e73741e576d79d82578  output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd
a109702ffbc2923c4ce03de589d712081eee4da5ba1af76fd8270b56ce91e0da  docs/v2/audit/leaf23_r2_9_run/stop_94322_20261018_r2_9.md   (kill -STOP 05:56:31 ET)
cc16c59916c2e481ce41f2cc09b337ca8f6d92faddca0f35605eec4d25caa7e1  docs/v2/audit/leaf23_r2_7_run/ARCH_LEAF23_RUN_CONDITIONS_ZH.md
```
- 命令按条件文档 §4 原文执行，--arch-ok 换成 /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok（旧 r2.7 .ok 已用过，本次没用）。

## 2. r2.7 停跑产物作废移位（05:57 ET）
- output/ai_factory/leaf23_sue_desens_cs/ 里原有的 4 个文件（目录里只有这 4 个）移到 output/ai_factory/_void/leaf23_r2_7_stage02_stop_20261018/。
- 移动前写 SHA256SUMS_before.txt，移动后写 SHA256SUMS_after.txt，两份 `cmp` 完全一致，文件 sha 都是 cd874a64ff13fa69c060b98eb7d8fadd1caad8582ca20b3a403ff9f0813f6298。
- 移完后 leaf23_sue_desens_cs/ 留作空目录，本次运行的产物写在里面。
```
b99002f0a4fab80f5b881721767bb64ed9f24596f6b21a424ee554ff1aaecc89  blackout_pairs.parquet
75238129d08b149ca7c5385bb0ebf59733aa8294e8ab1e03b293a53bea27d302  event_table.parquet
b883dabbc529a7474d73c3854cbb634355ac95f97eab1f7b635783339a29a541  event_table_oldsel.parquet
73cbea185d5c11d0804524ad93b54f682c25b0085f1461dd0ce15207c7285bbd  fund_meta.json
```

## 3. 环境与执行方式
- 解释器 /workspace/qlvenv/bin/python：`3.12.14 (main, Sep 24 2026, 17:57:43) [Clang 22.1.3 ]`；numpy 2.5.3；pandas 3.0.6；pyarrow 25.0.1。**与叶19/20 不同**：它们当时用系统 python3 3.13（pyarrow 26.0.0）跑。
- 包装脚本 /tmp/l23run_r29/run_stage.sh 和 chain.sh 只用 bash，不 import 项目代码。在 nice 0 的 shell 里先做检查，再用 `( cd /workspace/QuantLab && exec env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py … )` 启动（与 §4 命令等价，exec 使 PID 就是 python 进程）。每 0.5 s 采样 /proc/<pid>/status，取 VmPeak 和 VmHWM 的最大值。日志在 /tmp/l23run_r29/。
- 每个阶段前的检查：§6 全部项，加上主 Agent 追加的一项：扫描 /proc/*/fd 和 fdinfo flags，确认没有进程以写方式打开 data/v2/events 下的文件（box 上没有 lsof）。

## 4. 阶段汇总
| stage | 命令 | start / end (ET) | wall | exit | VmPeak | VmHWM（采样最大） | meta peak_rss_mb |
|---|---|---|---|---|---|---|---|
| 01 | primary_fund | 05:57:16 / 05:57:30 | 14.8 s | 0 | 3671480 kB | 1267380 kB | |
| 02 | primary_build_HILIQ | 05:57:38 / 05:58:12 | 34.4 s | 0 | 3610368 kB | 1260308 kB | |
| 03 | primary_build_FULLA | 05:58:20 / 05:58:52 | 32.3 s | 0 | 3840504 kB | 1406620 kB | |
| 04 | primary_eval | 05:58:59 / 06:00:22 | 82.3 s | 137 | 3919472 kB | 1704112 kB | |
- meta peak_rss_mb：fund 1237.68；build_HILIQ 1230.77；build_FULLA 1373.65；eval 没写 meta（被杀）。stdout 中 eval 的 ru_maxrss：HILIQ 段结束时 1596 MB。

## stage 01 原文
### §6 检查（含 events 写 fd 扫描）
```
### precheck stage 01 primary_fund
2026-10-18T05:57:08-04:00
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
585909 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   11387164 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（命令原文、运行中 ps -o pid,stat,ni,rss,args、pgrep -af python）
```
stage=01 label=primary_fund
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage fund
pid=596726 start=2026-10-18T05:57:16-04:00 end=2026-10-18T05:57:30-04:00 wall_s=14.8
exit=0 VmPeak_kB=3671480 VmHWM_kB=1267380
--- in-run ps sample
05:57:18-04:00
    PID STAT  NI   RSS COMMAND
 596726 RNl   10 372068 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage fund
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
585909 [python3] <defunct>
596726 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage fund
```
### stdout 末尾
```
fund done rss=1238
```

## stage 02 原文
### §6 检查（含 events 写 fd 扫描）
```
### precheck stage 02 primary_build_HILIQ
2026-10-18T05:57:30-04:00
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
597375 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   11231560 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（命令原文、运行中 ps -o pid,stat,ni,rss,args、pgrep -af python）
```
stage=02 label=primary_build_HILIQ
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni HILIQ
pid=607748 start=2026-10-18T05:57:38-04:00 end=2026-10-18T05:58:12-04:00 wall_s=34.4
exit=0 VmPeak_kB=3610368 VmHWM_kB=1260308
--- in-run ps sample
05:57:40-04:00
    PID STAT  NI   RSS COMMAND
 607748 RNl   10 394672 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni HILIQ
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
597375 [python3] <defunct>
607748 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni HILIQ
```
### stdout 末尾
```
HILIQ 2024 built rss=1071
HILIQ 2025 built rss=1221
HILIQ 2026 built rss=1231
```

## stage 03 原文
### §6 检查（含 events 写 fd 扫描）
```
### precheck stage 03 primary_build_FULLA
2026-10-18T05:58:12-04:00
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
597375 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   10782536 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（命令原文、运行中 ps -o pid,stat,ni,rss,args、pgrep -af python）
```
stage=03 label=primary_build_FULLA
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni FULLA
pid=619654 start=2026-10-18T05:58:20-04:00 end=2026-10-18T05:58:52-04:00 wall_s=32.3
exit=0 VmPeak_kB=3840504 VmHWM_kB=1406620
--- in-run ps sample
05:58:22-04:00
    PID STAT  NI   RSS COMMAND
 619654 RNl   10 377936 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni FULLA
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
597375 [python3] <defunct>
619654 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage build --uni FULLA
```
### stdout 末尾
```
FULLA 2024 built rss=1102
FULLA 2025 built rss=1367
FULLA 2026 built rss=1374
```

## stage 04 原文
### §6 检查（含 events 写 fd 扫描）
```
### precheck stage 04 primary_eval
2026-10-18T05:58:52-04:00
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
597375 [python3] <defunct>
$ grep MemAvailable
MemAvailable:   11256944 kB
$ write-open fds under data/v2/events (scan /proc/*/fd + fdinfo flags)
events_write_open=0
PRECHECK_OK
```
### 运行结果（命令原文、运行中 ps -o pid,stat,ni,rss,args、pgrep -af python）
```
stage=04 label=primary_eval
cmd=cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage eval
pid=631531 start=2026-10-18T05:58:59-04:00 end=2026-10-18T06:00:22-04:00 wall_s=82.3
exit=137 VmPeak_kB=3919472 VmHWM_kB=1704112
--- in-run ps sample
05:59:01-04:00
    PID STAT  NI   RSS COMMAND
 631531 RNl   10 364024 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage eval
--- pgrep -af python
53 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
204 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
27366 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
27427 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
80415 python3 -X utf8 server.py
94322 python3 scripts/acquire/remaining_after_stk_surv.py
631531 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_9_X2.ok --stage eval
631557 [python3] <defunct>
```
### stdout 末尾
```
HILIQ eval done rss=1596
RSS_GUARD_KILL rss_kb=1536432 (limit 1536000)
```

## 5. 产物 sha（全部；stage 04 是失败阶段，它写出的文件**不算有效产物，不能给 CMC 用**）
### output/ai_factory/leaf23_sue_desens_cs/
```
6ee60d6b201ec5a80ce4c00dff15f5ffe6ed4e5a90dbe8fe7f296ce06c3be379  alpha_FULLA_2024.parquet
aa9bf462d60742bd09fa79ffcc9d5b6e5b0edb21ff36ea1cd5866e265671c773  alpha_FULLA_2025.parquet
85039688d56942155c29824a182c4822ce49b002a037849dd4b1124534af6d26  alpha_FULLA_2026.parquet
7f5b1f796bfa9cfaa2a2cd25e3443e458d6db6b9c5fb77f4ebb9b59c7a173f2a  alpha_HILIQ_2024.parquet
ff3f29520fc956cbe8401f6517b19d0e739e8f0520221084457e0145e49c3565  alpha_HILIQ_2025.parquet
c4bbe9cdc7937eeb7d0ea66cbe627512dd00608ffb3ce888a272a28b16c58820  alpha_HILIQ_2026.parquet
b99002f0a4fab80f5b881721767bb64ed9f24596f6b21a424ee554ff1aaecc89  blackout_pairs.parquet
07391924685c262f6ccff1e5ca284cd240b5995aac5bb22a28d0820cc2fcbc1d  build_FULLA_meta.json
fb4b2ad4f6ae798d46e225a67a679198b45d6eed28636ee235b2b23af50a4acc  build_HILIQ_meta.json
d071cc9a40263d80549e040da04f062cc45d1a0208db809e0595127be3e34c0c  coverage_FULLA.parquet
756fcf96ed139ebeb07ce216cca056db537ae6e3fc3b3913b4dea8c9bff7faf7  coverage_HILIQ.parquet
7fa8ee88d95cbdc29e55c0dec1cb0142cb70fec25665b4b2f8dc3033660ecf2e  eval_weights_HILIQ_top10_100w_cap20_disclosure_x2_20261018_055902.parquet
067910784ea7ec3a7286b14b848764957f020767bd0edbf968c7ad5a55f4fa29  eval_weights_HILIQ_top10_100w_x2_20261018_055902.parquet
5445cfe127ab4619b702165c2a90b3496f65a0486b3c309e3887acac81c64bbb  eval_weights_HILIQ_top20_disclosure_x2_20261018_055902.parquet
63d64393f832560ab3e8ba7047b1df25a7a9e89e5c1d0971ebef5b7c8bc2d2e6  eval_weights_HILIQ_top6_60w_cap20_disclosure_x2_20261018_055902.parquet
d4fb418f5ec4cc74b0bb26d7024e140a8ff087e3bb7d95fec165da9f92056010  eval_weights_HILIQ_top6_60w_x2_20261018_055902.parquet
7981f14a2a9285f6b4270f856f9be757e30aa241b3698b892153b0029326c9f3  event_table.parquet
a218b0ca590df98a661438fcc2ac2bf3b1a92b4afcae3c2d80c54225800b2a7f  event_table_oldsel.parquet
f393b3e9635130fa57c0d74c9915e49b7eda2804da494c4f00d0813a899c6509  fund_meta.json
1612071f1fa5b279b4f985ffe170b72a8f40f94d1ec08ff7bc28111ce54f8f54  gate_FULLA_2024.parquet
f6dbc43c6f11a6af3d89e14a681853fc9b66d6cfd5ebffb4a6f4bc1fbd039731  gate_FULLA_2025.parquet
ae70cb6fdf021d68b850e9b53b21a88ae690a0a1bd97aaba089e0ed0305d57c6  gate_FULLA_2026.parquet
863a7bebfe5584a15d84d5a19de06a59950979a2ff0989f35ff1475ea61690db  gate_HILIQ_2024.parquet
8d5b355d06ff80d61627c483ff14dd6cefa88d3125c97ce111e02d7ba9f6c2f7  gate_HILIQ_2025.parquet
b4efabaccfb8766951cfbb1282dca9a5e7bf5cb383f3ca1398c56ffaa68556e9  gate_HILIQ_2026.parquet
```
### output/ai_factory/g1g5_*sue_desens*（stage 04 HILIQ 段写出，05:59:35–37 ET）
```
067910784ea7ec3a7286b14b848764957f020767bd0edbf968c7ad5a55f4fa29  g1g5_sue_desens_cs_top10_100w_daily_weights_20261018_055902.parquet
ad228af90336749119317a73714898104c3388ad226a9b6d746863015b4f17fe  g1g5_sue_desens_cs_top10_100w_run_meta_20261018_055902.json
d4fb418f5ec4cc74b0bb26d7024e140a8ff087e3bb7d95fec165da9f92056010  g1g5_sue_desens_cs_top6_60w_daily_weights_20261018_055902.parquet
b0df8b2fe9ad3979e522e0407ae9639bdae0419422bc96ccff2151495c6f8daa  g1g5_sue_desens_cs_top6_60w_run_meta_20261018_055902.json
```
- run_meta 只有 mechanism_tag/universe/tier/variant/live=false/promotion_approved=false/stamp 20261018_055902/window x2/script_sha256/arch_ok_sha256，没有 diag。
- **没有生成**：summary_*.json、eval_meta.json、FULLA 的 eval_weights、B3_carry_mismatch_*；4 个敏感性目录都不存在。脚本 L895–896 在两个 uni 都跑完后才写 summary 和 eval_meta，所以 HILIQ 段的 diag 也没落盘。

## 6. 核对项（都需要 diag/summary，本次都没生成）
- r0.index 是否等于 rr.index：**输出里没有记录**。脚本 L779 注释写 `r0.index == rr.index`，但没有写进 diag；summary 本次也没生成。
- N4（金融股及 600519/002371 剔除的名·日数和 wb 权重占比）：**没有记录**（summary/diag 没生成）。build meta 里只有 b4_oldorder_fallback_name_days_x2（HILIQ 2024/2025/2026 = 55/1060/47；FULLA = 185/1796/47）和 p3c_nv120_lt100_share_x2，没有 N4 字段。
- 7 只退市股（000416.SZ 000961.SZ 002699.SZ 300116.SZ 300495.SZ 600321.SH 600823.SH）在 X2 内 S=True 的名·日数：**无法核对**（diag 没落盘）。预期是 0。
- delisted_master_max_delist_date：diag 没生成。按 Data 计数 docs/v2/audit/data_delist_count_leaf23_24/out.txt（b54705fd…，第 29 行 max delist_date 2026-07-30）预期为 2026-07-30，等续跑的 eval diag 再核。
- P3-6（*_primary_cut_delist_date 与 bench cagr244）：没能核对。
- 头条结果：**没有**。HAC t（lag 19，两档，|t|≥2.50）、CAGR（244 日为主、252 日并列）、MDD、60万/100万，都要从 summary json 取，本次没生成，所以不报任何数字。

## 7. 披露
- 数据截止日 20261014；301139.SZ 有数据缺口；非主口径一律「未做多重检验校正，仅披露」；影子口径只披露。
- 文件 mtime 说明（由主 Agent 转告）：
  1. research/、hx2、fulla、research/tests_sw_pit/ 下 05:50–05:51 ET 的 mtime 记录是 Arch 审查时造成的：据 Arch 说明，Arch 误改了仓库，随后已复原。AI 执行代理没有改这些文件。
  2. research/__pycache__/g1g5_sue_desens_cs_alpha.cpython-313.pyc（mtime 05:50:07 与 05:53:45）是 AI 在交付 r2.8/r2.9 时用系统 python3 3.13 做 `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile` 静态检查写出的。py_compile 不管 PYTHONDONTWRITEBYTECODE 都会写 pyc。本次运行用的 qlvenv 3.12 不读 cpython-313 的 pyc。该文件保留不动；以后 py_compile 用 cfile= 输出到 /tmp。

## 8. 原因分析与建议（只读，没有运行额外项目代码）
- eval 进程在 HILIQ 段峰值约 1596 MB，FULLA 段当前 RSS 到 1536432 kB 后被杀。build 阶段峰值 1.23/1.37 GB，eval 一个进程里连着跑 HILIQ 和 FULLA（L760 `for uni in ("HILIQ","FULLA")`），每段都读 2024–2026 的面板 PX 并做 pivot（L766–773），再进 pool_benchmarks（2018 起逐年递推）。
- 建议（须 Arch 审，并重签 .ok）：
  - eval 内存要降到 1.5GB 以下。办法包括：按 uni 拆成两个进程；PX 只读需要的列并转 float32/category；pool_benchmarks 逐年处理后及时 del 释放。
  - 另一条路是由主 Agent/Arch 裁定是否调整上限。按红线，AI 不能自行放宽。
  - 看门狗也该改成同时检查 VmHWM 或 ru_maxrss，避免峰值超限却漏检。
- 续跑要求：本 .ok（b21e9952…）按 §10 视为已用，续跑需新签。主口径目录里已有 r2.9 的 fund/build 产物和失败 eval 的部分产物，output/ai_factory 下也有失败 eval 写的 2 个权重 parquet 和 2 个 run_meta。CMC 的 leaf_path() 会按最新 stamp 解析到这个 top10_100w 文件，所以续跑前**必须**由 Arch 决定作废移位这些文件。
