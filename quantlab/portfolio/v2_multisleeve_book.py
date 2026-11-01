"""Multi-sleeve portfolio book (Strategy). Research only, strategy_promotion_approved=false.

Mandate (2026-10-12 unified draft): stock basket + ETF ballast are the MAIN book;
CB / gold / futures notional are EXPLICIT CONTRAST arms only.
See docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md.

Default sleeves: core=510300 (1.0). stock / alpha_event reserved at 0 until a
consumable weight long-table is supplied (--stock-path / --alpha-event-path).
marp / cb / xd / gold / e2 / ind_mom: only when explicitly set in --sleeves.

Spot financing: nominal L<=1.0 (no MarginConfig borrowing). --leverage>1 or
--max-gross>1 is weight-scale / futures-overlay research only — NEVER report as
executable spot leverage. Hard refuse above MAX_GROSS=1.5.

AlphaEventSleeve / stock sleeve contract: long table with columns aliases
  session|date|trade_date, instrument_id|instrument|ts_code|code, weight|target_weight.
Missing/empty path → schedule {} and status not_book_consumable (logged).

Engine: run_weight_schedule + ExecConfig.strategy_v1(impact_k=1.0), corporate_actions on,
no_limit_codes={'sh.510300'}, record_weights=True.
"""
from __future__ import annotations
import argparse, hashlib, json, logging, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from quantlab.platform.execution import run_weight_schedule, ExecPanels, ExecConfig  # noqa: E402
from quantlab.platform.futures import (FuturesLeg, FuturesConfig, load_index_futures_panels)  # noqa: E402
FUT_ROOTS = {"IC"}

log = logging.getLogger("mbook")
CORE, CASH_ETF = "sh.510300", "sh.511880"
ETF_CODES = ["510300.SH", "510500.SH", "159915.SZ", "512100.SH", "511010.SH", "518880.SH", "511880.SH"]
WINDOWS = {"X1": ("2015-06-01", "2017-12-29"), "X2": ("2024-06-03", "2026-10-09"), "exploration": ("2024-06-03", "2026-10-09")}
SEALED = ("2018-01-02", "2024-05-31")   # NEVER run (V3_B2X_PREREG / PREREGISTRATION_V2): guarded in main()
WINDOW_LABEL = {"X1": "探索窗 X1 2015-06..2017-12", "X2": "探索窗 X2 2024-06..2026-10-09",
                "exploration": "探索窗 2024-06 起（只作探索）"}
HASH_FILES = ["data/v2/etf/etf_daily_adj.parquet", "data/v2/cb/cb_daily.parquet",
              "data/v2/cb/raw/cb_basic_raw.parquet", "data/v2/cb/raw/cb_share_raw.parquet",
              "data/v2/cb/cb_events_actionable_pit.parquet",
              "data/v2/futures/raw/fut_basic.parquet", "data/v2/futures/raw/index_daily.parquet"]
DEFAULT_SLEEVES = {"core": 1.0, "stock": 0.0, "alpha_event": 0.0}  # Mandate 2026-10-12: ETF ballast; stock/alpha reserved
# Contrast-only (explicit --sleeves): marp / cb / xd / gold / e2 / ind_mom — NOT defaults
# NO-IC historical diag: see v2_multisleeve_book_noic.py (CB+ballast; appendix only under new Mandate)
MAX_GROSS = 1.5          # hard refuse above (futures overlay contrast)
SPOT_MAX_GROSS = 1.0     # Mandate: spot nominal L<=1.0; default --max-gross
IND_MOM_NOTE = "Strategy-built research placeholder (not Beta-sealed); Beta E1/E0 failed ETF_ROTATION_PREREG"
tc = lambda c: ("sh." if c.endswith(".SH") else "sz.") + c[:6]


def sha(p, n=1 << 20):
    h = hashlib.sha256(); f = ROOT / p
    if not f.exists(): return None
    st = f.stat(); h.update(f"{st.st_size}".encode())
    with open(f, "rb") as fh:   # head+tail+size (cheap, stable)
        h.update(fh.read(n)); fh.seek(max(0, st.st_size - n)); h.update(fh.read(n))
    return h.hexdigest()[:16]


