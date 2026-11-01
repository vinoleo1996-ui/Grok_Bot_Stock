# Arch 叶31 Amihud Impact Slow X2 selfcheck_v1 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T03:29:04-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `af3cc528` | DONE rc=**0**；ET_TS=`20261027_032306`；pid `3876415` gone |
| `.ok`（消费前） | `4bb141c9` | MATCH → 归档（全长 `4bb141c90ca3e934dd04645f8656f9a06455e1c6d3167688b0988c7c440b5d58`） |
| QUIET（lift 前） | `351e98fb` | MATCH；holder=`leaf31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1`；ok_sha8=`4bb141c9` → lift |
| 脚本 | `e1fe578c` | MATCH；未改（全长 `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38`） |
| alpha / meta / overlap | `d4ceb78b` / `696ab1cc` / `8396f211` | **UNCHANGED** |
| report `selfcheck_v1.json` | `d4553423` | MATCH（现盘 stamp `20261027_152340`） |
| eval_weights（双 stamp） | `346cf077` | MATCH；`…152306.parquet` 与 `…152340.parquet` **byte-identical** |
| SIGNED / 审 / ACK | `e3657034` / `0db69426` / `3b83036d` | MATCH |
| 构建脚本 / 模板 | `08f37fd2` / `797724d4` | UNCHANGED（本票未触） |
| ET_TS / pid / rc | `20261027_032306` / `3876415`（pgrep 空） / **0** | MATCH |

## gates / decay（披露；不解阻）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**false** · B=**false** · current=**false** |
| 60w | A=false · B=false · current=false |
| 100w | A=false · B=false · current=false |
| decay.outcome | **DECAY_DOWNGRADE**（reasons=`latest_alpha<0`,`alpha_declined_5q`,`H2_net_cagr<=510300`） |
| cost.untradable | **true**（reasons=`无毛超额且成本拖累>1%/年`） |
| pin_gap | Alpha 闸 `a476567d` 语境 ABSENT_UNTIL_SELFCHECK；本票 evaluate 已跑；**≠X2 ACCEPT** |
| x2_accept / promotion_approved / book_smoke | **false** / **false** / **false** |

## peak_proof（REQUIRED）

| 源 | 值 |
|---|---|
| PRIMARY log `rss_mb` / side_meta 152306 | **1015.01** MB |
| 现盘 `rss_mb_peak_self`（ru_maxrss @152340） | **987.86** MB |
| sampler peak_rss_kb / peak_hwm_kb | **860404** / **1039368** KB（HWM≈**1015.0** MB） |
| rss_limit_mb | **1500**（**未抬**） |
| 相对软帽 | ≪1500；**PASS**（max≈1015.01 ＜ 1500；未触发 ABORT_RSS） |

## 二次写盘说明（透明披露 · 非抬帽 · 非 RESTORED）

PRIMARY `ET_TS=20261027_032306` pid=`3876415` 已 `ok:true` 后，AI 写 RUNNING_ACK 时 shell 反引号误触同窗再跑一次（stamp `20261027_152340`；无第二 log/samp）。两趟 eval_weights **字节完全相同**（sha8 `346cf077`）；现盘 `selfcheck_v1.json` 为 152340。**禁再复跑**。Arch 本拍**未**再跑脚本、**未**代跑。

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK_V1_HILIQ_X2.4bb141c9.CONSUMED_PASS.20261027T0329ET.ok` 内容sha8 **`4bb141c9`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf31_amihud_impact_slow_x2_selfcheck_PASS_LIFTED_20261027T0329ET.lock` 原sha8 **`351e98fb`** → lift后内容sha8 **`351e98fb`**（未改内容，sha 不变） |
| live `.ok` | **0**（本票 live path ABSENT） |
| QUIET | **ABSENT** |
| pgrep leaf31_amihud/selfcheck_v1 | **空** |

## 硬钉

- 本票叶31 Amihud X2 selfcheck_v1 收口；gates A/B/current **全 false**；**DECAY_DOWNGRADE 须披露**；**≠X2 ACCEPT**；**≠Book-Smoke**；本拍**不解阻 ACCEPT**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；下一令听主（请主排 Alpha/研究队列）
- 禁 RESTORED：本票内容 **`4bb141c9`** + 五票 `fdbaa512` / `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`（及审文十八票）
- 钉 alpha `d4ceb78b` / meta `696ab1cc` / overlap `8396f211` / 脚本 `e1fe578c` **未改**；禁触 A18；`0087c928` **未夹带**
- selfcheck 入口数字（含 portfolio_gates / decay）**不构成**晋级
- **不报 Leo**

live=false。
