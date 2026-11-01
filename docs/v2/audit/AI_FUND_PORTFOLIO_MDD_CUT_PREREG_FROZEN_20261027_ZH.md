# 【FROZEN 预注册 2026-10-27 23:15 ET】fund_portfolio who_pays · 组合层降 MDD（PREREG_FROZEN · MDD-cut · EXECUTED=false）

- 角色：QuantLab AI（执行器）
- 冻结时点：**2026-10-27 23:15 ET**（America/New_York；ISO `2026-10-27T23:15:00-04:00`）
- 状态：**PREREG_FROZEN**（相对 MDD-cut DRAFT **`eeccb25e`** 升格；主裁 ~23:10 ET **FROZEN GO**；Arch DRAFT 只审 **PASS_WC `41d4fc76` MATCH**——文内自称 `eee21297` **勿采**，以盘上 sha256 前 8 为准）
- 冻结前**未**读任何新收益/股价选定义/方向；**未**改 DRAFT 六变体阈值阈
- 主令：2026-10-27 ~23:10 ET — **fund 降 MDD 升 FROZEN GO**（钉本 DRAFT 参数表；主候选 **V_BALLAST_MIX**；备选 V_NAME_CAP→V_SAT_ON_TRUNK；对照 stock∈{0.40,0.60}；EXECUTED=false；禁自开 Eng/BS/X2）
- 上游钉（本机开写前复算 **MATCH**）：
  - MDD DRAFT：`docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` sha8 **`eeccb25e`**
  - MDD DRAFT RECEIPT：`docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_RECEIPT_20261027_ZH.md` sha8 **`2bf42d4b`**
  - Arch DRAFT 审：`docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` 实算 sha8 **`41d4fc76`**（PASS_WC；文内 `eee21297` 勿采）
  - 原 who_pays FROZEN：**`303e0185`** / ArchFROZEN：**`bcbe4b72`**（本票**不改其字节**；组合层另案）
  - mask **`6ab6a305`**；Eng BS **`b013a7a8`**；Arch BS **`694b9a80`** / CONSUMED **`3e2a9b9c`**
  - WHO **`547b246e`** / ALLA **`724e1df5`**；C2 events **`81afda13`**
  - 叶38旁线 **`c01c2034`**（不混）；禁 RESTORED **`f08ce32c`**
- 机制范围：**只改组合构建层**（袖套 / 名额 / 持有·双阈 / 行业·Size / 卫星叠主干 / 波动缩放）；**禁改** WHO/ALLA 事件定义条款区；主变体事件仍钉 **`dark_horse_add`**；池仍钉 **ALLA**；掩码仍钉 **`6ab6a305`**
- 体例对照：who_pays PREREG_FROZEN `303e0185`（**结构**）+ MDD DRAFT `eeccb25e`（**参数内容**）
- **本冻结 ≠ `.ok` / ≠ Eng X2 / ≠ Book-Smoke / ≠ selfcheck / ≠ACCEPT**；**禁**自签 `.ok`；**禁**挂 QUIET；**禁**自开 Eng/BS/X2；**EXECUTED=`false`**
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**；**≠Book-Smoke ACCEPT**；`leo_notify=false`
- **未改**原 who_pays FROZEN `303e0185` 任何字节；**未** RESTORED `f08ce32c`；**未**混叶38

---

## 0. 主裁 / Arch 可摘抄摘要框

