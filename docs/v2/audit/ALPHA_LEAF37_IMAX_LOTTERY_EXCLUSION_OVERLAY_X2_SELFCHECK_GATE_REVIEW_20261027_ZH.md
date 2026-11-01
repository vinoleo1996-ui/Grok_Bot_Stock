# 叶37 IMAX Lottery Exclusion Overlay X2 selfcheck · Alpha 闸门审（新口径）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 19:42 ET**（America/New_York） |
| **主裁决 VERDICT** | **HOLD** |
| 一句话理由 | decay=**KEEP** ≠ ACCEPT ∧ 门A/B/current **总 false** ∧ **ρ_excess≈0.9589≫0.5**（高度近似主干）∧ overlay **略逊** capacity ∧ cost **untradable=true**；KEEP **不解阻** X2 ACCEPT；主硬钉 **≠Book-Smoke / 不派 Eng / 禁晋级** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠自开 Book-Smoke** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** / **禁 RESTORED `57ab9096`+`b5be1164`+`4096d401`+…（forbid_n=32+本票）** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`4afd5ae1`**（`.ok` 归档 **`57ab9096`**） |
| QUIET | **ABSENT**（本票从未挂；无需 lift） |
| 上游 B1 CONSUME | sha8 **`c0a6b5ae`** / consumed build `.ok` **`b5be1164`**（本审不回撤、不 RESTORED） |
| 对齐先例 | 叶32 selfcheck HOLD sha8 **`45dd87dc`**（主文「叶34」实指该 sha；新口径：工程 DONE≠Alpha ACCEPT；KEEP≠ACCEPT） |
| 叶31 / 叶30 | HOLD **`7ef5aa11`** / **`f00536b9`**（**不回撤**） |
| report | `output/ai_factory/leaf_reports/leaf37_imax_lottery/selfcheck_v1.json` sha8 **`d27a53f5`**（≡ `_selfcheck/selfcheck_run_meta_…073125.json` 同 sha） |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **HOLD** | 研究披露 selfcheck 数字；不建议 Eng Book-Smoke；≠X2 ACCEPT；禁晋级 |
| 钉对齐 | **MATCH** | Arch/archived `.ok`/RECEIPT/report≡meta/weights/脚本/mask/meta/overlap/B1 CONSUME 前 8 全 MATCH；live `.ok` ABSENT；QUIET ABSENT |
| 门A | **false** | 60w/100w A_debeta：**CAGR 逊于** capacity 且 MDD **深于** capacity → 总 **false** |
| 门B | **false** | 60w overlay Calmar≈0.898 **略逊** capacity≈0.900 → 单档 B=false；100w B=true；总须两档皆过 → **B=false** |
| current | **false** | 60万 overlay CAGR≈0.1269 **&lt;** cap≈0.1282；100万≈0.1508 **&lt;** 0.1519 → 两档 current false → 总 **false** |
| decay | **KEEP** | latest_resid_alpha&gt;0 ∧ consecutive_declines=0 ∧ H2 net_cagr 优于 510300；**KEEP≠ACCEPT**；不解阻 X2 |
| ρ_excess | **≈0.9589 ≫ 0.5** | 与 capacity_adv 日超额高度相关 → **近亲/近似主干风险** → **强化 HOLD**；禁烟禁晋级 |
| cost | **untradable=true** | 成本拖累&gt;毛超额一半（drag≈1.10% vs gross_excess≈0.59%） |
| Book-Smoke 建议 | **否** | 主硬约束 + ρ≫0.5 + 组合门总 false + untradable；KEEP **不**自动开烟 |
| JSON 旗标 | x2_accept=false · book_smoke=false · live=false · promotion_approved=false | 与裁决一致 |
| 工程 DONE | CONSUMED_PASS / rc=0 / peak≈960MB | **≠** Alpha ACCEPT（新口径硬句） |

