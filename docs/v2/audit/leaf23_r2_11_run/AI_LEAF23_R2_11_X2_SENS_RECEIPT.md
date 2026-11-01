# Leaf23 r2.11 X2 SENS receipt (A04-A27) -- STOP BEFORE A04 (precheck: ps not clean)
- [ZH placeholder] Written by AI executor 2026-10-18 ET with printf+mv (no python). live=false; promotion=false. No step run, no retry, no commit, no agent messaged. .pyc not deleted.

## 1. Precheck (07:25 ET)
- lock output/loop/RESEARCH_QUIET.lock present, sha256 6afb7c1892a3... (OK).
- .ok cf0fa9a135dd... / .cmd 9ce882871a0f... / step table 14899dc8011e... / script 4aa19627cd65...: all match.
- No sensitivity out_dir exists yet (leaf23_sue_desens_cs_* absent).
- Runner prepared WITHOUT python: cp /tmp/l23rerun2_211.py -> /tmp/l23sens_211.py + sed (log dir logs_sens; stop line VmHWM>1331200 kB both in-loop and post-step). Not executed.
- **ps NOT clean** (logs_sens/ps_pre_A04.txt, 07:25:37 ET). Dashboard stack was restarted at 07:25:28-29 ET (parent PID 53), cwd /workspace/quantlab-web:
  - 758615 /bin/bash ./supervise.sh (start 07:25:28)
  - 758619 python3 -X utf8 server.py (start 07:25:28)
  - 758620 /bin/bash ./deploy_supervise.sh (start 07:25:29)
  - 758625 python3 export_static.py (start 07:25:29), spawning /usr/bin/python3 /workspace/quantlab-web/kline.py <code> children (e.g. 759063 sh.601166, 759314 sh.601919)
  - 758898 defunct python3 child of server.py
- Per rule (server.py / supervise.sh / kline.py count as concurrent; when unsure, stop): STOP. A04-A27 not run. .ok cf0fa9a1 not consumed by any sensitivity step.

## 2. Steps
| step | rc | VmHWM kB | meta sha | STAMP | verdict |
|---|---|---|---|---|---|
| A04-A27 | - | - | - | - | NOT RUN (precheck stop) |
- C5 records: none (no step started).

## 3. Disclosures (carried forward)
- 7-name check: current evidence only = 600321.SH delisting cut in FULLA (delisted_cut_name_days_x2 = 552) and cut_failure_check passed; full S=True name-day count of the 7 names awaits a separate read-only .ok from Arch after the window is lifted.
- N4: r0.index == rr.index exists only as the comment at script L890; not recorded in summary/meta, cannot be checked from outputs; next version adds a meta field (P3).
- 07:20 ET python runner-build (string-replace script in /tmp, no data read): Arch ruled P3.

# Run 2 (07:27 ET, Arch cleared after dashboard stop 07:26:36) -- STOP @ A06 (VmHWM > 1331200 kB stop line)
- Precheck 07:27:37 ET: lock 6afb7c1892a3 OK; ps clean (logs_sens/ps_pre_A04_run.txt: only sand-*/websockify/supervise-* system daemons, orca-ide utility, 94322 Tsl; no server.py/supervise.sh/export_static.py/kline.py/start_all.sh).
- Runner /tmp/l23sens_211.py sha256 9afedfe5e3f1a77816b90776593dcf574d5d03c569d87b4ffdcf5954c5df6192 (A01-A03 runner /tmp/l23rerun2_211.py 9d0a172e02e86826b62fee06ceabe504c19e1c1237f8923c693a693d845e21b0). diff (logs_sens/runner_diff.txt):
  - L4: logs_rerun2 -> logs_sens (log path)
  - L130: `if VIOL:` -> `if VIOL or hwm>1331200:` (stop line, in-loop)
  - L145: `if hwm>1536000: fail.append("hwm")` -> `if hwm>1331200: fail.append("hwm>1300MiB")` (stop line, post-step)
  - Only the two allowed changes (stop line appears in 2 places). Nothing else.

