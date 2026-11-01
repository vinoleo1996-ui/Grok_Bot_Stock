#!/usr/bin/env python3
"""D21 (Arch review db781708 D21 / E-3; LOTFIX §8 Beta L6; CLARIFY-1 d075a2a6 §4): v1.3 feasibility RE-JUDGED UNDER BASIS C,
for the C-vs-C side-by-side comparison with v1.4. Weights/feasibility labels only; NO returns. live=false, promotion=false.

What it does (read-only w.r.t. every v1.3 / v1.4 product; writes only its own out dir + one lock file):
  1. Replays the v1.3 decision path exactly as research/optimizer_core_x2_run.py b6238254 lines 312–366 (= canonical 29b38cf8
     logic): prepare_day -> v1.3 ① lot-cost exclusion -> V.solve_v11 (POOL_STD=IND_POOL=True) -> V.lot_round_greedy per sleeve
     -> v1.3 adoption rule (basis-A lot_flag, two-sleeve coupling). Holdings / w0 chain follow v1.3 (basis A) unchanged.
  2. Re-judges every solved day under basis C with the v1.4 runner's own book_exposures + hard_eval (same D15 tolerance
     TOL=1e-6, same slack as the v1.3 solve), coupled: a sleeve is strict-C on a day iff the solve succeeded, BOTH sleeves pass
     the basis-C HARD check and that sleeve's cash <= 2%.
  3. §8 per CLARIFY-1 (same R.post_run_disclosures code as v1.4): per tier sleeve_A/B strict days, both-sleeves-same-day days,
     denominator 29, daily detail; plus the reproduced basis-A labels for an A-vs-A control.
  4. Reproduction check vs the canonical v1.3 products (disclosure; status labels + rebalance-day weights). Not a VOID condition.
It never calls optimizer_core_x2_run.py (that module creates directories at import) and never modifies it.

Gate: output/strategy_optimizer/core_x2/ARCH_RUN_AUTH_D21_v1_3C.ok (Arch writes it; Strategy never creates it) + --auth-sha256.
Same field / sha / interpreter / determinism-env / lock rules as v1.4 (R). Unified exception handling: no summary -> VOID.md.
Launch (only if Leo continues Core; D21 runs BEFORE v1.4, serial; CLARIFY-1 §4):
  cd /workspace/QuantLab && PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup \
    /workspace/QuantLab/.venv_opt/bin/python research/optimizer_core_v1_3_basisC_recalc_d21.py --auth-sha256 <sha of .ok> \
    > output/strategy_optimizer/core_x2/d21_run.log 2>&1 &
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, re, signal, sys, time, traceback
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_core_x2_run_v1_4 as R      # v1.4 runner: basis-C judge, §8 CLARIFY-1 code, gate helpers (no side effects at import)
C, V = R.C, R.V

VERSION = "d21_v1_3_basisC"
D21_REL = "research/optimizer_core_v1_3_basisC_recalc_d21.py"
CODE_FILES_D21 = (D21_REL, R.RUNNER_REL, "research/optimizer_core_v1_1.py", "research/optimizer_lambda_calib_sealed.py")
OUT_REL = R.CORE_REL + "/v1_3_basisC_d21"                   # own out dir; must be absent or empty; never v1_4*/ or v1.3 products
OUT_DIR = ROOT / OUT_REL
AUTH_PATH = R.CORE / "ARCH_RUN_AUTH_D21_v1_3C.ok"
LOCK = R.CORE / ".d21_v1_3_basisC_run.lock"
CLARIFY_1 = ("docs/v2/LOTFIX_V1_4_FREEZE_RECORD_APPENDIX_CLARIFY_1_ZH.md", "d075a2a68f2d5c42c750669cdff2dd51f93794e11ea907f08ffc29c39c724d85")
PINNED_DOCS = {"lotfix_sha256": R.PINNED_DOCS["lotfix_sha256"], "clarify_sha256": CLARIFY_1}
V13_PRODUCTS = {   # canonical v1.3 products (29b38cf8 run 2026-10-18 00:20–00:27 ET): read-only, used only for the reproduction check
    "v13_disclosure_sha256": R.CORE_REL + "/core_v1_3_disclosure.csv",
    "v13_w_eq100_60w_sha256": R.CORE_REL + "/core_equity_100_60w.parquet",
    "v13_w_eq100_100w_sha256": R.CORE_REL + "/core_equity_100_100w.parquet",
    "v13_w_eq80_60w_sha256": R.CORE_REL + "/core_equity80_etf20_510300_60w.parquet",
    "v13_w_eq80_100w_sha256": R.CORE_REL + "/core_equity80_etf20_510300_100w.parquet",
}
AUTH_REQUIRED_D21 = ("format", "version", "signed_by", "signed_et", "allow_full", "allow_smoke", "live", "promotion", "python_exe",
                     "out_dir", "runner_sha256", "combined_sha256") + tuple(PINNED_DOCS) + tuple(R.DATA_INPUTS) + tuple(V13_PRODUCTS)
SHA_KEYS_D21 = ("runner_sha256", "combined_sha256") + tuple(PINNED_DOCS) + tuple(R.DATA_INPUTS) + tuple(V13_PRODUCTS)
EXCLUDED = ("run_runtime.json",)
STATUS_COLS = ["date", "window", "aum", "sleeve", "status_A_repro", "status_C_coupled", "hard_C_this", "hard_C_both", "cash", "cash_gt2",
               "reasons_C", "size_slack", "ind_slack", "n_names", "n_excluded_v13", "size_act_C", "midcap_act_C", "beta_act_C",
               "ind_active_max_C", "ind_abs_max_C", "beta_port", "stage_A", "lot_flag_A"]


class RunAborted(BaseException):
    pass


def code_sha256_d21():
    per = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE_FILES_D21}
    return {"combined": hashlib.sha256("".join(f"{f}={per[f]}\n" for f in CODE_FILES_D21).encode()).hexdigest(), "files": per}


def parse_run_auth_d21(path):
    if not path.exists(): raise SystemExit(f"d21 blocked: run-auth file missing: {path} (Arch writes it; Strategy never creates it)")
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"): raise SystemExit("d21 blocked: .ok has a BOM")
    kv = {}
    for ln in raw.decode("utf-8").splitlines():
        m = re.match(r"^([a-z0-9_]+)=(.*)$", ln.strip())
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if k in kv: raise SystemExit(f"d21 blocked: field '{k}' appears more than once in {path}")
        kv[k] = v
    miss = [k for k in AUTH_REQUIRED_D21 if not kv.get(k)]
    if miss: raise SystemExit(f"d21 blocked: {path} lacks fields {miss}")
    if kv["format"] != "quantlab_run_auth_v1": raise SystemExit(f"d21 blocked: format={kv['format']!r}")
    if kv["version"] != VERSION: raise SystemExit(f"d21 blocked: version={kv['version']!r}, expected {VERSION}")
    if kv["signed_by"].lower() != "arch": raise SystemExit("d21 blocked: signed_by must be arch")
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


def preflight(expected_auth_sha):
    """All gate checks; writes nothing. SystemExit = refused before anything is written."""
    for k, (rel, pin) in PINNED_DOCS.items():
        if R.sha_file(ROOT / rel) != pin: raise SystemExit(f"d21 blocked: {rel} sha256 != pinned {pin}")
    mask_sha = C.file_sha256(C.MASK_PATH)
    if mask_sha != C.MASK_SHA_EXPECT: raise SystemExit(f"d21 blocked: HI_LIQ mask sha {mask_sha} != {C.MASK_SHA_EXPECT}")
    R.check_input_paths(); R.check_determinism_env()
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
    inputs = R.check_inputs(kv)
    v13 = v13_product_shas()
    bad = sorted(k for k in V13_PRODUCTS if kv[k] != v13[k])
    if bad: raise SystemExit(f"d21 blocked: v1.3 product sha mismatch {bad}")
    R.check_interpreter(kv)
    od = OUT_DIR.resolve()
    if (ROOT / "output/strategy_hiliq").resolve() in od.parents: raise SystemExit("d21 blocked: out dir under output/strategy_hiliq")
    if od.exists() and any(od.iterdir()): raise SystemExit(f"d21 blocked: out dir {od} not empty (no resume / no retry)")
    if LOCK.exists(): raise SystemExit(f"d21 blocked: lock {LOCK} exists (Arch must archive it)")
    return {"lr": lr, "lt": lt, "code_sha": cs, "auth": kv, "auth_sha": auth_sha, "mask_sha": mask_sha, "inputs": inputs,
            "v13_products": v13, "interp": R.interpreter_info(), "out_dir": od}


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


def _tag(rows, n0, held, a):
    """Attach the book actually held after this tier's decision (v1.3 path) to the rows just written (repro check only)."""
    for r in rows[n0:]: r["_held"] = held[(a, r["sleeve"])]


