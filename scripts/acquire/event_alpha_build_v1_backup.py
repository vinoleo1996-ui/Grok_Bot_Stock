"""Alpha-schema deliverables (research, promotion_approved=false)."""
import pandas as pd, numpy as np, glob, json, hashlib, pathlib, re, pyarrow.parquet as pq
R=pathlib.Path("data/v2/tushare_raw"); V=pathlib.Path("data/v2"); TZ="Asia/Shanghai"
out={}
# --- 1. exalter institution map
ti=pd.read_parquet(V/"dragon_tiger/top_inst.parquet",columns=["exalter"])
ex=ti.exalter.astype(str).value_counts().rename("n_rows").reset_index().rename(columns={"index":"exalter"})
ex.columns=["exalter","n_rows"]
def lab(s):
    if "机构专用" in s: return "institution"
    if re.search(r"沪股通|深股通",s): return "northbound_channel"
    if "自营" in s: return "broker_prop"
    return "retail_or_hot_money"
ex["seat_type"]=ex.exalter.map(lab); ex["is_institution"]=ex.seat_type.eq("institution")
ex["rule_version"]="seat_rules_v1:机构专用->institution;沪/深股通->northbound;自营->broker_prop;else hot_money/营业部"
ex.to_parquet(V/"dragon_tiger/exalter_institution_map.parquet",index=False)
t=pd.read_parquet(V/"dragon_tiger/top_inst.parquet")
t=t.drop(columns=[c for c in ["seat_label"] if c in t]).merge(ex[["exalter","seat_type","is_institution"]],on="exalter",how="left")
d=pd.to_datetime(t.trade_date.astype(str),format="%Y%m%d")
t["available_at"]=(d+pd.Timedelta(hours=18)).dt.tz_localize(TZ)  # 交易所当晚披露
t["available_at_alpha_conservative"]=(d+pd.offsets.BDay(1)+pd.Timedelta(hours=15)).dt.tz_localize(TZ)
t["promotion_approved"]=False
t.to_parquet(V/"dragon_tiger/top_inst_labeled.parquet",index=False)
out["exalter_map"]={"seats":len(ex),"seat_type_rows":t.seat_type.value_counts().to_dict()}
# --- 3. margin
fs=sorted(glob.glob(str(R/"margin_detail/*.parquet")))
m=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
for c in m.columns:
    if c not in("trade_date","ts_code","name"): m[c]=pd.to_numeric(m[c],errors="coerce")
m=m.drop_duplicates(["trade_date","ts_code"])
d=pd.to_datetime(m.trade_date.astype(str),format="%Y%m%d")
m["available_at"]=(d+pd.offsets.BDay(1)+pd.Timedelta(hours=9)).dt.tz_localize(TZ)  # 交易所T+1早间公布
m["promotion_approved"]=False
m.to_parquet(V/"margin/rzrq_daily_tushare.parquet",index=False)
mk=m.groupby("trade_date").ts_code.apply(lambda s:s.str[-2:].nunique())
out["margin"]={"rows":len(m),"codes":m.ts_code.nunique(),"days":m.trade_date.nunique(),"range":[m.trade_date.min(),m.trade_date.max()],"days_missing_SZ":int((mk<2).sum())}
# --- 1. announcements classified
RULES=[("inquiry_reply",r"回复.*(问询|关注)函|(问询|关注)函.*回复"),("inquiry_letter",r"问询函|关注函|监管工作函"),
("penalty",r"行政处罚|处罚决定|立案|纪律处分|公开谴责|警示函|监管措施"),("buyback",r"回购"),
("insider_decrease",r"减持"),("insider_increase",r"增持"),
("earnings_beat",r"业绩预增|扭亏|预盈|大幅增长"),("earnings_miss",r"业绩预减|预亏|首亏|续亏|大幅下降")]
POL={"buyback":1,"insider_increase":1,"earnings_beat":1,"insider_decrease":-1,"earnings_miss":-1,"inquiry_letter":-1,"penalty":-1,"inquiry_reply":0,"other":0}
# v2: 回购细分（Alpha）。按顺序首个命中生效；excluded_* 改 event_type=buyback_excluded、polarity=0
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
def buyback_subtype(title):
    st=pd.Series("repurchase_other",index=title.index)
    for k,p in BUYBACK_SUB[::-1]: st[title.str.contains(p,regex=True)]=k
    return st
cv="rules_v2_"+hashlib.sha1(json.dumps([RULES,BUYBACK_SUB],ensure_ascii=False).encode()).hexdigest()[:8]
fs=[f for f in sorted(glob.glob(str(R/"anns_d/*.parquet"))) if pq.read_metadata(f).num_rows]
a=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True) if fs else pd.DataFrame()
if len(a): a["src"]="tushare_anns_d"
# 巨潮补路（不走 relay）：data/v2/announcements/cninfo/by_stock/*.parquet，announcementTime 毫秒戳→ann_time
cf=[f for f in sorted(glob.glob(str(V/"announcements/cninfo/by_stock/*.parquet"))) if pq.read_metadata(f).num_rows]
if cf:
    c=pd.concat([pd.read_parquet(f) for f in cf],ignore_index=True)
    ts=pd.to_datetime(pd.to_numeric(c.announcementTime,errors="coerce"),unit="ms",utc=True).dt.tz_convert(TZ).dt.tz_localize(None)
    ex=c.instrument.str.split(".").str[0].str.upper(); cd=c.instrument.str.split(".").str[1]
    c=pd.DataFrame({"ts_code":cd+"."+ex,"ann_date":ts.dt.strftime("%Y%m%d"),"ann_time":ts.astype(str),
        "title":c.announcementTitle.astype(str).str.replace(r"</?em>","",regex=True),
        "url":"http://static.cninfo.com.cn/"+c.adjunctUrl.astype(str),"name":c.secName,"ann_type":c.columnId,"src":"cninfo_hisAnnouncement"})
    a=pd.concat([c,a],ignore_index=True)  # cninfo 在前：去重时优先保留毫秒时点
    out["anns_cninfo"]={"stocks":len(cf),"rows":len(c)}
