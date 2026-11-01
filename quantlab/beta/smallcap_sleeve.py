"""Standalone small-cap β sleeve (research; parallel to core 510300).

Leo 2026-10-10 21:30 ET: promote small-cap from the default-OFF satellite menu to
a standalone stock-basket sleeve, not bound by Mandate ``max_etf``. Mandate JSON
is NOT edited; ``promotion_approved`` is always False.

Universe (adapted from the M2 replication in ``research/attrib_v2/benchmarks.py``):
  history >= 253 sessions, not ST, trading, 20d mean float cap known
  → float-cap rank 3001–5000 (absolute) or bottom 40% (relative fallback)
  → ADV60 floor (tail-risk control; drops reported)
  → pe_ttm > 0 and 0 < PB <= 3 (hard filter with tier fallback)
  → seeded order, retain current holdings inside top 150, SW_L1 industry cap
  → ~50 names, equal weight inside the sleeve
Old "exclude smallest 30% mktcap" filter is dropped (research override).

Outputs are selections, weights, risk flags and a stress-test harness.
Performance (CAGR/MDD/Sharpe) is NOT produced: the backtest engine currently
books limit/halt days as 0 return and is being fixed by Strategy/Eng.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Sequence

from quantlab.config import ROOT
from quantlab.mandate_v2 import MandateV2

SMALLCAP_CONFIG_PATH = Path(__file__).resolve().parent / "configs" / "smallcap_standalone_v1.json"


def load_smallcap_config(path: str | Path | None = None) -> dict:
    cfg_path = Path(path) if path else SMALLCAP_CONFIG_PATH
    raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    raw["promotion_approved"] = False
    raw["config_path"] = str(cfg_path.resolve())
    return raw


# ---------------------------------------------------------------------------
# Data (research panels built from box data; no invented OHLC/fundamentals)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SmallcapPanels:
    close: object
    ret: object
    amount: object
    trad: object
    st: object
    lu: object
    ld: object
    circ_mv: object
    pe_ttm: object
    pb: object
    turnover_rate: object
    etf_ret: object
    hist: object
    adv: object
    cap: object
    sw: object
    panels_dir: str
    gaps: tuple[str, ...]


@lru_cache(maxsize=2)
def _load_panels_cached(panels_dir: str, sw_path: str, cap_window: int, adv_window: int, adv_min: int) -> SmallcapPanels:
    import pandas as pd

    P = Path(panels_dir)
    need = ["close", "ret", "amount", "trad", "st", "lu", "ld"]
    missing = [k for k in need if not (P / f"{k}.parquet").is_file()]
    if missing:
        raise FileNotFoundError(f"smallcap_panels_missing:{P}:{','.join(missing)}")
    D = {k: pd.read_parquet(P / f"{k}.parquet") for k in need}
    cols = D["close"].columns
    gaps: list[str] = []
    for k in ("circ_mv", "pe_ttm", "pb", "turnover_rate"):
        f = P / f"db_{k}.parquet"
        if f.is_file():
            D[k] = pd.read_parquet(f).reindex(columns=cols)
        else:
            D[k] = pd.DataFrame(index=D["close"].index, columns=cols, dtype="float32")
            gaps.append(f"db_{k}_missing")
    etf_f = P / "etf510300.parquet"
    etf_ret = pd.read_parquet(etf_f)["ret"].astype("float64") if etf_f.is_file() else None
    if etf_ret is None:
        gaps.append("etf510300_ret_missing")

    hist = D["close"].notna().cumsum()
    pos = D["amount"].where(D["amount"] > 0)
    adv = pos.rolling(adv_window, min_periods=adv_min).mean()
    cap = D["circ_mv"].rolling(cap_window, min_periods=10).mean() * 1e4  # 万元 → CNY

    sw = pd.read_parquet(sw_path) if Path(sw_path).is_file() else None
    if sw is None:
        gaps.append("sw_l1_missing")
    else:
        sw = sw.copy()
        sw["in_date"] = pd.to_datetime(sw["in_date"])
        sw["out_date"] = pd.to_datetime(sw["out_date"])
    return SmallcapPanels(
        close=D["close"], ret=D["ret"], amount=D["amount"], trad=D["trad"], st=D["st"],
        lu=D["lu"], ld=D["ld"], circ_mv=D["circ_mv"], pe_ttm=D["pe_ttm"], pb=D["pb"],
        turnover_rate=D["turnover_rate"], etf_ret=etf_ret, hist=hist, adv=adv, cap=cap,
        sw=sw, panels_dir=str(P.resolve()), gaps=tuple(gaps),
    )


@lru_cache(maxsize=4)
def _panels_first_usable(panels_dir: str, min_hist: int):
    """First session with >= min_hist sessions in the 2023+ panels (reads only the index column)."""
    import pandas as pd
    import pyarrow.parquet as pq

    f = Path(panels_dir) / "close.parquet"
    if not f.is_file():
        return None
    pf = pq.ParquetFile(f)
    idx_cols = [c for c in (pf.schema_arrow.pandas_metadata or {}).get("index_columns", []) if isinstance(c, str)]
    if not idx_cols:
        return None
    idx = pd.to_datetime(pq.read_table(f, columns=idx_cols).column(0).to_pandas()).sort_values()
    return idx.iloc[min_hist] if len(idx) > min_hist else None


@lru_cache(maxsize=2)
def _load_basket_cache(path: str) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text())["baskets"] if p.is_file() else {}


def precompute_history_baskets(sessions, path: str | Path, *, chain_retention: bool = True) -> dict:
    """Build chained (retention-aware) 2015+ baskets for a rebalance schedule and save JSON.

    Provider(data_source='history_2015', basket_cache=path).basket(session) then reads them
    (when called without ``current``)."""
    import pandas as pd

    from quantlab.beta.smallcap_history_selector import select

    out, prev = {}, None
    for s_ in sessions:
        r = select(s_, current=prev if chain_retention else None)
        out[str(pd.Timestamp(s_).date())] = r
        prev = r.get("names")
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"promotion_approved": False, "chain_retention": chain_retention,
                             "source": "smallcap_history_selector (history_2015)", "baskets": out}, default=str))
    _load_basket_cache.cache_clear()
    return out


@lru_cache(maxsize=1)
def _load_st_daily(path: str):
    """Data's is_st_daily table (only ST=True rows) → {Timestamp: frozenset(iid)}."""
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    d = pd.read_parquet(fp)
    d = d[d["is_st_at_open"].astype(bool)]
    return {pd.Timestamp(k): frozenset(v) for k, v in d.groupby("trade_date")["instrument_id"]}


