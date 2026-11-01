#!/usr/bin/env python3
"""Downstream eval for leaf19 cfacc_rnoa / leaf20 sue_resid / leaf18v overnight_idio_ivol_lowto (resume after 10-15 stall).
Reuses alpha/gate/eval-weights already built under FROZEN preregs (no rebuild, no param change).
Steps: window×tier perf (sealed+X2, 60万/100万, cs_panel T+1 open engine of g1g5_fund_resid_alpha, 244/252),
selfcheck (de-β α, by-year, ρ/Jaccard vs capacity_adv old+HI_LIQ & legs), decay v1 + v1.1, cost/tradability,
LC Gate A/B (portfolio gates), prereg Gate A/B, leaf_selfcheck_v3 (new pool, ic_t_hac disclosure), GATE_V3 (with v1.1 decay).
live=false; promotion=false; no Book-Smoke; no 8787. Usage: --leaf 19|20|18v"""
import argparse, json, sys, resource, gc
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.leaf_selfcheck_common as LC
import research.leaf_selfcheck_v3 as V3
import research.alpha_decay_gate as ADG
import research.alpha_decay_gate_v1_1 as ADG11
import research.g1g5_fund_resid_alpha as FE
AF = R/"output/ai_factory"; HL = R/"output/strategy_hiliq/legs"
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
CFG = {
 "19": dict(name="cfacc_rnoa", dir="leaf19_cfacc_rnoa", tags=("cfacc_rnoa", "cfacc_rnoa_fulla"),
            ew={"HILIQ": {"sealed": "eval_weights_HILIQ_sealed_20261014_213132", "x2": "eval_weights_HILIQ_x2_20261014_213132"},
                "FULLA": {"sealed": "eval_weights_FULLA_sealed_20261014_213132", "x2": "eval_weights_FULLA_x2_20261014_213132"}},
            prereg="docs/v2/AI_G1G5_CFACC_RNOA_WHO_PAYS_PREREG_ZH.md",
            who="高应计(现金含量低)+RNOA未改善被按报表利润高估；只看EPS增速者付钱。base-α=rank(-CFACC)+rank(ΔRNOA)池内残差化(行业+市值+mom20/60+vol20+logADV)分域标定；快门3日残差左尾不入α；20日再平衡",
            lag="财报 available_at 次一日起；同期取最早版本"),
 "20": dict(name="sue_resid", dir="leaf20_sue_resid", tags=("sue_resid", "sue_resid_fulla"),
            ew={"HILIQ": {"sealed": "eval_weights_HILIQ_sealed_20261014_220029", "x2": "eval_weights_HILIQ_x2_20261014_220029"},
                "FULLA": {"sealed": "eval_weights_FULLA_sealed_20261014_220029", "x2": "eval_weights_FULLA_x2_20261014_220029"}},
            prereg="docs/v2/AI_G1G5_SUE_RESID_WHO_PAYS_PREREG_ZH.md",
            who="PEAD 去敏残差：扣行业/市值/动量/波动/logADV 后的纯季度盈余意外；锚定旧盈利者付钱。时间序列SUE，不用一致预期；≤60交易日有效；20日再平衡",
            lag="财报 available_at 次一日起；公告后≤90自然日"),
 "21": dict(name="biz_climate", dir="leaf21_biz_climate", tags=("biz_climate", "biz_climate_fulla"),
            ew={"HILIQ": {"sealed": "eval_weights_HILIQ_sealed_20261018_003628", "x2": "eval_weights_HILIQ_x2_20261018_003628"},
                "FULLA": {"sealed": "eval_weights_FULLA_sealed_20261018_003628", "x2": "eval_weights_FULLA_x2_20261018_003628"}},
            prereg="docs/v2/AI_G1G5_BIZ_CLIMATE_WHO_PAYS_PREREG_ZH.md",
            who="经营景气：合同负债(含预收)同比扩张/平均总资产 + 存货周转同比加快，SW L1 内标准化，剔金融；池内残差化(行业+市值+mom20/60+vol20+logADV)分域标定；快门3日残差左尾不入α；20日再平衡",
            lag="资产负债表/利润表 available_at 次一日起；同期取最早版本；>200 自然日无新报告视为过期"),
 "22": dict(name="rd_innov", dir="leaf22_rd_innov", tags=("rd_innov", "rd_innov_fulla"),
            ew={"HILIQ": {"x2": "eval_weights_HILIQ_x2_20261018_005339"}, "FULLA": {"x2": "eval_weights_FULLA_x2_20261018_005339"}},
            prereg="docs/v2/AI_G1G5_RD_INNOV_WHO_PAYS_PREREG_ZH.md",
            who="研发强度：z(RD_ttm/平均总资产)+z(Δ研发/收入)−z(资本化占比)，SW L1 内标准化，剔金融；池内残差化(行业+市值+mom20/60+vol20+logADV+叶19 α)分域标定；快门3日残差左尾不入α；20日再平衡",
            lag="利润表 ann_date 次日起（最早版本）；资产负债表 available_at 次日起；>200 自然日视为过期"),
 "18v": dict(name="overnight_idio_ivol_lowto", dir="leaf18v_overnight_idio_ivol_lowto", tags=("overnight_idio_ivol_lowto_hiliq", "overnight_idio_ivol_lowto_fulla"),
            ew={"HILIQ": {"sealed": "eval_weights_HILIQ_sealed_20261014_213446", "x2": "eval_weights_HILIQ_x2_20261014_212630"},
                "FULLA": {"sealed": "eval_weights_FULLA_sealed_20261014_215531", "x2": "eval_weights_FULLA_x2_20261014_214401"}},
            prereg="docs/v2/AI_G1G5_OVERNIGHT_IDIO_IVOL_LOWTO_VARIANT_PREREG_ZH.md",
            who="VARIANT：低特质隔夜波动；20日再平衡+前40缓冲；快门只管新开仓",
            lag="日频 OHLC；T+1 开盘"),
}

