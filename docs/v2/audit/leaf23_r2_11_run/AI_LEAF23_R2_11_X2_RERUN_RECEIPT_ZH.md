# 叶23 r2.11 X2 重跑回执 — **STOP @ A01（增补 §3-5 / C5：运行窗口内出现其他 python 进程）**
- 起草：AI（executor），2026-10-18 ET。live=false；promotion=false。未改代码/.ok/.cmd/参数，未碰 _void，未提交，未重试。
- 前置核对（07:11–07:12 ET）：.ok c61409b7252b10e62f8e387fc68af04eaa67d87dead0c2e49501be0a4e75b859；.cmd 9ce88287…（头注释钉步骤表 14899dc8 + 增补 876ee6b0，本身不含阶段命令）；步骤表 docs/v2/AI_LEAF23_R2_11_PROPOSED_CMD.txt 14899dc8…（27 条 A 行，与增补 876ee6b0 §5 逐字节 diff 相同）；增补 876ee6b0…；脚本 HEAD 1a5b8d9 blob sha256 = 工作区 = 4aa19627…。
- 执行器 /tmp/l23rerun211.py（由上次 /tmp/l23run211.py 只改 .ok 前缀、日志目录 logs_rerun、C5 监控扩为全部 python 进程）。放行：80415 server.py、94322（T）；系统常驻 sand-exit-watch(53)/sand-memory-watch(27366)/websockify(204,27427)；server.py 的子进程记录但不计入（运行中仅见 734328 僵尸）。

## 1. 开跑前 ps 全量（07:12:20 ET，logs_rerun/ps_pre_A01.txt）
53 sand-exit-watch；204/27427 websockify；27366 sand-memory-watch；80415 server.py（Sl）；94322 remaining_after_stk_surv.py（Tsl）；734328 server.py 的僵尸子进程 [python3] <defunct>。除放行项外无其他 python 进程。MemAvailable 10863316 kB。

## 2. 步骤
| 步 | 开始–结束 ET | rc | VmHWM kB | meta peak_rss_mb | meta sha | STAMP | 判定 |
|---|---|---|---|---|---|---|---|
| A01 eval HILIQ | 07:12:23–07:13:12 | 0 | 1067168 | 1042.16 | eval_HILIQ_meta 4a1f7ee5fab0349d69b27989460a5ce51774ddbad40e6f71058c7db832e336fd | 20261018_071227 | **FAIL C5** |
A01 的 C1–C4 全满足（9 行 pb peak_check 2018–2026 + peak_check eval HILIQ + STAMP，无 RSS_GUARD_KILL/RSS_WATCHDOG_ERROR/STOP/refused/Traceback，meta 字段与 outputs sha 一致），但运行中采样到两个非本执行器的进程（同一父进程 736626，停跑时均已退出、父进程不可查）：
- `736630 python3 -c import pandas, pyarrow; print(pandas.__version__, pyarrow.__version__)`（系统 python，RSS 约 58 MB）
- `736643 /workspace/qlvenv/bin/python -c import pandas; print(pandas.__version__)`（RSS 约 25 MB）
从命令看是版本查询，不读数据；但按增补 §3-5 与「运行期间不得有其他 python 进程」规则仍判失败即停。来源未知（疑为其他 agent 的环境检查）。A02–A27 未执行；按增补「任一步失败整体作废」，c61409b7 应视为作废，需 Arch 裁决与新 .ok。

## 3. 复现性对比（A01 vs _void/leaf23_r2_11_intel_overlap_stop_20261018，只读）
- 5 个权重 parquet 逐字节相同：top10_100w_x2 06791078…、top6_60w_x2 d4fb418f…、top10 cap20 7fa8ee88…、top6 cap20 63d64393…、top20 5445cfe1…；外部 daily_weights top10/top6 同上，相同。
- summary_HILIQ（437 个叶键）仅 6 处不同，全为时间戳/授权/进程类：auth.arch_ok_sha256、auth.issued_at、auth.process.mem_available_mb、ps_snapshot[4].rss_mb、peak_rss_mb_eval（1042.08→1042.16）、stamp（070437→071227）。新 sha c8fd2ad5…（旧 75faf9cb…）。
- eval_HILIQ_meta：除 arch_ok_sha256、mem_available_mb、peak_rss_mb、ps_snapshot rss、stamp 以及文件名带 STAMP 的 outputs/external_outputs 键外，相同；各输出文件 sha 值不变（summary 与 run_meta 因内含 stamp/ok sha 而变）。
- 外部 run_meta top10 2ec7e1da…、top6 2a8b9153…：仅 arch_ok_sha256 与 stamp 不同。
- 结论：A01 结果可复现。

## 4. 其他
- restored 行说明、FULLA eval 上界（约 ≤1380 MiB，参照 r2.9 实测 1373.7 MiB）、7 名核对、r0.index 核对：均依赖 A02/A03，本次未到，未做。
- 本次 A01 产物（out_dir 6 个 + 外部 4 个，STAMP 071227）留在原位未动，待 Arch 移 _void；否则新 .ok 下 A01 会被 guard_fresh 拒绝。
- .pyc 未删（叶23 未完成）。中间读数按 Arch 要求不在此外传。
- 日志：logs_rerun/A01.log、steps.jsonl、runner_A01_A03.out、ps_pre_A01.txt。
