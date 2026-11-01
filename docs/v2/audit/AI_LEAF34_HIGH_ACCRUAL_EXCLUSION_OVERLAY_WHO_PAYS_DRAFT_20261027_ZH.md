# 【DRAFT — NOT FROZEN】叶34 who_pays：HI_LIQ 高应计剔除 overlay（主干负向过滤）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 09:42 ET（America/New_York；ISO `2026-10-27T09:42:00-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER + **轻量计数闸**；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向/阈值；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁**完整 α 长跑。
- 叶号意向：**叶34**（台账下一空号；叶28/29 仍 FROZEN 另队；叶26 GAP **不交审**；叶23/24 另轨不复开；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR / 叶31 Amihud / 叶32 `MARGIN_NET_FLOW_RESID` / 叶33 `SHARE_UNLOCK_PRESSURE_RESID` 已占轴）。
- 主令上下文：dig `cfd83e85` MATCH（`DIG_FACTOR_20261027_0934ET.md`）；叶33 HOLD **CLOSED**（Arch `30efc8ed`；`.ok` `81521fb5` CONSUMED；lift `ee5235e6`；ratio med=0.3365≪0.5；正式 `afbbe7e7` UNCHANGED）。live `.ok`=0 / QUIET ABSENT。叶32 HOLD `45dd87dc` / 叶31 `7ef5aa11` / 叶30 `f00536b9` **不回撤**。本票 = 工厂续挖新叶（dig 优先序 **(1) 高应计剔除 overlay**）。
- 禁：GP / 高杠杆 / 教科书量价当主线；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；moneyflow 80/20 叠仓主轴；北向 hk_hold 换皮；margin/Amihud/解禁换皮；重开 accrual_quality / 叶19 `cfacc_rnoa` / 叶25 应计脱敏 **主叶**；把叶19/25 α 当本叶主输入；ETF 份额进本叶主信号（那是备选2）；问询函进本叶主信号（备选3）；复跑叶30–33 selfcheck/X2；禁改正式叶33 `afbbe7e7`；RESTORED/`forbid` **二十票齐 + `245df63f`+`c5ed13df`+`5774bb6e`**（点名见 §11）；申 `.ok`；挂/抬 QUIET；抬 RSS；`0087c928`（叶30 KEEP 修复）另队不夹带。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；`EXECUTED_full_alpha=false`；**≠X2 ACCEPT**；`leo_notify=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_high_accrual_exclusion_overlay_v1`（叶34 意向）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 内忽视应计质量恶化、仍给高应计名足额权重的持仓者——高应计剔除/降权后，主干少踩应计反转与质量踩雷。  
> **可检验预测**：交付形态 **A（推荐）** = 日度 exclusion mask / soft-penalty 向量（高应计名 `α_overlay≤0` 或 `mask=0`），供优化器/主干叠加；**不是**完整截面应计多空排序复刻叶19/25。判定路径：叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干。活跃集 vs 叶19/25 Jaccard ≪0.7（**≥0.7 硬拒**）；ρ_excess>0.5 **只算强度过滤**；另披露 vs 叶27/30/31/32/33。覆盖 HI_LIQ 再平衡日可算 overlay 有效名 median≥300（本拍轻量计数已估，见 COUNT RECEIPT）。  
> **失效条件**：退化为叶19/25 完整 CFACC 多空主叶或 accrual_quality TopN 长端复开；或与叶19/25 Jaccard≥0.7；或主信号混入卖方/金股/TP/LLM/ETF份额/问询函；或冻结后事后改 top_q / 翻转剔除方向读收益；或用 `available_at > t` 偷看；或把本 overlay 伪称「全新会计 α」掩盖与应计族相关。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT + 轻量计数闸。

---

