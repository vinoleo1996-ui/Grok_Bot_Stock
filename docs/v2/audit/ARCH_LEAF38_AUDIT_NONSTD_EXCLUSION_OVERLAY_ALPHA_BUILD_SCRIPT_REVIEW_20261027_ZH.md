# Arch 审阅：叶38 非标审计意见剔除 overlay 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T21:14:08-04:00`（America/New_York；墙钟 `2026-10-27 21:14 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`ce0eb2ce`** · Arch FROZEN 审 **`01753ff4`**（PASS_WC）· who_pays 审 **`acba0865`** · LAND RECEIPT **`d157429b`** · who **`16c1f70b`** · COVER **`7c3b8691`** · COUNT 盘上 **`e82aefa2`** · COUNT脚本（非正式）**`ba34da2a`** · JSON **`2b3babb5`** · dig **`fa973826`** · FROZEN RECEIPT **`bb8051bd`** · HI_LIQ **`c5433e80`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / `--allow-real-data` 真构建（仅 `py_compile` + `pyflakes` + `--dry-compile-only`）；**不改**脚本/FROZEN/RECEIPT/上游件；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+；叶37 HOLD CLOSED 不回撤、禁复开；旁线 fund recount **不混**；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 · 叶38 LAND_SCRIPT READY MATCH（脚本 `d5cf50bb` / LAND `d157429b`）→ Arch 另窗只审脚本 GO |
| 轻量复跑 | `py_compile` **PASS**；`python -m pyflakes` **CLEAN exit0**；`--dry-compile-only` exit **0**（`script_sha8=d5cf50bb` / FROZEN=`ce0eb2ce` / ArchFROZEN=`01753ff4` / who_pays=`acba0865` / PRIMARY_DELIVERY=`mask_only` / rss=1500 / soft_penalty_is_primary=false / §6.1 全套 true / peak_proof_le_1500_required / ban_raise_rss / executed=false）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`d5cf50bb` MATCH**：mechanism=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；PRIMARY=**mask-only**（非标审计意见 `is_non_standard=True`→mask=0；可算其余 mask=1；不可算不填假 0）；soft-penalty **默认关、非 PRIMARY**；PIT=`available_at→T1` 键=`ts_code`；厚度 median≥**30** ∧ frac(≥10)≥**0.60** ∧ zero_frac≤**0.50**（勿盲抄 300）；Jaccard 硬拒 **>0.5** vs negevent **或** 叶36；披露 vs 34/35/37；窗 2024-06-03→2026-10-09；PRIMARY=HILIQ；`--universe FULLA` STOP；**§6.1 压峰全套落地**（分进程 Jaccard / 流式年块 HI_LIQ / categorical·int id / OMP·MKL·NUMEXPR=1 / Exit **94·95** / **rss=1500 禁抬**（真路径+worker 硬 STOP）/ **peak_proof≤1500 REQUIRED**）；forbid∋`57ab9096`+`b5be1164`+`4096d401`+（33 项）；COUNT `ba34da2a` **≠** 正式脚本；未自签 `.ok`；LAND EXECUTED=false；dry/pyflakes PASS；叶37 HOLD CLOSED；live `.ok`/QUIET **ABSENT**。**本拍不签**；请主另排独立 X2 签窗（钉 **`d5cf50bb` only**）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py` | `d5cf50bb` | `d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263` | **MATCH** · 1483 行 |
| LAND RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_LAND_SCRIPT_RECEIPT_20261027_ZH.md` | `d157429b` | `d157429b14d8f4a9fcdcedde8df62d3be84828275171e4f80a529114032f843f` | **MATCH** · EXECUTED=false |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `ce0eb2ce` | `ce0eb2ce9486778e229d2722a647b6fb37e90810df2ac9f1530054d8040b93ed` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `01753ff4` | `01753ff4434abcbaba0cbe77def38e67763836b3f613be7ee09f05594e9839a5` | **MATCH** · PASS_WC |
| who | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `16c1f70b` | `16c1f70bc96b0c7c3d83cfb8493c42dc9ea554e1a2a45f978e78fbf0e573729c` | **MATCH** |
| COVER | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `7c3b8691` | `7c3b86915440d3a440be5bde10313cfe7f49360199ed7f70617b572d19f71fea` | **MATCH** |
| COUNT 盘上 | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `e82aefa2` | `e82aefa24a158719e46acafa3933a33e2b78ca6ea674284f138d2b407087a20b` | **MATCH** |
| COUNT脚本（非正式） | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `ba34da2a` | `ba34da2a6da73fc3736894d99548fee85a3ee74b2ea1722b51d8da3f164be296` | **MATCH** · **≠**正式脚本 |
| JSON | `output/ai_factory/leaf38_audit_nonstd_exclusion_count_20261027.json` | `2b3babb5` | `2b3babb5d83947d27b61306b9702a43f6093b0b0565ccea3d5e19d6431462750` | **MATCH** |
| dig | `output/d1/DIG_FACTOR_20261027_2026ET.md` | `fa973826` | `fa973826c86be2d7e555d5abd30da4c32a3f5c6540b15e33e08f876eeb529101` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `acba0865` | `acba08650a034b7f40773a5a19923d529dcee0c0cabc6997ddee63501fe0caf2` | **MATCH** |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `bb8051bd` | `bb8051bd00d5b7ff30a017eaced668d26b3c60de8f1fb1139eedba49b445efeb` | **MATCH** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | **MATCH** |
| 叶34 正式（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | 前8 MATCH | **UNCHANGED** |
| 叶35 正式（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | 前8 MATCH | **UNCHANGED** |
| 叶37 基盘（只读） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build.py` | `108aba8f` | 前8 MATCH | **UNCHANGED** · 禁复跑 |
| 叶37 B1（只读） | `research/leaf37_imax_lottery_exclusion_overlay_alpha_build_b1_lowmem.py` | `32605aca` | 前8 MATCH | **只读骨架** · 禁复用 IMAX |
| 叶36 HOLD WHO（只读） | `docs/v2/audit/AI_LEAF36_INQUIRY_LETTER_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `feaa5dbb` | 前8 MATCH | **不回撤** |
| 叶36 HOLD JSON（只读） | `output/ai_factory/leaf36_inquiry_letter_exclusion_count_20261027.json` | `575e8276` | 前8 MATCH | **不回撤** |
| `research/leaf38*` | 仅正式脚本 1 件 | 1 | 1 | **MATCH** |
| live leaf38 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF38*` / `*.ok` | 0 | 0 | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |

哈希闭环：脚本常量钉 FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays `acba0865` / COVER `7c3b8691` / COUNT盘 `e82aefa2` / COUNT脚本 `ba34da2a`（NOT formal）/ JSON `2b3babb5` / dig `fa973826` / HI_LIQ `c5433e80` / FROZEN RECEIPT `bb8051bd` 与盘上一致；dry 打印 `script_sha8=d5cf50bb` 与本机现算 MATCH。COUNT 脚本 `ba34da2a` **≠** 正式脚本 `d5cf50bb`。

## 2. 必审清单（脚本 vs FROZEN `ce0eb2ce` §6 / §6.1 / C1–C13）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** 正式脚本落地；COUNT 非正式 | **PASS** | `research/leaf38*` 仅 `…_alpha_build.py`；`COUNT_SCRIPT_SHA8=ba34da2a` 明示 NOT formal；dry `count_script_sha8_NOT_formal` |
| 2 | **C9 / §6.1 压峰全套**（首要） | **PASS** | (1) `_run_jaccard_subprocess` + `--jaccard-worker-only`；(2) `_load_hiliq_mask_by_chunks(year_chunk=True)`+del/gc；(3) categorical + `_instrument_vocab` int id + 磁盘 `(date,inst_id) int32` npy；(4) `OMP/MKL/OPENBLAS/NUMEXPR/VECLIB=1` + `enforce_single_thread`；(5) `check_rss` → Exit **94**/ **95**；`rss_limit_mb>1500` 真路径/worker **硬 STOP**；(6) `final_peak_proof` / `peak_proof_le_1500`；失败 return 94 禁 `.ok` |
| 3 | **rss=1500 禁抬** + peak_proof≤1500 REQUIRED | **PASS_WITH_CONDITIONS** | `RSS_LIMIT_MB=1500`；真路径+jaccard worker 禁抬 `rss_limit_mb`；dry 钉 `ban_raise_rss`+`peak_proof_required` 标签。**缺口**：CLI `--c4-kb`/`--hard-kb`/`--stop-kb` 仍可抬（无常量硬 STOP）——须签文硬钉双保险；本拍**不改脚本** |
| 4 | **PRIMARY=mask-only ≠主叶**；soft-penalty 非 PRIMARY | **PASS** | `PRIMARY_DELIVERY=mask_only`；`SOFT_PENALTY_DEFAULT=False`；dry `soft_penalty_is_primary=false`；`--enable-soft-penalty` → 真路径 PIN_GAP return 2；C11 钉禁完整多空审计 α |
| 5 | **C3** PIT `available_at→T1`；非标剔除；键=`ts_code`；禁偷看 | **PASS** | `t1_of` + `_load_audit_and_build_excl`；`C3_FORMULA_PIN`；最新 `is_non_standard=True`→excl；禁标准无保留当剔除（文钉） |
| 6 | **C5** 厚度 median≥30 ∧ frac≥10≥0.60 ∧ zero_frac≤0.50 | **PASS** | `COV_MEDIAN_MIN=30` / `FRAC_GE10_MIN=0.60` / `ZERO_FRAC_MAX=0.50`；`_excl_thickness`；失败 return 3；禁盲抄 300 |
| 7 | **C7** Jaccard 硬拒 >0.5 vs negevent/叶36；披露 34/35/37 | **PASS_WITH_CONDITIONS** | `JACCARD_HARD=0.5`；`HARD_OVERLAP_TAGS`/`DISCLOSE_OVERLAP_TAGS`；真路径禁 `--no-overlap-report`。**缺口**：leaf36 pairs 未预落 → PIN_GAP 且 `max=None` 时**不触发**硬拒——签窗须预落/重建，**禁**把 PIN_GAP 当硬过 |
| 8 | **C6** HI_LIQ PRIMARY；FULLA 不得作 PRIMARY | **PASS** | dry/run `--universe FULLA` STOP exit2；`--also-fulla-research` 仅 dry 钉（真路径未接线 FULLA 产出——可接受；PRIMARY 仍 HILIQ） |
| 9 | **C8** forbid∋`57ab9096`+`b5be1164`+`4096d401`+；禁自开 `.ok` | **PASS** | `FORBID_OK_SHA8` **33** 项含主令三点名+叶37 RESTORED 串；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；**无写 `.ok` 逻辑**（`ban_self_sign_ok`） |
| 10 | **C10** 叶37 HOLD CLOSED；旁线 fund 不混 | **PASS** | 常量钉禁复跑 `015e6f06`/`32605aca`/`108aba8f`；`ban_reopen_leaf36_inquiry`；`ban_fund_portfolio_mix`；本拍未触 fund recount |
| 11 | **C11/C12/C13** overlay≠主叶；COUNT≠ACCEPT；KEEP≠ACCEPT | **PASS** | dry/meta 明示；decay 仅 PIN 不执行门；COUNT APPROX 不解阻 |
| 12 | dry/pyflakes；默认 dry；未自签；LAND EXECUTED=false | **PASS** | 本机复跑见上；默认无 flag STOP exit2；`research/__pycache__/leaf38*` 已清理；LAND `EXECUTED=false`；live `.ok`/QUIET ABSENT |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| CLI `--c4-kb`/`--hard-kb`/`--stop-kb` 可被抬（`rss_limit_mb` 真路径已硬 STOP） | **管控** | dry 钉 `ban_raise_rss`；须签文硬钉禁抬 c4/stop/hard；破→停+上报；本拍不改文 |
| dry 路径 `--rss-limit-mb>1500` 仍 exit0（仅打印常量 1500） | **低** | 真路径+worker 已硬 STOP；签窗禁传抬帽 |
| leaf36 pairs 未预落 → PIN_GAP；`max=None` 不硬拒 | **管控** | 签窗须预落 `leaf36_pairs.npy` 或完整重建；**禁** PIN_GAP 当硬过 |
| `--no-overlap-report` CLI 仍在（真跑已硬 STOP） | **管控** | 靠脚本硬 STOP + 签文双闸 |
| HI_LIQ「年块」仍整表读后按年过滤（非 row-group 流） | **中** | 有 del+gc+rss 检查；须 peak_proof；破→停；**禁抬帽** |
| `--also-fulla-research` 真路径未接线产出 | **低** | PRIMARY=HILIQ 不受影响；若另窗 FULLA 须补钉 |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；启用即 PIN_GAP；不得抬作 PRIMARY |
| COUNT peak≈1584 WATCH / gate_pass | **披露** | ≠X2 ACCEPT（C12）；须压峰+peak_proof≤1500 |
| APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻 |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`d5cf50bb` only**（全长 `d5cf50bb3a7f5755de323c772771a222f1aaa8c535436d091040560b439df263`）。
2. **禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+旧票**：forbid∋33 sha8；禁复用叶18/24/27/30–37 任一 `.ok`；禁复用 VOID/CONSUMED 路径；禁复跑叶37 `015e6f06`/`32605aca`/`108aba8f`。
3. **真跑前主 MATCH**：script 全长如上；dry-compile PASS；FROZEN `ce0eb2ce` / ArchFROZEN `01753ff4` / who_pays `acba0865` / LAND `d157429b` / 本审回执；叶34 `482009dc` / 叶35 `434ff42c` / 叶37 `108aba8f` 不回撤；叶36 HOLD `feaa5dbb`/`575e8276` 不复开；旁线 fund 不混。
4. **签文硬钉 rss=1500 禁抬**：PRIMARY CLI **不得**传 `--rss-limit-mb`>`1500` 或抬 `--c4-kb`/`--stop-kb`/`--hard-kb`；peak_proof REQUIRED（含 `after_hiliq_chunk_*` / `after_mask_by` / `after_audit_excl` / `after_mask_expand` / `after_jaccard_subprocess` / `final_peak_proof`）；破 soft/hard → 停+上报；**无 peak_proof≤1500 不得申 `.ok`**。
5. **C7 签文硬钉**：真跑**必须**写并消费 overlap JSON；Jaccard>0.5 vs negevent **或** 叶36 → 硬拒；leaf36 pairs **须预落或完整重建**（PIN_GAP ≠ 硬过）；披露 34/35/37；签文 **禁** `--no-overlap-report`。
6. **PRIMARY 纪律**：判决=HILIQ **mask-only**；PIT `available_at→T1`；厚度阈不改；soft-penalty 启用须另窗+SW+style，**不得**作 PRIMARY；C11≠完整多空审计 α 主叶。
7. **PRIMARY CLI 钉**（占位；现不可跑；无 `--no-overlap-report`；无抬 rss）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf38_audit_nonstd_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf38_audit_nonstd_exclusion/<ET_TS>/`
8. sampler `/tmp/quantlab_leaf38_audit_nonstd_*`；out `_leaf38_audit_nonstd_exclusion/<ET_TS>/`；Arch **不代跑**；可挂 leaf38 自有 QUIET（当前 QUIET **ABSENT**）。
9. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻 · KEEP 不解阻。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶38 / RESTORED `57ab9096`+`b5be1164`+`4096d401`+旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** 脚本 `d5cf50bb` / LAND / FROZEN / Arch 审 / who / COVER / COUNT / JSON
- **未** `--allow-real-data` / **未**代跑 X2 / **未** Book-Smoke（仅 `py_compile` + `pyflakes` + dry）；`research/__pycache__/leaf38*` **已清理**
- **未** RESTORED；**未**抬 rss；**未**改厚度阈 / mask-only
- **未改** 叶34 `482009dc` / 叶35 `434ff42c` / 叶37 `108aba8f`；**未回撤** 叶37 HOLD CLOSED / 叶36 HOLD；**禁复开** inquiry / IMAX
- **未混** 旁线 fund recount
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 d5cf50bb（本审 PASS_WITH_CONDITIONS · FROZEN ce0eb2ce / ArchFROZEN 01753ff4 / who_pays acba0865 / LAND d157429b）
  → 请主另排独立 X2 签窗（新 .ok；钉 d5cf50bb only；禁 RESTORED 57ab9096+b5be1164+4096d401+）
      → AI prelaunch→execute（无 --no-overlap-report；rss=1500 禁抬；peak_proof≤1500；§6.1；mask-only PRIMARY；leaf36 pairs 预落；C11≠主叶）
          → Arch CONSUME（≠X2 ACCEPT；叶37 HOLD CLOSED 不复开；旁线 fund 不混）
