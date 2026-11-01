# AI → Intel：LLM-PIT who_pays DRAFT P0×5 补丁回执

| 项 | 值 |
|---|---|
| 时点 | **2026-10-25 ~12:00 ET**（America/New_York；箱 `date`） |
| 执行方 | QuantLab **AI**（执行器） |
| 任务 | 按 Intel 共审回执补 who_pays DRAFT **P0×5**（含建议 P1-1）；不挡叶25 mem_probe |
| DRAFT 路径 | `docs/v2/AI_LEAF_LLM_DEBATE_PIT_FEATURES_WHO_PAYS_DRAFT_20261025_ZH.md`（**未改名**） |
| 初稿 sha256 | `b57a75f37b555eaf473f8b2833ab4f8db2cb6f01a4246c8e5eb7835f9b2edac5`（sha8 **b57a75f3**） |
| **修订后 sha256** | `a18bb8e6351754b69b88c8ff8ac68af84407f9220ba96e5d44414a74ca820b2e`（sha8 **a18bb8e6**） |
| Intel 回执 | `docs/v2/audit/INTEL_AI_LLM_DEBATE_PIT_INTERFACE_REVIEW_20261025_ZH.md` |
| Intel 回执 sha256 | `52e394ff38bdd57bdef4a5ea50f9b2e2227a01da9e0ca875392e0c0c3e66c9fa`（sha8 **52e394ff**） |
| 证据政策 V1 sha256 | `7a265b8eb36c2d008a193841754f69aee0802b2d5dc781174b4d4764d1b7d172`（sha8 **7a265b8e**） |
| 范围 | **只文档**；未改代码；未申 `.ok`；未实跑；未 git commit；`live=false` |
| 请 Intel | 复核对表 P0×5；本席不代改回执 |

---

## P0×5 勾选表

| # | 要求 | 本修订落点 | 状态 |
|---|---|---|---|
| P0-1 | 证据链列（evidence_id/source_type/publisher/url/published_at/retrieved_at/traceability/supports_fact/caliber/impact/strength/weighted_score/independent_n） | 新增 **§3.3 证据卡子表** + 特征行 `evidence_card_ids[]` 外键 | **DONE** |
| P0-2 | 独立 `gaps[]` + 验收「禁止写入 bear_score / 风险扣分」 | 新增 **§3.4**；§3.2 字段行；§6 验收句硬钉 | **DONE** |
| P0-3 | SourceType 五类 + supports_fact；KOL/INFERENCE 永不升事实；权重引用政策 V1 | 新增 **§3.5**；权重表**不另起**，权威=政策 V1 §3 | **DONE** |
| P0-4 | dedupe_key + independent_n（同稿/同 publisher 不算多源） | **§3.5** 步骤 1–5；特征行 `independent_n`；子表 `dedupe_key` | **DONE** |
| P0-5 | sentiment_net/rating 映射 **或** 明文钉五级由 Intel balance 另算 | **选项 B 钉死**（§3.2「P0-5 钉死」）：本叶只出 bull/bear/disagreement；五级由 Intel `balance`/`rating_from_balance` 另算 | **DONE** |
| P1-1（建议） | retrieved_at/fetched_at 禁冒充 available_at | §3.1 增列；§3.3 子表列；§3.6 硬禁；§6 验收「fetched≠available」 | **DONE** |

---

## 红线自检

| 红线 | 状态 |
|---|---|
| 禁 LLM 买卖权重 / 下单 α | **保持**（§0、§3.6） |
| live=false | **是** |
| 不申 `.ok` / 不实跑 / 不 git commit | **是** |
| 不挡叶25 mem_probe | **是**（文档并行） |
| 文件名未改 | **是** |

---

## 一句话

P0×5 + P1-1 已写入 who_pays DRAFT §3/§6；P0-5 选 **Intel balance 出五级**；请 Intel 按勾选表复核后喊主排号。`live=false`。

---

## 落盘钉

| 项 | 值 |
|---|---|
| 本回执路径 | `docs/v2/audit/AI_LEAF_LLM_DEBATE_PIT_P0x5_PATCH_RECEIPT_20261025_ZH.md` |
| DRAFT 修订后 sha256 | `a18bb8e6351754b69b88c8ff8ac68af84407f9220ba96e5d44414a74ca820b2e` |
| 本回执 sha256 | 以落盘后 `sha256sum` 本文件为准 |
