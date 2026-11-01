# QuantLab DATA V2 — Free Hunt (resume after box reboot)

> Updated: 2026-10-10T11:34:04.530275-04:00 (America/New_York)  
> Policy: **Leo free-only** — no Tushare/Wind/JQ credentials. No Mac CopyToBox.  
> Do **not** fight Dist Data `enrich_asof_curl.py` on asof amount (PID may be live).  
> All artifacts: `promotion_approved=false`.

Landing root: `QuantLab/data/v2/free_hunt/`

---

## Executive ceilings (unchanged)

| Gap | Free ceiling |
|---|---|
| Daily float_mktcap | Proxy via amount/turnover or close×float_share; **not** exchange official free-float; NetEase chddata **dead**; akshare `stock_zh_a_hist_163` **removed** |
| Fundamentals available_at | EM `NOTICE_DATE`/`EITIME` + CNInfo `announcementTime` proxies; **no as-filed restatement ledger** |
| SW_L1 official in/out | **No free full-market API**; best = local `StockClassifyUse_stock.xls` prefix method; fresh XLS download from swsresearch **timed out** from box |

---

## 1) Float mktcap — validation vs Data research proxy

### Data coverage reality (post reboot)

| Artifact | Stats |
|---|---|
| `float_mktcap_asof_2026-06-30.parquet` | 5506 rows / **5184** non-null |
| `float_mktcap_asof_2026-10-09.parquet` | **only 955** rows (enrich still climbing) |
| `float_mktcap_daily_20260630_20261009.parquet` | 88106 rows / 5193 names; **median ~956 names/session** after 6/30; only ~958 names have ≥60 days |

### Validation landed this resume

| Check | Result | Path |
|---|---|---|
| Data asof 2026-10-09 vs Tencent qt circ_mv | n=955; **within 1% = 0.9267015706806283**; within 5% = 0.9759162303664921; median abs_rel = 2.9993079584899616e-05 | `free_hunt/mktcap/validate_data_asof_vs_tencent_20261009.{json,parquet}` |
| Data daily vs free_hunt hist (2026-06-30, 300 codes) | ~74% within 1%, **99% within 5%** (prior session; same amount/turnover identity) | (inline prior) |
| Extend-derived vs Data daily | n=2345; **within 1% = 1.0** (turnover **must** be treated as percent) | `float_mktcap_from_asof_extend.parquet` |
| Extend-derived vs Tencent 10-09 | n=35; within 1% = 0.45714285714285713; within 5% = 1.0 | same |

### Prior free_hunt hist (still best long history)

| Item | Value |
|---|---|
| Path | `free_hunt/mktcap/float_mktcap_hist_from_1c85/` |
| Panels | 5439 written / 6026 scanned |
| Rows | 9141365 |
| Window | 2018-01-01 → 2026-06-30 |
| Method | amount/(turnover_pct/100) from 1c85 panels |

### Extend window derivation (this resume)

| Item | Value |
|---|---|
| Path | `free_hunt/mktcap/float_mktcap_from_asof_extend.parquet` |
| Instruments with amount+turnover so far | **67** / 5201 panels |
| Rows | 4489 (2026-07-01 → 2026-10-09) |
| Note | READ-ONLY from Data asof_extend; **did not write/fight enrich**. Coverage grows as Data fills amount/turnover. |

### Dead / blocked free sources probed

- NetEase `quotes.money.163.com/service/chddata.html` — connection failed  
- akshare `stock_zh_a_hist_163` — attribute removed in akshare 1.18.97  
- EM `push2` stock/get & bulk kline — intermittent RemoteDisconnected / rate limit (pilot aborted)  
- BaoStock live — module missing in probe venv; historically blacklisted on box  

### Practical recommendation

1. Trust Data asof/proxy for **research** shell filters when validated vs Tencent (~93% within 1% on 955-name 10-09 asof).  
2. Use `float_mktcap_hist_from_1c85` for **2018–2026-06-30** daily proxy.  
3. Post-6/30: wait for Data enrich OR keep re-deriving from asof_extend amount/turnover (percent).  
4. **Do not promote** — not official free-float.

---

## 2) Fundamentals / EP with announcement timing

### Landed this resume

| Artifact | Stats |
|---|---|
| `free_hunt/fundamentals/em_yjbb_pit_seed_notice_le_20260630.parquet` | **3000** rows / **2366** names; filter `NOTICE_DATE<=2026-06-30` |
| `available_at` | **100% from EM `EITIME`** (ingest timestamp) — better than announced_on@18:00 convention |
| `ep_from_em_yjbb_asof_20260630.parquet` | **1430** EP rows; sane(-1,1)=1427; median_sane=0.003785077546496311 |
| vs Data EP | n=1412; corr=0.5137392203386644; median_abs_rel=0.0 |
| `cninfo_periodic_announcements_sample.parquet` | 80 rows / 4 names; HTTPS works; `announcementTime` epoch |

