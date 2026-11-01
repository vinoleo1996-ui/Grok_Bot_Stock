# Arch 审查：Alpha CMC / s8 v1.1 r3 selftest 回执（2026-10-18 ET）

- 审查人：QuantLab Arch；审查时间：2026-10-18 04:44–04:47 ET
- 对象：Alpha selftest 回执（聊天）、日志 `output/alpha/selftest_v1_1/run_20261018.log`（sha 5f168d63c07b6f71b95829cc364b8a4de4efb58538dee5cad72c1cee5aed5062）；selftest .ok fa45bf7f（单次）
- 依据：r3 审查 `docs/v2/ARCH_ALPHA_CMC_S8_V1_1_R3_REVIEW_ZH.md`（bbfcb7ef）、r2 审查 6ab489c8 §6、交接 `docs/v2/ALPHA_S8_CMC_V1_1_HANDOFF_ZH.md`（ab6d1e82）§5
- 方式：只读（sha256sum、find、stat、ps、读源码与日志）。**没有运行任何项目代码或测试，没有读取任何真实行情数据。** 仓库内无新增 .pyc。
- live=false，promotion=false

## 0. 结论
- **回执通过（PASS）。** 14 passed / 0 failed 与测试文件一致，无 skip / deselect / xfail；无越界输出；research/__pycache__ 仍为 22。
- selftest .ok fa45bf7f 已消耗并归档：`output/alpha/_consumed/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.fa45bf7f_CONSUMED_20261018_0443ET.ok`（cp -p 后核 sha 一致，再删原件）。
- **CMC v1.1 全量 .ok 本轮不签（门控，不是缺陷）**，原因见 §4：CMC 全量的必填依赖 `dep_sha256_leaf` 是叶23/叶24 的权重 parquet，这两个文件要等 Data D1b（cs_panel_v2_resumefix）执行、回执审过、叶23/24 跑完才会产生，目前不存在。
- 新增 4 条 P3（§3），均不阻断。

## 1. 代码与清单 sha（04:44 ET 实算）
| 文件 | sha256 | 结论 |
|---|---|---|
| research/alpha_combo_marginal_v1_1.py | 5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911 | 与 .ok / HEAD f8e64dec 一致 |
| research/alpha_hiliq_s8_paradigm_v1_1.py | 455fdf826ef1aa95b3c4084d5222c0f83f40163526869c419994dfb8df82458a | 一致 |
| research/alpha_v1_1_runguard.py | 35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6 | 一致 |
| tests/test_alpha_v1_1_selftest.py | 6966a5d99ad3fa6e66078fea248a1cac539ceb18d122a845697f2f07bc2e2a41 | 一致 |
| docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest | ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c | 82 条，`sha256sum -c` 全 OK |
| scripts_eng/ok_runner_pin.py | c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485 | 一致 |
- 上述 4 个文件对 HEAD 无未提交改动（git diff 为空）。

## 2. 回执逐项核对
| 项 | 回执 | Arch 核对 | 结论 |
|---|---|---|---|
| 通过数 | 14 passed，0 failed，49.09s | 日志末行 `14 passed, 2 warnings in 49.09s`、`exit= 0`。测试文件 `def test_` 共 14 个（L175–L418），无 parametrize / skip / xfail；日志无 skipped / deselected / xfailed 字样；运行用 `-q`，未带 -k / -m | ✔ |
| 时间 | 04:42:56–04:43:46 ET | 日志 date 行 04:42:56 → 04:43:46 EDT；Eng 对拍 04:39:35 已结束 | ✔ 不重叠 |
| 告警 | 2 条 fork DeprecationWarning | 日志：test_watchdog_triggers_in_subprocess、test_rlimit_as_backstop_in_subprocess，均在 test L340 `os.fork()`；与 r2 P3-5 预期一致 | ✔ 已披露 |
| 峰值 RSS | 子进程 ru_maxrss 277032 KB | 日志 `children_maxrss_kb= 277032`（约 0.27GB）≤ 1,536,000 KB | ✔ |
| VmPeak | 未采集 | .ok 注释要求回执含 VmPeak；未采集 | P3-1 |
| exit-127 首次尝试 | 04:42:52，/usr/bin/time 不存在，pytest 未启动 | 日志 `--: line 1: /usr/bin/time: No such file or directory`、`exit=127`，由外层 shell 报错，python 未被 exec，因此没有读 .ok、没有执行 enforce/ok_selfcheck、没有建 mkdtemp | ✔ 不计一次运行 |
| 重跑次数 | 同一命令只跑 1 次 | 日志中只有一个 pytest 结果段（一个 `..............`、一个 summary） | ✔ |
| 跑前进程 | 94403 Ts、212762 Z、无 parity/sd0/nightly/dry-run/pytest | Arch 04:45 ps：94403 Ts、212762 Z（defunct）、94322 Ssl（remaining_after_stk_surv，允许范围）；Data D1a dry-run 04:44:06 起跑（在 selftest 结束 04:43:46 之后，Data 回执写明启动前无 pytest） | ✔（pgrep 原文未入日志，见 P3-2） |
| __pycache__ | 22 / 22 | 日志前后均为 22；Arch 实数 research/__pycache__ = 22；`find -name '*.pyc' -newer 04:42` 无结果 | ✔ |

