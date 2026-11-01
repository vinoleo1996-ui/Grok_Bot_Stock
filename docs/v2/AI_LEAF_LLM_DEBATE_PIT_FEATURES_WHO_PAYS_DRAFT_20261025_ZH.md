# 【叶28 · 文档冻结交接面】LLM 多空辩论 → PIT 事件/情绪特征 who_pays / 预注册草案

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-25 ~11:46–11:50 ET（America/New_York；箱 `date`）初稿；**修订 ~12:00 ET**（P0×5 补丁）；**残留钉 ~2026-10-25 12:07 ET**（P1-3/P1-5 一句 + 叶号28）
- **状态=DOCUMENT_INTERFACE_FROZEN**（文档级交接面冻结；**非**叶级 ACCEPT / **非**预注册 FROZEN / **不**申 `.ok`）。主排号 **叶28**（令文 `docs/v2/audit/MAIN_LEAF28_29_WHO_PAYS_QUEUE_20261025_ZH.md`）。
- 来源：Leo（经主 Agent ~11:45 ET）纠正——AlphaLens / TradingAgents 路线「LLM 多空辩论」**开放为研究叶**，但边界收窄为 **只产 PIT 结构化特征**。
- 机制参考（只读、不抄禁项）：`docs/v2/TRADINGAGENTS_DEEP_READ_ZH.md`（角色分离、as_of/coverage_gap、settlement≠NAV、禁 Yahoo 主路径、禁用决策网格冒充 Book-Smoke）。
- 吸收对照：`docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` A4 证据政策 → Intel；本叶特征须可被证据政策映射。
- 证据政策权威：`docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md`（sha8 **7a265b8e…**）；本 DRAFT **不另起** SourceType 权重表。
- **禁**：LLM **直接**输出买卖权重或当下单 α；本叶申 `.ok` 开实盘/纸面下单；git commit；接 Yahoo/Reddit/StockTwits 主路径；把 hit_rate 决策网格写入 Strategy 密封目录。
- **不挡**：叶25 mem_probe / 叶25 r6 FROZEN 审阅（本修订为文档并行）。
- `live=false`；`promotion_approved=false`；`research_only=true`。

### 修订说明（相对初稿）

| 项 | 值 |
|---|---|
| 触发 | Intel 共审回执 `docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REVIEW_20261025_ZH.md` |
| 回执全文 sha256 | `52e394ff38bdd57bdef4a5ea50f9b2e2227a01da9e0ca875392e0c0c3e66c9fa`（sha8 **52e394ff**） |
| 初稿全文 sha256 | `b57a75f37b555eaf473f8b2833ab4f8db2cb6f01a4246c8e5eb7835f9b2edac5`（sha8 **b57a75f3**） |
| 结论前态 | 有条件可对齐 → 本修订补 **P0×5** + 建议 **P1-1** |
| 本修订范围 | 仅扩 §3（证据卡子表 / gaps / SourceType / dedupe / 五级净分交接）+ §6 验收句；**不**改文件名；**不**申 `.ok`；**不**实跑；**不** git commit |
| P0-5 钉法 | **选项 B**：本叶只出 `bull_score`/`bear_score`/`disagreement_score`；五级 `sentiment_net`/`sentiment_rating` 由 Intel `balance`/`rating_from_balance` 另算，本叶不替代 |


### 修订说明（相对 P0×5 · 叶28 残留钉）

| 项 | 值 |
|---|---|
| 触发 | 主排号叶28 + Intel 复核 `655e6ef0…`（残留 P1-3/P1-5 可排号后补一句） |
| Intel 复核 sha8 | `655e6ef0`（`docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REREVIEW_20261025_ZH.md`） |
| 前序全文 sha256 | `a18bb8e6351754b69b88c8ff8ac68af84407f9220ba96e5d44414a74ca820b2e`（sha8 **a18bb8e6**） |
| 本修订范围 | 仅钉 **P1-3**（scope=instrument）+ **P1-5**（拥挤/日历另页）+ 叶号28 文档冻结戳；**不**改 schema 列集；**不**申 `.ok`；**不**实跑 |
---

## 0. Alpha 空位填写（交主排号用）

