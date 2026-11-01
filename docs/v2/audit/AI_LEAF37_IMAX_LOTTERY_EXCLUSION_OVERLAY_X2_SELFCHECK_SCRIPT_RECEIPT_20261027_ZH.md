# AI 回执：叶37 IMAX/隔夜彩票剔除 Overlay X2 selfcheck_v1 脚本落盘（DRAFT ONLY）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 18:58 ET**（America/New_York） |
| **结论** | **DRAFT READY** · **SELFCHECK_EXECUTED=false** · **交主→Arch 只审脚本** |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`015e6f06`** / 全长 `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` |
| 派生自 | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py`（`d210efba` 只读；未改） |
| B1 构建侧 | **`32605aca` UNCHANGED** |
| 基盘 | **`108aba8f` UNCHANGED** ban_as_live |
| dry-compile | **PASS** rc=0（mask sha8 `2503a41e`；meta `e9e9aa1d`；overlap `8177578f`；forbid∋32 票含 `b5be1164`+`4096d401`；rss=1500；C3=B；top_q=0.20；b1_lowmem=true；coverage_median=2816.5≥300；peak_kb=1107536；无 `--arch-ok-path` CLI；KEEP 不解阻披露；schema 轻读 OK） |
| 无 `--execute` | **exit=2**（MATCH 预期） |
| py_compile | **PASS** → `/tmp/leaf37_selfcheck.pyc` |
| pyflakes | **CLEAN**（`/tmp/ql_pyflakes_venv`） |
| 硬钉 | mask **`2503a41e`** / meta **`e9e9aa1d`** / overlap **`8177578f`** |
| Arch CONSUME | **`c0a6b5ae`** |
| consumed `.ok` | **`b5be1164`**（ABSENT；禁 RESTORED） |
| VOID `.ok` | **`4096d401`**（禁 RESTORED） |
| AI X2 RUN | **`c6d8b1ce`** |
| RUNNING_ACK | **`08652c66`** |
| SIGNED / 审 / VOID回执 | **`7b3bd298`** / **`b403a7e5`** / **`998171e1`** |
| FROZEN | **`c5927f1b`** |
| PIN | **`e01be34c`** |
| mechanism | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| PRIMARY | mask-only top_q=0.20 叠加主干（≠ α TopN）；C3=B IMAX_proxy；b1_lowmem=true |
| Gate | 书面冻结于 COVER/脚本注释（先于读数）+ `evaluate` → decay KEEP 三闸 + portfolio A/B/current；**KEEP 不解阻 X2 ACCEPT** |
| 未创建 | `.ok` / QUIET / eval_weights / `selfcheck_v1.json` |
| ≠ | 实跑 / 申 `.ok` / 改 B1 或基盘或模板 / 重跑构建 / Book-Smoke / X2 ACCEPT / 升纸面 / 夹带 `0087c928` / 复开叶36 |
| 交 | **主→Arch 只审脚本**（COVER+CMD+DIFF+脚本） |

## 附件 sha8

| 件 | sha8 | 全长 |
|---|---|---|
| COVER | **`8c83ba13`** | `8c83ba135e9e2d675e56b8c47cd82b2ea56aa8189f2ece25477b6cd25769874c` |
| CMD（P0；禁 `--arch-ok-path`） | **`6f5d48bd`** | `6f5d48bdc5e3f7f63889e72a140b02d56b937337f92d8ceefd2f630be59632b2` |
| DIFF（NEW FILE；相对叶34 模板派生说明） | **`2542e7cd`** | `2542e7cdaa2fe24f18bd78b36284d754197cbe533163056141736c6005ff123c` |
| 脚本 | **`015e6f06`** | `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` |

## 静校摘要

- `rg -n 'arch-ok-path' research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` → 仅注释/披露禁令（无 CLI 实现）
- 无 `--execute` 且无 dry → exit=2
- forbid∋`b5be1164`+`4096d401`+`eb70eef4`+…（n=32 MATCH）
- B1 脚本 sha8 仍 `32605aca`；基盘仍 `108aba8f`；模板 `d210efba`/`dcf6b559`/`218b61cf` UNCHANGED
- pgrep 未开实跑；未建拟 `.ok`；未挂 QUIET；live `.ok`=0
- 叶33 `afbbe7e7` / 叶35 `434ff42c` / 叶34 `482009dc` UNCHANGED；叶36 HOLD 不复开

**leo_notify=false** · live=false · ok_requested=false · EXECUTED=false
