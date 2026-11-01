"""Build wide panels (2017-06..latest) for TRADABLE_IC_V1. Research only, promotion_approved=false."""
import sys, os
from pathlib import Path
import pandas as pd, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, '/workspace/QuantLab')
from quantlab.data.v2_readers import default_v2_roots, load_merged_panel
R = default_v2_roots()
COLS = ['open','close','factor','amount','turnover','is_st_at_open','tradestatus','limit_up','reference_price','volume']
START = pd.Timestamp('2017-06-01')
def one(iid):
    try:
        f = load_merged_panel(iid, d0_root=R.d0_root, asof_extend_dir=R.asof_extend_dir).frame
    except Exception as e:
        return iid, None
    if f is None or f.empty: return iid, None
    et = pd.to_datetime(f['event_time']).dt.normalize()
    f = f.assign(event_time=et)
    f = f[f.event_time >= START].drop_duplicates('event_time', keep='last').set_index('event_time')
    out = {c: pd.to_numeric(f[c], errors='coerce') if c in f.columns else pd.Series(np.nan, index=f.index) for c in COLS}
    return iid, pd.DataFrame(out)
if __name__ == '__main__':
    ids = sorted({p.stem for p in (R.d0_root/'panels').glob('*.parquet')} | {p.stem for p in (R.asof_extend_dir/'panels').glob('*.parquet')})
    ids = [i for i in ids if i[:3] in ('sh.','sz.','bj.')]
    print('n_ids', len(ids), flush=True)
    res = {}
    with ProcessPoolExecutor(6) as ex:
        for iid, df in ex.map(one, ids, chunksize=50):
            if df is not None and len(df): res[iid] = df
    out = Path('/workspace/scratch/tic')
    for c in COLS:
        w = pd.DataFrame({k: v[c] for k, v in res.items()}).sort_index()
        w.to_parquet(out/f'{c}.parquet')
        print(c, w.shape, flush=True)
