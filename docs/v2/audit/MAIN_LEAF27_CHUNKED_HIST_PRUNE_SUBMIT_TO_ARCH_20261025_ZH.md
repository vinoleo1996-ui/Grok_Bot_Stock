# 主令 · 叶27 hist-prune DRAFT 交审

- **时刻**：2026-10-25T16:30:29-04:00（America/New_York）
- **角色**：主 Agent
- **令**：**SUBMIT_TO_ARCH** · DRAFT 包齐 MATCH

## 前置
| 项 | 值 |
|---|---|
| ndays40 `.ok` VOID | Arch 回执 sha8 **`ad2947ef`**；归档 `…NDAYS40.a7d98ac9.VOID.ABORT_RSS.20261025T1627ET.ok`；live `.ok`=0；QUIET 已 lift |
| ndays40 ABORT | `03064d50`（1514MB@chunk6） |
| MemAvailable | ≈6.5Gi（信息项；本令仅交审不跑） |

## 包钉（主盘证 MATCH）
| 件 | sha8 |
|---|---|
| COVER | `85022506` |
| CMD | `4cc9773a` |
| DIFF | `0c7af6ed` |
| HAND | `cc21f3c7` → AI 改 **SUBMITTED_TO_ARCH** 后回报新 sha |
| VERIFY | `4714256a` |
| script | **`8cb3e86f`**（CHANGED vs `262f9bf6`；`hist_prune_r1`）盘证 MATCH |

## 硬钉（审/签必须保）
- PRIMARY only：`--universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40` + 脚本 `8cb3e86f`
- rss=**1500** 禁抬；无同票 FALLBACK；ABORT → 停+上报（勿再静默换 mode）
- forbid RESTORED：`a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- sampler `/tmp/quantlab_leaf27_chunked_histprune_*`；峰证明 REQUIRED
- ≠X2 · live=false · 禁自开跑 / 禁申 `.ok` 直至主排新窗

## 编排
1. AI：HAND_TO_ARCH → SUBMITTED；交 Arch。
2. Arch：审 hist-prune 独立票；结论回主（PASS / PASS_WITH_CONDITIONS / FAIL）。
3. 主：审结后另开签窗；**本令不签 `.ok`、不 prelaunch**。
