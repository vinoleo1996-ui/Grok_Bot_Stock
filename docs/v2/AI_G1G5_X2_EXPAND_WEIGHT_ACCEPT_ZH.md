# Alpha 裁决 · AI G1G5 扩池/动量日更权重包（X2 延伸 · 对照）

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
**meta**：`g1g5_expand_daily_weights_20261012_111354.parquet.meta.json` / `g1g5_expand_run_meta_20261012_111354.json`  
**AI 回执**：`docs/v2/AI_G1G5_X2_EXTEND_GP_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（辩论权重袖套 · 动量对照 X2 延伸）** · **非** FactorCandidate · **非主线**  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE · 不密封

角色：备选/对照（动量）；主攻见 nontextbook `111316`。  
前版：`g1g5_expand_daily_weights_20261012_105459.parquet`（242 sessions）。

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **33400** 行 / **668** sessions / **50** 标的 · 日均 50 行 |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；max==2026-10-09 |
| stub 禁 | ✅ sessions=668 ≫10；`stub_window=false` |
| reaches_x2 | ✅ meta `reaches_x2_end=true`；面板 50/50 达末日；相对前版 +426 sessions |
| 列契约 | ✅ AI+权威别名齐全；Eng `validate_weight_path` **ok**（668 sessions / 13360 非零行） |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；单票 ≤0.05；日活 **20** |
| `mechanism_tag` | ✅ `g1g5_pit_debate_rule_v2_expand` |
| `who_pays_zh` | ✅ 截面动量 PIT 规则选股；文案含「非隔夜」；正向 overnight 叶命中 **0** |
| vs nontextbook X2 | ✅ Spearman≈**−0.07**；Jaccard≈**0.22**（对照分化成立） |
| vs 前版 105459 | ✅ 重叠窗 Spearman≈**0.92** / Jaccard≈**0.91**（同袖套延伸；轻微再选差异，不阻断） |
| G6 | ✅ `g6_proof.G6=pass` |
| promotion / not_mainline | ✅ false / true |

## 2. ACCEPT 范围

- 辩论/评级**对照**权重上下文；动量备选全日更至 X2。  
- **不做**：当主攻；进 hard_gates；密封；Strategy；扩 ACTIVE。

## 3. 缺口 / 标注（不阻断）

1. 仍无双读 ICIR / 冲击两档 — 定位对照袖套。  
2. `who_pays_zh` 含「截面动量」— 若误丢进非教科书闸会撞车；本 ACCEPT **仅作对照**。  
3. 相对前版重叠窗 corr≈0.92 非 1.0：X2 重生在共用窗有轻微持仓差异；机制/宇宙/结构一致，不阻断。  
4. 宇宙为 pit **top50** 子集。

`promotion_approved=false`
