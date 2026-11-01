# Arch：叶23 r2.7 X2 授权运行条件（.ok 附带条件文件）

- 写入：Arch，2026-10-18T05:44:14-04:00。.ok 白名单不能带额外键，所以本次运行的附加条件写在这里；本文件和 .ok 一起生效，违反任一条即视为未授权运行。
- live=false；promotion=false；promotion_approved=false。

## 1. 授权文件
| 文件 | sha256 |
|---|---|
| output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok（54 键，只读 0444） | 82d79d23f6cea72b5c4aea546a1dc262af16d481ce26c75f8712088f3ffe205d |
| output/ai_factory/ARCH_TOOL_CMDS_LEAF23_X2.cmd | 19db13ccdd9c082f4c139283adfd1278500f414284f8694d7553a7791a855658 |
| 脚本 research/g1g5_sue_desens_cs_alpha.py（r2.7，= commit 62000993 blob，= HEAD 7dd5bea5 blob） | 3d094e22d3af3e3cfe4d3c6164fc3d817c93cb92edfc339db2a156981933adc1 |
| 预注册 docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md | 8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e |

- issued_at=2026-10-18T05:42:25-04:00；expires_et=2026-10-19T04:30:00-04:00（见 §3）。
- 键集合按 AST 抽取 set(OK_FIXED)|set(OK_REQUIRED)|set(TOOLS)|set(TOOL_CLOSURE)：19+9+22+4=54，无多余键。
- 离线校验：/tmp/l23_check_ok.py（0027072b…，逻辑按文本照抄 read_ok/白名单/OK_FIXED/tz_iso/not_expired/cmc_cmd_ok/TOOLS+TOOL_CLOSURE sha/verify_panel，未 import 项目代码），90 项全部 PASS。

## 2. 运行次序
1. 主口径：fund → build_HILIQ → build_FULLA → eval。
2. 然后 4 个敏感性逐个跑：sig-sue → denom-daily → nofc → bo40，每个都按 fund → build_HILIQ → build_FULLA → eval。
3. 全程串行，每个进程必须在上一个进程 exit 0 之后才启动；任何一步非 0 退出即停下报 Arch，不重试、不清理目录。
4. 各阶段之间不需要 Arch 逐步审（取代 FIX5/FIX6 审查 §11 第 5 条的逐步审要求）：脚本用阶段 meta 链（check_meta/verify_upstream/verify_primary_eval）串联，敏感性的 fund 要求主口径 eval_meta 完整。全部 20 个进程跑完后整体交回执。
5. 输出目录：主口径 output/ai_factory/leaf23_sue_desens_cs；敏感性 output/ai_factory/leaf23_sue_desens_cs_<tag>（tag = sig-sue / denom-daily / nofc / bo40）。签发时 5 个目录都不存在。

## 3. 时间窗
- 计划窗口：签发起至 2026-10-19 04:30 ET。.ok 的 expires_et 就是 2026-10-19T04:30:00-04:00，脚本在 authorize 和每个阶段开始（panel_recheck）都会核对，过期即拒。
- 2026-10-19 04:30 ET 之后不得启动任何叶23 阶段。
- 原因：Data 的 nightly_update 工作日 05:55 ET 运行（下一次 10-19 05:55），它的 events 步骤会写 data/v2/events 并重写 forecast manifest，钉住的 sha 会失效。
- 如果 04:30 前没有全部跑完：AI 在阶段边界停下并报告。nightly 照常运行，Data 不跳过、不推迟，因此 Data 不需要额外 .ok。nightly 之后续跑必须由 Arch 新签 .ok，重新钉 forecast parquet 和它的 manifest。
- 10-19 16:40–18:40 ET 的禁跑窗（补数重启前后 1 小时）在 expires_et 之后，已被这次有效期覆盖。
- 不得与补数重启、任何 Data 运行、其他研究运行或 selftest 重叠（包括 Alpha CMC、Strategy、Intel 的运行和自测）。脚本 process_check 会拒绝其他 cmdline 同时含 python 和 research/ 的进程，以及 scripts/fix_sd1/、scripts_eng/、scripts/nightly_update.py；scripts/acquire/ 只记录不拦截，所以 94322 必须按 §5 人工 STOP。

