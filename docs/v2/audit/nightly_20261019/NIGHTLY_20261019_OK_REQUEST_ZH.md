# 10-19 日更 run .ok 申请 v3（Data → Arch；按设计审查 2dada5ed §5 全 17 项与 §6 键草案重写，待签）

- 作者：QuantLab Data；修订 2026-10-18 13:02 ET（原地修改；上一版 9da13049… 已归档 _recovery/data/nightly_20261019/predraft2_20261018T114300/）。
- 驱动 run_nightly_v1.py 63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16（a7292a61 不再申请签发，Arch 2dada5ed 判不可签）；兜底 routine_fallback_v1.py f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f（新文件）。
- 配套：例程草稿 ROUTINE_PROMPT_DRAFT_ZH.md；例程 diff ROUTINE_DIFF_ZH.md；驱动 diff DRIVER_DIFF_vs_predraft2_20261018T130216.diff 与说明 DRIVER_DIFF_vs_predraft2_20261018T130216_ZH.md（含 17 项逐条行号、超时与 Known gaps、写路径清单、94403 结论）；测试回执 DRIVER_TEST_RECEIPT2_20261018T130216_ZH.md；票 docs/v2/tickets/TKT_tushare_proxy_connect15_20261018.md。
- 依据：Arch 2dada5ed（§5 1–17、§6）、Arch 12:16 / 12:24 / 12:36 / 12:38；主 Agent 12:32（1）–（4）；Eng 12:34 / 12:40（tier1_pull 5b70dfed 已合入，code .ok ed56e336）。
- 自报：11:24 ET 曾对真实 trade_cal 跑过一次 cal_restore_v2 拒绝路径测试（脚本在读写目标前退出 2，sha 未变，已报）；此后测试只用 /tmp 假文件。

## 1. 钉 sha（签前请重算；驱动逐个核磁盘文件，任一不符即前置失败）
| 键 / 文件 | sha256（磁盘重算） |
|---|---|
| sha_driver：docs/v2/audit/nightly_20261019/run_nightly_v1.py | 63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16 |
| sha_cal_restore：docs/v2/audit/nightly_20261019/cal_restore_v2.py | 6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4 |
| sha_cal_compare：docs/v2/audit/nightly_20261019/cal_compare_v1.py | 74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc |
| sha_snapshot_tool：docs/v2/audit/nightly_sha_scope_snapshot_v2_20261018.py | c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a |
| sha_scope：docs/v2/audit/nightly_20261019/nightly_sha_scope_20261019.txt | 04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807 |
| sha_nightly_update：scripts/nightly_update.py | ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636 |
| sha_tier1_pull：scripts/acquire/tier1_pull.py | 5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf |
| sha_tushare_proxy：quantlab/data_sources/tushare_proxy.py | ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772 |
| sha_relay_health：scripts/acquire/relay_health.py | 6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f |
| sha_adj_factor_incr：scripts/acquire/adj_factor_incr.py | 723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad |
| sha_tier1_materialize：scripts/acquire/tier1_materialize.py | e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb |
| sha_etf_daily_adj_incr：scripts/acquire/etf_daily_adj_incr.py | ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4 |
| sha_eng_daily_panels：scripts/acquire/eng_daily_panels.py | a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be |
| sha_mid_large_universe_incr：scripts/acquire/mid_large_universe_incr.py | fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b |
| sha_light_event_windows_pull：scripts/acquire/_light_event_windows_pull.py | f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71 |
| sha_forecast_manifest_declare：scripts/acquire/forecast_manifest_declare.py | f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731 |
| sha_fill_hsgt_top10_extend：scripts/acquire/fill_hsgt_top10_extend.py | 36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918 |
| sha_cyq_perf_monthly：scripts/acquire/cyq_perf_monthly.py | 6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f |
| sha_tier3_daily_snapshot：scripts/acquire/tier3_daily_snapshot.py | 64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067 |
| sha_data_freshness_status：scripts/acquire/data_freshness_status.py | a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50 |
| sha_routine_fallback：docs/v2/audit/nightly_20261019/routine_fallback_v1.py | f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f |
| pin_trade_cal：data/v2/tushare_raw/trade_cal.parquet | 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086（磁盘 一致） |
| data/v2/calendar/trade_cal_sse_pit.parquet | fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41（磁盘 一致） |
| data/v2/calendar/manifest.json | 7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4（磁盘 一致） |
| docs/v2/eng_sd1/paper_import_closure.json | 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20（磁盘 一致） |

