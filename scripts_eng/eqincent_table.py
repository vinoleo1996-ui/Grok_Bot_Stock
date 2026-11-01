import json,pandas as pd
O='output/v3/'
def k(d,c,arm='BOOK'):
    s=json.load(open(f'{O}{d}/book_smoke_summary.json'))['by_capital'][str(c)][f'X2/{arm}']
    n=pd.read_csv(f'{O}{d}/aum_{c}/X2/{arm}/nav.csv'); n=n.set_index(pd.to_datetime(n.iloc[:,0])).nav
    y=[];p=n.iloc[0]
    for yr in (2024,2025,2026): e=n[n.index.year==yr].iloc[-1]; y.append(e/p-1); p=e
    return s,y
TR={600000:(0.1382,-0.1007),1000000:(0.1223,-0.1162)}
arms=[('叶 equity_incentive','book_smoke_g1g5_equity_incentive_x2',None),('主干 capacity_adv','book_smoke_g1g5_capacity_adv_x2',None),
 ('70/30 主干+叶','book_smoke_g1g5_combo_capadv_eqincent_70_30_x2',None),('80/20 主干+叶','book_smoke_g1g5_combo_capadv_eqincent_80_20_x2',None),
 ('4腿诊断 B1eq×3/4+叶×1/4','book_smoke_g1g5_conc4leg_b1eq_eqincent_60w_x2',600000),('4腿诊断 B1eq×3/4+叶×1/4','book_smoke_g1g5_conc4leg_b1eq_eqincent_100w_x2',1000000)]
rows=[];beat={}
for c in (600000,1000000):
    for nm,d,only in arms:
        if only and only!=c: continue
        s,y=k(d,c); g='过' if 0.12<=s['cagr']<=0.18 and s['mdd']>=-0.28 else '不过'
        bt='—' if '主干 ' in nm else ('胜' if s['cagr']>TR[c][0] and s['mdd']>TR[c][1] else '否')
        beat.setdefault(nm,[]).append(bt)
        rows.append(f"| {nm} | {c//10000}万 | {s['cagr']*100:.2f}% | {s['mdd']*100:.2f}% | {s['sharpe']:.2f} | {s['cost_pct_initial']*100:.2f}% | {' / '.join(f'{v*100:+.2f}' for v in y)} | {g} | {bt} |")
    s,y=k(arms[0][1],c,'C0')
    rows.append(f"| C0 纯510300 | {c//10000}万 | {s['cagr']*100:.2f}% | {s['mdd']*100:.2f}% | {s['sharpe']:.2f} | {s.get('cost_pct_initial',0)*100:.2f}% | {' / '.join(f'{v*100:+.2f}' for v in y)} | — | — |")
out="| 臂 | AUM | CAGR | MDD | Sharpe | 成本/AUM | 分年 2024(6/3起)/2025/2026(至10/9) % | Alpha门 | vs 主干(CAGR高且MDD浅) |\n|"+"---|"*9+"\n"+"\n".join(rows)
out+="\n\n组合判定（两档都须胜）：" + "；".join(f"{n}: {'胜主干' if all(x=='胜' for x in v) else '不胜主干'}（{'/'.join(v)}）" for n,v in beat.items() if n.startswith(('70','80')))
open('/tmp/ei_table.md','w').write(out); print(out)
