while ! grep -q DONE data/v2/tushare_raw/adj_factor_hist.out; do sleep 60; done
while pgrep -f "factor_jump_count.py before" >/dev/null; do sleep 30; done
python3 scripts_factor_rebuild.py > output/d1/factor_rebuild.out 2>&1 && python3 scripts_factor_jump_count.py after > output/d1/factor_jumps_after.out 2>&1
echo CHAIN_DONE >> output/d1/factor_rebuild.out
