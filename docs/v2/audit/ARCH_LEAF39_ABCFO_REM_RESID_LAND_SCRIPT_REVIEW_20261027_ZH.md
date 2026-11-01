# Arch 审阅：叶39 ABCFO / 真实盈余管理残差 α 正式构建脚本（LAND_SCRIPT；只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-28T00:20:00-04:00`（America/New_York；墙钟 `2026-10-28 00:20 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本审回执盘上 sha8 | 落盘后以本机 `sha256sum` 为准（见 §8 / TEAM_STATE；文内若填入自算不一致则**采盘上**） |
| 对照 | 脚本 **`e99376dd`** · LAND RECEIPT **`04f6c7bb`** · FROZEN **`150d1a28`** · ArchFROZEN **`b51a59a0`** · FROZEN RECEIPT **`507f09f1`** · ArchDRAFT **`4a1b4dd0`** · DRAFT **`542138d6`** · DRAFT RECEIPT **`691bbc14`** · COUNT **`d0d11598`** · COUNT脚本 **`20313ba3`** · dig **`440410de`** · HI_LIQ **`c5433e80`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** X2 / Book-Smoke / 全量 α / 计数（仅 `py_compile` + `pyflakes` + `--dry-compile-only` / `--help` / 无授权 STOP）；**不改**脚本/FROZEN/RECEIPT/上游件；**不自开 X2**；禁 RESTORED `f08ce32c`/`335635dd`；**不混** fund MDD HOLD（`ba7609af`/`fbc1bd9a`/`335635dd`）/ 叶38（`c01c2034`/`5f694370`）；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 · 叶39 LAND_SCRIPT READY MATCH（脚本 `e99376dd` / RECEIPT `04f6c7bb`；上游 FROZEN `150d1a28` / ArchFROZEN `b51a59a0`）→ Arch **另窗只审脚本** |
| 轻量复跑 | `py_compile` **PASS**；`python -m pyflakes` **CLEAN exit0**；`--dry-compile-only` exit **0**（`script_sha8=e99376dd` / FROZEN=`150d1a28` / ArchFROZEN=`b51a59a0` / PRIMARY=`residual_alpha_vector` / rss=1500 / peak_proof REQUIRED / EXECUTED_full_alpha=false）；`--help` exit **0**；无授权 flag → STOP exit **2**；`--rss-limit-mb 1600` → STOP exit **2**；`--universe FULLA --dry-compile-only` → STOP exit **2**（PRIMARY=HILIQ） |

## 0. 一句话

