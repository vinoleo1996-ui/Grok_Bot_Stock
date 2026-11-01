# Arch 口径判：A18 §5.3 dest/ref `year_sorted_content_col_hashes`（优先路径 A）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行手） |
| 时刻（America/New_York） | `2026-10-26T18:05:00-04:00`（墙钟 2026-10-26 18:05 ET） |
| **结论** | **HASH_CALIBER_BUG**（驱动/对账实现偏差；**非**成品 vs raw 真不一致） |
| 依据跑次 | Eng OUT_TMP `/tmp/a18_s53_20261026T175303_2902093`；审 `232a2295` §3.1；驱动 `/tmp/a18_s53_driver.py`；incr `a7ac54b3` |
| Eng D1 | sha8 **`09c1b2c8`**；A9_RECONCILE_FAIL；diff_count=**286**；rows 差=**0**；合计 rows=12309945；peak_kb=260192 a13_ok；baseline ABSENT |
| 本判动作 | 只读对照 + 2014 最小重放；**未**写 baseline；**未**改生产；**未**代跑全量；live=false |

## 0. 一句话

全年 **行数齐**（13 年 rows 差=0）但 **22 列 × 13 年 = 286** 条 `year_sorted_content_col_hashes` **全异** → 系统偏差。根因：§3.1 驱动 **dest 侧按「整年一次」**拼物理 dig，而 `ref_build_year` **按月累加**物理 dig；二者即使用同一排序内容也必然全列失配。2014 最小对照：key stub / 行列内容 **全等**；把 dest 2014 按月重放累加后 **22/22 列 hash 与 ref MATCH**。故判 **HASH_CALIBER_BUG**，**非** TRUE_CONTENT_MISMATCH。

## 1. 事实钉（跑次）

| 项 | 值 |
|---|---|
| reconcile.ok | false |
| diff_count | 286 |
| kind | 全部 `year_sorted_content_col_hashes`（rows 差=0） |
| years | 2014..2026（13；每年恰好 22 列） |
| cols | `available_at, close, dv_ttm, float_mktcap, float_share, free_share, instrument_id, pb, pe, pe_ttm, promotion_approved, ps, ps_ttm, quality_status, source, total_mv, total_share, trade_date, ts_code, turnover_rate, turnover_rate_f, volume_ratio` |
| 含稳定键列 | **是**（`ts_code` / `trade_date` / `close` 等亦全异）→ 强系统偏差信号 |
| ref 2014 stub | `02bb7e2122743075e1f615aa6798ee3b1fd945f99f4d081fff3ed87451b88c9d`（`year_sorted_content_col_hashes_stub`） |
| A9 | baseline **未写**（正确） |

## 2. 两侧实现对照（口径）

### 2.1 ref（`daily_basic_incremental.ref_build_year`，incr `a7ac54b3`）

- 按月读 raw → `transform_daily_basic_one` → 月内 `drop_duplicates(ts_code,trade_date,keep=last)` → `sort_values([trade_date,ts_code])`
- **外层 header 只喂一次**（首月）：`name + \0 + arrow_type + \0`
- **每月**调用 `_row_group_physical_col_hashes(month_table)`（该 dig **自身**再含 `name+\0+type+\0+nrows+\0+payload`）
- `col_hashes[c].update(bytes.fromhex(dig_month))` → **月 dig 串联**
- A13：不全年驻留大表

### 2.2 dest（审稿 §3.1 / `/tmp/a18_s53_driver.py`）

- 按年拼 row groups → pandas → 年级 `drop_duplicates` → `sort_values([trade_date,ts_code])`
- 外层 header：`name + \0 + **原 parquet tbl** dtype + \0`（注意：dtype 取自 round-trip **前**的 `tbl`）
- **一次** `_row_group_physical_col_hashes(tbl2)`（`tbl2=from_pandas` 后的整年表）→ 只串联 **一个年 dig**
- 与 ref 的「月 dig 串联」**聚合粒度不同** → 即便 payload 字节流相同，复合 sha 也必异

### 2.3 结构性不等式（充分条件）

对任意列 c：

`H( header ‖ dig(year) )  ≠  H( header ‖ dig(m1) ‖ dig(m2) ‖ … ‖ dig(m12) )`

