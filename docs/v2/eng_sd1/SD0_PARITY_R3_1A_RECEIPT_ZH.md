# SD0 纸面对拍回执 r3.1a（Eng；写于 2026-10-18T04:41:34-04:00，America/New_York）

- **结论：通过。8 个 case 全部 PASS_BIT_IDENTICAL，all_pass=true，hash_files_stable=true，没有中止（aborted=None）。runner 退出码 0。**只跑了一次。
- 授权：docs/v2/eng_sd1/ARCH_SD1_EXEC.ok c054a9c99e49f94b03d06f990c13d16849feffca17a4380b3b5abf7c2bd60645（门禁返回 PINNED_MATCH，runner 7e3cc6ef）；Arch 回执审查 docs/v2/ARCH_SD1_R3_1A_RECEIPT_REVIEW_ZH.md d023f51749f5d1be03693a127fbf10e48c6b78202340a67009e105204da2e8f9。主 Agent 04:34 ET 放行，Arch 04:35 ET 确认可开跑。
- 命令（原样执行）：`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 python3 scripts_eng/sd0_parity_runner.py --suite paper --out-tag r3_1a_20261018_7e3cc6ef`。外面包了 RSS 采样器 /workspace/sd1_work/parity_r3_1a/rss_wrap.py（sha 4ab56880bd199d5bd815e69c7415fee18dd72ac8807e9cb8e91541691733873f，selftest_r3_1a 版本的副本，只增加了记录 env 和 nice 的功能，只用 stdlib，不 import 项目代码）。runner 开始 2026-10-18T04:37:11-04:00，结束 2026-10-18T04:39:35-04:00；采样器记录用时 144.65 秒。
- 开跑时间在 13:45 ET 之前，不在 16:40–18:40 ET 内。EXEC.ok 的 expires_et / latest_start_et 都是 14:00 ET，开跑时在有效期内。live=false，promotion=false（报告记录 live=False，promotion_approved=False）。只跑了 paper suite。

## 1. 窗口留证
- (1) Data 留证回执：docs/v2/audit/data_cs_panel_v3_dryrun/sw_terminate_and_stop_20261018.md，sha 40417702fbb13dc429086cfc20d0144e79f42c94457dfdf2b81318b82def066e。
- (2) 父会话 04:33:32 ET 的只读自查：data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 的 sha 以 89d4afa337435a23 开头，mtime 01:08:43；02:28 以后受保护路径没有写入，有写入的只有 hsgt/northbound/tier3_daily/alerts 和 _quarantine/sw_pit_INCOMPLETE_20261018，都不在对拍读取范围内。主 Agent 04:33 ET 独立核对的结果相同（94403 处于 Ts，212762 是僵尸进程，212763 已退出，隔离区以外没有 tmp/part 文件）。
- Eng 本次复核：sw_l1_pit 在运行前后都是 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c，mtime 01:08:43，没有变化。

## 2. 开跑前快照（最后一次，04:37:05 ET；文件 /workspace/sd1_work/parity_r3_1a/final_pgrep.txt，sha eaa69bd32c8e39aa553020bc4a9076411d692166782ef7783d4977eb3f943f2f）
```
2026-10-18T04:37:05-04:00
## pgrep -af 'fix_sd1|nightly_update|relay_outage|tier3|sd0_parity|cs_panel'
94403 python3 scripts/acquire/relay_outage_backfill.py
## ps -o pid,stat,rss,args -p 94403,212762,94322
    PID STAT   RSS COMMAND
  94322 Ssl  140992 python3 scripts/acquire/remaining_after_stk_surv.py
  94403 Ts   35780 python3 scripts/acquire/relay_outage_backfill.py
 212762 Z        0 [python3] <defunct>
## python procs
     53 Rs   14736 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
    204 S    32564 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
  27366 Ss   24188 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
  27427 S    35112 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  80415 Sl   170488 python3 -X utf8 server.py
  94322 Ssl  140992 python3 scripts/acquire/remaining_after_stk_surv.py
  94403 Ts   35780 python3 scripts/acquire/relay_outage_backfill.py
 212762 Z        0 [python3] <defunct>
 450832 ZN       0 [python3] <defunct>
c054a9c99e49f94b03d06f990c13d16849feffca17a4380b3b5abf7c2bd60645  docs/v2/eng_sd1/ARCH_SD1_EXEC.ok
7e3cc6ef0f4a3cf645d64b641834198d5cbea1cce313c505d74a3d3962823542  scripts_eng/sd0_parity_runner.py
373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c  quantlab/platform/execution.py
bfdfa63cbd7f39d7f0b1eb5a9b91ca00a30bdbd21e31ef3b90d89ac6080e99fc  quantlab/platform/__init__.py
```
- 212762 确认为僵尸进程（/workspace/sd1_work/parity_r3_1a/z212762.txt）：
```
2026-10-18T04:35:28-04:00
    PID STAT   RSS COMMAND
 212762 Z        0 [python3] <defunct>
```
- 判定：94403 仍是 T；212762 是 Z，按已退出处理；94322 fund_portfolio 获准继续跑；没有其他 nightly、backfill、cs_panel、fix_sd1 进程。450832 ZN 是 Web server.py 的僵尸子进程，与 Data 无关。04:34:45 ET 的第一份快照见 preflight_ps.txt，结论相同。
- 四个 sha 在开跑前又核了一次：EXEC.ok c054a9c9、runner 7e3cc6ef、execution.py 373fed30、__init__ bfdfa63c，全部一致。

