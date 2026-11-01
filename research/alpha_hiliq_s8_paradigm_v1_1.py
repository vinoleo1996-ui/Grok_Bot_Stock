"""§8 paradigm material for HI_LIQ legs/leaves (Alpha) — VERSION v1.1.
Derived from research/alpha_hiliq_s8_paradigm.py (af48bc05fbcfb55e72336806c03455dbf4f0b52079c833aed9f141bece00966c, FROZEN:
kept unchanged for the v4/v4.1 reproduction chain; do not edit it). Ruling: 主 Agent 2026-10-18 02:44 ET — leaf23/24 §8 and CMC use
v1.1; new files only; THRESHOLDS UNCHANGED; old-tool results only as a disclosure comparison column; leaf25+ default v1.1.
POST-HOC (Arch bd3abe5c P3-B; Alpha docs/v2/ALPHA_S8_LAG_SELFCHECK_ZH.md 238b2978): applies to later leaves only; v4/v4.1 verdicts stand.
Rules frozen first: docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md (+ v1.1 anchor clarification appended 2026-10-18).

v1.1 changes vs af48bc05 (nothing else):
  1. Signal-side exposures (resid_multi: A, A', stacked IC/CMC, C rho) are strictly t−1 relative to the SIGNAL date d:
       mc   = log float mcap at close d−1          (MC_sig = MC_wide.shift(1)); FMC read from START exactly like af48bc05 (L61), so
              the START day has no d−1 value → mc NaN → START day dropped from signal residualisation (Arch r2 P1-1 option b)
       beta = 120-session beta on returns d−120..d−1 (beta.shift(1))
       mom  = C(d−21)/C(d−121) − 1 = returns d−120..d−21 (C.shift(21)/C.shift(121) − 1)
       liq  = log ADV20 = mask adv20_yuan[d] = mean amount of the 20 sessions strictly before d (already t−1; unchanged —
              writer research/strategy_hiliq_universe_v1.py L130–141: prior = sess[sess < S][-ADV_WIN:]; adv = mean)
       SW L1 = members effective ON the snapshot date (in_date ≤ snap < out_date), snapshot = last month-end session ≤ d (a month-end
              day uses its same-day members; SW changes are pre-announced); pool = mask in_universe[d] (ADV / previous bar from
              sessions < d; ST / suspension = day-d status, known pre-open).
  2. B (resid_ret: neutralised return on return day r) keeps the ORIGINAL exposure set X at r−1 (xmat(c, d0=r−1)) — unchanged.
  3. Forward return F truncated at END: F[d] = C[d+20]/C[d] − 1 only if d+20 ≤ END (else NaN); checked (last H rows all NaN).
  4. vol20 is NOT used (not part of the frozen style set).
  5. SW L1 first-month fix (Arch 31b4b8ba P2-3; 主 Agent 2026-10-18 ruling = FIX), applies to BOTH X_sig and the B set X: af48bc05
     took snapshots only from window month-ends, so 2024-06-03..2024-06-27 had NO industry (all '_UNK'). v1.1 adds exactly ONE
     pre-window snapshot 2024-05-31 (combo_v1_1.sw_snapshot_dates asserts it is the only date < START; SW member table only, no
     prices / returns for it); check_ind_coverage refuses any window day whose pool is entirely unclassified.
     Pre-window market data (主 Agent 02:59 / 03:10; Arch 6ab489c8 P1-1): the ONLY pre-window market data read is the inherited price
     look-back for beta / mom — same read range (PRICE_START = "2023-06-01" .. "2026-11-30", byte-identical to af48bc05 L36, asserted),
     same window lengths (beta 120 min 60; mom span 100), same source (ADG.bench / ADG._close), same formulas; after the 02:44 t−1 shift
     the earliest price touched is one session earlier (d−121), still inside the same read range. Float mcap is read from START (asserted).
     Diff vs af48bc05 (disclosed): the START day 2024-06-03 has no mc_{t−1} and is dropped from A / A′ / C (signal side); B (X at r−1)
     is unaffected.
  6. Run gate (as __main__): ok_runner_pin.enforce (c7805d9a, itself a pinned dep) mode 'full' → research/alpha_v1_1_runguard (pinned)
     ok_selfcheck (expires_et tz-aware & not expired, scope=full, no BOM, LF, every known allow_* explicit, only allow_full true; .ok
     out_dir if present must equal --out-dir) → out_dir must be empty → RSS watchdog (0.5 s poll, 1,536,000 KB) + RLIMIT_AS backstop →
     heavy imports. Import closure (docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest, pinned) verified after build and before writing; .ok
     re-checked before writing. Outputs exclusive-create.
  7. Leaves to evaluate are passed with --leaf NAME=PATH (repeatable; each pinned as dep_sha256_leaf_<NAME>); without --leaf the five
     frozen HI_LIQ event legs are evaluated (comparison only).
Universe HI_LIQ_V1.1 mask; window X2 2024-06-03..2026-10-09; h=20; styles: SW L1 + log float mcap + beta120 + mom(t-120..t-20) + log ADV20.
Research-grade; live=false; promotion=false; no GP; no Eng.
"""
from __future__ import annotations
import sys, json, time, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
TOOL_VERSION = "v1.1"
OUT_DEFAULT = ROOT / "output/alpha/hiliq_s8_v1_1"
MASK = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
LEGD = ROOT / "output/strategy_hiliq/legs"
CAP = LEGD / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
FMC = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
LEGS = {"equity_incentive": "202436", "earnings_event": "202822", "insider_increase": "202928",
        "insurer_surv": "203108", "report_rc_allup": "203201"}
