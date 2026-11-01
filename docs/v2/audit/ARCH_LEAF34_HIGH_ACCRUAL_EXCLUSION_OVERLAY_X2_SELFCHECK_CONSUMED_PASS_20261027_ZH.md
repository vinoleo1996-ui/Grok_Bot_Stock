# Arch 叶34 High Accrual Exclusion Overlay X2 selfcheck_v1 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T11:59:47-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `cc0947c2` | DONE rc=**0**；ET_TS=`20261027_115317`；pid `341702` gone（pgrep leaf34 空） |
| RUNNING_ACK | `571ed4a4` | MATCH（全长 `571ed4a415ff7e929e94344cd11cd581c0e4fc9b72146cf708a40fdeb2d3450d`） |
| `.ok`（消费前） | `178e90e9` | MATCH → 归档（全长 `178e90e905466abfea88186967fdcba5dbb4600e67d969452b68f3afd6c3671d`） |
| QUIET（lift 前） | `3fce510e` | MATCH；holder=`leaf34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1`；ok_sha8=`178e90e9` → lift（全长 `3fce510eea7c4594904e85402c0c5f17df5310f0b6ad4d26dd4c3c5c2d52c2de`） |
| 脚本 | `d210efba` | MATCH；**UNCHANGED**（全长 `d210efba27ff3b45d3da88faa3f0767adc4d6b5481420f48a31bf6e77e38f7f6`） |
| mask / meta / overlap | `8b5d6d24` / `4fc6108d` / `77368c8f` | MATCH（out `output/ai_factory/_leaf34_high_accrual/20261027_105941/`） |
| report `selfcheck_v1.json` | `b4b9208d` | MATCH（stamp `20261027_115317`；=side_meta） |
| eval_weights | `680d516e` | MATCH；`…/_selfcheck/eval_weights_HILIQ_x2_20261027_115317.parquet`（全长 `680d516e4b778271f7ec498d04774c41f1c45bd18e14d45ea971e919730ed6ce`） |
| side_meta | `b4b9208d` | MATCH；`…/_selfcheck/selfcheck_run_meta_HILIQ_x2_20261027_115317.json`（=report IDENTICAL） |
| SIGNED / 审 | `56580a5c` / `e2902e64` | MATCH |
| 构建脚本 | `482009dc` | UNCHANGED（本票未触；alpha_build） |
| 模板叶32 / 叶33 / 叶31 / common | `dcf6b559` / `afbbe7e7` / `e1fe578c` / `218b61cf` | 只读钉（本票未触） |
| 上游 CONSUMED / FROZEN / PIN | `fea9b3ff` / `8be1099e` / `bb418e6a` | 钉齐（本票未触） |
| COVER / CMD / DIFF / RECEIPT | `0bf02521` / `4255ad33` / `a1a6689d` / `a5467d7d` | 只读钉 |
| ET_TS / pid / rc | `20261027_115317` / `341702`（pgrep 空） / **0** | MATCH |

## gates / decay / ρ（披露；不解阻；与盘一致）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false** |
| 60w | A=false · B=false · current=false（overlay Calmar≈0.886 ＜ cap≈0.900） |
| 100w | A=false · B=false · current=false（overlay Calmar≈1.217 ≈ cap≈1.218；未优于主干） |
| decay.outcome | **KEEP**（reasons=[]；latest_resid_alpha≈**0.03208**；consecutive_declines=**0**；H2_net_cagr≈0.0155 ＞ bench≈−0.0337） |
| cost.untradable | **true**（reasons=`成本拖累>毛超额一半`） |
| ρ_excess vs capacity_adv | ≈**0.960841**（≫0.5；未走「ρ&lt;0.5 且双叠加优于主干」支路） |
| pin_gap.overall | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA** |
| KEEP 不解阻 | **true**（叶32 HOLD `45dd87dc`；`keep_does_not_unblock_x2_accept=true`） |
| x2_accept / promotion_approved / book_smoke / live | **false** / **false** / **false** / **false** |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| side_meta / report `rss_mb_peak_self` / `peak_proof.ru_maxrss_mb` | **956.92** MB |
| evaluate.peak_rss_mb | **956.91796875** MB |
| rss_mb soft=hard | **1500**（**未抬**） |
| 相对软帽 | ≪1500；**PASS**（max≈956.92 ＜ 1500；未触发 ABORT_RSS） |
| sampler_prefix | `/tmp/quantlab_leaf34_x2_selfcheck_*` only |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_X2_SELFCHECK_V1_HILIQ_X2.178e90e9.CONSUMED_PASS.20261027T1159ET.ok` 内容sha8 **`178e90e9`**（整文件 mv；禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf34_high_accrual_exclusion_overlay_x2_selfcheck_v1_PASS_LIFTED_20261027T1159ET.lock` 原sha8 **`3fce510e`** → lift后内容sha8 **`3fce510e`**（未改内容，sha 不变） |
| live `.ok` | **0**（本票 live path ABSENT；`ARCH_RUN_AUTH_*.ok` 顶层=0） |
| QUIET | **ABSENT** |
| pgrep leaf34 | **空** |

## 硬钉

- 本票叶34 High Accrual Exclusion Overlay X2 **selfcheck_v1** 收口；PRIMARY=HI_LIQ **mask-only** top_q=**0.20**×capacity_adv（≠α TopN）；Gate A/B/current **全 false**；decay=**KEEP** 须披露；ρ_excess≈**0.960841**≫0.5；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**；KEEP **不解阻**（`45dd87dc`）
- 禁复跑本票；禁抬帽（rss=1500）；**禁代跑**；禁代改脚本/权重/报告；不触 A18；不审/不夹带 `0087c928`/28/29
- 禁 RESTORED：本票内容 **`178e90e9`** + `c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+二十票(+`81521fb5`)
- 钉 mask `8b5d6d24` / meta `4fc6108d` / overlap `77368c8f` / 脚本 `d210efba` / 构建 `482009dc` **未改**；叶33 正式 **`afbbe7e7` UNCHANGED**；叶32 HOLD **`45dd87dc`** 不回撤
- selfcheck 入口数字（含 portfolio_gates / decay KEEP / ρ_excess）**不构成**业务晋级；**Arch 不自决 X2 ACCEPT**
- Data 旁注（非本票；不代办）：中转双通 DUAL_STABLE_FAIL R1 `f2623f42`+R2 `119c6309` SUSPEND 维持
- **下一跳交主决策**（HOLD/其它）；Arch 待机听令
- **不报 Leo**（leo_notify=false）

live=false。
