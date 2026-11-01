# QuantLab 原仓精髓 → V2 可复用清单

> 写于 2026-10-10（America/New_York）  
> 立场：能抬研究年化的都进**可选菜单**，按贡献调权重；主 β 仍 **510300**；`promotion_approved=false`。  
> 性质：拆零件、对照臂、研究开关——**不是**整包晋升、不是已验证可实盘绩效。  
> 主证据：`docs/STRATEGY_SCORECARD_2026-09-30.md`、`docs/PHASE1_GATE_20261008.md`、`docs/trial_ledger.csv`、`docs/prereg/*`、`QuantLab-READTHROUGH.md`、`qlab_b/`、`rev/`。

---

## 0. 一句话精髓

原仓真正值钱的不是「某一条已达标主策略」（可交易候选 = 0），而是三层积木：

1. **收益来源菜单**：微盘宽篮/M2 卫星、TURN 低换手因子、转债双低、（可选）海外黄金/ETF 腿——各自有账本数字，可按贡献加权进袖套。  
2. **执行与风险机器**：现金股数账本、LW 目标波动配权、P2 回撤阶梯、涨跌停/整手/成本、D1/流动性掩码、预注册+试验台账。  
3. **研究纪律**：先预注册再跑、族内计次、对照臂不冒充主结论、失败账本保留。

V2 该做的是：**主 β=510300 + 残差凑 β0.70 + 可选卫星/因子菜单**，用原仓机器量贡献，而不是再搜一次「微盘圣杯当主线」。

---

## 1. 可复用收益来源（按对 V2 研究年化的期望贡献排序）

均为条件性研究结果；数字来自原仓记分卡/闸门/台账，**不可当晋升绩效**。

| 秩 | 来源 | 历史关键指标 | 数据依赖 | 接入 V2 方式 | 期望贡献 |
|---:|---|---|---|---|---|
| **1** | **50 只 / 连续宽篮（ADV 尾部池，约 3001–5000 名）** | 拼接参考约 **15.10%**；连续宽篮 **13.84% / MDD −21.34%**；补 2018 宽篮 **14.63% / −22.45%**；三段多为正。选股 alpha≈0（同池等权常更强）——收益主要来自**池子风格**，非排序。 | 日额/amount、流通市值、ST、上市天数、整手账本；PIT 财务可选 | **Beta 卫星（`smallcap_satellite` 的股票版 / 50 篮对照臂）**：从 ETF 预算内切一小份，或独立风格袖套；权重由贡献菜单调，**不抬 `max_etf`、不改主 β=510300** | **高（抬年化主候选）**；容量/流动性/2025 末段塌陷需并排对照 |
| **2** | **TURN（20 日均换手，方向负；市值+行业中性）** | 发现段闸门 **pass**：IC t≈**10.2**，扣费超额约 **+3.7%/年**，6/9 年为正；增量 t≈4.5。对 SMB+HML 回归后截距 t≈−0.05（仍偏小盘/价值暴露）。TURN50 规模配对组合 **未过**（约 2% vs EW 9%，alpha t≈−1.5）。 | 换手率 PIT、行业、流通市值、PB（做对照时） | **Alpha 因子**：进 P1 因子库，中性/正交后加权；**不要**单独当 50 只选股圣杯（TURN50 已否） | **高（截面 alpha 最干净的过关信号）** |
| **3** | **M2 小盘对照篮（R 池后 40% ADV + 财务档 + 50 只等权）** | 账本中位成本×1：**10.83% / −29.7%**；成本×2：9.45%；确认段弱确认 1.53%/−29.2%（同期中证2000 −11.2%） | 同宽篮 + `float_mktcap`、PB/净利润 PIT | **Beta 卫星构造器 / Strategy 对照臂**：ETF 代理（512100/510500）已有开关；真·50 股篮需 Strategy 接 `smallcap/universe.py` 选池 | **中高**；回撤约 −30% 超 25% 预算 → 只能小权重卫星 |
| **4** | **可转债双低 CB_DL20** | 腿闸门 pass：CAGR **10.93%** vs 000832 **5.82%**；成本×2 仍 10.10%；MDD −29.6%。周频版 **13.83% / −21.6%**（规则变更前后分裂需披露） | 转债日线、溢价率、退市/强赎、账本 10 张一手 | **Strategy 可选 overlay 袖套**（资产类，非股票 Alpha）；与 510300 低相关时作分散 | **中**（抬组合年化/降相关）；需 CB 数据晋级 |
| **5** | **T3：M2 + 511260 风险平价开关** | 相对 M2：dCAGR **+0.61pp**，dMDD **+4.75pp**（10/10 路径）；全组合复核未采纳（dCAGR −0.10） | 国债 ETF 511260、M2 路径 | **Beta/Strategy 风险预算 overlay**：卫星开启时用国债对冲尾部，不改主 β 目标 | **中（控回撤为主，年化次之）** |
| **6** | **价量族其余信号（REV/IVOL/MAX/TREND；ATURN 失败）** | 仅 TURN 过主门槛；ATURN 净 −1.0%/年 | 同 TURN | **Alpha 候选池**：作正交残差诊断，默认权重 0，直到复现过关 | **低～中** |
| **7** | **海外股指 + 黄金被动腿 / ETF 轮动** | 预注册为低相关来源；收益本质是资产涨幅非选股 alpha；发现段美股黄金偏顺风 | QDII/黄金 ETF 日线 | **可选多资产袖套**（研究菜单）；A 股 Mandate 内慎用容量与 QDII 溢价 | **低～中（分散，不保证抬 A 股年化）** |
| **8** | **12-1 动量（qlab_b）** | 预登记在 120 只冻结池上的挑战者；小样本信号测试 | 复权收盘 | **Alpha 动量因子**（已部分在 V2 P1）；勿用 120 池结论外推 | **低～中** |
| **9** | **专家路由 / quality·PB 主策略** | 专家长段约 **10.80% / −25.3%**；quality/PB+P2 约 **0.63%** 或 2025 新账户 **−2.94%** | 财务 PIT、专家分 | **Alpha 遗留对照**；可拆因子进 P1，**禁止**整包当主线 | **低（已退出候选）** |
| **10** | **题材图谱 / 价格因子臂** | 同池不打分 13.67%（不可采用）；题材 12.84%/−35.84% 退出；价格因子 9.78% 退出 | 概念快照（非 PIT）等 | 观察即可；概念快照前视风险高 | **低 / 暂避** |