> **票种**：fund who_pays **组合层降 MDD** · **PREREG_FROZEN**（EXECUTED=**false**；≠ACCEPT）  
> **问题陈述**（只引用已公开 BS Headline；**非**密封 / **≠ACCEPT**）：基线 Book-Smoke（Eng **`b013a7a8`**）stock=100% · dark_horse_add · ALLA — 60万 CAGR **13.65%** / MDD **−32.07%**；100万 **15.55%** / **−32.85%**；vs C0 ≈**11.27%** / **−16.24%**。**|MDD| 破 Leo ≤25% 硬闸** → Arch PASS_WC **`694b9a80`** + CONSUMED_PASS **`3e2a9b9c`** 后主裁 HOLD，另开本 MDD-cut 票。  
> **钉保持**：事件主变体 **`dark_horse_add`**；池 **ALLA**；掩码 **`6ab6a305`**；原 FROZEN **`303e0185`** / ArchFROZEN **`bcbe4b72`**（字节不改）；WHO **`547b246e`** / ALLA **`724e1df5`**；C2 events **`81afda13`**；weights 基线 **`601c5cf6`** / summary **`0d1ddcb0`**（只作基线陈述）。  
> **主候选（FROZEN）**：**`V_BALLAST_MIX`** — sleeves **`{"core":0.50,"stock":0.50,"alpha_event":0.0}`**（core=**510300** ballast）  
> **备选事先优先级**：**`V_NAME_CAP` → `V_SAT_ON_TRUNK`**（禁事后按收益翻）  
> **对照臂事先写入**（同 V_BALLAST_MIX 族）：**stock∈{0.40, 0.60}**（与 0.50 共 **3** 臂；禁事后按收益改）  
> **成功闸**：探索窗 60万&100万 **|MDD|≤25%** 且 **CAGR≥C0**；并报 **|MDD|≤15%** 对照（非主闸）  
> **Arch COND 入钉**：须新独立 Eng BS `.ok`；禁 RESTORED `f08ce32c`；CLI_GAP 另票；跑序先 V_BALLAST_MIX+对照再备选；不混叶38  
> **下一跳**：**交主 → Arch 只审本 FROZEN**；过审后再由主令新独立 Eng Book-Smoke。**禁**自开 Eng/BS/X2；**禁**把本 FROZEN 当 ACCEPT。  
> **旁线**：叶38 CONSUMED_PASS **`c01c2034`** 不混；`.ok` **`f08ce32c` 已归档禁 RESTORED**。

---

## 1. 问题与边界（组合构建层 only）— **FROZEN**

| 项 | 值 |
|---|---|
| 基线 sleeves | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| 基线仓位规则 | 每名 **4%**、**≤20**、SW L1 **≤28%**、余额 **510300**；持有 **60**；T2 入场 |
| 基线 Headline | 见 §0（Eng `b013a7a8`；summary `0d1ddcb0`） |
| Leo 硬闸 | 探索窗 **\|MDD\|≤25%**（主成功标准） |
| 对照轨 | **\|MDD\|≤15%**（只披露可达否；**非**本票主硬闸） |
| 本票改什么 | 袖套 ballast、名额/行业、持有·双阈、卫星叠主干、波动缩放 — **组合层参数写死** |
| 本票不改什么 | WHO/ALLA 事件阈（K / 非一致≤5 / 增持≥0.1% 等）；池 ALLA；掩码实现；主变体 dark_horse_add；C2 events 定义 |
| 禁 mid_large | **是**（主口径仍 ALLA；禁 mid_large 主口径） |
| 禁 RESTORED | **`f08ce32c`** 及任何已归档 fund BS `.ok` |
| 禁混叶38 | **是**（`c01c2034` 旁线） |
| 原 FROZEN `303e0185` | **仍有效**作事件/池/掩码钉；本票 **不**修改其条款字节 |

**谁付钱 / 风控逻辑（本另案）**：事件 alpha 仍由 dark_horse_add「独立研究加仓 vs 抱团忽视」付钱；**MDD 破闸的付钱方是组合层过度权益暴露与集中度**（stock=100% + 4%/20 名 + SW28% → 尾部同步回撤）。本票用 ballast / 名额稀释 / 双阈出场 / 行业·Size / 卫星限额 / 波动缩放，把**尾部风险预算**从「全额吃 alpha」改为「可验收的回撤帽」，不改编故事、不改事件阈。

---

## 2. 开写前盘证 MATCH（本机复算）— **FROZEN**

