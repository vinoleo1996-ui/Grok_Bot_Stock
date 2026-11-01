# ACCEPTED_DEFAULTS — platform default data paths + overall gate

## Approval provenance
- **Leo confirmed in Eng chat 2026-10-10 20:52 ET; Data acceptance all PASS**
  (docs/v2/PROMOTION_ACCEPTANCE.md, output/d1/ENG_PING_PATHS.json: five gates PASS,
  `promotion_approved_overall=true`).
- Scope: **data/platform gate only.** This says nothing about strategy performance,
  paper NAV quality, or go-live. No such conclusion is made here.

## The single overall gate
`quantlab/promotion_gate.py`

```python
OVERALL_PROMOTION_OVERRIDE: bool | None = None   # None = follow ENG_PING
```
- `overall_promotion_approved()` is THE gate; currently True (follows ENG_PING
  `promotion_approved_overall`).
- To re-freeze: set `OVERALL_PROMOTION_OVERRIDE = False` (one line). Everything below follows.
- Consumers (all compare to the gate, not to a hardcoded False):
  `V2DataRoots.promotion_approved`, `mandate_v2` (`promotion_approved`, `require_not_promoted()`
  now = gate-consistency check), `d1_masks` result + notes, `strategy_feed`
  (`d1_members_at`, feed meta), paper runners (`v2_strategy_paper*.py`), smokes
  (`v2_smoke`, `v2_proto_smoke`, `v2_eng_smoke`).
- `dataset_accepted(key)` = per-dataset acceptance from ENG_PING `acceptance[key].pass`.

## Defaults before → after
| item | before | after (default) | fallback |
|---|---|---|---|
| float_mktcap daily | `float_mktcap_daily_20260630_20261009.parquet` | `float_mktcap_daily_tushare.parquet` (session-filtered pyarrow read; trade_date→session; available_at = session 18:00 proxy) | old daily (if session empty) → `float_mktcap_asof*.parquet` |
| asof_extend merge panels | `asof_extend_202610/panels` | `asof_extend_tushare_202610/panels` (trade_date→event_time, instrument_id added, tradestatus→open_status, volume in shares = D0) | per-instrument `asof_extend_202610/panels`; calendar + `d0_as_of` still from `asof_extend_202610` (tushare dir has none). 1c85 untouched |
| financials available_at | `financials_available_at_latest_per_key.parquet` (via `load_financials_pit`) | `load_financials_available_at()` → `financials_available_at_tushare.parquet` | legacy latest_per_key |
| dividend / corporate actions | (no reader) | `load_dividends()` → `corporate_actions/dividend_tushare.parquet` (adds instrument_id from ts_code) | — |
| SW L1 | tushare | tushare (unchanged) | prefix / vote |

## Per-dataset honesty (unchanged)
- Accepted (dataset promotable=True): SW tushare, float daily tushare, extend tushare, financials_available_at tushare, dividend tushare.
- Still non-promotable: SW prefix/vote/xls, legacy float daily/asof (stale_carry), `load_financials_pit` metric/value table (legacy; manifest true no longer raises when financials acceptance PASS, but view stays promotable=False), EP research (`ep_research_asof_20260630`), EM EITIME, Beta/factor outputs.
- EP: **not re-derived** — tushare financials table is timing-only (no metric values), so EP stays on `ep_research_asof_20260630.parquet` (research).

## Notes
- `strategy_feed` disk cache key now includes extend source name → old caches are not reused.
- Running jobs (Strategy Full D1+TURN) were started before this change and keep old imports.

## 2026-10-10 21:35 ET — EP + financials defaults switched to accepted Tushare

Provenance: Data rebuilt numeric PIT `financials_pit_tushare.parquet` and re-accepted it
(ENG_PING `acceptance.financials_pit_tushare.pass=true`, 2026-10-10 21:32 ET; manifest
`data/v2/financials_pit/financials_pit_tushare_manifest.json`). Leo approved overall=true
in the Data chat and confirmed in the Eng chat (21:35 ET): keep overall true and switch
EP + financials defaults. Backups of edited files: `/tmp/epfin_bak/`.

| item | before | after (default) |
| --- | --- | --- |
| `load_financials_pit()` | `financials_available_at_latest_per_key.parquet` (research) | `financials_pit_tushare.parquet`, melted to long (net_profit, revenue, roe, debt_to_assets, gross_margin, basic_eps, bps); all update versions kept; `prefer="d0_announced_on"` / `"baostock"` still available |
| `load_ep_research()` | `ep_research_asof_20260630` for every session (stale carry) | latest `ep_tushare_asof_YYYYMMDD` with asof <= `session`; `ep := ep_latest`; rows with available_at > asof blanked; fallback to research table when no tushare asof <= session |
| dataset acceptance | always non-promotable | `dataset_accepted("financials_pit_tushare")` |
| `financials_available_at_tushare` | treated as accepted | timing index only (Data corrected acceptance to pass=false as numeric source); smoke now only requires tushare variant |

