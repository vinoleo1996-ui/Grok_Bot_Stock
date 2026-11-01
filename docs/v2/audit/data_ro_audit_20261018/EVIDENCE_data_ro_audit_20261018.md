# Read-only metadata audit, Data, 2026-10-18 (ET). No .ok needed (Arch rule): no project imports, no repo writes.
Commands: `PYTHONDONTWRITEBYTECODE=1 nice -n 10 /usr/bin/python3 /tmp/data_ro_audit_20261018/<script>`. Before each step: `pgrep -af 'research/|leaf'` returned empty. MemAvailable was about 10.9GB.
Scripts: s0_schema.py, a1_sw.py (06:44:26 ET), a2_sw.py (06:44:32), b1_cal.py (06:44:40). Outputs: A_output.txt, A2_output.txt, B_output.txt. Per-file read shas: A_reads.csv. Peak VmHWM was 259MB (a1).

## Input shas
- industry_members_sw_l1_pit.parquet 0b1d3432…89f6 (matches manifest); bak_pre_fix 59734014…9c; sw2021_members_l1l2l3_raw 4e36abc3…789a; manifest.json 7c73e70b…36d282
- trade_cal_sse_pit.parquet fa4260b8…8a41 (matches manifest); calendar/manifest.json 7ccc911e…89a4; tushare_raw/trade_cal.parquet 141078fa…6d06086
- stock_delisted_v2 9d757b96…3750; sw_pit_refresh.py a18684fe…96e9; trade_cal_pit.py 90e3df43…2f54

## A. SW L1 PIT
- Current table: 7573 rows / 5600 instruments. Pre-fix bak: 7743 / 5759. Raw union: 11028 / 5600. Per-L1 pulls in tushare_raw/index_member_all (62 files, mtime 10-18 01:08): 7920 rows / 5914 codes.
- (a) Reproduced: 12 codes with 2 open L1 rows each (list in A_12codes_open_records.csv). The raw union also has 2 open rows for each of them. The per-L1 pulls have exactly 1 open row, and the other row appears there closed (e.g. 002420 801110 2021-07-30→2026-06-30 N). The extra open rows come from the unfiltered full Y/N paginated pull, which returns stale or inconsistent versions (e.g. 002420 801110 in_date 2010-06-01 open Y, and rows marked is_new=Y that carry an out_date). Verdict: the relay/source is inconsistent between endpoints, and our merge amplifies it. sw_pit_refresh.py does concat + exact-row drop_duplicates, then groupby(instrument, code, out_key). Nothing gives precedence or reconciles open vs closed versions of the same membership, so both survive.
- (b) Could not reproduce 477 with the stated definition. My universe: SSE/SZ 6-digit codes, list_date ≤ D, not delisted (stock_basic D/L/P + stock_delisted_v2). That gives 349 codes missing an active L1 membership on every trading day from 2026-09-24 to 10-16 (11 days, 3839 code-days); the gap is constant per day. Classification (B_missing_codes_classified.csv):
  - 235 codes: in the pre-fix bak and in the per-L1 pulls (open Y), but dropped from the current table. The 10-14 04:00 fix removed 254 codes (7743→7573). This does not match docs/v2/ALPHA_DATA_D5D6_FIX_ZH.md, which says 7735 rows plus an is_primary column; the current file has no is_primary. Verdict: our merge/fix step.
  - 68 codes: only in the per-L1 pulls, never in our build. Their max in_date is 2026-01-23, all Y. Verdict: the full-pull truncation was not backfilled (our pull/merge).
  - 46 codes: present in the table but with no active row (closed history only). Likely a source gap (matches the doc's "197 with no current class, source empty").
  - No missing code was listed after 2026-06.

## B. trade_cal_sse_pit
- max cal_date 20261231; 8035 rows; 5343 open days. These match the manifest.
- (1) Builder ran 00:18:48 ET (logs/nightly/20261016_trade_cal.log) and wrote finished_at 04:19:01Z (00:19 ET). stat on the parquet: Birth 01:13:35.472, Modify 01:13:35.476, Change 01:13:35.500. manifest.json was born 01:13:35.432. A new inode was created at 01:13, so the file was not touched in place, and its content is byte-identical (sha matches). 50,685 repo files have mtime between 01:12 and 01:15. _recovery/ai/RECOVERY_MANIFEST_ZH.md records that the workspace was bulk-rewritten between 01:13:24 and 01:14:51 ET after the 01:05 restart. mtimes were not preserved, so that rewrite was not cp -p/rsync -a. Verdict: an external workspace restore rewrote the files; the data did not change.
- (2) In the raw pull, 20130424 (is_open=1) has an empty pretrade_date, and it is row 0 of data/v2/tushare_raw/trade_cal.parquet, at a page boundary. trade_cal_pit.py copies pretrade_date verbatim; it derives nothing. Every overlapping row is identical between PIT and raw (0 diffs). Every YYYY0101 row is also blank (closed days, harmless). Verdict: a Tushare/relay source quirk. The correct value is 20130423.