def latest(pat):
    l = sorted(AF.glob(pat)) + sorted(HL.glob(pat)); return l[-1] if l else None

def debeta(r, b):
    ix = r.index.intersection(b.index); r, b = r[ix], b[ix]
    if len(r) < 60 or b.std() == 0: return r*0, 0.0, 0.0
    be = float(np.cov(r, b)[0, 1]/np.var(b)); res = r-be*b; return res, be, float(res.mean()*244)

def jacc(wa, wb):
    wa = wa[~wa.instrument.map(LC.etf)]; wb = wb[~wb.instrument.map(LC.etf)]
    A = wa.groupby("date").instrument.apply(set); B = wb.groupby("date").instrument.apply(set); js = []
    for d in A.index.intersection(B.index):
        u = A[d] | B[d]
        if u: js.append(len(A[d] & B[d])/len(u))
    return dict(mean=float(np.mean(js)) if js else 0.0, max=float(np.max(js)) if js else 0.0, n=len(js))

def topn_rows(W, N):  # keep row order (= α desc as written by builder)
    out = []
    for d, g in W.groupby("date", sort=True):
        e = g[g.instrument.map(LC.etf)]; s = g[~g.instrument.map(LC.etf)]
        if len(s): k = s.head(N).copy(); k["target_weight"] *= s.target_weight.sum()/k.target_weight.sum(); out += [e, k]
        else: out.append(e)
    return pd.concat(out)

X2_ONLY = False
def window_perf(cfg, out):
    e = pd.read_parquet(R/"data/v2/etf/etf_daily_adj.parquet", columns=["trade_date","close_hfq"], filters=[("ts_code","==",FE.BAL)])
    e.index = pd.to_datetime(e.trade_date, format="%Y%m%d"); bench = e.close_hfq.sort_index().pct_change(); res = {}
    for wn, (s, en) in FE.WIN.items():
        if X2_ONLY and wn != "x2": continue
        for uni in ("HILIQ", "FULLA"):
            W = pd.read_parquet(out/f"{cfg['ew'][uni][wn]}.parquet", columns=["date","instrument","target_weight"]); W = W[W.target_weight > 0]
            W["date"] = pd.to_datetime(W.date); ent = {}
            for tier, N in (("full20", 20), ("60w", 6), ("100w", 10)):
                Wt = W if N == 20 else topn_rows(W, N); r, to = FE.book_ret(Wt, s, en)
                m = FE.met(r, bench); m["turnover_1s_daily"] = to; m["mean_names"] = float(Wt[~Wt.instrument.map(LC.etf)].groupby("date").size().mean())
                yb = {}
                for y, g in r.groupby(r.index.year):
                    bb = bench.reindex(g.index).fillna(0); yb[str(y)] = dict(ret=float((1+g).prod()-1), resid_alpha244=float((g-m["beta"]*bb).mean()*244))
                m["by_year"] = yb; ent[tier] = m
            res[f"{uni}_{wn}"] = ent; print("perf", uni, wn, {t: (round(v["cagr244"], 4), round(v["mdd"], 3)) for t, v in ent.items()}, f"rss={rss():.0f}", flush=True)
        FE._RET.clear(); gc.collect()
    return res