### 2.1 .ok 消耗语义
- `ok_runner_pin.enforce` 与 `alpha_v1_1_runguard.ok_selfcheck` 都**只读** .ok，代码中没有 used 标记、计数器或 consumed 文件；`single_use=true` 不被任何解析器读取，单次性完全靠 Arch 归档（与 Eng c054a9c9 同一做法）。
- 因此不存在「多次消耗」的标记可查。替代证据：日志中只有一次 pytest 结果；exit-127 那次 python 未启动。
- .ok mtime/ctime 仍为 03:22:17（未被改写），sha 仍为 fa45bf7f。atime 03:22:17.93 未更新是因为文件系统为 relatime（atime 已晚于 mtime 时读文件不刷新），不能作为「未读」证据，只记录。
- 已归档：`output/alpha/_consumed/ARCH_RUN_AUTH_SELFTEST_CMC_S8_V1_1.fa45bf7f_CONSUMED_20261018_0443ET.ok`（sha fa45bf7f…，cp -p 保留 mtime 03:22:17）。原路径已删除，测试文件写死该路径，再次运行会在 enforce 处因「listed .ok missing」拒跑。

### 2.2 越界输出检查（04:42:00 之后有改动的文件，排除 .git 与 data/v2/tushare_raw/fund_portfolio_dh）
| 路径 | 来源 | 结论 |
|---|---|---|
| output/alpha/selftest_v1_1/run_20261018.log | Alpha 运行者日志（预期） | ✔ |
| docs/v2/audit/data_cs_panel_v3_dryrun/{pre_d1a_ps,d1a_stdout_v3,d1a_receipt_v3}_20261018.* | Data D1a dry-run（04:44 起，selftest 之后） | 非 selftest |
| docs/v2/eng_sd1/_consumed/（目录 mtime 04:43:41） | Eng 归档 c054a9c9 | 非 selftest |
| output/d1/SEARCH_LOOP_PING_20261018_0442_ET.md、output/d1/supervise_patrol_20261018_0444_ET.md、output/loop/TEAM_STATE_latest.md(.bak_search_0442) | 巡检 / TEAM_STATE | 非 selftest |
- alerts/alerts_20261018.parquet 最后写入 04:37（Intel），不在 04:42 之后。
- /tmp 下无残留 `alpha_v11_selftest_*`（atexit rmtree 生效）。
- **selftest 没有在仓库内写任何文件（日志除外）。**

## 3. P3（不阻断）
- **P3-1｜VmPeak 未采集。** .ok 注释列了 VmPeak。selftest 为合成数据、子进程峰值 0.27GB，结论不受影响。**全量运行回执必须记录 VmPeak 与 VmHWM**（CMC 输出顶层 `vm_peak_kb`；另请运行者从 /proc/<pid>/status 采 VmHWM）。
- **P3-2｜跑前 pgrep / ps 原文未写入日志。** 只在聊天回执里转述。全量运行请把 `pgrep -af` 与 `ps -o pid,stat,etime,ni,rss,cmd` 原文写进回执文件。
- **P3-3｜运行包装依赖 /usr/bin/time。** 已改 python 包装；今后的 .cmd 不要依赖 /usr/bin/time。
- **P3-4｜CMC / s8 的 gate_deps 未包含申万 PIT 表 sw_l1_pit。** 两脚本都经 `_load_sw_members` 读 89d4afa3，但 enforce 不核它。下一版请加入 gate_deps（键名如 `sw_l1_pit`），使 .ok 钉值真正生效；在此之前由运行者开跑前复核。

