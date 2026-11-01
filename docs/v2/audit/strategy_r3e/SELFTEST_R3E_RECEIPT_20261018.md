# STRATEGY sw_pit r3e SELFTEST RECEIPT (2026-10-18)

- ok: output/strategy_hiliq/ARCH_RUN_AUTH_STRATEGY_SW_PIT_R3E_SELFTEST.ok
- ok_sha256: bf4ee8c72b308ed6fe258d41db3b8e3310fabd6e3c95cc4d9894378b30abd889  (未移动/未修改，交 Arch 归档)
- ok 条件: not_before 12:55 ET / expires 15:00 ET / single_use / live=false / promotion=false / timeout 900s / rss_cap_kb 1536000 / allow_write_outside=/tmp/swr5/selftest_r3e/
- 开跑窗口自设 ≥12:55:30 ET；pre-check 时间 2026-10-18T12:55:48-04:00
- start_et=2026-10-18T12:55:50-04:00 (ET)
- end_et=2026-10-18T12:55:53-04:00 (ET)
- 单次运行，未重跑，未改代码，未 commit，未删除任何东西

## 命令（.ok 原文 + 外加 timeout 900 + tee）
```
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 timeout 900 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit 2>&1 | tee /tmp/swr5/selftest_r3e/pytest_full.txt; echo EXIT=${PIPESTATUS[0]}
```

## 结果
- 计数: 85 passed, 0 failed, 0 error, 0 skipped
- EXIT=0  → PASS（计数与退出码均符合 .ok expected）
- pytest_full.txt sha256: 98eafc4f02b3ac589091169b3d2f326a5af8f7a44c457faf0efff3097c44ca7f
- 峰值 RSS（pytest 进程，0.5s 采样）: peak_rss_kb=155464 < cap 1536000
```
........................................................................ [ 84%]
.............                                                            [100%]
85 passed in 3.50s
```

## 锁检查
- RESEARCH_QUIET.lock absent 2026-10-18T12:55:48-04:00

## pgrep（[k] 写法 + /tmp/swr5/pgrep_check.sh）
- pre  bracket: EXIT=1 | pre  script: EXIT=1
- post bracket: EXIT=1 | post script: EXIT=1

## 跑前 ps（python 相关）
```
     53 root        11:48:48 /usr/bin/python3 /usr/local/bin/sand-exit-watch --telemetry-log /tmp/sand-box-telemetry.log --exec-owner 323 --supervise-owner 27167 --daemon-launcher orbitd=/usr/local/libexec/sand/orbitd/start
    204 box         11:48:48 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 --token-plugin TokenFile --token-source /tmp/sand-novnc-tokens.d 0.0.0.0:6081
  17533 box         02:38:02 python3 -X utf8 server.py
  27366 root        11:40:02 /usr/bin/python3 /usr/local/bin/sand-memory-watch --telemetry-log /tmp/sand-box-telemetry.log
  27427 box         11:40:02 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc --heartbeat=30 0.0.0.0:6080 localhost:5900
  94322 box         11:32:07 python3 scripts/acquire/remaining_after_stk_surv.py
```
注：pid 94322 scripts/acquire/remaining_after_stk_surv.py（01:23 ET 起）非 Strategy 进程，不在 pgrep 名单内；运行期间它写入了 data/v2/tushare_raw/fund_portfolio_dh/20251231/ 下 2 个文件（见 post_newer_files_repo.txt），与本测试无关。

## HEAD / 暂存区
- pre HEAD 0ec3829 / post HEAD 0ec3829；暂存区 pre/post 均为空

