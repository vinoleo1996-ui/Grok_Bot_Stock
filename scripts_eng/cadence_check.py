"""Weight-change cadence per month: frozen X2 vs extension (per leg and combined). Read-only."""
import json, sys
import pandas as pd
def changes(path, end=None):
    w = pd.read_parquet(path, columns=["session", "instrument_id", "weight"]) if "instrument_id" in pd.read_parquet(path).columns else None
    w["s"] = pd.to_datetime(w.session.astype(str).str[:10])
    P = w.pivot_table(index="s", columns="instrument_id", values="weight", aggfunc="sum").fillna(0)
    ch = P.index[1:][(P.diff().abs().sum(axis=1).iloc[1:] > 1e-9).values]
    return list(ch)
def per_month(ch, a="2024-06-01", b="2026-10-09"):
    s = pd.Series(1, index=pd.DatetimeIndex(ch)).loc[a:b]
    m = s.groupby(s.index.to_period("M")).size()
    me = sum(1 for d in s.index if (d + pd.offsets.BMonthEnd(0)) == d or d == s.index[s.index.to_period("M") == d.to_period("M")].max())
    return dict(months=len(m), changes=int(s.sum()), mean_per_month=round(float(m.mean()), 2), max_per_month=int(m.max()),
                months_with_intramonth=int((m > 1).sum()))
F = {"capacity_adv": "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
     "earnings_event": "output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet",
     "insider_increase": "output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet",
     "B4_60w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w.parquet",
     "B4_100w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w.parquet"}
E = {"capacity_adv": "output/ai_factory/g1g5_capacity_adv_daily_weights_paper_20261013.parquet",
     "earnings_event": "output/ai_factory/g1g5_earnings_event_daily_weights_20261014_111825.parquet",
     "insider_increase": "output/ai_factory/g1g5_insider_increase_daily_weights_20261014_111825.parquet",
     "B4_60w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013.parquet",
     "B4_100w": "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013.parquet"}
out = {}
for k in F:
    fc = changes(F[k]); ec = changes(E[k])
    out[k] = dict(frozen=per_month(fc), frozen_last5=[str(d.date()) for d in fc[-5:]],
                  ext_new_changes=[str(d.date()) for d in ec if d > pd.Timestamp("2026-10-09")])
print(json.dumps(out, indent=1, ensure_ascii=False))
