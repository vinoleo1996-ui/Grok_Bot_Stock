# AI 回执：叶35 ETF Passive Flow Pressure Overlay X2 B1 · DONE（rc=0）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI 后台执行器 |
| 时刻 | **2026-10-27 15:30:11 EDT**（America/New_York） |
| **结论** | **DONE rc=0**（stdout 末行 `OK … peak_kb=714280 overlap_hard_reject=False pin_gap=False`；无 Exit 94/95；无 Traceback；**已产出** exclusion_mask / overlap / run_meta） |
| ET_TS | `20261027_152756` |
| run_pid | `561293`（已退出；nice=10；pgrep 现空） |
| **rc** | **0** |
| status | **OK_MASK_WRITTEN** |
| script | `research/leaf35_etf_passive_flow_pressure_overlay_alpha_build.py` sha8 **`434ff42c`** / 全长 `434ff42c1ba7998e122e0ded4f984c98d40ecbfc12f124afe7ef99742bd69b0a`（现核 MATCH；**未改**；禁把 `25ae4572` 当活脚本） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` sha8 **`eb70eef4`** / 全长 `eb70eef4386ae856f5f0b02733bca718ff96125765556fd72b70fefc82f94921`（现核 MATCH；**仍在位**；未自签/未删；交 Arch CONSUME） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`ef9b69b4`** / 全长 `ef9b69b486edb3ec8d679b7aae22d5d21e33cedff85db5cdfea331dfc80bac3b`（现核 MATCH；holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`；**未擅 lift / 未删 / 未改**） |
| SIGNED | sha8 **`65d89851`** / 全长 `65d89851ba1895b08d44156a5aef3820835b8854ea70772410e79a6a61a889f0`（钉）→ `docs/v2/audit/ARCH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_B1_OK_SIGNED_20261027_ZH.md` |
| 审 | sha8 **`df19dd2a` PASS_WITH_CONDITIONS**（钉）；补丁审 **`31a08790`** |
| RUNNING_ACK | sha8 **`474320ee`** / 全长 `474320ee312015cb44252c490fece778530c1312eee7ce7078e2ddb47ef72893` → `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_B1_RUNNING_ACK_20261027_152756_ZH.md` |
| leaf33 | `research/leaf33_share_unlock_pressure_resid_alpha_build.py` sha8 **`afbbe7e7` UNCHANGED** / 全长 `afbbe7e7292c17399bbf4733d9f34a922e6d81f1a914a60d24dc61fcba86cbc9` |
| out | `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/` |
| log | `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/stdout.log` + `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/stderr.log` + `/tmp/quantlab_leaf35_etf_passive_20261027_152756.log` |
| samp | `/tmp/quantlab_leaf35_etf_passive_20261027_152756_peak_sampler.tsv`（前缀 `/tmp/quantlab_leaf35_etf_passive_*`） |
| CLI | approved_cmd **exact**（`--universe HILIQ --window x2 --x2-end 20261009 --allow-real-data --arch-ok-path … --out …`；外加 `nice -n 10`）；**无** `--no-overlap-report`；**无** `--enable-soft-penalty`；**无** FULLA PRIMARY；rss=1500 **禁抬且未抬** |
| expires | 窗→16:49 / expires **16:53 ET**（启动≈15:28:15 ET；完成≈15:28:44 ET；未逾窗） |
| MemAvailable@prelaunch | **12840968** kB（软底；未抬 rss） |
| live | false |
| leo_notify | false |
| ≠ | X2 ACCEPT / Book-Smoke / selfcheck；**勿复跑 / 勿改门 / 勿改脚本**（本拍已遵守） |

## 1. peak_proof 摘要（REQUIRED；PRESENT）

