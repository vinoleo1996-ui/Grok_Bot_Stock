# Arch 叶30 CRR X2 selfcheck_v1 · CONSUMED_PASS

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-27T01:53:25-04:00`（America/New_York） |
| 结论 | **CONSUMED_PASS** |
| live / ≠X2 ACCEPT / ≠Book-Smoke | **false** / **true** / **true** |

## 核盘 MATCH

| 件 | sha8 | 结果 |
|---|---|---|
| AI RUN_RECEIPT | `62bc5bd7` | DONE rc=**0**；ET_TS=`20261027_014833`；pid `3705608` gone |
| `.ok`（消费前） | `aa25e989` | MATCH → 归档 |
| QUIET（lift 前） | `0eb56fe2` | MATCH；holder=`leaf30_CRR_X2_SELFCHECK_V1`；ok_sha8=`aa25e989` → lift |
| 脚本 | `797724d4` | MATCH；未改 |
| alpha（钉 R3） | `c8c7a5a5` | UNCHANGED |
| report `selfcheck_v1.json` | `3eeffb02` | MATCH |
| eval_weights | `900970d4` | MATCH |
| SIGNED / 审 / CMD | `21078eb5` / `3826aa63` / `c25f1321` | MATCH |
| 构建脚本 | `3ee9fed2` | UNCHANGED（本票未触） |

## gates / decay（披露；不解阻）

| 项 | 值 |
|---|---|
| portfolio_gates.verdict | A=**true** · B=**false** · current=**false** |
| 60w | A=true · B=false · current=false |
| 100w | A=true · B=true · current=false |
| decay.outcome | **DECAY_DOWNGRADE**（reasons=`latest_alpha<0`,`H2_net_cagr<=510300`） |
| pin_gap | Alpha 闸 `1c992d62` 语境 ABSENT_UNTIL_SELFCHECK；本票 evaluate 已跑；**≠X2 ACCEPT** |
| x2_accept / promotion_approved | **false** / **false** |

## peak_proof

| 源 | 值 |
|---|---|
| `rss_mb_peak_self`（ru_maxrss） | **1027.0** MB |
| rss_limit_mb | **1500**（**未抬**） |
| 相对软帽 | ≪1500；**PASS** |

## 归档

| 项 | 值 |
|---|---|
| `.ok` 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK_V1_HILIQ_X2.aa25e989.CONSUMED_PASS.20261027T0153ET.ok` 内容sha8 **`aa25e989`**（禁 RESTORED） |
| QUIET lift | `output/loop/_lifted/RESEARCH_QUIET_leaf30_x2_selfcheck_v1_PASS_LIFTED_20261027T0153ET.lock` 原sha8 **`0eb56fe2`** → lift后sha8 **`c999e733`** |
| live `.ok` | **0** |
| QUIET | **ABSENT** |
| pgrep selfcheck/3705608 | **空** |

## 硬钉

- 本票叶30 X2 selfcheck_v1 收口；**A=true 不解阻**；B/current=false；**DECAY_DOWNGRADE 须披露**；**≠X2 ACCEPT**；**≠Book-Smoke**
- 禁复跑本票；禁抬帽（rss=1500）；禁代跑；下一令听主
- 禁 RESTORED：`aa25e989` + `7e239487` + `5af20222` + `5ae077fa`（及十六票其余）
- 钉 alpha `c8c7a5a5` / 脚本 `797724d4` **未改**；禁触 A18 `a62881b9`
- selfcheck 入口数字（含 portfolio_gates / decay）**不构成**晋级
- **不报 Leo**

live=false。
