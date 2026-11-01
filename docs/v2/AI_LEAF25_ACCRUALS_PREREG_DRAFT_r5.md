# 【DRAFT r5 — NOT FROZEN】Leaf 25 preregistration draft: cash-flow accruals / earnings quality (g1g5_ashare_cfacc_desens_cs_v1)

- r5 (2026-10-18T10:52:44-04:00, from `date`): wording fix only, R4-P3-1 of Arch review docs/v2/ARCH_AI_LEAF25_PREREG_R4_REVIEW_ZH.md (efb013d8…) L39–40: r4 L83 “Q1 earlier than annual → fallback rule” replaced by “NaN until the annual report is available” (r5 L84). No other change; r4 (6678c9b7…) unchanged. Note: the r4 status line said “~10:55 ET”, which was an estimate; the r4 file mtime is 10:45 ET. Times are from `date` from now on.
- Status: DRAFT r4 by AI, 2026-10-18 ~10:55 ET. Revises r3 (0fb784f2d5a751dc006ee5624298fdbf08425f13ef223517609d5a8a39423d9f) per Arch review docs/v2/ARCH_AI_LEAF25_PREREG_R3_REVIEW_ZH.md (fc5fa9377d0bfe81…). r1, r2, r3 unchanged. Not frozen, leaf not opened, no data or schema read by AI, nothing run.
- Provenance (Arch review L103–106, P3): the step −1 script research/leaf25_ttm_recon_step_m1.py was overwritten in place on 2026-10-18 at 10:33:22 ET (file mtime, from `stat`), changing sha 6f508001… to 7edf577f875512e8d5eab28c9f3590ec5d2bfb85add9bdc99b925adf6524cf83. 6f508001 was never run, never referenced by any .ok, and no result depends on it. Arch rated this P3. The fix is the new file research/leaf25_ttm_recon_step_m1_r2.py (§11); 7edf577f is kept unchanged (superseded). From now on, every file whose sha Arch has seen gets a new filename when it changes.
- **Cannot be frozen** until Strategy DIFF C r3b (913e6830) is Arch-reviewed and its shared function sw_l1_asof_with_gap_carry has landed with a pinned sha (§4).
- Locks: promotion_approved=false; live=false; research_only=true; no GP; no leverage; no short leg; no sell-side / survey / consensus / analyst inputs.

## 0. 变更记录（r4 change log: review fc5fa937 item [review line] → r4 section）
| Item [review L] | r3 lines | Change | r4 § |
|---|---|---|---|
| N-P2-1 balancesheet report_type labels [L60–61, L56] | L53 | only report_type == "1" is used; every other value (the consolidated period-end text label, 268 null report_type rows) is never used or remapped, and is counted per value (all rows and end_date ≥ 2018) for all three tables; 475 null update_flag rows = not original, counted; if any non-"1" value is above 0.5% of rows from 2018 on, Arch rules on remapping before freeze | §2.2, §11 |
| N-P2-2 single-name cap [L63–66] | L86 | both tiers 6% per name, remainder in 510300 (HI_LIQ prereg L14 ADV floor; leaves 23/24) | §7 |
| N-P2-3 step −1 pick vs dates [L68–73] | L107–108 | trigger tuple carried from stage 1 through every later stage; case (i) only TTM-component corrections; case (ii) uses the trigger year annual; rule_exercised per case, exit non-zero if any is false; orphan-correction and per-value counts | §11 |
| N-P3-1 fina_indicator [L76] | L42 | fina_indicator-sourced columns banned (latest snapshot, not PIT) | §2.0 |
| N-P3-2 orphan corrections [L77] | — | disclosed and counted | §2.2 |
| N-P3-3 version rule vs leaf 19 [L78] | — | disclosed (leaf 19: earliest version, bs_cf; leaf 25: latest as-of version, separate files) | §0.1, §5 |
| N-P3-4 two annuals [L79] | L59 | rule removed; fiscal-year change not identifiable from end_date, disclosed | §2.3 |
| N-P3-5 memory stage 2 [L80] | — | new estimate: single row group, tens of MB; worst case ~650 MB | §11 |
| N-P3-6 --out check [L81] | — | path-component (parents) check in _r2 | §11 |
| N-P3-7 --meta [L82] | — | new .cmd passes --meta run_meta.json | §11 |
| N-P3-8 new filename [L83] | — | _r2 script, R2 .cmd and estimate | §11 |
| Schema verified [L47] | L42 | “verified only by step −1” replaced with “Arch verified (review fc5fa937 L46–57)” | §2.0 |
| Overwrite provenance [L103–106] | — | provenance line added | header |
| .ok memory keys [L101] | L109 | C4 1331200; wrapper stop 1484800; hard 1536000; peak above 650000 = P3 only | §11 |

