import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
OUT = Path('/workspace/QuantLab/output/alpha/TRADABLE_IC_V1')
R = pd.read_parquet(OUT/'ic_by_date.parquet'); N = pd.read_parquet(OUT/'noise_ic_by_date.parquet')
corr = json.load(open(OUT/'pool_corr_mean_spearman.json'))
LABS = ['oo1','oo5','oo20','overnight','intraday','cc1','oo1_lag1','oo5_lag1','resid_all_oo1','resid_exown_oo1','resid_all_oo5','resid_exown_oo5']
FAC = ['R02_20D','turn_20d','L01_RV60','V02_BP','LIQ02_AMIHUD','EW5']
def st(s):
    s = s.dropna(); m, sd = s.mean(), s.std()
    return {'mean_ic': round(m,5), 'icir': round(m/sd,4) if sd>0 else None, 't_naive': round(m/sd*np.sqrt(len(s)),2) if sd>0 else None, 'pos_frac': round((s>0).mean(),3), 'n_dates': int(len(s))}
nz = {}
for (u, l), g in N.groupby(['universe','label']):
    per = g.groupby('k')['ic'].agg(['mean','std']); per['icir'] = per['mean']/per['std']
    nz[f'{u}|{l}'] = {'p95_abs_mean_ic': round(float(per['mean'].abs().quantile(.95)),5), 'p95_abs_icir': round(float(per['icir'].abs().quantile(.95)),4), 'n_noise': int(len(per))}
summary = {'promotion_approved': False, 'spec': {}, 'noise': nz, 'pool_corr': corr, 'results': {}}
R['year'] = pd.to_datetime(R['date']).dt.year
for u in ['full','smallcap']:
    for f in FAC:
        g = R[(R.universe==u)&(R.factor==f)]
        res = {l: st(g[l]) for l in LABS}
        by_year = g.groupby('year')[['oo1','oo5','oo20','overnight','intraday','cc1']].mean().round(5)
        by_year.to_csv(OUT/f'by_year_{u}_{f}.csv')
        # walk-forward: expanding train (years < y) fixes sign; test year y improves if IC*sign>0
        folds = []
        for lab in ['oo1','oo5']:
            yrs = sorted(g.year.unique()); imp = 0; tot = 0
            for y in yrs[1:]:
                tr = g[g.year < y][lab].mean(); te = g[g.year == y][lab].mean()
                if np.isfinite(tr) and np.isfinite(te): tot += 1; imp += int(np.sign(tr)*te > 0)
            folds.append({'label': lab, 'folds_improved': imp, 'folds': tot})
        ic1 = res['oo1']['mean_ic']; icl = res['oo1_lag1']['mean_ic']
        lag = {'ic_oo1': ic1, 'ic_oo1_lag1': icl, 'delta_lag': round(max(0.0, abs(ic1)-abs(icl)) if np.sign(ic1)==np.sign(icl) else abs(ic1),5), 'retained_frac': round(icl/ic1,3) if ic1 else None}
        n1 = nz[f'{u}|oo1']; n5 = nz[f'{u}|oo5']
        noise_pass = {'oo1': abs(ic1) > n1['p95_abs_mean_ic'], 'oo5': abs(res['oo5']['mean_ic']) > n5['p95_abs_mean_ic']}
        mc = None
        if f != 'EW5':
            c = pd.DataFrame(corr[u]); mc = round(float(c[f].drop(f).abs().max()), 4)
        gates = {'icir_oo1_gt_0.10': bool(abs(res['oo1']['icir'] or 0) > 0.10), 'icir_oo5_gt_0.10': bool(abs(res['oo5']['icir'] or 0) > 0.10),
                 'max_pool_corr_lt_0.70': (mc < 0.70) if mc is not None else None, 'noise95_oo1': bool(noise_pass['oo1']), 'noise95_oo5': bool(noise_pass['oo5']),
                 'wf_majority_oo1': folds[0]['folds_improved']*2 > folds[0]['folds'], 'lag_retained_ge_0.5': bool((lag['retained_frac'] or 0) >= 0.5),
                 'resid_all_same_sign_oo1': bool(np.sign(res['resid_all_oo1']['mean_ic'])==np.sign(ic1))}
        core = [gates['icir_oo1_gt_0.10'] or gates['icir_oo5_gt_0.10'], gates['noise95_oo1'] or gates['noise95_oo5'], gates['wf_majority_oo1'], gates['lag_retained_ge_0.5']] + ([gates['max_pool_corr_lt_0.70']] if mc is not None else [])
        summary['results'][f'{u}|{f}'] = {'stats': res, 'lag': lag, 'walk_forward': folds, 'max_abs_pool_corr': mc, 'gates': gates, 'survives': bool(all(core))}
        pd.DataFrame(res).T.to_csv(OUT/f'stats_{u}_{f}.csv')
