# Arch SIGNED：方案 A · 票1 baseline→manifest.build 种子 `.ok`

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T18:44:50-04:00` |
| **状态** | **SIGNED**（只签授权；**不代写** manifest） |
| `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_MANIFEST_BUILD_BASELINE_SEED.ok` |
| `.ok` sha8 / 全长 | **`86eef522`** / `86eef5227480cbe11d5e65f0083ff212dddef52e8f48005ae92d544b420daa5b` |
| verdict | BASELINE_SEED_AUTHORIZED |
| auth_type | manifest_build_baseline_seed |
| 方案 | **A** §5 步（dig **`bd188832`**）；**≠** 盲 seed B；**≠** 改 precheck C |
| expires | **`2026-10-27T08:00:00-04:00`** |
| QUIET | **未挂**（live ABSENT；本拍不挂） |
| live / promotion | false / false |

## 签前门禁（本签复算）

| 项 | 结果 |
|---|---|
| baseline `273163cc` / `273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486` PRESENT | **PASS** |
| product_sha256 == dest **`f6bbf9e5`** / `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` | **PASS** |
| transform `308b5054` / runtime 3.13.5/3.0.6/26.0.0/2.5.4 | **PASS** |
| raw_inventory `91b1b069…` | **PASS**（从 baseline） |
| manifest `8c2c978b` **无 `build`**；date_max=`2026-10-16` | **PASS** |
| GAP `28f177cf` / dig `bd188832` / CONSUME `9758452c` | **PASS** |
| Eng D1 `0ddeb1b7`/`1a50b8a5`；EXEC_V2 `a62881b9` CONSUMED_PASS | **PASS** |
| QUIET live ABSENT；无 a18/leaf30/daily_basic 重进程 | **PASS** |
| 禁复用 `4377eb59`（enable allow_run=false 已过期） | **钉入** |

## 授权边界（Data 消费时）

在**不改 parquet 字节**前提下，原子写入 `daily_basic_full_tushare_manifest.json` 的 `build`：

```
mode=baseline_seed
prev_sha256=null
new_sha256=f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948
transform_sha=308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974
runtime_versions={python:3.13.5,pandas:3.0.6,pyarrow:26.0.0,numpy:2.5.4}
raw_inventory=91b1b0694f9f1345489d31f48ae9c1d7daf4c056876c57a7e56ac3a45b9519d6
rows_by_year={} 或从 baseline 拷贝
seeded_from=daily_basic_full_tushare_build_baseline.json
seeded_from_sha256=273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486
seeded_at=<ET>
```

- allow_write_manifest_build_only=**true**
- allow_write_production_parquet / allow_materialize / allow_run / allow_incr / allow_enable = **false**
- forbid 方案 B/C；forbid 盲 seed；single_use；archive_by=Arch only
- **Arch 不代写**；Data 消费本票后方可写种子

## 请主

1. MATCH 本票 sha8 **`86eef522`** + 本回执
2. 令 Data：**先**消费票1 写 `manifest.build` → 再消费票2（另票）物化
3. 勿混票；勿复用 `4377eb59`；勿假 DONE；勿签叶30

≠X2；不报 Leo；live=false。

---
文档结束（Arch 方案A 票1 SIGNED）
