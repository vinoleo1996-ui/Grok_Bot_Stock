"""SSE trading calendar for the paper loop (research only).
Source: data/v2/tushare_raw/trade_cal.parquet (Data-pulled SSE trade_cal, same as research/capacity_adv_paper_extend.py;
covers future dates), cross-checked against Data's realised calendar data/v2/asof_extend_202610/calendar.parquet."""
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data/v2/tushare_raw/trade_cal.parquet"
DATA_CAL = ROOT / "data/v2/asof_extend_202610/calendar.parquet"
# ONE cutoff constant. SSE closes 15:00 Asia/Shanghai = 03:00 ET (EDT) / 02:00 ET (EST); Data's daily update lands ~06:07 ET.
# A session D becomes *required* at D 06:30 ET (grace for Data until the 06:37 ET routine). Before that, D-1 is required.
CUTOFF_ET = (6, 30)
CUTOFF_HOUR_ET = CUTOFF_ET[0]   # legacy alias

# Test-only override (None = read SRC parquet). Never used by paper path in production.
_OPEN_DAYS_OVERRIDE = None


@lru_cache(1)
def open_days():
    if _OPEN_DAYS_OVERRIDE is not None:
        return _OPEN_DAYS_OVERRIDE
    t = pd.read_parquet(SRC); t = t[(t.exchange == "SSE") & (t.is_open.astype(int) == 1)]
    return pd.DatetimeIndex(sorted(pd.to_datetime(t.cal_date.astype(str)).unique()))


def _set_open_days_for_test(idx):
    """Test hook: inject a DatetimeIndex of open days; pass None to clear. Not for production."""
    global _OPEN_DAYS_OVERRIDE
    open_days.cache_clear()
    if idx is None:
        _OPEN_DAYS_OVERRIDE = None
    else:
        _OPEN_DAYS_OVERRIDE = pd.DatetimeIndex(pd.to_datetime(idx)).normalize().unique().sort_values()


def cross_check():
    d = pd.DatetimeIndex(pd.to_datetime(pd.read_parquet(DATA_CAL).session)).normalize()
    o = open_days(); o = o[(o >= d.min()) & (o <= d.max())]
    return dict(data_cal_days=len(d), trade_cal_days=len(o), only_data=len(d.difference(o)), only_trade_cal=len(o.difference(d)),
                agree=bool(d.equals(o)))


def now_et():
    s = os.environ.get("QL_ASOF_ET")   # test override, e.g. 2026-10-17T06:37
    return pd.Timestamp(s).tz_localize("America/New_York") if s else pd.Timestamp(datetime.now(ZoneInfo("America/New_York")))


def is_trading_day(d):
    return pd.Timestamp(d).normalize() in open_days()


def prev_trading_day(d, inclusive=False):
    d = pd.Timestamp(d).normalize(); o = open_days()
    o = o[o <= d] if inclusive else o[o < d]
    return o[-1]


def close_passed(d, now=None):
    """True once session d's 15:00 Asia/Shanghai close is in the past."""
    now = now or now_et()
    return now.tz_convert("Asia/Shanghai") >= pd.Timestamp(pd.Timestamp(d).date()).tz_localize("Asia/Shanghai") + pd.Timedelta(hours=15)


def expected_session(now=None):
    """Minimum session whose data must be present now (refuse if Data is older than this)."""
    now = now or now_et(); d = pd.Timestamp(now.date())
    return prev_trading_day(d, inclusive=(now.hour, now.minute) >= CUTOFF_ET)


def latest_closed_session(now=None):
    now = now or now_et(); d = pd.Timestamp(now.tz_convert("Asia/Shanghai").date())
    return prev_trading_day(d, inclusive=close_passed(d, now))


def month_end_sessions(after, upto=None):
    o = open_days(); o = o[o > pd.Timestamp(after)]
    if upto is not None: o = o[o <= pd.Timestamp(upto)]
    return [g.max() for _, g in pd.Series(o, index=o).groupby(o.to_period("M"))]


def next_month_end(after):
    return month_end_sessions(after)[0]


def first_trading_day_on_or_after(d):
    o = open_days(); return o[o >= pd.Timestamp(d)][0]


def advance_open_days(d, n: int = 0):
    """Return the trading day that is n open days after first_trading_day_on_or_after(d).

    n=0 → first open day on or after d; n=1 → next open day after that, etc.
    Uses SSE open_days (trade_cal.parquet); never weekday/BDay.
    """
    o = open_days()
    o = o[o >= pd.Timestamp(d).normalize()]
    if len(o) <= n:
        raise IndexError(f"not enough open days on/after {d} for n={n} (have {len(o)})")
    return o[n]


def open_day_range(start, periods: int) -> pd.DatetimeIndex:
    """First `periods` SSE open days on or after start. Never pd.bdate_range."""
    o = open_days()
    o = o[o >= pd.Timestamp(start).normalize()]
    if len(o) < periods:
        raise ValueError(f"not enough open days on/after {start} (need {periods}, have {len(o)})")
    return o[:periods]
