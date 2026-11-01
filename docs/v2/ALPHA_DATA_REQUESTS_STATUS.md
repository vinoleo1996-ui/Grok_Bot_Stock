# ALPHA_DATA_REQUESTS_STATUS（研究级，promotion_approved=false；未改动 promotion_approved_overall）
更新：2026-10-10 ~21:50 ET。依据 output/alpha/ALPHA_REBUILD_HYPOTHESES_ZH.md。

| # | 需求 | 状态 | 路径 | 覆盖 | 已知缺口 |
|---|---|---|---|---|---|
| 1 | 带数值财务 PIT | 有 | data/v2/financials_pit/financials_pit_tushare.parquet | 422,129 行 / 5,910 只；fina_indicator 已重拉（fina_indicator_v2，无 100 行截断） | 52 只两源均无 fina_indicator；由另一任务负责 |
| 2 | 涨跌停/停牌/成交额覆盖 | 有（沪深）/部分（北交所） | docs/v2/LIMIT_COVERAGE_2018.md；1c85 panels；asof_extend_tushare_202610 | 2018-01→2026-06（1c85）+ 2026-07→2026-10-09（extend） | 北交所在 1c85 缺 limit/tradestatus/open_status（约 23.3 万行）；Tushare stk_limit/suspend_d/daily 2018→2026-06 回补进行中（含北交所） |
| 3 | 沪深300/中证500/中证1000 成分+调样 | 部分 | data/v2/index_members/index_weight_csi300_500_1000.parquet；index_member_events.parquet | 月度快照 2018-01-31→2026-09-30，三个指数各 105 个 | Tushare 没有公告日；生效日只能界定在相邻两次快照之间（主要在 6 月和 12 月）；可选免费来源：中证官网调样公告（未抓） |
| 4 | 限售解禁 | 部分（补拉中） | data/v2/share_float/share_float_2018plus.parquet | 按 float_date 月窗口；字段 ann_date/float_date/float_share/float_ratio/holder_name/share_type | 2021-10 起的大月份分页失败（截至 21:45 失败 14 个月）；正按 float_date 逐日补拉 |
| 5a | 龙虎榜 top_list/top_inst | 部分（补拉中） | data/v2/dragon_tiger/ | 回补 2018→2026-10-09，按 trade_date | 约 42% 完成 |
| 5b | ST 戴帽/摘帽 | 有 | data/v2/st_events/st_events_from_namechange.parquet；namechange_all.parquet | promax relay 可用 namechange：12,832 行 / 5,903 只，公告日 1998→2026-10-09；ST 相关 3,763 条（2018 起 1,582 条） | datahub 无此接口；ann_date 是更名公告日，不是监管决定时间 |
| D | 分红 | 有 | data/v2/corporate_actions/dividend_tushare.parquet（全史，268,204 行 / 5,880 只）；dividend_by_exdate_tushare.parquet（2024+） | 实施公告 1991→2026；2018 起每年 2.7k–5.1k 条 | 全表 record/ex/pay 非空约 22%，因为预案和股东大会阶段本来没有这些日期；div_proc=实施时 ann 99.9%、record 100%、ex 99.9%、pay 93.8%；另有 imp_ann_date（实施公告日） |

## Alpha 追加
(a) extend panels 的 factor：已用 tushare_raw/adj_factor（另补拉 20260630）补齐。新增 adj_factor_tushare 列（371,051 行，0 缺失），并加 factor = D0 在 2026-06-30 的 factor × (tushare_adj_t / tushare_adj_20260630)，与 D0 尺度连续（5,523 个 panel 已衔接，其余只有 tushare 尺度，factor_basis 列标明）。修改前的备份：panels_backup_prefactor/。

(b) d1_masks 所需 D0 列覆盖（2018 起，非空 %；float_mktcap 取自 float_mktcap_daily_tushare）：
| 年 | 行 | tradestatus | open_status | is_st_at_open | limit_up | limit_down | amount | turnover | float_mktcap |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 817267 | 100.00 | 99.94 | 100.00 | 99.94 | 99.94 | 100 | 100.00 | 100.00 |
| 2019 | 884885 | 100.00 | 99.91 | 100.00 | 99.91 | 99.91 | 100 | 100.00 | 100.00 |
| 2020 | 945566 | 100.00 | 99.83 | 100.00 | 99.83 | 99.83 | 100 | 100.00 | 100.00 |
| 2021 | 1061039 | 99.75 | 99.54 | 99.75 | 99.54 | 99.54 | 100 | 99.75 | 99.75 |
| 2022 | 1170379 | 97.88 | 97.75 | 97.88 | 97.76 | 97.76 | 100 | 97.88 | 97.90 |
| 2023 | 1257953 | 96.09 | 96.01 | 96.09 | 96.01 | 96.01 | 100 | 96.09 | 96.09 |
| 2024 | 1292384 | 95.38 | 95.35 | 95.38 | 95.35 | 95.35 | 100 | 95.38 | 95.33 |
| 2025 | 1310288 | 95.20 | 95.17 | 95.20 | 95.17 | 95.17 | 100 | 95.20 | 96.54 |
| 2026 | 636103 | 94.46 | 94.41 | 94.46 | 94.42 | 94.42 | 100 | 94.46 | 100.00 |
2021 年起缺口基本都是北交所（1c85 无状态列）。

(c) 3,853 条 D0 未解释除权参考价（unexplained_ex_reference）重新核对：
方法：取 D0 当日 reference_price，与 implied = (前收 − 当日实施 cash_div_tax 合计) / (1 + stk_div) 比较，容差 max(0.011 元, 0.2%)；只用 dividend_tushare 中 div_proc=实施、ex_date 等于该交易日的记录。
结果：已解释 2,344 条；仍未解释 1,509 条，其中有分红但价格对不上 567 条（可能是配股、合并或税率口径不同），当日没有 Tushare 实施分红 942 条（可能是配股/增发/吸收合并，或除权日不一致）。明细：data/v2/corporate_actions/exrights_unexplained_recheck_tushare.parquet。配股不在 dividend 表里，需要 Tushare 配股接口（rights issue）另补。

## 后台任务（scripts/acquire/alpha_finalize.sh 会在完成后自动重建表并刷新 LIMIT_COVERAGE_2018.md）
limit_hist 950/6174；toplist 1775/4250；share_float 主窗口完成后按 float_date 逐日补拉失败月份。日志 logs/alpha_*.log，结果汇总 output/d1/alpha_build_summary.json。
