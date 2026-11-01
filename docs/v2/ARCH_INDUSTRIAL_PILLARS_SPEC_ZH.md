# 工业级选股四支柱规格（Arch → Strategy / 全队）

- 起草：2026-10-14 ≈08:02 ET（Arch）
- 依据：Leo **07:56 ET** 工业级范式拍板（可交易池 + 分域 α + 组合优化器，**禁止 Top-N 主路径**）；Leo **07:58 ET** 前后对四门道的展开（股票池/分域、快慢因子、优化器硬软约束与拥挤度、双阈值死区与 3/2 冲击）；主 Agent 转发；双轨 **07:42**（FULLA=研究 / HI_LIQ=纸面候选）。
- 配套：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（Strategy，**DRAFT 非冻结**）；`ARCH_OPTIMIZER_CVXPY_SKFOLIO_TEMPLATE_ZH.md`（本轮可落地模板）；`ARCH_GITHUB_LANDSCAPE_20261014_ZH.md`；`BETA_BUDGET_MDD25_FOR_COMBO_ZH.md`；`audit/ARCH_SURVIVORSHIP_AUDIT_20261014_ZH.md`。
- **约束**：`live=false`；`strategy_promotion=false`；**禁 GP**；**不改** `FROZEN_CONFIG` / capacity_adv / B4 / S6 纸面轨；本文**只新增文档**，不跑优化器回测。
- 风险模型起点（与 Strategy **共签**）：**Ledoit–Wolf + 申万一级行业哑元**，再演进 Barra 类风格因子（见支柱③与模板文）。

---

## 0. 一句话

真正拉开「回测神话 vs 可活夏普」的，不是单个神奇因子，而是四个实战环节：

1. **股票池怎么切**（可交易过滤 + 分域 α + 跨池合成基准风格；锁非线性市值防杠铃）
2. **长短周期因子怎么拼**（慢因子定目标底仓，快因子做交易门控；残差/正交提纯）
3. **优化器约束怎么放缩**（硬约束锁尾部风险；软惩罚放有把握的风格；拥挤度进惩罚/Σ）
4. **调仓怎么防冲击与踩踏**（双阈值无交易死区 + \(3/2\) 次冲击 + 分步建仓）

QuantLab 现行主路径仍是 **Top-N / 固定袖套混合**（capacity_adv、B4）。Leo 07:56 要求主研发转向优化器路径；纸面 FROZEN **先不动**，研究轨按四支柱对齐。

---

## 1. 四支柱对照表

### ① 股票池与分域

| 项 | 内容 |
|---|---|
| **工业门道** | 可交易宽池过滤（剔 ST/停牌/次新/ADV 不足）→ **分域独立 α**（大盘动量 vs 中小反转等）→ 优化器把行业/β/市值 **合成到基准风格**；必须锁 **非线性市值（MidCap / Non-linear Size）** 防「一头超大 + 一头极微」杠铃；可选「基本面白名单 + 池内量价轮动」双层漏斗。 |
| **开源/业界锚** | 宽宇宙截面：qlib `market=all`、RQFactor `universe=None`、WorldQuant TOP3000 级流动性池（见 `ARCH_INDUSTRY_UNIVERSE_PRACTICE_ZH.md`）；风险侧非线性 Size 属 Barra 族常见项（演进目标，非 V1 伪造成熟 Barra）。 |
| **现状缺口** | FULLA_V1 已做可交易过滤（ADV≥300万）且历史含退市股 ✅；**无分域 α**（全池一把尺子）；纸面仍 mid_large top300 / HI_LIQ Top-N 袖套；**无非线性市值硬锁**；B4 线性混袖不是跨池合成基准风格；幸存者：引擎个股无退市清算（Arch S1 未落地）→ 宽池研究须标注风险。 |
| **建议负责** | Strategy（池/分域标签/域预算）· Alpha（分域慢 α）· AI（分域事件/快分）· Beta（MidCap 暴露定义共签）· Data（成分 PIT、退市日线合并）· Eng（退市 terminal） |
| **FULLA 研究轨** | 掩码继续作最宽可交易研究宇宙；分域标签在 FULLA 上打（D1 CSI300 / D2 CSI500∪1000 / D3 其余或市值后 30%）；**裸 FULLA 不进纸面**（Leo 07:42）。优化器研究可先在 HI_LIQ 子集上求解，FULLA 上做 α 诊断与分域贡献披露。 |
| **HI_LIQ 纸面双轨** | HI_LIQ_V1.1（ADV≥1亿，无市值筛，IND≤25% 为旧 Top-N absolute）作 **OPTIMIZER investable 候选**（Strategy DRAFT 方案 A）；优化器路径下行业改 **相对 \(w_b\) ± 带宽**，25% absolute 可降为兜底。纸面 FROZEN 仍跑旧 Top-N，直至 Leo 明示晋级。 |

