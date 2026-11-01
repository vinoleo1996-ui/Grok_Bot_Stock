# Alpha 裁决 · AI G1G5 个股残差×ETF份额流 日更权重包

**日期**：2026-10-13 · America/New_York  
**包**：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
**meta**：`g1g5_resid_etf_daily_weights_20261013_002418.parquet.meta.json` / `g1g5_resid_etf_run_meta_20261013_002418.json`  
**AI 回执**：`docs/v2/AI_G1G5_RESID_ETF_WEIGHT_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（研究级辩论/主线残差×ETF 袖套）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE · 不密封 · **不跑 GP**

对照（勿当主线）：  
- 摩擦 X2：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- 降换手：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- 动量 expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **33400** 行 / **668** sessions / **50** 标的 · 日行恒 50 |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；max==2026-10-09 |
| stub 禁 | ✅ sessions=668 ≫10；`stub_window=false`；`stub_forward_fill=false` |
| reaches_x2 | ✅ meta `reaches_x2_end=true`；panel 50/50 达末日 |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 映射 ok |
| Eng validate | ✅ `status=ok` · 668 sessions · 非零 **13360** 行（=668×20）· `weight_long_v1_20261012` · `promotion_approved=false` |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；单票 ≤0.05；日活 **20** |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_resid_etf_flow_v1` |
| `who_pays_zh` | ✅ 残差定价修正 + ETF 创设/赎回对手盘；**明示排除**相对强弱/估值/质量主线；**无「动量」作主支付方**；明示非摩擦四臂复刻 |
| vs 摩擦 111316 | ✅ 相关但非同构：Spearman 均≈**0.27**（中位 0.25）；Jaccard 均≈**0.40**（中位 0.38）；日均仅新≈8.7/20 |
| vs expand 111354 | ✅ 非动量换皮：Spearman 均≈**0.29**（中位 0.33）；Jaccard 均≈**0.41**（中位 0.43） |
| vs lowturn 112301 | ✅ 明显分化：Spearman 均≈**0.05**；Jaccard 均≈**0.24** |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.0289**（与月频摩擦同量级；高于 lowturn 符合未做季频带宽） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_v29_gp=true` |
| 再平衡 | ✅ 月末+首日 **35** 次；top20 EW；三臂 0.55/0.30/0.15 |

## 2. ACCEPT 范围

- **研究级**辩论/评级权重上下文：个股行业残差×size demean + ETF 份额流 + 交互（主线残差×ETF 族）。  
- 相对摩擦包：去掉 unlock/T+1/limit 四臂，改残差主轴；相对 expand：不用 `excess_vs_510300` 动量排序。  
- **不做**：FactorCandidate 硬闸；密封；Strategy 交接；扩 ACTIVE；Alpha **不跑 GP / v29+**。

## 3. 缺口 / 标注（不阻断）

1. 宇宙仍为 mid_large **top50** 子集（`g1g5_mid_large_liquid_top50`）；待 Data D3 成员交叉审计不阻断本 ACCEPT。  
2. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选，符合 meta。  
3. 残差臂用 trailing 20 日行业内相对收益再 size demean — **不是** overnight 价差叶，也不是教科书 excess_vs_510300 排序；脚本禁动量/价值/quality token。若日后写入 **expr 短清单**，须另过短清单专审（含 overnight 精神禁令）。  
4. peak_rss ≈**1767.7 MB**（≤2GB）— 通过。  
5. Book-Smoke @60万∧100万 vs 510300：**未**由 Alpha 执行；可交 New Bot / Beta，非本裁决范围。

## 4. who_pays 一行

个股残差×行业 ETF 申赎份额流：行业内相对收益残差经流通市值三分位中性化后的定价修正对手盘 + ETF 创设/赎回对手盘；**明确排除**教科书相对强弱/估值/质量主线；非摩擦四臂复刻。

## 5. 机读

`output/alpha/AI_G1G5_RESID_ETF_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false`
