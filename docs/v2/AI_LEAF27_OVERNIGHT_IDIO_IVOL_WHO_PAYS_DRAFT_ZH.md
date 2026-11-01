# 【DRAFT — NOT FROZEN】叶27 who_pays：overnight−intraday / idiosyncratic vol

- 角色：QuantLab AI（后台执行器）
- 时点：2026-10-25 约 05:58–06:00 ET（America/New_York；箱 `date`）
- 状态：**DRAFT NOT FROZEN**。只交 who_pays 草稿；**不申请** `.ok`；**不** git commit；**不**读实行情/收益调参；**不**挡叶25 10:00–10:45 ET 窗。
- 对齐 Alpha：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md` sha256 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605` —— **叶候选 2** 空位（overnight−intraday / idiosyncratic vol）。
- 叶26 权威钉（正交参照，非本叶规格）：`docs/v2/AI_LEAF26_BROAD_ETF_FLOW_STOCK_WHO_PAYS_DRAFT_r2.md` sha256 `0b55bfeb3b033da4715e4dbc5c996e92b954fc10e385c10b308da992d87a60b5`（仅 510300/510500）。
- 叶25 优先钉：`.ok` sha8 `7b279d47` + R5c_v3 `be7f5e5a`；质量应计（候选3）**等叶25 闸后再开**——本文件**不开质量主轴**。
- 禁：卖方 / 金股 / 一致预期；禁 GP；禁个股 moneyflow 主轴；禁 overnight「精神/情绪」叙事主轴；禁与 v23 已 REJECT 精神同构重开；禁 moneyflow×capacity_adv 80/20 叠仓挖洞。
- `live=false`；`promotion_approved=false`。

---

## 0. Alpha 空位填写（交 Alpha 用·可整段摘抄）

> **mechanism_tag**：`g1g5_ashare_on_minus_id_idio_ivol_v1`（叶27）  
> **who_pays（一句·价量公式）**：付钱的是在日频价上忽视「`r_on=open/pre_close−1` 与 `r_id=close/open−1` 之差 `on_minus_id=r_on−r_id`、经 SW L1·log 流通市值·滚动β·capacity_adv 残差后的滚动特质波动 σ(ε)」所刻画的开盘跳空相对连续竞价冲击错配、从而在高 σ(ε) 一侧过度承接流动性需求的对手盘——**公式对手，不是「隔夜情绪/精神面」叙事对手**。  
> **可检验预测**：残差化后的拆分特质波动 α，对次日特质收益的截面 IC 符号在预注册**冻结时**写死（本 DRAFT 不读收益选号）；活跃集 vs capacity_adv / expand / moneyflow_resid / 叶18·18v / 叶24 / 叶25 / 叶26 的 Jaccard ≪0.7 且 frac(J≥0.7)=0；须报残差 ρ。
> **失效条件**：who_pays 或正文以精神/情绪/叙事作主轴；或退化成未残差隔夜收益动量（expand 换皮）；或与叶18 `α=−std(ε_on)` 近等权（Jaccard≥0.7∧近等权）；或与叶24 IMAX 日内右尾近等权；或主信号混入个股 moneyflow / ETF 份额流 / 应计质量；或冻结后事后翻转方向。  
> **交 Alpha 时点**：正式预注册冻结 + Arch 审脚本 + 本叶**独立**新窗 `.ok` + X2 回执之后；现在只交 DRAFT。叶25 窗冲突时本叶让路。

---

## 1. 机制（价量拆分，非精神）

A 股日收益可拆为隔夜与日内：

- `r_on = open / pre_close − 1`（缺 open/pre_close 或 pre_close≤0 → 当日该票无效）
- `r_id = close / open − 1`
- **主拆分量**：`on_minus_id = r_on − r_id`

本叶主 α 来自对 `on_minus_id`（或先对市场/510300 回归后的残差）做截面残差化后的**滚动特质波动**，捕捉开盘跳空相对日内连续竞价的**可复现价量错配**。  
**允许**：价量公式、残差、σ。  
**禁止**：把「隔夜精神 / 隔夜情绪 / 叙事面」写进 who_pays 或作主轴（与 Alpha 候选2 硬禁、v23 类 REJECT 同构禁开一致）。

主交付：**日度 base-α 向量**（instrument→alpha），不是 Top-N 名单当闸。

