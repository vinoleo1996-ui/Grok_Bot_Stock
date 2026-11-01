# 叶32 Margin Net Flow Resid X2 selfcheck · Alpha 闸门审（组合/衰减过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 05:38 ET**（America/New_York） |
| **主裁决 VERDICT** | **HOLD** |
| 一句话理由 | decay=**KEEP**（≠叶30/31 DECAY_DOWNGRADE）∧ 门A/B/current **总 false** ∧ cost **untradable=true**；KEEP **不解阻** X2 ACCEPT，亦不自动过组合闸；主硬钉 **≠Book-Smoke / 不派 Eng**；**A=true 亦不解阻 X2 ACCEPT**（本拍 A=false） |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠自开 Book-Smoke** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** / **禁 RESTORED `5774bb6e`+`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`+二十票其余** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`efa033e0`**（`.ok` 归档 **`5774bb6e`**） |
| QUIET lift | 原 sha8 **`3301eb86`** → `_lifted/…selfcheck_PASS_LIFTED_20261027T0534ET.lock`；现盘 **ABSENT** |
| 前序构建闸 | sha8 **`1aa432a5`**（ACCEPT **仅构建过程**；本审**不回撤**） |
| 叶31 selfcheck | HOLD sha8 **`7ef5aa11`**（**不回撤**） |
| 叶30 selfcheck | HOLD sha8 **`f00536b9`**（**不回撤**）；`0087c928` 另队 |
| report | `output/ai_factory/leaf_reports/leaf32_margin_flow/selfcheck_v1.json` sha8 **`99675387`** |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **HOLD** | 研究披露 selfcheck 数字；不建议 Eng Book-Smoke；≠X2 ACCEPT |
| 钉对齐 | **MATCH** | Arch/archived `.ok`/QUIET lift/report/eval_weights/alpha/meta/overlap/脚本/RUN_RECEIPT/SIGNED/审/前序构建闸 前 8 全 MATCH；live `.ok`=0；QUIET ABSENT |
| 门A | **false** | 60w/100w A_debeta MDD **均深于**同档 capacity → 总 **false**；**即便 A=true 亦不解阻 X2 ACCEPT** |
| 门B | **false** | 60w overlay MDD≈−15.15% **破** −15% → 单档 B=false；100w B=true；总须两档皆过 → **B=false** |
| current / GATE_V3 本地 | **false** | 60w current=false（MDD 劣于 capacity）；100w current=true；总 **false**；GATE_V3：KEEP 满足但 untradable + 组合门未过 → 本地 FAIL |
| decay | **KEEP** | `latest_resid_alpha>0` ∧ `consecutive_declines=1` ∧ H2 net_cagr 优于 510300；reasons=[]；**≠**叶30/31 DECAY_DOWNGRADE |
| cost | **untradable=true** | 成本拖累&gt;毛超额一半（drag≈3.69% vs gross_excess≈5.41%） |
| Book-Smoke 建议 | **否** | 主硬约束 ≠Book-Smoke / 不派 Eng；组合门总 false + untradable；KEEP **不**自动开烟 |
| JSON 旗标 | x2_accept=false · book_smoke=false · live=false | 与裁决一致 |
| KEEP vs HOLD | KEEP 仅衰减过程非 DOWNGRADE | **不解阻** X2 ACCEPT；**不自动** ACCEPT 组合闸 |

