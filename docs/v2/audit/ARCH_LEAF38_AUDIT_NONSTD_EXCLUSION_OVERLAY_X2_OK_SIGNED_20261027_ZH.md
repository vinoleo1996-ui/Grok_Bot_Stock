# Arch 叶38 非标审计剔除 overlay · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T21:23:44-04:00`（America/New_York） |
| 主令 | 主 ~21:19 ET priority · 叶38 脚本审票 `87eb63f4` PASS_WITH_CONDITIONS 认 → 开独立 X2 **只签** `.ok` 窗（钉脚本 `d5cf50bb` only；**禁**混 COUNT `ba34da2a`；**禁**混 fund；**禁**复开叶37；**禁挂 QUIET**；≠X2 ACCEPT） |
| 脚本审 | `87eb63f4…` **PASS_WITH_CONDITIONS** |
| FROZEN / ArchFROZEN / who_pays审 / LAND / who | `ce0eb2ce…` / `01753ff4…` / `acba0865…` / `d157429b…` / `16c1f70b…` |
| COVER / COUNT盘 / COUNT脚本（非正式） / JSON / dig / HI_LIQ | `7c3b8691…` / `e82aefa2…` / `ba34da2a…`≠正式 / `2b3babb5…` / `fa973826…` / `c5433e80…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶38 非标审计意见剔除 overlay（mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only**；soft-penalty **非 PRIMARY**；再平衡=20；PIT=`available_at→T1` 键=`ts_code`；厚度 median≥30 ∧ frac(≥10)≥0.60 ∧ zero_frac≤0.50；Jaccard硬拒 **>0.5** vs negevent **或** 叶36；披露 34/35/37；§6.1 压峰全套；→ `_leaf38_audit_nonstd_exclusion/<ET_TS>/`）**新** `.ok` 已落盘；脚本全长 **`d5cf50bb…` only**；COUNT脚本 **`ba34da2a` ≠正式 / ban_as_live**；脚本审 **`87eb63f4` PASS_WITH_CONDITIONS**；FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays审 `acba0865` / LAND `d157429b` / who `16c1f70b`；COVER `7c3b8691` / COUNT盘 `e82aefa2` / JSON `2b3babb5` / dig `fa973826` / HI_LIQ `c5433e80`；叶34 **`482009dc` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶37 **`108aba8f`/`32605aca` HOLD CLOSED 禁复开**；叶36 HOLD **`feaa5dbb`/`575e8276`** 不回撤/不复开；旁线 fund **不混**。**禁 RESTORED** **`57ab9096`+`b5be1164`+`4096d401`+旧票（**n=33**；首项 `57ab9096`）。**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠叶36/叶37 复开**。CONDITIONS 全入签：
1. CLI c4/hard/stop **禁抬**双保险（破→停+上报）
2. 禁 `--no-overlap-report`
3. leaf36 pairs **须预落**（PIN_GAP≠硬过）
4. mask-only PRIMARY；soft-penalty 非 PRIMARY
5. rss=1500 禁抬 + peak_proof≤1500 REQUIRED（破禁 `.ok`；硬 Exit **94/95**）
6. 禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+

须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 overlap（硬拒 negevent/叶36；披露 34/35/37）。**Arch 不代跑**；**QUIET 本拍未挂=ABSENT**（`ban_hang_quiet_this_sign=true`；holder 字段仅标识=`leaf38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2`）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `87eb63f4` PASS_WITH_CONDITIONS | `87eb63f4805a9beaafccbe69497f5603b97bbe9b9cae50068587e678e1d1cbe9` | **MATCH** |
| 正式脚本 | `d5cf50bb…` only | `d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263` | **MATCH** |
| COUNT脚本 | `ba34da2a` ≠正式 / ban_as_live | `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296` | **MATCH** |
| FROZEN / ArchFROZEN | `ce0eb2ce` / `01753ff4` | `ce0eb2ce9486778e229d2722a647b6fb37e90810df2ac9f1530054d8040b93ed` / `01753ff4434abcbaba0cbe77def38e67763836b3f613be7ee09f05594e9839a5` | **MATCH** |
| who_pays审 / LAND / who | `acba0865` / `d157429b` / `16c1f70b` | `acba08650a034b7f40773a5a19923d529dcee0c0cabc6997ddee63501fe0caf2` / `d157429b14d8f4a9fcdcedde8df62d3be84828275171e4f80a529114032f843f` / `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c` | **MATCH** |
| COVER / COUNT盘 / JSON / dig / HI_LIQ | `7c3b8691` / `e82aefa2` / `2b3babb5` / `fa973826` / `c5433e80` | 全长现算 MATCH | **MATCH** |
| 叶34 / 叶35 / 叶37 | `482009dc` / `434ff42c` / `108aba8f` UNCHANGED | MATCH | **MATCH** |
| 叶36 HOLD | `feaa5dbb` / `575e8276` 不回撤 | MATCH | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`） | ABSENT | **MATCH** |
| QUIET 签前/签后 | **ABSENT**（本拍禁挂） | ABSENT / ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid33 | ≠`57ab9096`/`b5be1164`/`4096d401`/… | `62acf9fc` ∉ forbid33 | **MATCH** |
| forbid n / 含三钉 | n=33；首项 `57ab9096`；含 `b5be1164`+`4096d401` | n=33 且三钉在列首 | **MATCH** |
| pgrep leaf38 | 空 | 空 | **MATCH** |
| 窗期 | 90min + 4min expires | `2026-10-27T21:19:00-04:00` → `2026-10-27T22:49:00-04:00` / expires `2026-10-27T22:53:00-04:00`；签时 `2026-10-27T21:23:44-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `62acf9fc` / `62acf9fc95e1b00b3d4284db3ecae3fe5349eb503a268d041a18a55166b78e15` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**；`quiet_set_at_sign=false`；`ban_hang_quiet_this_sign=true`） |
| holder（标识 only） | `leaf38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2` |
| 正式脚本 | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` = `d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263` |
| COUNT脚本 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` = `ba34da2a…` **≠正式 / ban_as_live** |
| 脚本审 | `87eb63f4805a9beaafccbe69497f5603b97bbe9b9cae50068587e678e1d1cbe9` PASS_WITH_CONDITIONS |
| FROZEN / ArchFROZEN / who_pays审 / LAND / who | `ce0eb2ce…` / `01753ff4…` / `acba0865…` / `d157429b…` / `16c1f70b…` |
| COVER / COUNT盘 / JSON / dig / HI_LIQ | `7c3b8691…` / `e82aefa2…` / `2b3babb5…` / `fa973826…` / `c5433e80…` |
| 叶34 / 叶35 / 叶37 | `482009dc` UNCHANGED / `434ff42c` UNCHANGED / `108aba8f` HOLD CLOSED 禁复开 |
| 叶36 HOLD | `feaa5dbb` / `575e8276` · forbid_leaf36=true · forbid_reopen_leaf36_inquiry=true |
| 窗期 | `2026-10-27T21:19:00-04:00` → `2026-10-27T22:49:00-04:00`；expires `2026-10-27T22:53:00-04:00` |
| CLI PRIMARY（占位·不执行） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf38_audit_nonstd_exclusion/<ET_TS>/`；**无** `--no-overlap-report`；**无**抬 rss/c4/hard/stop |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；禁抬 c4/stop/hard；硬 Exit **94/95** |
| overlap | 强制 overlap vs negevent/leaf36 硬拒 + 披露 34/35/37；Jaccard>0.5 硬拒；leaf36 pairs 须预落（PIN_GAP≠硬过）；缺→PIN_GAP |
| mechanism / delivery | `g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；mask-only PRIMARY；soft-penalty 非 PRIMARY |
| 禁 RESTORED | **33** 票：`57ab9096,b5be1164,4096d401,eb70eef4,00eec671,10927bd9,25ae4572,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36/叶37复开 / fund混 | **false** / **false** / **false** / **≠** / **≠** |
| peak_proof | **REQUIRED**（含 `after_hiliq_chunk_*` / `after_mask_by` / `after_audit_excl` / `after_mask_expand` / `after_jaccard_subprocess` / `final_peak_proof`） |
| MemAvailable@签 | 13144776 kB |
| ALPHA_BUILD_EXECUTED@签 | **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT**（主令明文禁挂；同叶37 B1 签窗） |
| quiet_set_at_sign | **false** |
| ban_hang_quiet_this_sign | **true** |
| neq_a18 | **true** |
| pgrep leaf38 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（ALPHA_BUILD_EXECUTED=false） |

## 下一跳

1. **主** MATCH 本 `.ok`（+ SIGNED 回执）后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**；若主另令挂 QUIET 再挂——本签未挂）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap/jaccard + peak rss + hiliq/jaccard 分块标签；峰＞1500→Exit 94/95 停；Jaccard>0.5 vs negevent OR 叶36→硬拒票；leaf36 pairs 预落）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；≠叶36/叶37 复开；禁混 COUNT `ba34da2a`；禁混 fund；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 33 票（含 `57ab9096`+`b5be1164`+`4096d401`）；live=false；leo_notify=false

live=false.
