# Arch 叶25 mem_probe r3 实峰 `.ok` 预检旁证

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:47:07-04:00`（America/New_York） |
| live / promotion | false / false |

| # | 检查 | 结果 |
|---|---|---|
| 1 QUIET.lock | `2026-10-25T12:46:52-04:00` `arch_quiet_leaf25_mem_probe_r3@…` | **PASS** |
| 2 healthz quiet=true（≤90s） | `2026-10-25T12:46:52-04:00` quiet=true | **PASS** |
| 3 再等 ≥15s | 自 quiet_true 起 ≥15s | **PASS** |
| 4 healthz 复检 | quiet=true；gen/snapshot/kline_running=false；child_pids={} | **PASS**（`2026-10-25T12:47:07-04:00`） |
| 5 pgrep web | `[k]line.py|[e]xport_static.py|[s]napshot.py|[g]en.py` | **empty** |
| 6 pgrep research | mem_probe / leaf25_full_factor | **empty** |
| 7 MemAvailable | 12440760 kB ≥ 2621440 | **PASS** |
| 8 script sha | `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` | **MATCH** |
| 9 research `__pycache__` r3 | 已删 | **PASS** |
| 10 错开叶27 | 窗至 13:45；叶27 默认 14:00–14:45 | **PASS** |

对齐审阅 `63500a9f…` PASS_WITH_CONDITIONS；主令 PASS 后另签；拟窗请主确认。
