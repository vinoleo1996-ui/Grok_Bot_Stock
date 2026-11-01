# QuantLab Intel 证据政策 V1（吸收 AlphaLens / WorkBuddy）

> **结论先行**：本政策把 AlphaLens/WorkBuddy 的来源分权、可追溯、转载去重、充分度、多空平衡与「资料缺口≠反证」吸收为 Intel 事件特征契约；证据与多空净分只进 **PIT 事件/情绪特征候选**，经 AI 叶 who_pays / Alpha 残差闸消费。**Intel 不下单、不改权重、不进纸面 `target_weight`。** `live=false` · `promotion=false`。

---

## 1. 元信息

| 项 | 值 |
|---|---|
| 版本 | **V1** |
| 日期 | **2026-10-25**（America/New_York，ET） |
| 作者 | QuantLab Intel |
| 状态 | **DRAFT / 研究级** |
| live | **false** |
| promotion_approved | **false** |
| 计划行 | `docs/v2/audit/MAIN_ALPHALENS_ABSORB_PLAN_20261025_ZH.md` **A4** |
| 箱内 refs | `docs/v2/refs/alphalens_workbuddy/evidence_models.py` · `evidence_policy.py` · `news_evidence_policy.md` |
| PIT 对照 | `docs/v2/INTEL_PIT_EVENT_FEATURE_CANDIDATES_ZH.md` · `output/intel/ETF_FLOW_PIT_CANDIDATES_latest.md` |
| 本回合范围 | **仅文档**；不改代码、不跑 `intel_run` / research 管道 / alert-ingest |

### 禁抄项（精确表述 · Leo 2026-10-25 纠正）

| 禁止 | 允许（研究级） |
|---|---|
| 把 **8 维技术打分**当主 alpha | — |
| **LLM 多空辩论下单**（辩论结论直接变买卖指令 / 改权重） | 把多空辩论沉淀为**可回测的 PIT 情绪/事件特征**（须 evidence 链 + 严格 `available_at`） |
| **当日股票池回测**（幸存者偏差） | 历史 PIT 窗内、与现有事件研究同一口径的回测（另签） |
| 移植 AlphaLens 全站 / NeoData / 服务端口 | 吸收证据政策字段与纪律到 Intel 契约 |

---

## 2. 核心纪律（吸收 models 顶部 6 条 + news_evidence_policy）

1. **来源类型分离**：公司披露 / 可复算数据 / 可追溯报道 / 第三方观点 / 系统推断——报道不得改标成公告原文。
2. **traceable ≠ 真实性认证**：可追溯只描述出处可检查性（媒体、链接、时间、非标题内容），不是媒体白名单，也不自动把有限/不足/观点/传闻升为充分。
3. **一条可靠报道只支持一个限定事实**；观点与传闻**永不**升级为事实。
4. **口径不得混用**：期间（如 2026Q3）、同比/环比、归母/扣非、单季/累计、金额与预测限定必须分开判断。
5. **转载同稿 ≠ 多源独立验证**（按 `dedupe_key` / title + publisher 去重）。
6. **资料缺口（抓取失败 / 缺正文）≠ 反证 / 扣分 / 减仓理由**；缺口进独立 `gaps[]`，禁止写入 bear 证据或风险扣分。

补充（news 政策）：

- 「公司披露某报告期利润区间」「未来经营展望」「消息解释股价」分别判断。
- 正式业绩预告/快报是公司披露；普通「未经审计、以定期报告为准」属**口径说明**，不单独构成反证。
- 检索失败 ≠ 新闻失实；历史报告不覆盖、不把旧「不足」强改为充分。

---

## 3. 来源分权 SourceType + 权重

对照 `SOURCE_WEIGHT`（`evidence_policy.py`）：

| SourceType | 中文 | SOURCE_WEIGHT | 可否 `supports_fact` |
|---|---|---|---|
| DISCLOSURE | 公司披露（公告/财报/预告） | **1.0** | 是（且 traceability ∈ FULL\|LIMITED） |
| DATA | 可复算数据（行情/K线/宏观读数） | **0.9** | 是（同上） |
| REPORT | 可追溯报道（有媒体、链接、时间） | **0.75** | 是（同上） |
| KOL | 第三方观点（大V/机构观点） | **0.25** | **否**（永不升级为事实） |
| INFERENCE | 系统推断 | **0.2** | **否** |

