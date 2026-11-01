# 统一记分卡 + 闭环缺口 Eng 回执（2026-10-14 ET，研究/paper，live=false）

## 1. 统一记分卡
- 代码：`quantlab/portfolio/scorecard.py`，paper-daily 结束时自动调用。输出 `output/loop/paper_daily_<日期>/scorecard.{json,md}` 和 `output/loop/scorecard_latest.{json,md}`。
- 只复用现成 NAV，不重跑。X2 的 CAGR/MDD 取引擎 summary.json（与各回执口径一致）；月/日胜率、月胜C0、年化换手（actual_weights 单边 ×244）从 NAV/权重算。X2/X2H/FWD 分段不合并；X2H 太短，不给 CAGR；FWD 自 11-02 起；缺失一律写 missing。

| 轨道 | AUM | 段 | CAGR% | MDD% | Calmar | 月胜率% | 日胜率% | 月胜C0% | 年化换手 | 成本/AUM% | ΔCAGR vs capadv | ΔMDD vs capadv | ΔCAGR vs B4 | ΔMDD vs B4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| capacity_adv [PAPER] | 60万 | X2 | 13.82 | -10.07 | 1.37 | 52 | 52.7 | 48 | 4.6 | 1.72 | 0.00 | 0.00 | -1.28 | 3.77 |
| capacity_adv [PAPER] | 60万 | X2H | missing | -0.15 | missing | missing | 50.0 | missing | missing | missing | missing | missing | missing | missing |
| capacity_adv [PAPER] | 60万 | FWD | missing |||||||||||| official forward starts 2026-11-02 |
| capacity_adv [PAPER] | 100万 | X2 | 12.23 | -11.62 | 1.05 | 59 | 53.6 | 48 | 4.7 | 1.71 | 0.00 | 0.00 | -2.00 | 1.55 |
| capacity_adv [PAPER] | 100万 | X2H | missing | -0.11 | missing | missing | 50.0 | missing | missing | missing | missing | missing | missing | missing |
| capacity_adv [PAPER] | 100万 | FWD | missing |||||||||||| official forward starts 2026-11-02 |
| B4 conc 50/25/25 [PAPER] | 60万 | X2 | 15.11 | -13.85 | 1.09 | 62 | 52.5 | 59 | 6.9 | 2.48 | 1.28 | -3.77 | 0.00 | 0.00 |
| B4 conc 50/25/25 [PAPER] | 60万 | X2H | missing | 0.00 | missing | missing | 100.0 | missing | missing | missing | missing | missing | missing | missing |
| B4 conc 50/25/25 [PAPER] | 60万 | FWD | missing |||||||||||| official forward starts 2026-11-02 |
| B4 conc 50/25/25 [PAPER] | 100万 | X2 | 14.24 | -13.17 | 1.08 | 55 | 52.9 | 59 | 6.1 | 2.22 | 2.00 | -1.55 | 0.00 | 0.00 |
| B4 conc 50/25/25 [PAPER] | 100万 | X2H | missing | -0.09 | missing | missing | 50.0 | missing | missing | missing | missing | missing | missing | missing |
| B4 conc 50/25/25 [PAPER] | 100万 | FWD | missing |||||||||||| official forward starts 2026-11-02 |
| insider_increase | 60万 | X2 | 13.14 | -16.50 | 0.80 | 52 | 54.5 | 59 | 6.2 | 2.31 | -0.68 | -6.42 | -1.97 | -2.65 |
| insider_increase | 100万 | X2 | 13.14 | -17.20 | 0.76 | 52 | 55.0 | 59 | 6.3 | 2.50 | 0.90 | -5.58 | -1.10 | -4.03 |
| earnings_event | 60万 | X2 | 13.64 | -18.29 | 0.75 | 55 | 53.6 | 45 | 4.2 | 1.18 | -0.19 | -8.21 | -1.47 | -4.44 |
| earnings_event | 100万 | X2 | 13.87 | -19.08 | 0.73 | 52 | 53.1 | 41 | 4.4 | 1.32 | 1.63 | -7.46 | -0.37 | -5.91 |
| equity_incentive | 60万 | X2 | 14.31 | -14.80 | 0.97 | 52 | 51.8 | 45 | 4.4 | 1.58 | 0.49 | -4.72 | -0.79 | -0.95 |
| equity_incentive | 100万 | X2 | 15.18 | -15.58 | 0.97 | 48 | 52.2 | 48 | 4.7 | 1.75 | 2.95 | -3.96 | 0.94 | -2.41 |
| capadv+insinc 70/30 | 60万 | X2 | 11.68 | -10.68 | 1.09 | 55 | 54.1 | 52 | 4.6 | 1.91 | -2.15 | -0.60 | -3.43 | 3.17 |
| capadv+insinc 70/30 | 100万 | X2 | 13.18 | -12.67 | 1.04 | 55 | 54.8 | 52 | 5.1 | 1.93 | 0.94 | -1.04 | -1.06 | 0.50 |
| capadv+insinc 80/20 | 60万 | X2 | 11.38 | -10.46 | 1.09 | 55 | 54.7 | 52 | 4.5 | 1.92 | -2.44 | -0.38 | -3.73 | 3.39 |
| capadv+insinc 80/20 | 100万 | X2 | 13.30 | -11.22 | 1.19 | 59 | 55.4 | 52 | 5.0 | 1.97 | 1.07 | 0.40 | -0.93 | 1.95 |
| capadv+earnevt 70/30 | 60万 | X2 | 12.73 | -11.29 | 1.13 | 62 | 54.0 | 52 | 4.2 | 1.65 | -1.09 | -1.21 | -2.37 | 2.56 |
| capadv+earnevt 70/30 | 100万 | X2 | 13.42 | -13.27 | 1.01 | 55 | 53.4 | 59 | 4.6 | 1.63 | 1.18 | -1.64 | -0.82 | -0.09 |
| capadv+earnevt 80/20 | 60万 | X2 | 12.38 | -11.04 | 1.12 | 55 | 54.3 | 52 | 4.2 | 1.68 | -1.45 | -0.97 | -2.73 | 2.81 |
| capadv+earnevt 80/20 | 100万 | X2 | 13.60 | -12.05 | 1.13 | 55 | 53.3 | 52 | 4.6 | 1.68 | 1.37 | -0.42 | -0.64 | 1.12 |
| capadv+eqincent 70/30 | 60万 | X2 | 11.74 | -10.37 | 1.13 | 62 | 53.1 | 48 | 4.1 | 1.66 | -2.08 | -0.29 | -3.36 | 3.48 |
| capadv+eqincent 70/30 | 100万 | X2 | 13.75 | -12.08 | 1.14 | 55 | 52.5 | 55 | 4.6 | 1.71 | 1.52 | -0.45 | -0.49 | 1.10 |
| capadv+eqincent 80/20 | 60万 | X2 | 11.40 | -9.94 | 1.15 | 55 | 54.0 | 48 | 4.2 | 1.71 | -2.42 | 0.13 | -3.71 | 3.91 |
| capadv+eqincent 80/20 | 100万 | X2 | 12.67 | -11.41 | 1.11 | 55 | 53.3 | 52 | 4.5 | 1.71 | 0.44 | 0.21 | -1.56 | 1.76 |
| conc_v2 CORE | 60万 | X2 | 13.69 | -12.57 | 1.09 | 59 | 53.4 | 52 | 3.8 | 1.31 | -0.13 | -2.50 | -1.41 | 1.27 |
| conc_v2 CORE | 100万 | X2 | 13.83 | -11.66 | 1.19 | 48 | 52.7 | 48 | 4.5 | 1.67 | 1.60 | -0.04 | -0.41 | 1.51 |
| conc_v2 B1_equal topN | 60万 | X2 | 15.97 | -16.49 | 0.97 | 55 | 53.1 | 59 | 7.3 | 2.67 | 2.14 | -6.42 | 0.86 | -2.64 |
| conc_v2 B1_equal topN | 100万 | X2 | 14.50 | -15.22 | 0.95 | 59 | 54.0 | 55 | 6.4 | 2.36 | 2.27 | -3.60 | 0.27 | -2.05 |
| conc4leg B1eq+eqincent | 60万 | X2 | 14.49 | -13.81 | 1.05 | 59 | 52.9 | 55 | 6.1 | 2.36 | 0.67 | -3.73 | -0.61 | 0.04 |
| conc4leg B1eq+eqincent | 100万 | X2 | 13.24 | -13.90 | 0.95 | 55 | 54.0 | 66 | 5.6 | 2.05 | 1.01 | -2.27 | -0.99 | -0.72 |
| C0 510300 | 60万 | X2 | 11.27 | -16.24 | 0.69 | 62 | 52.2 | missing | missing | missing | -2.56 | -6.17 | -3.84 | -2.40 |
| C0 510300 | 100万 | X2 | 11.27 | -16.24 | 0.69 | 62 | 52.2 | missing | missing | missing | -0.97 | -4.62 | -2.97 | -3.07 |

