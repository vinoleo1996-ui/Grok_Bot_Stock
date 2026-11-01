# Arch 审阅：叶35 ETF 被动压力 overlay PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T13:10:00-04:00`（America/New_York；墙钟 `2026-10-27 13:10 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/PIN/RECEIPT/WHO/COVER/COUNT/迁仓脚本；**不触** A18；叶34 HOLD CLOSED（`178e90e9`/`3fce510e`/`a37257b9`）不回撤；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；`0087c928`/叶28/29 **另队不夹带**；禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 13:06 ET 令 Arch 只审本 FROZEN（对照 who_pays 审 C1–C13；TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN **`be9fc459`** / PIN(C3) **`dd17044a`** / RECEIPT **`132ba6f1`** / 迁仓脚本 **`4e964d40`** / 上游 who_pays 审 **`ee7ec307`** / WHO **`05942769`** / COVER **`f41d7db8`** / COUNT **`cbca88e7`** / JSON **`a17b75fb`** 本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**（非仍标 DRAFT）；mechanism=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`；**PRIMARY=mask-only** top_q=**0.20**（高 `|pressure|`=剔除）；soft-penalty **明示非 PRIMARY**；**C3** PIN 方案 A=月末权重点→**次月首个交易日 09:00 Asia/Shanghai** = `weight_available_at` ∧ 份额 `available_at≤t`；**禁**静默月末向后 asof；**C11** overlay≠叶26 完整残差 α 硬钉；C1–C13 契约入钉；HI_LIQ PRIMARY + FULLA 研究双钉；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；vs moneyflow/叶26残差(若有)/8a(若有)/25/27/30–34 完整重叠须 X2 前重算；forbid 含 `178e90e9`+`c1b71e64`+`81521fb5`；rss=1500+peak_proof；decay KEEP 三闸 + KEEP 不解阻；C12 APPROX≠ACCEPT；`research/leaf35*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false。开放余项：正式构建脚本另窗（C2）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_20261027_ZH.md` | `be9fc459` | `be9fc4593249928460ec5a118a0bd79e033fd446ec921a64f6d47bdd09b01ed6` | **MATCH** |
| PIN（C3） | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WEIGHT_PIT_PIN_20261027_ZH.md` | `dd17044a` | `dd17044ab6f2890283f226112609eebfdb5dddcc10df8fda8e8565de8ac77a36` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `132ba6f1` | `132ba6f1f78be22bd3e22c6214eaf5c2f3c0f92ebb6501161f0ec7ed674c676a` | **MATCH** |
| 计数脚本迁仓 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `4e964d40` | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` | **MATCH**（≡`/tmp/…count_gate.py` 字节相同） |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md` | `ee7ec307` | `ee7ec307e22bb5e6b98b6521d76e5f62a04311ffc9917efafde24524861a6f93` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `05942769` | `0594276917a88969456ed3b7103d7f51ca26d4b2923125295507f1a8f2802997` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `f41d7db8` | `f41d7db8f0632a8433972def18bd92b6f76f625fdabd9603b5fe18be74ca92a1` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `cbca88e7` | `cbca88e797c4c423e082d8db189ef1e0265747e90990817bbfd823f09798b431` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` | `a17b75fb` | `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6` | **MATCH** |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH**（不回撤） |
| 构建脚本 `research/leaf35*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶35 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |

对照形态：叶34 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_PREREG_FROZEN_REVIEW_20261027_ZH.md`（结构对齐；内容换叶35）。

## 2. C1–C13 对照表（相对 who_pays 审 `ee7ec307` §3）

