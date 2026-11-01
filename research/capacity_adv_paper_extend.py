#!/usr/bin/env python3
"""capacity_adv paper track daily extend (idempotent). Paper only; promotion=false; live=false; no Book-Smoke; no 8787.

History rows (<= 2026-10-09) are copied verbatim from the frozen file: a full-window recompute is NOT reproducible
(selector output depends on PYTHONHASHSEED and on data refreshed after the freeze), see receipt.
Forward days: non-rebalance day -> carry forward previous day's weights (frozen expand semantics);
forward month-end rebalance day -> one frozen-code decision for that session only.
Reuses the frozen leg code in research/g1g5_capacity_adv_weights.py unchanged (universe select, D1-ADV scoring,
name/industry/ADV caps, 80/20 ballast, build_daily_weights_expand). Only the end date moves.

Rebalance calendar (frozen rule = month-end + first + last of the frozen window):
  - frozen part: month_end_sessions(2024-01-02, 2026-10-09) + first + last  -> exactly the frozen file's calendar
    (2026-10-09 is a rebalance there because it was the window's last day; kept as history).
  - forward part: last SSE open day of each calendar month in (2026-10-09, data_end], from tushare trade_cal
    (so 2026-10-30, 2026-11-30, ... are known on the day). No rolling "last day" rebalance going forward,
    otherwise every daily run would rewrite yesterday's row.
Self-check (abort, write nothing on fail):
  - rows with date <= 2026-10-09 equal the frozen file row-by-row (keys/order/metadata identical, |dw| <= 1e-8);
    recomputed extra zero rows in history must be 0 and are dropped so history == frozen rows.
  - new rows: single stock <= NAME_CAP (0.04, from the frozen script), daily sum == 1 (1e-9), no negative,
    hard-exclude 600519/002371 absent.
Output: output/ai_factory/g1g5_capacity_adv_daily_weights_paper_<YYYYMMDD>.parquet + .check.json.
Exists+identical -> NOOP; exists+different -> abort (exit 3). Never overwrites the frozen file.
Usage: python3 research/capacity_adv_paper_extend.py [--end YYYY-MM-DD] [--calendar-only]
"""
from __future__ import annotations
import argparse, gc, hashlib, json, os, resource, sys
from pathlib import Path
# paper-extend path: lift X2 asof_extend clip (research default stays frozen at 2026-10-09); pin hash seed so the
# (hash-seed dependence fixed at the root in g1g5_capacity_adv_weights.py: stable code-order tie-breaks)
os.environ.setdefault("QL_X2_EXTEND_END", "2026-12-31")
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.g1g5_capacity_adv_weights as C  # noqa: E402  (frozen leg code, not modified)
from research.g1g5_expand_g6 import month_end_sessions, build_daily_weights_expand  # noqa: E402
from research.ai_debate_memory_runner import _load_benchmark_closes  # noqa: E402

