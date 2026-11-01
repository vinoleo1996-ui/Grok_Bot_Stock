# Arch 叶34 High Accrual Exclusion Overlay HILIQ×x2 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T11:08:30-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke / ≠selfcheck | **false** / **true** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `1441a7ec` | DONE rc=**0**；pid `285178` gone；ET_TS=`20261027_105941`；无 Exit 94/95；AI **未擅 lift** |
| RUNNING_ACK | `c03d2f16` | MATCH（全长 `c03d2f16bee7fb4bf4aff7fbb523ea9b9c9f4112745fd16c0a36b400a6dc886a`） |
| `.ok`（消费前） | `c1b71e64` | MATCH → 归档（全长 `c1b71e646093dbbe1cfea41c684d8ee0de8e5af8f0a8f058182c251d7dbe4ce1`） |
| QUIET（lift 前） | `bc6f8b83` | MATCH；holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2`；ok_sha8=`c1b71e64` → lift（全长 `bc6f8b83f49e16f015ec3416580d846cd279594a4042ba0e406aaabe70565389`） |
| 脚本 | `482009dc` | MATCH；**UNCHANGED**（全长 `482009dc697cbf74b369cbf3fb035f1fc447a4af9339de8abf283f3ed4e971bc`） |
| mask / overlap / run_meta | `8b5d6d24` / `77368c8f` / `4fc6108d` | MATCH（out `output/ai_factory/_leaf34_high_accrual/20261027_105941/`） |
| SIGNED / 脚本审 | `de0ee2cb` / `033b66f8` | MATCH |
| FROZEN / ArchFROZEN / PIN / FROZEN RECEIPT | `8be1099e` / `027efa26` / `bb418e6a` / `438ee33d` | MATCH（只读钉） |
| COVER / CMD / DIFF / SCRIPT RECEIPT | `c491e7a4` / `cfa3ca4e` / `f583b616` / `f73c986f` | MATCH（只读钉） |
| ET_TS / pid / rc / pgrep | `20261027_105941` / `285178`（已退出；pgrep leaf34 空） / **0** | MATCH |
| overlap 硬钉 | `any_jaccard_hard_reject=false`；`any_required_pin_gap=false` | MATCH |

## peak_proof

| 源 | 值 |
|---|---|
| peak_kb（run_meta / peak_kb_final） | **701040** |
| OK 行 peak_kb | **728360** |
| RSS_CHECK 全局 max peak_kb | **701820** @ `after_mask_cs_rebal_20260227` |
| rss_limit_mb | **1500**（**未抬**） |
| 相对硬帽 | max(OK728360, RSS701820) / 1536000 ≈ **47.4%**；≪1500MB |
| `after_mask` | **PRESENT**（peak_kb=527820） |
| `after_ocf_rebal_*` | **PRESENT** ×**30**（max peak_kb=701348） |
| `after_mask_cs_rebal_*` | **PRESENT** ×**30**（max peak_kb=701820） |
| `after_daily_concat` | **PRESENT**（peak_kb=701040） |
| Exit 94/95 | **无** |
| STOP/ABORT | **无** |

## overlap 摘要

| 项 | 值 |
|---|---|
| schema | `leaf34_overlap_vs_leaf19_25_27_30_31_32_33`；n_rows=6 |
| vs leaf19 ρ | min/max/mean ≈ **0.253 / 0.441 / 0.367**；j20_max ≈ **0.026** |
| vs leaf25 ρ | min/max/mean ≈ **0.251 / 0.512 / 0.369**；j20_max ≈ **0.053**；**strength_filter=true**（ρ_max≈**0.51168** strength-only；**非硬拒**） |
| vs leaf27 ρ | min/max/mean ≈ **−0.006 / 0.063 / 0.030** |
| vs leaf30 ρ | min/max/mean ≈ **0.221 / 0.356 / 0.296** |
| vs leaf31 ρ | min/max/mean ≈ **−0.121 / 0.013 / −0.053** |
| vs leaf32 ρ | min/max/mean ≈ **−0.040 / 0.018 / −0.016** |
| vs leaf33 ρ | min/max/mean ≈ **−0.195 / 0.091 / −0.043** |
| 叶25 尾窗披露 | 钉日 `2026-04-27` / `2026-10-09` → `n_common_leaf25=0`、`rho_leaf25=null`（已披露） |
| Jaccard≥0.7 hard reject | **无**（`any_jaccard_hard_reject=false`） |
| PIN_GAP | **0**（`any_required_pin_gap=false`） |
| `--no-overlap-report` | **未使用**；文件已写出并消费 |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_HILIQ.c1b71e64.CONSUMED_PASS.20261027T1108ET.ok` 内容sha8 **`c1b71e64`**（整文件 mv；禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf34_high_accrual_exclusion_overlay_x2_PASS_LIFTED_20261027T1108ET.lock` 原sha8 **`bc6f8b83`** → lift后内容sha8 **`bc6f8b83`**（未改内容，sha 不变） |
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF34*` ABSENT） |
| QUIET | **ABSENT** |

## 硬钉

- 本票叶34 High Accrual Exclusion Overlay X2 PRIMARY（HI_LIQ **mask-only** top_q=**0.20**）alpha 构建收口；**≠X2 ACCEPT**；**≠Book-Smoke**；**≠selfcheck**；本拍**不解阻 ACCEPT**；KEEP **不解阻**
- PRIMARY 纪律：HI_LIQ mask-only；禁静默 FULLA PRIMARY；soft-penalty 非 PRIMARY
- C3：日表+PIT `e_available_at≤t`+NP≤0+YTD_cumulative；PIN **`bb418e6a`** 未改
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改脚本/mask/产物；不触 A18；不审/不夹带 `0087c928`/28/29
- 禁 RESTORED：本票内容 **`c1b71e64`** + `245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)
- 叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤
- Data 旁注（非本票；不代办）：中转双通 **DUAL_STABLE_FAIL** R1 `f2623f42`+R2 `119c6309`；SUSPEND 维持；未消费 `9e4359f9`
- 下一跳交主决策（是否 selfcheck / 组合接线 / HOLD）——**Arch 不自决 ACCEPT**
- **不报 Leo**（leo_notify=false）

live=false。
