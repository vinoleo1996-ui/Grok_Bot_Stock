# 【DRAFT — NOT FROZEN】叶35 who_pays：ETF 申赎→成分股被动资金压力 overlay（主干叠加）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 12:42 ET（America/New_York；ISO `2026-10-27T12:42:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向/阈值；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑。
- 叶号意向：**叶35**（台账下一空号；叶28/29 仍 FROZEN 另队；叶26 BROAD_ETF_FLOW **DRAFT 另队勿重开同构**；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud / 叶32 `MARGIN_NET_FLOW_RESID` / 叶33 `SHARE_UNLOCK_PRESSURE_RESID` / 叶34 `HIGH_ACCRUAL_EXCLUSION_OVERLAY` 已占轴）。
- 主令上下文：dig 文内钉 `814e8a68` / 磁盘现算 sha8 `7f1e2bb4`（`DIG_FACTOR_20261027_1235ET.md`）；叶34 X2 selfcheck **HOLD CLOSED**（`.ok` `178e90e9` CONSUMED；lift `3fce510e`；回执 `a37257b9`；Gate A/B/current 全 false；ρ_excess≈0.960841≫0.5；60万/100万叠加未优于主干；decay=KEEP 不解阻；≠X2 ACCEPT）。live `.ok`=0 / QUIET ABSENT。叶33/32 HOLD 不回撤；正式叶33 `afbbe7e7` UNCHANGED。本票 = 工厂续挖新叶（dig 优先序 **(1) ETF 申赎→成分被动压力**）。
- 禁：GP / 高杠杆 / 教科书量价当主线；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮；margin/Amihud/解禁/应计换皮；**重开叶26 完整多层残差 α 主叶同构**；交易行业 ETF 本身（叶4/8a）；把个股 moneyflow 当主信号；复跑叶30–34 selfcheck/X2；禁改正式叶33 `afbbe7e7`；RESTORED/`forbid` 见 §11；申 `.ok`；挂/抬 QUIET；抬 RSS；`0087c928`（叶30 KEEP 修复）/叶28/29 另队不夹带。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_etf_passive_flow_pressure_overlay_v1`（叶35 意向）  
> **who_pays（一句）**：付钱的是在宽基 ETF 大额申赎日、忽视「产品层份额变化→篮子权重」机械冲击、仍给高被动压力名足额权重的持仓者——压力 overlay 降权/剔除后，主干少踩 AP 篮子冲击。  
> **可检验预测**：交付形态 **A（推荐）** = 日度高 `|pressure|` 尾部 soft-penalty / exclusion-tilt 向量（`α_overlay≤0` 或 `mask` 降权），**叠主干**；**不是**叶26 式完整 A/A′ 多层残差 α 主叶；**不是**交易 ETF 本身。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃集 vs moneyflow_resid Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；vs 叶26 残差 α（若日后落盘）同硬拒精神；vs 叶8a 披露（本拍 GAP）。覆盖 HI_LIQ 再平衡日可映射压力名 median≥300（本拍轻量计数已估，见 COUNT RECEIPT）。  
> **失效条件**：退化为叶26 `g1g5_ashare_broad_etf_flow_stock_v1` 完整残差 α 主叶；或与 moneyflow_resid Jaccard≥0.7；或主信号混入个股 D2 moneyflow / 行业 ETF 持仓路径 / 卖方/金股/TP/LLM；或冻结后事后改 top_q / 翻转剔除方向读收益；或用未来权重/`available_at > t` 偷看；或把本 overlay 伪称「全新 ETF α」掩盖与叶26 raw 压力同幅。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 轻量计数闸。

---

## 1. 选型理由（PRIMARY = ETF 被动压力 overlay，反叶26 同构）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| **叶26** `g1g5_ashare_broad_etf_flow_stock_v1` | 宽基流量→**完整多层残差 α 向量主叶**（DRAFT 另队） | **反同构硬写**：本叶 = **形态 A 被动压力 overlay**（高 `|pressure|` 尾部 soft-penalty / exclusion-tilt **叠主干**）；**不是**完整 A/A′ 残差 α 主叶；**不得**重开叶26 同构 |
| 叶8a `ind_etf_flow_rev` | 行业 ETF 申赎极值反转（**FAIL 同构**；交易 ETF 本身） | 本叶评分对象=**股票暴露 overlay**；禁行业 ETF 持仓路径作主轴 |
| 叶4 industry_etf_rotation | 持有行业 ETF | 本叶**不**交易 ETF |
| moneyflow_resid | 个股主力净流入残差权重 | 本叶主轴=ETF **产品层**份额×权重；个股 moneyflow **禁**进主信号（仅正交披露） |
| 叶34 高应计剔除 overlay | `1−OCF/NP` 尾部剔除 | 本叶**不**读财务应计；叶34 HOLD CLOSED 不回撤 |
| 叶33 解禁压力残差 | float unlock | 本叶**不**读解禁；叶33 HOLD 不回撤 |
| 叶32 两融 / 叶31 Amihud / 叶30 CRR / 叶27 on−id / 叶25 cfacc | 各已占 | 本叶主轴=ETF 被动压力 overlay；零两融/冲击/CRR/隔夜/应计 |
| 叶28 LLM / 叶29 tech_crowd | 另队 FROZEN | **不夹带、不升 PRIMARY** |

**PRIMARY 选定**：**ETF 申赎→成分股被动资金压力 overlay**（dig 优先序 1；数据硬缺口未触发）。  
**备选（§12，不升 PRIMARY）**：问询函/复合排雷剔除 overlay。

---

## 2. 机制（被动压力 overlay；交付形态 A）

在 HI_LIQ 池、ETF 份额 PIT + 指数权重 as-of 上定义 **个股被动资金压力**：

对每个再平衡日 \(t\)，宽基三件套映射：

| ETF | 指数 |
|---|---|
| `510300.SH` | `000300.SH` |
| `510500.SH` | `000905.SH` |
| `512100.SH` | `000852.SH` |

\[
\mathrm{pressure}_{i,t} = \sum_{e\in\mathcal{E}} w(i,\mathrm{index}(e),\mathrm{asof}(t)) \times z_{e,t}
\]

其中 \(z_{e,t}\) = 当日 PIT 可得的 `flow_est_wan_yuan`（缺则回退 `d_share_wan`）；`available_at ≤ t` 纪律（份额表有 `available_at`）。  
权重表 `index_weight_csi300_500_1000` **无 `available_at`** → 本 DRAFT 用月末 `trade_date` **向后 asof**（**APPROX**；对齐叶26 Data GAP 笔记；冻结前可升级方案 A「次月首日 09:00 SH」）。

**剔除 / 惩罚规则（DRAFT 冻结意向，不读收益选阈值）**：

\[
\mathcal{H}_{t} = \{i\in\mathrm{HI\_LIQ}_t\cap\mathrm{mappable}_t:\; |\mathrm{pressure}_{i,t}| \ge Q_{1-q}(|\mathrm{pressure}|_{\cdot,t})\}
\quad q=0.20
\]

**交付形态 A（推荐）**：

- **exclusion / soft-penalty**：\(i\in\mathcal{H}_t\) → `mask` 降权或 \(\alpha_{\mathrm{overlay},i,t} = -|\mathrm{pressure}_{i,t}|\) 分位惩罚（连续分 **须** SW+style 残差；阈值仍冻结 top 20% `|pressure|`，**不**读收益选）
- **叠主干**；不可映射名 → 不进 overlay 有效集，**不填假 0 分**

**与叶26 / 叶8a / moneyflow 公式差异（硬写）**：

| 叶 | 公式核 | 交付 |
|---|---|---|
| 叶26 | 同族 raw 压力 → SW demean + vs log 市值 + vs β + vs capacity_adv **多层残差** | **完整日度 α 主叶** |
| 叶8a | 行业 ETF `flow_est` 极值反转 | **交易行业 ETF**（FAIL） |
| moneyflow_resid | 个股 `net_mf_amount` 残差 | 权重腿 / α |
| **叶35（本）** | 同族 raw 压力水平 → **top 20% `|pressure|` 剔除/惩罚** | **mask / soft-penalty overlay 叠主干** |

- 再平衡建议每 **20** 交易日（慢；对齐近叶）。
- **符号/阈值纪律**：DRAFT 默认「高绝对被动压力=剔除/惩罚」；`q=0.20` **冻结时写死**；本 DRAFT **不**读收益选号。
- **行业 ETF 持仓路径禁作主轴**（仅宽基三件套）。

---

## 3. 残差规格（overlay；缺则记 GAP）

1. **主路径（形态 A mask / soft-penalty）**：截面 `|pressure|` 分位阈值剔除/惩罚，**可不**做叶26 式全残差（overlay 已是池内相对尾部）。  
2. **若用连续 soft-penalty 分**：同日 HI_LIQ 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP。  
3. 披露 vs moneyflow_resid / 叶26 残差 α（若有）/ 叶8a / 叶25/27/30–34 的 **Jaccard** 与 **ρ_excess**。  
4. **禁**把个股 moneyflow、叶26 完整残差 α、行业 ETF 持仓、两融/Amihud/解禁/应计/hk_hold 当本叶主输入。

---

## 4. 数据 PIT（本拍 schema/路径 + 轻量计数；禁完整 α 长跑）

| # | 输入 | 备注 |
|---|---|---|
| 1 | 宽基份额流主表 | `data/v2/etf/share_pit/etf_share_flow_pit_major.parquet`；列含 `ts_code,trade_date,d_share_wan,flow_est_wan_yuan,*_available_at,available_at`；含 510300/510500/512100 等；sha8 `a3eac35b` |
| 2 | 全样本份额流（校验） | `etf_share_flow_pit_all.parquet`；本拍计数未强制 |
| 3 | 指数成分权重 | `data/v2/index_members/index_weight_csi300_500_1000.parquet`；`index_code,con_code,trade_date,weight`；仅 000300/000905/000852；**月末点**；**无 available_at** → **APPROX**；sha8 `d543a485` |
| 4 | ETF↔指数映射 | 叶26 DRAFT 硬编码三件套（见上表）；`docs/v2/audit/leaf26_20261026/DATA_LEAF26_BROAD_ETF_INDEX_MAP_DRAFT.csv` 只读对照 |
| 5 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`；sha8 `c5433e80` |
| 6 | moneyflow_resid 权重（仅正交） | `output/ai_factory/g1g5_moneyflow_resid_daily_weights_20261013_050716.parquet`；sha8 `dd6da010`；**不进主信号** |
| 7 | 叶26 残差 α | **ABSENT** → Jaccard **GAP**（不得伪造）；仅重建 leaf26-like raw 作披露 |
| 8 | 叶8a 股票 α | **ABSENT**（FAIL / 交易 ETF）→ Jaccard **GAP** |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造**。本拍计数 = APPROX（权重无 PIT `available_at`）；见 COUNT RECEIPT。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主**；FULLA 研究对照意向（预注册双钉，PRIMARY=HI_LIQ） |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | DRAFT **20** 交易日 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 soft-penalty / exclusion-tilt overlay** → 优化器/主干叠加；非 Top-N 主叶；非叶26 完整 α |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| rss 意向 | **1500** MB 禁抬；peak_proof REQUIRED（脚本阶段再钉） |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. 交付形态 A：mask 与/或 soft-penalty；连续分则 SW+style。  
2. `q=0.20` 与「高 `|pressure|`=剔除/惩罚」符号冻结写死；**禁**读收益改阈值。  
3. 宽基三件套映射冻结；行业 ETF 禁主轴。  
4. HI_LIQ 判决为主。  
5. 权重 PIT 规则（APPROX→方案 A/B）冻结前共签。  
6. walk-forward 分段披露。  
7. Gate B / GATE_V3；衰减门 v1.1。  
8. **decay KEEP** 硬验收（§7）。  
9. Jaccard/ρ 硬拒意向 vs moneyflow_resid / 叶26 残差 α（§8）+ 披露 8a/25/27/30–34。

