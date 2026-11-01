# 叶23 r2.11 X2 运行回执 — **STOP @ A02（C5：运行窗口内有其他 research 进程）**
- 脚本 4aa19627…（HEAD 1a5b8d9 blob cfcd6a41 = 工作区文件）；.ok e646d9b5…；.cmd 9ce88287…（头注释钉步骤表 14899dc8 + 增补 876ee6b0，经 .ok tool_cmds_sha256 间接钉住）；步骤表 14899dc8 与增补 876ee6b0 §5 的 27 条 A 行逐字节 diff 相同（已人工核对）。Data STOP 证据 e4c44b09。
- 执行器 /tmp/l23run211.py：逐字取步骤表 A 行，串行，无 || true，不重试；0.3 s 采样子进程 VmHWM 与 ps。server.py（PID 80415）按 Arch 放行不计入。

## 步骤
| 步 | 开始–结束 ET | rc | VmHWM kB | meta peak_rss_mb | meta sha | 判定 |
|---|---|---|---|---|---|---|
| A01 eval HILIQ | 07:04:33–07:05:23 | 0 | 1067736 | 1042.1 | eval_HILIQ_meta 188e9310… | PASS（五条全满足） |
| A02 eval FULLA | 07:05:23–07:06:15 | 0 | 1184912 | 1156.6 | eval_FULLA_meta 78662166… | **FAIL C5** |
A02 的 C1–C4 全满足（9 行 pb peak_check + peak_check eval FULLA + STAMP 20261018_070527，无 B3 STOP/硬断言/RSS_GUARD_KILL），但运行期间 ps 采到另一进程：
`python3 research/intel/intel_run.py --mode preopen`（PID 722823，RSS 约 108 MB，父进程 722822 为 python3 -c 包装，系统 python3，非 qlvenv）。来源非本执行器；停跑时已退出。是否读真实数据未核实，按增补 §3-5 即停。A03–A27 未执行；主口径回执（PRIMARY）因 A03 未跑而未写。

## 产物 sha（保留原位，未动）
- HILIQ：summary_HILIQ_20261018_070437 75faf9cb…；weights top10_100w_x2 06791078…、top6_60w_x2 d4fb418f…、top10 cap20 7fa8ee88…、top6 cap20 63d64393…、top20 5445cfe1…；外部 daily_weights top10 06791078… / top6 d4fb418f…，run_meta top10 7a607193… / top6 fc7f6438…
- FULLA：summary_FULLA_20261018_070527 84a4792c…；weights top10_x2 a15170fe…、top6_x2 36da3a34…、top10 cap20 b754c734…、top6 cap20 b78c9e10…、top20 88311c2d…
- 日志 logs/A01.log f28ec1f6…，logs/A02.log 97b89e72…，logs/steps.jsonl，logs/runner.out。

## 参考读数（非正式；merge 未跑）
- HILIQ decisive：t_hac_ge_2_50=False，wb_floor_pass=False，beats_poolEW=False，beats_capadv_hiliq_recomputed=True，verdict_cap=FAIL。60万 CAGR244 3.18%/252 3.28%，MDD −21.96%，HAC t −1.40；100万 4.39%/4.54%，−22.72%，t −0.82。
- FULLA：60万 13.98%/14.47%，MDD −17.30%，t 0.21；100万 18.41%/19.07%，MDD −20.15%，t 0.77。
- 两档 |t| 均 <2.50。沿用名·日：HILIQ 3717、FULLA 5376（not_suspended 0）。N4 中位排除名数 HILIQ 117 / FULLA 124。B3 FULLA 两条旧不一致已消失。
- 内存口径（Arch P2-1）：FULLA eval 上界约 ≤1380 MiB（实测 1157 MiB）；敏感性 build FULLA 参照 r2.9 实测 1373.7 MiB；硬线 1536000 kB。
- P3-2：carried_to_window_end 仍按 VAL 为空判定，窗口末 restored 沿用行不入披露清单（只影响披露）。
- 披露：数据截止 20261014；301139.SZ 有缺口；qlvenv 3.12.14 / pandas 3.0.6 / pyarrow 25.0.1；resume r2.9 meta f393b3e9 / fb4b2ad4 / 07391924。
- .pyc 未删（叶23 未完成）。未改代码/.ok/.cmd，未碰 _void，未提交。
