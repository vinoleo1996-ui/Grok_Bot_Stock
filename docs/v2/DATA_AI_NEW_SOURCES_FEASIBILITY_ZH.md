# AI 新叶数据源可得性评估（2026-10-13，轻量探测）

范围：2018-01→2026-10，研究用；live/promotion=false，禁GP。本轮每接口仅 1–3 次请求，未开重拉，未碰 cyq_perf(PID 4094376)，未启 8787。
探测：relay=PCD Tushare 中转；datahub=datahubco Tushare；EM=东财 datacenter/reportapi。

| 项 | 本地已有 | 可用源（权限/单次上限） | 样本 | 预估覆盖/行数 | available_at | 预估拉取 |
|---|---|---|---|---|---|---|
| ①大宗交易 block_trade | 无 | relay ✅、datahub ✅（按 trade_date，单日一次即全量；字段 ts_code/trade_date/price/vol/amount/buyer/seller） | 20261012: relay 109 / datahub 114 行；20180105: 220 / 236 行 | ~2,150 交易日 × ~150–250 ≈ 40–50 万行，2018 起满窗 | 可信：交易所当日盘后披露 → 设 T+1 开盘 09:00 | ~2,150 请求，单源约 1–1.5h；两源行数不一致，建议双源拉取后并集+差异报告（约 2–3h） |
| ②公募持仓 fund_portfolio | 无 | relay ✅ 仅按 ts_code（单次上限 8000，period 参数 400）；datahub ✅ 按 period，单次上限 1000（需 offset 翻页） | 510300：ann_date 2015-04-21→2026-08-29；period=20250630 返回满页 1000 | 2018Q1–2026Q2 共 34 期；季报仅前十大，半年报/年报全持仓；估计 1,500–3,000 万行 | 可信：有 ann_date → 设 ann_date+1 开盘（同一 end_date 多次披露保留首次）| 重：全基金约 1–2 万只，按 ts_code 需 1–3 万请求 ≈ 6–10h；建议先限主动权益+指数股基(约 6–8k 只) 或仅季报前十大，≈3–5h |
| ③分析师预测/评级 report_rc | 无 | relay ❌（400 无权限）；datahub ✅（按 report_date，21 列含 org/author/rating/tp/np/eps，单次 1000）；EM reportapi 研报列表 ✅（2018-01 单月 794 条，含 EPS 预测）；EM RPT_WEB_RESPREDICT 仅当前快照（非 PIT） | 20180110: 427 行；20261010: 38 行 | ~2,900 日 × ~200–400 ≈ 60–100 万行；一致预期需自行由明细滚动聚合 | 基本可信：report_date 为发布日（无时刻）→ 设 T+1 开盘；EM 快照不可用于 PIT | datahub ~3,000 请求（部分日需翻页）≈ 2–3h |
| ③b 机构调研 stk_surv（附带） | 无 | relay ✅ datahub ✅ | 20261010: 19 行 | 估 20–40 万行 | surv_date≠披露日，需保守滞后（如 +2 交易日）或配公告日 | ~2,150 请求 ≈1h |
| ④股权激励 | 无（announcements 文本可辅） | Tushare 无对应接口；EM RPT_EQUITY_INCENTIVE ✅（总 16,007 条，含方式/标的/数量/行权价/进度） | 有 LASTEST_NOTICE_DATE，无首次公告日、无考核门槛字段 | 规模：16k 方案全量（含新三板需过滤）；考核门槛需解析草案公告正文 | 部分：仅"最新公告日"，首次公告日需从公告表匹配草案日；门槛需文本解析 | 规模表 ~320 页 ≈ 10min；门槛解析另需公告 PDF 抓取，数小时级，按需 |
| ⑤ETF 份额日序列 | ✅ `data/v2/etf/share_pit/etf_share_flow_pit_all.parquet`：1,838 只，2014-01-02→2026-10-09，157.8 万行，含 share/nav/available_at | relay fund_share 按 trade_date 单日 1,786 行一次取全；datahub 上限 1000 | — | 已满窗，仅缺 10/12–10/13 | 已有 | 增量 2 请求，<1min |

## 结论/建议顺序
1. block_trade：可满窗、可信 PIT，最便宜，先做（双源对账）。
2. report_rc（datahub）：可满窗，PIT 可接受，第二。
3. fund_portfolio：可得且 PIT 可信，但量大，建议先限范围。
4. 股权激励：规模可得；首次公告日与考核门槛需结合公告文本，研究级 PARTIAL。
5. ETF 份额：已有，仅需日常增量。
