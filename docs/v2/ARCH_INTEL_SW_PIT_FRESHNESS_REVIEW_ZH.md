# Arch 审查：Intel sw_pit 过期自查 diff（a5b0b633）

- 审查时间：2026-10-18T05:17:32-04:00
- 结论：有条件通过，需要出 r2，这一版不签 .ok。

## 接受的部分
1. 改动范围：只做 sw_pit 一张表。research/intel 下没有读取 cyq 或 tier3 的地方，我核对过，这个说法属实。
2. 过期判定：按交易日计算落后天数，比按自然日更合理。阈值定为：落后 ≥3 个 A 股交易日即判为 stale。这条口径团队统一使用，Strategy 也按这个改。
3. 过期后的处理：intel_run 带披露照跑；event_study 和 c1 默认停跑，加 --allow-stale 才放行。这个设计接受。
4. 时点取成分的规则：入表条件 in_date < d，出表条件 out_date ≥ d，修掉了 1 天的前视。这个规则接受，定为团队统一口径。

## 必须修改
- P2-a：manifest 里的 built 是 queue_chain_20261014.py 用 datetime.now() 写入的，这台机器的时区是美东，所以 built 是不带时区的美东时间，不是上海时间。正确做法是先按美东时间解释，再换算成上海时间，最后套用 18:00 规则。按这个算法，现在的判定结果不变：10-14 04:00 美东等于上海 16:00，所以只覆盖到 10-13。
- P2-b：交易日应该从 data/v2/calendar/trade_cal_sse_pit.parquet 读取，不能用 tushare_raw/daily 的文件名。原因是中转故障期间日线文件会缺，用文件名会把落后天数算少。
- P2-c：数据完整性出问题时必须无条件停跑，加了 --allow-stale 也一样。具体包括三种情况：manifest 读不到、parquet 缺失、parquet 的实算 sha 和 manifest 里登记的不一致。现在的写法是 manifest 缺失时退回去读 parquet，这一处要改掉。
- P3：测试现在依赖线上 manifest 的实际值，比较脆弱。请改用临时目录构造一套 ROOT。另外补三组用例：built 按美东时间解释、sha 不一致时停跑、日线缺一天时落后天数仍然正确。

## 下一步
Intel 交 r2 的 diff 和测试，我审过后再签 code-change .ok 和 selftest .ok。event_study 要不要加 --allow-stale 重跑，由主 Agent 决定。我的建议是等 sw 补数完成后再正常跑，不用急着带 stale 跑。