**主裁决词单列**：**HOLD** = selfcheck 收益/组合过程**不过晋级闸**；数字可披露；decay=KEEP 须披露。**不是** X2 ACCEPT，**不是** Book-Smoke 授权。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `efa033e0` | `efa033e05f8a1a4d47ef7b63429da5b753b7355599d64f8b9c370075478389cf` | **MATCH** |
| archived `.ok` 内容 | `5774bb6e` | `5774bb6e8a1ad3e5dc879561b4cb3f08b9a6ad67e2bbdf34168f9c2117d26909`（路径 `_consumed/…5774bb6e.CONSUMED_PASS.20261027T0534ET.ok`） | **MATCH** |
| QUIET lift 原锁 | `3301eb86` | `3301eb8635e224ef38200ff413872f2780f5bee060f204e0b91db6b844a2c2ad`（`_lifted/…selfcheck_PASS_LIFTED_20261027T0534ET.lock`） | **MATCH** |
| report `selfcheck_v1.json` / side_meta | `99675387` | `996753878d9ebfeb67f7c3076194c84ec7ad6b644ed69f0024b9beb4b4b82692` | **MATCH** |
| eval_weights parquet | `6ef6741a` | `6ef6741a761b6c1ad78524ae9f26169404fb0974b3ed783f4b7b8d64d28fa820`（`…/_selfcheck/eval_weights_HILIQ_x2_20261027_172541.parquet`） | **MATCH** |
| alpha parquet | `13eee6fd` | `13eee6fdf0922b14756cf22985964dcd177810772a2ee4ec3bdb7c1668646ed2` | **MATCH**（UNCHANGED） |
| meta `run_meta.json` | `e510f346` | `e510f346bed46e6ca64f802de3aaed5f28f469f0a2fbf68ee2d5f2fffc4f6610` | **MATCH** |
| overlap json | `a643d71a` | `a643d71ad77e3ae06eab2dc1fb20a0b99bf3d572db9310821b00ba8627bfe5fe` | **MATCH** |
| 脚本 selfcheck `leaf32_…_x2_selfcheck_v1.py` | `dcf6b559` | `dcf6b559165e43dcaa56df8adc3cb5d9574b6b55cc5ba20cf39d97b0285cda4f` | **MATCH** |
| 构建脚本 `leaf32_…_alpha_build.py` | `4e0f3c00` | `4e0f3c002057393c031598e0379c6622afe8ca4a18579c9ab3b9f3d7ba4ae187` | **MATCH**（UNCHANGED） |
| AI RUN_RECEIPT | `89c1f1b0` | `89c1f1b0b0e564b0ec20fa9243f8bff4ee3f4dce01c13a5b78bc082243537665` | **MATCH** |
| SIGNED | `e00f8f51` | `e00f8f51f5e4ec27c4ad802a7dd03324b83edb1fbe26bf13d63efd73f03961cd` | **MATCH** |
| Arch 审 | `3d7a5848` | `3d7a584880e13898ce34bf528630e8386e251e7aed671079199f816a2ae5933d` | **MATCH** |
| 前序构建闸 `1aa432a5` | `1aa432a5` | `1aa432a5c0529122c13f8ef05a42ac37921bf3a3c738e7ffe6778eb896c0d885` | **MATCH**（不回撤） |
| 叶31 selfcheck HOLD | `7ef5aa11` | `7ef5aa1195b4e6426f6399a798df1fefe5384f692616d34bd88dfa78eaf3195d` | **MATCH**（不回撤） |
| 叶30 selfcheck HOLD | `f00536b9` | `f00536b9978eed619cf672bb327c4c898c9a998dbbeda167814762e3ecdac0dd` | **MATCH**（不回撤） |

附加硬钉：

