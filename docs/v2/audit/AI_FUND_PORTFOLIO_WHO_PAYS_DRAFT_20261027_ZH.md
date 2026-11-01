# 【DRAFT — NOT FROZEN · 全票】fund_portfolio who_pays：公募季报持仓边际（主变体 dark_horse_add · ALLA 池）

- 角色：QuantLab AI（执行器）
- 时点：2026-10-27 ~21:59 ET（America/New_York；ISO `2026-10-27T21:59:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。本票 = **who_pays 全票草稿**（非计数附录；非 X2）。**EXECUTED=`false`**；**promotion=`false`**；**live=`false`**；**leo_notify=`false`**；**≠X2 ACCEPT**；**≠本票 ACCEPT**。
- 触发：主裁双线 GO · fund who_pays 线；Arch 审 **`5f7ff5a6` PASS**（`docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md`）→ 可开 who_pays。
- 机制标签意向：`g1g5_ashare_fund_portfolio_v1`（ALLA 补充 `g1g5_ashare_fund_portfolio_v1_allA`）；主变体 **`dark_horse_add`**；crowd_add = 备选（亦过计数闸）。
- **未**重跑计数；**未**读收益/股价序列；**未**自签 `.ok`；**未**挂 QUIET；**未** Book-Smoke；**未**自派 X2；**未**混叶38；**未** git commit；**未**抬 rss 叙事。
- 冻结条款锚：WHO 全文 **`547b246e`**（前缀条款区字节 **禁改**；前缀快照 **`05346562`**）；ALLA 全文 **`724e1df5`**（前缀 **`9a90c4eb`**）。本票只引用、不改条款区。

---

## 0. Alpha / 主裁空位填写（可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_fund_portfolio_v1`（ALLA 池：`g1g5_ashare_fund_portfolio_v1_allA`）  
> **主变体**：`dark_horse_add`（冻结优先级：先 DH 后 crowd；crowd_add 备选）  
> **who_pays（一句）**：DH — 付钱的是只盯热门抱团、忽视冷门名字的资金；信息来自少数基金经理对非一致持仓票的独立加仓。crowd — 付钱的是季报披露前卖出且对持仓信息反应慢的资金（多家主动权益同季集中加仓 → 跟随/补仓）。  
> **可检验预测**（写于读收益前；本票不验）：事件后 T2 起 60 交易日，组合相对 510300 去 β 残差 α > 0；vs capacity_adv / earnings_event / report_rc_allup / insider_increase 去 β ρ <0.5；DH 残差 α 应高于 crowd（若相反 → 疑动量/抱团）。  
> **计数闸（已引用 C2；本票不重跑）**：**gate_pass=`true`**；DH X2 不同股票 **2835**（≥50）；年 2024/25/26 = **1727/2007/1614**（各≥25）；全压舱 **1.65%**（≪40%）；池=ALLA 可交易；**非** mid_large 主口径。  
> **失效 / 硬闸**：沿用 WHO FROZEN（Jaccard / ρ / α / 组合门 / 成本·衰减 / RSS≤1.5GB / G6 等）；**≠本票 ACCEPT**；终判以 Eng Book-Smoke X2 为准（本执行器不自跑）。  
> **交 Alpha / 下一跳**：本票交主 → **Arch 只审 who_pays**；**禁**自签 `.ok`；**禁**自派 X2 / Book-Smoke。过 Arch 后再由主令开窗。

---

## 1. 机制与谁付钱

| 变体 | 机制 | 谁付钱 |
|---|---|---|
| **dark_horse_add（主）** | 非一致持仓票（上季持有基金数少）被少数基金显著加仓/新进；信息 = 基金经理独立研究 | 只盯热门抱团、忽视冷门名字的资金 |
| **crowd_add（备选）** | 多家主动权益同季集中加仓某票；后续同风格跟随、季报后被动补仓 | 季报披露前卖出、且对持仓信息反应慢的资金 |

仓位规则（沿用 WHO/ALLA FROZEN；本票不改）：每名 4%、≤20 名、SW L1 ≤28%，余额 510300；排除 600519/002371。

---

## 2. 数据与 PIT / available_at / 判定日

