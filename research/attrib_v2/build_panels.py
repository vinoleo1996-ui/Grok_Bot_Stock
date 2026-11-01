"""Build lean float32 wide panels for attribution research (research-grade, promotion_approved=false).
Returns: D0 part uses close*factor ratio; extend part uses tushare adj_factor ratio; seam day raw ratio.
|r|>0.35 nulled (relist/IPO artefacts)."""
import glob, os, sys, json
import numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, '/workspace/QuantLab')
from quantlab.data.v2_readers import load_merged_panel
OUT = '/workspace/QuantLab/output/research_attrib_v2/panels'
LO, HI = pd.Timestamp('2023-01-01'), pd.Timestamp('2026-10-09')
CUT = pd.Timestamp('2026-06-30')
etf = pd.read_parquet('data/v2/etf_510300/panels/sh.510300.parquet')
etf['et'] = pd.to_datetime(etf.event_time).dt.tz_localize(None).dt.normalize()
etf = etf[(etf.et >= LO) & (etf.et <= HI)].drop_duplicates('et').set_index('et')
CAL = etf.index
# tushare adj factor for extension
af = pd.concat([pd.read_parquet(f, columns=['ts_code','trade_date','adj_factor']) for f in sorted(glob.glob('data/v2/tushare_raw/adj_factor/*.parquet'))])
def ts2iid(t):
    c, ex = t.split('.'); return {'SH':'sh','SZ':'sz','BJ':'bj'}[ex] + '.' + c
af['iid'] = af.ts_code.map(ts2iid); af['d'] = pd.to_datetime(af.trade_date)
AF = af.pivot_table(index='d', columns='iid', values='adj_factor').reindex(CAL)
del af
FIELDS = ['close','ret','amount','turnover','trad','lu','ld','st']
def one(iid):
    try:
        f = load_merged_panel(iid).frame
    except Exception:
        return iid, None
    if f is None or f.empty or 'close' not in f: return iid, None
    f = f.copy(); f['et'] = pd.to_datetime(f.event_time).dt.normalize()
    f = f[(f.et >= LO) & (f.et <= HI)].drop_duplicates('et', keep='last').set_index('et')
    if len(f) < 20: return iid, None
    c = pd.to_numeric(f.close, errors='coerce')
    fac = pd.to_numeric(f.get('factor'), errors='coerce') if 'factor' in f else pd.Series(np.nan, index=f.index)
    raw = c / c.shift(1)
    d0adj = (c * fac) / (c * fac).shift(1)
    if iid in AF.columns:
        a = AF[iid].reindex(f.index); exadj = raw * (a / a.shift(1))
    else:
        exadj = raw
    r = pd.Series(np.where(f.index <= CUT, d0adj.fillna(raw), exadj.fillna(raw)), index=f.index) - 1
    r[(r.abs() > 0.35)] = np.nan
    lu = pd.to_numeric(f.get('limit_up'), errors='coerce') if 'limit_up' in f else None
    ld = pd.to_numeric(f.get('limit_down'), errors='coerce') if 'limit_down' in f else None
    o = {'close': c, 'ret': r,
         'amount': pd.to_numeric(f.get('amount'), errors='coerce'),
         'turnover': pd.to_numeric(f.get('turnover'), errors='coerce'),
         'trad': pd.to_numeric(f.get('tradestatus'), errors='coerce'),
         'lu': (c >= lu - 1e-6).astype(float) if lu is not None else pd.Series(0.0, index=f.index),
         'ld': (c <= ld + 1e-6).astype(float) if ld is not None else pd.Series(0.0, index=f.index),
         'st': f['is_st_at_open'].astype(float) if 'is_st_at_open' in f else pd.Series(0.0, index=f.index)}
    return iid, {k: v.reindex(CAL).to_numpy(np.float32) for k, v in o.items()}
if __name__ == '__main__':
    ids = sorted({os.path.basename(p)[:-8] for p in glob.glob('data/local_market/1c85fd9aceaa03c3c4863bec/panels/*.parquet')} |
                 {os.path.basename(p)[:-8] for p in glob.glob('data/v2/asof_extend_tushare_202610/panels/*.parquet')})
    ids = [i for i in ids if i[:2] in ('sh','sz','bj') and i[3] in '036' or i.startswith('bj.')]
    print('n ids', len(ids), flush=True)
    store = {k: {} for k in FIELDS}
    with Pool(4, maxtasksperchild=300) as p:
        for n, (iid, d) in enumerate(p.imap_unordered(one, ids, chunksize=20)):
            if d:
                for k in FIELDS: store[k][iid] = d[k]
            if n % 1000 == 0: print(n, flush=True)
    for k in FIELDS:
        pd.DataFrame(store[k], index=CAL).astype(np.float32).to_parquet(f'{OUT}/{k}.parquet')
    e = etf.close * etf.factor.fillna(1.0)
    pd.DataFrame({'close': etf.close, 'ret': (e / e.shift(1) - 1)}).to_parquet(f'{OUT}/etf510300.parquet')
    # daily_basic: circ_mv, total_mv, pe_ttm, pb, turnover_rate
    fs = [f for f in sorted(glob.glob('data/v2/tushare_raw/daily_basic/*.parquet')) if '20230101' <= os.path.basename(f)[:8] <= '20261009']
    db = pd.concat([pd.read_parquet(f, columns=['ts_code','trade_date','circ_mv','total_mv','pe_ttm','pb','turnover_rate']) for f in fs])
    db['iid'] = db.ts_code.map(ts2iid); db['d'] = pd.to_datetime(db.trade_date)
    for k in ['circ_mv','total_mv','pe_ttm','pb','turnover_rate']:
        db.pivot_table(index='d', columns='iid', values=k).reindex(CAL).astype(np.float32).to_parquet(f'{OUT}/db_{k}.parquet')
    print('done', flush=True)