| # | who_pays 条件 | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C1** | 须另窗冻结预注册（相对 DRAFT） | 状态 **FROZEN**；冻结时点 13:03 ET；明示「冻结前**未**读任何本叶收益选 λ/q/方向」；相对 who_pays/COVER/COUNT DRAFT **升格**；mask-only / q / 再平衡 / 失效 / 交付写死 | **PASS** |
| **C2** | 正式构建脚本尚未写；本冻结≠脚本；/tmp 计数迁仓 | 文首 + §14：本冻结 ≠ 构建脚本；`research/leaf35*` **ABSENT**（本拍禁落）；计数脚本已迁仓 **`4e964d40`** → `docs/v2/audit/…COUNT_GATE_SCRIPT_…py`（≡/tmp）；脚本另窗 | **PASS_WITH_CONDITIONS**（余项：另窗落正式脚本） |
| **C3** | 权重 asof APPROX→方案 A；份额 `available_at≤t`；禁静默月末向后 asof | §1.1 + PIN **`dd17044a`**：月末权重点→**次月首个交易日 09:00 Asia/Shanghai** = `weight_available_at`（交易日历，非纯日历日）；份额 `available_at≤t`；映射三件套；权重 percent_div100；**禁**静默 APPROX；asof 仅在合成 PIT 约束下 | **PASS**（与 PIN 一致） |
| **C4** | soft-penalty / mask-only 明示 | §1.2/§3：**明示 mask-only PRIMARY**；连续 soft-penalty **非 PRIMARY**；启用须 SW L1 + log 流通市值 + mom20/vol20/logADV20；缺列→PIN_GAP | **PASS** |
| **C5** | top_q=0.20 符号冻结 | §1.2/§2：q=**0.20**；「高 `|pressure|`=剔除」；禁读收益改阈值/翻方向；行业 ETF 禁主轴 | **PASS** |
| **C6** | FULLA 双钉 | §5：HI_LIQ_V1.1 **PRIMARY**（median≥300）+ FULLA_V1 **研究**（median≥800）；明示「PRIMARY 不得静默改 FULLA」 | **PASS** |
| **C7** | X2 前完整重叠 | §4：vs moneyflow / 叶26残差(若有) / 8a(若有) / **25/27/30–34** Jaccard≥0.7 **硬拒**；ρ>0.5 **强度过滤**；leaf26-like J=1.0 不得当硬拒或正交已证；COUNT 轻量不能替正式重叠 | **PASS** |
| **C8** | 禁 RESTORED / 禁复用旧窗 | §10：forbid∋`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e`+二十票+**`81521fb5`**；禁复用叶25/27/30–34 `.ok`；禁 `--arch-ok-path` 自开 | **PASS** |
| **C9** | rss=1500 + peak_proof | §6：rss **1500** MB 禁抬；peak_proof **REQUIRED**；未来执行窗硬 ABORT | **PASS** |
| **C10** | `0087c928`/叶28/29 另队 | §11：叶30 KEEP 修复 **`0087c928` 另队不并入**；叶28/29 仍 FROZEN 不夹带；本拍未打开/未审 | **PASS（未审声明）** |
| **C11** | overlay ≠ 叶26 完整残差 α | §1.2/§9：交付=形态 A **mask-only overlay 叠主干**；禁输出叶26 `g1g5_ashare_broad_etf_flow_stock_v1` 完整多层残差 α 当本叶主 α；禁 moneyflow / 行业 ETF 持仓主输入；raw 同幅持续披露 | **PASS** |
| **C12** | APPROX ≠ X2 ACCEPT | §0/§6/§12/§13：COUNT gate_pass（APPROX）仅放行 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke | **PASS** |
| **C13** | decay KEEP | §7：近端=**252**d（≥126 日出 α）；KEEP 三闸合取；失败→最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 HOLD `45dd87dc` / 叶34 `178e90e9`） | **PASS** |

### 附加硬钉（任务清单）