# 东财补路：只有日期 → ann_time 空 → available_at 按公告日 23:59 保守口径
ef=[f for f in sorted(glob.glob(str(V/"announcements/eastmoney/by_stock/*.parquet"))) if pq.read_metadata(f).num_rows]
if ef:
    e=pd.concat([pd.read_parquet(f) for f in ef],ignore_index=True)
    ex=e.instrument.str.split(".").str[0].str.upper(); cd=e.instrument.str.split(".").str[1]
    e=pd.DataFrame({"ts_code":cd+"."+ex,"ann_date":e.notice_date.str.replace("-","").str[:8],"ann_time":None,"title":e.title.astype(str),
        "url":"https://data.eastmoney.com/notices/detail/"+cd+"/"+e.art_code.astype(str)+".html","name":e.secName,"ann_type":e.column,"src":"eastmoney_ann"})
    a=pd.concat([a,e],ignore_index=True)  # 东财在后：跨源去重时优先保留巨潮/Tushare
    out["anns_eastmoney"]={"stocks":len(ef),"rows":len(e)}
if len(a):
    for c in["ann_time","ann_type"]:
        if c not in a: a[c]=None
    a["ann_date"]=a.ann_date.astype(str).str.replace("-","").str[:8]
    title=a.title.fillna("").astype(str)
    a["event_type"]="other"
    for k,p in reversed(RULES): pass
    et=pd.Series("other",index=a.index)
    for k,p in RULES[::-1]: et[title.str.contains(p,regex=True)]=k
    a["event_type"]=et
    # 无时钟→保守：公告日次交易时段可用（视作当日盘后，T+1 开盘可交易）
    tt=pd.to_datetime(a.ann_time,errors="coerce")
    hasclock=tt.notna()&((tt.dt.hour+tt.dt.minute)>0)
    base=pd.to_datetime(a.ann_date,format="%Y%m%d")
    a["available_at"]=np.where(hasclock,tt,base+pd.Timedelta(hours=23,minutes=59))
    a["available_at"]=pd.to_datetime(a.available_at).dt.tz_localize(TZ)
    a["available_at_rule"]=np.where(hasclock,"ann_time","ann_date 23:59 (no clock; tradable next session)")
    a=a.rename(columns={"ts_code":"instrument","title":"ann_title"})
    a["polarity"]=a.event_type.map(POL).astype(float)
    a["subtype"]=None; bb=a.event_type.eq("buyback")
    a.loc[bb,"subtype"]=buyback_subtype(a.loc[bb,"ann_title"].fillna("").astype(str))
    exm=bb&a.subtype.astype(str).str.startswith("excluded_")
    a.loc[exm,"event_type"]="buyback_excluded"; a.loc[exm,"polarity"]=0.0
    a.loc[bb&~exm,"polarity"]=a.loc[bb&~exm,"subtype"].map(SUB_POL).astype(float)
    a["event_id"]=[hashlib.sha1(f"{i}|{d}|{t}|{u}".encode()).hexdigest()[:16] for i,d,t,u in zip(a.instrument,a.ann_date,a.ann_title,a.url)]
    a["source"]=a.src; a["promotion_approved"]=False; a["classifier_version"]=cv
    a["meta_json"]=[json.dumps({"url":u,"ann_type":t,"name":n},ensure_ascii=False) for u,t,n in zip(a.url,a.ann_type,a.name)]
    a=a.drop_duplicates("event_id")
    # 跨源去重：股票+标题(去掉"公司简称："前缀/空白)+日期；保留来源并记录 sources_all
    a["_k"]=a.instrument.astype(str)+"|"+a.ann_date+"|"+a.ann_title.astype(str).str.replace(r"^[^：:]{1,12}[：:]","",regex=True).str.replace(r"\s","",regex=True)
    a["sources_all"]=a.groupby("_k").source.transform(lambda s:"|".join(sorted(set(s))))
    a=a.drop_duplicates("_k").drop(columns="_k")
    cols=["instrument","event_type","subtype","available_at","polarity","event_id","ann_title","source","promotion_approved","classifier_version","meta_json","ann_date","available_at_rule","url","sources_all"]
    a[cols].to_parquet(V/"events/announcements_classified_pit.parquet",index=False)
    days_trunc=[pathlib.Path(f).stem for f in fs if pq.read_metadata(f).num_rows>=5000]
    out["anns"]={"rows":len(a),"codes":a.instrument.nunique(),"days_files":len(fs),"range":[a.ann_date.min(),a.ann_date.max()],"source_rows":a.source.value_counts().to_dict(),
      "event_type":a.event_type.value_counts().to_dict(),"buyback_subtype":a.subtype.value_counts().to_dict(),"days_truncated_5000":len(days_trunc),"classifier_version":cv}
json.dump(out,open("output/d1/event_alpha_build_summary.json","w"),ensure_ascii=False,indent=1,default=str)
print(json.dumps(out,ensure_ascii=False,default=str))
