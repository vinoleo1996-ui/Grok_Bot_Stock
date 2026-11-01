"""Quantify the engine's 'limit-up/limit-down/halt -> 0 contribution' rule on the EW D1-proxy book, and regress it on the same factor model as arm A."""
import sys, json
sys.path.insert(0, '/workspace/QuantLab/research/attrib_v2')
import numpy as np, pandas as pd
from common import *
D = load(); F = features(D); RB = rebal_dates()
R = D['ret'].loc[START:END]; lu = D['lu'].loc[START:END] == 1; ld = D['ld'].loc[START:END] == 1
rb = RB + [END + pd.Timedelta(days=1)]
parts = {k: pd.Series(0.0, index=R.index) for k in ['ew_true', 'lu_part', 'ld_part']}
for i in range(len(RB)):
    u = universe_d1(RB[i], D, F); sl = (R.index > RB[i]) & (R.index <= rb[i + 1])
    r = R.loc[sl, u]; n = r.notna().sum(1)
    parts['ew_true'][sl] = r.sum(1) / n
    parts['lu_part'][sl] = r.where(lu.loc[sl, u]).sum(1) / n
    parts['ld_part'][sl] = r.where(ld.loc[sl, u]).sum(1) / n
P = pd.DataFrame(parts); yrs = len(P) / 252
fd = pd.read_csv(f'{OUT}/attribution_daily.csv', index_col=0, parse_dates=True)
zob = P.ew_true - P.lu_part - P.ld_part
X = np.column_stack([np.ones(len(fd)), fd[['MKT_510300', 'SMB_broad', 'HML_EP', 'UMD_M01']].to_numpy()])
def reg(y):
    c, *_ = np.linalg.lstsq(X, y.reindex(fd.index).fillna(0).to_numpy(), rcond=None); return c
c_true, c_zob = reg(P.ew_true), reg(zob)
res = {'promotion_approved': False, 'years': yrs,
       'sum_daily_ew_true': float(P.ew_true.sum()), 'sum_limit_up_days_dropped': float(P.lu_part.sum()), 'sum_limit_down_days_dropped': float(P.ld_part.sum()),
       'annual_limit_up_dropped': float(P.lu_part.sum() / yrs), 'annual_limit_down_dropped': float(P.ld_part.sum() / yrs),
       'net_annual_leak_from_rule': float(-(P.lu_part.sum() + P.ld_part.sum()) / yrs),
       'alpha_annual_ew_true': float(c_true[0] * 252), 'alpha_annual_ew_zero_on_block': float(c_zob[0] * 252),
       'betas_true': c_true[1:].tolist(), 'betas_zero_on_block': c_zob[1:].tolist()}
json.dump(res, open(f'{OUT}/limit_zero_rule_leak.json', 'w'), indent=1); print(json.dumps(res, indent=1))