> **mechanism_tag（拟）**：`g1g5_ashare_llm_debate_pit_features_v1`（**未排号**）  
> **who_pays（假说级一句）**：付钱的是在信息冲击与意见分歧上反应不足或过度拥挤的对手盘——当 PIT 可得的公告/舆情/结构化多空分歧特征（非 LLM 权重）经后续**残差工厂另叶**消费后，若分歧极端或冲击未即时反映于价，则下一窗特质收益可检验；**本叶本身不声称可交易 α，不产出下单权重**。  
> **本叶产出**：PIT 特征表 / JSONL 事件行（见 §3 schema）+ 证据卡子表行；进 **Intel 台账 / 叶台账**交接面。  
> **明确不产出**：`session,instrument,weight`；五档评级当成交；PM「买入」自然语言当 α；**不**产出可直接下单的 `sentiment_rating` 权重。  
> **失效条件**：任何路径让 LLM 分数/评级直接进 Book-Smoke 或纸面权重；无 `available_at`/`as_of` 的伪 PIT；用 `retrieved_at`/`fetched_at` 冒充 `available_at`；社媒未归档却当严格历史特征；用决策 hit_rate 冒充 NAV 过门；把 `gaps[]` 写入 `bear_score` / 风险扣分。  
> **交下游时点**：主排号 → Arch/Intel 审 schema → Data 确认本地源 PIT → 特征落盘契约冻结 → **另叶**（残差工厂消费者）再写 who_pays/预注册；本叶始终是特征叶。

---

## 1. 机制边界（谁付钱 · 假说级）

| # | 假说 | 本叶角色 | 消费方 |
|---|---|---|---|
| H1 信息冲击 | 公告/研报级事件的结构化冲击强度对后续收益有增量 | 只抽 PIT 字段（类型、极性、强度、源权） | 另叶：事件残差 α |
| H2 意见分歧 | Bull⇄Bear 结构化分歧度（非胜负叙事）可交易 | 候选：`disagreement_score`、轮次、是否僵局 | 另叶：分歧截面残差 |
| H3 证据充分度 | 「资料缺口≠反证」（证据政策）改变有效样本 | 标记 `coverage_gap` / `evidence_adequacy` / 独立 `gaps[]` | Intel + 消费者叶过滤 |

**TradingAgents 可借鉴（参考深读 §4.1）**：角色分离、schema 输出、as_of 夹紧、coverage_gap、settlement 与决策质量分轨。  
**明确不抄**：Yahoo 工具链；Reddit/StockTwits；把 rating×事后 α 网格当组合回测；无 `promotion` 门控的「年化好看」。

---

## 2. 交接面（Intel / 叶台账；本叶不下单）

```
[本地 PIT 源: 公告/面板/S1 舆情…]
        → 辩论 runner（顺序/并行任务近似即可，不强制搬 LangGraph）
        → 本叶：结构化特征行（parquet/JSONL）+ 证据卡子表
        → Intel：证据政策映射 + balance/五级净分 + 台账索引（as_of 可查询）
        → 叶台账：登记 mechanism_tag / 特征版本 sha / 覆盖缺口
        → 【另叶】残差工厂读特征 → base-α → Gate B / GATE_V3
        → Strategy / Book-Smoke   【本叶禁止直连】
```

已有桩（勿重复造轮；路径以深读 §5 为准）：

- `quantlab/intel/debate_ledger.py` — TypedDict + JSONL  
- `quantlab/intel/asof_window.py` — as_of / coverage_gap  
- `research/ai_debate_memory_runner.py` — dry-run / 510300 settle（**settle 仅决策质量，非本叶 α**）

---

## 3. PIT 特征 schema 草案（字段 + 时间戳规则）

### 3.1 主键与时间

| 字段 | 类型 | 规则 |
|---|---|---|
| `feature_version` | str | 本 schema 语义版本；变字段必升版 |
| `mechanism_tag` | str | 固定拟名至主排号后改钉 |
| `trade_session` | date | SSE 开市日；信号会话 |
| `instrument_id` | str | 与 panel 一致（`ts_code` 或 Eng 映射表终钉后统一） |
| `as_of_ts` | datetime | 特征**可用来做决策**的时刻（Asia/Shanghai）；须 ≥ 所有源 `available_at` |
| `available_at` | datetime | 本行特征对外可消费时刻；默认 = `as_of_ts`；回填禁止改历史 `available_at` |
| `source_max_available_at` | datetime | 行内所依赖源的最大 `available_at`；若 > 声称的 `as_of_ts` → **拒写** |
| `retrieved_at` / `fetched_at` | datetime | **抓取时刻**（P1-1）；**禁止**冒充 `available_at`；可与 `available_at` 并存但语义分轨 |
| `coverage_status` | enum | `ok` / `coverage_gap` / `withheld` / `partial`（与 `gaps[]` 并存，不替代） |

