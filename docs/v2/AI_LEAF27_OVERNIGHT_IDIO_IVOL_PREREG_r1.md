# 【FROZEN 2026-10-25 06:11:04 ET】叶27 正式预注册 r1：隔夜−日内差特质波动（g1g5_ashare_on_minus_id_idio_ivol_v1）

- **起草/冻结**：2026-10-25 06:11:04 ET（America/New_York；箱 `TZ=America/New_York date`）
- **角色**：QuantLab AI（后台执行器）
- **状态**：**FROZEN**（本文件落盘瞬间写死方向、β 窗、W、停牌/涨跌停规则；**冻结后禁翻号**）
- **声明**：冻结前**未读**本叶任何收益 / IC / X2 / 密封读数以选方向或窗长；起草默认 `α_raw=−ivol` 来自 Alpha 空位填审与 who_pays DRAFT，非事后选号。
- **对齐输入**（落盘前 Read；sha 以磁盘为准）：
  - Alpha 空位填审 PASS_WITH_CONDITIONS：`docs/v2/ALPHA_LEAF27_WHO_PAYS_SLOT_FILL_REVIEW_20261025_ZH.md` sha256 `01ab6bf39ca276c459c9febb1178f1d1afa9e5b8170a167b4a16a904a297f801`
  - who_pays DRAFT：`docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_WHO_PAYS_DRAFT_ZH.md` sha256 `4a0eec1a4d1694be7a91b8cd291b8d1547e68ff41f8b9121e90dd7f44967282b`
  - Alpha 骨架（候选2）：`docs/v2/ALPHA_NEXT_ORTHO_LEAF_DEFS_20261025_ZH.md`（审阅钉 `20c031c911c46e7e61d09f9f811616f066b93a0122900f3b85ce2076f6a14605`；盘上可能已追加空位填注，定义以候选2 正文为准）
  - 叶18 预注册对照：`docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_WHO_PAYS_PREREG_ZH.md`
- **锁**：`live=false` · `promotion_approved=false` · 研究级 · **不申 `.ok`** · **不** git commit · **不**改 TEAM_STATE · **不挡**叶25 10:00–10:45 ET（钉 `7b279d47` / R5c_v3 `be7f5e5a`）· 禁 GP / 卖方 / 金股 / 一致预期 · 禁 moneyflow 80/20 续挖

---

## 0. mechanism_tag 与 who_pays（一句·价量公式）

> **mechanism_tag**：`g1g5_ashare_on_minus_id_idio_ivol_v1`（叶27）  
> **who_pays**：付钱的是在日频价上忽视「`r_on=open/pre_close−1` 与 `r_id=close/open−1` 之差 `on_minus_id=r_on−r_id`，经 SW L1·log 流通市值·滚动β·capacity_adv 残差后的滚动特质波动 σ(ε)」所刻画的开盘跳空相对连续竞价冲击错配、从而在高 σ(ε) 一侧过度承接流动性需求的对手盘——**公式对手，不是「隔夜情绪/精神面」叙事对手**。

**可检验预测**：残差化后的拆分特质波动 α 对次日特质收益的截面 IC 符号以本文件冻结的主规格方向为准（`α_raw=−ivol`）；活跃集 vs capacity_adv / expand / moneyflow_resid / 叶18·18v / 叶24 / 叶25 / 叶26 的 Jaccard ≪0.7 且 frac(J≥0.7)=0；须报残差 ρ。

**失效条件**：who_pays/正文以精神/情绪/叙事作主轴；或退化成未残差隔夜收益动量（expand 换皮）；或与叶18 `α=−std(ε_on)` 近等权（Jaccard≥0.7∧近等权）；或与叶24 IMAX 日内右尾近等权；或主信号混入个股 moneyflow / ETF 份额流 / 应计质量；或冻结后事后翻转方向。

---

## 1. 双宇宙（看结果前同时冻结）