### ② 多周期因子融合

| 项 | 内容 |
|---|---|
| **工业门道** | **慢因子（20–60d+ 基本面/中频）定目标底仓**；**快因子（1–3d 量价/事件）只做交易门控**（同向才加仓、逆向则暂缓）；进入合成前对行业+市值做截面残差，并对已有因子库正交，拿 **特质 α**。禁止「高频与低频直接加权求和」导致每天洗掉慢 Alpha。 |
| **开源锚** | alphagen「组合目标而非单因子 IC」思路（**不用其 GP/RL 生成器**，禁 GP）；qlib 滚动训练；RD-Agent hypo_critic（假设先批判）；残差正交为金工常识，QuantLab 叶侧已有部分残差腿可复用。 |
| **现状缺口** | 叶工厂大量事件/量价叶按单叶验收；B4 用 **50/25/25 线性混袖**（非慢底仓+快门控）；残差/正交不统一进组合层；leaf_selfcheck IC 有 `f.notna()` 丢退市标签风险（幸存者审计 S2）。 |
| **建议负责** | AI（快因子门控信号 + 残差快分）· Alpha（慢 α 全池向量，非 Top-25 权重）· Strategy（合成进优化器的接口）· Arch（验收门：禁止名次当 α） |
| **FULLA** | 慢/快 α 均在 FULLA 可交易掩码上算截面；报告分域 IC/贡献；门控逻辑研究可先 FULLA。 |
| **HI_LIQ / 纸面** | 优化器 V1：**仅慢残差 α 定 \(w^*\)**；快因子默认 **只门卫、不加通道量**（与 Strategy DRAFT §2 一致）。纸面 FROZEN 腿逻辑不改。 |

### ③ 优化器硬/软约束 + 拥挤度

| 项 | 内容 |
|---|---|
| **工业门道** | 尾部不可预测维度（β、线性/非线性市值）→ **硬约束**；有把握的风格（动量/波动/估值残差等）→ **二次软惩罚**，允许用一点风险预算换 α；在 Σ 或惩罚项中加入 **同行拥挤度**，避免 Barra 看不见的残差空间抱团踩踏。约束过死会压低 Transfer Coefficient。 |
| **开源锚** | Riskfolio-Lib（CDaR/MaxDD、风险预算）：https://github.com/dcajasn/Riskfolio-Lib ；skfolio（CPCV/walk-forward）：https://github.com/skfolio/skfolio ；PyPortfolioOpt / sklearn Ledoit–Wolf：https://github.com/PyPortfolio/PyPortfolioOpt 、https://scikit-learn.org/stable/modules/generated/sklearn.covariance.LedoitWolf.html ；cvxpy：https://www.cvxpy.org/ / https://github.com/cvxpy/cvxpy |
| **现状缺口** | 无显式 \(\Sigma\) 优化主路径；行业多为 absolute cap；无 MidCap 硬锁；无拥挤度；Beta MDD 预算目前在 **nav 层袖套** 上搜权重（B4 100%），不是持仓层优化器；回撤降β钩子默认关。 |
| **建议负责** | Strategy（求解与约束表）· Beta（硬/软参数与 \(\Sigma\) 共签、MDD≤25%/另报≤15%）· Arch（四闸审计、拥挤度代理可审计性）· Eng（约束违规检测进 book-smoke） |
| **\(\Sigma\) V1（共签）** | 可交易池内 \(L=120\) 日收益 → **Ledoit–Wolf**；+ **申万一级行业哑元**（或行业因子+对角特异风险）；**禁止**在未建成时声称完整 Barra。演进路线：+ Size / Non-linear Size / Momentum / Residual Vol 等风格因子后升格「Barra 类」，须 Arch+Beta dated 共签。 |
| **FULLA** | 宽池上估计 \(\Sigma\) 样本更全，但退市清算未落地前报告须打标；拥挤度代理可在 FULLA 上校准。 |
| **HI_LIQ / 纸面** | 优化器求解宇宙优先 HI_LIQ_V1.1；纸面 FROZEN 不接优化器输出，直至晋级预注册。 |

