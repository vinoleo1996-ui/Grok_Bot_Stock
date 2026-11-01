# AI 叶25 X2 selfcheck_v2 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-26T16:26:12-0400（America/New_York；墙钟 2026-10-26 16:26 ET） |
| 状态 | **DONE**（单次 PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |
| PIN_GAP | **PARTIAL**（β120/mom/logADV20/vol20；CFACC 已实装；勿称全残差齐） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261026_162438` |
| stamp | `20261026_162440` |
| run_pid / sampler_pid | `2819312`（shell 启）→ python 短跑已 gone / `2819316`（已停） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ok` sha8 **`ebc673bf`**（**仍在盘**；听 Arch CONSUME/VOID；∉ forbid 十二票含 `3c297052`） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`5282f37f`**（**仍挂；未擅 lift**） |
| 脚本 | `research/leaf25_x2_selfcheck_v2.py` sha8 **`b1db0886`** |
| 构建脚本 | `research/leaf25_full_factor_alpha_build_r1.py` sha8 **`de7b3647` UNCHANGED**（未改） |
| Arch 审 / SIGNED | `23f371a1` / `8958c993` |
| 主窗 | **16:15–17:45** expires **17:47** |
| HAND / H2A / COVER / CMD / DIFF / VERIFY / PIN | `41c9d8a6` / `13294f83` / `c151d351` / `e2dde42d` / `eba5b6b2` / `7b7ad21c` / `16706b04` |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf25_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/_leaf25_full_factor/20261026_015610/alpha_HILIQ_x2_20261026_125138.parquet --execute` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf25_x2_selfcheck_20261026_162438` |
| log | `output/ai_factory/_leaf25_full_factor/20261026_015610/_selfcheck/_logs/run_20261026_162438.log` sha8 **`158ec3e3`**（末行 `ok:true` `rss_mb:1009.16`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| alpha `…/alpha_HILIQ_x2_20261026_125138.parquet` | **`8be12024`** | UNCHANGED |
| meta `…/run_meta.json` | **`44c27f54`** | UNCHANGED |
| 构建 `leaf25_full_factor_alpha_build_r1.py` | **`de7b3647`** | UNCHANGED |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `…/_selfcheck/eval_weights_HILIQ_x2_20261026_162440.parquet` sha8 **`48f729df`**（全长 `48f729df5f711aa87417bf14f3ff475c9900897351a26aebccde09140f366c49`） |
| selfcheck_v2.json | `output/ai_factory/leaf_reports/leaf25_full_factor/selfcheck_v2.json` sha8 **`a95f192f`**（全长 `a95f192fb410726cb52b13465625481c395bf149df6be2ab45165ce0617500e9`） |
| side_meta | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261026_162440.json` sha8 **`a95f192f`**（与 report 同内容） |
| n_weight_rows / n_weight_days | `11970` / `570` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| `rss_mb_peak_self`（ru_maxrss） | **1009.16** MB |
| `evaluate.peak_rss_mb` | **1009.15625** MB |
| sampler peak_kb（30s） | **2228** KB（≈2.2 MB；跑时 <30s，仅采到 shell 启程；**以 ru_maxrss 为准**） |
| 相对软帽 1500 | **PASS**（1009.16 ＜ 1500；未触发 ABORT_RSS） |

## 评价摘要（入口票数字 · **≠X2 ACCEPT**）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false**（60万档 B=true 但 100万 B=false → 总 B=false） |
| 60万 overlay | CAGR≈19.70% · MDD≈−14.52% · Calmar≈1.36 |
| 100万 overlay | CAGR≈19.01% · MDD≈−13.43% · Calmar≈1.42 |
| cost | untradable=true（无毛超额且成本拖累>1%/年）；gross_cagr≈6.70% · net_cagr≈4.69% · bench≈11.26% |
| decay.outcome | **DECAY_DOWNGRADE**（latest_alpha&lt;0；H2_net_cagr≤510300） |
| live / book_smoke / x2_accept | 全 **false** |

> 上表仅为 selfcheck 入口披露；**不构成** X2 ACCEPT / Book-Smoke / 晋级。下一跳听主/Arch。

## 硬钉收尾

- **单次已完**；**禁自复跑**；**禁抬帽**；**禁改构建 `de7b3647`**；**禁覆写钉盘 alpha·meta**
- `.ok` `ebc673bf` / QUIET `5282f37f` **仍在**；**未擅 lift**；听 Arch CONSUME+lift
- forbid RESTORED 十二票含 **`3c297052`** 仍有效
- PIN_GAP **PARTIAL** 须保留披露
- FALLBACK 无；Arch 不代跑；≠A18

live=false。
