# Alpha 裁决 · AI G1G5 非教科书日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_nontextbook_daily_weights_20261012_110220.parquet`  
**meta**：`g1g5_nontextbook_run_meta_20261012_110220.json` / `.meta.json`  
**回执**：`docs/v2/AI_G1G5_NONTEXTBOOK_WEIGHT_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（辩论权重袖套 · 当前主攻可接）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE primary

对照包：`g1g5_expand_daily_weights_20261012_105459.parquet`（动量）**保留备选，未废弃**。

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ 12100 行 / **242** sessions / **50** 标的 · 非 stub |
| 列契约 | ✅ AI+权威别名齐全；Eng validate ok |
| 日权重合计 | ✅ 恒 **1.0**；单票 ≤0.05；日活 20 |
| `mechanism_tag` | ✅ `g1g5_ashare_inst_friction_v1` 行级非空 |
| `who_pays_zh` | ✅ 明示排除教科书相对强弱/估值排序；**无「动量」字样** |
| vs expand 权重 | ✅ 同宇宙但权重分化（corr≈−0.19；非换皮） |
| vs `mid_large_members_pit` | ✅ 抽样 2024-06-28：**50/50** |
| G6 | ✅ meta `G6=pass` |
| promotion / not_hard_gates | ✅ false / true |

## 2. ACCEPT 范围

- 辩论/评级主攻权重上下文（制度摩擦：ETF 份额流 + 解禁供给 + T+1 抛压 + 涨跌停带宽）。  
- **不做**：FactorCandidate 硬闸；密封；Strategy；扩 ACTIVE。

## 3. 缺口 / 标注（不阻断）

1. **「隔夜抛压」措辞**：who_pays 描述 T+1 制度对手盘，**不是** `overnight_ret` / `ind_rel_overnight` 价差叶。本包 ACCEPT 为辩论袖套；若日后把同名机制写进 **expr 短清单**，须另过 HARD_BAN_OVERNIGHT_SPIRIT 专审（持有窗残差叶仍禁 overnight*）。  
2. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选，符合 meta。  
3. 宇宙仍为 mid_large **top50** 子集。

`promotion_approved=false`
