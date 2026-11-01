# Arch read-only audit: reconcile resume-day counts. Writes only to /workspace/arch_audit. No leaf returns / IC.
import pandas as pd, numpy as np, resource, json, sys
from pathlib import Path
R=Path("/workspace/QuantLab"); RAW=R/"data/v2/tushare_raw"; MASK=R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
last_h={}   # instrument -> in_universe on last traded non-resume day (unbounded lookback)
seen=set(); res={}
prev_traded=None
alldays=sorted(p.stem for p in (RAW/"daily").glob("2*.parquet"))
for y in range(2018,2027):
    m=pd.read_parquet(MASK,columns=["date","instrument","in_universe","st","suspended","young","adv20_yuan"],filters=[("date",">=",pd.Timestamp(f"{y}-01-01")),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    c=dict(mask_susp_traded_notfull=0,true_resume_nobarprev=0,intraday_S_with_barprev=0,R_record=0,elig=0,restored_fullA_or_carry=0,
           carry_unbounded=0,carry_60d_proxy=0,restored_true_resume_only=0,v1_fulla_rows=0,flags_def_resume=0,flags_def_ipo_firstday=0)
    for d,g in m.groupby("date",sort=True):
        ds=f"{pd.Timestamp(d):%Y%m%d}"; p=RAW/f"daily/{ds}.parquet"
        x=pd.read_parquet(p,columns=["ts_code","vol"]) if p.exists() else pd.DataFrame(columns=["ts_code","vol"])
        vol=x.groupby("ts_code").vol.sum(); traded_set=set(vol.index[vol>0])
        sp=RAW/f"suspend_d/{ds}.parquet"
        s=pd.read_parquet(sp,columns=["ts_code","suspend_type","suspend_timing"]) if sp.exists() else pd.DataFrame(columns=["ts_code","suspend_type","suspend_timing"])
        t=s.suspend_timing.astype("string").str.strip(); intra=s.suspend_timing.notna()&t.notna()&~t.isin(["","None","nan"])
        S=s[s.suspend_type=="S"]; full_set=set(S.ts_code[~intra[S.index]]); sS=set(S.ts_code); Rset=set(s.ts_code[s.suspend_type=="R"])
        inst=g.instrument.to_numpy(); traded=np.fromiter((i in traded_set for i in inst),bool,len(inst))
        full=np.fromiter((i in full_set for i in inst),bool,len(inst)); inS=np.fromiter((i in sS for i in inst),bool,len(inst))
        susp=g.suspended.to_numpy(); res_d=susp&traded&~full
        barprev_false=susp&~inS   # suspended only via ~bar_prev
        elig=(~g.st.to_numpy())&(~g.young.to_numpy())&(g.adv20_yuan.to_numpy()>=3e6)
        hp=np.array([last_h.get(i,np.nan) for i in inst],dtype=float)
        carry=res_d&(hp==1.0)
        c["mask_susp_traded_notfull"]+=int(res_d.sum()); c["true_resume_nobarprev"]+=int((res_d&barprev_false).sum())
        c["intraday_S_with_barprev"]+=int((res_d&inS&~barprev_false).sum()) if False else 0
        c["R_record"]+=int((res_d&np.fromiter((i in Rset for i in inst),bool,len(inst))).sum())
        c["elig"]+=int((res_d&elig).sum()); c["restored_fullA_or_carry"]+=int((res_d&(elig|carry)).sum())
        c["carry_unbounded"]+=int(carry.sum()); c["restored_true_resume_only"]+=int((res_d&barprev_false&(elig|carry)).sum())
        fulla=(~g.st.to_numpy())&(~susp)&(~g.young.to_numpy())&(g.adv20_yuan.to_numpy()>=3e6); c["v1_fulla_rows"]+=int(((fulla)|g.in_universe.to_numpy()).sum())
        # suspend_flags_v2 definition (vol-based newres or R) & ~full
        if prev_traded is not None:
            newres=traded_set-prev_traded; fl=(newres|(Rset&traded_set))-full_set
            c["flags_def_resume"]+=len(fl); c["flags_def_ipo_firstday"]+=len(newres-seen)
        seen|=traded_set; prev_traded=traded_set
        # update state: last traded non-resume day in_universe
        upd=traded&~res_d; iu=g.in_universe.to_numpy()
        for i,v in zip(inst[upd],iu[upd]): last_h[i]=float(v)
    # 60d proxy count via Data's own function semantics is not replicated here; see note
    res[y]=c; print(y,json.dumps(c),f"rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f}MB",flush=True)
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024>1400: sys.exit("ABORT rss")
json.dump(res,open("/workspace/arch_audit/resume_counts.json","w"),indent=1)
