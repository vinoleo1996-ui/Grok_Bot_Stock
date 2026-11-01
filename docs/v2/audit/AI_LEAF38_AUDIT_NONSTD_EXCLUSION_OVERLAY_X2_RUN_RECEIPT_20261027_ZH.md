# AI · 叶38 audit_nonstd_exclusion_overlay · B1_PUSHDOWN X2 RUN_RECEIPT · 2026-10-27

- status: **DONE**（rc=0；peak_proof≤1500；mask-only PRIMARY；≠X2 ACCEPT）
- rc: **0**
- ET_TS / OUT: `20261027_222656` → `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/`
- run_subdir: `20261027_222658`
- wall_et_start: 2026-10-27 22:26:57 EDT
- wall_et_done: 2026-10-27 22:28:38 EDT
- leo_notify: **false**；live: **false**；promotion: **false**；≠X2 ACCEPT；book_smoke: false
- QUIET: **ABSENT**（本签禁挂；未挂；收尾仍 ABSENT）
- web_exempt: **false**（prelaunch pgrep 空）
- b1_pushdown: **true**；hiliq_load_mode=`parquet_date_filters_year_chunk_pushdown`

## MATCH pins（开跑前复算 + 跑后仍 MATCH）

| pin | sha8 | 注 | 状态 |
|---|---|---|---|
| `.ok` | `794f6578` | `ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok`；valid_to=23:41 / expires=23:45 ET；rss=1500；forbid 首项 `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+ | MATCH |
| SIGNED | `e6e30511` | `ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_OK_SIGNED_20261027_ZH.md` | MATCH |
| 脚本 | `3a44471d` | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` **only**（≠旧 `d5cf50bb`）；**未改** | MATCH |
| Arch pushdown 审 | `1b98470f` | PASS_WITH_CONDITIONS | MATCH |
| LAND PUSHDOWN | `37f55893` | | MATCH |
| VOID Exit95 | `167996dd` | 旧窗 ABORT（只读） | MATCH |
| leaf36 count JSON | `575e8276` | 预落对齐量级 | MATCH |
| RESTORED forbid | `62acf9fc`+… | 未复用；未 RESTORED | 遵守 |

dry-compile-only：exit0；script_sha8=`3a44471d`；primary_delivery=`mask_only`；rss_limit_mb=`1500`；b1_pushdown=true。

## approved_cmd（精确；未抬帽；未 --no-overlap-report；未 FULLA）

正式成功窗用**绝对** `--out`（与签文相对路径同指；修 pathlib `relative_to(ROOT)`；**未改脚本 / 未抬 rss/c4/stop/hard**）：

```
PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok --out /workspace/QuantLab/output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/
```

（attempt1 `20261027_222556` 用相对 `--out`：全链路 peak≤1500 已过、jaccard/mask 已落，收尾 `mask_out.relative_to(ROOT)` ValueError → rc≠0；**未抬帽**；同窗绝对路径重跑成功。attempt1 peak≈969.7 / abort_stage=None / post_compute_path_bug。）

## Prelaunch

1. QUIET `output/loop/RESEARCH_QUIET.lock` **ABSENT**
2. `pgrep -af 'kline.py|export_static.py|snapshot.py|gen.py'` **empty**
3. MemAvailable ≈13.2Gi ≥ soft 2621440 kb
4. dry-compile-only exit0 + pins 如上
5. 脚本未改；未混 fund；未自签；未挂 QUIET；未 RESTORED

## leaf36 pairs 预落证明

- 源：只读复用 `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` 的 filter_primary+build_exclusion（WIN=20；HI_LIQ×X2）；**未**复开叶36 who_pays/X2
- staging：`/tmp/quantlab_leaf38_preland/leaf36_date_tscode_pairs.jsonl` sha8 **`1913e011`**
- staging_meta sha8 **`624afd47`**：n_pairs=**5745**；n_windows_applied_hiliq=**345**（对齐 count JSON `575e8276`）；n_unique_instruments=208；n_unique_dates=570；preland peak≈1276MB（独立进程已退出）
- watcher：`/tmp/quantlab_leaf38_preland/watcher.py` → LAND `leaf36_pairs.npy` sha8 **`72ab602b`**（n_landed=5745；miss=0；source=`prelanded_leaf36_pairs.npy`）
- **非 PIN_GAP 静默过闸**：jaccard worker 消费预落 npy；hard_reject_jaccard=**false**

## 跑果

