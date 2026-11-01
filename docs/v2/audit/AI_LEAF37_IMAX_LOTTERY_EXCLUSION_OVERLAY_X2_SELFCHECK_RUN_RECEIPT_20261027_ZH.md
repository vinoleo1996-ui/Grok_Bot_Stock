# AI 叶37 IMAX Lottery Exclusion Overlay X2 selfcheck_v1 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-27T19:31:39-04:00（America/New_York；墙钟 2026-10-27 19:31–19:32 ET） |
| 状态 | **DONE**（PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA**（mask-only；无完整主 α TopN；勿称 X2 ACCEPT） |
| rc | **0**（log 末 `ok:true`） |
| decay.outcome | **KEEP**（reasons=[]；≠X2 ACCEPT；组合闸 verdict A/B/current=false；KEEP≠ACCEPT） |
| KEEP 不解阻 X2 ACCEPT | **true**（`45dd87dc`；叶36 HOLD 不复开） |
| web_exempt | **false**（prelaunch#2 pgrep **空**；未命中 quantlab-web） |
| leo_notify | **false** |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS / stamp | `20261027_193125`（ET 启跑） / 脚本内 stamp `20261028_073125`（UTC=now） |
| run_pid | `851818`（已 gone） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1.ok` sha8 **`57ab9096`**（全长 `57ab909622f1edaf2c19dd3f40824a20b6ef407b8b3436c9dafe1fabc820fa64`；**仍在盘未自 consume**；听 Arch CONSUME/VOID；forbid∋`b5be1164`+`4096d401`+… n=32；新 ok ∉ forbid） |
| QUIET | **ABSENT**（本窗 `ban_hang_quiet_this_sign`；**未挂**；签时 QUIET ABSENT 保持） |
| 脚本 | `research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py` sha8 **`015e6f06` only**（全长 `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61`） |
| B1 构建 / 基盘 | **`32605aca` UNCHANGED ban_as_live** / **`108aba8f` UNCHANGED ban_as_live（本窗不跑）** |
| Arch SIGNED / 审 / CONSUMED | **`b1fc8325`** / **`3d40f713` PASS_WC** / **`c0a6b5ae`** |
| COVER / CMD / DIFF / RECEIPT(脚本) | **`8c83ba13`** / **`6f5d48bd`** / **`2542e7cd`** / **`bb616bdb`** |
| 主窗 | **19:17→20:47** expires **20:51** ET（本跑未过期） |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf37_imax_lottery_exclusion_overlay_x2_selfcheck_v1.py --universe HILIQ --window x2 --execute`（**禁 `--arch-ok-path`**；未加） |
| rss_limit | **1500** MB（**未抬**；未破硬帽） |
| log | `output/ai_factory/_leaf37_imax_lottery/20261027_193125_selfcheck_logs/run_20261027_193125.log` sha8 **`95f5d040`**（末 `ok:true` `rss_mb:960.07`） |
| sampler | `/tmp/quantlab_leaf37_x2_selfcheck_20261027_193125.tsv`（prefix `/tmp/quantlab_leaf37_x2_selfcheck_`） |

## prelaunch（本拍重做 MATCH）

