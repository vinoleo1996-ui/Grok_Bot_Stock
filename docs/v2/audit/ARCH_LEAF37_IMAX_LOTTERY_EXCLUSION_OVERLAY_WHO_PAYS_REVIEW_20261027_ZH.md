# Arch 审阅：叶37 IMAX/隔夜彩票剔除 overlay who_pays + COVER + COUNT（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T16:54:00-04:00`（America/New_York；墙钟 `2026-10-27 16:54 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本/COUNT/JSON；**不出 FROZEN**；不触 A18；叶36 inquiry HOLD CLOSED（`feaa5dbb`/`575e8276`）不回撤；叶35/34/33/`afbbe7e7`/32/`45dd87dc` HOLD 不回撤；禁 RESTORED `eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 16:49 ET 排号叶37 → 令 Arch 只审 WHO+COVER+COUNT（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO **`0ed8e9d8`** / COVER **`847245f8`** / COUNT **`154bc157`** / JSON **`2217f580`**（中间计数钉 `2986cee1`→终稿 **`2217f580`**）/ 计数脚本 **`c10b735f`** 本机 sha256 **MATCH**；PRIMARY=`g1g5_ashare_imax_lottery_exclusion_overlay_v1` 可检验（`IMAX_proxy`=raw `r_id` 20d top-5 → top_q=0.20 高尾 → 形态 **A** mask/soft-penalty **叠主干**；**非**叶24 完整 −IMAX 排序主 α；**非**叶18/27 波动主 α）；H/再平衡 DRAFT=20；符号「高 IMAX=剔除」冻结纪律；失效条件齐（退化为叶24 主叶 / vs 18·27 Jaccard≥0.7 / 精神叙事 / 事后改 q）；**明确 ≠** 重开叶24 −IMAX 主叶；ρ>0.5 强度过滤披露-only；COUNT 闸 **gate_pass=true（APPROX）**：computable_median=**2816.5**；excl_median=**564**；zero_frac=**0**；J18max≈**0.311** / J27max≈**0.443** / J24≈**0.223** ≪0.7；ρ18≈**0.505** / ρ27≈**0.665**（强度过滤已触）；peak≈**1030**≪1500；APPROX 披露诚实（**≠X2 ACCEPT**）；HI_LIQ 主；禁卖方/金股/survey/TP/LLM/GP/高杠杆/重开叶24/复开叶36；rss=1500；DRAFT **NOT FROZEN** / EXECUTED_full_alpha=false / ok_requested=false；`research/leaf36*|leaf37*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**。开放项见 §3（须另窗 FROZEN；IMAX APPROX 升级共签；overlay≠叶24）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `0ed8e9d8` | `0ed8e9d81edd2a751b4cf7c8b0e4116ba300c418b12d88476220a336238616cf` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `847245f8` | `847245f8ef5786e95e68b6b73e713a12a3bc573fcd49b40ba757ee33013e01b6` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `154bc157` | `154bc157d6b054ddd039e1c9bd800abf388b0406e85ed279dfd67bd3c4258023` | **MATCH** |
| COUNT SCRIPT | `docs/v2/audit/AI_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_COUNT_GATE_SCRIPT_20261027.py` | `c10b735f` | `c10b735f20e00e74dfc1e16519947903cf0199b8ed1b5925e55f26262b9251ad` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf37_imax_lottery_exclusion_count_20261027.json` | `2217f580` | `2217f5801b558fd8227da4390f7f77c84f9bd9242863e26610dabe6e5562291d` | **MATCH**（取代中间钉 `2986cee1`） |
| dig（上下文） | `output/d1/DIG_FACTOR_20261027_1625ET.md` | `74234fca` | `74234fca…`（前8 MATCH） | **MATCH** |
| 叶36 HOLD CLOSED | WHO / JSON | `feaa5dbb` / `575e8276` | 前8 MATCH | **MATCH 不回撤** |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | 前8 MATCH | **MATCH UNCHANGED** |
| 叶35 正式脚本（只读） | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` | `434ff42c` | 前8 MATCH | **MATCH 未碰**（禁 RESTORED `25ae4572`） |
| 叶32 HOLD（只读） | `…ALPHA_LEAF32…GATE_REVIEW…` | `45dd87dc` | 文钉齐 | **不回撤** |
| 构建脚本 `research/leaf36*|leaf37*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶37 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |

对照模板：`docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_REVIEW_20261027_ZH.md`（sha8 `ee7ec307`）；叶34 who_pays 审 `9d8a2f9e`。

### 1.1 COUNT 闸数字再核（JSON ↔ COUNT ↔ who_pays）

| 指标 | JSON | COUNT / WHO | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| APPROX | approx[] 非空；`full_residual_e_id=false` | APPROX 醒目（IMAX_proxy） | **MATCH**（诚实） |
| computable_median | 2816.5 | 2816.5 | **MATCH**（≥300） |
| excl_median | 564.0 | 564.0 | **MATCH**（≥30） |
| zero_frac_masked | 0.0 | 0.0 | **MATCH**（≤0.05） |
| J18_max / J18v_max | 0.3107 | ≈0.311 / 0.3107 | **MATCH**（≪0.7） |
| J27_max | 0.4430 | ≈0.443 / 0.4430 | **MATCH**（≪0.7） |
| J24_max（披露） | 0.2229 | ≈0.223 / 0.2229 | **MATCH**（disclose-only） |
| ρ18_mean / ρ27_mean | 0.5051 / 0.6653 | ≈0.505 / ≈0.665 | **MATCH**（强度过滤已触；披露-only） |
| hard_reject_jaccard | false | False | **MATCH** |
| peak_rss_mb | 1030.15 | 1030.1 | **MATCH**（≪1500） |
| EXECUTED_full_alpha / ok_requested / live | false / false / false | false | **MATCH** |

附注：叶18 vs 叶18v 样本日 α MAE=0（corr≈1）—重叠读数重合，硬拒仍按 ≥0.7；本拍未算 vs 叶34/35/36 剔除集（→ C7）。叶24 重叠中等偏低属预期（proxy≠全 e_id）；反同构靠形态 A。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：`IMAX_proxy`→top_q=0.20 高尾→形态 A mask/soft-penalty 叠主干（非完整 −IMAX 主 α）；H/再平衡/符号纪律；失效条件齐 | **PASS** | WHO §0/§2/§9；COVER 公式钉；禁事后翻/冻结前未读收益选 q |
| 2 | **明确 ≠** 重开叶24 −IMAX 完整排序主叶；vs 叶18/18v/27 Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；披露 vs 叶24 | **PASS_WITH_CONDITIONS** | WHO §1/§8 差表；COUNT 轻量验 18/18v/27/24；完整重叠 → **C7/C11** |
| 3 | COUNT 闸：median/excl/zero_frac/J*/ρ；APPROX 披露诚实；**勿把计数当 X2 ACCEPT** | **PASS_WITH_CONDITIONS** | §1.1 MATCH；COUNT APPROX 醒目；文钉 ≠X2 → **C12** |
| 4 | APPROX `IMAX_proxy`=raw r_id 20d top-5（非全 e_id / 非叶24 full residual）可进 FROZEN？ | **PASS_WITH_CONDITIONS** | JSON `imax_spec.approx=true`；WHO §2/§4；须冻结前共签升级或钉 proxy 为意向 → **C3** |
| 5 | C4/mask-only / top_q=0.20 意图与 WHO/COVER 一致 | **PASS_WITH_CONDITIONS** | WHO §2 形态 A + q=0.20；COVER 同步；soft-penalty 残差后钉 → **C4/C5** |
| 6 | overlay ≠ 叶24 主叶边界钉死 | **PASS_WITH_CONDITIONS** | WHO §1/§8/§11；COVER 禁止清单；FROZEN 须硬钉 → **C11** |
| 7 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆/重开叶24/复开叶36；rss=1500 | **PASS** | WHO 文首+§11；COVER 禁止清单；rss 意向；本拍未触卖方/教科书/GP |
| 8 | DRAFT NOT FROZEN / EXECUTED_full_alpha=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 9 | forbid `eb70eef4+00eec671+10927bd9+25ae4572`+旧票 | **PASS** | WHO/COVER §11 钉齐 → **C8** |
| 10 | 叶36 inquiry HOLD CLOSED 不回撤；禁放宽覆盖阈；叶35/34/33/32 HOLD 不回撤 | **PASS** | 主令；盘证 `feaa5dbb`/`575e8276`；`afbbe7e7`/`434ff42c`/`45dd87dc` 只读 |
| 11 | decay KEEP 意向合理；KEEP 不解阻 X2 ACCEPT | **PASS_WITH_CONDITIONS** | WHO §7；预注册写死近端窗 → **C13** |
| 12 | 备选 B 未混 PRIMARY | **PASS** | WHO §12；COVER：B 不升 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31–36 who_pays）。PASS ≠ 可签 `.ok`。请主择令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2；或 HOLD。
2. **C2 正式构建脚本尚未写**：`research/leaf36*|leaf37*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。计数脚本已落 audit（`c10b735f`）；正式构建勿把计数脚本当 α 构建。
3. **C3 IMAX APPROX → 冻结前共签**：`IMAX_proxy`=raw `r_id` 20d top-5（`full_residual_e_id=false`）。FROZEN 须二选一写死：**(A)** 升级为叶24 全路径 `e_id`（SW L1 + logmv_{t−1}）并重跑计数闸；或 **(B)** 明示冻结 proxy 为交付定义并持续 APPROX 披露。**勿静默把 proxy 当全残差 IMAX**。
4. **C4 soft-penalty / mask-only**：若冻结选连续 soft-penalty，须钉 SW L1 + log 流通市值 + style；缺列 → PIN_GAP。纯 mask 主路径可后钉残差，但须在 FROZEN 明示「mask-only」。
5. **C5 top_q=0.20 冻结纪律**：`q=0.20` 与「高 IMAX=剔除」符号冻结写死；**禁**读收益改阈值/翻方向；再平衡=20 写死。
6. **C6 HI_LIQ 主判决**：PRIMARY 宇宙=HI_LIQ；不得静默改 FULLA 当主。
7. **C7 X2 前完整重叠重算**：须用完整 overlay 重算 vs 叶18/18v/27（硬拒）及叶24/34/35/36（披露）；DRAFT 轻量计数 **不能**替正式重叠证明；ρ 强度过滤（ρ18≈0.505 / ρ27≈0.665）须进 FROZEN 披露，**不解阻也不单独废叶**。
8. **C8 禁 RESTORED / 禁复用旧窗**：forbid∋`eb70eef4+00eec671+10927bd9+25ae4572+178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`；禁复用叶18/24/27/30–36 `.ok`；禁 `--arch-ok-path` 自开。
9. **C9 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。本拍计数 peak≈1030 仅参考。
10. **C10 叶36 inquiry HOLD CLOSED**：禁复开 inquiry 主轴；禁放宽其覆盖阈；本票不得借窗口夹带改叶36。
11. **C11 overlay ≠ 叶24 −IMAX 主叶硬钉**：FROZEN/脚本须钉交付=**形态 A mask/soft-penalty overlay 叠主干**；**禁**输出完整 `g1g5_ashare_imax_intraday_v1` 多层残差/排序主 α；禁把叶18/27/24 α 当主输入。
12. **C12 APPROX 计数 ≠ X2 ACCEPT**：gate_pass（APPROX）仅放行继续 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面。
13. **C13 decay KEEP 冻结口径**：预注册写死 `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` + 近端窗；失败 → 最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32/34/35/36 HOLD 教训）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算完整 α / 不开全窗 X2
- 不改 WHO / COVER / COUNT / SCRIPT / JSON DRAFT；不把 DRAFT 当 FROZEN；不把 COUNT 当 X2 ACCEPT；不出 FROZEN
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不回撤叶36/35/34/33/32 HOLD；不改叶33 `afbbe7e7` / 叶35 `434ff42c`；不碰 RESTORED `25ae4572`；不推 Leo；live=false
- EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 5. 硬钉下一跳

