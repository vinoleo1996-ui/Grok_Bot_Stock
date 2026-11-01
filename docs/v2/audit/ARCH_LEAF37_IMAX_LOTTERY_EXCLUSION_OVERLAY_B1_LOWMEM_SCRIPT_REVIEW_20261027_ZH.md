# Arch 审阅：叶37 IMAX/隔夜彩票剔除 overlay · B1 / LOW_MEM 脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审 B1_LOWMEM 另票脚本） |
| 时刻 | `2026-10-27T18:17:09-04:00`（America/New_York；墙钟 `2026-10-27 18:17 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | 原脚本审 **`8d8ae2f3`**（基盘 `108aba8f`）· VOID **`998171e1`** · PREREG_FROZEN **`c5927f1b`** · PIN **`e01be34c`** · ArchFROZEN **`a5a9336d`** · who_pays **`4a074f0a`** · COVER **`a4bfa39d`** · CMD **`286e2104`** · DIFF **`6d61fd79`** · RECEIPT **`46f4192d`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / `--allow-real-data` 真构建（仅 `py_compile` + `pyflakes` + `--dry-compile-only`）；**不改** B1 脚本/基盘/FROZEN/PIN/COVER/CMD/DIFF/RECEIPT/AI 件；禁 RESTORED `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；叶36 HOLD（`feaa5dbb`/`575e8276`）不回撤；叶35/34/33 不回撤；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 · 叶37 B1_LOWMEM 只审 GO（AI LOW_MEM 另票 READY 盘证 MATCH；EXECUTED=false；≠X2 ACCEPT） |
| 轻量复跑 | `py_compile` **PASS**；`pyflakes` **CLEAN exit0**；`--dry-compile-only` exit **0**（`script_sha8=32605aca` / `b1_lowmem=true` / `prev_script_sha8=108aba8f` / forbid0=`4096d401` n=31 / FROZEN=`c5927f1b` / PIN=`e01be34c` / ArchFROZEN=`a5a9336d` / top_q=0.20 / PRIMARY_DELIVERY=`mask_only` / rss=1500 / C3=B / `full_residual_e_id=false` / `primary_load=panel_year_chunk_r_id_instr_chunk_imax` / executed=false）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