## 1. 选型理由（PRIMARY = 高应计剔除 overlay，非应计主叶复开）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| 叶19 `cfacc_rnoa` | CFACC TTM + RNOA 残差 **完整 α 排序** | 本叶交付=**负向过滤 overlay**（mask/soft-penalty）；**不**输出完整截面多空 α 复刻叶19 |
| 叶25 `cfacc_desens_cs` | CFACC TTM 脱敏截面残差 **全因子** | 同族禁复开主叶；本叶**不**重建 leaf25 α；仅剔除高应计尾部 |
| accrual_quality `g1g5_ashare_accrual_quality_v1` | BS WC 应计/资产 → TopN 低应计长端 | **不是**重开该主叶；无 TopN EW 长端，只作主干叠加的 exclusion |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化率主 α | 本叶用单期 CF-accrual **水平**做剔除阈值，**不是**多季转化率主轴 |
| 叶27 overnight−intraday idio | `on_minus_id` 残差 σ | 本叶主轴=应计质量剔除，**零**隔夜−日内 |
| 叶31 Amihud 冲击慢 | `\|r\|/amount` | 本叶**不**读冲击 |
| 叶32 `MARGIN_NET_FLOW_RESID` | 两融净流入残差 | 本叶**不**读两融 |
| 叶33 `SHARE_UNLOCK_PRESSURE_RESID` | 限售解禁压力残差 | 本叶**不**读解禁/float_share；叶33 HOLD CLOSED 不回撤 |
| 叶26 GAP ETF 流 | 产品层份额 | 备选(2) 另写；**禁** ETF 份额进本叶主信号 |
| 叶28 LLM / 叶29 tech_crowd | 另队 FROZEN | **不夹带、不升 PRIMARY** |
| 北向 / moneyflow | 资金流换皮 | 本叶升格=应计剔除 overlay；**不**读 hk_hold / moneyflow |

**PRIMARY 选定**：**HI_LIQ 高应计剔除 overlay**（dig 优先序 1）。  
**备选（§12，不升 PRIMARY）**：(2) ETF 申赎→成分被动压力；(3) 问询函/复合排雷剔除。

---

## 2. 机制（高应计剔除；交付形态 A）

在 HI_LIQ 池、财务 PIT 上定义 **CF-accrual 代理**（DRAFT 默认；冻结时写死）：

对每个再平衡日 \(t\)，取 as-of 有效的 OCF/净利润：

\[
\mathrm{accrual\_cf}_{i,t} = 1 - \mathrm{ocf\_to\_profit}_{i,t}
\quad\text{（等价于 }(\mathrm{NP}-\mathrm{OCF})/\mathrm{NP}\text{ 当 }\mathrm{NP}>0\text{）}
\]

有效行纪律（与计数闸一致，冻结可加严）：

- `ocf_to_profit` 有限；`denom_small=false`；`net_profit>0`；`np_negative=false`
- PIT：底层 `available_at` / `e_available_at ≤ t`（日表已 as-of 展开；禁偷看）

**剔除规则（DRAFT 冻结意向，不读收益选阈值）**：

\[
\mathcal{H}_{t} = \{i\in\mathrm{HI\_LIQ}_t:\; \mathrm{accrual\_cf}_{i,t} \ge Q_{1-q}(\mathrm{accrual\_cf}_{\cdot,t})\}
\quad q=0.20
\]

**交付形态 A（推荐）**：

- **exclusion mask**：\(\mathrm{mask}_{i,t}=0\) if \(i\in\mathcal{H}_t\) else \(1\)（仅对可算名；不可算名 → 不进 overlay 有效集，**不填假 0 分**）
- **soft-penalty 向量（可选并行钉）**：\(\alpha_{\mathrm{overlay},i,t} = -\mathbf{1}[i\in\mathcal{H}_t]\) 或连续分位惩罚（若用连续分 **须** SW+style 残差；分位阈值仍冻结 top 20%，**不**读收益选）

**与叶19/25/accrual_quality 公式差异（硬写）**：

| 叶 | 公式核 | 交付 |
|---|---|---|
| 叶19 | CFACC TTM + RNOA 残差排序 | 完整日度 α |
| 叶25 | CFACC TTM desensitize + 截面残差 | 完整日度 α |
| accrual_quality | BS `WC_ACC/TA`→SW+市值残差；低应计 TopN | 完整权重腿 |
| **叶34（本）** | `1−OCF/NP` 水平 → **top 20% 剔除** | **mask / soft-penalty overlay** |

可选冻结升级（非本拍计数路径）：改用 BS `WC_ACC/TA`（Sloan 风格，同 accrual_quality 分子但 **仍只做剔除**）——须另证 vs 叶19/25 Jaccard，并重跑计数闸。

- 再平衡建议每 **20** 交易日（慢；对齐叶19/30/31/32/33）。
- **符号/阈值纪律**：DRAFT 默认「高应计=剔除/惩罚」；`q=0.20` **冻结时写死**；本 DRAFT **不**读收益选号。

---

## 3. 残差规格（overlay；缺则记 GAP）

