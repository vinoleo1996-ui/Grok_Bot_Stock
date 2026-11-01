# AI_CMC_WRAPPER_V3_REVIEW (draft for Arch; not committed)

- new file: docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v3_61676a3c.sh sha256 61676a3c812035d99b446e277047721824b3b522efcdea6994347f2d83875ff7; bash -n OK; shellcheck not installed (not run)
- predecessor unchanged: docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v2_dcfef770.sh dcfef770c6f8cf00748778f6944a516952ca5485d011432f6e1b7a7ae9c5e1a4
- synthetic .ok files (in /tmp/w3 only, never in output/): synthetic_allow.ok 236c64a4 (allow_no_guard=true, allow_c5_ignore=true); fake_real_noc5.ok 9e328a8c (allow_no_guard=true only); fake_real_plain.ok b48abaa4 (no allow keys)
- tests: synthetic only (sleep / bash+head /dev/zero), no python, no data, no project code; 94322 not touched (state S throughout)

## Changes vs dcfef770 (per Arch 09:28)
- Guard default ON (94322); passes only if state T or pid exited; checked at launch (refuse rc=89) and every sample (kill group, rc=89).
- --no-guard only if --arch-ok contains line allow_no_guard=true, else refuse rc=90 before launch (also refused when no .ok).
- --c5-ignore: with --arch-ok (real run) needs allow_c5_ignore=true else refuse rc=91; without .ok only allowed under --selftest else rc=91.
- Selftest-only hooks (rc=92 if used without --selftest): --test-stopkb N, --test-force-pgid-mismatch, --selftest-assert (keeps the cmdline assert on in selftest).
- PRELAUNCH log line: guard pid + state + sha of ps_before snapshot (ps now includes STAT column).
- Sampler: VmHWM max and summed VmRSS over all pids in the child process group (catches children, e.g. the memory-hog subshell).
- Stopline rc=95, C5 rc=96, 97, 98 unchanged; _void skipped in selftest; ARCH_OK sha logged.
- rc table: 89 guard | 90 no-guard refused | 91 c5-ignore refused | 92 test hook w/o selftest | 95 stopline | 96 C5 | 97 PGID_MISMATCH | 98 cmdline assert | 2 usage.