| 口径 | 掩码 | 角色 | 行业帽 |
|---|---|---|---|
| **HI_LIQ_V1.1**（主） | `output/strategy_hiliq/universe_mask_hiliq_v1.parquet` | 主报密封满窗 + X2 | SW L1 ≤25% |
| **FULLA_V1**（研究对照） | `output/strategy_fulla/universe_mask_fulla_v1.parquet` | X2 对照；密封仅重叠段 | SW L1 ≤28% |

掩码列沿用既有契约（含 `date, instrument, in_universe, st, suspended, young, adv_fail, adv20_yuan` 等）。本叶不新开宇宙。

---

## 2. 冻结参数（落盘瞬间 FROZEN；禁止读收益后改）

### 2.1 方向（主规格）

| 项 | 冻结值 |
|---|---|
| 主规格 | **`α_raw = −ivol`**（高拆分特质波动 → 惩罚；低波动优先） |
| 敏感性支路 | **`+ivol` 仅可事前标为敏感性**，不得升格为主规格；不得因读数把主规格翻成 `+ivol` |
| 冻结后 | **禁翻号** |

### 2.2 β 窗（主规格）

| 项 | 冻结值 |
|---|---|
| 市场基准 | **510300** 日收益（主规格写死这一种；非「市场或 510300」双选） |
| 滚动窗 | **60 会话** |
| 最少有效观测 | **40**；不足 → 该票当日无效（不进 α、不进活跃集） |

### 2.3 W（ivol 窗）

| 项 | 冻结值 |
|---|---|
| 定义 | `ivol = std(ε, W)`，ε 为残差清单末步残差 |
| W | **20 会话** |
| 最少有效残差 | **15**；不足 → 该票当日无效 |

### 2.4 停牌 / 涨跌停规则（写死）

| 情形 | 规则 |
|---|---|
| **当日停牌** | **无效**：不进 α、不进活跃集。旗名优先：宇宙掩码 `suspended` / HI_LIQ 池 `suspend_d` 当日停牌语义；若面板另有 `halted_fullday` 等 Arch/Data 已 ACCEPT 旗，以盘面已有旗为准并在回执披露所用列名与 sha。 |
| **当日涨跌停** | **不参与当日截面回归与 ivol 更新**；持仓侧评价权重该日 **gate=0**。旗名优先：面板 `limit_up_flag` / `limit_down_flag`（若存在且 PIT）；否则收盘触板旗，或 `|close/pre_close−1|` 达板且成交受限之 Arch/Data 已钉旗——**回执必须披露实际采用的旗名与实现 sha**，不得静默换定义。 |
| **复牌首日** | `r_on` / `on_minus_id` **可算则计入**残差与 ivol；须在回执披露复牌跳空统计（名数/分位）；**不**另开精神/情绪叙事；`is_resume_day`（若有）仅作披露与入场闸参考，不改主公式。 |
| **缺 open / pre_close 或 pre_close≤0** | **无效** |

---

## 3. 公式与残差化清单（同日截面；缺任一步 → GAP，不得静默跳过）

### 3.1 价量拆分

1. `r_on = open / pre_close − 1`
2. `r_id = close / open − 1`
3. **主拆分量**：`on_minus_id = r_on − r_id`

PIT：当日 OHLC / `research/adj_price` 口径（实现 sha 在独立 `.ok` 窗重钉；本预注册不打开收益列调参）。

### 3.2 残差清单（顺序写死）

1. 原始：`on_minus_id`（§2.4 无效票剔除后）  
2. **SW L1 demean**（行业内去均值；名过少时仅 demean，回执披露）  
3. vs **log 流通市值** OLS 残差（市值 **T−1** PIT）  
4. vs **滚动β**（对 **510300**，§2.2：60 会话 / 最少 40）  
5. vs **capacity_adv** 暴露/活跃指示  
6. `ivol = std(ε, W)`（§2.3：W=20 / 最少 15）→ **`α_raw = −ivol`**  
7. 分域（流通市值 P70/P90：小微/中小盘/大盘）内 rank→[-1,1]；再对行业+log 市值残差一次，得 **base-α**（日度 instrument→alpha 向量；不是 Top-N 名单当闸）