def selfcheck(wpath, extra_cmp):
    w = LC._w(wpath); r = LC._ret(w); b = ADG.bench().pct_change().reindex(r.index).fillna(0)
    resid, beta, a = debeta(r, b)
    cmp = {"capacity_adv": LC.CAP_ADV, "capacity_adv_hiliq": HL/"g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"}
    for k in ("earnings_event", "equity_incentive", "insider_increase", "insurer_surv", "report_rc_allup"):
        p = latest(f"g1g5_{k}_hiliq_v1_daily_weights_2*.parquet")
        if p: cmp[k+"_hiliq"] = p
    p = latest("g1g5_earnings_event_daily_weights_2*.parquet")
    if p: cmp["earnings_event"] = p
    cmp.update(extra_cmp); rho, jac, capstats = {}, {}, {}
    for nm, p in cmp.items():
        if p is None or not Path(p).exists(): continue
        wo = LC._w(p); ro = LC._ret(wo).reindex(r.index).dropna(); ro_res, bo, ao = debeta(ro, b.reindex(ro.index))
        ix = resid.index.intersection(ro_res.index)
        if len(ix) > 60 and resid[ix].std() > 0 and ro_res[ix].std() > 0: rho[nm] = float(np.corrcoef(resid[ix], ro_res[ix])[0, 1])
        jac[nm] = jacc(w, wo)
        if nm.startswith("capacity_adv"):
            nav = (1+ro).cumprod(); capstats[nm] = dict(cagr244=float(nav.iloc[-1]**(244/len(ro))-1), mdd=float((nav/nav.cummax()-1).min()), resid_alpha244=ao, span=[str(ro.index[0].date()), str(ro.index[-1].date())])
    by = {str(y): dict(alpha_ann=float(g.mean()*244), beta=beta) for y, g in resid.groupby(resid.index.year)}
    nav = (1+r).cumprod()
    return dict(alpha_ann_leaf=a, beta_leaf=beta, leaf_cagr_net244=float(nav.iloc[-1]**(244/len(r))-1), leaf_cagr_net252=float(nav.iloc[-1]**(252/len(r))-1),
                mdd_leaf=float((nav/nav.cummax()-1).min()), rho_excess_debeta=rho.get("capacity_adv"), rho_excess_debeta_hiliq_cap=rho.get("capacity_adv_hiliq"),
                rho_resid_vs=rho, jaccard_vs=jac, cap_stats=capstats, by_year=by, n_days=len(r), span=[str(r.index[0].date()), str(r.index[-1].date())],
                gateA_prereg=bool(a > 0 and max(abs(rho.get("capacity_adv", 0)), abs(rho.get("capacity_adv_hiliq", 0))) < 0.5),
                jaccard_hard_reject=bool(any(v["max"] >= 0.7 for v in jac.values())), filter_only=bool(any(v > 0.5 for v in rho.values())),
                annualization_primary=244, annualization_compare=252, engine="LC._ret T+1 open net 17.5bp adj")

