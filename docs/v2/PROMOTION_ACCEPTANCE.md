# PROMOTION_ACCEPTANCE

- checked_at: 2026-10-10T14:43:21.987009-04:00 (ET)
- rule: per-table promotion_approved reflects acceptance evidence only
- acceptance_gates: **ALL PASS** (evidence only)
- promotion_approved_overall: **true**（Leo 明确批准翻回 true（2026-10-11T09:35:17.449101+08:00）：财务数值 PIT 重建并重验通过）

## sw_l1_pit_tushare — PASS
- path: `/workspace/QuantLab/data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet`
- metrics: `{"listed_cover_frac": 1.0, "listed_n": 5573, "current_members_n": 5914, "asof_20260630_agree_vs_prefix": 0.9923, "asof_overlap_n": 5465, "rows": 7920, "n_l1": 31, "n_instruments": 5914, "available_at_nulls": 0, "in_date_min": "1984-05-09", "in_date_max": "2026-09-24"}`
- blockers: (none)

## float_mktcap_daily — PASS
- path: `/workspace/QuantLab/data/v2/float_mktcap/float_mktcap_daily_tushare.parquet`
- metrics: `{"rows": 9756821, "n_instruments": 5820, "date_min": "2018-01-02", "date_max": "2026-10-09", "asof_window_days": 68, "asof_window_median_inst": 5540, "asof_window_min_inst": 5508, "vs_asof0630_n": 5184, "vs_asof0630_within_1pct": 0.9954, "vs_asof0630_within_5pct": 0.9977, "vs_asof0630_median_abs_rel": 1e-05, "vs_asof_within_5pct": 0.9977, "vs_asof_within_1pct": 0.9954, "vs_asof_n": 5184, "vs_asof_median_abs_rel": 1e-05, "vs_asof1009_n": 955, "vs_asof1009_within_1pct": 0.9267, "vs_asof1009_within_5pct": 0.9759, "vs_asof1009_median_abs_rel": 0.0, "tencent_validate": {"built_at": "2026-10-10T11:22:45.498820-04:00", "promotion_approved": false, "n_asof": 955, "n_tencent_spot": 955, "n_merged": 955, "session_asof": "2026-10-09", "note": "Data float_mktcap_asof_2026-10-09 vs Tencent qt circ_mv (field44 * 1e8 CNY)", "stats": {"ratio_median": 0.9999988431414116, "ratio_mean": 0.99280903342602, "abs_rel_median": 2.9993079584899616e-05, "within_1pct": 0.9267015706806283, "within_5pct": 0.9759162303664921, "within_10pct": 0.9842931937172775}, "data_coverage_note": "Data daily after 2026-06-30 sparse (~956 names/session); asof_2026-10-09 has only 955 rows vs 5184 on 2026-06-30"}}`
- blockers: (none)

## daily_panels_asof_extend — PASS
- path: `/workspace/QuantLab/data/v2/asof_extend_tushare_202610/panels`
- metrics: `{"n_panels": 5578, "sample_n": 50, "amount_nn_frac_mean": 1.0, "limit_up_nn_frac_mean": 1.0, "tradestatus_panels": 50}`
- blockers: (none)

## financials_available_at — ~~PASS~~ → RETRACTED (correction 2026-10-11T09:32:40.086506+08:00)
- path: `/workspace/QuantLab/data/v2/financials_pit/financials_available_at_tushare.parquet`
- 更正：之前的 PASS 只验了时点列（ann/f_ann/available_at），表内**没有任何财务数值**；门槛过弱，撤回。仅保留为时点索引。
- 另发现：原 fina_indicator 拉取 **284 只股票被 100 行上限截断**，且只拉了 roe 等 5 个字段（无 eps/profit_dedt）。