| 项 | 冻结口径（WHO `547b246e` + ALLA `724e1df5`） |
|---|---|
| 源 | `fund_portfolio`（ts_code=基金，symbol=股票，end_date、ann_date、mkv、amount、stk_mkv_ratio、stk_float_ratio） |
| 基金过滤 | 仅主动权益（`fund_basic` AE）；剔指数/ETF/联接 |
| AE 钉 | `data/v2/ref/fund_basic_active_equity.parquet` **`d96b83e1`**（Data RECEIPT **`e2f1ccbc`**） |
| available_at | 该基金该期 **ann_date 次一交易日 09:00**；基金层逐只 ann_date；**不用**季末日 |
| 截面 | 「多家基金」只用 `available_at ≤ 判定日` 的基金 |
| **判定日** | 季末后第 **16** 个交易日（Q1/Q3 前十大口径）；中报/年报全持仓不与前十大混算 |
| 加仓 | 同基金同票本期 amount 较上期 **≥20%**，或新进入前十大 |
| 入场 | 判定日 T1，**T2 入场**，持 **60** 交易日；同票新事件截断旧窗 |
| X2 窗意向 | **2024-01-02 → 2026-10-09**；封存窗 2018→2024-05 只计数、不读价格/收益 |
| 本票 | **未**读收益/股价；只引用 C2 已落盘计数 |

---

## 3. 事件定义（钉冻结阈值；主变体 dark_horse_add）

沿用 WHO FROZEN（阈值已写死；计数后不调）：

1. **crowd_add**：判定日上，满足「加仓」的不同主动权益基金数 **≥ K（K=10）**。  
2. **dark_horse_add**：上季持有该票基金数 **≤ 5**（非一致）；本季加仓/新进基金数 **≥ 2**；且加仓基金合计增持市值 **≥ 该票流通市值 0.1%**。  
3. 主/子变体只选一个送 ACCEPT 路径：优先级 **先 `dark_horse_add`、后 `crowd_add`** — 第一个过计数闸者为主变体（写于计数前；C2 已确认 DH 过闸 → 主变体 = DH）。

---

## 4. 池：ALLA 可交易（明确非 mid_large 主口径）

