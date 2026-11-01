# Arch 叶37 IMAX 彩票剔除 overlay · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T17:41:25-04:00`（America/New_York） |
| 主令 | 主 ~17:33 ET priority · 叶37 正式脚本 PASS_WC 认 → 开独立 X2 签窗（脚本审 `8d8ae2f3` PASS_WITH_CONDITIONS；钉脚本 `108aba8f` only；≠X2 ACCEPT；≠叶36） |
| 脚本审 | `8d8ae2f3…` **PASS_WITH_CONDITIONS** |
| COVER / CMD / DIFF / RECEIPT | `bbd16814…` / `4b735113…` / `40284f4f…` / `ff1bf3cc…` |
| FROZEN / ArchFROZEN / PIN / who_pays | `c5927f1b…` / `a5a9336d…` / `e01be34c…` / `4a074f0a…` |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶37 IMAX 彩票剔除 overlay（mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；再平衡=20；**C3=B IMAX_proxy**（`full_residual_e_id=false`；continuous **APPROX**；禁静默升 full e_id）；PIN **`e01be34c`**；**C11** overlay≠叶24 `g1g5_ashare_imax_intraday_v1` 主 α → `_leaf37_imax_lottery/<ET_TS>/`）**新** `.ok` 已落盘；脚本全长 **`108aba8f…` only**；脚本审 **`8d8ae2f3` PASS_WITH_CONDITIONS**；COVER `bbd16814` / CMD `4b735113` / DIFF `40284f4f` / RECEIPT `ff1bf3cc`；FROZEN `c5927f1b` / ArchFROZEN `a5a9336d` / PIN `e01be34c` / who_pays `4a074f0a`；叶33 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶34 **`482009dc` UNCHANGED**；叶36 HOLD **`feaa5dbb`/`575e8276`** 不回撤/不复开。**禁 RESTORED** `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票（**n=30**；`25ae4572` 亦为叶35 旧脚本 sha，禁碰）。**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；**≠叶36**。rss **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**；须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 overlap JSON；**禁** `--no-overlap-report`；C7 硬拒 18/18v/27 + 披露 24/34/35/36。**Arch 不代跑**；QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2`；reason=`leaf37_imax_lottery_exclusion_overlay_x2_hiliq`）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `8d8ae2f3` PASS_WITH_CONDITIONS | `8d8ae2f38ac378a8a9ea1ed1de9b72c2784855ef4b3c7debed8b225f4f199f22` | **MATCH** |
| 脚本 | `108aba8f…` only | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH** |
| COVER | `bbd16814` | `bbd16814e895e244784955b00ddd5e405533618f0c04d523ce793cfcfa06d0d6` | **MATCH** |
| CMD | `4b735113` | `4b7351131caec10b819cbc093334cb83e21460488069d074d5002dc175e95624` | **MATCH** |
| DIFF | `40284f4f` | `40284f4f69a84a95f189b26d24c9a223bb444949619fba5f47329379f0b98f97` | **MATCH** |
| RECEIPT | `ff1bf3cc` | `ff1bf3ccbad48e3223798a6bfff327e8ca6f8ec442ac401f621dff248ee9a095` | **MATCH** |
| FROZEN / PIN | `c5927f1b` / `e01be34c` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` / `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| ArchFROZEN / who_pays | `a5a9336d` / `4a074f0a` | `a5a9336db924c70636603f5815375ee12086d93684823c12e3d7db8da4dc3313` / `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859` | **MATCH** |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` / `434ff42c` / `482009dc` UNCHANGED | MATCH | **MATCH** |
| 叶36 HOLD | `feaa5dbb` / `575e8276` 不回撤 | `feaa5dbb0ed11f1879a9e40d5dd389cd8bb51656a05c4ad0cedccfffe8d94840` / `575e8276058fd2b752adb87fd64184fe6a2fbf6243a12755e9a1e88fcc931345` | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid30 | ≠`eb70eef4`/`00eec671`/`10927bd9`/`25ae4572`/… | `4096d401` ∉ forbid30 | **MATCH** |
| forbid n / 含四钉 | n=30；含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572` | n=30 且四钉在列首 | **MATCH** |
| pgrep leaf37 | 空 | 空 | **MATCH** |
| 窗期 | 90min + 4min expires | `2026-10-27T17:33:00-04:00` → `2026-10-27T19:03:00-04:00` / expires `2026-10-27T19:07:00-04:00`；签时 `2026-10-27T17:41:25-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `4096d401` / `4096d401a11124f4f6999efd66e1158e8e13378f24be355ffc8565975be44a74` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `beb7dc8c` / `beb7dc8c23d6295a554a593d3b8a131cb29de3bf1085ba546ef2df98b66c6573` |
| QUIET holder / reason | `leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2` / `leaf37_imax_lottery_exclusion_overlay_x2_hiliq` |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` = `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` |
| 脚本审 | `8d8ae2f38ac378a8a9ea1ed1de9b72c2784855ef4b3c7debed8b225f4f199f22` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `bbd16814…` / `4b735113…` / `40284f4f…` / `ff1bf3cc…` |
| FROZEN / ArchFROZEN / PIN / who_pays | `c5927f1b…` / `a5a9336d…` / `e01be34c…` / `4a074f0a…` |
| 叶33 / 叶35 / 叶34 | `afbbe7e7` UNCHANGED / `434ff42c` UNCHANGED / `482009dc` UNCHANGED |
| 叶36 HOLD | `feaa5dbb` / `575e8276` · forbid_leaf36=true · forbid_reopen_leaf36_inquiry=true |
| 窗期 | `2026-10-27T17:33:00-04:00` → `2026-10-27T19:03:00-04:00`；expires `2026-10-27T19:07:00-04:00` |
| CLI PRIMARY（占位·不执行） | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf37_imax_lottery/<ET_TS>/`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json`；Jaccard≥0.7 硬拒 18/18v/27；披露 24/34/35/36；缺→PIN_GAP |
| C3 / C11 | B IMAX_proxy；`full_residual_e_id=false`；APPROX；PIN `e01be34c`；forbid_leaf24_imax_intraday_main / ban `g1g5_ashare_imax_intraday_v1` |
| mechanism / top_q / delivery | `g1g5_ashare_imax_lottery_exclusion_overlay_v1`；0.20；mask-only |
| 禁 RESTORED | **30** 票：`eb70eef4,00eec671,10927bd9,25ae4572,178e90e9,c1b71e64,245df63f,c5ed13df,5774bb6e,81521fb5,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74` |
| Book-Smoke / X2 ACCEPT / selfcheck / 叶36 | **false** / **false** / **false** / **≠** |
| peak_proof | **REQUIRED** |
| MemAvailable@签 | 13181424 kB |
| ALPHA_BUILD_EXECUTED@签 | **false** |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T17:41:25-04:00` reason=`leaf37_imax_lottery_exclusion_overlay_x2_hiliq` holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf37 | 空 |
| Arch 代跑 `--allow-real-data` | **未执行**（ALPHA_BUILD_EXECUTED=false） |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap JSON + peak rss；峰＞1500→Exit 94/95 停；Jaccard≥0.7 vs 18/18v/27→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；≠叶36 复开；COUNT APPROX ≠ ACCEPT；**≠A18**；不 RESTORED 30 票（含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`）；live=false；leo_notify=false

live=false.
