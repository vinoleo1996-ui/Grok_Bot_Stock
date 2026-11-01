# Arch 叶25 X2 selfcheck_v2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-26T16:29:40-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `413d1871` | DONE 非 ABORT |
| `.ok`（消费前） | `ebc673bf` | MATCH → 归档 |
| QUIET（lift 前） | `5282f37f` | MATCH → lift |
| RUNNING_ACK | `5b80432c` | MATCH（可选） |
| 脚本 | `b1db0886` | MATCH |
| 构建 UNCHANGED | `de7b3647` | MATCH |
| 审 / SIGNED | `23f371a1` / `8958c993` | MATCH |
| alpha / meta | `8be12024` / `44c27f54` | UNCHANGED |
| eval_weights | `48f729df` | MATCH |
| selfcheck_v2.json | `a95f192f` | MATCH |
| log | `158ec3e3` | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| rss_mb_peak_self（ru_maxrss） | **1009.16** / 1500 |
| evaluate.peak_rss_mb | **1009.15625** |
| sampler peak_kb | **2228**（以 ru_maxrss 为准） |
| 相对软帽 | **PASS** |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_X2_SELFCHECK_V2_HILIQ_X2.ebc673bf.CONSUMED_PASS.20261026T1629ET.ok` 归档sha **`cc2611c8`**（内容钉 `ebc673bf`；禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf25_x2_selfcheck_v2_PASS_LIFTED_20261026T1629ET.lock` sha **`1d255700`** |
| live `.ok` | **0** |
| QUIET | **无** |

## 硬钉

- 本票内存路径收口；**不解阻**全量 X2；**≠X2 ACCEPT**；**≠Book-Smoke**
- PIN_GAP **PARTIAL**；decay=DECAY_DOWNGRADE；gates A/B/current 全 false；SELFCHECK_EXECUTED=true；x2_accept=false
- 禁 RESTORED：十二票含 `3c297052` + 本票内容 `ebc673bf`
- 禁代跑 / 禁抬帽 / 禁触 A18 `.ok` `6de02e74`；下一令听主
- selfcheck 入口数字（含 portfolio_gates / decay）**不构成**晋级
- **不报 Leo**

live=false.
