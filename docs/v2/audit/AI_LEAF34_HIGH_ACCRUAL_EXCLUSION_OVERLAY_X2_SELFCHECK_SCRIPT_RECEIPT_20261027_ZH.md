# AI 回执：叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 脚本落盘（DRAFT ONLY）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 11:16 ET**（America/New_York） |
| **结论** | **DRAFT READY** · **SELFCHECK_EXECUTED=false** · **交主→Arch 只审脚本** |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`d210efba`** / 全长 `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` |
| 派生自 | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py`（`dcf6b559` 只读；未改） |
| 构建侧 | **`482009dc` UNCHANGED** |
| dry-compile | **PASS** rc=0（mask sha8 `8b5d6d24`；meta `4fc6108d`；overlap `77368c8f`；forbid∋25 票含 `c1b71e64`；rss=1500；无 `--arch-ok-path` CLI；KEEP 不解阻披露；schema 轻读 OK） |
| 无 `--execute` | **exit=2**（MATCH 预期） |
| py_compile | **PASS** → `/tmp/leaf34_sc.pyc` |
| 硬钉 | mask **`8b5d6d24`** / meta **`4fc6108d`** / overlap **`77368c8f`** |
| Arch CONSUME | **`fea9b3ff`** |
| consumed `.ok` | **`c1b71e64`**（ABSENT；禁 RESTORED） |
| AI X2 RUN | **`1441a7ec`** |
| RUNNING_ACK | **`c03d2f16`** |
| FROZEN | **`8be1099e`** |
| PIN | **`bb418e6a`** |
| mechanism | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| PRIMARY | mask-only top_q=0.20 叠加主干（≠ α TopN） |
| Gate | 书面冻结于 COVER/脚本注释（先于读数）+ `evaluate` → decay KEEP 三闸 + portfolio A/B/current；**KEEP 不解阻 X2 ACCEPT**（`45dd87dc`） |
| 未创建 | `.ok` / QUIET / eval_weights / `selfcheck_v1.json` |
| ≠ | 实跑 / 申 `.ok` / 改构建或模板 / 重跑构建 / Book-Smoke / X2 ACCEPT / 升纸面 / 夹带 `0087c928` |
| 交 | **主→Arch 只审脚本**（COVER+CMD+DIFF+脚本） |

## 附件 sha8

| 件 | sha8 | 全长 |
|---|---|---|
| COVER | **`0bf02521`** | `0bf0252123d09e61a483ac9b9a9dcc8ebd6cb47ce14d6aef1f8fd62046a1bd03` |
| CMD（P0；禁 `--arch-ok-path`） | **`4255ad33`** | `4255ad338bec4bf07d5c84b20a2b857a8e477334487065a86d05ab7737768860` |
| DIFF（NEW FILE） | **`a1a6689d`** | `a1a6689dff0ef55de117c7712d7210986fbef3e086947ada5540330f49fd0819` |
| 脚本 | **`d210efba`** | `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6` |

## 静校摘要

- `rg -n 'arch-ok-path' research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` → 仅注释/披露禁令（无 CLI 实现）
- 无 `--execute` 且无 dry → exit=2
- forbid∋`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)（n=25 MATCH）
- 构建脚本 sha8 仍 `482009dc`；模板 `dcf6b559`/`e1fe578c`/`218b61cf` UNCHANGED
- pgrep 未开实跑；未建拟 `.ok`；未挂 QUIET；live `.ok`=0
- 叶33 `afbbe7e7` / 叶32 HOLD `45dd87dc` 不回撤

**leo_notify=false** · live=false · ok_requested=false · EXECUTED=false
