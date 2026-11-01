"""Platform execution + cost engine (opt-in, research-grade).

Strategy calls these helpers; nothing here changes the defaults of
``quantlab.backtest.ledger.Ledger`` or ``quantlab.smallcap.sim.simulate``.
No performance conclusions are produced here.

Conventions (see docs/v2/EXECUTION_COSTS_PLATFORM.md):
  * panels are wide ``date x code`` DataFrames; volume is **shares**
    (use :func:`normalize_volume_to_shares` for lot-denominated sources);
    amount is **CNY**.
  * a schedule maps signal session -> {code: weight of NAV at that close}.
    Codes missing from a new signal are sold to zero.
  * fill modes: ``close`` (fill at signal-day close), ``next_open`` (T+1 open),
    ``next_vwap`` (T+1 amount/volume_shares; fallback documented in
    :func:`vwap_panel`).
  * holdings are always marked to close (halt -> last close carried, full move
    realized on resumption). Limit / halt rules only block fills.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

STAMP_CUT = pd.Timestamp("2023-08-28")
LIMIT_EPS = 0.005  # CNY; one half tick

__all__ = [
    "ExecConfig", "ExecPanels", "LotRule", "lot_rule_for", "round_order_quantity",
    "normalize_volume_to_shares", "infer_volume_scale", "vwap_panel",
    "sqrt_impact_cost", "split_returns", "forward_return_components",
    "run_weight_schedule", "capacity_curve", "reconcile_zero_cost",
    "corporate_action_arrays", "total_return_factor", "load_corporate_action_panels",
    "cost_ladder", "load_execution_panels", "ZERO_COST", "round_to_tick",
    "tick_for_code", "is_exchange_fund", "stamp_exempt", "resolve_tick",
    "IMPACT_K_SENSITIVITY", "impact_sensitivity_configs", "run_impact_sensitivity",
    "IMPACT_K_SIZE_BUCKET_REFERENCE", "effective_n_holdings", "return_stats_ex_suspended",
    "instrument_type", "is_convertible_bond", "fund_limit_pct", "derived_limit_pct", "CB_LIMIT_START",
    "load_cb_panels", "load_fund_daily_panels", "is_exchangeable_bond", "is_exchange_bond",
    "prepare_panels_for_execution", "subset_exec_panels", "filter_cb_panels",
    "PANEL_POLICY_FULL", "impact_inputs_for_codes",
]

# ----------------------------------------------------------------- instrument types (2026-10-11)
# CB  : SH 110/111/113/118xxx, SZ 123/127/128xxx (verified against data/v2/cb/raw/cb_daily; that source
#       also carries exchangeable bonds sh.132 / sz.120 which are classified separately as 'eb').
# EB  : SH 132xxx, SZ 120xxx exchangeable bonds (2026-10-11): no stamp tax, lot 10, tick 0.001, CB
#       commission, and NO price limit (Data: the 2022-08-01 CB trading rules do not cover EBs;
#       COMPLIANCE TO REVIEW).
# fund: SH 50/51/52/56/58xxxx, SZ 15/16/18xxxx (ETF / LOF).
# stock: everything else (unchanged behaviour).
CB_LIMIT_START = pd.Timestamp("2022-08-01")   # SSE/SZSE CB trading rules: +-20% vs prev close, 30% temp halt
CB_PREFIX = {"sh": ("110", "111", "113", "118"), "sz": ("123", "127", "128")}
EB_PREFIX = {"sh": ("132",), "sz": ("120",)}
_WIDE_LIMIT_FUNDS: set | None = None


def _split_code(code: str) -> tuple[str, str]:
    c = str(code).lower().strip()
    if c.endswith((".sh", ".sz", ".bj")):
        return c[-2:], c[:-3]
    if "." in c:
        a, b = c.split(".", 1)
        return a, b
    if c[:2] in ("sh", "sz", "bj"):
        return c[:2], c[2:]
    return "", c


def is_convertible_bond(code: str) -> bool:
    exch, num = _split_code(code)
    return len(num) == 6 and num.isdigit() and num.startswith(CB_PREFIX.get(exch, ("~",)))


def is_exchangeable_bond(code: str) -> bool:
    exch, num = _split_code(code)
    return len(num) == 6 and num.isdigit() and num.startswith(EB_PREFIX.get(exch, ("~",)))


def is_exchange_bond(code: str) -> bool:
    """Convertible OR exchangeable bond (shared lot/tick/stamp/commission rules)."""
    return is_convertible_bond(code) or is_exchangeable_bond(code)


def instrument_type(code: str) -> str:
    """'cb' | 'eb' | 'fund' | 'stock' (code-prefix classifier; see module notes)."""
    if is_convertible_bond(code):
        return "cb"
    if is_exchangeable_bond(code):
        return "eb"
    if is_exchange_fund(code):
        return "fund"
    return "stock"


def _wide_limit_funds() -> set:
    """Best-effort set of SZ 159xxx funds tracking ChiNext/STAR indices (+-20%), from fund_basic_E
    name/benchmark containing 创业板/科创/双创. sh.588xxx is always treated as STAR (+-20%)."""
    global _WIDE_LIMIT_FUNDS
    if _WIDE_LIMIT_FUNDS is None:
        out = set()
        try:
            fb = pd.read_parquet(Path(__file__).resolve().parents[2] / "data/v2/etf/raw/fund_basic_E.parquet",
                                 columns=["ts_code", "name", "benchmark"])
            txt = fb["name"].fillna("").astype(str) + "|" + fb["benchmark"].fillna("").astype(str)
            m = txt.str.contains("创业板|科创|双创", regex=True)
            for tc in fb.loc[m, "ts_code"].astype(str):
                num, ex = tc.split(".")
                if ex.upper() == "SZ" and num.startswith("159"):
                    out.add(f"sz.{num}")
        except Exception:
            pass
        _WIDE_LIMIT_FUNDS = out
    return _WIDE_LIMIT_FUNDS


def fund_limit_pct(code: str) -> float:
    """ETF price limit: 0.20 for STAR (sh.588) and ChiNext/STAR-tracking sz.159 funds (best effort), else 0.10."""
    exch, num = _split_code(code)
    if exch == "sh" and num.startswith("588"):
        return 0.20
    if exch == "sz" and num.startswith("159") and f"sz.{num}" in _wide_limit_funds():
        return 0.20
    return 0.10


def derived_limit_pct(code: str, day) -> float | None:
    """Limit band used when no limit_up/limit_down panel value exists. Stocks -> None (unchanged).
    CB: None before 2022-08-01, 0.20 after (the 30% intraday temporary halt is not modelled: fills
    beyond +-20% are simply blocked). Funds: :func:`fund_limit_pct`."""
    t = instrument_type(code)
    if t == "cb":
        return 0.20 if pd.Timestamp(day) >= CB_LIMIT_START else None
    if t == "fund":
        return fund_limit_pct(code)
    return None

# Literature reference ONLY (not A-share calibrated; Strategy to calibrate):
# sqrt-impact coefficient by size bucket, expressed as cost at reference
# participation: large 0.45%, small 0.74%, micro 1.82%. Not a default.
IMPACT_K_SIZE_BUCKET_REFERENCE = {"large": 0.45, "small": 0.74, "micro": 1.82}

IMPACT_K_SENSITIVITY = (0.5, 1.0, 2.0)


def round_to_tick(px: float, tick: float | None) -> float:
    """Round a price half-up to ``tick`` (Ledger convention). ``None``/0 -> unchanged."""
    if not tick or not np.isfinite(px):
        return px
    from decimal import Decimal, ROUND_HALF_UP
    return float((Decimal(str(px)) / Decimal(str(tick))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) * tick


# ----------------------------------------------------------------- lots
@dataclass(frozen=True)
class LotRule:
    minimum: int      # minimum buy declaration (shares)
    step: int         # increment above the minimum


def lot_rule_for(code: str) -> LotRule:
    """A-share board lots implemented here.

    * STAR (``688xxx`` / ``689xxx``): min 200, then 1-share increments.
    * Beijing exchange (``bj.``/``8xxxxx``/``4xxxxx``/``92xxxx``): min 100, then 1.
    * everything else (main board, ChiNext): 100-share lots.
    ETFs / unknown non-stock codes passed in ``ExecConfig.no_limit_codes`` use 100.
    """
    c = str(code).lower()
    num = c.split(".")[-1]
    if is_exchange_bond(c):
        return LotRule(10, 10)       # 1 lot = 10 bonds (par 100)
    if is_exchange_fund(c):
        return LotRule(100, 100)
    if num.startswith(("688", "689")):
        return LotRule(200, 1)
    if c.startswith("bj.") or c.endswith(".bj"):
        return LotRule(100, 1)
    return LotRule(100, 100)


def is_exchange_fund(code: str) -> bool:
    """Exchange-traded funds (ETF / LOF / listed bond & money funds).

    SH ``50/51/52/56/58xxxx``, SZ ``15/16/18xxxx``. These trade with a 0.001
    tick, are stamp-duty exempt and use 100-unit lots.
    """
    c = str(code).lower()
    num = c.split(".")[-1] if "." in c else c
    if c.endswith((".sh", ".sz")):
        num = c.split(".")[0]
    exch = "sh" if (c.startswith("sh") or c.endswith(".sh")) else "sz" if (c.startswith("sz") or c.endswith(".sz")) else ""
    if len(num) != 6 or not num.isdigit():
        return False
    if exch == "sh":
        return num.startswith(("50", "51", "52", "56", "58"))
    if exch == "sz":
        return num.startswith(("15", "16", "18"))
    return False


def tick_for_code(code: str) -> float:
    """Minimum price increment: 0.001 for exchange funds, else 0.01 (A-shares)."""
    return 0.001 if (is_exchange_fund(code) or is_exchange_bond(code)) else 0.01


def stamp_exempt(code: str) -> bool:
    """Funds, convertible and exchangeable bonds pay no stamp duty (only stocks on sells)."""
    return is_exchange_fund(code) or is_exchange_bond(code)


def resolve_tick(code: str, price_tick) -> float | None:
    """``price_tick`` may be None/0 (off), a float (uniform) or 'auto' (per code)."""
    if isinstance(price_tick, str):
        if price_tick != "auto":
            raise ValueError(f"bad price_tick {price_tick}")
        return tick_for_code(code)
    return price_tick


def round_order_quantity(code: str, qty: float, side: int, holding: float = 0.0) -> int:
    """Largest legal quantity <= ``qty``.

    Sells may include an odd residual only when they close the whole position
    (exchange rule); otherwise sells use the same min/step as buys.
    """
    q = int(np.floor(max(qty, 0.0) + 1e-9))
    if side < 0 and holding > 0 and q >= int(round(holding)):
        return int(round(holding))
    rule = lot_rule_for(code)
    if q < rule.minimum:
        return 0
    return rule.minimum + (q - rule.minimum) // rule.step * rule.step


# ----------------------------------------------------------------- units
def infer_volume_scale(amount: pd.DataFrame, volume: pd.DataFrame, close: pd.DataFrame) -> pd.DataFrame:
    """Shares per volume unit, per cell: 100 when amount/(volume*close) ~ 100 (lots),
    else 1. Cells without a usable amount are NaN (caller decides fallback)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = amount / (volume * close)
    out = pd.DataFrame(np.where(ratio > 10, 100.0, np.where(ratio > 0, 1.0, np.nan)),
                       index=ratio.index, columns=ratio.columns)
    return out


