# AI 回执：叶35 ETF Passive Flow Pressure Overlay X2 · STOP（rc=1）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 13:54:43 EDT**（America/New_York） |
| **结论** | **STOP**（stderr 末行 `STOP: zero mask rows (check etf share / weights scheme A / HI_LIQ / top_q)`；`SystemExit(str)` → **rc=1**；无 Exit 94/95；无 Traceback；**无产物 parquet/json**） |
| ET_TS | `20261027_135145` |
| run_pid | `470069`（已退出；nice=10；pgrep 现空） |
| **rc** | **1** |
| status | **STOP_ZERO_MASK_ROWS** |
| script | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`25ae4572`**（现核 MATCH；**未改**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` sha8 **`10927bd9`**（现核 MATCH；**仍在位**；未自签/未删；交 Arch CONSUME；∉forbid26） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`c8d95fee`**（现核 MATCH；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`3b25f9d7`**（钉） |
| 审 | sha8 **`ea395dc4` PASS_WITH_CONDITIONS**（钉） |
| RUNNING_ACK | sha8 **`46b32368`** |
| leaf33 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7` UNCHANGED** |
| out | `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_135145/` |
| log | `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_135145/stdout.log` + `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_135145/stderr.log` + `/tmp/quantlab_leaf35_etf_passive_20261027_135145.log` |
| samp | `/tmp/quantlab_leaf35_etf_passive_20261027_135145_peak_sampler.tsv`（前缀 `/tmp/quantlab_leaf35_etf_passive_*`） |
| CLI | approved_cmd **exact**（`--universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path … --out …`；外加 `nice -n 10`）；**无** `--no-overlap-report`；**无** `--enable-soft-penalty`；**无** FULLA PRIMARY；rss=1500 **禁抬且未抬** |
| expires | 窗→15:08 / expires **15:12 ET**（启动 13:53:13 ET；STOP≈13:53:16 ET；未逾窗） |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke / selfcheck；**勿复跑 / 勿改门 / 勿改脚本**（本拍已遵守） |

## 1. peak_proof 摘要（REQUIRED；部分 PRESENT，因 STOP 早退）

| 源 | 值 |
|---|---|
| log 全局 max peak_kb | **528588** @ `after_mask` |
| sampler max VmHWM | **528248** |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=**1500 未抬**） |
| stderr `ru_maxrss` @ build_start | **107136** |
| **`after_mask`** | **PRESENT** peak_kb=**528588** vmrss_kb=**528588** |
| **`after_weight_pin`** | **PRESENT** peak_kb=**528248** vmrss_kb=**460760** |
| **`after_etf_share_window`** | **PRESENT** peak_kb=**528248** vmrss_kb=**465852** |
| **`after_pressure_rebal_*`** | **PRESENT** n=**30**；max peak_kb=**528248**（含 `…_20261009`） |
| **`after_mask_cs_rebal_*`** | **ABSENT**（每日 `press empty/unmappable` → continue，未达 mask_cs） |
| **`after_daily_concat`** | **ABSENT**（STOP 于 rebal_rows 空） |
| 相对硬帽 | max_peak **528588** / 1536000 ≈ **34.4%**；**无 Exit 94/95** |
| ABORT_PEAK | **无** |

## 2. STOP 诊断（照实；未改脚本/未复跑）

- 路径：`raise SystemExit("STOP: zero mask rows …")` @ script L1498–1501 → **rc=1**
- 现象：`after_pressure_rebal_*` 打满 30 个 rebal day，但 **`rebal_rows` 始终为空** → 推断每日 `_pressure_on_day` 返回 `None/empty`（`pin_gaps gap=pressure_empty_or_unmappable`），故 **从未进入** `after_mask_cs_rebal_*` / daily concat / overlap 写出
- **未**写 overlap JSON（STOP 早于 overlap 阶段；CLI **未**带 `--no-overlap-report`）
- **未**产出 alpha / mask parquet / run_meta.json

## 3. 产物

| 文件 | 状态 |
|---|---|
| exclusion/overlay mask parquet | **无** |
| overlap JSON | **无** |
| run_meta.json | **无** |
| alpha parquet | **无** |
| stdout/stderr log | **有**（见上） |

coverage/n：无正式 coverage 落盘；日志侧仅能确认 30× pressure rebal 后 zero rows。

## 4. 门控与硬禁复核（跑后）

- `.ok` 仍 **`10927bd9`** 在位（**未删**；交 Arch CONSUME）
- QUIET 仍 **`c8d95fee`**；holder 未改；**未擅 lift**
- 脚本仍 **`25ae4572`**；叶33 仍 **`afbbe7e7`**
- forbid RESTORED 未触（本票仅 `10927bd9`）
- C3 方案 A / C4 mask-only top_q=0.20 / C11≠叶26：CLI 与脚本字节未改；本拍因 zero rows **未形成 PRIMARY mask 交付**
- rss=1500 未抬；peak_proof 以 log RSS_CHECK + sampler 为证
- EXECUTED=**true**（已真实执行批准命令）；结果=**STOP rc=1**；**≠X2 ACCEPT**
- leo_notify=false；live=false
- 备注：同 ET_TS 下曾有一次空 `--out` 误启（工具变量膨胀失败），**已立即 pkill**，未留产物；正式执行 pid=`470069` 为唯一计入回执的批准形态命令

## 5. 交主

交主 → Arch CONSUME（`.ok` 仍保留）。本执行器 **不**复跑、**不**改门、**不**改脚本、**不**自签 `.ok`、**不** lift QUIET。
