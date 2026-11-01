"""外盘冲击→次日 A 股申万一级行业事件研究。只用 2024-06 以后数据（封存窗口 2018→2024-05 不读）。
A 股收益：tushare daily close × adj_factor（后复权），mid_large 池（当日 session）等权行业收益。
外盘：Yahoo chart 日线。US 交易日 T 收盘(16:00 ET = 次日 04:00 CST) → 映射到第一个 >T 的 A 股交易日。
日经/KOSPI 与 A 股同时段交易，映射到 >T 的 A 股交易日（即「次日」），不是同日共振。
研究级，live=false，不下单、不改权重、禁 GP。"""
from __future__ import annotations
import argparse, json, resource, sys
from pathlib import Path
import pandas as pd, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_common as C

START_A = "20240603"   # 基准日；首个收益日 20240604
START_US = pd.Timestamp("2024-06-03")
R = C.ROOT

EVENTS = [  # (rule key, label, factor, op, threshold)
    ("nasdaq", "纳指≤-2%", "nasdaq", "le", -2.0), ("nasdaq3", "纳指≤-3%", "nasdaq", "le", -3.0),
    ("sox", "费半≤-2%", "sox", "le", -2.0), ("sox3", "费半≤-3%", "sox", "le", -3.0),
    ("kweb", "KWEB≤-3%", "kweb", "le", -3.0),
    ("us10y", "美债10Y≥+10bp", "us10y", "ge", 10.0), ("us10y7", "美债10Y≥+7bp", "us10y", "ge", 7.0),
    ("dxy", "美元≥+0.8%", "dxy", "ge", 0.8),
    ("n225", "日经≤-2%", "n225", "le", -2.0), ("kospi", "KOSPI≤-2%", "kospi", "le", -2.0),
]


def a_share_industry_returns():
    """逐日流式计算，控制 peak RSS（≤1.5GB）。"""
    import pyarrow.dataset as ds
    files = sorted(p for p in (R / "data/v2/tushare_raw/daily").glob("*.parquet") if p.stem >= START_A)
    adj = pd.read_parquet(R / "data/v2/adj/adj_factor_2023h2plus.parquet", filters=[("trade_date", ">=", START_A)])
    pass
    adj_by_day = {d: g.set_index("ts_code")["adj_factor"] for d, g in adj.groupby("trade_date")}
    del adj
    mlds = ds.dataset(R / "data/v2/universe/mid_large_members_pit.parquet")
    ml = mlds.to_table(columns=["session", "instrument_id"], filter=ds.field("session") >= "2024-06-04").to_pandas()
    ml_by_day = {d: set(g.instrument_id) for d, g in ml.groupby("session")}
    del ml
    sw = pd.read_parquet(R / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet", columns=["instrument_id", "ts_code", "l1_name", "in_date", "out_date"])
    C.verify_sha("sw_pit", R)  # r3 P3-4：读后复核
    prev_hfq, last_fac, rows, mrows = None, pd.Series(dtype=float), {}, {}
    for f in files:
        td = f.stem
        px = pd.read_parquet(f, columns=["ts_code", "close"]).set_index("ts_code")["close"]
        fac = adj_by_day.get(td)
        if fac is not None:
            last_fac = fac.combine_first(last_fac) if len(last_fac) else fac
        hfq = px * last_fac.reindex(px.index)
        if prev_hfq is not None:
            d = pd.Timestamp(td)
            ret = (hfq / prev_hfq.reindex(hfq.index) - 1).dropna().clip(-0.35, 0.35)
            mem = ml_by_day.get(str(d.date()), set())
            s = C.sw_members_asof(sw, d); s = s[s.instrument_id.isin(mem)].drop_duplicates("ts_code")
            s = s.assign(r=s.ts_code.map(ret)).dropna(subset=["r"])
            if len(s):
                rows[d] = s.groupby("l1_name").r.mean()
                mrows[d] = s.r.mean()
        prev_hfq = hfq
    ind = pd.DataFrame(rows).T.sort_index()
    mkt = pd.Series(mrows).sort_index()
    return ind, mkt


def us_changes():
    out = {}
    for k, m in C.MARKETS.items():
        if k == "hxc":
            continue
        s = C.yahoo_daily(m["sym"], "5y")
        s = s[s.index >= START_US - pd.Timedelta(days=7)]
        ch = s.diff() * 100 if m["kind"] == "bp" else s.pct_change() * 100
        out[k] = ch[ch.index >= START_US].dropna()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--allow-stale", action="store_true", help="sw_pit 过期时仍照跑（disclosure 写入回执）")
    fresh = C.require_fresh("sw_pit", allow_stale=ap.parse_args().allow_stale)
    ind, mkt = a_share_industry_returns()
    rel = ind.sub(mkt, axis=0)
    sess = ind.index
    us = us_changes()
    res, byrule = [], {}
    for key, label, fac, op, th in EVENTS:
        ch = us[fac]
        ev = ch[ch <= th] if op == "le" else ch[ch >= th]
        nxt = [sess[sess > d][0] for d in ev.index if (sess > d).any()]
        nxt = sorted(set(nxt))
        rules = C.SHOCK_RULES[fac]
        for name in ind.columns:
            r = ind.loc[nxt, name].dropna(); rr = rel.loc[nxt, name].dropna()
            exp = rules.get(name)
            row = {"event": label, "rule_key": key, "industry": name, "n": int(len(r)),
                   "mean_ret_pct": float(r.mean() * 100) if len(r) else None,
                   "mean_rel_pct": float(rr.mean() * 100) if len(rr) else None,
                   "pct_down": float((r < 0).mean()) if len(r) else None,
                   "base_pct_down": float((ind[name].dropna() < 0).mean()),
                   "rule_dir": exp}
            if exp is not None and len(r):
                row["hit_rate"] = float((np.sign(r) == exp).mean())
                row["rel_hit_rate"] = float((np.sign(rr) == exp).mean())
                if key == fac:  # 主阈值写入 by_rule，供 intel_run 降级使用
                    byrule[f"{fac}|{name}"] = {"rule": label, "n": row["n"], "hit_rate": row["hit_rate"],
                                               "rel_hit_rate": row["rel_hit_rate"], "mean_ret_pct": row["mean_ret_pct"]}
            res.append(row)
        mr = mkt.loc[nxt]
        res.append({"event": label, "rule_key": key, "industry": "_全市场(mid_large等权)", "n": int(len(mr)),
                    "mean_ret_pct": float(mr.mean() * 100) if len(mr) else None, "pct_down": float((mr < 0).mean()) if len(mr) else None,
                    "base_pct_down": float((mkt < 0).mean()), "rule_dir": -1 if fac not in ("us10y", "dxy") else None})
    df = pd.DataFrame(res)
    out = R / "output/intel"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "event_study_full.csv", index=False)
    meta = {"window_a_share": f"{sess.min().date()}→{sess.max().date()}", "a_sessions": int(len(sess)),
            "by_rule": byrule, "sw_pit_freshness": fresh, "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024}
    (out / "event_study_hitrate.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "by_rule"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
