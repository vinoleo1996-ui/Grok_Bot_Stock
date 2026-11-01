# AI 回执：叶30 CRR R2 X2 PRIMARY · ABORT_PEAK_HWM（Exit 94）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-26 23:54:42 EDT**（America/New_York） |
| **结论** | **ABORT_PEAK_HWM**（脚本 `SystemExit(94)`；非 Exit 95 hard；非 AI 主动 SIGTERM） |
| ET_TS | `20261026_231925` |
| run_pid | `3554729`（已退出） |
| **rc** | **94**（log 末行证据：`STOP: RSS >= 0.85*C4 peak_kb=1433684 >= split=1131520; split further — ban raise cap`） |
| script | `research/leaf30_crr_cfooe_volpen_alpha_build_r2_chunk.py` sha8 **`0a264402`**（现核 `0a264402`；未改） |
| `.ok` | `ARCH_RUN_AUTH_LEAF30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R2_HILIQ_X2.ok` sha8 **`5af20222`** / 全长 `5af20222df0d2fc6fd4b893903abf01a6d3bb19acc7f66524f3e93ee4dbf12c0`（现核 `5af20222`；**仍在位**；未自申/未改） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`c0f3ff81`**（现核 `c0f3ff81`；holder=`leaf30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R2`；**未擅 lift**） |
| out | `output/ai_factory/_leaf30_crr/20261026_231925/` |
| log | `output/ai_factory/_leaf30_crr/20261026_231925_logs/run_20261026_231925.log` |
| samp | `/tmp/quantlab_leaf30_crr_r2_20261026_231925` |
| CLI | approved_cmd 原样；**无** `--no-overlap-report`；rss=1500 禁抬 |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / selfcheck / Book-Smoke；禁触 A18；forbid∋`5ae077fa`；禁盲重跑 `a2cef5af` |

## 1. peak_proof 摘要

| 源 | 值 |
|---|---|
| 最后 `RSS_CHECK` | **`after_logmv_rebal`** peak_kb=**1433684** vmrss_kb=**835468** soft=1536000 split=1131520 c4=1331200 hard=1536000 |
| 触发 | peak_kb ≥ split（0.85×C4=1131520）→ Exit **94**；文案禁抬帽 |
| sampler peak VmHWM | **1433684** kB |
| sampler peak VmRSS | **1207320** kB |
| sampler.log | `sampler_start 2026-10-27T11:19:25+08:00
sampler_end_no_pid 2026-10-27T11:53:20+08:00` |
| `after_daily_concat` | **未到达**（abort 于 `after_logmv_rebal`，日度 expand/concat 之前） |
| 脚本 ru_maxrss/VmHWM 峰 | 以最后 RSS_CHECK peak_kb=**1433684** 为准（=max(ru_maxrss,VmHWM)） |

### RSS_CHECK 序列要点（非逐月）

1. `build_start` peak=105600
2. `after_mask` peak=501020
3. `after_sw` peak=502032
4. `after_fund` peak=528636
5. `after_logmv_avail`（月循环 201904→202610 完成）peak=921616
6. `after_vol_pen` peak=921616
7. **`after_logmv_rebal` peak=1433684 → STOP Exit 94**

## 2. overlap 结果

- **未产出**：out 无 `overlap_vs_leaf19_25.json`（abort 早于 overlap 阶段）
- Jaccard vs leaf19/25：**N/A**
- hard reject：**N/A**（未跑到判定）
- ρ：**N/A**
- 声明：本次 **未** 使用 `--no-overlap-report`；失败原因为 RSS split abort，非跳过 overlap

## 3. 产物

- out 文件列表：（空；无 alpha / meta / summary / overlap_vs_leaf19_25.json / peak_proof*）
- 关键 alpha / meta / summary / overlap / peak_proof* sha8：**无**（目录空）
- log 行数：113；末行即 STOP

## 4. 钉与禁止项声明

| 项 | 状态 |
|---|---|
| `.ok` `5af20222` | **仍在**（交 Arch CONSUME / 可能 VOID；AI 未自申） |
| QUIET `c0f3ff81` | **仍在；未擅 lift** |
| 脚本 `0a264402` | 未改 |
| 抬帽 / 盲重跑 / 新 `.ok` | **禁且未做** |
| forbid∋`5ae077fa` | 未复用 |
| 禁盲重跑 `a2cef5af` | 未触 |
| 禁触 A18 | 未触 |
| ≠X2 ACCEPT / selfcheck / Book-Smoke | 声明成立 |
| live | false |
| leo_notify | false |

## 5. 下一跳

交主 / Arch：**ABORT_PEAK_HWM rc=94**；peak 于 `after_logmv_rebal`（1433684≥split）；无 overlap / 无 after_daily_concat；**.ok 仍在位** 待 Arch CONSUME/VOID。**禁**自重试；**禁**抬帽；**勿报 Leo**。
