# Arch SIGNED：方案 A · 票2 daily_basic incr allow_run（缺口 1019–1026）`.ok`

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T18:44:50-04:00` |
| **状态** | **SIGNED**（只签授权；**不代跑** incr） |
| `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_INCR_ALLOW_RUN_GAP_1019_1026.ok` |
| `.ok` sha8 / 全长 | **`6d5aa893`** / `6d5aa8932bfa874df4c16107eb535ad205f08d52f2ba56359380337e93493087` |
| verdict | INCR_ALLOW_RUN_AUTHORIZED |
| auth_type | incr_allow_run |
| 票1（硬前提） | `ARCH_RUN_AUTH_DAILY_BASIC_MANIFEST_BUILD_BASELINE_SEED.ok` sha8 **`86eef522`** / `86eef5227480cbe11d5e65f0083ff212dddef52e8f48005ae92d544b420daa5b` |
| 方案 | **A** §6 步；**新票**（**绝未**覆写 `…INCR_V3_1_ENABLE.ok` `4377eb59`） |
| gap_dates | `20261019`–`20261023` + `20261026`（end=`20261026`） |
| expires | **`2026-10-27T08:00:00-04:00`** |
| QUIET | **未挂** |
| live / promotion | false / false |

## 消费硬前提（Data 开跑前）

1. 票1 **已 CONSUMED_PASS**
2. `manifest.build.new_sha256` **PRESENT** 且全长 == `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948`（sha8 `f6bbf9e5`）
3. 缺 build 时本票 **不**授权开跑

## 签前门禁

| 项 | 结果 |
|---|---|
| incr `a7ac54b3` / transform `308b5054` MATCH | **PASS** |
| 票1 已落盘 sha8 `86eef522`（本拍先签） | **PASS** |
| enable `4377eb59` allow_run=false 已过期 → **禁复用** | **钉入** |
| QUIET ABSENT；EXEC_V2 已 CONSUMED；无重进程 | **PASS** |
| 未覆写 `ARCH_RUN_AUTH_DAILY_BASIC_INCR_V3_1_ENABLE.ok` | **PASS** |

## 授权边界

- allow_run=**true**；allow_write_production=**true**（**仅** daily_basic incr 合法路径）
- allow_enable=**false**（代码路径已 enable）
- A13 / 单进程；rss≤1500；禁抬帽；禁 `--c5-ignore`；禁假 DONE；禁候选3 enable
- forbid∋`4377eb59`/`6de02e74`/`a158f17a`/`5ae077fa`
- single_use；archive_by=Arch only
- **Arch 不代跑**；≠ 票1 混票；≠ 叶30

## 请主

1. MATCH 本票 sha8 **`6d5aa893`** + 本回执
2. 令 Data：**先**消费票1 → **再**消费本票物化缺口 → 再写 DONE
3. 叶30 仍听主 ≥23:05 另令（本拍不签）

≠X2；不报 Leo；live=false。

---
文档结束（Arch 方案A 票2 SIGNED）
