# 【DRAFT r2 — NOT FROZEN】Leaf 25 preregistration draft: cash-flow accruals / earnings quality (g1g5_ashare_cfacc_desens_cs_v1)

- Status: DRAFT r2 by AI, 2026-10-18 ~10:25 ET, revising r1 (docs/v2/AI_LEAF25_ACCRUALS_PREREG_DRAFT.md, sha 993c4ce5) per Arch audit AUDIT_20261018_1018_ET_ZH.md (sha 88db7a5a). Not frozen, leaf not opened, no data read, no code written.
- Locks: promotion_approved=false; live=false; research_only=true; no GP; no leverage; no short leg; no sell-side / survey / consensus / analyst inputs.
- Format follows leaf 23 r2.1 (AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md) and leaf 24 prereg (c289e770).

## 0. 变更记录（r2 change log: audit item → section）
| Audit item | Change | Section |
|---|---|---|
| P2-1 TTM | TTM differencing formula; same-as-of version for all 3 components; f_ann_date availability; corrections only from own available_at; missing-quarter / late-annual rule; pre-memtest 3-stock hand reconciliation (own read-only Arch .ok, not run) | §2.1–§2.3, §11 step −1 |
| P2-2 family | leaf 19 cfacc_rnoa added to family; n=4, t*=2.50; duplicate hard gate also vs leaf 19 | §0.1, §5, §9 |
| P2-3 SW L1 PIT | pin industry_members_sw_l1_prefix.parquet sha 610b0956…; switch to sw_l1_pit_v2 when landed; as-of trading-day rule = Strategy as-of fix (in_date < d; 1-SSE-day gap carry); financial exclusion via the same table | §3, §4 |
| P3-1 refs | Gate B → CMC v1.2; wrapper → cmc_wrapper_v4 6174eacb | §7, §11 |
| P3-2 real estate | real estate kept in primary; S-exRE sensitivity, disclosure only | §3, §10 |
| P3-3 annualization | 244 trading days, printed in summary | §7 |
| P3-4 cost | 30bp per side hard-set (judged); 17.5bp disclosure only | §7 |
| P3-5 entry path | PASS → slow factor into Optimizer Core target weights, not a standalone Top-N satellite | §12 |

## 0.1 家族与前史披露（Family history）
- Same family already tried: (i) leaf 19 cfacc_rnoa (cash-flow accrual + RNOA improvement; HI_LIQ primary; WATCH: decay v1.1 DOWNGRADE, cost > half of gross excess, GATE_V3 FAIL); (ii) accrual_quality leaf (2026-10-13, balance-sheet Sloan WC accrual / TA) → WATCH / DONE_FAIL (Book-Smoke 5.50%/5.81%, any_pass=false); (iii) OCF-related arm (northbound/OCF/d1_val, WATCH).
- Leaf 25 is family trial n=4 (§9). Prior readings are treated as already seen; X2 is an entry ticket only, not independent OOS.
- Required differences vs leaf 19 and accrual_quality (else re-skin → rejected): pure NI−CFO accrual without RNOA component; desensitized; full style residualization; cs_panel_v2_resumefix engine; duplicate hard gate vs both (§5).

## 1. 机制、命名与谁付钱（Mechanism / who pays）
- Hypothesis: investors fixate on reported net income and under-weight its cash component; high-accrual (NI ≫ CFO) firms subsequently disappoint (Sloan 1996; A-share evidence mixed, weaker post-2015).
- Who pays: earnings-fixated holders of high-accrual names repricing on later reports. Long-only: buy LOW accrual names; no short leg.

## 2. 数据与 PIT（Data and point-in-time）
- Sources (sha pinned in .ok): data/v2/financials_pit/cashflow_pit_tushare.parquet (n_cashflow_act), PIT income (n_income_attr_p), balancesheet_pit_tushare.parquet (total_assets); policy AVAILABLE_AT_RESTATEMENT_POLICY.md (states "Not TTM-certified").
### 2.1 TTM 差分（TTM differencing）
- Tushare cash-flow and income items are year-to-date (YTD). TTM_q = YTD_q + Annual_{y−1} − YTD_{same period, y−1}. For q = annual report: TTM = Annual_y.
- All three components are taken as the latest version available on the SAME as-of date d (each component: the newest record of that period with available_at < d). Never splice final revised figures; never back-fill earlier dates with corrected (update_flag) values.
### 2.2 可得时点（Availability）
- available_at of a record = its f_ann_date (first announcement date); usable from the first SSE trading day strictly after f_ann_date. A corrected version takes effect only from its own available_at; before that, the original version is used.
### 2.3 缺季与年报晚于一季报（Missing quarter / annual later than Q1）
- Chosen rule: **last fully available TTM**. If on date d any of the three components of the newest period is unavailable (e.g. Q1 published before the prior annual report, or a quarter missing), use the most recent TTM whose three components are all available at d.
- Staleness cap: that fallback TTM may be at most one fiscal quarter older than the newest published period; otherwise CFACC = NaN on d (name dropped that day). Count of fallback and NaN name-days is reported per year.
- Denominator avg(TA_t, TA_{t−4q}) uses the same as-of versions; missing TA_{t−4q} → NaN.
- No forecast / express / consensus / analyst / survey fields.

