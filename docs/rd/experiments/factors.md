# 因子消融设计

状态：股票池符号已记在 `run_pool_sign_20261101.md`，三组未齐，30–60 只截断仍未写。因子实验不开跑。不授权改 `quantlab/strategy/experts.py`。不承诺年化。代码序不再当不打分对照。

## 目的

在同一冻结池、同一等权持有上，看打分有没有增量。对照不打分的那一臂。

## 三组对照

1. 不打分：不用代码序截 30 到 60 只。对照是股票池实验冻结后的合格名单等权。本轮股票池实验不截 60 只，因子实验继续等待那份名单，不在这里新写截断。
2. 现有五专家：`quantlab/strategy/experts.py` 的动量、价值代理、低波、成交、综合。因子窗口只使用决策日及以前的收盘，与 `quantlab/factors/engine.py` 的正向 `shift` 一致。
3. 有 `available_at` 的财务或事件：`financials_metric_asof` 只保留上海日期早于决策日的行。列不存在则该臂失败。不用报告期代替公布日。事件臂使用已经落盘、且带 `available_at` 的公告表；没有这张表就失败。

## 数据

池子实验冻结的名单，加上 `data/v2/financials_pit/financials_pit_tushare.parquet` 的 `instrument_id`、`metric`、`value`、`available_at`。事件表路径若源码里没有字面量，不发明路径，记入数据缺口。

## 预期能区分的差异

打分臂相对不打分臂的日超额是否跨零。跨零则该打分没有增量，不继续调专家温度。`value_lowtension` 的注释与符号不一致（`quantlab/factors/engine.py` 对缩量取负）只作为已知实现差异，本设计不顺便改符号。
