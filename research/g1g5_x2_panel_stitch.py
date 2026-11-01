"""X2 panel stitch: D0 local panels + asof_extend_tushare_202610 (2026-07-01..).

Honest coverage to 2026-10-09 without stub forward-fill of last D0 bar.
promotion_approved=false for research weights; data tables may carry own flags.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_D0_PANELS = ROOT / "data" / "local_market" / "1c85fd9aceaa03c3c4863bec" / "panels"
ASOF_EXTEND_PANELS = ROOT / "data" / "v2" / "asof_extend_tushare_202610" / "panels"
X2_END_FROZEN = "2026-10-09"
# Research default stays frozen at 2026-10-09. Paper-extend paths only (b4_paper_extend / capacity_adv_paper_extend)
# set env QL_X2_EXTEND_END=YYYY-MM-DD before importing this module to lift the asof_extend clip.
X2_END = __import__("os").environ.get("QL_X2_EXTEND_END") or X2_END_FROZEN
X2_START = "2024-01-02"

_FEATURE_CACHE: dict[str, pd.DataFrame] = {}
_CLOSE_CACHE: dict[str, pd.Series] = {}


def to_panel_id(instrument: str) -> str:
    s = str(instrument).strip()
    if "." not in s:
        return s
    a, b = s.split(".", 1)
    if a.isdigit() and b.upper() in ("SH", "SZ", "BJ"):
        return f"{b.lower()}.{a}"
    if a.lower() in ("sh", "sz", "bj") and b.isdigit():
        return f"{a.lower()}.{b}"
    return s


def _derive_limit_ratio(edf: pd.DataFrame) -> pd.Series:
    if "limit_up" in edf.columns and "open" in edf.columns:
        open_ = pd.to_numeric(edf["open"], errors="coerce")
        up = pd.to_numeric(edf["limit_up"], errors="coerce")
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = (up / open_) - 1.0
        ratio = pd.Series(ratio, index=edf.index).replace([np.inf, -np.inf], np.nan)
        # ChiNext/STAR often ~0.2; main ~0.1; clamp sane band
        ratio = ratio.where((ratio >= 0.05) & (ratio <= 0.25))
        # fill by board heuristic from instrument id in index name — caller may pass default
        return ratio
    return pd.Series(np.nan, index=edf.index)


def load_panel_features_x2(instrument: str) -> pd.DataFrame:
    """OHLCV + limit_ratio_at_open indexed by session, D0∪asof_extend."""
    if instrument in _FEATURE_CACHE:
        return _FEATURE_CACHE[instrument]
    pid = to_panel_id(instrument)
    cols = ["open", "close", "turnover", "amount", "volume", "limit_ratio_at_open"]
    pieces: list[pd.DataFrame] = []
    d0 = DEFAULT_D0_PANELS / f"{pid}.parquet"
    if d0.exists():
        df = pd.read_parquet(d0, columns=[c for c in cols if c != "limit_ratio_at_open"] + (
            ["limit_ratio_at_open"] if True else []
        ))
        # some panels may miss limit_ratio
        have = [c for c in cols if c in df.columns]
        df = df[have].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
        df = df[~df.index.duplicated(keep="last")].sort_index()
        if "limit_ratio_at_open" not in df.columns:
            df["limit_ratio_at_open"] = 0.1
        pieces.append(df[cols])
    extp = ASOF_EXTEND_PANELS / f"{pid}.parquet"
    if extp.exists():
        edf = pd.read_parquet(extp)
        edf = edf.copy()
        edf["session"] = pd.to_datetime(edf["trade_date"]).dt.tz_localize(None).dt.normalize()
        edf = edf.set_index("session")
        edf = edf[~edf.index.duplicated(keep="last")].sort_index()
        # only keep through X2_END for weight calendar honesty (data may include next open day)
        edf = edf[edf.index <= pd.Timestamp(X2_END)]
        ratio = _derive_limit_ratio(edf)
        default_lr = 0.2 if pid.startswith("sz.3") or pid.startswith("sh.68") else 0.1
        out = pd.DataFrame(
            {
                "open": pd.to_numeric(edf.get("open"), errors="coerce"),
                "close": pd.to_numeric(edf.get("close"), errors="coerce"),
                "turnover": pd.to_numeric(edf.get("turnover"), errors="coerce"),
                "amount": pd.to_numeric(edf.get("amount"), errors="coerce"),
                "volume": pd.to_numeric(edf.get("volume"), errors="coerce"),
                "limit_ratio_at_open": ratio.fillna(default_lr),
            },
            index=edf.index,
        )
        if pieces:
            cut = pieces[0].index.max()
            out = out[out.index > cut]
        pieces.append(out[cols])
    if not pieces:
        _FEATURE_CACHE[instrument] = pd.DataFrame(columns=cols)
        return _FEATURE_CACHE[instrument]
    df = pd.concat(pieces).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    _FEATURE_CACHE[instrument] = df
    return df


def load_equity_closes_x2(instrument: str) -> pd.Series:
    """Close series D0∪asof_extend (raw close; research-grade consistent with prior expand)."""
    if instrument in _CLOSE_CACHE:
        return _CLOSE_CACHE[instrument]
    feat = load_panel_features_x2(instrument)
    if feat.empty or "close" not in feat.columns:
        empty = pd.Series(dtype=float)
        _CLOSE_CACHE[instrument] = empty
        return empty
    ser = pd.to_numeric(feat["close"], errors="coerce")
    ser = ser.dropna()
    ser = ser[ser > 0].sort_index()
    # clip to X2_END
    ser = ser[ser.index <= pd.Timestamp(X2_END)]
    _CLOSE_CACHE[instrument] = ser
    return ser


def install_equity_close_monkeypatch() -> dict[str, Any]:
    """Monkeypatch research.ai_debate_memory_runner._load_equity_closes → x2 stitch."""
    import research.ai_debate_memory_runner as m

    prev = m._load_equity_closes

    def _wrapped(instrument: str, panels_dir: Path | None = None):
        # only stitch when using default D0; explicit panels_dir left alone
        if panels_dir is not None and Path(panels_dir) != DEFAULT_D0_PANELS:
            return prev(instrument, panels_dir=panels_dir)
        return load_equity_closes_x2(instrument)

    m._load_equity_closes = _wrapped  # type: ignore[assignment]
    # also clear cache so old D0-only entries are not reused
    m._EQUITY_CLOSE_CACHE.clear()
    return {"prev": prev, "module": m}


def clear_caches() -> None:
    _FEATURE_CACHE.clear()
    _CLOSE_CACHE.clear()


def coverage_report(instruments: list[str]) -> dict[str, Any]:
    ends = []
    missing_ext = []
    for i in instruments:
        f = load_panel_features_x2(i)
        if f.empty:
            ends.append({"instrument": i, "end": None, "n": 0})
            continue
        ends.append(
            {
                "instrument": i,
                "start": str(pd.Timestamp(f.index.min()).date()),
                "end": str(pd.Timestamp(f.index.max()).date()),
                "n": int(len(f)),
            }
        )
        pid = to_panel_id(i)
        if not (ASOF_EXTEND_PANELS / f"{pid}.parquet").exists():
            missing_ext.append(i)
    ends_ok = [e for e in ends if e.get("end") and e["end"] >= X2_END]
    return {
        "x2_end_target": X2_END,
        "n_instruments": len(instruments),
        "n_reaching_x2_end": len(ends_ok),
        "min_end": min((e["end"] for e in ends if e.get("end")), default=None),
        "max_end": max((e["end"] for e in ends if e.get("end")), default=None),
        "missing_asof_extend": missing_ext,
        "sample_ends": ends[:5],
        "sources": {
            "d0": str(DEFAULT_D0_PANELS.relative_to(ROOT)),
            "asof_extend": str(ASOF_EXTEND_PANELS.relative_to(ROOT)),
        },
    }


def load_adj_close_x2(instrument: str):
    """Self-check-only back-adjusted close (raw X2 close × adj_factor, research/adj_price.py).

    Do NOT use for signals: signal layer keeps load_panel_features_x2 raw prices unchanged.
    """
    from research.adj_price import adj_close
    f = load_panel_features_x2(instrument)
    if f is None or f.empty:
        import pandas as _pd
        return _pd.Series(dtype=float)
    return adj_close(instrument, f["close"])
