#!/bin/bash
# CMC v1.1 leaf24 top10_100w wrapper (logic of 572ca30f; command verbatim, setsid inserted after env assignment)
L=/workspace/QuantLab/output/alpha/cmc_v1_1_leaf24_logs; OD=/workspace/QuantLab/output/alpha/cmc_v1_1_leaf24
mkdir -p $L; MK=$L/start.marker; touch $MK; sleep 1
MYPG=$(ps -o pgid= -p $$ | tr -d " ")
c5watch() { while kill -0 $PID 2>/dev/null; do for d in /proc/[0-9]*; do p=${d#/proc/}; [ "$p" = 94322 ] && continue; g=$(ps -o pgid= -p $p 2>/dev/null | tr -d " "); [ -z "$g" ] && continue; [ "$g" = "$PGID" ] && continue; [ "$g" = "$MYPG" ] && continue; c=$(tr "\0" " " < $d/cmdline 2>/dev/null); hit=""; case "$c" in *"/workspace/QuantLab/data"*|*"/workspace/QuantLab/output"*|*"research/"*|*"scripts/"*|*server.py*|*kline.py*|*export_static*|*start_all*|*supervise.sh*) hit="cmd";; esac; if [ -z "$hit" ]; then for fd in $d/fd/*; do t=$(readlink $fd 2>/dev/null); case "$t" in /workspace/QuantLab/data*|/workspace/QuantLab/output*) hit="fd:$t"; break;; esac; done; fi; if [ -n "$hit" ]; then echo "$(date +%H:%M:%S.%N) C5_HIT pid=$p pgid=$g $hit cmd=$c" >> $L/cmc_c5.txt; kill -TERM -- -$PGID; sleep 5; if kill -0 -- -$PGID 2>/dev/null; then kill -KILL -- -$PGID; fi; return; fi; done; sleep 0.5; done; }
ps -eo pid,pgid,ni,rss,etime,args > $L/cmc_ps_before.txt
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 setsid env -u QL_X2_EXTEND_END -u ALPHA_V11_RLIMIT_AS_KB nice -n 10 /workspace/qlvenv/bin/python research/alpha_combo_marginal_v1_1.py --universe hiliq --base capadv --arch-ok /workspace/QuantLab/output/alpha/ARCH_RUN_AUTH_CMC_V1_1_FULL_LEAF24.ok --out /workspace/QuantLab/output/alpha/cmc_v1_1_leaf24/CMC_V1_1_LEAF24_imax_intraday_top10_100w_hiliq_capadv.json imax_intraday_top10_100w > $L/cmc.log 2>&1 & PID=$!; PGID=$PID; STOPKB=1484800; TGTKB=1331200; STOPPED=0; AT=0
[ "$(ps -o pgid= -p $PID | tr -d ' ')" = "$PGID" ] && echo "PGID_OK pid=$PID" >> $L/cmc_sampler.txt || echo "PGID_MISMATCH pid=$PID" >> $L/cmc_sampler.txt
c5watch & WPID=$!
while kill -0 $PID 2>/dev/null; do echo "$(date +%H:%M:%S.%N) $(grep -E '^(VmRSS|VmHWM):' /proc/$PID/status 2>/dev/null | tr -s ' \n' ' ')" >> $L/cmc_sampler.txt; H=$(awk '/^VmHWM:/{print $2}' /proc/$PID/status 2>/dev/null)
 S9=$(awk '{print $3}' /proc/94322/stat 2>/dev/null); if [ "$S9" != T ]; then echo "$(date +%H:%M:%S.%N) P94322_STATE=$S9" >> $L/cmc_sampler.txt; STOPPED=2; kill -TERM -- -$PGID; sleep 5; kill -0 -- -$PGID 2>/dev/null && kill -KILL -- -$PGID; break; fi
 if [ -n "$H" ] && [ "$AT" = 0 ] && [ "$H" -gt "$TGTKB" ]; then echo "$(date +%H:%M:%S.%N) ABOVE_TARGET hwm_kb=$H target_kb=$TGTKB (report only)" >> $L/cmc_sampler.txt; AT=1; fi
 if [ -n "$H" ] && [ "$H" -gt "$STOPKB" ]; then echo "$(date +%H:%M:%S.%N) STOPLINE hwm_kb=$H stop_kb=$STOPKB" >> $L/cmc_sampler.txt; STOPPED=1; kill -TERM -- -$PGID; sleep 5; if kill -0 -- -$PGID 2>/dev/null; then kill -KILL -- -$PGID; fi; break; fi; sleep 1; done
rc=0; wait $PID || rc=$?; echo "exit=$rc stopped=$STOPPED" > $L/cmc_exit.txt; ps -eo pid,pgid,ni,rss,etime,args > $L/cmc_ps_after.txt
if pgrep -g $PGID > /dev/null; then echo "PGID_ALIVE $PGID" >> $L/cmc_exit.txt; else echo "PGREP_G_EMPTY $PGID" >> $L/cmc_exit.txt; fi
if [ "$rc" -ne 0 ]; then V=/workspace/QuantLab/output/ai_factory/_void/cmc_v1_1_leaf24_rc${rc}_$(date +%Y%m%d_%H%M%S); mkdir -p "$V"; for f in $(find $OD -type f -newer $MK 2>/dev/null); do sha256sum "$f" >> "$V/SHA_MTIME.before"; stat -c '%y %n' "$f" >> "$V/SHA_MTIME.before"; mv "$f" "$V/"; done; fi
wait $WPID 2>/dev/null
echo "WRAPPER_DONE rc=$rc stopped=$STOPPED"
