"""MAINBOOK_V2 A2 sealed-window revalidation (research-only).
Window: 2018-01-01 → 2024-05-31. Forbidden: selection on 2024-06+.
Arm A = EW5 current defaults (Amihud weight 1). Arm B = Amihud weight 0, EW4.
Does NOT mutate P1_DEFAULT_INTEGRATE_WEIGHTS. promotion_approved=false.
"""
from __future__ import annotations
import sys, json, hashlib, time, gc
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Mean of empty slice")

def rankdata(a):
    return pd.Series(a).rank().values

def winsorize_zscore(x, degenerate_fallback="rank"):
    """Aligned with quantlab.factors.engine.winsorize_zscore (Eng Amihud fix)."""
    x = pd.to_numeric(x, errors="coerce")
    med = x.median()
    mad = (x - med).abs().median() * 1.4826
    if mad >= 1e-9:
        return ((x - med) / mad).clip(-4.0, 4.0)
    mad = x.std()
    if np.isfinite(mad) and mad >= 1e-9:
        return ((x - med) / mad).clip(-4.0, 4.0)
    # Eng default: rank fallback (no silent zero)
    if str(degenerate_fallback).lower() == "zero":
        return x * 0.0
    ranks = x.rank(method="average")
    rstd = float(ranks.std()) if ranks.notna().sum() > 1 else float("nan")
    if not np.isfinite(rstd) or rstd < 1e-12:
        return x * 0.0
    return ((ranks - ranks.median()) / rstd).clip(-4.0, 4.0)

T0 = time.time()
S = Path("/workspace/scratch/tic")
V2 = Path("/workspace/QuantLab/data/v2")
OUT = Path("/workspace/QuantLab/output/alpha/MAINBOOK_V2_A2_SEALED")
OUT.mkdir(parents=True, exist_ok=True)
STEP = 5
NNOISE = 50  # cheaper noise bench within sealed window
rng = np.random.default_rng(20261010)
SEAL_START = "2018-01-01"
SEAL_END = "2024-05-31"
# holdout after seal — report only, never for selection
HOLDOUT_START = "2024-06-01"

ld = lambda c: pd.read_parquet(S / f"{c}.parquet").astype("float32")
op, cl, fa = ld("open"), ld("close"), ld("factor")
cols0 = list(cl.columns)
cols = [
    c
    for c in cols0
    if (
        c[:6] in ("sh.600", "sh.601", "sh.603", "sh.605", "sh.688", "sh.689")
        or c[:5] in ("sz.00", "sz.30")
        or c.startswith("bj.")
    )
]
cols = [c for c in cols if not c.startswith("bj.") or c[3] in "489"]
op, cl, fa = op[cols], cl[cols], fa[cols]
amt, tov, ts, lu = (
    ld("amount")[cols],
    ld("turnover")[cols],
    ld("tradestatus")[cols],
    ld("limit_up")[cols],
)
fa = fa.ffill()
aO, aC = op * fa, cl * fa
ret = aC.pct_change(fill_method=None)

raw = {}
raw["R02_20D"] = -(aC / aC.shift(20) - 1)
raw["turn_20d"] = -tov.rolling(20, min_periods=15).mean()
raw["L01_RV60"] = -(ret.rolling(60).std() * np.sqrt(252))
amih = (ret.abs() / amt.replace(0, np.nan)) * 1e9
raw["LIQ02_AMIHUD"] = -amih.rolling(20).mean()  # mainbook sign (negative illiquidity)

val = pd.read_parquet(
    V2 / "valuation/daily_basic_valuation_tushare.parquet",
    columns=["trade_date", "instrument_id", "pb"],
)
pb = val.pivot_table(index="trade_date", columns="instrument_id", values="pb").reindex(
    index=cl.index, columns=cols
)
raw["V02_BP"] = 1 / pb.where(pb > 0)
del val, pb
gc.collect()

# EP side note (PIT daily)
ep = pd.read_parquet(
    V2 / "ep/ep_pit_daily_tushare.parquet", columns=["trade_date", "instrument_id", "ep"]
)
ep_p = ep.pivot_table(index="trade_date", columns="instrument_id", values="ep").reindex(
    index=cl.index, columns=cols
)
raw["V01_EP"] = ep_p.astype("float32")
del ep, ep_p
gc.collect()

