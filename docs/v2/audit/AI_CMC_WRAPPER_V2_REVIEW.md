# AI_CMC_WRAPPER_V2_REVIEW (draft for Arch; not committed)

- new file: docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v2_dcfef770.sh sha256 dcfef770c6f8cf00748778f6944a516952ca5485d011432f6e1b7a7ae9c5e1a4
- predecessor (unchanged): docs/v2/audit/cmc_v1_1_leaf24/cmc_l24_wrapper_f757e7ca.sh f757e7ca721adb2dfc07447fc2b22c13b59dceedc3543d3097fb221e5a903b13; 572ca30f also unchanged
- drafts kept in /tmp/w2 (draft.sh..draft4.sh); final = draft4.sh
- checks: bash -n OK; shellcheck NOT installed on box (not run); no python, no data read

## Changes vs f757e7ca
- (a) `cd "$RUNCWD"` is its own statement (default /workspace/QuantLab, --cwd).
- (b) only `setsid "$@" > LOG 2>&1 &` is backgrounded; command/interpreter are positional params after `--` (nothing bound). Non-interactive bash child is not a pgrp leader, so setsid does not fork and $! is the command PID.
- (c) after 0.2 s: pgid from /proc/$PID/stat must equal $PID else PGID_MISMATCH -> kill group, rc=97; then /proc/$PID/cmdline must contain --assert STR (default alpha_combo; polled up to 5 s for env/nice exec chain) else kill group, rc=98. --selftest disables the cmdline assert and _void handling only.
- (d) VmHWM/VmRSS sampled every 0.2 s.
- Peak: at exit peak_kb = max(sampler, log hwm_kb=, log "peak RSS N KB" STOP line, meta peak_rss_mb*1024, meta peak_rss_kb, meta vm_peak_kb) via grep/jq; C4 = peak_kb <= 1536000; written to <tag>_exit.txt.
- Kills: single killgrp(): kill -TERM -PGID, poll pgrep -g up to 5 s, kill -KILL -PGID, then log PGREP_G_EMPTY / PGID_ALIVE_AFTER_KILL. Used by stopline, guard, C5, 97, 98. Never targets a shell only.
- C5: foreign = any pid outside the wrapper own PID tree (self + descendants, rebuilt each scan) and outside the child pgid, whose cwd is under QuantLab/{data,output}, or has an open fd there, or maps project code (QuantLab/research|scripts) in /proc/pid/maps, or runs python on research/ or scripts/. Hit -> killgrp, rc=96. f757e7ca matched cmdline substrings and skipped only the (wrong) pgid.
- Guard: --guard-pid PID (default 94322) must be in state T, else killgrp (rc from child, typically 143, stopped=2); --no-guard disables. --c5-ignore PID: explicit logged exclusion, intended for selftest only.
- Kept: STOPKB 1484800 (rc=95 override), ABOVE_TARGET 1331200 report-only, _void on non-zero rc (files in --outdir newer than start marker -> output/ai_factory/_void/<tag>_rc<rc>_<ts>, sha+mtime first), ps before/after, final pgrep -g.

