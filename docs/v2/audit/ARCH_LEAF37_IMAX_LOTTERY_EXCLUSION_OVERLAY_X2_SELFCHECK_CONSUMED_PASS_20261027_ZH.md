# Arch 叶37 IMAX Lottery Exclusion Overlay X2 selfcheck_v1 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T19:38:42-04:00`（America/New_York） |
| 主令 | 主 ~19:35 ET · 叶37 X2 selfcheck DONE→CONSUME（主 MATCH：report `d27a53f5` / RUN_RECEIPT `d1976899` / eval_weights `f05f1300` / 脚本 `015e6f06` / `.ok` `57ab9096` 仍在位；QUIET ABSENT；pid gone；rss_peak≈960≪1500；rc=0） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |
| leo_notify | **false** |

## 0. 一句话

叶37 X2 **selfcheck_v1**（脚本 `015e6f06` only；B1 `32605aca` / 基盘 `108aba8f` ban_as_live 本窗不跑）DONE（rc=0；ρ_excess≈**0.9589**≫0.5；Gate A/B/current **全 false**；decay **KEEP**；60万 overlay≈0.1269 vs cap≈0.1282；100万≈0.1508 vs 0.1519；peak≈**960.07**≪1500）已 **CONSUME**：live `.ok` **`57ab9096`** 归档至 `_consumed/`（内容字节不变）。**QUIET ABSENT**（本票从未挂；**无需 lift**；未创建/改 QUIET）。脚本 **`015e6f06` UNCHANGED**；禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+…；**未**代改脚本；**未**代跑；**未**新签；**未**改产物。**仍 ≠X2 ACCEPT**；KEEP≠ACCEPT（`45dd87dc`）；下一跳交主令 Alpha 新口径审闸（预期 HOLD）——**Arch 不自派 Alpha、不自决 ACCEPT**。

## 1. 核盘 MATCH

| 件 | sha8 / 值 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `d1976899` = `d1976899154e10ad7eb4258dae5af824fa4ee2db6f8ed0bbe840ba54c8a74155` | **MATCH** · DONE rc=**0**；ET_TS=`20261027_193125`；pid `851818` gone |
| `.ok`（消费前 live） | `57ab9096` = `57ab909622f1edaf2c19dd3f40824a20b6ef407b8b3436c9dafe1fabc820fa64` | **MATCH** → 归档（内容字节不变） |
| QUIET | **ABSENT** | 本窗 `ban_hang_quiet_this_sign`；**从未挂**；**无需 lift**；无 lift 文件 |
| 脚本 selfcheck | `015e6f06` = `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` | **MATCH · UNCHANGED · only** |
| B1 / 基盘 | `32605aca` / `108aba8f` | UNCHANGED；**ban_as_live**；本窗不跑 |
| mask | `2503a41e` = `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` | **MATCH · UNCHANGED** |
| meta | `e9e9aa1d` = `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` | **MATCH · UNCHANGED** |
| overlap | `8177578f` = `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | **MATCH · UNCHANGED** |
| report `selfcheck_v1.json` | `d27a53f5` = `d27a53f53ebaded3c242e5f2e54222665858b821b28d87fe7312e2302e457919` | **MATCH**（stamp `20261028_073125`；=side_meta） |
| eval_weights | `f05f1300` = `f05f130015ca1598953e8c05407b58fcadfc3d115ac68479dbaab0666320363b` | **MATCH**；`…/_selfcheck/eval_weights_HILIQ_x2_20261028_073125.parquet` |
| SIGNED / 审 | `b1fc8325` / `3d40f713` PASS_WC | **MATCH** |
| COVER / CMD / DIFF / RECEIPT(脚本) | `8c83ba13` / `6f5d48bd` / `2542e7cd` / `bb616bdb` | 只读钉 |
| 上游 B1 CONSUMED | `c0a6b5ae` | 只读钉（本票未触） |
| ET_TS / pid / rc / pgrep | `20261027_193125` / `851818`（gone） / **0** / 空 | **MATCH** |
| SELFCHECK_EXECUTED / PIN_GAP | **true** / **MASK_ONLY_OVERLAY_NO_FULL_ALPHA** | **MATCH** |
| x2_accept / promotion / book_smoke / live | false / false / false / false | **MATCH** |

## 2. gates / decay / ρ（披露；不解阻；与盘一致）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false** |
| 60w | A=false · B=false · current=false（overlay cagr≈**0.126870** ＜ cap≈**0.128224**；Calmar≈0.898 ＜ cap≈0.900） |
| 100w | A=false · B=true（单档） · current=false；verdict B 仍 **false**（overlay cagr≈**0.150845** ＜ cap≈**0.151872**） |
| decay.outcome | **KEEP**（reasons=[]；latest_resid_alpha≈**0.023212**；consecutive_declines=**0**；decay net_cagr≈0.007825 ＞ bench≈−0.033709） |
| cost.untradable | **true**（reasons=`成本拖累>毛超额一半`；披露不改 KEEP≠ACCEPT） |
| ρ_excess vs capacity_adv | ≈**0.958902**（≫0.5；未走「ρ&lt;0.5 且双叠加优于主干」支路） |
| pin_gap.overall | **MASK_ONLY_OVERLAY_NO_FULL_ALPHA** |
| KEEP 不解阻 | **true**（叶32 HOLD `45dd87dc`；`keep_does_not_unblock_x2_accept=true`；叶36 HOLD 不复开） |
| x2_accept / promotion_approved / book_smoke / live | **false** / **false** / **false** / **false** |

## 3. peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| side_meta / report `rss_mb_peak_self` / `peak_proof.ru_maxrss_mb` | **960.07** MB |
| evaluate.peak_rss_mb | **960.0703125** MB |
| sampler VmRSS / VmHWM peak | **969756** / **983112** KB（`/tmp/quantlab_leaf37_x2_selfcheck_20261027_193125.tsv`） |
| rss_mb soft=hard | **1500**（**未抬**） |
| 相对软帽 | ≪1500；**PASS**（max≈960.07 ＜ 1500；未触发 ABORT_RSS） |
| sampler_prefix | `/tmp/quantlab_leaf37_x2_selfcheck_` |

## 4. 归档（QUIET 跳过 lift）

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1.57ab9096.CONSUMED_PASS.20261027T1935ET.ok` |
| `.ok` 内容 sha8 / 全长 | **`57ab9096`** / `57ab909622f1edaf2c19dd3f40824a20b6ef407b8b3436c9dafe1fabc820fa64`（内容字节不变；**禁 RESTORED**） |
| QUIET lift | **无**（本票 QUIET **ABSENT**；禁挂；**无需 lift**；未创建任何 lift 文件） |
| live `.ok` | **ABSENT**（`ARCH_RUN_AUTH_LEAF37_IMAX_LOTTERY_EXCLUSION_OVERLAY_X2_SELFCHECK_V1.ok` 空） |
| live QUIET | **ABSENT**（`output/loop/RESEARCH_QUIET.lock` 不存在；保持） |
| pgrep leaf37 selfcheck | **空** |

