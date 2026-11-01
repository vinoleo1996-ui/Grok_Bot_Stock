# 【FROZEN 预注册 2026-10-27 22:14 ET】fund_portfolio who_pays：公募季报持仓边际（PREREG_FROZEN · 主变体 dark_horse_add · ALLA 池）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 22:14 ET**（America/New_York；ISO `2026-10-27T22:14:00-04:00`）
- 状态：**FROZEN**（相对 who_pays 全票 **DRAFT** `7cfbb3e5` 升格为预注册冻结；主裁 **C2=A**）。冻结前**未**读任何收益/股价选定义/方向。
- 主令：2026-10-27 ~22:11 ET — 主裁 **fund who_pays → PREREG_FROZEN**（C2=A）；Arch DRAFT 只审 **`985564ee` PASS_WC** → 令 AI 出 FROZEN（钉 DRAFT/Arch/C1C2/C2 链/WHO/ALLA/前缀·NOTE/掩码；dark_horse_add；ALLA；EXECUTED=false；禁 mid_large 主口径）。
- 上游钉（本机开写前复算 **MATCH**）：
  - DRAFT：`docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` sha8 **`7cfbb3e5`**
  - Arch DRAFT 审：`docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` sha8 **`985564ee` PASS_WC**
  - Arch C1C2：`docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` sha8 **`5f7ff5a6`**
  - C2 RECEIPT / JSON / events：`cb48e5d9` / `d6024472` / `81afda13`
  - WHO 全文 / ALLA 全文：`547b246e` / `724e1df5`（条款区字节 **禁改**；本票只引用）
  - 前缀 WHO/ALLA / NOTE：`05346562` / `9a90c4eb` / `956588eb`
  - 掩码脚本：`research/all_a_universe_mask.py` **`6ab6a305`**
  - 基线 events / AE / Data：`6c8e6613` / `d96b83e1` / `e2f1ccbc`
- 机制标签：`g1g5_ashare_fund_portfolio_v1`（ALLA 补充 `g1g5_ashare_fund_portfolio_v1_allA`）；主变体 **`dark_horse_add`**；crowd_add = 备选（亦过计数闸）。
- 体例对照：叶38 PREREG_FROZEN / RECEIPT `bb8051bd`（**结构**对齐；**内容为本 fund 机制**，非叶38 overlay；**不混叶38**）。
- **本冻结 ≠ `.ok` / ≠ Eng X2 / ≠ Book-Smoke / ≠ selfcheck**；**禁**自签 `.ok`；**禁**挂 QUIET；**禁**自派 X2；**EXECUTED=`false`**。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；`leo_notify=false`。
- **未改** WHO/ALLA「## 计数附录」以上任何冻结条款字节；前缀 startswith 闭环保持。

---

## 0. Alpha / 主裁空位填写（可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_fund_portfolio_v1`（ALLA 池：`g1g5_ashare_fund_portfolio_v1_allA`）  
> **主变体**：**`dark_horse_add`**（冻结优先级：先 DH 后 crowd；crowd_add 备选）  
> **who_pays（一句）**：DH — 付钱的是只盯热门抱团、忽视冷门名字的资金；信息来自少数基金经理对非一致持仓票的独立加仓。crowd — 付钱的是季报披露前卖出且对持仓信息反应慢的资金（多家主动权益同季集中加仓 → 跟随/补仓）。  
> **可检验预测**（写于读收益前；本冻结不验）：事件后 T2 起 60 交易日，组合相对 510300 去 β 残差 α > 0；vs capacity_adv / earnings_event / report_rc_allup / insider_increase 去 β ρ <0.5；DH 残差 α 应高于 crowd（若相反 → 疑动量/抱团）。  
> **计数闸（已引用 C2；本票不重跑）**：**gate_pass=`true`**；DH X2 不同股票 **2835**（≥50）；年 2024/25/26 = **1727/2007/1614**（各≥25）；全压舱 **1.65%**（≪40%）；池=ALLA 可交易；**非** mid_large 主口径。  
> **失效 / 硬闸**：沿用 WHO FROZEN（Jaccard / ρ / α / 组合门 / 成本·衰减 / RSS≤1.5GB / G6 等）；**≠本票 ACCEPT**；终判以 Eng Book-Smoke X2 为准（本执行器不自跑）。  
> **交 Alpha / 下一跳**：本票交主 → **Arch 只审本 FROZEN**；**禁**自签 `.ok`；**禁**自派 X2 / Book-Smoke。过 Arch 后再由主令开 Eng 窗。

