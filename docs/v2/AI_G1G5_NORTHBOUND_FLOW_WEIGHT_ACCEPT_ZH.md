# Alpha 裁决 · AI G1G5 北向持股变化流日更权重包

**日期**：2026-10-13 · America/New_York  
**包**：`output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet`  
**meta**：`…111252.parquet.meta.json` / `g1g5_northbound_flow_run_meta_20261013_111252.json`  
**AI 回执**：`docs/v2/AI_G1G5_NORTHBOUND_FLOW_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_NORTHBOUND_FLOW_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级·北向持股变化流）→ WATCH** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy**

对照九败包（禁同构；capacity_adv 已 RESEARCH_CANDIDATE，短裁当时未计入败包基线）：  
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
| 规模 | ✅ **34068** 行 / **668** sessions / **51** 标的（与 New Bot 声称一致；盘面核验） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false`（断档用两融补窗，非 stub 前推） |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id（`sh.600519` 风格）可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **≈0.767** / 压舱 **≈0.233**（仅 `510300.SH`；再平衡日压舱随 n_stock 波动，最高≈0.56） |
| 活跃个股数 | ✅ 设计 top20；日活 min/med/max=**11 / 20 / 20**（信号稀疏日允许 <20） |
| 单票 / 分散 | ✅ 个股单票恒 **0.04**（有仓时）；再平衡日 near_ew=**100%**；CV≈**0**（设计等权） |
| ETF 腿 | ✅ 非压舱行业/宽基 ETF **无**；主仓个股；**非** etf_core 0.70 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_northbound_flow_v1` |
| `who_pays_zh` | ✅ 与预注册一致：北向配置流（hk_hold Δratio 增持侧）+ 断档两融补窗；**明确非**相对强弱截面 / 估值残差 / OCF / 调仓事件 / 份额流×残差 / ETF-core；**无** momentum/value/quality /「动量/价值/质量」主线禁词；**无** CB/金主 |
| 再平衡 | ✅ **月频** `month_end_plus_first_last`；n_rebal=**35**；**非**事件调仓 / **非**半月摩擦 / **非**季末粘性 |
| 主信号 | ✅ hk_hold PIT `Δratio` 增持侧（密窗≈20 日 / 稀疏窗最近两观测）；陈旧 >45 日 → 两融 `Δrzye/lag` 补窗（`source=margin_fallback`，**18**/35）；moneyflow_hsgt **仅**市场北向净流入日志/门控，**不作**个股评分 |
| 行业硬顶 | ✅ 设计 ≤**30%**；臂日志 max_ind=**0.28**（均≈0.15）；Alpha SW L1 PIT 映射侧 max≈**0.24**（均≈0.14）；违规日=**0** |
| vs expand | ✅ Jaccard 均/max≈**0.207 / 0.379**；frac≥0.7=**0** |
| vs nontextbook | ✅ Jaccard 均/max≈**0.226 / 0.423** |
| vs lowturn | ✅ Jaccard 均/max≈**0.188 / 0.321** |
| vs resid_etf | ✅ Jaccard 均/max≈**0.207 / 0.379** |
| vs etf_core | ✅ Jaccard 均/max≈**0.092 / 0.185**；结构正交（个股主仓 vs ETF-core 0.70） |
| vs friction_cost | ✅ Jaccard 均/max≈**0.235 / 0.538**（max 最高对照，仍 ≪0.7） |
| vs idx_rebal | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs 叶A indcap | ✅ Jaccard 均/max≈**0.257 / 0.444**；机制 OCF≠北向流 |
| vs 叶B d1_val | ✅ Jaccard 均/max≈**0.247 / 0.333**；机制估值残差≠北向流 |
| 等权同构硬闸 | ✅ **未触发**（Jaccard≥0.7 ∧ EW clone）；虽为 EW top20，但 max≪0.7 且主轴为北向持股变化非动量/非裸价值 |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.0236**（月频；34 非零再平衡日） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2017.3 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| Book-Smoke | ⚠️ New Bot/Beta 回传 **已灭**：**11.08% / 10.95%** @60万∧100万 vs C0 **−0.19 / −0.32pp**；MDD −14.38%/−13.80%；**any_pass=false** · **handoff=NO** → **WATCH / DONE_FAIL**；回执 `docs/v2/BOOK_SMOKE_G1G5_NORTHBOUND_FLOW_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy。非 Alpha 执行 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true` |

**硬闸**：未触发（stub / sum 破 / who_pays 禁词作主轴 / Jaccard≥0.7∧等权同构 / G6 fail / PIT 前推证据 / 假 D2 moneyflow 全样本主轴冒充）。

---

## 2. ACCEPT 范围（研究级；烟前 PENDING）

- **研究级**辩论权重：北向 `hk_hold` PIT 持股占比变化（增持侧）→ top20 EW + 行业硬顶≤30% + 压舱 510300；hk_hold 断档/陈旧 >45 日以两融融资余额变化同族补窗；月频+首末日。  
- 相对九败包：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.54 vs friction_cost）；机制为北向配置流，**非**截面动量、非四臂/解禁份额/ETF0.70/调仓事件、非叶A OCF、非叶B 估值残差换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；**不跑 Book-Smoke**；不把本 ACCEPT 当工厂/晋级授权。  
- Book-Smoke **WATCH** → 过闸后由 New Bot 派 Beta 满窗烟；若 any_pass=false → 入 WATCH，不交 Strategy。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT）

1. peak_rss ≈**2017.3 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口（主因 margin 分块加载）。  
2. **Book-Smoke WATCH**：已灭 **11.08% / 10.95%**（vs C0 −0.19/−0.32pp）；**handoff=NO** — **勿升主书** / 不交 Strategy。容量叶仍 RESEARCH_CANDIDATE。非 Alpha 执行。  
3. **hk_hold 覆盖**：个股持股数据最晚 trade_date≈**2025-06-30**；其后及陈旧>45 日再平衡用两融 Δrzye 补窗（**18**/35）— who_pays 已诚实披露；**非** stub 前推；**非**把两融升格为独立主叶名。  
4. **moneyflow / D2**：`moneyflow_hsgt` 仅市场北向净流入日志/门控参考；D2 个股 moneyflow 仍非 Alpha ACCEPT — 本包**不**依赖其作主信号；若叙事被误读为 D2 全样本流，以 who_pays+臂 `source` 为准。  
5. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
6. SW L1 PIT 部分再平衡日有未映射名；臂日志/映射侧 max_ind 仍 ≤0.28/0.24，硬顶未破。  
7. AI WEIGHT_RECEIPT 样例月 Jaccard 与 Alpha 全再平衡日重算略异（方法差）— 以 Alpha 盘面重算为准；结论同向（均 ≪0.7）。  
8. capacity_adv 并行叶 ACCEPT 仍为 Book-Smoke PENDING — **未**纳入本轮败包对照。

---

## 4. who_pays 一行

北向配置流：沪深港通北向对个股的边际增持与持股占比上升由境外配置与被动跟踪资金支付相对510300的持有窗；本叶吃持股变化与流入的对手盘；hk_hold断档后再平衡日以两融融资余额变化作同族补窗；明确非相对强弱截面排序、非估值残差、非OCF、非调仓事件、非份额流乘残差、非ETF-core直接持有。

---

## 5. 机读

`output/alpha/AI_G1G5_NORTHBOUND_FLOW_WEIGHT_VERIFY_STATS_20261013.json`

`promotion_approved=false` · Book-Smoke **WATCH** · **勿升主书** · **不交 Strategy** · **禁 GP** · 九败对照 Jaccard≪0.7

---

## 6. 请 New Bot / Beta

主测本包：

`output/ai_factory/g1g5_northbound_flow_daily_weights_20261013_111252.parquet`

派 **Book-Smoke @60万∧100万 vs 510300**（X2 满窗）。Alpha **不**代跑。若 any_pass=false → 回写本回执为 ACCEPT→WATCH / DONE_FAIL，不交 Strategy。

---

## 6. Book-Smoke 标注（2026-10-12 ~23:18 ET）

- run_id `book_smoke_20261013_111630`；窗 X2；资金 60万∧100万；成本开。
- BOOK：**11.08% / −14.38%**（60万）、**10.95% / −13.80%**（100万）；相对 C0 ≈−0.2/−0.3pp；CAGR 未进 [12%,18%]。
- **any_pass=false** → **不标研究备选**；**handoff=NO**；勿升主书；不交 Strategy；禁 GP；勿再派烟。
- 容量叶仍 **RESEARCH_CANDIDATE**（与本叶分开）。
- 回执：`docs/v2/BOOK_SMOKE_G1G5_NORTHBOUND_FLOW_X2_RECEIPT_ZH.md`
