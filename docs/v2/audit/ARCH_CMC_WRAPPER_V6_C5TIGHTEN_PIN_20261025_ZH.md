# Arch PIN：cmc_wrapper v6 C5TIGHTEN（侧稿钉）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T13:09:21-04:00`（America/New_York） |
| 审阅 | `docs/v2/audit/ARCH_CMC_WRAPPER_V6_C5TIGHTEN_REVIEW_20261025_ZH.md` sha8 **`74149e29`**（PASS_WITH_CONDITIONS） |
| 对照裁定 | `43fe482e` |
| live / promotion | **false** / **false** |

## PIN

| 项 | 值 |
|---|---|
| 源 draft | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN.draft.sh` |
| **PIN 路径** | `docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh` |
| sha256 | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` |
| sha8 | `b1208d3c` |
| live v5 | **未替换**（仍钉 `docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v5_4240ce82.sh` / `4240ce82`） |

## 用途

- AI r3b CMD **必须**引用本 PIN 路径（或同 sha 副本），**禁**混用 AI 并行草案 `e03a61b6`。
- 本 PIN **≠** 生产 live 替换；**≠** 解阻 X2；**≠** 签 probe `.ok`。
- 禁实跑 `--c5-ignore`；禁抬 C4/STOP/HARD。

## 下一跳

1. AI：交 r3b COVER+CMD+DIFF（脚本可 UNCHANGED `8da4f2e6`；wrapper=本 PIN）→ Arch 另审另签新 `.ok`（禁 `c5e54085`/`cd230f9c`/`1c32ab1e`）。
2. 排窗错开叶27 **14:00–14:45 ET**。
3. Eng 可选：补 `output*` 树下 sleep+fd 合成自测（非挡签）。

live=false；promotion_approved=false。
