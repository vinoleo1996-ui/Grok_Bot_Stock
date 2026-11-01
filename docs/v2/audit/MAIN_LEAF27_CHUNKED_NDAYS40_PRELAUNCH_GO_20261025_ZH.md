# 主令 · 叶27 ndays40 PRELAUNCH GO

- **时刻**：2026-10-25T16:21:05-04:00（America/New_York）
- **角色**：主 Agent
- **令**：**GO_PRELAUNCH** · PRIMARY **ndays40** 单次

## 盘证（发令前）
| 项 | 值 |
|---|---|
| `.ok` sha8 | **`a7d98ac9`** MATCH（全长 `a7d98ac97a34c3e966577c22168e4d782a247ff0930afc0dea912afa331bac90`） |
| `.ok` 路径 | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_CHUNKED_MEMBERS_MKTCAP_HILIQ_X2_NDAYS40.ok` |
| QUIET | 已挂不 lift；8795 quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep 研究 python / leaf27 | 空 |
| script sha8 | **`262f9bf6`** UNCHANGED |
| MemAvailable | ≈**6.5Gi**（≥软地板 5–6Gi；硬帽仍 rss=1500） |
| 窗 | `c6fb3c2e` **16:15–17:00** expires **17:02** |
| 审 | `18ea1567` PASS_WITH_CONDITIONS |
| Arch 回执 / 预检 | `bc86ca19` / `9eedb34e` |

## 决策
- 条件 A 满足：Arch 已签 + QUIET 净 + Mem≥软地板 → **立刻令 AI prelaunch 单次**。
- AI **仅**执行：`PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode ndays --chunk-ndays 40`
- **无同票 FALLBACK**；ABORT_RSS → **停**；另交 hist-prune 票；**禁静默换 mode / 禁抬帽**。
- forbid RESTORED：`8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0`
- 峰证明 REQUIRED；采样 `/tmp/quantlab_leaf27_chunked_ndays40_*`
- 禁申 X2 · ≠X2 · live=false · Arch 不代跑 · 禁双开 · 禁擅 lift QUIET

## 回执要求
AI 开跑后写 RUN_RECEIPT（含 peak_kb / C4/C5 或 ABORT 原因）；主收讫后再论 CONSUME/VOID。
