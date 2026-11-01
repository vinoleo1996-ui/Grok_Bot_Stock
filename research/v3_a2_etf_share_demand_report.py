# V3-A2 ETF share×weight demand report arm (prereg revision B). Research only.
# Does NOT re-run sealed T1/T2 tests. Reuses output/alpha/V3_A2_SEALED/events.csv.
import os, json, hashlib, resource, re
import numpy as np
import pandas as pd

ROOT = '/workspace/QuantLab'
OUT = ROOT + '/output/alpha/V3_A2_ETF_SHARE_DEMAND'
PRE = ROOT + '/docs/prereg/V3_A2_INDEX_REBAL_MIGRATION.md'
PSHA = hashlib.sha256(open(PRE, 'rb').read()).hexdigest()
mem = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
os.makedirs(OUT, exist_ok=True)

basic = pd.read_parquet(ROOT + '/data/v2/etf/etf_basic.parquet')
excl = re.compile(r'增强|联接|质量|价值|成长|红利|ESG|自由现金流|等权重|行业|主题|非银行|金融地产|低波|医药|信息|原料|工业')

def pick(df, bench_pat, label):
    m = df[df.category == '宽基'].copy()
    m = m[m.benchmark.fillna('').str.contains(bench_pat, regex=True)]
    m = m[~m.name.fillna('').str.contains(excl)]
    m = m[~m.benchmark.fillna('').str.contains(excl)]
    return m.assign(tracker=label)[['ts_code', 'name', 'benchmark', 'list_date', 'delist_date', 'tracker']]

t300 = pick(basic, r'沪深300指数', 'CSI300')
t500 = pick(basic, r'中证500指数|中证小盘500指数', 'CSI500')
for code, lab in [('510300.SH', 'CSI300'), ('159919.SZ', 'CSI300'),
                  ('510500.SH', 'CSI500'), ('159922.SZ', 'CSI500')]:
    sub = t300 if lab == 'CSI300' else t500
    if code not in set(sub.ts_code):
        row = basic[basic.ts_code == code]
        if len(row):
            extra = row.assign(tracker=lab)[['ts_code', 'name', 'benchmark', 'list_date', 'delist_date', 'tracker']]
            if lab == 'CSI300':
                t300 = pd.concat([t300, extra], ignore_index=True)
            else:
                t500 = pd.concat([t500, extra], ignore_index=True)

trackers = pd.concat([t300, t500], ignore_index=True).drop_duplicates('ts_code')
trackers.to_csv(OUT + '/tracker_universe.csv', index=False)
print('trackers', trackers.groupby('tracker').size().to_dict(), 'mem', mem())

codes = trackers.ts_code.tolist()
etf = pd.read_parquet(
    ROOT + '/data/v2/etf/share_pit/etf_share_flow_pit_all.parquet',
    columns=['ts_code', 'trade_date', 'share_wan', 'unit_nav', 'available_at'],
)
etf = etf[etf.ts_code.isin(codes)].copy()
etf['aum_wan'] = etf['share_wan'] * etf['unit_nav']
etf = etf.merge(trackers[['ts_code', 'tracker']], on='ts_code', how='left')
etf = etf.dropna(subset=['aum_wan', 'available_at']).sort_values(['tracker', 'available_at'])
aum_daily = (etf.groupby(['tracker', 'available_at'], as_index=False)['aum_wan'].sum()
             .sort_values(['tracker', 'available_at']))
aum_daily.to_csv(OUT + '/aum_tracker_available_at.csv', index=False)

cal = pd.read_parquet(ROOT + '/data/v2/index_members/csi_review_calendar.parquet')
cal['ann_avail'] = pd.to_datetime(cal['available_at'])

def aum_asof(tracker, ts):
    g = aum_daily[aum_daily.tracker == tracker]
    hit = g[g.available_at <= ts]
    return float(hit.iloc[-1].aum_wan) if len(hit) else np.nan

rev_aum = []
for _, c in cal.iterrows():
    ts = c.ann_avail
    def n_asof(tr):
        sub = etf[(etf.tracker == tr) & (etf.available_at <= ts)]
        return int(sub.sort_values('available_at').groupby('ts_code').tail(1).shape[0])
    rev_aum.append(dict(
        review=c.review, ann_avail=ts,
        aum300_wan=aum_asof('CSI300', ts), aum500_wan=aum_asof('CSI500', ts),
        n300=n_asof('CSI300'), n500=n_asof('CSI500'),
    ))
rev_aum = pd.DataFrame(rev_aum)
rev_aum.to_csv(OUT + '/review_tracker_aum.csv', index=False)

iw = pd.read_parquet(
    ROOT + '/data/v2/index_members/index_weight_csi300_500_1000.parquet',
    columns=['index_code', 'con_code', 'trade_date', 'weight'],
)
iw = iw[iw.index_code.isin(['000300.SH', '000905.SH'])].copy()
iw['snap'] = pd.to_datetime(iw.trade_date.astype(str))
iw['inst'] = iw.con_code.str[-2:].str.lower() + '.' + iw.con_code.str[:6]
wmap = {(r.index_code, r.inst, r.snap): float(r.weight) for r in iw.itertuples()}
snaps = sorted(iw.snap.unique())

E = pd.read_csv(ROOT + '/output/alpha/V3_A2_SEALED/events.csv')
E['entry'] = pd.to_datetime(E.entry)
E['exit'] = pd.to_datetime(E.exit)
E0 = E[E.exit_rule == 'eff'].copy()

rows = []
for (rv, arm), g in E0.groupby(['review', 'arm']):
    ra = rev_aum[rev_aum.review == rv]
    if ra.empty:
        continue
    a300 = float(ra.aum300_wan.iloc[0]); a500 = float(ra.aum500_wan.iloc[0])
    entry = g.entry.iloc[0]; eff = g.exit.iloc[0]
    old_snaps = [s for s in snaps if s < entry]
    new_snaps = [s for s in snaps if s >= eff]
    if not old_snaps or not new_snaps or not np.isfinite(a300) or not np.isfinite(a500):
        continue
    snap_old, snap_new = old_snaps[-1], new_snaps[0]
    for _, r in g.iterrows():
        inst = r['inst']
        adv = float(r['adv_in']) if np.isfinite(r['adv_in']) and r['adv_in'] > 0 else np.nan
        w300_old = wmap.get(('000300.SH', inst, snap_old), 0.0)
        w500_old = wmap.get(('000905.SH', inst, snap_old), 0.0)
        w300_new = wmap.get(('000300.SH', inst, snap_new), 0.0)
        w500_new = wmap.get(('000905.SH', inst, snap_new), 0.0)
        if 'T1' in arm:
            dp_wan = (w300_new / 100.0) * a300 - (w500_old / 100.0) * a500
        else:
            dp_wan = (w500_new / 100.0) * a500 - (w300_old / 100.0) * a300
        demand = (dp_wan * 1e4 / adv) if np.isfinite(adv) else np.nan
        rows.append(dict(
            review=rv, arm=arm, inst=inst, window=r['window'],
            xs=float(r['xs']),
            demand_proxy=float(r['demand_proxy']) if pd.notna(r['demand_proxy']) else np.nan,
            demand_share=demand, delta_passive_wan=dp_wan, adv_in=adv,
            aum300_wan=a300, aum500_wan=a500,
            w300_old=w300_old, w500_old=w500_old, w300_new=w300_new, w500_new=w500_new,
            snap_old=str(snap_old.date()), snap_new=str(snap_new.date()),
        ))

D = pd.DataFrame(rows)
D.to_csv(OUT + '/event_demand_share.csv', index=False)