## 5. 硬钉

- 本票叶37 IMAX Lottery Exclusion Overlay X2 **selfcheck_v1** 收口；PRIMARY=HI_LIQ **mask-only** top_q=**0.20**×capacity_adv（≠α TopN）；Gate A/B/current **全 false**；decay=**KEEP** 须披露；ρ_excess≈**0.958902**≫0.5；60万/100万 overlay 均未优于主干 cap；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**；KEEP **不解阻**（`45dd87dc`）
- 禁复跑本票；禁抬帽（rss=1500）；**禁代跑**；禁代改脚本/权重/报告；不触 A18；不审/不夹带 `0087c928`/28/29
- 禁 RESTORED：本票内容 **`57ab9096`** + `b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+旧票（forbid_n=32）；禁 RESTORED VOID/CONSUMED
- 钉 mask `2503a41e` / meta `e9e9aa1d` / overlap `8177578f` / 脚本 `015e6f06` **未改**；B1 `32605aca` / 基盘 `108aba8f` **ban_as_live**；叶32 HOLD **`45dd87dc`** 不回撤；叶36 HOLD 不复开
- selfcheck 入口数字（含 portfolio_gates / decay KEEP / ρ_excess）**不构成**业务晋级；**Arch 不自决 X2 ACCEPT**；**不自派 Alpha**
- **下一跳交主决策**（主令 Alpha 新口径审闸；预期 HOLD）；Arch 待机听令
- **不报 Leo**（leo_notify=false）

## 6. 下一跳（听主）

```
CONSUMED_PASS（本回执）
  → 请主裁：令 Alpha 新口径审闸（预期 HOLD）
      → Arch 不自派 Alpha；≠X2 ACCEPT；KEEP≠ACCEPT（45dd87dc）；禁 Book-Smoke；禁 RESTORED 57ab9096+b5be1164+4096d401+…
```

live=false。