B1 另票脚本 **`32605aca` MATCH**：并列 `…_b1_lowmem.py`（`b1_lowmem=true`；`prev_script_sha8=108aba8f`）；基盘 **`108aba8f` UNCHANGED**；`_load_panel_imax` 年分块 panel→瘦长 `r_id`→del+gc + instrument 列块 IMAX（step=256）+ 分块 peak_proof 标签，**静态针对**原 ABORT @`after_r_id` peak_kb=1204776≥split；契约未漂（mask-only q=0.20 / C3=B / C11≠叶24 / soft-penalty 非 PRIMARY / HI_LIQ PRIMARY / FULLA STOP / overlap 硬拒 18/18v/27）；rss=1500 硬 ABORT + peak_proof REQUIRED；forbid 首项 **`4096d401`** n=**31**；dry/pyflakes PASS；COVER/CMD/DIFF/RECEIPT 互钉 MATCH；EXECUTED=false；live `.ok`/QUIET **ABSENT**。**足以过 soft-split 仅静态可信** → **PASS_WITH_CONDITIONS**。**本拍不签**；请主另排独立 X2 签窗（钉 **`32605aca` only**）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **B1 LOW_MEM 脚本** | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` | `32605aca` | `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **MATCH** · 1915 行 · NEW 并列 |
| **基盘（禁改）** | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f` | `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **UNCHANGED MATCH** · 1835 行 |
| COVER DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_COVER_DRAFT_20261027_ZH.md` | `a4bfa39d` | `a4bfa39dce43a4c7c9d06fdbb4db06482610c520dced6524899ca05e5998b084` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_CMD_DRAFT_20261027_ZH.md` | `286e2104` | `286e2104466c01170a8744c3bbd8c67a2a6ed2de24e0b3b8f69511b470c1843f` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_DIFF_DRAFT_20261027.diff` | `6d61fd79` | `6d61fd790e589f2d283f629c906393d1ff90eb997496f780ebc851701438ec96` | **MATCH** · vs 基盘；NEW 并列非覆盖 |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_SCRIPT_RECEIPT_20261027_ZH.md` | `46f4192d` | `46f4192dd1ac0b6bbe4fbc3a36d414df53ec88296cb3b3f174154b9a81f98dec` | **MATCH** · EXECUTED=false |
| Arch VOID.ABORT_PEAK | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_VOID_ABORT_PEAK_20261027_ZH.md` | `998171e1` | `998171e12ab3b14ec9dcde0323e7ada6db83b091ee5ada53d2f25c7fc2362141` | **MATCH** |
| 原脚本审（对照） | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` | `8d8ae2f3` | `8d8ae2f38ac378a8a9ea1ed1de9b72c2784855ef4b3c7debed8b225f4f199f22` | **MATCH** |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `c5927f1b` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` | **MATCH** · 未改 |
| PIN（C3=B） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | `e01be34c` | `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** · 未改 |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `a5a9336d` | `a5a9336db924c70636603f5815375ee12086d93684823c12e3d7db8da4dc3313` | **MATCH** · 未改 |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `4a074f0a` | `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859` | **MATCH** · 未改 |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **UNCHANGED** |
| 叶35 正式（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a` | **UNCHANGED** |
| 叶34 模板（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **UNCHANGED** |
| 叶36 HOLD WHO（只读） | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `feaa5dbb` | 前8 MATCH | **不回撤** |
| 叶36 HOLD JSON（只读） | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` | `575e8276` | 前8 MATCH | **不回撤** |
| `research/leaf36*` | — | ABSENT | ABSENT | **MATCH** |
| VOID `.ok`（禁 RESTORED） | `output/ai_factory/_consumed/…4096d401.VOID.ABORT_PEAK…ok` | `4096d401` | archived | **禁 RESTORED** |
| live leaf37 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37*` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

哈希闭环：B1 脚本/COVER/CMD/DIFF/RECEIPT 互指 sha8 与盘上一致；脚本常量钉 FROZEN `c5927f1b` / PIN `e01be34c` / ArchFROZEN `a5a9336d` / who_pays `4a074f0a` / 原审 `8d8ae2f3` / VOID `998171e1` / RUN_RECEIPT `c2a120f7` / ACK `dd8a7d2e` / VOID_OK `4096d401` / prev `108aba8f` / 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` / 叶36 HOLD `feaa5dbb`+`575e8276`。DIFF 头明示 NEW 并列、BASE UNCHANGED；非覆盖基盘。

