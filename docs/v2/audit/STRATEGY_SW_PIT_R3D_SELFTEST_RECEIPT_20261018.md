# STRATEGY sw_pit r3d 自测回执（2026-10-18）

**结论：FAIL：8 failed, 75 passed，EXIT=1。不满足 .ok 里 expect_exact=83 passed; 0 failed; 0 error; 0 skipped 的要求。**
按指令只跑了这一次，没有重跑，没有修代码，没有 commit，没有动 .ok（由 Arch 归档）。live=false，promotion=false。

## .ok
- output/strategy_hiliq/ARCH_SELFTEST_STRATEGY_SW_PIT_R3D.ok，sha256 8cef6e9db52821a1e6d0e30a59baa3acf251689ac60015dfe3d8584924a6acba（跑前和跑后一致）
- expires_et 2026-10-18T15:00:00-04:00，single_use=true，live=false，promotion=false，allow_real_data=false，allow_commit=false
- .ok 里的 cmd 和下面执行的命令逐字一致

## 时间（ET，UTC-4）
- 跑前检查：2026-10-18T12:06:05-04:00（在 12:06–12:15 窗口内）
- pytest 开跑：2026-10-18T12:06:05-04:00；结束：2026-10-18T12:06:08-04:00（pytest 报告用时 3.15s）

## 命令（原样执行）
`cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit; echo EXIT=$?`
用 tee 存到 /tmp/swr5/selftest_r3d/pytest_full.txt

## 计数
- passed 75 / failed 8 / error 0 / skipped 0，共 83；EXIT=1
- 8 个失败都在 research/tests_sw_pit/test_sw_members_asof.py，原因相同：结果在应为 None 的位置给出 nan（"At index N diff: nan != None"）
  - test_in_date_eq_d_excluded_out_date_eq_d_included (L82)
  - test_null_out_date_member_and_unknown_code (L86)
  - test_rowfilter_matches_intel_verbatim_and_vectorized (L109)
  - test_natural_day_cases_under_tradeday_rule (L190)
  - test_out_on_sunday_carried_on_monday (L249)
  - test_load_sw_l1_clean_layout_adapter (L437)
  - test_gap_carry_multi_candidate_raise_and_count (L568)
  - test_tsh00018_excluded_exactly_never_normalised (L695，`_norm_a_share(pd.Series(["Tsh.00018"]))` 返回 [nan]）
- 运行环境 ql-enrich-venv：pandas 3.0.6，numpy 2.5.3，pyarrow 26.0.0，pytest 9.1.1（看 dist-info 得到）。原因未分析，留给 Arch 裁定。

## 跑前检查
- RESEARCH_QUIET.lock 不存在（12:06:05）
- pgrep，用 [k] 写法放在脚本文件里执行（/tmp/swr5/selftest_r3d/pgrep_bracket.sh）：没有输出，EXIT=1。证据：/tmp/swr5/selftest_r3d/pre_pgrep_bracket.txt
- bash /tmp/swr5/pgrep_check.sh：没有输出，EXIT=1。证据：/tmp/swr5/selftest_r3d/pre_pgrep_script.txt
- 7 个文件 sha256sum -c 全部 OK，EXIT=0。证据：/tmp/swr5/selftest_r3d/pre_sha_check.txt

## sha（跑前和跑后都是 OK）
| 文件 | sha256 |
|---|---|
| research/sw_members_asof.py | 72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8 |
| research/tests_sw_pit/test_sw_members_asof.py | 3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | 2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2 |
| research/strategy_hiliq_capadv_b4_x2.py | 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1 |
| research/strategy_fulla_b4_x2.py | fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b |
| research/sw_pit_freshness.py | 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f |
| research/tests_sw_pit/test_sw_pit_freshness.py | cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e |
证据：/tmp/swr5/selftest_r3d/pre_sha_check.txt 和 /tmp/swr5/selftest_r3d/post_sha_check.txt（两份都是 EXIT=0）。没有对数据文件做 sha。

## 跑后检查
- 跑后 pgrep：两种写法都是 EXIT=1。证据：/tmp/swr5/selftest_r3d/post_pgrep_*.txt
- 缓存：用 `find /workspace/QuantLab ( -name __pycache__ -o -name .pytest_cache ) -newer /tmp/swr5/selftest_r3d/ts_before` 查，结果为空。跑前和跑后整个仓库的缓存目录清单完全一样（/tmp/swr5/selftest_r3d/pre_cache_list.txt），所以没有删任何东西。research/__pycache__ 和 research/intel/__pycache__ 是跑之前就有的，不是这次产生的，没有动。
- pytest 的 tmp_path 在 /tmp/pytest-of-box/，不在仓库里。

## 证据
- /tmp/swr5/selftest_r3d/pytest_full.txt（sha256 12404088ff4e19ad05109ec0668be3041fcc16db9bb7a20f433a8620ed152d09）
- /tmp/swr5/selftest_r3d/run.sh、/tmp/swr5/selftest_r3d/run_console.txt、/tmp/swr5/selftest_r3d/run_times.txt、/tmp/swr5/selftest_r3d/pre_lock.txt、/tmp/swr5/selftest_r3d/pre_ok_sha.txt、/tmp/swr5/selftest_r3d/pre_ps.txt、/tmp/swr5/selftest_r3d/expected_sha.txt
