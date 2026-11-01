#!/usr/bin/env python3
"""Arch MILP lot-polish feasibility PROBE v1 (docs/v2/ARCH_MILP_LOTPOLISH_PREREG_SPEC_ZH.md §9).
SYNTHETIC DATA ONLY. Loads no market data, no QuantLab module, no weights, computes no returns.
Purpose: confirm HiGHS availability/version and measure per-MILP wall time + peak RSS for a ~300-name
integer-lot tracking problem with all caliber-C hard constraints. Numbers here are NOT evidence about Core.
Run: .venv_opt/bin/python docs/v2/audit/arch_milp_probe_v1.py  (single process, threads=1)."""
import json, resource, sys, time, platform
import numpy as np
import highspy
import importlib.metadata as md

N, G = 300, 28
CAP = {600000: 0.06, 1000000: 0.05}
B = {"eq100": 1.0, "eq80": 0.8}
FLOOR, IND_REL, IND_ABS, STY, BETA, CASH = 0.02, 0.08, 0.20, 0.35, 0.10, 0.02
LADDER = [(0.0, 0.0), (0.05, 0.005), (0.05, 0.01)]  # (style slack σ, industry slack) = v1.4 ladder
MU, KAPPA = 0.1, 0.0015          # spec §2.3 turnover weight; synthetic one-way cost placeholder
TIME_LIMIT, REL_GAP_SOLVER = 60.0, 1e-4
TOL = 1e-6

def rss_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

def synth(seed, pmed=18.0):
    r = np.random.default_rng(seed)
    lnm = r.normal(10.0, 1.0, N); z = (lnm - lnm.mean()) / lnm.std()
    m = (lnm - lnm.mean()) ** 2; m = (m - m.mean()) / m.std()
    wb = np.exp(lnm); wb /= wb.sum()
    beta = 1.0 + 0.25 * r.standard_normal(N) + 0.05 * z
    ind = r.integers(0, G, N)
    price = np.exp(r.normal(np.log(pmed), 0.9, N)).clip(2, 400)
    lot = np.where(r.random(N) < 0.10, 200, 100)
    return dict(z=z, m=m, wb=wb, beta=beta, ind=ind, price=price, lot=lot, alpha=r.standard_normal(N), alpha_prev=r.standard_normal(N))

def lp_target(d, alpha, cand, cap, margin=0.8):
    """Synthetic continuous w* on the equity book (Σw=1): LP max alpha'w, slack-0 caliber constraints, w<=min(cap,4.5%)."""
    h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("threads", 1)
    n = len(cand); ub = np.full(n, min(cap, 0.045))
    h.addCols(n, -alpha[cand], np.zeros(n), ub, 0, np.array([], np.int32), np.array([], np.int32), np.array([]))
    rows = [(np.ones(n), 1.0, 1.0)]
    for g in range(G):
        a = (d["ind"][cand] == g).astype(float); wg = d["wb"][d["ind"] == g].sum()
        rows.append((a, max(wg - IND_REL, 0.0), min(wg + IND_REL, IND_ABS)))
    for f, bd in ((d["z"], STY), (d["m"], STY), (d["beta"], BETA)):
        fb = float(d["wb"] @ f); rows.append((f[cand], fb - bd * margin, fb + bd * margin))  # margin<1: target strictly inside bands
    for a, lo, hi in rows:
        idx = np.nonzero(a)[0].astype(np.int32); h.addRow(lo, hi, len(idx), idx, a[idx])
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal: return None
    w = np.array(h.getSolution().col_value); w[w < 1e-9] = 0; return w

