# Intel ↔ AI：LLM 多空辩论 PIT 特征接口共审回执

| 项 | 值 |
|---|---|
| 时点 | **2026-10-25 11:54 ET**（America/New_York；箱 `date`） |
| 审方 | QuantLab **Intel** |
| 任务 | 主 Agent 共审：AI who_pays DRAFT（叶 B）对照证据政策 V1 的 **PIT 接口**（非叶级 ACCEPT） |
| AI DRAFT | `docs/v2/AI_LEAF_LLM_DEBATE_PIT_FEATURES_WHO_PAYS_DRAFT_20261025_ZH.md` |
| AI DRAFT sha256 | `b57a75f37b555eaf473f8b2833ab4f8db2cb6f01a4246c8e5eb7835f9b2edac5`（前缀 **b57a75f3** 核验通过） |
| 证据政策 V1 | `docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md` |
| 政策 sha256 | `7a265b8eb36c2d008a193841754f69aee0802b2d5dc781174b4d4764d1b7d172`（sha8 **7a265b8e** 已核） |
| 范围 | **只文档**；不改代码、不跑 `intel_run`、不改 AI DRAFT 原文；`live=false` |
| **结论** | **有条件可对齐** |

**一句话**：边界与禁交易权重已对齐；schema 尚缺政策 §8 证据链/分权/去重/`gaps[]`/五级净分的一对一字段，补齐后即可冻结交接面。

---

## 1. MATCH 清单（已对齐）

| # | 点 | DRAFT 出处 | 政策出处 |
|---|---|---|---|
| M1 | **禁买卖指令 / 禁权重 / 禁 α 直出**；硬禁字段含 `weight`/`target_position`/`alpha`/`order_side`/`lots` | §0、§3.3、§8 草稿钉 | §1 禁抄项、§9.2、§11.3 |
| M2 | 本叶只产 **PIT 结构化特征**；消费方为另叶残差工厂；**禁**直连 Book-Smoke / 纸面 | §0、§2 交接面、§4 | §8 消费路径、§9.4 |
| M3 | **`available_at` / `as_of_ts` 纪律**；`source_max_available_at ≤ as_of_ts` 否则拒写；回填不改历史 `available_at` | §3.1 | §8 `available_at` 行、§9.2 |
| M4 | **资料缺口 ≠ 反向信号**；`coverage_gap` 默认不进 α / 禁止当反向 | §1 H3、§4.5 | §2.6、§7 专节 |
| M5 | 概念承认 **来源分权 + 转载去重后** 的权重合计（`source_weight_sum`） | §3.2 | §3、§5 |
| M6 | `evidence_adequacy` 明示映射 A4「充分度」 | §3.2 | §4 sufficiency |
| M7 | `news_context_ref` 指向证据卡 id、**非全文进特征表**（方向对） | §3.2 | §8 `news_context` |
| M8 | 分工：AI 做 who_pays / 叶预注册；Intel 做证据映射与台账；本叶不申 `.ok` 实跑 | §0、§2、§7 | §9.3 |
| M9 | `live=false` · `promotion_approved=false` · `research_only=true`；未改代码 | §0、§8 | §1、§11.5 |
| M10 | `event_polarity` 空=未知、**不得当 0**（避免把缺失当地空） | §3.2 | §7 精神（缺口≠反证） |

---

## 2. 缺口清单

### P0（冻结交接面前必须补）