### 菜单用法（Leo 定调）

- 主 β：**510300**（不变）。  
- 卫星/腿：宽篮·M2·转债·国债对冲·（可选）海外黄金 —— **贡献加权**，默认小权重或关。  
- Alpha：优先接 **TURN**，再扩 REV/IVOL/低波/流动性；与 P1 中性/正交/walk-forward 对齐。  
- 对外主结论仍认 **Full D1 + 成本**；250 池 / 无成本烟测不当主结论。

---

## 2. 可复用风险 / 执行机器（带路径）

| 能力 | 路径 | V2 用途 |
|---|---|---|
| **现金·股数·费用账本** | `quantlab/backtest/ledger.py`（+ `tax.py`） | 唯一可信净值源；订单是意图，成交才改现金/持仓；涨跌停/停牌估值缺口 |
| **回测引擎** | `quantlab/backtest/engine.py` | 信号收盘 → 次日开盘；与 V2 paper runner 对齐成本语义 |
| **LW 收缩协方差 + 目标波动配权** | `quantlab/strategy/portfolio.py`（`ledoit_wolf_cov`, `target_vol_weights`） | Strategy 残差仓配权；行业上限 + 降杠杆到目标 vol |
| **预期收益分配 + 换手费** | `quantlab/strategy/allocation.py` | 显式换手/退出约束下的再平衡 |
| **回撤阶梯（P0）** | `quantlab/strategy/risk.py` | 10/15/18/20% 诊断与对照 |
| **动态风险政策 P1/P2** | `quantlab/strategy/risk_policy.py`（`PolicyController`, `RiskBudget`） | MA60/波动状态 + 12/18/22/25% 阶梯；**注意**：P2 对 P1 曾约 −2pp，外部 drawdown_scaler 亦净损——作**可选开关**，默认勿激进永久停机 |
| **风险卖出取整** | `quantlab/strategy/risk_trades.py` | 避免为几元缺口机械卖整手 |
| **因子中性化** | `quantlab/factors/neutralize.py`（+ `orthogonalize.py`, `industry.py`） | Alpha P1 标配：行业去均值 + 市值分位 |
| **价量中性检验脚本** | `scripts/neutral_alpha.py`、`scripts/p1_b_turn50.py` | 复现 TURN / 壳价值判定 |
| **小盘池与选篮** | `quantlab/smallcap/universe.py`, `layers.py`, `panel.py`, `sim.py` | 卫星 50 篮 / M2 对照；快仿 vs 正式账本要对齐 |
| **正式账本回放** | `scripts/stable_book.py`（`replay_account`） | 卫星/对照的权威成本口径 |
| **ETF/多资产账本** | `quantlab/etf_account.py` | 转债腿、国债腿、海外腿 |
| **拥挤度** | `quantlab/strategy/crowding.py` | 卫星仓位上限/降档输入 |
| **机会模块（因果价量）** | `quantlab/strategy/opportunity.py` | 研究侧车；须冻结预测，不作静默主策略 |
| **试验台账 + 预注册** | `docs/trial_ledger.csv`, `docs/prereg/*`, `quantlab/research_trials.py` | 每改菜单计次；DSR/族校正 |
| **指标与诊断** | `quantlab/report/metrics.py`, `research_diagnostics.py` | CAGR/Sharpe/MDD/换手/成本分列 |
| **数据集契约 / PIT** | `docs/DATASET_CONTRACT.md`, `quantlab/data/contracts.py`, `data_os/pit.py` | Data 晋级门槛 |
| **V2 已落卫星开关** | `docs/v2/BETA_SMALLCAP_SATELLITE.md`, `quantlab/beta/satellite.py` | ETF 代理卫星（默认关）；真·股票宽篮待接 |

