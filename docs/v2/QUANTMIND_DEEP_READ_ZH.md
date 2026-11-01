# QuantMind 源码深读（相对 QuantLab 因子工厂）

**日期**：2026-10-12 · America/New_York  
**上游**：https://github.com/qusong0627/QuantMind · ref=`master` · HEAD=`7d8019cac06e5f44de5f19b501481886535a6c32`（作者时间 2026-10-11 09:33 ET）  
**许可**：AGPL-3.0（根目录 `LICENSE`）— **不 vendor** 进 QuantLab  
**读法**：GitHub 远程只读（`get_file_contents` / raw）；**无 clone**；下文只引用路径+函数名+逻辑摘要  
**对照皮毛（勿复述为主文）**：`docs/v2/QUANTMIND_ADAPT_PLAN_ZH.md`、`QUANTMIND_ADAPT_RECEIPT_20261012_ZH.md`  
**门锁**：`promotion_approved=false`；不下单；不开密封；本侧 **不启 GP**；工厂搜索仍归 QuantLab AI；Alpha 只闸门/短清单  

---

## 1. 范围与读法

本次强制打开了三条链路的真实源文件（≥12）：因子演化（alphaagent + backend rd_agent wrapper）、截面推理（inference/）、回测（qlib_app + shared backtest_engine + trading_cost）。  
未读为「营销主结论」的 README 叙事；偶用目录树定位，逻辑一律来自 `.py`。

关键 blob（抽样可复核）：

| 路径 | blob SHA（master） |
|---|---|
| `alphaagent/app/qlib_rd_loop/factor_mining.py` | `21c8ef4e…` |
| `alphaagent/app/qlib_rd_loop/conf.py` | `36410bfb…` |
| `alphaagent/components/coder/factor_coder/evolving_strategy.py` | `701ae1c5…` |
| `alphaagent/components/coder/factor_coder/expr_parser.py` | `8dd09e1b…` |
| `alphaagent/components/coder/factor_coder/factor_ast.py` | `2d372821…` |
| `alphaagent/scenarios/qlib/developer/factor_runner.py` | `39f06cbd…` |
| `backend/services/engine/rd_agent/rd_loop_wrapper.py` | `a237f217…` |
| `backend/services/engine/rd_agent/market_adapters/a_share.py` | `97456aa9…` |
| `backend/services/engine/inference/batch_orchestrator.py` | `32868423…` |
| `backend/services/engine/inference/position_signal.py` | `0d29a778…` |
| `backend/services/engine/inference/neutralizer.py` | `afdbd816…` |
| `backend/services/engine/inference/trading_cost.py` | `c1517933…` |

---

## 2. 架构地图（路径级）

```
[假设] LLM HypothesisGen
   │  alphaagent/scenarios/qlib/proposal/factor_proposal.py
   │  AlphaAgentHypothesisGen / AlphaAgentHypothesis2FactorExpression
   ▼
[表达式] FactorTask.factor_expression + FactorRegulator(AST 近亲)
   │  factor_ast.py / expr_parser.py / regulator/factor_regulator.py
   ▼
[实现] FactorParsingStrategy → template.jinjia2 → factor.py → eval(expr) → result.h5
   │  evolving_strategy.py · function_lib.py · FactorFBWorkspace.execute
   ▼
[组合回测] QlibFactorRunner.develop → qrun conf*.yaml → IC / excess IR / MDD
   │  factor_runner.py · feedback.py（LLM 比 SOTA）
   ▲
[QuantMind 包装] RDLoopWrapper(a_share) 注入 QuantDB→daily_pv.h5、base_factors.json、中文 prompt
   │  rd_loop_wrapper.py · market_adapters/a_share.py · quantbot/rd_agent_launcher.py

─── 另一条生产链（模型，非表达式 GP）───
QuantDB 特征 → ModelLoader → batch_predict / BatchInferenceOrchestrator
   → Neutralizer(行业+log_cap) → position_signal(Top%/凯利) → engine_signal_scores
   → QlibBacktestService / shared BacktestEngine / inference BacktestService
```

三句话：**(1)** 因子挖掘主循环在 `alphaagent`（RD-Agent 风格 CoSTEER），**(2)** 生产截面分在 `backend/.../inference` 绑 **已训练模型 + QuantDB**，**(3)** 回测默认吃 **Qlib CSI300 宇宙 + Topk 类策略**，另有自研 `BacktestEngine` 做停牌/涨跌停过滤。

