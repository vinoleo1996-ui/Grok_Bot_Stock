while ! grep -q EXT_DONE data/v2/cb/raw/pull2015.out 2>/dev/null; do sleep 30; done
python3 scripts_v3_queue.py > data/v2/futures/raw/queue.out 2>&1