def build_and_solve(d, cand, xstar, xprev, Bs, aum, sl):
    cap = CAP[aum]; n = len(cand)
    u = d["lot"][cand] * d["price"][cand] / aum
    mmax = np.floor(cap * Bs / u + 1e-6); fmin = np.ceil(FLOOR * Bs / u - 1e-6)
    ok = fmin <= mmax
    # columns: n(0..n-1) int, z(n..2n-1) bin, t(2n..3n-1), dd(3n..4n-1)
    nc = 4 * n
    cost = np.r_[np.zeros(2 * n), np.ones(n), MU * np.ones(n)]
    lo = np.zeros(nc); hi = np.r_[np.where(ok, mmax, 0), np.where(ok, 1, 0), np.full(2 * n, np.inf)]
    h = highspy.Highs()
    for k, v in (("output_flag", False), ("threads", 1), ("random_seed", 0), ("time_limit", TIME_LIMIT),
                 ("mip_rel_gap", REL_GAP_SOLVER), ("mip_abs_gap", 1e-7)):
        h.setOptionValue(k, v)
    E = np.array([], np.int32)
    h.addCols(nc, cost, lo, hi, 0, E, E, np.array([]))
    h.changeColsIntegrality(2 * n, np.arange(2 * n, dtype=np.int32), np.array([highspy.HighsVarType.kInteger] * (2 * n)))
    INF = highspy.kHighsInf
    def row(idx, val, l, r_): h.addRow(l, r_, len(idx), np.asarray(idx, np.int32), np.asarray(val, float))
    for i in range(n):
        row([2 * n + i, i], [1, -u[i]], -xstar[i], INF); row([2 * n + i, i], [1, u[i]], xstar[i], INF)
        row([3 * n + i, i], [1, -u[i]], -xprev[i], INF); row([3 * n + i, i], [1, u[i]], xprev[i], INF)
        row([i, n + i], [1, -mmax[i]], -INF, 0); row([i, n + i], [1, -fmin[i]], 0, INF)
    row(list(range(n, 2 * n)), [1] * n, 20, 30)
    row(list(range(n)) + list(range(3 * n, 4 * n)), list(u) + [KAPPA] * n, Bs - CASH, Bs)  # cash in [0,2%] after cost
    s_sty, s_ind = sl
    for g in range(G):
        sel = np.nonzero(d["ind"][cand] == g)[0]; wg = d["wb"][d["ind"] == g].sum()   # wb on FULL pool (L2)
        l_, r_ = Bs * max(wg - IND_REL - s_ind, 0.0), Bs * min(wg + IND_REL + s_ind, IND_ABS)
        if len(sel): row(sel, u[sel], l_, r_)
        elif l_ > TOL: return dict(status="INFEASIBLE_TRIVIAL")
    for f, bd in ((d["z"], STY + s_sty), (d["m"], STY + s_sty), (d["beta"], BETA)):
        fb = float(d["wb"] @ f); row(list(range(n)), u * f[cand], Bs * (fb - bd), Bs * (fb + bd))
    t0 = time.perf_counter(); rs = h.run(); dt = time.perf_counter() - t0
    if rs == highspy.HighsStatus.kError: raise SystemExit("probe: HiGHS run returned kError")
    st = h.getModelStatus(); info = h.getInfo()
    res = dict(status=h.modelStatusToString(st), wall_s=dt, n_cols=nc, n_rows=h.getNumRow(),
               gap=float(info.mip_gap) if info.primal_solution_status == 2 else None, nodes=int(info.mip_node_count))
    if info.primal_solution_status != 2: return res
    x = np.array(h.getSolution().col_value)
    q = np.round(x[:n]); zz = np.round(x[n:2 * n])
    xl = u * q
    # independent re-check from integer lots (tol 1e-6), not trusting solver row activities
    viol = []
    turn = np.abs(xl - xprev).sum(); cash = Bs - xl.sum() - KAPPA * turn
    if not (-TOL <= cash <= CASH + TOL): viol.append("cash")
    nn = int((q > 0).sum())
    if not (20 <= nn <= 30): viol.append("names")
    if np.any(xl > cap * Bs + TOL): viol.append("cap")
    if np.any((q > 0) & (xl < FLOOR * Bs - TOL)): viol.append("floor")
    for g in range(G):
        wg = d["wb"][d["ind"] == g].sum(); Gg = xl[d["ind"][cand] == g].sum() / Bs
        if Gg - wg > IND_REL + s_ind + TOL or wg - Gg > IND_REL + s_ind + TOL: viol.append("ind_rel")
        if Gg > IND_ABS + TOL: viol.append("ind_abs")
    for nm, f, bd in (("size", d["z"], STY + s_sty), ("midcap", d["m"], STY + s_sty), ("beta", d["beta"], BETA)):
        if abs(float(xl @ f[cand]) / Bs - float(d["wb"] @ f)) > bd + TOL: viol.append(nm)
    res.update(n_names=nn, track_l1=float(np.abs(xl - xstar).sum()), turn_l1=float(turn), cash=float(cash),
               check_pass=not viol, viol=sorted(set(viol)), obj=float(h.getInfo().objective_function_value))
    return res

