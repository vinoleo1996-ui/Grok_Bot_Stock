#!/usr/bin/env python3
"""Read-only SW L1 look-ahead count (Strategy, 2026-10-18; Arch request). pandas only, no project imports.
Writes ONLY to the --out directory (under /tmp). Compares, per (code, session) key in X2 = 2024-06-03..2026-10-09:
  legacy  = hx2 load_industry_map logic verbatim on BAD (sort_values("in_date").groupby("ts_code").tail(1); out_date ignored)
  pit_bad / pit_clean = pure as-of rule in_date < d AND (out_date null OR out_date >= d) on BAD / CLEAN;
    >1 active row -> fixed tie order (latest in_date -> is_new Y -> out_date null -> later file row), counted as overlap.
Gap carry is NOT applied (pure rule, as requested)."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
BAD = ROOT / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"
CLEAN = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
CAL = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"
DB = ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet"
LEGS = {k: ROOT / "output/strategy_hiliq/legs" / v for k, v in {
    "capacity_adv": "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
    "earnings_event": "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
    "insider_increase": "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet"}.items()}
BOOKS = {k: ROOT / f"output/strategy_hiliq/b4/B4_50_25_25_topN_{k}.parquet" for k in ("60w", "100w")}
X2 = ("2024-06-03", "2026-10-09")
PIN = {"BAD": "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6",
       "CLEAN": "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def is_etf(s): return s.astype(str).str.split(".").str[0].str[:2].isin(["51", "56", "58", "15"])


def prep(df, code, name):
    t = pd.DataFrame({"_code": df[code].astype(str).values, "l1": df[name].astype(str).values,
                      "in_date": pd.to_datetime(df["in_date"], errors="coerce").dt.normalize().values,
                      "out_date": pd.to_datetime(df["out_date"], errors="coerce").dt.normalize().values})
    isnew = df["is_new"].astype(str).str.upper().eq("Y").values
    t["_pri"] = 2 * isnew.astype(int) + t["out_date"].isna().astype(int)
    t["_ord"] = np.arange(len(t))
    return t


def pit(t, keys):
    """keys: DataFrame _code, _d, _rid. Returns (Series l1 per _rid or None, n_cand per _rid, active rows)."""
    m = keys.merge(t, on="_code", how="inner")
    m = m[(m["in_date"] < m["_d"]) & (m["out_date"].isna() | (m["out_date"] >= m["_d"]))]
    ncand = m.groupby("_rid").size()
    pick = m.sort_values(["_rid", "in_date", "_pri", "_ord"]).drop_duplicates("_rid", keep="last")
    out = pd.Series(None, index=keys["_rid"], dtype=object)
    out.loc[pick["_rid"].values] = pick["l1"].values
    return out, ncand.reindex(keys["_rid"]).fillna(0).astype(int), m


def compare(keys, ref, new, tag_ref, tag_new, w=None):
    r, n = ref.values, new.values
    rk, nk = pd.notna(r), pd.notna(n)
    both = rk & nk
    diff_known = both & (r != n)
    unk_new = rk & ~nk
    neq_cap = pd.Series(r).fillna("_UNK_").values != pd.Series(n).fillna("_UNK_").values  # what apply_ind_cap sees
    N = len(keys)
    codes = keys["_code"].values
    o = {"ref": tag_ref, "new": tag_new, "n_keys": int(N), "n_codes": int(pd.unique(codes).size),
         "diff_both_known_keys": int(diff_known.sum()), "diff_both_known_codes": int(pd.unique(codes[diff_known]).size),
         "diff_both_known_share_keys": float(diff_known.mean()) if N else None,
         "new_unknown_ref_known_keys": int(unk_new.sum()),
         "new_unknown_ref_known_codes": int(pd.unique(codes[unk_new]).size),
         "new_unknown_keys": int((~nk).sum()), "new_unknown_codes": int(pd.unique(codes[~nk]).size),
         "new_unknown_share_keys": float((~nk).mean()) if N else None,
         "ref_unknown_keys": int((~rk).sum()), "ref_unknown_codes": int(pd.unique(codes[~rk]).size),
         "ref_unknown_new_known_keys": int((~rk & nk).sum()),
         "ref_unknown_new_known_codes": int(pd.unique(codes[~rk & nk]).size),
         "neq_incl_unknown_keys": int(neq_cap.sum()), "neq_incl_unknown_codes": int(pd.unique(codes[neq_cap]).size),
         "neq_incl_unknown_share_keys": float(neq_cap.mean()) if N else None}
    if w is not None:
        ww = w.values.astype(float)
        o["diff_both_known_share_weight"] = float(ww[diff_known].sum() / ww.sum())
        o["neq_incl_unknown_share_weight"] = float(ww[neq_cap].sum() / ww.sum())
        o["new_unknown_share_weight"] = float(ww[~nk].sum() / ww.sum())
    return o, diff_known, unk_new


def overlap(keys, ncand, m, tag):
    rid = ncand.index[ncand.values > 1]
    mm = m[m["_rid"].isin(rid)]
    conf = mm.groupby("_code")["l1"].nunique()
    days = mm.groupby("_code")["_d"].agg(["min", "max", "nunique"])
    lst = [{"code": c, "first_day": str(days.loc[c, "min"].date()), "last_day": str(days.loc[c, "max"].date()),
            "n_days": int(days.loc[c, "nunique"]), "conflict": bool(conf.loc[c] > 1),
            "candidates": sorted(set(mm.loc[mm["_code"] == c, "l1"]))} for c in sorted(conf.index)]
    return {"table": tag, "overlap_keys": int(len(rid)), "overlap_codes": int(len(conf)),
            "overlap_codes_conflict": int((conf > 1).sum()), "codes": lst}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    out = Path(a.out); assert str(out.resolve()).startswith("/tmp/"), "output must be under /tmp"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in [BAD, CLEAN, CAL, *LEGS.values(), *BOOKS.values()]}
    assert inputs[str(BAD.relative_to(ROOT))] == PIN["BAD"] and inputs[str(CLEAN.relative_to(ROOT))] == PIN["CLEAN"]
    res = {"started_et": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "inputs_sha256": inputs, "pandas": pd.__version__,
           "window": list(X2)}
    # tables
    badraw = pd.read_parquet(BAD)
    cleanraw = pd.read_parquet(CLEAN)
    # legacy verbatim (hx2 load_industry_map, minus sw_pit_ensure_checked)
    ind = pd.read_parquet(BAD, columns=["ts_code", "l1_name", "in_date", "out_date"])
    ind["in_date"] = pd.to_datetime(ind["in_date"], errors="coerce")
    last = ind.sort_values("in_date").groupby("ts_code").tail(1)
    legacy = dict(zip(last["ts_code"], last["l1_name"]))
    tb = prep(badraw, "ts_code", "l1_name")
    iid = cleanraw["instrument_id"].astype(str)
    ok = iid.str.match(r"^(sz|sh|bj)\.\d{6}$")
    cleanraw["ts_code"] = np.where(ok, iid.str[3:] + "." + iid.str[:2].str.upper(), iid)  # sz.000001 -> 000001.SZ
    res["clean_adapter"] = {"code": "instrument_id sz.000001 -> ts_code 000001.SZ", "name": "sw_name -> l1_name",
                            "n_rows": int(len(cleanraw)), "n_instrument_id_malformed": int((~ok).sum()),
                            "malformed": sorted(iid[~ok].unique().tolist())}
    tc = prep(cleanraw, "ts_code", "sw_name")
    # calendar
    cal = pd.read_parquet(CAL, columns=["cal_date", "is_open"])
    od = pd.to_datetime(cal.loc[cal["is_open"] == 1, "cal_date"].astype(str), format="%Y%m%d").sort_values()
    x2days = od[(od >= X2[0]) & (od <= X2[1])]
    # scopes
    legs = {}
    for k, p in LEGS.items():
        d = pd.read_parquet(p, columns=["session", "instrument", "weight"])
        d["session"] = d["session"].astype(str).str[:10]
        legs[k] = d[d["weight"] > 0]
    common = set.intersection(*[set(d["session"]) for d in legs.values()])
    L = pd.concat([d[["instrument", "session"]] for d in legs.values()])
    L = L[~is_etf(L["instrument"]) & L["session"].isin(common) & (L["session"] >= X2[0]) & (L["session"] <= X2[1])]
    books = {}
    for k, p in BOOKS.items():
        d = pd.read_parquet(p, columns=["session", "instrument", "weight"])
        d["session"] = d["session"].astype(str).str[:10]
        books[k] = d[(d["weight"] > 0) & ~is_etf(d["instrument"]) & (d["session"] >= X2[0]) & (d["session"] <= X2[1])]
    B = pd.concat([d[["instrument", "session"]] for d in books.values()])
    synth = pd.concat([L, B]).drop_duplicates()
    db = pd.read_parquet(DB, columns=["ts_code", "trade_date"],
                         filters=[("trade_date", ">=", pd.Timestamp(X2[0])), ("trade_date", "<=", pd.Timestamp(X2[1]))])
    db = db[~is_etf(db["ts_code"])]
    mkt = pd.DataFrame({"instrument": db["ts_code"].astype(str).values,
                        "session": db["trade_date"].dt.strftime("%Y-%m-%d").values}).drop_duplicates()
    res["market_scope_note"] = "daily_basic_full_tushare 当日有记录的代码（停牌日无记录不计）；非 ETF"
    res["inputs_sha256"][str(DB.relative_to(ROOT))] = sha(DB)
    scopes = {"synth_legs_plus_b4": (synth, None), "b4_book_60w": (books["60w"], "weight"),
              "b4_book_100w": (books["100w"], "weight"), "market_daily_basic": (mkt, None)}
    res["scopes"] = {}
    mismatch_rows = []
    for name, (df, wcol) in scopes.items():
        keys = pd.DataFrame({"_code": df["instrument"].astype(str).values,
                             "_d": pd.to_datetime(df["session"]).dt.normalize().values})
        keys["_rid"] = np.arange(len(keys))
        nonopen = int((~keys["_d"].isin(set(od))).sum())
        ref = pd.Series(keys["_code"].map(legacy).values, index=keys["_rid"])
        pb, ncb, mb = pit(tb, keys)
        pc, ncc, mc = pit(tc, keys)
        w = df[wcol].reset_index(drop=True) if wcol else None
        c1, dk1, un1 = compare(keys, ref, pb, "legacy_BAD", "pit_BAD", w)
        c2, dk2, un2 = compare(keys, ref, pc, "legacy_BAD", "pit_CLEAN", w)
        c3, dk3, _ = compare(keys, pb, pc, "pit_BAD", "pit_CLEAN", w)
        c3["diff_both_known_code_list"] = sorted(pd.unique(keys["_code"].values[dk3]).tolist())[:50]
        res["scopes"][name] = {"n_keys": int(len(keys)), "n_codes": int(keys["_code"].nunique()),
                               "n_sessions": int(keys["_d"].nunique()), "n_keys_not_open_day": nonopen,
                               "legacy_unknown_keys": int(ref.isna().sum()),
                               "legacy_BAD_vs_pit_BAD": c1, "legacy_BAD_vs_pit_CLEAN": c2, "pit_BAD_vs_pit_CLEAN": c3,
                               "overlap_BAD": overlap(keys, ncb, mb, "BAD"), "overlap_CLEAN": overlap(keys, ncc, mc, "CLEAN")}
        if name == "synth_legs_plus_b4":
            for lab, dk, un, nw in (("pit_BAD", dk1, un1, pb), ("pit_CLEAN", dk2, un2, pc)):
                sel = dk | un
                mismatch_rows.append(pd.DataFrame({"compare": f"legacy_BAD_vs_{lab}", "code": keys["_code"].values[sel],
                                                   "session": keys["_d"].dt.strftime("%Y-%m-%d").values[sel],
                                                   "legacy": ref.values[sel], "pit": nw.values[sel],
                                                   "kind": np.where(dk[sel], "diff_both_known", "pit_unknown")}))
        print(name, "done", round(time.time() - t0, 1), flush=True)
    pd.concat(mismatch_rows).to_csv(out / "synth_mismatch_rows.csv", index=False)
    # 18 vs 12: BAD overlaps over ALL table codes, per open day
    days = od[(od >= X2[0]) & (od <= "2026-10-16")]
    allk = pd.MultiIndex.from_product([tb["_code"].unique(), days], names=["_code", "_d"]).to_frame(index=False)
    allk["_rid"] = np.arange(len(allk))
    _, nca, ma = pit(tb, allk)
    allk["n"] = nca.values
    ov = allk[allk["n"] > 1]
    listed = set(zip(mkt["instrument"], pd.to_datetime(mkt["session"])))
    ov_l = ov[[(c, d) in listed for c, d in zip(ov["_code"], ov["_d"])]]
    per_day = ov.groupby("_d")["_code"].nunique()
    open_end = badraw[badraw["out_date"].isna()].groupby("ts_code").size()
    res["overlap_18_vs_12"] = {
        "bad_all_codes_overlap_any_day_x2": int(ov[ov["_d"] <= X2[1]]["_code"].nunique()),
        "bad_all_codes_overlap_any_day_x2_listed_daily_basic": int(ov_l["_code"].nunique()),
        "bad_codes_overlap_any_day_0924_1016": int(ov[ov["_d"] >= "2026-09-24"]["_code"].nunique()),
        "bad_codes_overlap_every_day_0924_1016": int((ov[ov["_d"] >= "2026-09-24"].groupby("_code")["_d"].nunique()
                                                      == int(((days >= "2026-09-24")).sum())).sum()),
        "bad_codes_two_open_rows_out_null": int((open_end > 1).sum()),
        "per_day_overlap_codes_min_max_x2": [int(per_day[per_day.index <= X2[1]].min()), int(per_day[per_day.index <= X2[1]].max())],
        "per_day_overlap_codes_0924_1016": {str(k.date()): int(v) for k, v in per_day[per_day.index >= "2026-09-24"].items()},
        "codes_any_day_x2": overlap(allk[["_code", "_d", "_rid"]], nca, ma, "BAD_all")["codes"]}
    res["elapsed_sec"] = round(time.time() - t0, 1)
    res["finished_et"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    print("WROTE", out / "result.json")


if __name__ == "__main__":
    main()