## 4. 每个阶段的确切命令
解释器：/workspace/qlvenv/bin/python（CPython 3.12.14，uv venv，include-system-site-packages=false）。site-packages 里有 numpy 2.5.3、pandas 3.0.6、pyarrow 25.0.1（另有 scipy、statsmodels）；脚本及其唯一项目依赖 research/g1g5_fund_resid_alpha.py 只 import 标准库 + numpy/pandas（pyarrow 作为 parquet 引擎）。只按目录核对，未运行脚本。
- 其他候选：/workspace/QuantLab/.venv_opt/bin/python（3.13.5；numpy 2.5.4、pandas 3.0.6、pyarrow 26.0.0）和系统 python3（3.13；numpy/pandas 在 /usr/local/lib/python3.13/dist-packages，pyarrow 26.0.0 只在 ~/.local）也满足 import。叶19/20 当时用的是系统 python3（leaf20 build.log）。本次统一用 qlvenv，20 个进程不得换解释器；回执里写 sys.version 和 numpy/pandas/pyarrow 版本，并披露与叶19/20 环境不同。
- 每条命令必须在本仓库根目录、在 nice 0 的 shell 下执行，使进程 niceness = 10（脚本要求 ≥ 10）。

主口径（--signal dep --denom fixed --blackout 20 为默认值，不另写）：
```
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni FULLA
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage eval
```
敏感性（每个变体只改一个因素，tag 必须在 sensitivity_specs 里）：
```
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund --signal sue
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ --signal sue
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni FULLA --signal sue
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage eval --signal sue
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund --denom daily
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ --denom daily
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni FULLA --denom daily
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage eval --denom daily
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund --no-forecast
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ --no-forecast
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni FULLA --no-forecast
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage eval --no-forecast
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage fund --blackout 40
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni HILIQ --blackout 40
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage build --uni FULLA --blackout 40
cd /workspace/QuantLab && env -u QL_X2_EXTEND_END PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/g1g5_sue_desens_cs_alpha.py --panel-dir /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix --arch-ok /workspace/QuantLab/output/ai_factory/ARCH_RUN_AUTH_LEAF23_R2_7_X2.ok --stage eval --blackout 40
```
- 次序固定为 sig-sue（--signal sue）→ denom-daily（--denom daily）→ nofc（--no-forecast）→ bo40（--blackout 40）。不得组合多个变体参数，不得加 --sealed。

