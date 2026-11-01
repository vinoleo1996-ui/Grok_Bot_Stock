"""B4 paper track (concentrated three-leg 50/25/25) — research/paper only, NO orders.

Frozen by docs/v2/STRATEGY_COMBO_CONCLUSION_20261013_ZH.md (PAPER_TRACK_2_CONFIRMED).
Mirrors capacity-adv-paper (core=0/stock=1, ExecConfig.strategy_v1 via book_smoke); each AUM uses its own
frozen weight file. Does not touch output/strategy_paper_capacity_adv or the capacity-adv-paper CLI.

modes: backfill (X2 history) | forward (from FORWARD_START; waits until weights cover it) | monitor | all
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo


def now_et():
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "output/strategy_paper_b4"
FROZEN_DOC = "docs/v2/STRATEGY_COMBO_CONCLUSION_20261013_ZH.md"
WEIGHTS = {600000: "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w.parquet",
           1000000: "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w.parquet"}
TRUNK_RUN = "output/v3/book_smoke_g1g5_capacity_adv_x2"
FORWARD_START = "2026-11-02"
SLEEVES = '{"core":0.0,"stock":1.0,"alpha_event":0.0}'
FLAGS = dict(live=False, live_orders=False, promotion_approved=False, strategy_promotion_approved=False,
             handoff_live_mainbook="NO", sealed_window_touched=False, promotion_path="paper")


SCRIPTS_B4_DEFAULT = ["research/b4_paper_extend.py", "research/capacity_adv_paper_extend.py", "research/g1g5_capacity_adv_weights.py",
                      "research/g1g5_earnings_event_weights.py", "research/g1g5_insider_increase_weights.py"]
FROZEN_EVENT_LEGS_B4 = {"earnings_event": "output/ai_factory/g1g5_earnings_event_daily_weights_20261014_005430.parquet",
                        "insider_increase": "output/ai_factory/g1g5_insider_increase_daily_weights_20261014_011841.parquet"}
# Track spec: defaults reproduce B4 exactly; other tracks (S6) call configure(spec) via quantlab.portfolio.paper_track.
SPEC = dict(name="b4", out="output/strategy_paper_b4", frozen_doc=FROZEN_DOC, weights=dict(WEIGHTS),
            legs={"capacity_adv": .5, "earnings_event": .25, "insider_increase": .25}, event_legs=FROZEN_EVENT_LEGS_B4,
            sleeve="B4_conc_50_25_25", status="PAPER_TRACK_2_BACKFILL_READY_FORWARD_PENDING", fwd_label="B4 paper forward (2026-11+)",
            bridge_key="b4", x2h_pending_reason="no rehash-gated B4 weights past 2026-10-09", rehash_prefix="B4_PAPER_REHASH",
            title="B4 纸面轨", retire_gate=None, scripts=SCRIPTS_B4_DEFAULT)


def configure(spec):
    global OUT, WEIGHTS, FROZEN_DOC
    SPEC.clear(); SPEC.update(spec)
    OUT = ROOT / spec["out"]; FROZEN_DOC = spec["frozen_doc"]
    WEIGHTS.clear(); WEIGHTS.update(spec["weights"])


def retire_gate(psegs):
    g = SPEC["retire_gate"]; out = dict(rule=g, retire=False, by_aum={})
    for c, segs in psegs.items():
        f = segs.get("forward_from_" + FORWARD_START, {})
        mdd = f.get("mdd")
        hit = mdd is not None and mdd < g["fwd_mdd_floor"]
        out["by_aum"][c] = dict(fwd_mdd=mdd, status=("RETIRE" if hit else ("OK" if mdd is not None else "NO_FWD_YET")))
        out["retire"] = out["retire"] or hit
    return out


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def freeze_check():
    OUT.mkdir(parents=True, exist_ok=True)
    fz = OUT / "FROZEN_CONFIG.json"
    cur = {str(c): dict(path=p, sha256=sha(p)) for c, p in WEIGHTS.items()}
    if not fz.exists() and SPEC["name"] != "b4":
        fz.write_text(json.dumps(dict(track=SPEC["name"], frozen_doc=FROZEN_DOC, weights=cur, sleeves=json.loads(SLEEVES),
                                      exec="ExecConfig.strategy_v1 (book_smoke default)", N={"600000": 6, "1000000": 10},
                                      single_name_cap=0.06, legs=SPEC["legs"], event_legs=list(SPEC["event_legs"]),
                                      forward_start=FORWARD_START, retire_gate=SPEC.get("retire_gate"), frozen_et=now_et(), **FLAGS),
                                 indent=2, ensure_ascii=False))
        return cur
    if not fz.exists():
        fz.write_text(json.dumps(dict(frozen_doc=FROZEN_DOC, weights=cur, sleeves=json.loads(SLEEVES),
                                      exec="ExecConfig.strategy_v1 (book_smoke default)", N={"600000": 6, "1000000": 10},
                                      single_name_cap=0.06, legs={"capacity_adv": .5, "earnings_event": .25, "insider_increase": .25},
                                      forward_start=FORWARD_START, frozen_et=now_et(), **FLAGS),
                                 indent=2, ensure_ascii=False))
        return cur
    old = json.loads(fz.read_text())["weights"]
    cur = {c: dict(path=v["path"], sha256=sha(v["path"])) for c, v in old.items()}
    for c in cur:
        if cur[c]["sha256"] != old[c]["sha256"]:
            raise SystemExit(f"FROZEN weight file changed: {cur[c]['path']}")
    return cur


def _run_smoke(path, cap, window, out, receipt):
    from quantlab.portfolio.book_smoke import run as bs
    return bs(["--stock-path", path, "--sleeves", SLEEVES, "--windows", window,
               "--capitals", str(cap), "--arms", "BOOK,C0", "--out", out, "--receipt", receipt])


def backfill():
    freeze_check()
    for cap, p in WEIGHTS.items():
        _run_smoke(p, cap, "X2", f"{SPEC['out']}/backfill_x2/aum_{cap}_run",
                   f"{SPEC['out']}/backfill_x2/RECEIPT_{cap}.md")


def forward():
    freeze_check()
    import quantlab.portfolio.v2_multisleeve_book as M
    for cap, p in WEIGHTS.items():
        w = pd.read_parquet(ROOT / p, columns=["session"])
        last = pd.to_datetime(w.session.astype(str).str[:10]).max()
        if last < pd.Timestamp(FORWARD_START):
            print(json.dumps(dict(mode="forward", aum=cap, status="WAITING",
                                  reason=f"weights end {last.date()} < forward start {FORWARD_START}")))
            continue
        M.WINDOWS["FWD"] = (FORWARD_START, str(last.date())); M.WINDOW_LABEL["FWD"] = SPEC["fwd_label"]
        _run_smoke(p, cap, "FWD", f"{SPEC['out']}/forward/aum_{cap}_run",
                   f"{SPEC['out']}/forward/RECEIPT_{cap}.md")


def _nav(d, cap, arm):
    n = pd.read_csv(ROOT / d / f"aum_{cap}/X2/{arm}/nav.csv")
    return n.set_index(pd.to_datetime(n.iloc[:, 0])).nav


def _stats(n):
    from quantlab import metrics as QM   # single source of truth (244-day annualisation)
    r = QM.returns(n)
    return dict(cagr=QM.cagr(n), mdd=QM.mdd(n), sharpe=QM.sharpe(r), ret=float(n.iloc[-1] / n.iloc[0] - 1))


def segments(n, c0, tr):
    idx = n.index; mid = idx[len(idx) // 2]
    segs = {"2024": ("2024-01-01", "2024-12-31"), "2025": ("2025-01-01", "2025-12-31"),
            "2026": ("2026-01-01", "2026-12-31"), "H1": (idx[0], mid), "H2": (mid, idx[-1])}
    out = {}
    for k, (a, b) in segs.items():
        def cut(x):
            s = x.loc[a:b]
            before = x.loc[:pd.Timestamp(a) - pd.Timedelta(days=1)]
            return pd.concat([before.iloc[-1:], s]) if len(before) else s   # anchor on prior close
        sb, sc, st = cut(n), cut(c0), cut(tr)
        b, c, t = _stats(sb), _stats(sc), _stats(st)
        out[k] = dict(**b, ex_ret_vs_c0=b["ret"] - c["ret"], ex_ret_vs_trunk=b["ret"] - t["ret"],
                      trunk=t, c0=c, start=str(sb.index[0].date()), end=str(sb.index[-1].date()))
    return out


def _seg_row(n, c0, tr):
    b = _stats(n); c = _stats(c0)
    row = dict(start=str(n.index[0].date()), end=str(n.index[-1].date()), cagr=b["cagr"], mdd=b["mdd"], sharpe=b["sharpe"],
               ret=b["ret"], c0_ret=c["ret"], ex_ret_vs_c0=b["ret"] - c["ret"])
    if tr is not None and len(tr) > 2:
        t = _stats(tr); row.update(trunk_ret=t["ret"], trunk_mdd=t["mdd"], ex_ret_vs_trunk=b["ret"] - t["ret"])
    else:
        row.update(trunk_ret=None, ex_ret_vs_trunk=None, trunk_note="capacity_adv trunk has no forward NAV for this span yet")
    return row


def paper_segments(cap, base=None):
    base = base or SPEC["out"]
    """Separate (never merged) segments: backfill H1, backfill H2, forward (from FORWARD_START)."""
    d = f"{base}/backfill_x2/aum_{cap}_run"
    n, c0, tr = _nav(d, cap, "BOOK"), _nav(d, cap, "C0"), _nav(TRUNK_RUN, cap, "BOOK")
    mid = n.index[len(n.index) // 2]
    out = {"backfill_X2_H1": _seg_row(n.loc[:mid], c0.loc[:mid], tr.loc[:mid]),
           "backfill_X2_H2": _seg_row(n.loc[mid:], c0.loc[mid:], tr.loc[mid:])}
    out = {"X2_frozen_H1": out["backfill_X2_H1"], "X2_frozen_H2": out["backfill_X2_H2"]}
    import glob as _g
    recs = sorted(_g.glob(str(ROOT / "output/loop/paper_daily_*/paper_daily_recon.json")))
    br = None
    if recs:
        br = json.loads(Path(recs[-1]).read_text()).get("segments", {}).get("X2H_bridge", {}).get(SPEC["bridge_key"], {}).get("aum", {}).get(str(cap))
    out["X2H_bridge_2026-10-12_to_2026-11-01"] = br or dict(status="PENDING", reason=SPEC["x2h_pending_reason"])
    fdir = ROOT / f"{base}/forward/aum_{cap}_run/aum_{cap}/FWD"
    if (fdir / "BOOK/nav.csv").exists():
        def rd(arm):
            x = pd.read_csv(fdir / arm / "nav.csv"); return x.set_index(pd.to_datetime(x.iloc[:, 0])).nav
        out["forward_from_" + FORWARD_START] = _seg_row(rd("BOOK"), rd("C0"), None)
    else:
        out["forward_from_" + FORWARD_START] = dict(status="WAITING", reason="no forward NAV yet (weights not extended past 2026-10-09)")
    return out


def monitor(base=None):
    base = base or f"{SPEC['out']}/backfill_x2"
    sys.path.insert(0, str(ROOT / "scripts_eng"))
    from conc_fill_diag import diag
    res = dict(frozen=freeze_check(), **FLAGS, aum={})
    for cap, p in WEIGHTS.items():
        d = f"{base}/aum_{cap}_run"
        s = json.loads((ROOT / d / "book_smoke_summary.json").read_text())["by_capital"][str(cap)]
        bk = s["X2/BOOK"]
        W = pd.read_parquet(ROOT / p); st = W[W.instrument_id != "sh.510300"]
        mx = st.groupby("session").weight.max()
        aw = pd.read_parquet(ROOT / d / f"aum_{cap}/X2/BOOK/actual_weights.parquet")
        A = aw.pivot_table(index="session", columns="instrument_id", values="weight", aggfunc="sum").fillna(0)
        turn = float(A.diff().abs().sum(axis=1).iloc[1:].sum() / 2 / (len(A) / __import__("quantlab.metrics", fromlist=["PERIODS"]).PERIODS))
        n, c0, tr = _nav(d, cap, "BOOK"), _nav(d, cap, "C0"), _nav(TRUNK_RUN, cap, "BOOK")
        res["aum"][str(cap)] = dict(
            book=dict(cagr=bk["cagr"], mdd=bk["mdd"], sharpe=bk["sharpe"], cost_pct_initial=bk["cost_pct_initial"],
                      total_cost=bk["total_cost"], fill_ratio=bk.get("fill_ratio")),
            c0=dict(cagr=s["X2/C0"]["cagr"], mdd=s["X2/C0"]["mdd"]),
            trunk=_stats(tr), fills=diag(f"{d}/aum_{cap}/X2/BOOK", cap),
            cap_check=dict(max_target_single=float(mx.max()), sessions_over_6pct=int((mx > 0.0605).sum()),
                           max_actual_single=float(aw[aw.instrument_id != "sh.510300"].weight.max())),
            turnover_one_way_annual=turn, segments=segments(n, c0, tr),
            recon_note="target=weights file (T) vs actual_weights (T+1 fill); fills section")
    res["paper_segments"] = {str(c): paper_segments(c) for c in WEIGHTS}
    a6, a10 = res["aum"]["600000"]["segments"]["H1"], res["aum"]["1000000"]["segments"]["H1"]
    res["segment_finding"] = dict(
        first_half_end="2025-08-01",
        trails_c0_and_trunk_both_aum=bool(a6["ex_ret_vs_c0"] < 0 and a6["ex_ret_vs_trunk"] < 0 and a10["ex_ret_vs_c0"] < 0 and a10["ex_ret_vs_trunk"] < 0),
        h1_ex_vs_c0_pp={"600000": round(a6["ex_ret_vs_c0"] * 100, 2), "1000000": round(a10["ex_ret_vs_c0"] * 100, 2)},
        h1_ex_vs_trunk_pp={"600000": round(a6["ex_ret_vs_trunk"] * 100, 2), "1000000": round(a10["ex_ret_vs_trunk"] * 100, 2)},
        note_zh="X2 前半段（至 2025-08-01）两档均跑输 C0 与 capacity_adv 主干；超额全部来自后半段。前向结果须与回填分段分别展示，不得合并。")
    if SPEC.get("retire_gate"):
        res["retire_gate"] = retire_gate(res["paper_segments"])
    (OUT / "monitor.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float))
    O = SPEC["out"]
    stt = dict(sleeve=SPEC["sleeve"], status=(SPEC["status"] if not res.get("retire_gate", {}).get("retire") else "RETIRED_BY_PREREG_GATE"),
               forward_start=FORWARD_START, **FLAGS, paths=dict(
                   backfill_nav_600000=f"{O}/backfill_x2/aum_600000_run/aum_600000/X2/BOOK/nav.csv",
                   backfill_nav_1000000=f"{O}/backfill_x2/aum_1000000_run/aum_1000000/X2/BOOK/nav.csv",
                   forward_nav_600000=f"{O}/forward/aum_600000_run/aum_600000/FWD/BOOK/nav.csv",
                   forward_nav_1000000=f"{O}/forward/aum_1000000_run/aum_1000000/FWD/BOOK/nav.csv",
                   monitor=f"{O}/monitor.json", frozen=f"{O}/FROZEN_CONFIG.json"),
               updated_et=now_et())
    (OUT / "STATUS.json").write_text(json.dumps(stt, indent=2, ensure_ascii=False))
    return res


FROZEN_END = "2026-10-09"


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def _wtab(path):
    w = pd.read_parquet(_abs(path), columns=["session", "instrument_id", "weight"])
    w["session"] = pd.to_datetime(w.session.astype(str).str[:10])
    return w.groupby(["session", "instrument_id"]).weight.sum()


def check_extension(old_path, new_path, tol=1e-8, cap=0.06, cap_tol=1e-6, end=None):
    o, n = _wtab(old_path), _wtab(new_path)
    end = pd.Timestamp(end or FROZEN_END)
    oh = o[o.index.get_level_values(0) <= end]; nh = n[n.index.get_level_values(0) <= end]
    ko, kn = set(oh.index), set(nh.index)
    common = oh.index.intersection(nh.index)
    dmax = float((oh.loc[common] - nh.loc[common]).abs().max()) if len(common) else float("nan")
    a = dict(rows=len(oh), only_in_old=len(ko - kn), only_in_new=len(kn - ko), max_abs_diff=dmax)
    a["pass"] = bool(a["only_in_old"] == 0 and a["only_in_new"] == 0 and np.isfinite(dmax) and dmax <= tol)
    new = n[n.index.get_level_values(0) > end].reset_index()
    if len(new):
        st = new[new.instrument_id != "sh.510300"]
        sums = new.groupby("session").weight.sum()
        b = dict(new_sessions=int(new.session.nunique()), first=str(new.session.min().date()), last=str(new.session.max().date()),
                 max_single=float(st.weight.max()) if len(st) else 0.0,
                 sessions_over_cap=int((st.groupby("session").weight.max() > cap + cap_tol).sum()),
                 sum_min=float(sums.min()), sum_max=float(sums.max()), n_neg=int((new.weight < 0).sum()))
        b["pass"] = bool(b["sessions_over_cap"] == 0 and b["n_neg"] == 0 and abs(b["sum_min"] - 1) <= 1e-6 and abs(b["sum_max"] - 1) <= 1e-6)
    else:
        b = {"new_sessions": 0, "note": "no rows after frozen end (nothing new to check)", "pass": True}
    return dict(history_match=a, new_rows=b, ok=bool(a["pass"] and b["pass"]))


FROZEN_EVENT_LEGS = FROZEN_EVENT_LEGS_B4


def cadence_check(new_path, new_last):
    """Strategy 2026-10-13: B4 must keep frozen cadence (capacity_adv month-end; event legs on events, intra-month).
    Verified via the extension's .check.json: event legs must be recomputed by the frozen leg scripts (new leg files,
    history identical, leg_end >= new last session). A carried/held event leg (suppressed intra-month) FAILS."""
    cj = _abs(str(new_path).replace(".parquet", ".check.json"))
    if new_last <= pd.Timestamp(FROZEN_END):
        return dict(pass_=True, note="no new sessions")
    if not cj.exists():
        return dict(pass_=False, reason=f"missing {cj.name}: cannot verify event-leg recompute")
    c = json.loads(cj.read_text())
    legs, ends, hc = c.get("legs", {}), c.get("leg_end", {}), c.get("leg_hist_check", {})
    bad = []
    for k, frozen in SPEC["event_legs"].items():
        if legs.get(k) in (None, frozen): bad.append(f"{k}: not recomputed (uses frozen leg file)")
        elif str(ends.get(k, "")) < str(new_last.date()): bad.append(f"{k}: leg_end {ends.get(k)} < {new_last.date()} (carried)")
        elif not hc.get(k, {}).get("ok"): bad.append(f"{k}: leg history check failed")
    return dict(pass_=not bad, reason="; ".join(bad) or None, legs=legs, leg_end=ends,
                rule="event legs recomputed by frozen scripts with only WEIGHT_END moved (research/b4_paper_extend.py run_legs)")


# ---------------------------------------------------------------- content-based pinning (Strategy 2026-10-14)
SCRIPTS_B4 = ["research/b4_paper_extend.py", "research/capacity_adv_paper_extend.py", "research/g1g5_capacity_adv_weights.py",
              "research/g1g5_earnings_event_weights.py", "research/g1g5_insider_increase_weights.py"]
LEG_SCRIPT = {"capacity_adv": "research/capacity_adv_paper_extend.py", "earnings_event": "research/g1g5_earnings_event_weights.py",
              "insider_increase": "research/g1g5_insider_increase_weights.py", "equity_incentive": "research/g1g5_equity_incentive_weights.py"}
SHA_FIELD = "frozen_script_sha256"   # required in every combo and leg .check.json: {script_path: sha256}


def _fsha(p):
    return hashlib.sha256(_abs(p).read_bytes()).hexdigest()


def _leg_check_json(p):
    p = str(p)
    for c in (p + ".check.json", p.replace(".parquet", ".check.json")):
        if _abs(c).exists(): return _abs(c)
    return None


def _hist_rows_equal(old, new, end, tol=1e-8, freeze_end=None, leg=None):
    """Leg history vs pin <= end (主 Agent 2026-10-14): outer-join, missing -> 0.
    <= freeze_end (last X2/original freeze end): |dw| <= tol, and a column present on only one side must be all-zero (else fail, named).
    (freeze_end, end]: leg-weight revisions allowed but every one is returned in `revisions` (session, leg, instrument, old, new)."""
    o, n = _wtab(old), _wtab(new); e = pd.Timestamp(end); fe = pd.Timestamp(freeze_end or FROZEN_END)
    oh = o[o.index.get_level_values(0) <= e]; nh = n[n.index.get_level_values(0) <= e]
    M = pd.concat([oh.rename("old"), nh.rename("new")], axis=1).fillna(0.0); d = (M.old - M.new).abs()
    sess = M.index.get_level_values(0); inst = M.index.get_level_values(1)
    H = M[sess <= fe]; dh = d[sess <= fe]
    io = set(oh[oh.index.get_level_values(0) <= fe].index.get_level_values(1)); inn = set(nh[nh.index.get_level_values(0) <= fe].index.get_level_values(1))
    one = sorted(io ^ inn)
    bad_cols = sorted(i for i in one if float(H.xs(i, level=1)[["old", "new"]].abs().max().max()) > tol)
    bad_hist = dh[dh > tol]
    W = M[(sess > fe) & (d > tol)]
    revs = [dict(session=str(s_.date()), leg=leg, instrument=i, old=float(r.old), new=float(r.new)) for (s_, i), r in W.iterrows()]
    ok = not bad_cols and not len(bad_hist)
    r = dict(end=str(e.date()), freeze_end=str(fe.date()), compare="outer_join_fill0", rows=len(oh), one_sided_cols=one,
             zero_cols_added=[i for i in one if i not in bad_cols], differing_rows=int(len(bad_hist)) + len(bad_cols),
             max_abs_diff_hist=float(dh.max()) if len(dh) else 0.0, revisions=revs, n_revisions=len(revs), pass_=bool(ok))
    if not ok:
        r["fail_reason"] = "; ".join(x for x in [f"nonzero one-sided columns {bad_cols}" if bad_cols else "",
            f"revision at/before freeze_end {fe.date()}: {sorted({(str(a.date()), b) for a, b in bad_hist.index})[:10]}" if len(bad_hist) else ""] if x)
    return r


def ensure_pins(cfg, check_json=None):
    """Record current frozen-script shas and the current leg files (content pins) in FROZEN_CONFIG (no weight hash change)."""
    ch = False
    if "frozen_script_sha256" not in cfg:
        cfg["frozen_script_sha256"] = {s: _fsha(s) for s in SPEC.get("scripts", SCRIPTS_B4)}; ch = True
    if "leg_pins" not in cfg and check_json and _abs(check_json).exists():
        legs = json.loads(_abs(check_json).read_text()).get("legs", {})
        last = {}
        for k, p in legs.items():
            s = pd.read_parquet(_abs(p), columns=["session"]).session.astype(str).str[:10].max(); last[k] = s
        cfg["leg_pins"] = {k: dict(path=p, sha256=_fsha(p), last_date=last[k]) for k, p in legs.items()}; ch = True
    return ch


def content_gate(new_path, cfg, last_pin_date):
    """(1) leg history <= pinned last_date row-by-row; (2) leg recomputed by frozen script + has .check.json;
    (3) cadence (separately); (4) frozen-script shas in .check.json == FROZEN_CONFIG."""
    bad, legs_out, missing, revs = [], {}, [], []
    cj = _abs(str(new_path).replace(".parquet", ".check.json"))
    if not cj.exists():
        return dict(pass_=False, reason="combo .check.json missing")
    c = json.loads(cj.read_text()); want = cfg.get("frozen_script_sha256", {})
    got = c.get(SHA_FIELD)
    if not isinstance(got, dict):
        missing.append(f"{cj.name}: {SHA_FIELD}"); bad.append(f"combo .check.json lacks {SHA_FIELD}")
    else:
        for s, h in want.items():
            if got.get(s) != h: bad.append(f"script changed/missing: {s} (check {str(got.get(s))[:12]} vs pinned {h[:12]})")
    for k, p in c.get("legs", {}).items():
        pin = cfg.get("leg_pins", {}).get(k); r = dict(path=p)
        if pin is None:
            bad.append(f"{k}: no leg pin in FROZEN_CONFIG"); legs_out[k] = r; continue
        h = _hist_rows_equal(pin["path"], p, pin["last_date"], freeze_end=FROZEN_END, leg=k); r["history"] = h
        revs.extend(h["revisions"])
        if not h["pass_"]: bad.append(f"{k}: history vs pin <= {pin['last_date']} failed ({h.get('fail_reason')})")
        same = _fsha(p) == pin["sha256"]
        lj = _leg_check_json(p); r["leg_check_json"] = str(lj) if lj else None
        if same and p == pin["path"]:
            r["note"] = "unchanged pinned leg"
        elif lj is None:
            bad.append(f"{k}: leg .check.json missing"); missing.append(f"{Path(p).name}.check.json (with recomputed_with_frozen_script, {SHA_FIELD})")
        else:
            lc = json.loads(lj.read_text())
            if lc.get("recomputed_with_frozen_script") is not True: bad.append(f"{k}: leg not marked recomputed_with_frozen_script")
            ls = lc.get(SHA_FIELD)
            if not isinstance(ls, dict):
                bad.append(f"{k}: leg .check.json lacks {SHA_FIELD}"); missing.append(f"{lj.name}: {SHA_FIELD}")
            elif ls.get(LEG_SCRIPT[k]) != want.get(LEG_SCRIPT[k]):
                bad.append(f"{k}: leg script sha != pinned ({LEG_SCRIPT[k]})")
        legs_out[k] = r
    dc = deferral_check(c, last_pin_date)
    if not dc["pass_"]: bad.append(dc["reason"])
    return dict(pass_=not bad, reason="; ".join(bad) or None, legs=legs_out, ai_must_add=sorted(set(missing)) or None,
                last_pin_date=last_pin_date, leg_revision_audit=revs, revision_window=[FROZEN_END, last_pin_date], deferral=dc)


def deferral_check(c, last_pin_date):
    """Cadence relaxation for a deferred rebalance (booked-day rule): allowed for exactly ONE trading day after the last booked day."""
    from quantlab.portfolio import trade_calendar as T
    bd = c.get("booked_days") or {}; dd = bd.get("deferred_rebalance_day")
    if not dd: return dict(pass_=True, deferred=None)
    lb = bd.get("booked_last") or last_pin_date
    nxt = str(T.first_trading_day_on_or_after(pd.Timestamp(lb) + pd.Timedelta(days=1)).date())
    ok = dd == nxt and lb == last_pin_date
    return dict(pass_=bool(ok), deferred=dd, booked_last=lb, allowed=nxt,
                reason=None if ok else f"deferred rebalance {dd} not exactly one trading day after booked {lb} (allowed {nxt}; pin {last_pin_date})")


def rehash(new60, new100, dry_run=False, receipt=None):
    fz = OUT / "FROZEN_CONFIG.json"
    freeze_check()
    cfg = json.loads(fz.read_text())
    res = dict(ts=now_et(), aum={})
    cur_cj = {c: str(v["path"]).replace(".parquet", ".check.json") for c, v in cfg["weights"].items()}
    if ensure_pins(cfg, cur_cj.get("600000")) and not dry_run:
        fz.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    for cap, newp in ((600000, new60), (1000000, new100)):
        old = cfg["weights"][str(cap)]
        lpd = str(_wtab(old["path"]).index.get_level_values(0).max().date())   # last pin date of the current frozen file
        r = check_extension(old["path"], newp, end=lpd)
        nl = _wtab(newp).index.get_level_values(0).max()
        cc = cadence_check(newp, nl); r["cadence"] = cc
        cg = content_gate(newp, cfg, lpd); r["content_gate"] = cg
        r["ok"] = bool(r["ok"] and cc["pass_"] and cg["pass_"])
        r.update(old_path=old["path"], old_sha256=old["sha256"], new_path=str(newp),
                 new_sha256=hashlib.sha256(_abs(newp).read_bytes()).hexdigest())
        res["aum"][str(cap)] = r
    res["ok"] = all(v["ok"] for v in res["aum"].values())
    print(json.dumps(res, indent=2, ensure_ascii=False, default=str))
    if not res["ok"]:
        print("REHASH REFUSED: checks failed; FROZEN_CONFIG.json unchanged"); return 1
    if dry_run:
        print("REHASH CHECK PASSED (dry-run; FROZEN_CONFIG.json unchanged)"); return 0
    cfg.setdefault("rehash_history", []).append(dict(ts=res["ts"], **{c: dict(old_sha256=v["old_sha256"], new_sha256=v["new_sha256"],
                                                                              old_path=v["old_path"], new_path=v["new_path"],
                                                                              leg_revision_audit=v["content_gate"]["leg_revision_audit"],
                                                                              deferral=v["content_gate"]["deferral"]) for c, v in res["aum"].items()}))
    for c, v in res["aum"].items():   # audit list also into the new combo .check.json
        cj = _abs(str(v["new_path"]).replace(".parquet", ".check.json")); j = json.loads(cj.read_text())
        j["leg_revision_audit"] = v["content_gate"]["leg_revision_audit"]; j["leg_revision_window"] = v["content_gate"]["revision_window"]
        cj.write_text(json.dumps(j, ensure_ascii=False, indent=1, default=str))
    for c, v in res["aum"].items():
        cfg["weights"][c] = dict(path=v["new_path"], sha256=v["new_sha256"])
    nl = json.loads(_abs(str(res["aum"]["600000"]["new_path"]).replace(".parquet", ".check.json")).read_text()).get("legs", {})
    for k, p in nl.items():
        cfg.setdefault("leg_pins", {})[k] = dict(path=p, sha256=_fsha(p),
                                                 last_date=pd.read_parquet(_abs(p), columns=["session"]).session.astype(str).str[:10].max())
    fz.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    rp = _abs(receipt or f"docs/v2/{SPEC['rehash_prefix']}_{datetime.now(ZoneInfo('America/New_York')).strftime('%Y%m%d_%H%M%S')}_ZH.md")
    L = [f"# {SPEC['title']} 权重换哈希回执（{res['ts']}）", "", "live=false；promotion=false；仅纸面。", "",
         "| AUM | 旧路径 | 旧 sha256 | 新路径 | 新 sha256 | 历史逐行一致（≤1e-8） | 新增行检查 |", "|---|---|---|---|---|---|---|"]
    for c, v in res["aum"].items():
        h, b = v["history_match"], v["new_rows"]
        L.append(f"| {c} | {v['old_path']} | {v['old_sha256']} | {v['new_path']} | {v['new_sha256']} | 通过（{h['rows']} 行，最大差 {h['max_abs_diff']:.1e}） | "
                 f"通过（新增 {b.get('new_sessions', 0)} 日，单名最大 {b.get('max_single', 0):.4f}，负权 {b.get('n_neg', 0)}） |")
    rp.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"REHASH APPLIED; receipt {rp}")
    return 0


def _load_cfg_weights():
    fz = OUT / "FROZEN_CONFIG.json"
    if fz.exists():
        for c, v in json.loads(fz.read_text())["weights"].items():
            WEIGHTS[int(c)] = v["path"]


def run(argv=None):
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["backfill", "forward", "monitor", "all", "rehash"], default="monitor")
    ap.add_argument("--new-60w"); ap.add_argument("--new-100w"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--receipt")
    a = ap.parse_args(argv)
    _load_cfg_weights()
    if a.mode == "rehash":
        if not (a.new_60w and a.new_100w):
            print("rehash needs --new-60w and --new-100w"); return 2
        return rehash(a.new_60w, a.new_100w, dry_run=a.dry_run, receipt=a.receipt)
    if a.mode in ("backfill", "all"): backfill()
    if a.mode in ("forward", "all"): forward()
    if a.mode in ("monitor", "all"): monitor()
    return 0
