# Arch 叶25 mem_probe r2 实峰 `.ok` 预检旁证

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:24:34-04:00`（America/New_York） |
| live / promotion | false / false |

| # | 检查 | 结果 |
|---|---|---|
| 1 QUIET.lock | `2026-10-25T12:20:29-04:00` `arch_quiet_leaf25_mem_probe_r2@…` | **PASS** |
| 2 healthz quiet=true（≤90s） | `2026-10-25T12:22:10-04:00` quiet=true | **PASS** |
| 3 再等 ≥15s | 自 quiet_true 起 ≥15s | **PASS** |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} | **PASS**（`2026-10-25T12:24:34-04:00`） |
| 5 pgrep web | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` | **empty** |
| 6 pgrep research | mem_probe / leaf25_full_factor / g1g5 | **empty** |
| 7 MemAvailable | 12550980 kB ≥ 2621440 | **PASS** |
| 8 script sha | `9dfe173a9104330287f6ebfe2f758c63891f3c92b5f9d112118b697898d50e0f` | **MATCH** |
| 9 research `__pycache__` r2 | 已删 | **PASS** |

对齐审阅 `1b706f9b…` PASS_WITH_CONDITIONS；主令另审另签。