## 5. 94322 与 data/v2/events
- 94322 现状（签发时）：`ps` 为 `Ssl`，cmdline `python3 scripts/acquire/remaining_after_stk_surv.py`（2d9cf67f…，导入 scripts/acquire/queue_chain_20261014.py 208cb552…），cwd /workspace/QuantLab，日志 logs/remaining_after_stk_surv_restart_20261018_0122ET.log。
- 它的 __main__ 只跑三步：org_norm（已有 DONE 标记，跳过）、fund_portfolio、broker_recommend。写入路径：data/v2/tushare_raw/fund_portfolio_dh/、data/v2/tushare_raw/broker_recommend/、data/v2/events/fund_portfolio_2018plus*、data/v2/events/broker_recommend_2018plus*（org_norm 若重跑还会写 data/v2/events/report_rc_org_name_map.*）、docs/v2/DATA_*_RECEIPT_ZH.md、output/markers/、output/remaining_queue_status.json。**不写 forecast_2024plus.parquet，也不写 adj_factor**（tushare_raw/adj_factor*、data/v2/adj/ 都不在它的代码里）。CMC 工具经 adj_price 读 adj_factor，与 94322 不交叉。
- forecast_2024plus.parquet 的写入方是 scripts/acquire/forecast_history_pull.py（94ed8e72…），文件 mtime 2026-10-18 01:14 ET，签发时 `pgrep -af forecast_history_pull` 无输出。
- **STOP 要求不变，理由改为**：94322 写同一个目录 data/v2/events，并且要限制运行期间的资源和 API 占用。Data 在主口径 fund 启动前对 94322 发 SIGSTOP，留 `ps -o pid,stat,args -p 94322` 显示 T 的原文证据；最后一个敏感性（bo40 eval）exit 0 之后，或运行在阶段边界停下并报告之后，才发 SIGCONT。
- Data 在叶23 全部运行（含敏感性）结束、且 Arch 审过回执之前，不得启动 forecast_history_pull 或任何其他写 data/v2/events 的程序（nightly_update 按 §3 处理：04:30 后不再启动叶23 阶段）。
- 签发时记录的 sha（data_forecast_sha256 已由 .ok 钉住）：
  - data/v2/events/forecast_2024plus.parquet = f1e59284c0a77eeca7eebb3005efce6c90d98639fb907b11dc2278ed9ad4a3e5（manifest 内 sha256 字段也是这个值）
  - data/v2/events/forecast_2024plus_manifest.json = 0bdabc4760e22e516b24089b339596d30e739b927126d605d245834c3c7f90f3
- 如果 94322 在叶23 开跑前翻页完成并自动合并 fund_portfolio_2018plus / broker_recommend_2018plus，可以接受：grep 确认叶23 脚本和 research/g1g5_fund_resid_alpha.py 里没有 fund_portfolio、broker_recommend、report_rc 任何字样，叶23 不读它们。这两份合并产物在任何消费者使用之前须经 Arch 审。

## 6. 每个阶段启动前的检查（20 次都做，原文写进回执）
```
date +%Y-%m-%dT%H:%M:%S%:z
pgrep -af forecast_history_pull
sha256sum data/v2/events/forecast_2024plus.parquet data/v2/events/forecast_2024plus_manifest.json
sha256sum data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
ps -o pid,stat,args -p 94322
pgrep -af python
grep MemAvailable /proc/meminfo
```
- 时间早于 2026-10-19T04:30:00-04:00；pgrep forecast_history_pull 无输出；两个 forecast sha 等于 §5 的值；94322 为 T；MemAvailable ≥ 2GB（2097152 kB）；没有其他研究/Data 进程。任何一项不符就不启动，报 Arch。
- sw_l1_pit：data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 必须 = 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c（签发时实测一致，= D1b 回执 pins.sw_l1_sha256）。注：叶23 不直接读这张表，行业来自面板 ind 列（面板由它构建），所以这里是记录型复核。

## 7. 只记录、不进 .ok 的钉
- suspend_flags_v2：data/v2/suspend_flags/suspend_flags_v2.parquet = ac5c10fde28a5dfbea10b755a2b79df1fc876690c1c7d7aebf5134f53a447377。
- stock_delisted_v2：data/v2/ref/stock_delisted_v2.parquet = 9d757b96bb27540ea02ca0af323aacfb3880797604830a3984eb6fa4fdff3750。
- grep 结果：叶23 脚本和它唯一导入的项目模块 research/g1g5_fund_resid_alpha.py 都**不读** suspend_flags 和 stock_delisted（v1、v2 都不读）。停牌信息来自面板 is_resume_day/hiliq_carry 和 mask 的 suspended 列；退市来自 delisted_master（data_delisted_sha256，已钉）。
- CMC / 工具闭包额外文件（AI 列出的，Arch 实测；不进叶 .ok，到 CMC .ok 时再钉）：
  - research/alpha_v1_1_runguard.py = 35991407875094fd9a456b69fda2b48a059f6a140ed48c6f84a9fc2cda8267b6
  - quantlab/metrics.py = a822dfee88b2f524af61ac1de9fae149885f46c4363e93414897c1c77b4bfb62
  - quantlab/platform/strategy_feed.py = bf37b40173402754160bdd5291408b356c8857c075528c6ae55a702a6bc428b8
  - research/ai_debate_memory_runner.py = e1736d80c589ecd717731dc38ae99a52f3d448da9841b2c3794ee008f59613ea
  - research/g1g5_wiring.py = ff510148a8d0c571680986c8345b5d83e70fd572eca80206b1383f3c35da8c54；research/g1g5_expand_g6.py = b2d26c0d26933778df62af99828dc58e17d37f94432004ca2d2de94ed2ba1a16
  - docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest = ab91f3e0cc3c81013a46da3fee2432f61fe717e3c8c3b16a8ea930b29dbc538c（sha256sum -c 全部 OK）
  - data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet = 346d0dda8a95e8d209fd388cfb1aad5425745fc0b5eb0a16dd4de3ab3d72a1ef（= D1b pins.float_mktcap_sha256）
