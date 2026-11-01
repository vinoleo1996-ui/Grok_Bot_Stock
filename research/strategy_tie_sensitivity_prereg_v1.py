#!/usr/bin/env python3
"""PRE-REGISTERED tie-break sensitivity v1 (docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md, rev2 after Arch review
docs/v2/ARCH_TIE_SENSITIVITY_PREREG_REVIEW_ZH.md). RESEARCH-ONLY. live=false; promotion=false; no paper/FROZEN touch; no sealed.

DO NOT RUN without the Arch-written structured run-auth file output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok
(format spec in the prereg §6; parser modelled on research/optimizer_core_x2_run.py b6238254 parse_run_auth).

Arms: B4@HI_LIQ (N1 legs, 50/25/25 diagnostic, per-leg Top-6 @600000 / Top-10 @1000000) x 24 fixed variants
      {PROD, CODE, ADV, SPLIT, RAND1..RAND20}; capadv-only@HI_LIQ_V1.1 (full 25-name leg, no Top-N) = one PROD run,
      null by construction (pinned audit CSV: 0 duplicate scores at 35/35 rebalances) and checked vs existing capadv_x2.
Order: auth -> sha checks -> out_dir -> build all weights -> PROD reproduction gate -> smokes -> summary.
Any failure -> SystemExit; partial results are VOID (VOID.md written, no summary.json).
The pure functions (parse_run_auth, enforce_run_auth, check_out_dir, file_sha256, select_split) load no market data."""
from __future__ import annotations
import hashlib, json, re, sys, time, resource
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "output/strategy_hiliq/ARCH_RUN_AUTH_TIE_SENS_v1.ok"
OUT_REL = "output/strategy_hiliq/tie_sens_prereg_v1"
SEEDS = list(range(1, 21))  # RAND1..RAND20 = integer seeds 1..20 (fixed; NOT extended)
VARIANTS = ["PROD", "CODE", "ADV", "SPLIT"] + [f"RAND{s}" for s in SEEDS]
SELECTABLE = ()  # no variant may ever be adopted as a rule from these results (prereg §4 rule 6)
TIERS = (600000, 1000000)
TOL_CAPADV = 1e-6

# file pinned in the .ok : .ok key -> repo-relative path
PINNED = {
    "script_sha256": "research/strategy_tie_sensitivity_prereg_v1.py",
    "prereg_sha256": "docs/v2/STRATEGY_TIE_SENSITIVITY_PREREG_ZH.md",
    "dep_ts_sha256": "research/strategy_capadv_topn_tie_sensitivity.py",
    "dep_lr_sha256": "research/strategy_b4_hiliq_leg_review.py",
    "dep_hx2_sha256": "research/strategy_hiliq_capadv_b4_x2.py",
    "ref_weights_60w_sha256": "output/strategy_hiliq/b4_leg_review/weights_B4_50_25_25_60w.parquet",
    "ref_weights_100w_sha256": "output/strategy_hiliq/b4_leg_review/weights_B4_50_25_25_100w.parquet",
    "audit_csv_sha256": "output/strategy_hiliq/topn_tie_audit/capadv_leg_score_tie_by_rebalance.csv",
    "capadv_pos_weights_sha256": "output/strategy_hiliq/b4_leg_review/capadv_only_pos_weights.parquet",
    "capadv_ref_nav_60w_sha256": "output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK/nav.csv",
    "capadv_ref_nav_100w_sha256": "output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK/nav.csv",
    "leg_capadv_sha256": "output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
    "leg_ee_sha256": "output/strategy_hiliq/legs/g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
    "leg_ii_sha256": "output/strategy_hiliq/legs/g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet",
}
AUTH_REQUIRED = ("format", "version", "signed_by", "signed_et", "allow_full", "allow_smoke", "out_dir") + tuple(PINNED)