TYPE_CAP = {"report_rc_allup": "report", "insurer_surv": "survey"}
START, END, H, BAL = "2024-06-03", "2026-10-09", 20, "510300.SH"
TIERS = {"60w": 6, "100w": 10}
PRICE_START, PRICE_END = "2023-06-01", "2026-11-30"   # inherited from af48bc05 L36; asserted unchanged
MANIFEST = ROOT / "docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest"   # sha256sum format; full static import closure (incl. quantlab/*)
CODE_DEPS = {"adg": ROOT / "research/alpha_decay_gate.py", "combo_v1_1": ROOT / "research/alpha_combo_marginal_v1_1.py",
             "adj_price": ROOT / "research/adj_price.py", "panel_stitch": ROOT / "research/g1g5_x2_panel_stitch.py",
             "nontextbook": ROOT / "research/g1g5_nontextbook_weights.py", "hiliq_universe": ROOT / "research/hiliq_v1_universe.py",
             "metrics": ROOT / "quantlab/metrics.py",
             "selfcheck_v3": ROOT / "research/leaf_selfcheck_v3.py", "selfcheck_common": ROOT / "research/leaf_selfcheck_common.py",
             "ai_debate_memory_runner": ROOT / "research/ai_debate_memory_runner.py", "g1g5_wiring": ROOT / "research/g1g5_wiring.py",
             "g1g5_expand_g6": ROOT / "research/g1g5_expand_g6.py", "ok_runner_pin": ROOT / "scripts_eng/ok_runner_pin.py",
             "runguard": ROOT / "research/alpha_v1_1_runguard.py", "closure_manifest": MANIFEST}
log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)


def _cli():
    ap = argparse.ArgumentParser(description="Alpha §8 paradigm v1.1 (HI_LIQ). Requires an Arch .ok.")
    ap.add_argument("--arch-ok", required=True, help="Arch run-auth .ok pinning runner_sha256_alpha_hiliq_s8_paradigm_v1_1 + deps")
    ap.add_argument("--leaf", action="append", default=[], help="NAME=PATH of a daily target-weight parquet (repeatable)")
    ap.add_argument("--out-dir", default=str(OUT_DEFAULT))
    return ap.parse_args()


def _leaves(a) -> dict:
    out = {}
    for s in a.leaf:
        if "=" not in s: raise SystemExit(f"--leaf must be NAME=PATH, got {s!r}")
        k, p = s.split("=", 1); k = k.strip()
        if not k.replace("_", "").isalnum() or k in out: raise SystemExit(f"bad/duplicate leaf name {k!r}")
        out[k] = (ROOT / p) if not Path(p).is_absolute() else Path(p)
    return out


