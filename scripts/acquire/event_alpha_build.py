"""Alpha-schema deliverables (research, promotion_approved=false). v2 低内存版。
默认只重建公告分类表；两融/龙虎榜重写需显式 --with-dragon / --with-margin。
公告：逐文件只读必要列→统一 category/精简列→分块分类→合并；与 v1 输出逐行一致。
用法: python3 event_alpha_build.py [--with-dragon] [--with-margin] [--out-dir DIR]"""
import pandas as pd, numpy as np, glob, json, hashlib, pathlib, re, argparse, gc, pyarrow.parquet as pq
ap=argparse.ArgumentParser(); ap.add_argument("--with-dragon",action="store_true"); ap.add_argument("--with-margin",action="store_true")
ap.add_argument("--out-dir",default=None,help="测试用：所有输出写到该目录"); A=ap.parse_args()
R=pathlib.Path("data/v2/tushare_raw"); V=pathlib.Path("data/v2"); TZ="Asia/Shanghai"
O=pathlib.Path(A.out_dir) if A.out_dir else None
def P(default,name): return (O/name) if O else default
SUMF=P(pathlib.Path("output/d1/event_alpha_build_summary.json"),"summary.json")
try: out=json.load(open(SUMF)) if not O else {}
except Exception: out={}
if A.with_dragon:
    ti=pd.read_parquet(V/"dragon_tiger/top_inst.parquet",columns=["exalter"])
    ex=ti.exalter.astype(str).value_counts().rename("n_rows").reset_index(); ex.columns=["exalter","n_rows"]; del ti
    def lab(s):
        if "机构专用" in s: return "institution"
        if re.search(r"沪股通|深股通",s): return "northbound_channel"
        if "自营" in s: return "broker_prop"
        return "retail_or_hot_money"
    ex["seat_type"]=ex.exalter.map(lab); ex["is_institution"]=ex.seat_type.eq("institution")
    ex["rule_version"]="seat_rules_v1:机构专用->institution;沪/深股通->northbound;自营->broker_prop;else hot_money/营业部"
    ex.to_parquet(P(V/"dragon_tiger/exalter_institution_map.parquet","exmap.parquet"),index=False)
    t=pd.read_parquet(V/"dragon_tiger/top_inst.parquet")
    t=t.drop(columns=[c for c in ["seat_label"] if c in t]).merge(ex[["exalter","seat_type","is_institution"]],on="exalter",how="left")
    d=pd.to_datetime(t.trade_date.astype(str),format="%Y%m%d")
    t["available_at"]=(d+pd.Timedelta(hours=18)).dt.tz_localize(TZ)
    t["available_at_alpha_conservative"]=(d+pd.offsets.BDay(1)+pd.Timedelta(hours=15)).dt.tz_localize(TZ)
    t["promotion_approved"]=False
    t.to_parquet(P(V/"dragon_tiger/top_inst_labeled.parquet","topinst.parquet"),index=False)
    out["exalter_map"]={"seats":len(ex),"seat_type_rows":t.seat_type.value_counts().to_dict()}; del t,d,ex; gc.collect()
if A.with_margin:
    fs=sorted(glob.glob(str(R/"margin_detail/*.parquet")))
    m=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
    for c in m.columns:
        if c not in("trade_date","ts_code","name"): m[c]=pd.to_numeric(m[c],errors="coerce")
    m=m.drop_duplicates(["trade_date","ts_code"])
    d=pd.to_datetime(m.trade_date.astype(str),format="%Y%m%d")
    m["available_at"]=(d+pd.offsets.BDay(1)+pd.Timedelta(hours=9)).dt.tz_localize(TZ)
    m["promotion_approved"]=False
    m.to_parquet(P(V/"margin/rzrq_daily_tushare.parquet","margin.parquet"),index=False)
    mk=m.groupby("trade_date").ts_code.apply(lambda s:s.str[-2:].nunique())
    out["margin"]={"rows":len(m),"codes":m.ts_code.nunique(),"days":m.trade_date.nunique(),"range":[m.trade_date.min(),m.trade_date.max()],"days_missing_SZ":int((mk<2).sum())}
    del m,d; gc.collect()