---

## 2. 相对历史包的差异（禁止同构重开）

| 包 | 要点 | 叶27 必须多出来的正交 |
|---|---|---|
| 叶18 `overnight_idio_ivol` | `std(ε_on,20)`，α=−ivol；WATCH（不可交易/衰减/Gate A·B/GATE_V3 FAIL） | **主轴是 `on_minus_id` 的残差波动**，不是单纯 overnight 残差 σ；残差清单强制含滚动β + vs capacity_adv；禁 silent 复跑叶18 |
| 叶18v lowto | 仅换手/再平衡变体；WATCH；与叶18 ρ≈0.85 | 不得以「再调再平衡」当新叶；Jaccard/ρ 对叶18·18v 硬闸 |
| 叶24 IMAX（剔隔夜） | 日内特质收益 20 日窗前 5 大均值，低 IMAX 做多 | 本叶是**拆分差的二阶矩**，不是日内右尾极值；须对叶24 α（若已有）残差或 Jaccard 硬闸 |
| v23 类 overnight「精神」 | 已硬禁 / REJECT | who_pays **零**精神/情绪叙事关键词作主轴 |
| expand / 相对强弱 | 未残差隔夜/动量 | 禁用未残差 `r_on` 当动量换皮 |
| moneyflow_resid | 个股资金流残差 | 禁个股 moneyflow 进主信号；已否 80/20 叠仓 |
| 叶25 cfacc_desens | 应计脱敏（优先窗） | 会计慢叶；本叶偏快价量；禁混 .ok |
| 叶26 ETF 流→成分 | 产品层份额流 | 禁 ETF 份额/资金流进主信号 |

**一句话分家**：叶18=隔夜残差波动；叶24=日内右尾；叶27=**隔夜−日内差**的残差特质波动；精神叙事=禁区。

---

## 3. 残差化清单（同日截面；缺则记 GAP，不得静默跳过）

1. 原始拆分量：`on_minus_id`（PIT：当日 OHLC/`research/adj_price` 口径；停牌/涨跌停旗披露）。  
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）。  
3. vs **log 流通市值** OLS 残差（市值用 T−1 PIT）。  
4. vs **滚动β**（市场或 510300；窗长预注册冻结时写死，DRAFT 建议 60 会话、最少 40 有效）。  
5. vs **capacity_adv 暴露/活跃指示** 再正交一层。  
6. 滚动特质波动：`ivol = std(ε, W)`（DRAFT 建议 W=20 会话、最少 15 有效）→ 得 σ(ε)。  
7. 披露 vs 叶18 / 叶18v / 叶24 / expand / moneyflow_resid / 叶25 / 叶26 / capacity_adv 的 Jaccard 与 ρ_excess。

残差化最低清单与 Alpha 三条共用闸一致：**SW L1 + log 市值 + 滚动β + vs capacity_adv**。

---

## 4. 方向预注册说明（不可事后切换）

| 项 | DRAFT 约定 |
|---|---|
| 主规格方向 | **待冻结**：默认写作倾向 `α_raw = −ivol`（高拆分特质波动 → 惩罚 / 低波动优先），与叶18 方向族一致但**主轴不同** |
| 禁事后翻 | 冻结后不得因 X2/密封读数把主规格改为 `α=+ivol`；奖励高波动只能作为**事前**敏感性支路且不得升格为主规格 |
| 冻结时机 | 正式预注册文件（非本 DRAFT）落盘瞬间写死方向；冻结前**禁止**读本叶收益/IC 选方向 |
| 本 DRAFT | 不读生产 parquet 算收益；不声称方向已 FROZEN |

---

## 5. 正交硬闸

共用：活跃集 Jaccard 均 ≪0.7 且 frac(Jaccard≥0.7)=0；≥0.7∧近等权 → 换皮硬拒；须报残差 ρ；伪耦合（ρ 高且叠加≈加权和）→ CMC 不得 PASS。

