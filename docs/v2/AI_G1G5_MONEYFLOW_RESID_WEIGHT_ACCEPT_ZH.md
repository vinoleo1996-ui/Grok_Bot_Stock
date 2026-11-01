# Alpha 裁决 · AI G1G5 个股资金流残差叶（moneyflow_resid）

**日期**：2026-10-13 ~05:09 ET · America/New_York  
**包**：`output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet`  
**meta**：`output/ai_factory/g1g5_moneyflow_resid_run_meta_20261013_050716.json`  
**G6 proof**：`output/ai_factory/debate_ledger_g1g5_moneyflow_resid_20261013_050716_g6_proof.jsonl`  
**AI 回执**：`docs/v2/AI_G1G5_MONEYFLOW_RESID_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_MONEYFLOW_RESID_WHO_PAYS_PREREG_ZH.md`  
**verify（AI）**：`output/alpha/AI_G1G5_MONEYFLOW_RESID_WEIGHT_VERIFY_STATS_20261013_050716.json`  
**裁决**：**ACCEPT（研究级）→ WATCH** · Book-Smoke **WATCH / DONE_FAIL** · **非** FactorCandidate · **非** live 晋级  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy** · **不下单** · **不密封** · **禁 GP** · **live=false**

对照十二灭/WATCH + capacity_adv（paper_active）：  
- expand / nontextbook(friction_monthly) / lowturn / resid_etf / etf_core / friction_cost_redesign / idx_rebal_flow  
- indcap_momneut_ocf（WATCH）/ d1_val_resid（WATCH）/ northbound_flow（WATCH）/ margin_delta（已灭）/ accrual_quality（已灭）/ capacity_adv（paper_active）

---

## 1. 核验摘要（Alpha 盘面重算）

| 项 | 结果 |
|---|---|
| 规模 | ✅ **32732** 行 / **668** sessions / **49** 标的（与声称一致） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_forward_fill=false`；唯一组合指纹=**35**=再平衡次数（日更展开，非 10 日 stub） |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；`weight≡target_weight`；date≡session；`instrument`↔`instrument_id`（`601857.SH`↔`sh.601857`）可逆映射 ok |
| 日权重合计 | ✅ 恒 **1.0**（max\|Σw−1\|=0）；非负；无负权 |
| 个股 / 压舱 | ✅ 日均个股 **≈0.757** / 压舱 **≈0.243**（仅 `510300.SH`）；落在预注册 ≈0.15–0.25 软带；**≪** etf_core 0.70 |
| 活跃个股数 | ✅ 日活 **16–25**（均≈23.7；设计 topN=25） |
| 单票硬顶 | ✅ 个股单名 **max=0.032**（≤4%）；违规日=**0**；压舱单日最高观测≈0.488（余量归压舱，**非**个股破顶） |
| **硬排除 600519/002371** | ✅ 包内 **0 行**（正权=0） |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_moneyflow_resid_v1` |
| `universe_id` | ✅ `g1g5_mid_large_liquid_top50`；`universe_kind=mid_large_stock` |
| `who_pays_zh` | ✅ 与预注册一致：PIT Σ`net_mf_amount`（L≈20）/ADV → 申万一级 demean → log 流通市值残差；高残差优先；ADV **仅分母**；**明确非** ADV 分位选股 / 两融 Δrzye / 北向 hk_hold / 应计 / OCF / 估值残差 / 相对强弱 / 四臂 / 解禁 / 份额流 / 调仓 / ETF-core |
| 主信号 | ✅ `moneyflow_net_mf_over_adv_ind_mcap_resid`；主数据 D2 `moneyflow_stock_daily_pit`（ACCEPT_FULL）；D1 仅 `float_mktcap`+`turnover_rate` 作 ADV 分母与市值协变量；脚本 `available_at.normalize()≤session`；**未**读 margin/hk_hold/balancesheet/ocf/pe |
| 再平衡 | ✅ 月频 `month_end_plus_first_last`；n_rebal=**35** |
| 行业硬顶 | ✅ 设计 ≤**28%**；单名 ≤**4%** |
| vs capacity_adv | ✅ Jaccard 均/max≈**0.316 / 0.471**；frac≥0.7=**0**（ADV 仅分母 ≠ ADV 分位选股） |
| vs margin_delta | ✅ Jaccard 均/max≈**0.223 / 0.371**；frac≥0.7=**0** |
| vs accrual_quality | ✅ Jaccard 均/max≈**0.172 / 0.351**；frac≥0.7=**0** |
| vs northbound_flow | ✅ Jaccard 均/max≈**0.238 / 0.406**；frac≥0.7=**0** |
| vs d1_val_resid | ✅ Jaccard 均/max≈**0.274 / 0.448**；frac≥0.7=**0** |
| vs indcap_momneut_ocf | ✅ Jaccard 均/max≈**0.297 / 0.467**；frac≥0.7=**0** |
| vs expand | ✅ Jaccard 均/max≈**0.355 / 0.571**；frac≥0.7=**0** |
| vs resid_etf | ✅ Jaccard 均/max≈**0.379 / 0.552**；frac≥0.7=**0** |
| vs 其余灭侧 | ✅ lowturn max≈0.364；friction_cost/nontextbook max=0.375；etf_core max≈0.194；idx_rebal=0；全 frac≥0.7=**0** |
| 同构硬闸 | ✅ **未触发**（≥0.7 ∧ 近等权）；全局 max Jaccard≈**0.571**（vs expand）≪0.7 |
| G6 | ✅ proof `G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2009.4 MB**（软标 ≤1GB / 目标 ≤1.5GB **未达**）；与同厂叶（margin≈1978 / accrual≈2079 / capacity≈1994）同量级 → **软缺口，非硬拒** |
| Book-Smoke | ⚠️ New Bot/Eng 回传 **已灭**：**9.75% / 9.70%** @60万∧100万 vs C0 **−1.52 / −1.57pp**；MDD −15.25%/−16.27%；**any_pass=false** · **both_aum_pass=false** · **research_candidate=false** · **handoff=NO** → **WATCH / DONE_FAIL**；回执 `docs/v2/BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy / **勿再派烟**。非 Alpha 执行 |
| promotion | ✅ false；handoff=NO；no_gp；no Strategy；no main-book；no seal；live=false |