| 钉 | 路径 | 期望 sha8 | 实算 | 状态 |
|---|---|---|---|---|
| MDD DRAFT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_20261027_ZH.md` | `eeccb25e` | `eeccb25e` | **MATCH** |
| MDD DRAFT RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_DRAFT_RECEIPT_20261027_ZH.md` | `2bf42d4b` | `2bf42d4b` | **MATCH** |
| Arch DRAFT 审 | `docs/v2/audit/ARCH_FUND_PORTFOLIO_MDD_CUT_DRAFT_REVIEW_20261027_ZH.md` | `41d4fc76` | `41d4fc76` | **MATCH**（文内 `eee21297` 勿采） |
| 原 FROZEN | `docs/v2/audit/AI_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_20261027_ZH.md` | `303e0185` | `303e0185` | **MATCH**（字节未改） |
| ArchFROZEN | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_PREREG_FROZEN_REVIEW_20261027_ZH.md` | `bcbe4b72` | `bcbe4b72` | **MATCH** |
| 掩码 | `research/all_a_universe_mask.py` | `6ab6a305` | `6ab6a305` | **MATCH** |
| Eng BS | `docs/v2/audit/ENG_FUND_WHO_PAYS_BOOK_SMOKE_RUN_RECEIPT_20261027_ZH.md` | `b013a7a8` | `b013a7a8` | **MATCH** |
| Arch PASS_WC | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_RUN_REVIEW_20261027_ZH.md` | `694b9a80` | `694b9a80` | **MATCH** |
| Arch CONSUMED | `docs/v2/audit/ARCH_FUND_PORTFOLIO_WHO_PAYS_BOOK_SMOKE_CONSUMED_PASS_20261027_ZH.md` | `3e2a9b9c` | `3e2a9b9c` | **MATCH** |
| WHO | `docs/v2/AI_G1G5_FUND_PORTFOLIO_WHO_PAYS_PREREG_ZH.md` | `547b246e` | `547b246e` | **MATCH** |
| ALLA | `docs/v2/AI_G1G5_FUND_PORTFOLIO_ALLA_SUPPLEMENT_PREREG_ZH.md` | `724e1df5` | `724e1df5` | **MATCH** |
| C2 events | `output/ai_factory/fund_portfolio_count_appendix_20261027_c2_alla_events.json` | `81afda13` | `81afda13` | **MATCH** |
| 叶38 旁线 | `docs/v2/audit/ARCH_LEAF38_…_CONSUMED_PASS_20261027_ZH.md` | `c01c2034` | `c01c2034` | **MATCH**（不混） |
| live fund `.ok` | `output/ai_factory/*.ok`（非 `_consumed`） | ABSENT | ABSENT | **MATCH** |
| QUIET | `output/loop/RESEARCH_QUIET.lock` | ABSENT | ABSENT | **MATCH** |
| `f08ce32c` | `_consumed/…CONSUMED_PASS…ok` | 仅归档 | 仅归档；未 RESTORED | **MATCH** |

未申 `.ok`；QUIET 勿挂；未跑 BS/X2；未按未跑收益调阈。

---

## 3. 事先编号变体（参数写死；禁事后改）— **FROZEN**

共 **6** 个稳定名。**角色标注（冻结时钉死；禁事后按收益翻）**：

| 角色 | 变体 | 说明 |
|---|---|---|
| **主候选** | **`V_BALLAST_MIX`**（stock=**0.50** / core·510300=**0.50**） | 升窗首跑 |
| **对照臂**（同族事先） | `V_BALLAST_MIX` stock∈{**0.40**, **0.60**} | 与 0.50 共 3 臂；禁事后改 |
| **备选 1** | **`V_NAME_CAP`** | 事先优先级第 2 |
| **备选 2** | **`V_SAT_ON_TRUNK`** | 事先优先级第 3 |
| 机制对照 | `V_HOLD_GATE` / `V_IND_SIZE` / `V_VOL_SCALE` | 同窗披露，不升主 |

公共钉（所有变体；沿 DRAFT `eeccb25e`；**冻结时不得改阈**）：

| 公共项 | 写死值 |
|---|---|
| 主变体 / 事件 | **dark_horse_add**；C2 `events_dark_horse_add`（`81afda13`） |
| 池 | **ALLA** 可交易；掩码 `6ab6a305`；**禁 mid_large 主口径** |
| 入场 | 判定日 T1，**T2 入场**；同票新事件截断旧窗 |
| 排除 | **600519 / 002371** |
| 窗 | 权重覆盖 FROZEN **2024-01-02→2026-10-09**；BS/X2 评窗与基线同模块 **2024-06-03→2026-10-09**（披露起点差，不另开） |
| AUM | **60万 & 100万** 两档同报 |
| rss 意向 | ≤**1500** MB 禁抬 |
| EXECUTED | **false**（本票；真跑须主令新独立 Eng BS） |

