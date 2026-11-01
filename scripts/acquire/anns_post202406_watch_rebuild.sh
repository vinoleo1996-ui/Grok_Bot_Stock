#!/bin/bash
# Watch EM/CN post-202406 pulls; rebuild embedding corpus at milestones; exit when both pulls done + final rebuild.
set -e
cd /workspace/QuantLab
LOG=logs/anns_post202406_watch.log
exec >>"$LOG" 2>&1
echo "WATCH_START $(date -Iseconds)"
last_rebuild=0
final_done=0
while true; do
  em=$(ls data/v2/announcements/eastmoney/by_stock_post202406/*.parquet 2>/dev/null | wc -l)
  cn=$(ls data/v2/announcements/cninfo/by_stock_post202406/*.parquet 2>/dev/null | wc -l)
  em_alive=$(pgrep -f 'anns_post202406_pull.py' | wc -l)
  mem=$(awk '/MemAvailable/{printf "%.1f",$2/1024/1024}' /proc/meminfo)
  echo "$(date +%H:%M:%S) em=$em cn=$cn procs=$em_alive mem=${mem}G last_rebuild=$last_rebuild"
  # rebuild when EM crosses 200/600/1200/2000 or pulls finished
  do=0
  if [ "$em" -ge 200 ] && [ "$last_rebuild" -lt 200 ]; then do=1; last_rebuild=200; fi
  if [ "$em" -ge 600 ] && [ "$last_rebuild" -lt 600 ]; then do=1; last_rebuild=600; fi
  if [ "$em" -ge 1200 ] && [ "$last_rebuild" -lt 1200 ]; then do=1; last_rebuild=1200; fi
  if [ "$em" -ge 2000 ] && [ "$last_rebuild" -lt 2000 ]; then do=1; last_rebuild=2000; fi
  if [ "$em_alive" -eq 0 ] && [ "$em" -ge 50 ] && [ "$final_done" -eq 0 ]; then do=1; final_done=1; last_rebuild=9999; fi
  if [ "$do" -eq 1 ]; then
    echo "REBUILD at em=$em cn=$cn"
    python3 -u scripts/acquire/ann_embed_extend_post202406.py --force || echo "REBUILD_FAIL $?"
    # mark first delivery flag for parent
    if [ ! -f output/d1/ann_embed_post202406_first_delivery.flag ]; then
      date -Iseconds > output/d1/ann_embed_post202406_first_delivery.flag
      echo "FIRST_DELIVERY_FLAG"
    fi
  fi
  if [ "$final_done" -eq 1 ]; then
    echo "WATCH_DONE $(date -Iseconds)"
    exit 0
  fi
  sleep 45
done
