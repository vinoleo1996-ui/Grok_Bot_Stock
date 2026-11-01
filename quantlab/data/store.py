"""Small local cache used by the public data feed tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


class DataStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, market: str, name: str) -> Path:
        return self.root / f"{market}_{name}.pkl"

    def save(self, frame: pd.DataFrame, market: str, name: str) -> None:
        frame.to_pickle(self._path(market, name))

    def load(self, market: str, name: str):
        path = self._path(market, name)
        if not path.is_file():
            return None
        return pd.read_pickle(path)
