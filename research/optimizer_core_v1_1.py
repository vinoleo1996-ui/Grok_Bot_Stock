"""OPTIMIZER Core FROZEN_v1.1 solver (docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_v1_1_ZH.md).
Implementation fix only: Σw=1; hard 20–30 names via deterministic iterative top-k (2% floor, name cap);
step2 failure -> INFEASIBLE (caller carries prior holdings, never step-1 basket);
lot rounding + greedy lot-adding so residual cash ≤2%. λ unchanged. live=false."""
from __future__ import annotations
import numpy as np, pandas as pd
import optimizer_lambda_calib_sealed as C

W_FLOOR = 0.02      # parent PREREG §3.5(b) single-name floor
CASH_MAX = 0.02
POOL_STD = False    # v1.2: True -> Size/MidCap standardized over full HI_LIQ pool, benchmark exposure from full-pool wb
IND_POOL = False    # v1.3 (主 Agent 2026-10-18 ruling): True -> industry benchmark = full-pool wb (normalized), frozen spec
                    # ±8% relative (+slack) and ≤20% absolute; also constrains industries with no support name. v0–v1.2 used
                    # support-name wb (defect, disclosed in AMEND_v1_3); False keeps v0–v1.2 reproducible.

def pool_ind_bench(D):
    """Full-pool in-pool benchmark industry weights (wb normalized to 1 over the solver pool)."""
    pool = D["alpha"].index; wb = D["wb"].reindex(pool).fillna(0.0); wb = wb / max(float(wb.sum()), 1e-12)
    ind = D["industry"]
    return wb.groupby(wb.index.map(lambda n: ind.get(n, "_UNK"))).sum()

def _solve_support(D, w0, names, aum, lr, lt, size_slack=0.0, ind_slack=0.0, equality=True, floor=True):
    import cvxpy as cp
    alpha, wb = D["alpha"], D["wb"]; ind = D["industry"]; lnm = D["ln_mcap"]
    n = len(names)
    a = alpha.reindex(names).fillna(0.0).values
    wb_v = wb.reindex(names).fillna(0.0).values
    w0_v = w0.reindex(names).fillna(0.0).values
    full_ix = {nm: i for i, nm in enumerate(alpha.index)}
    inds = sorted(set(ind.get(nm, "_UNK") for nm in names)); k = len(inds); jx = {g: j for j, g in enumerate(inds)}
    B = np.zeros((n, k))
    for i, nm in enumerate(names): B[i, jx[ind.get(nm, "_UNK")]] = 1.0
    F = np.eye(k) * float(np.mean(np.diag(D["F"]))) if D["F"].size else np.eye(k) * 1e-4
    dl = np.array([D["delta"][full_ix[nm]] if nm in full_ix else 1e-4 for nm in names])
    beta = D["betas"].reindex(names).fillna(1.0).values
    if POOL_STD:
        pool = alpha.index; x = lnm.reindex(pool).astype(float)
        zp = (x - x.mean()) / (x.std(ddof=0) + 1e-12)
        mp = (x - x.mean()) ** 2; mp = (mp - mp.mean()) / (mp.std(ddof=0) + 1e-12)
        wbp = wb.reindex(pool).fillna(0.0)
        zb = float((wbp * zp.fillna(0)).sum()); midb = float((wbp * mp.fillna(0)).sum())
        z = zp.reindex(names).fillna(0).values; mid = mp.reindex(names).fillna(0).values
        bp = D["betas"].reindex(pool).fillna(1.0); beta_b = float((wbp * bp).sum() / max(wbp.sum(), 1e-12))
    else:
        z = lnm.reindex(names).astype(float); z = ((z - z.mean()) / (z.std(ddof=0) + 1e-12)).fillna(0).values
        mid = (lnm.reindex(names).astype(float) - lnm.reindex(names).mean()) ** 2
        mid = ((mid - mid.mean()) / (mid.std(ddof=0) + 1e-12)).fillna(0).values
        zb, midb = float(wb_v @ z), float(wb_v @ mid); beta_b = 1.0
    # v0–v1.2: industry benchmark = support-name wb (defect). v1.3 IND_POOL: full-pool wb.
    if IND_POOL:
        gb = pool_ind_bench(D); wb_ind = np.array([float(gb.get(g, 0.0)) for g in inds])
        # industries with no support name: pi=0, so |0 - wb_g| <= box must hold (else infeasible at this support)
        if any(float(v) > C.IND_ACTIVE + ind_slack + 1e-12 for g, v in gb.items() if g not in jx):
            return None, "infeasible_pool_industry_uncovered"
    else:
        wb_ind = B.T @ wb_v
    w = cp.Variable(n, nonneg=True); act = w - wb_v
    risk = cp.quad_form(B.T @ act, F) + cp.sum(cp.multiply(dl, cp.square(act)))
    obj = -(a @ w) + lr * risk + lt * cp.norm1(w - w0_v)
    cap = C.NAME_CAP[aum]
    cons = [(cp.sum(w) == 1.0) if equality else (cp.sum(w) <= 1.0), w <= cap, cp.sum_squares(w) <= 1.0 / C.NEFF_LO]
    if floor: cons.append(w >= W_FLOOR)
    pi = B.T @ w; box = C.IND_ACTIVE + ind_slack
    for j in range(k): cons += [pi[j] - wb_ind[j] <= box, wb_ind[j] - pi[j] <= box, pi[j] <= C.IND_ABS]
    sb = C.SIZE_BOX + size_slack
    cons += [w @ z - zb <= sb, zb - w @ z <= sb, w @ mid - midb <= sb, midb - w @ mid <= sb,
             w @ beta - beta_b <= C.BETA_BOX, beta_b - w @ beta <= C.BETA_BOX]
    p = cp.Problem(cp.Minimize(obj), cons)
    st = "ERR"
    for s in (cp.CLARABEL, cp.OSQP):
        try:
            p.solve(solver=s, verbose=False); st = str(p.status)
            if st in ("optimal", "optimal_inaccurate") and w.value is not None: break
        except Exception as e: st = f"ERR:{type(e).__name__}"
    if w.value is None or st not in ("optimal", "optimal_inaccurate"): return None, st
    wv = np.clip(np.array(w.value, float), 0, None)
    return pd.Series(wv / wv.sum() if equality else wv, index=names), st