| step | ET | rc | VmHWM kB | meta peak_rss_mb | meta sha256 | STAMP | verdict |
|---|---|---|---|---|---|---|---|
| A04 sig-sue fund | 07:27:39-07:27:55 | 0 | 1253936 | 1224.55 | fund_meta b61af37ef8eb549d4eaf685264c4bc59583ae3300f4e7aaa4e2587fed30b44ab | n/a (fund prints no STAMP) | PASS |
| A05 sig-sue build_HILIQ | 07:27:55-07:28:35 | 0 | 1242056 | 1212.95 | build_HILIQ_meta 6eff37780d890f049c9b058e4a4855452d50b73a7f6cab55814d8a4f781ecc05 | n/a (build prints no STAMP) | PASS |
| A06 sig-sue build_FULLA | 07:28:35-07:28:55 | -15 (terminated) | 1336932 | - | none (build_FULLA_meta not written) | n/a | **FAIL: VmHWM > 1331200 kB stop line** |
- A07-A27 not run. C5: 0 violations in A04-A06 (the "C5 other heavy: [{}]" entry in A06 fail list is an empty-dict artifact of the stop path, not a C5 hit). No dashboard process seen.
- A06 log last line: "FULLA 2024 built rss=1188". Context: r2.9 measured build FULLA 1373.7 MiB, so the 1300 MiB stop line was expected to bind here; VmHWM 1336932 kB = 1305.6 MiB, below the 1536000 kB hard line.
- **Disclosure (orphan):** runner terminate() hit the shell=True wrapper only; the python child PID 761978 (reparented to PID 53) kept running after the runner exited at 07:28:55. I found it at ~07:29:02 and sent SIGTERM to my own step process (not a dashboard process); gone by 07:29:04. It wrote no new files after 07:28:50. Runner defect, should kill the process group next version.
- A06 partial outputs left in place (not in _void; the mv rule applied only to dashboard return): leaf23_sue_desens_cs_sig-sue/alpha_FULLA_2024.parquet, gate_FULLA_2024.parquet (07:28:50). A04/A05 outputs kept. Arch to decide on _void.
- Log sha: A04.log b95d559f7b5a1451, A05.log 1e05e642e3fa0161, A06.log a7c92aebfde5f6e5, steps.jsonl a22a62588d17a3b7, runner_A04_A27.out 2eb5417a46831a30, runner_diff.txt 2fe38eebccbc5ef9.
- .pyc not deleted. No commit. No agent messaged. No python other than the runner (plus kill/printf/mv/jq/sha256sum/ps).

# Run 3 (07:30 ET, rerun from A06; Arch approved; A06 run-2 partials in _void/leaf23_r2_11_sens_A06_memstop_20261018/) -- STOP @ A23 (C5)
- Arch ruling: orphan PID 761978 in run 2 = AI P3; run-2 A04/A05 results valid.
- Precheck 07:30:53 ET: lock 6afb7c1892a3 OK; ps clean (logs_sens/ps_pre_A06_run.txt); no FULLA files in sig-sue out_dir. Run-2 A06 log renamed logs_sens/A06_run1_memstop.log.
- Runner /tmp/l23sens2_211.py sha256 12547e9af7cc771a9ba6e162002b901fd259ff7bf573850ab965cfdaa8bfd771, built with cp+sed only, vs A01-A03 runner 9d0a172e02e86826b62fee06ceabe504c19e1c1237f8923c693a693d845e21b0. Full diff (logs_sens/runner2_diff.txt):
```
4c4
< LOG=R+"/docs/v2/audit/leaf23_r2_11_run/logs_rerun2"; AIF=R+"/output/ai_factory"
---
> LOG=R+"/docs/v2/audit/leaf23_r2_11_run/logs_sens"; AIF=R+"/output/ai_factory"
115a116
>     LIM=1484800 if sid in ("A06","A12","A18","A24") else 1331200
122c123
<         p=subprocess.Popen(cmd,shell=True,stdout=f,stderr=subprocess.STDOUT)
---
>         p=subprocess.Popen(cmd,shell=True,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
130,131c131,132
<             if VIOL:
<                 extra+=[str(VIOL)]; p.terminate(); p.wait(); break
---
>             if VIOL or hwm>LIM:
>                 extra+=[str(VIOL)] if VIOL else ["hwm>%d" % LIM]; subprocess.run(["kill","-TERM","--","-%d" % p.pid],capture_output=True); time.sleep(5); subprocess.run(["kill","-KILL","--","-%d" % p.pid],capture_output=True); p.wait(); break
145c146
<     if hwm>1536000: fail.append("hwm")
---
>     if hwm>LIM: fail.append("hwm>%d" % LIM)
```
- Changes = (1) log path; (2) two-tier stop line LIM (1484800 kB for A06/A12/A18/A24, else 1331200 kB), in-loop and post-step; (3) start_new_session=True (setsid) + kill -TERM -PGID, sleep 5, kill -KILL -PGID. Note: the hwm stop path reuses the extra list, so an hwm stop would print under the "C5 other heavy" label (cosmetic).