## 3. 信号定义（Signal）
- Primary: CFACC = (NI_ttm − CFO_ttm) / avg(TA_t, TA_{t−4q}). Prefer LOW CFACC.
- Desensitization: within-date winsor 1/99 → rank → normal score.
- Applicability exclusion (not universe definition): SW L1 banks and non-bank financials, determined with the SAME PIT SW L1 table and as-of rule as §4; hard-exclude 600519, 002371. Real estate is NOT excluded in the primary spec (choice: keep comparability with leaf 19/23); its distortion of NI−CFO via pre-sale receipts is tested by S-exRE (§10, disclosure only).
- Rebalance monthly.

## 4. 残差化与正交（Residualization / orthogonality）
- Daily cross-sectional OLS on rebalance dates: SW L1 dummies, logmv_{t−1}, beta120_{t−1} (vs 510300), mom t−120→t−20, logADV20, vol20_{t−1} (frozen style set as leaf 24 §4).
- SW L1 table pinned: data/v2/sw_l1_pit/industry_members_sw_l1_prefix.parquet, sha256 610b0956ec9a01cda1ea63951751bb993290fa0370079140ed1e6cc882bb6af1 (research default, NOT_PROMOTION_GRADE). Switch to sw_l1_pit_v2 once it lands and Arch pins its sha (prereg amendment, before any run).
- As-of trading-day rule (same as Strategy SW PIT as-of fix; 主 Agent 06:01 ruling; Arch ARCH_STRATEGY_SW_PIT_ASOF_FIX_R2_REVIEW_ZH.md c72f0856 L74 and ARCH_STRATEGY_SW_PIT_ASOF_TRADEDAY_C_REVIEW_ZH.md 28eabd35 L7): member of industry on session d iff in_date < d and (out_date null or out_date ≥ d), d normalized; gap carry: only if the old out_date equals the previous SSE trading day of d, keep the old industry for exactly 1 trading day; calendar passed as parameter; d beyond calendar coverage → error. Note: the Strategy r3/r3b drafts (cd90f2f3 / 821dcfaa) were voided per ARCH_STRATEGY_SW_PIT_FRESHNESS_R4_REVIEW_ZH.md; the rule above is the surviving as-of fix that the audit refers to.
- Factor-library orthogonality: report ρ (de-β) vs capacity_adv, earnings_event, accrual_quality, OCF arm, leaves 15–24.

## 5. 低重合论证与重复硬闸（Overlap, words only; duplicate hard gate）
- vs leaf 23 (desensitized SUE): ranks the CHANGE in earnings scaled by price; leaf 25 ranks the CASH COMPOSITION of the earnings level scaled by assets; accruals are largely orthogonal to surprises in the literature; timing differs (announcement vs persistent). Expected low overlap.
- vs leaf 24 (imax intraday): pure price lottery feature vs no price input; disjoint mechanism and data. Expected very low overlap.
- vs leaf 19 (cfacc_rnoa) and accrual_quality: HIGHEST overlap risk (same family).
- Hard duplicate rule, applied vs leaf 19, accrual_quality, leaf 23, leaf 24: ρ_excess (de-β vs pool EW) > 0.5 OR median top-10 Jaccard ≥ 0.5 → duplicate → FAIL.

## 6. 宇宙与窗口（Universes and windows — frozen）
- HI_LIQ_V1.1 (decisive) and FULLA_V1 (research control, disclosure only), frozen as in leaf 23/24.
- X2: 2024-06-03 → latest panel date at .ok issue. Sealed window 2018-01-02 → 2024-05-31, read ONCE only after X2 passes ALL hard gates, separate Arch .ok; both tiers net excess vs HI_LIQ wb > 0 and same sign as X2, else cap WATCH; family has used this period (not independent OOS).

