"""D1 tradable-mask pipeline (mask-first) — Eng frozen field names.

Pipeline order (Mandate / DATA_V2_MIN_SPEC §3), decision session ``t``:

  1. historical instruments (incl. pre-delist)
  2. listing_trading_days >= 120
  3. tradable & not ST  (tradestatus / open_status / is_st_at_open)
  4. U30: median_amount_20d >= threshold (Mandate liquidity)
  5. limit-up buy block / limit-down sell block
  6. exclude bottom ~30% float_mktcap (PIT)
  7. attach SW_L1 as-of from industry_members_sw_l1 (not D0 industry_records)

Frozen names (do not rename):
  - float_mktcap          (CNY, quantlab.v2.float_mktcap.v1)
  - median_amount_20d     (U30 metric)
  - industry_members_sw_l1 columns per SWL1MemberRow

Panel resolution (research merge; 1c85 originals untouched):
  prefer D0 bar if session <= d0_as_of_cutoff (default 2026-06-30)
  else asof_extend bar from data/v2/asof_extend_202610/panels/<id>.parquet
  See quantlab.data.v2_readers.load_merged_panel + docs/v2/ASOF_EXTEND_PANEL_MERGE.md.

Strict ledger mode rejects open_status in {derived, unknown} as trading.
Research mode may keep derived/unknown with quality notes; amount gaps on
asof_extend waive U30 (adv_fail) rather than inventing liquidity; promotion_approved=False.
"""
from __future__ import annotations

from quantlab.promotion_gate import overall_promotion_approved as _gate

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Literal, Sequence

import numpy as np
import pandas as pd

from quantlab.config import ROOT
from quantlab.v2_schemas import (
    FLOAT_MKTCAP_FIELD,
    PANEL_MASK_COLUMNS,
    SW_L1_TABLE_NAME,
    SWL1AsOfAssignment,
)

DEFAULT_D0_ROOT = ROOT / "data" / "local_market" / "1c85fd9aceaa03c3c4863bec"
DEFAULT_ASOF_EXTEND_DIR = ROOT / "data" / "v2" / "asof_extend_tushare_202610"  # accepted default; v2_readers falls back to asof_extend_202610 per instrument
DEFAULT_SW_L1_PATHS = (
    # Research default: accepted tushare SW_L1 PIT
    ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1_tushare.parquet",
    # Fallback: XLS-prefix → Eng columns
    ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1_prefix.parquet",
    # Fallback: legacy vote reconstruction
    ROOT / "data" / "v2" / "sw_l1_pit" / "industry_members_sw_l1.parquet",
    ROOT / "data" / "sw" / "industry_members_sw_l1.parquet",
    DEFAULT_D0_ROOT / "industry_members_sw_l1.parquet",
)

OpenStatusMode = Literal["research", "strict"]

# Locked U30 metric name
MEDIAN_AMOUNT_20D_FIELD = "median_amount_20d"


@dataclass(frozen=True)
class D1MaskConfig:
    listing_min_trading_days: int = 120
    exclude_bottom_mktcap_pct: float = 0.30
    liquidity_threshold_cny: float = 3.0e7  # U30 primary
    amount_lookback: int = 20
    open_status_mode: OpenStatusMode = "research"
    # float_mktcap proxy when column absent: close * volume / (turnover/100)
    # turnover unit on D0 panels: percent (manifest turnover_unit)
    turnover_is_percent: bool = True
    # Research-only: when median_amount_20d is NaN due to asof_extend amount
    # gaps, do not fail U30 (adv_fail=False) — never claims promotion readiness.
    waive_u30_on_amount_gap: bool = True


@dataclass(frozen=True)
class D1MaskResult:
    session: date
    n_instruments_in: int
    n_after_listing: int
    n_after_tradable_st: int
    n_after_u30: int
    n_after_limits: int
    n_after_mktcap: int
    member_ids: tuple[str, ...]
    frame: pd.DataFrame  # columns include mask fields + float_mktcap + median_amount_20d
    promotion_approved: bool = False  # overall — set from quantlab.promotion_gate
    sw_l1_promotable: bool = False  # dataset-level SW flag (True ok for accepted tushare)
    float_mktcap_source: str = "none"  # v2_daily | v2_parquet | panel_derived | stale_carry | none
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved and not _gate():
            raise ValueError("d1_mask_promotion_approved_exceeds_gate")
        # sw_l1_promotable may be True when Data accepted tushare SW dataset;
        # that is distinct from overall promotion_approved.


