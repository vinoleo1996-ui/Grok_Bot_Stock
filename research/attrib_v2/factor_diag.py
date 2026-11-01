"""Full-D1-proxy factor diagnostics: rank IC/ICIR (raw vs size+industry neutral) and decile long-only after costs."""
import sys, json, resource
sys.path.insert(0, '/workspace/QuantLab/research/attrib_v2')
import numpy as np, pandas as pd
from common import *
D = load(); F = features(D); RB = rebal_dates()
logc = np.log(D['close']); r = D['ret']
fac = {
 'M01_12_1': logc.shift(21) - logc.shift(252),
 'M02_3_1': logc.shift(21) - logc.shift(63),
 'V01_EP': 1.0 / D['pe_ttm'],
 'V02_BP': 1.0 / D['pb'],
 'R01_5D': -(logc - logc.shift(5)),
 'R02_20D': -(logc - logc.shift(20)),
 'L01_RV60': -r.rolling(60, min_periods=40).std(),
 'turn_20d': -D['turnover_rate'].rolling(20, min_periods=10).mean(),
 'LIQ02_AMIHUD': (r.abs() / D['amount']).rolling(20, min_periods=10).mean() * 1e9,
 'SIZE_small': -np.log(F['cap20']),
}
# EP: loss-makers (pe_ttm NaN in tushare) -> treat as lowest EP (0 - tiny) rather than drop
fac['V01_EP'] = fac['V01_EP'].where(D['pe_ttm'].notna() | D['circ_mv'].isna(), -1e-3)
# forward returns between rebalances
rb = RB + [END]
cum = (1 + r.fillna(0)).cumprod()
fwd = {RB[i]: cum.loc[rb[i + 1]] / cum.loc[RB[i]] - 1 for i in range(len(RB) - 1)}
def neutral(x, d, u):
    z = x.rank(pct=True) - 0.5
    lc = np.log(F['cap20'].loc[d, u]); ind = industry_on(d, u).fillna('NA')
    df = pd.DataFrame({'z': z, 'lc': lc}).dropna()
    Xd = pd.get_dummies(ind.reindex(df.index), dtype=float)
    X = np.column_stack([df.lc.to_numpy() - df.lc.mean(), Xd.to_numpy()])
    beta, *_ = np.linalg.lstsq(X, df.z.to_numpy(), rcond=None)
    return pd.Series(df.z.to_numpy() - X @ beta, index=df.index)
res = {}; tops = {}
for name, f in fac.items():
    for mode in ['raw', 'neutral']:
        ics, ttop, tbot = [], {}, {}
        for d in RB:
            u = universe_d1(d, D, F); x = f.loc[d, u].replace([np.inf, -np.inf], np.nan).dropna()
            if len(x) < 200: continue
            if mode == 'neutral':
                x = neutral(x, d, x.index)
            if d in fwd:
                y = fwd[d].reindex(x.index); ok = y.notna()
                ics.append(x[ok].rank().corr(y[ok].rank()))
            q = x.rank(pct=True, method='first')
            t = q[q > 0.9].index; bt = q[q <= 0.1].index
            ttop[d] = pd.Series(1 / len(t), index=t); tbot[d] = pd.Series(1 / len(bt), index=bt)
        ics = np.array(ics)
        navt, ct, tt = simulate(ttop, D); navb, cb, tb_ = simulate(tbot, D)
        mt, mb = metrics(navt, ct, tt), metrics(navb, cb, tb_)
        key = f'{name}|{mode}'
        res[key] = {'mean_rank_ic': float(ics.mean()), 'ic_std': float(ics.std(ddof=1)), 'icir_per_period': float(ics.mean() / ics.std(ddof=1)),
                    'icir_annualized': float(ics.mean() / ics.std(ddof=1) * np.sqrt(25.2)), 't_stat': float(ics.mean() / ics.std(ddof=1) * np.sqrt(len(ics))),
                    'ic_pos_frac': float((ics > 0).mean()), 'n_periods': int(len(ics)),
                    'top_decile_after_cost': mt, 'bottom_decile_after_cost': mb,
                    'top_minus_bottom_cagr': mt['cagr'] - mb['cagr']}
        print(key, round(ics.mean(), 4), round(res[key]['t_stat'], 2), 'top', round(mt['cagr'], 4), 'bot', round(mb['cagr'], 4), flush=True)
json.dump({'promotion_approved': False, 'research_only': True, 'universe': 'Full-D1 proxy (listed>=120, !ST, trading, 20d median amount>=3e7, drop bottom 30% float cap)',
           'fwd_horizon': 'rebalance-to-rebalance (~10 sessions), 57 grid dates', 'neutral': 'pct-rank residual on log float cap + SW L1 dummies (OLS)',
           'EP_source': 'tushare daily_basic 1/pe_ttm (loss-makers=-0.001), NOT the V2 ep_research_asof', 'factors': res,
           'peak_rss_gb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6}, open(f'{OUT}/factor_diag.json', 'w'), indent=1)