脚本 **`e99376dd` MATCH**（1554 行）：mechanism=`g1g5_ashare_abcfo_rem_resid_v1`；**PRIMARY=日度残差 α 向量 parquet**（C8；**非** Top-N；**非** exclusion mask）；公式=YTD→单季后 CFO/A ~ 1/A+S/A+ΔS/A（**C2(a) 再平衡日截面 SW L1 OLS APPROX；不升年×行业面板；未重跑 COUNT `d0d11598`**）→ ABCFO=ε → `α ∝ −ε` → SW L1 demean + vs logmv OLS；HI_LIQ + 银/地/非银硬掩码；窗 2024-06-03→2026-10-09；再平衡20；成本30bp（评价）；硬闸 vs 叶19/25/30 Jaccard∨ρ_excess>0.5；**C2(b)** ρ_excess 路径已预留（`--skip-rho-excess` 默认 True；`--no-skip-rho-excess`；清 skip 后仍诚实 `PIN_GAP_RETURNS_PANEL_NOT_WIRED` — **正式估须 X2 前接线**）；**C3** 叶34 Jaccard=**PIN_GAP**（CLI `--leaf34-jaccard` 已预留；硬拒 0.5；禁事后改 PRIMARY）；**C4** 禁自签/自开；FORBID∋`f08ce32c`/`335635dd`/`c01c2034`/`5f694370`/`ba7609af`/`fbc1bd9a`+；rss≤1500 禁抬 + peak_proof REQUIRED + Exit 94·95；**C5** CRR_MOD2/IO 不升 PRIMARY；**C9** COUNT≠X2 ACCEPT；§压峰（年块 HI_LIQ / logmv 懒加载 / 单线程 / del+gc）可见；dry/pyflakes PASS；叶39 live `.ok` **ABSENT**；QUIET **ABSENT**；LAND `EXECUTED_full_alpha=false`。**本拍不签**；**建议主裁：排独立 X2 签窗**（钉 `e99376dd` only；须 peak_proof + 正式 ρ_excess + 叶34 Jaccard + decay KEEP；KEEP≠ACCEPT）。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf39_abcfo_rem_resid_alpha_build.py` | `e99376dd` | `e99376dd71ce889ad7c16e5b6e6e87d3f2058f8f3b1f1e93880bd260eea8806b` | **MATCH** · 1554 行 |
| LAND RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_LAND_SCRIPT_RECEIPT_20261027_ZH.md` | `04f6c7bb` | `04f6c7bbd00a78736a6e9c16a41e7204ef3bffc3d79b6da511c2c69030ac5373` | **MATCH** · EXECUTED_full_alpha=false |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_20261027_ZH.md` | `150d1a28` | `150d1a2827c1284d6c1c890109a7a1e32ea0fb07925cc29959676b5816818d0f` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `b51a59a0` | `b51a59a0207c5d9767cabbe04ac73ed709a839bda830dea62c3d8b376d02fc24` | **MATCH** · PASS_WC |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `507f09f1` | `507f09f19f8abbc3c8f1d44d765a724de4cc1e61e3f9811bfa1ed65d7d6b5c9a` | **MATCH** |
| Arch who_pays DRAFT 审 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `4a1b4dd0` | `4a1b4dd0ec9992a63466e31323828083dcd548663605a4c0eb4b99c1b609c06b` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `542138d6` | `542138d6893f820d98f9a5db91a3b99e55953829815226ce49a0f8b1a42e5882` | **MATCH** |
| DRAFT RECEIPT | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_WHO_PAYS_DRAFT_RECEIPT_20261027_ZH.md` | `691bbc14` | `691bbc148780d88205a1f01996b2e6b662305d0bd868c652cb071aa70f6a52f9` | **MATCH** |
| COUNT JSON | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_20261027.json` | `d0d11598` | `d0d115989805cd169ca9435de14a3795c18d2310366427170fb3a39e54d6abf8` | **MATCH** |
| COUNT SCRIPT（非正式） | `docs/v2/audit/AI_LEAF39_ABCFO_REM_RESID_COUNT_GATE_SCRIPT_20261027.py` | `20313ba3` | `20313ba3ea14ddaa9d328fa5177f33b15194d93b2135aec952395a252c0e8587` | **MATCH** · **≠**正式脚本 |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_2330ET.md` | `440410de` | `440410de9b9a0e005d4c8021f93c26d120393c9109c645dbf92d7aa940add0d6` | **MATCH**；自称 `87f65bbe` **勿采** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | `c5433e80` | `c5433e80a74ac3acc0cd5a52d57fdd0bda5ed578fb86fb98cbd652ccb9f1b9af` | **MATCH** |
| 叶34 正式（只读） | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | 前8 MATCH | **UNCHANGED** · C3 只读 |
| `research/leaf39*` | 仅正式脚本 1 件 | 1 | 1 | **MATCH** |
| 叶39 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF39*` | ABSENT | ABSENT | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| fund MDD HOLD CLOSED | Arch / CONSUME / `.ok` | `ba7609af` / `fbc1bd9a` / `335635dd` | 本拍未触 | **旁线不混**；禁 RESTORED |
| 叶38 旁线 | — | `c01c2034` / `5f694370` | 本拍未触 | **不混** |
| 禁 RESTORED | fund | `f08ce32c` (+`335635dd`) | FORBID 入钉；未触 | **禁触** |

哈希闭环：脚本常量钉 FROZEN `150d1a28` / ArchFROZEN `b51a59a0` / FROZEN RECEIPT `507f09f1` / ArchDRAFT `4a1b4dd0` / DRAFT `542138d6` / DRAFT RECEIPT `691bbc14` / COUNT `d0d11598` / COUNT脚本 `20313ba3`（NOT formal）/ dig `440410de` / HI_LIQ `c5433e80` 与盘上一致；dry 打印 `script_sha8=e99376dd` 与本机现算 MATCH。COUNT 脚本 `20313ba3` **≠** 正式脚本 `e99376dd`。文内自称 dig `87f65bbe` **勿采**。

对照模板：`docs/v2/audit/ARCH_LEAF38_AUDIT_NONSTD_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md`；上游 ArchFROZEN `b51a59a0`。

## 2. 必审清单（脚本 vs FROZEN `150d1a28` COND C2–C5/C8/C9）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **pins_match** 全钉 | **PASS** | §1 表：脚本/RECEIPT/FROZEN/ArchFROZEN/FROZEN RECEIPT + 上游 DRAFT/ArchDRAFT/COUNT/脚本/dig/HI_LIQ **全 MATCH** |
| 2 | **C2(a)** 截面 SW L1 OLS APPROX；不升面板；未重跑计数 | **PASS** | `C2A_PIN`；`ols_resid_sw` 按 `sw_code` groupby 截面 lstsq；n<25 市场 fallback；dry `approx_note` 明示 NOT year×industry panel；COUNT `d0d11598` 未重跑 |
| 3 | **C2(b)** ρ_excess 路径预留；正式估@X2 前 | **PASS_WITH_CONDITIONS** | `formal_rho_excess_stub` + `--skip-rho-excess`/`--no-skip-rho-excess`；默认 skip=True→`SKIPPED_LAND_DEFAULT`；清 skip→诚实 `PIN_GAP_RETURNS_PANEL_NOT_WIRED`（returns 钩未接线防 PnL 选阈）。**余项**：X2 前须接线 excess-return 面板并清 skip；禁把 Spearman 当 ρ_excess；硬拒仍 >0.5 |
| 4 | **C3** 叶34 Jaccard=PIN_GAP；CLI 预留；硬拒 0.5；勿改 PRIMARY | **PASS_WITH_CONDITIONS** | `--leaf34-jaccard` 默认 OFF→`PIN_NOT_REQUESTED`；开则估 top20 α vs leaf34 excl；硬拒 0.5；`ban_posthoc_PRIMARY_rewrite`；缺 mask→`PIN_GAP_LEAF34_MASK_MISSING`（≠硬过）。**余项**：最迟 X2 前补估；PIN_GAP≠硬过 |
| 5 | **C4** 禁自签/自开 BS·X2；不混旁线；rss≤1500 + peak_proof | **PASS_WITH_CONDITIONS** | 无写 `.ok` 逻辑；真跑须现存 `--arch-ok-path`∉FORBID；`--rss-limit-mb>1500` 主路径硬 STOP；`check_rss`→Exit 94/95；peak_proof 标签列表 + `final_peak_proof`。**缺口**：CLI `--c4-kb`/`--hard-kb`/`--stop-kb`/`--split-kb` 仍可抬（无常量硬 STOP）——须签文硬钉双保险；本拍**不改脚本** |
| 6 | **C5** CRR_MOD2/IO 不升 PRIMARY | **PASS** | dry `ban_raise_crr_mod2_or_io_to_primary=true`；`arch_conditions.C5`；PRIMARY 钉残差 α |
| 7 | **C8** PRIMARY=残差 α 向量（非 mask/非 Top-N） | **PASS** | `PRIMARY_DELIVERY=residual_alpha_vector`；出列 `trade_date,ts_code,alpha,abcfo,raw`；dry 明示 NOT Top-N / NOT mask |
| 8 | **C9** 轻量计数/本脚本 ≠X2 ACCEPT | **PASS** | `C9_PIN`；dry `x2_accept=false`；`count_script_sha8_NOT_formal`；KEEP 不解阻；本审 ≠ACCEPT |
| 9 | **ABSENT 核** 叶39 `.ok`/QUIET；EXECUTED_full_alpha=false；未改主干 | **PASS** | live `.ok`=0；QUIET ABSENT；LAND RECEIPT EXECUTED_full_alpha=false；上游 FROZEN/DRAFT/COUNT sha 未漂；未改脚本字节（本拍只读） |
| 10 | **静态质量** py_compile/pyflakes/dry/help；rss 护栏 | **PASS** | 本机复跑见上；默认无授权 STOP；FULLA dry STOP；rss 抬帽 STOP；pgrep 重活 empty |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| C2(b) returns 面板未接线（清 skip 仍 PIN_GAP） | **管控** | 诚实缺口；X2 前须接线；禁 Spearman 冒充 ρ_excess；禁 PIN_GAP 当硬过 |
| C3 叶34 Jaccard 仍 PIN_GAP（本拍 dry 未估） | **管控** | CLI 已预留；最迟 X2 前补估；缺 mask→PIN_GAP≠硬过；禁事后改 PRIMARY |
| CLI `--c4-kb`/`--hard-kb`/`--stop-kb`/`--split-kb` 可被抬 | **管控** | `--rss-limit-mb>1500` 已硬 STOP；签文须禁抬 c4/stop/hard；破→停+上报 |
| HI_LIQ「年块」仍整表过滤风格依赖实现 | **中** | 有 del+gc+rss 检查+peak_proof；破→停；禁抬帽 |
| C3 Jaccard 定义= top20 α ∩ leaf34 excl | **披露** | 残差 α 非 mask 交付下合理；签窗披露定义；硬拒 0.5 |
| COUNT gate_pass / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻（C9） |
| 旁线 fund MDD / 叶38 混入签窗 | **管控** | FORBID 已含；签文再钉不混 |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前；开放余项）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF39_ABCFO_REM_RESID_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`e99376dd` only**（全长 `e99376dd71ce889ad7c16e5b6e6e87d3f2058f8f3b1f1e93880bd260eea8806b`）。
2. **禁 RESTORED `f08ce32c`/`335635dd`+旧票**：FORBID∋fund/叶38/VOID 串；禁复用旁线 `.ok`；**不混** fund MDD HOLD（`ba7609af`/`fbc1bd9a`/`335635dd`）；**不混**叶38（`c01c2034`/`5f694370`）。
3. **真跑前主 MATCH**：script 全长如上；dry-compile PASS；FROZEN `150d1a28` / ArchFROZEN `b51a59a0` / LAND RECEIPT `04f6c7bb` / 本审回执；COUNT `d0d11598` 不解阻。
4. **签文硬钉 rss=1500 禁抬**：PRIMARY CLI **不得**传 `--rss-limit-mb`>`1500` 或抬 `--c4-kb`/`--stop-kb`/`--hard-kb`/`--split-kb`；peak_proof REQUIRED（含 `after_fundamentals` / `after_hiliq_chunk_*` / `after_rebal_ols_*` / `after_logmv_rebal_*` / `after_overlap_gate` / `after_leaf34_jaccard` / `final_peak_proof`）；破 soft/hard → 停+上报；**无 peak_proof≤1500 不得申 `.ok`**。
5. **C2(b) 签文硬钉**：真跑前须 `--no-skip-rho-excess` **且** excess-return 面板已接线得正式 ρ_excess；Spearman 仅代理；ρ_excess∨Jaccard>0.5 vs 叶19/25/30 → 硬拒；PIN_GAP≠硬过。
6. **C3 签文硬钉**：真跑须 `--leaf34-jaccard`（或等价预估附录）；硬拒 0.5；缺 mask/PIN_GAP≠硬过；**禁止**事后改 PRIMARY 救闸。
7. **PRIMARY 纪律**：判决=HILIQ **残差 α 向量**；PIT `available_at≤t`；银/地/非银+HI_LIQ；C5 禁升 CRR_MOD2/IO；C8≠mask/≠Top-N；C9 COUNT/本脚本≠ACCEPT；KEEP≠ACCEPT。
8. **PRIMARY CLI 钉**（占位；现不可跑；无抬 rss；X2 前开 ρ_excess+叶34）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf39_abcfo_rem_resid_alpha_build.py --universe HILIQ --window x2 --window-start 2024-06-03 --window-end 2026-10-09 --allow-real-data --arch-ok-path <NEW_OK> --out-dir output/ai_factory/_leaf39_abcfo_rem_resid/<ET_TS>/ --leaf34-jaccard --no-skip-rho-excess`
9. sampler `/tmp/quantlab_leaf39_abcfo_*`；out `_leaf39_abcfo_rem_resid/<ET_TS>/`；Arch **不代跑**；可挂叶39 自有 QUIET（当前 QUIET **ABSENT**）。
10. live=false · promotion=false · book_smoke=false · **x2_accept=false** · **≠X2 ACCEPT** · COUNT APPROX 不解阻 · KEEP 不解阻。

