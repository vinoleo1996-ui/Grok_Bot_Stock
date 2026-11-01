# Data 回执：方案 A · 票1 baseline→manifest.build 种子 **CONSUMED_PASS**

| 项 | 值 |
|---|---|
| 角色 | QuantLab Data |
| 时刻（America/New_York） | `2026-10-26T18:48:42-04:00`（墙钟 2026-10-26 18:48:42 EDT） |
| **结论** | **CONSUMED_PASS** |
| `.ok` 原路径 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_MANIFEST_BUILD_BASELINE_SEED.ok` |
| `.ok` sha8 / 全长 | **`86eef522`** / `86eef5227480cbe11d5e65f0083ff212dddef52e8f48005ae92d544b420daa5b` |
| SIGNED | sha8 **`4ca6cdd5`** / `4ca6cdd5d1e3b390135a6fb3dc9e0897dda75142123443cc03ffa3dcce2ee7bd` |
| 归档 | `output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_MANIFEST_BUILD_BASELINE_SEED.86eef522.CONSUMED_PASS.20261026T184842ET.ok`（内容 sha 不变） |
| live | false |

## 1. 签前复核

| 项 | 结果 |
|---|---|
| 墙钟 ∈ [18:44:50, 08:00) ET | **PASS** |
| baseline `273163cc` | **MATCH** |
| dest `f6bbf9e5` | **MATCH**（写后仍同；**未改 parquet 字节**） |
| manifest pre `8c2c978b` 无 build | **PASS** |
| QUIET ABSENT / 无真实数据进程 | **PASS**（开跑前核） |
| 禁复用 `4377eb59` | **遵守** |

## 2. 写入的 `manifest.build`

```json
{
  "mode": "baseline_seed",
  "prev_sha256": null,
  "new_sha256": "f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948",
  "transform_sha": "308b5054c39801116fd0eb19b4e4bd10bdccd4b4d40bfb67dd06a58fa67ab974",
  "runtime_versions": {
    "python": "3.13.5",
    "pandas": "3.0.6",
    "pyarrow": "26.0.0",
    "numpy": "2.5.4"
  },
  "raw_inventory": "91b1b0694f9f1345489d31f48ae9c1d7daf4c056876c57a7e56ac3a45b9519d6",
  "rows_by_year": {
    "2014": 570677,
    "2015": 570310,
    "2016": 642209,
    "2017": 743941,
    "2018": 817637,
    "2019": 885332,
    "2020": 946539,
    "2021": 1062121,
    "2022": 1171417,
    "2023": 1258463,
    "2024": 1292960,
    "2025": 1313182,
    "2026": 1035157
  },
  "seeded_from": "daily_basic_full_tushare_build_baseline.json",
  "seeded_from_sha256": "273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486",
  "seeded_at": "2026-10-26T18:48:42-04:00"
}
```

| 项 | 值 |
|---|---|
| manifest post sha256 | `f3a727a5e740778d1b64030d1e66ed576db1f6dab8e2969a98d49fa4b8359d5f`（sha8 `f3a727a5`） |
| `build.new_sha256` | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` **PRESENT MATCH** |
| 其他顶层键 | **保留**（path/rows/date_*/schema/backup_path/…） |
| baseline 字节 | **未改** `273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486` |

## 3. 禁区

- 未物化 / 未跑 incr / 未消费票2 / 未假 DONE / 未挂 QUIET / 未候选3 enable / 未改 parquet / 未改 baseline
- 下一跳：核 `new_sha256` 后消费票2 `.ok` `6d5aa893` 物化缺口

---
文档结束（Data 票1 CONSUMED_PASS）
