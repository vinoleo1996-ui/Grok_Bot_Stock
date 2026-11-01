# Alpha 裁决 · AI G1G5 非教科书日更权重包（X2 延伸）

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
**meta**：`g1g5_nontextbook_daily_weights_20261012_111316.parquet.meta.json` / `g1g5_nontextbook_run_meta_20261012_111316.json`  
**AI 回执**：`docs/v2/AI_G1G5_X2_EXTEND_GP_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（辩论权重袖套 · 非教科书主攻 X2 延伸）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE · 不密封

对照包：`g1g5_expand_daily_weights_20261012_111354.parquet`（动量）**保留备选/对照**。  
前版：`g1g5_nontextbook_daily_weights_20261012_110220.parquet`（242 sessions）为本包重叠窗完美延续（corr=1.0）。

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **33400** 行 / **668** sessions / **50** 标的 · 日均 50 行 |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；max==2026-10-09 |
| stub 禁 | ✅ sessions=668 ≫10；`stub_window=false`；非前推 stub |
| reaches_x2 | ✅ meta `reaches_x2_end=true`；`panel_coverage_x2` 50/50 达末日；相对前版 +426 sessions |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 映射 ok |
| Eng validate | ✅ `status=ok` · 668 sessions · 非零 13360 行（=668×20）· `weight_long_v1_20261012` |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；单票 ≤0.05；日活 **20** |
| `mechanism_tag` | ✅ 行级非空 · `g1g5_ashare_inst_friction_v1` |
| `who_pays_zh` | ✅ 明示排除教科书相对强弱/估值排序；**无「动量」字样**；制度摩擦（ETF/解禁/T+1/涨跌停） |
| vs expand X2 | ✅ 分化：Spearman≈**−0.07**（中位 −0.08）；Jaccard≈**0.22**；非换皮 |
| vs 前版 110220 | ✅ 重叠 242 日 corr=**1.0** / Jaccard=**1.0**（真延伸，非重生漂移） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true` |

## 2. ACCEPT 范围

- 辩论/评级主攻权重上下文（制度摩擦 X2 全日更至 2026-10-09）。  
- **不做**：FactorCandidate 硬闸；密封；Strategy 交接；扩 ACTIVE；GP / dense_micro / search。

## 3. 缺口 / 标注（不阻断）

1. **「隔夜抛压」措辞**：who_pays 描述 T+1 制度对手盘，**不是** `overnight_ret` / `ind_rel_overnight` 价差叶。本包 ACCEPT 为辩论袖套；若日后把同名机制写进 **expr 短清单**，须另过 HARD_BAN_OVERNIGHT_SPIRIT 专审。  
2. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选，符合 meta。  
3. 宇宙仍为 mid_large **top50** 子集。  
4. AI 回执记 peak MEM 略超 2GB WARN — 不阻断权重 ACCEPT；后续重生可压内存。

## 4. who_pays 一行

A股制度摩擦组合：行业ETF申赎份额流 + 解禁供给残差 + T+1隔夜抛压对手盘 + 涨跌停带宽；**明确排除**教科书相对强弱/估值排序。

`promotion_approved=false`
