# Arch 审阅：叶34 高应计剔除 overlay who_pays + COVER + COUNT（只审 DRAFT；不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器静态审） |
| 时刻 | `2026-10-27T09:52:00-04:00`（America/New_York；墙钟 `2026-10-27 09:52 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不代跑**；不改 DRAFT/脚本/COUNT/JSON；**不触** A18；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤；`0087c928`/叶28/29 **另队不夹带**；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票（及叶33 探针 `81521fb5`）；**≠X2 ACCEPT**；≠Book-Smoke；live=false；**不推 Leo** |
| 触发 | 主 09:46 ET 排号叶34 → 令 Arch 只审 WHO+COVER+COUNT（TEAM_STATE 顶条 + 主令） |

## 0. 一句话

WHO **`fa6aa2e3`** / COVER **`76b37ca3`** / COUNT **`806e1758`** / JSON **`9730d432`** 本机 sha256 **MATCH**；PRIMARY=`g1g5_ashare_high_accrual_exclusion_overlay_v1` 可检验（`accrual_cf=1−ocf_to_profit` → top_q=0.20 剔除 → 交付 **mask/soft-penalty overlay**，**非**完整多空 α；H/再平衡 DRAFT=慢 20；符号「高应计=剔除」冻结纪律；失效条件齐，含 vs 叶19/25/accrual_quality 主叶硬拒）；**明确 ≠** 重开叶19/25/accrual_quality；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；另须披露 vs 27/30/31/32/33；COUNT 闸 **gate_pass=true（APPROX）**：masked_median=**2431**；zero_frac=**0**；J20_max vs 19/25≈**0.053**≪0.7；ρ_mean≈**0.37**；peak≈**900**MB；APPROX 披露诚实（CF proxy 非 BS WC；**≠X2 ACCEPT**）；HI_LIQ 主 / FULLA 研究双轨意向；禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow；rss=1500；DRAFT **NOT FROZEN** / EXECUTED_full_alpha=false / ok_requested=false；`research/leaf34*` **ABSENT**；live `.ok`=0 / QUIET **ABSENT**；ocf 日表只读核 9,754,991 行列齐。开放项见 §3（须另窗 FROZEN；PIT/NP≤0/soft-penalty 残差/top_q 冻结/完整重叠）。**本拍不签**。

## 1. 钉表再核（本机 sha256）

| 件 | 路径 | 期望 sha8 | 实测全长 | 结果 |
|---|---|---|---|---|
| WHO_PAYS DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` | `fa6aa2e3` | `fa6aa2e3ffb084cc01f6a4d20575e528f1c095262c10a00e70dadb4c15cc473b` | **MATCH** |
| COVER DRAFT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` | `76b37ca3` | `76b37ca33be72f5311ded30693493ab431b5ac0820730c2f4d0081cfe9b5aa8c` | **MATCH** |
| COUNT RECEIPT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` | `806e1758` | `806e17589697c48c0078cc43f42c01736a80b1995a71947484358cc4c2c4aae9` | **MATCH** |
| COUNT JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` | `9730d432` | `9730d432735f48892eaceb0c3c8d73f3a104d4cf32a73dd0863cc9a23f546731` | **MATCH** |
| 叶33 正式脚本（只读） | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` | `afbbe7e7` | `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` | **MATCH UNCHANGED** |
| 叶32 HOLD（只读） | `docs/v2/ALPHA_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_GATE_REVIEW_20261027_ZH.md` | `45dd87dc` | `45dd87dc915b89e887e2b02dd1fae2cdcbe3b40695db6f9dce22b89e42ec5d9e` | **MATCH**（不回撤） |
| 构建脚本 `research/leaf34*` | — | ABSENT | ABSENT | **MATCH 预期** |
| 叶34 live `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF34*` | ABSENT | ABSENT | **MATCH** |
| live QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| live `.ok` 计数 | `output/ai_factory/*.ok`（非 `_consumed`/`_superseded`） | 0 | 0 | **MATCH** |
| ocf_to_profit 日表（只读） | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet` | 列含 ocf/NP/PIT | 9,754,991 行；列含 `ocf_to_profit`/`net_profit`/`denom_small`/`np_negative`/`e_available_at`/`period_basis`；文钉 sha8 `f9faf7e7` | **MATCH**（只读；未实算 α） |

对照模板：`docs/v2/audit/ARCH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_WHO_PAYS_REVIEW_20261027_ZH.md`（叶31–33 who_pays 亦是 **DRAFT** → CONDITIONS 含「须另窗冻结预注册」）。

### 1.1 COUNT 闸数字再核（JSON ↔ 主称）

| 指标 | JSON | 主称 | 结果 |
|---|---|---|---|
| gate_pass | true | true | **MATCH** |
| APPROX | 是（approx[] 非空） | APPROX | **MATCH**（诚实） |
| masked_median | 2431.0 | 2431 | **MATCH** |
| zero_frac_masked | 0.0 | 0 | **MATCH** |
| J20_max vs19 / vs25 | 0.0526 / 0.0526 | ≈0.053 | **MATCH**（≪0.7） |
| ρ_mean vs19 / vs25 | 0.3673 / 0.3690 | ≈0.37 | **MATCH**（未触 ρ>0.5 强度过滤均值闸） |
| peak_rss_mb | 899.99 | ≈900 | **MATCH**（<1500） |
| EXECUTED_full_alpha / ok_requested | false / false | false | **MATCH** |

附注：叶25 重叠样本日 2026-04-27 / 2026-10-09 的 `n_common=0`（ρ/J null）已在 JSON 披露；n_days_ok=4。X2 前须完整重算并解释尾窗空交（C7）。ρ_max vs25=0.5117 单日触及 >0.5，但规则为 ρ_mean 强度过滤 → 本拍未触；冻结/X2 仍须披露。

## 2. 必审清单

| # | 要点 | 结果 | 证据 |
|---|---|---|---|
| 1 | 机制可检验：`accrual_cf=1−ocf_to_profit` → top_q=0.20 剔除 → 交付 mask/soft-penalty overlay（非完整多空 α）；H/再平衡/符号纪律；失效条件齐 | **PASS** | WHO §0/§2/§9；COVER 公式钉同构；禁事后翻/冻结前未读收益选 q |
| 2 | **明确 ≠** 重开叶19/25/accrual_quality 主叶；Jaccard≥0.7 硬拒；ρ>0.5 强度过滤；另 vs 27/30/31/32/33 | **PASS_WITH_CONDITIONS** | WHO §1/§2 差表 + §8；COUNT 轻量只验 19/25；完整重叠 → **C7/C11** |
| 3 | COUNT 闸：masked_median≥300；zero_frac；J20；ρ；APPROX 披露诚实；**勿把计数当 X2 ACCEPT** | **PASS_WITH_CONDITIONS** | §1.1 MATCH；COUNT APPROX/GAP 醒目；文钉 ≠X2 → **C12** |
| 4 | PIN_GAP / 开放项：ocf_to_profit 数据源与 PIT、NP≤0、soft-penalty 是否须残差、top_q 冻结、FULLA 双轨 | **PASS_WITH_CONDITIONS** | WHO §2/§3/§4/§5；日表只读列齐；开放 → **C3–C6** |
| 5 | 禁卖方/金股/survey/TP/LLM/GP/高杠杆/moneyflow；rss=1500 | **PASS** | WHO 文首+§11；COVER 禁止清单；rss 意向 |
| 6 | DRAFT NOT FROZEN / EXECUTED_full_alpha=false / ok_requested=false / 无 `.ok` / QUIET ABSENT / 无构建脚本 | **PASS** | 文钉 + 盘证 §1；本拍未签未挂 |
| 7 | forbid 二十票 + `245df63f`+`c5ed13df`+`5774bb6e`（及叶33 探针 `81521fb5`） | **PASS** | WHO/COVER §11 钉齐；探针 CONSUMED 点名 → **C8** |
| 8 | `0087c928`/叶28/29 **本拍不审不夹带**；叶33/`afbbe7e7` UNCHANGED；叶32 HOLD 不回撤 | **PASS（未审声明）** | 主令；本回执未打开/未审 `0087c928`；叶28/29 另队；HOLD/正式只读对照 |
| 9 | decay KEEP 意向合理；KEEP 不解阻 X2 ACCEPT（叶32 教训） | **PASS_WITH_CONDITIONS** | WHO §7；预注册写死近端窗 → **C13** |
| 10 | 备选 (2)ETF/(3)问询函未混 PRIMARY | **PASS** | WHO §12；COVER：备选不升 |

## 3. 条件（冻结预注册 / 脚本 / X2 前必须满足）

1. **C1 须另窗冻结预注册**：本拍审的是 **DRAFT NOT FROZEN**（对齐叶31–33 who_pays）。PASS ≠ 可签 `.ok`。请主令 AI 出 FROZEN → Arch 再审 FROZEN → 再谈脚本/X2。
2. **C2 正式构建脚本尚未写**：`research/leaf34*` ABSENT（预期）。另窗 AI 写脚本 → Arch 审脚本 → 独立 X2 `.ok`；**本拍禁签**。
3. **C3 ocf_to_profit 数据源 / PIT / NP≤0**：冻结时写死——(a) 日表路径与 `e_available_at ≤ t` PIT；(b) `denom_small`/`np_negative`/`net_profit>0` 有效行；(c) `period_basis`/YTD-ish 口径是否接受或改季表/TTM；(d) NP≤0 名是否一律剔除（本 COUNT 已剔）或另规则。**勿静默改口径**。
4. **C4 soft-penalty 残差纪律**：若冻结选连续 soft-penalty（非纯 mask），须钉 SW L1 + log 流通市值 + style（mom20/vol20/logADV20）；缺列 → PIN_GAP。纯 mask 主路径可后钉残差，但须在 FROZEN 明示「mask-only」。
5. **C5 top_q=0.20 冻结纪律**：`q=0.20` 与「高应计=剔除」符号冻结写死；**禁**读收益改阈值/翻方向。
6. **C6 FULLA 双钉规格**：预注册须同时冻结 HI_LIQ（PRIMARY）与 FULLA（研究对照）；PRIMARY 不得静默改 FULLA。
7. **C7 X2 前完整重叠重算**：须用完整 overlay/α 重算 vs 叶19/25 **及** 27/30/31/32/33 的 Jaccard/ρ；解释叶25 尾窗 `n_common=0`；披露 ρ_max vs25 单日>0.5；DRAFT 轻量计数 **不能**替正式重叠证明。
8. **C8 禁 RESTORED / 禁复用旧窗**：forbid∋`245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`；另禁复用叶33 探针窗 `81521fb5`；禁复用叶25/27/30–33 `.ok`；禁 `--arch-ok-path` 自开。
9. **C9 rss=1500 + peak_proof**：未来执行窗硬 ABORT；禁抬。本拍计数 peak≈900 仅参考。
10. **C10 `0087c928`/叶28/29 另队**：本拍未审；不得借本审窗口夹带签跑。
11. **C11 overlay ≠ 应计主叶硬钉**：FROZEN/脚本须钉交付=**mask/soft-penalty overlay**；**禁**输出完整 CFACC/accrual_quality TopN 多空当本叶主 α；禁把叶19/25 α 当主输入。
12. **C12 APPROX 计数 ≠ X2 ACCEPT**：gate_pass（APPROX）仅放行继续 FROZEN/脚本讨论；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面。
13. **C13 decay KEEP 冻结口径**：预注册写死 `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300` + 近端窗；失败 → 最多 WATCH/HOLD；**KEEP 不解阻** X2 ACCEPT（叶32 HOLD `45dd87dc` 教训）。

## 4. 禁项（本回合）

- 不签 / 不改任何 `.ok`；不挂 QUIET；不代跑 python 重活 / 不实算完整 α / 不开全窗 X2
- 不改 WHO / COVER / COUNT / JSON DRAFT；不把 DRAFT 当 FROZEN；不把 COUNT 当 X2 ACCEPT
- 不触 A18；不解阻 X2；≠Book-Smoke
- 不审 `0087c928`；不夹带叶28/29；不回撤叶32 HOLD；不改叶33 正式 `afbbe7e7`；不推 Leo；live=false

## 5. 硬钉下一跳

```
who_pays DRAFT fa6aa2e3 + COVER 76b37ca3 + COUNT 806e1758 / JSON 9730d432
  （本审 PASS_WITH_CONDITIONS；gate_pass=true APPROX）
  → 请主择令 AI 出 FROZEN 预注册（钉 PIT/NP/top_q/overlay≠主叶）或 HOLD
      → Arch 审 FROZEN / 正式脚本（另窗；research/leaf34* 现 ABSENT）
          → 独立新窗 .ok（禁 RESTORED 245df63f+c5ed13df+5774bb6e+二十票+81521fb5）
              → X2（完整重叠重算含 19/25/27/30–33；rss+peak_proof；decay KEEP）
```

**本拍不签**。

## 6. 本回合非动作声明

- **未签**任何 `.ok`
- **未挂** QUIET
- **未代跑**构建/X2/selfcheck/完整 α；**未改** DRAFT/COUNT/JSON
- **未审**叶30 衰减修复 `0087c928`（另队）；**未夹带**叶28/29
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 只读不回撤
- **不推 Leo**；live=false；promotion=false；x2_accept=false；ok_requested=false；EXECUTED_full_alpha=false

## 7. 结论

**PASS_WITH_CONDITIONS** — WHO+COVER+COUNT DRAFT 契约可收；四件钉 MATCH；机制/正交（≠应计主叶）/COUNT 闸（APPROX 诚实；median=2431；J20≪0.7；ρ≈0.37）/双轨/禁项/rss/PIT/forbid 齐。开放项见 §3（C1–C13），首要 **另窗冻结预注册（请主择令 AI 出 FROZEN 或 HOLD）** 与 **C3 PIT/NP 口径 + C11 overlay≠主叶**。本回合不签、不挂、不代跑。

live=false.
