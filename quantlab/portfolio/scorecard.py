"""Unified paper/candidate scorecard (research only; reuses existing NAVs, never reruns).
Segments X2 (frozen backfill), X2H (bridge), FWD (official forward from 2026-11-02) are kept separate."""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd

from quantlab.metrics import PERIODS as QM_PERIODS, CONVENTION as QM_CONVENTION
ROOT = Path(__file__).resolve().parents[2]; LOOP = ROOT / "output/loop"; V3 = "output/v3/book_smoke_"
CAPS = (600000, 1000000)


def _both(d):  return {c: f"{d}/aum_{c}/X2" for c in CAPS}
def _one(d60, d100): return {600000: f"{d60}/aum_600000/X2", 1000000: f"{d100}/aum_1000000/X2"}


TRACKS = {  # name -> {cap: X2 dir containing BOOK/ and C0/}
    "capacity_adv [PAPER]": _both(V3 + "g1g5_capacity_adv_x2"),
    "B4 conc 50/25/25 [PAPER]": {c: f"output/strategy_paper_b4/backfill_x2/aum_{c}_run/aum_{c}/X2" for c in CAPS},
    "S6 shadow 50/25/25 [SHADOW]": {c: f"output/strategy_paper_s6/backfill_x2/aum_{c}_run/aum_{c}/X2" for c in CAPS},
    "insider_increase": _both(V3 + "g1g5_insider_increase_x2"),
    "earnings_event": _both(V3 + "g1g5_earnings_event_x2"),
    "equity_incentive": _both(V3 + "g1g5_equity_incentive_x2"),
    "capadv+insinc 70/30": _both(V3 + "g1g5_combo_capadv_insinc_70_30_x2"),
    "capadv+insinc 80/20": _both(V3 + "g1g5_combo_capadv_insinc_80_20_x2"),
    "capadv+earnevt 70/30": _both(V3 + "g1g5_combo_capadv_earnevt_70_30_x2"),
    "capadv+earnevt 80/20": _both(V3 + "g1g5_combo_capadv_earnevt_80_20_x2"),
    "capadv+eqincent 70/30": _both(V3 + "g1g5_combo_capadv_eqincent_70_30_x2"),
    "capadv+eqincent 80/20 [Alpha gateB cand: FAIL]": _both(V3 + "g1g5_combo_capadv_eqincent_80_20_x2"),
    "leaf11 cap80+rc20 topN [GATE_V3: FAIL@60w]": _one(V3 + "gatev3_leaf11_cap80_rc20_60w", V3 + "gatev3_leaf11_cap80_rc20_100w"),
    "conc_v2 CORE": _one(V3 + "conc_v2r_CORE_60w_x2", V3 + "conc_v2r_CORE_100w_x2"),
    "conc_v2 B1_equal topN": _one(V3 + "conc_v2_B_B1_equal_topN_60w_x2", V3 + "conc_v2_B_B1_equal_topN_100w_x2"),
    "conc4leg B1eq+eqincent": _one(V3 + "g1g5_conc4leg_b1eq_eqincent_60w_x2", V3 + "g1g5_conc4leg_b1eq_eqincent_100w_x2"),
}


def _nav(p):
    n = pd.read_csv(ROOT / p); i = n.columns[0]; n[i] = pd.to_datetime(n[i]); return n.set_index(i)["nav"].astype(float)


def metrics(nav, c0=None):
    """All figures via quantlab.metrics (244-day annualisation; monthly win excludes incomplete first/last months)."""
    from quantlab import metrics as QM
    nav = nav.astype(float); r = QM.returns(nav)
    cagr = QM.cagr(nav) if len(r) >= 5 else None; mdd = QM.mdd(nav)
    mw = QM.monthly_win_rate(r, nav_base=nav.index[0])
    out = dict(start=str(nav.index[0].date()), end=str(nav.index[-1].date()), days=len(nav),
               total_return=float(nav.iloc[-1] / nav.iloc[0] - 1), cagr=cagr, mdd=mdd, calmar=QM.calmar(cagr, mdd),
               win_daily=QM.daily_win_rate(r), win_monthly=mw["monthly_win"] if mw["months"] >= 1 else None,
               months_used=mw["months"], monthly_note=mw["monthly_note"])
    if c0 is not None:
        c = c0.reindex(nav.index).ffill(); rc = QM.returns(c)
        out["win_daily_vs_c0"] = float((r - rc.reindex(r.index) > 0).mean())
        out["win_monthly_vs_c0"] = QM.monthly_win_rate(r, rc, nav_base=nav.index[0]).get("monthly_beat")
    return out