def hiliq_cap_gateB(wpath):
    """Disclosure: cap80(HI_LIQ capacity_adv leg)+leaf20(top-N α order) vs HI_LIQ cap leg, X2, LC engine."""
    cap = LC._w(HL/"g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"); cap = cap[cap.date >= "2024-06-03"]
    L = LC._w(wpath); rc = LC._ret(cap); out = {}
    for tier, N in V3.NT.items():
        Lt = topn_rows(L.assign(date=L.date), N); lt = {d: g.set_index("instrument").target_weight for d, g in Lt.groupby("date")}
        rm = LC._ret(V3.stack(cap, lt)); ix = rc.index.intersection(rm.index)
        m0, m1 = V3.metrics(rc[ix]), V3.metrics(rm[ix]); out[tier] = dict(cap=m0, cap80_leaf20=m1, beats=bool(m1["cagr"] > m0["cagr"]))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--leaf", required=True, choices=list(CFG)); ap.add_argument("--skip-perf", action="store_true"); ap.add_argument("--x2-only", action="store_true"); a = ap.parse_args()
    global X2_ONLY; X2_ONLY = a.x2_only
    cfg = CFG[a.leaf]; out = AF/cfg["dir"]; stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    et = (datetime.now()-timedelta(hours=0)).strftime("%Y-%m-%d %H:%M:%S")
    S = dict(x2_only=a.x2_only, leaf=a.leaf, name=cfg["name"], prereg=cfg["prereg"], et=et, live=False, promotion_approved=False, research_candidate_self_sealed=False)
    S["window_perf"] = None if a.skip_perf else window_perf(cfg, out)
    extra = {}
    if a.leaf == "20": extra["leaf19_cfacc_rnoa"] = latest("g1g5_cfacc_rnoa_daily_weights_2*.parquet")
    if a.leaf == "21":
        extra["leaf19_cfacc_rnoa"] = latest("g1g5_cfacc_rnoa_daily_weights_2*.parquet"); extra["leaf20_sue_resid"] = latest("g1g5_sue_resid_daily_weights_2*.parquet")
    if a.leaf == "22":
        extra["leaf19_cfacc_rnoa"] = latest("g1g5_cfacc_rnoa_daily_weights_2*.parquet"); extra["leaf20_sue_resid"] = latest("g1g5_sue_resid_daily_weights_2*.parquet"); extra["leaf21_biz_climate"] = latest("g1g5_biz_climate_daily_weights_2*.parquet")
    if a.leaf == "18v": extra["leaf18_overnight_idio_ivol"] = latest("g1g5_overnight_idio_ivol_hiliq_daily_weights_2*.parquet")
    for uni, tag in zip(("HILIQ", "FULLA"), cfg["tags"]):
        wp = V3.wfile(tag); mp = V3.mfile(tag); print(uni, "weights", wp.name, flush=True)
        sc = selfcheck(wp, extra); print(uni, "selfcheck done", f"rss={rss():.0f}", flush=True)
        meta = json.loads(mp.read_text()); meta.update(selfcheck=sc, who_pays_zh=cfg["who"], who_pays_prereg=cfg["prereg"])
        w = LC._w(wp); meta["mean_names"] = float(w[~w.instrument.map(LC.etf)].groupby("date").size().mean())
        meta["mean_ballast"] = float(w[w.instrument.map(LC.etf)].groupby("date").target_weight.sum().mean()); mp.write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=str))
        V3.LAG[tag] = cfg["lag"]
        v3 = V3.run(tag, "HI_LIQ_V1.1" if uni == "HILIQ" else "FULLA_V1"); print(uni, "v3 done", f"rss={rss():.0f}", flush=True)
        d11 = ADG11.evaluate_weights(wp); lcg = LC.evaluate(wp, gates=True); print(uni, "decay/LC gates done", f"rss={rss():.0f}", flush=True)
        g3 = dict(v3["gate_v3"]); g3["decay_keep"] = d11["outcome"] == "KEEP"; g3["decay_version"] = "v1.1"
        g3["pass"] = bool(all(g3["mdd_le_25"].values()) and all(g3["cagr_gt_cap"].values()) and g3["decay_keep"] and g3["tradable"])
        gb_pre = all(v3["marginal"][f"{t}_capacity_adv"]["with_leaf"]["cagr"] > v3["marginal"][f"{t}_capacity_adv"]["base"]["cagr"] for t in V3.NT)
        hb = hiliq_cap_gateB(wp) if uni == "HILIQ" else None
        S[uni+"_x2"] = dict(weights=str(wp.relative_to(R)), selfcheck=sc, decay_v1=v3["decay"], decay_v1_1={k: d11.get(k) for k in ("outcome", "reasons", "latest_resid_alpha", "gate_version") if k in d11},
                            decay_v1_1_full=d11, cost=v3["cost"], lc_portfolio_gates=lcg.get("portfolio_gates"), gate_v3_v11=g3,
                            gateA_prereg=sc["gateA_prereg"], gateB_prereg_oldcap=bool(gb_pre), gateB_hiliq_cap_disclosure=hb,
                            marginal=v3["marginal"], factor_ic=v3["factor"]["ic"], factor_pool=v3["factor"]["pool_universe"], holding_autocorr=v3["factor"]["holding_autocorr_jaccard"])
        del w; gc.collect()
    S["peak_rss_mb"] = rss(); p = out/f"eval_resume_{stamp}.json"; p.write_text(json.dumps(S, ensure_ascii=False, indent=1, default=float)); print("WROTE", p, "rss", rss(), flush=True)
if __name__ == "__main__": main()
