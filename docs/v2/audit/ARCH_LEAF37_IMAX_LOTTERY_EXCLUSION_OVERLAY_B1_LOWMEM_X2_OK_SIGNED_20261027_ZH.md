# Arch 叶37 B1_LOWMEM IMAX 彩票剔除 overlay · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T18:26:46-04:00`（America/New_York） |
| 主令 | 主 ~18:20 ET priority · 叶37 B1_LOWMEM 审票 `b403a7e5` PASS_WITH_CONDITIONS 认 → 开独立 X2 **只签** `.ok` 窗（钉脚本 `32605aca` only；**禁**基盘 `108aba8f` 当本窗真跑票；**禁挂 QUIET**；≠X2 ACCEPT；≠叶36） |
| 脚本审 | `b403a7e5…` **PASS_WITH_CONDITIONS** |
| COVER / CMD / DIFF / RECEIPT | `a4bfa39d…` / `286e2104…` / `6d61fd79…` / `46f4192d…` |
| VOID / FROZEN / ArchFROZEN / PIN / who_pays | `998171e1…` / `c5927f1b…` / `a5a9336d…` / `e01be34c…` / `4a074f0a…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶37 B1_LOWMEM IMAX 彩票剔除 overlay（mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；`b1_lowmem=true`；PRIMARY=HILIQ×x2→20261009；**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；再平衡=20；**C3=B IMAX_proxy**（`full_residual_e_id=false`；continuous **APPROX**；禁静默升 full e_id）；PIN **`e01be34c`**；**C11** overlay≠叶24 `g1g5_ashare_imax_intraday_v1` 主 α；`primary_load=panel_year_chunk_r_id_instr_chunk_imax` → `_leaf37_imax_lottery/<ET_TS>/`）**新** `.ok` 已落盘；脚本全长 **`32605aca…` only**；基盘 **`108aba8f` UNCHANGED** 且 **ban_as_live**；脚本审 **`b403a7e5` PASS_WITH_CONDITIONS**；COVER `a4bfa39d` / CMD `286e2104` / DIFF `6d61fd79` / RECEIPT `46f4192d`；VOID `998171e1` / FROZEN `c5927f1b` / ArchFROZEN `a5a9336d` / PIN `e01be34c` / who_pays `4a074f0a`；叶33 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶34 **`482009dc` UNCHANGED**；叶36 HOLD **`feaa5dbb`/`575e8276`** 不回撤/不复开。**禁 RESTORED** **`4096d401`**+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票（**n=31**；首项 `4096d401`=原 X2 VOID.ABORT_PEAK）。**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠叶36**。rss **1500** 禁抬（禁 `--rss-limit-mb`>1500 / 禁抬 c4·stop·hard / 禁放宽 split；硬 Exit **94/95**）；peak_proof **REQUIRED**（含 `after_panel_year_*` / `after_r_id_year_*` / `after_imax_instr_chunk_*`）；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 overlap JSON；**禁** `--no-overlap-report`；C7 硬拒 18/18v/27 + 披露 24/34/35/36。**Arch 不代跑**；**QUIET 本拍未挂=ABSENT**（与上次叶37 签不同；`ban_hang_quiet_this_sign=true`；holder 字段仅标识=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2`）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `b403a7e5` PASS_WITH_CONDITIONS | `b403a7e58b4bef3a948541b55c5e2789f65b6d6ff3d65bda5e27ba0895b8064b` | **MATCH** |
| B1 脚本 | `32605aca…` only | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **MATCH** |
| 基盘脚本 | `108aba8f` UNCHANGED 禁当真跑票 | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH** |
| COVER | `a4bfa39d` | `a4bfa39dce43a4c7c9d06fdbb4db06482610c520dced6524899ca05e5998b084` | **MATCH** |
| CMD | `286e2104` | `286e2104466c01170a8744c3bbd8c67a2a6ed2de24e0b3b8f69511b470c1843f` | **MATCH** |
| DIFF | `6d61fd79` | `6d61fd790e589f2d283f629c906393d1ff90eb997496f780ebc851701438ec96` | **MATCH** |
| RECEIPT | `46f4192d` | `46f4192dd1ac0b6bbe4fbc3a36d414df53ec88296cb3b3f174154b9a81f98dec` | **MATCH** |
| VOID | `998171e1` | `998171e12ab3b14ec9dcde0323e7ada6db83b091ee5ada53d2f25c7fc2362141` | **MATCH** |
| FROZEN / PIN | `c5927f1b` / `e01be34c` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` / `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| ArchFROZEN / who_pays | `a5a9336d` / `4a074f0a` | `a5a9336db924c70636603f5815375ee12086d93684823c12e3d7db8da4dc3313` / `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859` | **MATCH** |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` / `434ff42c` / `482009dc` UNCHANGED | MATCH | **MATCH** |
| 叶36 HOLD | `feaa5dbb` / `575e8276` 不回撤 | `feaa5dbb0ed11f1879a9e40d5dd389cd8bb51656a05c4ad0cedccfffe8d94840` / `575e8276058fd2b752adb87fd64184fe6a2fbf6243a12755e9a1e88fcc931345` | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED `4096d401`） | ABSENT | **MATCH** |
| QUIET 签前/签后 | **ABSENT**（本拍禁挂） | ABSENT / ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid31 | ≠`4096d401`/`eb70eef4`/`00eec671`/`10927bd9`/`25ae4572`/… | `b5be1164` ∉ forbid31 | **MATCH** |
| forbid n / 含五钉 | n=31；首项 `4096d401`；含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572` | n=31 且五钉在列首 | **MATCH** |
| pgrep leaf37 | 空 | 空 | **MATCH** |
| 窗期 | 90min + 4min expires | `2026-10-27T18:20:00-04:00` → `2026-10-27T19:50:00-04:00` / expires `2026-10-27T19:54:00-04:00`；签时 `2026-10-27T18:26:46-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `b5be1164` / `b5be11642107551e241578c41907105763a4a92009fa3a91a0bc810dad453ff0` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET 状态 | **ABSENT**（本拍**未挂**；`quiet_set_at_sign=false`；`ban_hang_quiet_this_sign=true`） |
| holder（标识 only） | `leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2` |
| B1 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` = `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` |
| 基盘脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` = `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` **UNCHANGED / ban_as_live** |
| 脚本审 | `b403a7e58b4bef3a948541b55c5e2789f65b6d6ff3d65bda5e27ba0895b8064b` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `a4bfa39d…` / `286e2104…` / `6d61fd79…` / `46f4192d…` |
| VOID / FROZEN / ArchFROZEN / PIN / who_pays | `998171e1…` / `c5927f1b…` / `a5a9336d…` / `e01be34c…` / `4a074f0a…` |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` UNCHANGED / `434ff42c` UNCHANGED / `482009dc` UNCHANGED |
| 叶36 HOLD | `feaa5dbb` / `575e8276` · forbid_leaf36=true · forbid_reopen_leaf36_inquiry=true |
| 窗期 | `2026-10-27T18:20:00-04:00` → `2026-10-27T19:50:00-04:00`；expires `2026-10-27T19:54:00-04:00` |
| CLI PRIMARY（占位·不执行） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok --out output/ai_factory/_leaf37_imax_lottery/<ET_TS>/`；**无** `--no-overlap-report`；**无**抬 rss |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json`；Jaccard≥0.7 硬拒 18/18v/27；披露 24/34/35/36；缺→PIN_GAP |
| C3 / C11 | B IMAX_proxy；`full_residual_e_id=false`；APPROX；PIN `e01be34c`；forbid_leaf24_imax_intraday_main / ban `g1g5_ashare_imax_intraday_v1` |
| mechanism / top_q / delivery | `g1g5_ashare_imax_lottery_exclusion_overlay_v1`；0.20；mask-only |
| 禁 RESTORED | **31** 票：`4096d401,eb70eef4,00eec671,10927bd9,25ae4572,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36 | **false** / **false** / **false** / **≠** |
| peak_proof | **REQUIRED**（含 year/instr 分块标签） |
| MemAvailable@签 | 12116532 kB |
| ALPHA_BUILD_EXECUTED@签 | **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 本拍 | **未挂 = ABSENT**（主令明文禁挂；与上次叶37 签不同） |
| quiet_set_at_sign | **false** |
| ban_hang_quiet_this_sign | **true** |
| neq_a18 | **true** |
| pgrep leaf37 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（ALPHA_BUILD_EXECUTED=false） |

## 下一跳

1. **主** MATCH 本 `.ok`（+ SIGNED 回执）后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**；若主另令挂 QUIET 再挂——本签未挂）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap JSON + peak rss + year/instr 分块标签；峰＞1500→Exit 94/95 停；Jaccard≥0.7 vs 18/18v/27→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；≠叶36 复开；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 31 票（含 `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`）；禁基盘 `108aba8f` 当真跑票；live=false；leo_notify=false

live=false.
