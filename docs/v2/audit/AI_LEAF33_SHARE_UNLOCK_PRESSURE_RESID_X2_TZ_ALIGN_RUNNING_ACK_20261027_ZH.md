# AI RUNNING ACK：叶33 X2 tz-align PRIMARY STARTED

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-27 07:21 ET**（ISO `2026-10-27T07:21:59-04:00`） |
| 主令 | ~07:18 ET GO MATCH；`.ok` **`245df63f`** / QUIET **`ca492c09`** / SIGNED **`731f05d7`** / 落地审 **`069ba364`** / 补丁审 **`19cc790f`** / 脚本 **`afbbe7e7`** |
| **状态** | **RUNNING** |
| ≠X2 ACCEPT | **true** |
| ≠selfcheck / ≠Book-Smoke | **true** |
| live / leo_notify | **false** / **false** |

## 运行钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_072135` |
| pid | `4194000` |
| nice | 10 |
| 脚本 | **`afbbe7e7`**（基线钉 `05c45917`；`tz_align_mode=naive_calendar_day`） |
| `.ok` | **`245df63f`** → `output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok`（**≠** RESTORED `c5ed13df`） |
| QUIET | **`ca492c09`** holder=`leaf33_SHARE_UNLOCK_PRESSURE_RESID_X2` expires **08:45 ET**；**do_not_lift**（本拍不 lift） |
| SIGNED | **`731f05d7`** |
| approved_cmd | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf33_share_unlock_pressure_resid_alpha_build.py --universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path output/ai_factory/ARCH_RUN_AUTH_LEAF33_SHARE_UNLOCK_PRESSURE_RESID_X2_HILIQ.ok --out output/ai_factory/_leaf33_share_unlock/20261027_072135/ --sample-dir /tmp/quantlab_leaf33_share_unlock_20261027_072135` |
| `--no-overlap-report` | **未加**（禁） |
| rss | **1500 禁抬**；破峰 Exit 94/95 停+上报禁自改复跑 |
| out | `output/ai_factory/_leaf33_share_unlock/20261027_072135/` |
| sample-dir | `/tmp/quantlab_leaf33_share_unlock_20261027_072135` |
| log | `output/ai_factory/_leaf33_share_unlock/20261027_072135_logs/run_20261027_072135.log` |
| pgrep kline/export_static/snapshot/gen | **空** |
| 早期进度 | 已过 `after_mask` / `after_sw` / `after_share_float_rebal_20240603`（**越过**前次 L818 TypeError 崩溃点） |

## 禁令自检

- 未 RESTORED `c5ed13df`+`5774bb6e`+二十票；未抬 rss；未 `--no-overlap-report`；未触 A18
- `0087c928`/叶28/29 另队；未报 Leo；未宣称 X2 ACCEPT
- QUIET **未擅 lift**

完后交 **RUN_RECEIPT→主→Arch CONSUME**。