---

## 3. 具体 Port List（Alpha / Beta / Strategy）

> effort：S ≤1–2 日 · M ≈3–5 日 · L >1 周（含数据/对照）

### Alpha

| # | 原文件 / 函数 | 目标 V2 模块 | effort | 备注 |
|---|---|---|---|---|
| A1 | `scripts/neutral_alpha.py`（TURN 定义与中性化） | `quantlab/factors/p1_factor_lib.py` 增 `turn_20d` | S | **优先**；方向负；接已有中性管线 |
| A2 | `quantlab/factors/neutralize.py` | 已部分在 V2；对齐申万 L1 PIT | S | 无申万则退化为证监会门类/sector 首字母 |
| A3 | `quantlab/factors/orthogonalize.py` + walk_forward | `p1_pipeline` / `walk_forward.py` | S–M | TURN 与动量/EP 正交后再加权 |
| A4 | P1-B：REV / IVOL / MAX | `p1_factor_lib.py` | M | 默认权重 0，先复现 IC 闸门 |
| A5 | `qlab_b/strategy.py` 12-1 动量 | 已有动量因子则做口径对齐 | S | 跳过近 1 月的 12-1 |
| A6 | `quantlab/strategy/experts.py` / `scoring.py` 可拆因子 | 因子卡文档，不整包路由 | M | 专家路由整包已弱，只拆零件 |
| A7 | `quantlab/strategy/opportunity.py` | 研究侧车信号，不进主决策除非预注册 | L | 需冻结预测身份 |

### Beta

| # | 原文件 / 函数 | 目标 V2 模块 | effort | 备注 |
|---|---|---|---|---|
| B1 | `docs/v2/BETA_SMALLCAP_SATELLITE.md`（已有） | 保持默认 **OFF**；菜单贡献权重 | — | 主 β=510300 |
| B2 | `quantlab/smallcap/universe.py`：`pool_on` / `select` | `beta/satellite.py` 或 `strategy` 股票卫星 | M–L | 真·50 篮；先对照 ETF 代理 |
| B3 | `scripts/p1_m2.py` + `P1_M2_SMALLCAP_CONTROL.md` | 对照臂配置 JSON | M | 报告用，不设采纳门槛 |
| B4 | `scripts/p1_a_position.py` 四条仓位规则 | 可选「卫星仓位缩放」开关 | M | A 腿合成择时**未过闸**；可作诊断，默认不用合成开门 |
| B5 | T3：M2+511260 风险平价（台账 pass） | `beta` 风险预算 overlay | M | 卫星开时降回撤 |
| B6 | `residual_weight_to_hit_target_beta`（已交） | Strategy 组合层 | S | 方案 C：凑组合 β≈0.70 |

