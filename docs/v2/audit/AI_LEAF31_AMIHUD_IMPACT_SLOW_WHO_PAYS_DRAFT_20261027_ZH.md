# 【DRAFT — NOT FROZEN】叶31 who_pays：HI_LIQ 短窗冲击成本残差（Amihud 慢 α）

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-27 02:01 ET（America/New_York；ISO `2026-10-27T02:01:19-04:00`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays + COVER 草稿；**不申请** `.ok`；**不** git commit；**不**读本叶收益选 λ/方向；**不**开全窗 X2 / selfcheck / Book-Smoke；**禁实跑**。
- 叶号意向：**叶31**（台账下一空号；叶28/29 仍 FROZEN；叶26 GAP **不交审**；叶25 `cfacc` / 叶27 overnight−intraday idio / 叶30 CRR 已占轴）。
- 主令上下文：叶30 selfcheck Alpha **HOLD** `f00536b9`（A=true 不解阻；B/current=false；**DECAY_DOWNGRADE**；不派 Eng Book-Smoke）。本票 = 工厂续挖新叶，**盯 decay KEEP**。
- 禁：GP / 高杠杆 / 教科书主线当主轴；卖方研报 / 金股 / survey / TP / 一致预期；LLM 权重当 α；复跑叶30 selfcheck；RESTORED `aa25e989`/`7e239487`/`5af20222`/`5ae077fa`；申 `.ok`；挂/抬 QUIET；抬 RSS。
- `live=false`；`promotion_approved=false`；`ok_requested=false`；**≠X2 ACCEPT**。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_amihud_impact_slow_v1`（叶31 意向）  
> **who_pays（一句）**：付钱的是在 HI_LIQ 池内按「高成交额=好流动性」定价、却忽视「短窗 |收益|/成交额（Amihud 型冲击）经 SW+style 残差后仍偏高」的交易者；高残差冲击名在再平衡后继续被过度追捧，低残差冲击名被低估为「相对便宜的流动性」。  
> **可检验预测**：残差化后的 `α_raw = −rank(impact_resid)`（符号冻结时写死；DRAFT 默认惩罚高残差冲击）对次期特质收益的截面 IC 符号在预注册**冻结时**写死（本 DRAFT **不**读收益选号）；活跃集 vs 叶19/25/27/30 Jaccard ≪0.7（**≥0.7 硬拒**，对齐叶30 count gate 精神）；ρ_excess>0.5 **只算强度过滤**；覆盖 HI_LIQ 再平衡日可算 α 名数 median≥300。  
> **失效条件**：退化为未残差 ADV/换手动量或单纯低波动；或与叶27 `on_minus_id` 特质波动近等权（Jaccard≥0.7）；或混入隔夜−日内 idio 复刻；或主信号混入卖方/金股/TP/LLM 权重；或冻结后事后翻转方向；或未做 SW+style 截面残差。  
> **交 Alpha 时点**：主排号确认→正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT。

---

## 1. 选型理由（PRIMARY = HI_LIQ 微观，非质量复开）

| 已占轴 | 机制 | 本叶为何不撞 |
|---|---|---|
| 叶19 `cfacc_rnoa` / 叶25 应计脱敏 | 会计应计+经营资产 | 本叶**零会计字段**进主信号 |
| 叶30 CRR+CFOOE vol_pen | 多季利润→OCF 转化 | 同族禁复开；本叶价量冲击 |
| 叶27 overnight−intraday idio ivol | `on_minus_id` 残差 σ | 本叶主轴是 **|r|/金额** 冲击水平残差，**不是**隔夜−日内差的二阶矩 |
| 叶18/18v overnight idio | `std(ε_on)` | 禁 overnight σ 换皮 |
| 叶24 IMAX | 日内右尾 | 禁右尾极值复刻 |
| 叶26 GAP ETF 流 | 产品层份额 | 本票不交审叶26；禁 ETF 份额进主信号 |

**PRIMARY 选定**：**HI_LIQ 短窗 Amihud/冲击成本残差慢 α**。  
**备选（§12）**：CFO/应计质量正交切片（ΔNOA 或 CCC 残差）— 仅作研究备注，**不**升 PRIMARY，须另证 vs 叶25/30 低相关。

---

## 2. 机制（价量微观；慢 α）

在 HI_LIQ 池、日频 OHLC+成交额上定义短窗冲击：

\[
\mathrm{Amihud}_{i,t}^{\mathrm{raw}} = \frac{1}{W}\sum_{s=0}^{W-1} \frac{|r_{i,t-s}|}{\mathrm{amount}_{i,t-s}}
\]

- \(r\) = 复权日收益（`research/adj_price` 口径；缺价/停牌 → 该日无效，不填 0）。
- \(\mathrm{amount}\) = 成交额（元）；≤0 或缺失 → 该日无效。
- **W DRAFT=20** 交易日（最少有效日冻结时写死，建议 ≥15）；再平衡建议每 **20** 日（慢 α，对齐叶19/30 慢节奏，非叶27 快波动复刻）。
- 可选同族变体（**敏感性支路，非主规格**）：日内冲击 `|r_id|/amount`、或 `|open/pre_close−1|×f(amount)` 开盘缺口×成交额；冻结前**不算收益选支路**。

**合成（DRAFT）**：

\[
\alpha_{\mathrm{raw}} = -\mathrm{rank}(\mathrm{impact\_resid})
\]

池内百分位 rank；再按残差清单中性 → **日度 base-α 向量**（instrument→alpha；**非 Top-N**）。

---

## 3. 残差规格（截面；缺则记 GAP）

同日截面、HI_LIQ 掩码后：

1. 原始：`Amihud_raw`（或冻结时写死的冲击定义）。
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。
3. vs **log 流通市值** OLS 残差（市值 T−1 PIT）。
4. vs **style 代理**（DRAFT 建议至少：mom20、vol20、log ADV20 / capacity_adv 暴露）— 冻结时写死清单；缺列 → PIN_GAP，勿静默跳过。
5. 披露 vs 叶19 / 叶25 / 叶27 / 叶30 α 的 **Jaccard** 与 **ρ_excess**（家族多重检验 n 至少含上述 + 本叶）。
6. **禁**把叶27 `on_minus_id` 或 overnight ε 当本叶主输入。

---

## 4. 数据 PIT

| # | 输入 | 备注 |
|---|---|---|
| 1 | 日频 OHLC / 复权因子 | `research/adj_price`；涨跌停/停牌旗披露 |
| 2 | 成交额 amount | bars/日频；单位元；PIT as-of 再平衡日 |
| 3 | HI_LIQ 掩码 | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet`（HI_LIQ_V1.1） |
| 4 | SW L1 PIT | `data/v2/sw_l1_pit/…` |
| 5 | 流通市值 T−1 | 残差用 |
| 6 | 叶19/25/27/30 α parquet | **仅** Jaccard/ρ；不进主信号 |

