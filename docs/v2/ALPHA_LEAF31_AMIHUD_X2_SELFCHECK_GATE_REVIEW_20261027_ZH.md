# 叶31 Amihud Impact Slow X2 selfcheck · Alpha 闸门审（组合/衰减过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 03:33 ET**（America/New_York） |
| **主裁决 VERDICT** | **HOLD** |
| 一句话理由 | decay=**DECAY_DOWNGRADE** ∧ 门A/B/current **全 false** ∧ cost **untradable=true**；清单禁对非 KEEP / GATE_V3 本地 FAIL 派烟；**A=true 亦不解阻 X2 ACCEPT**（本拍 A=false） |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠自开 Book-Smoke** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** / **禁 RESTORED `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`fc7e712a`**（`.ok` 归档 **`4bb141c9`**） |
| QUIET lift | 原 sha8 **`351e98fb`** → `_lifted/…PASS_LIFTED_20261027T0329ET.lock`；现盘 **ABSENT** |
| 前序构建闸 | sha8 **`a476567d`**（ACCEPT **仅构建过程**；本审**不回撤**） |
| 叶30 selfcheck | HOLD sha8 **`f00536b9`**（**不回撤**）；`0087c928` 另队 |
| report | `output/ai_factory/leaf_reports/leaf31_amihud/selfcheck_v1.json` sha8 **`d4553423`** |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **HOLD** | 研究披露 selfcheck 数字；不建议 Eng Book-Smoke；≠X2 ACCEPT |
| 钉对齐 | **MATCH** | Arch/archived `.ok`/QUIET lift/report/eval_weights/alpha/meta/overlap/脚本/RUN_RECEIPT/前序构建闸 前 8 全 MATCH；live `.ok`=0；QUIET ABSENT |
| 门A | **false** | 60w/100w A_debeta CAGR·MDD **均未**优于同档 capacity；**即便 A=true 亦不解阻 X2 ACCEPT** |
| 门B | **false** | 两档 overlay Calmar **均未**优于 capacity（60w 1.233&lt;1.254；100w 1.358&lt;1.468）；MDD 虽未破 −15% 仍总 B=false |
| current / GATE_V3 本地 | **false** | 两档 overlay CAGR **未**优于 capacity；衰减非 KEEP → 清单本地 FAIL |
| decay | **DECAY_DOWNGRADE** | `latest_alpha<0` + `alpha_declined_5q` + `H2_net_cagr<=510300` |
| cost | **untradable=true** | 无毛超额且成本拖累&gt;1%/年；net_cagr≈−4.80% vs bench≈11.26% |
| Book-Smoke 建议 | **否** | 清单：不派烟给「衰减非 KEEP / GATE_V3 本地 FAIL」；Alpha 不派；须衰减修复/另窗 KEEP 或主明示例外才再议 |
| JSON 旗标 | x2_accept=false · book_smoke=false · live=false | 与裁决一致 |
| 二次写盘 | 已披露；两趟 eval_weights **字节同** `346cf077` | **禁再复跑** |

**主裁决词单列**：**HOLD** = selfcheck 收益/组合过程**不过晋级闸**；数字可披露。**不是** X2 ACCEPT，**不是** Book-Smoke 授权。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `fc7e712a` | `fc7e712a40d03956f00ab23b56fc355817e3f1ccaddaf7429db298fc642f5333` | **MATCH** |
| archived `.ok` 内容 | `4bb141c9` | `4bb141c90ca3e934dd04645f8656f9a06455e1c6d3167688b0988c7c440b5d58`（路径 `_consumed/…4bb141c9.CONSUMED_PASS.20261027T0329ET.ok`） | **MATCH** |
| QUIET lift 原锁 | `351e98fb` | `351e98fbcd53e0144914744f97ad44eee2a4e392b62f466d78bbd58bf7ed3e87`（`_lifted/…selfcheck_PASS_LIFTED_20261027T0329ET.lock`） | **MATCH** |
| report `selfcheck_v1.json` | `d4553423` | `d4553423f2f7d2cd8dc8c1628f2c8cf439fe3f49d3f343e84cba8e6373ecbf1e` | **MATCH** |
| eval_weights parquet（152340） | `346cf077` | `346cf077eaf95a7c15cf6981e3189ef3c4e5aeaf4da73007129c85720e2698d8` | **MATCH** |
| eval_weights 二次写盘（152306） | （同字节） | 同 `346cf077…` | **MATCH**（SAME_BYTES） |
| alpha parquet | `d4ceb78b` | `d4ceb78b1d4b7c5516149a74bad87141083695ac6c4b7be43e3fa9a64c4452ce` | **MATCH**（UNCHANGED） |
| meta `run_meta.json` | `696ab1cc` | `696ab1cc25eed077cf7171b4461e8e6946677901c3fbfaf68be5cd55c4d9ab12` | **MATCH** |
| overlap json | `8396f211` | `8396f2111411dd0f9040d0215369394e83e646adca2dac15072b1003289df75b` | **MATCH** |
| 脚本 `leaf31_amihud_impact_slow_x2_selfcheck_v1.py` | `e1fe578c` | `e1fe578ca70bd61f6c98bd849357beecb918f9e88f0732ac6bbc98dcfb0d4b38` | **MATCH** |
| AI RUN_RECEIPT | `af3cc528` | `af3cc5285c134f600a01db35e173674398bfc046c5afdca309676eba6c52c636` | **MATCH** |
| 前序构建闸 `a476567d` | `a476567d` | `a476567d537629f182e7c0da656a059f59708a2c1c1575b854600884a93153c0` | **MATCH** |
| 叶30 selfcheck HOLD | `f00536b9` | `f00536b9978eed619cf672bb327c4c898c9a998dbbeda167814762e3ecdac0dd` | **MATCH**（不回撤） |

附加硬钉：

| 项 | 值 | 判定 |
|---|---|---|
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF31_AMIHUD_IMPACT_SLOW_X2_SELFCHECK*.ok` ABSENT） | **PASS** |
| QUIET | `RESEARCH_QUIET.lock` **ABSENT** | **PASS** |
| RESTORED | 未恢复 `4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa`；仅 `_consumed` | **PASS** |
| JSON 旗标 | `x2_accept=false` `book_smoke=false` `live=false` `promotion_approved=false` | **PASS** |
| peak_rss | PRIMARY log/HWM≈**1015.01** MB；现盘 ru_maxrss@152340=**987.86** MB ≪ 1500 | 过程 OK（本审不重跑） |
| RUN_RECEIPT rc | **0**（`ok:true`） | **PASS** |
| 构建 ACCEPT | `a476567d` 仍成立；本审**不回撤** | 分层保留 |
| `0087c928` | 另队；本审不夹带 | **PASS** |

