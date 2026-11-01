# 宽基 ETF 资金流 · 慢因子 / 卫星袖套一页方案（研究级）

- **日期**：2026-10-25 ≈04:40 ET · America/New_York  
- **作者**：QuantLab Strategy  
- **对象**：主 Agent / Leo（抄 AI / Alpha / Beta / Arch / Data）  
- **锁**：`live=false` · `promotion_approved=false` · `strategy_promotion_approved=false`  
- **禁**：改 FROZEN_CONFIG / 纸面 capadv·B4·S6；装跑纸面 catch-up；GP；读实数据重跑；抢 AI 叶26 who_pays  
- **背景**：Leo 04:35 ET 加压抬密封窗年化；Alpha 同日叠仓一页 + 正交叶定义已落；AI 叶26 who_pays 撰写中。

---

## A. 目标与约束

| 项 | 口径 |
|---|---|
| Leo 今日冲刺（04:35） | 密封窗净成本年化约 **12–15%**，**MDD≤25%**（搜索例程用语；未改 Mandate 门锁） |
| Mandate 门锁（Leo 10-12） | CAGR **12%–18%** · MDD **不差于 −28%**（`MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md` §1/§7） |
| AUM | **60万 ∧ 100万** 同时过；现货名义 L≤1.0；无融资 |
| 主干 | 纸面仍是 **capacity_adv（top300）** / **B4 50/25/25**；本方案只加研究级叠层 |
| 密封窗 | 2018-01→2024-05；当前多数 HI_LIQ/FULLA 腿自 2024-01 起 → **密封声明 N/A**（须先补齐权重覆盖再谈密封） |
| 盒机事故 | 纸面 catch-up/.ok 曾失效（`ARCH_BOX_REFRESH_INCIDENT_20261025_0111ET_ZH.md`）；**本方案不授权任何纸面装跑** |

**可比现状（样本内 X2，非密封；不作主结论）**

| 轨 | 60万 CAGR/MDD | 100万 CAGR/MDD | 出处 |
|---|---|---|---|
| 纸面 capacity_adv top300 | 13.82% / −10.07% | 12.23% / −11.62% | `output/loop/scorecard_latest.md` L5–8；SEARCH_LOOP 04:37 |
| 纸面 B4 conc 50/25/25 | 15.11% / −13.85% | 14.24% / −13.17% | 同上 L11–14 |
| B4 HI_LIQ（N1 更正后） | 21.43% / −19.74% | 13.77% / −23.28% | `STRATEGY_HILIQ_CAPADV_X2_ZH.md` 置顶更正（旧 22.44/14.90 作废） |
| capacity_adv HI_LIQ 单腿 | −0.58% / −29.93% | 1.71% / −32.99% | 同上 §1（两档破 MDD≤25%） |
| moneyflow_resid 单跑 | 9.75% / −15.25% | 9.70% / −16.27% | `BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md` 数字表 |
| etf_core_sleeve 单跑 | 8.46% / −20.39% | 9.43% / −20.05% | `BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` 数字表 |
| resid_etf（已败） | 5.25% / −14.92% | 5.52% / −14.74% | `BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` |

纸面顶线已贴近 12–15%，但 **密封未过 + 双引擎对账未做**；裸 HI_LIQ capadv 破 MDD。本页只给机制接线，不承诺数字。

---

## B. 两条可行路径（相对 capacity_adv / B4）

### 路径 1 · 慢因子目标权重（优先试）

| 项 | 定义 |
|---|---|
| 信号（PIT） | 宽基 ETF 份额 Δ 或 `flow_est_*`（候选池默认 `510300` 为主，可选扩 `510050/510500/159915`，**禁 512100**）；`available_at.normalize()≤session`；数据候选见 §引用 `etf_share_flow_pit_major` / `etf_share_flow_pit_all` |
| 更新频率 | **慢·月频**（对齐 `month_end_plus_first_last`，与 capacity_adv 同日历） |
| 进入组合 | 不另开袖套：把信号变成 **压舱/卫星预算的慢倾斜**——例：510300 压舱权重在 \[0.10, 0.30\] 内随宽基净流入 z 缓变；或对 B4 合成后的行业桶做 ±κ 倾斜（κ 预注册，默认小） |
| vs capacity_adv/B4 | **选股轴不变**（仍 ADV/事件腿）；只改「多少仓放宽基压舱 / 行业桶」；相对差异 = 产品层流量→β 配置，不是换皮 Top-N |
| Strategy 职责 | 预注册倾斜函数、边界、双口径对标（纯股票 / 80·股票+20·510300）；**不写** who_pays 正文 |

