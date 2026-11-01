# Arch 叶31 Amihud Impact Slow HILIQ×x2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T02:50:26-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `49d6641c` | DONE rc=**0**；pid `3772744` gone；ET_TS=`20261027_024204` |
| `.ok`（消费前） | `fdbaa512` | MATCH → 归档（全长 `fdbaa512fa8da9e6b5256c30f397cd5a3d2bd2c1fbd1a5a295af873ea7271d81`） |
| QUIET（lift 前） | `11cfe000` | MATCH；holder=`leaf31_AMIHUD_IMPACT_SLOW_X2`；ok_sha8=`fdbaa512` → lift |
| 脚本 | `08f37fd2` | MATCH；未改（全长 `08f37fd2deb15f6a2a4e6bc7bc16e07d16fc50c70b807e0e1ae617627f98bde0`） |
| alpha / overlap / run_meta | `d4ceb78b` / `8396f211` / `696ab1cc` | MATCH（out `output/ai_factory/_leaf31_amihud/20261027_024204/`） |
| SIGNED / 脚本审 / RUNNING_ACK | `238cc7c2` / `2271cb93` / `e02e5a81` | MATCH（SIGNED path=`ARCH_LEAF31_AMIHUD_IMPACT_SLOW_X2_OK_SIGNED_20261027_ZH.md`） |
| ET_TS / pid / rc | `20261027_024204` / `3772744`（已退出；pgrep 空） / **0** | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| peak_kb（log / run_meta） | **847092** |
| sampler peak VmHWM / VmRSS | **847628** / **847628** kB |
| rss_limit_mb | **1500**（**未抬**） |
| 相对硬帽 | 847092 / 1536000 ≈ **55.1%**；≪1500MB |
| `after_mask` | **PRESENT**（peak_kb=518880） |
| `after_bars_rebal_*` | **PRESENT** ×**30** |
| `after_logmv_rebal_*` | **PRESENT** ×**30** |
| `after_daily_concat` | **PRESENT**（peak_kb=847092） |
| Exit 94/95 | **无** |
| STOP/ABORT | **无** |

## overlap 摘要

| 项 | 值 |
|---|---|
| schema | `leaf31_overlap_vs_leaf19_25_27_30`；n_rows=6 |
| vs leaf19 ρ | min/max/mean ≈ **−0.045 / 0.007 / −0.021**；j20_max ≈ **0.026** |
| vs leaf25 ρ | min/max/mean ≈ **−0.095 / −0.011 / −0.041**；j20_max=**0.0** |
| vs leaf27 ρ | min/max/mean ≈ **−0.188 / −0.005 / −0.057**；j20_max=**0.0** |
| vs leaf30 ρ | min/max/mean ≈ **−0.014 / 0.039 / 0.008**；j20_max=**0.0** |
| Jaccard≥0.7 hard reject | **无**（`any_jaccard_hard_reject=false`） |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_HILIQ.fdbaa512.CONSUMED_PASS.20261027T0249ET.ok` 内容sha8 **`fdbaa512`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf31_amihud_impact_slow_x2_PASS_LIFTED_20261027T0249ET.lock` 原sha8 **`11cfe000`** → lift后内容sha8 **`11cfe000`**（未改内容，sha 不变） |
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF31*` ABSENT） |
| QUIET | **ABSENT** |

## 硬钉

- 本票叶31 Amihud Impact Slow X2 PRIMARY（HI_LIQ）alpha 构建收口；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改 alpha；不触 A18；不审 `0087c928`
- 禁 RESTORED：本票内容 **`fdbaa512`** + 四票 `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`
- 下一跳交主：Alpha 闸门 / 研究队列由主排
- **不报 Leo**

live=false。