class Data:
    def __init__(self, with_cb=True, with_ind_etf=False):
        codes = list(ETF_CODES)
        self.IND_MAP = None
        if with_ind_etf:
            mp = ROOT / "data/v2/etf/sw_l1_etf_map_pit_daily.parquet"
            if mp.exists():
                M = pd.read_parquet(mp)
                M = M[M.etf_ts_code.notna() & (~M.no_etf.fillna(False))]
                ind_codes = sorted(M.etf_ts_code.unique().tolist())
                codes = sorted(set(codes) | set(ind_codes))
                M["date"] = pd.to_datetime(M.trade_date.astype(str)); self.IND_MAP = M
            else:
                log.warning("industry ETF map missing: %s — ind_mom sleeve unavailable", mp)
        E = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", filters=[("ts_code", "in", codes)])
        E["date"] = pd.to_datetime(E.trade_date); E["code"] = E.ts_code.map(tc); self.E = E
        self.HFQ = E.pivot(index="date", columns="code", values="close_hfq")
        self.AMT = E.pivot(index="date", columns="code", values="amount") * 1000  # yuan
        self.CB = self.BAS = None
        if with_cb:
            c = pd.read_parquet(ROOT / "data/v2/cb/cb_daily.parquet", columns=["ts_code", "trade_date", "open", "high", "low",
                                "close", "vol", "amount", "cb_over_rate", "is_placeholder"])
            c = c[(~c.is_placeholder) & c.close.gt(0) & ~c.ts_code.str.startswith(("132", "120"))]
            c["date"] = pd.to_datetime(c.trade_date); c["code"] = c.ts_code.map(tc); self.CB = c
            B = pd.read_parquet(ROOT / "data/v2/cb/raw/cb_basic_raw.parquet"); B["code"] = B.ts_code.map(tc); self.BAS = B

    def fut(self, a, b):
        """IC real CFFEX bars (Eng load_index_futures_panels), cached per window."""
        key = (a, b)
        if getattr(self, "_fut", None) is None: self._fut = {}
        if key not in self._fut:
            self._fut[key] = load_index_futures_panels(("IC",), a, b)
        return self._fut[key]

    def csi500(self):
        if getattr(self, "_c5", None) is None:
            x = pd.read_parquet(ROOT / "data/v2/futures/raw/index_daily.parquet")
            x = x[x.ts_code == "000905.SH"]; self._c5 = x.set_index(pd.to_datetime(x.trade_date.astype(str))).close.sort_index()
        return self._c5

    def cash_ret(self, idx):
        r5 = self.HFQ[CASH_ETF].pct_change().reindex(idx)
        gap = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
        return r5.where(r5.notna(), 0.02 * gap / 365)

    def panels(self, codes, a, b):
        etf = [c for c in codes if c in self.HFQ.columns]; cbc = [c for c in codes if c not in self.HFQ.columns]
        x = self.E[self.E.code.isin(etf) & (self.E.date >= a) & (self.E.date <= b)]
        w = lambda f: x.pivot(index="date", columns="code", values=f)
        parts = dict(close=w("close"), open=w("open"), high=w("high"), low=w("low"), volume=w("vol") * 100,
                     amount=w("amount") * 1000, adj_factor=w("adj_factor"))
        cal = parts["close"].index
        if cbc:
            y = self.CB[self.CB.code.isin(cbc) & (self.CB.date >= a) & (self.CB.date <= b)]
            v = lambda f: y.pivot(index="date", columns="code", values=f).reindex(cal)
            cl = v("close"); term = pd.DataFrame(np.nan, index=cal, columns=cl.columns)
            dl = self.BAS.set_index("code").delist_date.dropna()
            for code in cl.columns:
                if code in dl.index:
                    col = cl[code].dropna()
                    if len(col):
                        pos = cal.searchsorted(col.index[-1], side="right")
                        if pos < len(cal): term.iloc[pos, term.columns.get_loc(code)] = col.iloc[-1]
            cbp = dict(close=cl, open=v("open"), high=v("high"), low=v("low"), volume=v("vol") * 10, amount=v("amount") * 1e4)
            for k, df in cbp.items(): parts[k] = pd.concat([parts[k], df], axis=1)
            parts["adj_factor"] = parts["adj_factor"].reindex(columns=parts["close"].columns)  # CB: NaN -> no CA
            parts["terminal_price"] = term.reindex(columns=parts["close"].columns)
        return ExecPanels(**parts).aligned()

    def returns(self, codes, idx):
        """daily proxy returns: ETFs hfq, CBs raw close (no CA)."""
        out = {}
        for c in codes:
            if c in self.HFQ.columns: out[c] = self.HFQ[c].pct_change()
        cbc = [c for c in codes if c not in out]
        if cbc and self.CB is not None:
            y = self.CB[self.CB.code.isin(cbc)].pivot(index="date", columns="code", values="close")
            for c in cbc: out[c] = y[c].pct_change(fill_method=None)
        return pd.DataFrame(out).reindex(idx).fillna(0.0)


def month_ends(idx):
    """Last session of each month in idx. The final month counts only if its last session is the last weekday of
    the calendar month (so a forward run never treats a partial month's latest session as a month-end)."""
    s = pd.Series(idx, index=idx); m = list(s.groupby(s.dt.to_period("M")).max())
    if m:
        t = m[-1]; rest = pd.bdate_range(t + pd.Timedelta(days=1), t + pd.offsets.MonthEnd(0))
        if len(rest): m = m[:-1]
    return m


# ----------------------------------------------------------------- sleeves
def sleeve_core(D, idx, **_): return {idx[0]: {CORE: 1.0}}

def sleeve_static(D, idx, weights, monthly=True, **_):
    return {t: dict(weights) for t in ([idx[0]] + month_ends(idx) if monthly else [idx[0]])}

def sleeve_marp(D, idx, **_):
    rr = D.HFQ[[CORE, "sh.511010", "sh.518880"]].pct_change(); S = {}
    for t in [idx[0]] + month_ends(idx):
        iv = 1 / rr.loc[:t].tail(60).std(); S[t] = (iv / iv.sum()).to_dict()
    return S

def sleeve_e2(D, idx, pool=("sh.510300", "sh.510500", "sz.159915"), **_):
    S = {}
    for t in idx[::20]:
        h = D.HFQ.loc[:t, list(pool)]; m = (h.iloc[-1] / h.iloc[-21] - 1).dropna()
        m = m[[c for c in m.index if h[c].notna().sum() >= 21]]; tgt = {c: 0.0 for c in pool}
        if len(m) and m.max() > 0: tgt[m.idxmax()] = 1.0
        S[t] = tgt
    return S

