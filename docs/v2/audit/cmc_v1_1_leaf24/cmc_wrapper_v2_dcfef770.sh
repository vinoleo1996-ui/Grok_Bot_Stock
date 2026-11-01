#!/bin/bash
# cmc_wrapper_v2: generic memory/concurrency wrapper (successor of f757e7ca; Arch-approved fixes a-d + peak/C5/kill fixes)
# usage: cmc_wrapper_v2.sh [--selftest] [--guard-pid PID|--no-guard] [--c5-ignore PID (logged; selftest use)] --tag TAG --logdir DIR --outdir DIR [--meta JSON] [--assert STR] [--cwd DIR] -- CMD [ARGS...]
#   CMD (interpreter + script + args) is a parameter; nothing is bound here. Env assignments go via: env -u X VAR=1 nice -n 10 <interp> ...
# exit codes: child rc | 96 C5 hit | 97 PGID_MISMATCH | 98 cmdline assert failed | 95 stopline (child TERM/KILL) | 2 usage
set -u
GUARDPID=94322; C5IGN=""; STOPKB=1484800; TGTKB=1331200; HARDKB=1536000; DT=0.2; SELFTEST=0; ASSERT=alpha_combo; META=""; RUNCWD=/workspace/QuantLab; TAG=""; L=""; OD=""
while [ $# -gt 0 ]; do case "$1" in
  --selftest) SELFTEST=1; shift;; --tag) TAG=$2; shift 2;; --logdir) L=$2; shift 2;; --outdir) OD=$2; shift 2;;
  --meta) META=$2; shift 2;; --guard-pid) GUARDPID=$2; shift 2;; --no-guard) GUARDPID=""; shift;; --c5-ignore) C5IGN=$2; shift 2;; --assert) ASSERT=$2; shift 2;; --cwd) RUNCWD=$2; shift 2;; --) shift; break;; *) echo "usage error: $1" >&2; exit 2;; esac; done