- universe=**HILIQ**；window=**x2**；x2-end=**20261009**；PRIMARY=**mask_only**
- rss_limit_mb=**1500**（**未抬**；c4/stop/hard 未抬）
- rc=**0**；`STAGE run_build_done`
- peak_rss_mb=**967.67578125**；peak_proof_le_1500=**true**
- thickness：median=**48.0**；frac_ge10=**1.0**；zero_frac=**0.0**；pass_thickness=**true**
- Jaccard hard（negevent / leaf36）：max=**0.0** / **0.0649…**；hard_reject=**false**
- disclose 34/35/37：max≈0.0177 / 0.0088 / 0.0546（披露 only；非硬拒）
- 禁项：未 `--no-overlap-report`；未抬帽；未改脚本；未 Book-Smoke；未自签 `.ok`；未挂 QUIET；未混 fund；未 git commit；未把 KEEP/收益当 ACCEPT

## peak_proof 全序列（REQUIRED；含 after_hiliq_chunk_*）

soft=1536000 / split=1131520 / c4=1331200 / hard=1536000

```
STAGE run_build_begin ru_maxrss=114900
STAGE load_hiliq_begin ru_maxrss=114900
STAGE load_hiliq_done ru_maxrss=455240
STAGE audit_excl_begin ru_maxrss=455240
STAGE audit_excl_done ru_maxrss=476032
STAGE run_build_done ru_maxrss=990900
RSS_CHECK after_hiliq_chunk_2024 peak_kb=234484 vmrss_kb=219256 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=229.0
RSS_CHECK after_hiliq_chunk_2025 peak_kb=363596 vmrss_kb=317464 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=355.1
RSS_CHECK after_hiliq_chunk_2026 peak_kb=363596 vmrss_kb=323800 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=355.1
RSS_CHECK after_mask_by peak_kb=455240 vmrss_kb=442148 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=444.6
RSS_CHECK after_calendar peak_kb=455240 vmrss_kb=444300 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=444.6
RSS_CHECK after_audit_excl peak_kb=476032 vmrss_kb=469412 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=464.9
RSS_CHECK after_pair_land peak_kb=615016 vmrss_kb=574196 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=600.6
RSS_CHECK after_mask_expand peak_kb=990900 vmrss_kb=563184 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=967.7
RSS_CHECK after_disclose_leaf34 peak_kb=990900 … peak_rss_mb=967.7
RSS_CHECK after_disclose_leaf35 peak_kb=990900 … peak_rss_mb=967.7
RSS_CHECK after_disclose_overlap peak_kb=990900 … peak_rss_mb=967.7
RSS_CHECK after_free_before_jaccard_subprocess peak_kb=990900 … peak_rss_mb=967.7
RSS_CHECK after_jaccard_subprocess peak_kb=990900 … peak_rss_mb=967.7
RSS_CHECK final_peak_proof peak_kb=990900 vmrss_kb=595276 soft=1536000 split=1131520 c4=1331200 hard=1536000 peak_rss_mb=967.7
```

（pushdown 有效：after_hiliq_chunk_2024 ≈229MB ≪ 旧窗 Exit95@1604MB。）

## 产物路径

| 产物 | 路径 | sha8 |
|---|---|---|
| exclusion_mask | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/20261027_222658/exclusion_mask_HILIQ_x2_20261027_222658.parquet` | `1d3d0d88` |
| run_meta | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/20261027_222658/run_meta_20261027_222658.json` | `81068e47` |
| overlap disclose | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/20261027_222658/overlap_vs_negevent_leaf36_hard_34_35_37_disclose.json` | `7d224a42` |
| jaccard_worker | `/tmp/quantlab_leaf38_audit_nonstd_run_20261027_222658/jaccard_worker.json` | `0c118d20` |
| leaf36_pairs.npy | `/tmp/quantlab_leaf38_audit_nonstd_run_20261027_222658/pairs/leaf36_pairs.npy` | `72ab602b` |
| staging jsonl | `/tmp/quantlab_leaf38_preland/leaf36_date_tscode_pairs.jsonl` | `1913e011` |
| peak_proof_sequence | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/peak_proof_sequence.txt` | — |
| attempt1（相对 out 收尾崩） | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222556/` | 旁证；非正式 |

## COND 遵守

| COND | 结果 |
|---|---|
| rss=1500 禁抬 | **遵守** |
| peak_proof≤1500 REQUIRED（含 after_hiliq_chunk_*） | **PASS**（967.7） |
| leaf36 pairs 须预落；PIN_GAP≠硬过 | staging+watcher+npy 落地；source=prelanded |
| 禁 no-overlap-report | 遵守（硬拒 negevent/leaf36；披露 34/35/37） |
| mask-only PRIMARY | 遵守 |
| 禁 RESTORED / 禁混 COUNT ba34da2a / 禁混 fund / 禁复开叶36/37 | 遵守 |
| ban_hang_quiet_this_sign | QUIET 始终 ABSENT |
| ≠X2 ACCEPT | **遵守**（run_meta.x2_accept=false） |

## 下一跳

**交主 → Arch CONSUME**（本拍 DONE；peak_proof PASS；≠X2 ACCEPT）。旁线 fund FROZEN/BS **不混**。

- receipt_written_et: 2026-10-27 22:28:38 EDT