## 2. 闸门数字复核（自 JSON；勿盲信任务声称）

### 2.1 portfolio_gates.verdict

| 门 | JSON | 复核 |
|---|---|---|
| A | **false** | 60w A=false ∧ 100w A=false → 总 **false** |
| B | **false** | 60w B=false ∧ 100w B=false → 总 **false** |
| current | **false** | 60w=false ∧ 100w=false → 总 **false** |

### 2.2 分档 overlay / capacity / A_debeta（净；引擎 T+1 next_open）

| 档 | 口径 | CAGR | MDD | Calmar |
|---|---|---|---|---|
| 60万 | capacity | 17.85% | −14.24% | 1.254 |
| 60万 | **overlay** | **16.82%** | **−13.64%** | **1.233** |
| 60万 | A_debeta | 14.40% | −15.64% | 0.921 |
| 100万 | capacity | 18.30% | −12.47% | 1.468 |
| 100万 | **overlay** | **17.76%** | **−13.07%** | **1.358** |
| 100万 | A_debeta | 14.80% | −14.25% | 1.039 |

（JSON 精确：60w overlay cagr=`0.168247…` mdd=`-0.136438…` calmar=`1.23314…`；100w overlay cagr=`0.177582…` mdd=`-0.130725…` calmar=`1.35843…`。capacity 60w=`0.178516…`/`-0.142402…`；100w=`0.183031…`/`-0.124678…`。）

与任务声称 **MATCH**（约数对齐）。

### 2.3 cost

| 项 | 值 |
|---|---|
| net_cagr | **≈−4.80%**（`-0.047990…`） |
| bench_cagr | **≈11.26%**（`0.112592…`） |
| gross_cagr | ≈−1.91% |
| cost_drag_ann | ≈3.01% |
| to_2s_mean | ≈0.070 |
| untradable | **true**（理由：无毛超额且成本拖累&gt;1%/年） |

与任务声称 **MATCH**。

## 3. decay 含义（对照 `ALPHA_DECAY_GATE_PREREG_ZH.md` / v1.1）

| 项 | JSON 实数 | 规则含义 |
|---|---|---|
| outcome | **DECAY_DOWNGRADE** | v1：最新 α&lt;0 **或** 季 α 连降 3 **或** H1/H2 任一失败 |
| reasons | `['latest_alpha<0', 'alpha_declined_5q', 'H2_net_cagr<=510300']` | **三触发** |
| latest_resid_alpha | **−0.22847**（年化残差 α） | **&lt;0** → 硬触发 DOWNGRADE |
| consecutive_declines | **5** | ≥3 → `alpha_declined_5q` 触发 |
| H2 | net_cagr≈**−23.88%** vs bench_net_cagr≈**−3.37%** | 窗内净 CAGR **未优于** 510300 → H2 失败 |
| H1 换手 | turnover_mean_2s≈0.0711 | **未**触发（&lt;20%） |
| quarterly_alpha 近端 | 2026-03-31=−0.174；2026-06-30=−0.1825；2026-09-30=−0.2207；2026-10-09=−0.2285 | 近端持续为负且连降 |
| window | 2024-06-04→2026-10-09（569 日） | short_history=false |
| prereg_sha256 | `eecc84ba…` | 与衰减预注册钉一致路径 |