**硬闸**：未触发（stub / Σw 破 / who_pays 禁词主轴 / 600519·002371 正权 / 单名>0.04 / Jaccard≥0.7∧近等权 / G6 fail / ADV 分位换皮 / 非 moneyflow 主腿 / PIT 前视证据）。

---

## 2. ACCEPT 范围（研究级；烟后 WATCH）

- **研究级**辩论权重：PIT Σ`net_mf_amount`（L≈20 自然日，`available_at≤session`）/ ADV → 申万一级 demean → log 流通市值 OLS 残差 → 高残差优先 top25 等权 + 行业≤28% + 单名≤4% + 硬排除巨头 + 压舱 510300≈0.24；月频+首末日。  
- 相对十二灭+容量：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.571 vs expand；vs capacity max≈0.471）；机制为**个股资金流残差（mf/ADV）**，非 ADV 流动性分位、非两融、非北向、非应计/OCF/估值、非相对强弱换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；**不跑 Book-Smoke**；不把本 ACCEPT 当工厂/晋级/live 授权。  
- Book-Smoke **已灭** → 状态 **ACCEPT→WATCH / DONE_FAIL**；**勿再派烟**；不交 Strategy；勿升主书；handoff=NO；live=false。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT；烟后保持 WATCH）

1. peak_rss ≈**2009.4 MB** 软标 ≤1GB（目标 ≤1.5GB）未达 — 研究级可消费，记 **GAP**（与同厂叶一致）。  
2. **Book-Smoke WATCH**：已灭 **9.75% / 9.70%**（vs C0 −1.52/−1.57pp）；两端 CAGR 未进 [12%,18%]；MDD 两端 ≥−28% 过门；**any_pass=false** · **both_aum_pass=false** · **handoff=NO** — **勿升主书** / 不交 Strategy / 勿再派烟。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. AI verify 样例月 Jaccard 与 Alpha 全 35 再平衡日重算略异（方法/对照包路径差；如 resid_etf max 0.50→0.55）— 以 Alpha 盘面重算为准；结论同向（全 frac≥0.7=0）。  
5. D2 moneyflow **已**作主腿（正确；依赖 D2 ACCEPT_FULL）；ADV **仅**分母。

---

## 4. who_pays 一行

忽视行业/市值中性后的个股净资金流入强度（相对 ADV）的对手盘：以 PIT `net_mf_amount` 约 L=20 累计除以 ADV（`float_mktcap×turnover/100` 仅分母），经申万一级 demean + 对数流通市值残差分位；高残差（相对净流入）优先；主叙事=个股资金流残差（moneyflow/ADV）；明确非 ADV 流动性分位选股、非两融、非北向、非应计/OCF/估值残差、非相对强弱/四臂/解禁/份额流/调仓/ETF-core。

---

## 5. 机读

`output/alpha/AI_G1G5_MONEYFLOW_RESID_WEIGHT_ACCEPT_20261013.json`

`status=RESEARCH_ACCEPT`（权重硬闸仍成立）· Book-Smoke **WATCH / DONE_FAIL** · `any_pass=false` · `research_candidate=false` · `promotion_approved=false` · **handoff=NO** · **勿升主书** · **不交 Strategy** · **禁 GP** · **live=false** · 十二灭+容量 Jaccard 硬拒未触发 · 600519/002371=0 · 单名 max=0.032 · peak_rss 软 GAP

---

## 6. Book-Smoke 标注（2026-10-13 ~05:12 ET）

- run_id `book_smoke_20261013_051054`；窗 X2；资金 60万∧100万；成本开；回执 `docs/v2/BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md`；摘要 `output/v3/book_smoke_g1g5_moneyflow_resid_x2/book_smoke_summary.json`。  
- BOOK：**9.75% / −15.25%**（60万）、**9.70% / −16.27%**（100万）；相对 C0 ≈**−1.52 / −1.57pp**；CAGR 未进 [12%,18%]（MDD 两端 ≥−28% 过门，收益端不过）。  
- **any_pass=false** · **both_aum_pass=false** → **不标研究备选**（`research_candidate=false`）→ **WATCH / DONE_FAIL**。  
- **叶锁**：`promotion_approved=false` · **handoff=NO** · **live=false** · **勿升主书** · **不交 Strategy** · **禁 GP** · **勿再派烟** · **不密封** · **不下单**。  
- 权重包研究级 ACCEPT（硬闸/正交）**保持**；烟灭仅改 Book-Smoke 状态，不推翻盘面核验。  
- **禁止**：GP；升主书 live；交 Strategy 实盘；密封；把 RESEARCH_ACCEPT / paper 路径当工厂或 live 授权；Alpha 自跑/再派烟。
