# QuantLab Data 例程回执：A股日线收盘后更新 D=20261026

- 角色：QuantLab Data 执行器
- 时区：America/New_York（ET）
- 回执生成时刻（ET）：2026-10-26T06:41:06-04:00
- live=false；promotion_approved=false；未启动 8787；未碰 moneyflow；未跑 trade_cal/sw

## 1. 启动前核验

| 项 | 结果 |
|---|---|
| /proc/94322 | 不存在 → 跳过 SIGCONT |
| MemAvailable 起步 | ≈6.18 GiB ≥2GB，继续 |
| 冻结日历 trade_cal_sse_pit.parquet | sha=fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41 MATCH |
| SSE 20261026 / 20261027 is_open | 均为 1 |
| calendar/manifest.json | sha=7ccc911e8a3ed2e408f30db1f95f12eb71a6fea18003ba88a31246f941cc89a4 MATCH |
| Eng 日历 trade_cal.parquet | sha=141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086 MATCH |
| 快照脚本 nightly_sha_scope_snapshot_20261018.py | sha=0aa6c6505a90aa7b09cb1c56b079695499a44515758a0da849aebfab29328e37 MATCH |
| 基线 nightly_sha_baseline_20261018_1022.txt | sha=dfdc25552918c7de24af240138fbc298d1ef2cb532723e18a6a4b7d892fb674c MATCH |
| 跑前快照 vs 基线 | RESULT OK（仅 META_ONLY_CHANGE；无 MUST_NOT_CHANGE sha 漂移） |
| 跑前快照路径 | docs/v2/audit/nightly_20261026/sha_pre_20261026.txt sha=1cb374f6443fce49bcbde43fd53cee8eecbd9bc047c41372923e79271d0d1f61 |

## 2. 步骤 1 备份 Eng 日历

- 命令：`cp -p data/v2/tushare_raw/trade_cal.parquet _recovery/data/nightly_20261026/trade_cal.parquet.bak` 后 chmod a-w
- 备份 sha：**141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086**（== PIN）

## 3. 第一次调用（daily_pull）

- 完整命令：`cd /workspace/QuantLab && python3 scripts/nightly_update.py --date 20261026 --steps daily_pull`
- 开始 ET：2026-10-26T06:05:05-04:00；结束 ET：2026-10-26T06:10:00-04:00
- **rc=0**；summary overall=ok；sec=295
- 关键日志：/workspace/QuantLab/logs/nightly/20261026_daily_pull.log
- 摘要：/workspace/QuantLab/logs/nightly/20261026_summary.json（随后被第二次调用覆盖为 partial）
- 日志摘录：daily/daily_basic/adj_factor/stk_limit/suspend_d 对 20261026 均 ok（如 daily 20261026 ok 5570）

## 4. 步骤 3 比对 + 原子恢复

- 比对脚本：/tmp/cal_compare_20261026.py（亦存 docs/v2/audit/nightly_20261026/cal_compare_20261026.py）
- 脚本 sha256：**ff52ebba0f03640063a606c49529309db18921c53be68045cbb415c4c990d386**
- MUST_OPEN=[20261026,20261027]；OUT_DIRS 允许 nightly_20261026/ 与 /tmp/
- 命令：`python3 /tmp/cal_compare_20261026.py --current .../trade_cal.parquet --backup .../trade_cal.parquet.bak --out docs/v2/audit/nightly_20261026/cal_compare_result.txt`
- **比对 RESULT IDENTICAL exit=0**：行数 9862、schema 全同、排序后 exchange/cal_date/is_open/pretrade_date 逐格相同；SSE 两日 is_open=1
- 注：本次 daily_pull 未改写 Eng 日历（跑后仍为 141078fa…）；仍按规程一律恢复
- 恢复：`python3 docs/v2/audit/nightly_20261019/cal_restore_v2.py --backup ... --target data/v2/tushare_raw/trade_cal.parquet --keep-rewritten-dir _recovery/data/nightly_20261026/`
- cal_restore_v2.py sha=6686876bdcfc95f11d493b5201f55eb726e69e4894d8c96bfaf46ab1748387a4；**RESTORE_RC=0**
- 恢复后目标 sha：**141078fa6da0ef94bc3cc8829aa031789490b7ff3e051b4baa4e38c496d06086** MATCH PIN
- 留存：_recovery/data/nightly_20261026/trade_cal.parquet.rewritten_20261026T061009_141078fa6da0

## 5. 第二次调用（14 步，不含 daily_pull/trade_cal/sw）

- 完整命令：`cd /workspace/QuantLab && python3 scripts/nightly_update.py --date 20261026 --steps index_pull,adj_factor,bars,daily_basic,index,etf_daily_adj,eng_panels,mid_large_universe,events,hsgt,cyq,tier3,bundle,freshness`
- 开始 ET：2026-10-26T06:10:15-04:00；结束 ET：2026-10-26T06:37:55-04:00
- **进程 exit rc=0**；summary overall=**partial**；promotion_approved=false

