# 叶35 ETF 被动资金压力 overlay · who_pays 封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T12:42:00-04:00（America/New_York；墙钟 2026-10-27 12:42 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **EXECUTED_full_alpha=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑全窗** · 轻量计数已做 · **未挂 QUIET** · Arch **只审不签** · live=false · promotion_approved=false
- **票种**：**新叶 who_pays 提案 + 轻量计数闸**（**≠** selfcheck · **≠** Book-Smoke · **≠** X2 ACCEPT · **≠** 叶30–34 RESTORED）
- **主令**：2026-10-27 ~12:35 ET dig 文内 `814e8a68` / 磁盘 `7f1e2bb4`；叶34 HOLD CLOSED → 续挖叶35（优先 ETF 被动压力 overlay；避 25/27/30–34 同构；**禁**重开叶26 同构）

## 一句话

叶34 `HIGH_ACCRUAL_EXCLUSION_OVERLAY` **X2 selfcheck HOLD CLOSED**（`.ok` `178e90e9`；lift `3fce510e`；回执 `a37257b9`；ρ≈0.960841；Gate 全 false）。本票提案 **叶35 PRIMARY = ETF 申赎→成分被动压力 overlay**（`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`）：`pressure=Σ w×flow_est` → 池内 top 20% `|pressure|` **soft-penalty / exclusion-tilt 叠主干**；**不是**叶26 完整多层残差 α 主叶；**不是**交易 ETF。轻量计数 **gate_pass=true**（median=1552.5；J20_max vs moneyflow≈0.25；叶26 残差 α GAP；APPROX）。请主**排号→Arch 只审不签**；过闸后再裁 FROZEN→Arch→X2。

## 对照钉

| 项 | 值 |
|---|---|
| 叶号意向 | **35**（28/29 FROZEN；26 DRAFT 另队勿重开同构；34 HOLD CLOSED） |
| mechanism_tag | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1` |
| who_pays | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| dig | 文内钉 `814e8a68` / 磁盘 `7f1e2bb4`（`DIG_FACTOR_20261027_1235ET.md`） |
| 叶34 HOLD CLOSED | `.ok` `178e90e9` · lift `3fce510e` · 回执 `a37257b9` · ρ≈0.960841 · ≠X2 ACCEPT |
| 叶33 / 32 HOLD | 正式 `afbbe7e7` / HOLD `45dd87dc`（不回撤） |
| 反叶26 | 形态 A overlay ≠ 完整残差 α 主叶；映射 510300↔000300、510500↔000905、512100↔000852 |
| 正交硬拒 | vs moneyflow_resid Jaccard≥0.7；叶26 残差 α GAP（本拍不伪造）；叶8a GAP |
| q / rebal | DRAFT top **20%** `|pressure|` / **20** 交易日 |
| 交付 | 形态 A：soft-penalty / exclusion-tilt；叠主干 |
| 计数闸 | **gate_pass=true**（APPROX；见 COUNT RECEIPT） |
| rss 意向 | **1500** 禁抬 |
| forbid | `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票` |
| `0087c928` / 叶28/29 | 另队不夹带 |
| EXECUTED_full_alpha | **false** |

## 提案摘要（mechanism / 数据 / 公式）

| 项 | 内容 |
|---|---|
| mechanism | ETF 产品层申赎→成分被动压力 overlay；忽视机械冲击仍满仓者付钱 |
| 数据路径 | `etf_share_flow_pit_major.parquet` + `index_weight_csi300_500_1000.parquet`（无 available_at→APPROX）+ HI_LIQ mask |
| 公式 | `pressure=Σ w×flow_est`；`H_t=top 20% |pressure|`；soft-penalty / mask on H_t |
| 与叶26 差 | 26=完整多层残差 α 主叶；本叶=尾部 overlay 叠主干 |
| 宇宙 | HI_LIQ 主判决 |
| X2 窗意向 | 2024-06-03 → 2026-10-09 |
| decay KEEP | latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300 |
| 判定 | 主干级或 ρ_excess vs capacity_adv<0.5 且 60万/100万叠加优于主干 |

## 禁止清单（forbid）

- 申 `.ok` / 全窗 X2 / Book-Smoke / selfcheck / 升纸面 / 挂 QUIET
- 重开叶26 完整残差 α 同构；碰 RESTORED `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5` + 二十票
- 禁改叶33 `afbbe7e7`；夹带 `0087c928`；叶28/29 升 PRIMARY
- 卖方/金股/个股 moneyflow/行业 ETF 持仓当本叶主信号；GP/杠杆；hk_hold/margin/Amihud/解禁/应计换皮
- git commit；报 Leo

## 请主 / Arch

1. **主**：确认叶号（默认 **35**）→ 收 who_pays+COVER+COUNT → hand Arch **只审不签**；通过后再谈预注册冻结/脚本窗 / 独立 `.ok`+X2。
2. **Arch**：只审文档契约与正交/禁项/PIT/APPROX/反叶26；**不签** `.ok`；不代跑。
3. 备选问询函不升；仅当 PRIMARY 后续硬拒时由主改派。

## 盘证

| 件 | 路径 |
|---|---|
| WHO_PAYS | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` |
| dig | `output/d1/DIG_FACTOR_20261027_1235ET.md`（文内 `814e8a68` / 磁盘 `7f1e2bb4`） |

live=false · ≠X2 · ok_requested=false · EXECUTED_full_alpha=false · QUIET 未挂 · leo_notify=false
