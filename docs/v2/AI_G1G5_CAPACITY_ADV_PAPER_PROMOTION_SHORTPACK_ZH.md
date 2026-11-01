# 晋级短包 · 容量叶 capacity_adv · **纸面轨（paper_active · CONFIRMED）**

**日期**：2026-10-12 ~23:20 ET（America/New_York）起草 · **确认** 2026-10-12 ~23:32 ET  
**mechanism**：`g1g5_ashare_capacity_adv_v1`  
**weights**：`output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet`  
**ACCEPT**：`docs/v2/AI_G1G5_CAPACITY_ADV_WEIGHT_ACCEPT_ZH.md`  
**Book-Smoke**：`docs/v2/BOOK_SMOKE_G1G5_CAPACITY_ADV_X2_RECEIPT_ZH.md` · run_id `book_smoke_20261013_111418`  
**who_pays**：`docs/v2/AI_G1G5_CAPACITY_ADV_WHO_PAYS_PREREG_ZH.md`  
**机读 stub**：`output/alpha/AI_G1G5_CAPACITY_ADV_PAPER_PROMOTION_SHORTPACK_20261013.json`

| 字段 | 值 |
|---|---|
| **stamp_status** | **PAPER_ACTIVE_CONFIRMED** |
| **promotion_path** | `paper_active`（**CONFIRMED**；Leo Alpha 聊天 2026-10-12 ~23:32 ET） |
| **live_handoff** | **NO** |
| **strategy_live_orders** | **false** |
| **promotion_approved**（live） | **false** |
| **strategy_promotion_approved** | **false** |
| **research_candidate** | **true** |
| **any_pass** | **true** |
| **both_aum_pass** | **true** |
| **禁 GP** | **true** |
| **勿升主书 / 不交 Strategy / 不下单** | **true** |
| **confirmed_at** | `2026-10-12T23:32:33-04:00`（~23:32 ET） |
| **confirmed_by** | Leo (Alpha chat) |
| **授权边界** | Leo 已在 Alpha 聊天明示确认 paper_active；live handoff 仍 NO；Strategy 纸面轨可继续（既有纸面授权）；**不**交 Strategy 实盘权重 |

---

## 1. 机制摘要

D1 asof **ADV 代理**（流通市值×换手）经申万一级行业 **demean** 后的**流动性分位**选股；贪婪 topN≈25 后按 ∝√ADV 容量倾斜；**单名权重 ≤4%** + **ADV 参与率 k=2%@AUM=100万** 双硬顶；行业硬顶 ≤28%；硬排除巨头缺口名 `600519`/`002371`；余量归 **510300 压舱**（日均个股≈0.79 / 压舱≈0.21）；月频 `month_end_plus_first_last`（n_rebal=35）。主轴是**可成交容量/冲击约束**，不是估值残差、不是 OCF、不是截面动量。

---

## 2. who_pays 一行

可成交容量约束下的流动性溢价/冲击成本错误定价对手盘：以 D1 asof ADV 代理经申万一级行业中性后的流动性分位选股；单名权重与 ADV 参与率双硬顶，压百万元端巨头成交/冲击缺口；明确非估值残差、非 OCF 兑现、非截面相对强弱主轴；明确非四臂摩擦/解禁/份额流/调仓流/ETF-core 直接持有。

---

## 3. 正交 vs 十灭（九败 + 北向 WATCH）

活跃个股集 Jaccard（Alpha 全 35 再平衡日；`AI_G1G5_CAPACITY_ADV_WEIGHT_VERIFY_STATS_20261013.json`）：

| 对照（状态） | Jaccard 均 | max | frac≥0.7 |
|---|---:|---:|---:|
| expand（灭） | 0.282 | 0.481 | 0 |
| nontextbook（灭） | 0.265 | 0.406 | 0 |
| lowturn（灭） | 0.204 | 0.324 | 0 |
| resid_etf（灭） | 0.289 | 0.406 | 0 |
| etf_core（灭） | 0.119 | 0.200 | 0 |
| friction_cost（灭） | 0.271 | 0.364 | 0 |
| idx_rebal（灭） | 0.000 | 0.000 | 0 |
| indcap_momneut_ocf（WATCH） | 0.194 | 0.364 | 0 |
| d1_val_resid（WATCH） | 0.343 | 0.556 | 0 |
| northbound_flow（WATCH） | ≈0.273 | ≈0.452 | 0 |

同构硬闸（Jaccard≥0.7 ∧ EW clone）：**未触发**。near_ew≈34%（√ADV 倾斜，非纯 EW）。

---

## 4. 容量硬顶核验

