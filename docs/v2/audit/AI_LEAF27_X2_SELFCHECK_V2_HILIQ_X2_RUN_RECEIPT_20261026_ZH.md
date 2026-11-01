# AI 叶27 X2 selfcheck_v2 · HILIQ×x2 RUN_RECEIPT

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | 2026-10-26T01:06:10-04:00（America/New_York；墙钟 2026-10-26 01:06 ET） |
| 状态 | **DONE**（单次 PRIMARY 完结；**非 ABORT**；**禁自复跑**） |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| SELFCHECK_EXECUTED | **true**（本票 evaluate 已跑；≠X2 ACCEPT） |

## 盘证钉

| 项 | 值 |
|---|---|
| ET_TS | `20261026_010504` |
| run_pid / sampler_pid | `2008153` / `2008152`（**均 gone**） |
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.ok` sha8 **`3c19dd7d`**（**仍在盘**；听 Arch CONSUME/VOID；∉ forbid 八票） |
| QUIET | `output/loop/RESEARCH_QUIET.lock` sha8 **`69cd9d8e`**（**仍挂；未擅 lift**） |
| 脚本 | `research/leaf27_x2_selfcheck_v2.py` sha8 **`a40d7069`** |
| 构建脚本 | `research/leaf27_chunked_members_mktcap_r1.py` sha8 **`585ba746` UNCHANGED**（未改） |
| 主 GO / 窗 | `0e5a37e2` / `f268d120` **00:55–01:40** expires **01:42** |
| Arch 审 / SIGNED | `46526394` / `b5484e5a` |
| HAND / H2A / COVER / CMD / DIFF / VERIFY / PIN | `3dd71dc3` / `48aa5db7` / `1e28d0e5` / `61c3ef3b` / `1c4fb74a` / `c47be63a` / `4e0473bd` |
| RUNNING_ACK | sha8 **`472c8b50`** |
| CLI | `PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/leaf27_x2_selfcheck_v2.py --universe HILIQ --window x2 --alpha-path output/ai_factory/leaf27_on_minus_id_idio_ivol/alpha_HILIQ_x2_20261025_224033.parquet --execute` |
| rss_limit | **1500** MB（**未抬**） |
| sampdir | `/tmp/quantlab_leaf27_x2_selfcheck_20261026_010504` |
| log | `output/ai_factory/leaf27_on_minus_id_idio_ivol/_selfcheck/_logs/run_20261026_010504.log`（末行 `ok:true` `rss_mb:1123.44`） |

## 钉盘未覆写（MATCH）

| 件 | sha8 | 状态 |
|---|---|---|
| alpha `…/alpha_HILIQ_x2_20261025_224033.parquet` | **`652b8a68`** | UNCHANGED |
| meta `…/run_meta_HILIQ_x2_20261025_224033.json` | **`85c2dc78`** | UNCHANGED |
| summary `…/build_summary_20261025_224333.json` | **`80596bff`** | UNCHANGED |

## 产物（本票新建）

| 件 | sha8 / 值 |
|---|---|
| eval_weights | `…/_selfcheck/eval_weights_HILIQ_x2_20261026_010504.parquet` sha8 **`7fc3b828`**（全长 `7fc3b8285c346c2620a3874855e1dbdd42a662da5b204c2c00191b3fc52fcd74`） |
| selfcheck_v2.json | `output/ai_factory/leaf_reports/leaf27_on_minus_id_idio_ivol/selfcheck_v2.json` sha8 **`b5182220`**（全长 `b5182220df7e09a15fb3749f8871e5580b00c56ef27d345a82c9092ba44c3f6a`） |
| side_meta | `…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261026_010504.json` |
| n_weight_rows / n_weight_days | `11970` / `570` |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| `rss_mb_peak_self`（ru_maxrss） | **1123.44** MB |
| `evaluate.peak_rss_mb` | **1123.44140625** MB |
| sampler peak_kb（30s） | **684904** KB（≈668.9 MB；末行 `EXIT`；30s 采样低于进程 HWM，以 ru_maxrss 为准） |
| 相对软帽 1500 | **PASS**（1123.44 ＜ 1500；未触发 ABORT_RSS） |

## 评价摘要（入口票数字 · **≠X2 ACCEPT**）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**true** · current=**false** |
| 60万 overlay | CAGR≈16.61% · MDD≈−12.92% · Calmar≈1.29 |
| 100万 overlay | CAGR≈19.14% · MDD≈−11.66% · Calmar≈1.64 |
| cost | untradable=true（成本拖累>毛超额一半）；net_cagr≈7.01% |
| decay.outcome | **DECAY_DOWNGRADE**（latest_alpha&lt;0；H2_net_cagr≤510300） |
| live / book_smoke / x2_accept | 全 **false** |

> 上表仅为 selfcheck 入口披露；**不构成** X2 ACCEPT / Book-Smoke / 晋级。下一跳听主/Arch。

## 硬钉收尾

- **单次已完**；**禁自复跑**；**禁抬帽**；**禁改构建 `585ba746`**；**禁覆写钉盘 alpha·meta·summary**
- `.ok` `3c19dd7d` / QUIET `69cd9d8e` **仍在**；**未擅 lift**；听 Arch CONSUME+lift
- forbid RESTORED 八票含 `0f50daf7` 仍有效
- FALLBACK 无；Arch 不代跑

live=false。
