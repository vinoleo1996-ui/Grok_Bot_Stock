#!/bin/bash
# Chain: wait hk_hold -> rebuild -> hsgt_top10 (polite) -> rebuild
set -e
cd /workspace/QuantLab
LOG=logs/event_nb_chain.log
prog() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

# Wait for hk_hold PID if still running
HK_PID=$(pgrep -f 'fill_nb_margin_gaps.py hk_hold' || true)
if [ -n "$HK_PID" ]; then
  prog "waiting hk_hold pid=$HK_PID"
  while kill -0 "$HK_PID" 2>/dev/null; do sleep 30; done
  prog "hk_hold finished"
else
  prog "hk_hold not running; proceed"
fi

prog "rebuild northbound after hk_hold"
python3 -u scripts/acquire/fill_nb_margin_gaps.py rebuild >> logs/event_nb_rebuild.log 2>&1
prog "rebuild done"

# polite top10 — longer sleep to yield to anns
prog "start hsgt_top10 TOP10_SLEEP=4"
env TOP10_SLEEP=4.0 WORKERS=1 python3 -u scripts/acquire/fill_nb_margin_gaps.py hsgt_top10 \
  >> logs/event_hsgt_top10_fill_stdout.log 2>&1
prog "hsgt_top10 finished exit=$?"

prog "final rebuild"
python3 -u scripts/acquire/fill_nb_margin_gaps.py rebuild >> logs/event_nb_rebuild.log 2>&1

# write final receipt
python3 << 'PY'
import json, pandas as pd
from pathlib import Path
V = Path('/workspace/QuantLab/data/v2')
out = {}
for name, path in [
    ('hk_hold_ashare', V/'northbound/hk_hold_ashare_daily_2018plus.parquet'),
    ('hsgt_top10', V/'northbound/hsgt_top10_daily_2018plus.parquet'),
    ('margin_detail', V/'margin/margin_detail_daily_2018plus.parquet'),
]:
    if not path.exists():
        out[name] = {'missing': True}; continue
    df = pd.read_parquet(path, columns=['trade_date'] if 'trade_date' in pd.read_parquet(path).columns else None)
    # re-read for cols safely
    df = pd.read_parquet(path)
    dcol = 'trade_date'
    out[name] = {
        'path': str(path),
        'rows': int(len(df)),
        'date_min': str(df[dcol].min()),
        'date_max': str(df[dcol].max()),
        'days': int(df[dcol].nunique()),
        'cols': list(df.columns),
    }
    if 'available_at' in df.columns:
        out[name]['available_at_min'] = str(df['available_at'].min())
        out[name]['available_at_max'] = str(df['available_at'].max())
    if 'available_at_rule' in df.columns:
        out[name]['available_at_rule'] = str(df['available_at_rule'].iloc[0])
json.dump(out, open('/workspace/QuantLab/output/d1/nb_margin_fill_receipt.json','w'),
          ensure_ascii=False, indent=2, default=str)
print(json.dumps(out, ensure_ascii=False, indent=2, default=str)[:3000])
PY
prog "ALL DONE receipt=output/d1/nb_margin_fill_receipt.json"
