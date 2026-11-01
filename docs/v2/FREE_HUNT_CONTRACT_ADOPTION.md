# Free Hunt → Research Contract Adoption

**Updated:** 2026-10-10T11:36:38.603354-04:00 (America/New_York)  
**Policy:** Leo free-only · `promotion_approved=false` always · no Mac CopyToBox · do not fight `enrich_asof_curl.py`  
**Source hunt doc:** `/workspace/QuantLab-DATA_V2_FREE_HUNT.md`  
**Artifacts root:** `/workspace/QuantLab/data/v2/free_hunt/`

This document states what from free_hunt is **adopted into the research contract** for Eng/Alpha consumption vs **parked**. Nothing here is promotion-grade.

---

## Hard rules (unchanged)

1. `promotion_approved=false` on every path below.
2. Do **not** overwrite `data/v2/financials_pit/financials_available_at.parquet`.
3. Primary float_mktcap remains `data/v2/float_mktcap/`; free_hunt paths are secondary / validation / history.
4. Do not touch / kill `enrich_asof_curl.py` (PID may be live).
5. No paid APIs; no Mac large copies.

---

## Adopted into research contract

### A) Float mktcap — secondary + validation

| Role | Path | Use |
|---|---|---|
| **Primary (unchanged)** | `data/v2/float_mktcap/` (`float_mktcap_daily_*`, `float_mktcap_asof*`) | Shell filter / Eng mask kick-shell |
| Validation | `free_hunt/mktcap/validate_data_asof_vs_tencent_20261009.json` (+ `.parquet`) | asof 2026-10-09 vs Tencent circ_mv: **~92.7% within 1%**, ~97.6% within 5% (n=955) |
| Long hist (secondary) | `free_hunt/mktcap/float_mktcap_hist_from_1c85/` | 2018-01-01→2026-06-30 daily proxy via amount/(turnover%/100); 5439 panels / ~9.1M rows |
| Post-0630 bridge (secondary) | `free_hunt/mktcap/float_mktcap_from_asof_extend.parquet` | READ-ONLY derive from asof_extend amount+turnover; coverage grows with enrich (~67 names so far) |

**Limitations:** Not exchange official free-float; NetEase chddata dead; post-6/30 primary asof still sparse (~955) until enrich fills amount/turnover.

### B) Financials / EP — SECONDARY research only

| Role | Path | Use |
|---|---|---|
| **Primary available_at (untouched)** | `financials_pit/financials_available_at.parquet` | 1c85 announced_on@18:00 proxy |
| **Primary EP research** | `financials_pit/ep_research_asof_20260630.parquet` | Eng/Alpha default EP |
| Secondary EM EITIME seed | `financials_pit/research_em_yjbb_pit_seed_notice_le_20260630.parquet` | `available_at` **100% from EM `EITIME`** — better intraday proxy for research cross-check |
| Secondary EM EP | `financials_pit/research_ep_from_em_yjbb_asof_20260630.parquet` | Cross-check vs primary EP (corr≈0.51 on overlap; median abs rel 0) |
| Secondary EM 2024+ pilot | `financials_pit/research_em_yjbb_pit_seed_2024plus.parquet` | Extra pilot pages |
| CNInfo sample | `financials_pit/research_cninfo_periodic_announcements_sample.parquet` | 80 rows / 4 names — clock cross-check only |

Pointer: `financials_pit/research_free_hunt_secondary_manifest.json`

**Limitations:** EM pilot ~60 pages not full market; EITIME is ingest timestamp not certified exchange clock; no as-filed restatement ledger → **cannot promote**.

### C) SW_L1 PIT — prefix preferred over vote

| Priority | Path | Notes |
|---|---|---|
| **Research-preferred** | `data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet` | Eng columns + extras; XLS prefix L1 → 801xxx where mappable; 12925 rows / 5930 names; mapped_801=11457 |
| Legacy kept | `data/v2/sw_l1_pit/industry_members_sw_l1.parquet` | Vote method 7115/5847 — A/B only |
| Raw free_hunt | `free_hunt/sw_pit/sw_l1_pit_from_xls_prefix.parquet` | Native columns; 12925/5930 |

See `data/v2/sw_l1_pit/NOT_PROMOTION_GRADE.md` (updated).

**Limitations:** No free official full in/out API; out_date derived (next_in−1d); unmapped prefix L1 → `PREFIX_*`: ['210000', '250000', '260000', '310000', '320000', '440000', '470000']; fresh swsresearch XLS download timed out from box.

---

## Parked (not in Eng default path)

| Artifact | Why parked |
|---|---|
| `free_hunt/mktcap/em_kline_float_mktcap_proxy_pilot.parquet` | EM push2 intermittent; pilot only |
| `free_hunt/mktcap/tencent_spot_mktcap.parquet` | Spot sanity, not panel |
| CNInfo beyond sample | Full-market crawl fragile |
| NetEase / akshare_163 / BaoStock live probes | Dead / removed / blacklisted |
| Paid SW tapes (Tushare/Wind/JQ/BigQuant) | Leo free-only — excluded |

---

## Eng / Alpha consumption (see `output/d1/ENG_PING_PATHS.json`)

- Shell kick: primary `data/v2/float_mktcap/` + optional hist_from_1c85 / from_asof_extend secondary.
- Industry: prefer `industry_members_sw_l1_prefix.parquet`; keep vote for comparison.
- EP / available_at: primary tables unchanged; EM `research_*` for secondary timing/EP cross-check only.
- Always treat `quality_status` / manifests with `research_not_promotable` as non-promotion.

---

## Explicit non-actions this adoption

- Did **not** set `promotion_approved=true` anywhere.
- Did **not** overwrite `financials_available_at.parquet`.
- Did **not** interrupt enrich PID.
- Did **not** Mac-copy or call paid APIs.
