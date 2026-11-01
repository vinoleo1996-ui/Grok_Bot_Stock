"""Alpha 2026-10-18 §8 errata/addendum (Arch N4 + AI recon): sparse event legs — re-report A/A′ for five HI_LIQ legs with
(i) 0/1 held signal vs raw fwd20 (t→t+20) and (ii) style-residualized z (frozen definition) vs neutralized fwd (Alpha ε summed t+2..t+21);
CMC ΔIC under (ii). naive/neff/HAC t disclosure; thresholds unchanged. Read-only; live=false."""
import sys, json, time, numpy as np, pandas as pd
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
import research.alpha_hiliq_s8_paradigm as S8
from research.alpha_combo_marginal import ic_tstats
H = 20; OUT = R/"output/alpha/recon_eqinc"; log = lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True)
def ics(Z, F, minn=50):
    s = {}
    for d in Z.index:
        z, f = Z.loc[d], F.loc[d]; ok = z.notna() & f.notna()
        if ok.sum() >= minn and z[ok].std() > 0: s[d] = z[ok].rank().corr(f[ok].rank())
    return pd.Series(s).dropna()
def pk(s):
    roll = (s.rolling(252).mean()/s.rolling(252).std()).dropna()
    return dict(rank_ic=float(s.mean()), icir_full=float(s.mean()/s.std()), icir_roll252_median=float(roll.median()) if len(roll) else None, n=int(len(s)),
                **{k: v for k, v in ic_tstats(s, H).items() if k.startswith("ic_t_") and k != "ic_t_note"})
t0 = time.time(); c = S8.build(); log("ctx"); E = S8.resid_ret(c); log("E")
F0 = c["F"]; FN = E.shift(-2).rolling(H, min_periods=1).sum().shift(-(H-1))
INU = c["INU"]
Scap = S8.sig(c, S8.CAP); Mcap = (Scap > 0).astype(float)
SL = {k: S8.sig(c, S8.LEGD/f"g1g5_{k}_hiliq_v1_daily_weights_20261014_{st}.parquet") for k, st in S8.LEGS.items()}
ZA = S8.resid_multi(c, {"cap": Scap, **SL}); ZI = S8.resid_multi(c, SL, extra=Scap); log("Z")
Zcap = ZA["cap"]; ICcapN = ics(Zcap, FN)
res = {"cap": {"i_held01_raw": pk(ics((Mcap.where(INU)), F0)), "ii_resid_vs_neutfwd": pk(ICcapN)}}
for k in S8.LEGS:
    M = (SL[k] > 0).astype(float).where(INU)
    # A′(i): 0/1 held orthogonalized to capacity_adv holdings (per-day OLS on intercept + cap 0/1)
    Mo = pd.DataFrame(np.nan, index=M.index, columns=M.columns)
    for d in M.index:
        y = M.loc[d].dropna(); x = Mcap.loc[d, y.index].values
        if len(y) < 50 or y.std() == 0: continue
        X = np.c_[np.ones(len(y)), x]; cf, *_ = np.linalg.lstsq(X, y.values, rcond=None); Mo.loc[d, y.index] = y.values - X@cf
    combo = (0.8*Zcap + 0.2*ZI[k].fillna(0)).where(Zcap.notna()); ICc = ics(combo, FN); ix = ICc.index.intersection(ICcapN.index)
    cc, cp = pk(ICc[ix]), pk(ICcapN[ix]); dIC = ICc[ix]-ICcapN[ix]
    res[k] = dict(i_held01_raw=dict(A=pk(ics(M, F0)), A_prime=pk(ics(Mo, F0))),
                  ii_resid_vs_neutfwd=dict(A=pk(ics(ZA[k], FN)), A_prime=pk(ics(ZI[k], FN)),
                                          cmc=dict(d_ic=float(dIC.mean()), d_icir_full=cc["icir_full"]-cp["icir_full"],
                                                   d_icir_roll=(cc["icir_roll252_median"]-cp["icir_roll252_median"]) if cc["icir_roll252_median"] is not None and cp["icir_roll252_median"] is not None else None,
                                                   d_ic_t=ic_tstats(dIC, H))))
    log(k)
(OUT/"step_c_s8_errata_sparse_ic.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float)); log("done", round(time.time()-t0))
