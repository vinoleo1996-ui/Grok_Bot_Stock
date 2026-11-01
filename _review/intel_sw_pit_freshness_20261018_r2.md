# Intel：sw_pit 过期 + 完整性检查 r2（只出 diff，待 Arch 审）
- 时间：2026-10-18 05:19 ET。对应 Arch 审查 docs/v2/ARCH_INTEL_SW_PIT_FRESHNESS_REVIEW_ZH.md（r1 diff a5b0b633）。正式 research/intel 文件**未改**（cmp 核对）；改动只在临时副本 /tmp/qlrev 上测试。live=false。
- 产出：intel_sw_pit_freshness_20261018_r2.diff（含新测试文件），测试另存 intel_sw_pit_freshness_20261018_r2_tests.py，本说明；各配 .sha256。diff 相对正式文件，git apply --check 通过。
- 已接受部分未动：落后 ≥3 个交易日判 stale；intel_run 带披露照跑；event_study 和 c1 默认停跑、--allow-stale 才放行；入表 in_date<d，出表 out_date>=d。

## P2-a built 的时区
- 来源已核对：scripts/acquire/queue_chain_20261014.py:33 写 `built=datetime.datetime.now().isoformat()`，不带时区；按 Arch 的说明，本机时区为美东。
- 代码：`BUILT_TZ = America/New_York`，注释写明来源。built 先 tz_localize 为美东，再 tz_convert 到 Asia/Shanghai，最后套 18:00 规则。disclosure 同时写出美东原值和换算后的上海时间。
- 现值：10-14 04:00 美东 = 10-14 16:00 上海，早于 18:00，所以只覆盖到 10-13，结论与 r1 相同。

## P2-b 交易日来源
- 改为读 data/v2/calendar/trade_cal_sse_pit.parquet。实际列名：cal_date（str，YYYYMMDD）、is_open（int64，1 = 开市，0 = 休市）、pretrade_date（str）、available_at（datetime）。取 is_open == 1 的日子作为交易日。
- 不再使用 tushare_raw/daily 的文件名。

## P2-c 完整性问题一律硬停
- 新增 `TableIntegrityError`。以下三种情况一律硬停：manifest 读不到或解析失败、parquet 缺失、parquet 实算 sha256 与 manifest.sha256["sw_pit/industry_members_sw_l1_pit.parquet"] 不一致（含 manifest 未登记 sha）。manifest 缺少 in_date_range 或 built 也按完整性错误处理。
- 去掉了 manifest 缺失时回退读 parquet 的路径。
- `require_fresh` 遇完整性错误时报 "HARD STOP"，**--allow-stale 也不放行**；stale 仍是普通 STOP，可以用 --allow-stale 放行。
- 正式文件现状：实算 sha 0b1d3432… 与 manifest 一致，不会触发硬停。
- **intel_run 的两种处理（请 Arch 定）**：
  - **方案 A（已实现，建议）**：只停行业映射这一步。`industry_stocks()` 返回空池，各行业的"相关个股"为空；`source_status.tables.sw_pit` 写 {status: error, severity: high, disclosure}，md 标"HIGH：完整性错误"。行业预警、外盘快照、新闻、events、manual_review 照常输出。
    - 理由：行业得分来自外盘冲击和新闻规则，不读 sw_pit，sw_pit 只用于列出每个行业的个股，停掉不影响行业结论。实时预警整轮停掉的代价，比少一列个股更大。
  - **方案 B（未实现）**：完整性错误时整轮停跑，不写 ALERTS_latest，只写一条错误日志。好处是不会产出可能被误读的结果；代价是下游 alert-ingest 和纸面风控在这一轮拿不到任何预警，旧的 ALERTS 会继续留着并被当作最新的。如果 Arch 选 B，改动是在 intel_run 里捕获 `TableIntegrityError` 后 SystemExit，约 3 行。

## P3 测试
- `test_sw_freshness.py` 改为在临时目录自建 ROOT：manifest、一行的小 parquet、2026-10-08 到 10-23 的交易日历（周末休市），并故意让日线缺 10-15。不再依赖线上 manifest 的值。
- 新增用例：
  - 美东时间跨上海 18:00 边界：05:59 美东（上海 17:59）覆盖 10-13、落后 3；06:00 美东（上海 18:00）覆盖 10-14、落后 2、ok。另有美东 10-13 20:00 = 上海 10-14 08:00、覆盖 10-13 的用例。
  - sha 不一致：check 抛错，require_fresh 在 allow_stale 为 False 和 True 时都硬停。
  - 日线缺一天时，落后天数仍为 3。
  - manifest 缺失、parquet 缺失：同样硬停，加 allow_stale 也停。
  - 研究脚本入口：在临时 ROOT 上调用两个脚本的 main()，不加参数时报 STOP；sha 不一致时即使加 --allow-stale 也报 HARD STOP。都在任何计算之前停下。
  - intel_run 路径：完整性错误时返回空池，SW_FRESHNESS 为 error/high。
  - as-of 成分规则的两条用例保留。