| # | DRAFT 现状 | 应对齐政策 | 建议谁改 |
|---|---|---|---|
| P0-1 | §3 schema **无** `evidence_id` / `source_type` / `publisher` / `url` / `published_at` / `retrieved_at` / `traceability` / `supports_fact` / `caliber` / `impact` / `strength` / `weighted_score` / `independent_n`；仅有聚合后的 `evidence_adequacy` + `source_weight_sum` | §8 映射表全文；§9.1「证据链字段」为多空辩论交付形态硬要求 | **AI 改 DRAFT**（扩 schema 或声明「证据卡行」子表 + 特征行外键）；Intel 可补契约示例行，不代写叶稿 |
| P0-2 | **无** `gaps[]` / `gap_flags` 独立字段；只有 `coverage_status` enum（`ok`/`coverage_gap`/`withheld`/`partial`），未写清缺口不得进 bear / 风险扣分 | §2.6、§7、§8 `gaps[]` | **AI 改 DRAFT** 增 `gaps: list[str]`（或行级 `gap_flags`）+ 验收句「禁止写入 bear_score / 风险扣分」；Intel 在契约注释钉同句 |
| P0-3 | **未钉** SourceType 五类（DISCLOSURE/DATA/REPORT/KOL/INFERENCE）及 `supports_fact` 规则；`source_weight_sum` 未说明权重表与「KOL/INFERENCE 永不升事实」 | §3 来源分权表 + `supports_fact` 公式 | **双方**：AI 在 §3 引用政策权重表或嵌枚举；Intel 保持 V1 为权威，不在 DRAFT 另起权重 |
| P0-4 | **无** `dedupe_key`；未写「同稿/同 publisher 不算多源独立」；`source_weight_sum` 仅括号注「转载去重后」无算法 | §5 转载去重；§4 `independent_sources`（dedupe_key → publisher） | **AI 改 DRAFT** 增 `dedupe_key` + `independent_n`（或证明由证据卡层算完再汇总）；Intel 可给伪代码指针 |
| P0-5 | 有 `bull_score`/`bear_score`/`disagreement_score`，**无** `sentiment_net` / `sentiment_rating`（强多/偏多/中性/偏空/强空）及与 `balance`/`rating_from_balance` 的映射；也未声明五级=信息面标签非投资建议 | §6、§8 末行、§9.1 多空净分 | **AI 改 DRAFT**：或新增两字段并给映射公式，或显式写「本叶只出 bull/bear/disagreement，五级净分由 Intel 证据包 `balance` 另算、本叶不替代」——二选一须钉死 |

### P1（前视 / 口径风险）

| # | DRAFT 现状 | 应对齐政策 | 建议谁改 |
|---|---|---|---|
| P1-1 | schema **无** `retrieved_at` / `fetched_at`；仅有 `available_at`/`as_of_ts`/`source_max_available_at`。若 runner 用抓取时刻填 `available_at` → **前视** | §8：`retrieved_at`/`fetched_at` = 抓取时刻，**禁止**冒充 `available_at` | **AI 改 DRAFT** 增抓取时刻列 + 验收「fetched≠available」；Data 确认源侧 PIT |
| P1-2 | **无** `caliber`（期间/同比/归母等）；事件型 `event_type` 不能替代口径分离 | §2.4、§8 `caliber` | **AI 改 DRAFT**（事件行可选 `caliber`；财报类强制） |
| P1-3 | **无** `scope`（sector\|shared）/ `sectors`；跨板块 shared 折价 0.5 未提 | §5、§6 sector 模式 | **AI** 若做行业截面则补；若本叶仅标的级可写「scope 固定 instrument、不做 shared 折价」并让 Intel `balance` 层处理 |
| P1-4 | `news_context_ref` 仅为 id 指针；政策要的 `news_context`（媒体/链接/时间/内容状态/有界摘录）是否由证据卡承载未钉 | §8 `news_context` | **双方**：约定「特征行只存 ref；证据卡 JSON 必含 news_context 全字段」 |
| P1-5 | 政策 §9.1 **拥挤/日历**辅助字段本叶未列（可接受「另页」但须声明不在本 schema） | §9.1 | **AI** 加一句「拥挤/日历不在本叶，走 ETF_FLOW / 财报日历候选」；或 Intel 另页索引 |

### P2（命名 / 卫生）

| # | DRAFT 现状 | 应对齐政策 | 建议谁改 |
|---|---|---|---|
| P2-1 | `evidence_adequacy` ↔ 政策 `sufficiency`；`instrument_id` ↔ `instruments`；`coverage_status` ↔ `gaps[]` 语义重叠 | §8 命名 | **AI** 主名对齐政策（可保留别名列一版）或出对照表钉同义 |
| P2-2 | `raw_decision_rating` 可选审计列——DRAFT 已禁消费者映射为 weight/α；仍有泄漏风险 | §9.2、§11.3 | **AI** 保持可选+禁映射；验收加「主表导出默认 drop 该列」 |
| P2-3 | `llm_model_id` / `prompt_sha256` 为叶特有审计字段（政策无对应）——**允许多出**，建议保留 | — | 无需改；Arch 契约纳入 sha 清单即可 |

---

## 3. 字段对照表（DRAFT §3 ↔ 政策 §8）

