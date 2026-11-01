import json, sys, glob
p = sorted(glob.glob(f"output/ai_factory/{sys.argv[1]}/eval_resume_*.json"))[-1]; d = json.load(open(p)); print(p)
f = lambda x: "NA" if x is None else f"{x*100:.2f}%"
if d["window_perf"]:
    for k, ent in d["window_perf"].items():
        for t, m in ent.items():
            print(f"{k:13s} {t:6s} CAGR244 {f(m['cagr244'])} /252 {f(m['cagr252'])} MDD {f(m['mdd'])} exc {f(m['excess_ann244'])} resα {f(m['resid_alpha244'])} β {m['beta']:.2f} TO1s {f(m['turnover_1s_daily'])} names {m['mean_names']:.1f} yrs " + " ".join(f"{y}:{v['resid_alpha244']*100:+.1f}" for y, v in m['by_year'].items()))
for u in ("HILIQ", "FULLA"):
    x = d[u+"_x2"]; s = x["selfcheck"]; print(f"=== {u} X2 LC engine")
    print(" net CAGR244", f(s["leaf_cagr_net244"]), "252", f(s["leaf_cagr_net252"]), "MDD", f(s["mdd_leaf"]), "resα", f(s["alpha_ann_leaf"]), "β", round(s["beta_leaf"], 2), "years", {y: round(v["alpha_ann"]*100, 1) for y, v in s["by_year"].items()})
    print(" rho", {k: round(v, 3) for k, v in s["rho_resid_vs"].items()}); print(" jac max", {k: round(v["max"], 2) for k, v in s["jaccard_vs"].items()}); print(" capstats", s["cap_stats"])
    print(" gateA_prereg", x["gateA_prereg"], "jacc_reject", s["jaccard_hard_reject"], "filter_only", s["filter_only"])
    print(" decay v1", x["decay_v1"], "v1.1", x["decay_v1_1"]); c = x["cost"]; print(" cost TO2s", f(c["to_2s_mean"]), "gross", f(c["gross_cagr"]), "net", f(c["net_cagr"]), "netT1", f(c.get("net_cagr_t1")), "untradable", c["untradable"], c["reasons"])
    pg = x["lc_portfolio_gates"]; print(" LC gates verdict", pg["verdict"]); [print("  ", t, "cap", {k: round(v, 3) for k, v in pg[t]["cap"].items() if v is not None}, "ov", {k: round(v, 3) for k, v in pg[t]["overlay"].items() if v is not None}, "A", {k: round(v, 3) for k, v in pg[t]["A_debeta"].items() if v is not None}) for t in ("60w", "100w")]
    for t in ("60w", "100w"):
        m = x["marginal"][f"{t}_capacity_adv"]; print(f"  marg {t} cap {f(m['base']['cagr'])}/{f(m['base']['mdd'])} -> +leaf {f(m['with_leaf']['cagr'])}/{f(m['with_leaf']['mdd'])}  B4: {f(x['marginal'][t+'_B4']['delta']['cagr'])}pp S6: {f(x['marginal'][t+'_S6']['delta']['cagr'])}pp")
    print(" gateB_prereg_oldcap", x["gateB_prereg_oldcap"], "hiliq_cap_B", None if not x["gateB_hiliq_cap_disclosure"] else {t: (f(v["cap"]["cagr"]), f(v["cap80_leaf20"]["cagr"]), f(v["cap80_leaf20"]["mdd"]), v["beats"]) for t, v in x["gateB_hiliq_cap_disclosure"].items()})
    g = x["gate_v3_v11"]; print(" GATE_V3(v1.1)", g["pass"], g["mdd_le_25"], g["cagr_gt_cap"], "decay_keep", g["decay_keep"], "tradable", g["tradable"])
    print(" IC pool", x["factor_pool"], {h: (round(v["ic_mean"], 4), round(v["ic_t"], 2), None if v["ic_t_hac"] is None else round(v["ic_t_hac"], 2)) for h, v in x["factor_ic"].items()})
print("peak", d["peak_rss_mb"])
