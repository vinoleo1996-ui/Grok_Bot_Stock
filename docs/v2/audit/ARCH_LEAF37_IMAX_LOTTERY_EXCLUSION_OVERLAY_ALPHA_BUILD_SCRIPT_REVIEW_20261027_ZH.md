# Arch 审阅：叶37 IMAX/隔夜彩票剔除 overlay 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T17:29:13-04:00`（America/New_York；墙钟 `2026-10-27 17:29 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`c5927f1b`** · FROZEN 审 **`a5a9336d`**（PASS_WC · C2 正式脚本）· who_pays 审 **`4a074f0a`** · PIN **`e01be34c`** · COVER **`bbd16814`** · CMD **`4b735113`** · DIFF **`40284f4f`** · RECEIPT **`ff1bf3cc`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / `--allow-real-data` 真构建（仅 `py_compile` + `pyflakes` + `--dry-compile-only`）；**不改**脚本/FROZEN/PIN/COVER/CMD/DIFF/RECEIPT/AI 件；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；叶36 HOLD（`feaa5dbb`/`575e8276`）不回撤、禁复开 inquiry；叶35/34/33/`afbbe7e7`/32 HOLD 不回撤；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 · 叶37 LAND_SCRIPT 正式脚本只审 GO（AI DRAFT READY 盘证 MATCH；EXECUTED=false） |
| 轻量复跑 | `py_compile` **PASS**；`pyflakes` **CLEAN exit0**；`--dry-compile-only` exit **0**（`script_sha8=108aba8f` / FROZEN=`c5927f1b` / PIN=`e01be34c` / ArchFROZEN=`a5a9336d` / top_q=0.20 / PRIMARY_DELIVERY=`mask_only` / rss=1500 / C3=B / `full_residual_e_id=false` / ban leaf24 `g1g5_ashare_imax_intraday_v1`；executed=false）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`108aba8f` MATCH**：mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高 IMAX mask=0；可算其余 mask=1；不可算不填假 0）；soft-penalty **默认关、非 PRIMARY**；C3=B `IMAX_proxy=mean(largest 5 finite r_id in [t-19,t])` min_valid≥15；`r_id=(1+ret)/(1+ret_on)-1`；`full_residual_e_id=false` 持续 APPROX；再平衡=20；X2 2024-06-03→2026-10-09；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选；C7 overlap 硬拒 Jaccard≥0.7 vs 叶18/18v/27 + 披露 vs 24/34/35/36；rss=1500 硬 ABORT + peak_proof REQUIRED；forbid **30** 项≡FROZEN §10（含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`）；C11 overlay≠叶24 主 α；C12 APPROX≠ACCEPT；C10 叶36 HOLD CLOSED；DIFF **字节≡脚本**；dry/pyflakes PASS；叶33 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` UNCHANGED**；叶34 **`482009dc` UNCHANGED**；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗（钉 **`108aba8f` only**）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH** · 1835 行 |
| COVER DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `bbd16814` | `bbd16814e895e244784955b00ddd5e405533618f0c04d523ce793cfcfa06d0d6` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `4b735113` | `4b7351131caec10b819cbc093334cb83e21460488069d074d5002dc175e95624` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `40284f4f` | `40284f4f69a84a95f189b26d24c9a223bb444949619fba5f47329379f0b98f97` | **MATCH** · NEW；重建字节 **≡脚本** |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `ff1bf3cc` | `ff1bf3ccbad48e3223798a6bfff327e8ca6f8ec442ac401f621dff248ee9a095` | **MATCH** · EXECUTED=false |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `c5927f1b` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` | **MATCH** |
| PIN（C3=B） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | `e01be34c` | `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `a5a9336d` | `a5a9336db924c70636603f5815375ee12086d93684823c12e3d7db8da4dc3313` | **MATCH** · PASS_WC |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `4a074f0a` | `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859` | **MATCH** |
| FROZEN RECEIPT（只读） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `3992f0fa` | `3992f0faf0cb075b0e641f2da5dbeda3adb67ef101cf7f79f384560d774ecbe2` | **MATCH** |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| 叶35 正式（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` | **UNCHANGED** |
| 叶34 模板（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **UNCHANGED** |
| 叶36 HOLD WHO（只读） | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `feaa5dbb` | 前8 MATCH | **不回撤** |
| 叶36 HOLD JSON（只读） | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` | `575e8276` | 前8 MATCH | **不回撤** |
| `research/leaf36*` | — | ABSENT | ABSENT | **MATCH** |
| live leaf37 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37*` / `*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

