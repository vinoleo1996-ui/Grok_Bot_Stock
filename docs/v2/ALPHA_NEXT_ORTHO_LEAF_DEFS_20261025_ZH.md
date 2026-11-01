# 下一批正交叶 · 残差/正交定义预写（Alpha）

- **日期**：2026-10-25 ET · America/New_York  
- **作者**：QuantLab Alpha（定义所有权在 Alpha；**who_pays 正文由 AI 交**）  
- **锁**：`promotion_approved=false` · `live=false` · 禁 GP / 卖方 / 金股 / 一致预期  
- **注**：叶25（`g1g5_ashare_cfacc_desens_cs_v1`）正在等 Arch **新窗 .ok**→AI 跑→Alpha 闸；**本文件不替代叶25 预注册**，也不消费旧 `R5_v2.ok`。

验收总闸（三条共用）：研究级至少 **A+A′**；进 GATE_V3/派 Eng 须 **A+A′+B+C**（见 `ALPHA_ACCEPT_PARADIGM_RESID_NEUT_ZH.md`）+ 叶验收 v2 + `GATE_V3_MDD25_PREREG_ZH.md`（cap80+叶20；两档 MDD≤25% 且净 CAGR>capacity_adv；衰减 KEEP；换手≤20%/日）。门B 并报（Calmar 两档胜主干且 MDD≤15%）。

正交硬闸（三条共用）：相对 **capacity_adv** 与已 RESEARCH_ACCEPT/WATCH 腿，活跃集 Jaccard **均≪0.7** 且 **frac(Jaccard≥0.7)=0**（≥0.7∧近等权→换皮硬拒）；须报残差 ρ；伪耦合（ρ 高且叠加≈加权和）→ CMC 不得 PASS。

残差化最低清单（三条共用，同日截面）：**SW L1 demean + log 流通市值 OLS 残差 + 滚动β**；并相对 **capacity_adv 暴露/活跃指示** 再正交一层（缺则记 GAP，不得静默跳过）。

---

## 叶候选 1 · ETF 资金流（宽基/行业 ETF）

### 机制一句话
ETF 份额增减或 ETF 端资金流刻画**产品层再配置压力**向成分股/行业的传导；对手盘是忽视 ETF 被动/半被动流量的个股定价——**不是**个股 `net_mf_amount` 换皮。

### PIT 输入候选
- `data/v2/etf/*`、fund 份额/净值日更、`fund_daily`（以 Arch/Data 已 ACCEPT 或可钉 sha 者为准；冻结前重钉）  
- 成分映射：宽基/行业 ETF→持股或官方权重的 **as-of** 表（禁未来成分）  
- 辅：SW L1 PIT、log 流通市值、trade_cal  
- **禁读**作主轴：个股 D2 `moneyflow_stock_daily_pit`（与 moneyflow_resid 分家）；卖方/金股/一致预期

### 残差化清单
1. 原始：ETF 份额 Δ 或资金流强度（PIT `available_at≤session`）→ 映射到股票/行业暴露  
2. SW L1 demean  
3. vs log 流通市值 OLS 残差  
4. vs 滚动β  
5. vs capacity_adv 暴露  
6. 披露 vs moneyflow_resid / etf_core / resid_etf / idx_rebal_flow 的 Jaccard 与 ρ

### 正交硬闸
- vs moneyflow_resid：机制必须是 **ETF 产品层**，个股 moneyflow 不得进主信号  
- vs etf_core：不得退化成「直接持有 ETF≈0.70」；本叶是流量→股票暴露  
- vs resid_etf / idx_rebal_flow：禁份额流×残差旧构、禁调样事件窗换皮  
- Jaccard/ρ 阈值同上共用闸

### who_pays 空位（等 AI）
> 〔AI 填写：一句 who_pays + mechanism_tag + 可检验预测/失效条件；交 Alpha 时点〕

### 验收门
A/A′（ETF 流量残差 IC/ICIR + 特质α）→ B（中性后相对 capacity_adv）→ C（快慢：ETF 流多为日/周，须标快慢标签）→ CMC / GATE_V3；过门后才可议 Book-Smoke。

### 禁项
个股 moneyflow 换皮；etf_core overlay 双计；无 PIT 成分；小盘主线；GP；把 Data 探针当 ACCEPT。

---

## 叶候选 2 · overnight−intraday / idiosyncratic vol

### 机制一句话
把收益拆成隔夜/日内或剥离系统因子后的**特质波动/拆分残差**，捕捉价量微观结构错价；**允许的是可复现的价量拆分与残差**，不是叙事「隔夜情绪/精神面」。

### 与历史硬禁的边界（必读）
- 历史曾 **硬禁 overnight「精神」类叶**（如 v23 类叙事）。  
- **本定义允许**：`overnight_ret` / `intraday_ret` / `on_minus_id` 等**价量拆分后的可计算量**，再经行业·市值·β 残差化后的特质波动或拆分残差排序。  
- **本定义禁止**：无公式的 overnight 情绪/精神/叙事主轴；禁把「隔夜精神」写进 who_pays。

### PIT 输入候选
- 日频 OHLC / 复权价（`research/adj_price` 口径）；停牌/涨跌停旗  
- SW L1 PIT、log 流通市值、滚动β（市场或 510300）  
- 可选：已有结构叶字段 `overnight_ret`,`intraday_ret`,`on_minus_id`（方向库已列名，须重钉实现 sha）

