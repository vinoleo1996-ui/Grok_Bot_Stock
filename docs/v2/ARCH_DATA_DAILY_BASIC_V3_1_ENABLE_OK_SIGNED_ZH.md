# daily_basic v3.1 — 启用 .ok 签发回执

- 时刻（America/New_York）：2026-10-25T04:37:21-04:00
- 依据：Leo 04:30 ET 解冻；主分签令；启用包审查 PASS_WITH_CONDITIONS（sha `fc6a41aa4191b3db0dfabf50d6a6e29819a34d81479b64555f0d8bcd7616df7d`）
- live=false；promotion=false

## .ok

| 项 | 值 |
|---|---|
| 路径 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_ENABLE.ok` |
| sha256 | `4377eb592c18c3bed067c9a7dc775330a3d78f811adb6f51f550b0fa54ccbd73` |
| sha8 | `4377eb59` |
| allow_enable | true |
| allow_run | false |
| allow_paper / stream / backfill | false |

## 必填钉（全长）

- `sha_daily_basic_incremental` = `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8`
- `pin_daily_basic_transform` = `308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974`
- `sha_driver` = `f1910e8ab054c30628184f6e451a77db9c7e3487c31023f0761e50e510e87f05`

## 边界

- 仅授权启用代码路径；**不**授权 nightly/补跑/纸面/stream 实跑（须另签）。
- 例程切到新驱动须另签；f99 字节未动。
- 现盘钉复核：driver/nightly/tier1/incr/scope/f99/transform/pack 全 MATCH。

## 下一步

Eng 可接本 enable .ok；补跑/纸面听主编排另签。叶25 另文件分签。
