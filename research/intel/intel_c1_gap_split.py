"""C1 纳指≤-2% 次日科技链：拆 收盘→开盘(隔夜) / 开盘→收盘(日内)，扣成本判断可交易性。
研究级，live=false，不开叶，不下单。只用 2024-06 以后数据。逐日流式，RSS<1.5GB。
成本口径取 quantlab/config.py：佣金 2.5bp/边、印花税 5bp(卖出)、滑点 30bp/边(保守)；另给 10bp/边敏感性。
60万/100万两档：持仓 20–30 只、单票约 2–5 万，佣金按 max(2.5bp, 5元/笔) 计。"""
from __future__ import annotations
import argparse, json, resource, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_common as C, intel_event_study as S
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
R = C.ROOT; OUT = R / "output/intel/pit_candidates"
INDS = ["通信", "计算机", "传媒", "电子"]

def legs(with_cc=False):
    files = sorted(p for p in (R / "data/v2/tushare_raw/daily").glob("*.parquet") if p.stem >= S.START_A)
    adj = pd.read_parquet(R / "data/v2/adj/adj_factor_2023h2plus.parquet", filters=[("trade_date", ">=", S.START_A)])
    adj_by = {d: g.set_index("ts_code")["adj_factor"] for d, g in adj.groupby("trade_date")}; del adj
    import pyarrow.dataset as ds
    ml = ds.dataset(R / "data/v2/universe/mid_large_members_pit.parquet").to_table(columns=["session", "instrument_id"], filter=ds.field("session") >= "2024-06-04").to_pandas()
    ml_by = {d: set(g.instrument_id) for d, g in ml.groupby("session")}; del ml
    sw = pd.read_parquet(R / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet", columns=["instrument_id", "ts_code", "l1_name", "in_date", "out_date"])
    C.verify_sha("sw_pit", R)  # r3 P3-4：读后复核
    prev_c, fac, on, idy, cc = None, pd.Series(dtype=float), {}, {}, {}
    for f in files:
        px = pd.read_parquet(f, columns=["ts_code", "open", "close"]).set_index("ts_code")
        a = adj_by.get(f.stem)
        if a is not None: fac = a.combine_first(fac) if len(fac) else a
        fa = fac.reindex(px.index); o, c = px.open * fa, px.close * fa
        if prev_c is not None:
            d = pd.Timestamp(f.stem); mem = ml_by.get(str(d.date()), set())
            s = C.sw_members_asof(sw, d); s = s[s.instrument_id.isin(mem)].drop_duplicates("ts_code")
            r_on = (o / prev_c.reindex(o.index) - 1).clip(-.35, .35); r_id = (c / o - 1).clip(-.35, .35)
            r_cc = (c / prev_c.reindex(c.index) - 1).clip(-.35, .35)
            s = s.assign(a=s.ts_code.map(r_on), b=s.ts_code.map(r_id), e=s.ts_code.map(r_cc)).dropna(subset=["a", "b", "e"])
            if len(s):
                g = s.groupby("l1_name")
                on[d] = pd.concat([g.a.mean(), pd.Series({"_mkt": s.a.mean()})]); idy[d] = pd.concat([g.b.mean(), pd.Series({"_mkt": s.b.mean()})]); cc[d] = pd.concat([g.e.mean(), pd.Series({"_mkt": s.e.mean()})])
        prev_c = c
    out = (pd.DataFrame(on).T.sort_index(), pd.DataFrame(idy).T.sort_index())
    return out + (pd.DataFrame(cc).T.sort_index(),) if with_cc else out

def cost_rt(slip_bp, book, n=25):
    per = book / n  # 单票成交额
    comm = max(2.5e-4, 5 / per)
    return 2 * comm + 5e-4 + 2 * slip_bp * 1e-4  # 卖开盘+买回收盘 一个来回

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--allow-stale", action="store_true", help="sw_pit 过期时仍照跑（disclosure 写入回执）")
    fresh = C.require_fresh("sw_pit", allow_stale=ap.parse_args().allow_stale)
    on, idy = legs(); sess = on.index
    ixic = C.yahoo_daily("^IXIC", "5y").pct_change().mul(100).dropna()
    ev = sorted({sess[sess > d][0] for d in ixic.index[(ixic <= -2) & (ixic.index >= S.START_US)] if (sess > d).any()})
    rows = []
    for k in INDS + ["_mkt"]:
        a, b = on.loc[ev, k], idy.loc[ev, k]
        ax_, bx = a - on.loc[ev, "_mkt"], b - idy.loc[ev, "_mkt"]
        base_b = idy[k].drop(ev)
        rows.append({"industry": "全市场" if k == "_mkt" else k, "n": len(ev),
            "overnight_abs": a.mean()*100, "intraday_abs": b.mean()*100, "intraday_abs_t": b.mean()/(b.std(ddof=1)/np.sqrt(len(b)))*1, 
            "intraday_hit_down": (b < 0).mean(), "intraday_base_mean": base_b.mean()*100,
            "overnight_excess": ax_.mean()*100, "intraday_excess": bx.mean()*100,
            "intraday_excess_t": (bx.mean()/(bx.std(ddof=1)/np.sqrt(len(bx)))) if k != "_mkt" else None})
    df = pd.DataFrame(rows).round(4)
    costs = {f"{b//10000}万_slip{s}bp": round(cost_rt(s, b)*100, 3) for b in (600000, 1000000) for s in (30, 10)}
    # 可交易口径：A股无法在 t0 收盘前知道纳指，隔夜段不可捕获；只能 t1 开盘卖出、收盘买回（回避型）
    for kc, cv in costs.items():
        df[f"net_avoid_{kc}"] = (-df.intraday_abs - cv).round(3)
        df[f"net_rotate_{kc}"] = (-df.intraday_excess - 2*cv).round(3)
    df.to_csv(OUT / "c1_gap_split.csv", index=False)
    ts = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M")
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    p = df.set_index("industry")[["overnight_abs", "intraday_abs"]]; p.plot.bar(ax=ax[0], color=["#4C72B0", "#DD8452"], rot=0)
    ax[0].axhline(0, c="k", lw=.6); ax[0].set_title(f"纳指≤-2% 次日：隔夜 vs 日内（绝对，n={len(ev)}）"); ax[0].set_ylabel("%"); ax[0].legend(ax[0].containers, ["收盘→开盘", "开盘→收盘"]); ax[0].set_xlabel("")
    q = df[df.industry != "全市场"].set_index("industry")
    w = .35; x = np.arange(len(q))
    ax[1].bar(x - w/2, -q.intraday_abs, w, label="回避收益(−日内)"); ax[1].axhline(costs["60万_slip30bp"], c="r", ls="--", label=f"成本 60万/滑点30bp {costs['60万_slip30bp']:.2f}%")
    ax[1].axhline(costs["60万_slip10bp"], c="orange", ls=":", label=f"成本 60万/滑点10bp {costs['60万_slip10bp']:.2f}%")
    ax[1].bar(x + w/2, -q.intraday_excess, w, label="轮动收益(−日内超额，成本为2倍)"); ax[1].set_xticks(x, q.index); ax[1].axhline(0, c="k", lw=.6)
    ax[1].set_title("日内段可捕获收益 vs 一个来回成本"); ax[1].set_ylabel("%"); ax[1].legend(fontsize=8)
    fig.suptitle("C1 纳指≤-2% 次日科技链：开盘跳空拆分与成本（2024-06→最新，研究级）", fontsize=11); fig.tight_layout()
    png = OUT / f"c1_gap_split_{ts}.png"; fig.savefig(png, dpi=120)
    meta = {"written_et": ts, "png": str(png), "n_events": len(ev), "costs_roundtrip_pct": costs, "sw_pit_freshness": fresh, "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)}
    (OUT / "c1_gap_split_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps(meta, ensure_ascii=False)); print(df.to_string())

if __name__ == "__main__": main()
