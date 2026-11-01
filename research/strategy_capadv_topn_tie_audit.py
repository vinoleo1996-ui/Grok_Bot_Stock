#!/usr/bin/env python3
"""RESEARCH-ONLY tie/NaN audit of Top-N selection (capacity_adv HI_LIQ leg + B4 composers).
Analysis only; no paper/FROZEN_CONFIG touch; live=false. Outputs: output/strategy_hiliq/topn_tie_audit/."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
OUT = ROOT / "output/strategy_hiliq/topn_tie_audit"; OUT.mkdir(parents=True, exist_ok=True)
L = ROOT / "output/strategy_hiliq/legs"
LEGS = {
 "capacity_adv": L/"g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
 "earnings_event_N1": L/"g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
 "insider_increase_N1": L/"g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet",
 "earnings_event_OLD": L/"_rejected_ind_cap/g1g5_earnings_event_hiliq_v1_daily_weights_20261014_195336.parquet",
 "insider_increase_OLD": L/"_rejected_ind_cap/g1g5_insider_increase_hiliq_v1_daily_weights_20261014_195433.parquet",
}
X2 = ("2024-06-03", "2026-10-09")
def is_etf(s): return str(s).split(".")[0][:2] in ("51","56","58","15")
rows = []
for leg, p in LEGS.items():
    d = pd.read_parquet(p, columns=["session","instrument","weight"]); d["session"] = d.session.astype(str).str[:10]
    d = d[(d.weight > 0) & (d.session >= X2[0]) & (d.session <= X2[1])]
    for s, g in d.groupby("session", sort=True):
        st = g[~g.instrument.map(is_etf)].set_index("instrument")["weight"]
        code_sorted = list(st.index) == sorted(st.index)
        v = st.round(12); nn = len(v); nuniq = v.nunique(); stock_sum = float(st.sum())
        for N in (6, 10, 25):
            r = dict(leg=leg, session=s, N=N, n_stock=nn, n_unique_w=nuniq, equal_weight=bool(nuniq == 1), stock_sum=stock_sum,
                     file_code_sorted=code_sorted, nan_w=int(st.isna().sum()))
            if nn <= N:
                r.update(boundary_tie=False, tie_group=0, tie_slots=0, tiebreak_chosen=[], tiebreak_dropped=[], affected_w_share=0.0)
            else:
                srt = v.sort_values(ascending=False, kind="mergesort")
                thr = srt.iloc[N-1]; nxt = srt.iloc[N]
                tie = bool(abs(thr - nxt) < 1e-12)
                grp = v[(v - thr).abs() < 1e-12]
                above = int((v > thr + 1e-12).sum()); slots = N - above
                # actual production pick: pandas default quicksort on file-order index
                kept = list(st.sort_values(ascending=False).head(N).index)
                ch = [i for i in grp.index if i in kept] if tie else []
                dr = [i for i in grp.index if i not in kept] if tie else []
                r.update(boundary_tie=tie, tie_group=int(len(grp)) if tie else 0, tie_slots=slots if tie else 0,
                         tiebreak_chosen=ch, tiebreak_dropped=dr,
                         chosen_alpha_first=bool(tie and sorted(grp.index)[:slots] == sorted(ch)),
                         affected_w_share=float(st[ch].sum() / st.sort_values(ascending=False).head(N).sum()) if tie else 0.0)
            rows.append(r)
df = pd.DataFrame(rows)
df.to_parquet(OUT/"tie_audit_by_session.parquet", index=False)
summ = []
for (leg, N), g in df.groupby(["leg","N"]):
    reb = g.drop_duplicates(subset=["n_stock","n_unique_w"]) if False else g
    summ.append(dict(leg=leg, N=N, sessions=len(g), sessions_n_gt_N=int((g.n_stock > N).sum()), equal_weight_sessions=int(g.equal_weight.sum()),
                     median_n_stock=float(g.n_stock.median()), boundary_tie_sessions=int(g.boundary_tie.sum()),
                     boundary_tie_pct=float(g.boundary_tie.mean()), mean_tie_group=float(g.loc[g.boundary_tie,"tie_group"].mean()) if g.boundary_tie.any() else 0,
                     mean_tiebreak_chosen=float(g.loc[g.boundary_tie,"tiebreak_chosen"].map(len).mean()) if g.boundary_tie.any() else 0,
                     mean_affected_w_share=float(g.loc[g.boundary_tie,"affected_w_share"].mean()) if g.boundary_tie.any() else 0,
                     alpha_first_pct=float(g.loc[g.boundary_tie,"chosen_alpha_first"].mean()) if g.boundary_tie.any() else None,
                     file_code_sorted_pct=float(g.file_code_sorted.mean()), nan_w=int(g.nan_w.sum())))
S = pd.DataFrame(summ); S.to_csv(OUT/"tie_audit_summary.csv", index=False); print(S.to_string())
