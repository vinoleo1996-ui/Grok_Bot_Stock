"""NO-IC multi-sleeve book skeleton (Strategy, 2026-10-12).

Research / diagnostic only · promotion_approved=false · ban smallcap.
Leo AUM main conclusions: 600_000 and 1_000_000 CNY only.
Large-AUM (5M) results are appendix only — never the headline.

Book = full-rules CB (CB1 or CB2) + bond/gold ballast (511010 / 518880 inverse-vol).
Or MATPREM via --external-targets / --cb-mode MATPREM (handoff targets already include
CB≈50% + ballast≈50% — feed straight to run_book; do NOT re-combine_noic).
NO IC futures, NO 510500 basis proxy, NO smallcap, NO Full D1.

Usage:
  python3 -m quantlab.portfolio.v2_multisleeve_book_noic \
    --capital 600000 --cb-mode CB2 --windows X1,X2 \
    --out output/strategy_mbook_noic_diag
  python3 -m quantlab.portfolio.v2_multisleeve_book_noic --smoke   # 2–3 sessions, cheap
  python3 -m quantlab.portfolio.v2_multisleeve_book_noic \
    --cb-mode MATPREM --capitals 600000,1000000 --windows X1,X2 \
    --out output/strategy_mbook_noic_diag/matprem
  python3 -m quantlab.portfolio.v2_multisleeve_book_noic \
    --external-targets output/v3/handoff_strategy/cb_matprem \
    --capitals 600000,1000000 --windows X1,X2 \
    --out output/strategy_mbook_noic_diag/matprem
"""
from __future__ import annotations
import argparse, json, logging, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from quantlab.portfolio.v2_multisleeve_book import (  # noqa: E402
    Data, CASH_ETF, WINDOWS, SEALED, WINDOW_LABEL, HASH_FILES, MAX_GROSS,
    month_ends, sleeve_cb, sha, run_book, tc,
)

log = logging.getLogger("mbook_noic")
BOND, GOLD = "sh.511010", "sh.518880"
DEFAULT_CB_W = 0.50
DEFAULT_BAL_W = 0.50
ALLOWED_CAPITAL = (600_000, 1_000_000)
APPENDIX_CAPITAL_NOTE = "5_000_000 is appendix-only; refuse as main --capital"
DEFAULT_MATPREM_HANDOFF = "output/v3/handoff_strategy/cb_matprem"
BALAST_CODES = {BOND, GOLD, CASH_ETF}


def sleeve_cb2(D, idx, n=20, full_rules=True, **_):
    """Full-rules CB2: close<=130, lowest premium n (matches Beta cb_schedule('CB2'))."""
    x = D.CB[(D.CB.date >= idx[0] - pd.Timedelta(days=60)) & (D.CB.date <= idx[-1])]
    adv = x.pivot(index="date", columns="code", values="amount").mul(1e4).rolling(20, min_periods=20).mean()
    cl = x.pivot(index="date", columns="code", values="close")
    pr = x.pivot(index="date", columns="code", values="cb_over_rate")
    mat = pd.to_datetime(D.BAS.set_index("code").maturity_date, errors="coerce")
    EXCL = pd.Series(dtype="datetime64[ns]"); rs_idx = {}
    if full_rules:
        ev = pd.read_parquet(ROOT / "data/v2/cb/cb_events_actionable_pit.parquet")
        fr = ev[(ev.event_type == "强制赎回") & (ev.subtype.isin(["公告实施强赎", "公告提示强赎"]))].copy()
        fr["code"] = fr.ts_code.map(tc)
        EXCL = fr.groupby("code").available_at.min()
        rs = pd.read_parquet(ROOT / "data/v2/cb/raw/cb_share_raw.parquet")[["ts_code", "publish_date", "remain_size"]]
        rs["publish_date"] = pd.to_datetime(rs.publish_date); rs["code"] = rs.ts_code.map(tc)
        rs = rs.sort_values(["code", "publish_date"])
        rs_idx = {c: (g.publish_date.values.astype("datetime64[ns]"), g.remain_size.values.astype(float))
                  for c, g in rs.groupby("code")}
    S = {}
    for t in idx[::10]:
        if t not in cl.index:
            continue
        ok = (adv.loc[t] >= 1e7) & cl.loc[t].notna() & pr.loc[t].notna()
        ok &= pd.Series({c: pd.notna(mat.get(c, pd.NaT)) and (mat.get(c) - t).days >= 182 for c in ok.index})
        if full_rules:
            sz = {}
            t64 = np.datetime64(pd.Timestamp(t).to_datetime64())
            for c in ok.index:
                if c in rs_idx:
                    dts, vals = rs_idx[c]
                    j = int(dts.searchsorted(t64, side="right")) - 1
                    sz[c] = vals[j] if j >= 0 else 0.0
                else:
                    sz[c] = 0.0
            ok &= pd.Series(sz) >= 1e8
            ex = EXCL.reindex(ok.index)
            fr_hit = ex.notna() & (ex.dt.normalize() < pd.Timestamp(t).normalize())
            ok &= ~fr_hit
        el = ok[ok].index
        e2 = [c for c in el if cl.loc[t, c] <= 130]
        pick = pr.loc[t, e2].nsmallest(n).index if e2 else []
        S[t] = {c: 1 / len(pick) for c in pick} if len(pick) else {}
    sleeve_cb2.last_diag = dict(mode="CB2", full_rules=bool(full_rules), n_signals=len(S),
                                avg_names=float(np.mean([len(v) for v in S.values()])) if S else 0.0)
    return S


