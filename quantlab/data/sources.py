"""Public quote adapters exercised by the unit tests. Network calls stay behind patches."""
from __future__ import annotations

import pandas as pd

from quantlab.config import CONFIG


class DataFeed:
    def __init__(self, store, source: str = "akshare"):
        self.store = store
        self.source = source

    def _ak(self):
        raise RuntimeError("akshare client is not configured")

    def _a_daily(self, *args, **kwargs):
        raise RuntimeError("stock endpoint forbidden")

    def _sleep(self):
        return None

    def fetch_industry_a(self):
        return None

    def _baostock_daily(self, *args, **kwargs):
        return None

    def _east_daily(self, *args, **kwargs):
        return None

    def _sina_daily(self, *args, **kwargs):
        return None

    def _a_candidates(self) -> pd.DataFrame:
        spot = self._ak().stock_zh_a_spot_em()
        frame = spot.copy()
        floor = CONFIG.universe.a_min_mktcap_yi * 1e8
        kept = frame[frame["流通市值"] >= floor]
        out = pd.DataFrame({
            "code": kept["代码"].astype(str),
            "name": kept["名称"],
            "float_mktcap": kept["流通市值"].astype(float),
        })
        self.fetch_industry_a()
        return out.reset_index(drop=True)

    def fetch_benchmark(self, market: str) -> pd.DataFrame:
        if market != "a":
            raise ValueError("unsupported market")
        raw = self._ak().stock_zh_index_daily_em(symbol="sh000300")
        frame = pd.DataFrame({"close": raw["close"].astype(float)}, index=pd.to_datetime(raw["date"]))
        frame.attrs["asset_type"] = "index"
        frame.attrs["instrument_id"] = "XSHG.INDEX.000300"
        frame.attrs["source"] = "akshare"
        return frame

    def fetch_daily(self, market: str, symbol: str, expected_session=None) -> pd.DataFrame:
        cached = self.store.load(market, f"daily_raw_{symbol}")
        if cached is None:
            cached = pd.DataFrame()
        try:
            fresh = self._ak().stock_zh_a_hist()
            row = pd.DataFrame(
                {"open": fresh["开盘"].astype(float), "close": fresh["收盘"].astype(float), "amount": fresh["成交额"].astype(float)},
                index=pd.to_datetime(fresh["日期"]),
            )
            self._sleep()
            merged = pd.concat([cached, row])
            merged = merged[~merged.index.duplicated(keep="last")].sort_index()
            merged.attrs["freshness"] = "current" if expected_session is None or pd.Timestamp(expected_session) in merged.index else "stale"
            merged.attrs["source"] = "akshare"
            merged.attrs["price_basis"] = "raw"
            self.store.save(merged, market, f"daily_raw_{symbol}")
            return merged
        except Exception as exc:
            if cached is None or len(cached) == 0:
                raise
            stale = cached.copy()
            stale.attrs["freshness"] = "stale"
            stale.attrs["update_error"] = "all_sources_failed"
            stale.attrs["update_exception"] = str(exc)
            return stale
