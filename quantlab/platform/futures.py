"""CFFEX stock-index futures leg + cash interest for the V2 platform engine.

Opt-in: ``run_weight_schedule(..., futures=FuturesLeg(...))`` and
``ExecConfig(cash_rate=...)``. Defaults (None) leave every existing result unchanged.
Docs: docs/v2/EXECUTION_FUTURES_CASH.md (rules, dated tables, sources/assumptions).

Accounting (per contract, CNY):
  ref  = sum(lots x reference price x multiplier); at each session start ref = pos*prev_settle*mult.
  trade dq lots at p: ref += dq*p*mult, pos += dq      (no cash moves except fees)
  settle S:           vm = pos*S*mult - ref; cash += vm; ref = pos*S*mult
So variation margin over a holding period = sum of settle diffs x mult x lots (+ entry/exit legs).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

ROOTS = ("IF", "IH", "IC", "IM")
MULTIPLIER = {"IF": 300.0, "IH": 300.0, "IC": 200.0, "IM": 200.0}
TICK = 0.2   # index points, all four
DAILY_LIMIT = 0.10        # vs previous settle
LAST_DAY_LIMIT = 0.20     # last trading day of a contract (CFFEX rule)

# ---- CFFEX treasury bond futures (2026-10-11). Prices are quoted per 100 CNY face.
# multiplier = face/100: T/TF/TL face 1,000,000 -> 10,000; TS face 2,000,000 -> 20,000.
# Multiplier and tick VERIFIED against data/v2/futures/raw/fut_basic.parquet (multiplier column,
# quote_unit_desc): T/TF 0.005, TS 0.002 (not 0.005), TL 0.01. Last trading day = second Friday of
# the delivery month (fut_basic delist_date: 150/155 on 2nd-Friday dates, rest moved by holidays).
# Limits / margins / fees below are ASSUMPTIONS pending Data/compliance verification (see docs).
BOND_ROOTS = ("TS", "TF", "T", "TL")
BOND_MULTIPLIER = {"T": 10_000.0, "TF": 10_000.0, "TS": 20_000.0, "TL": 10_000.0}
BOND_TICK = {"T": 0.005, "TF": 0.005, "TS": 0.002, "TL": 0.01}
BOND_DAILY_LIMIT = {"T": 0.02, "TF": 0.012, "TS": 0.005, "TL": 0.035}   # vs prev settle
BOND_LAST_DAY_LIMIT = dict(BOND_DAILY_LIMIT)   # ASSUMPTION: same band on the last trading day
# per-contract CNY fees: (open, close_yesterday, close_today). VERIFIED (docs/v2/FUTURES_FEE_MARGIN_VERIFY.md
# "国债期货" section, CFFEX fee schedules zjssf/20240701/39212 & zjssf/20260601/47965): open/close-yesterday
# 3 CNY/lot, close-today FREE (平今仓免收). Delivery fee 5 CNY/lot not modelled (no physical delivery).
BOND_FEE_TABLE = [("2013-09-06", 3.0, 3.0, 0.0)]
BOND_DELIVERY_FEE_PER_LOT = 5.0
# Data 2026-10-11 (bond_fut_fee_hist.parquet / fut_settle): constant since listing, no dated change history
# found -> open/close-yd 3, close-today 0, delivery 5 CNY/lot carried back to listing = ASSUMPTION.
BOND_FEE_ASSUMED = True
# exchange minimum margin (fraction of notional, non-delivery-month). VERIFIED same doc: T 2%, TF 1% (not 1.2%;
# 1.2% = typical broker add-on / TF daily limit), TS 0.5%, TL 3.5%. Delivery-month step-ups not modelled
# (positions roll before the delivery month).
# DATED TABLE (2026-10-12): rows only at each root's LISTING date (fut_basic.list_date: TF 2013-09-06,
# T 2015-03-20, TS 2018-08-17, TL 2023-04-21). NO dated exchange margin CHANGE for T/TF/TS/TL is documented in
# any verified source on the box (FUTURES_FEE_MARGIN_VERIFY.md gives only the CURRENT standard), so every
# root carries its current verified value back to listing = ASSUMPTION, flagged. Known unknowns for Data:
# TF early rules reportedly said 1.2% (undated); any 2015-2016 / 2020 adjustments. Add rows here only from
# a dated CFFEX notice.
BOND_MARGIN_TABLE = [
    ("2013-09-06", {"TF": 0.01}),
    ("2015-03-20", {"T": 0.02}),
    ("2018-08-17", {"TS": 0.005}),
    ("2023-04-21", {"TL": 0.035}),
]
BOND_MARGIN_TABLE_CFFEX_CURRENT = list(BOND_MARGIN_TABLE)   # RULE FLOOR (细则 minimum, TF 1%) back to listing; sensitivity, not executed margin
BOND_MARGIN_TABLE_SETTLE_OBSERVED = None
BOND_MARGIN_ASSUMED_FLAT = True   # history before current standard unknown (see above)
_BOND_MARGIN_RAW = "data/v2/futures/bond_fut_settle_margin_raw.parquet"


_BOND_MARGIN_OFFICIAL = "data/v2/futures/bond_fut_margin_official.parquet"


def load_bond_margin_official(path=None):
    """CFFEX-verified non-delivery-month minimum margin history (Data, 2026-10-11, bond_fut_margin_official:
    notices linked per row; TF 2014-11-03 verified-via-reprint). Rows with a dated 生效日 only; negative-check
    rows (verified-absent: no 2015-16 / 2020 general-month changes; 2020-09-29 TF1.4/TS0.6 fut_settle spike
    NOT official) are skipped. Returns [(date, {root: rate})] or None."""
    from pathlib import Path
    f = Path(path) if path else (_REPO / _BOND_MARGIN_OFFICIAL)
    if not f.is_file():
        return None
    d = pd.read_parquet(f)
    d = d[d["品种"].isin(BOND_ROOTS) & d["生效日"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}$") & d["最低保证金"].notna()]
    rows, last = [], {}
    for r in d.sort_values("生效日").itertuples(index=False):
        root, day, rate = r[0], str(r[1]), round(float(r[2]) / 100.0, 6)
        if last.get(root) != rate:   # 2018-02-13 TF row = step-up rule change only, same 1.2% base
            rows.append((day, {root: rate})); last[root] = rate
    return rows


def load_bond_margin_table(path=None):
    """Dated NON-delivery-month exchange margin per bond root from Tushare fut_settle (Data, 2026-10-11):
    per (root, sampled date) take the MIN long_margin_rate across listed contracts (= base rate; contracts
    in/near delivery carry step-ups 3%/2%/1%/5%, which are therefore excluded here and modelled only via
    FuturesConfig.bond_delivery_margin -> no double count). Rows = dates where the base rate changes.
    fut_settle is SAMPLED (443 of ~3,200 sessions), so a change date is the first OBSERVED date, the true
    effective date may be earlier (flag). Returns [(date, {root: rate})] or None if the file is missing."""
    from pathlib import Path
    f = Path(path) if path else (_REPO / _BOND_MARGIN_RAW)
    if not f.is_file():
        return None
    r = pd.read_parquet(f, columns=["ts_code", "trade_date", "long_margin_rate", "short_margin_rate"])
    r = r.assign(root=r.ts_code.str.extract(r"^([A-Z]+)")[0],
                 rate=(r[["long_margin_rate", "short_margin_rate"]].max(axis=1) / 100.0).round(6))
    g = r.groupby(["root", "trade_date"]).rate.min().reset_index().sort_values(["root", "trade_date"])
    rows = []
    for root, x in g.groupby("root"):
        x = x[x.rate.ne(x.rate.shift())]
        rows += [(pd.Timestamp(str(d)).strftime("%Y-%m-%d"), root, float(v)) for d, v in zip(x.trade_date, x.rate)]
    return [(d, {root: v}) for d, root, v in sorted(rows)]
# delivery-month step-up, VERIFIED (same doc, CFFEX contract pages/rules): from the 2nd session BEFORE the
# delivery month: T 3%, TF 2%, TS 1%, TL 5%. Opt-in via FuturesConfig.bond_delivery_margin.
BOND_DELIVERY_MARGIN = {"T": 0.03, "TF": 0.02, "TS": 0.01, "TL": 0.05}
BOND_DELIVERY_MARGIN_SESSIONS = 2
ALL_MULTIPLIER = {**MULTIPLIER, **BOND_MULTIPLIER}


def is_bond_root(root: str) -> bool:
    return root in BOND_MULTIPLIER


def tick_for_root(root: str) -> float:
    return BOND_TICK.get(root, TICK)


def daily_limit(root: str, last_day: bool = False) -> float:
    if is_bond_root(root):
        return (BOND_LAST_DAY_LIMIT if last_day else BOND_DAILY_LIMIT)[root]
    return LAST_DAY_LIMIT if last_day else DAILY_LIMIT


def bond_fee_per_lot(day) -> tuple[float, float, float]:
    return tuple(_lookup(BOND_FEE_TABLE, day))

# ---- dated fee table (fraction of notional). effective_date -> (open, close, close_today)
# Sources (CFFEX notices, as recalled; Data/compliance to verify): 2015-09-07 anti-HFT package
# (close-today 23 bp-of-10k = 0.0023); relaxations 2017-02-17, 2017-09-18, 2018-12-03, 2019-04-22,
# 2023-03-20. Open/close 0.23/10000 since 2015-09-07. Pre-2015-09-07 approximate 0.25/10000 all legs.
# IM (listed 2022-07-22) follows the IC/IF schedule. Exchange fees only; broker add-on via fee_add.
FEE_TABLE = [
    ("2010-04-16", 0.000025, 0.000025, 0.000025),
    ("2015-09-07", 0.000023, 0.000023, 0.0023),
    ("2017-02-17", 0.000023, 0.000023, 0.00092),
    ("2017-09-18", 0.000023, 0.000023, 0.00069),
    ("2018-12-03", 0.000023, 0.000023, 0.00046),
    ("2019-04-22", 0.000023, 0.000023, 0.000345),
    ("2023-03-20", 0.000023, 0.000023, 0.00023),
]
DELIVERY_FEE = 0.0001   # fraction of final-settlement notional (CFFEX index futures)

# ---- dated exchange margin table (speculative), effective_date -> {root: rate}. Same caveats.
MARGIN_TABLE = [
    ("2010-04-16", {"IF": 0.12, "IH": 0.12, "IC": 0.12, "IM": 0.12}),
    ("2015-09-07", {"IF": 0.40, "IH": 0.40, "IC": 0.40, "IM": 0.40}),
    ("2017-02-17", {"IF": 0.20, "IH": 0.20, "IC": 0.30, "IM": 0.30}),
    ("2017-09-18", {"IF": 0.15, "IH": 0.15, "IC": 0.30, "IM": 0.30}),
    ("2018-12-03", {"IF": 0.10, "IH": 0.10, "IC": 0.15, "IM": 0.15}),
    ("2019-04-22", {"IF": 0.10, "IH": 0.10, "IC": 0.12, "IM": 0.12}),
    ("2022-07-22", {"IF": 0.12, "IH": 0.12, "IC": 0.12, "IM": 0.12}),
]
# 2026-10-11: the former 2022-07-22 row (IF/IH 12%, IC 14%, IM 15%) was NOT verifiable and looks like
# broker margin; replaced per docs/v2/FUTURES_FEE_MARGIN_VERIFY.md (current CFFEX exchange standard
# 12% for IF/IH/IC/IM; ccbfutures.com 2026-05-06, guoshengqh.com 2026-09-29). The exact date IF/IH moved
# 10%->12% is UNVERIFIED (kept at 2022-07-22 = IM listing); run 10%/12% sensitivity via margin_override.
# FEE_TABLE rows 2015-09-07..2023-03-20 verified in the same doc (2010-04-16 row approximate).


def _lookup(table, day):
    day = pd.Timestamp(day)
    cur = table[0][1:] if len(table[0]) > 2 else table[0][1]
    for row in table:
        if pd.Timestamp(row[0]) <= day:
            cur = row[1:] if len(row) > 2 else row[1]
    return cur


def fee_rates(day) -> tuple[float, float, float]:
    """(open, close, close_today) fraction of notional on ``day``."""
    return tuple(_lookup(FEE_TABLE, day))


def margin_rate(root: str, day, source: str = "hist") -> float:
    """source (bonds only): 'hist' = BOND_MARGIN_TABLE (CFFEX-verified official history; TF 1.2% since
    2015-03-16) | 'settle_observed' = Tushare fut_settle-derived table (incl. 2020-09-29 TF1.4/TS0.6 spike)
    | 'cffex_current' = RULE FLOOR (细则 minimum, TF 1%) carried back to listing: a sensitivity, NOT the
    actually executed margin."""
    if is_bond_root(root):
        cur = None
        tab = {"cffex_current": BOND_MARGIN_TABLE_CFFEX_CURRENT,
               "settle_observed": BOND_MARGIN_TABLE_SETTLE_OBSERVED or BOND_MARGIN_TABLE}.get(source, BOND_MARGIN_TABLE)
        for d0, m in tab:      # per-root dated rows (each row may carry a subset of roots)
            if root in m and (cur is None or pd.Timestamp(d0) <= pd.Timestamp(day)):
                cur = m[root]
        return float(cur)
    return float(_lookup(MARGIN_TABLE, day)[root])


def root_of(contract: str) -> str:
    return "".join(ch for ch in contract if ch.isalpha()).upper()


def third_friday(year: int, month: int) -> pd.Timestamp:
    d = pd.Timestamp(year, month, 1)
    first_fri = d + pd.Timedelta(days=(4 - d.weekday()) % 7)
    return first_fri + pd.Timedelta(days=14)


def second_friday(year: int, month: int) -> pd.Timestamp:
    return third_friday(year, month) - pd.Timedelta(days=7)


def last_trade_date(contract: str, sessions: Sequence | None = None) -> pd.Timestamp:
    """Index futures: third Friday of the contract month; treasury bond futures (T/TF/TS/TL):
    second Friday. If not a session, the next session in that month (CFFEX)."""
    digits = "".join(ch for ch in contract if ch.isdigit())
    y, m = 2000 + int(digits[:2]), int(digits[2:4])
    d = second_friday(y, m) if is_bond_root(root_of(contract)) else third_friday(y, m)
    if sessions is not None:
        s = pd.DatetimeIndex(sessions)
        later = s[s >= d]
        if len(later) and later[0].month == m:
            return later[0]
    return d


def round_to_tick(px: float, tick: float = TICK) -> float:
    return float(np.floor(px / tick + 0.5 + 1e-9) * tick)


@dataclass
class FuturesPanels:
    """session x contract (e.g. 'IF2412'). settle required. pre_settle optional
    (default: previous session's settle; NaN on listing day -> limit not checked).
    expiry optional {contract: last trading day} (default: third-Friday rule on these sessions)."""
    settle: pd.DataFrame
    open: pd.DataFrame | None = None
    close: pd.DataFrame | None = None
    pre_settle: pd.DataFrame | None = None
    volume: pd.DataFrame | None = None
    expiry: Mapping | None = None


@dataclass
class FuturesConfig:
    roll_mode: str = "roll"            # roll: move to next contract roll_days sessions before last trade | deliver: cash-settle at expiry
    roll_days: int = 5                 # sessions before last trading day (session index distance)
    contract_months: str = "all"       # all | quarterly (choose among Mar/Jun/Sep/Dec only)
    lot_rounding: str = "nearest"      # nearest | floor (toward 0) on target contracts
    slippage_ticks: float = 0.0        # per side, in ticks
    fee_add: float = 0.0               # broker add-on, fraction of notional per side
    fee_override: tuple | None = None  # (open, close, close_today) constant
    margin_add: float = 0.0            # broker add-on to exchange margin rate
    margin_override: Mapping | None = None   # {root: rate} constant (roots missing from it use the table)
    bond_roll_before_delivery_month: bool = True   # bonds: roll anchor = first session of delivery month (no physical delivery modelled)
    # per-root roll distance (sessions); roots missing use roll_days. e.g. {"T": 15, "TF": 15, "IF": 5}
    roll_days_by_root: Mapping | None = None
    # bonds: "delivery_month_anchor" (legacy default: roll roll_days sessions before the first session of
    # the delivery month) | "earlier_of" (roll at min(LTD - roll_days, first delivery-month session -
    # bond_exit_sessions_before_dm)), i.e. N sessions before the root's own LTD but never inside the
    # delivery month. Only applies when bond_roll_before_delivery_month=True.
    bond_roll_rule: str = "delivery_month_anchor"
    bond_exit_sessions_before_dm: int = 1
    bond_delivery_margin: bool = False   # apply BOND_DELIVERY_MARGIN from 2 sessions before delivery month
    bond_fee_override: tuple | None = None   # (open, close, close_today) CNY per lot for T/TF/TS/TL
    bond_margin_source: str = "hist"   # hist (CFFEX-verified official; TF 1.2%) | settle_observed (Tushare fut_settle) | cffex_current (rule floor TF 1%, sensitivity only)
    shortfall_action: str = "flag"     # flag | reduce (forced reduce to affordable lots at next session's open)
    enforce_limits: bool = True
    delivery_fee: float = DELIVERY_FEE

    def __post_init__(self):
        assert self.roll_mode in ("roll", "deliver")
        assert self.contract_months in ("all", "quarterly")
        assert self.lot_rounding in ("nearest", "floor")
        assert self.shortfall_action in ("flag", "reduce")
        assert self.bond_roll_rule in ("delivery_month_anchor", "earlier_of")
        assert self.bond_margin_source in ("hist", "settle_observed", "cffex_current")

    def roll_days_for(self, root: str) -> int:
        r = self.roll_days_by_root or {}
        return int(r.get(root, self.roll_days))


@dataclass
class FuturesLeg:
    panels: FuturesPanels
    config: FuturesConfig = field(default_factory=FuturesConfig)


class FuturesBook:
    """State machine driven by run_weight_schedule hooks."""

    def __init__(self, leg: FuturesLeg, dates: pd.DatetimeIndex, events: list):
        self.cfg = leg.config
        p = leg.panels
        self.dates = dates
        S = p.settle.reindex(dates)
        self.contracts = list(S.columns)
        self.S = S.to_numpy(dtype=float)
        # forward-filled settle, only within each contract's own life (never past its last bar)
        _last = S.apply(lambda col: col.last_valid_index())
        _ff = S.ffill()
        for c in S.columns:
            if _last[c] is not None:
                _ff.loc[_ff.index > _last[c], c] = np.nan
        self.S_ff = _ff.to_numpy(dtype=float)
        self.O = p.open.reindex(index=dates, columns=self.contracts).to_numpy(float) if p.open is not None else self.S.copy()
        self.Cl = p.close.reindex(index=dates, columns=self.contracts).to_numpy(float) if p.close is not None else self.S.copy()
        if p.pre_settle is not None:
            self.PS = p.pre_settle.reindex(index=dates, columns=self.contracts).to_numpy(float)
        else:
            self.PS = np.vstack([np.full((1, len(self.contracts)), np.nan), self.S[:-1]])
        exp = dict(p.expiry or {})
        self.ltd = {c: pd.Timestamp(exp[c]) if c in exp else last_trade_date(c, dates) for c in self.contracts}
        # Expiries after the last session are OUTSIDE the window: sentinel index (never due to
        # roll / deliver inside the window). searchsorted would return len(dates) ("past the last
        # session"), making every such contract look due in the final roll_days sessions.
        self.BEYOND = len(dates) + 10**6
        _end = np.datetime64(dates.values[-1])
        def _idx(ts):
            d = np.datetime64(pd.Timestamp(ts))
            return self.BEYOND if d > _end else int(np.searchsorted(dates.values, d))
        self.ltd_idx = {c: _idx(self.ltd[c]) for c in self.contracts}
        self.col = {c: i for i, c in enumerate(self.contracts)}
        # roll anchor: last trading day (index) / first session of the delivery month (bonds, default)
        self.roll_idx = {}; self.dm_idx = {}; self.trig = {}
        for c in self.contracts:
            r = root_of(c); n_r = self.cfg.roll_days_for(r)
            a = self.ltd_idx[c]
            dm = _idx(self.ltd[c].replace(day=1)) if is_bond_root(r) else self.BEYOND
            self.dm_idx[c] = dm
            trig = a - n_r
            if is_bond_root(r) and self.cfg.bond_roll_before_delivery_month:
                if self.cfg.bond_roll_rule == "earlier_of":
                    trig = min(a - n_r, dm - self.cfg.bond_exit_sessions_before_dm)
                else:
                    a = dm; trig = dm - n_r
            self.roll_idx[c] = a
            self.trig[c] = trig      # roll mode: contract is "due" (roll out / not chosen) at sessions t >= trig
        self.roots = sorted({root_of(c) for c in self.contracts})
        n = len(self.contracts)
        self.pos = np.zeros(n); self.ref = np.zeros(n); self.opened_today = np.zeros(n)
        self.pending: dict[int, float] = {}          # contract -> signed lots
        self.target_w: dict[str, float] = {}         # root -> weight (sticky)
        self.events = events
        self.costs = dict(fee=0.0, slippage=0.0, roll_fee=0.0, roll_slippage=0.0, delivery_fee=0.0)
        self.vm_total = 0.0; self.margin_peak = 0.0; self.margin = 0.0
        self.n_rolls = 0; self.roll_spread_pnl = 0.0
        self.vm_series = np.zeros(len(dates)); self.margin_series = np.zeros(len(dates))
        self.exposure = np.zeros((len(dates), n), dtype=np.float32)
        self.fills: list = []
        self.forced: dict[int, float] = {}

    # -- helpers
    def mult(self, j): return ALL_MULTIPLIER[root_of(self.contracts[j])]

    def tick(self, j): return tick_for_root(root_of(self.contracts[j]))

    def mrate(self, j, t):
        r = root_of(self.contracts[j])
        mo = self.cfg.margin_override
        base = mo[r] if (mo and r in mo) else margin_rate(r, self.dates[t], self.cfg.bond_margin_source)
        if self.cfg.bond_delivery_margin and is_bond_root(r) and t >= self.dm_idx[self.contracts[j]] - BOND_DELIVERY_MARGIN_SESSIONS:
            base = max(base, BOND_DELIVERY_MARGIN[r])
        return base + self.cfg.margin_add

    def fee_amount(self, j, t, px, n_open, n_close, n_ct):
        """CNY fee for one fill. Index: fraction of notional; bonds: CNY per lot."""
        if is_bond_root(root_of(self.contracts[j])):
            fo, fc, fct = self.cfg.bond_fee_override or bond_fee_per_lot(self.dates[t])
            return n_open * fo + n_close * fc + n_ct * fct + (n_open + n_close + n_ct) * abs(px) * self.mult(j) * self.cfg.fee_add
        fo, fc, fct = self.fees(t)
        return abs(px) * self.mult(j) * (n_open * fo + n_close * fc + n_ct * fct)

    def fees(self, t):
        f = self.cfg.fee_override or fee_rates(self.dates[t])
        return tuple(x + self.cfg.fee_add for x in f)

    def choose(self, root, t) -> int | None:
        """Contract to hold for ``root`` as of session t: nearest listed contract whose
        last trading day is more than roll_days sessions away (roll mode) / not expired (deliver)."""
        best = None
        for c in self.contracts:
            if root_of(c) != root:
                continue
            if self.cfg.contract_months == "quarterly" and int(c[-2:]) % 3:
                continue
            j = self.col[c]
            if not np.isfinite(self.S_ff[t, j]):   # not yet listed (no settle so far) / no data
                continue
            gap = self.ltd_idx[c] - t
            if gap < 0 or (self.cfg.roll_mode == "roll" and t >= self.trig[c]):
                continue
            if best is None or self.ltd[c] < self.ltd[self.contracts[best]]:
                best = j
        return best

    def _held_unexpired(self, root, t) -> int | None:
        """Currently held contract of ``root`` whose last trading day is after session t (or None)."""
        for j in np.flatnonzero(self.pos):
            c = self.contracts[j]
            if root_of(c) == root and self.ltd_idx[c] > t and np.isfinite(self.S_ff[t, j]):
                return int(j)
        return None

    def margin_req(self, t, px=None):
        px = self.S[t] if px is None else px
        m = 0.0
        for j in np.flatnonzero(self.pos):
            mk = px[j] if np.isfinite(px[j]) else self.S[t - 1, j]
            m += abs(self.pos[j]) * mk * self.mult(j) * self.mrate(j, t)
        return m

    def unrealized(self, t, px):
        u = 0.0
        for j in np.flatnonzero((self.pos != 0) | (self.ref != 0)):
            mk = px[j] if np.isfinite(px[j]) else (self.S[t - 1, j] if t else np.nan)
            if np.isfinite(mk):
                u += self.pos[j] * mk * self.mult(j) - self.ref[j]
        return u

    # -- hooks
    def start(self, t):
        self.opened_today[:] = 0.0

    def trade(self, t, PX, cash, kind="target"):
        """Execute forced, roll and pending orders at PX row t. Returns cash delta (fees only)."""
        day = self.dates[t]; dcash = 0.0
        orders: list[tuple[int, float, str]] = []
        for j, q in list(self.forced.items()):
            orders.append((j, q, "forced_reduce"))
        self.forced.clear()
        if self.cfg.roll_mode == "roll":
            for j in np.flatnonzero(self.pos):
                c = self.contracts[j]
                if t >= self.trig[c]:
                    nj = self.choose(root_of(c), t)
                    if nj is None or nj == j:
                        if not any(e.get("reason") == "fut_roll_no_next" and e.get("code") == c for e in self.events[-50:]):
                            self.events.append(dict(date=str(day.date()), code=c, reason="fut_roll_no_next"))
                        continue
                    q = self.pos[j]
                    pend = self.pending.pop(j, 0.0)
                    orders.append((j, -q, "roll_out"))
                    orders.append((nj, q + pend, "roll_in"))
        for j, q in list(self.pending.items()):
            orders.append((j, q, "order"))
        blocked_out = False
        for j, q, why in orders:
            if q == 0:
                continue
            if why == "order" and j in self.forced:
                continue
            px0 = PX[t, j]
            if why == "roll_in" and blocked_out:
                blocked_out = False
                continue
            blocked_out = False
            if not np.isfinite(px0):
                self.events.append(dict(date=str(day.date()), code=self.contracts[j], reason="fut_no_price", lots=q))
                if why == "roll_out":
                    blocked_out = True
                elif why == "roll_in":
                    self.pending[j] = q
                continue
            side = 1 if q > 0 else -1
            if self.cfg.enforce_limits and np.isfinite(self.PS[t, j]):
                lim = daily_limit(root_of(self.contracts[j]), self.ltd_idx[self.contracts[j]] == t)
                up = self.PS[t, j] * (1 + lim)
                dn = self.PS[t, j] * (1 - lim)
                if (side > 0 and px0 >= up - 1e-6) or (side < 0 and px0 <= dn + 1e-6):
                    self.events.append(dict(date=str(day.date()), code=self.contracts[j], reason="fut_limit_up" if side > 0 else "fut_limit_down", lots=q))
                    if why == "roll_out":
                        blocked_out = True
                    elif why == "roll_in":
                        self.pending[j] = q   # leg-in retried next session as a normal order
                    continue   # pending / roll retried next session
            px = round_to_tick(px0 + side * self.cfg.slippage_ticks * self.tick(j), self.tick(j))
            m = self.mult(j)
            # fee: closing part uses close / close-today rate
            closing = min(abs(q), abs(self.pos[j])) if np.sign(self.pos[j]) == -side else 0.0
            ct = min(closing, self.opened_today[j])
            fee = self.fee_amount(j, t, px, abs(q) - closing, closing - ct, ct)
            slip = abs(px - px0) * m * abs(q)
            if why == "roll_out" or why == "roll_in":
                self.costs["roll_fee"] += fee; self.costs["roll_slippage"] += slip
                if why == "roll_out":
                    self.n_rolls += 1
            else:
                self.costs["fee"] += fee; self.costs["slippage"] += slip
            self.ref[j] += q * px * m
            self.pos[j] += q
            if abs(q) > closing:
                self.opened_today[j] += abs(q) - closing
            dcash -= fee
            if why == "order":
                self.pending.pop(j, None)
            elif why == "roll_in":
                self.pending.pop(j, None)
            self.fills.append(dict(date=str(day.date()), code=self.contracts[j], lots=q, price=px, ref_price=px0, fee=fee, why=why))
        return dcash

    def signal(self, t, weights: Mapping, nav_sig: float):
        """New root weights (signed notional/NAV) -> pending lot orders, locked at signal settle."""
        self.pending = {}
        for r, w in weights.items():
            self.target_w[r] = float(w)
        tgt: dict[int, float] = {}
        for r, w in self.target_w.items():
            j = self.choose(r, t + 1 if t + 1 < len(self.dates) else t) if self.cfg.roll_mode == "roll" else self.choose(r, t)
            if j is None and self.cfg.roll_mode == "roll":
                j = self._held_unexpired(r, t)   # no next contract: keep holding current if not expired in-window
            if j is None:
                if w:
                    self.events.append(dict(date=str(self.dates[t].date()), code=r, reason="fut_no_contract"))
                continue
            ref = self.S_ff[t, j]   # last known settle (a missing settle row must not give NaN lots)
            raw = w * nav_sig / (ref * self.mult(j))
            lots = np.round(raw) if self.cfg.lot_rounding == "nearest" else np.trunc(raw + np.sign(raw) * 1e-9)
            tgt[j] = float(lots)
        for j in set(np.flatnonzero(self.pos)) | set(tgt):
            d = tgt.get(j, 0.0) - self.pos[j]
            if d:
                self.pending[j] = d

    def settle(self, t, cash: float, nav_ex_fut: float, stock_cash_needed: float = 0.0, credit: float = 0.0):
        """MTM at settle; delivery at expiry; margin + shortfall check. Returns cash delta."""
        day = self.dates[t]; dcash = 0.0
        for j in np.flatnonzero((self.pos != 0) | (self.ref != 0)):
            s = self.S[t, j]
            if not np.isfinite(s):
                continue   # no settle (suspended row): carry, margin on last settle
            vm = self.pos[j] * s * self.mult(j) - self.ref[j]
            dcash += vm; self.vm_total += vm; self.vm_series[t] += vm
            self.ref[j] = self.pos[j] * s * self.mult(j)
            if self.pos[j] and self.ltd_idx[self.contracts[j]] == t:   # cash delivery at final settlement
                if is_bond_root(root_of(self.contracts[j])):
                    fee = abs(self.pos[j]) * BOND_DELIVERY_FEE_PER_LOT   # CNY/lot (ASSUMPTION constant, see BOND_FEE_ASSUMED)
                else:
                    fee = abs(self.pos[j]) * s * self.mult(j) * self.cfg.delivery_fee
                self.costs["delivery_fee"] += fee; dcash -= fee
                self.events.append(dict(date=str(day.date()), code=self.contracts[j], reason="fut_delivery",
                                        lots=float(self.pos[j]), settle=float(s), fee=fee))
                self.pos[j] = 0.0; self.ref[j] = 0.0; self.pending.pop(j, None)
        self.margin = self.margin_req(t)
        self.margin_series[t] = self.margin
        self.margin_peak = max(self.margin_peak, self.margin)
        free = cash + dcash + credit - self.margin   # credit: unused financing line (margin account)
        if free < -1e-6:
            self.events.append(dict(date=str(day.date()), reason="fut_margin_shortfall", cash=cash + dcash,
                                    margin=self.margin, shortfall=-free, action=self.cfg.shortfall_action))
            if self.cfg.shortfall_action == "reduce":
                budget = max(cash + dcash + credit, 0.0)
                scale = budget / self.margin if self.margin > 0 else 0.0
                for j in np.flatnonzero(self.pos):
                    keep = np.trunc(self.pos[j] * scale)
                    if keep != self.pos[j]:
                        self.forced[j] = keep - self.pos[j]
                        self.pending.pop(j, None)
        if nav_ex_fut + dcash > 0:
            for j in np.flatnonzero(self.pos):
                self.exposure[t, j] = self.pos[j] * self.S[t, j] * self.mult(j) / (nav_ex_fut + dcash)
        return dcash

    def report(self):
        d = self.dates
        return dict(fut_costs=dict(self.costs), fut_total_fees=self.costs["fee"] + self.costs["roll_fee"] + self.costs["delivery_fee"],
                    roll_cost=self.costs["roll_fee"] + self.costs["roll_slippage"], n_rolls=self.n_rolls,
                    margin_peak=self.margin_peak, variation_margin=self.vm_total,
                    variation_margin_daily=pd.Series(self.vm_series, index=d),
                    margin=pd.Series(self.margin_series, index=d),
                    fut_positions={self.contracts[j]: float(self.pos[j]) for j in np.flatnonzero(self.pos)},
                    fut_exposure=pd.DataFrame(self.exposure, index=d, columns=self.contracts),
                    fut_fills=self.fills)


# ------------------------------------------------------------- cash interest

def cash_rate_per_session(dates: pd.DatetimeIndex, cash_rate, convention: str = "act365",
                          series_kind: str = "annual", day_count: float | None = None) -> np.ndarray:
    """Per-session simple rate r[t] applied to idle cash held over (t-1 close -> t close).
    r[0] = 0.
    * float: annual rate; convention 'act365' -> rate*days/365 (calendar days since prior session),
      'per_session' -> rate/252.
    * Series (by session): series_kind 'annual' (decimal annual rate, e.g. Shibor O/N/100, fixed at
      t-1, accrues rate*days/day_count; day_count default 365, use 360 for Shibor money-market basis)
      or 'return' (per-session total return of e.g. 511880 on session t, applied as is).
    Missing series values are forward-filled; before first value -> 0."""
    dates = pd.DatetimeIndex(dates)
    n = len(dates); r = np.zeros(n)
    if cash_rate is None or n < 2:
        return r
    days = np.diff(dates.values).astype("timedelta64[D]").astype(float)
    if np.isscalar(cash_rate):
        rate = float(cash_rate)
        if convention == "act365":
            r[1:] = rate * days / 365.0
        elif convention == "per_session":
            r[1:] = rate / 252.0
        else:
            raise ValueError(convention)
        return r
    s = pd.Series(cash_rate).copy(); s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    if series_kind == "return":
        a = s.reindex(dates).fillna(0.0).to_numpy(float)
        r[1:] = a[1:]
        return r
    if series_kind != "annual":
        raise ValueError(series_kind)
    dc = float(day_count or 365.0)
    a = s.reindex(s.index.union(dates)).ffill().reindex(dates).fillna(0.0).to_numpy(float)
    r[1:] = a[:-1] * days / dc
    return r


_REPO = __import__("pathlib").Path(__file__).resolve().parents[2]


def load_shibor(tenor: str = "ON", start=None, end=None, path=None) -> pd.Series:
    """Shibor fixing as DECIMAL annual rate by date (data/v2/rates/shibor.parquet, percent as landed).
    Use with ExecConfig(cash_rate=s, cash_rate_kind='annual', cash_rate_day_count=360) (ACT/360)."""
    col = {"ON": "on", "O/N": "on", "1W": "1w", "2W": "2w", "1M": "1m", "3M": "3m", "6M": "6m",
           "9M": "9m", "1Y": "1y"}[str(tenor).upper()]
    df = pd.read_parquet(path or _REPO / "data/v2/rates/shibor.parquet", columns=["date", col])
    s = pd.Series(pd.to_numeric(df[col], errors="coerce").to_numpy() / 100.0,
                  index=pd.to_datetime(df["date"].astype(str), format="%Y%m%d"), name=f"shibor_{col}")
    s = s[~s.index.duplicated(keep="last")].sort_index().dropna()
    if start is not None:
        s = s[s.index >= pd.Timestamp(start)]
    if end is not None:
        s = s[s.index <= pd.Timestamp(end)]
    return s


def load_lpr(tenor: str = "1Y", start=None, end=None, path=None) -> pd.Series:
    """Loan Prime Rate (monthly fixing) as DECIMAL annual rate by fixing date, from
    data/v2/rates/lpr.parquet (percent as landed; 5Y starts 2019-08-20). Step series: reindex+ffill
    onto sessions for use as a financing-rate base (e.g. MarginConfig spread over LPR 1Y)."""
    col = {"1Y": "1y", "5Y": "5y"}[str(tenor).upper()]
    df = pd.read_parquet(path or _REPO / "data/v2/rates/lpr.parquet", columns=["date", col])
    s = pd.Series(pd.to_numeric(df[col], errors="coerce").to_numpy() / 100.0,
                  index=pd.to_datetime(df["date"].astype(str), format="%Y%m%d"), name=f"lpr_{col}")
    s = s[~s.index.duplicated(keep="last")].sort_index().dropna()
    if start is not None:
        s = s[s.index >= pd.Timestamp(start)]
    if end is not None:
        s = s[s.index <= pd.Timestamp(end)]
    return s


_FUT_DAILY_DIR = _REPO / "data/v2/futures/raw/daily"
_FUT_BASIC = _REPO / "data/v2/futures/raw/fut_basic.parquet"


_BOND_DAILY = _REPO / "data/v2/futures/bond_fut_daily.parquet"
_BOND_CONTRACTS = _REPO / "data/v2/futures/bond_fut_contracts.parquet"


def repair_missing_settle(settle: pd.DataFrame, pre_settle: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Tushare leaves settle NaN on a few bond-futures days (2019-01-18/02-13/02-15, every T/TF/TS
    contract, both raw/daily and bond_fut_daily). The exchange settle of day t is the NEXT session's
    pre_settle (same number, published t 17:00), so fill from there. Returns (settle, n_filled)."""
    nxt = pre_settle.reindex_like(settle).shift(-1)
    fill = settle.isna() & nxt.notna()
    # only inside a contract's life (a bar exists that day): pre_settle row present on day t
    fill &= pre_settle.reindex_like(settle).notna()
    return settle.where(~fill, nxt), int(fill.to_numpy().sum())


def load_bond_futures_panels(roots=BOND_ROOTS, start=None, end=None, *, contracts=None,
                             daily_path=None, contracts_path=None) -> FuturesPanels:
    """T/TF/TS/TL from Data's consolidated bond_fut_daily.parquet (155 contracts incl. expired,
    2013-09-06..2026-10-09; identical bars to raw/daily, checked 2026-10-11) + expiry from
    bond_fut_contracts.delist_date. Missing settles repaired via repair_missing_settle."""
    df = pd.read_parquet(daily_path or _BOND_DAILY,
                         columns=["ts_code", "trade_date", "open", "close", "settle", "pre_settle", "vol"])
    df = df.assign(c=df.ts_code.str.split(".").str[0])
    df = df[df.c.str.extract(r"^([A-Z]+)")[0].isin(roots)] if contracts is None else df[df.c.isin([x.split(".")[0] for x in contracts])]
    if start is not None:
        df = df[df.trade_date.astype(str) >= pd.Timestamp(start).strftime("%Y%m%d")]
    if end is not None:
        df = df[df.trade_date.astype(str) <= pd.Timestamp(end).strftime("%Y%m%d")]
    if df.empty:
        raise FileNotFoundError(f"no bond futures bars for {roots or contracts}")
    df = df.assign(date=pd.to_datetime(df.trade_date.astype(str), format="%Y%m%d"))
    _u = df.drop_duplicates(["date", "c"], keep="last")
    w = lambda f: _u.pivot(index="date", columns="c", values=f).sort_index().astype(float)   # pivot_table would DROP all-NaN-settle days
    ps = w("pre_settle")
    st, n = repair_missing_settle(w("settle"), ps)
    b = pd.read_parquet(contracts_path or _BOND_CONTRACTS, columns=["ts_code", "delist_date"])
    cs = set(df.c)
    expiry = {t.split(".")[0]: pd.Timestamp(str(d)) for t, d in zip(b.ts_code, b.delist_date)
              if t.split(".")[0] in cs and pd.notna(d)}
    p = FuturesPanels(settle=st, open=w("open"), close=w("close"), pre_settle=ps, volume=w("vol"), expiry=expiry)
    p.settle_repaired = n
    return p


def _merge_panels(a: FuturesPanels, b: FuturesPanels) -> FuturesPanels:
    j = lambda x, y: None if x is None or y is None else pd.concat([x, y], axis=1).sort_index()
    return FuturesPanels(settle=j(a.settle, b.settle), open=j(a.open, b.open), close=j(a.close, b.close),
                         pre_settle=j(a.pre_settle, b.pre_settle), volume=j(a.volume, b.volume),
                         expiry={**(a.expiry or {}), **(b.expiry or {})})


def load_futures_panels(roots=("IF",), start=None, end=None, *, contracts=None, bond_source="auto", **kw) -> FuturesPanels:
    """Any CFFEX roots (IF/IH/IC/IM and T/TF/TS/TL) -> one FuturesPanels for a multi-root FuturesLeg.
    Bond roots/contracts come from bond_fut_daily.parquet when present (bond_source='auto'|'bond_files'),
    else / 'raw' from raw/daily. File pattern is root + exactly 4 digits, so "T" never picks TF/TS/TL."""
    use_bond = bond_source == "bond_files" or (bond_source == "auto" and _BOND_DAILY.is_file())
    if contracts is not None:
        bc = [c for c in contracts if is_bond_root(root_of(c.split(".")[0]))]
        ic = [c for c in contracts if c not in bc]
        parts = []
        if bc and use_bond:
            parts.append(load_bond_futures_panels(contracts=bc, start=start, end=end))
        elif bc:
            parts.append(load_index_futures_panels(start=start, end=end, contracts=bc, **kw))
        if ic:
            parts.append(load_index_futures_panels(start=start, end=end, contracts=ic, **kw))
    else:
        br = tuple(r for r in roots if is_bond_root(r)); ir = tuple(r for r in roots if r not in br)
        parts = []
        if br and use_bond:
            parts.append(load_bond_futures_panels(br, start, end))
        elif br:
            parts.append(load_index_futures_panels(br, start, end, **kw))
        if ir:
            parts.append(load_index_futures_panels(ir, start, end, **kw))
    out = parts[0]
    for q in parts[1:]:
        out = _merge_panels(out, q)
    return out


def load_index_futures_panels(roots=("IF",), start=None, end=None, *, contracts=None,
                              daily_dir=None, basic_path=None) -> FuturesPanels:
    """Real CFFEX daily bars (Tushare fut_daily, one file per contract in data/v2/futures/raw/daily,
    e.g. IF2412.CFX.parquet) -> FuturesPanels keyed by bare contract ('IF2412'): settle, open, close,
    pre_settle (exchange), volume (lots); expiry from fut_basic.delist_date (last trading day)."""
    from pathlib import Path
    d = Path(daily_dir or _FUT_DAILY_DIR)
    if contracts is None:
        files = [f for r in roots for f in sorted(d.glob(f"{r}[0-9][0-9][0-9][0-9].CFX.parquet"))]
    else:
        files = [d / f"{c.split('.')[0]}.CFX.parquet" for c in contracts]
    rows = []
    lo = pd.Timestamp(start).strftime("%Y%m%d") if start is not None else None
    hi = pd.Timestamp(end).strftime("%Y%m%d") if end is not None else None
    for f in files:
        if not f.is_file():
            continue
        df = pd.read_parquet(f, columns=["ts_code", "trade_date", "open", "close", "settle", "pre_settle", "vol"])
        if lo:
            df = df[df.trade_date.astype(str) >= lo]
        if hi:
            df = df[df.trade_date.astype(str) <= hi]
        if len(df):
            rows.append(df)
    if not rows:
        raise FileNotFoundError(f"no futures bars for {roots or contracts} in {d}")
    raw = pd.concat(rows)
    raw = raw.assign(c=raw.ts_code.str.split(".").str[0], date=pd.to_datetime(raw.trade_date.astype(str), format="%Y%m%d"))
    _u = raw.drop_duplicates(["date", "c"], keep="last")
    w = lambda f: _u.pivot(index="date", columns="c", values=f).sort_index().astype(float)   # keep all-NaN-settle days
    b = pd.read_parquet(basic_path or _FUT_BASIC, columns=["ts_code", "delist_date"])
    b = b.assign(c=b.ts_code.str.split(".").str[0])
    cs = set(raw.c)
    expiry = {r.c: pd.Timestamp(str(r.delist_date)) for r in b.itertuples() if r.c in cs and pd.notna(r.delist_date)}
    ps = w("pre_settle")
    st, _n = repair_missing_settle(w("settle"), ps)
    return FuturesPanels(settle=st, open=w("open"), close=w("close"), pre_settle=ps,
                         volume=w("vol"), expiry=expiry)


def load_511880_returns(start=None, end=None, root=None, table=None) -> pd.Series:
    """Per-session total return of 511880.SH (money-market ETF). Default source:
    data/v2/etf/etf_daily_adj.parquet (close x adj_factor, through 2026-10-09); fallback / ``root``:
    data/v2/etf/raw fund_daily x fund_adj. Use with series_kind='return'. Note 511880's adj_factor
    carries its distributions; Data's fake-jump investigation concerns 510300 (check if in doubt)."""
    from pathlib import Path
    tbl = Path(table) if table else (_REPO / "data/v2/etf/etf_daily_adj.parquet" if root is None else None)
    if tbl is not None and tbl.is_file():
        import pyarrow.parquet as pq
        flt = [("ts_code", "=", "511880.SH")]
        if start is not None:
            flt.append(("trade_date", ">=", pd.Timestamp(start).strftime("%Y%m%d")))
        if end is not None:
            flt.append(("trade_date", "<=", pd.Timestamp(end).strftime("%Y%m%d")))
        df = pq.read_table(tbl, columns=["trade_date", "close", "adj_factor"], filters=flt).to_pandas()
        if len(df):
            df.index = pd.to_datetime(df.trade_date.astype(str), format="%Y%m%d")
            df = df[~df.index.duplicated(keep="last")].sort_index()
            px = df.close.astype(float) * df.adj_factor.astype(float).ffill().bfill()
            return px.pct_change().fillna(0.0)
    root = Path(root or _REPO / "data/v2/etf/raw")
    rows = []
    for f in sorted((root / "fund_daily").glob("*.parquet")):
        d = f.stem
        if (start and d < pd.Timestamp(start).strftime("%Y%m%d")) or (end and d > pd.Timestamp(end).strftime("%Y%m%d")):
            continue
        df = pd.read_parquet(f, columns=["ts_code", "trade_date", "close"])
        df = df[df.ts_code == "511880.SH"]
        if len(df):
            rows.append(df)
    if not rows:
        return pd.Series(dtype=float)
    px = pd.concat(rows); px.index = pd.to_datetime(px.trade_date.astype(str)); px = px.close.astype(float).sort_index()
    adj = []
    for f in sorted((root / "fund_adj").glob("*.parquet")):
        d = f.stem
        if (start and d < pd.Timestamp(start).strftime("%Y%m%d")) or (end and d > pd.Timestamp(end).strftime("%Y%m%d")):
            continue
        df = pd.read_parquet(f)
        df = df[df.ts_code == "511880.SH"]
        if len(df):
            adj.append(df[["trade_date", "adj_factor"]])
    if adj:
        a = pd.concat(adj); a.index = pd.to_datetime(a.trade_date.astype(str)); a = a.adj_factor.astype(float).sort_index()
        px = px * a.reindex(px.index).ffill().bfill()
    return px.pct_change().fillna(0.0)


# ---- 2026-10-11: dated bond margin history from Tushare fut_settle replaces the flat table (default
# FuturesConfig.bond_margin_source='hist'); cffex_current sensitivity keeps the flat current standard.
# 2026-10-11 (later): default 'hist' = CFFEX-verified official file; settle-derived kept as 'settle_observed'.
BOND_MARGIN_TABLE_SETTLE_OBSERVED = load_bond_margin_table()
_off = load_bond_margin_official()
if _off:
    BOND_MARGIN_TABLE = _off
    BOND_MARGIN_ASSUMED_FLAT = False
    BOND_MARGIN_SOURCE = "official"
elif BOND_MARGIN_TABLE_SETTLE_OBSERVED:
    BOND_MARGIN_TABLE = BOND_MARGIN_TABLE_SETTLE_OBSERVED
    BOND_MARGIN_ASSUMED_FLAT = False
    BOND_MARGIN_SOURCE = "settle_observed"
else:
    BOND_MARGIN_SOURCE = "cffex_current_flat"
del _off
