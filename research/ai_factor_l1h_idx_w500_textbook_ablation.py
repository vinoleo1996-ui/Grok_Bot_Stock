#!/usr/bin/env python3
"""L1h idx_w500 family: textbook corr penalty + size ablation. explore only."""
from __future__ import annotations
import gc, importlib.util, json, math, re, resource, sys, time, types
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
SCRATCH = Path("/workspace/scratch/tic")
V2 = ROOT / "data/v2"
L1H = ROOT / "output/ai_factor/l1h_new_mech_family"
OUT = ROOT / "output/ai_factor/l1h_idx_w500_textbook_ablation"
REPORT = ROOT / "output/alpha/AI_FACTOR_L1h_IDX_W500_TEXTBOOK_ABLATION_ZH.md"
LOOKBACK_START = pd.Timestamp("2024-01-02")
EXPLORE_START = pd.Timestamp("2024-06-03")
IMP60_FLOOR = 0.10
CORR_THRESHOLD = 0.5
COV_NONEMPTY_MIN = 0.08
SEED = 20261012
PROMOTION_APPROVED = False

OPS = {"add","sub","mul","div","neg","abs","rank","zscore","industry_neutral","size_neutral"}
for k in (1,5,10,20,60):
    OPS |= {f"delay_{k}", f"ts_mean_{k}", f"ts_std_{k}", f"ts_delta_{k}", f"ts_max_{k}"}