def _deps(leaves: dict) -> dict:
    d = {"mask": MASK, "float_mktcap": FMC, "capacity_adv_leg": CAP, **CODE_DEPS}
    if leaves:
        d.update({f"leaf_{k}": p for k, p in leaves.items()})
    else:
        d.update({f"leg_{k}": LEGD / f"g1g5_{k}_hiliq_v1_daily_weights_20261014_{st}.parquet" for k, st in LEGS.items()})
    return d


_GATE = _OKREC = _WD = None
if __name__ == "__main__":   # gate BEFORE heavy imports (Arch selftest spec 1aa43bdd §4 pattern; runner gate c7805d9a)
    _A = _cli(); _LV = _leaves(_A)
    sys.path.insert(0, str(ROOT / "scripts_eng"))
    from ok_runner_pin import enforce
    _GATE = enforce(__file__, [_A.arch_ok], modes=["full"], deps=_deps(_LV))
    import research.alpha_v1_1_runguard as RG   # pinned above (dep_sha256_runguard); stdlib only
    _OUTD = RG.precheck_out_dir(_A.out_dir)
    _OKREC = RG.ok_selfcheck([_A.arch_ok], _GATE, "full", out_target=_OUTD)
    _MAN0 = RG.verify_manifest_shas(MANIFEST, "startup")
    _WD = RG.start_watchdog(rlimit_as_kb=RG.rlimit_as_kb())

import numpy as np, pandas as pd   # noqa: E402  (after the gate)
import research.alpha_decay_gate as ADG   # noqa: E402
from research.alpha_combo_marginal_v1_1 import ic_tstats, nw_se, sw_snapshot_dates, check_ind_coverage, check_f_truncated, check_fmc_lower_bound   # noqa: E402  (v1.1; no old-tool import)
COST = ADG.COST
OUT = OUT_DEFAULT


def _rss_kb() -> int:
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def panel():
    cp = OUT / "_panel_close.parquet"
    mk = pd.read_parquet(MASK, columns=["date", "instrument", "in_universe", "adv20_yuan"],
                         filters=[("date", ">=", pd.Timestamp(START)), ("date", "<=", pd.Timestamp(END))])
    mk["instrument"] = mk.instrument.astype(str); mk["date"] = pd.to_datetime(mk.date)
    INU = mk.pivot_table(index="date", columns="instrument", values="in_universe", aggfunc="max").fillna(False).astype(bool)
    U = sorted(INU.columns[INU.any()])
    ADV = mk.pivot_table(index="date", columns="instrument", values="adv20_yuan").reindex(columns=U)
    INU = INU.reindex(columns=U)
    if cp.exists():
        C = pd.read_parquet(cp)
    else:
        if (PRICE_START, PRICE_END) != ("2023-06-01", "2026-11-30"): raise RuntimeError("price read range must stay identical to af48bc05")
        b = ADG.bench(); days = b.index[(b.index >= PRICE_START) & (b.index <= PRICE_END)]
        cols = {}
        for k, i in enumerate(U):
            try: cols[i] = ADG._close(i).reindex(days)
            except Exception: pass
            if k % 200 == 0: log("close", k, len(U))
        C = pd.DataFrame(cols); C["__b"] = b.reindex(days)
        with open(cp, "xb") as f: C.to_parquet(f)
    rb = C.pop("__b").pct_change()
    C = C.reindex(columns=U)
    return U, INU, ADV, C, rb


