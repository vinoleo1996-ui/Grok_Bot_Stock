# 【DRAFT r3 — NOT FROZEN】Leaf 25 preregistration draft: cash-flow accruals / earnings quality (g1g5_ashare_cfacc_desens_cs_v1)

- Status: DRAFT r3 by AI, 2026-10-18 ~10:50 ET. Revises r2 (6dcc919d…01bd94) per Arch review docs/v2/ARCH_AI_LEAF25_PREREG_R2_REVIEW_ZH.md (69d88da7). r1 (993c4ce5) and r2 unchanged. Not frozen, leaf not opened, no data read (sha256 of files only; manifests JSON read), no code run.
- **Cannot be frozen** until Strategy DIFF C r3b (913e6830) is Arch-reviewed and its shared function sw_l1_asof_with_gap_carry has landed with a pinned sha (§4).
- Locks: promotion_approved=false; live=false; research_only=true; no GP; no leverage; no short leg; no sell-side / survey / consensus / analyst inputs.

## 0. 变更记录（r3 change log: review item [review line] → r3 section）
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

## 1. 机制与谁付钱（Mechanism）
- Investors fixate on reported earnings and under-weight its cash component; high-accrual (NI ≫ CFO) firms subsequently disappoint (Sloan 1996; A-share evidence mixed). Long-only: buy LOW accruals; no short leg.

## 2. 数据与 PIT（Data and point-in-time）
### 2.0 输入（Inputs; sha re-pinned at freeze — Data rerun 10-14→10-16 may change them）
- Income: data/v2/financials_pit/financials_pit_tushare.parquet, sha256 bc0f4c3d3cd70a11d17f44496861e21268806509656247400c64be2d3ae7fab3; columns ts_code, end_date, ann_date, f_ann_date, available_at, update_flag, report_type, n_income, n_income_attr_p (names from Arch review L117 / leaf 19 prereg; verified only by the step −1 schema check under its .ok).
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
- report_type: primary uses report_type = 1 (consolidated) only. Adjusted comparatives carried in later reports (other report_types) are NOT used for A_{y−1} or YTD_{y−1} (chosen rule; disclosed).
- Ties: among usable rows of one (table, ts_code, end_date), take the latest available_at; if several rows share that available_at → the original (update_flag = 0); if none is original → the earliest row in file order. Tie-group count reported per year.
### 2.3 缺失、过期与特殊情形（Missing / stale / special cases）
- Fallback: if the newest period E lacks any component on d, use the newest E whose components are all usable, at most one quarter older than the newest published income period; otherwise NaN.
- Absolute cap (P3-A): E < d − 15 months → NaN. Counts of fallback and NaN name-days reported per year.
- IPO (P3-B): pre-listing periods usable only if their row available_at < d; missing A_{y−1}, YTD_{y−1} or TA_{t−4q} → NaN; IPO-caused NaN counted per year.
- Fiscal year (P3-C): end_date must be 03-31/06-30/09-30/12-31, else row ignored (counted); two annual rows for one year → NaN for that year.
- Annual + Q1 same day (P3-E): both become usable the same session; TTM_Q1 uses that A_y; no fallback; counted. Q1 earlier than annual (rare) → fallback rule.
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
- Books: 60w top-6 (single-name cap 17%), 100w top-10 (cap 10%); industry cap 25%/28%; 20-name 4% book disclosure only.
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
- Step −1 (NOT run; own read-only Arch .ok after Arch passes r3 §2; checklist = review L110–124):
  - script research/leaf25_ttm_recon_step_m1.py sha256 7edf577f875512e8d5eab28c9f3590ec5d2bfb85add9bdc99b925adf6524cf83 (stdlib/pandas/pyarrow; re-checks input sha, exits on mismatch; column projection + pushdown to 3 codes; writes only raw_rows.csv, ttm_script.csv, run_meta.json under output/ai_factory/_leaf25_ttm_recon/<ET ts>/; STAGE ru_maxrss lines + peak RSS in run_meta).
  - .cmd docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1.cmd (sha 6e01e1de…), wrapper v4 6174eacb, qlvenv, PYTHONDONTWRITEBYTECODE=1. Memory estimate docs/v2/audit/leaf25_step_m1/LEAF25_STEP_M1_MEM_ESTIMATE.md (sha bf2c29fe…): ~413,000 kB (+30% → ~537,000) < 600,000.
  - Deterministic pick (frozen in script; no pre-viewing): over all ts_code in the three files, report_type 1, quarter-end end_date ≥ 2018-01-01: (i) smallest ts_code with some (ts_code, end_date) having >1 distinct available date in exactly one of the three statements; (ii) next smallest ts_code (≠ i) whose first Q1(y) income available date ≤ first annual(y−1) available date, y ≥ 2019; (iii) next smallest ts_code (≠ i, ii) whose first report_type-1 income period ≥ 2019-03-31 (IPO < 4 quarters during the window). Not restricted to HI_LIQ (no list file read).
  - As-of dates per code (from available_at + SSE calendar): correction case → last open day before and first open day after the correction; plus first open day after the latest annual (and the open day before it), first open day after the latest H1/Q3, first open day after the earliest Q1 ≥ 2018. ≥4 dates required else stop.
- Step 0 memtest (build/eval FULLA etc.) with cmc_wrapper_v4 6174eacb, STOPKB 1484800, C4 1331200; then formal serial run; CMC v1.2 after its own memtest.
- Preconditions: Arch passes r3; DIFF C r3b landed (shared function sha); frozen sha; inputs re-pinned after Data rerun; .ok + .cmd; 94322 in state T or exited; Web pre-checks per review L123.

## 12. 交付、入组路径与禁止（Deliverables / entry / prohibitions）
- As r2 §12: deliverables incl. TTM fallback/NaN/tie/IPO/fiscal counts; if PASS → slow factor in Optimizer Core target weights (industry ±8%, Size/MidCap ±0.35σ, L1 turnover), not a Top-N satellite; prohibitions unchanged.
