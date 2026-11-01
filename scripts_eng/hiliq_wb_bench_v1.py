"""P2: HI_LIQ float-mktcap benchmark aligned to solver wb (C.prepare_day): pool=mask in_universe on day (no carry, HARD_EXCLUDE),
mcap = snapshot_asof(available_at<=day), eligible iff >=max(40,L_VOL//2) non-NaN returns in last L_SIGMA rows. Research only; live=false."""
import sys, gc
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "research")); sys.path.insert(0, str(ROOT))
import optimizer_lambda_calib_sealed as C
import optimizer_core_x2_run as R
OUT = ROOT / "output/strategy_optimizer/core_x2"
MINH = max(40, C.L_VOL // 2)

def solver_wb(day):
    """Exact replica of C.prepare_day wb steps (their functions)."""
    pool = C.load_pool(day)
    if len(pool) < 80: return None, pool
    s0 = day - pd.Timedelta(days=int(C.L_SIGMA * 1.8 + 30))
    basic = C.load_daily_basic_window(pool, s0, day)
    snap = C.snapshot_asof(basic, day, pool)
    wb = C.build_wb(snap, pool)
    close = basic.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last")
    close = close.reindex(columns=[c for c in pool if c in close.columns])
    rets = C.returns_from_close(close).tail(C.L_SIGMA)
    cols = [c for c in pool if c in rets.columns and rets[c].notna().sum() >= MINH]
    wb = wb.reindex(cols).fillna(0.0); wb = wb / max(wb.sum(), 1e-12)
    # v0 rule on same day: mask ffill(5) carry, trade_date mcap at day, valid close at day, no history requirement
    return wb, basic

def v0_wb(day, basic, mask):
    d = mask[(mask.date <= day) & (mask.date > day - pd.Timedelta(days=10))]
    ses = sorted(d.date.unique())[-6:]
    names = sorted(set(d[d.date.isin(ses)].instrument.map(C.to_ts)) - set(C.HARD_EXCLUDE))
    b = basic[basic.trade_date.dt.normalize() == day]
    mv = b.set_index("ts_code")["float_mktcap"].astype(float).reindex(names).dropna()
    mv = mv[mv > 0]; return mv / mv.sum()

def main():
    rd = R.rebal_days(R.sessions()); rows = []; W = []
    mask = pq.read_table(C.MASK_PATH, columns=["date", "instrument", "in_universe"], filters=[("in_universe", "=", True)]).to_pandas()
    mask["date"] = pd.to_datetime(mask["date"]).dt.tz_localize(None).dt.normalize()
    for d in rd:
        wb, basic = solver_wb(d)
        if wb is None:
            rows.append(dict(session=d.date(), status="POOL<80")); continue
        basic["trade_date"] = pd.to_datetime(basic["trade_date"]).dt.tz_localize(None)
        # aligned bench, independent build from trade_date panel (mv at last trade_date<=day) + history rule
        pool = C.load_pool(d)
        cl = basic.pivot_table(index="trade_date", columns="ts_code", values="close", aggfunc="last").sort_index()
        mv = basic.pivot_table(index="trade_date", columns="ts_code", values="float_mktcap", aggfunc="last").reindex(cl.index).loc[:d]
        h = cl.loc[:d].pct_change(fill_method=None).tail(C.L_SIGMA).notna().sum()
        el = [c for c in pool if c in h.index and h[c] >= MINH]
        m = mv.ffill().iloc[-1].reindex(el).astype(float); m = m[m > 0].dropna(); bw = m / m.sum()
        v0 = v0_wb(d, basic, mask)
        W.append(pd.DataFrame({"session": d, "instrument": bw.index, "weight": bw.values}))
        S, Bs = set(wb[wb > 0].index), set(bw.index)
        al = pd.concat([bw, wb], axis=1).fillna(0)
        rows.append(dict(session=d.date(), window="SEALED" if d <= pd.Timestamp("2024-05-31") else "X2",
                         max_abs_diff=float((al.iloc[:, 0] - al.iloc[:, 1]).abs().max()), n_bench=len(Bs), n_solver=len(S),
                         symdiff=len(S ^ Bs), n_v0=len(v0), symdiff_v0_vs_solver=len(set(v0.index) ^ S),
                         max_abs_diff_v0_vs_solver=float(pd.concat([v0, wb], axis=1).fillna(0).diff(axis=1).abs().max().max())))
        del basic, cl, mv; gc.collect()
        print(rows[-1], "RSS", C.rss_mb(), flush=True)
    pd.concat(W).to_parquet(OUT / "bench_hiliq_wb_weights.parquet", index=False)
    pd.DataFrame(rows).to_csv(OUT / "bench_vs_solver_wb_diff.csv", index=False)

if __name__ == "__main__":
    main()
