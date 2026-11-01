# 叶23 r2.11 X2 第二次重跑回执（主口径 A01–A03）— **A01–A03 全部 PASS**
- 起草：AI（executor），2026-10-18 ET。live=false；promotion=false。只跑 A01–A03，A04 起等 Arch 审本回执。未改代码/.ok/.cmd/参数，未碰两个 _void 目录，未提交，未重试，未联系任何 agent。上一份回执 0de086f5 保持不变。

## 1. 授权与锁核对（07:20 ET）
- .ok output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_11_X2.ok = cf0fa9a135dd34b4372dfebcd918e20787a3afe54b714aaae4b88bba80e68ca1（issued 07:16:13，summary auth/issued_at 一致）。
- .cmd 9ce88287…；步骤表 docs/v2/AI_LEAF23_R2_11_PROPOSED_CMD.txt 14899dc8…（27 条 A 行，与增补 §5 逐字节相同，上次已 diff 核对，本次 sha 不变）；增补 876ee6b0…。
- 脚本 research/g1g5_sue_desens_cs_alpha.py：HEAD 1a5b8d9 blob 与工作区均为 4aa19627…。
- 锁 output/loop/RESEARCH_QUIET.lock 存在，sha256 6afb7c1892a340fe780647cca317b1bd633f907994816d95907d5bf27f0e8d7c（以 6afb7c18 开头 ✔）。
- out_dir 起跑前无 eval_*/summary_* 产物（前两次已由 Arch 移 _void）。

## 2. ps 全量检查
- 开跑前 07:21:03 ET（logs_rerun2/ps_pre_A01.txt）：只有系统常驻 sand-exit-watch 53、websockify 204/27427、sand-memory-watch 27366、supervise-exec-daemon 323、supervise-egress-tunnel 324、supervise-sand-supervisor 27167、sand-daemon-supervisor 27390、orca-ide 网络工具进程 26762，以及 94322（Tsl）。80415 server.py 已不存在；无 snapshot.py / gen.py / kline.py / server.py / supervise.sh / research / scripts（94322 除外）/ qlvenv 进程。
- 结束后 07:22:47 ET（logs_rerun2/ps_post_A03.txt）：同上，无新增。
- 每步前 checks()：forecast f1e59284 / manifest 0bdabc47 / sw_l1 89d4afa3 一致；data/v2/events 无写打开；94322 状态 T；MemAvailable A01 10863316 / A02 10893476 / A03 11186088 kB。

## 3. C5 监控（Arch 临时书面口径）
- 执行器 /tmp/l23rerun2_211.py（由 /tmp/l23rerun211.py 改：.ok 前缀 cf0fa9a1、日志 logs_rerun2、去掉 80415 豁免、加 C5 扫描）。每步运行中约每 0.1 s（加上扫描自身耗时，实际间隔约 0.1–0.3 s）遍历 /proc 全部进程：cmdline、/proc/<pid>/cwd、/proc/<pid>/fd 打开文件。命中以下任一即终止该步并停：cmdline 或打开文件含 /workspace/QuantLab/data 或 /output；cmdline 含 research/、scripts/、quantlab、snapshot.py、gen.py、kline.py、server.py、supervise.sh、uvicorn；cwd 在仓库内且非 -c 的 python。其余新出现的进程只记录。
- 结果：A01–A03 违规 0。只记录（不停）的新进程：其他 agent 的 shell 包装（bash -O extglob -c …，cwd /tmp/swr5 等）、sleep 2/5（cwd /workspace）、websockify 的短连接子进程（/usr/share/novnc）、一次 curl 本机控制面 Ping（PID 754766，07:21:23，127.0.0.1:14012）。计数：A01 bash 4 / websockify 9 / curl 1 / sleep2 48 / sleep5 9；A02 bash 4 / websockify 10 / sleep2 53 / sleep5 11；A03 sleep2 3。逐条 PID、命令、时间见 logs_rerun2/steps.jsonl 的 c5_record。
- **披露：采样会漏掉很短的进程。** 例：Strategy 的 sw_lookahead_count.py 在 07:04:39–07:05:13 运行，与第一次 r2.11 运行（e646d9b5，A01 07:04:33–07:05:23，已作废）重叠，当时的采样没有抓到。本次采样更密并加了打开文件检查，但仍不能保证捕获寿命短于采样间隔的进程。
- **披露：上次 A01（c61409b7）采到的 736626 的子进程**（python -c 版本查询 736630/736643）经 Arch 说明是 Arch 的叶24 审核：版本查询 + 07:07–07:14 合成内存测试（约 340 MiB）+ 在 /tmp 做的 py_compile 与 pyflakes。
- **披露（本次自身）：** 静默窗口内、起跑前（约 07:20 ET）我用系统 python3 跑过一次只做字符串替换的小脚本，生成执行器 /tmp/l23rerun2_211.py（不读数据、不 import 项目代码、只读写 /tmp）；此后只用 sha256sum / jq / rg / diff / ps 做核对，回执写入用一次 python 原子写。报 Arch 判是否违反「窗口内不起额外 python」。

