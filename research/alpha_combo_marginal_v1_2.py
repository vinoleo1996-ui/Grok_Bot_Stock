"""CMC per docs/v2/ALPHA_LEAF_ACCEPT_V2_PREREG_ZH.md §1 — VERSION v1.2 = MEMORY-ONLY refactor of research/alpha_combo_marginal_v1_1.py
(5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911; that file and docs/v2/ALPHA_V1_1_IMPORT_CLOSURE.manifest are NOT edited and
NOT imported). Trigger: 2026-10-18 09:04 ET the leaf24 CMC v1.1 full run was stopped by runguard rc=3 (peak RSS ≥ 1630960 kB > 1536000 kB,
~90 s in, inferred in ctx() building P / rolling beta). Spec: Arch→Alpha 2026-10-18 (memory only, numerics unchanged). THRESHOLDS, DEFINITIONS
AND OUTPUT NUMBERS ARE THOSE OF v1.1; only how intermediates are held in memory changes:
  M1. P built per instrument: ADG._close(i).reindex(days) into a float64 matrix (index unique and dtype float64 asserted per series), and
      ADG._cache.pop(i) right after use (AP._F, the adj-factor table, is kept). v1.1: pd.DataFrame({i: series}) on the ~3100-day union index.
  M2. sig(): parquet read with filters=[("target_weight", "!=", 0.0)]; pivot_table(sum) → reindex(index=ev, columns=U) → fillna(0.0) kept,
      so an absent row and a zero row give the same cell (+0.0). No instrument filter (reindex(columns=U) does that, as in v1.1).
  M3. mem: ev×U boolean matrix (ctx key mem_mask) + U_arr (object array of U); a day's pool = U_arr[mem_mask[k]].tolist() = the same list in
      the same U order as v1.1 [i for i in U if i in mem[d]]. Call sites: ctx (coverage), resid_z, pool_ew, check_ind_coverage.
  M4. del + gc.collect() between stages: ctx full-date P / R / beta / F (only the ev-window slices are kept, as v1.1 stored), mk; b0's Z.
      Independent steps inside ctx are reordered (F and check_f_truncated right after P, before R / beta) — same formulas, same inputs.
  M5. stderr line 'STAGE <name> ru_maxrss=<kB>' after: imports, mk/mem, _factors (after the first ADG._close, i.e. adj-factor load),
      P, beta, FMC, IND, every sig (sig:<label>), b0, tiers (per tier); extra key=value diagnostics may follow on the same line.
  Also (guard, not numerics): legacy_column refuses a v1.1 output as well as a v1.2 one. Closure manifest = docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest
  (v1.1 manifest + this file). Runner .ok key: runner_sha256_alpha_combo_marginal_v1_2. Runguard research/alpha_v1_1_runguard.py (35991407)
  reused unchanged. Receipts must disclose: tool sha v1_2 ≠ 5658f612 (numerics asserted bit-identical on synthetic data by
  tests/test_alpha_v1_2_equiv_selftest.py). Not done (per spec): float32, per-year chunking, panel_stitch changes, process split.
---- v1.1 definition notes (semantics unchanged in v1.2) ----
CMC (Alpha-owned thresholds; AI produces data, no verdict) — VERSION v1.1.
Derived from research/alpha_combo_marginal.py (bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c, FROZEN: not edited,
not imported). Ruling: 主 Agent 2026-10-18 02:44 ET — leaf23/24 §8 and CMC use v1.1; THRESHOLDS UNCHANGED; legacy-tool results only as a
disclosure comparison column (read from an existing legacy JSON output, --legacy-json); leaf25+ default v1.1. POST-HOC (Arch bd3abe5c P3-B;
Alpha docs/v2/ALPHA_S8_LAG_SELFCHECK_ZH.md): applies to later leaves only.
v1.1 changes vs bee23019 (nothing else in the CMC arithmetic):
  1. Signal residualisation exposures (resid_z) strictly t−1 vs the signal date d:
       mc   = log float mcap at close d−1   (was close d)          — ctx(): MC_sig = MC_cal.shift(1); FMC read from START exactly
              like bee23019 (L95), so the START day has no d−1 value → mc NaN → START day skipped in resid_z (Arch r2 P1-1 option b)
       beta = 120-session beta on returns d−120..d−1 (was ..d)      — ctx(): beta.shift(1)
     SW L1 = members effective ON the snapshot date (in_date ≤ snap < out_date), snapshot = last month-end session ≤ d (a month-end
     day d itself uses its same-day members; SW changes are pre-announced); pool = mask in_universe[d] (ADV / previous bar from
     sessions < d; ST / suspension = day-d status, known pre-open). CMC uses no mom / liq / vol20 regressors (unchanged).
  2. SW L1 first-month fix (Arch 31b4b8ba P2-3; 主 Agent 2026-10-18 ruling = FIX): bee23019 took snapshots only from window month-ends,
     so 2024-06-03..2024-06-27 had NO industry (all '_UNK'). v1.1 adds exactly ONE pre-window snapshot, SW_PRE_SNAPSHOT = 2024-05-31
     (= last session before START), used for the SW membership lookup only. sw_snapshot_dates() asserts that it is the only snapshot
     date < START; the lookup reads the SW member table only (no prices / returns / mcap for it). check_ind_coverage() refuses any window
     day whose pool is entirely unclassified.
     Pre-window market data (主 Agent 02:59 / 03:10; Arch 6ab489c8 P1-1): the ONLY pre-window market data read is the inherited price
     look-back for beta — same read range (PRICE_START = "2023-09-01", byte-identical to bee23019 L82, asserted), same window length (120,
     min 60), same source (ADG.bench / ADG._close), same formula; after the 02:44 t−1 shift the earliest price touched is one session
     earlier (d−121 instead of d−120), still inside the same read range. Float mcap is read from START (not earlier; asserted).
     Diff vs bee23019 (disclosed): the START day 2024-06-03 has no mc_{t−1} and is skipped (window shorter by 1 day).
  3. F (20d fwd adj return) truncated at END (P reindexed to days ≤ END → F[d] NaN when d+20 > END; same as bee23019). Checked by
     check_f_truncated(): P ends ≤ END and the last H rows of F are all NaN (bee23019-v1.1 draft had a tautological assert).
  4. Output adds tool_version, exposure_anchor, ind_coverage, peak_rss_kb, gate receipt, ok self-check receipt, closure receipt,
     env QL_X2_EXTEND_END; optional legacy comparison column (disclosure_only).
  5. Run gate (as __main__): scripts_eng/ok_runner_pin.enforce (c7805d9a, itself a pinned dep) mode 'full' → research/alpha_v1_1_runguard
     (pinned) ok_selfcheck (expires_et tz-aware and not expired, scope=full, no BOM, LF, every known allow_* explicit, only allow_full
     true) → --out pre-check → RSS watchdog + RLIMIT_AS backstop → heavy imports. Import closure (v1.2: docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest,
     pinned) verified after computing and before writing; .ok re-checked (unchanged, not expired) before writing. --out exclusive create.
B0 = B4 paper book for IC combo; tier nav baseline under hiliq = capacity_adv HI_LIQ book-smoke (主 Agent 2026-10-18 00:54 ET), b4 = diagnostic (capacity_adv/earnings_event/insider_increase 50/25/25, current paper weights);
B1 = 0.8*B0 + 0.2*leaf (leaf top-N 6/10, merged single name <=6%, overflow 510300).
Signals: leg/leaf weight per stock-day (event-holding signal); cross-sectional OLS residual vs SW L1 dummies, log float mcap_{t−1},
rolling-120d beta_{t−1} (and, for candidate, the three B0 leg signals); z-scored per day on the PIT pool
(universe mask in_universe that day: --universe hiliq [default, gate] = HI_LIQ_V1.1; fulla = FULLA_V1 [diagnostic]).
Significance disclosure (thresholds unchanged): ic_t_naive, ic_t_neff (n/h), ic_t_hac (Newey-West Bartlett, lag=h-1). Combo z: B0 = .5 z_cap + .25 z_ee + .25 z_ins; B1 = .8*B0 + .2*z_leaf.
Metrics: RankIC vs 20d fwd adj return (daily), ICIR full + rolling-252 median, net ΔCAGR/ΔMDD (17.5bp/unit TO) per tier,
yearly ΔCAGR, rho(leaf resid, B0 combo). Window = Eng X2 smoke 2024-06-03..2026-10-09. promotion=false; live=false."""
from __future__ import annotations
import sys, json, os, argparse, glob, hashlib, gc, resource
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
TOOL_VERSION = "v1.2"
V1_1_SHA = "5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911"   # numerics reference; disclosed: v1_2 sha != this
LEGACY_SHA = "bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c"
AF = ROOT / "output/ai_factory"
LEGS = {"capacity_adv": AF / "g1g5_capacity_adv_daily_weights_paper_20261013_r2.parquet",
        "earnings_event": AF / "g1g5_earnings_event_daily_weights_20261014_111825.parquet",
        "insider_increase": AF / "g1g5_insider_increase_daily_weights_20261014_111825.parquet"}
