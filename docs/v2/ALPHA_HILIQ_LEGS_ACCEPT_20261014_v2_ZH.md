# HI_LIQ_V1.1 纸面腿正式验收（Alpha）— 2026-10-14（v2：AI 重生后复核）

- **更新**：2026-10-14 08:34 ET（v1 08:28 ET 被本版取代）
- 清单 `docs/v2/ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`（§2.1/§8）；范式 `docs/v2/ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`；AI 回执 `docs/v2/AI_HILIQ_V1_LEGS_REGEN_RECEIPT_ZH.md`
- JSON：`output/alpha/ALPHA_HILIQ_LEGS_ACCEPT_20261014.json`
- 不改 FROZEN/纸面；promotion/live=false；禁 GP；不派 Eng

## 0. 显式声明
1. Strategy 过渡 Top-N X2 = **仅诊断**，不得单独作 ACCEPT / 派 Book-Smoke / 纸面证据。
2. 主路径 = **OPTIMIZER Core（Leo）**；Eng capacity_adv Top-25@HI_LIQ = 对照，非纸面替换。
3. 密封窗 N/A（腿自 2024-01-02 起）。
4. 新叶站立规则：AI 已停卖方一致预期/金股/调研线；新叶优先残差正交 vs capacity_adv + CMC；研报类新叶直接拒收。report_rc（研报类）、insurer_surv（调研类）只保持 WATCH，不走新叶 ACCEPT 路径。

## 1. §2.1 复核方法
Alpha 独立重算：每个持仓日按 PIT 申万一级（`industry_on_date`），全窗所有持仓日（非抽样），sha 与 .check.json 一致。门槛：账面 ≤0.20（=袖预算 25%×0.80），书内 ≤0.25。根因（AI）：事件日行业粘滞→持仓期 PIT 改类超限；已修。

## 2. 逐腿表

| 腿 | ind_cap_ok_book | max_book | 袖预算 max | 袖内持仓占比 max | 四行业 X2 袖均（电/计/通/医） | 范式 §8 | 状态 |
|---|---|---|---|---|---|---|---|
| capacity_adv 195620 | True | 0.20（抽样 0.198） | 0.247 | — | 0.128/0.100/0.112/0.049 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS；Top-N X2 两档 MDD 破 25% 仅诊断） |
| equity_incentive 202436 | True | 0.20 | 0.25 | 0.25 | 0.188/0.081/0.034/0.098 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS） |
| earnings_event 202822 | True | 0.20 | 0.25 | 1.00 | 0.239/0.046/0.079/0.042 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS） |
| insider_increase 202928 | True | 0.20 | 0.25 | 0.25 | 0.065/0.044/0.008/0.102 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS） |
| insurer_surv 203108 | True | 0.20 | 0.25 | 0.25 | 0.170/0.073/0.044/0.085 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS；survey-type: WATCH only, not new-leaf ACCEPT path） |
| report_rc_allup 203201 | True | 0.20 | 0.25 | 1.00 | 0.134/0.082/0.029/0.083 | NOT_SUPPLIED | **WATCH**（INDUSTRY_PASS；report-type: WATCH only, not new-leaf ACCEPT path） |
| _rejected_ind_cap/ 195* 五包 | — | — | — | — | — | — | **REJECT_IND_CAP**（隔离，不得验收） |

注：earnings_event / report_rc_allup 稀疏日只持 1 只票（≤0.20，其余 510300），袖内占比达 1.0；闸门按预注册 §2 用袖预算口径，此处披露。insurer_surv 有 _UNK 行业权重（累计 0.08）、equity 0.04，均已计入且未超限。

## 3. 包级裁决
- **NO_ACCEPT**：六腿 §2.1 全过（INDUSTRY_PASS），可进 B4 / 密封合成的行业合格池；但 §8 A/A′/B/C 全缺 → 均 WATCH，不 ACCEPT、不派烟、不进纸面。
- 下一步：AI 补 HI_LIQ 上相对 capacity_adv 的残差 IC / 特质 α / 中性化超额 / 快慢错配；Alpha 再按叶验收 v2 判。
