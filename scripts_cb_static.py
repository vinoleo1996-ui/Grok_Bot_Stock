import sys,os,time; sys.path.insert(0,'.')
exec(open("scripts_cb_etf_pull.py").read().split("cal=call")[0])
import pandas as pd
R="data/v2/cb/raw/"
# put probes
for api in ["cb_put","cb_resale","cb_putback","cb_price_chg","cb_rating"]:
    try: d=call(api,ts_code="113050.SH"); print("PROBE",api,len(d),list(d.columns))
    except Exception as e: print("PROBE",api,"ERR",str(e)[:120])
b=call("cb_basic"); print("cb_basic",len(b)); b.to_parquet(R+"cb_basic_raw.parquet")
fb=[]
for st in ["L","D","I"]:
    x=call("fund_basic",market="E",status=st); x["status_q"]=st; fb.append(x); print("fund_basic",st,len(x))
pd.concat(fb).to_parquet("data/v2/etf/raw/fund_basic_E.parquet")
codes=sorted(b.ts_code)
def per(api,**kw):
    out=[]
    for i,c in enumerate(codes):
        try: out.append(call(api,ts_code=c,**kw))
        except Exception as e: print("FAIL",api,c,str(e)[:80])
    d=pd.concat(out,ignore_index=True); d.to_parquet(R+f"{api}_raw.parquet"); print(api,len(d),flush=True)
per("cb_rate",fields="ts_code,rate_freq,rate_start_date,rate_end_date,coupon_rate")
per("cb_call")
per("cb_share")
