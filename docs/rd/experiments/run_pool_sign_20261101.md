# 探索窗三组对照的符号（2026-11-01）

脚本 `research/rd_pool_sign_20261101.py`。窗口 2024-06-03 至 2026-06-30，每 10 个交易日决策一次，共 51 个决策日、50 段持有。没有调用 `stable_book`，没有把名次带截成 60 只，没有读 `adj_close`，没有重跑密封窗。`strategy_promotion_approved` 为 false。数字来自 `output/rd_pool_sign_20261101/summary.json`。这些超额是合格名单等权、下一开盘到下一开盘的诊断，不是 60 万可成交账户的年化。

主成本按 `ExecConfig.strategy_v1`：滑点 0，佣金 2.5bp，卖出印花税 5bp，加在等权换手上。冲击没有套进这张诊断。滑点 5bp 只作敏感性。价格是原始开盘，加上 `data/v2/corporate_actions/dividend_by_exdate_tushare.parquet` 里 `div_proc` 为「实施」的现金和送转。

mid-large 的可见性是 `available_at` 不晚于决策日 18:00 Asia/Shanghai（`quantlab/data/contracts.py` 的 `decision_time`）。这张表的时钟是决策日 09:00，早于 18:00，当日 126944 行都可见。不用申万那种「上海日期必须早于决策日」。

| 臂 | 名单中位数 | 相对 510300 的诊断超额符号 | 5bp 敏感性符号 |
| --- | ---: | ---: | ---: |
| 后排宽篮，去掉北交所、当日 ST、已可见退市整理 | 1824 | 正 | 正 |
| 上市满 120 日、非 ST、20 日成交额中位数至少 3000 万、去掉流通市值最低 30% | 3277 | 正 | 正 |
| mid-large，18:00 前可见，再去掉北交所、当日 ST、已可见退市整理 | 2489 | 正 | 正 |

名单重合度中位数：宽篮对中大盘 0.168，宽篮对 mid-large 0.106，中大盘对 mid-large 0.746。

三组符号同为正。按 `docs/rd/experiments/universe.md`，同号则停。没有改专家、没有调温度、没有改宽篮名次公式、没有改构造器默认帽。30–60 只的截断不在这张同号结果之后补写。