## Test outputs (2026-10-18 ~09:31 ET)
```
### T1_stopline: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --test-stopkb 20000 --tag t1 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- bash -c x=$(head -c 50M /dev/zero | tr \\0 a); sleep 5
WRAPPER_DONE tag=t1 rc=95 stopped=1 peak_kb=96584 C4=PASS
wrapper_rc=95
PGREP_G_EMPTY 2866429
exit=95 stopped=1 launched=1
peak_kb=96584 sampler=96584 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
ARCH_OK /tmp/w3/synthetic_allow.ok sha256=236c64a4485899dde19274a6f09ef19264a7560c2c83aea3e9ead915942a63cc
NO_GUARD allowed by .ok allow_no_guard=true
C5_IGNORE pid=94322 (selftest/allowed)
SELFTEST_STOPKB override=20000
PRELAUNCH guard_pid=none guard_state=n/a ps_before=766b7f09de7ecdd6
PGID_OK pid=2866429 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=bash -c x=$(head -c 50M /dev/zero | tr \\0 a); sleep 5 )
STOPLINE hwm_kb=96584 stop_kb=20000
PGREP_G_EMPTY 2866429
samples=1
POSTCHECK pgrep -g 2866429: EMPTY

### T2_rc97: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --test-force-pgid-mismatch --tag t2 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_DONE tag=t2 rc=97 stopped=0 peak_kb=0 C4=PASS
wrapper_rc=97
PGREP_G_EMPTY 2882040
exit=97 stopped=0 launched=1
peak_kb=0 sampler= log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
ARCH_OK /tmp/w3/synthetic_allow.ok sha256=236c64a4485899dde19274a6f09ef19264a7560c2c83aea3e9ead915942a63cc
NO_GUARD allowed by .ok allow_no_guard=true
C5_IGNORE pid=94322 (selftest/allowed)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=f0dcb7af04d60133
SELFTEST_HOOK force PGID mismatch (real pgid=2882040)
PGID_MISMATCH pid=2882040 pgid=2882040-forced
PGREP_G_EMPTY 2882040
samples=0
POSTCHECK pgrep -g 2882040: EMPTY

### T3_rc98: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --selftest-assert --tag t3 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_DONE tag=t3 rc=98 stopped=0 peak_kb=0 C4=PASS
wrapper_rc=98
PGREP_G_EMPTY 2882197
exit=98 stopped=0 launched=1
peak_kb=0 sampler= log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
ARCH_OK /tmp/w3/synthetic_allow.ok sha256=236c64a4485899dde19274a6f09ef19264a7560c2c83aea3e9ead915942a63cc
NO_GUARD allowed by .ok allow_no_guard=true
C5_IGNORE pid=94322 (selftest/allowed)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=4c440d1612bbc466
PGID_OK pid=2882197 guard=none c5_ignore=94322
CMDLINE_ASSERT_FAIL 'alpha_combo' cmdline=
PGREP_G_EMPTY 2882197
samples=0
POSTCHECK pgrep -g 2882197: EMPTY

### T4a_noguard_plain_ok: --arch-ok /tmp/w3/fake_real_plain.ok --no-guard --tag t4a --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_REFUSED tag=t4a rc=90 --no-guard requires allow_no_guard=true in --arch-ok
wrapper_rc=90
exit=90 refused=1 reason=--no-guard requires allow_no_guard=true in --arch-ok launched=0
ARCH_OK /tmp/w3/fake_real_plain.ok sha256=b48abaa4ac99ce472a808b86720c864370fcbb56fd00eb6d5f27088fe7207479
REFUSED rc=90 --no-guard requires allow_no_guard=true in --arch-ok
samples=0
POSTCHECK: nothing launched

### T4b_noguard_no_ok: --selftest --no-guard --tag t4b --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_REFUSED tag=t4b rc=90 --no-guard requires allow_no_guard=true in --arch-ok
wrapper_rc=90
exit=90 refused=1 reason=--no-guard requires allow_no_guard=true in --arch-ok launched=0
REFUSED rc=90 --no-guard requires allow_no_guard=true in --arch-ok
samples=0
POSTCHECK: nothing launched

### T5_c5ignore_fake_real: --arch-ok /tmp/w3/fake_real_noc5.ok --no-guard --c5-ignore 94322 --tag t5 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_REFUSED tag=t5 rc=91 --c5-ignore refused: real run (.ok given) without allow_c5_ignore=true
wrapper_rc=91
exit=91 refused=1 reason=--c5-ignore refused: real run (.ok given) without allow_c5_ignore=true launched=0
ARCH_OK /tmp/w3/fake_real_noc5.ok sha256=9e328a8c2f60c27df7cc08df7cfe2421fa8aa73f8e8cdfb1da722c3502b18eb6
NO_GUARD allowed by .ok allow_no_guard=true
REFUSED rc=91 --c5-ignore refused: real run (.ok given) without allow_c5_ignore=true
samples=0
POSTCHECK: nothing launched

### T6_default_guard: --selftest --tag t6 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 5
WRAPPER_REFUSED tag=t6 rc=89 guard pid 94322 state=S (needs T or exited)
wrapper_rc=89
exit=89 refused=1 reason=guard pid 94322 state=S (needs T or exited) launched=0
PRELAUNCH guard_pid=94322 guard_state=S ps_before=074e7a6b630a166f
REFUSED rc=89 guard pid 94322 state=S (needs T or exited)
samples=0
POSTCHECK: nothing launched

### T7_clean: --selftest --arch-ok /tmp/w3/synthetic_allow.ok --no-guard --c5-ignore 94322 --tag t7 --logdir /tmp/w3/st --outdir /tmp/w3/od --cwd /tmp -- sleep 3
WRAPPER_DONE tag=t7 rc=0 stopped=0 peak_kb=2020 C4=PASS
wrapper_rc=0
PGREP_G_EMPTY 2882459
exit=0 stopped=0 launched=1
peak_kb=2020 sampler=2020 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
ARCH_OK /tmp/w3/synthetic_allow.ok sha256=236c64a4485899dde19274a6f09ef19264a7560c2c83aea3e9ead915942a63cc
NO_GUARD allowed by .ok allow_no_guard=true
C5_IGNORE pid=94322 (selftest/allowed)
PRELAUNCH guard_pid=none guard_state=n/a ps_before=679ad777ef8f0ef6
PGID_OK pid=2882459 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 3 )
samples=13
POSTCHECK pgrep -g 2882459: EMPTY

### stray check
2861878 sleep 300
2895313 sleep 5
94322 state: S (untouched)
```
- Result: T1 stopline rc=95 (hwm 96584 > test STOPKB 20000) group empty; T2 rc=97 group empty; T3 rc=98 group empty; T4a/T4b rc=90 refused, nothing launched; T5 rc=91 refused, nothing launched; T6 default guard rc=89 refused (94322 state S); T7 clean rc=0 group empty.
- T3 note: assert polls up to 5 s, so sleep 5 had exited when the FAIL line printed its (empty) cmdline; assert still correctly failed.
- Stray check: "sleep 300" pid 2861878 belongs to /bin/bash ./deploy_loop.sh (pgid 2859819, started before the tests, not AI); "sleep 5" pid 2895313 was a transient non-test process (gone). No test process survived.

