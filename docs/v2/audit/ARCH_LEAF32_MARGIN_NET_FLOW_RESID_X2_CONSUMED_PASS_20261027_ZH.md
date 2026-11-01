# Arch 叶32 Margin Net Flow Resid HILIQ×x2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T04:51:37-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `f3e8f991` | DONE rc=**0**；pid `3952200` gone；ET_TS=`20261027_042805`；无 Exit 94/95 |
| `.ok`（消费前） | `02426b73` | MATCH → 归档（全长 `02426b73d253237127772bd0023c52938ad58bdb76204feeddac87ceb385d736`） |
| QUIET（lift 前） | `6d62911f` | MATCH；holder=`leaf32_MARGIN_NET_FLOW_RESID_X2`；ok_sha8=`02426b73` → lift（全长 `6d62911f53c0ab7820be756dbbbddae3fa7c78f623d58cdf377ec64edd3505a5`） |
| 脚本 | `4e0f3c00` | MATCH；**UNCHANGED**（全长 `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187`） |
| alpha / overlap / run_meta | `13eee6fd` / `a643d71a` / `e510f346` | MATCH（out `output/ai_factory/_leaf32_margin_flow/20261027_042805/`） |
| SIGNED / 脚本审 / RUNNING_ACK | `39baa28e` / `814939b8` / `3c4d0124` | MATCH |
| ET_TS / pid / rc | `20261027_042805` / `3952200`（已退出；pgrep 空） / **0** | MATCH |
| overlap 硬钉 | `any_jaccard_hard_reject=false`；PIN_GAP=**0** | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| peak_kb（log / run_meta） | **929300** |
| sampler peak VmHWM / VmRSS | **929300** / **915276** kB |
| rss_limit_mb | **1500**（**未抬**） |
| 相对硬帽 | 929300 / 1536000 ≈ **60.5%**；≪1500MB |
| `after_mask` | **PRESENT**（peak_kb=513296） |
| `after_sw` | **PRESENT**（peak_kb=516368） |
| `after_margin_rebal_*` | **PRESENT** ×**30** |
| `after_float_rebal_*` | **PRESENT** ×**30** |
| `after_bars_rebal_*` | **PRESENT** ×**30** |
| `after_logmv_rebal_*` | **PRESENT** ×**30** |
| `after_daily_concat` | **PRESENT**（peak_kb=929300） |
| Exit 94/95 | **无** |
| STOP/ABORT | **无** |

## overlap 摘要

| 项 | 值 |
|---|---|
| schema | `leaf32_overlap_vs_leaf19_25_27_30_31_margin_delta`；n_rows=6 |
| vs leaf19 ρ | min/max/mean ≈ **−0.063 / 0.071 / −0.016**；j20_max ≈ **0.026** |
| vs leaf25 ρ | min/max/mean ≈ **0.009 / 0.122 / 0.053**；j20_max=**0** |
| vs leaf27 ρ | min/max/mean ≈ **−0.171 / 0.034 / −0.038** |
| vs leaf30 ρ | min/max/mean ≈ **−0.079 / 0.018 / −0.016** |
| vs leaf31 ρ | min/max/mean ≈ **−0.063 / 0.071 / 0.028** |
| vs margin_delta ρ | min/max/mean ≈ **−0.432 / 0.162 / −0.159** |
| Jaccard≥0.7 hard reject | **无**（`any_jaccard_hard_reject=false`） |
| PIN_GAP | **0** |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF32_MARGIN_NET_FLOW_RESID_X2_HILIQ.02426b73.CONSUMED_PASS.20261027T0451ET.ok` 内容sha8 **`02426b73`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf32_margin_net_flow_resid_x2_PASS_LIFTED_20261027T0451ET.lock` 原sha8 **`6d62911f`** → lift后内容sha8 **`6d62911f`**（未改内容，sha 不变） |
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF32*` ABSENT） |
| QUIET | **ABSENT** |

## 硬钉

- 本票叶32 Margin Net Flow Resid X2 PRIMARY（HI_LIQ）alpha 构建收口；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改 alpha；不触 A18；不审 `0087c928`
- 禁 RESTORED：本票内容 **`02426b73`** + 六票 `4bb141c9` / `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`
- 下一跳交主：Alpha 闸门 / 研究队列由主排
- **不报 Leo**

live=false。