### Fields of value (EM `RPT_LICO_FN_CPD`)

- `NOTICE_DATE`, **`EITIME`** (intraday), `REPORTDATE`, `PARENT_NETPROFIT`, `BASIC_EPS`, `TOTAL_OPERATE_INCOME`, `WEIGHTAVG_ROE`  
- Full market pages ≈ **2197×50** under `NOTICE_DATE<=2026-06-30` filter — this resume only pulled **60 pages** (pilot)

### Still blocked for promote

- No as-filed vs restated value chain  
- Period profit ≠ certified TTM  
- CNInfo full-market crawl fragile; sample only  
- Data's `financials_available_at` remains primary 1c85 proxy table (untouched)

### Recommendation

- Research EP: prefer Data `ep_research_asof_*` + optionally cross-check EM yjbb EITIME  
- To improve available_at: batch more EM pages + CNInfo clock (date-level often midnight)  
- **Cannot promote** without as-filed ledger

---

## 3) SW_L1 industry change history

### Best free artifact (already on box; still best)

| Item | Value |
|---|---|
| Path | `free_hunt/sw_pit/sw_l1_pit_from_xls_prefix.parquet` |
| Rows / names | 12925 / 5930 |
| Method | `swsresearch_StockClassifyUse_stock.xls + industry_code[:2]+0000 as L1 (simonlin/a-stock-data method); out_date=next_in-1d` |
| vs Data vote method | prior 7115 rows → new 12925 (prefix better than majority vote) |

### Resume probe results

- Fresh `StockClassifyUse_stock.xls` from swsresearch.com — **timeout / unreachable** from box  
- akshare `index_component_sw` — works but **current weights + 计入日期 only**, no out_date ledger  
- GitHub code search — 401 without token  
- BigQuant / CnOpenData / Tushare / JQ / Wind — gated (unchanged)

### Conclusion

**No freer official SW_L1 full in/out tape found.** Research must keep using XLS-prefix PIT with `promotion_approved=false`.

---

## Coordination (writers)

| Path | Writer |
|---|---|
| `data/v2/asof_extend_202610/` amount enrich | **QuantLab Data only** |
| `data/v2/float_mktcap/*` | QuantLab Data |
| `data/v2/free_hunt/**` | Free-hunt executor (this doc) |
| `data/v2/financials_pit/financials_available_at*` | QuantLab Data (do not overwrite) |

---

## New files this resume

```
data/v2/free_hunt/mktcap/validate_data_asof_vs_tencent_20261009.json
data/v2/free_hunt/mktcap/validate_data_asof_vs_tencent_20261009.parquet
data/v2/free_hunt/mktcap/float_mktcap_from_asof_extend.parquet
data/v2/free_hunt/mktcap/float_mktcap_from_asof_extend_manifest.json
data/v2/free_hunt/fundamentals/em_yjbb_pit_seed_2024plus.parquet
data/v2/free_hunt/fundamentals/em_yjbb_pit_seed_notice_le_20260630.parquet
data/v2/free_hunt/fundamentals/ep_from_em_yjbb_asof_20260630.parquet
data/v2/free_hunt/fundamentals/em_yjbb_pit_manifest.json
data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_sample.parquet
data/v2/free_hunt/fundamentals/cninfo_periodic_announcements_manifest.json
data/v2/free_hunt/sw_pit/resume_probe_20261010.json
data/v2/free_hunt/logs/resume_probes_*.json
```

---

## Next free-only actions (if continued)

1. Re-derive `float_mktcap_from_asof_extend` after Data enrich coverage rises (target ≫67 names/session).  
2. Page more EM `RPT_LICO_FN_CPD` (up to ~2200 pages) for fuller EP/EITIME seed — slow, free.  
3. Optional CNInfo multi-name announcementTime backfill for available_at cross-check.  
4. Retry swsresearch XLS download later; keep prefix PIT as research default.  
5. Never set `promotion_approved=true` on free path alone.

---

## Continue pass (2026-10-10T12:20:41.480703-04:00)

- Re-derived `float_mktcap_from_asof_extend` as enrich climbed.
- Expanded EM `RPT_LICO_FN_CPD` EITIME seed (~250 pages this pass; merged).
- Broadened CNInfo sample; added `exrights_sharebonus_crosscheck_sample`.
- See `output/d1/LEO_STATUS_ZH.md` + `ENG_PING_PATHS.json`.
- `promotion_approved=false`.
