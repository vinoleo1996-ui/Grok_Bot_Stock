# Alpha 裁决 · AI G1G5 D1 估值残差 asof 日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/ai_factory/g1g5_d1_val_resid_daily_weights_20261013_110154.parquet`  
**meta**：`…110154.parquet.meta.json` / `g1g5_d1_val_resid_run_meta_20261013_110154.json`  
**AI 回执**：`docs/v2/AI_G1G5_D1_VAL_RESID_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_D1_VAL_RESID_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级·D1 估值残差 asof）→ WATCH** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy**

对照八败包（禁同构；含刚灭叶 A）：  
- expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
- friction/nontextbook：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- lowturn：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- etf_core：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`  
- friction_cost：`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`  
- idx_rebal：`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`  
- indcap_momneut_ocf（叶 A WATCH）：`output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **34068** 行 / **668** sessions / **51** 标的（与 New Bot 声称一致；盘面核验） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false` |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **0.80** / 压舱 **0.20**（仅 `510300.SH`；全日恒定） |
| 活跃个股数 | ✅ 日活 **20**（设计 top20 EW） |
| 单票 / 分散 | ✅ 个股单票恒 **0.04**；再平衡日 near_ew=**100%**；CV≈**0**（设计等权，非动量倾斜） |
| ETF 腿 | ✅ 非压舱行业/宽基 ETF **无**；主仓个股；**非** etf_core 0.70 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_d1_val_resid_v1` |
| `who_pays_zh` | ✅ 与预注册一致：D1 asof 估值倍数经行业+市值中性后的残差修正 + 20d 超额正交；**明确非裸 EP/BM/PE**；**无** momentum/value/quality /「动量/价值/质量」主线禁词；**无** CB/金主 |
| 再平衡 | ✅ **月频** `month_end_plus_first_last`；n_rebal=**35**；间隔中位 ≈**21** 交易日；**非**事件调仓 / **非**半月摩擦 / **非**季末粘性 |
| 主信号 | ✅ D1 `pe_ttm`→EP → SW L1 demean → 流通市值三分位 demean → 对 20d 相对 510300 超额 OLS 正交；**非**裸 EP 截面；**非**相对强弱选股 |
| 行业硬顶 | ✅ 设计 ≤**30%**；Alpha SW L1 PIT 重算再平衡日 max_ind_w=**0.20**（均≈0.13）；违规日=**0** |
| vs expand | ✅ Jaccard 均/max≈**0.272 / 0.481**（全 35 再平衡日）；frac≥0.7=**0** |
| vs nontextbook | ✅ Jaccard 均/max≈**0.253 / 0.379** |
| vs lowturn | ✅ Jaccard 均/max≈**0.225 / 0.300** |
| vs resid_etf | ✅ Jaccard 均/max≈**0.264 / 0.379** |
| vs etf_core | ✅ Jaccard 均/max≈**0.128 / 0.222**；结构正交（个股0.80 vs ETF-core 0.70） |
| vs friction_cost | ✅ Jaccard 均/max≈**0.243 / 0.379** |
| vs idx_rebal | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs 叶A indcap | ✅ Jaccard 均/max≈**0.303 / 0.481**；机制 OCF≠估值残差 |
| 价值/等权同构硬闸 | ✅ **未触发**（Jaccard≥0.7 ∧ EW clone）；虽为 EW top20，但 max≪0.7 且主轴为残差非裸价值/非动量 |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.00618**（月频；33 非零再平衡日） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**1940.6 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| Book-Smoke | ⚠️ New Bot/Beta 回传 **已灭**：**11.64% / 9.76%** @60万∧100万 vs C0 **+0.37 / −1.51pp**；MDD −14.88%/−16.71%；**any_pass=false** · **handoff=NO** → **WATCH**；回执 `docs/v2/BOOK_SMOKE_G1G5_D1_VAL_RESID_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy / **勿再派烟**。非 Alpha 执行 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true`；D1 ACCEPT_FULL ≠ 工厂/Strategy 授权 |

**硬闸**：未触发（stub / sum 破 / who_pays 禁词作主轴 / Jaccard≥0.7∧等权同构 / G6 fail / PIT 前推证据 / 裸价值换皮）。

---

## 2. ACCEPT 范围（研究级；烟后 WATCH）

- **研究级**辩论权重：D1 asof EP → 行业+市值中性残差 → 20d 超额正交 → 低估侧 top20 EW + 行业硬顶≤30% + 压舱 510300≈0.20；月频+首末日。  
- 相对八败包：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.48 vs expand / 叶A）；机制为估值残差纠偏，**非**截面动量、非四臂/解禁份额/ETF0.70/调仓事件、非叶A OCF 换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；不把本 ACCEPT / D1 ACCEPT_FULL 当工厂/晋级授权。  
- Book-Smoke **已灭** → 状态 **ACCEPT→WATCH**；**勿再派烟**。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT；烟后保持 WATCH）

1. peak_rss ≈**1940.6 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口。  
2. **Book-Smoke WATCH**：已灭 **11.64% / 9.76%**（vs C0 +0.37/−1.51pp）；60万距门锁下沿约 **0.36pp**；**handoff=NO** — **勿升主书** / 不交 Strategy / 勿再派烟。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. vs expand / 叶A Jaccard 均≈0.27–0.30（软关注带）但主轴/who_pays 证伪「裸价值或动量换皮」→ **不**触发硬闸。  
5. AI meta 样例月 Jaccard 与 Alpha 全再平衡日重算略异（方法差）— 以 Alpha 盘面重算为准；结论同向。  
6. SW L1 PIT 部分再平衡日有未映射名；已映射侧 max_ind≤0.20，硬顶未破。

---

## 4. who_pays 一行

错误定价纠偏：D1 asof 估值倍数经申万一级行业与流通市值中性后的残差修正；低估侧收敛由边际资金支付相对 510300 的持有窗；并对相对宽基 20 日超额收益暴露做正交化压低；明确非裸 EP/BM/PE 截面排序；明确非残差收益×份额流同构；明确非四臂摩擦/解禁/调仓流/ETF-core 直接持有。

---

## 5. 机读

`output/alpha/AI_G1G5_D1_VAL_RESID_WEIGHT_VERIFY_STATS_20261013.json`

`promotion_approved=false` · Book-Smoke **WATCH**（DONE_FAIL）· **勿升主书** · **不交 Strategy** · **禁 GP** · 八败对照 Jaccard≪0.7

---

## 6. Book-Smoke 标注（2026-10-12 ~23:06 ET）

- run_id `book_smoke_20261013_110353`；窗 X2；资金 60万∧100万；成本开。  
- BOOK：**11.64% / −14.88%**（60万）、**9.76% / −16.71%**（100万）；相对 C0 ≈+0.37/−1.51pp；CAGR 未进 [12%,18%]。  
- **any_pass=false** → **不标研究备选**；**ACCEPT→WATCH**；保持 locks；**禁止再启 GP**；勿升主书；勿交 Strategy；**勿再派烟**。  
- 回执：`docs/v2/BOOK_SMOKE_G1G5_D1_VAL_RESID_X2_RECEIPT_ZH.md`
