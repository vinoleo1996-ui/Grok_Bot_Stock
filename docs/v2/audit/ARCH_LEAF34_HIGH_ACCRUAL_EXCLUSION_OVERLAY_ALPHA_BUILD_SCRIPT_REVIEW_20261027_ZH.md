# Arch 审阅：叶34 高应计剔除 overlay 正式构建脚本（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审脚本） |
| 时刻 | `2026-10-27T10:37:00-04:00`（America/New_York；墙钟 `2026-10-27 10:37 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 对照 | PREREG_FROZEN **`8be1099e`** · FROZEN 审 **`027efa26`**（C1–C13 / C2 正式脚本）· who_pays 审 **`9d8a2f9e`** · PIN **`bb418e6a`** · FROZEN RECEIPT **`438ee33d`** |
| 本回合动作 | **不签**任何 `.ok`；**不挂** QUIET；**不代跑** `--allow-real-data` / `--execute` / 真构建（仅 `py_compile` + `--dry-compile-only`）；**不改**脚本/FROZEN/RECEIPT/COVER/CMD/DIFF/PIN；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；叶28/29 **另队不夹带**；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；**≠X2 ACCEPT**；live=false；**不报 Leo**；**leo_notify=false** |
| 触发 | 主 ~10:32 ET · 叶34 C2 正式脚本只审（脚本 `482009dc` / COVER `c491e7a4` / CMD `cfa3ca4e` / DIFF `f583b616` / RECEIPT `f73c986f`） |
| 轻量复跑 | `py_compile` **PASS**；`--dry-compile-only` exit **0**（零大表；JSON 含 mechanism/mask_only/top_q=0.20/C3 PIN/forbid24/peak_proof/overlap vs19–33/decay KEEP）；`--universe FULLA` dry → STOP exit **2**；无授权 flag → STOP exit **2** |

## 0. 一句话

脚本 **`482009dc` MATCH**：mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；PRIMARY=**mask-only** top_q=**0.20**（高应计 mask=0；可计算其余 mask=1；不可计算不填假 0）；soft-penalty **默认关、非 PRIMARY**（`--enable-soft-penalty` 须 SW+style，缺列 PIN_GAP）；C3=`accrual_cf=1−ocf_to_profit` + PIT `e_available_at≤t` + NP≤0 剔除 + `YTD_cumulative`/YTD-ish + 日表 `f9faf7e7` + **禁 BS WC PRIMARY**；再平衡=20；X2 2024-06-03→2026-10-09；PRIMARY=HILIQ；`--universe FULLA` STOP；`--also-fulla-research` 可选且不得作 PRIMARY；C7 overlap vs 19/25/27/30/31/32/**33** + Jaccard≥0.7 exit4 + ρ>0.5 强度 + 叶25 尾窗披露 + 缺→PIN_GAP；rss=1500 硬 ABORT + peak_proof（after_mask / after_ocf_rebal_* / after_mask_cs_rebal_* / after_daily_concat）；再平衡日懒加载 ocf；forbid∋`245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`（**24** sha8）；真跑须 `--allow-real-data` + **已实现** `--arch-ok-path`（现存且∉forbid）；CMD 拟 cmd 含未来新 `.ok`（现不可跑）；decay KEEP 三闸+**KEEP 不解阻**仅钉；C11 overlay≠应计主叶；C12 APPROX≠ACCEPT；C10 `0087c928`/28/29 另队；禁 `--force` / 盲 seed；dry-compile PASS；DIFF **字节≡脚本**；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 模板 **`4e0f3c00`** 只读；live `.ok`/QUIET **ABSENT**；EXECUTED=false。**本拍不签**；请主另排独立 X2 签窗。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 / 值 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| **正式脚本** | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` | `482009dc` | `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc` | **MATCH** · 1715 行 |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_RECEIPT_20261027_ZH.md` | `f73c986f` | `f73c986fcacc24d7df41eed64442e91c4f550e2fd222c089dcd0da97cc5cc693` | **MATCH** · EXECUTED=false |
| COVER DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_COVER_DRAFT_20261027_ZH.md` | `c491e7a4` | `c491e7a4bfcf40123cb4781bd8985a1df5ca6b4b96ac0e1e9ed7c879b7c6ca5d` | **MATCH** |
| CMD DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_CMD_DRAFT_20261027_ZH.md` | `cfa3ca4e` | `cfa3ca4ec41a825ba0c9eb29d578c9798ed39c4120c19f1d64eef0a2629098c7` | **MATCH** |
| DIFF DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_DIFF_DRAFT_20261027.diff` | `f583b616` | `f583b61645ad5a8fd2dd8e116fd91d60cc34f448e95c3fa65723b06112876919` | **MATCH** · NEW；重建字节 **≡脚本** |
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `8be1099e` | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` | **MATCH** |
| Arch FROZEN 审 | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `027efa26` | `027efa26093696e2684a44784b1c2cfba2e907d7027f95ace4ba0e4eae22fe4b` | **MATCH** |
| FROZEN RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `438ee33d` | `438ee33dc3acd8c5781af1c983b78246bdd0082db1e868ea4bcd8ee5a0dbf01a` | **MATCH** |
| PIN 决议（C3） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` | `bb418e6a` | `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `9d8a2f9e` | `9d8a2f9edde9f00ae230b9914025fc95db2fba35dc102f83c2a38c26d8247ecd` | **MATCH**（只读引用） |
| 叶33 正式（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| 叶32 模板（只读） | `research/leaf32_margin_net_flow_resid_alpha_build.py` | `4e0f3c00` | （只读未改） | **UNCHANGED** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH**（不回撤） |
| 对照模板（只读） | `docs/v2/audit/ARCH_LEAF33_…_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` | （形态对照） | — | **只读** |
| live leaf34 `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF34*` | ABSENT | — | **ABSENT** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | — | **ABSENT** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| 叶30 KEEP `0087c928` | 衰减修复 DRAFT | 另队 | 本拍**未打开/未审** | **未审声明** |

哈希闭环：脚本/RECEIPT/COVER/CMD/DIFF 互指 sha8 与盘上一致；脚本常量钉 FROZEN `8be1099e` / FROZEN 审 `027efa26` / who_pays `9d8a2f9e` / PIN `bb418e6a` / FROZEN RECEIPT `438ee33d` / 叶33 `afbbe7e7` / 叶32 HOLD `45dd87dc`。DIFF 自 `/dev/null` NEW 重建内容 **字节等于** 脚本（sha 同 `482009dc`）。

## 2. 必审清单（脚本 vs FROZEN `8be1099e` / 审 `027efa26` / PIN `bb418e6a`）

| # | 审点 | 结果 | 证据 |
|---|---|---|---|
| 1 | **C2** 哈希闭环 + 机制对齐：mask-only overlay；`accrual_cf=1−ocf_to_profit`；top_q=0.20；再平衡 20；≠CFACC TopN / Amihud / unlock / margin 主输入；避 19/25/27/30–33 同构主叶 | **PASS** | `MECHANISM_TAG`；`PRIMARY_DELIVERY=mask_only`；`TOP_Q=0.20`；`REBAL_EVERY=20`；`ALPHA_SIGN=high_accrual_mask0_exclusion`；dry bans：`ban_cfacc_topn_main` / `ban_accrual_quality_topn_main` / `ban_leaf19_25_alpha_as_main_input` / `ban_amihud_main` / `ban_share_unlock_main` / `ban_margin_flow_main`；常量钉 FROZEN/PIN/ArchFROZEN |
| 2 | **PRIMARY 纪律**：HI_LIQ mask-only；禁静默 FULLA；soft-penalty 非 PRIMARY | **PASS** | dry/run `--universe FULLA` STOP exit2；`ban_silent_fulla_as_primary=true`；`SOFT_PENALTY_DEFAULT=False`；`soft_penalty_is_primary=false`；`--enable-soft-penalty` 可选且须 style 列，缺→PIN_GAP |
| 3 | **C3** 脚本落地：日表路径 + PIT `e_available_at≤t` + 有效行合取 + NP≤0 剔除 + YTD；禁改 PIN 语义 / 禁 BS WC PRIMARY | **PASS** | `_load_ocf_one_day`：filter trade_date + `eav≤d` + `period_basis∈YTD*` + valid（ocf finite ∧ ~denom_small ∧ net_profit>0 ∧ ~np_negative）；`C3_FORMULA_PIN`；`OCF_DAILY_SHA8_PIN=f9faf7e7`；`ban_bs_wc_acc_primary=true`；`ACCEPTED_PERIOD_BASIS=("YTD_cumulative",)` |
| 4 | **C7 / X2 前重叠**：vs 19/25/27/30–33 + Jaccard≥0.7 硬拒 + ρ>0.5 强度 + 叶25 尾窗；CMD/COVER 可见（本拍不签不跑） | **PASS_WITH_CONDITIONS** | `write_overlap_report` → `overlap_vs_leaf19_25_27_30_31_32_33.json`；缺→`any_required_pin_gap`；Jaccard 硬拒 return **4**；CMD/COVER 明示完整重叠须签窗前重算；CLI 仍保留 `--no-overlap-report` 但真跑硬 STOP → **仍须入签文硬闸**（双保险） |
| 5 | **C9** 内存：rss=1500 + peak_proof；禁抬 | **PASS** | `RSS_LIMIT_MB=1500`；抬 rss → STOP；`check_rss` 于 after_mask / after_ocf_rebal_* / after_mask_cs_rebal_* / after_daily_concat；`primary_load=rebal_day_lazy_ocf_daily_pit`；dry `sign_notes.peak_proof_required` 齐全 |
| 6 | **C8** forbid `245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`；禁 RESTORED；禁 `--force`/盲 seed；`--arch-ok-path` 已实现 | **PASS** | `FORBID_OK_SHA8` **24** 项含四硬钉+`81521fb5`；真跑须现存 `--arch-ok-path` 且 sha8∉forbid；无写 `.ok` 逻辑；源码无 `--force` |
| 7 | **C13** decay KEEP 三闸+KEEP 不解阻仅钉（本脚本不执行闸） | **PASS** | `DECAY_KEEP_PIN`（三闸合取；near=252；`keep_does_not_unblock_x2_accept=true`）；meta note 不跑 decay；`ban_selfcheck=true` |
| 8 | **C10**：`0087c928` 另队未审、未夹带；叶28/29 另队 | **PASS（未审声明）** | `LEAF30_KEEP_REPAIR_SHA8_SEPARATE=0087c928`；本拍未打开/未审该 DRAFT；叶28/29 不夹带 |
| 9 | **C11/C12**：overlay≠应计主叶；APPROX≠X2 ACCEPT | **PASS** | 交付 exclusion mask；`ban_cfacc_topn_main`；`count_approx_not_x2_accept=true`；文钉 ≠X2 ACCEPT |
| 10 | 模板/DIFF：相对叶32/33 形态合理（机制换皮，非乱改主干）；叶33/32 未回撤 | **PASS** | DIFF `f583b616` 标 NEW；语义=mask-only high-accrual overlay；叶33 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 骨架 **`4e0f3c00`** 只读 |
| 11 | dry-compile PASS；CMD 拟 approved_cmd 含未来新 `.ok`；禁不当旗标；EXECUTED=false；live ok/QUIET ABSENT；COVER/CMD/RECEIPT 互钉 MATCH | **PASS** | 本机复跑见上；CMD 拟 `…LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok`（未创建）；禁 `--no-overlap-report` / 禁 FULLA PRIMARY；RECEIPT EXECUTED=false；五件互钉 MATCH |

## 3. 残留风险（知情接受 · 签窗监控）

| 风险 | 等级 | 备注 |
|---|---|---|
| `after_daily_concat` 残峰仍可能逼近 split | **中** | 月分片后一次 concat；须 peak_proof；破→停+上报；**禁抬帽** |
| 再平衡日懒加载 ocf 大表 I/O | **低–中** | `primary_load=rebal_day_lazy_ocf_daily_pit`；可接受 |
| CLI `--no-overlap-report` 仍在（真跑已硬 STOP） | **管控** | 靠脚本硬 STOP + 签文双闸；消费端须读 overlap JSON（含 vs leaf33） |
| soft-penalty 启用路径（非 PRIMARY） | **管控** | 默认关；启用须另窗+SW+style；不得抬作 PRIMARY 判决 |
| FULLA 研究失败仅 WARN | **低** | PRIMARY HILIQ 已写；研究失败不抬 PRIMARY |
| COUNT APPROX / KEEP 被误读为 ACCEPT | **管控** | 文钉+脚本钉均明示不解阻；签窗再钉 |

## 4. CONDITIONS（另窗签新 X2 `.ok` 前）

1. **本拍不签**：须主另排**独立 X2 签窗**；**新** `.ok`（建议名 `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.ok` 或主定新名）；钉脚本 sha8 **`482009dc` only**。
2. **禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)**：forbid∋24 sha8；禁复用叶25/27/30–33 任一 `.ok`。
3. **真跑前主 MATCH**：script sha256 全长 `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc`；dry-compile PASS；FROZEN `8be1099e` / FROZEN 审 `027efa26` / PIN `bb418e6a` / FROZEN RECEIPT `438ee33d` / 本审回执。
4. **peak_proof REQUIRED**：回执须含 `after_mask` / `after_ocf_rebal_*` / `after_mask_cs_rebal_*` / `after_daily_concat`（及 ru_maxrss/VmHWM/`RSS_CHECK`）；破 soft/hard → 停+上报；**rss=1500 禁抬**。
5. **C7 签文硬钉**：真跑**必须**写并消费 `overlap_vs_leaf19_25_27_30_31_32_33.json`；Jaccard≥0.7 → 硬拒；ρ>0.5 → 强度；缺→PIN_GAP；须披露叶25 尾窗 n_common + ρ_max；签文 **禁** `--no-overlap-report`（脚本已硬 STOP，签文双保险）。
6. **C3 签文硬钉**：日表路径 + `e_available_at≤t` + NP≤0 剔除 + YTD_cumulative；禁事后改 period_basis / 升 BS WC / 改 PIN 语义。
7. **PRIMARY 纪律**：判决=HILIQ **mask-only** top_q=0.20；FULLA 仅 `--also-fulla-research`；不得静默改 FULLA 作 PRIMARY；soft-penalty 启用须另窗+SW+style，**不得**作 PRIMARY。
8. **PRIMARY CLI 钉**（无 `--no-overlap-report`）：
   `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path <NEW_OK> --out output/ai_factory/_leaf34_high_accrual/<ET_TS>/`
9. sampler `/tmp/quantlab_leaf34_high_accrual_*`；out `_leaf34_high_accrual/<ET_TS>/`；Arch **不代跑**；可挂 leaf34 自有 QUIET（当前 QUIET **ABSENT**）。
10. **C10 仍另队**：`0087c928` / 叶28/29 不得借本脚本/签窗夹带。
11. **C13 另窗**：decay KEEP 硬验收不在本构建脚本；X2/selfcheck 另窗；失败最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT。
12. live=false · promotion=false · book_smoke=false · **x2_accept=false** · selfcheck=false · **≠X2 ACCEPT** · COUNT APPROX 不解阻。

## 5. 禁项 / 本回合非动作

- **未签**任何 `.ok`（含新叶34 / RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票+`81521fb5`）
- **未挂** QUIET；live QUIET **ABSENT**（未改）
- **未改** 脚本 `482009dc` / COVER / CMD / DIFF / RECEIPT / FROZEN / PIN
- **未** `--allow-real-data` / **未** `--execute` / **未**代跑真构建（仅 `py_compile` + dry）；repo `__pycache__/leaf34*` **ABSENT**；`output/ai_factory/_leaf34*` **ABSENT**
- **未** RESTORED；**未**抬 rss；**未**触 A18 产物
- **未审**叶30 衰减修复 `0087c928`（另队）；**未打开**该 DRAFT；**未夹带**叶28/29
- **未改** 叶33 正式 `afbbe7e7`；**未回撤** 叶32 HOLD `45dd87dc` / 模板 `4e0f3c00`
- **≠X2 ACCEPT** / ≠selfcheck / ≠Book-Smoke
- **未** SendToUser / **未**报 Leo（leo_notify=false）

## 6. 硬钉下一跳

```
脚本 482009dc（本审 PASS_WITH_CONDITIONS · FROZEN 8be1099e / 审 027efa26 / PIN bb418e6a / RECEIPT 438ee33d / who_pays 9d8a2f9e）
  → 请主另排独立 X2 签窗（新 .ok；钉 482009dc；§4 CONDITIONS）
      → AI prelaunch→execute（无 --no-overlap-report；peak_proof；overlap 含 vs leaf33；C3 PIT/NP 钉；mask-only PRIMARY）
          → Arch CONSUME（≠X2 ACCEPT）