def sleeve_ind_mom(D, idx, top_n=3, lookback=20, min_adv=2e7, min_listed=60, **_):
    """Strategy-built research placeholder: rotate among liquid industry ETFs by lookback-day momentum.
    NOT Beta-sealed (Beta E1/E0 failed ETF_ROTATION_PREREG; no industry handoff in handoff_strategy/).
    Cash fallback when best momentum <= 0. Uses sw_l1_etf_map_pit_daily for the universe."""
    if D.IND_MAP is None:
        log.warning("ind_mom: no IND_MAP loaded; returning empty schedule")
        return {}
    S, diag = {}, []
    for t in idx[::lookback]:
        day = D.IND_MAP[D.IND_MAP.date == t]
        if day.empty:
            # nearest prior map date
            prior = D.IND_MAP[D.IND_MAP.date <= t]
            if prior.empty: S[t] = {}; continue
            day = prior[prior.date == prior.date.max()]
        day = day[day.etf_ts_code.notna() & (~day.no_etf.fillna(False))]
        if "amt20" in day.columns:
            day = day[day.amt20.fillna(0) >= (min_adv / 1e4)]  # map amt20 in 万元
        codes = sorted({tc(c) for c in day.etf_ts_code.unique() if tc(c) in D.HFQ.columns})
        elig = []
        for c in codes:
            h = D.HFQ[c].loc[:t].dropna()
            if len(h) < min_listed: continue
            if len(h) < lookback + 1: continue
            # ADV check from amount panel if map amt20 missing
            if "amt20" not in day.columns or day[day.etf_ts_code.map(tc) == c].empty:
                adv = D.AMT[c].loc[:t].tail(20).mean() if c in D.AMT.columns else 0
                if not np.isfinite(adv) or adv < min_adv: continue
            mom = h.iloc[-1] / h.iloc[-(lookback + 1)] - 1
            if np.isfinite(mom): elig.append((mom, c))
        elig.sort(reverse=True)
        picks = [(m, c) for m, c in elig[:top_n] if m > 0]
        if picks:
            w = 1.0 / len(picks); S[t] = {c: w for _, c in picks}
        else:
            S[t] = {}  # cash via parking
        diag.append(dict(session=str(t.date()), n_elig=len(elig), n_picks=len(picks),
                         top=[(round(float(m), 4), c) for m, c in elig[:top_n]]))
    sleeve_ind_mom.last_diag = diag
    return S

def sleeve_cb(D, idx, mode="CB1", n=20, full_rules=True, **_):
    """CB1 double-low (or CBLIQ control). full_rules=True matches Beta FULLCB=1 / CB_PREREG §12:
    remain_size as-of >= 1e8 (cb_share_raw) and exclude bonds with 强制赎回 subtype in
    {公告实施强赎, 公告提示强赎} once available_at.date() < T (cb_events_actionable_pit)."""
    x = D.CB[(D.CB.date >= idx[0] - pd.Timedelta(days=60)) & (D.CB.date <= idx[-1])]
    adv = x.pivot(index="date", columns="code", values="amount").mul(1e4).rolling(20, min_periods=20).mean()
    cl = x.pivot(index="date", columns="code", values="close"); pr = x.pivot(index="date", columns="code", values="cb_over_rate")
    mat = pd.to_datetime(D.BAS.set_index("code").maturity_date, errors="coerce")
    EXCL = pd.Series(dtype="datetime64[ns]"); rs_idx = {}
    n_sz = n_fr = 0
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
        if t not in cl.index: continue
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
            sz_ok = pd.Series(sz) >= 1e8
            n_sz += int((ok & ~sz_ok).sum()); ok &= sz_ok
            ex = EXCL.reindex(ok.index)
            fr_hit = ex.notna() & (ex.dt.normalize() < pd.Timestamp(t).normalize())
            n_fr += int((ok & fr_hit).sum()); ok &= ~fr_hit
        el = ok[ok].index
        if mode == "CB1": pick = (cl.loc[t, el] + pr.loc[t, el]).nsmallest(n).index
        elif mode == "CBLIQ": pick = adv.loc[t, el].nlargest(n).index   # no-signal control: most liquid n
        else: pick = el
        S[t] = {c: 1 / len(pick) for c in pick} if len(pick) else {}
    sleeve_cb.last_diag = dict(full_rules=bool(full_rules), size_exclusions_daybond=int(n_sz),
                               fr_exclusions_daybond=int(n_fr), n_signals=len(S),
                               avg_names=float(np.mean([len(v) for v in S.values()])) if S else 0.0,
                               min_names=int(min((len(v) for v in S.values()), default=0)))
    return S

def _ic_candidates(F, idx, i):
    """Beta b2x_run.cands: quarterly IC contracts with a settle today and >5 sessions to last trade, nearest first."""
    S = F.settle.reindex(idx); out = []
    for c in S.columns:
        if int(c[-2:]) % 3 != 0 or not np.isfinite(S.iat[i, S.columns.get_loc(c)]): continue
        e = pd.Timestamp(F.expiry[c]); k = idx.searchsorted(e) if e <= idx[-1] else i + 10 ** 6
        if k - i > 5: out.append((e, c))
    return [c for _, c in sorted(out)[:2]]

def ic_discount(D, F, idx, i):
    """annualized basis b = (S-F)/S * 365/calendar days to last trade (Beta V3_B2X_PREREG X-D); F=settle, S=CSI500 close."""
    cs = _ic_candidates(F, idx, i)
    if not cs: return np.nan, None
    c = cs[0]; t = idx[i]; Fv = F.settle.reindex(idx).iat[i, F.settle.columns.get_loc(c)]
    s = D.csi500().get(t, np.nan); d = (pd.Timestamp(F.expiry[c]) - t).days
    return (s - Fv) / s * 365 / max(d, 1), c

def sleeve_xd(D, idx, F=None, thresh=0.05, **_):
    """X-D: month-end IC quarterly notional 1.0 if annualized discount >= 5% else 0.5; rest of the sleeve = cash collateral.
    Weights are futures NOTIONAL / NAV (engine futures leg); sleeve capital stays as cash (margin + VM pool)."""
    S, diag = {}, []
    for t in [idx[0]] + month_ends(idx):
        i = idx.get_loc(t); b, c = ic_discount(D, F, idx, i)
        w = 1.0 if (np.isfinite(b) and b >= thresh) else 0.5
        S[t] = {"IC": w}; diag.append((str(t.date()), c, None if not np.isfinite(b) else round(float(b), 5), w))
    sleeve_xd.last_diag = diag
    return S

