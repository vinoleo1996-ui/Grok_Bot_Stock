#!/usr/bin/env python3
"""B4 paper track daily extend (idempotent). Paper only; promotion=false; live=false; no Book-Smoke; no 8787.

Frozen rule (same as research/small_aum_conc_lib.py run_group, variant topN, unchanged):
  legs capacity_adv/earnings_event/insider_increase mixed 50/25/25; per leg keep top-N stock names by weight
  (60w N=6, 100w N=10), renormalize to the leg's stock budget; ETF parts pass through; portfolio merged
  single-name cap 6%, overflow -> 510300.SH; normalize to sum 1.

Usage:
  python3 research/b4_paper_extend.py                 # use newest leg weight files found in output/ai_factory
  python3 research/b4_paper_extend.py --legs-only-check  # just report data/leg end dates
  python3 research/b4_paper_extend.py --run-legs      # first re-run the frozen leg scripts to latest data date
Writes output/small_aum_concentration/v2/B_B4_50_25_25_topN_{60w,100w}_<YYYYMMDD>.parquet (+ .check.json).
Never overwrites: if the target exists with identical content, it is a no-op (idempotent); if it differs, abort.
Self-check (abort on fail): rows with session <= FROZEN_END match frozen files row-by-row (|dw|<=1e-8, same
keys/order/metadata); new rows: single stock <= 6%, daily sum == 1 (1e-9), no negative weights.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, subprocess, sys
from pathlib import Path
# paper-extend path only: lift the X2 asof_extend clip (research default stays frozen at 2026-10-09)
os.environ.setdefault("QL_X2_EXTEND_END", "2026-12-31")
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
AF = ROOT / "output/ai_factory"; OUT = ROOT / "output/small_aum_concentration/v2"
MIX = {"capacity_adv": 0.5, "earnings_event": 0.25, "insider_increase": 0.25}
N = {600000: 6, 1000000: 10}; CAP = 0.06; BAL = "510300.SH"; TOL = 1e-8
FROZEN_END = "2026-10-09"
REV = "r2"  # 2026-10-13 Strategy ruling: re-overlay on any leg change day (daily rebuild from legs)
STATUS = ROOT / "output/daily_update_status.json"
FROZEN = {600000: OUT / "B_B4_50_25_25_topN_60w.parquet", 1000000: OUT / "B_B4_50_25_25_topN_100w.parquet"}
FROZEN_LEGS = {"capacity_adv": AF / "g1g5_capacity_adv_daily_weights_20261013_111219.parquet",
               "earnings_event": AF / "g1g5_earnings_event_daily_weights_20261014_005430.parquet",
               "insider_increase": AF / "g1g5_insider_increase_daily_weights_20261014_011841.parquet"}
etf = lambda x: x[:2] in ("51", "56", "58", "15")
# scripts pinned in output/strategy_paper_b4/FROZEN_CONFIG.json (Eng content gate); recorded as frozen_script_sha256
TRACK_SCRIPTS = ["research/b4_paper_extend.py", "research/capacity_adv_paper_extend.py", "research/g1g5_capacity_adv_weights.py",
                 "research/g1g5_earnings_event_weights.py", "research/g1g5_insider_increase_weights.py"]
LEG_SCRIPTS = {"capacity_adv": ["research/capacity_adv_paper_extend.py", "research/g1g5_capacity_adv_weights.py"],
               "earnings_event": ["research/g1g5_earnings_event_weights.py"],
               "insider_increase": ["research/g1g5_insider_increase_weights.py"],
               "equity_incentive": ["research/g1g5_equity_incentive_weights.py"]}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()


def script_shas(paths) -> dict:
    return {p: (sha(ROOT / p) if (ROOT / p).exists() else "MISSING") for p in paths}


def leg_check_path(p: Path) -> Path:
    return Path(str(p) + ".check.json")


def write_leg_check(k: str, p: Path, recomputed: bool, basis: str, extra: dict | None = None) -> dict:
    """<leg>.parquet.check.json for the Eng content gate. Call only right after the frozen script produced p."""
    c = leg_hist_check(k, p) if k in FROZEN_LEGS else {}
    d = pd.read_parquet(p, columns=["session", "weight"]); d["session"] = d.session.astype(str).str[:10]
    new = d[d.session > FROZEN_END]
    r = dict(leg=k, file=str(p.relative_to(ROOT)), sha256=sha(p), recomputed_with_frozen_script=bool(recomputed), basis_zh=basis,
             first_date=d.session.min(), last_date=d.session.max(), rows=int(len(d)),
             frozen_ref=str(FROZEN_LEGS[k].relative_to(ROOT)) if k in FROZEN_LEGS else None, history_cutoff=FROZEN_END,
             history_keys_identical=c.get("keys_identical"), history_max_abs_diff=c.get("max_abs_diff"), history_ok=c.get("ok"),
             new_sessions=sorted(new.session.unique().tolist()), new_rows=int(len(new)),
             new_sum_ok=bool(((new.groupby("session").weight.sum() - 1).abs() < 1e-9).all()), new_nonneg=bool((new.weight >= 0).all()),
             frozen_script_sha256=script_shas(LEG_SCRIPTS[k]), promotion_approved=False, live=False)
    if extra: r.update(extra)
    leg_check_path(p).write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    return r


def data_end() -> str:
    from research.ai_debate_memory_runner import _load_benchmark_closes
    from research.g1g5_x2_panel_stitch import load_panel_features_x2
    ends = [_load_benchmark_closes("510300").index.max()] + [load_panel_features_x2(s).index.max() for s in ("600036.SH", "000001.SZ")]
    return str(min(pd.Timestamp(e) for e in ends).date())


def newest_leg(k: str) -> Path:
    fs = sorted(glob.glob(str(AF / f"g1g5_{k}_daily_weights_2*.parquet")))
    if k == "capacity_adv":  # capacity_adv leg is extended by research/capacity_adv_paper_extend.py
        fs += sorted(glob.glob(str(AF / "g1g5_capacity_adv_daily_weights_paper_2*.parquet")))
    fs = [Path(f) for f in fs if not f.endswith(".meta.json") and not f.endswith(".check.json")]
    # prefer leg files that carry <file>.parquet.check.json (Eng content gate); fall back to frozen leg
    best = FROZEN_LEGS[k]; bend = leg_end(best); bchk = leg_check_path(best).exists()
    for f in fs:
        e, chk = leg_end(f), leg_check_path(f).exists()
        if (chk, e) >= (bchk, bend): best, bend, bchk = f, e, chk
    return best


def leg_end(p: Path) -> str:
    return str(pd.read_parquet(p, columns=["session"]).session.astype(str).str[:10].max())


def leg_hist_check(k: str, p: Path) -> dict:
    """History check of a recomputed leg vs its frozen leg on sessions <= FROZEN_END (Eng 2026-10-14, outer-join).
    Outer-join on (session, instrument), missing -> 0, then |dw| <= TOL. Strict: an instrument present on only one
    side must be all-zero over the compared history, else fail and name it. Duplicate keys or a changed session set fail."""
    F = pd.read_parquet(FROZEN_LEGS[k], columns=["session", "instrument", "weight"]); F["session"] = F.session.astype(str).str[:10]
    N_ = pd.read_parquet(p, columns=["session", "instrument", "weight"]); N_["session"] = N_.session.astype(str).str[:10]
    H = N_[N_.session <= FROZEN_END].reset_index(drop=True)
    keys_identical = len(H) == len(F) and (H[["session", "instrument"]].values == F[["session", "instrument"]].values).all()
    dup = int(H.duplicated(["session", "instrument"]).sum() + F.duplicated(["session", "instrument"]).sum())
    sess_ok = set(H.session) == set(F.session)
    M = F.merge(H, on=["session", "instrument"], how="outer", suffixes=("_f", "_n"), indicator=True)
    M[["weight_f", "weight_n"]] = M[["weight_f", "weight_n"]].fillna(0.0)
    d = (M.weight_f - M.weight_n).abs(); dmax = float(d.max()) if len(d) else 0.0
    fi, ni = set(F.instrument), set(H.instrument)
    def nz(cols, w):
        return sorted(i for i in cols if float(M.loc[M.instrument == i, w].abs().max()) > TOL)
    only_new, only_old = sorted(ni - fi), sorted(fi - ni)
    bad_new, bad_old = nz(only_new, "weight_n"), nz(only_old, "weight_f")
    bad_rows = M[d > TOL]
    ok = bool(dup == 0 and sess_ok and not bad_new and not bad_old and dmax <= TOL)
    r = dict(file=str(p.relative_to(ROOT)), keys_identical=bool(keys_identical), compare="outer_join_fill0", max_abs_diff=dmax,
             rows_only_in_new=int((M._merge == "right_only").sum()), rows_only_in_frozen=int((M._merge == "left_only").sum()),
             cols_only_in_new=only_new, cols_only_in_frozen=only_old, zero_cols_added=[i for i in only_new if i not in bad_new],
             sessions_identical=bool(sess_ok), duplicate_keys=dup, ok=ok)
    if not ok:
        r["fail_reason"] = "; ".join(x for x in [
            f"nonzero one-sided columns new={bad_new} frozen={bad_old}" if (bad_new or bad_old) else "",
            f"max_abs_diff {dmax:.3g} > {TOL} at {sorted(set(bad_rows.instrument))[:20]}" if dmax > TOL else "",
            "session set differs" if not sess_ok else "", f"duplicate keys {dup}" if dup else ""] if x)
    return r


def splice_booked(W: pd.DataFrame, booked_path: Path) -> tuple[pd.DataFrame, dict]:
    """Booked-day rule (主 Agent 2026-10-14): sessions already booked (FROZEN_END < s <= booked last) keep their booked rows;
    recomputed weights take effect from the next session. Returns (W', audit of booked vs recomputed)."""
    B_ = pd.read_parquet(booked_path); B_["session"] = B_.session.astype(str).str[:10]
    bl = B_.session.max(); win = lambda x: (x.session > FROZEN_END) & (x.session <= bl)
    bk = B_[win(B_)][W.columns.tolist()]; rc = W[win(W)]
    m = bk[["session", "instrument", "weight"]].merge(rc[["session", "instrument", "weight"]], on=["session", "instrument"],
                                                      how="outer", suffixes=("_booked", "_recomputed")).fillna(0.0)
    diff = m[(m.weight_booked - m.weight_recomputed).abs() > TOL].sort_values(["session", "instrument"])
    out = pd.concat([W[W.session <= FROZEN_END], bk, W[W.session > bl]]).sort_values(["session", "instrument"], kind="mergesort").reset_index(drop=True)
    nxt = sorted(x for x in W.session.unique() if x > bl)
    deferred = nxt[0] if (len(diff) and nxt) else None   # booked-day rule: the deferred recompute lands on the next session
    if deferred:   # exactly one SSE trading day after the last booked day, nothing later
        from quantlab.portfolio import trade_calendar as T
        assert deferred == str(T.first_trading_day_on_or_after(pd.Timestamp(bl) + pd.Timedelta(days=1)).date()), f"deferral {deferred} > 1 trading day after {bl}"
    return out, dict(deferred_rebalance_day=deferred, booked_file=str(booked_path.relative_to(ROOT)), booked_last=bl, rule="booked days never rewritten; recompute effective from next session",
                     n_diff_rows=int(len(diff)), diff=diff.to_dict("records"))


def booked_path(track_dir: Path, aum: int) -> Path | None:
    f = track_dir / "FROZEN_CONFIG.json"
    if not f.exists(): return None
    p = ROOT / json.loads(f.read_text())["weights"][str(aum)]["path"]
    return p if p.exists() and leg_end(p) > FROZEN_END else None


def run_legs(end: str) -> None:
    # capacity_adv: paper extend (frozen history + carry-forward / frozen month-end rebalance)
    env = dict(os.environ, QL_X2_EXTEND_END=end, PYTHONHASHSEED="0")
    subprocess.run([sys.executable, "research/capacity_adv_paper_extend.py", "--end", end], cwd=ROOT, check=True, env=env)
    # event legs: frozen scripts, only WEIGHT_END moved (sequential, each ~1.1-1.2 GB peak)
    for k in ("earnings_event", "insider_increase"):
        run_event_leg(k, end, env)


def run_event_leg(k: str, end: str, env: dict) -> Path:
    """Re-run the frozen leg script (code untouched; only WEIGHT_END moved) and write its .parquet.check.json."""
    before = set(glob.glob(str(AF / f"g1g5_{k}_daily_weights_2*.parquet")))
    code = (f"import sys; sys.path.insert(0,'.'); import research.g1g5_{k}_weights as m; "
            f"m.WEIGHT_END='{end}'; m.run()")
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True, env=env)
    new = sorted(set(glob.glob(str(AF / f"g1g5_{k}_daily_weights_2*.parquet"))) - before)
    new = [Path(f) for f in new if f.endswith(".parquet")]
    assert len(new) == 1, f"{k}: expected exactly one new leg file, got {new}"
    write_leg_check(k, new[0], True, f"由本脚本 run_event_leg 刚刚调用冻结脚本 research/g1g5_{k}_weights.py 重算（仅 WEIGHT_END={end}，PYTHONHASHSEED={env.get('PYTHONHASHSEED')}）")
    return new[0]


