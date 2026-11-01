#!/usr/bin/env python3
"""OPTIMIZER Core FROZEN — Stage1 sealed disclosure + X2 weights, dual sleeves, book-smoke.
Frozen λ from output/strategy_optimizer/calib (no re-calibration). live=false. Paper untouched.
Phases: --phase weights | smoke | all
"""
from __future__ import annotations
import argparse, gc, json, sys, time, pickle
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C  # reuse solver / HARD / two-step polish
CAL = ROOT / "output/strategy_optimizer/calib"
OUT = ROOT / "output/strategy_optimizer/core_x2"; OUT.mkdir(parents=True, exist_ok=True)
CK = OUT / "_ckpt"; CK.mkdir(exist_ok=True)
START, END = "2018-01-02", "2026-10-09"
X2 = ("2024-06-03", "2026-10-09")
AUMS = {600_000: "60w", 1_000_000: "100w"}

def frozen_lambdas():
    r = json.loads((CAL / "calib_lambda_risk.json").read_text())
    lr = float(r.get("lambda_risk"))
    lt = {a: float(json.loads((CAL / f"calib_lambda_turn_{t}.json").read_text())["lambda_turn"]) for a, t in AUMS.items()}
    assert abs(lr - 117.21317483995702) < 1e-6 and all(abs(v - 0.6) < 1e-9 for v in lt.values()), (lr, lt)
    return lr, lt

def sessions():
    cal = pd.read_parquet(C.CAL_PATH)
    cal["d"] = pd.to_datetime(cal["cal_date"].astype(str), format="%Y%m%d")
    s = cal.loc[cal["is_open"] == 1, "d"].sort_values()
    return [pd.Timestamp(x) for x in s[(s >= START) & (s <= END)]]

def rebal_days(sess):
    me = C.month_ends(START, END)
    r = sorted(set([sess[0]] + me + [sess[-1]]))
    return r

