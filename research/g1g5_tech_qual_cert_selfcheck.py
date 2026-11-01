#!/usr/bin/env python3
"""Leaf18 selfcheck: enrich run_meta.selfcheck then leaf_selfcheck_v3 + dual-universe summary.
Arch TODO noted in receipt if leaf_selfcheck_v3 not patched (delist terminal; FULLA/HI_LIQ residual pool).
live=false; no Book-Smoke.
"""
from __future__ import annotations
import json, sys, resource, hashlib
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import research.leaf_selfcheck_common as LC
import research.leaf_selfcheck_v3 as V3
import research.alpha_decay_gate as ADG
from quantlab.metrics import cagr_from_returns as cg

AF = ROOT / "output/ai_factory"
OUT = AF / "leaf18_tech_qual_cert"
WHO = "docs/v2/AI_G1G5_TECH_QUAL_CERT_WHO_PAYS_PREREG_ZH.md"
WHO_ZH = (
    "成长行业资质/认证认定后，对资质→订单与估值溢价反应慢的资金付钱；"
    "base-α=60日事件强度分域标定+行业市值残差；快门1–3日量价不入α。"
)
COMPARE = {
    "capacity_adv": AF / "g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
    "earnings_event": sorted(AF.glob("g1g5_earnings_event_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_earnings_event_daily_weights_2*.parquet")) else None,
    "report_rc_allup": sorted(AF.glob("g1g5_report_rc_allup_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_report_rc_allup_daily_weights_2*.parquet")) else None,
    "analyst_recoverage": sorted(AF.glob("g1g5_analyst_recoverage_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_analyst_recoverage_daily_weights_2*.parquet")) else None,
    "insider_increase": sorted(AF.glob("g1g5_insider_increase_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_insider_increase_daily_weights_2*.parquet")) else None,
    "equity_incentive": sorted(AF.glob("g1g5_equity_incentive_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_equity_incentive_daily_weights_2*.parquet")) else None,
    "tp_rerate": sorted(AF.glob("g1g5_tp_rerate_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_tp_rerate_daily_weights_2*.parquet")) else None,
    "broker_gold_new": sorted(AF.glob("g1g5_broker_gold_new_alla_daily_weights_2*.parquet") or AF.glob("g1g5_broker_gold_new_daily_weights_2*.parquet"))[-1] if list(AF.glob("g1g5_broker_gold_new*_daily_weights_2*.parquet")) else None,
    "major_contract_growth": (sorted(AF.glob("g1g5_major_contract_growth_*_daily_weights_2*.parquet")) or [None])[-1],
}


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def debeta(r, b):
    ix = r.index.intersection(b.index)
    r, b = r[ix], b[ix]
    if len(r) < 60 or b.std() == 0:
        return r * 0, 0.0, 0.0
    beta = float(np.cov(r, b)[0, 1] / np.var(b))
    resid = r - beta * b
    return resid, beta, float(resid.mean() * 244)


def jaccard_daily(wa: pd.DataFrame, wb: pd.DataFrame) -> dict:
    wa = wa[~wa.instrument.map(LC.etf)].copy()
    wb = wb[~wb.instrument.map(LC.etf)].copy()
    ja = []
    for d in sorted(set(wa.date) & set(wb.date)):
        a = set(wa.loc[wa.date == d, "instrument"])
        b = set(wb.loc[wb.date == d, "instrument"])
        if not a and not b:
            continue
        ja.append(len(a & b) / len(a | b))
    if not ja:
        return dict(mean=0.0, max=0.0, n=0)
    return dict(mean=float(np.mean(ja)), max=float(np.max(ja)), n=int(len(ja)))


def build_selfcheck(weights: Path) -> dict:
    w = LC._w(weights)
    r = LC._ret(w)
    b = ADG.bench().pct_change().reindex(r.index).fillna(0)
    resid, beta, alpha_ann = debeta(r, b)
    # capacity
    wc = LC._w(COMPARE["capacity_adv"])
    rc = LC._ret(wc).reindex(r.index).fillna(0)
    resid_c, beta_c, alpha_c = debeta(rc, b)
    by = {}
    for y, g in resid.groupby(resid.index.year):
        by[str(y)] = dict(alpha_ann=float(g.mean() * 244), beta=beta, leaf_cagr=float(cg(r[r.index.year == y])) if (r.index.year == y).any() else None,
                          bench_cagr=float(cg(b[b.index.year == y])) if (b.index.year == y).any() else None)
    rho_vs = {}
    jac = {}
    for name, path in COMPARE.items():
        if path is None or not Path(path).exists():
            continue
        wo = LC._w(path)
        ro = LC._ret(wo).reindex(r.index).fillna(0)
        res_o, _, _ = debeta(ro, b)
        ix = resid.index.intersection(res_o.index)
        if len(ix) > 60 and resid[ix].std() > 0 and res_o[ix].std() > 0:
            rho_vs[name] = float(np.corrcoef(resid[ix], res_o[ix])[0, 1])
        jac[name] = jaccard_daily(w, wo)
    return dict(
        alpha_ann_leaf=alpha_ann,
        alpha_ann_cap=alpha_c,
        beta_leaf=beta,
        beta_cap=beta_c,
        leaf_cagr_gross=float(cg(r)),
        cap_cagr_gross=float(cg(rc)),
        bench_cagr=float(cg(b)),
        mdd_leaf=float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min()),
        mdd_cap=float(((1 + rc).cumprod() / (1 + rc).cumprod().cummax() - 1).min()),
        mdd_bench=float(((1 + b).cumprod() / (1 + b).cumprod().cummax() - 1).min()),
        leaf_vs_bench_excess_ann=float((r - b).mean() * 244),
        rho_excess_debeta=rho_vs.get("capacity_adv"),
        rho_raw_excess=float(np.corrcoef(r - b, rc - b)[0, 1]) if (r - b).std() > 0 else None,
        rho_resid_vs=rho_vs,
        jaccard_vs=jac,
        by_year=by,
        n_days=int(len(r)),
        span=[str(r.index.min().date()), str(r.index.max().date())],
        gate_resid_pos=bool(alpha_ann > 0),
        gate_rho_lt_0_5=bool((rho_vs.get("capacity_adv") or 0) < 0.5),
        gate_pass=bool(alpha_ann > 0 and (rho_vs.get("capacity_adv") or 0) < 0.5),
        note_zh="自检估计；年化244；T+1净收益见 leaf_selfcheck；Arch TODO: 退市终值、验收宇宙切 FULLA/HI_LIQ",
        annualization_primary=244,
        annualization_compare=252,
    )


