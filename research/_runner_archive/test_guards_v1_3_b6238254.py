import sys, pickle, copy
from pathlib import Path
sys.argv=["x"]; sys.path.insert(0,"research")
import optimizer_core_x2_run as R
T=Path("/tmp/ldtest2"); cs=R.code_sha256(); print("optimize_flag", sys.flags.optimize, "runner", cs["files"]["research/optimizer_core_x2_run.py"][:12], "combined", cs["combined"][:12])
s=pickle.load(open(T/"smoke.pkl","rb"))
g=copy.deepcopy(s); g["smoke"]=False; g["code_sha256"]=cs
cases={"smoke_void":s,"good":g}
cases["badsha"]=dict(g, code_sha256={"combined":"0"*64}); cases["badver"]=dict(g, version="v1_2"); cases["nover"]={k:v for k,v in g.items() if k!="version"}
for k,v in cases.items(): pickle.dump(v,open(T/f"{k}.pkl","wb"))
def tryit(name,f):
    try: f(); print(f"  {name}: ACCEPTED")
    except SystemExit as e: print(f"  {name}: REFUSED code={1 if isinstance(e.code,str) else e.code} :: {str(e.code)[:110]}")
print("loader:")
for k in ("legacy","smoke_void","badsha","badver","nover","good"): tryit(k, lambda k=k: R.load_ckpt_v13(T/f"{k}.pkl", cs))
R_=cs["files"]["research/optimizer_core_x2_run.py"]; C_=cs["combined"]
base=f"""ARCH RUN AUTH v1.3 free text ignored
format=quantlab_run_auth_v1
version=v1_3
signed_by=arch
signed_et=2026-10-18 00:40 ET
allow_full={{full}}
allow_smoke={{smk}}
runner_sha256={{r}}
combined_sha256={{c}}
smoke_days={{sd}}
"""
def ok(name, **kw):
    d=dict(full="true",smk="false",r=R_,c=C_,sd=""); d.update(kw); (T/f"{name}.ok").write_text(base.format(**d)); return T/f"{name}.ok"
print("auth:")
tryit("real_current_ok_parse", lambda: R.parse_run_auth(T/"real.ok"))
tryit("missing_file", lambda: R.parse_run_auth(T/"nope.ok"))
for name,kw,smk in [("full_allowed",{},[]),("full_not_allowed",{"full":"false"},[]),
    ("smoke_not_allowed",{},["2026-09-30"]),("smoke_allowed_in_list",{"smk":"true","sd":"2026-09-30,2025-11-28"},["2026-09-30"]),
    ("smoke_day_not_listed",{"smk":"true","sd":"2026-09-30"},["2024-06-28"]),("smoke_allowed_empty_list",{"smk":"true"},["2026-09-30"]),
    ("runner_sha_mismatch",{"r":"a"*64},[]),("combined_sha_mismatch",{"c":"b"*64},[]),("bool_typo",{"smk":"yes"},[]),("short_sha",{"r":"abc"},[])]:
    p=ok(name,**kw); tryit(name, lambda p=p,smk=smk: R.enforce_run_auth(R.parse_run_auth(p), cs, smk))
p=ok("dup"); p.write_text(p.read_text()+"allow_smoke=true\n"); tryit("duplicate_field", lambda: R.parse_run_auth(p))