**规则**：`supports_fact = source_type ∈ {DISCLOSURE, DATA, REPORT} ∧ traceability ∈ {FULL, LIMITED}`。观点与推断永远不能作为事实依据；仍可进入信息面方向加权（低权重），但不得单独支撑「核心事实充分」。

---

## 4. 可追溯 Traceability 与充分度

| Traceability | 中文 | TRACE_WEIGHT | 含义 |
|---|---|---|---|
| FULL | 充分 | **1.0** | 有原文/完整口径/可复核 |
| LIMITED | 有限 | **0.6** | 仅标题/摘要或单一来源 |
| INSUFFICIENT | 不足 | **0.2** | 缺出处/无时间/传闻 |

**单条加权**：`weighted_score = strength × SOURCE_WEIGHT × TRACE_WEIGHT`（`strength` ∈ [0,1]）。

**包级充分度 `sufficiency(items)`**（仅计 `supports_fact`）：

| 级别 | 条件 |
|---|---|
| 充分 FULL | ≥ **2** 个**独立**可追溯来源，且至少一个 FULL |
| 有限 LIMITED | 恰好 1 个可追溯来源（FULL 或 LIMITED） |
| 不足 INSUFFICIENT | 无可用来源（仅观点/推断/传闻） |

**独立源计数**（`independent_sources`）：

1. 只保留 `supports_fact` 条目；
2. 按 `dedupe_key`（缺省用 `title.strip()`）合并，同键保留加权分最高者；
3. 再按 `publisher`（缺省 `url` / `id`）去重计数——**同一 publisher 多条不算独立确认**。

---

## 5. 转载去重

| 步骤 | 规则 |
|---|---|
| 键 | `dedupe_key`；缺省 `title.strip()` |
| 保留 | 同键取 `weighted_score`（或 balance 内同权函数）最高者 |
| 禁止 | 把通稿/转载计为多源独立验证 |
| 范围 | `scope=sector` 行业专属；`scope=shared` 宏观/政策类全板块共享（balance 时 shared 折价 **0.5**） |

---

## 6. 充分度与多空平衡（信息面标签，非投资建议）

`balance(pack, sector?)` → `{bull, bear, net, ratio, n_bull, n_bear}`：

- 去重后按 impact 累加加权分；sector 模式 = 行业专属 + shared（折价 0.5）。
- `rating_from_balance(net, total)` 五级（`score = net / max(total, ε)`）：

| 评级 | 条件 | 含义 |
|---|---|---|
| 强多 | score ≥ +0.35 | 加权证据显著偏多 |
| 偏多 | score ≥ +0.12 | 偏多 |
| 中性 | \|score\| < 0.12 或 total≤0 | 多空接近 / 无有效证据 |
| 偏空 | score ≤ −0.12 | 偏空 |
| 强空 | score ≤ −0.35 | 加权证据显著偏空 |

**明确**：五级是**信息面方向标签**，不是投资建议；**不进下单、不改权重、不进纸面 `target_weight`**。可映射为 PIT 情绪特征字段（见 §8 / §多空辩论节）。

---

## 7. 资料缺口 ≠ 反证（专节）

### 7.1 原则

- `EvidencePack.gaps: list[str]` **单独存储**；缺口**不得**进入 `bears()`、不得写入风险扣分、不得作为减仓/优化/NEW_HIGH 升空理由。
- 抓取失败、仅缺正文、常规「未经审计」声明 = **资料限制**，不是经营恶化证据。

### 7.2 缺口示例（进 `gaps[]` / `gap_flags`，不进 bear）

| 情形 | 正确处理 |
|---|---|
| 公告 URL 抓取失败 / 超时 | `gaps` 记「公告抓取失败」；不编造正文；不升空 |
| 仅有标题、缺正文或非标题摘录 | traceability≤有限；缺正文本身不进 bear |
| 业绩预告中的常规「未经审计、以定期报告为准」 | 口径说明；不单独反证/扣分/配置限制 |
| 一致预期库缺失、检索失败 | 数据缺口；≠ 新闻失实 |

