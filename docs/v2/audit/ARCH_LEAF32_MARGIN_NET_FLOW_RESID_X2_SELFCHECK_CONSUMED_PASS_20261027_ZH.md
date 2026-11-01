# Arch 叶32 Margin Net Flow Resid X2 selfcheck_v1 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T05:34:08-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `89c1f1b0` | DONE rc=**0**；ET_TS=`20261027_052540`；pid `4008220` gone |
| RUNNING_ACK | `33088baa` | MATCH |
| `.ok`（消费前） | `5774bb6e` | MATCH → 归档（全长 `5774bb6e8a1ad3e5dc879561b4cb3f08b9a6ad67e2bbdf34168f9c2117d26909`） |
| QUIET（lift 前） | `3301eb86` | MATCH；holder=`leaf32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1`；ok_sha8=`5774bb6e` → lift |
| 脚本 | `dcf6b559` | MATCH；**UNCHANGED**（全长 `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f`） |
| alpha / meta / overlap | `13eee6fd` / `e510f346` / `a643d71a` | **UNCHANGED** |
| report `selfcheck_v1.json` | `99675387` | MATCH（stamp `20261027_172541`；=side_meta） |
| eval_weights | `6ef6741a` | MATCH；`…/_selfcheck/eval_weights_HILIQ_x2_20261027_172541.parquet` |
| side_meta | `99675387` | MATCH；`…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_172541.json`（=report） |
| SIGNED / 审 | `e00f8f51` / `3d7a5848` | MATCH |
| 构建脚本 / 模板 | `4e0f3c00` / `e1fe578c` | UNCHANGED（本票未触） |
| Alpha 闸 / 构建 CONSUME / FROZEN | `1aa432a5` / `a1a5e35a` / `6b8de5e9` | 钉齐（本票未触） |
| ET_TS / pid / rc | `20261027_052540` / `4008220`（pgrep 空） / **0** | MATCH |

## gates / decay（披露；不解阻）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false** |
| 60w | A=false · B=false · current=false |
| 100w | A=false · B=true · current=true（总 verdict 取严 → 仍全 false） |
| decay.outcome | **KEEP**（reasons=[]；latest_resid_alpha≈0.123；consecutive_declines=1） |
| cost.untradable | **true**（reasons=`成本拖累>毛超额一半`） |
| pin_gap | Alpha 闸 `1aa432a5` 语境 ABSENT_UNTIL_SELFCHECK；本票 evaluate 已跑；**≠X2 ACCEPT** |
| x2_accept / promotion_approved / book_smoke | **false** / **false** / **false** |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log `rss_mb` / side_meta `rss_mb_peak_self` | **923.17** MB |
| sampler peak_rss_kb / peak_hwm_kb | **646172** / **945328** KB（HWM≈**923.17** MB） |
| rss_limit_mb | **1500**（**未抬**） |
| 相对软帽 | ≪1500；**PASS**（max≈923.17 ＜ 1500；未触发 ABORT_RSS） |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.5774bb6e.CONSUMED_PASS.20261027T0534ET.ok` 内容sha8 **`5774bb6e`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf32_margin_net_flow_resid_x2_selfcheck_PASS_LIFTED_20261027T0534ET.lock` 原sha8 **`3301eb86`** → lift后内容sha8 **`3301eb86`**（未改内容，sha 不变） |
| live `.ok` | **0**（本票 live path ABSENT；`ARCH_RUN_AUTH_*.ok` 顶层=0） |
| QUIET | **ABSENT** |
| pgrep leaf32_margin_net_flow_resid_x2_selfcheck / pid 4008220 | **空** |

## 硬钉

- 本票叶32 Margin Net Flow Resid X2 selfcheck_v1 收口；gates A/B/current **全 false**；decay=**KEEP** 须披露；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；下一令听主（请主排 Alpha 审闸）
- 禁 RESTORED：本票内容 **`5774bb6e`** + 二十票（七票在前）`02426b73` / `4bb141c9` / `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa` / `3c297052` / `e107383f` / `2be59acd` / `a7d98ac9` / `8e51de63` / `3a6caa4f` / `8bcd79dc` / `725be3e0` / `0f50daf7` / `3c19dd7d` / `1c32ab1e` / `6054b3bf` / `6de02e74`
- 钉 alpha `13eee6fd` / meta `e510f346` / overlap `a643d71a` / 脚本 `dcf6b559` / 构建 `4e0f3c00` / 模板 `e1fe578c` **未改**；禁触 A18；`0087c928` **未夹带**
- selfcheck 入口数字（含 portfolio_gates / decay KEEP）**不构成**晋级
- **不报 Leo**

live=false。
