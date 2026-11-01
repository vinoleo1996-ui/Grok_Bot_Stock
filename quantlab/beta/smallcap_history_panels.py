"""Light, 2015+ panel shim for SmallcapBetaSleeveProvider (data_source='history_2015').

Backs the provider's weights/capacity/crowding/β helpers with the same sources as
smallcap_history_selector (daily_basic wide caches + full-market float mktcap), instead of
output/research_attrib_v2/panels (2023-01+ only, ~2.9 GB peak on load).

Fields (SmallcapPanels-compatible subset):
  close          daily_basic close (UNADJUSTED; fine for lot/capacity checks)
  adv            60d mean of ADV proxy = turnover_rate% × circ_mv (amount not in daily_basic)
  turnover_rate  proxy = amt_proxy / float_mktcap × 100 (crowding flags)
  ret            close-to-close of unadjusted close, |r|>0.22 clipped to NaN (ex-right days) — descriptive β only
  etf_ret        510300 adjusted (close × factor) return from data/v2 ETF reader
Not available (None): amount, trad, st, lu, ld (limit flags) → stress_test stays on the 2023+ panels path.
Research-only; promotion_approved=false.
"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def load_history_panels(adv_window: int = 60, adv_min: int = 20):
    import pandas as pd

    from quantlab.beta.smallcap_history_selector import daily_basic_panels
    from quantlab.beta.smallcap_sleeve import SmallcapPanels
    from quantlab.beta.survivorship import load_full_market_float_mktcap

    P = daily_basic_panels()
    close = P["close"]
    amt = P["amt_proxy"]
    adv = amt.rolling(adv_window, min_periods=adv_min).mean().astype("float32")
    fm = load_full_market_float_mktcap().reindex(index=amt.index, columns=amt.columns)
    tr = (amt / fm * 100.0).astype("float32")
    ret = close.pct_change(fill_method=None)
    ret = ret.where(ret.abs() <= 0.22).astype("float32")
    etf_ret = None
    try:
        from quantlab.data.v2_readers import load_etf_510300

        pf = load_etf_510300().panel_frame
        d = pd.to_datetime(pf["event_time"]).dt.normalize()
        px = (pd.to_numeric(pf["close"], errors="coerce") * pd.to_numeric(pf["factor"], errors="coerce").fillna(1.0))
        etf_ret = pd.Series(px.to_numpy(), index=d).groupby(level=0).last().sort_index().pct_change()
    except Exception:  # pragma: no cover
        etf_ret = None
    hist = close.notna().cumsum()
    return SmallcapPanels(
        close=close, ret=ret, amount=None, trad=None, st=None, lu=None, ld=None,
        circ_mv=None, pe_ttm=P["pe_ttm"], pb=P["pb"], turnover_rate=tr, etf_ret=etf_ret,
        hist=hist, adv=adv, cap=None, sw=None, panels_dir="history_2015:daily_basic+float_mktcap_from2015",
        gaps=("history_2015:amount=turnover_rate×circ_mv proxy", "history_2015:close_unadjusted",
              "history_2015:no_limit_flags_stress_test_unavailable"),
    )