### 3.1 `V_BALLAST_MIX` — **主候选**（+ 对照臂）

- **角色**：**主候选**（stock=0.50）；对照 stock∈{0.40, 0.60} 事先写入  
- **机制一句**：把 stock 袖套从 100% 降到固定 ballast 比例，余额进 **core=510300**（指数压舱），降低权益 β 与同步回撤深度。  
- **为何预期降 MDD**（方向陈述；**不编造未跑数字**）：基线 MDD≈32% 在 stock=1.0；线性压舱通常近似按权益权重缩放组合回撤（另有再平衡/成本效应）；目标是把 |MDD| 压进 ≤25%，并观察 CAGR 是否仍 ≥ C0。  
- **vs B4 / capacity_adv**：B4 = 多叶线性混袖纸面轨；capacity_adv = Top-N 容量纸面主干。本变体 **不是** 改 B4 权重、也 **不是** 把 DH 事件换成 capacity_adv 事件；只是在 **DH 权重长表之上** 做 sleeve 级 ballast（stock↔510300）。与 capacity_adv 的关系 = 对照/正交对象仍按 WHO 硬闸（Jaccard/ρ），本票不重跑。

| 参数 | 主候选写死 | 对照（同票披露，不升主） |
|---|---|---|
| sleeves | `{"core":0.50,"stock":0.50,"alpha_event":0.0}` | stock∈{**0.40**, **0.60**}（core=1−stock；alpha_event=0） |
| ballast_tag | `510300_core_ballast` | 同 |
| name_cap / n_max | **4%** / **≤20**（沿基线） | 同 |
| SW L1 ind_cap | **≤28%** | 同 |
| hold | **60** | 同 |
| Size / 双阈 / vol | 关 | 关 |

### 3.2 `V_NAME_CAP` — **备选 1**

- **角色**：**备选 1**（事先优先级：主 → 本 → V_SAT_ON_TRUNK）  
- **机制一句**：单票上限下调 + 名数上限上调，在同一事件池上稀释个股与行业尾部贡献。  
- **为何预期降 MDD**：基线 4%×20 允许高集中；降到 2.5%×40 降低单名冲击，并同步收紧 SW L1，减轻行业柱同步回撤。