## 测试输出（临时副本 /tmp/qlrev）
```
test_news_classifier: 29/29 passed
test_intel_run_merge: 11/11 passed
test_sw_freshness:
PASS 返回字段齐全
PASS 基准：built 10-14 04:00 美东 = 16:00 上海 → 覆盖到 10-13，asof 10-18 落后 3 → stale
PASS 日线缺 10-15 时落后天数仍为 3（交易日取自 trade_cal）
PASS asof 10-15 → 落后 2 → ok
PASS 美东 05:59（上海 17:59）→ 覆盖 10-13、落后 3
PASS 美东 06:00（上海 18:00）→ 覆盖 10-14、落后 2、ok
PASS 美东 10-13 20:00 = 上海 10-14 08:00 → 覆盖 10-13（不是按美东日期算 10-13 收盘后）
PASS sha 不一致：check 抛完整性错误
PASS sha 不一致：require_fresh(allow_stale=False) 硬停
PASS sha 不一致：require_fresh(allow_stale=True) 硬停
PASS manifest 缺失：check 抛完整性错误
PASS manifest 缺失：require_fresh(allow_stale=False) 硬停
PASS manifest 缺失：require_fresh(allow_stale=True) 硬停
PASS parquet 缺失：check 抛完整性错误
PASS parquet 缺失：require_fresh(allow_stale=False) 硬停
PASS parquet 缺失：require_fresh(allow_stale=True) 硬停
[freshness] {"table": "sw_pit", "max_date": "2026-09-24", "built": "2026-10-14T04:00:00", "covered_through": "2026-10-13", "lag_days": 3, "status": "stale", "disclosure": "sw_pit: built=2026-10-14T04:00:00（美东）= 2026-10-14 16:00 上海，覆盖到 2026-10-13，落后 3 个交易日（asof 2026-10-18，最近交易日 2026-10-16，阈值 ≥3）；最后一次成分变动 2026-09-24；sha256 校验通过（STALE）"}
PASS stale 默认停跑（非硬停）
[freshness] {"table": "sw_pit", "max_date": "2026-09-24", "built": "2026-10-14T04:00:00", "covered_through": "2026-10-13", "lag_days": 3, "status": "stale", "disclosure": "sw_pit: built=2026-10-14T04:00:00（美东）= 2026-10-14 16:00 上海，覆盖到 2026-10-13，落后 3 个交易日（asof 2026-10-18，最近交易日 2026-10-16，阈值 ≥3）；最后一次成分变动 2026-09-24；sha256 校验通过（STALE）"}
PASS --allow-stale 放行 stale 并带 disclosure
[freshness] {"table": "sw_pit", "max_date": "2026-09-24", "built": "2026-10-14T04:00:00", "covered_through": "2026-10-13", "lag_days": 3, "status": "stale", "disclosure": "sw_pit: built=2026-10-14T04:00:00（美东）= 2026-10-14 16:00 上海，覆盖到 2026-10-13，落后 3 个交易日（asof 2026-10-18，最近交易日 2026-10-16，阈值 ≥3）；最后一次成分变动 2026-09-24；sha256 校验通过（STALE）"}
PASS intel_event_study.py 无 --allow-stale 时停跑
PASS intel_event_study.py sha 不一致 + --allow-stale 仍硬停
[freshness] {"table": "sw_pit", "max_date": "2026-09-24", "built": "2026-10-14T04:00:00", "covered_through": "2026-10-13", "lag_days": 3, "status": "stale", "disclosure": "sw_pit: built=2026-10-14T04:00:00（美东）= 2026-10-14 16:00 上海，覆盖到 2026-10-13，落后 3 个交易日（asof 2026-10-18，最近交易日 2026-10-16，阈值 ≥3）；最后一次成分变动 2026-09-24；sha256 校验通过（STALE）"}
PASS intel_c1_gap_split.py 无 --allow-stale 时停跑
PASS intel_c1_gap_split.py sha 不一致 + --allow-stale 仍硬停
PASS intel_run 路径：完整性错误 → 空池 + source_status high
PASS as-of：变动当天不可用、出表当天仍是成员
PASS as-of：次日生效

25/25 passed
intel_run dry-run（--out-dir /tmp/qlrev_dry）:
dry-run written /tmp/qlrev_dry
maxrss_MB 221.0
119:数据表新鲜度：sw_pit stale——sw_pit: built=2026-10-14T04:00:19.995930（美东）= 2026-10-14 16:00 上海，覆盖到 2026-10-13，落后 3 个交易日（asof 2026-10-18，最近交易日 2026-10-16，阈值 ≥3）；最后一次成分变动 2
```

## 按新规则 sw_pit 当前的判定
- **stale**：built 10-14 04:00 美东 = 16:00 上海，覆盖到 10-13；asof 10-18，最近交易日 10-16（按 trade_cal），落后 3 个交易日，达到 ≥3 的阈值。sha 校验通过，没有完整性错误。另存在 data/v2/_quarantine/sw_pit_INCOMPLETE_20261018/，已写进 disclosure。

## 对现有输出的影响（与 r1 相比）
- ALERTS：stale 时多一行披露（含美东和上海时间），行业分数与个股不变。
- event_study 和 c1：落地后不加 --allow-stale 会停；完整性错误一律停。
- intel_run 在完整性错误下按方案 A 运行：个股为空，source_status 为 high。
