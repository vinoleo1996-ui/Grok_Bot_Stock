#!/usr/bin/env python3
"""C5 re-report (K2/K6): HARD-only vs STRICT feasibility, cash dist, cash drag.

usage: core_c5_rereport.py [v1_3] [--root DIR] [--tag SUFFIX]

Definitions are aligned with Strategy's research/optimizer_core_v1_3_stats.py via scripts_eng/core_feas_defs.py
(that file writes outputs at import time, so its logic is re-stated there and cross-checked against core_v1_3_stats.json):
  - HARD-only (K2 official): status ∈ {OK, LOT_CASH_GT2}.
  - STRICT: HARD-feasible AND cash ≤ 2% (≡ status == OK).
  - Denominator excludes the no-data first day 2018-01-02 (NO_DATA_CARRY).
  - Primary unit = tier × sleeve; a tier-deduped row (date passes only if BOTH sleeves pass) is reported for reference.
Cash over 2% is disclosed only under K2; never the official failure flag.

K6: industry deviation measured vs full-pool wb. Pre-K6 sha256s live in core_x2/_void_pre_K6_sha.json; matching ⇒ 作废版本.
--root DIR computes on another dir (e.g. _archive_v1_3_pre_ruling) and writes *_{tag}.csv/txt cross-check files only.

Cash drag = sum_t max(cash_t−0.02, 0) × wb_ret_t, annualized pp (×244).
Computed ONLY when ARCH_RESIGN_A_v1_3.ok exists; else PENDING（待放行标记）.
live=false; does not create the resign marker; does not run book_smoke.
"""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_feas_defs as FD

import argparse
_ap = argparse.ArgumentParser(); _ap.add_argument("version", nargs="?", default="v1_3"); _ap.add_argument("--root"); _ap.add_argument("--tag", default="")
ARGS = _ap.parse_args()
V = ARGS.version
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/strategy_optimizer/core_x2"
ARCH_VOID = OUT / "_archive_v1_3_pre_ruling"
GATE = OUT / "ARCH_RESIGN_A_v1_3.ok"
VOID_SHA = OUT / "_void_pre_K6_sha.json"
CASH_MAX = 0.02
PERIODS = 244
WEIGHT_NAMES = (
    "core_equity_100_60w.parquet",
    "core_equity80_etf20_510300_60w.parquet",
    "core_equity_100_100w.parquet",
    "core_equity80_etf20_510300_100w.parquet",
)
HARD_OK = {"OK", "LOT_CASH_GT2"}  # cash>2% disclosed, not HARD-fail (K2)


def resolve_v13_root() -> Path:
    if ARGS.root:
        r = Path(ARGS.root)
        return r if r.is_absolute() else (OUT / r if (OUT / r).exists() else r.resolve())
    if (OUT / f"core_{V}_disclosure.csv").exists():
        return OUT
    if (ARCH_VOID / f"core_{V}_disclosure.csv").exists():
        return ARCH_VOID
    return OUT


def weight_stamp(root: Path) -> dict:
    files, shas = {}, []
    for name in WEIGHT_NAMES:
        p = root / name
        if not p.exists() and not ARGS.root:
            p = OUT / name
        if not p.exists():
            files[name] = {"missing": True}
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        st = p.stat()
        files[name] = {
            "sha256": h,
            "mtime_et": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S ET"),
            "mtime_epoch": st.st_mtime,
            "size": st.st_size,
            "path": str(p.relative_to(OUT) if p.is_relative_to(OUT) else p),
        }
        shas.append(h)
    void = False
    if VOID_SHA.exists() and shas:
        reg = json.loads(VOID_SHA.read_text(encoding="utf-8"))
        void_map = {k: v["sha256"] for k, v in reg.get("files", {}).items()}
        void = all(files.get(n, {}).get("sha256") == void_map.get(n) for n in WEIGHT_NAMES if n in void_map)
        if any(files.get(n, {}).get("missing") for n in WEIGHT_NAMES):
            void = False
        # if all present weights match void registry and none missing among registered
        present = [n for n in WEIGHT_NAMES if not files.get(n, {}).get("missing")]
        if present and all(files[n]["sha256"] == void_map.get(n) for n in present if n in void_map):
            void = len(present) == len(void_map) and all(n in void_map for n in present)
    label = "作废版本（K6 前），待 Strategy 重跑" if void else ("现行权重（K6 后授权重跑，全池 wb 行业口径）" if shas else "权重缺失")
    return {"files": files, "void_pre_K6": void, "label": label}


