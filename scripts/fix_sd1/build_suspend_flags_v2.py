#!/usr/bin/env python3
"""suspend_flags_v2 (QuantLab Data, D-2; Arch r2 P1-1, P1-5, P1-6, P2-2/3/4/8 applied). Step D2_suspend_flags.
Sparse halt/resume flag table for the SD1 engine; does NOT touch asof/D0 panels or tier1 bars.
Date span 2018-01-02 .. mask last session (cutoff recorded; later raw days listed as excluded).
Rows: every (ts_code, trade_date) with a suspend_d record, plus every is_resume_day row (shared definition
sd1_common.ResumeState: same function as cs_panel_v2_resumefix; IPO first day / never-traded / first data session excluded; seeded with mask young=False at the first session;
prev-session bar on amount>0, same basis as mask bar_prev; intraday S with prev bar and no R is not a resume).
r6 (Arch probe 9b81bff1, P2-A/P3): "daily row missing => halted" holds ONLY for SH/SZ. .BJ codes (BSE / NEEQ, incl. pre-listing
NEEQ period) have no-trade days with no daily row and no S; a .BJ is_resume_day requires an R record on t or a full-day S on the
previous session; a missing prior row alone is not a resume. Applied as a filter here only (sd1_common.ResumeState unchanged, so
D1b/cs_panel are unaffected; the mask holds 0 .BJ codes). Universe: all A shares (research scope), not limited to the mask.
resume_evidence: 'R' (R on t) | 'S_prev' (full-day S on previous session) | 'gap_S' (full-day S somewhere since last trade) | 'none'.
Join key (instrument_id, trade_date); instrument_id like 'sz.002445'; absent row => normal trading day.
Columns (available_at Asia/Shanghai):
  suspend_type_raw, suspend_timing         t 09:00   source suspend_d (published pre-open)
  halted_fullday   S & empty timing         t 09:00   engine: block buy & sell
  intraday_halt, intraday_halt_timing      t 09:00   engine: block open fill only if window covers 09:30
  resume_announced R record                 t 09:00   source suspend_d R; engine pre-open no-new-buy gate
  is_resume_day                             t 16:00   needs vol(t); disclosure only
  vol, amount, traded                       t 16:00   source daily
  prev_traded_date, halt_sessions           t 16:00
  tradestatus_v2   0 iff halted_fullday & not traded   t 16:00 (accounting)
  tier1_v1_tradestatus, conflict_v1        reconciliation with tier1_materialize rule
  available_at_open, available_at_close, build_version, promotion_approved
Gate: --arch-ok required in all modes; predecessor receipt D1b required. Staging -> rename; abort -> VOID.
usage: build_suspend_flags_v2.py --arch-ok PATH [--execute]     live=false promotion_approved=false"""
import sys, hashlib
from pathlib import Path
HERE = Path(__file__).resolve().parent
COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
def _sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
sys.path.insert(0, str(HERE)); import sd1_common as C
A = sys.argv[1:]; STEP = "D2_suspend_flags"; EXEC = "--execute" in A
KV, PINS, PREV = C.gate(A, STEP, ["mask_sha256"], EXEC)                     # <- nothing above reads market data