def sleeve_ic_static(D, idx, w=0.75, **_):
    return {t: {"IC": w} for t in [idx[0]] + month_ends(idx)}


def _normalize_instrument_id(x: str) -> str:
    """Map ts_code / bare code / ql code to engine style sh.600000 / sz.000001."""
    s = str(x).strip()
    if not s or s.lower() in ("nan", "none"):
        return s
    if s.startswith(("sh.", "sz.", "bj.")):
        return s
    if "." in s:
        a, b = s.split(".", 1)
        if b.upper() in ("SH", "SZ", "BJ") and a.isdigit():
            return {"SH": "sh.", "SZ": "sz.", "BJ": "bj."}[b.upper()] + a
        if a.lower() in ("sh", "sz", "bj") and b.isdigit():
            return a.lower() + "." + b
    if s.isdigit() and len(s) == 6:
        return ("sh." if s.startswith(("5", "6", "9")) else "sz.") + s
    return s


class WeightLongTableSleeve:
    """Consumes a date/instrument/weight long table for stock or alpha_event sleeves.

    Column aliases:
      session <- session|date|trade_date
      instrument_id <- instrument_id|instrument|ts_code|code
      weight <- weight|target_weight
    Empty/missing/unreadable → {} and status not_book_consumable.
    """
    SESSION_ALIASES = ("session", "date", "trade_date")
    INST_ALIASES = ("instrument_id", "instrument", "ts_code", "code")
    W_ALIASES = ("weight", "target_weight")

    def __init__(self, path=None, *, name="alpha_event"):
        self.path = path
        self.name = name
        self.status = "not_book_consumable"
        self.n_rows = 0
        self.n_sessions = 0
        self.error = None

    def _load(self) -> pd.DataFrame:
        if not self.path:
            self.status, self.error = "not_book_consumable", "no_path"
            return pd.DataFrame()
        p = Path(self.path) if not isinstance(self.path, Path) else self.path
        if not p.is_absolute():
            p = ROOT / p
        if not p.exists():
            self.status, self.error = "not_book_consumable", f"missing:{p}"
            log.warning("%s sleeve: path missing → not_book_consumable (%s)", self.name, p)
            return pd.DataFrame()
        try:
            df = pd.read_parquet(p) if p.suffix.lower() in (".parquet", ".pq") else pd.read_csv(p)
        except Exception as e:
            self.status, self.error = "not_book_consumable", f"read_error:{e}"
            log.warning("%s sleeve: read failed → not_book_consumable (%s)", self.name, e)
            return pd.DataFrame()
        colmap = {}
        cols = {c.lower(): c for c in df.columns}
        for canon, aliases in (("session", self.SESSION_ALIASES),
                               ("instrument_id", self.INST_ALIASES),
                               ("weight", self.W_ALIASES)):
            hit = next((cols[a] for a in aliases if a in cols), None)
            if hit is None:
                self.status, self.error = "not_book_consumable", f"missing_col:{canon}"
                log.warning("%s sleeve: missing column %s (aliases=%s) → not_book_consumable",
                            self.name, canon, aliases)
                return pd.DataFrame()
            colmap[hit] = canon
        df = df.rename(columns=colmap)[["session", "instrument_id", "weight"]].copy()
        df["session"] = pd.to_datetime(df["session"].astype(str))
        df["instrument_id"] = df["instrument_id"].map(_normalize_instrument_id)
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
        df = df.dropna(subset=["session", "instrument_id", "weight"])
        df = df[df["weight"] > 0]
        self.n_rows = int(len(df))
        if self.n_rows == 0:
            self.status, self.error = "not_book_consumable", "zero_rows"
            log.warning("%s sleeve: zero positive-weight rows → not_book_consumable", self.name)
            return df
        self.status = "book_consumable"
        self.error = None
        return df

    def schedule(self, D, idx, **_):
        df = self._load()
        if df.empty:
            return {}
        # keep sessions inside book index (carry is handled by combine)
        lo, hi = idx[0], idx[-1]
        df = df[(df.session >= lo) & (df.session <= hi)]
        if df.empty:
            self.status, self.error = "not_book_consumable", "no_rows_in_window"
            log.warning("%s sleeve: no rows in window %s..%s → not_book_consumable",
                        self.name, lo.date(), hi.date())
            return {}
        out = {}
        for t, g in df.groupby("session"):
            # last row wins on duplicate instrument
            out[pd.Timestamp(t)] = g.groupby("instrument_id")["weight"].sum().to_dict()
        self.n_sessions = len(out)
        self.status = "book_consumable"
        log.info("%s sleeve: book_consumable rows=%d sessions=%d path=%s",
                 self.name, self.n_rows, self.n_sessions, self.path)
        return out


# backward-compatible name
class AlphaEventSleeve(WeightLongTableSleeve):
    def __init__(self, path=None):
        super().__init__(path, name="alpha_event")


