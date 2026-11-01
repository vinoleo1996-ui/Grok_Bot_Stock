# Arch 审阅：叶32 净融资流入强度残差慢 α 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T04:16:00-04:00`（America/New_York；墙钟 `2026-10-27 04:16 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`6b8de5e9`** · FROZEN 审 **`7c0d864f`**（C1–C9 / C2 正式脚本）· who_pays 审 **`84df02b5`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / `--execute` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**脚本/FROZEN/RECEIPT/COVER/CMD/DIFF；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；禁 RESTORED 六票；**≠X2 ACCEPT**；live=false；**不报 Leo** |
| 触发 | 主 ~04:11 ET priority · 叶32 正式脚本只审（脚本 `4e0f3c00` / RECEIPT `0937a882` / COVER `b269aec5` / CMD `53002ae3` / DIFF `264d0159`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 mechanism/W20/rebal20/−rank/forbid6/peak_proof/primary_load=rebal_day_lazy_margin_float_bars）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`4e0f3c00` MATCH**：mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；net_rz=`rzmre−rzche` → flow_raw=`mean_W(net_rz/float_mktcap_T−1)`（W=20 / min_valid≥15）→ SW L1 demean → OLS logmv T−1 + mom20/vol20/**logADV20** → α=`−rank(flow_resid)` 符号冻结；再平衡=20；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选且不得作 PRIMARY；X2 2024-06-03→2026-10-09；日度 base-α 非 Top-N；overlap vs 19/25/27/30/31 + **margin_delta**（weight）Jaccard≥0.7 exit4 + ρ>0.5 强度；margin_delta 缺→PIN_GAP；rss=1500 硬 ABORT + peak_proof（after_mask / after_sw / after_margin_rebal_* / after_float_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat）；再平衡日懒加载 margin+float+bars；forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；真跑须 `--allow-real-data` + **已实现** `--arch-ok-path`（现存且∉forbid）；CMD 拟 cmd 含未来新 `.ok`（现不可跑）；decay KEEP 三闸仅钉（本脚本不跑）；禁 hk_hold / Amihud / on_minus_id / CRR / margin_delta 主输入；无 `--force` / 盲 seed；dry-compile PASS；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c00` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH** · 1866 行 |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `0937a882` | `0937a8823a01cf025ba07aaaa3c4546bc2863ca72964676971d2faedd449b438` | **MATCH** · EXECUTED=false |
| COVER DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `b269aec5` | `b269aec512b826f74384106d3313f85c4e2f69b18f1fac370171b2244201818a` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `53002ae3` | `53002ae3860b64e79f52455f13fc046ae5baa5302ec079d46ef0410e78e7067f` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `264d0159` | `264d01596154c71923f17fa4b0106db661daf29f95f19e9ccddbf1e91256b294` | **MATCH** · NEW FILE vs 叶31 |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `7c0d864f` | `7c0d864f7d544e8bd16817c74fa4dd7e35c9609c5066eedc4ee15f71765b5d84` | **MATCH** |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `7623ce8c` | `7623ce8c351ce7c1927b17dd095953f8c968753fbfe5f9d5eb29042bf814bb37` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `84df02b5` | `84df02b5ddfd10314bf8bc95acdf931d12ba9e53e43dd318e61fdc85b7b6fb01` | **MATCH** |
| WHO_PAYS / who COVER | `…WHO_PAYS_DRAFT…` / `…COVER_DRAFT…`（背景） | `fad5911e` / `ebda2603` | （本机 MATCH） | **MATCH** |
| 叶31 模板（只读） | `research/leaf31_amihud_impact_slow_alpha_build.py` | `08f37fd2` | `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0` | **UNCHANGED** |
| 对照模板（只读） | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_SCRIPT_REVIEW_20261027_ZH.md` | （形态对照） | — | **只读** |
| live leaf32 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF32*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| 叶30 KEEP `0087c928` | 衰减修复 DRAFT | 另队 | 本拍**未打开/未审** | **未审声明** |

哈希闭环：脚本/RECEIPT/COVER/CMD/DIFF 互指 sha8 与盘上一致；脚本常量钉 FROZEN `6b8de5e9` / FROZEN 审 `7c0d864f` / who_pays `84df02b5` / WHO `fad5911e` / COVER `ebda2603`。

## 2. 必审清单（脚本 vs FROZEN `6b8de5e9` / 审 `7c0d864f`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 哈希闭环 + 机制对齐：net_rz→flow_raw→SW+style→α=`−rank`；W/rebal=20/20；不读 hk_hold；≠margin_delta/Amihud/on−id/CRR | **PASS** | `MECHANISM_TAG`；`FLOW_W=20`/`FLOW_MIN_VALID=15`/`REBAL_EVERY=20`；`ALPHA_SIGN=neg_rank_flow_resid`；L1423–1425 `alpha=-rnk`；`IC_SIGN_EXPECTED=positive`；dry bans：`ban_hk_hold_northbound_main` / `ban_amihud_main` / `ban_on_minus_id_main` / `ban_crr_accounting_main` / `ban_margin_delta_as_main`；PIT=`available_at` |
| 2 | **C3** 重叠：正交/Jaccard vs 叶19/25/27/30/31 + vs margin_delta；Jaccard≥0.7 硬拒；ρ>0.5 强度 | **PASS_WITH_CONDITIONS** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30_31_margin_delta.json`；margin_delta 用 weight/target_weight；缺文件→`any_required_pin_gap`；`any_jaccard_hard_reject` → return **4**。CLI **仍保留** `--no-overlap-report`（dry `ban_no_overlap_report=true`）→ **须入签文硬闸**。重叠抽样 ≈6 再平衡日 |
| 3 | **C4** 残差：SW L1 + style 残差与 FROZEN 一致；缺列 PIN_GAP；禁事后换 capacity_adv | **PASS** | `_residualize_cross_section`；`STYLE_COLS_PINNED=("mom20","vol20","logADV20")`；`STYLE_SOURCE_PINNED=derived_from_daily_bars_W20`；缺列 `STOP: PIN_GAP`；logmv T−1 via `_load_logmv_t1`（`trade_date < asof`） |
| 4 | **C5** 宇宙：HI_LIQ PRIMARY + FULLA 双钉；`--universe FULLA` STOP | **PASS** | dry/run STOP FULLA exit2；`build_alpha_for_window(..., "HILIQ")` 主路径；FULLA 仅 `also_fulla_research`；coverage median 闸 300/800 |
| 5 | **C6** decay KEEP 三闸仅钉（本脚本不执行 selfcheck 晋级） | **PASS** | `DECAY_KEEP_PIN`（latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；near=252）；meta note「script does not execute decay gate」；`ban_selfcheck=true` |
| 6 | **C7** forbid 六票；禁 RESTORED；禁 `--force`/盲 seed；`--arch-ok-path` 已实现 | **PASS** | `FORBID_OK_SHA8` 含六票；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 .ok 逻辑；源码无 `--force` / 盲 seed |
| 7 | **C8** 内存：rss=1500 + peak_proof；单进程 RSS≤1.5GB；禁抬 | **PASS** | `RSS_LIMIT_MB=1500`；抬 rss → STOP；Exit 94/95；`_rss` 于 after_mask / after_sw / after_margin_* / after_float_* / after_bars_* / after_logmv_* / after_daily_concat；`primary_load=rebal_day_lazy_margin_float_bars`；del+gc |
| 8 | **C9**：`0087c928` 另队未审、未夹带 | **PASS（未审声明）** | `LEAF30_KEEP_REPAIR_SHA8_SEPARATE=0087c928`；本拍未打开/未审该 DRAFT |
| 9 | 模板：相对叶31 `08f37fd2` DIFF 合理（机制换皮，非乱改主干） | **PASS** | DIFF `264d0159` 标 NEW FILE；语义差=Amihud→margin flow / +leaf31+margin_delta overlap / forbid 4→6 / sampler·out 换叶32；叶31 **UNCHANGED** |
| 10 | dry-compile PASS；CMD 拟 approved_cmd 含未来新 `.ok`；EXECUTED=false；live ok/QUIET ABSENT | **PASS** | 本机复跑见上；CMD 拟 `…LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok`（未创建）；RECEIPT EXECUTED=false |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 月分片后一次 concat；须 peak_proof；破→94/95，**禁抬帽** |
| 再平衡日三重懒加载（margin+float+bars）I/O 变慢 | **低–中** | 吸取叶30/31 peak；可接受 |
| CLI `--no-overlap-report` 仍在 | **管控** | 靠签文硬闸；消费端须读 overlap JSON（含 vs margin_delta） |
| overlap 抽样日数≈6 | **低–管控** | 硬拒仍 exit4；完整 α 另交付；签窗勿用 DRAFT 意向替正式重叠 |
| FULLA 研究失败仅 WARN | **低** | PRIMARY HILIQ 已写；研究失败不抬 PRIMARY |
| margin 大表按再平衡窗过滤仍可能瞬时峰 | **中** | peak_proof 阶段性标签已入；破则 ABORT |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`4e0f3c00` only**。
2. **禁 RESTORED 六票**：forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30/31 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长 `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187`；dry-compile PASS；FROZEN `6b8de5e9` / FROZEN 审 `7c0d864f` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_sw` / `after_margin_rebal_*` / `after_float_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → Exit **94/95** 停+上报；**rss=1500 禁抬**。
5. **C3 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25_27_30_31_margin_delta.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；margin_delta 缺→PIN_GAP；签文 **禁** `--no-overlap-report`。
6. **PRIMARY 纪律**：判决=HILIQ；FULLA 仅 `--also-fulla-research` 研究披露；不得静默改 FULLA 作 PRIMARY。
7. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf32_margin_flow/<ET_TS>/`
8. sampler `/tmp/quantlab_leaf32_margin_flow_*`；out `_leaf32_margin_flow/<ET_TS>/`；Arch **不代跑**；可挂 leaf32 自有 QUIET（当前 QUIET **ABSENT**）。
9. **C9 仍另队**：`0087c928` 不得借本脚本/签窗夹带。
10. **C6 另窗**：decay KEEP 硬验收不在本构建脚本；X2/selfcheck 另窗；失败最多 WATCH/HOLD。
11. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶32 / RESTORED 六票）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 脚本 `4e0f3c00` / COVER / CMD / DIFF / RECEIPT / FROZEN
- **未** `--allow-real-data` / **未** `--execute` / **未**代跑真构建（仅 `py_compile` + dry）；repo `__pycache__/leaf32*` **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审**叶30 衰减修复 `0087c928`（另队）；**未打开**该 DRAFT
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 4e0f3c00（本审 PASS_WITH_CONDITIONS · FROZEN 6b8de5e9 / 审 7c0d864f / who_pays 84df02b5）
  → 请主另排独立 X2 签窗（新 .ok；钉 4e0f3c00；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof；overlap 含 vs margin_delta）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`4e0f3c00` MATCH** |
| RECEIPT / COVER / CMD / DIFF | **`0937a882`** / **`b269aec5`** / **`53002ae3`** / **`264d0159`** MATCH |
| FROZEN / FROZEN 审 / who_pays 审 | **`6b8de5e9`** / **`7c0d864f`** / **`84df02b5`** MATCH |
| 叶31 模板 | **`08f37fd2` UNCHANGED** |
| dry-compile | **PASS**（exit0）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `4e0f3c00`；本拍不签） |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| 脚本 sha8 | **`4e0f3c00`** |
| RECEIPT / COVER / CMD / DIFF | **`0937a882`** / **`b269aec5`** / **`53002ae3`** / **`264d0159`** |
| FROZEN / FROZEN 审 / who_pays 审 | **`6b8de5e9`** / **`7c0d864f`** / **`84df02b5`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签；请主另排独立 X2 签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
