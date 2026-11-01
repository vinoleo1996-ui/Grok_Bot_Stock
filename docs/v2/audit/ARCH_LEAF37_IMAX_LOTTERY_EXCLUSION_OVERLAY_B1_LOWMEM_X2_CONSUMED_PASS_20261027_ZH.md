# Arch 叶37 IMAX Lottery Exclusion Overlay HILIQ×x2 · B1_LOWMEM · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T18:47:48-04:00`（America/New_York） |
| 主令 | 主 ~18:41 ET · 叶37 B1_LOWMEM X2 CONSUME GO（主盘证 MATCH：rc=0 / ET_TS=`20261027_183719` / OUT=`output/ai_factory/_leaf37_imax_lottery/20261027_183719/`；mask `2503a41e` / overlap `8177578f` / run_meta `e9e9aa1d` / run.log `9773df94`；ACK `08652c66` / RECEIPT `c6d8b1ce`；.ok `b5be1164` 仍在位；QUIET `a616211d` 未 lift） |
| 结论 | **CONSUMED_PASS**（rc=**0**；exclusion_mask **PRESENT**；overlap `any_jaccard_hard_reject=False`；coverage_median=**2816.5**≥300 PASS；peak_kb=**1107536**＜split=1131520 / soft=1536000；rss=1500 未抬；无 Exit94/95） |
| live / ≠X2 ACCEPT / ≠Book-Smoke / ≠selfcheck / ≠叶36 | **false** / **true** / **true** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

