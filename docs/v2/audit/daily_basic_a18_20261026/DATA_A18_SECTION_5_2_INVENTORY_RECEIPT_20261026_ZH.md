# Data 回执：A18 §5.2 只读盘点

| 项 | 值 |
|---|---|
| 角色 | QuantLab Data（执行手） |
| 时刻（America/New_York） | `2026-10-26T14:21:36-04:00`（墙钟 2026-10-26 14:21:36 EDT） |
| **结论** | **PASS** |
| 原因 | 空档干净；dest/manifest 全长 sha 与钉 MATCH；baseline ABSENT；has_build=false；metadata rows/date_max 与 manifest 一致；无 pending/quarantine/tmp/parts/raw *.tmp.parquet；无未处理残留。 |
| Arch `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_2_INVENTORY.ok` |
| Arch `.ok` 全长 sha256 | `dc51a0b30fdddbbf94234ad346ec15a180bd5b256d5772cdf1c4fc24efcc68ed`（sha8 `dc51a0b3`） |
| 审稿 | `docs/v2/audit/daily_basic_a18_20261026/ARCH_A18_SECTION_5_2_INVENTORY_REVIEW_20261026_ZH.md` sha8 **`abe5a3c5`** 全长 `abe5a3c581df356696f21f28c28aef9c21727b46c05e7e8016fa60e8b7626b11` |
| SIGNED 回执 | `ARCH_A18_SECTION_5_2_INVENTORY_SIGNED_20261026_ZH.md` sha8 **`40304dda`** 全长 `40304dda54698e615788477f939eef451c621c81e5a71d344bc9722cd7c6c166` |
| 签窗 | 2026-10-26 14:15–16:00 America/New_York |
| live | false |
| 本票 | ≠§5.3 |

## 1. 空档门

| 项 | 结果 |
|---|---|
| pgrep（acquire\|nightly\|daily_basic\|ref_build\|materialize\|tier1_materialize\|eng_daily_panels\|run_nightly） | **空**（PGREP_CLEAN=yes） |
| `output/loop/RESEARCH_QUIET.lock` | **无**（QUIET_ABSENT=yes） |
| 墙钟在窗内 | **是**（执行起 `2026-10-26 14:21:36 EDT` 前已核 14:20:49 ET；清单完成约 14:20:58 ET；写回执 `2026-10-26 14:21:36 EDT`） |

## 2. dest / manifest / baseline

| 项 | 值 | vs pin |
|---|---|---|
| DEST | `data/v2/valuation/daily_basic_full_tushare.parquet` | — |
| DEST size / mtime / inode | 745129744 / 2026-10-25 01:09:09.440449311 -0400 / 138082 | — |
| DEST 全长 sha256 | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948`（sha8 `f6bbf9e5`） | **MATCH**（钉 `f6bbf9e5…`） |
| MAN | `data/v2/valuation/daily_basic_full_tushare_manifest.json` | — |
| MAN size / mtime / inode | 831 / 2026-10-25 01:15:03.092072452 -0400 / 141320 | — |
| MAN 全长 sha256 | `8c2c978b384e8d3206da0876686fa214d7960353f472e81151a7acc3b0c74ac8`（sha8 `8c2c978b`） | **MATCH**（钉 `8c2c978b…`） |
| BASE | `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` | — |
| baseline_exists | **false** | **ABSENT**（`stat` No such file；`baseline_sha=ABSENT`） |

## 3. pq.read_metadata + manifest JSON 键（禁读行）

| 项 | 值 |
|---|---|
| num_rows | 12309945 |
| num_row_groups | 18 |
| num_columns | 22 |
| schema_names | ['ts_code', 'instrument_id', 'trade_date', 'close', 'turnover_rate', 'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ttm', 'total_share', 'float_share', 'free_share', 'total_mv', 'float_mktcap', 'available_at', 'source', 'quality_status', 'promotion_approved'] |
| manifest_keys | ['available_at_rule', 'backup_path', 'built_at', 'date_max', 'date_min', 'history_diff_rows', 'instruments', 'note', 'path', 'priority_cols', 'promotion_approved', 'rows', 'schema'] |
| has_build | **false** |
| rows | 12309945 |
| date_min | 2014-01-02 |
| date_max | 2026-10-16 |
| built_at | 2026-10-18T00:21:47-0400 |
| backup_path | `/workspace/QuantLab/backups/valuation/daily_basic_full_tushare.20261018_0020.parquet` |
| rows_match_meta | **true** |
| baseline_exists | **false** |

## 4. pending / quarantine / tmp / parts / raw *.tmp.parquet

| 项 | 结论 |
|---|---|
| `_daily_basic_parts_*` | **NO_PARTS_DIRS** |
| `*pending*` | **NO_PENDING** |
| `_quarantine` | **NO_QUARANTINE_DIR** |
| find VAL maxdepth2 `*.tmp`/`*.tmp.*`/`*.part*`/`*pending*` | **空**（NO_TMP_PARTS_PENDING） |
| find RAW `*.tmp.parquet` | **空**（NO_RAW_TMP_PARQUET） |

## 5. backups 目录清单（只列；未动）

### backups/valuation/

```
daily_basic_full_tushare.20261014_1136.parquet
daily_basic_full_tushare.20261014_1137_dupbug.parquet
daily_basic_full_tushare.20261014_1803.parquet
daily_basic_full_tushare.20261017_2357.parquet
daily_basic_full_tushare.20261018_0020.parquet
```

（其中 `20261014_1136` / `20261014_1137_dupbug` nlink=2，与 valuation_pinned 硬链一致；`20261018_0020` = manifest.backup_path。）

### backups/valuation_pinned/

```
daily_basic_full_tushare.20261014_1136.parquet
daily_basic_full_tushare.20261014_1137_dupbug.parquet
```

## 6. 残留

- **无未处理残留**（pending/quarantine/tmp/parts/raw *.tmp.parquet 全无）。
- 本票 **未** 做隔离；若日后发现残留，隔离另签（本 `.ok` `allow_quarantine_move=false`）。

## 7. 禁区声明（本回合）

- **未** `pq.read_table` / `read_row_group` / `to_pandas` / `take` / 任何读行
- **未** 写/改/删/移动生产 parquet / manifest / baseline
- **未** 跑 incr / ref_build / materialize / nightly / tier1_materialize
- **未** seed `manifest.build`；**未** 写 `build_baseline.json`
- **未** quarantine 移动
- **未** 复用 enable `.ok` sha8 `4377eb59`
- **未** 触碰叶25 CONSUMED `3c297052` / `d37a157e`
- 本票 **≠§5.3**；live=false；promotion=false

## 8. 命令清单来源

审稿 §3 原样执行（`abe5a3c5`）；工具仅 `stat`/`ls`/`sha256sum`/`find`(只列)/`python3`+`pq.read_metadata`/读 manifest JSON 键。

---
文档结束（Data A18 §5.2 只读盘点回执；结论 **PASS**）
