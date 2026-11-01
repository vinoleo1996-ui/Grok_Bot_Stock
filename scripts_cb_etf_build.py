import pandas as pd, glob, json, os, numpy as np, re
O="data/v2/"
days=json.load(open(O+"cb/raw/days_20150101.json")); END="20261009"
def cat(p):
    fs=sorted(glob.glob(p)); return pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f)>0],ignore_index=True), len(fs)
rep={}
# ---------- CB ----------
b=pd.read_parquet(O+"cb/raw/cb_basic_raw.parquet")
b.to_parquet(O+"cb/cb_basic.parquet")
cd,n=cat(O+"cb/raw/cb_daily/*.parquet")
cd=cd[cd.close.notna()]
# close==0 rows: non-trading placeholders
cd["is_placeholder"]=cd.close.fillna(0)<=0
cd["available_at"]=pd.to_datetime(cd.trade_date)+pd.Timedelta(hours=15)
cd["available_at_tz"]="Asia/Shanghai"
share=pd.read_parquet(O+"cb/raw/cb_share_raw.parquet") if os.path.exists(O+"cb/raw/cb_share_raw.parquet") else None
if share is not None:
    share=share.drop_duplicates()
    share["available_at"]=pd.to_datetime(share.publish_date.fillna(share.end_date))+pd.Timedelta(hours=18)
    share.to_parquet(O+"cb/cb_share_balance.parquet")
    # asof remain_size onto daily
    s=share.dropna(subset=["remain_size"]).sort_values("available_at")[["ts_code","available_at","remain_size","convert_price"]].rename(columns={"available_at":"bal_avail","remain_size":"remain_size_asof","convert_price":"convert_price_asof"})
    cd["_t"]=pd.to_datetime(cd.trade_date)+pd.Timedelta(hours=9)
    cd=pd.merge_asof(cd.sort_values("_t"),s.sort_values("bal_avail"),left_on="_t",right_on="bal_avail",by="ts_code",direction="backward").drop(columns="_t")
cd.sort_values(["trade_date","ts_code"]).to_parquet(O+"cb/cb_daily.parquet")
real=cd[~cd.is_placeholder]
rep["cb"]={"daily_rows":len(cd),"daily_real_rows":len(real),"bonds":int(real.ts_code.nunique()),"days_files":n,"days_expected":len(days),
  "date_min":real.trade_date.min(),"date_max":real.trade_date.max(),
  "missing_rate_real":{c:round(float(real[c].isna().mean()),4) for c in ["close","amount","cb_value","cb_over_rate","bond_value","bond_over_rate"]+(["remain_size_asof"] if share is not None else [])},
  "cb_basic_rows":len(b),"cb_basic_delisted":int(b.delist_date.notna().sum())}
miss=[d for d in days if d<=END and d not in set(cd.trade_date)]
rep["cb"]["missing_days"]=miss[:50]; rep["cb"]["n_missing_days"]=len(miss)
# events
ev=[]
if os.path.exists(O+"cb/raw/cb_call_raw.parquet"):
    c=pd.read_parquet(O+"cb/raw/cb_call_raw.parquet").drop_duplicates()
    c["event_type"]=c.call_type.map(lambda x:"call" if "赎" in str(x) else ("put" if "回售" in str(x) else str(x)))
    c["available_at"]=pd.to_datetime(c.ann_date)+pd.Timedelta(hours=18)
    c.to_parquet(O+"cb/cb_call_events.parquet"); rep["cb"]["call_events"]=len(c); rep["cb"]["call_types"]=c.call_type.value_counts().to_dict()
if share is not None:
    # down-revision proxy: convert_price drop not explained... flag all convert_price changes
    s=share.dropna(subset=["convert_price"]).sort_values(["ts_code","available_at"])
    s["prev"]=s.groupby("ts_code").convert_price.shift()
    chg=s[s.prev.notna()&(s.convert_price!=s.prev)].copy()
    chg["chg_pct"]=chg.convert_price/chg.prev-1
    chg["event_type"]=np.where(chg.chg_pct<-0.03,"price_chg_down_candidate","price_chg_adjust")
    chg=chg[["ts_code","publish_date","end_date","prev","convert_price","chg_pct","event_type","available_at"]]
    chg.to_parquet(O+"cb/cb_conv_price_changes_derived.parquet"); rep["cb"]["conv_price_changes_derived"]=len(chg); rep["cb"]["down_candidates"]=int((chg.event_type=="price_chg_down_candidate").sum())