missing = 该指标无现成数据，未编造。X2H 为桥接段（太短，只给总收益/MDD/日胜率）；FWD 自 2026-11-02 起。

## 2. 缺口
- NAV 前滚：freshness 读 `output/daily_update_status.json`（status=ok、target_trade_date=2026-10-13、tables.etf_daily_adj.last_date=2026-10-13 ≥ 目标）→ fresh。01:2x ET 运行 `paper-daily --run-nav`（无其它大任务）：exit 0，墙钟 43s，峰值 RSS 815MB；两条扩展都是 NOOP_EXISTS_IDENTICAL（r2 = 20261013 内容）；capacity_adv weight-gate PASS；B4 rehash（含 cadence）PASS，FROZEN_CONFIG 指向 _r2；X2H：capacity_adv 60万 816,368 / 100万 1,317,300（10-13），B4 X2H 已生成；track_status capacity_adv=OK_HOLD_EXTEND，b4=OK。
- alpha_labels.json：已接入，loop-sync 回退解析 0 个（见上一份回执）。
- capacity_adv 10-30：AI 扩展脚本的前向调仓日 = SSE trade_cal 每月最后开市日（10-30 is_open=1，已在 trade_cal 中）；paper-daily 顺序：extend → weight-gate（历史逐行 + 新行规则）→ pin 切片校验 → recompute_hook 读 AI 的 rebal_check/simulate；月末守卫 next_scheduled_rebalance=2026-10-30。如果 10-30 没有新权重 → PENDING。10-30 数据到之前无法端到端实测。注：freshness 仍用工作日日历，可改用同一个 trade_cal（建议）。

