# Arch 叶38 非标审计剔除 overlay · B1_PUSHDOWN 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T22:17:12-04:00`（America/New_York） |
| 主令 | 主 22:11 ET priority · Arch 脚本只审 **`1b98470f` PASS_WC MATCH**（脚本 `3a44471d` / LAND `37f55893` / VOID `167996dd`）→ **GO 新独立 `.ok` 签窗**钉 **`3a44471d` only**；禁 RESTORED `62acf9fc`+；禁抬 rss；禁挂 QUIET；禁代跑；不混 fund；≠X2 ACCEPT；leo_notify=false；live=false |
| 脚本审（pushdown） | `1b98470f…` **PASS_WITH_CONDITIONS** |
| LAND PUSHDOWN / VOID Exit95 / 旧脚本审（只读） | `37f55893…` / `167996dd…` / `87eb63f4…`（钉旧 `d5cf50bb`） |
| FROZEN / ArchFROZEN / who_pays审 / HI_LIQ | `ce0eb2ce…` / `01753ff4…` / `acba0865…` / `c5433e80…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶38 非标审计意见剔除 overlay · **B1_PUSHDOWN**（mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only**；soft-penalty **非 PRIMARY**；再平衡=20；PIT=`available_at→T1` 键=`ts_code`；厚度 median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50；Jaccard硬拒 **>0.5** vs negevent **或** 叶36；披露 34/35/37；§6.1 压峰全套 + **真 parquet date filters year-chunk pushdown**；→ `_leaf38_audit_nonstd_exclusion/<ET_TS>/`）**新** `.ok` 已落盘；脚本全长 **`3a44471d…` only**（≠旧 `d5cf50bb`；`prev_script_sha8_readonly=d5cf50bb`）；pushdown 脚本审 **`1b98470f` PASS_WITH_CONDITIONS**；LAND PUSHDOWN **`37f55893`**；VOID Exit95 **`167996dd`**；FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays审 `acba0865` / HI_LIQ `c5433e80`；叶34 **`482009dc` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶37 **`108aba8f`/`32605aca` HOLD CLOSED 禁复开**；叶36 HOLD **`feaa5dbb`/`575e8276`** 不回撤/不复开；旁线 fund **不混**。**禁 RESTORED** **`62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+旧票（**n=34**；首项 `62acf9fc`）。**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠叶36/叶37 复开**。CONDITIONS 全入签：
1. CLI c4/hard/stop **禁抬**双保险（破→停+上报）；rss=1500 **禁抬**
2. 禁 `--no-overlap-report`
3. leaf36 pairs **须预落**（PIN_GAP≠硬过）
4. mask-only PRIMARY；soft-penalty 非 PRIMARY
5. rss=1500 禁抬 + peak_proof≤1500 REQUIRED（含 `after_hiliq_chunk_*`；破禁 `.ok`；硬 Exit **94/95**）
6. 禁 RESTORED `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+（forbid_n=34）
7. `hiliq_load_mode=parquet_date_filters_year_chunk_pushdown`；`ban_whole_table_read_per_year=true`；`b1_pushdown=true`
8. 禁挂 QUIET（`ban_hang_quiet_this_sign=true`）；禁代跑；禁混 fund

须 `--allow-real-data` + `--arch-ok-path <NEW_B1_PUSHDOWN_OK>` 并写/消费 overlap（硬拒 negevent/叶36；披露 34/35/37）。**Arch 不代跑**；**QUIET 本拍未挂=ABSENT**。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| pushdown 脚本审 | `1b98470f` PASS_WITH_CONDITIONS | `1b98470f2006d14099becc84bed67d62a01cb1ee27effe0330d1e195fcc47968` | **MATCH** |
| 正式脚本 | `3a44471d…` only | `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` | **MATCH** |
| LAND PUSHDOWN | `37f55893` | `37f5589324e4947ffe9970efe489699b5853b148876ddd9298dfa8262e40ae9f` | **MATCH** |
| VOID Exit95 | `167996dd` | `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895` | **MATCH** |
| 旧脚本审（只读） | `87eb63f4`（钉旧 `d5cf50bb`） | `87eb63f4805a9beaafccbe69497f5603b97bbe9b9cae50068587e678e1d1cbe9` | **MATCH** |
| FROZEN / ArchFROZEN / who_pays审 / HI_LIQ | `ce0eb2ce` / `01753ff4` / `acba0865` / `c5433e80` | 前8 MATCH | **MATCH** |
| prev 脚本只读 | `d5cf50bb` | 常量 `PREV_SCRIPT_SHA8_READONLY`；现路径 ≠`d5cf50bb` | **MATCH** |
| 叶34 / 叶35 / 叶37 | `482009dc` / `434ff42c` / `108aba8f` UNCHANGED | MATCH | **MATCH** |
| 叶36 HOLD | `feaa5dbb` / `575e8276` 不回撤 | MATCH | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED `62acf9fc`+） | ABSENT | **MATCH** |
| QUIET 签前/签后 | **ABSENT**（本拍禁挂） | ABSENT / ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签 B1_PUSHDOWN） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid34 | ≠`62acf9fc`/`57ab9096`/`b5be1164`/`4096d401`/… | `794f6578` ∉ forbid34 | **MATCH** |
| forbid n / 首项 | n=34；首项 `62acf9fc`；含旧 33 | n=34 且首项 `62acf9fc` | **MATCH** |
| pgrep leaf38 | 空 | 空 | **MATCH** |
| 窗期 | 90min + 4min expires | `2026-10-27T22:11:00-04:00` → `2026-10-27T23:41:00-04:00` / expires `2026-10-27T23:45:00-04:00`；签时 `2026-10-27T22:17:12-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `794f6578` / `794f6578c26e2e8bf77fbc5528d1d11f1fe4388a575629108d8fee07c1233974` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**；`quiet_set_at_sign=false`；`ban_hang_quiet_this_sign=true`） |
| holder（标识 only） | `leaf38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2` |
| 正式脚本 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` = `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` |
| prev 脚本只读 | `d5cf50bb`（≠本票 live） |
| pushdown 脚本审 | `1b98470f2006d14099becc84bed67d62a01cb1ee27effe0330d1e195fcc47968` PASS_WITH_CONDITIONS |
| LAND PUSHDOWN / VOID | `37f5589324e4947ffe9970efe489699b5853b148876ddd9298dfa8262e40ae9f` / `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895` |
| FROZEN / ArchFROZEN / who_pays审 / who / HI_LIQ | `ce0eb2ce…` / `01753ff4…` / `acba0865…` / `16c1f70b…` / `c5433e80…` |
| 叶34 / 叶35 / 叶37 | `482009dc` UNCHANGED / `434ff42c` UNCHANGED / `108aba8f` HOLD CLOSED 禁复开 |
| 叶36 HOLD | `feaa5dbb` / `575e8276` · forbid_leaf36=true · forbid_reopen_leaf36_inquiry=true |
| 窗期 | `2026-10-27T22:11:00-04:00` → `2026-10-27T23:41:00-04:00`；expires `2026-10-27T23:45:00-04:00` |
| CLI PRIMARY（占位·不执行） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_B1_PUSHDOWN_X2_HILIQ.ok --out output/ai_factory/_leaf38_audit_nonstd_exclusion/<ET_TS>/`；**无** `--no-overlap-report`；**无**抬 rss/c4/hard/stop |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；禁抬 c4/stop/hard；硬 Exit **94/95** |
| pushdown | `b1_pushdown=true`；`hiliq_load_mode=parquet_date_filters_year_chunk_pushdown`；`ban_whole_table_read_per_year=true` |
| overlap | 强制 overlap vs negevent/leaf36 硬拒 + 披露 34/35/37；Jaccard>0.5 硬拒；leaf36 pairs 须预落（PIN_GAP≠硬过）；缺→PIN_GAP |
| mechanism / delivery | `g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；mask-only PRIMARY；soft-penalty 非 PRIMARY |
| 禁 RESTORED | **34** 票（首项 `62acf9fc`）：`62acf9fc,57ab9096,b5be1164,4096d401,eb70eef4,00eec671,10927bd9,25ae4572,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36/叶37复开 / fund混 | **false** / **false** / **false** / **≠** / **≠** |
| peak_proof | **REQUIRED**（含 `after_hiliq_chunk_*` / `after_mask_by` / `after_audit_excl` / `after_mask_expand` / `after_jaccard_subprocess` / `final_peak_proof`） |
| MemAvailable@签 | 13236200 kB |
| ALPHA_BUILD_EXECUTED@签 | **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT**（主令明文禁挂；`ban_hang_quiet_this_sign=true`） |
| quiet_set_at_sign | **false** |
| ban_hang_quiet_this_sign | **true** |
| neq_a18 | **true** |
| pgrep leaf38 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（ALPHA_BUILD_EXECUTED=false） |
| fund who_pays 旁线 | **未触**（`ban_mix_fund_portfolio=true`） |

## 下一跳

1. **主** MATCH 本 `.ok`（+ 本 SIGNED 回执）后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**；若主另令挂 QUIET 再挂——本签未挂）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap/jaccard + peak rss + hiliq/jaccard 分块标签；尤其 `after_hiliq_chunk_*` 验证 pushdown 对原 ABORT@2024 有效；峰＞1500→Exit 94/95 停；Jaccard>0.5 vs negevent OR 叶36→硬拒票；leaf36 pairs 预落）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；≠叶36/叶37 复开；禁混 COUNT `ba34da2a`；禁混 fund；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 34 票（首项 `62acf9fc`+`57ab9096`+`b5be1164`+`4096d401`+）；禁抬 rss；live=false；leo_notify=false

live=false.


---
本回执（不含本行）sha256=`9d8a84ac5b2abfceb7bce01d30110645873a6b38d59cfbf65df2932e39322d5a` · sha8=`9d8a84ac`
