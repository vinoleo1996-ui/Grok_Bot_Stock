"""纸面持仓（paper_daily_20261014 风险标记文件 + S6 影子 20261014）→ 申万一级暴露。只读。"""
import pandas as pd, json, glob
R='/workspace/QuantLab/'
m=pd.read_parquet(R+'data/v2/sw_l1_pit/industry_members_sw_l1.parquet')
m=m[m.out_date.isna()].drop_duplicates('instrument_id',keep='last')[['instrument_id','sw_code','sw_name']]
names={}
for f in glob.glob(R+'data/v2/ref/*.parquet'):
    try:
        d=pd.read_parquet(f)
        if 'name' in d.columns:
            idc=[c for c in d.columns if c in('instrument_id','ts_code','code')]
            if idc:
                for a,b in zip(d[idc[0]],d['name']):
                    a=str(a)
                    if '.' in a and a[-2:] in('SH','SZ','BJ'): a=a[-2:].lower()+'.'+a[:6]
                    names[a]=b
    except Exception: pass
r=pd.read_parquet(R+'output/loop/paper_daily_20261014/risk_flags.parquet')[['instrument_id','weight','track']]
for aum in ('100w','60w'):
    s=pd.read_parquet(R+f'output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_{aum}_20261014.parquet'); s=s[s.session==s.session.max()]
    r=pd.concat([r,pd.DataFrame({'instrument_id':s.instrument_id,'weight':s.weight,'track':'s6_'+aum})])
r=r.merge(m,on='instrument_id',how='left'); r['sw_name']=r.sw_name.fillna('未映射'); r['name']=r.instrument_id.map(names).fillna('')
exp=r.pivot_table(index='sw_name',columns='track',values='weight',aggfunc='sum').fillna(0).round(4)
print(exp.to_string())
out={'source':'output/loop/paper_daily_20261014/risk_flags.parquet + output/strategy_paper_s6/S6_*_20261014.parquet; sw_l1_pit','asof':'2026-10-14',
 'exposure':exp.to_dict(),'holdings':{t:g.sort_values('weight',ascending=False)[['instrument_id','name','sw_name','weight']].to_dict('records') for t,g in r.groupby('track')}}
json.dump(out,open(R+'output/intel/weekly_data/paper_exposure_20261014.json','w'),ensure_ascii=False,indent=1)
for t,g in r.groupby('track'): print(t, g.sort_values('weight',ascending=False).head(25)[['instrument_id','name','sw_name','weight']].to_string(index=False))
