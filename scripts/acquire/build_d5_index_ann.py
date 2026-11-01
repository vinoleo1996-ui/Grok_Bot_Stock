"""D5: 指数定期调样公告日补强 (沪深300/中证500/中证1000). PIT available_at = ann_date 20:00 Asia/Shanghai."""
import json, pandas as pd, pathlib
ROOT=pathlib.Path("/workspace/QuantLab"); D=ROOT/"data/v2/index_members"
c=pd.read_parquet(ROOT/"data/v2/tushare_raw/trade_cal.parquet"); cal=sorted(c[c.is_open.astype(int)==1].cal_date.astype(str))
def nexttd(d): d=d.strftime("%Y%m%d"); return next(x for x in cal if x>d)
def nth_fri(y,m,n):
    d=pd.Timestamp(y,m,1); d+=pd.Timedelta(days=(4-d.weekday())%7); return d+pd.Timedelta(weeks=n-1)
def last_fri(y,m):
    d=pd.Timestamp(y,m,1)+pd.offsets.MonthEnd(0)
    while d.weekday()!=4: d-=pd.Timedelta(days=1)
    return d
# (ann_date, first trading day with new constituents, url)
VER={
 (2018,6):("20180525","20180611","https://www.sse.com.cn/market/sseindex/diclosure/c/c_20180525_4561394.shtml"),
 (2018,12):(None,"20181217","https://www.cs.com.cn/gppd/tzzx/201812/t20181203_5899657.html"),
 (2019,6):(None,"20190617","https://finance.sina.com.cn/money/fund/jjyj/2019-06-03/doc-ihvhiews6535087.shtml"),
 (2019,12):(None,"20191216","https://www.nbd.com.cn/articles/2019-12-03/1390828.html"),
 (2020,6):(None,"20200615","http://www.zqrb.cn/stock/gupiaoyaowen/2020-06-01/A1590963843606.html"),
 (2020,12):("20201127","20201214","http://www.sse.com.cn/market/sseindex/diclosure/c/c_20201127_5268298.shtml"),
 (2021,6):("20210528","20210615","https://www.nmgttcy.com/caijing/2021053033785.html"),
 (2021,12):("20211126","20211213","http://finance.ce.cn/stock/gsgdbd/202111/27/t20211127_37121432.shtml"),
 (2022,12):("20221125","20221212","https://www.cs.com.cn/gppd/gsyj/202211/t20221125_6310359.html"),
 (2023,6):("20230526","20230612","http://m.yuebao.yktchina.com/kj/2023/0527/12574.html"),
 (2023,12):("20231124","20231211","https://www.yicai.com/brief/101911781.html"),
 (2024,6):("20240531","20240617","https://www.stcn.com/article/detail/1220049.html"),
 (2024,12):("20241129","20241216","https://finance.sina.com.cn/stock/relnews/cn/2024-11-29/doc-incxtvcm1811148.shtml"),
 (2025,6):("20250530","20250616","https://finance.sina.com.cn/money/fund/fundzmt/2025-05-30/doc-ineyixvc7718850.shtml"),
 (2025,12):("20251128","20251215","https://finance.sina.com.cn/stock/hkstock/hkstocknews/2025-11-28/doc-infyyhva7246962.shtml"),
 (2026,6):("20260529","20260615","web_search_2026-10-13(多家媒体: 5/29公告, 6/12收市后生效)"),
}
rows=[]
for y in range(2018,2027):
    for m in (6,12):
        ann_r=last_fri(y,m-1).strftime("%Y%m%d"); eff_r=nexttd(nth_fri(y,m,2))
        a,e,src=VER.get((y,m),(None,None,None))
        future=(y,m)==(2026,12)
        q="public_report" if a else ("scheduled_future_rule" if future else "rule_inferred")
        rows.append(dict(review=f"{y}-{m:02d}",ann_date=a or ann_r,ann_date_source="public_report" if a else "rule_inferred(last Friday of prior month)",
            effective_date=e or eff_r,effective_source="public_report" if e else "rule_inferred(trading day after 2nd Friday close)",
            rule_effective_check=eff_r,source_url=src,quality_status=q,
            indices="000300.SH,000905.SH,000852.SH"))
t=pd.DataFrame(rows); t["available_at"]=pd.to_datetime(t.ann_date)+pd.Timedelta(hours=20)
t["available_at_tz"]="Asia/Shanghai"; t["promotion_approved"]=False
t.to_parquet(D/"csi_review_calendar.parquet",index=False)
ev=pd.read_parquet(D/"index_member_events.parquet")
ev=ev.drop(columns=[x for x in ["ann_date","effective_date","ann_date_source","available_at","quality_status","promotion_approved"] if x in ev])
ev=ev.merge(t[["review","ann_date","effective_date","ann_date_source","available_at","quality_status"]],on="review",how="left")
ev.loc[ev.review.isna(),"quality_status"]="non_periodic_no_ann"
ev["promotion_approved"]=False
ev.to_parquet(D/"index_member_events.parquet",index=False)
past=t[t.review<="2026-06"]
man=dict(table="index_members/csi_review_calendar + index_member_events (D5)",rows_calendar=len(t),rows_events=len(ev),
 date_range=[t.ann_date.min(),t.ann_date.max()],reviews_public=int((past.quality_status=="public_report").sum()),reviews_rule=int((past.quality_status=="rule_inferred").sum()),
 events_by_quality=ev.quality_status.value_counts().to_dict(),source="中证/上交所公告+财经媒体转载; 成分来自 tushare index_weight 月末快照",
 available_at="ann_date 20:00 Asia/Shanghai(公告多在交易日盘后发布)",promotion_approved=False,built=pd.Timestamp.now().isoformat())
json.dump(man,open(D/"manifest_d5.json","w"),ensure_ascii=False,indent=2,default=str); print(json.dumps(man,ensure_ascii=False,default=str))