def _solve_with_slack(D, w0, names, aum, lr, lt, **kw):
    ss, isl = 0.0, 0.0
    while True:
        w, st = _solve_support(D, w0, names, aum, lr, lt, size_slack=ss, ind_slack=isl, **kw)
        if w is not None: return w, st, {"size_slack": ss, "ind_slack": isl}
        if ss >= C.SIZE_SLACK_MAX - 1e-12 and isl >= C.IND_SLACK_MAX - 1e-12: return None, st, {"size_slack": ss, "ind_slack": isl}
        ss = min(C.SIZE_SLACK_MAX, ss + 0.05); isl = min(C.IND_SLACK_MAX, isl + 0.005)

def solve_v11(D, w0, aum, lr, lt, exclude=()):
    """Return (w or None, info). w sums to 1, 20–30 names, each in [2%, cap].
    v1.3: `exclude` = names removed from the candidate set (price-infeasible lots); benchmark/pool exposures unchanged."""
    ex = set(exclude); names_all = [n for n in D["alpha"].index if n not in ex]
    w1, st1, sl1 = _solve_with_slack(D, w0, names_all, aum, lr, lt, equality=True, floor=False)
    if w1 is None: return None, {"status": "INFEASIBLE", "stage": "step1", "cvx": st1}
    order = sorted(names_all, key=lambda n: (-abs(w1[n]), n))
    k0 = int(np.clip((w1 >= W_FLOOR).sum(), C.NEFF_LO, C.NEFF_HI))
    ks = list(range(k0, C.NEFF_HI + 1)) + list(range(k0 - 1, C.NEFF_LO - 1, -1))
    for t, K in enumerate(ks):
        w, st, sl = _solve_with_slack(D, w0, order[:K], aum, lr, lt, equality=True, floor=True)
        if w is not None:
            return w, {"status": "OK", "K": K, "k0": k0, "tries": t + 1, "slack": sl, "step1_slack": sl1, "cvx": st}
    return None, {"status": "INFEASIBLE", "stage": "step2", "k0": k0, "tries": len(ks)}

def style_ctx(D, size_slack, ind_slack):
    """v1.3: full-pool exposure vectors (same definitions as v1.2 solver + C1 recheck)."""
    pool = D["alpha"].index; x = D["ln_mcap"].astype(float).reindex(pool)
    z = ((x - x.mean()) / (x.std(ddof=0) + 1e-12)).fillna(0)
    m = (x - x.mean()) ** 2; m = ((m - m.mean()) / (m.std(ddof=0) + 1e-12)).fillna(0)
    b = D["betas"].reindex(pool).fillna(1.0); wb = D["wb"].reindex(pool).fillna(0.0); wb = wb / max(wb.sum(), 1e-12)
    return {"z": z.to_dict(), "m": m.to_dict(), "b": b.to_dict(), "zb": float((wb * z).sum()), "mb": float((wb * m).sum()),
            "bb": float((wb * b).sum()), "sbox": C.SIZE_BOX + float(size_slack or 0), "ind_box": C.IND_ACTIVE + float(ind_slack or 0)}