## 2. 必审清单（B1 vs 基盘 `108aba8f` / VOID `998171e1` / FROZEN `c5927f1b`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **另票**：新文件并列；基盘字节未改；DIFF vs 基盘合理（年分块+instr 列块）；非覆盖基盘 | **PASS** | `diff -q` 两文件不同；基盘全长仍 `108aba8f…`；B1=`32605aca`；DIFF `6d61fd79` 头钉 NEW 并列 / BASE UNCHANGED；`PREV_SCRIPT_SHA8=108aba8f`；`B1_LOWMEM=True`；`SCRIPT_REL=…_b1_lowmem.py` |
| 2 | **低内存意图**：`_load_panel_imax` 年循环读 panel→瘦长 r_id→del+gc；IMAX instr 列块 step=256；分块 peak_proof；足以针对原 ABORT @`after_r_id` | **PASS_WITH_CONDITIONS** | 实现见 `_load_panel_imax`：years 2023–2026；`pq.read_table` cols+date filter；merge HI_LIQ；`r_id=(1+ret)/(1+ret_on)-1`；lean=`in_hiliq & r_id.notna` 三列；del+gc；`after_panel_year_*` / `after_r_id_year_*`；concat lean → pivot → instr chunk step=256 drop+gc → `after_imax_instr_chunk_*` / `after_panel_imax`。**CONDITIONS**：瘦长 concat / 全窗 pivot 后 `after_r_id` / 宽表残峰仍可能逼近 soft-split——静态可信、未真跑 peak_proof；本拍**不代改** |
| 3 | **rss=1500 禁抬**：硬 ABORT + peak_proof REQUIRED；CLI 抬帽是否硬 STOP；禁抬 split | **PASS_WITH_CONDITIONS** | `RSS_LIMIT_MB=1500`；`check_rss` Exit 94/95；dry `ban_raise_rss=true` + peak_proof 含分块标签；split=`0.85*C4`。**缺口（同原审）**：`main` **未**硬 STOP `--rss-limit-mb>1500` / 抬 `--c4-kb`/`--stop-kb`/`--hard-kb`——须签文硬钉禁抬（双保险）；本拍**不改脚本** |
| 4 | **契约未漂**：mask-only top_q=0.20；C3=B；C11≠叶24；soft-penalty 非 PRIMARY；HI_LIQ PRIMARY；FULLA STOP；overlap 硬拒 18/18v/27；forbid 首项 `4096d401` n=31 | **PASS** | dry pins：`primary_delivery=mask_only` / `top_q=0.2` / `c3_option=B` / `full_residual_e_id=false` / `soft_penalty_is_primary=false` / `LEAF24_MECHANISM_BAN` / `HARD_OVERLAP_TAGS=(leaf18,leaf18v,leaf27)` / forbid0=`4096d401` n=31（基盘 30 + 新增 VOID）；FULLA dry STOP exit2 |
| 5 | **dry/pyflakes**：本机复跑；禁 `--allow-real-data` | **PASS** | 见上轻量复跑；`research/__pycache__/leaf37*` ABSENT/已清 |
| 6 | **DIFF/COVER/CMD/RECEIPT** 互钉与脚本一致；EXECUTED=false | **PASS** | 五件互钉 MATCH；RECEIPT/CMD/COVER/dry 均 EXECUTED=false；拟真跑 CLI 钉 B1 脚本 + 新 `.ok` 名（未创建） |
| 7 | **禁项核**：未签.ok、未挂 QUIET、未代跑、未 RESTORED、未改基盘/FROZEN/PIN | **PASS** | live `.ok`=0；QUIET ABSENT；VOID `4096d401` 仅在 `_consumed`；基盘/FROZEN/PIN/Arch 审全长未变；本拍仅写本审票 |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| 瘦长 concat / 全窗 pivot 后 `after_r_id` 残峰仍可能逼近 soft-split | **中** | B1 针对原 peak@`after_r_id`；须真跑 peak_proof 验证分块有效；破 soft/hard → 停+上报；**禁抬帽**；本拍不代改 |
| CLI `--rss-limit-mb` / C4·stop·hard 可被抬（无叶34 式硬 STOP） | **管控** | dry 钉 `ban_raise_rss`；须签文硬钉 rss=1500 禁抬；破→停+上报 |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 脚本真跑硬 STOP + 签文双闸禁传 |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；启用须另窗+SW+style；不得抬作 PRIMARY |
| APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻 |
| RESTORED `4096d401`（VOID.ABORT_PEAK） | **硬禁** | forbid 首项；签窗禁复用任何 VOID/CONSUMED 路径 |

