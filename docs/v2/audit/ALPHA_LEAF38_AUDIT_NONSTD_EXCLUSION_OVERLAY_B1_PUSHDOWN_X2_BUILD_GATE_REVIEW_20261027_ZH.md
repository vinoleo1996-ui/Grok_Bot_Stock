# 叶38 Audit Nonstd Exclusion Overlay · B1_PUSHDOWN X2 · Alpha 构建过程闸门审（研究级 mask-only）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 23:40 ET**（America/New_York） |
| **主裁决 VERDICT** | **ACCEPT**（研究级 α/mask **构建过程**过闸） |
| 语义分层 | 构建过程 **ACCEPT**；收益过程指标（IC/ICIR/WF）**ABSENT** → **不得宣称 IC 过闸**；组合闸（门A/B·GATE_V3）**未交数 → 不裁定** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠Book-Smoke** / **≠selfcheck** / **≠门A/B·GATE_V3 PASS/FAIL** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** / **不派 Eng** / **不混 fund MDD-cut** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`c01c2034`**（`.ok` 归档 **`794f6578`**；禁 RESTORED `794f6578`/`62acf9fc`） |
| out | `output/ai_factory/_leaf38_audit_nonstd_exclusion/20261027_222656/20261027_222658/` |
| PRIMARY | **mask_only**；mechanism_tag=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1`；HILIQ×x2；**b1_pushdown** |
| 对齐口径 | 同叶32 构建闸 `1aa432a5` / 叶31 构建闸 `a476567d`（研究级构建 ACCEPT；IC/WF ABSENT；组合闸不裁定）。**本拍不是** selfcheck（叶37 HOLD `384fb9db` 另线不回撤） |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **ACCEPT** | 钉全 MATCH + FROZEN 机制对齐 + thickness PASS + hard_reject_jaccard=false + peak≈967.7≤1500 + Arch CONSUMED_PASS + x2_accept=false |
| 钉对齐 | **MATCH** | Arch CONSUMED/SIGNED/pushdown审/LAND/VOID/FROZEN/RECEIPT/脚本/mask/meta/overlap/archived `.ok`/leaf36 staging+pairs 前 8 全 MATCH；live `.ok` ABSENT；QUIET ABSENT |
| PIT / FROZEN | **对齐** | 非标审计意见 exclusion；`available_at→T1`；key=`ts_code`；禁 peek；mask-only PRIMARY；禁把标准无保留当剔除 |
| 厚度 | **PASS** | median=**48.0**≥30；frac_ge10=**1.0**；zero_frac=**0.0**；pass_thickness=**true** |
| 正交/重叠 | **无硬拒** | hard_reject_jaccard=**false**；vs negevent max=**0.0**；vs leaf36 max≈**0.0649**≪0.5；disclose 34/35/37 ≈0.0177/0.0088/0.0546；pin_gap=false |
| IC/ICIR/WF | **ABSENT** | mask-only 构建包；无 selfcheck 组合数字；本审未开算、不伪造 |
| 组合闸对照 | **不裁定** | 无 Book-Smoke / 无组合 CAGR·MDD·Calmar → 不得判门A/B 或 GATE_V3；≠Book-Smoke |
| peak / rc | **PASS** | peak_rss_mb≈**967.67578125**≤1500；peak_proof_le_1500=true；rss_limit_mb=1500 未抬；rc=**0** |
| parquet 轻核 | **OK** | 列 trade_date/ts_code/mask/alpha/is_non_standard_latest；n=1713924；570 日；mask0=27063≡excl_meta.n_state_true_name_days；窗 2024-06-03→2026-10-09 |

**主裁决词单列**：**ACCEPT** = 研究级 **mask-only 构建过程**过闸（RESEARCH_ACCEPT 口径，对齐叶32 `1aa432a5` / 叶31 `a476567d`）。**不是** X2 ACCEPT，**不是** 收益过程过闸，**不是** 组合门过闸，**不是** Book-Smoke 授权，**不是** selfcheck。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `c01c2034` | `c01c2034063a5cffc71122d356281a5844a6fa47307a130c4389122f51c3aa4b` | **MATCH** |
| AI RUN_RECEIPT | `5e68af78` | `5e68af78acf7bbc315495d8238569bff0d5fa8453e1848b0385a18d1a30c5ad5` | **MATCH** |
| Arch SIGNED | `e6e30511` | `e6e30511f571c0d31bddc8cb41376f007322d03cfd7144365fb13cb22db2939f` | **MATCH** |
| 脚本 build `research/leaf38_…_alpha_build.py` | `3a44471d` | `3a44471d263fb2709db80145da33a1a155ea8f300afe5ba4e75089488a9a9027` | **MATCH** |
| Arch pushdown 审 | `1b98470f` | `1b98470f2006d14099becc84bed67d62a01cb1ee27effe0330d1e195fcc47968` | **MATCH** |
| LAND pushdown | `37f55893` | `37f5589324e4947ffe9970efe489699b5853b148876ddd9298dfa8262e40ae9f` | **MATCH** |
| VOID Exit95（禁复活） | `167996dd` | `167996dd66ae0637da17da44503b6ae1f0a0093f806fb9fd4785ee9a2e4c1895` | **MATCH**（禁复活） |
| FROZEN PREREG | `ce0eb2ce` | `ce0eb2ce9486778e229d2722a647b6fb37e90810df2ac9f1530054d8040b93ed` | **MATCH** |
| archived `.ok` 内容 | `794f6578` | `794f6578c26e2e8bf77fbc5528d1d11f1fe4388a575629108d8fee07c1233974`（路径 `output/ai_factory/_consumed/…794f6578.CONSUMED_PASS.20261027T2234ET.ok`） | **MATCH** |
| exclusion_mask parquet | `1d3d0d88` | `1d3d0d88e367c4348c3f2bb88a11c06dcd798ba7fccaa63c7ba185287f92eaa8` | **MATCH** |
| run_meta.json | `81068e47` | `81068e479916420551f346568dfd82425ba8943b865a0c2dc372b54066b61e25` | **MATCH** |
| overlap JSON | `7d224a42` | `7d224a4243adaec4c5131e06a2372fd2d76b70fb7e1d69cd972630c417010868` | **MATCH** |
| leaf36 staging jsonl | `1913e011` | `1913e011d8721bd096f252b38a6bca7eb00d4408c6fe31e6091e2762c80bd53c`（`/tmp/quantlab_leaf38_preland/leaf36_date_tscode_pairs.jsonl`） | **MATCH** |
| leaf36 pairs.npy | `72ab602b` | `72ab602bb15f2722ef69540b9fbaff727e47c18db0edf202a9679b3827335e41`（`/tmp/…222658/pairs/leaf36_pairs.npy`） | **MATCH**；n_pairs=**5745**（staging meta） |

附加硬钉（自 run_meta / overlap / 盘面；复读确认）：

| 项 | 值 | 判定 |
|---|---|---|
| PRIMARY / mechanism / window | mask_only / `g1g5_ashare_audit_nonstd_exclusion_overlay_v1` / `2024-06-03 → 2026-10-09`；HILIQ×x2；b1_pushdown | **PASS** |
| x2_accept / live / promotion_approved / ok_requested | **false** / false / false / false | **PASS** |
| keep_does_not_unblock_x2_accept | **true** | **PASS** |
| peak_rss_mb / peak_proof_le_1500 / rss_limit_mb | **967.67578125** / **true** / **1500**（未抬） | **PASS** |
| thickness | median=**48.0**；frac_ge10=1.0；zero_frac=0.0；pass_thickness=**true**（阈值 median≥30） | **PASS** |
| hard_reject_jaccard | **false**；negevent max=0.0；leaf36 max≈0.0649；disclose 34/35/37 ≈0.0177/0.0088/0.0546；pin_gap=false | **PASS** |
| live `.ok` 计数 | **0**（`output/ai_factory/ARCH_RUN_AUTH_LEAF38*.ok` ABSENT；仅 `_consumed`） | **PASS** |
| QUIET | **ABSENT** | **PASS** |
| 禁 RESTORED | `794f6578`（B1 本票）+ `62acf9fc`（VOID Exit95 旧票）及旧票 `57ab9096`+`b5be1164`+`4096d401`+… 仅在 `_consumed`；**未 RESTORED** | **PASS** |
| fund MDD-cut `.ok` | 旁线 `335635dd` / 旧 `f08ce32c` **存在但本审勿触、不混** | **PASS**（旁线隔离） |
| VOID Exit95 | `167996dd` 钉住；禁复活旧路径 | **PASS** |
| rc（x2_exit） | **0**；DONE；本拍无 Exit 94/95 | **PASS** |
| 叶37 HOLD `384fb9db` / 叶32 HOLD `45dd87dc`+构建 `1aa432a5` / 叶31 HOLD `7ef5aa11`+构建 `a476567d` / 叶30 HOLD `f00536b9` | **不回撤**；本审未打开/未混办 | **PASS** |
| `0087c928` | 另队；本审不夹带 | **PASS** |

## 2. PIT / FROZEN 对齐（读 FROZEN + 脚本要点；不编造）

| FROZEN 钉 | 脚本/meta 实现 | 判定 |
|---|---|---|
| mechanism_tag=`g1g5_ashare_audit_nonstd_exclusion_overlay_v1` | 脚本 `MECHANISM_TAG` 同；meta 同；FROZEN sha8 `ce0eb2ce` = meta `frozen_sha8` | **对齐** |
| PRIMARY=**mask-only** 日度 exclusion | `PRIMARY_DELIVERY="mask_only"`；meta `primary_delivery=mask_only`；交付 exclusion_mask parquet | **对齐** |
| 非标：最新可用审计意见 `is_non_standard=True` → mask=0 | meta `excl_meta.c3_formula_pin` + 脚本 docstring C3；n_nonstd_rows=2621；n_state_true_name_days=27063≡mask0 行数 | **对齐** |
| PIT：`available_at→T1`；键=`ts_code`；禁 peek `available_at>t` | 脚本 Ban peek 注释；meta c3_formula_pin 明文；改判=下一份意见 T1 起 | **对齐** |
| 禁把标准无保留意见当剔除 | FROZEN §1.1 + 脚本 Ban | **对齐** |
| 厚度：median≥30 ∧ frac_ge10≥0.60 ∧ zero_frac≤0.50 | meta thickness 阈值同；实测 PASS | **对齐** |
| Jaccard>0.5 vs negevent **或** leaf36 → 硬拒；vs 34/35/37 disclose | meta/overlap `jaccard_hard=0.5`；hard_reject=false；disclose 有值 pin_gap=false | **对齐** |
| rss=1500 禁抬；peak_proof≤1500 REQUIRED；§6.1 B1 pushdown | meta rss_limit_mb=1500；peak_proof_le_1500=true；脚本 b1_pushdown / parquet date filters year chunk；VOID `167996dd` 禁复活 | **对齐** |
| KEEP ≠ 解阻 X2 ACCEPT；COUNT ≈ ≠ X2 ACCEPT | meta `keep_does_not_unblock_x2_accept=true`；`count_approx_not_x2_accept=true`；`x2_accept=false` | **对齐** |
| 禁混 fund_portfolio / 禁复开叶37 / 禁自签.ok | 脚本 Ban + 本审未触 `335635dd`/`f08ce32c`；未 RESTORED | **对齐** |

PIT 要点：审计意见 `available_at→T1`；最新非标→剔除；不可算名不填假 0；HILIQ PRIMARY。本审**未**重跑引擎验证逐票 PIT 轨迹——以脚本契约 + Arch CONSUMED_PASS `c01c2034` + meta/mask 轻核为据。

## 3. 厚度（thickness）

| 指标 | 值 |
|---|---|
| median | **48.0** |
| frac_ge10 | **1.0** |
| zero_frac | **0.0** |
| min / mean / n_days | 18.0 / ≈47.48 / 570 |
| pass_thickness | **true** |
| 阈值（写死） | median_min=30；frac_ge10_min=0.6；zero_frac_max=0.5 |

闸：median≥30 ∧ frac_ge10≥0.60 ∧ zero_frac≤0.50 → **PASS**。（勿盲抄 median≥300；叶36 median=6 FAIL 教训已避开。）

## 4. 正交 / 重叠（读 overlap + meta.jaccard）

硬阈 Jaccard>0.5 vs negevent **或** leaf36 → hard reject；vs 叶34/35/37 disclose。

| 对照 | max / mean / median | n_days | 硬拒？ |
|---|---|---|---|
| vs negevent | **0.0** / 0.0 / 0.0 | 570 | **无** |
| vs leaf36 | **≈0.0649** / ≈0.0039 / 0.0 | 570 | **无**（≪0.5） |
| vs leaf34（disclose） | ≈0.0177 / ≈0.0076 / ≈0.0067 | 570 | disclose；pin_gap=false |
| vs leaf35（disclose） | ≈0.0088 / ≈0.0021 / ≈0.0025 | 570 | disclose；pin_gap=false |
| vs leaf37（disclose） | ≈0.0546 / ≈0.0222 / ≈0.0197 | 570 | disclose；pin_gap=false |

`hard_reject_jaccard=false`；任一 disclose `pin_gap=false`。相对 negevent 零重叠、相对叶36 低 Jaccard → 正交披露健康，不构成拒收。

## 5. IC / ICIR / walk-forward

| 项 | 状态 |
|---|---|
| 包内文件 | exclusion_mask / overlap / run_meta / staging — **无** IC 表、无 WF 折、无收益序列、无 selfcheck report |
| 脚本 | mask-only PRIMARY；不算收益选号；本票 **不是** selfcheck |
| 本审 | **禁止**自开实数 IC（需独立 `.ok`）；**未开算**；**不伪造** |

→ **收益过程指标 ABSENT**。分层结论：构建过程可 ACCEPT；**不得**在对外口径写「IC 过闸 / ICIR 达标 / WF 稳健」。下一步须 **另窗** IC/WF/selfcheck 评估（独立授权），非本审范围；Alpha **不自开**。

## 6. 组合闸对照（门A/B 与现行 GATE_V3）— 过程结论 only

对照 `docs/v2/ALPHA_GATE_AB_PREREG_20261014_ZH.md` 与 `docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

