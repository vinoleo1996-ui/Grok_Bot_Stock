"""Benchmark arms on Full D1 window / cost knobs / rebalance grid (research only)."""
import sys, json, hashlib, math, resource
sys.path.insert(0, '/workspace/QuantLab/research/attrib_v2')
import numpy as np, pandas as pd
from common import *
D = load(); F = features(D); RB = rebal_dates()
out = {}; navs = {}
def run(name, targets, **kw):
    nav, c, t = simulate(targets, D, **kw); navs[name] = nav; out[name] = metrics(nav, c, t)
    out[name]['avg_names'] = float(np.mean([len(v) for v in targets.values()]))
    print(name, {k: round(v, 4) for k, v in out[name].items()}, flush=True)
# (a) 510300 buy-and-hold (one buy at start)
run('a_510300_buyhold', {RB[0]: pd.Series({'510300': 1.0})})
# (b) EW Full-D1-proxy tradable universe, rebalanced every grid date
tb = {}; ud = {}
for d in RB:
    u = universe_d1(d, D, F); ud[str(d.date())] = len(u); tb[d] = pd.Series(1.0 / len(u), index=u)
BIG = 1e9  # wide EW baskets cannot be held at 600k (each line < 2000 CNY min trade); run at 1e9 notional, cost reported scaled to 600k-equivalent fraction
run('b_ew_d1_universe', tb, capital=BIG)
run('b_ew_d1_universe_zero_on_block', tb, capital=BIG, zero_on_block=True)
# (c1) M2-like: cap band ranks 3001-5000 (desc), ADV60>=5m, hist>=253, not ST; tier (pe_ttm>0 & 0<pb<=3) then seeded random; keep holdings in top150; <=15/industry; 50 names; 90% gross
def prio(seed, code): return int(hashlib.sha256(f'{seed}:{code}'.encode()).hexdigest()[:12], 16)
def m2_targets(seed=0, band='absolute'):
    tg = {}; cur = []
    for d in RB:
        el = universe_broad(d, D, F, min_adv=5e6, min_hist=253)
        cap = F['cap20'].loc[d, el].sort_values(ascending=False)
        if band == 'absolute': pool = cap.iloc[3000:5000].index
        else: pool = cap.iloc[math.ceil(0.6 * len(cap)):].index
        pe = D['pe_ttm'].loc[d, pool]; pb = D['pb'].loc[d, pool]
        tier = ((pe > 0) & (pb > 0) & (pb <= 3)).astype(int)
        order = sorted(pool, key=lambda c: (-tier[c], prio(seed, c)))
        top150 = set(order[:150]); ind = industry_on(d, order)
        keep = [c for c in cur if c in top150]
        sel, cnt = [], {}
        for c in keep + [c for c in order if c not in keep]:
            g = ind.get(c, 'NA'); g = 'NA' if not isinstance(g, str) else g
            if cnt.get(g, 0) >= 15: continue
            sel.append(c); cnt[g] = cnt.get(g, 0) + 1
            if len(sel) == 50: break
        cur = sel; tg[d] = pd.Series(0.9 / len(sel), index=sel)
    return tg, len(pool)
tg, npool = m2_targets(0, 'absolute'); out_pool = npool
run('c1_m2like_capband3001_5000_50', tg)
tg2, _ = m2_targets(0, 'relative'); run('c2_m2like_bottom40pct_50', tg2)
# (c3) pure smallest 50 by 20d float cap, ADV60>=5m, hist>=253, EW 100%
tg3 = {}
for d in RB:
    el = universe_broad(d, D, F, min_adv=5e6, min_hist=253)
    s = F['cap20'].loc[d, el].nsmallest(50).index; tg3[d] = pd.Series(1 / 50, index=s)
run('c3_smallest50_cap', tg3)
run('c3_smallest50_cap_zero_on_block', tg3, zero_on_block=True)
# (c4) lowest-ADV 50 (ADV60>=5m)
tg4 = {}
for d in RB:
    el = universe_broad(d, D, F, min_adv=5e6, min_hist=253)
    s = F['adv60'].loc[d, el].nsmallest(50).index; tg4[d] = pd.Series(1 / 50, index=s)
run('c4_lowadv50', tg4)
# (d) cap quintiles on broad universe (ADV60>=5m, hist>=120, not ST), EW
for q in range(5):
    tq = {}
    for d in RB:
        el = universe_broad(d, D, F)
        cap = F['cap20'].loc[d, el]; rk = cap.rank(pct=True)
        s = rk[(rk > q / 5) & (rk <= (q + 1) / 5)].index; tq[d] = pd.Series(1 / len(s), index=s)
    run(f'd_capQ{q+1}' + ('_smallest' if q == 0 else '_largest' if q == 4 else ''), tq, capital=BIG)
pd.DataFrame(navs).to_csv(f'{OUT}/benchmarks_nav.csv')
json.dump({'promotion_approved': False, 'research_only': True, 'window': [str(START.date()), str(END.date())],
           'rebalances': len(RB), 'cost_knobs': dict(commission_bps=COMM_BP, min_cny=COMM_MIN, slippage_bps=SLIP_BP, stamp_sell_bps=STAMP_BP, min_trade_cny=MIN_TRADE, capital=CAP0),
           'd1_proxy_universe_size': ud, 'm2_last_pool_size': out_pool, 'arms': out,
           'peak_rss_gb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6}, open(f'{OUT}/benchmarks.json', 'w'), indent=1, ensure_ascii=False)