@lru_cache(maxsize=1)
def _load_audit_annual(path: str):
    """Annual (end_date month 12) audit opinions; available date = available_at local date."""
    import pandas as pd

    fp = ROOT / path
    if not fp.exists():
        return None
    a = pd.read_parquet(fp)
    a = a[a["end_date"].dt.month == 12].copy()
    a["avail_date"] = pd.to_datetime(a["available_at"].dt.tz_convert("Asia/Shanghai").dt.date)
    return a.sort_values(["instrument_id", "end_date", "avail_date"])


@lru_cache(maxsize=1)
def _load_namechange_st(glob_pat: str):
    """Tushare namechange rows whose name contains 'ST' (PIT via ann_date)."""
    import glob

    import pandas as pd

    files = sorted(glob.glob(str(ROOT / glob_pat)))
    if not files:
        return None
    nc = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    nc = nc[nc["name"].astype(str).str.upper().str.contains("ST", na=False)].copy()
    ex = {"SH": "sh", "SZ": "sz", "BJ": "bj"}
    nc["iid"] = nc["ts_code"].map(lambda s: ex.get(s.split(".")[1], "x") + "." + s.split(".")[0])
    for col in ("start_date", "end_date", "ann_date"):
        nc[col] = pd.to_datetime(nc[col], format="%Y%m%d", errors="coerce")
    return nc


def _priority(seed: int, code: str) -> int:
    return int(hashlib.sha256(f"{seed}:{code}".encode()).hexdigest()[:12], 16)


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SmallcapBasket:
    session: date
    data_session: date | None
    names: tuple[str, ...]
    industries: Mapping[str, str]
    band_used: str
    funnel: Mapping[str, int]
    filters_hit: Mapping[str, int]
    industry_mix: Mapping[str, int]
    adv_stats: Mapping[str, float | None]
    fundamentals_fallback_used: int
    data_ready: bool
    promotion_approved: bool = False
    notes: tuple[str, ...] = ()
    # Full ranked candidate pool (selection order) for capacity-aware tier baskets
    ranked_pool: tuple[str, ...] = ()
    ranked_industries: Mapping[str, str] = field(default_factory=dict)
    retained_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("smallcap_basket_promotion_approved_must_be_false")


@dataclass(frozen=True)
class SmallcapTierWeights:
    tier: str
    sleeve_weight_target: float
    sleeve_weight_effective: float
    per_name_weight: float
    name_weights: Mapping[str, float]
    single_name_cap_book: float
    single_name_cap_binding: bool
    per_name_notional_cny: float
    min_trade_feasible: bool
    lot_infeasible_names: int
    adv_capacity_breaches: int
    promotion_approved: bool = False

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("smallcap_tier_promotion_approved_must_be_false")