def turnover_cost(d, cap):
    o = {}
    try:
        s = json.loads((ROOT / d / "BOOK/summary.json").read_text())["metrics"]
        o["cost_pct_aum"] = s.get("cost_pct_initial"); o["total_cost"] = s.get("total_cost")
    except Exception:
        o["cost_pct_aum"] = o["total_cost"] = None
    try:
        a = pd.read_parquet(ROOT / d / "BOOK/actual_weights.parquet")
        P = a.pivot_table(index="session", columns="instrument_id", values="weight", aggfunc="sum").fillna(0)
        o["turnover_ann"] = float(P.diff().abs().sum(axis=1).iloc[1:].mean() / 2 * QM_PERIODS)
    except Exception:
        o["turnover_ann"] = None
    return o


def _x2h(day_dir, name, cap):
    if day_dir is None: return None
    key = {"capacity_adv [PAPER]": "capacity_adv", "B4 conc 50/25/25 [PAPER]": "b4", "S6 shadow 50/25/25 [SHADOW]": "s6"}.get(name)
    if not key: return None
    fs = glob.glob(str(day_dir / "bridge_X2H" / f"{key}*_{cap}_X2H_nav.csv"))
    return fs[0] if fs else None


def build(day_dir=None):
    day_dir = (ROOT / day_dir) if day_dir else None
    rows = []
    for name, dd in TRACKS.items():
        for cap, d in dd.items():
            base = dict(track=name, aum=cap)
            if not (ROOT / d / "BOOK/nav.csv").exists():
                rows.append(dict(base, segment="X2", status="missing", path=d)); continue
            nav = _nav(f"{d}/BOOK/nav.csv"); c0 = _nav(f"{d}/C0/nav.csv") if (ROOT / d / "C0/nav.csv").exists() else None
            m = metrics(nav, c0)
            try:   # engine's own CAGR/MDD (same annualisation as all receipts)
                sm = json.loads((ROOT / d / "BOOK/summary.json").read_text())["metrics"]
                m.update(cagr=sm["cagr"], mdd=sm["mdd"], calmar=sm["cagr"] / abs(sm["mdd"]) if sm["mdd"] < 0 else None)
            except Exception: pass
            rows.append(dict(base, segment="X2", status="ok", path=d, **m, **turnover_cost(d, cap)))
            if "[PAPER]" in name or "[SHADOW]" in name:
                x = _x2h(day_dir, name, cap)
                if x:
                    n = pd.read_csv(x); col = "nav" if "nav" in n else n.columns[1]; n.index = pd.to_datetime(n.iloc[:, 0])
                    rows.append(dict(base, segment="X2H", status="ok", path=str(x),
                                     **{k: v for k, v in metrics(n[col].astype(float)).items() if k in ("start", "end", "days", "total_return", "mdd", "win_daily")},
                                     note="bridge: too short for CAGR/Calmar/monthly win -> missing"))
                else:
                    rows.append(dict(base, segment="X2H", status="missing", note="X2H PENDING: no gated weights past 2026-10-09 for this track"))
                rows.append(dict(base, segment="FWD", status="missing", note="official forward starts 2026-11-02"))
    for c in CAPS:  # C0 reference
        d = TRACKS["capacity_adv [PAPER]"][c]; m = metrics(_nav(d + "/C0/nav.csv"))
        try:
            sm = json.loads((ROOT / d / "C0/summary.json").read_text())["metrics"]; m.update(cagr=sm["cagr"], mdd=sm["mdd"], calmar=sm["cagr"] / abs(sm["mdd"]))
        except Exception: pass
        rows.append(dict(track="C0 510300", aum=c, segment="X2", status="ok", path=d + "/C0", **m))
    df = pd.DataFrame(rows)
    for ref, nm in (("capacity_adv [PAPER]", "capadv"), ("B4 conc 50/25/25 [PAPER]", "b4")):
        R = df[(df.track == ref) & (df.segment == "X2")].set_index("aum")
        for k in ("cagr", "mdd", "calmar"):
            df[f"{k}_vs_{nm}"] = [(r[k] - R.at[r.aum, k]) if (r.segment == "X2" and pd.notna(r.get(k)) and r.aum in R.index and pd.notna(R.at[r.aum, k])) else None
                                  for _, r in df.iterrows()]
    return df


