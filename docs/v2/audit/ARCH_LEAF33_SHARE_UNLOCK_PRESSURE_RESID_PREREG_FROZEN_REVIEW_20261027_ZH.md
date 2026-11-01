# Arch 审阅：叶33 限售解禁压力残差慢 α PREREG_FROZEN（只审 FROZEN；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T06:01:00-04:00`（America/New_York；墙钟 `2026-10-27 06:01 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 FROZEN/WHO/COVER/PIN/脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（另队）；叶28/29 **另队不夹带**；**≠X2 ACCEPT**；live=false；**不推 Leo** |
| 触发 | 主 05:58 ET 令 Arch 只审 FROZEN（对照 who_pays 审 C1–C10；TEAM_STATE 顶条 + 主令） |

## 0. 一句话

FROZEN **`8ed43721`** / 回执 **`8f43e2f8`** / PIN **`4e17ccfc`** / 上游 who_pays 审 **`55531e12`** / WHO_PAYS **`1032477d`** / COVER **`61d9f656`** 本机 sha256 **MATCH**；相对 DRAFT **已升格 FROZEN**；mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1`；C3 选径 **(a)+加价**（`unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`；表内 `float_ratio` PRIMARY 禁用）；α=`−rank(pressure_resid)` 符号冻结；H/H_back/W/rebal=20/5/20/20；X2 窗 2024-06-03→2026-10-09；C1–C10 契约入钉；HI_LIQ PRIMARY + FULLA 研究双钉；SW+style 残差；Jaccard≥0.7 硬拒；decay KEEP 三闸+KEEP 不解阻；forbid `5774bb6e`+二十票；rss=1500+peak_proof；`0087c928`/叶28/29 另队；`research/leaf33*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ok_requested=false / EXECUTED=false。开放余项：正式构建脚本另窗。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| PREREG_FROZEN | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_20261027_ZH.md` | `8ed43721` | `8ed437210214015bfd6b3ee17104b4bae3c38baf62583f2e529433f550983189` | **MATCH** |
| AI FROZEN 回执 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_PREREG_FROZEN_RECEIPT_20261027_ZH.md` | `8f43e2f8` | `8f43e2f8f1f62ad9dddfb9a9be71c32c574b9c3037c61a256e971ef2385085ff` | **MATCH** |
| PIN 决议 | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_FLOAT_RATIO_PIN_20261027_ZH.md` | `4e17ccfc` | `4e17ccfc16cb3c2ed388941514dc65e0dbfce1242bb15b3923cc2f89da6cfb75` | **MATCH**（选径 a；FROZEN 升级 (a)+加价） |
| Arch who_pays 审 | `docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md` | `55531e12` | `55531e129e89077e9390a45c2f1310d5e2a80421ff6d16927b46bbaf1a7ee3c5` | **MATCH** |
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `1032477d` | `1032477d54c9c2c4b0bc4398066d76d852369d9187f3ff3e7c7610953c086075` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` | `61d9f656` | `61d9f656b8dcfa686f512f92637c884ab3029dfd523956bda4d2bfbbf70c5f70` | **MATCH** |
| 叶32 FROZEN 审（形态） | `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md` | （形态对照） | `7c0d864f7d544e8bd16817c74fa4dd7e35c9609c5066eedc4ee15f71765b5d84` | **只读** |
| 构建脚本 `research/leaf33*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶33 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET*` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`） | 0 | 0 | **MATCH** |
| share_float_pit schema | `data/v2/share_float/share_float_pit.parquet` | 列含 `float_share`/`float_ratio`/`available_at`/`float_date` | 6,449,659 行；列齐 | **MATCH**（只读；未实算 α） |

对照形态：叶32 PREREG_FROZEN 审 `docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_PREREG_FROZEN_REVIEW_20261027_ZH.md`；本叶结构对齐（机制/符号/残差/正交/宇宙/窗/decay/forbid/状态机；另多 C3 PIN 量纲钉）。

## 2. C1–C10 对照表（相对 who_pays 审 `55531e12`）

| # | who_pays 条件 | FROZEN 落点 | 结果 |
|---|---|---|---|
| **C1** | 须另窗冻结预注册（相对 DRAFT） | 状态 **FROZEN**；冻结时点 05:56 ET；明示「冻结前**未**读任何本叶收益选 W/方向/符号」；相对 who_pays/COVER DRAFT **升格**；α/H/H_back/W/再平衡/失效写死 | **PASS** |
| **C2** | 正式构建脚本尚未写；本冻结≠脚本 | 文首 + §13：本冻结 ≠ 构建脚本；`research/leaf33*` **ABSENT**（本拍禁落）；脚本另窗 | **PASS_WITH_CONDITIONS**（余项：另窗落脚本） |
| **C3** | PIN_GAP=`float_ratio`：选 (a) 并核量纲同口径（改公式或加价勿静默）或 (b)；禁静默混用 | §1.1：由 PIN `4e17ccfc` 选径 (a) **升级 (a)+加价**：`unlock_mv=Σ float_share×close_T−1`；`unlock_raw=unlock_mv/float_mktcap_T−1`（元/元 无量纲）；表内 `float_ratio` **PRIMARY 禁用**；**不是**改用 (b)；close/市值缺失→无效不填 0 | **PASS** |
| **C4** | Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；X2 前完整 α 重算重叠；另须披露 vs margin_delta/hk_hold/moneyflow | §4：vs 叶19/25/27/30/31/32 Jaccard≥0.7 **硬拒**；ρ>0.5 **强度过滤**；vs 历史 margin_delta/hk_hold/moneyflow 须披露且 Jaccard≥0.7 硬拒；「正式重叠须用完整 α 重算」 | **PASS** |
| **C5** | 残差清单写死；缺列→PIN_GAP | §3：SW L1 demean → log 流通市值 → mom20/vol20/`logADV20`（或钉死 capacity_adv，**二者择一并钉**）；缺列→PIN_GAP；禁两融/Amihud/on_minus_id/CRR/hk_hold/float_ratio 主输入 | **PASS** |
| **C6** | HI_LIQ PRIMARY + FULLA 研究双钉；禁静默改 FULLA 作 PRIMARY | §5：HI_LIQ_V1.1 **PRIMARY 判决**（掩码路径写死，median≥300）；FULLA_V1 **研究对照**（median≥800）；明示「PRIMARY 不得静默改 FULLA」 | **PASS** |
| **C7** | decay KEEP 三闸：latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300；近端窗写死；KEEP 不解阻 | §7：近端=评估日起最近 **252** 交易日（gate v1.1；≥126 日出 α）；`latest_resid_alpha>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` 合取才 KEEP；失败最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 `45dd87dc`） | **PASS** |
| **C8** | 禁 RESTORED `5774bb6e`+二十票 | §10：forbid∋`5774bb6e`+二十票（含 `02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` 等合取串）；禁复用叶25/27/30/31/32 `.ok`；禁 `--arch-ok-path` 自开 | **PASS** |
| **C9** | rss=1500 + peak_proof；禁抬 | §6：rss **1500** MB 禁抬；peak_proof **REQUIRED**；未来执行窗硬 ABORT | **PASS** |
| **C10** | `0087c928` 另队；叶28/29 不夹带；本拍不审 | §11：叶30 KEEP 修复 **`0087c928` 另队不并入**；叶28/29 仍 FROZEN 不夹带；本拍未打开/未审 | **PASS（未审声明）** |

### 附加硬钉（任务清单）

| 项 | 结果 | 证据 |
|---|---|---|
| 机制链 unlock→pressure_raw→pressure_resid→α=`−rank`；与 who_pays 一致 | **PASS** | §1/§2；RECEIPT 机制钉；(a)+加价公式 |
| 符号 α=`−rank(pressure_resid)` 冻结；禁事后翻 | **PASS** | §1/§2/§15 |
| H/H_back/W/再平衡=20/5/20/20；最少有效日≥15 | **PASS** | §1.2/§6/§15 |
| PIT=`available_at≤t`；禁未来公告偷看 | **PASS** | §1.2/§8 |
| 避 25/27/30/31/32 同构；≠hk_hold/northbound/moneyflow | **PASS** | §0 失效 + §1 边界 + §4/§9/§14 |
| 失效条件齐 | **PASS** | §0：未残差解禁规模排序；vs 叶32/31/27/30/25 近等权；hk_hold/northbound/moneyflow；卖方/金股/TP/LLM；事后翻；未做 SW+style；偷看 available_at>t；PRIMARY 静默混用 float_ratio；FULLA 静默改 PRIMARY |
| 禁卖方/金股/LLM/GP/高杠杆 | **PASS** | §0 失效 + §14 禁项 |
| 成本 **30bp**；日度 base-α **非 Top-N** | **PASS** | §4/§6 |
| PIT/GAP | **PASS** | §8：缺列/缺窗→PIN_GAP；勿静默编造 |
| 备选/敏感性未混 PRIMARY | **PASS** | §5/§9 分家表；PRIMARY=HI_LIQ |
| ok_requested=false / EXECUTED=false / 无脚本未实跑 | **PASS** | 文钉 + 盘证 §1 |
| 形态对齐叶32 FROZEN 审 | **PASS** | 机制/符号/正交/宇宙/窗/forbid/状态机齐全；另钉 C3 量纲 |

## 3. CONDITIONS（余项；非缺硬钉 FAIL）

1. **正式构建脚本另窗**：须钉本 FROZEN **`8ed43721`** + PIN **`4e17ccfc`**（(a)+加价）；落 `research/leaf33_*` → Arch **只审脚本** → 再谈独立 `.ok`。**本拍禁落脚本/禁签**。
2. **X2 独立签窗**：完整 α；vs 叶19/25/27/30/31/32 Jaccard/ρ **重算**；**另须披露 vs margin_delta/hk_hold/moneyflow**；decay KEEP 硬验收；禁 RESTORED `5774bb6e`+二十票；禁复用叶25/27/30/31/32 `.ok`；禁 `--arch-ok-path` 自开；**KEEP 不解阻** X2 ACCEPT。
3. **PRIMARY 纪律**：判决=HI_LIQ；FULLA 仅研究披露；不得静默改 FULLA 作 PRIMARY；不得静默混用表内 `float_ratio`。
4. **C3 脚本落地纪律**：脚本须钉 close 价列（不复权收盘价元 **或** 标准 adj close；二者择一不得事后换）；回执披露列名；`float_share`=股、`float_mktcap`=元、close=元/股 → unlock_raw 无量纲。
5. **C10 仍另队**：`0087c928` / 叶28/29 不得借本 FROZEN/脚本窗夹带。
6. **本冻结 ≠ X2 ACCEPT**；≠Book-Smoke；live=false；不报 Leo。

缺 C 硬钉才 FAIL——本票 C1–C10 **均已入钉**；余项仅为流程下一跳（首要 **C2 正式脚本另窗**），故 **PASS_WITH_CONDITIONS**（非 FAIL）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活；不实算 α
- 不改 FROZEN / WHO / COVER / PIN；不落构建脚本；不把本审当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不推 Leo；live=false

## 5. 硬钉下一跳

```
PREREG_FROZEN 8ed43721（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 落正式脚本 research/leaf33_*（钉本 FROZEN + PIN 4e17ccfc (a)+加价）
      → Arch 审脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED 5774bb6e+二十票；禁复用叶25/27/30/31/32；forbid 合取）
              → X2（完整 α；重叠重算含 vs margin_delta/hk_hold/moneyflow；decay KEEP 硬验收；KEEP 不解阻 ACCEPT）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算** α
- **未改** FROZEN / WHO_PAYS / COVER / PIN
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- **未落** `research/leaf33*`
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — PREREG_FROZEN 契约可收；钉 MATCH（含回执 `8f43e2f8` / PIN `4e17ccfc`）；C1–C10 对照齐；符号/失效/双轨/正交（含 vs 叶25/27/30/31/32 + margin_delta/hk_hold/moneyflow）/C3 (a)+加价量纲/decay KEEP 三闸+KEEP 不解阻/forbid `5774bb6e`+二十票/rss/PIT 硬钉入文。开放余项见 §3（首要 **请主令 AI 落正式脚本**）。**本回合不签、不挂、不代跑**。

live=false.