### r3 change log (retained, vs r2 review 69d88da7)
| Item [review L] | r2 lines | Change | r3 § |
|---|---|---|---|
| P2-A version pick / availability [L74–79] | L29, L32, L34 | same-available_at ties → update_flag=0 else earliest file row, tie count reported; per-row available_at = coalesce(f_ann_date, ann_date) 18:00 Shanghai, null → never used; report_type=1 only, adjusted comparatives (other report_types) NOT used; income file path + sha + column names pinned | §2.0–§2.2 |
| P2-B NI field [L81–82] | L29, L42 | NI = n_income (consolidated, as leaf 19 prereg L8); n_income_attr_p → sensitivity S-NIparent | §2.0, §3, §10 |
| P2-C OCF member [L84–85] | L20, L51, L57, L78 | member = indcap_momneut_ocf (g1g5_ashare_indcap_momneut_ocf_v1); duplicate hard gate applies to it; northbound / d1_val removed | §0.1, §5, §9 |
| P2-D leaf 19 formula overlap [L87–88] | L22, L42, L48 | leaf 19 cfacc_rnoa base-α added to residualization (same pool/day, missing → 0) as in leaf 22 / leaf 23 preregs; "no leaf-19 residual" → sensitivity S-noL19 | §4, §10 |
| P2-E as-of rule [L57–61, L90–91] | L12, L50 | "r3b voided" sentence corrected (821dcfaa = freshness r3b); gap carry = DIFF C r3b 913e6830 L108–124; calendar fa4260b8; must call shared function; freeze blocked until it lands | §4 |
| P2-F SW table [L93–94] | L49 | primary = industry_members_sw_l1_tushare.parquet 89d4afa3 (research_preferred); prefix table 610b0956 → sensitivity S-SWprefix (1468 rows unmapped) | §3, §4, §10 |
| P3-A absolute staleness [L97] | L37 | TTM period end older than d − 15 months → NaN, counted | §2.3 |
| P3-B IPO < 4 quarters [L98] | (r1 L19) | pre-listing periods only if available_at < d; any missing A_{y−1} / YTD_{y−1} / TA_{t−4q} → NaN; IPO NaN counted per year | §2.3 |
| P3-C fiscal-year change [L99] | — | end_date only 03-31/06-30/09-30/12-31 else NaN + count; two annual reports in one year → NaN | §2.3 |
| P3-D single-statement correction example [L100] | — | example written; step −1 rule (i) covers it | §2.1, §11 |
| P3-E annual + Q1 same day [L101] | L36 | rule written (no fallback; both usable), counted; Q1 before annual → fallback rule | §2.3 |
| P3-F ADV window / trade timing [L102] | L48 | logADV20 = mean of t−20..t−1; signal at close t, trade T+1 open | §4, §7 |
| P3-G single-name cap [L103] | L64 | 60w top-6: 17%; 100w top-10: 10%; 20-name book 4% (disclosure) | §7 |
| P3-H PASS sign [L104] | L72 | both tiers HAC t ≥ +2.50 (positive) | §8 |
| P3-I cost comparability [L105] | L65 | judged 30bp (incl. Gate B and wb floor); comparisons with leaves 19/23/24 show 17.5bp alongside 30bp | §7 |
| P3-J X2 end [L106] | L61 | X2 end date hard-set at freeze (after Data 10-14→10-16 rerun is verified) | §6 |
| P3-K leaf 21 [L107] | L51 | leaf 21 biz_climate named in ρ disclosure; if 主 Agent rules it same-family → n=5, t*=2.58 | §4, §9 |
| P3-L step −1 pick rule [L108] | L84 | deterministic rule frozen in script; cashflow ann_min 2015-01-01 disclosed | §2.0, §11 |
| §5 checklist [L110–124] | — | step −1 package drafted (script, .cmd, memory estimate); not run | §11 |

