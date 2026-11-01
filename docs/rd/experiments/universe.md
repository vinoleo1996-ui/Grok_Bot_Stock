# 股票池消融设计

状态：设计已写明合格条件。不授权改宽篮名次公式。不承诺年化。不把本臂结果写成可交易收益。

## 目的

分开「池子」和「打分」。打分固定为不打分。执行时点是下一交易日开盘。主成本是 `ExecConfig.strategy_v1`（滑点 0.0，`impact_k` 1.0，佣金 2.5bp，最低 5 元，卖出印花税按 2023-08-28 前后的法定税率）。草案第 70 行的滑点 5bp 只作敏感性，不作为通过条件，也不改 `strategy_v1` 的默认值。

价格用原始 `open`/`close`。公司行动走 `quantlab/data/v2_readers.py` 第 29–30 行的 `data/v2/corporate_actions/`。不读 `adj_close`。`quantlab/smallcap/panel.py` 第 94 行的复权 `bfill` 仍不作为本实验的价格。

## 三组对照

1. 后排宽篮：决策日前 60 日成交额为正、先按成交额排名、第 3001 到第 5000 名，均额至少 500 万元。规则仍是 `quantlab/smallcap/universe.py` 的名次带。不足 3001 只则当日不买。然后去掉 `bj.`，去掉当日 `is_st_at_open` 为真的名字，去掉退市整理已经可见的名字。不再按代码序截 60 只。
2. Mandate 中大盘：上市满 120 个交易日、当日不是 ST、20 日成交额中位数至少 3000 万元、在这些名字里剔除流通市值最低的 30%。流通市值用 `float_mktcap_daily_tushare_pit.parquet`，决策按开盘可知，只用前一会话。同样去掉 `bj.` 和已经可见的退市整理。不调用会把缺失 ST 当成非 ST 的旧掩码。
3. 纸面 mid-large：`data/v2/universe/mid_large_members_pit.parquet`。`available_at` 的上海日期必须早于决策日。表不在则该臂失败，不用另两臂的名单顶上。再去掉 `bj.`、当日 ST 和已经可见的退市整理。

ST 表是 `data/v2/st_flags/is_st_daily_2018_2026.parquet`，只收录 `is_st_at_open` 为真的行。某个决策日在这张表里没有任何行时，该日记缺口，不把缺失当成非 ST。退市整理用 `data/v2/ref/stock_delisted_v2.parquet` 里 `entered_delisting_period_v2` 为真、且 `available_at` 早于决策日、决策日又落在整理期起止之间的 `instrument_id`。不新建 `delist_events_v1.parquet`。

这一臂不从名次带里再截 30–60 只。全名单在 60 万上不能当成可成交的账户，所以只报告三组名单的重合度，以及相对 510300 下一开盘超额的符号。不写可交易年化。30–60 只的截断等符号结果出来后再写，这里不补排序公式。

## 数据

- D0 `data/local_market/1c85fd9aceaa03c3c4863bec/panels/<id>.parquet` 的 `event_time`、`open`、`close`、`amount`
- 同目录 `calendar.parquet`、`instruments.parquet` 的 `listing_date`
- 流通市值 PIT：`data/v2/float_mktcap/float_mktcap_daily_tushare_pit.parquet`。原表没有 `available_at`，不用它顶上
- 申万表本实验的名单不依赖行业标签

## 窗口和停的条件

探索窗 2024-06-03 至 2026-06-30。不重跑 2018-01-02 至 2024-05-31。个股面板停在 2026-06-30，不编其后的盈亏。

三组相对 510300 的超额同号则停，不改专家、不调温度、不改构造器默认帽。文件缺失的臂记失败，不补数。`strategy_promotion_approved` 保持 false。