---

## 7. decay KEEP 设计（盯近端；对齐叶30–34 HOLD 教训）

叶30/31 HOLD 含 DECAY_DOWNGRADE；叶32/34 decay=KEEP 但仍门 A/B/current 总 false——**KEEP 不解阻** X2 ACCEPT。本叶同时盯 KEEP 与组合闸：

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（若以叠加超额评价；衰减门 v1.1） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **H2_net_cagr > 510300** |
| KEEP 合取 | `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；否则 **DOWNGRADE** |
| 组合闸路径（意图） | overlay 降被动冲击噪声 + 慢再平衡 → **意图**改善可交易性/叠加稳定性；**勿宣称已过闸** |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；不派 Book-Smoke；≠X2 ACCEPT |

---

## 8. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| moneyflow_resid | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → 强度过滤（披露）；禁个股 moneyflow 主输入 |
| 叶26 BROAD_ETF_FLOW | **禁**重开完整残差 α 主叶同构；残差 α 落盘后 Jaccard≥0.7 硬拒；本拍残差 α **GAP**（raw 同幅属 APPROX 披露，反同构靠交付形态 A） |
| 叶8a ind_etf_flow_rev | 禁交易行业 ETF；股票 Jaccard 本拍 **GAP** |
| 叶25 / 27 / 30–34 | 披露 Jaccard/ρ（X2 阶段可补）；禁各自主轴换皮 |
| 覆盖 | HI_LIQ 再平衡日可映射压力名 **median≥300**；`zero_frac≤0.05` |
| 换手/成本 | 成本 30bp；冻结后评价 |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

**本拍轻量计数（摘要）**：masked_median=**1552.5**；zero_frac=**0.0**；J20_max vs moneyflow_resid=**0.25**；ρ_mean≈**−0.080**（未触强度过滤）；叶26 残差 α **GAP**；叶8a **GAP**；**gate_pass=true**（APPROX）。详见 COUNT RECEIPT。

---

## 9. 失败截断

- 计数闸 median<300 或 zero_frac>0.05 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs moneyflow_resid → 硬拒；RECEIPT 可建议改升备选问询函，**不擅自改 PRIMARY who_pays**
- 退化为叶26 完整残差 α 主叶 → 废叶
- 冻结前读收益选方向/q/λ → 违规作废
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT（未来执行窗）
- 误读个股 moneyflow / 行业 ETF 持仓当主输入 / 偷看 future 权重 → 废叶

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER + COUNT | 本文件 + COVER + COUNT RECEIPT + JSON；**ok_requested=false** |
| 主排号 | 请主确认叶号=35 并登记台账意向行 |
| Arch | **只审不签**（文档契约）；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED（§11）；禁复用叶25/27/30–34 `.ok` |
| 叶26 | **另队 DRAFT**；本叶只反同构 overlay，**不**代跑叶26 |
| 叶28/29 / `0087c928` | **另队**不夹带 |
| 叶30/31/32/33/34 | HOLD/CLOSED 不回撤；禁改叶33 正式 `afbbe7e7` |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- 重开叶26 完整残差 α 主叶同构；交易行业 ETF（叶4/8a）
- 个股 moneyflow / hk_hold / margin / Amihud / 解禁 / 应计换皮进主信号
- 禁改叶33 正式脚本 sha `afbbe7e7`
- `0087c928` / 叶28/29 另队不夹带
- **RESTORED / forbid**：`178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
  - 主令点名：`178e90e9`, `c1b71e64`, `245df63f`, `c5ed13df`, `5774bb6e`, `81521fb5`
  - 二十票全集：`02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
- 推 Leo；`live=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）