@dataclass(frozen=True)
class SmallcapSleevePlan:
    session: date
    basket: SmallcapBasket
    tiers: Mapping[str, SmallcapTierWeights]
    crowding: Mapping[str, object]
    beta_descriptive: Mapping[str, object]
    interaction_with_core: Mapping[str, object] | None
    capacity: Mapping[str, object] = field(default_factory=dict)
    bound_by_max_etf: bool = False
    performance_reporting: str = "blocked_until_engine_limit_fix"
    promotion_approved: bool = False
    todos: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.promotion_approved:
            raise ValueError("smallcap_sleeve_promotion_approved_must_be_false")


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SmallcapBetaSleeveProvider:
    """Standalone small-cap β sleeve, parallel to the core 510300 sleeve."""

    mandate: MandateV2
    config_path: str | Path | None = None
    seed: int | None = None
    # 'auto' (default): 2023+ research_attrib_v2 panels when they have >=253 sessions of history
    # before the session, else the 2015+ history path. 'history_2015': always the light 2015+ path
    # (smallcap_history_selector + float_mktcap_from2015 + daily_basic caches). 'panels_2023': legacy only.
    data_source: str = "auto"
    # Optional JSON {session: [names]} from precompute_history_baskets(); history path only.
    basket_cache: str | Path | None = None

    # -- infra --
    def config(self) -> dict:
        return load_smallcap_config(self.config_path)

    def _panels(self) -> SmallcapPanels:
        cfg = self.config()
        rc = cfg["risk_controls"]
        return _load_panels_cached(
            str((ROOT / cfg["data"]["panels_dir"]).resolve()),
            str((ROOT / cfg["data"]["sw_l1"]).resolve()),
            int(cfg["universe"]["cap_window"]),
            int(rc["adv_window"]),
            int(rc["adv_min_periods"]),
        )

    def _use_history(self, session) -> bool:
        mode = (self.data_source or "auto").lower()
        if mode == "history_2015":
            return True
        if mode == "panels_2023":
            return False
        import pandas as pd

        first = _panels_first_usable(str((ROOT / self.config()["data"]["panels_dir"]).resolve()),
                                     int(self.config()["universe"]["min_history_sessions"]))
        return first is None or pd.Timestamp(session) < first

    def _panels_for(self, session) -> SmallcapPanels:
        if self._use_history(session):
            from quantlab.beta.smallcap_history_panels import load_history_panels

            return load_history_panels()
        return self._panels()

    def _history_basket(self, session: date, current: Sequence[str] | None, retain_top_override: int | None) -> SmallcapBasket:
        import pandas as pd

        if self.basket_cache:
            cached = _load_basket_cache(str(self.basket_cache))
            hit = cached.get(str(pd.Timestamp(session).date()))
            if hit is not None and current is None:
                r = hit
            else:
                r = None
        else:
            r = None
        if r is None:
            from quantlab.beta.smallcap_history_selector import select

            r = select(session, current=current, retain_top=retain_top_override)
        names = tuple(r.get("names", ()))
        ok = bool(r.get("ok")) and len(names) > 0
        notes = ["data_source=history_2015", "adv=turnover_rate×circ_mv proxy", "band: abs 3001-5000 if N>=5000 else bottom 40%"]
        if r.get("history_truncated"):
            notes.append("history_truncated_pre_2016")
        if len(names) < int(self.config()["selection"]["target_names"]):
            notes.append(f"basket_short:{len(names)}")
        return SmallcapBasket(
            session=session,
            data_session=pd.Timestamp(r["data_session"]).date() if r.get("data_session") else None,
            names=names,
            industries=dict(r.get("industries", {})),
            band_used=str(r.get("band_mode", "none")),
            funnel={"universe": int(r.get("universe", 0)), "pool": int(r.get("pool", 0)),
                    "fund_pass": int(r.get("fund_pass", 0)), "selected": len(names)},
            filters_hit={k: int(v) for k, v in (r.get("filters") or {}).items()},
            industry_mix=dict(r.get("industry_mix", {})),
            adv_stats={},
            fundamentals_fallback_used=int(r.get("fund_fallback", 0)),
            data_ready=ok,
            notes=tuple(notes),
            ranked_pool=tuple(r.get("ranked_pool", names)),
            ranked_industries=dict(r.get("ranked_industries", r.get("industries", {}))),
            retained_order=tuple(c for c in (current or ()) if c in set(names)),
        )

    @staticmethod
    def _data_day(Dp: SmallcapPanels, session: date):
        import pandas as pd

        idx = Dp.close.index
        ts = pd.Timestamp(session)
        prior = idx[idx <= ts]
        return prior[-1] if len(prior) else None

    def _industry_on(self, Dp: SmallcapPanels, day, codes: Sequence[str]) -> dict[str, str]:
        if Dp.sw is None:
            return {c: "unknown" for c in codes}
        s = Dp.sw
        m = s[(s.in_date <= day) & (s.out_date.isna() | (s.out_date > day))]
        m = m.drop_duplicates("instrument_id", keep="last").set_index("instrument_id")["sw_code"]
        out = {}
        for c in codes:
            v = m.get(c)
            out[c] = str(v) if isinstance(v, str) and v else "unknown"
        return out

    # -- basket --
    def basket(
        self,
        session: date,
        *,
        current: Sequence[str] | None = None,
        min_history_override: int | None = None,
        retain_top_override: int | None = None,
        ranking_mode_override: str | None = None,
    ) -> SmallcapBasket:
        """Select the small-cap basket for ``session`` (membership only; no returns)."""
        import pandas as pd

        self.mandate.require_not_promoted()
        if self._use_history(session):
            return self._history_basket(session, current, retain_top_override)
        cfg = self.config()
        U, Fd, S, rc = cfg["universe"], cfg["fundamentals"], cfg["selection"], cfg["risk_controls"]
        seed = int(self.seed if self.seed is not None else S["seed"])
        Dp = self._panels()
        day = self._data_day(Dp, session)
        notes: list[str] = list(Dp.gaps)
        if day is None:
            return SmallcapBasket(
                session=session, data_session=None, names=(), industries={}, band_used="none",
                funnel={}, filters_hit={}, industry_mix={}, adv_stats={}, fundamentals_fallback_used=0,
                data_ready=False, notes=tuple(notes + ["no_panel_session_on_or_before"]),
            )
        if day.date() != session:
            notes.append(f"data_session_shift={day.date()}")

        listed = Dp.close.loc[day].notna()
        n_listed = int(listed.sum())
        min_hist = int(U["min_history_sessions"]) if min_history_override is None else int(min_history_override)
        if min_history_override is not None:
            notes.append(f"min_history_override={min_hist}:history_truncated_by_panel_start")
        hist_ok = Dp.hist.loc[day] >= min_hist
        RX = cfg.get("risk_exclusions") or {}
        risk_info: dict = {}
        # --- ST: Data is_st_daily (primary) ; namechange PIT fallback ; panel diagnostic ---
        st_panel = (Dp.st.loc[day] == 1)
        st_flag = st_panel.copy()
        st_cfg = RX.get("st") or {}
        if U.get("exclude_st", True) and st_cfg.get("enabled", True):
            idx_s = st_flag.index.to_series()
            daily = _load_st_daily(st_cfg.get("daily_table", "data/v2/st_flags/is_st_daily_2018_2026.parquet"))
            nc = _load_namechange_st(st_cfg.get("namechange_glob", "data/v2/tushare_raw/namechange/*.parquet"))
            st_nc = None
            if nc is not None:
                act = nc[(nc.start_date <= day) & (nc.end_date.isna() | (nc.end_date >= day)) & (nc.ann_date <= day)]
                st_nc = idx_s.isin(set(act["iid"])).to_numpy()
            if daily is not None and day >= min(daily):
                st_tab = idx_s.isin(daily.get(day, frozenset())).to_numpy()
                st_flag = pd.Series(st_tab, index=st_flag.index)
                risk_info["st_source"] = "is_st_daily_table"
                risk_info["st_table_flagged_on_listed"] = int((listed & st_flag).sum())
                if st_nc is not None:
                    risk_info["st_disagree_table_only_vs_namechange"] = int((listed & st_flag & ~st_nc).sum())
                    risk_info["st_disagree_namechange_only_vs_table"] = int((listed & ~st_flag & st_nc).sum())
                risk_info["st_disagree_table_vs_panel"] = int((listed & (st_flag != st_panel)).sum())
            elif st_nc is not None:
                st_flag = st_panel | st_nc
                risk_info["st_source"] = "fallback_panel_or_namechange"
                notes.append("st_daily_table_missing_fallback_namechange")
            else:
                risk_info["st_source"] = "panel_only"
                notes.append("st_daily_and_namechange_missing_panel_only")
            risk_info["st_panel_flagged_on_listed"] = int((listed & st_panel).sum())
        st_ok = ~st_flag if U.get("exclude_st", True) else (listed | True)
        # --- low price (raw close on session) ---
        lp_cfg = RX.get("low_price") or {}
        if lp_cfg.get("enabled", False):
            lowpx_ok = ~(Dp.close.loc[day] < float(lp_cfg.get("price_floor_cny", 2.0)))
        else:
            lowpx_ok = listed | True
        # --- non-standard audit opinion: latest annual report available before session ---
        au_cfg = RX.get("non_standard_audit_opinion") or {}
        audit_ok = listed | True
        risk_info["audit_rule_enabled"] = bool(au_cfg.get("enabled", False))
        au = _load_audit_annual(au_cfg.get("table", "data/v2/audit/audit_opinion_pit_tushare.parquet")) if au_cfg.get("enabled") else None
        risk_info["audit_data_ready"] = au is not None
        if au_cfg.get("enabled") and au is None:
            notes.append("audit_table_missing:not_applied")
        if au is not None:
            max_age = int(au_cfg.get("max_fiscal_years_back", 2))
            v = au[(au["avail_date"] < day) & (au["end_date"].dt.year >= day.year - max_age)]
            latest = v.groupby("instrument_id").tail(1).set_index("instrument_id")
            ns = set(latest.index[latest["is_non_standard"].astype(bool)])
            have = set(latest.index)
            idx_s = audit_ok.index.to_series()
            audit_ok = ~pd.Series(idx_s.isin(ns).to_numpy(), index=audit_ok.index)
            miss = listed & ~pd.Series(idx_s.isin(have).to_numpy(), index=audit_ok.index)
            risk_info["audit_non_standard_on_listed"] = int((listed & ~audit_ok).sum())
            risk_info["audit_missing_on_listed_not_excluded"] = int(miss.sum())
            risk_info["_audit_missing_ids"] = miss
        trad_ok = Dp.trad.loc[day] == 1 if U.get("require_trading", True) else True
        # --- B1 survivorship-corrected float-cap ranking (full market, then filter) ---
        from quantlab.beta.survivorship import later_delisted_in_band, merge_cap_for_ranking
        b1 = cfg.get("survivorship_b1") or {}
        b1_on = bool(b1.get("enabled", True))
        mode = ranking_mode_override or ("b1_full_market_then_filter" if b1_on else "legacy_filter_then_rank")
        if b1_on:
            cap_full, cap_diag = merge_cap_for_ranking(Dp.circ_mv, day, cap_window=int(cfg["universe"].get("cap_window", 20)))
            if cap_full is None:
                cap_s = Dp.cap.loc[day]
                cap_ok = cap_s.notna()
                notes.append("survivorship_merge_unavailable_fallback_panel_cap")
                b1_on = False
            else:
                # align to panel index; keep extra delisted-only ids for ranking
                cap_s = cap_full
                cap_ok = cap_s.notna()
                risk_info.update({f"b1_{k}": v for k, v in cap_diag.items()})
        else:
            cap_s = Dp.cap.loc[day]
            cap_ok = cap_s.notna()
            notes.append("survivorship_b1_disabled:ranking_may_be_survivor_biased")
        # Rank the FULL market with known float cap (no ST/low-price/audit yet).
        rank_universe = cap_s.dropna().sort_values(ascending=False)
        filters_hit = {
            "listed_on_session": n_listed,
            "b1_survivorship_ranking": b1_on,
            "rank_universe_size": int(len(rank_universe)),
            "drop_history_lt_min": int((listed & ~hist_ok).sum()),
            "drop_st": int((listed & hist_ok & ~st_ok).sum()),
            "drop_low_price": int((listed & hist_ok & st_ok & ~lowpx_ok).sum()),
            "drop_audit_opinion": int((listed & hist_ok & st_ok & lowpx_ok & ~audit_ok).sum()),
            "drop_not_trading": int((listed & hist_ok & st_ok & lowpx_ok & audit_ok & ~trad_ok).sum()),
            "drop_float_cap_missing": int((listed & hist_ok & st_ok & lowpx_ok & audit_ok & trad_ok & ~cap_s.reindex(listed.index).notna()).sum()) if hasattr(listed, 'index') else 0,
        }
        if mode == "legacy_filter_then_rank":
            # Pre-B1: apply risk filters first, then take ranks 3001-5000 of the filtered set.
            base = listed & hist_ok & st_ok & lowpx_ok & audit_ok & (trad_ok if isinstance(trad_ok, pd.Series) else True) & Dp.cap.loc[day].notna()
            elig = Dp.cap.loc[day][base].sort_values(ascending=False)
            band_used = U["band"]
            if band_used == "absolute" and len(elig) >= int(U["rank_start"]):
                band_ids = list(elig.index[int(U["rank_start"]) - 1 : int(U["rank_end"])])
            else:
                band_used = "relative"
                band_ids = list(elig.index[math.ceil((1 - float(U["relative_bottom_frac"])) * len(elig)) :])
            filters_hit["ranking_mode"] = "legacy_filter_then_rank"
            filters_hit["band_size"] = len(band_ids)
            band = elig.reindex(band_ids).dropna()
            adv_s = Dp.adv.loc[day]
            floor = float(rc["adv_floor_cny"])
            band_adv = adv_s.reindex(band.index)
            adv_ok = band_adv >= floor
            pool = list(band.index[adv_ok.fillna(False).to_numpy()])
            filters_hit["band_after_risk_filters"] = len(band)
            filters_hit["drop_adv_floor"] = int((~adv_ok.fillna(False)).sum())
            filters_hit["drop_adv_missing"] = int(band_adv.isna().sum())
            filters_hit["later_delisted_in_band"] = later_delisted_in_band(band_ids, day)["count"]
            # jump to fundamentals via pool already set — skip B1 band block
            pe = Dp.pe_ttm.loc[day].reindex(pool)
            pb = Dp.pb.loc[day].reindex(pool)
            fund_ok = (pe > float(Fd["pe_ttm_gt"])) & (pb > float(Fd["pb_gt"])) & (pb <= float(Fd["pb_le"]))
            fund_ok = fund_ok.fillna(False)
            filters_hit["fund_pass"] = int(fund_ok.sum())
            filters_hit["fund_fail_or_missing"] = int((~fund_ok).sum())
            filters_hit["pe_ttm_missing"] = int(pe.isna().sum())
            filters_hit["pb_missing"] = int(pb.isna().sum())
            target = int(S["target_names"])
            passing = [c for c in pool if bool(fund_ok.get(c, False))]
            failing = [c for c in pool if not bool(fund_ok.get(c, False))]
            order = sorted(passing, key=lambda c: _priority(seed, c))
            fallback_used = 0
            if Fd.get("mode") == "filter_with_tier_fallback" and len(order) < target:
                extra = sorted(failing, key=lambda c: _priority(seed, c))
                fallback_used = min(len(extra), target - len(order))
                order = order + extra
            ind = self._industry_on(Dp, day, order)
            retain_n = int(S["retain_top"] if retain_top_override is None else retain_top_override)
            retain = set(order[:retain_n])
            keep = [c for c in (current or []) if c in retain]
            max_ind = int(S["max_names_per_industry"]); max_unknown = int(S["unknown_industry_max_names"])
            chosen, counts, industry_cap_skips = [], {}, 0
            for c in keep + [c for c in order if c not in keep]:
                g = ind.get(c, "unknown"); lim = max_unknown if g == "unknown" else max_ind
                if counts.get(g, 0) >= lim:
                    industry_cap_skips += 1; continue
                chosen.append(c); counts[g] = counts.get(g, 0) + 1
                if len(chosen) == target: break
            filters_hit["industry_cap_skips"] = industry_cap_skips
            filters_hit["retained_from_current"] = len(keep)
            sel_adv = adv_s.reindex(chosen).dropna()
            adv_stats = {"adv_floor_cny": floor, "min": float(sel_adv.min()) if len(sel_adv) else None,
                         "p10": float(sel_adv.quantile(0.10)) if len(sel_adv) else None,
                         "median": float(sel_adv.median()) if len(sel_adv) else None,
                         "p90": float(sel_adv.quantile(0.90)) if len(sel_adv) else None}
            funnel = {"listed": n_listed, "eligible_pre_band": int(len(elig)), "band": len(band_ids),
                      "band_after_risk_filters": len(band), "after_adv_floor": len(pool),
                      "fund_pass": len(passing), "selected": len(chosen)}
            mix = dict(sorted(counts.items(), key=lambda kv: -kv[1]))
            notes.append("ranking_mode=legacy_filter_then_rank")
            notes.extend(["sw_l1_research_tushare_promotable=false", "promotion_approved=false"])
            return SmallcapBasket(session=session, data_session=day.date(), names=tuple(chosen),
                industries={c: ind.get(c, "unknown") for c in chosen}, band_used=band_used,
                funnel=funnel, filters_hit=filters_hit, industry_mix=mix, adv_stats=adv_stats,
                fundamentals_fallback_used=int(fallback_used), data_ready=len(chosen) > 0,
                notes=tuple(notes), ranked_pool=tuple(order), ranked_industries=dict(ind),
                retained_order=tuple(keep))

        band_used = U["band"]
        if band_used == "absolute" and len(rank_universe) >= int(U["rank_start"]):
            band_ids = list(rank_universe.index[int(U["rank_start"]) - 1 : int(U["rank_end"])])
        else:
            if band_used == "absolute":
                notes.append(f"absolute_band_short:ranked={len(rank_universe)}<{U['rank_start']}")
                if not U.get("fallback_to_relative_if_short", True):
                    band_ids = []
                else:
                    band_used = "relative"
            if band_used == "relative":
                band_ids = list(rank_universe.index[math.ceil((1 - float(U["relative_bottom_frac"])) * len(rank_universe)) :])
        pre_band = band_ids
        ld_band = later_delisted_in_band(band_ids, day)
        filters_hit["later_delisted_in_band"] = ld_band["count"]
        filters_hit["st_in_reference_band"] = int(sum(1 for c in pre_band if c in st_ok.index and not bool(st_ok.get(c, True))))
        filters_hit["low_price_in_reference_band"] = int(sum(1 for c in pre_band if c in lowpx_ok.index and not bool(lowpx_ok.get(c, True))))
        filters_hit["audit_non_standard_in_reference_band"] = int(sum(1 for c in pre_band if c in audit_ok.index and not bool(audit_ok.get(c, True))))
        _miss = risk_info.pop("_audit_missing_ids", None)
        if _miss is not None:
            filters_hit["audit_missing_in_reference_band"] = int(sum(1 for c in pre_band if c in _miss.index and bool(_miss.get(c, False))))
        risk_info["later_delisted_in_band_names"] = ld_band["names"][:20]  # cap list size
        filters_hit.update(risk_info)
        # Post-ranking risk filters inside the band (B1: ST/low-price/audit AFTER rank)
        def _ok(series, code, default=False):
            if code not in series.index:
                return default
            v = series.get(code)
            return bool(v) if v == v else default
        band_pass = []
        for c in band_ids:
            if c not in Dp.close.columns:
                continue  # delisted-only name with no panel bars: countable in band, not selectable without OHLC
            if not _ok(listed, c):
                continue
            if not _ok(hist_ok, c):
                continue
            if not _ok(st_ok, c, True):
                continue
            if not _ok(lowpx_ok, c, True):
                continue
            if not _ok(audit_ok, c, True):
                continue
            if isinstance(trad_ok, pd.Series):
                if not _ok(trad_ok, c, True):
                    continue
            elif trad_ok is not True:
                continue
            band_pass.append(c)
        band = rank_universe.reindex(band_pass).dropna()
        adv_s = Dp.adv.loc[day]
        floor = float(rc["adv_floor_cny"])
        band_adv = adv_s.reindex(band.index)
        adv_ok = band_adv >= floor
        pool = list(band.index[adv_ok.fillna(False).to_numpy()])
        filters_hit["band_size"] = int(len(band_ids))
        filters_hit["band_after_risk_filters"] = int(len(band))
        filters_hit["drop_adv_floor"] = int((~adv_ok.fillna(False)).sum())
        filters_hit["drop_adv_missing"] = int(band_adv.isna().sum())
        filters_hit["delisted_only_in_band_not_selectable"] = int(sum(1 for c in band_ids if c not in Dp.close.columns))

        pe = Dp.pe_ttm.loc[day].reindex(pool)
        pb = Dp.pb.loc[day].reindex(pool)
        fund_ok = (pe > float(Fd["pe_ttm_gt"])) & (pb > float(Fd["pb_gt"])) & (pb <= float(Fd["pb_le"]))
        fund_ok = fund_ok.fillna(False)
        filters_hit["fund_pass"] = int(fund_ok.sum())
        filters_hit["fund_fail_or_missing"] = int((~fund_ok).sum())
        filters_hit["pe_ttm_missing"] = int(pe.isna().sum())
        filters_hit["pb_missing"] = int(pb.isna().sum())

        target = int(S["target_names"])
        passing = [c for c in pool if bool(fund_ok.get(c, False))]
        failing = [c for c in pool if not bool(fund_ok.get(c, False))]
        order = sorted(passing, key=lambda c: _priority(seed, c))
        fallback_used = 0
        if Fd.get("mode") == "filter_with_tier_fallback" and len(order) < target:
            extra = sorted(failing, key=lambda c: _priority(seed, c))
            fallback_used = min(len(extra), target - len(order))
            order = order + extra
            notes.append(f"fundamental_tier_fallback_names={fallback_used}")

        ind = self._industry_on(Dp, day, order)
        retain = set(order[: int(S["retain_top"] if retain_top_override is None else retain_top_override)])
        keep = [c for c in (current or []) if c in retain]
        max_ind = int(S["max_names_per_industry"])
        max_unknown = int(S["unknown_industry_max_names"])
        chosen: list[str] = []
        counts: dict[str, int] = {}
        industry_cap_skips = 0
        for c in keep + [c for c in order if c not in keep]:
            g = ind.get(c, "unknown")
            lim = max_unknown if g == "unknown" else max_ind
            if counts.get(g, 0) >= lim:
                industry_cap_skips += 1
                continue
            chosen.append(c)
            counts[g] = counts.get(g, 0) + 1
            if len(chosen) == target:
                break
        filters_hit["industry_cap_skips"] = industry_cap_skips
        filters_hit["retained_from_current"] = len(keep)
        if fallback_used:
            fallback_in = sum(1 for c in chosen if c in set(failing))
            fallback_used = fallback_in

        sel_adv = adv_s.reindex(chosen).dropna()
        adv_stats = {
            "adv_floor_cny": floor,
            "min": float(sel_adv.min()) if len(sel_adv) else None,
            "p10": float(sel_adv.quantile(0.10)) if len(sel_adv) else None,
            "median": float(sel_adv.median()) if len(sel_adv) else None,
            "p90": float(sel_adv.quantile(0.90)) if len(sel_adv) else None,
        }
        funnel = {
            "listed": n_listed,
            "eligible_pre_band": int(len(rank_universe)),
            "band": int(len(band_ids)),
            "band_after_risk_filters": int(len(band)),
            "after_adv_floor": int(len(pool)),
            "fund_pass": int(len(passing)),
            "selected": int(len(chosen)),
        }
        mix = dict(sorted(counts.items(), key=lambda kv: -kv[1]))
        unknown_n = counts.get("unknown", 0)
        if unknown_n:
            notes.append(f"sw_l1_unknown_names={unknown_n}")
        notes.extend(["sw_l1_research_tushare_promotable=false", "promotion_approved=false"])
        return SmallcapBasket(
            session=session,
            data_session=day.date(),
            names=tuple(chosen),
            industries={c: ind.get(c, "unknown") for c in chosen},
            band_used=band_used,
            funnel=funnel,
            filters_hit=filters_hit,
            industry_mix=mix,
            adv_stats=adv_stats,
            fundamentals_fallback_used=int(fallback_used),
            data_ready=len(chosen) > 0,
            notes=tuple(notes),
            ranked_pool=tuple(order),
            ranked_industries=dict(ind),
            retained_order=tuple(keep),
        )

    # -- weights --
    def tier_weights(self, basket: SmallcapBasket, tier: str) -> SmallcapTierWeights:
        cfg = self.config()
        rc = cfg["risk_controls"]
        tiers = cfg["tiers"]
        if tier not in tiers:
            raise KeyError(f"smallcap_tier_unknown:{tier}")
        w_target = float(tiers[tier])
        n = len(basket.names)
        cap_book = min(
            float(rc["max_name_weight_of_book"]),
            float(rc["max_name_frac_of_sleeve"]) * w_target,
            float(self.mandate.portfolio_limits.max_single_stock_weight),
        )
        if n == 0:
            return SmallcapTierWeights(
                tier=tier, sleeve_weight_target=w_target, sleeve_weight_effective=0.0, per_name_weight=0.0,
                name_weights={}, single_name_cap_book=cap_book, single_name_cap_binding=False,
                per_name_notional_cny=0.0, min_trade_feasible=False, lot_infeasible_names=0, adv_capacity_breaches=0,
            )
        ew = w_target / n
        per = min(ew, cap_book)
        binding = ew > cap_book + 1e-15
        eff = round(per * n, 6)
        capital = float(rc.get("research_notional_cny") or rc["book_capital_cny"])
        notional = per * capital
        Dp = self._panels_for(basket.session)
        day = self._data_day(Dp, basket.data_session or basket.session)
        lot = int(rc["lot_size"])
        lot_bad = 0
        adv_bad = 0
        if day is not None:
            px = Dp.close.loc[day].reindex(list(basket.names))
            adv = Dp.adv.loc[day].reindex(list(basket.names))
            buf = float(rc.get("capacity_buffer", 1.0))
            lot_bad = int((px * lot * buf > notional).fillna(True).sum())
            adv_bad = int((notional > float(rc["max_order_vs_adv"]) * adv).fillna(True).sum())
        return SmallcapTierWeights(
            tier=tier,
            sleeve_weight_target=w_target,
            sleeve_weight_effective=eff,
            per_name_weight=round(per, 8),
            name_weights={c: round(per, 8) for c in basket.names},
            single_name_cap_book=round(cap_book, 8),
            single_name_cap_binding=bool(binding),
            per_name_notional_cny=round(notional, 2),
            min_trade_feasible=notional >= float(rc["min_trade_notional_cny"]) * float(rc.get("capacity_buffer", 1.0)),
            lot_infeasible_names=lot_bad,
            adv_capacity_breaches=adv_bad,
        )

    # -- capacity: minimum notional so all names clear 1 lot + min trade --
    def required_capital(self, basket: SmallcapBasket) -> Mapping[str, object]:
        """Per tier: min book capital C with (w*C/N) >= buffer*max(min_trade, lot*max_price)."""
        import math

        cfg = self.config()
        rc = cfg["risk_controls"]
        buf = float(rc.get("capacity_buffer", 1.0))
        lot = int(rc["lot_size"])
        min_trade = max(float(rc["min_trade_notional_cny"]), float(self.mandate.portfolio_limits.min_trade_notional_cny))
        Dp = self._panels_for(basket.session)
        day = self._data_day(Dp, basket.data_session or basket.session)
        names = list(basket.names)
        n = len(names)
        if day is None or n == 0:
            return {"available": False}
        px = Dp.close.loc[day].reindex(names)
        n_px_missing = int(px.isna().sum())
        max_px = float(px.max())
        binding = max(min_trade, lot * max_px)
        per_name_need = buf * binding
        out = {
            "available": True,
            "n_names": n,
            "max_price": max_px,
            "max_price_name": str(px.idxmax()),
            "median_price": float(px.median()),
            "lot_size": lot,
            "min_trade_cny": min_trade,
            "capacity_buffer": buf,
            "per_name_need_cny": round(per_name_need, 2),
            "binding_constraint": "lot_of_most_expensive_name" if lot * max_px >= min_trade else "min_trade",
            "price_missing": n_px_missing,
            "by_tier": {},
        }
        for tier, w in cfg["tiers"].items():
            c = per_name_need * n / float(w)
            out["by_tier"][tier] = {"sleeve_weight": float(w), "required_capital_cny": round(c, 0)}
        return out

    # -- live 600k account profile (Leo 22:34 ET): 20-30 names, per-name min weight --
    def live_basket(self, basket: SmallcapBasket, tier: str, *, current: Sequence[str] | None = None,
                    retain_mult: float | None = None) -> Mapping[str, object]:
        import dataclasses
        import math

        cfg = self.config()
        L = cfg["live_profile"]
        w = float(cfg["tiers"][tier])
        cap = float(L["account_capital_cny"])
        n = int(min(L["n_max"], max(L["n_min"], math.floor(w / float(L["min_name_weight_of_book"]) + 1e-9))))
        per = w * cap / n
        lot, buf = int(L["lot_size"]), float(L["lot_buffer"])
        min_trade = max(2000.0, float(self.mandate.portfolio_limits.min_trade_notional_cny))
        max_ind = max(3, math.ceil(int(cfg["selection"]["max_names_per_industry"]) * n / 50))
        Dp = self._panels_for(basket.session)
        day = self._data_day(Dp, basket.data_session or basket.session)
        px = Dp.close.loc[day]
        chosen, counts, lot_swaps, ind_skips = [], {}, 0, 0
        if retain_mult is None:
            retain_mult = float(L.get("retain_mult", 0.0)) if current is not None else 0.0
        pool = list(basket.ranked_pool)
        keep: list[str] = []
        if current and retain_mult > 0:
            zone = set(pool[: int(math.ceil(retain_mult * n))])
            keep = [c for c in current if c in zone]
        walk = keep + [c for c in pool if c not in set(keep)]
        for c in walk:
            p_ = px.get(c)
            if p_ is None or p_ != p_:
                continue
            if lot * float(p_) * buf > per or math.floor(per / (lot * float(p_))) * lot * float(p_) < min_trade:
                lot_swaps += 1  # 1 lot unaffordable, or whole-lot holding would fall below min trade
                continue
            g = basket.ranked_industries.get(c, "unknown")
            if counts.get(g, 0) >= max_ind:
                ind_skips += 1
                continue
            chosen.append(c)
            counts[g] = counts.get(g, 0) + 1
            if len(chosen) == n:
                break
        cp = px.reindex(chosen)
        lots = [math.floor(per / (lot * float(v))) for v in cp]
        held = [k * lot * float(v) for k, v in zip(lots, cp)]
        lb = dataclasses.replace(basket, names=tuple(chosen), industries={c: basket.ranked_industries.get(c, "unknown") for c in chosen},
                                 industry_mix=dict(sorted(counts.items(), key=lambda kv: -kv[1])))
        return {
            "tier": tier, "sleeve_weight": w, "account_capital_cny": cap, "n": len(chosen), "n_target": n,
            "per_name_weight_of_book": w / n, "per_name_target_cny": round(per, 2),
            "held_cny_after_lot_rounding_min": round(min(held), 2) if held else None,
            "held_cny_after_lot_rounding_median": round(sorted(held)[len(held) // 2], 2) if held else None,
            "lot_unaffordable": sum(1 for k in lots if k < 1),
            "below_min_trade": sum(1 for h in held if h < min_trade),
            "lot_swaps": lot_swaps, "industry_cap": max_ind, "industry_cap_skips": ind_skips,
            "min_commission_bp_at_target": round(5.0 / per * 1e4, 1),
            "n_industries": len(counts), "max_names_one_industry": max(counts.values()) if counts else 0,
            "overlap_with_research_basket": len(set(chosen) & set(basket.names)),
            "retain_mult": retain_mult, "retained_from_current": len([c for c in chosen if c in set(keep)]),
            "max_price": float(cp.max()) if len(cp) else None,
            "names": chosen, "_basket": lb, "promotion_approved": False,
        }

    # -- risk: crowding (descriptive flags) --
    def crowding(self, basket: SmallcapBasket) -> Mapping[str, object]:
        import numpy as np

        cfg = self.config()["risk_controls"]["crowding"]
        Dp = self._panels_for(basket.session)
        day = self._data_day(Dp, basket.data_session or basket.session)
        names = list(basket.names)
        if day is None or not names:
            return {"available": False}
        tr = Dp.turnover_rate[names]
        pos = Dp.turnover_rate.index.get_loc(day)
        lb = int(cfg["turnover_lookback_sessions"])
        rec = int(cfg["turnover_recent_sessions"])
        med = tr.iloc[max(0, pos - lb + 1) : pos + 1].median(axis=1)
        recent = float(med.iloc[-rec:].mean()) if len(med) >= rec else None
        roll = med.rolling(rec, min_periods=rec).mean().dropna()
        pct = float((roll <= recent).mean()) if recent is not None and len(roll) else None
        win = int(cfg["hot_ret_window"])
        c = Dp.close[names]
        if pos >= win:
            r20 = c.iloc[pos] / c.iloc[pos - win] - 1.0
            hot_frac = float((r20 > float(cfg["hot_ret_threshold"])).mean())
        else:
            hot_frac = None
        crowded_turn = pct is not None and pct >= float(cfg["crowded_turnover_pct"])
        hot_alert = hot_frac is not None and hot_frac >= float(cfg["hot_name_frac_alert"])
        return {
            "available": True,
            "basket_median_turnover_recent": recent,
            "turnover_percentile_vs_lookback": pct,
            "crowded_turnover_flag": bool(crowded_turn),
            "hot_name_frac_20d_gt_threshold": hot_frac,
            "hot_names_alert": bool(hot_alert),
            "crowding_flag": bool(crowded_turn or hot_alert),
            "method": "basket names' median turnover_rate, recent 20d mean vs trailing 250d; frac names with 20d price ret > 25%",
            "label": "descriptive_flag_not_a_signal",
        }

    # -- descriptive β vs 510300 (pre-engine-fix descriptive) --
    def beta_descriptive(self, basket: SmallcapBasket, lookback: int = 120) -> Mapping[str, object]:
        import numpy as np

        Dp = self._panels_for(basket.session)
        day = self._data_day(Dp, basket.data_session or basket.session)
        names = list(basket.names)
        if day is None or not names or Dp.etf_ret is None:
            return {"available": False}
        r = Dp.ret[names].loc[:day].iloc[-lookback:]
        ew = r.mean(axis=1)
        e = Dp.etf_ret.reindex(ew.index)
        ok = ew.notna() & e.notna()
        if ok.sum() < 40:
            return {"available": False, "obs": int(ok.sum())}
        x, y = e[ok].to_numpy(float), ew[ok].to_numpy(float)
        beta = float(np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1))
        return {
            "available": True,
            "basket_unit_beta_vs_510300": beta,
            "obs": int(ok.sum()),
            "window_sessions": lookback,
            "method": "OLS of EW basket daily return (membership fixed at session) on 510300 return, trailing window",
            "label": "pre_engine_fix_descriptive (lookback uses current membership — look-ahead in membership, not for performance)",
        }

    # -- stress harness --
    def stress_test(self, test_id: str = "smallcap_crash_2024_02") -> Mapping[str, object]:
        import numpy as np
        import pandas as pd

        cfg = self.config()
        spec = next((s for s in cfg["stress_tests"] if s["id"] == test_id), None)
        if spec is None:
            raise KeyError(f"stress_test_unknown:{test_id}")
        Dp = self._panels()
        form = pd.Timestamp(spec["formation_on_or_before"]).date()
        day0 = self._data_day(Dp, form)
        avail = int((Dp.close.index <= day0).sum()) if day0 is not None else 0
        cfg_hist = int(cfg["universe"]["min_history_sessions"])
        override = None
        if avail <= cfg_hist:
            # Panels start 2023-01-03: listing age is truncated, not real. Adapt + flag.
            override = max(120, avail - 20)
        b = self.basket(form, min_history_override=override)
        names = list(b.names)
        lo, hi = pd.Timestamp(spec["window_start"]), pd.Timestamp(spec["window_end"])
        r = Dp.ret[names].loc[lo:hi] if names else None
        out: dict = {
            "id": test_id,
            "harness_status": "ready" if names else "no_basket",
            "label": spec["label"],
            "note": spec["note"],
            "formation_session": str(b.data_session),
            "window": [spec["window_start"], spec["window_end"]],
            "basket_count": len(names),
            "band_used": b.band_used,
            "panel_sessions_available_at_formation": avail,
            "min_history_used": override if override is not None else cfg_hist,
            "history_truncated_by_panel_start": override is not None,
            "basket_funnel": dict(b.funnel),
            "required_capital": self.required_capital(b),
            "engine_dependency": cfg["engine_dependency"],
            "promotion_approved": False,
        }
        if not names or r is None or r.empty:
            return out
        nan_cells = int(r.isna().sum().sum())
        # EW buy-and-hold with drift: track per-name value
        val = (1.0 + r.fillna(0.0)).cumprod()
        path = val.mean(axis=1)
        dd = path / path.cummax() - 1.0
        trough_day = dd.idxmin()
        e = Dp.etf_ret.reindex(r.index).fillna(0.0) if Dp.etf_ret is not None else None
        etf_path = (1.0 + e).cumprod() if e is not None else None
        ld = Dp.ld[names].loc[lo:hi]
        halt = Dp.trad[names].loc[lo:hi] != 1
        basket_dd = float(dd.min())
        tiers = cfg["tiers"]
        out.update(
            {
                "sessions": int(len(r)),
                "ret_nan_cells": nan_cells,
                "basket_ew_max_drawdown_descriptive": basket_dd,
                "basket_trough_session": str(trough_day.date()),
                "basket_window_end_return_descriptive": float(path.iloc[-1] - 1.0),
                "etf_510300_window_max_drawdown_descriptive": float((etf_path / etf_path.cummax() - 1).min()) if etf_path is not None else None,
                "limit_down_name_days": int((ld == 1).sum().sum()),
                "halt_name_days": int(halt.sum().sum()),
                "max_names_limit_down_same_day": int((ld == 1).sum(axis=1).max()),
                "book_impact_by_tier_descriptive": {t: float(w) * basket_dd for t, w in tiers.items()},
                "caveat": "raw adjusted returns; limit-down days not modelled as unsellable exits; no costs; pre-engine-fix — NOT a performance claim",
            }
        )
        return out

    # -- plan --
    def plan(
        self,
        session: date,
        *,
        current: Sequence[str] | None = None,
        core_plan: object | None = None,
    ) -> SmallcapSleevePlan:
        self.mandate.require_not_promoted()
        b = self.basket(session, current=current)
        cfg = self.config()
        tiers = {t: self.tier_weights(b, t) for t in cfg["tiers"]}
        crowd = self.crowding(b)
        beta = self.beta_descriptive(b)
        inter = None
        if core_plan is not None:
            rc = getattr(core_plan, "residual_book_weight_cap", None)
            core_beta = getattr(core_plan, "implied_sleeve_beta", None)
            target = float(self.mandate.risk.target_beta_vs_benchmark)
            sb = beta.get("basket_unit_beta_vs_510300") if beta.get("available") else 1.0
            inter = {}
            for t, tw in tiers.items():
                w = tw.sleeve_weight_effective
                port_beta = (core_beta or 0.0) + w * float(sb)
                gap = target - port_beta
                inter[t] = {
                    "core_etf_weight": getattr(core_plan, "etf_sleeve_weight", None),
                    "core_cash_weight": getattr(core_plan, "cash_weight", None),
                    "smallcap_weight": w,
                    "residual_book_weight_cap_after": None if rc is None else round(max(0.0, float(rc) - w), 6),
                    "core_plus_smallcap_beta": round(port_beta, 6),
                    "remaining_beta_gap_to_target": round(gap, 6),
                    "residual_weight_to_hit_target_beta_after": None if rc is None else round(min(max(0.0, gap), max(0.0, float(rc) - w)), 6),
                    "smallcap_unit_beta_used": sb,
                }
        todos = (
            "promotion_approved=false",
            "bound_by_max_etf=false",
            "mandate_json_unchanged",
            "mandate_microcap_policy_conflict:exclude_bottom_30pct_and_microcap_as_universe_banned",
            "performance_blocked_until_engine_limit_fix",
            "sw_l1_research_only",
        )
        return SmallcapSleevePlan(
            session=session,
            basket=b,
            tiers=tiers,
            crowding=crowd,
            beta_descriptive=beta,
            interaction_with_core=inter,
            capacity=self.required_capital(b),
            todos=todos,
        )

    def describe_contract(self) -> Mapping[str, object]:
        cfg = self.config()
        mp = self.mandate.universe.microcap_policy
        return {
            "provider": "SmallcapBetaSleeveProvider",
            "layer": "L1b_standalone_smallcap_beta_sleeve",
            "parallel_to": "sh.510300 core sleeve (VolTargetBetaSleeveProvider)",
            "config_path": cfg["config_path"],
            "tiers": cfg["tiers"],
            "bound_by_max_etf": False,
            "promotion_approved": False,
            "mandate_conflicts": {
                "microcap_policy_mode": mp.mode,
                "exclude_bottom_mktcap_pct": mp.exclude_bottom_mktcap_pct,
                "microcap_as_universe_banned": mp.microcap_as_universe_banned,
                "note": "Sleeve drops the bottom-30% exclusion per Leo; Mandate JSON untouched; any promotion would need a Mandate decision",
            },
            "api": {
                "basket": "basket(session, current=None) -> SmallcapBasket",
                "data_source": "SmallcapBetaSleeveProvider(mandate, data_source='auto'|'history_2015'|'panels_2023', basket_cache=None)",
                "precompute": "precompute_history_baskets(sessions, path) -> JSON cache for basket_cache",
                "tier_weights": "tier_weights(basket, 'T10'|'T15'|'T20') -> SmallcapTierWeights",
                "plan": "plan(session, current=None, core_plan=VolTargetBetaSleeveProvider.plan(session)) -> SmallcapSleevePlan",
                "crowding": "crowding(basket)",
                "stress_test": "stress_test('smallcap_crash_2024_02')",
            },
            "engine_dependency": cfg["engine_dependency"],
        }