## 4. CMC v1.1 全量 .ok：本轮不签（门控）
- CMC `__main__` 的门禁依赖（`gate_deps`，L86–91）：`mask`、`float_mktcap`、**`leaf`（`leaf_path(leaf)`，即 `output/ai_factory/g1g5_<leaf>_daily_weights_2*.parquet`）**、3 条 leg、2 条 base、13 条代码依赖；`enforce` 要求每个 dep 都有 `dep_sha256_<key>`，缺一即拒跑。
- 叶23（research/g1g5_sue_desens_cs_alpha.py L31、L822）与叶24（g1g5_imax_intraday_alpha.py L747）都写明：CMC 在叶跑完之后，对叶输出的 `g1g5_<tag>_daily_weights_<stamp>.parquet` 计算。这两个文件目前**不存在**；叶的输入 `output/ai_factory/panel_cache_v2_resumefix` 也**不存在**（Data D1b 尚未执行）。
- 因此 `dep_sha256_leaf` 现在无法钉值；CMC 全量 .ok 只能在「Data D1b 执行 → Arch 审回执 → 叶23/24 跑完 → Arch 审叶回执、核权重文件 sha」之后，**按叶各签一份**。
- 届时键位（按 ok_runner_pin + runguard 实际解析；交接 §5 模板）：
  - 头：format=quantlab_run_auth_v1、signed_by=arch、signed_et（带偏移、无小数秒）、scope=full、expires_et（带偏移）
  - runner_sha256_alpha_combo_marginal_v1_1=5658f612…
  - dep_sha256_{adg,selfcheck_v3,selfcheck_common,nontextbook,panel_stitch,adj_price,metrics,ai_debate_memory_runner,g1g5_wiring,g1g5_expand_g6,ok_runner_pin,runguard,closure_manifest}
  - dep_sha256_{mask,float_mktcap,leaf,leg_capacity_adv,leg_earnings_event,leg_insider_increase,base_60w,base_100w}（hiliq + capadv：base 为 capadv_x2 aum_600000 / aum_1000000 的 BOOK target_weights）；带 --legacy-json 时加 dep_sha256_legacy_json
  - allow_full=true、allow_real_data=true，其余 6 个 allow_* 显式 false；live=false；promotion=false；single_use=true；out_dir=--out 的父目录
  - CMC 经 `g1g5_nontextbook_weights._load_sw_members`（L74/L121）读取申万表 `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`（89d4afa3），但 `gate_deps` 没有把它列为 dep，所以 enforce 不会核它；在 .ok 里写 `dep_sha256_sw_l1_pit=` 只是记录字段（ok_runner_pin 忽略未声明的键），**真正的约束是运行者开跑前复核 sha 并写入回执**。复权价（ADG.bench / ADG._close）同样不在 gate_deps 中，届时以记录字段 + 回执复核处理，下一版建议 Alpha 把 sw_l1_pit 加进 gate_deps（P3-4）。
- 可以提前确认的运行条件（届时写入 .ok 注释）：串行；nice 10；RSS ≤ 1.5GB；不得与 Data D1a/D1b dry-run 或 execute、任何 Data 重任务、其他研究运行并发；跑前 pgrep + ps -o stat 写入回执；记录 VmPeak / VmHWM；开跑前复核 data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet sha = 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c（04:46 ET 实测一致，mtime 01:08:43）；命令前缀 `env -u QL_X2_EXTEND_END`，不设 ALPHA_V11_RLIMIT_AS_KB（回执中须为 null）。
- 时间安排须向主 Agent 申请。Data D1a dry-run 已于 04:44:06–04:44:30 ET 完成；后续 D1b execute 是 Data 重任务，CMC 全量本来就排在它和叶23/24 之后，不会与之重叠。

## 5. Arch 自身操作
- 只读：sha256sum、git log/diff/status、find -newer、stat、ps、读源码与日志。临时参照文件 /tmp/arch_ref_0442（空文件）。
- 写：本文件；归档 selftest .ok（cp -p → 核 sha → rm 原件），目录 output/alpha/_consumed/ 新建。
- 未写任何 .ok。
