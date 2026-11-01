#!/usr/bin/env python3
"""Arch 程序性复签 v1.3 — 独立复算脚本（只读；不算收益；不写 core_x2/）。
输入：output/strategy_optimizer/core_x2/_ckpt_v1_3_poolind/*.pkl、core_*_{60w,100w}.parquet、core_v1_3_*.csv、数据层 C.prepare_day（池、全池 wb、申万行业、ln_mcap、β）。
约束复算全部由本脚本自写；一手价格由本脚本直接读 daily_basic parquet。
INFEASIBLE 日：为了分类失败原因、核对“沿用上期而非 step1 篮子”，在内存中用生产求解器复现当日求解+整手（不落盘），再用本脚本的检查器判定越界项。
输出：docs/v2/audit/arch_core_v1_3_resign_{expo.csv,excl.csv,infeas.csv,summary.json}
"""
import sys, json, pickle, os, re, resource, random, hashlib
sys.path.insert(0, '/workspace/QuantLab'); sys.path.insert(0, '/workspace/QuantLab/research')
import numpy as np, pandas as pd, pyarrow.parquet as pq
import optimizer_lambda_calib_sealed as C
import optimizer_core_v1_1 as V
V.POOL_STD = True; V.IND_POOL = True   # 只在内存，供 INFEASIBLE 日复现
ROOT = '/workspace/QuantLab/'; OUT = ROOT + 'output/strategy_optimizer/core_x2/'; CK = OUT + '_ckpt_v1_3_poolind/'
AUD = ROOT + 'docs/v2/audit/'
AUMS = (600000, 1000000); SLV = ('equity_100', 'equity80_etf20_510300'); BF = {'equity_100': 0.0, 'equity80_etf20_510300': 0.20}
X2S = pd.Timestamp('2024-06-03'); TOL = 1e-6
rss = lambda: round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
S = {}

# ---------- (a) 污染检查 ----------
log_lines = open(OUT + 'run_weights_v1_3.log').read().splitlines()
m = re.search(r'run_start_et=(\S+ \S+)', log_lines[0]); run_start = pd.Timestamp(m.group(1)[:26]) if m else None
files = sorted(os.listdir(CK)); pk = [f for f in files if f.endswith('.pkl')]
mt = {f: pd.Timestamp(os.stat(CK + f).st_mtime, unit='s', tz='UTC').tz_convert('America/New_York').tz_localize(None) for f in pk}
smoke_hits = []
for f in pk:
    r = pickle.load(open(CK + f, 'rb'))
    blob = json.dumps({k: v for k, v in r.items() if k in ('log',)}, default=str).lower() + ' '.join(map(str, r.keys())).lower()
    if 'smoke' in blob: smoke_hits.append(f)
    if r.get('day', '').replace('-', '') != f[:8]: smoke_hits.append(f + ':day_mismatch')
cal = pd.read_parquet(C.CAL_PATH); cal['d'] = pd.to_datetime(cal['cal_date'].astype(str), format='%Y%m%d')
sess = sorted(cal.loc[(cal.is_open == 1) & (cal.d >= '2018-01-02') & (cal.d <= '2026-10-09'), 'd'])
me = cal.loc[(cal.is_open == 1) & (cal.d >= '2018-01-02') & (cal.d <= '2026-10-09'), 'd']
me = list(me.groupby(me.dt.to_period('M')).max())
rd_expect = sorted(set([sess[0]] + me + [sess[-1]]))
S['a_contamination'] = {
    'run_start_et': str(run_start), 'n_files': len(files), 'non_pkl_files': [f for f in files if not f.endswith('.pkl')],
    'n_pkl': len(pk), 'expected_rebal_days': len(rd_expect), 'ckpt_days_match_calendar': [f[:8] for f in pk] == [f'{d:%Y%m%d}' for d in rd_expect],
    'earliest_mtime_et': str(min(mt.values())), 'latest_mtime_et': str(max(mt.values())),
    'earliest_ge_run_start': bool(run_start is not None and min(mt.values()) >= run_start),
    'earliest_ge_0020': bool(min(mt.values()) >= pd.Timestamp('2026-10-18 00:20:00')),
    'mtime_monotonic_in_day_order': all(mt[pk[i]] <= mt[pk[i + 1]] for i in range(len(pk) - 1)),
    'smoke_markers_in_ckpt': smoke_hits,
    'log_smoke_tokens': [l[:120] for l in log_lines if re.search(r'smoke_days|SMOKE_DONE|--smoke', l)],
    'log_header': log_lines[0][:300], 'log_exit': [l for l in log_lines if l.startswith('EXIT=')],
}
print('A', S['a_contamination'], flush=True)