| 对照 | 硬规则 |
|---|---|
| capacity_adv | 残差清单第 5 步强制；ρ 与 Jaccard 按共用闸 |
| expand / 相对强弱 | 禁用未残差隔夜收益当动量换皮 |
| moneyflow_resid | 个股 D2 moneyflow **不得**进主信号；禁 80/20 叠仓路径续挖 |
| 叶18 / 18v | Jaccard≥0.7∧近等权 → 拒；ρ_excess>0.5 → 最多作过滤、不得开主叶 ACCEPT |
| 叶24 IMAX | 同上；构造上禁止退化为日内右尾 |
| 叶25 应计 | 机制分家（价量快 vs 会计慢）；禁复用叶25 `.ok`；窗冲突让路叶25 |
| 叶26 ETF 流 | 禁产品层份额流/ETF↔指数映射进主信号 |
| 已禁 overnight 精神叶 | who_pays/正文不得以精神/情绪叙事关键词作主轴 |

---

## 6. PIT 输入候选与缺数（只列，不读生产收益）

| # | 候选输入 | 备注 / 缺数 |
|---|---|---|
| 1 | 日频 OHLC / 复权价（`research/adj_price` 或 Arch 钉的 daily PIT） | 须重钉实现 sha；本 DRAFT 不打开收益列调参 |
| 2 | 停牌 / 涨跌停旗 | 复牌首日跳空披露；信号是否剔除预注册写死 |
| 3 | SW L1 PIT | 与叶25/26 同族契约；缺 as-of 则记 GAP |
| 4 | log 流通市值 PIT（T−1） | 缺则不得静默用 T |
| 5 | 滚动β（市场或 510300） | 窗长/最少有效日冻结时写死 |
| 6 | capacity_adv 暴露/活跃指示 | 缺则记 GAP，不得跳过正交 |
| 7 | 可选结构字段 `overnight_ret`,`intraday_ret`,`on_minus_id`（方向库已列名） | **须重钉实现 sha**；不得假设旧字段与本公式字节级一致 |
| 8 | 叶18/18v/叶24 α 向量（若盘面仍在） | 仅供正交残差/Jaccard，不进主信号合成 |

**禁读作主轴**：个股 `moneyflow_stock_daily_pit`；ETF 份额流（叶26）；financials/应计（叶25/候选3）；卖方/金股/一致预期。

---

## 7. 验收门（研究级；本 DRAFT 不跑）

- A/A′：拆分残差 ivol 的 IC/ICIR + 特质 α  
- B：中性后相对 capacity_adv（含 cap80+叶20）  
- C：本叶偏**快**（日/周），与 moneyflow 慢袖错配检查必做  
- CMC / GATE_V3：过门后才可议 Book-Smoke；衰减 KEEP；换手≤20%/日；两档 MDD≤25% 且净 CAGR>capacity_adv  
- 门B 并报（Calmar 两档胜主干且 MDD≤15%）

研究级至少 A+A′；进 GATE_V3/派 Eng 须 A+A′+B+C。

---

## 8. 交 Alpha 时点表

| 里程碑 | 时点 / 条件 |
|---|---|
| 本 DRAFT 交主/Alpha | 本文件落盘（sha 见文末） |
| 预注册 r1（FROZEN） | 方向写死 + 残差窗长写死 + Arch 可审脚本 + Data 确认 OHLC/市值/SW PIT 契约 |
| 申请 `.ok` | **另窗**；不复用叶25 `7b279d47`/`be7f5e5a`；叶25 10:00–10:45 ET 优先时本叶排队 |
| X2 / 交 Alpha 闸 | 独立回执后；WATCH/FAIL 不交 ACCEPT |
| 质量应计（候选3） | **等叶25 闸**；本文件不开 |

---

## 9. 禁项清单（再钉）

- overnight「精神 / 情绪 / 叙事」主轴或 who_pays  
- 与 v23 已 REJECT 精神同构重开  
- 无残差 Top-N 等权当闸  
- 高杠杆 / 隔夜杠杆产品；GP  
- 个股 moneyflow 主轴；moneyflow×capacity_adv 80/20 续挖  
- 叶25/26 混 .ok 或抢跑质量应计  
- 冻结后翻转高 idio vol 惩罚↔奖励  
- 本 DRAFT 阶段读生产收益选参 / 申 `.ok` / 改 TEAM_STATE

---

## 10. 草稿钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md` |
| 状态 | DRAFT NOT FROZEN |
| live | false |
| promotion_approved | false |

**sha256**（整文件，写出后由 `sha256sum` 打印；以磁盘为准）：见落盘后命令输出。