def build(legs: dict[str, Path], aum: int) -> pd.DataFrame:
    D = {}
    for k, p in legs.items():
        d = pd.read_parquet(p, columns=["session", "instrument", "weight"]); d["session"] = d.session.astype(str).str[:10]
        D[k] = d[d.weight > 0]
    sess = sorted(set.intersection(*[set(d.session) for d in D.values()]))
    G = {k: {s: g.set_index("instrument").weight for s, g in d.groupby("session")} for k, d in D.items()}
    rows = []
    for s in sess:
        agg = {}
        for k, m in MIX.items():
            w = G[k].get(s)
            if w is None: continue
            w = w * m
            e = w[[etf(i) for i in w.index]]; st = w.drop(e.index)
            for i, v in e.items(): agg[i] = agg.get(i, 0) + v
            if not len(st): continue
            keep = st.sort_values(ascending=False).head(N[aum]); keep = keep * st.sum() / keep.sum()
            for i, v in keep.items(): agg[i] = agg.get(i, 0) + v
        for i in list(agg):
            if not etf(i) and agg[i] > CAP:
                agg[BAL] = agg.get(BAL, 0) + agg[i] - CAP; agg[i] = CAP
        t = sum(agg.values()); rows += [(s, i, v / t) for i, v in agg.items()]
    W = pd.DataFrame(rows, columns=["session", "instrument", "weight"]).groupby(["session", "instrument"], as_index=False).weight.sum()
    W["date"] = W.session; W["target_weight"] = W.weight
    W["instrument_id"] = W.instrument.map(lambda x: x[-2:].lower() + "." + x[:6])
    W["mechanism_tag"] = f"small_aum_conc_v2_topN_B4_50_25_25_{aum // 10000}w"
    W["who_pays_zh"] = "执行层整手集中化 v2（研究混合）"; W["universe_id"] = "conc_v2"
    return W