## pin sha256（跑前 = 跑后，14/14 OK，EXIT=0/0）
```
dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7  research/sw_members_asof.py
e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc  research/tests_sw_pit/test_sw_members_asof.py
28b89a61310a582f34f7447e2695d1698f75ff8e31e39c3e6e08a73b186bd2b5  docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md
7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1  research/strategy_hiliq_capadv_b4_x2.py
fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b  research/strategy_fulla_b4_x2.py
5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f  research/sw_pit_freshness.py
cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e  research/tests_sw_pit/test_sw_pit_freshness.py
89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c  data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet
87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3  data/v2/sw_l1_pit/industry_members_sw_l1.parquet
fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41  data/v2/calendar/trade_cal_sse_pit.parquet
0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6  data/v2/sw_pit/industry_members_sw_l1_pit.parquet
0493991cd34f72a85d8cb1139b1f3b947b0754fa38029f54ad06a45b2a26446b  data/v2/sw_l1_pit/manifest.json
6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20  docs/v2/eng_sd1/paper_import_closure.json
cd379089cb3902064501b16a8dec0a8706dbc68da5cb4546dd58eb75fbf98611  docs/v2/audit/STRATEGY_SW_PIT_R3E_LANDING_RECEIPT_20261018.md
```
pre check:
```
research/sw_members_asof.py: OK
research/tests_sw_pit/test_sw_members_asof.py: OK
docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md: OK
research/strategy_hiliq_capadv_b4_x2.py: OK
research/strategy_fulla_b4_x2.py: OK
research/sw_pit_freshness.py: OK
research/tests_sw_pit/test_sw_pit_freshness.py: OK
data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet: OK
data/v2/sw_l1_pit/industry_members_sw_l1.parquet: OK
data/v2/calendar/trade_cal_sse_pit.parquet: OK
data/v2/sw_pit/industry_members_sw_l1_pit.parquet: OK
data/v2/sw_l1_pit/manifest.json: OK
docs/v2/eng_sd1/paper_import_closure.json: OK
docs/v2/audit/STRATEGY_SW_PIT_R3E_LANDING_RECEIPT_20261018.md: OK
EXIT=0
```
post check:
```
research/sw_members_asof.py: OK
research/tests_sw_pit/test_sw_members_asof.py: OK
docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md: OK
research/strategy_hiliq_capadv_b4_x2.py: OK
research/strategy_fulla_b4_x2.py: OK
research/sw_pit_freshness.py: OK
research/tests_sw_pit/test_sw_pit_freshness.py: OK
data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet: OK
data/v2/sw_l1_pit/industry_members_sw_l1.parquet: OK
data/v2/calendar/trade_cal_sse_pit.parquet: OK
data/v2/sw_pit/industry_members_sw_l1_pit.parquet: OK
data/v2/sw_l1_pit/manifest.json: OK
docs/v2/eng_sd1/paper_import_closure.json: OK
docs/v2/audit/STRATEGY_SW_PIT_R3E_LANDING_RECEIPT_20261018.md: OK
EXIT=0
```

## __pycache__ / .pytest_cache
- 全仓清单 pre=234 条，post=234 条，diff 为空（完全一致）；完整清单见 pre_cache_list.txt / post_cache_list.txt
- find -newer ts_before（__pycache__/.pytest_cache/*.pyc）: 无（post_newer_cache.txt 为空）
- 非 venv 部分（pre=post）：
```
/workspace/QuantLab/.pytest_cache
/workspace/QuantLab/_recovery/ai/pre_arch_fix_0154/tools/__pycache__
/workspace/QuantLab/quantlab/__pycache__
/workspace/QuantLab/quantlab/data/__pycache__
/workspace/QuantLab/quantlab/data_sources/__pycache__
/workspace/QuantLab/quantlab/intel/__pycache__
/workspace/QuantLab/quantlab/platform/__pycache__
/workspace/QuantLab/quantlab/portfolio/__pycache__
/workspace/QuantLab/quantlab/universe/__pycache__
/workspace/QuantLab/research/__pycache__
/workspace/QuantLab/research/intel/__pycache__
/workspace/QuantLab/scripts/acquire/__pycache__
/workspace/QuantLab/scripts_eng/__pycache__
/workspace/QuantLab/tests/__pycache__
```
注：基线中除 research/__pycache__、research/intel/__pycache__ 外，还存在根目录 .pytest_cache（mtime 01:17 ET，早于本次）及 quantlab/、scripts*/、tests/、_recovery/ 下的历史 __pycache__ 与 .venv-data-api 内的缓存；均非本次生成，未删除。
