#!/usr/bin/env python3
"""SW L1 -> ETF PIT map. rules: keyword match on benchmark (fund_basic). Research-grade where fund_share missing."""
import pandas as pd,glob,re,os,json
SW=pd.read_parquet("data/v2/tushare_raw/index_classify/SW2021_L1.parquet")[["index_code","industry_name"]]
SWITCH="20211213"  # 申万2021版指数正式发布/切换日
OLD={"基础化工":"化工","电力设备":"电气设备","社会服务":"休闲服务","纺织服饰":"纺织服装","商贸零售":"商业贸易",
     "煤炭":"采掘(2014版,拆分前)","石油石化":"采掘/化工(2014版,拆分前)","环保":"公用事业(2014版,拆分前)","美容护理":"化工/轻工(2014版,拆分前)"}
# (pattern on benchmark index name, match_type, basis)
R={
"农林牧渔":[(r"农林牧渔|农业|畜牧|养殖|粮食|现代农业",'close')],
"基础化工":[(r"化工|细分化工|化学",'close'),(r"新材料",'partial')],
"钢铁":[(r"钢铁",'close')],
"有色金属":[(r"^中证有色金属指数|有色金属行业|细分有色",'close'),(r"有色|稀土|黄金|矿业|稀有金属",'partial')],
"电子":[(r"电子",'close'),(r"半导体|芯片|集成电路|消费电子",'partial')],
"汽车":[(r"汽车|整车",'close'),(r"新能源车|新能源汽车|智能汽车|电动汽车|汽车零部件",'partial')],
"家用电器":[(r"家用电器|家电",'close')],
"食品饮料":[(r"食品饮料|食品|主要消费|消费|酒",'close')],
"纺织服饰":[(r"纺织|服装|服饰",'close')],
"轻工制造":[(r"轻工",'close'),(r"家居|造纸|包装",'partial')],
"医药生物":[(r"医药|生物|医疗|健康|创新药|中药|疫苗",'close')],
"公用事业":[(r"公用事业|电力|绿色电力|绿电",'close')],
"交通运输":[(r"交通运输|物流|航运|港口|航空",'close')],
"房地产":[(r"房地产|地产",'close')],
"商贸零售":[(r"商贸|零售|电商|商业",'close')],
"社会服务":[(r"旅游|社会服务|教育|休闲",'close')],
"银行":[(r"银行",'close')],
"非银金融":[(r"证券|保险|非银|券商",'close'),(r"金融科技",'partial')],
"建筑材料":[(r"建材|建筑材料|水泥",'close')],
"建筑装饰":[(r"建筑|基建",'close')],
"电力设备":[(r"电力设备|电气设备",'close'),(r"新能源|光伏|风电|储能|电池|电网",'partial')],
"机械设备":[(r"机械|工程机械|机器人|高端装备|工业母机|装备",'close')],
"国防军工":[(r"军工|国防|航天|航空航天",'close')],
"计算机":[(r"计算机|软件|信息技术|云计算|大数据|人工智能|信创|信息安全|网络安全",'close')],
"传媒":[(r"传媒|游戏|影视|动漫|文化",'close')],
"通信":[(r"通信(?!息)|5G|电信",'close')],
"煤炭":[(r"煤炭",'close')],
"石油石化":[(r"石油|石化|油气|能源化工",'close')],
"环保":[(r"环保|环境",'close')],
"美容护理":[(r"美容|护理|化妆品",'close')],
"综合":[],
}
fb=pd.read_parquet("data/v2/etf/raw/fund_basic_E.parquet")
fb=fb[fb.name.str.contains("ETF")&~fb.name.str.contains("联接|债|货币|黄金ETF$|商品")].copy()
fb["idx_name"]=fb.benchmark.fillna("").str.replace(r"(收益率|\*|×|x|100%|\d+%|\(.*?\)|（.*?）).*$","",regex=True).str.strip()
fb=fb[~fb.idx_name.str.contains(r"港股|恒生|沪港深|沪深港|香港|纳斯达克|标普|海外|全球|成份指数$|成指$|证券交易所|可选消费|金融地产|大消费|消费50")]
def classify(r):
    s=r.idx_name+" "+r["name"]
    # exact: tracks a Shenwan L1 index
    for _,w in SW.iterrows():
        if re.search(r"申万"+w.industry_name+r"(指数)?$",r.idx_name) or re.search(r"申万"+OLD.get(w.industry_name,"@@")+r"(指数)?$",r.idx_name):
            return w.index_code,w.industry_name,"exact","基准=申万一级行业指数"
    for _,w in SW.iterrows():
        for pat,mt in R[w.industry_name]:
            if re.search(pat,r.idx_name):
                return w.index_code,w.industry_name,mt,f"基准名关键词/{pat}/→{mt}"
    return None,None,None,None
fb[["sw_l1_code","sw_l1_name","match_type","match_basis"]]=fb.apply(lambda r:pd.Series(classify(r)),axis=1)
fb=fb[fb.sw_l1_code.notna()]
# 宽基/主要消费等歧义收紧：'消费' 只当名称不含 50/100/宽基
fb=fb[~((fb.sw_l1_name=="食品饮料")&fb.idx_name.str.contains(r"^.{0,4}消费\d|大消费|消费龙头|消费50|新消费"))]
print("matched etfs",len(fb))
fb["list_date"]=fb.list_date.fillna(fb.found_date).astype(str).str[:8]
fb["delist_date"]=fb.delist_date.astype("string").str[:8]
# daily scale
shares=[]
for f in glob.glob("data/v2/etf/raw/fund_share/*.parquet"):
    c=os.path.basename(f)[:-8]
    if c in set(fb.ts_code): shares.append(pd.read_parquet(f)[["ts_code","trade_date","fd_share"]])