## Selftest output (sleep 3, no python, no data; 2026-10-18 ~09:26 ET)
```
## run A: --selftest --no-guard --c5-ignore 94322 -- sleep 3 (clean PID path)
WRAPPER_DONE tag=stA rc=0 stopped=0 peak_kb=1936 C4=PASS
wrapper_rc=0
PGREP_G_EMPTY 2813124
exit=0 stopped=0
peak_kb=1936 sampler=1936 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
PGID_OK pid=2813124 guard=none c5_ignore=94322
SELFTEST: cmdline assert disabled (cmdline=sleep 3 )
samples=14 c5_file=none
## run B: --selftest (default guard 94322) -- sleep 3
WRAPPER_DONE tag=stB rc=143 stopped=2 peak_kb=1932 C4=PASS
wrapper_rc=143
PGREP_G_EMPTY 2828620
exit=143 stopped=2
peak_kb=1932 sampler=1932 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
PGID_OK pid=2828620 guard=94322 c5_ignore=none
SELFTEST: cmdline assert disabled (cmdline=sleep 3 )
GUARD_PID_NOT_T pid=94322
PGREP_G_EMPTY 2828620
## run C: --selftest --no-guard (C5 not ignoring 94322) -- sleep 3
WRAPPER_DONE tag=stC rc=96 stopped=0 peak_kb=1980 C4=PASS
wrapper_rc=96
PGREP_G_EMPTY 2844109
exit=96 stopped=0
peak_kb=1980 sampler=1980 log_hwm= log_stop= meta_mb_x1024= meta_peak_rss_kb= meta_vm_peak_kb= C4=PASS
09:26:56.252048454 C5_HIT pid=94322 pgid=94322 cmd cmd=python3 scripts/acquire/remaining_after_stk_surv.py 
```
- A shows the fixed PID path: PGID_OK, 14 samples in ~3 s, rc=0, group empty.
- B/C: 94322 is NO LONGER in state T (now S/Ssl, resumed by someone after the 09:05:48 quiet-window lift; not by AI). Default guard stops the run (B), and C5 flags 94322 as a foreign data process (C). Any real run now would stop unless Arch rules on 94322.
- Not exercised: STOPLINE, rc=97, rc=98 (would need a memory hog / real cmd; not done).