[ -n "$TAG" ] && [ -n "$L" ] && [ -n "$OD" ] && [ $# -gt 0 ] || { echo "usage: --tag --logdir --outdir -- CMD" >&2; exit 2; }
mkdir -p "$L"; S="$L/${TAG}_sampler.txt"; X="$L/${TAG}_exit.txt"; C5F="$L/${TAG}_c5.txt"; LOG="$L/${TAG}.log"; MK="$L/${TAG}_start.marker"
touch "$MK"; sleep 1
log() { echo "$(date +%H:%M:%S.%N) $*" >> "$S"; }
killgrp() { # always the whole process group, never just a shell
  kill -TERM -- "-$PGID" 2>/dev/null; for _ in 1 2 3 4 5 6 7 8 9 10; do pgrep -g "$PGID" >/dev/null || break; sleep 0.5; done
  pgrep -g "$PGID" >/dev/null && kill -KILL -- "-$PGID" 2>/dev/null; sleep 0.5
  if pgrep -g "$PGID" >/dev/null; then log "PGID_ALIVE_AFTER_KILL $PGID"; else log "PGREP_G_EMPTY $PGID"; fi; }
mytree() { # wrapper's own PID tree (self + all descendants), space separated
  local t=" $$ " n p c; n=1; while [ $n = 1 ]; do n=0; for p in /proc/[0-9]*; do c=${p#/proc/}; case "$t" in *" $c "*) continue;; esac
    pp=$(awk '{print $4}' "$p/stat" 2>/dev/null); case "$t" in *" $pp "*) t="$t$c "; n=1;; esac; done; done; echo "$t"; }
c5watch() { while kill -0 "$PID" 2>/dev/null; do T=$(mytree); for d in /proc/[0-9]*; do p=${d#/proc/}
    case "$T" in *" $p "*) continue;; esac; [ -n "$GUARDPID" ] && [ "$p" = "$GUARDPID" ] && continue; [ -n "$C5IGN" ] && [ "$p" = "$C5IGN" ] && continue
    g=$(awk '{print $5}' "$d/stat" 2>/dev/null); [ -z "$g" ] && continue; [ "$g" = "$PGID" ] && continue
    hit=""; cw=$(readlink "$d/cwd" 2>/dev/null)
    case "$cw" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="cwd:$cw";; esac
    if [ -z "$hit" ]; then for fd in "$d"/fd/*; do t=$(readlink "$fd" 2>/dev/null); case "$t" in /workspace/QuantLab/data/*|/workspace/QuantLab/output/*) hit="fd:$t"; break;; esac; done; fi
    if [ -z "$hit" ]; then m=$(grep -m1 -oE '/workspace/QuantLab/(research|scripts)/[^ ]+' "$d/maps" 2>/dev/null); [ -n "$m" ] && hit="map:$m"; fi
    if [ -z "$hit" ]; then c=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline"); case "$c" in *python*research/*|*python*scripts/*|*/workspace/QuantLab/research/*.py*|*/workspace/QuantLab/scripts/*.py*) hit="cmd";; esac; fi
    if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$(tr '\0' ' ' 2>/dev/null < "$d/cmdline")" >> "$C5F"; killgrp; return; fi
  done; sleep 0.5; done; }
ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_before.txt"
cd "$RUNCWD" || exit 2                                   # (a) cd as its own statement
setsid "$@" > "$LOG" 2>&1 &                              # (b) only the command is backgrounded; setsid does not fork (we are not a pgrp leader), so $! is the command
PID=$!; PGID=$PID; STOPPED=0; AT=0; RC_OVR=""
sleep 0.2
G=$(awk '{print $5}' /proc/$PID/stat 2>/dev/null)
if [ "$G" != "$PGID" ]; then log "PGID_MISMATCH pid=$PID pgid=$G"; [ -n "$G" ] && PGID=$G; killgrp; RC_OVR=97; fi   # (c)
if [ -z "$RC_OVR" ]; then log "PGID_OK pid=$PID guard=${GUARDPID:-none} c5_ignore=${C5IGN:-none}"
  if [ "$SELFTEST" = 1 ]; then log "SELFTEST: cmdline assert disabled (cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null))"
  else ok=0; for _ in $(seq 1 25); do grep -qa -- "$ASSERT" /proc/$PID/cmdline 2>/dev/null && { ok=1; break; }; sleep 0.2; done   # env/nice exec chain settles
    if [ $ok = 1 ]; then log "CMDLINE_ASSERT_OK '$ASSERT'"; else log "CMDLINE_ASSERT_FAIL '$ASSERT' cmdline=$(tr '\0' ' ' < /proc/$PID/cmdline 2>/dev/null)"; killgrp; RC_OVR=98; fi; fi; fi
if [ -z "$RC_OVR" ]; then c5watch & WPID=$!
  while kill -0 "$PID" 2>/dev/null; do                                  # (d) 0.2 s sampling
    H=$(awk '/^VmHWM:/{print $2}' /proc/$PID/status 2>/dev/null); R=$(awk '/^VmRSS:/{print $2}' /proc/$PID/status 2>/dev/null)
    [ -n "$H" ] && log "VmHWM: $H kB VmRSS: $R kB"
    if [ -n "$GUARDPID" ] && [ -e /proc/$GUARDPID ] && [ "$(awk '{print $3}' /proc/$GUARDPID/stat 2>/dev/null)" != T ]; then log "GUARD_PID_NOT_T pid=$GUARDPID"; STOPPED=2; killgrp; break; fi
    if [ -n "$H" ] && [ $AT = 0 ] && [ "$H" -gt $TGTKB ]; then log "ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)"; AT=1; fi
    if [ -n "$H" ] && [ "$H" -gt $STOPKB ]; then log "STOPLINE hwm_kb=$H stop_kb=$STOPKB"; STOPPED=1; killgrp; break; fi
    sleep $DT; done
fi
rc=0; wait "$PID" || rc=$?
[ -n "${WPID:-}" ] && { wait "$WPID" 2>/dev/null; [ -s "$C5F" ] && RC_OVR=${RC_OVR:-96}; }
[ "$STOPPED" = 1 ] && RC_OVR=${RC_OVR:-95}
[ -n "$RC_OVR" ] && rc=$RC_OVR
ps -eo pid,pgid,ni,rss,etime,args > "$L/${TAG}_ps_after.txt"
pgrep -g "$PGID" >/dev/null && echo "PGID_ALIVE $PGID" >> "$X" || echo "PGREP_G_EMPTY $PGID" >> "$X"
# peak = max(sampler, log peak_check hwm_kb, log STOP-line KB, meta peak_rss_mb*1024, meta peak_rss_kb, meta vm_peak_kb)
P1=$(grep -oE 'VmHWM: [0-9]+' "$S" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
P2=$(grep -oE 'hwm_kb=[0-9]+' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
P3=$(grep -oiE 'peak RSS [0-9]+ KB' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1)
P4=""; P5=""; P6=""; if [ -n "$META" ] && [ -f "$META" ]; then
  P4=$(jq -r '.peak_rss_mb // empty | . * 1024 | floor' "$META" 2>/dev/null); P5=$(jq -r '.peak_rss_kb // empty' "$META" 2>/dev/null); P6=$(jq -r '.vm_peak_kb // empty' "$META" 2>/dev/null); fi
PEAK=0; for v in "${P1:-0}" "${P2:-0}" "${P3:-0}" "${P4:-0}" "${P5:-0}" "${P6:-0}"; do v=${v%.*}; [ "$v" -gt "$PEAK" ] 2>/dev/null && PEAK=$v; done
[ "$PEAK" -le $HARDKB ] && C4=PASS || C4=FAIL
{ echo "exit=$rc stopped=$STOPPED"; echo "peak_kb=$PEAK sampler=${P1:-} log_hwm=${P2:-} log_stop=${P3:-} meta_mb_x1024=${P4:-} meta_peak_rss_kb=${P5:-} meta_vm_peak_kb=${P6:-} C4=$C4"; } >> "$X"
if [ "$rc" -ne 0 ] && [ "$SELFTEST" = 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/${TAG}_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"
  find "$OD" -type f -newer "$MK" 2>/dev/null | while read -r f; do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
echo "WRAPPER_DONE tag=$TAG rc=$rc stopped=$STOPPED peak_kb=$PEAK C4=$C4"
exit "$rc"