| 项 | 值 |
|---|---|
| 主口径 | **ALLA 可交易**（`research/all_a_universe_mask.py`；mask 实现 sha8 现盘 **`6ab6a305`**） |
| **mid_large 主口径** | **`false`**（禁 mid_large 作主口径；对照口径非本票主裁） |
| 池滤参数（C2 JSON） | `pool_filter=ALLA_tradable_on_judgment_day` |
| 剔除 | ST/*ST；停牌；上市 **&lt;60** 交易日；**ADV20 &lt; 200 万元**（=100万档 capacity_adv：NAME_CAP 4% × AUM 100万 / k=0.02） |
| 判定日掩码聚合（C2 披露） | mask_rows=149775；in=142761；st=4758；susp=452；young=1874；adv=132 |
| 相对无池滤基线 | DH 剔 272 / crowd 剔 194（drop reason=`not_in_all_a`）；基线 events **`6c8e6613`** |

---

## 5. 计数闸结果（只引用 C2 钉；不重跑）

| 项 | 值 | 来源 |
|---|---|---|
| **gate_pass** | **`true`** | RECEIPT `cb48e5d9` / JSON `d6024472` / Arch `5f7ff5a6` |
| 主变体 | **`dark_horse_add`** | 冻结优先级 + C2 `primary_variant_candidate` |
| crowd_add | gate_pass=`true`（备选） | 同 |
| peak_rss_mb | **249.2**（≤1500；未抬） | C2 |
| 本票动作 | **未**重跑计数；**未**读收益冒充过闸 | — |

### dark_horse_add（主）

| 指标 | 值 | 闸 |
|---|---:|---|
| 全窗事件 | 12763 | — |
| X2 事件 | 5348 | — |
| X2 不同股票 | **2835** | ≥50 → **PASS** |
| 年 2024 / 2025 / 2026 | 1727 / 2007 / 1614 | 各≥25 → **PASS** |
| 全压舱日 | 11/668 = **1.65%** | >40% 才记稀疏 → **否** |

### crowd_add（备选）

| 指标 | 值 | 闸 |
|---|---:|---|
| 全窗 / X2 事件 / X2 股 | 21557 / 9476 / **2063** | 股≥50 → **PASS** |
| 年 2024/25/26 | 3302 / 3518 / 2656 | **PASS** |
| 全压舱 | 1.65% | 稀疏风险=否 |

详分季批次数与漏斗：见 WHO/ALLA「计数附录」与 JSON `d6024472`（本票不复抄全表以免双源漂移）。

---

## 6. 失败条件 / 硬闸（沿用 WHO FROZEN；≠本票 ACCEPT）

读收益前写死（摘自 WHO；终判以 Eng Book-Smoke X2 为准；**本执行器不自跑、不代判 ACCEPT**）：

1. 任一日 Jaccard vs 任一旧包（重点 capacity_adv、northbound_flow、moneyflow_resid；硬闸清单另含 B4、report_rc_allup、earnings_event、insider_increase、analyst_recoverage、tp_rerate）**≥0.7** → 同构硬拒。  
2. 去 β / 去行业·市值残差 ρ vs capacity_adv / earnings_event / report_rc_allup 等 **>0.5** → 不过（或只作强度过滤、不开主叶，以 FROZEN 条文为准）。  
3. 残差 α ≤0 → 不过；≥2 个年份残差 α 为负 → WATCH。  
4. 组合门：cap80+叶20，60万/100万两档；并行 Gate A/B；GATE_V3 等 — 见 WHO。  
5. 成本门：自检 v2 不可交易 → 不过；衰减门非 KEEP → 不过。  
6. peak RSS **>1.5GB** 或 G6 不过 → 不过。  
7. 年化：ALLA 补充主报 **244**（252 对照）；两口径结论不一致 → WATCH。  
8. promotion=`false`；live=`false`；禁 GP/高杠杆；**禁 mid_large 主口径**。

**本票明确**：列出硬闸 ≠ 本票 ACCEPT；≠ X2 ACCEPT。

---

## 7. 上游 sha 钉表（开写前复算 MATCH）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| Arch 审 PASS | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | `5f7ff5a6` | **MATCH** |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | `05346562` | **MATCH** |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | `9a90c4eb` | **MATCH** |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | `956588eb` | **MATCH** |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e6613` | **MATCH** |
| AE | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| Data RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc` | **MATCH** |
| 旧审 RERUN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_COUNT_APPENDIX_RERUN_REVIEW_20261027_ZH.md` | `b410680b` | `b410680b` | **MATCH** |

**C1 前缀闭环**：WHO/ALLA 全文仍 startswith 前缀快照；本票**未改**「## 计数附录」以上任何冻结条款字节。

---

## 8. 禁项回执

- 禁自派 X2 / Book-Smoke / 自签 `.ok` / 挂 QUIET  
- 禁读收益冒充过闸；禁重跑计数改钉  
- 禁混叶38（`.ok` `62acf9fc` / 脚本 `d5cf50bb` / RECEIPT `4649335f` **只读不碰**）  
- 禁 git commit；禁抬 rss 叙事  
- 禁改已钉 WHO/ALLA 前缀条款区（`05346562` / `9a90c4eb`）  
- live=`false`；promotion=`false`；leo_notify=`false`；EXECUTED=`false`；≠X2 ACCEPT；≠本票 ACCEPT

---

## 9. 下一跳

**交主 → Arch 只审本 who_pays 全票草稿。**  
过审后由主令再开 Eng Book-Smoke / X2 窗（本执行器**不**自开）。  
fund 线与叶38 **不混**。

---

## 10. 文末短回执

| 项 | 值 |
|---|---|
| 本 DRAFT 路径 | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` |
| 角色 / 时点 | QuantLab AI · 2026-10-27 ~21:59 ET |
| gate_pass / 主变体 | `true` / `dark_horse_add`（crowd 备选） |
| 池 | ALLA 可交易；mid_large_主口径=`false` |
| Arch | `5f7ff5a6` PASS |
| C2 钉 | RECEIPT `cb48e5d9` / JSON `d6024472` / events `81afda13` |
| WHO/ALLA | `547b246e` / `724e1df5`；前缀 `05346562` / `9a90c4eb` |
| EXECUTED / promotion / live | false / false / false |
| 未跑 X2 / 未签 `.ok` / 未混叶38 | 确认 |
| 下一跳 | 交主→Arch 只审 who_pays |