### 7.3 仍保留的真实反证（可进 bear / 风险）

| 情形 | 说明 |
|---|---|
| 同口径数字冲突 | 两源对同一期间/口径数字不一致 |
| 官方否认 / 更正 / 预告下修 | 按实际披露影响评价 |
| 真实经营问题 | 亏损、下滑、集中度、现金流等——各自评价，不与缺口混写 |
| 异常核算或审计不确定性 | ≠ 普通「未经审计」声明 |

### 7.4 与 NEW_HIGH / ALERTS

周末轻量刷新与外盘例程：**NEW_HIGH 只看 high 预警变化**；**不因资料缺口升空或新开 high**。

---

## 8. 映射到 QuantLab PIT 事件特征字段（关键交付）

对照 `INTEL_PIT_EVENT_FEATURE_CANDIDATES_ZH`（`available_at` 严格；美东事件 → 下一 A 股可交易时）与 `ETF_FLOW_PIT_CANDIDATES`（`fetched_at` 禁冒充 `available_at`）。

| Evidence / 政策字段 | Intel PIT / 事件特征字段 | 口径说明 |
|---|---|---|
| `id` | `evidence_id` | 短 hex / 稳定键 |
| `source_type` | `source_type` | DISCLOSURE\|DATA\|REPORT\|KOL\|INFERENCE |
| `publisher` | `publisher` | 独立源计数用 |
| `url` | `url` | 可检查出处 |
| `published_at` | `published_at` | 原文发布时间（带时区） |
| `retrieved_at` | `retrieved_at` / `fetched_at` | **抓取时刻**；**禁止**冒充 `available_at` |
| （派生） | **`available_at`** | PIT 严格：信息可知时刻；美东事件 → 映射下一 SSE 可交易时（常用 t1 开盘前）；记清 tz |
| `traceability` | `traceability` | FULL\|LIMITED\|INSUFFICIENT |
| `sufficiency(...)` | `sufficiency` | 包/主题级充分度 |
| `independent_sources(...)` | `independent_n` | 去重后独立 publisher 数 |
| `impact` | `impact` | bull\|bear\|mixed\|neutral |
| `strength` | `strength` | [0,1] |
| `weighted_score(...)` | `weighted_score` | strength×SOURCE×TRACE |
| `caliber` | `caliber` | 口径字符串，如 `2026Q3/同比/归母` |
| `dedupe_key` | `dedupe_key` | 转载合并键 |
| `scope` | `scope` | sector\|shared |
| `sectors` | `sectors` | 申万一级（PIT） |
| `instruments` | `instruments` | 标的列表（研究标记） |
| `supports_fact` | `supports_fact` | bool |
| `EvidencePack.gaps` | **`gaps[]` / `gap_flags`** | **单独字段**；禁止写入 bear 或风险扣分 |
| （news 传递） | `news_context` | 媒体、链接、时间、内容状态、可追溯、有界摘录——避免压成裸 `news` 标签后降级 |
| `balance` / `rating_from_balance` | `sentiment_net` / `sentiment_rating` | 信息面多空净分与五级标签（研究特征，非下单） |

**消费路径（Intel 边界）**：

```
证据卡 / 多空净分 / 拥挤·日历字段
  → ALERTS / MACRO_EARNINGS_BRIEF / 事件特征候选（含 ETF_FLOW_PIT 类）
  → AI 叶 who_pays / 机制预注册
  → Alpha 残差·正交闸
  →（可选）event_study（另签后再跑）
Intel：只产特征与清单；不下单、不写 target_weight；promotion=false
```

---

## 9. 多空辩论 → PIT 情绪特征（Leo 2026-10-25 纠正）

TradingAgents / AlphaLens 式**多空辩论：可研究**。禁的是「辩论结论直接下单」，不是「辩论产出结构化特征」。

### 9.1 交付形态（Intel）