## 0.1 家族与前史披露（Family; n=4）
1. leaf 19 cfacc_rnoa (g1g5_ashare_cfacc_rnoa_v1; ledger L46; WATCH). α files: output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet (sha 16202b2e…), alpha_FULLA_20261014_213132.parquet (sha c761dc36…).
2. accrual_quality (2026-10-13, balance-sheet Sloan WC accrual / TA; WATCH / DONE_FAIL).
3. indcap_momneut_ocf (mechanism_tag g1g5_ashare_indcap_momneut_ocf_v1; leaf A; ocf_to_profit = CFO/NI; WATCH); weights output/ai_factory/g1g5_indcap_momneut_ocf_daily_weights_20261013_105739.parquet (sha 7d289d54…).
4. leaf 25 (this).
- Not counted: northbound_flow, d1_val_resid (unrelated mechanism; r2 wording removed); STOCK-OCF-QUALITY V32 (proposal only, no trial consumed); leaf 21 biz_climate (neighbour family, ρ disclosure only); leaf 22 rd_innov (different family).
- Version rule differs from leaf 19 (N-P3-3): leaf 19 takes the earliest version of each period and uses bs_cf; leaf 25 takes the latest version usable as of d and uses the separate statement files. Both are PIT-valid; the difference is stated whenever the duplicate gate compares against leaf 19.

## 1. 机制与谁付钱（Mechanism）
- Investors fixate on reported earnings and under-weight its cash component; high-accrual (NI ≫ CFO) firms subsequently disappoint (Sloan 1996; A-share evidence mixed). Long-only: buy LOW accruals; no short leg.

## 2. 数据与 PIT（Data and point-in-time）
### 2.0 输入（Inputs; sha re-pinned at freeze — Data rerun 10-14→10-16 may change them）
- Income: data/v2/financials_pit/financials_pit_tushare.parquet, sha256 bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3; columns ts_code, end_date, ann_date, f_ann_date, available_at, update_flag, report_type, n_income, n_income_attr_p (names and types verified by Arch from schema, review fc5fa937 L46–57).
- Banned (N-P3-1): every fina_indicator-sourced column in financials_pit_tushare (eps, roe, bps, profit_dedt, etc.). Per the manifest they are the latest snapshot per (ts_code, end_date), not PIT, and are never read.
- Cash flow: data/v2/financials_pit/cashflow_pit_tushare.parquet, sha256 71d5c3d39fbf2de05064ce7f21334e15c9b1d977c64494ffe699f7eeb0b95d79; n_cashflow_act (+ same key columns). Manifest: ann_min 2015-01-01 → TTM warm-up for the 2018 sealed start is sufficient (disclosed).
- Balance: data/v2/financials_pit/balancesheet_pit_tushare.parquet, sha256 9ca054962e850cad7305262e978758c9e9f36613c4cca025efdd99276de8dbb5; total_assets. (Not bs_cf 01a015bf: its manifest does not document per-statement version retention; see step −1 estimate.)
- Calendar: data/v2/calendar/trade_cal_sse_pit.parquet fa4260b808755b9a1c91e3ade210edec84bbdb91e0dfff4c6a955c4d35fd8a41.
- Policy: AVAILABLE_AT_RESTATEMENT_POLICY.md ("Not TTM-certified") → step −1 hand reconciliation required.
### 2.1 TTM 差分（TTM differencing）
- TTM_E = YTD_E + A_{y−1} − YTD_{E−1y}; E annual → TTM = A_y. Same E for NI, CFO and TA.
- Each component = version selected by §2.2 on the same as-of session d; never final revised figures; never back-filled corrections.
- Example (single-statement correction): the prior-year Q3 cash-flow statement is corrected (new row, own available_at = t_c) while income and balance are unchanged. For Q3-based TTM: before t_c the original CFO YTD_{Q3,y−1} is used; from the first session after t_c the corrected value is used; NI and TA keep their own (unchanged) versions. Step −1 rule (i) selects exactly such a case.
### 2.2 版本与可得时点（Version pick and availability）
- Availability: each row (version) uses its OWN available_at column = coalesce(f_ann_date, ann_date) 18:00 Asia/Shanghai (manifest rule). A row is usable on session d iff its Shanghai available date < d. Rows with null available_at are never used; never inferred from end_date + lag.
- report_type (N-P2-1): only report_type == "1" is used, in all three tables. Every other value is never used and never remapped by code: text labels (the balancesheet consolidated period-end label 合并期末) and nulls (268 null report_type rows in balancesheet). Adjusted comparatives are not used. Step −1 run_meta reports per-value row counts of report_type and update_flag for each table, both for all rows and for end_date ≥ 2018. If any value other than "1" is above 0.5% of rows from 2018 on, Arch rules on remapping before freeze.
- Ties: among usable rows of one (table, ts_code, end_date), take the latest available_at; if several rows share that available_at → the original (update_flag = 0); if none is original → the earliest row in file order. Tie-group count reported per year.
- Null update_flag (475 balancesheet rows) counts as not original in tie-breaks, and is counted.
- Orphan corrections (N-P3-2): a (table, ts_code, end_date) group with no update_flag = "0" row cannot be checked for look-ahead in the data. Such groups are used under the same rule, but disclosed and counted (all rows and end_date ≥ 2018).
### 2.3 缺失、过期与特殊情形（Missing / stale / special cases）
- Fallback: if the newest period E lacks any component on d, use the newest E whose components are all usable, at most one quarter older than the newest published income period; otherwise NaN.
- Absolute cap (P3-A): E < d − 15 months → NaN. Counts of fallback and NaN name-days reported per year.
- IPO (P3-B): pre-listing periods usable only if their row available_at < d; missing A_{y−1}, YTD_{y−1} or TA_{t−4q} → NaN; IPO-caused NaN counted per year.
- Fiscal year: end_date must be 03-31/06-30/09-30/12-31, else the row is ignored and counted. A fiscal-year change cannot be identified from end_date (the table has no end_type column); this is disclosed, not detected. (The r3 “two annual reports in one year” rule is removed: it cannot trigger once only quarter-end end_dates are used.)
- Annual + Q1 same day (P3-E): both become usable the same session; TTM_Q1 uses that A_y; no fallback; counted. Q1 earlier than annual (rare): under the max-one-fiscal-quarter-lag cap (§2.3 fallback) the only allowed fallback period is the not-yet-available annual A_{y−1}, so the value stays NaN until the annual report is available; counted (matches script fallback break; R4-P3-1).
- No forecast / express / consensus / analyst / survey fields.

