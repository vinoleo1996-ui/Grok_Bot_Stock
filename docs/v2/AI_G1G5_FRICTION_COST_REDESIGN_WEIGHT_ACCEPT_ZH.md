# Alpha 裁决 · AI G1G5 摩擦降成本再设计 日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`  
**meta**：`…214334.parquet.meta.json` / `g1g5_friction_cost_redesign_run_meta_20261012_214334.json`  
**AI 回执**：`docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_FRICTION_COST_REDESIGN_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级辩论/摩擦降成本再设计）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · **不交 Strategy** · 不扩 ACTIVE · 不密封 · **不跑 GP** · **勿升主书** · Book-Smoke **handoff=NO**

对照（勿当主线 / 五败包）：  
- expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
- friction/nontextbook：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- lowturn：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- etf_core：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **34068** 行 / **668** sessions / **51** 标的 |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false` |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；日活恒 **21**（20 个股 + 510300） |
| 个股 / 压舱 | ✅ 日均个股 **0.85** / 压舱 **0.15**（仅 `510300.SH`）；ETF 腿日均 **0.15≪0.25**；**非** etf_core 0.70/0.30 |
| 单票硬顶 | ✅ 个股 max=**0.05**（L≤5%）；近等权 frac=**0.0**；mean CV≈**0.271**；样例日 w∈≈[0.016,0.05]，容量×得分倾斜 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_friction_cost_redesign_v1` |
| `who_pays_zh` | ✅ 解禁供给冲击残差对手盘 + 行业 ETF 份额流转→成分股配置对手盘；**无**「动量/momentum/价值/value/quality」主线 token；**无** CB/金主 |
| 再平衡 | ✅ **半月** `biweekly_step_10_plus_first_last`；n_rebal=**68**；间隔中位 **10** 交易日；**非**季末+进12/出28 |
| 臂权 | ✅ 有效 `etf=0.55` / `unlock=0.45`；**t1=disabled(0)**；**limit=disabled(0)** |
| vs expand | ✅ Jaccard 均≈**0.249**（max≈0.48）；Spearman 均≈**−0.489** |
| vs friction 111316 | ✅ Jaccard 均≈**0.447**（中位 0.429；max 偶达 1.0 但 near_ew=0 → **非**等权换皮）；Spearman 均≈**−0.335**；frac≥0.7≈**0.13** |
| vs lowturn 112301 | ✅ Jaccard 均≈**0.250**（中位 0.231；max≈0.67≪硬闸「≥0.7 且 EW」）；Spearman 均≈**−0.501**；frac≥0.7=**0** |
| vs resid_etf | ✅ Jaccard 均≈**0.335**；Spearman 均≈**−0.407** |
| vs etf_core | ✅ Jaccard 均≈**0.224**；结构正交（本叶主仓个股 0.85 vs 对侧 ETF-core 0.70） |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.046**（半月 cadence） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2033.3 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| 数据依赖 | ✅ D1 `float_mktcap`×`turnover_rate` asof + 解禁/份额流 PIT；**非** D2 moneyflow 满样本；D1 ACCEPT_FULL **仅**研究 asof |
| Book-Smoke | ⚠️ New Bot 回传 **已灭**：**6.03% / 6.74%** @60万∧100万 vs C0 **−5.23 / −4.53pp**；**handoff=NO** → **WATCH**；**勿升主书** / 不交 Strategy / 不扩 ACTIVE。非 Alpha 执行 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true` |

**硬闸八条**：全部未触发（stub/sum/lowturn 同参复刻/T+1·limit 臂/ETF 腿>0.25·0.70 结构/Jaccard≥0.7∧EW/who_pays 禁词/G6 fail）。

---

## 2. ACCEPT 范围

- **研究级**辩论权重上下文：慢制度两臂（份额流→成分股 + 解禁残差）+ D1 容量加权 + 宽基压舱 0.15；砍高换手臂；半月 cadence。  
- 相对五败包：非 lowturn 季末粘性复刻；非 friction 四臂等权 top20；非 etf_core 0.70 主仓；非 resid×份额同构；非 expand 动量主线。  
- **不做**：FactorCandidate 硬闸；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP / v29+**；不把 D1 ACCEPT / 本 ACCEPT 当工厂或晋级授权。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT）

1. peak_rss ≈**2033 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口。  
2. **Book-Smoke WATCH**：已灭 **6.03% / 6.74%**（vs C0 −5.23/−4.53pp）；**handoff=NO**；六窗满样本包均未过烟雾 — **勿升主书** / 不交 Strategy。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选。  
5. D2 moneyflow **未** ACCEPT — 本包不依赖其满样本。  
6. vs friction 活跃集 Jaccard 均≈0.45（部分日可达 1.0）但权重 **非等权**（near_ew=0、CV≈0.27）且 cadence/臂权/压舱结构不同 → 未触发「≥0.7∧EW」硬闸；记观察。

---

## 4. who_pays 一行

解禁公告窗供给冲击残差对手盘 + 行业 ETF 创设/赎回份额流转映射到成分股的配置对手盘，支付相对 510300 压舱的持有窗；执行侧以 D1 换手×流通市值 asof 做容量匹配并加单票硬顶压冲击；明确砍掉 T+1/涨跌停高换手臂；明确非季末+进12/出28；明确非 ETF-core 0.70 结构。

---

## 5. 机读

`output/alpha/AI_G1G5_FRICTION_COST_REDESIGN_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书**