# ----------------------------------------------------------------- book
def combine(sleeve_sched, sleeve_w, idx, *, collateral_frac=1.0, cash_target=0.02, target_vol=None, vol_lookback=60, leverage=1.0,
            max_gross=MAX_GROSS, per_sleeve_vol=None, D=None, scale_dates=None):
    """sleeve_sched {name: schedule}; returns (final schedule, sleeve-level weights frame, diagnostics).
    Caps spot+|futures notional| at max_gross (default 1.5) by scaling futures first, then the whole book."""
    days = sorted(set().union(*[set(s) for s in sleeve_sched.values() if s]) | {idx[0]} | set(scale_dates or []))
    days = [d for d in days if idx[0] <= d <= idx[-1]]
    cur = {k: {} for k in sleeve_sched}; final, rows, scales = {}, [], []
    allc = sorted((set().union(*[set(w) for s in sleeve_sched.values() for w in s.values()]) | {CASH_ETF}) - FUT_ROOTS)
    R = D.returns(allc, D.HFQ.index) if (target_vol or per_sleeve_vol) else None
    for t in days:
        for k, s in sleeve_sched.items():
            if t in s: cur[k] = {c: w for c, w in s[t].items() if w > 0}
        book, row = {}, {"session": t}
        for k, w in sleeve_w.items():
            sw = cur.get(k, {}); f = 1.0
            if per_sleeve_vol and sw and R is not None and not (set(sw) & FUT_ROOTS):   # down-only per-sleeve vol scaling
                r = (R.loc[:t, list(sw)].tail(vol_lookback) * pd.Series(sw)).sum(axis=1)
                v = r.std() * np.sqrt(244); tv = per_sleeve_vol.get(k)
                if tv and v > 0: f = min(1.0, tv / v)
            for c, x in sw.items(): book[c] = book.get(c, 0) + w * x * f
            row[k] = w * sum(sw.values()) * f
        # vol target on the risky book (excluding parking)
        sc = 1.0
        if target_vol and R is not None and book and not (set(book) & FUT_ROOTS):
            r = (R.loc[:t, list(book)].tail(vol_lookback) * pd.Series(book)).sum(axis=1)
            v = r.std() * np.sqrt(244)
            if v > 0: sc = min(leverage, target_vol / v)
        else:
            sc = leverage
        book = {c: x * sc for c, x in book.items()}
        fut_notional = sum(abs(x) for c, x in book.items() if c in FUT_ROOTS)
        # Cap gross = spot + |fut notional| at max_gross: scale futures first, then whole book if still over.
        inv0 = sum(x for c, x in book.items() if c not in FUT_ROOTS)
        gross0 = inv0 + fut_notional
        if max_gross is not None and gross0 > max_gross + 1e-12:
            if fut_notional > 1e-12 and inv0 < max_gross:
                fscale = (max_gross - inv0) / fut_notional
                for c in list(book):
                    if c in FUT_ROOTS: book[c] *= fscale
                fut_notional *= fscale
            else:
                gscale = max_gross / gross0
                book = {c: x * gscale for c, x in book.items()}
                fut_notional *= gscale
                sc *= gscale
        # futures sleeves keep their whole capital as cash (margin + daily VM pool): not parked in 511880
        collateral = collateral_frac * sum(w for k, w in sleeve_w.items() if any(c in FUT_ROOTS for c in cur.get(k, {})))
        inv = sum(x for c, x in book.items() if c not in FUT_ROOTS)
        park = max(0.0, (1 - cash_target - collateral) - inv)
        if park > 1e-9: book[CASH_ETF] = book.get(CASH_ETF, 0) + park
        spot = inv + park
        row.update(scale=sc, invested_ex_parking=inv, parking_511880=park, futures_collateral_cash=collateral,
                   futures_notional=fut_notional, gross_exposure=spot + fut_notional, max_gross=max_gross,
                   idle_cash_target=max(0.0, 1 - spot - collateral))
        rows.append(row); final[t] = book; scales.append(sc)
    return final, pd.DataFrame(rows).set_index("session"), dict(scale_mean=float(np.mean(scales)))


def metrics(nav):
    from quantlab import metrics as QM   # single source of truth (244-day annualisation)
    nav = pd.Series(nav).dropna(); r = nav.pct_change().dropna(); cg = QM.cagr(nav); md = QM.mdd(nav)
    return dict(cagr=cg, mdd=md, sharpe=QM.sharpe(r), vol=QM.vol(r), calmar=QM.calmar(cg, md),
                total_return=float(nav.iloc[-1] / nav.iloc[0] - 1), start=str(nav.index[0])[:10], end=str(nav.index[-1])[:10])


def exec_cfg(D, idx, **ov):
    return ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=ov.pop("min_trade_value", 2000),
                                  cash_rate=D.cash_ret(idx), cash_rate_kind="return",
                                  no_limit_codes=frozenset({CORE}), corporate_actions=True, **ov)


def futures_leg(D, a, b):
    F = D.fut(a, b)
    return FuturesLeg(F, FuturesConfig(roll_mode="roll", roll_days=5, contract_months="quarterly", slippage_ticks=1.0))