## 3. 信号（Signal）
- Primary: CFACC = (n_income_ttm − n_cashflow_act_ttm) / avg(TA_E, TA_{E−1y}); prefer LOW. Desensitize: winsor 1/99 → rank → normal score; monthly rebalance.
- Applicability exclusion (not universe): SW L1 banks and non-bank financials via the primary SW table and as-of rule of §4; hard-exclude 600519, 002371. Real estate kept in primary (S-exRE disclosure).

## 4. 残差化与正交（Residualization）
- Cross-sectional OLS per rebalance date: SW L1 dummies; logmv_{t−1}; beta120_{t−1} (vs 510300); mom t−120→t−20; logADV20 = mean(ADV over t−20..t−1); vol20_{t−1}; **leaf 19 cfacc_rnoa base-α, same pool/day, missing → 0** (precedent: leaf 22 AI_G1G5_RD_INNOV_WHO_PAYS_PREREG_ZH.md L24 (sha 74aa58b9…); leaf 23 AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md L95 (sha 8f5d8ac4…)).
- SW L1 primary table: data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet, sha256 89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c (manifest research_preferred; read-only frozen artefact). Prefix table 610b0956… → S-SWprefix only (1468 of 12925 rows unmapped to 801xxx). Re-pin to sw_l1_pit_v2 when it lands (prereg amendment).
- As-of rule (Strategy DIFF C r3b, docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3b.diff, sha 913e683082cfd63707f314cc4bd5f5166854cc787d685c1560a3e29cd891f5ae, L108–124; pending Arch review): main rule in_date < d and (out_date null or out_date ≥ d), d normalized; d must be an SSE open day; one exception — if a code has no active row on d and has an old row with parsed in_date, in_date ≤ out_date, and prev_open(d) ≤ out_date < d (prev_open = latest open day < d in the passed calendar), carry that row for day d only (≤1 trading day); no successor row required; out_date on a closed day also carried (disclosed n_rows_gap_carry_out_on_closed_day); unparsed in_date never carried; calendar passed as TradeCal pinned fa4260b8; d NaT / outside calendar / not open / no prior open day → SwPitIntegrityError, never calendar-day fallback.
- Correction of r2: 821dcfaa (voided by ARCH_STRATEGY_SW_PIT_FRESHNESS_R4_REVIEW_ZH.md 8d5bc796 L4) is the freshness r3b, not the DIFF C as-of r3b; r2 conflated them.
- Implementation MUST call the shared function sw_l1_asof_with_gap_carry once DIFF C r3b lands (sha pinned in .ok); no private reimplementation. Leaf 25 cannot be frozen before that.
- ρ disclosure: capacity_adv, earnings_event, accrual_quality, indcap_momneut_ocf, leaves 15–24 incl. **leaf 21 biz_climate** (named).