## financials_pit_tushare — PASS (value gate)，dataset promotion_approved=false（待 Leo 审）
- path: `/workspace/QuantLab/data/v2/financials_pit/financials_pit_tushare.parquet`（manifest: `financials_pit_tushare_manifest.json`）
- 内容：income 全版本（update_flag/report_type）+ fina_indicator（重拉 v2，分页按日期窗）；available_at = f_ann_date||ann_date 18:00 Asia/Shanghai
- rows 422129 / 标的 5910
- **新门槛**：最新期 2026-06-30（合并报表）上市股 net_profit 与 eps 非空 ≥95%，且无截断
  - net_profit 99.98%，eps 98.96%，basic_eps 99.96%，revenue 99.98%，roe 98.14%，profit_dedt 96.81%（listed=5479）→ PASS
  - 截断：原 284 只 =100 行；重拉后 273 只 >100 行，其余去重后 <100，仍恰为 100 的 0 → PASS
- EP 对拍（vs ep_research_asof_20260630）：`{"old_rows": 5464, "old_ep_nonnull": 5154, "new_rows": 5910, "new_ep_latest_nonnull": 5508, "new_ep_ttm_nonnull": 5419, "overlap_both_nonnull": 5154, "pearson_ep_latest_vs_old(sane)": 0.9908, "spearman_ep_latest_vs_old": 0.9988, "spearman_ep_ttm_vs_old": 0.7988, "same_report_period_share": 0.9978, "net_profit_exact_match_share(rel<1e-4)": 0.9978}`
- caveats：fina_indicator 每 (股票,期) 仅最新快照；无资产负债表（总权益缺，仅 bps）；52 只无 fina_indicator 返回

## dividend_exrights — PASS
- path: `/workspace/QuantLab/data/v2/corporate_actions/dividend_tushare.parquet`
- metrics: `{"rows": 283482, "n_instruments": 6175, "actions_cols": ["action_id", "instrument_id", "record_date", "ex_date", "pay_date", "share_date", "cash_per_share", "share_ratio", "available_at", "source", "revision", "quality_status", "tax_policy", "action_type", "ingested_at", "availability_basis"], "actions_rows": 36442, "reconcile_date_col": "ex_date", "keys_tushare": 14843, "keys_1c85": 11419, "intersection": 11419, "only_1c85": 0, "only_tushare": 3424, "explain_frac_1c85": 1.0}`
- blockers: (none)



## ep_pit_daily_tushare — PASS（2026-10-11T10:22:52.746254+08:00）
- path: `/workspace/QuantLab/data/v2/ep/ep_pit_daily_tushare.parquet`；脚本 `scripts/build_ep_pit_daily.py`；验收 json `data/v2/ep/ep_pit_daily_tushare_acceptance.json`
- 定义：e_ttm=归母净利润(n_income_attr_p)累计值TTM(年报直接用；季报=当期累计+上年年报-上年同期累计)，每个 available_at 时点按当时可见版本(含重述)取可算TTM的最新报告期；mv=daily_basic.total_mv(元)；trade_date d 只用 available_at<=d 15:00 CST 的 E（18:00 公告当日不可见，次日起生效）
- rows 3,613,482，668 个交易日 2024-01-02~2026-10-09，5673 只；ep 非空 99.9926%（逐日最低 99.9801%）
- 无未来数据：e_available_at<=trade_date 15:00 CST 违规 0 行（100% 通过）
- 对拍 1/daily_basic.pe_ttm：2024-06-28 pearson 0.9956；2025-06-30 0.9999；2026-06-30 0.9999；2026-10-09 0.9998（中位比值≈1.0000）
- 对拍旧 ep_research_asof_20260630（2026-06-30 截面，n=5154）：pearson 0.466，spearman 0.786，符号一致 0.845。差异来自口径：旧表=单季/YTD 最新净利润÷派生流通市值，新表=TTM 归母÷总市值，属预期。

