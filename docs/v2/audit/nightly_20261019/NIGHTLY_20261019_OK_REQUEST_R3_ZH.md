# 10-19 日更 run .ok 申请 R3（Data → Arch；严格按 Arch v3.1 行级审 §8 草案；待签，不是 .ok）

- 写成 2026-10-18T13:59:33-0400（ET，date 生成）；作者 QuantLab Data。只写本文档；没有运行项目代码；没有创建、移动任何 .ok；没有发信号或消息。
- 依据：docs/v2/ARCH_DATA_NIGHTLY_V31_LINE_REVIEW_ZH.md（41bcbcc84832c3329ce9aecbb817ef08ce6cf26af7efe8a01b9b1d22755a856e）§8 键表（审查文档 L162–219，58 键）与 §1 签发条件 C1–C4；主 Agent 13:56 定值。
- 取代：NIGHTLY_20261019_OK_REQUEST_R2_ZH.md（b54907e3649057576c507151d0681d50816393465140b8c9e97ad8f75280299d；文件本身未动，仅作废，见第 2 节）。
- 驱动 run_nightly_v1.py（v3.1）sha256 = f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a
- 兜底 routine_fallback_v1.py（v3.1）sha256 = 559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384
- 配套例程草稿 ROUTINE_PROMPT_DRAFT_R4_1_ZH.md sha256 = 57a44a933cb61e794fc14b44fe38e3d7f3e9bd0c636713b60b7d43f337b59da3（**仅作配对记录，不是 .ok 键**：§8 键表里没有例程草稿 sha 键，驱动拒绝未知键，审查文档 L154 / 驱动 L729–730；见第 6 节第 1 条）。

## 1. 定值（与 §8 逐键核对，无冲突）
- allow_relay_partial_20261019=true，allow_hsgt_source_empty_warn_20261019=true。**两者必须取同一个值**（同 true 或同 false，不得一真一假）：r4.5 relaxed 2a (ii) 只要有 WARN 就要求两个 ok_flags 都为 true，一真一假时驱动会写出合法的带 WARN 的 DONE，例程却会挡下（审查 F-6、C1）。若主 Agent 改取保守值，两键一起写 false。
- source_relay_only=false（审查第 7 节：datahub 是 REQUIRED 原始数据实际来源，true 会把回落路径变成单点失败）。
- allow_profile_relaxed_20261019=true（relaxed），allow_daily_pull_retry_20261019=2（retry；驱动取 min(2, 键值)，只有 MAX_RUN 可重试，审查 F-5）。
- expires_et=2026-10-19T16:00:00-04:00。
- issued_at 留空（`issued_at=`），由 Arch 签发时用 date +%Y-%m-%dT%H:%M:%S%:z 填写；signed_et 照 §8 保留占位 <date>，同样由 Arch 填。**留空状态不可直接签发**：issued_at 是必填键，驱动 L774–776 要求带时区且不晚于当前。
- sha_driver、sha_routine_fallback 用上面的全长值；其余 sha_* / pin_* 原样取自 §8。

## 2. R2 作废项
- R2 的 allow_profile_relaxed_20261019=false、allow_daily_pull_retry_20261019=0、expires_et=2026-10-19T16:40:00-04:00（R2 L46、L56、L103–104）全部作废。
- R2 的「键数 55」（R2 L124）以及 R2 变更里「加两键后 57 键」的说法全部作废；以本文 58 键为准。
- R2 的 allow_relay_partial_20261019=false、allow_hsgt_source_empty_warn_20261019=false 作废，改为第 1 节的同值 true。
- R2 示例 issued_at=2026-10-18T17:30:00-04:00 作废（本文留空，由 Arch 填）。
- 与 R2 键块逐键比对（脚本核对）：§8 新增 1 键：signed_et；R2 有而 §8 无：无；取值变化 6 处：issued_at 2026-10-18T17:30:00-04:00→<date>；expires_et 2026-10-19T16:40:00-04:00→2026-10-19T16:00:00-04:00；allow_profile_relaxed_20261019 false→true；allow_daily_pull_retry_20261019 0→2；allow_relay_partial_20261019 false→true；allow_hsgt_source_empty_warn_20261019 false→true。

## 3. 建议签发的 .ok 文本（58 键；key=value，LF，无注释；os.link 独占创建）

```
ok_id=ARCH_RUN_AUTH_DATA_NIGHTLY_20261019
ok_type=run
date=20261019
signed_by=QuantLab Arch
signed_et=<date>
issued_at=
expires_et=2026-10-19T16:00:00-04:00
single_use=true
live=false
promotion_approved=false
interpreter=/usr/bin/python3
sha_driver=f99dd11aa26f611aca382f98b00ea14fdbcafc99960c8259102e421f02281b0a
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
sha_routine_fallback=559d1e017b1c53b1dd1cdffdc0571fc1d33a6157ea4437735421cc3fab271384
allow_run_daily_pull_20261019=true
allow_run_call_b_20261019=true
allow_restore_trade_cal_20261019=true
allow_write_nightly_marker_20261019=true
allow_routine_fallback_restore_20261019=true
allow_quarantine_mv_daily_raw_20261019=true
allow_create_research_quiet_lock_20261019=true
allow_profile_relaxed_20261019=true
allow_daily_pull_retry_20261019=2
allow_relay_partial_20261019=true
allow_hsgt_source_empty_warn_20261019=true
source_relay_only=false
```

- 键数 58（脚本逐行计数，无重复键）；顺序与 §8 草案完全相同。与 §8 唯一的差别：issued_at 由 `<date>` 改为留空（主 Agent 定值）。

## 4. .ok 归档时间（审查第 4 节、C3）
- .ok 最早在 **2026-10-19 17:05 ET 之后**才可移入 _consumed/（原建议 16:40 作废：兜底在驱动结束后 20 分钟内运行，最晚约 17:02）。
- 并且必须**同时**满足三条：(1) 磁盘上已存在 10-19 的 marker（DONE 或 FAILED）；(2) 活动 trade_cal 的 sha256 等于 PIN 141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086；(3) 当天兜底没有以 exit 5 退出。任一条不满足就不归档，报 Arch。
- 理由：.ok 一旦移走，兜底读到空 kv，issued_at 为 None，没有 marker 时退出 7 不代写 FAILED，日历不是 PIN 时也因未授权无法恢复（审查第 4 节）。

## 5. 签发条件（照审查 §1）
- C2：签 v3.1（f99dd11a）配 Eng r4.5（relaxed）；不交叉配对。
- C4：94322 在 05:25 前必须是 T（04:25 例程用 dc827675 执行 STOP）；STOP 未成功时驱动前置拒跑，属正确行为。
- 签发前在签发时刻重算全部 sha，任何一处不符就不签；签前跑一次驱动 --check-only，确认 .ok 解析通过（审查 L221）。

## 6. 与定值的出入（原样回报，未自行处理）
1. 主 Agent 要求「routine 草稿的 sha 用 R4.1 的新 sha」，但 §8 的 58 键里没有任何例程草稿 sha 键（sha_routine_fallback 是兜底脚本的 sha，已按定值填 559d1e01…）；加新键会变成 59 键，且驱动会把未知键拒掉（审查 L154、驱动 L729–730）。本文**没有**新增键，只在文头记录 R4.1 sha 作配对用。是否需要别的承载方式，请主 Agent / Arch 定。
2. issued_at：§8 写的是 `<date>` 占位，定值要求留空；两者意思相同（都由 Arch 签发时填），按定值写成 `issued_at=`。
3. 除上述两条外，§8 与定值无冲突；键数 = 58。
