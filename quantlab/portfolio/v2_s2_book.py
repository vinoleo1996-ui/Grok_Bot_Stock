"""S2 runner: V2 book = 510300 core + Beta standalone smallcap sleeve + Alpha MAINBOOK_V2
residual (idle cash <= 5%), executed on Eng's platform engine
(``run_weight_schedule`` + ``ExecConfig.strategy_v1(impact_k=1.0)``, record_weights=True),
plus the C0-C8 controls of QuantLab-V2_REBUILD_PLAN_ZH.md and one-variable comparison arms.

Research only, promotion_approved=false.
Windows (docs/v2/PREREGISTRATION_V2_ZH.md): --start 2018-01-02 .. 2024-05-31 = dev/validation;
2024-06 onward = exploration. Nothing here is promotion evidence.
Smallcap sleeve: SmallcapBetaSleeveProvider(mandate, data_source="history_2015",
basket_cache=...) with optional precompute_history_baskets into
output/strategy_s2/basket_cache/.

Two phases (memory-safe): (1) signals per rebalance session -> signals.parquet
(Beta provider panels freed afterwards); (2) execution of each arm, one at a time,
NAV/weights written and frames dropped before the next arm.

Arms (one variable each vs the V2 main book "V2"):
  V2         510300 (VolTarget core) + smallcap T15 + MAINBOOK_V2 top-N residual, cash target 5%
  V2_T10/V2_T20  smallcap tier only
  V2_EXCL30  residual universe keeps the bottom-30% float-mktcap exclusion (Leo: comparison only)
  V2_LIVE600K  smallcap via Beta live 600k profile (20-30 names, retention), capital 600k
  C0  510300 buy & hold (cash target)
  C1  equal-weight full-A (as-of D1 universe members)
  C2  510300 + static smallcap basket at V2's mean weights, no timing, rest cash
  C3  same-vol static heavy smallcap (sleeve weight scaled to V2 ex-ante vol), rest cash
  C4  ex-post best static weights over component sleeves (report only, not a verdict)
  C5  C2 + down-only per-sleeve vol scaling (target = trailing 250d median vol)
  C6  random smallcap baskets (same band pool, same N) - component-return approximation
  C7  constant exposure (V2 mean invested, engine) + circular-shift placebo (component space)
  C8  V2 zero-cost vs full-cost + platform/ledger/fastsim zero-cost reconcile
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import resource
import sys
import time
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ETF = "sh.510300"
EXPLORATION_START = pd.Timestamp("2024-06-01")
DEV_END = pd.Timestamp("2024-05-31")
ALL_ARMS = ["V2", "V2_T10", "V2_T20", "V2_EXCL30", "V2_LIVE600K",
            "C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
ENGINE_ARMS = {"V2", "V2_T10", "V2_T20", "V2_EXCL30", "V2_LIVE600K", "C0", "C1", "C2", "C3", "C5", "C7", "C8"}
HASH_FILES = [
    "data/v2/ep/ep_pit_daily_tushare.parquet",
    "data/v2/ep/ep_pit_daily_tushare_acceptance.json",
    "data/v2/valuation/daily_basic_valuation_tushare.parquet",
    "data/v2/float_mktcap/float_mktcap_daily_tushare.parquet",
    "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet",
    "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet",
    "data/v2/delisted/delisted_master_tushare.parquet",
    "data/v2/st_flags/is_st_daily_2018_2026.parquet",
    "quantlab/beta/configs/smallcap_standalone_v1.json",
    "output/research_attrib_v2/panels/etf510300.parquet",
    "docs/v2/PREREGISTRATION_V2_ZH.md",
]


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _log(msg: str) -> None:
    print(f"[s2 {time.strftime('%H:%M:%S')} rss={_rss_mb():.0f}MB] {msg}", flush=True)


def _sha256(p: Path, chunk: int = 1 << 22) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def provenance() -> dict:
    hashes = {}
    for rel in HASH_FILES:
        p = ROOT / rel
        hashes[rel] = dict(sha256=_sha256(p), bytes=p.stat().st_size if p.exists() else None)
    ep_acc = {}
    try:
        a = json.loads((ROOT / "data/v2/ep/ep_pit_daily_tushare_acceptance.json").read_text())
        ep_acc = {k: a.get(k) for k in ("rows", "dates", "date_min", "date_max", "instruments", "coverage_overall", "future_leak_rows")}
    except Exception as e:  # noqa: BLE001
        ep_acc = {"error": repr(e)}
    trials = dict(total=None, by_family={})
    try:
        with open(ROOT / "docs/trial_ledger.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        trials["total"] = len(rows)
        for r in rows:
            trials["by_family"][r.get("family")] = trials["by_family"].get(r.get("family"), 0) + 1
    except Exception as e:  # noqa: BLE001
        trials["error"] = repr(e)
    git = None
    try:
        import subprocess
        git = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or None
    except Exception:  # noqa: BLE001
        pass
    return dict(
        ep_data_version=dict(path="data/v2/ep/ep_pit_daily_tushare.parquet", kind="tushare_pit_daily",
                             sha256=hashes["data/v2/ep/ep_pit_daily_tushare.parquet"]["sha256"], acceptance=ep_acc,
                             note="MAINBOOK_V2 effective members R02/turn_20d/RV60/BP; EP (V01_EP) is NOT a member; recorded for audit"),
        data_hashes=hashes, trial_ledger=trials, git_head=git,
        prereg="docs/v2/PREREGISTRATION_V2_ZH.md",
    )


# ------------------------------------------------------------------ sessions
def trading_sessions(start, end) -> pd.DatetimeIndex:
    e = pd.read_parquet(ROOT / "output/research_attrib_v2/panels/etf510300.parquet")
    idx = pd.DatetimeIndex(e.index).normalize()
    return idx[(idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))]


def rebalance_sessions(sessions: pd.DatetimeIndex, every: int, max_sessions: int | None) -> list[pd.Timestamp]:
    out = list(sessions[::every])
    return out[:max_sessions] if max_sessions else out


def _sw_assignments(sw: pd.DataFrame, session: date, ids):
    from quantlab.v2_schemas import SWL1AsOfAssignment
    d = pd.Timestamp(session)
    m = sw[(sw.in_date <= d) & (sw.out_date > d)].drop_duplicates("instrument_id", keep="last").set_index("instrument_id")
    out = []
    for i in ids:
        if i in m.index:
            r = m.loc[i]
            out.append(SWL1AsOfAssignment(i, session, r.sw_code, r.sw_name, r.available_at.to_pydatetime() if pd.notna(r.available_at) else None,
                                          r.quality_status, False))
        else:
            out.append(SWL1AsOfAssignment(i, session, None, None, None, None, True))
    return out


# ------------------------------------------------------------------ phase 1
def build_signals(rebals, *, pool_limit: int | None, residual_n: int, cash_target: float, out: Path,
                 basket_cache: str | Path | None = None) -> pd.DataFrame:
    """One row per (session, component, instrument, book weight) for every variant needed."""
    from quantlab.beta import SmallcapBetaSleeveProvider, VolTargetBetaSleeveProvider
    from quantlab.factors.p1_pipeline import mainbook_v2_d1_config, run_mainbook_v2_session
    from quantlab.mandate_v2 import load_mandate_v2
    from quantlab.universe.d1_masks import build_d1_masks_for_session

    m = load_mandate_v2()
    core_p = VolTargetBetaSleeveProvider(m)
    sc = SmallcapBetaSleeveProvider(m, data_source="history_2015", basket_cache=basket_cache)
    sw = pd.read_parquet(ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet")
    sw["out_date"] = sw["out_date"].fillna(pd.Timestamp("2100-01-01"))
    rows, meta = [], []
    prev_sc: dict[str, list[str]] = {}
    max_name = float(m.portfolio_limits.__dict__.get("max_single_name_weight", 0.05) or 0.05)
    for k, ts in enumerate(rebals):
        s = ts.date()
        t0 = time.time()
        core = core_p.plan(s)
        etf_w = float(core.etf_sleeve_weight or 0.0)
        max_etf = float(core.max_etf_sleeve_weight)
        cfg = mainbook_v2_d1_config()
        mask = build_d1_masks_for_session(s, config=cfg)
        uni = list(mask.member_ids)
        fr = mask.frame.set_index("instrument_id")
        if pool_limit:
            step = max(1, len(uni) // pool_limit)
            uni = uni[::step][:pool_limit]
        mc = fr["float_mktcap"].reindex(uni)
        cut30 = mc.quantile(0.30)
        excl30 = set(mc.index[mc < cut30])
        res = run_mainbook_v2_session(s, uni, float_mktcap=None, sw_l1=_sw_assignments(sw, s, uni))
        assert res.promotion_approved is False
        scores = pd.Series(res.composite.scores, dtype=float).dropna().sort_values(ascending=False)
        tiers = {}
        plan = sc.plan(s, current=prev_sc.get("research"), core_plan=core)
        for t in ("T10", "T15", "T20"):
            tiers[t] = dict(plan.tiers[t].name_weights)
        live = sc.live_basket(plan.basket, "T15", current=prev_sc.get("live"))
        prev_sc["research"] = list(plan.basket.names)
        prev_sc["live"] = list(live["names"])
        live_w = {c: 0.15 / max(1, len(live["names"])) for c in live["names"]}
        pool = list(plan.basket.ranked_pool)

        def emit(variant, comp, w: dict):
            for c, x in w.items():
                if x > 0:
                    rows.append((ts, variant, comp, c, float(x)))

        for variant, scw, excl in (("V2", tiers["T15"], False), ("V2_T10", tiers["T10"], False),
                                   ("V2_T20", tiers["T20"], False), ("V2_EXCL30", tiers["T15"], True),
                                   ("V2_LIVE600K", live_w, False)):
            sc_sum = sum(scw.values())
            resid_w = max(0.0, 1.0 - cash_target - etf_w - sc_sum)
            cand = [c for c in scores.index if c not in scw and (not excl or c not in excl30)][:residual_n]
            per = min(max_name, resid_w / max(1, len(cand))) if cand else 0.0
            emit(variant, "etf", {ETF: etf_w})
            emit(variant, "smallcap", scw)
            emit(variant, "residual", {c: per for c in cand})
            meta.append(dict(session=str(s), variant=variant, etf_w=etf_w, smallcap_w=sc_sum, residual_w=per * len(cand),
                             cash_w=1 - etf_w - sc_sum - per * len(cand), n_residual=len(cand), n_smallcap=len(scw),
                             max_etf=max_etf, max_etf_soft_breach=bool(etf_w > max_etf + 1e-12)))
        emit("C1", "eqw_all", {c: (1 - cash_target) / len(uni) for c in uni})
        # random-basket pool for C6 (component approximation)
        rows.extend((ts, "POOL", "sc_pool", c, float(i)) for i, c in enumerate(pool[:200]))
        _log(f"signals {k+1}/{len(rebals)} {s} uni={len(uni)} scored={len(scores)} etf={etf_w:.2f} "
             f"sc={len(tiers['T15'])} live={len(live_w)} crowd={plan.crowding.get('crowding_flag')} {time.time()-t0:.0f}s")
        del mask, fr, res
        gc.collect()
    sig = pd.DataFrame(rows, columns=["session", "variant", "component", "instrument_id", "weight"])
    sig.to_parquet(out / "signals.parquet")
    pd.DataFrame(meta).to_csv(out / "signals_meta.csv", index=False)
    try:  # free Beta provider panels
        from quantlab.beta import smallcap_sleeve as _s
        _s._load_panels_cached.cache_clear()
    except Exception:  # noqa: BLE001
        pass
    try:
        from quantlab.beta.smallcap_history_panels import load_history_panels
        load_history_panels.cache_clear()
    except Exception:  # noqa: BLE001
        pass
    del sc, core_p
    gc.collect()
    return sig


# ------------------------------------------------------------------ panels
def load_panels(ids, start, end, *, delist_mark: float, diag_out: dict):
    from quantlab.platform.execution import load_execution_panels
    p, diag = load_execution_panels(sorted(set(ids)), start, end)
    idx = trading_sessions(start, end)
    fields = ("close", "open", "high", "low", "volume", "amount", "limit_up", "limit_down")
    for f in fields:
        setattr(p, f, getattr(p, f).reindex(idx))
    # Eng load_execution_panels + _extend_fund_panel supplies real 510300 OHLCV
    # through 2026-10-09 from panels/sh.510300.parquet (price_tick auto = 0.001).
    # Do NOT patch open:=close / volume:=1e9.
    if "fund_panel_extended" in diag:
        diag_out["fund_panel_extended"] = diag["fund_panel_extended"]
    # terminal delist mark
    dm = pd.read_parquet(ROOT / "data/v2/delisted/delisted_master_tushare.parquet")
    dm = dm[dm.instrument_id.isin(p.close.columns) & dm.last_trade_date.notna()]
    sus = p.suspended.reindex(index=idx, columns=p.close.columns).fillna(False).astype(bool) if p.suspended is not None \
        else pd.DataFrame(False, index=idx, columns=p.close.columns)
    applied = []
    for r in dm.itertuples():
        after = idx > pd.Timestamp(r.last_trade_date)
        if not after.any():
            continue
        last = p.close.loc[~after, r.instrument_id].dropna()
        if last.empty:
            continue
        p.close.loc[after, r.instrument_id] = np.float32(last.iloc[-1] * (1.0 - delist_mark))
        p.open.loc[after, r.instrument_id] = np.nan
        sus.loc[after, r.instrument_id] = True
        applied.append(r.instrument_id)
    p.suspended = sus
    diag_out["delist_mark"] = -delist_mark
    diag_out["delist_marked_ids"] = applied
    diag_out["loader"] = {k: (v if k != "missing_ids" else v[:50]) for k, v in diag.items()}
    diag_out["n_missing_ids"] = len(diag.get("missing_ids", []))
    return p


# ------------------------------------------------------------------ helpers
def schedule_from(sig: pd.DataFrame, variant: str, components=None, scale: dict | None = None) -> dict:
    d = sig[sig.variant == variant]
    if components:
        d = d[d.component.isin(components)]
    out = {}
    for ts, g in d.groupby("session"):
        w = {}
        for comp, gg in g.groupby("component"):
            k = 1.0 if scale is None else float(scale.get((ts, comp), scale.get(comp, 1.0)))
            for c, x in zip(gg.instrument_id, gg.weight):
                w[c] = w.get(c, 0.0) + x * k
        out[pd.Timestamp(ts)] = w
    return out


def stats(nav: pd.Series) -> dict:
    nav = nav.dropna()
    if len(nav) < 2 or nav.iloc[0] <= 0:
        return dict(n=len(nav))
    r = nav.pct_change().dropna()
    yrs = max(len(r) / 252.0, 1e-9)
    tot = nav.iloc[-1] / nav.iloc[0] - 1
    q = r.quantile(0.05)
    return dict(n=len(nav), start=str(nav.index[0].date()), end=str(nav.index[-1].date()), total_return=float(tot),
                cagr_geo=float((1 + tot) ** (1 / yrs) - 1) if tot > -1 else -1.0,
                vol_ann=float(r.std() * math.sqrt(252)), sharpe=float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else None,
                mdd=float((nav / nav.cummax() - 1).min()), cvar5_daily=float(r[r <= q].mean()) if len(r) else None)


def segmented(nav: pd.Series) -> dict:
    return dict(all=stats(nav), dev_2018_2024_05=stats(nav[nav.index <= DEV_END]),
                exploration_2024_06_on=stats(nav[nav.index >= EXPLORATION_START]),
                by_year={str(y): stats(g) for y, g in nav.groupby(nav.index.year)})


def component_returns(p, sig, variant, comps) -> pd.DataFrame:
    """Daily close-to-close return of each component sleeve (unit weight, held between rebalances)."""
    from quantlab.platform.execution import ExecConfig
    out = {}
    for comp in comps:
        sched = schedule_from(sig, variant, [comp])
        if not sched:
            continue
        tot = {ts: sum(w.values()) for ts, w in sched.items()}
        sched = {ts: {c: x / tot[ts] for c, x in w.items()} for ts, w in sched.items() if tot[ts] > 0}
        nv = _fast_nav(p, sched)
        out[comp] = nv[nv.index >= min(sched)].pct_change()
    return pd.DataFrame(out)


def _fast_nav(p, sched) -> pd.Series:
    """Frictionless weight-held NAV (close-to-close, fixed share count between rebalances)."""
    C = p.close.ffill()
    rets = C.pct_change(fill_method=None).fillna(0.0)
    nav, v, w = [], 1.0, pd.Series(dtype=float)
    keys = sorted(sched)
    k = 0
    for d in C.index:
        if not w.empty:
            v *= 1 + float((w * rets.loc[d].reindex(w.index).fillna(0)).sum())
            gr = (1 + rets.loc[d].reindex(w.index).fillna(0))
            tot = float((w * gr).sum()) + (1 - float(w.sum()))
            w = w * gr / tot if tot > 0 else w
        nav.append(v)
        while k < len(keys) and keys[k] <= d:
            w = pd.Series(sched[keys[k]], dtype=float)
            k += 1
    return pd.Series(nav, index=C.index)


# ------------------------------------------------------------------ main
def run(args) -> dict:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad = [a for a in arms if a not in ALL_ARMS]
    if bad:
        raise SystemExit(f"unknown arms {bad}; valid={ALL_ARMS}")
    t_start = time.time()
    start_ts, end_ts = pd.Timestamp(args.start), pd.Timestamp(args.end)
    if start_ts >= EXPLORATION_START:
        win_label = "exploration"
    elif end_ts <= DEV_END:
        win_label = "dev_validation"
    else:
        win_label = "mixed_dev_and_exploration"
    summary = dict(runner="quantlab.portfolio.v2_s2_book", research_only=True, promotion_approved=False,
                   window=dict(start=args.start, end=args.end, rebalance_every=args.rebalance_every,
                               exploration_from=str(EXPLORATION_START.date()),
                               dev_end=str(DEV_END.date()),
                               label=win_label),
                   rules=dict(unfilled="carry", bottom30_exclusion="dropped_main; V2_EXCL30 comparison", max_etf="soft (breach logged)",
                              one_variable_per_arm=True, terminal_delist_mark=-args.delist_mark, cash_target=args.cash_target,
                              exec="ExecConfig.strategy_v1(impact_k=%s)" % args.impact_k,
                              price_tick="auto", smallcap_data_source="history_2015",
                              smoke=bool(args.smoke)),
                   provenance=provenance(), arms={}, diag={})
    sessions = trading_sessions(args.start, args.end)
    rebals = rebalance_sessions(sessions, args.rebalance_every, args.max_rebalances)
    _log(f"sessions={len(sessions)} rebalances={len(rebals)} arms={arms}")
    cache_path = Path(args.basket_cache)
    if not cache_path.is_absolute():
        cache_path = ROOT / cache_path
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # Precompute only when asked or for tiny smoke; do NOT auto-precompute 2018+ full schedules here.
    if args.precompute_baskets or args.smoke:
        from quantlab.beta.smallcap_sleeve import precompute_history_baskets
        _log(f"precompute_history_baskets n={len(rebals)} -> {cache_path}")
        precompute_history_baskets(rebals, cache_path)
        summary["diag"]["basket_cache_precomputed"] = True
    else:
        summary["diag"]["basket_cache_precomputed"] = False
    summary["diag"]["basket_cache"] = str(cache_path)
    summary["diag"]["smallcap_history_2015_limits"] = dict(
        data_source="history_2015",
        adv="turnover_rate×circ_mv proxy",
        closes="unadjusted",
        limit_flags="none before 2023",
        stress_test="2023+ panels path only",
        note="Beta history_2015 limits; stress_test still 2023+ only",
    )
    sig_path = out / "signals.parquet"
    if args.reuse_signals and sig_path.exists():
        sig = pd.read_parquet(sig_path)
    else:
        sig = build_signals(rebals, pool_limit=args.pool_limit, residual_n=args.residual_n,
                            cash_target=args.cash_target, out=out, basket_cache=cache_path)
    meta = pd.read_csv(out / "signals_meta.csv")
    summary["signals_meta_mean"] = meta.groupby("variant")[["etf_w", "smallcap_w", "residual_w", "cash_w"]].mean().round(4).to_dict("index")
    summary["diag"]["max_etf_soft_breaches"] = int(meta.max_etf_soft_breach.sum())
    ids = set(sig[sig.variant != "POOL"].instrument_id) | {ETF}
    if "C6" in arms:
        ids |= set(sig[sig.variant == "POOL"].instrument_id)
    _log(f"loading exec panels for {len(ids)} ids")
    warm = trading_sessions(pd.Timestamp(args.start) - pd.Timedelta(days=60), args.start)
    warm_start = str(warm[0].date()) if len(warm) else args.start
    summary["diag"]["panel_warmup_start"] = warm_start  # ADV/sigma for impact need ~20 sessions of history
    p = load_panels(ids, warm_start, args.end, delist_mark=args.delist_mark, diag_out=summary["diag"])
    _log("panels loaded")

    from quantlab.platform.execution import ExecConfig, ZERO_COST, reconcile_zero_cost, run_weight_schedule
    cfg = ExecConfig.strategy_v1(impact_k=args.impact_k, no_limit_codes=frozenset({ETF}))
    cash0 = args.capital

    def engine_arm(name, sched, config=cfg, capital=cash0):
        t0 = time.time()
        r = run_weight_schedule(p, sched, initial_cash=capital, config=config, record_weights=True)
        d = out / name
        d.mkdir(exist_ok=True)
        r["nav"][r["nav"].index >= pd.Timestamp(args.start)].rename("nav").to_csv(d / "nav.csv")
        for key in ("target_weights", "actual_weights"):
            w = r[key]
            w = w[w.index >= pd.Timestamp(args.start)]
            w = w.loc[:, (w != 0).any(axis=0)]
            long = w.stack()
            long = long[long != 0].rename("weight").reset_index()
            long.columns = ["session", "instrument_id", "weight"]
            long.to_parquet(d / f"{key}.parquet")
        sched_json = {str(k.date()): v for k, v in sched.items()}
        (d / "schedule.json").write_text(json.dumps(sched_json))
        r["nav"] = r["nav"][r["nav"].index >= pd.Timestamp(args.start)]
        res = dict(stats=segmented(r["nav"]), costs={k: float(v) for k, v in r["costs"].items()}, total_cost=float(r["total_cost"]),
                   fill_ratio=float(r["fill_ratio"]) if r["fill_ratio"] == r["fill_ratio"] else None,
                   carried_or_dropped_events=len(r["events"]), effective_n_mean=r["effective_n_mean"],
                   capital=capital, wall_s=round(time.time() - t0, 1))
        _log(f"arm {name} done {res['wall_s']}s total_ret={res['stats']['all'].get('total_return')}")
        nav = r["nav"]
        del r
        gc.collect()
        return res, nav

    navs = {}
    meanw = meta[meta.variant == "V2"][["etf_w", "smallcap_w", "residual_w"]].mean()
    for a in arms:
        if a in ("V2", "V2_T10", "V2_T20", "V2_EXCL30"):
            summary["arms"][a], navs[a] = engine_arm(a, schedule_from(sig, a))
        elif a == "V2_LIVE600K":
            summary["arms"][a], navs[a] = engine_arm(a, schedule_from(sig, a), capital=600_000.0)
        elif a == "C0":
            summary["arms"][a], navs[a] = engine_arm(a, {rebals[0]: {ETF: 1 - args.cash_target}})
        elif a == "C1":
            summary["arms"][a], navs[a] = engine_arm(a, schedule_from(sig, "C1"))
        elif a == "C2":
            sched = schedule_from(sig, "V2", ["etf", "smallcap"], scale={})
            sched = {ts: {c: (meanw.etf_w if c == ETF else x / max(1e-12, sum(v for k_, v in w.items() if k_ != ETF)) * meanw.smallcap_w)
                          for c, x in w.items()} for ts, w in sched.items()}
            summary["arms"][a], navs[a] = engine_arm(a, sched)
        elif a in ("C3", "C5", "C7", "C4", "C6"):
            comp = component_returns(p, sig, "V2", ["etf", "smallcap", "residual"])
            if a == "C3":
                v2r = (comp.fillna(0) @ meanw.reindex(["etf_w", "smallcap_w", "residual_w"]).set_axis(["etf", "smallcap", "residual"]).reindex(comp.columns).fillna(0))
                k = float(min(1 - args.cash_target, v2r.std() / max(1e-12, comp["smallcap"].std())))
                sched = schedule_from(sig, "V2", ["smallcap"])
                sched = {ts: {c: x / sum(w.values()) * k for c, x in w.items()} for ts, w in sched.items()}
                summary["arms"][a], navs[a] = engine_arm(a, sched)
                summary["arms"][a]["smallcap_weight"] = k
            elif a == "C5":
                vol = comp.rolling(60, min_periods=20).std()
                tgt = vol.rolling(250, min_periods=20).median()
                scl = (tgt / vol).clip(upper=1.0).fillna(1.0)
                scale = {}
                for ts in rebals:
                    for cname in ("etf", "smallcap"):
                        prev = scl.loc[:ts, cname]
                        scale[(ts, cname)] = float(prev.iloc[-1]) if len(prev) else 1.0
                base = schedule_from(sig, "V2", ["etf", "smallcap"])
                sched = {}
                for ts, w in base.items():
                    scs = sum(x for c, x in w.items() if c != ETF)
                    sched[ts] = {c: (meanw.etf_w * scale[(ts, "etf")] if c == ETF else x / max(scs, 1e-12) * meanw.smallcap_w * scale[(ts, "smallcap")])
                                 for c, x in w.items()}
                summary["arms"][a], navs[a] = engine_arm(a, sched)
            elif a == "C7":
                inv = float(meanw.sum())
                base = schedule_from(sig, "V2")
                sched = {ts: {c: x / sum(w.values()) * inv for c, x in w.items()} for ts, w in base.items()}
                res, navs[a] = engine_arm("C7_const_exposure", sched)
                rng = np.random.default_rng(0)
                m = meta[meta.variant == "V2"].set_index("session")[["etf_w", "smallcap_w", "residual_w"]]
                shifts = []
                cr = comp.fillna(0)
                for _ in range(args.c7_shifts):
                    sh = int(rng.integers(1, max(2, len(m))))
                    mw = pd.DataFrame(np.roll(m.to_numpy(), sh, axis=0), index=pd.to_datetime(m.index), columns=["etf", "smallcap", "residual"])
                    wd = mw.reindex(cr.index).ffill().fillna(0)[cr.columns]
                    shifts.append(float((1 + (wd * cr).sum(axis=1)).prod() - 1))
                res["circular_shift_placebo"] = dict(n=len(shifts), total_return_quantiles=np.quantile(shifts, [0.05, 0.5, 0.95]).tolist() if shifts else None,
                                                     method="component-return approximation, frictionless")
                summary["arms"][a] = res
            elif a == "C4":
                best, grid = None, np.arange(0, 1.0001, 0.05)
                cr = comp.fillna(0)
                for we in grid:
                    for ws in grid:
                        if we + ws > 1 - args.cash_target + 1e-9:
                            continue
                        wr = 1 - args.cash_target - we - ws
                        nav = (1 + cr.get("etf", 0) * we + cr.get("smallcap", 0) * ws + cr.get("residual", 0) * wr).cumprod()
                        s_ = stats(nav).get("sharpe") or -9
                        if best is None or s_ > best[0]:
                            best = (s_, we, ws, wr, stats(nav))
                summary["arms"][a] = dict(report_only=True, not_a_verdict=True, criterion="max Sharpe, frictionless, ex-post",
                                          best=dict(etf=best[1], smallcap=best[2], residual=best[3], stats=best[4]) if best else None)
            elif a == "C6":
                pool = sig[sig.variant == "POOL"]
                n_sc = int(meta[meta.variant == "V2"].n_smallcap.median())
                rng = np.random.default_rng(0)
                tots = []
                for _ in range(args.c6_draws):
                    sched = {}
                    for ts, g in pool.groupby("session"):
                        names = list(g.sort_values("weight").instrument_id)
                        pick = rng.choice(names, size=min(n_sc, len(names)), replace=False)
                        sched[pd.Timestamp(ts)] = {c: 1.0 / len(pick) for c in pick}
                    nav = _fast_nav(p, sched)
                    tots.append(float(nav.iloc[-1] / nav.iloc[0] - 1))
                actual = comp["smallcap"].fillna(0)
                act = float((1 + actual).prod() - 1)
                summary["arms"][a] = dict(method="random same-band baskets (top-200 ranked pool), same N, frictionless component approximation",
                                          draws=len(tots), sleeve_total_return=act,
                                          random_quantiles=np.quantile(tots, [0.05, 0.5, 0.95]).tolist() if tots else None,
                                          pct_random_beating_sleeve=float(np.mean(np.array(tots) > act)) if tots else None)
            del comp
            gc.collect()
        elif a == "C8":
            sched = schedule_from(sig, "V2")
            zres, _ = engine_arm("C8_zero_cost", sched, config=replace(cfg, **ZERO_COST))
            full = summary["arms"].get("V2") or engine_arm("C8_full_cost", sched)[0]
            rec = reconcile_zero_cost(p, sched, initial_cash=cash0)
            rec["navs"].to_csv(out / "C8_reconcile_navs.csv")
            summary["arms"][a] = dict(zero_cost=zres["stats"]["all"], full_cost=full["stats"]["all"], full_total_cost=full["total_cost"],
                                      reconcile=dict(reference=rec["reference"], diffs=rec["diffs"]))
        (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str, ensure_ascii=False))
    summary["wall_s"] = round(time.time() - t_start, 1)
    summary["peak_rss_mb"] = round(_rss_mb(), 0)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str, ensure_ascii=False))
    _log(f"done wall={summary['wall_s']}s -> {out}/summary.json")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arms", default=",".join(ALL_ARMS))
    ap.add_argument("--start", default="2024-06-03",
                    help="window start; use 2018-01-02 for the prereg dev/validation window")
    ap.add_argument("--end", default="2026-10-09",
                    help="window end; use 2024-05-31 with --start 2018-01-02 for pure dev/validation")
    ap.add_argument("--rebalance-every", type=int, default=10)
    ap.add_argument("--max-rebalances", type=int, default=None)
    ap.add_argument("--pool-limit", type=int, default=None, help="cap residual universe (smoke)")
    ap.add_argument("--residual-n", type=int, default=50)
    ap.add_argument("--cash-target", type=float, default=0.05)
    ap.add_argument("--capital", type=float, default=5_000_000.0, help="research notional (Beta research profile)")
    ap.add_argument("--impact-k", type=float, default=1.0)
    ap.add_argument("--delist-mark", type=float, default=0.5, help="terminal delist loss; 0.5 = -50%% primary, 1.0 = -100%% sensitivity")
    ap.add_argument("--c6-draws", type=int, default=1000)
    ap.add_argument("--c7-shifts", type=int, default=200)
    ap.add_argument("--basket-cache", default="output/strategy_s2/basket_cache/history_baskets.json",
                    help="JSON path for precompute_history_baskets / SmallcapBetaSleeveProvider basket_cache")
    ap.add_argument("--precompute-baskets", action="store_true",
                    help="precompute history_2015 baskets for this run's rebalance sessions (smoke always does)")
    ap.add_argument("--memory-safe", action="store_true", help="phase-split, frees Beta panels before execution, one arm at a time")
    ap.add_argument("--reuse-signals", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default="output/strategy_s2/v2_book")
    args = ap.parse_args(argv)
    if args.smoke:
        args.max_rebalances = min(args.max_rebalances or 3, 3)
        args.pool_limit = min(args.pool_limit or 250, 250)
        args.c6_draws = min(args.c6_draws, 5)
        args.c7_shifts = min(args.c7_shifts, 5)
    run(args)


if __name__ == "__main__":
    main()
