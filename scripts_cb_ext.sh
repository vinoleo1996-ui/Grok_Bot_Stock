while pgrep -f "scripts_cb_etf_pull.py" >/dev/null; do sleep 30; done
START=20150101 python3 scripts_cb_etf_pull2.py > data/v2/cb/raw/pull2015.out 2>&1
echo EXT_DONE >> data/v2/cb/raw/pull2015.out