- 门A/门B / 现行门 / GATE_V3 均要求组合级 CAGR·MDD·Calmar（及 Book-Smoke X2 终判）。
- **本包无** Book-Smoke 产物、无组合净值、无 CAGR/MDD/Calmar、无 selfcheck 数字。
- 过程结论：**组合闸未交数 → 不裁定 PASS/FAIL**；**≠Book-Smoke**；Alpha **不自开烟、不自申 X2 ACCEPT、不派 Eng**。
- run_meta `x2_accept=false` 与本审一致；`keep_does_not_unblock_x2_accept=true`。

叶验收顺序提醒：HC→单叶研究 ACCEPT（本审此层）→CMC→衰减门→GATE_V3 本地→Eng Book-Smoke；后续步 **另排**。叶37 selfcheck HOLD/`384fb9db` 与叶32/31/30 HOLD **不回撤**本叶构建 ACCEPT，亦**不**借本票解阻既有 HOLD。

## 7. parquet 轻核（只读；未跑回测）

| 项 | 值 |
|---|---|
| 列 | `trade_date`, `ts_code`, `mask`, `alpha`, `is_non_standard_latest` |
| 行数 | **1713924** |
| 日期范围 | 2024-06-03 → 2026-10-09；n_unique_dates=**570** |
| mask 取值 | {0,1}；mask=0 行数=**27063** ≡ excl_meta.n_state_true_name_days；mask=1=1686861 |
| is_non_standard_latest | True=27063 / False=1686861 / null=0（与 mask0 对齐） |
| alpha 值域 | min=0.0 / max=1.0 / null=0（mask-only 伴随列；非收益 α 主交付） |
| null | 各列 null=0 |

