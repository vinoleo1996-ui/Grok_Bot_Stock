# AI 叶30 CRR X2 selfcheck_v1 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-27T01:50:02-04:00（America/New_York；墙钟 2026-10-27 01:50 ET） |
| 状态 | **DONE**（单次 PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **ABSENT_UNTIL_SELFCHECK**→evaluate 已跑；勿称 X2 ACCEPT |
| rc | **0**（log 末行 `ok:true`） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261027_014833` |
| stamp | `20261027_134833` |
| run_pid / sampler_pid | `3705608`（nice=10；已 gone）/ `sampler.pid` 已停 |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.ok` sha8 **`aa25e989`**（**仍在盘**；听 Arch CONSUME；forbid∋`7e239487`+`5af20222`+`5ae077fa`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`0eb56fe2`**（**仍挂；未擅 lift**） |
| 脚本 | `research/leaf30_crr_x2_selfcheck_v1.py` sha8 **`797724d4`** |
| 构建脚本 | `research/leaf30_crr_cfooe_volpen_alpha_build_r3_peakcut.py` sha8 **`3ee9fed2` UNCHANGED** |
| Arch 审 / SIGNED / CMD | `3826aa63` / `21078eb5` / **`c25f1321`**（禁 `--arch-ok-path`） |
| RUNNING_ACK | **`fb690360`** |
| 主窗 | **01:44–03:14** expires **03:16** |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf30_crr_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf30_x2_selfcheck_20261027_014833` |
| log | `output/ai_factory/_leaf30_crr/20261027_003132/_selfcheck/_logs/run_20261027_014833.log` sha8 **`0d80a596`**（末行 `ok:true` `rss_mb:1027.0`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| alpha `…/alpha_HILIQ_x2_20261027_010815.parquet` | **`c8c7a5a5`** | UNCHANGED |
| meta `…/run_meta.json` | **`a6acfe27`** | UNCHANGED |
| overlap `…/overlap_vs_leaf19_25.json` | **`f9991d9d`** | UNCHANGED |
| 构建 `…_r3_peakcut.py` | **`3ee9fed2`** | UNCHANGED |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `…/_selfcheck/eval_weights_HILIQ_x2_20261027_134833.parquet` sha8 **`900970d4`**（全长 `900970d44adbec80fc1e96c39ab41cd1c823fac6107bded0a9da704c24c618e9`） |
| selfcheck_v1.json | `output/ai_factory/leaf_reports/leaf30_crr/selfcheck_v1.json` sha8 **`3eeffb02`**（全长 `3eeffb023e8f438ecb3e3ae7fb93df545bb2917dfd9bcdd2b713323224ccc58b`） |
| side_meta | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_134833.json` sha8 **`3eeffb02`** |
| n_weight_rows / n_weight_days | `11970` / `570` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| `rss_mb_peak_self`（ru_maxrss） | **1027.0** MB |
| `peak_proof.ru_maxrss_mb` | **1027.0** MB |
| sampler peak_kb（30s） | **357840** KB（≈349 MB；短跑；**以 ru_maxrss 为准**） |
| 相对软帽 1500 | **PASS**（1027.0 ＜ 1500；未触发 ABORT_RSS） |

## 评价摘要（入口票数字 · **≠X2 ACCEPT**）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**true**（60w A=true · 100w A=true） · B=**false**（60w B=false · 100w B=true） · current=**false**（60w=false · 100w=false） |
| 60万 overlay | CAGR≈16.22% · MDD≈-15.09% · Calmar≈1.08 |
| 100万 overlay | CAGR≈18.16% · MDD≈-11.49% · Calmar≈1.58 |
| 60万 A_debeta | CAGR≈18.13% · MDD≈-12.58% · Calmar≈1.44 |
| 100万 A_debeta | CAGR≈18.56% · MDD≈-11.13% · Calmar≈1.67 |
| decay.outcome | **DECAY_DOWNGRADE**（reasons=['latest_alpha<0', 'H2_net_cagr<=510300']） |
| cost | `{"cost_per_unit_to": 0.00175, "to_2s_mean": 0.0351493848857645, "gross_cagr": 0.14543121103481504, "net_cagr": 0.1284443368252559, "bench_cagr": 0.11259223120285178, "gross_excess": 0.032838979831963266, "cost_drag_ann": 0.015008787346221443, "untradable": false, "reasons": [], "net_cagr_t1": 0.1250` |
| live / book_smoke / x2_accept | 全 **false** |

> 上表仅为 selfcheck 入口披露；**不构成** X2 ACCEPT / Book-Smoke / 晋级。下一跳听主/Arch CONSUME。

## 硬钉收尾

- **单次已完**；**禁自复跑**；**禁抬帽**；**禁改构建 `3ee9fed2`**；**禁覆写钉盘 alpha·meta·overlap**
- `.ok` `aa25e989` / QUIET `0eb56fe2` **仍在**；**未擅 lift**；听 Arch CONSUME+lift
- forbid RESTORED 十六票含 **`7e239487`/`5af20222`/`5ae077fa`** 仍有效
- FALLBACK 无；Arch 不代跑；≠A18；禁 `--arch-ok-path`

**leo_notify=false** · live=false
