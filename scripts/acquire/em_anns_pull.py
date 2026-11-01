"""东财按股票补 2018-01-01→2024-05-31 公告（只拉优先名单，从尾部往前；与巨潮按股票进程分工）。
跳过巨潮或东财已落文件的股票。输出 data/v2/announcements/eastmoney/by_stock/{sh.600000}.parquet
available_at 由构建脚本按公告日 23:59 保守口径（display_time 仅留作参考）。限速+退避，坏信号自动降速。"""
import os,time,random,pathlib,collections,requests,pandas as pd
R=pathlib.Path("/workspace/QuantLab"); C=R/"data/v2/announcements/cninfo/by_stock"; O=R/"data/v2/announcements/eastmoney/by_stock"; O.mkdir(parents=True,exist_ok=True)
LOG=open(R/"logs/em_anns.log","a"); SLEEP=float(os.environ.get("EM_SLEEP",0.6)); A,B="2018-01-01","2024-05-31"
H={"User-Agent":"Mozilla/5.0","Referer":"https://data.eastmoney.com/"}; s=requests.Session(); s.headers.update(H)
win=collections.deque(maxlen=40)
def get(code,p):
    global SLEEP
    for i in range(7):
        ok=False
        try:
            r=s.get("https://np-anotice-stock.eastmoney.com/api/security/ann",params=dict(sr=-1,page_size=100,page_index=p,ann_type="A",client_source="web",stock_list=code,f_node=0,s_node=0),timeout=25)
            if r.status_code==200: d=r.json().get("data") or {}; ok=True
            else: LOG.write(f"HTTP {r.status_code} {code} p{p}\n")
        except Exception as e: LOG.write(f"ERR {code} p{p} {str(e)[:80]}\n")
        win.append(ok); LOG.flush()
        if len(win)>=20 and win.count(False)/len(win)>0.2:
            SLEEP=min(5,SLEEP*2); LOG.write(f"BACKOFF sleep={SLEEP}\n"); win.clear(); time.sleep(120)
        time.sleep(SLEEP+random.random()*0.3)
        if ok: return d
        time.sleep(min(300,5*2**i))
    raise RuntimeError("giveup")
def one(iid):
    if (C/f"{iid}.parquet").exists() or (O/f"{iid}.parquet").exists(): return "skip"
    code=iid.split(".")[1]; rows=[]; p=1
    while p<=60:
        L=(get(code,p).get("list") or [])
        for x in L:
            nd=str(x.get("notice_date",""))[:10]
            if A<=nd<=B: rows.append({"title":x.get("title"),"notice_date":nd,"display_time":x.get("display_time"),"art_code":x.get("art_code"),
                "column":";".join(c.get("column_name","") for c in (x.get("columns") or [])),"secName":(x.get("codes") or [{}])[0].get("short_name")})
        if len(L)<100 or str(L[-1].get("notice_date",""))[:10]<A: break
        p+=1
    df=pd.DataFrame(rows,columns=["title","notice_date","display_time","art_code","column","secName"]); df["instrument"]=iid
    df.astype(str).to_parquet(O/f"{iid}.parquet",index=False); return len(df)
if __name__=="__main__":
    pr=open(R/"data/v2/announcements/cninfo/priority_csi300_500.txt").read().split()
    ids=[f"{c.split('.')[1].lower()}.{c.split('.')[0]}" for c in pr][::-1]
    print("START",len(ids),"sleep",SLEEP,flush=True); n=0
    for k,i in enumerate(ids):
        # 两进程交汇：剩余未拉 < 3 就停（巨潮那边正在拉）
        try: r=one(i)
        except Exception as e: LOG.write(f"FAIL {i} {e}\n"); r="fail"
        if r not in("skip","fail"): n+=1
        if k%25==0: print(time.strftime("%H:%M:%S"),k,"new",n,"sleep",SLEEP,flush=True)
    print("DONE",n,flush=True)
