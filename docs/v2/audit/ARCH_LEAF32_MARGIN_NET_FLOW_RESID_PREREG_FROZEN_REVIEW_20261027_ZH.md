# Arch 审阅：叶32 净融资流入强度残差慢 α PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T03:55:19-04:00`（America/New_York；墙钟 `2026-10-27 03:55 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 03:52 ET 令 Arch 只审 FROZEN（对照 who_pays 审 C1–C9；TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN **`6b8de5e9`** / 回执 **`7623ce8c`** / 上游 who_pays 审 **`84df02b5`** / WHO_PAYS **`fad5911e`** / COVER **`ebda2603`** 本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**；mechanism=`g1g5_ashare_margin_net_flow_resid_v1`；W/再平衡=20/20；α=`−rank(flow_resid)` 符号冻结；X2 窗 2024-06-03→2026-10-09；C1–C9 契约入钉；HI_LIQ PRIMARY + FULLA 研究双钉；正交含 vs margin_delta；禁卖方/金股；Jaccard≥0.7 硬拒；forbid 六票；rss=1500+peak_proof；`research/leaf32*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false。开放余项：正式构建脚本另窗。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_20261027_ZH.md` | `6b8de5e9` | `6b8de5e9d4a4cc6caecbe344bfc4b6ce4da0f9e983f87c7c7b73759e0f893f42` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `7623ce8c` | `7623ce8c351ce7c1927b17dd095953f8c968753fbfe5f9d5eb29042bf814bb37` | **MATCH** |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `84df02b5` | `84df02b5ddfd10314bf8bc95acdf931d12ba9e53e43dd318e61fdc85b7b6fb01` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `fad5911e` | `fad5911eec855a3b77d77971f8d44241798bfa4355adebd3f14aa67910fc6c44` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF32_MARGIN_NET_FLOW_RESID_COVER_DRAFT_20261027_ZH.md` | `ebda2603` | `ebda2603283198382c7225924f4105d9ec9891acad3ba83a022a2172a1dac9fc` | **MATCH** |
| 叶31 FROZEN 审（形态） | `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_REVIEW_20261027_ZH.md` | （形态对照） | `7a6a1e1adb6bfb71cd128fe08e71c16c763c59187dd4e1d4bb40abc6c2adc639` | **只读** |
| 构建脚本 `research/leaf32*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶32 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF32*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET*` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |

对照形态：叶31 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF31_AMIHUD_IMPACT_SLOW_PREREG_FROZEN_REVIEW_20261027_ZH.md`；本叶结构对齐（机制/符号/残差/正交/宇宙/窗/decay/forbid/状态机）。

## 2. C1–C9 对照表（相对 who_pays 审 `84df02b5`）

| # | who_pays 条件 | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C1** | 须另窗冻结预注册（相对 DRAFT） | 状态 **FROZEN**；冻结时点 03:50 ET；明示「冻结前**未**读任何本叶收益选 W/方向/符号」；相对 who_pays/COVER DRAFT **升格** | **PASS** |
| **C2** | 正式构建脚本尚未写；本冻结≠脚本 | 文首 + §13：本冻结 ≠ 构建脚本；`research/leaf32*` **ABSENT**（本拍禁落）；脚本另窗 | **PASS_WITH_CONDITIONS**（余项：另窗落脚本） |
| **C3** | Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；X2 前完整 α 重算重叠；**另须披露 vs margin_delta** | §4：vs 叶19/25/27/30/31 Jaccard≥0.7 **硬拒**；ρ>0.5 **强度过滤**；vs 历史 `margin_delta`（Δrzye）须披露且 Jaccard≥0.7 硬拒；「正式重叠须用完整 α 重算」 | **PASS** |
| **C4** | 残差清单写死；缺列→PIN_GAP | §3：SW L1 demean → log 流通市值 → mom20/vol20/`logADV20`（或钉死 capacity_adv，**二者择一并钉**）；缺列→PIN_GAP；禁 Amihud/on_minus_id/CRR/hk_hold 主输入 | **PASS** |
| **C5** | HI_LIQ PRIMARY + FULLA 研究双钉；禁静默改 FULLA 作 PRIMARY | §5：HI_LIQ_V1.1 **PRIMARY 判决**（掩码路径写死，median≥300）；FULLA_V1 **研究对照**（median≥800）；明示「PRIMARY 不得静默改 FULLA」 | **PASS** |
| **C6** | decay KEEP 三闸：latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端窗写死 | §7：近端=评估日起最近 **252** 交易日（gate v1.1；≥126 日出 α）；`latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` 合取才 KEEP；失败最多 WATCH/HOLD | **PASS** |
| **C7** | 禁 RESTORED 六票 | §10：forbid∋`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30/31 `.ok`；禁 `--arch-ok-path` 自开 | **PASS** |
| **C8** | rss=1500 + peak_proof；禁抬 | §6：rss **1500** MB 禁抬；peak_proof **REQUIRED**；未来执行窗硬 ABORT | **PASS** |
| **C9** | `0087c928` 另队；本拍不审 | §11：叶30 KEEP 修复 **`0087c928` 另队不并入**；本拍未打开/未审 | **PASS（未审声明）** |