### 3.3 评价权重（研究级默认；不挡本文件冻结）

- 再平衡：每 **5** 个交易日按当日 base-α 重算评价权重（与叶18 同类；正式跑前可在 Arch 审脚本时确认，**不得**借此改方向/β/W）  
- 每名 ≤4%、≤20 名；行业帽见 §1；余额 510300；硬排除 600519/002371；只在 gate=1 的票中按 α 降序取  
- 涨跌停日 gate=0（§2.4）

### 3.4 窗口与成本（研究叙述；本文件不跑）

- 密封：2018-01-02→2024-05-31（HI_LIQ 满窗；FULLA 重叠段）  
- X2：2024-06-03→（结束日在独立 `.ok` 窗硬钉，不在本文件读最新日）  
- AUM 60万/100万；年化 244 主 / 252 对照  
- 成本与叶18/23/24 并报表口径一致披露（17.5bp 与 30bp 并列处从 Arch/自检惯例）

---

## 4. 与叶18 构造差对照（必节；禁 silent 复跑叶18）

| 维 | 叶18 `g1g5_ashare_overnight_idio_ivol_v1` | 叶27（本文件）`g1g5_ashare_on_minus_id_idio_ivol_v1` |
|---|---|---|
| 主轴原始量 | `r_on` → 截面残差 `ε_on` | **`on_minus_id = r_on − r_id`** → 残差 ε |
| 残差是否含滚动β | 叶18 主规格：SW L1 + log 市值（**无**滚动β步） | **强制**滚动β（510300，60/40） |
| 残差是否含 capacity_adv | 叶18 主规格：**无** vs capacity_adv 步 | **强制** vs capacity_adv |
| ivol / 方向 | `ivol=std(ε_on,20)`；`α=−ivol` | `ivol=std(ε,20)`；**同为 `α=−ivol`，但主轴不同** |
| 快门 | 近 1–3 日 ε_on 左尾 5% gate=0 | 本叶主规格**不**复用叶18 快门；涨跌停/停牌按 §2.4 |
| 正交 | — | 对叶18/18v α：**Jaccard≪0.7** 且 frac(J≥0.7)=0；Jaccard≥0.7∧近等权 → **硬拒**；ρ_excess>0.5 → 最多过滤、不得主叶 ACCEPT |
| 禁 | — | **禁 silent 复跑** `std(ε_on)` 当本叶；禁以「再调再平衡/换 W」冒充新叶（叶18v 先例） |

**一句话分家**：叶18=隔夜残差波动；叶24=日内右尾；叶27=**隔夜−日内差**的残差特质波动；精神叙事=禁区。

---

## 5. 正交硬闸（读收益前写死）

共用：活跃集 Jaccard 均 ≪0.7 且 frac(Jaccard≥0.7)=0；≥0.7∧近等权 → 换皮硬拒；须报残差 ρ；伪耦合（ρ 高且叠加≈加权和）→ CMC 不得 PASS。

| 对照 | 硬规则 |
|---|---|
| capacity_adv | 残差清单第 5 步强制；ρ 与 Jaccard 按共用闸 |
| expand / 相对强弱 | 禁用未残差 `r_on` 动量换皮 |
| moneyflow_resid | 个股 D2 moneyflow **不得**进主信号；**禁** moneyflow×capacity_adv 80/20 叠仓续挖（Leo 已否） |
| 叶18 / 18v | 见 §4；禁 silent 复跑 |
| 叶24 IMAX | 构造禁止退化为日内右尾；Jaccard/ρ 硬闸 |
| 叶25 cfacc_desens | 价量快 vs 会计慢分家；**禁复用**叶25 `.ok`（`7b279d47`/`be7f5e5a`）；窗冲突让路叶25 |
| 叶26 ETF 流 | 禁产品层份额流 / ETF↔指数映射进主信号 |
| v23 类 overnight「精神」 | who_pays/正文 **零**精神/情绪叙事关键词作主轴 |

覆盖闸（冻结后、读收益前计数；阈值不因结果调）：

