# Leaf 25 step -1 r2 memory estimate (file sizes, Arch-verified schema/row counts in review fc5fa937 L48-57; no data read)

- Script: research/leaf25_ttm_recon_step_m1_r2.py sha256 f46e0fb5898ba58566c4c6fa6ed05b370a36a38941f766ffcbbee56d316956da. Supersedes LEAF25_STEP_M1_MEM_ESTIMATE.md (bf2c29fe; kept unchanged).
- Runtime (Arch L99): pandas 3.0.6 + pyarrow 25.0.1; strings come back Arrow-backed (str dtype), not per-cell Python objects.
- Rows: income 422,129; cashflow 315,718; balance 451,857 (one row group each); calendar 8,035.

Phase 1 (all rows, 5 key columns, three tables held together, then filtered copies U):
- ~100-110 B/row incl. derived columns -> 1,189,704 rows ~ 128 MB; norm() transient copy of largest table ~ 49 MB; Arrow buffers ~ 36 MB; value_counts / orphan groupby / filtered copies U (<= one more set) ~ 60 MB; trigger groupbys ~ 30 MB.
- import baseline ~ 150 MB.
- Phase 1 peak ~ 150 + 128 + 49 + 36 + 60 + 30 ~ 455 MB.

Phase 2 (corrected per N-P3-5): each file is a single row group, so the ts_code filter cannot skip row groups; pyarrow first materializes the projected columns (12 key+value columns for income, <= 9 for the others) for all ~452k rows, then filters. Transient per table ~ 452k x 12 x ~10 B ~ 55 MB Arrow, freed after filtering; tens of MB, not <5 MB. Phase-1 frames are deleted before phase 2, so phase 2 stays below the phase-1 peak.

ESTIMATE: typical peak ~ 455 MB ~ 466,000 kB (< 600,000). Worst case (string cells as Python objects, ~ +200 MB) ~ 650 MB ~ 665,000 kB; Arch L99-100 rules this unlikely and no dictionary read / pre-filter is required.
.ok memory keys: C4 line 1331200 kB (M = max(STAGE ru_maxrss, sampled VmHWM, runguard STOP, JSON peak_rss_kb); vm_peak excluded); wrapper STOPKB 1484800 (default); hard 1536000; expected-peak report line 650000 kB - exceeding it is P3 review only, not void.
