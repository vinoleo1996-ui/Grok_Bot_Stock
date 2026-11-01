# Eng DIFF：A18 §5.3 §3.1 dest `year_sorted_content_col_hashes` 月累加同构

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻（America/New_York） | `2026-10-26 18:13 ET`（墙钟） |
| 依据判稿 | Arch **HASH_CALIBER_BUG** sha8 **`6466c490`** |
| 归档回执 | Arch A9 archive sha8 **`f28183e0`**（EXEC `.ok` `6de02e74` live ABSENT） |
| 先前 A9 D1 | Eng sha8 **`09c1b2c8`** |
| 生产 incr | **未改** pin `a7ac54b3`（全长 `a7ac54b3ecdf33d338710df5c96f447fbec51affdcfbf167fb3e00648f678dd8`） |
| DIFF sha8 | 见 `SHA256SUMS` 本文件行 |
| RECEIPT sha8 | 见 `SHA256SUMS` |
| live | false |

## 0. 一句话

旧 dest 侧「整年一次」物理 dig 与 `ref_build_year`「按月累加」不同构 → 286 列全异（口径 bug）。本 DIFF 交付 **侧草稿** helper + v2 驱动：dest 年表去重排序后按月 `groupby` → header-once + 月 `_row_group_physical_col_hashes` 累加；2014 钉测相对 OUT_TMP `ref_year_2014.json` **22/22 MATCH**（stub/rows 亦 MATCH）。**未**写 baseline；**未**复跑 2014..2026；**未**复用 `.ok`/`4377eb59`。

## 1. 旧 vs 新（dest 侧）

### 1.1 旧（`/tmp/a18_s53_driver.py`，导致 A9）

```
year tbl → pandas → drop_duplicates → sort
→ 外层 header-once（dtype 取 round-trip 前 tbl）
→ 一次 _row_group_physical_col_hashes(整年 tbl2)
→ H(header ‖ dig(year))
```

### 1.2 新（权威 = `ref_build_year`）

```
year tbl → pandas → drop_duplicates → sort
→ groupby(month=trade_date.month) 升序
→ 每月：month drop_duplicates+sort → from_pandas
→ 首月 header-once（dtype = 该月 from_pandas 列类型）
→ 每月 accumulate bytes.fromhex(_row_group_physical_col_hashes(month_tbl)[c])
→ H(header ‖ dig(m1) ‖ … ‖ dig(m12))
```

结构性对齐判稿 §2.3 / §5.3 修法要点。

### 1.3 次要瑕疵一并收

| 瑕疵（判稿 §4） | 本草稿处理 |
|---|---|
| 外层 dtype 取 round-trip 前 tbl | **已消**：header dtype 与物理 dig 同源（首月 `from_pandas` 表） |
| 双重 header（外层 + physical 内嵌） | **保持与 ref 同构**（两侧都双重；单一化留给后续设计澄清，本票不单独改 ref） |

## 2. 交付物（均在 audit pack，生产树零改）

| 文件 | sha8 | 说明 |
|---|---|---|
| `a18_s53_year_sorted_content_col_hashes_helper.py` | **`3094f0b6`** | 纯函数 helper；侧草稿；全长 `3094f0b60fa721922489b5ea21b1e7c4ca29b1b7d2bb8b65288b80b22fa9ab02` |
| `a18_s53_driver_v2_dest_monthly.py` | **`af15b52d`** | 完整 §3.1 驱动（A9 仍有效；禁区同审）；全长 `af15b52dbd54ed52216b41891f29a833cd13084f9c21512ca1fe01389e622deb` |
| `ENG_A18_SECTION_5_3_DEST_HASH_ISOMORPH_PIN_2014_PROOF.json` | **`2cc3e356`** | 2014 钉测证明；全长 `2cc3e3568a33c7e6283561942fef66b96f4e0ae95a237ce43e3c0f05494a4b5f` |
| 本 DIFF | 见 `SHA256SUMS` | 避免自指改写抖动 |
| RECEIPT | 见 `SHA256SUMS` | — |

`py_compile` 对 helper/driver **PASS**（侧草稿；无需 `.ok`）。

## 3. 2014 钉测

| 项 | 值 |
|---|---|
| dest | `data/v2/valuation/daily_basic_full_tushare.parquet` pin `f6bbf9e5`（只读 2014 RG） |
| ref 钉 | `/tmp/a18_s53_20261026T175303_2902093/ref_year_2014.json` |
| rows | dest=ref=**570677** |
| stub | **MATCH** `02bb7e21…` |
| `year_sorted_content_col_hashes` | **22 / 22 MATCH**（out_cols 全列） |
| mismatched_cols | `[]` |
| 方法 | `year_dedupe_sort_then_groupby_month_header_once_monthly_physical` |
| 复验 | 内联实现与 audit helper import 各跑一次，均 22/22 |

## 4. 明确未做（禁区）

- 未复用 `.ok` `6de02e74` / enable `4377eb59`
- 未 seed `manifest.build` / allow_run / 物化 / 写 baseline / 改生产 parquet·manifest
- 未启动第二轮全量 2014..2026 ref_build
- 未改 `scripts/acquire/daily_basic_incremental.py`（pin 仍 `a7ac54b3`）
- 未 git commit；未启候选3；未触叶25/叶30 consumed oks
- 纸面日终仍 HOLD（无 nightly DONE；禁 --force）

## 5. 建议下一跳（给主 / Arch）

1. Arch **复审**本 DIFF + v2 驱动命令清单（对照审 `232a2295` §3 / 判 `6466c490`）
2. 主 **另签新窗** + 新 `.ok`（**禁**复用 `6de02e74`）
3. 新窗内用 v2 驱动重跑 §5.3（A9 仍钉；不一致不写 baseline）

---
文档结束（Eng A18 §5.3 DEST_HASH_ISOMORPH_DIFF）
