#!/usr/bin/env python3
"""stock_delisted_v2 (QuantLab Data, D-3/D-4; Arch r2 P1-1, P1-4, P1-6, P2-7, P2-8, P3-3 applied). Step D3D4_stock_delisted.
Derived from frozen data/v2/ref/stock_delisted.parquet (read-only) + namechange_all + delisted_daily. v1 columns unchanged,
new columns appended. Join key ts_code (instrument_id also present). All new columns are ex-post (available_at = delist_date)
except delist_period_ann_date, which is the PIT time a forced-sell trigger may use.
New columns:
  delist_period_start / delist_period_ann_date  first namechange record named '*退' or '退市*' (start_date / ann_date);
                         fixes D-4 (v1 only matched names ending with '退'); MANUAL_OVERRIDE only with a verified source.
  delist_period_end, delist_period_days         last_trade_date; #delisted_daily vol>0 days in [start,end]
  entered_delisting_period_v2, delist_period_source ('namechange'|'manual_override'|''), delist_period_pit_usable
  face_value_delist_flag, face_value_last20_max_close   20 traded closes BEFORE delist_period_start (or last 20 if no
                         period) all < 1.00 (P3-3)
  delist_reason_category_v2   v1 category; v1 merger/privatisation class & face value -> '强制退市(面值退市)';
                         remaining merger/privatisation class without announcement source -> 'UNKNOWN(缺公告来源)'
  needs_manual_source    True for UNKNOWN (P1-4) (and for any unverified override)
  sd1_delist_type_default  FORCED | UNKNOWN (UNKNOWN is treated as FORCED by SD1); MERGER_SWAP / CASH_OUT only after an
                         announcement source (no., date, URL) is recorded -> none in this version
  sd1_forced_recovery_default (0.0), sd1_recovery_sensitivity ('0.0,0.3,0.7')
  override_source_verified, source_ann_no, source_url, source_published_date
Gate: --arch-ok required in all modes; predecessor receipt D2 required; target files must not exist; staging -> rename.
usage: build_stock_delisted_v2.py --arch-ok PATH [--execute]     live=false promotion_approved=false"""
import sys, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
def _sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
sys.path.insert(0, str(HERE)); import sd1_common as C
A = sys.argv[1:]; STEP = "D3D4_stock_delisted"; EXEC = "--execute" in A
KV, PINS, PREV = C.gate(A, STEP, ["stock_delisted_v1_sha256", "namechange_all_sha256", "delisted_daily_sha256"], EXEC)  # <- no data read above
EXPECT = C.parse_d3d4_expectations(KV, EXEC)   # r6b: execute without both keys -> blocked here, before any data read
DIAG_FACE4 = ["000861.SZ", "002505.SZ", "002509.SZ", "600297.SH"]   # diagnosis (last-20-closes rule), DATA_SUSPEND_RESUME_DELIST_DIAG_ZH D-3

import json, pandas as pd
R = C.ROOT
MERGER = "疑似主动/吸收合并/私有化退市(退市前非ST)"
# Verified by QuantLab Data 2026-10-18 ET: announcement text read via WebFetch of the SZSE PDF (curl timed out from box).
MANUAL_OVERRIDE = {"002509.SZ": dict(delist_period_start="20200604", delist_period_ann_date="20200527", override_source_verified=True,
    source_ann_no="天广中茂 2020-053《关于公司股票终止上市的公告》; 深证上【2020】442号",
    source_url="http://disc.static.szse.cn/download/disc/disk02/finalpage/2020-05-28/9f3e0d5c-66cd-4ab0-b727-ed74438ea31a.PDF",
    source_published_date="20200528",
    note="SZSE decided termination 2020-05-27; 2020-04-09..05-11 20 consecutive closes < 1 CNY (rule 14.4.1(18)); delisting period from 2020-06-04. namechange lacks the '退' record.")}
