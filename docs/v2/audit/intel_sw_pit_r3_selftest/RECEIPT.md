# 回执：Intel sw_pit freshness r3 代码落地 + selftest（依据两份 Arch .ok）
- T0：2026-10-18T05:42:00-04:00；全部步骤结束：2026-10-18T05:42:29-04:00
- 授权（两份都在有效期内，到期 2026-10-19T05:40:22-04:00；执行时间不在禁跑窗口 10-19 16:40–18:40 ET 内）：
  - output/data/ARCH_CODE_CHANGE_INTEL_SW_PIT_FRESHNESS_R3.ok sha256 49ac45a97eabebb64ed686f152684b97f639f76f24709d00fa8c6739a2037b0e
  - output/data/ARCH_RUN_AUTH_SELFTEST_INTEL_SW_PIT_R3.ok sha256 a907c61496a04a2ac4fa7000bf44cafe3ef560e039a7ff19ceec0d21fcc01a77
  - 审查文档 docs/v2/ARCH_INTEL_SW_PIT_FRESHNESS_R3_REVIEW_ZH.md sha256 3406b57620f1e617bec10dd3b671b7fdccc878d5137622f95bff2d03f9eba755
- 没有联网，没有跑 intel_run 或 dry-run，没有改测试文件，没有写 output/intel、纸面轨或 FROZEN 产物；live=false。

## 步骤
0. 记录 T0、ps、ALERTS 前值（step0_1_evidence.log）。ps 显示最大的进程是 exec-daemon（1.1GB，平台进程）；PID 94322 scripts/acquire/remaining_after_stk_surv.py（约 138MB，Data 的采集任务）不是重任务。
1. ls /tmp/qlrev*、/tmp/arch_intel_r3_selftest：都不存在。另记录到 01:20 merge 任务留下的 /tmp/alerts_dryrun 和 /tmp/latest_before.sha（不属于 qlrev*，未删除）。void 留证 _review/intel_r3_selfrun_void_evidence_20261018.txt sha 4e7cd48d24e018def61dcbc118db09b39f3fa8d951948510fcedb8e85edb41a0。
2. 前置核对全部 OK（step2_precheck.log）：diff 为 ce54e502…257c；4 个文件的当前 sha 与 .ok 的 current 一致；test_sw_freshness.py 不存在。旧文件已归档到 _recovery/intel/sw_pit_freshness_pre_r3_20261018/（cp -p，附 SHA256SUMS）。
3. git apply --check 后再 git apply。三方 sha 核对 THREEWAY OK（step3_threeway.log）。py_compile 只编译到 /tmp/intel_r3_pyc（cfile 指定），5 个文件都编译通过，随后删除 /tmp 下的 pyc；research/ 下新增 pyc 为 0（step3_pycompile.log）。
4. 按 selftest .ok 原样串行执行 3 条命令，每条只跑一次；每条之前都重新核对 3 个测试文件的 sha，都与 .ok 一致（pre_cmd{1,2,3}_test_shas.txt）。
5. 记录 ALERTS 后值（step5_alerts_after.log）。
6. find -newermt T0（step6_find_newer.log），写入方归属见 step6_writer_attribution.log。

## 文件 sha（修改前 → 修改后）
| 文件 | 修改前 | 修改后（= .ok new，三方核对一致） |
|---|---|---|
| research/intel/intel_common.py | 9a725d5cea69a9592f5e03b9d1defae5c924cebeb1c636db73e04e0134a38580 | 25f23dff40e09c1724011bc1bfeb3eefa0bb1a924af67e2ccf27664f65dce74a |
| research/intel/intel_run.py | 0de787c1b6b14b7f59498667e682e8557a2cba828bc40d8783f7a7a8441ff87d | ecebb10b79790e46e7c645ce75fd4453cf9d79a5c6ef0d5a947bd9cde0fa99d6 |
| research/intel/intel_event_study.py | ad95fe43b73a193b186f4a8250319d505d283951fce242488870e099cdf6c2cd | b211b21120e5f2eca77e283674b87e2bddefd28d990fe2467dfae8cf84d5cb4d |
| research/intel/intel_c1_gap_split.py | 2063e6aaa212ac9c5c2dac804d6ce1e7adf5309b5a75b67640224fd325d46d9e | a5edf0feed0cb56331b7a0915780ce281f51b6f2771468be6ca746f78466c8a6 |
| research/intel/test_sw_freshness.py | 不存在 | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33（= _review r3_tests.py） |