fm = pd.read_parquet(
    V2 / "float_mktcap/float_mktcap_daily_tushare.parquet",
    columns=["trade_date", "instrument_id", "float_mktcap"],
)
size = np.log(
    fm.pivot_table(index="trade_date", columns="instrument_id", values="float_mktcap")
    .reindex(index=cl.index, columns=cols)
    .where(lambda x: x > 0)
)
del fm
gc.collect()

FAC = ["R02_20D", "turn_20d", "L01_RV60", "V02_BP", "LIQ02_AMIHUD"]
ARM_A = FAC[:]  # EW5
ARM_B = ["R02_20D", "turn_20d", "L01_RV60", "V02_BP"]  # Amihud=0
SIDE = ["V01_EP"]

mkt = ret.mean(axis=1)
mvol = mkt.rolling(20).std()
cov = ret.rolling(60, min_periods=40).cov(mkt).astype("float32")
var = mkt.rolling(60, min_periods=40).var()
STY = {
    "beta": cov.div(var, axis=0),
    "vol": ret.rolling(60).std(),
    "mom": aC.shift(20) / aC.shift(240) - 1,
    "rev": aC / aC.shift(20) - 1,
    "liq": np.log(tov.rolling(20, min_periods=15).mean()),
}
for _d in (raw, STY):
    for _k in list(_d):
        _d[_k] = _d[_k].astype("float32")
size = size.astype("float32")
del cov, var, amih, amt, fa, ret
gc.collect()

OWN = {
    "R02_20D": ["rev"],
    "L01_RV60": ["vol"],
    "turn_20d": ["liq"],
    "LIQ02_AMIHUD": ["liq"],
    "V02_BP": [],
    "V01_EP": [],
    "ArmA_EW5": [],
    "ArmB_EW4": [],
}

tradable1 = ts.shift(-1).eq(1) & op.shift(-1).notna()
limup1 = (op.shift(-1) >= lu.shift(-1) - 0.005) & lu.shift(-1).notna()
buy_ok = tradable1 & ~limup1
del tradable1, limup1, lu, op
gc.collect()


def labels_at(loc, ids):
    g = lambda F, k: (
        F.iloc[loc + k].reindex(ids).values.astype(float)
        if loc + k < len(F)
        else np.full(len(ids), np.nan)
    )
    o1, c0, c1 = g(aO, 1), g(aC, 0), g(aC, 1)
    return {
        "oo1": g(aO, 2) / o1 - 1,
        "oo5": g(aO, 6) / o1 - 1,
        "oo20": g(aO, 21) / o1 - 1,
        "overnight": o1 / c0 - 1,
        "intraday": c1 / o1 - 1,
        "cc1": c1 / c0 - 1,
    }


TRADABLE_LABELS = {"oo1", "oo5", "oo20", "intraday"}

sw = pd.read_parquet(V2 / "sw_l1_pit/industry_members_sw_l1_tushare.parquet")
sw["out_date"] = sw["out_date"].fillna(pd.Timestamp("2100-01-01"))

all_dates = cl.index[(cl.index >= SEAL_START) & (cl.index <= SEAL_END)]
# need +21 sessions headroom inside index for oo20 label
need = 21
usable = cl.index[: len(cl.index) - need]
dates_seal = all_dates.intersection(usable)[::STEP]
# holdout dates (confirm only)
hold_dates = cl.index[(cl.index >= HOLDOUT_START)].intersection(usable)[::STEP]

print(
    "seal_dates",
    len(dates_seal),
    "hold_dates",
    len(hold_dates),
    "first",
    dates_seal[0].date() if len(dates_seal) else None,
    "last",
    dates_seal[-1].date() if len(dates_seal) else None,
    flush=True,
)


def ind_map(d):
    m = sw[(sw.in_date <= d) & (sw.out_date > d)].drop_duplicates(
        "instrument_id", keep="last"
    )
    return m.set_index("instrument_id")["sw_code"]


def rank_ic(x, y):
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 50:
        return np.nan
    return np.corrcoef(rankdata(x[ok]), rankdata(y[ok]))[0, 1]