**主裁决词单列**：**HOLD** = selfcheck 收益/组合过程**不过晋级闸**；数字可披露；decay=KEEP 与 ρ_excess≫0.5 **须披露**。**不是** X2 ACCEPT，**不是** Book-Smoke 授权，**不是**晋级。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| Arch CONSUMED_PASS | `4afd5ae1` | `4afd5ae15562febc49ce4011f672fa7d4c04107673fc9666ee8744d6c778d601` | **MATCH** |
| archived `.ok` 内容 | `57ab9096` | `57ab909622f1edaf2c19dd3f40824a20b6ef407b8b3436c9dafe1fabc820fa64`（路径 `_consumed/…57ab9096.CONSUMED_PASS.20261027T1935ET.ok`） | **MATCH** |
| AI RUN_RECEIPT | `d1976899` | `d1976899154e10ad7eb4258dae5af824fa4ee2db6f8ed0bbe840ba54c8a74155` | **MATCH** |
| report `selfcheck_v1.json` | `d27a53f5` | `d27a53f53ebaded3c242e5f2e54222665858b821b28d87fe7312e2302e457919` | **MATCH** |
| side_meta `selfcheck_run_meta_…073125.json` | （≡ report） | `d27a53f53ebaded3c242e5f2e54222665858b821b28d87fe7312e2302e457919` | **MATCH**（同 sha） |
| eval_weights parquet | `f05f1300` | `f05f130015ca1598953e8c05407b58fcadfc3d115ac68479dbaab0666320363b` | **MATCH** |
| 脚本 selfcheck `leaf37_…_x2_selfcheck_v1.py` | `015e6f06` | `015e6f0666f697d07f33ea33f4572b4e90d099ab6e6bfba74e10c00328e61e61` | **MATCH**（UNCHANGED） |
| exclusion_mask parquet | `2503a41e` | `2503a41e297442da43cca4db2598acec314c8647af954231e7c49456c0862f62` | **MATCH** |
| meta `run_meta.json` | `e9e9aa1d` | `e9e9aa1df45b95cf0e44d995a9151068bd739b5aae4592bc13b6184accfacd2f` | **MATCH** |
| overlap json | `8177578f` | `8177578f72f327fe2d20cd05760459f1a934a3dd903a6cde28651b953e368af8` | **MATCH** |
| 上游 B1 CONSUME | `c0a6b5ae` | `c0a6b5ae6a6408a3bae35b84f8daa2c4734a1ce29cdc2a87212d899bd4903c98` | **MATCH** |
| consumed build `.ok` | `b5be1164` | 路径 `_consumed/…b5be1164.CONSUMED_PASS.20261027T1843ET.ok`（内容未 RESTORED） | **MATCH**（禁 RESTORED） |
| 叶32 selfcheck HOLD | `45dd87dc` | `45dd87dc…`（`docs/v2/ALPHA_LEAF32_…GATE_REVIEW_…`） | **MATCH**（不回撤） |
| 叶31 selfcheck HOLD | `7ef5aa11` | `7ef5aa11…` | **MATCH**（不回撤） |
| 叶30 selfcheck HOLD | `f00536b9` | `f00536b9…` | **MATCH**（不回撤） |

附加硬钉：

| 项 | 值 | 判定 |
|---|---|---|
| live `.ok` | **ABSENT**（`output/ai_factory/ARCH_RUN_AUTH_LEAF37*.ok` 顶层无） | **PASS** |
| QUIET | **ABSENT**（无需 lift） | **PASS** |
| RESTORED | 未恢复 `57ab9096`/`b5be1164`/`5774bb6e`/`02426b73`/`4bb141c9`/`fdbaa512`/`aa25e989`/`7e239487`/`5af20222`/`5ae077fa` 及 forbid_n=32 其余；仅 `_consumed` | **PASS** |
| JSON 旗标 | `x2_accept=false` `book_smoke=false` `live=false` `promotion_approved=false` | **PASS** |
| PRIMARY | mask-only top_q=**0.20** × capacity_adv；C3=**B** IMAX_proxy；b1_lowmem=true | **PASS**（披露） |
| peak | ru_maxrss≈**960.07** MB ≪ 1500；build peak_kb≈1107536 | 过程 OK（本审不重跑） |
| `0087c928` | 另队；本审不夹带 | **PASS** |