- HI_LIQ：密封与 X2 各自 median 日可算 ivol 名数 **≥200** 且 **≥80%** 交易日 ≥200  
- FULLA：X2 median **≥500** 且 **≥80%** 日 ≥500  

---

## 6. 验收门（研究级叙述；本文件不跑）

- **A / A′**：拆分残差 ivol 的 IC/ICIR + 特质 α  
- **B**：中性后相对 capacity_adv（含 cap80+叶20）  
- **C**：本叶偏**快**（日/周），与 moneyflow 慢袖错配检查必做  
- **CMC / GATE_V3**：过门后才可议 Book-Smoke；衰减 KEEP；换手≤20%/日；两档 MDD≤25% 且净 CAGR>capacity_adv  
- **门B 并报**：Calmar 两档胜主干且 MDD≤15%  

研究级至少 A+A′；进 GATE_V3 / 派 Eng 须 A+A′+B+C。  
本文件 **不**申请 `.ok`、**不**跑自检、**不**读生产收益。

---

## 7. PIT 输入与禁读

| # | 输入 | 备注 |
|---|---|---|
| 1 | 日频 OHLC / 复权价 | 实现 sha 在独立窗重钉 |
| 2 | 停牌 / 涨跌停旗 | §2.4；回执披露旗名 |
| 3 | SW L1 PIT | 与叶25/26 同族契约 |
| 4 | log 流通市值 PIT（T−1） | 缺则不得静默用 T |
| 5 | 510300 日收益（β） | §2.2 |
| 6 | capacity_adv 暴露/活跃指示 | 缺则记 GAP |
| 7 | 可选结构字段名 `overnight_ret`,`intraday_ret`,`on_minus_id` | **须重钉实现 sha**；不得假设与本公式字节级一致 |
| 8 | 叶18/18v/叶24 α（若盘面仍在） | 仅供正交残差/Jaccard，不进主信号合成 |

**禁读作主轴**：个股 `moneyflow_stock_daily_pit`；ETF 份额流（叶26）；financials/应计（叶25/候选3）；卖方/金股/一致预期。

---

## 8. 交闸时点与非动作

| 里程碑 | 条件 |
|---|---|
| 本 r1 FROZEN | 本文件落盘（sha 见文末） |
| 申请本叶独立 `.ok` | Arch 审脚本 + Data 确认 OHLC/市值/SW/停牌涨跌停旗契约之后；**另窗**；不复用叶25 钉 |
| 叶25 窗 | **10:00–10:45 ET 优先**；冲突时本叶排队 |
| X2 / Alpha 闸 | 独立回执后；WATCH/FAIL 不交 ACCEPT |
| 质量应计（候选3） | **等叶25 闸**；本文件不开 |

**非动作**：不申 `.ok`；不改脚本；不读生产收益选参；不改 `alpha_labels`；不派 Eng/Book-Smoke；不碰纸面；不改 TEAM_STATE；不 git commit。

---

## 9. 失败条件（摘要）

覆盖闸失败；同构硬拒（§4–§5）；ρ_excess>0.5 对兄弟主叶；不可交易；衰减非 KEEP；Gate A/B/GATE_V3 不过；跑不赢主干；who_pays 精神化；冻结后翻号 → WATCH/DONE_FAIL，不派 Book-Smoke。

---

## 10. FROZEN 钉

| 项 | 值 |
|---|---|
| 路径 | `docs/v2/AI_LEAF27_OVERNIGHT_IDIO_IVOL_PREREG_r1.md` |
| 状态 | **FROZEN** |
| 冻结时刻 | 2026-10-25 06:11:04 ET America/New_York |
| 方向 | `α_raw = −ivol` |
| β | 510300 · 60 会话 · 最少 40 |
| W | 20 会话 · 最少 15 |
| live | false |
| promotion_approved | false |

**sha256**（整文件）：以本文件 `sha256sum` 为准（文末为去末行正文 hash）。

`32243b746c40d05bb051101aa615b370614d992aec6e8522888ef9cf41c696ff`