def phase_weights():
    lr, lt = frozen_lambdas()
    sess = sessions(); rd = rebal_days(sess)
    prev = {a: None for a in AUMS}; log = []
    for d in rd:
        ck = CK / f"{d:%Y%m%d}.pkl"
        if ck.exists():
            rec = pickle.load(open(ck, "rb"))
            for a in AUMS:
                if rec["w"][a] is not None: prev[a] = rec["w"][a]
            log.append(rec["log"]); continue
        t0 = time.time(); D = C.prepare_day(d); rec = {"w": {}, "log": {"day": str(d.date())}}
        for a in AUMS:
            if D is None:
                rec["w"][a] = None; rec["log"][f"status_{a}"] = "NO_DATA_CARRY"; continue
            w0 = (prev[a] if prev[a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
            r = C.two_step_polish(D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"], D["B"], D["F"],
                                  D["delta"], D["betas"], aum=a, lambda_risk=lr, lambda_turn=lt[a])
            if r.w is None:
                rec["w"][a] = None; rec["log"][f"status_{a}"] = "INFEASIBLE_CARRY"; continue
            w = r.w[r.w > 0]
            idx = w.index.union(prev[a].index if prev[a] is not None else w.index)
            tow = 0.5 * float((w.reindex(idx).fillna(0) - (prev[a].reindex(idx).fillna(0) if prev[a] is not None else 0)).abs().sum()) if prev[a] is not None else None
            rec["w"][a] = w; prev[a] = w
            rec["log"].update({f"status_{a}": r.status, f"neff_{a}": r.neff, f"n_{a}": int(len(w)),
                               f"sum_w_{a}": float(w.sum()), f"one_way_{a}": tow})
        rec["log"]["sec"] = round(time.time() - t0, 1); rec["log"]["rss_mb"] = round(C.rss_mb())
        pickle.dump(rec, open(ck, "wb")); log.append(rec["log"])
        print(json.dumps(rec["log"]), flush=True); del D; gc.collect()
    # expand to daily (hold from rebal day until next rebal)
    recs = {d: pickle.load(open(CK / f"{d:%Y%m%d}.pkl", "rb"))["w"] for d in rd}
    # PREREG §(d) lot rounding: q=floor(w*AUM/(P*lot))*lot, residual -> cash. PIT close on rebal day.
    names = sorted({str(i) for d in rd for a in AUMS if recs[d][a] is not None for i in recs[d][a].index} | {C.BALLAST})
    basic = C.load_daily_basic_window(names, pd.Timestamp(START) - pd.Timedelta(days=10), pd.Timestamp(END))
    close = basic.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last").sort_index()
    close.index = pd.to_datetime(close.index)
    lot_stats = {"no_price_unrounded": 0, "zeroed_by_lot": 0, "cash_from_lot": []}
    def lot_round(w, d, aum):
        px = close.loc[:d].ffill().iloc[-1] if (close.index <= d).any() else pd.Series(dtype=float)
        out = {}
        for inst, wt in w.items():
            P = px.get(inst, np.nan)
            if not np.isfinite(P) or P <= 0:
                out[inst] = wt; lot_stats["no_price_unrounded"] += 1; continue
            lot = C.lot_round_rule(inst); q = np.floor(wt * aum / (P * lot)) * lot
            if q <= 0: lot_stats["zeroed_by_lot"] += 1; continue
            out[inst] = q * P / aum
        o = pd.Series(out, dtype=float); lot_stats["cash_from_lot"].append(float(w.sum() - o.sum())); return o
    paths = {}
    for a, tag in AUMS.items():
        for sleeve in C.REPORT_SLEEVES:
            rows = []; cur = None; ri = 0
            for s in sess:
                if s in recs and recs[s][a] is not None:
                    cur = lot_round(C.apply_report_sleeve(recs[s][a], sleeve), s, a)
                if cur is None: continue
                ss = s.strftime("%Y-%m-%d")
                for inst, wt in cur.items():
                    if wt > 0: rows.append((ss, inst, float(wt)))
            df = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
            df["date"] = df["session"]; df["target_weight"] = df["weight"]
            df["instrument_id"] = df["instrument"].map(lambda x: f"{x.split('.')[1].lower()}.{x.split('.')[0]}")
            df["universe_id"] = "HI_LIQ_V1"; df["mechanism_tag"] = "optimizer_core_frozen"; df["who_pays_zh"] = "N/A"
            df["aum"] = a; df["sleeve"] = sleeve; df["is_rebalance_day"] = df["session"].isin({x.strftime("%Y-%m-%d") for x in rd})
            df["window"] = np.where(df["session"] >= X2[0], "X2", "SEALED")
            p = OUT / f"core_{sleeve}_{tag}.parquet"; df.to_parquet(p, index=False); paths[f"{sleeve}_{tag}"] = str(p.relative_to(ROOT))
    meta = {"hard_spec": C.HARD_SPEC, "cadence": C.CADENCE, "lambda_risk": lr, "lambda_turn": {str(k): v for k, v in lt.items()},
            "window": [START, END], "sealed": [C.SEALED_START, C.SEALED_END], "x2": list(X2),
            "mask": str(C.MASK_PATH.relative_to(ROOT)), "mask_sha256": C.file_sha256(C.MASK_PATH),
            "n_rebal": len(rd), "paths": paths, "live": False, "paper_touched": False,
            "x2_returns_used_for_selection": False, "lot_stats": {k: (v if not isinstance(v, list) else {"mean": float(np.mean(v)) if v else None, "max": float(np.max(v)) if v else None, "n": len(v)}) for k, v in lot_stats.items()}, "rebal_log": log, "annualization": 244}
    (OUT / "core_weights_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=str))
    print("WEIGHTS_DONE", json.dumps(paths))

def exposure_drift(wl, D):
    """Post-rounding Size/MidCap/β drift vs benchmark (pool-level standardization; cash=0 exposure)."""
    lnm = D["ln_mcap"].astype(float); pool = D["alpha"].index
    x = lnm.reindex(pool); z = (x - x.mean()) / (x.std(ddof=0) + 1e-12)
    m = (x - x.mean()) ** 2; m = (m - m.mean()) / (m.std(ddof=0) + 1e-12)
    b = D["betas"].reindex(pool).fillna(1.0); wb = D["wb"].reindex(pool).fillna(0.0)
    we = wl.drop(C.BALLAST, errors="ignore").reindex(pool).fillna(0.0)
    bal = float(wl.get(C.BALLAST, 0.0))  # 510300 ~ benchmark-like: size/mid = wb exposure, beta 1.0
    f = lambda v: float((we * v.fillna(0)).sum() + bal * (wb * v.fillna(0)).sum() / max(wb.sum(), 1e-12))
    ind = D["industry"]; gi = lambda w: w.groupby(w.index.map(lambda n: ind.get(n, "_UNK"))).sum()
    eqs = float(we.sum()); pi = gi(we[we > 0]); bi = gi(wb) / max(wb.sum(), 1e-12) * eqs  # equity-book industry vs wb scaled to equity
    act = pi.reindex(pi.index.union(bi.index)).fillna(0) - bi.reindex(pi.index.union(bi.index)).fillna(0)
    return {"ind_active_max": float(act.abs().max()) / max(eqs, 1e-12), "ind_abs_max": float(pi.max()) / max(eqs, 1e-12),
            "size_drift": f(z) - float((wb * z.fillna(0)).sum()),
            "midcap_drift": f(m) - float((wb * m.fillna(0)).sum()),
            "beta_drift": (lambda bb: float((we * b).sum() + bal * bb) - bb)(float((wb * b).sum() / max(wb.sum(), 1e-12)) if BETA_POOL else 1.0)}

BETA_POOL = False  # v1.2: β benchmark = full-pool wb-weighted β (solver and recheck alike)

V11_STATUSES = ("OK", "INFEASIBLE", "LOT_HARD_FAIL", "LOT_CASH_GT2")
RUN_AUTH = {}  # v1.3: filled from ARCH_RUN_AUTH_v1_3.ok, recorded in meta

def write_v11_outputs(ck_dir, rd, sess, out_dir, version="v1_1"):
    """Daily expansion (same filenames/schema as v0) + per-day disclosure CSV + meta. No returns."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    rd = [d for d in rd if (ck_dir / f"{d:%Y%m%d}.pkl").exists()]
    recs = {d: pickle.load(open(ck_dir / f"{d:%Y%m%d}.pkl", "rb")) for d in rd}
    rdset = {x.strftime("%Y-%m-%d") for x in rd}; disc = []; paths = {}
    held = {(a, sv): None for a in AUMS for sv in C.REPORT_SLEEVES}
    targets = {}  # (a, sv, day) -> Series
    for d in rd:
        rec = recs[d]
        for a in AUMS:
            lg = rec["log"].get(a, {}); sl = rec.get("sleeves", {}).get(a)
            for sv in C.REPORT_SLEEVES:
                if sl is not None and sv in sl:
                    x = sl[sv]; st = "LOT_CASH_GT2" if x["lot_flag"] == "LOT_CASH_GT2" else "OK"
                    held[(a, sv)] = x["w"]
                else:
                    x = dict(rec.get("carry_drift", {}).get(a, {}).get(sv, {}))
                    st = "LOT_HARD_FAIL" if lg.get("stage") == "lot" else ("INFEASIBLE" if lg.get("status") in ("INFEASIBLE",) else lg.get("status", "MISSING"))
                targets[(a, sv, d)] = held[(a, sv)]
                w = held[(a, sv)]; eq = w.drop(C.BALLAST, errors="ignore") if w is not None else None
                disc.append({"date": f"{d:%Y-%m-%d}", "window": "X2" if d >= pd.Timestamp(X2[0]) else "SEALED", "aum": a, "sleeve": sv,
                    "status": st, "carry": lg.get("carry"), "stage": lg.get("stage"), "K": lg.get("K"), "tries": lg.get("tries"),
                    "n_names": int((eq > 0).sum()) if eq is not None else 0, "sum_w": float(w.sum()) if w is not None else 0.0,
                    "cash": (1.0 - float(w.sum())) if w is not None else 1.0,
                    "size_slack": (lg.get("slack") or {}).get("size_slack"), "ind_slack": (lg.get("slack") or {}).get("ind_slack"),
                    "size_drift": x.get("size_drift"), "midcap_drift": x.get("midcap_drift"), "beta_drift": x.get("beta_drift"),
                    "K0": lg.get("k0"), "ind_active_max": x.get("ind_active_max"), "ind_abs_max": x.get("ind_abs_max"),
                    "n_excluded": lg.get("n_excluded"), "lot_fail_reason": lg.get("lot_fail_reason"), "carry_drift_disclosed": bool(rec.get("carry_drift", {}).get(a)) and sl is None,
                    "neff_opt": lg.get("neff_opt"), "one_way_opt": lg.get("one_way"),
                    "carry_n_out_of_pool": x.get("carry_n_out_of_pool"), "carry_out_of_pool_names": x.get("carry_out_of_pool_names")})
    D = pd.DataFrame(disc)
    ss_ = D["size_slack"].fillna(0); is_ = D["ind_slack"].fillna(0)
    sb = C.SIZE_BOX + ss_ + 1e-6
    D["c1_size_breach"] = D["size_drift"].abs() > sb
    D["c1_midcap_breach"] = D["midcap_drift"].abs() > sb
    D["c1_beta_breach"] = D["beta_drift"].abs() > C.BETA_BOX + 1e-6
    D["c1_ind_breach"] = (D["ind_active_max"] > C.IND_ACTIVE + is_ + 1e-6) | (D["ind_abs_max"] > C.IND_ABS + 1e-6)
    D["LOT_STYLE_DRIFT"] = D[["c1_size_breach", "c1_midcap_breach", "c1_beta_breach", "c1_ind_breach"]].any(axis=1) & D["size_drift"].notna()
    D["slack_at_cap"] = (ss_ >= C.SIZE_SLACK_MAX - 1e-9) & (is_ >= C.IND_SLACK_MAX - 1e-9)
    D["slack_used"] = (ss_ > 0) | (is_ > 0)
    assert set(D.status) <= set(V11_STATUSES) | {"NO_DATA_CARRY"}, set(D.status)
    D.to_csv(out_dir / f"core_{version}_disclosure.csv", index=False)
    ex = [e for d in rd for a in AUMS for e in recs[d].get("exclusions", {}).get(a, [])]
    if ex: pd.DataFrame(ex).to_csv(out_dir / f"core_{version}_lot_exclusions.csv", index=False)
    D[D.status.isin(["INFEASIBLE", "LOT_HARD_FAIL", "NO_DATA_CARRY"])][["date", "window", "aum", "sleeve", "status", "stage", "carry"]].to_csv(out_dir / f"core_{version}_infeasible_days.csv", index=False)
    for a, tag in AUMS.items():
        for sv in C.REPORT_SLEEVES:
            rows = []; cur = None
            for s_ in sess:
                if s_ in recs: cur = targets[(a, sv, s_)]
                if cur is None: continue
                ss = s_.strftime("%Y-%m-%d")
                rows += [(ss, i, float(wt)) for i, wt in cur.items() if wt > 0]
            df = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
            df["date"] = df["session"]; df["target_weight"] = df["weight"]
            df["instrument_id"] = df["instrument"].map(lambda x: f"{x.split('.')[1].lower()}.{x.split('.')[0]}")
            df["universe_id"] = "HI_LIQ_V1"; df["mechanism_tag"] = f"optimizer_core_frozen_{version}"; df["who_pays_zh"] = "N/A"
            df["aum"] = a; df["sleeve"] = sv; df["is_rebalance_day"] = df["session"].isin(rdset)
            df["window"] = np.where(df["session"] >= X2[0], "X2", "SEALED")
            pth = out_dir / f"core_{sv}_{tag}.parquet"; df.to_parquet(pth, index=False); paths[f"{sv}_{tag}"] = str(pth)
    lr, lt = frozen_lambdas()
    meta = {"version": "FROZEN_" + version.replace("_", "."), "amend_doc": f"docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_{version}_ZH.md", "lambda_risk": lr,
            "lambda_turn": {str(k): v for k, v in lt.items()}, "cadence": C.CADENCE, "n_rebal": len(rd), "paths": paths,
            "status_counts": D.groupby(["aum", "sleeve", "status"]).size().rename("n").reset_index().to_dict("records"),
            "mask_sha256": C.file_sha256(C.MASK_PATH), "live": False, "paper_touched": False, "returns_computed": False,
            "industry_benchmark": ("full_pool_wb" if version == "v1_3" else "support_name_wb(defect)"), "arch_run_auth": dict(RUN_AUTH) or None}
    (out_dir / "core_weights_meta.json").write_text(json.dumps(meta, indent=1, default=str))
    print("WEIGHTS_DONE_V1_1", json.dumps(paths)); return paths, D

def phase_weights_v11(smoke_days=None, arch_cosigned=False, version="v1_1"):
    """FROZEN_v1.1 (docs/v2/STRATEGY_OPTIMIZER_PREREG_AMEND_v1_1_ZH.md). Weights only, no returns."""
    import optimizer_core_v1_1 as V
    global BETA_POOL
    V.POOL_STD = version in ("v1_2", "v1_3"); BETA_POOL = V.POOL_STD; v13 = version == "v1_3"
    V.IND_POOL = v13  # 主 Agent 2026-10-18: industry benchmark = full-pool wb (support-name wb rejected)
    lr, lt = frozen_lambdas(); sess = sessions(); rd = rebal_days(sess)
    # v1.3 ckpts written under the rejected support-wb industry benchmark are void -> new ckpt dir
    ck_dir = CK.parent / (f"_ckpt_{version}_poolind" if v13 else f"_ckpt_{version}")
    if smoke_days and not v13:
        days = [pd.Timestamp(x) for x in smoke_days]; ck_dir = CK.parent / "_smoke_v1_1"; ck_dir.mkdir(exist_ok=True)
    else:
        if v13:  # gate covers smoke days too: any v1.3 weight generation needs the Arch file
            # 主 Agent 2026-10-18 (process, strict): the CLI flag is NOT sufficient for v1.3. Only an Arch-written
            # run-auth file opens the full run. Strategy never creates this file.
            auth = OUT / "ARCH_RUN_AUTH_v1_3.ok"
            txt = auth.read_text(encoding="utf-8").strip() if auth.exists() else ""
            if not txt or "arch" not in txt.lower():
                raise SystemExit(f"v1_3 full run blocked: Arch run-auth file missing or empty: {auth} (do not create it yourself)")
            import hashlib; RUN_AUTH.update({"file": str(auth.relative_to(ROOT)), "sha256": hashlib.sha256(auth.read_bytes()).hexdigest(), "text": txt[:300]})
        elif not arch_cosigned:
            raise SystemExit("v1_1 full rerun not enabled until Arch cosign (pass --arch-cosigned once signed)")
        days = rd if not smoke_days else [pd.Timestamp(x) for x in smoke_days]
    ck_dir.mkdir(exist_ok=True)
    prev = {a: None for a in AUMS}; prev_sl = {a: None for a in AUMS}; out = {}
    for d in days:
        ck = ck_dir / f"{d:%Y%m%d}.pkl"
        if ck.exists() and not smoke_days:
            rec = pickle.load(open(ck, "rb"))
        else:
            t0 = time.time(); D = C.prepare_day(d); rec = {"day": str(d.date()), "w": {}, "sleeves": {}, "log": {}}
            px = None
            if v13 and D is not None:  # v1.3 ①: PIT close on rebalance day, needed before solve
                nm = sorted(set(D["alpha"].index))
                b = C.load_daily_basic_window(nm, d - pd.Timedelta(days=10), d)
                b["trade_date"] = pd.to_datetime(b["trade_date"])
                px = b.sort_values("trade_date").groupby("ts_code")["close"].last()
            rec["exclusions"] = {}; rec["carry_drift"] = {}
            for a in AUMS:
                if D is None:
                    rec["w"][a] = prev[a]; rec["log"][a] = {"status": "NO_DATA_CARRY"}; continue
                w0 = (prev[a] if prev[a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
                excl = []
                if v13:
                    for i in D["alpha"].index:
                        P_ = px.get(i, np.nan); cost = C.lot_round_rule(i) * P_ if np.isfinite(P_) else np.nan
                        if np.isfinite(cost) and cost > C.NAME_CAP[a] * a:
                            excl.append({"date": rec["day"], "aum": a, "instrument": i, "close": float(P_), "lot": C.lot_round_rule(i),
                                         "lot_cost": float(cost), "cap_amount": C.NAME_CAP[a] * a})
                    rec["exclusions"][a] = excl
                w, info = V.solve_v11(D, w0, a, lr, lt[a], exclude=[e["instrument"] for e in excl])
                info["n_excluded"] = len(excl)
                def _carry(info):
                    rec["w"][a] = prev[a]; info["carry"] = "prior_holdings" if prev[a] is not None else "all_cash"
                    if v13 and prev_sl[a] is not None:  # v1.3 ③ carry-day drift
                        rec["carry_drift"][a] = {sv: exposure_drift(x["w"], D) for sv, x in prev_sl[a].items()}
                        pool_ = set(D["alpha"].index)  # v1.3: carried holdings no longer in today's pool (Arch v1.3 cosign P2)
                        for sv, x in prev_sl[a].items():
                            outp = sorted(i for i in x["w"].index if i != C.BALLAST and x["w"][i] > 0 and i not in pool_)
                            rec["carry_drift"][a][sv].update({"carry_n_out_of_pool": len(outp), "carry_out_of_pool_names": ",".join(outp)})
                if w is None:
                    _carry(info); rec["log"][a] = info; continue
                if px is None:
                    nm = sorted(set(D["alpha"].index))
                    b = C.load_daily_basic_window(nm, d - pd.Timedelta(days=10), d)
                    b["trade_date"] = pd.to_datetime(b["trade_date"])
                    px = b.sort_values("trade_date").groupby("ts_code")["close"].last()
                sl = {}
                for sleeve, bf in (("equity_100", 0.0), ("equity80_etf20_510300", C.ETF_BALLAST_FRAC)):
                    sty = V.style_ctx(D, info["slack"]["size_slack"], info["slack"]["ind_slack"]) if v13 else None
                    # v1.3: full-pool wb industry benchmark in the lot repair/top-up (same as solver); industry, style and β checked together
                    wl, li = V.lot_round_greedy(w * (1 - bf), px, a, D["industry"], D["wb"].reindex(D["alpha"].index).fillna(0.0), C.NAME_CAP[a], ballast_frac=bf, style=sty, wb_raw=False)
                    sl[sleeve] = {"w": wl, **li, **exposure_drift(wl, D)}
                bad = sl["equity_100"]["lot_flag"] == "LOT_HARD_FAIL" or (version in ("v1_2", "v1_3") and any(x["lot_flag"] == "LOT_HARD_FAIL" for x in sl.values()))
                if bad:
                    info["status"] = "INFEASIBLE"; info["stage"] = "lot"
                    info["lot_fail_reason"] = ",".join(sorted({("style" if (x.get("style_excess") or 0) > 1e-6 else "names_or_industry") for x in sl.values() if x["lot_flag"] == "LOT_HARD_FAIL"}))
                    _carry(info)
                else:
                    rec["w"][a] = w; rec["sleeves"][a] = sl
                info.update({"n_opt": int((w > 0).sum()), "sum_w_opt": float(w.sum()), "neff_opt": float(1 / (w ** 2).sum()),
                             "min_w_opt": float(w.min()), "max_w_opt": float(w.max()),
                             "one_way": (0.5 * float((w.reindex(w.index.union(prev[a].index)).fillna(0) - prev[a].reindex(w.index.union(prev[a].index)).fillna(0)).abs().sum()) if prev[a] is not None else None),
                             **{f"{k}_{sv}": v for sv, x in sl.items() for k, v in x.items() if k in ("lot_flag", "cash", "n", "style_excess")}})
                rec["log"][a] = info
            rec["log"]["sec"] = round(time.time() - t0, 1)
            pickle.dump(rec, open(ck, "wb"))
        for a in AUMS:
            if rec["w"][a] is not None: prev[a] = rec["w"][a]
            if a in rec.get("sleeves", {}): prev_sl[a] = rec["sleeves"][a]
        out[rec["day"]] = rec["log"]; print(json.dumps({"day": rec["day"], **{str(k): v for k, v in rec["log"].items()}}, default=str), flush=True)
    if smoke_days:
        (ck_dir / "smoke_feasibility.json").write_text(json.dumps(out, indent=1, default=str)); print("SMOKE_DONE"); return
    write_v11_outputs(ck_dir, rd, sess, OUT, version=version)

def phase_smoke(sleeves):
    # T1 (Arch audit): disabled. Canonical A-column NAV = Eng book-smoke output core_x2/book_smoke_{sleeve}_{aum}/nav.csv
    # (read by scripts_eng/core_x2_scorecard.py). Strategy writes weights only.
    raise SystemExit("phase_smoke disabled (T1): Eng runs book-smoke -> core_x2/book_smoke_{sleeve}_{aum}/nav.csv")
    from strategy_hiliq_capadv_b4_x2 import run_smoke
    res = {}
    for sleeve in sleeves:
        for a, tag in AUMS.items():
            p = OUT / f"core_{sleeve}_{tag}.parquet"
            od = OUT / f"smoke_{sleeve}_{tag}"
            r = run_smoke(p, od, str(a)); res[f"{sleeve}_{tag}"] = {k: v for k, v in r.items() if k != "summary"}
            print(sleeve, tag, r.get("ok"), r.get("log"), flush=True)
    (OUT / f"smoke_runs_{int(time.time())}.json").write_text(json.dumps(res, indent=1))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", default="weights")
    ap.add_argument("--sleeves", default="equity80_etf20_510300,equity_100")
    ap.add_argument("--arch-cosigned", action="store_true")
    ap.add_argument("--version", default="v0", choices=["v0", "v1_1", "v1_2", "v1_3"])
    ap.add_argument("--smoke-days", default="", help="comma list; v1_1 feasibility smoke only (no returns)")
    a = ap.parse_args()
    if a.version in ("v1_1", "v1_2", "v1_3"):
        phase_weights_v11([x for x in a.smoke_days.split(",") if x] or None, arch_cosigned=a.arch_cosigned, version=a.version); sys.exit(0)
    if a.phase in ("weights", "all"): phase_weights()
    if a.phase in ("smoke", "all"): phase_smoke(a.sleeves.split(","))
