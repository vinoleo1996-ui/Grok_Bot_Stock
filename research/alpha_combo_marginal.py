"""CMC per docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md §1 (Alpha-owned thresholds; AI produces data, no verdict).
B0 = B4 paper book for IC combo; tier nav baseline under hiliq = capacity_adv HI_LIQ book-smoke (主 Agent 2026-10-18 00:54 ET), b4 = diagnostic (capacity_adv/earnings_event/insider_increase 50/25/25, current paper weights);
B1 = 0.8*B0 + 0.2*leaf (leaf top-N 6/10, merged single name <=6%, overflow 510300).
Signals: leg/leaf weight per stock-day (event-holding signal); cross-sectional OLS residual vs SW L1 dummies, log float mcap,
rolling-120d beta (and, for candidate, the three B0 leg signals); z-scored per day on the PIT pool
(universe mask in_universe that day: --universe hiliq [default, gate] = HI_LIQ_V1.1; fulla = FULLA_V1 [diagnostic]).
Arch P1 2026-10-14: top300/mid_large default removed (2026-10-17: hiliq also swaps B0 legs/B4 tracks to HI_LIQ_V1.1 artefacts). Significance disclosure (thresholds unchanged): ic_t_naive, ic_t_neff (n/h), ic_t_hac (Newey-West Bartlett, lag=h-1). Combo z: B0 = .5 z_cap + .25 z_ee + .25 z_ins; B1 = .8*B0 + .2*z_leaf.
Metrics: RankIC vs 20d fwd adj return (daily), ICIR full + rolling-252 median, net ΔCAGR/ΔMDD (17.5bp/unit TO) per tier,
yearly ΔCAGR, rho(leaf resid, B0 combo). Window = Eng X2 smoke 2024-06-03..2026-10-09. promotion=false; live=false."""
from __future__ import annotations
import sys, json, os, argparse
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_decay_gate as ADG
import research.leaf_selfcheck_v3 as V3
AF = ROOT / "output/ai_factory"
LEGS = {"capacity_adv": AF / "g1g5_capacity_adv_daily_weights_paper_20261013_r2.parquet",
        "earnings_event": AF / "g1g5_earnings_event_daily_weights_20261014_111825.parquet",
        "insider_increase": AF / "g1g5_insider_increase_daily_weights_20261014_111825.parquet"}
HL = ROOT / "output/strategy_hiliq/legs"
# 2026-10-17 Alpha: hiliq (gate) uses HI_LIQ_V1.1 legs + HI_LIQ B4 tracks (no top300/mid_large artefacts); fulla keeps the ai_factory legs (diagnostic).
LEGS_BY_UNIVERSE = {"hiliq": {"capacity_adv": HL / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
                              "earnings_event": HL / "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
                              "insider_increase": HL / "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet"},
                    "fulla": LEGS}
# 主 Agent ruling 2026-10-18 00:54 ET: HI_LIQ leaf CMC/GATE_V3 baseline = capacity_adv HI_LIQ standalone, book-smoke basis
# (Strategy X2 target weights; -0.6%/-29.9% @60w, 1.7%/-33.0% @100w). B4 is diagnostic only. Mandatory parallel disclosure: excess vs HI_LIQ pool-EW.
CAPADV_BOOK_TRACKS = {"60w": ROOT / "output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK/target_weights.parquet",
                      "100w": ROOT / "output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK/target_weights.parquet"}
BASE = os.environ.get("ALPHA_CMC_BASE", "capadv")  # capadv (gate default under hiliq) | b4 (diagnostic)


def _load_track(path) -> pd.DataFrame:
    b = pd.read_parquet(path)
    if "target_weight" not in b.columns:  # book-smoke format: session, instrument_id (sh.600000), weight
        b = b.rename(columns={"session": "date", "weight": "target_weight"})
        b["instrument"] = b["instrument_id"].str.split(".").map(lambda x: f"{x[1]}.{x[0].upper()}")
    b = b[["date", "instrument", "target_weight"]].copy(); b["date"] = b["date"].astype(str).str[:10]
    return b[b.target_weight > 0]


def pool_ew() -> pd.Series:
    """HI_LIQ (or FULLA) pool equal-weight daily return (close-to-close, clipped ±20%, no cost) — disclosure benchmark."""
    c = ctx(); R = c["R"]; out = {}
    for d in R.index:
        m = c["mem"].get(d.strftime("%Y-%m-%d"))
        if m: out[d] = R.loc[d, [i for i in c["U"] if i in m]].clip(-.2, .2).mean()
    return pd.Series(out).dropna()