1. **主路径（形态 A mask）**：截面分位阈值剔除，**可不**做全残差（mask 已是池内相对）。  
2. **若用连续 soft-penalty 分**：同日 HI_LIQ 掩码后须 **SW L1 demean + vs log 流通市值 OLS + style（mom20/vol20/logADV20）**；缺列 → PIN_GAP。  
3. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 / 叶31 / 叶32 / 叶33 α 的 **Jaccard** 与 **ρ_excess**。  
4. **禁**把叶19/25 α、叶30 CRR 主轴、两融/Amihud/解禁/hk_hold/moneyflow/ETF份额/问询函当本叶主输入。

---

## 4. 数据 PIT（本拍 schema/路径 + 轻量计数；禁完整 α 长跑）

| # | 输入 | 备注 |
|---|---|---|
| 1 | OCF/利润 PIT 日表（计数主路径） | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`；**9,754,991** 行；列含 `trade_date, instrument_id, ts_code, n_cashflow_act, net_profit, ocf_to_profit, denom_small, np_negative, e_available_at, period_basis`；sha8 `f9faf7e7` |
| 2 | OCF/利润 PIT 季表（对照） | `ocf_to_profit_pit_tushare.parquet`；228,450 行；含 `available_at` |
| 3 | 现金流 PIT | `cashflow_pit_tushare.parquet`；315,718 行；`n_cashflow_act, net_profit, available_at` |
| 4 | 资产负债表 PIT（冻结可选 BS 路径） | `balancesheet_pit_tushare.parquet`；451,857 行；含 `total_assets` 与营运资本字段；`available_at` |
| 5 | bs_cf 合并 PIT | `bs_cf_pit_tushare.parquet`；558,358 行 |
| 6 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（同叶31/32/33；sha8 `c5433e80`） |
| 7 | SW L1 / style / 市值 | 连续分路径才强制；mask 主路径可后钉 |
| 8 | 叶19/25 α parquet | **仅** Jaccard/ρ；不进主信号；叶19 sha8 `16202b2e`；叶25 sha8 `8be12024` |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造**。本拍计数 = APPROX（CF proxy，非完整 BS WC）；见 COUNT RECEIPT。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主**；FULLA 研究对照意向（预注册双钉，PRIMARY=HI_LIQ） |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09** |
| 再平衡 | DRAFT **20** 交易日 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 exclusion mask / soft-penalty 向量** → 优化器/主干叠加；非 Top-N 主叶 |
| 判定 | 叶自身主干级 **或** ρ_excess vs capacity_adv <0.5 且 60万/100万叠加均优于主干 |
| rss 意向 | **1500** MB 禁抬；peak_proof REQUIRED（脚本阶段再钉） |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. 交付形态 A：mask 与/或 soft-penalty；连续分则 SW+style。  
2. `q=0.20` 与「高应计=剔除」符号冻结写死；**禁**读收益改阈值。  
3. HI_LIQ 判决为主。  
4. walk-forward 分段披露。  
5. Gate B / GATE_V3；衰减门 v1.1。  
6. **decay KEEP** 硬验收（§7）；组合闸过关路径可检验。  
7. Jaccard/ρ 硬拒意向 vs 叶19/25（§8）+ 披露 27/30/31/32/33。

---

## 7. decay KEEP 设计（盯近端；对齐叶30/31/32 HOLD 教训）

叶30/31 HOLD 含 DECAY_DOWNGRADE；叶32 HOLD `45dd87dc` 则 decay=KEEP 但仍门 A/B/current 总 false——**KEEP 不解阻** X2 ACCEPT。本叶同时盯 KEEP 与组合闸：

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（若以叠加超额评价；衰减门 v1.1） |
| 连降 | **非连降 5 季** |
| H2 净 CAGR | **H2_net_cagr > 510300** |
| KEEP 合取 | `latest_resid_α>0 ∧ 非连降5季 ∧ H2_net_cagr>510300`；否则 **DOWNGRADE** |
| 组合闸路径（意图） | overlay 降换手噪声（剔质量踩雷）+ 慢再平衡 → **意图**改善可交易性/叠加稳定性；**勿宣称已过闸** |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；不派 Book-Smoke；≠X2 ACCEPT |

---

## 8. 正交硬闸

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → 强度过滤（披露） |
| 叶27 | 同上；禁 `on_minus_id` 主输入 |
| 叶30 CRR | 同上；禁把多季 CRR 主轴当本叶主信号（允许同族数据源，交付必须是剔除 overlay） |
| 叶31 Amihud | 同上；禁冲击主输入 |
| 叶32 两融 | 同上；禁两融主输入 |
| 叶33 解禁 | 同上；禁 float_share 解禁主输入 |
| 北向 / moneyflow | 披露；建议 Jaccard≥0.7 同硬拒精神 |
| 覆盖 | HI_LIQ 再平衡日可算 overlay 有效名 **median≥300**；`zero_frac≤0.05` |
| 换手/成本 | 成本 30bp；冻结后评价 |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

**本拍轻量计数（摘要）**：masked_median=**2431.0**；zero_frac=**0.0**；J20_max vs 叶19/25=**≈0.053**；ρ_mean≈**0.37**（未触强度过滤）；**gate_pass=true**（APPROX）。详见 COUNT RECEIPT。

---

## 9. 失败截断

- 计数闸 median<300 或 zero_frac>0.05 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs 叶19/25 → 硬拒；RECEIPT 可建议改升备选(2)/(3)，**不擅自改 PRIMARY who_pays**
- 冻结前读收益选方向/q/λ → 违规作废
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT（未来执行窗）
- 误读叶19/25 α 当主输入 / 偷看 future available_at / 复开 accrual_quality 主叶 → 废叶

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER + COUNT | 本文件 + COVER + COUNT RECEIPT + JSON；**ok_requested=false** |
| 主排号 | 请主确认叶号=34 并登记台账意向行 |
| Arch | **只审不签**（文档契约）；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED `245df63f`+`c5ed13df`+`5774bb6e`+二十票；禁复用叶25/27/30–33 `.ok` |
| 叶26 | **不交审** |
| 叶28/29 / `0087c928` | **另队**不夹带 |
| 叶30/31/32/33 | HOLD/CLOSED 不回撤；禁改叶33 正式 `afbbe7e7` |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- 重开 accrual_quality / 叶19 / 叶25 应计主叶；叶19/25 α 当主输入
- ETF 份额 / 问询函当本叶主信号（备选另节）
- moneyflow 80/20；hk_hold / margin / Amihud / 解禁换皮
- 禁改叶33 正式脚本 sha `afbbe7e7`
- `0087c928` 另队不夹带
- **RESTORED / forbid**：`245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
  - 主令点名新增：`245df63f`, `c5ed13df`, `5774bb6e`
  - 二十票全集：`02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74`