def cash_from_weights(root: Path) -> pd.DataFrame | None:
    """Post-lot cash on rebalance days from weight files: cash = 1 − Σw. Columns: date,aum,sleeve,cash_w."""
    rows = []
    for name in WEIGHT_NAMES:
        p = root / name
        if not p.exists() and not ARGS.root:
            p = OUT / name
        if not p.exists():
            continue
        w = pd.read_parquet(p, columns=["session", "weight", "aum", "sleeve", "is_rebalance_day", "window"])
        rb = w[w["is_rebalance_day"]].copy()
        if rb.empty:
            # some builds mark only first row; fall back to unique sessions present in disclosure later
            g = w.groupby(["session", "aum", "sleeve", "window"], as_index=False)["weight"].sum()
        else:
            g = rb.groupby(["session", "aum", "sleeve", "window"], as_index=False)["weight"].sum()
        g["cash_w"] = 1.0 - g["weight"]
        g = g.rename(columns={"session": "date"})
        rows.append(g[["date", "aum", "sleeve", "window", "cash_w"]])
    if not rows:
        return None
    return pd.concat(rows, ignore_index=True)


def wb_returns() -> pd.Series:
    for name in ("bench_hiliq_wb_x2_aligned.csv", "bench_hiliq_wb_x2.csv"):
        f = OUT / name
        if f.exists():
            b = pd.read_csv(f)
            # accept date,ret or index
            if "ret" in b.columns:
                dcol = "date" if "date" in b.columns else b.columns[0]
                return pd.Series(b["ret"].astype(float).values, index=pd.to_datetime(b[dcol].astype(str).str[:10]))
    return pd.Series(dtype=float)


def cash_drag_ann_pp(cash_by_day: pd.Series, wb: pd.Series) -> str | float:
    """cash_by_day indexed by date (datetime), values = tier cash (max across sleeves), possibly sparse rebal → ffill."""
    if not GATE.exists():
        return "PENDING（待放行标记）"
    if wb.empty or cash_by_day.empty:
        return "N/A_no_wb_or_cash"
    idx = wb.index.intersection(pd.date_range(cash_by_day.index.min(), max(cash_by_day.index.max(), wb.index.max()), freq="D"))
    # align on wb trading days only
    c = cash_by_day.sort_index().reindex(wb.index, method="ffill")
    c = c.dropna()
    if c.empty:
        return "N/A_no_overlap"
    common = c.index.intersection(wb.index)
    if len(common) < 5:
        return "N/A_short_overlap"
    excess = (c.loc[common] - CASH_MAX).clip(lower=0.0)
    drag = excess * wb.loc[common].astype(float)
    return float(drag.mean() * PERIODS * 100.0)  # annualized percentage points


