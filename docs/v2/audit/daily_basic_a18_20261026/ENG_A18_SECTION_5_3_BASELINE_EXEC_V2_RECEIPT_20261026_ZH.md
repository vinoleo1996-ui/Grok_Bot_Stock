# Eng 回执：A18 §5.3 EXEC_V2 全窗基线（D1）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng（执行手 / 背景监视） |
| 时刻（America/New_York） | `2026-10-26 18:34:35 EDT`（ISO `2026-10-26T18:34:35-0400`） |
| **结论** | **DONE / RECONCILE_OK_BASELINE_WRITTEN** |
| 路径 | STARTED → DONE（A9 一致 → 已写 baseline） |
| pid | **2950358**（已退出；推断 exit **0**；stderr 空） |
| OUT_TMP | `/tmp/a18_s53_v2_20261026T182853_2950340` |
| 开跑 | 2026-10-26 **18:28:54 EDT** |
| 结束 | ≈2026-10-26 **18:31 EDT**（`reconcile.json` / baseline mtime） |
| live | **false** |
| 纸面 | **HOLD**（本票未触纸面） |
| Leo | **不报** |

## 1. 授权钉（结束后复算仍 MATCH）

| 钉 | sha8 | 状态 |
|---|---|---|
| EXEC_V2 `.ok` `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC_V2.ok` | **`a62881b9`** | **仍 live / Eng 未消费未归档**（Arch only） |
| QUIET `output/loop/RESEARCH_QUIET.lock` holder=`a18_s53_v2` | **`bf4548d4`** | **仍挂；禁 lift** |
| SIGNED `ARCH_A18_SECTION_5_3_BASELINE_EXEC_V2_SIGNED_20261026_ZH.md` | **`b49544ed`** | MATCH |
| dest 同构审 `…DEST_ISOMORPH_REVIEW…` | **`0815e13f`** | MATCH |
| driver_v2 `a18_s53_driver_v2_dest_monthly.py` | **`af15b52d`** | MATCH |
| helper `a18_s53_year_sorted_content_col_hashes_helper.py` | **`3094f0b6`** | MATCH |
| 生产 incr `scripts/acquire/daily_basic_incremental.py` | **`a7ac54b3`** | **UNTOUCHED MATCH** |
| dest parquet | **`f6bbf9e5`** | MATCH（只读） |
| manifest | **`8c2c978b`** | MATCH（只读） |
| 判稿 HASH_CALIBER | **`6466c490`** | （reconcile.judge_sha8） |

窗：not_before 18:25 → expires **23:02 ET**（跑时窗内）。YEARS=**2014..2026**；END=`20261016`。

## 2. 对账（A9）+ A13

| 项 | 值 |
|---|---|
| reconcile_ok | **true** |
| diff_count | **0** |
| diffs_sample | `[]` |
| dest_hash_caliber | `monthly_accumulate_isomorphic_ref_build_year_v2` |
| years_completed | **13** / 13 |
| peak VmHWM（全年） | **263040** kB |
| a13_limit_kb | 1_000_000 |
| a13_ok | **true** |
| baseline | **PRESENT** `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` sha8 **`273163cc`**（stdout：`BASELINE_WRITTEN … sha8 273163cc`） |

`OUT_TMP/reconcile.json` 钉：ok=true；peak_vmhwm_kb_all_years=263040；a13_ok=true；judge_sha8=6466c490。

## 3. ref_build 逐年（stdout）

| 年 | rows | peak_kb（累计） |
|---|---:|---:|
| 2014 | 570677 | 218376 |
| 2015 | 570310 | 220508 |
| 2016 | 642209 | 240240 |
| 2017 | 743941 | 240240 |
| 2018 | 817637 | 254628 |
| 2019 | 885332 | 260292 |
| 2020 | 946539 | 263040 |
| 2021 | 1062121 | 263040 |
| 2022 | 1171417 | 263040 |
| 2023 | 1258463 | 263040 |
| 2024 | 1292960 | 263040 |
| 2025 | 1313182 | 263040 |
| 2026 | 1035157 | 263040 |

OUT_TMP 另有：`ref_year_YYYY.json`×13、`raw_inventory.json`、`driver.stdout.log`、`driver.stderr.log`（0 字节）、`ENG_STARTED.txt`。

## 4. 硬禁复述（本票遵守）

- **禁**复用 `6de02e74` / `4377eb59` / `a158f17a` / `5ae077fa`
- **禁** seed / allow_run / 物化 / 改生产 parquet·manifest
- **禁**第二驱动；**禁**候选3 enable
- **禁** lift QUIET（`bf4548d4` 仍挂）
- **禁** Eng 消费/归档 `.ok`（Arch only；`.ok` **仍 live** `a62881b9`）
- 单进程逐年；只写 OUT_TMP +（A9 通过时）baseline
- live=false；**不报 Leo**；纸面 HOLD

## 5. 产物

| 产物 | 路径 | 备注 |
|---|---|---|
| 本回执 MD | `docs/v2/audit/daily_basic_a18_20261026/ENG_A18_SECTION_5_3_BASELINE_EXEC_V2_RECEIPT_20261026_ZH.md` | 本文件 |
| 本回执 JSON | `…/ENG_A18_SECTION_5_3_BASELINE_EXEC_V2_RECEIPT_20261026.json` | 机器字段 |
| baseline | `data/v2/valuation/daily_basic_full_tushare_build_baseline.json` | sha8 **`273163cc`** |
| OUT_TMP reconcile | `/tmp/a18_s53_v2_20261026T182853_2950340/reconcile.json` | ok=true |

## 6. 下一跳

交主 MATCH D1 → 令 Arch CONSUME `.ok` + 处置 QUIET（Eng **不**自 lift/不自消费）。纸面仍 HOLD 至主另令。Eng 停等。不报 Leo。

---
文档结束（Eng A18 §5.3 BASELINE_EXEC_V2_RECEIPT）