| 政策字段（§8） | DRAFT 字段 | 状态 |
|---|---|---|
| `evidence_id` | — | **缺** |
| `source_type` | —（仅有聚合 `source_weight_sum`） | **缺** |
| `publisher` | — | **缺** |
| `url` | — | **缺** |
| `published_at` | — | **缺** |
| `retrieved_at` / `fetched_at` | — | **缺**（前视风险 P1-1） |
| `available_at` | `available_at`（+ `as_of_ts` / `source_max_available_at`） | **OK**（且加强） |
| `traceability` | — | **缺** |
| `sufficiency` | `evidence_adequacy` | **改名**（语义近；须钉同义或改名） |
| `independent_n` | — | **缺** |
| `impact` | —（有 `event_polarity` 近但不等于 bull\|bear\|mixed\|neutral） | **缺** / 部分近义 |
| `strength` | `event_intensity`（近；非 strength×SOURCE×TRACE） | **改名/拆分** |
| `weighted_score` | `source_weight_sum`（聚合，非单条） | **缺**单条；聚合另议 |
| `caliber` | — | **缺** |
| `dedupe_key` | — | **缺** |
| `scope` | — | **缺** |
| `sectors` | — | **缺** |
| `instruments` | `instrument_id`（单标的主键） | **OK**（粒度：行级单标 vs 列表） |
| `supports_fact` | — | **缺** |
| `gaps[]` / `gap_flags` | `coverage_status`（enum，非列表） | **缺**独立 gaps；status 可并存 |
| `news_context` | `news_context_ref` | **改名/降级为指针**（P1-4） |
| `sentiment_net` / `sentiment_rating` | `bull_score`/`bear_score`/`disagreement_score` | **缺**五级净分映射（P0-5） |
| （§9.1）拥挤/日历 | — | **缺**（可声明另页） |
| — | `feature_version` / `mechanism_tag` / `trade_session` / `debate_rounds` / `stance_stalemate` / `llm_model_id` / `prompt_sha256` / `raw_decision_rating` / `event_type` / `coverage_status` | **多出**（叶侧合理；非违规） |

---

## 4. 专题结论（任务 7 问）

| # | 问 | 结论 |
|---|---|---|
| 1 | PIT 字段覆盖 | 时间主键与情绪聚合字段有；**§8 证据链主体大量缺失** → 条件对齐 |
| 2 | 来源分权 | 口头承认分权；**无枚举/无 supports_fact** → P0-3 |
| 3 | 转载去重 | 括号提及；**无 dedupe_key / publisher 规则** → P0-4 |
| 4 | 资料缺口≠反证 | 原则对齐（H3、§4.5、polarity 空≠0）；**缺独立 `gaps[]`** → P0-2 |
| 5 | 多空辩论边界 | **对齐**：只产 PIT 特征，硬禁权重/下单 | 
| 6 | 分工越权 | **未越权**：不申 `.ok`、不直连 Strategy、who_pays 停在特征叶 | 
| 7 | available_at / fetched_at | `available_at` 纪律好；**缺 fetched_at 分离** → P1-1 |

---

## 5. 红线确认

| 红线 | 状态 |
|---|---|
| 禁交易权重 / 禁买卖指令 / 禁纸面 `target_weight` | **DRAFT 已写死**（§0、§3.3）；本审认同 |
| `live=false` | **双方** |
| 未改代码 / 未跑 `intel_run` / 未改 AI DRAFT 原文 | **本回合遵守** |
| 本回执非叶级 ACCEPT | **是**；仅接口共审 |

---

## 6. 给主 Agent / AI 的一句话

- **给主 Agent**：接口结论=**有条件可对齐**；红线与分工已合，**5 条 P0**（证据链字段、`gaps[]`、SourceType/supports_fact、dedupe/independent_n、五级净分映射）须 AI 改 DRAFT 后再请 Intel 复核 schema，方可排号冻结交接面；本席未改代码、`live=false`。
- **给 AI**：请在 who_pays DRAFT §3 扩（或挂证据卡子表）：补齐政策 §8 证据链列 + 独立 `gaps[]` + SourceType/`supports_fact` + `dedupe_key`/`independent_n` + `sentiment_net`/`sentiment_rating`（或明文放弃五级、改由 Intel `balance` 出）；并增 `retrieved_at`且禁冒充 `available_at`；**不要**把 `raw_decision_rating`/辩论胜负写成 weight。补完后喊 Intel 复核对表即可，无需本席代改你的 DRAFT。

---

## 7. 落盘钉

| 项 | 值 |
|---|---|
| 本回执路径 | `docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REVIEW_20261025_ZH.md` |
| TEAM_STATE bak | `output/loop/TEAM_STATE_latest.md.bak_intel_debate_review_20261025_1153` |
| 本回合动作 | 只审 + 写回执 + 更新 `### Intel` 节首；**未**改 AI DRAFT；**未**改代码；**未**跑 intel_run |
| sha256 | 落盘后以 `sha256sum` 为准 |
