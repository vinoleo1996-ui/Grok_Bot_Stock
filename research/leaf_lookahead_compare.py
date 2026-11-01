"""Compare truncated-source runs vs full run on dates <= cutoff (Freqtrade-style lookahead check); writes lookahead_check.json."""
import sys, json
from pathlib import Path
import pandas as pd
R = Path(__file__).resolve().parents[1] / "output/ai_factory/leaf_reports"
for leaf in sys.argv[1:]:
    d = R / leaf; F = pd.read_parquet(d / "lookahead_full.parquet"); F["date"] = F["date"].astype(str).str[:10]
    out = {}
    for c in ["2024-12-31", "2025-06-30", "2026-03-31"]:
        T = pd.read_parquet(d / f"lookahead_{c}.parquet"); T["date"] = T["date"].astype(str).str[:10]
        a = F[F.date <= c].set_index(["date", "instrument"]).target_weight; b = T[T.date <= c].set_index(["date", "instrument"]).target_weight
        a, b = a[a.abs() > 1e-12], b[b.abs() > 1e-12]; j = pd.concat([a, b], axis=1, keys=["full", "trunc"]).fillna(0)
        diff = (j.full - j.trunc).abs(); bad = j[diff > 1e-9]
        out[c] = dict(rows_full=int(len(a)), rows_trunc=int(len(b)), max_abs_diff=float(diff.max()), n_mismatch=int(len(bad)),
                      first_mismatch_date=(bad.index[0][0] if len(bad) else None), ok=bool(len(bad) == 0))
    res = dict(leaf=leaf, method="事件源表按 available_at 截断于 T 后重跑；比较 date<=T 的权重", cutoffs=out, status="PASS" if all(v["ok"] for v in out.values()) else "FAIL")
    (d / "lookahead_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(leaf, res["status"], {k: (v["n_mismatch"], v["max_abs_diff"], v["first_mismatch_date"]) for k, v in out.items()})
