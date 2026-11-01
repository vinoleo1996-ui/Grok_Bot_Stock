"""Versioned market dataset and the timestamps the ledger already calls."""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
import hashlib
import json

import pandas as pd


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(key): _jsonable(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(value) for value in obj]
    return obj


def fingerprint(obj) -> str:
    payload = json.dumps(_jsonable(obj), sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def timestamp(value):
    """Timezone-aware Asia/Shanghai timestamp. Naive values are local Shanghai."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return pd.NaT
    try:
        if pd.isna(value):
            return pd.NaT
    except TypeError:
        pass
    stamp = pd.Timestamp(value)
    if pd.isna(stamp):
        raise ValueError(f"invalid timestamp: {value}")
    if stamp.tzinfo is None:
        return stamp.tz_localize("Asia/Shanghai")
    return stamp.tz_convert("Asia/Shanghai")


def decision_time(day):
    """Research decision cutoff: 18:00 Asia/Shanghai on the session date."""
    base = timestamp(day)
    return base.normalize() + pd.Timedelta(hours=18)


def timestamps_series(series: pd.Series) -> pd.Series:
    converted = series.map(lambda value: timestamp(value) if pd.notna(value) else pd.NaT)
    out = pd.to_datetime(converted, utc=True).dt.tz_convert("Asia/Shanghai")
    out.index = series.index
    return out


def asof_records(frame: pd.DataFrame, as_of) -> pd.DataFrame:
    """Latest instrument row whose effective and available times are known by as_of."""
    if frame is None or len(frame) == 0:
        return pd.DataFrame()
    cutoff = timestamp(as_of)
    work = frame.copy()
    if "instrument_id" not in work.columns:
        work = work.reset_index()
    available = work["available_at"].map(lambda value: timestamp(value) if pd.notna(value) else pd.NaT)
    if "effective_at" in work.columns:
        effective = work["effective_at"].map(lambda value: timestamp(value) if pd.notna(value) else pd.NaT)
    else:
        effective = pd.Series(pd.NaT, index=work.index)
    known = available.notna() & (available <= cutoff) & (effective.isna() | (effective <= cutoff))
    work = work.loc[known].copy()
    if work.empty:
        return work.set_index("instrument_id")
    work["_available"] = available.loc[work.index]
    work["_effective"] = effective.loc[work.index]
    revision = work["revision"] if "revision" in work.columns else ""
    work["_revision"] = revision
    work = work.sort_values(["instrument_id", "_effective", "_available", "_revision"])
    chosen = work.groupby("instrument_id", sort=False).tail(1)
    return chosen.drop(columns=["_available", "_effective", "_revision"]).set_index("instrument_id")


@dataclass
class InstrumentRules:
    instrument_id: str
    asset_type: str
    buy_lot: int
    sell_lot: int
    sell_delay: int
    price_tick: float
    commission: float
    min_commission: float
    limit_ratio: float | None
    min_buy_quantity: int | None = None
    min_sell_quantity: int | None = None

    def minimum_quantity(self, side: str) -> int:
        raw = self.min_buy_quantity if side == "buy" else self.min_sell_quantity
        if raw is None:
            raw = self.buy_lot if side == "buy" else self.sell_lot
        return int(raw)

    def order_quantity(self, qty, side: str, holding=None) -> int:
        quantity = int(max(qty, 0) // 1) if not isinstance(qty, int) else max(qty, 0)
        # Floor first so a float just under an integer does not round up.
        import math
        quantity = int(math.floor(float(qty) + 1e-9))
        if side == "sell" and holding is not None and float(holding) > 0 and quantity >= int(round(float(holding))):
            return int(round(float(holding)))
        step = int(self.buy_lot if side == "buy" else self.sell_lot)
        minimum = self.minimum_quantity(side)
        if step <= 0:
            raise ValueError("invalid order lot")
        if quantity < minimum:
            return 0
        return minimum + (quantity - minimum) // step * step

    @classmethod
    def from_record(cls, row):
        data = row.to_dict() if hasattr(row, "to_dict") else dict(row)
        if "instrument_id" not in data or pd.isna(data.get("instrument_id")):
            if getattr(row, "name", None) not in (None, ""):
                data["instrument_id"] = row.name
        kwargs = {}
        for item in fields(cls):
            if item.name not in data or pd.isna(data[item.name]):
                if item.default is not None or item.name.startswith("min_"):
                    continue
                if item.name == "limit_ratio" and (item.name not in data or pd.isna(data.get(item.name))):
                    kwargs[item.name] = None
                    continue
            else:
                value = data[item.name]
                if item.name in {"min_buy_quantity", "min_sell_quantity"}:
                    number = int(value)
                    if number <= 0:
                        raise ValueError("invalid order minimum")
                    kwargs[item.name] = number
                elif item.name in {"buy_lot", "sell_lot", "sell_delay"}:
                    kwargs[item.name] = int(value)
                elif item.name in {"price_tick", "commission", "min_commission", "limit_ratio"}:
                    kwargs[item.name] = float(value)
                else:
                    kwargs[item.name] = value
        if "limit_ratio" not in kwargs:
            kwargs["limit_ratio"] = None
        return cls(**kwargs)


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame()


@dataclass
class MarketDataset:
    panels: dict
    instruments: pd.DataFrame
    calendar: pd.DatetimeIndex
    benchmark: pd.DataFrame = field(default_factory=_empty_frame)
    manifest: dict = field(default_factory=dict)
    actions: pd.DataFrame = field(default_factory=_empty_frame)
    industry_records: pd.DataFrame = field(default_factory=_empty_frame)
    financials: pd.DataFrame = field(default_factory=_empty_frame)
    evidence_root: Path | None = None

    @property
    def version(self) -> str:
        identity = {
            "manifest": {key: value for key, value in self.manifest.items() if key != "coverage_evidence"},
            "panels": {code: [str(self.panels[code].index.min()), str(self.panels[code].index.max()), len(self.panels[code])]
                       for code in sorted(self.panels)},
            "instruments": len(self.instruments),
        }
        return fingerprint(identity)

    def validate(self, data_mode: str = "strict") -> list[str]:
        reasons = []
        industry = self.industry_records
        proxy = (
            self.manifest.get("industry_mode") == "effective_date_proxy"
            or (industry is not None and len(industry) and "available_at" in industry.columns and industry["available_at"].isna().all())
        )
        if data_mode == "strict" and proxy and industry is not None and len(industry):
            reasons.append("industry_proxy_not_PIT")
        return reasons


def coverage_input_fingerprint(dataset: MarketDataset) -> str:
    identity = {
        "manifest": {key: value for key, value in dataset.manifest.items() if key != "coverage_evidence"},
        "calendar": [str(dataset.calendar[0]), str(dataset.calendar[-1]), len(dataset.calendar)],
        "instruments": sorted(map(str, dataset.instruments.get("instrument_id", []))),
    }
    return fingerprint(identity)


def _table_token(frame: pd.DataFrame) -> str:
    if frame is None or len(frame.columns) == 0 and len(frame.index) == 0:
        return ""
    hashed = pd.util.hash_pandas_object(frame.reset_index(), index=False).to_numpy()
    return hashlib.sha256(hashed.tobytes()).hexdigest()


def dump_dataset(dataset: MarketDataset, folder) -> str:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    identity = {
        "manifest": dataset.manifest,
        "calendar": [str(value) for value in dataset.calendar],
        "instruments": _table_token(dataset.instruments),
        "benchmark": _table_token(dataset.benchmark),
        "actions": _table_token(dataset.actions),
        "industry": _table_token(dataset.industry_records),
        "financials": _table_token(dataset.financials),
        "panels": {code: _table_token(panel) for code, panel in sorted(dataset.panels.items())},
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, default=str).encode()).hexdigest()
    root = folder / digest
    if not (root / "manifest.json").is_file():
        root.mkdir(parents=True, exist_ok=True)
        (root / "manifest.json").write_text(json.dumps(dataset.manifest, default=str), encoding="utf-8")
        pd.Series(dataset.calendar.astype(str)).to_frame("session").to_parquet(root / "calendar.parquet")
        dataset.instruments.to_parquet(root / "instruments.parquet")
        dataset.benchmark.to_parquet(root / "benchmark.parquet")
        dataset.actions.to_parquet(root / "actions.parquet")
        dataset.industry_records.to_parquet(root / "industry.parquet")
        dataset.financials.to_parquet(root / "financials.parquet")
        panel_dir = root / "panels"
        panel_dir.mkdir(exist_ok=True)
        for code, panel in dataset.panels.items():
            panel.to_parquet(panel_dir / f"{code}.parquet")
    return str(root / "manifest.json")


def _read_table(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_dataset(path, profile: str = "strict") -> MarketDataset:
    root = Path(path).parent
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    calendar = pd.DatetimeIndex(pd.to_datetime(pd.read_parquet(root / "calendar.parquet")["session"]))
    panels = {item.stem: pd.read_parquet(item) for item in sorted((root / "panels").glob("*.parquet"))}
    return MarketDataset(
        panels,
        _read_table(root / "instruments.parquet"),
        calendar,
        benchmark=_read_table(root / "benchmark.parquet"),
        manifest=manifest,
        actions=_read_table(root / "actions.parquet"),
        industry_records=_read_table(root / "industry.parquet"),
        financials=_read_table(root / "financials.parquet"),
    )