def run_book(D, sched, a, b, outdir, *, initial_cash=5e6, sleeve_frame=None, meta=None, write=True, record_fills=False):
    codes = sorted((set().union(*[set(v) for v in sched.values()]) | {CORE}) - FUT_ROOTS)
    has_fut = any(c in FUT_ROOTS for v in sched.values() for c in v)
    # WeightLongTableSleeve may name stocks / extra ETFs outside Data.HFQ (default 7 ETFs).
    # Fall back to platform load_execution_panels (D0+asof / fund / CB) so stock path is book-consumable.
    need_merged = [c for c in codes if c not in getattr(D, "HFQ", pd.DataFrame()).columns]
    if need_merged:
        from quantlab.platform.execution import load_execution_panels
        p, _diag = load_execution_panels(codes, a, b, corporate_actions=True)
        log.info("run_book: load_execution_panels for %d codes (%d outside HFQ)", len(codes), len(need_merged))
    else:
        p = D.panels(codes, a, b)
    idx = p.close.index
    sched = {(t if t in idx else idx[idx.searchsorted(t)]): w for t, w in sched.items() if t <= idx[-1]}
    cfg = exec_cfg(D, idx)
    leg = futures_leg(D, a, b) if has_fut else None
    if leg is not None:
        log.warning("FUTURES LEG ON: IC notional rides on the shared cash/collateral pool -> book gross exposure "
                    "(spot + |futures notional|) can exceed 1.0 (research only, not Mandate-approved)")
    r = run_weight_schedule(p, sched, initial_cash=initial_cash, config=cfg, record_weights=True,
                            record_fills=record_fills, futures=leg)
    nav = r["nav"]; m = metrics(nav); costs = {k: float(v) for k, v in r["costs"].items()}
    aw = r["actual_weights"]; idle = 1 - aw.sum(axis=1)
    def _ser(x):
        if leg is None or x is None: return pd.Series(0.0, index=nav.index)
        a_ = np.asarray(x.values if hasattr(x, "values") else x, dtype=float)
        if a_.ndim == 2: a_ = np.nansum(np.abs(a_), axis=1)
        return pd.Series(a_, index=nav.index)
    fexp = _ser(r.get("fut_exposure")); fmargin = _ser(r.get("margin"))
    gross = aw.sum(axis=1) + fexp.abs()
    m.update(fut_exposure_mean=float(fexp.abs().iloc[1:].mean()), gross_exposure_mean=float(gross.iloc[1:].mean()),
             gross_exposure_max=float(gross.max()), fut_total_fees=float(r.get("fut_total_fees") or 0),
             fut_n_rolls=r.get("n_rolls"), fut_margin_peak=float(r.get("margin_peak") or 0),
             fut_shortfall_events=sum(1 for e in r["events"] if "shortfall" in str(e)),
             cash_ex_margin_mean=float((idle - fmargin / nav).iloc[1:].mean()))
    m["_raw"] = r
    m.update(costs=costs, total_cost=float(r["total_cost"]), cost_pct_initial=float(r["total_cost"]) / initial_cash,
             fill_ratio=float(r["fill_ratio"]), cash_interest=float(r.get("cash_interest") or 0),
             idle_cash_mean=float(idle.iloc[1:].mean()), idle_cash_p95=float(idle.iloc[1:].quantile(.95)),
             gross_mean=float(aw.sum(axis=1).iloc[1:].mean()), n_signals=len(sched),
             corporate_action_cash=float(r.get("corporate_action_cash") or 0), n_codes=len(codes))
    if write:
        outdir.mkdir(parents=True, exist_ok=True)
        def long(df):
            s = df.stack(); s = s[s.abs() > 1e-7]
            return s.rename("weight").rename_axis(["session", "instrument_id"]).reset_index()
        long(r["target_weights"]).to_parquet(outdir / "target_weights.parquet", index=False)
        long(aw).to_parquet(outdir / "actual_weights.parquet", index=False)
        pd.DataFrame({"nav": nav, "nav_open": r["nav_open"], "cash_incl_collateral": idle, "fut_exposure": fexp,
                      "fut_margin_frac": fmargin / nav, "gross_exposure": gross}).to_csv(outdir / "nav.csv")
        if sleeve_frame is not None: sleeve_frame.to_csv(outdir / "sleeve_weights.csv")
        json.dump(dict(metrics={k: v for k, v in m.items() if k != "_raw"}, **(meta or {})), open(outdir / "summary.json", "w"), indent=1, default=str)
    return m


def build_sleeves(D, idx, a, b, args, static=False):
    """{sleeve: schedule}; only sleeves with weight>0 and data available. Returns (sleeves, notes)."""
    sw = json.loads(args.sleeves) if isinstance(args.sleeves, str) else args.sleeves
    notes, ss = {}, {}
    for k, w in sw.items():
        if w <= 0 and k not in ("alpha_event", "stock"): continue
        if k == "core": ss[k] = sleeve_core(D, idx)
        elif k == "marp": ss[k] = sleeve_static(D, idx, {CORE: .4, "sh.511010": .4, "sh.518880": .2}) if static else sleeve_marp(D, idx)
        elif k == "e2": ss[k] = sleeve_e2(D, idx, pool=tuple(args.e2_pool.split(",")))
        elif k == "cb":
            full = bool(getattr(args, "cb_full_rules", True))
            sc = sleeve_cb(D, idx, mode="CBLIQ" if static else "CB1", full_rules=full)
            dg = getattr(sleeve_cb, "last_diag", {})
            nn = [len(v) for v in sc.values()]
            notes["cb"] = dict(avg_names=float(np.mean(nn)) if nn else 0, min_names=int(min(nn)) if nn else 0,
                               empty_signals=int(sum(1 for x in nn if x == 0)),
                               full_rules=full,
                               size_exclusions_daybond=dg.get("size_exclusions_daybond"),
                               fr_exclusions_daybond=dg.get("fr_exclusions_daybond"),
                               rule=("CBLIQ static control" if static else
                                     ("CB1 full-rules (Beta FULLCB=1 / CB_PREREG §12)" if full else
                                      "CB1 degraded (no size/FR filters)")))
            ss[k] = sc
        elif k == "xd":
            F = D.fut(a, b)
            if static:
                ss[k] = sleeve_ic_static(D, idx, w=float(args.static_ic))
            else:
                ss[k] = sleeve_xd(D, idx, F=F); dg = sleeve_xd.last_diag
                notes["xd"] = dict(frac_full=float(np.mean([x[3] == 1.0 for x in dg])), n_signals=len(dg), signals=dg)
        elif k == "ind_mom":
            sc = sleeve_ind_mom(D, idx)
            dg = getattr(sleeve_ind_mom, "last_diag", [])
            notes["ind_mom"] = dict(label=IND_MOM_NOTE, n_signals=len(dg),
                                    avg_elig=float(np.mean([d["n_elig"] for d in dg])) if dg else 0,
                                    avg_picks=float(np.mean([d["n_picks"] for d in dg])) if dg else 0)
            ss[k] = sc
        elif k in ("alpha_event", "stock"):
            path = getattr(args, "stock_path", None) if k == "stock" else getattr(args, "alpha_event_path", None)
            # stock may fall back to alpha_event_path if stock_path unset
            if k == "stock" and not path:
                path = getattr(args, "alpha_event_path", None)
            sleeve = WeightLongTableSleeve(path, name=k)
            sched = sleeve.schedule(D, idx)
            notes[k] = dict(status=sleeve.status, n_rows=sleeve.n_rows, n_sessions=sleeve.n_sessions,
                            path=str(path) if path else None, error=sleeve.error,
                            not_book_consumable=(sleeve.status != "book_consumable"))
            if w > 0 and sleeve.status != "book_consumable":
                log.warning("sleeve %s budget=%.3f but %s — book will park that budget in 511880",
                            k, w, sleeve.status)
            ss[k] = sched
        elif k == "gold":
            ss[k] = sleeve_static(D, idx, {"sh.518880": 1.0})
    return ss, sw, notes


