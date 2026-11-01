"""Arch read-only smoke (temp dir only). No returns. Does not touch core_x2 official paths."""
import sys, json, pickle, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/"research"))
import optimizer_lambda_calib_sealed as C
import optimizer_core_v1_1 as V
LR, LT = 117.21317483995702, 0.6
K2 = ROOT/"output/strategy_optimizer/core_x2"
AUMS = [600_000, 1_000_000]
def px_for(D, d):
    nm = sorted(set(D["alpha"].index)); b = C.load_daily_basic_window(nm, d - pd.Timedelta(days=10), d)
    b["trade_date"] = pd.to_datetime(b["trade_date"]); return b.sort_values("trade_date").groupby("ts_code")["close"].last()
def check(wl, D, budget, sl, aum):
    pool = D["alpha"].index; wb = D["wb"].reindex(pool).fillna(0); wb = wb/wb.sum(); ind = D["industry"]
    we = wl.drop(C.BALLAST, errors="ignore"); we = we[we > 0]
    gi = lambda w: w.groupby(w.index.map(lambda n: ind.get(n, "_UNK"))).sum()
    gb = gi(wb) * budget; gp = gi(we).reindex(gb.index.union(gi(we).index)).fillna(0); gb = gb.reindex(gp.index).fillna(0)
    box = (C.IND_ACTIVE + sl["ind_slack"]) * budget
    sty = V.style_ctx(D, sl["size_slack"], sl["ind_slack"])
    ez = sum(v*sty["z"][i] for i, v in we.items()) + (1-budget)*sty["zb"] - sty["zb"]
    em = sum(v*sty["m"][i] for i, v in we.items()) + (1-budget)*sty["mb"] - sty["mb"]
    eb = sum(v*sty["b"][i] for i, v in we.items()) + (1-budget)*sty["bb"] - sty["bb"]
    zero_held = [g for g in gb.index if gp[g] == 0 and gb[g] > 0]
    return {"n": int(len(we)), "cash": round(1-float(wl.sum()), 4), "max_name": round(float(we.max()), 4), "name_cap_budget": C.NAME_CAP[aum]*budget,
            "ind_rel_max": round(float((gp-gb).abs().max()), 4), "ind_rel_up_max": round(float((gp-gb).max()), 4), "ind_rel_dn_max": round(float((gb-gp).max()), 4),
            "ind_box_budget": round(box, 4), "ind_abs_max": round(float(gp.max()), 4), "ind_abs_lim": C.IND_ABS*budget,
            "zero_held_inds": [(g, round(float(gb[g]), 4)) for g in zero_held],
            "size": round(ez, 4), "mid": round(em, 4), "beta": round(eb, 4), "sbox": round(sty["sbox"], 3),
            "viol": bool((gp-gb).abs().max() > box+1e-6 or gp.max() > C.IND_ABS*budget+1e-6 or abs(ez) > sty["sbox"]+1e-6 or abs(em) > sty["sbox"]+1e-6 or abs(eb) > C.BETA_BOX+1e-6 or len(we) < 20 or len(we) > 30)}
def run_v13(day, prev_ck):
    V.POOL_STD = True; V.IND_POOL = True
    d = pd.Timestamp(day); D = C.prepare_day(d); px = px_for(D, d); out = {"day": day}
    prev = pickle.load(open(prev_ck, "rb"))
    gbpool = V.pool_ind_bench(D); out["pool_inds_gt_box"] = {g: round(float(v), 4) for g, v in gbpool.items() if v > C.IND_ACTIVE}
    for a in AUMS:
        w0 = (prev["w"][a] if prev["w"][a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
        excl = [i for i in D["alpha"].index if np.isfinite(px.get(i, np.nan)) and C.lot_round_rule(i)*px[i] > C.NAME_CAP[a]*a]
        t0 = time.time(); w, info = V.solve_v11(D, w0, a, LR, LT, exclude=excl); r = {"n_excl": len(excl), "solve": {k: info.get(k) for k in ("status","stage","K","tries","slack","cvx")}, "sec": round(time.time()-t0,1)}
        if w is not None:
            # solver-level industry check vs full-pool wb (pre-rounding)
            ind = D["industry"]; gp = w.groupby(w.index.map(lambda n: ind.get(n, "_UNK"))).sum().reindex(gbpool.index).fillna(0)
            r["solver_ind_rel_max"] = round(float((gp - gbpool).abs().max()), 4); r["solver_ind_abs_max"] = round(float(gp.max()), 4)
            r["solver_zero_held_inds"] = [(g, round(float(gbpool[g]), 4)) for g in gbpool.index if gp[g] == 0 and gbpool[g] > 0]
            for sv, bf in (("equity_100", 0.0), ("equity80_etf20_510300", C.ETF_BALLAST_FRAC)):
                sty = V.style_ctx(D, info["slack"]["size_slack"], info["slack"]["ind_slack"])
                wl, li = V.lot_round_greedy(w*(1-bf), px, a, D["industry"], D["wb"].reindex(D["alpha"].index).fillna(0.0), C.NAME_CAP[a], ballast_frac=bf, style=sty, wb_raw=False)
                r[sv] = {"lot_flag": li["lot_flag"], **check(wl, D, 1-bf, info["slack"], a)}
        out[str(a)] = r
    return out
def repro_v12(day, prev_day):
    V.POOL_STD = True; V.IND_POOL = False
    d = pd.Timestamp(day); D = C.prepare_day(d); px = px_for(D, d)
    ck = pickle.load(open(K2/f"_ckpt_v1_2/{day.replace('-','')}.pkl", "rb")); pv = pickle.load(open(K2/f"_ckpt_v1_2/{prev_day}.pkl", "rb")); res = {"day": day}
    for a in AUMS:
        w0 = pv["w"][a].reindex(D["alpha"].index).fillna(0.0); w, info = V.solve_v11(D, w0, a, LR, LT)
        r = {"status": info["status"], "ck_status": ck["log"][a].get("status")}
        if w is not None and ck["log"][a].get("status") == "OK":
            r["max_abs_diff_w"] = float((w.reindex(ck["w"][a].index.union(w.index)).fillna(0) - ck["w"][a].reindex(ck["w"][a].index.union(w.index)).fillna(0)).abs().max())
            for sv, bf in (("equity_100", 0.0), ("equity80_etf20_510300", C.ETF_BALLAST_FRAC)):
                wl, li = V.lot_round_greedy(w*(1-bf), px, a, D["industry"], D["wb"].reindex(D["alpha"].index).fillna(0.0), C.NAME_CAP[a], ballast_frac=bf, style=None, wb_raw=False)
                ref = ck["sleeves"][a][sv]["w"]; u = wl.index.union(ref.index)
                r[f"lot_diff_{sv}"] = float((wl.reindex(u).fillna(0) - ref.reindex(u).fillna(0)).abs().max())
        res[str(a)] = r
    return res
if __name__ == "__main__":
    res = {"v12_repro": repro_v12("2026-07-31", "20260630")}
    print(json.dumps(res, default=str), flush=True)
    A = K2/"_archive_v1_3_pre_ruling/_ckpt_v1_3"
    for day, prev in (("2026-06-30", "20260529"), ("2025-11-28", "20251031")):
        res[day] = run_v13(day, A/f"{prev}.pkl"); print(json.dumps(res[day], default=str, ensure_ascii=False), flush=True)
    Path("/workspace/scratch_arch_v13smoke/smoke_result.json").write_text(json.dumps(res, default=str, ensure_ascii=False, indent=1))
