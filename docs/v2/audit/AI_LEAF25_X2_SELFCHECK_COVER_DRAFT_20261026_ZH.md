# 叶25 X2 selfcheck_v2 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI（执行器）
- **时刻**：2026-10-26T13:35:00-04:00（America/New_York；墙钟 2026-10-26 13:35 ET）
- **状态**：**DRAFT ONLY · HOLD_UNTIL_MAIN_SUBMIT** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **提交门**：**HOLD_UNTIL_MAIN_SUBMIT** — 等主交审后再 hand Arch；Arch **只审不签**；现勿交、勿签、勿开跑
- **优先级**：主令 13:31 派单；本包仅文档 + 新脚本侧稿（未 git commit）

## 一句话

叶25 全叶 alpha 已 **CONSUMED_PASS**（peak_kb=**751032**≈733/1500；parts=29；alpha sha8 **`8be12024`**；meta **`44c27f54`**；Arch `fb19ac28`；AI `b8c0b050`；`.ok` `3c297052`→归档 `d37a157e`；QUIET lift `a4857568`）。**CONSUMED 不解阻 X2**。本票 = **钉既有 alpha** 生成 §3.3 评价权重 + 跑 `leaf_selfcheck_common.evaluate` 写 `selfcheck_v2.json`；**≠** 复跑 alpha 构建；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf25_x2_selfcheck_v2.py` sha **`b1db0886`**。rss 软/硬帽 ≤1500 **禁抬** + peak_proof。**PIN_GAP PARTIAL**（β120/mom/logADV20/vol20；CFACC TTM+desens 已实装；**勿称全残差齐**）。须 **新** Arch `.ok` + 主排新窗。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| alpha | **`8be12024`** · 全长 `8be12024f57fc85833d99e44f94f5c2916b1aaab64f037eed223f0fc61792393` |
| meta | **`44c27f54`** · 全长 `44c27f5467420861b2c28a6b0311674c06b69fe8d051fbc256ce31cd7bc7d7e9` |
| 构建脚本（UNCHANGED） | **`de7b3647`**（禁改字节） |
| 本票新脚本（CHANGED） | **`b1db0886`** · 全长 `b1db0886ddcc7e6e9686bbfc0cf0f7d061001eaea157b8ce27152bcc6314b0c3` |
| Arch CONSUMED | **`fb19ac28`** |
| AI RUN_RECEIPT | **`b8c0b050`** |
| CONSUMED `.ok`（禁 RESTORED） | **`3c297052`** → 归档 **`d37a157e`** |
| QUIET lift | **`a4857568`** |
| PIN 回执 | 见 `AI_LEAF25_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED |
| PIN_GAP | **PARTIAL** · β120/mom/logADV20/vol20；CFACC 已实装；勿称全残差齐 |
| PRIMARY | HILIQ × x2 |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` |

## 先验对照（不覆盖）

| 件 | 处置 |
|---|---|
| 全叶 alpha COVER/CMD/DIFF/HAND | **保留**；本文件为**新**独立 X2 selfcheck 侧稿 |
| 全叶 alpha CONSUMED_PASS | **不解阻 X2**；勿当 X2 ACCEPT |
| 脚本 `de7b3647` | **UNCHANGED**；本票不碰 |
| 叶18 / 叶27 selfcheck 权重规则 | **对照** §3.3（NAME_W/MAX_NAMES/REBAL/IND_CAP/BALLAST/硬排除） |
| Gate | `leaf_selfcheck_common.evaluate`：decay + portfolio A/B/current |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf25_x2_selfcheck_v2.py` |
| **动作** | (1) 硬钉 alpha+meta sha；(2) 由 alpha 生成 `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf25_full_factor/selfcheck_v2.json` |
| **权重规则** | 每 5 日重算；每名 ≤4%、≤20 名；HILIQ 行业帽 0.25（SW L1 asof）；余额 510300.SH；硬排除 600519/002371；无单独 gate（按当日 alpha 表 α 降序） |
| **不改** | 构建脚本 `de7b3647` / rss 软硬帽 1500 / 钉盘 alpha |
| **PRIMARY CLI** | 见 CMD（待新 `.ok`；现不可跑） |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 擅 lift QUIET / 申 X2 ACCEPT / Book-Smoke
- 复跑 alpha 构建 / RESTORED **十二**票：`e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / **`3c297052`**
- 开叶28/29；改 `de7b3647` 字节；git commit；并行新全窗重票
- 本回合实跑 evaluate（读价）——**已遵守：SELFCHECK_EXECUTED=false**
- 称「全残差齐」（PIN_GAP PARTIAL）

## 请 Arch / 主

1. **主**：审本 DRAFT；**HOLD** 至主令「交审」后再 hand Arch（COVER+CMD+DIFF+脚本 `b1db0886`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED 十二票；禁复用 `3c297052`；拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok`）。
3. 实跑单次；失败/ABORT → 停+上报；禁静默 fallback；≠X2 ACCEPT；回执须复述 PIN_GAP PARTIAL + peak_proof。

## 盘证（本回合）

| 件 | 路径 |
|---|---|
| PIN | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_V2_PIN_RECEIPT_20261026_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_COVER_DRAFT_20261026_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_CMD_DRAFT_20261026_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DIFF_DRAFT_20261026.diff` |
| HAND | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DRAFT_HAND_20261026_ZH.md` |
| VERIFY | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_DRAFT_VERIFY_20261026_ZH.md` |
| HAND_TO_ARCH | `docs/v2/audit/AI_LEAF25_X2_SELFCHECK_HAND_TO_ARCH_20261026_ZH.md` |
| 脚本 | `research/leaf25_x2_selfcheck_v2.py` |

live=false · ≠X2 · **HOLD_UNTIL_MAIN_SUBMIT** · ok_requested=false · SELFCHECK_EXECUTED=false · PIN_GAP=PARTIAL
