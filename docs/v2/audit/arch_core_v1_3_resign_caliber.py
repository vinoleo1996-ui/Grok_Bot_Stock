#!/usr/bin/env python3
"""Arch v1.3 复签 pass2：整手后可行日在三种口径下的 HARD 复算（只读，不算收益）。
A 代码口径：NAV 层；口径② 510300 记为基准暴露（Size/MidCap/β 取 wb 加权），现金暴露 0；行业 ÷ 预算(1 或 0.8)。
B 股票部分归一（disclosure 口径）：只看股票，权重 ÷ 实际股票合计；现金、510300 都不进分母。
C 股票袖按预算归一：权重 ÷ 预算（现金留在分母、暴露 0）；行业与 A 相同，口径② 风格/β = A ÷ 0.8。"""
import sys, json, pickle, os
sys.path.insert(0, '/workspace/QuantLab'); sys.path.insert(0, '/workspace/QuantLab/research')
import numpy as np, pandas as pd, optimizer_lambda_calib_sealed as C
CK = '/workspace/QuantLab/output/strategy_optimizer/core_x2/_ckpt_v1_3_poolind/'; AUD = '/workspace/QuantLab/docs/v2/audit/'
BF = {'equity_100': 0.0, 'equity80_etf20_510300': 0.2}; TOL = 1e-6; rows = []
for f in sorted(x for x in os.listdir(CK) if x.endswith('.pkl')):
    d = pd.Timestamp(f[:8]); rec = pickle.load(open(CK + f, 'rb'))
    if not rec.get('sleeves'): continue
    D = C.prepare_day(d)
    pool = D['alpha'].index; x = D['ln_mcap'].astype(float).reindex(pool)
    z = ((x - x.mean()) / x.std(ddof=0)).fillna(0); m = (x - x.mean()) ** 2; m = ((m - m.mean()) / m.std(ddof=0)).fillna(0)
    b = D['betas'].reindex(pool).fillna(1.0); wb = D['wb'].reindex(pool).fillna(0); wb = wb / wb.sum()
    ind = pd.Series({i: D['industry'].get(i, '_UNK') for i in pool}); gb = wb.groupby(ind).sum()
    ref = {'z': float((wb * z).sum()), 'm': float((wb * m).sum()), 'b': float((wb * b).sum())}
    for a, sl in rec['sleeves'].items():
        lg = rec['log'][a]; ss = float(lg['slack']['size_slack']); isl = float(lg['slack']['ind_slack'])
        for sv, X in sl.items():
            w = X['w']; bal = float(w.get(C.BALLAST, 0)); we = w.drop(C.BALLAST, errors='ignore').reindex(pool).fillna(0)
            eqs = float(we.sum()); bud = 1 - BF[sv]
            G = we.groupby(ind).sum().reindex(gb.index.union(we.groupby(ind).sum().index)).fillna(0); g0 = gb.reindex(G.index).fillna(0)
            out = dict(date=f'{d:%Y-%m-%d}', window='X2' if d >= pd.Timestamp('2024-06-03') else 'SEALED', aum=a, sleeve=sv, cash=1 - eqs - bal, eq_sum=eqs, size_slack=ss, ind_slack=isl)
            for cal, den, style_nav in (('A', bud, True), ('B', eqs, False), ('C', bud, False)):
                if style_nav:
                    e = {k: float((we * v).sum() + bal * ref[k] - ref[k]) for k, v in (('z', z), ('m', m), ('b', b))}
                else:
                    e = {k: float((we / den * v).sum() - ref[k]) for k, v in (('z', z), ('m', m), ('b', b))}
                Gn = G / den; act = (Gn - g0).abs()
                v = dict(size=max(0, abs(e['z']) - C.SIZE_BOX - ss), mid=max(0, abs(e['m']) - C.SIZE_BOX - ss), beta=max(0, abs(e['b']) - C.BETA_BOX),
                         ind_rel=max(0, float(act.max()) - C.IND_ACTIVE - isl), ind_abs=max(0, float(Gn.max()) - C.IND_ABS))
                for k, val in v.items(): out[f'{cal}_v_{k}'] = val
                out[f'{cal}_size'] = e['z']; out[f'{cal}_mid'] = e['m']; out[f'{cal}_beta'] = e['b']; out[f'{cal}_ind_rel_max'] = float(act.max()); out[f'{cal}_ind_abs_max'] = float(Gn.max())
                out[f'{cal}_any'] = any(val > TOL for val in v.values())
            rows.append(out)
    print(f[:8], flush=True); del D
R = pd.DataFrame(rows); R.to_csv(AUD + 'arch_core_v1_3_resign_caliber.csv', index=False)
S = {}
for cal in 'ABC':
    S[cal] = {}
    for (a, sv), g in R.groupby(['aum', 'sleeve']):
        S[cal][f'{a}_{sv}'] = {'rows': len(g), 'breach_rows': int(g[f'{cal}_any'].sum()), 'X2_breach_rows': int(g[g.window == 'X2'][f'{cal}_any'].sum()),
                               **{k: {'n': int((g[f'{cal}_v_{k}'] > TOL).sum()), 'max_pp_or_sigma': float(g[f'{cal}_v_{k}'].max())} for k in ('size', 'mid', 'beta', 'ind_rel', 'ind_abs')}}
    td = R.groupby(['date', 'aum'])[f'{cal}_any'].any()
    S[cal]['tier_days_flip'] = {str(a): int(td.xs(a, level='aum').sum()) for a in (600000, 1000000)}
    S[cal]['tier_days_flip_X2'] = {str(a): int(R[R.window == 'X2'].groupby(['date', 'aum'])[f'{cal}_any'].any().xs(a, level='aum').sum()) for a in (600000, 1000000)}
json.dump(S, open(AUD + 'arch_core_v1_3_resign_caliber_summary.json', 'w'), indent=1)
print('CALIBER_DONE')
