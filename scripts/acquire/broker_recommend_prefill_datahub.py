"""broker_recommend 按月预填 (datahub, 中转宕机期间). 只写缺失月份 raw/broker_recommend/<mo>.parquet (source=datahub),
运行中的 560350 在 broker 步会跳过已存在月份。幂等。MemAvailable<2GB 暂停。"""
import os,sys,time,pathlib,json
ROOT=pathlib.Path("/workspace/QuantLab"); os.chdir(ROOT); sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"scripts/acquire"))
import pandas as pd
from quantlab.data_sources.tushare_proxy import datahub,_to_df
od=ROOT/"data/v2/tushare_raw/broker_recommend"; od.mkdir(parents=True,exist_ok=True)
months=[f"{y}{m:02d}" for y in range(2018,2027) for m in range(1,13) if f"{y}{m:02d}"<="202610"]
def mem(): return next(int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemAvailable"))/1e6
ok=fail=0; fails=[]
for mo in months:
    f=od/f"{mo}.parquet"
    if f.exists(): continue
    while mem()<2.0: time.sleep(60)
    try:
        s,d=datahub("broker_recommend",month=mo); t=_to_df(d)
        if s!=200: raise RuntimeError(f"{s} {str(d)[:80]}")
        t["source"]="datahub"; t.to_parquet(f,index=False); ok+=1
    except Exception as e: fail+=1; fails.append(f"{mo}:{str(e)[:80]}")
    time.sleep(0.3)
print(json.dumps(dict(ok=ok,fail=fail,fails=fails[:20]),ensure_ascii=False))
