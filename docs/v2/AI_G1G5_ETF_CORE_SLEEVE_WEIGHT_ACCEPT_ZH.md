# Alpha 裁决 · AI G1G5 ETF-core+个股袖套 日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`  
**meta**：`g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet.meta.json` / `g1g5_etf_core_sleeve_run_meta_20261012_204928.json`  
**AI 回执**：`docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级辩论/ETF-core+个股袖套）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · 不交 Strategy · 不扩 ACTIVE · 不密封 · **不跑 GP**

对照（勿当主线）：  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- 摩擦 X2：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- 降换手：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **59452** 行 / **668** sessions / **89** 标的（ETF 曾现 39 + 个股宇宙 50） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；max==2026-10-09 |
| stub 禁 | ✅ sessions=668 ≫10；`stub_window=false`；`stub_forward_fill=false` |
| reaches_x2 | ✅ meta `reaches_x2_end=true`；末日持仓可消费 |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id（`XXXXXX.SH/SZ`↔`sh\|sz.XXXXXX`）可逆映射 ok |
| Eng validate | ⚠️ 本包未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN；日活约 **8–14**（均≈12.9） |
| ETF-core / 袖套 | ✅ 日均 ETF-core **0.70** / 个股袖套 **0.30**（按 51/15 等 ETF 代码形态分类；全日区间稳定）；**非** 100% 股票满仓 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_etf_core_sleeve_v1` |
| `who_pays_zh` | ✅ 行业 ETF 创设/赎回份额流对手盘 + 流入行业流动性承接对手盘；**无**「动量/momentum/价值/value/quality」主支付方 token；**无** CB/金主作主线 |
| vs resid_etf | ✅ 结构正交：Jaccard 均≈**0.178**（中位 0.172；最大≈0.308≪0.7）；Spearman 均≈**0.130**（中位 0.112） |
| vs 摩擦 111316 | ✅ Jaccard 均≈**0.229**（中位 0.259）；Spearman 均≈**0.208** |
| vs lowturn 112301 | ✅ Jaccard 均≈**0.123**（中位 0.097）；Spearman 均≈**0.040** |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.0291**（月频再平衡量级） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2081.2 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| 数据依赖 | ✅ ETF 份额流 PIT + D1 `turnover_rate` asof；**非** D2 moneyflow 满样本依赖；D1 ACCEPT_FULL **仅**研究 asof，非晋级授权 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true`；`no_v29_gp=true` |
| 再平衡 | ✅ 月末+首日 **35** 次；ETF-core 0.70（含 510300 压舱）+ 袖套 0.30 |

## 2. ACCEPT 范围

- **研究级**辩论/评级权重上下文：液态行业 ETF-core（份额流 PIT）+ 有限个股流动性承接袖套（D1 换手 asof）。  
- 相对已败四包（expand / nontextbook / lowturn / resid_etf）：主仓为 **ETF 工具本身**，非 100% 股票满仓；袖套用换手承接而非残差×份额交互 / 教科书相对强弱。  
- **不做**：FactorCandidate 硬闸；密封；Strategy 交接；扩 ACTIVE；Alpha **不跑 GP / v29+**；不把 D1 ACCEPT 当工厂/晋级授权。

## 3. 缺口 / 标注（不阻断）

1. peak_rss ≈**2081 MB** 软目标 ≤1.5GB 未达（D1 估值 asof 过滤读主导）— 研究级可消费，记缺口。  
2. Book-Smoke @60万∧100万 vs 510300：New Bot 回传 **已灭**（≈**8.46% / 9.43%**，未进门锁）→ **WATCH**；确认本 ACCEPT 仅研究观察，**勿升主书** / 不交 Strategy / 不扩 ACTIVE。非 Alpha 执行。  
3. 袖套宇宙仍为 mid_large **top50** 子集（`g1g5_etf_core_sleeve_mid_large_v1`）；待 Data D3 成员交叉审计不阻断本 ACCEPT。  
4. 仍无双读 ICIR / 冲击两档 — 非 evolve 候选，符合 meta。  
5. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验；若 Eng 后补 validate，以本 ACCEPT 盘面数字为准对照。  
6. D2 moneyflow **未** ACCEPT — 本包不依赖其满样本；后续若改用 moneyflow 须另过闸。

## 4. who_pays 一行

行业 ETF 创设/赎回份额流对手盘支付液态 ETF-core 相对 510300 压舱的配置差 + 流入行业内中大盘个股的流动性承接/冲击吸收对手盘支付有限袖套；明确排除教科书相对强弱/估值排序主线；明确非 100% 股票满仓四包同构。

## 5. 机读

`output/alpha/AI_G1G5_ETF_CORE_SLEEVE_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false`
