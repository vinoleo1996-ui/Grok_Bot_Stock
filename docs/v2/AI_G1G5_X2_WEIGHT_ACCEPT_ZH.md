# Alpha 裁决 · AI G1G5 X2 日更权重包（主攻+对照）

**日期**：2026-10-12 · America/New_York  
**裁决总览**：主攻 **ACCEPT** · 对照 **ACCEPT** · `promotion_approved=false`  
**不做**：密封 · 扩 ACTIVE · Strategy 交接 · GP / dense_micro / search

| 角色 | 包 | 行/日/标的 | 跨度 | mechanism_tag | 裁决 |
|---|---|---|---|---|---|
| **主攻** | `g1g5_nontextbook_daily_weights_20261012_111316.parquet` | 33400/668/50 | 2024-01-02→**2026-10-09** | `g1g5_ashare_inst_friction_v1` | **ACCEPT** |
| 对照 | `g1g5_expand_daily_weights_20261012_111354.parquet` | 33400/668/50 | 2024-01-02→**2026-10-09** | `g1g5_pit_debate_rule_v2_expand` | **ACCEPT** |

- reaches_x2：两包 meta `reaches_x2_end=true`；面板 50/50 达末日。  
- 主攻 vs 对照：Spearman≈−0.07 · Jaccard≈0.22（非换皮）。  
- 主攻 vs 前版 110220：重叠 corr=1.0（真延伸）。  
- Eng validate：两包 `status=ok`。G6：两包 pass。  
- 明细：`AI_G1G5_X2_NONTEXTBOOK_WEIGHT_ACCEPT_ZH.md` · `AI_G1G5_X2_EXPAND_WEIGHT_ACCEPT_ZH.md`  
- 机读：`output/alpha/AI_G1G5_X2_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false`