def main():
    t_all = time.perf_counter(); out = []
    meta = dict(highspy=md.version("highspy"), highs_core=h_ver(), python=sys.version.split()[0], platform=platform.platform(),
                numpy=np.__version__, scipy=md.version("scipy"), threads=1, time_limit_s=TIME_LIMIT, N=N, G=G, synthetic=True)
    MODE = sys.argv[1] if len(sys.argv) > 1 else "base"
    # base: median price 18, target inside 80% of style/β bands. stress: median price 60 (coarser lots) and target ON the
    # band edges (margin=1.0), so caliber-C on B=0.8 and lot granularity actually bind. Both synthetic.
    # tight: stress data, but MILP bands shrunk to β ±0.01 / style ±0.05σ (target built with the normal bands) to time
    # hard / near-infeasible branch-and-bound and infeasibility proofs. Not a model variant; timing only.
    pmed, margin = {"base": (18.0, 0.8), "stress": (60.0, 1.0), "tight": (60.0, 1.0)}[MODE]
    global BETA, STY
    if MODE == "tight":
        STY_T, BETA_T = 0.05, 0.01
    else:
        STY_T, BETA_T = STY, BETA
    meta.update(mode=MODE, price_median=pmed, target_margin=margin)
    for seed in range(10):
        d = synth(seed, pmed)
        for aum in (600000, 1000000):
            cand = np.nonzero(d["lot"] * d["price"] <= CAP[aum] * 0.8 * aum)[0]   # v1.4 S5 shared (② threshold)
            BETA, STY = 0.10, 0.35  # targets always built on the real bands
            w = lp_target(d, d["alpha"], cand, CAP[aum], margin); wp = lp_target(d, d["alpha_prev"], cand, CAP[aum], margin)
            if w is None or wp is None: out.append(dict(seed=seed, aum=aum, status="TARGET_LP_INFEASIBLE")); continue
            BETA, STY = BETA_T, STY_T
            for sv, Bs in B.items():
                for li, sl in enumerate(LADDER):
                    r = build_and_solve(d, cand, Bs * w, (Bs - 0.01) * wp, Bs, aum, sl)
                    r.update(seed=seed, aum=aum, sleeve=sv, slack_level=li, n_cand=int(len(cand)), n_target=int((w > 0).sum()),
                             rss_mb=round(rss_mb(), 1))
                    out.append(r); print(json.dumps(r), flush=True)
                    if r.get("check_pass"): break
    ok = [r for r in out if "wall_s" in r]
    ws = np.array([r["wall_s"] for r in ok])
    summ = dict(meta=meta, n_milp=len(ok), wall_s=dict(median=float(np.median(ws)), p90=float(np.quantile(ws, .9)), max=float(ws.max()), total=float(ws.sum())),
                n_feasible_checked=sum(1 for r in ok if r.get("check_pass")), n_check_fail=sum(1 for r in ok if r.get("check_pass") is False),
                statuses={s: sum(1 for r in ok if r["status"] == s) for s in {r["status"] for r in ok}},
                peak_rss_mb=round(rss_mb(), 1), elapsed_s=time.perf_counter() - t_all)
    print("SUMMARY", json.dumps(summ, indent=1))
    json.dump(dict(summary=summ, rows=out), open(__file__.replace(".py", f"_result_{MODE}.json"), "w"), indent=1, default=str)

def h_ver():
    h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("threads", 1); return h.version()

if __name__ == "__main__":
    main()
