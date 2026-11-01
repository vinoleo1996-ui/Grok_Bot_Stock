# 叶30 CRR X2 selfcheck · Alpha 闸门审（组合/衰减过程）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Alpha 执行手 |
| 时刻 | **2026-10-27 01:57 ET**（America/New_York） |
| **主裁决 VERDICT** | **HOLD** |
| 一句话理由 | decay=**DECAY_DOWNGRADE** ∧（门B=false ∨ current=false）；清单禁对非 KEEP / GATE_V3 本地 FAIL 派烟；**A=true 不解阻 X2 ACCEPT** |
| live / promotion | **false** / **false** |
| ≠ | **≠X2 ACCEPT** / **≠自开 Book-Smoke** / **勿升纸面** / **不改 alpha_labels** / **不签.ok** / **不报 Leo** / **禁 RESTORED `aa25e989`** |
| Arch | **CONSUMED_PASS** 回执 sha8 **`c68382f9`**（`.ok` 归档 **`aa25e989`**） |
| 前序构建闸 | sha8 **`1c992d62`**（ACCEPT **仅构建过程**；本审**不回撤**） |
| report | `output/ai_factory/leaf_reports/leaf30_crr/selfcheck_v1.json` sha8 **`3eeffb02`** |

## 结论先行

| 项 | 结果 | 一句话 |
|---|---|---|
| **VERDICT** | **HOLD** | 研究披露 selfcheck 数字；不建议 Eng Book-Smoke；≠X2 ACCEPT |
| 钉对齐 | **MATCH** | report/eval_weights/AI/alpha/脚本/Arch/archived `.ok`/前序构建闸 前 8 全 MATCH；live `.ok`=0；QUIET ABSENT |
| 门A | **true**（60w∧100w） | **研究口径**；60/100万实盘 IF 不可行；**不解阻 X2 ACCEPT** |
| 门B | **false** | 60w overlay MDD≈**−15.09%** 破 −15% 硬线，且 Calmar≈1.08 **未**优于 capacity≈1.25；100w B=true 不足以总过 |
| current / GATE_V3 本地 | **false** | 两档 overlay CAGR/MDD **未**双优于 capacity；衰减非 KEEP → 清单本地 FAIL |
| decay | **DECAY_DOWNGRADE** | `latest_alpha<0`（latest_resid_alpha≈−0.021）+ `H2_net_cagr<=510300` |
| Book-Smoke 建议 | **否** | 清单：不派烟给「衰减非 KEEP / GATE_V3 本地 FAIL」；Alpha 不派；须衰减修复/另窗 KEEP 或主明示例外才再议 |
| JSON 旗标 | x2_accept=false · book_smoke=false · live=false | 与裁决一致 |

**主裁决词单列**：**HOLD** = selfcheck 收益/组合过程**不过晋级闸**；数字可披露。**不是** X2 ACCEPT，**不是** Book-Smoke 授权。

## 1. 钉核对（独立 sha256sum；前 8 字符）

| 物 | 声称 sha8 | 盘面 sha256 | 结果 |
|---|---|---|---|
| report `selfcheck_v1.json` | `3eeffb02` | `3eeffb023e8f438ecb3e3ae7fb93df545bb2917dfd9bcdd2b713323224ccc58b` | **MATCH** |
| side_meta `_selfcheck/selfcheck_run_meta_…json` | （同内容） | 同 `3eeffb02…` | **MATCH**（与 report 同 sha） |
| eval_weights parquet | `900970d4` | `900970d44adbec80fc1e96c39ab41cd1c823fac6107bded0a9da704c24c618e9` | **MATCH** |
| AI RUN_RECEIPT | `62bc5bd7` | `62bc5bd7492c5d33afbbeb7d204d8151e98e7cf00361fcfe3b877b71183f477b` | **MATCH** |
| alpha parquet | `c8c7a5a5` | `c8c7a5a5c8df7f2c62d28b340602b6a4c3996d43285f8e78ec3a51e6c42a07a1` | **MATCH** |
| 脚本 `leaf30_crr_x2_selfcheck_v1.py` | `797724d4` | `797724d411704ffc8dfe1fcc77039c87ffadda4e6dcd38fb60af60ee8bb27344` | **MATCH** |
| Arch CONSUMED_PASS | `c68382f9` | `c68382f96a01caf0288f4bfbb4f0daf8c33859b1237284d3fc1825056e4b9277` | **MATCH** |
| archived `.ok` 内容 | `aa25e989` | `aa25e989cf31e0810a0b485c7db7f7e0272cd2e8af9093bf3722e2c9b0b304ea`（路径 `_consumed/…aa25e989.CONSUMED_PASS.20261027T0153ET.ok`） | **MATCH** |
| 前序构建闸 `1c992d62` | `1c992d62` | `1c992d62c63ffd4560ad2ee0f738602f70e047741fc4f0cde9140953c3015f3d` | **MATCH** |