### 路径 2 · 卫星袖套（与 Alpha 叠仓同形）

| 项 | 定义 |
|---|---|
| 信号（PIT） | **ETF 产品层流量 → 成分/行业暴露**（Alpha 叶候选 1 / AI 叶26）；**禁读**个股 D2 `moneyflow_stock_daily_pit` 作主轴 |
| 更新频率 | 日/周信号可算，**组合消费默认月频**（快慢标签须披露；见 Alpha 正交叶定义） |
| 进入组合 | 新袖套 key 建议 `alpha_slow_etf_flow`；名义 **≤20%**（主口径 80/20 叠 capacity_adv）；表内若含 510300 **先剥离再缩放**（同 Alpha moneyflow 叠仓接口） |
| vs capacity_adv/B4 | 主干仍 capacity_adv（或 B4）；卫星只贡献边际；**禁止**退化成 etf_core「直接持有行业 ETF≈0.70」 |
| Strategy 职责 | 袖套预算、剥舱、门B/GATE_V3 组合诊断接线；因子定义 / who_pays **归 AI+Alpha** |

**默认推进顺序**：先路径 1（不新开因子叶、摩擦更低）做诊断敏感性；路径 2 等 AI 叶26 who_pays + Alpha A/A′ 过闸后再叠。

---

## C. 与 moneyflow_resid / 叶线的正交与叠加

| 对照 | 规则 |
|---|---|
| **moneyflow_resid** | 机制必须是 **ETF 份额/申赎流**，不得用个股 `net_mf_amount`；叠仓时两卫星预算 **合计建议 ≤20%**，或路径 2 信号对 moneyflow 活跃集/暴露再残差一层（ρ 与 Jaccard 披露） |
| **etf_core_sleeve** | 已 X2 未过门（≈8–9% CAGR）；本方案 **不重开 0.70 ETF-core**；路径 1 只动压舱带，路径 2 是流量→股票暴露 |
| **resid_etf / ind_etf_flow_rev** | 已 FAIL / 同构 FAIL；**禁止**同数据同方向粗版重开（见 `AI_G1G5_IND_ETF_FLOW_REV_WHO_PAYS_PREREG_DRAFT_ZH.md`） |
| **V3_BROAD_ETF_PXVOL_CROWD** | 价量拥挤轮换，**不用份额流**；若并行须报 ρ，避免「拥挤+份额」双计同一宽基题材 |
| **叶线（叶25 等）** | 叶25 优先占窗；本方案不抢 `.ok`/算力；会计叶与 ETF 流默认正交，仍报 Jaccard |
| **双计压舱** | 叠进 capacity_adv 账时：`sleeves.core=0`；剥表内 510300；禁止再叠 etf_core overlay（Alpha 叠仓一页 §3/§4） |

---

## D. 摩擦与 MDD（60万 / 100万）

**有出处的量级（研究对照，非本方案实测）**

| 事实 | 数字 | 出处 |
|---|---|---|
| capacity_adv 密封重叠换手（弱样本 n=5） | 中位单边 **18.3%** / 双边 **36.6%**；年化单边≈2.2× | `STRATEGY_OPTIMIZER_CAPADV_TURN_REF_ZH.md` |
| Leo λ_turn 中心目标 | 月双边≈50% → 单边≈25% | 同上；`STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md` 再平衡节 |
| B4 纸面重叠换手 | 约 35–42% 单边（高于 capadv，非优先） | 换手参考文 |
| 纸面 cost/AUM（X2） | capadv ≈1.7%；B4 ≈2.2–2.5% | `scorecard_latest.md` |
| moneyflow 单跑 cost/AUM | ≈1.97–2.02% | moneyflow X2 回执 |
| etf_core 单跑 cost/AUM | ≈3.7–4.4%（行业 ETF 执行偏贵） | etf_core X2 回执 |
| GATE_V3 换手软闸 | 双边换手 **≤20%/日**（组合诊断） | Alpha 叠仓一页 / 正交叶定义引用 |