## 5. 低重合与重复硬闸（Overlap; duplicate gate）
- vs leaf 23 (ΔE/P change vs cash composition of level) low; vs leaf 24 (price lottery, no price input here) very low — words only.
- Hard duplicate rule vs leaf 19, accrual_quality, indcap_momneut_ocf, leaf 23, leaf 24: ρ_excess (de-β vs pool EW) > 0.5 OR median top-10 Jaccard ≥ 0.5 → FAIL.

## 6. 宇宙与窗口（Universes / windows）
- HI_LIQ_V1.1 decisive; FULLA_V1 disclosure; frozen as leaf 23/24.
- X2: 2024-06-03 → **end date hard-set at freeze** (written as a literal date after Data 10-14→10-16 rerun is verified; not "latest at .ok issue").
- Sealed 2018-01-02 → 2024-05-31: read once only after X2 passes all hard gates, separate .ok; both tiers > 0 vs HI_LIQ wb and same sign as X2 else WATCH cap; family has used it.

## 7. 评价与硬闸（Evaluation; decisive HI_LIQ）
- Timing: signal at close t; trade at T+1 open (as leaf 23/24).
- Books: 60w top-6 and 100w top-10, single-name cap 6% in both tiers, remainder held in 510300; industry cap 25%/28%; the 20-name 4% book is disclosure only. Basis: docs/v2/STRATEGY_HI_LIQ_SUBSET_PREREG_ZH.md L14 derives the HI_LIQ ADV floor from 6% × 1,000,000 / 0.6% = 10,000,000, so a cap above 6% breaks fillability at the universe edge; leaves 23/24 use the same 6% (Arch 0d9bd147 L96; leaf 24 prereg L61, L88).
- Cost: 30bp per side for all judged figures incl. HI_LIQ wb hard floor and Gate B; 17.5bp shown alongside 30bp in every comparison table with leaves 19/23/24 (their judged cost).
- Annualization 244 trading days (printed).
- Hard floor (both tiers net 30bp CAGR > HI_LIQ wb), coverage (HI_LIQ ≥300, FULLA ≥800), alpha_decay_gate v1.1 via research/leaf_selfcheck_v3.py sha256 ecaa30d8760f7ae5f53c330c128e6702476d01d8d69112b1dbf2fe769b7eaebe, Gate A (ρ vs cap <0.5, residual α >0).
- Gate B: CMC v1.2 research/alpha_combo_marginal_v1_2.py sha256 bba212afadefce68dcd1bf76919f91de39402658e4398e925e3d80c6f01592c4; cap80 + leaf 20%; gating-only.

## 8. 判定（Verdicts）
- PASS (entry ticket; promotion only via FWD 2026-11-02): all hard gates AND both tiers HAC t (NW lag 19) of daily net excess vs HI_LIQ wb **≥ +2.50** AND beats pool EW AND Gate A, Gate B, decay pass AND not duplicate.
- WATCH / FAIL as r2 §8 (FAIL: hard floor, coverage, duplicate, uncleared C1–C5).
- report_to_leo only for the decisive spec on PASS; sensitivities never a basis.

## 9. 试验预算（Trial budget）
- n = 4 (leaf 19 + accrual_quality + indcap_momneut_ocf + leaf 25); t* = Φ⁻¹(1 − 0.05/8) = 2.4977 → 2.50 (Arch review L27–32). If 主 Agent rules leaf 21 same-family: n = 5, t* = 2.58.

## 10. 敏感性（Sensitivities; disclosure only)
- S-BS, S-NOA, S-noresid, S-exfin-off, S-q, S-exRE (as r2) plus S-NIparent (n_income_attr_p), S-noL19 (no leaf-19 regressor), S-SWprefix (prefix SW table 610b0956).