def resid(Y, X):
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return Y - X @ b


def zs(v):
    s = np.nanstd(v)
    return (v - np.nanmean(v)) / s if s > 0 else v * 0


rec = []
noise_rec = []
corr_rec = []

ALL_NAMES = FAC + SIDE + ["ArmA_EW5", "ArmB_EW4"]


def run_loop(dates, window_tag):
    for i, d in enumerate(dates):
        loc = cl.index.get_loc(d)
        base = ts.loc[d].eq(1) & cl.loc[d].notna() & size.loc[d].notna()
        im = ind_map(d)
        ids = base[base].index.intersection(im.index)
        if len(ids) < 300:
            continue
        D = pd.get_dummies(im.reindex(ids)).values.astype(float)
        X = np.column_stack([size.loc[d, ids].values, D])
        tercile = size.loc[d, ids].rank(pct=True).values <= 1 / 3

        def neutral(sig):
            z = winsorize_zscore(sig.reindex(ids)).values.astype(float)
            ok = np.isfinite(z)
            out = np.full(len(ids), np.nan)
            if ok.sum() < 300:
                return out
            out[ok] = zs(resid(z[ok], X[ok]))
            return out

        neu = {}
        for f in FAC + SIDE:
            neu[f] = neutral(raw[f].loc[d])
            neu[f + "@lag1"] = neutral(raw[f].iloc[loc - 1])

        # Arm A EW5 / Arm B EW4
        for arm, members, name in (
            (ARM_A, ARM_A, "ArmA_EW5"),
            (ARM_B, ARM_B, "ArmB_EW4"),
        ):
            M = np.column_stack([neu[f] for f in members])
            n = np.isfinite(M).sum(1)
            c = np.where(n >= max(2, len(members) - 1), np.nanmean(M, 1), np.nan)
            neu[name] = zs(c)
            M1 = np.column_stack([neu[f + "@lag1"] for f in members])
            n1 = np.isfinite(M1).sum(1)
            c1 = np.where(
                n1 >= max(2, len(members) - 1), np.nanmean(M1, 1), np.nan
            )
            neu[name + "@lag1"] = zs(c1)

        St = {
            k: winsorize_zscore(v.loc[d].reindex(ids)).values.astype(float)
            for k, v in STY.items()
        }
        bok = buy_ok.loc[d, ids].values
        labs = {}
        for k, y in labels_at(loc, ids).items():
            if k in TRADABLE_LABELS:
                y = np.where(bok, y, np.nan)
            labs[k] = y

        names = FAC + SIDE + ["ArmA_EW5", "ArmB_EW4"]
        for uni, um in (("full", np.ones(len(ids), bool)), ("smallcap", tercile)):
            for f in names:
                x = np.where(um, neu[f], np.nan)
                r = {
                    "date": d,
                    "window": window_tag,
                    "universe": uni,
                    "factor": f,
                    "n": int(np.isfinite(x).sum()),
                }
                for k, y in labs.items():
                    r[k] = rank_ic(x, y)
                r["oo1_lag1"] = rank_ic(
                    np.where(um, neu[f + "@lag1"], np.nan), labs["oo1"]
                )
                r["oo5_lag1"] = rank_ic(
                    np.where(um, neu[f + "@lag1"], np.nan), labs["oo5"]
                )
                # residual IC vs size+ind+styles
                keys = list(STY)
                Z = np.column_stack([X] + [St[k] for k in keys])
                ok = np.isfinite(x) & np.isfinite(Z).all(1)
                xr = np.full(len(ids), np.nan)
                if ok.sum() > 300:
                    xr[ok] = resid(x[ok], Z[ok])
                r["resid_all_oo1"] = rank_ic(xr, labs["oo1"])
                r["resid_all_oo5"] = rank_ic(xr, labs["oo5"])
                # decile on oo5
                y5 = labs["oo5"]
                ok2 = np.isfinite(x) & np.isfinite(y5)
                if ok2.sum() > 100:
                    q = pd.Series(x[ok2]).rank(pct=True).values
                    yy = y5[ok2]
                    r["top_dec_oo5"] = float(yy[q > 0.9].mean())
                    r["bot_dec_oo5"] = float(yy[q <= 0.1].mean())
                    r["univ_oo5"] = float(yy.mean())
                    r["top_dec_lowprice_frac"] = float(
                        (cl.loc[d, ids].values[ok2][q > 0.9] < 3).mean()
                    )
                    r["top_dec_size_pct"] = float(
                        pd.Series(size.loc[d, ids].values[ok2])
                        .rank(pct=True)
                        .values[q > 0.9]
                        .mean()
                    )
                r["mkt_vol20"] = float(mvol.iloc[loc])
                r["mkt_oo5"] = float(np.nanmean(labs["oo5"]))
                rec.append(r)

            # pool corr among FAC only
            M = np.column_stack([np.where(um, neu[f], np.nan) for f in FAC])
            dfm = pd.DataFrame(M, columns=FAC).dropna()
            if len(dfm) > 100:
                corr_rec.append((window_tag, uni, dfm.rank().corr().values))

            # noise (sealed only — cheaper)
            if window_tag == "sealed":
                G = rng.standard_normal((len(ids), NNOISE))
                Gr = resid(G, X)
                Gr = (Gr - Gr.mean(0)) / np.maximum(Gr.std(0), 1e-12)
                for lk, y in (("oo1", labs["oo1"]), ("oo5", labs["oo5"])):
                    ok = um & np.isfinite(y)
                    if ok.sum() < 50:
                        continue
                    ry = rankdata(y[ok])
                    RG = pd.DataFrame(Gr[ok]).rank().values
                    ic = ((RG - RG.mean(0)) * (ry - ry.mean())[:, None]).sum(0) / (
                        RG.std(0) * ry.std() * ok.sum() + 1e-12
                    )
                    noise_rec.append(
                        pd.DataFrame(
                            {
                                "date": d,
                                "universe": uni,
                                "label": lk,
                                "k": np.arange(NNOISE),
                                "ic": ic,
                            }
                        )
                    )

        if i % 40 == 0:
            print(
                window_tag,
                i,
                len(dates),
                d.date(),
                round(time.time() - T0),
                "mem_rec",
                len(rec),
                flush=True,
            )
            gc.collect()