---

## 3. RD-Agent / AlphaAgent 因子演化（真实控制流）

### 3.1 入口与配置

- CLI：`alphaagent/app/qlib_rd_loop/factor_mining.py::main` → `AlphaAgentLoop(ALPHA_AGENT_FACTOR_PROP_SETTING, …)`；`USE_LOCAL` 决定本地 vs Docker 回测。  
- 配置：`conf.py::AlphaAgentFactorBasePropSetting`：
  - `scen` = `QlibAlphaAgentScenario`
  - `hypothesis_gen` = `AlphaAgentHypothesisGen`
  - `hypothesis2experiment` = `AlphaAgentHypothesis2FactorExpression`（**直接出表达式**，不是先写 Python 因子体）
  - `coder` = `QlibFactorParser`（解析/渲染模板，非自由写码为主）
  - `runner` = `QlibFactorRunner`
  - `summarizer` = `AlphaAgentQlibFactorHypothesisExperiment2Feedback`
  - `evolving_n` = 5  
- 产品侧包装：`backend/services/engine/rd_agent/rd_loop_wrapper.py::RDLoopWrapper` 默认 `market="a_share"`，实际调 **嵌入的 `rdagent.app.qlib_rd_loop.factor.FactorRDLoop`**（`rd-agent/` 树），并把 env（训练窗 2016→、valid/test 切分、LLM、workspace）钉死。

### 3.2 一步一步：假设如何变成表达式

`alphaagent/components/workflow/alphaagent_loop.py::AlphaAgentLoop` 五步：

1. **`factor_propose`** — LLM 出 `AlphaAgentHypothesis`（含 concise_specification）。  
2. **`factor_construct`** — `AlphaAgentHypothesis2FactorExpression.convert`：把假设变成多个 `FactorTask`，字段含 **`expression`**；经 `FactorRegulator.is_parsable` + `evaluate`（与 factor zoo 最大公共子树 / 自由参数数 / 唯一 `$` 变量数）。不可接受则把「重复子树」反馈再生成。  
3. **`factor_calculate`** — coder：`FactorParsingStrategy.implement_one_task`：首次把 `expr` 灌进 `template.jinjia2`；失败路径再让 LLM 改 `expr`。模板逻辑：读 `daily_pv.h5` → `parse_symbol`/`parse_expression` → **`eval(expr)`** → `result.h5`。  
4. **`factor_backtest`** — `QlibFactorRunner.develop`：拼 `combined_factors_df.pkl`，`experiment_workspace.execute(qlib_config_name=conf.yaml|conf_cn_combined_…)`。  
5. **`feedback`** — LLM 对照 Current vs SOTA 的 `IC`、`1day.excess_return_without_cost.{IR,annualized,MDD}`，决定是否 `Replace Best Result`。

表达式 DSL：`expr_parser.py` 把 `+ - * /` 改写成 `ADD/SUBTRACT/MULTIPLY/DIVIDE`，逻辑 `AND/OR`，三元 `np.where`；`function_lib.py` 提供 `DELTA/RANK/TS_*` 等 **截面/时序** 原语（按 `instrument`/`datetime` groupby）。`factor_ast.py` 做 AST 近亲（`find_largest_common_subtree` / `match_alphazoo`）——这是他们的「novelty」，**不是** QuantLab 的族 ρ / θ_cov。

### 3.3 数据如何进演化

`RDLoopWrapper._ensure_data_file`（A 股优先）：

1. 从 QuantDB parquet **生成** `daily_pv.h5`（MultiIndex datetime×instrument；列 `$open…$amount` + 白名单富化列：`rsi_14/pe_ttm/float_mv/netflow_*/bp/ep/ind_strength…`，见 `_ENRICH_FEATURES_DAILY` / `_ENRICH_L1`）。  
2. 失败则 copy 预置 `daily_pv_all.h5`。  
3. 软链 Qlib provider → `~/.qlib/qlib_data/cn_data`。  
4. `AShareAdapter.generate_base_factors_json`：给 LLM 一份「可仿写」种子——**含 Alpha158 风格兜底 + L2 日频近似表达式 + QuantDB 可直接 `$引用` 列说明**。

`AShareAdapter.get_data_config`：**`market="csi300"`**；描述字符串写明「CSI300，Qlib Alpha158 因子集」。回测费用默认 `commission_rate=0.001`、`limit_threshold=0.1`。

### 3.4 与 Qlib 的耦合点

