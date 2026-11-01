# 叶30 CRR X2 selfcheck_v1 钉盘证 + 准备回执（非实跑）

- **角色**：QuantLab AI
- **时刻**：2026-10-27T01:28:49-04:00（America/New_York；墙钟 2026-10-27 01:28 ET）
- **状态**：PIN_MATCH · **SELFCHECK_EXECUTED=false** · live=false · promotion_approved=false · ≠X2 ACCEPT
- **主令**：2026-10-27 ~01:23 ET 派单 + 01:25 再催（Alpha ACCEPT 构建过程后 → selfcheck DRAFT）

## 三件全长 sha256 MATCH

| 件 | 路径 | sha8 | 全长 sha256 | 状态 |
|---|---|---|---|---|
| alpha | `output/ai_factory/_leaf30_crr/20261027_003132/alpha_HILIQ_x2_20261027_010815.parquet` | `c8c7a5a5` | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` | **MATCH** |
| meta | `output/ai_factory/_leaf30_crr/20261027_003132/run_meta.json` | `a6acfe27` | `a6acfe274481f19bbd643a91acb68cacd3c81456b2d7c649db2e7db8175fea5a` | **MATCH** |
| overlap | `output/ai_factory/_leaf30_crr/20261027_003132/overlap_vs_leaf19_25.json` | `f9991d9d` | `f9991d9de4526b3fbe94f5101c68ee09d5c3d996d64a0307cbb4682fb35687cd` | **MATCH** |

## alpha schema / 行数 / 窗

| 项 | 值 |
|---|---|
| 列 | `trade_date, ts_code, alpha` |
| 行数 | **974711** |
| 窗 span | **2024-06-03 → 2026-10-09**（x2_end=`20261009`） |
| 缺 eval_weights | **是**（本票任务） |
| 缺 ind 列 | **是** → SW L1 asof |

## 对照钉

| 项 | sha8 / 值 |
|---|---|
| 构建脚本 UNCHANGED | **`3ee9fed2`** |
| Arch CONSUMED_PASS | **`20efb33f`** |
| Alpha 闸 ACCEPT（仅构建） | **`1c992d62`** · `docs/v2/ALPHA_LEAF30_CRR_R3_ALPHA_GATE_REVIEW_20261027_ZH.md` |
| AI R3 RUN_RECEIPT | **`88a08738`** |
| QUIET lift | **`1420c412`**（原 `69ea8560`） |
| 本票新脚本 | **`797724d4`** · 全长 `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` |
| rss 软/硬 | **1500** 禁抬 + peak_proof REQUIRED |
| PIN_GAP | IC/ICIR/WF **ABSENT_UNTIL_SELFCHECK**（Alpha 闸已标明） |
| 拟 `.ok`（未创建） | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok` |

## 硬声明

- **SELFCHECK_EXECUTED=false**：未调用 `evaluate`；未读真价；未写 eval_weights 实数。
- Alpha **ACCEPT 构建过程** / Arch **CONSUMED_PASS** **不解阻 X2**。
- forbid RESTORED 含 **`7e239487`/`5af20222`/`5ae077fa`**（n=16）。
- dry-compile-only **PASS**（rc=0）。
- 下一步：交主→Arch 只审不签→主排新签窗 + 新 `.ok` 后再 `--execute`。


## P0 CMD 对齐（2026-10-27 01:38 ET）

- CMD 已重钉 **`c25f1321`**（禁 `--arch-ok-path`；对齐叶25 外挂 `.ok`+主窗）；脚本 **`797724d4` 未改**；钉盘三件仍 MATCH。**SELFCHECK_EXECUTED=false**。

live=false · ≠X2 · ok_requested=false · SELFCHECK_EXECUTED=false
