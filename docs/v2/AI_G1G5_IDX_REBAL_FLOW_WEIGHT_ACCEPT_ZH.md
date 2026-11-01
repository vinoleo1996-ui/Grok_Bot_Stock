# Alpha 裁决 · AI G1G5 指数调仓迁移流 日更权重包

**日期**：2026-10-12 · America/New_York  
**包**：`output/ai_factory/g1g5_idx_rebal_flow_daily_weights_20261012_215737.parquet`  
**meta**：`…215737.parquet.meta.json` / `g1g5_idx_rebal_flow_run_meta_20261012_215737.json`  
**AI 回执**：`docs/v2/AI_G1G5_IDX_REBAL_FLOW_WEIGHT_RECEIPT_ZH.md`  
**who_pays 预注册**：`docs/v2/AI_G1G5_IDX_REBAL_FLOW_WHO_PAYS_PREREG_ZH.md`  
**裁决**：**ACCEPT（研究级·指数调仓迁移流）** · **非** FactorCandidate  
**门锁**：`promotion_approved=false` · 不下单 · **不交 Strategy** · 不扩 ACTIVE · 不密封 · **不跑 GP** · **勿升主书** · Book-Smoke **WATCH**（已灭 · handoff=NO）

对照六败包（禁同构）：  
- expand：`output/intel/g1g5_expand_daily_weights_20261012_111354.parquet`  
- friction/nontextbook：`output/intel/g1g5_nontextbook_daily_weights_20261012_111316.parquet`  
- lowturn：`output/intel/g1g5_lowturn_daily_weights_20261012_112301.parquet`  
- resid_etf：`output/ai_factory/g1g5_resid_etf_daily_weights_20261013_002418.parquet`  
- etf_core：`output/ai_factory/g1g5_etf_core_sleeve_daily_weights_20261012_204928.parquet`  
- friction_cost：`output/ai_factory/g1g5_friction_cost_redesign_daily_weights_20261012_214334.parquet`

---

## 1. 核验摘要

| 项 | 结果 |
|---|---|
| 规模 | ✅ **3243** 行 / **668** sessions / **121** 标的（稀疏正权重） |
| 日期跨度 | ✅ **2024-01-02 → 2026-10-09**；`reaches_x2_end=true` |
| stub 禁 | ✅ `stub_window=false`；`stub_forward_fill=false` |
| 列契约 | ✅ AI `date,instrument,target_weight` + 权威 `session,instrument_id,weight`；date≡session；weight≡target；instrument↔instrument_id 可逆映射 ok |
| Eng validate | ⚠️ 未见独立 Eng validate 回执；列契约与日权重合计由 **Alpha 盘面核验**通过 |
| 日权重合计 | ✅ 恒 **1.0**；非负；无 NaN |
| 覆盖结构 | ✅ 个股活跃日 **103/668 ≈15.4%**；窗间 **565** 日纯压舱（诚实事件稀，**非** stub） |
| 活跃日个股/压舱 | ✅ 恒 **0.70 / 0.30**（N=25×0.028 + `510300.SH`）；全日均压舱/个股 ≈**0.892 / 0.108** |
| 单票 | ✅ 个股 max=**0.028**（设计等权）；活跃日 near_ew=1（本叶写死 topN EW，**非**换皮判据） |
| ETF 腿 | ✅ 非压舱腿 **无** 行业/宽基 ETF；仅 `510300.SH` 压舱；**非** etf_core 0.70 行业 ETF 主仓 |
| `mechanism_tag` | ✅ 行级唯一 · `g1g5_ashare_idx_rebal_flow_v1` |
| `who_pays_zh` | ✅ 被动指数调入强制再平衡买卖需求；**无**「动量/momentum/价值/value/quality」主线 token；**无** CB/金主；否定句「非估值/质量」可保留 |
| 再平衡 | ✅ **事件驱动** CSI300/500 `event=in`；K=10；约 **5** 次审查窗；n_change=**11**；**非**月频四臂 / **非**半月摩擦 / **非**季末粘性 |
| vs expand | ✅ Jaccard 均/max=**0.0 / 0.0**（103 活跃日） |
| vs friction 月频 | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs lowturn | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs resid_etf | ✅ Jaccard 均/max=**0.0 / 0.0** |
| vs etf_core | ✅ Jaccard 均/max=**0.0 / 0.0**；结构正交（个股调入篮 vs ETF-core 0.70） |
| vs friction_cost | ✅ Jaccard 均/max=**0.0 / 0.0**；信号正交（调入事件 vs 解禁+份额流） |
| 换手 | ✅ 日均单向 mean_one_way ≈**0.0105**（事件稀；10/667 非零） |
| G6 | ✅ run_meta `g6_proof.G6=pass`（as_of 过滤挡前视） |
| peak_rss | ⚠️ ≈**2011.5 MB**（软目标 ≤1.5GB **未达**）；研究级缺口，**非**硬拒 |
| Book-Smoke | ⚠️ New Bot 回传 **已灭**：**9.97% / 10.04%** @60万∧100万 vs C0 **−1.29 / −1.23pp**；MDD −18.43%/−19.07%；**any_pass=false** · **handoff=NO** → **WATCH**；回执 `docs/v2/BOOK_SMOKE_G1G5_IDX_REBAL_FLOW_X2_RECEIPT_ZH.md`；**勿升主书** / 不交 Strategy / 不扩 ACTIVE。非 Alpha 执行 |
| promotion | ✅ false；`not_hard_gates_candidate=true`；`no_strategy_submit=true`；`no_gp=true` |

