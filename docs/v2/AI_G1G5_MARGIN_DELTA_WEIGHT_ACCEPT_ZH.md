# Alpha 裁决 · AI G1G5 两融融资余额边际变化叶（margin_delta）

**日期**：2026-10-13 ~02:10 ET · America/New_York  
**包**：`output/ai_factory/g1g5_margin_delta_daily_weights_20261013_020825.parquet`  
**meta**：`output/ai_factory/g1g5_margin_delta_run_meta_20261013_020825.json`  
**G6 proof**：`output/ai_factory/debate_ledger_g1g5_margin_delta_20261013_020825_g6_proof.jsonl`  
**AI 回执**：`docs/v2/AI_G1G5_MARGIN_DELTA_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_MARGIN_DELTA_WHO_PAYS_PREREG_ZH.md`  
**verify（AI）**：`output/alpha/AI_G1G5_MARGIN_DELTA_WEIGHT_VERIFY_STATS_20261013_020825.json`  
**裁决**：**ACCEPT（研究级）→ WATCH** · Book-Smoke **WATCH / DONE_FAIL** · **非** FactorCandidate · **非** live 晋级  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy 实盘权重** · **不下单** · **不密封** · **禁 GP** · **live=false**

对照十灭 + capacity_adv（paper_active）+ northbound（WATCH）：  
- expand / friction_monthly / lowturn / resid_etf / etf_core / friction_cost_redesign / idx_rebal_flow  
- indcap_momneut_ocf（WATCH）/ d1_val_resid（WATCH）/ northbound_flow（WATCH）/ capacity_adv（paper_active）

---

## 1. 核验摘要（Alpha 盘面重算）

| 项 | 结果 |
|---|---|
| 规模 | ✅ **32732** 行 / **668** sessions / **49** 标的（与声称一致） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false`；唯一组合指纹=**35**=再平衡次数（日更展开，非 10 日 stub） |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；`weight≡target_weight`；date≡session |
| 日权重合计 | ✅ 恒 **1.0**（max|Σw−1|=0）；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **≈0.736** / 压舱 **≈0.264**（仅 `510300.SH`）；压舱略高于预注册 0.15–0.25 带 → **软缺口** |
| 活跃个股数 | ✅ 日活 **18–25**（均≈23；设计 topN=25） |
| 单票硬顶 | ✅ 个股单名 **max=0.032**（≤4%）；违规日=**0**；压舱单日最高≈0.424（余量归压舱，**非**个股破顶） |
| **硬排除 600519/002371** | ✅ 包内 **0 行**（正权=0） |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_margin_delta_v1` |
| `universe_id` | ✅ `g1g5_mid_large_liquid_top50`；`universe_kind=mid_large_stock`；脚本 `mid_large_members_on` + PIT |
| `who_pays_zh` | ✅ 与预注册一致：全窗 **Δrzye** → 申万一级 demean → log(流通市值) 残差分位；高Δ优先；**明确非**北向 hk_hold、非 ADV 分位、非估值/OCF/相对强弱/四臂/解禁/份额流/调仓/ETF-core；禁词（动量/momentum/value/quality）**无命中** |
| 主信号 | ✅ `margin_delta_rzye_ind_mcap_resid`；主数据 `margin_detail_daily_2018plus`（rzye+available_at）；D1 仅 float_mktcap 协变量；**未**用 D2 moneyflow 主腿；**未**读 hk_hold |
| 再平衡 | ✅ 月频 `month_end_plus_first_last`；n_rebal=**35** |
| 行业硬顶 | ✅ 设计 ≤**28%**；单名 ≤**4%** |
| vs capacity_adv | ✅ Jaccard 均/max≈**0.315 / 0.400**；frac≥0.7=**0** |
| vs northbound_flow | ✅ Jaccard 均/max≈**0.378 / 0.667**；frac≥0.7=**0**（max&lt;0.7） |
| vs 十灭其余 | ✅ 全 frac≥0.7=**0**；最高 max≈0.43（indcap）/0.43（d1_val）；idx_rebal=0 |
| 同构硬闸 | ✅ **未触发**（≥0.7 ∧ 近等权）；机制差：全窗两融 ≠ hk_hold 主臂 ≠ ADV 分位选股 |
| G6 | ✅ proof `G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**1978.5 MB**（软标 ≤1GB **未达**）；与同厂叶（northbound≈2017 / capacity≈1994）同量级 → **软缺口，非硬拒** |
| Book-Smoke | ⚠️ New Bot/Eng 回传 **已灭**：**7.85% / 8.62%** @60万∧100万 vs C0 **−3.41 / −2.65pp**；MDD −13.02%/−14.18%；**any_pass=false** · **research_candidate=false** · **handoff=NO** → **WATCH / DONE_FAIL**；回执 `docs/v2/BOOK_SMOKE_G1G5_MARGIN_DELTA_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy / **勿再派烟**。非 Alpha 执行 |
| promotion | ✅ false；handoff=NO；no_gp；no Strategy；no main-book；no seal |

