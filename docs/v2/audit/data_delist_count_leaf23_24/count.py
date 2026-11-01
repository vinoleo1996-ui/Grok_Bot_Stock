# QuantLab Data read-only delisting metadata count (leaf 23/24 .ok prep). No project code imported. No writes outside /tmp.
import hashlib, os, datetime, resource
import pandas as pd
R = "/workspace/QuantLab/"
X2S, X2E = pd.Timestamp("2024-06-03"), pd.Timestamp("2026-10-09")  # ARCH_AI_LEAF23_24_FIX5_FIX6_REVIEW_ZH.md:136; research/g1g5_sue_desens_cs_alpha.py:90
F = {"master": "data/v2/delisted/delisted_master_tushare.parquet",
     "sb": "data/v2/meta/stock_basic_incl_delisted.parquet",
     "ref": "data/v2/ref/stock_delisted.parquet"}
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
print("start_et", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
for k, p in F.items():
    st = os.stat(R + p)
    print(f"input {k}: {p} sha256={sha(R+p)} mtime_et={datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')} size={st.st_size}")
inwin = lambda s: s.notna() & (s >= X2S) & (s <= X2E)
m = pd.read_parquet(R + F["master"]); sb = pd.read_parquet(R + F["sb"]); rf = pd.read_parquet(R + F["ref"])
print("\n== master rows", len(m), "unique ts_code", m.ts_code.nunique(), "list_status counts", m.list_status.value_counts(dropna=False).to_dict())
# (b) duplicates
for name, df in (("master", m), ("stock_basic", sb), ("ref_stock_delisted", rf)):
    d = df[df.ts_code.duplicated(keep=False)]
    print(f"(b) {name}: duplicated ts_code count={d.ts_code.nunique()} rows={len(d)} codes={sorted(d.ts_code.unique())}")
    for c, g in d.groupby("ts_code"):
        diff = [col for col in g.columns if g[col].astype(str).nunique() > 1]
        print("   ", c, "differing fields:", {col: g[col].astype(str).tolist() for col in diff})
# also instrument_id dups / symbol dups in master
print("(b') master duplicated symbol:", sorted(m[m.symbol.duplicated(keep=False)].ts_code), " duplicated instrument_id:", sorted(m[m.instrument_id.duplicated(keep=False)].ts_code))
# (a) missing delist_date
print("\n(a) master null delist_date:", m.delist_date.isna().sum(), sorted(m[m.delist_date.isna()].ts_code))
print("(a) master null last_trade_date:", m.last_trade_date.isna().sum(), m[m.last_trade_date.isna()][["ts_code","delist_date","list_status"]].to_dict("records"))
sbD = sb[sb.list_status == "D"]
print("(a) stock_basic list_status=D rows", len(sbD), "null delist_date:", sbD.delist_date.isna().sum(), sorted(sbD[sbD.delist_date.isna()].ts_code))
sbL = sb[sb.list_status != "D"]
print("(a) stock_basic non-D with delist_date set:", sbL.delist_date.notna().sum(), sorted(sbL[sbL.delist_date.notna()].ts_code))
rfdd = pd.to_datetime(rf.delist_date, format="%Y%m%d", errors="coerce")
print("(a) ref stock_delisted null/unparseable delist_date:", rfdd.isna().sum(), sorted(rf[rfdd.isna()].ts_code))
# names whose last_trade_date in X2 but delist_date missing or outside X2
lt_in = inwin(m.last_trade_date); dd_in = inwin(m.delist_date)
print("(a) master last_trade_date in X2 & delist_date null:", sorted(m[lt_in & m.delist_date.isna()].ts_code))
print("(a) master last_trade_date in X2 & delist_date after X2E:", m[lt_in & (m.delist_date > X2E)][["ts_code","last_trade_date","delist_date"]].astype(str).to_dict("records"))
print("(a) master last_trade_date before X2S & delist_date in X2:", m[(m.last_trade_date < X2S) & dd_in][["ts_code","last_trade_date","delist_date"]].astype(str).to_dict("records"))
# set coverage master vs stock_basic D vs ref
sm, sd, sr = set(m.ts_code), set(sbD.ts_code), set(rf.ts_code)
print("(a) codes in stock_basic D not in master:", sorted(sd - sm), " in master not in stock_basic D:", sorted(sm - sd), " master^ref:", sorted(sm ^ sr))
# 3. totals
w = m[dd_in]
gap = (w.delist_date - w.last_trade_date).dt.days
print("\n(3) master delist_date in X2 [2024-06-03, 2026-10-09]: names", w.ts_code.nunique(), "rows", len(w))
print("(3) of which (delist_date - last_trade_date) > 1 calendar day:", int((gap > 1).sum()), " >=1:", int((gap >= 1).sum()), " null gap:", int(gap.isna().sum()),
      " median gap days", float(gap[gap > 1].median()), " max", float(gap.max()))
print("(3) of which gap_days_last_trade_to_delist column > 1:", int((w.gap_days_last_trade_to_delist > 1).sum()))
print("(3) by delist_date year:", w.delist_date.dt.year.value_counts().sort_index().to_dict())
print("(3) by exchange:", w.exchange.value_counts().to_dict(), " by reason:", w.delist_reason_category.value_counts(dropna=False).to_dict())
print("(3) last_trade_date in X2 names:", int(lt_in.sum()), "; union(dd or lt in X2):", int((lt_in | dd_in).sum()))
print("(3) stock_basic D delist_date in X2:", int(inwin(sbD.delist_date).sum()), "; ref delist_date in X2:", int(inwin(rfdd).sum()))
print("(3) master max delist_date", m.delist_date.max().date(), "max last_trade_date", m.last_trade_date.max().date(), "; names delisted after X2E:", sorted(m[m.delist_date > X2E].ts_code))
print("(3) X2 list:", ";".join(f"{r.ts_code}|ltd={r.last_trade_date.date() if pd.notna(r.last_trade_date) else None}|dd={r.delist_date.date()}" for r in w.sort_values("delist_date").itertuples()))
print("\nmaxrss_mb", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, "end_et", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
