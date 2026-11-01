# Arch 审阅：叶35 ETF 被动压力 overlay who_pays + COVER + COUNT（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T12:54:00-04:00`（America/New_York；墙钟 `2026-10-27 12:54 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本/COUNT/JSON；**不出 FROZEN**；不触 A18；叶34 HOLD CLOSED（`178e90e9`/`3fce510e`/`a37257b9`）不回撤；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；`0087c928`/叶28/29 **另队不夹带**；禁 RESTORED `178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+二十票；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 12:51 ET 排号叶35 → 令 Arch 只审 WHO+COVER+COUNT（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO **`05942769`** / COVER **`f41d7db8`** / COUNT **`cbca88e7`** / JSON **`a17b75fb`** / 计数脚本 **`4e964d40`** 本机 sha256 **MATCH**；PRIMARY=`g1g5_ashare_etf_passive_flow_pressure_overlay_v1` 可检验（`pressure=Σ w×flow_est` → top_q=0.20 `|pressure|` → 交付形态 **A** soft-penalty/exclusion-tilt **叠主干**；**非**叶26 完整多层残差 α 主叶；**非**交易 ETF）；H/再平衡 DRAFT=慢 20；符号「高 `|pressure|`=剔除/惩罚」冻结纪律；失效条件齐，含 vs moneyflow Jaccard≥0.7 硬拒 / 退化为叶26 同构废叶；**明确 ≠** 重开叶26 / 叶8a / moneyflow 主轴；ρ>0.5 强度过滤；另须披露 vs 25/27/30–34；COUNT 闸 **gate_pass=true（APPROX）**：masked_median=**1552.5**；zero_frac=**0**；J20_max vs moneyflow=**0.25**≪0.7；ρ_mean≈**−0.080**；peak≈**566**MB；叶26 残差 α / 叶8a **GAP 未伪造**；叶26-like raw 诊断同幅披露诚实（不作硬拒）；权重 asof **APPROX**（无 `available_at`）须冻结前升级；APPROX 披露诚实（**≠X2 ACCEPT**）；HI_LIQ 主 / FULLA 研究双轨意向；禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 主轴；rss=1500；DRAFT **NOT FROZEN** / EXECUTED_full_alpha=false / ok_requested=false；`research/leaf35*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**。开放项见 §3（须另窗 FROZEN；权重 PIT；overlay≠叶26；完整重叠）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `05942769` | `0594276917a88969456ed3b7103d7f51ca26d4b2923125295507f1a8f2802997` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `f41d7db8` | `f41d7db8f0632a8433972def18bd92b6f76f625fdabd9603b5fe18be74ca92a1` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `cbca88e7` | `cbca88e797c4c423e082d8db189ef1e0265747e90990817bbfd823f09798b431` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` | `a17b75fb` | `a17b75fbb383620ed7e39470056f83031708a7f8b9ae9d4013583a4718aa28e6` | **MATCH** |
| 计数脚本（/tmp） | `/tmp/quantlab_leaf35_etf_passive_flow_pressure_count_gate.py` | `4e964d40` | `4e964d4024115b3a73f97d7789dac22e328e6eed519ca4935fcd2dcf5ba82538` | **MATCH PRESENT**（/tmp 易失；本拍在场） |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7…`（前8 MATCH） | **MATCH UNCHANGED** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc…`（前8 MATCH） | **MATCH**（不回撤） |
| 叶34 HOLD CLOSED 钉 | `.ok`/`lift`/回执 | `178e90e9`/`3fce510e`/`a37257b9` | WHO/COVER/JSON 文钉齐 | **MATCH 不回撤** |
| 构建脚本 `research/leaf35*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶35 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md`（sha8 曾为 `9d8a2f9e`）。

### 1.1 COUNT 闸数字再核（JSON ↔ COUNT ↔ who_pays）

| 指标 | JSON | COUNT / WHO | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| APPROX | approx[] 非空 | APPROX 醒目 | **MATCH**（诚实） |
| masked_median | 1552.5 | 1552.5 | **MATCH**（≥300） |
| zero_frac_masked | 0.0 | 0.0 | **MATCH**（≤0.05） |
| J20_max vs moneyflow | 0.25 | 0.25 / 0.25 | **MATCH**（≪0.7；硬拒未触） |
| ρ_mean vs moneyflow | −0.0795 | ≈−0.080 / ≈−0.08 | **MATCH**（未触 ρ_mean>0.5） |
| 叶26 残差 α | status=GAP | GAP 未伪造 | **MATCH** |
| 叶8a | status=GAP | GAP 未伪造 | **MATCH** |
| peak_rss_mb | 566.23 | 566.2 | **MATCH**（<1500） |
| EXECUTED_full_alpha / ok_requested | false / false | false | **MATCH** |