## 7. 评价与硬闸（Evaluation and hard gates; decisive = HI_LIQ）
- Books: 60w top-6, 100w top-10, long-only, industry cap 25% (HI_LIQ) / 28% (FULLA); 20-name 4% book disclosure only.
- Cost: **30bp per side hard-set** for all judged figures (conservative; matches the 09:25 deep-dive routine); 17.5bp per side computed as disclosure only.
- Annualization: 244 trading days (same as leaf 23/24 engine), printed in the summary.
- Benchmarks: capacity_adv HI_LIQ single-leg book-smoke (cap), HI_LIQ wb, pool EW, 510300. Turnover (monthly one-way), cost drag, gross vs net CAGR; only net (30bp) is judged.
- HI_LIQ wb hard floor (both tiers net CAGR > HI_LIQ wb else FAIL); coverage HI_LIQ ≥ 300, FULLA ≥ 800 else FAIL; alpha_decay_gate v1.1 (leaf_selfcheck_v3.py, pinned sha), fail → WATCH cap; Gate A: ρ vs cap < 0.5 and residual α > 0.
- Gate B: CMC v1.2 (research/alpha_combo_marginal_v1_2.py, selftest r2 + leaf 24 memtest passed), cap80 + leaf 20%, both tiers net CAGR > cap; gating-only (keep/lower, never raise).

## 8. 判定（Verdicts）
- PASS (entry ticket only; promotion only via FWD from 2026-11-02): all hard gates AND both tiers HAC t (NW lag 19) of daily net excess vs HI_LIQ wb ≥ 2.50 same sign AND beats pool EW AND Gate A, Gate B, decay pass AND not duplicate.
- WATCH: hard floor + coverage pass, not duplicate, but any of t* / pool EW / Gate A / Gate B / decay / sealed direction fails.
- FAIL: hard floor, coverage, duplicate, or uncleared C1–C5 run failure.
- report_to_leo only for the decisive spec and only on PASS; sensitivities never a basis for reporting to Leo.

## 9. 试验预算（Trial budget）
- Family n = 4 (leaf 19 cfacc_rnoa, accrual_quality, OCF arm, leaf 25); Bonferroni-Holm two-sided 5% → **t* = 2.50** (same as leaf 23). Raise further if Arch identifies more family members. ONE decisive spec.

## 10. 敏感性（Sensitivities — upfront, disclosure only, uncorrected）
- S-BS (balance-sheet WC accrual), S-NOA (net operating assets denominator), S-noresid (industry+size only), S-exfin-off (keep financials), S-q (latest-quarter accrual, non-TTM), **S-exRE (exclude SW L1 real estate via the same PIT table)**. Each: build HILIQ / build FULLA / eval HILIQ / eval FULLA / merge after the primary; no selection among variants.

## 11. 前置、内存测试与执行（Pre-checks, memtest, execution）
- Step −1 (before memtest; NOT run in this draft): 3-stock TTM hand reconciliation — for 3 Arch-chosen codes and ≥4 as-of dates each (incl. one Q1-before-annual case and one correction case), recompute TTM by hand from raw YTD rows and compare with the script; requires its OWN read-only Arch .ok; any mismatch → stop, report.
- Step 0: memtest build HILIQ / build FULLA / eval FULLA in scratch via harness, separate .ok each; wrapper = cmc_wrapper_v4 (docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh, sha 6174eacb…), STOPKB 1484800, C4 limit 1331200, peak = max(group VmHWM sampler, log hwm, STAGE ru_maxrss, meta RSS; VmPeak excluded).
- Then formal primary → sensitivities, strictly serial, no retries, C1–C5 per step; CMC v1.2 only after its own memtest.
- Preconditions: Arch review of this prereg + script; frozen sha; .ok + .cmd; Arch ruling on process 94322 and concurrency.

## 12. 交付、入组路径与禁止（Deliverables, entry path, prohibitions）
- Deliver: daily base-α vectors (HI_LIQ/FULLA), 60w/100w eval weights, eval summary (benchmarks, net 30bp / gross / 17.5bp disclosure, turnover, decay, gates, duplicate checks, TTM fallback/NaN counts, sensitivities), receipts.
- Entry path if final verdict is PASS: enters Optimizer Core target weights as a SLOW factor (industry ±8%, Size/MidCap ±0.35σ, L1 turnover constraints), NOT as a standalone Top-N satellite; Top-6/Top-10 books are leaf-gate smoke only; fast factors only as trading gates.
- Prohibited: GP, leverage, short leg, sell-side/survey/consensus/analyst data, forecasts/express reports, orders or Strategy handoff, promotion, live, sealed window before X2 passes.