# ---------- (b) 常量 ----------
cl = json.load(open(ROOT + 'output/strategy_optimizer/calib/calib_lambda_risk.json'))['lambda_risk']
ct = {t: json.load(open(ROOT + f'output/strategy_optimizer/calib/calib_lambda_turn_{t}.json'))['lambda_turn'] for t in ('60w', '100w')}
meta = json.load(open(OUT + 'core_weights_meta.json'))
S['b_constants'] = {'calib_lambda_risk': cl, 'calib_lambda_turn': ct, 'meta_lambda_risk': meta['lambda_risk'], 'meta_lambda_turn': meta['lambda_turn'],
    'ok': abs(cl - 117.213) < 5e-4 and abs(meta['lambda_risk'] - cl) < 1e-12 and all(abs(v - 0.6) < 1e-12 for v in ct.values()) and all(abs(v - 0.6) < 1e-12 for v in meta['lambda_turn'].values()),
    'NAME_CAP': C.NAME_CAP, 'W_FLOOR': V.W_FLOOR, 'IND_ACTIVE': C.IND_ACTIVE, 'IND_ABS': C.IND_ABS, 'SIZE_BOX': C.SIZE_BOX, 'BETA_BOX': C.BETA_BOX,
    'SIZE_SLACK_MAX': C.SIZE_SLACK_MAX, 'IND_SLACK_MAX': C.IND_SLACK_MAX, 'NEFF': [C.NEFF_LO, C.NEFF_HI], 'ETF': C.ETF_BALLAST_FRAC, 'CASH_MAX': V.CASH_MAX,
    'mask_sha256_meta': meta['mask_sha256'], 'industry_benchmark_meta': meta.get('industry_benchmark'), 'returns_computed_meta': meta.get('returns_computed')}
print('B', S['b_constants'], flush=True)

# ---------- 独立检查器 ----------
def ctx(D):
    pool = D['alpha'].index; x = D['ln_mcap'].astype(float).reindex(pool)
    z = ((x - x.mean()) / x.std(ddof=0)).fillna(0); mm = (x - x.mean()) ** 2; mm = ((mm - mm.mean()) / mm.std(ddof=0)).fillna(0)
    b = D['betas'].reindex(pool).fillna(1.0); wb = D['wb'].reindex(pool).fillna(0.0); wb = wb / wb.sum()
    ind = pd.Series({i: D['industry'].get(i, '_UNK') for i in pool})
    gb = wb.groupby(ind).sum()
    return dict(pool=pool, z=z, m=mm, b=b, wb=wb, ind=ind, gb=gb, zb=float((wb * z).sum()), mb=float((wb * mm).sum()), bb=float((wb * b).sum()))