| 产出 | 说明 |
|---|---|
| 证据链字段 | §8 表：`evidence_id`、来源分权、traceability、caliber、dedupe、`supports_fact`、`gaps[]` 等 |
| 多空净分 | `balance` → `sentiment_net`（bull/bear/net/ratio）+ `sentiment_rating`（强多/偏多/中性/偏空/强空） |
| 拥挤 / 日历相关 | 与现有 ETF/资金流/事件日历候选对齐的辅助字段（如行业申赎确认、财报日历 asof）；细节另页，契约仍服从本政策的 evidence + `available_at` |

### 9.2 硬边界

- **不**输出买卖指令；**不**下单；**不**改权重；**不**进纸面 `target_weight`。
- 每条情绪/事件特征必须带 **evidence 链** + 严格 **`available_at`**（`fetched_at`/`retrieved_at` 不得冒充）。
- `live=false`；代码吸收另签 Arch `.ok`。

### 9.3 与 AI 分工

| 角色 | 职责 |
|---|---|
| **Intel** | 定特征契约与取数纪律（本政策 + PIT 字段映射）；产出 ALERTS/BRIEF/事件特征候选；维护 gaps≠反证 |
| **AI** | 叶预注册 / who_pays / 正交说明；消费 Intel 特征，不反向要求 Intel 下单 |
| **Alpha** | 残差·正交闸；promotion 仍 false 直至另裁 |

### 9.4 接线一句话

**多空净分 / 拥挤 / 日历 → 事件特征候选 → AI 叶**；Intel 停在特征契约，live=false。

---

## 10. 与现有 Intel 工件接线

| 工件 | 接线要点 |
|---|---|
| `output/intel/ALERTS_latest.md` / `.json` | 行业得分与 high/watch；证据政策约束「缺口不升空」；NEW_HIGH 只看 high 变化 |
| `MACRO_EARNINGS_BRIEF_latest.md` | 财报/宏观摘要携带 `news_context` 与口径；观点不升事实 |
| `ETF_FLOW_PIT_CANDIDATES_*` | 资金流类 PIT 候选；asof/`available_at` 纪律与本政策一致 |
| `event_study` / PIT 候选清单 | 证据充分度与独立源规则可作事件过滤；另签后再跑实数 |
| 周末轻量刷新 | 禁实数据重跑时仍可维护展示层；不因 gaps 改方向标签为强空 |
| 外盘例程 NEW_HIGH | 仅 high 预警变化触发推送逻辑；**不因缺口升空** |

---

## 11. 不做 / 红线

1. 不移植 AlphaLens 全站 / NeoData / 8722 类服务。
2. **不把资料缺口当空头证据**；不把观点/传闻当事实。
3. **不把 LLM 多空辩论结果直接下单或改权重**（辩论→PIT 特征见 §9，允许研究）。
4. 不把 8 维技术打分当主 alpha；不做当日池回测充当 OOS。
5. **不改 live**；本回合不改生产代码；代码吸收须另签 Arch `.ok`。
6. 不推 Leo（除非 NEW_HIGH 等既有推送契约触发——本任务无）。
7. 不启例程；不下单；不改权重。

---

## 12. 验收清单

| # | 项 | 状态 |
|---|---|---|
| 1 | 文档落盘 `docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md` | ☑ |
| 2 | 含「资料缺口≠反证」专节 | ☑ |
| 3 | PIT 字段映射表齐全（含 gaps / news_context / available_at） | ☑ |
| 4 | Leo 纠正：多空辩论→PIT 情绪特征专节 | ☑ |
| 5 | 禁抄表述已修正（禁下单，不禁特征） | ☑ |
| 6 | TEAM_STATE `### Intel` 节首更新 + bak | ☑ |
| 7 | 回执 `docs/v2/audit/INTEL_EVIDENCE_POLICY_V1_RECEIPT_20261025_ZH.md` | ☑ |
| 8 | 未改代码 / 未跑 intel_run / live=false | ☑ |

---

## 13. sha 说明

全文 sha256 与 sha8（前 8 位十六进制）在回执中记录：`docs/v2/audit/INTEL_EVIDENCE_POLICY_V1_RECEIPT_20261025_ZH.md`。计算方式：`sha256sum docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md`。
