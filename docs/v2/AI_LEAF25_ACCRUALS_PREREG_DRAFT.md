# 【DRAFT — NOT FROZEN】Leaf 25 preregistration draft: cash-flow accruals / earnings quality (g1g5_ashare_cfacc_desens_cs_v1)

- Status: DRAFT by AI, 2026-10-18 ~09:30 ET. Not frozen, leaf not opened, no data read, no code written. Requires Arch review + 主 Agent ruling before freeze.
- Locks: promotion_approved=false; live=false; research_only=true; no GP; no leverage; no short leg; no sell-side / survey / consensus / analyst inputs.
- Format follows leaf 23 r2.1 (AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md) and leaf 24 prereg (c289e770).

## 0. 家族与前史披露（Family history — read first）
- This is NOT a fresh direction. Same family already tried: (i) accrual_quality leaf (2026-10-13, balance-sheet Sloan WC accrual / TA, SW L1 demean + log float-mcap residual) → Alpha ACCEPT research-grade → **WATCH / DONE_FAIL** (Book-Smoke 5.50%/5.81% @60w/100w, any_pass=false); (ii) OCF-related arm (northbound/OCF/d1_val, WATCH).
- Leaf 25 counts as family trial n=3 for multiple-testing (§9). The prior accrual_quality sealed/X2 readings are treated as already-seen; X2 here is an entry ticket only, not independent OOS.
- What is different (must be true or the leaf is a re-skin and is rejected): cash-flow-statement accrual (NI − CFO) instead of balance-sheet WC proxy; desensitized (rank/winsor, no level effects); full style residualization (not just ind+size); evaluated on cs_panel_v2_resumefix with the leaf 23/24 X2 engine; duplicate rule vs accrual_quality weights is a hard gate (§5).

## 1. 机制、命名与谁付钱（Mechanism / who pays）
- Hypothesis: investors fixate on reported net income and under-weight its cash component; firms with high accruals (NI far above CFO) subsequently disappoint (Sloan 1996 accrual anomaly; A-share evidence mixed, weaker post-2015).
- Who pays: earnings-fixated holders of high-accrual names who reprice on later reports. Long-only: we buy LOW accrual (high cash-backed earnings) names; no short leg.
- Name: g1g5_ashare_cfacc_desens_cs_v1, leaf 25.

## 2. 数据与 PIT（Data and point-in-time）
- Sources (record-only here; sha pinned in .ok): data/v2/financials_pit/cashflow_pit_tushare.parquet (n_cashflow_act), income from the PIT financials set (n_income_attr_p), balancesheet_pit_tushare.parquet (total_assets); policy AVAILABLE_AT_RESTATEMENT_POLICY.md.
- PIT rule: a report is usable from the first trading day strictly after available_at (ann_date-based; restatements only from their own available_at; never back-filled). Use TTM sums of the latest 4 available quarters; require ≥4 quarters.
- No forecast / express / consensus / analyst / survey fields. No price-derived inputs in the raw signal except the residualization controls (§4).

## 3. 信号定义（Signal）
- Primary: CFACC = (NI_ttm − CFO_ttm) / avg(TA_t, TA_{t−4q}). Prefer LOW CFACC.
- Desensitization: within-date cross-sectional winsor 1/99 then rank → normal score; financial-sector exclusion (SW L1 banks, non-bank financials) as factor-applicability exclusion, not universe definition; hard-exclude 600519, 002371 (as leaf 23).
- Rebalance monthly (signal changes only on new reports; monthly cadence keeps turnover bounded).

## 4. 残差化与正交（Residualization / orthogonality）
- Cross-sectional OLS each rebalance date on: SW L1 dummies, logmv_{t−1}, beta120_{t−1} (vs 510300), mom t−120→t−20, logADV20, vol20_{t−1} (same frozen style set as leaf 24 §4). Residual = alpha score.
- Factor-library orthogonality: report ρ (de-β) of the alpha score / book returns vs capacity_adv, earnings_event, accrual_quality, OCF arm, leaves 15–24.

## 5. 与叶23 / 叶24 的低重合论证（Overlap argument, words only — no computation）
- vs leaf 23 (desensitized SUE, ΔE/P): leaf 23 ranks the CHANGE in earnings level scaled by price; leaf 25 ranks the CASH COMPOSITION of the earnings level scaled by assets. A firm can have strong ΔE (high SUE) with either high or low accruals; the accrual literature shows accruals are largely orthogonal to earnings surprise and the two anomalies co-exist. Timing also differs: SUE reacts around announcements, accruals persist across quarters. Expected low overlap, but both use report timing, so the Jaccard/ρ rule below is binding.
- vs leaf 24 (imax intraday): leaf 24 is a pure price/intraday-return lottery feature (right-tail daily returns, residualized on vol20); leaf 25 uses no price information in the raw signal. Mechanisms (lottery preference vs earnings fixation) and data sources (minute/daily prices vs financial statements) are disjoint. Expected very low overlap.
- vs accrual_quality (prior leaf): HIGHEST risk of overlap (same anomaly family). Hard duplicate rule: ρ_excess (de-β vs pool EW) > 0.5 OR median top-10 Jaccard ≥ 0.5 vs accrual_quality X2 weights → leaf 25 is a duplicate → FAIL (not WATCH).
- Same hard rule applied vs leaf 23 and leaf 24 with thresholds ρ_excess > 0.5 or Jaccard ≥ 0.5.

