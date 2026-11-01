"""Arch K6 历史披露：v0/v1.1/v1.2（及 v1.3 作废版参考）归档权重的行业偏离，全池 wb 口径 vs 旧支撑集口径。
只读：不改代码、不算收益。按调仓日逐日 prepare_day（与求解器同源的 pool/industry/wb），单进程。
"""
import sys, gc, pickle, resource, json
sys.path.insert(0, '/workspace/QuantLab/research')
import pandas as pd, numpy as np
import optimizer_lambda_calib_sealed as C
OUT = '/workspace/QuantLab/output/strategy_optimizer/core_x2/'
AUD = '/workspace/QuantLab/docs/v2/audit/'
VERS = {'v0': OUT+'_archive_v0/', 'v1_1': OUT+'_archive_v1_1/', 'v1_2': OUT+'_archive_v1_2/', 'v1_3_void': OUT+'_archive_v1_3_pre_ruling/'}
SLV = ['equity_100', 'equity80_etf20_510300']; AUMS = {600000: '60w', 1000000: '100w'}
# per-version status / ind_slack
meta = {}
for v in ['v1_1', 'v1_2']:
    d = pd.read_csv(VERS[v]+f'core_{v}_disclosure.csv')
    for r in d.itertuples(): meta[(v, r.date, r.aum, r.sleeve)] = (r.status, r.ind_slack)
d = pd.read_csv(VERS['v1_3_void']+'core_v1_3_disclosure.csv')
for r in d.itertuples(): meta[('v1_3_void', r.date, r.aum, r.sleeve)] = (r.status, r.ind_slack)
import glob, os
for p in sorted(glob.glob(OUT+'_archive_v0/_ckpt_v0/*.pkl')):
    lg = pickle.load(open(p, 'rb')).get('log', {})
    day = lg.get('day')
    if day is None: continue
    for a in AUMS:
        for s in SLV: meta[('v0', day, a, s)] = (lg.get(f'status_{a}', 'NA'), np.nan)
W = {}
for v, base in VERS.items():
    for s in SLV:
        for a, t in AUMS.items():
            w = pd.read_parquet(base+f'core_{s}_{t}.parquet', columns=['session', 'instrument', 'weight', 'is_rebalance_day'])
            w = w[w.is_rebalance_day]; w['session'] = pd.to_datetime(w['session']).dt.strftime('%Y-%m-%d')
            W[(v, a, s)] = {k: g.set_index('instrument').weight for k, g in w.groupby('session')}
days = sorted({d for x in W.values() for d in x})
rows = []
for day in days:
    D = C.prepare_day(pd.Timestamp(day))
    if D is None:
        print(day, 'NO_D', flush=True); continue
    cols = list(D['alpha'].index); ind = pd.Series({c: D['industry'].get(c, '_UNK') for c in cols})
    wb = D['wb'].reindex(cols).fillna(0.0); wb = wb / wb.sum()
    gb = wb.groupby(ind).sum()
    for (v, a, s), byday in W.items():
        if day not in byday: continue
        w = byday[day]; we = w.drop(C.BALLAST, errors='ignore'); we = we[we > 0]
        eqs = float(we.sum())
        if eqs <= 0: continue
        budget = 1.0 - (C.ETF_BALLAST_FRAC if s != 'equity_100' else 0.0)
        wind = pd.Series({i: D['industry'].get(i, '_UNK') for i in we.index})
        pi = we.groupby(wind).sum() / eqs                         # 股票簿内行业占比
        allind = pi.index.union(gb.index)
        act = pi.reindex(allind).fillna(0) - gb.reindex(allind).fillna(0)      # 全池 wb 口径
        wbs = wb.reindex(we.index).fillna(0.0)                                 # 旧口径：入选股 wb，不重归一（求解器同）
        gs = wbs.groupby(wind).sum()
        act_old = pi - gs.reindex(pi.index).fillna(0)
        gs2 = gs / max(float(gs.sum()), 1e-12)                                 # 旧口径变体：入选股 wb 重归一到 1
        act_old2 = pi - gs2.reindex(pi.index).fillna(0); jo2 = act_old2.abs().idxmax()
        j = act.abs().idxmax(); jo = act_old.abs().idxmax()
        st, sl = meta.get((v, day, a, s), ('NA', np.nan))
        rows.append(dict(version=v, date=day, window=('X2' if day >= '2024-06-03' else 'SEALED'), aum=a, sleeve=s, status=st,
                         ind_slack=sl, n_names=len(we), eq_sum=eqs, n_notpool=int((~we.index.isin(cols)).sum()),
                         act_full_max=float(act.abs().max()), act_full_signed=float(act[j]), act_full_ind=j,
                         abs_eq_max=float(pi.max()), abs_eq_ind=pi.idxmax(), abs_nav_max=float((we.groupby(wind).sum()).max()),
                         abs_budget_max=float(pi.max()*eqs/budget),
                         act_old_max=float(act_old.abs().max()), act_old_signed=float(act_old[jo]), act_old_ind=jo,
                         act_old2_max=float(act_old2.abs().max()), act_old2_signed=float(act_old2[jo2]), act_old2_ind=jo2,
                         wb_support_sum=float(wbs.sum())))
    del D; gc.collect()
    print(day, 'rss_mb', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, flush=True)
pd.DataFrame(rows).to_csv(AUD+'arch_k6_industry_fullpool_rows.csv', index=False)
print('DONE peak_rss_mb', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)