（各 `dig(*)` 还内嵌各自 `nrows`，年 nrows ≠ 月 nrows，进一步放大差异。）

故出现「行数全齐 + 含 `ts_code`/`trade_date` 在内所有列全异」的 **系统图案**，无需假设成品损坏。

## 3. 2014 最小对照（内容 vs 口径）

| 检查 | 结果 |
|---|---|
| dest rows / ref monthly sum / year-dedupe | 570677 / 570677 / 570677 |
| stub（`ts_code,trade_date` 行流 sha） | **MATCH** `02bb7e21…` |
| keyset only_dest / only_ref | **0 / 0**（both=570677） |
| 列内容（str/num）：`ts_code, trade_date, close, pe, total_mv, available_at, source, promotion_approved` | **全等**（n_diff=0） |
| head/tail 样本 | dest=ref（如 `000001.SZ@2014-01-02 close=12.23` … `603998.SH@2014-12-31 close=35.26`） |
| Arrow dtype（ref 首月 vs dest after_pd） | 一致：`large_string` / `timestamp[us]` / `double` / `timestamp[us,tz=Asia/Shanghai]` / `bool` |
| dest 按月重放累加 vs 文件内 ref_year_2014 ysch | **22 / 22 MATCH** |
| dest 年一次风格 `ts_code` | `f557f72f…` = DIFFS dest；≠ ref `8309eca5…` |

**解释**：成品 2014 与 raw→transform 重放 **内容一致**；DIFFS 中的「全列失配」由 dest 哈希拼法与 `ref_build_year` 不一致造成。

## 4. 裁决

| 选项 | 是否 |
|---|---|
| **HASH_CALIBER_BUG** | **是（主结论）** |
| TRUE_CONTENT_MISMATCH | **否**（至少 2014 已证伪；系统图案 + 22/22 重放 MATCH 足以定口径；其余年 rows 齐且同图案，残留真差概率极低，修口径后复跑可一览） |
| 「口径 bug 为主 + 残留真差待复验」 | 不采用为并列主结论；修驱动后若仍有少数列/年差异再升真差 |

### 次要口径瑕疵（非本拍主因，修驱动时一并收）

1. dest 外层 dtype 取自 pandas round-trip **前**的 `tbl`，物理 dig 用 round-trip **后**的 `tbl2`——本次 dtype 碰巧一致，但属脆弱点。
2. `_row_group_physical_col_hashes` 已含 header，外层再喂 header → **双重 header**；ref/dest 两侧同构，不单独制造 286，但规范上应单一化（与设计 §4.2/D4 对齐时由 Eng 澄清）。
3. 设计语义「year_sorted_content」vs 实现「月流式累加」：在 A13 约束下以 **`ref_build_year` 为权威累加口径**；dest 对账侧必须 **同构**（按 `trade_date` 月切后累加），或抽共享 helper，禁止各写各的。

## 5. 另签 / 下游建议（给主）

1. **建议另签重跑票：是**——但 **先** Eng 修 §3.1 dest 侧（或抽 `year_sorted_content_col_hashes_from_table` 与 `ref_build_year` 同构），Arch **复审**命令清单/驱动钉，**再**由主另开新窗签发新 `.ok`。
2. **禁**复用已归档票 **`6de02e74`**；**禁**复用 enable **`4377eb59`**；**禁**盲 seed / allow_run / 物化 / 带病写 baseline。
3. 修法要点（Eng）：dest 年表排序去重后，按月 `groupby(month)` → 与 `ref_build_year` 相同的 header-once + monthly `_row_group_physical_col_hashes` 累加；外层 dtype 与物理 dig 同源；单测钉 2014：与现 `ref_year_2014.json` 22 列全 MATCH。
4. 复跑窗：错开叶25 16:15–17:45；A13 仍钉；A9 仍有效（不一致不写）。
5. **不**交 Data 定位真差（本拍已否决 TRUE_CONTENT_MISMATCH）；若修后复跑仍有非空 DIFFS，再开真差轨。

## 6. 禁区复述

不签新 `.ok`；不代跑；不 seed；不 allow_run；不改生产数据；不报 Leo；叶30 另线。live=false。

---
文档结束（Arch A18 §5.3 HASH_CALIBER_JUDGE）
