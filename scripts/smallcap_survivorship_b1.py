"""B1 survivorship fix report. Research-only; promotion_approved=false. No performance claims."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from quantlab.beta.smallcap_sleeve import SmallcapBetaSleeveProvider
from quantlab.beta.survivorship import (
    delist_sensitivity_table,
    later_delisted_in_band,
    load_delisted_master,
    merge_cap_for_ranking,
    rank_band,
)
from quantlab.mandate_v2 import load_mandate_v2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/v2_proto/smallcap_survivorship_b1.json"
SESSIONS = [date(2026, 6, 30), date(2026, 10, 9)]


def slim(f):
    return {k: v for k, v in f.items() if k not in ("later_delisted_in_band_names",) and not str(k).startswith("_")}


def main():
    m = load_mandate_v2()
    sc = SmallcapBetaSleeveProvider(m)
    cfg = sc.config()
    master = load_delisted_master()
    Dp = sc._panels()
    prev_json = json.loads((ROOT / "output/v2_proto/smallcap_beta_sleeve.json").read_text())

    by = {}
    for s in SESSIONS:
        b1 = sc.basket(s)  # default B1 on
        leg = sc.basket(s, ranking_mode_override="legacy_filter_then_rank")
        prev_names = set(prev_json["by_session"][str(s)]["names"])
        live = {}
        for t in cfg["tiers"]:
            lv = sc.live_basket(b1, t)
            live[t] = {k: lv[k] for k in ("n", "lot_unaffordable", "below_min_trade", "lot_swaps",
                                           "min_commission_bp_at_target", "n_industries",
                                           "max_names_one_industry", "overlap_with_research_basket",
                                           "held_cny_after_lot_rounding_min", "held_cny_after_lot_rounding_median") if k in lv}
        by[str(s)] = {
            "research50_b1": {
                "n": len(b1.names), "names": list(b1.names), "filters_hit": slim(b1.filters_hit),
                "later_delisted_in_band": b1.filters_hit.get("later_delisted_in_band"),
                "later_delisted_in_band_names": b1.filters_hit.get("later_delisted_in_band_names", []),
                "n_industries": len(b1.industry_mix),
                "max_per_industry": max(b1.industry_mix.values()) if b1.industry_mix else 0,
                "survivorship_label": "survivorship-corrected ranking (panel ∪ delisted daily; filters after band)",
            },
            "research50_legacy_filter_then_rank": {
                "n": len(leg.names), "names": list(leg.names),
                "later_delisted_in_band": leg.filters_hit.get("later_delisted_in_band"),
                "note": "pre-B1: ST/low-price/audit applied before taking ranks 3001-5000",
            },
            "prev_json_basket_n": len(prev_names),
            "overlap_b1_vs_legacy": len(set(b1.names) & set(leg.names)),
            "overlap_b1_vs_prev_json": len(set(b1.names) & prev_names),
            "live": live,
        }
        print(s, "b1", len(b1.names), "legacy", len(leg.names),
              "overlap_legacy", by[str(s)]["overlap_b1_vs_legacy"],
              "overlap_prev", by[str(s)]["overlap_b1_vs_prev_json"],
              "ld_band", b1.filters_hit.get("later_delisted_in_band"), flush=True)

    # Historical later-delisted in band (panel window only)
    hist = []
    for day in list(Dp.circ_mv.index[::21]) + [Dp.circ_mv.index[-1]]:
        cap, diag = merge_cap_for_ranking(Dp.circ_mv, day, int(cfg["universe"]["cap_window"]))
        band, _ = rank_band(cap, int(cfg["universe"]["rank_start"]), int(cfg["universe"]["rank_end"]))
        info = later_delisted_in_band(band, day, master)
        hist.append({"session": str(day.date()), "later_delisted_in_band": info["count"],
                     "band_size": len(band), "alive_later_delisted": diag.get("later_delisted_alive_on_session")})

    # Selected names that later delisted (panel window rebalances)
    every = 20
    idx = Dp.close.index
    s0 = int((idx >= "2023-12-29").argmax()) if (idx >= "2023-12-29").any() else 0
    selected, hit = set(), set()
    prev = None
    for t in range(s0, len(idx), every):
        ov = max(120, t + 1 - 20) if t + 1 <= int(cfg["universe"]["min_history_sessions"]) else None
        b = sc.basket(idx[t].date(), current=prev, min_history_override=ov)
        if b.names:
            selected |= set(b.names)
            prev = list(b.names)
    if master is not None:
        for c in selected:
            if c in master.index and master.loc[c, "delist_date"] <= idx[-1]:
                hit.add(c)

    stress = sc.basket(date(2023, 12, 29), min_history_override=222)
    out = {
        "ok": True,
        "phase": "beta_smallcap_survivorship_b1",
        "promotion_approved": False,
        "mandate_json_edited": False,
        "survivorship_clean_for_panel_window_2023_plus": True,
        "survivorship_clean_for_pre_2023": False,
        "label": "B1: as-of float circ_mv ranks over full market (panel ∪ delisted daily, alive that day); ST/low-price/audit AFTER band. Terminal −50%/−100% defined. Pre-2023 band ranks INCOMPLETE (no full-market panel before 2023-01-03).",
        "by_session": by,
        "stress_formation_2023_12_29": {
            "n": len(stress.names),
            "later_delisted_in_band": stress.filters_hit.get("later_delisted_in_band"),
            "later_delisted_in_band_names": stress.filters_hit.get("later_delisted_in_band_names", []),
            "survivorship_label": "survivorship-corrected within panel window",
        },
        "historical_later_delisted_in_band_panel_window": hist,
        "historical_summary": {
            "max_later_delisted_in_band": max(h["later_delisted_in_band"] for h in hist),
            "mean_later_delisted_in_band": round(sum(h["later_delisted_in_band"] for h in hist) / len(hist), 1),
            "on_2023_12_29": next(h for h in hist if h["session"] == "2023-12-29") if any(h["session"]=="2023-12-29" for h in hist) else None,
        },
        "selected_names_that_later_delisted_panel_window": {
            "n_unique_selected": len(selected),
            "n_later_delisted": len(hit),
            "names": sorted(hit),
            "terminal_sensitivity": delist_sensitivity_table(sorted(hit)),
            "note": "descriptive; not a performance claim. Apply −50% and −100% once at last close when a held name delists.",
        },
        "delist_terminal_scenarios": {
            "minus_50": "mark position at last_close * 0.5 (terminal return −50%)",
            "minus_100": "mark position at 0 (terminal return −100%)",
            "rule": "no invented post-delist prices; apply once on/after last_trade_date",
            "reason_field": "heuristic via namechange (Data: no official delist reason)",
        },
        "pre_panel_gap": {
            "panel_start": str(Dp.close.index[0].date()),
            "b3_2015_ready": False,
            "why": "research_attrib_v2 panels start 2023-01-03. Delisted daily from 2015 exists, but ranks 3001-5000 need a full-market as-of circ_mv panel for 2015-2016. Stop after B1; B3 deferred.",
        },
        "config_block": cfg.get("survivorship_b1"),
        "data_paths": {
            "master": "data/v2/delisted/delisted_master_tushare.parquet",
            "daily_from2015": "data/v2/delisted/delisted_daily_from2015_tushare.parquet",
            "st_daily": "data/v2/delisted/delisted_is_st_daily_from2015.parquet",
            "panels": cfg["data"]["panels_dir"],
        },
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    print("wrote", OUT)
    print("hist max/mean", out["historical_summary"])
    print("later-delisted selected", len(hit), sorted(hit)[:10])


if __name__ == "__main__":
    main()