# --- announcements classified
RULES=[("inquiry_reply",r"回复.*(问询|关注)函|(问询|关注)函.*回复"),("inquiry_letter",r"问询函|关注函|监管工作函"),
("penalty",r"行政处罚|处罚决定|立案|纪律处分|公开谴责|警示函|监管措施"),("buyback",r"回购"),
("insider_decrease",r"减持"),("insider_increase",r"增持"),
("earnings_beat",r"业绩预增|扭亏|预盈|大幅增长"),("earnings_miss",r"业绩预减|预亏|首亏|续亏|大幅下降")]
POL={"buyback":1,"insider_increase":1,"earnings_beat":1,"insider_decrease":-1,"earnings_miss":-1,"inquiry_letter":-1,"penalty":-1,"inquiry_reply":0,"other":0}
BUYBACK_SUB=[("excluded_withdrawn_notice",r"[（(]已取消[)）]"),("excluded_pledge_repo",r"质押式回购|股票质押|质押回购|约定购回|购回交易|延期购回|提前购回|补充质押|解除质押|新增质押"),
("excluded_treasury_repo",r"逆回购|报价回购|债券回购|理财"),
("excluded_perf_comp",r"业绩补偿|补偿股份|业绩承诺|发行股份购买资产|定向回购"),
("excluded_incentive_cancel",r"限制性股票|股权激励|激励计划|激励对象|激励股份|股票期权|员工持股|回购注销.*(离职|解锁|解除限售)"),
("excluded_non_share",r"(子公司|参股|控股股东|合伙).{0,20}回购.{0,10}(股权|出资|份额)|回购.{0,6}(股权|房产|资产|债券|转债|份额)|收益权|回购融资|回购款|永续"),
("excluded_treasury_sale",r"(集中竞价|大宗).{0,4}减持.{0,4}(结果|计划|进展)?|减持.{0,6}已?回购|出售.{0,8}回购"),("repurchase_terminate",r"终止|(?<!已)取消|撤销|中止|放弃"),
("repurchase_done",r"实施完毕|实施结果|回购完成|完成回购|回购.{0,8}股份完成|完成.{0,4}公告|注销完成|注销.{0,10}(已回购|库存)|期限届满|届满|注销.{0,6}已?回购股份|已回购股份.{0,6}注销"),
("repurchase_ancillary",r"前十|债权人|法律意见|独立意见|核查意见|财务顾问|用途|调整|变更|延长|延期|问询|说明|减资|违规|专用证券账户"),
("repurchase_progress",r"进展|首次.{0,6}回购|达到|超过|比例|回购.{0,10}股份情况"),
("repurchase_plan",r"预案|方案|报告书|提议|拟.{0,15}回购|回购.{0,15}(议案|计划)")]
SUB_POL={"repurchase_plan":1,"repurchase_progress":1,"repurchase_done":1,"repurchase_terminate":-1,"repurchase_ancillary":0,"repurchase_other":0}
cv="rules_v2_"+hashlib.sha1(json.dumps([RULES,BUYBACK_SUB],ensure_ascii=False).encode()).hexdigest()[:8]
import warnings; warnings.filterwarnings("ignore",category=UserWarning)
STD=["ts_code","ann_date","ann_time","title","url","name","ann_type","src"]
def rd(f,cols):
    have=set(pq.read_schema(f).names); return pd.read_parquet(f,columns=[c for c in cols if c in have])
def nonempty(g): return [f for f in sorted(glob.glob(g)) if pq.read_metadata(f).num_rows]
def tushare(f):
    x=rd(f,["ts_code","name","title","ann_type","ann_date","ann_time","url"]); x["src"]="tushare_anns_d"; return x