**硬闸**：未触发（stub / Σw 破 / who_pays 禁词主轴 / 600519·002371 正权 / 单名>0.04 / Jaccard≥0.7∧近等权 / G6 fail / 北向或 ADV 换皮证据 / D2 moneyflow 冒充主腿）。

---

## 2. ACCEPT 范围（研究级；烟后 WATCH）

- **研究级**辩论权重：全窗两融融资余额 **Δrzye**（PIT `available_at`）→ 申万一级 demean → log 流通市值残差 → top25 等权 + 行业≤28% + 单名≤4% + 硬排除巨头 + 压舱 510300；月频+首末日。  
- 相对十灭+容量+北向：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.667 vs northbound，仍 &lt;0.7 且 frac=0）；机制为**杠杆资金流**，非 hk_hold、非 ADV 分位、非估值/OCF/相对强弱换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；**不跑 Book-Smoke**；不把本 ACCEPT 当工厂/晋级/live 授权。  
- Book-Smoke **已灭** → 状态 **ACCEPT→WATCH / DONE_FAIL**；**勿再派烟**；不交 Strategy；勿升主书；handoff=NO；live=false。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT；烟后保持 WATCH）

1. peak_rss ≈**1978.5 MB** 软标 ≤1GB 未达 — 研究级可消费，记 **GAP**（与同厂叶一致）。  
2. 压舱日均 ≈**0.264** 略高于预注册 0.15–0.25 目标带（覆盖不足日抬升）— 仍 ≪ etf_core 0.70；记软关注，**不**硬拒。  
3. vs northbound max Jaccard≈**0.667** 接近 0.7 软关注带，但 frac≥0.7=0 且主轴全窗两融≠hk_hold → **不**触发硬闸。  
4. **Book-Smoke WATCH**：已灭 **7.85% / 8.62%**（vs C0 −3.41/−2.65pp）；两端 CAGR 未进 [12%,18%]；**handoff=NO** — **勿升主书** / 不交 Strategy / 勿再派烟。非 Alpha 执行。  
5. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
6. D2 moneyflow **未**作主腿（正确）；未当满样本。

---

## 4. who_pays 一行

国内两融/杠杆资金边际加仓与去杠杆压力下的错误定价对手盘：以个股融资余额 Δrzye（asof available_at）经申万一级行业 demean + 对数流通市值残差后的分位选股；高 Δ（融资净增）优先；主叙事=杠杆资金流；明确非北向持股、非 ADV 容量分位、非估值残差、非 OCF、非相对强弱、非四臂/解禁/份额流/调仓/ETF-core。

---

## 5. 机读

`output/alpha/AI_G1G5_MARGIN_DELTA_WEIGHT_ACCEPT_20261013.json`

`status=RESEARCH_ACCEPT`（权重硬闸仍成立）· Book-Smoke **WATCH / DONE_FAIL** · `any_pass=false` · `research_candidate=false` · `promotion_approved=false` · **handoff=NO** · **勿升主书** · **不交 Strategy** · **禁 GP** · **live=false** · 十灭+容量+北向 Jaccard 硬拒未触发 · 600519/002371=0 · 单名 max=0.032

---

## 6. Book-Smoke 标注（2026-10-13 ~02:21 ET）

- run_id `book_smoke_20261013_021225`；窗 X2；资金 60万∧100万；成本开；回执 `docs/v2/BOOK_SMOKE_G1G5_MARGIN_DELTA_X2_RECEIPT_ZH.md`。
- BOOK：**7.85% / −13.02%**（60万）、**8.62% / −14.18%**（100万）；相对 C0 ≈**−3.41 / −2.65pp**；CAGR 未进 [12%,18%]（MDD 两端 ≥−28% 过门，收益端不过）。
- **any_pass=false** → **不标研究备选**（`research_candidate=false`）→ **WATCH / DONE_FAIL**。
- **叶锁**：`promotion_approved=false` · **handoff=NO** · **live=false** · **勿升主书** · **不交 Strategy** · **禁 GP** · **勿再派烟** · **不密封** · **不下单**。
- 权重包研究级 ACCEPT（硬闸/正交）**保持**；烟灭仅改 Book-Smoke 状态，不推翻盘面核验。
- **禁止**：GP；升主书 live；交 Strategy 实盘；密封；把 RESEARCH_ACCEPT / paper 路径当工厂或 live 授权。