## 4. 步骤（五条判定 + C5 全满足）
| 步 | 开始–结束 ET | rc | VmHWM kB | meta peak_rss_mb | meta sha256 | STAMP | 判定 |
|---|---|---|---|---|---|---|---|
| A01 eval HILIQ | 07:21:03–07:21:51 | 0 | 1060980 | 1035.39 | eval_HILIQ_meta a4ce5c95a12c9ff260910415c5957eba4b7f80b3bec2ccc21143de6c8b2762cf | 20261018_072107 | PASS |
| A02 eval FULLA | 07:21:51–07:22:44 | 0 | 1178096 | 1149.60 | eval_FULLA_meta 55b9543930571f47f0145415ea83e5efe66938a3b67393ff4409de815c34fbda | 20261018_072155 | PASS |
| A03 merge | 07:22:44–07:22:47 | 0 | 467040 | 455.43 | eval_meta d67922d6b6c23aba809a54707462d7628d49b5465a60847913e0535fe1561b0b | 20261018_072247 | PASS |
- 日志：A01/A02 各 9 行 pool_benchmarks peak_check（2018–2026）+ peak_check eval + STAMP；A03 peak_check merge + STAMP；无 RSS_GUARD_KILL / RSS_WATCHDOG_ERROR / STOP / refused / Traceback；meta 的 stage / script_sha256 / arch_ok_sha256 / variant=primary 正确，outputs 齐全且 sha 一致。VmHWM 全部 ≤1536000 kB，也低于 1300 MiB 目标。
- 产物：summary_HILIQ_20261018_072107 47cb8dda…、summary_FULLA_20261018_072155 49ca84d0…、summary_20261018_072247 a917d624…；外部 run_meta top10 0acdd335…、top6 9fb9620d…。
- 日志 sha：A01.log 23957d63…、A02.log c7278339…、A03.log 41d964c8…、steps.jsonl 8039b453…、runner_A01_A03.out 52c7bcdf…、ps_pre_A01 9154cdaa…、ps_post_A03 3f715c0b…。

## 5. 对上一份回执（0de086f5）的更正
- 上份写「out_dir 6 个」有误：out_dir 实为 7 个产物（5 个权重 parquet + summary_HILIQ + eval_HILIQ_meta.json 4a1f7ee5…），漏数了 eval_HILIQ_meta.json。外部 4 个不变。