def cninfo(f):
    c=rd(f,["announcementTime","instrument","announcementTitle","adjunctUrl","secName","columnId"])
    ts=pd.to_datetime(pd.to_numeric(c.announcementTime,errors="coerce"),unit="ms",utc=True).dt.tz_convert(TZ).dt.tz_localize(None)
    ex=c.instrument.str.split(".").str[0].str.upper(); cd=c.instrument.str.split(".").str[1]
    return pd.DataFrame({"ts_code":cd+"."+ex,"ann_date":ts.dt.strftime("%Y%m%d"),"ann_time":ts.astype(str),
        "title":c.announcementTitle.astype(str).str.replace(r"</?em>","",regex=True),
        "url":"http://static.cninfo.com.cn/"+c.adjunctUrl.astype(str),"name":c.secName,"ann_type":c.columnId,"src":"cninfo_hisAnnouncement"})
def eastm(f):
    e=rd(f,["instrument","notice_date","title","art_code","secName","column"])
    ex=e.instrument.str.split(".").str[0].str.upper(); cd=e.instrument.str.split(".").str[1]
    return pd.DataFrame({"ts_code":cd+"."+ex,"ann_date":e.notice_date.str.replace("-","").str[:8],"ann_time":None,"title":e.title.astype(str),
        "url":"https://data.eastmoney.com/notices/detail/"+cd+"/"+e.art_code.astype(str)+".html","name":e.secName,"ann_type":e.column,"src":"eastmoney_ann"})
def norm(x):
    for c in STD:
        if c not in x: x[c]=None
    x=x[STD].copy()
    x["ann_date"]=x.ann_date.astype(str).str.replace("-","").str[:8]
    for c in ["ann_time","ann_type","name"]: x[c]=x[c].astype(object).where(x[c].notna(),None)
    return x
import zlib, shutil, tempfile, pyarrow as pa
NB=16  # 按股票分桶：event_id 与跨源键都含 instrument，桶内去重 == 全局去重
fs=nonempty(str(R/"anns_d/*.parquet")); cf=nonempty(str(V/"announcements/cninfo/by_stock/*.parquet")); ef=nonempty(str(V/"announcements/eastmoney/by_stock/*.parquet"))
SCH=pa.schema([(c,pa.string()) for c in STD])
TD=pathlib.Path(tempfile.mkdtemp(prefix="anns_bkt_",dir="/tmp")); W={}
def spill(d):
    b=d.ts_code.astype(str).map(lambda x:zlib.crc32(x.encode())%NB)
    for k,g in d.groupby(b,sort=False):
        if k not in W: W[k]=pq.ParquetWriter(TD/f"b{k}.parquet",SCH)
        W[k].write_table(pa.Table.from_pandas(g.astype(object).where(g.notna(),None),schema=SCH,preserve_index=False))
