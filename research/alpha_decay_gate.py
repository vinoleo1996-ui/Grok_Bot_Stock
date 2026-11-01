"""Leaf alpha-decay gate v1 (prereg docs/v2/ALPHA_DECAY_GATE_PREREG_ZH.md, sha256 eecc84ba...c13b).
Research-grade; promotion_approved=false; live=false. Never changes paper status.

API:
    evaluate_weights(weights_path) -> dict   # decay_gate outcome for one daily weights parquet
    evaluate_returns(gross: pd.Series, turnover: pd.Series, bench: pd.Series) -> dict
CLI:
    python3 research/alpha_decay_gate.py <weights.parquet> [...]
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
B = "510300.SH"; COST = 0.00175; WIN = 252; MINH = 126; N_DECL = 3; TO_MAX = 0.20; WARN = 0.01
PREREG_SHA = "eecc84ba7774939e19a9428f578aec2a72711a6021d4eb6192301ed5be34c13b"
_bench = None; _cache: dict = {}


def bench() -> pd.Series:
    global _bench
    if _bench is None:
        e = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date", "close_hfq"], filters=[("ts_code", "==", B)])
        _bench = pd.Series(e.close_hfq.values, index=pd.to_datetime(e.trade_date, format="%Y%m%d")).sort_index()
    return _bench


def _close(i):
    if i == B: return bench()
    if i not in _cache:
        from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches
        import research.adj_price as AP
        c0 = load_panel_features_x2(i)["close"]; clear_caches()
        c0 = pd.to_numeric(c0, errors="coerce"); c0.index = pd.to_datetime(c0.index)
        _cache[i] = AP.adj_close(i, c0)
    return _cache[i]


def gross_and_turnover(weights_path):
    d = pd.read_parquet(weights_path, columns=["date", "instrument", "target_weight"])
    d["date"] = pd.to_datetime(d["date"].astype(str).str[:10])
    P = d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    R = pd.DataFrame({i: _close(i).reindex(P.index).pct_change(fill_method=None) for i in P.columns}).fillna(0)
    g = (P.shift(1) * R).sum(axis=1).iloc[1:]
    to = P.diff().abs().sum(axis=1).iloc[1:]
    return g, to


def _alpha(y, x):
    X = np.c_[np.ones(len(x)), x]; cf, *_ = np.linalg.lstsq(X, y, rcond=None); return float(cf[0] * 252), float(cf[1])


def evaluate_returns(gross, turnover, b=None):
    b = bench().pct_change() if b is None else b
    df = pd.DataFrame({"g": gross, "to": turnover}).join(b.rename("b"), how="inner").dropna()
    df["n"] = df.g - COST * df.to
    out = dict(prereg_sha256=PREREG_SHA, window=[str(df.index[0].date()), str(df.index[-1].date()), len(df)] if len(df) else None)
    if len(df) < MINH:
        out.update(outcome="INSUFFICIENT", reasons=["history<126"]); return out
    idx = df.index
    def a_at(t):
        h = df.loc[:t].iloc[-WIN:]
        return None if len(h) < MINH else _alpha(h.n.values, h.b.values)[0]
    qe = pd.Series(idx, index=idx).groupby(idx.to_period("Q")).max()
    pts = [(str(pd.Timestamp(t).date()), a_at(pd.Timestamp(t))) for t in qe.values]
    if pts[-1][0] != str(idx[-1].date()): pts.append((str(idx[-1].date()), a_at(idx[-1])))
    pts = [(t, a) for t, a in pts if a is not None and t >= "2024-10-01"]
    run = 0
    for k in range(1, len(pts)):
        run = run + 1 if pts[k][1] < pts[k - 1][1] else 0
    latest = pts[-1][1] if pts else a_at(idx[-1])
    h = df.iloc[-WIN:]; from quantlab.metrics import PERIODS as _QP; ny = len(h) / _QP   # Eng 2026-10-14: CAGR annualisation 244 (WIN=252 window and alpha x252 are prereg-locked, unchanged)
    net_cagr = float((1 + h.n).prod() ** (1 / ny) - 1)
    b_cagr = float(((1 + h.b).prod() * (1 - COST)) ** (1 / ny) - 1)
    to_mean = float(h.to.mean()); beta = _alpha(h.n.values, h.b.values)[1]
    reasons = []
    if latest < 0: reasons.append("latest_alpha<0")
    if run >= N_DECL: reasons.append(f"alpha_declined_{run}q")
    if to_mean > TO_MAX: reasons.append("H1_turnover>20%")
    if net_cagr <= b_cagr: reasons.append("H2_net_cagr<=510300")
    if reasons: oc = "DECAY_DOWNGRADE"
    elif latest < WARN or run >= 2:
        oc = "DECAY_WATCH"; reasons = (["latest_alpha<1%"] if latest < WARN else []) + ([f"alpha_declined_{run}q"] if run >= 2 else [])
    else: oc = "KEEP"
    out.update(outcome=oc, reasons=reasons, latest_resid_alpha=latest, beta=beta, consecutive_declines=run,
               quarterly_alpha=[[t, round(a, 4)] for t, a in pts], turnover_mean_2s=to_mean, net_cagr=net_cagr,
               bench_net_cagr=b_cagr, short_history=len(h) < WIN)
    return out


def evaluate_weights(weights_path):
    g, to = gross_and_turnover(weights_path)
    r = evaluate_returns(g, to); r["weights_path"] = str(weights_path); return r


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(evaluate_weights(p), ensure_ascii=False, default=float, indent=1))
