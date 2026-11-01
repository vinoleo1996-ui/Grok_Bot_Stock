import glob, json, unicodedata, sys
import pandas as pd
sys.path.insert(0, "research")
from all_a_universe_mask import universe_mask, open_sessions
b = pd.concat(pd.read_parquet(f) for f in sorted(glob.glob("data/v2/tushare_raw/broker_recommend/*.parquet")))
b["broker"] = b.broker.astype(str).map(lambda s: unicodedata.normalize("NFKC", s).strip())
b = b.drop_duplicates(["month", "broker", "ts_code"])
months = sorted(b.month.unique())
sess = open_sessions()
top = pd.read_parquet("data/v2/universe/mid_large_top300_monthly_pit.parquet")
top = top[top.in_top300]; top["av"] = pd.to_datetime(top.available_at).dt.tz_localize(None)
EXCL = {"600519.SH", "002371.SZ"}
def conv(x): return x.split(".")[1] + "." + x.split(".")[0].upper()
rows = []
for i, m in enumerate(months[1:], 1):
    pm = months[i - 1]
    if int(m) != int(pd.Period(pm, "M").__add__(1).strftime("%Y%m")): pass
    cur = b[b.month == m]; prev = b[b.month == pm]
    prev_b = set(prev.broker)
    pset = set(zip(prev.broker, prev.ts_code))
    new = cur[cur.broker.isin(prev_b) & ~pd.Series(list(zip(cur.broker, cur.ts_code)), index=cur.index).isin(pset)]
    c = new.groupby("ts_code").broker.nunique()
    ev = set(c[c >= 2].index) - EXCL
    ms = sess[(sess.year == int(m[:4])) & (sess.month == int(m[4:]))]
    if len(ms) < 3: continue
    T2 = ms[2]
    if not (pd.Timestamp("2024-01-02") <= T2 <= pd.Timestamp("2026-10-09")): continue
    snap = top[top.av <= T2 + pd.Timedelta(hours=9)]
    ml = {conv(x) for x in snap[snap.month == snap.month.max()].instrument_id}
    ua = universe_mask(T2); aa = set(ua.index[ua.in_all_a])
    rows.append(dict(month=m, T2=str(T2.date()), raw=len(ev), mid_large=sorted(ev & ml), all_a=sorted(ev & aa),
                     n_ml_univ=len(ml), n_alla_univ=len(aa)))
out = {}
for k in ("mid_large", "all_a"):
    n = [len(r[k]) for r in rows]; st = set().union(*[set(r[k]) for r in rows])
    yr = {}
    for r in rows: yr[r["month"][:4]] = yr.get(r["month"][:4], 0) + len(r[k])
    out[k] = dict(months=len(rows), events=sum(n), distinct_stocks=len(st), monthly_mean=sum(n)/len(rows),
                  by_year=yr, zero_months=sum(x == 0 for x in n), gate_pass=len(st) >= 50 and sum(n)/len(rows) >= 5)
out["raw_events"] = sum(r["raw"] for r in rows)
out["per_month"] = [{k: (len(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows]
json.dump(out, open("output/ai_factory/broker_gold_new_count_20261014.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_month"}, ensure_ascii=False))
for r in out["per_month"]: print(r)
