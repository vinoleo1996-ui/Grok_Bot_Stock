"""Alpha 2026-10-18: reconcile HI_LIQ capacity_adv leg 195620 X2 numbers across bases (LC engine; read-only; live=false)."""
import sys, json, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.leaf_selfcheck_common as LC
from research.leaf_selfcheck_v3 import leaf_topn, metrics
CAP = R/"output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
OLD = sorted((R/"output/strategy_hiliq/legs/_rejected_ind_cap").glob("*capacity_adv*.parquet"))
W = LC._w(CAP); out = {"file": str(CAP.relative_to(R)), "names_per_day": float(W[~W.instrument.map(LC.etf)].groupby("date").size().mean()),
                      "etf_share": float(W[W.instrument.map(LC.etf)].groupby("date").target_weight.sum().mean())}
def run(Wx, tag):
    r = LC._ret(Wx)
    for wn, (a, b) in {"X2_0603": ("2024-06-03", "2026-10-09"), "from_0102": ("2024-01-02", "2026-10-09")}.items():
        x = r[(r.index >= a) & (r.index <= b)]; m = metrics(x); m["yearly"] = {str(y): float((1+x[x.index.year == y]).prod()-1) for y in sorted(set(x.index.year))}
        out[f"{tag}|{wn}"] = m
run(W, "full_25+ETF20")
for t, N in {"60w": 6, "100w": 10}.items():
    lt = leaf_topn(W, N); lw = pd.DataFrame([(d, i, v) for d, s in lt.items() for i, v in s.items()], columns=["date", "instrument", "target_weight"]); run(lw, f"topN_{t}")
for p in OLD: out["old_rejected_file"] = str(p.relative_to(R)); run(LC._w(p), "OLD_rejected_full")
Path(R/"output/alpha/recon_eqinc/capadv_hiliq_basis.json").write_text(json.dumps(out, indent=1, default=float)); print(json.dumps(out, indent=1, default=float))