t0=0.0
def mem_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def log(*a): print(f"[idx500_abl {time.time()-t0:5.0f}s {mem_mb():.0f}MB]", *a, flush=True)
def leaves_in(expr): return {t for t in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", expr) if t not in OPS}
def clean(o):
    if isinstance(o,float) and (math.isnan(o) or math.isinf(o)): return None
    if isinstance(o,dict): return {k:clean(v) for k,v in o.items()}
    if isinstance(o,list): return [clean(x) for x in o]
    return o
def fmt_pct(x): return f"{x:.2%}" if isinstance(x,float) and math.isfinite(x) else "—"
def fmt_f(x,nd=3): return f"{x:.{nd}f}" if isinstance(x,float) and math.isfinite(x) else "—"

def core_key(expr):
    e=expr.strip()
    while True:
        m=re.fullmatch(r"(?:rank|zscore)\((.+)\)", e)
        if not m: break
        e=m.group(1)
    return e

def _ensure_pkgs():
    if "quantlab" not in sys.modules:
        q=types.ModuleType("quantlab"); q.__path__=[str(ROOT/"quantlab")]; sys.modules["quantlab"]=q
    if "quantlab.factors" not in sys.modules or not hasattr(sys.modules["quantlab.factors"],"__path__"):
        f=types.ModuleType("quantlab.factors"); f.__path__=[str(ROOT/"quantlab/factors")]; sys.modules["quantlab.factors"]=f
    def load(name,path):
        spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
        sys.modules[name]=mod; assert spec.loader; spec.loader.exec_module(mod); return mod
    load("quantlab.factors.ops", ROOT/"quantlab/factors/ops.py")
    af=types.ModuleType("quantlab.factors.ai_factory"); af.__path__=[str(ROOT/"quantlab/factors/ai_factory")]
    sys.modules["quantlab.factors.ai_factory"]=af
    for n in ("ledger","novelty","fitness","evaluate","search","structural_leaves"):
        load(f"quantlab.factors.ai_factory.{n}", ROOT/f"quantlab/factors/ai_factory/{n}.py")

def _import_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod; assert spec.loader; spec.loader.exec_module(mod); return mod

def to_nested_tuple(obj):
    if isinstance(obj,list): return tuple(to_nested_tuple(x) for x in obj)
    return obj

def _seed_to_tuple(s):
    s=s.strip()
    if s.isidentifier(): return ("leaf", s)
    m=re.fullmatch(r"neg\((.+)\)", s)
    if m: return ("op","neg",_seed_to_tuple(m.group(1)))
    m=re.fullmatch(r"rank\((.+)\)", s)
    if m: return ("op","rank",_seed_to_tuple(m.group(1)))
    m=re.fullmatch(r"zscore\((.+)\)", s)
    if m: return ("op","zscore",_seed_to_tuple(m.group(1)))
    m=re.fullmatch(r"abs\((.+)\)", s)
    if m: return ("op","abs",_seed_to_tuple(m.group(1)))
    for pref in ("delay_","ts_std_","ts_delta_","ts_max_","ts_mean_"):
        m=re.fullmatch(rf"{pref}(\d+)\((.+)\)", s)
        if m: return ("op", f"{pref}{m.group(1)}", _seed_to_tuple(m.group(2)))
    for op in ("mul","add","sub","div"):
        m=re.fullmatch(rf"{op}\((.+)\)", s)
        if m:
            inner=m.group(1); depth=0; split_at=None
            for i,ch in enumerate(inner):
                if ch=="(": depth+=1
                elif ch==")": depth-=1
                elif ch=="," and depth==0: split_at=i; break
            if split_at is None: raise ValueError(s)
            return ("op", op, _seed_to_tuple(inner[:split_at].strip()), _seed_to_tuple(inner[split_at+1:].strip()))
    raise ValueError(f"cannot parse: {s}")

def size_residualize(fac, size):
    idx=fac.index.intersection(size.index)
    cols=[c for c in fac.columns if c in size.columns]
    F=fac.reindex(index=idx,columns=cols).to_numpy(dtype=np.float64,copy=False)
    S=size.reindex(index=idx,columns=cols).to_numpy(dtype=np.float64,copy=False)
    out=np.full_like(F,np.nan)
    for t in range(F.shape[0]):
        y,x=F[t],S[t]; m=np.isfinite(y)&np.isfinite(x); n=int(m.sum())
        if n<30: continue
        yy,xx=y[m],x[m]; yy0=yy-yy.mean(); xx0=xx-xx.mean(); var=float(np.dot(xx0,xx0))
        if var<1e-18: out[t,m]=yy0; continue
        beta=float(np.dot(xx0,yy0)/var); resid=np.full(y.shape,np.nan); resid[m]=yy0-beta*xx0; out[t]=resid
    return pd.DataFrame(out,index=idx,columns=cols,dtype="float32")

def corr_with(fac, other):
    idx=fac.index.intersection(other.index)
    f=fac.reindex(idx).to_numpy(dtype=np.float64,copy=False)
    o=other.reindex(idx).to_numpy(dtype=np.float64,copy=False)
    cors=[]
    for t in range(len(idx)):
        a,b=f[t],o[t]; m=np.isfinite(a)&np.isfinite(b)
        if int(m.sum())<30: continue
        aa,bb=a[m],b[m]
        if aa.std()==0 or bb.std()==0: continue
        cors.append(float(np.corrcoef(aa,bb)[0,1]))
    return float(np.nanmean(cors)) if cors else float("nan")

def build_textbook(cal, cols, mask):
    out={}
    # size from float mktcap
    fm=pd.read_parquet(V2/"float_mktcap/float_mktcap_daily_tushare.parquet",
        columns=["trade_date","instrument_id","float_mktcap"],
        filters=[("trade_date",">=", LOOKBACK_START)])
    fm["trade_date"]=pd.to_datetime(fm["trade_date"]); fm=fm[fm.instrument_id.isin(cols)]
    wide=(fm.drop_duplicates(["trade_date","instrument_id"],keep="last")
          .set_index(["trade_date","instrument_id"])["float_mktcap"].unstack()
          .reindex(index=cal,columns=cols).astype("float32"))
    if mask is not None: wide=wide.where(mask)
    out["size"]=np.log(wide.where(wide>0)).astype("float32"); del fm,wide; gc.collect()
    # EP
    ep_path=V2/"ep/ep_pit_daily_tushare.parquet"
    if ep_path.exists():
        ep=pd.read_parquet(ep_path, columns=["trade_date","instrument_id","ep"],
            filters=[("trade_date",">=", LOOKBACK_START-pd.Timedelta(days=5))])
        ep["trade_date"]=pd.to_datetime(ep["trade_date"]); ep=ep[ep.instrument_id.isin(cols)]
        w=(ep.dropna(subset=["ep"]).sort_values(["trade_date","instrument_id"])
           .drop_duplicates(["trade_date","instrument_id"],keep="last")
           .set_index(["trade_date","instrument_id"])["ep"].unstack()
           .reindex(index=cal,columns=cols).astype("float32").ffill(limit=5))
        if mask is not None: w=w.where(mask)
        out["EP"]=w.astype("float32"); del ep,w; gc.collect()
    # BM / turnover
    val_path=V2/"valuation/daily_basic_valuation_tushare.parquet"
    if val_path.exists():
        val=pd.read_parquet(val_path, columns=["trade_date","instrument_id","pb","pe_ttm"],
            filters=[("trade_date",">=", LOOKBACK_START-pd.Timedelta(days=5))])
        val["trade_date"]=pd.to_datetime(val["trade_date"]); val=val[val.instrument_id.isin(cols)]
        def pivot(col):
            sub=val[["trade_date","instrument_id",col]].dropna(subset=[col])
            sub=sub.sort_values(["trade_date","instrument_id"]).drop_duplicates(["trade_date","instrument_id"],keep="last")
            w=sub.set_index(["trade_date","instrument_id"])[col].unstack().reindex(index=cal,columns=cols).astype("float32").ffill(limit=5)
            if mask is not None: w=w.where(mask)
            return w.astype("float32")
        pb=pivot("pb"); out["BM"]=(1.0/pb.replace(0,np.nan)).astype("float32"); del val,pb; gc.collect()
    tov=pd.read_parquet(SCRATCH/"turnover.parquet", columns=cols).astype("float32")
    tov=tov.loc[tov.index>=LOOKBACK_START].reindex(index=cal,columns=cols)
    turn20=tov.rolling(20,min_periods=10).mean().astype("float32")
    if mask is not None: turn20=turn20.where(mask)
    out["turnover"]=turn20; del tov,turn20; gc.collect()
    return out

def main():
    global t0; t0=time.time()
    OUT.mkdir(parents=True, exist_ok=True); REPORT.parent.mkdir(parents=True, exist_ok=True)
    _ensure_pkgs()
    l1h=_import_mod("ai_factor_l1h_new_mech_family_explore", ROOT/"research/ai_factor_l1h_new_mech_family_explore.py")
    l1b=_import_mod("ai_factor_l1b_structural_explore", ROOT/"research/ai_factor_l1b_structural_explore.py")
    sci=_import_mod("ai_factor_l1d_shortlist_coverage_impact", ROOT/"research/ai_factor_l1d_shortlist_coverage_impact.py")
    from quantlab.factors.ai_factory.ledger import append_attempt
    from quantlab.factors.ops import apply_expr, parse_expr

    gate_ok=json.loads((L1H/"gate_ok.json").read_text())
    # focus idx_w500 family (+ rank twins collapsed by core_key)
    idx_rows=[r for r in gate_ok if "idx_w500" in r.get("expr","")]
    # unique cores
    cores={}
    for r in idx_rows:
        ck=core_key(r["expr"])
        if ck not in cores or (r.get("metrics") or {}).get("imp60_p25",-1) > (cores[ck].get("metrics") or {}).get("imp60_p25",-1):
            cores[ck]=r
    parents=sorted(cores.values(), key=lambda r: -((r.get("metrics") or {}).get("imp60_p25") or -1))
    log("idx_w500 GATE_OK", len(idx_rows), "unique cores", len(parents), [p["expr"] for p in parents])

    log("load structural for mask")
    panels, label, public, load_meta = l1b.load_structural_panels()
    peak=mem_mb()
    if "overnight_ret" in panels:
        mask=panels["overnight_ret"].notna(); cols=list(panels["overnight_ret"].columns); cal=panels["overnight_ret"].index
    else:
        cols=list(next(iter(panels.values())).columns); cal=next(iter(panels.values())).index; mask=None
    for k in list(panels): del panels[k]
    panels={}; gc.collect()

    idx_panels, idx_gap = l1h.build_idx_panels(cal, cols, mask)
    panels.update(idx_panels); del idx_panels; gc.collect()
    log("idx panels", sorted(panels.keys())[:12], "gap", idx_gap.get("ok"), "peak", mem_mb())

    textbook=build_textbook(cal, cols, mask)
    size_panel=textbook.get("size")
    sig, adv = sci.load_sig_adv(cols, cal)
    peak=max(peak, mem_mb())

    main_ledger=ROOT/"output/ai_factor/ledger.jsonl"
    run_ledger=OUT/"ledger_run.jsonl"
    if run_ledger.exists(): run_ledger.unlink()
    n_before=sum(1 for x in main_ledger.read_text().splitlines() if x.strip()) if main_ledger.exists() else 0

    corr_rows=[]; verdicts=[]; results=[]; survivors=[]; demoted=[]
    for parent_row in parents:
        parent=core_key(parent_row["expr"])
        # prefer non-rank form as parent for eval
        expr=parent
        log("core", expr)
        try:
            tup=_seed_to_tuple(expr)
            fac=apply_expr(parse_expr(to_nested_tuple(tup)), panels).astype("float32")
        except Exception as exc:
            log("skip parse", expr, exc); continue
        cov=sci.coverage_stats(fac); cs=sci.cs_std_stats(fac)
        sim=sci.simulate_book(fac,label,sig,adv) if cs.get("passes_cs_variation") else {"skipped":True}
        base_m=sci.pack_metrics(None if sim.get("skipped") else sim)

        # corr vs textbook (esp size — 防市值壳)
        corr_map={}
        for name,panel in textbook.items():
            c=corr_with(fac.loc[fac.index>=EXPLORE_START], panel.loc[panel.index>=EXPLORE_START])
            corr_map[name]=c
        max_name=None; max_abs=0.0
        for n,c in corr_map.items():
            if isinstance(c,float) and math.isfinite(c) and abs(c)>max_abs:
                max_abs=abs(c); max_name=n
        demote=bool(max_abs>CORR_THRESHOLD)
        corr_info={"expr":expr,"corr":corr_map,"max_abs_corr":max_abs,"max_corr_name":max_name,"demote_textbook":demote}

        # ablations: sign_flip, delay_5, static leaf, size residual
        abl_jobs=[
            ("sign_flip", f"neg({expr})"),
            ("delay_5", f"delay_5({expr})"),
            ("static_idx_w500", "idx_w500"),
            ("static_neg_idx_w500", "neg(idx_w500)"),
            ("size_neutral_manual", None),
        ]
        abl_rows=[]
        for abl_name, abl_expr in abl_jobs:
            try:
                if abl_name=="size_neutral_manual":
                    if size_panel is None: continue
                    fac_a=size_residualize(fac, size_panel)
                else:
                    fac_a=apply_expr(parse_expr(to_nested_tuple(_seed_to_tuple(abl_expr))), panels).astype("float32")
                cov_a=sci.coverage_stats(fac_a); cs_a=sci.cs_std_stats(fac_a)
                sim_a=sci.simulate_book(fac_a,label,sig,adv) if cs_a.get("passes_cs_variation") else {"skipped":True}
                m_a=sci.pack_metrics(None if sim_a.get("skipped") else sim_a)
                abl_rows.append({"ablation":abl_name,"expr":abl_expr or f"__SIZE_RESID__::{expr}",
                                 "metrics":m_a,"coverage":cov_a,"promotion_approved":False})
                del fac_a; gc.collect()
            except Exception as exc:
                abl_rows.append({"ablation":abl_name,"error":str(exc),"promotion_approved":False})

        # honesty
        fails=[]; notes=[]; flags=[]
        if demote:
            fails.append("textbook_corr_gt_0.5")
            notes.append(f"教科书相关惩罚 max|corr|={fmt_f(max_abs)} vs {max_name} → DEMOTE")
        # size kill
        sz=next((r for r in abl_rows if r.get("ablation")=="size_neutral_manual"), None)
        if sz and isinstance((sz.get("metrics") or {}).get("imp60_p25"), float):
            if not math.isfinite(sz["metrics"]["imp60_p25"]) or sz["metrics"]["imp60_p25"] <= 0:
                fails.append("size_kills_edge"); notes.append("size 残差后≤0 — 疑市值通道")
            elif base_m.get("imp60_p25") and sz["metrics"]["imp60_p25"] < 0.5 * base_m["imp60_p25"]:
                flags.append("size_sensitive"); notes.append(f"size 残差后腰斩至 {fmt_pct(sz['metrics']['imp60_p25'])}")
        # sign flip better?
        sf=next((r for r in abl_rows if r.get("ablation")=="sign_flip"), None)
        if sf and isinstance((sf.get("metrics") or {}).get("imp60_p25"), float) and isinstance(base_m.get("imp60_p25"), float):
            if math.isfinite(sf["metrics"]["imp60_p25"]) and sf["metrics"]["imp60_p25"] > base_m["imp60_p25"] + 0.02:
                fails.append("sign_flip_better"); notes.append("取负显著更赚 — 符号不稳")
        # hard gate recheck
        impact_ok=(math.isfinite(base_m.get("flat25",float("nan"))) and base_m["flat25"]>0
                   and math.isfinite(base_m.get("imp60_p25",float("nan"))) and base_m["imp60_p25"]>=IMP60_FLOOR
                   and math.isfinite(base_m.get("imp100_p25",float("nan"))) and base_m["imp100_p25"]>=IMP60_FLOOR)
        icir_ok=math.isfinite(base_m.get("icir",float("nan"))) and base_m["icir"]>0
        cov_ok=bool(cov.get("passes_coverage"))
        if not cov_ok: fails.append("coverage")
        if not impact_ok: fails.append("impact_gate")
        if not icir_ok: fails.append("icir_le_0")

        if demote or "size_kills_edge" in fails or "sign_flip_better" in fails:
            verdict="DEMOTE_TEXTBOOK" if demote else "FAIL_ABLATION"
        elif fails:
            verdict="FAIL_GATE"
        else:
            verdict="SURVIVE"
        v={"expr":expr,"verdict":verdict,"fails":fails,"flags":flags,"notes":notes,
           "metrics":base_m,"coverage":cov,"corr":corr_info,"ablations":abl_rows,
           "promotion_approved":False,"gate_ok":verdict=="SURVIVE"}
        verdicts.append(v); corr_rows.append(corr_info); results.append(v)
        if verdict=="SURVIVE": survivors.append(v)
        elif demote: demoted.append(v)

        fit=base_m.get("imp60_p25")
        append_attempt(engine="idx_w500_ablation", seed=SEED, universe="midlarge_top1500",
                       cost=0.0025, window="l1h_idx_w500_textbook_ablation_explore",
                       expr_str=expr, fitness=float(fit) if isinstance(fit,float) and math.isfinite(fit) else None,
                       notes=f"verdict={verdict};max_corr={max_abs:.3f}@{max_name};ablation", path=run_ledger)
        append_attempt(engine="idx_w500_ablation", seed=SEED, universe="midlarge_top1500",
                       cost=0.0025, window="l1h_idx_w500_textbook_ablation_explore",
                       expr_str=expr, fitness=float(fit) if isinstance(fit,float) and math.isfinite(fit) else None,
                       notes=f"verdict={verdict};max_corr={max_abs:.3f}@{max_name};ablation", path=main_ledger)
        del fac; gc.collect()
        peak=max(peak, mem_mb())

    n_after=sum(1 for x in main_ledger.read_text().splitlines() if x.strip())
    summary={
        "promotion_approved":False,"sealed":False,"strategy_weights":False,
        "n_idx_w500_gate_ok":len(idx_rows),"n_cores":len(parents),
        "n_survive":len(survivors),"n_demote_textbook":len(demoted),
        "ledger_N_before":n_before,"ledger_N_after":n_after,
        "peak_rss_MB":round(peak),"runtime_s":round(time.time()-t0,1),
        "survive_exprs":[s["expr"] for s in survivors],
        "corr_threshold":CORR_THRESHOLD,
    }
    (OUT/"corr_screen.json").write_text(json.dumps(clean(corr_rows),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"verdicts.json").write_text(json.dumps(clean(verdicts),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"survivors.json").write_text(json.dumps(clean(survivors),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"demoted_textbook.json").write_text(json.dumps(clean(demoted),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"alpha_handback_package.json").write_text(json.dumps(clean({
        "promotion_approved":False,"for_alpha_shortlist_adjudication":True,
        "not_strategy_weights":True,"diagnostic_overlay_candidates_only":True,
        "source":"l1h_idx_w500_textbook_ablation",
        "survivors":[{
            "expr":s["expr"],
            "nonempty_rate":(s.get("coverage") or {}).get("nonempty_rate"),
            "flat25":(s.get("metrics") or {}).get("flat25"),
            "imp60_p25":(s.get("metrics") or {}).get("imp60_p25"),
            "imp100_p25":(s.get("metrics") or {}).get("imp100_p25"),
            "icir":(s.get("metrics") or {}).get("icir"),
            "max_abs_public_corr":(s.get("corr") or {}).get("max_abs_corr"),
            "max_corr_name":(s.get("corr") or {}).get("max_corr_name"),
            "rank_fill_cov":False,"verdict":s["verdict"],"flags":s.get("flags"),
        } for s in survivors],
        "demoted_textbook":[{"expr":d["expr"],"max_abs_corr":(d.get("corr") or {}).get("max_abs_corr"),
                             "max_corr_name":(d.get("corr") or {}).get("max_corr_name")} for d in demoted],
    }),indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"summary.json").write_text(json.dumps(clean(summary),indent=2,ensure_ascii=False),encoding="utf-8")

    lines=["# L1h idx_w500 教科书相关惩罚 + 消融",
           "",
           "- **时间：** 2026-10-12（America/New_York）",
           "- **promotion_approved：** false；**密封：** 未开；**不交 Strategy 权重**",
           "- **本金：** 60万 / 100万；主裁决=冲击+flat25",
           f"- 上游：L1h GATE_OK idx_w500；账本 N {n_before}→{n_after}",
           f"- 峰值 RSS：{peak:.0f} MB；运行 {summary['runtime_s']}s",
           "",
           "## 规则",
           f"- |corr|>{CORR_THRESHOLD} vs EP/BM/size/turnover → **DEMOTE_TEXTBOOK**（防市值壳）",
           "- size 残差后≤0 → FAIL_ABLATION",
           "- 冲击+25bp@60∧100万≥10% ∧ ICIR>0 ∧ 覆盖硬过 才可 SURVIVE",
           "",
           "## 核心结果",
           "",
           "| # | 表达式 | flat25 | 60万+25bp | 100万+25bp | ICIR | max|corr| | vs | 裁决 |",
           "|---|---|---:|---:|---:|---:|---:|---|---|"]
    for i,v in enumerate(verdicts,1):
        m=v.get("metrics") or {}; c=v.get("corr") or {}
        lines.append(f"| {i} | `{v['expr']}` | {fmt_pct(m.get('flat25'))} | {fmt_pct(m.get('imp60_p25'))} | "
                     f"{fmt_pct(m.get('imp100_p25'))} | {fmt_f(m.get('icir'))} | {fmt_f(c.get('max_abs_corr'))} | "
                     f"{c.get('max_corr_name')} | {v['verdict']} |")
    lines += ["",
              f"1. **SURVIVE（可回传 Alpha 短清单裁决）：** {len(survivors)}",
              f"2. **DEMOTE_TEXTBOOK：** {len(demoted)}",
              "3. **不开密封、不交 Strategy**；仅 diagnostic_overlay_candidate",
              "",
              "## 产物",
              f"- 报告：`{REPORT.relative_to(ROOT)}`",
              f"- JSON：`output/ai_factor/l1h_idx_w500_textbook_ablation/`",
              f"- 回传包：`output/ai_factor/l1h_idx_w500_textbook_ablation/alpha_handback_package.json`",
              f"- 账本 N={n_after}",
              ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    log("DONE", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