### ④ 双阈值无交易死区 + \(3/2\) 冲击与分步建仓

| 项 | 内容 |
|---|---|
| **工业门道** | 排序策略也绝非「掉出前 N 立刻全卖」：买入线/持有线 **双阈值** 形成无交易死区（优化器对应 \(\lambda_1\|w-w_0\|_1\)）；冲击用参与率的 **\(3/2\) 次**（非固定费率），大单自动拆成多日平滑建仓。 |
| **开源锚** | pysystemtrade 持仓 buffer / 波动率目标：https://github.com/pst-group/pysystemtrade ；Lean 可插拔 Fill/Slippage：https://github.com/QuantConnect/Lean ；vnpy 4.5 VWAP/fill_price：https://github.com/vnpy/vnpy ；业界 Almgren 族常出现 \(q^{3/2}\) 型冲击（实现为优化内代理，终判仍走引擎）。 |
| **现状缺口** | 引擎 `sqrt_impact_cost`（\(\propto\sqrt{\mathrm{participation}}\)）已有，**优化内无 \(3/2\) 代理、无双阈死区、无 staged builds**；Top-N 掉名即卖；60万档按手稀释已知；impact 缺失时记 0（内审 P2）。 |
| **建议负责** | Strategy（死区/冲击参数分档写死）· Eng（与 strategy_v1 对齐标定、staged 执行、VWAP 敏感性）· Beta（换手/成本对 MDD 的边际） |
| **FULLA** | 研究可报「若无死区」对照；宽池小票冲击更敏感，须分 ADV 分位披露。 |
| **HI_LIQ / 纸面** | 优化器路径：**60万/100万分别标定**死区与 \(\kappa_{3/2}\)（Strategy DRAFT 表）；纸面 FROZEN 仍用现 cadence，不改。 |

---

## 2. 与 Leo 拍板的对齐清单

| 拍板 | 本规格落实 |
|---|---|
| 07:56 禁 Top-N 主路径 | 四支柱主研发 = 优化器；Top-N / B4 仅对照与纸面 FROZEN |
| 07:42 双轨 | FULLA=研究；HI_LIQ=纸面/优化 investable；裸 FULLA 不进纸面 |
| 07:48 ADV | FULLA≥300万；纸面 HI_LIQ≥1亿；all_a 200万退役 |
| 07:24 小盘可买 | 无市值剔除；小盘贡献仅披露；**仍锁 MidCap 暴露**（防杠铃 ≠ 禁小盘） |
| MDD≤25%（另报≤15%） | 组合验收硬关注；Beta 预算文档继续有效；优化器报告两档 |
| 禁 GP / live=false | 不引入 alphagen/AlphaGPT 生成器；不碰实盘 |

---

## 3. 派工摘要（供主 Agent 转发）

| ID | 交付 | Owner | 状态 |
|---|---|---|---|
| P1 | 确认/修订 `STRATEGY_OPTIMIZER_PREREG_DRAFT` → 待 Leo/主 Agent 改 FROZEN | Strategy | DRAFT |
| P2 | 按 `ARCH_OPTIMIZER_CVXPY_SKFOLIO_TEMPLATE` 实现研究脚本（**不改纸面**） | Strategy + Eng | 待开 |
| P3 | \(\Sigma\) V1 + β/Size/MidCap 硬约束可实现性共签 | Beta + Arch | 待签 |
| P4 | 慢 α 全池残差向量；快因子门卫接口 | Alpha + AI | 待开 |
| P5 | 退市清算 S1 + 日线并退市库（宽池前提） | Eng + Data | 已派，未完 |
| P6 | 拥挤度 V1 代理可审计定义 | Arch + Strategy | 本模板定接口 |

---

## 4. 明确不做

- 不改 FROZEN_CONFIG / 纸面日终逻辑 / 密封窗起算。
- 不把优化器结果当晋级依据，直至预注册 FROZEN + 密封窗+X2 双档过门 + 共签。
- 不宣称完整 Barra；不虚构拥挤度「实盘借券数据」。
- 不恢复禁小盘；不把 MidCap 硬锁解释成「去掉小盘」。
- 不做 GP；不接 live。

---

## 5. 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:02 ET | Arch 初稿：四支柱对照 + 双轨接法 + 共签与派工。 |