**GAP 纪律**：缺列/缺窗 → 记 GAP，**勿静默编造** amount 或收益。

---

## 5. 宇宙 / 窗 / 交付

| 项 | 值 |
|---|---|
| 宇宙判决 | **HI_LIQ 主**（纸面路径）；**FULLA 研究**对照双钉意向（预注册须同时冻结两池规格，但 PRIMARY 判决 = HI_LIQ） |
| X2 样本内窗意向 | **2024-06-03 → 2026-10-09**（与叶25/30 对齐；冻结时写死） |
| 再平衡 | DRAFT **20** 交易日 |
| 成本口径 | **30bp**（评价；本 DRAFT 不算 PnL） |
| 主交付 | **日度 base-α 向量** → 优化器；非 Top-N 当闸 |
| rss 意向 | **1500** MB 禁抬 |
| live / promotion | `false` / `false` |

---

## 6. 预注册须（冻结前写死）

1. **截面残差**：SW L1 + style（上表清单）。
2. **HI_LIQ 判决**为主；FULLA 仅研究披露。
3. **walk-forward** 分段披露（冻结时钉切点；本 DRAFT 不跑）。
4. **Gate B / GATE_V3** 评价清单；衰减门 v1.1。
5. **decay KEEP 硬验收**（见 §7）。
6. Jaccard/ρ 硬拒意向 vs 叶19/25/27/30（§8）。

---

## 7. decay KEEP 设计（盯近端；对齐叶30 HOLD 教训）

叶30 HOLD 根因：`latest_alpha<0` + `H2_net_cagr<=510300` → **DECAY_DOWNGRADE**。本叶设计时即把 KEEP 当硬验收，而非事后补丁：

