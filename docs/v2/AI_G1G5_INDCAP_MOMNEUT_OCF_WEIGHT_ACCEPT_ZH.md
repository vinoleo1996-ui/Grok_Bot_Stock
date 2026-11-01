# Alpha 裁决 · AI G1G5 行业硬顶+动量暴露中性·OCF兑现 日更权重包

**日期**：2026-10-13 · America/New_York  
**包**：`output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`  
**meta**：`…105739.parquet.meta.json` / `g1g5_indcap_momneut_ocf_run_meta_20261013_105739.json`  
**AI 回执**：`docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_INDCAP_MOMNEUT_OCF_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级·行业硬顶+动量暴露中性·OCF兑现）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy**

对照七败包（禁同构）：  
- expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
- friction/nontextbook：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- lowturn：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- etf_core：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`  
- friction_cost：`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`  
- idx_rebal：`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **34068** 行 / **668** sessions / **51** 标的（50 个股 + `510300.SH` 名位） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false` |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN |
| 个股 / 压舱 | ✅ 日均个股 **1.0** / 压舱 **0.0**（`510300.SH` 行在、权重恒 0；覆盖满则无需压舱余量——诚实，非 stub） |
| 活跃个股数 | ✅ 日活 **17–20**（设计 top20；行业顶约束后可 <20） |
| 单票 / 分散 | ✅ 个股 max≈**0.103**；再平衡日 near_ew≈**34%**；mean CV≈**0.18**（mom 走廊倾斜后非纯等权） |
| ETF 腿 | ✅ 非压舱行业/宽基 ETF **无**；主仓个股；**非** etf_core 0.70 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_indcap_momneut_ocf_v1` |
| `who_pays_zh` | ✅ 与预注册一致：OCF/利润 PIT 兑现落差对手盘 + 行业硬顶 + 超额暴露走廊中性；**无** momentum/value/quality 英文主线 token；**无**「动量/价值/质量」作肯定主轴（仅排除句与中性化约束）；**无** CB/金主 |
| 再平衡 | ✅ **月频** `month_end_plus_first`；n_rebal=**35**；间隔中位 ≈**31** 交易日；**非**事件调仓 / **非**半月摩擦 / **非**季末粘性 |
| 主信号 | ✅ 脚本 `ocf_to_profit` PIT 截面排序；**非** excess_vs_510300 选股；动量仅 `neutralize_mom_exposure` 篮内倾斜 |
| 行业硬顶 | ✅ 预注册/脚本 ≤**28%**；run_meta HHI 均/max=**0.114 / 0.148**（告警阈 0.18；告警率 0%） |
| 动量暴露 | ✅ after 均值 ≈**+0.02pp**；\|·\| 均值 ≈**1.59pp**（走廊 1.5pp；略超已记，非硬拒） |
| vs expand | ✅ Jaccard 均/max≈**0.250 / 0.429**（全 35 再平衡日重算；AI 样例月均 0.233/0.333）；frac≥0.7=**0** |
| vs nontextbook | ✅ Jaccard 均/max≈**0.249 / 0.379** |
| vs lowturn | ✅ Jaccard 均/max≈**0.240 / 0.348** |
| vs resid_etf | ✅ Jaccard 均/max≈**0.247 / 0.357** |
| vs etf_core | ✅ Jaccard 均/max≈**0.113 / 0.222**；结构正交（个股主仓 vs ETF-core 0.70） |
| vs friction_cost | ✅ Jaccard 均/max≈**0.232 / 0.333** |
| vs idx_rebal | ✅ Jaccard 均/max=**0.0 / 0.0** |
| 动量同构硬闸 | ✅ **未触发**（Jaccard≥0.7 ∧ 等权换皮）；主轴诚实为 OCF，momneut≠动量叶 |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.00903**（月频；33 非零再平衡日） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**1967.5 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| Book-Smoke | ⚠️ New Bot/Beta 回传 **已灭**：**8.61% / 8.10%** @60万∧100万 vs C0 **−2.66 / −3.17pp**；MDD −14.60%/−15.98%；**any_pass=false** · **handoff=NO** → **WATCH**；回执 `docs/v2/BOOK_SMOKE_G1G5_INDCAP_MOMNEUT_OCF_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy。非 Alpha 执行 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true` |

**硬闸**：未触发（stub / sum 破 / who_pays 禁词作主轴 / Jaccard≥0.7∧等权同构 / G6 fail / PIT 前推证据 / 动量主线换皮）。

---

## 2. ACCEPT 范围

- **研究级**辩论权重：OCF/利润 PIT 兑现排序 → 申万一级单行业硬顶贪婪 top20 → 相对 510300 的 20d 超额暴露走廊中性化倾斜；月频+首日；满覆盖时压舱权重可为 0。  
- 相对七败包：活跃个股 Jaccard 均 ≪0.7（最高 max≈0.43 vs expand）；机制为现金流兑现+行业顶+暴露中性，**非**截面动量主轴、非四臂/解禁份额/ETF0.70/调仓事件换皮。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；不把本 ACCEPT 当工厂/晋级授权。Book-Smoke 待 New Bot 派测。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT）

1. peak_rss ≈**1967.5 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口。  
2. **Book-Smoke WATCH**：已灭 **8.61% / 8.10%**（vs C0 −2.66/−3.17pp）；欠门锁 12% 约 3.4–3.9pp；**handoff=NO** — **勿升主书** / 不交 Strategy。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. 压舱权重全日 **0**（名位保留）— 属满覆盖诚实画像，非 stub；与「余量→510300」设计兼容。  
5. mom 暴露 \|after\| 均 ≈1.59pp 略超 1.5pp 走廊 — 回执已记；观察，非硬拒。  
6. vs expand Jaccard 均≈0.25（软关注带）但主轴/who_pays/near_ew 证伪「动量换皮」→ **不**触发 HARD_BAN_MOMENTUM_ISOMORPH。  
7. AI 回执样例月 Jaccard 与 Alpha 全再平衡日重算略异（方法差）— 以 Alpha 盘面重算为准；结论同向。

---

## 4. who_pays 一行

经营现金流相对净利润的兑现落差（OCF/利润 PIT）在中大盘液态宇宙内被错误定价的对手盘，支付本叶相对 510300 的持有窗；另受申万一级单行业硬顶与相对 510300 的 20 日超额强度暴露走廊中性化约束；明确排除截面相对强弱排序主轴、教科书 EP/BM 估值主轴、残差×份额流、ETF-core overlay、四臂摩擦与指数调仓流换皮。

---

## 5. 机读

`output/alpha/AI_G1G5_INDCAP_MOMNEUT_OCF_WEIGHT_VERIFY_STATS_20261013.json`

`promotion_approved=false` · Book-Smoke **WATCH** · **勿升主书** · **不交 Strategy** · **禁 GP** · 七败对照 Jaccard≪0.7

---

## 6. 请 New Bot / Beta

主测本包：

`output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet`

若 Book-Smoke any_pass=false → 入 WATCH，不交 Strategy；保持 locks。

---

## 6. Book-Smoke 标注（2026-10-12 ~23:02 ET）

- run_id `book_smoke_20261013_110016`；窗 X2；资金 60万∧100万；成本开。
- BOOK：**8.61% / −14.60%**（60万）、**8.10% / −15.98%**（100万）；相对 C0 ≈−2.7/−3.2pp；CAGR 未进 [12%,18%]。
- **any_pass=false** → **不标研究备选**；保持 locks；**禁止再启 GP**；勿升主书；勿交 Strategy。
- 回执：`docs/v2/BOOK_SMOKE_G1G5_INDCAP_MOMNEUT_OCF_X2_RECEIPT_ZH.md`
