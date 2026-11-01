# QuantLab 内部审计（Arch，2026-10-14）

范围：只读代码，并做了几个只读的 smoke 复现。主干没改，live=false，不涉及 GP 和小盘。
覆盖：执行引擎 `quantlab/platform/execution.py`、成本与可交易性 `quantlab/portfolio/v2_execution_costs.py`、交易日历、多袖套 book、`b4_paper`/S6、旧纸面轨 `v2_strategy_paper`、叶自检/衰减闸门（`research/leaf_selfcheck_common.py`、`alpha_decay_gate.py`）、三条腿的权重构建（capacity_adv / earnings_event / insider_increase）。
没覆盖到的（待下一轮）：900 多个 research 脚本里的 GP 历史版本、Web、Intel 管线、CB/期货袖套细节。
测试：box 上的 python 没装 pytest，`tests/` 没能跑，标"待确认"。

## 0. 先更正我上一份评审（ARCH_REVIEW_20261014）
- 我之前说"510300/ETF 复权停在 10-09、没有 A 股交易日历"，**这个结论现在不成立**。`output/data_freshness_status.json` 显示各表 last_date=20261013、stale=false，`etf_daily_adj` 最新到 20261014。`quantlab/portfolio/trade_calendar.py` 已经用 SSE trade_cal（覆盖到 20261231）。现在停在 2026-10-09 的是**权重文件和 X2 窗口常量**（`v2_multisleeve_book.py:36` 写死 `X2 end=2026-10-09`；B4 权重也到 10-09），不是数据。Top1 应改成"权重/窗口延展"，不是"数据补齐"。

## 1. 已通过的检查（没发现问题）
- 主引擎撮合：`ExecConfig.strategy_v1` 用 next_open 成交（execution.py:343-351），每天先卖后买（:741），日内不会回转，T+1 满足。涨跌停按成交价对比 limit_up/down 拦截（:750-755）；停牌由 close 为 NaN 或 volume≤0 判定（:679-682），停牌期间按收盘价 ffill 估值，复牌当天兑现全部涨跌。
- 个股面板：抽查 600519/000001/601318 在 X2 段，limit_up/limit_down/close/amount 都没有缺失（load_execution_panels smoke）。
- 印花税：2023-08-28 起从 10bp 改为 5bp，只对卖出征收，ETF 免征（v2_execution_costs.py:35-55）。
- daily_basic 的 available_at = 交易日 18:00 +08，capacity_adv 用 `available_at.normalize() <= session`，配合 next_open 成交，没有前视。
- 事件腿：T1 = available_at 之后的第一个交易日（searchsorted right），从 T2 开始入场，方向偏保守。
- 一日延迟 smoke：三条腿把权重延迟 1 天和延迟 2 天分别算 CAGR，延迟 2 天反而更高（capacity_adv 17.1%→17.7%、earnings_event 16.4%→18.0%、insider 15.1%→15.8%，按 244 年化），**没有一日前视的迹象**。

## 2. 问题清单