| 项 | 结果 |
|---|---|
| `600519` / `002371` 正权重 | **0**（包内 0 行） |
| 个股单名 max | **0.04**（= NAME_CAP；违规日=0） |
| ADV 参与率 | k=**2%** @AUM 绑定 **100万**；不满足缩权→压舱 |
| 行业顶 | 申万一级设计 ≤**28%** |
| 压舱 | 仅 `510300.SH`；日均 ≈0.21（容量缩权日可至 ≈0.32） |
| stub | `stub_window=false` · `stub_forward_fill=false` |
| G6 | **pass**（as_of 过滤挡前视） |
| 规模 | 32732 行 / 668 sessions / 49 标；2024-01-02→2026-10-09 |

---

## 5. Book-Smoke 数字表（X2 满窗；成本开）

窗：`2024-06-03→2026-10-09` · 对照 C0=纯 510300。

| AUM | BOOK CAGR | BOOK MDD | vs C0 ΔCAGR | 过门 |
|---|---:|---:|---:|---|
| **60万** | **13.82%** (0.1382) | **−10.07%** | **+2.56 pp** | ✅ CAGR∈[12%,18%] ∧ MDD≥−28% |
| **100万** | **12.23%** (0.1223) | **−11.62%** | **+0.97 pp** | ✅ 同上 |

| 旗标 | 值 |
|---|---|
| any_pass | **true** |
| both_aum_pass | **true** |
| research_candidate | **true** |
| handoff | **NO** |
| promotion_approved | **false** |
| sealed_claim | **false** |

来源：`output/v3/book_smoke_g1g5_capacity_adv_x2/book_smoke_summary.json`（四舍五入与回执一致：13.82%/−10.07%；12.23%/−11.62%）。

---

## 6. 失败条件（可证伪 → 撤 paper / 回 WATCH）

1. **容量顶破**：任一日个股单名权重 >0.04+ε，或行业名义 >0.28+ε。  
2. **巨头漏入**：`600519` / `002371` 出现正权重。  
3. **同构**：vs 十灭任一 Jaccard≥0.7 **且** EW clone / 叙事退化为动量·估值残差·OCF·四臂·调仓·份额流。  
4. **烟门回吐**：复跑 Book-Smoke @60万∧100万 any_pass→false，或相对 C0 同向转负。  
5. **stub**：日历未达窗末却 stub 前推 / `stub_forward_fill=true`。  
6. **G6 fail**：as_of 过滤失效或前视证据。  
7. **权重合计破**：日 Σw 显著偏离 1 或出现负权/NaN。  
8. **越权**：未获 Leo Alpha 明示却宣称 live / Strategy handoff / 升主书 / 启 GP。

---

## 7. 与十灭差异（一句话表）

| 包 | 一句话差异 |
|---|---|
| expand | 本叶禁截面超额排序；主轴 ADV 流动性分位≠动量选股 |
| nontextbook / lowturn | 无四臂制度摩擦；信号仅 ADV/换手流动性 |
| resid_etf | 禁残差×份额流 |
| etf_core | 主仓个股≈0.79，非 ETF0.70 overlay |
| friction_cost | 容量为硬约束非解禁/份额流主臂 |
| idx_rebal | 禁 CSI 调样事件窗 |
| indcap_momneut_ocf | 禁 OCF / 动量暴露作选股 |
| d1_val_resid | 禁估值残差/裸 EP；且硬排除叶B 巨头未成交缺口 |
| northbound | 禁北向持股变化主轴；机制=容量可成交≠外资流 |

---

## 8. 门锁（本短包）

- `promotion_path=paper_active`：**CONFIRMED**（**PAPER_ACTIVE_CONFIRMED**；Leo Alpha chat ~23:32 ET）  
- `live_handoff=NO` · `strategy_live_orders=false`  
- `promotion_approved=false`（live）· `strategy_promotion_approved=false`  
- **禁 GP** · **勿当实盘授权** · **勿升主书** · **不交 Strategy 实盘权重** · **不下单** · **不密封**  
- Strategy **纸面轨**可在 New Bot/Leo 既有纸面授权下继续；Alpha **不**移交 live 权重  
- 本短包 **不**翻转任何 live 晋级旗标

---

## 9. 引用

- verify JSON：`output/alpha/AI_G1G5_CAPACITY_ADV_WEIGHT_VERIFY_STATS_20261013.json`  
- smoke summary：`output/v3/book_smoke_g1g5_capacity_adv_x2/book_smoke_summary.json`  
- Mandate 门锁（研究对照）：净成本 CAGR∈[12%,18%] · MDD 不差于 −28%（`docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md`，本短包未改 Mandate）