| step | ET | rc | VmHWM kB | meta peak_rss_mb | meta sha256 | STAMP | C5 viol / records | verdict |
|---|---|---|---|---|---|---|---|---|
| A06 sig-sue build_FULLA | 07:30:58-07:31:39 | 0 | 1399252 | 1366.45703125 | 5cac787d673145fb9cf5361b604313478d3b308b3d2405bf26857eb7cccaedc1 | n/a | 0 / 63 | PASS |
| A07 sig-sue eval_HILIQ | 07:31:40-07:32:29 | 0 | 1080808 | 1055.4765625 | 3a0dbdeb228ba7ded64d36a9731f9dd541398a92f9fbd75687240422951e2742 | 20261018_073144 | 0 / 67 | PASS |
| A08 sig-sue eval_FULLA | 07:32:29-07:33:27 | 0 | 1173576 | 1146.0703125 | 97f8eeb39bb0e9702837c1f3201b6bf5755c5eb8a38a885f53c074b626e5800a | 20261018_073233 | 0 / 80 | PASS |
| A09 sig-sue merge | 07:33:27-07:33:30 | 0 | 439900 | 429.58984375 | 246ba4687b7010edb1d672c45441318bc5222d62d5595825aeb92b20e63ef60f | 20261018_073330 | 0 / 6 | PASS |
| A10 denom-daily fund | 07:33:30-07:33:47 | 0 | 1265448 | 1235.7890625 | 96338c3d1858f5ef5747e49ccae7d3274681d898f11079e3e0a2e446e7e4088c | n/a | 0 / 24 | PASS |
| A11 denom-daily build_HILIQ | 07:33:47-07:34:20 | 0 | 1278544 | 1248.578125 | 22c35ed33deba36b41208ab34f6c3db88c0f79b719d6d76437180079638aaa21 | n/a | 0 / 45 | PASS |
| A12 denom-daily build_FULLA | 07:34:20-07:35:02 | 0 | 1413392 | 1380.265625 | c3b31832f0d90729d1d74284b5b01a9c9ea8467d410428079346894267f764ea | n/a | 0 / 58 | PASS |
| A13 denom-daily eval_HILIQ | 07:35:02-07:35:52 | 0 | 1066860 | 1041.00390625 | 470d266bf062110b6bae8644fab53f0eb4cb248615eaf110c62e2908781487d0 | 20261018_073507 | 0 / 70 | PASS |
| A14 denom-daily eval_FULLA | 07:35:52-07:36:57 | 0 | 1204336 | 1176.109375 | 48a125f7ad3b791810f3869b56161810d06c3c44604f1a27290906bebbc6a454 | 20261018_073557 | 0 / 89 | PASS |
| A15 denom-daily merge | 07:36:57-07:37:00 | 0 | 446832 | 435.76953125 | 386107097f38219c076393e912a64e7e7e62b6c4924725e7294ff02d22b1d859 | 20261018_073700 | 0 / 5 | PASS |
| A16 nofc fund | 07:37:00-07:37:13 | 0 | 1182020 | 1154.31640625 | 3a5a6cc39d4764c568b2cfd48493fb535e011a28e86b1c347147ca9491031281 | n/a | 0 / 17 | PASS |
| A17 nofc build_HILIQ | 07:37:13-07:37:58 | 0 | 1232460 | 1203.57421875 | 470c957e16300232fee0eda79eebea20123e94d1835afbe6b96dbd3598343558 | n/a | 0 / 68 | PASS |
| A18 nofc build_FULLA | 07:37:58-07:38:43 | 0 | 1388964 | 1356.41015625 | f51d274fd04a2f12b5b709545fcc8726d5fd5097be81aa9a2b9d04971b067434 | n/a | 0 / 62 | PASS |
| A19 nofc eval_HILIQ | 07:38:43-07:39:34 | 0 | 1095288 | 1068.8671875 | bb4c820917aa8b3d7d1bc26dfc2ea2933cabf6dabff8433dae7cd1e50a904eb4 | 20261018_073848 | 0 / 72 | PASS |
| A20 nofc eval_FULLA | 07:39:35-07:40:24 | 0 | 1166812 | 1138.5078125 | 1245bc9b1efb73b896fc76185d9ad95ca121bd1c96b2c076edda569993d88eae | 20261018_073939 | 0 / 67 | PASS |
| A21 nofc merge | 07:40:24-07:40:27 | 0 | 446036 | 435.58203125 | 12291866f014fceed395a9bdd8bd144b0acf255f558becc04e8a1a0a9adb7d35 | 20261018_074027 | 0 / 5 | PASS |
| A22 bo40 fund | 07:40:27-07:40:42 | 0 | 1276700 | 1246.77734375 | 17afb03a3248c95e116b5f7faadeafe19421f26da8202f36047e12c8c34e4a46 | n/a | 0 / 22 | PASS |
| A23 bo40 build_HILIQ | 07:40:43-07:41:19 | -15 | 1272840 | - | none | n/a | 1 / 47 | FAIL |

