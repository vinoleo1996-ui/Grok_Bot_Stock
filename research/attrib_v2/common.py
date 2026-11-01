"""Shared loaders + cost-aware long-only simulator (research-grade, promotion_approved=false)."""
import json, hashlib
import numpy as np, pandas as pd
P = '/workspace/QuantLab/output/research_attrib_v2/panels'
OUT = '/workspace/QuantLab/output/research_attrib_v2'
START, END = pd.Timestamp('2024-06-03'), pd.Timestamp('2026-10-09')
CAP0 = 600000.0
COMM_BP, COMM_MIN, SLIP_BP, STAMP_BP, MIN_TRADE = 2.5, 5.0, 5.0, 5.0, 2000.0

def load():
    D = {k: pd.read_parquet(f'{P}/{k}.parquet') for k in ['close','ret','amount','turnover','trad','lu','ld','st']}
    cols = D['close'].columns
    for k in ['circ_mv','pe_ttm','pb','turnover_rate']:
        D[k] = pd.read_parquet(f'{P}/db_{k}.parquet').reindex(columns=cols)
    D['etf'] = pd.read_parquet(f'{P}/etf510300.parquet')['ret'].astype('float64')
    return D

def rebal_dates():
    log = json.load(open('/workspace/QuantLab/output/strategy_paper_costs/full_d1_turn/rebalance_log.json'))
    return [pd.Timestamp(r['session']) for r in log]

def industry_on(day, cols, _cache={}):
    if 'sw' not in _cache:
        _cache['sw'] = pd.read_parquet('/workspace/QuantLab/data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet')
    s = _cache['sw']
    m = s[(s.in_date <= day) & (s.out_date.isna() | (s.out_date > day))].drop_duplicates('instrument_id', keep='last')
    return m.set_index('instrument_id')['sw_code'].reindex(cols)

def features(D):
    """PIT features as of each close (only info <= that day)."""
    amt = D['amount']; F = {}
    F['hist'] = D['close'].notna().cumsum()
    F['amt20_med'] = amt.rolling(20, min_periods=10).median()
    pos = amt.where(amt > 0)
    F['adv60'] = pos.rolling(60, min_periods=40).mean()
    F['cap20'] = D['circ_mv'].rolling(20, min_periods=10).mean() * 1e4  # 万元 -> CNY
    return F

def universe_d1(day, D, F):
    """Full-D1 proxy: listed>=120 sessions, not ST, trading, 20d median amount>=3e7, drop bottom 30% float cap."""
    h = F['hist'].loc[day]; ok = (h >= 120) & (D['st'].loc[day] != 1) & (D['trad'].loc[day] == 1) & (F['amt20_med'].loc[day] >= 3e7)
    cap = F['cap20'].loc[day].where(ok).dropna()
    return cap[cap >= cap.quantile(0.30)].index

def universe_broad(day, D, F, min_adv=5e6, min_hist=120):
    h = F['hist'].loc[day]; ok = (h >= min_hist) & (D['st'].loc[day] != 1) & (D['trad'].loc[day] == 1) & (F['adv60'].loc[day] >= min_adv) & F['cap20'].loc[day].notna()
    return ok[ok].index

def simulate(targets, D, etf_col=False, zero_on_block=False, name='', capital=None):
    """targets: {rebal_day: pd.Series weights (sum<=1)} ; weights drift between rebalances.
    Trades at rebal-day close; buy blocked on limit-up/halt/ST, sell blocked on limit-down/halt.
    Costs: commission max(2.5bp,5CNY)/order + 5bp slippage + 5bp stamp on stock sells; trades<2000 CNY skipped.
    etf_col: if True, key '510300' in targets is the ETF (no stamp, never blocked)."""
    R = D['ret'].loc[START:END]; days = R.index; cols = list(R.columns) + ['510300']
    idx = {c: i for i, c in enumerate(cols)}
    Rv = np.nan_to_num(R.to_numpy(np.float64), nan=0.0)
    Rv = np.column_stack([Rv, D['etf'].reindex(days).fillna(0).to_numpy()])
    lu = D['lu'].loc[START:END].to_numpy() == 1; ld = D['ld'].loc[START:END].to_numpy() == 1
    halt = D['trad'].loc[START:END].to_numpy() != 1; st = D['st'].loc[START:END].to_numpy() == 1
    pad = np.zeros((len(days), 1), bool)
    lu, ld, halt, st = [np.hstack([a, pad]) for a in (lu, ld, halt, st)]
    blocked = lu | ld | halt
    CAPX = capital or CAP0
    hold = np.zeros(len(cols)); cash = CAPX
    navs, tot_cost, turns, rets = [], 0.0, [], []
    for t, d in enumerate(days):
        if t > 0:
            r = Rv[t].copy()
            if zero_on_block: r[blocked[t]] = 0.0
            hold = hold * (1 + r)
        nav = hold.sum() + cash
        if d in targets:
            w = np.zeros(len(cols)); tg = targets[d]
            for c, v in tg.items():
                if c in idx: w[idx[c]] = v
            want = w * nav; delta = want - hold
            buy_ok = ~(lu[t] | halt[t] | st[t]); sell_ok = ~(ld[t] | halt[t])
            delta[(delta > 0) & ~buy_ok] = 0; delta[(delta < 0) & ~sell_ok] = 0
            delta[np.abs(delta) < MIN_TRADE] = 0
            nz = delta != 0
            comm = np.maximum(np.abs(delta[nz]) * COMM_BP / 1e4, COMM_MIN).sum()
            slip = np.abs(delta[nz]).sum() * SLIP_BP / 1e4
            sells = delta < 0; sells[-1] = False
            stamp = -delta[sells].sum() * STAMP_BP / 1e4
            cost = comm + slip + stamp
            turns.append(np.abs(delta).sum() / 2 / nav)
            hold = hold + delta; cash = cash - delta.sum() - cost; tot_cost += cost
            nav = hold.sum() + cash
        navs.append(nav)
    nav = pd.Series(navs, index=days) / CAPX
    return nav, tot_cost * CAP0 / CAPX, float(np.mean(turns)) if turns else 0.0

def metrics(nav, tot_cost=np.nan, turn=np.nan):
    r = nav.pct_change().fillna(nav.iloc[0] - 1)
    yrs = len(nav) / 252.0
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    mdd = (nav / nav.cummax() - 1).min()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    return dict(cagr=float(cagr), total=float(nav.iloc[-1] - 1), mdd=float(mdd), sharpe=float(sh),
                vol=float(r.std() * np.sqrt(252)), turnover_mean_per_rebal=float(turn),
                cost_cny=float(tot_cost), cost_frac=float(tot_cost / CAP0))