## 3. 读取路径清单（判定依据）
- 依据一：从 book_smoke、v2_multisleeve_book、execution、execution_sd1、quantlab.platform 出发，做静态 AST import 闭包（模块级和函数内的 import 都算），共 67 个模块。在这 67 个文件里用 rg 找出所有 data/ 和 output/ 字面路径，以及 ROOT/"data" 这种拼接写法。
- 依据二：读源码确认的主要读取点：
  - v2_multisleeve_book 的 HASH_FILES 7 个文件，另读 etf/sw_l1_etf_map_pit_daily；
  - run_book → execution.load_execution_panels → v2_readers.load_merged_panel，读 D0 快照 data/local_market/1c85fd9aceaa03c3c4863bec 和 asof_extend_tushare_202610（回退到 asof_extend_202610），以及 cb/、etf/、corporate_actions 分红；
  - futures.load_index_futures_panels，读 data/v2/futures；
  - metrics → trade_calendar，读 data/v2/tushare_raw/trade_cal.parquet 和 asof_extend_202610/calendar.parquet；
  - 6 个权重文件；
  - _vs_ref 读 output/v3/book_smoke_g1g5_capacity_adv_x2。
- 前后快照取的是一个**宽松的超集**（/workspace/sd1_work/parity_r3_1a/snap_inputs.py），以免漏掉：
  - 目录：data/local_market/1c85fd9aceaa03c3c4863bec、data/v2/{asof_extend_tushare_202610, asof_extend_202610, cb, etf, etf_510300, futures, rates, corporate_actions, sw_l1_pit, float_mktcap, ref, suspend_flags, delisted, st_events, share_float, ep, financials_pit}、data/fund、data/sw、output/v3/book_smoke_g1g5_capacity_adv_x2；
  - 单个文件：data/v2/tushare_raw/trade_cal.parquet、6 个权重文件、docs/v2/QuantLab-MANDATE_V2.json、output/d1/ENG_PING_PATHS.json，另加 data/v2/alerts/alerts_20261018.parquet（仅作披露）。
  - 共 51565 个条目，每个都记了 size、mtime_ns 和全长 sha256。