- 因子值最终进 Qlib 组合回测 YAML（`conf.yaml` / combined），评估指标是 **Qlib 报表 IC + 超额收益（且 feedback 里用的是 without_cost 系列）**。  
- `FactorFBWorkspace.execute` 依赖本地 `daily_pv.h5` 与 `FACTOR_CoSTEER_*` 路径；超时默认 1200s。  
- `QlibFactorRunner` 里「与 SOTA 因子 corr>0.99 去重」**被 `if False:` 关掉**——近亲过滤实际靠 FactorRegulator 的 AST 阈值（默认 duplication_threshold=8），**不是** 截面相关硬闸。

### 3.5 他们解决什么问题 / 默认答案 / 为何不能照搬

| 问题 | QuantMind 默认答案 | QuantLab 为何炸 |
|---|---|---|
| 如何从自然语言到可回测因子？ | LLM→DSL 表达式→eval→Qlib | 无 `who_pays`；无残差 ICIR 双读；无 θ_cov/冲击 |
| 如何防教材重复？ | AST 最大公共子树 vs alpha zoo | 仍种子大量 Alpha158/动量波动模板；闸门后仍会冒出教科书叶 |
| 宇宙？ | **CSI300** + QuantDB 全市场特征混用 | 中大盘 ∩ 禁小盘主仓；CSI300≠我们的可交易宇宙 |
| 评估？ | IC + excess IR（常看 without_cost） | 必须净成本 + impact@60万∧100万 + `icir_eps_gate` |
| overnight / 开盘跳空？ | DSL 无硬禁 | 精神禁 overnight* / ind_rel_overnight |
| 谁付钱？ | 无字段 | Direction/`who_pays_zh` 硬约束 |

---

## 4. 截面批量推理

### 4.1 契约

- **离线批**：`inference/batch_predict.py::run_batch_inference`  
  - 强制 `metadata.data_source == "quantdb_factors"`（`model_qlib` 已废弃）。  
  - `ModelLoader` → `load_date_data`/`preprocess` → `BacktestService._predict` → CSV `{symbol,date,score}`。  
- **多日编排**：`batch_orchestrator.py::BatchInferenceOrchestrator`  
  - 交易日来自 **Qlib `day.txt`**（刻意不用可能缺表的 calendar DB）。  
  - lookback≤60 或 range≤300 交易日；并发≤5；幂等复用已有 run；输出 `window_meta.effective_independent_bets`（诚实暴露 N/H 重叠）。  
- **实时适配**：`data_adapter.py` 把 tick/bar 映射到 Qlib 列名，经 `HistoryBuffer` 算 MA/波动，缺特征 **填 0**——研究级可接受，密封级不可。

### 4.2 中性化

`neutralizer.py::Neutralizer.neutralize`：截面回归  
`Y ~ 1 + log(mkt_cap) + industry_dummies`，残差写回 feature。元数据来自 duckdb `official_factors.duckdb`（`stk_shares_raw` / `TRD_Dalyr` / `TRD_Co` ASOF）。  
对照 QuantLab Z 设计：`[log float mcap CS-z, SW_L1, shortlist_PRIMARY]`——**他们无 shortlist_PRIMARY 正交，也无残差 ICIR(ε) 作为晋级闸**。

### 4.3 Top-N / 仓位

- 策略模板 `strategy_templates/alpha_cross_section.py`：`RedisWeightStrategy`，**topk=50，max_weight=0.05，min_score=0**——典型教科书 TopkDropout 形状。  
- 生产仓位：`position_signal.py`  
  - 双门槛：行业分位≥0.80 **且** 全市场分位≥0.60 才非零；  
  - 融合权重 market/industry/board/cap；半凯利 + `p^3` 强度映射 → `position_score∈{0}∪[0.1,0.99]`；  
  - 市值档含 **微盘/小盘**（`<30亿`/`<100亿`）；北交所板别存在。  
  - 弱市：全市场正分占比 `<30%` → 全体 `position_score=0`。  

**问题思路**：他们要解决的是「模型分 → 可执行建议仓」；默认答案是 **百分位+凯利+板块/市值分层**。QuantLab 不能照搬：微盘/小盘入主仓路径与资本档冲突；无冲击成本闸；Top-50 等权/封顶与 ACTIVE 短清单（24+8）治理无关。

### 4.4 与训练模型的关系

