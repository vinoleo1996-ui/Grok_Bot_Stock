# 叶27 X2 selfcheck_v2 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T00:35:00-04:00（America/New_York；墙钟 2026-10-26 00:35 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — 等主交审后再 hand Arch；Arch **只审不签**；现勿交、勿签、勿开跑
- **优先级**：主令 00:27 深挖派单；本包仅文档 + 新脚本侧稿（未 git commit）

## 一句话

叶27 baseline_evac 已 **CONSUMED_PASS**（peak **1401**/1500；n_chunks=17；alpha sha8 **`652b8a68`**；Arch `78557480`；AI `1671eec4`；`.ok` `0f50daf7`→归档 `7e06a5b3`）。**CONSUMED 不解阻 X2**。本票 = **钉既有 alpha** 生成 §3.3 评价权重 + 跑 `leaf_selfcheck_common.evaluate` 写 `selfcheck_v2.json`；**≠** 复跑 baseline_evac；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf27_x2_selfcheck_v2.py` sha **`a40d7069`**。rss 软披露 ≤1500 **禁抬**。须 **新** Arch `.ok` + 主排新窗。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| alpha | **`652b8a68`** · 全长 `652b8a68b28871ddc1cbf623834650c23c79c8a81235fabc578ede71f17cf1b1` |
| meta | **`85c2dc78`** · 全长 `85c2dc7897c2796e36357042d8521e8b4b91beec8f2cd43bf18c31bdf48d4068` |
| summary | **`80596bff`** · 全长 `80596bffb7de1296f6859f3e7bf1afa5c73ef2ec79a579bb365061cba8579cd6` |
| 构建脚本（UNCHANGED） | **`585ba746`**（禁改字节） |
| 本票新脚本（CHANGED） | **`a40d7069`** · 全长 `a40d7069374bb940863b8af6e3e103a07aa6c82f10c9cf389f53c76c57edddc0` |
| Arch CONSUMED | **`78557480`** |
| AI RUN_RECEIPT | **`1671eec4`** |
| CONSUMED `.ok`（禁 RESTORED） | **`0f50daf7`** → 归档 **`7e06a5b3`** |
| PIN 回执 | 见 `AI_LEAF27_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` |
| rss 软帽 | **1500**（禁抬） |
| PRIMARY | HILIQ × x2 |

## 先验对照（不覆盖）

| 件 | 处置 |
|---|---|
| baseline_evac COVER/CMD/DIFF/HAND | **保留**；本文件为**新**独立 X2 selfcheck 侧稿 |
| baseline_evac CONSUMED_PASS | **不解阻 X2**；勿当 X2 ACCEPT |
| 脚本 `585ba746` | **UNCHANGED**；本票不碰 |
| 叶18 `g1g5_overnight_idio_ivol_alpha.py` 权重规则 | **对照** §3.3（NAME_W/MAX_NAMES/REBAL/IND_CAP/BALLAST/硬排除） |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf27_x2_selfcheck_v2.py` |
| **动作** | (1) 硬钉三件 sha；(2) 由 alpha 生成 `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json` |
| **权重规则** | 每 5 日重算；每名 ≤4%、≤20 名；HILIQ 行业帽 0.25；余额 510300.SH；硬排除 600519/002371；无单独 gate（按当日 alpha 表 α 降序） |
| **不改** | chunked 脚本 `585ba746` / lowmem / g1g5 因子路径 / rss 软帽 1500 |
| **PRIMARY CLI** | 见 CMD（待新 `.ok`；现不可跑） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 擅 lift QUIET / 申 X2 ACCEPT / Book-Smoke
- 复跑 baseline_evac / RESTORED **八**票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / **`0f50daf7`**
- 开叶28/29；改 `585ba746` 字节；git commit
- 本回合实跑 evaluate（读价）——**已遵守：SELFCHECK_EXECUTED=false**

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF+脚本 `a40d7069`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED 八票；禁复用 `0f50daf7`）。
3. 实跑单次；失败/ABORT → 停+上报；禁静默 fallback；≠X2 ACCEPT。

## 盘证（本回合）

| 件 | 路径 |
|---|---|
| PIN | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_COVER_DRAFT_20261026_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_CMD_DRAFT_20261026_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DIFF_DRAFT_20261026.diff` |
| HAND | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_DRAFT_VERIFY_20261026_ZH.md` |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF27_X2_SELFCHECK_HAND_TO_ARCH_20261026_ZH.md` |
| 脚本 | `research/leaf27_x2_selfcheck_v2.py` |

live=false · ≠X2 · **HOLD_UNTIL_MAIN_SUBMIT** · ok_requested=false · SELFCHECK_EXECUTED=false
