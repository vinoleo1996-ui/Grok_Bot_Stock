# AI 回执：叶32 Margin Net Flow Resid X2 selfcheck_v1 脚本落盘（DRAFT ONLY）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 05:02 ET**（America/New_York） |
| **结论** | **DRAFT READY** · **SELFCHECK_EXECUTED=false** · **交主→Arch 只审脚本** |
| 脚本 | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` sha8 **`dcf6b559`** / 全长 `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` |
| 派生自 | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py`（`e1fe578c` 只读；未改） |
| 构建侧 | **`4e0f3c00` UNCHANGED** |
| dry-compile | **PASS** rc=0（alpha sha8 `13eee6fd`；forbid∋七票；rss=1500；无 `--arch-ok-path` CLI；decay KEEP 披露） |
| py_compile | **PASS** → `/tmp/leaf32_selfcheck.pyc` |
| 硬钉 | alpha **`13eee6fd`** / meta **`e510f346`** / overlap **`a643d71a`** |
| Alpha 闸 | **`1aa432a5`** ACCEPT（仅构建；IC/ICIR/WF ABSENT） |
| Arch CONSUME | **`a1a5e35a`** |
| AI X2 RUN | **`f3e8f991`** |
| RUNNING_ACK | **`3c4d0124`** |
| FROZEN | **`6b8de5e9`** |
| mechanism | `g1g5_ashare_margin_net_flow_resid_v1` |
| Gate | `leaf_selfcheck_common.evaluate` → decay KEEP 三闸 + portfolio A/B/current；盯 decay KEEP |
| 未创建 | `.ok` / QUIET / eval_weights / `selfcheck_v1.json` |
| ≠ | 实跑 / 申 `.ok` / 改构建或模板 / 重跑 alpha / Book-Smoke / X2 ACCEPT / 升纸面 / 夹带 `0087c928` |
| 交 | **主→Arch 只审脚本**（COVER+CMD+DIFF+脚本） |

## 附件 sha8

| 件 | sha8 | 全长 |
|---|---|---|
| COVER | **`e901405b`** | `e901405bb1015c7f1ade9704211e1e1a2a55214f7381827c12f22966aac626c8` |
| CMD（P0；禁 `--arch-ok-path`） | **`754bf251`** | `754bf25123c680faaac38e185363d08a0a9e78fd50dde642b02272d8d41c62c9` |
| DIFF（相对 leaf31 `e1fe578c`） | **`3f98d664`** | `3f98d66413a05f05cc5d2692fd91d043334b0c4c2c226118bd1a6392f218a0f9` |
| 脚本 | **`dcf6b559`** | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` |

## 静校摘要

- `rg -n 'arch-ok-path' research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` → 仅注释/披露禁令（无 CLI 实现）
- 无 `--execute` 且无 dry → exit=2
- forbid∋`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`
- 构建脚本 sha8 仍 `4e0f3c00`；模板 `e1fe578c`/`797724d4` UNCHANGED
- pgrep 未开实跑；未建拟 `.ok`；未挂 QUIET
- TEAM_STATE prepend AI NOW（EXECUTED=false）

**leo_notify=false** · live=false · ok_requested=false · EXECUTED=false
