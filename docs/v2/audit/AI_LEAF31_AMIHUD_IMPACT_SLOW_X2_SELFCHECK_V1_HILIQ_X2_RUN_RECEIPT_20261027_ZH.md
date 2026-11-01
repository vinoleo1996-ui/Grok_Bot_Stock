# AI 叶31 Amihud Impact Slow X2 selfcheck_v1 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-27T03:25:43-04:00（America/New_York；墙钟 2026-10-27 03:25 ET） |
| 状态 | **DONE**（PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **ABSENT_UNTIL_SELFCHECK**→evaluate 已跑；勿称 X2 ACCEPT |
| rc | **0**（log 末行 `ok:true`） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_032306` |
| stamp（报告现盘） | `20261027_152340`（见下方「二次写盘说明」） |
| 首跑 stamp | `20261027_152306`（PRIMARY log 对齐） |
| run_pid / sampler | `3876415`（nice=10；已 gone）/ `/tmp/quantlab_leaf31_x2_selfcheck_20261027_032306` 已停 |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.ok` sha8 **`4bb141c9`**（**仍在盘**；听 Arch CONSUME；forbid∋`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`351e98fb`**（**仍挂；未擅 lift**） |
| 脚本 | `research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py` sha8 **`e1fe578c`** |
| 构建脚本 | `research/leaf31_amihud_impact_slow_alpha_build.py` sha8 **`08f37fd2` UNCHANGED** |
| 模板 | `research/leaf30_crr_x2_selfcheck_v1.py` sha8 **`797724d4` UNCHANGED** |
| Arch 审 / SIGNED / CMD | `0db69426` / `e3657034` / **`25c16a2b`**（禁 `--arch-ok-path`） |
| RUNNING_ACK | **`3b83036d`** |
| 主窗 | **03:17–04:47** expires **04:49** |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf31_amihud_impact_slow_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf31_x2_selfcheck_20261027_032306` |
| log | `output/ai_factory/_leaf31_amihud/20261027_024204/_selfcheck/_logs/run_20261027_032306.log` sha8 **`b1c3c481`**（末行 `ok:true` `rss_mb:1015.01`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| alpha `…/alpha_HILIQ_x2_20261027_024422.parquet` | **`d4ceb78b`** | UNCHANGED |
| meta `…/run_meta.json` | **`696ab1cc`** | UNCHANGED |
| overlap `…/overlap_vs_leaf19_25_27_30.json` | **`8396f211`** | UNCHANGED |
| 构建 `leaf31_amihud_impact_slow_alpha_build.py` | **`08f37fd2`** | UNCHANGED |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights（字节同；两 stamp） | `…/_selfcheck/eval_weights_HILIQ_x2_20261027_152306.parquet` 与 `…_152340.parquet` sha8 **`346cf077`**（全长 `346cf077eaf95a7c15cf6981e3189ef3c4e5aeaf4da73007129c85720e2698d8`；**byte-identical**） |
| selfcheck_v1.json（现盘=stamp 152340） | `output/ai_factory/leaf_reports/leaf31_amihud/selfcheck_v1.json` sha8 **`d4553423`**（全长 `d4553423f2f7d2cd8dc8c1628f2c8cf439fe3f49d3f343e84cba8e6373ecbf1e`） |
| side_meta 152340 | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_152340.json` sha8 **`d4553423`**（=report） |
| side_meta 152306 | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_152306.json` sha8 **`051a4022`** |
| n_weight_rows / n_weight_days | `11970` / `570` |
| mechanism | `g1g5_ashare_amihud_impact_slow_v1` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log `rss_mb` / side_meta 152306 | **1015.01** MB |
| 现盘 `rss_mb_peak_self`（ru_maxrss @152340） | **987.86** MB |
| sampler peak_rss_kb / peak_hwm_kb | **860404** / **1039368** KB（HWM≈**1015.0** MB；以 PRIMARY ru_maxrss/HWM 为准） |
| 相对软帽 1500 | **PASS**（max≈1015.01 ＜ 1500；未触发 ABORT_RSS） |

## 二次写盘说明（透明披露 · 非抬帽 · 非 RESTORED）

PRIMARY `ET_TS=20261027_032306` pid=`3876415` 已 `ok:true` 后，AI 写 RUNNING_ACK 时 shell 未引用 heredoc 导致 approved_cmd 反引号被二次展开，**误触同窗同 `.ok` 再跑一次**（stamp `20261027_152340`；无第二 log/samp）。两趟 eval_weights **字节完全相同**（sha8 `346cf077`）；现盘 `selfcheck_v1.json` 为 152340。**禁再复跑**；听 Arch CONSUME 口径。≠抬帽；≠改脚本；≠覆写钉盘 alpha/meta/overlap。

## 评价摘要（入口票数字 · **≠X2 ACCEPT**）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false**（60w/100w A=false） · B=**false** · current=**false** |
| 60万 overlay | CAGR≈16.82% · MDD≈-13.64% · Calmar≈1.23 |
| 100万 overlay | CAGR≈17.76% · MDD≈-13.07% · Calmar≈1.36 |
| 60万 A_debeta | CAGR≈14.40% · MDD≈-15.64% · Calmar≈0.92 |
| 100万 A_debeta | CAGR≈14.80% · MDD≈-14.25% · Calmar≈1.04 |
| 60万 cap | CAGR≈17.85% · MDD≈-14.24% · Calmar≈1.25 |
| 100万 cap | CAGR≈18.30% · MDD≈-12.47% · Calmar≈1.47 |
| decay.outcome | **DECAY_DOWNGRADE**（reasons=['latest_alpha<0', 'alpha_declined_5q', 'H2_net_cagr<=510300']） |
| cost | untradable=**True**；gross_cagr≈-1.91%；net_cagr≈-4.80%；gross_excess≈-13.17%；cost_drag_ann≈3.01%；reasons=['无毛超额且成本拖累>1%/年'] |
| live / book_smoke / x2_accept | 全 **false** |

> 上表仅为 selfcheck 入口披露；**不构成** X2 ACCEPT / Book-Smoke / 晋级。下一跳听主/Arch CONSUME。

## 硬钉收尾

- **PRIMARY 已完**；**禁自复跑**；**禁抬帽**；**禁改构建 `08f37fd2`**；**禁覆写钉盘 alpha·meta·overlap**
- `.ok` `4bb141c9` / QUIET `351e98fb` **仍在**；**未擅 lift**；听 Arch CONSUME+lift
- forbid RESTORED 十八票含 **`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`** 仍有效
- FALLBACK 无；Arch 不代跑；≠A18；禁 `--arch-ok-path`；`0087c928` 另队

**leo_notify=false** · live=false