- ok_runner_pin：AI 说找不到，这一说法不对。文件在 scripts_eng/ok_runner_pin.py，sha c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485（= CMC 文档第 28 行所写 c7805d9a）。CMC 第 108 行先把 ROOT/scripts_eng 插进 sys.path 再 import，所以能找到。但它**没有被 git 跟踪**，签 CMC .ok 前须提交。只影响 CMC 步骤，不影响叶23。

## 8. 资源
- 命令前缀 nice -n 10，进程 niceness = 10；MemAvailable ≥ 2GB；RSS ≤ 1.5GB（脚本看门狗 1536000 kB，超限 os._exit(137)，按失败处理报 Arch）。
- 命令前缀 env -u QL_X2_EXTEND_END；不设 RLIMIT，不用 /usr/bin/time。

## 9. 回执必须包含
- 每个进程：启动/结束时间（date 原文）、命令原文、exit code、§6 检查原文、`pgrep -af python` 与 `ps -o pid,stat,ni,rss,args` 原文、/proc/<pid>/status 的 VmPeak 与 VmHWM（进程结束前采样）、stage meta 的 peak_rss_mb、各 *_meta.json 的 sha。
- 94322 的 SIGSTOP / SIGCONT 证据（ps 原文，含时间）。
- 7 只退市股 000416.SZ、000961.SZ、002699.SZ、300116.SZ、300495.SZ、600321.SH、600823.SH 在 X2 内 S=True 的名·日数：预期 0；非 0 停下报 Arch。
- diag 里 delisted_master_max_delist_date = 2026-07-30。依据 Data 计数 docs/v2/audit/data_delist_count_leaf23_24/out.txt（b54705fd9355e3062b252335c3dfeca75fd6859d74a1bd3aca036f0b477b3eb6；SHA256SUMS 三个文件 sha256sum -c 全部 OK；out.txt 第 29 行 max delist_date 2026-07-30，输入 master sha 63590f23 = 本 .ok 的 data_delisted_sha256）。
- FIX5/FIX6 审查 P3-6 的核对：每个 uni 的 diag *_primary_cut_delist_date 等于 bench poolEW_cagr244 / wb_cagr244；主口径与影子口径截断名数、名·日数。
- 披露：数据截止日 20261014；301139.SZ 数据缺口；非主口径一律「未做多重检验校正，仅披露」；影子口径只披露，不进判定，不计家族次数。
- eval 产出的 HILIQ 权重文件 g1g5_sue_desens_cs_top6_60w_daily_weights_<stamp>.parquet / g1g5_sue_desens_cs_top10_100w_daily_weights_<stamp>.parquet 的 sha（CMC .ok 要钉）。

## 10. 单次有效
- 本 .ok 只用于这一次（主口径 + 4 个敏感性共 20 个进程）。运行结束或停下后由 Arch 归档 .ok，不得复用；续跑需新签。
- live=false；promotion=false。
