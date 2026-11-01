# D1b execute 回执（EXECUTE_v1.ok，r6c 代码 b9674c8b）

- 执行人：QuantLab Data；单进程；live=false，promotion_approved=false，strategy_promotion=false
- 放行依据：`docs/v2/ARCH_DATA_SD1_EXEC_D1A_REVIEW_ZH.md`，Arch 于 05:21:18 EDT 书面放行 D1b（已通读）
- 时间（America/New_York）：T0=2026-10-18 05:22:20.481016744 EDT；结束 05:23:36.898505977 EDT；**exit 0**
- 命令：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 scripts/fix_sd1/build_cs_panel_v2_resumefix.py --arch-ok output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok --fixes resume --execute`
  - 外层用 /usr/bin/python3 跑 subprocess，用 getrusage(RUSAGE_CHILDREN) 测峰值 RSS。

## 前置核对（05:21:55–05:22:20 EDT，全部满足）
- .ok：`output/data/ARCH_RUN_AUTH_CS_PANEL_RESUMEFIX_EXECUTE_v1.ok`
  - sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52 ✓（只用了这一份 .ok）
  - signed_et 05:16:02 不晚于 `date`（05:22:12 EDT）✓
  - expires_et 2026-10-19T16:00:00-04:00 未到；当前不在 forbid_window ✓
- 代码 pin 7 项：工作区、`git show b9674c8b:<path>` 和 .ok 三处一致 ✓
  - 362e3239、903e64ef、6e2e1273、6b8fd033、34e46899、542dd136、7dbcf5d3
- 数据 pin 14 项与 .ok 一致 ✓
- scripts/fix_sd1：`git status --porcelain --ignored` 输出为空，没有 __pycache__ ✓（运行前后都检查过）
- 运行前不存在的路径：panel_cache_v2_resumefix 及其 staging、output/ai_factory/*VOID*、data/v2/suspend_flags ✓
- D1a 收据 RECEIPT_D1a_fixesnone_check.json 的 sha256=21db8530…，与 D1a 回执一致 ✓
- MemAvailable ≥ 2GB ✓
  - 11,022,020 kB（05:22:13 ps 留证时）
  - **运行前 11,204,676 kB**（T0 前一刻）
  - **运行后 10,526,624 kB**
- 进程：`pre_d1b_exec_ps_20261018.txt`（sha256=dedec4b6c48cffe577fe415dd250b9a523982959155a1da668b1bc1516376cd0）
  - 存活判断只读 /proc，没有用 kill -0。
  - 没有 nightly_update、tier3_daily_snapshot、relay_outage_backfill、daily_pull、tier1_pull、adj_factor、bars_materialize 进程 ✓
  - 94403 不存在 ✓
  - 94322 state=**T** ✓
  - 80415 server.py 是 Web 看板，Arch 已确认不在禁止名单内。
- 94322 运行后仍为 T。没有 CONT，没有 kill。

## 门禁与提交
```
RUN_CONDITION_MATCHES []
GATE_PASS step=D1b_resume_execute mode=execute ok_sha256=f03357f19f087def6cd47716f34e7ae0fd093184a2fde7f31231357f13fe1a52
COMMITTED /workspace/QuantLab/output/ai_factory/panel_cache_v2_resumefix
```
- 没有 VOID；output/ai_factory 下没有 staging 或 VOID 残留。

## P3-9 raw_content
- manifest：`{"cutoff": "20261014", "n_files": 4256, "raw_content_sha256": "4d03c9836464b7793fc72b4f2c1cdd885f151cda76c19ab8a22540ad89f1a2be"}`
- RECEIPT_D1b JSON：`{"cutoff": "20261014", "n_files": 4256, "raw_content_sha256": "4d03c9836464b7793fc72b4f2c1cdd885f151cda76c19ab8a22540ad89f1a2be"}`
- 断言：manifest、D1b 收据、D1a 收据与基准 {"cutoff":"20261014","n_files":4256,"raw_content_sha256":"4d03c983…a2be"} 四者以 dict 比较完全相等，结果为 **True** ✓
- 另外，脚本的 raw_pin_start 在 execute 模式下会把本次值与 D1a 收据比对，不一致就抛错。本次通过。

## 逐年统计（脚本 stdout；括号内为 v3 dry-run 的值）
| 年 | rows_v1 | rows | rows_added | v1 缺失 | v1 改变 | restored | resume/intraday | HI_LIQ carry | hiliq 或 fulla 为真 | rss_mb v3/exec | 除 rss 外与 v3 一致 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 783,166 | 784,156 | 990 | 0 | 0 | 990 (990) | 959/31 | 296 (296) | 0 | 806/769 | ✓ |
| 2019 | 846,470 | 846,942 | 472 | 0 | 0 | 472 (472) | 466/6 | 214 (214) | 0 | 979/979 | ✓ |
| 2020 | 880,720 | 881,143 | 423 | 0 | 0 | 423 (423) | 419/4 | 186 (186) | 0 | 1048/1066 | ✓ |
| 2021 | 983,990 | 984,306 | 316 | 0 | 0 | 316 (316) | 315/1 | 145 (145) | 0 | 1151/1112 | ✓ |
| 2022 | 1,087,168 | 1,087,448 | 280 | 0 | 0 | 280 (280) | 278/2 | 151 (151) | 0 | 1199/1212 | ✓ |
| 2023 | 1,163,879 | 1,164,066 | 187 | 0 | 0 | 187 (187) | 186/1 | 63 (63) | 0 | 1219/1225 | ✓ |
| 2024 | 1,198,136 | 1,198,350 | 214 | 0 | 0 | 214 (214) | 214/0 | 110 (110) | 0 | 1306/1296 | ✓ |
| 2025 | 1,204,295 | 1,204,703 | 408 | 0 | 0 | 408 (408) | 408/0 | 273 (273) | 0 | 1336/1318 | ✓ |
| 2026 | 924,485 | 924,774 | 289 | 0 | 0 | 289 (289) | 288/1 | 183 (183) | 0 | 1336/1318 | ✓ |

- **v1 行断言：9 年都是 v1_rows_missing_in_v2=0、v1_value_mismatch=0** ✓。脚本遇非 0 会 VOID，本次没有 VOID。
- **合计：restored 3579 = resume 3533 + intraday 46；HI_LIQ carry 1621；missing 0；mismatch 0**
  - 与预期 3579 / 3533 / 46 / 1621 一致，与 v3 dry-run 一致 ✓
- 每年 rows = rows_v1 + restored；restored 行的 hiliq 和 fulla 均为 False（计数 0）✓
- 对比方法：逐年把 v3 dry-run 打印的每个键（除 rss_mb 外）与 execute 的值比较，9 年全部相同。execute 多出的键只有 sha256 和 v1_sha256。

## sessions_walked 与 D2 天数
- manifest 中 sessions_walked=**2128**，first_session_forced_no_resume=2018-01-02。
- D2 天数：v3 D2 dry-run 的 stdout 和回执都没有打印 days_walked（这个值只写进 execute manifest，见 build_suspend_flags_v2.py 第 116 行）。
  - 所以我按 D2 脚本第 44 行的同一规则只读统计：data/v2/tushare_raw/daily/2*.parquet 中 20180102 ≤ stem ≤ CUTOFF(20261014) 的文件数 = **2128**。
- 结论：2128 = 2128，一致 ✓（Arch r4 P3-3）。D2 execute 后以其 manifest 的 days_walked 为准，届时再核一次。

## 输出（已 commit 到 `output/ai_factory/panel_cache_v2_resumefix/`）
| 路径 | 字节 | sha256 |
|---|---|---|
| output/ai_factory/panel_cache_v2_resumefix/RECEIPT_D1b_resume_execute.json | 4070 | 2edd6e2614c4aec7f9fa229626e496d96d21f467bc6fc9615dfc134e327472a9 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2018.parquet | 14946763 | d0cedc255c4bcbb9171e25ebb3c299db89c7fe7bc303d8d94beb987c277178cb |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2019.parquet | 15905529 | dcb7201c8719b9628851ff84e9ec40c6eba02bb7b65e9dd61e70b67147666922 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2020.parquet | 17044100 | 3fe4f5806463ee3bbf0f4e6d48d1c86874d701930799ac0a120d0bbc61c93284 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2021.parquet | 19418636 | c5de7a803e00af0ae1c17e807a4e63e110cf4a6c8b1ed41727bd02a35bd3fd5e |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2022.parquet | 21875121 | 2ee5aa8efc48b42a4d561d3c26fb1ac4fef7fb0dca96c841a7d71b5c760d0e09 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2023.parquet | 23412047 | 6588573a83c8ee7fa654208b70df8952e9d96cc8c7ec94dad2e1e7fd7f6cfe96 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2024.parquet | 24053767 | bbbfe95a1d81417f35a4b5ff7097ca3d21037e74a49bfe465ceca5d31211ff82 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2025.parquet | 24582651 | 164cde980da9eb40fc57b8af5eafc08767a15c0c006157f5ed8d9291a98e8a48 |
| output/ai_factory/panel_cache_v2_resumefix/cs_panel_2026.parquet | 19080035 | 8df4afecd59fd8d5d4d568b101524ccc69f2f855ee64ed5f61aa5bc661b177c0 |
| output/ai_factory/panel_cache_v2_resumefix/ind_names.csv | 345 | 1ce867127690040bf04b6c8ad5bc16a6d99a396d2ac431893a21eef7892a902a |
| output/ai_factory/panel_cache_v2_resumefix/manifest.json | 14916 | 5c44019df6acae1a1b18aa829993ba0d1662a8dd61edf58017d9cb5253416df7 |

- manifest.json sha256=5c44019df6acae1a1b18aa829993ba0d1662a8dd61edf58017d9cb5253416df7
  - step=D1b_resume_execute，mode=execute，fixes=resume，status=PASS
  - raw_file_list_sha256=d8e00a96…，与 D1a 相同
  - ind_names_sha256 = ind_names_v1_sha256 = 1ce86712…
  - live、promotion_approved、strategy_promotion 均为 false
- RECEIPT_D1b_resume_execute.json sha256=2edd6e2614c4aec7f9fa229626e496d96d21f467bc6fc9615dfc134e327472a9
  - status=PASS
  - manifest_sha256=5c44019d…，与 manifest 一致
  - **ok_sha256=f03357f1…，等于 D1a 收据中的 ok_sha256** ✓
  - prev_receipt_sha256=21db8530526897286329a828c974f4d7c8fc879bccda33492b3bee62ecb69212，等于 D1a 收据文件的 sha ✓
  - year_sha256 与上表各年 parquet 的 sha 一致
- 9 年 parquet 均与 v1 不同（新增了恢复行和新列），这是预期的。逐年 v1_sha256 见 stdout，等于 .ok 的 v1 pin。

## 峰值 RSS
- 1,349,296 KB（约 1318 MB），低于 1400 的披露线，也低于 .ok rss_cap_mb 1450 ✓
- 对比：v3 dry-run 为 1,367,880 KB；脚本自报的最大值 rss_mb=1318。

## stdout 对比（v3 D1b dry-run d1b_stdout_v3_20261018.txt，sha256 4313dac0…）
- stdout：`d1b_exec_stdout_20261018.txt`，sha256=945a62a811532e6673df19b9dc03f9b22a06f9c4efa58e3180064fbf5422642a
- 原始 diff：`d1b_exec_rawdiff_vs_v3_dryrun.txt`，28 行，sha256=a90e65f696bd3ff97d91ebea2a297bb1a0e1ad8e4848a1ae54dde162656a8ddf。差异项：
  1. RUN_CONDITION_MATCHES：v3 为 94403 T，exec 为 []。
  2. GATE_PASS：mode 和 ok_sha 不同。
  3. 9 个年度行：rss_mb 不同，并新增 sha256 和 v1_sha256 两个字段。
  4. 末行：DRY-RUN PASS 变为 COMMITTED。
  5. 包装行的标签和 RSS 数值。
- 规范化 diff：`d1b_exec_normdiff_vs_v3_dryrun.txt`，**0 行**，sha256=e3b0c442…（空文件）。规则与 D1a execute 相同：
  - 去掉 RUN_CONDITION_MATCHES 行和 WRAPPER_EXIT 行。
  - ok_sha256=<64hex> 换成 <OK>；mode=(dryrun|execute) 换成 <MODE>；"rss_mb": N 换成 <RSS>。
  - 去掉 execute 新增的 `, "sha256": "<64hex>", "v1_sha256": "<64hex>"`（D1b 没有 bytes_equal 字段）。
  - 去掉 `DRY-RUN PASS: nothing written` 和 `COMMITTED …` 末行。

## find -newermt T0 写入核对（运行后执行）
- 命令：`find data/v2 output ref docs scripts -newermt '2026-10-18 05:22:20.481016744' -type f -not -path 'docs/v2/audit/data_cs_panel_execute/*'`

| 目录 | 文件数 |
|---|---|
| output/ai_factory/panel_cache_v2_resumefix | 12（全部是 D1b 输出） |
| data/v2/tushare_raw/fund_portfolio_dh | **0**（94322 处于 T） |
| 其他目录（data/v2、output/data、docs 不含回执目录、scripts） | 0 |

- 仓库根目录下没有 ref/。

## 未做
- 没有 D2、D3D4。
- 94322 没有 CONT，也没有 kill，保持 T。
- 没有动补数队列和 moneyflow，没有启 8787，没有发消息，没有 git 操作。