- **tushare_raw**：整个闭包里引用 tushare_raw 的只有 trade_calendar.py 读 trade_cal.parquet（L12）。**不读 fund_portfolio_dh，也不读 tushare_raw 下任何其他目录**（闭包里 rg fund_portfolio 为 0 条）。04:00 以后 tushare_raw 下只有 fund_portfolio_dh/20231231 一个目录有写入，不在读取范围内。trade_cal.parquet 运行前后都是 95261B，mtime 01:08:43，sha 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086，没有在写，也没有变化。
- **alerts 和 risk_flag**：只在 quantlab/portfolio/research_loop.py 和 cli.py 里出现，这两个文件**都不在 67 个模块的闭包里**。闭包里出现的 "alert" 只是 config 中的回撤和拥挤阈值字段名，没有读取 data/v2/alerts 的地方。结论：对拍**不读** alerts，所以不存在「不可判定」的 case。
- 披露：alerts_20261018.parquet 在运行期间被写过：运行前 21176B，mtime 04:04:58，sha 19357c97401052e4edf972983a50436dfba0ca309d488af2598a29dd893b2454；运行后 24204B，mtime 04:37:25，sha 048fcdfb67684603807640b405f61d6eaec7839831f266b521b38f55aa8c0e42。写入方是 Intel 的 alert-ingest（/tmp/alert_ingest_0436.log 04:37:25，output/intel/ALERTS_* 04:37:02），不是 Data。
- 输入快照的结果：51565 个条目里，**只有 alerts_20261018.parquet 变了**。去掉这一项后，快照清单的 sha 前后相同：edf65b2260e0fefe82f11cdd7eb6e86eba2322487de0e80bf5c822745353b909。运行前快照 inputs_before.json 的 sha 是 6d07e71d6b5130bbda466b37cf4e90f90765c146843774ce6e6e5cddf7e0e894，运行后 inputs_after.json 是 553db4d72304cecc7d549fb72ef54aa914729e5439347aa57224bdda1eec5ede。

## 4. 结果
- SD0_PARITY_REPORT.json：f1656fa940d71c43279573146cea35ba2df5256d1af9d64fe8f464fa7dd3140a
- 报告字段：nice=10，hash_files_stable=True，all_pass=True，aborted=None

| case | 状态 | 比对文件数 | px_end | 权重 sha8 | _vs_ref（仅供参考） | CASE.json sha256 |
|---|---|---|---|---|---|---|
| paper_capadv_20261013_60w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-09 | 4348877e | BYTES_EQUAL | a199b59d4164a834460b629546ebac1afd9d6e5019e905142e9352803eb2d25c |
| paper_capadv_20261013_100w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-09 | 4348877e | BYTES_EQUAL | a50f78d7bb44b7754c6bfcf14321abe0103bfddc595916b806fe17f8c6483965 |
| paper_capadv_paper_20261014_r2_60w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | e03028ee | NO_STORED_REFERENCE | 676fb94ebe4440b393e0ad05b0c646a5ef2d79c805617196fba1fbb0a0f289dc |
| paper_capadv_paper_20261014_r2_100w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | e03028ee | NO_STORED_REFERENCE | 1362befa7b557d5342a9632c6f44c10fb6e439cd94af4fedeab8bc6dedbbf9e4 |
| paper_b4_60w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | efcef7c4 | NO_STORED_REFERENCE | 7a391e8317e5c90f2f37986cd2665605c2f99e5fb23ecb1fa01043af8b463036 |
| paper_b4_100w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | 4736c030 | NO_STORED_REFERENCE | 6233b5831270e55e6286ef80cb5f1b50818376d07d7a23e4cfe19ab9b21da06a |
| paper_s6_60w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | 6ce63a79 | NO_STORED_REFERENCE | bcbf5020d641988510f18c059c54ef59f8c0ce528cec9256e5c8e8341184f86b |
| paper_s6_100w | **PASS_BIT_IDENTICAL** | 19 | 2026-10-14 | b1f9ae65 | NO_STORED_REFERENCE | 9ab30e0c3fa66a4e1fcdd3087660d66b5db3d1271a1f6546d6244f1aaa5379de |

- 比对方法是双向的：两边的文件集合必须相同；parquet 逐列比较（浮点用 array_equal 且 equal_nan，同时比 dtype 和 index 的值、类型、名字）；json 去掉 run_id 和时间戳后整体比较；csv 等其他文件逐字节比较；RECEIPT.md 只核对是否存在。每个 case 比对 19 个文件，全部相等。
- _vs_ref：capadv_20261013 的两个 AUM 档，与存档 output/v3/book_smoke_g1g5_capacity_adv_x2 的 X2/BOOK/nav.csv 逐字节相同（BYTES_EQUAL）；其余 6 个 case 没有存档参考。这一项仅供参考，不参与判定。