```
who_pays DRAFT 0ed8e9d8 + COVER 847245f8 + COUNT 154bc157 / JSON 2217f580（←2986cee1）/ 脚本 c10b735f
  （本审 PASS_WITH_CONDITIONS；gate_pass=true APPROX）
  → 请主择令 AI 出 FROZEN 预注册（钉 IMAX APPROX 升级或 proxy 冻结 / top_q / 形态A overlay≠叶24）或 HOLD
      → Arch 审 FROZEN / 正式脚本（另窗；research/leaf37* 现 ABSENT）
          → 独立新窗 .ok（禁 RESTORED eb70eef4+00eec671+10927bd9+25ae4572+旧票）
              → X2（完整重叠重算含 18/18v/27/24/34–36；rss+peak_proof；decay KEEP）
```

**本拍不签**。**推荐主裁：出 FROZEN**（闸已过、APPROX/同构边界已诚实披露，开放项属冻结文案而非硬缺陷）。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/完整 α / 计数脚本；**未改** DRAFT/COUNT/JSON/SCRIPT；**未出** FROZEN
- 叶36 HOLD CLOSED（`feaa5dbb`/`575e8276`）/ 叶35 `434ff42c` / 叶33 `afbbe7e7` / 叶32 `45dd87dc` 只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED_full_alpha=false；EXECUTED_PROBE=false；SIGNED=false；QUIET=false

## 7. 结论

**PASS_WITH_CONDITIONS** — WHO+COVER+COUNT DRAFT 契约可收；五钉 MATCH（JSON 终稿 `2217f580` 取代 `2986cee1`）；机制/正交（≠叶24 完整 −IMAX 主叶；形态 A overlay）/COUNT 闸（APPROX 诚实；median=2816.5；excl=564；J18/J27≪0.7；ρ 强度过滤披露；peak≈1030）/禁项/rss/forbid 齐。开放项见 §3（C1–C13），首要 **另窗冻结预注册（请主择令 AI 出 FROZEN）** 与 **C3 IMAX APPROX 共签 + C11 overlay≠叶24**。本回合不签、不挂、不代跑、不出 FROZEN。

live=false.
