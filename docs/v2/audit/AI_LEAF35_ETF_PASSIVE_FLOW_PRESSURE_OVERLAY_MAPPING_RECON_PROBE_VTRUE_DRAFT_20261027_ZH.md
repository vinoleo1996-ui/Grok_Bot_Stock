# 叶35 ETF 被动压力 overlay · **mapping recon 真值只读探针版 DRAFT**（Option A · 非叶36）

- **角色**：QuantLab AI 后台执行器
- **时刻**：2026-10-27 14:22 ET（America/New_York）；ISO `2026-10-27T14:22:19-04:00`
- **票种**：**诊断票 · 真值探针实现 DRAFT** · **≠叶36** · **≠X2 ACCEPT** · **≠Book-Smoke** · **≠selfcheck**
- **主裁**：Option **A**（Arch recon 只审 **PASS_WITH_CONDITIONS `cb3ca975` MATCH**）
- **状态**：**可审真值版已落** · **EXECUTED_PROBE=false** · **本拍未** `--allow-real-data` 真跑 · **未**申 `.ok` · **未**挂 QUIET · **未**改正式脚本
- **正式脚本钉**：`research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`** **UNCHANGED**
- **骨架探针钉**：`…_MAPPING_RECON_PROBE_DRAFT_20261027.py` sha8 **`c2f2ca94`** **UNCHANGED**（另写本真值版；不覆盖骨架）
- **叶33**：`afbbe7e7` **UNCHANGED**

## 0. 上游钉（MATCH）

| 项 | sha8 |
|---|---|
| Arch recon 只审 | **`cb3ca975`** PASS_WITH_CONDITIONS |
| recon DRAFT / COVER / RECEIPT | **`350ed22b`** / **`26def8fb`** / **`fb0c7a4b`** |
| 骨架探针 / recon JSON | **`c2f2ca94`** / **`ad4b47a2`** |
| VOID / ok VOID / QUIET lift | **`dfafff28`** / **`10927bd9`** / **`f50975e4`** |
| PIN C3 / COUNT JSON / COUNT script | **`dd17044a`** / **`a17b75fb`** / **`4e964d40`** |
| 正式脚本 / 叶33 | **`25ae4572`** / **`afbbe7e7`** |

## 1. 本交付（真值探针版）

| 文件 | 角色 |
|---|---|
| `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py` | **真值只读探针 py**（实现可 `--allow-real-data`；本拍未真跑） |
| `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027_ZH.md` | 本说明/对照 |
| `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_COVER_DRAFT_20261027_ZH.md` | COVER |
| `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_CMD_DRAFT_20261027_ZH.md` | 拟真跑 CMD（本拍不执行） |
| `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_RECEIPT_20261027_ZH.md` | RECEIPT |
| `output/ai_factory/leaf35_etf_passive_flow_pressure_mapping_recon_vtrue_pending_20261027.json` | 占位 JSON（`executed_probe=false`） |

探针 py sha8（落盘核）= **`2c2226e0`**（全长见 RECEIPT）。

## 2. CLI / 门

| 调用 | 期望 |
|---|---|
| `--dry-compile-only` | **PASS** rc=0；ZERO 大表；`executed_probe=false`；钉 formal=`25ae4572` / skeleton=`c2f2ca94` |
| 无 `--allow-real-data`（且非 dry） | **STOP** rc=3 |
| `--allow-real-data` 无合法现存 `.ok` | **STOP**（缺文件 rc=4 / forbid sha8 rc=5） |
| `--allow-real-data --arch-ok-path <NEW_OK> --out <diag>` | 真跑 per-rebal 诊断（**须** Arch 只审本版 + 主签**新**只读探针窗；**禁** RESTORED `10927bd9`） |

硬禁：`--force`→STOP；抬 `rss>1500`→STOP；禁写 alpha/mask/overlap；禁改 `25ae4572`。

