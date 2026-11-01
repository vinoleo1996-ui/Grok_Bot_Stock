# Arch 审阅：叶34 高应计剔除 overlay PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T10:10:00-04:00`（America/New_York；墙钟 `2026-10-27 10:10 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/PIN/RECEIPT/WHO/COVER/COUNT；**不触** A18；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；`0087c928`/叶28/29 **另队不夹带**；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 10:06 ET 令 Arch 只审本 FROZEN（对照 who_pays 审 C1–C13；TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN **`8be1099e`** / PIN(C3) **`bb418e6a`** / RECEIPT **`438ee33d`** / 上游 who_pays 审 **`9d8a2f9e`** / WHO **`fa6aa2e3`** / COVER **`76b37ca3`** / COUNT **`806e1758`** / JSON **`9730d432`** 本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**（非仍标 DRAFT）；mechanism=`g1g5_ashare_high_accrual_exclusion_overlay_v1`；**PRIMARY=mask-only** top_q=**0.20**（高应计=剔除）；soft-penalty **明示非 PRIMARY**；C3 PIN 与日表 PIT/NP≤0/YTD-ish 一致；C1–C13 契约入钉；HI_LIQ PRIMARY + FULLA 研究双钉；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；vs 19/25/**27/30–33** 完整重叠须 X2 前重算；forbid 含 `81521fb5`；rss=1500+peak_proof；decay KEEP 三闸 + KEEP 不解阻；C12 APPROX≠ACCEPT；C11 overlay≠应计主叶；`research/leaf34*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false。开放余项：正式构建脚本另窗（C2）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `8be1099e` | `8be1099e73c6029ad2ddcbe7a18a28fc5a27cc03acfb91cba048e26b7867f815` | **MATCH** |
| PIN（C3） | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_OCF_PIT_PIN_20261027_ZH.md` | `bb418e6a` | `bb418e6ae8ee7fd2b0cfc6816360bcb7bb197537dc1aac44fcfb05d375224e9b` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `438ee33d` | `438ee33dc3acd8c5781af1c983b78246bdd0082db1e868ea4bcd8ee5a0dbf01a` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `9d8a2f9e` | `9d8a2f9edde9f00ae230b9914025fc95db2fba35dc102f83c2a38c26d8247ecd` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `fa6aa2e3` | `fa6aa2e3ffb084cc01f6a4d20575e528f1c095262c10a00e70dadb4c15cc473b` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `76b37ca3` | `76b37ca33be72f5311ded30693493ab431b5ac0820730c2f4d0081cfe9b5aa8c` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `806e1758` | `806e17589697c48c0078cc43f42c01736a80b1995a71947484358cc4c2c4aae9` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` | `9730d432` | `9730d432735f48892eaceb0c3c8d73f3a104d4cf32a73dd0863cc9a23f546731` | **MATCH** |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH**（不回撤） |
| 构建脚本 `research/leaf34*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶34 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF34*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |

对照形态：叶33 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md`；叶31/32 FROZEN 审结构对齐（机制/符号/正交/宇宙/窗/decay/forbid/状态机；本叶另钉 C3 PIN + mask-only PRIMARY + C11/C12）。

## 2. C1–C13 对照表（相对 who_pays 审 `9d8a2f9e`）

