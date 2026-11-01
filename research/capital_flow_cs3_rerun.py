"""CAPITAL_FLOW_CS3_RERUN — CS3 margin only with backfilled rzrq (through 2024-07-26).
Research only; promotion_approved=False. Does not touch MAINBOOK; no H3; no new variants.
Reuses design from research/capital_flow_sealed_v1.py CS3 section.
Signals (preregistered):
  CS3a -(rzye_t - rzye_t-5)/fmc
  CS3b -(mean5(rzmre/amt) - mean60(rzmre/amt))
  CS3c -rqye/fmc
available_at T+1 09:00 -> entry T+1 open (same as V1).
Sealed 2018-01..2024-05 selection; 2024-06..data_max confirm-only (no picking).
"""
from __future__ import annotations
import gc, json, hashlib, resource, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

t0 = time.time()
ROOT = Path('/workspace/QuantLab')
V2 = ROOT / 'data/v2'
S = Path('/workspace/scratch/tic')
OUT = ROOT / 'output/alpha/CAPITAL_FLOW_CS3_RERUN'
OUT.mkdir(parents=True, exist_ok=True)
SEAL_S, SEAL_E = pd.Timestamp('2018-01-01'), pd.Timestamp('2024-05-31')
CONF_S = pd.Timestamp('2024-06-01')
H = (5, 20)
COSTS = (25, 50, 100)
rng = np.random.default_rng(20261011)
NNOISE = 5

def mem_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