def _f(v, pct=True, nd=2):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "missing"
    return f"{v*100:.{nd}f}" if pct else f"{v:.{nd}f}"


def write(day_dir=None, stale=None):
    df = build(day_dir)
    if stale:
        df["STALE"] = True
    meta = dict(generated_from="existing NAVs only (no reruns)", live=False, promotion_approved=False,
                segments_rule="X2/X2H/FWD separate, never merged", day_dir=str(day_dir) if day_dir else None,
                STALE=bool(stale), stale_reasons=stale or [], metrics_convention=QM_CONVENTION)
    js = dict(meta=meta, rows=json.loads(df.to_json(orient="records")))
    L = (["# 🔴 STALE — 数据过期，今日 NAV 未运行，下表为上次可用数据", "", *[f"- {r}" for r in stale], ""] if stale else []) + ["# 统一记分卡（研究/paper；X2/X2H/FWD 分段不合并）", "",
         "| 轨道 | AUM | 段 | CAGR% | MDD% | Calmar | 月胜率% | 日胜率% | 月胜C0% | 年化换手 | 成本/AUM% | ΔCAGR vs capadv | ΔMDD vs capadv | ΔCAGR vs B4 | ΔMDD vs B4 |", "|" + "---|" * 15]
    for _, r in df.iterrows():
        if r.status != "ok":
            L.append(f"| {r.track} | {r.aum//10000}万 | {r.segment} | missing |||||||||||| {r.get('note') or ''} |"); continue
        g = lambda k: r.get(k) if k in r and pd.notna(r.get(k)) else None
        L.append(f"| {'🔴STALE ' if stale else ''}{r.track} | {r.aum//10000}万 | {r.segment} | {_f(g('cagr'))} | {_f(g('mdd'))} | {_f(g('calmar'),False)} | {_f(g('win_monthly'),nd=0)} | {_f(g('win_daily'),nd=1)} | {_f(g('win_monthly_vs_c0'),nd=0)} | {_f(g('turnover_ann'),False,1)} | {_f(g('cost_pct_aum'))} | {_f(g('cagr_vs_capadv'))} | {_f(g('mdd_vs_capadv'))} | {_f(g('cagr_vs_b4'))} | {_f(g('mdd_vs_b4'))} |")
    md = "\n".join(L) + "\n\nmissing = 该指标无现成数据，未编造。X2H 为桥接段（太短，只给总收益/MDD/日胜率）；FWD 自 2026-11-02 起。\n口径：quantlab.metrics，年化 244 个交易日；月胜率剔除首尾不完整月（X2 剔除 2026-10，共 28 个月）。\n"
    outs = [LOOP / "scorecard_latest"] + ([Path(day_dir) / "scorecard"] if day_dir else [])
    for o in outs:
        o.with_suffix(".json").write_text(json.dumps(js, indent=1, ensure_ascii=False, default=str)); o.with_suffix(".md").write_text(md)
    return df, md


if __name__ == "__main__":
    import sys; print(write(sys.argv[1] if len(sys.argv) > 1 else None)[1])
