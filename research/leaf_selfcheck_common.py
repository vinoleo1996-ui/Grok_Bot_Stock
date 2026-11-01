"""Leaf self-check v2 (common). Research-grade; live=false; promotion=false; no Book-Smoke.
Components (doc: docs/v2/AI_LEAF_SELFCHECK_V2_RECEIPT_ZH.md):
 (a) alpha_decay_gate.evaluate_weights (constants untouched).
 (b) cost: two-sided daily turnover TO=sum|dw| ; net = gross - COST*TO, COST = alpha_decay_gate.COST (0.00175 / unit TO,
     prereg docs/v2/ALPHA_DECAY_GATE_PREREG_ZH.md; strategy_v1 Book-Smoke approx 0.0016 used in wf_screen is close).
     UNTRADABLE if TO_mean > 0.20/day (= decay gate H1) OR (gross excess vs 510300 > 0 and annual cost drag > 50% of it)
     OR (gross excess <= 0 and cost drag > 1%/yr).
 (c) portfolio gates vs capacity_adv alone at 60w(N=6)/100w(N=10), conc v2 topN merged cap 6%, adj prices, gross:
     CURRENT: cap80+leaf20 CAGR>cap AND MDD>=cap (shallower) both tiers.
     A: de-beta leaf then stack (return-level estimate): r = 0.8*r_capN + 0.2*(r_510300 + r_leaf - beta_leaf*r_510300);
        CAGR and MDD both better than r_capN both tiers. beta full-sample (in-sample).
     B: stack as-is (= CURRENT portfolio): Calmar better both tiers AND MDD >= -15% both tiers.
 2026-10-14 Arch audit fix (#4/#5, docs/v2/ARCH_INTERNAL_AUDIT_20261014_ZH.md; response docs/v2/AI_ARCH_AUDIT_RESPONSE_ZH.md):
  - portfolio-gate returns are NET of COST*TO and T+1: weight dated T fills at next open (Eng fill=next_open):
    r_t = (1 + sum H_{t-1}*overnight_t) * (1 + sum H_t*intraday_t) - 1 - COST*sum|H_t - H_{t-1}|, H_t = W_{t-1}.
    Adj open = raw open * (adj_close/raw close); ETFs open_hfq/close_hfq. Halted day (no open): open := prev close.
    No limit-up/down fill block, no participation cap (still approximation; Eng X2 is final).
  - close returns via quantlab.platform.strategy_feed.close_to_close_returns (ffill inside: halt move booked on resume).
  - A-arm beta: rolling 120 sessions (min 60) on leaf net returns vs 510300, estimated through t-1 only (PIT).
  - (b) cost section keeps alpha_decay_gate numbers (frozen) and adds net_cagr_t1 from the fixed engine.
"""
from __future__ import annotations
import sys, json, resource
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_decay_gate as ADG
CAP_ADV = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
BAL = "510300.SH"; etf = lambda i: i[:2] in ("51", "56", "58", "15")
TO_MAX, DRAG_FRAC, DRAG_ABS = 0.20, 0.5, 0.01


def _w(p):
    d = pd.read_parquet(p, columns=["date", "instrument", "target_weight"]); d["date"] = d["date"].astype(str).str[:10]
    return d[d.target_weight > 0]


_PX: dict = {}


def _px(i):
    """(adj_open, adj_close) series for instrument i."""
    if i not in _PX:
        if etf(i):
            e = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["trade_date", "open_hfq", "close_hfq"], filters=[("ts_code", "==", i)])
            ix = pd.to_datetime(e.trade_date, format="%Y%m%d"); o = pd.Series(e.open_hfq.values, ix).sort_index(); c = pd.Series(e.close_hfq.values, ix).sort_index()
        else:
            from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches
            f = load_panel_features_x2(i); clear_caches(); f.index = pd.to_datetime(f.index)
            c0 = pd.to_numeric(f["close"], errors="coerce"); o0 = pd.to_numeric(f["open"], errors="coerce")
            c = ADG._close(i); fac = (c / c0.reindex(c.index)); o = o0.reindex(c.index) * fac
        _PX[i] = (o, c)
    return _PX[i]


def _ret(W: pd.DataFrame, net: bool = True) -> pd.Series:
    """T+1 next-open, net-of-cost daily book return (see module doc)."""
    from quantlab.platform.strategy_feed import close_to_close_returns
    P = W.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    P.index = pd.to_datetime(P.index)
    C = pd.DataFrame({i: _px(i)[1] for i in P.columns}).reindex(P.index)
    O = pd.DataFrame({i: _px(i)[0] for i in P.columns}).reindex(P.index)
    cc = close_to_close_returns(C)
    Cf = C.ffill(limit_area="inside"); O = O.where(O.notna() & C.notna(), Cf.shift(1))
    on = (O / Cf.shift(1) - 1).where(cc.notna(), 0.0).fillna(0.0)
    intra = ((1 + cc.fillna(0)) / (1 + on) - 1).fillna(0.0)
    H = P.shift(1).fillna(0)
    r = (1 + (H.shift(1).fillna(0) * on).sum(axis=1)) * (1 + (H * intra).sum(axis=1)) - 1
    if net: r = r - ADG.COST * H.diff().abs().sum(axis=1).fillna(H.abs().sum(axis=1))
    return r.iloc[2:]


