#!/usr/bin/env python3
"""cs_panel_v2_resumefix (QuantLab Data, D-1; Arch review r2 P1-1..6, P2-2..8 applied).
Steps (serial, gated by Arch .ok, see sd1_common.SERIAL):
  --fixes none   -> D1a_fixesnone_check: v1 logic for 2018-2026, every year asserted DataFrame.equals(v1) AND
                    pa.Table.equals(v1 table); any miss/inequality -> non-zero exit, nothing written.
  --fixes resume -> D1b_resume_execute: v1 rows untouched (asserted per year: 0 missing, 0 changed) + restored rows.
Rulings (Arch r2 §4): hiliq/fulla keep v1 mask definition (restored rows: both False). Booking-only columns
(hiliq_carry, fulla_carry; use t-close info, NEVER for same-day selection or pool definition). is_resume_day = disclosure
and no-new-buy gate only (engine pre-open uses suspend_flags_v2.resume_announced, t 09:00).
Extra columns (D1b): is_resume_day, intraday_halt, hiliq_carry, fulla_carry, row_origin('v1'|'restored'),
restore_reason('resume'|'intraday_halt'|''), prev_traded_date, halt_sessions, build_version.
All modes require --arch-ok (dry-run needs allow_dryrun=true; --execute needs allow_full=true). Writes go to
<out>.staging_<ts>/ then rename; abort -> VOID file, no partials. RSS<=1.5GB, MemAvailable<2GB -> abort.
usage: build_cs_panel_v2_resumefix.py --arch-ok PATH --fixes none|resume [--execute]
live=false promotion_approved=false strategy_promotion=false"""
import sys, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
def _sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
sys.path.insert(0, str(HERE)); import sd1_common as C

A = sys.argv[1:]
FIX = A[A.index("--fixes") + 1] if "--fixes" in A and A.index("--fixes") + 1 < len(A) else None
if FIX not in ("none", "resume"): raise SystemExit("SD1 gate blocked: --fixes none|resume required")
STEP = "D1a_fixesnone_check" if FIX == "none" else "D1b_resume_execute"
if "--step" in A and A[A.index("--step") + 1] != STEP: raise SystemExit("SD1 gate blocked: --step does not match --fixes")
EXEC = "--execute" in A
DATA_KEYS = ["mask_sha256", "float_mktcap_sha256", "sw_l1_sha256"] + [f"v1_cs_panel_{y}_sha256" for y in C.YEARS]
KV, PINS, PREV_RECEIPT_SHA = C.gate(A, STEP, DATA_KEYS, EXEC)          # <- nothing above reads market data