- build_FULLA VmHWM (line 1484800 kB): A06 1399252 kB (1366.5 MiB) PASS; A12 1413392 kB (1380.3 MiB) PASS; A18 1388964 kB (1356.4 MiB) PASS; A24 not run. Run-2 A06 (stopped) was 1336932 kB.
- All passing eval steps: 9 pb peak_check lines + peak_check eval + STAMP; merge steps: peak_check merge + STAMP; fund/build: no STAMP by design (C3b only). C5 records are only-record entries (other agents shell wrappers, sleep, websockify, curl ping); full PID/command/time list in logs_sens/steps.jsonl c5_record.
- **A23 STOP (C5):** at 07:41:14 ET PID 785559 `find . -newer output/d1/supervise_patrol_20261018_0715_ET.md -type f -not -path */node_modules/* -not -path */.git/*`, cwd /workspace/QuantLab, held open dirs under /workspace/QuantLab/data/v2/tushare_raw (anns_d). Touches data -> stop. Source not identified (looks like another agent supervise/patrol scan). Runner killed process group (TERM, 5 s, KILL); A23 rc -15, ended 07:41:19.
- Process group confirmed gone after stop (ps: no g1g5 / find process).
- A23 partial outputs left in place in output/ai_factory/leaf23_sue_desens_cs_bo40/ (alpha_HILIQ_2024/2025, gate_HILIQ_2024/2025, 07:40:54-07:41:05); A22 outputs (fund_meta, event_table*, blackout_pairs) kept. Not moved to _void (mv rule was for dashboard return); Arch to decide. A24-A27 not run.
- Log sha (prefix): A06 ed490213 A07 db9c2e73 A08 2c315678 A09 d254f3eb A10 a122f156 A11 e017be23 A12 5ae07ed5 A13 f47ecfb6 A14 b5b17ca9 A15 a574d518 A16 a3a556b9 A17 4e214c7d A18 d427ff8d A19 04577bcf A20 802754de A21 a5085960 A22 e9a5fe3b A23 52d7256b steps.jsonl 154abfc2 runner_A06_A27.out 3f50cd27 runner2_diff 863c5713 ps_pre_A06_run 0aeb2586.
- .pyc not deleted. No commit. No agent messaged. No python other than the runner.