| 步 | 结果 |
|---|---|
| 1 sha `.ok`/脚本/mask/meta/overlap | **ALL MATCH** `57ab9096`/`015e6f06`/`2503a41e`/`e9e9aa1d`/`8177578f` |
| 2 sleep≥15s + pgrep | **空** → 继续；web_exempt=**false** |
| 3 dry-compile-only | **rc=0**；pin_sha_match；rows=1421604；rss_mb≈68.71 |
| 4 MemAvailable | ≈12.5Gi（软地板≈12.4Gi） |
| 5 QUIET | **ABSENT**（禁挂保持） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| mask `…/exclusion_mask_HILIQ_x2_20261027_183755.parquet` | **`2503a41e`** | UNCHANGED |
| meta `…/run_meta.json` | **`e9e9aa1d`** | UNCHANGED |
| overlap `…/overlap_vs_leaf18_18v_27_hard_24_34_35_36_disclose.json` | **`8177578f`** | UNCHANGED |
| 脚本 selfcheck | **`015e6f06`** | UNCHANGED |
| B1 / 基盘 | **`32605aca`** / **`108aba8f`** | UNCHANGED；未跑 |
| `.ok` / QUIET | **`57ab9096`** / **ABSENT** | `.ok` 仍在；未挂 QUIET |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `output/ai_factory/_leaf37_imax_lottery/20261027_183719/_selfcheck/eval_weights_HILIQ_x2_20261028_073125.parquet` sha8 **`f05f1300`**（全长 `f05f130015ca1598953e8c05407b58fcadfc3d115ac68479dbaab0666320363b`） |
| selfcheck_v1.json（=side_meta） | `output/ai_factory/leaf_reports/leaf37_imax_lottery/selfcheck_v1.json` sha8 **`d27a53f5`**（全长 `d27a53f53ebaded3c242e5f2e54222665858b821b28d87fe7312e2302e457919`） |
| side_meta | `output/ai_factory/_leaf37_imax_lottery/20261027_183719/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261028_073125.json` sha8 **`d27a53f5`**（=report） |
| n_weight_rows / n_weight_days | `13321` / `668` |
| mechanism | `g1g5_ashare_imax_lottery_exclusion_overlay_v1` |
| primary_delivery / top_q / C3 | `mask_only` / `0.20` / **B** IMAX_proxy；b1_lowmem=true |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log/side_meta `rss_mb` / `rss_mb_peak_self` / `peak_proof.ru_maxrss_mb` | **960.07** MB |
| peak_rss_kb（ru_maxrss×1024） | **983112** KB |
| 外部 sampler VmRSS peak / VmHWM peak | **969756** / **983112** KB（`/tmp/quantlab_leaf37_x2_selfcheck_20261027_193125.tsv`） |
| 上游 B1 build_meta `peak_kb`（只读引用） | **1107536**（本票 selfcheck 峰以 ru_maxrss=960.07 为准） |
| 硬帽 1500 MB | **未破**（960.07 < 1500；**禁抬**） |
| sampler_prefix | `/tmp/quantlab_leaf37_x2_selfcheck_` |

## 闸门 / decay / ρ_excess（复述；≠X2 ACCEPT）

| 项 | 值 |
|---|---|
| Gate A / B / current（verdict） | **False** / **False** / **False** |
| 60w A/B/current | False / False / False |
| 100w A/B/current | False / **True** / False |
| 60w overlay cagr/mdd/calmar | 0.126870 / -0.141276 / 0.898028 |
| 100w overlay cagr/mdd/calmar | 0.150845 / -0.123512 / 1.221301 |
| decay.outcome | **KEEP** |
| latest_resid_alpha | 0.023212 |
| consecutive_declines | 0 |
| decay net_cagr / bench_net_cagr | 0.007825 / -0.033709 |
| cost net_cagr / gross_cagr / bench_cagr | 0.112928 / 0.125226 / 0.119283 |
| ρ_excess vs capacity_adv | **0.958902**（阈值 <0.5 未过；本值≫0.5） |
| x2_accept | **false** |
| keep_does_not_unblock_x2_accept | **true** |
| untradable (cost) | true（成本拖累>毛超额一半；披露不改 KEEP≠ACCEPT） |

## 禁项核验

- **未挂/未 lift QUIET**；未自重跑；未抬帽；未 RESTORED `b5be1164`+`4096d401`+…；未 Book-Smoke；未自称 X2 ACCEPT
- 未传 `--arch-ok-path`；未跑 B1/`108aba8f`；未自签/改 `.ok`；未 git commit
- 未夹带 `0087c928`/28/29；leo_notify=false；live=false；promotion=false

## 交 Arch / 主

`.ok` **`57ab9096`** 仍在盘 → **请主→Arch CONSUME/VOID**（本拍 AI 不 consume、不挂 QUIET）。≠X2 ACCEPT；KEEP≠ACCEPT。