**硬闸**：未触发（stub / sum 破 / who_pays 禁词 / Jaccard≥0.7∧同构叙事 / G6 fail / PIT 前推证据）。

---

## 2. ACCEPT 范围

- **研究级**辩论权重：CSI300/CSI500 调入公告 PIT → 生效+K=10 持有窗；top25 等权个股 0.70 + 510300 压舱 0.30；窗间诚实纯压舱。  
- 相对六败包：活跃个股 Jaccard **全 0**；机制为指数调样强制流，非动量/四臂/解禁份额/ETF0.70/半月摩擦再设计。  
- **不做**：FactorCandidate；密封；Strategy 交接；扩 ACTIVE；升主书；Alpha **不跑 GP**；不把本 ACCEPT 当工厂/晋级授权。Book-Smoke 已由 New Bot 代跑并灭 → 仅研究观察。

---

## 3. 缺口 / 标注（不阻断研究级 ACCEPT）

1. peak_rss ≈**2011.5 MB** 软目标 ≤1.5GB 未达 — 研究级可消费，记缺口。  
2. **Book-Smoke WATCH**：已灭 **9.97% / 10.04%**（vs C0 −1.29/−1.23pp）；欠门锁 12% 约 2.0pp；**handoff=NO**；**七包满窗均败** — **勿升主书** / 不交 Strategy。非 Alpha 执行。  
3. 未见独立 Eng validate 回执 — 列契约由 Alpha 盘面核验。  
4. 稀疏覆盖（活跃 ≈15.4%）属事件叶诚实画像，非 stub；满窗烟雾与连续持仓叶不可直接比。  
5. D2 moneyflow **未** ACCEPT — 本包不依赖其满样本。  
6. PIT 细检（逐条 available_at→下一开盘）未做独立重放 — 依 stub_forward_fill=false + G6 + 预注册口径；若后续发现前移公告则改 REJECT。

---

## 4. who_pays 一行

CSI300/CSI500 成分调入公告后、生效日前后，被动指数跟踪与量化对标的强制再平衡买卖需求支付相对 510300 的持有窗；本叶做多公告已到的调入个股篮；明确非截面动量/估值·质量主轴、非解禁·席位·份额流同构、非 ETF-core 0.70、非摩擦四臂换皮。

---

## 5. 机读

`output/alpha/AI_G1G5_IDX_REBAL_FLOW_WEIGHT_VERIFY_STATS_20261012.json`

`promotion_approved=false` · Book-Smoke **WATCH** · **handoff=NO** · **勿升主书** · **不交 Strategy** · 七包均败

---

## 6. Book-Smoke 标注（2026-10-12 ~22:44 ET）

- run_id `book_smoke_20261012_224226`；窗 X2；资金 60万∧100万；成本开。
- BOOK：**9.97% / −18.43%**（60万）、**10.04% / −19.07%**（100万）；相对 C0 ≈−1.3pp；CAGR 未进 [12%,18%]。
- **any_pass=false** → **不标研究备选**；保持 locks；**禁止再启 GP**；勿代跑工厂。
- 回执：`docs/v2/BOOK_SMOKE_G1G5_IDX_REBAL_FLOW_X2_RECEIPT_ZH.md`
