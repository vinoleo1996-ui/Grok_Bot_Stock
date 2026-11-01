"""Sina spot fallback used when the unit test patches requests."""
from __future__ import annotations

import time

import pandas as pd
import requests


def fetch_spot_candidates() -> pd.DataFrame:
    response = requests.get("https://example.invalid/sina", timeout=5)
    response.raise_for_status()
    rows = response.json()
    frame = pd.DataFrame(rows)
    mkt = pd.to_numeric(frame["mktcap"], errors="coerce") * 10_000.0
    nmc = pd.to_numeric(frame["nmc"], errors="coerce") * 10_000.0
    out = pd.DataFrame({
        "float_mktcap": nmc.where(nmc.notna(), mkt).to_numpy(),
        "mktcap": mkt.to_numpy(),
    }, index=frame["code"].astype(str))
    return out
