# Arch 叶25 mem_probe r3b 实峰 `.ok` 预检旁证

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T15:09:33-04:00`（America/New_York） |
| live / promotion | false / false |

| # | 检查 | 结果 |
|---|---|---|
| 1 QUIET.lock | `2026-10-25T15:08:19-04:00` `output/loop/RESEARCH_QUIET.lock`（`arch_quiet leaf25_mem_probe_r3b @… reason=LEAF25_MEM_PROBE_R3B_ok_window`） | **PASS** |
| 2 healthz quiet=true（≤90s） | `2026-10-25T15:08:26-04:00` quiet=true | **PASS** |
| 3 再等 ≥15s | 自 quiet_true 起 ≥15s | **PASS** |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} | **PASS**（`2026-10-25T15:08:41-04:00`；原文摘要：`{"ok": true, "ts": "2026-10-25T15:08:41-04:00", "live": false, "quiet": true, "quiet_reason": "lock:/workspace/QuantLab/output/loop/RESEARCH_QUIET.lock", "snapshot_pending": false, "gen_running": false, "snapshot_running": false, "kline_running": false, "child_pids": {}}`） |
| 5 pgrep web | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` | **empty** |
| 6 pgrep research | mem_probe / leaf25_full_factor / leaf27 | **empty** |
| 7 MemAvailable | 5395892 kB ≥ 2621440 | **PASS** |
| 8 钉 MATCH | 审阅 `eaedd655…` / 主窗 `bd13c878…` / COVER `c5d0c4f0…` / CMD `689dc55c…` / DIFF `e92796fe…` / HAND 盘 `9fab0ef4…` / PIN `b1208d3c…` / 探针 `8da4f2e6…` / chunk `e858b32d…` / stub `45537fb9…` | **ALL MATCH** |
| 9 无 live 同名 `.ok` | `ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok` 签前不存在 | **PASS** |
| 10 叶27 无冲突 | 无 live 叶27 `.ok`；窗 14:00–14:45 已过（VOID `3a6caa4f`） | **PASS** |

对齐审阅 `eaedd655…` PASS_WITH_CONDITIONS；主窗令 `bd13c878…` 15:00–15:45 expires 15:47；签后 QUIET **不 lift**（留给 AI prelaunch）。