## selftest 结果
| # | 命令（原样按 .ok） | exit | passed | stdout sha256 | stderr |
|---|---|---|---|---|---|
| 1 | test_sw_freshness.py（TMPDIR=/tmp/arch_intel_r3_selftest） | 0 | 59/59 passed | 84f96dcaf3752597d600cab0d597605d63ce362e97919738ecaaf140fad10fd4 | 0 B |
| 2 | test_news_classifier.py | 0 | 29/29 passed | 306f990404b29e6f0a92262a0aace1b566e0a50d9428fe99cc0754425e635fd9 | 0 B |
| 3 | test_intel_run_merge.py | 0 | 11/11 passed | daf933c7a38ff3672f8a8fe8330e60868a14a567c9b906cf847546fff770e0f1 | 0 B |
与预期 59/29/11 passed、exit 0 完全一致。

## ALERTS_latest.json 前后对比（readonly_real）
- 前：522966a9a1ac347a57bed3bbb4656b377e6e79cf00a312e46c2b3c0da2ded070，mtime 2026-10-18 04:37:02.924683904 -0400，36134 B
- 后：522966a9a1ac347a57bed3bbb4656b377e6e79cf00a312e46c2b3c0da2ded070，mtime 2026-10-18 04:37:02.924683904 -0400，36134 B
- **sha 和 mtime 都相同**。期间 30 分钟刷新例程没有写入这个文件（最近一次写入是 04:36 的 intraday；05:12 和 05:35 两次都是"无阈值变化"，见看板事件）。

## find -newermt T0（output、data、research）
- output/：没有新文件。
- research/intel/ 目录本身，以及 intel_common.py、intel_run.py、intel_event_study.py、intel_c1_gap_split.py、test_sw_freshness.py：本次 git apply 写入（我们写的）。
- data/v2/tushare_raw/fund_portfolio_dh/20240630/*.parquet：由正在运行的 PID 94322（scripts/acquire/remaining_after_stk_surv.py，01:22:39 启动）写入，属于 Data 采集，与本次无关。
- research/ 下没有新的 __pycache__ 或 pyc。
- 本回执目录 docs/v2/audit/intel_sw_pit_r3_selftest/ 和归档目录 _recovery/intel/sw_pit_freshness_pre_r3_20261018/ 是我们写的，不在 find 的范围内。

## 收尾
- 回执写完后删除 /tmp/arch_intel_r3_selftest（运行后为空目录），并再确认一次 research/ 下没有 __pycache__，见 cleanup.log。

## 日志文件 sha256
- step0_1_evidence.log eb6c36ad97a0b200bf05f23a5078a08710982bdf0184fcc96bb5c99f39882182
- step2_precheck.log 9862da5457262a1787c187444bccac1f062216ec896e1961366737234fade20c
- step3_threeway.log 312aec1ff6f6e636d37b06d38bb934167c4f1468de79f4cd5aaf44aead559992
- step3_pycompile.log e2099768b044faa47d07dc0e6657f87641ae34887b713b044a18fd3042358880
- pre_cmd1_test_shas.txt 84b0acb94b97aeea84ab469ad49dcb87464f9b7c0e8166577240356fcaa5a227
- pre_cmd2_test_shas.txt 84b0acb94b97aeea84ab469ad49dcb87464f9b7c0e8166577240356fcaa5a227
- pre_cmd3_test_shas.txt 84b0acb94b97aeea84ab469ad49dcb87464f9b7c0e8166577240356fcaa5a227
- cmd1.stdout 84f96dcaf3752597d600cab0d597605d63ce362e97919738ecaaf140fad10fd4
- cmd1.stderr e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- cmd1.exit 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
- cmd2.stdout 306f990404b29e6f0a92262a0aace1b566e0a50d9428fe99cc0754425e635fd9
- cmd2.stderr e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- cmd2.exit 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
- cmd3.stdout daf933c7a38ff3672f8a8fe8330e60868a14a567c9b906cf847546fff770e0f1
- cmd3.stderr e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- cmd3.exit 9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa
- step5_alerts_after.log 114a21d24b293abf30db65e6d2f1fe84570b9a92e5191acd27f2b6607f9e01c8
- step6_find_newer.log 80f9bf82ee28dccdc01212797e44df9c7ced22e724c86c31f9ec027d69efc1c5
- step6_writer_attribution.log a47605f034acd475a423844f8390807114afae9141f570c0f2fc4528e00fa86e
- T0.txt 4f983147ff179a3b5433e1d1a13ceb8ea2c06114524de62c10cf3ed8002b986e
