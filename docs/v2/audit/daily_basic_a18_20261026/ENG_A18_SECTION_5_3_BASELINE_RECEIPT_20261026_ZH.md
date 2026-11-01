# Eng 回执：A18 §5.3 引导基线 / ref_build（D1）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng（执行手） |
| 时刻（America/New_York） | `2026-10-26T17:59:21-0400`（墙钟 2026-10-26 17:59:21 EDT） |
| **结论** | **A9_RECONCILE_FAIL** |
| 原因 | 单进程逐年 ref_build 2014..2026（end=`20261016`）完成；对账 `reconcile_ok=false`；`diff_count=286`（全为 `year_sorted_content_col_hashes`；**无** rows 差）；按 A9 **未写** baseline |
| Arch EXEC `.ok` | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok` |
| Arch `.ok` sha8 | **`6de02e74`**（开跑前/结束后仍在；**本 Eng 未消费/未归档**） |
| 审稿 | `docs/v2/audit/daily_basic_a18_20261026/ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md` sha8 **`232a2295`** |
| SIGNED EXEC | `ARCH_A18_SECTION_5_3_BASELINE_EXEC_SIGNED_20261026_ZH.md` sha8 **`bb04979f`** |
| 签窗 | 2026-10-26 **17:45–23:00** America/New_York（not_before=17:45；expires=23:00） |
| live | **false** |
| 本票 | ≠seed / ≠allow_run / ≠物化 / ≠改生产 parquet·manifest |

## 1. 执行身份

| 项 | 值 |
|---|---|
| pid | **2902104**（`/tmp/a18_s53_driver.pid`） |
| driver | `/tmp/a18_s53_driver.py`（Arch 审 §3.1） |
| OUT_TMP | `/tmp/a18_s53_20261026T175303_2902093` |
| 开跑 | ≈2026-10-26 17:53:03 EDT（窗内；非 16:15–17:45） |
| 结束 | ≈2026-10-26 17:55:59 EDT（`driver.log` mtime） |
| 推断 exit / rc | **9**（驱动 `return 9` = RECONCILE_FAIL A9；日志末行 `RECONCILE_FAIL diff_count= 286 baseline_NOT_written A9`） |
| 第二驱动 | **未启** |

## 2. 钉核（结束后复算）

| 项 | sha8 | vs pin |
|---|---|---|
| DEST `daily_basic_full_tushare.parquet` | `f6bbf9e5` | **MATCH** |
| MAN `daily_basic_full_tushare_manifest.json` | `8c2c978b` | **MATCH** |
| EXEC `.ok` | `6de02e74` | **仍在 / 未消费** |
| 审稿 | `232a2295` | MATCH |
| baseline `daily_basic_full_tushare_build_baseline.json` | **ABSENT** | A9 未写 |

## 3. ref_build 逐年摘要

| 年 | rows | peak_vmhwm_kb |
|---|---:|---:|
| 2014 | 570677 | 217500 |
| 2015 | 570310 | 227964 |
| 2016 | 642209 | 251184 |
| 2017 | 743941 | 251184 |
| 2018 | 817637 | 251184 |
| 2019 | 885332 | 255224 |
| 2020 | 946539 | 260192 |
| 2021 | 1062121 | 260192 |
| 2022 | 1171417 | 260192 |
| 2023 | 1258463 | 260192 |
| 2024 | 1292960 | 260192 |
| 2025 | 1313182 | 260192 |
| 2026 | 1035157 | 260192 |
| **合计** | **12309945** | peak_all=**260192** |

- years=`2014..2026`；end=`20261016`
- ref 合计 rows **12309945**（与 dest/manifest rows 一致）
- **peak VmHWM（全年）** = **260192** kB
- **a13_ok** = **true**（limit 1_000_000 kB）

## 4. 对账（A9）

| 项 | 值 |
|---|---|
| reconcile_ok | **false** |
| diff_count | **286** |
| kinds | `year_sorted_content_col_hashes` ×286；**rows 差 = 0** |
| 覆盖 | 每年 22 列 × 13 年 = 286（全列全年均 hash 不一致） |
| DIFFS | `OUT_TMP/DIFFS.json`（全量 286） |
| reconcile | `OUT_TMP/reconcile.json`（`diffs_sample` 前 100） |
| baseline | **未写**（A9） |

### 差异样例（前 8；完整见 DIFFS.json）

```
year=2014 kind=year_sorted_content_col_hashes col=available_at
  ref=d41fef77963c66061cd00fae229d16be5a872b1044688bfa4cb684ba46bc97bc
  dest=038a8f3a5cfb9a86ada73d4d987f7e364f684e50fee7e879263988370b48f1b3