### 3.2 事件/情绪结构化字段（LLM 只填这些，不填权重）

| 字段 | 类型 | 说明 |
|---|---|---|
| `event_type` | str | 如 earnings / contract / buyback / regulatory / sentiment_burst / other；未知 → `other`+披露 |
| `event_polarity` | float | [-1,1]；空=未知（不得当 0） |
| `event_intensity` | float | [0,1] |
| `bull_score` / `bear_score` | float | [0,1]；来自结构化辩论轮，非自然语言摘录冒充 |
| `disagreement_score` | float | 如 `|bull-bear|` 或 1−同意度；公式冻结时钉 |
| `debate_rounds` | int | 完成轮次 |
| `stance_stalemate` | bool | 是否僵局/REVIEW（对照深读 REVIEW 哨兵思想） |
| `evidence_adequacy` | float | [0,1]；映射政策 `sufficiency`（同义别名；权威名见政策 V1） |
| `source_weight_sum` | float | 来源分权合计（**经 dedupe_key 转载去重后**；权重表引用政策 V1 §3，不另起） |
| `independent_n` | int | 去重后独立 publisher 数（见 §3.5）；同稿/同 publisher **不算**多源独立 |
| `gaps` / `gap_flags` | list[str] | **独立缺口字段**（见 §3.4）；禁止写入 `bear_score` / 风险扣分 |
| `evidence_card_ids` | list[str] | 外键 → §3.3 证据卡子表 `evidence_id`（可空列表=无链则 `coverage_status=withheld` 或 `coverage_gap`） |
| `news_context_ref` | str | 可选；指向研究报告/证据卡 id；**非**全文进特征表（news_context 全字段由证据卡 JSON 承载） |
| `llm_model_id` | str | 模型/提示词版本 id；缺省则行级 `withheld` |
| `prompt_sha256` | str | 提示词束哈希 |
| `raw_decision_rating` | str | **可选审计列**；若存在，消费者叶 **禁止** 映射为 weight/α；主表导出默认 drop |

#### P0-5 钉死：五级净分交接（选项 B）

- **本叶只出** `bull_score` / `bear_score` / `disagreement_score`（及辩论元数据）。  
- **不**在本叶主表产出 `sentiment_net` / `sentiment_rating`（强多/偏多/中性/偏空/强空）。  
- 五级信息面标签由 **Intel** 证据包 `balance` → `rating_from_balance` **另算**（政策 V1 §6 / §8）；本叶**不替代**、不把辩论胜负写成五级、更不写成下单权重。  
- 消费者叶若需五级：读 Intel 台账/证据包字段，**禁止**把本叶 `bull`/`bear` 私自映射为 weight/α。

### 3.3 证据卡子表（P0-1：证据链列）

特征行通过 `evidence_card_ids[]` 外键挂接。单条证据卡（一行一证）字段对齐政策 V1 §8：

| 字段 | 类型 | 口径 |
|---|---|---|
| `evidence_id` | str | 短 hex / 稳定键 |
| `source_type` | enum | **DISCLOSURE / DATA / REPORT / KOL / INFERENCE**（见 §3.5；权重表=政策 V1 §3） |
| `publisher` | str | 独立源计数用 |
| `url` | str | 可检查出处 |
| `published_at` | datetime | 原文发布时间（带时区） |
| `retrieved_at` | datetime | 抓取时刻；**禁**冒充 `available_at`（P1-1） |
| `available_at` | datetime | 该证 PIT 可知时刻（严格） |
| `traceability` | enum | FULL / LIMITED / INSUFFICIENT |
| `supports_fact` | bool | 规则见 §3.5；KOL/INFERENCE **永不**升事实 |
| `caliber` | str | 可选；财报/业绩类事件**强制**（如 `2026Q3/同比/归母`） |
| `impact` | enum | bull / bear / mixed / neutral |
| `strength` | float | [0,1] |
| `weighted_score` | float | `strength × SOURCE_WEIGHT × TRACE_WEIGHT`（权重权威=政策 V1） |
| `dedupe_key` | str | 转载合并键；缺省 `title.strip()` |
| `independent_n` | int | 可选冗余；包级以特征行 `independent_n` 为准 |
| `news_context` | object/str | 媒体/链接/时间/内容状态/有界摘录（特征行只存 ref） |

**关系**：1 特征行 : N 证据卡；无卡不得伪称「充分」；聚合 `source_weight_sum` / `evidence_adequacy` 必须可自子表复算（允许浮点容差披露）。