缺 COND 硬钉才 FAIL/HOLD——本票 pins 全 MATCH；C2(a)/C5/C8/C9/ABSENT/静态 **PASS**；C2(b)/C3/C4 入钉且路径诚实预留，余项为签窗流程，故 **PASS_WITH_CONDITIONS**（非 FAIL / 非 HOLD / **≠ACCEPT**）。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶39 / RESTORED `f08ce32c`/`335635dd` / 旁线旧票）
- **未挂** QUIET；live QUIET **ABSENT**
- **未改** 脚本 `e99376dd` / LAND RECEIPT / FROZEN / Arch 审 / DRAFT / COUNT
- **未** `--allow-real-data` 真构建 / **未**代跑 X2 / Book-Smoke / 全量 α / 计数（仅 `py_compile` + `pyflakes` + dry/help/护栏 STOP）
- **未** RESTORED；**未**抬 rss；**未**自开 X2
- **未混** fund MDD HOLD；**未混**叶38
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳 / 建议主裁

```
脚本 e99376dd（本审 PASS_WITH_CONDITIONS · FROZEN 150d1a28 / ArchFROZEN b51a59a0 / LAND 04f6c7bb）
  → 请主另排独立 X2 签窗（新 .ok；钉 e99376dd only；禁 RESTORED f08ce32c/335635dd；不混 fund/叶38）
      → AI prelaunch→execute（--leaf34-jaccard；--no-skip-rho-excess + returns 接线；rss=1500 禁抬；peak_proof≤1500；PRIMARY=残差α）
          → Arch CONSUME（≠X2 ACCEPT；C9 COUNT 不解阻；KEEP 不解阻）
```

