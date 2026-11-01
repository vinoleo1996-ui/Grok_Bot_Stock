"""Book-Smoke skeleton — Mandate-aligned main book @60万∧100万 (research only).

strategy_promotion_approved=false. Does NOT claim sealed pass.
Default: core ETF (510300) 100% when no stock/alpha weight table is supplied.
KPI: consumable weight long-table rows + book NAV path (not GP attempt counts).

Usage:
  python3 -m quantlab.portfolio.book_smoke
  python3 -m quantlab.portfolio.book_smoke --stock-path path/to/weights.parquet
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from quantlab.portfolio.v2_multisleeve_book import (  # noqa: E402
    DEFAULT_SLEEVES, SPOT_MAX_GROSS, WINDOWS, WINDOW_LABEL, Data, sha, HASH_FILES,
    arm_schedules, run_book,
)

log = logging.getLogger("book_smoke")
AUMS = (600_000, 1_000_000)
DEFAULT_OUT = "output/v3/book_smoke_stock_etf"
RECEIPT = "docs/v2/BOOK_SMOKE_STOCK_ETF_RECEIPT_20261012_ZH.md"


def _consumable_rows(notes: dict) -> dict:
    out = {}
    for k in ("stock", "alpha_event"):
        n = notes.get(k) or {}
        out[k] = {
            "status": n.get("status", "absent"),
            "n_rows": n.get("n_rows", 0),
            "n_sessions": n.get("n_sessions", 0),
            "not_book_consumable": n.get("not_book_consumable", True),
            "path": n.get("path"),
            "error": n.get("error"),
        }
    return out


def run(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--windows", default="X2", help="default explore X2; sealed refused by book module")
    ap.add_argument("--capitals", default="600000,1000000")
    ap.add_argument("--sleeves", default=json.dumps(DEFAULT_SLEEVES))
    ap.add_argument("--arms", default="BOOK,C0")
    ap.add_argument("--stock-path", default=None)
    ap.add_argument("--alpha-event-path", default=None)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--receipt", default=RECEIPT)
    ap.add_argument("--skip-run", action="store_true", help="write receipt scaffold only")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    capitals = [int(x) for x in a.capitals.split(",") if x.strip()]
    for c in capitals:
        if c not in AUMS:
            log.warning("capital %s not in Mandate main set %s (allowed for diag)", c, AUMS)

    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    sleeve_w = json.loads(a.sleeves) if isinstance(a.sleeves, str) else a.sleeves
    has_stock_budget = float(sleeve_w.get("stock", 0) or 0) + float(sleeve_w.get("alpha_event", 0) or 0) > 0
    gap = []
    if not (a.stock_path or a.alpha_event_path):
        gap.append("无 --stock-path / --alpha-event-path → 纯 510300 book baseline")
    if not has_stock_budget:
        gap.append("stock+alpha_event 预算均为 0 → 默认 core=1.0")

    ns = argparse.Namespace(
        sleeves=a.sleeves, stock_path=a.stock_path, alpha_event_path=a.alpha_event_path,
        cash_target=0.02, target_vol=None, leverage=1.0, max_gross=SPOT_MAX_GROSS,
        collateral_frac=1.0, e2_pool="sh.510300,sh.510500,sz.159915",
        cb_full_rules=True, static_ic=0.75,
    )

    result = {
        "run_id": f"book_smoke_{time.strftime('%Y%m%d_%H%M%S')}",
        "strategy_promotion_approved": False,
        "mandate_ref": "docs/v2/MANDATE_UNIFIED_STOCK_ETF_20261012_ZH.md",
        "sealed_claim": False,
        "gaps": gap,
        "sleeve_weights": sleeve_w,
        "windows": a.windows,
        "capitals": capitals,
        "kpi_note": "consumable weight long-table rows + book NAV; NOT GP attempt counts",
        "factory_stop_suggestion": "连续 GATE_OK=0 包 → 停 GP；以 Book-Smoke / 可消费长表为进度 KPI",
        "by_capital": {},
        "consumable": {},
    }

    if a.skip_run:
        # Validate a supplied weight table without opening ETF panels or writing NAV.
        from quantlab.platform.weight_long_table import validate_weight_path

        def _path_note(path):
            if not path:
                return {
                    "status": "not_book_consumable",
                    "n_rows": 0,
                    "n_sessions": 0,
                    "not_book_consumable": True,
                    "path": None,
                    "error": "no_path",
                }
            meta = validate_weight_path(path, require_rows=True)
            readable = meta.get("status") == "ok" and int(meta.get("n_rows") or 0) > 0
            return {
                "status": "book_consumable" if readable else "not_book_consumable",
                "n_rows": int(meta.get("n_rows") or 0),
                "n_sessions": int(meta.get("n_sessions") or 0),
                "not_book_consumable": not readable,
                "path": str(path),
                "error": meta.get("error"),
                "promotion_approved": False,
            }

        result["consumable"] = {
            "stock": _path_note(a.stock_path),
            "alpha_event": _path_note(a.alpha_event_path),
        }
        result["nav_ran"] = False
        result["strategy_promotion_approved"] = False
        (out / "book_smoke_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        _write_receipt(ROOT / a.receipt, result, ran=False)
        return result

    D = Data(with_cb=False, with_ind_etf=False)
    hashes = {f: sha(f) for f in HASH_FILES if (ROOT / f).exists()}
    wins = {w: WINDOWS[w] for w in a.windows.split(",")}

    # Probe stock/alpha consumability once (independent of C0 empty notes)
    probe_idx = D.HFQ.loc[list(wins.values())[0][0]:list(wins.values())[0][1]].index
    _, _, _, probe_notes = arm_schedules("BOOK", D, probe_idx, sleeve_w, ns, *list(wins.values())[0])
    result["consumable"] = _consumable_rows(probe_notes)

    for capital in capitals:
        bucket = {}
        for wn, (s, e) in wins.items():
            idx = D.HFQ.loc[s:e].index
            if len(idx) < 5:
                bucket[wn] = {"error": f"too_few_sessions:{len(idx)}"}
                continue
            for arm in a.arms.split(","):
                t0 = time.time()
                sched, sf, desc, notes = arm_schedules(arm, D, idx, sleeve_w, ns, s, e)
                meta = dict(
                    arm=arm, description=desc, window=wn,
                    window_label=WINDOW_LABEL.get(wn, "custom"),
                    window_dates=[s, e], research_only=True,
                    strategy_promotion_approved=False, promotion_approved=False,
                    sealed_claim=False, book_smoke=True,
                    mandate_ref=result["mandate_ref"],
                    sleeve_weights=sleeve_w, gaps=gap,
                    consumable=result["consumable"],
                    spot_financing_executable=True,
                    leverage=1.0, max_gross=SPOT_MAX_GROSS,
                    data_hashes=hashes, initial_cash=capital,
                    engine="run_weight_schedule + ExecConfig.strategy_v1",
                )
                odir = out / f"aum_{capital}" / wn / arm
                m = run_book(D, sched, s, e, odir, initial_cash=float(capital),
                             sleeve_frame=sf, meta=meta)
                m.pop("_raw", None)
                key = f"{wn}/{arm}"
                bucket[key] = {k: v for k, v in m.items() if k != "costs"} | {"costs": m.get("costs")}
                # also dump target weight long count
                tw = odir / "target_weights.parquet"
                n_tw = int(__import__("pandas").read_parquet(tw).shape[0]) if tw.exists() else 0
                bucket[key]["n_target_weight_rows"] = n_tw
                log.info("AUM=%s %s cagr=%.4f mdd=%.4f sh=%.3f cost=%.4f tw_rows=%d (%.1fs)",
                         capital, key, m["cagr"], m["mdd"], m["sharpe"], m["cost_pct_initial"],
                         n_tw, time.time() - t0)
        result["by_capital"][str(capital)] = bucket

    # headline table
    headline = []
    for capital, bucket in result["by_capital"].items():
        for key, m in bucket.items():
            if "error" in m:
                continue
            headline.append(dict(
                capital=int(capital), arm=key,
                cagr=m.get("cagr"), mdd=m.get("mdd"), sharpe=m.get("sharpe"),
                cost_pct_initial=m.get("cost_pct_initial"),
                n_target_weight_rows=m.get("n_target_weight_rows"),
                start=m.get("start"), end=m.get("end"),
            ))
    result["headline"] = headline
    (out / "book_smoke_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    _write_receipt(ROOT / a.receipt, result, ran=True)
    log.info("wrote %s and %s", out / "book_smoke_summary.json", a.receipt)
    return result


def _write_receipt(path: Path, result: dict, *, ran: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Book-Smoke 回执（个股+ETF 主书骨架）",
        "",
        f"**run_id**：`{result.get('run_id')}`  ",
        f"**strategy_promotion_approved**：`false`  ",
        f"**sealed_claim**：`false`（不声称过密封线）  ",
        f"**Mandate**：`{result.get('mandate_ref')}`  ",
        "",
        "## 缺口",
        "",
    ]
    for g in result.get("gaps") or ["（无）"]:
        lines.append(f"- {g}")
    lines += [
        "",
        "## 袖套",
        "",
        f"```json\n{json.dumps(result.get('sleeve_weights'), ensure_ascii=False)}\n```",
        "",
        "## 可消费权重长表（KPI）",
        "",
        f"```json\n{json.dumps(result.get('consumable'), indent=2, ensure_ascii=False)}\n```",
        "",
        "## 停机建议",
        "",
        result.get("factory_stop_suggestion", ""),
        "",
    ]
    if not ran:
        lines += ["## 结果", "", "（`--skip-run`：未执行净值）", ""]
    else:
        lines += [
            "## 净值摘要（探索窗；成本开；非密封）",
            "",
            "| AUM | arm | CAGR | MDD | Sharpe | cost/AUM | target_weight 行数 | 起止 |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for h in result.get("headline") or []:
            lines.append(
                f"| {h['capital']} | {h['arm']} | "
                f"{h['cagr']:.4f} | {h['mdd']:.4f} | {h['sharpe']:.3f} | "
                f"{h['cost_pct_initial']:.4f} | {h['n_target_weight_rows']} | "
                f"{h['start']}→{h['end']} |"
            )
        lines += [
            "",
            f"JSON：`output/v3/book_smoke_stock_etf/book_smoke_summary.json`",
            "",
            "> 无个股权重时长表时，BOOK≈C0（纯 510300）。有 `--stock-path` 后 BOOK 才会偏离 C0。",
            "",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
