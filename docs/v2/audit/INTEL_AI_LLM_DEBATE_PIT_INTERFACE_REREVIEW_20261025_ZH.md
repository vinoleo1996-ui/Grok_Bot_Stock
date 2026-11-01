# Intel ↔ AI：LLM 多空辩论 PIT 特征接口 · P0×5 复核回执

| 项 | 值 |
|---|---|
| 时点 | **2026-10-25 12:02 ET**（America/New_York；箱 `date`） |
| 审方 | QuantLab **Intel** |
| 任务 | AI 补丁后勾选复核（**不代改** DRAFT）；对照共审 `52e394ff` × 政策 `7a265b8e` |
| AI DRAFT（修订） | `docs/v2/AI_LEAF_LLM_DEBATE_PIT_FEATURES_WHO_PAYS_DRAFT_20261025_ZH.md` |
| DRAFT 修订后 sha256 | `a18bb8e6351754b69b88c8ff8ac68af84407f9220ba96e5d44414a74ca820b2e`（sha8 **a18bb8e6**；全长核验 **MATCH**） |
| 初稿 sha256 | `b57a75f37b555eaf473f8b2833ab4f8db2cb6f01a4246c8e5eb7835f9b2edac5`（sha8 **b57a75f3**） |
| AI 补丁回执 | `docs/v2/audit/AI_LEAF_LLM_DEBATE_PIT_P0x5_PATCH_RECEIPT_20261025_ZH.md` |
| 补丁回执 sha256 | `e650af1b9bf4dec673e91b189aafe296dadc6c644e92eeb0933cf234d37e5867`（sha8 **e650af1b**；**MATCH**） |
| 共审回执 | `docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REVIEW_20261025_ZH.md` |
| 共审 sha256 | `52e394ff38bdd57bdef4a5ea50f9b2e2227a01da9e0ca875392e0c0c3e66c9fa`（sha8 **52e394ff**；**MATCH**） |
| 证据政策 V1 | `docs/v2/INTEL_EVIDENCE_POLICY_V1_ZH.md` |
| 政策 sha256 | `7a265b8eb36c2d008a193841754f69aee0802b2d5dc781174b4d4764d1b7d172`（sha8 **7a265b8e**；**MATCH**） |
| 范围 | **只文档勾选**；未改 AI DRAFT；未改代码；未跑 `intel_run`；不挡叶25 mem_probe；`live=false` |
| **结论** | **接口可对齐 / 可冻结交接面（文档级）** |

**一句话**：P0×5 + P1-1 勾选全 PASS；选项 B（五级由 Intel `balance` 另算）已钉死；红线维持；**仍非叶级 ACCEPT、不申 `.ok`、`live=false`**。

---

## 1. 勾选表（PASS / FAIL）

| # | 要求 | 判定 | 证据（小节 / 短引） |
|---|---|---|---|
| **P0-1** | 证据卡子表 + `evidence_card_ids`（覆盖政策 §8 证据链列） | **PASS** | §3.2 `evidence_card_ids`；**§3.3** 子表含 `evidence_id`/`source_type`/`publisher`/`url`/`published_at`/`retrieved_at`/`available_at`/`traceability`/`supports_fact`/`caliber`/`impact`/`strength`/`weighted_score`/`dedupe_key`/`independent_n`/`news_context`；§6「凡声称有证据支撑…`evidence_card_ids` 非空」 |
| **P0-2** | 独立 `gaps[]` + 禁写入 bear_score / 风险扣分 | **PASS** | **§3.4** 独立列；验收句硬钉「禁止将 `gaps[]`/`gap_flags` 写入 `bear_score`、风险扣分…」；§3.2、§3.6、§6 同句 |
| **P0-3** | SourceType 五类 + `supports_fact`；权重引 V1 | **PASS** | **§3.5** DISCLOSURE/DATA/REPORT/KOL/INFERENCE；`supports_fact` 公式与政策一致；文首+§3.5「权重数字以政策 V1 §3 表为准，本叶不另起权重表」 |
| **P0-4** | `dedupe_key` + `independent_n`（同稿/同 publisher 不算多源） | **PASS** | **§3.5** 步骤 1–5；§3.2 `independent_n`；§3.3 `dedupe_key`；明文「同稿或同 publisher 多条 ≠ 多源独立验证」 |
| **P0-5 选项B** | 五级 `sentiment_net`/`sentiment_rating` 由 Intel `balance` 另算；本叶不替代 | **PASS** | 修订说明钉「选项 B」；**§3.2「P0-5 钉死」**：本叶只出 bull/bear/disagreement；五级由 Intel `balance`→`rating_from_balance` 另算、**不替代**；§3.6/§6 禁本叶自算 `sentiment_rating` |
| **P1-1** | `retrieved_at`/`fetched_at` 存在且 fetched≠available | **PASS** | §3.1 增列；§3.3 子表列；§3.6 硬禁；§6 验收「**fetched≠available**」 |
| **红线** | 仍禁 LLM 买卖权重 / 下单 α | **PASS** | §0「禁：LLM **直接**输出买卖权重或当下单 α」；§3.6 硬禁 `weight`/`target_position`/`alpha`/`order_side`/`lots`；§4/§6 禁直连 Book-Smoke |

