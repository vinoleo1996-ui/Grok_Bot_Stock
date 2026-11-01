# Data · nightly 20261026 物化 + DONE marker 回执

- written_at_et: 2026-10-26T18:54:18.795530-04:00
- writer: QuantLab Data
- live: false
- promotion_approved: false

## 票与前置

| 项 | 值 |
|---|---|
| 票1 | CONSUMED_PASS（勿重做）`86eef522` → `_consumed/...184842ET.ok`；种子回执 sha8 `940d4dd7` |
| 票2 live sha 全长 | `6d5aa8932bfa874df4c16107eb535ad205f08d52f2ba56359380337e93493087` |
| 票2 SIGNED sha8 | `6ce353eb` |
| 票2 归档 | `output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_INCR_ALLOW_RUN_GAP_1019_1026.6d5aa893.CONSUMED_PASS.20261026T185307ET.ok` |
| 硬门 | t1 live ABSENT；manifest/dest pre=`f6bbf9e5…`；QUIET ABSENT；无冲突进程；票2未过期 |

## incr 物化

| 项 | 值 |
|---|---|
| 脚本钉 | `scripts/acquire/daily_basic_incremental.py` sha8 `a7ac54b3` |
| transform | `308b5054…` MATCH |
| 调用 | sys.path=`scripts/acquire`+`.`；`--mode incremental --end 20261026 --start 20140101`；路径显式 |
| 首次失败 | `ModuleNotFoundError: tier1_materialize`（未插 path）→ 修正 path 后重试 |
| 二次失败 | `AttributeError: str has no get`：seed 将 `build.raw_inventory` 写成 digest 字符串 `91b1b069…`，incr `_rebuild_years` 要 dict.by_year |
| 兼容处理 | 原子改写 `raw_inventory`→`{mode:seed_digest_coerced, seed_digest:91b1b069…, by_year:{}}`；**未改** parquet / baseline；commit 后由 incr 覆写 build |
| incr rc | **0** |
| reason_code | OK |
| rebuilt_years | [2026] |
| copied_years | 2014..2025 |
| prev_sha256 | `f6bbf9e51af78dfab2c021fa8809c58ad0d36df7293f8a488200b9dd5ceaf948` |
| new_sha256 | `31c232e3f1664b370fcf45b95b73b281fcf31c275491a6353ed6eb33c6080c4e` |
| rows | 12343357（pre 12309945 → +33412） |
| trade_date max | **2026-10-26**（parquet column stats） |
| max_rss_mb | 954（≤1500） |
| peak_vmhwm_kb | 1032816 |
| history_diff_rows | 0 |
| backup | `backups/valuation/daily_basic_full_tushare.20261026_185248.parquet` |

## mid_large / freshness

| 项 | 值 |
|---|---|
| mid_large rc | 0 |
| mid_large | APPENDED 20261019..23+20261026；last_date **2026-10-26**；rows 5580516；sha8 `c74112a8` |
| freshness | overall **ok**；expected 20261026；stale_tables [] |
| warn_list | sw_pit, cyq_perf_raw, tier3_*（WARN 级，不影响 DONE） |

## REQUIRED 六表矩阵（last==20261026）

| 表 | last_date | rows | sha8 |
|---|---|---|---|
| etf_daily_adj | 20261026 | 1575090 | d9ea0d94 |
| daily_ohlcv_raw_pit | 20261026 | 100135 | f8eaa9c1 |
| daily_basic | 20261026 | 12343357 | 31c232e3 |
| mid_large_universe | 20261026 | 5580516 | c74112a8 |
| etf510300 | 20261026 | 3501 | a5d31a85 |
| asof_ts | 20261026 | n_panels=5585 | 6fea85e6 |

daily_update_status.status = **ok**；target_trade_date=2026-10-26。

## DONE marker

| 项 | 值 |
|---|---|
| path | `output/nightly_markers/nightly_20261026.DONE.json` |
| sha256 | `fbddcd2bcab1fdec8127ab51f414cf8ed2a8433f6b8ebc330dde5a208e7f8b71` |
| sha8 | `fbddcd2b` |
| status | OK |
| O_EXCL | yes（不覆盖） |

## baseline / 禁区

| 项 | 值 |
|---|---|
| baseline sha | `273163cceb18c9da82d42f04ce6d60f82a96c8572229643cc16e133638aa5486`（sha8 **273163cc** 未改） |
| 禁复用 enable 4377eb59 | 遵守 |
| 禁候选3 enable | 遵守 |
| 禁 --force 纸面 | 遵守 |
| 禁挂 QUIET | 遵守（全程 ABSENT） |
| 禁假 DONE | 遵守（REQUIRED 全到 D 后才写） |
| 禁 env | QL_DB_INCR_ALLOW_STALE_SHA / LOOSE_READBACK / ALLOW_FULL / QL_C5_IGNORE 全程 absent |
| 禁抬帽 | 遵守；rss≤1500 |

## 交叉钉（D/P raw）

- P=20261023 daily_basic raw rows=5572 sha8=f29d1850
- D=20261026 daily_basic raw rows=5570 sha8=23f697ec
- D=20261026 daily raw rows=5570 sha8=9b50ee9e
