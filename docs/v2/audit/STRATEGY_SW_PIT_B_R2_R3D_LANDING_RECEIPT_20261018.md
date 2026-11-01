# Strategy 落地回执：SW PIT B r2 + r3d（2026-10-18）

- 结果：**LANDED**。B r2 与 r3d 连续 apply，中间未 commit；未 git add、未 commit。
- 未跑任何测试、python、collect；未读真实数据内容（数据文件只算 sha256）。live=false，promotion=false。
- 落地时间（ET）：start 2026-10-18T11:47:49-04:00；APPLY_B2 与 APPLY_R3D 均在 11:47:49 -04:00；post 证据 11:48:01 -04:00。
- HEAD 不变：0ec38296adbfb1fe691694879c2c042f3b45422d。

## 授权
- .ok：output/strategy_hiliq/ARCH_CODE_CHANGE_STRATEGY_SW_PIT_B_R2_R3D.ok
  sha256 82db7c053f4386e4e54422163889a95f8af63b72115d95252f613f27c8e38fa4（前后一致）
  signed_et 2026-10-18T11:45:04-04:00；expires_et 2026-10-18T20:00:00-04:00；single_use=true；live=false；promotion=false；allow_apply=true；allow_commit=false；allow_run_tests=false；allow_real_data=false。
- 本次落地已使用该 .ok（single_use，视为已消耗，不得再用）。.ok 原文与审查文档都没有要求移到 _consumed/，所以原地不动；未创建、未修改任何 .ok。
- 审查文档：docs/v2/ARCH_STRATEGY_DIFF_C_R3D_REVIEW_ZH.md，sha c08065f30a3372bfe5c6e2503ce81c461f832b471a70295b84da096eddc8ca37（§7.1）。

## 前置条件
- RESEARCH_QUIET.lock 不存在（落地前 ls EXIT=2；land.sh 内再查一次也不存在）。
- 时间不在 10-19 16:40–18:40 ET 内（落地时间是 10-18 11:47 ET）。
- pgrep：`bash /tmp/swr5/pgrep_check.sh` EXIT=1；括号写法 `pgrep -af '[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py'` EXIT=1。落地前、land.sh 内、落地后都没有匹配。
- Diff sha：
  - B r2 docs/v2/audit/STRATEGY_SW_PIT_ASOF_FIX_PROPOSAL_20261018_r2.diff = d0fb1d3faa6962d19e8405280975e8818766ef406b00f390edcc9b02f81ee250
  - r3d docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3d.diff = 090e9c2a4ebbd40cd056f6438e2216a1292b00b172d8be99675c778ab5eceaa8
- /tmp 试运行（/tmp/swr5/land_r3d/dry，真实文件副本）：check B r2 EXIT=0 → apply → check r3d EXIT=0 → apply，最终 5 个 sha 全部等于 .ok 的 after_*。apply B r2 时 git 提示“new blank line at EOF”，只是空白警告，不是错误。

## 文件 sha（旧 → B r2 中间态 b2 → r3d 终态）
| 文件 | 旧 (HEAD) | b2 | r3d（= .ok after_*） |
|---|---|---|---|
| research/strategy_hiliq_capadv_b4_x2.py | 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45 | 1728c12666af87ece9c5a76486c279e3f3b0f7868ef027464a6ea21f6b2695a2 | 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1 |
| research/strategy_fulla_b4_x2.py | 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316 | 88b6f36746ecf2e062d78fe67f390f1c6d8d886a85f660a527d44910cd7ff824 | fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b |
| research/sw_members_asof.py | absent | 0444d9d6f6b66195d19a91cf9c45e53ed0cb715b81b2a595c1388a47ecc2e945 | 72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8 |
| research/tests_sw_pit/test_sw_members_asof.py | absent | 4f468b482613329912e82ab71b2bd4c0d062efdc4451d508e16e21812eeb3ffb | 3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3 |
| docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md | absent | c2b37127772bdb792cd4f85851c47325fbe9a13794cb99ecbb2c374de8d1003c | 2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2 |

## 归档（被覆盖的旧文件）
- 目录：_recovery/strategy/20261018T1147ET_pre_b2r3d/
  - strategy_hiliq_capadv_b4_x2.py.20261018_pre_b2r3d = 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45
  - strategy_fulla_b4_x2.py.20261018_pre_b2r3d = 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316
- 新增的 3 个文件在 HEAD 上不存在，所以没有需要归档的旧版本。

## 不该变的文件（落地前 = 落地后 = .ok 钉值；只算 sha256）
- data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c
- data/v2/sw_l1_pit/industry_members_sw_l1.parquet 87d769aaca06212186986af489f6507b6f0d98c8937f7a4476f97538562733b3
- data/v2/calendar/trade_cal_sse_pit.parquet fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41
- data/v2/sw_pit/industry_members_sw_l1_pit.parquet 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6
- data/v2/sw_l1_pit/manifest.json 0493991cd34f72a85d8cb1139b1f3b947b0754fa38029f54ad06a45b2a26446b
- docs/v2/eng_sd1/paper_import_closure.json 6919e7afe605cc4d1af48868a06b6550db66e3fd1923a3e61bdcc16c621bae20
- research/sw_pit_freshness.py 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f
- research/tests_sw_pit/test_sw_pit_freshness.py cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e
- pre_sha.txt 与 post_sha.txt 的这 8 行逐行 diff：EXIT=0（完全一致）。

## git status
- 落地前后 `git status --short` 的差异只有 5 行：` M` hx2、` M` fulla、`??` sw_members_asof.py、`??` tests_sw_pit/test_sw_members_asof.py、`??` STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md。暂存区为空。其余条目都是落地前就有的，未改动。
- research/ 下没有新增 __pycache__ 或 .pytest_cache。

## 证据（/tmp/swr5/land_r3d/）
pre_pgrep_script.txt、pre_pgrep_bracket.txt、pre_ps.txt、pre_lock.txt、pre_sha.txt、pre_git_status.txt、pre_dryrun.txt、land.sh、land_log.txt、post_pgrep_script.txt、post_pgrep_bracket.txt、post_ps.txt、post_sha.txt、post_git_status.txt、git_status_delta.txt

## 后续
- 等 Arch 签自测 .ok（必须刚好 83 passed）；签发前不跑任何测试。
- P2-1：跑 pitfix-compare 前改 prereg 的 L1/L3（prereg sha 会变，需要重钉）。P2-2：Intel 用 sw_l1_table_check 之前先把 as_of 规整为 Timestamp。
- TIE_SENS_v1.ok 的 dep_hx2 要作废后重签。