def arm_schedules(arm, D, idx, sleeve_w, args, a=None, b=None):
    if arm == "C0": return {idx[0]: {CORE: 1.0}}, None, "510300 买入持有", {}
    if arm == "C1":
        w = {c: 1 / 3 for c in ("sh.510300", "sh.510500", "sz.159915")}
        return sleeve_static(D, idx, w), None, "宽基等权 510300/510500/159915 月度", {}
    if arm.startswith("SA_"):   # one sleeve standalone (its capital = 100%)
        k = arm[3:]; one = dict(args.__dict__); one["sleeves"] = {k: 1.0}
        ss, sw, notes = build_sleeves(D, idx, a, b, argparse.Namespace(**one))
        f, sf, _ = combine(ss, sw, idx, cash_target=args.cash_target, max_gross=getattr(args, "max_gross", MAX_GROSS), D=D)
        return f, sf, f"单袖套 {k}（100%）" + (f" [{IND_MOM_NOTE}]" if k == "ind_mom" else ""), notes
    if arm in ("BOOK", "STATIC"):
        ss, sw, notes = build_sleeves(D, idx, a, b, args, static=(arm == "STATIC"))
        mg = getattr(args, "max_gross", MAX_GROSS)
        f, sf, _ = combine(ss, sw, idx, collateral_frac=args.collateral_frac, cash_target=args.cash_target, target_vol=args.target_vol if arm == "BOOK" else None,
                           leverage=args.leverage if arm == "BOOK" else 1.0, max_gross=mg, D=D,
                           scale_dates=month_ends(idx) if (arm == "BOOK" and args.target_vol) else None)
        # Mandate 2026-10-12: describe from actual sleeve keys present
        keys = [k for k, w in sw.items() if w > 0]
        if arm == "BOOK":
            if set(keys) <= {"core", "stock", "alpha_event"} or keys == ["core"]:
                desc = "主书（Mandate）：宽基 ETF 压舱 + 预留 stock/alpha_event；现货名义 L≤1.0"
            else:
                desc = f"多袖套账本（含对照袖套 {keys}）；现货名义 L≤1.0；>1 仅权重缩放/期货对照"
        else:
            desc = f"静态对照袖套 {keys}"
        return f, sf, desc, notes
    raise ValueError(arm)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arms", default="BOOK,C0", help="default BOOK+C0 under Mandate; pass SA_cb/SA_xd etc for contrast only")
    ap.add_argument("--windows", default="X1,X2")
    ap.add_argument("--collateral-frac", type=float, default=1.0,
                    help="share of the futures sleeve's capital kept as cash collateral (rest parked in 511880); <1 = overlay, gross>1")
    ap.add_argument("--static-ic", type=float, default=0.75, help="STATIC arm constant IC notional (X-D midpoint 0.5/1.0)")
    ap.add_argument("--sleeves", default=json.dumps(DEFAULT_SLEEVES), help="JSON sleeve weights")
    ap.add_argument("--target-vol", type=float, default=None, help="annual vol target for the book (off by default)")
    ap.add_argument("--leverage", type=float, default=1.0,
                    help="book scale cap; 1.0=unlevered. Hard-refused above MAX_GROSS=1.5 (Leo: no high-lev FUT-RP in book)")
    ap.add_argument("--max-gross", type=float, default=SPOT_MAX_GROSS,
                    help="cap on spot+|futures notional|; Mandate default 1.0 (spot); hard refuse above 1.5")
    ap.add_argument("--e2-pool", default="sh.510300,sh.510500,sz.159915", help="512100 (CSI1000) excluded: no-smallcap rule")
    ap.add_argument("--alpha-event-path", default=None,
                    help="long table parquet/csv for alpha_event sleeve (session,instrument,weight)")
    ap.add_argument("--stock-path", default=None,
                    help="long table parquet/csv for stock sleeve; falls back to --alpha-event-path if unset")
    ap.add_argument("--cb-full-rules", dest="cb_full_rules", action="store_true", default=True,
                    help="CB1 full rules: remain_size>=1e8 + forced-redemption PIT exclude (default on)")
    ap.add_argument("--cb-degraded", dest="cb_full_rules", action="store_false",
                    help="CB1 without size/FR filters (legacy degraded sleeve)")
    ap.add_argument("--cash-target", type=float, default=0.02, help="planned idle cash; hard limit 5%%")
    ap.add_argument("--initial-cash", type=float, default=5e6)
    ap.add_argument("--start", default=None); ap.add_argument("--end", default=None)
    ap.add_argument("--out", default="output/strategy_mbook")
    ap.add_argument("--no-ic", action="store_true",
                    help="refuse here; use quantlab.portfolio.v2_multisleeve_book_noic for AUM 60万/100万 NO-IC diagnostic book")
    ap.add_argument("--capital", type=float, default=None,
                    help="for NO-IC AUM policy see v2_multisleeve_book_noic (--capital 600000|1000000); 5M=appendix only")
    a = ap.parse_args(argv)
    if a.no_ic or (a.capital is not None and abs(float(a.capital) - 5e6) > 1 and "xd" in a.sleeves):
        raise SystemExit(
            "NO-IC / Leo AUM-60万·100万 book lives in quantlab.portfolio.v2_multisleeve_book_noic "
            "(--capital 600000|1000000; 5M appendix only). This module still embeds X-D/IC; do not mix.")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    sleeve_w = json.loads(a.sleeves)
    if "smallcap" in a.sleeves: raise SystemExit("smallcap sleeve forbidden (Leo)")
    if a.leverage > MAX_GROSS + 1e-12:
        raise SystemExit(f"--leverage {a.leverage} > MAX_GROSS={MAX_GROSS}: refused (Leo: unlevered or L<=1.5 only; FUT-RP on hold)")
    if a.max_gross > MAX_GROSS + 1e-12:
        raise SystemExit(f"--max-gross {a.max_gross} > MAX_GROSS={MAX_GROSS}: refused")
    if a.leverage > 1.0 + 1e-12 or a.max_gross > SPOT_MAX_GROSS + 1e-12:
        log.warning(
            "LEVERAGE/max_gross=%.2f/%.2f > spot L=1.0: NOT executable spot financing "
            "(no MarginConfig borrowing); mark as weight-scale / futures-overlay contrast only",
            a.leverage, a.max_gross)
    need_ind = ("ind_mom" in a.sleeves) or any(x.strip() == "SA_ind_mom" for x in a.arms.split(","))
    D = Data(with_cb=True, with_ind_etf=need_ind)
    hashes = {f: sha(f) for f in HASH_FILES}
    out = Path(ROOT / a.out); table = {}
    wins = {w: WINDOWS[w] for w in a.windows.split(",")} if not a.start else {"custom": (a.start, a.end)}
    for wn, (s, e) in wins.items():   # seal guard: any overlap with 2018-01-02..2024-05-31 is refused
        if pd.Timestamp(s) <= pd.Timestamp(SEALED[1]) and pd.Timestamp(e) >= pd.Timestamp(SEALED[0]):
            raise SystemExit(f"window {wn} {s}..{e} overlaps the SEALED window {SEALED}; refused")
    for wn, (s, e) in wins.items():
        idx = D.HFQ.loc[s:e].index
        for arm in a.arms.split(","):
            t0 = time.time()
            sched, sf, desc, notes = arm_schedules(arm, D, idx, sleeve_w, a, s, e)
            meta = dict(arm=arm, description=desc, window=wn, window_label=WINDOW_LABEL.get(wn, "custom（探索）"),
                        window_dates=[s, e], research_only=True, promotion_approved=False, smallcap=False,
                        sleeve_weights=sleeve_w if arm not in ("C0", "C1") else None,
                        target_vol=a.target_vol, leverage=a.leverage,
                        leverage_note=(f"scale={a.leverage}, max_gross={a.max_gross}; futures cash-collateral only, no MarginConfig borrowing; "
                                       f"hard cap {MAX_GROSS}") if a.leverage != 1.0 or a.max_gross != 1.0 else f"unlevered (1.0), max_gross={a.max_gross}",
                        max_gross=a.max_gross,
                        return_basis="engine total-return: raw OHLC fills + corporate_actions=True (ETF cash div / adj_factor fallback); "
                                     "CB raw price + terminal redemption payout; idle cash earns 511880 per-session return",
                        engine="run_weight_schedule + ExecConfig.strategy_v1(impact_k=1.0, min_trade_value=2000, "
                               "no_limit_codes={'sh.510300'}, cb_commission=1bp/min ¥1)",
                        data_hashes=hashes, initial_cash=a.initial_cash, cash_target=a.cash_target, idle_cash_limit=0.05,
                        strategy_promotion_approved=False,
                        dataset_promotion_note="see Eng ping / V2 roots; do not conflate with strategy_promotion_approved",
                        mandate_ref="docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md",
                        spot_financing_executable=bool(a.leverage <= 1.0 + 1e-12 and a.max_gross <= SPOT_MAX_GROSS + 1e-12),
                        alpha_event_path=a.alpha_event_path,
                        stock_path=getattr(a, "stock_path", None),
                        alpha_event_sleeve=("not_book_consumable (no path)" if not a.alpha_event_path
                                           else a.alpha_event_path),
                        sleeve_notes=notes, collateral_frac=a.collateral_frac,
                        futures="IC via Eng FuturesLeg(load_index_futures_panels, roll 5d quarterly, 1 tick slip); notional rides on the "
                                f"shared cash pool (no MarginConfig borrowing); gross capped at {a.max_gross}",
                        cash_note="cash_incl_collateral includes futures collateral; idle<=5% applies to non-futures capital")
            m = run_book(D, sched, s, e, out / wn / arm, initial_cash=a.initial_cash, sleeve_frame=sf, meta=meta)
            table[f"{wn}/{arm}"] = m
            m.pop("_raw", None)
            log.info("%s %s cagr=%.4f mdd=%.4f sh=%.2f gross=%.2f/%.2f fut=%.2f cost=%.4f (%.0fs)", wn, arm, m["cagr"], m["mdd"],
                     m["sharpe"], m["gross_exposure_mean"], m["gross_exposure_max"], m["fut_exposure_mean"], m["cost_pct_initial"], time.time() - t0)
    json.dump(table, open(out / "compare_table.json", "w"), indent=1, default=str)
    return table


if __name__ == "__main__":
    main()
