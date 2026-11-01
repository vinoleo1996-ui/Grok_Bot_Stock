# Alpha 裁决 · AI G1–G5 扩池日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/intel/g1g5_expand_daily_weights_20261012_105459.parquet`  
**meta**：`output/intel/g1g5_expand_run_meta_20261012_105459.json`  
**回执**：`docs/v2/AI_G1G5_EXPAND_G6_RECEIPT_ZH.md`  
**裁决**：**ACCEPT（辩论权重袖套 / 扩池可接）** · **非** FactorCandidate 硬闸包  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE primary

相对旧包 `g1g5_daily_weights_20261012_104627`（3 标的）本包为扩池重生；旧包仍可作窄对照。

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 行数 / sessions / 标的 | ✅ **12100 / 242 / 50**（2024-01-02→2024-12-31） |
| stub | ✅ `stub_window=false`；sessions≫10 |
| 列别名 | ✅ AI 列 + 权威 `session,instrument_id,weight` |
| date≡session / weight≡target | ✅ |
| `mechanism_tag` | ✅ 行级非空 · `g1g5_pit_debate_rule_v2_expand` |
| `who_pays_zh` | ✅ 非空；文案含「非隔夜」· 正向 overnight 命中 **0** |
| `universe_id` | ✅ `g1g5_mid_large_liquid_top50` |
| vs Data `mid_large_members_pit` | ✅ 抽样 session `2024-06-28`：**50/50 in_pit** |
| 日权重和 | ✅ 每日 gross **=1.0**；单票 ≤0.05；日活约 20 名 |
| Eng `validate_weight_path` | ✅ `status=ok`（非零 4840 行 / 242 session） |
| meta `promotion_approved` | ✅ false；`column_contract_version=weight_long_v1_20261012` + qm_alias |
| G6 | ✅ meta `g6_proof.G6=pass`（as_of 过滤挡前视） |

## 2. ACCEPT 范围

- 辩论 / 评级权重上下文；扩池全日更消费。  
- **不做**：进 `hard_gates` 当因子候选；密封 Book-Smoke；Strategy 交接；扩 ACTIVE。

## 3. 缺口（不阻断）

1. 仍无双读 ICIR / 冲击两档 — 定位辩论袖套，**勿**当 evolve 候选。  
2. `who_pays_zh` 含「截面动量」字样 — 若误丢进 textbook 闸会撞车；本 ACCEPT 不走该闸。  
3. 宇宙为 pit **top50** 子集，非全 `mid_large`；命名已标明 top50。

`promotion_approved=false`