def sleeve_ballast(D, idx, **_):
    """511010 / 518880 inverse 60d-vol, monthly (MA-RP style without equity leg)."""
    cols = [BOND, GOLD]
    rr = D.HFQ[cols].pct_change()
    S = {}
    for t in [idx[0]] + month_ends(idx):
        iv = 1 / rr.loc[:t].tail(60).std().replace(0, np.nan)
        iv = iv.dropna()
        if iv.empty:
            S[t] = {BOND: 0.5, GOLD: 0.5}
        else:
            S[t] = (iv / iv.sum()).to_dict()
    return S


def load_external_targets(handoff_root: Path, capital: float | int, window: str):
    """Load handoff targets CSV → {Timestamp: {code: w}}.

    Handoff layout: <root>/AUM_<capital>/*targets_{window}.csv
    Targets are already synthesized CB≈50% + ballast≈50% — feed straight to run_book;
    do NOT pass through combine_noic (would double-count ballast).
    """
    root = Path(handoff_root)
    if not root.is_absolute():
        root = ROOT / root
    aum_dir = root / f"AUM_{int(capital)}"
    if not aum_dir.is_dir():
        if root.name.startswith("AUM_") and root.is_dir():
            aum_dir = root
        else:
            raise SystemExit(f"external-targets: missing AUM dir {aum_dir}")
    cands = sorted(aum_dir.glob(f"*targets_{window}.csv"))
    if not cands:
        raise SystemExit(f"external-targets: no *targets_{window}.csv under {aum_dir}")
    path = cands[0]
    df = pd.read_csv(path, parse_dates=["date"])
    need = {"date", "instrument", "target_weight"}
    if not need.issubset(df.columns):
        raise SystemExit(f"external-targets: {path} missing columns {need - set(df.columns)}")
    sched = {}
    for d, g in df.groupby("date"):
        wmap = {
            str(r.instrument): float(r.target_weight)
            for r in g.itertuples()
            if abs(float(r.target_weight)) > 1e-15
        }
        if wmap:
            sched[pd.Timestamp(d)] = wmap
    return sched, df, path


def pool_depth_from_targets(targets: pd.DataFrame):
    """Calendar-pool depth (CB names per rebalance day) — soft-risk for MATPREM X1."""
    is_cb = targets.instrument.astype(str).str.match(r"^(sh|sz)\.(11|12)")
    by = targets.loc[is_cb].groupby("date").size()
    all_days = targets.groupby("date").size()
    n_days = int(len(all_days))
    filled = by.reindex(all_days.index).fillna(0) if n_days else by
    n_empty = int((filled == 0).sum()) if n_days else 0
    return dict(
        n_rebalance_days=n_days,
        days_with_cb=int((by > 0).sum()) if len(by) else 0,
        days_empty_cb=n_empty,
        frac_empty=float(n_empty / n_days) if n_days else None,
        avg_cb_names=float(by.mean()) if len(by) else 0.0,
        avg_cb_names_all_reb=float(filled.mean()) if n_days else 0.0,
        min_cb_names=int(by.min()) if len(by) else 0,
        max_cb_names=int(by.max()) if len(by) else 0,
        n_unique_cb=int(targets.loc[is_cb, "instrument"].nunique()),
        ballast_codes=sorted(
            c for c in targets.instrument.unique()
            if str(c) in BALAST_CODES or str(c).endswith(("511010", "518880", "511880"))
        ),
    )