## 2. 闸门数字复核（自 JSON；勿盲信任务声称）

### 2.1 portfolio_gates.verdict

| 门 | JSON 总 | 60w | 100w | 复核 |
|---|---|---|---|---|
| A | **false** | false | false | 两档皆 false → 总 **false** |
| B | **false** | false | **true** | 须两档皆过 → 总 **false** |
| current | **false** | false | false | 两档皆 false → 总 **false** |

与任务声称 **MATCH**（Gate A/B/current 全 false）。

### 2.2 分档 overlay / capacity / A_debeta（净；引擎 T+1 next_open）

| 档 | 口径 | CAGR | MDD | Calmar |
|---|---|---|---|---|
| 60万 | capacity | **12.82%** | −14.24% | 0.900 |
| 60万 | **overlay** | **12.69%** | −14.13% | **0.898** |
| 60万 | A_debeta | 12.41% | −14.66% | 0.847 |
| 100万 | capacity | **15.19%** | −12.47% | 1.218 |
| 100万 | **overlay** | **15.08%** | −12.35% | **1.221** |
| 100万 | A_debeta | 14.29% | −13.25% | 1.079 |

（JSON 精确：60w overlay cagr=`0.1268699…` vs cap=`0.1282235…`；100w overlay=`0.1508451…` vs cap=`0.1518719…`。overlay **略逊** capacity → current FAIL。）

### 2.3 ρ_excess（新口径强化项）

| 项 | 值 |
|---|---|
| ρ_excess vs capacity_adv | **0.9589024987797109** ≈ **0.9589** |
| 阈值 | ≫ **0.5**（预注册：ρ&lt;0.5 才可走「叠加优于主干」旁路） |
| 含义 | 叶超额与主干 capacity_adv 高度相关 → **近亲/近似主干**；即使单档数字改善，亦**不**构成独立 α 晋级证据 |
| 对裁决 | **强化 HOLD**；禁 Book-Smoke；禁 X2 ACCEPT；禁晋级 |

与任务声称 **MATCH**。

### 2.4 cost

| 项 | 值 |
|---|---|
| net_cagr | ≈**11.29%**（`0.112927…`） |
| bench_cagr | ≈**11.93%**（`0.119283…`） |
| gross_cagr | ≈12.52% |
| gross_excess | ≈0.59% |
| cost_drag_ann | ≈1.10% |
| to_2s_mean | ≈0.0258 |
| untradable | **true**（理由：成本拖累&gt;毛超额一半） |

## 3. decay 含义（KEEP ≠ ACCEPT）

| 项 | JSON 实数 | 规则含义 |
|---|---|---|
| outcome | **KEEP** | 最新残差 α&gt;0 ∧ 非五季连降 ∧ H2 净 CAGR 优于 510300 |
| reasons | `[]` | **无触发** |
| latest_resid_alpha | **+0.02321** | **&gt;0** → 未触发 DOWNGRADE |
| consecutive_declines | **0** | &lt;阈值 → 未触发连降 |
| H2 | net_cagr≈**+0.78%** vs bench_net_cagr≈**−3.37%** | 窗内净 CAGR **优于** 510300 → H2 过 |
| H1 换手 | turnover_mean_2s≈0.0318 | **未**触发 |
| window | 2024-01-03→2026-10-09（667 日） | short_history=false |
| keep_does_not_unblock_x2_accept | **true**（JSON 明示） | 与叶32 `45dd87dc` 对齐 |

**为何仍 HOLD（新口径）**：

1. **工程 DONE / CONSUMED_PASS ≠ Alpha ACCEPT**。
2. **KEEP ≠ ACCEPT**；KEEP 仅衰减过程非 DOWNGRADE，**不解阻** X2 ACCEPT。
3. 门 A/B/current **总 false** → 组合闸不过。
4. **ρ_excess≫0.5** → 高度近似主干，强化 HOLD，禁烟禁晋级。
5. overlay **略逊** capacity → current FAIL。
6. cost **untradable**；主硬钉另禁 Book-Smoke / 禁晋级。