def vs_pool_ew(r: pd.Series, ew: pd.Series) -> dict:
    b = ew.reindex(r.index).fillna(0.0); n = len(r)
    be = float(np.cov(r, b)[0, 1] / b.var()) if b.var() > 0 else 0.0; res = r - be * b; se = nw_se(res.values, 5)
    return dict(cagr=m(r)["cagr"], poolEW_cagr=float((1 + b).prod() ** (244 / n) - 1), excess_cagr=m(r)["cagr"] - float((1 + b).prod() ** (244 / n) - 1),
                beta_vs_poolEW=be, resid_alpha_vs_poolEW_244=float(res.mean() * 244), t_hac5=float(res.mean() / se) if se > 0 else None)


B4_TRACKS = {"hiliq": {"60w": ROOT / "output/strategy_hiliq/b4/B4_50_25_25_topN_60w.parquet",
                       "100w": ROOT / "output/strategy_hiliq/b4/B4_50_25_25_topN_100w.parquet"},
             "fulla": None}  # None -> V3.TRACKS["B4"] (legacy paper B4; diagnostic only)
B0W = {"capacity_adv": .5, "earnings_event": .25, "insider_increase": .25}
START, END = "2024-06-03", "2026-10-09"; COST = ADG.COST; H = 20
_CTX = {}
UNIVERSE_MASKS = {"hiliq": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
                  "fulla": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"}
UNIVERSE = os.environ.get("ALPHA_CMC_UNIVERSE", "hiliq")  # hiliq = gate; fulla = diagnostic only


def set_universe(u: str):
    global UNIVERSE
    if u not in UNIVERSE_MASKS: raise ValueError(f"universe must be one of {list(UNIVERSE_MASKS)}")
    if u != UNIVERSE: _CTX.clear(); _B0.clear()
    UNIVERSE = u


def ctx():
    if _CTX: return _CTX
    import research.g1g5_moneyflow_resid_weights as mf
    from research.g1g5_nontextbook_weights import _load_sw_members, sw_code_on
    from research.g1g5_x2_panel_stitch import to_panel_id
    b = ADG.bench(); days = b.index[(b.index >= "2023-09-01") & (b.index <= END)]
    ev0 = days[(days >= START)]
    mk = pd.read_parquet(UNIVERSE_MASKS[UNIVERSE], columns=["date", "instrument", "in_universe"],
                         filters=[("date", ">=", pd.Timestamp(START)), ("date", "<=", pd.Timestamp(END)), ("in_universe", "==", True)])
    mk["d"] = pd.to_datetime(mk["date"]).dt.strftime("%Y-%m-%d"); mk["instrument"] = mk["instrument"].astype(str)
    U = sorted(set(mk["instrument"]))
    P = pd.DataFrame({i: ADG._close(i) for i in U}).reindex(days)
    R = P.pct_change(fill_method=None); rb = b.reindex(days).pct_change()
    beta = R.rolling(120, min_periods=60).cov(rb).div(rb.rolling(120, min_periods=60).var(), axis=0)
    ev = days[(days >= START)]
    mem = {d: set(g) for d, g in mk.groupby("d")["instrument"]}
    pids = {to_panel_id(i): i for i in U}
    fm = pd.read_parquet(ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet", columns=["instrument_id", "trade_date", "float_mktcap"],
                         filters=[("trade_date", ">=", pd.Timestamp(START)), ("instrument_id", "in", list(pids))])
    fm["i"] = fm.instrument_id.map(pids)
    MC = np.log(fm.pivot_table(index="trade_date", columns="i", values="float_mktcap").reindex(ev).ffill()).reindex(columns=U)
    sw = _load_sw_members(); me = pd.Series(ev, index=ev).groupby(ev.to_period("M")).max().values
    IND = pd.DataFrame({i: [sw_code_on(i, d, sw) for d in me] for i in U}, index=me).reindex(ev, method="ffill")
    F = P.shift(-H) / P - 1
    _CTX.update(R=R.reindex(ev), universe=UNIVERSE, mask=str(UNIVERSE_MASKS[UNIVERSE].relative_to(ROOT)), U=U, ev=ev, mem=mem, beta=beta.reindex(ev), MC=MC, IND=IND, F=F.reindex(ev))
    return _CTX


def sig(path) -> pd.DataFrame:
    c = ctx(); d = pd.read_parquet(path, columns=["date", "instrument", "target_weight"]); d["date"] = pd.to_datetime(d["date"].astype(str).str[:10])
    S = d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum")
    return S.reindex(index=c["ev"], columns=c["U"]).fillna(0.0)


def resid_z(S: pd.DataFrame, extra: list[pd.DataFrame] | None = None) -> pd.DataFrame:
    c = ctx(); out = pd.DataFrame(np.nan, index=S.index, columns=S.columns)
    for d in S.index:
        pool = [i for i in c["U"] if i in c["mem"].get(d.strftime("%Y-%m-%d"), set())]
        X = pd.DataFrame({"mc": c["MC"].loc[d, pool], "beta": c["beta"].loc[d, pool]})
        for k, e in enumerate(extra or []): X[f"x{k}"] = e.loc[d, pool]
        X = X.join(pd.get_dummies(c["IND"].loc[d, pool].fillna("_UNK"), dtype=float))
        y = S.loc[d, pool]; ok = X.notna().all(axis=1) & y.notna()
        if ok.sum() < 30 or y[ok].std() == 0: continue
        Xm = np.c_[np.ones(ok.sum()), X[ok].values.astype(float)]
        cf, *_ = np.linalg.lstsq(Xm, y[ok].values, rcond=None); e = y[ok].values - Xm @ cf
        sd = e.std()
        if sd > 0: out.loc[d, y[ok].index] = (e - e.mean()) / sd
    return out


def ic_stats(Z: pd.DataFrame) -> dict:
    F = ctx()["F"]; ics = []
    for d in Z.index:
        z, f = Z.loc[d], F.loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= 30: ics.append((d, z[ok].rank().corr(f[ok].rank())))
    s = pd.Series(dict(ics)).dropna()
    roll = (s.rolling(252).mean() / s.rolling(252).std()).dropna()
    return dict(rank_ic=float(s.mean()), icir_full=float(s.mean() / s.std()), icir_roll252_median=float(roll.median()) if len(roll) else None, n=int(len(s)),
                **ic_tstats(s))


def nw_se(x: np.ndarray, lag: int) -> float:
    """Newey-West (Bartlett) s.e. of the mean."""
    x = np.asarray(x, float); n = len(x); e = x - x.mean()
    g = e @ e / n
    for k in range(1, min(lag, n - 1) + 1):
        g += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    return float(np.sqrt(max(g, 0) / n))


def ic_tstats(s: pd.Series, h: int = H) -> dict:
    """Disclosure only (Arch P1); gate thresholds unchanged. Daily IC on h-day fwd returns overlaps → naive t overstated."""
    x = s.dropna().values; n = len(x)
    if n < 3: return dict(ic_t_naive=None, ic_t_neff=None, ic_t_hac=None, ic_n_eff=None, ic_hac_lag=h - 1)
    mu, sd = x.mean(), x.std(ddof=1); lag = max(h - 1, 1)
    se = nw_se(x, lag)
    return dict(ic_t_naive=float(mu / (sd / np.sqrt(n))), ic_t_neff=float(mu / (sd / np.sqrt(n / h))), ic_n_eff=float(n / h),
                ic_t_hac=float(mu / se) if se > 0 else None, ic_hac_lag=int(lag), ic_t_note="disclosure only; thresholds unchanged")


def nav_stats(W: pd.DataFrame) -> pd.Series:
    n = V3.LC._ret(W)  # audit fix: T+1 next_open, net, close_to_close_returns
    return n[(n.index >= START) & (n.index <= END)]


def m(r):
    nav = (1 + r).cumprod(); return dict(cagr=float(nav.iloc[-1] ** (244 / len(r)) - 1), mdd=float((nav / nav.cummax() - 1).min()))  # AI 2026-10-14: CAGR 年化 244 主报（quantlab/metrics.PERIODS）


_B0 = {}


def b0():
    if _B0: return _B0
    S = {k: sig(p) for k, p in LEGS_BY_UNIVERSE[UNIVERSE].items()}; Z = {k: resid_z(s) for k, s in S.items()}
    combo = sum(B0W[k] * Z[k].fillna(0) for k in Z).where(Z["capacity_adv"].notna())
    _B0.update(S=S, combo=combo, ic=ic_stats(combo))
    return _B0


def _ic_series(Z: pd.DataFrame) -> pd.Series:
    F = ctx()["F"]; ics = {}
    for d in Z.index:
        z, f = Z.loc[d], F.loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= 30: ics[d] = z[ok].rank().corr(f[ok].rank())
    return pd.Series(ics).dropna()


def _d_ic_series(Z0: pd.DataFrame, Z1: pd.DataFrame) -> pd.Series:
    a, b = _ic_series(Z0), _ic_series(Z1); ix = a.index.intersection(b.index)
    return b[ix] - a[ix]


def cmc(leaf: str) -> dict:
    B = b0(); wf = Path(leaf) if str(leaf).endswith(".parquet") else V3.wfile(leaf)  # leaf name (ai_factory) or explicit parquet path
    zl = resid_z(sig(wf), extra=list(B["S"].values()))
    c1 = (0.8 * B["combo"] + 0.2 * zl.fillna(0)).where(B["combo"].notna())
    ic1 = ic_stats(c1)
    zs = resid_z(sig(wf))  # style-only residual (ind/mcap/beta), for rho reference
    rho = [zs.loc[d].corr(B["combo"].loc[d]) for d in zs.index]
    rho_post = [zl.loc[d].corr(B["combo"].loc[d]) for d in zl.index]
    out = dict(B0_ic=B["ic"], B1_ic=ic1, d_ic=ic1["rank_ic"] - B["ic"]["rank_ic"],
               d_icir_full=ic1["icir_full"] - B["ic"]["icir_full"],
               leaf_file=str(wf), b0_legs={k: str(v) for k, v in LEGS_BY_UNIVERSE[UNIVERSE].items()},
               universe=UNIVERSE, universe_mask=ctx()["mask"], universe_role="gate" if UNIVERSE == "hiliq" else "diagnostic_only",
               d_ic_tstats=ic_tstats(_d_ic_series(B["combo"], c1)),
               d_icir_roll252_median=(ic1["icir_roll252_median"] - B["ic"]["icir_roll252_median"]) if ic1["icir_roll252_median"] is not None and B["ic"]["icir_roll252_median"] is not None else None,
               rho_leaf_resid_vs_B0=float(np.nanmean(rho)), rho_after_leg_resid=float(np.nanmean(rho_post)),
               rho_note="rho 用叶对行业/市值/β 残差化后的信号 vs B0 组合信号（日均截面相关）；再对 B0 腿信号残差化后 ρ≈0（构造使然），另列 rho_after_leg_resid", tiers={})
    L = V3.LC._w(wf); EW = pool_ew()
    for tier, N in V3.NT.items():
        if UNIVERSE == "hiliq" and BASE == "capadv": trk = CAPADV_BOOK_TRACKS[tier]
        else: trk = (B4_TRACKS[UNIVERSE] or V3.TRACKS["B4"])[tier]
        b = _load_track(trk)
        b1 = V3.stack(b, V3.leaf_topn(L, N))
        r0, r1 = nav_stats(b), nav_stats(b1); ix = r0.index.intersection(r1.index); r0, r1 = r0[ix], r1[ix]
        m0, m1 = m(r0), m(r1)
        yr = {str(y): float((1 + r1[r1.index.year == y]).prod() - (1 + r0[r0.index.year == y]).prod()) for y in sorted(set(ix.year))}
        out["tiers"][tier] = dict(B0_net=m0, B1_net=m1, d_cagr_net=m1["cagr"] - m0["cagr"], d_mdd=m1["mdd"] - m0["mdd"], mdd_worsening_pp=float((m0["mdd"] - m1["mdd"]) * 100),
                                  B1_mdd=m1["mdd"], yearly_d_return_net=yr, n_neg_years=int(sum(v < 0 for v in yr.values())),
                                  base_track=str(trk), base=("capadv_hiliq_book_smoke" if (UNIVERSE == "hiliq" and BASE == "capadv") else "b4_diag"),
                                  vs_poolEW=dict(B0=vs_pool_ew(r0, EW), B1=vs_pool_ew(r1, EW)),
                                  report_to_leo_eligible=bool(m1["cagr"] > m0["cagr"] and vs_pool_ew(r1, EW)["excess_cagr"] > 0))
    out["definition_notes"] = __doc__
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="CMC (Alpha). hiliq=gate (default), fulla=diagnostic.")
    ap.add_argument("leaf"); ap.add_argument("--universe", choices=list(UNIVERSE_MASKS), default="hiliq")
    ap.add_argument("--base", choices=["capadv", "b4"], default="capadv", help="hiliq tier baseline: capadv book-smoke (gate, 主 Agent 10-18 00:54) | b4 (diag)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(); set_universe(a.universe); BASE = a.base
    r = cmc(a.leaf); r.pop("definition_notes", None); r.update(live=False, promotion_approved=False)
    txt = json.dumps(r, ensure_ascii=False, indent=2, default=str)
    if a.out: Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(txt)
    print(txt)
