"""Generic paper track runner (research/paper only). Reuses b4_paper's logic through a track spec; B4 itself keeps
its default spec, code path and hashes. Usage: python -m quantlab.cli paper-track --track s6 --mode backfill|forward|monitor|all|rehash"""
import sys
from quantlab.portfolio import b4_paper as B

AF = "output/ai_factory/"
TRACKS = {
    "s6": dict(name="s6", out="output/strategy_paper_s6", frozen_doc="docs/v2/STRATEGY_S6_SHADOW_PREREG_ZH.md",
               weights={600000: "output/strategy_wf_combo/weights_S6_60w.parquet", 1000000: "output/strategy_wf_combo/weights_S6_100w.parquet"},
               legs={"capacity_adv": .5, "earnings_event": .25, "equity_incentive": .25},
               event_legs={"earnings_event": AF + "g1g5_earnings_event_daily_weights_20261014_005430.parquet",
                           "equity_incentive": AF + "g1g5_equity_incentive_daily_weights_20261014_023222.parquet"},
               sleeve="S6_shadow_capadv_earnevt_eqincent_50_25_25", status="SHADOW_PAPER_CANDIDATE_BACKFILL_READY_FORWARD_PENDING",
               fwd_label="S6 shadow paper forward (2026-11+)", bridge_key="s6",
               x2h_pending_reason="equity_incentive extension script from AI pending; no gated S6 weights past 2026-10-09",
               rehash_prefix="S6_PAPER_REHASH",
               scripts=["research/s6_paper_extend.py", "research/b4_paper_extend.py", "research/capacity_adv_paper_extend.py",
                        "research/g1g5_capacity_adv_weights.py", "research/g1g5_earnings_event_weights.py",
                        "research/g1g5_equity_incentive_weights.py"], title="S6 影子纸面轨",
               retire_gate=dict(fwd_mdd_floor=-0.15, six_month_rule="FWD>=6m and both AUM CAGR<B4 FWD and MDD deeper -> RETIRE (manual check)")),
}


def run(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    i = argv.index("--track"); name = argv[i + 1]; del argv[i:i + 2]
    B.configure(TRACKS[name])
    rc = B.run(argv)
    if rc == 0 and ("monitor" in argv or "all" in argv or "--mode" not in argv):
        _peers()
    return rc


def _peers():
    """Side-by-side with B4 and capacity_adv (X2 frozen + segments); written into this track's monitor.json."""
    import json
    mp = B.OUT / "monitor.json"; m = json.loads(mp.read_text())
    b4 = json.loads((B.ROOT / "output/strategy_paper_b4/monitor.json").read_text())
    cap = json.loads((B.ROOT / B.TRUNK_RUN / "book_smoke_summary.json").read_text())["by_capital"]
    peers = {}
    for c in ("600000", "1000000"):
        me = m["aum"][c]["book"]; b = b4["aum"][c]["book"]; t = cap[c]["X2/BOOK"]
        peers[c] = {B.SPEC["name"]: dict(cagr=me["cagr"], mdd=me["mdd"]), "b4": dict(cagr=b["cagr"], mdd=b["mdd"]),
                    "capacity_adv": dict(cagr=t["cagr"], mdd=t["mdd"]),
                    "segments": {"self": list(m["paper_segments"][c]), "b4": list(b4.get("paper_segments", {}).get(c, {}))},
                    "note": "X2 is in-sample (S6 picked post hoc from 16 combos); compare FWD only for decisions"}
    m["peers_X2"] = peers; mp.write_text(json.dumps(m, indent=2, ensure_ascii=False, default=float))
