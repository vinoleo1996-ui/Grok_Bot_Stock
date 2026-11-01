# 研究循环端到端演练（dry-run）回执（2026-10-13 ~23:10 ET）

红线：live=false；不下单；无 GP、结构搜索或自动开新叶；单进程串行；无 uvicorn/8787；未写 AI 目录或代码；capacity_adv 纸面 STATUS/输出未改（output/strategy_paper_capacity_adv/STATUS.json 的 mtime 仍为 17:06）。

## 本次改动
- loop-sync --writeback：有限回写到 output/loop/factory_feedback.{json,parquet}，只含优先级、fitness、黑名单，带 version_sha256，幂等。契约见 docs/v2/LOOP_APPROVE_EVOLVE_CONTRACT_ZH.md。
- paper-daily 的新鲜度改用 Data 的完成标记 output/daily_update_status.json（status=="ok" 且 target_trade_date == 预期交易日）。
- alert-ingest 默认读 output/intel/ALERTS_latest.json，映射到预警契约（docs/v2/ALERT_INTERFACE_CONTRACT_ZH.md）。

## 引擎读的是哪些路径（核查结论）
| 输入 | 引擎/strategy_feed 实际路径 | 最新日 |
|---|---|---|
| 个股行情 | default_v2_roots：asof_extend_dir = data/v2/asof_extend_tushare_202610（主），asof_extend_202610 为 fallback | 2026-10-13 ✓ |
| 510300 成交/盯市（load_execution_panels） | merged 面板 + data/v2/etf_510300/panels/sh.510300.parquet 续接 | 2026-10-13 ✓ |
| 股票分红 | data/v2/corporate_actions/dividend_by_exdate_tushare.parquet（execution.py L1576） | 2026-10-13 ✓ |
| **Book-Smoke 交易日历与 C0/HFQ**（v2_multisleeve_book.Data） | **data/v2/etf/etf_daily_adj.parquet（close_hfq）** | **2026-10-09 ✗**（未在本次日更中） |
| 基金分红/复权因子 | etf_daily_adj.adj_factor + etf/raw/fund_div.parquet | 2026-10-09 |
| strategy_feed 510300 收益 | data/v2/etf_510300 | 2026-10-13 ✓ |
另外，Book-Smoke 的 X2 窗口终点写死为 2026-10-09（WINDOWS["X2"]），B4 和 capacity_adv 的权重也只到 2026-10-09。**所以即使行情已到 10-13，纸面 NAV 仍只到 10-09。**

## 逐步结果（串行）
| 步 | 命令 | 结果 | 耗时 | 峰值 RSS |
|---|---|---|---|---|
| 1 | loop-sync | PASS：21 叶、8 组合 → output/loop/leaf_status_index.{json,parquet} | 0.38s | 118MB |
| 2 | loop-sync --writeback | PASS：32 行，黑名单 12（3 叶 fail、1 计数闸、8 个未胜主干的组合）；再跑一次输出 unchanged（version 4345564953…） | 0.35s | 119MB |
| 3 | paper-daily --run-nav（演练） | PASS：完成标记 ok，target_trade_date=2026-10-13=预期 → 判为新鲜，**按 10-13 数据批次运行，而不是 New Bot 要求的强制 10-09**；但 NAV 实际仍止于 10-09（原因见上）。三步 exit 0；风险标记 B4 60万 7 名、B4 100万 9 名、capacity_adv 4 名，权重未改 | 6.5s | 816MB |
| 4 | alert-ingest（真实 ALERTS_latest.json，preopen 22:57 ET） | PASS：63 行（行业加个股），unmapped_industries=[] → data/v2/alerts/alerts_20261013.parquet | 0.35s | 133MB |
注：步 3 在步 4 之后又跑了一次，以便带上真实预警；上表风险标记数来自这次重跑。

## 纸面输出路径与 NAV 尾值
- capacity_adv（paper-daily 演练副本，不覆盖原纸面轨）：
  - 权重：output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet
  - NAV：output/loop/paper_daily_20261013/capacity_adv_paper/aum_{600000,1000000}/X2/BOOK/nav.csv
  - 60万：09-30 810,046；10-08 811,226；10-09 811,507。100万：09-30 1,306,935；10-08 1,309,138；10-09 1,308,840。
  - 原纸面轨 NAV（符号链接，未动）：output/strategy_paper_capacity_adv/aum_*/X2/BOOK/nav.csv
- B4：
  - 权重：FROZEN_CONFIG 指向 output/small_aum_concentration/v2/B_B4_50_25_25_topN_{60w,100w}_20261009.parquet
  - 回填 NAV：output/strategy_paper_b4/backfill_x2/aum_{600000,1000000}_run/aum_*/X2/BOOK/nav.csv
  - 60万：09-30 838,926；10-08 833,384；10-09 832,994。100万：09-30 1,373,090；10-08 1,365,777；10-09 1,363,919。
  - 前向 NAV：output/strategy_paper_b4/forward/…/FWD/BOOK/nav.csv（WAITING，起点 2026-11-02）。
- 合并对账：output/loop/paper_daily_20261013/paper_daily_recon.json；风险标记：同目录 risk_flags.parquet。

## 剩余缺口
1. **etf_daily_adj（510300 close_hfq、基金复权因子）不在 Data 日更里，停在 10-09**。它是 Book-Smoke 的日历和 C0 来源，需要 Data 纳入日更，或由 Eng 改为读 etf_510300 加 fund_adj（需单独授权改引擎）。
2. X2 窗口写死到 10-09；纸面日更 NAV 需要一个“X2 + 前向”的窗口定义（前向窗 FWD 已在 b4_paper 中按运行时注入，capacity_adv 尚无对应前向）。
3. 两轨权重都只到 10-09：AI 的 B4 续出（research/b4_paper_extend.py --run-legs）本次未跑（RSS/耗时未测）；capacity_adv 没有日更续出脚本。
4. Alpha 标签解析只看 ACCEPT 文档开头，部分叶（如 moneyflow_resid 被 Alpha 判 DONE_FAIL、accrual/margin 为 WATCH）显示 unlabeled，需要 Alpha 提供机读标签文件。
5. 预警失效时间是 Eng 暂定的 24h；AI 源数据没有 expiry 字段。
6. 无盘中数据源（只有 EOD）；交易日历未建模 A 股节假日。
7. 510300 在 10-12、10-13 的 turnover 为空：引擎用 volume/amount 计算成交与冲击，不受影响；任何读 turnover 的信号会受影响。