附加硬钉：

| 项 | 值 | 判定 |
|---|---|---|
| live `.ok` | **0**（`ARCH_RUN_AUTH_LEAF30_CRR_X2_SELFCHECK*.ok` ABSENT） | **PASS** |
| QUIET | `RESEARCH_QUIET.lock` **ABSENT** | **PASS**（与任务钉一致） |
| RESTORED | 未恢复 `aa25e989` / `7e239487` 等；仅 `_consumed` | **PASS** |
| JSON 旗标 | `x2_accept=false` `book_smoke=false` `live=false` `promotion_approved=false` | **PASS** |
| peak_rss | ru_maxrss=**1027.0** MB ≪ 1500 | 过程 OK（本审不重跑） |
| 构建 ACCEPT | `1c992d62` 仍成立；本审**不回撤** | 分层保留 |

## 2. 闸门数字复核（自 JSON；勿盲信任务声称）

### 2.1 portfolio_gates.verdict

| 门 | JSON | 复核 |
|---|---|---|
| A | **true** | 60w A=true ∧ 100w A=true → 总 **true** |
| B | **false** | 60w B=false ∧ 100w B=true → 总 **false** |
| current | **false** | 60w=false ∧ 100w=false → 总 **false** |

### 2.2 分档 overlay / capacity / A_debeta（净；引擎 T+1 next_open）

| 档 | 口径 | CAGR | MDD | Calmar |
|---|---|---|---|---|
| 60万 | capacity | 17.85% | −14.24% | 1.254 |
| 60万 | **overlay** | **16.22%** | **−15.09%** | **1.075** |
| 60万 | A_debeta | 18.13% | −12.58% | 1.441 |
| 100万 | capacity | 18.30% | −12.47% | 1.468 |
| 100万 | **overlay** | **18.16%** | **−11.49%** | **1.581** |
| 100万 | A_debeta | 18.56% | −11.13% | 1.667 |

（JSON 精确：60w overlay cagr=`0.162199…` mdd=`-0.150852…` calmar=`1.07521…`；100w overlay cagr=`0.181622…` mdd=`-0.114881…` calmar=`1.58096…`。）

### 2.3 cost

| 项 | 值 |
|---|---|
| net_cagr | **≈12.84%**（`0.128444…`） |
| bench_cagr | **≈11.26%**（`0.112592…`） |
| gross_cagr | ≈14.54% |
| cost_drag_ann | ≈1.50% |
| to_2s_mean | ≈0.035 |
| untradable | **false** |

与任务声称 **MATCH**。

## 3. decay 含义（对照 `ALPHA_DECAY_GATE_PREREG_ZH.md` / v1.1）

| 项 | JSON 实数 | 规则含义 |
|---|---|---|
| outcome | **DECAY_DOWNGRADE** | v1：最新 α&lt;0 **或** 季 α 连降 3 **或** H1/H2 任一失败 |
| reasons | `['latest_alpha<0', 'H2_net_cagr<=510300']` | 双触发 |
| latest_resid_alpha | **−0.02102**（年化残差 α） | **&lt;0** → 硬触发 DOWNGRADE |
| H2 | net_cagr≈**−6.56%** vs bench_net_cagr≈**−3.37%** | 窗内净 CAGR **未优于** 510300 → H2 失败 |
| H1 换手 | turnover_mean_2s≈0.0346 | **未**触发（&lt;20%） |
| consecutive_declines | 1 | **未**触连降 3 |
| quarterly_alpha 近端 | 2026-06-30=−0.0314；2026-09-30=−0.0155；2026-10-09=−0.021 | 近端转负（佐证 latest&lt;0；非单独第三触发） |
| window | 2024-06-04→2026-10-09（569 日） | short_history=false |
| prereg_sha256 | `eecc84ba…` | 与衰减预注册钉一致路径 |