**勾选汇总**：7/7 **PASS**（P0×5 + P1-1 + 红线）。

---

## 2. 结论

| 项 | 值 |
|---|---|
| 接口对齐 | **可对齐** |
| 交接面冻结 | **可冻结（文档级）**——schema/禁字段/五级交接/证据链外键已齐 |
| 叶级 ACCEPT | **否**（本回执仅接口复核） |
| 申 `.ok` / 实跑 | **否** |
| `live` | **false** |
| 不挡叶25 mem_probe | **是** |

相对共审 `52e394ff` 前态「有条件可对齐」：P0×5 已闭合 → 升级为 **可对齐 / 可冻结交接面（文档级）**。

---

## 3. 残留 P1（不挡文档级冻结）

| # | 项 | 现状 | 是否挡冻结 |
|---|---|---|---|
| P1-2 | `caliber` | §3.3 已有（可选；财报/业绩类强制）——**基本闭合** | 否 |
| P1-3 | `scope` / `sectors` / shared 折价 0.5 | 本叶未声明「scope 固定 instrument」 | **否**（建议排号前加一句；Intel balance 层可兜） |
| P1-4 | `news_context` 全字段 | §3.3 子表已承载 `news_context`；特征行只存 ref——**基本闭合** | 否 |
| P1-5 | 拥挤 / 日历 | 未在 schema 列；who_pays 假说句提及拥挤但未钉「另页」 | **否**（建议加一句走 ETF_FLOW / 财报日历候选；不挡冻结） |
| P2 | `evidence_adequacy`↔`sufficiency` 别名等 | 仍有同义别名；非阻塞 | 否 |

残留 P1 **不挡**文档级冻结交接面；主排号 / Arch 契约时可顺手钉 P1-3/P1-5 一句。

---

## 4. 给主 Agent / AI

- **给主 Agent**：P0×5+P1-1 勾选全 PASS；接口结论升级为 **可对齐 / 可冻结交接面（文档级）**（DRAFT sha `a18bb8e6…` × 政策 `7a265b8e`）；仍非叶级 ACCEPT、不申 `.ok`；可进入排号 + Arch 契约审；残留 P1-3/P1-5（scope 声明、拥挤/日历另页）不挡冻结。`live=false`。
- **给 AI**：复核 **全 PASS**；P0-5 选项 B 钉法认可；无需再改本 DRAFT 即可等主排号；残留 P1-3/P1-5 可排号后补一句；红线维持；**不挡**叶25 mem_probe。本席未代改你的 DRAFT。

---

## 5. 落盘钉

| 项 | 值 |
|---|---|
| 本回执路径 | `docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REREVIEW_20261025_ZH.md` |
| TEAM_STATE bak | `output/loop/TEAM_STATE_latest.md.bak_intel_debate_rereview_20261025_1202` |
| 本回合动作 | 只勾选复核 + 写回执 + 更新 `### Intel` 节首；**未**改 AI DRAFT；**未**改代码；**未**跑 intel_run |
| sha256 | 落盘后以 `sha256sum` 为准 |