def combine_noic(cb_sched, bal_sched, idx, *, cb_w=DEFAULT_CB_W, bal_w=DEFAULT_BAL_W, cash_target=0.02):
    """Blend CB + ballast; park idle in 511880. No futures keys."""
    days = sorted(set(cb_sched) | set(bal_sched) | {idx[0]})
    out, rows = {}, []
    cur_cb, cur_bal = {}, {}
    for t in days:
        if t in cb_sched:
            cur_cb = cb_sched[t]
        if t in bal_sched:
            cur_bal = bal_sched[t]
        tg = {}
        for c, w in cur_cb.items():
            tg[c] = tg.get(c, 0.0) + cb_w * float(w)
        for c, w in cur_bal.items():
            tg[c] = tg.get(c, 0.0) + bal_w * float(w)
        invested = sum(abs(v) for v in tg.values())
        idle = max(0.0, 1.0 - invested)
        # soft cash_target: if idle > cash_target and book under-invested, leave as 511880
        if idle > 1e-12:
            tg[CASH_ETF] = tg.get(CASH_ETF, 0.0) + idle
        g = sum(abs(v) for v in tg.values())
        if g > 1.0 + 1e-9:
            tg = {k: v / g for k, v in tg.items()}
        out[t] = tg
        rows.append(dict(session=t, cb_w=cb_w, bal_w=bal_w, invested=invested, idle=idle,
                         n_cb=sum(1 for c in cur_cb if cur_cb[c] > 0)))
    sf = pd.DataFrame(rows).set_index("session") if rows else None
    return out, sf


def build_book(D, idx, *, cb_mode="CB2", cb_w=DEFAULT_CB_W, bal_w=DEFAULT_BAL_W, full_rules=True):
    if abs(cb_w + bal_w - 1.0) > 1e-6:
        raise SystemExit(f"cb_w+bal_w must sum to 1 (got {cb_w}+{bal_w})")
    if cb_mode.upper() == "CB2":
        cb = sleeve_cb2(D, idx, full_rules=full_rules)
        notes = dict(cb=getattr(sleeve_cb2, "last_diag", {}), mode="CB2")
    elif cb_mode.upper() == "CB1":
        cb = sleeve_cb(D, idx, mode="CB1", full_rules=full_rules)
        notes = dict(cb=getattr(sleeve_cb, "last_diag", {}), mode="CB1")
    elif cb_mode.upper() in ("MATPREM", "MATPREM_EXTERNAL"):
        raise SystemExit(
            "cb-mode MATPREM uses --external-targets (handoff already includes ballast); "
            "do not call build_book/combine_noic"
        )
    else:
        raise SystemExit(f"unknown --cb-mode {cb_mode}; use CB1, CB2, or MATPREM (+ --external-targets)")
    bal = sleeve_ballast(D, idx)
    sched, sf = combine_noic(cb, bal, idx, cb_w=cb_w, bal_w=bal_w)
    desc = (f"NO-IC diagnostic book: full-rules {cb_mode.upper()} {cb_w:.0%} + "
            f"511010/518880 ballast {bal_w:.0%}; no IC / no 510500 / no smallcap")
    return sched, sf, desc, notes