def main() -> None:
    import ok_runner_pin
    ok_runner_pin.enforce(__file__, [GATE])  # refuse on runner-sha mismatch (GATE is frozen and carries no pin → always refuses until Arch issues a dedicated .ok)
    root = resolve_v13_root()
    # Arch review 4698a2c1 §8 #2: c5 rerun dropped; if it ever reruns it MUST carry --tag and write NEW suffixed files only.
    import re as _re
    if not ARGS.tag or not _re.fullmatch(r"[A-Za-z0-9_]+", ARGS.tag):
        raise SystemExit("REFUSED: core_c5_rereport needs --tag TAG ([A-Za-z0-9_]+); untagged reruns would overwrite manifest-recorded c5_* files")
    sfx = f"_{ARGS.tag}"
    for _f in (f"c5_feasibility_{V}{sfx}.csv", f"c5_cash_dist_{V}{sfx}.csv", f"c5_weight_stamp_{V}{sfx}.json", f"c5_rereport_{V}_hard_strict{sfx}.txt"):
        if (OUT / _f).exists():
            raise SystemExit(f"REFUSED: {OUT / _f} already exists; use a new --tag")
    disc_path = root / f"core_{V}_disclosure.csv"
    if not disc_path.exists():
        print(f"MISSING disclosure: {disc_path}")
        sys.exit(1)
    stamp = weight_stamp(root)
    rel = root.relative_to(OUT) if root.is_relative_to(OUT) and root != OUT else "."
    print(f"## 权重指纹 | root={rel} | {stamp['label']}")
    for n, info in stamp["files"].items():
        print(f"  {n}: MISSING" if info.get("missing") else f"  {n}: sha256={info['sha256'][:16]}… mtime={info['mtime_et']}")

    D = FD.load(disc_path)
    cw = cash_from_weights(root)
    if cw is not None:
        D = D.merge(cw, on=["date", "aum", "sleeve", "window"], how="left")
        D["cash_post"] = D["cash_w"].where(D["cash_w"].notna(), D["cash"])
    else:
        D["cash_post"] = D["cash"]
    n_cash_diff = int(((D.cash_post - D.cash).abs() > 1e-4).sum())
    T = FD.table(D)
    chk = FD.check_against_stats(T, root / f"core_{V}_stats.json")
    runs = {int(a): FD.consecutive_fail_runs(D, int(a)) for a in sorted(D.aum.unique())}

    lines = [
        f"# C5 重报 {V}（K2 HARD-only / STRICT；定义对齐 research/optimizer_core_v1_3_stats.py；K6 指纹）",
        f"- 权重标签：{stamp['label']}",
        f"- 数据根：{root}",
        "- 定义：HARD-only = status∈{OK,LOT_CASH_GT2}；STRICT = HARD 可行 且 cash≤2%（≡ status==OK）；分母剔除 2018-01-02 NO_DATA_CARRY 首日；"
        "主单位 = 资金档×口径，档去重行（两口径都过才算过）仅作参考。",
        f"- 与 Strategy core_{V}_stats.json 交叉核对：{'; '.join(chk)}",
        f"- strict==status OK 一致：{D.attrs.get('strict_eq_ok')}；disclosure cash 与权重推算 cash 差>1e-4 的行：{n_cash_diff}（判定用 disclosure cash，与 Strategy 一致）",
        f"- X2 起（2024-06）连续 ≥2 个调仓日 HARD 失败的区段（按档，任一口径失败即算）：{runs}",
        f"- 门控 ARCH_RESIGN_A_v1_3.ok：{'存在' if GATE.exists() else '不存在（现金拖累=PENDING）'}",
        "",
        "| window | aum | 口径 | n(剔除首日) | HARD-only | STRICT | HARD 可行但 cash>2% |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in T.itertuples():
        lines.append(f"| {r.window} | {r.aum} | {r.tag} {r.sleeve} | {r.n_eval} | {r.n_hard}/{r.n_eval}={r.hard_pct}% | {r.n_strict}/{r.n_eval}={r.strict_pct}% | {r.cash_gt2_hard_rows} |")

    cash_rows, drag_rows = [], []
    wb = wb_returns()
    for (w, a), g in pd.concat([D, D.assign(window="ALL")]).groupby(["window", "aum"], sort=False):
        d = g[~g.nodata].groupby("date").agg(cash=("cash_post", "max"))
        cv = d.cash.astype(float)
        cash_rows.append(dict(window=w, aum=a, basis="tier_max_over_sleeves_ex_nodata", cash_p5=float(cv.quantile(.05)), cash_p50=float(cv.quantile(.5)),
                              cash_p95=float(cv.quantile(.95)), cash_max=float(cv.max()), cash_gt2_share=float((cv > CASH_MAX + FD.EPS).mean()),
                              cash_gt2_days=int((cv > CASH_MAX + FD.EPS).sum())))
        # wb (bench_hiliq_wb_x2.csv) only covers X2 (2024-06-03→2026-10-09): drag is defined for X2 only
        drag = cash_drag_ann_pp(pd.Series(cv.values, index=pd.to_datetime(d.index)).sort_index(), wb) if w == "X2" else "N/A（wb 仅覆盖 X2）"
        drag_rows.append(dict(window=w, aum=a, cash_drag_ann_pp=drag))
    C = pd.DataFrame(cash_rows).merge(pd.DataFrame(drag_rows), on=["window", "aum"])
    T2 = T.merge(C, on=["window", "aum"], how="left")
    T2["void_pre_K6"] = stamp["void_pre_K6"]; T2["weight_label"] = stamp["label"]
    T2["hard_runs_ge2_from_X2"] = T2.aum.map(lambda a: " ".join(runs.get(int(a), [])) or "none")
    T2["stats_crosscheck"] = chk[0] if len(chk) == 1 else "MISMATCH"
    lines += ["", "| window | aum | 现金 p5/p50/p95/max（档内两口径取 max，剔除首日） | cash>2% 占比 | 现金拖累(年化pp) |", "|---|---|---|---|---|"]
    for r in C.itertuples():
        dr = r.cash_drag_ann_pp if isinstance(r.cash_drag_ann_pp, str) else f"{r.cash_drag_ann_pp:.3f}pp"
        lines.append(f"| {r.window} | {r.aum} | {r.cash_p5:.3f}/{r.cash_p50:.3f}/{r.cash_p95:.3f}/{r.cash_max:.3f} | {r.cash_gt2_share:.1%} | {dr} |")
        print(f"{r.window} {r.aum}: cash p50={r.cash_p50:.3f} max={r.cash_max:.3f} gt2={r.cash_gt2_share:.1%} drag={dr}")
    print(T[["window", "aum", "tag", "n_eval", "hard_pct", "strict_pct"]].to_string(index=False))
    print("crosscheck:", chk, "| runs:", runs)
    T2.to_csv(OUT / f"c5_feasibility_{V}{sfx}.csv", index=False)
    C.to_csv(OUT / f"c5_cash_dist_{V}{sfx}.csv", index=False)
    (OUT / f"c5_weight_stamp_{V}{sfx}.json").write_text(json.dumps(stamp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    txt = OUT / f"c5_rereport_{V}_hard_strict{sfx}.txt"
    txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT / f'c5_feasibility_{V}{sfx}.csv'} and {txt}")


if __name__ == "__main__":
    main()
