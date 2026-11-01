# SD1 单测回执 r3.1a（Eng，2026-10-18 03:09 ET）

- 授权：docs/v2/eng_sd1/ARCH_SD1_TEST.ok sha baec3e6209b205adecc55f5f523dd314a9f7e52e2a52d5c27db2194048a73ef7（scope=selftest，allow_real_data=false，expires 2026-10-19T02:56-04:00）
- 被测：tests/test_sd1_suspend_delist.py 3b565da725cd19dd151eb63583fd76fab3b005339cc70e1544616c62ef07ee68
- 命令：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`，外包 stdlib RSS 采样器（/workspace/sd1_work/selftest_r3_1a/rss_wrap.py，0.1s，上限 1536MB 超限杀进程树）
- 只跑一次，串行；03:09:02 → 03:09:06 ET，耗时 3.7s，exit 0
- 结果：**44 passed, 1 skipped, 0 failed**（3.36s）。跳过的是 T13 真实数据用例（skipUnless(REAL_DATA)，L740），属预期。
- RSS：采样 34 次，进程树 VmRSS 之和峰值 269.5MB；单进程 VmHWM 峰值 156.1MB；getrusage(children) maxrss 155.8MB；未超限
- 副作用核对：仓内 *.pyc 前后列表 diff 0 行；tests/__pycache__ 不存在；/tmp 前后列表一致
- 未动：execution.py 373fed30、platform/__init__ bfdfa63c、delist_accounting 222b63ae、sd1_pit_static_check a8c0d3f6
- 原始文件：sd1_selftest_r3_1a_pytest.log f0df7f82a3c465e69686958c69802083eb0b60cae0f1bd6b8a475795305f84f9；sd1_selftest_r3_1a_rss.json 5d93009787b10f415ee83bbf3c0ae2c43f08a28199c028201a6138ba33760d70
- SD1_SHAS.txt 已把测试 sha 两处 70ddd427 → 3b565da7（非 .ok dep）。
- live=false，promotion=false。