| 项 | 结果 | 证据 |
|---|---|---|
| 真正 FROZEN（非仍标 DRAFT） | **PASS** | 文首状态 **FROZEN**；冻结时点 13:03 ET；§16 状态钉 |
| PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY | **PASS** | §1.2/§3/§16；RECEIPT 机制钉 |
| **C3 方案 A** 次月首个交易日 09:00 SH；禁静默月末向后 asof | **PASS** | PIN §1.2 + FROZEN §1.1；交易日历非纯日历日 |
| **C11** overlay≠叶26 完整残差 α | **PASS** | §1.2/§9/§12 C11；RECEIPT 明示 |
| 机制与 who_pays/COVER 无静默改号 | **PASS** | mechanism 同 tag；公式 `pressure_raw=Σ w×flow_est_proxy`；q=0.20；再平衡 20 |
| ≠重开叶26 / 叶8a / moneyflow 主轴 | **PASS** | §0 失效 + §9 分家 + C11 |
| 失效条件 / Jaccard 硬拒 / 禁卖方 | **PASS** | §0 失效；§4 Jaccard；§15 禁卖方/金股/LLM/GP/高杠杆 |
| 迁仓脚本 ≡/tmp | **PASS** | `cmp` 字节相同；sha8 `4e964d40` |
| 脚本仍 ABSENT（预期） | **PASS** | 盘证 §1；CONDITIONS 保留 C2 |
| 未申请 .ok / 未挂 QUIET | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 叶33 `afbbe7e7` UNCHANGED / 叶32 HOLD / 叶34 HOLD CLOSED 不回撤 | **PASS** | 只读对照 §1 |
| 形态对齐叶34 FROZEN 审 | **PASS** | 机制/符号/正交/宇宙/窗/forbid/状态机齐全；另钉 C3 PIN + mask-only + C11/C12 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗（C2）**：须钉本 FROZEN **`be9fc459`** + PIN **`dd17044a`**；落 `research/leaf35_*` → Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本/禁签**。
2. **X2 独立签窗**：完整 overlay；vs moneyflow / 叶26残差(若有) / 8a(若有) / **25/27/30–34** Jaccard/ρ **重算**；披露 leaf26-like raw 同幅纪律；decay KEEP 硬验收；禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)；禁复用叶25/27/30–34 `.ok`；禁 `--arch-ok-path` 自开；**KEEP 不解阻** X2 ACCEPT。
3. **PRIMARY 纪律**：判决=HI_LIQ mask-only；FULLA 仅研究披露；不得静默改 FULLA 作 PRIMARY；soft-penalty 启用须另窗+SW+style。
4. **C3 脚本落地纪律**：脚本须钉方案 A（次月首个交易日 09:00 Asia/Shanghai）、份额 `available_at≤t`、映射三件套、percent_div100；**不得**静默沿用月末向后 asof 当 PIT 完备；COUNT APPROX ≠ 方案 A PIT。
5. **C11 脚本落地纪律**：交付须为 mask-only overlay 叠主干；禁输出叶26 完整残差 α；禁 moneyflow/行业 ETF 持仓主输入；raw 同幅持续披露。
6. **C10 仍另队**：`0087c928` / 叶28/29 不得借本 FROZEN/脚本窗夹带。
7. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；COUNT APPROX 不解阻；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C13 **均已入钉**；余项仅为流程下一跳（首要 **C2 正式脚本另窗**），故 **PASS_WITH_CONDITIONS**（非 FAIL）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算完整 α
- 不改 FROZEN / PIN / RECEIPT / WHO / COVER / COUNT / 迁仓脚本；不落构建脚本；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不回撤叶32/34 HOLD；不改叶33 正式 `afbbe7e7`；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN be9fc459 + PIN dd17044a（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf35_*（钉本 FROZEN + PIN dd17044a；mask-only PRIMARY；C3 方案 A；C11≠叶26）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED 178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+二十票+81521fb5；禁复用叶25/27/30–34）
              → X2（完整 overlay；重叠重算含 moneyflow/叶26残差/8a/25/27/30–34；rss+peak_proof；decay KEEP；KEEP 不解阻 ACCEPT）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算**完整 α
- **未改** FROZEN / PIN / RECEIPT / WHO_PAYS / COVER / COUNT / 迁仓脚本
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- **未落** `research/leaf35*`
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 叶34 HOLD CLOSED（`178e90e9`/`3fce510e`/`a37257b9`）只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（含 PIN `dd17044a` / RECEIPT `132ba6f1` / 迁仓脚本 `4e964d40` / 上游审 `ee7ec307`）；C1–C13 对照齐；PRIMARY=mask-only top_q=0.20；soft-penalty 非 PRIMARY；**C3** 方案 A 权重 PIT 硬钉（次月首个交易日 09:00 Asia/Shanghai；禁静默月末向后 asof）；**C4=mask-only PRIMARY**；**C11** overlay≠叶26 完整残差 α；失效/正交（含 vs moneyflow/叶26残差/8a/25/27/30–34）/C12 APPROX≠ACCEPT/decay KEEP 三闸+KEEP 不解阻/forbid 含 `178e90e9`+`81521fb5`/rss/PIT 硬钉入文。开放余项见 §3（首要 **请主令 AI 落正式脚本**）。**本回合不签、不挂、不代跑、未写 leaf35 脚本**。

live=false.