def resolve_sw_l1_path(explicit: Path | None = None) -> Path | None:
    """Prefer accepted tushare via v2_readers; fall back to DEFAULT_SW_L1_PATHS."""
    if explicit is not None and explicit.is_file():
        return explicit
    try:
        from quantlab.data.v2_readers import resolve_sw_l1_research_path

        path, _variant = resolve_sw_l1_research_path(None)
        return path
    except FileNotFoundError:
        pass
    for p in DEFAULT_SW_L1_PATHS:
        if p.is_file():
            return p
    return None


def load_calendar(
    d0_root: Path,
    *,
    asof_extend_dir: Path | None = None,
) -> pd.DatetimeIndex:
    """Prefer asof_extend calendar (superset); fall back to D0."""
    from quantlab.data.v2_readers import load_merged_calendar

    view = load_merged_calendar(
        d0_root=d0_root,
        asof_extend_dir=asof_extend_dir if asof_extend_dir is not None else DEFAULT_ASOF_EXTEND_DIR,
    )
    return view.sessions


def listing_age_trading_days(
    listing_date: date | None,
    session: date,
    calendar: pd.DatetimeIndex,
) -> int | None:
    if listing_date is None or pd.isna(listing_date):
        return None
    ld = pd.Timestamp(listing_date)
    sess = pd.Timestamp(session)
    return int(((calendar >= ld) & (calendar <= sess)).sum())


def derive_float_mktcap(panel: pd.DataFrame, *, turnover_is_percent: bool = True) -> pd.Series:
    """PIT float_mktcap proxy from D0 panels when column absent.

    Formula (turnover percent): close * volume / (turnover / 100)
    Returns CNY series aligned to panel index; NaN where turnover<=0 or missing.
    """
    if FLOAT_MKTCAP_FIELD in panel.columns and panel[FLOAT_MKTCAP_FIELD].notna().any():
        return pd.to_numeric(panel[FLOAT_MKTCAP_FIELD], errors="coerce")
    close = pd.to_numeric(panel.get("close"), errors="coerce")
    volume = pd.to_numeric(panel.get("volume"), errors="coerce")
    turnover = pd.to_numeric(panel.get("turnover"), errors="coerce")
    if turnover_is_percent:
        denom = turnover / 100.0
    else:
        denom = turnover
    out = close * volume / denom.replace(0, np.nan)
    out = out.where(turnover > 0)
    return out


