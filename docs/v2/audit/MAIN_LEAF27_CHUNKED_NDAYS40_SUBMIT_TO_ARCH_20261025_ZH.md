# 主令 · 叶27 ndays=40 DRAFT 交审

- **时刻**：2026-10-25T16:00:36-04:00（America/New_York）
- **角色**：主 Agent
- **令**：**SUBMIT_TO_ARCH** · DRAFT 包齐 MATCH

## 前置
| 项 | 值 |
|---|---|
| month `.ok` VOID | Arch 回执 sha8 **`30f7289d`**；live `.ok`=0；QUIET 已 lift |
| month ABORT | `03c58db5`（1502MB@chunk12） |
| MemAvailable | ≈7.2Gi（信息项；本令仅交审不跑） |

## 包钉（主盘证 MATCH AI 声称）
| 件 | sha8 |
|---|---|
| COVER | `ec5f67e9` |
| CMD | `af6f0d49` |
| DIFF | `5449dde5`（NO_CODE_CHANGE） |
| HAND | `5547940b` |
| VERIFY | `305f7a93` |
| HAND_TO_ARCH（交审前） | `b7c33ca8` → AI 改 **SUBMITTED_TO_ARCH** 后回报新 sha |
| script | `262f9bf6` UNCHANGED |

## 硬钉（审/签必须保）
- PRIMARY only：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
- rss=**1500** 禁抬；无同票 FALLBACK；ABORT → 另交 hist-prune
- forbid RESTORED：`8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- ≠X2 · live=false · 禁自开跑 / 禁申 `.ok` 直至主排新窗

## 编排
1. AI：HAND_TO_ARCH → SUBMITTED；交 Arch。
2. Arch：审 ndays40 独立票；结论回主（PASS / PASS_WITH_CONDITIONS / FAIL）。
3. 主：审结后另开签窗；**本令不签 `.ok`、不 prelaunch**。