## 4. CONDITIONS（另窗签新 B1 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`32605aca` only**（全长 `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c`）；**禁**钉/跑基盘 `108aba8f` 当真跑票。
2. **禁 RESTORED `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票**：forbid∋**31** sha8（首项 `4096d401`）；禁复用 VOID/CONSUMED / 叶18/24/27/30–36 任一 `.ok`。
3. **真跑前主 MATCH**：B1 全长如上；dry-compile PASS；基盘 `108aba8f` UNCHANGED；FROZEN `c5927f1b` / PIN `e01be34c` / ArchFROZEN `a5a9336d` / who_pays `4a074f0a` / VOID `998171e1` / 本审回执；叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` 不回撤；叶36 HOLD `feaa5dbb`/`575e8276` 不复开。
4. **签文硬钉 rss=1500 禁抬**：PRIMARY CLI **不得**传 `--rss-limit-mb`>`1500` 或抬 `--c4-kb`/`--stop-kb`/`--hard-kb`；**禁**放宽 split；peak_proof REQUIRED（`after_mask` / `after_panel_year_*` / `after_r_id_year_*` / `after_r_id` / `after_imax_instr_chunk_*` / `after_panel_imax` / `after_mask_cs_rebal_*` / `after_daily_concat`）；破 soft/hard → 停+上报；真跑须验证分块对原 ABORT 点有效。
5. **C7 签文硬钉**：真跑**必须**写并消费 overlap JSON（硬拒 18/18v/27；披露 24/34/35/36）；Jaccard≥0.7 → 硬拒；缺硬文件→PIN_GAP；签文 **禁** `--no-overlap-report`。
6. **C3 / PRIMARY 纪律**：`IMAX_proxy` C3=B；`full_residual_e_id=false`；持续 APPROX；禁静默升全 e_id；判决=HILIQ **mask-only** top_q=0.20；FULLA 仅 `--also-fulla-research`；soft-penalty 不得作 PRIMARY；C11≠叶24 主 α。
7. **PRIMARY CLI 钉**（占位；现不可跑；无 `--no-overlap-report`；无抬 rss）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_B1_OK> --out output/ai_factory/_leaf37_imax_lottery/<ET_TS>/`
8. sampler `/tmp/quantlab_leaf37_imax_lottery_b1_*`；out `_leaf37_imax_lottery/<ET_TS>/`；Arch **不代跑**；可挂 leaf37 自有 QUIET（当前 QUIET **ABSENT**）。
9. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻 · KEEP 不解阻。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新 B1 / RESTORED `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** B1 脚本 `32605aca` / 基盘 `108aba8f` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN / Arch 审 / VOID
- **未** `--allow-real-data` / **未**代跑 X2 / **未** Book-Smoke（仅 `py_compile` + `pyflakes` + dry）；`research/__pycache__/leaf37*` **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**改 top_q / mask-only / 升 e_id
- **未改** 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc`；**未回撤** 叶36 HOLD；**未**落地 `research/leaf36*`；**禁复开 inquiry**
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
B1 脚本 32605aca（本审 PASS_WITH_CONDITIONS · prev 108aba8f UNCHANGED · VOID 998171e1 · FROZEN c5927f1b / PIN e01be34c）
  → 请主另排独立 X2 签窗（新 .ok；钉 32605aca only；禁 RESTORED 4096d401+eb70eef4+00eec671+10927bd9+25ae4572+旧票）
      → AI prelaunch→execute（无 --no-overlap-report；rss=1500 禁抬；peak_proof 含 year/instr 分块；C3=B；mask-only PRIMARY；C11≠leaf24）
          → Arch CONSUME（≠X2 ACCEPT；叶36 HOLD 不复开；验 peak_proof 分块有效）
```

**本拍不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| B1 脚本 | **`32605aca` MATCH** |
| 基盘 | **`108aba8f` UNCHANGED** |
| COVER / CMD / DIFF / RECEIPT | **`a4bfa39d`** / **`286e2104`** / **`6d61fd79`** / **`46f4192d`** MATCH |
| VOID / FROZEN / PIN / ArchFROZEN / who_pays / 原审 | **`998171e1`** / **`c5927f1b`** / **`e01be34c`** / **`a5a9336d`** / **`4a074f0a`** / **`8d8ae2f3`** MATCH |
| forbid | 首项 **`4096d401`** · n=**31** |
| 叶33 / 叶35 / 叶34 | **`afbbe7e7` UNCHANGED** / **`434ff42c` UNCHANGED** / **`482009dc` UNCHANGED** |
| 叶36 HOLD | **`feaa5dbb`/`575e8276`** 不回撤 |
| dry-compile / py_compile / pyflakes | **PASS**（exit0 / PASS / CLEAN）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `32605aca` only；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | B1/`32605aca` · prev/`108aba8f` · COVER/`a4bfa39d` · CMD/`286e2104` · DIFF/`6d61fd79` · RECEIPT/`46f4192d` · VOID/`998171e1` · FROZEN/`c5927f1b` · PIN/`e01be34c` · ArchFROZEN/`a5a9336d` · who_pays/`4a074f0a` · 原审/`8d8ae2f3` |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见父回报）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑.
