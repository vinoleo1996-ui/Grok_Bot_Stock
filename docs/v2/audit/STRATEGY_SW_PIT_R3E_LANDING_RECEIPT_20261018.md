# STRATEGY SW PIT r3e 落地回执 (2026-10-18)

- 授权：output/strategy_hiliq/ARCH_CODE_CHANGE_STRATEGY_SW_PIT_R3E.ok sha256=17652a9a930960d693eaad6f738d1bacd95f43ed1adf1c0474e3f83fa69b1b6d（signed 12:19:28 ET，expires 20:00 ET，single_use，live=false，promotion=false；未改动，由 Arch 归档）
- 增量 diff：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3e_incremental.diff sha256=4f1952ef0e278613ec6283ef071ccde6ae2471a35cfb9f65f641c01fd907f670
- 基于 r3d 落地状态；git HEAD 0ec38296（未变）；未 git add、未 commit、未跑测试、未跑任何 python、未读真实数据内容、未删除任何文件

## 前置（ET）
- 12:20:34 RESEARCH_QUIET.lock 不存在；不在 10-19 16:40–18:40
- 12:20:48 pre pgrep（[k] 写法脚本 /tmp/swr5/land_r3e/kpgrep.sh）EXIT=1；bash /tmp/swr5/pgrep_check.sh EXIT=1；ps 快照 /tmp/swr5/land_r3e/pre_ps.txt
- git apply --check：/tmp r3d 副本（/tmp/swr5/land_r3e/dry）=0，试应用得 dec73305/e80f98ed/28b89a61；真实 repo =0
- 落地前 git 暂存区为空；research/ __pycache__ 基线：research/__pycache__、research/intel/__pycache__（未删）

## 三个文件 sha256
```
pre (r3d):
72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8  research/sw_members_asof.py
3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3  research/tests_sw_pit/test_sw_members_asof.py
2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2  docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md
post (r3e):
dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7  research/sw_members_asof.py
e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc  research/tests_sw_pit/test_sw_members_asof.py
28b89a61310a582f34f7447e2695d1698f75ff8e31e39c3e6e08a73b186bd2b5  docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md
```

## 归档（落地前副本）：_recovery/strategy/20261018T1221ET_pre_r3e/
```
2e1347b510322115a42979bce93918ef53f94b68e4f4edce5de898d795db82c2  ./docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md.20261018_pre_r3e
72e4e4c3a99c1b1a98023c9f387f3dc3a4201fc77219257d9d8b6659905f2ea8  ./research/sw_members_asof.py.20261018_pre_r3e
3fa3878d503397e3d5dbd9bfd61e14ffe191f89d818fd5d9a4c080d28b57a6c3  ./research/tests_sw_pit/test_sw_members_asof.py.20261018_pre_r3e
```

## git apply：2026-10-18T12:21:05-0400 APPLY_REAL=0

## 落地后（ET）
- 12:21:15 post pgrep [k] EXIT=1；pgrep_check.sh EXIT=1；ps 快照 /tmp/swr5/land_r3e/post_ps.txt
- 不该变文件 pre/post sha diff EXIT=0
- git status --short pre/post diff EXIT=0（三个文件本为 ??，状态码不变）；暂存区为空
- __pycache__ 清单（research/ 及全 repo）pre/post diff EXIT=0，无新增

## 不该变文件 sha256（pre=post）
```
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
```

## 证据路径
/tmp/swr5/land_r3e/{pre,post}_pgrep_k.txt, {pre,post}_pgrep_check.txt, {pre,post}_ps.txt, {pre,post}_sha_3files.txt, {pre,post}_sha_mustnot.txt, {pre,post}_git_status.txt, git_status_delta.txt, {pre,post}_git_cached.txt, {pre,post}_pycache*.txt, archive_sha.txt, apply_ts.txt, dry/

下一步：等 Arch 签自测 .ok（必须恰好 85 passed），避开 Data 12:25–12:55。