| 备选 | 说明 |
|---|---|
| （2）问询函/复合排雷剔除 | `data/v2/events/announcements_classified_pit.parquet` 财务问询/关注函，剔重组类；HI_LIQ 计数 + vs negevent Jaccard；只作剔除 overlay；**本票不升**（PRIMARY 数据齐且计数过闸） |

若 COUNT 对 PRIMARY 显著 FAIL，仅在 RECEIPT/就绪摘要建议是否改升 (2)，**不改写本节 PRIMARY**。

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf35_etf_passive_flow_pressure_count_20261027.json` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_etf_passive_flow_pressure_overlay_v1` |
| PRIMARY | ETF 申赎→成分被动压力 overlay（形态 A） |
| 上下文钉 | dig 文内 `814e8a68` / 磁盘 `7f1e2bb4`；叶34 HOLD CLOSED `.ok` `178e90e9` / lift `3fce510e` / 回执 `a37257b9`；叶33 `afbbe7e7`；叶32 HOLD `45dd87dc` |
| forbid | `178e90e9+c1b71e64+245df63f+c5ed13df+5774bb6e+81521fb5+二十票` |
| gate_pass（轻量） | **true**（APPROX；见 COUNT） |
| live / promotion / ok_requested / EXECUTED_full_alpha | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
