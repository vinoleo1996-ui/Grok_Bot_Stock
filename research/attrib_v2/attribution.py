"""Return attribution of Full D1 arm A (M01+EP, costs+βc+LW) from logged daily weights (research only)."""
import sys, json
sys.path.insert(0, '/workspace/QuantLab/research/attrib_v2')
import numpy as np, pandas as pd
from common import *
D = load(); F = features(D); RB = rebal_dates()
A = pd.read_csv('/workspace/QuantLab/output/strategy_paper_costs/full_d1_turn/arm_a_baseline_m01_ep/nav.csv', parse_dates=['date']).set_index('date')
L = pd.read_csv('/workspace/QuantLab/output/strategy_paper_costs/full_d1_turn/arm_a_baseline_m01_ep/costs_ledger.csv', parse_dates=['session']).set_index('session')
cost_ret = (L.cost_drag_unit_nav / L.nav_unit_before).reindex(A.index).fillna(0.0)
retm = D['ret'].loc[START:END]; r_etf = D['etf'].reindex(A.index).fillna(0.0)
# daily style factor returns, membership fixed at each rebal date (EW, daily)
def ls_series(sel_fn):
    out = pd.Series(0.0, index=retm.index); rb = RB + [END + pd.Timedelta(days=1)]
    for i in range(len(RB)):
        lo, hi = sel_fn(RB[i]); per = retm.loc[(retm.index > RB[i]) & (retm.index <= rb[i + 1])]
        out.loc[per.index] = per[lo].mean(1).fillna(0) - per[hi].mean(1).fillna(0)
    return out
def ew_series(sel_fn):
    out = pd.Series(0.0, index=retm.index); rb = RB + [END + pd.Timedelta(days=1)]
    for i in range(len(RB)):
        u = sel_fn(RB[i]); per = retm.loc[(retm.index > RB[i]) & (retm.index <= rb[i + 1])]
        out.loc[per.index] = per[u].mean(1).fillna(0)
    return out
logc = np.log(D['close'])
mom = (logc.shift(21) - logc.shift(252))
ep = 1.0 / D['pe_ttm']
def smb(d):
    el = universe_broad(d, D, F); rk = F['cap20'].loc[d, el].rank(pct=True)
    return rk[rk <= 0.3].index, rk[rk > 0.7].index
def tb(fac):
    def f(d):
        u = universe_d1(d, D, F); rk = fac.loc[d, u].rank(pct=True).dropna()
        return rk[rk > 0.7].index, rk[rk <= 0.3].index
    return f
FAC = pd.DataFrame({'MKT_510300': r_etf, 'SMB_broad': ls_series(smb), 'HML_EP': ls_series(tb(ep)), 'UMD_M01': ls_series(tb(mom))}).reindex(A.index).fillna(0)
EWD1 = ew_series(lambda d: universe_d1(d, D, F)).reindex(A.index).fillna(0)
# decomposition
w_etf, w_book, w_cash = A.etf_w, A.residual_book_w, A.cash_w
etf_c = w_etf * r_etf
book_c = A.daily_ret + cost_ret - etf_c          # stock book contribution (pre-cost)
m = w_book > 0.01
b = (book_c[m] / w_book[m])                      # per-unit book return
X = np.column_stack([np.ones(m.sum()), FAC[m].to_numpy()])
coef, *_ = np.linalg.lstsq(X, b.to_numpy(), rcond=None)
resid = b.to_numpy() - X @ coef
names = ['alpha_daily'] + list(FAC.columns)
tstats = coef / (np.sqrt(np.sum(resid ** 2) / (len(b) - X.shape[1]) * np.diag(np.linalg.inv(X.T @ X))))
yrs = len(A) / 252.0
contrib = {}
contrib['ETF_510300_sleeve'] = etf_c.sum()
for j, n in enumerate(FAC.columns, start=1):
    contrib[f'book_{n}_exposure'] = (w_book[m] * coef[j] * FAC.loc[m, n]).sum()
contrib['book_selection_alpha+resid'] = (w_book[m] * (coef[0] + resid)).sum()
contrib['book_unexplained_lowweight_days'] = book_c[~m].sum()
contrib['costs'] = -cost_ret.sum()
contrib['cash_direct'] = 0.0
total_arith = A.daily_ret.sum()
opp_cash_vs_510300 = -(w_cash * r_etf).sum()
opp_cash_vs_ewd1 = -(w_cash * EWD1).sum()
r2 = 1 - resid.var() / b.var()
res = {'promotion_approved': False, 'research_only': True,
       'method': 'daily arithmetic contributions from logged etf_w/residual_book_w/cash_w (engine holds weights constant intra-period); book per-unit return regressed on MKT(510300), SMB(broad cap bottom30-top30 EW), HML_EP, UMD_M01 (D1 proxy top30-bottom30). Sum of daily contributions; annualized = sum/years. Compounding gap reported.',
       'years': yrs, 'avg_weights': {'etf': float(w_etf.mean()), 'book': float(w_book.mean()), 'cash': float(w_cash.mean())},
       'regression': {n: {'coef': float(c), 't': float(t)} for n, c, t in zip(names, coef, tstats)}, 'r2': float(r2),
       'alpha_annual_per_unit_book': float(coef[0] * 252),
       'contrib_total_sum': {k: float(v) for k, v in contrib.items()},
       'contrib_annualized': {k: float(v / yrs) for k, v in contrib.items()},
       'sum_of_contribs': float(sum(contrib.values())), 'arm_daily_ret_sum': float(total_arith),
       'arm_total_return_compounded': float(A.nav.iloc[-1] - 1),
       'cash_opportunity_cost_vs_510300_sum': float(opp_cash_vs_510300), 'cash_opportunity_cost_vs_EW_D1_sum': float(opp_cash_vs_ewd1),
       'factor_total_returns_sum': {c: float(FAC[c].sum()) for c in FAC.columns}, 'ew_d1_sum': float(EWD1.sum()),
       'book_unit_return_sum': float(b.sum()), 'book_unit_ann_vol': float(b.std() * np.sqrt(252))}
json.dump(res, open(f'{OUT}/attribution_armA.json', 'w'), indent=1)
pd.DataFrame({'etf_c': etf_c, 'book_c': book_c, 'cost': -cost_ret, 'w_etf': w_etf, 'w_book': w_book, 'w_cash': w_cash, **{c: FAC[c] for c in FAC}, 'EW_D1': EWD1}).to_csv(f'{OUT}/attribution_daily.csv')
print(json.dumps(res, indent=1))