**过程含义**：残差 α 最新点为负，且同窗净收益跑输 510300 → 衰减闸 **只降不升** 语义下标 DOWNGRADE；对照验收清单 §3.4 / §4.3：**必须 KEEP** 才可请 Eng → 本叶 **不满足**。

## 4. 与门A / 门B / 现行对照

对照 `ALPHA_GATE_AB_PREREG_20261014_ZH.md` + `GATE_V3_MDD25_PREREG_ZH.md` + `ALPHA_HILIQ_GATEV3_ACCEPT_CHECKLIST_ZH.md`：

### 4.1 门A（去β再叠；研究口径）

- 定义：卫星先去β再 80/20；两档 CAGR 与 MDD 都优于 capacity。
- 结果：**A=true**（60w/100w A_debeta CAGR·MDD 均优于同档 capacity）。
- 边界：预注册写明门A 在 60/100万 **实盘不可行**（IF 一手名义远大于卫星对冲名义）→ **仅为研究口径**。
- **硬句**：**A=true 不解阻 X2 ACCEPT**；不构成晋级 / 不构成 Book-Smoke 授权。

### 4.2 门B（不去β叠）

- 定义：两档 Calmar 都优于 capacity，且 MDD **不深于 −15%**。
- **60万失败原因**（足以总 B=false）：
  1. overlay MDD≈**−15.085%** **深于** −15% 硬线；
  2. overlay Calmar≈**1.075** **未**优于 capacity Calmar≈**1.254**。
- 100万：overlay Calmar≈1.581 &gt; capacity≈1.468，且 MDD≈−11.49% 不深于 −15% → 单档 B=true。
- 总裁决须两档皆过 → **B=false**。

### 4.3 现行 / GATE_V3 本地

- 现行门（AB 预注册）：两档 CAGR 与 MDD 都优于 capacity，且 MDD 不深于 −25%。
  - 60万：overlay CAGR 16.22% **&lt;** capacity 17.85%；MDD 更深 → fail。
  - 100万：overlay CAGR 18.16% **&lt;** capacity 18.30% → fail。
  - → **current=false**（与 JSON 一致；MDD 虽未破 −25%，但「优于 capacity」未满足）。
- GATE_V3 清单四条：MDD≤25%（本 overlay 两档满足）∧ 净 CAGR 严格高于 HI_LIQ capacity（**本叶未满足**）∧ 衰减=**KEEP**（**本叶 DOWNGRADE**）∧ 可交易（换手过程 OK）。
- → **GATE_V3 本地 FAIL**；清单 §6：**不派烟给「衰减非 KEEP / GATE_V3 本地 FAIL」的叶**。

## 5. 披露边界

| 可披露 | 不可宣称 |
|---|---|
| selfcheck 入口数字（上表 CAGR/MDD/Calmar/cost/decay） | **X2 ACCEPT** / 晋级 / 纸面 |
| 门A=true（研究口径） | 门A 解阻实盘或 X2 |
| 构建过程 ACCEPT（`1c992d62`）仍成立 | 收益过程 / 组合门过闸 |
| HOLD + Book-Smoke=否 | Alpha 自开烟 / 恢复 `_consumed` `.ok` |

附注：JSON `pin_gap.gap_fields` 仍列 ic/icir/walk_forward；evaluate 产出为 decay/cost/portfolio_gates，**未见**独立 IC/ICIR/WF 字段。本审以组合闸+衰减为准；**不**据此单独 REJECT（非钉假/作弊），亦不宣称 IC 过闸。

## 6. 下一步（给主；Alpha 不执行）

1. **维持 HOLD**；**不建议**令 Eng Book-Smoke（除非主明示豁免衰减/清单例外——本审不假设）。
2. 若续研：衰减修复（近端残差 α 转正 + H2 净 CAGR 优于 510300）或另窗重评至 **KEEP** 后，再议组合闸；门B 须先解决 60万 overlay MDD 破 −15% 与 Calmar 劣于 capacity。
3. **禁止**：签.ok；开跑；RESTORED `aa25e989`；自开 Book-Smoke；宣布 X2 ACCEPT；改 FROZEN_CONFIG/paper/alpha_labels；报 Leo。
4. 叶25/27：仍等候既有线（本审不改其状态）。

---

**VERDICT=HOLD** · Book-Smoke 建议=**否** · ≠X2 ACCEPT · live=false · leo_notify=false
