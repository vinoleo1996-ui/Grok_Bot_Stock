"""Arch P1-T3 rescore: v1.1 INFEASIBLE logic at FROZEN λ (unchanged). Sealed window only; no X2 returns."""
import json, sys, time, gc
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import optimizer_lambda_calib_sealed as C

def main():
    meta = json.loads((C.OUT_DIR / "calib_meta.json").read_text())
    lam_risk = float(meta["lambda_risk"])
    lam_t = {600_000: float(meta["lambda_turn_60w"]), 1_000_000: float(meta["lambda_turn_100w"])}
    import pandas as pd
    days = [pd.Timestamp(d) for d in meta["rebalance_days"]]
    data = []
    for d in days:
        D = C.prepare_day(d)
        if D is not None:
            data.append(D)
        gc.collect()
    print("prepared", len(data), "RSS", C.rss_mb(), flush=True)
    out = {}
    for aum in (600_000, 1_000_000):
        w_prev = None; held = {}; rows = []
        for D in data:
            w0 = (w_prev if w_prev is not None else D["wb"].copy()).reindex(D["alpha"].index).fillna(0.0)
            r = C.two_step_polish(D["alpha"], D["wb"], w0, D["industry"], D["ln_mcap"], D["B"], D["F"],
                                  D["delta"], D["betas"], aum=aum, lambda_risk=lam_risk, lambda_turn=lam_t[aum])
            fn = (r.info or {}).get("final_n")
            rows.append({"day": str(D["day"].date()), "status": r.status, "reason": (r.info or {}).get("reason"),
                         "final_n_raw": fn, "sum_w": (r.info or {}).get("sum_w")})
            if r.w is not None:
                w_prev = r.w[r.w > 0]
            if w_prev is not None:
                held[D["day"]] = w_prev
        turns = C.one_way_turnover_series(held)
        n_ok = sum(x["status"] == "OK" for x in rows)
        ns = [x["final_n_raw"] for x in rows if x["final_n_raw"] is not None]
        out[str(aum)] = {
            "lambda_turn": lam_t[aum], "n_days": len(rows), "n_ok": n_ok, "n_infeasible": len(rows) - n_ok,
            "feasible_rate": n_ok / max(len(rows), 1),
            "n_days_gt30_raw": sum(n > 30 for n in ns), "n_days_lt20_raw": sum(n < 20 for n in ns),
            "n_step2_failed": sum(x["reason"] == "step2_failed" for x in rows),
            "carry_forward_turnover_median_one_way": float(np.median(turns)) if turns else None,
            "turn_target_one_way": C.TURN_FALLBACK_ONE_WAY,
            "turn_band_hit_note": "target 0.25 one-way (monthly two-way 50% fallback)",
            "days": rows,
        }
        print(aum, {k: v for k, v in out[str(aum)].items() if k != "days"}, flush=True)
    res = {"version": "v1.1", "source_meta": "calib_meta.json", "lambda_risk": lam_risk,
           "lambda_values_changed": False, "x2_returns_used": False, "window": meta["window"],
           "rule_zh": "step2 失败或最终持仓数∉[20,30] → INFEASIBLE，沿用上期权重（v0 回退 step1 大篮子作废）",
           "v0_infeasible_0_status": "MISREPORTED", "per_aum": out, "peak_rss_mb": C.rss_mb(),
           "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    (C.OUT_DIR / "calib_meta_v1_1.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
main()
