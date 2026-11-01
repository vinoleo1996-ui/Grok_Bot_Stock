# Alpha 裁决 · AI G1–G5 日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_daily_weights_20261012_104627.parquet`  
**回执**：`docs/v2/AI_G1G5_WIRING_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（辩论权重袖套 / 消费可接）** · **非** factor_evolve 候选闸门包  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE primary

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 存在 / 行数 | ✅ 726 |
| distinct sessions | ✅ **242**（2024-01-02→2024-12-31）· **非 stub**（≤10 阈值） |
| 列 | ✅ `date,instrument,target_weight` + 权威别名 `session,instrument_id,weight` 齐全 |
| date≡session / weight≡target_weight | ✅ |
| `mechanism_tag` 行级非空 | ✅ 恒 `g1g5_pit_debate_rule_v1` |
| `who_pays_zh` | ✅ 非空 |
| `universe_id` | ✅ `g1g5_mid_large_liquid` |
| Eng `validate_weight_path` | ✅ `status=ok`（权威三列；非零约 585 行 / 195 session） |
| overnight 精神 | ✅ who_pays 文案明示非隔夜 |
| promotion | ✅ false（回执）；parquet 无该列（见缺口） |

## 2. ACCEPT 范围

- **可接**：辩论 / 评级权重上下文；`WeightLongTableSleeve` 形状消费；与 `QUANTMIND_P0_GATE_WEIGHT_CONTRACT` 日更列别名对齐。  
- **不可接为本轮动作**：当作 `FactorCandidate` 进 `hard_gates` 晋级/扩 ACTIVE；Book-Smoke 密封；Strategy 权重交接。

## 3. 缺口清单（不阻断本 ACCEPT）

1. **窄标的**：仅 3 只（600519/601318/000858）——全日历有、截面极窄；后续若称「全宇宙日更」须扩池或改名以免误读。  
2. **非 evolve 候选**：表内无 `icir_eps_gate` / `icir_eps_posthoc` / `impact_flat25_pct_60万|100万`——符合回执「辩论规则袖套」定位；**勿**丢进 `factor_evolve` 硬闸当因子候选。  
3. **契约版本字符串漂移**：回执写 `weight_long_v1_qm_p0_20261012`；Eng 模块 `COLUMN_CONTRACT_VERSION=weight_long_v1_20261012`；parquet **无** `column_contract_version` 列——建议 meta sidecar 统一，避免各写各的。  
4. **`promotion_approved` 未落列**：仅文档/回执声明；建议 meta.json 并列 `promotion_approved=false`。  
5. **宇宙未接 Data PIT**：`g1g5_mid_large_liquid` 自研标签；等 Data D3 `mid_large_members_pit` 后再交叉审计（不阻断本包研究消费）。

## 4. 下一步

- AI：可继续 G1–G5 接线；扩标的或补 meta sidecar 时再喊 Alpha 复核。  
- Alpha：等 Data P0 D1–D4；等下一 GATE_OK>0 因子包再短清单裁决；**不启 GP**。

`promotion_approved=false`