def build():
    U, INU, ADV, C, rb = panel()
    R = C.pct_change(fill_method=None)
    ev = INU.index[(INU.index >= START) & (INU.index <= END)]
    beta = R.rolling(120, min_periods=60).cov(rb).div(rb.rolling(120, min_periods=60).var(), axis=0)   # info: returns d−119..d
    mom = C.shift(20) / C.shift(120) - 1                                                                  # info: returns d−119..d−20
    beta_sig = beta.shift(1)                                                                              # v1.1: returns d−120..d−1
    mom_sig = C.shift(21) / C.shift(121) - 1                                                              # v1.1: returns d−120..d−21
    Ce = C.loc[:END]                                                                                       # v1.1: F truncated at END
    F = Ce.shift(-H) / Ce - 1                                                                              # NaN when d+H > END
    from research.g1g5_x2_panel_stitch import to_panel_id
    from research.g1g5_nontextbook_weights import _load_sw_members
    from research.hiliq_v1_universe import industry_on_date
    pids = {to_panel_id(i): i for i in U}
    fm = pd.read_parquet(FMC, columns=["instrument_id", "trade_date", "float_mktcap"],
                         filters=[("trade_date", ">=", pd.Timestamp(START)), ("instrument_id", "in", list(pids))])   # == af48bc05 L61
    fmc_min = check_fmc_lower_bound(fm["trade_date"])
    fm["i"] = fm.instrument_id.map(pids)
    FMp = fm.pivot_table(index="trade_date", columns="i", values="float_mktcap"); del fm
    MC = np.log(FMp.reindex(ev).ffill()).reindex(columns=U)                                               # B set: unchanged (close d)
    cal = C.index[(C.index >= pd.Timestamp(START)) & (C.index <= pd.Timestamp(END))]
    MC_sig = np.log(FMp.reindex(cal).ffill()).shift(1).reindex(ev).reindex(columns=U)                    # v1.1: close d−1; START NaN
    if MC_sig.loc[pd.Timestamp(START)].notna().any(): raise RuntimeError("START-day mc_{t−1} must be NaN (no pre-window float mcap)")
    del FMp
    check_f_truncated(Ce, F, ev)
    sw = _load_sw_members()
    me = sw_snapshot_dates(C.index[C.index <= pd.Timestamp(END)], ev)                                    # v1.1: + 2024-05-31 (SW table only)
    IND = pd.DataFrame([industry_on_date(U, d, sw) for d in me], index=me).reindex(columns=U).reindex(ev, method="ffill")
    INUe = INU.reindex(ev).fillna(False).astype(bool)
    indcov = check_ind_coverage(IND, {d: list(INUe.columns[INUe.loc[d].values]) for d in ev})
    liq = np.log(ADV.reindex(ev).clip(lower=1))                                                           # mask adv20[d] = d−20..d−1
    X = dict(mc=MC, beta=beta.reindex(ev), mom=mom.reindex(ev), liq=liq)                                 # B (resid_ret at r−1): unchanged
    X_sig = dict(mc=MC_sig, beta=beta_sig.reindex(ev), mom=mom_sig.reindex(ev), liq=liq)                 # signal residualisation: t−1
    return dict(U=U, ev=ev, INU=INU.reindex(ev), R=R, F=F.reindex(ev), X=X, X_sig=X_sig, IND=IND, ind_coverage=indcov,
                sw_snapshots=[str(pd.Timestamp(x).date()) for x in me],
                reads=dict(price_start=str(C.index.min().date()), fmc_earliest_trade_date=fmc_min, start_day_skipped_signal_side=START))


_XC = {}


def xmat(c, d, key="X"):
    """Cached (pool, Xm) for day d: intercept + styles (exposure set c[key]: 'X' = B set, 'X_sig' = signal set) + SW L1 dummies."""
    ck = (d, key)
    if ck not in _XC:
        pool = c["INU"].columns[c["INU"].loc[d].values]
        Xd = pd.DataFrame({k: v.loc[d, pool] for k, v in c[key].items()})
        Xd = Xd.join(pd.get_dummies(c["IND"].loc[d, pool].fillna("_UNK"), dtype=float))
        ok = Xd.notna().all(axis=1)
        Xd = Xd[ok]
        _XC[ck] = (Xd.index, np.c_[np.ones(len(Xd)), Xd.values.astype(float)])
    return _XC[ck]