## 3. capacity_adv pin 改为历史切片 hash（Strategy 裁定）
- `slice_digest`：pyarrow 按 10 万行批流式读取，过滤 date ≤ pin_date（2026-10-13；d1 用 trade_date，pit 用 session），固定列序（按名排序）。行级 hash_pandas_object 做多重集摘要（行数 + 和 + 异或，与行顺序无关，因此不需要全局排序、内存低），再 sha256。追加新日期不影响；历史改写 → PENDING。
- 两个文件都按切片规则处理（mid_large_members_pit 是否只追加无法事后证明，切片规则两种情况都适用）。整文件 sha 仅记录参考。
- 每次 paper-daily 跑一次；耗时/RSS 写入 FROZEN_CONFIG.last_slice_check 和 recon：d1 约 8s、pit 约 2s，峰值 RSS 约 310-354MB（首版整行组读取曾到 1.2GB，已改为批读）。不再需要每天手工 repin。
- 【已解决 2026-10-14】Strategy 已接受与顺序无关的切片 hash；Data 确认这次 D1 重写 history_diff_rows=0（≤10-13 历史未变），不再列为风险。原记录：daily_basic_full_tushare.parquet 在 2026-10-13 23:42 ET 被 Data 重写（size 744049878，整文件 sha 3356730c…，不再是 AI 记录的 4820339f…）。切片 pin 是在重写之后做的，所以无法判断重写是否改了 ≤10-13 的历史行；建议请 Data 确认是只追加/修正当日数据。

## 4. 盘中数据
见 docs/v2/INTRADAY_DATA_FEASIBILITY_ZH.md（tushare 代理探测超时、权限未定；新浪通；东财 502）。