**本拍不签 / 不挂 / 不代跑**。**建议主裁：排独立 X2 签窗**（若主认为 C3 PIN / C2(b) returns 未接线前不宜开签窗，可 HOLD / 令补钉接线后再签）。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`e99376dd` MATCH** |
| LAND / FROZEN / ArchFROZEN / FROZEN RECEIPT | **`04f6c7bb`** / **`150d1a28`** / **`b51a59a0`** / **`507f09f1`** MATCH |
| ArchDRAFT / DRAFT / DRAFT RECEIPT / COUNT / COUNT脚本 / dig / HI_LIQ | **`4a1b4dd0`** / **`542138d6`** / **`691bbc14`** / **`d0d11598`** / **`20313ba3`≠正式** / **`440410de`** / **`c5433e80`** MATCH |
| C2(a) / C2(b) / C3 / C4 / C5 / C8 / C9 | APPROX **PASS** / ρ路径 **COND** / 叶34 PIN **COND** / rss+禁自签 **COND(签窗)** / 备选不升 **PASS** / 残差α **PASS** / ≠ACCEPT **PASS** |
| dry-compile / py_compile / pyflakes | **PASS**（exit0 / PASS / CLEAN）；FULLA STOP；rss 抬帽 STOP；无授权 STOP |
| EXECUTED_full_alpha | **false**（LAND） |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **排独立 X2 签窗**（钉 `e99376dd` only；本拍不签） |
| live | **false** |
| ≠X2 ACCEPT | **true** |
| leo_notify | **false** |

## 8. 本回执钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF39_ABCFO_REM_RESID_LAND_SCRIPT_REVIEW_20261027_ZH.md` |
| VERDICT | **PASS_WITH_CONDITIONS** |
| 本审盘上 sha8 | 见落盘 `sha256sum` / TEAM_STATE |
| 上游钉 | script/`e99376dd` · LAND/`04f6c7bb` · FROZEN/`150d1a28` · ArchFROZEN/`b51a59a0` · FROZEN RECEIPT/`507f09f1` · ArchDRAFT/`4a1b4dd0` · DRAFT/`542138d6` · COUNT/`d0d11598` · dig/`440410de` · HI_LIQ/`c5433e80` |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（回填 `1f9100e8`）。

**EXECUTED=false** · **leo_notify=false** · **live=false** · **ok_requested=false** · **≠X2 ACCEPT** · 只审不签不挂不代跑 · 旁线未混.
