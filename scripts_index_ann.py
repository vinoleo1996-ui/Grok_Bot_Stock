import pandas as pd, json
cal=sorted(json.load(open("data/v2/cb/raw/days.json")))
def nexttd(d):
    d=d.strftime("%Y%m%d"); return next(x for x in cal if x>d)
def nth_fri(y,m,n):
    d=pd.Timestamp(y,m,1); d+=pd.Timedelta(days=(4-d.weekday())%7); return d+pd.Timedelta(weeks=n-1)
def last_fri(y,m):
    d=pd.Timestamp(y,m,1)+pd.offsets.MonthEnd(0)
    while d.weekday()!=4: d-=pd.Timedelta(days=1)
    return d
VER={ # (ann_date, effective first trading day with new constituents, source)
 (2018,6):("20180525","20180611","https://www.sse.com.cn/market/sseindex/diclosure/c/c_20180525_4561394.shtml"),
 (2018,12):(None,"20181217","https://www.cs.com.cn/gppd/tzzx/201812/t20181203_5899657.html"),
 (2019,6):(None,"20190617","https://finance.sina.com.cn/money/fund/jjyj/2019-06-03/doc-ihvhiews6535087.shtml"),
 (2020,6):(None,"20200615","http://www.zqrb.cn/stock/gupiaoyaowen/2020-06-01/A1590963843606.html"),
 (2020,12):("20201127","20201214","http://www.sse.com.cn/market/sseindex/diclosure/c/c_20201127_5268298.shtml"),
 (2022,12):("20221125","20221212","https://www.cs.com.cn/gppd/gsyj/202211/t20221125_6310359.html"),
 (2023,6):("20230526","20230612","http://m.yuebao.yktchina.com/kj/2023/0527/12574.html"),
 (2024,12):("20241129","20241216","https://finance.sina.com.cn/stock/relnews/cn/2024-11-29/doc-incxtvcm1811148.shtml"),
 (2025,6):("20250530","20250616","https://finance.sina.com.cn/money/fund/fundzmt/2025-05-30/doc-ineyixvc7718850.shtml"),
}
rows=[]
for y in range(2018,2027):
    for m in (6,12):
        if (y,m)>(2026,6): continue
        ann_r=last_fri(y,m-1).strftime("%Y%m%d"); eff_r=nexttd(nth_fri(y,m,2))
        a,e,src=VER.get((y,m),(None,None,None))
        rows.append(dict(review=f"{y}-{m:02d}",ann_date=a or ann_r,ann_date_source="public_report" if a else "rule_inferred(last Friday of prior month)",
            effective_date=e or eff_r,effective_source="public_report" if e else "rule_inferred(trading day after 2nd Friday close)",
            rule_effective_check=eff_r,source_url=src))
t=pd.DataFrame(rows); t["available_at"]=pd.to_datetime(t.ann_date)+pd.Timedelta(hours=20)
t.to_parquet("data/v2/index_members/csi_review_calendar.parquet"); print(t.to_string())
ev=pd.read_parquet("data/v2/index_members/index_member_events.parquet")
ev["review"]=None
for _,r in t.iterrows():
    # snapshot_date month-end of June/Dec containing effective date
    mk=(ev.snapshot_date.str[:6]==r.effective_date[:6])
    ev.loc[mk,"review"]=r.review
ev=ev.merge(t[["review","ann_date","effective_date","ann_date_source","available_at"]].rename(columns={"ann_date":"ann_date_r"}),on="review",how="left")
ev["ann_date"]=ev.ann_date_r; ev=ev.drop(columns="ann_date_r")
ev["ann_date_note"]=ev.review.isna().map({True:"非定期调整(临时调整/样本变更)，无统一公告日，保持空",False:""})
ev.to_parquet("data/v2/index_members/index_member_events.parquet")
print(ev.ann_date.notna().mean(), ev.groupby(ev.review.isna()).size())