### 3.4 独立 `gaps[]`（P0-2）

| 项 | 钉 |
|---|---|
| 字段名 | `gaps: list[str]`（别名 `gap_flags` 可并存一版） |
| 存放 | **特征行级**独立列；**不得**并入 `bear_score` / `event_polarity` / `evidence_adequacy` 数值 |
| 语义 | 抓取失败、缺正文、源不可用、常规「未经审计」声明等 → **资料限制**，不是经营恶化 |
| **验收句（硬）** | **禁止将 `gaps[]` / `gap_flags` 写入 `bear_score`、风险扣分、减仓理由或 NEW_HIGH 升空依据**（对齐政策 V1 §2.6 / §7） |
| 与 `coverage_status` | 并存：`coverage_status=coverage_gap` 时 `gaps` 应非空；`gaps` 非空不自动改写 `bear_score` |

### 3.5 SourceType / supports_fact / dedupe（P0-3 · P0-4）

**SourceType 五类**（枚举钉死；**权重数字以政策 V1 §3 表为准，本叶不另起权重表**）：

| SourceType | 可否 `supports_fact`（另须 traceability） |
|---|---|
| DISCLOSURE | 是（且 `traceability ∈ {FULL, LIMITED}`） |
| DATA | 是（同上） |
| REPORT | 是（同上） |
| KOL | **否**（永不升级为事实） |
| INFERENCE | **否** |

**`supports_fact` 规则**（引用政策，不改写）：

```
supports_fact = source_type ∈ {DISCLOSURE, DATA, REPORT}
                ∧ traceability ∈ {FULL, LIMITED}
```

KOL/INFERENCE 可进低权信息面方向加权，**不得**单独支撑「核心事实充分」，**不得**计入 `independent_n` 的事实源。

**`dedupe_key` + `independent_n`（P0-4）**：

1. 键：`dedupe_key`；缺省 `title.strip()`。  
2. 同键合并：保留 `weighted_score` 最高者（通稿/转载**不算**多源独立）。  
3. 再按 `publisher`（缺省回退 `url`/`id`）去重计数 → `independent_n`。  
4. **同稿或同 publisher 多条 ≠ 多源独立验证**（政策 V1 §4–§5）。  
5. 特征行 `source_weight_sum` 必须在上述去重之后汇总。

### 3.6 硬禁字段（出现即 schema 违规）

- `weight` / `target_position` / `alpha` / `order_side` / `lots`  
- 任何「建议仓位%」「可执行交易计划」数值列进本叶主表  
- 无 `available_at` 的社媒原始抓取冒充历史 PIT  
- 用 `retrieved_at` / `fetched_at` 填入或冒充 `available_at`（P1-1）  
- 本叶主表私自写入 `sentiment_rating` 并映射为下单/权重（违背 P0-5 选项 B）  
- 将 `gaps[]` 写入 `bear_score` / 风险扣分

### 3.7 残留钉（P1-3 · P1-5；主排号后一句）

- **P1-3（scope）**：本叶 `scope` **固定为 `instrument`**（标的级特征行）；**不做**跨板块 `shared` 折价 0.5；行业/板块聚合若需要，由 Intel `balance` 层或消费者另叶处理，**不**进本 schema。
- **P1-5（拥挤/日历）**：政策 V1 §9.1 拥挤度与财报日历辅助字段 **不在本叶 schema**；声明走 **另页**——拥挤 → ETF_FLOW / 资金流候选叶；日历 → 财报日历/事件日历候选；本叶 who_pays 假说句中的「过度拥挤」仅为机制叙述，**非**本表列。

---

## 4. 残差工厂如何另叶消费（本叶只定义接口）

1. 消费者叶按 `as_of_ts ≤ 决策会话` 左连接特征。  
2. 截面：SW L1 + style（logmv/β/mom/vol/ADV）对 `disagreement_score` / `event_intensity×polarity` 等残差。  
3. 判决宇宙 HI_LIQ；FULLA 披露。  
4. Gate B / GATE_V3 走消费者叶的预注册——**不**在本叶申请。  
5. `coverage_gap` / 非空 `gaps[]` 行：默认不进 α（或进单独敏感性），**禁止**把缺口当反向信号（证据政策）。  
6. 若需五级净分：读 Intel `sentiment_*`，**不**把本叶 bull/bear 当 weight。

---

## 5. 数据与 GAP（不读生产收益；不编造）