HL = ROOT / "output/strategy_hiliq/legs"
LEGS_BY_UNIVERSE = {"hiliq": {"capacity_adv": HL / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
                              "earnings_event": HL / "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
                              "insider_increase": HL / "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet"},
                    "fulla": LEGS}
CAPADV_BOOK_TRACKS = {"60w": ROOT / "output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK/target_weights.parquet",
                      "100w": ROOT / "output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK/target_weights.parquet"}
B4_TRACKS = {"hiliq": {"60w": ROOT / "output/strategy_hiliq/b4/B4_50_25_25_topN_60w.parquet",
                       "100w": ROOT / "output/strategy_hiliq/b4/B4_50_25_25_topN_100w.parquet"},
             "fulla": {"60w": ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013_r2.parquet",     # = leaf_selfcheck_v3.TRACKS["B4"]
                       "100w": ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013_r2.parquet"}}
UNIVERSE_MASKS = {"hiliq": ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet",
                  "fulla": ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"}
FMC = ROOT / "data/v2/float_mktcap/float_mktcap_daily_from2015_tushare.parquet"
PRICE_START = "2023-09-01"       # inherited from bee23019 L82 (`b.index >= "2023-09-01"`); asserted unchanged
SW_PRE_SNAPSHOT = "2024-05-31"   # the ONLY SW snapshot date < START (主 Agent 2026-10-18 P2-3 ruling)
MANIFEST = ROOT / "docs/v2/ALPHA_V1_2_IMPORT_CLOSURE.manifest"   # v1.2: v1.1 manifest + this file (sha256sum format)
CODE_DEPS = {"adg": ROOT / "research/alpha_decay_gate.py", "selfcheck_v3": ROOT / "research/leaf_selfcheck_v3.py",
             "selfcheck_common": ROOT / "research/leaf_selfcheck_common.py",
             "nontextbook": ROOT / "research/g1g5_nontextbook_weights.py", "panel_stitch": ROOT / "research/g1g5_x2_panel_stitch.py",
             "adj_price": ROOT / "research/adj_price.py", "metrics": ROOT / "quantlab/metrics.py",
             "ai_debate_memory_runner": ROOT / "research/ai_debate_memory_runner.py", "g1g5_wiring": ROOT / "research/g1g5_wiring.py",
             "g1g5_expand_g6": ROOT / "research/g1g5_expand_g6.py", "ok_runner_pin": ROOT / "scripts_eng/ok_runner_pin.py",
             "runguard": ROOT / "research/alpha_v1_1_runguard.py", "closure_manifest": MANIFEST}
BASE = os.environ.get("ALPHA_CMC_BASE", "capadv")  # capadv (gate default under hiliq) | b4 (diagnostic)
UNIVERSE = os.environ.get("ALPHA_CMC_UNIVERSE", "hiliq")  # hiliq = gate; fulla = diagnostic only


def _stage(name: str, **kv) -> int:
    """M5: one stderr line per stage, 'STAGE <name> ru_maxrss=<kB>' (Linux ru_maxrss = peak RSS so far, kB) + optional k=v diagnostics.
    Stdlib only; writes nothing to stdout (stdout carries the JSON)."""
    kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"STAGE {name} ru_maxrss={kb}" + "".join(f" {k}={v}" for k, v in kv.items()), file=sys.stderr, flush=True)
    return kb


def leaf_path(leaf: str) -> Path:
    """leaf name (ai_factory, same glob as leaf_selfcheck_v3.wfile) or explicit parquet path."""
    if str(leaf).endswith(".parquet"): return Path(leaf)
    fs = sorted(glob.glob(str(AF / f"g1g5_{leaf}_daily_weights_2*.parquet")))
    if not fs: raise SystemExit(f"no weights file for leaf {leaf!r}")
    return Path(fs[-1])


def gate_deps(leaf: str, universe: str, base: str) -> dict:
    d = {"mask": UNIVERSE_MASKS[universe], "float_mktcap": FMC, "leaf": leaf_path(leaf), **CODE_DEPS}
    d.update({f"leg_{k}": p for k, p in LEGS_BY_UNIVERSE[universe].items()})
    trk = CAPADV_BOOK_TRACKS if (universe == "hiliq" and base == "capadv") else B4_TRACKS[universe]
    d.update({f"base_{t}": p for t, p in trk.items()})
    return d


def _cli():
    ap = argparse.ArgumentParser(description="CMC v1.2 (Alpha; memory-only refactor of v1.1 5658f612). hiliq=gate (default), fulla=diagnostic. Requires an Arch .ok.")
    ap.add_argument("leaf"); ap.add_argument("--universe", choices=list(UNIVERSE_MASKS), default="hiliq")
    ap.add_argument("--base", choices=["capadv", "b4"], default="capadv", help="hiliq tier baseline: capadv book-smoke (gate, 主 Agent 10-18 00:54) | b4 (diag)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--arch-ok", required=True, help="Arch .ok pinning runner_sha256_alpha_combo_marginal_v1_2 + dep_sha256_<key>")
    ap.add_argument("--legacy-json", default=None, help="existing JSON written by the legacy tool bee23019 for the SAME leaf/universe/base; "
                                                        "read only (legacy tool is not imported or run); emitted as a disclosure-only comparison column")
    return ap.parse_args()


_GATE = _OKREC = _WD = None
if __name__ == "__main__":   # gate BEFORE heavy imports (Arch selftest spec 1aa43bdd §4 pattern; runner gate c7805d9a)
    _A = _cli()
    sys.path.insert(0, str(ROOT / "scripts_eng"))
    from ok_runner_pin import enforce
    _deps = gate_deps(_A.leaf, _A.universe, _A.base)
    if _A.legacy_json: _deps["legacy_json"] = Path(_A.legacy_json)
    _GATE = enforce(__file__, [_A.arch_ok], modes=["full"], deps=_deps)
    import research.alpha_v1_1_runguard as RG   # pinned above (dep_sha256_runguard; 35991407 reused unchanged); stdlib only
    _OUTP = RG.precheck_out_file(_A.out) if _A.out else None
    _OKREC = RG.ok_selfcheck([_A.arch_ok], _GATE, "full", out_target=_OUTP.parent if _OUTP else None)
    _MAN0 = RG.verify_manifest_shas(MANIFEST, "startup")     # v1.2 manifest
    _WD = RG.start_watchdog(rlimit_as_kb=RG.rlimit_as_kb())

import numpy as np, pandas as pd   # noqa: E402  (after the gate)
import research.alpha_decay_gate as ADG   # noqa: E402
import research.leaf_selfcheck_v3 as V3   # noqa: E402
_stage("imports")
B0W = {"capacity_adv": .5, "earnings_event": .25, "insider_increase": .25}
START, END = "2024-06-03", "2026-10-09"; COST = ADG.COST; H = 20
_CTX = {}


def _load_track(path) -> pd.DataFrame:
    b = pd.read_parquet(path)
    if "target_weight" not in b.columns:  # book-smoke format: session, instrument_id (sh.600000), weight
        b = b.rename(columns={"session": "date", "weight": "target_weight"})
        b["instrument"] = b["instrument_id"].str.split(".").map(lambda x: f"{x[1]}.{x[0].upper()}")
    b = b[["date", "instrument", "target_weight"]].copy(); b["date"] = b["date"].astype(str).str[:10]
    return b[b.target_weight > 0]


def _pool(c: dict, d) -> list:
    """M3: PIT pool on session d as a list in U order — identical to v1.1 [i for i in U if i in mem.get(d_str, set())] for every d in ev
    (ev_pos is built from ev itself). d not in ev → [] (v1.1 callers then fail on .loc[d] exactly as before; no caller passes such d)."""
    k = c["ev_pos"].get(d.strftime("%Y-%m-%d"))
    return [] if k is None else c["U_arr"][c["mem_mask"][k]].tolist()


def pool_ew() -> pd.Series:
    """HI_LIQ (or FULLA) pool equal-weight daily return (close-to-close, clipped ±20%, no cost) — disclosure benchmark."""
    c = ctx(); R = c["R"]; out = {}
    for d in R.index:
        mm = _pool(c, d)                                   # M3 (v1.1: mem set; non-empty ⇔ same list non-empty)
        if mm: out[d] = R.loc[d, mm].clip(-.2, .2).mean()
    return pd.Series(out).dropna()


def vs_pool_ew(r: pd.Series, ew: pd.Series) -> dict:
    b = ew.reindex(r.index).fillna(0.0); n = len(r)
    be = float(np.cov(r, b)[0, 1] / b.var()) if b.var() > 0 else 0.0; res = r - be * b; se = nw_se(res.values, 5)
    return dict(cagr=m(r)["cagr"], poolEW_cagr=float((1 + b).prod() ** (244 / n) - 1), excess_cagr=m(r)["cagr"] - float((1 + b).prod() ** (244 / n) - 1),
                beta_vs_poolEW=be, resid_alpha_vs_poolEW_244=float(res.mean() * 244), t_hac5=float(res.mean() / se) if se > 0 else None)


def set_universe(u: str):
    global UNIVERSE
    if u not in UNIVERSE_MASKS: raise ValueError(f"universe must be one of {list(UNIVERSE_MASKS)}")
    if u != UNIVERSE: _CTX.clear(); _B0.clear()
    UNIVERSE = u


def sw_snapshot_dates(cal: pd.DatetimeIndex, ev: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """SW L1 snapshot dates = SW_PRE_SNAPSHOT + last session of each window month. Asserts SW_PRE_SNAPSHOT is the last session before
    START in the calendar and the ONLY snapshot date < START (主 Agent 2026-10-18 P2-3 ruling)."""
    s0, st = pd.Timestamp(SW_PRE_SNAPSHOT), pd.Timestamp(START)
    pre = cal[cal < st]
    if len(pre) == 0 or pre.max() != s0: raise RuntimeError(f"SW pre-window snapshot {SW_PRE_SNAPSHOT} is not the last session before {START}")
    me = pd.DatetimeIndex([s0]).append(pd.DatetimeIndex(pd.Series(ev, index=ev).groupby(ev.to_period("M")).max().values))
    if list(me[me < st]) != [s0] or not me.is_monotonic_increasing or me.has_duplicates:
        raise RuntimeError(f"SW snapshot dates before START must be exactly [{SW_PRE_SNAPSHOT}]: {list(me[me < st])}")
    return me


def check_ind_coverage(IND: pd.DataFrame, mem_mask: np.ndarray, U_arr: np.ndarray, ev: pd.DatetimeIndex) -> dict:
    """Refuse if any window day's pool is entirely unclassified (all '_UNK'); report coverage. M3: pools from the ev×U mask, in ev order
    (= v1.1's dict built over ev), each pool in U order."""
    cov = {}
    for k, d in enumerate(ev):
        pool = U_arr[mem_mask[k]].tolist()
        if len(pool) == 0: continue
        cov[d] = float(IND.loc[d, pool].notna().mean())
    bad = [str(pd.Timestamp(d).date()) for d, v in cov.items() if v == 0.0]
    if bad: raise RuntimeError(f"all-_UNK industry days in window: {bad[:5]} (n={len(bad)})")
    s = pd.Series(cov)
    return dict(n_days=int(len(s)), n_all_unk_days=0, min_coverage=float(s.min()), first_day=str(pd.Timestamp(s.index.min()).date()),
                first_day_coverage=float(s.iloc[0]), mean_coverage=float(s.mean()))


def check_f_truncated(P: pd.DataFrame, F: pd.DataFrame, ev: pd.DatetimeIndex):
    """Replaces the tautological draft assert (Arch 31b4b8ba P3-1): prices end ≤ END and the last H window rows of F are all NaN."""
    if P.index.max() > pd.Timestamp(END): raise RuntimeError("P extends beyond END")
    if not F.reindex(ev).iloc[-H:].isna().all().all(): raise RuntimeError("F has values in the last H sessions before END")


def check_fmc_lower_bound(trade_dates) -> str | None:
    """Arch 6ab489c8 P1-1: float mcap rows actually read must all be ≥ START (no pre-window float mcap)."""
    if len(trade_dates) == 0: return None
    m = pd.Timestamp(pd.to_datetime(trade_dates).min())
    if m < pd.Timestamp(START): raise RuntimeError(f"float mcap read before START: {m.date()}")
    return str(m.date())


def _rel(p) -> str:
    try: return str(Path(p).resolve().relative_to(ROOT))
    except ValueError: return str(p)


def _af_loaded() -> bool:
    m = sys.modules.get("research.adj_price")
    return bool(m is not None and getattr(m, "_F", None) is not None)


def ctx():
    if _CTX: return _CTX
    from research.g1g5_nontextbook_weights import _load_sw_members, sw_code_on
    from research.g1g5_x2_panel_stitch import to_panel_id
    if PRICE_START != "2023-09-01": raise RuntimeError("price read start must stay byte-identical to bee23019 (2023-09-01)")
    b = ADG.bench(); days = b.index[(b.index >= PRICE_START) & (b.index <= END)]
    ev = days[(days >= START)]
    # ---- stage mk/mem (M3): same mask read as v1.1; mem as an ev×U boolean matrix instead of 570 Python sets
    mk = pd.read_parquet(UNIVERSE_MASKS[UNIVERSE], columns=["date", "instrument", "in_universe"],
                         filters=[("date", ">=", pd.Timestamp(START)), ("date", "<=", pd.Timestamp(END)), ("in_universe", "==", True)])
    mk["d"] = pd.to_datetime(mk["date"]).dt.strftime("%Y-%m-%d"); mk["instrument"] = mk["instrument"].astype(str)
    U = sorted(set(mk["instrument"]))
    U_arr = np.array(U, dtype=object)
    ev_pos = {d.strftime("%Y-%m-%d"): k for k, d in enumerate(ev)}             # v1.1 looked mem up by d.strftime("%Y-%m-%d")
    if len(ev_pos) != len(ev): raise RuntimeError("window sessions are not unique by date string")
    u_pos = {i: j for j, i in enumerate(U)}
    rk = mk["d"].map(ev_pos); keep = rk.notna().to_numpy()                        # mask dates that are not sessions in ev: never looked up in v1.1
    mem_mask = np.zeros((len(ev), len(U)), dtype=bool)
    mem_mask[rk.to_numpy()[keep].astype(np.int64), mk["instrument"].map(u_pos).to_numpy()[keep].astype(np.int64)] = True
    del mk, rk, keep; gc.collect()
    _stage("mk/mem", n_ev=len(ev), n_U=len(U), n_member_days=int(mem_mask.sum()))
    # ---- stage P (M1): per-instrument reindex onto days (≤ END → F truncated at END), popped from ADG._cache after use
    arr = np.full((len(days), len(U)), np.nan, dtype=np.float64)
    for j, i in enumerate(U):
        s = ADG._close(i)
        if not s.index.is_unique: raise RuntimeError(f"close series index not unique for {i} (v1.1 would also fail to align it)")
        if s.dtype != np.float64: raise RuntimeError(f"close series dtype {s.dtype} != float64 for {i} (v1.2 equivalence precondition)")
        arr[:, j] = s.reindex(days).to_numpy()
        ADG._cache.pop(i, None); del s                                           # AP._F (adj factors) is kept
        if j == 0: _stage("_factors", adj_factors_loaded=_af_loaded())
    if len(U) == 0: _stage("_factors", adj_factors_loaded=_af_loaded())
    P = pd.DataFrame(arr, index=days, columns=U, copy=False); del arr
    F = P.shift(-H) / P - 1                                                        # same formula as v1.1; computed before R so P can go
    check_f_truncated(P, F, ev)
    F_ev = F.reindex(ev); del F
    R = P.pct_change(fill_method=None); del P; gc.collect()
    _stage("P", n_days=len(days), adj_cache_left=len(ADG._cache))
    # ---- stage beta (unchanged formula); only the ev slices are kept (as v1.1 stored)
    rb = b.reindex(days).pct_change()
    beta = R.rolling(120, min_periods=60).cov(rb).div(rb.rolling(120, min_periods=60).var(), axis=0)
    beta_ev = beta.shift(1).reindex(ev); del beta                                 # v1.1: returns d−120..d−1
    R_ev = R.reindex(ev); del R, rb; gc.collect()
    _stage("beta")
    # ---- stage FMC (unchanged)
    pids = {to_panel_id(i): i for i in U}
    fm = pd.read_parquet(FMC, columns=["instrument_id", "trade_date", "float_mktcap"],
                         filters=[("trade_date", ">=", pd.Timestamp(START)), ("instrument_id", "in", list(pids))])   # == bee23019 L95
    fmc_min = check_fmc_lower_bound(fm["trade_date"])
    fm["i"] = fm.instrument_id.map(pids)
    FMp = fm.pivot_table(index="trade_date", columns="i", values="float_mktcap"); del fm
    cal = days[days >= pd.Timestamp(START)]
    MC_sig = np.log(FMp.reindex(cal).ffill()).shift(1).reindex(ev).reindex(columns=U)   # v1.1: close d−1; START row NaN (skipped)
    if MC_sig.loc[pd.Timestamp(START)].notna().any(): raise RuntimeError("START-day mc_{t−1} must be NaN (no pre-window float mcap)")
    del FMp; gc.collect()
    _stage("FMC")
    # ---- stage IND (unchanged lookup; coverage pools from the mask, M3)
    sw = _load_sw_members(); me = sw_snapshot_dates(days, ev)                  # v1.1: + 2024-05-31 (SW table only)
    IND = pd.DataFrame({i: [sw_code_on(i, d, sw) for d in me] for i in U}, index=me).reindex(ev, method="ffill")
    indcov = check_ind_coverage(IND, mem_mask, U_arr, ev)
    del sw; gc.collect()
    _stage("IND")
    _CTX.update(R=R_ev, universe=UNIVERSE, mask=_rel(UNIVERSE_MASKS[UNIVERSE]), U=U, U_arr=U_arr, ev=ev, ev_pos=ev_pos, mem_mask=mem_mask,
                beta=beta_ev, MC=MC_sig, IND=IND, F=F_ev, ind_coverage=indcov, sw_snapshots=[str(x.date()) for x in me],
                reads=dict(price_start=str(days.min().date()), fmc_earliest_trade_date=fmc_min, start_day_skipped=START))
    return _CTX


def sig(path, label: str | None = None) -> pd.DataFrame:
    """M2: zero-weight rows filtered at read (absent row ≡ zero row after reindex + fillna(0.0)). STAGE line reports nonzero rows and
    duplicate (date, instrument) keys among them: dup_keys_nonzero == 0 ⇒ every pivot cell sums ONE value in v1.1 and v1.2 alike."""
    c = ctx()
    d = pd.read_parquet(path, columns=["date", "instrument", "target_weight"], filters=[("target_weight", "!=", 0.0)])
    n_rows = int(len(d)); ndup = 0
    if n_rows:
        d["date"] = pd.to_datetime(d["date"].astype(str).str[:10])
        ndup = int(d.duplicated(["date", "instrument"]).sum())
        S = d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum"); del d
        S = S.reindex(index=c["ev"], columns=c["U"]).fillna(0.0)
    else:                                                                          # every row was zero (v1.1: all-zero pivot → 0.0 grid)
        del d; S = pd.DataFrame(0.0, index=c["ev"], columns=c["U"])
    _stage(f"sig:{label or Path(path).name}", rows_nonzero=n_rows, dup_keys_nonzero=ndup)
    return S


def resid_z(S: pd.DataFrame, extra: list[pd.DataFrame] | None = None) -> pd.DataFrame:
    """Residualise on SW L1 + mc_{t−1} + beta_{t−1} (v1.1) [+ extra signals at d]; z-score per day."""
    c = ctx(); out = pd.DataFrame(np.nan, index=S.index, columns=S.columns)
    for d in S.index:
        pool = _pool(c, d)                                                         # M3
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
    nav = (1 + r).cumprod(); return dict(cagr=float(nav.iloc[-1] ** (244 / len(r)) - 1), mdd=float((nav / nav.cummax() - 1).min()))


_B0 = {}


def b0():
    if _B0: return _B0
    S = {k: sig(p, label=k) for k, p in LEGS_BY_UNIVERSE[UNIVERSE].items()}; Z = {k: resid_z(s) for k, s in S.items()}
    combo = sum(B0W[k] * Z[k].fillna(0) for k in Z).where(Z["capacity_adv"].notna())
    del Z; gc.collect()                                                            # M4: Z never stored (v1.1 also dropped it on return)
    _B0.update(S=S, combo=combo, ic=ic_stats(combo))
    _stage("b0")
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
    B = b0(); wf = leaf_path(leaf)
    zl = resid_z(sig(wf, label="leaf"), extra=list(B["S"].values()))
    c1 = (0.8 * B["combo"] + 0.2 * zl.fillna(0)).where(B["combo"].notna())
    ic1 = ic_stats(c1)
    zs = resid_z(sig(wf, label="leaf_style"))  # style-only residual (ind/mcap/beta at t−1), for rho reference
    rho = [zs.loc[d].corr(B["combo"].loc[d]) for d in zs.index]
    rho_post = [zl.loc[d].corr(B["combo"].loc[d]) for d in zl.index]
    out = dict(tool_version=TOOL_VERSION, B0_ic=B["ic"], B1_ic=ic1, d_ic=ic1["rank_ic"] - B["ic"]["rank_ic"],
               d_icir_full=ic1["icir_full"] - B["ic"]["icir_full"],
               leaf_file=str(wf), b0_legs={k: str(v) for k, v in LEGS_BY_UNIVERSE[UNIVERSE].items()},
               universe=UNIVERSE, universe_mask=ctx()["mask"], universe_role="gate" if UNIVERSE == "hiliq" else "diagnostic_only",
               d_ic_tstats=ic_tstats(_d_ic_series(B["combo"], c1)),
               d_icir_roll252_median=(ic1["icir_roll252_median"] - B["ic"]["icir_roll252_median"]) if ic1["icir_roll252_median"] is not None and B["ic"]["icir_roll252_median"] is not None else None,
               rho_leaf_resid_vs_B0=float(np.nanmean(rho)), rho_after_leg_resid=float(np.nanmean(rho_post)),
               rho_note="rho 用叶对行业/市值/β（t−1）残差化后的信号 vs B0 组合信号（日均截面相关）；再对 B0 腿信号残差化后 ρ≈0（构造使然），另列 rho_after_leg_resid",
               exposure_anchor=dict(mc="log float mcap at close d−1", beta="returns d−120..d−1 vs 510300",
                                    ind="SW L1 members effective on the last month-end session ≤ d (same-day members on that date); "
                                        "2024-06-03..06-27 use the 2024-05-31 snapshot",
                                    pool="mask in_universe[d] (ADV/prev bar from sessions < d; ST/suspension = day-d status, known pre-open)",
                                    F="close d → close d+20, NaN if d+20 > END", vol20_used=False, mom_used=False, liq_used=False),
               ind_coverage=ctx()["ind_coverage"], sw_snapshot_dates_head=ctx()["sw_snapshots"][:3], reads=ctx()["reads"],
               diff_vs_bee23019=["signal mc/beta at t−1", "SW L1 2024-06-03..06-27 from the 2024-05-31 snapshot (was all _UNK)",
                                 "START day 2024-06-03 skipped in residualisation (no mc_{t−1}; float mcap read from START as before)"],
               tiers={})
    L = V3.LC._w(wf); EW = pool_ew()
    for tier, N in V3.NT.items():
        trk = CAPADV_BOOK_TRACKS[tier] if (UNIVERSE == "hiliq" and BASE == "capadv") else B4_TRACKS[UNIVERSE][tier]
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
        _stage(f"tiers:{tier}")
    out["definition_notes"] = __doc__
    return out


def legacy_column(path: str, new: dict, pinned_sha256: str) -> dict:
    """Disclosure-only comparison with an EXISTING legacy (bee23019) JSON output; the legacy tool is not imported or run.
    Refuses (Arch 31b4b8ba P3-3): bytes read now != the sha pinned by the gate (dep_sha256_legacy_json); a v1.1 or v1.2 output; universe
    mismatch; leaf file name mismatch; any tier whose base (capadv_hiliq_book_smoke / b4_diag) is missing or differs.
    Key names (v1_1 / diff_v1_1_minus_legacy) are kept from v1.1 for schema continuity: they hold this tool's (v1.2 ≡ v1.1 numerics) values."""
    p = Path(path); raw = p.read_bytes(); got = hashlib.sha256(raw).hexdigest()
    if got != pinned_sha256: raise SystemExit(f"--legacy-json sha {got} != gate-pinned {pinned_sha256} (changed after enforce)")
    L = json.loads(raw.decode("utf-8"))
    if L.get("tool_version") in ("v1.1", TOOL_VERSION): raise SystemExit(f"--legacy-json is a {L.get('tool_version')} output, not a legacy one")
    if str(L.get("universe")) != str(new["universe"]): raise SystemExit(f"--legacy-json universe {L.get('universe')!r} != current {new['universe']!r}")
    if Path(str(L.get("leaf_file", ""))).name != Path(str(new["leaf_file"])).name:
        raise SystemExit(f"--legacy-json leaf_file {L.get('leaf_file')!r} != current {new['leaf_file']!r}")
    for t, nt in new.get("tiers", {}).items():
        lb = ((L.get("tiers") or {}).get(t) or {}).get("base")
        if lb != nt.get("base"): raise SystemExit(f"--legacy-json tier {t} base {lb!r} != current {nt.get('base')!r}")
    keys = ("d_ic", "d_icir_full", "d_icir_roll252_median", "rho_leaf_resid_vs_B0")
    col = dict(role="disclosure_only (主 Agent 2026-10-18 02:44 ET; verdict uses v1.1)", legacy_tool_sha256=LEGACY_SHA,
               legacy_leaf_file=L.get("leaf_file"), legacy_json=str(p), legacy_json_sha256=got,
               legacy={k: L.get(k) for k in keys}, v1_1={k: new.get(k) for k in keys},
               diff_v1_1_minus_legacy={k: (new[k] - L[k]) if isinstance(new.get(k), (int, float)) and isinstance(L.get(k), (int, float)) else None for k in keys},
               tiers={})
    for t, nt in new.get("tiers", {}).items():
        lt = (L.get("tiers") or {}).get(t, {})
        col["tiers"][t] = dict(legacy_d_cagr_net=lt.get("d_cagr_net"), v1_1_d_cagr_net=nt.get("d_cagr_net"),
                               legacy_report_to_leo_eligible=lt.get("report_to_leo_eligible"), v1_1_report_to_leo_eligible=nt.get("report_to_leo_eligible"),
                               base=nt.get("base"))
    return col


if __name__ == "__main__":
    set_universe(_A.universe); BASE = _A.base
    r = cmc(_A.leaf); r.pop("definition_notes", None)
    if _A.legacy_json: r["legacy_comparison"] = legacy_column(_A.legacy_json, r, _GATE["deps"]["legacy_json"])
    _CL = RG.verify_closure(MANIFEST, "after compute")
    RG.recheck_expiry(_OKREC, "before write")
    r.update(live=False, promotion_approved=False, gate=_GATE, ok_selfcheck=_OKREC, closure=dict(startup=_MAN0, after_compute=_CL),
             watchdog=_WD, env=RG.env_snapshot(), peak_rss_kb=RG.rss_kb(), vm_peak_kb=RG.vm_peak_kb(),
             memory_refactor_of=dict(tool="research/alpha_combo_marginal_v1_1.py", sha256=V1_1_SHA,
                                     note="v1_2 sha != 5658f612: memory-only refactor (M1-M5), numerics asserted bit-identical on synthetic data "
                                          "(tests/test_alpha_v1_2_equiv_selftest.py); thresholds unchanged"))
    txt = json.dumps(r, ensure_ascii=False, indent=2, default=str)
    if _A.out:
        _OUTP.parent.mkdir(parents=True, exist_ok=True)
        with open(_OUTP, "x", encoding="utf-8") as f: f.write(txt)   # exclusive create (pre-checked before computing)
    print(txt)
