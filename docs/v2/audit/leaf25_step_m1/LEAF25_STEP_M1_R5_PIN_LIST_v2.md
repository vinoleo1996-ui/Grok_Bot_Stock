# 叶25 步骤 −1 R5 签发钉单 v2（供 Arch 签 ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5.ok）

- 编写：AI，2026-10-18T13:25:15-04:00（取自 `date`）。v2 按 Arch 13:24 核对 v1（1d952cd7，保留不动）后的要求修改：r3e 项、.cmd 改钉 R5b、§5.2/§5.3 顺序与写法、回执内容、STOP 窗口、.ok 有效期。依据仍为主 Agent 13:20 裁定。
- 本文只做静态整理：读脚本/.cmd/manifest JSON/文档文本，对文件算 sha256（逐字节哈希，不解析）、取 mtime 与大小。没有打开 parquet、没有读 schema 或页脚元数据、没有运行任何脚本、没有提交。live=false，promotion=false。

## 一、钉住的代码与文档（全长 sha256）
| 项 | 路径 | sha256 |
|---|---|---|
| 预注册 r5 | docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT_r5.md | 81123646382f7bb188a135e0d9142372b373c079e289d47066f5587a1fde40e1 |
| 脚本 _r5 | research/leaf25_ttm_recon_step_m1_r5.py | f43b901671728204437279da1f49c7729ec11f11d8070e73434b5d6288953d68 |
| .cmd R5b | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5b.cmd | 8d0d35d93da729021a1e96f27f49b496ac48e6f2c279f8fc7a4c1fb49dbdb2a6 |
| （备选）.cmd R5c | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5c.cmd | a6c36ad1a4d1e8aeab3ed72c1f8cf4976e713b52df050e423de3dbe5dc9a5c0b |
| 内存估计 R5 | docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R5_MEM_ESTIMATE.md | c2fef26b1911b061b6c61137737cc5c52ebb6233e98d7566239de06525822e24 |
| Arch 差异复核 R5 | docs/v2/ARCH_AI_LEAF25_STEP_M1_R5_DIFF_REVIEW_ZH.md | 9fb4fccbcdf44cd1e4b4bbd0bb37211d5c06215b2e87e000ec7ebdf5cf7ebebd |
| 包装器 v4 | docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh | 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169 |

- assert=leaf25_ttm_recon_step_m1_r5；tag=leaf25_step_m1_r5
- ok_path=output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R5.ok
- 解释器 /workspace/qlvenv/bin/python；env PYTHONDONTWRITEBYTECODE=1；--meta <out_dir>/run_meta.json；out_dir/log_dir 在 output/ai_factory/_leaf25_ttm_recon/ 下，签发时写成字面值。
- 其余键按 Arch 9fb4fccb 第七节（column_whitelist、allow_*、guard_pid=94322、c4_limit_kb=1331200、stopkb=1484800、rss_limit_kb=1536000、expected_peak_kb=650000、expected_rc=0、single_use、run_serial 等）。

## 二、四个输入文件（来源：_r5 脚本 INPUTS L59–L63 与文档字符串 L7；.cmd 不另列输入）
快照位置：当前盘上的 v2 目录本身（data/v2/financials_pit/、data/v2/calendar/），没有另建副本。sha256 是逐字节哈希（sha256sum），不解析文件；mtime、大小取自 stat。日期范围只抄 manifest 原文，没有打开 parquet 核对。

| 键 | 路径 | sha256 | mtime（ET） | 大小（字节） | manifest 所述范围 |
|---|---|---|---|---|---|
| input_income_sha256 | data/v2/financials_pit/financials_pit_tushare.parquet | bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3 | 2026-10-18 01:09:47 | 47342959 | financials_pit_tushare_manifest.json：rows 422129、instruments 5910、built_at 2026-10-11T09:32；manifest 未写 end_date/ann_date 范围，只有 coverage_report_type1 到 2026-06-30 期 |
| input_cashflow_sha256 | data/v2/financials_pit/cashflow_pit_tushare.parquet | 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79 | 2026-10-18 01:12:34 | 5098386 | bs_cf_pit_manifest.json：rows 315718；end_date 2009-12-31～2026-09-30；ann 2015-01-01～2026-10-10 |
| input_balance_sha256 | data/v2/financials_pit/balancesheet_pit_tushare.parquet | 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5 | 2026-10-18 01:06:48 | 130444287 | bs_cf_pit_manifest.json：rows 451857；end_date 1989-12-31～2026-09-30；ann 1991-06-10～2026-10-13 |
| input_calendar_sha256 | data/v2/calendar/trade_cal_sse_pit.parquet | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 | 2026-10-18 01:13:35 | 77822 | calendar/manifest.json：rows 8035；20050101～20261231；open_days 5343；manifest 内 sha 与本值一致 |

- 四个 sha 与 _r5 INPUTS 现钉值逐字相同，脚本不需换文件名。脚本启动时会再全长比对，不符即 exit 3。
- mtime 都在 10-18 01:06–01:13 ET，是 01:05 box 重启后整体恢复回写所致（见 TEAM_STATE 06:48 条），不是内容变更。
- **已知缺口（披露）**：10-14→10-16 的补跑没有做（方案 R 已作废），这几天新披露的财报不在这三张表里（manifest 中 ann 最大日为 2026-10-10/10-13）。步骤 −1 只做 3 只股票的 TTM 手算对账、验证规则，不依赖最新几天，结论不受影响；正式运行前需按届时数据重钉。

