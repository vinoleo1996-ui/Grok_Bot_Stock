"""HI_LIQ_V1.1 pool review (X2 ONLY 2024-06-03→2026-10-09; sealed window NOT read). Read-only. live=false.
① PIT membership audit (member count, churn, exclusion reasons, delisting/suspension handling, float-mcap distribution)
② pool equal-weight index vs 510300 / CSI300 / synthetic CSI800 (=float-cap weighted 000300+000905)
③ benchmark factor sanity: REV20, EP rank IC / ICIR / naive t / HAC t (lag h-1), HI_LIQ vs FULLA."""
import sys, json, glob, resource, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
from research.leaf_selfcheck_v3 import ic_tstat_hac
S, E = pd.Timestamp("2024-06-03"), pd.Timestamp("2026-10-09"); OUT = R/"output/ai_factory/hiliq_pool_review"; OUT.mkdir(exist_ok=True)
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024; res = {"window": [str(S.date()), str(E.date())], "sealed_read": False}
# ---------- ① mask audit
mk = pd.read_parquet(R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet", filters=[("date", ">=", S - pd.Timedelta(days=10)), ("date", "<=", E)])
mk = mk[mk.instrument.str.endswith((".SH", ".SZ"))]
cnt = mk.groupby("date").in_universe.sum(); cntx = cnt[cnt.index >= S]
M = mk.pivot_table(index="date", columns="instrument", values="in_universe", aggfunc="max").fillna(False).astype(bool)
chg = (M != M.shift(1)).iloc[1:]; enter = (M & ~M.shift(1, fill_value=False)).iloc[1:].sum(1); exit_ = (~M & M.shift(1, fill_value=False)).iloc[1:].sum(1)
enter, exit_ = enter[enter.index >= S], exit_[exit_.index >= S]
mo = pd.DataFrame({"members_mean": cntx.resample("ME").mean(), "members_min": cntx.resample("ME").min(), "members_max": cntx.resample("ME").max(),
                   "enter_per_day": enter.resample("ME").mean(), "exit_per_day": exit_.resample("ME").mean()})
x = mk[mk.date >= S]; nonm = x[~x.in_universe]
reasons = {k: float(nonm[k].mean()) for k in ("st", "suspended", "young", "adv_fail")}
excl_only_adv = float((nonm.adv_fail & ~nonm.st & ~nonm.suspended & ~nonm.young).mean())
ever = M.loc[M.index >= S].any(); static_ever = int(ever.sum())
# daily overlap of member set vs fixed anchor (first X2 day) → shows PIT not static
first = M.loc[cntx.index[0]]; jac_anchor = (M.loc[cntx.index] & first).sum(1)/(M.loc[cntx.index] | first).sum(1)
# delisting
dm = pd.read_parquet(R/"data/v2/delisted/delisted_master_tushare.parquet", columns=["ts_code","delist_date","last_trade_date","delist_reason_category"])
dm["delist_date"] = pd.to_datetime(dm.delist_date.astype(str), errors="coerce"); dm["last_trade_date"] = pd.to_datetime(dm.last_trade_date.astype(str), errors="coerce")
dx = dm[(dm.last_trade_date >= S) & (dm.last_trade_date <= E)]
dl = []
for _, r in dx.iterrows():
    if r.ts_code not in M.columns: dl.append((r.ts_code, False, None, r.delist_reason_category)); continue
    mm = M[r.ts_code]; mm = mm[mm]
    last_mem = mm.index.max() if len(mm) else None
    gap = int(((M.index > last_mem) & (M.index <= r.last_trade_date)).sum()) if last_mem is not None else None
    dl.append((r.ts_code, bool(len(mm)), gap, r.delist_reason_category))
dl = pd.DataFrame(dl, columns=["ts_code","ever_member_x2","sessions_last_member_to_last_trade","reason"])
res["membership"] = dict(pit_rule="逐日重算：ADV20=前20个开市日成交额均值(不含当日)≥1亿；剔 ST(namechange 区间含当日)、停牌(suspend_d 当日 S 类 或 前一日无成交)、上市<60开市日；无市值筛；沪深A(无北交所)",
    member_count=dict(mean=float(cntx.mean()), min=int(cntx.min()), max=int(cntx.max()), first=int(cntx.iloc[0]), last=int(cntx.iloc[-1])),
    daily_churn=dict(enter_mean=float(enter.mean()), exit_mean=float(exit_.mean())), ever_member_x2=static_ever,
    jaccard_vs_first_day=dict(q25=float(jac_anchor.quantile(.25)), median=float(jac_anchor.median()), min=float(jac_anchor.min()), last=float(jac_anchor.iloc[-1])),
    nonmember_reason_share=reasons, nonmember_only_adv_fail=excl_only_adv,
    delist_in_x2=dict(n=int(len(dl)), ever_member=int(dl.ever_member_x2.sum()), gap_sessions_of_members=dl.loc[dl.ever_member_x2, "sessions_last_member_to_last_trade"].describe().round(1).to_dict(),
                      reasons=dl.loc[dl.ever_member_x2, "reason"].value_counts().to_dict()))
mo.round(1).to_csv(OUT/"members_monthly.csv"); print("① done", f"rss={rss():.0f}", flush=True)
del M, chg, mk, x, nonm
# ---------- panel X2
P = pd.concat([pd.read_parquet(R/f"output/ai_factory/panel_cache/cs_panel_{y}.parquet", columns=["date","instrument","hiliq","fulla","ret","logmv","ind"]) for y in (2024, 2025, 2026)])
P = P[P.date >= S - pd.Timedelta(days=60)]
# mcap distribution (float mcap, 亿元)
Q = P[(P.date >= S) & (P.date <= E) & (P.hiliq | P.fulla)].copy(); Q["mv_yi"] = np.exp(Q.logmv)/1e8; Q["m"] = Q.date.dt.to_period("Q")
def qs(g): return pd.Series({"n_days_mean": g.groupby("date").size().mean(), "p10": g.mv_yi.quantile(.1), "p25": g.mv_yi.quantile(.25), "p50": g.mv_yi.median(), "p75": g.mv_yi.quantile(.75), "p90": g.mv_yi.quantile(.9)})
mvd = pd.concat({"HILIQ": Q[Q.hiliq].groupby("m").apply(qs), "FULLA": Q[Q.fulla].groupby("m").apply(qs)}, axis=1).round(1)
mvd.to_csv(OUT/"mcap_quarterly.csv")
# share of HI_LIQ members falling in FULLA size buckets (FULLA logmv P70/P90 per day)
def bucket(g):
    f = g[g.fulla]; p70, p90 = f.logmv.quantile(.7), f.logmv.quantile(.9); h = g[g.hiliq]
    return pd.Series({"micro_lt_P70": (h.logmv < p70).mean(), "mid_P70_P90": ((h.logmv >= p70) & (h.logmv < p90)).mean(), "large_ge_P90": (h.logmv >= p90).mean(), "hiliq_share_of_fulla": len(h)/max(len(f), 1)})
bk = Q.groupby("date").apply(bucket); bkq = bk.groupby(bk.index.to_period("Q")).mean().round(3); bkq.to_csv(OUT/"hiliq_in_fulla_size_buckets_quarterly.csv")
res["mcap"] = dict(hiliq_median_yi_first_q=float(mvd["HILIQ"]["p50"].iloc[0]), hiliq_median_yi_last_q=float(mvd["HILIQ"]["p50"].iloc[-1]),
                   fulla_median_yi_first_q=float(mvd["FULLA"]["p50"].iloc[0]), fulla_median_yi_last_q=float(mvd["FULLA"]["p50"].iloc[-1]),
                   hiliq_bucket_share_mean=bk.mean().round(3).to_dict(), hiliq_bucket_share_first_q=bkq.iloc[0].to_dict(), hiliq_bucket_share_last_q=bkq.iloc[-1].to_dict())
print("① mcap done", f"rss={rss():.0f}", flush=True); del Q
# ---------- ② EW index (members at t-1 held over day t; no clip)
RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index()
def ew(col):
    Mm = P.pivot_table(index="date", columns="instrument", values=col, aggfunc="max").reindex_like(RW).fillna(False).astype(bool).shift(1).fillna(False)
    return RW.where(Mm).mean(1)
ews = {"HILIQ_EW": ew("hiliq"), "FULLA_EW": ew("fulla")}
e = pd.read_parquet(R/"data/v2/etf/etf_daily_adj.parquet", columns=["trade_date","close_hfq"], filters=[("ts_code","==","510300.SH")]); e.index = pd.to_datetime(e.trade_date.astype(str).str.replace("-",""), format="%Y%m%d")
ix = pd.read_parquet(R/"data/v2/index/index_daily_pit.parquet", columns=["ts_code","trade_date","close"]); ix["trade_date"] = pd.to_datetime(ix.trade_date)
I = ix.pivot_table(index="trade_date", columns="ts_code", values="close").sort_index().pct_change()
# synthetic CSI800: float-cap weight of 000300 vs 000905 constituents at each month
MV = P[["date","instrument","logmv"]].dropna()
wgt = []
for f in sorted(glob.glob(str(R/"data/v2/tushare_raw/index_weight/000300_SH_20*.parquet")) + glob.glob(str(R/"data/v2/tushare_raw/index_weight/000905_SH_20*.parquet"))):
    ym = f[-14:-8]
    if ym < f"{S.year}{S.month-1:02d}" or ym > "202610": continue
    w = pd.read_parquet(f, columns=["index_code","con_code","trade_date"]); wgt.append(w)
W8 = pd.concat(wgt); W8["trade_date"] = pd.to_datetime(W8.trade_date.astype(str)); W8 = W8.drop_duplicates(["index_code","con_code","trade_date"])
cap_by = []
for (ic, td), g in W8.groupby(["index_code","trade_date"]):
    fd = MV[(MV.date <= td) & (MV.date > td - pd.Timedelta(days=10)) & MV.instrument.isin(g.con_code)].sort_values("date").drop_duplicates("instrument", keep="last")
    cap_by.append((ic, td, float(np.exp(fd.logmv).sum()), len(fd), len(g)))
cb = pd.DataFrame(cap_by, columns=["ic","td","cap","n_found","n_cons"]).pivot_table(index="td", columns="ic", values="cap").sort_index()
share300 = (cb["000300.SH"]/(cb["000300.SH"]+cb["000905.SH"])).reindex(I.index, method="ffill")
I["CSI800_synth"] = share300.shift(1)*I["000300.SH"] + (1-share300.shift(1))*I["000905.SH"]
B = pd.DataFrame({"510300": e.close_hfq.sort_index().pct_change(), "CSI300": I["000300.SH"], "CSI500": I["000905.SH"], "CSI800_synth": I["CSI800_synth"], "CSI1000": I.get("000852.SH")})
D = pd.concat([pd.DataFrame(ews), B], axis=1); D = D[(D.index >= S) & (D.index <= E)].dropna(subset=["HILIQ_EW","510300"]).fillna(0)
def mets(r):
    n = len(r); nav = (1+r).cumprod(); return dict(cagr244=float(nav.iloc[-1]**(244/n)-1), cagr252=float(nav.iloc[-1]**(252/n)-1), mdd=float((nav/nav.cummax()-1).min()), vol_ann=float(r.std()*np.sqrt(244)), n=n)
res["ew_index"] = {k: mets(D[k]) for k in D.columns}
rel = {}
for b in ("510300", "CSI800_synth", "CSI300"):
    rr = (1+D.HILIQ_EW).cumprod()/(1+D[b]).cumprod(); rel[f"HILIQ_EW/{b}"] = dict(end=float(rr.iloc[-1]), rel_mdd=float((rr/rr.cummax()-1).min()),
        quarterly=rr.resample("QE").last().round(3).rename(lambda d: str(d.date())).to_dict(), excess_ann244=float((D.HILIQ_EW-D[b]).mean()*244), te=float((D.HILIQ_EW-D[b]).std()*np.sqrt(244)))
rel["csi800_synth_note"] = dict(share300_mean=float(share300[(share300.index >= S)].mean()), corr_vs_510300=float(D.CSI800_synth.corr(D["510300"])))
rel["csi800_synth_note"]["n_found_vs_cons_min_ratio"] = float((pd.DataFrame(cap_by, columns=["ic","td","cap","n_found","n_cons"]).eval("n_found/n_cons")).min()); res["ew_relative"] = rel; (1+D).cumprod().to_csv(OUT/"ew_vs_bench_nav.csv"); print("② done", f"rss={rss():.0f}", flush=True)
# ---------- ③ factor sanity
ep = pd.read_parquet(R/"data/v2/ep/ep_pit_daily_tushare.parquet", columns=["trade_date","ts_code","ep","e_available_at"], filters=[("trade_date", ">=", S - pd.Timedelta(days=5))])
ep["trade_date"] = pd.to_datetime(ep.trade_date); pit_viol = float((ep.e_available_at.dt.tz_convert("Asia/Shanghai").dt.tz_localize(None) > ep.trade_date + pd.Timedelta(hours=15)).mean())
EP = ep.pivot_table(index="trade_date", columns="ts_code", values="ep").reindex(index=RW.index, columns=RW.columns)
REV20 = -RW.rolling(20, min_periods=15).sum()
FW = {h: (np.log1p(RW.fillna(0)).rolling(h).sum().shift(-h)).where(RW.shift(-h).notna()) for h in (5, 20)}
IND = P.pivot_table(index="date", columns="instrument", values="ind").reindex_like(RW)
fac = {}
for uni in ("hiliq", "fulla"):
    Mm = P.pivot_table(index="date", columns="instrument", values=uni, aggfunc="max").reindex_like(RW).fillna(False).astype(bool)
    for fn, F in (("REV20", REV20), ("EP", EP)):
        for h in (5, 20):
            ics, icn = [], []
            for d in RW.index[(RW.index >= S) & (RW.index <= E)]:
                m = Mm.loc[d] & F.loc[d].notna() & FW[h].loc[d].notna()
                if m.sum() < 100: continue
                f, y = F.loc[d][m], FW[h].loc[d][m]; ics.append(f.rank().corr(y.rank()))
                ind = IND.loc[d][m]; fz = f.groupby(ind).rank(pct=True); yz = y - y.groupby(ind).transform("mean"); icn.append(fz.corr(yz.rank()))
            for tag, s in (("raw", np.array(ics)), ("ind_neutral", np.array(icn))):
                s = s[np.isfinite(s)]
                fac[f"{uni}|{fn}|h{h}|{tag}"] = dict(rank_ic=float(s.mean()), icir=float(s.mean()/s.std()), t_naive=float(s.mean()/s.std()*np.sqrt(len(s))), t_hac=ic_tstat_hac(s, h), hac_lag=max(h-1, 1), n=len(s))
        print("③", uni, fn, f"rss={rss():.0f}", flush=True)
res["factor_sanity"] = fac; res["ep_pit_violation_share"] = pit_viol; res["peak_rss_mb"] = rss()
(OUT/"pool_review_x2.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float)); print(json.dumps(res, ensure_ascii=False, indent=1, default=float))
