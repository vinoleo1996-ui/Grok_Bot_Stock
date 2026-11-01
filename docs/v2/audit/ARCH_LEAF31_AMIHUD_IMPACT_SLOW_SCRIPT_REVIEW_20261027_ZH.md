# Arch 审阅：叶31 Amihud 冲击慢 α 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T02:32:00-04:00`（America/New_York；墙钟 `2026-10-27 02:32 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`bcbec955`** · FROZEN 审 **`7a6a1e1a`**（C1–C9 / C2 正式脚本） |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；禁 RESTORED 四票；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~02:28 ET priority · 叶31 正式脚本只审（脚本 `08f37fd2` / COVER `e736a033` / CMD `37443b02` / DIFF `6c47e185` / RECEIPT `a3981844`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 mechanism/W20/rebal20/−rank/forbid4/peak_proof/primary_load=rebal_day_lazy_bars）；`--universe FULLA` dry → STOP exit **2** |

## 0. 一句话

脚本 **`08f37fd2` MATCH**：mechanism=`g1g5_ashare_amihud_impact_slow_v1`；Amihud W=20 / min_valid≥15 / 再平衡=20；α=`−rank(impact_resid)` 符号冻结；残差 SW L1 demean → OLS logmv T−1 + mom20/vol20/**logADV20**（钉死；禁 capacity_adv 事后换）；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选且不得作 PRIMARY；X2 2024-06-03→2026-10-09；日度 base-α 非 Top-N；overlap vs 19/25/27/30 Jaccard≥0.7 exit4 + ρ>0.5 强度；rss=1500 硬 ABORT + peak_proof（after_mask / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat）；再平衡日懒加载 bars+logmv；forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；真跑须 `--allow-real-data` + **已实现** `--arch-ok-path`（现存且∉forbid）；CMD 拟 cmd 含未来新 `.ok`（现不可跑）；amount 千元×1000→元；adj PIT；禁卖方/金股/会计/on_minus_id 主输入；dry-compile PASS；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf31_amihud_impact_slow_alpha_build.py` | `08f37fd2` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **MATCH** · 1532 行 |
| COVER DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `e736a033` | `e736a03349cf6bac7ea8ae726f26cedc43619b8185dbc8d59c25b16758935978` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `37443b02` | `37443b02ac526ee5a52d9483f40cc90e43318309b4a78d10c937b6f3dd0e0cbc` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `6c47e185` | `6c47e185272a6749881ae554f36bf06b1672250cc182e2f73d1f9b8dfab03e04` | **MATCH** · NEW FILE |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `a3981844` | `a398184414a8868c1a2a2a9fa32f9bd3b4eb1fa444b70dc979e79e2a4ad95bd0` | **MATCH** · EXECUTED=false |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_20261027_ZH.md` | `bcbec955` | `bcbec955937bd1d5c972cb81a9ba78e944fe14ccd2e9bf11fdbb874ced8aece4` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `7a6a1e1a` | `7a6a1e1adb6bfb71cd128fe08e71c16c763c59187dd4e1d4bb40abc6c2adc639` | **MATCH** |
| 对照模板（只读） | `docs/v2/audit/ARCH_LEAF30_CRR_ALPHA_BUILD_R3_PEAKCUT_SCRIPT_REVIEW_20261026_ZH.md` | `d081054e` | （形态对照） | **只读** |
| 叶30 R3 peakcut（只读） | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` | `3ee9fed2` | （形态对照；未改） | **只读** |
| live leaf31 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF31*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| 叶30 KEEP `0087c928` | 衰减修复 DRAFT | 另队 | 本拍**未打开/未审** | **未审声明** |

## 2. 必审清单（脚本 vs FROZEN `bcbec955` / 审 `7a6a1e1a`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | mechanism / Amihud W=20 / min≥15 / 再平衡=20 / α=−rank / 禁事后翻 | **PASS** | `MECHANISM_TAG`；`AMIHUD_W=20`/`AMIHUD_MIN_VALID=15`/`REBAL_EVERY=20`；`ALPHA_SIGN=neg_rank_impact_resid`；L1108–1110 `alpha=-rnk`；`IC_SIGN_EXPECTED=positive` 注释钉；dry `ban_posthoc_sign_flip` |
| 2 | 残差 C4：SW L1 → OLS logmv T−1 + mom20/vol20/**logADV20**；缺列 PIN_GAP；禁换 capacity_adv | **PASS** | `_residualize_cross_section`；`STYLE_COLS_PINNED=("mom20","vol20","logADV20")`；`STYLE_SOURCE_PINNED=derived_from_daily_bars_W20`；缺列 `STOP: PIN_GAP`；`_load_logmv_t1` 用 `trade_date < asof` |
| 3 | PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选非 PRIMARY | **PASS** | `normalize_universe`+dry/run STOP FULLA；`build_alpha_for_window(..., "HILIQ")` 主路径；FULLA 仅 `also_fulla_research` 分支且 meta 注 research only |
| 4 | X2 窗 2024-06-03→2026-10-09；日度 base-α 非 Top-N | **PASS** | `X2_START/END`；`--x2-end` 硬钉 `20261009`；月分片展开日度 `trade_date/ts_code/alpha`；无 Top-N 闸 |
| 5 | overlap vs 19/25/27/30：Jaccard≥0.7 硬拒；ρ>0.5 强度 | **PASS_WITH_CONDITIONS** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30.json`；`any_jaccard_hard_reject` → return **4**；ρ>0.5 `strength_filter_*`。CLI **仍保留** `--no-overlap-report`（dry `ban_no_overlap_report=true`）→ **须入签文硬闸**。重叠抽样 ≈6 再平衡日（完整日度 α 已产；正式消费端须读 overlap JSON） |
| 6 | rss=1500 硬 ABORT + peak_proof；禁抬；再平衡日懒加载 | **PASS** | `RSS_LIMIT_MB=1500`；抬 rss/C4/stop/hard → STOP；Exit 94/95；`_rss` 于 after_mask / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat（另 after_sw）；`primary_load=rebal_day_lazy_bars`；按日 `_load_daily_window` + `_load_logmv_t1(..., [d], …)` + del+gc；无整窗 `logmv_rebal=` |
| 7 | forbid 四票；`--arch-ok-path` 已实现；不自造 .ok | **PASS** | `FORBID_OK_SHA8` 含 `aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 .ok 逻辑 |
| 8 | CMD 拟 approved_cmd 含未来新 `.ok`；现不可跑；EXECUTED=false | **PASS** | CMD `37443b02`：拟 path `…LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok`（未创建）；RECEIPT EXECUTED=false；本机 live `.ok` ABSENT |
| 9 | 禁卖方/金股/accounting/on_minus_id；amount 千元→元；adj PIT | **PASS** | dry bans；amount `×1000`；adj `adj_factor_2023h2plus` hfq；叶27 α 仅 overlap 对照路径 |
| 10 | dry-compile PASS；live ok/QUIET ABSENT；`0087c928` 另队未审 | **PASS** | 本机复跑见上；`LEAF30_KEEP_REPAIR_SHA8_SEPARATE=0087c928`；本拍未审该 DRAFT |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 月分片后一次 concat；须 peak_proof；破→94/95，**禁抬帽** |
| 按日 I/O 变慢 | **低–中** | 吸取叶30 peak；可接受 |
| CLI `--no-overlap-report` 仍在 | **管控** | 靠签文硬闸；消费端须读 overlap JSON |
| overlap 抽样日数≈6 | **低–管控** | 硬拒仍 exit4；完整 α 另交付；签窗勿用 DRAFT 意向替正式重叠 |
| FULLA 研究失败仅 WARN | **低** | PRIMARY HILIQ 已写；研究失败不抬 PRIMARY |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`08f37fd2` only**。
2. **禁 RESTORED 四票**：forbid∋`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长 `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0`；dry-compile PASS；FROZEN `bcbec955` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → Exit **94/95** 停+上报；**rss=1500 禁抬**。
5. **C3 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25_27_30.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；签文 **禁** `--no-overlap-report`。
6. **PRIMARY 纪律**：判决=HILIQ；FULLA 仅 `--also-fulla-research` 研究披露；不得静默改 FULLA 作 PRIMARY。
7. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf31_amihud/<ET_TS>/`
8. sampler `/tmp/quantlab_leaf31_amihud_*`；out `_leaf31_amihud/<ET_TS>/`；Arch **不代跑**；可挂 leaf31 自有 QUIET（当前 QUIET **ABSENT**）。
9. **C9 仍另队**：`0087c928` 不得借本脚本/签窗夹带。
10. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶31 / RESTORED 四票）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 脚本 `08f37fd2` / COVER / CMD / DIFF / RECEIPT / FROZEN
- **未** `--allow-real-data` / **未**代跑真构建（仅 `py_compile` + dry）；repo `__pycache__/leaf31*` **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审**叶30 衰减修复 `0087c928`（另队）
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 08f37fd2（本审 PASS_WITH_CONDITIONS · FROZEN bcbec955 / 审 7a6a1e1a）
  → 请主另排独立 X2 签窗（新 .ok；钉 08f37fd2；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`08f37fd2` MATCH** |
| COVER / CMD / DIFF / RECEIPT | **`e736a033`** / **`37443b02`** / **`6c47e185`** / **`a3981844`** MATCH |
| FROZEN / FROZEN 审 | **`bcbec955`** / **`7a6a1e1a`** MATCH |
| dry-compile | **PASS**（exit0）；FULLA PRIMARY STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `08f37fd2`；本拍不签） |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_SCRIPT_REVIEW_20261027_ZH.md` |
| 脚本 sha8 | **`08f37fd2`** |
| COVER / CMD / DIFF / RECEIPT | **`e736a033`** / **`37443b02`** / **`6c47e185`** / **`a3981844`** |
| FROZEN / FROZEN 审 | **`bcbec955`** / **`7a6a1e1a`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签；请主另排独立 X2 签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
