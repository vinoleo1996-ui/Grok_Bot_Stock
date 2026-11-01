"""Negative/positive tests for B4/S6 content gate (主 Agent 2026-10-14). Scratch files only under /tmp; no pins touched."""
import json, sys, copy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "research"))
import pandas as pd
from quantlab.portfolio import b4_paper as P
import b4_paper_extend as B
T = Path("/tmp/ql_gate_tests"); T.mkdir(exist_ok=True)
cfg = json.loads((ROOT / "output/strategy_paper_b4/FROZEN_CONFIG.json").read_text())
pin = cfg["leg_pins"]["earnings_event"]; newleg = ROOT / "output/ai_factory/g1g5_earnings_event_daily_weights_20261014_184648.parquet"
res = {}
def leg_variant(fn, name):
    d = pd.read_parquet(newleg); fn(d); p = T / name; d.to_parquet(p); return p
# 0 positive: real recomputed leg passes, revisions only in (10-09, 10-13]
r = P._hist_rows_equal(pin["path"], newleg, pin["last_date"], freeze_end=P.FROZEN_END, leg="earnings_event")
res["pos_real_leg"] = dict(pass_=r["pass_"], n_revisions=r["n_revisions"], zero_cols=r["zero_cols_added"], expect=True)
# 1 nonzero one-sided column
p = leg_variant(lambda d: d.__setitem__("weight", d.weight.where(~((d.instrument == "600256.SH") & (d.session.astype(str) < "2025")), 0.01)), "neg1.parquet")
r = P._hist_rows_equal(pin["path"], p, pin["last_date"], freeze_end=P.FROZEN_END, leg="earnings_event"); res["neg_nonzero_one_sided"] = dict(pass_=r["pass_"], reason=r.get("fail_reason"), expect=False)
# 2 revision at/before 10-09
def rev(d):
    m = (d.session.astype(str).str[:10] == "2026-10-09") & (d.instrument == "510300.SH"); d.loc[m, "weight"] = d.loc[m, "weight"] - 0.01
p = leg_variant(rev, "neg2.parquet")
r = P._hist_rows_equal(pin["path"], p, pin["last_date"], freeze_end=P.FROZEN_END, leg="earnings_event"); res["neg_revision_le_freeze_end"] = dict(pass_=r["pass_"], reason=r.get("fail_reason"), expect=False)
# 3 portfolio booked row change (<= pin 10-13)
old = cfg["weights"]["600000"]["path"]; W = pd.read_parquet(ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261014_r2.parquet")
m = (W.session.astype(str).str[:10] == "2026-10-13") & (W.instrument == "510300.SH"); W.loc[m, "weight"] += 1e-6; p = T / "neg3.parquet"; W.to_parquet(p)
r = P.check_extension(old, p, end="2026-10-13"); res["neg_portfolio_row_change"] = dict(pass_=r["history_match"]["pass"], max_abs_diff=r["history_match"]["max_abs_diff"], expect=False)
# 4 deferral 2 trading days later (10-15) vs 1 day (10-14)
res["pos_deferral_1d"] = dict(pass_=P.deferral_check({"booked_days": {"booked_last": "2026-10-13", "deferred_rebalance_day": "2026-10-14"}}, "2026-10-13")["pass_"], expect=True)
d2 = P.deferral_check({"booked_days": {"booked_last": "2026-10-13", "deferred_rebalance_day": "2026-10-15"}}, "2026-10-13")
res["neg_deferral_2d"] = dict(pass_=d2["pass_"], reason=d2["reason"], expect=False)
# 4b extension-side: splice with booked_last two trading days back must assert
try:
    Wb = pd.read_parquet(ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261014_r2.parquet"); Wb["session"] = Wb.session.astype(str).str[:10]
    bk = Wb[Wb.session <= "2026-10-12"].copy(); bk.loc[bk.session == "2026-10-12", "weight"] *= 1.0; p = T / "booked_1012.parquet"
    m = (bk.session == "2026-10-12") & (bk.instrument == "510300.SH"); bk.loc[m, "weight"] += 0.01; bk.to_parquet(p)
    Wc = Wb[Wb.session != "2026-10-13"]   # gap: next session after 10-12 is 10-14 in this frame -> 2 trading days
    B.ROOT = Path("/"); B.splice_booked(Wc, p); res["neg_deferral_2d_extend"] = dict(pass_=True, expect=False)
except AssertionError as e:
    res["neg_deferral_2d_extend"] = dict(pass_=False, reason=str(e), expect=False)
finally:
    B.ROOT = ROOT
ok = all(v["pass_"] == v["expect"] for v in res.values())
print(json.dumps(dict(all_ok=ok, tests=res), ensure_ascii=False, indent=1, default=str)); sys.exit(0 if ok else 1)