### 附加硬钉（任务清单）

| 项 | 结果 | 证据 |
|---|---|---|
| 机制链 net_rz→flow_raw→flow_resid→α=`−rank`；与 who_pays 一致 | **PASS** | §1/§2；RECEIPT 机制钉 |
| 符号 α=`−rank` 冻结；禁事后翻 | **PASS** | §1/§2/§15 |
| 不读 hk_hold；不复刻 margin_delta/Amihud/on−id/CRR | **PASS** | §0 失效 + §1 边界 + §4/§9/§14 |
| 失效条件齐 | **PASS** | §0：未残差融资排序；vs margin_delta 近等权；hk_hold/northbound；Amihud/on_minus_id/CRR/应计主输入；卖方/金股/TP/LLM；事后翻；未做 SW+style；FULLA 静默改 PRIMARY |
| 禁卖方/金股/LLM/GP/高杠杆 | **PASS** | §0 失效 + §14 禁项 |
| 成本 **30bp**；日度 base-α **非 Top-N** | **PASS** | §4/§6 |
| PIT/GAP | **PASS** | §8：缺列/缺窗→PIN_GAP；勿静默编造 |
| 备选/敏感性未混 PRIMARY | **PASS** | §5/§9 分家表；PRIMARY=HI_LIQ |
| ok_requested=false / EXECUTED=false / 无脚本未实跑 | **PASS** | 文钉 + 盘证 §1 |
| 形态对齐叶31 FROZEN 审 | **PASS** | 机制/符号/正交/宇宙/窗/forbid/状态机齐全 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗**：须钉本 FROZEN **`6b8de5e9`**；落 `research/leaf32_*` → Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本/禁签**。
2. **X2 独立签窗**：完整 α；vs 叶19/25/27/30/31 Jaccard/ρ **重算**；**另须披露 vs margin_delta**；decay KEEP 硬验收；禁 RESTORED `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；禁复用叶25/27/30/31 `.ok`；禁 `--arch-ok-path` 自开。
3. **PRIMARY 纪律**：判决=HI_LIQ；FULLA 仅研究披露；不得静默改 FULLA 作 PRIMARY。
4. **C9 仍另队**：`0087c928` 不得借本 FROZEN/脚本窗夹带。
5. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C9 **均已入钉**；余项仅为流程下一跳，故 **PASS_WITH_CONDITIONS**（非 FAIL）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活
- 不改 FROZEN / 不落构建脚本；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN 6b8de5e9（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf32_*（钉本 FROZEN）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED；禁复用叶25/27/30/31；forbid 六票）
              → X2（完整 α；重叠重算含 vs margin_delta；decay KEEP 硬验收）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count
- **未改** FROZEN / WHO_PAYS / COVER
- **未审**叶30 衰减修复 `0087c928`（另队）
- **未落** `research/leaf32*`
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（含回执 `7623ce8c`）；C1–C9 对照齐；符号/失效/双轨/正交（含 vs margin_delta）/decay KEEP 三闸/forbid 六票/rss/PIT 硬钉入文。开放余项见 §3（首要 **请主令 AI 落正式脚本**）。**本回合不签、不挂、不代跑**。

live=false.
