"""Raw vs hfq diagnostic for leaves 3/7/8/9 (window 2024-01-02→2026-10-09 only). No conclusion changes."""
import sys, glob, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from research.ai_debate_memory_runner import _load_benchmark_closes
from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches
import research.adj_price as A
B = "510300.SH"
braw = _load_benchmark_closes("510300"); braw.index = pd.to_datetime(braw.index)
e = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date", "close_hfq"], filters=[("ts_code", "==", B)])
badj = pd.Series(e.close_hfq.values, index=pd.to_datetime(e.trade_date, format="%Y%m%d")).sort_index()
def leaf_ret(p, adj):
    w = pd.read_parquet(p, columns=["date", "instrument", "target_weight"]); w["date"] = w["date"].astype(str).str[:10]
    W = w.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0); W.index = pd.to_datetime(W.index)
    R = {}
    for i in W.columns:
        if i == B: c = badj if adj else braw
        else:
            c = load_panel_features_x2(i)["close"]; clear_caches()
            if adj: c = A.adj_close(i, c)
        R[i] = pd.to_numeric(c, errors="coerce").reindex(W.index).pct_change(fill_method=None)
    R = pd.DataFrame(R).reindex(columns=W.columns).astype(float).fillna(0)
    return (W.shift(1) * R).sum(axis=1).iloc[1:]
def stats(r, b, rc):
    df = pd.concat([r, b, rc], axis=1, keys=["e", "b", "c"]).dropna()
    X = np.c_[np.ones(len(df)), df.b]
    ce, *_ = np.linalg.lstsq(X, df.e, rcond=None); cc, *_ = np.linalg.lstsq(X, df.c, rcond=None)
    re_, rc_ = df.e - X @ ce, df.c - X @ cc
    nav = (1 + df.e).cumprod(); cagr = lambda s: float((1 + s).prod() ** (252 / len(s)) - 1)
    yr = {str(y): round(float(np.linalg.lstsq(np.c_[np.ones(len(g)), g.b], g.e, rcond=None)[0][0] * 252), 4) for y, g in df.groupby(df.index.year)}
    return dict(cagr=round(cagr(df.e), 4), mdd=round(float((nav / nav.cummax() - 1).min()), 4), beta=round(float(ce[1]), 3),
                alpha=round(float(ce[0] * 252), 4), rho_cap=round(float(np.corrcoef(re_, rc_)[0, 1]), 3), bench_cagr=round(cagr(df.b), 4),
                cap_cagr=round(cagr(df.c), 4), alpha_by_year=yr)
LEAVES_ALL = {"1_earnings_event": "earnings_event", "5_insider_increase": "insider_increase", "6_equity_incentive": "equity_incentive", "3_buyback_cancel": "buyback_cancel", "7_block_trade": "block_trade", "8_unlock_rebound": "unlock_rebound", "9_interim_div_init": "interim_div_init"}
SEL = sys.argv[1].split(",") if len(sys.argv) > 1 else ["3", "7", "8", "9"]
leaves = {k: v for k, v in LEAVES_ALL.items() if k.split("_")[0] in SEL}
cap = sorted(glob.glob(str(ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet")))[-1]
out = {}
rc = {k: leaf_ret(cap, k == "adj") for k in ("raw", "adj")}
for name, k in leaves.items():
    p = sorted(glob.glob(str(ROOT / f"output/ai_factory/g1g5_{k}_daily_weights_*.parquet")))[-1]
    out[name] = dict(path=Path(p).name)
    for mode in ("raw", "adj"):
        r = leaf_ret(p, mode == "adj"); b = (badj if mode == "adj" else braw).pct_change()
        out[name][mode] = stats(r, b, rc[mode])
import resource
out["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
Path(ROOT / f"output/ai_factory/adj_diag_leaves_{''.join(SEL)}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1))