def enrich_and_run(leaf_tag: str, weights: Path, meta_path: Path):
    meta = json.loads(meta_path.read_text())
    sc = build_selfcheck(weights)
    meta["selfcheck"] = sc
    meta["who_pays_zh"] = WHO_ZH
    meta["who_pays_prereg"] = WHO
    meta["mean_names"] = float(
        LC._w(weights).loc[lambda x: ~x.instrument.map(LC.etf)].groupby("date").size().mean()
    ) if len(LC._w(weights)) else 0.0
    w = LC._w(weights)
    ball = w.loc[w.instrument.map(LC.etf)].groupby("date")["target_weight"].sum()
    meta["mean_ballast"] = float(ball.mean()) if len(ball) else 1.0
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str))
    # canonical for v3
    # leaf_selfcheck_v3 mfile/wfile require g1g5_{leaf}_*_2*.json/parquet (year stamp)
    import re
    m = re.search(r"(20\d{6}_\d{6})", weights.name)
    stamp = m.group(1) if m else datetime.now().strftime("%Y%m%d_%H%M%S")
    canon_w = AF / f"g1g5_{leaf_tag}_daily_weights_{stamp}.parquet"
    canon_m = AF / f"g1g5_{leaf_tag}_run_meta_{stamp}.json"
    canon_w.write_bytes(weights.read_bytes())
    canon_m.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str))
    # also refresh meta_path
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str))
    # patch LAG note via env — v3 uses LAG.get
    V3.LAG[leaf_tag] = "公告 available_at → 下一交易日 sess；T2 入场；快门用当日成交额（PIT）"
    res = V3.run(leaf_tag)
    return meta, res


def main():
    # Primary research = FULLA x2
    w_fulla = sorted(OUT.glob("eval_weights_FULLA_x2_*.parquet"))[-1]
    m_fulla = sorted(OUT.glob("run_meta_FULLA_x2_*.json"))[-1]
    # Also HILIQ x2
    w_hiliq = sorted(OUT.glob("eval_weights_HILIQ_x2_*.parquet"))[-1]
    m_hiliq = sorted(OUT.glob("run_meta_HILIQ_x2_*.json"))[-1]

    print("FULLA selfcheck...", flush=True)
    meta_f, res_f = enrich_and_run("tech_qual_cert", w_fulla, m_fulla)
    print("HILIQ selfcheck...", flush=True)
    meta_h, res_h = enrich_and_run("tech_qual_cert_hiliq", w_hiliq, m_hiliq)

    summary = {
        "et": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "FULLA_x2": {"selfcheck": meta_f["selfcheck"], "gate_v3": res_f["gate_v3"], "decay": res_f["decay"], "cost": res_f["cost"],
                     "marginal_60w_cap": res_f["marginal"].get("60w_capacity_adv"), "marginal_100w_cap": res_f["marginal"].get("100w_capacity_adv")},
        "HILIQ_x2": {"selfcheck": meta_h["selfcheck"], "gate_v3": res_h["gate_v3"], "decay": res_h["decay"], "cost": res_h["cost"],
                     "marginal_60w_cap": res_h["marginal"].get("60w_capacity_adv"), "marginal_100w_cap": res_h["marginal"].get("100w_capacity_adv")},
        "peak_rss_mb": rss(),
        "arch_todo": [
            "leaf_selfcheck_v3: delist terminal returns (P1)",
            "leaf_selfcheck_v3: acceptance residual universe FULLA/HI_LIQ not static top300 (P2) — factor_report still uses mid_large top300",
        ],
    }
    sp = OUT / "selfcheck_summary_x2.json"
    sp.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float))
    print("wrote", sp, "rss", rss())


if __name__ == "__main__":
    main()
