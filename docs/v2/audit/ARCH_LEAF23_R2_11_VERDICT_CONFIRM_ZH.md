# Arch 书面确认：叶23 sue_desens_cs r2.11 X2 判定

- 确认时间：2026-10-18T09:31:34-04:00（ET）
- 方式：只读。用 cat / rg / jq 读 summary JSON 文本、sha256sum 核 sha；没有读 parquet，没有起任何读真实数据的进程。
- live=false，promotion=false。

## 1. 依据
- 脚本：research/g1g5_sue_desens_cs_alpha.py，sha 4aa19627（与 .ok cf0fa9a1、各 meta 的 script_sha256 一致）。判定逻辑在 L999-1007：
  - floor = 两档 cagr244 都 > HI_LIQ wb_cagr244；
  - tpass = 两档 vs_wb 的 t_hac 都 ≥ T_DECISIVE（L130：2.50）；
  - verdict_cap = floor 不过 → FAIL；floor 过、t 不过 → WATCH；都过 → PENDING_EXTERNAL_GATES；
  - report_to_leo_allowed = floor 且 beats_poolEW。
- 预注册：docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md，sha 8f5d8ac4（= .ok cf0fa9a1 的 prereg_sha256）。
- 回执：docs/v2/audit/leaf23_r2_11_run/AI_LEAF23_R2_11_X2_RERUN2_RECEIPT_ZH.md（主口径 A01-A03，sha d9c49bf4）；AI_LEAF23_R2_11_X2_SENS_RECEIPT.md（敏感性 A04-A27，sha e6b61806，24 步全部 PASS）。

## 2. 判定读数（摘自脚本写出的 merge summary，res.HILIQ.decisive）
| 规格 | 来源文件 | sha8 | 60万 top6 CAGR | 100万 top10 CAGR | HI_LIQ wb CAGR | t_hac 6 / 10（vs wb） | floor | t≥2.50 | beats_capadv | beats_poolEW | report_to_leo | verdict_cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 主口径 primary（唯一判定规格） | output/ai_factory/leaf23_sue_desens_cs/summary_20261018_072247.json | a917d624 | 3.18% | 4.39% | 11.55% | -1.40 / -0.82 | false | false | true | false | false | **FAIL** |
| 敏感性 sig-sue | output/ai_factory/leaf23_sue_desens_cs_sig-sue/summary_20261018_073330.json | e88691fb | 7.01% | 7.89% | 11.55% | -0.67 / -0.25 | false | false | true | false | false | FAIL（仅披露） |
| 敏感性 denom-daily | output/ai_factory/leaf23_sue_desens_cs_denom-daily/summary_20261018_073700.json | 59b533b2 | 3.70% | 11.83% | 11.55% | -1.35 / 0.27 | false | false | true | false | false | FAIL（仅披露） |
| 敏感性 nofc（S_F） | output/ai_factory/leaf23_sue_desens_cs_nofc/summary_20261018_074027.json | e470326a | 7.59% | 7.02% | 11.55% | -0.53 / -0.40 | false | false | true | false | false | FAIL（仅披露） |
| 敏感性 bo40 | output/ai_factory/leaf23_sue_desens_cs_bo40/summary_20261018_074854.json | 247f87c3 | 6.69% | 5.91% | 11.55% | -0.69 / -0.53 | false | false | true | false | false | FAIL（仅披露） |

- 主口径 is_decisive_spec=true；四个敏感性 is_decisive_spec=false，脚本注明「未做多重检验校正，仅披露」。
- 两个股票池（HILIQ、FULLA）的分位单调性 monotone 在 5 个规格里都是 false（只披露）。
- FULLA 只披露，不出 decisive 段。
- 披露：capadv 重算 CAGR 两档相同（1.26%），这与 Strategy 09:01 说明的「两档共用同一份目标权重」一致。它不影响判定：FAIL 来自 wb 地板。

## 3. 结论
**叶23 判 FAIL，不进 CMC。**

- 主口径两档净 CAGR（3.18%、4.39%）都低于 HI_LIQ wb（11.55%），没过硬地板。预注册 §7 原文：「HI_LIQ wb 硬地板：60万、100万两档净 CAGR 都要 > HI_LIQ wb，否则判 FAIL（不只是 WATCH）……未过地板的叶不报 Leo。」
- 预注册 §9 原文：「同时须过 §7 wb 硬地板（未过即 FAIL）及其余硬闸。」§9 还写明：结论以主口径为准，敏感性方向不一致也不改判定。
- 不进 CMC 的理由：预注册 §7/§8 把 Gate B / CMC 列为硬闸之一，只能维持或下调结论。主口径已经因地板判 FAIL，CMC 改变不了结论，跑它只会多花一次真实数据运行和家族试验次数。预注册里没有「FAIL 不进 CMC」这句原文，这一条是 Arch 依据 §7、§9 作出的裁定。
- 家族台账：本叶是 who_pays 家族第 4 次试验，结果 FAIL，记入 docs/v2/AI_LEAF_LEDGER_ZH.md 第 23 行（由 AI 更新，Arch 复核）。

## 4. .ok 归档核对（sha256sum 前 8 位须等于文件名中的标签）
| 归档 | sha256 | 结果 |
|---|---|---|
| output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF23_R2_11_X2_cf0fa9a1_CONSUMED_20261018_0750ET.ok | cf0fa9a135dd34b4372dfebcd918e20787a3afe54b714aaae4b88bba80e68ca1 | 一致 |
| output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF24_R10_X2_41a839c0_CONSUMED_20261018_0851ET.ok | 41a839c07677d88bf6cfa085397a7980c80f91ad646646d1ceea4b8a27fb604d | 一致 |

## 5. 留待处理
- 7 名退市股的全量只读核查：.ok 草稿已备好，尚未签发。
- 两个残留 .pyc 待删除，需要记录 sha。