| 参数 | 主候选写死 | 对照 |
|---|---|---|
| sleeves | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` | 同 |
| name_cap / n_max | **2.5%** / **≤40** | **3.0%** / **≤30** |
| SW L1 ind_cap | **≤20%**（相对基线 28% 收紧） | 对照臂可报 **≤28%** 保持（只披露） |
| hold | **60** | 同 |
| ballast_tag | `none` | — |

### 3.3 `V_HOLD_GATE` — 机制对照

- **角色**：机制对照（同窗披露，不升主）  
- **机制一句**：**慢目标仓**（持有期缩短）+ **快闸**（滚动回撤触阈降仓）+ **双阈值 no-trade buffer**（掉出持有线才卖，避免一触即翻）。  
- **为何预期降 MDD**：缩短权益暴露久期；回撤触阈强制去杠杆；双阈减少震仓放大成本与被动高水位回撤。  
- **禁**：只事后看收益改阈（下列阈值写死于本 FROZEN / 源 DRAFT）。

| 参数 | 写死 |
|---|---|
| sleeves | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| name_cap / n_max / ind_cap | **4%** / **≤20** / SW L1 **≤28%** |
| hold_slow（目标持有） | **40** 交易日（相对基线 60） |
| fast_gate | 名维度：过去 **20** 交易日滚动简单收益 ≤ **−12%** → 该名目标权重置 **0**（次日 T+1 生效） |
| dual_threshold | 买入线 = 事件入场（T2）；持有线 = 剩余持有日 >0 **且** 未触 fast_gate；若仅因「排序/拥挤」拟减仓但未破持有线 → **no-trade buffer**（本变体无二次排序分，buffer 表现为：非 gate/非到期不主动换仓） |
| ballast_tag | `none` |

### 3.4 `V_IND_SIZE` — 机制对照（对齐 Leo 工业柱③）

- **角色**：机制对照（同窗披露，不升主）  
- **机制一句**：行业 **硬约束**收紧 + Size **软约束**（slack）— 硬锁尾部行业集中，软罚风格漂移。  
- **为何预期降 MDD**：SW 一级过厚是 A 股同步回撤常见通道；收紧 ind_cap 降低柱风险；Size 中性减少杠铃暴露（对齐 `ARCH_INDUSTRIAL_PILLARS_SPEC_ZH.md` 硬/软分工）。  
- **硬 vs 软**：行业 SW L1 **硬**（超限不可行→截断/再分配至合规）；Size 偏离 **软**（二次罚或 slack 阶梯，允许 ≤ slack 上限）。

| 参数 | 写死 |
|---|---|
| sleeves | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` |
| name_cap / n_max | **4%** / **≤20** |
| SW L1 ind_cap（硬） | **≤18%**（落在建议带 15–20%；对照可另报 **≤15%**） |
| Size（软） | 相对可交易池标准化 Size 暴露目标 **0**；允许 soft slack **±0.35σ**，slack 上限再 **+0.05σ**（对齐优化器族既有盒；本票若 Eng 无 Size 管道则记 `SIZE_PIPE_GAP` 只披露行业硬约束臂） |
| hold | **60** |
| ballast_tag | `none` |

### 3.5 `V_SAT_ON_TRUNK` — **备选 2**

- **角色**：**备选 2**（事先优先级第 3；依赖 trunk 可消费）  
- **机制一句**：dark_horse_add 作 **卫星**，叠在 **capacity_adv**（或现行纸面主干权重）上；卫星权重写死，过闸看 **组合级** NAV。  
- **为何预期降 MDD**：主干已在纸面族验收过较浅回撤；卫星限额锁定增量回撤预算。  
- **过闸口径**：**组合级**（trunk+satellite 合成 NAV 的 CAGR/MDD）为主成功标准；**卫星残差**（satellite−trunk 或去 β 残差）只作 who_pays/正交披露，**不**单独充当 |MDD|≤25% 主闸。

| 参数 | 写死 |
|---|---|
| trunk | `capacity_adv` 纸面主干权重（Eng 取现行可消费路径；若缺 → `TRUNK_PIN_GAP` 阻断该臂，不改用 mid_large） |
| satellite | dark_horse_add 权重长表（由 C2 events + 基线同构规则重建；**禁** RESTORED 旧 `.ok`） |
| satellite_weight | **0.30**（trunk=**0.70**）；对照臂 sat∈{**0.20**, **0.40**} 只披露 |
| sleeves 语义 | 合成后等效 stock 暴露 = trunk_stock×0.70 + sat_stock×0.30（实现以 Eng 合成器为准；本票钉比例） |
| name_cap / n_max / ind_cap（卫星腿） | **4%** / **≤20** / **≤28%**（卫星内部）；组合级另受 trunk 约束 |
| hold（卫星） | **60** |
| 过闸 | **组合级** \|MDD\| / CAGR；残差臂另表 |

### 3.6 `V_VOL_SCALE` — 可选机制对照

- **角色**：机制对照（同窗披露，不升主）  
- **机制一句**：按实现波动相对目标波动缩放总权益暴露（vol targeting）。  
- **为何预期降 MDD**：高波动阶段自动降杠杆，压制回撤峰值。

| 参数 | 写死 |
|---|---|
| sleeves 基 | `{"core":0.0,"stock":1.0,"alpha_event":0.0}` 再乘 scale |
| target_vol（年化） | **0.12** |
| lookback | **60** 交易日（组合日收益标准差 × √244；年化口径与 ALLA 补充主报 244 对齐；252 对照另披露） |
| scale 公式 | `scale_t = min(1.0, target_vol / max(realized_vol_{t-1}, 1e-6))`；再 `stock_exposure_t = scale_t`，余额进 510300 |
| 上下帽 | scale ∈ **[0.25, 1.00]**（禁杠杆 >1） |
| name_cap / n_max / ind_cap / hold | **4%** / **≤20** / **≤28%** / **60** |
| realization | 用**已实现**组合收益（含成本开）；**禁**用未来窗估 vol |