---

## 1. 机制与谁付钱 — **FROZEN**

| 变体 | 机制 | 谁付钱 |
|---|---|---|
| **dark_horse_add（主）** | 非一致持仓票（上季持有基金数少）被少数基金显著加仓/新进；信息 = 基金经理独立研究 | 只盯热门抱团、忽视冷门名字的资金 |
| **crowd_add（备选）** | 多家主动权益同季集中加仓某票；后续同风格跟随、季报后被动补仓 | 季报披露前卖出、且对持仓信息反应慢的资金 |

仓位规则（沿用 WHO `547b246e` / ALLA `724e1df5`；本票**不改**条款区）：每名 **4%**、**≤20** 名、SW L1 **≤28%**，余额 **510300**；排除 **600519/002371**。

主/子变体只选一个送 ACCEPT 路径：优先级 **先 `dark_horse_add`、后 `crowd_add`** — 第一个过计数闸者为主变体（写于计数前；C2 已确认 DH 过闸 → 主变体 = DH）。**禁**事后改优先级。

---

## 2. 数据与 PIT / available_at / 判定日 — **FROZEN**

| 项 | **FROZEN**（WHO `547b246e` + ALLA `724e1df5`） |
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
| 本冻结 | **未**读收益/股价；只引用 C2 已落盘计数；**不重算** |

---

## 3. 事件定义（阈值写死；主变体 dark_horse_add）— **FROZEN**

沿用 WHO FROZEN（阈值已写死；计数后不调；本票不改条款区）：

1. **crowd_add**：判定日上，满足「加仓」的不同主动权益基金数 **≥ K（K=10）**。  
2. **dark_horse_add**：上季持有该票基金数 **≤ 5**（非一致）；本季加仓/新进基金数 **≥ 2**；且加仓基金合计增持市值 **≥ 该票流通市值 0.1%**。  
3. 主变体 = **`dark_horse_add`**（C2 `primary_variant_candidate` MATCH）。

**禁**冻结后读收益改阈 / 改 K / 改非一致上限 / 翻主变体。

---

## 4. 池：ALLA 可交易（明确非 mid_large 主口径）— **FROZEN**

