"""L0 universe membership + tradability masks (Phase 0 interface).

Mask-first: eligibility and buy/sell permission precede factor ranking.

Data contracts (frozen field names — see :mod:`quantlab.v2_schemas`):
  - calendar.parquet: session
  - instruments.parquet: instrument_id, available_at, effective_at, active,
    is_st, listing_date, delist_date, asset_type, quality_status, ...
  - panels/<id>.parquet mask cols: tradestatus, is_st_at_open, limit_up,
    limit_down, open_status, open_status_available_at, amount, turnover,
    available_at, quality_status
  - float_mktcap PIT (:class:`quantlab.v2_schemas.FloatMktcapAsOf`)
  - industry_members_sw_l1 (:class:`quantlab.v2_schemas.SWL1MemberRow`)
    **not** D0 ``industry_records`` (csrc proxy)

D0 landed path (meta/calendar readable now):
  ``data/local_market/1c85fd9aceaa03c3c4863bec/``

Full membership application stays NotImplemented until SW_L1 PIT + float_mktcap
land. Smoke may probe calendar/instruments via :class:`D0MetaStore`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from quantlab.mandate_v2 import MandateV2
from quantlab.v2_schemas import (
    FLOAT_MKTCAP_FIELD,
    PANEL_MASK_COLUMNS,
    SW_L1_COLUMN_SPEC,
    SW_L1_TABLE_NAME,
    SWL1AsOfAssignment,
    SWL1MemberRow,
)

# Mandate ``universe.tradability_masks`` names (stable string ids).
MASK_NAMES: tuple[str, ...] = (
    "suspended",
    "limit_up_buy_block",
    "limit_down_sell_block",
    "st_flag",
    "adv_fail",
    "data_gap",
)


@dataclass(frozen=True)
class TradabilityMaskRow:
    """Per-instrument tradability flags at one decision cutoff (PIT-safe)."""

    instrument_id: str
    session: date
    in_universe: bool
    asset_type: str  # stock | equity_etf
    listing_trading_days: int | None
    suspended: bool
    limit_up_buy_block: bool
    limit_down_sell_block: bool
    st_flag: bool
    adv_fail: bool
    data_gap: bool
    may_buy: bool
    may_sell: bool
    open_status: str | None = None
    float_mktcap: float | None = None  # field name locked: float_mktcap
    median_amount_20d: float | None = None
    # SW_L1 as-of (from industry_members_sw_l1 — frozen schema)
    industry_sw_l1_code: str | None = None  # sw_code
    industry_sw_l1_name: str | None = None  # sw_name
    industry_sw_l1_available_at: datetime | None = None
    quality_status: str | None = None
    available_at: datetime | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class UniverseMembership:
    """Typed empty-capable membership snapshot for one decision date."""

    session: date
    decision_cutoff_note: str
    mandate_id: str
    liquidity_label: str
    listing_min_trading_days: int
    microcap_mode: str
    exclude_bottom_mktcap_pct: float
    member_ids: tuple[str, ...]
    rows: tuple[TradabilityMaskRow, ...]
    sw_l1_assignments: tuple[SWL1AsOfAssignment, ...] = ()
    promotion_approved: bool = False
    data_ready: bool = False
    d0_root: str | None = None
    calendar_ok: bool = False
    todos: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("universe_membership_promotion_approved_must_be_false")


def empty_membership(
    session: date,
    mandate: MandateV2,
    *,
    reason: str,
    d0_root: str | None = None,
    calendar_ok: bool = False,
) -> UniverseMembership:
    """Typed empty membership with explicit Data TODOs (no fake member ids)."""
    u = mandate.universe
    todos = (
        reason,
        f"TODO(Data): table {SW_L1_TABLE_NAME} columns="
        + ",".join(n for n, _ in SW_L1_COLUMN_SPEC),
        f"TODO(Data): PIT {FLOAT_MKTCAP_FIELD} for exclude_bottom_mktcap_pct",
        "TODO(Data): median_amount_20d from panels.amount for U30",
        "TODO(Eng): apply mask-first pipeline once SW_L1 + float_mktcap land",
        f"panel_mask_columns_expected={','.join(PANEL_MASK_COLUMNS)}",
        "promotion_approved=false",
    )
    return UniverseMembership(
        session=session,
        decision_cutoff_note=f"Asia/Shanghai {mandate.rebalance.decision_time_china}",
        mandate_id=mandate.mandate_id,
        liquidity_label=u.liquidity_rule.active_label,
        listing_min_trading_days=u.listing_min_trading_days,
        microcap_mode=u.microcap_policy.mode,
        exclude_bottom_mktcap_pct=u.microcap_policy.exclude_bottom_mktcap_pct,
        member_ids=(),
        rows=(),
        sw_l1_assignments=(),
        promotion_approved=False,
        data_ready=False,
        d0_root=d0_root,
        calendar_ok=calendar_ok,
        todos=todos,
    )


class UniverseMaskProvider(Protocol):
    def membership_at(self, session: date) -> UniverseMembership: ...

    def mask_rows(self, session: date, instrument_ids: Sequence[str]) -> tuple[TradabilityMaskRow, ...]: ...

    def sw_l1_asof(self, session: date, instrument_ids: Sequence[str]) -> tuple[SWL1AsOfAssignment, ...]: ...


@dataclass(frozen=True)
class StubUniverseMaskProvider:
    """Phase 0 stub: D0 calendar/meta probe; SW_L1 / full membership NotImplemented."""

    mandate: MandateV2
    d0_root: str | Path | None = None

    def _store(self):
        from quantlab.data.v2_d0_meta import D0MetaStore, DEFAULT_D0_ROOT

        root = self.d0_root if self.d0_root is not None else DEFAULT_D0_ROOT
        return D0MetaStore(root)

    def membership_at(self, session: date) -> UniverseMembership:
        store = self._store()
        try:
            store.require_session(session)
            calendar_ok = True
            reason = (
                f"D0 calendar ok for {session}; full V2 membership blocked — "
                f"need {SW_L1_TABLE_NAME} PIT + {FLOAT_MKTCAP_FIELD} "
                "(not inventing eligible ids)"
            )
        except FileNotFoundError as exc:
            return empty_membership(
                session,
                self.mandate,
                reason=f"d0_unavailable:{exc}",
                d0_root=None,
                calendar_ok=False,
            )
        except ValueError as exc:
            return empty_membership(
                session,
                self.mandate,
                reason=str(exc),
                d0_root=str(store.root),
                calendar_ok=False,
            )
        return empty_membership(
            session,
            self.mandate,
            reason=reason,
            d0_root=str(store.root),
            calendar_ok=calendar_ok,
        )

    def mask_rows(self, session: date, instrument_ids: Sequence[str]) -> tuple[TradabilityMaskRow, ...]:
        if not instrument_ids:
            return ()
        raise NotImplementedError(
            "tradability_mask_loader_not_implemented:"
            f"need panels mask cols {PANEL_MASK_COLUMNS} applied PIT; "
            f"n_ids={len(instrument_ids)} session={session}"
        )

    def sw_l1_asof(self, session: date, instrument_ids: Sequence[str]) -> tuple[SWL1AsOfAssignment, ...]:
        """Frozen return type; loader awaits industry_members_sw_l1.parquet."""
        _ = (session, instrument_ids, SWL1MemberRow.SCHEMA_VERSION)
        raise NotImplementedError(
            "sw_l1_pit_loader_not_implemented:"
            f"await table={SW_L1_TABLE_NAME} schema={SWL1MemberRow.SCHEMA_VERSION}; "
            "D0 industry_records is csrc_2012 effective_date_proxy — do not substitute"
        )

    def describe_contract(self) -> Mapping[str, object]:
        u = self.mandate.universe
        d0_info: dict[str, object] = {"wired": False}
        try:
            probe = self._store().probe()
            d0_info = {
                "wired": True,
                "root": probe.manifest.root,
                "calendar_n_sessions": probe.calendar.n_sessions,
                "calendar_first": str(probe.calendar.first_session),
                "calendar_last": str(probe.calendar.last_session),
                "instruments_n": probe.instruments.n_unique_ids,
                "asset_types": dict(probe.instruments.asset_type_counts),
                "has_float_mktcap": probe.instruments.has_float_mktcap,
                "has_510300": probe.instruments.has_510300,
                "sw_l1_pit_ready": probe.industry_gap.sw_l1_pit_ready,
                "benchmark_id": probe.benchmark.code,
            }
        except FileNotFoundError as exc:
            d0_info = {"wired": False, "error": str(exc)}
        return {
            "layer": "L0_tradability_universe_mask",
            "mask_first": u.mask_first,
            "mask_names": list(MASK_NAMES),
            "mandate_masks": list(u.tradability_masks),
            "listing_min_trading_days": u.listing_min_trading_days,
            "liquidity_label": u.liquidity_rule.active_label,
            "liquidity_threshold_cny": u.liquidity_rule.threshold_cny_active,
            "microcap_mode": u.microcap_policy.mode,
            "exclude_bottom_mktcap_pct": u.microcap_policy.exclude_bottom_mktcap_pct,
            "sw_l1_table": SW_L1_TABLE_NAME,
            "sw_l1_schema_version": SWL1MemberRow.SCHEMA_VERSION,
            "float_mktcap_field": FLOAT_MKTCAP_FIELD,
            "promotion_approved": False,
            "d0": d0_info,
        }


# ---------------------------------------------------------------------------
# Contract-based prototype (consumes V2 Data paths)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PrototypeUniverseMaskProvider:
    """L0 mask prototype over merged D0+asof_extend panels + float_mktcap + SW_L1.

    Panels resolve via :func:`quantlab.data.v2_readers.load_merged_panel`
    (D0 through ``d0_as_of``, then asof_extend). Overall
    ``promotion_approved`` stays False; SW dataset ``sw_l1_promotable`` may
    be True for accepted tushare. Sample ``max_instruments`` for smoke speed;
    full-universe is opt-in.
    """

    mandate: MandateV2
    d0_root: str | Path | None = None
    max_instruments: int | None = 300
    open_status_mode: str = "research"

    def _roots(self):
        from quantlab.data.v2_readers import default_v2_roots

        roots = default_v2_roots()
        if self.d0_root is not None:
            from dataclasses import replace

            roots = replace(roots, d0_root=Path(self.d0_root))
        return roots

    def membership_at(self, session: date) -> UniverseMembership:
        from quantlab.data.v2_readers import load_float_mktcap_asof, load_sw_l1_members
        from quantlab.universe.d1_masks import D1MaskConfig, build_d1_masks_for_session

        self.mandate.require_not_promoted()
        roots = self._roots()
        u = self.mandate.universe
        todos: list[str] = [
            "promotion_approved=false",
            "prototype_not_live_trading",
        ]

        # Validate SW_L1 contract (fail loud on missing available_at).
        sw_view = load_sw_l1_members(roots=roots)
        todos.append(f"sw_l1_source_variant={sw_view.source_variant}")
        todos.append(f"sw_l1_dataset_promotable={str(bool(sw_view.promotable)).lower()}")
        todos.append(
            f"sw_l1_dataset_promotion_approved={str(bool(sw_view.promotion_approved)).lower()}"
        )
        todos.append(f"sw_l1_rows={sw_view.n_rows}")
        todos.append(f"sw_l1_quality_label={sw_view.quality_label}")

        fm_view = load_float_mktcap_asof(roots=roots)
        todos.append(f"float_mktcap_non_null={fm_view.n_non_null}/{fm_view.n_rows}")
        todos.append(f"float_mktcap_session={fm_view.session}")

        cfg = D1MaskConfig(
            listing_min_trading_days=u.listing_min_trading_days,
            exclude_bottom_mktcap_pct=u.microcap_policy.exclude_bottom_mktcap_pct,
            liquidity_threshold_cny=u.liquidity_rule.threshold_cny_active,
            open_status_mode=self.open_status_mode,  # type: ignore[arg-type]
        )
        result = build_d1_masks_for_session(
            session,
            d0_root=roots.d0_root,
            asof_extend_dir=roots.asof_extend_dir,
            config=cfg,
            max_instruments=self.max_instruments,
            sw_l1_path=roots.sw_l1_path,
            float_mktcap_path=roots.float_mktcap_path,
        )
        if result.promotion_approved:
            raise RuntimeError("mask_result_overall_promotion_approved_leaked_true")

        rows: list[TradabilityMaskRow] = []
        assignments: list[SWL1AsOfAssignment] = []
        if not result.frame.empty:
            for _, r in result.frame.iterrows():
                iid = str(r["instrument_id"])
                sw_code = r.get("industry_sw_l1_code")
                sw_name = r.get("industry_sw_l1_name")
                sw_code_s = None if sw_code is None or (isinstance(sw_code, float) and pd_isna(sw_code)) else str(sw_code)
                sw_name_s = None if sw_name is None or (isinstance(sw_name, float) and pd_isna(sw_name)) else str(sw_name)
                qs = r.get("industry_sw_l1_quality")
                qs_s = None if qs is None or (isinstance(qs, float) and pd_isna(qs)) else str(qs)
                unknown = bool(r.get("industry_sw_l1_unknown", True))
                assignments.append(
                    SWL1AsOfAssignment(
                        instrument_id=iid,
                        session=session,
                        sw_code=sw_code_s,
                        sw_name=sw_name_s,
                        available_at=None,
                        quality_status=qs_s,
                        is_unknown_bucket=unknown,
                    )
                )
                med = r.get("median_amount_20d")
                fm = r.get("float_mktcap")
                rows.append(
                    TradabilityMaskRow(
                        instrument_id=iid,
                        session=session,
                        in_universe=True,
                        asset_type="stock",
                        listing_trading_days=int(r["listing_trading_days"])
                        if r.get("listing_trading_days") is not None and not pd_isna(r.get("listing_trading_days"))
                        else None,
                        suspended=bool(r.get("suspended", False)),
                        limit_up_buy_block=bool(r.get("limit_up_buy_block", False)),
                        limit_down_sell_block=bool(r.get("limit_down_sell_block", False)),
                        st_flag=bool(r.get("st_flag", False)),
                        adv_fail=bool(r.get("adv_fail", False)),
                        data_gap=bool(r.get("data_gap", False)),
                        may_buy=not bool(r.get("limit_up_buy_block", False))
                        and not bool(r.get("suspended", False))
                        and not bool(r.get("st_flag", False)),
                        may_sell=not bool(r.get("limit_down_sell_block", False)),
                        open_status=None if pd_isna(r.get("open_status")) else str(r.get("open_status")),
                        float_mktcap=None if fm is None or pd_isna(fm) else float(fm),
                        median_amount_20d=None if med is None or pd_isna(med) else float(med),
                        industry_sw_l1_code=sw_code_s,
                        industry_sw_l1_name=sw_name_s,
                        industry_sw_l1_available_at=None,
                        quality_status=(
                            f"research_prototype;sw_l1_dataset_promotable="
                            f"{str(bool(sw_view.promotable)).lower()}"
                        ),
                        available_at=None,
                        notes=(
                            f"sw_l1_dataset_promotable={str(bool(sw_view.promotable)).lower()}",
                            "overall_promotion_approved=false",
                        ),
                    )
                )

        todos.extend(list(result.notes[:8]))
        if self.max_instruments is not None:
            todos.append(f"sampled_max_instruments={self.max_instruments}")

        return UniverseMembership(
            session=session,
            decision_cutoff_note=f"Asia/Shanghai {self.mandate.rebalance.decision_time_china}",
            mandate_id=self.mandate.mandate_id,
            liquidity_label=u.liquidity_rule.active_label,
            listing_min_trading_days=u.listing_min_trading_days,
            microcap_mode=u.microcap_policy.mode,
            exclude_bottom_mktcap_pct=u.microcap_policy.exclude_bottom_mktcap_pct,
            member_ids=result.member_ids,
            rows=tuple(rows),
            sw_l1_assignments=tuple(assignments),
            promotion_approved=False,
            data_ready=True,  # contract paths present; still research-only
            d0_root=str(roots.d0_root),
            calendar_ok=True,
            todos=tuple(todos),
        )

    def mask_rows(self, session: date, instrument_ids: Sequence[str]) -> tuple[TradabilityMaskRow, ...]:
        mem = self.membership_at(session)
        wanted = set(instrument_ids)
        return tuple(r for r in mem.rows if r.instrument_id in wanted)

    def sw_l1_asof(self, session: date, instrument_ids: Sequence[str]) -> tuple[SWL1AsOfAssignment, ...]:
        from quantlab.data.v2_readers import load_sw_l1_members, sw_l1_asof_assignments

        view = load_sw_l1_members(roots=self._roots())
        # Dataset may be promotable (accepted tushare); overall stays research.
        return sw_l1_asof_assignments(view.frame, session, instrument_ids)

    def describe_contract(self) -> Mapping[str, object]:
        stub = StubUniverseMaskProvider(self.mandate, d0_root=self.d0_root)
        base = dict(stub.describe_contract())
        base["provider"] = "PrototypeUniverseMaskProvider"
        try:
            from quantlab.data.v2_readers import load_sw_l1_members

            sw = load_sw_l1_members(roots=self._roots())
            base["sw_l1_promotable"] = bool(sw.promotable)
            base["sw_l1_dataset_promotion_approved"] = bool(sw.promotion_approved)
            base["sw_l1_source_variant"] = sw.source_variant
        except Exception as exc:  # noqa: BLE001 — describe must not raise
            base["sw_l1_promotable"] = False
            base["sw_l1_describe_error"] = f"{type(exc).__name__}:{exc}"
        base["max_instruments"] = self.max_instruments
        base["promotion_approved"] = False
        return base


def pd_isna(value: object) -> bool:
    """Local na check avoiding importing pandas at module import for stub path."""
    try:
        import pandas as pd

        return bool(pd.isna(value))
    except Exception:
        return value is None