def _style_excess(c, sty, bal):
    e_z = sum(v * sty["z"].get(i, 0) for i, v in c.items()) + bal * sty["zb"] - sty["zb"]
    e_m = sum(v * sty["m"].get(i, 0) for i, v in c.items()) + bal * sty["mb"] - sty["mb"]
    e_b = sum(v * sty["b"].get(i, 1.0) for i, v in c.items()) + bal * sty["bb"] - sty["bb"]
    return max(0, abs(e_z) - sty["sbox"]) + max(0, abs(e_m) - sty["sbox"]) + max(0, abs(e_b) - C.BETA_BOX)

def lot_round_greedy(w, px, aum, industry, wb, cap, ballast_frac=0.0, style=None, wb_raw=False):
    """Floor to lots, then greedily add one lot to the largest shortfall name within cap /
    industry abs ≤20% / industry ±8% vs wb / cash ≥0, until cash ≤ CASH_MAX or nothing fits.
    Equity budget = 1-ballast_frac. Returns (w_lot Series, info)."""
    budget = 1.0 - ballast_frac
    tgt = w.astype(float); q = {}; P = {}; nopx = []
    for i, wt in tgt.items():
        p_ = px.get(i, np.nan)
        if not np.isfinite(p_) or p_ <= 0: nopx.append(i); continue
        P[i] = float(p_); L = C.lot_round_rule(i)
        q[i] = np.floor(wt * aum / (P[i] * L)) * L
    cur = lambda: pd.Series({i: q[i] * P[i] / aum for i in q}, dtype=float)
    # wb_raw=True: support-name wb, not renormalized (v1.3 pre-ruling; REJECTED by 主 Agent 2026-10-18).
    # v1.3 now passes full-pool D["wb"] with wb_raw=False -> full-pool benchmark scaled to the equity budget.
    wbi = wb.groupby(wb.index.map(lambda n: industry.get(n, "_UNK"))).sum() * (budget if wb_raw else budget / max(wb.sum(), 1e-12))
    if style is not None:  # v1.3 ② style repair: single-lot adds or (remove one lot j, add one lot i) swaps that strictly cut excess (vectorized)
        nm = sorted(q); n = len(nm)
        lotv = np.array([C.lot_round_rule(i) for i in nm], float); Pv = np.array([P[i] for i in nm]); dw = lotv * Pv / aum
        Z = np.array([style["z"].get(i, 0) for i in nm]); M = np.array([style["m"].get(i, 0) for i in nm]); Bt = np.array([style["b"].get(i, 1.0) for i in nm])
        gl = sorted({industry.get(i, "_UNK") for i in nm}); gix = np.array([gl.index(industry.get(i, "_UNK")) for i in nm])
        wbg = np.array([wbi.get(g, 0.0) for g in gl]); glim = np.minimum(C.IND_ABS * budget, wbg + style["ind_box"] * budget) + 1e-9
        same = (gix[:, None] == gix[None, :])
        bal = ballast_frac
        def exc(ez, em, eb):
            return (np.maximum(0, np.abs(ez + bal * style["zb"] - style["zb"]) - style["sbox"]) + np.maximum(0, np.abs(em + bal * style["mb"] - style["mb"]) - style["sbox"])
                    + np.maximum(0, np.abs(eb + bal * style["bb"] - style["bb"]) - C.BETA_BOX))
        for _ in range(300):
            qv = np.array([q[i] for i in nm], float); w_ = qv * Pv / aum
            ez, em, eb = w_ @ Z, w_ @ M, w_ @ Bt; v_now = exc(ez, em, eb)
            if v_now <= 1e-9: break
            cash = budget - w_.sum(); G = np.bincount(gix, weights=w_, minlength=len(gl)); cnt = (qv > 0).sum()
            # rows j = removed (row n = none), cols i = added (col n = none, i.e. pure one-lot sale)
            dz = np.append(dw * Z, 0); dm = np.append(dw * M, 0); db = np.append(dw * Bt, 0); dwa = np.append(dw, 0)
            rz = np.append(dw * Z, 0); rm = np.append(dw * M, 0); rb = np.append(dw * Bt, 0); rdw = np.append(dw, 0)
            EZ = ez + dz[None, :] - rz[:, None]; EM = em + dm[None, :] - rm[:, None]; EB = eb + db[None, :] - rb[:, None]
            V2 = exc(EZ, EM, EB)
            okc = (cash - dwa[None, :] + rdw[:, None]) >= -1e-12
            okcap = np.broadcast_to(np.append(w_ + dw <= cap * budget + 1e-9, True)[None, :], V2.shape)
            gx = np.append(gix, -1)
            Gi = np.append(G[gix] + dw, -np.inf); lim = np.append(glim[gix], np.inf)
            sm = (gx[:, None] == gx[None, :]) & (gx[:, None] >= 0)
            okind = (Gi[None, :] - np.where(sm, rdw[:, None], 0.0)) <= lim[None, :]
            # industry lower bound (wb_g − box) on the removed name's industry: a sale/swap may not push it below the
            # bound unless it was already below and the move does not make it worse (industry, style and β checked together)
            glo = wbg - style["ind_box"] * budget - 1e-9
            Gj = np.append(G[gix], np.inf); loj = np.append(glo[gix], -np.inf)
            Gj_new = Gj[:, None] - rdw[:, None] + np.where(sm, dwa[None, :], 0.0)
            okind &= (Gj_new >= loj[:, None]) | (Gj_new >= Gj[:, None] - 1e-12)
            canrem = np.append(qv > 0, True)[:, None]
            newcnt = cnt + np.append(qv == 0, False)[None, :].astype(int) - np.append((qv == lotv) & (qv > 0), False)[:, None].astype(int)
            notself = ~np.eye(n + 1, dtype=bool); notself[n, n] = False
            ok = okc & okcap & okind & canrem & (newcnt >= C.NEFF_LO) & notself & (V2 < v_now - 1e-9)
            if not ok.any(): break
            V2m = np.where(ok, V2, np.inf); jj, ii = np.unravel_index(np.argmin(V2m), V2m.shape)
            if ii < n: q[nm[ii]] += lotv[ii]
            if jj < n: q[nm[jj]] -= lotv[jj]
    while True:
        c = cur(); cash = budget - c.sum()
        if cash <= CASH_MAX: break
        ind_w = c.groupby(c.index.map(lambda n: industry.get(n, "_UNK"))).sum()
        cand = sorted(q, key=lambda i: (-(tgt[i] - c[i]), i)); added = False
        ibox = style["ind_box"] if style else C.IND_ACTIVE
        if style is not None:
            v_now = _style_excess(c, style, ballast_frac); best = None
        for i in cand:
            dw = C.lot_round_rule(i) * P[i] / aum; g = industry.get(i, "_UNK")
            if dw > cash + 1e-12 or c[i] + dw > cap * budget + 1e-9: continue
            gi = ind_w.get(g, 0) + dw
            if gi > C.IND_ABS * budget + 1e-9 or gi - wbi.get(g, 0) > ibox * budget + 1e-9: continue
            if style is None:
                q[i] += C.lot_round_rule(i); added = True; break
            c2 = c.copy(); c2[i] += dw; v2 = _style_excess(c2, style, ballast_frac)
            if v2 > v_now + 1e-12: continue
            key = (round(v2, 12), -(tgt[i] - c[i]), i)  # style repair first, then shortfall, then ticker
            if best is None or key < best[0]: best = (key, i)
        if style is not None and best is not None:
            q[best[1]] += C.lot_round_rule(best[1]); added = True
        if not added: break
    c = cur(); c = c[c > 0]
    for i in nopx: c[i] = tgt[i]
    if ballast_frac > 0: c[C.BALLAST] = ballast_frac
    cash = 1.0 - float(c.sum())
    flag = "OK"; sx = None
    if style is not None:
        ce = c.drop(C.BALLAST, errors="ignore"); sx = _style_excess(ce, style, ballast_frac)
        eqs = float(ce.sum()); gi = ce.groupby(ce.index.map(lambda n: industry.get(n, "_UNK"))).sum()
        ind_bad = any(v > C.IND_ABS * budget + 1e-6 or v - wbi.get(g, 0) > style["ind_box"] * budget + 1e-6 for g, v in gi.items()) or \
                  any(wbi.get(g, 0) - gi.get(g, 0) > style["ind_box"] * budget + 1e-6 for g in wbi.index)
    if (c.drop(C.BALLAST, errors="ignore") > 0).sum() < C.NEFF_LO: flag = "LOT_HARD_FAIL"
    elif style is not None and (sx > 1e-6 or ind_bad): flag = "LOT_HARD_FAIL"
    elif cash > CASH_MAX + 1e-9: flag = "LOT_CASH_GT2"
    return c, {"lot_flag": flag, "style_excess": sx, "cash": cash, "n": int((c.drop(C.BALLAST, errors="ignore") > 0).sum()), "no_price": nopx}