**本方案摩擦预期（定性，待测）**

- 路径 1：只调压舱/行业桶，预期增量换手 **远小于** 新开满仓卫星；目标保持在 capadv 换手中位 ±20% 内（与优化器标定同形）。  
- 路径 2：月频 80/20 叠仓，成本量级预期介于 capadv 与 moneyflow 单跑之间；**若落到行业 ETF 实物腿，成本可能靠近 etf_core 的 3–4%——故默认映射到股票暴露而非持有一篮子行业 ETF**。  
- 60万档按手取整会稀释卫星仓（Beta MDD 预算文已提示）→ 两档必须同报。

**MDD 叠加风险**

- 纸面 B4/capadv 的 X2 MDD 均浅于 25%；但 Beta 明确：**X2 约束不起作用 ≠ 前向/长窗 MDD≤25%**（`BETA_BUDGET_MDD25_FOR_COMBO_ZH.md` §注意事项）。  
- HI_LIQ capadv 单腿已破 25%；任何把流量信号加深中小盘 β 的叠法须报 vs 510300 与 vs 池等权。  
- 缓冲建议（研究）：组合滚动 MDD **>15% 上报**、**>25% 触发复核**（只复核、不自动降仓；同 Beta 预算建议）；路径 2 卫星名义封顶 20%。  
- **无现成数字**：本叠层在 60/100万上的联合 CAGR/MDD/成本 —— **待测**。

---

## E. 可测定义与闸门（不改纸面）

| 项 | 定义 |
|---|---|
| 对标 | ① capacity_adv alone（纸面权重）；② B4 alone；③ 纯 510300 C0；路径 1/2 各出 **双口径**（纯股票 / 80·股票+20·510300） |
| 窗 | 探索 X2（2024-06→今）先机制；密封窗仅在权重覆盖完整后另跑，**禁止**用部分重叠冒充密封 |
| 验收（研究） | **门B**：两档 Calmar 严格优于 capacity_adv 单跑，且 MDD≤15%；**GATE_V3**：两档 MDD≤25%、两档净 CAGR>capacity_adv、衰减 KEEP、双边换手≤20%/日 |
| 正交披露 | vs moneyflow_resid / etf_core / resid_etf / idx_rebal / capacity_adv：Jaccard（活跃集）与信号 ρ；≥0.7∧近等权 → 硬拒 |
| 晋级 | 过门也只进 **研究诊断包 / WATCH**；`handoff=NO`；**不**扩 paper ACTIVE、不改 FROZEN |

---

## F. 下一步 · 谁做什么 / 明确不做什么

| 角色 | 做 | 不做 |
|---|---|---|
| **AI** | 叶26 who_pays + mechanism_tag + 失效条件（宽基 ETF 资金流→暴露） | 不改组合预算；不签纸面 |
| **Alpha** | 残差清单 A/A′、与 moneyflow 分家闸、ACCEPT；叠仓接口确认剥舱 | 不替代 Strategy 接线；不派本叶再烟（moneyflow 已 WATCH） |
| **Data** | 钉宽基份额流契约：`data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`（及 all）的 sha、`available_at` 规则、510300 覆盖；缺则开契约票 | 不把探针当 ACCEPT |
| **Strategy** | 本页路径 1 倾斜预注册草稿；路径 2 袖套预算接线设计；摩擦/MDD 诊断表模板 | **不抢** AI 因子定义；不改 FROZEN；不装跑纸面；无 Arch `.ok` 不读实数据 |
| **Beta** | 叠层后 β/波动/MDD 预算联签（≤25% 复核规则） | 不自动降仓钩子（默认仍关） |
| **Arch / Eng** | 叶25 窗优先；本方案任何实数据跑另签 `.ok`；与 94322 空档协调 | 不与 enable/叶25 混签 |
| **主 Agent** | 裁定先走路径 1 诊断还是等叶26；是否派组合诊断（非再烟） | — |

**明确不做什么**

