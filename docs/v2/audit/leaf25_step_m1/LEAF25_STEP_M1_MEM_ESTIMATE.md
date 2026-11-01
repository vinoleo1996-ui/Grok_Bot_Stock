# Leaf 25 step -1 memory estimate (file sizes + column math only; no data read)

Inputs (manifest row counts): income financials_pit_tushare 422,129 rows (47.3 MB file); cashflow 315,718 rows (5.1 MB); balancesheet 451,857 rows (130.4 MB file; wide table, only 5 of its columns read); calendar trade_cal_sse_pit small.
Why balancesheet (9ca05496) not bs_cf (01a015bf): bs_cf_pit_manifest documents its balancesheet and cashflow parts as "all update_flag/report_type versions kept" with multi_version stats, but the combined file entry lists only rows; the version rule (P2-A) must be checked per statement, so separate per-statement files are used. Cost: bs_cf would avoid the wide 130 MB file, but column projection makes file width irrelevant to RSS.

Phase 1 (all rows, 5 key columns: ts_code, end_date, available_at, update_flag, report_type), three tables held together:
- pyarrow to_pandas deduplicates string objects by default (deduplicate_objects=True): string cell ~ 8 B pointer + few thousand unique strings.
- per row: 5 cells x 8 B = 40 B; derived end_s 8, avail_sh_date 8, qend_ok 1, row_ord 8, table 8, report_type/update_flag str copies 16 -> ~ 100 B/row (+ index 8).
- 1,189,704 rows x 108 B = 128 MB held; transient norm() copy of the largest table 451,857 x 108 x 1 = 49 MB; Arrow buffers during conversion ~ 451,857 x 5 x 16 B = 36 MB; groupby/concat temporaries ~ 40 MB.
- interpreter + pandas + pyarrow import baseline ~ 150 MB (conservative; leaf 24 harness STAGE imports were in this range).
- Phase 1 peak ~ 150 + 128 + 49 + 36 + 40 = 403 MB.
Phase 2 (3 codes, pushdown filter, ~ 3 x 60 periods x <=8 versions x 3 tables ~ 5k rows): < 5 MB. Phase 1 frames deleted before phase 2.

ESTIMATE: peak RSS ~ 403 MB ~ 413,000 kB; with a 30% safety margin ~ 537,000 kB < 600,000 kB (Arch requirement). Hard 1,536,000; C4 1,331,200; wrapper stop 1,484,800.
Risk noted: if pyarrow dedup were disabled or columns are dictionary-typed differently, string cells could cost ~60 B each -> phase 1 ~ +250 MB (~ 650 MB, over 600k). Mitigation if Arch wants a hard bound: read phase 1 one table at a time and keep only the groupby results (code change, new filename + sha).
