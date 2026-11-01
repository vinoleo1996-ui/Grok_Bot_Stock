# Arch 叶30 CRR R3 PEAKCUT HILIQ×x2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T01:16:06-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠selfcheck / ≠Book-Smoke | **false** / **true** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `88a08738` | DONE rc=**0**；pid `3630722` gone；ET_TS=`20261027_003132` |
| `.ok`（消费前） | `7e239487` | MATCH → 归档 |
| QUIET（lift 前） | `69ea8560` | MATCH；holder=`leaf30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R3_PEAKCUT`；ok_sha8=`7e239487` → lift |
| 脚本 | `3ee9fed2` | MATCH；未改 |
| alpha / overlap / run_meta | `c8c7a5a5` / `f9991d9d` / `a6acfe27` | MATCH（out `output/ai_factory/_leaf30_crr/20261027_003132/`） |
| SIGNED / 审 / AI落盘 / RUNNING_ACK | `927b1fed` / `d081054e` / `4d951ea3` / `692b3667` | MATCH |
| ET_TS / pid / rc | `20261027_003132` / `3630722`（已退出） / **0** | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| peak_kb（log / run_meta） | **917820** |
| rss_limit_mb | **1500**（**未抬**） |
| 相对硬帽 | 917820 / 1536000 ≈ **59.8%**；≪1500MB |
| `after_daily_concat` | **PRESENT** |
| `after_logmv_rebal_*` | **PRESENT** ×**30** |
| Exit 94/95 | **无** |
| STOP/ABORT | **无** |

## overlap 摘要

| 项 | 值 |
|---|---|
| vs leaf19 ρ | ≈ **0.34–0.45**（min/max/mean ≈ 0.341 / 0.450 / 0.399） |
| vs leaf25 ρ | ≈ **0.20–0.22**（min/max/mean ≈ 0.195 / 0.221 / 0.207；4/6 有值） |
| j20_max | ≈ **0.053**（leaf19）；leaf25 j20_max=**0.0** |
| Jaccard≥0.7 hard reject | **无** |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF30_CRR_CFOOE_VOLPEN_ALPHA_BUILD_R3_PEAKCUT_HILIQ_X2.7e239487.CONSUMED_PASS.20261027T0116ET.ok` 内容sha8 **`7e239487`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf30_r3_peakcut_PASS_LIFTED_20261027T0116ET.lock` 原sha8 **`69ea8560`** → lift后sha8 **`1420c412`** |
| live `.ok` | **0** |
| QUIET | **ABSENT** |

## 硬钉

- 本票叶30 R3 PEAKCUT X2 alpha 构建收口；**≠X2 ACCEPT**；**≠selfcheck**；**≠Book-Smoke**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；下一令听主
- 禁 RESTORED：`5af20222` / `5ae077fa` / **本票内容 `7e239487`**
- 禁触 A18：`a62881b9`；禁盲重跑 `a2cef5af` / `0a264402`-as-ticket
- **不报 Leo**

live=false。