def run_smoke(D, capital=600_000):
    """Cheap 2–3 session structural smoke on the latest X2 dates — no Full D1."""
    s, e = WINDOWS["X2"]
    idx = D.HFQ.loc[s:e].index
    if len(idx) < 5:
        raise SystemExit("smoke: X2 calendar too short")
    # last ~3 month-ends or last 3 decimated signal days
    smoke_idx = idx[-60:]  # enough history for vol lookback
    sched, sf, desc, notes = build_book(D, smoke_idx, cb_mode="CB2", full_rules=True)
    # keep only last 3 signal days
    keys = sorted(sched)[-3:]
    sched = {k: sched[k] for k in keys}
    a, b = str(keys[0].date()), str(smoke_idx[-1].date())
    out = ROOT / "output/strategy_mbook_noic_diag/smoke"
    meta = dict(arm="NOIC_SMOKE", description=desc, research_only=True, promotion_approved=False,
                diagnostic=True, smallcap=False, no_ic=True, capital=capital,
                smoke_sessions=[str(k.date()) for k in keys], sleeve_notes=notes,
                appendix_note=APPENDIX_CAPITAL_NOTE)
    m = run_book(D, sched, a, b, out, initial_cash=float(capital), sleeve_frame=sf, meta=meta)
    m.pop("_raw", None)
    json.dump(m, open(out / "smoke_summary.json", "w"), indent=1, default=str)
    log.info("smoke ok sessions=%s cagr=%.4f (diagnostic only)", keys, m.get("cagr"))
    return m


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--capital", type=float, default=600_000,
                    help="main conclusion AUM: 600000 or 1000000 only (5M=appendix, refused as main)")
    ap.add_argument("--capitals", default=None,
                    help="comma list e.g. 600000,1000000 to run both main AUMs")
    ap.add_argument("--cb-mode", default="CB2",
                    choices=["CB1", "CB2", "cb1", "cb2", "MATPREM", "matprem", "MATPREM_EXTERNAL"])
    ap.add_argument("--external-targets", default=None,
                    help="handoff root (e.g. output/v3/handoff_strategy/cb_matprem) with "
                         "AUM_*/ *targets_X*.csv; already includes ballast — skips combine_noic")
    ap.add_argument("--cb-w", type=float, default=DEFAULT_CB_W)
    ap.add_argument("--bal-w", type=float, default=DEFAULT_BAL_W)
    ap.add_argument("--windows", default="X1,X2")
    ap.add_argument("--cash-target", type=float, default=0.02)
    ap.add_argument("--out", default="output/strategy_mbook_noic_diag")
    ap.add_argument("--smoke", action="store_true", help="2–3 session structural smoke only")
    ap.add_argument("--allow-appendix-5m", action="store_true",
                    help="permit capital=5e6 as appendix arm (tagged appendix_only; not main conclusion)")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    mode = a.cb_mode.upper()
    ext = a.external_targets
    if mode in ("MATPREM", "MATPREM_EXTERNAL") and not ext:
        ext = DEFAULT_MATPREM_HANDOFF
        log.info("MATPREM mode → default --external-targets %s", ext)
    use_external = bool(ext)
    if use_external:
        mode = "MATPREM_EXTERNAL"

    D = Data(with_cb=True, with_ind_etf=False)
    if a.smoke and not use_external:
        return run_smoke(D, capital=int(a.capital) if a.capital in ALLOWED_CAPITAL else 600_000)

    caps = [float(x) for x in (a.capitals.split(",") if a.capitals else [a.capital])]
    for c in caps:
        if c in ALLOWED_CAPITAL:
            continue
        if c == 5_000_000 and a.allow_appendix_5m:
            log.warning("capital=5e6 tagged APPENDIX ONLY — not a main conclusion")
            continue
        raise SystemExit(
            f"--capital {c} refused. Main conclusions use {ALLOWED_CAPITAL}. "
            f"5M needs --allow-appendix-5m and is appendix-only. {APPENDIX_CAPITAL_NOTE}"
        )

    hashes = {f: sha(f) for f in HASH_FILES}
    out = Path(ROOT / a.out)
    table = {}
    wins = {w: WINDOWS[w] for w in a.windows.split(",")}
    for wn, (s, e) in wins.items():
        if pd.Timestamp(s) <= pd.Timestamp(SEALED[1]) and pd.Timestamp(e) >= pd.Timestamp(SEALED[0]):
            raise SystemExit(f"window {wn} overlaps SEALED {SEALED}; refused (no Full D1 / no sealed)")
    for capital in caps:
        appendix = (capital == 5_000_000)
        for wn, (s, e) in wins.items():
            t0 = time.time()
            if use_external:
                sched, tdf, tpath = load_external_targets(Path(ext), capital, wn)
                depth = pool_depth_from_targets(tdf)
                sf = None
                try:
                    src = str(tpath.relative_to(ROOT))
                except ValueError:
                    src = str(tpath)
                desc = (
                    f"NO-IC diagnostic book: MATPREM external targets "
                    f"(CB calendar-pool low-prem + ballast already in CSV) from {src}; "
                    f"no combine_noic re-stack; no IC / no 510500 / no smallcap"
                )
                notes = dict(
                    mode="MATPREM_EXTERNAL",
                    source=src,
                    handoff_root=str(ext),
                    pool_depth=depth,
                    soft_risk_x1_empty_approx="81.7% when X1 calendar pool thin (ballast-dominated)",
                    n_signal_days=len(sched),
                )
                tag = f"{wn}/NOIC_MATPREM_{int(capital)}"
                cb_meta = "MATPREM_EXTERNAL"
                ballast_note = (
                    "embedded in external targets (511010/518880); NOT re-applied via sleeve_ballast"
                )
            else:
                idx = D.HFQ.loc[s:e].index
                sched, sf, desc, notes = build_book(
                    D, idx, cb_mode=a.cb_mode, cb_w=a.cb_w, bal_w=a.bal_w, full_rules=True)
                depth = None
                tag = f"{wn}/NOIC_{a.cb_mode.upper()}_{int(capital)}"
                cb_meta = a.cb_mode.upper()
                ballast_note = "511010/518880 inverse-60d-vol monthly (MA-RP style without equity)"
            meta = dict(
                arm="NOIC_BOOK" if not use_external else "NOIC_MATPREM",
                description=desc, window=wn,
                window_label=WINDOW_LABEL.get(wn, "custom"),
                window_dates=[s, e], research_only=True, promotion_approved=False,
                diagnostic=True, smallcap=False, no_ic=True, no_510500=True,
                capital=capital, appendix_only=appendix,
                main_aum_policy="report 600k and 1M as headlines; 5M appendix only",
                cb_mode=cb_meta, cb_w=a.cb_w, bal_w=a.bal_w,
                ballast=ballast_note,
                max_gross=1.0, leverage=1.0,
                data_hashes=hashes, sleeve_notes=notes,
                futures="NONE (NO-IC book)",
                watch_beta="reconcile immediately when Beta drops handoff under output/v3/handoff_strategy/",
            )
            if depth is not None:
                meta["pool_depth"] = depth
                meta["soft_risk"] = (
                    f"X1 empty≈{depth.get('frac_empty')}; avg_cb≈{depth.get('avg_cb_names_all_reb')} "
                    "(calendar pool thin → X1 mostly ballast)"
                    if wn == "X1" else
                    f"empty={depth.get('frac_empty')}; avg_cb={depth.get('avg_cb_names_all_reb')}"
                )
            m = run_book(D, sched, s, e, out / tag, initial_cash=float(capital),
                         sleeve_frame=sf, meta=meta)
            m.pop("_raw", None)
            if depth is not None:
                m["pool_depth"] = depth
            table[tag] = m
            log.info("%s cagr=%.4f mdd=%.4f sh=%.2f capital=%s empty=%.3f (%.0fs) diagnostic",
                     tag, m["cagr"], m["mdd"], m["sharpe"], int(capital),
                     (depth or {}).get("frac_empty", -1.0) if depth else -1.0, time.time() - t0)
    summary = dict(
        research_only=True, promotion_approved=False, diagnostic=True, no_ic=True,
        smallcap=False, main_capitals=[600000, 1000000],
        appendix_note=APPENDIX_CAPITAL_NOTE,
        cb_mode=mode,
        external_targets=str(ext) if ext else None,
        compare=table,
        prereg_refs=[
            "docs/v2/V3_CIB2_NOIC_PREREG.md",
            "docs/v2/STRATEGY_NOIC_AUM_SKELETON_ZH.md",
            "docs/v2/CB_PREREG.md",
            "docs/v2/V3_CB_MATPREM_PREREG.md",
        ],
    )
    out.mkdir(parents=True, exist_ok=True)
    json.dump(summary, open(out / "compare_table.json", "w"), indent=1, default=str)
    readme = (
        "# NO-IC multi-sleeve book (diagnostic)\n\n"
        "- **promotion_approved=false** · research / diagnostic only · **ban smallcap**\n"
        "- Main conclusion AUM: **60万 / 100万** (`--capital 600000` / `1000000`)\n"
        "- **Large-AUM (5M) results are appendix only** — never headline metrics.\n"
        "- Sleeves: full-rules CB1/CB2 + 511010/518880 ballast, **or** `--cb-mode MATPREM` / "
        "`--external-targets` (handoff CB+ballast, no re-stack). **No IC futures**, no 510500 proxy.\n"
        "- Do **not** run Full D1 / sealed window here.\n"
        "- Watch Beta handoffs under `output/v3/handoff_strategy/`; reconcile immediately when present.\n"
        "- Related fail_explore (no handoff): TCarry-G, CIB2-NOIC, CB3-IC — see "
        "`docs/v2/PREREGISTRATION_V2_ZH.md` descriptive section.\n"
    )
    if use_external:
        readme += (
            "\n## MATPREM external mode\n"
            f"- source: `{ext}`\n"
            "- Soft risk: **X1 日历池空仓≈81.7%**，近一年主要靠债金压舱。\n"
        )
    (out / "README.md").write_text(readme, encoding="utf-8")
    return summary


if __name__ == "__main__":
    main()