## 三、第二前置：Strategy sw_pit r3e 自测
- r3e 自测 2026-10-18 12:55:50–12:55:53 ET，85 passed / 0 failed，EXIT=0（回执 docs/v2/audit/strategy_r3e/SELFTEST_R3E_RECEIPT_20261018.md，sha256 ec10c0569813b16c2d9a7fb6317856afb8a182cfd00a371e5558e5691037ce91；.ok bf4ee8c7）。r3e 落地件：research/sw_members_asof.py dec73305…，测试 e80f98ed…，预注册 28b89a61…（落地回执 cd379089…）。
- commit sha：**未提交，按文件 sha 钉**。research/sw_members_asof.py dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7；自测回执 docs/v2/audit/strategy_r3e/SELFTEST_R3E_RECEIPT_20261018.md ec10c0569813b16c2d9a7fb6317856afb8a182cfd00a371e5558e5691037ce91，Arch 12:58 ET 受理。
- 说明：步骤 −1 脚本本身不读申万表、不调用 sw_members_asof；此前置是为叶25 冻结链。

## 四、本次运行的一行预注册
- 期望：rc=0；--out 下恰好 3 个输出文件（raw_rows.csv、ttm_script.csv、run_meta.json）；run_meta.rule_exercised 三例（i、ii、iii）全部为 true。任一不符即停、报，不重跑。注：run_meta 的 n_candidates.ii 是 jj 筛选前的代码数，不扣除因 avail_E 被跳过的同生效日候选；n_annual_q1_same_day_all_codes 为自然日口径，只作披露。

## 五、开跑前与运行中清单（所有时刻取自 `date`）
1. 94322 处于 T 或已退出：Data 提供 ps 证据，签发前一次、启动前一次。
2. 静默门禁按此顺序：① 设 output/loop/RESEARCH_QUIET.lock；② 轮询 localhost:8795/healthz，直到 quiet=true（最多 90 秒，超时则停、报，不开跑）；③ 再等 15 秒；④ 再取一次 healthz，确认所有 *_running 标志为 false 且 child_pids={}。四步各留 date 时刻与 healthz 原文。
3. 开跑前手工执行 `pgrep -af '[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py'`（方括号写法避免匹配 pgrep 自身），结果须为空；若不空，等待其自然结束，**绝不 kill**。
4. 运行期间每 30 秒做一次只读采样：同一条 pgrep -af 命令，加 ps 快照，加包装器进程组的 RSS（VmRSS/VmHWM，只读 /proc）样本，带 date 时刻写入回执；只读，不发信号。
5. 单进程、单次、不重试；任何异常停下报 Arch。
6. 运行窗口：只在 Data 的 94322 STOP 窗口内跑。窗口须落在 10-18 18:30–23:00 ET 之间、时长 ≥45 分钟；建议 19:00–19:45 ET，**待 Data 确认**。禁止窗：10-19 04:25 ET 起直到当日纸面各轨跑完，尤其 16:40–18:40 ET。
7. .ok 的 expires_et 须早于 2026-10-19T04:25:00-04:00。
8. 退出码 0 不等于成功：逐个核对三份输出、triggers（E_before/E_after、same_day）、每例 rule_exercised、report_type 计数；rc≠0 到 output/ai_factory/_void/ 取件。.ok 用后由 Arch 归档（AI 不归档，写“待 Arch 归档”）。

## 六、timeout 与包装器 v4 的交互（静态阅读包装器源码，未改包装器、未运行）
- R5b（外层 `timeout 900 bash 包装器 …`）有一个确定会出的问题：
  - 包装器的 C5 只排除自己的进程树（mytree：包装器 $$ 及其子孙，L46）。timeout 是包装器的父进程，不在树内。
  - timeout 的命令行原样含 `… /workspace/qlvenv/bin/python research/leaf25_ttm_recon_step_m1_r5.py …`，命中 C5 命令行模式 `*python*research/*`（L56）。
  - 结论：C5 每次都会把 timeout 判为外来进程 → killgrp → rc=96，.ok 白白作废。
  - 另外：GNU timeout 9.7 到时只向自己的进程组发 TERM；python 已被包装器 setsid 放进新会话（L60），不在该组内，收不到信号。包装器 bash 被 TERM 后没有 trap，直接退出，跳过峰值汇总和 rc≠0 时移入 _void（L80–L98），python 继续无人监管地跑，外层 rc=124。
- R5c（备选，timeout 放在包装器 `--` 之后）：
  - setsid 直接 exec timeout，timeout 就是 PID，PGID=PID（timeout 自己的 setpgid 对会话首进程无效，组不变），PGID 检查通过。
  - timeout 的命令行含脚本路径，--assert 子串匹配通过；它在包装器树内，C5 排除。
  - python 是其子进程、同组，VmHWM 采样覆盖。到时 timeout 先 TERM python 再 TERM 全组，rc=124 经包装器 `wait` 返回，峰值读取与 _void 移动照常。
- 建议：签 R5c（a6c36ad1…）而不是 R5b。本钉单按要求写 R5b，由 Arch 定；若选 R5c，.ok 的 cmd_path/cmd_sha256 改为 R5c。