def median_amount_20d(amount: pd.Series, lookback: int = 20) -> pd.Series:
    """Locked U30 metric: rolling median of daily amount over ``lookback`` sessions."""
    a = pd.to_numeric(amount, errors="coerce")
    return a.rolling(lookback, min_periods=max(5, lookback // 2)).median()


def _session_row(panel: pd.DataFrame, session: date) -> pd.Series | None:
    from quantlab.data.v2_readers import panel_session_row

    try:
        return panel_session_row(panel, session)
    except ValueError:
        return None


def load_panel(
    d0_root: Path,
    instrument_id: str,
    *,
    asof_extend_dir: Path | None = None,
) -> pd.DataFrame | None:
    """Research-merged panel (D0 + asof_extend). Prefer :func:`load_merged_panel_frame`."""
    return load_merged_panel_frame(
        instrument_id,
        d0_root=d0_root,
        asof_extend_dir=asof_extend_dir if asof_extend_dir is not None else DEFAULT_ASOF_EXTEND_DIR,
    )


def load_merged_panel_frame(
    instrument_id: str,
    *,
    d0_root: Path = DEFAULT_D0_ROOT,
    asof_extend_dir: Path = DEFAULT_ASOF_EXTEND_DIR,
) -> pd.DataFrame | None:
    from quantlab.data.v2_readers import load_merged_panel

    view = load_merged_panel(
        instrument_id,
        d0_root=d0_root,
        asof_extend_dir=asof_extend_dir,
    )
    return view.frame


def sw_l1_asof(
    members: pd.DataFrame,
    session: date,
    instrument_ids: Sequence[str],
) -> dict[str, SWL1AsOfAssignment]:
    """Point-in-time SW_L1 from industry_members_sw_l1 (frozen columns)."""
    require = {"instrument_id", "sw_code", "sw_name", "in_date", "out_date", "available_at"}
    missing = require - set(members.columns)
    if missing:
        raise ValueError(f"sw_l1_columns_missing:{','.join(sorted(missing))}")
    sess = pd.Timestamp(session).date()
    sess_ts = pd.Timestamp(sess)
    out: dict[str, SWL1AsOfAssignment] = {}
    sub = members[members["instrument_id"].isin(list(instrument_ids))].copy()
    sub["in_date"] = pd.to_datetime(sub["in_date"]).dt.normalize()
    sub["out_date"] = pd.to_datetime(sub["out_date"], errors="coerce").dt.normalize()

    def _published_before_session(value) -> bool:
        stamp = pd.Timestamp(value)
        if pd.isna(stamp):
            return False
        if stamp.tzinfo is None:
            stamp = stamp.tz_localize("Asia/Shanghai")
        else:
            stamp = stamp.tz_convert("Asia/Shanghai")
        return stamp.date() < sess

    sub = sub[sub["available_at"].map(_published_before_session)]
    for iid, g in sub.groupby("instrument_id"):
        cand = g[(g["in_date"] <= sess_ts) & (g["out_date"].isna() | (g["out_date"] > sess_ts))]
        if cand.empty:
            out[iid] = SWL1AsOfAssignment(
                instrument_id=iid,
                session=sess,
                sw_code=None,
                sw_name=None,
                available_at=None,
                quality_status=None,
                is_unknown_bucket=True,
            )
            continue
        # last in_date wins
        row = cand.sort_values("in_date").iloc[-1]
        avail = row["available_at"]
        if isinstance(avail, str):
            avail = pd.Timestamp(avail).to_pydatetime()
        out[iid] = SWL1AsOfAssignment(
            instrument_id=iid,
            session=sess,
            sw_code=str(row["sw_code"]),
            sw_name=str(row["sw_name"]),
            available_at=avail,
            quality_status=str(row.get("quality_status", "")),
            is_unknown_bucket=False,
        )
    return out


def build_d1_masks_for_session(
    session: date,
    *,
    d0_root: Path = DEFAULT_D0_ROOT,
    asof_extend_dir: Path | None = None,
    config: D1MaskConfig | None = None,
    instrument_ids: Sequence[str] | None = None,
    max_instruments: int | None = None,
    sw_l1_path: Path | None = None,
    float_mktcap_path: Path | None = None,
) -> D1MaskResult:
    """Compute D1 mask for one session over research-merged panels.

    Panel source: D0 bars for ``session <= d0_as_of_cutoff``, else asof_extend
    (see :func:`quantlab.data.v2_readers.load_merged_panel`). Never mutates 1c85.

    If ``instrument_ids`` is None, uses D0 ``instruments.parquet`` (optionally
    capped by ``max_instruments`` for prototypes).

    float_mktcap: prefer V2 **daily** parquet for exact ``session``
    (``v2_daily``); else asof exact match (``v2_parquet``); else research
    stale-carry of single-asof (``stale_carry``). Never promotion-ready.

    U30 / amount gaps on asof_extend: in research mode with
    ``waive_u30_on_amount_gap``, NaN ``median_amount_20d`` does not fail U30.
    SW_L1 dataset may be promotion-grade (accepted tushare); overall
    ``promotion_approved`` on this result stays False.
    """
    from quantlab.data.v2_readers import (
        load_merged_calendar,
        load_merged_panel,
        resolve_d0_asof_cutoff,
    )

    cfg = config or D1MaskConfig()
    d0_root = Path(d0_root)
    extend_dir = Path(asof_extend_dir) if asof_extend_dir is not None else DEFAULT_ASOF_EXTEND_DIR
    cutoff = resolve_d0_asof_cutoff(extend_dir)

    cal_view = load_merged_calendar(d0_root=d0_root, asof_extend_dir=extend_dir)
    cal = cal_view.sessions
    if not (cal.normalize() == pd.Timestamp(session)).any():
        raise ValueError(f"session_not_in_calendar:{session}")

    instruments = pd.read_parquet(d0_root / "instruments.parquet")
    if instrument_ids is not None:
        instruments = instruments[instruments["instrument_id"].isin(list(instrument_ids))]
    elif max_instruments is not None:
        instruments = instruments.head(max_instruments)

    notes: list[str] = [
        f"panel_mask_columns_expected={','.join(PANEL_MASK_COLUMNS)}",
        f"float_mktcap_field={FLOAT_MKTCAP_FIELD}",
        f"u30_field={MEDIAN_AMOUNT_20D_FIELD}",
        f"open_status_mode={cfg.open_status_mode}",
        f"panel_merge_cutoff={cutoff}",
        f"asof_extend_dir={extend_dir}",
        f"calendar_source={cal_view.path_primary}",
        f"calendar_includes_extend={cal_view.includes_extend}",
        f"overall_promotion_approved={str(_gate()).lower()}",
        "sw_l1_dataset_flags_from_loader",
    ]
    if session > cutoff:
        notes.append(f"session_in_extend_window:{session}>cutoff:{cutoff}")

    # Prefer daily float_mktcap by session; fall back to asof / stale-carry.
    from quantlab.data.v2_readers import float_mktcap_lookup_for_session

    id_list = instruments["instrument_id"].astype(str).tolist()
    fm_sess = float_mktcap_lookup_for_session(
        session,
        asof_path=float_mktcap_path,
        instrument_ids=id_list,
        prefer_daily=True,
    )
    fm_lookup: dict[str, float] = dict(fm_sess.values)
    fm_source_by_id: dict[str, str] = dict(fm_sess.source_by_id)
    float_mktcap_source = fm_sess.primary_source
    notes.extend(list(fm_sess.notes))
    notes.append(f"float_mktcap_non_null={len(fm_lookup)}")

    rows: list[dict] = []
    n_amount_gap_waived = 0
    n_merged = 0
    n_extend_only_row = 0
    merge_notes_sample: list[str] = []

    for iid in instruments["instrument_id"].astype(str).tolist():
        view = load_merged_panel(
            iid,
            d0_root=d0_root,
            asof_extend_dir=extend_dir,
            d0_asof_cutoff=cutoff,
        )
        panel = view.frame
        if panel is None or panel.empty:
            continue
        n_merged += 1
        if view.panel_source == "merged" and session > cutoff:
            n_extend_only_row += 1  # session row comes from extend half
        if len(merge_notes_sample) < 6:
            for qn in view.quality_notes:
                if qn.startswith("extend_") and qn not in merge_notes_sample:
                    merge_notes_sample.append(qn)

        panel = panel.sort_values("event_time")
        if iid in fm_lookup:
            panel = panel.copy()
            panel[FLOAT_MKTCAP_FIELD] = np.nan
        else:
            mkt = derive_float_mktcap(panel, turnover_is_percent=cfg.turnover_is_percent)
            panel = panel.copy()
            panel[FLOAT_MKTCAP_FIELD] = mkt
            if float_mktcap_source == "none" and mkt.notna().any():
                float_mktcap_source = "panel_derived"

        amount_series = (
            pd.to_numeric(panel["amount"], errors="coerce")
            if "amount" in panel.columns
            else pd.Series(np.nan, index=panel.index)
        )
        panel[MEDIAN_AMOUNT_20D_FIELD] = median_amount_20d(amount_series, cfg.amount_lookback)
        row = _session_row(panel, session)
        if row is None:
            continue

        inst = instruments.loc[instruments["instrument_id"] == iid].iloc[0]
        listing_raw = inst.get("listing_date")
        try:
            listing_d = pd.Timestamp(listing_raw).date() if pd.notna(listing_raw) else None
        except Exception:
            listing_d = None
        age = listing_age_trading_days(listing_d, session, cal)

        open_status = str(row.get("open_status", "unknown"))
        tradestatus = row.get("tradestatus")
        is_st = row.get("is_st_at_open")
        limit_up = row.get("limit_up")
        limit_down = row.get("limit_down")
        close = row.get("close")

        suspended = False
        if pd.notna(tradestatus):
            try:
                suspended = float(tradestatus) == 0.0
            except Exception:
                suspended = False
        if cfg.open_status_mode == "strict" and open_status in {"derived", "unknown", "halted"}:
            if open_status == "halted":
                suspended = True
            tradable_open = open_status == "trading"
        else:
            tradable_open = open_status in {"trading", "derived"} and not suspended

        st_flag = bool(is_st) if pd.notna(is_st) else False
        limit_up_buy_block = False
        limit_down_sell_block = False
        try:
            if pd.notna(limit_up) and pd.notna(close) and float(close) >= float(limit_up) - 1e-9:
                limit_up_buy_block = True
            if pd.notna(limit_down) and pd.notna(close) and float(close) <= float(limit_down) + 1e-9:
                limit_down_sell_block = True
        except Exception:
            pass

        med_amt = row.get(MEDIAN_AMOUNT_20D_FIELD)
        amount_gap = bool(pd.isna(row.get("amount")))
        if pd.isna(med_amt):
            if (
                cfg.open_status_mode == "research"
                and cfg.waive_u30_on_amount_gap
                and amount_gap
            ):
                adv_fail = False
                n_amount_gap_waived += 1
            else:
                adv_fail = True
        else:
            adv_fail = float(med_amt) < cfg.liquidity_threshold_cny
        listing_ok = age is not None and age >= cfg.listing_min_trading_days

        rows.append({
            "instrument_id": iid,
            "session": session,
            "listing_trading_days": age,
            "listing_ok": listing_ok,
            "suspended": suspended,
            "st_flag": st_flag,
            "tradable_open": tradable_open,
            "open_status": open_status,
            "limit_up_buy_block": limit_up_buy_block,
            "limit_down_sell_block": limit_down_sell_block,
            MEDIAN_AMOUNT_20D_FIELD: float(med_amt) if pd.notna(med_amt) else None,
            "adv_fail": adv_fail,
            FLOAT_MKTCAP_FIELD: (
                fm_lookup[iid]
                if iid in fm_lookup
                else (float(row[FLOAT_MKTCAP_FIELD]) if pd.notna(row.get(FLOAT_MKTCAP_FIELD)) else None)
            ),
            "float_mktcap_source": (
                fm_source_by_id.get(iid, float_mktcap_source)
                if iid in fm_lookup
                else (
                    "panel_derived"
                    if pd.notna(row.get(FLOAT_MKTCAP_FIELD))
                    else "none"
                )
            ),
            "data_gap": amount_gap or pd.isna(tradestatus),
            "panel_source": view.panel_source,
            "u30_waived_amount_gap": bool(
                pd.isna(med_amt)
                and cfg.open_status_mode == "research"
                and cfg.waive_u30_on_amount_gap
                and amount_gap
            ),
        })

    notes.extend(merge_notes_sample)
    notes.append(f"panels_loaded={n_merged}")
    if n_amount_gap_waived:
        notes.append(f"u30_waived_amount_gap_research={n_amount_gap_waived}")
    if session > cutoff:
        notes.append(f"extend_session_rows_seen≈{n_extend_only_row}")

    frame = pd.DataFrame(rows)
    n_in = len(frame)
    if frame.empty:
        return D1MaskResult(
            session=session,
            n_instruments_in=0,
            n_after_listing=0,
            n_after_tradable_st=0,
            n_after_u30=0,
            n_after_limits=0,
            n_after_mktcap=0,
            member_ids=(),
            frame=frame,
            promotion_approved=_gate(),
            sw_l1_promotable=False,
            float_mktcap_source=float_mktcap_source,
            notes=tuple(notes + ["empty_frame"]),
        )

    f1 = frame[frame["listing_ok"]].copy()
    f2 = f1[(~f1["suspended"]) & (~f1["st_flag"]) & (f1["tradable_open"])].copy()
    f3 = f2[~f2["adv_fail"]].copy()
    f4 = f3[~f3["limit_up_buy_block"]].copy()

    f5 = f4.copy()
    mkt = f5[FLOAT_MKTCAP_FIELD]
    valid = mkt.notna()
    if valid.any():
        mkt_cutoff = mkt[valid].quantile(cfg.exclude_bottom_mktcap_pct)
        f5 = f5[~valid | (mkt >= mkt_cutoff)].copy()
        notes.append(f"float_mktcap_bottom_pct_cutoff={mkt_cutoff}")
    else:
        notes.append("float_mktcap_all_null_skip_shell_filter")

    sw_path = resolve_sw_l1_path(sw_l1_path)
    sw_dataset_promotable = False
    if sw_path is not None:
        from quantlab.data.v2_readers import load_sw_l1_members

        sw_view = load_sw_l1_members(path=sw_path)
        sw = sw_view.frame
        sw_dataset_promotable = bool(sw_view.promotable)
        if "available_at" not in sw.columns or sw["available_at"].isna().any():
            raise ValueError("sw_l1_available_at_missing_or_null")
        assign = sw_l1_asof(sw, session, f5["instrument_id"].tolist())
        f5["industry_sw_l1_code"] = f5["instrument_id"].map(
            lambda i: assign.get(i).sw_code if i in assign else None
        )
        f5["industry_sw_l1_name"] = f5["instrument_id"].map(
            lambda i: assign.get(i).sw_name if i in assign else None
        )
        f5["industry_sw_l1_unknown"] = f5["instrument_id"].map(
            lambda i: assign.get(i).is_unknown_bucket if i in assign else True
        )
        f5["industry_sw_l1_quality"] = f5["instrument_id"].map(
            lambda i: (assign.get(i).quality_status if i in assign else None)
        )
        f5["industry_sw_l1_promotable"] = sw_dataset_promotable
        notes.append(f"sw_l1_path={sw_path}")
        notes.append(f"sw_l1_table={SW_L1_TABLE_NAME}")
        notes.append(f"sw_l1_source_variant={sw_view.source_variant}")
        notes.append(f"sw_l1_dataset_promotable={str(sw_dataset_promotable).lower()}")
        notes.append(
            f"sw_l1_dataset_promotion_approved={str(bool(sw_view.promotion_approved)).lower()}"
        )
        notes.append(f"sw_l1_quality_label={sw_view.quality_label}")
        notes.append(f"overall_promotion_approved={str(_gate()).lower()}")
    else:
        notes.append(f"sw_l1_missing:{SW_L1_TABLE_NAME}")
        f5["industry_sw_l1_code"] = None
        f5["industry_sw_l1_name"] = None
        f5["industry_sw_l1_unknown"] = True
        f5["industry_sw_l1_quality"] = None
        f5["industry_sw_l1_promotable"] = False

    notes.append(f"float_mktcap_source={float_mktcap_source}")

    members = tuple(f5["instrument_id"].tolist())
    return D1MaskResult(
        session=session,
        n_instruments_in=n_in,
        n_after_listing=len(f1),
        n_after_tradable_st=len(f2),
        n_after_u30=len(f3),
        n_after_limits=len(f4),
        n_after_mktcap=len(f5),
        member_ids=members,
        frame=f5,
        promotion_approved=_gate(),
        sw_l1_promotable=sw_dataset_promotable,
        float_mktcap_source=float_mktcap_source,
        notes=tuple(notes),
    )


# ---------------------------------------------------------------------------
# Pseudocode (module path map) — kept as docstring for Eng/Data handshake
# ---------------------------------------------------------------------------
PSEUDOCODE = """
MODULE MAP
  quantlab.universe.mask          # Phase-0 contracts / StubUniverseMaskProvider
  quantlab.universe.d1_masks      # THIS: executable D1 pipeline
  quantlab.v2_schemas             # frozen SW_L1 / 510300 / float_mktcap names
  quantlab.data.v2_d0_meta        # D0 calendar/instruments probe
  data/v2/sw_l1_pit/industry_members_sw_l1.parquet
  data/v2/etf_510300/panels/sh.510300.parquet
  data/local_market/1c85.../panels/*.parquet
  data/v2/asof_extend_202610/panels/*.parquet  # session > d0_as_of only
  quantlab.data.v2_readers.load_merged_panel   # D0+extend research merge

PSEUDOCODE membership_at(session t):
  instruments ← read instruments.parquet (historical, asset_type in {stock, equity_etf})
  calendar    ← read calendar.parquet
  for each instrument i:
      panel ← merge(D0 panels/i[session<=cutoff], extend panels/i[session>cutoff])
      age   ← count sessions in [listing_date, t]
      float_mktcap[i,t] ← panel.float_mktcap OR close*volume/(turnover/100)
      median_amount_20d[i,t] ← median(amount[t-19..t])
      flags ← {suspended, st_flag, limit_up_buy_block, limit_down_sell_block,
               open_status, data_gap}
  U ← {i | age>=120}
  U ← {i in U | not suspended and not st_flag and tradable_open}
  U ← {i in U | median_amount_20d >= threshold}          # U30
  U ← {i in U | not limit_up_buy_block}                  # buy eligibility
  U ← {i in U | float_mktcap >= quantile_30%(U)}         # shell filter
  attach SW_L1 from industry_members_sw_l1 where
      in_date<=t and (out_date is null or out_date>t)
      and available_at not null
  return UniverseMembership(promotion_approved=False, ...)
"""