```

**本拍不签 / 不挂 / 不代跑**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`d5cf50bb` MATCH** |
| LAND / FROZEN / ArchFROZEN / who_pays | **`d157429b`** / **`ce0eb2ce`** / **`01753ff4`** / **`acba0865`** MATCH |
| who / COVER / COUNT盘 / COUNT脚本 / JSON / dig / HI_LIQ | **`16c1f70b`** / **`7c3b8691`** / **`e82aefa2`** / **`ba34da2a`≠正式** / **`2b3babb5`** / **`fa973826`** / **`c5433e80`** MATCH |
| §6.1 / C9 | **全套落地**（分进程/流式/降表示/单线程/Exit94·95/rss=1500禁抬/peak_proof REQUIRED） |
| 叶34 / 叶35 / 叶37 | **`482009dc` UNCHANGED** / **`434ff42c` UNCHANGED** / **`108aba8f` UNCHANGED**（禁复跑） |
| 叶37 HOLD / 叶36 HOLD | **CLOSED 不复开** / **`feaa5dbb`/`575e8276` 不回撤** |
| dry-compile / py_compile / pyflakes | **PASS**（exit0 / PASS / CLEAN）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `d5cf50bb` only；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 上游钉 | script/`d5cf50bb` · LAND/`d157429b` · FROZEN/`ce0eb2ce` · ArchFROZEN/`01753ff4` · who_pays/`acba0865` · who/`16c1f70b` · COVER/`7c3b8691` · COUNT/`e82aefa2` · JSON/`2b3babb5` · dig/`fa973826` · HI_LIQ/`c5433e80` |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见父回报）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑 · 旁线未混.
