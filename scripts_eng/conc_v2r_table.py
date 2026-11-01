import json,pandas as pd,os
O='output/v3/'
def k(d,c,arm='BOOK'):
    p=f'{O}{d}/book_smoke_summary.json'
    if not os.path.exists(p): return None
    s=json.load(open(p))['by_capital'].get(str(c))
    if not s or f'X2/{arm}' not in s: return None
    r=dict(s[f'X2/{arm}']); n=pd.read_csv(f'{O}{d}/aum_{c}/X2/{arm}/nav.csv',parse_dates=['_et']).set_index('_et').nav
    y={}; prev=n.iloc[0]
    for yr in (2024,2025,2026):
        e=n[n.index.year==yr].iloc[-1]; y[yr]=e/prev-1; prev=e
    r['yr']=y; return r
def ballast(f):
    d=pd.read_parquet(f); return d[d.instrument_id=='sh.510300'].groupby('session').weight.sum().reindex(d.session.unique()).fillna(0).mean()
TR={600000:(0.1382,-0.1007),1000000:(0.1223,-0.1162)}
trc15={c:k(f'book_smoke_conc_v2r_trunk_{t}_c15_x2',c) for c,t in [(600000,'60w'),(1000000,'100w')]}
rows=[];fl=[]
def f(x): return f'{x*100:.2f}%'
def add(name,d,c,base_d,wfile,note=''):
    r=k(d,c); r15=k(d.replace('_x2','_c15_x2'),c); b=k(base_d,c) if base_d else None; tr=TR[c]
    gate='过' if 0.12<=r['cagr']<=0.18 and r['mdd']>=-0.28 else '不过'
    vb='—' if not b else f"{(r['cagr']-b['cagr'])*100:+.2f}pp / MDD {(r['mdd']-b['mdd'])*100:+.2f}pp"
    vt='胜' if r['cagr']>tr[0] and r['mdd']>tr[1] else '否'
    t15=trc15[c]; c15s=f"{f(r15['cagr'])}（{'>' if r15['cagr']>t15['cagr'] else '≤'}主干×1.5 {f(t15['cagr'])}）"
    y=' / '.join(f"{v*100:+.2f}" for v in r['yr'].values())
    rows.append(f"| {name}{note} | {c//10000}万 | {f(r['cagr'])} | {f(r['mdd'])} | {r['sharpe']:.2f} | {y} | {c15s} | {gate} | {vb} | {vt} | {ballast(wfile)*100:.1f}% |")
    if b:
        for yr in r['yr']:
            dd=r['yr'][yr]-b['yr'][yr]
            if abs(dd)>0.03: fl.append(f"{name} {c//10000}万 {yr}: 相对基准 {dd*100:+.2f}pp")
    return r,b,r15
R='output/small_aum_concentration/v2_robust/'; V='output/small_aum_concentration/v2/'
res={}
for bk in ['B1_equal','B4_50_25_25']:
  for t,c in [('60w',600000),('100w',1000000)]:
    base=f'book_smoke_conc_v2_B_{bk}_topN_{t}_x2'
    add(f'base {bk}',base.replace('_x2',''),c,None,f'{V}B_{bk}_topN_{t}.parquet') if False else None
    # base row (c15 lives in v2r dir)
    r=k(base,c); r15=k(f'book_smoke_conc_v2r_base_{bk}_{t}_c15_x2',c); t15=trc15[c]
    y=' / '.join(f"{v*100:+.2f}" for v in r['yr'].values())
    rows.append(f"| **基准 v2 {bk}** | {c//10000}万 | {f(r['cagr'])} | {f(r['mdd'])} | {r['sharpe']:.2f} | {y} | {f(r15['cagr'])}（{'>' if r15['cagr']>t15['cagr'] else '≤'}主干×1.5 {f(t15['cagr'])}） | {'过' if 0.12<=r['cagr']<=0.18 and r['mdd']>=-0.28 else '不过'} | — | {'胜' if r['cagr']>TR[c][0] and r['mdd']>TR[c][1] else '否'} | {ballast(f'{V}B_{bk}_topN_{t}.parquet')*100:.1f}% |")
    for v in ['Nminus','Nplus']:
      res[(v,bk,t)]=add(f'{v} {bk}',f'book_smoke_conc_v2r_{v}_{bk}_{t}_x2',c,base,f'{R}{v}_{bk}_topN_{t}.parquet')
    cap_bad = not (bk=='B1_equal' and t=='100w')
    res[('drop',bk,t)]=add(f'drop3hp {bk}',f'book_smoke_conc_v2r_drop3hp_{bk}_{t}_x2',c,base,f'{R}drop3hp_B_{bk}_topN_{t}.parquet',' ⚠cap_ok=false' if cap_bad else '')
tr={c:k('book_smoke_g1g5_capacity_adv_x2',c) for c in TR}
for t,c in [('60w',600000),('100w',1000000)]:
    r=tr[c]; t15=trc15[c]; y=' / '.join(f"{v*100:+.2f}" for v in r['yr'].values())
    rows.append(f"| **主干 capacity_adv（未集中）** | {c//10000}万 | {f(r['cagr'])} | {f(r['mdd'])} | {r['sharpe']:.2f} | {y} | {f(t15['cagr'])} | — | — | — | {ballast('output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet')*100:.1f}% |")
    add('CORE 集中化',f'book_smoke_conc_v2r_CORE_{t}_x2',c,'book_smoke_g1g5_capacity_adv_x2',f'{V}conc_CORE_{t}.parquet')
hdr="| 臂 | AUM | CAGR | MDD | Sharpe | 分年 2024(6/3起)/2025/2026(至10/9) % | 成本×1.5 CAGR（vs 主干×1.5） | Alpha门 | vs v2基准（CORE行为vs主干） ΔCAGR/ΔMDD | vs 主干(CAGR高且MDD浅) | 510300 均值占比 |\n|"+"---|"*11
out=hdr+"\n"+"\n".join(rows)
# robustness verdict
v=[]
for bk in ['B1_equal','B4_50_25_25']:
  for t,c in [('60w',600000),('100w',1000000)]:
    ok=True; why=[]
    for vv in ['Nminus','Nplus']:
      r,b,_=res[(vv,bk,t)]
      if abs(r['cagr']-b['cagr'])>0.01: ok=False; why.append(f'{vv} ΔCAGR {(r["cagr"]-b["cagr"])*100:+.2f}pp')
      if r['mdd']<b['mdd']-0.02: ok=False; why.append(f'{vv} MDD 劣 {(b["mdd"]-r["mdd"])*100:.2f}pp')
    r,b,_=res[('drop',bk,t)]
    if b['cagr']-r['cagr']>0.015: ok=False; why.append(f'drop3hp 降 {(b["cagr"]-r["cagr"])*100:.2f}pp')
    for key in [('Nminus',bk,t),('Nplus',bk,t),('drop',bk,t)]:
      if res[key][2]['cagr']<=trc15[c]['cagr']: ok=False; why.append(f'{key[0]} 成本×1.5 ≤ 主干×1.5')
    b15=k(f'book_smoke_conc_v2r_base_{bk}_{t}_c15_x2',c)
    if b15['cagr']<=trc15[c]['cagr']: ok=False; why.append('基准 成本×1.5 ≤ 主干×1.5')
    v.append(f"- {bk} {t}: {'稳健' if ok else '脆弱'}" + (f"（{'; '.join(why)}）" if why else ''))
out+="\n\n## 预注册稳健判读\n"+"\n".join(v)+"\n\n## 分年反向 >3pp\n"+("\n".join('- '+x for x in fl) or '- 无')
open('/tmp/v2r_table.md','w').write(out); print(out)
