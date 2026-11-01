# Arch 审阅：叶33 限售解禁压力残差慢 α who_pays + COVER（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T05:49:00-04:00`（America/New_York；墙钟 `2026-10-27 05:49 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本；**不触** A18；叶30 衰减修复 **`0087c928` 未审**（主明令本拍不审/另队）；叶28/29 **另队不夹带**；叶30/31/32 HOLD **不回撤**（叶32 HOLD **`45dd87dc`**）；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 05:47 ET 排号 **意向叶33** → 令 Arch 只审 who_pays+COVER（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO_PAYS **`1032477d`** / COVER **`61d9f656`** 本机 sha256 **MATCH**；mechanism=`g1g5_ashare_share_unlock_pressure_resid_v1` 可检验（解禁 PIT → unlock_raw=`sum(float_share)/float_mktcap_T-1` → pressure_raw=mean_W → SW+style 残差 → α=−rank(pressure_resid)；H/H_back/W/再平衡 DRAFT=20/5/20/20；符号冻结纪律；失效条件齐，含 vs margin_net_flow / Amihud / on_minus_id / CRR / 应计 / hk_hold）；与叶19/25/27/30/31/32 正交意向写清（零会计/零两融/零 Amihud 主轴；Jaccard≥0.7 硬拒 / ρ_excess>0.5 强度过滤）；**PIN_GAP=`float_ratio` 单位未核死**已披露且主路径钉 `sum(float_share)/float_mktcap_T-1`（**勿静默混用**）；HI_LIQ 主 / FULLA 研究双轨；禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 80/20；rss=1500；禁 RESTORED `5774bb6e`+二十票（含 `02426b73`）；DRAFT **NOT FROZEN** / EXECUTED=false / ok_requested=false；`research/leaf33*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；share_float schema 只读核 MATCH（含 `available_at`；行数 6,449,659）。开放项见 §3（须另窗冻结预注册；`float_ratio`/量纲核死等）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_DRAFT_20261027_ZH.md` | `1032477d` | `1032477d54c9c2c4b0bc4398066d76d852369d9187f3ff3e7c7610953c086075` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_COVER_DRAFT_20261027_ZH.md` | `61d9f656` | `61d9f656b8dcfa686f512f92637c884ab3029dfd523956bda4d2bfbbf70c5f70` | **MATCH** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH**（本拍只读对照；不回撤） |
| 构建脚本 `research/leaf33*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶33 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF33*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok` | 0 | 0 | **MATCH** |
| share_float_pit schema | `data/v2/share_float/share_float_pit.parquet` | 行含 `available_at`/`float_share`/`float_ratio` | 6,449,659 行；`available_at`=timestamp[us, tz=Asia/Shanghai]；列齐 | **MATCH**（只读；未实算 α） |
| float_mktcap | `data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet` | 存在 | 11,711,361 行含 `float_mktcap` | **MATCH** |
| HI_LIQ mask | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | 存在 | 11,748,583 行 | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF32_MARGIN_NET_FLOW_RESID_WHO_PAYS_REVIEW_20261027_ZH.md`（叶32 当时亦是 **DRAFT** → CONDITIONS 含「须另窗冻结预注册」）。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：解禁 PIT→unlock_raw→pressure_raw→SW+style 残差→α=−rank；H/H_back/W/再平衡 DRAFT=20/5/20/20；符号冻结纪律；失效条件清晰（含 vs 叶32 两融 / 叶31 Amihud / 叶27 on_minus_id / 叶30 CRR / 叶25 应计） | **PASS** | WHO_PAYS §0/§2/§3/§9：公式、合成、禁事后翻/冻结前未读收益选号、失效条件齐；COVER 公式钉同构 |
| 2 | 与叶19/25/27/30/31/32 正交；Jaccard≥0.7 硬拒；ρ_excess>0.5 强度过滤；明确 ≠northbound/hk_hold/moneyflow/margin/Amihud 换皮；≠叶32 两融净流入复刻 | **PASS** | WHO_PAYS §1/§3.5–§3.6/§8；COVER 对照钉；避应计·CRR / overnight−idio / Amihud / MARGIN_NET_FLOW / hk_hold |
| 3 | **PIN_GAP=`float_ratio` 单位未核死** → 主路径钉 `sum(float_share)/float_mktcap_T-1`；**勿静默混用** | **PASS_WITH_CONDITIONS** | WHO_PAYS §2/§4/§13 + COVER PIN_GAP 钉主路径；禁静默混用写清；冻结前须核死量纲或弃用 ratio → **C3/C4** |
| 4 | HI_LIQ 主 / FULLA 研究双轨；PRIMARY 判决=HI_LIQ | **PASS_WITH_CONDITIONS** | WHO_PAYS §5：PRIMARY=HI_LIQ；FULLA 研究对照；预注册须同时冻结两池规格 → C6 |
| 5 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 80/20 | **PASS** | WHO_PAYS 文首禁项 + §11；COVER 禁止清单 |
| 6 | rss=1500 禁抬意向 | **PASS** | WHO_PAYS §5/§9；COVER rss 意向 |
| 7 | DRAFT NOT FROZEN / EXECUTED=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 8 | decay KEEP 意向（latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300）合理写入 CONDITIONS；KEEP 不解阻 X2 ACCEPT（叶32 教训） | **PASS_WITH_CONDITIONS** | WHO_PAYS §7（合取三闸 + 组合闸意图如实勿宣称过闸）；预注册须写死近端窗/口径 → C7 |
| 9 | 数据 PIT / GAP；日度 base-α 非 Top-N；30bp；X2 窗 2024-06-03→2026-10-09；本拍禁实算 α | **PASS** | WHO_PAYS §4/§5；本机只读核 share_float 6,449,659 行、列含 `float_share/float_ratio/available_at`；float 11,711,361 行含 `float_mktcap`；HI_LIQ mask 存在；GAP 勿静默编造；**未**实算 α |
| 10 | 备选质量切片未混 PRIMARY；叶28/29 不夹带 | **PASS** | WHO_PAYS §1/§12：异常换手 / AlphaLens 仅备案不升；叶28/29 另队 FROZEN |
| 11 | 叶30 衰减修复 `0087c928` **本拍不审**；叶30/31/32 HOLD 不回撤 | **PASS（未审声明）** | 主令本拍不审；本回执**未打开/未审** `0087c928`；另队；HOLD 只读对照（叶32=`45dd87dc`） |
| 12 | forbid `5774bb6e`+二十票写入 CONDITIONS | **PASS** | WHO_PAYS/COVER §11 钉二十票齐 + `5774bb6e`（含 `02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`）→ C8 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31/32 who_pays 审深度）。PASS ≠ 可签 `.ok`。请主令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2。
2. **C2 正式构建脚本尚未写**：`research/leaf33*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。
3. **C3 PIN_GAP=`float_ratio` 单位核死或弃用**：冻结时二选一写死——(a) 继续主路径 `sum(float_share)/float_mktcap_T-1` 并核死 `float_share` 与 `float_mktcap` **量纲同口径**（股数 vs 市值；若不同量须改公式或加价，**勿静默**）；或 (b) 核死后改用表内 `float_ratio`（单位=流通比且口径一致）。**禁静默混用**两条路径。
4. **C4 X2 前重算重叠**：须用完整 α 重算 vs 叶19/25/27/30/31/32 的 Jaccard/ρ；**另须披露 vs 历史 margin_delta / hk_hold / moneyflow**；DRAFT 硬拒意向不能替正式重叠证明。
5. **C5 残差清单写死**：冻结时钉 SW L1 + log 流通市值 + style（mom20/vol20/logADV20 或等价）；缺列 → PIN_GAP，勿静默跳过；后加项须补丁；H/H_back/W/最少有效日写死。
6. **C6 FULLA 双钉规格**：预注册须同时冻结 HI_LIQ（PRIMARY 判决）与 FULLA（研究对照）规格；PRIMARY 不得静默改 FULLA。
7. **C7 decay KEEP 冻结口径**：预注册写死 `latest_resid_alpha>0` ∧ `非连降5季` ∧ `H2_net_cagr>510300` + 近端窗定义（与 `alpha_decay_gate` H2 对齐）；失败 → 最多 WATCH/HOLD，不派烟、≠X2 ACCEPT；**KEEP 不解阻** X2 ACCEPT（叶32 HOLD `45dd87dc` 教训）。组合闸路径仅意图，冻结后另验。
8. **C8 禁 RESTORED / 禁复用旧窗**：forbid∋`5774bb6e`+二十票（`02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`）；禁复用叶25/27/30/31/32 `.ok`；禁 `--arch-ok-path` 自开。
9. **C9 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。
10. **C10 叶30 修复 / 叶28/29 另队**：`0087c928` 本拍未审；叶28/29 仍 FROZEN 不夹带；不得借本审窗口夹带签跑。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算 α
- 不改 WHO_PAYS / COVER DRAFT；不把 DRAFT 当 FROZEN
- 不触 A18；不解阻 X2；不当 X2 ACCEPT；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不回撤叶30/31/32 HOLD（叶32=`45dd87dc`）；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays DRAFT 1032477d + COVER 61d9f656（本审 PASS_WITH_CONDITIONS）
  → 请主令 AI 出 FROZEN 预注册（钉 float_ratio PIN_GAP 选径 + 量纲）
      → Arch 审 FROZEN / 正式脚本（另窗）
          → 独立新窗 .ok（禁 RESTORED 5774bb6e+二十票；禁复用叶25/27/30/31/32）
              → X2（完整 α；重叠重算含 vs margin/Amihud/on_minus_id/CRR；decay KEEP 硬验收）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/count；**未实算** α
- **未改** DRAFT / COVER
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED=false

## 7. 结论

**PASS_WITH_CONDITIONS** — who_pays+COVER DRAFT 契约可收；钉 MATCH；机制/正交（含 ≠叶32 两融 / ≠Amihud / ≠应计·CRR）/双轨/禁项/rss/PIT/`float_ratio` PIN_GAP 主路径钉死/decay KEEP 意向齐。开放项见 §3（C1–C10），首要 **另窗冻结预注册（请主令 AI 出 FROZEN）** 与 **C3 PIN_GAP 量纲核死**。本回合不签、不挂、不代跑。

live=false.