| # | 严重度 | 文件:行 | 证据 | 影响 | 修复建议 | 负责 |
|---|---|---|---|---|---|---|
| 1 | P1 | b4_paper.py:127,129,198；v2_multisleeve_book.py:470-473 用 **244**；v2_strategy_paper.py:214,218,230、leaf_selfcheck_common.py:59,67,69、alpha_decay_gate.py:17,52,74、research_statistics.py:3 用 **252** | SSE 实际每年 242-244 个交易日，X2 共 570 个交易日。smoke：同一组 capacity_adv 收益，按 252 算 CAGR 17.74%，按 244 算 17.13% | 闸门/叶自检（252）和纸面轨（244）的 CAGR、Calmar 不能直接对比，252 一侧大约高估 0.6pp。叶闸门里"叶 CAGR > cap CAGR"两边口径相同，所以不影响结论，但报告里拿来跨模块对比的数字会错 | 新建一个 `quantlab/metrics.py`，统一 `PERIODS=244`（或者按实际日历天数 /365.25 算年数），所有模块都调用它；scorecard 上注明口径 | Eng（主），Alpha/AI 迁移调用 |
| 2 | P1 | v2_strategy_paper.py:377 + strategy_feed.py:428-434；自注见 v2_strategy_paper_turn_compare.py:1136-1138 | 旧纸面 v1 用 `merged_daily_returns` 时**没传 total_return_factor**，等于用原始收盘价算收益。代码注释原文是 "paper NAV uses … raw closes (total_return_factor not passed)" | 除息、送转当天会被记成亏损（10 送 10 会记 −50%），复权口径和主引擎（corporate_actions=True）不一致。`output/strategy_paper_v1*` 里的结论都可能偏低 | v1 已经是旧线的话，在 README 和 scorecard 上标"原始价口径，作废/仅参考"；还要用的话就补上 total_return_factor 重跑。并入 Top5 的复权重算 | Eng / AI |
| 3 | P1 | v2_strategy_paper.py:414-416, 588 | 自注 "close_to_close_prior_weights; no_Tplus1_lag; no_limit_up_fill; missing_bar_ret=0"；而且权重在两次调仓之间保持固定，不随持仓漂移 | 不模拟 T+1、涨跌停和漂移，和主引擎口径不同。如果还有报告引用 v1 数字，它们和 B4/S6 不可比 | 同第 2 条：旧线降级为仅参考，统一走 run_weight_schedule | Strategy（确认是否还在引用）/ Eng |
| 4 | P1 | leaf_selfcheck_common.py:8-12,80-88 | 组合闸门（current/A/B）用的是**毛收益**（`_ret` 不扣成本），cap 和 overlay 都按 close-to-close、没有 T+1、没有涨跌停 | 换手高的叶在闸门里占便宜（成本只在 (b) 部分单独看）。A 臂的 beta 是全样本回归（:77，样本内，文档里已承认）。闸门判"过"的叶，进了引擎可能就不过 | 闸门改用净收益（g − COST×TO），或者直接调 book_smoke 引擎；beta 改成滚动、只用历史数据估计 | AI（闸门 owner）/ Alpha 复核 |
| 5 | P2 | leaf_selfcheck_common.py:33；alpha_decay_gate.py:45 | `close.reindex(P.index).pct_change(fill_method=None).fillna(0)`：停牌日和复牌日的收益都被置 0，停牌期间的涨跌**直接丢掉**，和 strategy_feed.close_to_close_returns 的原则相反。smoke：capacity_adv 有 11 个持仓格子受影响，累计收益 53.80% 对 54.07%（改成 ffill 后） | 目前影响小，但对事件叶、停牌多的叶会系统性地抹掉大跌（类似幸存者偏差） | 改用 `close_to_close_returns`（ffill inside） | AI |
| 6 | P2 | g1g5_earnings_event_weights.py:183；g1g5_insider_increase_weights.py:190 | `assert X.max() if cond else 0.0 <= 0` 按 Python 的优先级解析成 `assert (X.max() if cond else True)`（ast 已验证）。被硬排除的名字权重 >0 时断言反而**通过** | 600519/002371 的硬排除守卫实际不起作用（当前产出的权重里确认没有这两只，只是潜在风险） | 改成 `assert weights.loc[weights.instrument==b,'target_weight'].sum() <= 0` | AI |
| 7 | P2 | g1g5_insider_increase_weights.py:2-7 | docstring 写的是 "buyback-for-cancellation … 业绩预告/业绩快报"，但实际代码（:73-76）过滤的是 insider_increase/增持 | 文档和代码不一致，复核和追溯时容易误读 | 改 docstring | AI |
| 8 | P2（待确认） | g1g5_d1_val_resid_weights.py:96-156（被 capacity_adv:60 引用）；事件腿 docstring "anchor 2024-06-28" | 股票池是 **2024-06-28 那一天**按流通市值排的 top300，静态不变；B4 权重从 2024-01-02 开始，X2 从 2024-06-03 开始 | 2024-01 到 2024-06-27 这段用到了"未来"的股票池（轻微前视），后续新进大盘的票也进不来。事件腿有 PIT 成员过滤（:135-136），capacity_adv 有没有待确认 | 股票池改成按月 PIT 重排（mid_large_members_pit 每月一个锚点） | Data（池）/ AI |
| 9 | P2 | execution.py:757-759 | 参与率上限用的是**成交当天**的全天 volume，但成交时点是开盘 | 开盘时其实还不知道全天量，属于轻微前视，容量估计偏乐观 | 改用 V.shift(1)，或者用 ADV×参与率 | Eng |
| 10 | P2 | execution.py:779-783 | ADV 或 sigma 缺失时冲击成本记 0，只计数 `impact_missing` | fail-open，会低估成本 | 缺失时用分档默认 bp 兜底，并把 impact_missing 写进 receipt 和闸门 | Eng |
| 11 | P2 | v2_execution_costs.py:378-392, 507-509 | 可交易性面板在数据缺失时一律放行（缺 limit 价、tradestatus、ST 都当作可交易，注释写明 "do not invent"）；整只票没有面板时只记一条 no_panel | 用 S2 快速仿真时，缺数据的票会被当成可交易 | 缺失率超过阈值就判 FAIL，或者缺失时禁止买入 | Eng / Data |
| 12 | P2（待确认） | execution.py:645 `Cm = close.ffill(limit_area="inside").ffill()` | 个股没有 terminal_price（只有 CB 有，v2_multisleeve_book.py:117-124），退市后永远按最后收盘价估值，而且卖不出去 | 中大盘里退市少，影响小；但这是幸存者口径上的漏洞 | Data 提供个股退市价和退市日期，引擎按 terminal 处理 | Data / Eng |
| 13 | P2 | b4_paper.py:73-79 | S6 的 FROZEN_CONFIG 里 `N={600000:6,1000000:10}`，但实际权重每天的持仓数中位数是 **16 / 24**（最多 18 / 30），每只权重上限 6% | N 实际是每条腿内部的 topN 截断（leaf_selfcheck _overlay:47），不是组合持仓数，字段名容易误读 | 改名为 `per_leg_topN`，再补一个 `realized_names_median` | Strategy |
| 14 | P2（治理） | output/strategy_paper_s6/FROZEN_CONFIG.json | 01:51 ET 冻结，02:01 ET 就换了两档的权重文件（rehash_history 有记录） | 有留痕，但"冻结 10 分钟后重哈希"会削弱冻结的意义。S6 本身是 16 组里事后挑出来的，X2 是样本内（prereg:4 已承认） | 冻结后再改要附理由，并经 Leo 或主 Agent 签字；X2 成绩在任何地方都标"样本内" | Strategy / Beta |
| 15 | P2 | data_freshness_status.json `cutoff_hour_sh=20`；trade_calendar.py:15 `CUTOFF_HOUR_ET=17`（相当于上海 05:00） | 两处判定"当天数据该到没到"的截止口径不同 | 新鲜度告警和纸面 loop 对"应有交易日"的判断可能差一天 | 统一放在 trade_calendar 里一个常量 | Data / Eng |
| 16 | P2 | research_statistics.py:190 | 月胜率把首尾不完整的月份也算进去 | 窗口短时胜率有偏 | 剔除不完整月，或者单独注明 | Eng |
| 17 | P2 | v2_multisleeve_book.py:36 | X2 窗口终点和 B4/S6 权重终点写死为 2026-10-09；forward 段要等权重延展（b4_paper.py:101-110） | forward 2026-11-02 能不能按时启动，取决于权重延展脚本有没有跑 | 加一个日历驱动的权重延展任务，加上 WAITING 告警 | Strategy / Eng |
| 18 | P2（待确认） | capacity_adv:192 | "ADV" 实际是**单日** float_mktcap×turnover/100，不是均值 | 单日噪声大，容量上限会跳变；100万档和 60万档共用 AUM_BINDING=1M（:78），60万档偏保守 | 改成 20 日均值；文档里写清楚 60万档沿用 100万档的约束 | AI / Strategy |

## 3. 下一步
- 先修 #1（统一年化）和 #4/#5（闸门改净收益、停牌收益），否则 Top2 衰减闸门的结论不可靠。
- Top5 复权重算要把 #2/#3 的旧 v1 纸面线一起纳入。
- 等 pytest 装好后补跑 `tests/test_execution_*`，结果补进本文档。