# Run 4 (07:43 ET, rerun A23-A27; Arch approved; A23 run-3 partials in _void/leaf23_r2_11_sens_A23_c5stop_20261018/) -- STOP @ A24 (C5)
- 785559 (run-3 C5) = Supervise patrol routine of the main agent, now stopped for the window (per Arch).
- Precheck 07:43:29 ET: lock 6afb7c1892a3 OK; runner /tmp/l23sens2_211.py 12547e9a unchanged; .ok cf0fa9a1; ps clean (logs_sens/ps_pre_A23_run.txt). Run-3 A23 log renamed logs_sens/A23_run3_c5stop.log.

| step | ET | rc | VmHWM kB | meta peak_rss_mb | meta sha256 | STAMP | C5 viol | verdict |
|---|---|---|---|---|---|---|---|---|
| A23 bo40 build_HILIQ | 07:43:3x-07:44:01 | 0 | 1264232 | 1234.60 | f74c31ed6509ed8ae7d362cc6fd3cde206359480e8b4998bcd58a36c901a737f | n/a (build) | 0 | PASS |
| A24 bo40 build_FULLA | 07:44:01-07:44:22 | -15 | 1194636 (partial; line 1484800) | - | none | n/a | 1 | FAIL (C5) |
- **A24 STOP (C5):** 07:44:17 ET PID 788830 `rg -l ql_start_all /home/box/.orca /workspace/quantlab-web /home/box`, cwd /tmp, no open files under QuantLab/data or /output. Matched pattern "quantlab" (in /workspace/quantlab-web path). rg is a record-only tool and this scan did not target /workspace/QuantLab, but it searches /home/box recursively (which contains no QuantLab data path by default) and the rule says when unsure stop; runner stopped automatically. Source unknown (looks like someone investigating start_all.sh). Process group TERM/5s/KILL; group confirmed gone (no g1g5 process).
- A24 outputs moved to output/ai_factory/_void/leaf23_r2_11_sens_A24_c5stop_20261018/: alpha_FULLA_2024.parquet 236a2d3f56732d311b716685044759c89180e51a89b8d8925a00275fdd0a5dff, gate_FULLA_2024.parquet 1612071f1fa5b279b4f985ffe170b72a8f40f94d1ec08ff7bc28111ce54f8f54 (both mtime 07:44:16; SHA_MTIME.before + SHA256SUMS.after identical). A22/A23 outputs kept in leaf23_sue_desens_cs_bo40/. A25-A27 not run.
- Log sha (prefix): A23 b8ca7ca0 A24 2079bd5f runner_A23_A27.out d5dd70b6 ps_pre_A23_run eaf0cf3b steps.jsonl 8f75603c.

# Interim summary A04-A27 (as of 07:45 ET; final summary after A27)
- PASS (22): A04 A05 (run 2); A06-A22 (run 3); A23 (run 4). Not yet passed: A24 (C5 stop in run 4); A25-A27 not run.
- build_FULLA VmHWM: A06 1399252 kB (run-2 attempt 1336932 kB, stopped at 1300 line); A12 1413392; A18 1388964; A24 not completed (1194636 kB at stop).
- Stops and handling: run 1 none (precheck stop, dashboard restarted 07:25); run 2 A06 VmHWM>1331200 (orphan 761978, AI P3) -> partials to _void/leaf23_r2_11_sens_A06_memstop_20261018/; run 3 A23 C5 find 785559 (Supervise patrol) -> _void/leaf23_r2_11_sens_A23_c5stop_20261018/; run 4 A24 C5 rg 788830 -> _void/leaf23_r2_11_sens_A24_c5stop_20261018/.
- _void dirs this leaf (r2.11): leaf23_r2_11_intel_overlap_stop_20261018, leaf23_r2_11_rerun1_verscheck_stop_20261018, leaf23_r2_11_sens_A06_memstop_20261018, leaf23_r2_11_sens_A23_c5stop_20261018, leaf23_r2_11_sens_A24_c5stop_20261018.
- .pyc not deleted. No commit. No agent messaged. No python other than the runner.