summary['trial_count'] = {'factor_x_universe_x_label_variants': int(len(FAC)*2*len(LABS)), 'factors': len(FAC), 'universes': 2, 'labels': LABS, 'noise_factors': '100 x 2 universes x 2 labels (benchmark, not counted as trials)'}
json.dump(summary, open(OUT/'summary.json','w'), indent=1, ensure_ascii=False, default=lambda o: bool(o) if isinstance(o, np.bool_) else str(o))
for k, v in summary['results'].items():
    s = v['stats']; print(k, 'oo1', s['oo1']['mean_ic'], s['oo1']['icir'], '| oo5', s['oo5']['mean_ic'], s['oo5']['icir'], '| oo20', s['oo20']['mean_ic'], s['oo20']['icir'],
          '| on', s['overnight']['mean_ic'], 'id', s['intraday']['mean_ic'], 'cc', s['cc1']['mean_ic'], '| rA', s['resid_all_oo1']['mean_ic'], 'rX', s['resid_exown_oo1']['mean_ic'], s['resid_exown_oo5']['mean_ic'],
          '| lag', v['lag']['ic_oo1_lag1'], v['lag']['retained_frac'], '| wf', v['walk_forward'], '| corr', v['max_abs_pool_corr'], '| G', {a:b for a,b in v['gates'].items()}, 'SURV', v['survives'])
print(json.dumps(nz)); print(json.dumps(corr, ensure_ascii=False))
# ---------- extensions (steering 22:26 ET) ----------
ext = {}
dates = sorted(R.date.unique()); d20 = set(dates[::4])  # non-overlapping 20d (every 4th 5-step sample)
for (u, f), g in R.groupby(['universe','factor']):
    g = g.dropna(subset=['top_dec_oo5','bot_dec_oo5']).copy()
    g['spread'] = g.top_dec_oo5 - g.bot_dec_oo5
    g['lo_net'] = g.top_dec_oo5 - g.univ_oo5 - 0.0020  # long-only top decile vs EW universe, 20bp per weekly rebalance (conservative: full turnover)
    hv = g.mkt_vol20 > g.mkt_vol20.median(); big = g.mkt_oo5.abs() > g.mkt_oo5.abs().quantile(.8)
    sp = g.spread.values; top10 = np.sort(np.abs(sp))[::-1][:max(1, len(sp)//10)].sum()
    srt = g.spread.sort_values(ascending=False)
    k = max(1, len(g)//20); drop_top = g.spread.drop(srt.index[:k]).mean() if np.sign(g.spread.mean())>0 else g.spread.drop(srt.index[-k:]).mean()
    nz20 = g[g.date.isin(d20)]['oo20']
    ann = lambda m: (1+m)**(252/5)-1
    e = {'ic_oo5_highvol': round(g[hv].oo5.mean(),5), 'ic_oo5_lowvol': round(g[~hv].oo5.mean(),5),
         'ic_oo5_bigmove': round(g[big].oo5.mean(),5), 'ic_oo5_smallmove': round(g[~big].oo5.mean(),5),
         'spread_oo5_mean': round(g.spread.mean(),5), 'spread_oo5_geo_ann': round(ann(g.spread.mean()),4),
         'spread_mean_ex_best5pct_weeks': round(drop_top,5), 'fragile_flag': bool(np.sign(drop_top) != np.sign(g.spread.mean()) or abs(drop_top) < 0.5*abs(g.spread.mean())),
         'rankic_vs_spread_agree': bool(np.sign(g.oo5.mean()) == np.sign(g.spread.mean())),
         'top_dec_lowprice_lt3_frac': round(g.top_dec_lowprice_frac.mean(),4), 'top_dec_mean_size_pctile': round(g.top_dec_size_pct.mean(),4),
         'longonly_top_dec_minus_univ_net20bp_weekly_mean': round(g.lo_net.mean(),5), 'longonly_net_geo_ann': round(float(np.prod(1+g.lo_net)**(52/len(g))-1),4),
         'longonly_net_pos': bool(g.lo_net.mean() > 0),
         'nonoverlap_oo5': st(g.oo5), 'nonoverlap_oo20_every4th': st(nz20)}
    if f == 'R02_20D':  # structural-break down-weighting: weeks with |mkt oo5| top 5% weighted 0.25
        w = np.where(g.mkt_oo5.abs() > g.mkt_oo5.abs().quantile(.95), .25, 1.0)
        e['reversal_ic_oo5_downweight_breaks'] = round(float(np.average(g.oo5.fillna(0), weights=w)), 5)
        ex = g[~((g.date >= '2024-01-01') & (g.date < '2024-03-01')) & ~((g.date >= '2020-01-20') & (g.date < '2020-03-31'))]
        e['reversal_ic_oo5_excl_2020Q1covid_2024JanFeb'] = round(ex.oo5.mean(), 5)
    ext[f'{u}|{f}'] = e
summary['extensions'] = ext
json.dump(summary, open(OUT/'summary.json','w'), indent=1, ensure_ascii=False, default=lambda o: bool(o) if isinstance(o, np.bool_) else str(o))
for k, v in ext.items(): print('EXT', k, {a: b for a, b in v.items() if not isinstance(b, dict)}, 'NO20', v['nonoverlap_oo20_every4th'])