def change_days(df: pd.DataFrame, col: str = "weight") -> list:
    d = df.copy(); d["session"] = d.session.astype(str).str[:10]
    P = d.pivot_table(index="session", columns="instrument", values=col, aggfunc="sum").fillna(0).sort_index()
    return [x for x in P.index[(P.diff().abs() > 1e-12).any(axis=1)]]


LEG_CHG: set = set()


def check(W: pd.DataFrame, aum: int) -> dict:
    F = pd.read_parquet(FROZEN[aum]); H = W[W.session <= FROZEN_END].reset_index(drop=True)
    keys_ok = len(H) == len(F) and (H[["session", "instrument"]].values == F[["session", "instrument"]].values).all()
    dmax = float(np.abs(H.weight.values - F.weight.values).max()) if keys_ok else float("inf")
    meta_ok = keys_ok and all((H[c].astype(str).values == F[c].astype(str).values).all()
                              for c in ("date", "instrument_id", "mechanism_tag", "who_pays_zh", "universe_id"))
    tw_ok = keys_ok and float(np.abs(H.target_weight.values - F.target_weight.values).max()) <= TOL
    new = W[W.session > FROZEN_END]; stk = new[[not etf(i) for i in new.instrument]]
    r = dict(hist_rows=len(H), frozen_rows=len(F), hist_keys_identical=bool(keys_ok), hist_max_abs_diff=dmax,
             hist_meta_identical=bool(meta_ok), hist_ok=bool(keys_ok and meta_ok and tw_ok and dmax <= TOL),
             new_rows=len(new), new_sessions=sorted(new.session.unique().tolist()),
             new_max_single_stock=float(stk.weight.max()) if len(stk) else None,
             new_sum_ok=bool(((new.groupby("session").weight.sum() - 1).abs() < 1e-9).all()),
             new_nonneg=bool((new.weight >= 0).all()),
             new_cap_ok=bool(stk.weight.max() <= CAP + 1e-9) if len(stk) else True)
    F2 = F.copy(); bchg_f = change_days(F2); bchg_w = [x for x in change_days(W) if x <= FROZEN_END]
    fchg = [x for x in change_days(W[W.session >= FROZEN_END]) if x > FROZEN_END]
    r["hist_change_days_identical"] = bool(bchg_f == bchg_w)
    r["new_change_days"] = fchg; r["leg_change_days_forward"] = sorted(x for x in LEG_CHG if x > FROZEN_END)
    r["rhythm_ok"] = bool(r["hist_change_days_identical"] and set(fchg) <= LEG_CHG)
    r["ok"] = r["rhythm_ok"] and r["hist_ok"] and r["new_sum_ok"] and r["new_nonneg"] and r["new_cap_ok"]
    return r


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-legs", action="store_true"); ap.add_argument("--legs-only-check", action="store_true")
    a = ap.parse_args()
    dend = data_end()
    if a.run_legs and any(leg_end(newest_leg(k)) < dend for k in MIX): run_legs(dend)
    legs = {k: newest_leg(k) for k in MIX}; lend = {k: leg_end(p) for k, p in legs.items()}
    lchk = {k: leg_hist_check(k, p) for k, p in legs.items()}
    for k, p in legs.items():
        LEG_CHG.update(change_days(pd.read_parquet(p, columns=["session", "instrument", "weight"])))
    st = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    fresh = {t: (v or {}).get("last_date") for t, v in (st.get("tables") or {}).items()}
    info = dict(data_end=dend, legs={k: str(p.relative_to(ROOT)) for k, p in legs.items()}, leg_end=lend,
                params=dict(mix=MIX, N=N, cap=CAP, ballast=BAL), leg_hist_check=lchk, daily_update_status=dict(target_trade_date=st.get("target_trade_date"), status=st.get("status"), mid_large_universe=fresh.get("mid_large_universe")), promotion_approved=False, live=False,
                forward_paper_start="2026-11-02")
    if min(lend.values()) < dend:
        info["warning"] = "leg weights stale vs data_end; run with --run-legs"
    if a.legs_only_check:
        print(json.dumps(info, ensure_ascii=False, indent=1)); return 0
    if not all(v["ok"] for v in lchk.values()):
        print(json.dumps(dict(info, status="ABORT_LEG_HISTORY_MISMATCH"), ensure_ascii=False, indent=1)); return 4
    rc = 0
    for aum in (600000, 1000000):
        W = build(legs, aum); bp = booked_path(ROOT / "output/strategy_paper_b4", aum); booked = None
        if bp is not None:
            W, booked = splice_booked(W, bp)
            if booked["deferred_rebalance_day"]: LEG_CHG.add(booked["deferred_rebalance_day"])
            # Option A (Arch APPROVE 20261026): booked-window realized change days stay in LEG_CHG across re-extends
            # Hotfix: use .update (not |=) so module-global LEG_CHG is not treated as local in main()
            LEG_CHG.update(change_days(pd.read_parquet(bp, columns=["session", "instrument", "weight"])))
        last = W.session.max(); c = check(W, aum)
        fp = OUT / f"B_B4_50_25_25_topN_{aum // 10000}w_{last.replace('-', '')}_{REV}.parquet"
        res = dict(info, aum=aum, last_session=last, check=c, file=str(fp.relative_to(ROOT)), frozen_script_sha256=script_shas(TRACK_SCRIPTS),
                   leg_sha256={k: sha(p) for k, p in legs.items()}, leg_check_json={k: leg_check_path(p).exists() for k, p in legs.items()},
                   frozen_file=str(FROZEN[aum].relative_to(ROOT)), frozen_sha256=sha(FROZEN[aum]), booked_days=booked)
        if not c["ok"]:
            res["status"] = "ABORT_SELFCHECK"; rc = 2
        else:
            tmp = fp.with_suffix(".tmp.parquet"); W.to_parquet(tmp, index=False)
            if fp.exists():
                same = pd.read_parquet(fp).equals(pd.read_parquet(tmp)); tmp.unlink()
                res["status"] = "NOOP_EXISTS_IDENTICAL" if same else "ABORT_EXISTS_DIFFERENT"; rc = rc or (0 if same else 3)
            else:
                tmp.rename(fp); res["status"] = "WRITTEN"
            if fp.exists(): res["sha256"] = sha(fp)
        fp.with_suffix(".check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(json.dumps({k: res[k] for k in ("aum", "last_session", "status", "file") if k in res} | {"hist_ok": c["hist_ok"], "max_diff": c["hist_max_abs_diff"], "new_rows": c["new_rows"], "sha256": res.get("sha256")}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