---

## 4. 成功标准 / 失效 / 禁项（事先；≠本票 ACCEPT）— **FROZEN**

### 4.1 主成功标准（探索窗；60万 & 100万 **同时**）

1. **\|MDD\| ≤ 25%**（Leo 硬闸；两档皆过）。  
2. **CAGR ≥ C0**（基线 BS 同窗 C0 ≈11.27%；以新跑 summary 的 C0 臂为准，不手工改数）。  
3. 事先可接受替代（若 C0 臂缺失）：CAGR ≥ **0** 且相对基线 BOOK 的 MDD 改善（\|MDD\| 严格浅于基线 32% 带）— **仅当** Eng 声明 C0 不可用时启用；默认用 (1)+(2)。  
4. 成本开；peak_rss ≤1500；禁 mid_large；事件仍 dark_horse_add。

### 4.2 ≤15% 对照轨（非主闸）

- 同窗同变体另标：`mdd15_reachable = (\|MDD\|≤15%)` 布尔；**不**因 false 单独否决主成功。  
- 若主候选未达 15%，备选/对照中**任一**达 15% 且 CAGR≥C0 → 记 `MDD15_ALT_HIT` 供主裁另令，**不**自动升主。

### 4.3 失效条件（组合层）

1. 任档 \|MDD\| >25% → 该变体主成功 **FAIL**（可留对照数字）。  
2. CAGR < C0 且 \|MDD\|≤25% → **WATCH**（回撤过、收益未过；不自动 ACCEPT）。  
3. Jaccard/ρ 相对 capacity_adv 等触发 WHO 硬闸 → 同构硬拒（沿原 FROZEN；本票不重定义）。  
4. `TRUNK_PIN_GAP` / `SIZE_PIPE_GAP` → 该臂阻断，不改钉临时换池。  
5. 事后改阈 / 翻主候选优先级 → 本预注册作废，须新 DRAFT。

### 4.4 硬禁

| 禁项 | 说明 |
|---|---|
| 禁 RESTORED `f08ce32c` | 已归档 CONSUMED；新窗须主令另签独立 `.ok` |
| 禁 mid_large 主口径 | 池=ALLA |
| 禁改 WHO/ALLA 事件条款区 | 只改组合构建层；原 FROZEN `303e0185` 字节不改 |
| 禁混叶38 | `c01c2034` 旁线 |
| 禁自开 Eng / Book-Smoke / X2 | 本票 EXECUTED=false；须主令新独立窗 |
| 禁把本 FROZEN 当 ACCEPT | 须 Arch 只审本 FROZEN → 主令 Eng BS → 再审 |
| 禁按未跑收益调阈 | 参数已写死于 DRAFT/本 FROZEN |
| 禁挂 QUIET / 自签 `.ok` | — |
| 禁 git commit | — |

---

## 5. 推荐优先级 / 跑序（事先；勿按未跑收益挑）— **FROZEN**

| 优先级 | 变体 | 理由（机制，非收益） |
|---|---|---|
| **主候选** | **`V_BALLAST_MIX`**（stock=0.50） | 对 MDD 的作用路径最短（直接降权益暴露）；实现贴近现行 book_smoke sleeves；与 B4 混袖叙事可区分（DH 事件不变） |
| **对照臂** | 同族 stock∈{0.40, 0.60} | 事先写入；与主候选共 3 臂首跑 |
| **备选 1** | **`V_NAME_CAP`**（2.5%/≤40；SW≤20%） | 保持满仓权益、用分散度降尾部；若 ballast 过度伤 CAGR 时的备路 |
| **备选 2** | **`V_SAT_ON_TRUNK`**（sat=0.30） | 对齐纸面主干风险预算；过闸组合级；依赖 trunk 可消费（有 PIN_GAP 风险故列第三） |
| 对照 | `V_HOLD_GATE` / `V_IND_SIZE` / `V_VOL_SCALE` | 工业柱②④ / ③ / 波动缩放机制验证；同窗披露 |

