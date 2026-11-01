# moneyflow_resid 叠仓抬 Calmar 一页建议（主 Agent + Strategy）

- **日期**：2026-10-25 ET · America/New_York  
- **作者**：QuantLab Alpha  
- **对象**：主 Agent、Strategy  
- **锁**：`promotion_approved=false` · `live=false` · `handoff=NO` · 禁 GP · 不改 FROZEN_CONFIG  
- **依据**：`AI_G1G5_MONEYFLOW_RESID_WEIGHT_ACCEPT_ZH.md`；`BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md`；`ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`；`ALPHA_GATE_AB_PREREG_20261014_ZH.md`；`GATE_V3_MDD25_PREREG_ZH.md`；叶24 CMC v1.2 正式结果（WATCH）

## 结论先行

**moneyflow_resid 保持 RESEARCH_ACCEPT（研究级）+ Book-Smoke WATCH/DONE_FAIL；不要再单独当主腿冲年化。**  
要抬 Calmar，只能走「相对 capacity_adv（HI_LIQ）的小权重卫星叠仓 + 门B / GATE_V3 组合诊断」；单独 X2 账本已证明抬不动 CAGR，且相对纯 510300 为负。

## 1. 现状一句话

研究级权重硬闸与正交已过（个股≈0.76 + 510300≈0.24；月频；mf/ADV→SW L1 demean→log 市值残差；universe 当时 mid_large top50），但 X2 Book-Smoke：**60万 CAGR 9.75% / MDD −15.25%；100万 9.70% / −16.27%；vs 纯510300 −1.52 / −1.57pp；any_pass=false；handoff=NO**。MDD 已浅于门锁 −28%，**收益端未进 [12%,18%]**，故单独抬不了年化；勿再派烟。

纸面主干仍是 **capacity_adv（HI_LIQ）**。CMC / GATE_V3 对卫星是**组合级相对 capacity_adv**；门B = 两档 Calmar 胜主干且 MDD≤15%。背景：叶24 CMC v1.2 正式结果**维持 WATCH**（B0 净 CAGR 1.26% / MDD −36.6%），说明底座弱时卫星绝对账好看也难晋级。

## 2. 三条可执行叠法（按优先）

### (A) 优先：小权重卫星叠 capacity_adv + 门B / GATE_V3 组合诊断

| 项 | 口径 |
|---|---|
| 输入 | 主干=`capacity_adv` HI_LIQ 纸面权重；卫星=`g1g5_moneyflow_resid_daily_weights_*`（只取个股侧，**剥掉表内 510300 压舱**后再归一，避免双计） |
| 混合 | 主口径 **80/20**（主干/卫星）；90/10、70/30 仅敏感性，不判定 |
| 检验门 | **门B**：两档 Calmar 严格优于 capacity_adv 单跑，且 MDD≤15%；并报 **GATE_V3**：两档 MDD≤25%、两档净 CAGR>capacity_adv、衰减 KEEP、双边换手≤20%/日 |
| 快慢 | moneyflow **慢（月频）** vs capacity_adv 调仓节奏须披露 ρ / 半衰期；叠加增量须来自正交而非伪耦合（范式 C） |
| 禁止 | 把单独 X2 BOOK 数字当过门；再派本叶烟；升 paper 主腿；与 etf_core overlay 双计压舱 |

### (B) 次选：先对 capacity_adv 再残差正交，再叠

| 项 | 口径 |
|---|---|
| 输入 | 同 (A) 权重长表 + capacity_adv 活跃集/信号 |
| 残差化 | 卫星信号在同日截面上再对 **capacity_adv 暴露（或活跃集指示）+ SW L1 + log 流通市值 + 滚动β** 回归取残差，再 topN；产出新研究权重包（须 Arch 新窗 .ok，**本文件不授权跑**） |
| 检验门 | 研究级 A+A′（残差 IC/ICIR + 特质α）→ 再走 (A) 的门B/GATE_V3；Jaccard vs capacity_adv / 已 ACCEPT 腿 frac≥0.7∧近等权 → 硬拒 |
| 禁止 | 跳过残差直接等权 Top-N 当闸门证据；无 .ok 实数据重跑 |

### (C) 备选：HI_LIQ 重表达后再 CMC（非 mid_large top50）

| 项 | 口径 |
|---|---|
| 输入 | 同机制（mf/ADV→行业 demean→log 市值残差），**宇宙改 HI_LIQ_V1.1**（非 `g1g5_mid_large_liquid_top50`）；压舱规则跟 HI_LIQ 叶（单名顶等与叶23/24 对齐） |
| 检验门 | 叶验收 v2：HC→单叶→**CMC 相对 capacity_adv**→衰减→GATE_V3 本地；CMC 只能维持/下调，不得单靠本叶上调主书 |
| 禁止 | 旧 mid_large 包直接冒充 HI_LIQ；与当前 WATCH 叶简单加权求和冒充边际 |

## 3. 明确禁止

1. **勿再单独派 X2 烟**（本叶已 WATCH/DONE_FAIL；handoff=NO）。  
2. **勿当 paper 主腿**；paper 主干仍是 capacity_adv。  
3. **勿与 etf_core overlay 双计压舱**（表内已有 510300≈0.24；叠仓时须剥舱或 sleeves.core=0）。  
4. **`promotion_approved=false` · `live=false`**；不交 Strategy 实盘；不密封；禁 GP。

## 4. 给 Strategy 的接口建议

| 项 | 建议 |
|---|---|
| 权重列 | 权威消费：`session,instrument_id,weight`（与 AI `date,instrument,target_weight` 可逆映射）；日 Σw=1；非负 |
| sleeve 角色 | `alpha_slow_moneyflow`（**慢·月频**）；与快事件袖套分账 |
| 比例上限 | 组合内卫星名义建议 **≤20%**（门A/B 主口径）；敏感性可读 10%/30%，不扩上限 |
| 压舱 | 叠进 capacity_adv 账时：**禁止**再加 core/etf_core；表内 510300 须先剥离再按卫星预算缩放 |
| 交付 | 仅研究诊断包（门B/GATE_V3 对照表）；**不**触发 handoff / 纸面扩 ACTIVE |

## 5. 下一步（Alpha 侧）

1. 等 Strategy 确认剥舱+80/20 接口后，由主 Agent 派 **组合诊断**（非本叶再烟）。  
2. 叶25（cf accruals desens）Arch 新窗 .ok→AI 跑→Alpha 闸门审；与本叶正交表一并更新。  
3. 下一批正交叶定义见 `docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md`。

---
**sha256**（文件正文，不含本尾栏）：`aa927891e50e06ffe234682fdad95899ab463cc2027dad99bafcb422da866b8b`  
**path**：`docs/v2/ALPHA_MONEYFLOW_RESID_CALMAR_STACK_NOTE_20261025_ZH.md`
