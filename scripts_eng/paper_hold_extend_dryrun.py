"""DRY-RUN (labelled): carry capacity_adv + B4 paper NAV past the X2 end by holding the last weights.
- Does NOT change WINDOWS['X2']; injects a runtime-only window 'X2H' = (2024-06-03, <last calendar session>).
- Weights: last session's rows copied forward to each later session (hold); written under output/loop/hold_extend_dryrun/.
- Never touches output/strategy_paper_capacity_adv, B4 FROZEN_CONFIG, or the source weight files. live=false.
"""
import json, sys, os
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
import quantlab.portfolio.v2_multisleeve_book as M
from quantlab.portfolio.book_smoke import run as bs
OUT = Path("output/loop/hold_extend_dryrun"); OUT.mkdir(parents=True, exist_ok=True)
cal = pd.read_parquet("data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date"], filters=[("ts_code", "=", "510300.SH")])
cal = sorted(pd.to_datetime(cal.trade_date.astype(str)).unique())
END = str(pd.Timestamp(cal[-1]).date())
M.WINDOWS["X2H"] = ("2024-06-03", END); M.WINDOW_LABEL["X2H"] = f"DRY-RUN X2+hold to {END} (not a research window)"
fz = json.loads(Path("output/strategy_paper_b4/FROZEN_CONFIG.json").read_text())["weights"]
jobs = [("capacity_adv", "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet", [600000, 1000000]),
        ("b4_60w", fz["600000"]["path"], [600000]), ("b4_100w", fz["1000000"]["path"], [1000000])]
S = '{"core":0.0,"stock":1.0,"alpha_event":0.0}'
meta = dict(label="DRY_RUN_HOLD_EXTEND", live=False, promotion_approved=False, end=END, runs={})
for name, src, caps in jobs:
    w = pd.read_parquet(src); key = w.session.astype(str).str[:10]
    last = key.max(); tail = w[key == last]
    add = []
    for d in [pd.Timestamp(x) for x in cal if pd.Timestamp(x) > pd.Timestamp(last)]:
        t = tail.copy()
        for c in ("session", "date"):
            if c in t: t[c] = d if w[c].dtype.kind == "M" else str(d.date())
        add.append(t)
    ext = pd.concat([w] + add, ignore_index=True)
    p = OUT / f"{name}_weights_hold_to_{END.replace('-', '')}.parquet"; ext.to_parquet(p, index=False)
    for cap in caps:
        o = OUT / f"{name}_aum_{cap}"
        bs(["--stock-path", str(p), "--sleeves", S, "--windows", "X2H", "--capitals", str(cap), "--arms", "BOOK,C0",
            "--out", str(o), "--receipt", str(o / "RECEIPT_DRYRUN.md")])
        n = pd.read_csv(o / f"aum_{cap}/X2H/BOOK/nav.csv")
        meta["runs"][f"{name}_{cap}"] = dict(weights=str(p), held_from=last, added_sessions=len(add),
                                            nav=str(o / f"aum_{cap}/X2H/BOOK/nav.csv"), tail=n.iloc[-4:, :2].values.tolist())
(OUT / "DRYRUN_SUMMARY.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str))
print(json.dumps(meta["runs"], ensure_ascii=False, default=str, indent=1))
