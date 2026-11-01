# AI 回执：叶30 CRR X2 PRIMARY · ABORT_PEAK_HWM

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | **2026-10-26 18:19:02 EDT**（America/New_York） |
| 主令 | STARTED MATCH 后 URGENT peak（VmHWM>hard）→ 主动 SIGTERM |
| **结论** | **ABORT_PEAK_HWM**（非脚本 SystemExit 95；主复检峰已破帽且 check_rss 间隙无新检查 → AI 主动停） |
| ET_TS | `20261026_181634` |
| run_pid | `2934563`（SIGTERM 后 ~2s gone） |
| sampler_pid | `2934562` |

## 1. 峰证 peak_proof

| 源 | 值 |
|---|---|
| `/proc` 停前 **VmHWM** | **2429160 kB（≈2372 MB）** > hard **1536000** |
| `/proc` 停前 **VmRSS** | **1431984 kB（≈1398 MB）** < hard（sampler 未触发 ABORT_RSS） |
| sampler `sampler_30s.txt` 峰 VmRSS | **1426396 kB**（最后行 18:18:34 ET OK） |
| 脚本 last `RSS_CHECK` | `after_fund` peak_kb=**544376** vmrss_kb=512576（此后无新 check；峰在日度/后续阶段间隙冲过帽） |
| hard / soft | 1536000 / 1536000（rss=1500 禁抬） |

## 2. 阶段与产物

- 最后 STAGE/RSS_CHECK：`after_fund`（log 无 `OK leaf30_crr_alpha`）
- out `output/ai_factory/_leaf30_crr/20261026_181634/`：**空**（无 alpha / run_meta / overlap）
- log：`output/ai_factory/_leaf30_crr/20261026_181634_logs/run_20261026_181634.log`
- samp：`/tmp/quantlab_leaf30_crr_20261026_181634`（含 `AI_ABORT_STATUS.txt`）

## 3. 钉与动作

| 项 | 状态 |
|---|---|
| `.ok` `5ae077fa` | **仍在**（未自申新票；交 Arch 核 / 可能 VOID） |
| QUIET `e6180a7a` | **仍在；未自 lift** |
| 脚本 `a2cef5af` | 未改 |
| 抬帽 / 重试 / 新 `.ok` | **禁且未做** |
| SIGTERM | 主 URGENT 硬令 #2（长时间无 check_rss + VmHWM 已破） |

## 4. 下一跳

交主 / Arch 核（VOID 或 ABORT 签文）；**禁**自重试；**禁**抬帽；≠X2 ACCEPT；≠Book-Smoke。叶26/28/29 不动。**不报 Leo**。live=false。
