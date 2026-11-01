"""TRADABLE_IC_V1 — research-only IC under tradable conventions. promotion_approved=false.
Inputs: /workspace/scratch/tic/*.parquet (built by research/tradable_ic_v1_build_panels.py from load_merged_panel),
valuation (pb), float_mktcap_daily_tushare (size), SW L1 tushare PIT (industry)."""
import sys, json, hashlib, time
from pathlib import Path
import numpy as np, pandas as pd
def rankdata(a):
    return pd.Series(a).rank().values
sys.path.insert(0, '/workspace/QuantLab')
def winsorize_zscore(x):
    """verbatim copy of quantlab.factors.engine.winsorize_zscore (Series path; engine imports scipy, absent in this python)."""
    x = pd.to_numeric(x, errors="coerce"); med = x.median(); mad = (x - med).abs().median() * 1.4826
    if mad < 1e-9:
        mad = x.std()
        if not np.isfinite(mad) or mad < 1e-9: return x * 0.0
    return ((x - med) / mad).clip(-4.0, 4.0)
T0 = time.time()
S = Path('/workspace/scratch/tic'); V2 = Path('/workspace/QuantLab/data/v2')
OUT = Path('/workspace/QuantLab/output/alpha/TRADABLE_IC_V1'); OUT.mkdir(parents=True, exist_ok=True)
STEP = 5; NNOISE = 100; rng = np.random.default_rng(20261010)
ld = lambda c: pd.read_parquet(S/f'{c}.parquet').astype('float32')
op, cl, fa = ld('open'), ld('close'), ld('factor')
cols0 = list(cl.columns)
cols = [c for c in cols0 if (c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689') or c[:5] in ('sz.00','sz.30') or c.startswith('bj.'))]
cols = [c for c in cols if not c.startswith('bj.') or c[3] in '489']
op, cl, fa = op[cols], cl[cols], fa[cols]
amt, tov, ts, lu = ld('amount')[cols], ld('turnover')[cols], ld('tradestatus')[cols], ld('limit_up')[cols]
fa = fa.ffill()
aO, aC = op*fa, cl*fa
ret = aC.pct_change(fill_method=None)
# ---- raw factors (mirror p1_factor_lib definitions) ----
raw = {}
raw['R02_20D'] = -(aC/aC.shift(20)-1)
raw['turn_20d'] = -tov.rolling(20, min_periods=15).mean()
raw['L01_RV60'] = -(ret.rolling(60).std()*np.sqrt(252))
# x1e9 scaling: rank-invariant; avoids winsorize_zscore mad<1e-9 collapse (raw Amihud ~1e-11 when amount in yuan)
amih = (ret.abs()/amt.replace(0, np.nan))*1e9
raw['LIQ02_AMIHUD'] = -amih.rolling(20).mean()
val = pd.read_parquet(V2/'valuation/daily_basic_valuation_tushare.parquet', columns=['trade_date','instrument_id','pb','float_mktcap'])
pb = val.pivot_table(index='trade_date', columns='instrument_id', values='pb').reindex(index=cl.index, columns=cols)
raw['V02_BP'] = (1/pb.where(pb > 0))
fm = pd.read_parquet(V2/'float_mktcap/float_mktcap_daily_tushare.parquet', columns=['trade_date','instrument_id','float_mktcap'])
size = np.log(fm.pivot_table(index='trade_date', columns='instrument_id', values='float_mktcap').reindex(index=cl.index, columns=cols).where(lambda x: x > 0))
del val, fm
import gc; gc.collect()
FAC = ['R02_20D','turn_20d','L01_RV60','V02_BP','LIQ02_AMIHUD']
# style exposures for residual IC
mkt = ret.mean(axis=1)
mvol = mkt.rolling(20).std()
cov = ret.rolling(60, min_periods=40).cov(mkt).astype('float32'); var = mkt.rolling(60, min_periods=40).var()
STY = {'beta': cov.div(var, axis=0), 'vol': ret.rolling(60).std(), 'mom': aC.shift(20)/aC.shift(240)-1,
       'rev': aC/aC.shift(20)-1, 'liq': np.log(tov.rolling(20, min_periods=15).mean())}
for _d in (raw, STY):
    for _k in list(_d): _d[_k] = _d[_k].astype('float32')
size = size.astype('float32'); del cov, var, amih, amt, fa, pb; gc.collect()
OWN = {'R02_20D': ['rev'], 'L01_RV60': ['vol'], 'turn_20d': ['liq'], 'LIQ02_AMIHUD': ['liq'], 'V02_BP': []}
# ---- labels ----
tradable1 = ts.shift(-1).eq(1) & op.shift(-1).notna()
limup1 = (op.shift(-1) >= lu.shift(-1) - 0.005) & lu.shift(-1).notna()
buy_ok = tradable1 & ~limup1
del tradable1, limup1, lu, ret, op; gc.collect()
O1 = aO.shift(-1)
del O1
def labels_at(loc, ids):
    g = lambda F, k: F.iloc[loc+k].reindex(ids).values.astype(float) if loc+k < len(F) else np.full(len(ids), np.nan)
    o1, c0, c1 = g(aO,1), g(aC,0), g(aC,1)
    return {'oo1': g(aO,2)/o1-1, 'oo5': g(aO,6)/o1-1, 'oo20': g(aO,21)/o1-1, 'overnight': o1/c0-1, 'intraday': c1/o1-1, 'cc1': c1/c0-1}
TRADABLE_LABELS = {'oo1','oo5','oo20','intraday'}
# ---- industry PIT ----
sw = pd.read_parquet(V2/'sw_l1_pit/industry_members_sw_l1_tushare.parquet')
sw['out_date'] = sw['out_date'].fillna(pd.Timestamp('2100-01-01'))
dates = cl.index[(cl.index >= '2018-01-02')]
dates = dates[:len(dates)-2][::STEP]
def ind_map(d):
    m = sw[(sw.in_date <= d) & (sw.out_date > d)].drop_duplicates('instrument_id', keep='last')
    return m.set_index('instrument_id')['sw_code']
def rank_ic(x, y):
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 50: return np.nan
    return np.corrcoef(rankdata(x[ok]), rankdata(y[ok]))[0, 1]
def resid(Y, X):
    b, *_ = np.linalg.lstsq(X, Y, rcond=None); return Y - X @ b
def zs(v):
    s = np.nanstd(v); return (v - np.nanmean(v))/s if s > 0 else v*0
rec = []; noise_rec = []; corr_rec = []
for i, d in enumerate(dates):
    loc = cl.index.get_loc(d)
    base = ts.loc[d].eq(1) & cl.loc[d].notna() & size.loc[d].notna()
    im = ind_map(d)
    ids = base[base].index.intersection(im.index)
    if len(ids) < 300: continue
    D = pd.get_dummies(im.reindex(ids)).values.astype(float)
    X = np.column_stack([size.loc[d, ids].values, D])
    tercile = size.loc[d, ids].rank(pct=True).values <= 1/3
    neu = {}
    def neutral(sig):
        z = winsorize_zscore(sig.reindex(ids)).values.astype(float)
        ok = np.isfinite(z); out = np.full(len(ids), np.nan)
        if ok.sum() < 300: return out
        out[ok] = zs(resid(z[ok], X[ok])); return out
    for f in FAC:
        neu[f] = neutral(raw[f].loc[d]); neu[f+'@lag1'] = neutral(raw[f].iloc[loc-1])
    for suf in ['', '@lag1']:
        M = np.column_stack([neu[f+suf] for f in FAC]); n = np.isfinite(M).sum(1)
        c = np.where(n >= 3, np.nanmean(M, 1), np.nan); neu['EW5'+suf] = zs(c)
    # style matrix (winsorized z of each style), neutralized vs size+industry
    St = {k: winsorize_zscore(v.loc[d].reindex(ids)).values.astype(float) for k, v in STY.items()}
    bok = buy_ok.loc[d, ids].values
    labs = {}
    for k, y in labels_at(loc, ids).items():
        if k in TRADABLE_LABELS: y = np.where(bok, y, np.nan)
        labs[k] = y
    lab_noise = labs['oo1']; lab_noise5 = labs['oo5']
    for uni, um in [('full', np.ones(len(ids), bool)), ('smallcap', tercile)]:
        for f in FAC + ['EW5']:
            x = np.where(um, neu[f], np.nan)
            r = {'date': d, 'universe': uni, 'factor': f, 'n': int(np.isfinite(x).sum())}
            for k, y in labs.items(): r[k] = rank_ic(x, y)
            r['oo1_lag1'] = rank_ic(np.where(um, neu[f+'@lag1'], np.nan), labs['oo1'])
            r['oo5_lag1'] = rank_ic(np.where(um, neu[f+'@lag1'], np.nan), labs['oo5'])
            # residual IC: regress out size+ind + 5 styles (all), and ex-own
            for tag, keys in [('resid_all', list(STY)), ('resid_exown', [k for k in STY if k not in OWN.get(f, [])])]:
                Z = np.column_stack([X] + [St[k] for k in keys]); ok = np.isfinite(x) & np.isfinite(Z).all(1)
                xr = np.full(len(ids), np.nan)
                if ok.sum() > 300: xr[ok] = resid(x[ok], Z[ok])
                r[tag+'_oo1'] = rank_ic(xr, labs['oo1']); r[tag+'_oo5'] = rank_ic(xr, labs['oo5'])
            # decile spread / long-only on oo5 (non-overlapping because STEP=5)
            y5 = labs['oo5']; ok = np.isfinite(x) & np.isfinite(y5)
            if ok.sum() > 100:
                q = pd.Series(x[ok]).rank(pct=True).values; yy = y5[ok]
                r['top_dec_oo5'] = yy[q > .9].mean(); r['bot_dec_oo5'] = yy[q <= .1].mean(); r['univ_oo5'] = yy.mean()
                r['top_dec_lowprice_frac'] = float((cl.loc[d, ids].values[ok][q > .9] < 3).mean())
                r['top_dec_size_pct'] = float(pd.Series(size.loc[d, ids].values[ok]).rank(pct=True).values[q > .9].mean())
            r['mkt_vol20'] = float(mvol.iloc[loc]); r['mkt_oo5'] = float(np.nanmean(labs['oo5']))
            rec.append(r)
        # pool correlations
        M = np.column_stack([np.where(um, neu[f], np.nan) for f in FAC])
        dfm = pd.DataFrame(M, columns=FAC).dropna()
        if len(dfm) > 100: corr_rec.append((uni, dfm.rank().corr().values))
        # noise
        G = rng.standard_normal((len(ids), NNOISE))
        Gr = resid(G, X); Gr = (Gr - Gr.mean(0))/Gr.std(0)
        for lk, y in [('oo1', lab_noise), ('oo5', lab_noise5)]:
            ok = um & np.isfinite(y)
            if ok.sum() < 50: continue
            ry = rankdata(y[ok]); RG = pd.DataFrame(Gr[ok]).rank().values
            ic = ((RG - RG.mean(0)) * (ry - ry.mean())[:, None]).sum(0) / (RG.std(0)*ry.std()*ok.sum())
            noise_rec.append(pd.DataFrame({'date': d, 'universe': uni, 'label': lk, 'k': np.arange(NNOISE), 'ic': ic}))
    if i % 40 == 0: print(i, len(dates), d.date(), round(time.time()-T0), flush=True)
R = pd.DataFrame(rec); R.to_parquet(OUT/'ic_by_date.parquet')
N = pd.concat(noise_rec); N.to_parquet(OUT/'noise_ic_by_date.parquet')
C = {u: np.nanmean([c for uu, c in corr_rec if uu == u], 0) for u in ['full','smallcap']}
json.dump({u: pd.DataFrame(C[u], index=FAC, columns=FAC).round(4).to_dict() for u in C}, open(OUT/'pool_corr_mean_spearman.json','w'), indent=1, ensure_ascii=False)
print('done', round(time.time()-T0), len(dates))
