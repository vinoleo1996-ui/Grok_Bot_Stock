# 接线

权重长表 `quantlab/platform/weight_long_table.py` 已能校验 `session`、`instrument_id`、`weight`。`book_smoke --skip-run` 只做这步校验，不读 ETF。

`book_smoke --run-nav` 进入 `quantlab/portfolio/v2_multisleeve_book.py` 的 `Data`，直接读 `data/v2/etf/etf_daily_adj.parquet`。

D1 与 `strategy_feed` 走 `quantlab/data/v2_readers.py`。文件在则按 `docs/v2/ASOF_EXTEND_PANEL_MERGE.md` 拼接 D0 与 extend；文件不在则 `FileNotFoundError`。读取器不计算收益。

`quantlab/portfolio/v2_strategy_paper.py` 仍是收盘到收盘、无 T+1，不作为这轮组合实验的执行。

未关闭：`quantlab/smallcap/panel.py` 第 94 行复权因子 `bfill`。`quantlab/v2_eng_smoke.py` 第 224 行要求日频流通市值视图的 `promotion_approved` 为 true；读取结果保持 false，因为 `output/d1/ENG_PING_PATHS.json` 不在检出里。
