"""CAPITAL_FLOW_SEALED_V1 — CS1 Dragon-Tiger + CS3 margin on sealed window. Research only.
promotion_approved=False on every output. Does not touch MAINBOOK weights; does not run H3.
Pre-registered variants (ledger rows written before run):
 CS1a inst_net>0 ; CS1b inst_net/amount>1% ; CS1c hot_net>0 & inst_net<=0 (prior negative) ;
 CS1d inst_net>0 & hot_net<0. Lags: PRIMARY avail T+1 15:00 -> entry T+2 open; SENS T 18:00 -> entry T+1 open.
 CS3a -(rzye_t - rzye_t-5)/fmc ; CS3b -(mean5(rzmre/amt) - mean60(rzmre/amt)) ; CS3c -rqye/fmc. avail T+1 09:00 -> entry T+1 open.
"""
import gc, json, sys, time, resource
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, '/workspace/QuantLab')
import importlib.util as _iu  # load skeleton directly (package __init__ needs scipy, absent on box)
_sp=_iu.spec_from_file_location('event_pipeline','/workspace/QuantLab/quantlab/factors/event_pipeline.py'); ep=_iu.module_from_spec(_sp); sys.modules['event_pipeline']=ep; _sp.loader.exec_module(ep)
t0 = time.time()
ROOT = Path('/workspace/QuantLab'); V2 = ROOT/'data/v2'; S = Path('/workspace/scratch/tic')
OUT = ROOT/'output/alpha/CAPITAL_FLOW_SEALED_V1'; OUT.mkdir(parents=True, exist_ok=True)
SEAL_S, SEAL_E, CONF_S = pd.Timestamp(ep.SEALED_START), pd.Timestamp(ep.SEALED_END), pd.Timestamp(ep.CONFIRM_START)
H = (1, 5, 20); COSTS = (25, 50, 100); rng = np.random.default_rng(20261011); NPLAC = 30
def mem(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024

ld = lambda c: pd.read_parquet(S/f'{c}.parquet').loc['2017-10-01':].astype('float32')
op = ld('open'); cols = [c for c in op.columns if c[:6] in ('sh.600','sh.601','sh.603','sh.605','sh.688','sh.689') or c[:5] in ('sz.00','sz.30')]
op = op[cols]; fa = ld('factor')[cols].ffill(); lu = ld('limit_up')[cols]; ts = ld('tradestatus')[cols]
dates = op.index; ND, NC = op.shape; cix = {c:i for i,c in enumerate(cols)}
aO = (op*fa).values; del fa; gc.collect()
O = op.values
limit_open = (O >= lu.values - 0.005) & np.isfinite(lu.values); del lu
tradable = (ts.values == 1) & np.isfinite(O) & (O > 0); del ts, op; gc.collect()
buyable = tradable & ~limit_open
fwd = {}
for h in H:
    f = np.full_like(aO, np.nan); f[:-h] = aO[h:]/aO[:-h] - 1; fwd[h] = f.astype('float32')
r1 = np.nan_to_num(fwd[1], nan=0.0)
# float mktcap & industry
fm = pd.read_parquet(V2/'float_mktcap/float_mktcap_daily_tushare.parquet', columns=['trade_date','instrument_id','float_mktcap'])
fm = fm[fm.trade_date >= '2017-10-01']
FMC = fm.pivot_table(index='trade_date', columns='instrument_id', values='float_mktcap').reindex(index=dates, columns=cols).ffill().astype('float32').values
del fm; gc.collect()
sw = pd.read_parquet(V2/'sw_l1_pit/industry_members_sw_l1_tushare.parquet'); sw['out_date'] = sw['out_date'].fillna(pd.Timestamp('2100-01-01'))
codes = {c:i for i,c in enumerate(sorted(sw.sw_code.unique()))}; NI = len(codes)+1
IND = np.full((ND, NC), NI-1, np.int16)
for iid, g in sw.groupby('instrument_id'):
    j = cix.get(iid)
    if j is None: continue
    for _, r in g.iterrows():
        m = (dates >= r.in_date) & (dates < r.out_date); IND[m, j] = codes[r.sw_code]
# size quintile on day d-1 (known before open d)
SZQ = np.full((ND, NC), -1, np.int8)
for d in range(1, ND):
    x = FMC[d-1]; ok = np.isfinite(x)
    if ok.sum() < 100: continue
    rk = pd.Series(x[ok]).rank(pct=True).values; SZQ[d, ok] = np.minimum((rk*5).astype(int), 4)
KEY = IND.astype(np.int32)*5 + SZQ.astype(np.int32); KEY[SZQ < 0] = -1; NK = NI*5
# benchmark: size x SW-L1 matched mean over buyable stocks on entry day
BEN = {}
for h in H:
    B = np.full((ND, NC), np.nan, np.float32)
    for d in range(ND):
        v = fwd[h][d]; ok = buyable[d] & np.isfinite(v) & (KEY[d] >= 0)
        if ok.sum() < 50: continue
        s = np.bincount(KEY[d][ok], weights=v[ok], minlength=NK); n = np.bincount(KEY[d][ok], minlength=NK)
        gm = np.where(n > 0, s/np.maximum(n, 1), np.nan); k = KEY[d]; B[d, k >= 0] = gm[k[k >= 0]]
    BEN[h] = B
print('panels ok', ND, NC, f'{time.time()-t0:.0f}s', f'maxrss {mem():.0f}MB', flush=True)

def ann(daily):  # geometric, 244 sessions
    daily = np.asarray(daily, float); n = len(daily)
    if n == 0: return np.nan
    tot = np.prod(1 + daily); return tot**(244/n) - 1

def window_mask(kind):
    if kind == 'sealed': return (dates >= SEAL_S) & (dates <= SEAL_E)
    return dates >= CONF_S

# ---------------- CS1 Dragon-Tiger ----------------
ti = pd.read_parquet(V2/'dragon_tiger/top_inst_labeled.parquet', columns=['trade_date','ts_code','exalter','buy','sell','net_buy','seat_type'])
cov = {'top_inst_rows': int(len(ti)), 'top_inst_range': [ti.trade_date.min(), ti.trade_date.max()], 'seat_type_counts': ti.seat_type.value_counts().to_dict()}
ti = ti.drop_duplicates(['trade_date','ts_code','exalter','buy','sell'])
cov['top_inst_rows_dedup'] = int(len(ti))
ti['inst'] = np.where(ti.seat_type == 'institution', ti.net_buy, 0.0); ti['hot'] = np.where(ti.seat_type == 'retail_or_hot_money', ti.net_buy, 0.0)
ev = ti.groupby(['trade_date','ts_code'])[['inst','hot']].sum().reset_index(); del ti; gc.collect()
tl = pd.read_parquet(V2/'dragon_tiger/top_list.parquet', columns=['trade_date','ts_code','amount']).groupby(['trade_date','ts_code']).amount.max().reset_index()
ev = ev.merge(tl, on=['trade_date','ts_code'], how='left'); del tl
ev['iid'] = ev.ts_code.str[-2:].str.lower() + '.' + ev.ts_code.str[:6]
ev['T'] = pd.to_datetime(ev.trade_date); ev['col'] = ev.iid.map(cix)
ev = ev[ev.col.notna()].copy(); ev['col'] = ev.col.astype(int)
ev['p'] = np.searchsorted(dates.values, ev['T'].values)  # session index of T (T is a session)
ev = ev[(ev.p < ND) & (dates[np.minimum(ev.p, ND-1)] == ev['T'])]
ev['inst_r'] = ev.inst / ev.amount
cov['lhb_stock_days'] = int(len(ev))
VARS = {'CS1a_inst_netbuy_pos': ev.inst > 0, 'CS1b_inst_netbuy_gt1pct_amt': ev.inst_r > 0.01,
        'CS1c_hotmoney_only_netbuy': (ev.hot > 0) & (ev.inst <= 0), 'CS1d_inst_buy_hot_sell_diverge': (ev.inst > 0) & (ev.hot < 0)}
LAGS = {'primary_T+1_1500_entryT+2': 2, 'sens_T_1800_entryT+1': 1}

def portfolio(e_arr, c_arr, h, mask_days, cost_bp):
    """EW across live positions; enter at open e, exit at open e+h; daily open->open."""
    sumr = np.zeros(ND); n = np.zeros(ND); ent = np.zeros(ND); ex = np.zeros(ND)
    for e, c in zip(e_arr, c_arr):
        end = min(e+h, ND-1)
        sumr[e:end] += r1[e:end, c]; n[e:end] += 1; ent[e] += 1; ex[end] += 1
    g = np.where(n > 0, sumr/np.maximum(n, 1), 0.0)
    nprev = np.r_[0, n[:-1]]
    turn = np.where(n > 0, ent/np.maximum(n, 1), 0) + np.where(nprev > 0, ex/np.maximum(nprev, 1), 0)
    out = {}
    for cb in cost_bp:
        net = g - turn*cb/1e4; out[cb] = net[mask_days]
    return g[mask_days], out, turn[mask_days], n[mask_days]

def smallcap_ctrl(h, mask_days, cost_bp):
    idx = np.where(mask_days)[0]; reb = idx[::h]; res = {cb: [] for cb in cost_bp}; gross = []; prev = None; tv = []
    for d in reb:
        x = FMC[d-1]; ok = buyable[d] & np.isfinite(x)
        if ok.sum() < 100: continue  # no fmc coverage that day -> skip rebalance
        thr = np.nanquantile(x[ok], 1/3); mem_ = np.where(ok & (x <= thr))[0]
        rr = np.nanmean(np.nan_to_num(fwd[h][d, mem_], nan=0.0))
        s = set(mem_); f = 1.0 if prev is None else 1 - len(s & prev)/max(len(s), 1); prev = s; tv.append(f)
        gross.append(rr)
        for cb in cost_bp: res[cb].append(rr - 2*f*cb/1e4)
    yrs = len(gross)*h/244
    a = lambda v: np.prod(1+np.array(v))**(1/yrs) - 1 if yrs > 0 else np.nan
    return {'gross_ann': a(gross), **{f'net_ann_{cb}bp': a(res[cb]) for cb in cost_bp}, 'avg_oneway_turnover_per_reb': float(np.mean(tv)), 'n_reb': len(reb)}

CS1 = {}; byyear_rows = []
for kind in ('sealed', 'confirm'):
    wm = window_mask(kind)
    for vname, vm in VARS.items():
        for lname, lag in LAGS.items():
            sub = ev[vm.values]; e = (sub.p + lag).values; c = sub.col.values
            ok = e < ND - 1; e, c = e[ok], c[ok]; T_ = sub['T'].values[ok]
            inwin = wm[e]; e, c, T_ = e[inwin], c[inwin], T_[inwin]
            n_raw = len(e); b = buyable[e, c]; e, c, T_ = e[b], c[b], T_[b]
            rec = {'n_events_raw': int(n_raw), 'n_excluded_limitup_or_susp': int(n_raw - len(e)), 'n_events': int(len(e)),
                   'n_names': int(len(set(c))), 'events_per_month': float(len(e)/max(wm.sum()/21, 1))}
            for h in H:
                car = fwd[h][e, c] - BEN[h][e, c]; car = car[np.isfinite(car)]
                rec[f'CAR{h}_mean'] = float(car.mean()) if len(car) else np.nan
                rec[f'CAR{h}_t'] = float(car.mean()/car.std(ddof=1)*np.sqrt(len(car))) if len(car) > 2 else np.nan
                rec[f'CAR{h}_hit'] = float((car > 0).mean()) if len(car) else np.nan
                # placebo: random buyable stock in same size x industry cell, same entry day
                if kind == 'sealed' and lag == 2 and h in (5, 20):
                    pm = []
                    for _ in range(NPLAC):
                        vals = []
                        for d in np.unique(e):
                            kk = KEY[d, c[e == d]]; pool_ok = buyable[d] & (KEY[d] >= 0)
                            for k in kk:
                                cand = np.where(pool_ok & (KEY[d] == k))[0]
                                if len(cand): j = rng.choice(cand); vals.append(fwd[h][d, j] - BEN[h][d, j])
                        vals = np.array(vals); pm.append(np.nanmean(vals))
                    rec[f'placebo_CAR{h}_p95'] = float(np.nanpercentile(pm, 95)); rec[f'placebo_CAR{h}_p05'] = float(np.nanpercentile(pm, 5))
            if lag == 2 or kind == 'sealed':
                for h in (5, 20):
                    g, nets, turn, nn = portfolio(e, c, h, wm, COSTS)
                    rec[f'port_h{h}_gross_ann'] = float(ann(g)); rec[f'port_h{h}_invested_frac'] = float((nn > 0).mean())
                    rec[f'port_h{h}_avg_names'] = float(nn[nn > 0].mean()) if (nn > 0).any() else 0.0
                    rec[f'port_h{h}_daily_turnover_oneway'] = float(turn.mean()/2)
                    for cb in COSTS: rec[f'port_h{h}_net_ann_{cb}bp'] = float(ann(nets[cb]))
                    if kind == 'sealed':
                        yrs = dates[wm].year
                        for y in np.unique(yrs):
                            ym = yrs == y
                            byyear_rows.append({'variant': vname, 'lag': lname, 'h': h, 'year': int(y), 'gross_ann': float(ann(g[ym])),
                                                **{f'net_ann_{cb}bp': float(ann(nets[cb][ym])) for cb in COSTS}})
                # subperiod CAR5
                yrsE = pd.DatetimeIndex(T_).year; car5 = fwd[5][e, c] - BEN[5][e, c]
                for lab, m in (('2018_2020', yrsE <= 2020), ('2021_2024', yrsE >= 2021)):
                    v = car5[m]; v = v[np.isfinite(v)]; rec[f'CAR5_{lab}'] = float(v.mean()) if len(v) else np.nan
                for y in np.unique(yrsE):
                    v = car5[yrsE == y]; v = v[np.isfinite(v)]; rec[f'CAR5_y{y}'] = float(v.mean()) if len(v) else np.nan
            CS1[f'{kind}|{vname}|{lname}'] = rec
            print(kind, vname, lname, rec['n_events'], round(rec.get('CAR5_mean', np.nan), 5), f'{time.time()-t0:.0f}s', flush=True)
CTRL = {f'{k}|h{h}': smallcap_ctrl(h, window_mask(k), COSTS) for k in ('sealed', 'confirm') for h in (5, 20)}
del ev; gc.collect()

# ---------------- CS3 margin ----------------
mg = pd.read_parquet(V2/'margin/rzrq_daily_tushare.parquet', columns=['trade_date','ts_code','rzye','rzmre','rqye'])
cov['margin_rows'] = int(len(mg)); cov['margin_range'] = [mg.trade_date.min(), mg.trade_date.max()]; cov['margin_codes'] = int(mg.ts_code.nunique())
mg['iid'] = mg.ts_code.str[-2:].str.lower() + '.' + mg.ts_code.str[:6]; mg['T'] = pd.to_datetime(mg.trade_date)
piv = lambda c: mg.pivot_table(index='T', columns='iid', values=c).reindex(index=dates, columns=cols).astype('float32')
RZ, RZB, RQ = piv('rzye'), piv('rzmre'), piv('rqye'); mg_end = mg['T'].max(); del mg; gc.collect()
amt = ld('amount')[cols]
present = RZ.notna(); hist = present.cumsum()  # eligibility: >=60 sessions of margin data
fmcD = pd.DataFrame(FMC, index=dates, columns=cols)
sig = {'CS3a_neg_rzye_chg5_over_fmc': -(RZ - RZ.shift(5))/fmcD,
       'CS3b_neg_finbuy_ratio_chg': -((RZB/amt).rolling(5, min_periods=4).mean() - (RZB/amt).rolling(60, min_periods=40).mean()),
       'CS3c_neg_rqye_over_fmc': -(RQ/fmcD)}
del RZ, RZB, RQ, amt; gc.collect()
ELIG = (hist.values >= 60) & present.values; del hist, present

def neutral(x, d):
    lf = np.log(FMC[d]); ok = np.isfinite(x) & np.isfinite(lf) & (IND[d] < NI-1)
    if ok.sum() < 200: return None, ok
    xr = pd.Series(x[ok]).rank(pct=True).values - 0.5
    D = np.zeros((ok.sum(), NI)); D[np.arange(ok.sum()), IND[d][ok]] = 1; X = np.c_[D, lf[ok]-lf[ok].mean()]
    beta, *_ = np.linalg.lstsq(X, xr, rcond=None); out = np.full(NC, np.nan); out[ok] = xr - X@beta; return out, ok

def spear(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 100: return np.nan
    return float(np.corrcoef(pd.Series(a[m]).rank(), pd.Series(b[m]).rank())[0, 1])

marg_last = int(np.searchsorted(dates.values, np.datetime64(mg_end), side='right')) - 1
CS3 = {}; cs3_year = []
for name, P in sig.items():
    Pv = P.values
    for h in (5, 20):
        sd = np.where((dates >= SEAL_S) & (dates <= SEAL_E))[0]; sd = sd[(sd <= marg_last) & (sd + 1 + h < ND)][::h]  # non-overlapping
        ics, ics_lag, noise, port, ctrl, tvs, yrs = [], [], [], {cb: [] for cb in COSTS}, [], [], []; prev = None; gross = []
        for d in sd:
            e = d + 1  # avail T+1 09:00 -> entry T+1 open 09:30
            x = np.where(ELIG[d], Pv[d], np.nan); z, ok = neutral(x, d)
            if z is None: continue
            y = np.where(buyable[e], fwd[h][e], np.nan)
            yr_, _ = neutral(y, d)  # size+industry neutral label
            ics.append(spear(z, yr_)); yrs.append(dates[d].year)
            xl = np.where(ELIG[d-1], Pv[d-1], np.nan); zl, _ = neutral(xl, d-1); ics_lag.append(spear(zl, yr_) if zl is not None else np.nan)  # use signal one day staler
            nz = [spear(neutral(np.where(ok, rng.standard_normal(NC), np.nan), d)[0], yr_) for _ in range(5)]; noise.append(nz)
            m = np.isfinite(z) & buyable[e]; thr = np.nanquantile(z[m], 0.9); top = np.where(m & (z >= thr))[0]
            rr = float(np.nanmean(np.nan_to_num(fwd[h][e, top], nan=0.0))); s = set(top)
            f = 1.0 if prev is None else 1 - len(s & prev)/max(len(s), 1); prev = s; tvs.append(f); gross.append(rr)
            for cb in COSTS: port[cb].append(rr - 2*f*cb/1e4)
            # small-cap control on same dates, among same eligible universe? use full buyable universe bottom tercile
            xx = FMC[d]; okc = buyable[e] & np.isfinite(xx); cm = np.where(okc & (xx <= np.nanquantile(xx[okc], 1/3)))[0]
            ctrl.append(float(np.nanmean(np.nan_to_num(fwd[h][e, cm], nan=0.0))))
        ics = np.array(ics); nmeans = np.array(noise)  # per-date 5 draws -> build 5 noise ICIR series
        noise_icir = [np.nanmean(nmeans[:, k])/np.nanstd(nmeans[:, k]) for k in range(nmeans.shape[1])]
        yrsN = len(gross)*h/244; a = lambda v: float(np.prod(1+np.array(v))**(1/yrsN) - 1)
        rec = {'n_dates': int(len(ics)), 'span': [str(dates[sd[0]].date()), str(dates[min(sd[-1], ND-1)].date())],
               'IC_mean': float(np.nanmean(ics)), 'ICIR': float(np.nanmean(ics)/np.nanstd(ics)), 'IC_pos_frac': float(np.nanmean(ics > 0)),
               'IC_t_nonoverlap': float(np.nanmean(ics)/np.nanstd(ics)*np.sqrt(np.isfinite(ics).sum())),
               'IC_mean_lag1': float(np.nanmean(ics_lag)), 'ICIR_lag1': float(np.nanmean(ics_lag)/np.nanstd(ics_lag)),
               'noise_ICIR_absmax_of_5draws': float(np.nanmax(np.abs(noise_icir))),
               'top_decile_gross_ann': a(gross), **{f'top_decile_net_ann_{cb}bp': a(port[cb]) for cb in COSTS},
               'avg_oneway_turnover_per_reb': float(np.mean(tvs)), 'smallcap_ctrl_gross_ann_same_dates': a(ctrl)}
        for y in sorted(set(yrs)):
            v = ics[np.array(yrs) == y]; cs3_year.append({'signal': name, 'h': h, 'year': y, 'IC_mean': float(np.nanmean(v)), 'n': int(len(v))})
        CS3[f'{name}|h{h}'] = rec; print(name, h, {k: round(v, 4) for k, v in rec.items() if isinstance(v, float)}, flush=True)
    del Pv; gc.collect()

summary = {'promotion_approved': False, 'research_only': True, 'run_id': 'CAPITAL_FLOW_SEALED_V1', 'generated_at_local': time.strftime('%Y-%m-%d %H:%M'),
           'sealed': [str(SEAL_S.date()), str(SEAL_E.date())], 'confirm_from': str(CONF_S.date()), 'coverage': cov,
           'margin_truncated_at': str(mg_end.date()), 'CS1': CS1, 'CS1_smallcap_ctrl': CTRL, 'CS3': CS3,
           'placebo_draws': NPLAC, 'runtime_s': round(time.time()-t0), 'maxrss_MB': round(mem())}
json.dump(summary, open(OUT/'summary.json', 'w'), ensure_ascii=False, indent=1, default=str)
pd.DataFrame([{'key': k, **v} for k, v in CS1.items()]).to_csv(OUT/'cs1_events.csv', index=False)
pd.DataFrame(byyear_rows).to_csv(OUT/'cs1_portfolio_by_year.csv', index=False)
pd.DataFrame([{'key': k, **v} for k, v in CTRL.items()]).to_csv(OUT/'smallcap_ctrl.csv', index=False)
pd.DataFrame([{'key': k, **{a: b for a, b in v.items() if a != 'span'}} for k, v in CS3.items()]).to_csv(OUT/'cs3_margin_ic.csv', index=False)
pd.DataFrame(cs3_year).to_csv(OUT/'cs3_ic_by_year.csv', index=False)
print('DONE', f'{time.time()-t0:.0f}s', f'maxrss {mem():.0f}MB', flush=True)
