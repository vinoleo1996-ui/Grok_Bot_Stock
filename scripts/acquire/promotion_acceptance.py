#!/usr/bin/env python3
"""Run promotion acceptance checklist; write PROMOTION_ACCEPTANCE.md + update manifests.
Only sets promotion_approved=true when evidence passes. Never invents data.
"""
from __future__ import annotations
import json, os, sys, pathlib, datetime as dt
from zoneinfo import ZoneInfo
import warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab")
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd

TZ = ZoneInfo("America/New_York")
NOW = dt.datetime.now(TZ)
DOC = ROOT / "docs/v2/PROMOTION_ACCEPTANCE.md"
RAW = ROOT / "data/v2/tushare_raw"
V2 = ROOT / "data/v2"

def to_iid(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(
        r"(\d+)\.(SH|SZ|BJ)",
        lambda m: ("sh." if m.group(2) == "SH" else "sz." if m.group(2) == "SZ" else "bj.") + m.group(1),
        regex=True,
    )

def jdump(path: pathlib.Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n")

def check_sw() -> dict:
    path = V2 / "sw_l1_pit/industry_members_sw_l1_tushare.parquet"
    out = {"id": "sw_l1_pit_tushare", "path": str(path), "pass": False, "blockers": [], "metrics": {}}
    if not path.exists():
        out["blockers"].append("missing tushare SW table"); return out
    sw = pd.read_parquet(path)
    req = ["instrument_id","sw_code","sw_name","in_date","out_date","available_at","source","revision","quality_status"]
    missing = [c for c in req if c not in sw.columns]
    if missing: out["blockers"].append(f"missing cols {missing}")
    n_l1 = int(sw.sw_code.nunique())
    n_inst = int(sw.instrument_id.nunique())
    null_at = int(sw.available_at.isna().sum())
    cur = sw[sw.get("is_new", pd.Series(dtype=str)) == "Y"] if "is_new" in sw.columns else sw[sw.out_date.isna()]
    # reconcile vs stock_basic listed
    sb_parts = []
    for st in "L":
        f = RAW / "stock_basic" / f"{st}.parquet"
        if f.exists(): sb_parts.append(pd.read_parquet(f))
    cover = None
    if sb_parts:
        sb = pd.concat(sb_parts, ignore_index=True)
        sb["instrument_id"] = to_iid(sb.ts_code)
        listed = set(sb.instrument_id)
        cur_ids = set(cur.instrument_id)
        cover = len(listed & cur_ids) / max(len(listed), 1)
        out["metrics"]["listed_cover_frac"] = round(cover, 4)
        out["metrics"]["listed_n"] = len(listed)
        out["metrics"]["current_members_n"] = len(cur_ids)
    # sample reconcile vs prefix on overlapping instruments
    pref = V2 / "sw_l1_pit/industry_members_sw_l1_prefix.parquet"
    agree = None
    if pref.exists():
        p = pd.read_parquet(pref)
        # as-of 2026-06-30 assignment compare
        asof = pd.Timestamp("2026-06-30")
        def assign(df):
            x = df.copy()
            x["in_date"] = pd.to_datetime(x.in_date)
            x["out_date"] = pd.to_datetime(x.out_date)
            m = (x.in_date <= asof) & (x.out_date.isna() | (x.out_date > asof))
            a = x.loc[m].sort_values("in_date").groupby("instrument_id").tail(1)
            return a.set_index("instrument_id")["sw_code"]
        a_ts, a_pf = assign(sw), assign(p)
        def norm(c):
            return c.astype(str).str.replace(r"\.SI$","", regex=True)
        both = a_ts.index.intersection(a_pf.index)
        if len(both):
            agree = float((norm(a_ts.loc[both]).values == norm(a_pf.loc[both]).values).mean())
            out["metrics"]["asof_20260630_agree_vs_prefix"] = round(agree, 4)
            out["metrics"]["asof_overlap_n"] = int(len(both))
    out["metrics"].update({
        "rows": len(sw), "n_l1": n_l1, "n_instruments": n_inst,
        "available_at_nulls": null_at,
        "in_date_min": str(pd.to_datetime(sw.in_date).min())[:10],
        "in_date_max": str(pd.to_datetime(sw.in_date).max())[:10],
    })
    # Pass criteria (promotion-grade bar)
    if n_l1 < 31: out["blockers"].append(f"L1 codes {n_l1}<31")
    if null_at > 0: out["blockers"].append(f"available_at nulls={null_at}")
    if cover is not None and cover < 0.90: out["blockers"].append(f"listed cover {cover:.2%}<90%")
    if n_inst < 5000: out["blockers"].append(f"instruments {n_inst}<5000")
    # agreement with prefix is informational; don't require (prefix may be wrong)
    if not out["blockers"] and not missing:
        out["pass"] = True
        out["quality_status"] = "promotion_candidate_tushare"
    else:
        out["quality_status"] = "research_tushare_candidate"
    return out

def check_float_mktcap() -> dict:
    path = V2 / "float_mktcap/float_mktcap_daily_tushare.parquet"
    out = {"id": "float_mktcap_daily", "path": str(path), "pass": False, "blockers": [], "metrics": {}}
    if not path.exists():
        out["blockers"].append("missing float_mktcap_daily_tushare.parquet"); return out
    m = pd.read_parquet(path)
    m["trade_date"] = pd.to_datetime(m.trade_date)
    out["metrics"]["rows"] = len(m)
    out["metrics"]["n_instruments"] = int(m.instrument_id.nunique())
    out["metrics"]["date_min"] = str(m.trade_date.min())[:10]
    out["metrics"]["date_max"] = str(m.trade_date.max())[:10]
    # asof window coverage 2026-06-30 .. 2026-10-09
    win = m[(m.trade_date >= "2026-06-30") & (m.trade_date <= "2026-10-09")]
    by_day = win.groupby(win.trade_date.dt.date).instrument_id.nunique()
    out["metrics"]["asof_window_days"] = int(by_day.shape[0])
    out["metrics"]["asof_window_median_inst"] = int(by_day.median()) if len(by_day) else 0
    out["metrics"]["asof_window_min_inst"] = int(by_day.min()) if len(by_day) else 0
    # cross-check vs research asof (prefer full 2026-06-30)
    for asof_name, day in [("float_mktcap_asof_2026-06-30.parquet", "2026-06-30"),
                           ("float_mktcap_asof_2026-10-09.parquet", "2026-10-09")]:
        asof_p = V2 / "float_mktcap" / asof_name
        if not asof_p.exists() or not len(win):
            continue
        a = pd.read_parquet(asof_p)
        w = win[win.trade_date == day][["instrument_id","float_mktcap"]].rename(columns={"float_mktcap":"ts"})
        if w.empty or "float_mktcap" not in a.columns:
            continue
        a2 = a[["instrument_id","float_mktcap"]].rename(columns={"float_mktcap":"ref"})
        j = w.merge(a2, on="instrument_id")
        j = j[(j.ts > 0) & (j.ref > 0)]
        if not len(j):
            continue
        rel = (j.ts - j.ref).abs() / j.ref
        key = "vs_asof0630" if "06-30" in asof_name else "vs_asof1009"
        out["metrics"][f"{key}_n"] = int(len(j))
        out["metrics"][f"{key}_within_1pct"] = round(float((rel <= 0.01).mean()), 4)
        out["metrics"][f"{key}_within_5pct"] = round(float((rel <= 0.05).mean()), 4)
        out["metrics"][f"{key}_median_abs_rel"] = round(float(rel.median()), 6)
        # primary gate uses best full-market day
        if "06-30" in asof_name:
            out["metrics"]["vs_asof_within_5pct"] = out["metrics"][f"{key}_within_5pct"]
            out["metrics"]["vs_asof_within_1pct"] = out["metrics"][f"{key}_within_1pct"]
            out["metrics"]["vs_asof_n"] = out["metrics"][f"{key}_n"]
            out["metrics"]["vs_asof_median_abs_rel"] = out["metrics"][f"{key}_median_abs_rel"]
    # also check free_hunt tencent validate json
    tj = V2 / "free_hunt/mktcap/validate_data_asof_vs_tencent_20261009.json"
    if tj.exists():
        out["metrics"]["tencent_validate"] = json.loads(tj.read_text())
    # Pass bar: asof window daily full market ~>=4500 instruments on most days, date_max>=2026-10-09
    if out["metrics"]["date_max"] < "2026-10-09":
        out["blockers"].append(f"date_max {out['metrics']['date_max']} < 2026-10-09")
    if out["metrics"]["asof_window_min_inst"] < 4500:
        out["blockers"].append(f"asof_window_min_inst {out['metrics']['asof_window_min_inst']}<4500")
    if out["metrics"].get("vs_asof_within_5pct") is not None and out["metrics"]["vs_asof_within_5pct"] < 0.85:
        out["blockers"].append(f"vs_asof_within_5pct {out['metrics']['vs_asof_within_5pct']}<0.85")
    # need enough history hint
    if out["metrics"]["date_min"] > "2024-01-01":
        out["blockers"].append(f"history shallow date_min={out['metrics']['date_min']} (want <=2024-01-01 for full hist; asof OK if window pass)")
        # soft: if asof window alone is good, don't fail solely on hist — but Leo asked full market daily
        # Keep as blocker for full promotion of long hist; allow partial flag
        out["partial_asof_window_ok"] = out["metrics"]["asof_window_min_inst"] >= 4500 and out["metrics"]["date_max"] >= "2026-10-09"
    if not out["blockers"]:
        out["pass"] = True
    return out

def check_daily_panels() -> dict:
    panels = V2 / "asof_extend_tushare_202610/panels"
    out = {"id": "daily_panels_asof_extend", "path": str(panels), "pass": False, "blockers": [], "metrics": {}}
    if not panels.exists():
        # fallback: raw extend coverage
        raw_days = sorted(p.stem for p in (RAW/"daily").glob("*.parquet"))
        out["metrics"]["raw_daily_days"] = len(raw_days)
        out["metrics"]["raw_daily_min"] = raw_days[0] if raw_days else None
        out["metrics"]["raw_daily_max"] = raw_days[-1] if raw_days else None
        out["blockers"].append("extend_panels not materialized yet")
        if len(raw_days) < 60:
            out["blockers"].append(f"raw daily days {len(raw_days)}<60")
        return out
    files = list(panels.glob("*.parquet"))
    out["metrics"]["n_panels"] = len(files)
    # sample 50 panels for field completeness
    sample = files[:: max(len(files)//50, 1)][:50]
    stats = {"amount_nn_frac": [], "limit_up_nn_frac": [], "tradestatus_ok": 0}
    for f in sample:
        x = pd.read_parquet(f)
        n = len(x) or 1
        stats["amount_nn_frac"].append(float(x.amount.notna().mean()) if "amount" in x.columns else 0.0)
        stats["limit_up_nn_frac"].append(float(x.limit_up.notna().mean()) if "limit_up" in x.columns else 0.0)
        if "tradestatus" in x.columns: stats["tradestatus_ok"] += 1
    out["metrics"]["sample_n"] = len(sample)
    out["metrics"]["amount_nn_frac_mean"] = round(float(np.mean(stats["amount_nn_frac"])), 4) if stats["amount_nn_frac"] else 0
    out["metrics"]["limit_up_nn_frac_mean"] = round(float(np.mean(stats["limit_up_nn_frac"])), 4) if stats["limit_up_nn_frac"] else 0
    out["metrics"]["tradestatus_panels"] = stats["tradestatus_ok"]
    if len(files) < 4500: out["blockers"].append(f"panels {len(files)}<4500")
    if out["metrics"]["amount_nn_frac_mean"] < 0.95: out["blockers"].append("amount fill <95%")
    if out["metrics"]["limit_up_nn_frac_mean"] < 0.90: out["blockers"].append("limit_up fill <90%")
    if not out["blockers"]:
        out["pass"] = True
    return out

def check_financials() -> dict:
    path = V2 / "financials_pit/financials_available_at_tushare.parquet"
    out = {"id": "financials_available_at", "path": str(path), "pass": False, "blockers": [], "metrics": {}}
    if not path.exists():
        out["blockers"].append("missing financials_available_at_tushare.parquet"); return out
    f = pd.read_parquet(path)
    out["metrics"]["rows"] = len(f)
    out["metrics"]["n_instruments"] = int(f.instrument_id.nunique())
    out["metrics"]["available_at_nulls"] = int(f.available_at.isna().sum())
    out["metrics"]["has_f_ann"] = bool("f_ann_date" in f.columns and f.f_ann_date.notna().any())
    # disclosure_date coverage if present
    disc_dir = RAW / "disclosure_date"
    if disc_dir.exists():
        out["metrics"]["disclosure_raw_files"] = len(list(disc_dir.glob("*.parquet")))
    if out["metrics"]["available_at_nulls"] > 0:
        out["blockers"].append(f"available_at nulls={out['metrics']['available_at_nulls']}")
    if out["metrics"]["n_instruments"] < 4000:
        out["blockers"].append(f"instruments {out['metrics']['n_instruments']}<4000")
    # Restatement chain: update_flag presence is weak evidence — require note
    if "update_flag" in f.columns:
        out["metrics"]["update_flag_nonzero"] = int((pd.to_numeric(f.update_flag, errors="coerce").fillna(0) != 0).sum())
    else:
        out["blockers"].append("no update_flag column — restatement chain weak")
    # Hard: without as-filed revision values, mark conditional
    out["metrics"]["restatement_policy"] = "available_at from f_ann_date||ann_date @18:00; no as-filed value chain"
    if not out["blockers"]:
        # still require explicit judgment: PIT timing OK for research-promotion if ann dates solid
        out["pass"] = True
        out["caveat"] = "PIT timing from ann/f_ann; not full as-filed revision ledger"
    return out

def check_dividend() -> dict:
    path = V2 / "corporate_actions/dividend_tushare.parquet"
    path_ex = V2 / "corporate_actions/dividend_by_exdate_tushare.parquet"
    out = {"id": "dividend_exrights", "path": str(path), "pass": False, "blockers": [], "metrics": {}}
    frames = []
    for p in (path, path_ex):
        if p.exists():
            frames.append(pd.read_parquet(p))
            out.setdefault("paths", []).append(str(p))
    if not frames:
        out["blockers"].append("no dividend_tushare tables"); return out
    d = pd.concat(frames, ignore_index=True)
    if "ts_code" in d.columns and "instrument_id" not in d.columns:
        d["instrument_id"] = to_iid(d.ts_code)
    out["metrics"]["rows"] = len(d)
    out["metrics"]["n_instruments"] = int(d.instrument_id.nunique()) if "instrument_id" in d.columns else 0
    # reconcile vs 1c85 actions
    act = ROOT / "data/local_market/1c85fd9aceaa03c3c4863bec/actions.parquet"
    if act.exists():
        a = pd.read_parquet(act)
        # try to find ex_date-like columns
        out["metrics"]["actions_cols"] = list(a.columns)[:20]
        out["metrics"]["actions_rows"] = len(a)
        # build keys
        ex_col = "ex_date" if "ex_date" in d.columns else None
        if ex_col and "instrument_id" in d.columns:
            d2 = d.dropna(subset=[ex_col]).copy()
            d2["ex_date"] = pd.to_datetime(d2[ex_col].astype(str), errors="coerce")
            d2 = d2[d2.ex_date >= "2024-01-01"]
            keys_ts = set(zip(d2.instrument_id, d2.ex_date.dt.strftime("%Y-%m-%d")))
            # 1c85 actions schema
            iid_col = "instrument_id" if "instrument_id" in a.columns else None
            # common: session or ex_date or effective_date
            for c in ("ex_date", "session", "effective_date", "action_date", "date"):
                if c in a.columns:
                    a2 = a.copy()
                    a2["_d"] = pd.to_datetime(a2[c].astype(str), errors="coerce")
                    a2 = a2[a2["_d"] >= pd.Timestamp("2024-01-01")]
                    if iid_col:
                        keys_a = set(zip(a2[iid_col], a2._d.dt.strftime("%Y-%m-%d")))
                        inter = keys_ts & keys_a
                        only_a = keys_a - keys_ts
                        only_ts = keys_ts - keys_a
                        out["metrics"]["reconcile_date_col"] = c
                        out["metrics"]["keys_tushare"] = len(keys_ts)
                        out["metrics"]["keys_1c85"] = len(keys_a)
                        out["metrics"]["intersection"] = len(inter)
                        out["metrics"]["only_1c85"] = len(only_a)
                        out["metrics"]["only_tushare"] = len(only_ts)
                        if keys_a:
                            out["metrics"]["explain_frac_1c85"] = round(1 - len(only_a)/len(keys_a), 4)
                        break
    if out["metrics"]["n_instruments"] < 2000:
        out["blockers"].append(f"dividend instruments {out['metrics']['n_instruments']}<2000")
    # Pass if we explain >=80% of 1c85 2024+ keys OR document residual
    ef = out["metrics"].get("explain_frac_1c85")
    if ef is not None and ef < 0.80:
        out["blockers"].append(f"1c85 explain_frac {ef}<0.80 (only_1c85={out['metrics'].get('only_1c85')})")
    if ef is None and not out["blockers"]:
        out["blockers"].append("could not reconcile keys vs 1c85 actions")
    if not out["blockers"]:
        out["pass"] = True
    return out

def update_manifests(results: list[dict]):
    by = {r["id"]: r for r in results}
    # SW
    if "sw_l1_pit_tushare" in by:
        r = by["sw_l1_pit_tushare"]
        man_path = V2 / "sw_l1_pit/manifest.json"
        man = json.loads(man_path.read_text()) if man_path.exists() else {}
        man["tushare_candidate"] = {
            "path": r["path"],
            "promotion_approved": bool(r["pass"]),
            "metrics": r["metrics"],
            "blockers": r["blockers"],
            "checked_at": NOW.isoformat(),
        }
        if r["pass"]:
            man["research_preferred"] = "industry_members_sw_l1_tushare.parquet"
            man["promotion_approved"] = True
            man["quality_label"] = "promotion_tushare_index_member_all"
            man["promotable"] = True
        else:
            # don't downgrade unrelated; keep global false if not pass
            man["promotion_approved"] = False
        jdump(man_path, man)
    # float
    if "float_mktcap_daily" in by:
        r = by["float_mktcap_daily"]
        man_path = V2 / "float_mktcap/manifest.json"
        man = json.loads(man_path.read_text()) if man_path.exists() else {}
        man["tushare_daily_path"] = r["path"]
        man["promotion_approved"] = bool(r["pass"])
        man["acceptance"] = {"metrics": r["metrics"], "blockers": r["blockers"], "checked_at": NOW.isoformat()}
        if r.get("partial_asof_window_ok"):
            man["partial_asof_window_ok"] = True
        jdump(man_path, man)
    # financials
    if "financials_available_at" in by:
        r = by["financials_available_at"]
        man_path = V2 / "financials_pit/manifest.json"
        man = json.loads(man_path.read_text()) if man_path.exists() else {}
        man["tushare_available_at"] = r["path"]
        man["promotion_approved"] = bool(r["pass"])
        man["acceptance"] = {"metrics": r["metrics"], "blockers": r["blockers"], "checked_at": NOW.isoformat(), "caveat": r.get("caveat")}
        jdump(man_path, man)
    # CA
    if "dividend_exrights" in by:
        r = by["dividend_exrights"]
        man_path = V2 / "corporate_actions/manifest.json"
        man = json.loads(man_path.read_text()) if man_path.exists() else {}
        man["dividend_tushare"] = r.get("paths") or [r["path"]]
        man["promotion_approved"] = bool(r["pass"])
        man["acceptance"] = {"metrics": r["metrics"], "blockers": r["blockers"], "checked_at": NOW.isoformat()}
        jdump(man_path, man)
    # panels
    if "daily_panels_asof_extend" in by:
        r = by["daily_panels_asof_extend"]
        man_path = V2 / "asof_extend_tushare_202610/manifest.json"
        man = {
            "path": r["path"],
            "promotion_approved": bool(r["pass"]),
            "acceptance": {"metrics": r["metrics"], "blockers": r["blockers"], "checked_at": NOW.isoformat()},
        }
        jdump(man_path, man)

def write_doc(results: list[dict]):
    lines = [
        f"# PROMOTION_ACCEPTANCE",
        f"",
        f"- checked_at: {NOW.isoformat()} (ET)",
        f"- rule: per-table promotion_approved reflects acceptance evidence only",
        f"- acceptance_gates: **{'ALL PASS' if all(r['pass'] for r in results) else 'FAIL / partial'}** (evidence only)",
        f"- promotion_approved_overall: **false** (Leo must flip; never auto-promote from gates)",
        f"",
    ]
    for r in results:
        lines.append(f"## {r['id']} — {'PASS' if r['pass'] else 'FAIL'}")
        lines.append(f"- path: `{r.get('path')}`")
        if r.get("caveat"):
            lines.append(f"- caveat: {r['caveat']}")
        lines.append(f"- metrics: `{json.dumps(r.get('metrics',{}), ensure_ascii=False)}`")
        if r["blockers"]:
            lines.append(f"- blockers:")
            for b in r["blockers"]:
                lines.append(f"  - {b}")
        else:
            lines.append(f"- blockers: (none)")
        lines.append("")
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(lines) + "\n")
    print("wrote", DOC)

def main():
    results = [
        check_sw(),
        check_float_mktcap(),
        check_daily_panels(),
        check_financials(),
        check_dividend(),
    ]
    update_manifests(results)
    write_doc(results)
    summary = {r["id"]: {"pass": r["pass"], "blockers": r["blockers"], "metrics": r["metrics"]} for r in results}
    outj = ROOT / "docs/v2/PROMOTION_ACCEPTANCE.json"
    jdump(outj, {"checked_at": NOW.isoformat(), "results": summary})
    print(json.dumps({k: v["pass"] for k,v in summary.items()}, ensure_ascii=False))
    return 0 if all(r["pass"] for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
