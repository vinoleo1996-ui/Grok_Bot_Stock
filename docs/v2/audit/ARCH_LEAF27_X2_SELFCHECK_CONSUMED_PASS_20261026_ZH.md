# Arch 叶27 X2 selfcheck_v2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-26T01:08:52-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `f30b611f` | DONE 非 ABORT |
| `.ok`（消费前） | `3c19dd7d` | MATCH → 归档 |
| QUIET（lift 前） | `69cd9d8e` | MATCH → lift |
| 脚本 | `a40d7069` | MATCH |
| 构建 UNCHANGED | `585ba746` | MATCH |
| 窗令 / GO / 审 / SIGNED | `f268d120` / `0e5a37e2` / `46526394` / `b5484e5a` | MATCH |
| alpha / meta / summary | `652b8a68` / `85c2dc78` / `80596bff` | UNCHANGED |
| eval_weights | `7fc3b828` | MATCH |
| selfcheck_v2.json | `b5182220` | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| rss_mb_peak_self | **1123.44** / 1500 |
| evaluate.peak_rss_mb | **1123.44140625** |
| sampler peak_kb | **684904**（EXIT） |
| 相对软帽 | **PASS** |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF27_X2_SELFCHECK_V2_HILIQ_X2.3c19dd7d.CONSUMED_PASS.20261026T0108ET.ok` 归档sha **`78fd2088`**（禁 RESTORED 内容 `3c19dd7d`） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf27_x2_selfcheck_v2_PASS_LIFTED_20261026T0108ET.lock` sha **`ec32185b`** |
| live `.ok` | **0** |
| QUIET | **无** |

## 硬钉

- 本票内存路径收口；**不解阻**叶25/全量 X2；**≠X2 ACCEPT**
- 禁 RESTORED：八票含 `0f50daf7` + 本票内容 `3c19dd7d`
- 禁代跑 / 禁抬帽 / 禁 Book-Smoke；下一令听主
- selfcheck 入口数字（含 portfolio_gates / decay）**不构成**晋级

live=false。