1. 不改纸面 FROZEN_CONFIG / capadv / B4 / S6。  
2. 不重开 resid_etf、ind_etf_flow_rev、etf_core 0.70 主仓。  
3. 不用个股 moneyflow 换皮冒充 ETF 流。  
4. 无 Arch 运行 `.ok` 不跑；`RESEARCH_QUIET.lock` 存在则停。  
5. 不把 X2 样本内数字写成密封或晋级。  
6. 盒机刷新事故后 **不**自行恢复/消费失效的纸面 catch-up `.ok`。

---

## 引用列表（路径 · 关键事实）

1. `docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md` — 门锁 12–18% / MDD≥−28%；主书个股+ETF；L≤1.0；60∧100万。  
2. `docs/v2/ALPHA_MONEYFLOW_RESID_CALMAR_STACK_NOTE_20261025_ZH.md` — moneyflow RESEARCH_ACCEPT+WATCH；80/20 叠 capadv；剥 510300；门B/GATE_V3。  
3. `docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md` — ETF 资金流叶：产品层≠个股 mf；残差清单与硬闸。  
4. `docs/v2/AI_G1G5_MONEYFLOW_RESID_WEIGHT_RECEIPT_ZH.md` — mf/ADV→SW demean→log 市值残差；压舱≈0.24。  
5. `docs/v2/BOOK_SMOKE_G1G5_MONEYFLOW_RESID_X2_RECEIPT_ZH.md` — 9.75%/−15.25% · 9.70%/−16.27%；cost≈2%。  
6. `docs/v2/AI_G1G5_ETF_CORE_SLEEVE_WHO_PAYS_PREREG_ZH.md` — ETF-core 0.70 + 个股 0.30 结构。  
7. `docs/v2/BOOK_SMOKE_G1G5_ETF_CORE_SLEEVE_X2_RECEIPT_ZH.md` — 8.46%/−20.39% · 9.43%/−20.05%；cost≈3.7–4.4%。  
8. `docs/v2/BOOK_SMOKE_G1G5_RESID_ETF_X2_RECEIPT_ZH.md` — resid_etf 已败 ≈5.3–5.5%。  
9. `docs/v2/AI_G1G5_IND_ETF_FLOW_REV_WHO_PAYS_PREREG_DRAFT_ZH.md` — 行业 ETF 流反转同构 FAIL。  
10. `docs/v2/V3_BROAD_ETF_PXVOL_CROWD_PREREG.md` — 宽基价量拥挤（不用份额流）；池含 510300 等。  
11. `docs/v2/BETA_BUDGET_MDD25_FOR_COMBO_ZH.md` — MDD≤25%/≤15% 预算；X2 内 B4 满仓最优；长窗警告。  
12. `docs/v2/STRATEGY_OPTIMIZER_CAPADV_TURN_REF_ZH.md` — 换手中位 18.3% 单边（弱样本）。  
13. `docs/v2/STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md` — 双口径对标；月末调仓对齐。  
14. `docs/v2/STRATEGY_HILIQ_CAPADV_X2_ZH.md` — B4 HI_LIQ N1 更正数；capadv HI_LIQ 破 MDD；密封 N/A。  
15. `docs/v2/STRATEGY_FULLA_B4_X2_ZH.md` — FULLA B4 16.80%/−19.95% · 13.78%/−22.21%。  
16. `output/loop/scorecard_latest.md` — 纸面 capadv/B4 X2 主表。  
17. `output/d1/SEARCH_LOOP_PING_20261025_0437_ET.md` — 密封 12–15%/MDD≤25% 未达标；旧 B4≈22.4% 引述（以 HILIQ 更正为准）。  
18. `docs/v2/DATA_INVENTORY_STATS_20261012.md` — `etf/share_pit/*`、`etf_share_flow_pit_major`、510300 面板路径。  
19. `docs/v2/EVENT_FLOW_DATA_STATUS.md` — ind_etf_share_flow `available_at` / trade_date 约定。  
20. `docs/v2/ARCH_BOX_REFRESH_INCIDENT_20261025_0111ET_ZH.md` — 纸面 catch-up/.ok 失效，禁混签装跑。

---
**状态**：研究草案 · 未跑实数据 · 未申请 `.ok` · 未 commit  
**path**：`docs/v2/STRATEGY_ETF_FLOW_SLEEVE_PLAN_20261025_ZH.md`