## 2. 时间盒（两档相同；Arch 第 1 项、主 Agent 12:32）
| 项 | 值 |
|---|---|
| 开跑 | 05:30 ET（驱动拒绝早于 05:25 或 ET 日期 ≠ 20261019） |
| daily_pull 单次硬停 | 30 分钟（daily_pull_max_min=30） |
| call B 预算 | 75 分钟（call_b_budget_min=75）；起跑闸门 起跑 + 75 ≤ 16:00；在 min(起跑 + 75, 16:00) 硬停 → FAILED（CALLB_TIMEOUT） |
| 16:40–18:40 | 任何调用到 16:40 即停树 → FAILED（BLACKOUT）；禁跑期内不启动 |
| 重试 | strict：无。relaxed：仅 reason_code=MAX_RUN，≤ min(2, allow_daily_pull_retry_20261019)，间隔 30 分钟，满足 Q-A3 (a)–(f)；RSS / HANG / 残留 / ATTEMPT_FAILED 一律不重试 |
| expires_et | 建议 2026-10-19T16:40:00-04:00（驱动在 call A 每次尝试前与 call B 前复核） |

## 3. .ok 文本（ASCII、LF、key=value、无行内注释、无重复键；不得含 DRAFT 字样；签发时把 issued_at 换成实际时刻）
以下示例已用新驱动的 parse_ok / check_ok 逻辑在 /tmp 校验通过（见测试回执 T02 与第 5 节）。
```
ok_id=ARCH_RUN_AUTH_DATA_NIGHTLY_20261019
ok_type=run
date=20261019
signed_by=QuantLab Arch
issued_at=2026-10-18T17:30:00-04:00
expires_et=2026-10-19T16:40:00-04:00
single_use=true
live=false
promotion_approved=false
interpreter=/usr/bin/python3
sha_driver=63b5a88462f9f75ae7975f52320bbd6f88433cdf4857bf95c6de557d6d880e16
pin_trade_cal=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086
pin_frozen_closure=6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20
daily_pull_max_min=30
call_b_budget_min=75
call_b_latest_finish=16:00
rss_stop_kb=1484800
rss_hard_kb=1536000
blackout_et=16:40-18:40
allow_kill_scope=driver_descendants_exact_pid
allow_trade_cal_step=false
allow_sw=false
allow_force=false
allow_delete=false
allow_commit=false
sha_cal_restore=6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4
sha_cal_compare=74093ff3be4c431bab8c469307b207b43b8e1cff707dd0bac1319a7e265cddfc
sha_snapshot_tool=c930ed5c627bf937e6b5d139c52f18945f045286e78dba66cbe5adfab92ab79a
sha_scope=04d716af2a87a8bf365431c97097a5c740353c6c273de82677d826f1c4d98807
sha_nightly_update=ec079d56912aea8a4358a7ae97a73a3ad6ee3df34e83845ad4d655d31d838636
sha_tier1_pull=5b70dfed08a237034b586ef9738e2c1b81607b20387a62df49a1e6994ba711cf
sha_tushare_proxy=ae91f230560d445b4d2321e8e022d01b55773e168d4d842fc6987fa9458fc772
sha_relay_health=6d3ea9f57f63af8d82d6eeaf140a989aeb09cda941e6711c25f12fd3bbe0e17f
sha_adj_factor_incr=723726c5623a1739ee1fb1dcf97a6be6efd4532717a4c4411fb5e24dfd1422ad
sha_tier1_materialize=e9c89a6c3a0719d9b78064404f2b7d66a7076430f5676e65335db06efae1c3bb
sha_etf_daily_adj_incr=ae670dfc0da14f7aa90bb1d6edd3377b027f69dcb739987dc016388e45b02ae4
sha_eng_daily_panels=a754205397d22b6bb1109d92ee4040d65faedec2d37afd575f77e63da642f0be
sha_mid_large_universe_incr=fe4bbffe1c7c8e0a3f4d38a590acbbcaab61f53b08939722e9b503fa2901d64b
sha_light_event_windows_pull=f12660b90c01089278f01e22b3bdf53154780802668ed4ea90ea5c38c3fc9d71
sha_forecast_manifest_declare=f77673811aa2dd05d461cf895476212f52b05abc3f26212cba87ea30578bd731
sha_fill_hsgt_top10_extend=36cff47c008244ee50f7fb2fcc5f6fd0588d7141901b3a23afe50c48f058e918
sha_cyq_perf_monthly=6aae6c1b8de7b37752fb5032c22ea65b698f252cc57f8e5af94b1e13d6e09c1f
sha_tier3_daily_snapshot=64a71f5607439c5b09ddd92a8dfeffd94e4f5244297f83fbc5c65e3abfcf1067
sha_data_freshness_status=a759d29788859b43783bac6360014347b2df0e4dce5949302a0908db511f1d50
sha_routine_fallback=f3244472da360b74cc692f90548fab4f8839f13f3938bf65374d592b2d61ac5f
allow_run_daily_pull_20261019=true
allow_run_call_b_20261019=true
allow_restore_trade_cal_20261019=true
allow_write_nightly_marker_20261019=true
allow_routine_fallback_restore_20261019=true
allow_quarantine_mv_daily_raw_20261019=true
allow_create_research_quiet_lock_20261019=true
allow_profile_relaxed_20261019=false
allow_daily_pull_retry_20261019=0
source_relay_only=false
```
可选键（不写即为 false / 不适用）：signed_et、allow_profile_relaxed_20261019、allow_daily_pull_retry_20261019（0..2，仅 relaxed）、allow_quarantine_mv_daily_raw_20261019、allow_create_research_quiet_lock_20261019、allow_routine_fallback_restore_20261019（兜底脚本恢复日历的授权；建议 true）、supersede_failed_marker_sha256（仅 18:40 后重跑，64 位全长）、source_relay_only（true / false，**默认 false**，Arch 12:38；true 时子进程加 SOURCE=relay）。