## 3. 真值对照列（Arch C2 钉齐）

**钉列**：`rebal_date,n_share_rows,n_share_rows_avail_le_tts,n_weight_rows_schemeA,n_mapped,n_pressure_nonnull,n_hiliq_intersect,empty_reason`

**附加（不替换钉列）**：`n_share_rows_pin13_avail_only,n_share_rows_count_approx_style,empty_reason_detail`

### A 份额 PIT（主）

| 口径 | 计数 |
|---|---|
| 正式（A） | `n_share_rows` = `trade_date==rebal`；`n_share_rows_avail_le_tts` = 再 `available_at_clock≤t_ts(15:00 Asia/Shanghai)`（import 正式 `_load_etf_flows_window` / `_pressure_on_day` 只读） |
| COUNT APPROX | `n_share_rows_count_approx_style` ≈ 同日行、**未**滤 `available_at`（对照 `a17b75fb` / `4e964d40`） |
| PIN §1.3 | `n_share_rows_pin13_avail_only` = **仅** `available_at≤t_ts`（**未**要求 `trade_date==rebal`）— 量化与实现张力 |

### B 方案 A（次）

`n_weight_rows_schemeA`：月末点→次月首个交易日 09:00 Asia/Shanghai=`weight_available_at`；`weight_available_at≤t_ts` 下三指数 asof 成分行数之和（正式 `_load_weight_pin_scheme_a` / `_asof_weight_scheme_a`）。

### empty_reason 枚举

`share_pit_empty_dual_filter|share_avail_late|share_trade_date_empty|weight_schemeA_empty|map_fail|hiliq_intersect_empty|pressure_all_null|ok|PIN_GAP_needs_ok_window`

窗：HILIQ×x2→20261009；rebal every 20；rss=1500 禁抬；peak_proof STAGE/`RSS_CHECK`；out 仅 diag JSON/tsv。

## 4. 本拍质量门（已核）

| 项 | 结果 |
|---|---|
| `py_compile` → `/tmp/leaf35_mapping_recon_probe_vtrue_draft_20261027.pyc` | **PASS** |
| `pyflakes` | **PASS**（0 findings） |
| `--dry-compile-only` | **PASS** rc=0；`executed_probe=false`；formal=`25ae4572`；skel=`c2f2ca94` |
| 无 `--allow-real-data` | **STOP** rc=3 |
| `--allow-real-data` 无合法 `.ok` | **STOP** rc=4（缺文件）/ rc=5（`10927bd9` forbid） |
| 正式 / 骨架 / 叶33 | **`25ae4572` / `c2f2ca94` / `afbbe7e7` UNCHANGED** |
| live `.ok` / QUIET | **0 / ABSENT** |
| EXECUTED_PROBE | **false** |

## 5. 禁项（本拍）

- **禁**改正式脚本 **`25ae4572`**；**禁**改骨架 **`c2f2ca94`**；**禁**碰叶33 **`afbbe7e7`**
- **禁**复跑 X2；**禁**自签 `.ok`；**禁**挂 QUIET；**禁** Book-Smoke
- **禁** RESTORED `10927bd9`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票（`02426b73`…`6de02e74`）
- **禁**本拍 `--allow-real-data` 真执行；**禁**写 alpha/mask/overlap；**禁**开叶36
- **≠X2 ACCEPT**；leo_notify=false；live=false

## 6. 推荐下一跳

```
本真值探针版 DRAFT（EXECUTED_PROBE=false）
  → Arch 只审本版（列钉 / CLI 门 / 禁改 25ae4572 / 禁 RESTORED 10927bd9）
    → 主签**新**只读探针 .ok（禁 RESTORED）
      → AI 持新 .ok 真跑 per-rebal JSON/tsv
        → 主裁是否开 Option B 补丁 DRAFT（对照 PIN §1.3）
```

**交主→Arch 只审。** 本执行器不自签、不真跑、不改 `25ae4572`。