# Run 5 (07:46 ET, rerun A24-A27; Arch approved; A24 run-4 partials accepted in _void/leaf23_r2_11_sens_A24_c5stop_20261018/) -- A24-A27 ALL PASS
- Precheck 07:46 ET: lock 6afb7c1892a3 OK; runner 12547e9a unchanged; .ok cf0fa9a1; ps clean of python/dashboard/research (logs_sens/ps_pre_A24_run.txt). Disclosure: a pre-existing idle `rg -n enforce\(modes|import.*enforce` PID 701496 (started 06:53:03, cwd /workspace/QuantLab, stdin socket, no files open under data/output) was present; it was also present through runs 3-4; not python, not a data reader; recorded, not a stop. Run-4 A24 log renamed logs_sens/A24_run4_c5stop.log.
- Run-4 false positive (record): 788830 `rg -l ql_start_all ...` cwd /tmp touched no QuantLab data/output and imported no project code; under Arch new wording it is record-only, but the runner stopped on the "quantlab" substring. Arch direction: next runner version judges by cwd and open files, not the substring.

| step | ET | rc | VmHWM kB | meta peak_rss_mb | meta sha256 | STAMP | C5 viol / records | verdict |
|---|---|---|---|---|---|---|---|---|
| A24 bo40 build_FULLA | 07:46:26-07:47:15 | 0 | 1399084 | 1365.48 | cc0dcddb0616f663d32437bf9f7ee64f0aab6f00fe8abf85232202f856870986 | n/a (build) | 0 / 71 | PASS |
| A25 bo40 eval_HILIQ | 07:47:15-07:48:02 | 0 | 1066864 | 1040.94 | 9771c1683df573e7fdd45804eaeadc693194f390e570938cba08b233edf6843f | 20261018_074720 | 0 / 64 | PASS |
| A26 bo40 eval_FULLA | 07:48:02-07:48:51 | 0 | 1182916 | 1154.46 | 18bdfedb8da5c409683f4b6fce35b2251899d4001f39918909950020721fa62e | 20261018_074806 | 0 / 69 | PASS |
| A27 bo40 merge | 07:48:51-07:48:54 | 0 | 450712 | 439.45 | 758a370c246b3394d5b608346fe768705962eea5d282b787f4cafc589a51ef44 | 20261018_074854 | 0 / 4 | PASS |
- Log sha (prefix): A24.log 922c7d50; A25.log 15954c1a; A26.log 19bace6f; A27.log 32c3da8b; runner_A24_A27.out 1a4dcd44; ps_pre_A24_run.txt cf589c8c; steps.jsonl f9e51d8d; 