year=2014 kind=year_sorted_content_col_hashes col=close
  ref=65ab96ff30b757df97488ced108df0dad3652a6c63739e111b2ad59e2d152a93
  dest=12e233ee24cbbaf7b99a064bf64bdab9fb5da717cd9cef8d51621a017f653552
year=2014 kind=year_sorted_content_col_hashes col=ts_code
  （见 DIFFS.json）
… 每年 22 列同模式；2026 末列 volume_ratio 等同构 …
```

**Eng 观察（交 Arch/主，非定论）**：rows 全年对齐且合计=12309945，但 `year_sorted_content_col_hashes` 全列全季不一致 → 更像 **hash 口径/实现路径**（ref vs dest 侧）系统偏差，而非单年行数漂移。后续须 Arch 判：修驱动对账口径 vs 数据真不一致。

## 5. driver.log 末段

```
REF_BUILD_YEAR_END 2026 rows=1035157 peak_kb=260192
RECONCILE_FAIL diff_count= 286 baseline_NOT_written A9
OUT_TMP /tmp/a18_s53_20261026T175303_2902093
```

## 6. 禁区回执（本回合 Eng）

| 禁项 | 本回合 |
|---|---|
| seed `manifest.build` | **未做** |
| allow_run / 物化 | **未做** |
| 改生产 parquet / manifest | **未改**（dest/man sha 仍 MATCH） |
| 复用 enable `.ok` `4377eb59` | **未复用** |
| 盲 seed / 代码 bootstrap | **未做** |
| 消费/归档 EXEC `.ok` | **未做**（Arch only；`.ok` 仍在） |
| 删除 OUT_TMP | **未删** |
| 候选3 enable | **仍禁** |
| live | **false** |

## 7. 交付物路径

| 路径 | 说明 |
|---|---|
| `OUT_TMP/reconcile.json` | reconcile_ok=false；peak；a13 |
| `OUT_TMP/DIFFS.json` | 全量 286 差异（交 Arch/主） |
| `OUT_TMP/raw_inventory.json` | raw inventory（未写 baseline，故未入产品） |
| `OUT_TMP/ref_year_YYYY.json` | 2014..2026 |
| `OUT_TMP/driver.log` | 全程日志 |
| baseline 产品路径 | **ABSENT** |

## 8. 下一跳（Eng 停；建议主裁）

差异已列；**Eng 停**。本票 **不**盲 seed；**不**自启第二驱动；**不**写 baseline。

| 建议 | 说明 |
|---|---|
| **A. Arch 先判 hash 口径**（优先） | rows 全年对齐且合计=manifest `12309945`，但 22×13=286 全为 `year_sorted_content_col_hashes` → 高度像 **ref vs dest 对账实现/列序/类型** 系统偏差；请 Arch 对照 `ref_build_year` 与 §3.1 dest 侧 hash 路径，确认是否驱动 bug |
| **B. 确认数据真不一致** | 若口径无误 → 按 dig P1-4：成品可能早于现行 raw；须 Data/Arch 另票定修成品或重物化路径（**≠本票 seed**） |
| **C. `.ok` 处理** | 审文 `archive_by=Arch only` + `single_use=true` → **Eng 未挪** live `.ok` `6de02e74`；请 **Arch CONSUME/A9 归档** 后，主另排修口径/重跑票（勿复用本 EXEC） |
| **D. 禁** | 盲 seed `manifest.build` / 复用 `4377eb59` / allow_run / 物化 / 带病写 baseline |

OUT_TMP 保留：`/tmp/a18_s53_20261026T175303_2902093`（含 `DIFFS.json` / `reconcile.json`）。

— Eng D1 / A18 §5.3 / 2026-10-26