| 项 | 值 | 判定 |
|---|---|---|
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF32_*SELFCHECK*.ok` 顶层 ABSENT） | **PASS** |
| QUIET | `RESEARCH_QUIET.lock` **ABSENT** | **PASS** |
| RESTORED | 未恢复 `5774bb6e`/`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` 及二十票其余；仅 `_consumed` | **PASS** |
| JSON 旗标 | `x2_accept=false` `book_smoke=false` `live=false` `promotion_approved=false` | **PASS** |
| peak_rss | sampler HWM≈**945328** KB（≈923.17 MB）；ru_maxrss/PRIMARY≈**923.17** MB ≪ 1500 | 过程 OK（本审不重跑） |
| RUN_RECEIPT rc | **0**（`ok:true`） | **PASS** |
| 构建 ACCEPT | `1aa432a5` 仍成立；本审**不回撤** | 分层保留 |
| `0087c928` | 另队；本审不夹带 | **PASS** |

## 2. 闸门数字复核（自 JSON；勿盲信任务声称）

### 2.1 portfolio_gates.verdict

| 门 | JSON 总 | 60w | 100w | 复核 |
|---|---|---|---|---|
| A | **false** | false | false | 两档皆 false → 总 **false** |
| B | **false** | false | **true** | 须两档皆过 → 总 **false** |
| current | **false** | false | **true** | 须两档皆过 → 总 **false** |

与任务声称 **MATCH**（100w current/B 单档 true，verdict 仍全 false）。

### 2.2 分档 overlay / capacity / A_debeta（净；引擎 T+1 next_open）

| 档 | 口径 | CAGR | MDD | Calmar |
|---|---|---|---|---|
| 60万 | capacity | 17.85% | −14.24% | 1.254 |
| 60万 | **overlay** | **26.34%** | **−15.15%** | **1.738** |
| 60万 | A_debeta | 18.59% | −14.65% | 1.269 |
| 100万 | capacity | 18.30% | −12.47% | 1.468 |
| 100万 | **overlay** | **24.63%** | **−11.88%** | **2.074** |
| 100万 | A_debeta | 19.04% | −13.23% | 1.439 |

（JSON 精确：60w overlay cagr=`0.263356…` mdd=`-0.151540…` calmar=`1.73786…`；100w overlay cagr=`0.246317…` mdd=`-0.118785…` calmar=`2.07365…`。capacity 60w=`0.178516…`/`-0.142402…`；100w=`0.183032…`/`-0.124679…`。）

### 2.3 cost

| 项 | 值 |
|---|---|
| net_cagr | **≈12.45%**（`0.124547…`） |
| bench_cagr | **≈11.26%**（`0.112592…`） |
| gross_cagr | ≈16.67% |
| gross_excess | ≈5.41% |
| cost_drag_ann | ≈3.69% |
| to_2s_mean | ≈0.0865 |
| untradable | **true**（理由：成本拖累&gt;毛超额一半） |

与任务声称 **MATCH**。

## 3. decay 含义（对照 `ALPHA_DECAY_GATE_PREREG_ZH.md` / v1.1）

| 项 | JSON 实数 | 规则含义 |
|---|---|---|
| outcome | **KEEP** | v1：最新 α&gt;0 ∧ 非季 α 连降≥3 ∧ H1/H2 皆过 |
| reasons | `[]` | **无触发** |
| latest_resid_alpha | **+0.12305**（年化残差 α） | **&gt;0** → 未触发 DOWNGRADE |
| consecutive_declines | **1** | &lt;3 → 未触发 `alpha_declined_*q` |
| H2 | net_cagr≈**+4.96%** vs bench_net_cagr≈**−3.37%** | 窗内净 CAGR **优于** 510300 → H2 过 |
| H1 换手 | turnover_mean_2s≈0.0867 | **未**触发（&lt;20%） |
| quarterly_alpha 近端 | 2026-06-30=+0.1508；2026-09-30=+0.1674；2026-10-09=+0.123 | 近端为正；仅末点相对前季回落 1 步 |
| window | 2024-06-04→2026-10-09（569 日） | short_history=false |
| prereg_sha256 | `eecc84ba…` | 与衰减预注册钉一致路径 |

**与叶30/31 差异**：叶30/31 均为 **DECAY_DOWNGRADE**（`latest_alpha<0` + 连降 + H2 失败）。本叶 **KEEP**——衰减过程**非** DOWNGRADE，须披露。

**为何仍 HOLD**：KEEP **仅**表示衰减三闸未触发降级；清单/主硬钉下，组合门 A/B/current 总 false、cost untradable、且 **≠Book-Smoke / ≠X2 ACCEPT** → KEEP **不解阻**晋级，也**不自动** ACCEPT 组合闸。

## 4. 与门A / 门B / 现行对照

对照 `ALPHA_GATE_AB_PREREG_20261014_ZH.md` + `GATE_V3_MDD25_PREREG_ZH.md` + `ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

### 4.1 门A（去β再叠；研究口径）

- 定义：卫星先去β再 80/20；两档 CAGR 与 MDD 都优于 capacity。
- 60万：A_debeta CAGR 18.59%&gt;17.85%，但 MDD −14.65% **深于** capacity −14.24% → 单档 A=false。
- 100万：A_debeta CAGR 19.04%&gt;18.30%，但 MDD −13.23% **深于** capacity −12.47% → 单档 A=false。
- → **A=false**。
- **硬句**：**A=true 亦不解阻 X2 ACCEPT**（本拍 A=false，仍写清该硬钉）；不构成晋级 / 不构成 Book-Smoke 授权。