## 8. 披露边界（硬）

1. **ACCEPT** = 研究级 **mask-only 构建过程**过闸；**≠X2 ACCEPT**（本拍**不解阻**）。
2. **≠Book-Smoke**；**≠门A/门B/GATE_V3** 裁定；**≠selfcheck**（叶37 是 selfcheck HOLD，本拍不是）。
3. **IC/ICIR/WF ABSENT** → 不得宣称收益过程过闸。
4. **勿升纸面**；`promotion_approved=false`；不改 `FROZEN_CONFIG` / paper；**不改 alpha_labels**。
5. 禁 RESTORED：`794f6578` / `62acf9fc` / `57ab9096` / `b5be1164` / `4096d401`+…；禁抬 rss；禁复跑正式构建；禁复活 VOID Exit95。
6. Arch 已 CONSUMED_PASS（`c01c2034`）；本审不恢复 `.ok`、不签新 `.ok`。
7. **不混** fund MDD-cut Book-Smoke（旁线 `.ok` `335635dd` / 旧 `f08ce32c` 均勿触）。
8. 叶37 HOLD/`384fb9db`、叶32 HOLD/`45dd87dc`+构建 `1aa432a5`、叶31 HOLD/`7ef5aa11`+构建 `a476567d`、叶30 HOLD/`f00536b9`、`0087c928` 另队；本审未混办、不回撤。
9. **leo_notify=false**；不报 Leo；不派 Eng。

