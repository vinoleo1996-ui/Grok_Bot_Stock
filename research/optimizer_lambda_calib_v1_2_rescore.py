"""Eng C5: v1.2 rescore of calib (24 sealed days, FROZEN λ unchanged). Uses Strategy's v1.2 path
(optimizer_core_v1_1.POOL_STD=True, BETA_POOL=True, lot rounding both sleeves, LOT_HARD_FAIL on either).
No parameter/HARD changes. Sealed only; no returns. live=false."""
import json, sys, time, gc
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import optimizer_lambda_calib_sealed as C
import optimizer_core_v1_1 as V
import optimizer_core_x2_run as R
V.POOL_STD = True; R.BETA_POOL = True

def main():
    meta = json.loads((C.OUT_DIR / "calib_meta.json").read_text())
    lr, lt = R.frozen_lambdas()
    days = [pd.Timestamp(d) for d in meta["rebalance_days"]]
    prev = {a: None for a in R.AUMS}; rows = {a: [] for a in R.AUMS}; held = {a: {} for a in R.AUMS}
    for d in days:
        D = C.prepare_day(d)
        if D is None:
            for a in R.AUMS: rows[a].append({"day": str(d.date()), "status": "NO_DATA_CARRY"})
            continue
        px = None
        for a in R.AUMS:
            w0 = (prev[a] if prev[a] is not None else D["wb"]).reindex(D["alpha"].index).fillna(0.0)
            w, info = V.solve_v11(D, w0, a, lr, lt[a])
            row = {"day": str(d.date()), "status": info["status"], "stage": info.get("stage"), "K": info.get("K"),
                   "size_slack": (info.get("slack") or {}).get("size_slack"), "ind_slack": (info.get("slack") or {}).get("ind_slack")}
            if w is not None:
                if px is None:
                    b = C.load_daily_basic_window(sorted(D["alpha"].index), d - pd.Timedelta(days=10), d)
                    b["trade_date"] = pd.to_datetime(b["trade_date"]); px = b.sort_values("trade_date").groupby("ts_code")["close"].last()
                for sv, bf in (("equity_100", 0.0), ("equity80_etf20_510300", C.ETF_BALLAST_FRAC)):
                    wl, li = V.lot_round_greedy(w * (1 - bf), px, a, D["industry"], D["wb"], C.NAME_CAP[a], ballast_frac=bf)
                    ex = R.exposure_drift(wl, D)
                    row.update({f"lot_{sv}": li["lot_flag"], f"n_{sv}": li["n"], f"beta_drift_{sv}": ex["beta_drift"],
                                f"size_drift_{sv}": ex["size_drift"], f"ind_active_max_{sv}": ex["ind_active_max"]})
                if any(row.get(f"lot_{sv}") == "LOT_HARD_FAIL" for sv in ("equity_100", "equity80_etf20_510300")):
                    row["status"] = "INFEASIBLE"; row["stage"] = "lot"
                else:
                    prev[a] = w
            if prev[a] is not None: held[a][d] = prev[a]
            rows[a].append(row)
        print(d.date(), {a: rows[a][-1]["status"] for a in R.AUMS}, "RSS", round(C.rss_mb()), flush=True)
        del D; gc.collect()
    out = {}
    for a in R.AUMS:
        rs = rows[a]; ok = [r for r in rs if r["status"] == "OK"]
        turns = C.one_way_turnover_series(held[a])
        f = lambda k: [r[k] for r in ok if r.get(k) is not None]
        out[str(a)] = {"lambda_turn": lt[a], "n_days": len(rs), "n_ok": len(ok), "feasible_rate": len(ok) / max(len(rs), 1),
            "n_inf_step2": sum(r.get("stage") == "step2" for r in rs), "n_inf_lot": sum(r.get("stage") == "lot" for r in rs),
            "n_inf_other": sum(r["status"] != "OK" and r.get("stage") not in ("step2", "lot") for r in rs),
            "ind_slack_pp_max": 100 * max(f("ind_slack") or [0]), "ind_slack_days": sum(x > 0 for x in f("ind_slack")),
            "size_slack_sigma_max": max(f("size_slack") or [0]), "size_slack_days": sum(x > 0 for x in f("size_slack")),
            "beta_drift_abs_max": max([abs(x) for sv in ("equity_100", "equity80_etf20_510300") for x in f(f"beta_drift_{sv}")] or [0]),
            "beta_box": C.BETA_BOX, "K_range": [min(f("K") or [0]), max(f("K") or [0])],
            "turnover_median_one_way": float(np.median(turns)) if turns else None, "turn_target_one_way": C.TURN_FALLBACK_ONE_WAY,
            "days": rs}
        print(a, {k: v for k, v in out[str(a)].items() if k != "days"}, flush=True)
    res = {"version": "v1.2", "solver": "optimizer_core_v1_1.solve_v11 POOL_STD=True + BETA_POOL + dual-sleeve LOT_HARD_FAIL",
           "lambda_risk": lr, "lambda_values_changed": False, "hard_changed": False, "x2_returns_used": False,
           "window": meta.get("window"), "per_aum": out, "peak_rss_mb": C.rss_mb(), "live": False,
           "note_zh": "v1.2 逻辑重报；calib_meta_v1_1.json 为旧求解器口径诊断", "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    (C.OUT_DIR / "calib_meta_v1_2.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str) + "\n")
main()
