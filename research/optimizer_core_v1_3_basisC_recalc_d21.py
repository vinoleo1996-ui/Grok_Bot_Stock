#!/usr/bin/env python3
"""D21 (Arch review db781708 D21 / E-3; LOTFIX §8 Beta L6; CLARIFY-1 d075a2a6 §4; CLARIFY-2): v1.3 feasibility RE-JUDGED UNDER
BASIS C, the §8 baseline for the C-vs-C comparison with v1.4. Weights/feasibility labels only; NO returns. live=false, promotion=false.

What it does (read-only w.r.t. every v1.3 / v1.4 product; writes only its own out dir + one lock file):
  1. MAIN RESULT = §8 BASELINE (CLARIFY-2): replays the v1.3 decision path exactly as research/optimizer_core_x2_run.py b6238254
     lines 312–366 (= canonical 29b38cf8 logic): prepare_day -> v1.3 ① lot-cost exclusion -> V.solve_v11 (POOL_STD=IND_POOL=True)
     -> V.lot_round_greedy per sleeve -> v1.3 adoption rule (basis-A lot_flag, two-sleeve coupling). Holdings / w0 chain follow
     the v1.3 (basis A) decisions unchanged; ONLY the feasibility label is re-judged under basis C.
  2. Basis-C judge: the v1.4 runner's own book_exposures + hard_eval (D15 TOL=1e-6, the v1.3 day's slack), coupled: a sleeve is
     strict-C on a day iff the solve succeeded, BOTH sleeves pass the basis-C HARD check and that sleeve's cash <= 2%.
  3. §8 with the identical v1.4 code (R.post_run_disclosures: CLARIFY-1 both-sleeves-same-day + CLARIFY-2 no-data / absolute 24);
     plus the reproduced basis-A labels for an A-vs-A control.
  4. SECOND DISCLOSURE COLUMN (CLARIFY-2): a separate replay whose DECISIONS also follow basis C (adopt iff both sleeves pass the
     basis-C hard check; otherwise carry) -> a different w0 chain, i.e. a counterfactual path, NOT v1.3. Disclosure only: never
     used for §8 or any verdict.
  5. Reproduction check vs the canonical v1.3 products and the citability rule written into code (CLARIFY-2; Arch r2 §7 item 6):
     citable = "VALID" only if (a) every status label equals core_v1_3_disclosure.csv row by row (0 mismatches, same key set),
     (b) max |weight diff| <= 1e-6 on every compared rebalance day, (c) identical holding sets and identical lot counts;
     otherwise "VALID_WITH_DISCLOSURE" with "解释前不得引用" (must not be cited until Arch explains every difference).
     The check itself is disclosure only and never a VOID condition.
r4 (Arch rulings 1/4; CLARIFY-2 85e843cd pinned): lot counts compared against the v1.3 ckpt lot books (_ckpt_v1_3_poolind/*.pkl;
这是 pickle，只读仓库内已钩文件 - combined sha pinned by .ok key v13_ckpt_combined_sha256, bytes verified before unpickling); the ckpt
stores weights not counts, so counts are back-computed exactly (bit-for-bit, no tolerance); §8 integrity_warning per R.
It never imports optimizer_core_x2_run.py (that module creates directories at import) and never modifies it.

Gate: output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_D21_v1_3C.ok (Arch writes it; Strategy never creates it) + --auth-sha256.
Same field / sha / interpreter / determinism-env / lock / whitelist / expires_et rules as v1.4 (R). Unified exception handling:
no summary -> VOID.md. Runtime ≈ 2 v1.3 runs (two replays).
Launch (only if Leo continues Core; D21 runs BEFORE v1.4, serial; CLARIFY-1 §4):
  cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup \
    /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_v1_3_basisC_recalc_d21.py --auth-sha256 <sha of .ok> \
    > output/strategy_optimizer/core_x2/d21_run.log 2>&1 &
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, pickle, re, signal, sys, time, traceback   # pickle: v1.3 ckpts only (sha-verified bytes; r4)
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_core_x2_run_v1_4 as R      # v1.4 runner: basis-C judge, §8 code, gate helpers (no side effects at import)
C, V = R.C, R.V

VERSION = "d21_v1_3_basisC"
D21_REL = "research/optimizer_core_v1_3_basisC_recalc_d21.py"
CODE_FILES_D21 = (D21_REL, R.RUNNER_REL, "research/optimizer_core_v1_1.py", "research/optimizer_lambda_calib_sealed.py")
OUT_REL = R.CORE_REL + "/v1_3_basisC_d21"                   # own out dir; must be absent or empty; never v1_4*/ or v1.3 products
OUT_DIR = ROOT / OUT_REL
AUTH_PATH = R.CORE / "ARCH_RUN_AUTH_D21_v1_3C.ok"
LOCK = R.CORE / ".d21_v1_3_basisC_run.lock"
# r3: stop rule pinned too (Arch P3-7: D21 evaluates it via R.post_run_disclosures); CLARIFY-2 via R.check_clarify2.
PINNED_DOCS = {**{k: R.PINNED_DOCS[k] for k in ("lotfix_sha256", "stoprule_sha256", "clarify_sha256")},
               "clarify2_sha256": (R.CLARIFY2_REL, R.CLARIFY2_SHA256)}   # r4: CLARIFY-2 85e843cd pinned here too
# r4 (Arch ruling 4): v1.3 checkpoint pickles = the canonical lot books (rec["sleeves"][aum][sleeve]["w"], written by 29b38cf8
# l.276/283/290). THIS IS PICKLE: only these repo files are ever unpickled, and only from bytes whose per-file sha256 rolls up to the
# .ok-pinned combined (sorted "name=sha\n" lines) - the bytes are hashed and unpickled from the same in-memory buffer (no re-read).
V13_CKPT_REL = R.CORE_REL + "/_ckpt_v1_3_poolind"
V13_CKPT_KEY = "v13_ckpt_combined_sha256"
V13_PRODUCTS = {   # canonical v1.3 products (29b38cf8 run 2026-10-18 00:20–00:27 ET): read-only, used only for the reproduction check
    "v13_disclosure_sha256": R.CORE_REL + "/core_v1_3_disclosure.csv", **R.V13_WEIGHTS}
INPUT_KEYS_D21 = tuple(dict.fromkeys(tuple(R.PINNED_INPUTS) + tuple(V13_PRODUCTS) + (V13_CKPT_KEY,)))   # data+closure+weights+disclosure+ckpt
AUTH_REQUIRED_D21 = (("format", "version", "signed_by", "signed_et", "expires_et", "allow_full", "allow_smoke", "live", "promotion",
                      "python_exe", "out_dir", "runner_sha256", "combined_sha256") + tuple(PINNED_DOCS) + INPUT_KEYS_D21)
AUTH_ALLOWED_D21 = frozenset(AUTH_REQUIRED_D21)              # r3 (Arch P2-3): whitelist
SHA_KEYS_D21 = ("runner_sha256", "combined_sha256") + tuple(PINNED_DOCS) + INPUT_KEYS_D21
EXCLUDED = ("run_runtime.json",)
CITE_WEIGHT_TOL = 1e-6                                       # CLARIFY-2 / Arch r2 §7 item 6
STATUS_COLS = ["date", "window", "aum", "sleeve", "status_A_repro", "status_C_coupled", "hard_C_this", "hard_C_both", "cash", "cash_gt2",
               "reasons_C", "size_slack", "ind_slack", "n_names", "n_excluded_v13", "size_act_C", "midcap_act_C", "beta_act_C",
               "ind_active_max_C", "ind_abs_max_C", "beta_port", "stage_A", "lot_flag_A"]


class RunAborted(BaseException):
    pass


def code_sha256_d21():
    per = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE_FILES_D21}
    return {"combined": hashlib.sha256("".join(f"{f}={per[f]}\n" for f in CODE_FILES_D21).encode()).hexdigest(), "files": per}


def parse_run_auth_d21(path, now=None):
    kv = R.parse_ok_strict(path, AUTH_REQUIRED_D21, AUTH_ALLOWED_D21, "d21")   # r3: whitelist, malformed/unknown refused, LF, no BOM
    if kv["format"] != "quantlab_run_auth_v1": raise SystemExit(f"d21 blocked: format={kv['format']!r}")
    if kv["version"] != VERSION: raise SystemExit(f"d21 blocked: version={kv['version']!r}, expected {VERSION}")
    if kv["signed_by"] != "arch": raise SystemExit("d21 blocked: signed_by must be arch")
    R.check_auth_times(kv, "d21", now)                                           # r3: expires_et required, not expired
    for k in ("allow_full", "allow_smoke"):
        if kv[k] not in ("true", "false"): raise SystemExit(f"d21 blocked: {k}={kv[k]!r}, must be exactly true or false")
        kv[k] = kv[k] == "true"
    for k in ("live", "promotion"):
        if kv[k] != "false": raise SystemExit(f"d21 blocked: {k}={kv[k]!r}, must be exactly false")
        kv[k] = False
    for k in SHA_KEYS_D21:
        if not re.fullmatch(r"[0-9a-f]{64}", kv[k]): raise SystemExit(f"d21 blocked: {k} is not a 64-hex sha256")
    if not os.path.isabs(kv["python_exe"]): raise SystemExit("d21 blocked: python_exe must be an absolute path")
    return kv


def v13_product_shas():
    return {k: R.sha_file(ROOT / rel) for k, rel in V13_PRODUCTS.items()}


# ---------------------------------------------------------------- r4 (Arch ruling 4): v1.3 checkpoint pickles (canonical lot books)
# 这是 pickle，只读仓库内已钩文件：only output/strategy_optimizer/core_x2/_ckpt_v1_3_poolind/*.pkl, only after the sha256 of the very
# bytes being unpickled has been checked against the .ok-pinned combined sha (v13_ckpt_combined_sha256). Never any other pickle.
# Content per writer source 29b38cf8 l.234/276/283/290 (same structure as b6238254 l.344–372):
#   rec = {"day", "w": {aum: solver weights}, "sleeves": {aum: {sleeve: {"w": lot book Series, lot_flag, style_excess, cash, n, no_price,
#          exposure drifts}}} (adopted days only), "log", ...}. The lot book "w" = q*P/aum (optimizer_core_v1_1 b500c21b l.128/197);
#   NO share/lot counts are stored (lot_round_greedy info keys: lot_flag, style_excess, cash, n, no_price - l.210) -> lots are
#   back-computed by exact_lots() and must reproduce the book weight bit-for-bit (no tolerance).
def ckpt_dir():
    return ROOT / V13_CKPT_REL


def ckpt_names():
    d = ckpt_dir()
    if not d.is_dir() or d.is_symlink(): raise SystemExit(f"d21 blocked: v1.3 ckpt dir missing or a symlink: {V13_CKPT_REL}")
    names = sorted(p.name for p in d.iterdir())
    bad = [n for n in names if not re.fullmatch(r"\d{8}\.pkl", n) or not (d / n).is_file() or (d / n).is_symlink()]
    if bad or not names: raise SystemExit(f"d21 blocked: v1.3 ckpt dir has unexpected entries {bad[:5]} (or is empty)")
    return names


def ckpt_combined(per):
    """sha256 over sorted 'name=sha256\\n' lines (same rule as the code combined sha)."""
    return hashlib.sha256("".join(f"{n}={per[n]}\n" for n in sorted(per)).encode()).hexdigest()


def ckpt_shas():
    """Hash only (no unpickling): used by preflight and the end-of-run recheck."""
    names = ckpt_names()
    per = {n: R.sha_file(ckpt_dir() / n) for n in names}
    return {"combined": ckpt_combined(per), "n_files": len(per), "files": per}


def load_v13_ckpts(pin):
    """这是 pickle，只读仓库内已钩文件. Read every file's bytes once, hash those bytes, compare the combined sha with the .ok pin,
    and only then unpickle from the same in-memory buffers. Any mismatch -> RuntimeError (VOID); nothing is unpickled."""
    names = ckpt_names(); raw = {}
    for n in names:
        with open(ckpt_dir() / n, "rb") as f: raw[n] = f.read()
    per = {n: hashlib.sha256(b).hexdigest() for n, b in raw.items()}
    got = ckpt_combined(per)
    if got != pin: raise RuntimeError(f"v1.3 ckpt combined sha256 {got} != authorized {pin}; nothing unpickled")
    recs = {f"{n[0:4]}-{n[4:6]}-{n[6:8]}": pickle.loads(raw[n]) for n in names}   # verified bytes only
    del raw
    return recs, {"combined": got, "n_files": len(per), "files": per}


def preflight(expected_auth_sha):
    """All gate checks; writes nothing. SystemExit = refused before anything is written."""
    for k, (rel, pin) in PINNED_DOCS.items():
        if R.sha_file(ROOT / rel) != pin: raise SystemExit(f"d21 blocked: {rel} sha256 != pinned {pin}")
    mask_sha = C.file_sha256(C.MASK_PATH)
    if mask_sha != C.MASK_SHA_EXPECT: raise SystemExit(f"d21 blocked: HI_LIQ mask sha {mask_sha} != {C.MASK_SHA_EXPECT}")
    R.check_input_paths(); R.check_determinism_env()
    for k, rel in V13_PRODUCTS.items():
        if not (ROOT / rel).is_file(): raise SystemExit(f"d21 blocked: v1.3 product {k} missing: {rel}")
    lr, lt = R.frozen_lambdas()
    cs = code_sha256_d21()
    kv = parse_run_auth_d21(AUTH_PATH)
    auth_sha = R.sha_file(AUTH_PATH)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_auth_sha or ""): raise SystemExit("d21 blocked: --auth-sha256 must be 64-hex")
    if auth_sha != expected_auth_sha: raise SystemExit(f"d21 blocked: .ok sha256 {auth_sha} != --auth-sha256 {expected_auth_sha}")
    if kv["allow_smoke"]: raise SystemExit("d21 blocked: no smoke mode; allow_smoke must be false")
    if not kv["allow_full"]: raise SystemExit("d21 blocked: allow_full is not true")
    if kv["out_dir"] != OUT_REL: raise SystemExit(f"d21 blocked: .ok out_dir={kv['out_dir']!r} != {OUT_REL!r}")
    if kv["runner_sha256"] != cs["files"][D21_REL]: raise SystemExit("d21 blocked: runner sha256 != authorized")
    if kv["combined_sha256"] != cs["combined"]: raise SystemExit(f"d21 blocked: combined sha256 {cs['combined']} != authorized")
    for k, (rel, pin) in PINNED_DOCS.items():
        if kv[k] != pin: raise SystemExit(f"d21 blocked: {k} authorized {kv[k]} != pinned {pin}")
    R.check_clarify2(kv, "d21")
    inputs = R.check_inputs(kv)                          # data + nontextbook closure + v1.3 weights (r3 P2-2)
    v13 = v13_product_shas()
    bad = sorted(k for k in V13_PRODUCTS if kv[k] != v13[k])
    if bad: raise SystemExit(f"d21 blocked: v1.3 product sha mismatch {bad}")
    ck = ckpt_shas()                                     # r4: hash only, nothing unpickled before the run
    if ck["combined"] != kv[V13_CKPT_KEY]:
        raise SystemExit(f"d21 blocked: v1.3 ckpt combined sha256 {ck['combined']} != authorized {kv[V13_CKPT_KEY]}")
    R.check_interpreter(kv)                              # r3: pyvenv.cfg required, PYTHON* env, packages under prefix
    od = OUT_DIR.resolve()
    if (ROOT / "output/strategy_hiliq").resolve() in od.parents: raise SystemExit("d21 blocked: out dir under output/strategy_hiliq")
    if od.exists() and any(od.iterdir()): raise SystemExit(f"d21 blocked: out dir {od} not empty (no resume / no retry)")
    if LOCK.exists(): raise SystemExit(f"d21 blocked: lock {LOCK} exists (Arch must archive it)")
    return {"lr": lr, "lt": lt, "code_sha": cs, "auth": kv, "auth_sha": auth_sha, "mask_sha": mask_sha, "inputs": inputs,
            "v13_products": v13, "v13_ckpt": ck, "interp": R.interpreter_info(), "out_dir": od, "code_files": list(CODE_FILES_D21)}


# ---------------------------------------------------------------- v1.3 replay (logic of b6238254 l.312–366) + basis-C judge
def _px(D, d):
    nm = sorted(set(D["alpha"].index))
    b = C.load_daily_basic_window(nm, d - pd.Timedelta(days=10), d)
    b["trade_date"] = pd.to_datetime(b["trade_date"])
    return b.sort_values("trade_date").groupby("ts_code")["close"].last()       # same call as v1.3 (default sort kind)


def judge_C(sl, info, D, a):
    """Basis-C HARD check of the v1.3 lot books with the v1.4 code (book_exposures + hard_eval, TOL=1e-6, v1.3 slack)."""
    ss, isl = info["slack"]["size_slack"], info["slack"]["ind_slack"]
    ctx = {"sty": V.style_ctx(D, ss, isl), "ind_map": D["industry"], "wbg": V.pool_ind_bench(D), "pool_set": set(D["alpha"].index)}
    out = {}
    for sv, bf in R.SLEEVES:
        res = R.book_exposures(sl[sv]["w"], 1.0 - bf, ctx)
        out[sv] = {"res": res, "chk": R.hard_eval(res, "C", ss, isl)}
    return out


def _tag(rows, n0, held, a, held_day=None):
    """Attach the book actually held after this tier's decision (and the day it was formed, r4: lot back-computation uses that
    day's close) to the rows just written (repro check only)."""
    for r in rows[n0:]:
        r["_held"] = held[(a, r["sleeve"])]
        r["_held_day"] = None if held_day is None else held_day[(a, r["sleeve"])]