## 5. 每个子进程（共 16 个，串行；engine_sha256 和 co_filename 全部通过核对）
| case | 引擎 | 开始 | 结束 | exit | engine_sha256 | co_filename | polled MB | VmHWM MB | peak_rss_mb_self | RUSAGE_CHILDREN 累计 MB | 被杀/超限 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| paper_capadv_20261013_60w | pristine | 04:37:11 | 04:37:17 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 630.5 | 685.6 | 685.6 | 685.6 | False/False |
| paper_capadv_20261013_60w | sd0 | 04:37:17 | 04:37:23 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 707.6 | 715.4 | 715.4 | 715.4 | False/False |
| paper_capadv_20261013_100w | pristine | 04:37:23 | 04:37:29 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 707.6 | 718.7 | 718.7 | 718.7 | False/False |
| paper_capadv_20261013_100w | sd0 | 04:37:29 | 04:37:34 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 728.2 | 728.2 | 728.0 | 728.0 | False/False |
| paper_capadv_paper_20261014_r2_60w | pristine | 04:37:35 | 04:37:40 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 733.5 | 738.6 | 738.6 | 738.6 | False/False |
| paper_capadv_paper_20261014_r2_60w | sd0 | 04:37:40 | 04:37:46 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 670.4 | 730.5 | 730.5 | 738.6 | False/False |
| paper_capadv_paper_20261014_r2_100w | pristine | 04:37:46 | 04:37:52 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 742.2 | 757.7 | 757.7 | 757.7 | False/False |
| paper_capadv_paper_20261014_r2_100w | sd0 | 04:37:52 | 04:37:59 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 672.2 | 731.2 | 731.2 | 757.7 | False/False |
| paper_b4_60w | pristine | 04:37:59 | 04:38:10 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 684.0 | 740.0 | 740.0 | 757.7 | False/False |
| paper_b4_60w | sd0 | 04:38:10 | 04:38:22 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 679.4 | 739.9 | 739.9 | 757.7 | False/False |
| paper_b4_100w | pristine | 04:38:22 | 04:38:36 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 720.4 | 747.3 | 747.3 | 757.7 | False/False |
| paper_b4_100w | sd0 | 04:38:36 | 04:38:49 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 690.3 | 752.5 | 752.5 | 757.7 | False/False |
| paper_s6_60w | pristine | 04:38:49 | 04:39:00 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 752.9 | 767.3 | 767.3 | 767.3 | False/False |
| paper_s6_60w | sd0 | 04:39:00 | 04:39:11 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 731.8 | 733.3 | 733.3 | 767.3 | False/False |
| paper_s6_100w | pristine | 04:39:11 | 04:39:24 | 0 | 373fed30 ✓ | quantlab/platform/execution.py ✓ | 670.9 | 732.7 | 732.7 | 767.3 | False/False |
| paper_s6_100w | sd0 | 04:39:24 | 04:39:35 | 0 | 8c7615f7 ✓ | quantlab/platform/execution_sd1.py ✓ | 713.8 | 735.2 | 735.2 | 767.3 | False/False |

- 时间均为 2026-10-18 ET。pristine 应为 373fed30 的 execution.py，sd0 应为 8c7615f7 的 execution_sd1.py，两者都与 EXEC.ok 的 dep 一致。

## 6. 内存
- 采样器：每 0.1 秒采一次，共 1353 次。进程树最多同时 2 个进程（runner 加一个 worker），共见到 17 个 pid（1 个 runner 加 16 个 worker）。
- 进程树 VmRSS 之和峰值 **1031.8 MB**（runner 父进程加当时的 worker）；单进程 VmHWM 峰值 **767.3 MB**；RUSAGE_CHILDREN 的 ru_maxrss 为 **767.3 MB**。都低于 1536MB，没有触发强杀（killed_over_cap=False）。
- runner 自己的轮询：每个 worker 的 peak_rss_mb_polled 最高 752.9MB，peak_rss_mb_self 最高 767.3MB（见 §5）。没有任何 worker 被杀或判超限（FAIL_RSS）。
- env 和 nice（按 Arch P3-R2）：env 记录了 PYTHONDONTWRITEBYTECODE=1、LANG=C.UTF-8、PWD=/workspace/QuantLab；PYTHONPATH、PYTHONOPTIMIZE、QL_SD1_REAL_DATA、VIRTUAL_ENV 均未设置，没有记录任何密钥。采样器自己的 os.nice(0)=0。runner 第一次被采到时 nice=0，因为它在启动后才执行 os.nice(10)，报告里记录的 nice=10；16 个 worker 都是 nice=10。rss.json 的 sha 是 a5e28a3b95554a9c4d4b341ef7fdb3586bba473f8a0b8b2858d1d87a0f52d5f3。