| 源 | 状态 | 备注 |
|---|---|---|
| 本地公告 / messages loader | 部分 | 深读 G1；须 `available_at≤asof`；抓取失败进 `gaps[]` |
| S1 舆情（A 股） | **GAP** 风险 | 未齐则 sentiment 角色强制 `coverage_gap`；禁 Reddit/StockTwits |
| 财报 filing 公开日 | 部分/G12 | 禁用报告期冒充公开日；`caliber` 强制 |
| Yahoo / yfinance | **禁** | 深读 §3.5 |
| LLM API 密钥/采样 | 运行时依赖 | 无钥时只跑规则模板特征，禁止空话冒充辩论分 |

---

## 6. 验收（特征叶；非 α 叶）

- Schema 校验：无禁字段；时间戳单调；`source_max_available_at ≤ as_of_ts`。  
- **P1-1**：`retrieved_at`/`fetched_at` ≠ `available_at` 语义；验收句「**fetched≠available**」——抓取时刻不得写入 `available_at`。  
- **P0-1**：凡声称有证据支撑的特征行，`evidence_card_ids` 非空且子表含 §3.3 全列（或显式 `withheld`）。  
- **P0-2**：`gaps[]` 独立；**禁止写入 bear_score / 风险扣分**。  
- **P0-3**：`source_type` ∈ 五类；`supports_fact` 符合公式；KOL/INFERENCE 永不升事实。  
- **P0-4**：存在 `dedupe_key`；`independent_n` 按 publisher 去重；同稿不计多源。  
- **P0-5**：主表无本叶自算 `sentiment_rating`；五级仅来自 Intel balance（选项 B）。  
- **P1-3**：本叶 scope 固定 `instrument`；无 shared 折价列；跨板块折价不在本叶。
- **P1-5**：拥挤/日历字段不在本 schema；另页 ETF_FLOW / 财报日历候选。
- 重放：同 `prompt_sha256`+源快照 → 特征行字节级或允许的温度披露（非确定性须在 meta 声明，不得当严格 PIT α）。  
- Intel 可按 `(trade_session, instrument_id)` 检索。  
- 台账有版本 sha；**无** Book-Smoke 直连。  
- 决策质量网格若跑：只写 `output/intel/decision_quality_*`，文案强制「非 NAV」。  
- `raw_decision_rating`：主表导出默认 drop。

---

## 7. 待主排号清单

| # | 项 | Owner 建议 |
|---|---|---|
| 1 | 正式叶号 | **已钉叶28**（主令 `MAIN_LEAF28_29_WHO_PAYS_QUEUE_20261025_ZH.md`） |
| 2 | Intel 复核 P0×5 | **7/7 PASS** `655e6ef0`；残留 P1-3/P1-5 本修订已钉 |
| 3 | Arch 契约：禁字段闸、sha 清单、与 runner 输出对齐 | Arch |
| 4 | Data：公告/S1/`available_at` 覆盖与 GAP 记账；fetched≠available | Data |
| 5 | Eng：instrument_id 映射表终钉（深读 G11） | Eng |
| 6 | 消费者叶（残差工厂）另开 who_pays 的排号与排窗 | 主 |
| 7 | 本叶不申 `.ok` 实跑辩论；若需 dry-run 另窗另签 | 主 + Arch |

---

## 8. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF_LLM_DEBATE_PIT_FEATURES_WHO_PAYS_DRAFT_20261025_ZH.md`（**未改名**） |
| 状态 | **DOCUMENT_INTERFACE_FROZEN**（叶28）；非叶级 ACCEPT；不申 `.ok` |
| 初稿 sha256 | `b57a75f37b555eaf473f8b2833ab4f8db2cb6f01a4246c8e5eb7835f9b2edac5` |
| P0×5 修订 sha256 | `a18bb8e6351754b69b88c8ff8ac68af84407f9220ba96e5d44414a74ca820b2e` |
| Intel 共审 sha256 | `52e394ff38bdd57bdef4a5ea50f9b2e2227a01da9e0ca875392e0c0c3e66c9fa` |
| Intel 复核 sha8 | `655e6ef0` |
| 证据政策 sha8 | `7a265b8e` |
| live | false |
| promotion_approved | false |
| 本回合动作 | 叶28 钉号 + P1-3/P1-5 一句 + 文档级冻结戳；**未**申 `.ok`；**未**开跑；**未**实跑；**未** git commit |

**本文件正文 sha256**（不含本行）：`229c5d1bc2552b4491a92eeb7a6dabbc7df7f61a01e661f431497ecc458b54a3`（sha8 **229c5d1b**）。