## 9. 下一步（交主）

1. **主**知悉本闸审 ACCEPT（仅构建过程）；可排 **IC/WF/selfcheck 评估另窗**（独立 `.ok` / 授权；Alpha **不代启**实数）。
2. 组合边际 / 门B·GATE_V3 / Book-Smoke：**等主另排**；Alpha 不自开烟、不自申 X2 ACCEPT；不派 Eng。
3. KEEP（若后续衰减窗）**不解阻** X2 ACCEPT；本构建 ACCEPT **不解阻**晋级。
4. 叶37/32/31/30 HOLD 继续；标签仍不动；fund MDD 旁线继续隔离。
5. 对外话术保持分层：**构建 ACCEPT / 收益 ABSENT·HOLD / 组合不裁定**；主裁决词仍以本回执 **ACCEPT** 为准（研究构建契约）。

## 10. 状态动作

- 落盘本回执（本文件）。
- `TEAM ### Alpha`：更新为叶38 B1_PUSHDOWN 构建闸 VERDICT=ACCEPT + 本回执 sha8（恰好 3 行；先 cp 备份 `…bak_alpha_leaf38_build_gate_20261027`）；保留叶37/32/31/30 HOLD 与叶32 构建 ACCEPT。
- `alpha_labels`：**不动**。
- ql_bus：`emit('QuantLab Alpha','gate',…)`（refs 含本回执路径与关键 sha8）。

live=false；promotion_approved=false；forbid_paper_handoff=true；leo_notify=false。