## 7. hash_files_stable
- **true**。运行前后的 HASH_FILES 7 个文件 sha 相同：
  - data/v2/etf/etf_daily_adj.parquet 48b21e84695b120b8621eff11f31f3e47879bfc05c93d3d979ddab9220ffd74c
  - data/v2/cb/cb_daily.parquet 89f59e77fc5c1b3c52e618da8cee72ab7f540d5ca5a919d1b544bdcbb51b5879
  - data/v2/cb/raw/cb_basic_raw.parquet 105829aa6e8a32c23ce32f88ed12838ab2117eac54d8142fb35248b9b18bdf87
  - data/v2/cb/raw/cb_share_raw.parquet bddf7d742b8041cf55f57eef98622459a1ef3d39da439b2d02f9258e3004d48a
  - data/v2/cb/cb_events_actionable_pit.parquet 1dc9e57d5997eb648b9a754ae0df2e9d54b6f0b24b994f347e9dce0a207318f8
  - data/v2/futures/raw/fut_basic.parquet b2464509b445f843f2db0f7439abe024ac1509bcc62508cb67f798ea2f9a0138
  - data/v2/futures/raw/index_daily.parquet 1a820341eb6440a92039af6c4688f5a4f6ed6398116624f69e9bbd1bb6e9d003

