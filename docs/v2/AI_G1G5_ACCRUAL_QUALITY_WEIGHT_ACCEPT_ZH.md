# Alpha 裁决 · AI G1G5 应计质量叶（accrual_quality）

**日期**：2026-10-13 ~02:26 ET · America/New_York  
**包**：`output/ai_factory/g1g5_accrual_quality_daily_weights_20261013_022400.parquet`  
**meta**：`output/ai_factory/g1g5_accrual_quality_run_meta_20261013_022400.json`  
**G6 proof**：`output/ai_factory/debate_ledger_g1g5_accrual_quality_20261013_022400_g6_proof.jsonl`  
**AI 回执**：`docs/v2/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_ACCRUAL_QUALITY_WHO_PAYS_PREREG_ZH.md`  
**verify（AI）**：`output/alpha/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_VERIFY_STATS_20261013_022400.json`  
**裁决**：**ACCEPT（研究级）→ WATCH** · Book-Smoke **WATCH / DONE_FAIL** · **非** FactorCandidate · **非** live 晋级  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy 实盘权重** · **不下单** · **不密封** · **禁 GP** · **live=false**

对照十灭 + capacity_adv（paper_active）+ margin_delta（WATCH）+ northbound/OCF/d1_val（WATCH）：  
- expand / friction_monthly / lowturn / resid_etf / etf_core / friction_cost_redesign / idx_rebal_flow  
- indcap_momneut_ocf / d1_val_resid / northbound_flow / capacity_adv / margin_delta

---

## 1. 核验摘要（Alpha 盘面重算）

| 项 | 结果 |
|---|---|
| 规模 | ✅ **52772** 行 / **668** sessions / **79** 标的（与声称一致） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false`；再平衡 **35** 次日更展开（非 stub） |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；`weight≡target_weight`；date≡session |
| 日权重合计 | ✅ 恒 **1.0**（max\|Σw−1\|=0）；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **0.800** / 压舱 **0.200**（仅 `510300.SH`）；落在 0.15–0.25；**禁** etf_core 0.70 overlay |
| 活跃个股数 | ✅ 日活恒 **25**（设计 topN=25） |
| 单票硬顶 | ✅ 个股单名 **max=0.032**（≤4%）；违规日=**0** |
| **硬排除 600519/002371** | ✅ 包内 **0 行**（正权=0） |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_accrual_quality_v1` |
| `universe_id` | ✅ `g1g5_mid_large_liquid_top50`；`universe_kind=mid_large_stock`；PIT mid_large |
| `who_pays_zh` | ✅ 与预注册一致：PIT **BS 营运资本应计/TA**（无 Dep）→ 申万一级 demean → log(流通市值) 残差；**低应计优先**；主叙事=非 OCF 应计质量（资产负债表）；明确 **非** ocf_to_profit、非 EP/BM、非 ADV 分位、非两融/北向、非相对强弱/四臂/解禁/份额流/调仓/ETF-core |
| 主信号 | ✅ `accrual_primary=true`；公式 `WC_ACC=(ΔCA−ΔCash)−(ΔCL−ΔSTD−ΔTP)` / TA；主数据 `balancesheet_pit_tushare`（available_at PIT）；D1 仅 float_mktcap 协变量；**未**用 ocf_to_profit；**未**用 D2 moneyflow 主腿；**未**读 margin/hk_hold |
| 再平衡 | ✅ 月频 `month_end_plus_first_last`；n_rebal=**35** |
| 行业硬顶 | ✅ 设计 ≤**28%**；单名 ≤**4%** |
| vs indcap_momneut_ocf | ✅ Jaccard 均/max≈**0.128 / 0.194**；frac≥0.7=**0** |
| vs d1_val_resid | ✅ Jaccard 均/max≈**0.149 / 0.216**；frac≥0.7=**0** |
| vs capacity_adv | ✅ Jaccard 均/max≈**0.163 / 0.220**；frac≥0.7=**0** |
| vs margin_delta | ✅ Jaccard 均/max≈**0.174 / 0.289**；frac≥0.7=**0** |
| vs northbound_flow | ✅ Jaccard 均/max≈**0.130 / 0.212**；frac≥0.7=**0** |
| vs 十灭其余 | ✅ 全 frac≥0.7=**0**；全库最高 max≈**0.364**（friction_cost_redesign）；idx_rebal=0 |
| 同构硬闸 | ✅ **未触发**（≥0.7 ∧ 近等权）；机制差：BS 应计 ≠ OCF 兑现 ≠ EP 估值 ≠ ADV 分位 ≠ 两融 Δrzye ≠ hk_hold |
| G6 | ✅ proof `G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2079.3 MB**（软标 ≤1GB / 目标≤1.5GB **未达**）；与同厂叶（margin≈1978 / northbound≈2017）同量级 → **软缺口，非硬拒** |
| Book-Smoke | ⚠️ New Bot/Eng 回传 **已灭**：**5.50% / 5.81%** @60万∧100万 vs C0 **−5.77 / −5.45pp**；MDD −12.05%/−13.81%；**any_pass=false** · **research_candidate=false** · **handoff=NO** → **WATCH / DONE_FAIL**；回执 `docs/v2/BOOK_SMOKE_G1G5_ACCRUAL_QUALITY_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy / **勿再派烟**。非 Alpha 执行 |
| promotion | ✅ false；handoff=NO；no_gp；no Strategy；no main-book；no seal |

