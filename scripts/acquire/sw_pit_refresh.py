"""SW2021 L1/L2(/L3) PIT 成分刷新: tushare index_member_all (按 L1 × is_new Y/N). 写候选表, 不覆盖已 promotion 的 industry_members_sw_l1.parquet."""
import sys, json, time, pathlib, pandas as pd
ROOT=pathlib.Path("/workspace/QuantLab"); sys.path.insert(0,str(ROOT))
from quantlab.data_sources.tushare_proxy import relay,_to_df
OUTD=ROOT/"data/v2/sw_pit"; OUTD.mkdir(parents=True,exist_ok=True)
def call(api,**kw):
    out,off=[],0
    for a in range(6):
        try:
            while True:
                s,r=relay(api,limit=3000,offset=off,**kw)
                if s!=200 or not isinstance(r,dict): raise RuntimeError(f"{s} {str(r)[:150]}")
                df=_to_df(r); out.append(df)
                if len(df)<3000: return pd.concat(out,ignore_index=True)
                off+=3000
        except Exception as e:
            print("retry",api,kw,e,flush=True); time.sleep(5*2**a); out,off=[],0
    raise RuntimeError(f"fail {api} {kw}")
cls=call("index_classify",level="L1",src="SW2021")
cls.to_parquet(OUTD/"sw2021_classify_l1.parquet",index=False)
call("index_classify",level="L2",src="SW2021").to_parquet(OUTD/"sw2021_classify_l2.parquet",index=False)
parts=[]
# relay 的 l1_code 过滤在负载下不稳定(观测到忽略过滤/截断), 改为全量 Y/N 分页后本地去重
for isn in "YN":
    df=call("index_member_all",is_new=isn); df["is_new"]=isn; parts.append(df); print("members",isn,len(df),flush=True); time.sleep(0.5)
# 再按 L1 × Y/N 分拉补齐 (全量分页在 relay 端存在截断), 合并去重
for c in cls.index_code:
    for isn in "YN":
        try:
            df=call("index_member_all",l1_code=c,is_new=isn); df["is_new"]=isn; parts.append(df[df.l1_code==c])
        except Exception as e: print("l1 fail",c,isn,e,flush=True)
        time.sleep(0.3)
m=pd.concat(parts,ignore_index=True).drop_duplicates()
print("union rows",len(m),"instruments",m.ts_code.nunique(),flush=True)
assert m.ts_code.nunique()>5000, f"too few instruments {m.ts_code.nunique()} -> relay 截断, 不落盘"
m["in_date"]=pd.to_datetime(m.in_date,errors="coerce"); m["out_date"]=pd.to_datetime(m.out_date,errors="coerce")
m["instrument_id"]=m.ts_code.str.split(".").str[1].str.lower()+"."+m.ts_code.str.split(".").str[0]
m["available_at"]=m.in_date+pd.Timedelta(hours=18)
m["source"]="tushare.index_member_all(SW2021)"; m["promotion_approved"]=False
m.to_parquet(OUTD/"sw2021_members_l1l2l3_raw.parquet",index=False)
asof=pd.Timestamp.now(tz="Asia/Shanghai").tz_localize(None).normalize()
man={}
for lv in ["l1","l2"]:
    t=m[["instrument_id","ts_code","name",f"{lv}_code",f"{lv}_name","in_date","out_date","is_new","available_at","source","promotion_approved"]].copy()
    t["out_key"]=t.out_date.fillna(pd.Timestamp("2099-12-31"))
    t=t.sort_values("in_date").groupby(["instrument_id",f"{lv}_code","out_key"],as_index=False).first().drop(columns="out_key")
    f=OUTD/f"industry_members_sw_{lv}_pit.parquet"; t.to_parquet(f,index=False)
    man[lv]=dict(path=str(f),rows=len(t),instruments=int(t.instrument_id.nunique()),n_codes=int(t[f"{lv}_code"].nunique()),
                 in_date_range=[str(t.in_date.min().date()),str(t.in_date.max().date())],current_members=int(t.out_date.isna().sum()))
man.update(source="tushare relay index_member_all + index_classify SW2021",available_at="in_date 18:00 Asia/Shanghai (Tushare 未提供公告时间, 近似)",
  note="不覆盖已 promotion 的 data/v2/sw_l1_pit/industry_members_sw_l1.parquet; 本表为 research 候选",promotion_approved=False,built=pd.Timestamp.now().isoformat())
json.dump(man,open(OUTD/"manifest.json","w"),ensure_ascii=False,indent=2); print(json.dumps(man,ensure_ascii=False))