## 8. 副作用（运行前后对比）
- pyc：仓内 *.pyc 共 1655 行，运行前后 sha 都是 a26b725264b56cae8f7cab0b3b1e207603ea91723ac0efbd5939337f395896ef，diff 为空，**没有新增 pyc**。
- output/：运行前 13433 个文件。新增的 345 个文件全部在 output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/ 下，是本次对拍的产出。其他变化都来自别的 agent，不是 Eng 写的：
```
< 2026-10-18_04:04:57.8526839040 53381 output/intel/ALERTS_latest.json
< 2026-10-18_04:04:57.8526839040 26309 output/intel/ALERTS_latest.md
> 2026-10-18_04:37:02.9246839040 36134 output/intel/ALERTS_latest.json
> 2026-10-18_04:37:02.9246839040 22414 output/intel/ALERTS_latest.md
> 2026-10-18_04:37:02.9286839040 36134 output/intel/history/ALERTS_20261018_0436.json
> 2026-10-18_04:37:02.9246839040 22414 output/intel/history/ALERTS_20261018_0436.md
< 2026-10-18_02:07:48.8166839040 3134 output/intel/intraday_state.json
> 2026-10-18_04:37:02.9286839040 1484 output/intel/intraday_state.json
< 2026-10-18_04:34:02.8486839040 70797 output/loop/TEAM_STATE_latest.md
> 2026-10-18_04:37:39.9046839040 70759 output/loop/TEAM_STATE_latest.md
```
  - output/intel/*：Intel 的 alert 例程，04:37:02 写入。
  - output/loop/TEAM_STATE_latest.md：其他 agent 04:37:39 写入。
  - **Data 写入**：94322 fund_portfolio 的 output/markers/*.DONE 和 output/remaining_queue_status.json，**在本窗口内没有变化**（diff 里没有它们）。94322 写的 data/v2/tushare_raw/fund_portfolio_dh/ 不在读取范围内。
- /tmp：没有 Eng 的残留。前后 diff 只多了 /tmp/alert_ingest_0436.log（Intel 04:37:25 写入）。tmp_before.txt 的 sha 是 61ed37285844875fb8333f32093a2f57ce78f2d6d6bd75dbe1de2d922327e36c，tmp_after.txt 是 0b6964decdecb4142dcdeea4e482d2c0debcd8be01a28d73a4396b9ea2de9265。
- 运行后复核：execution.py 373fed30 和 __init__ bfdfa63c 都没动。没有碰纸面路径和 FROZEN 文件，没有停任何 Data 进程。

## 9. 输出目录树（共 345 个文件，9.2MB）
```
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/SD0_PARITY_REPORT.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_100w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_100w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_100w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_100w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_100w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_60w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_60w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_60w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_60w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_b4_60w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_100w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_100w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_100w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_100w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_100w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_60w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_60w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_60w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_60w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_20261013_60w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_100w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_100w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_100w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_100w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_100w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_60w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_60w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_60w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_60w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_capadv_paper_20261014_r2_60w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_100w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_100w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_100w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_100w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_100w/sd0
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_60w
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_60w/CASE.json
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_60w/logs
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_60w/pristine
output/_sd0_parity/paper_r3_1a_20261018_7e3cc6ef/paper_s6_60w/sd0
```
- 以 paper_capadv_20261013_60w 为例的叶子文件（其余 case 结构相同）：
```
paper_capadv_20261013_60w/CASE.json
paper_capadv_20261013_60w/logs/pristine.log
paper_capadv_20261013_60w/logs/sd0.log
paper_capadv_20261013_60w/pristine/RECEIPT.md
paper_capadv_20261013_60w/pristine/aum_600000/PX/BOOK/actual_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/PX/BOOK/nav.csv
paper_capadv_20261013_60w/pristine/aum_600000/PX/BOOK/sleeve_weights.csv
paper_capadv_20261013_60w/pristine/aum_600000/PX/BOOK/summary.json
paper_capadv_20261013_60w/pristine/aum_600000/PX/BOOK/target_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/PX/C0/actual_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/PX/C0/nav.csv
paper_capadv_20261013_60w/pristine/aum_600000/PX/C0/summary.json
paper_capadv_20261013_60w/pristine/aum_600000/PX/C0/target_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/X2/BOOK/actual_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/X2/BOOK/nav.csv
paper_capadv_20261013_60w/pristine/aum_600000/X2/BOOK/sleeve_weights.csv
paper_capadv_20261013_60w/pristine/aum_600000/X2/BOOK/summary.json
paper_capadv_20261013_60w/pristine/aum_600000/X2/BOOK/target_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/X2/C0/actual_weights.parquet
paper_capadv_20261013_60w/pristine/aum_600000/X2/C0/nav.csv
paper_capadv_20261013_60w/pristine/aum_600000/X2/C0/summary.json
paper_capadv_20261013_60w/pristine/aum_600000/X2/C0/target_weights.parquet
paper_capadv_20261013_60w/pristine/book_smoke_summary.json
paper_capadv_20261013_60w/sd0/RECEIPT.md
paper_capadv_20261013_60w/sd0/aum_600000/PX/BOOK/actual_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/PX/BOOK/nav.csv
paper_capadv_20261013_60w/sd0/aum_600000/PX/BOOK/sleeve_weights.csv
paper_capadv_20261013_60w/sd0/aum_600000/PX/BOOK/summary.json
paper_capadv_20261013_60w/sd0/aum_600000/PX/BOOK/target_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/PX/C0/actual_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/PX/C0/nav.csv
paper_capadv_20261013_60w/sd0/aum_600000/PX/C0/summary.json
paper_capadv_20261013_60w/sd0/aum_600000/PX/C0/target_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/X2/BOOK/actual_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/X2/BOOK/nav.csv
paper_capadv_20261013_60w/sd0/aum_600000/X2/BOOK/sleeve_weights.csv
paper_capadv_20261013_60w/sd0/aum_600000/X2/BOOK/summary.json
paper_capadv_20261013_60w/sd0/aum_600000/X2/BOOK/target_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/X2/C0/actual_weights.parquet
paper_capadv_20261013_60w/sd0/aum_600000/X2/C0/nav.csv
paper_capadv_20261013_60w/sd0/aum_600000/X2/C0/summary.json
paper_capadv_20261013_60w/sd0/aum_600000/X2/C0/target_weights.parquet
paper_capadv_20261013_60w/sd0/book_smoke_summary.json
```

## 10. 留证文件（/workspace/sd1_work/parity_r3_1a/）
- final_pgrep.txt eaa69bd3…；preflight_ps.txt b6348a7d…；z212762.txt 18afe59b…
- pyc_before/after a26b7257…；output_before 4511afc2…；output_after 0d824cb0…；output_diff 0c7840ba…
- inputs_before 6d07e71d…；inputs_after 553db4d7…；snap_inputs.py 002c9ffd…
- rss.json a5e28a3b…；runner_raw.log 2ce79425…；rss_wrap.py 4ab56880…