# FINAL SUMMARY A04-A27 (all 24 steps PASS; .ok cf0fa9a1, .cmd 9ce88287, step table 14899dc8, script 4aa19627)
| step | run | rc | VmHWM kB | meta sha (prefix) | STAMP | verdict |
|---|---|---|---|---|---|---|
| A04 sig-sue fund | 2 | 0 | 1253936 | b61af37e | n/a | PASS |
| A05 sig-sue build_HILIQ | 2 | 0 | 1242056 | 6eff3778 | n/a | PASS |
| A06 sig-sue build_FULLA | 3 | 0 | 1399252 | 5cac787d | n/a | PASS |
| A07 sig-sue eval_HILIQ | 3 | 0 | 1080808 | 3a0dbdeb | 20261018_073144 | PASS |
| A08 sig-sue eval_FULLA | 3 | 0 | 1173576 | 97f8eeb3 | 20261018_073233 | PASS |
| A09 sig-sue merge | 3 | 0 | 439900 | 246ba468 | 20261018_073330 | PASS |
| A10 denom-daily fund | 3 | 0 | 1265448 | 96338c3d | n/a | PASS |
| A11 denom-daily build_HILIQ | 3 | 0 | 1278544 | 22c35ed3 | n/a | PASS |
| A12 denom-daily build_FULLA | 3 | 0 | 1413392 | c3b31832 | n/a | PASS |
| A13 denom-daily eval_HILIQ | 3 | 0 | 1066860 | 470d266b | 20261018_073507 | PASS |
| A14 denom-daily eval_FULLA | 3 | 0 | 1204336 | 48a125f7 | 20261018_073557 | PASS |
| A15 denom-daily merge | 3 | 0 | 446832 | 38610709 | 20261018_073700 | PASS |
| A16 nofc fund | 3 | 0 | 1182020 | 3a5a6cc3 | n/a | PASS |
| A17 nofc build_HILIQ | 3 | 0 | 1232460 | 470c957e | n/a | PASS |
| A18 nofc build_FULLA | 3 | 0 | 1388964 | f51d274f | n/a | PASS |
| A19 nofc eval_HILIQ | 3 | 0 | 1095288 | bb4c8209 | 20261018_073848 | PASS |
| A20 nofc eval_FULLA | 3 | 0 | 1166812 | 1245bc9b | 20261018_073939 | PASS |
| A21 nofc merge | 3 | 0 | 446036 | 12291866 | 20261018_074027 | PASS |
| A22 bo40 fund | 3 | 0 | 1276700 | 17afb03a | n/a | PASS |
| A23 bo40 build_HILIQ | 4 | 0 | 1264232 | f74c31ed | n/a | PASS |
| A24 bo40 build_FULLA | 5 | 0 | 1399084 | cc0dcddb | n/a | PASS |
| A25 bo40 eval_HILIQ | 5 | 0 | 1066864 | 9771c168 | 20261018_074720 | PASS |
| A26 bo40 eval_FULLA | 5 | 0 | 1182916 | 18bdfedb | 20261018_074806 | PASS |
| A27 bo40 merge | 5 | 0 | 450712 | 758a370c | 20261018_074854 | PASS |
- build_FULLA VmHWM (line 1484800 kB = 1450 MiB): A06 1399252 (1366.5 MiB); A12 1413392 (1380.3 MiB); A18 1388964 (1356.4 MiB); A24 1399084 (1366.3 MiB). Max 1413392 kB, below 1536000 kB hard line. All other steps <= 1278544 kB (< 1331200).
- Stops and handling:
  - run 1 (07:25): precheck stop, dashboard restarted by Web hourly start_all.sh; no step run; Arch stopped dashboard 07:26:36.
  - run 2 (07:27): A06 VmHWM 1336932 > 1331200 (old single line); orphan 761978 killed by AI (Arch: AI P3, results valid); partials -> _void/leaf23_r2_11_sens_A06_memstop_20261018/ (by Arch).
  - run 3 (07:30): A23 C5, find 785559 (main agent Supervise patrol) with open dirs under QuantLab/data; partials -> _void/leaf23_r2_11_sens_A23_c5stop_20261018/ (by Arch).
  - run 4 (07:43): A24 C5, rg 788830 (false positive, "quantlab" substring); partials -> _void/leaf23_r2_11_sens_A24_c5stop_20261018/ (by AI, Arch accepted).
  - run 5 (07:46): A24-A27 PASS, no stop.
- All _void dirs for r2.11: leaf23_r2_11_intel_overlap_stop_20261018; leaf23_r2_11_rerun1_verscheck_stop_20261018; leaf23_r2_11_sens_A06_memstop_20261018; leaf23_r2_11_sens_A23_c5stop_20261018; leaf23_r2_11_sens_A24_c5stop_20261018.
- P3 list: 07:20 python runner-build (AI P3); orphan 761978 (AI P3); runner hwm-stop label text; runner "quantlab" substring false positive (next version: judge by cwd + open files); r0.index meta field (next version).
- Pending: 7-name full check (Arch read-only .ok after window lift); .pyc deletion (after Arch archives .ok and user confirms). Not deleted. No commit. No agent messaged. No python other than the runner.