## 11. 步骤 −1、内存测试与执行（Step −1, memtest, execution）
- Step −1 (NOT run; own read-only Arch .ok after Arch passes r4 §2; checklist = review fc5fa937 §6 L108–117):
  - script research/leaf25_ttm_recon_step_m1_r2.py sha256 f46e0fb5898ba58566c4c6fa6ed05b370a36a38941f766ffcbbee56d316956da (stdlib/pandas/pyarrow; re-checks input sha, exits 3 on mismatch; no fina_indicator columns; --out must be strictly under output/ai_factory/_leaf25_ttm_recon/ by path-component check; writes only raw_rows.csv, ttm_script.csv, run_meta.json). Supersedes 7edf577f (kept unchanged).
  - .cmd docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R2.cmd (sha 73aceedc05716dd7fdf1c0908b6163a2958aa4c1688fd8ea2944735ab9e6b69f): wrapper v4 6174eacb, qlvenv, PYTHONDONTWRITEBYTECODE=1, --assert leaf25_ttm_recon_step_m1_r2, --meta <out>/run_meta.json, .ok output/ai_factory/ARCH_RUN_AUTH_LEAF25_TTM_RECON_STEP_M1_R2.ok.
  - Memory estimate docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_R2_MEM_ESTIMATE.md (sha e95db81ddf24f09aed904e96871b4a537260a5029c151c7f0216f631ea5e6dfd): typical ~466,000 kB; worst case ~650 MB (stage 2 is tens of MB because each file has a single row group).
  - .ok memory keys: C4 line 1331200 kB; wrapper stop 1484800 (default); hard 1536000; expected peak report line 650000 kB, and a peak above it is P3 review only.
  - Deterministic pick: smallest ts_code; the trigger tuple is carried unchanged from stage 1 into every later stage.
    (i) (ts_code, end_date, table, corr_date): end_date ≥ 2018, quarter end, more than one distinct available date in exactly one table; corr_date = second distinct date. Only corrections whose end_date is one of the TTM component periods used on next_open(corr_date) for that table (income/cashflow: E, A_{y−1}, YTD_{E−1y}; balance: TA_E, TA_{E−1y}).
    (ii) (ts_code, y, annual date, Q1 date): y ≥ 2019, first Q1(y) income date ≤ first annual(y−1) date; dates are taken from that trigger year, not the latest year.
    (iii) (ts_code, first period, first date): first report_type-1 income period ≥ 2019-03-31. The three codes must be distinct.
  - As-of dates: (i) the open day before and the first open day after corr_date; (ii) the effective first day of the trigger year's Q1 and annual and the open day before each; (iii) the first open day after the first report. Each code also gets context dates (latest annual before/after, latest H1/Q3, earliest Q1); at least 4 dates per code, else exit 3.
  - rule_exercised in run_meta: (i) the triggering table's key for end_date shows an older version before and the corr_date version after; (ii) same-day: on the Q1 effective day E = Q1(y) with status OK, using A_{y−1}; Q1 first: E = Q1(y) is not OK that day; (iii) TTM is NaN on the first report. Any false → exit 4 after writing outputs (stop and report). run_meta also has per-value report_type/update_flag counts, a flag for any non-"1" share above 0.5% (end_date ≥ 2018), orphan-correction counts, tie counts and non-quarter-end counts.
- Step 0 memtest (build/eval FULLA etc.) with cmc_wrapper_v4 6174eacb, STOPKB 1484800, C4 1331200; then formal serial run; CMC v1.2 after its own memtest.
- Preconditions: Arch passes r4; DIFF C r3b landed (shared function sha); frozen sha; inputs re-pinned after Data rerun (script gets a new filename if any input sha changes); .ok + .cmd; 94322 in state T or exited; quiet-lock and Web pre-checks per review fc5fa937 L113–114.

## 12. 交付、入组路径与禁止（Deliverables / entry / prohibitions）
- As r2 §12: deliverables incl. TTM fallback/NaN/tie/IPO/fiscal counts; if PASS → slow factor in Optimizer Core target weights (industry ±8%, Size/MidCap ±0.35σ, L1 turnover), not a Top-N satellite; prohibitions unchanged.