叶37 B1_LOWMEM（脚本 `32605aca` only；基盘 `108aba8f` UNCHANGED 禁跑）X2 PRIMARY DONE（rc=0；mask `2503a41e`；overlap hard_reject=**False**；pin_gap=**False**；coverage_median=**2816.5** PASS；peak=**1107536**＜split/soft；过 soft-split）已 **CONSUME**：live `.ok` **`b5be1164`** 归档至 `_consumed/`（内容字节不变）；QUIET **`a616211d`**（holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2`）已 lift。脚本 **`32605aca` UNCHANGED**；基盘 **`108aba8f` UNCHANGED**；禁 RESTORED `b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+旧票；**未**代改脚本；**未**代跑；**未**新签；**未**改产物/mask。**仍 ≠X2 ACCEPT**；Alpha/selfcheck **另票听主**（Arch 不自派）；禁 Book-Smoke；≠叶36。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `c6d8b1ce` = `c6d8b1cedd1205c4b2c408c6445adae5b3fcbc7a7f8eaf3e971571f3f9ea32ef` | **MATCH** · DONE rc=**0** |
| RUNNING_ACK | `08652c66` = `08652c663911a508da9f9b6dcad76495c25901ae650cfbd80aec62c2ec343fd9` | **MATCH** |
| `.ok`（消费前 live） | `b5be1164` = `b5be11642107551e241578c41907105763a4a92009fa3a91a0bc810dad453ff0` | **MATCH** → 归档（内容字节不变） |
| QUIET（lift 前 live） | `a616211d` = `a616211dd0cdfc06a60f8b40c095c2f543b4f53f886fef6761a8034d6b2d054e`；holder=`leaf37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2` | **MATCH** → lift |
| SIGNED | `7b3bd298` = `7b3bd2981dbb86bd5f815ced87287b1b0431ab4b809bc466d7c6ce3f4222724a` | **MATCH** |
| 脚本审 | `b403a7e5` PASS_WC | **MATCH** |
| 脚本 B1_LOWMEM | `32605aca` = `32605acac230b777cc02e72f8385f31aa64bafd5fdf2784f9f05c8b567090d0c` | **MATCH · UNCHANGED · only** |
| 基盘（禁跑） | `108aba8f` = `108aba8f5c3f58f2792d31b36a793ff5251fa732174667e037ffae113eb91f2b` | **MATCH · UNCHANGED** |
| mask | `2503a41e` = `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` | **MATCH** · PRESENT |
| overlap | `8177578f` = `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | **MATCH** · hard_reject=**False** |
| run_meta | `e9e9aa1d` = `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` | **MATCH** |
| run.log | `9773df94` = `9773df94e75b5b99c29ff9fd6adfbe7ec274c4911b65801f144239d8c83e86d2` | **MATCH** |
| ET_TS / OUT / rc / pgrep | `20261027_183719` / `_leaf37_imax_lottery/20261027_183719/` / **0** / 空 | **MATCH** |
| Exit94/95 / Traceback / ABORT_PEAK | **无** | **MATCH** |
| x2_accept / leaf36 / live / leo_notify | false / false / false / false | **MATCH** |

## 2. peak_proof / 覆盖 / overlap

| 项 | 值 |
|---|---|
| peak_kb（OK 行 / run_meta） | **1107536**（≈1081.6 MiB） |
| run_meta `peak_kb` / `peak_kb_final` | **1107536** / **1107536** |
| RSS_CHECK max | **1107536** @ `after_mask_cs_rebal_20240603` 起至 after_daily_concat |
| soft / split / c4 / hard | **1536000** / **1131520** / **1331200** / **1536000** |
| vs split / soft | peak **＜** split（过 soft-split）；≪ hard；rss_limit_mb=**1500**（**未抬**） |
| Exit 94/95 / ABORT_PEAK | **无** |
| coverage_median / gate | **2816.5** / 300 · **PASS**（`coverage_gate_pass=True`） |
| coverage_excl_median / excl_gate | **564.0** / 30 |
| zero_frac / max | **0.0** / 0.05 |
| n_pin_gaps / required pin_gap | **0** / **False** |
| `overlap_any_jaccard_hard_reject` | **False** |
| j_excl max（硬同伴 leaf18/18v/27） | 18/18v≈**0.310**；27≈**0.442** ≪0.7；disclose leaf24≈0.223 / 34≈0.117 / 35≈0.061；leaf36 HOLD_CLOSED missing（非 hard PIN_GAP） |
| PRIMARY | HILIQ · mask-only · top_q=0.20 · C3=B IMAX_proxy · B1_LOWMEM · soft-penalty 非 PRIMARY |

## 3. 归档 / lift

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.b5be1164.CONSUMED_PASS.20261027T1843ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`b5be1164`** / `b5be11642107551e241578c41907105763a4a92009fa3a91a0bc810dad453ff0`（内容字节不变；**禁 RESTORED**） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf37_imax_lottery_exclusion_overlay_b1_lowmem_x2_CONSUMED_PASS_LIFTED_20261027T1843ET.lock` |
| QUIET 原内容 sha8 / 全长 | **`a616211d`** / `a616211dd0cdfc06a60f8b40c095c2f543b4f53f886fef6761a8034d6b2d054e`（可追溯） |
| lift 文件 sha8 / 全长 | **`cc03c7eb`** / `cc03c7eba17d10bc009b3b38dd1ec564c360dcb0694a5e08a769a57653a08955` · 尾加 `# ARCH_QUIET_LIFTED`；lifted_by=arch / CONSUMED_PASS / consumed_ok_sha8=`b5be1164` / do_not_restore=true |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_B1_LOWMEM_X2_HILIQ.ok` 空） |
| live QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在） |

## 4. 硬钉

- 本票叶37 IMAX Lottery Exclusion Overlay X2 PRIMARY（HI_LIQ **mask-only** top_q=**0.20**；**B1_LOWMEM**；C3=B IMAX_proxy APPROX）alpha 构建收口；**仍 ≠X2 ACCEPT**；**≠Book-Smoke**；**≠selfcheck**；**≠叶36**；本拍**不解阻 ACCEPT**；KEEP **不解阻**
- PRIMARY 纪律：HI_LIQ mask-only；禁静默 FULLA PRIMARY；soft-penalty 非 PRIMARY；C3=B；脚本 **`32605aca` only**；基盘 **`108aba8f` 禁当 live**；PIN / FROZEN 未改
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；禁代改脚本/mask/产物；不触 A18
- 禁 RESTORED：本票内容 **`b5be1164`** + `4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+旧票；禁把 `108aba8f` 当活脚本；禁 RESTORED VOID 票 `4096d401`
- 叶33 正式 `afbbe7e7` / 叶35 `434ff42c` / 叶34 skeleton `482009dc` UNCHANGED；叶36 HOLD CLOSED 不回撤；前 VOID ABORT_PEAK（`4096d401`）不复活
- **下一跳交主决策**（是否 Alpha 组合接线 / selfcheck 另票 / HOLD）——**Arch 不自决 ACCEPT、不自派 selfcheck、不自派下一叶**
- **不报 Leo**（leo_notify=false）

## 5. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：Alpha/组合接线 或 selfcheck 另票 或 HOLD
      → Arch 不自派；≠X2 ACCEPT；≠叶36；禁 Book-Smoke；禁 RESTORED b5be1164+4096d401+eb70eef4+00eec671+10927bd9+25ae4572+旧票
```

live=false。