## Diff vs dcfef770 (unified)
```diff
--- docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v2_dcfef770.sh	2026-10-18 09:26:14.723931890 -0400
+++ docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v3_61676a3c.sh	2026-10-18 09:29:03.039931890 -0400
@@ -1,26 +1,50 @@
 #!/bin/bash
-# cmc_wrapper_v2: generic memory/concurrency wrapper (successor of f757e7ca; Arch-approved fixes a-d + peak/C5/kill fixes)
-# usage: cmc_wrapper_v2.sh [--selftest] [--guard-pid PID|--no-guard] [--c5-ignore PID (logged; selftest use)] --tag TAG --logdir DIR --outdir DIR [--meta JSON] [--assert STR] [--cwd DIR] -- CMD [ARGS...]
-#   CMD (interpreter + script + args) is a parameter; nothing is bound here. Env assignments go via: env -u X VAR=1 nice -n 10 <interp> ...
-# exit codes: child rc | 96 C5 hit | 97 PGID_MISMATCH | 98 cmdline assert failed | 95 stopline (child TERM/KILL) | 2 usage
+# cmc_wrapper_v3: successor of cmc_wrapper_v2 (dcfef770). Arch 09:28 rulings: guard default-on (94322, pass iff state T or exited);
+#   --no-guard only with allow_no_guard=true in --arch-ok; --c5-ignore only in synthetic selftests (refused for real runs unless allow_c5_ignore=true);
+#   pre-launch ps snapshot incl. guard pid state. Selftest-only hooks: --test-stopkb N, --test-force-pgid-mismatch, --selftest-assert.
+# usage: cmc_wrapper_v3.sh [--selftest] [--arch-ok OK] [--guard-pid PID|--no-guard] [--c5-ignore PID] --tag TAG --logdir DIR --outdir DIR
+#                          [--meta JSON] [--assert STR] [--cwd DIR] -- CMD [ARGS...]      (CMD/interpreter unbound)
+# rc: child rc | 89 guard pid not T at launch | 90 --no-guard refused | 91 --c5-ignore refused | 92 test hook outside --selftest
+#     | 95 stopline | 96 C5 hit | 97 PGID_MISMATCH | 98 cmdline assert failed | 2 usage
 set -u
-GUARDPID=94322; C5IGN=""; STOPKB=1484800; TGTKB=1331200; HARDKB=1536000; DT=0.2; SELFTEST=0; ASSERT=alpha_combo; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""
+GUARDPID=94322; NOGUARD=0; C5IGN=""; OK=""; STOPKB=1484800; TGTKB=1331200; HARDKB=1536000; DT=0.2; SELFTEST=0; SELFASSERT=0
+ASSERT=alpha_combo; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""; TSTOP=""; TMISMATCH=0
 while [ $# -gt 0 ]; do case "$1" in
-  --selftest) SELFTEST=1; shift;; --tag) TAG=$2; shift 2;; --logdir) L=$2; shift 2;; --outdir) OD=$2; shift 2;;
-  --meta) META=$2; shift 2;; --guard-pid) GUARDPID=$2; shift 2;; --no-guard) GUARDPID=""; shift;; --c5-ignore) C5IGN=$2; shift 2;; --assert) ASSERT=$2; shift 2;; --cwd) RUNCWD=$2; shift 2;; --) shift; break;; *) echo "usage error: $1" >&2; exit 2;; esac; done
+  --selftest) SELFTEST=1; shift;; --selftest-assert) SELFASSERT=1; shift;; --arch-ok) OK=$2; shift 2;;
+  --guard-pid) GUARDPID=$2; shift 2;; --no-guard) NOGUARD=1; shift;; --c5-ignore) C5IGN=$2; shift 2;;
+  --test-stopkb) TSTOP=$2; shift 2;; --test-force-pgid-mismatch) TMISMATCH=1; shift;;
+  --tag) TAG=$2; shift 2;; --logdir) L=$2; shift 2;; --outdir) OD=$2; shift 2;; --meta) META=$2; shift 2;;
+  --assert) ASSERT=$2; shift 2;; --cwd) RUNCWD=$2; shift 2;; --) shift; break;; *) echo "usage error: $1" >&2; exit 2;; esac; done
 [ -n "$TAG" ] && [ -n "$L" ] && [ -n "$OD" ] && [ $# -gt 0 ] || { echo "usage: --tag --logdir --outdir -- CMD" >&2; exit 2; }
 mkdir -p "$L"; S="$L/${TAG}_sampler.txt"; X="$L/${TAG}_exit.txt"; C5F="$L/${TAG}_c5.txt"; LOG="$L/${TAG}.log"; MK="$L/${TAG}_start.marker"
-touch "$MK"; sleep 1
 log() { echo "$(date +%H:%M:%S.%N) $*" >> "$S"; }
-killgrp() { # always the whole process group, never just a shell
-  kill -TERM -- "-$PGID" 2>/dev/null; for _ in 1 2 3 4 5 6 7 8 9 10; do pgrep -g "$PGID" >/dev/null || break; sleep 0.5; done
+refuse() { log "REFUSED rc=$1 $2"; echo "exit=$1 refused=1 reason=$2 launched=0" >> "$X"; echo "WRAPPER_REFUSED tag=$TAG rc=$1 $2"; exit "$1"; }
+okkey() { [ -n "$OK" ] && [ -f "$OK" ] && grep -qxE "$1=true" "$OK"; }
+REAL=0; [ -n "$OK" ] && REAL=1
+[ -n "$OK" ] && { [ -f "$OK" ] || refuse 2 "arch-ok not found: $OK"; log "ARCH_OK $OK sha256=$(sha256sum "$OK" | cut -c1-64)"; }
+# --- policy checks before anything is launched ---
+if [ "$SELFTEST" = 0 ] && { [ -n "$TSTOP" ] || [ "$TMISMATCH" = 1 ] || [ "$SELFASSERT" = 1 ]; }; then refuse 92 "test hook given without --selftest"; fi
+if [ "$NOGUARD" = 1 ]; then okkey allow_no_guard || refuse 90 "--no-guard requires allow_no_guard=true in --arch-ok"; GUARDPID=""; log "NO_GUARD allowed by .ok allow_no_guard=true"; fi
+if [ -n "$C5IGN" ]; then
+  if [ "$REAL" = 1 ]; then okkey allow_c5_ignore || refuse 91 "--c5-ignore refused: real run (.ok given) without allow_c5_ignore=true"
+  elif [ "$SELFTEST" = 0 ]; then refuse 91 "--c5-ignore only allowed in synthetic --selftest"; fi
+  log "C5_IGNORE pid=$C5IGN (selftest/allowed)"; fi
+[ -n "$TSTOP" ] && { STOPKB=$TSTOP; log "SELFTEST_STOPKB override=$STOPKB"; }
+gstate() { [ -e "/proc/$1" ] && awk '{print $3}' "/proc/$1/stat" 2>/dev/null || echo EXITED; }
+guard_ok() { [ -z "$GUARDPID" ] && return 0; s=$(gstate "$GUARDPID"); [ "$s" = T ] || [ "$s" = EXITED ]; }
+# --- pre-launch snapshot incl. guard pid state ---
+ps -eo pid,pgid,stat,ni,rss,etime,args > "$L/${TAG}_ps_before.txt"
+log "PRELAUNCH guard_pid=${GUARDPID:-none} guard_state=$([ -n "$GUARDPID" ] && gstate "$GUARDPID" || echo n/a) ps_before=$(sha256sum "$L/${TAG}_ps_before.txt" | cut -c1-16)"
+guard_ok || refuse 89 "guard pid $GUARDPID state=$(gstate "$GUARDPID") (needs T or exited)"
+touch "$MK"; sleep 1
+killgrp() { kill -TERM -- "-$PGID" 2>/dev/null; for _ in 1 2 3 4 5 6 7 8 9 10; do pgrep -g "$PGID" >/dev/null || break; sleep 0.5; done
   pgrep -g "$PGID" >/dev/null && kill -KILL -- "-$PGID" 2>/dev/null; sleep 0.5
   if pgrep -g "$PGID" >/dev/null; then log "PGID_ALIVE_AFTER_KILL $PGID"; else log "PGREP_G_EMPTY $PGID"; fi; }
-mytree() { # wrapper's own PID tree (self + all descendants), space separated
-  local t=" $$ " n p c; n=1; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case "$t" in *" $c "*) continue;; esac
+mytree() { local t=" $$ " n p c pp; n=1; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case "$t" in *" $c "*) continue;; esac
     pp=$(awk '{print $4}' "$p/stat" 2>/dev/null); case "$t" in *" $pp "*) t="$t$c "; n=1;; esac; done; done; echo "$t"; }
 c5watch() { while kill -0 "$PID" 2>/dev/null; do T=$(mytree); for d in /proc/[0-9]*; do p=${d#/proc/}
-    case "$T" in *" $p "*) continue;; esac; [ -n "$GUARDPID" ] && [ "$p" = "$GUARDPID" ] && continue; [ -n "$C5IGN" ] && [ "$p" = "$C5IGN" ] && continue
+    case "$T" in *" $p "*) continue;; esac
+    [ -n "$GUARDPID" ] && [ "$p" = "$GUARDPID" ] && continue; [ -n "$C5IGN" ] && [ "$p" = "$C5IGN" ] && continue
     g=$(awk '{print $5}' "$d/stat" 2>/dev/null); [ -z "$g" ] && continue; [ "$g" = "$PGID" ] && continue
     hit=""; cw=$(readlink "$d/cwd" 2>/dev/null)
     case "$cw" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="cwd:$cw";; esac
@@ -29,33 +53,33 @@
     if [ -z "$hit" ]; then c=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline"); case "$c" in *python*research/*|*python*scripts/*|*/workspace/QuantLab/research/*.py*|*/workspace/QuantLab/scripts/*.py*) hit="cmd";; esac; fi
     if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline")" >> "$C5F"; killgrp; return; fi
   done; sleep 0.5; done; }
-ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_before.txt"
-cd "$RUNCWD" || exit 2                                   # (a) cd as its own statement
-setsid "$@" > "$LOG" 2>&1 &                              # (b) only the command is backgrounded; setsid does not fork (we are not a pgrp leader), so $! is the command
+cd "$RUNCWD" || exit 2                                   # (a)
+setsid "$@" > "$LOG" 2>&1 &                              # (b) only the command is backgrounded; $! is the command
 PID=$!; PGID=$PID; STOPPED=0; AT=0; RC_OVR=""
 sleep 0.2
 G=$(awk '{print $5}' /proc/$PID/stat 2>/dev/null)
-if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; [ -n "$G" ] && PGID=$G; killgrp; RC_OVR=97; fi   # (c)
+[ "$TMISMATCH" = 1 ] && { log "SELFTEST_HOOK force PGID mismatch (real pgid=$G)"; G="$G-forced"; }
+if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; killgrp; RC_OVR=97; fi   # (c) kill uses PGID (=PID; setsid made it the leader)
 if [ -z "$RC_OVR" ]; then log "PGID_OK pid=$PID guard=${GUARDPID:-none} c5_ignore=${C5IGN:-none}"
-  if [ "$SELFTEST" = 1 ]; then log "SELFTEST: cmdline assert disabled (cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null))"
-  else ok=0; for _ in $(seq 1 25); do grep -qa -- "$ASSERT" /proc/$PID/cmdline 2>/dev/null && { ok=1; break; }; sleep 0.2; done   # env/nice exec chain settles
-    if [ $ok = 1 ]; then log "CMDLINE_ASSERT_OK '$ASSERT'"; else log "CMDLINE_ASSERT_FAIL '$ASSERT' cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null)"; killgrp; RC_OVR=98; fi; fi; fi
+  if [ "$SELFTEST" = 1 ] && [ "$SELFASSERT" = 0 ]; then log "SELFTEST: cmdline assert disabled (cmdline=$(tr '\0' ' ' 2>/dev/null < /proc/$PID/cmdline))"
+  else ok=0; for _ in $(seq 1 25); do grep -qa -- "$ASSERT" /proc/$PID/cmdline 2>/dev/null && { ok=1; break; }; sleep 0.2; done
+    if [ $ok = 1 ]; then log "CMDLINE_ASSERT_OK '$ASSERT'"; else log "CMDLINE_ASSERT_FAIL '$ASSERT' cmdline=$(tr '\0' ' ' 2>/dev/null < /proc/$PID/cmdline)"; killgrp; RC_OVR=98; fi; fi; fi
 if [ -z "$RC_OVR" ]; then c5watch & WPID=$!
-  while kill -0 "$PID" 2>/dev/null; do                                  # (d) 0.2 s sampling
-    H=$(awk '/^VmHWM:/{print $2}' /proc/$PID/status 2>/dev/null); R=$(awk '/^VmRSS:/{print $2}' /proc/$PID/status 2>/dev/null)
-    [ -n "$H" ] && log "VmHWM: $H kB VmRSS: $R kB"
-    if [ -n "$GUARDPID" ] && [ -e /proc/$GUARDPID ] && [ "$(awk '{print $3}' /proc/$GUARDPID/stat 2>/dev/null)" != T ]; then log "GUARD_PID_NOT_T pid=$GUARDPID"; STOPPED=2; killgrp; break; fi
-    if [ -n "$H" ] && [ $AT = 0 ] && [ "$H" -gt $TGTKB ]; then log "ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)"; AT=1; fi
-    if [ -n "$H" ] && [ "$H" -gt $STOPKB ]; then log "STOPLINE hwm_kb=$H stop_kb=$STOPKB"; STOPPED=1; killgrp; break; fi
+  while kill -0 "$PID" 2>/dev/null; do                    # (d) 0.2 s; group-wide VmHWM max (children included)
+    H=0; R=0; for q in $(pgrep -g "$PGID"); do h=$(awk '/^VmHWM:/{print $2}' /proc/$q/status 2>/dev/null); r=$(awk '/^VmRSS:/{print $2}' /proc/$q/status 2>/dev/null)
+      [ -n "$h" ] && [ "$h" -gt "$H" ] && H=$h; [ -n "$r" ] && R=$((R + r)); done
+    log "VmHWM: $H kB VmRSS: $R kB"
+    if ! guard_ok; then log "GUARD_PID_NOT_T pid=$GUARDPID state=$(gstate "$GUARDPID")"; STOPPED=2; killgrp; break; fi
+    if [ "$H" -gt $TGTKB ] && [ $AT = 0 ]; then log "ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)"; AT=1; fi
+    if [ "$H" -gt "$STOPKB" ]; then log "STOPLINE hwm_kb=$H stop_kb=$STOPKB"; STOPPED=1; killgrp; break; fi
     sleep $DT; done
 fi
 rc=0; wait "$PID" || rc=$?
 [ -n "${WPID:-}" ] && { wait "$WPID" 2>/dev/null; [ -s "$C5F" ] && RC_OVR=${RC_OVR:-96}; }
-[ "$STOPPED" = 1 ] && RC_OVR=${RC_OVR:-95}
+[ "$STOPPED" = 1 ] && RC_OVR=${RC_OVR:-95}; [ "$STOPPED" = 2 ] && RC_OVR=${RC_OVR:-89}
 [ -n "$RC_OVR" ] && rc=$RC_OVR
-ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_after.txt"
+ps -eo pid,pgid,stat,ni,rss,etime,args > "$L/${TAG}_ps_after.txt"
 pgrep -g "$PGID" >/dev/null && echo "PGID_ALIVE $PGID" >> "$X" || echo "PGREP_G_EMPTY $PGID" >> "$X"
-# peak = max(sampler, log peak_check hwm_kb, log STOP-line KB, meta peak_rss_mb*1024, meta peak_rss_kb, meta vm_peak_kb)
 P1=$(grep -oE 'VmHWM: [0-9]+' "$S" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
 P2=$(grep -oE 'hwm_kb=[0-9]+' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
 P3=$(grep -oiE 'peak RSS [0-9]+ KB' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
@@ -63,7 +87,7 @@
   P4=$(jq -r '.peak_rss_mb // empty | . * 1024 | floor' "$META" 2>/dev/null); P5=$(jq -r '.peak_rss_kb // empty' "$META" 2>/dev/null); P6=$(jq -r '.vm_peak_kb // empty' "$META" 2>/dev/null); fi
 PEAK=0; for v in "${P1:-0}" "${P2:-0}" "${P3:-0}" "${P4:-0}" "${P5:-0}" "${P6:-0}"; do v=${v%.*}; [ "$v" -gt "$PEAK" ] 2>/dev/null && PEAK=$v; done
 [ "$PEAK" -le $HARDKB ] && C4=PASS || C4=FAIL
-{ echo "exit=$rc stopped=$STOPPED"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} meta_vm_peak_kb=${P6:-} C4=$C4"; } >> "$X"
+{ echo "exit=$rc stopped=$STOPPED launched=1"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} meta_vm_peak_kb=${P6:-} C4=$C4"; } >> "$X"
 if [ "$rc" -ne 0 ] && [ "$SELFTEST" = 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/${TAG}_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"
   find "$OD" -type f -newer "$MK" 2>/dev/null | while read -r f; do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
 echo "WRAPPER_DONE tag=$TAG rc=$rc stopped=$STOPPED peak_kb=$PEAK C4=$C4"
```