截面分来自 **已落盘 production 模型**（metadata 钉死特征列与 `quantdb_dir`），不是当日 GP 表达式现场算。RD-Agent 挖出的因子要进这条链，必须再走「特征入库 → 再训练/拼接」——QuantMind 产品里这条桥很重，QuantLab **不应** 为接桥而 vendor 整仓。

---

## 5. 回测链路

### 5.1 引擎选择（三套并存）

1. **Qlib 组合回测（主产品）** — `qlib_app/services/backtest_service.py` + `backtest_service_runtime.py`：`StrategyFactory` / 模板 / pool_id→instruments 文件；`_qlib_universe` 兼容 csi300/all/文件路径；排除北交所有工具函数。费用路径可走 `cn_exchange.CnExchange`（佣金+最低5元+印花税）。  
2. **自研日频引擎** — `backend/shared/backtest_engine/core/engine.py::BacktestEngine`：显式 **停牌（volume=0）与涨跌停**（`get_price_limit_threshold`，含 ST 口径委托 `limit_pct`）；佣金/滑点参数化。  
3. **推理质量滚动评估** — `inference/backtest_service.py::BacktestService`：预测 vs 真实前瞻收益，IC/十分位/多头超额；`trading_cost.CostModel`（佣金 2.5bp、印花税 10bp、滑点 10bp、过户费沪市）；`exclude_limit_moves` 默认 True；基准默认 **等权宇宙** 而非指数。

AlphaAgent 因子环内的回测仍是 **Qlib YAML + mlflow 报表**（`factor_runner`），feedback 关键指标含 **without_cost**——这是密封叙事最危险的默认。

### 5.2 费用 / 涨跌停 / 停牌（源码有写的）

| 机制 | 在哪 | 备注 |
|---|---|---|
| A 股费率 | `inference/trading_cost.py`、`qlib_app/utils/cn_exchange.py`、`a_share.BacktestConfig` | 默认不完全一致（0.025% vs adapter 0.1%），产品层可 override |
| 涨跌停剔除 | `trading_cost.limit_threshold`；`BacktestEngine._can_execute_order`；推理回测 `exclude_limit_moves` | 有容差；ST/板块差异在自研引擎更完整 |
| 停牌 | `BacktestEngine` volume/收盘无效 | Qlib 路径依赖数据与 Exchange 实现 |
| T+1 | 模拟盘/文档层强调；因子环反馈不把它当硬闸 | QuantLab 资本档需自己的执行假设 |

### 5.3 与「教科书宇宙」的绑定

- 适配器硬编码 **csi300**。  
- 策略模板 Topk=50。  
- base_factors / fallback 大量 **K 线动量·波动·均线**（Alpha158 子集）。  
- 评估常看 **IC / without_cost excess**。  

这些默认叠在一起，正好是 QuantLab 已写进永久拒绝的「教材主攻」形状。

---

## 6. 真实数据与问题思路（相对 QuantLab 会直接 FAIL 的默认）

QuantLab 硬闸（见 `_context/QUANTLAB_FACTORY_CONTEXT_FOR_QUANTMIND.md`）：θ_cov=0.08 / θ_primary=0.15；impact+flat25@60万∧100万≥10%；ICIR(ε)>0；双读 gate vs posthoc；族 ρ soft0.35/hard0.50；禁 overnight 精神；禁擅自扩 ACTIVE primary；中大盘；PIT parquet。

| QuantMind 默认 | 在 QuantLab 的命运 |
|---|---|
| CSI300 宇宙 + Topk50 | 宇宙错；小票/拥挤未按资本档冲击测 → **FAIL impact** |
| 评估偏 IC / without_cost | 双读与净成本缺失 → **不能晋级**；易出现「事后 ICIR 虚高」类 EDGE_WARN |
| AST 近亲阈值=8 节点 | 不等于族 ρ；可与 ACTIVE primary 高相关漏网 → **FAIL ρ/θ_cov** |
| Alpha158/动量波动种子 | 教材主攻 → **novelty/方向闸拒绝** |
| QuantDB 预计算 `$pe/$bp/$netflow` 直接进式 | 若无 PIT as_of 对齐 → **数据专责 FAIL** |
| position_signal 含微盘/小盘档 | 禁小盘主仓 → **资本档 FAIL** |
| 无 `who_pays_zh` | Direction 契约 FAIL（仓内 `quantmind_loop` 已强制） |
| overnight 类价差无硬禁 | 精神禁 → **DEMOTE/REJECT** |
| LLM「Replace Best」当闸门 | 非残差 ICIR，不可作 ACTIVE 扩席依据 |
| Docker 整仓 / QuantDB Key / 实盘桥 | 永久拒绝（见 §8） |

