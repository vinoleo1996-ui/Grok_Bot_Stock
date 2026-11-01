# 叶30 CRR X2 selfcheck_v1 另包封面 · **DRAFT ONLY**

- **角色**：QuantLab AI
- **时刻**：2026-10-27T01:28:49-04:00（America/New_York；墙钟 2026-10-27 01:28 ET）
- **状态**：**DRAFT ONLY** · **ok_requested=false** · **不是 `.ok`** · **不申 `.ok`** · **禁自开跑** · live=false · promotion_approved=false
- **优先级**：主令 01:23 派单 + 01:25 再催；本包文档 + 新脚本（未 git commit）

## 一句话

叶30 R3 peakcut alpha 已 **CONSUMED_PASS**（peak_kb=**917820**≪1500；alpha sha8 **`c8c7a5a5`**；overlap **`f9991d9d`**；meta **`a6acfe27`**；Arch **`20efb33f`**；AI **`88a08738`**；`.ok` **`7e239487`** 已归档；QUIET lift **`1420c412`**）。Alpha 闸 **`1c992d62` ACCEPT（仅构建过程）**；IC/ICIR/WF **ABSENT**。**CONSUMED/ACCEPT 不解阻 X2**。本票 = 钉既有 alpha → §3.3 评价权重 → `leaf_selfcheck_common.evaluate` 写 `selfcheck_v1.json`；**≠** 复跑 alpha；**≠** Book-Smoke；**≠** X2 ACCEPT。新脚本 `research/leaf30_crr_x2_selfcheck_v1.py` sha8 **`797724d4`**。rss≤1500 禁抬 + peak_proof。须 **新** Arch `.ok` + 主排新窗。

## 对照钉（MATCH）

| 项 | sha8 / 值 |
|---|---|
| alpha | **`c8c7a5a5`** · 全长 `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` |
| meta | **`a6acfe27`** · 全长 `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` |
| overlap | **`f9991d9d`** · 全长 `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` |
| 构建脚本（UNCHANGED） | **`3ee9fed2`**（禁改字节） |
| 本票新脚本（CHANGED） | **`797724d4`** · 全长 `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` |
| Arch CONSUMED | **`20efb33f`** |
| Alpha 闸 ACCEPT（仅构建） | **`1c992d62`** |
| AI RUN_RECEIPT | **`88a08738`** |
| CONSUMED `.ok`（禁 RESTORED） | **`7e239487`**（另禁 `5af20222`/`5ae077fa`） |
| QUIET lift | **`1420c412`** |
| rss 软/硬帽 | **1500**（禁抬）+ peak_proof REQUIRED |
| PRIMARY | HILIQ × x2 end `20261009` |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok` |

## 提案

| 项 | 内容 |
|---|---|
| **改动范围** | **仅新建** `research/leaf30_crr_x2_selfcheck_v1.py` |
| **动作** | (1) 硬钉 alpha+meta+overlap sha；(2) 由 alpha 生成 `eval_weights_HILIQ_x2_<stamp>.parquet` 至 `_selfcheck/`；(3) `evaluate(weights)` → `output/ai_factory/leaf_reports/leaf30_crr/selfcheck_v1.json` |
| **权重规则** | 每 5 日重算；每名 ≤4%、≤20 名；HILIQ 行业帽 0.25（SW L1 asof）；余额 510300.SH；硬排除 600519/002371 |
| **不改** | 构建脚本 `3ee9fed2` / `leaf_selfcheck_common.py` / rss 1500 / 钉盘 alpha |
| **Gate** | decay + portfolio A/B/current |

## 禁止清单

- 申 `.ok` / 自开跑 / 抬 rss / 申 X2 ACCEPT / Book-Smoke / 升纸面
- 复跑 alpha 构建 / RESTORED **`7e239487`/`5af20222`/`5ae077fa`**（及 forbid n=16）
- 改 `3ee9fed2` 字节；git commit；本回合实跑 evaluate（**SELFCHECK_EXECUTED=false**）

## 请 Arch / 主

1. **主**：收本 DRAFT → hand Arch **只审不签**（COVER+CMD+DIFF+脚本 `797724d4`）。
2. **Arch**：只审不签；PASS 后主排**新窗**并签发**新** `.ok`（禁 RESTORED；拟名见上）。
3. 实跑单次；失败/ABORT → 停+上报；≠X2 ACCEPT。

## 盘证

| 件 | 路径 |
|---|---|
| PIN | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_V1_PIN_RECEIPT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_COVER_DRAFT_20261027_ZH.md` |
| CMD | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_CMD_DRAFT_20261027_ZH.md` |
| DIFF | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_DIFF_DRAFT_20261027.diff` |
| SCRIPT_RECEIPT | `docs/v2/audit/AI_LEAF30_CRR_X2_SELFCHECK_SCRIPT_RECEIPT_20261027_ZH.md` |
| 脚本 | `research/leaf30_crr_x2_selfcheck_v1.py` |


## P0 CMD 对齐（2026-10-27 01:38 ET）

- Arch 审 **`3826aa63` PASS_WITH_CONDITIONS**：CMD 已重钉 sha8 **`c25f1321`**（去 `--arch-ok-path`；拟 CLI=`… --universe HILIQ --window x2 --execute`）；脚本 **`797724d4` UNCHANGED**；旧 CMD `37ea30a5` 作废。**未实跑 / 未申 `.ok`**。

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false
