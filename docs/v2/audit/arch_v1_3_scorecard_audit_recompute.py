"""Arch read-only audit: independent metrics from NAV files + suspended/delisted holding event counts. No engine runs."""
import pandas as pd, numpy as np, resource
from quantlab.data.v2_readers import load_merged_panel
X2=('2024-06-03','2026-10-09')
O='output/strategy_optimizer/core_x2/'
cols={}
for t,aum in (('60w',600000),('100w',1000000)):
  for sl in ('equity80_etf20_510300','equity_100'):
    cols[('A',t,sl)]=O+f'book_smoke_v1_3_{sl}_{t}/aum_{aum}/X2/BOOK'
    if sl=='equity_100':
      for c in 'BC': cols[(c,t,sl)]=O+f't6_native_eq100/{c}_{aum}/aum_{aum}/X2/BOOK'
    else:
      cols[('B',t,sl)]=f'output/v3/book_smoke_g1g5_capacity_adv_x2/aum_{aum}/X2/BOOK'
      cols[('C',t,sl)]=f'output/strategy_hiliq/capadv_x2/aum_{aum}/X2/BOOK'
def metr(p):
  d=pd.read_csv(p+'/nav.csv');s=pd.Series(d['nav'].astype(float).values,index=pd.to_datetime(d.iloc[:,0].astype(str).str[:10])).sort_index().loc[X2[0]:X2[1]]
  r=s.pct_change().dropna()
  nav=np.r_[1.0,(1+r).cumprod().values]
  n=len(r);cagr=nav[-1]**(244/n)-1
  mdd=(nav/np.maximum.accumulate(nav)-1).min()
  m=(1+r).groupby(r.index.to_period('M')).prod()-1
  return dict(start=str(s.index[0].date()),end=str(s.index[-1].date()),n=n,cagr=cagr,mdd=mdd,calmar=cagr/abs(mdd),
    sharpe=r.mean()/r.std(ddof=1)*np.sqrt(244),daily_win=(r>0).mean(),monthly_win=(m>0).mean(),months=len(m))
rows=[];panel={}
def pan(c):
  if c not in panel:
    try: f=load_merged_panel(c).frame; panel[c]=f.set_index(pd.to_datetime(f.event_time))[['close','volume']]
    except Exception: panel[c]=None
  return panel[c]
for k,p in cols.items():
  r=metr(p); r.update(col=k[0],tier=k[1],sleeve=k[2])
  w=pd.read_parquet(p+'/actual_weights.parquet');w=w[(w.weight>1e-6)&(w.instrument_id!='sh.510300')].copy()
  w['session']=pd.to_datetime(w.session)
  sus=0;dl=0;dlc=set();susc=set();miss=set()
  for c,g in w.groupby('instrument_id'):
    f=pan(c)
    if f is None: miss.add(c);continue
    last=f.index.max();ff=f.reindex(g.session.values)
    after=(g.session>last).values
    dl+=int(after.sum())
    if after.any(): dlc.add(c)
    s=((ff.close.isna()|(ff.volume<=0)).values)&(~after)
    sus+=int(s.sum())
    if s.any(): susc.add(c)
  r.update(held_name_days=len(w),susp_name_days=sus,susp_codes=len(susc),post_lastbar_name_days=dl,post_lastbar_codes=';'.join(sorted(dlc)),no_panel=';'.join(sorted(miss)))
  rows.append(r)
df=pd.DataFrame(rows);pd.set_option('display.width',250);pd.set_option('display.max_columns',30)
print(df[['col','tier','sleeve','start','end','n','cagr','mdd','calmar','sharpe','daily_win','monthly_win','months']].round(4).to_string())
print(df[['col','tier','sleeve','held_name_days','susp_name_days','susp_codes','post_lastbar_name_days','post_lastbar_codes','no_panel']].to_string())
df.to_csv('docs/v2/audit/arch_v1_3_scorecard_audit_recompute.csv',index=False)
print('peak_rss_mb',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