import json, numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
R = C.ROOT; RAW = R / "data/v2/tushare_raw"; V1 = R / "output/ai_factory/panel_cache"
MASK = R / C.PIN_DATA["mask_sha256"]; VERSION = "cs_panel_v2_resumefix"
EXTRA = ["is_resume_day", "intraday_halt", "hiliq_carry", "fulla_carry", "row_origin", "restore_reason", "carry_state", "prev_traded_date", "halt_sessions", "build_version"]
def ts(x): m, c = x.split('.', 1); return f"{c}.{m.upper()}"
ST = C.Staging(STEP, EXEC)
try:
    man = {"step": STEP, "version": VERSION, "fixes": FIX, "mode": "execute" if EXEC else "dryrun", "ok_path": KV["_ok_path"],
           "ok_sha256": KV["_ok_sha256"], "pins": PINS, "prev_receipt_sha256": PREV_RECEIPT_SHA, "common_sha256": COMMON_SHA256,
           "live": False, "promotion_approved": False, "strategy_promotion": False, "years": {}}
    sw = pd.read_parquet(R / C.PIN_DATA["sw_l1_sha256"], columns=["instrument_id", "sw_name", "in_date", "out_date"])
    sw["inst"] = sw.instrument_id.map(ts); sw["in_date"] = pd.to_datetime(sw.in_date); sw["out_date"] = pd.to_datetime(sw.out_date).fillna(pd.Timestamp("2100-01-01"))
    INDS = sorted(sw.sw_name.unique()); IND_ID = {n: i for i, n in enumerate(INDS)}
    if EXEC:
        pd.Series(INDS).to_csv(ST.path("ind_names.csv"), index=False)
        man["ind_names_sha256"] = C.file_sha256(ST.path("ind_names.csv")); man["ind_names_v1_sha256"] = C.file_sha256(V1 / "ind_names.csv")
        if man["ind_names_sha256"] != man["ind_names_v1_sha256"]: ST.void("ind_names.csv differs from v1")
    raw_list = sorted(p.name for p in (RAW / "daily").glob("2*.parquet")) + sorted(p.name for p in (RAW / "suspend_d").glob("2*.parquet"))
    man["raw_file_list_sha256"] = hashlib.sha256("\n".join(raw_list).encode()).hexdigest()
    man["run_conditions"] = KV["_run_conditions"]
    CUTOFF = C.mask_last_date(); man["raw_content"] = C.raw_pin_start(STEP, CUTOFF, execute=EXEC)   # P2-1
    state = C.ResumeState(); FIRST_SESSION = None

    def resume_flags_year(y, mfull):
        """walk sessions of year y (state carried from previous years). returns sparse flag frame."""
        global FIRST_SESSION
        out = []
        for d, g in mfull.groupby("date", sort=True):
            d = pd.Timestamp(d); p = RAW / f"daily/{d:%Y%m%d}.parquet"; s = RAW / f"suspend_d/{d:%Y%m%d}.parquet"
            if not p.exists(): continue
            if FIRST_SESSION is None:
                FIRST_SESSION = d; state.seed_listed(g.instrument[~g.young.astype(bool)])
            x = pd.read_parquet(p, columns=["ts_code", "vol", "amount"])
            vol_pos = set(x.ts_code[x.vol > 0]); amt_pos = set(x.ts_code[x.amount > 0])
            full, intra, Rr = set(), set(), set()
            if s.exists():
                z = pd.read_parquet(s, columns=["ts_code", "suspend_type", "suspend_timing"])
                t = z.suspend_timing.astype("string").str.strip(); has_t = z.suspend_timing.notna() & t.notna() & ~t.isin(["", "None", "nan"])
                full = set(z.ts_code[(z.suspend_type == "S") & ~has_t]); intra = set(z.ts_code[(z.suspend_type == "S") & has_t]) - full
                Rr = set(z.ts_code[z.suspend_type == "R"])
            res, info = state.step(d, vol_pos, amt_pos, full, Rr)
            codes = g.instrument.to_numpy(); susp = g.suspended.astype(bool).to_numpy()
            hu = g.in_universe.astype(bool).to_numpy(); fv = g.fulla_v1.to_numpy(); keep1 = g.keep_v1.to_numpy()
            upd = []
            if state.sess_idx % 20 == 0: ST.guard(f"{d.date()}")
            for c, su, h, f, k in zip(codes, susp, hu, fv, keep1):
                tr = c in vol_pos; isr = c in res; ih = c in intra
                ptd, hs = info.get(c, (None, None)) if (isr or ih) else (None, None)
                try:
                    hc, fc, restore_reason, carry_state = C.classify_restore(y, c, su, tr, k, c in full, isr, ih, state.carry(c), ptd, state.seeded)
                except ValueError as e:
                    ST.void(f"invariant: {e} on {d.date()}")
                hs = -1 if hs is None else hs
                if isr or ih or restore_reason or carry_state:
                    out.append((d, c, isr, ih, hc, fc, restore_reason, carry_state, ptd, hs))
                if tr and not su: upd.append((c, h, f))
            state.update_pool(upd)
        f = pd.DataFrame(out, columns=["date", "instrument", "is_resume_day", "intraday_halt", "hiliq_carry", "fulla_carry", "restore_reason", "carry_state", "prev_traded_date", "halt_sessions"])
        f["prev_traded_date"] = pd.to_datetime(f.prev_traded_date)
        return f

    for y in C.YEARS:
        ST.guard(f"start {y}")
        v1p = V1 / f"cs_panel_{y}.parquet"
        if not v1p.exists(): ST.void(f"v1 file missing for {y}")
        m = pd.read_parquet(MASK, filters=[("date", ">=", pd.Timestamp(f"{y}-01-01")), ("date", "<=", pd.Timestamp(f"{y}-12-31"))])
        if not len(m): ST.void(f"mask empty for {y}")
        m["fulla"] = (~m.st.astype(bool)) & (~m.suspended.astype(bool)) & (~m.young.astype(bool)) & (m.adv20_yuan >= 3e6)
        keep_v1 = m.fulla | m.in_universe.astype(bool)
        if FIX == "resume":
            mf = m[["date", "instrument", "in_universe", "suspended", "young"]].assign(fulla_v1=m.fulla.to_numpy(), keep_v1=keep_v1.to_numpy())
            fl = resume_flags_year(y, mf); del mf
            m = m.merge(fl, on=["date", "instrument"], how="left")
            for c in ["is_resume_day", "intraday_halt", "hiliq_carry", "fulla_carry"]: m[c] = m[c].fillna(False).astype(bool)
            m["restore_reason"] = m.restore_reason.fillna(""); m["carry_state"] = m.carry_state.fillna("")
            unk = m[m.carry_state.str.startswith("unknown")]
            ev = np.where(unk.is_resume_day, "resume", "intraday_halt")
            unk_stats = {"unknown_rows": len(unk),
                         "unknown_by_event_x_label": {f"{e}|{l}": int(n) for (e, l), n in pd.Series(1, index=pd.MultiIndex.from_arrays([ev, unk.carry_state.to_numpy()])).groupby(level=[0, 1]).sum().items()},
                         "unknown_by_label": unk.carry_state.value_counts().to_dict(),
                         "unknown_sample": [f"{a} {b.date()} {l}" for a, b, l in zip(unk.instrument.head(5), unk.date.head(5), unk.carry_state.head(5))]}
            m["halt_sessions"] = m.halt_sessions.fillna(-1).astype("int32")
            restored = (~keep_v1.to_numpy()) & (m.hiliq_carry | m.fulla_carry).to_numpy()
            m["row_origin"] = np.where(restored, "restored", "v1")
            m.loc[~restored, "restore_reason"] = ""; m.loc[~restored & (m.carry_state == "known").to_numpy(), "carry_state"] = ""
            keep = keep_v1.to_numpy() | restored
            cols = ["date", "instrument", "in_universe", "fulla", "adv20_yuan"] + [c for c in EXTRA if c != "build_version"]
        else:
            keep = keep_v1.to_numpy(); cols = ["date", "instrument", "in_universe", "fulla", "adv20_yuan"]
        stats_pre = {}
        if FIX == "resume":
            stats_pre = {"resume_events_all_mask_rows": int(m.is_resume_day.sum()),
                         "true_resume_eligible_2865_basis": int((m.is_resume_day & ~m.st.astype(bool) & ~m.young.astype(bool) & (m.adv20_yuan >= 3e6)).sum()),
                         "intraday_halt_rows_all": int(m.intraday_halt.sum()), **unk_stats}
        m = m[keep][cols].rename(columns={"in_universe": "hiliq"})
        mc = pq.read_table(R / C.PIN_DATA["float_mktcap_sha256"], columns=["instrument_id", "trade_date", "float_mktcap"], filters=[("trade_date", ">=", pd.Timestamp(f"{y}-01-01")), ("trade_date", "<=", pd.Timestamp(f"{y}-12-31 23:59"))]).to_pandas()
        mc["instrument"] = mc.instrument_id.map(lambda x: ts(x) if x[:2] in ("sh", "sz", "bj") else x); mc["date"] = pd.to_datetime(mc.trade_date).dt.normalize()
        m = m.merge(mc[["date", "instrument", "float_mktcap"]], on=["date", "instrument"], how="left"); del mc
        rows = []
        for d in sorted(m.date.unique()):
            p = R / f"data/v2/tushare_raw/daily/{pd.Timestamp(d):%Y%m%d}.parquet"
            if p.exists():
                x = pd.read_parquet(p, columns=["ts_code", "open", "close", "pre_close"]); x["date"] = pd.Timestamp(d); rows.append(x)
        px = pd.concat(rows); px["ret"] = px.close / px.pre_close - 1; px["ret_on"] = px.open / px.pre_close - 1
        m = m.merge(px.rename(columns={"ts_code": "instrument"})[["date", "instrument", "ret", "ret_on", "close"]], on=["date", "instrument"], how="left")
        s = sw[(sw.in_date <= pd.Timestamp(f"{y}-12-31")) & (sw.out_date >= pd.Timestamp(f"{y}-01-01"))]
        mm = m[["date", "instrument"]].merge(s[["inst", "sw_name", "in_date", "out_date"]], left_on="instrument", right_on="inst", how="left")
        mm = mm[(mm.date >= mm.in_date) & (mm.date < mm.out_date)].drop_duplicates(["date", "instrument"], keep="last")
        m = m.merge(mm[["date", "instrument", "sw_name"]], on=["date", "instrument"], how="left")
        m["ind"] = m.sw_name.map(IND_ID).fillna(-1).astype("int16"); m["logmv"] = np.log(m.float_mktcap.clip(lower=1)).astype("float32")
        m = m.drop(columns=["sw_name", "float_mktcap"])
        for c in ["ret", "ret_on", "close", "adv20_yuan"]: m[c] = m[c].astype("float32")
        V1COLS = ["date", "instrument", "hiliq", "fulla", "adv20_yuan", "ret", "ret_on", "close", "ind", "logmv"]
        v1 = pd.read_parquet(v1p); st = {"rows_v1": len(v1), **stats_pre}
        if FIX == "none":
            m = m.reset_index(drop=True)
            fe = bool(m.equals(v1)); te = bool(pa.Table.from_pandas(m, preserve_index=False).equals(pq.read_table(v1p)))
            st.update(rows=len(m), v1_frame_equals=fe, v1_table_equals=te)
            if not (fe and te): ST.void(f"{y}: fixes=none output != v1 (frame_equals={fe}, table_equals={te})")
        else:
            m = m[V1COLS + [c for c in EXTRA if c != "build_version"]]; m["build_version"] = VERSION
            m = m.reset_index(drop=True)
            j = v1.merge(m[V1COLS], on=["date", "instrument"], how="left", suffixes=("", "_v2"), indicator=True)
            miss = int((j._merge != "both").sum())
            mism = int(sum((~((j[c] == j[c + "_v2"]) | (j[c].isna() & j[c + "_v2"].isna()))).sum() for c in V1COLS[2:]))
            r = m[m.row_origin == "restored"]
            st.update(rows=len(m), rows_added=len(m) - len(v1), v1_rows_missing_in_v2=miss, v1_value_mismatch=mism,
                      restored=len(r), restored_by_reason=r.restore_reason.value_counts().to_dict(),
                      restored_hiliq_carry=int(r.hiliq_carry.sum()), restored_fulla_carry=int(r.fulla_carry.sum()),
                      restored_hiliq_or_fulla_true=int((r.hiliq | r.fulla).sum()))
            if miss or mism: ST.void(f"{y}: v1 rows missing={miss} changed={mism}")
            if st["restored_hiliq_or_fulla_true"]: ST.void(f"{y}: restored rows must have hiliq=fulla=False")
            if len(m) != len(v1) + len(r): ST.void(f"{y}: row count identity failed")
        st["rss_mb"] = round(C.rss_mb())
        if EXEC:
            fp = ST.path(f"cs_panel_{y}.parquet"); m.to_parquet(fp, index=False); st["sha256"] = C.file_sha256(fp); st["v1_sha256"] = C.file_sha256(v1p)
            if FIX == "none":
                st["bytes_equal"] = st["sha256"] == st["v1_sha256"]
                if not st["bytes_equal"]:
                    a, b = pq.ParquetFile(fp).metadata, pq.ParquetFile(v1p).metadata
                    st["parquet_meta_diff"] = {"created_by": [a.created_by, b.created_by], "num_rows": [a.num_rows, b.num_rows],
                        "schema_equal": a.schema.equals(b.schema), "kv_meta_equal": (a.metadata == b.metadata)}
        print(y, json.dumps(st, ensure_ascii=False, default=str), flush=True)
        man["years"][str(y)] = st; del m, v1, px, rows
        ST.guard(f"end {y}")
    man["sessions_walked"] = state.sess_idx + 1   # Arch r4 P3-3: must equal D2 days
    man["status"] = "PASS"; man["first_session_forced_no_resume"] = str(FIRST_SESSION.date()) if FIRST_SESSION is not None else None
    if C.raw_content_sha256(CUTOFF) != man["raw_content"]: ST.void("raw daily/suspend_d content changed during the run (P2-1)")
    if EXEC:
        ST.path("manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        rec = {k: man[k] for k in ("step", "ok_sha256", "pins", "status", "prev_receipt_sha256", "raw_content", "run_conditions")}
        rec["manifest_sha256"] = C.file_sha256(ST.path("manifest.json")); rec["year_sha256"] = {y: v.get("sha256") for y, v in man["years"].items()}
        ST.path(f"RECEIPT_{STEP}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        ST.commit(); print("COMMITTED", C.out_path(STEP))
    else:
        print("DRY-RUN PASS: nothing written")

except SystemExit: raise
except BaseException as e:   # P2-2: any exception after staging exists -> VOID
    ST.void(f"exception: {type(e).__name__}: {e}")
