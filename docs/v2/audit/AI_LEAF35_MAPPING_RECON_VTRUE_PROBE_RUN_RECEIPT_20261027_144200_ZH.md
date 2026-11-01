# AI 回执：叶35 Mapping Recon VTRUE 只读探针 · DONE（rc=0）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 14:44:26 EDT**（America/New_York） |
| **结论** | **DONE**（`executed_probe=true`；`ok=true`；**rc=0**；无 Exit 94/95；无 Traceback；仅 diag JSON/tsv；**禁写 alpha/mask/overlap 已遵守**） |
| ET_TS | `20261027_144200` |
| run_pid | `517908`（已退出；nice=10；pgrep 现空） |
| **rc** | **0** |
| status | **EXECUTED_PROBE_DONE** |
| EXECUTED_PROBE | **true** |
| 探针 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_MAPPING_RECON_PROBE_VTRUE_DRAFT_20261027.py` sha8 **`2c2226e0`**（现核 MATCH；**未改**） |
| 正式脚本 | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572` UNCHANGED**（现核 MATCH；**未改**） |
| 骨架 | sha8 **`c2f2ca94` UNCHANGED** |
| 叶33 | sha8 **`afbbe7e7` UNCHANGED** |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_MAPPING_RECON_VTRUE_PROBE.ok` sha8 **`00eec671`**（现核 MATCH；**仍在位**；未自签/未删；交 Arch CONSUME；∉forbid；≠RESTORED `10927bd9`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`bf3470cb`**（现核 MATCH；holder=`leaf35_MAPPING_RECON_VTRUE_PROBE`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`97a84fa7`**（钉） |
| Arch 审探针 | sha8 **`bbbf809b` PASS_WITH_CONDITIONS**（钉） |
| recon 只审 | sha8 **`cb3ca975`**（钉） |
| PIN C3 | sha8 **`dd17044a`**（钉） |
| VOID | sha8 **`dfafff28`**（钉；void_ok=`10927bd9`） |
| RUNNING_ACK | sha8 **`6dbe12d3`** |
| out | `output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/` |
| log | `output/ai_factory/_leaf35_mapping_recon_vtrue/20261027_144200/stdout.log` + `stderr.log` + `/tmp/quantlab_leaf35_mapping_recon_vtrue_20261027_144200.log` |
| samp | `/tmp/quantlab_leaf35_mapping_recon_vtrue_20261027_144200_peak_sampler.tsv`（前缀 `/tmp/quantlab_leaf35_mapping_recon_vtrue_*`） |
| CLI | approved_cmd **exact**（`--universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path … --out …`；外加 `nice -n 10`）；**无** `--force`；rss=1500 **禁抬且未抬** |
| expires | 窗→16:07 / expires **16:11 ET**（启动≈14:42:25 ET；STOP≈14:42:28 ET；未逾窗） |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / 叶36 / Book-Smoke / selfcheck / 正式 α；**勿复跑 / 勿改门 / 勿改脚本**（本拍已遵守） |

## 1. peak_proof 摘要（REQUIRED；PRESENT）

| 源 | 值 |
|---|---|
| log 全局 max peak_kb | **512264**（含 `after_daily_concat`） |
| payload `peak_kb` | **512264** |
| sampler max VmHWM | **512824** |
| soft / hard | soft=1536000 hard=1536000（rss_limit_mb=**1500 未抬**） |
| STAGE 序列 | n=**37**（`vtrue_probe_start`→`after_import_formal`→30×`after_pressure_rebal_*`→`after_daily_concat`） |
| 相对硬帽 | max_peak **512264** / 1536000 ≈ **33.4%**；**无 Exit 94/95** |
| ABORT_PEAK | **无** |

## 2. 诊断主结论（照实；Option A）

- **n_rebal=30**；**n_mapped=0** 全日；**n_pressure_nonnull=0**；**n_hiliq_intersect=0**
- **空压原因分布**：`share_avail_late` × **30**（100%）
- **主因 A（份额 PIT / available_at）**：每个 rebal 日 `n_share_rows=3`（trade_date==rebal 有行），但 **`n_share_rows_avail_le_tts=0`**（全部 `available_at_clock > t_ts(15:00 Asia/Shanghai)`）→ 正式口径过滤后份额为空 → 无法映射压力
- **对照 COUNT 未滤 available_at**：`n_share_rows_count_approx_style=3`（与同日行数一致；说明问题不在 trade_date 缺行，而在 available_at 时钟）
- **对照 PIN §1.3 avail-only（不钉 trade_date）**：`n_share_rows_pin13_avail_only` 约 **4695–6405**（有可用份额，但不满足「当日 trade_date ∧ avail≤15:00」双条件）
- **主因 B（权重方案 A）**：**非主因**——全日 `n_weight_rows_schemeA=1800`（稳定非空；scheme A / PIN `dd17044a` 映射正常）
- **HI_LIQ**：`n_hiliq_members` 约 **1480–3833**；因 mapped=0 → intersect=0（连带，非独立根因）
- detail 统一：`same-day share rows exist but all available_at_clock > t_ts(15:00)`
- **解释 X2 STOP_ZERO_MASK_ROWS**：与本探针一致——正式路径因份额 available_at 过晚导致 30× rebal press empty/unmappable

## 3. per-rebal 摘要表

| rebal_date | n_share | avail≤tts | count≈ | pin13_avail | weightA | mapped | press | hiliq∩ | empty_reason |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2024-06-03 | 3 | 0 | 3 | 4695 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-07-02 | 3 | 0 | 3 | 4752 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-07-30 | 3 | 0 | 3 | 4815 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-08-27 | 3 | 0 | 3 | 4875 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-09-26 | 3 | 0 | 3 | 4935 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-10-31 | 3 | 0 | 3 | 4995 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-11-28 | 3 | 0 | 3 | 5055 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2024-12-26 | 3 | 0 | 3 | 5115 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-01-24 | 3 | 0 | 3 | 5175 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-03-03 | 3 | 0 | 3 | 5238 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-03-31 | 3 | 0 | 3 | 5298 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-04-29 | 3 | 0 | 3 | 5355 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-05-30 | 3 | 0 | 3 | 5415 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-06-30 | 3 | 0 | 3 | 5478 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-07-28 | 3 | 0 | 3 | 5538 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-08-25 | 3 | 0 | 3 | 5598 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-09-22 | 3 | 0 | 3 | 5658 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-10-28 | 3 | 0 | 3 | 5712 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-11-25 | 3 | 0 | 3 | 5775 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2025-12-23 | 3 | 0 | 3 | 5835 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-01-22 | 3 | 0 | 3 | 5892 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-02-27 | 3 | 0 | 3 | 5955 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-03-27 | 3 | 0 | 3 | 6015 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-04-27 | 3 | 0 | 3 | 6078 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-05-28 | 3 | 0 | 3 | 6135 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-06-26 | 3 | 0 | 3 | 6198 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-07-24 | 3 | 0 | 3 | 6258 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-08-21 | 3 | 0 | 3 | 6318 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-09-18 | 3 | 0 | 3 | 6378 | 1800 | 0 | 0 | 0 | `share_avail_late` |
| 2026-10-09 | 3 | 0 | 3 | 6405 | 1800 | 0 | 0 | 0 | `share_avail_late` |

## 4. 产物（仅 diag）

| 文件 | sha8 | 状态 |
|---|---|---|
| `mapping_recon_vtrue_per_rebal.json` | **`446b60d1`** | 有；n_rebal=30；executed_probe=true |
| `mapping_recon_vtrue_per_rebal.tsv` | **`f1ef19ca`** | 有 |
| alpha / mask / overlap / exclusion parquet | — | **无**（禁写已遵守） |
| run_meta / alpha parquet | — | **无** |

## 5. 门控与硬禁复核（跑后）

- `.ok` 仍 **`00eec671`** 在位（**未删**；交 Arch CONSUME）
- QUIET 仍 **`bf3470cb`**；holder=`leaf35_MAPPING_RECON_VTRUE_PROBE`；**未擅 lift**
- 探针仍 **`2c2226e0`**；正式仍 **`25ae4572`**；骨架 **`c2f2ca94`**；叶33 **`afbbe7e7`**
- forbid RESTORED 未触（本票仅新 `.ok` `00eec671`；禁 `10927bd9`+旧票）
- rss=1500 未抬；peak_proof 以 log RSS_CHECK + sampler + payload.peak_kb 为证
- **≠X2 ACCEPT**；**≠叶36**；leo_notify=false；live=false
- 禁 Book-Smoke / 禁复跑 X2 / 禁改正式脚本 / 禁改 TEAM_STATE / 禁 git commit：本拍已遵守

## 6. 交主

交主 → Arch CONSUME（`.ok` **`00eec671`** 仍保留；QUIET **`bf3470cb`** 未擅 lift）。本执行器 **不**复跑、**不**改门、**不**改脚本、**不**自签 `.ok`、**不** lift QUIET。