def check(w, X, a, budget, size_slack, ind_slack, prelot):
    """w: Series incl. optional 510300; returns dict of exposures and violation magnitudes (>0 = breach)."""
    bal = float(w.get(C.BALLAST, 0.0)); we = w.drop(C.BALLAST, errors='ignore'); we = we[we > 0]
    notpool = [i for i in we.index if i not in X['pool']]
    wep = we.reindex(X['pool']).fillna(0.0); eqs = float(we.sum()); cash = 1.0 - eqs - bal
    sz = float((wep * X['z']).sum() + bal * X['zb'] - X['zb']); md = float((wep * X['m']).sum() + bal * X['mb'] - X['mb'])
    bt = float((wep * X['b']).sum() + bal * X['bb'] - X['bb'])
    G = wep.groupby(X['ind']).sum(); idx = G.index.union(X['gb'].index); G = G.reindex(idx).fillna(0); gbb = X['gb'].reindex(idx).fillna(0) * budget
    act = G - gbb; sbox = C.SIZE_BOX + size_slack; ibox = (C.IND_ACTIVE + ind_slack) * budget
    zero_held = [g for g in idx if G[g] <= 0 and gbb[g] > 0]
    cap = C.NAME_CAP[a] * budget
    r = dict(n=int(len(we)), eq_sum=eqs, ballast=bal, cash=cash, sum_total=eqs + bal,
             maxw=float(we.max()) if len(we) else np.nan, minw=float(we.min()) if len(we) else np.nan,
             size=sz, mid=md, beta=bt, ind_act_max=float(act.abs().max() / budget), ind_abs_max=float(G.max() / budget),
             ind_act_max_eqnorm=float((G / max(eqs, 1e-12) - X['gb'].reindex(idx).fillna(0)).abs().max()), ind_abs_max_eqnorm=float(G.max() / max(eqs, 1e-12)),
             zero_held_ind_max_wb=float(max([gbb[g] / budget for g in zero_held], default=0.0)), n_zero_held_ind=len(zero_held), n_notpool=len(notpool),
             v_size=max(0, abs(sz) - sbox), v_mid=max(0, abs(md) - sbox), v_beta=max(0, abs(bt) - C.BETA_BOX),
             v_ind_rel=max(0, float(act.abs().max()) - ibox), v_ind_abs=max(0, float(G.max()) - C.IND_ABS * budget),
             v_cap=max(0, (float(we.max()) if len(we) else 0) - cap), v_names=int(not (C.NEFF_LO <= len(we) <= C.NEFF_HI)),
             v_cashneg=max(0, -cash), v_slack=max(0, size_slack - C.SIZE_SLACK_MAX) + max(0, ind_slack - C.IND_SLACK_MAX),
             v_floor=max(0, V.W_FLOOR * budget - (float(we.min()) if len(we) else 0)), n_below_floor=int((we < V.W_FLOOR * budget - TOL).sum()),
             v_sum=abs(eqs + bal - 1.0) if prelot else 0.0, v_ballast=abs(bal - (0.20 if budget < 1 else 0.0)))
    return r

def lot_px(d):
    t = pq.read_table(C.DAILY_BASIC, columns=['ts_code', 'trade_date', 'close'],
                      filters=[('trade_date', '>=', d - pd.Timedelta(days=10)), ('trade_date', '<=', d)]).to_pandas()
    t['ts_code'] = t['ts_code'].astype(str); return t.sort_values('trade_date').groupby('ts_code')['close'].last()