## 6. 复现性对比（逐字节，两个 _void 目录只读）
- V1 = _void/leaf23_r2_11_intel_overlap_stop_20261018（STAMP 070437/070527），V2 = _void/leaf23_r2_11_rerun1_verscheck_stop_20261018（STAMP 071227，只有 HILIQ）。
- 权重 parquet 逐字节相同：HILIQ 5 个（top10_100w_x2 06791078、top6_60w_x2 d4fb418f、top10 cap20 7fa8ee88、top6 cap20 63d64393、top20 5445cfe1）= V1 = V2；FULLA 5 个（top10_x2 a15170fe、top6_x2 36da3a34、top10 cap20 b754c734、top6 cap20 b78c9e10、top20 88311c2d）= V1；外部 daily_weights top10 06791078 / top6 d4fb418f = V1 = V2。
- JSON（jq 展平后逐键比，文件名中的 STAMP 归一）。下列差异全部是时间戳 / STAMP / 授权 / 进程快照类，单独列出；**其余所有键（含全部绩效、判定、B3、N4 字段）完全相同**：
  - summary_HILIQ vs V1、V2，summary_FULLA vs V1：auth.arch_ok_sha256（e646d9b5 / c61409b7 → cf0fa9a1）、auth.issued_at（07:02:18 / 07:10:58 → 07:16:13）、auth.process.mem_available_mb、auth.process.ps_snapshot（80415 server.py 条目消失、94322 序号前移、rss_mb 135.8）、peak_rss_mb_eval（HILIQ 1042.08 / 1042.16 → 1035.39；FULLA 1156.56 → 1149.60）、stamp。
  - eval_HILIQ_meta vs V1、V2，eval_FULLA_meta vs V1：arch_ok_sha256、mem_available_mb、peak_rss_mb、ps_snapshot 同上、stamp、outputs/external_outputs 中 summary 与 run_meta 的 sha（因其内含 stamp 与 ok sha 而变；权重 sha 不变）；eval_FULLA_meta 另有 upstream eval_HILIQ_meta sha（188e9310 → a4ce5c95）。
  - 外部 run_meta vs V2：只有 arch_ok_sha256 与 stamp。
- 结论：A01、A02 在三次运行间完全可复现。merge（A03）无历史对照。

## 7. restored 行说明（P3-2）与 B3
- 两侧 b3_pool_carry：carry_mismatch=0、carry_unindexed=0、resume_rows_checked=805；r2.10 FULLA 的两条旧不一致（002868.SZ 2025-04-30、603056.SH 2026-01-14）已消失；mask 停牌 ⟺ restored 硬断言全年未触发。
- 沿用名·日：HILIQ 3717、FULLA 5376，全部为 suspended，not_suspended=0（按 S & sus==1 计，属自洽检查）。
- P3-2：carried_to_window_end 仍按 VAL 为空判定（HILIQ 8 名、FULLA 11 名），窗口末若是 restored 沿用行不会列入该清单；只影响披露清单，不影响判定或校验。
- delisted_master max delist_date 2026-07-30、max last_trade_date 2026-07-29；cut_failure_check（(S & gone) 恒 False）通过。

## 8. 内存口径
- FULLA eval 上界写为约 ≤1380 MiB（参照 r2.9 实测 1373.7 MiB）；本次实测 FULLA VmHWM 1178096 kB ≈ 1150.5 MiB，HILIQ 1060980 kB ≈ 1036.1 MiB。硬线 1536000 kB 不变。

## 9. 7 名核对与 r0.index 核对
- 7 只退市股（000416.SZ 000961.SZ 002699.SZ 300116.SZ 300495.SZ 600321.SH 600823.SH）在 X2 内 S=True 名·日：summary 没有直接字段。能从产物读到的：仅 600321.SH 出现在 FULLA delisted_cut_name_days_x2（552 日被截断；shadow 口径 570），其余 6 名不在任一侧截断清单；cut_failure_check 通过说明截断日后 S 全为 False。直接计数需读面板/权重 parquet，静默窗口禁止额外 python，**本次未做**，待 Arch 指示是否另批一次只读核对。
- r0.index == rr.index：脚本 L890 只有注释，summary/meta 未落该字段，**无法从产物核对**；IX 会再 reindex 到 r0.index，只影响 N4 披露。N4：HILIQ 排除名日中位 117、wb 权重占比中位 22.8%；FULLA 124、21.0%。

## 10. 其他
- 中间读数（判定块等）按 Arch 要求不在此外传；主结果读数以 summary_20261018_072247 为准，待 Arch 审。
- .pyc 未删（叶23 敏感性未跑完）。A04–A27 未跑。