### 残差化清单
1. 定义拆分量（例：`r_on`, `r_id`, `r_on−r_id`）或 idiosyncratic vol（对市场/行业回归残差的滚动 σ）  
2. SW L1 demean → log 市值残差 → 滚动β 残差  
3. vs capacity_adv  
4. 方向须预注册（高 idio vol 惩罚 vs 奖励不可事后切换）

### 正交硬闸
- vs expand / 相对强弱：禁用未残差的隔夜收益当动量换皮  
- vs 已禁 overnight 精神叶：who_pays 不得出现精神/情绪叙事关键词作主轴  
- Jaccard/ρ 共用闸；须报与叶24 类微观结构叶的相关（若并发）

### who_pays 空位（已填·Alpha 2026-10-25 06:02 ET）
> **mechanism_tag**：`g1g5_ashare_on_minus_id_idio_ivol_v1`（叶27）  
> **who_pays**：付钱的是忽视 `on_minus_id=r_on−r_id` 经 SW L1·log 市值·滚动β·capacity_adv 残差后的滚动 σ(ε) 所刻画的开盘跳空相对连续竞价冲击错配、从而在高 σ(ε) 一侧过度承接流动性的对手盘（**价量公式，禁精神/情绪叙事**）。  
> **状态**：DRAFT 空位 **PASS_WITH_CONDITIONS**；方向 **UNFROZEN**（禁读收益选向）；详见 `ALPHA_LEAF27_WHO_PAYS_SLOT_FILL_REVIEW_20261025_ZH.md`；AI 草稿 sha `4a0eec1a…`。叶25 优先；本叶不申 `.ok`。

### 验收门
A/A′→B→C（本叶偏**快**，与 moneyflow 慢袖错配检查必做）→ CMC/GATE_V3。

### 禁项
overnight「精神」叙事；无残差 Top-N 等权当闸；高杠杆/隔夜杠杆产品；GP；与 v23 已 REJECT 精神同构重开。

---

## 叶候选 3 · 质量应计（与叶25 / leaf19 / accrual_quality 的差异）

### 机制一句话
应计质量的**另一正交切片**（须在预注册写死公式），专打「盈余中应计成分被误定价」；不得与叶25 cf accruals desens、leaf19 cfacc_rnoa、accrual_quality（Sloan WC）同构。

### 与既有应计家族的差异与正交要求

| 包 | 要点 | 本候选必须多出来的正交 |
|---|---|---|
| accrual_quality | BS 营运资本应计 / TA；WATCH/DONE_FAIL | **禁**同 WC/TA 主轴重开 |
| leaf19 cfacc_rnoa | 现金流应计×RNOA 族；WATCH | 公式/版本规则须可区分；残差池须**纳入 leaf19 α**（同 leaf25 思路） |
| 叶25 cfacc_desens | TTM NI−CFO 应计脱敏（预注册 r5 DRAFT，**未跑完**） | **等叶25 闸门结论后**再定是否还开本候选；若开，须对叶25 α 残差化且 Jaccard 硬闸 |

**建议默认**：叶25 未出 Alpha 闸前，本候选只保留定义位，**不派 AI 产权**。

### PIT 输入候选
- `financials_pit` / `cashflow_pit` / `balancesheet_pit`（列与 available_at 规则跟 Arch 钉；禁 `fina_indicator` 非 PIT 快照）  
- SW L1、log 流通市值、滚动β、capacity_adv  
- **禁**：卖方盈余质量评分、金股、一致预期

### 残差化清单
1. 预注册应计原始量（须 ≠ WC/TA 单纯复制，且 ≠ 叶25 已写死 TTM 差分）  
2. SW L1 + log 市值 + 滚动β  
3. **强制**对 leaf19 α、accrual_quality 信号、（若已 ACCEPT）叶25 α 做同池残差或活跃集 Jaccard 闸  
4. vs capacity_adv

### 正交硬闸
- 家族 n 计数披露（leaf19 + accrual_quality + 叶25 + 本叶）  
- Jaccard/ρ 共用闸；任一对兄弟叶触发 ≥0.7∧近等权 → 拒  
- 版本规则（earliest vs latest as-of）若与叶19/25 不同须正文写明

### who_pays 空位（等 AI）
> 〔AI 填写：一句 who_pays + 与叶25/19/accrual_quality 的公式差一张表 + mechanism_tag〕

### 验收门
A/A′→B→C（会计叶偏**慢·季频**）→ CMC/GATE_V3；Book-Smoke 仅在组合门路径需要时由主 Agent 派 Eng。

### 禁项
与叶25 抢跑/混 .ok；fina_indicator 非 PIT；Sloan WC 换皮；在叶25 WATCH/REJECT 前平行开同族第二烟；GP。

---

## 调度备注（给主 Agent）

1. 资源冲突时 **叶25 优先**（TEAM_STATE AI 条已写）。  
2. 本文件三条是 Alpha 残差定义骨架；AI 交 who_pays 后 Alpha 才开 ACCEPT 闸。  
3. moneyflow_resid 叠仓：研究披露见 `ALPHA_MONEYFLOW_8020_GATE_DISCLOSE_20261025_ZH.md`；Leo 已否 80/20 晋级——**停推**；与本文件不互替。