# ---------- 主循环 ----------
PQ = {(a, sv): pd.read_parquet(OUT + f'core_{sv}_{"60w" if a == 600000 else "100w"}.parquet') for a in AUMS for sv in SLV}
EXC = pd.read_csv(OUT + 'core_v1_3_lot_exclusions.csv')
rows, exrows, infrows, spot = [], [], [], []
prev_rec_w = {a: None for a in AUMS}; prev_held = {(a, sv): None for a in AUMS for sv in SLV}
random.seed(20261018)
for f in pk:
    d = pd.Timestamp(f[:8]); rec = pickle.load(open(CK + f, 'rb')); win = 'X2' if d >= X2S else 'SEALED'
    D = C.prepare_day(d)
    if D is None:
        for a in AUMS: rows.append(dict(date=f'{d:%Y-%m-%d}', window=win, aum=a, status='NO_DATA_CARRY'))
        continue
    X = ctx(D); px = lot_px(d)
    for a in AUMS:
        lg = rec['log'][a]; st = lg.get('status')
        # (e) 一手剔除独立复算
        cost = pd.Series({i: C.lot_round_rule(i) * px.get(i, np.nan) for i in X['pool']})
        mine = set(cost[cost > C.NAME_CAP[a] * a].index); theirs_ck = {e['instrument'] for e in rec.get('exclusions', {}).get(a, [])}
        theirs_csv = set(EXC[(EXC.date == f'{d:%Y-%m-%d}') & (EXC.aum == a)].instrument)
        exrows.append(dict(date=f'{d:%Y-%m-%d}', window=win, aum=a, n_mine=len(mine), n_ckpt=len(theirs_ck), n_csv=len(theirs_csv), log_n_excluded=lg.get('n_excluded'),
                           miss=len(mine - theirs_ck), extra=len(theirs_ck - mine), csv_eq_ckpt=theirs_csv == theirs_ck, n_nopx=int(cost.isna().sum())))
        for e in rec.get('exclusions', {}).get(a, []):
            if random.random() < 0.01: spot.append(dict(e, my_close=float(px.get(e['instrument'], np.nan)), my_lot=C.lot_round_rule(e['instrument'])))
        base = dict(date=f'{d:%Y-%m-%d}', window=win, aum=a, status=st, K=lg.get('K'), tries=lg.get('tries'), cvx=lg.get('cvx'),
                    size_slack=(lg.get('slack') or {}).get('size_slack'), ind_slack=(lg.get('slack') or {}).get('ind_slack'),
                    one_way_opt=lg.get('one_way'), n_excluded=lg.get('n_excluded'), lot_fail_reason=lg.get('lot_fail_reason'), stage=lg.get('stage'))
        ss = float((lg.get('slack') or {}).get('size_slack') or 0); isl = float((lg.get('slack') or {}).get('ind_slack') or 0)
        if st == 'OK':
            w = rec['w'][a]
            held_bad = sorted(set(w[w > 0].index) & mine)
            r = check(w, X, a, 1.0, ss, isl, True); rows.append(dict(base, stage_chk='prelot', sleeve='solver', held_excluded=len(held_bad), **r))
            for sv in SLV:
                wl = rec['sleeves'][a][sv]['w']
                p = PQ[(a, sv)]; p = p[p.session == f'{d:%Y-%m-%d}'].set_index('instrument').weight
                dpq = float((wl[wl > 0].reindex(p.index.union(wl[wl > 0].index)).fillna(0) - p.reindex(p.index.union(wl[wl > 0].index)).fillna(0)).abs().max())
                lc = max([C.lot_round_rule(i) * px.get(i, 0) for i in wl.index if i != C.BALLAST and wl[i] > 0] + [0])
                r = check(wl, X, a, 1 - BF[sv], ss, isl, False)
                rows.append(dict(base, stage_chk='postlot', sleeve=sv, ckpt_vs_parquet_maxdiff=dpq, max_lot_cost=lc,
                                 lot_flag=rec['sleeves'][a][sv]['lot_flag'], held_excluded=len(set(wl[wl > 0].index) & mine),
                                 turnover_target=(0.5 * float((wl.reindex(wl.index.union(prev_held[(a, sv)].index)).fillna(0) - prev_held[(a, sv)].reindex(wl.index.union(prev_held[(a, sv)].index)).fillna(0)).abs().sum()) if prev_held[(a, sv)] is not None else np.nan), **r))
                prev_held[(a, sv)] = wl
        elif st in ('INFEASIBLE',):
            # (d) 沿用核对 + 原因复现
            carried_same = prev_rec_w[a] is not None and rec['w'][a] is not None and rec['w'][a].equals(prev_rec_w[a])
            w0 = (prev_rec_w[a] if prev_rec_w[a] is not None else D['wb']).reindex(D['alpha'].index).fillna(0.0)
            ws, info = V.solve_v11(D, w0, a, json.load(open(ROOT + 'output/strategy_optimizer/calib/calib_lambda_risk.json'))['lambda_risk'], 0.6, exclude=sorted(mine))
            rep = dict(base, carried_rec_w_equals_prev=carried_same, sleeves_absent=a not in rec.get('sleeves', {}),
                       repro_status=info.get('status'), repro_K=info.get('K'), repro_match_K=info.get('K') == lg.get('K'))
            if ws is not None:
                rep['solver_w_differs_from_carried'] = float((ws.reindex(ws.index.union(prev_rec_w[a].index)).fillna(0) - prev_rec_w[a].reindex(ws.index.union(prev_rec_w[a].index)).fillna(0)).abs().max()) if prev_rec_w[a] is not None else np.nan
                for sv in SLV:
                    sty = V.style_ctx(D, info['slack']['size_slack'], info['slack']['ind_slack'])
                    wl, li = V.lot_round_greedy(ws * (1 - BF[sv]), px.reindex(D['alpha'].index), a, D['industry'], D['wb'].reindex(D['alpha'].index).fillna(0.0), C.NAME_CAP[a], ballast_frac=BF[sv], style=sty, wb_raw=False)
                    r = check(wl, X, a, 1 - BF[sv], info['slack']['size_slack'], info['slack']['ind_slack'], False)
                    cat = [k for k, v in (('names', r['v_names'] > 0), ('size', r['v_size'] > TOL), ('midcap', r['v_mid'] > TOL), ('beta', r['v_beta'] > TOL),
                                          ('ind_rel', r['v_ind_rel'] > TOL), ('ind_abs', r['v_ind_abs'] > TOL)) if v]
                    rep[f'{sv}_repro_flag'] = li['lot_flag']; rep[f'{sv}_repro_flag_matches_log'] = li['lot_flag'] == lg.get(f'lot_flag_{sv}')
                    rep[f'{sv}_viol'] = '+'.join(cat) or 'none'; rep[f'{sv}_n'] = r['n']; rep[f'{sv}_cash'] = r['cash']
            # parquet 当日 = 上期持仓
            for sv in SLV:
                p = PQ[(a, sv)]; p = p[p.session == f'{d:%Y-%m-%d}'].set_index('instrument').weight
                ph = prev_held[(a, sv)]
                rep[f'{sv}_parquet_eq_prevheld'] = ph is not None and float((p.reindex(p.index.union(ph[ph > 0].index)).fillna(0) - ph[ph > 0].reindex(p.index.union(ph[ph > 0].index)).fillna(0)).abs().max()) < 1e-12
            infrows.append(rep); rows.append(dict(base, stage_chk='carry', sleeve='both'))
        else:
            rows.append(dict(base, stage_chk='other', sleeve='?'))
        if rec['w'][a] is not None: prev_rec_w[a] = rec['w'][a]
    print(f[:8], 'rss', rss(), flush=True); del D, X, px