import json, pandas as pd
R = C.ROOT; RAW = R / "data/v2/tushare_raw"
ST = C.Staging(STEP, EXEC)
try:
    def iid(c): n, ex = c.split("."); return f"{ex.lower()}.{n}"
    CUTOFF = C.mask_last_date()          # P2-3: truncate to the mask's last session (same span as D1)
    days = sorted(p.stem for p in (RAW / "daily").glob("2*.parquet") if "20180102" <= p.stem <= CUTOFF)
    excluded_after_cutoff = sorted(p.stem for p in (RAW / "daily").glob("2*.parquet") if p.stem > CUTOFF)
    RAWC = C.raw_pin_start(STEP, CUTOFF, execute=EXEC)  # P2-1
    raw_list = [f"{d}.parquet" for d in days] + sorted(p.name for p in (RAW / "suspend_d").glob("2*.parquet"))
    state = C.ResumeState(); out = []
    prev_full = set(); s_since_trade = set(); bj_dropped = 0   # r6 P2-A / P3 evidence tracking
    m0 = pd.read_parquet(R / C.PIN_DATA["mask_sha256"], columns=["date", "instrument", "young"], filters=[("date", "==", pd.Timestamp(days[0]))])
    state.seed_listed(m0.instrument[~m0.young.astype(bool)]); del m0
    for i, d in enumerate(days):
        if i % 20 == 0: ST.guard(d)
        x = pd.read_parquet(RAW / f"daily/{d}.parquet", columns=["ts_code", "vol", "amount"]).drop_duplicates("ts_code").set_index("ts_code")
        vol_pos = set(x.index[x.vol > 0]); amt_pos = set(x.index[x.amount > 0])
        sp = RAW / f"suspend_d/{d}.parquet"
        s = pd.read_parquet(sp, columns=["ts_code", "suspend_type", "suspend_timing"]) if sp.exists() else pd.DataFrame(columns=["ts_code", "suspend_type", "suspend_timing"])
        t = s.suspend_timing.astype("string").str.strip(); s["has_t"] = (s.suspend_timing.notna() & t.notna() & ~t.isin(["", "None", "nan"])).astype(bool)
        full = set(s.ts_code[(s.suspend_type == "S") & ~s.has_t]); intra = set(s.ts_code[(s.suspend_type == "S") & s.has_t]) - full
        Rr = set(s.ts_code[s.suspend_type == "R"])
        res, info = state.step(d, vol_pos, amt_pos, full, Rr)
        def evid(c):
            return "R" if c in Rr else ("S_prev" if c in prev_full else ("gap_S" if c in s_since_trade else "none"))
        bj_drop = {c for c in res if c.endswith(".BJ") and not (c in Rr or c in prev_full)}   # r6 P2-A
        bj_dropped += len(bj_drop); res = res - bj_drop
        g = s.groupby("ts_code").agg(suspend_type_raw=("suspend_type", lambda v: "|".join(sorted(set(v)))),
                                     suspend_timing=("suspend_timing", lambda v: "|".join(sorted({str(i) for i in v if pd.notna(i) and str(i).strip() not in ("", "None", "nan")}))))
        for c in sorted(set(g.index) | res):
            vol = x.vol.get(c); amt = x.amount.get(c); tr = bool(vol is not None and vol > 0)
            hf = c in full; ih = c in intra; ra = c in Rr; isr = c in res
            ptd, hs = info.get(c, (None, None)) if isr else (None, None)
            ev = evid(c) if isr else ""
            styp = g.suspend_type_raw.get(c) if c in g.index else None
            out.append((iid(c), c, d, styp, g.suspend_timing.get(c, "") if c in g.index else "", hf, ih, g.suspend_timing.get(c, "") if ih else "",
                        ra, isr, vol, amt, tr, ptd, -1 if hs is None else hs, 0 if (hf and not tr) else 1, 0 if styp else 1, ev))
        s_since_trade = (s_since_trade | full) - vol_pos; prev_full = full
    F = pd.DataFrame(out, columns=["instrument_id", "ts_code", "trade_date", "suspend_type_raw", "suspend_timing", "halted_fullday", "intraday_halt",
                                   "intraday_halt_timing", "resume_announced", "is_resume_day", "vol", "amount", "traded", "prev_traded_date",
                                   "halt_sessions", "tradestatus_v2", "tier1_v1_tradestatus", "resume_evidence"])
    F["trade_date"] = pd.to_datetime(F.trade_date); F["prev_traded_date"] = pd.to_datetime(F.prev_traded_date)
    for c in ["tradestatus_v2", "tier1_v1_tradestatus"]: F[c] = F[c].astype("int8")
    F["halt_sessions"] = F.halt_sessions.astype("int32")
    F["conflict_v1"] = (F.tier1_v1_tradestatus == 0) & F.traded
    F["available_at_open"] = (F.trade_date + pd.Timedelta(hours=9)).dt.tz_localize("Asia/Shanghai")
    F["available_at_close"] = (F.trade_date + pd.Timedelta(hours=16)).dt.tz_localize("Asia/Shanghai")
    F["build_version"] = "suspend_flags_v2"; F["promotion_approved"] = False
    F = F.sort_values(["trade_date", "instrument_id"]).reset_index(drop=True)
    if F.duplicated(["instrument_id", "trade_date"]).any(): ST.void("duplicate join keys")
    F["y"] = F.trade_date.dt.year
    by = F.groupby("y").agg(rows=("ts_code", "size"), halted_fullday=("halted_fullday", "sum"), intraday_halt=("intraday_halt", "sum"),
                            resume_announced=("resume_announced", "sum"), is_resume_day=("is_resume_day", "sum"), conflict_v1=("conflict_v1", "sum"))
    F = F.drop(columns="y")
    st = {"rows": len(F), "by_year": {int(k): {kk: int(vv) for kk, vv in v.items()} for k, v in by.iterrows()},
          "conflict_v1_by_class": F[F.conflict_v1].assign(k=lambda z: z.suspend_type_raw.fillna("none") + "/" + z.intraday_halt.map({True: "intra", False: "nointra"})).k.value_counts().to_dict(),
          "fullday_but_traded": int((F.halted_fullday & F.traded).sum()),
          "is_resume_day_without_R": int((F.is_resume_day & ~F.resume_announced).sum()), "R_without_resume": int((F.resume_announced & ~F.is_resume_day).sum()),
          "first_session_forced_no_resume": days[0], "rss_mb": round(C.rss_mb())}
    # r6 P2-B / P3 disclosure (stdout + manifest.stats)
    nb = F[~F.ts_code.str.endswith(".BJ")]; bj = F[F.ts_code.str.endswith(".BJ")]
    nbr = nb[nb.is_resume_day]; nbr_noR = nbr[~nbr.resume_announced]
    st["table_rows"] = len(F); st["table_rows_expected_approx"] = 111480
    st["nonbj_is_resume_day_by_year"] = {int(k): int(v) for k, v in nbr.trade_date.dt.year.value_counts().sort_index().items()}
    st["nonbj_without_R"] = len(nbr_noR)
    st["nonbj_without_R_rows"] = [f"{r.ts_code} {r.trade_date:%Y-%m-%d} ev={r.resume_evidence} prev={'' if pd.isna(r.prev_traded_date) else f'{r.prev_traded_date:%Y-%m-%d}'} gap={r.halt_sessions}" for r in nbr_noR.itertuples()]
    st["bj_resume_rows_kept"] = [f"{r.ts_code} {r.trade_date:%Y-%m-%d} ev={r.resume_evidence}" for r in bj[bj.is_resume_day].itertuples()]
    st["bj_resume_dropped_missing_row_only"] = bj_dropped
    st["resume_evidence_counts"] = {k: int(v) for k, v in F.loc[F.is_resume_day, "resume_evidence"].value_counts().items()}
    EXP_NONBJ = {2018: 1286, 2019: 563, 2020: 542, 2021: 518, 2022: 455, 2023: 304, 2024: 318, 2025: 559, 2026: 441}   # Arch independent repro
    EXP_NONBJ_NO_R = 35
    print(json.dumps(st, ensure_ascii=False, default=str), flush=True); ST.guard("end")
    if st["nonbj_is_resume_day_by_year"] != EXP_NONBJ: ST.void(f"non-BJ is_resume_day by year {st['nonbj_is_resume_day_by_year']} != Arch expected {EXP_NONBJ}")
    if st["nonbj_without_R"] != EXP_NONBJ_NO_R: ST.void(f"non-BJ is_resume_day without R = {st['nonbj_without_R']} != {EXP_NONBJ_NO_R}")
    man = {"step": STEP, "version": "suspend_flags_v2", "mode": "execute" if EXEC else "dryrun", "ok_path": KV["_ok_path"], "ok_sha256": KV["_ok_sha256"],
           "pins": PINS, "prev_receipt_sha256": PREV, "common_sha256": COMMON_SHA256, "join_key": ["instrument_id", "trade_date"],
           "raw_file_list_sha256": hashlib.sha256("\n".join(raw_list).encode()).hexdigest(), "raw_content": RAWC, "cutoff_date": CUTOFF,
           "excluded_after_cutoff": excluded_after_cutoff, "days_walked": len(days), "run_conditions": KV["_run_conditions"], "stats": st, "status": "PASS",
           "live": False, "promotion_approved": False}
    if C.raw_content_sha256(CUTOFF) != RAWC: ST.void("raw daily/suspend_d content changed during the run (P2-1)")
    if EXEC:
        fp = ST.path("suspend_flags_v2.parquet"); F.to_parquet(fp, index=False); man["sha256"] = C.file_sha256(fp)
        ST.path("manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        rec = {k: man[k] for k in ("step", "ok_sha256", "pins", "status", "prev_receipt_sha256", "sha256", "raw_content", "cutoff_date", "run_conditions")}; rec["manifest_sha256"] = C.file_sha256(ST.path("manifest.json"))
        ST.path(f"RECEIPT_{STEP}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        ST.commit(); print("COMMITTED", C.out_path(STEP))
    else: print("DRY-RUN PASS: nothing written")
except SystemExit: raise
except BaseException as e:   # P2-2: any exception after staging exists -> VOID
    ST.void(f"exception: {type(e).__name__}: {e}")