**过程含义**：残差 α 最新点大幅为负，季 α 连降 5，且同窗净收益跑输 510300 → 衰减闸 **只降不升** 语义下标 DOWNGRADE；对照验收清单 §3.4 / §4.3：**必须 KEEP** 才可请 Eng → 本叶 **不满足**。

## 4. 与门A / 门B / 现行对照

对照 `ALPHA_GATE_AB_PREREG_20261014_ZH.md` + `GATE_V3_MDD25_PREREG_ZH.md` + `ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

### 4.1 门A（去β再叠；研究口径）

- 定义：卫星先去β再 80/20；两档 CAGR 与 MDD 都优于 capacity。
- 结果：**A=false**（60w A_debeta CAGR 14.40%&lt;17.85%、MDD −15.64% 更深；100w CAGR 14.80%&lt;18.30%、MDD 更深）。
- **硬句**：**A=true 亦不解阻 X2 ACCEPT**（本拍 A=false，仍写清该硬钉）；不构成晋级 / 不构成 Book-Smoke 授权。

### 4.2 门B（不去β叠）

- 定义：两档 Calmar 都优于 capacity，且 MDD **不深于 −15%**。
- 60万：overlay MDD≈−13.64% **未**破 −15%，但 Calmar≈**1.233** **未**优于 capacity≈**1.254** → 单档 B=false。
- 100万：overlay MDD≈−13.07% 不破 −15%，但 Calmar≈**1.358** **未**优于 capacity≈**1.468** → 单档 B=false。
- 总裁决须两档皆过 → **B=false**。

### 4.3 现行 / GATE_V3 本地

- 现行门（AB 预注册）：两档 CAGR 与 MDD 都优于 capacity，且 MDD 不深于 −25%。
  - 60万：overlay CAGR 16.82% **&lt;** capacity 17.85% → fail。
  - 100万：overlay CAGR 17.76% **&lt;** capacity 18.30%；MDD −13.07% **深于** capacity −12.47% → fail。
  - → **current=false**（与 JSON 一致）。
- GATE_V3 清单四条：MDD≤25%（本 overlay 两档满足）∧ 净 CAGR 严格高于 HI_LIQ capacity（**本叶未满足**）∧ 衰减=**KEEP**（**本叶 DOWNGRADE**）∧ 可交易（**本叶 untradable=true**）。
- → **GATE_V3 本地 FAIL**；清单 §6：**不派烟给「衰减非 KEEP / GATE_V3 本地 FAIL」的叶**。

## 5. 披露边界

| 可披露 | 不可宣称 |
|---|---|
| selfcheck 入口数字（上表 CAGR/MDD/Calmar/cost/decay） | **X2 ACCEPT** / 晋级 / 纸面 |
| 门A=false（及 A=true 亦不解阻硬钉） | 门A 解阻实盘或 X2 |
| 构建过程 ACCEPT（`a476567d`）仍成立 | 收益过程 / 组合门过闸 |
| HOLD + Book-Smoke=否 | Alpha 自开烟 / 恢复 `_consumed` `.ok` |
| 二次写盘透明披露（字节同） | 据此复跑 / 抬帽 |

附注：JSON `pin_gap.gap_fields` 仍列 ic/icir/walk_forward；evaluate 产出为 decay/cost/portfolio_gates，**未见**独立 IC/ICIR/WF 字段。本审以组合闸+衰减为准；**不**据此单独 REJECT（非钉假/作弊），亦不宣称 IC 过闸。

## 6. 下一步（给主；Alpha 不执行）

1. **维持 HOLD**；**不建议**令 Eng Book-Smoke（除非主明示豁免衰减/清单例外——本审不假设）。
2. 若续研：衰减修复（近端残差 α 转正 + 打断连降 + H2 净 CAGR 优于 510300）且 cost 可交易后，再议组合闸；门A/B/current 均需先解决 overlay/A_debeta 劣于 capacity。
3. **禁止**：签.ok；开跑；RESTORED `4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`；自开 Book-Smoke；宣布 X2 ACCEPT；改 FROZEN_CONFIG/paper/alpha_labels；报 Leo；再复跑 selfcheck。
4. 叶30 HOLD `f00536b9` **不回撤**；构建闸 `a476567d` **不回撤**；`0087c928` 另队。

---

**VERDICT=HOLD** · Book-Smoke 建议=**否** · ≠X2 ACCEPT · live=false · leo_notify=false