E = pd.DataFrame(rows); EX = pd.DataFrame(exrows); IF = pd.DataFrame(infrows)
E.to_csv(AUD + 'arch_core_v1_3_resign_expo.csv', index=False); EX.to_csv(AUD + 'arch_core_v1_3_resign_excl.csv', index=False)
IF.to_csv(AUD + 'arch_core_v1_3_resign_infeas.csv', index=False); pd.DataFrame(spot).to_csv(AUD + 'arch_core_v1_3_resign_excl_spot.csv', index=False)

# ---------- parquet 日度展开：调仓间持仓不变 ----------
flat_bad = {}
for (a, sv), p in PQ.items():
    rdset = set(p.loc[p.is_rebalance_day, 'session']); g = {s: x.set_index('instrument').weight for s, x in p.groupby('session')}
    last = None; bad = 0
    for s in sorted(g):
        if s in rdset: last = g[s]; continue
        if last is None or not g[s].sort_index().equals(last.sort_index()): bad += 1
    flat_bad[f'{a}_{sv}'] = bad
S['parquet_flat_between_rebal_violations'] = flat_bad

viol = ['v_size', 'v_mid', 'v_beta', 'v_ind_rel', 'v_ind_abs', 'v_cap', 'v_names', 'v_cashneg', 'v_slack', 'v_floor', 'v_sum', 'v_ballast']
for stg in ('prelot', 'postlot'):
    x = E[E.stage_chk == stg]
    S[f'c_{stg}'] = {'n_rows': len(x), **{v: {'n_gt_tol': int((x[v] > TOL).sum()), 'max': float(x[v].max())} for v in viol},
                     'abs_size_max': float(x['size'].abs().max()), 'abs_mid_max': float(x['mid'].abs().max()), 'abs_beta_max': float(x['beta'].abs().max()),
                     'ind_act_max': float(x.ind_act_max.max()), 'ind_abs_max': float(x.ind_abs_max.max()), 'zero_held_ind_max_wb': float(x.zero_held_ind_max_wb.max()),
                     'n_range': [int(x.n.min()), int(x.n.max())], 'held_excluded_total': int(x.held_excluded.sum()), 'n_notpool_total': int(x.n_notpool.sum())}
    if stg == 'postlot':
        S['c_postlot'].update({'ckpt_vs_parquet_maxdiff': float(x.ckpt_vs_parquet_maxdiff.max()), 'max_lot_cost_over_cap': int((x.max_lot_cost > x.aum.map(lambda a: C.NAME_CAP[a] * a) + 1e-6).sum()),
                               'eqnorm_ind_abs_gt20_rows': int((x.ind_abs_max_eqnorm > 0.20 + TOL).sum()), 'eqnorm_ind_abs_max': float(x.ind_abs_max_eqnorm.max()),
                               'eqnorm_ind_act_gt_box_rows': int((x.ind_act_max_eqnorm > 0.08 + x.ind_slack.fillna(0) + TOL).sum()), 'eqnorm_ind_act_max': float(x.ind_act_max_eqnorm.max()),
                               'below_floor_rows': int((x.n_below_floor > 0).sum()), 'below_floor_names': int(x.n_below_floor.sum()), 'minw_min': float(x.minw.min())})
