# 【PUSHDOWN LAND 回执 2026-10-27】叶38：HI_LIQ 真 parquet 按年 pushdown

- **时点**：2026-10-27 22:00:46 America/New_York (ET)
- **主裁**：双线 GO · 叶38 真 pushdown/按年读表（Arch VOID `167996dd` 后）
- **本拍角色**：AI 执行器落 **B1_PUSHDOWN 正式脚本 + LAND RECEIPT**；**未**真跑 X2；**未**自签 `.ok`；**未**挂 QUIET；**未** Book-Smoke；**未** git commit；**未**抬 rss；**未**混 fund
- **leo_notify**=false；**live**=false；**promotion**=false；**ok_requested**=false；**EXECUTED**=**false**
- **≠** X2 ACCEPT；禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+

---

## 1. 交付物

| # | 路径 | sha8 | 说明 |
|---|---|---|---|
| 1 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` | **`3a44471d`** | B1_PUSHDOWN 正式脚本（覆盖同路径；新 sha ≠ prev `d5cf50bb`） |
| 2 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PUSHDOWN_LAND_RECEIPT_20261027_ZH.md` | （本文件；落盘后以磁盘 sha8 为准） | 本回执 |
| 3 | `/tmp/leaf38_audit_nonstd_exclusion_overlay_alpha_build.pyc` | n/a | `py_compile` 产物（size=67847） |

**脚本全长 sha256**：`3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027`

**prev 只读对照**：`d5cf50bb`（`d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263`）— 年循环整表 `pq.read_table` 再滤；**保留只读**；本票主脚本 ≠ prev。

---

## 2. 钉 MATCH

| 项 | 期望 sha8 | 盘上 sha8 | 结果 |
|---|---|---|---|
| Arch VOID Exit95 | `167996dd` | `167996dd` | **MATCH** |
| prev 脚本（只读） | `d5cf50bb` | `d5cf50bb` | **MATCH**（未改回） |
| 本票新脚本 | （新） | `3a44471d` | **NEW ≠ d5cf50bb** |
| HI_LIQ mask | `c5433e80` | `c5433e80` | **MATCH** |
| FROZEN | `ce0eb2ce` | （未改） | 钉不变 |
| VOIDED `.ok` | `62acf9fc` | 已入 `FORBID_OK_SHA8` | **禁 RESTORED** |

VOID 路径：`docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_VOID_ABORT_EXIT95_20261027_ZH.md`  
全长 `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895`

---

## 3. Pushdown 实现要点（根因对治）

**根因（VOID `167996dd`）**：`_load_hiliq_mask_by_chunks` 年循环仍 `pq.read_table(mask_path, columns=cols)` **无 filters** → 首年 2024 即整表入 RSS → peak≈1604 MiB ≥ hard 1500 → Exit **95**。

**本拍修复（B1_PUSHDOWN）**：

1. 每年算 `y_start`/`y_end`，与 X2 `lo`/`hi` 相交得 `d_lo`/`d_hi`；空交则 skip + 仍打 `rss_cb(after_hiliq_chunk_YYYY)`。
2. `filters=[(date,'>=',d_lo),(date,'<=',d_hi)]`；若 schema 有 `in_universe` 再追加 `('in_universe','==',True)`（pyarrow bool filter 已核可用）。
3. 列剪枝只读 `date` / `instrument` / `in_universe`；读完 `del t` + `gc.collect()`；pandas 侧再 normalize + 防御性 univ/窗/年滤。
4. **禁止**每年无 filters 的整表 `pq.read_table(mask_path)`。
5. `rss_cb('after_hiliq_chunk_YYYY')` / `after_mask_by` 保留；rss 默认 **1500** / c4=`1331200` / hard=`1536000` / Exit 94·95 **未抬**。
6. 其余 §6.1（分进程 Jaccard、leaf36 预落、禁 no-overlap-report 默认、mask-only PRIMARY、禁 RESTORED）保持。

文首钉：`B1_PUSHDOWN` / `prev=d5cf50bb` / `VOID=167996dd` / 禁 RESTORED `62acf9fc`+…  
常量：`PREV_SCRIPT_SHA8_READONLY` / `ARCH_VOID_EXIT95_SHA8` / `VOIDED_OK_SHA8`；`FORBID_OK_SHA8` 首项加 `62acf9fc`。

---

## 4. 可选轻量只读证明（禁真跑 X2）

对 HI_LIQ mask `c5433e80`、切片 **2024-06-03→2024-12-31**（X2∩2024）：

| 项 | pushdown（filters） | 旧整表再滤 |
|---|---|---|
| 行数 | **331034** | **331034** |
| arrow nbytes | 8441386 | 296651721 |
| nbytes 比（整/推） | — | **35.14×** |
| 整表 raw 行 | — | 11748583 |
| row_count_match | **true** | |

另：函数冒烟 `_load_hiliq_mask_by_chunks("2024-06-03","2024-12-31")` → ndays=144；peak_kb≈241496（≈235.8 MiB）≪1500；**非** `--allow-real-data` 全窗 X2；无 audit/Jaccard/mask 写出。

旁证 JSON（/tmp，非正式产物）：`/tmp/leaf38_pushdown_2024_proof.json`

---

## 5. 静态门（本拍）

| 检查 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf38_audit_nonstd_exclusion_overlay_alpha_build.pyc` | **PASS**（size=67847） |
| `--dry-compile-only` | **exit 0**；`script_sha8=3a44471d`；`rss_limit_mb=1500`；`b1_pushdown=true`；`primary_delivery=mask_only`；`executed=false`；`hiliq_load_mode=parquet_date_filters_year_chunk_pushdown`；ZERO 大表加载 |
| 默认帽 | rss=**1500** / hard=**1536000** / c4=**1331200** / stop=**1484800** — **未抬** |
| 真跑 X2 / `--allow-real-data` 全窗 | **未做** |
| 自签 `.ok` / 挂 QUIET | **未做** |
| 混 fund / Book-Smoke / git commit | **未做** |

---

## 6. 禁项再钉（已遵守）

- 禁抬 rss=1500；禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+
- 禁本拍真跑 X2；禁自签 `.ok`；禁挂 QUIET
- 禁混 fund；禁 git commit；禁 Book-Smoke；≠X2 ACCEPT
- 禁把 prev `d5cf50bb` 当本票主脚本；禁把 COUNT `ba34da2a` 当正式构建

---

## 7. 下一跳

**交主 → Arch 只审本脚本**（sha8 **`3a44471d`** / 全长 `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` + 本 RECEIPT）。  
**禁** AI 自签 `.ok`；**禁**未新独立 `.ok` 开 X2；**禁**抬帽。  
通过后由主令新 LAND/签新独立 `.ok` 再开跑。fund 旁线不混。

---

## 8. 非动作

- 未真跑 X2；未自签 `.ok`；未挂 QUIET；未抬 rss；未 RESTORED；未改 FROZEN；未混 fund；未报 Leo；live=false；EXECUTED=false