FROZEN = ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"
FROZEN_START, FROZEN_END = C.WEIGHT_START, "2026-10-09"
OUT = ROOT / "output/ai_factory"; TOL = 1e-8
REV = "r2"  # 2026-10-13 Strategy ruling: rhythm = frozen X2 behaviour; deterministic selector
MON = OUT / "paper_monitor"
STATUS = ROOT / "output/daily_update_status.json"
COLS = ["date", "instrument", "target_weight", "mechanism_tag", "who_pays_zh", "universe_id", "session", "instrument_id", "weight"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()
TRACK_SCRIPTS = ["research/capacity_adv_paper_extend.py", "research/g1g5_capacity_adv_weights.py"]  # = capacity_adv_FROZEN_CONFIG


def script_shas(paths) -> dict:
    return {p: (sha(ROOT / p) if (ROOT / p).exists() else "MISSING") for p in paths}


def rss_mb() -> float: return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def data_end() -> str:
    from research.g1g5_x2_panel_stitch import load_panel_features_x2
    ends = [_load_benchmark_closes("510300").index.max()] + [load_panel_features_x2(s).index.max() for s in ("600036.SH", "000001.SZ")]
    return str(min(pd.Timestamp(e) for e in ends).date())


def calendar(end: str) -> tuple[list[str], list[str]]:
    reb = month_end_sessions(FROZEN_START, FROZEN_END)
    b = _load_benchmark_closes("510300"); cal0 = b.index[(b.index >= FROZEN_START) & (b.index <= FROZEN_END)]
    first, last = cal0[0].strftime("%Y-%m-%d"), cal0[-1].strftime("%Y-%m-%d")
    if reb[0] != first: reb = [first] + [x for x in reb if x != first]
    if last not in reb: reb.append(last)
    t = pd.read_parquet(ROOT / "data/v2/tushare_raw/trade_cal.parquet")
    t = t[(t.exchange == "SSE") & (t.is_open.astype(int) == 1)]
    d = pd.to_datetime(t.cal_date.astype(str)).sort_values()
    me = d.groupby(d.dt.to_period("M")).max().dt.strftime("%Y-%m-%d").tolist()
    fwd = [x for x in me if FROZEN_END < x <= end]
    return reb, fwd


def d1_end() -> str:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(str(C.D1_VALUATION)); mx = None
    for i in range(pf.metadata.num_row_groups):
        rg = pf.metadata.row_group(i)
        for j in range(rg.num_columns):
            col = rg.column(j)
            if col.path_in_schema == "trade_date" and col.statistics and col.statistics.has_min_max:
                v = str(pd.Timestamp(col.statistics.max).date()); mx = v if mx is None or v > mx else mx
    return mx or "0000-00-00"


REBAL_W: dict = {}


def d1_info() -> dict:
    p = C.D1_VALUATION; st = p.stat()
    return dict(path=str(p.relative_to(ROOT)), mtime=pd.Timestamp(st.st_mtime, unit="s", tz="UTC").tz_convert("America/New_York").isoformat(),
                size=st.st_size, sha256=sha(p), trade_date_max=d1_end())


def rebal_crosscheck(su: list, d: str, wm: pd.Series) -> dict:
    """Independent recompute of rebalance d: full-window decision path (frozen calendar + forward month-ends <= d)."""
    reb0, fwd0 = calendar(d)
    sessions = reb0 + [x for x in fwd0 if x != d] + [d]
    dec, _m, _i = C.build_rebalance_decisions_capacity_adv(su, sessions, active_n=C.DEFAULT_ACTIVE_N, use_pit_membership=True)
    w2 = pd.Series({x["instrument"]: float(x["target_weight_override"]) for x in dec if x["session"] == d})
    diff = w2.sub(wm, fill_value=0.0).abs()
    a, b = set(wm[wm > 0].index), set(w2[w2 > 0].index)
    r = dict(session=d, kind="rebalance_single_day_recompute_check", max_abs_diff=float(diff.max()), ok=bool(diff.max() <= TOL),
             only_used=sorted(a - b), only_recompute=sorted(b - a), n_names_used=len(a), d1=d1_info(),
             generated_at=pd.Timestamp.now(tz="America/New_York").isoformat())
    MON.mkdir(parents=True, exist_ok=True)
    (MON / f"capacity_adv_rebal_check_{d.replace('-', '')}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    del dec; gc.collect()
    return r


def forward(end: str, fwd: list[str], simulate: str | None = None) -> pd.DataFrame:
    F = pd.read_parquet(FROZEN)
    b = _load_benchmark_closes("510300")
    days = [x.strftime("%Y-%m-%d") for x in b.index if FROZEN_END < x.strftime("%Y-%m-%d") <= end]
    reb = set(fwd) | ({simulate} if simulate else set())
    prev = F[F.date == FROZEN_END][["instrument", "target_weight"]].reset_index(drop=True)
    su = None; out = []
    for d in days:
        if d in reb:
            d1max = d1_end()
            prevday = max(x for x in [y.strftime("%Y-%m-%d") for y in b.index] if x < d)
            if d1max < prevday:
                raise SystemExit(f"ABORT: D1 daily_basic_full ends {d1max} < {prevday}; rebalance {d} needs fresh ADV")
            st = json.loads(STATUS.read_text()) if STATUS.exists() else {}
            ml = (st.get("tables") or {}).get("mid_large_universe") or {}
            if str(ml.get("last_date", ""))[:10] < d:
                raise SystemExit(f"ABORT: daily_update_status tables.mid_large_universe.last_date={ml.get('last_date')} < rebalance {d}")
            import pyarrow.dataset as _ds
            mmax = str(_ds.dataset(str(ROOT / "data/v2/universe/mid_large_members_pit.parquet")).to_table(columns=["session"]).column("session").to_pandas().astype(str).str[:10].max())
            if mmax < d:
                raise SystemExit(f"ABORT: mid_large_members_pit ends {mmax} < rebalance {d}; frozen selector would fall to coverage_gap (100% 510300). Ask Data to extend.")
            if su is None:
                uni = C.select_mid_large_topn_light(top_n=C.DEFAULT_SCORE_N)
                su = [i for i in uni["instruments"] if i not in C.HARD_EXCLUDE]
            dec, _m, _i = C.build_rebalance_decisions_capacity_adv(su, [d], active_n=C.DEFAULT_ACTIVE_N, use_pit_membership=True)
            w1 = build_daily_weights_expand(dec, start=d, end=d, mechanism_tag=C.MECHANISM_TAG, who_pays_zh=C.WHO_PAYS_ZH, universe_id=C.UNIVERSE_ID)
            wm = w1.set_index("instrument").target_weight
            if float(wm.get(C.BALLAST_ETF, 0.0)) > 0.999:
                raise SystemExit(f"ABORT: rebalance {d} produced 100% ballast (coverage_gap); not writing")
            rebal_crosscheck(su, d, wm)
            REBAL_W[d] = wm
            order = list(prev.instrument) + [i for i in wm.index if i not in set(prev.instrument)]
            prev = pd.DataFrame({"instrument": order, "target_weight": [float(wm.get(i, 0.0)) for i in order]})
            gc.collect()
        r = prev.copy(); r["date"] = d; out.append(r)
    if not out:
        return pd.DataFrame(columns=COLS)
    N_ = pd.concat(out, ignore_index=True)
    N_["mechanism_tag"] = C.MECHANISM_TAG; N_["who_pays_zh"] = C.WHO_PAYS_ZH; N_["universe_id"] = C.UNIVERSE_ID
    N_["session"] = N_.date; N_["instrument_id"] = N_.instrument.map(lambda x: x[-2:].lower() + "." + x[:6]); N_["weight"] = N_.target_weight
    return N_[COLS]


def build(end: str, fwd: list[str], simulate: str | None = None) -> pd.DataFrame:
    F = pd.read_parquet(FROZEN)[COLS]
    return pd.concat([F, forward(end, fwd, simulate)], ignore_index=True)


FWD_EXPECTED: list = []


def check(W: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    F = pd.read_parquet(FROZEN)
    Hall = W[W.date <= FROZEN_END]
    fk = set(zip(F.date, F.instrument))
    inF = np.array([k in fk for k in zip(Hall.date, Hall.instrument)])
    extra = Hall[~inF]; H = Hall[inF].reset_index(drop=True)
    keys = len(H) == len(F) and (H[["date", "instrument"]].values == F[["date", "instrument"]].values).all()
    dmax = float(max(np.abs(H.weight.values - F.weight.values).max(), np.abs(H.target_weight.values - F.target_weight.values).max())) if keys else float("inf")
    meta = keys and all((H[c].astype(str).values == F[c].astype(str).values).all() for c in ("session", "instrument_id", "mechanism_tag", "who_pays_zh", "universe_id"))
    new = W[W.date > FROZEN_END]; pos = new[new.target_weight > 1e-15]
    stk = pos[pos.instrument != C.BALLAST_ETF]
    s = new.groupby("date").target_weight.sum()
    r = dict(frozen_rows=len(F), hist_rows=len(H), hist_keys_identical=bool(keys), hist_max_abs_diff=dmax,
             hist_meta_identical=bool(meta), hist_extra_rows=len(extra), hist_extra_all_zero=bool((extra.target_weight.abs() <= TOL).all()),
             new_rows=len(new), new_sessions=sorted(new.date.unique().tolist()),
             new_max_single_stock=float(stk.target_weight.max()) if len(stk) else None, name_cap=C.NAME_CAP,
             new_cap_ok=bool(stk.target_weight.max() <= C.NAME_CAP + 1e-9) if len(stk) else True,
             new_sum_ok=bool(((s - 1).abs() < 1e-9).all()), new_nonneg=bool((new.target_weight >= -1e-15).all()),
             new_hard_exclude_absent=bool(not pos.instrument.isin(C.HARD_EXCLUDE).any()))
    P = pd.concat([F[F.date == FROZEN_END], new]).pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    chg = [x for x in P.index[(P.diff().abs() > 1e-12).any(axis=1)] if x > FROZEN_END]
    r["new_change_days"] = chg; r["forward_rebalance_expected"] = sorted(FWD_EXPECTED)
    r["rhythm_ok"] = bool(set(chg) <= set(FWD_EXPECTED))
    r["hist_ok"] = bool(keys and meta and dmax <= TOL and r["hist_extra_all_zero"])
    r["ok"] = r["hist_ok"] and r["rhythm_ok"] and r["new_cap_ok"] and r["new_sum_ok"] and r["new_nonneg"] and r["new_hard_exclude_absent"]
    return r, pd.concat([H, new], ignore_index=True)


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--end"); ap.add_argument("--calendar-only", action="store_true")
    ap.add_argument("--simulate-rebalance", help="dry run: force a rebalance on this forward date, check only, write nothing")
    a = ap.parse_args()
    dend = data_end(); end = min(a.end or dend, dend)
    reb, fwd = calendar(end)
    info = dict(data_end=dend, end=end, frozen_rebalance_tail=reb[-4:], n_frozen_rebalance=len(reb), forward_rebalance=fwd,
                params=dict(score_n=C.DEFAULT_SCORE_N, active_n=C.DEFAULT_ACTIVE_N, stock_budget=C.STOCK_BUDGET, ballast=C.BALLAST_ETF,
                            name_cap=C.NAME_CAP, ind_cap=C.IND_CAP, adv_k=C.ADV_PARTICIPATION_K, aum_binding=C.AUM_BINDING),
                promotion_approved=False, live=False)
    if a.calendar_only:
        print(json.dumps(info, ensure_ascii=False, indent=1)); return 0
    FWD_EXPECTED[:] = fwd + ([a.simulate_rebalance] if a.simulate_rebalance else [])
    W = build(end, fwd, a.simulate_rebalance); c, OUTW = check(W); last = str(OUTW.date.max())
    if a.simulate_rebalance:
        d = OUTW[OUTW.date == a.simulate_rebalance]; pos = d[d.target_weight > 0]
        MON.mkdir(parents=True, exist_ok=True); tagd = a.simulate_rebalance.replace("-", "")
        d.to_parquet(MON / f"capacity_adv_simulate_{tagd}.parquet", index=False)
        (MON / f"capacity_adv_simulate_{tagd}.json").write_text(json.dumps(dict(
            session=a.simulate_rebalance, simulate=True, written_to_track=False,
            weights={i: float(w) for i, w in zip(pos.instrument, pos.target_weight)},
            prev_weights_20261009={i: float(w) for i, w in OUTW[(OUTW.date == FROZEN_END) & (OUTW.target_weight > 0)][["instrument", "target_weight"]].values},
            rebal_crosscheck=json.loads((MON / f"capacity_adv_rebal_check_{tagd}.json").read_text()) if (MON / f"capacity_adv_rebal_check_{tagd}.json").exists() else None,
            d1=d1_info()), ensure_ascii=False, indent=1))
        print(json.dumps(dict(simulate=a.simulate_rebalance, check_ok=c["ok"], n_pos=len(pos), ballast=float(pos[pos.instrument == C.BALLAST_ETF].target_weight.sum()),
                              max_stock=float(pos[pos.instrument != C.BALLAST_ETF].target_weight.max()), sum=float(d.target_weight.sum()),
                              n_changed_vs_prev=int((OUTW[OUTW.date == a.simulate_rebalance].set_index("instrument").target_weight
                                                     .sub(OUTW[OUTW.date == FROZEN_END].set_index("instrument").target_weight, fill_value=0).abs() > 1e-9).sum()),
                              peak_rss_mb=rss_mb()), ensure_ascii=False)); return 0
    fp = OUT / f"g1g5_capacity_adv_daily_weights_paper_{last.replace('-', '')}_{REV}.parquet"
    res = dict(info, check=c, last_session=last, file=str(fp.relative_to(ROOT)), frozen_file=str(FROZEN.relative_to(ROOT)), frozen_sha256=sha(FROZEN), d1=d1_info(),
               rebal_checks={k: json.loads((MON / f"capacity_adv_rebal_check_{k.replace('-', '')}.json").read_text()) for k in REBAL_W})
    rc = 0
    if not c["ok"]:
        res["status"] = "ABORT_SELFCHECK"; rc = 2
    else:
        tmp = fp.with_suffix(".tmp.parquet"); OUTW.to_parquet(tmp, index=False)
        if fp.exists():
            same = pd.read_parquet(fp).equals(pd.read_parquet(tmp)); tmp.unlink()
            res["status"] = "NOOP_EXISTS_IDENTICAL" if same else "ABORT_EXISTS_DIFFERENT"; rc = 0 if same else 3
        else:
            tmp.rename(fp); res["status"] = "WRITTEN"
        if fp.exists(): res["sha256"] = sha(fp)
    res["peak_rss_mb"] = rss_mb()
    res["frozen_script_sha256"] = script_shas(TRACK_SCRIPTS)
    res["recomputed_with_frozen_script"] = bool(fp.exists() and res.get("status") in ("WRITTEN", "NOOP_EXISTS_IDENTICAL"))
    res["basis_zh"] = "本脚本按冻结规则生成（历史逐行复制冻结文件，续出段用冻结腿代码 g1g5_capacity_adv_weights 月末决策/沿用）；NOOP 表示当前脚本重算与已有文件逐字节等价（DataFrame.equals）"
    res["last_date"] = last; res["history_max_abs_diff"] = c.get("hist_max_abs_diff")
    fp.with_suffix(".check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    Path(str(fp) + ".check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))  # <file>.parquet.check.json for Eng gate
    print(json.dumps({k: res.get(k) for k in ("status", "file", "last_session", "sha256", "peak_rss_mb")} | {"hist_ok": c["hist_ok"], "max_diff": c["hist_max_abs_diff"], "extra": c["hist_extra_rows"], "new_rows": c["new_rows"]}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