**一句话问题思路**：QuantMind 解决的是「LLM 因子工场 + 模型截面生产 + Qlib 回测工作台」的产品闭环；QuantLab 解决的是「PIT 中大盘、残差可交易、硬闸短清单」。形状可学，默认答案几乎全部要换。

---

## 7. 融入 QuantLab 因子工厂的缺口清单

> 分工不变：**不启本侧 GP**；搜索归 QuantLab AI；Alpha 只闸门/短清单。下列「建议动作」是契约/闸门/出口，不是让 Alpha 代跑演化。

### P0（不做则接上必炸）

1. **评估双读缺失**  
   - QuantMind 有：Qlib IC / excess IR（常 without_cost）；LLM feedback。  
   - QuantLab 缺：把「候选 expr」强制跑 `icir_eps_gate` vs `icir_eps_posthoc` 对照出口。  
   - 动作：**ADAPT** — 任何从 QM 形状学来的候选，只认双读包字段；事后 ICIR 单独标 EDGE_WARN。  

2. **冲击×资本档未接**  
   - QM 有：费率模型、涨跌停剔除、position_score。  
   - QL 缺：impact+flat25@60万∧100万 与权重长表绑定的统一闸。  
   - 动作：**ADAPT** — 截面分→权重必须过 `validate_gate`/Book-Smoke 资本档；拒 CSI300-Topk 净结果当密封。  

3. **宇宙错误默认**  
   - QM：`a_share.py` → csi300。  
   - QL：中大盘 ∩ 可交易池。  
   - 动作：**REJECT** 默认宇宙；**ADAPT** 契约「score panel 必须声明 universe_id=mid_large」。  

4. **近亲定义错位**  
   - QM：AST 公共子树 /（已关闭的）corr>0.99。  
   - QL：族 ρ soft/hard + θ_cov + ACTIVE 叶共享检查。  
   - 动作：**ADAPT** — 可借鉴「最大公共子树」作 **软 novelty 提示**；晋级仍只认 ρ/θ_cov；与 v24 次席共享叶要显式 DEMOTE（已有实践）。  

5. **who_pays / 机制字段**  
   - QM：假设文本无「谁付钱」。  
   - QL：`quantmind_loop` / `rdagent_min_loop` 已要求 `who_pays_zh`。  
   - 动作：**ADAPT** — 继续强制；QM 风格假设若缺字段直接自拒。  

### P1

6. **截面分→权重长表出口**  
   - QM：`position_signal` + RedisWeightStrategy Topk。  
   - QL：`agents/factor_evolve` stub / Book-Smoke 槽仍弱。  
   - 动作：**ADAPT** — 学「百分位门槛」形状，但权重出口走 `session,instrument_id,weight` parquet；禁微盘档。  

7. **中性化 Z 不完全对齐**  
   - QM：行业+log_cap 回归。  
   - QL：Z 含 SW_L1 + shortlist_PRIMARY。  
   - 动作：**ADAPT** — 保留行业/市值 neut 思路；补 PRIMARY 正交后再报 ICIR(ε)。  

8. **表达式 DSL ↔ QuantLab 叶语言**  
   - QM：`function_lib` RANK/TS_* + `$` 列。  
   - QL：自有 primitives / structural leaves。  
   - 动作：**延后** 全量翻译；**ADAPT** 仅文档级对照表，禁止把 `eval(expr)` 运行时搬进专有树。  

### P2

9. **多日推理窗口诚实元数据**  
   - QM：`effective_independent_bets` / overlap_ratio。  
   - QL：可学。  
   - 动作：**ADAPT**（低优先级）写入 handback 包 meta。  

10. **停牌/涨跌停执行过滤**  
    - QM 自研引擎已写清。  
    - QL Book-Smoke 需确认同口径。  
    - 动作：**ADAPT** 对照清单，不换引擎。  

11. **base_factors 种子治理**  
    - QM 主动喂 Alpha158/L2 近似。  
    - 动作：**REJECT** 作主种子；若 AI 工厂要「仿写范例」，只用仓内 Direction 库叶。  

12. **检查点/会话恢复**  
    - QM：`AlphaAgentLoop.load` / batch reuse。  
    - 动作：**延后** JSON meta 即可（皮毛文档已述）。  

---