def resid_multi(c, Ss: dict, extra: pd.DataFrame | None = None) -> dict:
    """Residualize several signals at once on the SIGNAL exposure set (t−1, v1.1); z-score per day."""
    out = {k: pd.DataFrame(np.nan, index=c["ev"], columns=c["U"]) for k in Ss}
    for d in c["ev"]:
        pool, Xm = xmat(c, d, "X_sig")
        if len(pool) < 50: continue
        if extra is not None: Xm = np.c_[Xm, extra.loc[d, pool].values]
        Y = np.column_stack([Ss[k].loc[d, pool].values for k in Ss])
        cf, *_ = np.linalg.lstsq(Xm, Y, rcond=None); E = Y - Xm @ cf
        for j, k in enumerate(Ss):
            e = E[:, j]
            if Y[:, j].std() > 0 and e.std() > 0: out[k].loc[d, pool] = (e - e.mean()) / e.std()
    return out


def resid_ret(c):
    """Daily cross-sectional residual returns vs industry+style exposures at t-1 (= return day r−1; ORIGINAL set X, unchanged)."""
    E = pd.DataFrame(np.nan, index=c["ev"], columns=c["U"]); evs = list(c["ev"])
    for k in range(1, len(evs)):
        d0, d = evs[k - 1], evs[k]
        pool, Xm = xmat(c, d0, "X")
        y = c["R"].loc[d, pool].values; ok = ~np.isnan(y)
        if ok.sum() < 50: continue
        cf, *_ = np.linalg.lstsq(Xm[ok], y[ok], rcond=None)
        E.loc[d, pool[ok]] = y[ok] - Xm[ok] @ cf
    return E


def sig(c, path):
    d = pd.read_parquet(path, columns=["date", "instrument", "target_weight"]); d["date"] = pd.to_datetime(d.date.astype(str).str[:10])
    d = d[d.instrument != BAL]
    return d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").reindex(index=c["ev"], columns=c["U"]).fillna(0.0)


def ic_series(c, Z):
    s = {}
    for d in Z.index:
        z, f = Z.loc[d], c["F"].loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= 50 and z[ok].std() > 0: s[d] = z[ok].rank().corr(f[ok].rank())
    return pd.Series(s).dropna()


def icpack(s):
    roll = (s.rolling(252).mean() / s.rolling(252).std()).dropna()
    return dict(rank_ic=float(s.mean()), icir_full=float(s.mean() / s.std()),
                icir_roll252_median=float(roll.median()) if len(roll) else None, n=int(len(s)), **ic_tstats(s, H))


def topn(S, N):
    W = S.copy()
    rk = W.rank(axis=1, ascending=False, method="first")
    W = W.where((rk <= N) & (W > 0), 0.0)
    return W.div(W.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)


def neut_net(E, W):
    Wl = W.shift(2).fillna(0.0)  # T signal → T+1 open fill ≈ earns from T+2 close-to-close (conservative)
    g = (Wl * E.reindex_like(Wl).fillna(0.0)).sum(axis=1)
    to = W.diff().abs().sum(axis=1).fillna(W.abs().sum(axis=1)).shift(1).fillna(0.0)
    n = (g - COST * to).iloc[3:]; act = Wl.sum(axis=1).iloc[3:] > 0
    se = nw_se(n.values, 5)
    return dict(ann_net_excess=float(n.mean() * 244), ann_gross_excess=float(g.iloc[3:].mean() * 244),
                ann_cost=float(COST * to.iloc[3:].mean() * 244), to_daily_two_sided=float(to.mean()),
                t_hac5=float(n.mean() / se) if se > 0 else None, active_day_frac=float(act.mean()), series=n)


