# Arch 叶34 高应计剔除 overlay · 独立 X2 `.ok` 签发回执

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T10:50:10-04:00`（America/New_York） |
| 主令 | 主 10:43 ET priority · 叶34 独立 X2 签窗 OPEN→SIGN（脚本审 `033b66f8` PASS_WITH_CONDITIONS；钉脚本 `482009dc` only） |
| 脚本审 | `033b66f8…` **PASS_WITH_CONDITIONS** |
| FROZEN / FROZEN审 / PIN / FROZEN RECEIPT | `8be1099e…` / `027efa26…` / `bb418e6a…` / `438ee33d…` |
| COVER / CMD / DIFF / RECEIPT | `c491e7a4…` / `cfa3ca4e…` / `f583b616…` / `f73c986f…` |
| who_pays 审 | `9d8a2f9e…`（只读） |
| live / promotion_approved / leo_notify | **false** / **false** / **false** |

## 结论

**SIGNED** — 叶34 高应计剔除 overlay（mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；PRIMARY=HILIQ×x2→20261009；**mask-only** top_q=**0.20**；soft-penalty **非 PRIMARY**；再平衡=20；C3=日表 OCF PIT `e_available_at≤t` + NP≤0 剔除 + YTD_cumulative + **ban_bs_wc_acc_primary**；PIN **`bb418e6a`**；primary_load=`rebal_day_lazy_ocf_daily_pit` → `_leaf34_high_accrual/<ET_TS>/`）**新** `.ok` 已落盘；**≠ RESTORED** `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)（**24**）；**≠ X2 ACCEPT**；**≠ selfcheck**；**≠ Book-Smoke**；脚本全长 **`482009dc…`**；脚本审 **`033b66f8` PASS_WITH_CONDITIONS**；COVER `c491e7a4` / CMD `cfa3ca4e` / DIFF `f583b616` / RECEIPT `f73c986f`；FROZEN `8be1099e` / FROZEN审 `027efa26` / FROZEN RECEIPT `438ee33d`；PIN `bb418e6a`；who_pays 审 `9d8a2f9e` / WHO `fa6aa2e3` / who COVER `76b37ca3`；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；模板 `4e0f3c00` 只读；**禁** `--no-overlap-report`；真跑须 `--allow-real-data` + `--arch-ok-path <NEW_OK>` 并写/消费 `overlap_vs_leaf19_25_27_30_31_32_33.json`（Jaccard≥0.7 硬拒；ρ>0.5 强度；叶25 尾窗披露；缺→PIN_GAP）；rss 软/硬帽 **1500** 禁抬（硬 Exit **94/95**）；peak_proof **REQUIRED**（`after_mask` / `after_ocf_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat` + ru_maxrss/VmHWM/`RSS_CHECK`）；**Arch 不代跑**；叶30 KEEP/衰减修复 `0087c928` / 叶28/29 **另队不夹带**；KEEP **不解阻** X2 ACCEPT；**禁触 A18**。QUIET **已挂且保留**供 AI prelaunch（本回合不 lift；holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2`；reason=`leaf34_high_accrual_exclusion_overlay_x2_hiliq`）。PRIMARY only；FULLA 仅 `--also-fulla-research` 研究旁路；**无同票 FALLBACK**；峰＞1500→Exit 94/95 停+上报（禁抬帽）。ALPHA_BUILD_EXECUTED@签=**false**。**≠A18**。leo_notify=**false**。

## 钉点 MATCH 表

| 项 | 期望 | 实测 | 结果 |
|---|---|---|---|
| 脚本审 | `033b66f8` PASS_WITH_CONDITIONS | `033b66f8462eeda178c8bb5410dd210885fdfbc49bab4ff4f9a56f99c97bd6a0` | **MATCH** |
| 脚本 | `482009dc…` only | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **MATCH** |
| COVER | `c491e7a4` | `c491e7a4bfcf40123cb4781bd8985a1df5ca6b4b96ac0e1e9ed7c879b7c6ca5d` | **MATCH** |
| CMD | `cfa3ca4e` | `cfa3ca4ec41a825ba0c9eb29d578c9798ed39c4120c19f1d64eef0a2629098c7` | **MATCH** |
| DIFF | `f583b616` | `f583b61645ad5a8fd2dd8e116fd91d60cc34f448e95c3fa65723b06112876919` | **MATCH** |
| RECEIPT | `f73c986f` | `f73c986fcacc24d7df41eed64442e91c4f550e2fd222c089dcd0da97cc5cc693` | **MATCH** |
| FROZEN | `8be1099e` | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` | **MATCH** |
| FROZEN审 | `027efa26` | `027efa26093696e2684a44784b1c2cfba2e907d7027f95ace4ba0e4eae22fe4b` | **MATCH** |
| FROZEN RECEIPT | `438ee33d` | `438ee33dc3acd8c5781af1c983b78246bdd0082db1e868ea4bcd8ee5a0dbf01a` | **MATCH** |
| PIN | `bb418e6a` | `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` | **MATCH** |
| who_pays 审 | `9d8a2f9e` | `9d8a2f9edde9f00ae230b9914025fc95db2fba35dc102f83c2a38c26d8247ecd` | **MATCH** |
| who_pays draft | `fa6aa2e3` | `fa6aa2e3ffb084cc01f6a4d20575e528f1c095262c10a00e70dadb4c15cc473b` | **MATCH** |
| who COVER | `76b37ca3` | `76b37ca33be72f5311ded30693493ab431b5ac0820730c2f4d0081cfe9b5aa8c` | **MATCH** |
| 叶33 正式 | `afbbe7e7` UNCHANGED | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH** |
| 叶32 HOLD | `45dd87dc` 不回撤 | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH** |
| 拟 .ok 签前 | ABSENT（禁 RESTORED） | ABSENT | **MATCH** |
| QUIET 签前 | ABSENT | ABSENT | **MATCH** |
| ai_factory live `.ok` | 0→1（本签） | 签前 0 / 签后 1 | **MATCH** |
| 新 `.ok` sha8 ∉ forbid24 | ≠`245df63f`/`c5ed13df`/`5774bb6e`/`81521fb5` 等 | `c1b71e64` ∉ forbid24 | **MATCH** |
| pgrep leaf34 | 空 | 空 | **MATCH** |
| 窗期 | ≥90min prelaunch → expires | `2026-10-27T10:43:00-04:00` → `2026-10-27T12:13:00-04:00` / expires `2026-10-27T12:17:00-04:00`；签时 `2026-10-27T10:50:10-04:00` | **IN_WINDOW** |