PIT: `available_at` (Asia/Shanghai date) <= session everywhere (`financials_metric_asof`,
EP asof selection, `compute_ep_cross_section` drops a passed-in EP view dated after session).

Not switched / caveats:
- `ocf_to_profit` (Q_ACCRUAL_PROXY) defaults to accepted `ocf_to_profit_pit_tushare` (legacy opt-in only).
- Sessions before 2018-01-02 fall outside daily PIT EP → research fallback (itself dated 2026-06-30; labeled lookahead).
- Factor/strategy outputs stay research-grade (`financials_promotable=False` in factor meta).
- Paper runners (Strategy-owned) call `load_ep_research(roots=...)` without session → latest file;
  the EP compute path re-selects per session for PIT.

## 2026-10-10 晚：EP PIT 日表 + ocf_to_profit PIT（Data 验收 PASS，ENG_PING `ep_ocf_update`）

| 项 | 之前默认 | 现在默认 | 回退/旧口径 |
|---|---|---|---|
| EP (`load_ep_research`) | `ep_tushare_asof_*`（asof<=session），2026-06-30 前退回 `ep_research_asof_20260630`（有前视） | `data/v2/ep/ep_pit_daily_tushare.parquet`：取 trade_date<=session 的最近一天（pyarrow 过滤，只读一天）；E=TTM 归母净利，mv=total_mv；available_at 18:00 SH，**当日公告次日才可用**（读取时再兜底屏蔽 available_at 日期>=trade_date 的行）；`dataset_accepted("ep_pit_daily_tushare")` | 覆盖 2018-01-02..2026-10-09 之外：`ep_tushare_asof_*` → `ep_research_asof_*`；研究回退若 asof 晚于 session，quality_label 带 `;lookahead_outside_pit_coverage`。显式 `prefer="tushare"` 仍可用旧 asof 表 |
| `ocf_to_profit`（`load_financials_pit`） | 旧研究表行拼接（`legacy_research_ocf_to_profit`） | `data/v2/financials_pit/ocf_to_profit_pit_tushare.parquet`（n_cashflow_act/n_income，按报告期+available_at；|NP|<1M→NaN）；source=`ocf_to_profit_pit_tushare`；`dataset_accepted("ocf_to_profit_pit_tushare")` | `load_financials_pit(ocf_source="legacy_research")` |

v2_min_pipeline 元数据：`metric_used="ep_pit_daily_tushare"`，`ep_definition="ep_pit_daily_ttm_attr_np_over_total_mv"`。
注意：EP 定义从 ep_latest/float_mktcap 换成 TTM 归母/total_mv，因子值与之前不可直接比。Strategy 正在跑的任务需重开才会用新默认。
Execution（execution.py）新增：effective_n / effective_n_mean、impact_bp_per_traded、`return_stats_ex_suspended`（opt-in）、`impact_k_by_bucket`+`size_bucket`（默认 None；`IMPACT_K_SIZE_BUCKET_REFERENCE` = large 0.45% / small 0.74% / micro 1.82% 仅文献参考，A 股由 Strategy 标定）。
备份：/tmp/epocf_bak/

## 2026-10-10/11 — EP / ocf coverage extend to 2018-01-02

- `ep_pit_daily_tushare.parquet`: trade_date **2018-01-02 .. 2026-10-09** (2125 sessions);
  `load_ep_research(prefer="pit_daily")` picks it; 2019 sessions have 0 lookahead rows
  (available_at 18:00 SH → usable next session). Pre-2018 still falls back to research asof
  (labeled `;lookahead_outside_pit_coverage`).
- `ocf_to_profit_pit_tushare` (per-report, default in `load_financials_pit`) + daily twin
  `ocf_to_profit_pit_daily_tushare` (same 2018-01-02..2026-10-09 coverage). Factors keep
  per-report PIT via `financials_metric_asof`; daily is for cross-section convenience.
- Amount/volume units (ENG_PING `units_note`): prefer `asof_extend_tushare_202610`
  (volume=股, amount=元). Legacy `asof_extend_202610` may be lots — `load_execution_panels`
  honors `volume_shares` / `volume_unit` when present.