| 源 | 值 |
|---|---|
| OK 行 / 全局 max peak_kb | **714280** |
| sampler max VmHWM | **714280** |
| sampler max VmRSS | **664360** |
| RSS_CHECK 序列内 max（至 `after_daily_concat`） | **520912** @ `after_daily_concat` |
| run_meta `peak_kb` / `peak_kb_final` | **520976** / **520256** |
| hard / soft / split / c4 | hard=1536000 soft=1536000 split=1131520 c4=1331200（rss_limit_mb=**1500 未抬**） |
| stderr `ru_maxrss` @ build_start | **106992** |
| **`after_mask`** | **PRESENT** peak_kb=**516768** vmrss_kb=**516768** |
| **`after_weight_pin`** | **PRESENT** peak_kb=**516204** vmrss_kb=**445808** |
| **`after_etf_share_window`** | **PRESENT** peak_kb=**516204** vmrss_kb=**450728** |
| **`after_pressure_rebal_*`** | **PRESENT** n=**30**（含 `…_20261009`） |
| **`after_mask_cs_rebal_*`** | **PRESENT** n=**30** |
| **`after_daily_concat`** | **PRESENT** peak_kb=**520912** vmrss_kb=**520912** |
| 相对硬帽 | max_peak **714280** / 1536000 ≈ **46.5%**；**无 Exit 94/95** |
| ABORT_PEAK | **无** |

## 2. 产物（路径 + sha8 + 全长）

| 文件 | sha8 | 全长 |
|---|---|---|
| `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/exclusion_mask_HILIQ_x2_20261027_152844.parquet` | **`576ca398`** | `576ca398c0327d0ebbe434bada568ffc56bee8800f9a14ea177e2ba549d7e650` |
| `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/overlap_vs_moneyflow_leaf26resid_8a_25_27_30_31_32_33_34.json` | **`54933299`** | `54933299df35cb7941888eff3e59b1c08a0079854ef3d209b9d247ca3194e160` |
| `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/run_meta.json` | **`2bb21a76`** | `2bb21a760a8dfb7cfa18787aa118f961138dd937e6da90c7e7b28906e22d6fbc` |
| `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/stdout.log` | **`e3f755ab`** | `e3f755ab63196c0687fb0c806558f1555b6a1fda9d4e0f3b74d8ccb0c5071604` |
| `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756/stderr.log` | **`6e93c03c`** | `6e93c03c17f7d354f923aa439e79f4eaf451107690e5fc74106e760b19c17cb2` |
| alpha parquet | **无**（mask-only PRIMARY；符合 C3） |

coverage：median=**1552.5**；gate=300 **PASS**；n_daily_rows=**815854**；n_month_chunks=**29**；leaf26_like_raw_days=**30**；n_pin_gaps=**0**（required）。

## 3. overlap / hard_reject

| 项 | 值 |
|---|---|
| `overlap_any_jaccard_hard_reject` | **False** |
| `overlap_any_required_pin_gap` | **False** |
| jaccard_hard 阈值 | **0.7** |
| sample_dates n | **6** |
| max j20（硬拒同伴；leaf26_like_raw 诊断除外） | leaf25/leaf30=**0.052632**；leaf27/32/34=**0.025641**；moneyflow/leaf31/leaf33=**0.0**（均 ≪0.7） |
| j20_leaf26_like_raw max | **1.0**（by-construction 诊断；**NOT** hard reject；C7/C11） |
| optional PIN_GAP | leaf26_resid / leaf8a missing_file（optional=True；不构成 required pin_gap） |

## 4. 门控与硬禁复核（跑后）

- `.ok` 仍 **`eb70eef4`** 在位（**未删**；交 Arch CONSUME）
- QUIET 仍 **`ef9b69b4`**；holder 未改；**未擅 lift**
- 脚本仍 **`434ff42c`**；叶33 仍 **`afbbe7e7` UNCHANGED**
- forbid RESTORED 未触（本票仅 `eb70eef4`；禁 `00eec671`+`10927bd9`+`25ae4572`+旧票）
- C3 方案 A / C4 mask-only top_q=0.20 / C11≠叶26：CLI 与脚本字节未改；PRIMARY=mask-only 已落盘
- rss=1500 未抬；peak_proof 以 log RSS_CHECK + sampler + OK 行为证
- EXECUTED=**true**（已真实执行批准命令）；结果=**DONE rc=0**；**≠X2 ACCEPT**
- leo_notify=false；live=false
- 本拍未 Book-Smoke；未开叶36；未改脚本

## 5. 交主

交主 → Arch CONSUME（`.ok` 仍保留；QUIET 未 lift）。本执行器 **不**复跑、**不**改门、**不**改脚本、**不**自签 `.ok`、**不** lift QUIET。
