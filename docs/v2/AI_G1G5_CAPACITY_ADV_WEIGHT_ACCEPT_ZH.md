# Alpha 裁决 · AI G1G5 容量/ADV 可成交约束日更权重包

**日期**：2026-10-13 · America/New_York  
**包**：`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`  
**meta**：`…111219.parquet.meta.json` / `g1g5_capacity_adv_run_meta_20261013_111219.json`  
**AI 回执**：`docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级·容量/ADV 可成交约束）→ RESEARCH_CANDIDATE** · **非** FactorCandidate · **非** live 晋级  
**门锁**：`promotion_approved=false` · Book-Smoke **RESEARCH_CANDIDATE** · **handoff=NO** · **勿升主书** · **不交 Strategy 实盘权重** · **不下单** · **不密封** · **禁 GP**  
**纸面轨**：`promotion_path=paper_active` **CONFIRMED**（Leo Alpha chat 2026-10-12 ~23:32 ET；短包 `docs/v2/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_ZH.md` / `output/alpha/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_20261013.json`）；Strategy 纸面轨可继续；Alpha **不**移交 live 权重

对照九败包（禁同构）：  
- expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
- friction/nontextbook：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- lowturn：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- etf_core：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`  
- friction_cost：`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`  
- idx_rebal：`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`  
- indcap_momneut_ocf（WATCH）：`output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`  
- d1_val_resid（WATCH）：`output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **32732** 行 / **668** sessions / **49** 标的（与 New Bot 声称一致；盘面核验） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false` |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；`instrument`↔`instrument_id`（`601857.SH`↔`sh.601857`）可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **≈0.789** / 压舱 **≈0.211**（仅 `510300.SH`） |
| 活跃个股数 | ✅ 日活个股 **17–25**（中位 **22**；设计 top N=25 约束后） |
| 单票硬顶 | ✅ 个股单名 **max=0.04**（= NAME_CAP）；违规日=**0**；压舱单日最高观测 ≈0.32（余量归压舱，**非**个股破顶） |
| **硬排除 600519/002371** | ✅ **正权重行数=0**；两码在包内 **0 行**（连零权也无）— New Bot 声称 **成立** |
| ETF 腿 | ✅ 非压舱行业/宽基 ETF **无**；主仓个股；**非** etf_core 0.70 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_capacity_adv_v1` |
| `who_pays_zh` | ✅ 与预注册一致：D1 asof ADV（流通市值×换手）经申万一级行业 demean 流动性分位 + 单名权重/ADV 参与率双硬顶；**明确非**估值残差 / OCF / 截面相对强弱；**无** momentum/value/quality /「动量/价值/质量」主线禁词；**无** CB/金主 |
| 再平衡 | ✅ **月频** `month_end_plus_first_last`；n_rebal=**35**；**非**事件调仓 / **非**半月摩擦 / **非**季末粘性 |
| 主信号 | ✅ `adv_ind_demean_capacity_cap4_ind28_exclude_mega_fillgap`；容量∝√ADV 倾斜（near_ew≈**34%**，CV≈**0.10**）；**非**动量选股、**非**估值残差、**非** OCF |
| 行业硬顶 | ✅ 设计申万一级 ≤**28%**（AI 回执）；容量绑定 AUM=100万、参与率 k=2% |
| vs expand | ✅ Jaccard 均/max≈**0.282 / 0.481**（全 35 再平衡日）；frac≥0.7=**0** |
| vs nontextbook | ✅ Jaccard 均/max≈**0.265 / 0.406** |
| vs lowturn | ✅ Jaccard 均/max≈**0.204 / 0.324** |
| vs resid_etf | ✅ Jaccard 均/max≈**0.289 / 0.406** |
| vs etf_core | ✅ Jaccard 均/max≈**0.119 / 0.200**；结构正交（个股≈0.79 vs ETF-core 0.70） |
| vs friction_cost | ✅ Jaccard 均/max≈**0.271 / 0.364** |
| vs idx_rebal | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs indcap_momneut_ocf | ✅ Jaccard 均/max≈**0.194 / 0.364**；机制 OCF≠容量/ADV |
| vs d1_val_resid | ✅ Jaccard 均/max≈**0.343 / 0.556**；同 mid_large 池略高，但主轴/排除/单名顶正交 |
| 同构硬闸 | ✅ **未触发**（Jaccard≥0.7 ∧ EW clone）；near_ew≪0.9 且 max≪0.7 |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.0125**（月频） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**1994.3 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| Book-Smoke | ✅ New Bot/Beta 回传 **过门**：**13.82% / 12.23%** @60万∧100万 vs C0 **+2.56 / +0.97pp**；MDD −10.07%/−11.62%；**any_pass=true** · **both_aum_pass=true** · **research_candidate=true** · **handoff=NO** · **promotion=false**（live）→ **RESEARCH_CANDIDATE**；回执 `docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy 实盘权重 / 禁 GP；纸面轨已确认 `promotion_path=paper_active`（见晋级短包）。非 Alpha 执行 live |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true` |

**硬闸**：未触发（stub / sum 破 / who_pays 禁词作主轴 / 600519·002371 正权重 / 单名>0.04 / Jaccard≥0.7∧等权同构 / G6 fail / PIT 前推证据）。

---

## 2. ACCEPT 范围（研究级；烟前 PENDING）

- **研究级**辩论权重：D1 asof ADV 代理 → 申万一级行业 demean 流动性分位 → 贪婪 topN + 单名≤4% + ADV 参与率≤2%@AUM=100万 + 行业≤28% + 硬排除巨头缺口名 + 压舱 510300≈0.21；月频+首末日。  
- 相对九败包：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.56 vs d1_val_resid）；机制为**容量/冲击可成交**，**非**截面动量、非估值残差、非 OCF、非四臂/解禁份额/ETF0.70/调仓事件换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；**不跑 Book-Smoke**；不把本 ACCEPT 当工厂/晋级授权。  
- Book-Smoke **RESEARCH_CANDIDATE** → 过闸后由 New Bot 派 Beta 满窗烟；若 any_pass=false → 入 WATCH，不交 Strategy。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT）

1. peak_rss ≈**1994.3 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口（尖峰来自日权展开+九败对照）。  
2. **Book-Smoke RESEARCH_CANDIDATE**：已过门 **13.82% / 12.23%**（vs C0 +2.56/+0.97pp）；**handoff=NO** · **promotion=false**（live）— **勿升主书** / 不交 Strategy 实盘权重；纸面轨 `promotion_path=paper_active` 已确认（Leo Alpha chat）。非 Alpha 执行 live。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. vs d1_val_resid Jaccard 均≈0.34 / max≈0.56（软关注带）但主轴/硬排除/单名顶证伪「估值残差换皮」→ **不**触发硬闸。  
5. AI meta 样例月 Jaccard 与 Alpha 全再平衡日重算略异（方法差）— 以 Alpha 盘面重算为准；结论同向。

---

## 4. who_pays 一行

可成交容量约束下的流动性溢价/冲击成本错误定价对手盘：以 D1 asof ADV 代理经申万一级行业中性后的流动性分位选股；单名权重与 ADV 参与率双硬顶，压百万元端巨头成交/冲击缺口；明确非估值残差、非 OCF 兑现、非截面相对强弱主轴；明确非四臂摩擦/解禁/份额流/调仓流/ETF-core 直接持有。

---

## 5. 机读

`output/alpha/AI_G1G5_CAPACITY_ADV_WEIGHT_VERIFY_STATS_20261013.json`

`promotion_approved=false` · Book-Smoke **RESEARCH_CANDIDATE** · **勿升主书** · **不交 Strategy** · **禁 GP** · 九败对照 Jaccard≪0.7 · 600519/002371 正权重=0 · 单名 max=0.04

---

## 6. Book-Smoke 标注（2026-10-12 ~23:16 ET）

- run_id `book_smoke_20261013_111418`；窗 X2；资金 60万∧100万；成本开。
- BOOK：**13.82% / −10.07%**（60万）、**12.23% / −11.62%**（100万）；相对 C0 +2.56/+0.97pp；两端 CAGR∈[12%,18%] 且 MDD 好于 −28%。
- **any_pass=true** · **research_candidate=true** → 标研究备选；**handoff=NO** · **promotion_approved=false**。
- **禁止**：升主书；交 Strategy；启 GP；密封；扩 ACTIVE。**等 Leo 本聊天明示才可晋级。**
- 回执：`docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md`