def run(leaves: dict, gate: dict | None, hooks: dict | None = None):
    """hooks (from __main__): after_build() / before_write() → receipts (closure manifest check, .ok re-check); recorded in meta."""
    hooks = hooks or {}; rcpt = {}
    t0 = time.time(); c = build(); log("ctx", round(time.time() - t0))
    if "after_build" in hooks: rcpt["after_build"] = hooks["after_build"]()
    E = resid_ret(c); log("resid_ret")
    Scap = sig(c, CAP)
    paths = leaves if leaves else {leg: LEGD / f"g1g5_{leg}_hiliq_v1_daily_weights_20261014_{st}.parquet" for leg, st in LEGS.items()}
    SL = {k: sig(c, p) for k, p in paths.items()}
    ZA = resid_multi(c, {"cap": Scap, **SL}); log("resid A")
    ZI = resid_multi(c, SL, extra=Scap); log("resid A_prime")
    Zcap = ZA["cap"]; ICcap = ic_series(c, Zcap)
    cap_to = float(Scap.diff().abs().sum(axis=1).mean())
    cb = neut_net(E, topn(Scap, 25)); capB = {t: cb for t in TIERS}  # capacity_adv own sleeve (≤25 names) as fast/slow reference
    res = dict(cap=dict(ic=icpack(ICcap), to_daily=cap_to, neut_net=capB["60w"] | {"series": None}))
    for leg, p in paths.items():
        log("leg", leg)
        S = SL[leg]; Za = ZA[leg]; A = icpack(ic_series(c, Za))
        Zi = ZI[leg]; Ap = icpack(ic_series(c, Zi))
        combo = (0.8 * Zcap + 0.2 * Zi.fillna(0)).where(Zcap.notna()); ICc = ic_series(c, combo)
        ix = ICc.index.intersection(ICcap.index); dIC = ICc[ix] - ICcap[ix]
        ccomb = icpack(ICc); ccap = icpack(ICcap[ix])
        d_icir_roll = (ccomb["icir_roll252_median"] - ccap["icir_roll252_median"]) if ccomb["icir_roll252_median"] is not None and ccap["icir_roll252_median"] is not None else None
        ws_ic = 0.8 * ccap["rank_ic"] + 0.2 * Ap["rank_ic"]
        B = {}
        for t, N in TIERS.items():
            r = neut_net(E, topn(S, N)); B[t] = {k: v for k, v in r.items() if k != "series"}
            if t == "60w": rl = r["series"]
        rc = capB["60w"]["series"]; jx = rl.index.intersection(rc.index); y, x = rl[jx].values, rc[jx].values
        Xm = np.c_[np.ones(len(x)), x]; cf, *_ = np.linalg.lstsq(Xm, y, rcond=None); e = y - Xm @ cf
        se_a = nw_se(e, 5)
        rho = float(np.nanmean([Za.loc[d].corr(Zcap.loc[d]) for d in c["ev"]]))
        to_leg = float(S.diff().abs().sum(axis=1).mean())
        hp_ratio = (cap_to / to_leg) if to_leg > 0 else None  # leaf holding period / cap holding period
        same_band = hp_ratio is not None and 0.5 <= hp_ratio <= 2
        ortho_alpha = float(cf[0] * 244)
        Cc = dict(rho_resid_vs_cap=rho, to_daily_leaf=to_leg, to_daily_cap=cap_to, holding_period_ratio_leaf_over_cap=hp_ratio,
                  same_frequency_band=bool(same_band), stacked_ic=ccomb["rank_ic"], cap_ic_same_days=ccap["rank_ic"],
                  weighted_sum_ic=float(ws_ic), stacked_minus_weighted_sum=float(ccomb["rank_ic"] - ws_ic),
                  ortho_alpha_ann_vs_cap=ortho_alpha, ortho_alpha_t_hac5=float(cf[0] / se_a) if se_a > 0 else None,
                  beta_on_cap=float(cf[1]), corr_neut_ret_vs_cap=float(np.corrcoef(x, y)[0, 1]))
        cmc = dict(d_ic=float(dIC.mean()), d_icir_full=ccomb["icir_full"] - ccap["icir_full"], d_icir_roll252_median=d_icir_roll,
                   d_ic_tstats=ic_tstats(dIC, H))
        # thresholds UNCHANGED vs af48bc05
        vA = A["rank_ic"] > 0 and A["icir_full"] > 0 and (A["icir_roll252_median"] or -1) > 0
        vAp = Ap["rank_ic"] > 0 and cmc["d_ic"] >= 0.003 and cmc["d_icir_full"] >= 0.05 and (d_icir_roll is not None and d_icir_roll >= 0.05)
        vB = all(B[t]["ann_net_excess"] > 0 for t in TIERS)
        vC = rho <= 0.5 and not (rho > 0.3 and same_band and ortho_alpha <= 0)
        allp = vA and vAp and vB and vC
        status = "RESEARCH_ACCEPT" if allp else "WATCH"
        if leg in TYPE_CAP and allp: status = "WATCH"
        res[leg] = dict(file=str(Path(p).resolve().relative_to(ROOT)) if str(Path(p).resolve()).startswith(str(ROOT)) else str(p),
                        A=A, A_prime=Ap, cmc=cmc, B=B, C=Cc,
                        verdict=dict(A=vA, A_prime=vAp, B=vB, C=vC, all_pass=allp, type_cap=TYPE_CAP.get(leg), status=status))
        log(leg, res[leg]["verdict"])
    res["meta"] = dict(tool_version=TOOL_VERSION, ruling="主 Agent 2026-10-18 02:44 ET", thresholds="unchanged vs af48bc05",
                       post_hoc="applies to later leaves only (leaf23/24 onward); v4/v4.1 verdicts stand",
                       frozen_predecessor="research/alpha_hiliq_s8_paradigm.py af48bc05 (not imported)",
                       rules="docs/v2/ALPHA_HILIQ_S8_PARADIGM_RULES_20261014_ZH.md", universe="HI_LIQ_V1.1", window=[START, END], h=H,
                       exposure_anchor=dict(signal="t−1 vs signal date d (mc close d−1; beta ret d−120..d−1; mom ret d−120..d−21; liq amt d−20..d−1)",
                                            B="r−1 vs return day r (original set X, unchanged)", F="truncated at END",
                                            ind="SW L1 members effective on the last month-end session ≤ d (same-day members on that date); "
                                                "2024-06-03..06-27 use the 2024-05-31 snapshot (only pre-window snapshot)",
                                            pool="mask in_universe[d] (ADV/prev bar from sessions < d; ST/suspension = day-d status, known pre-open)"),
                       ind_coverage=c["ind_coverage"], sw_snapshot_dates_head=c["sw_snapshots"][:3], reads=c["reads"],
                       diff_vs_af48bc05=["signal mc/beta/mom at t−1", "SW L1 2024-06-03..06-27 from the 2024-05-31 snapshot (was all _UNK; X_sig and B)",
                                         "START day 2024-06-03 dropped from signal residualisation (no mc_{t−1}; float mcap read from START as before)"],
                       vol20_used=False, gate=gate, peak_rss_kb=_rss_kb(),
                       live=False, promotion_approved=False, gp=False, eng_dispatched=False,
                       caveat="B uses capacity_adv top-25 sleeve as fast/slow reference; T+1 approximated by 2-day lag on close-to-close residual returns; not Eng X2.")
    if "before_write" in hooks: rcpt["before_write"] = hooks["before_write"]()
    res["meta"]["run_guard"] = rcpt; res["meta"]["peak_rss_kb"] = _rss_kb()
    with open(OUT / "ALPHA_HILIQ_S8_v1_1.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(res, ensure_ascii=False, indent=2, default=lambda o: None))
    log("done", round(time.time() - t0), "peak_rss_kb", _rss_kb())


def _before_write():
    cl = RG.verify_closure(MANIFEST, "before write"); RG.recheck_expiry(_OKREC, "before write")
    return dict(closure=dict(startup=_MAN0, before_write=cl), ok_selfcheck=_OKREC, watchdog=_WD, env=RG.env_snapshot(), vm_peak_kb=RG.vm_peak_kb())


if __name__ == "__main__":
    OUT = _OUTD
    OUT.mkdir(parents=True, exist_ok=True)
    RG.precheck_out_dir(OUT)
    run(_LV, _GATE, hooks=dict(after_build=lambda: RG.verify_closure(MANIFEST, "after build"), before_write=_before_write))