| 项 | **FROZEN** |
|---|---|
| 主口径 | **ALLA 可交易**（`research/all_a_universe_mask.py`；mask 实现 sha8 **`6ab6a305`**） |
| **mid_large 主口径** | **`false`**（**禁** mid_large 作主口径；对照口径非本票主裁） |
| 池滤参数（C2 JSON） | `pool_filter=ALLA_tradable_on_judgment_day` |
| 剔除 | ST/*ST；停牌；上市 **&lt;60** 交易日；**ADV20 &lt; 200 万元**（=100万档 capacity_adv：NAME_CAP 4% × AUM 100万 / k=0.02） |
| 判定日掩码聚合（C2 披露） | mask_rows=149775；in=142761；st=4758；susp=452；young=1874；adv=132 |
| 相对无池滤基线 | DH 剔 272 / crowd 剔 194（drop reason=`not_in_all_a`）；基线 events **`6c8e6613`** |
| Eng 硬钉（Arch C3） | 正式窗必须沿用判定日 ALLA 掩码；**禁**改回 mid_large 主口径；禁「计数无池滤、X2 再滤」 |

---

## 5. 计数闸结果（只引用 C2 钉；不重跑）— **FROZEN 引用**

| 项 | 值 | 来源 |
|---|---|---|
| **gate_pass** | **`true`** | RECEIPT `cb48e5d9` / JSON `d6024472` / Arch C1C2 `5f7ff5a6` |
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

**C12 纪律（对齐 Arch）**：gate_pass 仅放行继续讨论 / 开 FROZEN / 开 Eng 窗准备；**不解阻** X2 ACCEPT / Book-Smoke / 升纸面 / 签 `.ok`；本票与本冻结均**未**读收益。

---

## 6. 失败条件 / 硬闸（沿用 WHO FROZEN；≠本票 ACCEPT）— **FROZEN**

读收益前写死（摘自 WHO `547b246e`；终判以 Eng Book-Smoke X2 为准；**本执行器不自跑、不代判 ACCEPT**）：

1. 任一日 Jaccard vs 任一旧包（重点 capacity_adv、northbound_flow、moneyflow_resid；硬闸清单另含 B4、report_rc_allup、earnings_event、insider_increase、analyst_recoverage、tp_rerate）**≥0.7** → 同构硬拒。  
2. 去 β / 去行业·市值残差 ρ vs capacity_adv / earnings_event / report_rc_allup 等 **>0.5** → 不过（或只作强度过滤、不开主叶，以 WHO FROZEN 条文为准）。  
3. 残差 α ≤0 → 不过；≥2 个年份残差 α 为负 → WATCH。  
4. 组合门：cap80+叶20，60万/100万两档；并行 Gate A/B；GATE_V3 等 — 见 WHO。  
5. 成本门：自检 v2 不可交易 → 不过；衰减门非 KEEP → 不过。  
6. peak RSS **>1.5GB** 或 G6 不过 → 不过；**rss 意向 ≤1500 MB 禁抬**。  
7. 年化：ALLA 补充主报 **244**（252 对照）；两口径结论不一致 → WATCH。  
8. promotion=`false`；live=`false`；禁 GP/高杠杆；**禁 mid_large 主口径**。

**本票明确**：列出硬闸 ≠ 本票 ACCEPT；≠ X2 ACCEPT；KEEP 亦不解阻 ACCEPT。

---

## 7. Arch CONDITIONS 入钉（`985564ee` §3；主裁 C2=A）

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | DRAFT ≠ 可签 `.ok` / ≠ X2 ACCEPT | 本文件为 **PREREG_FROZEN**；仍 **≠** `.ok` / ≠ X2 ACCEPT；须主令另开 Eng 独立窗 |
| **C2** | 全票冻结路径 **A 或 B** | 主裁明示 **C2=A** → 本文件即 DRAFT→FROZEN 升格；下一跳 = Arch **只审本 FROZEN** → 再开 X2 |
| C3 | Eng 池硬钉 ALLA | §4：`6ab6a305` 判定日掩码；禁 mid_large 主口径；禁计数无池滤、X2 再滤 |
| C4 | 过程硬禁 | 禁签 fund `.ok`；禁挂 QUIET；禁自派 X2/Book-Smoke/计数；**禁混叶38**；禁抬 rss 意向 1500；live=false；leo_notify=false |
| C5 | 轻量闸 ≠ 收益验收 | gate_pass 仅放行讨论/开窗；残差 α / Jaccard / 组合门 / 成本·衰减 **以 Eng Book-Smoke X2 终判**；本冻结**未**读收益 |

残留 NOTE（不改结论；沿用 Arch）：WHO 前缀正文仍留「池：mid_large PIT top300」史句，已被 ALLA 补充 + C2 主口径 supersede；本 FROZEN 正确标 `mid_large_主口径=false`。

---

## 8. 上游 sha 钉表（开写前复算 MATCH）

| 件 | 路径 | 期望 sha8 | 实测 | 结果 |
|---|---|---|---|---|
| who_pays DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_DRAFT_20261027_ZH.md` | `7cfbb3e5` | `7cfbb3e5` | **MATCH** |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_DRAFT_REVIEW_20261027_ZH.md` | `985564ee` | `985564ee` | **MATCH** |
| Arch C1C2 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_C1C2_SNAPSHOT_ALLA_REREVIEW_20261027_ZH.md` | `5f7ff5a6` | `5f7ff5a6` | **MATCH** |
| RECEIPT C2 | `docs/v2/audit/AI_FUND_PORTFOLIO_COUNT_APPENDIX_RECEIPT_20261027_C2_ALLA_ZH.md` | `cb48e5d9` | `cb48e5d9` | **MATCH** |
| JSON C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla.json` | `d6024472` | `d6024472` | **MATCH** |
| events C2 | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| WHO 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA 全文 | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| WHO 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `05346562` | `05346562` | **MATCH** |
| ALLA 前缀 `.bin` | `docs/v2/audit/AI_FUND_PORTFOLIO_ALLA_CLAUSE_PREFIX_SNAPSHOT_20261027.bin` | `9a90c4eb` | `9a90c4eb` | **MATCH** |
| NOTE | `docs/v2/audit/AI_FUND_PORTFOLIO_PREFIX_SNAPSHOT_NOTE_20261027_ZH.md` | `956588eb` | `956588eb` | **MATCH** |
| 掩码脚本 | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| 基线 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_rerun_events.json` | `6c8e6613` | `6c8e6613` | **MATCH** |
| AE | `data/v2/ref/fund_basic_active_equity.parquet` | `d96b83e1` | `d96b83e1` | **MATCH** |
| Data RECEIPT | `docs/v2/audit/DATA_FUND_BASIC_ACTIVE_EQUITY_RECEIPT_20261027_ZH.md` | `e2f1ccbc` | `e2f1ccbc` | **MATCH** |

**C1 前缀闭环**：WHO/ALLA 全文仍 startswith 前缀快照（WHO 5618 B；ALLA 2700 B）；本票**未改**「## 计数附录」以上任何冻结条款字节。

---

## 9. 旁线 / 禁混叶38

| 项 | **FROZEN** |
|---|---|
| 叶38 | **旁线不混**：禁碰 / 禁 RESTORED `62acf9fc` / 脚本 `d5cf50bb` / RECEIPT `4649335f` / VOID 链；禁把叶38 overlay 规则抄进本 fund 机制 |
| 本机制 | 公募季报持仓边际（事件组合 α）；**≠** mask-only exclusion overlay |
| 叶38 体例 | 仅借结构（PREREG_FROZEN + RECEIPT）；内容为本 fund |

---

## 10. 状态机 / 下一跳

```
who_pays DRAFT 7cfbb3e5
  + Arch DRAFT PASS_WC 985564ee
  + Arch C1C2 5f7ff5a6 + C2 cb48e5d9/d6024472/81afda13
  + WHO 547b246e / ALLA 724e1df5 / 前缀 05346562·9a90c4eb
      → 主裁 C2=A
          → 【本文件】PREREG_FROZEN（dark_horse_add；ALLA；EXECUTED=false）
              → 交主 → Arch 只审本 FROZEN（本拍目标）
                  → 主令另开 Eng Book-Smoke / X2 独立窗（独立 .ok；禁自派；禁混叶38）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件** |
| 申 `.ok` / X2 / Book-Smoke / QUIET | **禁**（等主/Arch） |
| gate_pass | true（C2 引用）；**≠X2 ACCEPT** |
| mid_large 主口径 | **false** |
| EXECUTED / live / promotion / ok_requested | false / false / false / false |
| 叶38 | **旁线不混** |

---

## 11. 禁项清单（再钉）

- 禁自派 Eng X2 / Book-Smoke；禁自签 fund `.ok`；禁挂 `RESEARCH_QUIET.lock`
- 禁读收益冒充过闸；禁重跑计数改钉
- 禁混叶38；禁改 WHO/ALLA 前缀条款区（`05346562` / `9a90c4eb`）
- 禁 mid_large 主口径；禁抬 rss 意向 1500；禁 git commit
- live=`false`；promotion=`false`；leo_notify=`false`；EXECUTED=`false`；≠X2 ACCEPT；≠本票 ACCEPT

---

## 12. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` |
| RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_RECEIPT_20261027_ZH.md` |
| 状态 | **PREREG_FROZEN**（≠ `.ok`；≠ X2 ACCEPT） |
| mechanism_tag | `g1g5_ashare_fund_portfolio_v1` / ALLA `…_v1_allA` |
| 主变体 | **`dark_horse_add`**（crowd 备选） |
| 池 | ALLA 可交易；`mid_large_主口径=false`；mask **`6ab6a305`** |
| Arch DRAFT | `985564ee` PASS_WC；主裁 **C2=A** |
| C2 钉 | RECEIPT `cb48e5d9` / JSON `d6024472` / events `81afda13` |
| WHO/ALLA | `547b246e` / `724e1df5`；前缀 `05346562` / `9a90c4eb` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
