# AI_CMC_WRAPPER_V4_REVIEW (draft for Arch; not committed)

- new file: docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh sha256 6174eacb4ff2d0905634477430b96bf155d3606794cd66f23a5a38a4f85e4169; bash -n OK; shellcheck not installed
- predecessor unchanged: docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v3_61676a3c.sh 61676a3c812035d99b446e277047721824b3b522efcdea6994347f2d83875ff7
- tests: synthetic only (sleep, exec -a fake argv0, fake STAGE stderr lines, fake meta /tmp/w4/fake_meta.json with vm_peak_kb=9000000); synthetic .ok /tmp/w3/synthetic_allow.ok (236c64a4); no python, no data, no project code; 94322 not touched

## Fixes vs v3
- P1-W1: vm_peak_kb (runguard L114-122 vm_peak_kb() reads VmPeak = peak VIRTUAL size) removed from peak max; still logged as meta_vm_peak_kb_info_only.
- P2-W2: C4 limit = 1331200 kB (C4KB; hard 1536000 kept as constant). Peak now also includes max of STAGE lines "STAGE <name> ru_maxrss=<N>" from the log. Units: runguard L174 rss_kb() = getrusage(RUSAGE_SELF).ru_maxrss, comment "Linux: KB, peak"; alpha_combo_marginal_v1_2 L100-103 prints ru_maxrss raw (kB on Linux). Other sources: VmHWM (kB, /proc status), log hwm_kb= (kB), "peak RSS N KB" (kB), meta peak_rss_mb*1024 (kB), meta peak_rss_kb (kB). All kB, no conversion except MB*1024.
- P2-W3: C5 command match adds *python*scripts_eng/*, */workspace/QuantLab/scripts_eng/*, *python*import research*, *python*-m quantlab*; maps regex adds scripts_eng.
- P3: --assert default alpha_combo_marginal_v1_2 (v1_1 no longer satisfies it). PGID mismatch now calls killmis(): TERM to group + PID + all descendants (incl. setsid-escaped children), KILL after 5 s, logs KILLMIS_EMPTY / KILLMIS_ALIVE.
- Note: C4 is a verdict line in <tag>_exit.txt; it does not change rc (same as v2/v3).

## Test outputs (2026-10-18 ~09:46 ET)
```
### A1_stage_peak_C4fail: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --meta /tmp/w4/fake_meta.json --tag a1 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- bash -c echo "STAGE imports ru_maxrss=120000" >&2; echo "STAGE mk_mem ru_maxrss=1400000" >&2; sleep 1
WRAPPER_DONE tag=a1 rc=0 stopped=0 peak_kb=1400000 C4=FAIL
wrapper_rc=0
PGREP_G_EMPTY 2917334
exit=0 stopped=0 launched=1
peak_kb=1400000 sampler=1900 log_hwm= log_stop= meta_mb_x1024=491520 meta_peak_rss_kb=500000 stage_ru_maxrss=1400000 meta_vm_peak_kb_info_only=9000000 C4=FAIL(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=f46d4f59ce2f0510
PGID_OK pid=2917334 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 1 )
POSTCHECK pgrep -g 2917334: EMPTY

### A2_vmpeak_ignored_C4pass: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --meta /tmp/w4/fake_meta.json --tag a2 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- bash -c echo "STAGE imports ru_maxrss=120000" >&2; echo "STAGE factors ru_maxrss=900000" >&2; sleep 1
WRAPPER_DONE tag=a2 rc=0 stopped=0 peak_kb=900000 C4=PASS
wrapper_rc=0
PGREP_G_EMPTY 2932730
exit=0 stopped=0 launched=1
peak_kb=900000 sampler=1932 log_hwm= log_stop= meta_mb_x1024=491520 meta_peak_rss_kb=500000 stage_ru_maxrss=900000 meta_vm_peak_kb_info_only=9000000 C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=8388f50b774b2e1f
PGID_OK pid=2932730 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 1 )
POSTCHECK pgrep -g 2932730: EMPTY

fake C5 proc pid=2948125 cmdline=python -m quantlab 40 
### B_c5[python -m quantlab]: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --tag b20849 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- sleep 10
WRAPPER_DONE tag=b20849 rc=96 stopped=0 peak_kb=1940 C4=PASS
wrapper_rc=96
PGREP_G_EMPTY 2948147
exit=96 stopped=0 launched=1
peak_kb=1940 sampler=1940 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=ac278da4aab4e543
PGID_OK pid=2948147 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 10 )
PGREP_G_EMPTY 2948147
09:45:57.700053946 C5_HIT pid=2948125 pgid=2917310 cmd cmd=python -m quantlab 40 
POSTCHECK pgrep -g 2948147: EMPTY

fake C5 proc pid=2956022 cmdline=python -c import research.g1g5 40 
### B_c5[python -c import research.g1g5]: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --tag b13656 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- sleep 10
WRAPPER_DONE tag=b13656 rc=96 stopped=0 peak_kb=1884 C4=PASS
wrapper_rc=96
PGREP_G_EMPTY 2956044
exit=96 stopped=0 launched=1
peak_kb=1884 sampler=1884 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=e164b1fa2da5b901
PGID_OK pid=2956044 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 10 )
PGREP_G_EMPTY 2956044
09:46:06.143467403 C5_HIT pid=2956022 pgid=2917310 cmd cmd=python -c import research.g1g5 40 
POSTCHECK pgrep -g 2956044: EMPTY

fake C5 proc pid=2963888 cmdline=python /workspace/QuantLab/scripts_eng/x.py 40 
### B_c5[python /workspace/QuantLab/scripts_eng/x.py]: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --tag b29867 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- sleep 10
WRAPPER_DONE tag=b29867 rc=96 stopped=0 peak_kb=1980 C4=PASS
wrapper_rc=96
PGREP_G_EMPTY 2963920
exit=96 stopped=0 launched=1
peak_kb=1980 sampler=1980 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=27282e26a13eafb2
PGID_OK pid=2963920 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 10 )
PGREP_G_EMPTY 2963920
09:46:13.987435196 C5_HIT pid=2963888 pgid=2917310 cmd cmd=python /workspace/QuantLab/scripts_eng/x.py 40 
POSTCHECK pgrep -g 2963920: EMPTY

fake C5 proc pid=2971818 cmdline=python scripts_eng/x.py 40 
### B_c5[python scripts_eng/x.py]: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --tag b28835 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- sleep 10
WRAPPER_DONE tag=b28835 rc=96 stopped=0 peak_kb=1960 C4=PASS
wrapper_rc=96
PGREP_G_EMPTY 2971862
exit=96 stopped=0 launched=1
peak_kb=1960 sampler=1960 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=2f7b26888e093348
PGID_OK pid=2971862 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 10 )
PGREP_G_EMPTY 2971862
09:46:21.720826989 C5_HIT pid=2971818 pgid=2917310 cmd cmd=python scripts_eng/x.py 40 
POSTCHECK pgrep -g 2971862: EMPTY

### C1_assert_v1_1_rejected: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --selftest-assert --tag c1 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- bash -c exec -a alpha_combo_marginal_v1_1.py sleep 5
WRAPPER_DONE tag=c1 rc=98 stopped=0 peak_kb=0 C4=PASS
wrapper_rc=98
PGREP_G_EMPTY 2979818
exit=98 stopped=0 launched=1
peak_kb=0 sampler= log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=eff5ed7ba535b1a8
PGID_OK pid=2979818 guard=none c5_ignore=94322
CMDLINE_ASSERT_FAIL 'alpha_combo_marginal_v1_2' cmdline=
PGREP_G_EMPTY 2979818
POSTCHECK pgrep -g 2979818: EMPTY

### C2_assert_v1_2_ok: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --selftest-assert --tag c2 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- bash -c exec -a alpha_combo_marginal_v1_2.py sleep 2
WRAPPER_DONE tag=c2 rc=0 stopped=0 peak_kb=2024 C4=PASS
wrapper_rc=0
PGREP_G_EMPTY 2980024
exit=0 stopped=0 launched=1
peak_kb=2024 sampler=2024 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=0b9330991f80d2fe
PGID_OK pid=2980024 guard=none c5_ignore=94322
CMDLINE_ASSERT_OK 'alpha_combo_marginal_v1_2'
POSTCHECK pgrep -g 2980024: EMPTY

### D1_mismatch_kills_children: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --test-force-pgid-mismatch --tag d1 --logdir /tmp/w4/st --outdir /tmp/w4/od --cwd /tmp -- bash -c setsid sleep 37 & sleep 36 & sleep 35
WRAPPER_DONE tag=d1 rc=97 stopped=0 peak_kb=0 C4=PASS
wrapper_rc=97
PGREP_G_EMPTY 2995473
exit=97 stopped=0 launched=1
peak_kb=0 sampler= log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= stage_ru_maxrss= meta_vm_peak_kb_info_only= C4=PASS(limit=1331200)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=f2ca5565f62c7adf
SELFTEST_HOOK force PGID mismatch (real pgid=2995473)
PGID_MISMATCH pid=2995473 pgid=2995473-forced
KILLMIS targets: pgid=2995473 pids=2995473 2995475 2995476 2995477
KILLMIS_EMPTY pgid=2995473 pids=2995473 2995475 2995476 2995477
POSTCHECK pgrep -g 2995473: EMPTY

### stray check
2997312 sleep 5
2997485 sleep 2
2997486 sleep 2
94322 state: T (untouched)
```
- A1: STAGE max 1400000 > 1331200 -> C4=FAIL, peak=1400000 (stage). A2: STAGE max 900000 -> C4=PASS with meta vm_peak_kb=9000000 present (ignored; v3 would have given peak 9000000 and C4 FAIL).
- B (4 fake C5 procs via exec -a, outside wrapper tree): all four caught, rc=96, group empty.
- C1: argv0 alpha_combo_marginal_v1_1.py rejected by default assert -> rc=98; C2: alpha_combo_marginal_v1_2.py -> CMDLINE_ASSERT_OK rc=0.
- D1: forced mismatch with a setsid-escaped child (sleep 37) + 2 children: KILLMIS targets 4 pids, KILLMIS_EMPTY, rc=97.
- Stray check: remaining sleep 5 / sleep 2 are system supervise loops (exec-daemon/egress/USR1 ticker), not test processes; verified by parent. Fake C5 procs were killed by the test harness. 94322 was state T at end (Data resumed/stopped it; AI did not touch it).

## Diff vs v3 (unified)
```diff
--- docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v3_61676a3c.sh	2026-10-18 09:29:03.039931890 -0400
+++ docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v4_6174eacb.sh	2026-10-18 09:45:13.119931890 -0400
@@ -1,14 +1,15 @@
 #!/bin/bash
-# cmc_wrapper_v3: successor of cmc_wrapper_v2 (dcfef770). Arch 09:28 rulings: guard default-on (94322, pass iff state T or exited);
+# cmc_wrapper_v4: successor of cmc_wrapper_v3 (61676a3c). Arch 09:44: P1-W1 vm_peak_kb excluded from peak (VmPeak = virtual, runguard L114-122); P2-W2 C4 vs 1331200 + STAGE ru_maxrss (kB, Linux getrusage) in peak; P2-W3 C5 adds scripts_eng/, python -c "import research", -m quantlab; P3 assert default alpha_combo_marginal_v1_2, PGID mismatch also kills children.
+# (v3 header:) successor of cmc_wrapper_v2 (dcfef770). Arch 09:28 rulings: guard default-on (94322, pass iff state T or exited);
 #   --no-guard only with allow_no_guard=true in --arch-ok; --c5-ignore only in synthetic selftests (refused for real runs unless allow_c5_ignore=true);
 #   pre-launch ps snapshot incl. guard pid state. Selftest-only hooks: --test-stopkb N, --test-force-pgid-mismatch, --selftest-assert.
-# usage: cmc_wrapper_v3.sh [--selftest] [--arch-ok OK] [--guard-pid PID|--no-guard] [--c5-ignore PID] --tag TAG --logdir DIR --outdir DIR
+# usage: cmc_wrapper_v4.sh [--selftest] [--arch-ok OK] [--guard-pid PID|--no-guard] [--c5-ignore PID] --tag TAG --logdir DIR --outdir DIR
 #                          [--meta JSON] [--assert STR] [--cwd DIR] -- CMD [ARGS...]      (CMD/interpreter unbound)
 # rc: child rc | 89 guard pid not T at launch | 90 --no-guard refused | 91 --c5-ignore refused | 92 test hook outside --selftest
 #     | 95 stopline | 96 C5 hit | 97 PGID_MISMATCH | 98 cmdline assert failed | 2 usage
 set -u
 GUARDPID=94322; NOGUARD=0; C5IGN=""; OK=""; STOPKB=1484800; TGTKB=1331200; HARDKB=1536000; DT=0.2; SELFTEST=0; SELFASSERT=0
-ASSERT=alpha_combo; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""; TSTOP=""; TMISMATCH=0
+ASSERT=alpha_combo_marginal_v1_2; C4KB=1331200; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""; TSTOP=""; TMISMATCH=0
 while [ $# -gt 0 ]; do case "$1" in
   --selftest) SELFTEST=1; shift;; --selftest-assert) SELFASSERT=1; shift;; --arch-ok) OK=$2; shift 2;;
   --guard-pid) GUARDPID=$2; shift 2;; --no-guard) NOGUARD=1; shift;; --c5-ignore) C5IGN=$2; shift 2;;
@@ -40,6 +41,8 @@
 killgrp() { kill -TERM -- "-$PGID" 2>/dev/null; for _ in 1 2 3 4 5 6 7 8 9 10; do pgrep -g "$PGID" >/dev/null || break; sleep 0.5; done
   pgrep -g "$PGID" >/dev/null && kill -KILL -- "-$PGID" 2>/dev/null; sleep 0.5
   if pgrep -g "$PGID" >/dev/null; then log "PGID_ALIVE_AFTER_KILL $PGID"; else log "PGREP_G_EMPTY $PGID"; fi; }
+desc() { local t="$1" n=1 p c pp; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case " $t " in *" $c "*) continue;; esac; pp=$(awk '{print $4}' "$p/stat" 2>/dev/null); case " $t " in *" $pp "*) t="$t $c"; n=1;; esac; done; done; echo "$t"; }
+killmis() { local all; all=$(desc "$PID"); log "KILLMIS targets: pgid=$PGID pids=$all"; kill -TERM -- "-$PGID" 2>/dev/null; kill -TERM $all 2>/dev/null; sleep 5; kill -KILL -- "-$PGID" 2>/dev/null; kill -KILL $all 2>/dev/null; sleep 0.5; local left=""; for q in $all; do [ -e /proc/$q ] && [ "$(awk '{print $3}' /proc/$q/stat 2>/dev/null)" != Z ] && left="$left $q"; done; pgrep -g "$PGID" >/dev/null && left="$left pg:$PGID"; if [ -n "$left" ]; then log "KILLMIS_ALIVE$left"; else log "KILLMIS_EMPTY pgid=$PGID pids=$all"; fi; }
 mytree() { local t=" $$ " n p c pp; n=1; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case "$t" in *" $c "*) continue;; esac
     pp=$(awk '{print $4}' "$p/stat" 2>/dev/null); case "$t" in *" $pp "*) t="$t$c "; n=1;; esac; done; done; echo "$t"; }
 c5watch() { while kill -0 "$PID" 2>/dev/null; do T=$(mytree); for d in /proc/[0-9]*; do p=${d#/proc/}
@@ -49,8 +52,8 @@
     hit=""; cw=$(readlink "$d/cwd" 2>/dev/null)
     case "$cw" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="cwd:$cw";; esac
     if [ -z "$hit" ]; then for fd in "$d"/fd/*; do t=$(readlink "$fd" 2>/dev/null); case "$t" in /workspace/QuantLab/data/*|/workspace/QuantLab/output/*) hit="fd:$t"; break;; esac; done; fi
-    if [ -z "$hit" ]; then m=$(grep -m1 -oE '/workspace/QuantLab/(research|scripts)/[^ ]+' "$d/maps" 2>/dev/null); [ -n "$m" ] && hit="map:$m"; fi
-    if [ -z "$hit" ]; then c=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline"); case "$c" in *python*research/*|*python*scripts/*|*/workspace/QuantLab/research/*.py*|*/workspace/QuantLab/scripts/*.py*) hit="cmd";; esac; fi
+    if [ -z "$hit" ]; then m=$(grep -m1 -oE '/workspace/QuantLab/(research|scripts|scripts_eng)/[^ ]+' "$d/maps" 2>/dev/null); [ -n "$m" ] && hit="map:$m"; fi
+    if [ -z "$hit" ]; then c=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline"); case "$c" in *python*research/*|*python*scripts/*|*python*scripts_eng/*|*python*import\ research*|*python*-m\ quantlab*|*/workspace/QuantLab/scripts_eng/*|*/workspace/QuantLab/research/*.py*|*/workspace/QuantLab/scripts/*.py*) hit="cmd";; esac; fi
     if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline")" >> "$C5F"; killgrp; return; fi
   done; sleep 0.5; done; }
 cd "$RUNCWD" || exit 2                                   # (a)
@@ -59,7 +62,7 @@
 sleep 0.2
 G=$(awk '{print $5}' /proc/$PID/stat 2>/dev/null)
 [ "$TMISMATCH" = 1 ] && { log "SELFTEST_HOOK force PGID mismatch (real pgid=$G)"; G="$G-forced"; }
-if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; killgrp; RC_OVR=97; fi   # (c) kill uses PGID (=PID; setsid made it the leader)
+if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; killmis; RC_OVR=97; fi   # (c) P3: kill group + pid + all descendants
 if [ -z "$RC_OVR" ]; then log "PGID_OK pid=$PID guard=${GUARDPID:-none} c5_ignore=${C5IGN:-none}"
   if [ "$SELFTEST" = 1 ] && [ "$SELFASSERT" = 0 ]; then log "SELFTEST: cmdline assert disabled (cmdline=$(tr '\0' ' ' 2>/dev/null < /proc/$PID/cmdline))"
   else ok=0; for _ in $(seq 1 25); do grep -qa -- "$ASSERT" /proc/$PID/cmdline 2>/dev/null && { ok=1; break; }; sleep 0.2; done
@@ -83,11 +86,12 @@
 P1=$(grep -oE 'VmHWM: [0-9]+' "$S" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
 P2=$(grep -oE 'hwm_kb=[0-9]+' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
 P3=$(grep -oiE 'peak RSS [0-9]+ KB' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
+P7=$(grep -oE "^STAGE [^ ]+ ru_maxrss=[0-9]+" "$LOG" 2>/dev/null | grep -oE "[0-9]+$" | sort -n | tail -1)   # P2-W2: ru_maxrss kB (Linux getrusage, runguard L174 / v1_2 L100)
 P4=""; P5=""; P6=""; if [ -n "$META" ] && [ -f "$META" ]; then
   P4=$(jq -r '.peak_rss_mb // empty | . * 1024 | floor' "$META" 2>/dev/null); P5=$(jq -r '.peak_rss_kb // empty' "$META" 2>/dev/null); P6=$(jq -r '.vm_peak_kb // empty' "$META" 2>/dev/null); fi
-PEAK=0; for v in "${P1:-0}" "${P2:-0}" "${P3:-0}" "${P4:-0}" "${P5:-0}" "${P6:-0}"; do v=${v%.*}; [ "$v" -gt "$PEAK" ] 2>/dev/null && PEAK=$v; done
-[ "$PEAK" -le $HARDKB ] && C4=PASS || C4=FAIL
-{ echo "exit=$rc stopped=$STOPPED launched=1"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} meta_vm_peak_kb=${P6:-} C4=$C4"; } >> "$X"
+PEAK=0; for v in "${P1:-0}" "${P2:-0}" "${P3:-0}" "${P4:-0}" "${P5:-0}" "${P7:-0}"; do v=${v%.*}; [ "$v" -gt "$PEAK" ] 2>/dev/null && PEAK=$v; done   # P1-W1: P6 (vm_peak_kb = VmPeak, virtual) logged only, NOT in peak
+[ "$PEAK" -le $C4KB ] && C4=PASS || C4=FAIL   # P2-W2: C4 limit 1331200 kB (hard 1536000 kept for reference)
+{ echo "exit=$rc stopped=$STOPPED launched=1"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} stage_ru_maxrss=${P7:-} meta_vm_peak_kb_info_only=${P6:-} C4=$C4(limit=$C4KB)"; } >> "$X"
 if [ "$rc" -ne 0 ] && [ "$SELFTEST" = 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/${TAG}_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"
   find "$OD" -type f -newer "$MK" 2>/dev/null | while read -r f; do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
 echo "WRAPPER_DONE tag=$TAG rc=$rc stopped=$STOPPED peak_kb=$PEAK C4=$C4"
```
