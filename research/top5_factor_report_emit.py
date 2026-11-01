"""Emit Web dashboard factor report output/top5_factor_report/<YYYYMMDD>/summary.json for leaves 11-14.
Signal = leaf weight residualized (SW L1 / log float mcap / rolling beta) and z-scored per day on PIT pool (alpha_combo_marginal.resid_z);
fwd = 20-session adj close return; IC Pearson, RankIC Spearman daily mean; ICIR = mean/std (daily, unannualized);
q1/q5 = mean 20d fwd return of bottom/top quintile; long_short = q5-q1; turnover = two-sided daily TO of weights (alpha_decay_gate).
trusted = lookahead PASS and not untradable. Research-grade; live=false."""
import sys, json, datetime
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_combo_marginal as C, research.leaf_selfcheck_v3 as V3
LEAVES = sys.argv[1:] or ["report_rc_allup", "analyst_recoverage", "stk_surv", "insurer_surv"]  # argv leaves are merged into existing summary
out = []
for lf in LEAVES:
    Z = C.resid_z(C.sig(V3.wfile(lf))); F = C.ctx()["F"]; ic, ric, q1, q5 = [], [], [], []
    for d in Z.index:
        z, f = Z.loc[d], F.loc[d]; ok = z.notna() & f.notna()
        if ok.sum() < 30: continue
        z, f = z[ok], f[ok]; ic.append(z.corr(f)); ric.append(z.rank().corr(f.rank()))
        q = pd.qcut(z.rank(method="first"), 5, labels=False); q1.append(f[q == 0].mean()); q5.append(f[q == 4].mean())
    rp = ROOT / f"output/ai_factory/leaf_reports/{lf}"
    v2 = json.load(open(rp / "selfcheck_v2.json")); la = json.load(open(rp / "lookahead_check.json"))
    ric_s = pd.Series(ric)
    out.append(dict(leaf=lf, horizon=20, ic=float(np.nanmean(ic)), rank_ic=float(ric_s.mean()), icir=float(ric_s.mean() / ric_s.std()),
                    q1_ret=float(np.nanmean(q1)), q5_ret=float(np.nanmean(q5)), long_short=float(np.nanmean(q5) - np.nanmean(q1)),
                    turnover=float(v2["cost"]["to_2s_mean"]), trusted=bool(la["status"] == "PASS" and not v2["cost"]["untradable"]),
                    lookahead=la["status"], untradable=bool(v2["cost"]["untradable"]), n_days=len(ric)))
day = datetime.date.today().strftime("%Y%m%d"); o = ROOT / f"output/top5_factor_report/{day}"; o.mkdir(parents=True, exist_ok=True)
sp = o / "summary.json"
if len(sys.argv) > 1 and sp.exists():
    keep = [x for x in json.load(open(sp))["leaves"] if x["leaf"] not in LEAVES]; out = keep + out
res = dict(generated_at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"), window=[C.START, C.END], method=__doc__,
           leaves=out, promotion_approved=False, live=False)
(o / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(o / "summary.json")
for r in out: print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