```

**本拍不签**。

## 7. 结论

| 项 | 值 |
|---|---|
| VERDICT | **PASS_WITH_CONDITIONS** |
| 脚本 | **`482009dc` MATCH** |
| RECEIPT / COVER / CMD / DIFF | **`f73c986f`** / **`c491e7a4`** / **`cfa3ca4e`** / **`f583b616`** MATCH |
| FROZEN / FROZEN 审 / PIN / FROZEN RECEIPT / who_pays 审 | **`8be1099e`** / **`027efa26`** / **`bb418e6a`** / **`438ee33d`** / **`9d8a2f9e`** MATCH |
| 叶33 正式 / 叶32 HOLD | **`afbbe7e7` UNCHANGED** / **`45dd87dc`** 不回撤 |
| dry-compile | **PASS**（exit0）；FULLA PRIMARY STOP exit2；无授权 STOP exit2 |
| EXECUTED | **false** |
| live `.ok` / QUIET | **0** / **ABSENT** |
| 请主 | **另排独立 X2 签窗**（钉 `482009dc`；本拍不签） |
| live | **false** |
| leo_notify | **false** |

live=false · leo_notify=false · ≠X2 ACCEPT · 只审不签不挂不代跑.

## 8. 本审钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_ALPHA_BUILD_SCRIPT_REVIEW_20261027_ZH.md` |
| 脚本 sha8 | **`482009dc`** |
| RECEIPT / COVER / CMD / DIFF | **`f73c986f`** / **`c491e7a4`** / **`cfa3ca4e`** / **`f583b616`** |
| FROZEN / FROZEN 审 / PIN / FROZEN RECEIPT / who_pays 审 | **`8be1099e`** / **`027efa26`** / **`bb418e6a`** / **`438ee33d`** / **`9d8a2f9e`** |
| 结论 | **PASS_WITH_CONDITIONS**（本拍不签；请主另排独立 X2 签窗） |

全文件 sha256 / sha8：以本机 `sha256sum` 为准（见 TEAM_STATE 顶条与父回报）。

live=false.
