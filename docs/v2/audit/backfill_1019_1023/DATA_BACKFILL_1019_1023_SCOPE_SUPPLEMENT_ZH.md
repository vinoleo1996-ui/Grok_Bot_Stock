# Data→Eng：1019–23 补跑 scope 增补（MUST/EXPECTED）

- 时刻：2026-10-25 ~04:53 ET
- 基线 scope 文件：`docs/v2/audit/backfill_1019_1023/nightly_sha_scope_backfill_1019_1023.txt`（自 10-19 启用包衍生）
- 钉点总表：`DATA_BACKFILL_1019_1023_PIN_SHEET_ZH.md`
- 日历证据：`DATA_TRADE_CAL_1019_1023_IS_OPEN_EVIDENCE_ZH.md`
- 消费暂缓：`output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt`（探针 PASS 前禁实跑）
- live=false

## MUST（Data 侧）

1. **date_list 仅** `20261019,20261020,20261021,20261022,20261023`（本地 SSE `is_open=1` 已证；见证据 md）。
2. **主缺口**：`data/v2/tushare_raw/daily_basic/{D}.parquet` 五日全缺；`valuation/daily_basic_full_tushare.parquet` 五日行数=0（last≈20261016）。专用 runner 必须以 daily_basic incr v3.1（钉 incr `a7ac54b3` / transform `308b5054`）覆盖这五日。
3. **日历**：`trade_cal_sse_pit.parquet`（`fa4260b8`）与 manifest → **MUST_NOT_CHANGE**；`tushare_raw/trade_cal.parquet`（`141078fa`，= .ok `pin_trade_cal`）→ 若 runner 触达 daily_pull 类路径须 **RESTORED_TO_PIN**（与 10-19 同口径），禁止漂钉。
4. **禁**：用 `run_nightly_v1_dbincr_v3_1.py` 硬跑历史日；禁在消费暂缓解除前写生产。

## EXPECTED_CHANGE（Data 侧建议）

1. `data/v2/tushare_raw/daily_basic/20261019.parquet` … `20261023.parquet`（新建五日）。
2. `data/v2/valuation/daily_basic_full_tushare.parquet`（及对应 manifest）纳入五日行。
3. `output/data_freshness_status.json` / `output/daily_update_status.json`（若 runner 走 freshness 钩子）。

## 非本包默认（Data 不扩权；Eng/Arch 可另裁）

- `cyq_perf`、`tier3_daily/*`、`asof_extend_202610/calendar.parquet`：1019–23 亦缺，**默认不进**本专用包 MUST；若进包须 Arch 明示。

## 探针 / 重钉（现状）

- 脚本仓库：`docs/v2/audit/relay_probe_20261025/probe5_small.py` sha `1c3999c7…`；Arch 重钉 .ok sha8 `1f0d7f30`（已闭合）。
- 0448 回执 **不通**（`5d208af6`）；中转恢复后仓库路径复测。
