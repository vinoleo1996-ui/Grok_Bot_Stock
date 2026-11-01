"""Minimal RD-Agent-style stub: candidates → hard gates → consumable weight long-table.

Synthetic mid/large ETF + large-cap scores only (smoke). Does NOT open sealed.
Does NOT place orders. strategy_promotion_approved=false.

QuantMind P0 smoke fixtures cover:
  pass (dual ICIR + impact@60∧100), fail missing who_pays,
  fail impact below floor, fail overnight spirit.

KPI: n_weight_rows written under output/factor_evolve/.
Smoke windows are short by design; production AI daily must be full series
(see QUANTMIND_P0_GATE_WEIGHT_CONTRACT_ZH.md).

Usage:
  cd /workspace/QuantLab && python3 -m quantlab.agents.factor_evolve --smoke
  python3 -m quantlab.agents.factor_evolve --smoke --capital 1000000 --top-k 5
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from quantlab.agents.factor_evolve.hard_gates import (  # noqa: E402
    HARD_GATE_VERSION,
    gate_batch,
)
from quantlab.agents.factor_evolve.schemas import (  # noqa: E402
    COLUMN_CONTRACT_VERSION,
    EvolveRunMeta,
    FactorCandidate,
    PROMOTION_APPROVED,
)
from quantlab.agents.factor_evolve.weights_from_scores import (  # noqa: E402
    build_weight_meta,
    scores_to_long_table,
    write_weight_meta,
    write_weight_parquet,
)

OUT_DIR = ROOT / "output" / "factor_evolve"
DEFAULT_WINDOW = "X2_stub_2024-06..2024-07"


def _synth_candidates() -> list[FactorCandidate]:
    """Pass/fail fixtures for QuantMind P0 gates."""
    sessions = pd.bdate_range("2024-06-03", periods=10)
    etfs = ["510300.SH", "510500.SH", "512480.SH", "159915.SZ", "588000.SH"]
    large = ["600519.SH", "601318.SH", "600036.SH", "000858.SZ", "601166.SH"]

    def scores(codes: list[str], base: float) -> list[dict]:
        rows = []
        for i, d in enumerate(sessions):
            for j, c in enumerate(codes):
                rows.append(
                    {
                        "session": d.strftime("%Y-%m-%d"),
                        "instrument_id": c,
                        "score": base + 0.1 * ((i + j) % 5) - 0.05 * j,
                    }
                )
        return rows

    # 1) PASS — dual ICIR + impact both ≥10
    good_etf: FactorCandidate = {
        "candidate_id": "stub_etf_flow_resid_v1",
        "expr_str": "rank(etf_share_flow_20)",
        "mechanism_tag": "etf_flow",
        "who_pays_zh": "追逐主题ETF申购的短线资金在份额回流时把冲击卖给宽基承接盘。",
        "universe_kind": "etf_theme",
        "direction_zh": "行业/主题ETF份额流残差短窗，中大盘成分可交易。",
        "score_rows": scores(etfs, 1.0),
        "icir_eps_gate": 0.22,
        "icir_eps_posthoc": 0.19,
        "impact_flat25_pct_60万": 12.5,
        "impact_flat25_pct_100万": 11.2,
    }
    # 2) PASS — dual ICIR with EDGE_WARN gap (gate thin, posthoc large) still pass
    good_stock: FactorCandidate = {
        "candidate_id": "stub_nb_hold_delta_v1",
        "expr_str": "rank(hk_hold_delta_5)",
        "mechanism_tag": "sentiment",
        "who_pays_zh": "北向被动调仓与跟风内资在披露后次日承接。",
        "universe_kind": "mid_large_stock",
        "direction_zh": "北向持仓增量短窗，浮股市值中大盘篮。",
        "score_rows": scores(large, 0.8),
        "icir_eps_gate": 0.08,
        "icir_eps_posthoc": 2.15,
        "impact_flat25_pct_60万": 14.0,
        "impact_flat25_pct_100万": 13.1,
    }
    # 3) FAIL — missing who_pays
    bad_no_who: FactorCandidate = {
        "candidate_id": "stub_no_who_pays_fail",
        "expr_str": "rank(lockup_pressure)",
        "mechanism_tag": "lockup",
        "who_pays_zh": "",
        "universe_kind": "mid_large_stock",
        "direction_zh": "解禁压力短窗",
        "score_rows": scores(large[:3], 0.4),
        "icir_eps_gate": 0.18,
        "icir_eps_posthoc": 0.16,
        "impact_flat25_pct_60万": 11.0,
        "impact_flat25_pct_100万": 10.5,
    }
    # 4) FAIL — impact below 10% at 100万
    bad_impact: FactorCandidate = {
        "candidate_id": "stub_impact_fail",
        "expr_str": "rank(theme_breadth_mid)",
        "mechanism_tag": "theme",
        "who_pays_zh": "题材一日游资金把冲击卖给宽基。",
        "universe_kind": "mid_large_stock",
        "direction_zh": "主题拥挤度残差（冲击不足应拒）",
        "score_rows": scores(large[:3], 0.35),
        "icir_eps_gate": 0.20,
        "icir_eps_posthoc": 0.17,
        "impact_flat25_pct_60万": 11.0,
        "impact_flat25_pct_100万": 6.5,
    }
    # 5) FAIL — overnight spirit
    bad_overnight: FactorCandidate = {
        "candidate_id": "stub_overnight_fail",
        "expr_str": "ts_mean_5(ind_rel_overnight)",
        "mechanism_tag": "overnight_ind_rel",
        "who_pays_zh": "隔夜跳空对手方。",
        "universe_kind": "mid_large_stock",
        "direction_zh": "行业相对隔夜收益短窗（硬禁）",
        "score_rows": scores(large[:3], 0.55),
        "icir_eps_gate": 0.25,
        "icir_eps_posthoc": 0.21,
        "impact_flat25_pct_60万": 15.0,
        "impact_flat25_pct_100万": 14.0,
    }
    # 6) FAIL — textbook momentum (kept)
    bad_textbook: FactorCandidate = {
        "candidate_id": "stub_momentum_fail",
        "expr_str": "rank(momentum_20)",
        "mechanism_tag": "sentiment",
        "who_pays_zh": "谁付钱占位。",
        "universe_kind": "mid_large_stock",
        "direction_zh": "动量选股（应被硬闸拒绝）",
        "score_rows": scores(large[:3], 0.5),
        "icir_eps_gate": 0.12,
        "icir_eps_posthoc": 0.10,
        "impact_flat25_pct_60万": 12.0,
        "impact_flat25_pct_100万": 11.0,
    }
    return [good_etf, good_stock, bad_no_who, bad_impact, bad_overnight, bad_textbook]


def run(*, capital_cny: int = 600_000, top_k: int = 5, out_dir: Path | None = None) -> EvolveRunMeta:
    out = Path(out_dir) if out_dir else OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    run_id = f"fe_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    cands = _synth_candidates()
    gates = gate_batch(cands, capital_cny=capital_cny)
    passed_ids = {g["candidate_id"] for g in gates if g.get("verdict") == "pass"}
    passed = [c for c in cands if c.get("candidate_id") in passed_ids]
    failed = [g for g in gates if g.get("verdict") != "pass"]

    # sleeve_budget research-only: stub emits full-sleeve weights; Book-Smoke
    # still needs --sleeves with stock/alpha_event >0 to consume them.
    long_df = scores_to_long_table(passed, top_k=top_k, equal_weight=True, sleeve_budget=1.0)
    weight_path = out / f"{run_id}_weights.parquet"
    n_rows = write_weight_parquet(long_df, weight_path) if not long_df.empty else 0
    if long_df.empty:
        write_weight_parquet(long_df, weight_path)

    wmeta = build_weight_meta(long_df, smoke=True, extra={"run_id": run_id})
    wmeta_path = out / f"{run_id}_weights_meta.json"
    write_weight_meta(wmeta, wmeta_path)

    gate_path = out / f"{run_id}_gates.json"
    gate_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "hard_gate_version": HARD_GATE_VERSION,
                "promotion_approved": False,
                "gates": gates,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    meta: EvolveRunMeta = {
        "run_id": run_id,
        "capital_cny": capital_cny,
        "window": DEFAULT_WINDOW,
        "n_candidates": len(cands),
        "n_passed": len(passed),
        "n_failed": len(failed),
        "n_weight_rows": n_rows,
        "weight_path": str(weight_path.relative_to(ROOT)) if weight_path.is_relative_to(ROOT) else str(weight_path),
        "gate_receipt_path": str(gate_path.relative_to(ROOT)) if gate_path.is_relative_to(ROOT) else str(gate_path),
        "strategy_promotion_approved": bool(PROMOTION_APPROVED),
        "benchmark": "510300.SH",
        "mandate_note": "CAGR12-18%/MDD-28%; stub only; not sealed; no orders; QM P0 gates",
        "hard_gate_version": HARD_GATE_VERSION,
        "column_contract_version": COLUMN_CONTRACT_VERSION,
        "stub_window": False,  # smoke=True → not production stub WARN
        "smoke": True,
    }
    if wmeta.get("stub_window_warn"):
        meta["stub_window_warn"] = str(wmeta["stub_window_warn"])
    meta_path = out / f"{run_id}_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "latest_weights.path").write_text(str(weight_path) + "\n", encoding="utf-8")
    (out / "latest_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "latest_weights_meta.json").write_text(
        json.dumps(wmeta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--smoke", action="store_true", help="run synthetic stub (required for now)")
    ap.add_argument("--capital", type=int, default=600_000, choices=[600_000, 1_000_000])
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--out", default=str(OUT_DIR))
    a = ap.parse_args(argv)
    if not a.smoke:
        print("pass --smoke (real panels require Leo explore approval + Data panels)", file=sys.stderr)
        return 2
    meta = run(capital_cny=a.capital, top_k=a.top_k, out_dir=Path(a.out))
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(
        f"KPI n_weight_rows={meta['n_weight_rows']} path={meta['weight_path']} "
        f"n_passed={meta['n_passed']} n_failed={meta['n_failed']} "
        f"gate={meta.get('hard_gate_version')} promotion={meta['strategy_promotion_approved']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