n_c=n_e=0
for f in cf: d=norm(cninfo(f)); n_c+=len(d); spill(d)   # 顺序与 v1 一致：cninfo → tushare → eastmoney
for f in fs: spill(norm(tushare(f)))
for f in ef: d=norm(eastm(f)); n_e+=len(d); spill(d)
for w_ in W.values(): w_.close()
if cf: out["anns_cninfo"]={"stocks":len(cf),"rows":n_c}
if ef: out["anns_eastmoney"]={"stocks":len(ef),"rows":n_e}
cols=["instrument","event_type","subtype","available_at","polarity","event_id","ann_title","source","promotion_approved","classifier_version","meta_json","ann_date","available_at_rule","url","sources_all"]
def classify(a):
    title=a.title.fillna("").astype(str)
    et=pd.Series("other",index=a.index,dtype=object)
    for k,p in RULES[::-1]: et[title.str.contains(p,regex=True)]=k
    a["event_type"]=et
    tt=pd.to_datetime(a.ann_time,errors="coerce",format="ISO8601")
    hasclock=tt.notna()&((tt.dt.hour+tt.dt.minute)>0)
    base=pd.to_datetime(a.ann_date,format="%Y%m%d")
    a["available_at"]=pd.to_datetime(np.where(hasclock,tt,base+pd.Timedelta(hours=23,minutes=59))).tz_localize(TZ)
    a["available_at_rule"]=np.where(hasclock,"ann_time","ann_date 23:59 (no clock; tradable next session)")
    a=a.rename(columns={"ts_code":"instrument","title":"ann_title"})
    a["polarity"]=a.event_type.map(POL).astype(float)
    a["subtype"]=None; bb=a.event_type.eq("buyback")
    bt=title[bb]; st=pd.Series("repurchase_other",index=bt.index,dtype=object)
    for k,p in BUYBACK_SUB[::-1]: st[bt.str.contains(p,regex=True)]=k
    a.loc[bb,"subtype"]=st
    exm=bb&a.subtype.astype(str).str.startswith("excluded_")
    a.loc[exm,"event_type"]="buyback_excluded"; a.loc[exm,"polarity"]=0.0
    a.loc[bb&~exm,"polarity"]=a.loc[bb&~exm,"subtype"].map(SUB_POL).astype(float)
    a["event_id"]=[hashlib.sha1(f"{i}|{d}|{t}|{u}".encode()).hexdigest()[:16] for i,d,t,u in zip(a.instrument,a.ann_date,a.ann_title,a.url)]
    a=a.drop_duplicates("event_id")
    k=a.instrument.astype(str)+"|"+a.ann_date+"|"+a.ann_title.astype(str).str.replace(r"^[^：:]{1,12}[：:]","",regex=True).str.replace(r"\s","",regex=True)
    a["sources_all"]=a.src.groupby(k).transform(lambda s:"|".join(sorted(set(s))))
    a=a[~k.duplicated()].copy()
    a["source"]=a.src; a["promotion_approved"]=False; a["classifier_version"]=cv
    a["meta_json"]=[json.dumps({"url":u,"ann_type":t,"name":n},ensure_ascii=False) for u,t,n in zip(a.url,a.ann_type,a.name)]
    return a[cols]
if W:
    dst=P(V/"events/announcements_classified_pit.parquet","anns.parquet"); tmp=pathlib.Path(str(dst)+".tmp"); OW=None
    rows=0; codes=0; dmin=dmax=None; vc={"source":{}, "event_type":{}, "subtype":{}}
    def addvc(key,s):
        for k_,v_ in s.value_counts().items(): vc[key][k_]=vc[key].get(k_,0)+int(v_)
    for k in sorted(W):
        a=pd.read_parquet(TD/f"b{k}.parquet")
        for c in ["ann_time","ann_type","name"]: a[c]=a[c].where(a[c].notna(),None)
        a=classify(a); tb=pa.Table.from_pandas(a,preserve_index=False)
        if OW is None: OW=pq.ParquetWriter(tmp,tb.schema)
        OW.write_table(tb.cast(OW.schema))
        rows+=len(a); codes+=a.instrument.nunique(); dmin=min(filter(None,[dmin,a.ann_date.min()])); dmax=max(filter(None,[dmax,a.ann_date.max()]))
        addvc("source",a.source); addvc("event_type",a.event_type); addvc("subtype",a.subtype); del a,tb; gc.collect()
    OW.close(); tmp.replace(dst)
    srt=lambda d:dict(sorted(d.items(),key=lambda x:-x[1]))
    days_trunc=[f for f in fs if pq.read_metadata(f).num_rows>=5000]
    out["anns"]={"rows":rows,"codes":codes,"days_files":len(fs),"range":[dmin,dmax],"source_rows":srt(vc["source"]),
      "event_type":srt(vc["event_type"]),"buyback_subtype":srt(vc["subtype"]),"days_truncated_5000":len(days_trunc),"classifier_version":cv}
shutil.rmtree(TD,ignore_errors=True)
json.dump(out,open(SUMF,"w"),ensure_ascii=False,indent=1,default=str)
print(json.dumps(out.get("anns",{}),ensure_ascii=False,default=str))