S['e_exclusions'] = {'rows_ckpt_total': int(EX.n_ckpt.sum()), 'rows_mine_total': int(EX.n_mine.sum()), 'miss': int(EX.miss.sum()), 'extra': int(EX.extra.sum()),
                     'csv_eq_ckpt_all': bool(EX.csv_eq_ckpt.all()), 'log_n_excluded_eq': bool((EX.log_n_excluded.fillna(-1) == EX.n_ckpt).all()), 'n_spot': len(spot),
                     'spot_close_mismatch': int(sum(abs(s['close'] - s['my_close']) > 1e-9 for s in spot)), 'spot_lot_mismatch': int(sum(s['lot'] != s['my_lot'] for s in spot))}
S['d_infeasible'] = {'n': len(IF), 'all_carried_equal_prev': bool(IF.carried_rec_w_equals_prev.all()) if len(IF) else None,
                     'all_sleeves_absent': bool(IF.sleeves_absent.all()) if len(IF) else None,
                     'parquet_eq_prevheld_all': bool(all(IF[f'{sv}_parquet_eq_prevheld'].all() for sv in SLV)) if len(IF) else None,
                     'repro_K_match': int(IF.repro_match_K.sum()) if len(IF) else 0,
                     'repro_flag_match': {sv: int(IF[f'{sv}_repro_flag_matches_log'].sum()) for sv in SLV} if len(IF) else {}}
S['peak_rss_mb'] = rss()
json.dump(S, open(AUD + 'arch_core_v1_3_resign_summary.json', 'w'), ensure_ascii=False, indent=1, default=str)
print('RESIGN_CHECK_DONE rss', rss())
