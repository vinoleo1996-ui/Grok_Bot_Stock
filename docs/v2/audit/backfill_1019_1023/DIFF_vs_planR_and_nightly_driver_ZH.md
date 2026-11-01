# 1019–1023 补跑包 vs plan R / nightly 驱动

- 时刻（America/New_York）：见 PACK_META
- live=false；本包未跑生产

## vs `backfill_1014_1016/run_backfill_r_v3_1.py`（方案 R）

| 项 | plan R | 本包 |
|---|---|---|
| 目标 | cyq + tier3/bundle/freshness（单日 20261016） | daily_basic incr v3.1 全链路五日（1019–23） |
| CMD | run1 cyq；run2 tier3,bundle,freshness | 每 D：Call A `daily_pull`；Call B 14 步（CALL_B_STEPS） |
| 日历 | 不改 trade_cal（无 daily_pull） | daily_pull 后 compare→cal_restore_v2→双核 PIN |
| .ok | 单份 run .ok | **窗口授权** 9e4359f9 + **专用 runner .ok**（待 Arch 审签） |
| 日期闸 | 无 ET==D | **无 ET==D**（历史补跑）；禁用 nightly 驱动硬跑历史日 |
| 叶25 | 无 | 10:00–10:45 ET 硬停/不起 |
| Mem | 无显式 | MemAvailable≥2.5GiB |
| 停树/RSS/BLACKOUT/quiet | 有 | 对齐驱动 + plan R（不 STOP/CONT 94322） |

## vs `nightly_20261019/run_nightly_v1_dbincr_v3_1.py`（f1910e8a）

| 项 | nightly 驱动 | 本包 |
|---|---|---|
| ET 日==D | **强制** | **不要求**（专用补跑） |
| 调用方式 | 自身即驱动 | **禁止** subprocess 该文件跑历史日；只调 `scripts/nightly_update.py` |
| 日期 | 单日 `--date` | `DATE_LIST` 串行 |
| sha_driver | 自身 | `sha_driver_ref` 钉 f1910e8a（只核现盘，不调用） |
| 方案 B | — | **禁**：不改驱动加历史日豁免 |

## 未做

- 未签 runner .ok；未启跑；未写生产 data/；未切例程；未碰 fundport/stream/paper。
