# 叶27 who_pays · Alpha 空位填审（研究级）

- **日期**：2026-10-25 ≈06:02 ET · America/New_York
- **作者**：QuantLab Alpha
- **对象**：主 Agent、AI、Arch（知会）
- **输入草稿**：`docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md` sha256 `4a0eec1a4d1694be7a91b8cd291b8d1547e68ff41f8b9121e90dd7f44967282b`（sha8 `4a0eec1a`）
- **对齐骨架**：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md` sha256 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605` —— **叶候选 2**
- **锁**：`live=false` · `promotion_approved=false` · **不申 .ok** · 不挡叶25 · 禁 GP · 禁读收益选向

## 结论先行

| 项 | Alpha 裁定 |
|---|---|
| 空位填审 | **PASS_WITH_CONDITIONS**（可进正式预注册起草；非 FROZEN） |
| mechanism_tag | **采纳** `g1g5_ashare_on_minus_id_idio_ivol_v1` |
| 主轴 | **采纳** `on_minus_id = r_on − r_id` → 截面残差清单 → 滚动 `σ(ε)`；**非**叶18 单纯 `ε_on` |
| who_pays | **采纳价量公式对手**（见下）；精神/情绪/叙事主轴 = **硬拒** |
| 方向 | **未冻结**；DRAFT 倾向 `α=−ivol` 仅作起草默认，**冻结前禁读本叶收益/IC 选向**；冻结后禁翻号 |
| 叶25 | **仍优先**（钉 `7b279d47` + R5c_v3 `be7f5e5a`；窗 10:00–10:45 ET）；本叶排队、不申 `.ok` |
| 晋级 | 研究级骨架通过 ≠ ACCEPT；无独立新窗 `.ok`+X2 回执前不做闸审裁决 |

## 1. Alpha 空位（定稿可摘抄）

> **mechanism_tag**：`g1g5_ashare_on_minus_id_idio_ivol_v1`（叶27）  
> **who_pays（一句·价量公式）**：付钱的是在日频价上忽视「`r_on=open/pre_close−1` 与 `r_id=close/open−1` 之差 `on_minus_id=r_on−r_id`，经 SW L1·log 流通市值·滚动β·capacity_adv 残差后的滚动特质波动 σ(ε)」所刻画的开盘跳空相对连续竞价冲击错配、从而在高 σ(ε) 一侧过度承接流动性需求的对手盘——**公式对手，不是「隔夜情绪/精神面」叙事对手**。  
> **可检验预测**：残差化后的拆分特质波动 α，对次日特质收益的截面 IC 符号在**正式预注册冻结时**写死（本填审与 DRAFT 均不读收益选号）；活跃集 vs capacity_adv / expand / moneyflow_resid / 叶18·18v / 叶24 / 叶25 / 叶26 的 Jaccard ≪0.7 且 frac(J≥0.7)=0；须报残差 ρ。  
> **失效条件**：who_pays 或正文以精神/情绪/叙事作主轴；或退化成未残差隔夜收益动量（expand 换皮）；或与叶18 `α=−std(ε_on)` 近等权（Jaccard≥0.7∧近等权）；或与叶24 IMAX 日内右尾近等权；或主信号混入个股 moneyflow / ETF 份额流 / 应计质量；或冻结后事后翻转方向。  
> **交 Alpha 闸审时点**：正式预注册 **FROZEN** + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只填空位。叶25 窗冲突时本叶让路。

## 2. 相对历史包硬闸（Alpha 确认）

| 对照 | 硬规则（本叶必须） | Alpha 审阅 |
|---|---|---|
| 叶18 / 18v overnight_idio_ivol | 主轴必须是 **`on_minus_id` 残差波动**，禁止 silent 复跑 `std(ε_on)`；Jaccard≥0.7∧近等权→拒；ρ_excess>0.5→最多过滤、不得主叶 ACCEPT | **确认** |
| 叶24 IMAX（剔隔夜） | 二阶矩拆分差 ≠ 日内右尾极值；须对叶24 α 残差或 Jaccard 硬闸 | **确认** |
| v23 类 overnight「精神」 | who_pays/正文 **零**精神/情绪叙事关键词作主轴；同构重开→硬拒 | **确认**（与候选2 硬禁一致） |
| expand / 相对强弱 | 禁用未残差 `r_on` 动量换皮 | **确认** |
| moneyflow_resid | 个股 D2 moneyflow **不得**进主信号；**禁** moneyflow×capacity_adv 80/20 叠仓续挖（Leo 已否） | **确认** |
| 叶25 cfacc_desens | 价量快 vs 会计慢分家；禁复用叶25 `.ok`；窗冲突让路 | **确认** |
| 叶26 ETF 流 | 禁产品层份额流/ETF↔指数映射进主信号 | **确认** |
| capacity_adv | 残差清单强制第 5 步；共用 Jaccard/ρ 闸 | **确认** |

**一句话分家（Alpha 背书）**：叶18=隔夜残差波动；叶24=日内右尾；叶27=**隔夜−日内差**的残差特质波动；精神叙事=禁区。

## 3. 残差化清单（采纳 DRAFT §3；窗长仍待预注册冻结）

1. `on_minus_id`（PIT OHLC；缺 open/pre_close 或 pre_close≤0 → 无效）  
2. SW L1 demean  
3. vs log 流通市值 OLS（T−1 PIT）  
4. vs 滚动β（市场或 510300；**窗长冻结时写死**；DRAFT 建议 60 会话 / 最少 40 — Alpha **不在此冻结**）  
5. vs capacity_adv 暴露/活跃指示  
6. `ivol = std(ε, W)`（DRAFT 建议 W=20 / 最少 15 — **同样待冻结**）  
7. 披露 vs 叶18/18v/叶24/expand/moneyflow_resid/叶25/叶26/capacity_adv 的 Jaccard 与 ρ_excess  

缺任一步 → 记 GAP，不得静默跳过。

## 4. 方向（关键）

- **状态：UNFROZEN**。本填审 **不**把 `α=−ivol` 写成 FROZEN。  
- DRAFT 倾向 −ivol 可作正式预注册 **起草默认**，但冻结瞬间必须显式写死；冻结前 **禁止**打开本叶收益/IC/X2 选向。  
- 冻结后：主规格不得因读数翻成 `+ivol`；`+ivol` 仅可事前敏感性支路且不得升格。

## 5. 条件（PASS_WITH_CONDITIONS）

1. AI 出正式预注册 r1（FROZEN）时：方向、β 窗、W、停牌/涨跌停剔除规则一次写死；附与叶18 构造差对照表。  
2. Data/Arch：OHLC/`adj_price`、SW L1、市值 T−1、capacity_adv 指示契约确认后才可申本叶独立 `.ok`。  
3. **不**复用叶25 钉；叶25 10:00–10:45 ET 优先。  
4. 质量应计（候选3）仍等叶25 闸——本填审不开。  
5. moneyflow 80/20 叠仓路径已关闭，本叶验收门叙述中的「叠仓」仅指未来相对 capacity_adv 的组合诊断，**不**复活已否路径。

## 6. 非动作

- 不申 `.ok`；不改脚本；不读生产收益；不改 `alpha_labels`；不派 Eng/Book-Smoke；不碰纸面。  
- 叶25 无包不预判。

live=false；promotion_approved=false。