sh=pd.concat(shares) if shares else pd.DataFrame(columns=["ts_code","trade_date","fd_share"])
sh["trade_date"]=sh.trade_date.astype(str)
codes=set(fb.ts_code); px=[]
for f in sorted(glob.glob("data/v2/etf/raw/fund_daily/*.parquet")):
    if os.path.basename(f)[:8]<"20150101": continue
    x=pd.read_parquet(f,columns=["ts_code","trade_date","close","amount"]); px.append(x[x.ts_code.isin(codes)])
px=pd.concat(px); px["trade_date"]=px.trade_date.astype(str)
px=px.merge(sh,on=["ts_code","trade_date"],how="left").sort_values(["ts_code","trade_date"])
px["fd_share"]=px.groupby("ts_code").fd_share.ffill(limit=5)
px["aum_wan"]=px.fd_share*px.close   # 万份*元=万元
px["amt20"]=px.groupby("ts_code").amount.transform(lambda s:s.rolling(20,1).mean())
px["scale_source"]=px.aum_wan.notna().map({True:"fd_share*close",False:"research_grade:amt20_proxy"})
px["rank_key"]=px.aum_wan.fillna(-1e18+px.amt20.fillna(0))
px=px.merge(fb[["ts_code","sw_l1_code","sw_l1_name","match_type"]],on="ts_code")
mrank={"exact":0,"close":1,"partial":2}
px["mr"]=px.match_type.map(mrank)
# pick per industry/day: best match_type first, then largest scale
best=px.sort_values(["sw_l1_code","trade_date","mr","rank_key"],ascending=[1,1,1,0]).groupby(["sw_l1_code","trade_date"]).head(1)
days=sorted(px.trade_date.unique())
grid=pd.MultiIndex.from_product([SW.index_code,days],names=["sw_l1_code","trade_date"]).to_frame(index=False)
daily=grid.merge(best.drop(columns=["sw_l1_name","mr","rank_key"]),on=["sw_l1_code","trade_date"],how="left")
daily=daily.merge(SW.rename(columns={"index_code":"sw_l1_code","industry_name":"sw_l1_name"}),on="sw_l1_code")
daily["no_etf"]=daily.ts_code.isna()
daily["sw_version"]=(daily.trade_date>=SWITCH).map({True:"SW2021",False:"SW2014"})
daily["sw_l1_name_asof"]=daily.apply(lambda r:r.sw_l1_name if r.sw_version=="SW2021" else OLD.get(r.sw_l1_name,r.sw_l1_name),axis=1)
daily=daily.rename(columns={"ts_code":"etf_ts_code"}).merge(fb[["ts_code","name","benchmark","idx_name","match_basis","list_date","delist_date"]].rename(columns={"ts_code":"etf_ts_code","name":"etf_name","idx_name":"tracking_index_name"}),on="etf_ts_code",how="left")
daily["tracking_index_code"]=None
daily["available_at"]=pd.to_datetime(daily.trade_date)+pd.Timedelta(hours=17)
# intervals
daily=daily.sort_values(["sw_l1_code","trade_date"])
daily["k"]=daily.etf_ts_code.fillna("NO_ETF")
daily["blk"]=(daily.k!=daily.groupby("sw_l1_code").k.shift()).cumsum()
iv=daily.groupby("blk").agg(sw_l1_code=("sw_l1_code","first"),sw_l1_name=("sw_l1_name","first"),sw_version=("sw_version","first"),
   etf_ts_code=("etf_ts_code","first"),etf_name=("etf_name","first"),tracking_index_code=("tracking_index_code","first"),
   tracking_index_name=("tracking_index_name","first"),match_type=("match_type","first"),match_basis=("match_basis","first"),
   list_date=("list_date","first"),delist_date=("delist_date","first"),valid_from=("trade_date","min"),valid_to=("trade_date","max"),
   no_etf=("no_etf","first"),scale_source=("scale_source",lambda s:"research_grade" if (s!="fd_share*close").any() else "fd_share*close")).reset_index(drop=True)
os.makedirs("data/v2/etf",exist_ok=True)
iv.to_parquet("data/v2/etf/sw_l1_etf_map_pit.parquet")
daily.drop(columns=["k","blk"]).to_parquet("data/v2/etf/sw_l1_etf_map_pit_daily.parquet")
fb.to_parquet("data/v2/etf/sw_l1_etf_candidates.parquet")
first=px.groupby(["sw_l1_code"]).trade_date.min().rename("first_etf_date")
summ=SW.rename(columns={"index_code":"sw_l1_code","industry_name":"sw_l1_name"}).set_index("sw_l1_code").join(first)
summ["n_candidate_etfs"]=fb.groupby("sw_l1_code").size()
for t in ["exact","close","partial"]:
    summ["first_"+t]=px[px.match_type==t].groupby("sw_l1_code").trade_date.min()
summ.reset_index().to_parquet("data/v2/etf/sw_l1_etf_first_date.parquet")
summ.reset_index().to_csv("data/v2/etf/sw_l1_etf_first_date.csv",index=False)
print(summ.sort_values("first_etf_date").to_string())
print("intervals",len(iv),"research_grade rows",(daily.scale_source!="fd_share*close").sum(),"/",daily.etf_ts_code.notna().sum())