## 6. 宇宙与窗口（Universes and windows — frozen）
- Universes: HI_LIQ_V1.1 (decisive, paper path) and FULLA_V1 (research control, disclosure only). Both frozen as in leaf 23/24.
- X2: 2024-06-03 → latest panel date at .ok issue (leaf 23/24 used → 2026-10-09). Only X2 dates written; warm-up uses only financial data.
- Sealed window: 2018-01-02 → 2024-05-31. Read ONCE, only after X2 passes ALL hard gates (§7), with a separate Arch .ok. Rule: both tiers net excess vs HI_LIQ wb > 0 and same sign as X2, else cap at WATCH. Disclosure: the family (accrual_quality) has used this period; not independent OOS.

## 7. 评价与硬闸（Evaluation and hard gates; decisive = HI_LIQ）
- Books: X2 at 60w top-6 and 100w top-10, long-only, 17.5bp cost per side, industry cap 25% (HI_LIQ) / 28% (FULLA), single name ≤ 17%/10% by tier construction; 20-name 4% book disclosure only.
- Benchmarks side by side: capacity_adv HI_LIQ single-leg book-smoke (cap), HI_LIQ wb, pool EW, 510300.
- Turnover and net-of-cost: report monthly one-way turnover, cost drag (bp/yr), gross vs net CAGR; net figures are the only judged figures.
- HI_LIQ wb hard floor: both tiers net CAGR > HI_LIQ wb, else FAIL.
- Coverage: median names with valid alpha on rebalance dates HI_LIQ ≥ 300, FULLA ≥ 800, else FAIL.
- alpha_decay_gate (v1.1 via leaf_selfcheck_v3.py, pinned sha): IC at h = 1/5/20/60; decay gate per v1.1 thresholds; fail → WATCH cap.
- Gate A: ρ vs cap < 0.5 and residual α > 0.
- Gate B (CMC, alpha_combo_marginal v1.1 after Alpha/Eng memory rewrite, its own memtest + .ok): cap80 + leaf 20%, both tiers net CAGR > cap. Gate B is gating-only: can keep/lower, never raise.

## 8. 判定（Verdicts）
- PASS (entry ticket only; promotion still only via FWD from 2026-11-02): all hard gates pass AND both tiers HAC t (Newey-West lag 19) of daily net excess vs HI_LIQ wb ≥ t* (§9) with the same sign AND beats pool EW AND Gate A and Gate B pass AND decay gate pass AND not duplicate.
- WATCH: hard floor + coverage pass and not duplicate, but any of t* / pool EW / Gate A / Gate B / decay / sealed-window direction fails.
- FAIL: hard floor fails, OR coverage fails, OR duplicate (§5), OR any C1–C5 run failure not cleared by Arch.
- report_to_leo only on the decisive spec and only if PASS; sensitivity results are disclosure only, never a basis for reporting to Leo (k1 precedent, leaf 24).

## 9. 试验预算（Trial budget / multiple testing）
- Family n = 3 (accrual_quality, OCF arm, leaf 25); Bonferroni-Holm two-sided 5% → t* = 2.39 for n=3 (to be confirmed by Arch; leaf 23 used 2.50 for n=4). Only ONE decisive spec.

## 10. 敏感性（Sensitivity variants — defined upfront, disclosure only, uncorrected）
- S-BS: balance-sheet WC accrual (accrual_quality definition) on the same engine (also the duplicate reference).
- S-NOA: denominator = net operating assets instead of avg TA.
- S-noresid: industry+size residual only (no beta/mom/ADV/vol20).
- S-exfin-off: keep financials (show the effect of the applicability exclusion).
- S-q: quarterly (non-TTM) accrual of the latest quarter.
- Each variant: build HILIQ / build FULLA / eval HILIQ / eval FULLA / merge, after the primary spec; no selection among variants.

## 11. 内存测试与执行步骤（Memtest first; execution order）
- Step 0 (before any formal run): memtest of build HILIQ, build FULLA, eval FULLA in a scratch dir via a harness that calls only build()/evaluate() with separate Arch .ok per test; wrapper = cmc_wrapper_v2 (dcfef770 or Arch-approved successor), STOPKB 1484800, report line 1331200, peak = max(sampler, log hwm, meta).
- Then formal: primary build HILIQ → build FULLA → eval HILIQ → eval FULLA → merge; then sensitivities; strictly serial, no retries, C1–C5 per step, receipts per step; CMC only after its own memtest.
- Preconditions: Arch review of this prereg + script source; prereg frozen with sha; .ok + .cmd issued; quiet window and C5 as per Arch; process 94322 status ruled on by Arch.

## 12. 交付与禁止（Deliverables and prohibitions）
- Deliver: daily base-α vectors (HI_LIQ/FULLA), 60w/100w eval weights, eval summary (benchmarks, net/gross, turnover, decay, gates, duplicate checks, sensitivities), receipts.
- Prohibited: GP, leverage, short leg, sell-side/survey/consensus/analyst data, forecasts/express reports, any order or Strategy handoff, promotion, live, reading the sealed window before X2 passes.