def replay(lr, lt, decide="A", keep_px=False):
    """decide="A": v1.3 path (MAIN RESULT, §8 baseline). decide="C": counterfactual path whose adoption follows basis C
    (second disclosure column only). Labels status_A_repro / status_C_coupled are produced on both paths."""
    if decide not in ("A", "C"): raise ValueError(decide)
    V.POOL_STD = True; V.IND_POOL = True        # v1.3 settings (b6238254 l.281–282)
    sess = R.sessions(); rd = R.rebal_days(sess)
    prev = {a: None for a in R.AUMS}; held = {(a, sv): None for a in R.AUMS for sv, _ in R.SLEEVES}
    held_day = {k: None for k in held}
    rows, runtime_days, pxs = [], [], {}
    for d in rd:
        R._RSS["day_peak_mb"] = 0.0; t0 = time.time(); day_s = f"{d:%Y-%m-%d}"; win = "X2" if d >= pd.Timestamp(R.X2[0]) else "SEALED"
        D = C.prepare_day(d)
        px = _px(D, d) if D is not None else None
        if keep_px and px is not None: pxs[day_s] = px.astype(float).to_dict()   # lot-count comparison (repro check)
        for a in R.AUMS:
            n0 = len(rows)
            base = {"date": day_s, "window": win, "aum": a}
            if D is None:
                for sv, _ in R.SLEEVES:
                    rows.append({**base, "sleeve": sv, "status_A_repro": "NO_DATA_CARRY", "status_C_coupled": "NO_DATA_CARRY"})
                _tag(rows, n0, held, a, held_day); continue
            w0 = (prev[a] if prev[a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
            excl = [i for i in D["alpha"].index if np.isfinite(px.get(i, np.nan)) and C.lot_round_rule(i) * px.get(i, np.nan) > C.NAME_CAP[a] * a]
            w, info = V.solve_v11(D, w0, a, lr, lt[a], exclude=excl)
            R.rss_guard(f"d21[{decide}] solve {day_s} aum={a}")
            if w is None:
                for sv, _ in R.SLEEVES:
                    rows.append({**base, "sleeve": sv, "status_A_repro": "INFEASIBLE", "status_C_coupled": "INFEASIBLE", "n_excluded_v13": len(excl),
                                 "stage_A": info.get("stage")})
                _tag(rows, n0, held, a, held_day); continue
            sl = {}
            for sv, bf in R.SLEEVES:
                sty = V.style_ctx(D, info["slack"]["size_slack"], info["slack"]["ind_slack"])
                wl, li = V.lot_round_greedy(w * (1 - bf), px, a, D["industry"], D["wb"].reindex(D["alpha"].index).fillna(0.0), C.NAME_CAP[a],
                                            ballast_frac=bf, style=sty, wb_raw=False)
                sl[sv] = {"w": wl, **li}
            badA = any(x["lot_flag"] == "LOT_HARD_FAIL" for x in sl.values())             # v1.3 coupling rule (b6238254 l.355)
            jc = judge_C(sl, info, D, a)
            hard_both = all(jc[sv]["chk"]["hard_pass"] for sv, _ in R.SLEEVES)
            for sv, bf in R.SLEEVES:
                x = sl[sv]; ch = jc[sv]["chk"]; e = jc[sv]["res"]; bC = e["bases"]["C"]
                stA = "LOT_HARD_FAIL" if badA else ("LOT_CASH_GT2" if x["lot_flag"] == "LOT_CASH_GT2" else "OK")
                stC = "LOT_HARD_FAIL" if not hard_both else ("LOT_CASH_GT2" if ch["cash_gt2"] else "OK")
                rows.append({**base, "sleeve": sv, "status_A_repro": stA, "status_C_coupled": stC, "hard_C_this": bool(ch["hard_pass"]),
                    "hard_C_both": bool(hard_both), "cash": float(e["cash"]), "cash_gt2": bool(ch["cash_gt2"]), "reasons_C": ",".join(ch["reasons"]),
                    "size_slack": info["slack"]["size_slack"], "ind_slack": info["slack"]["ind_slack"], "n_names": int(e["n_names"]),
                    "n_excluded_v13": len(excl), "size_act_C": R.fnum(bC["size"]), "midcap_act_C": R.fnum(bC["midcap"]), "beta_act_C": R.fnum(bC["beta"]),
                    "ind_active_max_C": R._maxabs(bC["act"]), "ind_abs_max_C": R._max(bC["ind"]), "beta_port": float(e["beta_port"]),
                    "stage_A": ("lot" if badA else None), "lot_flag_A": x["lot_flag"]})
            adopt = (not badA) if decide == "A" else hard_both                          # the ONLY difference between the two paths
            if adopt:
                prev[a] = w
                for sv, _ in R.SLEEVES: held[(a, sv)] = sl[sv]["w"]; held_day[(a, sv)] = day_s
            _tag(rows, n0, held, a, held_day)
        rss = R.rss_guard(f"d21[{decide}] end of day {day_s}")
        runtime_days.append({"path": decide, "day": day_s, "sec": round(time.time() - t0, 1), "rss_mb": round(rss),
                             "rss_peak_intraday_mb": round(R._RSS["day_peak_mb"])})
        print(json.dumps({"path": decide, "day": day_s}), flush=True)
        del D, px; gc.collect()
    return rows, runtime_days, rd, pxs


def to_disc(rows, key):
    """Build a v1.4-shaped disclosure frame so the identical R.post_run_disclosures (§8, stop rule) code is used."""
    out = []
    for r in rows:
        d = {c: None for c in R.DISC_COLS}
        st = r[key]
        d.update({"date": r["date"], "window": r["window"], "aum": r["aum"], "sleeve": r["sleeve"], "status": st,
                  "fail_stage": ("solve" if st == "INFEASIBLE" else ("lot" if st == "LOT_HARD_FAIL" else None)),
                  "s3_used": False, "s3_trigger": "none", "s3_rescued_from_hard": False, "s3_rescued_from_cash": False,
                  "lot_fail_reason": (r.get("reasons_C") or "") if st == "LOT_HARD_FAIL" else "", "cash": r.get("cash"),
                  "turn_solver_gt40": False, "turn_lot_gt40": False, "clamp_count": 0, "eps_revert_count": 0})
        out.append(d)
    return pd.DataFrame(out, columns=R.DISC_COLS)


def exact_lots(book, px_day, a):
    """r4 (Arch ruling 4) exact back-computation of lot counts of a lot book formed with px_day (the PIT close of the day the book
    was formed). For each name: k = round(w*aum/(P*L)); accepted only if np.float64(k)*L * P / aum == w bit-for-bit (the very
    expression of lot_round_greedy, b500c21b l.128) - no tolerance. Names without a finite price keep their target weight in
    lot_round_greedy (no lots; l.198) and are counted separately; the ballast is not a lot position."""
    lots, bad, nopx = {}, [], 0
    for i, w in book.items():
        i = str(i)
        if i == C.BALLAST: continue
        w = float(w)
        if w <= 0: continue
        p = px_day.get(i)
        if p is None or not np.isfinite(p) or p <= 0:
            nopx += 1; continue
        P = float(p); L = C.lot_round_rule(i)
        k = int(np.floor(w * a / (P * L) + 0.5))
        if k <= 0 or np.float64(k) * L * P / a != w:
            bad.append(i); continue
        lots[i] = k
    return lots, bad, nopx


def ckpt_held(recs):
    """Canonical held lot book per (aum, sleeve, date) from the v1.3 ckpts, exactly as 29b38cf8 write_daily (l.140–151) expands it:
    a book is replaced only on days whose rec['sleeves'] has the tier; otherwise carried. Returns {(a, sv, date): (book, book_day)}."""
    out = {}; held = {(a, sv): (None, None) for a in R.AUMS for sv, _ in R.SLEEVES}
    for day in sorted(recs):
        rec = recs[day]; sls = rec.get("sleeves", {}) if isinstance(rec, dict) else {}
        for a in R.AUMS:
            sl = sls.get(a)
            for sv, _ in R.SLEEVES:
                if sl is not None and sv in sl: held[(a, sv)] = (sl[sv]["w"], day)
                out[(a, sv, day)] = held[(a, sv)]
    return out


def _wmap(book):
    return {str(i): float(v) for i, v in book.items() if float(v) > 0} if book is not None else {}


def repro_check(rows, pxs, recs):
    """Reproduced basis-A labels and books vs the canonical v1.3 products (pinned shas) + the citability rule (CLARIFY-2 §2.3).
    r4: books and lots are compared against the v1.3 ckpt lot books (path 1, preferred by Arch ruling 4); lot counts are
    back-computed exactly (path 2 inside path 1: the ckpt stores weights, not counts) - see docs/v2/STRATEGY_D21_V1_3_BASISC_RECALC_ZH.md.
    The parquet weight products are still compared (≤1e-6). Disclosure only; never a VOID condition."""
    can = pd.read_csv(ROOT / V13_PRODUCTS["v13_disclosure_sha256"], usecols=["date", "aum", "sleeve", "status"])
    cmap = {(str(r.date), int(r.aum), str(r.sleeve)): str(r.status) for r in can.itertuples(index=False)}
    mine = {(r["date"], int(r["aum"]), r["sleeve"]): r["status_A_repro"] for r in rows}
    keys = sorted(set(cmap) | set(mine))
    lab_mis = [{"date": k[0], "aum": k[1], "sleeve": k[2], "repro": mine.get(k), "canonical": cmap.get(k)} for k in keys if mine.get(k) != cmap.get(k)]
    ck = ckpt_held(recs)
    rd_rows = sorted({r["date"] for r in rows})
    ck_days = sorted(recs)
    wkey = {(600_000, "equity_100"): "v13_w_eq100_60w_sha256", (1_000_000, "equity_100"): "v13_w_eq100_100w_sha256",
            (600_000, "equity80_etf20_510300"): "v13_w_eq80_60w_sha256", (1_000_000, "equity80_etf20_510300"): "v13_w_eq80_100w_sha256"}
    wdiff, all_ok = {}, rd_rows == ck_days
    for (a, sv), k in wkey.items():
        df = pd.read_parquet(ROOT / V13_PRODUCTS[k], columns=["session", "instrument", "weight"])
        g = {s: dict(zip(x["instrument"].astype(str), x["weight"].astype(float))) for s, x in df.groupby(df["session"].astype(str))}
        del df
        mx_p = mx_k = 0.0; n_cmp = n_wp = n_wk = n_set = n_lot = n_bday = n_inexact = n_nopx = 0; ex = []
        for r in rows:
            if r["aum"] != a or r["sleeve"] != sv: continue
            my_w = _wmap(r.get("_held")); my_day = r.get("_held_day")
            par_w = {i: v for i, v in g.get(r["date"], {}).items() if v > 0}
            ck_book, ck_day = ck.get((a, sv, r["date"]), (None, None)); ck_w = _wmap(ck_book)
            dp = max((abs(par_w.get(i, 0.0) - my_w.get(i, 0.0)) for i in set(par_w) | set(my_w)), default=0.0)
            dk = max((abs(ck_w.get(i, 0.0) - my_w.get(i, 0.0)) for i in set(ck_w) | set(my_w)), default=0.0)
            same_set = set(ck_w) == set(my_w) == set(par_w)
            same_bday = my_day == ck_day
            if my_w or ck_w:
                lm, bm, nm = exact_lots(my_w, pxs.get(my_day, {}), a) if my_w else ({}, [], 0)
                lc, bc, nc = exact_lots(ck_w, pxs.get(ck_day, {}), a) if ck_w else ({}, [], 0)
                inexact = bool(bm or bc); same_lots = same_bday and not inexact and lm == lc
            else:
                nm = nc = 0; inexact = False; same_lots = same_bday
            mx_p = max(mx_p, dp); mx_k = max(mx_k, dk); n_cmp += 1
            bad_wp, bad_wk = dp > CITE_WEIGHT_TOL, dk > CITE_WEIGHT_TOL
            n_wp += int(bad_wp); n_wk += int(bad_wk); n_set += int(not same_set); n_lot += int(not same_lots)
            n_bday += int(not same_bday); n_inexact += int(inexact); n_nopx += int(nm + nc > 0)
            if (bad_wp or bad_wk or not same_set or not same_lots) and len(ex) < 50:
                ex.append({"date": r["date"], "max_abs_diff_vs_parquet": dp, "max_abs_diff_vs_ckpt": dk, "same_holding_set": same_set,
                           "same_book_day": same_bday, "book_day_repro": my_day, "book_day_ckpt": ck_day,
                           "lots_inexact_names": (bm + bc)[:20] if (my_w or ck_w) else [], "same_lots": same_lots})
        ok = n_cmp > 0 and n_wp == 0 and n_wk == 0 and n_set == 0 and n_lot == 0
        all_ok = all_ok and ok
        wdiff[f"{a}|{sv}"] = {"n_rebalance_days_compared": n_cmp, "max_abs_weight_diff_vs_parquet": mx_p, "max_abs_weight_diff_vs_ckpt": mx_k,
                              f"n_days_maxabs_gt_{CITE_WEIGHT_TOL:g}_parquet": n_wp, f"n_days_maxabs_gt_{CITE_WEIGHT_TOL:g}_ckpt": n_wk,
                              "n_days_holding_set_differs": n_set, "n_days_lots_differ": n_lot, "n_days_book_day_differs": n_bday,
                              "n_days_lots_not_exactly_reconstructible": n_inexact, "n_days_with_no_price_names": n_nopx,
                              "consistent": ok, "examples": ex}
    labels_ok = not lab_mis
    citable = "VALID" if (labels_ok and all_ok) else "VALID_WITH_DISCLOSURE"
    return {"disclosure_only": True, "not_a_void_condition": True, "n_label_rows": len(keys), "n_label_mismatch": len(lab_mis),
            "label_mismatches": lab_mis[:200], "weights": wdiff,
            "ckpt_days_equal_rebalance_days": rd_rows == ck_days, "n_ckpt_days": len(ck_days), "n_rebalance_days": len(rd_rows),
            "lots_path": ("ckpt lot books (v1.3 _ckpt_v1_3_poolind, pickle, sha-verified) + exact lot back-computation "
                          "(ckpt stores weights, not counts; bit-exact, no tolerance)"),
            "citable": citable,
            "citable_rule": ("CLARIFY-2 §2.3: VALID only if labels == core_v1_3_disclosure.csv row by row (0 mismatches), "
                             f"max |w diff| <= {CITE_WEIGHT_TOL:g} vs both the parquet weights and the ckpt lot books on every compared "
                             "rebalance day, identical holding sets, and identical lot counts (exact back-computation on both sides, "
                             "same book-formation day); ckpt days == rebalance days"),
            "citable_note_zh": (None if citable == "VALID" else "复现与 canonical v1.3 不一致：解释前不得引用为「v1.3 口径 C」对照（须 Arch 逐项解释）"),
            "note": "canonical v1.3 ran 29b38cf8 at 00:20 ET without a pinned determinism env; tiny solver-level differences are possible"}


def write_void(out_dir, exc, tb):
    lines = ["# VOID — D21 (v1.3 basis-C recalc) did not produce summary.json", "", f"- written: {R.et_now()} (automatic exception handler)",
             f"- exception: {type(exc).__name__}: {exc}", "- rule: any exit without summary.json voids the run; no retry; Arch re-review + new .ok.",
             "- files present (sha256 only):", ""]
    for p in sorted(out_dir.rglob("*")):
        if p.is_file() and p.name != "VOID.md": lines.append(f"  - {p.relative_to(out_dir)}  {R.sha_file(p)}")
    lines += ["", "```", tb, "```", ""]
    R.write_x(out_dir / "VOID.md", "\n".join(lines))   # r3 P3-2: exclusive create


def _sig(signum, frame):
    raise RunAborted(f"signal {signum}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="D21: v1.3 feasibility re-judged under basis C (Arch .ok required)")
    ap.add_argument("--auth-sha256", required=True)
    args = ap.parse_args(argv)
    pf = preflight(args.auth_sha256)            # SystemExit = refused, nothing written
    out_dir = pf["out_dir"]
    R.acquire_lock(LOCK, {"pid": os.getpid(), "started_et": R.et_now(), "auth_sha256": pf["auth_sha"], "argv": sys.argv})
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT): signal.signal(s, _sig)
    t_start = time.time(); rc = 0
    runtime = {"started_et": R.et_now(), "argv": sys.argv, "python": sys.version, "auth_sha256": pf["auth_sha"], "lock_file": str(LOCK.relative_to(ROOT))}
    try:
        rows, rdays, rd, pxs = replay(pf["lr"], pf["lt"], decide="A", keep_px=True)      # MAIN RESULT (§8 baseline)
        rows_c, rdays_c, _, _ = replay(pf["lr"], pf["lt"], decide="C")                   # second disclosure column only
        runtime["days"] = rdays + rdays_c
        recs, ck_loaded = load_v13_ckpts(pf["auth"][V13_CKPT_KEY])   # r4: 这是 pickle，只读仓库内已钩文件 (sha of the same bytes first);
        #   loaded before end_of_run_recheck so its loaded-module check also covers anything unpickling could import
        fin = R.end_of_run_recheck(pf)                   # r3: PINNED_INPUTS + mask + docs + CLARIFY-2 + loaded modules (else VOID)
        if v13_product_shas() != pf["v13_products"]: raise RuntimeError("v1.3 products changed during the run")
        if ckpt_shas()["combined"] != pf["v13_ckpt"]["combined"]: raise RuntimeError("v1.3 ckpts changed during the run")
        pd.DataFrame([{k: r.get(k) for k in STATUS_COLS} for r in rows], columns=STATUS_COLS).to_csv(out_dir / "d21_status.csv", index=False)
        pd.DataFrame([{k: r.get(k) for k in STATUS_COLS} for r in rows_c], columns=STATUS_COLS).to_csv(
            out_dir / "d21_status_Cdecision_disclosure_only.csv", index=False)
        repC = R.post_run_disclosures(to_disc(rows, "status_C_coupled"))
        repA = R.post_run_disclosures(to_disc(rows, "status_A_repro"))
        repCC = R.post_run_disclosures(to_disc(rows_c, "status_C_coupled"))
        R.write_x(out_dir / "d21_counts_basisC.json", R.jdump(repC, indent=1))
        R.write_x(out_dir / "d21_counts_basisA_repro.json", R.jdump(repA, indent=1))
        R.write_x(out_dir / "d21_counts_Cdecision_disclosure_only.json", R.jdump(repCC, indent=1))
        rep = repro_check(rows, pxs, recs)
        R.write_x(out_dir / "d21_repro_check.json", R.jdump(rep, indent=1))
        summary = {"version": VERSION, "live": False, "promotion": False, "paper_touched": False, "returns_computed": False,
            "purpose": "LOTFIX §8 Beta L6 C-vs-C comparator for v1.4; does not change the v1.3 basis-A release or scorecard (LOTFIX §8)",
            "main_result": "s8_basisC = §8 baseline (CLARIFY-2): holdings follow v1.3 basis-A decisions; labels re-judged under basis C",
            "citable": rep["citable"], "citable_rule": rep["citable_rule"], "citable_note_zh": rep["citable_note_zh"],
            "integrity_warning": bool(repC["s8"]["integrity_warning"] or repA["s8"]["integrity_warning"] or repCC["s8"]["integrity_warning"]),
            "integrity_warning_by_source": {"s8_basisC": repC["s8"]["integrity_warning"], "s8_basisA_repro": repA["s8"]["integrity_warning"],
                                            "C_decision_path": repCC["s8"]["integrity_warning"]},   # r4 (Arch ruling 1): disclosure_missing>0; never blocks
            "specs": {k: v[1] for k, v in PINNED_DOCS.items()}, "clarify_2": {"path": R.CLARIFY2_REL, "sha256": R.CLARIFY2_SHA256},
            "code_sha256": pf["code_sha"], "mask_sha256": pf["mask_sha"],
            "inputs_sha256": {k: {"path": R.PINNED_INPUTS[k], "sha256": pf["inputs"][k]} for k in R.PINNED_INPUTS},
            "nontextbook_closure": {"files": list(R.NT_CLOSURE_FILES), "combined_sha256": R.nt_closure_combined(pf["inputs"])},
            "loaded_project_modules": fin["loaded_project_modules"],
            "v13_products_sha256": {k: {"path": V13_PRODUCTS[k], "sha256": pf["v13_products"][k]} for k in V13_PRODUCTS},
            "v13_ckpt": {"dir": V13_CKPT_REL, "combined_sha256": ck_loaded["combined"], "n_files": ck_loaded["n_files"],
                         "note": "这是 pickle，只读仓库内已钩文件 (bytes sha-verified before unpickling)"},
            "interpreter": pf["interp"], "determinism_env": R.DETERMINISM_ENV,
            "arch_run_auth": {"file": str(AUTH_PATH.relative_to(ROOT)), "sha256": pf["auth_sha"], "fields": pf["auth"]},
            "lambda_risk": pf["lr"], "lambda_turn": {str(k): v for k, v in pf["lt"].items()}, "window": [R.START, R.END], "x2": list(R.X2),
            "n_rebal": len(rd), "tol_D15": R.TOL, "s8_basisC": repC["s8"], "s8_basisA_repro": repA["s8"],
            "stop_rule_x2_M4_basisC": repC["stop_rule_x2"]["per_tier_M4"],
            "disclosure_only_C_decision_path": {"role": "second disclosure column (CLARIFY-2); counterfactual path, NOT v1.3; never a §8 baseline or verdict input",
                                                "s8": repCC["s8"], "stop_rule_x2_M4": repCC["stop_rule_x2"]["per_tier_M4"]},
            "repro_label_mismatch": rep["n_label_mismatch"], "repro_weights": {k: {kk: vv for kk, vv in v.items() if kk != "examples"} for k, v in rep["weights"].items()},
            "outputs_sha256": {str(p.relative_to(out_dir)): R.sha_file(p) for p in sorted(out_dir.rglob("*"))
                               if p.is_file() and p.name not in EXCLUDED and not p.name.endswith(".tmp")}}
        R.write_x_atomic(out_dir / "summary.json", R.jdump(summary, indent=1))   # r3 P3-2
        print("D21_DONE summary.json", R.sha_file(out_dir / "summary.json"), "citable", rep["citable"], flush=True)
    except BaseException as e:  # noqa: BLE001
        rc = 1
        if not (out_dir / "summary.json").exists():
            try: write_void(out_dir, e, traceback.format_exc())
            except BaseException as e2: print(f"VOID write failed: {e2!r}", file=sys.stderr)
        print(f"D21_VOID {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    finally:
        runtime.update({"ended_et": R.et_now(), "elapsed_sec": round(time.time() - t_start, 1), "peak_rss_mb": round(C.rss_mb()), "rc": rc,
                        "summary_present": (out_dir / "summary.json").exists()})
        try: (out_dir / "run_runtime.json").write_text(R.jdump(runtime, indent=1))
        except BaseException: pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