## 钉

| 项 | 值 |
|---|---|
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok` |
| `.ok` sha8 / 全长 | `c1b71e64` / `c1b71e646093dbbe1cfea41c684d8ee0de8e5af8f0a8f058182c251d7dbe4ce1` |
| QUIET 路径 | `output/loop/RESEARCH_QUIET.lock` |
| QUIET sha8 / 全长 | `bc6f8b83` / `bc6f8b83f49e16f015ec3416580d846cd279594a4042ba0e406aaabe70565389` |
| QUIET holder / reason | `leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2` / `leaf34_high_accrual_exclusion_overlay_x2_hiliq` |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` = `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` |
| 脚本审 | `033b66f8462eeda178c8bb5410dd210885fdfbc49bab4ff4f9a56f99c97bd6a0` PASS_WITH_CONDITIONS |
| COVER / CMD / DIFF / RECEIPT | `c491e7a4…` / `cfa3ca4e…` / `f583b616…` / `f73c986f…` |
| FROZEN / FROZEN审 / FROZEN RECEIPT / PIN | `8be1099e…` / `027efa26…` / `438ee33d…` / `bb418e6a…` |
| who_pays 审 / WHO / who COVER | `9d8a2f9e…` / `fa6aa2e3…` / `76b37ca3…` |
| 叶33 / 叶32 HOLD | `afbbe7e7` UNCHANGED / `45dd87dc` 不回撤 |
| 窗期 | `2026-10-27T10:43:00-04:00` → `2026-10-27T12:13:00-04:00`；expires `2026-10-27T12:17:00-04:00` |
| CLI PRIMARY | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok --out output/ai_factory/_leaf34_high_accrual/<ET_TS>`；**无** `--no-overlap-report` |
| FALLBACK | **无**；峰＞1500 / 失败 / ABORT → Exit 94/95 停+上报（禁抬帽） |
| rss 软/硬帽 | **1500** MB；禁抬帽；硬 Exit **94/95** |
| overlap | 强制 `overlap_vs_leaf19_25_27_30_31_32_33.json`；Jaccard≥0.7 硬拒；ρ>0.5 强度；叶25 尾窗披露；缺→PIN_GAP；forbid_no_overlap_report=true |
| PRIMARY load | **rebal_day_lazy_ocf_daily_pit** |
| C3 | 日表+PIT `e_available_at≤t`+NP≤0+YTD_cumulative；PIN `bb418e6a`；ban_bs_wc_acc_primary=true |
| mechanism / top_q / delivery / 再平衡 | `g1g5_ashare_high_accrual_exclusion_overlay_v1`；0.20；mask-only；20 |
| 产物 | `_leaf34_high_accrual/<ET_TS>/` + exclusion_mask parquet + `run_meta.json` + overlap JSON |
| 采样 | 仅 `/tmp/quantlab_leaf34_high_accrual_*` |
| 禁 RESTORED | **24** 票：`245df63f,c5ed13df,5774bb6e,02426b73,4bb141c9,fdbaa512,aa25e989,7e239487,5af20222,5ae077fa,3c297052,e107383f,2be59acd,a7d98ac9,8e51de63,3a6caa4f,8bcd79dc,725be3e0,0f50daf7,3c19dd7d,1c32ab1e,6054b3bf,6de02e74,81521fb5` |
| Book-Smoke / X2 ACCEPT / selfcheck | **false** / **false** / **false** |
| peak_proof | **REQUIRED**（after_mask / after_ocf_rebal_* / after_mask_cs_rebal_* / after_daily_concat + ru_maxrss/VmHWM/RSS_CHECK） |
| `0087c928` / 叶28/29 | 另队；**不在**本 `.ok`；KEEP 不解阻 |
| MemAvailable@签 | 13197960 kB |

## QUIET / pgrep

| 项 | 值 |
|---|---|
| QUIET 挂时 | `2026-10-27T10:50:10-04:00` reason=`leaf34_high_accrual_exclusion_overlay_x2_hiliq` holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2` |
| do_not_lift_until_arch_or_consumed | **true**（本拍不 lift） |
| neq_a18 | **true** |
| pgrep leaf34 | 空 |
| 签时 web | **NOT empty**（`kline.py` / `export_static.py` 在跑）；**未触 A18**；AI prelaunch **须** healthz quiet + 清 web pgrep 后再跑 |
| Arch 代跑 `--allow-real-data` | **未执行** |

## 下一跳

1. **主** MATCH `.ok`+`QUIET` 后令 AI prelaunch 单次 PRIMARY（须在 expires 前；Arch **不代跑**）
2. AI 交实峰回执（mask/alpha sha + run_meta sha + overlap JSON 含 vs leaf33 + peak rss 含 after_mask / after_ocf_rebal_* / after_mask_cs_rebal_* / after_daily_concat；峰＞1500→Exit 94/95 停；Jaccard≥0.7→硬拒票）→ Arch 核 CONSUME
3. ≠X2 ACCEPT；≠selfcheck；≠Book-Smoke；不解阻 `0087c928`/叶28/29 另队；KEEP 不解阻；**≠A18**；不 RESTORED 24 票；live=false；leo_notify=false

live=false.