| 闸 | DRAFT 意向 |
|---|---|
| 近端残差 α | **latest_resid_alpha > 0**（年化；衰减门 v1.1 口径） |
| H2 净 CAGR | **H2_net_cagr > 510300 净 CAGR**（同窗、同成本口径） |
| 近端窗定义 | 冻结时写死（建议：X2 后半 / 最近 ~1y 交易日；与 `alpha_decay_gate` H2 对齐） |
| 失败截断 | 任一条不满足 → **最多 WATCH / HOLD**；**不派** Book-Smoke；≠X2 ACCEPT |
| 设计防衰减 | 慢再平衡（20d）+ 残差掉 ADV/市值（避免「高成交追涨」近端反转）；禁快闸与慢 α 混装同一主规格 |

**风险**：HI_LIQ 内 Amihud 截面离散度可能偏窄 → 覆盖/IC 弱；若与 capacity_adv / 低波动近等权则硬拒。失败即截断，不事后改符号。

---

## 8. 正交硬闸（对齐叶30 count gate 精神）

| 对照 | 硬规则 |
|---|---|
| 叶19 / 叶25 | Jaccard≥0.7 → **硬拒**；ρ_excess>0.5 → 强度过滤（披露） |
| 叶27 | 同上；**额外**：主输入不得为 `on_minus_id` / overnight ε |
| 叶30 CRR | 同上；禁会计转化率字段进主信号 |
| 覆盖 | HI_LIQ 再平衡日可算 α 名数 **median≥300** |
| 换手/成本 | 成本 30bp；>20%/日或成本>毛超额一半 → 不可交易（冻结后评价） |
| 衰减 / Gate A·B / GATE_V3 | 冻结+独立 `.ok`+X2 后再跑；本 DRAFT 不跑 |

---

## 9. 失败截断

- 计数闸 median<300 → 不冻结 / 不申 `.ok`
- Jaccard≥0.7 vs 叶19/25/27/30 → 硬拒，改机制或废叶
- 冻结前读收益选方向/W/λ → 违规，作废本草稿轮
- decay 非 KEEP 或 Gate B/GATE_V3 FAIL → 不派烟、≠X2 ACCEPT
- 内存 peak≥1500 → 硬 ABORT（未来执行窗）

---

## 10. 本拍交付与下一跳

| 里程碑 | 条件 |
|---|---|
| 本 who_pays + COVER DRAFT | 本文件 + audit COVER；**ok_requested=false** |
| 主排号 | 请主确认叶号=31（或台账下一空号）并登记台账意向行 |
| Arch | **只审不签**（文档契约）；PASS 后另排预注册冻结 / 脚本窗 |
| 申请 `.ok` / X2 | **另窗**；禁 RESTORED 旧 `.ok`；禁复用叶25/27/30 `.ok` |
| 叶26 | **不交审** |
| 叶28/29 | **仍 FROZEN** |
| 叶30 | HOLD 研究队列；衰减修复见可选 DRAFT；**禁**重跑 selfcheck |

---

## 11. 禁项清单（再钉）

- 全窗 X2 / selfcheck / Book-Smoke（本拍）
- 申 `.ok`；挂/抬 QUIET；抬 RSS；git commit
- GP / 杠杆 / 卖方 / 金股 / survey / TP / LLM 权重当 α
- 叶27 overnight−intraday idio 复刻；叶25/30 会计主轴复开
- RESTORED `aa25e989` / `7e239487` / `5af20222` / `5ae077fa`
- 推 Leo；`live=true`；`promotion_approved=true`；声称 X2 ACCEPT

---

## 12. 备选一节（非 PRIMARY）：质量正交切片

若主裁改走质量轴，候选 **ΔNOA 残差** 或 **cash conversion cycle（CCC）残差**（SW+style；HI_LIQ 判决）：

- 须事前证明 vs 叶25 `cfacc_desens` / 叶30 CRR 的 Jaccard≪0.7 且 ρ_excess 披露
- **本票不升 PRIMARY**；仅备案，避免与已 HOLD/WATCH 应计族叠床架屋

---

## 13. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_WHO_PAYS_DRAFT_20261027_ZH.md` |
| COVER | `docs/v2/audit/AI_LEAF31_AMIHUD_IMPACT_SLOW_COVER_DRAFT_20261027_ZH.md` |
| 状态 | **DRAFT NOT FROZEN** |
| mechanism_tag | `g1g5_ashare_amihud_impact_slow_v1` |
| PRIMARY | HI_LIQ 短窗冲击残差慢 α |
| live / promotion / ok_requested | false / false / false |
| ≠X2 ACCEPT | true |
| leo_notify | false |

**sha256 / sha8**：落盘后由写出脚本打印（以磁盘为准）。
