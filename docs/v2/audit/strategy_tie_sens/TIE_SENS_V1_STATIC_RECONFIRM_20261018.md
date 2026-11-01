# TIE_SENS v1 static reconfirm (no run)

- issued_et: 2026-10-18T13:08:44-04:00
- signer: QuantLab Arch
- mode: static only. No script run, no project import, no data contents read. sha256 of code/output files and manifest metadata only.
- live=false, promotion=false

## Verdict: RECONFIRMED (with caveats below)

The v1 results stand. Rerunning v1 with the current hx2 7b8235dc would not change them, because the TIE_SENS code path is the same apart from one SW freshness/integrity check. That check only warns on staleness. No rerun is needed.

## Evidence

1. Pins: script research/strategy_tie_sensitivity_prereg_v1.py = abef35f4d8422b6c4caa1a9551d5b62c36ae0349b843776739d0591c2b89f587. Current dep_ts 912fb007, dep_lr fed36cf2 and prereg 0af0aa10 all equal the values in v1 summary.json measured_sha256. Only dep_hx2 differs: v1 used 3f7f75c3, and the current file is 7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1.
2. hx2 history: 3f7f75c3 = git e7b240d. HEAD 7dd5bea = 1c51531a (freshness r4). The working tree is 7b8235dc and is uncommitted (git status M), the result of the PIT-fix landings r2/r3d/r3e. The diff 3f7f75c3 -> 7b8235dc is large (+246/-26). It is NOT freshness-only at file level.
3. TIE_SENS call path (static trace): prereg_v1 -> ts (912fb007) -> lr (fed36cf2) -> hx2. The path uses only these hx2 members: load_industry_map(), apply_ind_cap, _is_etf, to_id, load_leg, and the constants BAL/CAP/IND_CAP/N_BY_AUM/X2. run_smoke is lr's own definition. AST comparison of top-level defs: changed = load_industry_map, build_topn, run_smoke, smallcap_and_industry, main; added = pitfix/asof helpers and _cli. Of the changed defs, only load_industry_map is on the path.
4. The load_industry_map change is one added call, sw_pit_ensure_checked(ROOT, as_of=X2[1], as_of_defaulted=True). The read (data/v2/sw_pit/industry_members_sw_l1_pit.parquet) and the last-name-per-ts_code mapping are unchanged. research/sw_pit_freshness.py: staleness and coverage_gap only warn. Caveat: integrity failures (manifest/sha/calendar) RAISE SwPitIntegrityError, so the check is not purely warn-only. It only fails closed and cannot change the numbers.
5. sw_members_asof: imported at module level in hx2 (IndustryAsOf, load_sw_l1, sw_l1_asof_chunked, load_trade_cal, check_allow_ok, ...). None of these is called on the TIE_SENS path: load_industry_map, apply_ind_cap, ts and lr do not reference them. Caveat: module import side effects are now on the path (new imports at import time).
6. SW table: the legacy path data/v2/sw_pit/industry_members_sw_l1_pit.parquet. manifest data/v2/sw_pit/manifest.json (sha 7c73e70b152126d5a37ee9a002c55dd6a7542a7ae0519152c720a7384436d282) lists it as 0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6. The CLEAN 89d4afa3 / 87d769aa are used only by load_industry_asof/pitfix, which are off-path. The parquet bytes were not hashed by Arch; the ensure_checked integrity check verifies them at run time.
7. v1 output output/strategy_hiliq/tie_sens_prereg_v1: summary.json = 2f7ff034f42fce31aafec973735b39fc1806740efdebce8d0d3ae39f60e2d60b. There is no separate artifact manifest. The 98 top-level entries are 48 weights_B4_*.parquet (24 variants x 2 tiers), 49 smoke_* dirs (48 matching the weights plus smoke_CAPADV_ONLY_PROD, the capadv-only reconcile) and summary.json. v1 run_auth ARCH_RUN_AUTH_TIE_SENS_v1.ok sha 9a4e82b2. Mtimes run 2026-10-18 01:22-01:37 ET.

## Recommendation
- Do not issue a TIE_SENS v2 code-change .ok or run .ok. The v1 results stand as the deterministic reference.
- If the reference for the 60/100 tiers must be pinned to the current hx2, record 7b8235dc as "path-equivalent to 3f7f75c3 for TIE_SENS" per items 3-5.