def normalize_volume_to_shares(volume: pd.DataFrame, amount: pd.DataFrame | None = None,
                               close: pd.DataFrame | None = None, *,
                               default_scale: float | pd.DataFrame = 1.0) -> pd.DataFrame:
    """Return volume in shares. Per-cell scale from amount where available,
    then ffill/bfill per column, then ``default_scale`` (scalar or frame)."""
    if amount is None or close is None:
        return volume * default_scale
    scale = infer_volume_scale(amount, volume, close).ffill().bfill()
    if isinstance(default_scale, pd.DataFrame):
        scale = scale.fillna(default_scale.reindex_like(scale))
    else:
        scale = scale.fillna(float(default_scale))
    return volume * scale


def vwap_panel(amount: pd.DataFrame | None, volume_shares: pd.DataFrame, close: pd.DataFrame,
               open_: pd.DataFrame | None = None, high: pd.DataFrame | None = None,
               low: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily VWAP = amount / volume_shares.

    Fallback when amount is missing/<=0 but the bar traded: typical price
    (open+high+low+close)/4 if all four exist, else close. A VWAP outside
    [low, high] (unit mismatch) is also replaced by the fallback. Returns
    ``(vwap, used_fallback_bool_frame)``.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        v = amount / volume_shares if amount is not None else close * np.nan
    v = v.where((volume_shares > 0) & (v > 0))
    if high is not None and low is not None:
        v = v.where(~((v > high * 1.001) | (v < low * 0.999)))
    if all(x is not None for x in (open_, high, low)):
        fb = (open_ + high + low + close) / 4.0
        fb = fb.fillna(close)
    else:
        fb = close
    used = v.isna() & close.notna()
    return v.fillna(fb), used


# ----------------------------------------------------------------- costs
def sqrt_impact_cost(trade_value, adv_value, sigma_daily, k: float = 1.0):
    """Square-root impact in CNY: ``trade_value * k * sigma_daily * sqrt(trade_value / adv_value)``.

    ``sigma_daily`` is a daily return std (fraction), ``adv_value`` in CNY.
    The fractional rate is ``k*sigma*sqrt(participation)``; cost is CNY.
    Missing/zero ADV or sigma -> 0 (recorded by the engine as ``impact_missing``)."""
    tv = np.asarray(trade_value, dtype=float)
    adv = np.asarray(adv_value, dtype=float)
    sg = np.asarray(sigma_daily, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        rate = k * sg * np.sqrt(np.abs(tv) / adv)
    rate = np.where(np.isfinite(rate), rate, 0.0)
    return np.abs(tv) * rate


@dataclass
class ExecConfig:
    fill: str = "next_open"            # close | next_open | next_vwap
    commission: float = 0.00025
    min_commission: float = 5.0
    stamp_before: float = 0.001
    stamp_after: float = 0.0005
    slippage: float = 0.0              # fraction of price per side
    impact_k: float = 0.0              # 0 = off
    sigma_window: int = 20
    adv_window: int = 20
    participation_cap: float | None = None   # e.g. 0.10 = 10% of that day's volume
    unfilled: str = "carry"            # carry (retry next sessions until next signal) | drop
    lots: bool = True
    enforce_limits: bool = True
    min_trade_value: float = 0.0
    no_limit_codes: frozenset = field(default_factory=frozenset)   # ETFs etc.
    order_rounding: str = "target"     # target: lot-floor the target holding (Ledger; Strategy v1) | delta: legacy, lot-round the trade toward 0
    impact_k_by_bucket: Mapping | None = None   # e.g. {"large":..,"small":..,"micro":..}; None = off (uniform impact_k)
    size_bucket: Mapping | None = None          # code -> bucket name; codes w/o bucket use impact_k
    # Corporate actions (2026-10-11): on the ex-date, before the open, cash dividends are credited
    # (pre-tax per share x (1 - dividend_tax)) and bonus/transfer shares scale the holding; cells with
    # no per-event data but an adj_factor jump scale shares by the factor ratio (total-return
    # equivalent). Needs ExecPanels.cash_div/share_ratio/adj_factor; absent data -> no-op.
    # Default ON (correctness fix). corporate_actions=False reproduces pre-2026-10-11 results.
    corporate_actions: bool = True
    dividend_tax: float = 0.0   # 0 = pre-tax (documented default; institutional / >1y holder). e.g. 0.10 / 0.20 for short-hold individuals
    # Non-stock instruments (2026-10-11), keyed by instrument_type(); stocks unaffected.
    cb_commission: float = 0.0001
    cb_min_commission: float = 1.0
    derive_nonstock_limits: bool = True   # CB/fund cells w/o limit panel values: band vs prev close (derived_limit_pct)
    cash_rate: object = None                 # None = off (0% on idle cash). float annual rate or pd.Series by session (see futures.cash_rate_per_session)
    cash_rate_convention: str = "act365"     # float rate: act365 (rate*calendar days/365) | per_session (rate/252)
    cash_rate_kind: str = "annual"           # Series: annual (decimal rate fixed at t-1, ACT/day_count) | return (per-session return, e.g. 511880)
    cash_rate_day_count: float | None = None # Series 'annual': 365 default; 360 for Shibor basis
    price_tick: float | str | None = None    # 'auto' = tick_for_code per code (0.001 funds, 0.01 stocks); e.g. 0.01: fill price (after slippage) rounded half-up like Ledger; None = off (backward compatible)

    @classmethod
    def strategy_v1(cls, impact_k: float = 1.0, **overrides) -> "ExecConfig":
        """Strategy-agreed main convention (2026-10-10): next_open fills, per-code tick ('auto': 0.01 stocks, 0.001 funds),
        sqrt impact k (default 1.0), 10% participation cap, unfilled carry, lots,
        limits enforced, lot rounding on target holdings. Overrides via kwargs."""
        kw = dict(fill="next_open", price_tick="auto", impact_k=float(impact_k), participation_cap=0.10,
                  unfilled="carry", lots=True, enforce_limits=True, order_rounding="target",
                  corporate_actions=True)
        kw.update(overrides)
        return cls(**kw)

    def __post_init__(self):
        if self.fill not in ("close", "next_open", "next_vwap"):
            raise ValueError(f"bad fill mode {self.fill}")
        if self.unfilled not in ("carry", "drop"):
            raise ValueError(f"bad unfilled rule {self.unfilled}")
        if self.order_rounding not in ("target", "delta"):
            raise ValueError(f"bad order_rounding {self.order_rounding}")


def impact_sensitivity_configs(base: "ExecConfig | None" = None,
                               ks: Sequence[float] = IMPACT_K_SENSITIVITY) -> dict:
    """{k: config} with only ``impact_k`` changed (default base: strategy_v1)."""
    base = base or ExecConfig.strategy_v1()
    return {float(k): replace(base, impact_k=float(k)) for k in ks}


def run_impact_sensitivity(panels, schedule, *, initial_cash: float = 600_000.0,
                           base: "ExecConfig | None" = None, ks: Sequence[float] = IMPACT_K_SENSITIVITY,
                           record_weights: bool = False) -> pd.DataFrame:
    """Final NAV / cost / fill ratio per impact k. Rows: k, final_nav, total_return,
    impact_cny, total_cost, fill_ratio. No conclusions; research-grade."""
    rows = []
    for k, cfg in impact_sensitivity_configs(base, ks).items():
        r = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=cfg, record_weights=record_weights)
        rows.append(dict(k=k, final_nav=float(r["nav"].iloc[-1]), total_return=float(r["nav"].iloc[-1] / initial_cash - 1),
                         impact_cny=float(r["costs"]["impact"]), total_cost=float(r["total_cost"]),
                         fill_ratio=float(r["fill_ratio"]),
                         impact_bp_per_traded=float(r["impact_bp_per_traded"]),
                         effective_n_mean=float(r["effective_n_mean"])))
    return pd.DataFrame(rows)


ZERO_COST = dict(commission=0.0, min_commission=0.0, stamp_before=0.0, stamp_after=0.0,
                 slippage=0.0, impact_k=0.0)


@dataclass
class ExecPanels:
    close: pd.DataFrame
    open: pd.DataFrame | None = None
    high: pd.DataFrame | None = None
    low: pd.DataFrame | None = None
    volume: pd.DataFrame | None = None      # SHARES
    amount: pd.DataFrame | None = None      # CNY
    limit_up: pd.DataFrame | None = None
    limit_down: pd.DataFrame | None = None
    suspended: pd.DataFrame | None = None   # bool; default: close NaN or volume==0
    cash_div: pd.DataFrame | None = None    # CNY per share, PRE-TAX, on the ex-date row (0/NaN = none)
    share_ratio: pd.DataFrame | None = None # bonus+transfer shares per held share on the ex-date (1.0 = 10-for-10)
    adj_factor: pd.DataFrame | None = None  # multiplicative price adj factor (adj_px = px * F); fallback for events w/o data
    terminal_price: pd.DataFrame | None = None  # CB redemption/maturity/put: CNY per bond paid to cash before the open on that row

    def aligned(self) -> "ExecPanels":
        idx, cols = self.close.index, self.close.columns
        def al(x):
            return None if x is None else x.reindex(index=idx, columns=cols).astype(float)
        sus = self.suspended.reindex(index=idx, columns=cols).fillna(False).astype(bool) if self.suspended is not None else None
        return ExecPanels(self.close.astype(float), al(self.open), al(self.high), al(self.low), al(self.volume),
                          al(self.amount), al(self.limit_up), al(self.limit_down), sus,
                          al(self.cash_div), al(self.share_ratio), al(self.adj_factor), al(self.terminal_price))


# ----------------------------------------------------------------- panel policy (NAV gap 2026-10-12)
# Book/NAV and impact MUST use the same instrument×session panel set. Subsetting CB columns to the
# schedule-only set (historical Strategy ``filter_cb_panels``) changed column indices and cash-
# constrained fill order under participation caps, diverging PREMRESID impact/NAV from Beta's full
# ``cb_panels`` (X2 ≈ −31/−67bp). Schedule still only trades listed names; extra columns stay at 0.
# See output/v3/cb_premresid_cov/NAV_GAP_AUDIT_ZH.md.
PANEL_POLICY_FULL = "full"  # canonical: keep all panel columns for run_weight_schedule / impact


def subset_exec_panels(panels: "ExecPanels", codes) -> "ExecPanels":
    """Column-subset ``panels`` to ``codes`` (research / bug-repro only).

    Do **not** feed the result into NAV/impact recon against a full-panel book — that is the
    PREMRESID NAV-gap root cause. Prefer :func:`prepare_panels_for_execution`.
    """
    from dataclasses import fields as _fields
    want = {str(c) for c in codes}
    cols = [c for c in panels.close.columns if str(c) in want]
    if not cols:
        idx = panels.close.index
        empty = pd.DataFrame(index=idx)
        return ExecPanels(
            close=empty, open=empty, high=empty, low=empty,
            volume=empty, amount=empty, terminal_price=empty,
        ).aligned()
    kw = {}
    for f in _fields(ExecPanels):
        df = getattr(panels, f.name)
        if df is None:
            kw[f.name] = None
        else:
            keep = [c for c in cols if c in df.columns]
            kw[f.name] = df[keep]
    return ExecPanels(**kw).aligned()


def filter_cb_panels(panels: "ExecPanels", codes):
    """Deprecated alias of :func:`subset_exec_panels` (Strategy recon compat: returns ``(panels, 0)``).

    New callers should use :func:`prepare_panels_for_execution` (full panels) for execution/impact.
    """
    return subset_exec_panels(panels, codes), 0


def prepare_panels_for_execution(panels: "ExecPanels", schedule: Mapping | None = None,
                                 *, policy: str = PANEL_POLICY_FULL) -> "ExecPanels":
    """Align panels for ``run_weight_schedule`` / impact with the book/NAV path.

    **Chosen rule (``policy='full'``, default):** return ``panels.aligned()`` unchanged.
    Signal schedules still only trade listed names; full width does not change the holding set.
    Optional ``schedule`` is validated: every positive-weight code must exist in ``panels.close``.

    ``policy='schedule_only'`` subsets to schedule codes via :func:`subset_exec_panels` and is
    kept only to reproduce the historical NAV-gap bug in tests — not for production recon.
    """
    p = panels.aligned()
    if schedule is None:
        if policy != PANEL_POLICY_FULL:
            raise ValueError("schedule_only policy requires schedule")
        return p
    need = sorted({str(c) for w in schedule.values() for c, x in dict(w).items() if float(x) > 0})
    missing = [c for c in need if c not in p.close.columns]
    if missing:
        raise KeyError(f"schedule codes missing from panels: {missing[:8]}")
    if policy == "schedule_only":
        return subset_exec_panels(p, need)
    if policy != PANEL_POLICY_FULL:
        raise ValueError(f"unknown panel policy {policy!r}; use {PANEL_POLICY_FULL!r} or 'schedule_only'")
    return p


def impact_inputs_for_codes(panels: "ExecPanels", codes, *, sigma_window: int = 20,
                            adv_window: int = 20) -> dict:
    """Per-code ADV/SIG/close/amount slices used by sqrt-impact (shifted rolling).

    Same ids must yield identical inputs from a full panel or a column subset (no cross-sectional
    contamination). Fill-path NAV can still diverge under different column sets — use
    :func:`prepare_panels_for_execution` (full) for book/impact parity.
    """
    p = panels.aligned()
    codes = [str(c) for c in codes if str(c) in p.close.columns]
    out = {}
    _cl = p.close[codes].ffill(limit_area="inside")
    rets = _cl.pct_change(fill_method=None)
    sig = rets.rolling(sigma_window, min_periods=max(2, sigma_window // 2)).std().shift(1)
    if p.amount is not None:
        amt = p.amount.reindex(columns=codes)
    else:
        vol = (p.volume.reindex(columns=codes) if p.volume is not None
               else pd.DataFrame(np.nan, index=p.close.index, columns=codes))
        amt = vol * p.close[codes]
    adv = amt.rolling(adv_window, min_periods=max(1, adv_window // 2)).mean().shift(1)
    for c in codes:
        out[c] = dict(
            close=p.close[c].astype(float).copy(),
            amount=amt[c].astype(float).copy(),
            adv=adv[c].astype(float).copy(),
            sigma=sig[c].astype(float).copy(),
        )
    return out


FACTOR_JUMP_TOL = 1e-3      # qlib 'factor' = adj_close/close carries ~1e-4 daily rounding noise
EVENT_FACTOR_MISMATCH = 0.01  # event-implied multiplier vs factor ratio; above this = special_reorg, the factor wins (Data rule 10-11)


def corporate_action_arrays(p: "ExecPanels", *, fallback: bool = True, tol: float = FACTOR_JUMP_TOL,
                            mismatch: float = EVENT_FACTOR_MISMATCH, flags: list | None = None):
    """(CD, SR, FR) numpy arrays aligned to p.close: per-share pre-tax cash, bonus ratio and a
    fallback share multiplier (factor ratio F[t]/F[t-1]) used where there is no per-event data.

    Per-event rows are cross-checked against the factor when both exist: if the event-implied
    total-return multiplier (1+ratio)*C_prev/(C_prev-cash) differs from the factor ratio by more
    than ``mismatch`` (e.g. bankruptcy-reorg transfers that go to investors, not holders) the
    event is dropped and the factor ratio is used (recorded in ``flags``)."""
    shape = p.close.shape
    CD = np.nan_to_num(p.cash_div.to_numpy(dtype=float)) if p.cash_div is not None else np.zeros(shape)
    SR = np.nan_to_num(p.share_ratio.to_numpy(dtype=float)) if p.share_ratio is not None else np.zeros(shape)
    # Panels arrive as float32 (0.1 -> 0.10000000149): strip that noise so bonus shares stay whole and
    # all three engines see identical per-event values (declared ratios/cash have <=6 decimals per share).
    CD = np.round(CD, 6); SR = np.round(SR, 6)
    FR = np.ones(shape)
    if p.adj_factor is not None:
        F = p.adj_factor.ffill().to_numpy(dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            r = F[1:] / F[:-1]
        ok = np.isfinite(r) & (r > 0)
        r = np.where(ok, r, 1.0)
        ev = (CD != 0) | (SR != 0)
        Cm = p.close.ffill().to_numpy(dtype=float)
        for t, j in zip(*np.nonzero(ev)):
            if t == 0 or not ok[t - 1, j] or not np.isfinite(Cm[t - 1, j]) or Cm[t - 1, j] <= CD[t, j]:
                continue
            m_e = (1 + SR[t, j]) * Cm[t - 1, j] / (Cm[t - 1, j] - CD[t, j])
            if abs(m_e / r[t - 1, j] - 1) > mismatch:
                if flags is not None:
                    flags.append(dict(date=str(p.close.index[t].date()), code=str(p.close.columns[j]),
                                      event_multiplier=float(m_e), factor_ratio=float(r[t - 1, j]),
                                      label="special_reorg", cash_div=float(CD[t, j]), share_ratio=float(SR[t, j])))
                CD[t, j] = 0.0; SR[t, j] = 0.0
        if fallback:
            FR[1:] = np.where(np.abs(r - 1) > tol, r, 1.0)
            FR[(CD != 0) | (SR != 0)] = 1.0
    return CD, SR, FR


def total_return_factor(p: "ExecPanels") -> pd.DataFrame:
    """Cumulative total-return factor implied by the corporate actions (event data, else adj_factor)
    on raw closes: each ex-date multiplies by (1+ratio)*C_prev/(C_prev - cash). For mark-to-close
    total-return series (adj_close = close * TRF) used by strategy_feed / research paths."""
    p = p.aligned()
    CD, SR, FR = corporate_action_arrays(p)
    Cm = p.close.ffill().to_numpy(dtype=float)
    step = np.ones_like(Cm)
    with np.errstate(divide="ignore", invalid="ignore"):
        ev = (1 + SR[1:]) * Cm[:-1] / (Cm[:-1] - CD[1:])
    ev = np.where(np.isfinite(ev) & (ev > 0), ev, 1.0)
    step[1:] = ev * FR[1:]
    return pd.DataFrame(np.cumprod(step, axis=0), index=p.close.index, columns=p.close.columns)


# ----------------------------------------------------------------- returns
def split_returns(open_: pd.DataFrame, close: pd.DataFrame):
    """Daily overnight (prev close -> open) and intraday (open -> close) returns.

    (1+overnight)*(1+intraday) == 1 + close_to_close exactly where both exist.
    Halted interior sessions: close/open carried from the last close, so the
    move lands on resumption (overnight leg)."""
    c = close.ffill(limit_area="inside")
    o = open_.where(close.notna()).fillna(c)  # halted day: open := carried close
    o = o.where(c.notna())
    overnight = o / c.shift(1) - 1.0
    intraday = c / o - 1.0
    return overnight, intraday


def forward_return_components(open_: pd.DataFrame, close: pd.DataFrame, session, horizon: int) -> dict:
    """Forward returns from signal close ``session`` over ``horizon`` sessions.

    Returns dict of {name: {code: ret}} with names ``cc`` (close->close),
    ``overnight`` (compounded prev-close->open legs), ``intraday`` (compounded
    open->close legs) and ``open_entry`` (T+1 open -> T+h close, the return
    tradable with a next_open fill). (1+overnight)(1+intraday) == 1+cc.
    Plug any component into ``v2_min_pipeline.cross_section_ic``."""
    on, intra = split_returns(open_, close)
    idx = close.index
    t = pd.Timestamp(session)
    pos = idx.searchsorted(t, side="right") - 1
    if pos < 0 or pos + horizon >= len(idx):
        return {k: {} for k in ("cc", "overnight", "intraday", "open_entry")}
    win = slice(pos + 1, pos + horizon + 1)
    ovn = (1 + on.iloc[win]).prod(min_count=horizon) - 1
    itr = (1 + intra.iloc[win]).prod(min_count=horizon) - 1
    c = close.ffill(limit_area="inside")
    cc = c.iloc[pos + horizon] / c.iloc[pos] - 1
    o1 = open_.iloc[pos + 1]
    oe = c.iloc[pos + horizon] / o1 - 1
    def d(s):
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        return {str(k): float(v) for k, v in s.items()}
    return {"cc": d(cc), "overnight": d(ovn), "intraday": d(itr), "open_entry": d(oe)}


# ----------------------------------------------------------------- engine
def _stamp(day, cfg):
    return cfg.stamp_before if day < STAMP_CUT else cfg.stamp_after


def run_weight_schedule(panels: ExecPanels, schedule: Mapping, *, initial_cash: float = 600_000.0,
                        config: ExecConfig | None = None, record_fills: bool = False,
                        record_weights: bool = True, futures=None, margin=None) -> dict:
    """Run a weight schedule through the platform engine.

    Order of a session t: (1) mark open -> ``nav_open``; (2) execute pending
    orders (sells first) at the mode's fill price; (3) mark close -> ``nav``;
    (4) if t is a signal day: new target quantities (locked at signal close
    NAV/close, lot rounded) replace all pending orders. ``fill='close'``
    executes the new orders immediately at that close.

    Returns dict: nav, nav_open (Series), costs breakdown, requested/filled
    notional, fill_ratio, events (list), fills (optional), and (when
    ``record_weights``) ``target_weights`` / ``actual_weights`` float32
    DataFrames (session x code). target_weights: the latest signal's weights,
    carried forward until the next signal (0 before the first signal).
    actual_weights: post-fill holdings at that session's close mark / nav.
    """
    cfg = config or ExecConfig()
    p = panels.aligned()
    dates, codes = p.close.index, list(p.close.columns)
    C = p.close.to_numpy()
    Cm = p.close.ffill(limit_area="inside").ffill().to_numpy().copy()  # marks
    O = p.open.to_numpy() if p.open is not None else C.copy()
    V = p.volume.to_numpy() if p.volume is not None else np.full_like(C, np.nan)
    if p.amount is not None:
        A = p.amount.to_numpy()
    else:
        A = V * C
    if cfg.fill == "next_vwap":
        if p.volume is None:
            raise ValueError("next_vwap needs volume (shares)")
        vw, _fb = vwap_panel(p.amount, p.volume, p.close, p.open, p.high, p.low)
        PX = vw.to_numpy()
        fallback_cells = int(_fb.to_numpy().sum())
    elif cfg.fill == "next_open":
        PX, fallback_cells = O, 0
    else:
        PX, fallback_cells = C, 0
    LU = p.limit_up.to_numpy() if p.limit_up is not None else np.full_like(C, np.nan)
    LD = p.limit_down.to_numpy() if p.limit_down is not None else np.full_like(C, np.nan)
    if cfg.derive_nonstock_limits and cfg.enforce_limits:
        LU = LU.copy(); LD = LD.copy()
        prev = np.vstack([np.full((1, C.shape[1]), np.nan), p.close.ffill().to_numpy()[:-1]])
        for j, c in enumerate(codes):
            if instrument_type(c) == "stock":
                continue
            for t, day in enumerate(dates):
                pct = derived_limit_pct(c, day)
                if pct is None or not np.isfinite(prev[t, j]):
                    continue
                if not np.isfinite(LU[t, j]):
                    LU[t, j] = prev[t, j] * (1 + pct)
                if not np.isfinite(LD[t, j]):
                    LD[t, j] = prev[t, j] * (1 - pct)
    TP = p.terminal_price.to_numpy() if p.terminal_price is not None else None
    if p.suspended is not None:
        SUS = p.suspended.to_numpy() | ~np.isfinite(C)
    else:
        SUS = ~np.isfinite(C) | (np.isfinite(V) & (V <= 0))
    use_ca = bool(cfg.corporate_actions)
    ca_flags: list = []
    CD, SR, FR = corporate_action_arrays(p, flags=ca_flags) if use_ca else (None, None, None)
    _cl = p.close.ffill(limit_area="inside")
    if use_ca and (p.cash_div is not None or p.share_ratio is not None or p.adj_factor is not None):
        _cl = _cl * total_return_factor(p)   # sigma on total-return closes (no fake ex-date moves)
    rets = _cl.pct_change(fill_method=None)
    SIG = rets.rolling(cfg.sigma_window, min_periods=max(2, cfg.sigma_window // 2)).std().shift(1).to_numpy()
    amt_df = pd.DataFrame(A, index=dates, columns=codes)
    ADV = amt_df.rolling(cfg.adv_window, min_periods=max(1, cfg.adv_window // 2)).mean().shift(1).to_numpy()
    free = {i for i, c in enumerate(codes) if c in cfg.no_limit_codes}
    TICK = [resolve_tick(c, cfg.price_tick) for c in codes]
    EXEMPT = [stamp_exempt(c) for c in codes]
    IS_CB = [is_exchange_bond(c) for c in codes]   # CB + EB share cb_commission
    COMM = [cfg.cb_commission if (cb and (cfg.commission or cfg.min_commission)) else cfg.commission for cb in IS_CB]
    MINC = [cfg.cb_min_commission if (cb and (cfg.commission or cfg.min_commission)) else cfg.min_commission for cb in IS_CB]
    TICK_LIM = [tick_for_code(c) for c in codes]
    KJ = np.full(len(codes), float(cfg.impact_k))
    if cfg.impact_k_by_bucket and cfg.size_bucket:
        for i, c in enumerate(codes):
            b = cfg.size_bucket.get(c)
            if b is not None and b in cfg.impact_k_by_bucket:
                KJ[i] = float(cfg.impact_k_by_bucket[b])
    ENH = np.full(len(dates), np.nan)
    col = {c: i for i, c in enumerate(codes)}
    signals = {pd.Timestamp(k).normalize(): v for k, v in schedule.items()}

    shares = np.zeros(len(codes))
    cash = float(initial_cash)
    pending: dict[int, float] = {}
    nav_out = np.empty(len(dates)); navo_out = np.empty(len(dates))
    cost = dict(commission=0.0, stamp=0.0, slippage=0.0, impact=0.0)
    requested = filled = 0.0
    events, fills = [], []
    impact_missing = 0
    TW = np.zeros((len(dates), len(codes)), dtype=np.float32) if record_weights else None
    AW = np.zeros((len(dates), len(codes)), dtype=np.float32) if record_weights else None
    cur_tw = np.zeros(len(codes), dtype=np.float32)
    reserve = [0.0]   # cash encumbered as futures margin (stock buys cannot use it)
    from quantlab.platform.futures import FuturesBook, cash_rate_per_session
    RATE = cash_rate_per_session(dates, cfg.cash_rate, cfg.cash_rate_convention, cfg.cash_rate_kind,
                                 cfg.cash_rate_day_count) if cfg.cash_rate is not None else None
    interest_total = 0.0
    interest_series = np.zeros(len(dates)) if RATE is not None else None
    fb = FuturesBook(futures, dates, events) if futures is not None else None
    fut_roots = set(fb.roots) if fb is not None else set()
    credit = [0.0]   # margin account: extra buying power beyond cash - reserve
    mb = None
    if margin is not None:
        from quantlab.platform.margin import MarginBook
        mb = MarginBook(margin, dates, codes, events)
    liq_pending: set = set()

    def execute(t, day, mode_px):
        nonlocal cash, filled, impact_missing
        done = {}
        # Code-sorted fill order: independent of panel column index / width (NAV-gap fix).
        for side in (-1, 1):
            for j in sorted(pending.keys(), key=lambda i: codes[i]):
                rem = pending.get(j)
                if rem is None or rem == 0 or np.sign(rem) != side:
                    continue
                code = codes[j]
                px0 = mode_px[t, j]
                if SUS[t, j] or not np.isfinite(px0) or px0 <= 0:
                    events.append(dict(date=str(day.date()), code=code, side=side, reason="suspended"))
                    continue
                eps = LIMIT_EPS if TICK_LIM[j] >= 0.01 else 0.0005
                if cfg.enforce_limits and j not in free:
                    if side > 0 and np.isfinite(LU[t, j]) and px0 >= LU[t, j] - eps:
                        events.append(dict(date=str(day.date()), code=code, side=side, reason="limit_up")); continue
                    if side < 0 and np.isfinite(LD[t, j]) and px0 <= LD[t, j] + eps:
                        events.append(dict(date=str(day.date()), code=code, side=side, reason="limit_down")); continue
                qty = abs(rem)
                if cfg.participation_cap is not None:
                    vol = V[t, j]
                    cap = vol * cfg.participation_cap if np.isfinite(vol) else 0.0
                    if cap < qty:
                        events.append(dict(date=str(day.date()), code=code, side=side, reason="participation_cap",
                                           wanted=qty, cap=cap))
                    qty = min(qty, cap)
                px = round_to_tick(px0 * (1 + side * cfg.slippage), TICK[j])
                if side < 0:
                    qty = min(qty, shares[j])
                    if cfg.lots:
                        qty = round_order_quantity(code, qty, -1, holding=shares[j])
                else:
                    unit = px * (1 + COMM[j])
                    afford = max(cash - reserve[0] + credit[0] - MINC[j], 0.0) / unit
                    qty = min(qty, afford)
                    if cfg.lots:
                        qty = round_order_quantity(code, qty, 1)
                if qty <= 0:
                    continue
                notional = qty * px
                comm = max(MINC[j], notional * COMM[j]) if COMM[j] or MINC[j] else 0.0
                stamp = notional * _stamp(day, cfg) if side < 0 and not EXEMPT[j] else 0.0
                imp = 0.0
                if KJ[j]:
                    if not (np.isfinite(ADV[t, j]) and ADV[t, j] > 0 and np.isfinite(SIG[t, j])):
                        impact_missing += 1
                    imp = float(sqrt_impact_cost(qty * px0, ADV[t, j], SIG[t, j], KJ[j]))
                if side > 0:
                    while qty > 0 and notional + comm + imp > cash - reserve[0] + credit[0] + 1e-9:
                        step = lot_rule_for(code).step if cfg.lots else 1
                        qty -= step
                        if cfg.lots and qty < lot_rule_for(code).minimum:
                            qty = 0
                        notional = qty * px
                        comm = max(MINC[j], notional * COMM[j]) if (COMM[j] or MINC[j]) and qty else 0.0
                        imp = float(sqrt_impact_cost(qty * px0, ADV[t, j], SIG[t, j], KJ[j])) if KJ[j] else 0.0
                    if qty <= 0:
                        continue
                cash -= side * notional + comm + stamp + imp
                shares[j] += side * qty
                cost["commission"] += comm; cost["stamp"] += stamp; cost["impact"] += imp
                cost["slippage"] += abs(px - px0) * qty
                filled += qty * px0
                done[j] = qty
                pending[j] = rem - side * qty
                if abs(pending[j]) < 1e-9:
                    pending.pop(j)
                if record_fills:
                    fills.append(dict(date=str(day.date()), code=code, side=side, qty=qty, price=px, ref_price=px0,
                                      commission=comm, stamp=stamp, impact=imp))
        if cfg.unfilled == "drop":
            for j in list(pending):
                events.append(dict(date=str(day.date()), code=codes[j], reason="dropped_unfilled", remaining=pending[j]))
            pending.clear()

    marks_open = np.where(np.isfinite(O), O, Cm)
    ca_cash = 0.0; ca_events = 0
    term_cash_total = [0.0]
    for t, day in enumerate(dates):
        if RATE is not None and t > 0:
            idle = max(cash - (fb.margin if fb is not None else 0.0), 0.0)
            it = idle * RATE[t]
            cash += it; interest_total += it; interest_series[t] = it
        if mb is not None:
            cash += mb.accrue(t, cash)
        if fb is not None:
            fb.start(t)
        if use_ca and t > 0:
            for j in np.flatnonzero(shares > 0):
                cd, sr, fr = CD[t, j], SR[t, j], FR[t, j]
                if cd == 0 and sr == 0 and fr == 1.0:
                    continue
                q0 = shares[j]
                if cd:
                    amt = q0 * cd * (1.0 - cfg.dividend_tax)
                    cash += amt; ca_cash += amt
                mult = (1.0 + sr) * fr
                shares[j] = q0 * mult
                if j in pending:
                    pending[j] *= mult
                ca_events += 1
                events.append(dict(date=str(day.date()), code=codes[j], reason="corporate_action",
                                   cash_per_share=float(cd), share_ratio=float(sr), factor_ratio=float(fr), shares_before=float(q0)))
        if TP is not None:
            for j in np.flatnonzero(np.isfinite(TP[t]) & (shares > 0)):
                amt = shares[j] * TP[t, j]
                cash += amt; term_cash_total[0] += amt
                events.append(dict(date=str(day.date()), code=codes[j], reason="terminal_payout",
                                   price=float(TP[t, j]), shares=float(shares[j]), cash=float(amt)))
                shares[j] = 0.0
                pending.pop(j, None)
                Cm[t:, j] = np.nan   # no further marks after payout
        prev_mark = Cm[t - 1] if t else Cm[t]
        mo = np.where(np.isfinite(marks_open[t]) & ~SUS[t], marks_open[t], np.where(np.isfinite(Cm[t]), Cm[t], prev_mark))
        navo_out[t] = cash + float(np.nansum(shares * np.nan_to_num(mo)))
        if fb is not None:
            navo_out[t] += fb.unrealized(t, fb.O[t])
            if cfg.fill != "close":
                cash += fb.trade(t, fb.O, cash)
            reserve[0] = fb.margin_req(t, fb.O[t] if cfg.fill != "close" else None)
        if mb is not None:
            credit[0] = mb.credit(navo_out[t], cash)
        if cfg.fill != "close" and pending:
            execute(t, day, PX)
            if liq_pending:
                liq_pending.clear()
        if fb is not None:
            cash += fb.settle(t, cash, cash + float(np.nansum(shares * np.nan_to_num(Cm[t]))), credit=credit[0])
            reserve[0] = fb.margin
        w = signals.get(day)
        if w is not None and fb is not None:
            fw = {k: float(v) for k, v in w.items() if k in fut_roots}
            w = {k: v for k, v in w.items() if k not in fut_roots}
        if w is not None:
            nav_sig = cash + float(np.nansum(shares * np.nan_to_num(Cm[t])))
            if fb is not None:
                fb.signal(t, fw, nav_sig)
                if cfg.fill == "close":
                    cash += fb.trade(t, fb.S, cash)
                    cash += fb.settle(t, cash, nav_sig, credit=credit[0])
                    reserve[0] = fb.margin
            pending = {}
            tgt = {col[c]: float(x) for c, x in w.items() if c in col and x > 0}
            if record_weights:
                cur_tw = np.zeros(len(codes), dtype=np.float32)
                for j, x in tgt.items():
                    cur_tw[j] = x
            # Stable code order (not set/hash or column-index order) so full vs schedule-only
            # panels produce the same cash-constrained fill sequence for the same names.
            for j in sorted(set(np.flatnonzero(shares > 0)) | set(tgt), key=lambda i: codes[i]):
                ref = Cm[t, j]
                if not np.isfinite(ref) or ref <= 0:
                    continue
                desired = tgt.get(j, 0.0) * nav_sig / ref
                if j in tgt and cfg.lots and cfg.order_rounding == "target" and np.isclose(desired, shares[j], rtol=1e-12, atol=1e-8):
                    desired = shares[j]   # unchanged holding (incl. odd lots) stays (Ledger)
                elif j in tgt and cfg.lots and cfg.order_rounding == "delta":
                    raw = desired - shares[j]
                    step = lot_rule_for(codes[j]).step if lot_rule_for(codes[j]).step > 1 else 1
                    raw = np.floor(raw / step + 1e-9) * step if raw > 0 else np.ceil(raw / step - 1e-9) * step
                    desired = shares[j] + raw
                elif j in tgt and cfg.lots:
                    rule = lot_rule_for(codes[j])
                    # Ledger: floor the TARGET holding to the step only; board minima apply to the
                    # order (round_order_quantity at fill), so e.g. STAR 430 -> 190 sells 240 (legal).
                    units = desired / rule.step
                    if abs(units - round(units)) <= 1e-10:
                        units = round(units)
                    desired = np.floor(units) * rule.step
                delta = desired - shares[j]
                if abs(delta) < 1e-9:
                    continue
                if abs(delta) * ref < cfg.min_trade_value and j in tgt:
                    continue
                pending[j] = delta
                requested += abs(delta) * ref
            if cfg.fill == "close":
                execute(t, day, PX)
                if cfg.unfilled == "carry":
                    pass  # remaining orders retry at later closes until next signal
        elif cfg.fill == "close" and pending:
            execute(t, day, PX)
        nav_out[t] = cash + float(np.nansum(shares * np.nan_to_num(Cm[t])))
        if fb is not None:
            nav_out[t] += fb.unrealized(t, fb.S[t])   # nonzero only for contracts without a settle that day
        if mb is not None:
            forced = mb.check(t, cash, shares, Cm[t], nav_out[t])
            if forced:   # forced pro-rata selling replaces all pending stock orders (next session's fill)
                pending = {j: -q for j, q in forced.items()}
                liq_pending = set(forced)
                if cfg.fill == "close":
                    execute(t, day, PX)
                    nav_out[t] = cash + float(np.nansum(shares * np.nan_to_num(Cm[t])))
                    if fb is not None:
                        nav_out[t] += fb.unrealized(t, fb.S[t])
        if nav_out[t] > 0:
            _w = shares * np.nan_to_num(Cm[t]) / nav_out[t]
            _s2 = float(np.sum(_w * _w))
            ENH[t] = 1.0 / _s2 if _s2 > 0 else np.nan
        if record_weights:
            TW[t] = cur_tw
            if nav_out[t] > 0:
                AW[t] = (shares * np.nan_to_num(Cm[t]) / nav_out[t]).astype(np.float32)
    nav = pd.Series(nav_out, index=dates)
    total_cost = sum(cost.values())
    enh = pd.Series(ENH, index=dates, name="effective_n_holdings")
    extra = {}
    if RATE is not None:
        extra.update(cash_interest=interest_total, cash_interest_daily=pd.Series(interest_series, index=dates))
    if fb is not None:
        extra.update(fb.report())
    if mb is not None:
        extra.update(mb.report())
    return dict(**extra,
                effective_n=enh, effective_n_mean=float(enh.mean()) if enh.notna().any() else float("nan"),
                impact_bp_per_traded=(cost["impact"] / filled * 1e4) if filled > 0 else float("nan"),
                nav=nav, nav_open=pd.Series(navo_out, index=dates), costs=cost, total_cost=total_cost,
                requested_notional=requested, filled_notional=filled,
                fill_ratio=(filled / requested) if requested > 0 else np.nan,
                final_shares={codes[j]: float(shares[j]) for j in np.flatnonzero(shares)},
                cash=cash, events=events, fills=fills, vwap_fallback_cells=fallback_cells,
                impact_missing_fills=impact_missing, config=cfg,
                terminal_payout_cash=term_cash_total[0],
                corporate_action_cash=ca_cash, corporate_action_events=ca_events, corporate_action_flags=ca_flags,
                target_weights=None if TW is None else pd.DataFrame(TW, index=dates, columns=codes),
                actual_weights=None if AW is None else pd.DataFrame(AW, index=dates, columns=codes))


# ----------------------------------------------------------------- capacity
def capacity_curve(panels: ExecPanels, schedule: Mapping, capitals: Sequence[float] = (500_000, 2_000_000, 10_000_000),
                   config: ExecConfig | None = None) -> pd.DataFrame:
    """Same schedule at several capital levels. Columns: capital, net_return,
    zero_cost_return, cost_drag (= zero_cost_return - net_return, same fills
    rules), cost_cny, fill_ratio. Default config: next_open, sqrt impact k=1,
    10% participation cap."""
    cfg = config or ExecConfig(fill="next_open", impact_k=1.0, participation_cap=0.10, slippage=0.0)
    zero = replace(cfg, **ZERO_COST)
    rows = []
    for cap in capitals:
        r = run_weight_schedule(panels, schedule, initial_cash=float(cap), config=cfg, record_weights=False)
        z = run_weight_schedule(panels, schedule, initial_cash=float(cap), config=zero, record_weights=False)
        net = r["nav"].iloc[-1] / cap - 1
        zr = z["nav"].iloc[-1] / cap - 1
        rows.append(dict(capital=float(cap), net_return=float(net), zero_cost_return=float(zr),
                         cost_drag=float(zr - net), cost_cny=float(r["total_cost"]),
                         fill_ratio=float(r["fill_ratio"]),
                         impact_cny=float(r["costs"]["impact"]),
                         impact_bp_per_traded=float(r["impact_bp_per_traded"]),
                         effective_n_mean=float(r["effective_n_mean"])))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- reconciliation
def _diff_report(base: pd.Series, other: pd.Series, tol: float) -> dict:
    a, b = base.align(other, join="inner")
    d = (b - a)
    rel = d / a
    bad = rel.abs() > tol
    first = rel.index[bad.to_numpy()][0] if bad.any() else None
    return dict(per_day_diff=d, max_abs_diff=float(d.abs().max()) if len(d) else 0.0,
                max_abs_rel_diff=float(rel.abs().max()) if len(d) else 0.0,
                first_divergence=None if first is None else str(pd.Timestamp(first).date()))


def _ledger_actions(p: "ExecPanels", dividend_tax: float = 0.0) -> pd.DataFrame:
    """Per-event panels -> Ledger action rows (record date = prior session, paid/listed on ex-date,
    known before the open). Factor-only fallback events are NOT representable in the Ledger."""
    CD, SR, _ = corporate_action_arrays(p, fallback=False)
    idx, cols = p.close.index, list(p.close.columns)
    rows = []
    for t, j in zip(*np.nonzero((CD != 0) | (SR != 0))):
        if t == 0:
            continue
        ex = str(idx[t].date()); rec = str(idx[t - 1].date())
        rows.append(dict(action_id=f"{cols[j]}:{ex}", instrument_id=cols[j], ex_date=ex, record_date=rec,
                         pay_date=ex, share_date=ex, available_at=rec + " 18:00:00+08:00", action_type="distribution",
                         tax_policy="net_fixed", cash_per_share=float(CD[t, j]) * (1 - dividend_tax),
                         share_ratio=round(float(SR[t, j]), 6)))  # panels are float32: 0.1 -> 0.10000000149 made Ledger reject the whole action as fractional
    return pd.DataFrame(rows, columns=["action_id", "instrument_id", "ex_date", "record_date", "pay_date", "share_date",
                                       "available_at", "action_type", "tax_policy", "cash_per_share", "share_ratio"])


def _ledger_nav(panels: ExecPanels, schedule, initial_cash, price_tick="auto", corporate_actions: bool = True,
                dividend_tax: float = 0.0):
    from quantlab.backtest.ledger import Ledger
    from quantlab.data.contracts import InstrumentRules
    p = panels.aligned()
    codes = list(p.close.columns)
    rules = {}
    for c in codes:
        lr = lot_rule_for(c)
        kind = instrument_type(c)
        rules[c] = InstrumentRules(c, {"fund": "equity_etf", "cb": "convertible_bond", "eb": "convertible_bond"}.get(kind, "stock"), lr.step, lr.step, 1,
                                   tick_for_code(c) if price_tick == "auto" else float(price_tick or 0.01), 0.0, 0.0, None,
                                   min_buy_quantity=lr.minimum, min_sell_quantity=lr.minimum)
    led = Ledger(cash=initial_cash, slippage=0.0, cash_buffer=0.0, participation=1.0, cost_mult=0.0,
                 min_trade_value=0.0)
    O = p.open if p.open is not None else p.close
    signals = {pd.Timestamp(k).normalize(): v for k, v in schedule.items()}
    actions = _ledger_actions(p, dividend_tax) if corporate_actions else None
    cal = p.close.index
    out = []
    for s, day in enumerate(p.close.index):
        ds = str(day.date())
        if actions is not None and not actions.empty:
            led.corporate_actions(ds, s, actions, cal)
        bars = {}
        for c in codes:
            o = O.at[day, c]
            bars[c] = {"open": float(o) if pd.notna(o) and pd.notna(p.close.at[day, c]) else np.nan,
                       "open_status": "trading" if pd.notna(p.close.at[day, c]) else "halted",
                       "open_status_available_at": ds + " 09:25:00",
                       "limit_up": np.nan, "limit_down": np.nan}
        led.execute(ds, s, bars, rules, {c: 1e18 for c in codes})
        closes = {c: float(v) for c, v in p.close.loc[day].items() if pd.notna(v)}
        led.close(ds, s, closes)
        if day in signals:
            led.queue_targets({c: float(w) for c, w in signals[day].items() if w > 0}, ds, "rebalance", rules)
        out.append(led.nav())
    return pd.Series(out, index=p.close.index)


def _fastsim_nav(panels: ExecPanels, schedule, initial_cash, order_rounding: str = "target",
                 price_tick="auto", corporate_actions: bool = True, dividend_tax: float = 0.0,
                 cash_rate=None, cash_rate_convention: str = "act365", cash_rate_kind: str = "annual",
                 cash_rate_day_count=None):
    from quantlab.smallcap.sim import Costs, Market, simulate
    from quantlab.platform.futures import cash_rate_per_session
    p = panels.aligned()
    C = p.close.to_numpy()
    O = (p.open if p.open is not None else p.close).to_numpy()
    nanm = np.full_like(C, np.nan)
    if corporate_actions:
        CD, SR, FR = corporate_action_arrays(p)
        fac = np.cumprod(FR, axis=0)   # fallback-only factor; per-event cash/bonus handled explicitly
    else:
        CD = SR = None; fac = np.ones_like(C)
    m = Market(p.close.index, p.close.columns, O, C, fac, nanm, nanm.copy(),
               np.full_like(C, np.inf), cash_div=CD, share_ratio=SR,
               terminal_price=None if p.terminal_price is None else p.terminal_price.to_numpy(dtype=float))
    costs = Costs(slippage=0.0, commission=0.0, min_commission=0.0, stamp_before=0.0, stamp_after=0.0,
                  min_trade_value=0.0, participation=np.inf, multiplier=0.0, cash_buffer=0.0, gross_cap=1.0,
                  order_rounding=order_rounding, price_tick=price_tick, dividend_tax=dividend_tax,
                  cash_rate_per_session=None if cash_rate is None else cash_rate_per_session(
                      p.close.index, cash_rate, cash_rate_convention, cash_rate_kind, cash_rate_day_count))
    return simulate(m, schedule, initial_cash=initial_cash, costs=costs)["nav"]


def reconcile_zero_cost(panels: ExecPanels, schedule: Mapping, *, initial_cash: float = 600_000.0,
                        paper_nav: pd.Series | None = None, tol: float = 1e-9,
                        engines: Sequence[str] = ("platform", "ledger", "fastsim"),
                        corporate_actions: bool = True) -> dict:
    """Run the same weights with all costs/limits/caps off through the platform
    engine (next_open, lots on, per-code tick 'auto', order_rounding='target'), backtest
    Ledger and smallcap fast sim (target rounding, per-code tick + board lots). Legacy delta
    rounding is also run for both platform and fast sim.
    ``paper_nav`` (optional) may be a level series or unit NAV; it is rescaled
    to ``initial_cash`` at its first point. Reports per-day diffs vs the
    platform engine, first divergence day (|rel diff|>tol), max abs diff."""
    base_cfg = ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None, price_tick="auto",
                          order_rounding="target", corporate_actions=bool(corporate_actions), **ZERO_COST)
    navs = {}
    if "platform" in engines:
        navs["platform"] = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=base_cfg)["nav"]
        navs["platform_delta_rounding"] = run_weight_schedule(
            panels, schedule, initial_cash=initial_cash, config=replace(base_cfg, order_rounding="delta"),
            record_weights=False)["nav"]
    if "ledger" in engines:
        navs["ledger"] = _ledger_nav(panels, schedule, initial_cash, corporate_actions=corporate_actions)
    if "fastsim" in engines:
        navs["fastsim"] = _fastsim_nav(panels, schedule, initial_cash, corporate_actions=corporate_actions)
        navs["fastsim_delta_rounding"] = _fastsim_nav(panels, schedule, initial_cash, order_rounding="delta",
                                                      corporate_actions=corporate_actions)
    if paper_nav is not None:
        pn = paper_nav.copy(); pn.index = pd.to_datetime(pn.index)
        navs["paper"] = pn / pn.iloc[0] * initial_cash
    ref_name = next(iter(navs))
    report = {name: _diff_report(navs[ref_name], s, tol) for name, s in navs.items() if name != ref_name}
    # legacy like-for-like: delta rounding in both engines (old fast-sim behaviour).
    if "fastsim_delta_rounding" in navs and "platform_delta_rounding" in navs:
        report["fastsim_vs_platform_delta_rounding"] = _diff_report(navs["platform_delta_rounding"],
                                                                    navs["fastsim_delta_rounding"], tol)
    return dict(reference=ref_name, navs=pd.DataFrame(navs), diffs=report)


def cost_ladder(panels: ExecPanels, schedule: Mapping, *, initial_cash: float = 600_000.0,
                base: ExecConfig | None = None,
                items: Mapping[str, dict] | None = None) -> pd.DataFrame:
    """Start from zero cost, enable one item at a time. Default items:
    commission(+5 CNY min), stamp, slippage 10bp, sqrt impact k=1,
    participation cap 10%, limits, lots. Columns: item, final_nav, delta_vs_zero
    (CNY), delta_rel, cost_cny, fill_ratio, first_divergence."""
    zero = base or ExecConfig(fill="next_open", enforce_limits=False, participation_cap=None, lots=False, **ZERO_COST)
    items = items or {
        "commission": dict(commission=0.00025, min_commission=5.0),
        "stamp": dict(stamp_before=0.001, stamp_after=0.0005),
        "slippage_10bp": dict(slippage=0.001),
        "sqrt_impact_k1": dict(impact_k=1.0),
        "participation_10pct": dict(participation_cap=0.10),
        "limits": dict(enforce_limits=True),
        "lots": dict(lots=True),
    }
    z = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=zero)
    rows = [dict(item="zero_cost", final_nav=float(z["nav"].iloc[-1]), delta_vs_zero=0.0, delta_rel=0.0,
                 cost_cny=0.0, fill_ratio=float(z["fill_ratio"]), first_divergence=None,
                 impact_bp_per_traded=float(z["impact_bp_per_traded"]), effective_n_mean=float(z["effective_n_mean"]))]
    for name, kw in items.items():
        r = run_weight_schedule(panels, schedule, initial_cash=initial_cash, config=replace(zero, **kw))
        rep = _diff_report(z["nav"], r["nav"], 1e-12)
        rows.append(dict(item=name, final_nav=float(r["nav"].iloc[-1]),
                         delta_vs_zero=float(r["nav"].iloc[-1] - z["nav"].iloc[-1]),
                         delta_rel=float(r["nav"].iloc[-1] / z["nav"].iloc[-1] - 1),
                         cost_cny=float(r["total_cost"]), fill_ratio=float(r["fill_ratio"]),
                         first_divergence=rep["first_divergence"],
                         impact_bp_per_traded=float(r["impact_bp_per_traded"]),
                         effective_n_mean=float(r["effective_n_mean"])))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- loader
def _extend_fund_panel(iid: str, fr, roots, diag: dict):
    """Exchange funds (sh.510300): the merged D0+asof_extend reader stops at the
    D0/extend cut (2026-06-30). Append the accepted ETF panel
    (``roots.etf_panel_path``: OHLC tencent, amount CNY, volume in LOTS, matches
    Tushare fund_daily exactly) for sessions after the merged frame. Volume
    stays in lots here; the loader's amount/(volume*close) inference scales x100."""
    if not is_exchange_fund(iid):
        return fr
    path = Path(getattr(roots, "etf_panel_path", "") or "")
    if not path.is_file():
        return fr
    ep = pd.read_parquet(path)
    if "instrument_id" in ep.columns:
        ep = ep[ep["instrument_id"].astype(str) == iid]
    if ep.empty or "event_time" not in ep.columns:
        return fr
    ep_et = pd.to_datetime(ep["event_time"])
    if getattr(ep_et.dt, "tz", None) is not None:
        ep_et = ep_et.dt.tz_localize(None)
    ep = ep.assign(event_time=ep_et.dt.normalize())
    if fr is not None and not fr.empty:
        last = pd.to_datetime(fr["event_time"]).dt.tz_localize(None).dt.normalize().max() \
            if getattr(pd.to_datetime(fr["event_time"]).dt, "tz", None) is not None \
            else pd.to_datetime(fr["event_time"]).dt.normalize().max()
        ep = ep[ep["event_time"] > last]
        if ep.empty:
            return fr
        fr = pd.concat([fr, ep[[c for c in ep.columns if c in fr.columns]]], ignore_index=True)
    else:
        fr = ep
    diag.setdefault("fund_panel_extended", {})[iid] = dict(
        rows=int(len(ep)), first=str(ep["event_time"].min().date()), last=str(ep["event_time"].max().date()),
        source=str(path))
    return fr


def load_execution_panels(instrument_ids: Sequence[str], start, end, *, roots=None,
                          dtype: str = "float32", corporate_actions: bool = True,
                          fund_adj_factor_actions: bool = True) -> tuple[ExecPanels, dict]:
    """Wide OHLCV/limit panels from the merged D0+asof_extend reader for a
    SMALL id list (one instrument at a time; float32).

    Volume is always returned in **shares**. Priority per cell:
      1. ``volume_shares`` column when present (legacy ``asof_extend_202610``);
      2. ``volume`` scaled by ``volume_unit`` (``lot`` / ``lot_100sh`` / ``手`` → ×100;
         ``share`` / ``股`` → ×1);
      3. else infer from ``amount/(volume*close)`` (~100 → lots, ~1 → shares);
         missing amount → instrument neighbour scale, else 100 after D0 cutoff
         (legacy extend lots) and 1 before (D0 shares).

    Amount is **CNY** as landed. Default merge root is accepted
    ``asof_extend_tushare_202610`` (volume already shares, amount CNY; see
    ENG_PING ``units_note``). Returns ``(panels, diagnostics)``.

    Bonds (CB + EB) are read from ``data/v2/cb/cb_daily.parquet`` and exchange funds absent from the
    merged reader from ``data/v2/etf/etf_daily_adj.parquet`` (old per-day raw dirs = fallback). All
    trading/valuation uses RAW prices. ``fund_adj_factor_actions=True`` (default since 2026-10-11 post
    factor rebuild): ETF corporate actions for ALL exchange funds (incl. merged-reader 510300) use
    Tushare ``fund_adj`` (etf_daily_adj.adj_factor) as the factor and ``fund_div`` (implemented, deduped)
    for the per-unit cash amount, its ex-date aligned to the actual fund_adj jump session; factor
    fallback otherwise. ``False`` reproduces the pre-rebuild behaviour (fund factor dropped; merged-reader
    funds use the merged ``factor`` column). Stocks always use the rebuilt merged ``factor`` column
    (Tushare adj_factor), never ``factor_d0_orig``.
    """
    from quantlab.data.v2_readers import default_v2_roots, load_merged_panel, resolve_d0_asof_cutoff
    roots = roots or default_v2_roots()
    cutoff = pd.Timestamp(resolve_d0_asof_cutoff(roots.asof_extend_dir, roots=roots))
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    fields = ("open", "high", "low", "close", "volume", "amount", "limit_up", "limit_down")
    cols = {f: {} for f in fields}
    sus = {}
    diag = dict(
        d0_cutoff=str(cutoff.date()),
        asof_extend_dir=str(Path(roots.asof_extend_dir).resolve()),
        amount_missing_cells=0,
        volume_scale_fallback_cells=0,
        volume_shares_cells=0,
        volume_unit_scaled_cells=0,
        missing_ids=[],
        units_note="prefer asof_extend_tushare (shares+CNY); honor volume_shares/volume_unit when present",
    )
    facs = {}
    cb_ids = [str(i) for i in instrument_ids if is_exchange_bond(str(i))]
    nonstd: dict = {}
    if cb_ids:
        nonstd["cb"] = load_cb_panels(cb_ids, lo, hi, dtype=dtype, diag=diag)
    instrument_ids = [i for i in instrument_ids if str(i) not in set(cb_ids)]
    fund_fallback = []
    for iid in instrument_ids:
        if is_exchange_fund(str(iid)):
            _probe = load_merged_panel(str(iid), roots=roots).frame
            if _probe is None or _probe.empty:
                fund_fallback.append(str(iid))
    if fund_fallback:
        nonstd["fund"] = load_fund_daily_panels(fund_fallback, lo, hi, dtype=dtype, diag=diag)
        if not fund_adj_factor_actions:
            nonstd["fund"].pop("adj_factor", None)
            diag["fund_adj_factor_actions"] = "off (default; Data verifying etf_daily_adj adj_factor)"
        instrument_ids = [i for i in instrument_ids if str(i) not in set(fund_fallback)]
    for iid in instrument_ids:
        fr = load_merged_panel(str(iid), roots=roots).frame
        fr = _extend_fund_panel(str(iid), fr, roots, diag)
        if corporate_actions and fr is not None and not fr.empty and "factor" in fr.columns:
            _f = pd.Series(pd.to_numeric(fr["factor"], errors="coerce").to_numpy(dtype=float),
                           index=pd.to_datetime(fr["event_time"]).dt.tz_localize(None).dt.normalize()
                           if getattr(pd.to_datetime(fr["event_time"]).dt, "tz", None) is not None
                           else pd.to_datetime(fr["event_time"]).dt.normalize())
            facs[str(iid)] = _f[~_f.index.duplicated(keep="last")]
        if fr is None or fr.empty:
            diag["missing_ids"].append(str(iid)); continue
        et = pd.to_datetime(fr["event_time"]).dt.normalize()
        fr = fr.assign(_et=et).loc[(et >= lo) & (et <= hi)].drop_duplicates("_et", keep="last").set_index("_et")
        num = {f: pd.to_numeric(fr[f], errors="coerce") if f in fr else pd.Series(np.nan, index=fr.index) for f in fields}
        vol_shares = None
        if "volume_shares" in fr.columns:
            vs = pd.to_numeric(fr["volume_shares"], errors="coerce")
            if vs.notna().any():
                vol_shares = vs
                diag["volume_shares_cells"] += int(vs.notna().sum())
        if vol_shares is None and "volume_unit" in fr.columns:
            unit = fr["volume_unit"].astype(str).str.lower()
            scale_u = pd.Series(np.nan, index=fr.index, dtype=float)
            lot_mask = unit.str.contains("lot|手", regex=True, na=False)
            share_mask = unit.str.contains("share|股", regex=True, na=False) & ~lot_mask
            scale_u = scale_u.where(~lot_mask, 100.0).where(~share_mask, 1.0)
            if scale_u.notna().any():
                vol_shares = num["volume"] * scale_u
                diag["volume_unit_scaled_cells"] += int(scale_u.notna().sum())
        if vol_shares is None:
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = num["amount"] / (num["volume"] * num["close"])
            scale = pd.Series(np.where(ratio > 10, 100.0, np.where(ratio > 0, 1.0, np.nan)), index=fr.index)
            miss = scale.isna()
            diag["volume_scale_fallback_cells"] += int(miss.sum())
            default = pd.Series(np.where(fr.index > cutoff, 100.0, 1.0), index=fr.index)
            scale = scale.fillna(default)
            vol_shares = num["volume"] * scale
        num["volume"] = vol_shares
        diag["amount_missing_cells"] += int((num["amount"].isna() | (num["amount"] <= 0)).sum())
        for f in fields:
            cols[f][str(iid)] = num[f].astype(dtype)
        if "open_status" in fr:
            sus[str(iid)] = fr["open_status"].astype(str).isin(["halted", "suspended"])
    frames = {f: pd.DataFrame(v).sort_index() for f, v in cols.items()}
    extra_af, extra_tp = [], []
    for kind, pan in nonstd.items():
        if not pan:
            continue
        for f in fields:
            if f in pan:
                frames[f] = pd.concat([frames[f], pan[f]], axis=1).sort_index() if not frames[f].empty else pan[f]
            elif f in ("limit_up", "limit_down"):
                blank = pan["close"] * np.nan
                frames[f] = pd.concat([frames[f], blank], axis=1).sort_index() if not frames[f].empty else blank
        if "adj_factor" in pan:
            extra_af.append(pan["adj_factor"])
        if "terminal_price" in pan:
            extra_tp.append(pan["terminal_price"])
    close = frames["close"]
    frames = {f: v.reindex(index=close.index, columns=close.columns) for f, v in frames.items()}
    s = pd.DataFrame(sus).reindex(index=close.index, columns=close.columns).fillna(False).astype(bool) if sus else None
    cd = sr = af = None
    if corporate_actions and not close.empty:
        af = pd.DataFrame(facs).reindex(columns=close.columns) if facs else None
        if af is not None:
            af = af.sort_index().ffill().reindex(close.index, method="ffill").astype(dtype)
        stock_cols = [c for c in close.columns if instrument_type(c) not in ("cb", "eb")]
        cd, sr = load_corporate_action_panels(close.index, stock_cols, roots=roots, diag=diag, dtype=dtype)
        cd = cd.reindex(columns=close.columns).fillna(0.0) if cd is not None else None
        sr = sr.reindex(columns=close.columns).fillna(0.0) if sr is not None else None
        if extra_af:
            ea = pd.concat(extra_af, axis=1).reindex(close.index).ffill()
            af = ea.reindex(columns=close.columns) if af is None else af.combine_first(ea.reindex(columns=close.columns))
            af = af.astype(dtype)
    if corporate_actions and fund_adj_factor_actions and not close.empty:
        fids = [c for c in close.columns if is_exchange_fund(str(c))]
        if fids:
            faf, fcd = load_fund_corporate_actions(fids, close.index, dtype=dtype, diag=diag)
            if faf is not None and not faf.empty:
                af = faf.reindex(columns=close.columns) if af is None else af.copy()
                for c in faf.columns:
                    af[c] = faf[c].reindex(close.index).astype(dtype)
                af = af.astype(dtype)
            if fcd is not None:
                if cd is None:
                    cd = pd.DataFrame(0.0, index=close.index, columns=close.columns, dtype=dtype)
                for c in fcd.columns:
                    cd[c] = fcd[c].reindex(close.index).fillna(0.0).astype(dtype)
    elif fund_adj_factor_actions is False:
        diag.setdefault("fund_adj_factor_actions", "off")
    tp = pd.concat(extra_tp, axis=1).reindex(index=close.index, columns=close.columns) if extra_tp else None
    return ExecPanels(close=close, open=frames["open"], high=frames["high"], low=frames["low"],
                      volume=frames["volume"], amount=frames["amount"], limit_up=frames["limit_up"],
                      limit_down=frames["limit_down"], suspended=s, cash_div=cd, share_ratio=sr,
                      adj_factor=af, terminal_price=tp), diag


_CB_DIR = Path(__file__).resolve().parents[2] / "data/v2/cb/raw"
_FUND_DIR = Path(__file__).resolve().parents[2] / "data/v2/etf/raw"
_CB_TABLE = Path(__file__).resolve().parents[2] / "data/v2/cb/cb_daily.parquet"
_CB_BASIC = Path(__file__).resolve().parents[2] / "data/v2/cb/cb_basic.parquet"
_FUND_TABLE = Path(__file__).resolve().parents[2] / "data/v2/etf/etf_daily_adj.parquet"


def _read_table(path: Path, ts_codes: Sequence[str], start, end, columns) -> pd.DataFrame:
    """Filtered pyarrow read of a consolidated (ts_code, trade_date 'YYYYMMDD' str) table."""
    import pyarrow.parquet as pq
    lo, hi = pd.Timestamp(start).strftime("%Y%m%d"), pd.Timestamp(end).strftime("%Y%m%d")
    flt = [("ts_code", "in", list(ts_codes)), ("trade_date", ">=", lo), ("trade_date", "<=", hi)]
    have = set(pq.ParquetFile(path).schema_arrow.names)
    return pq.read_table(path, columns=[c for c in columns if c in have], filters=flt).to_pandas()


def _to_ts(iid: str) -> str:
    exch, num = _split_code(iid)
    return f"{num}.{exch.upper()}"


def _read_daily_dir(d: Path, ts_codes: Sequence[str], start, end, columns) -> pd.DataFrame:
    """Read Tushare per-day files (YYYYMMDD.parquet) in [start, end] filtered to ts_codes (small memory)."""
    lo, hi = pd.Timestamp(start).strftime("%Y%m%d"), pd.Timestamp(end).strftime("%Y%m%d")
    files = sorted(f for f in d.glob("2*.parquet") if lo <= f.stem <= hi)
    want = set(ts_codes); parts = []
    for f in files:
        x = pd.read_parquet(f, columns=columns)
        x = x[x["ts_code"].isin(want)]
        if len(x):
            parts.append(x)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=columns)


def _wide(df: pd.DataFrame, field: str, idmap: dict, dtype: str) -> pd.DataFrame:
    w = df.pivot_table(index="date", columns="ts_code", values=field, aggfunc="last")
    return w.rename(columns=idmap).astype(dtype)


def load_cb_panels(instrument_ids: Sequence[str], start, end, *, cb_dir=None, dtype: str = "float32",
                   diag: dict | None = None, table=None) -> dict:
    """Convertible-bond daily panels from Tushare ``cb_daily`` (data/v2/cb/raw/cb_daily/YYYYMMDD.parquet).

    Units as landed: ``vol`` in 手 (=10 bonds), ``amount`` in 万元 (verified: amount*1e4/(vol*close) ~ 10).
    Returned: volume in BONDS (vol*10), amount in CNY (amount*1e4). Terminal events (``terminal_price``):
    no redemption/maturity/put price table exists in data/v2/cb (cb_call / cb_rate not landed). Fallback: for
    bonds with ``cb_basic.delist_date`` whose last bar is inside the window, the holding is paid out at the
    LAST AVAILABLE CLOSE on the first session after the last bar; every such cell is flagged in
    ``diag['cb_terminal_fallback']``."""
    d = Path(cb_dir or _CB_DIR)
    idmap = {_to_ts(i): str(i) for i in instrument_ids}
    cols = ["ts_code", "trade_date", "pre_close", "open", "high", "low", "close", "vol", "amount"]
    tbl = Path(table) if table else (_CB_TABLE if cb_dir is None else None)
    src = "raw_dir"
    if tbl is not None and tbl.is_file():
        raw = _read_table(tbl, list(idmap), start, end, cols + ["is_placeholder"])
        if "is_placeholder" in raw:
            raw = raw[~raw["is_placeholder"].fillna(False).astype(bool)].drop(columns="is_placeholder")
        src = str(tbl)
    else:
        raw = _read_daily_dir(d / "cb_daily", list(idmap), start, end, cols)
    out = {}
    if raw.empty:
        if diag is not None:
            diag.setdefault("missing_ids", []).extend(map(str, instrument_ids))
        return out
    raw = raw.assign(date=pd.to_datetime(raw["trade_date"].astype(str), format="%Y%m%d"),
                     volume=raw["vol"] * 10.0, amount=raw["amount"] * 1e4)
    for f in ("open", "high", "low", "close", "volume", "amount", "pre_close"):
        out[f] = _wide(raw, f, idmap, dtype)
    term = pd.DataFrame(np.nan, index=out["close"].index, columns=out["close"].columns)
    flags = []
    try:
        if src != "raw_dir" and _CB_BASIC.is_file():
            basic = pd.read_parquet(_CB_BASIC, columns=["ts_code", "delist_date", "maturity_date"])
            import pyarrow.compute as pc, pyarrow.parquet as pq
            last_file = pc.max(pq.read_table(tbl, columns=["trade_date"])["trade_date"]).as_py()
        else:
            basic = pd.read_parquet(d / "cb_basic_raw.parquet", columns=["ts_code", "delist_date", "maturity_date"])
            last_file = max(f.stem for f in (d / "cb_daily").glob("2*.parquet"))
        basic = basic[basic["ts_code"].isin(set(idmap))]
        basic = basic.assign(delist_date=basic["delist_date"].map(
            lambda v: None if v is None or (isinstance(v, float) and np.isnan(v)) else pd.Timestamp(v).strftime("%Y%m%d")
            if not isinstance(v, str) else v.replace("-", "")[:8]))
        for _, r in basic.iterrows():
            code = idmap[r["ts_code"]]
            if code not in out["close"].columns or not isinstance(r["delist_date"], str) or r["delist_date"] > last_file:
                continue
            col = out["close"][code].dropna()
            if col.empty:
                continue
            lb = col.index[-1]
            pos = out["close"].index.searchsorted(lb, side="right")
            if pos >= len(term.index):
                flags.append(dict(code=code, last_bar=str(lb.date()), delist_date=r["delist_date"],
                                  note="event after window end; not applied"))
                continue
            term.iloc[pos, term.columns.get_loc(code)] = float(col.iloc[-1])
            flags.append(dict(code=code, last_bar=str(lb.date()), payout_date=str(term.index[pos].date()),
                              delist_date=r["delist_date"], maturity_date=r["maturity_date"], price=float(col.iloc[-1]),
                              note="fallback: last close (no redemption/maturity/put price data)"))
    except FileNotFoundError:
        pass
    out["terminal_price"] = term.astype(dtype)
    if diag is not None:
        diag["cb_terminal_fallback"] = flags
        diag["cb_source"] = dict(dir=src if src != "raw_dir" else str(d / "cb_daily"), last=str(out["close"].index.max().date()),
                                 units="vol 手(10 bonds)->bonds x10; amount 万元->CNY x1e4")
    return out


def load_fund_daily_panels(instrument_ids: Sequence[str], start, end, *, fund_dir=None, dtype: str = "float32",
                           diag: dict | None = None, table=None) -> dict:
    """Exchange-fund panels from Tushare ``fund_daily`` per-day files (data/v2/etf/raw/fund_daily).
    Units as landed: vol in 手 (100 units), amount in 千元 -> returned volume in UNITS (x100), amount CNY (x1000).
    ``adj_factor`` from ``fund_adj`` (distributions; used by the engine's factor fallback since no fund_div
    per-event table exists)."""
    d = Path(fund_dir or _FUND_DIR)
    idmap = {_to_ts(i): str(i) for i in instrument_ids}
    tbl = Path(table) if table else (_FUND_TABLE if fund_dir is None else None)
    out = {}
    if tbl is not None and tbl.is_file():
        raw = _read_table(tbl, list(idmap), start, end,
                          ["ts_code", "trade_date", "open", "high", "low", "close", "vol", "amount", "adj_factor"])
        if raw.empty:
            return out
        raw = raw.assign(date=pd.to_datetime(raw["trade_date"].astype(str), format="%Y%m%d"),
                         volume=raw["vol"] * 100.0, amount=raw["amount"] * 1000.0)
        for f in ("open", "high", "low", "close", "volume", "amount", "adj_factor"):
            out[f] = _wide(raw, f, idmap, dtype)
        if diag is not None:
            diag.setdefault("fund_daily_source", {})[",".join(map(str, out["close"].columns))] = dict(
                dir=str(tbl), last=str(out["close"].index.max().date()),
                units="vol 手->units x100; amount 千元->CNY x1000; RAW prices (hfq cols ignored)",
                fund_div="not available; adj_factor returned but load_execution_panels drops it unless fund_adj_factor_actions=True")
        return out
    raw = _read_daily_dir(d / "fund_daily", list(idmap), start, end,
                          ["ts_code", "trade_date", "open", "high", "low", "close", "vol", "amount"])
    if raw.empty:
        return out
    raw = raw.assign(date=pd.to_datetime(raw["trade_date"].astype(str), format="%Y%m%d"),
                     volume=raw["vol"] * 100.0, amount=raw["amount"] * 1000.0)
    for f in ("open", "high", "low", "close", "volume", "amount"):
        out[f] = _wide(raw, f, idmap, dtype)
    adj = _read_daily_dir(d / "fund_adj", list(idmap), start, end, ["ts_code", "trade_date", "adj_factor"])
    if not adj.empty:
        adj = adj.assign(date=pd.to_datetime(adj["trade_date"].astype(str), format="%Y%m%d"))
        out["adj_factor"] = _wide(adj, "adj_factor", idmap, dtype)
    if diag is not None:
        diag.setdefault("fund_daily_source", {})[",".join(map(str, out["close"].columns))] = dict(
            dir=str(d / "fund_daily"), last=str(out["close"].index.max().date()),
            units="vol 手->units x100; amount 千元->CNY x1000", fund_div="not available (factor fallback via fund_adj)")
    return out


_FUND_DIV = Path(__file__).resolve().parents[2] / "data/v2/etf/raw/fund_div.parquet"
FUND_DIV_ALIGN_SESSIONS = 5


def load_fund_corporate_actions(instrument_ids, index, *, table=None, div_path=None, dtype: str = "float32",
                                tol: float = FACTOR_JUMP_TOL, diag: dict | None = None):
    """(adj_factor, cash_div) wide panels for exchange funds on ``index``.

    Factor = Tushare ``fund_adj`` (etf_daily_adj.adj_factor; ffilled). Cash = ``fund_div`` rows with
    div_proc 实施, deduped on (ts_code, ex_date, div_cash) (Tushare repeats each event with/without
    net_ex_date). Each event's session = the fund_adj jump (|F_t/F_t-1 - 1| > tol) nearest its ex_date
    within FUND_DIV_ALIGN_SESSIONS sessions (Data: ex-date = actual jump day); no jump -> ex_date rolled
    to the next session. Funds without a fund_div event keep the factor fallback."""
    idx = pd.DatetimeIndex(index)
    ids = [str(i) for i in instrument_ids]
    idmap = {_to_ts(i): i for i in ids}
    tbl = Path(table) if table else _FUND_TABLE
    af = None
    if tbl.is_file() and len(idx):
        raw = _read_table(tbl, list(idmap), idx[0] - pd.Timedelta(days=10), idx[-1], ["ts_code", "trade_date", "adj_factor"])
        if not raw.empty:
            raw = raw.assign(date=pd.to_datetime(raw["trade_date"].astype(str), format="%Y%m%d"))
            w = _wide(raw, "adj_factor", idmap, "float64").sort_index().ffill()
            af = w.reindex(w.index.union(idx)).ffill().reindex(idx).astype(dtype)
    cd = pd.DataFrame(0.0, index=idx, columns=ids)
    info = dict(factor_source=str(tbl), div_source=None, events=0, aligned_to_jump=0, no_jump=0, shifted=0)
    dp = Path(div_path) if div_path else _FUND_DIV
    if dp.is_file() and len(idx):
        dv = pd.read_parquet(dp)
        dv = dv[dv["ts_code"].isin(list(idmap)) & (dv["div_proc"].astype(str) == "实施") & dv["ex_date"].notna()]
        dv = dv.assign(cash=pd.to_numeric(dv["div_cash"], errors="coerce"),
                       ex=pd.to_datetime(dv["ex_date"].astype(str), format="%Y%m%d", errors="coerce")).dropna(subset=["ex", "cash"])
        dv = dv[dv["cash"] > 0].drop_duplicates(["ts_code", "ex", "cash"])
        dv = dv[(dv["ex"] >= idx[0]) & (dv["ex"] <= idx[-1] + pd.Timedelta(days=7))]
        info["div_source"] = str(dp)
        for _, r in dv.iterrows():
            iid = idmap[r["ts_code"]]
            p0 = int(idx.searchsorted(r["ex"]))
            if p0 >= len(idx):
                continue
            pos = p0
            if af is not None and iid in af.columns:
                F = af[iid].to_numpy(dtype=float)
                with np.errstate(divide="ignore", invalid="ignore"):
                    jr = np.r_[np.nan, F[1:] / F[:-1]]
                cand = [k for k in range(max(1, p0 - FUND_DIV_ALIGN_SESSIONS), min(len(idx), p0 + FUND_DIV_ALIGN_SESSIONS + 1))
                        if np.isfinite(jr[k]) and abs(jr[k] - 1) > tol]
                if cand:
                    pos = min(cand, key=lambda k: abs(k - p0)); info["aligned_to_jump"] += 1
                    info["shifted"] += int(pos != p0)
                else:
                    info["no_jump"] += 1
            cd.iloc[pos, cd.columns.get_loc(iid)] += float(r["cash"]); info["events"] += 1
    if diag is not None:
        diag["fund_corporate_actions"] = info
    return af, cd.astype(dtype)


def load_corporate_action_panels(index, columns, *, roots=None, diag: dict | None = None, dtype: str = "float32"):
    """Per-event panels from Data's accepted Tushare dividend table (implemented rows, by ex_date).

    Units (Tushare ``dividend``): ``cash_div_tax`` = PRE-tax cash per SHARE (``cash_div`` is after-tax),
    ``stk_div`` = bonus+transfer shares per SHARE (= stk_bo_rate + stk_co_rate; 1.0 = 10-for-10).
    Ex-dates that are not sessions roll to the next session in ``index``. Returns (cash_div, share_ratio)."""
    from quantlab.data.v2_readers import default_v2_roots, load_dividends
    roots = roots or default_v2_roots()
    cand = Path(getattr(roots, "dividend_path", "")).with_name("dividend_by_exdate_tushare.parquet")
    try:
        fr = load_dividends(cand if cand.is_file() else None, roots=roots).frame
    except FileNotFoundError:
        if diag is not None:
            diag["corporate_actions"] = "dividend_table_missing"
        return None, None
    fr = fr[fr["instrument_id"].isin(set(map(str, columns))) & fr["ex_date"].notna()]
    if "div_proc" in fr.columns:
        fr = fr[fr["div_proc"].astype(str) == "实施"]
    fr = fr.assign(ex=pd.to_datetime(fr["ex_date"].astype(str), format="%Y%m%d", errors="coerce")).dropna(subset=["ex"])
    cash = pd.to_numeric(fr.get("cash_div_tax"), errors="coerce").fillna(0.0)
    stk = pd.to_numeric(fr.get("stk_div"), errors="coerce").fillna(0.0)
    fr = fr.assign(cash=cash, stk=stk).drop_duplicates(["instrument_id", "ex", "cash", "stk"])
    fr = fr[(fr["cash"] > 0) | (fr["stk"] > 0)]
    idx = pd.DatetimeIndex(index)
    pos = idx.searchsorted(fr["ex"].to_numpy())
    fr = fr.assign(_pos=pos)
    fr = fr[(fr["_pos"] < len(idx)) & (fr["ex"] >= idx[0] if len(idx) else False)]
    fr = fr.assign(session=idx[fr["_pos"].to_numpy()])
    g = fr.groupby(["session", "instrument_id"])[["cash", "stk"]].sum()
    cd = g["cash"].unstack().reindex(index=idx, columns=columns).fillna(0.0).astype(dtype)
    sr = g["stk"].unstack().reindex(index=idx, columns=columns).fillna(0.0).astype(dtype)
    if diag is not None:
        diag["corporate_actions"] = dict(source=str(cand), events=int(len(g)),
                                         note="cash_div_tax pre-tax CNY/share; stk_div shares/share")
    return cd, sr


# ----------------------------------------------------------------- reporting helpers
def effective_n_holdings(weights: pd.DataFrame) -> pd.Series:
    """Per-row 1/sum(w^2) of (actual) weights; NaN when no holdings."""
    w = weights.fillna(0.0).to_numpy(dtype=float)
    s2 = (w * w).sum(axis=1)
    with np.errstate(divide="ignore"):
        out = np.where(s2 > 0, 1.0 / np.where(s2 > 0, s2, 1.0), np.nan)
    return pd.Series(out, index=weights.index, name="effective_n_holdings")


def return_stats_ex_suspended(returns, suspended, *, periods_per_year: int = 252):
    """Opt-in risk stats that DROP suspended days instead of counting them as 0.

    ``returns``/``suspended``: aligned Series or DataFrame (bool mask). Returns a
    dict (Series input) or DataFrame (one row per column) with n_obs,
    n_suspended_excluded, mean, std, ann_return, ann_vol, sharpe (rf=0).
    Note: a resumption-day return that includes the halted-period move is kept.
    """
    if isinstance(returns, pd.Series):
        df = returns.to_frame("x"); mask = pd.Series(suspended).reindex(returns.index).fillna(False).to_frame("x")
    else:
        df = returns; mask = suspended.reindex(index=returns.index, columns=returns.columns).fillna(False)
    clean = df.where(~mask.astype(bool))
    rows = {}
    for c in clean.columns:
        x = clean[c].dropna()
        mu = float(x.mean()) if len(x) else float("nan")
        sd = float(x.std(ddof=1)) if len(x) > 1 else float("nan")
        rows[c] = dict(n_obs=int(len(x)), n_suspended_excluded=int(mask[c].astype(bool).sum()), mean=mu, std=sd,
                       ann_return=mu * periods_per_year, ann_vol=sd * np.sqrt(periods_per_year),
                       sharpe=(mu / sd * np.sqrt(periods_per_year)) if sd and np.isfinite(sd) and sd > 0 else float("nan"))
    out = pd.DataFrame.from_dict(rows, orient="index")
    return out.iloc[0].to_dict() if isinstance(returns, pd.Series) else out
