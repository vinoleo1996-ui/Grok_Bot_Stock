# Arch · GitHub 量化新亮点跟踪（每日增量）

维护：QuantLab Arch。约束：禁 GP、不改主干、live=false；小盘禁令已于 2026-10-14 07:24 ET 由 Leo 解除（全 A 研究、纸面用高流动子集），本文件按最新口径筛选。存量全景见 `ARCH_GITHUB_LANDSCAPE_20261014_ZH.md`。

---

## 2026-10-14（扫描窗口 10-13 00:00Z → 10-14 13:07Z）

扫描范围：qlib、RD-Agent、vnpy、alphalens-reloaded、TradingAgents（近一天无提交）；FinRL、skfolio、hikyuu、Riskfolio-Lib（有提交）；GitHub 新仓按 star 排序（近 7 天新建 quant/alpha/factor/trading/portfolio、近 14 天新建 A股/量化、`topic:quantitative-finance` 近一天推送）。

### 采纳候选 1：IC t 统计量的重叠窗口校正（HAC + wild bootstrap）
- 来源：[skfolio 提交 246176c](https://github.com/skfolio/skfolio/commit/246176ccfbbb1faabe43d44a510a38ad7f5193d1)（#409，2026-10-14 13:01Z）「fix(alpha): account for overlapping windows in the IC t-statistic」：用 quadratic-spectral 核 HAC 标准误处理评估日之间的相关性和时变波动，再用 Gaussian wild bootstrap 校准临界值。
- 为什么对 QuantLab 有用：多日前瞻收益（5/10/20/60 日）逐日计算的 IC 序列天然高度自相关，朴素 `mean/std*sqrt(n)` 会虚高 t 值，导致弱因子过闸。
- 内部现状（只读核查）：
  - `quantlab/factors/ai_factory/evaluate.py` 的主标签是 1 日 open→open（`y_t=open[t+2]/open[t+1]-1`），**不重叠**，AI 闸 `icir_vs` 的 `sqrt(252)` 年化本身无重叠问题。
  - `research/leaf_selfcheck_v3.py` 第 95–105 行对 h=5/10/20/60 用 `n_eff=len/h` 粗校正：能挡住重叠的主效应，但忽略 h 之外的自相关和波动聚集，A 股 2015/2024 这类高波段会让 t 仍偏高。
  - `research/alpha_combo_marginal.py` 用 `P.shift(-H)` 的 H 日前瞻，只报 ICIR（不报 t），无显著性判定，不受影响但也没保护。
  - 旁注：上述两个脚本仍用 `select_mid_large_topn_light(top_n=300)` 作池，与 Leo 07:23 ET「全 A / HI_LIQ」口径不一致，留给增量审计跟进。
- 建议做法（不改主干，只加并行列）：
  1. 新增工具函数 `ic_tstat_hac(ic_series, h)`：Newey-West（Bartlett 核，lag=max(h-1, ⌊4(n/100)^{2/9}⌋)），numpy 约 15 行实现即可（环境未装 statsmodels，不需新依赖）；可选 QS 核 + Andrews 带宽对齐 skfolio。
  2. 可选：Gaussian wild bootstrap（ε~N(0,1) 乘去均值 IC，B=999）给出 bootstrap p 值。
  3. `leaf_selfcheck_v3` 与 Alpha 闸报告里并列输出 `ic_t_naive / ic_t_neff / ic_t_hac`，**仅披露、不改现有阈值**；连续两周对比后再由 Alpha 提议是否把闸切到 HAC t。
- Owner 建议：Alpha（闸口统计口径）+ AI（自检脚本），Arch 复核。

### 已看过、不采纳
- FinRL #1456（StockTradingEnv 用价格而非首个指标判断可交易）：RL 环境修补，QuantLab 不用 FinRL 环境。
- hikyuu 一组 trade_sys/allocatefunds 加固（NaN 防护、预算上限、Or 越界修复）：工程质量修补，无新方法；可作为我们 optimizer 输入 NaN/非有限值防护的提醒，现有 FROZEN 流程已含可行性检查。
- 新仓：多为加密/预测市场机器人、ICT/SMC 技术分析技能、个人作品集；A 股相关的 `AllenPan-Git/SimpleQuant`（低代码回测）、`MrLaoGe/x2Stock`（仍是设计文档）、`CodeNightOwl/ai-trading-assistant`（LLM 投研助手）均无可采纳的新方法。`roberts9012062/futures-factor-mining-experiment` 是期货因子实验室，非 A 股选股。

---

## 2026-10-18（扫描窗口 10-16 13:00Z → 10-18 13:05Z；10-17 例行扫描失败，本次一并补扫）

扫描范围：qlib、RD-Agent、vnpy、FinRL、Riskfolio-Lib、vectorbt（窗口内无提交）；alphalens-reloaded、TradingAgents（发布 v0.7.0）、skfolio（v1.9.1–v1.9.4）、hikyuu（有提交）；GitHub 新仓按 star 排序（近 7 天新建 quant/alpha/factor/trading/portfolio/backtest，`topic:quantitative-finance` 与 `topic:algorithmic-trading` 近一天推送）。中文关键词（A股/量化/因子）搜索本次接口返回异常，未覆盖，下次补。

### 采纳候选 2：决策结算从「决策日之后的第一个交易日」起算（防同日前视）
- 来源：[TradingAgents 提交 f5e3eae](https://github.com/TauricResearch/TradingAgents/commit/f5e3eae)（#1518，2026-10-16 21:12Z，随 v0.7.0 发布）「fix(memory): score a decision from the first close after its date」：结算入场改到决策日之后的第一个交易日，避免决策日收盘后才发布的新闻被拿去对当天收盘打分。
- 内部现状（只读核查源码，未读任何行情或收益数据）：
  - `quantlab/agents/trading_loop/settle.py`（最后提交 94a7a11，10-12）第 88–97 行入场取 `inst.index >= session_ts` 的第一根 bar，`px0` 就是决策日当天收盘；第 110 行基准 `bench.asof(entry_dt)` 同样取当天收盘。
  - 决策若在收盘后做出，或用到当日盘后的新闻、公告（Intel 事件特征、ai_debate 都可能如此），当天的涨跌在决策时已可见却仍计入结算，结算 alpha 和写回记忆的 reflection 会偏乐观；`debate_ledger.py` 的 G6 记忆 PIT 过滤（resolution_date≤asof）只管记忆何时可用，挡不住入场点本身的前视。
  - 文件头注释第 5 行还留着未写完的「wait:」草稿，PIT 规则表述本身也需要定稿。
- 建议做法（不改主干，交 Eng 落地）：
  1. `compute_horizon_returns` 增加参数 `entry_rule`，默认改为 `next_session`（`inst.index > session_ts`），保留 `on_or_after` 只用于复现旧结果；基准使用同一个 entry_dt。
  2. 决策记录若有 `asof_decision_ts` 且早于 09:30，可选 `same_session_open`，但需要开盘价列；当前 etf_daily_adj 只读 close，先不做。
  3. decision_log 里已 settled 的记录保留原值，新增 `settle_rule` 字段区分口径；是否重算旧记录由 Eng/Beta 决定（重算要读真实价格，需先有 Arch .ok）。
  4. 单测只用合成序列：决策日当天大涨，新规则下 alpha 不应包含当天涨幅；旧规则下应包含，用来锁住行为差异。
- 影响面：只影响研究级 trading_loop 的记忆打分，不碰纸面轨、optimizer、闸口阈值；live/promotion=false 不变。
- Owner 建议：Eng（实现+单测），Intel/Alpha（确认决策时点字段的含义），Arch 复审 diff。排在叶23/24 串行链和 10-19 纸面开跑之后，不进入当前静默窗口（RESEARCH_QUIET.lock 存在期间不跑任何读数据的进程）。

### 口径备注：alphalens 分位价差改为 100% 毛敞口
- 来源：[alphalens-reloaded 提交 1bc181d](https://github.com/stefan-jansen/alphalens-reloaded/commit/1bc181d)（#49，10-17 18:17Z）：top 分位减 bottom 分位的原始差相当于 200% 毛敞口，新版减半为 50% 多 / 50% 空，误差带同步减半，历史数值整体变为一半。
- 内部：`research/top5_factor_report_emit.py` 的 `long_short = q5-q1` 是 200% 毛敞口口径。我们没有装 alphalens，内部前后比较不受影响；只是今后拿新版 alphalens 或外部报告的价差对比时要乘 2 换算。建议报告里标注「q5−q1，200% gross」，不需要改代码。

### 已看过、不采纳
- skfolio：ShrunkMu 的 Bodnar-Okhrin 系数修正（#398）、回撤贡献差分步长（#384）、WalkForward 空日历窗口和末窗遗漏（#427/#433）。我们的 optimizer 用 alpha 分数而非收缩均值，也不依赖 skfolio；WalkForward 两个修复可作为 λ 样本内校准切窗时检查「空窗、末窗被漏掉」的提醒。
- hikyuu：分析模块改为每个参数组合用独立账户、不共享 tm（edc8c47）。这是网格或敏感性批跑中组合之间状态串扰的经典坑，建议列入审计清单（并列敏感性类脚本要核对每个变体是否独立建 book），我尚未逐一核查现有脚本；其余为实盘引擎、GIL、spot agent 加固。
- alphalens #50/#68（保留日内行、纳秒精度前瞻收益列）和 pandas 3 支持：工程兼容，我们不用 alphalens。
- TradingAgents 其余提交：ChatGPT 账号登录 provider、CLI 提示等，与方法无关。
- 新仓：多为 Polymarket/加密机器人、交易终端、Claude 交易技能包。`BijectiveLabs/trading-research-agents`（智能体只提议、确定性系统做决定）理念与我们的 Arch .ok 闸一致，但无新方法；`HKUDS/Vibe-Trading`、`OpenByteInc/QuantDinger` 热度高，面向个人 vibe trading，无 A 股选股新方法。

---

## 2026-10-26（扫描窗口 10-25 13:00Z → 10-26 13:15Z）

扫描范围：qlib、RD-Agent、vnpy、TradingAgents、vectorbt、Riskfolio-Lib（dcajasn，窗口内无提交）；alphalens-reloaded（#74）、FinRL、skfolio（v1.12.0–1.12.2）、hikyuu（fasiondog，大量引擎加固）；GitHub 新仓按 star 排序（`created:>2026-10-19` quant/alpha/factor/backtest/portfolio；`topic:quantitative-finance|algorithmic-trading pushed:>2026-10-25`；中文 `量化|因子|A股 created:>2026-10-12`）。

### 采纳候选 3：持仓/前瞻到期与 freshness 必须携带节假日日历
- 来源：[alphalens-reloaded 提交 60755d1](https://github.com/stefan-jansen/alphalens-reloaded/commit/60755d1cc7d9d36a4c70c8344cbdb168fe99df24)（#74，2026-10-26 00:28Z）「Preserve holiday calendars through cleaning and factor holdings」：清洗与 factor holdings 到期时保留 `CustomBusinessDay`（含 holidays），避免 MultiIndex 复制 / groupby 丢掉休市日，导致到期落在闭市日（Closes #73）。
- 为什么对 QuantLab 有用：与已采纳的 next-session settle（防同日前视）互补，专攻**日历忠实度**。国庆/春节窗口若把休市日当成交易日，会扭曲持有期长度与新鲜度闸。
- 内部现状（只读核查源码，未读行情）：
  - 纸面主路径 `research_loop.data_freshness()` 与 `trade_calendar.open_days()` 已用 SSE `trade_cal.parquet`（节假日已建模）。
  - `_legacy_freshness()`（`research_loop.py` 第 704–724 行）仍注明「weekday calendar; CN holidays not modeled」，用 weekday 回退期望会话。
  - `trading_loop/settle.py` mock 路径第 79 行用 `pd.bdate_range`（只跳周末）；`v2_multisleeve_book.py`、`scripts_eng/s2_3_exec_layer.py`、若干测试同样用 `bdate_range`。
- 建议做法（不改主干策略权重，交 Eng 落地）：
  1. 审计 freshness 闸与任何「N 个交易日」到期/持有窗，统一走 `quantlab.portfolio.trade_calendar.open_days`（或等价 SSE 日历），淘汰 `_legacy_freshness` 的 weekday 回退或标明废弃。
  2. settle mock 与合成单测改用带 holidays 的日历（可用 `open_days` 切片或 `CustomBusinessDay(holidays=…)`）；补国庆窗口断言：到期日 / 新鲜度期望日不落休市日。
  3. 仅披露/审计，不改纸面权重与闸阈值；live/promotion=false 不变。
- Owner 建议：Eng（审计+单测），Arch 复审 diff。排在叶25 alpha 跑完与 QUIET 解除之后，不碰当前静默锁。

### 口径备注：skfolio bootstrap 须用局部 RNG
- 来源：[skfolio #465](https://github.com/skfolio/skfolio/commit/4d546b42f1bf1869d9fcf737828b020cdda5a89d)（2026-10-25）stationary bootstrap 勿改 NumPy 全局 RNG。
- 内部：并入已采纳候选 1（IC HAC + wild bootstrap）落地约束——实现 wild bootstrap 时用局部 `RandomState`/`Generator`，禁止 `np.random.seed`。不单列新方法。

### 已看过、不采纳
- FinRL #1196（ElegantRL/Gymnasium API）：QuantLab 不用 FinRL 环境。
- skfolio #403（named estimator collections in cross_val_predict）、v1.12 发版与 pandas inplace 兼容：我们不用 skfolio；λ 校准已有自研切窗。
- hikyuu（fasiondog）：trade_sys 配额/空头、GIL、退市/嵌套缓存矩阵测试、README——工程质量；延续 10-18「并列敏感性独立 book」审计提醒，无新选股方法。
- 新仓：`ChungKit-WAN/Quant-research-lab`（69★，next-session close + 缺失因子不补零，与已采纳 settle 同族，记 note 不重提）；NSE/ETF 轮动/配对交易；`huuan26/polars-anta`（技术指标库）；`dennynan/quantlab-oss`（Qlib+Alpha158 封装，名撞车）；`sysean/dragon-head-tactics` / `HKUDS/Vibe-Trading`（vibe，10-18 已排除）。

---

## 2026-10-27（扫描窗口 10-26 13:15Z → 10-27 13:15Z）

扫描范围：qlib、RD-Agent、vnpy、alphalens-reloaded、FinRL、vectorbt、Riskfolio-Lib、skfolio（窗口内无提交）；TradingAgents（v0.7.1 一批 memory/settlement 修复）；hikyuu（fasiondog，引擎/GIL/测试）；GitHub 新仓按 star（`created:>2026-10-20` quant/alpha/factor/backtest/portfolio）；`topic:quantitative-finance|algorithmic-trading pushed:>2026-10-26`；中文 `量化|因子|A股 created:>2026-10-12`。

### 采纳候选 4：结算只用「已终盘」价，长休市拉长取数窗，未到期不取价
- 来源：[TradingAgents 提交 eb4a486](https://github.com/TauricResearch/TradingAgents/commit/eb4a48609216ce30f880d2d067b6d797d703c83d)（#1548/#1539，随 v0.7.1，2026-10-27）「settle decisions on final closes, across long market closures」：
  1. 按标的市场日历日，**当日仍在交易的 bar 不当终盘**（Yahoo 盘中已给当日 bar，价格是 live 价）；
  2. 持有窗日历跨过长休市（如国庆）且尚不够交易日数时，**把取数上界拉到 today** 再试，仍不够则 pending；
  3. 按日历推算持有窗**不可能已走完**时，直接 pending，**不请求价格**。
- 旁证同族：[finathink #14](https://github.com/ceyyy427/finathink/commit/be081d004522901f27cd2078d1d9aeb7a677701a)「fence realized evidence by current time」——复盘有效截止取 `min(请求日末, 服务器当前时刻)`，并校验 `available_at`，避免「选了今天、却把当天晚些才可用的观察提前当已知」。不整仓引入 finathink，只借这条时间围栏口径。
- 为什么对 QuantLab 有用：与已采纳候选 2（next-session 入场）和候选 3（节假日日历）互补，专攻**结算时点的终盘忠实度**。盘中或日更刚写入 partial/`available_at` 未到的 bar 若被当成 exit/entry close，记忆 alpha 会掺 live 噪声；国庆前后若取数窗只按 `*7/5+7` 日历缓冲，停牌/长休市标的可能假 pending 或误用不足窗。
- 内部现状（只读核查源码；未改代码、未读收益序列做结论）：
  - `quantlab/agents/trading_loop/settle.py`：`_load_closes` **读了** `available_at` 列但**未按 now 过滤**；入场仍 `inst.index >= session_ts`（候选 2 的 next-session 尚未落地）；mock 已用 `open_day_range`（候选 3 备注），真路径依赖 parquet 里已有交易日。
  - 数据侧当日可有 `trade_date=今天` 且 `available_at=15:00` 的行；若 settle 在可用时刻前跑，当前实现仍可能纳入该 close。
  - `research/ai_debate_memory_runner.load_prior_settlements`：文件顺序 `rows[-limit:]`，**按写入序取最近 K**，未按 `session`/`resolution_date` 排序——与 TradingAgents [caf6792](https://github.com/TauricResearch/TradingAgents/commit/caf6792bba2d7c84e4fc266f81f07c3db90d8853)「按决策日取最近课」同族缺口；若日后回填旧结算，会挤掉更新的课。G6（`resolution_date≤as_of`）已挡前视，但不挡排序。
- 建议做法（不改主干权重/闸阈值，交 Eng 落地；须 Arch `.ok` 才读真行情单测以外的结算）：
  1. `compute_horizon_returns`：对 inst/bench 丢弃 `available_at > now` 的 bar；若缺 `available_at`，则丢弃「市场日历日 == 今天且 now 早于该市常规收盘」的 bar（A 股默认 15:00 Asia/Shanghai）。
  2. 入场默认切 `entry_rule=next_session`（落实候选 2）；exit 取 entry 后第 H 个**已终盘**交易日；不足则 `pending`，不写 settled。
  3. 取数上界：先按交易日历估 end；若仍不足 H+1 根且 end&lt;today，允许扩到 today（仅取数，不改 H 定义）。
  4. `load_prior_settlements`：过滤后按 `(session 或 resolution_date, 行序)` 降序取 limit；单测构造「先写 6 月、后回填 1 月」断言记忆块仍含 6 月。
  5. 合成单测：盘中假今日 bar → 不得 settled；国庆缺口 → pending 或扩窗后正确 exit；不改纸面轨/optimizer；live/promotion=false。
- Owner 建议：Eng（settle + 记忆排序 + 单测），Intel/Alpha（确认 asof_decision_ts / resolution_date 字段），Arch 复审 diff。排在叶链 QUIET 空窗；不碰当前研究锁。

### 已看过、不采纳
- TradingAgents 其余 v0.7.1：CLI/Azure LLM/SEC/Yahoo 打印/portfolio 非有限值拒绝/Docker `.env`——工程修补；非有限值拒绝可作 optimizer 输入 NaN 提醒（FROZEN 已有可行性检查），不单列。
- hikyuu：Python 3.15 绑定、GIL 探针、incremental shift 拒纳、3.0.0 准备——引擎质量，无新选股方法。
- finathink（★249）Phase 5–9：PIT 工作台/purged 因子实验/纸面延迟成交/复盘审核——产品面与我们已有 `quantlab/research.py` purge_labels、Arch `.ok` 闸同族；除上述「当前时刻围栏」口径外不整仓引入。
- 新仓：`theinvinciblepanther/etf-rotation-paper-bot`、`huuan26/polars-anta`（10-26 已记）、`manishY-iitm/QuantIntel`（当日新建 agent lab）、`HyeonbinJung/Signals-to-Alpha`（韩食另类数据）、`jundizhou/easy-stock` / `autumn-go/strategy-factor-dashboard`（A 股展示/日报）、`ml4t/skills`、`dennynan/quantlab-oss`（10-26 已排除）——无可落地的新选股/闸口方法；禁 GP。
