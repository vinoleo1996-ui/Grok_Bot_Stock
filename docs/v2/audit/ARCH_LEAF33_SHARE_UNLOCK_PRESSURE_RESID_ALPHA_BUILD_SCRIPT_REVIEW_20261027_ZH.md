# Arch 审阅：叶33 限售解禁压力残差慢 α 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T06:19:00-04:00`（America/New_York；墙钟 `2026-10-27 06:19 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`8ed43721`** · FROZEN 审 **`bf5234a9`**（C1–C10 / C2 正式脚本）· who_pays 审 **`55531e12`** · PIN **`4e17ccfc`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / `--execute` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**脚本/FROZEN/RECEIPT/COVER/CMD/DIFF/PIN；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；叶28/29 **另队不夹带**；禁 RESTORED `5774bb6e`+二十票；**≠X2 ACCEPT**；live=false；**不报 Leo**；**勿混** Data 日更基线刷新（另线） |
| 触发 | 主 ~06:15 ET · 叶33 正式脚本只审（脚本 `05c45917` / RECEIPT `147f08e5` / COVER `8f7504a2` / CMD `ccdb18d7` / DIFF `78878272`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 mechanism/H20/H_back5/W20/rebal20/−rank/forbid21/peak_proof/C3=(a)+加价/primary_load=rebal_day_lazy_share_float_close_mktcap_bars）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`05c45917` MATCH**：mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；C3=(a)+加价 `unlock_mv=Σ float_share×close_T−1`（close 钉不复权 `close`）→ `unlock_raw=unlock_mv/float_mktcap_T−1` → `pressure_raw=mean_W`（W=20 / min_valid≥15；H/H_back=20/5）→ SW L1 demean → OLS logmv T−1 + mom20/vol20/**logADV20** → α=`−rank(pressure_resid)` 符号冻结；再平衡=20；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选且不得作 PRIMARY；X2 2024-06-03→2026-10-09；日度 base-α 非 Top-N；overlap vs 19/25/27/30/31/**32** + **margin_delta/hk_hold/moneyflow** Jaccard≥0.7 exit4 + ρ>0.5 强度；缺→PIN_GAP；rss=1500 硬 ABORT + peak_proof（after_mask / after_sw / after_share_float_rebal_* / after_close_rebal_* / after_float_mktcap_rebal_* / after_bars_rebal_* / after_logmv_rebal_* / after_daily_concat）；再平衡日懒加载 share_float+close+mktcap+bars；forbid∋`5774bb6e`+二十票（21 sha8，含 `02426b73`）；表内 `float_ratio` PRIMARY 禁用；真跑须 `--allow-real-data` + **已实现** `--arch-ok-path`（现存且∉forbid）；CMD 拟 cmd 含未来新 `.ok`（现不可跑）；decay KEEP 三闸+**KEEP 不解阻**仅钉（本脚本不跑）；禁 Amihud / on_minus_id / CRR / hk_hold / moneyflow / margin / float_ratio 主输入；CLI 仍保留 `--no-overlap-report` 但**真跑硬 STOP**（优于叶32 仅签文闸）；无 `--force` / 盲 seed；dry-compile PASS；叶32 模板 **`4e0f3c00` UNCHANGED**；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `05c45917` | `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2` | **MATCH** · 2110 行 |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `147f08e5` | `147f08e5ec0cc373ac79ad956030ac3fa49b339ba1fde8a80af7c05c401eb2e4` | **MATCH** · EXECUTED=false |
| COVER DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `8f7504a2` | `8f7504a2dce4b92027e330300ac92fce56d5175a84d18bba5ab3c18de506ee68` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `ccdb18d7` | `ccdb18d7a316b884b4b1f6403d36b9435e076757a10ed791c46e2257793735b2` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `78878272` | `78878272e1f0c393a174f8cf7da4386fc39c9ba17bc0d4880c87b37d5dbc538d` | **MATCH** · NEW vs 叶32 |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | `8ed43721` | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bf5234a9` | `bf5234a9fb732a7e71a0bc1ca5b7e6097e50d4e1d023778e534f2bf58e9c19d3` | **MATCH** |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `8f43e2f8` | `8f43e2f8f1f62ad9dddfb9a9be71c32c574b9c3037c61a256e971ef2385085ff` | **MATCH** |
| PIN 决议 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75` | **MATCH**（FROZEN 升级 (a)+加价入码） |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `55531e12` | `55531e129e89077e9390a45c2f1310d5e2a80421ff6d16927b46bbaf1a7ee3c5` | **MATCH** |
| 叶32 模板（只读） | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c00` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **UNCHANGED** |
| 对照模板（只读） | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` | （形态对照） | — | **只读** |
| live leaf33 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| 叶30 KEEP `0087c928` | 衰减修复 DRAFT | 另队 | 本拍**未打开/未审** | **未审声明** |

哈希闭环：脚本/RECEIPT/COVER/CMD/DIFF 互指 sha8 与盘上一致；脚本常量钉 FROZEN `8ed43721` / FROZEN 审 `bf5234a9` / who_pays `55531e12` / WHO `1032477d` / COVER `61d9f656` / PIN `4e17ccfc` / 叶32 骨架 `4e0f3c00`。

## 2. 必审清单（脚本 vs FROZEN `8ed43721` / 审 `bf5234a9` / PIN `4e17ccfc`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 哈希闭环 + 机制对齐：unlock→pressure_raw→SW+style→α=`−rank`；H/H_back/W/rebal=20/5/20/20；≠Amihud/on−id/CRR/hk_hold/moneyflow/margin/float_ratio 主输入；避 25/27/30/31/32 同构 | **PASS** | `MECHANISM_TAG`；`PRESSURE_H/H_BACK/W=20/5/20`；`REBAL_EVERY=20`；`ALPHA_SIGN=neg_rank_pressure_resid`；L1625–1627 `alpha=-rnk`；`IC_SIGN_EXPECTED=positive`（注释钉；脚本不算 IC）；dry bans：`ban_amihud_main` / `ban_on_minus_id_main` / `ban_crr_accounting_main` / `ban_hk_hold_northbound_main` / `ban_moneyflow_main` / `ban_margin_flow_main` / `ban_margin_delta_as_main` / `ban_float_ratio_primary`；PIT=`available_at` |
| 2 | **C3** (a)+加价：`unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`；表内 float_ratio PRIMARY 禁用；close 钉不复权 | **PASS** | `C3_FORMULA_PIN`；`CLOSE_COL_PINNED=close` / `CLOSE_COL_ROLE=unadjusted_close_cny_per_share`；`BAN_FLOAT_RATIO_PRIMARY=True`；`_load_share_float` 明示不携带 float_ratio；缺 close/mktcap→无效不填 0 |
| 3 | **C4** 重叠：正交/Jaccard vs 叶19/25/27/30/31/32 + margin_delta/hk_hold/moneyflow；Jaccard≥0.7 硬拒；ρ>0.5 强度 | **PASS_WITH_CONDITIONS** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json`；缺文件→`any_required_pin_gap` exit3；`any_jaccard_hard_reject` → return **4**。CLI **仍保留** `--no-overlap-report`，但真跑硬 STOP exit2（`ban_no_overlap_report_bypass_on_real`）→ **仍须入签文硬闸**（双保险） |
| 4 | **C5** 残差：SW L1 + style 残差与 FROZEN 一致；缺列 PIN_GAP；禁事后换 capacity_adv | **PASS** | `_residualize_cross_section`；`STYLE_COLS_PINNED=("mom20","vol20","logADV20")`；`STYLE_SOURCE_PINNED=derived_from_daily_bars_W20`；缺列 `STOP: PIN_GAP`；logmv T−1 via `_load_logmv_t1`；style 用 adj、unlock_mv 用 raw close（禁互换） |
| 5 | **C6** 宇宙：HI_LIQ PRIMARY + FULLA 双钉；`--universe FULLA` STOP | **PASS** | dry/run STOP FULLA exit2；`build_alpha_for_window(..., "HILIQ")` 主路径；FULLA 仅 `also_fulla_research`；coverage median 闸 300/800 |
| 6 | **C7** decay KEEP 三闸+KEEP 不解阻仅钉（本脚本不执行 selfcheck 晋级） | **PASS** | `DECAY_KEEP_PIN`（latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；near=252；`keep_does_not_unblock_x2_accept=true`）；meta note「script does not execute decay gate」；`ban_selfcheck=true` |
| 7 | **C8** forbid `5774bb6e`+二十票；禁 RESTORED；禁 `--force`/盲 seed；`--arch-ok-path` 已实现 | **PASS** | `FORBID_OK_SHA8` **21** 项含 `5774bb6e`+`02426b73`+叶30/31 六票等；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 .ok 逻辑；源码无 `--force` / 盲 seed |
| 8 | **C9** 内存：rss=1500 + peak_proof；单进程 RSS≤1.5GB；禁抬 | **PASS** | `RSS_LIMIT_MB=1500`；抬 rss → STOP；Exit 94/95 路径；`_rss` 于 after_mask / after_sw / after_share_float_* / after_close_* / after_float_mktcap_* / after_bars_* / after_logmv_* / after_daily_concat；`primary_load=rebal_day_lazy_share_float_close_mktcap_bars`；del+gc |
| 9 | **C10**：`0087c928` 另队未审、未夹带；叶28/29 另队 | **PASS（未审声明）** | `LEAF30_KEEP_REPAIR_SHA8_SEPARATE=0087c928`；本拍未打开/未审该 DRAFT；叶28/29 不夹带 |
| 10 | 模板：相对叶32 `4e0f3c00` DIFF 合理（机制换皮，非乱改主干） | **PASS** | DIFF `78878272` 标 NEW vs 叶32；语义差=margin flow→share unlock / +leaf32+hk_hold+moneyflow overlap / forbid 6→21 / C3 加价 / sampler·out 换叶33；叶32 **UNCHANGED** |
| 11 | dry-compile PASS；CMD 拟 approved_cmd 含未来新 `.ok`；禁不当旗标；EXECUTED=false；live ok/QUIET ABSENT | **PASS** | 本机复跑见上；CMD 拟 `…LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok`（未创建）；CMD 明示禁 `--no-overlap-report`；流程门=.ok+主窗；RECEIPT EXECUTED=false |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 月分片后一次 concat；须 peak_proof；破→94/95，**禁抬帽** |
| 再平衡日四重懒加载（share_float+close+mktcap+bars）I/O 变慢 | **低–中** | 吸取叶30/31/32 peak；可接受 |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 靠脚本硬 STOP + 签文双闸；消费端须读 overlap JSON（含 vs leaf32/margin_delta/hk_hold/moneyflow） |
| overlap 抽样日数有限 | **低–管控** | 硬拒仍 exit4；完整 α 另交付；签窗勿用 DRAFT 意向替正式重叠 |
| FULLA 研究失败仅 WARN | **低** | PRIMARY HILIQ 已写；研究失败不抬 PRIMARY |
| share_float 大表按再平衡窗过滤仍可能瞬时峰 | **中** | peak_proof 阶段性标签已入；破则 ABORT |
| PIN 初稿 `sum(float_share)/mktcap` vs FROZEN (a)+加价 | **已闭环** | 脚本钉 FROZEN 升级路径；勿回退静默混用 float_ratio |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`05c45917` only**。
2. **禁 RESTORED `5774bb6e`+二十票**：forbid∋21 sha8（含 `5774bb6e`/`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`/…）；禁复用叶25/27/30/31/32 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长 `05c4591788b8bf244c03b63fd918f154ae87e15b5f08cb8930f5ff78c8fb01e2`；dry-compile PASS；FROZEN `8ed43721` / FROZEN 审 `bf5234a9` / PIN `4e17ccfc` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_sw` / `after_share_float_rebal_*` / `after_close_rebal_*` / `after_float_mktcap_rebal_*` / `after_bars_rebal_*` / `after_logmv_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → Exit **94/95** 停+上报；**rss=1500 禁抬**。
5. **C4 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25_27_30_31_32_margin_delta_hk_hold_moneyflow.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；缺→PIN_GAP；签文 **禁** `--no-overlap-report`（脚本已硬 STOP，签文双保险）。
6. **C3 签文硬钉**：close=`close`（不复权）；`unlock_mv=Σ float_share×close_T−1`；表内 float_ratio PRIMARY 禁用；禁事后改 adj。
7. **PRIMARY 纪律**：判决=HILIQ；FULLA 仅 `--also-fulla-research` 研究披露；不得静默改 FULLA 作 PRIMARY。
8. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf33_share_unlock/<ET_TS>/`
9. sampler `/tmp/quantlab_leaf33_share_unlock_*`；out `_leaf33_share_unlock/<ET_TS>/`；Arch **不代跑**；可挂 leaf33 自有 QUIET（当前 QUIET **ABSENT**）。
10. **C10 仍另队**：`0087c928` / 叶28/29 不得借本脚本/签窗夹带。
11. **C7 另窗**：decay KEEP 硬验收不在本构建脚本；X2/selfcheck 另窗；失败最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT。
12. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT**。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶33 / RESTORED `5774bb6e`+二十票）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 脚本 `05c45917` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN
- **未** `--allow-real-data` / **未** `--execute` / **未**代跑真构建（仅 `py_compile` + dry）；repo `__pycache__/leaf33*` **ABSENT**；`output/ai_factory/_leaf33*` **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审**叶30 衰减修复 `0087c928`（另队）；**未打开**该 DRAFT；**未夹带**叶28/29
- **未改** 叶32 模板 `4e0f3c00`；**未混** Data 日更基线刷新（另线）
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 05c45917（本审 PASS_WITH_CONDITIONS · FROZEN 8ed43721 / 审 bf5234a9 / PIN 4e17ccfc / who_pays 55531e12）
  → 请主另排独立 X2 签窗（新 .ok；钉 05c45917；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof；overlap 含 vs leaf32/margin_delta/hk_hold/moneyflow；C3 close 钉）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`05c45917` MATCH** |
| RECEIPT / COVER / CMD / DIFF | **`147f08e5`** / **`8f7504a2`** / **`ccdb18d7`** / **`78878272`** MATCH |
| FROZEN / FROZEN 审 / PIN / who_pays 审 | **`8ed43721`** / **`bf5234a9`** / **`4e17ccfc`** / **`55531e12`** MATCH |
| 叶32 模板 | **`4e0f3c00` UNCHANGED** |
| dry-compile | **PASS**（exit0）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `05c45917`；本拍不签） |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| 脚本 sha8 | **`05c45917`** |
| RECEIPT / COVER / CMD / DIFF | **`147f08e5`** / **`8f7504a2`** / **`ccdb18d7`** / **`78878272`** |
| FROZEN / FROZEN 审 / PIN / who_pays 审 | **`8ed43721`** / **`bf5234a9`** / **`4e17ccfc`** / **`55531e12`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签；请主另排独立 X2 签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
