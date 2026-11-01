"""Arch r3 audit probe (read-only). Replays the D1b restore loop of build_cs_panel_v2_resumefix.py (sha 29f66d98)
using sd1_common.ResumeState (sha-verified) to count rows that would hit the P2-5 VOID assertion
(isr and carry state None), plus restored counts and spot rows. Writes only a JSON next to this file."""
import sys, json, hashlib, resource
from pathlib import Path
import pandas as pd
R = Path("/workspace/QuantLab"); H = R / "scripts/fix_sd1"
assert hashlib.sha256((H/"sd1_common.py").read_bytes()).hexdigest() == "91eb61b433ea835f8174670a2a1c6a583b7a4e78c29d85884a319ad13f7516ca"
sys.path.insert(0, str(H)); import sd1_common as C
RAW = R/"data/v2/tushare_raw"; MASK = R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
state = C.ResumeState(); first = None
SPOT = {("002445.SZ","2026-03-09"),("002090.SZ","2025-07-23"),("300658.SZ","2026-01-19"),("603007.SH","2026-04-21"),("002445.SZ","2026-08-24")}
res = {"void_trigger_rows": [], "by_year": {}, "spot": {}}
for y in [int(a) for a in sys.argv[1:]] or C.YEARS:
    m = pd.read_parquet(MASK, filters=[("date",">=",pd.Timestamp(f"{y}-01-01")),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    m["fulla"] = (~m.st) & (~m.suspended) & (~m.young) & (m.adv20_yuan >= 3e6); m["keep_v1"] = m.fulla | m.in_universe
    yr = dict(resume=0, restored_resume=0, restored_intra=0, hc=0, fc=0, void=0)
    for d, g in m.groupby("date", sort=True):
        d = pd.Timestamp(d); p = RAW/f"daily/{d:%Y%m%d}.parquet"; s = RAW/f"suspend_d/{d:%Y%m%d}.parquet"
        if not p.exists(): continue
        if first is None: first = d; state.seed_listed(g.instrument[~g.young.astype(bool)])
        x = pd.read_parquet(p, columns=["ts_code","vol","amount"])
        vp = set(x.ts_code[x.vol>0]); ap = set(x.ts_code[x.amount>0]); full=intra=Rr=set()
        if s.exists():
            z = pd.read_parquet(s, columns=["ts_code","suspend_type","suspend_timing"])
            t = z.suspend_timing.astype("string").str.strip(); ht = z.suspend_timing.notna() & t.notna() & ~t.isin(["","None","nan"])
            full = set(z.ts_code[(z.suspend_type=="S") & ~ht]); intra = set(z.ts_code[(z.suspend_type=="S") & ht]) - full; Rr = set(z.ts_code[z.suspend_type=="R"])
        rs, info = state.step(d, vp, ap, full, Rr); upd = []
        for c, su, h, f, k in zip(g.instrument, g.suspended, g.in_universe, g.fulla, g.keep_v1):
            tr = c in vp; isr = c in rs; ih = c in intra
            if isr: yr["resume"] += 1
            if su and tr and not k and c not in full and (isr or ih):
                lh, lf = state.carry(c)
                if isr and lh is None:
                    yr["void"] += 1
                    if len(res["void_trigger_rows"]) < 40: res["void_trigger_rows"].append([c, str(d.date()), str(info.get(c))])
                    lh = lf = False
                hc, fc = bool(lh), bool(lf)
                if hc or fc:
                    yr["restored_resume" if isr else "restored_intra"] += 1; yr["hc"] += hc; yr["fc"] += fc
                if (c, str(d.date())) in SPOT: res["spot"][f"{c} {d.date()}"] = dict(isr=isr, ih=ih, hc=hc, fc=fc, info=str(info.get(c)))
            elif (c, str(d.date())) in SPOT: res["spot"][f"{c} {d.date()}"] = dict(isr=isr, ih=ih, su=bool(su), keep_v1=bool(k), note="not a restore candidate")
            if tr and not su: upd.append((c, h, f))
        state.update_pool(upd)
    res["by_year"][y] = yr; print(y, yr, flush=True); del m
res["first_session"] = str(first.date()); res["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
(Path(__file__).parent/"carry_none_probe.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != "by_year"}, ensure_ascii=False))