## Diff vs f757e7ca (unified)
```diff
--- docs/v2/audit/cmc_v1_1_leaf24/cmc_l24_wrapper_f757e7ca.sh	2026-10-18 09:02:44.003931890 -0400
+++ docs/v2/audit/cmc_v1_1_leaf24/cmc_wrapper_v2_dcfef770.sh	2026-10-18 09:26:14.723931890 -0400
@@ -1,19 +1,70 @@
 #!/bin/bash
-# CMC v1.1 leaf24 top10_100w wrapper (logic of 572ca30f; command verbatim, setsid inserted after env assignment)
-L=/workspace/QuantLab/output/alpha/cmc_v1_1_leaf24_logs; OD=/workspace/QuantLab/output/alpha/cmc_v1_1_leaf24
-mkdir -p $L; MK=$L/start.marker; touch $MK; sleep 1
-MYPG=$(ps -o pgid= -p $$ | tr -d " ")
-c5watch() { while kill -0 $PID 2>/dev/null; do for d in /proc/[0-9]*; do p=${d#/proc/}; [ "$p" = 94322 ] && continue; g=$(ps -o pgid= -p $p 2>/dev/null | tr -d " "); [ -z "$g" ] && continue; [ "$g" = "$PGID" ] && continue; [ "$g" = "$MYPG" ] && continue; c=$(tr "\0" " " < $d/cmdline 2>/dev/null); hit=""; case "$c" in *"/workspace/QuantLab/data"*|*"/workspace/QuantLab/output"*|*"research/"*|*"scripts/"*|*server.py*|*kline.py*|*export_static*|*start_all*|*supervise.sh*) hit="cmd";; esac; if [ -z "$hit" ]; then for fd in $d/fd/*; do t=$(readlink $fd 2>/dev/null); case "$t" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="fd:$t"; break;; esac; done; fi; if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$c" >> $L/cmc_c5.txt; kill -TERM -- -$PGID; sleep 5; if kill -0 -- -$PGID 2>/dev/null; then kill -KILL -- -$PGID; fi; return; fi; done; sleep 0.5; done; }
-ps -eo pid,pgid,ni,rss,etime,args > $L/cmc_ps_before.txt
-cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 setsid env -u QL_X2_EXTEND_END -u ALPHA_V11_RLIMIT_AS_KB nice -n 10 /workspace/qlvenv/bin/python research/alpha_combo_marginal_v1_1.py --universe hiliq --base capadv --arch-ok /workspace/QuantLab/output/alpha/ARCH_RUN_AUTH_CMC_V1_1_FULL_LEAF24.ok --out /workspace/QuantLab/output/alpha/cmc_v1_1_leaf24/CMC_V1_1_LEAF24_imax_intraday_top10_100w_hiliq_capadv.json imax_intraday_top10_100w > $L/cmc.log 2>&1 & PID=$!; PGID=$PID; STOPKB=1484800; TGTKB=1331200; STOPPED=0; AT=0
-[ "$(ps -o pgid= -p $PID | tr -d ' ')" = "$PGID" ] && echo "PGID_OK pid=$PID" >> $L/cmc_sampler.txt || echo "PGID_MISMATCH pid=$PID" >> $L/cmc_sampler.txt
-c5watch & WPID=$!
-while kill -0 $PID 2>/dev/null; do echo "$(date +%H:%M:%S.%N) $(grep -E '^(VmRSS|VmHWM):' /proc/$PID/status 2>/dev/null | tr -s ' \n' ' ')" >> $L/cmc_sampler.txt; H=$(awk '/^VmHWM:/{print $2}' /proc/$PID/status 2>/dev/null)
- S9=$(awk '{print $3}' /proc/94322/stat 2>/dev/null); if [ "$S9" != T ]; then echo "$(date +%H:%M:%S.%N) P94322_STATE=$S9" >> $L/cmc_sampler.txt; STOPPED=2; kill -TERM -- -$PGID; sleep 5; kill -0 -- -$PGID 2>/dev/null && kill -KILL -- -$PGID; break; fi
- if [ -n "$H" ] && [ "$AT" = 0 ] && [ "$H" -gt "$TGTKB" ]; then echo "$(date +%H:%M:%S.%N) ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)" >> $L/cmc_sampler.txt; AT=1; fi
- if [ -n "$H" ] && [ "$H" -gt "$STOPKB" ]; then echo "$(date +%H:%M:%S.%N) STOPLINE hwm_kb=$H stop_kb=$STOPKB" >> $L/cmc_sampler.txt; STOPPED=1; kill -TERM -- -$PGID; sleep 5; if kill -0 -- -$PGID 2>/dev/null; then kill -KILL -- -$PGID; fi; break; fi; sleep 1; done
-rc=0; wait $PID || rc=$?; echo "exit=$rc stopped=$STOPPED" > $L/cmc_exit.txt; ps -eo pid,pgid,ni,rss,etime,args > $L/cmc_ps_after.txt
-if pgrep -g $PGID > /dev/null; then echo "PGID_ALIVE $PGID" >> $L/cmc_exit.txt; else echo "PGREP_G_EMPTY $PGID" >> $L/cmc_exit.txt; fi
-if [ "$rc" -ne 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/cmc_v1_1_leaf24_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"; for f in $(find $OD -type f -newer $MK 2>/dev/null); do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
-wait $WPID 2>/dev/null
-echo "WRAPPER_DONE rc=$rc stopped=$STOPPED"
+# cmc_wrapper_v2: generic memory/concurrency wrapper (successor of f757e7ca; Arch-approved fixes a-d + peak/C5/kill fixes)
+# usage: cmc_wrapper_v2.sh [--selftest] [--guard-pid PID|--no-guard] [--c5-ignore PID (logged; selftest use)] --tag TAG --logdir DIR --outdir DIR [--meta JSON] [--assert STR] [--cwd DIR] -- CMD [ARGS...]
+#   CMD (interpreter + script + args) is a parameter; nothing is bound here. Env assignments go via: env -u X VAR=1 nice -n 10 <interp> ...
+# exit codes: child rc | 96 C5 hit | 97 PGID_MISMATCH | 98 cmdline assert failed | 95 stopline (child TERM/KILL) | 2 usage
+set -u
+GUARDPID=94322; C5IGN=""; STOPKB=1484800; TGTKB=1331200; HARDKB=1536000; DT=0.2; SELFTEST=0; ASSERT=alpha_combo; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""
+while [ $# -gt 0 ]; do case "$1" in
+  --selftest) SELFTEST=1; shift;; --tag) TAG=$2; shift 2;; --logdir) L=$2; shift 2;; --outdir) OD=$2; shift 2;;
+  --meta) META=$2; shift 2;; --guard-pid) GUARDPID=$2; shift 2;; --no-guard) GUARDPID=""; shift;; --c5-ignore) C5IGN=$2; shift 2;; --assert) ASSERT=$2; shift 2;; --cwd) RUNCWD=$2; shift 2;; --) shift; break;; *) echo "usage error: $1" >&2; exit 2;; esac; done
+[ -n "$TAG" ] && [ -n "$L" ] && [ -n "$OD" ] && [ $# -gt 0 ] || { echo "usage: --tag --logdir --outdir -- CMD" >&2; exit 2; }
+mkdir -p "$L"; S="$L/${TAG}_sampler.txt"; X="$L/${TAG}_exit.txt"; C5F="$L/${TAG}_c5.txt"; LOG="$L/${TAG}.log"; MK="$L/${TAG}_start.marker"
+touch "$MK"; sleep 1
+log() { echo "$(date +%H:%M:%S.%N) $*" >> "$S"; }
+killgrp() { # always the whole process group, never just a shell
+  kill -TERM -- "-$PGID" 2>/dev/null; for _ in 1 2 3 4 5 6 7 8 9 10; do pgrep -g "$PGID" >/dev/null || break; sleep 0.5; done
+  pgrep -g "$PGID" >/dev/null && kill -KILL -- "-$PGID" 2>/dev/null; sleep 0.5
+  if pgrep -g "$PGID" >/dev/null; then log "PGID_ALIVE_AFTER_KILL $PGID"; else log "PGREP_G_EMPTY $PGID"; fi; }
+mytree() { # wrapper's own PID tree (self + all descendants), space separated
+  local t=" $$ " n p c; n=1; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case "$t" in *" $c "*) continue;; esac
+    pp=$(awk '{print $4}' "$p/stat" 2>/dev/null); case "$t" in *" $pp "*) t="$t$c "; n=1;; esac; done; done; echo "$t"; }
+c5watch() { while kill -0 "$PID" 2>/dev/null; do T=$(mytree); for d in /proc/[0-9]*; do p=${d#/proc/}
+    case "$T" in *" $p "*) continue;; esac; [ -n "$GUARDPID" ] && [ "$p" = "$GUARDPID" ] && continue; [ -n "$C5IGN" ] && [ "$p" = "$C5IGN" ] && continue
+    g=$(awk '{print $5}' "$d/stat" 2>/dev/null); [ -z "$g" ] && continue; [ "$g" = "$PGID" ] && continue
+    hit=""; cw=$(readlink "$d/cwd" 2>/dev/null)
+    case "$cw" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="cwd:$cw";; esac
+    if [ -z "$hit" ]; then for fd in "$d"/fd/*; do t=$(readlink "$fd" 2>/dev/null); case "$t" in /workspace/QuantLab/data/*|/workspace/QuantLab/output/*) hit="fd:$t"; break;; esac; done; fi
+    if [ -z "$hit" ]; then m=$(grep -m1 -oE '/workspace/QuantLab/(research|scripts)/[^ ]+' "$d/maps" 2>/dev/null); [ -n "$m" ] && hit="map:$m"; fi
+    if [ -z "$hit" ]; then c=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline"); case "$c" in *python*research/*|*python*scripts/*|*/workspace/QuantLab/research/*.py*|*/workspace/QuantLab/scripts/*.py*) hit="cmd";; esac; fi
+    if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline")" >> "$C5F"; killgrp; return; fi
+  done; sleep 0.5; done; }
+ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_before.txt"
+cd "$RUNCWD" || exit 2                                   # (a) cd as its own statement
+setsid "$@" > "$LOG" 2>&1 &                              # (b) only the command is backgrounded; setsid does not fork (we are not a pgrp leader), so $! is the command
+PID=$!; PGID=$PID; STOPPED=0; AT=0; RC_OVR=""
+sleep 0.2
+G=$(awk '{print $5}' /proc/$PID/stat 2>/dev/null)
+if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; [ -n "$G" ] && PGID=$G; killgrp; RC_OVR=97; fi   # (c)
+if [ -z "$RC_OVR" ]; then log "PGID_OK pid=$PID guard=${GUARDPID:-none} c5_ignore=${C5IGN:-none}"
+  if [ "$SELFTEST" = 1 ]; then log "SELFTEST: cmdline assert disabled (cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null))"
+  else ok=0; for _ in $(seq 1 25); do grep -qa -- "$ASSERT" /proc/$PID/cmdline 2>/dev/null && { ok=1; break; }; sleep 0.2; done   # env/nice exec chain settles
+    if [ $ok = 1 ]; then log "CMDLINE_ASSERT_OK '$ASSERT'"; else log "CMDLINE_ASSERT_FAIL '$ASSERT' cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null)"; killgrp; RC_OVR=98; fi; fi; fi
+if [ -z "$RC_OVR" ]; then c5watch & WPID=$!
+  while kill -0 "$PID" 2>/dev/null; do                                  # (d) 0.2 s sampling
+    H=$(awk '/^VmHWM:/{print $2}' /proc/$PID/status 2>/dev/null); R=$(awk '/^VmRSS:/{print $2}' /proc/$PID/status 2>/dev/null)
+    [ -n "$H" ] && log "VmHWM: $H kB VmRSS: $R kB"
+    if [ -n "$GUARDPID" ] && [ -e /proc/$GUARDPID ] && [ "$(awk '{print $3}' /proc/$GUARDPID/stat 2>/dev/null)" != T ]; then log "GUARD_PID_NOT_T pid=$GUARDPID"; STOPPED=2; killgrp; break; fi
+    if [ -n "$H" ] && [ $AT = 0 ] && [ "$H" -gt $TGTKB ]; then log "ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)"; AT=1; fi
+    if [ -n "$H" ] && [ "$H" -gt $STOPKB ]; then log "STOPLINE hwm_kb=$H stop_kb=$STOPKB"; STOPPED=1; killgrp; break; fi
+    sleep $DT; done
+fi
+rc=0; wait "$PID" || rc=$?
+[ -n "${WPID:-}" ] && { wait "$WPID" 2>/dev/null; [ -s "$C5F" ] && RC_OVR=${RC_OVR:-96}; }
+[ "$STOPPED" = 1 ] && RC_OVR=${RC_OVR:-95}
+[ -n "$RC_OVR" ] && rc=$RC_OVR
+ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_after.txt"
+pgrep -g "$PGID" >/dev/null && echo "PGID_ALIVE $PGID" >> "$X" || echo "PGREP_G_EMPTY $PGID" >> "$X"
+# peak = max(sampler, log peak_check hwm_kb, log STOP-line KB, meta peak_rss_mb*1024, meta peak_rss_kb, meta vm_peak_kb)
+P1=$(grep -oE 'VmHWM: [0-9]+' "$S" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
+P2=$(grep -oE 'hwm_kb=[0-9]+' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
+P3=$(grep -oiE 'peak RSS [0-9]+ KB' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
+P4=""; P5=""; P6=""; if [ -n "$META" ] && [ -f "$META" ]; then
+  P4=$(jq -r '.peak_rss_mb // empty | . * 1024 | floor' "$META" 2>/dev/null); P5=$(jq -r '.peak_rss_kb // empty' "$META" 2>/dev/null); P6=$(jq -r '.vm_peak_kb // empty' "$META" 2>/dev/null); fi
+PEAK=0; for v in "${P1:-0}" "${P2:-0}" "${P3:-0}" "${P4:-0}" "${P5:-0}" "${P6:-0}"; do v=${v%.*}; [ "$v" -gt "$PEAK" ] 2>/dev/null && PEAK=$v; done
+[ "$PEAK" -le $HARDKB ] && C4=PASS || C4=FAIL
+{ echo "exit=$rc stopped=$STOPPED"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} meta_vm_peak_kb=${P6:-} C4=$C4"; } >> "$X"
+if [ "$rc" -ne 0 ] && [ "$SELFTEST" = 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/${TAG}_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"
+  find "$OD" -type f -newer "$MK" 2>/dev/null | while read -r f; do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
+echo "WRAPPER_DONE tag=$TAG rc=$rc stopped=$STOPPED peak_kb=$PEAK C4=$C4"
+exit "$rc"
```
