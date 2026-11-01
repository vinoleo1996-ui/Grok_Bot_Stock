#!/usr/bin/env python3
"""Arch read-only probe: re-implements sd1_common.ResumeState (sha 28fbb15d) is_resume_day independently
(does NOT import Data modules). Reads tushare_raw daily/suspend_d/stock_basic/namechange and the frozen mask (young col,
first session only). Writes ONLY to argv[1] (out dir). Single process."""
import sys, os, glob, json, resource, random
from pathlib import Path
import pandas as pd
ROOT = Path("/workspace/QuantLab"); RAW = ROOT / "data/v2/tushare_raw"; OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
MASK = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
import pyarrow.parquet as pq, pyarrow.compute as pc
CUTOFF = pc.max(pq.read_table(MASK, columns=["date"]).column("date")).as_py().strftime("%Y%m%d")
days = sorted(p.stem for p in (RAW / "daily").glob("2*.parquet") if "20180102" <= p.stem <= CUTOFF)
m0 = pd.read_parquet(MASK, columns=["date", "instrument", "young"], filters=[("date", "==", pd.Timestamp(days[0]))])
seed = set(m0.instrument[~m0.young.astype(bool)]); del m0
# instrument format check: mask instrument vs ts_code
sample_inst = next(iter(seed)) if seed else None
def to_ts(i):
    if "." in i and i.split(".")[0].isalpha():   # e.g. sz.002445
        ex, n = i.split("."); return f"{n}.{ex.upper()}"
    return i
seed_ts = {to_ts(i) for i in seed}
prev_amt = set(); prev_present = set(); prev_vol = {}; prev_amtv = {}; has_traded = set(seed_ts); first = True
last_traded = {}; last_idx = {}
prev_S_any = set(); prev_S_full = set(); S_since_last = {}  # code -> count of S records on sessions since last traded
rows = []; prev_d = None
for i, d in enumerate(days):
    x = pd.read_parquet(RAW / f"daily/{d}.parquet", columns=["ts_code", "vol", "amount"]).drop_duplicates("ts_code").set_index("ts_code")
    vol_pos = set(x.index[x.vol > 0]); amt_pos = set(x.index[x.amount > 0]); present = set(x.index)
    sp = RAW / f"suspend_d/{d}.parquet"
    s = pd.read_parquet(sp, columns=["ts_code", "suspend_type", "suspend_timing"]) if sp.exists() else pd.DataFrame(columns=["ts_code", "suspend_type", "suspend_timing"])
    t = s.suspend_timing.astype("string").str.strip(); has_t = (s.suspend_timing.notna() & t.notna() & ~t.isin(["", "None", "nan"])).astype(bool)
    full = set(s.ts_code[(s.suspend_type == "S") & ~has_t]); intra = set(s.ts_code[(s.suspend_type == "S") & has_t]) - full
    Rr = set(s.ts_code[s.suspend_type == "R"]); S_any = set(s.ts_code[s.suspend_type == "S"])
    if first: res = set()
    else:
        cand = (vol_pos - full) & has_traded
        res = {c for c in cand if (c not in prev_amt) or (c in Rr)}
    for c in res:
        gap = i - last_idx[c] - 1 if c in last_idx else None
        rows.append(dict(ts_code=c, trade_date=d, prev_date=prev_d, R_today=c in Rr, intra_S_today=c in intra,
                         prev_row_present=c in prev_present, prev_vol=prev_vol.get(c), prev_amount=prev_amtv.get(c),
                         prev_S_any=c in prev_S_any, prev_S_full=c in prev_S_full, gap_sessions=gap,
                         last_traded=last_traded.get(c), S_records_in_gap=S_since_last.get(c, 0), seeded=c in seed_ts))
    # S counts since last traded
    for c in S_any: S_since_last[c] = S_since_last.get(c, 0) + 1
    for c in vol_pos:
        last_traded[c] = d; last_idx[c] = i; S_since_last[c] = 0
    has_traded |= vol_pos; prev_amt = amt_pos; prev_present = present
    prev_vol = x.vol.to_dict(); prev_amtv = x.amount.to_dict(); prev_S_any = S_any; prev_S_full = full; first = False; prev_d = d
F = pd.DataFrame(rows)
# listing date and ST from namechange
sb = pd.concat([pd.read_parquet(p, columns=["ts_code", "list_date", "delist_date", "name"]) for p in glob.glob(str(RAW / "stock_basic/*.parquet"))]).drop_duplicates("ts_code")
F = F.merge(sb[["ts_code", "list_date"]], on="ts_code", how="left")
nc = pd.concat([pd.read_parquet(p, columns=["ts_code", "name", "start_date", "end_date"]) for p in glob.glob(str(RAW / "namechange/*.parquet"))]).drop_duplicates()
st = nc[nc.name.str.contains("ST", na=False)].copy(); st["end_date"] = st.end_date.fillna("99991231").replace("", "99991231")
stg = st.groupby("ts_code")
def is_st(c, d):
    if c not in stg.groups: return False
    g = stg.get_group(c); return bool(((g.start_date <= d) & (g.end_date >= d)).any())
F["st_on_date"] = [is_st(c, d) for c, d in zip(F.ts_code, F.trade_date)]
F["year"] = F.trade_date.str[:4].astype(int)
def cls(r):
    if r.R_today: return "A_R_announced"
    if not r.prev_row_present:
        if r.prev_S_any: return "B_prev_missing_with_S_prev"      # whole-day halt documented by S on t-1
        if r.S_records_in_gap > 0: return "C_prev_missing_S_in_gap_not_prev"
        return "D_prev_missing_no_S_anywhere_in_gap"            # halt not in suspend_d
    if r.prev_amount is None or not (r.prev_amount > 0):
        return "E_prev_row_amount_le0" + ("_withS" if r.prev_S_any else "_noS")
    return "Z_other"
F["cls"] = F.apply(cls, axis=1)
F["gap_bucket"] = pd.cut(F.gap_sessions.fillna(-1), [-2, -0.5, 0.5, 1.5, 5.5, 20.5, 60.5, 1e9], labels=["none", "0", "1", "2-5", "6-20", "21-60", ">60"])
F.to_parquet("/tmp/arch_probe_resume_rows.parquet", index=False)
by = F.groupby("year").agg(is_resume_day=("ts_code", "size"), R=("R_today", "sum"))
noR = F[~F.R_today]
summary = {"cutoff": CUTOFF, "days_walked": len(days), "seed_n": len(seed_ts), "seed_inst_example": sample_inst,
           "by_year": by.to_dict("index"), "is_resume_day_without_R": int(len(noR)),
           "noR_cls_by_year": pd.crosstab(noR.year, noR.cls).to_dict("index"),
           "noR_gap_by_year": pd.crosstab(noR.year, noR.gap_bucket).to_dict("index"),
           "noR_st_by_year": pd.crosstab(noR.year, noR.st_on_date).to_dict("index"),
           "withR_gap_by_year": pd.crosstab(F[F.R_today].year, F[F.R_today].gap_bucket).to_dict("index"),
           "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}
(OUT / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
pool = noR[noR.year == 2018].sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
idx = sorted(random.Random(20261018).sample(range(len(pool)), min(50, len(pool))))
pool.iloc[idx].to_csv(OUT / "sample50_2018_noR.csv", index=False)
print(json.dumps(summary, ensure_ascii=False, default=str))