def replay(lr, lt):
    V.POOL_STD = True; V.IND_POOL = True        # v1.3 settings (b6238254 l.281–282)
    sess = R.sessions(); rd = R.rebal_days(sess)
    prev = {a: None for a in R.AUMS}; held = {(a, sv): None for a in R.AUMS for sv, _ in R.SLEEVES}
    rows, runtime_days = [], []
    for d in rd:
        R._RSS["day_peak_mb"] = 0.0; t0 = time.time(); day_s = f"{d:%Y-%m-%d}"; win = "X2" if d >= pd.Timestamp(R.X2[0]) else "SEALED"
        D = C.prepare_day(d)
        px = _px(D, d) if D is not None else None
        for a in R.AUMS:
            n0 = len(rows)
            base = {"date": day_s, "window": win, "aum": a}
            if D is None:
                for sv, _ in R.SLEEVES:
                    rows.append({**base, "sleeve": sv, "status_A_repro": "NO_DATA_CARRY", "status_C_coupled": "NO_DATA_CARRY"})
                _tag(rows, n0, held, a); continue
            w0 = (prev[a] if prev[a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
            excl = [i for i in D["alpha"].index if np.isfinite(px.get(i, np.nan)) and C.lot_round_rule(i) * px.get(i, np.nan) > C.NAME_CAP[a] * a]
            w, info = V.solve_v11(D, w0, a, lr, lt[a], exclude=excl)
            R.rss_guard(f"d21 solve {day_s} aum={a}")
            if w is None:
                for sv, _ in R.SLEEVES:
                    rows.append({**base, "sleeve": sv, "status_A_repro": "INFEASIBLE", "status_C_coupled": "INFEASIBLE", "n_excluded_v13": len(excl),
                                 "stage_A": info.get("stage")})
                _tag(rows, n0, held, a); continue
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
            if not badA:
                prev[a] = w
                for sv, _ in R.SLEEVES: held[(a, sv)] = sl[sv]["w"]
            _tag(rows, n0, held, a)
        rss = R.rss_guard(f"d21 end of day {day_s}")
        runtime_days.append({"day": day_s, "sec": round(time.time() - t0, 1), "rss_mb": round(rss), "rss_peak_intraday_mb": round(R._RSS["day_peak_mb"])})
        print(json.dumps({"day": day_s}), flush=True)
        del D, px; gc.collect()
    return rows, runtime_days, rd


def to_disc(rows, key):
    """Build a v1.4-shaped disclosure frame so the identical R.post_run_disclosures (§8 CLARIFY-1, stop rule) code is used."""
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


def repro_check(rows):
    """Disclosure only: reproduced basis-A labels and rebalance-day books vs the canonical v1.3 products (pinned shas)."""
    can = pd.read_csv(ROOT / V13_PRODUCTS["v13_disclosure_sha256"], usecols=["date", "aum", "sleeve", "status"])
    cmap = {(str(r.date), int(r.aum), str(r.sleeve)): str(r.status) for r in can.itertuples(index=False)}
    lab_mis = [{"date": r["date"], "aum": r["aum"], "sleeve": r["sleeve"], "repro": r["status_A_repro"], "canonical": cmap.get((r["date"], r["aum"], r["sleeve"]))}
               for r in rows if cmap.get((r["date"], r["aum"], r["sleeve"])) != r["status_A_repro"]]
    wkey = {(600_000, "equity_100"): "v13_w_eq100_60w_sha256", (1_000_000, "equity_100"): "v13_w_eq100_100w_sha256",
            (600_000, "equity80_etf20_510300"): "v13_w_eq80_60w_sha256", (1_000_000, "equity80_etf20_510300"): "v13_w_eq80_100w_sha256"}
    wdiff = {}
    for (a, sv), k in wkey.items():
        df = pd.read_parquet(ROOT / V13_PRODUCTS[k], columns=["session", "instrument", "weight"])
        g = {s: dict(zip(x["instrument"].astype(str), x["weight"].astype(float))) for s, x in df.groupby(df["session"].astype(str))}
        del df
        mx, n_cmp, n_bad = 0.0, 0, 0
        for r in rows:
            if r["aum"] != a or r["sleeve"] != sv or r.get("_held") is None: continue
            can_w = g.get(r["date"], {}); mine = {str(i): float(v) for i, v in r["_held"].items() if float(v) > 0}
            names = set(can_w) | set(mine)
            dmax = max((abs(can_w.get(i, 0.0) - mine.get(i, 0.0)) for i in names), default=0.0)
            mx = max(mx, dmax); n_cmp += 1; n_bad += int(dmax > 1e-9)
        wdiff[f"{a}|{sv}"] = {"n_rebalance_days_compared": n_cmp, "n_days_maxabs_gt_1e-9": n_bad, "max_abs_weight_diff": mx}
    return {"disclosure_only": True, "not_a_void_condition": True, "n_label_rows": len(rows), "n_label_mismatch": len(lab_mis),
            "label_mismatches": lab_mis[:200], "weights": wdiff,
            "note": "canonical v1.3 ran 29b38cf8 at 00:20 ET without a pinned determinism env; tiny solver-level differences are possible"}


def write_void(out_dir, exc, tb):
    lines = ["# VOID — D21 (v1.3 basis-C recalc) did not produce summary.json", "", f"- written: {R.et_now()} (automatic exception handler)",
             f"- exception: {type(exc).__name__}: {exc}", "- rule: any exit without summary.json voids the run; no retry; Arch re-review + new .ok.",
             "- files present (sha256 only):", ""]
    for p in sorted(out_dir.rglob("*")):
        if p.is_file() and p.name != "VOID.md": lines.append(f"  - {p.relative_to(out_dir)}  {R.sha_file(p)}")
    lines += ["", "```", tb, "```", ""]
    (out_dir / "VOID.md").write_text("\n".join(lines), encoding="utf-8")


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
        rows, rdays, rd = replay(pf["lr"], pf["lt"])
        runtime["days"] = rdays
        if R.input_shas() != pf["inputs"] or v13_product_shas() != pf["v13_products"]:
            raise RuntimeError("pinned inputs / v1.3 products changed during the run")
        pd.DataFrame([{k: r.get(k) for k in STATUS_COLS} for r in rows], columns=STATUS_COLS).to_csv(out_dir / "d21_status.csv", index=False)
        repC = R.post_run_disclosures(to_disc(rows, "status_C_coupled"))
        repA = R.post_run_disclosures(to_disc(rows, "status_A_repro"))
        (out_dir / "d21_counts_basisC.json").write_text(R.jdump(repC, indent=1))
        (out_dir / "d21_counts_basisA_repro.json").write_text(R.jdump(repA, indent=1))
        rep = repro_check(rows)
        (out_dir / "d21_repro_check.json").write_text(R.jdump(rep, indent=1))
        summary = {"version": VERSION, "live": False, "promotion": False, "paper_touched": False, "returns_computed": False,
            "purpose": "LOTFIX §8 Beta L6 C-vs-C comparator for v1.4; does not change the v1.3 basis-A release or scorecard (LOTFIX §8)",
            "path_note": "holdings / w0 chain follow the v1.3 (basis A) decisions; only the feasibility label is re-judged under basis C (coupled)",
            "specs": {k: v[1] for k, v in PINNED_DOCS.items()}, "code_sha256": pf["code_sha"], "mask_sha256": pf["mask_sha"],
            "inputs_sha256": {k: {"path": R.DATA_INPUTS[k], "sha256": pf["inputs"][k]} for k in R.DATA_INPUTS},
            "v13_products_sha256": {k: {"path": V13_PRODUCTS[k], "sha256": pf["v13_products"][k]} for k in V13_PRODUCTS},
            "interpreter": pf["interp"], "determinism_env": R.DETERMINISM_ENV,
            "arch_run_auth": {"file": str(AUTH_PATH.relative_to(ROOT)), "sha256": pf["auth_sha"], "fields": pf["auth"]},
            "lambda_risk": pf["lr"], "lambda_turn": {str(k): v for k, v in pf["lt"].items()}, "window": [R.START, R.END], "x2": list(R.X2),
            "n_rebal": len(rd), "tol_D15": R.TOL, "s8_basisC": repC["s8"], "s8_basisA_repro": repA["s8"],
            "stop_rule_x2_M4_basisC": repC["stop_rule_x2"]["per_tier_M4"],
            "repro_label_mismatch": rep["n_label_mismatch"], "repro_weights": rep["weights"],
            "outputs_sha256": {str(p.relative_to(out_dir)): R.sha_file(p) for p in sorted(out_dir.rglob("*"))
                               if p.is_file() and p.name not in EXCLUDED and not p.name.endswith(".tmp")}}
        tmp = out_dir / "summary.json.tmp"; tmp.write_text(R.jdump(summary, indent=1)); os.replace(tmp, out_dir / "summary.json")
        print("D21_DONE summary.json", R.sha_file(out_dir / "summary.json"), flush=True)
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