**Eng 跑序（Arch C5；事先钉）**：若主令开跑 → **先主候选 + 其 stock∈{0.40,0.60} 两对照**（共 3 臂），再按主令加备选；**禁**一次跑完靠收益挑主；**禁**事后改阈。

---

## 6. Arch CONDITIONS 入钉（`41d4fc76` §3；主裁 FROZEN GO）— **FROZEN**

| # | 条件 | 本 FROZEN |
|---|---|---|
| C1 | DRAFT ≠ 可签 `.ok` / ≠ Book-Smoke·X2·本票 ACCEPT | 本文件为 **PREREG_FROZEN**；仍 **≠** `.ok` / ≠ BS·X2·本票 ACCEPT；须 Arch 再审本 FROZEN → 主令另开 Eng 独立窗 |
| C2 | 须升 PREREG_FROZEN 后再 Eng BS | **本文件即升格**；下一跳 = Arch **只审本 FROZEN** → 再由主令新独立 Eng BS |
| C3 | 禁 RESTORED `f08ce32c` | 已归档 CONSUMED_PASS；新窗必须 **新签独立 `.ok`**（新 ET/新钉）；禁恢复旧 auth |
| C4 | Eng 池/事件硬钉 | mask **`6ab6a305`**；池 **ALLA**；事件 **dark_horse_add**（C2 `81afda13`）；**禁 mid_large 主口径**；rss≤1500 禁抬 |
| C5 | 跑序事先钉 | 先 **`V_BALLAST_MIX`** + stock∈{0.40,0.60}（共 3 臂），再按主令加备选；禁靠收益翻主；禁事后改阈 |
| C6 | CLI_GAP 另票 | `book_smoke_no_arch_ok_path` 生产适配 **不本拍**；另票待机 |
| C7 | 不混叶38 | 禁碰/禁 CONSUME/禁签 leaf38 链（旁线 `c01c2034` 维持） |
| C8 | 过程硬禁 | 禁挂 `RESEARCH_QUIET.lock`；禁代跑；禁改上游 DRAFT/WHO/ALLA/原 FROZEN；禁 git commit；live=false；leo_notify=false |

残留 NOTE（不改结论；沿用 Arch）：N1 `V_SAT_ON_TRUNK` 依赖 trunk（`TRUNK_PIN_GAP`）；N2 `V_IND_SIZE` Size 管道（`SIZE_PIPE_GAP`）；N3 原 FROZEN `303e0185` 事件/池钉仍有效；N4 基线 BS 已破 Leo ≤25% → 本另案不重开 BS ACCEPT 讨论。

---

## 7. 与上游 FROZEN / BS / DRAFT 的关系— **FROZEN**

| 项 | 关系 |
|---|---|
| 原 FROZEN `303e0185` | **仍有效**作事件/池/掩码钉；本票 **不**修改其条款字节 |
| 原 BS `b013a7a8` / Arch `694b9a80`+`3e2a9b9c` | 问题陈述与基线仓位来源；**不**重跑；**不** RESTORED 其 `.ok`（`f08ce32c`） |
| MDD DRAFT `eeccb25e` / RECEIPT `2bf42d4b` | 本 FROZEN 参数来源；阈值阈 **冻结时不得改** |
| Arch DRAFT 审 `41d4fc76` | PASS_WC MATCH；COND C1–C8 入钉 |
| 本票 | 「组合层 MDD-cut」**PREREG_FROZEN**；签 `.ok` / Eng 跑数均须 **另令** |
| ACCEPT | **false**（本票与任何未主令之 BS/X2） |

---

## 8. 旁线 / 禁混叶38— **FROZEN**

| 项 | **FROZEN** |
|---|---|
| 叶38 | **旁线不混**：`c01c2034` 维持；禁碰 / 禁 RESTORED 叶38 `.ok` 链；禁把叶38 overlay 规则抄进本 fund MDD-cut |
| 本机制 | 公募季报持仓边际事件之上的**组合层回撤削减**；**≠** mask-only exclusion overlay |
| 体例 | 仅借 who_pays PREREG_FROZEN 结构；内容为 MDD-cut |