def file_sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_run_auth(path: Path) -> dict:
    """Only lines ^[a-z0-9_]+=value$ are parsed; other text ignored. Missing/empty/duplicate/invalid -> SystemExit."""
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"tie_sens blocked: run-auth file missing: {path} (Arch writes it; Strategy never creates it)")
    kv: dict = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z0-9_]+)=(.*)$", ln.strip())
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if k in kv:
            raise SystemExit(f"tie_sens blocked: run-auth field '{k}' appears more than once")
        kv[k] = v
    miss = [k for k in AUTH_REQUIRED if not kv.get(k)]
    if miss:
        raise SystemExit(f"tie_sens blocked: run-auth lacks structured fields {miss}")
    if kv["format"] != "quantlab_run_auth_v1":
        raise SystemExit(f"tie_sens blocked: format={kv['format']!r}, expected quantlab_run_auth_v1")
    if kv["version"] != "tie_sens_v1":
        raise SystemExit(f"tie_sens blocked: version={kv['version']!r}, expected tie_sens_v1")
    if kv["signed_by"].lower() != "arch":
        raise SystemExit(f"tie_sens blocked: signed_by={kv['signed_by']!r}, expected arch")
    for k in ("allow_full", "allow_smoke"):
        if kv[k] not in ("true", "false"):
            raise SystemExit(f"tie_sens blocked: {k}={kv[k]!r}, must be exactly true or false")
        kv[k] = kv[k] == "true"
    for k in PINNED:
        if not re.fullmatch(r"[0-9a-f]{64}", kv[k]):
            raise SystemExit(f"tie_sens blocked: {k} is not a 64-hex lowercase sha256")
    return kv


def enforce_run_auth(kv: dict, root: Path = ROOT) -> dict:
    """Mode + runtime sha256 of every pinned file must match the .ok. Returns measured shas."""
    if kv["allow_full"] is not True:
        raise SystemExit("tie_sens blocked: allow_full is not true (this script has only a full mode)")
    if kv["allow_smoke"] is not False:
        raise SystemExit("tie_sens blocked: allow_smoke must be false (no smoke/partial mode exists)")
    if kv["out_dir"] != OUT_REL:
        raise SystemExit(f"tie_sens blocked: out_dir={kv['out_dir']!r} != {OUT_REL!r}")
    got = {}
    for k, rel in PINNED.items():
        p = Path(root) / rel
        if not p.exists():
            raise SystemExit(f"tie_sens blocked: pinned file missing: {rel}")
        got[k] = file_sha256(p)
        if got[k] != kv[k]:
            raise SystemExit(f"tie_sens blocked: sha256 mismatch for {rel}: measured {got[k]} != authorized {kv[k]}")
    return got


def check_out_dir(out: Path) -> None:
    out = Path(out)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise SystemExit(f"tie_sens blocked: output dir exists and is not an empty directory: {out}")


def select_split(st, n):
    """SPLIT (disclosure-only baseline): names with w > w_(N) kept; if the tie group at the N-th weight crosses the
    cutoff, ALL tied names are kept and share the remaining slots' budget equally (each tied weight x slots/len(group));
    may hold > N names. st: pandas Series of leg stock weights. Leg renormalisation happens in the caller."""
    v = st.round(12)
    if len(v) <= n:
        return st.copy()
    thr = v.sort_values(ascending=False, kind="mergesort").iloc[n - 1]
    above = st[v > thr]
    grp = st[v == thr]
    slots = n - len(above)
    if len(grp) <= slots:  # no crossing tie
        return st[v >= thr]
    return __import__("pandas").concat([above, grp * (slots / len(grp))])


def void(out: Path, msg: str):
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "VOID.md").write_text(f"# VOID — tie_sens_v1\n\n{msg}\n\nNo partial results may be reported (prereg §5).\n", encoding="utf-8")
    finally:
        raise SystemExit(f"tie_sens VOID: {msg}")


