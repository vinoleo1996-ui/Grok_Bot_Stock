# Arch 审阅：叶37 IMAX/隔夜彩票剔除 overlay PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T17:06:00-04:00`（America/New_York；墙钟 `2026-10-27 17:06 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/PIN/RECEIPT/WHO/COVER/COUNT/脚本；**不触** A18；叶36 inquiry HOLD CLOSED（`feaa5dbb`/`575e8276`）不回撤；叶35/34/33/`afbbe7e7`/32/`45dd87dc` HOLD 不回撤；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 17:02 ET 令 Arch 只审本 FROZEN（对照 who_pays 审 C1–C13；TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN **`c5927f1b`** / PIN(C3=B) **`e01be34c`** / RECEIPT **`3992f0fa`** / 上游 who_pays 审 **`4a074f0a`** / WHO **`0ed8e9d8`** / COVER **`847245f8`** / COUNT **`154bc157`** / SCRIPT **`c10b735f`** / JSON **`2217f580`** / dig **`74234fca`** 本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**（非仍标 DRAFT）；mechanism=`g1g5_ashare_imax_lottery_exclusion_overlay_v1`；**PRIMARY=mask-only** top_q=**0.20**（高 IMAX=剔除）；soft-penalty **明示非 PRIMARY**；**C3=B** `IMAX_proxy`=raw `r_id` 20d top-5（≥15）为交付定义；`full_residual_e_id=false`；**持续 APPROX**；**禁**静默升全 e_id；**C11** overlay≠叶24 完整 −IMAX 主叶；C1–C13 契约入钉；HI_LIQ PRIMARY；Jaccard≥0.7 硬拒（vs 18/18v/27）；ρ>0.5 强度过滤披露（ρ18≈0.505 / ρ27≈0.665）；vs 24/34/35/36 完整重叠须 X2 前重算；forbid 含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；rss=1500+peak_proof；decay KEEP 三闸 + KEEP 不解阻；C12 APPROX≠ACCEPT；`research/leaf36*|leaf37*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false。开放余项：正式构建脚本另窗（C2）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `c5927f1b` | `c5927f1b07a67c4e839c3084202e84f10529a379779a3dfc10ae751487676213` | **MATCH** |
| PIN（C3=B） | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_IMAX_PROXY_PIN_20261027_ZH.md` | `e01be34c` | `e01be34cfedeedffe750e753ace1977071d0b073238ac294fe78d75284ea0c2a` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `3992f0fa` | `3992f0faf0cb075b0e641f2da5dbeda3adb67ef101cf7f79f384560d774ecbe2` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `4a074f0a` | `4a074f0a983a54f30607f01ac8b93f1c2cc4f1ea716bac438c67d8f3e8c79859` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `0ed8e9d8` | `0ed8e9d81edd2a751b4cf7c8b0e4116ba300c418b12d88476220a336238616cf` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `847245f8` | `847245f8ef5786e95e68b6b73e713a12a3bc573fcd49b40ba757ee33013e01b6` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `154bc157` | `154bc157d6b054ddd039e1c9bd800abf388b0406e85ed279dfd67bd3c4258023` | **MATCH** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `c10b735f` | `c10b735f20e00e74dfc1e16519947903cf0199b8ed1b5925e55f26262b9251ad` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` | `2217f580` | `2217f5801b558fd8227da4390f7f77c84f9bd9242863e26610dabe6e5562291d` | **MATCH** |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_1625ET.md` | `74234fca` | `74234fca3fef423d394b87b1dedce51c2de6bca3ea72c1be40d3ef4521f413a9` | **MATCH** |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | 前8 MATCH | **MATCH UNCHANGED** |
| 叶35 正式脚本（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | 前8 MATCH | **MATCH 未碰** |
| 叶32 HOLD（只读） | `…ALPHA_LEAF32…GATE_REVIEW…` | `45dd87dc` | 文钉齐 | **不回撤** |
| 构建脚本 `research/leaf36*|leaf37*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶37 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |

对照形态：叶35 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md`（sha8 `5a082d18`）；叶34 FROZEN 审 `027efa26`。

## 2. C1–C13 对照表（相对 who_pays 审 `4a074f0a` §3）

| # | who_pays 条件 | FROZEN / PIN 落点 | 结果 |
|---|---|---|---|
| **C1** | 须另窗冻结预注册（相对 DRAFT） | 状态 **FROZEN**；冻结时点 17:00 ET；明示「冻结前**未**读任何本叶收益选 q/方向」；相对 who_pays/COVER/COUNT DRAFT **升格**；mask-only / q / 再平衡 / 失效 / 交付写死 | **PASS** |
| **C2** | 正式构建脚本尚未写；本冻结≠脚本；计数非正式构建 | 文首 + §14：本冻结 ≠ 构建脚本；`research/leaf36*|leaf37*` **ABSENT**（本拍禁落）；计数脚本 audit **`c10b735f`**（非正式 α）；脚本另窗 | **PASS_WITH_CONDITIONS**（余项：另窗落正式脚本） |
| **C3** | IMAX APPROX 二选一；(B)=proxy 冻结+持续 APPROX | §1.1 + PIN **`e01be34c`**：`IMAX_proxy`=raw `r_id` 20d top-5（≥15）=**交付定义**；`full_residual_e_id=false`；持续 APPROX；升级须另窗重跑计数+修订 PIN/FROZEN；**禁**静默把 proxy 当全 e_id | **PASS**（与 PIN / 主裁 C3=B 一致） |
| **C4** | soft-penalty / mask-only 明示 | §1.2/§3：**明示 mask-only PRIMARY**；连续 soft-penalty **非 PRIMARY**；启用须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP | **PASS** |
| **C5** | top_q=0.20 符号冻结 | §1.2/§2：q=**0.20**；「高 IMAX=剔除」；禁读收益改阈值/翻方向；再平衡=20 | **PASS** |
| **C6** | HI_LIQ 主判决 | §5：HI_LIQ_V1.1 **PRIMARY**（median≥300；剔除≥30）；明示「PRIMARY 不得静默改 FULLA」 | **PASS** |
| **C7** | X2 前完整重叠；ρ 强度过滤披露 | §4：vs 18/18v/27 Jaccard≥0.7 **硬拒**；ρ>0.5 **强度过滤**；vs 24/34/35/36 **披露**；ρ18≈0.505 / ρ27≈0.665 持续披露；COUNT 轻量不能替正式重叠 | **PASS** |
| **C8** | 禁 RESTORED / 禁复用旧窗 | §10：forbid∋`eb70eef4+00eec671+10927bd9+25ae4572`+旧票全集；禁复用叶18/24/27/30–36 `.ok`；禁 `--arch-ok-path` 自开 | **PASS** |
| **C9** | rss=1500 + peak_proof | §6：rss **1500** MB 禁抬；peak_proof **REQUIRED**；未来执行窗硬 ABORT | **PASS** |
| **C10** | 叶36 inquiry HOLD CLOSED | §11：禁复开 inquiry；禁放宽覆盖阈；WHO `feaa5dbb` / JSON `575e8276` 不回撤；叶28/29/`0087c928` 另队不夹带 | **PASS（未审声明）** |
| **C11** | overlay ≠ 叶24 −IMAX 主叶 | §1.2/§9：交付=形态 A **mask-only overlay 叠主干**；禁完整 `g1g5_ashare_imax_intraday_v1` 排序/多层残差主 α；禁叶18/27/24 α 当主输入 | **PASS** |
| **C12** | APPROX ≠ X2 ACCEPT | §0/§6/§12/§13：COUNT gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke | **PASS** |
| **C13** | decay KEEP | §7：近端=**252**d（≥126 日出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32/34/35/36 教训） | **PASS** |

### 附加硬钉（任务清单 / 主点名）

| 项 | 结果 | 证据 |
|---|---|---|
| 真正 FROZEN（非仍标 DRAFT） | **PASS** | 文首状态 **FROZEN**；冻结时点 17:00 ET；§16 状态钉 |
| PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY | **PASS** | §1.2/§3/§16；RECEIPT 机制钉 |
| **C3=B** proxy 冻结+APPROX；禁静默升 e_id | **PASS** | PIN §1.1–1.3 + FROZEN §1.1；`full_residual_e_id=false` |
| **C4** mask-only PRIMARY | **PASS** | §1.2/§3/§12 C4；RECEIPT |
| **C5** q=0.20 | **PASS** | §1.2/§2/§16 |
| **C11** overlay≠叶24 完整 −IMAX 主叶 | **PASS** | §1.2/§9/§12 C11；RECEIPT 明示 |
| **C7·C12·C13** 入钉 | **PASS** | §4/§12/§7；ρ 强度过滤披露；APPROX≠ACCEPT；KEEP 不解阻 |
| 机制与 who_pays/COVER 无静默改号 | **PASS** | mechanism 同 tag；`IMAX_proxy`；q=0.20；再平衡 20 |
| ≠重开叶24 / 叶18/27 波动主轴 / 叶36 inquiry | **PASS** | §0 失效 + §9 分家 + C10/C11 |
| 失效条件 / Jaccard 硬拒 / 禁卖方 | **PASS** | §0 失效；§4 Jaccard；§15 禁卖方/金股/LLM/GP/高杠杆 |
| 脚本仍 ABSENT（预期） | **PASS** | 盘证 §1；CONDITIONS 保留 C2 |
| 未申请 .ok / 未挂 QUIET | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 叶33 `afbbe7e7` UNCHANGED / 叶35 `434ff42c` / 叶32 HOLD / 叶36 HOLD CLOSED 不回撤 | **PASS** | 只读对照 §1 |
| 形态对齐叶35/34 FROZEN 审 | **PASS** | 机制/符号/正交/宇宙/窗/forbid/状态机齐全；另钉 C3=B PIN + mask-only + C11/C12 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗（C2）**：须钉本 FROZEN **`c5927f1b`** + PIN **`e01be34c`**；落 `research/leaf37_*` → Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本/禁签**。
2. **X2 独立签窗**：完整 overlay；vs 叶18/18v/27（硬拒）及 **24/34/35/36**（披露）Jaccard/ρ **重算**；披露 ρ 强度过滤纪律；decay KEEP 硬验收；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；禁复用叶18/24/27/30–36 `.ok`；禁 `--arch-ok-path` 自开；**KEEP 不解阻** X2 ACCEPT。
3. **PRIMARY 纪律**：判决=HI_LIQ mask-only；不得静默改 FULLA 作 PRIMARY；soft-penalty 启用须另窗+SW+style。
4. **C3=B 脚本落地纪律**：脚本须钉 `IMAX_proxy`=raw `r_id` 20d top-5（≥15）、`full_residual_e_id=false`、持续 APPROX 披露；**不得**静默改用全 e_id；升级须另窗修订 PIN/FROZEN + 重跑计数闸。
5. **C11 脚本落地纪律**：交付须为 mask-only overlay 叠主干；禁输出叶24 完整 −IMAX 主 α；禁叶18/27/24 α 主输入。
6. **C10 仍另队**：叶36 inquiry HOLD CLOSED 不复开/不放宽；`0087c928` / 叶28/29 不得借本 FROZEN/脚本窗夹带；备选 B 勿开。
7. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；COUNT APPROX 不解阻；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C13 **均已入钉**；余项仅为流程下一跳（首要 **C2 正式脚本另窗**），故 **PASS_WITH_CONDITIONS**（非 FAIL）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算完整 α
- 不改 FROZEN / PIN / RECEIPT / WHO / COVER / COUNT / 计数脚本；不落构建脚本；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不复开叶36；不夹带叶28/29；不回撤叶32/34/35/36 HOLD；不改叶33 正式 `afbbe7e7` / 叶35 `434ff42c`；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN c5927f1b + PIN e01be34c（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf37_*（钉本 FROZEN + PIN e01be34c；mask-only PRIMARY；C3=B IMAX_proxy；C11≠叶24）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED eb70eef4+00eec671+10927bd9+25ae4572+旧票；禁复用叶18/24/27/30–36）
              → X2（完整 overlay；重叠重算含 18/18v/27/24/34–36；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

**本拍不签**。**推荐主裁：令 AI 落地脚本**（C1–C13 入钉完整；开放项属 C2 脚本窗而非硬缺陷）。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算**完整 α
- **未改** FROZEN / PIN / RECEIPT / WHO_PAYS / COVER / COUNT / 计数脚本
- **未复开**叶36 inquiry；**未夹带**叶28/29；**未开**备选 B
- **未落** `research/leaf37*`
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶35 **`434ff42c` 未碰**；叶32 HOLD **`45dd87dc`** / 叶36 HOLD CLOSED（`feaa5dbb`/`575e8276`）只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false；SIGNED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（含 PIN `e01be34c` / RECEIPT `3992f0fa` / 上游审 `4a074f0a` / 五钉 / dig）；C1–C13 对照齐；PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY；**C3=B** IMAX_proxy 交付硬钉（`full_residual_e_id=false`；持续 APPROX；禁静默升 e_id）；**C4=mask-only PRIMARY**；**C5** q=0.20；**C11** overlay≠叶24 完整 −IMAX 主叶；失效/正交（含 vs 18/18v/27/24/34–36）/C12 APPROX≠ACCEPT/decay KEEP 三闸+KEEP 不解阻/forbid 含 `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`/rss/PIT 硬钉入文。开放余项见 §3（首要 **请主令 AI 落正式脚本**）。**本回合不签、不挂、不代跑、未写 leaf37 脚本**。

live=false.