def file_sha16(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()[:16]

print(f'start maxrss={mem_mb():.0f}MB', flush=True)

# ---- price panels (float32, A-share filter) ----
ld = lambda c: pd.read_parquet(S / f'{c}.parquet').loc['2017-10-01':].astype('float32')
op = ld('open')
cols = [c for c in op.columns if c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689')
        or c[:5] in ('sz.00','sz.30')]
op = op[cols]
fa = ld('factor')[cols].ffill()
lu = ld('limit_up')[cols]
ts = ld('tradestatus')[cols]
dates = op.index
ND, NC = op.shape
cix = {c: i for i, c in enumerate(cols)}
aO = (op * fa).values.astype('float32')
del fa; gc.collect()
O = op.values
limit_open = (O >= lu.values - 0.005) & np.isfinite(lu.values)
del lu
tradable = (ts.values == 1) & np.isfinite(O) & (O > 0)
del ts, op; gc.collect()
buyable = tradable & ~limit_open
fwd = {}
for h in H:
    f = np.full_like(aO, np.nan)
    f[:-h] = aO[h:] / aO[:-h] - 1
    fwd[h] = f.astype('float32')
del aO; gc.collect()
print(f'panels ok ND={ND} NC={NC} {time.time()-t0:.0f}s maxrss={mem_mb():.0f}MB', flush=True)

# ---- float mktcap + SW L1 ----
fm = pd.read_parquet(V2 / 'float_mktcap/float_mktcap_daily_tushare.parquet',
                     columns=['trade_date', 'instrument_id', 'float_mktcap'])
fm = fm[fm.trade_date >= '2017-10-01']
FMC = (fm.pivot_table(index='trade_date', columns='instrument_id', values='float_mktcap')
         .reindex(index=dates, columns=cols).ffill().astype('float32').values)
del fm; gc.collect()

sw = pd.read_parquet(V2 / 'sw_l1_pit/industry_members_sw_l1_tushare.parquet')
sw['out_date'] = sw['out_date'].fillna(pd.Timestamp('2100-01-01'))
codes = {c: i for i, c in enumerate(sorted(sw.sw_code.unique()))}
NI = len(codes) + 1
IND = np.full((ND, NC), NI - 1, np.int16)
for iid, g in sw.groupby('instrument_id'):
    j = cix.get(iid)
    if j is None:
        continue
    for _, r in g.iterrows():
        m = (dates >= r.in_date) & (dates < r.out_date)
        IND[m, j] = codes[r.sw_code]
del sw; gc.collect()
print(f'fmc+sw ok {time.time()-t0:.0f}s maxrss={mem_mb():.0f}MB', flush=True)

# ---- margin ----
mg_path = V2 / 'margin/rzrq_daily_tushare.parquet'
mg_sha = file_sha16(mg_path)
mg = pd.read_parquet(mg_path, columns=['trade_date', 'ts_code', 'rzye', 'rzmre', 'rqye', 'available_at'])
cov = {
    'margin_rows': int(len(mg)),
    'margin_range': [str(pd.to_datetime(mg.trade_date.min()).date()),
                     str(pd.to_datetime(mg.trade_date.max()).date())],
    'margin_codes': int(mg.ts_code.nunique()),
    'margin_sha16': mg_sha,
    'available_at_sample': str(mg['available_at'].iloc[0]),
    'promotion_approved_in_table': False,
}
# sealed / confirm session counts on disk
_mgd = pd.to_datetime(mg.trade_date)
cov['sealed_sessions_on_disk'] = int(_mgd[(_mgd >= SEAL_S) & (_mgd <= SEAL_E)].nunique())
cov['confirm_sessions_on_disk'] = int(_mgd[_mgd >= CONF_S].nunique())
cov['post_2023_10_sessions'] = int(_mgd[_mgd >= '2023-10-01'].nunique())
cov['sz_codes'] = int(mg.loc[mg.ts_code.astype(str).str.endswith('.SZ'), 'ts_code'].nunique())
print('coverage', cov, flush=True)

mg['iid'] = mg.ts_code.str[-2:].str.lower() + '.' + mg.ts_code.str[:6]
mg['T'] = pd.to_datetime(mg.trade_date)
piv = lambda c: mg.pivot_table(index='T', columns='iid', values=c).reindex(index=dates, columns=cols).astype('float32')
RZ, RZB, RQ = piv('rzye'), piv('rzmre'), piv('rqye')
mg_end = mg['T'].max()
del mg, _mgd; gc.collect()

amt = ld('amount')[cols]
present = RZ.notna()
hist = present.cumsum()
fmcD = pd.DataFrame(FMC, index=dates, columns=cols)
sig = {
    'CS3a_neg_rzye_chg5_over_fmc': -(RZ - RZ.shift(5)) / fmcD,
    'CS3b_neg_finbuy_ratio_chg': -((RZB / amt).rolling(5, min_periods=4).mean()
                                   - (RZB / amt).rolling(60, min_periods=40).mean()),
    'CS3c_neg_rqye_over_fmc': -(RQ / fmcD),
}
del RZ, RZB, RQ, amt, fmcD; gc.collect()
ELIG = (hist.values >= 60) & present.values
del hist, present; gc.collect()
print(f'signals ok {time.time()-t0:.0f}s maxrss={mem_mb():.0f}MB', flush=True)

def neutral(x, d):
    lf = np.log(FMC[d])
    ok = np.isfinite(x) & np.isfinite(lf) & (IND[d] < NI - 1)
    if ok.sum() < 200:
        return None, ok
    xr = pd.Series(x[ok]).rank(pct=True).values - 0.5
    D = np.zeros((ok.sum(), NI))
    D[np.arange(ok.sum()), IND[d][ok]] = 1
    X = np.c_[D, lf[ok] - lf[ok].mean()]
    beta, *_ = np.linalg.lstsq(X, xr, rcond=None)
    out = np.full(NC, np.nan)
    out[ok] = xr - X @ beta
    return out, ok

def spear(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 100:
        return np.nan
    return float(np.corrcoef(pd.Series(a[m]).rank(), pd.Series(b[m]).rank())[0, 1])

marg_last = int(np.searchsorted(dates.values, np.datetime64(mg_end), side='right')) - 1

def eval_window(kind: str, name: str, Pv: np.ndarray, h: int):
    """kind: sealed | confirm | post202310_in_sealed"""
    if kind == 'sealed':
        mask = (dates >= SEAL_S) & (dates <= SEAL_E)
    elif kind == 'confirm':
        mask = dates >= CONF_S
    else:  # post-2023-10 within sealed (selection-side segment, report only)
        mask = (dates >= pd.Timestamp('2023-10-01')) & (dates <= SEAL_E)
    sd = np.where(mask)[0]
    sd = sd[(sd <= marg_last) & (sd + 1 + h < ND)][::h]  # non-overlapping; signal day d, entry d+1
    if len(sd) == 0:
        return None
    ics, ics_lag, noise, tvs, yrs, ctrl = [], [], [], [], [], []
    port = {cb: [] for cb in COSTS}
    gross = []
    prev = None
    for d in sd:
        e = d + 1  # avail T+1 09:00 -> entry T+1 open
        x = np.where(ELIG[d], Pv[d], np.nan)
        z, ok = neutral(x, d)
        if z is None:
            continue
        y = np.where(buyable[e], fwd[h][e], np.nan)
        yr_, _ = neutral(y, d)
        ics.append(spear(z, yr_))
        yrs.append(int(dates[d].year))
        xl = np.where(ELIG[d - 1], Pv[d - 1], np.nan) if d >= 1 else np.full(NC, np.nan)
        zl, _ = neutral(xl, d - 1) if d >= 1 else (None, None)
        ics_lag.append(spear(zl, yr_) if zl is not None else np.nan)
        nz = []
        for _ in range(NNOISE):
            noise_x = np.where(ok, rng.standard_normal(NC), np.nan)
            zn, _ = neutral(noise_x, d)
            nz.append(spear(zn, yr_) if zn is not None else np.nan)
        noise.append(nz)
        m = np.isfinite(z) & buyable[e]
        if m.sum() < 50:
            continue
        thr = np.nanquantile(z[m], 0.9)
        top = np.where(m & (z >= thr))[0]
        rr = float(np.nanmean(np.nan_to_num(fwd[h][e, top], nan=0.0)))
        s = set(top.tolist())
        f = 1.0 if prev is None else 1 - len(s & prev) / max(len(s), 1)
        prev = s
        tvs.append(f)
        gross.append(rr)
        for cb in COSTS:
            port[cb].append(rr - 2 * f * cb / 1e4)
        xx = FMC[d]
        okc = buyable[e] & np.isfinite(xx)
        if okc.sum() >= 100:
            cm = np.where(okc & (xx <= np.nanquantile(xx[okc], 1 / 3)))[0]
            ctrl.append(float(np.nanmean(np.nan_to_num(fwd[h][e, cm], nan=0.0))))
        else:
            ctrl.append(np.nan)
    ics = np.asarray(ics, float)
    if len(ics) < 5:
        return None
    nmeans = np.asarray(noise, float)
    noise_icir = [float(np.nanmean(nmeans[:, k]) / np.nanstd(nmeans[:, k]))
                  for k in range(nmeans.shape[1]) if np.nanstd(nmeans[:, k]) > 0]
    yrsN = len(gross) * h / 244.0
    a = (lambda v: float(np.prod(1 + np.asarray(v, float)) ** (1 / yrsN) - 1)
         if yrsN > 0 and len(v) else float('nan'))
    ic_std = float(np.nanstd(ics))
    ic_mean = float(np.nanmean(ics))
    lag = np.asarray(ics_lag, float)
    lag_std = float(np.nanstd(lag))
    rec = {
        'window': kind,
        'signal': name,
        'h': h,
        'n_dates': int(np.isfinite(ics).sum()),
        'span': [str(dates[sd[0]].date()), str(dates[sd[-1]].date())],
        'IC_mean': ic_mean,
        'ICIR': float(ic_mean / ic_std) if ic_std > 0 else float('nan'),
        'IC_pos_frac': float(np.nanmean(ics > 0)),
        'IC_t_nonoverlap': float(ic_mean / ic_std * np.sqrt(np.isfinite(ics).sum())) if ic_std > 0 else float('nan'),
        'IC_mean_lag1': float(np.nanmean(lag)),
        'ICIR_lag1': float(np.nanmean(lag) / lag_std) if lag_std > 0 else float('nan'),
        'noise_ICIR_absmax_of_5draws': float(np.nanmax(np.abs(noise_icir))) if noise_icir else float('nan'),
        'top_decile_gross_ann': a(gross),
        **{f'top_decile_net_ann_{cb}bp': a(port[cb]) for cb in COSTS},
        'avg_oneway_turnover_per_reb': float(np.mean(tvs)) if tvs else float('nan'),
        'smallcap_ctrl_gross_ann_same_dates': a([x for x in ctrl if np.isfinite(x)]),
        'fill_timing': 'available_at=T+1 09:00; entry=T+1 open (signal day d = T trade_date; entry open d+1)',
    }
    # year IC
    year_rows = []
    for y in sorted(set(yrs)):
        v = ics[np.asarray(yrs) == y]
        year_rows.append({'window': kind, 'signal': name, 'h': h, 'year': y,
                          'IC_mean': float(np.nanmean(v)), 'n': int(len(v))})
    # 8-rule lightweight gates (same spirit as V1 report)
    r1_icir = abs(rec['ICIR']) > 0.10 if np.isfinite(rec['ICIR']) else False
    # lag decay: large drop fails
    if np.isfinite(rec['ICIR']) and abs(rec['ICIR']) > 1e-9 and np.isfinite(rec['ICIR_lag1']):
        drop = 1 - abs(rec['ICIR_lag1']) / abs(rec['ICIR'])
        r1_lag_ok = drop < 0.50  # penalize >50% ICIR drop
    else:
        r1_lag_ok = False
        drop = float('nan')
    r3_noise = (abs(rec['ICIR']) > abs(rec['noise_ICIR_absmax_of_5draws'])
                if np.isfinite(rec['ICIR']) and np.isfinite(rec['noise_ICIR_absmax_of_5draws']) else False)
    # year fold: most years IC>0
    yics = [r['IC_mean'] for r in year_rows]
    r2_folds = (sum(1 for v in yics if v > 0) / len(yics) >= 0.6) if yics else False
    net25 = rec['top_decile_net_ann_25bp']
    sc = rec['smallcap_ctrl_gross_ann_same_dates']
    r6_net = bool(np.isfinite(net25) and net25 > 0 and (not np.isfinite(sc) or net25 > sc))
    # residual IC already size+SW; R4 residual after beta/vol/mom not re-done this round (state)
    gates = {
        'R1_lag_ok': bool(r1_lag_ok), 'R1_lag_drop_frac': float(drop) if np.isfinite(drop) else None,
        'R2_most_years_IC_pos': bool(r2_folds),
        'R3_beats_noise95_proxy': bool(r3_noise),  # absmax of 5 noise ICIRs as proxy
        'R4_size_SW_residual_IC_done': True,
        'R4_full_style_residual_not_rerun': True,
        'R5_label_open_to_open': True,
        'R6_net_pos_and_gt_smallcap': bool(r6_net),
        'R7_ablation_not_this_round': True,
        'R8_ICIR_gt_0p10': bool(r1_icir),
        'overall_pass_ex_ablation': bool(r1_icir and r1_lag_ok and r2_folds and r3_noise and r6_net),
    }
    rec['gates'] = gates
    return rec, year_rows

CS3 = {}
year_all = []
for name, P in sig.items():
    Pv = P.values
    for h in H:
        for kind in ('sealed', 'confirm', 'post202310_in_sealed'):
            out = eval_window(kind, name, Pv, h)
            if out is None:
                print(name, h, kind, 'SKIP empty', flush=True)
                continue
            rec, yrows = out
            key = f'{kind}|{name}|h{h}'
            CS3[key] = rec
            year_all.extend(yrows)
            g = rec['gates']
            print(kind, name, f'h{h}',
                  f"ICIR={rec['ICIR']:.3f}", f"net25={rec['top_decile_net_ann_25bp']:.3%}",
                  f"pass={g['overall_pass_ex_ablation']}",
                  f'{time.time()-t0:.0f}s rss={mem_mb():.0f}MB', flush=True)
    del Pv; gc.collect()

# load V1 truncated for delta
v1_path = ROOT / 'output/alpha/CAPITAL_FLOW_SEALED_V1/cs3_margin_ic.csv'
v1_cmp = {}
if v1_path.exists():
    v1 = pd.read_csv(v1_path)
    for _, r in v1.iterrows():
        v1_cmp[r['key']] = {k: r[k] for k in r.index if k != 'key'}

script_sha = file_sha16(ROOT / 'research/capital_flow_cs3_rerun.py')

summary = {
    'promotion_approved': False,
    'research_only': True,
    'run_id': 'CAPITAL_FLOW_CS3_RERUN',
    'generated_at_local': time.strftime('%Y-%m-%d %H:%M'),
    'tz_note': 'America/New_York (box-local)',
    'sealed': [str(SEAL_S.date()), str(SEAL_E.date())],
    'confirm_from': str(CONF_S.date()),
    'margin_max_on_disk': str(mg_end.date()),
    'coverage': cov,
    'fill_timing': 'available_at=T+1 09:00 Asia/Shanghai; entry at T+1 open (not T+2)',
    'CS3': CS3,
    'v1_truncated_keys': list(v1_cmp.keys()),
    'v1_truncated': v1_cmp,
    'hashes': {
        'script_sha16': script_sha,
        'rzrq_sha16': mg_sha,
        'v1_script_note': 'prior capital_flow_sealed_v1.py design reused',
    },
    'runtime_s': round(time.time() - t0),
    'maxrss_MB': round(mem_mb()),
    'trial_count_this_round': 3 * 2 * 2,  # a/b/c × h5/20 × sealed/confirm (post202310 segment report-only)
    'note': 'Confirm window not used for selection. No new signal variants. MAINBOOK untouched. H3 not run.',
}

json.dump(summary, open(OUT / 'summary.json', 'w'), ensure_ascii=False, indent=1, default=str)

# flat tables
rows = []
for k, v in CS3.items():
    flat = {kk: vv for kk, vv in v.items() if kk not in ('gates', 'span')}
    flat['key'] = k
    flat['span_start'] = v['span'][0]
    flat['span_end'] = v['span'][1]
    for gk, gv in v.get('gates', {}).items():
        flat[f'gate_{gk}'] = gv
    rows.append(flat)
pd.DataFrame(rows).to_csv(OUT / 'cs3_margin_ic.csv', index=False)
pd.DataFrame(year_all).to_csv(OUT / 'cs3_ic_by_year.csv', index=False)

# delta vs V1 (sealed only, matching keys name|h)
delta_rows = []
for name in sig:
    for h in H:
        k_new = f'sealed|{name}|h{h}'
        k_old = f'{name}|h{h}'
        if k_new not in CS3 or k_old not in v1_cmp:
            continue
        n, o = CS3[k_new], v1_cmp[k_old]
        delta_rows.append({
            'signal': name, 'h': h,
            'v1_span_note': 'truncated through 2022-09-19',
            'rerun_span': f"{n['span'][0]}..{n['span'][1]}",
            'ICIR_v1': o.get('ICIR'), 'ICIR_rerun': n['ICIR'],
            'ICIR_delta': (n['ICIR'] - float(o['ICIR'])) if pd.notna(o.get('ICIR')) else None,
            'net25_v1': o.get('top_decile_net_ann_25bp'),
            'net25_rerun': n['top_decile_net_ann_25bp'],
            'smallcap_v1': o.get('smallcap_ctrl_gross_ann_same_dates'),
            'smallcap_rerun': n['smallcap_ctrl_gross_ann_same_dates'],
            'pass_rerun_ex_ablation': n['gates']['overall_pass_ex_ablation'],
        })
pd.DataFrame(delta_rows).to_csv(OUT / 'cs3_vs_v1_delta.csv', index=False)

print('DONE', f'{time.time()-t0:.0f}s', f'maxrss={mem_mb():.0f}MB', 'keys', len(CS3), flush=True)