run_loop(dates_seal, "sealed")
run_loop(hold_dates, "holdout_confirm")  # confirm only

R = pd.DataFrame(rec)
R.to_parquet(OUT / "ic_by_date.parquet")
if noise_rec:
    N = pd.concat(noise_rec)
    N.to_parquet(OUT / "noise_ic_by_date.parquet")
else:
    N = pd.DataFrame()

# pool corr mean on sealed full only
C = {}
for uni in ("full", "smallcap"):
    mats = [c for w, u, c in corr_rec if w == "sealed" and u == uni]
    if mats:
        C[uni] = np.nanmean(mats, 0)
json.dump(
    {
        u: pd.DataFrame(C[u], index=FAC, columns=FAC).round(4).to_dict()
        for u in C
    },
    open(OUT / "pool_corr_mean_spearman.json", "w"),
    indent=1,
    ensure_ascii=False,
)

meta = {
    "promotion_approved": False,
    "sealed_window": [SEAL_START, SEAL_END],
    "holdout_confirm": [HOLDOUT_START, "index_end"],
    "step": STEP,
    "n_noise": NNOISE,
    "n_sealed_dates": int(len(dates_seal)),
    "n_holdout_dates": int(len(hold_dates)),
    "arm_a_members": ARM_A,
    "arm_b_members": ARM_B,
    "arm_b_note": "LIQ02_AMIHUD weight forced 0 in research arm only; library defaults untouched",
    "amihud_sign": "mainbook = -|r|/amount (negative illiquidity; NOT flipped)",
    "amihud_scale": "x1e9 before winsorize; winsorize degenerate_fallback=rank (Eng AMIHUD_WINSORIZE_FIX)",
    "labels": "t+1 open→t+2 open primary; also oo5/oo20; overnight/intraday; limit-up at t+1 open unbuyable; suspension excluded",
    "runtime_sec": round(time.time() - T0, 1),
}
json.dump(meta, open(OUT / "run_meta.json", "w"), indent=1, ensure_ascii=False)
print("done", meta["runtime_sec"], "rows", len(R), flush=True)
