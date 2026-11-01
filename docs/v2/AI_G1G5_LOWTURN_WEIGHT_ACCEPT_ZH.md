# Alpha 裁决 · AI G1G5 降换手日更权重包（制度摩擦变体）

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
**meta**：`g1g5_lowturn_daily_weights_20261012_112301.parquet.meta.json` / `g1g5_lowturn_run_meta_20261012_112301.json`  
**AI 回执**：`docs/v2/AI_G1G5_LOW_TURNOVER_RECEIPT_ZH.md`  
**基线（已 ACCEPT）**：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
**裁决**：**ACCEPT（辩论权重袖套 · ashare_inst_friction 降换手变体）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE · 不密封 · **不跑 GP**

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **33400** 行 / **668** sessions / **50** 标的 · 日行恒 50 |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；max==2026-10-09 |
| stub 禁 | ✅ sessions=668 ≫10；`stub_window=false`；`stub_forward_fill=false` |
| reaches_x2 | ✅ meta `reaches_x2_end=true`；panel 50/50 达末日 |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 映射 ok |
| Eng validate | ✅ `status=ok` · 668 sessions · 非零 **10374** 行 · `weight_long_v1_20261012` · `promotion_approved=false` |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；单票 ≤1/12≈0.083（等权于当日活跃集） |
| 日活持仓 | ✅ 带宽粘性下 **12–20**（均≈15.5）；非硬切 top20 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_inst_friction_v1_lowturn`（摩擦族 `_lowturn` 后缀） |
| `who_pays_zh` | ✅ 制度摩擦四臂 + 季频/带宽压成本；**明示排除**相对强弱/估值排序；**无「动量」字样** |
| 换手 vs 111316 | ✅ 日均单向 mean_one_way **0.00752** vs 基线 **0.02871**；降幅 **≈73.82%**（与 AI `turnover_reduction_ratio=0.738` 一致）；非零换手日 **12**/667 vs 基线 34 |
| vs 111316 相关 | ✅ 同族正向但更平滑：Spearman 均≈**0.185**（中位 0.083）；Jaccard 均≈**0.337**（中位 0.28）— 季频+粘性导致持仓分化，**非**换皮、**非**反相关对照 |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true` |
| 再平衡 | ✅ 季末+首末日 **13** 次；进 top12 / 出 rank>28；`cadence=quarter_end_plus_edges` |

## 2. ACCEPT 范围

- 辩论/评级 **降换手**权重上下文（制度摩擦 X2 全日更 + 季频带宽粘性）。  
- 相对月频非教科书 X2（111316）为**同机制变体**，非新机制、非动量包。  
- **不做**：FactorCandidate 硬闸；密封；Strategy 交接；扩 ACTIVE；Alpha **不跑/不停** GP。

## 3. 缺口 / 标注（不阻断）

1. **「隔夜抛压」措辞**：who_pays 描述 T+1 制度对手盘，**不是** `overnight_ret` 价差叶。本包 ACCEPT 为辩论袖套；若日后写入 **expr 短清单**，须另过 HARD_BAN_OVERNIGHT_SPIRIT 专审。  
2. 日活 12–20（非固定 20）与单票可达 ~8.3% — 设计使然（等权活跃集）；成本/AUM 情景须据此，勿当固定 5% 顶 20。  
3. vs 111316 秩相关中等（非「高相关」）— 符合降频+粘性预期；以换手降幅与机制/who_pays 同族为 ACCEPT 主据。  
4. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选，符合 meta。  
5. **GP v28（只读注记）**：`docs/v2/AI_GP_NEWLEAF_START_RECEIPT_ZH.md` — AI 已启 `v28_newleaf_friction`（PID 见回执，落盘时 alive）；Alpha **未**启动/终止 GP；禁 v27；**不晋级**。空跑结果不在本裁决范围。

## 4. who_pays 一行

A股制度摩擦组合（ETF份额流 / 解禁残差 / T+1 / 涨跌停）+ 季频带宽粘性压换手；**明确排除**教科书相对强弱/估值排序。

## 5. 机读

`output/alpha/AI_G1G5_LOWTURN_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false`
