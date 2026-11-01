# AI_CMC_V1_1_LEAF24_RECEIPT (CMC v1.1 leaf24 imax_intraday_top10_100w, hiliq/capadv) -- STOPPED rc=3

- .ok output/alpha/ARCH_RUN_AUTH_CMC_V1_1_FULL_LEAF24.ok sha256 43b37e89869832ed5361fade92264d6e6bf70fd371ff26de7ed54453479cd8d7 (expires 2026-10-19T04:30 ET) -- pending Arch archival (dai Arch gui dang)
- precheck 09:02 ET: .ok sha OK; 94322 state T; sw_l1_pit sha 89d4afa337435a23 OK; full ps: only system daemons + 94322; out_dir absent; lock 6afb7c1892a3 OK; research/__pycache__ 24 files
- wrapper /tmp/cmc_l24_wrapper_f757e7ca.sh sha256 f757e7ca721adb2dfc07447fc2b22c13b59dceedc3543d3097fb221e5a903b13 (new file, bash -n OK). Logs: output/alpha/cmc_v1_1_leaf24_logs/
- run 09:02:48 -> 09:04:18 ET; one run only, no retry; top6_60w not run

## Result: rc=3, script self-stop
- log (whole file, 1 line): STOP: peak RSS 1630960 KB > 1536000 KB
- exit=3 stopped=0 PGREP_G_EMPTY 2729381 
- peak: script-reported peak RSS 1630960 kB (from STOP line; peak_rss_kb / vm_peak_kb fields not available: no output JSON written). Wrapper sampler max 2000 kB is INVALID (sampled the wrong process, see below). Peak = 1630960 kB (1592.7 MiB) > STOPKB 1484800 and > hard 1536000.
- gate / ok_selfcheck / closure blocks: NOT AVAILABLE (no output JSON). Output sha: none; out_dir output/alpha/cmc_v1_1_leaf24 never created. _void dir output/ai_factory/_void/cmc_v1_1_leaf24_rc3_20261018_090418 created by wrapper, empty (0 files).
- python pid 2729383 gone after run; pgrep -g 2729383 empty; no alpha_combo process; 94322 still T; research/__pycache__ after: 24 files (unchanged)
- env: PYTHONDONTWRITEBYTECODE=1, QL_X2_EXTEND_END and ALPHA_V11_RLIMIT_AS_KB unset, nice 10, /workspace/qlvenv/bin/python

## WRAPPER DEFECT (AI fault, P-level for Arch)
- Wrapper ran "cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 setsid env ... &": bash backgrounded the whole && list as a subshell, so $!=2729381 was the subshell, not python (2729383, own session via setsid). PGID_MISMATCH logged at start.
- Consequences: (a) VmHWM sampler watched the subshell (2000 kB) -> the 1484800 stop line and 1331200 report line were NOT enforced on python; (b) c5watch flagged the real python as foreign (C5_HIT 09:02:53) and sent kill to the nonexistent group -2729381 ("No such process") -> no effect; (c) pgrep -g 2729381 empty is meaningless; verified separately that pid/pgid 2729383 is gone.
- Python was stopped only by its own RSS guard at 1630960 kB. MemAvailable before ~9 GB, no OOM.
- C5_HIT line is a self-false-positive (the hit IS the step process).
- Fix proposal (not applied, needs Arch): cd first as a separate statement, then "PYTHONDONTWRITEBYTECODE=1 setsid env ... &" so $! is the python pid; abort immediately if PGID_MISMATCH.

## Deviations to disclose
1. Interpreter: /workspace/qlvenv/bin/python instead of bare python3 (approved by Arch in .ok).
2. prereg section 8 names alpha_combo_marginal.py; v1_1 was used (reasons in ab6d1e82 and bbfcb7ef).
- Reading would be gating-only under WATCH (may keep or lower WATCH, never raise; report_to_leo=false); 60w figure disclosure-only (top-6 from top10 file, tie order undefined). No reading produced in this run.

## sha256
```
f60e837db7bd4370dd25d251c25b5d09a3485b5f577a3caa0227b338b42501a7  output/alpha/cmc_v1_1_leaf24_logs/cmc.log
19083226ffcc4ce6299a29bffc4e8be62a0438b7244f71be20e8b3a26d0a6f31  output/alpha/cmc_v1_1_leaf24_logs/cmc_c5.txt
8dcd0f9dcc7f32a22bcff4516158938e6ef692c3bcb51e6ee24a27ae1830dd33  output/alpha/cmc_v1_1_leaf24_logs/cmc_exit.txt
42de2240b1b7f35822779670fb51923d6f7ac57914f904283c161325c55fbd50  output/alpha/cmc_v1_1_leaf24_logs/cmc_ps_after.txt
4f8816b94ef53f73c68db3b24138680a5829ec3564d02399450c1dbe227169bd  output/alpha/cmc_v1_1_leaf24_logs/cmc_ps_before.txt
d215482658ec7d2134b2d551fd83811fad2fd7cae26a310f38f4ca5b7c5196ad  output/alpha/cmc_v1_1_leaf24_logs/cmc_sampler.txt
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  output/alpha/cmc_v1_1_leaf24_logs/start.marker
```

## 修订 1（2026-10-18 09:07 ET，按 Arch 裁定）
- a. PID 关系：2729381 是被后台化的 `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 setsid env ... &` 整条 && 链的子 shell；python 2729383 是它的子进程（setsid 后自成会话/进程组 2729383）。
- b. 采样器 2000 kB 无效：采样的是子 shell 2729381 的 /proc/<pid>/status，不是 python 2729383；停止线 1484800 与报告线 1331200 均未作用于 python。
- c. Arch 裁定：包装器缺陷 = AI P2；未做内存测试即放行完整运行 = Arch P2；.ok 43b37e89 已由 Arch 归档为 VOID；空 _void 目录 output/ai_factory/_void/cmc_v1_1_leaf24_rc3_20261018_090418 保留作记录。
- 批准的修复：cd 单独成句；只把 python 放后台；PGID_MISMATCH 即中止；断言 /proc/$PID/cmdline 含 alpha_combo；采样间隔 0.2 s。
- 叶24 维持 WATCH；叶24 CMC 暂停，待 Alpha/Eng 做脚本级内存改写；期间不运行任何读数据的脚本。
- 包装器副本：docs/v2/audit/cmc_v1_1_leaf24/cmc_l24_wrapper_f757e7ca.sh（sha256 f757e7ca721adb2dfc07447fc2b22c13b59dceedc3543d3097fb221e5a903b13）。

## 勘误 1（2026-10-18 ~09:46 ET）
- 偏差 1（解释器）的理由更正：裸 python3 = /usr/bin/python3 -> /usr/bin/python3.13，**已安装 pyarrow 26.0.0**（用户 site：/home/box/.local/lib/python3.13/site-packages/pyarrow-26.0.0.dist-info，mtime 2026-10-18 01:08:40 ET）。因此「裸 python3 缺 pyarrow」的说法是错误的（注：本回执正文并未写该句，该说法出自转述；此处一并更正）。
- 解释器仍为 /workspace/qlvenv/bin/python（python3.12，pyarrow 25.0.1）；更正后的理由：与自测（selftest）所用库版本保持一致。
- 核验方式（只读，无数据）：ls -l /usr/bin/python3；readlink -f；ls --full-time 上述 dist-info；读取 METADATA 的 Name/Version；ls qlvenv site-packages 的 pyarrow dist-info。