| 步骤 | status | sec | 备注 |
|---|---|---:|---|
| index_pull | ok | 57 | 日志 20261026_index_pull.log |
| adj_factor | ok | 2 | 追加 20261019-23+26；rows=4123764；last=20261026；n_20261026=5580 |
| bars | ok | 53 | rows=100135；date 20260923-20261026；**n_20261026=5570** |
| daily_basic | **fail rc=20** | 2 | DB_INCR_PRECOND: missing build.new_sha256 (A18)；物化表仍 max=20261016；n_20261026=0（raw 已有 20261026.parquet） |
| index | ok | 1 | rows=18669；max=20261026；n_20261026=5 |
| etf_daily_adj | ok | 832 | rows=1575090；last=2026-10-26；n_20261026=1710 |
| eng_panels | ok | 235 | etf510300 last=2026-10-26 rows=3501；asof_em/ts 已延至 2026-10-26；STATUS partial（因下游表） |
| mid_large_universe | ok | 1 | 日志 UP-TO-DATE 2026-10-16；basis_trade_date max=20261015；未写入 20261026 |
| events | partial | 468 | forecast 拉数完成；见 events 日志 |
| hsgt | partial | 0 | skipped RELAY_DOWN fast-fail；表 max 仍 20261016 |
| cyq | partial | 0 | skipped RELAY_DOWN fast-fail |
| tier3 | partial | 0 | skipped RELAY_DOWN fast-fail |
| bundle | ok | — | 复制既有小表/cyq 月包到 output/data_v2_bundle |
| freshness | ok | 2 | overall=stale；stale_tables=[daily_basic, mid_large_universe]；expected_trade_date=20261023（today_sh=20261026） |

## 6. 跑后快照

- 跑后快照：docs/v2/audit/nightly_20261026/sha_post_20261026.txt
- vs 基线：RESULT OK（EXPECTED_CHANGE：daily_update_status.json、data_freshness_status.json；无 MUST_NOT_CHANGE 漂移）
- vs 跑前：RESULT OK（同上两条 EXPECTED_CHANGE）
- **fa4260b8…（冻结日历）跑后不变**
- **7ccc911e…（manifest）跑后不变**
- Eng 日历恢复后仍为 141078fa…

## 7. 核验：20261026 是否落盘（不看 summary status）

| 表 | 路径 | 行数 | 日期范围 | 20261026 行数 | 判定 |
|---|---|---:|---|---:|---|
| bars | data/v2/bars/daily_ohlcv_raw_pit.parquet | 100135 | 20260923-20261026 | 5570 | **已落盘** |
| adj_factor | data/v2/adj/adj_factor_2023h2plus.parquet | 4123764 | 20230901-20261026 | 5580 | **已落盘** |
| index | data/v2/index/index_daily_pit.parquet | 18669 | 20140102-20261026 | 5 | **已落盘** |
| etf_daily_adj | data/v2/etf/etf_daily_adj.parquet | 1575090 | 20150105-20261026 | 1710 | **已落盘** |
| etf510300 | data/v2/etf_510300/panels/sh.510300.parquet | 3501 | available_at→2026-10-26 18:00+08 | — | **已落盘** |
| daily_basic | data/v2/valuation/daily_basic_full_tushare.parquet | 12309945 | 20140102-20261016 | 0 | **未物化**（raw 有） |
| mid_large | data/v2/universe/mid_large_members_pit.parquet | 5565449 | basis max 20261015 | 0 | **未更新** |
| hsgt_top10 | data/v2/northbound/hsgt_top10_daily_2018plus.parquet | 38364 | 20180102-20261016 | 0 | **未更新（RELAY_DOWN）** |

- output/daily_update_status.json 已写出；**target_trade_date=2026-10-26**；status=partial；live=false；promotion_approved=false
- 结论：**有新交易日核心日线数据落盘（yes）**；估值 daily_basic 物化与 hsgt/cyq/tier3/mid_large 未齐

## 8. priority 报警判断

- 冻结日历 / manifest / MUST_NOT_CHANGE：**不变** → **不要求** priority 报 Arch+主（日历类）
- Eng 日历恢复后 sha 正确 → 不报警
- **非 priority 但需知会**：daily_basic A18（missing build.new_sha256）导致估值表停在 20261016；hsgt/cyq/tier3 RELAY_DOWN；建议 Eng 修 A18 / 中继恢复后补跑（priority=false 通知 Eng；Arch/主摘要即可）

## 9. 关键路径速查

- bars: /workspace/QuantLab/data/v2/bars/daily_ohlcv_raw_pit.parquet
- daily_basic: /workspace/QuantLab/data/v2/valuation/daily_basic_full_tushare.parquet（未含 D）
- index: /workspace/QuantLab/data/v2/index/index_daily_pit.parquet
- etf_daily_adj: /workspace/QuantLab/data/v2/etf/etf_daily_adj.parquet
- adj_factor: /workspace/QuantLab/data/v2/adj/adj_factor_2023h2plus.parquet
- raw daily D: /workspace/QuantLab/data/v2/tushare_raw/daily/20261026.parquet
- raw daily_basic D: /workspace/QuantLab/data/v2/tushare_raw/daily_basic/20261026.parquet
- status: /workspace/QuantLab/output/daily_update_status.json
- freshness: /workspace/QuantLab/output/data_freshness_status.json
- 日志目录: /workspace/QuantLab/logs/nightly/20261026_*.log

## 10. 时间戳（America/New_York）

- 本回执 date 生成时刻：见文首
- 第一次调用：06:05:05-06:10:00 ET
- 比对/恢复：约 06:10:04-06:10:09 ET
- 第二次调用：06:10:15-06:37:55 ET
- 跑后快照：06:38:06-06:38:07 ET

