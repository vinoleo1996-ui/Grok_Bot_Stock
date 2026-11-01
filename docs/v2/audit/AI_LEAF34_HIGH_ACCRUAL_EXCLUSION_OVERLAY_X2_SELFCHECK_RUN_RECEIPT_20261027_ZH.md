# AI 叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-27T11:53:59-04:00（America/New_York；墙钟 2026-10-27 11:53 ET） |
| 状态 | **DONE**（PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**（mask-only；无完整主 α TopN；勿称 X2 ACCEPT） |
| rc | **0**（log 末 `ok:true`） |
| decay.outcome | **KEEP**（reasons=[]；≠X2 ACCEPT；组合闸 verdict A/B/current=false） |
| KEEP 不解阻 X2 ACCEPT | **true**（`45dd87dc`） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS / stamp | `20261027_115317` / `20261027_115317` |
| run_pid | `341702`（nice=10；已 gone） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.ok` sha8 **`178e90e9`**（**仍在盘**；听 Arch CONSUME；forbid∋`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`3fce510e`**（**仍挂；未擅 lift**；holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1`；窗→`13:13` expires `13:17` ET） |
| 脚本 | `research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`d210efba`** |
| 构建脚本 | `research/leaf34_high_accrual_exclusion_overlay_alpha_build.py` sha8 **`482009dc` UNCHANGED** |
| 模板 | 叶32 `dcf6b559` / 叶31 `e1fe578c` / common `218b61cf` / 叶33 `afbbe7e7`（只读） |
| Arch 审 / SIGNED / CMD | `e2902e64` / `56580a5c` / **`4255ad33`**（禁 `--arch-ok-path`） |
| RUNNING_ACK | **`571ed4a4`** → `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_RUNNING_ACK_20261027_ZH.md` |
| CONSUME / FROZEN / PIN | `fea9b3ff` / `8be1099e` / `bb418e6a` |
| 主窗 | **11:43–13:13** expires **13:17** ET |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute` |
| rss_limit | **1500** MB（**未抬**；未破硬帽） |
| log | `output/ai_factory/_leaf34_high_accrual/20261027_115317_selfcheck_logs/run_20261027_115317.log` sha8 **`6619946c`**（末 `ok:true` `rss_mb:956.92`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| mask `…/exclusion_mask_HILIQ_x2_20261027_105958.parquet` | **`8b5d6d24`** | UNCHANGED |
| meta `…/run_meta.json` | **`4fc6108d`** | UNCHANGED |
| overlap `…/overlap_vs_leaf19_25_27_30_31_32_33.json` | **`77368c8f`** | UNCHANGED |
| 构建 `leaf34_…_alpha_build.py` | **`482009dc`** | UNCHANGED |
| 脚本 selfcheck | **`d210efba`** | UNCHANGED |
| `.ok` / QUIET | **`178e90e9`** / **`3fce510e`** | 仍在；未 lift |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `output/ai_factory/_leaf34_high_accrual/20261027_105941/_selfcheck/eval_weights_HILIQ_x2_20261027_115317.parquet` sha8 **`680d516e`**（全长 `680d516e4b778271f7ec498d04774c41f1c45bd18e14d45ea971e919730ed6ce`） |
| selfcheck_v1.json（=side_meta） | `output/ai_factory/leaf_reports/leaf34_high_accrual/selfcheck_v1.json` sha8 **`b4b9208d`**（全长 `b4b9208d5d05c6cd91fed8a9270f10dbc59cf2f7bcbbbd1a1b50610733d11791`） |
| side_meta | `output/ai_factory/_leaf34_high_accrual/20261027_105941/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_115317.json` sha8 **`b4b9208d`**（=report） |
| n_weight_rows / n_weight_days | `12714` / `668` |
| mechanism | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| primary_delivery / top_q | `mask_only` / `0.2` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log `rss_mb` / side_meta `rss_mb_peak_self` / `peak_proof.ru_maxrss_mb` | **956.92** MB |
| peak_rss_kb（ru_maxrss×1024） | **979886** KB |
| 硬帽 1500 MB | **未破**（956.92 < 1500；禁抬） |
| sampler_prefix | `/tmp/quantlab_leaf34_x2_selfcheck_`（本跑以 ru_maxrss 为 PRIMARY peak_proof） |

## 闸门 / decay / ρ_excess（复述；≠X2 ACCEPT）

| 项 | 值 |
|---|---|
| Gate A / B / current（verdict） | **False** / **False** / **False** |
| 60w A/B/current | False / False / False |
| 100w A/B/current | False / False / False |
| 60w overlay cagr/mdd/calmar | 0.126117 / -0.142402 / 0.885638 |
| 100w overlay cagr/mdd/calmar | 0.151761 / -0.124679 / 1.217217 |
| decay.outcome | **KEEP** |
| latest_resid_alpha | 0.032080 |
| consecutive_declines | 0 |
| decay net_cagr / bench_net_cagr | 0.015512 / -0.033709 |
| cost net_cagr / gross_cagr / bench_cagr | 0.125241 / 0.136940 / 0.119283 |
| ρ_excess vs capacity_adv | **0.960841**（阈值 <0.5 未过；本值≫0.5） |
| x2_accept | **false** |
| keep_does_not_unblock_x2_accept | **true** |

## 禁项核验

- 未擅 lift QUIET；未自重跑；未抬帽；未 RESTORED；未 Book-Smoke；未自称 X2 ACCEPT
- 未传 `--arch-ok-path`；未夹带 `0087c928`/28/29；未触 A18；未改构建 `482009dc`
- leo_notify=false；live=false

## 交 Arch

`.ok` **`178e90e9`** + QUIET **`3fce510e`** 仍在 → **请 Arch CONSUME**（本拍 AI 不 lift）。≠X2 ACCEPT。
