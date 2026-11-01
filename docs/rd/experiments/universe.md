# 股票池消融设计

状态：等待数据。总监已记录，不授权改代码。不承诺年化。

## 目的

分开「池子」和「打分」。接续文档写明参考池内部排序超额接近零。本实验只换合格名单，打分固定为不打分，执行与成本固定为 `run_weight_schedule` 的 `next_open` 与 `ExecConfig.strategy_v1`。

## 三组对照

1. 后排宽篮：决策日前 60 日成交额为正、先排名、第 3001 到第 5000 名。规则来自 `docs/RESEARCH_CONTINUITY.md` 对宽篮审计的描述。不足 3001 只则当日不买。
2. Mandate 中大盘：`quantlab/universe/d1_masks.py` 的上市满 120 日、非 ST、20 日成交额中位数至少 3000 万元、剔除流通市值底部 30%。申万行的 `available_at` 上海日期必须早于决策日。
3. 纸面 mid-large：沿用 `research` 里 mid-large 成员表的路径字面量 `data/v2/universe/mid_large_members_pit.parquet`（见数据清单）。表不在则该臂失败，不用另两臂的名单顶上。

## 数据

- D0 `data/local_market/1c85fd9aceaa03c3c4863bec/panels/<id>.parquet` 的 `event_time`、`close`、`amount`
- extend 日历 `calendar.parquet` 的 `session` 或 `trade_date`
- 流通市值 `data/v2/float_mktcap/float_mktcap_daily_tushare.parquet` 的 `instrument_id`、`float_mktcap`、`available_at`
- 申万 `data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`

## 预期能区分的差异

三组名单的重合度，以及各自相对沪深 300 ETF 的超额是否同号。不能区分时停，不调参。文件缺失的臂记失败，不补数。
