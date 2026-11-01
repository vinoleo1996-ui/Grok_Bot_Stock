#!/usr/bin/env python3
"""report_rc 机构名归一 v2 → org_id (本地 0 请求; promotion_approved=false). 原始 org_name 保留.
输出: data/v2/events/report_rc_org_id_map.parquet/.csv (org_name→org_key→org_id)
      data/v2/events/report_rc_2018plus_orgid.parquet (原表 + org_name_norm + org_id)"""
import re,unicodedata,hashlib,json,pathlib,pandas as pd
R=pathlib.Path("/workspace/QuantLab"); E=R/"data/v2/events"
SUFFIX=["股份有限公司","有限责任公司","有限公司","研究咨询分公司","分公司","证券研究所","研究所","研究院","研究中心","研究部","证券投资","证券","集团","公司"]
# 别名: 同一法人或更名(非合并前不同法人). 键为去后缀后的 key.
ALIAS={"中金":"中金公司","中金公司":"中金公司","中信建投":"中信建投","申万宏源":"申万宏源","申万宏源研究":"申万宏源","国泰海通":"国泰海通",
"安信":"国投证券(原安信)","国投":"国投证券(原安信)","财富":"财信证券(原财富)","财信":"财信证券(原财富)",
"国联":"国联民生(原国联)","国联民生":"国联民生(原国联)","野村东方国际":"野村东方国际","东亚前海":"东亚前海",
"天风海南":"天风","高盛(GOLDMANSACHS)":"高盛","高盛":"高盛","BANKOFAMERICA":"美银","BANKOFAMERICASECURITIES":"美银",
"JPMORGAN":"摩根大通(海外)","CITIGROUP":"花旗","NOMURA":"野村(海外)","MACQUARIE":"麦格理","BERNSTEINRESEARCH":"伯恩斯坦",
"BERNSTEIN":"伯恩斯坦","CREDITSUISSE":"瑞信","DEUTSCHEBANK":"德意志银行","MORGANSTANLEY":"摩根士丹利","UOBKAYHIAN":"大华继显","DBS":"星展(海外)"}
def key(n):
    s=unicodedata.normalize("NFKC",str(n)).strip()           # 全角→半角
    s=re.sub(r"\s+","",s).upper()
    s=s.replace("RESEARCH","").replace("SECURITIES","") if re.fullmatch(r"[A-Z ().]+",s) else s
    for _ in range(3):
        for x in SUFFIX:
            if s.endswith(x) and len(s)>len(x)+1: s=s[:-len(x)]
    s=s.replace("天风海南","天风海南")
    if s.startswith("天风") and "海南" in s: s="天风海南"
    return s
def main():
    P=E/"report_rc_2018plus.parquet"; r=pd.read_parquet(P)
    names=pd.Series(sorted(r.org_name.dropna().unique()))
    m=pd.DataFrame({"org_name":names}); m["org_key"]=m.org_name.map(key)
    m["org_name_norm"]=m.org_key.map(lambda k: ALIAS.get(k,k))
    m["alias_rule"]=m.org_key.map(lambda k:"alias" if k in ALIAS and ALIAS[k]!=k else "suffix/width")
    ids={n:"ORG"+hashlib.sha1(n.encode()).hexdigest()[:8] for n in m.org_name_norm.unique()}
    m["org_id"]=m.org_name_norm.map(ids)
    m.to_parquet(E/"report_rc_org_id_map.parquet",index=False); m.to_csv(E/"report_rc_org_id_map.csv",index=False)
    o=r.merge(m[["org_name","org_name_norm","org_id"]],on="org_name",how="left")
    assert len(o)==len(r); o.to_parquet(E/"report_rc_2018plus_orgid.parquet",index=False)
    sha=hashlib.sha256((E/"report_rc_2018plus_orgid.parquet").read_bytes()).hexdigest()
    st=dict(rows=len(o),n_org_raw=int(names.size),n_org_after=int(m.org_id.nunique()),null_org=int(o.org_name.isna().sum()),sha256=sha,
            merged=m.groupby("org_id").org_name.apply(list).loc[lambda s:s.map(len)>1].to_dict())
    json.dump(st,open(E/"report_rc_2018plus_orgid_manifest.json","w"),ensure_ascii=False,indent=1); print(json.dumps(st,ensure_ascii=False,indent=1))
main()
