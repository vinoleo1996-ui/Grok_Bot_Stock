# Data→Eng：1019–23 专用包钉点对拍

- 时刻：2026-10-25 05:01:37 ET
- Eng 包回执：`ENG_BACKFILL_1019_1023_PACK_RECEIPT_ZH.md`（PACK_DELIVERED_AWAITING_ARCH_RUNNER_REVIEW）
- Data **未**实跑、**未**消费 .ok；consume_suspend 仍在则禁止写生产
- live=false

| 项 | 期望/Eng | Data 实测 | MATCH |
|---|---|---|---|
| pack_file:run_backfill_1019_1023_dbincr_v3_1.py | `fe2decee…` | `fe2decee…` | ✅ |
| pack_file:selftest_run_backfill_1019_1023_dbincr_v3_1.py | `7f4fb2a6…` | `7f4fb2a6…` | ✅ |
| pack_file:SELFTEST_RECEIPT_20261025.txt | `2d37f00c…` | `2d37f00c…` | ✅ |
| pack_file:nightly_sha_scope_backfill_1019_1023.txt | `c204fd5f…` | `c204fd5f…` | ✅ |
| pack_file:BACKFILL_1019_1023_OK_REQUEST_ZH.md | `ecc20423…` | `ecc20423…` | ✅ |
| pack_file:DIFF_vs_planR_and_nightly_driver_ZH.md | `1d78ff98…` | `1d78ff98…` | ✅ |
| auth_ok:output/data/ARCH_RUN_AUTH_DATA_BACKFILL_1019_1023.ok | `9e4359f9…` | `9e4359f9…` | ✅ |
| enable_ok:output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_ENABLE.ok | `4377eb59…` | `4377eb59…` | ✅ |
| sha_daily_basic_incremental:(ok field only) | `a7ac54b3…` | `a7ac54b3…` | ✅ |
| pin_daily_basic_transform:(ok field only) | `308b5054…` | `308b5054…` | ✅ |
| pin_trade_cal:data/v2/tushare_raw/trade_cal.parquet | `141078fa…` | `141078fa…` | ✅ |
| date_list_is_open:SSE trade_cal | `all 1` | `n=5 open=5` | ✅ |
| consume_suspend:output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt | `present` | `yes` | ✅ |
| probe_trade_cal_pass_receipt:docs/v2/audit/relay_probe_20261025/RELAY_PROBE_RECEIPT_20261025T0500ET_AFTER_HOSTS.md | `exists` | `yes` | ✅ |

## 总评：**PIN_ALIGN_PASS**

- Data 侧材料：钉点表 `b7c77408…` / 日历证据 `781777c9…` / scope 增补 `3a4ee49d…` / DRAFT scope `57fa100d…`
- 中转：hosts 后 trade_cal PASS（`830c2ed3`）；stock_basic 不稳；是否解除 CONSUME_SUSPEND 待主/Arch
- 下一步：Arch 审 runner `fe2decee…`；解除暂缓前禁实跑