if os.path.exists(O+"cb/raw/cb_rate_raw.parquet"):
    pd.read_parquet(O+"cb/raw/cb_rate_raw.parquet").to_parquet(O+"cb/cb_coupon_schedule.parquet")
# ---------- ETF ----------
fb=pd.read_parquet(O+"etf/raw/fund_basic_E.parquet").drop_duplicates("ts_code")
etf=fb[fb.name.str.contains("ETF",na=False)&~fb.name.str.contains("联接|LOF",na=False)].copy()
BROAD=r"沪深300|中证500|中证1000|中证800|中证2000|上证50|上证180|上证380|科创50|科创100|科创板|创业板|创业|深证100|深证成指|中小|双创|A50|A500|中证全指|红利|价值|成长|MSCI|富时|基本面|央企|国企|综指|上证指数|深100|300|500|1000|180|50ETF|恒生|纳斯达克|纳指|标普|日经|德国|法国|道琼斯|国债|政金债|公司债|城投|可转债|短融|货币|黄金|豆粕|有色期货|能源化工"
IND=r"银行|证券|券商|保险|非银|金融|地产|房地产|医药|医疗|生物|疫苗|中药|创新药|酒|食品|饮料|消费|家电|汽车|新能源车|电池|锂电|光伏|新能源|电力|煤炭|钢铁|有色|稀土|化工|建材|基建|建筑|军工|国防|半导体|芯片|集成电路|计算机|软件|通信|5G|传媒|游戏|电子|互联网|云计算|大数据|人工智能|机器人|养殖|农业|畜牧|交运|物流|航运|旅游|环保|石油|油气|材料|机械|高端装备|信息技术|科技"
def tag(nm):
    if re.search(r"货币|国债|政金债|公司债|城投|可转债|短融|信用债|地方债|利率债",nm): return "债券/货币"
    if re.search(r"黄金|豆粕|期货|白银",nm): return "商品"
    if re.search(r"恒生|纳斯达克|纳指|标普|日经|德国|法国|道琼斯|港股|中概|海外|美国|亚太|沙特|东南亚",nm): return "跨境"
    if re.search(IND,nm): return "行业"
    if re.search(BROAD,nm): return "宽基"
    return "主题/其他"
etf["category"]=etf.name.map(tag)
etf["category_rule"]="name_regex_v1(行业关键词优先于宽基;跨境/债券/商品单列)"
etf.to_parquet(O+"etf/etf_basic.parquet")
fd,n1=cat(O+"etf/raw/fund_daily/*.parquet"); fa,n2=cat(O+"etf/raw/fund_adj/*.parquet")
codes=set(etf.ts_code)
fd=fd[fd.ts_code.isin(codes)]; fa=fa[fa.ts_code.isin(codes)]
m=fd.merge(fa,on=["ts_code","trade_date"],how="left")
for c in ["open","high","low","close","pre_close"]: m[c+"_hfq"]=m[c]*m.adj_factor
m["available_at"]=pd.to_datetime(m.trade_date)+pd.Timedelta(hours=15); m["available_at_tz"]="Asia/Shanghai"
m=m.merge(etf[["ts_code","name","category"]],on="ts_code",how="left")
m.sort_values(["trade_date","ts_code"]).to_parquet(O+"etf/etf_daily_adj.parquet")
rep["etf"]={"etf_universe":len(etf),"delisted":int(etf.delist_date.notna().sum()),"category_counts":etf.category.value_counts().to_dict(),
  "daily_rows":len(m),"etfs_with_daily":int(m.ts_code.nunique()),"date_min":m.trade_date.min(),"date_max":m.trade_date.max(),
  "days_files":[n1,n2],"adj_factor_missing_rate":round(float(m.adj_factor.isna().mean()),5),
  "missing_rate":{c:round(float(m[c].isna().mean()),5) for c in ["close","vol","amount"]},
  "etfs_no_daily":int(len(codes-set(m.ts_code)))}
# reuse check 510300
try:
    old=pd.read_parquet(O+"etf_510300/fund_daily_tushare_510300.parquet")
    x=old.merge(m[m.ts_code=="510300.SH"],on="trade_date",suffixes=("_o",""))
    rep["etf"]["check_510300_vs_existing"]={"overlap":len(x),"max_abs_close_diff":float((x.close-x.close_o).abs().max())}
except Exception as e: rep["etf"]["check_510300_vs_existing"]=str(e)[:100]
json.dump(rep,open(O+"cb/../cb_etf_coverage.json","w"),ensure_ascii=False,indent=1,default=str)
print(json.dumps(rep,ensure_ascii=False,indent=1,default=str))