**硬闸**：未触发（stub / Σw 破 / who_pays 主轴换皮 / 600519·002371 正权 / 单名>0.04 / Jaccard≥0.7∧近等权 / G6 fail / OCF·估值·ADV·两融·北向换皮证据 / D2 moneyflow 冒充主腿）。

---

## 2. ACCEPT 范围（研究级；烟后 WATCH）

- **研究级**辩论权重：PIT 资产负债表 **营运资本应计/总资产**（Sloan 代理，无 Dep）→ 申万一级 demean → log 流通市值残差 → **低应计** top25 等权 + 行业≤28% + 单名≤4% + 硬排除巨头 + 压舱 510300≈20%；月频+首末日。  
- 相对十灭+容量+两融+OCF/估值/北向：活跃个股 Jaccard 均 ≪0.7（最高对照 max≈0.289 vs margin；全库 max≈0.364）；机制为 **BS 应计质量**，非 OCF 换皮、非估值/容量/两融/北向换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；**不跑 Book-Smoke**；不把本 ACCEPT 当工厂/晋级/live 授权。  
- Book-Smoke **已灭** → 状态 **ACCEPT→WATCH / DONE_FAIL**；**勿再派烟**；不交 Strategy；勿升主书；handoff=NO；live=false。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT；烟后保持 WATCH）

1. peak_rss ≈**2079.3 MB** 软标 ≤1GB（脚本目标≤1.5GB）未达 — 研究级可消费，记 **GAP**（与同厂叶一致）。  
2. **Book-Smoke WATCH**：已灭 **5.50% / 5.81%**（vs C0 −5.77/−5.45pp）；两端 CAGR 未进 [12%,18%]；MDD 两端 ≥−28% 过门；**handoff=NO** — **勿升主书** / 不交 Strategy / 勿再派烟。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. D2 moneyflow **未**作主腿（正确）；未当满样本。  
5. 金融缺 CA 跳过评分（RECEIPT：可评分≈57）— 设计可知悉，不硬拒。

---

## 4. who_pays 一行

投资者过度依赖应计盈余、低估低应计/资产负债表盈余的对手盘：以 PIT 资产负债表营运资本应计/总资产（Sloan 代理，缺 Dep 不加）经申万一级行业 demean + 对数流通市值残差分位选股；低应计优先；主叙事=非 OCF 应计质量（资产负债表）；明确非 ocf_to_profit、非 EP/BM 估值残差、非 ADV 容量分位、非两融/北向资金流、非相对强弱主轴、非四臂摩擦/解禁/份额流/调仓/ETF-core。

---

## 5. 机读

`output/alpha/AI_G1G5_ACCRUAL_QUALITY_WEIGHT_ACCEPT_20261013.json`

`status=RESEARCH_ACCEPT`（权重硬闸仍成立）· Book-Smoke **WATCH / DONE_FAIL** · `any_pass=false` · `research_candidate=false` · `promotion_approved=false` · **handoff=NO** · **勿升主书** · **不交 Strategy** · **禁 GP** · **live=false** · 十灭+容量+两融+OCF/估值/北向 Jaccard 硬拒未触发 · 600519/002371=0 · 单名 max=0.032 · peak_rss 软 GAP

---

## 6. Book-Smoke 标注（2026-10-13 ~02:44 ET）

- run_id `book_smoke_20261013_022718`；窗 X2；资金 60万∧100万；成本开；回执 `docs/v2/BOOK_SMOKE_G1G5_ACCRUAL_QUALITY_X2_RECEIPT_ZH.md`。  
- BOOK：**5.50% / −12.05%**（60万）、**5.81% / −13.81%**（100万）；相对 C0 ≈**−5.77 / −5.45pp**；CAGR 未进 [12%,18%]（MDD 两端 ≥−28% 过门，收益端不过）。  
- **any_pass=false** → **不标研究备选**（`research_candidate=false`）→ **WATCH / DONE_FAIL**。  
- **叶锁**：`promotion_approved=false` · **handoff=NO** · **live=false** · **勿升主书** · **不交 Strategy** · **禁 GP** · **勿再派烟** · **不密封** · **不下单**。  
- 权重包研究级 ACCEPT（硬闸/正交）**保持**；烟灭仅改 Book-Smoke 状态，不推翻盘面核验。  
- **禁止**：GP；升主书 live；交 Strategy 实盘；密封；把 RESEARCH_ACCEPT / paper 路径当工厂或 live 授权；Alpha 自跑/再派烟。
