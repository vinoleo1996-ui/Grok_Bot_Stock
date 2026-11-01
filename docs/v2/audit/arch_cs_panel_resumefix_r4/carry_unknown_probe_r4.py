"""Arch r4 audit probe (read-only). Replays the D1b restore loop of build_cs_panel_v2_resumefix.py (sha 78b204c9, lines 61-96)
with sd1_common.ResumeState (sha 2e4c4131, verified before import; module has no import-time side effects).
Counts: new-logic VOID rows (line 87), unknown_pre_data rows split by (resume|intraday) and by whether the code had any
earlier vol>0 session in the data (pure seed vs traded-but-never-normal), plus restored counts. Writes only a JSON here."""
import sys, json, hashlib, resource
from pathlib import Path
import pandas as pd
R = Path("/workspace/QuantLab"); H = R / "scripts/fix_sd1"
assert hashlib.sha256((H/"sd1_common.py").read_bytes()).hexdigest() == "2e4c413133b36ed15c48fc907d56cf9794afedfc3299c1626e02dea90af211c9"
sys.path.insert(0, str(H)); import sd1_common as C
RAW = R/"data/v2/tushare_raw"; MASK = R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
state = C.ResumeState(); first = None; seed = set()
res = {"by_year": {}, "samples_unknown": [], "samples_nonseed_unknown": []}
for y in [int(a) for a in sys.argv[1:]]:
    m = pd.read_parquet(MASK, filters=[("date",">=",pd.Timestamp(f"{y}-01-01")),("date","<=",pd.Timestamp(f"{y}-12-31"))])
    m["fulla"] = (~m.st.astype(bool)) & (~m.suspended.astype(bool)) & (~m.young.astype(bool)) & (m.adv20_yuan >= 3e6)
    m["keep_v1"] = m.fulla | m.in_universe.astype(bool)
    yr = dict(void_new=0, unknown=0, unknown_resume=0, unknown_intra=0, unknown_pure_seed=0, unknown_traded_never_normal=0,
              old_r3_void=0, restored=0, hc=0, fc=0)
    for d, g in m.groupby("date", sort=True):
        d = pd.Timestamp(d); p = RAW/f"daily/{d:%Y%m%d}.parquet"; s = RAW/f"suspend_d/{d:%Y%m%d}.parquet"
        if not p.exists(): continue
        if first is None:
            first = d; seed = set(g.instrument[~g.young.astype(bool)]); state.seed_listed(seed)
        x = pd.read_parquet(p, columns=["ts_code","vol","amount"])
        vp = set(x.ts_code[x.vol>0]); ap = set(x.ts_code[x.amount>0]); full, intra, Rr = set(), set(), set()
        if s.exists():
            z = pd.read_parquet(s, columns=["ts_code","suspend_type","suspend_timing"])
            t = z.suspend_timing.astype("string").str.strip(); ht = z.suspend_timing.notna() & t.notna() & ~t.isin(["","None","nan"])
            full = set(z.ts_code[(z.suspend_type=="S") & ~ht]); intra = set(z.ts_code[(z.suspend_type=="S") & ht]) - full; Rr = set(z.ts_code[z.suspend_type=="R"])
        rs, info = state.step(d, vp, ap, full, Rr); upd = []
        for c, su, h, f, k in zip(g.instrument, g.suspended.astype(bool), g.in_universe.astype(bool), g.fulla, g.keep_v1):
            tr = c in vp; isr = c in rs; ih = c in intra
            if su and tr and not k and c not in full and (isr or ih):
                lh, lf = state.carry(c)
                if lh is None:
                    if isr: yr["old_r3_void"] += 1
                    if state.normal_seen(c): yr["void_new"] += 1
                    yr["unknown"] += 1; yr["unknown_resume" if isr else "unknown_intra"] += 1
                    ptd = info.get(c, (None, None))[0]
                    cls = "unknown_pure_seed" if ptd is None else "unknown_traded_never_normal"; yr[cls] += 1
                    row = [c, str(d.date()), "resume" if isr else "intraday", "seed" if c in seed else "nonseed", str(ptd)]
                    if len(res["samples_unknown"]) < 10: res["samples_unknown"].append(row)
                    if cls != "unknown_pure_seed" and len(res["samples_nonseed_unknown"]) < 20: res["samples_nonseed_unknown"].append(row)
                elif lh or lf:
                    yr["restored"] += 1; yr["hc"] += bool(lh); yr["fc"] += bool(lf)
            if tr and not su: upd.append((c, h, f))
        state.update_pool(upd)
    res["by_year"][y] = yr; print(y, yr, flush=True); del m
res["first_session"] = str(first.date()); res["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)
(Path(__file__).parent/"carry_unknown_probe_r4.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
print(json.dumps({k: v for k, v in res.items() if k != "by_year"}, ensure_ascii=False, default=str))