ST = C.Staging(STEP, EXEC)
try:
    x = pd.read_parquet(R / C.PIN_DATA["stock_delisted_v1_sha256"]); n0 = len(x); v1cols = list(x.columns)
    nc = pd.read_parquet(R / C.PIN_DATA["namechange_all_sha256"], columns=["ts_code", "name", "start_date", "ann_date"])
    dd = pd.read_parquet(R / C.PIN_DATA["delisted_daily_sha256"], columns=["ts_code", "trade_date", "close", "vol"])
    dd["d"] = dd.trade_date.astype(str).str.replace("-", "").str[:8]; dd = dd[dd.vol > 0].sort_values(["ts_code", "d"])
    norm = lambda s: s.astype(str).str.replace("-", "").str[:8]
    pat = nc.name.str.endswith("退", na=False) | nc.name.str.startswith("退市", na=False)
    first = nc[pat].assign(s=lambda z: norm(z.start_date), a=lambda z: norm(z.ann_date)).sort_values("s").groupby("ts_code").first()
    x["delist_period_start"] = x.ts_code.map(first.s); x["delist_period_ann_date"] = x.ts_code.map(first.a)
    x["delist_period_source"] = x.delist_period_start.notna().map({True: "namechange", False: ""})
    for c in ["override_source_verified"]: x[c] = False
    for c in ["source_ann_no", "source_url", "source_published_date"]: x[c] = ""
    for c, o in MANUAL_OVERRIDE.items():
        k = (x.ts_code == c) & x.delist_period_start.isna()
        x.loc[k, "delist_period_start"] = o["delist_period_start"]; x.loc[k, "delist_period_ann_date"] = o["delist_period_ann_date"]
        x.loc[k, "delist_period_source"] = "manual_override"
        for f in ["override_source_verified", "source_ann_no", "source_url", "source_published_date"]: x.loc[k, f] = o[f]   # r6c P2-2: only on the overridden row(s)
    x["delist_period_end"] = pd.to_datetime(x.last_trade_date).dt.strftime("%Y%m%d")
    g = {k: v for k, v in dd.groupby("ts_code")}
    def ndays(r):
        z = g.get(r.ts_code)
        if z is None or not isinstance(r.delist_period_start, str): return 0
        return int(((z.d >= r.delist_period_start) & (z.d <= str(r.delist_period_end))).sum())
    x["delist_period_days"] = x.apply(ndays, axis=1).astype("int32")
    x["entered_delisting_period_v2"] = x.delist_period_days > 0
    x["delist_period_pit_usable"] = x.entered_delisting_period_v2 & ((x.delist_period_source == "namechange") | x.override_source_verified.astype(bool))
    def fv(r):
        z = g.get(r.ts_code)
        if z is None: return (False, float("nan"))
        if isinstance(r.delist_period_start, str): z = z[z.d < r.delist_period_start]
        t = z.tail(20)
        return (len(t) >= 20 and bool((t.close < 1.0).all()), float(t.close.max()) if len(t) else float("nan"))
    f = x.apply(fv, axis=1, result_type="expand"); x["face_value_delist_flag"] = f[0].astype(bool); x["face_value_last20_max_close"] = f[1].astype("float32")
    cat = x.delist_reason_category.copy()
    cat[(x.delist_reason_category == MERGER) & x.face_value_delist_flag] = "强制退市(面值退市)"
    cat[(cat == MERGER)] = "UNKNOWN(缺公告来源)"
    x["delist_reason_category_v2"] = cat
    x["needs_manual_source"] = (cat == "UNKNOWN(缺公告来源)") | ((x.delist_period_source == "manual_override") & ~x.override_source_verified.astype(bool))
    x["sd1_delist_type_default"] = cat.map(lambda c: "UNKNOWN" if c.startswith("UNKNOWN") else "FORCED")
    x["sd1_forced_recovery_default"] = 0.0; x["sd1_recovery_sensitivity"] = "0.0,0.3,0.7"
    x["build_version"] = "stock_delisted_v2"; x["promotion_approved"] = False
    if len(x) != n0 or list(x.columns[:len(v1cols)]) != v1cols: ST.void("v1 rows/columns not preserved")
    v1 = pd.read_parquet(R / C.PIN_DATA["stock_delisted_v1_sha256"])
    if not x[v1cols].equals(v1): ST.void("v1 columns changed")
    st = {"rows": len(x), "rows_v1": n0, "v1_columns_equal": True,
          "d4_v1_period_class_zero_days": int(((x.delist_reason_category.str.contains("整理期")) & (x.delisting_period_trade_days == 0)).sum()),
          "d4_v2_period_class_zero_days": int(((x.delist_reason_category.str.contains("整理期")) & (x.delist_period_days == 0)).sum()),
          "entered_v1": int(x.entered_delisting_period.sum()), "entered_v2": int(x.entered_delisting_period_v2.sum()),
          "face_value_flag": int(x.face_value_delist_flag.sum()),
          "recategorised": x.loc[x.delist_reason_category != x.delist_reason_category_v2].groupby("delist_reason_category_v2").ts_code.apply(list).to_dict(),
          "unknown_needs_source": x.loc[x.sd1_delist_type_default == "UNKNOWN", "ts_code"].tolist(),
          "manual_override": MANUAL_OVERRIDE, "rss_mb": round(C.rss_mb())}
    # r6 (Arch execute acceptance): full code lists for 89->151 split and face-value check, recorded in manifest.stats
    zero_fixed = (x.delist_reason_category.str.contains("整理期")) & (x.delisting_period_trade_days == 0) & (x.delist_period_days > 0)
    newly = x.entered_delisting_period_v2 & ~x.entered_delisting_period.astype(bool)
    lost = ~x.entered_delisting_period_v2 & x.entered_delisting_period.astype(bool)
    st["d4_zero_day_fixed_codes"] = sorted(x.loc[zero_fixed, "ts_code"].tolist())
    st["entered_newly_codes_other"] = sorted(x.loc[newly & ~zero_fixed, "ts_code"].tolist())
    st["entered_lost_codes"] = sorted(x.loc[lost, "ts_code"].tolist())
    st["face_value_recategorised_codes"] = sorted(x.loc[x.delist_reason_category_v2 == "强制退市(面值退市)", "ts_code"].tolist())
    st["face_value_expected_present"] = {c: c in set(st["face_value_recategorised_codes"]) for c in ("600297.SH", "002505.SZ", "000861.SZ", "002509.SZ")}
    LISTS = ("recategorised", "unknown_needs_source", "manual_override", "d4_zero_day_fixed_codes", "entered_newly_codes_other", "entered_lost_codes", "face_value_recategorised_codes")
    st["counts"] = {"recategorised": {kk: len(vv) for kk, vv in st["recategorised"].items()}, "unknown_needs_source": len(st["unknown_needs_source"]),
                    "manual_override": len(MANUAL_OVERRIDE), "d4_zero_day_fixed": len(st["d4_zero_day_fixed_codes"]),
                    "entered_newly_other": len(st["entered_newly_codes_other"]), "entered_lost": len(st["entered_lost_codes"])}
    # r6 Arch P2-1: dry-run prints counts AND full code lists (no "..."); manifest.stats carries the same
    print(json.dumps(st, ensure_ascii=False, default=str), flush=True)
    # r6 expectation asserts -> VOID. Only the statically certain one is enforced; face-value set / UNKNOWN==56 pending Arch (see report)
    # r6b disclosure: measured face set vs diagnosis 4 (both directions) + 20-close window per code; UNKNOWN vs 56
    face = st["face_value_recategorised_codes"]
    st["face_minus_diag4"] = sorted(set(face) - set(DIAG_FACE4)); st["diag4_minus_face"] = sorted(set(DIAG_FACE4) - set(face))
    def window(c):
        z = g.get(c); r = x.loc[x.ts_code == c]
        if z is None or r.empty: return {"code": c, "window": None}
        r = r.iloc[0]; zz = z[z.d < r.delist_period_start] if isinstance(r.delist_period_start, str) else z
        t = zz.tail(20)
        return {"code": c, "v1_cat": r.delist_reason_category, "v2_cat": r.delist_reason_category_v2, "period_start": r.delist_period_start if isinstance(r.delist_period_start, str) else None,
                "n_closes": len(t), "win_start": str(t.d.iloc[0]) if len(t) else None, "win_end": str(t.d.iloc[-1]) if len(t) else None,
                "win_max_close": float(t.close.max()) if len(t) else None, "face_flag": bool(r.face_value_delist_flag)}
    st["face_windows"] = [window(c) for c in sorted(set(DIAG_FACE4) | set(st["face_minus_diag4"]))]
    st["unknown_vs_56"] = {"measured": len(st["unknown_needs_source"]), "diag": 56, "diff": len(st["unknown_needs_source"]) - 56}
    st["expect_from_ok"] = EXPECT
    print("D3D4_FACE_CHECK " + json.dumps({k: st[k] for k in ("face_value_recategorised_codes", "face_minus_diag4", "diag4_minus_face", "face_windows", "unknown_vs_56", "expect_from_ok")}, ensure_ascii=False, default=str), flush=True)
    if EXPECT["face"] is not None and sorted(set(face)) != EXPECT["face"]: ST.void(f"face-value recategorised {sorted(set(face))} != .ok expected {EXPECT['face']}")
    if EXPECT["unknown_count"] is not None and len(st["unknown_needs_source"]) != EXPECT["unknown_count"]:
        ST.void(f"unknown_needs_source {len(st['unknown_needs_source'])} != .ok expected {EXPECT['unknown_count']}")
    # r6c Arch P2-2: assert on actual output rows (was a constant check, always true)
    mo_err = C.check_manual_override(zip(x.ts_code, x.delist_period_source, x.delist_period_start, x.source_ann_no, x.override_source_verified), {"002509.SZ": "20200604"})
    if mo_err: ST.void("manual_override row check failed: " + "; ".join(mo_err))
    ST.guard("end")
    man = {"step": STEP, "version": "stock_delisted_v2", "mode": "execute" if EXEC else "dryrun", "ok_path": KV["_ok_path"], "ok_sha256": KV["_ok_sha256"],
           "pins": PINS, "prev_receipt_sha256": PREV, "common_sha256": COMMON_SHA256, "join_key": "ts_code", "run_conditions": KV["_run_conditions"], "stats": st, "status": "PASS",
           "live": False, "promotion_approved": False}
    if EXEC:
        fin = C.out_path(STEP)
        x.to_parquet(ST.path("stock_delisted_v2.parquet"), index=False); man["sha256"] = C.file_sha256(ST.path("stock_delisted_v2.parquet"))
        ST.path("manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        rec = {k: man[k] for k in ("step", "ok_sha256", "pins", "status", "prev_receipt_sha256", "sha256", "run_conditions")}; rec["manifest_sha256"] = C.file_sha256(ST.path("manifest.json"))
        ST.path("receipt.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        ST.commit([("stock_delisted_v2.parquet", fin), ("manifest.json", fin.with_name(fin.name + ".manifest.json")), ("receipt.json", C.receipt_path(STEP))])
        print("COMMITTED", fin)
    else: print("DRY-RUN PASS: nothing written")
except SystemExit: raise
except BaseException as e:   # P2-2
    ST.void(f"exception: {type(e).__name__}: {e}")