### Strategy

| # | 原文件 / 函数 | 目标 V2 模块 | effort | 备注 |
|---|---|---|---|---|
| S1 | `quantlab/strategy/portfolio.py`：`target_vol_weights` | `portfolio/v2_constructor.py` 残差仓 | M | LW + 行业上限 + 目标 vol |
| S2 | `ledger.py` 成本语义（佣金/印花税/滑点/整手） | `v2_execution_costs.py` / Full D1 主跑 | M | P0 成本对照主路径 |
| S3 | `risk_policy.py` 回撤阶梯 | 可选 `RiskBudget` 接入 paper | M | 默认温和；忌 25% 永久停机僵局 |
| S4 | `scripts/stable_book.py` 相位中位数报告 | 卫星/宽篮对照报告模板 | S | 多相位中位，禁选幸运相位 |
| S5 | `etf_account.py` + `P2_CB_DOUBLE_LOW` | 可选转债袖套 runner | L | 数据就绪后再开 |
| S6 | 固定权重多腿（参考差距审计 §2） | 组合层 `fixed_sleeve_weights` | M | 微盘卫星 vs 510300 固定配比，降相位敏感 |
| S7 | 错峰子组合 + 只交易净差额（差距审计 §3） | 再平衡执行层 | L | 降换手；与双周/月频 Mandate 对齐 |
| S8 | `trial_ledger` / prereg 模板 | 每次菜单改动登记 | S | 保持 `promotion_approved=false` |

### 建议落地顺序（与急救方案对齐）

1. **P0**：Full D1 + 成本 + 涨跌停（已在跑）→ 主结论只认这份。  
2. **A1–A3**：TURN 接入 P1 并进主回测对照。  
3. **B1+B6+S1**：残差 β + LW 配权；卫星 ETF 开关做并排臂。  
4. **B2/B3**：股票宽篮/M2 对照臂（小权重菜单）。  
5. **S5/S6**：转债与固定多腿——数据与成本稳定后再开。

---

## 4. 该避开什么（简短）

| 避开 | 原因 |
|---|---|
| 把 **15% 宽篮/拼接参考** 写成已晋升主策略 | 可交易候选=0；池子效应≠选股 alpha；分红/前向/执行门未过 |
| **TURN50 当独立选股产品** | 规模配对后超额转负，闸门失败 |
| **A 腿合成 ETF 择时当默认** | 回撤只砍 24%＜30% 门槛；不通过 |
| **quality/PB 或专家路由整包装主线** | 全段年化远低于目标或已退出候选 |
| **题材图谱（当前概念快照）** | 非 PIT；回撤超预算 |
| **激进 P2 永久 25% 停机** | 易陷入长期全现金；外部/本仓均显示硬缩放常净损收益 |
| **调参救门槛 / 选幸运相位** | 相位差可达数个点～十余点；必须多相位中位 |
| **无成本短窗 250 池当对外数字** | 已证明美化；主结论用 Full D1+成本 |
| **改 Mandate 抬 `max_etf` 硬凑 β** | 应用残差仓方案 C；主 β 定义不动 |
| **rev/ 小样本 ～14% 实验当外推** | 池偏差大，仅机制参考 |

---

## 5. 给统筹的读法

- **有东西可用**——而且不少；精髓是「菜单 + 账本机器 + 纪律」，不是「一条已验证圣杯」。  
- 扭转研究年化的最大杠杆：**宽篮/M2 作小权重卫星（秩1）+ TURN 进 Alpha（秩2）+ 成本与 β 实现做对（机器层）**。  
- 全程研究级；贡献权重大小可以随机应变，**主 β 与晋升旗标不能随机应变**。