| # | who_pays 条件 | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C1** | 须另窗冻结预注册（相对 DRAFT） | 状态 **FROZEN**；冻结时点 10:03 ET；明示「冻结前**未**读任何本叶收益选 λ/q/方向」；相对 who_pays/COVER/COUNT DRAFT **升格**；mask-only / q / 再平衡 / 失效 / 交付写死 | **PASS** |
| **C2** | 正式构建脚本尚未写；本冻结≠脚本 | 文首 + §14：本冻结 ≠ 构建脚本；`research/leaf34*` **ABSENT**（本拍禁落）；脚本另窗 | **PASS_WITH_CONDITIONS**（余项：另窗落脚本） |
| **C3** | ocf/PIT/NP≤0/period_basis 写死 | §1.1 + PIN **`bb418e6a`**：日表路径+行数+sha；`e_available_at≤t`；有效行合取；**NP≤0 一律剔除**；接受 YTD-ish/`YTD_cumulative`（与 COUNT 同口径）；PRIMARY 不用 BS WC；改季表/TTM 须补丁+重计数 | **PASS**（与 PIN 一致） |
| **C4** | soft-penalty / mask-only 明示 | §1.2/§3：**明示 mask-only PRIMARY**；连续 soft-penalty **非 PRIMARY**；启用须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP | **PASS** |
| **C5** | top_q=0.20 符号冻结 | §1.2/§2：q=**0.20**；「高应计=剔除」；禁读收益改阈值/翻方向 | **PASS** |
| **C6** | FULLA 双钉 | §5：HI_LIQ_V1.1 **PRIMARY**（median≥300）+ FULLA_V1 **研究**（median≥800）；明示「PRIMARY 不得静默改 FULLA」 | **PASS** |
| **C7** | X2 前完整重叠 | §4：vs 19/25/**27/30–33** Jaccard≥0.7 **硬拒**；ρ>0.5 **强度过滤**；须解释叶25 尾窗 n_common=0；披露 ρ_max vs25；COUNT 轻量不能替正式重叠 | **PASS** |
| **C8** | 禁 RESTORED / 禁复用旧窗 | §10：forbid∋`245df63f+c5ed13df+5774bb6e`+二十票+**`81521fb5`**；禁复用叶25/27/30–33 `.ok`；禁 `--arch-ok-path` 自开 | **PASS** |
| **C9** | rss=1500 + peak_proof | §6：rss **1500** MB 禁抬；peak_proof **REQUIRED**；未来执行窗硬 ABORT | **PASS** |
| **C10** | `0087c928`/叶28/29 另队 | §11：叶30 KEEP 修复 **`0087c928` 另队不并入**；叶28/29 仍 FROZEN 不夹带；本拍未打开/未审 | **PASS（未审声明）** |
| **C11** | overlay ≠ 应计主叶 | §1.2/§9：交付=**mask-only overlay**；禁 CFACC/accrual_quality TopN 主 α；禁叶19/25 α 主输入；≠重开叶19/25/accrual_quality | **PASS** |
| **C12** | APPROX ≠ X2 ACCEPT | §0/§6/§12/§13：COUNT gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke | **PASS** |
| **C13** | decay KEEP | §7：近端=**252**d（≥126 日出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 HOLD `45dd87dc`） | **PASS** |

### 附加硬钉（任务清单）

| 项 | 结果 | 证据 |
|---|---|---|
| 真正 FROZEN（非仍标 DRAFT） | **PASS** | 文首状态 **FROZEN**；冻结时点 10:03 ET；§16 状态钉 |
| PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY | **PASS** | §1.2/§3/§16；RECEIPT 机制钉 |
| 机制与 who_pays/COVER 无静默改号 | **PASS** | mechanism 同 tag；公式 `accrual_cf=1−ocf_to_profit`；q=0.20；再平衡 20 |
| ≠重开叶19/25/accrual_quality | **PASS** | §0 失效 + §9 分家 + C11 |
| 失效条件 / Jaccard 硬拒 / 禁卖方 | **PASS** | §0 失效；§4 Jaccard；§15 禁卖方/金股/LLM/GP/高杠杆 |
| 脚本仍 ABSENT（预期） | **PASS** | 盘证 §1；CONDITIONS 保留 C2 |
| 未申请 .ok / 未挂 QUIET | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 叶33 `afbbe7e7` UNCHANGED / 叶32 HOLD 不回撤 | **PASS** | 只读对照 §1 |
| 形态对齐叶33 FROZEN 审 | **PASS** | 机制/符号/正交/宇宙/窗/forbid/状态机齐全；另钉 C3 PIN + mask-only + C11/C12 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗（C2）**：须钉本 FROZEN **`8be1099e`** + PIN **`bb418e6a`**；落 `research/leaf34_*` → Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本/禁签**。
2. **X2 独立签窗**：完整 overlay；vs 叶19/25/**27/30/31/32/33** Jaccard/ρ **重算**；解释叶25 尾窗 n_common=0；披露 ρ_max vs25；decay KEEP 硬验收；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)；禁复用叶25/27/30–33 `.ok`；禁 `--arch-ok-path` 自开；**KEEP 不解阻** X2 ACCEPT。
3. **PRIMARY 纪律**：判决=HI_LIQ mask-only；FULLA 仅研究披露；不得静默改 FULLA 作 PRIMARY；soft-penalty 启用须另窗+SW+style。
4. **C3 脚本落地纪律**：脚本须钉日表路径、`e_available_at≤t`、有效行合取、NP≤0 剔除、YTD-ish；不得静默改 period_basis / 升 BS WC。
5. **C10 仍另队**：`0087c928` / 叶28/29 不得借本 FROZEN/脚本窗夹带。
6. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；COUNT APPROX 不解阻；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C13 **均已入钉**；余项仅为流程下一跳（首要 **C2 正式脚本另窗**），故 **PASS_WITH_CONDITIONS**（非 FAIL）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算完整 α
- 不改 FROZEN / PIN / RECEIPT / WHO / COVER / COUNT；不落构建脚本；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不回撤叶32 HOLD；不改叶33 正式 `afbbe7e7`；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN 8be1099e + PIN bb418e6a（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf34_*（钉本 FROZEN + PIN bb418e6a；mask-only PRIMARY）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED 245df63f+c5ed13df+5774bb6e+二十票+81521fb5；禁复用叶25/27/30–33）
              → X2（完整 overlay；重叠重算含 19/25/27/30–33；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算**完整 α
- **未改** FROZEN / PIN / RECEIPT / WHO_PAYS / COVER / COUNT
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- **未落** `research/leaf34*`
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（含 PIN `bb418e6a` / RECEIPT `438ee33d` / 上游审 `9d8a2f9e`）；C1–C13 对照齐；PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY；C3 PIT/NP/period_basis 与 PIN 一致；失效/正交（含 vs 19/25/27/30–33）/C11 overlay≠主叶/C12 APPROX≠ACCEPT/decay KEEP 三闸+KEEP 不解阻/forbid 含 `81521fb5`/rss/PIT 硬钉入文。开放余项见 §3（首要 **请主令 AI 落正式脚本**）。**本回合不签、不挂、不代跑**。

live=false.