def tercile_table(df, col, label):
    q = df.dropna(subset=[col, 'xs']).copy()
    if q.empty:
        return pd.DataFrame(columns=['arm', 'terc', 'mean_xs', 'count', 'mean_demand', 'demand_kind'])
    q['terc'] = q.groupby('arm')[col].transform(lambda s: pd.qcut(s.rank(method='first'), 3, labels=False))
    t = (q.groupby(['arm', 'terc'], as_index=False)
           .agg(mean_xs=('xs', 'mean'), count=('xs', 'size'), mean_demand=(col, 'mean')))
    t['demand_kind'] = label
    return t

sealed = D[D.window == 'sealed']
confirm = D[D.window == 'confirm']
t_share_s = tercile_table(sealed, 'demand_share', 'share_weight')
t_proxy_s = tercile_table(sealed, 'demand_proxy', 'mcap_proxy')
t_share_c = tercile_table(confirm, 'demand_share', 'share_weight')
t_proxy_c = tercile_table(confirm, 'demand_proxy', 'mcap_proxy')
pd.read_csv(ROOT + '/output/alpha/V3_A2_SEALED/demand_proxy_terciles.csv').to_csv(
    OUT + '/demand_proxy_terciles_ref.csv', index=False)
pd.concat([t_share_s, t_proxy_s], ignore_index=True).to_csv(OUT + '/demand_terciles_sealed.csv', index=False)
pd.concat([t_share_c, t_proxy_c], ignore_index=True).to_csv(OUT + '/demand_terciles_confirm.csv', index=False)

def mono_note(t, arm):
    sub = t[(t.arm == arm) & (t.demand_kind == 'share_weight')].sort_values('terc')
    if len(sub) < 3:
        return 'insufficient'
    m = [round(float(x), 4) for x in sub['mean_xs'].tolist()]
    up = all(m[i] <= m[i + 1] + 1e-12 for i in range(len(m) - 1))
    down = all(m[i] >= m[i + 1] - 1e-12 for i in range(len(m) - 1))
    if up:
        return f'monotone_up {m}'
    if down:
        return f'monotone_down {m}'
    return f'non_monotone {m}'

notes = {
    'T1_sealed': mono_note(t_share_s, 'A2_T1_MIGRATE_IN_300'),
    'T2_sealed': mono_note(t_share_s, 'A2_T2_MIGRATE_OUT_300'),
    'T1_confirm': mono_note(t_share_c, 'A2_T1_MIGRATE_IN_300'),
    'T2_confirm': mono_note(t_share_c, 'A2_T2_MIGRATE_OUT_300'),
}
corr = {}
for arm, g in sealed.groupby('arm'):
    gg = g.dropna(subset=['demand_share', 'demand_proxy'])
    corr[arm] = float(gg['demand_share'].corr(gg['demand_proxy'])) if len(gg) > 3 else float('nan')

stats = sealed.groupby('arm').agg(
    n=('demand_share', 'size'), demand_mean=('demand_share', 'mean'),
    demand_med=('demand_share', 'median'), xs_mean=('xs', 'mean'),
    frac_demand_pos=('demand_share', lambda s: float((s > 0).mean())),
).reset_index()
stats.to_csv(OUT + '/demand_summary_sealed.csv', index=False)
sealed.groupby(['arm', 'review']).agg(xs=('xs', 'mean'), demand=('demand_share', 'mean')).reset_index().to_csv(
    OUT + '/by_review_sealed.csv', index=False)

meta = dict(
    prereg_sha256=PSHA, promotion_approved=False, research_only=True,
    sealed_T1_T2_fail_unchanged=True, by_not_reopened=True, iopv_missing=True,
    n_trackers_csi300=int((trackers.tracker == 'CSI300').sum()),
    n_trackers_csi500=int((trackers.tracker == 'CSI500').sum()),
    n_events_demand=int(len(D)), monotonicity=notes,
    corr_share_vs_proxy_sealed=corr, maxrss_MB=mem(),
)
json.dump(meta, open(OUT + '/results.json', 'w'), indent=1, ensure_ascii=False)
print('SEALED share:\n', t_share_s.to_string(index=False))
print('mono', notes, 'maxrss', mem())
