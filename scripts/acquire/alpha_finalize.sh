#!/bin/bash
# waits for alpha pulls, then share_float fix, rebuild tables + docs
cd /workspace/QuantLab
while pgrep -f "alpha_pull.py share_float$" >/dev/null; do sleep 30; done
python3 scripts/acquire/alpha_pull.py share_float_fix > logs/alpha_share_float_fix.log 2>&1
python3 scripts/acquire/alpha_build.py > logs/alpha_build.log 2>&1
while pgrep -f "alpha_pull.py (limit_hist|toplist)" >/dev/null; do sleep 60; done
python3 scripts/acquire/alpha_build.py > logs/alpha_build.log 2>&1
python3 scripts/acquire/alpha_limit_doc.py >> logs/alpha_build.log 2>&1
echo FINALIZED $(TZ=America/New_York date) >> logs/alpha_build.log