def _overlay(mix: dict, N: int) -> pd.DataFrame:
    G = {k: {d: g.set_index("instrument").target_weight for d, g in _w(p).groupby("date")} for k, p in mix.items()}
    days = sorted(set.intersection(*[set(v) for v in G.values()])); rows = []
    for d in days:
        agg = {}
        for k, (p) in mix.items():
            m = WMIX[k]; w = G[k][d] * m
            e = w[[etf(i) for i in w.index]]; st = w.drop(e.index)
            for i, v in e.items(): agg[i] = agg.get(i, 0) + v
            if len(st):
                keep = st.sort_values(ascending=False).head(N); keep = keep * st.sum() / keep.sum()
                for i, v in keep.items(): agg[i] = agg.get(i, 0) + v
        for i in list(agg):
            if not etf(i) and agg[i] > 0.06: agg[BAL] = agg.get(BAL, 0) + agg[i] - 0.06; agg[i] = 0.06
        t = sum(agg.values()); rows += [(d, i, v / t) for i, v in agg.items()]
    return pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])


WMIX: dict = {}


def _m(r):
    from quantlab import metrics as QM   # Eng 2026-10-14: unified 244-day annualisation (was 252)
    nav = (1 + r).cumprod(); c = QM.cagr_from_returns(r); md = float((nav / nav.cummax() - 1).min())
    return dict(cagr=c, mdd=md, calmar=QM.calmar(c, md))


def evaluate(weights_path, gates=True) -> dict:
    p = Path(weights_path)
    out = dict(weights_path=str(p), decay=ADG.evaluate_weights(p))
    g, to = ADG.gross_and_turnover(p); b = ADG.bench().pct_change().reindex(g.index).fillna(0)
    from quantlab.metrics import PERIODS as _QP, cagr_from_returns as _cg
    cg = lambda r: _cg(r)
    net = g - ADG.COST * to
    gx = cg(g) - cg(b); drag = float(ADG.COST * to.mean() * _QP)
    reasons = []
    if to.mean() > TO_MAX: reasons.append("TO>20%/日")
    if gx > 0 and drag > DRAG_FRAC * gx: reasons.append("成本拖累>毛超额一半")
    if gx <= 0 and drag > DRAG_ABS: reasons.append("无毛超额且成本拖累>1%/年")
    out["cost"] = dict(cost_per_unit_to=ADG.COST, to_2s_mean=float(to.mean()), gross_cagr=cg(g), net_cagr=cg(net), bench_cagr=cg(b),
                       gross_excess=gx, cost_drag_ann=drag, untradable=bool(reasons), reasons=reasons)
    _n = _ret(_w(p))
    out["cost"]["net_cagr_t1"] = _cg(_n)
    if gates:
        gl = _ret(_w(p)); bl = b.reindex(gl.index).fillna(0)
        beta_s = (gl.rolling(120, min_periods=60).cov(bl) / bl.rolling(120, min_periods=60).var()).shift(1)
        res = {}
        for tier, N in (("60w", 6), ("100w", 10)):
            WMIX.clear(); WMIX.update(cap=1.0); rc = _ret(_overlay({"cap": CAP_ADV}, N))
            WMIX.clear(); WMIX.update(cap=0.8, leaf=0.2); ro = _ret(_overlay({"cap": CAP_ADV, "leaf": p}, N))
            ix = rc.index.intersection(ro.index).intersection(gl.index); ix = ix[beta_s.reindex(ix).notna().values]; rc, ro = rc[ix], ro[ix]
            ra = 0.8 * rc + 0.2 * (bl[ix] + gl[ix] - beta_s[ix] * bl[ix])
            mc, mo, ma = _m(rc), _m(ro), _m(ra)
            res[tier] = dict(cap=mc, overlay=mo, A_debeta=ma,
                             current=bool(mo["cagr"] > mc["cagr"] and mo["mdd"] >= mc["mdd"]),
                             A=bool(ma["cagr"] > mc["cagr"] and ma["mdd"] >= mc["mdd"]),
                             B=bool(mo["calmar"] is not None and mc["calmar"] is not None and mo["calmar"] > mc["calmar"] and mo["mdd"] >= -0.15))
        res["beta_leaf_rolling120_median"] = float(beta_s.median()); res["engine"] = "T+1 next_open, net COST*TO, close_to_close_returns, rolling PIT beta"
        res["verdict"] = {k: bool(res["60w"][k] and res["100w"][k]) for k in ("current", "A", "B")}
        out["portfolio_gates"] = res
    out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(json.dumps(evaluate(a, gates="capacity_adv" not in a), ensure_ascii=False, default=float, indent=1))
