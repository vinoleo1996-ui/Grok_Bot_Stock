#!/usr/bin/env python3
"""OPTIMIZER Core v1.4 (LOTFIX) runner. Weights + disclosure only. NO returns. live=false, promotion=false. Paper untouched.

Derived from research/optimizer_core_x2_run.py (sha b6238254…, Arch v1.3 PASS). That file is NOT modified; v1.3 products
are never written. Specs (pinned below, checked at start):
  - LOTFIX v1.4 FROZEN text  docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md   d921dd3f…
  - Stop rule (k=3, M1-M6)   docs/v2/STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md  41f29825…
  - AMEND-1 r2.1 (snapshot)  docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md          0029672a…
Run gate: output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_v1_4.ok (Arch writes it; Strategy never creates it) plus
--auth-sha256 equal to that file's sha256. No smoke mode exists in v1.4. Field spec: docs/v2/STRATEGY_V1_4_RUNNER_CHANGES_ZH.md §6.
Unified exception handling (Arch P2-r2-1): once the out dir is claimed, any exit without summary.json writes VOID.md.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, math, os, pickle, re, signal, sys, time, traceback
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C  # data prep / constants (unchanged, read-only)
import optimizer_core_v1_1 as V            # style_ctx / pool_ind_bench / W_FLOOR / CASH_MAX (unchanged, read-only)

VERSION = "v1_4"
CAL = ROOT / "output/strategy_optimizer/calib"
CORE = ROOT / "output/strategy_optimizer/core_x2"        # v1.3 products live here: read-only, never written by v1.4
OUT_FULL = CORE / "v1_4"                                  # v1.4-only output dir (must be absent or empty, LOTFIX §10.6)
EQUIV_ROOT = CORE / "v1_4_equiv"                          # snapshot on/off equivalence runs (AMEND-1 §2)
CK_NAME = "_ckpt_v1_4"                                    # never _ckpt_v1_3_poolind/
AUTH_PATH = CORE / "ARCH_RUN_AUTH_v1_4.ok"
RUNNER_REL = "research/optimizer_core_x2_run_v1_4.py"
EQUIV_REL = "research/v1_4_snapshot_equiv_check.py"
CODE_FILES_V14 = (RUNNER_REL, "research/optimizer_core_v1_1.py", "research/optimizer_lambda_calib_sealed.py")
PINNED_DOCS = {
    "lotfix_sha256": ("docs/v2/STRATEGY_OPTIMIZER_STAGE2_LOTFIX_DRAFT_ZH.md", "d921dd3f0f698deb822a59e40aa643f1efc7f43f6c36eaed30c7a672dbdf9425"),
    "stoprule_sha256": ("docs/v2/STRATEGY_OPTIMIZER_STOPRULE_CONSEC_DRAFT_ZH.md", "41f29825c85a66c889474460605b45a19f5fa475ae46570f299416535cb3559b"),
    "amend_sha256": ("docs/v2/LOTFIX_V1_4_AMEND_POOL_SNAPSHOT_ZH.md", "0029672aed3d9e6a70409e25b02de16291caf5bafbc5c8d8b93624e16719f009"),
}
START, END = "2018-01-02", "2026-10-09"
X2 = ("2024-06-03", "2026-10-09")
AUMS = {600_000: "60w", 1_000_000: "100w"}
SLEEVES = (("equity_100", 0.0), ("equity80_etf20_510300", C.ETF_BALLAST_FRAC))  # B_s = 1 - ballast (LOTFIX §1)
LAMBDA_RISK_FROZEN, LAMBDA_TURN_FROZEN = 117.21317483995702, 0.6             # LOTFIX §1: unchanged, not re-calibrated
EPS_LOT = 1e-6            # LOTFIX §2: rounding tolerance in lots
STRICT_CAP_REL = 1e-9     # LOTFIX §3.1 / Arch P3-1: if +ε would take one lot beyond c_A·B_s·A, use the ε-free m for that name
CASH_MAX = V.CASH_MAX     # 0.02
K_MAX = C.NEFF_HI         # 30 (LOTFIX §4.2)
TOL = 1e-6                # hard-check tolerance (same order as v1.3 lot flags)
TURN_MONITOR = C.TURN_HARD_CAP  # 0.40: monitor only (LOTFIX §6.2), never a constraint
STOP_K = 3                # stop rule §2 / M6 (frozen)
RSS_LIMIT_MB = 1536.0     # AMEND-1 §2: single process RSS ≤ 1.5 GB
FAIL_STATUSES = ("INFEASIBLE", "LOT_HARD_FAIL")
STATUSES = ("OK", "LOT_CASH_GT2", "INFEASIBLE", "LOT_HARD_FAIL", "NO_DATA_CARRY")
EXCLUDED_FROM_EQUIV = ("core_v1_4_pool_snapshot.parquet", "core_v1_4_pool_snapshot_manifest.json", "run_runtime.json")


class RunAborted(BaseException):
    pass


def _json_default(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (pd.Timestamp,)): return str(o.date())
    if isinstance(o, (set, frozenset)): return sorted(o)
    return str(o)


def jdump(x, **kw):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, default=_json_default, **kw)


def sha_file(p):
    return C.file_sha256(Path(p))


def et_now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())


def fnum(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


# ---------------------------------------------------------------- unchanged helpers from b6238254 (same logic)
def frozen_lambdas():
    r = json.loads((CAL / "calib_lambda_risk.json").read_text())
    lr = float(r.get("lambda_risk"))
    lt = {a: float(json.loads((CAL / f"calib_lambda_turn_{t}.json").read_text())["lambda_turn"]) for a, t in AUMS.items()}
    if not (abs(lr - LAMBDA_RISK_FROZEN) < 1e-6 and all(abs(v - LAMBDA_TURN_FROZEN) < 1e-9 for v in lt.values())):
        raise SystemExit(f"frozen lambda check failed: {(lr, lt)}")
    return lr, lt


def _open_days():
    cal = pd.read_parquet(C.CAL_PATH)
    cal["d"] = pd.to_datetime(cal["cal_date"].astype(str), format="%Y%m%d")
    return [pd.Timestamp(x) for x in cal.loc[cal["is_open"] == 1, "d"].sort_values()]


def sessions():
    return [s for s in _open_days() if pd.Timestamp(START) <= s <= pd.Timestamp(END)]


def rebal_days(sess):
    me = C.month_ends(START, END)
    return sorted(set([sess[0]] + me + [sess[-1]]))


def code_sha256_v14():
    per = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE_FILES_V14}
    combo = hashlib.sha256("".join(f"{f}={per[f]}\n" for f in CODE_FILES_V14).encode()).hexdigest()
    return {"combined": combo, "files": per}


# ---------------------------------------------------------------- run gate (structured .ok, Arch P2-1 style)
AUTH_REQUIRED_V14 = ("format", "version", "signed_by", "signed_et", "allow_full", "allow_smoke", "allow_equiv_check",
                     "runner_sha256", "combined_sha256", "equiv_script_sha256", "lotfix_sha256", "stoprule_sha256", "amend_sha256")


def parse_run_auth_v14(path):
    if not path.exists():
        raise SystemExit(f"v1_4 blocked: run-auth file missing: {path} (Arch writes it; Strategy never creates it)")
    kv = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z0-9_]+)=(.*)$", ln.strip())
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if k in kv: raise SystemExit(f"v1_4 blocked: run-auth field '{k}' appears more than once in {path}")
        kv[k] = v
    miss = [k for k in AUTH_REQUIRED_V14 if not kv.get(k)]
    if miss: raise SystemExit(f"v1_4 blocked: run-auth {path} lacks structured fields {miss}")
    if kv["format"] != "quantlab_run_auth_v1": raise SystemExit(f"v1_4 blocked: format={kv['format']!r}")
    if kv["version"] != "v1_4": raise SystemExit(f"v1_4 blocked: version={kv['version']!r}, expected v1_4")
    if kv["signed_by"].lower() != "arch": raise SystemExit(f"v1_4 blocked: signed_by={kv['signed_by']!r}, expected arch")
    for k in ("allow_full", "allow_smoke", "allow_equiv_check"):
        if kv[k] not in ("true", "false"): raise SystemExit(f"v1_4 blocked: {k}={kv[k]!r}, must be exactly true or false")
        kv[k] = kv[k] == "true"
    for k in ("runner_sha256", "combined_sha256", "equiv_script_sha256", "lotfix_sha256", "stoprule_sha256", "amend_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", kv[k]): raise SystemExit(f"v1_4 blocked: {k} is not a 64-hex sha256")
    return kv


def enforce_run_auth_v14(kv, code_sha, mode, auth_file_sha, expected_auth_sha):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_auth_sha or ""):
        raise SystemExit("v1_4 blocked: --auth-sha256 must be the 64-hex sha256 of the Arch .ok")
    if auth_file_sha != expected_auth_sha:
        raise SystemExit(f"v1_4 blocked: .ok sha256 {auth_file_sha} != --auth-sha256 {expected_auth_sha}")
    if kv["allow_smoke"]:
        raise SystemExit("v1_4 blocked: v1.4 has no smoke mode; allow_smoke must be false")
    if kv["runner_sha256"] != code_sha["files"][RUNNER_REL]:
        raise SystemExit(f"v1_4 blocked: runner sha256 {code_sha['files'][RUNNER_REL]} != authorized {kv['runner_sha256']}")
    if kv["combined_sha256"] != code_sha["combined"]:
        raise SystemExit(f"v1_4 blocked: combined code sha256 {code_sha['combined']} != authorized {kv['combined_sha256']}")
    for k, (rel, pin) in PINNED_DOCS.items():
        cur = sha_file(ROOT / rel)
        if cur != pin or kv[k] != pin:
            raise SystemExit(f"v1_4 blocked: {rel} sha256 {cur} / authorized {kv[k]} / pinned {pin} disagree")
    if mode == "full":
        if not kv["allow_full"]: raise SystemExit("v1_4 blocked: full run requested but allow_full is not true")
    elif mode == "equiv":
        if not kv["allow_equiv_check"]: raise SystemExit("v1_4 blocked: equiv run requested but allow_equiv_check is not true")
        cur = sha_file(ROOT / EQUIV_REL)
        if kv["equiv_script_sha256"] != cur:
            raise SystemExit(f"v1_4 blocked: equiv script sha256 {cur} != authorized {kv['equiv_script_sha256']}")
    else:
        raise SystemExit(f"v1_4 blocked: unknown mode {mode!r}")


def expected_out_dir(mode, snap_on):
    if mode == "full": return OUT_FULL
    return EQUIV_ROOT / ("snap_on" if snap_on else "snap_off")


def check_out_dir(out_dir, mode, snap_on):
    out_dir = Path(out_dir).resolve()
    if mode == "full" and not snap_on:
        raise SystemExit("v1_4 blocked: the canonical full run must write the pool snapshot (AMEND-1); --pool-snapshot off is equiv-only")
    if out_dir != expected_out_dir(mode, snap_on).resolve():
        raise SystemExit(f"v1_4 blocked: out dir {out_dir} != {expected_out_dir(mode, snap_on)} for mode={mode}")
    if (ROOT / "output/strategy_hiliq").resolve() in out_dir.parents:
        raise SystemExit("v1_4 blocked: out dir under output/strategy_hiliq")
    if out_dir.exists() and any(out_dir.iterdir()):
        raise SystemExit(f"v1_4 blocked: out dir {out_dir} is not empty (LOTFIX §10.6: new ckpt dir must be empty; no resume/retry)")
    return out_dir


def preflight(mode, out_dir, snap_on, expected_auth_sha):
    """All gate checks; writes nothing. Any failure -> SystemExit before the out dir is claimed (no VOID needed: nothing ran)."""
    for k, (rel, pin) in PINNED_DOCS.items():
        cur = sha_file(ROOT / rel)
        if cur != pin: raise SystemExit(f"v1_4 blocked: {rel} sha256 {cur} != pinned {pin}")
    mask_sha = C.file_sha256(C.MASK_PATH)
    if mask_sha != C.MASK_SHA_EXPECT: raise SystemExit(f"v1_4 blocked: HI_LIQ mask sha {mask_sha} != {C.MASK_SHA_EXPECT}")
    lr, lt = frozen_lambdas()
    cs = code_sha256_v14()
    kv = parse_run_auth_v14(AUTH_PATH)
    auth_sha = sha_file(AUTH_PATH)
    enforce_run_auth_v14(kv, cs, mode, auth_sha, expected_auth_sha)
    od = check_out_dir(out_dir, mode, snap_on)
    return {"lr": lr, "lt": lt, "code_sha": cs, "auth": kv, "auth_sha": auth_sha, "out_dir": od, "mask_sha": mask_sha}


# ---------------------------------------------------------------- S1 / S5 lot arithmetic (LOTFIX §3, §5)
def lot_cap_lots(cA, Bs, aum, L, P):
    """S1: m = floor(c_A·B_s·A/(L·P) + ε). Arch P3-1 choice (to be ratified): if +ε took one lot beyond T, use the ε-free m."""
    T = cA * Bs * aum; u_ = L * P
    m = int(math.floor(T / u_ + EPS_LOT))
    if m > 0 and m * u_ > T * (1.0 + STRICT_CAP_REL):
        m -= 1
    return max(m, 0)


def tier_context(D, px, a):
    """Per (day, tier): lot data, S5 prefilter, S1 caps, full-pool benchmark (prefilter never changes pool/benchmark: §1, Beta L2)."""
    pool = list(D["alpha"].index)
    cA = C.NAME_CAP[a]
    rows = {}
    for i in pool:
        P_ = float(px.get(i, np.nan)) if px is not None else np.nan
        L = C.lot_round_rule(i)
        if np.isfinite(P_) and P_ > 0:
            cost = L * P_
            m = {sv: lot_cap_lots(cA, 1.0 - bf, a, L, P_) for sv, bf in SLEEVES}
            ex = {sv: cost > cA * (1.0 - bf) * a for sv, bf in SLEEVES}       # S5: L·P > T_{A,s}
            in_cand = not any(ex.values())                                    # shared solve -> both sleeves must pass (= ② threshold)
            caps_nav = {sv: m[sv] * cost / a for sv, _ in SLEEVES}            # cap_i^{s,lot} = m·u
            cap_lot = min(caps_nav[sv] / (1.0 - bf) for sv, bf in SLEEVES) if in_cand else 0.0
            if in_cand:
                if min(m.values()) < 1 or cap_lot < cA / 2.0 - 1e-12 or cap_lot > cA + 1e-12:
                    raise RuntimeError(f"S1 invariant broken for {i}: m={m} cap_lot={cap_lot} (LOTFIX §3.1 P2-5)")
            pref = "none" if in_cand else ("sleeve2_only" if (ex["equity80_etf20_510300"] and not ex["equity_100"]) else "both")
            rows[i] = {"price": P_, "lot": L, "u": cost / a, "m": m, "caps_nav": caps_nav, "cap_lot": cap_lot,
                       "in_cand": in_cand, "prefilter": pref, "lot_cost": cost}
        else:  # no price: handled as v1.3 (not excluded, not rounded), recorded as no_price; cap = c_A
            rows[i] = {"price": np.nan, "lot": L, "u": np.nan, "m": {sv: None for sv, _ in SLEEVES}, "caps_nav": {sv: np.nan for sv, _ in SLEEVES},
                       "cap_lot": cA, "in_cand": True, "prefilter": "no_price", "lot_cost": np.nan}
    cand = [i for i in pool if rows[i]["in_cand"]]
    sty = V.style_ctx(D, 0.0, 0.0)  # full-pool z/m/b and wb-weighted zb/mb/bb (slack-independent fields)
    x = D["ln_mcap"].astype(float).reindex(pool)
    m_raw = (x - x.mean()) ** 2
    wbg = V.pool_ind_bench(D)
    return {"pool": pool, "pool_set": set(pool), "rows": rows, "cand": cand, "sty": sty, "wbg": wbg,
            "x_nan": set(x.index[x.isna()]), "size_mu": float(x.mean()), "size_sd": float(x.std(ddof=0)),
            "mid_mu": float(m_raw.mean()), "mid_sd": float(m_raw.std(ddof=0)), "cA": cA}


# ---------------------------------------------------------------- solver (copy of V._solve_support with POOL_STD=IND_POOL=True; only change: w ≤ cap_i^{lot})
def _solve_support_v14(D, w0, names, aum, lr, lt, capmap, size_slack=0.0, ind_slack=0.0, equality=True, floor=True):
    import cvxpy as cp
    alpha, wb = D["alpha"], D["wb"]; ind = D["industry"]; lnm = D["ln_mcap"]
    n = len(names)
    if n == 0: return None, "empty_support"
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
    pool = alpha.index; x = lnm.reindex(pool).astype(float)
    zp = (x - x.mean()) / (x.std(ddof=0) + 1e-12)
    mp = (x - x.mean()) ** 2; mp = (mp - mp.mean()) / (mp.std(ddof=0) + 1e-12)
    wbp = wb.reindex(pool).fillna(0.0)
    zb = float((wbp * zp.fillna(0)).sum()); midb = float((wbp * mp.fillna(0)).sum())
    z = zp.reindex(names).fillna(0).values; mid = mp.reindex(names).fillna(0).values
    bp = D["betas"].reindex(pool).fillna(1.0); beta_b = float((wbp * bp).sum() / max(wbp.sum(), 1e-12))
    gb = V.pool_ind_bench(D); wb_ind = np.array([float(gb.get(g, 0.0)) for g in inds])
    if any(float(v) > C.IND_ACTIVE + ind_slack + 1e-12 for g, v in gb.items() if g not in jx):
        return None, "infeasible_pool_industry_uncovered"
    capv = np.array([float(capmap[nm]) for nm in names])   # S1: per-name lot-aware cap (≤ c_A)
    w = cp.Variable(n, nonneg=True); act = w - wb_v
    risk = cp.quad_form(B.T @ act, F) + cp.sum(cp.multiply(dl, cp.square(act)))
    obj = -(a @ w) + lr * risk + lt * cp.norm1(w - w0_v)
    cons = [(cp.sum(w) == 1.0) if equality else (cp.sum(w) <= 1.0), w <= capv, cp.sum_squares(w) <= 1.0 / C.NEFF_LO]
    if floor: cons.append(w >= V.W_FLOOR)
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


def _solve_with_slack_v14(D, w0, names, aum, lr, lt, capmap, **kw):
    """Slack ladder unchanged (LOTFIX §4.2): (0,0) -> (0.05σ,0.5pp) -> (0.05σ,1pp)."""
    ss, isl = 0.0, 0.0; n_solves = 0
    while True:
        w, st = _solve_support_v14(D, w0, names, aum, lr, lt, capmap, size_slack=ss, ind_slack=isl, **kw); n_solves += 1
        if w is not None: return w, st, {"size_slack": ss, "ind_slack": isl}, n_solves
        if ss >= C.SIZE_SLACK_MAX - 1e-12 and isl >= C.IND_SLACK_MAX - 1e-12: return None, st, {"size_slack": ss, "ind_slack": isl}, n_solves
        ss = min(C.SIZE_SLACK_MAX, ss + 0.05); isl = min(C.IND_SLACK_MAX, isl + 0.005)


# ---------------------------------------------------------------- exposures under bases A/B/C (LOTFIX §6.1) + hard check (basis C judges)
def book_exposures(book, Bs, ctx):
    sty = ctx["sty"]; ind = ctx["ind_map"]; wbg = ctx["wbg"]; pool_set = ctx["pool_set"]
    bal = float(book.get(C.BALLAST, 0.0))
    xe = [(i, float(v)) for i, v in book.items() if i != C.BALLAST and v > 0]
    S = float(sum(v for _, v in xe))
    inp = [(i, v) for i, v in xe if i in pool_set]
    ez = float(sum(v * sty["z"][i] for i, v in inp)); em = float(sum(v * sty["m"][i] for i, v in inp))
    eb = float(sum(v * sty["b"][i] for i, v in inp))
    G = {}
    for i, v in inp:
        g = ind.get(i, "_UNK"); G[g] = G.get(g, 0.0) + v
    gs = sorted(set(G) | set(str(g) for g in wbg.index))
    res = {"n_names": len(xe), "cash": 1.0 - float(book.sum()), "S": S, "bal": bal, "n_out_of_pool": len(xe) - len(inp),
           "out_of_pool_names": ",".join(sorted(i for i, _ in xe if i not in pool_set)),
           "beta_port": eb + bal * sty["bb"], "bases": {}}
    for basis in ("A", "B", "C"):
        if basis == "A":    # v1.3 code basis: 510300 carries benchmark exposure; industry as v1.3 lot check (budget-normalized)
            f = lambda e, b: e + bal * b - b; den = Bs
        elif basis == "B":  # equity-part normalized, cash not in the denominator (disclosure only)
            f = (lambda e, b: e / S - b) if S > 0 else (lambda e, b: np.nan); den = S
        else:               # C: equity sleeve normalized by its budget B_s (judgement basis from v1.4)
            f = lambda e, b: e / Bs - b; den = Bs
        indn = {g: (G.get(g, 0.0) / den if den > 0 else np.nan) for g in gs}
        act = {g: indn[g] - float(wbg.get(g, 0.0)) for g in gs}
        res["bases"][basis] = {"size": f(ez, sty["zb"]), "midcap": f(em, sty["mb"]), "beta": f(eb, sty["bb"]), "ind": indn, "act": act}
    return res


def hard_eval(res, basis, ss, isl):
    b = res["bases"][basis]; reasons = set()
    sbox = C.SIZE_BOX + ss; ibox = C.IND_ACTIVE + isl
    if res["n_names"] < C.NEFF_LO: reasons.add("names")
    for g in b["act"]:
        a_, v_ = b["act"][g], b["ind"][g]
        if not np.isfinite(a_) or a_ > ibox + TOL: reasons.add("industry_upper_rel")
        if not np.isfinite(a_) or -a_ > ibox + TOL: reasons.add("industry_lower_rel")
        if not np.isfinite(v_) or v_ > C.IND_ABS + TOL: reasons.add("industry_abs")
    for k, bound in (("size", sbox), ("midcap", sbox), ("beta", C.BETA_BOX)):
        v = b[k]
        if not np.isfinite(v) or abs(v) > bound + TOL: reasons.add(k)
    return {"hard_pass": not reasons, "reasons": sorted(reasons), "cash_gt2": res["cash"] > CASH_MAX + 1e-9}


# ---------------------------------------------------------------- lot rounding + repair + top-up under basis C (LOTFIX §3.2, §6.1)
def lot_round_v14(w, px, aum, Bs, mlots, ctx, ss, isl, trace, tkey):
    """Derived from V.lot_round_greedy (v1.3). Changes: (1) floor with +ε in lots; (2) caps in lots q_i+L_i ≤ m_i^s·L_i;
    (3) style/β excess in basis C (E = Σx·v/B_s − v_b; 510300 not in HARD); (4) no-price names enter offsets; (5) trace (§7.4)."""
    sty = ctx["sty"]; industry = ctx["ind_map"]; bal = 1.0 - Bs
    wbi = ctx["wbg"] * Bs
    sbox = C.SIZE_BOX + ss; ibox = C.IND_ACTIVE + isl
    tgt = (w.astype(float) * Bs)
    q, P, Lm, nopx, clamp = {}, {}, {}, [], 0
    for i in sorted(tgt.index):
        p_ = px.get(i, np.nan) if px is not None else np.nan
        if not (np.isfinite(p_) and p_ > 0): nopx.append(i); continue
        P[i] = float(p_); Lm[i] = C.lot_round_rule(i)
        lots = int(math.floor(float(tgt[i]) * aum / (P[i] * Lm[i]) + EPS_LOT))
        if lots > mlots[i]: lots = int(mlots[i]); clamp += 1
        q[i] = lots * Lm[i]
    q_floor = {i: q[i] // Lm[i] for i in q}
    z0 = sum(float(tgt[i]) * sty["z"].get(i, 0.0) for i in nopx); m0 = sum(float(tgt[i]) * sty["m"].get(i, 0.0) for i in nopx)
    b0 = sum(float(tgt[i]) * sty["b"].get(i, 1.0) for i in nopx); s0 = sum(float(tgt[i]) for i in nopx)
    n0 = sum(1 for i in nopx if float(tgt[i]) > 0)
    G0 = {}
    for i in nopx: G0[industry.get(i, "_UNK")] = G0.get(industry.get(i, "_UNK"), 0.0) + float(tgt[i])

    def book_now():
        c = {i: q[i] * P[i] / aum for i in q if q[i] > 0}
        for i in nopx: c[i] = float(tgt[i])
        if bal > 0: c[C.BALLAST] = bal
        return pd.Series(c, dtype=float).sort_index()

    def excC(ez, em, eb):
        return (np.maximum(0, np.abs(ez / Bs - sty["zb"]) - sbox) + np.maximum(0, np.abs(em / Bs - sty["mb"]) - sbox)
                + np.maximum(0, np.abs(eb / Bs - sty["bb"]) - C.BETA_BOX))

    def tr(**kv):
        trace.append({**tkey, **kv})

    def cash_now():
        return float(Bs - sum(q[i] * P[i] / aum for i in q) - s0)

    def names_now():
        return int(sum(1 for i in q if q[i] > 0) + n0)

    post_floor = book_now()
    nm = sorted(q); n = len(nm)
    tr(step=0, phase="floor", action="none", add_inst=None, rem_inst=None, lots=None, excess_before=None, excess_after=None,
       cash_before=None, cash_after=cash_now(), n_names=names_now(), stop_reason=None, clamp_count=clamp)
    step = 0
    if n > 0:
        lotv = np.array([Lm[i] for i in nm], float); Pv = np.array([P[i] for i in nm]); dw = lotv * Pv / aum
        mv = np.array([int(mlots[i]) for i in nm])
        Z = np.array([sty["z"].get(i, 0.0) for i in nm]); M = np.array([sty["m"].get(i, 0.0) for i in nm]); Bt = np.array([sty["b"].get(i, 1.0) for i in nm])
        gl = sorted({industry.get(i, "_UNK") for i in nm} | set(G0)); gix = np.array([gl.index(industry.get(i, "_UNK")) for i in nm])
        wbg_a = np.array([float(wbi.get(g, 0.0)) for g in gl]); G0a = np.array([G0.get(g, 0.0) for g in gl])
        glim = np.minimum(C.IND_ABS * Bs, wbg_a + ibox * Bs) + 1e-9
        glo = wbg_a - ibox * Bs - 1e-9
        stop = "iter_cap_300"
        for _ in range(300):
            qv = np.array([q[i] for i in nm], float); w_ = qv * Pv / aum
            ez, em, eb = w_ @ Z + z0, w_ @ M + m0, w_ @ Bt + b0; v_now = float(excC(ez, em, eb))
            if v_now <= 1e-9: stop = "excess_zero"; break
            cash = Bs - w_.sum() - s0; G = np.bincount(gix, weights=w_, minlength=len(gl)) + G0a; cnt = int((qv > 0).sum()) + n0
            # rows j = removed (row n = none), cols i = added (col n = none, i.e. pure one-lot sale) — same layout as v1.3
            dz = np.append(dw * Z, 0); dm = np.append(dw * M, 0); db = np.append(dw * Bt, 0); dwa = np.append(dw, 0)
            EZ = ez + dz[None, :] - dz[:, None]; EM = em + dm[None, :] - dm[:, None]; EB = eb + db[None, :] - db[:, None]
            V2 = excC(EZ, EM, EB)
            okc = (cash - dwa[None, :] + dwa[:, None]) >= -1e-12
            qlots = np.round(qv / lotv).astype(int)
            okcap = np.broadcast_to(np.append(qlots + 1 <= mv, True)[None, :], V2.shape)      # q_i + L_i ≤ m_i·L_i
            gx = np.append(gix, -1)
            Gi = np.append(G[gix] + dw, -np.inf); lim = np.append(glim[gix], np.inf)
            sm = (gx[:, None] == gx[None, :]) & (gx[:, None] >= 0)
            okind = (Gi[None, :] - np.where(sm, dwa[:, None], 0.0)) <= lim[None, :]
            Gj = np.append(G[gix], np.inf); loj = np.append(glo[gix], -np.inf)
            Gj_new = Gj[:, None] - dwa[:, None] + np.where(sm, dwa[None, :], 0.0)
            okind = okind & ((Gj_new >= loj[:, None]) | (Gj_new >= Gj[:, None] - 1e-12))
            canrem = np.append(qv > 0, True)[:, None]
            newcnt = cnt + np.append(qv == 0, False)[None, :].astype(int) - np.append((qv == lotv) & (qv > 0), False)[:, None].astype(int)
            notself = ~np.eye(n + 1, dtype=bool); notself[n, n] = False
            base = okc & okind & canrem & (newcnt >= C.NEFF_LO) & notself & (V2 < v_now - 1e-9)
            ok = base & okcap
            if not ok.any():
                stop = "cap_lot_block" if base.any() else "no_candidate"; break
            V2m = np.where(ok, V2, np.inf); jj, ii = np.unravel_index(np.argmin(V2m), V2m.shape)
            cb = float(cash)
            if ii < n: q[nm[ii]] += int(lotv[ii])
            if jj < n: q[nm[jj]] -= int(lotv[jj])
            step += 1
            act = "swap" if (ii < n and jj < n) else ("add" if ii < n else "sell")
            tr(step=step, phase="style_repair", action=act, add_inst=(nm[ii] if ii < n else None), rem_inst=(nm[jj] if jj < n else None),
               lots=1, excess_before=v_now, excess_after=float(V2[jj, ii]), cash_before=cb, cash_after=cash_now(),
               n_names=names_now(), stop_reason=None, clamp_count=None)
        tr(step=step, phase="style_repair", action="none", add_inst=None, rem_inst=None, lots=None, excess_before=None, excess_after=None,
           cash_before=None, cash_after=None, n_names=None, stop_reason=stop, clamp_count=None)
    post_repair = book_now()
    # cash top-up (v1.3 loop; cap in lots; style may not get worse in basis C)
    stop = "no_candidate"
    while True:
        c = {i: q[i] * P[i] / aum for i in q}; cash = Bs - sum(c.values()) - s0
        if cash <= CASH_MAX: stop = "cash_le_2pct"; break
        if not q: stop = "no_candidate"; break
        ind_w = dict(G0)
        for i, v in c.items(): ind_w[industry.get(i, "_UNK")] = ind_w.get(industry.get(i, "_UNK"), 0.0) + v
        ez = sum(v * sty["z"].get(i, 0.0) for i, v in c.items()) + z0; em = sum(v * sty["m"].get(i, 0.0) for i, v in c.items()) + m0
        eb = sum(v * sty["b"].get(i, 1.0) for i, v in c.items()) + b0
        v_now = float(excC(ez, em, eb))
        best = None; capblock = False
        for i in sorted(q, key=lambda i: (-(float(tgt[i]) - c[i]), i)):
            dwi = Lm[i] * P[i] / aum; g = industry.get(i, "_UNK")
            if dwi > cash + 1e-12: continue
            gi = ind_w.get(g, 0.0) + dwi
            if gi > C.IND_ABS * Bs + 1e-9 or gi - float(wbi.get(g, 0.0)) > ibox * Bs + 1e-9: continue
            v2 = float(excC(ez + dwi * sty["z"].get(i, 0.0), em + dwi * sty["m"].get(i, 0.0), eb + dwi * sty["b"].get(i, 1.0)))
            if v2 > v_now + 1e-12: continue
            if q[i] // Lm[i] + 1 > int(mlots[i]): capblock = True; continue      # q_i + L_i ≤ m_i·L_i
            key = (round(v2, 12), -(float(tgt[i]) - c[i]), i)
            if best is None or key < best[0]: best = (key, i, v2)
        if best is None:
            stop = "cap_lot_block" if capblock else "no_candidate"; break
        q[best[1]] += Lm[best[1]]; step += 1
        tr(step=step, phase="cash_topup", action="add", add_inst=best[1], rem_inst=None, lots=1, excess_before=v_now, excess_after=best[2],
           cash_before=float(cash), cash_after=cash_now(), n_names=names_now(), stop_reason=None, clamp_count=None)
    tr(step=step, phase="cash_topup", action="none", add_inst=None, rem_inst=None, lots=None, excess_before=None, excess_after=None,
       cash_before=None, cash_after=None, n_names=None, stop_reason=stop, clamp_count=None)
    final = book_now()
    q_final = {i: q[i] // Lm[i] for i in q}
    return final, {"post_floor": post_floor, "post_repair": post_repair, "q_floor": q_floor, "q_final": q_final,
                   "no_price": nopx, "clamp_count": clamp}


# ---------------------------------------------------------------- attempt bookkeeping
def solver_book(w, Bs):
    b = (w.astype(float) * Bs)
    if Bs < 1.0: b = pd.concat([b, pd.Series({C.BALLAST: 1.0 - Bs})])
    return b.sort_index()


def neff(v):
    v = np.asarray(v, float); v = v[v > 0]
    if v.size == 0: return None
    v = v / v.sum(); return float(1.0 / (v ** 2).sum())


def one_way(a, b):
    if a is None or b is None: return None
    idx = a.index.union(b.index)
    return 0.5 * float((a.reindex(idx).fillna(0.0) - b.reindex(idx).fillna(0.0)).abs().sum())


def run_attempt(K, w, st, sl, phase, idx, a, ctx, px, held, prev_w):
    att = {"attempt": idx, "K": K, "phase": phase, "solver_status": st, "slack": sl, "w": w,
           "sleeves": {}, "hard_both": False, "strict_both": False}
    if w is None:
        att["solver_status"] = "infeasible" if not str(st).startswith("ERR") else str(st)
        return att
    att["one_way_solver"] = one_way(w, prev_w)
    att["neff_solver"] = neff(w.values)
    hb, sb = True, True
    for sv, bf in SLEEVES:
        Bs = 1.0 - bf
        mlots = {i: (ctx["rows"][i]["m"][sv] if ctx["rows"][i]["m"][sv] is not None else 0) for i in w.index}
        trace = []
        tkey = {"aum": a, "sleeve": sv, "K": K, "attempt": idx}
        final, li = lot_round_v14(w, px, a, Bs, mlots, ctx, sl["size_slack"], sl["ind_slack"], trace, tkey)
        stages = {"solver": solver_book(w, Bs), "post_floor": li["post_floor"], "post_repair": li["post_repair"], "final": final}
        expo = {k: book_exposures(b, Bs, ctx) for k, b in stages.items()}
        chk = hard_eval(expo["final"], "C", sl["size_slack"], sl["ind_slack"])
        eq = final.drop(C.BALLAST, errors="ignore")
        att["sleeves"][sv] = {"book": final, "li": li, "stages": stages, "expo": expo, "chk": chk, "trace": trace,
                              "neff_lot": neff(eq.values), "one_way_lot": one_way(final, held.get(sv))}
        hb = hb and chk["hard_pass"]; sb = sb and chk["hard_pass"] and not chk["cash_gt2"]
    att["hard_both"], att["strict_both"] = hb, sb
    return att


def ktrace_entry(att):
    e = {"K": att["K"], "attempt": att["attempt"], "phase": att["phase"], "solver_status": att["solver_status"], "slack": att["slack"]}
    if att["w"] is not None:
        e.update({"hard": {sv: x["chk"]["hard_pass"] for sv, x in att["sleeves"].items()},
                  "cash": {sv: round(x["expo"]["final"]["cash"], 10) for sv, x in att["sleeves"].items()},
                  "reasons": {sv: x["chk"]["reasons"] for sv, x in att["sleeves"].items()}, "strict_both": att["strict_both"]})
    return e


def solve_tier(D, px, a, lr, lt_a, prev_w, held, ctx):
    """LOTFIX §4.3 order: existing K loop (cap -> cap_lot) -> lot at K_sel -> S3 K_sel+1..30 -> smallest hard-OK K -> LOT_HARD_FAIL."""
    w0 = (prev_w if prev_w is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
    capmap = {i: ctx["rows"][i]["cap_lot"] for i in ctx["pool"]}
    cand = ctx["cand"]
    out = {"attempts": [], "K_sel": None, "k0": None, "adopt": None, "fail_stage": None, "s3_trigger": "none", "s3_used": False,
           "step1": None, "solve_infeasible_K": []}
    w1, st1, sl1, _ = _solve_with_slack_v14(D, w0, cand, a, lr, lt_a, capmap, equality=True, floor=False)
    out["step1"] = {"status": st1 if w1 is not None else "infeasible", "slack": sl1}
    if w1 is None:
        out["fail_stage"] = "solve"; return out
    order = sorted(cand, key=lambda n: (-abs(w1[n]), n))
    k0 = int(np.clip((w1 >= V.W_FLOOR).sum(), C.NEFF_LO, C.NEFF_HI)); out["k0"] = k0
    ks = list(range(k0, C.NEFF_HI + 1)) + list(range(k0 - 1, C.NEFF_LO - 1, -1))
    bad_K = set(); sel = None
    for K in ks:
        w, st, sl, _ = _solve_with_slack_v14(D, w0, order[:K], a, lr, lt_a, capmap, equality=True, floor=True)
        att = run_attempt(K, w, st, sl, "solve_loop", len(out["attempts"]), a, ctx, px, held, prev_w)
        out["attempts"].append(att)
        if w is None: bad_K.add(K); continue
        sel = att; break
    out["solve_infeasible_K"] = sorted(bad_K)
    if sel is None:
        out["fail_stage"] = "solve"; return out
    out["K_sel"] = sel["K"]
    if sel["strict_both"]:
        out["adopt"] = sel; return out
    out["s3_used"] = True; out["s3_trigger"] = "hard" if not sel["hard_both"] else "cash"
    retry = [K for K in range(sel["K"] + 1, K_MAX + 1) if K not in bad_K][: max(0, K_MAX - sel["K"])]
    for K in retry:
        w, st, sl, _ = _solve_with_slack_v14(D, w0, order[:K], a, lr, lt_a, capmap, equality=True, floor=True)
        att = run_attempt(K, w, st, sl, "s3", len(out["attempts"]), a, ctx, px, held, prev_w)
        out["attempts"].append(att)
        if w is not None and att["strict_both"]:
            out["adopt"] = att; return out
    evald = [x for x in out["attempts"] if x["w"] is not None and x["K"] >= sel["K"] and x["hard_both"]]
    if evald:
        out["adopt"] = min(evald, key=lambda x: (x["K"], x["attempt"])); return out
    out["fail_stage"] = "lot"; return out


# ---------------------------------------------------------------- incremental writers (deterministic, per day append)
ATT_SCHEMA = pa.schema([("date", pa.string()), ("aum", pa.int64()), ("K", pa.int64()), ("attempt", pa.int64()), ("phase", pa.string()),
    ("solver_status", pa.string()), ("size_slack", pa.float64()), ("ind_slack", pa.float64()), ("instrument", pa.string()),
    ("w_solver", pa.float64()), ("cap_lot", pa.float64()), ("lot", pa.int64()), ("price", pa.float64()), ("u", pa.float64()),
    ("sleeve", pa.string()), ("q_floor", pa.int64()), ("q_final", pa.int64()), ("x_lot", pa.float64()), ("at_cap_lot", pa.bool_()),
    ("selected", pa.bool_()), ("beta_i", pa.float64()), ("size_z_i", pa.float64()), ("midcap_m_i", pa.float64()), ("sw_l1", pa.string()),
    ("s3_trigger", pa.string()), ("lot_flag", pa.string()), ("hard_pass_C", pa.bool_()), ("strict_pass_C", pa.bool_())])
SNAP_SCHEMA = pa.schema([("date", pa.string()), ("tier", pa.int64()), ("sleeve", pa.string()), ("code", pa.string()), ("instrument", pa.string()),
    ("in_pool", pa.bool_()), ("in_candidate", pa.bool_()), ("price", pa.float64()), ("lot_size", pa.int64()), ("lots", pa.int64()),
    ("u_i", pa.float64()), ("cap_lot", pa.float64()), ("cap_lot_sleeve", pa.float64()), ("m_lots", pa.int64()), ("beta", pa.float64()),
    ("size_z", pa.float64()), ("midcap_m", pa.float64()), ("exposure_filled", pa.bool_()), ("sw_l1", pa.string()), ("wb_i", pa.float64()),
    ("q_cont", pa.float64()), ("q_final", pa.float64()), ("selected", pa.bool_()), ("stage", pa.string()), ("K_sel", pa.int64()),
    ("k_final", pa.int64()), ("prefilter", pa.string())])


class Writers:
    def __init__(self, out_dir):
        self.out = out_dir; self.pq = {}; self.csv_started = set()

    def parquet(self, name, schema, rows):
        if not rows: return
        t = pa.Table.from_pydict({f.name: [r.get(f.name) for r in rows] for f in schema}, schema=schema)
        if name not in self.pq: self.pq[name] = pq.ParquetWriter(str(self.out / name), schema)
        self.pq[name].write_table(t)

    def csv(self, name, rows, columns):
        if not rows: return
        df = pd.DataFrame(rows, columns=list(columns))
        first = name not in self.csv_started
        df.to_csv(self.out / name, mode="w" if first else "a", header=first, index=False)
        self.csv_started.add(name)

    def jsonl(self, name, rows):
        if not rows: return
        with open(self.out / name, "a", encoding="utf-8") as f:
            for r in rows: f.write(jdump(r) + "\n")

    def close(self):
        for k in sorted(self.pq): self.pq[k].close()
        self.pq = {}


def _code(inst):
    if inst == C.BALLAST: return "sh.510300"
    s = str(inst).split(".")
    return f"{s[1].lower()}.{s[0]}" if len(s) == 2 else str(inst)


# ---------------------------------------------------------------- AMEND-1 pool snapshot (write-only; called only when --pool-snapshot on)
def build_pool_snapshot(day_s, a, sv, Bs, D, ctx, held_book, adopt_w, stage, K_sel, k_final, beta_port_disc):
    """One row per full-pool name (incl. S5-excluded / cap_lot=0), plus carried out-of-pool names, CASH and sh.510300.
    Reads only; never mutates its inputs; its return value feeds nothing but the snapshot file. Raises on A1/A3/coverage failure."""
    sty = ctx["sty"]; rows = []
    book = held_book if held_book is not None else pd.Series(dtype=float)
    braw = D["betas"].reindex(ctx["pool"])
    for i in ctx["pool"]:
        r = ctx["rows"][i]; qf = float(book.get(i, 0.0)); bi = float(braw.get(i, np.nan))
        priced = bool(np.isfinite(r["price"]))
        rows.append({"date": day_s, "tier": a, "sleeve": sv, "code": _code(i), "instrument": i, "in_pool": True, "in_candidate": bool(r["in_cand"]),
            "price": fnum(r["price"]), "lot_size": int(r["lot"]),
            "lots": ((int(round(qf * a / (r["lot"] * r["price"]))) if qf > 0 else 0) if priced else None),
            "u_i": fnum(r["u"]), "cap_lot": float(r["cap_lot"]), "cap_lot_sleeve": fnum(r["caps_nav"][sv]),
            "m_lots": (int(r["m"][sv]) if r["m"][sv] is not None else None),
            "beta": (bi if np.isfinite(bi) else None),                                          # A4: missing -> NaN (never 0)
            "size_z": (None if i in ctx["x_nan"] else float(sty["z"][i])), "midcap_m": (None if i in ctx["x_nan"] else float(sty["m"][i])),
            "exposure_filled": bool(i in ctx["x_nan"] or not np.isfinite(bi)), "sw_l1": str(ctx["ind_map"].get(i, "_UNK")),
            "wb_i": float(D["wb"].get(i, 0.0)), "q_cont": (float(adopt_w.get(i, 0.0)) * Bs if adopt_w is not None else None),
            "q_final": qf, "selected": bool(qf > 0), "stage": stage, "K_sel": K_sel, "k_final": k_final, "prefilter": r["prefilter"]})
    for i in sorted(x for x in book.index if x != C.BALLAST and x not in ctx["pool_set"] and float(book[x]) > 0):
        rows.append({"date": day_s, "tier": a, "sleeve": sv, "code": _code(i), "instrument": i, "in_pool": False, "in_candidate": False,
            "price": None, "lot_size": int(C.lot_round_rule(i)), "lots": None, "u_i": None, "cap_lot": None, "cap_lot_sleeve": None, "m_lots": None,
            "beta": None, "size_z": None, "midcap_m": None, "exposure_filled": False, "sw_l1": None, "wb_i": None, "q_cont": None,
            "q_final": float(book[i]), "selected": True, "stage": stage, "K_sel": K_sel, "k_final": k_final, "prefilter": "out_of_pool_carry"})
    bal = float(book.get(C.BALLAST, 0.0)); cash = 1.0 - float(book.sum())
    rows.append({"date": day_s, "tier": a, "sleeve": sv, "code": "sh.510300", "instrument": C.BALLAST, "in_pool": False, "in_candidate": False,
        "price": None, "lot_size": None, "lots": None, "u_i": None, "cap_lot": None, "cap_lot_sleeve": None, "m_lots": None,
        "beta": float(sty["bb"]), "size_z": None, "midcap_m": None, "exposure_filled": False, "sw_l1": None, "wb_i": None,
        "q_cont": ((1.0 - Bs) if adopt_w is not None else None), "q_final": bal, "selected": bool(bal > 0), "stage": stage,
        "K_sel": K_sel, "k_final": k_final, "prefilter": "ballast"})
    rows.append({"date": day_s, "tier": a, "sleeve": sv, "code": "CASH", "instrument": "CASH", "in_pool": False, "in_candidate": False,
        "price": None, "lot_size": None, "lots": None, "u_i": None, "cap_lot": None, "cap_lot_sleeve": None, "m_lots": None,
        "beta": 0.0, "size_z": None, "midcap_m": None, "exposure_filled": False, "sw_l1": None, "wb_i": None, "q_cont": None,
        "q_final": cash, "selected": bool(cash > 0), "stage": stage, "K_sel": K_sel, "k_final": k_final, "prefilter": "cash"})
    # ---- checks (raise -> unified handler -> VOID) ----
    inpool = [r for r in rows if r["in_pool"]]
    swb = sum(r["wb_i"] for r in inpool)
    swbb = sum(r["wb_i"] * float(sty["b"][r["instrument"]]) for r in inpool)   # β exactly as used by solver/recheck
    if abs(swb - 1.0) > 1e-9: raise RuntimeError(f"AMEND-1 A1 failed {day_s} {a} {sv}: Σwb_i={swb!r}")
    if abs(swbb - float(sty["bb"])) > 1e-9: raise RuntimeError(f"AMEND-1 A1 failed {day_s} {a} {sv}: Σwb·β={swbb!r} != bb={sty['bb']!r}")
    if cash < -1e-9: raise RuntimeError(f"AMEND-1 A3 failed {day_s} {a} {sv}: negative cash {cash!r}")
    sq = sum(r["q_final"] for r in rows)
    if abs(sq - 1.0) > 1e-6: raise RuntimeError(f"AMEND-1 A3 failed {day_s} {a} {sv}: Σq_final={sq!r}")
    for r in rows:
        if r["q_final"] > 0 and not r["selected"]: raise RuntimeError(f"AMEND-1 coverage failed {day_s} {a} {sv}: {r['code']}")
        if r["in_pool"] and r["q_final"] > 0 and r["beta"] is None:
            raise RuntimeError(f"AMEND-1 A3 cannot verify {day_s} {a} {sv}: held {r['code']} has missing β")
    held_codes = {_code(i) for i, v in book.items() if float(v) > 0}
    sel_codes = {r["code"] for r in rows if r["selected"]}
    if not held_codes <= sel_codes: raise RuntimeError(f"AMEND-1 coverage failed {day_s} {a} {sv}: {sorted(held_codes - sel_codes)}")
    sqb = sum(r["q_final"] * r["beta"] for r in rows if r["beta"] is not None and (r["in_pool"] or r["code"] in ("CASH", "sh.510300")))
    if beta_port_disc is None or abs(sqb - beta_port_disc) > 1e-6:
        raise RuntimeError(f"AMEND-1 A3 failed {day_s} {a} {sv}: Σq_final·β={sqb!r} != disclosure beta_port={beta_port_disc!r}")
    return rows


# ---------------------------------------------------------------- disclosure helpers
def beta_window(open_days, d):
    prior = [x for x in open_days if x <= d][-C.L_BETA:]
    return (str(prior[0].date()) if prior else None, str(prior[-1].date()) if prior else None, len(prior))


def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.size < 3: return None
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3 or np.std(a[ok]) < 1e-15 or np.std(b[ok]) < 1e-15: return None
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def load_v13_eq100():
    """§5 disclosure item 1: v1.3 ① holdings (read-only). Returns ({(date, aum): {inst: w}}, {file: sha})."""
    out, shas = {}, {}
    for a, tag in AUMS.items():
        p = CORE / f"core_equity_100_{tag}.parquet"
        if not p.exists(): continue
        shas[str(p.relative_to(ROOT))] = sha_file(p)
        df = pd.read_parquet(p, columns=["session", "instrument", "weight"])
        for s, g in df.groupby("session", sort=True):
            out[(str(s), a)] = dict(zip(g["instrument"].astype(str), g["weight"].astype(float)))
        del df
    return out, shas


DISC_COLS = ["date", "window", "aum", "sleeve", "status", "fail_stage", "carry", "K0", "K_sel", "k_final", "delta_k", "k_trace", "s3_used",
    "s3_trigger", "s3_rescued_from_hard", "s3_rescued_from_cash", "lot_fail_reason", "cash_gt2", "solve_infeasible_K", "step1_status",
    "size_slack", "ind_slack", "n_names", "cash", "beta_port", "neff_solver", "neff_lot", "one_way_solver", "one_way_lot",
    "one_way_solver_ksel", "one_way_lot_ksel", "n_prefilter", "n_prefilter_sleeve2_only", "n_no_price", "clamp_count",
    "size_act_A", "midcap_act_A", "beta_act_A", "size_act_B", "midcap_act_B", "beta_act_B", "size_act_C", "midcap_act_C", "beta_act_C",
    "ind_active_max_C", "ind_abs_max_C", "carry_n_out_of_pool", "carry_out_of_pool_names", "turn_solver_gt40", "turn_lot_gt40"]
STYLE_COLS = ["date", "aum", "sleeve", "K", "attempt", "stage", "basis", "size_act", "size_bound", "size_excess", "midcap_act", "midcap_bound",
    "midcap_excess", "beta_act", "beta_bound", "beta_excess", "cash"]
IND_COLS = ["date", "aum", "sleeve", "K", "attempt", "stage", "basis", "sw_l1", "G", "wb_g", "active", "bound_rel", "bound_abs", "breach_type", "excess"]
B15_COLS = ["date", "aum", "sleeve", "K", "attempt", "beta_act_C", "pass_beta010", "pass_beta015", "other_hard_pass", "beta15_would_rescue"]
BENCH_COLS = ["date", "aum", "bb", "zb", "mb", "size_mu", "size_sd", "mid_mu", "mid_sd", "beta_window_start", "beta_window_end", "beta_window_n",
    "beta_window_source", "pool_n", "n_prefilter", "n_prefilter_sleeve2_only", "wb_share_prefiltered", "wb_beta_prefiltered", "wb_size_prefiltered",
    "caplot_cut_sum", "corr_cut_lnprice", "corr_cut_size", "corr_cut_beta", "caplot_cut_sum_support", "corr_cut_lnprice_support",
    "corr_cut_size_support", "corr_cut_beta_support", "n_at_cap_lot_support", "sum_caplot_support"]
CARRY_COLS = ["date", "aum", "sleeve", "basis", "size_act", "midcap_act", "beta_act", "ind_active_max", "ind_abs_max", "cash",
    "carry_n_out_of_pool", "carry_out_of_pool_names"]
PREF_COLS = ["date", "aum", "instrument", "sw_l1", "price", "lot", "lot_cost", "T_sleeve1", "T_sleeve2", "prefilter", "wb_i", "beta", "size_z",
    "midcap_m", "v13_eq100_weight"]
S3CASH_COLS = ["date", "aum", "sleeve", "K_sel", "k_final", "delta_k", "rescued", "one_way_solver", "one_way_solver_ksel", "one_way_lot", "one_way_lot_ksel"]
TRACE_FILE = "core_v1_4_repair_trace.jsonl"


def _maxabs(d):
    v = [abs(x) for x in d.values() if np.isfinite(x)]
    return max(v) if v else None


def _max(d):
    v = [x for x in d.values() if np.isfinite(x)]
    return max(v) if v else None


def style_rows(day_s, a, sv, K, idx, stage, expo, ss):
    out = []; sb = C.SIZE_BOX + ss
    ex = lambda v, bd: (max(0.0, abs(v) - bd) if np.isfinite(v) else None)
    for basis in ("A", "B", "C"):
        b = expo["bases"][basis]
        out.append({"date": day_s, "aum": a, "sleeve": sv, "K": K, "attempt": idx, "stage": stage, "basis": basis,
                    "size_act": fnum(b["size"]), "size_bound": sb, "size_excess": ex(b["size"], sb),
                    "midcap_act": fnum(b["midcap"]), "midcap_bound": sb, "midcap_excess": ex(b["midcap"], sb),
                    "beta_act": fnum(b["beta"]), "beta_bound": C.BETA_BOX, "beta_excess": ex(b["beta"], C.BETA_BOX), "cash": expo["cash"]})
    return out


def ind_rows(day_s, a, sv, K, idx, stage, expo, ctx, isl):
    out = []; br = C.IND_ACTIVE + isl
    for basis in ("A", "B", "C"):
        b = expo["bases"][basis]
        for g in sorted(b["ind"]):
            G_, act = b["ind"][g], b["act"][g]; wbg = float(ctx["wbg"].get(g, 0.0))
            bt, exc = "none", 0.0
            if np.isfinite(G_):
                worst = max([("upper_rel", act - br), ("lower_rel", -act - br), ("abs", G_ - C.IND_ABS)], key=lambda t: t[1])
                if worst[1] > TOL: bt, exc = worst[0], float(worst[1])
            out.append({"date": day_s, "aum": a, "sleeve": sv, "K": K, "attempt": idx, "stage": stage, "basis": basis, "sw_l1": g,
                        "G": fnum(G_), "wb_g": wbg, "active": fnum(act), "bound_rel": br, "bound_abs": C.IND_ABS, "breach_type": bt, "excess": exc})
    return out


def _books_rec(held_a):
    return {sv: (sorted((str(i), float(v)) for i, v in held_a[sv].items()) if held_a[sv] is not None else None) for sv, _ in SLEEVES}


# ---------------------------------------------------------------- main loop
def run_v14(out_dir, snap_on, lr, lt, code_sha):
    ck_dir = out_dir / CK_NAME; ck_dir.mkdir(parents=True, exist_ok=False)
    W = Writers(out_dir)
    open_days = _open_days(); sess = sessions(); rd = rebal_days(sess)
    v13_eq100, v13_shas = load_v13_eq100()
    prev_w = {a: None for a in AUMS}
    held = {a: {sv: None for sv, _ in SLEEVES} for a in AUMS}
    disc_all, s3_cash_rows, runtime_days, snap_rows_n = [], [], [], 0
    for d in rd:
        t0 = time.time(); day_s = f"{d:%Y-%m-%d}"; win = "X2" if d >= pd.Timestamp(X2[0]) else "SEALED"
        D = C.prepare_day(d)
        day = {k: [] for k in ("att", "style", "ind", "b15", "bench", "carry", "pref", "trace", "disc", "snap")}
        rec = {"day": day_s, "version": VERSION, "code_sha256": code_sha, "tiers": {}}
        px = None
        if D is not None:  # PIT close on the rebalance day, ≤10 calendar days look-back, last print (same as v1.3)
            b = C.load_daily_basic_window(sorted(set(D["alpha"].index)), d - pd.Timedelta(days=10), d)
            b["trade_date"] = pd.to_datetime(b["trade_date"])
            px = b.sort_values("trade_date", kind="mergesort").groupby("ts_code")["close"].last()
            del b
        for a in AUMS:
            if D is None:  # stop rule M5: no-data day is skipped (neither breaks nor extends a run)
                for sv, _ in SLEEVES:
                    day["disc"].append({"date": day_s, "window": win, "aum": a, "sleeve": sv, "status": "NO_DATA_CARRY",
                                        "carry": ("prior_holdings" if held[a][sv] is not None else "all_cash")})
                rec["tiers"][a] = {"status": "NO_DATA_CARRY", "books": _books_rec(held[a])}
                continue
            ctx = tier_context(D, px, a); ctx["ind_map"] = D["industry"]
            held_before = dict(held[a])
            res = solve_tier(D, px, a, lr, lt[a], prev_w[a], held_before, ctx)
            ad = res["adopt"]; ksel = res["K_sel"]; trig = res["s3_trigger"]
            sel_att = next((x for x in res["attempts"] if x["phase"] == "solve_loop" and x["w"] is not None), None)
            # ---- §7.1–§7.5 per attempt ----
            for att in res["attempts"]:
                K, idx, sl = att["K"], att["attempt"], att["slack"]
                if att["w"] is None:
                    day["att"].append({"date": day_s, "aum": a, "K": K, "attempt": idx, "phase": att["phase"], "solver_status": att["solver_status"],
                        "size_slack": sl["size_slack"], "ind_slack": sl["ind_slack"], "sleeve": "SOLVER", "s3_trigger": trig, "selected": False})
                    continue
                for sv, bf in SLEEVES:
                    x = att["sleeves"][sv]; li = x["li"]; fb = x["book"]
                    flag = "LOT_HARD_FAIL" if not x["chk"]["hard_pass"] else ("LOT_CASH_GT2" if x["chk"]["cash_gt2"] else "OK")
                    for i in sorted(att["w"].index):
                        r = ctx["rows"][i]
                        day["att"].append({"date": day_s, "aum": a, "K": K, "attempt": idx, "phase": att["phase"], "solver_status": att["solver_status"],
                            "size_slack": sl["size_slack"], "ind_slack": sl["ind_slack"], "instrument": i, "w_solver": float(att["w"][i]),
                            "cap_lot": float(r["cap_lot"]), "lot": int(r["lot"]), "price": fnum(r["price"]), "u": fnum(r["u"]), "sleeve": sv,
                            "q_floor": (int(li["q_floor"][i]) if i in li["q_floor"] else None), "q_final": (int(li["q_final"][i]) if i in li["q_final"] else None),
                            "x_lot": float(fb.get(i, 0.0)), "at_cap_lot": bool(float(att["w"][i]) >= r["cap_lot"] - 1e-9), "selected": ad is att,
                            "beta_i": float(ctx["sty"]["b"][i]), "size_z_i": float(ctx["sty"]["z"][i]), "midcap_m_i": float(ctx["sty"]["m"][i]),
                            "sw_l1": str(D["industry"].get(i, "_UNK")), "s3_trigger": trig, "lot_flag": flag,
                            "hard_pass_C": bool(x["chk"]["hard_pass"]), "strict_pass_C": bool(x["chk"]["hard_pass"] and not x["chk"]["cash_gt2"])})
                    for stg in ("solver", "post_floor", "post_repair", "final"):
                        day["style"] += style_rows(day_s, a, sv, K, idx, stg, x["expo"][stg], sl["size_slack"])
                        day["ind"] += ind_rows(day_s, a, sv, K, idx, stg, x["expo"][stg], ctx, sl["ind_slack"])
                    bC = x["expo"]["final"]["bases"]["C"]["beta"]
                    p10 = bool(np.isfinite(bC) and abs(bC) <= C.BETA_BOX + TOL); p15 = bool(np.isfinite(bC) and abs(bC) <= 0.15 + TOL)
                    other = all(r_ == "beta" for r_ in x["chk"]["reasons"])
                    day["b15"].append({"date": day_s, "aum": a, "sleeve": sv, "K": K, "attempt": idx, "beta_act_C": fnum(bC), "pass_beta010": p10,
                        "pass_beta015": p15, "other_hard_pass": bool(other), "beta15_would_rescue": bool(other and not p10 and p15)})
                    day["trace"] += [{"date": day_s, **t} for t in x["trace"]]
            # ---- §7.6 daily bench + S1/S5 tilt (Beta L3); §5 prefilter detail ----
            sty = ctx["sty"]; rows = ctx["rows"]; wb = D["wb"]; cA = ctx["cA"]
            excl = [i for i in ctx["pool"] if not rows[i]["in_cand"]]
            s2o = [i for i in excl if rows[i]["prefilter"] == "sleeve2_only"]
            wbe = float(sum(float(wb.get(i, 0.0)) for i in excl))
            pr = [i for i in ctx["cand"] if np.isfinite(rows[i]["price"])]
            h = [1.0 - rows[i]["cap_lot"] / cA for i in pr]
            wsup = ad["w"] if ad is not None else (sel_att["w"] if sel_att is not None else None)
            sup = [i for i in (sorted(wsup.index) if wsup is not None else []) if np.isfinite(rows[i]["price"])]
            hs = [1.0 - rows[i]["cap_lot"] / cA for i in sup]
            bw = beta_window(open_days, d)
            day["bench"].append({"date": day_s, "aum": a, "bb": sty["bb"], "zb": sty["zb"], "mb": sty["mb"], "size_mu": ctx["size_mu"], "size_sd": ctx["size_sd"],
                "mid_mu": ctx["mid_mu"], "mid_sd": ctx["mid_sd"], "beta_window_start": bw[0], "beta_window_end": bw[1], "beta_window_n": bw[2],
                "beta_window_source": "sse_calendar_last_L_BETA_sessions_le_day", "pool_n": len(ctx["pool"]), "n_prefilter": len(excl),
                "n_prefilter_sleeve2_only": len(s2o), "wb_share_prefiltered": wbe,
                "wb_beta_prefiltered": (sum(float(wb.get(i, 0.0)) * sty["b"][i] for i in excl) / wbe if wbe > 0 else None),
                "wb_size_prefiltered": (sum(float(wb.get(i, 0.0)) * sty["z"][i] for i in excl) / wbe if wbe > 0 else None),
                "caplot_cut_sum": float(sum(cA - rows[i]["cap_lot"] for i in pr)),
                "corr_cut_lnprice": corr(h, [math.log(rows[i]["price"]) for i in pr]), "corr_cut_size": corr(h, [sty["z"][i] for i in pr]),
                "corr_cut_beta": corr(h, [sty["b"][i] for i in pr]),
                "caplot_cut_sum_support": float(sum(cA - rows[i]["cap_lot"] for i in sup)),
                "corr_cut_lnprice_support": corr(hs, [math.log(rows[i]["price"]) for i in sup]), "corr_cut_size_support": corr(hs, [sty["z"][i] for i in sup]),
                "corr_cut_beta_support": corr(hs, [sty["b"][i] for i in sup]),
                "n_at_cap_lot_support": (int(sum(1 for i in sup if float(wsup[i]) >= rows[i]["cap_lot"] - 1e-9)) if wsup is not None else None),
                "sum_caplot_support": float(sum(rows[i]["cap_lot"] for i in sup))})
            v13 = v13_eq100.get((day_s, a))
            for i in excl:
                r = rows[i]
                day["pref"].append({"date": day_s, "aum": a, "instrument": i, "sw_l1": str(D["industry"].get(i, "_UNK")), "price": r["price"], "lot": r["lot"],
                    "lot_cost": r["lot_cost"], "T_sleeve1": cA * 1.0 * a, "T_sleeve2": cA * (1.0 - C.ETF_BALLAST_FRAC) * a,
                    "prefilter": r["prefilter"], "wb_i": float(wb.get(i, 0.0)), "beta": float(sty["b"][i]),
                    "size_z": (None if i in ctx["x_nan"] else float(sty["z"][i])), "midcap_m": (None if i in ctx["x_nan"] else float(sty["m"][i])),
                    "v13_eq100_weight": (float(v13.get(i, 0.0)) if v13 is not None else None)})
            # ---- decision -> held books. Coupling (v1.3 l.355 kept): adoption needs both sleeves hard-OK; failure -> both sleeves carry ----
            ktr = jdump([ktrace_entry(x) for x in res["attempts"]])
            if ad is not None:
                if ad is sel_att: stage = "ksel" if ad["strict_both"] else "ksel_cash_gt2"
                else: stage = "s3_strict" if ad["strict_both"] else "s3_hard_ok_cash_gt2"
                for sv, _ in SLEEVES: held[a][sv] = ad["sleeves"][sv]["book"]
                prev_w[a] = ad["w"]
            else:
                stage = "carry_solve_fail" if res["fail_stage"] == "solve" else "carry_lot_fail"
            resc_h = bool(ad is not None and trig == "hard")
            resc_c = bool(ad is not None and trig == "cash" and ad["strict_both"] and ksel is not None and ad["K"] > ksel)
            ksel_reasons = sorted({r_ for sv, _ in SLEEVES for r_ in sel_att["sleeves"][sv]["chk"]["reasons"]}) if sel_att is not None else []
            for sv, bf in SLEEVES:
                Bs = 1.0 - bf; hb = held[a][sv]
                ksl = sel_att["sleeves"][sv] if sel_att is not None else None
                if ad is not None:
                    x = ad["sleeves"][sv]; e = x["expo"]["final"]
                    st_ = "LOT_CASH_GT2" if x["chk"]["cash_gt2"] else "OK"; carry = None; sl = ad["slack"]
                    ow_s, ow_l, nl, clamp, nnp, nsv = ad["one_way_solver"], x["one_way_lot"], x["neff_lot"], x["li"]["clamp_count"], len(x["li"]["no_price"]), ad["neff_solver"]
                else:
                    e = book_exposures(hb if hb is not None else pd.Series(dtype=float), Bs, ctx)
                    st_ = "INFEASIBLE" if res["fail_stage"] == "solve" else "LOT_HARD_FAIL"
                    carry = "prior_holdings" if hb is not None else "all_cash"
                    sl = sel_att["slack"] if sel_att is not None else {"size_slack": None, "ind_slack": None}
                    ow_s = ow_l = nl = clamp = nnp = nsv = None
                    for basis in ("A", "B", "C"):
                        bb_ = e["bases"][basis]
                        day["carry"].append({"date": day_s, "aum": a, "sleeve": sv, "basis": basis, "size_act": fnum(bb_["size"]),
                            "midcap_act": fnum(bb_["midcap"]), "beta_act": fnum(bb_["beta"]), "ind_active_max": _maxabs(bb_["act"]),
                            "ind_abs_max": _max(bb_["ind"]), "cash": e["cash"], "carry_n_out_of_pool": e["n_out_of_pool"],
                            "carry_out_of_pool_names": e["out_of_pool_names"]})
                bA, bB, bC_ = e["bases"]["A"], e["bases"]["B"], e["bases"]["C"]
                drow = {"date": day_s, "window": win, "aum": a, "sleeve": sv, "status": st_, "fail_stage": res["fail_stage"], "carry": carry,
                    "K0": res["k0"], "K_sel": ksel, "k_final": (ad["K"] if ad is not None else None),
                    "delta_k": ((ad["K"] - ksel) if (ad is not None and ksel is not None) else None), "k_trace": ktr, "s3_used": res["s3_used"],
                    "s3_trigger": trig, "s3_rescued_from_hard": resc_h, "s3_rescued_from_cash": resc_c,
                    "lot_fail_reason": (",".join(ksel_reasons) if (ad is None and res["fail_stage"] == "lot") else ""),
                    "cash_gt2": bool(e["cash"] > CASH_MAX + 1e-9), "solve_infeasible_K": jdump(res["solve_infeasible_K"]),
                    "step1_status": res["step1"]["status"], "size_slack": sl["size_slack"], "ind_slack": sl["ind_slack"],
                    "n_names": e["n_names"], "cash": e["cash"], "beta_port": e["beta_port"], "neff_solver": nsv, "neff_lot": nl,
                    "one_way_solver": ow_s, "one_way_lot": ow_l,
                    "one_way_solver_ksel": (sel_att["one_way_solver"] if sel_att is not None else None),
                    "one_way_lot_ksel": (ksl["one_way_lot"] if ksl is not None else None),
                    "n_prefilter": len(excl), "n_prefilter_sleeve2_only": len(s2o), "n_no_price": nnp, "clamp_count": clamp,
                    "size_act_A": fnum(bA["size"]), "midcap_act_A": fnum(bA["midcap"]), "beta_act_A": fnum(bA["beta"]),
                    "size_act_B": fnum(bB["size"]), "midcap_act_B": fnum(bB["midcap"]), "beta_act_B": fnum(bB["beta"]),
                    "size_act_C": fnum(bC_["size"]), "midcap_act_C": fnum(bC_["midcap"]), "beta_act_C": fnum(bC_["beta"]),
                    "ind_active_max_C": _maxabs(bC_["act"]), "ind_abs_max_C": _max(bC_["ind"]),
                    "carry_n_out_of_pool": (e["n_out_of_pool"] if ad is None else None),
                    "carry_out_of_pool_names": (e["out_of_pool_names"] if ad is None else None),
                    "turn_solver_gt40": (bool(ow_s > TURN_MONITOR) if ow_s is not None else None),
                    "turn_lot_gt40": (bool(ow_l > TURN_MONITOR) if ow_l is not None else None)}
                day["disc"].append(drow)
                if trig == "cash":  # LOTFIX §4.1(3): cash-only up-K days, with the K_sel attempt as control
                    s3_cash_rows.append({"date": day_s, "aum": a, "sleeve": sv, "K_sel": ksel, "k_final": drow["k_final"], "delta_k": drow["delta_k"],
                        "rescued": resc_c, "one_way_solver": ow_s, "one_way_solver_ksel": drow["one_way_solver_ksel"], "one_way_lot": ow_l,
                        "one_way_lot_ksel": drow["one_way_lot_ksel"]})
                if snap_on:  # AMEND-1: write-only. Nothing downstream reads day["snap"] except the snapshot writer.
                    day["snap"] += build_pool_snapshot(day_s, a, sv, Bs, D, ctx, hb, (ad["w"] if ad is not None else None), stage, ksel,
                                                       (ad["K"] if ad is not None else None), e["beta_port"])
            rec["tiers"][a] = {"status": stage, "K_sel": ksel, "k_final": (ad["K"] if ad is not None else None), "fail_stage": res["fail_stage"],
                               "books": _books_rec(held[a]),
                               "solver_w": (sorted((str(i), float(v)) for i, v in prev_w[a].items()) if prev_w[a] is not None else None)}
            del ctx, res
        # ---- write this day (append; deterministic order) ----
        W.parquet("core_v1_4_attempt_weights.parquet", ATT_SCHEMA, day["att"])
        W.csv("core_v1_4_style_components.csv", day["style"], STYLE_COLS)
        W.csv("core_v1_4_industry_detail.csv", day["ind"], IND_COLS)
        W.csv("core_v1_4_beta15_shadow.csv", day["b15"], B15_COLS)
        W.csv("core_v1_4_daily_bench.csv", day["bench"], BENCH_COLS)
        W.csv("core_v1_4_carry_exposure.csv", day["carry"], CARRY_COLS)
        W.csv("core_v1_4_prefilter_names.csv", day["pref"], PREF_COLS)
        W.jsonl(TRACE_FILE, day["trace"])
        if snap_on:
            W.parquet("core_v1_4_pool_snapshot.parquet", SNAP_SCHEMA, day["snap"]); snap_rows_n += len(day["snap"])
        disc_all += day["disc"]
        with open(ck_dir / f"{d:%Y%m%d}.pkl", "wb") as f: pickle.dump(rec, f, protocol=4)
        rss = C.rss_mb()
        runtime_days.append({"day": day_s, "sec": round(time.time() - t0, 1), "rss_mb": round(rss)})
        print(jdump({"day": day_s, **{str(k): v.get("status") for k, v in rec["tiers"].items()}}), flush=True)
        del D, day, px; gc.collect()
        if rss > RSS_LIMIT_MB: raise MemoryError(f"RSS {rss:.0f} MB > {RSS_LIMIT_MB:.0f} MB budget (AMEND-1 §2)")
    W.close()
    disc = pd.DataFrame(disc_all, columns=DISC_COLS)
    if not set(disc.status) <= set(STATUSES): raise RuntimeError(f"unexpected statuses: {sorted(set(disc.status))}")
    disc.to_csv(out_dir / "core_v1_4_disclosure.csv", index=False)
    pd.DataFrame(s3_cash_rows, columns=S3CASH_COLS).to_csv(out_dir / "core_v1_4_s3_cash_days.csv", index=False)
    paths = write_daily_weights(ck_dir, rd, sess, out_dir)
    report = post_run_disclosures(disc)
    (out_dir / "core_v1_4_disclosure_counts.json").write_text(jdump(report, indent=1))
    return {"paths": paths, "report": report, "v13_inputs": v13_shas, "runtime_days": runtime_days, "snap_rows": snap_rows_n, "n_rebal": len(rd)}


def write_daily_weights(ck_dir, rd, sess, out_dir):
    """Daily expansion of held targets (same schema as v1.3, mechanism_tag v1_4). Relative paths only (bit-equality across dirs)."""
    recs = {d: pickle.load(open(ck_dir / f"{d:%Y%m%d}.pkl", "rb")) for d in rd}
    rdset = {f"{x:%Y-%m-%d}" for x in rd}; paths = {}
    for a, tag in AUMS.items():
        for sv, _ in SLEEVES:
            rows = []; cur = None
            for s_ in sess:
                if s_ in recs: cur = recs[s_]["tiers"][a]["books"][sv]
                if cur is None: continue
                ss = f"{s_:%Y-%m-%d}"
                rows += [(ss, i, float(wt)) for i, wt in cur if wt > 0]
            df = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
            df["date"] = df["session"]; df["target_weight"] = df["weight"]
            df["instrument_id"] = df["instrument"].map(_code)
            df["universe_id"] = "HI_LIQ_V1"; df["mechanism_tag"] = "optimizer_core_frozen_v1_4"; df["who_pays_zh"] = "N/A"
            df["aum"] = a; df["sleeve"] = sv; df["is_rebalance_day"] = df["session"].isin(rdset)
            df["window"] = np.where(df["session"] >= X2[0], "X2", "SEALED")
            name = f"core_{sv}_{tag}.parquet"; df.to_parquet(out_dir / name, index=False); paths[f"{sv}_{tag}"] = name
    return paths


# ---------------------------------------------------------------- stop rule (frozen 41f29825) + §4.4 / §8 / M3 disclosures
def _runs(flags):
    """flags: list of bool -> list of (start_idx, end_idx) of consecutive True runs."""
    out = []; s = None
    for k, f in enumerate(flags):
        if f and s is None: s = k
        if not f and s is not None: out.append((s, k - 1)); s = None
    if s is not None: out.append((s, len(flags) - 1))
    return out


def _groups(df):
    return sorted(df.groupby(["aum", "sleeve"]), key=lambda t: (int(t[0][0]), str(t[0][1])))


def stop_rule_eval(disc, x2_only):
    """Evaluate-only for this research run: reports where the frozen rule WOULD stop; never alters any decision or target."""
    res = {}
    d0 = disc if not x2_only else disc[disc["date"] >= X2[0]]
    for (a, sv), g in _groups(d0):
        g = g.sort_values("date")
        nod = (g["status"] == "NO_DATA_CARRY").tolist(); dates_all = g["date"].tolist()
        seq = g[g["status"] != "NO_DATA_CARRY"]                      # M5: no-data days skipped, do not reset the count
        dates = seq["date"].tolist(); st = seq["status"].tolist()
        fail = [s in FAIL_STATUSES for s in st]                         # §2: INFEASIBLE or LOT_HARD_FAIL; cash>2% is not a failure
        cashf = [s == "LOT_CASH_GT2" for s in st]
        fr = _runs(fail)
        k3 = next((dates[s + STOP_K - 1] for s, e in fr if e - s + 1 >= STOP_K), None)
        months, mtrig = {}, None                                        # §2 ②: ≥2 failure days in one calendar month (v1.4+)
        for dt, f in zip(dates, fail):
            if f:
                m = dt[:7]; months[m] = months.get(m, 0) + 1
                if months[m] >= 2 and mtrig is None: mtrig = dt
        roll6 = [dates[k] for k in range(len(dates)) if sum(fail[max(0, k - 5): k + 1]) >= 3]   # M6 disclosure-only control
        nodata_runs = [(dates_all[s], dates_all[e], e - s + 1) for s, e in _runs(nod) if e - s + 1 >= 2]  # M5: report, no stop
        longest = max(fr, key=lambda t: (t[1] - t[0], -t[0]), default=None)
        cr = _runs(cashf); fcr = _runs([f or c for f, c in zip(fail, cashf)])
        reasons = {}
        for r_ in seq.loc[seq["status"] == "LOT_HARD_FAIL", "lot_fail_reason"].fillna(""):
            for x in [t for t in str(r_).split(",") if t]: reasons[x] = reasons.get(x, 0) + 1
        trig = min([t for t in (k3, mtrig) if t is not None], default=None)
        res[f"{a}|{sv}"] = {"n_days": len(dates), "n_fail": int(sum(fail)), "n_fail_solve": int(sum(1 for s in st if s == "INFEASIBLE")),
            "n_fail_lot": int(sum(1 for s in st if s == "LOT_HARD_FAIL")), "carry_days": int(sum(fail)),
            "longest_fail_run": ({"start": dates[longest[0]], "end": dates[longest[1]], "len": longest[1] - longest[0] + 1} if longest else None),
            "k3_trigger_date": k3, "monthly2_trigger_date": mtrig, "trigger_date": trig, "triggered": trig is not None,
            "rolling6_ge3_dates_disclosure_only": roll6, "nodata_runs_ge2_report": nodata_runs, "lot_fail_reasons": reasons,
            "cash_gt2_days": int(sum(cashf)), "cash_gt2_longest_run": max([e - s + 1 for s, e in cr], default=0),
            "cash_gt2_max": (fnum(seq.loc[seq["status"] == "LOT_CASH_GT2", "cash"].max()) if any(cashf) else None),
            "fail_or_cash_longest_run": max([e - s + 1 for s, e in fcr], default=0)}
    tiers = {}
    for a in AUMS:   # M4: any sleeve of a tier triggers -> the whole tier stops
        ts = sorted(res[k]["trigger_date"] for k in res if k.startswith(f"{a}|") and res[k]["trigger_date"])
        tiers[str(a)] = {"tier_stop_date_M4": ts[0] if ts else None}
    return {"per_sleeve": res, "per_tier_M4": tiers, "core_all_stop": all(tiers[t]["tier_stop_date_M4"] for t in tiers),
            "mode": "evaluate_only_no_decision_change", "x2_only": x2_only, "k": STOP_K}


def rescue_positions(disc):
    """LOTFIX §4.4: position of each S3-rescued day inside the run that would exist without rescue; counterfactual k=3."""
    out = {}
    for (a, sv), g in _groups(disc):
        seq = g[g["status"] != "NO_DATA_CARRY"].sort_values("date")
        dates = seq["date"].tolist(); st = seq["status"].tolist()
        rh = seq["s3_rescued_from_hard"].fillna(False).astype(bool).tolist(); rc = seq["s3_rescued_from_cash"].fillna(False).astype(bool).tolist()
        fail = [s in FAIL_STATUSES for s in st]; cash = [s == "LOT_CASH_GT2" for s in st]
        hyp = [f or r for f, r in zip(fail, rh)]
        hyp2 = [f or c or r for f, c, r in zip(fail, cash, rc)]

        def pos(flags, k):
            for s, e in _runs(flags):
                if s <= k <= e: return "isolated" if s == e else ("head" if k == s else ("tail" if k == e else "mid"))
            return None
        out[f"{a}|{sv}"] = {
            "s3_rescued_from_hard": [{"date": dates[k], "position": pos(hyp, k)} for k in range(len(dates)) if rh[k]],
            "counterfactual_k3_trigger_without_rescue": next((dates[s + STOP_K - 1] for s, e in _runs(hyp) if e - s + 1 >= STOP_K), None),
            "s3_rescued_from_cash": [{"date": dates[k], "position_in_fail_or_cash_run": pos(hyp2, k)} for k in range(len(dates)) if rc[k]],
            "n_rescued_hard": int(sum(rh)), "n_rescued_cash": int(sum(rc))}
    return out


def _dist(s):
    s = pd.Series(s).dropna().astype(float)
    if s.empty: return None
    return {"n": int(s.size), "mean": float(s.mean()), "p10": float(s.quantile(0.1)), "median": float(s.median()), "p90": float(s.quantile(0.9)),
            "min": float(s.min()), "max": float(s.max())}


def post_run_disclosures(disc):
    rep = {"stop_rule_full_sample": stop_rule_eval(disc, x2_only=False), "stop_rule_x2": stop_rule_eval(disc, x2_only=True),
           "s3_rescue": rescue_positions(disc), "k_neff": {}, "turnover_gt40": {}, "s8": {}}
    for (a, sv), g in _groups(disc):
        k = f"{a}|{sv}"; ok = g[g["status"] != "NO_DATA_CARRY"]
        rep["k_neff"][k] = {"K_sel": {str(int(x)): int(n) for x, n in ok["K_sel"].dropna().astype(int).value_counts().sort_index().items()},
            "k_final": {str(int(x)): int(n) for x, n in ok["k_final"].dropna().astype(int).value_counts().sort_index().items()},
            "neff_solver": _dist(ok["neff_solver"]), "neff_lot": _dist(ok["neff_lot"]),
            "s3_used_days": int(ok["s3_used"].fillna(False).astype(bool).sum()),
            "s3_trigger_counts": {str(t): int(n) for t, n in ok["s3_trigger"].fillna("none").value_counts().sort_index().items()},
            "fail_stage_counts": {str(t): int(n) for t, n in ok["fail_stage"].dropna().value_counts().sort_index().items()}}
        tv = {}
        for grp, gg in ok.groupby(ok["s3_used"].fillna(False).astype(bool)):
            tv[f"s3_used={bool(grp)}"] = {"solver_gt40": int(gg["turn_solver_gt40"].fillna(False).astype(bool).sum()),
                                         "lot_gt40": int(gg["turn_lot_gt40"].fillna(False).astype(bool).sum()), "n": int(len(gg))}
        rep["turnover_gt40"][k] = tv   # LOTFIX §6.2: monitor only
    # §8 (frozen 00:51 ET): X2, basis C strict (status OK, coupled); 100万 any sleeve <80% (<24/29) or k=3 on X2 -> still infeasible
    x2 = disc[(disc["date"] >= X2[0]) & (disc["status"] != "NO_DATA_CARRY")]
    s8 = {}
    for (a, sv), g in _groups(x2):
        n = int(len(g)); ns = int((g["status"] == "OK").sum())
        s8[f"{a}|{sv}"] = {"n_days": n, "n_strict": ns, "strict_rate": (ns / n if n else None), "below_80": (ns < 0.8 * n) if n else None,
                           "n_days_equals_29": n == 29}
    stop_x2 = rep["stop_rule_x2"]["per_sleeve"]
    v100 = any(bool(s8.get(f"1000000|{sv}", {}).get("below_80")) for sv, _ in SLEEVES) or \
        any(bool(stop_x2.get(f"1000000|{sv}", {}).get("k3_trigger_date")) for sv, _ in SLEEVES)
    v60_below = any(bool(s8.get(f"600000|{sv}", {}).get("below_80")) for sv, _ in SLEEVES)
    rep["s8"] = {"per_sleeve": s8, "verdict_100w_still_infeasible": bool(v100), "flag_60w_also_below_80": bool(v60_below),
                 "note_zh": ("60万 在口径 C 下也低于 80%：不可行不能只归因于 100万 的 5% 上限（LOTFIX §8 Beta L1）" if v60_below else None),
                 "v1_3_C_vs_C_comparison": "not computed by this runner (LOTFIX §8 Beta L6; needs a separately authorized step)"}
    return rep


# ---------------------------------------------------------------- unified exception handling (Arch P2-r2-1)
def write_void(out_dir, exc, tb):
    lines = ["# VOID — Core v1.4 run did not produce summary.json", "", f"- written: {et_now()} (automatic, runner exception handler)",
             f"- exception: {type(exc).__name__}: {exc}",
             "- rule (Arch P2-r2-1): any exit without summary.json voids the whole run; no retry; Arch re-review + new .ok required.",
             "- files present at void time (sha256 only; contents not interpreted):", ""]
    for p in sorted(out_dir.rglob("*")):
        if p.is_file() and p.name != "VOID.md":
            lines.append(f"  - {p.relative_to(out_dir)}  {sha_file(p)}")
    lines += ["", "```", tb, "```", ""]
    (out_dir / "VOID.md").write_text("\n".join(lines), encoding="utf-8")


def output_shas(out_dir):
    out = {}
    for p in sorted(out_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(out_dir))
            if rel in EXCLUDED_FROM_EQUIV or rel == "summary.json" or rel.endswith(".log") or rel.endswith(".tmp"): continue
            out[rel] = sha_file(p)
    return out


def _sig(signum, frame):
    raise RunAborted(f"signal {signum}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Core v1.4 LOTFIX runner (weights only; Arch .ok required)")
    ap.add_argument("--mode", choices=["full", "equiv"], default="full")
    ap.add_argument("--pool-snapshot", choices=["on", "off"], default="on", help="AMEND-1 snapshot writer switch (write-only)")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--auth-sha256", required=True, help="sha256 of ARCH_RUN_AUTH_v1_4.ok as communicated by Arch")
    args = ap.parse_args(argv)
    snap_on = args.pool_snapshot == "on"
    out_dir = Path(args.out_dir) if args.out_dir else expected_out_dir(args.mode, snap_on)
    if not out_dir.is_absolute(): out_dir = ROOT / out_dir
    pf = preflight(args.mode, out_dir, snap_on, args.auth_sha256)   # SystemExit here = refused before anything is written
    out_dir = pf["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(s, _sig)
    t_start = time.time()
    runtime = {"started_et": et_now(), "mode": args.mode, "pool_snapshot": snap_on, "out_dir": str(out_dir), "argv": sys.argv,
               "python": sys.version, "auth_file": str(AUTH_PATH.relative_to(ROOT)), "auth_sha256": pf["auth_sha"]}
    rc = 0
    try:
        r = run_v14(out_dir, snap_on, pf["lr"], pf["lt"], pf["code_sha"])
        runtime.update({"days": r["runtime_days"], "snapshot_rows": r["snap_rows"]})
        if snap_on:
            sp = out_dir / "core_v1_4_pool_snapshot.parquet"
            (out_dir / "core_v1_4_pool_snapshot_manifest.json").write_text(jdump({"file": sp.name, "sha256": (sha_file(sp) if sp.exists() else None),
                "rows": r["snap_rows"], "amend_sha256": PINNED_DOCS["amend_sha256"][1],
                "checks": ["A1 Σwb_i=1 and Σwb_i·β_i=bb", "A3 Σq_final=1 and Σq_final·β=beta_port (1e-6)", "coverage q_final>0 ⊆ selected"]}, indent=1))
        summary = {"version": "FROZEN_v1.4_LOTFIX", "live": False, "promotion": False, "paper_touched": False, "returns_computed": False,
            "x2_evidence_status": "diagnostic reproduction under basis C only (LOTFIX P2-1); not evidence for Core vs B",
            "specs": {k: v[1] for k, v in PINNED_DOCS.items()}, "code_sha256": pf["code_sha"], "mask_sha256": pf["mask_sha"],
            "arch_run_auth": {"file": str(AUTH_PATH.relative_to(ROOT)), "sha256": pf["auth_sha"], "fields": pf["auth"]},
            "lambda_risk": pf["lr"], "lambda_turn": {str(k): v for k, v in pf["lt"].items()}, "cadence": C.CADENCE, "window": [START, END],
            "x2": list(X2), "n_rebal": r["n_rebal"], "paths": r["paths"], "v1_3_inputs_read_only": r["v13_inputs"],
            "constants": {"EPS_LOT": EPS_LOT, "STRICT_CAP_REL": STRICT_CAP_REL, "CASH_MAX": CASH_MAX, "K_MAX": K_MAX, "TOL": TOL, "STOP_K": STOP_K},
            "s8": r["report"]["s8"], "stop_rule_x2_M4": r["report"]["stop_rule_x2"]["per_tier_M4"],
            "outputs_sha256": output_shas(out_dir), "excluded_from_equiv": list(EXCLUDED_FROM_EQUIV)}
        tmp = out_dir / "summary.json.tmp"; tmp.write_text(jdump(summary, indent=1)); os.replace(tmp, out_dir / "summary.json")
        print("V1_4_DONE summary.json", sha_file(out_dir / "summary.json"), flush=True)
    except BaseException as e:  # noqa: BLE001 — unified handler: no summary -> VOID (Arch P2-r2-1)
        rc = 1
        if not (out_dir / "summary.json").exists():
            try: write_void(out_dir, e, traceback.format_exc())
            except BaseException as e2: print(f"VOID write failed: {e2!r}", file=sys.stderr)
        print(f"V1_4_VOID {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    finally:
        runtime.update({"ended_et": et_now(), "elapsed_sec": round(time.time() - t_start, 1), "peak_rss_mb": round(C.rss_mb()), "rc": rc,
                        "summary_present": (out_dir / "summary.json").exists()})
        try: (out_dir / "run_runtime.json").write_text(jdump(runtime, indent=1))
        except BaseException: pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