---

## 9. 状态机 / 下一跳

```
MDD-cut DRAFT eeccb25e + RECEIPT 2bf42d4b
  + Arch DRAFT PASS_WC 41d4fc76（文内 eee21297 勿采）
  + 原 FROZEN 303e0185 / ArchFROZEN bcbe4b72（字节不改）
  + mask 6ab6a305 / Eng b013a7a8 / Arch BS 694b9a80+3e2a9b9c
  + WHO 547b246e / ALLA 724e1df5 / C2 81afda13
      → 主裁 ~23:10 ET FROZEN GO
          → 【本文件】PREREG_FROZEN（V_BALLAST_MIX 主；EXECUTED=false）
              → 交主 → Arch 只审本 FROZEN（本拍目标）
                  → 主令另开新独立 Eng Book-Smoke `.ok`（禁 RESTORED f08ce32c；先 V_BALLAST_MIX+对照；禁混叶38）
```

| 项 | 状态 |
|---|---|
| 本 PREREG_FROZEN | **本文件** |
| 申 `.ok` / X2 / Book-Smoke / QUIET | **禁**（等主/Arch） |
| 主候选 | **`V_BALLAST_MIX`** stock=0.50 / core·510300=0.50 |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 对照臂 | stock∈{0.40, 0.60}（事先） |
| mid_large 主口径 | **false** |
| EXECUTED / live / promotion / ok_requested | false / false / false / false |
| 叶38 | **旁线不混**（`c01c2034`） |

---

## 10. 禁项清单（再钉）

- 禁自开 Eng X2 / Book-Smoke；禁自签 fund `.ok`；禁挂 `RESEARCH_QUIET.lock`
- 禁读收益冒充过闸；禁事后改阈 / 翻主候选优先级
- 禁混叶38；禁改 WHO/ALLA 事件条款区；禁改原 FROZEN `303e0185` 字节
- 禁 mid_large 主口径；禁 RESTORED `f08ce32c`；禁抬 rss 意向 1500；禁 git commit
- live=`false`；promotion=`false`；leo_notify=`false`；EXECUTED=`false`；≠X2 ACCEPT；≠Book-Smoke ACCEPT；≠本票 ACCEPT

---

## 11. 冻结钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_20261027_ZH.md` |
| RECEIPT | `docs/v2/audit/AI_FUND_PORTFOLIO_MDD_CUT_PREREG_FROZEN_RECEIPT_20261027_ZH.md` |
| 状态 | **PREREG_FROZEN**（≠ `.ok`；≠ BS/X2/本票 ACCEPT） |
| 源 DRAFT / RECEIPT | `eeccb25e` / `2bf42d4b` |
| Arch DRAFT 审 | **`41d4fc76` PASS_WC MATCH**（文内 `eee21297` 勿采） |
| 主候选 | **`V_BALLAST_MIX`** sleeves stock=**0.50** / core·510300=**0.50** |
| 备选 | `V_NAME_CAP` → `V_SAT_ON_TRUNK` |
| 对照臂 | stock∈{0.40, 0.60}（事先；与 0.50 共 3 臂） |
| 六变体 | V_BALLAST_MIX / V_NAME_CAP / V_HOLD_GATE / V_IND_SIZE / V_SAT_ON_TRUNK / V_VOL_SCALE（阈冻结不得改） |
| 事件 / 池 | dark_horse_add；ALLA；mask **`6ab6a305`**；mid_large=**false** |
| 原 FROZEN | `303e0185` / ArchFROZEN `bcbe4b72`（字节未改） |
| Eng/Arch BS | `b013a7a8` / `694b9a80` / `3e2a9b9c` |
| WHO/ALLA/C2 | `547b246e` / `724e1df5` / `81afda13` |
| 叶38 | `c01c2034` 旁线不混 |
| 禁 RESTORED | `f08ce32c` |
| live / promotion / ok_requested / EXECUTED | false / false / false / false |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
