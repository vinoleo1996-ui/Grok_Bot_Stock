"""Disclosure: leaf book (full20, fund-engine T+1 net) excess vs pool equal-weight (size-neutral-ish) benchmark + vs 512100(CSI1000 ETF) if present. Read-only."""
import sys, numpy as np, pandas as pd, resource
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R)); import research.g1g5_fund_resid_alpha as FE
leafdir, stamps = sys.argv[1], dict(a.split("=") for a in sys.argv[2:])  # e.g. HILIQ_x2=eval_weights_..._stamp
out = {}
for key, fn in stamps.items():
    uni, wn = key.split("_"); s, e = FE.WIN[wn]; col = FE.UCOL[uni]
    ew = []
    for y in range(int(s[:4]), int(e[:4])+1):
        P = pd.read_parquet(FE.PC/f"cs_panel_{y}.parquet", columns=["date","ret",col]); P = P[P[col]]
        ew.append(P.groupby("date").ret.mean().clip(-.2, .2))
    ew = pd.concat(ew); ew.index = pd.to_datetime(ew.index); ew = ew.shift(-0)
    W = pd.read_parquet(R/f"output/ai_factory/{leafdir}/{fn}.parquet", columns=["date","instrument","target_weight"]); W = W[W.target_weight > 0]; W["date"] = pd.to_datetime(W.date)
    r, _ = FE.book_ret(W, s, e); b = ew.reindex(r.index).fillna(0)
    be = float(np.cov(r, b)[0,1]/b.var()); res = r-be*b
    n = len(r); navb = (1+b).prod()
    out[key] = dict(leaf_cagr244=float((1+r).prod()**(244/n)-1), poolEW_cagr244=float(navb**(244/n)-1), beta_vs_poolEW=be, resid_alpha_vs_poolEW_244=float(res.mean()*244),
                    t=float(res.mean()/res.std()*np.sqrt(n)), by_year={str(y): round(float(g.mean()*244), 4) for y, g in res.groupby(res.index.year)})
    print(key, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out[key].items()}, f"rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f}", flush=True)
    FE._RET.clear()
import json; Path(R/f"output/ai_factory/{leafdir}/poolew_excess.json").write_text(json.dumps(out, indent=1))
