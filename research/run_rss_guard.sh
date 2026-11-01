#!/bin/bash
# usage: run_rss_guard.sh <logfile> <cmd...> ; kills job if RSS > 1.5GB (1536000 KB); logs peak RSS
log=$1; shift
"$@" > "$log" 2>&1 &
tp=$!; peak=0
while kill -0 $tp 2>/dev/null; do
  r=$(awk '/VmRSS/{print $2}' /proc/$tp/status 2>/dev/null)
  if [ -n "$r" ]; then [ "$r" -gt "$peak" ] && peak=$r; if [ "$r" -gt 1536000 ]; then echo "RSS_GUARD_KILL rss_kb=$r" >> "$log"; kill $tp; fi; fi
  sleep 1
done
wait $tp; ec=$?; echo "EXIT $ec PEAK_RSS_KB $peak" >> "$log"