def main():
    kv = parse_run_auth(GATE)
    shas = enforce_run_auth(kv)
    out = ROOT / OUT_REL
    check_out_dir(out)
    import numpy as np, pandas as pd, importlib.util
    sp = importlib.util.spec_from_file_location("ts", ROOT / PINNED["dep_ts_sha256"]); ts = importlib.util.module_from_spec(sp); sp.loader.exec_module(ts)
    lr, hx2 = ts.lr, ts.hx2
    out.mkdir(parents=True, exist_ok=True); t0 = time.time()
    meta = dict(banner="PREREG tie_sens_v1; X2 in-sample; live=false; promotion=false; paper untouched; descriptive only",
                variants=VARIANTS, selectable=list(SELECTABLE), run_auth=dict(file=str(GATE.relative_to(ROOT)), sha256=file_sha256(GATE), fields=kv), measured_sha256=shas)
    # capadv-only null premise from the PINNED audit CSV (sha already verified)
    au = pd.read_csv(ROOT / PINNED["audit_csv_sha256"])
    if len(au) != 35 or int(au.dup_scores_in_ranked.sum()) != 0 or not bool(au.match_prod.all()):
        void(out, "capadv-only null premise violated in pinned audit CSV")
    sess = sorted(pd.read_parquet(ts.LEGS["capacity_adv"], columns=["session"]).session.astype(str).str[:10].unique())
    A = ts.adv_table([x for x in sess if x >= "2024-01-01"])

    def selector(name):
        if name == "PROD": return ts.sel_prod
        if name == "CODE": return ts.keyed(lambda st, s, k: np.argsort(np.argsort(np.array(st.index))))
        if name == "SPLIT": return lambda st, n, s, k: select_split(st, n)
        if name == "ADV":
            def advk(st, s, k):
                row = A.loc[s] if s in A.index else pd.Series(dtype=float); return -row.reindex(st.index).fillna(0.0).values
            return ts.keyed(advk)
        seed = int(name[4:])
        return ts.keyed(lambda st, s, k, seed=seed: np.array([int(hashlib.md5(f"{seed}|{k}|{i}".encode()).hexdigest()[:12], 16) for i in st.index]))

    # 1) build all weights (no returns)
    W = {}
    for v in VARIANTS:
        for aum, w in ts.build(selector(v)).items():
            W[(v, aum)] = w
    # 2) reproduction gate BEFORE any smoke: PROD == reference weights exactly, both tiers
    for aum in TIERS:
        ref = pd.read_parquet(ROOT / PINNED[f"ref_weights_{aum // 10000}w_sha256"], columns=["session", "instrument", "weight"])
        j = W[("PROD", aum)][["session", "instrument", "weight"]].merge(ref, on=["session", "instrument"], how="outer", suffixes=("", "_ref"), indicator=True)
        if (j["_merge"] != "both").any() or float((j.weight - j.weight_ref).abs().max()) != 0.0:
            void(out, f"PROD reproduction gate failed at {aum}: rows_only_one_side={int((j['_merge'] != 'both').sum())}")
    meta["reproduction_gate"] = "PASS (PROD == b4_leg_review reference, max|dw|=0, both tiers)"

    def turnover(w):
        P = w.pivot_table(index="session", columns="instrument", values="weight", aggfunc="sum").fillna(0).sort_index()
        P = P.loc[(P.index >= "2024-06-03") & (P.index <= "2026-10-09")]
        return float(0.5 * P.diff().abs().sum(axis=1).iloc[1:].mean() * 244)

    def smoke(fp, sd, caps):
        sm = lr.run_smoke(fp, sd, caps)
        if not sm or sm.get("ok") is False or "by_capital" not in sm:
            void(out, f"smoke failed: {sd.name}")
        return sm

    def collect(sm, sd, aum, w=None):
        nav = sd / f"aum_{aum}" / "X2" / "BOOK" / "nav.csv"
        if not nav.exists():
            void(out, f"nav missing: {nav}")
        m = lr.nav_metrics(nav)
        bk = next((x for kk, x in (sm["by_capital"].get(str(aum)) or {}).items() if "BOOK" in kk), None)
        if bk is None or any(m.get(k) is None or not np.isfinite(m[k]) for k in ("cagr", "mdd", "calmar")):
            void(out, f"metrics missing: {sd.name} {aum}")
        r = dict(cagr=m["cagr"], mdd=m["mdd"], calmar=m["calmar"], sharpe=m["sharpe"], win_daily=m["win_daily"], win_monthly=m["win_monthly"],
                 cost_pct_initial=bk.get("cost_pct_initial"), fill_ratio=bk.get("fill_ratio"))
        if w is not None:
            st = w[~w.instrument.map(hx2._is_etf) & (w.session >= "2024-06-03")]
            r.update(turnover_ann_oneway_target=turnover(w), mean_stock_names=float(st.groupby("session").size().mean()))
        return r

    # 3) smokes (serial)
    res = {}
    for v in VARIANTS:
        for aum in TIERS:
            tag = f"B4_{v}_{aum // 10000}w"; fp = out / f"weights_{tag}.parquet"; W[(v, aum)].to_parquet(fp, index=False)
            sd = out / f"smoke_{tag}"; res[tag] = collect(smoke(fp, sd, str(aum)), sd, aum, W[(v, aum)])
            print(tag, round(res[tag]["cagr"], 4), round(res[tag]["mdd"], 4), f"rss_mb={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f}", flush=True)
    sd = out / "smoke_CAPADV_ONLY_PROD"; sm = smoke(ROOT / PINNED["capadv_pos_weights_sha256"], sd, "600000,1000000")
    for aum in TIERS:
        r = collect(sm, sd, aum); refm = lr.nav_metrics(ROOT / PINNED[f"capadv_ref_nav_{aum // 10000}w_sha256"])
        r["diff_vs_capadv_x2"] = dict(cagr=abs(r["cagr"] - refm["cagr"]), mdd=abs(r["mdd"] - refm["mdd"]))
        if max(r["diff_vs_capadv_x2"].values()) > TOL_CAPADV:  # prereg §4 rule 5
            void(out, f"capadv-only differs from capadv_x2 at {aum}: {r['diff_vs_capadv_x2']} (engine non-determinism?)")
        res[f"CAPADV_ONLY_PROD_{aum // 10000}w"] = r
    # 4) pre-registered distribution summary
    for aum in TIERS:
        t = f"{aum // 10000}w"
        for k in ("cagr", "mdd", "calmar", "sharpe", "win_daily", "win_monthly", "cost_pct_initial", "fill_ratio", "turnover_ann_oneway_target"):
            x = np.array([res[f"B4_RAND{s}_{t}"][k] for s in SEEDS], float)
            res[f"RAND_dist_{k}_{t}"] = dict(n=len(x), median=float(np.median(x)), p10=float(np.percentile(x, 10)), p25=float(np.percentile(x, 25)),
                                             p75=float(np.percentile(x, 75)), p90=float(np.percentile(x, 90)), min=float(x.min()), max=float(x.max()),
                                             **{f"pct_rank_{v}": float((x < res[f"B4_{v}_{t}"][k]).mean()) for v in ("PROD", "CODE", "ADV", "SPLIT")})
        c = res[f"RAND_dist_cagr_{t}"]
        res[f"flags_{t}"] = dict(PROD_outside_p10_p90=not (c["p10"] <= res[f"B4_PROD_{t}"]["cagr"] <= c["p90"]),
                                 CODE_outside_p10_p90=not (c["p10"] <= res[f"B4_CODE_{t}"]["cagr"] <= c["p90"]),
                                 width_p90_p10_gt_5pp=(c["p90"] - c["p10"]) > 0.05, headline=f"RAND median {c['median']:.4f} [p10 {c['p10']:.4f}, p90 {c['p90']:.4f}]")
    meta.update(results=res, elapsed_min=(time.time() - t0) / 60, peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    (out / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, default=float)); print("WROTE", out / "summary.json")


if __name__ == "__main__":
    main()