哈希闭环：脚本/COVER/CMD/DIFF/RECEIPT 互指 sha8 与盘上一致；脚本常量钉 FROZEN `c5927f1b` / PIN `e01be34c` / ArchFROZEN `a5a9336d` / who_pays `4a074f0a` / 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` / 叶36 HOLD `feaa5dbb`+`575e8276`。DIFF 自 `/dev/null` NEW 重建内容 **字节等于** 脚本（sha 同 `108aba8f`）。脚本内 `COVER_SHA8=847245f8` 钉上游 who_pays COVER（非本拍 BUILD COVER `bbd16814`）——与 FROZEN 上游钉一致，**不冲突**。

## 2. 必审清单（脚本 vs FROZEN `c5927f1b` / PIN `e01be34c` / 审 `a5a9336d`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** 落地≡FROZEN+PIN：mechanism/常量对齐 | **PASS** | `MECHANISM_TAG=g1g5_ashare_imax_lottery_exclusion_overlay_v1`；`FROZEN_SHA8=c5927f1b`；`PIN_SHA8=e01be34c`；`ARCH_FROZEN_REVIEW_SHA8=a5a9336d`；`ARCH_WHO_PAYS_REVIEW_SHA8=4a074f0a`；dry pins 齐 |
| 2 | **PRIMARY=mask-only**；soft-penalty 非 PRIMARY / 默认关 | **PASS** | `PRIMARY_DELIVERY=mask_only`；`SOFT_PENALTY_DEFAULT=False`；dry `soft_penalty_is_primary=false`；`--enable-soft-penalty` 可选且须 SW+logmv+style，缺→PIN_GAP |
| 3 | **C3=B** IMAX_proxy：mean largest 5 finite r_id in [t-19,t]；min_valid≥15；`r_id=(1+ret)/(1+ret_on)-1`；`full_residual_e_id=false`；持续 APPROX；禁静默升全 e_id | **PASS** | `IMAX_WIN=20`/`IMAX_K_MAX=5`/`IMAX_MIN_VALID=15`；`FULL_RESIDUAL_E_ID=False`；`rolling_imax`+panel `r_id`；`C3_FORMULA_PIN`；`ban_silent_full_e_id_upgrade`；dry `approx=true` |
| 4 | **C5** top_q=**0.20**；高 IMAX→mask=0；不可算名不进有效集、不填假 0 | **PASS** | `TOP_Q=0.20`；`_cross_section_mask_imax`：`imax>=Q_(1-q)`→0 else 1；再平衡日 `day_imax[imax_proxy.notna()]` 过滤；空→`imax_empty_or_no_valid` PIN_GAP，不填假 0 |
| 5 | **C11** ≠叶24 `g1g5_ashare_imax_intraday_v1` 完整 −IMAX 排序主 α；交付 exclusion mask overlay 叠主干 | **PASS** | `LEAF24_MECHANISM_BAN`；交付日度 exclusion mask；`ban_leaf24_imax_intraday_main_alpha`；`alpha=-imax_proxy` 仅作 overlap ρ 连续分（schema 明示 PRIMARY=mask）；禁 18/27/24 α 主输入 |
| 6 | **rss=1500** 硬 ABORT + peak_proof REQUIRED；禁抬 | **PASS_WITH_CONDITIONS** | `RSS_LIMIT_MB=1500`；`check_rss` 于 `after_mask` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat`；dry `peak_proof_required`+`ban_raise_rss=true`。**缺口**：相对叶34，本脚本 `run_build` **未**硬 STOP `--rss-limit-mb>1500` / 抬 C4·stop·hard——须签文硬钉禁抬（双保险）；本拍**不改脚本** |
| 7 | **forbid** 含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票（30 项） | **PASS** | `FORBID_OK_SHA8` **30** 项集合 **≡** FROZEN §10 全集；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 `.ok` 逻辑 |
| 8 | **overlap**：硬拒 Jaccard≥0.7 vs 叶18/18v/27；披露 vs 24/34/35/36 | **PASS_WITH_CONDITIONS** | `HARD_OVERLAP_TAGS` / `DISCLOSE_OVERLAP_TAGS`；`JACCARD_HARD=0.7`；硬拒 return **4**；缺硬文件→PIN_GAP；CLI 仍保留 `--no-overlap-report` 但真跑硬 STOP → **仍须入签文硬闸**（双保险） |
| 9 | **HI_LIQ PRIMARY**；FULLA 仅 `--also-fulla-research`；`--universe FULLA` 作 PRIMARY 应 STOP | **PASS** | dry/run `--universe FULLA` STOP exit2；`ban_silent_fulla_as_primary`；`--also-fulla-research` 可选且失败仅 WARN |
| 10 | dry/pyflakes：仅允许 py_compile / pyflakes / `--dry-compile-only`；禁真跑 | **PASS** | 本机复跑见上；关键 pins MATCH；**未** `--allow-real-data`；`research/__pycache__/leaf37*` 已清理 |
| 11 | DIFF/COVER/CMD/RECEIPT 与脚本一致；EXECUTED=false | **PASS** | DIFF 重建≡脚本；五件互钉 MATCH；RECEIPT/CMD/COVER/dry 均 EXECUTED=false |
| 12 | 叶36 HOLD（feaa5dbb/575e8276）不回撤；禁复开 inquiry | **PASS** | 常量钉；`ban_reopen_leaf36_inquiry`；`research/leaf36*` ABSENT；本拍未触叶36 |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| CLI `--rss-limit-mb` / C4·stop·hard 可被抬（无叶34 式硬 STOP） | **管控** | dry 钉 `ban_raise_rss`；须签文硬钉 rss=1500 禁抬；破→停+上报；本拍不改文 |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 靠脚本硬 STOP + 签文双闸 |
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 须 peak_proof；破 soft/hard → 停+上报；**禁抬帽** |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；启用须另窗+SW+style；不得抬作 PRIMARY |
| COUNT ρ18≈0.505 / ρ27≈0.665 已触强度过滤 | **披露** | FROZEN 持续披露；不解阻也不单独废叶；签窗重算 |
| COVER_SHA8 常量钉上游 `847245f8`（≠ BUILD COVER） | **低** | 与 FROZEN 上游钉一致；BUILD COVER 以盘上 `bbd16814` 为准 |
| APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻 |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`108aba8f` only**（全长 `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b`）。
2. **禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票**：forbid∋30 sha8≡FROZEN §10；禁复用叶18/24/27/30–36 任一 `.ok`；禁复用 VOID/CONSUMED 路径。
3. **真跑前主 MATCH**：script 全长如上；dry-compile PASS；FROZEN `c5927f1b` / PIN `e01be34c` / ArchFROZEN `a5a9336d` / who_pays `4a074f0a` / 本审回执；叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` 不回撤；叶36 HOLD `feaa5dbb`/`575e8276` 不复开。
4. **签文硬钉 rss=1500 禁抬**：PRIMARY CLI **不得**传 `--rss-limit-mb`>`1500` 或抬 `--c4-kb`/`--stop-kb`/`--hard-kb`；peak_proof REQUIRED（`after_mask` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat`）；破 soft/hard → 停+上报。
5. **C7 签文硬钉**：真跑**必须**写并消费 overlap JSON（硬拒 18/18v/27；披露 24/34/35/36）；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；缺硬文件→PIN_GAP；签文 **禁** `--no-overlap-report`。
6. **C3 签文硬钉**：`IMAX_proxy` C3=B；`full_residual_e_id=false`；持续 APPROX；禁静默升全 e_id。
7. **PRIMARY 纪律**：判决=HILIQ **mask-only** top_q=0.20；FULLA 仅 `--also-fulla-research`；soft-penalty 启用须另窗+SW+style，**不得**作 PRIMARY；C11≠叶24 主 α。
8. **PRIMARY CLI 钉**（占位；现不可跑；无 `--no-overlap-report`；无抬 rss）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf37_imax_lottery/<ET_TS>/`
9. sampler `/tmp/quantlab_leaf37_imax_lottery_*`；out `_leaf37_imax_lottery/<ET_TS>/`；Arch **不代跑**；可挂 leaf37 自有 QUIET（当前 QUIET **ABSENT**）。
10. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻 · KEEP 不解阻。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶37 / RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** 脚本 `108aba8f` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN / Arch 审
- **未** `--allow-real-data` / **未**代跑 X2 / **未** Book-Smoke（仅 `py_compile` + `pyflakes` + dry）；`research/__pycache__/leaf37*` **已清理/ABSENT**
- **未** RESTORED；**未**抬 rss；**未**改 top_q / mask-only / 升 e_id
- **未改** 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc`；**未回撤** 叶36 HOLD；**未**落地 `research/leaf36*`；**禁复开 inquiry**
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 108aba8f（本审 PASS_WITH_CONDITIONS · FROZEN c5927f1b / PIN e01be34c / ArchFROZEN a5a9336d / who_pays 4a074f0a）
  → 请主另排独立 X2 签窗（新 .ok；钉 108aba8f only；禁 RESTORED eb70eef4+00eec671+10927bd9+25ae4572+旧票）
      → AI prelaunch→execute（无 --no-overlap-report；rss=1500 禁抬；peak_proof；C3=B；mask-only PRIMARY；C11≠leaf24）
          → Arch CONSUME（≠X2 ACCEPT；叶36 HOLD 不复开）
```

**本拍不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`108aba8f` MATCH** |
| COVER / CMD / DIFF / RECEIPT | **`bbd16814`** / **`4b735113`** / **`40284f4f`** / **`ff1bf3cc`** MATCH |
| FROZEN / PIN / ArchFROZEN / who_pays | **`c5927f1b`** / **`e01be34c`** / **`a5a9336d`** / **`4a074f0a`** MATCH |
| 叶33 / 叶35 / 叶34 | **`afbbe7e7` UNCHANGED** / **`434ff42c` UNCHANGED** / **`482009dc` UNCHANGED** |
| 叶36 HOLD | **`feaa5dbb`/`575e8276`** 不回撤 |
| dry-compile / py_compile / pyflakes | **PASS**（exit0 / PASS / CLEAN）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `108aba8f` only；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | script/`108aba8f` · COVER/`bbd16814` · CMD/`4b735113` · DIFF/`40284f4f` · RECEIPT/`ff1bf3cc` · FROZEN/`c5927f1b` · PIN/`e01be34c` · ArchFROZEN/`a5a9336d` · who_pays/`4a074f0a` |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见父回报）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑.