## ocf_to_profit_pit_tushare — PASS（2026-10-11T10:22:52.746254+08:00）
- 版本表 `/workspace/QuantLab/data/v2/financials_pit/ocf_to_profit_pit_tushare.parquet`（228,450 行，5867 只，报告期 2014-03-31~2026-09-30）
- 逐日 PIT `/workspace/QuantLab/data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet`（3,613,482 行，2024-01 起 668 日，覆盖 98.93%，未来数据 0 行）
- 原始 cashflow：`data/v2/tushare_raw/cashflow/`（5912 文件，2015 起公告，按日期窗口二分防 100 行截断，单股最多 88 行，无截断；45 只空=2015 前已退市）
- 定义：ocf_to_profit=cashflow.n_cashflow_act/income.n_income（YTD 累计口径，与旧 baostock CFOToNP 一致）；另给 ocf_to_profit_attr=/n_income_attr_p；available_at=两表当时可见版本的较晚公告时点(18:00 CST)；版本表每次任一侧更新(含重述)出一行
- 分母：|net_profit|<1e6 元 → ocf_to_profit=NaN，denom_small=True；净利润为负保留数值并标 np_negative=True（因子侧建议剔除或单独处理）；denom_small 占 0.94%，np_negative 占 17.60%
- 覆盖：2026-06-30 报告期上市股覆盖 99.24%（listed=5508）
- 对拍旧研究 ocf_to_profit（同股同期，n=147318）：1% 内 95.36%，5% 内 96.76%，符号一致 99.61%，pearson(截±20) 0.9904，rank 0.9916
- promotion_approved_overall 保持 true（Leo：非阻塞小 bug 不退回）


## EP / ocf_to_profit 逐日表前延至 2018-01-02 — 重验 PASS（2026-10-10T22:42:46.377378-04:00）
- ep_pit_daily_tushare：9,754,901 行，2125 日，5820 只；覆盖 99.9749%（单日最低 99.7297%）；未来数据 0 行；按年覆盖 {2018: 0.9993, 2019: 0.9995, 2020: 0.9997, 2021: 0.9998, 2022: 0.9997, 2023: 0.9998, 2024: 0.9998, 2025: 1.0, 2026: 1.0}
  - 对拍 1/pe_ttm pearson：2018-06-29 0.9860，2020-06-30 0.9974，2022-06-30 0.9953，其余同前（≥0.995）
- ocf_to_profit_pit_daily_tushare：9,754,991 行，2125 日，覆盖 99.01%，未来数据 0 行；按年覆盖 {2018: 0.9905, 2019: 0.9897, 2020: 0.99, 2021: 0.992, 2022: 0.9924, 2023: 0.9892, 2024: 0.9896, 2025: 0.9901, 2026: 0.9878}
- daily_basic total_mv 2018 起每年非空≈100%，无需补拉


## delisted D3 (B1/B3) — research PASS（2026-10-10T23:07:41.378218-04:00）
- master: `data/v2/delisted/delisted_master_tushare.parquet`（339 只，含 delist_date/last_trade_date/last_close/退市原因启发式/was_st）
- daily full: `delisted_daily_tushare.parquet`（1,241,374 行，1990-12-19~2026-07-29；未复权价+adj_factor；amount 元、volume 股、total_mv/circ_mv 元）
- daily from2015: `delisted_daily_from2015_tushare.parquet`（426,473 行；mv 非空 99.73%；adj 非空 100.00%）
- ST: `delisted_st_intervals_namechange.parquet`（792 段/282 只）；`delisted_is_st_daily_from2015.parquet`
- B3 窗 2015-06~2016-01：候选 232，有 K 线 228（98.3%），中位交易日数 141.5
- 跳过 T600018.SH（临时码无返回）

## fina_audit D4 — 小盘 3001-5000 带（2026-10-10T23:07:41.378218-04:00）
- 重拉空文件 215/216 后重建 `audit_opinion_pit_tushare.parquet`（56,144 行 / 5,807 只）
- 严格「上一年年报」：2024-06-28 缺 0；2025-06-30 缺 1（603210 新上市无 2024 年报）；2026-06-30 缺 1（688781 新上市无 2025 年报，但有 2024 年报）
- 「任意已公告年报」定义下三截面 missing=0。剩余缺口属 IPO 当年无完整上一年年报，非源缺失。