驱动硬性检查（Arch 第 10–12 项）：ASCII、无 CR、每行 key=value（整行 # 注释允许）、值内不得有 #、无重复键、无未知键、全文无 DRAFT；路径含 /_consumed/ 拒绝；必填键全有；ok_id / ok_type / date / signed_by=QuantLab Arch / single_use=true / live=false / promotion_approved=false / interpreter / pin_* / 时间盒数值 / blackout / allow_kill_scope / 五个禁止键=false 逐个等值比对；issued_at 带时区且不晚于当前；expires_et 带时区且在未来；全部 sha_* 与钉值一致且 sha_driver 等于驱动自身；四个 allow_run / restore / marker 键为 true。驱动**不移动、不删除** .ok，只记全长 sha。

## 4. marker 规则（不变）
- 每次运行只写一个 marker（DONE 或 FAILED，含 reason_codes 与 writer=driver），是最后一个写动作；回执先写。
- DONE 已存在 → 退出 2 不写；FAILED 已存在 → 只认 supersede_failed_marker_sha256（全长），否则退出 2 不写。
- 驱动被 SIGKILL 时由例程 20 分钟兜底（routine_fallback_v1.py）在无 marker 时代写唯一 FAILED（writer=routine_fallback，reason=driver_killed）。
- 退出码：0 DONE；1 FAILED；2 前置失败；3 marker 写入失败；4 日历未恢复（P0）；10 只读预检通过；11 统一异常收尾（信号 / 异常 / 子工具超时）。

## 5. 示例 .ok 的校验记录
- 校验时刻 2026-10-18T13:02:22-04:00；文件 /tmp/qd1018/v3/okval_20261018T130216/ARCH_RUN_AUTH_DATA_NIGHTLY_20261019.ok（issued_at 临时换成 2026-10-18T13:01:22-04:00）
- parse_ok 错误：无
- check_ok（strict）：通过
- check_ok（relaxed，示例 allow_profile_relaxed=false）：relaxed 档需要 .ok allow_profile_relaxed_20261019=true（预期拒绝）
- 文本 ASCII：True；键数 55

## 6. 待确认问题（详见驱动说明文档第 9 节）
- Q-1（退出码冲突）：主 Agent 11:42 定“只读预检通过 = 退出 10”；Arch 第 3 项把“exit 10”写进统一失败收尾。现实现：预检通过 = 10，统一异常收尾 = 11。请 Arch 确认或指定。
- Q-2：Arch 第 4 项“只有 MAX_RUN 可重试”已严格实现：rc≠0、原始文件不合格、summary 不符（ATTEMPT_FAILED）在 relaxed 下也不重试。是否如此？
- Q-3：hsgt 只认 remaining=0；若源端当日确无数据（relay_outage_backfill 注释提到 20251226 类空日）会判 FAILED。10-15 / 10-16 实测 remaining=0。是否接受该风险？
- Q-4：两个选择请确认：（a）PPID=1 的可疑孤儿只记录 P1、不发信号；（b）summary 路径为 logs/nightly/20261019_summary.json（nightly_update.py L137）。
- Q-5：94322 / 94403 只要求 T 或已退出（驱动永不发信号）；94403 已于 10-18 04:59:31 退出。若 10-19 05:25 前有人重启 relay_outage_backfill，它会与 daily_pull 抢中转，驱动将拒跑。是否需要放宽（见说明文档第 7 节的只读证据）？
