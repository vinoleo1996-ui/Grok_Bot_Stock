# AI 叶32 Margin Net Flow Resid X2 selfcheck_v1 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-27T05:28:09-04:00（America/New_York；墙钟 2026-10-27 05:28 ET） |
| 状态 | **DONE**（PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **ABSENT_UNTIL_SELFCHECK**→evaluate 已跑；勿称 X2 ACCEPT |
| rc | **0**（log 末行 `ok:true`） |
| decay.outcome | **KEEP**（reasons=[]；≠X2 ACCEPT；组合闸 verdict 仍 A/B/current=false） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_052540` |
| stamp（报告现盘） | `20261027_172541` |
| run_pid / sampler | `4008220`（nice=10；已 gone）/ `/tmp/quantlab_leaf32_x2_selfcheck_20261027_052540` 已停 |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1_HILIQ_X2.ok` sha8 **`5774bb6e`**（**仍在盘**；听 Arch CONSUME；forbid∋`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`3301eb86`**（**仍挂；未擅 lift**；holder=`leaf32_MARGIN_NET_FLOW_RESID_X2_SELFCHECK_V1`） |
| 脚本 | `research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py` sha8 **`dcf6b559`** |
| 构建脚本 | `research/leaf32_margin_net_flow_resid_alpha_build.py` sha8 **`4e0f3c00` UNCHANGED** |
| 模板 | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` sha8 **`e1fe578c` UNCHANGED** |
| Arch 审 / SIGNED / CMD | `3d7a5848` / `e00f8f51` / **`754bf251`**（禁 `--arch-ok-path`） |
| RUNNING_ACK | **`33088baa`** |
| Alpha 闸 / CONSUME / FROZEN | `1aa432a5` / `a1a5e35a` / `6b8de5e9` |
| 主窗 | **05:18–06:48** expires **06:50** |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf32_margin_net_flow_resid_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf32_x2_selfcheck_20261027_052540` |
| log | `output/ai_factory/_leaf32_margin_flow/20261027_042805/_selfcheck/_logs/run_20261027_052540.log` sha8 **`30b12ef7`**（末行 `ok:true` `rss_mb:923.17`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| alpha `…/alpha_HILIQ_x2_20261027_044214.parquet` | **`13eee6fd`** | UNCHANGED |
| meta `…/run_meta.json` | **`e510f346`** | UNCHANGED |
| overlap `…/overlap_vs_leaf19_25_27_30_31_margin_delta.json` | **`a643d71a`** | UNCHANGED |
| 构建 `leaf32_margin_net_flow_resid_alpha_build.py` | **`4e0f3c00`** | UNCHANGED |
| 脚本 selfcheck | **`dcf6b559`** | UNCHANGED |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `…/_selfcheck/eval_weights_HILIQ_x2_20261027_172541.parquet` sha8 **`6ef6741a`**（全长 `6ef6741a761b6c1ad78524ae9f26169404fb0974b3ed783f4b7b8d64d28fa820`） |
| selfcheck_v1.json（=side_meta） | `output/ai_factory/leaf_reports/leaf32_margin_flow/selfcheck_v1.json` sha8 **`99675387`**（全长 `996753878d9ebfeb67f7c3076194c84ec7ad6b644ed69f0024b9beb4b4b82692`） |
| side_meta | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_172541.json` sha8 **`99675387`**（=report） |
| n_weight_rows / n_weight_days | `11970` / `570` |
| mechanism | `g1g5_ashare_margin_net_flow_resid_v1` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log `rss_mb` / side_meta `rss_mb_peak_self` | **923.17** MB |
| sampler peak_rss_kb / peak_hwm_kb | **646172** / **945328** KB（HWM≈**923.17** MB；与 ru_maxrss 对齐） |
| 相对软帽 1500 | **PASS**（max≈923.17 ＜ 1500；未触发 ABORT_RSS） |

## 评价摘要（入口票数字 · **≠X2 ACCEPT**）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false**（60w A/B/current=false；100w current=true / B=true / A=false；总 verdict 取严） |
| 60万 overlay | CAGR≈26.34% · MDD≈-15.15% · Calmar≈1.74 |
| 100万 overlay | CAGR≈24.63% · MDD≈-11.88% · Calmar≈2.07 |
| 60万 A_debeta | CAGR≈18.59% · MDD≈-14.65% · Calmar≈1.27 |
| 100万 A_debeta | CAGR≈19.04% · MDD≈-13.23% · Calmar≈1.44 |
| 60万 cap | CAGR≈17.85% · MDD≈-14.24% · Calmar≈1.25 |
| 100万 cap | CAGR≈18.30% · MDD≈-12.47% · Calmar≈1.47 |
| decay.outcome | **KEEP**（reasons=[]；latest_resid_alpha≈0.123；consecutive_declines=1；net_cagr≈4.96%；叶30/31 曾 DECAY_DOWNGRADE — 本票不同） |
| cost | untradable=**True**；gross_cagr≈16.67%；net_cagr≈12.45%；gross_excess≈5.41%；cost_drag_ann≈3.69%；reasons=['成本拖累>毛超额一半'] |
| live / book_smoke / x2_accept | 全 **false** |

> 上表仅为 selfcheck 入口披露；**不构成** X2 ACCEPT / Book-Smoke / 晋级。decay=KEEP ≠ 组合闸通过（verdict A/B/current 仍 false）。下一跳听主/Arch CONSUME。

## 硬钉收尾

- **PRIMARY 已完**；**禁自复跑**；**禁抬帽**；**禁改构建 `4e0f3c00`**；**禁覆写钉盘 alpha·meta·overlap**
- `.ok` `5774bb6e` / QUIET `3301eb86` **仍在**；**未擅 lift**；听 Arch CONSUME+lift
- forbid RESTORED 二十票含 **`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`** 仍有效
- FALLBACK 无；Arch 不代跑；≠A18；禁 `--arch-ok-path`；`0087c928` 另队
- ≠X2 ACCEPT；≠Book-Smoke；勿宣称 ACCEPT

**leo_notify=false** · live=false