## 8. 永久拒绝清单

- **Vendor** AGPL 源码进 QuantLab 专有树（含 `rd-agent/`、`alphaagent/` 整树拷贝）。  
- **Docker 整仓** / 一键 compose 当主研究路径。  
- **QuantDB Key / 默认 300+ 维特征包** 绑死为主数据（契约可学，Key 不绑）。  
- **用 Qlib 引擎替换** `v2_multisleeve_book` / Book-Smoke 主书。  
- **Alpha158 / 动量·反转·低波·EP/BP** 作主 Top-K 结论。  
- **CSI300-Topk50 / 微盘主仓** 当可晋级结果。  
- **实盘桥**（通达信/QMT/`qmt-bridge-kit.zip`/`bridge/`）默认启用。  
- **本侧启 GP / 代跑 v27+ 工厂搜索**（归 QuantLab AI）。  
- **overnight\*** 精神违规叶扩 ACTIVE primary。  
- **把 LLM「Replace Best」或 stub Sharpe** 写成密封过线。  

---

## 9. 读过的关键文件清单（供复核）

1. `alphaagent/app/qlib_rd_loop/factor_mining.py`  
2. `alphaagent/app/qlib_rd_loop/conf.py`  
3. `alphaagent/app/qlib_rd_loop/factor_backtest.py`  
4. `alphaagent/components/workflow/alphaagent_loop.py`  
5. `alphaagent/components/coder/factor_coder/evolving_strategy.py`  
6. `alphaagent/components/coder/factor_coder/expr_parser.py`  
7. `alphaagent/components/coder/factor_coder/factor_ast.py`  
8. `alphaagent/components/coder/factor_coder/evaluators.py`  
9. `alphaagent/components/coder/factor_coder/factor.py`  
10. `alphaagent/components/coder/factor_coder/template.jinjia2`  
11. `alphaagent/components/coder/factor_coder/function_lib.py`（头部原语）  
12. `alphaagent/components/coder/factor_coder/config.py`  
13. `alphaagent/scenarios/qlib/developer/factor_runner.py`  
14. `alphaagent/scenarios/qlib/developer/feedback.py`  
15. `alphaagent/scenarios/qlib/proposal/factor_proposal.py`  
16. `alphaagent/scenarios/qlib/regulator/factor_regulator.py`  
17. `alphaagent/scenarios/qlib/experiment/factor_experiment.py`  
18. `backend/services/engine/rd_agent/rd_loop_wrapper.py`  
19. `backend/services/engine/rd_agent/market_adapters/a_share.py`  
20. `backend/services/engine/inference/batch_orchestrator.py`  
21. `backend/services/engine/inference/batch_predict.py`  
22. `backend/services/engine/inference/neutralizer.py`  
23. `backend/services/engine/inference/position_signal.py`  
24. `backend/services/engine/inference/data_adapter.py`  
25. `backend/services/engine/inference/trading_cost.py`  
26. `backend/services/engine/inference/backtest_service.py`  
27. `backend/services/engine/qlib_app/services/backtest_service.py`  
28. `backend/services/engine/qlib_app/services/backtest_service_runtime.py`（入口/宇宙）  
29. `backend/shared/backtest_engine/core/engine.py`  
30. `strategy_templates/alpha_cross_section.py`  
31. `LICENSE`（AGPL-3.0 确认）  

**未拿到/未深挖（非阻塞）**：`rd-agent/` 内微软上游全树逐文件（经 wrapper 确认调用 `FactorRDLoop`）；`qlib_app/api/backtest.py` 路由层（服务逻辑已在 services）；`eva_utils.py` 全文（evaluators 已覆盖调用链）；私有 QuantDB 数据本身（仅见生成 h5/中性化 SQL 契约）。

---

## 10. 一眼结论

QuantMind 的真核是 **「LLM 假设 → DSL 表达式 → daily_pv.h5 eval → Qlib 组合报表」** 与 **「QuantDB 模型截面 → 中性化 → Top%/凯利仓位」** 两条链，外面包 CSI300/Alpha158 种子与 AGPL 整仓产品。  
形状（假设环、表达式监管、截面出口、费用/涨跌停）可抽；默认宇宙、评估、近亲、种子与谁付钱 **几乎都会被 QuantLab 硬闸打死**。  
融入路径：契约级 ADAPT + 闸门/短清单裁决；**不 vendor、不换主书引擎、不启本侧 GP、不晋级。**

`promotion_approved=false`