即使数字意外过门，主硬禁下仍**不得**建议烟/ACCEPT 晋级；本拍数字**未**过门，裁决为 **HOLD**。

## 4. 与门A / 门B / 现行对照

### 4.1 门A（去β再叠）

- 60万：A_debeta CAGR 12.41% **&lt;** cap 12.82%，MDD −14.66% **深于** −14.24% → A=false。
- 100万：A_debeta CAGR 14.29% **&lt;** cap 15.19%，MDD −13.25% **深于** −12.47% → A=false。
- → **A=false**。即便 A=true 亦不解阻 X2 ACCEPT（本拍写清硬钉）。

### 4.2 门B（不去β叠）

- 60万：overlay Calmar≈0.898 **略逊** capacity≈0.900（MDD −14.13% 不破 −15%）→ 单档 B=false。
- 100万：overlay Calmar≈1.221 **略优** capacity≈1.218，MDD −12.35% 不破 −15% → 单档 B=true。
- 总须两档皆过 → **B=false**。

### 4.3 现行 / current

- 两档 overlay CAGR **均略逊** capacity（60w 12.69%&lt;12.82%；100w 15.08%&lt;15.19%）→ **current=false**。
- 叠加 ρ≫0.5：旁路「ρ&lt;0.5 且叠加优于主干」**不可用**。

## 5. 披露边界

| 可披露 | 不可宣称 |
|---|---|
| selfcheck 入口数字（CAGR/MDD/Calmar/cost/decay KEEP/ρ≈0.9589） | **X2 ACCEPT** / 晋级 / 纸面 / Book-Smoke |
| decay=KEEP（KEEP≠ACCEPT；对齐 `45dd87dc`） | KEEP 解阻实盘 / X2 / 自动过组合闸 |
| ρ_excess≫0.5 → 近亲风险 → 强化 HOLD | 「高度相关=可晋级」或烟测授权 |
| PRIMARY=mask-only top_q=0.20；C3=B IMAX_proxy；b1_lowmem | 完整主 α TopN / 叶24 同机制 |
| 工程 CONSUMED_PASS / peak≪1500 | Alpha 收益过程 ACCEPT |
| HOLD + Book-Smoke=否 | 自开烟 / RESTORED `_consumed` `.ok` / 派 Eng |

## 6. 下一步（给主；Alpha 不执行）

1. **维持 HOLD**；**不建议**令 Eng Book-Smoke；**不**晋级；**不**宣布 X2 ACCEPT。
2. 若续研：需同时满足 ρ_excess&lt;0.5（或证明独立信息）**且** 60w/100w overlay 严格优于 capacity，并把 cost 拖累压到可交易；KEEP 可保留披露。
3. **禁止**：签.ok；开跑/复跑；RESTORED `57ab9096`+`b5be1164`+`4096d401`+`eb70eef4`+`00eec671`+`10927bd9`+`25ae4572`+`178e90e9`+`c1b71e64`+`245df63f`+`c5ed13df`+`5774bb6e`+`81521fb5`+`02426b73`+`4bb141c9`+`fdbaa512`+`aa25e989`+`7e239487`+`5af20222`+`5ae077fa`+`3c297052`+`e107383f`+`2be59acd`+`a7d98ac9`+`8e51de63`+`3a6caa4f`+`8bcd79dc`+`725be3e0`+`0f50daf7`+`3c19dd7d`+`1c32ab1e`+`6054b3bf`+`6de02e74`；自开 Book-Smoke；改 FROZEN_CONFIG/paper/alpha_labels；报 Leo；抬帽。
4. 叶32 HOLD `45dd87dc` / 叶31 HOLD `7ef5aa11` / 叶30 HOLD `f00536b9` **不回撤**；`0087c928` 另队。

---

**VERDICT=HOLD** · decay=**KEEP**（仍 HOLD） · ρ_excess≈**0.9589**≫0.5 · Book-Smoke 建议=**否** · ≠X2 ACCEPT · live=false · leo_notify=false · promotion=false