附注：叶26-like raw 诊断 J20_max=1.0 / ρ 可塌缩（by construction 同幅；全日赎回时 `−|p|` vs `+p` 排名塌缩）—COUNT **不作硬拒**、反同构靠交付形态 A；剔除集 vs leaf26-like top20 long Jaccard≈0.00–0.07 已披露。本拍未算 vs 25/27/30–34（→ C7）。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：`pressure=Σ w×flow_est` → top_q=0.20 `|pressure|` → 形态 A soft-penalty/exclusion-tilt 叠主干（非完整多空 α）；H/再平衡/符号纪律；失效条件齐 | **PASS** | WHO §0/§2/§9；COVER 公式钉同构；禁事后翻/冻结前未读收益选 q |
| 2 | **明确 ≠** 重开叶26 完整残差 α / 叶8a 交易 ETF / moneyflow 主轴；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；另 vs 25/27/30–34 | **PASS_WITH_CONDITIONS** | WHO §1/§2 差表 + §8；COUNT 轻量只验 moneyflow + leaf26-like 诊断；完整重叠 → **C7/C11** |
| 3 | COUNT 闸：masked_median≥300；zero_frac；J20；ρ；APPROX 披露诚实；**勿把计数当 X2 ACCEPT** | **PASS_WITH_CONDITIONS** | §1.1 MATCH；COUNT APPROX/GAP 醒目；文钉 ≠X2 → **C12** |
| 4 | 叶26 残差α / 叶8a **GAP 未伪造**（不得假 Jaccard） | **PASS** | JSON `overlap_vs_leaf26_residual_alpha.status=GAP`；`overlap_vs_leaf8a.status=GAP`；COUNT 醒目；WHO §4 |
| 5 | 反叶26 同构论证是否站得住（形态 A overlay vs 完整残差 α） | **PASS_WITH_CONDITIONS** | 交付差表硬写；raw 同幅 by construction 已披露不作硬拒；冻结须钉 overlay≠主叶 → **C11**；权重 PIT → **C3** |
| 6 | 权重 asof APPROX 是否须冻结前升级 | **PASS_WITH_CONDITIONS** | index_weight 无 `available_at`；月末向后 asof；WHO §2/§4/§6.5；COUNT APPROX → **C3 必做** |
| 7 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow 主轴；rss=1500 | **PASS** | WHO 文首+§11；COVER 禁止清单；rss 意向；本拍未触卖方/教科书/GP |
| 8 | DRAFT NOT FROZEN / EXECUTED_full_alpha=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 9 | forbid `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5`+二十票 | **PASS** | WHO/COVER §11 钉齐 → **C8** |
| 10 | `0087c928`/叶28/29 **本拍不审不夹带**；叶33/`afbbe7e7` UNCHANGED；叶32/34 HOLD 不回撤 | **PASS（未审声明）** | 主令；本回执未打开/未审 `0087c928`；HOLD/正式只读对照 |
| 11 | decay KEEP 意向合理；KEEP 不解阻 X2 ACCEPT（叶32/34 教训） | **PASS_WITH_CONDITIONS** | WHO §7；预注册写死近端窗 → **C13** |
| 12 | 备选问询函未混 PRIMARY | **PASS** | WHO §12；COVER：备选不升 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31–34 who_pays）。PASS ≠ 可签 `.ok`。请主择令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2；或 HOLD。
2. **C2 正式构建脚本尚未写**：`research/leaf35*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。/tmp 计数脚本易失，冻结前须迁入仓内或重钉 sha。
3. **C3 权重 asof APPROX → 冻结前升级**：`index_weight_csi300_500_1000` **无 `available_at`**；本拍月末 `trade_date` 向后 asof。FROZEN 须共签方案 A（次月首日 09:00 SH）或等价 PIT 规则；**勿静默沿用 APPROX 当 PIT 完备**。份额表 `available_at≤t` 纪律同步写死。
4. **C4 soft-penalty 残差纪律**：若冻结选连续 soft-penalty（非纯 mask），须钉 SW L1 + log 流通市值 + style（mom20/vol20/logADV20）；缺列 → PIN_GAP。纯 mask 主路径可后钉残差，但须在 FROZEN 明示「mask-only」。
5. **C5 top_q=0.20 冻结纪律**：`q=0.20` 与「高 `|pressure|`=剔除/惩罚」符号冻结写死；**禁**读收益改阈值/翻方向；宽基三件套映射冻结；行业 ETF 禁主轴。
6. **C6 FULLA 双钉规格**：预注册须同时冻结 HI_LIQ（PRIMARY）与 FULLA（研究对照）；PRIMARY 不得静默改 FULLA。
7. **C7 X2 前完整重叠重算**：须用完整 overlay/α 重算 vs moneyflow_resid / **叶26 残差 α（若落盘）** / 叶8a（若有）**及** 25/27/30–34 的 Jaccard/ρ；DRAFT 轻量计数 **不能**替正式重叠证明；叶26-like raw 诊断 J=1.0 **不得**误当硬拒或误当正交已证。
8. **C8 禁 RESTORED / 禁复用旧窗**：forbid∋`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`；禁复用叶25/27/30–34 `.ok`；禁 `--arch-ok-path` 自开。
9. **C9 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。本拍计数 peak≈566 仅参考。
10. **C10 `0087c928`/叶28/29 另队**：本拍未审；不得借本审窗口夹带签跑。
11. **C11 overlay ≠ 叶26 完整残差 α 硬钉**：FROZEN/脚本须钉交付=**形态 A mask/soft-penalty overlay 叠主干**；**禁**输出完整 `g1g5_ashare_broad_etf_flow_stock_v1` 多层残差 α 当本叶主 α；禁把叶26 α / 行业 ETF 持仓 / 个股 moneyflow 当主输入；raw 同幅须持续披露。
12. **C12 APPROX 计数 ≠ X2 ACCEPT**：gate_pass（APPROX）仅放行继续 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面。
13. **C13 decay KEEP 冻结口径**：预注册写死 `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` + 近端窗；失败 → 最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 HOLD `45dd87dc` / 叶34 HOLD CLOSED `178e90e9` 教训）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算完整 α / 不开全窗 X2
- 不改 WHO / COVER / COUNT / JSON DRAFT；不把 DRAFT 当 FROZEN；不把 COUNT 当 X2 ACCEPT；不出 FROZEN
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不回撤叶32/33/34 HOLD；不改叶33 正式 `afbbe7e7`；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays DRAFT 05942769 + COVER f41d7db8 + COUNT cbca88e7 / JSON a17b75fb / 脚本 4e964d40
  （本审 PASS_WITH_CONDITIONS；gate_pass=true APPROX）
  → 请主择令 AI 出 FROZEN 预注册（钉权重 PIT/top_q/形态A overlay≠叶26）或 HOLD
      → Arch 审 FROZEN / 正式脚本（另窗；research/leaf35* 现 ABSENT）
          → 独立新窗 .ok（禁 RESTORED 178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票）
              → X2（完整重叠重算含 moneyflow/叶26残差/8a/25/27/30–34；rss+peak_proof；decay KEEP）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/完整 α；**未改** DRAFT/COUNT/JSON；**未出** FROZEN
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** / 叶34 HOLD CLOSED（`178e90e9`/`3fce510e`/`a37257b9`）只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED_full_alpha=false

## 7. 结论

**PASS_WITH_CONDITIONS** — WHO+COVER+COUNT DRAFT 契约可收；五钉 MATCH；机制/正交（≠叶26 完整残差 α；形态 A overlay）/COUNT 闸（APPROX 诚实；median=1552.5；J20=0.25≪0.7；ρ≈−0.08；叶26/8a GAP 未伪造）/双轨/禁项/rss/forbid 齐。开放项见 §3（C1–C13），首要 **另窗冻结预注册（请主择令 AI 出 FROZEN 或 HOLD）** 与 **C3 权重 asof APPROX 升级 + C11 overlay≠叶26**。本回合不签、不挂、不代跑、不出 FROZEN。

live=false.
