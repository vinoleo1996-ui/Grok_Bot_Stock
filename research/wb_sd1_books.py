#!/usr/bin/env python3
"""wb_SD1 side entry points for the three legacy weight books (spec docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md
sha256 2e428f39…bdbb0b; 主 Agent 01:33 ET ruling: legacy functions stay byte-identical = wb_SD0).

    book_ret_sd1(W, start, end, track=, delist_source=)          ~ research.g1g5_fund_resid_alpha.book_ret      (FE)
    lc_ret_sd1(W, net=True, track=, delist_source=)              ~ research.leaf_selfcheck_common._ret          (LC)
    gross_and_turnover_sd1(weights_path, track=, delist_source=) ~ research.alpha_decay_gate.gross_and_turnover (ADG)

``track`` (Arch P2-2; 'core' -> blocked budget kept as cash) and ``delist_source`` (Arch P2-4; src_events_v1 |
src_table_v2 | src_table_v1_d3rule, never auto-switched) are REQUIRED keyword arguments.
主 Agent E-2 (01:53 ET): FE and ADG outputs carry OPTIMISTIC_NO_LIMIT (no limit-up/down yet) and cannot serve as a
gate on their own; book_smoke takes precedence. Use ``*_full`` variants to get the result dict with flags/summary
(E-1 write-off categories + G2 combined weight).
r3 (Arch P2-R2): FE's resume-day entry gate defaults to resume_gate='require_announced' (resume_announced from
cs_panel_v2, else Data's suspend_flags_v2 at the pinned ``resume_flags_sha256``; neither -> refuse). 'off' is the
gate-off sensitivity (book_ret_sd1_gate_sensitivity); 'is_resume_day_fallback' is disclosure only.

Same return shapes as the legacy functions. They reuse the legacy modules' constants and price loaders read-only and
route the book through quantlab.platform.tradability.weight_book_returns. FE needs cs_panel_v2 (D-1; Data P0 per
ruling 4) and refuses cs_panel v1 unless allow_cs_panel_v1=True. Ex-post delisting info is read only inside the
platform accounting layer, never here. Running on real data needs an Arch .ok. live=false; promotion_approved=false.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def book_ret_sd1_full(W, start, end, *, track: str, delist_source: str, allow_cs_panel_v1: bool = False,
                      resume_gate: str = "require_announced", resume_flags_sha256: str | None = None):
    import research.g1g5_fund_resid_alpha as FE
    import quantlab.platform.tradability as TB
    e = pd.read_parquet(FE.R / "data/v2/etf/etf_daily_adj.parquet", columns=["trade_date", "open_hfq", "close_hfq"],
                        filters=[("ts_code", "==", FE.BAL)])
    e.index = pd.to_datetime(e.trade_date, format="%Y%m%d"); e = e.sort_index()
    r, to, res = TB.fe_book_ret_sd1(W, start, end, cost=FE.COST, bal=FE.BAL, bal_open=e.open_hfq, bal_close=e.close_hfq,
                                    panel_dir=FE.PC, allow_cs_panel_v1=allow_cs_panel_v1, track=track, delist_source=delist_source,
                                    resume_gate=resume_gate, resume_flags_sha256=resume_flags_sha256)
    return r, to, res


def book_ret_sd1_gate_sensitivity(W, start, end, *, track: str, delist_source: str, resume_flags_sha256: str | None = None,
                                  allow_cs_panel_v1: bool = False):
    """Arch P2-R2: main (require_announced) vs resume gate off; per-year blocked entries in each result's
    summary['resume_gate']. Disclosure only."""
    import research.g1g5_fund_resid_alpha as FE
    import quantlab.platform.tradability as TB
    e = pd.read_parquet(FE.R / "data/v2/etf/etf_daily_adj.parquet", columns=["trade_date", "open_hfq", "close_hfq"],
                        filters=[("ts_code", "==", FE.BAL)])
    e.index = pd.to_datetime(e.trade_date, format="%Y%m%d"); e = e.sort_index()
    return TB.fe_resume_gate_sensitivity(W, start, end, cost=FE.COST, bal=FE.BAL, bal_open=e.open_hfq, bal_close=e.close_hfq,
                                         panel_dir=FE.PC, allow_cs_panel_v1=allow_cs_panel_v1, track=track,
                                         delist_source=delist_source, resume_flags_sha256=resume_flags_sha256)


def book_ret_sd1(W, start, end, *, track: str, delist_source: str, allow_cs_panel_v1: bool = False,
                 resume_gate: str = "require_announced", resume_flags_sha256: str | None = None):
    r, to, _ = book_ret_sd1_full(W, start, end, track=track, delist_source=delist_source, allow_cs_panel_v1=allow_cs_panel_v1,
                                 resume_gate=resume_gate, resume_flags_sha256=resume_flags_sha256)
    return r, to   # OPTIMISTIC_NO_LIMIT (E-2): see book_ret_sd1_full()[2]['flags']


def lc_ret_sd1(W: pd.DataFrame, net: bool = True, *, track: str, delist_source: str) -> pd.Series:
    import research.leaf_selfcheck_common as LC
    import quantlab.platform.tradability as TB
    from research.g1g5_x2_panel_stitch import load_panel_features_x2, clear_caches

    def _raw(i):
        f = load_panel_features_x2(i); clear_caches(); f.index = pd.to_datetime(f.index); return f
    r, _ = TB.lc_ret_sd1(W, LC._px, _raw, cost=LC.ADG.COST, net=net, track=track, delist_source=delist_source,
                         etf=LC.etf)
    return r


def gross_and_turnover_sd1(weights_path, *, track: str, delist_source: str):
    import research.alpha_decay_gate as ADG
    import quantlab.platform.tradability as TB
    d = pd.read_parquet(weights_path, columns=["date", "instrument", "target_weight"])
    d["date"] = pd.to_datetime(d["date"].astype(str).str[:10])
    P = d.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    g, to, _ = TB.adg_gross_and_turnover_sd1(P, ADG._close, no_limit={ADG.B}, track=track,
                                         delist_source=delist_source)
    return g, to   # OPTIMISTIC_NO_LIMIT (E-2)