- 推 Leo；`live=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）

| 备选 | 说明 |
|---|---|
| （2）ETF 申赎→成分被动压力 | `data/v2/etf/share_pit/` 份额流×权重；vs moneyflow_resid/叶26 同构闸；叶26 GAP 不交审；**本票不升** |
| （3）问询函/复合排雷剔除 | `data/v2/events/announcements_classified_pit.parquet`；vs negevent Jaccard；先 HI_LIQ 计数；**本票不升** |

若 COUNT 对 PRIMARY 显著 FAIL，仅在 RECEIPT/就绪摘要建议是否改升 (2)/(3)，**不改写本节 PRIMARY**。

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COVER_DRAFT_20261027_ZH.md` |
| COUNT | `docs/v2/audit/AI_LEAF34_HIGH_ACCRUAL_EXCLUSION_OVERLAY_COUNT_GATE_RECEIPT_20261027_ZH.md` |
| JSON | `output/ai_factory/leaf34_high_accrual_exclusion_count_20261027.json` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_high_accrual_exclusion_overlay_v1` |
| PRIMARY | HI_LIQ 高应计剔除 overlay（形态 A） |
| 上下文钉 | dig `cfd83e85`；叶33 CLOSED Arch `30efc8ed` / `.ok` `81521fb5` / lift `ee5235e6` / 正式 `afbbe7e7`；叶32 HOLD `45dd87dc`；叶31 `7ef5aa11`；叶30 `f00536b9` |
| forbid | `245df63f+c5ed13df+5774bb6e+02426b73+4bb141c9+fdbaa512+aa25e989+7e239487+5af20222+5ae077fa+3c297052+e107383f+2be59acd+a7d98ac9+8e51de63+3a6caa4f+8bcd79dc+725be3e0+0f50daf7+3c19dd7d+1c32ab1e+6054b3bf+6de02e74` |
| gate_pass（轻量） | **true**（APPROX；见 COUNT） |
| live / promotion / ok_requested / EXECUTED_full_alpha | false / false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
