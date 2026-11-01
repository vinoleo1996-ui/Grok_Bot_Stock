# 主令 · 叶27 month PRELAUNCH GO（软 HOLD 因平台底解绑）

- **时刻**：2026-10-25T15:48:34-04:00（America/New_York）
- **角色**：主 Agent
- **令**：**GO_PRELAUNCH** · PRIMARY **month** 单次

## 盘证（发令前）
| 项 | 值 |
|---|---|
| `.ok` sha8 | **`8e51de63`** MATCH |
| QUIET | 已挂；8795 quiet=true；gen/snapshot/kline=false；child_pids={} |
| pgrep kline/export/snapshot/gen/leaf27 | 空 |
| script sha8 | **`262f9bf6`** |
| MemAvailable | ≈**3.2Gi**（≥ `.ok` 地板 2.5Gi；软门槛 5–6Gi **不可解**——drop_caches 后仍≈3.2Gi，平台 node/Xvfb 底座占满） |
| 窗 | `64c7da1e` 至 16:25 / expires 16:27 |

## 决策
- 软 HOLD（≳5–6Gi）因共享 box 平台底无法在窗内达成；**不解绑硬钉**。
- 发令依据：`.ok` prelaunch Mem≥2.5Gi **已满足** + QUIET/healthz 净 + **rss=1500 abort_on_rss_over** 仍硬保护；禁抬帽。
- AI **仅**执行：`PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_chunked_members_mktcap_r1.py --universe HILIQ --window x2 --chunk-mode month`
- ABORT_RSS → **停**；另交 ndays=40 票；**禁静默 fallback**。
- 禁申 X2 · ≠X2 · live=false · Arch 不代跑。
- 峰证明 REQUIRED；采样 `/tmp/quantlab_leaf27_chunked_month_*`。

## 回执要求
AI 开跑后写 RUN_RECEIPT（含 peak_kb / C4/C5 或 ABORT 原因）；主收讫后再论 CONSUME/VOID。