### 4.2 门B（不去β叠）

- 定义：两档 Calmar 都优于 capacity，且 MDD **不深于 −15%**。
- 60万：overlay Calmar≈**1.738** 优于 capacity≈**1.254**，但 MDD≈**−15.15%** **破** −15% → 单档 B=false。
- 100万：overlay Calmar≈**2.074** 优于 capacity≈**1.468**，MDD≈**−11.88%** 不破 −15% → 单档 B=true。
- 总裁决须两档皆过 → **B=false**。

### 4.3 现行 / GATE_V3 本地

- 现行门（AB 预注册）：两档 CAGR 与 MDD 都优于 capacity，且 MDD 不深于 −25%。
  - 60万：overlay CAGR 26.34%&gt;17.85%，但 MDD −15.15% **深于** capacity −14.24% → fail → current=false。
  - 100万：overlay CAGR 24.63%&gt;18.30% 且 MDD −11.88% **优于** −12.47% → current=true。
  - → **current=false**（与 JSON 一致）。
- GATE_V3 清单四条：MDD≤25%（本 overlay 两档满足）∧ 净 CAGR 严格高于 HI_LIQ capacity（60w MDD 路径未过现行；组合总 false）∧ 衰减=**KEEP**（**本叶满足**）∧ 可交易（**本叶 untradable=true**）。
- → **GATE_V3 本地 FAIL**（KEEP 不够；untradable + 组合门阻断晋级路径）；主硬钉另禁烟。

## 5. 披露边界

| 可披露 | 不可宣称 |
|---|---|
| selfcheck 入口数字（上表 CAGR/MDD/Calmar/cost/decay KEEP） | **X2 ACCEPT** / 晋级 / 纸面 |
| decay=KEEP（及与叶30/31 DOWNGRADE 差异） | KEEP 解阻实盘 / X2 / 自动过组合闸 |
| 门A=false（及 A=true 亦不解阻硬钉）；100w 单档 B/current true | 单档 true 解阻总裁决 |
| 构建过程 ACCEPT（`1aa432a5`）仍成立 | 收益过程 / 组合门过闸 |
| HOLD + Book-Smoke=否 | Alpha 自开烟 / 恢复 `_consumed` `.ok` / 派 Eng |

附注：JSON `pin_gap.gap_fields` 仍列 ic/icir/walk_forward；evaluate 产出为 decay/cost/portfolio_gates，**未见**独立 IC/ICIR/WF 字段。本审以组合闸+衰减为准；**不**据此单独 REJECT（非钉假/作弊），亦不宣称 IC 过闸。

## 6. 下一步（给主；Alpha 不执行）

1. **维持 HOLD**；**不建议**令 Eng Book-Smoke（主已禁烟；本审不假设例外）。
2. 若续研：先解决 60w overlay MDD 破 −15%/劣于 capacity，以及两档 A_debeta MDD；并把 cost 拖累压到可交易阈值；KEEP 已满足可保留披露。
3. **禁止**：签.ok；开跑；RESTORED `5774bb6e`+`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`（及二十票：`3c297052`/`e107383f`/`2be59acd`/`a7d98ac9`/`8e51de63`/`3a6caa4f`/`8bcd79dc`/`725be3e0`/`0f50daf7`/`3c19dd7d`/`1c32ab1e`/`6054b3bf`/`6de02e74`）；自开 Book-Smoke；宣布 X2 ACCEPT；改 FROZEN_CONFIG/paper/alpha_labels；报 Leo；再复跑 selfcheck；抬帽。
4. 叶31 HOLD `7ef5aa11` / 叶30 HOLD `f00536b9` **不回撤**；构建闸 `1aa432a5` **不回撤**；`0087c928` 另队。

---

**VERDICT=HOLD** · decay=**KEEP**（仍 HOLD） · Book-Smoke 建议=**否** · ≠X2 ACCEPT · live=false · leo_notify=false
