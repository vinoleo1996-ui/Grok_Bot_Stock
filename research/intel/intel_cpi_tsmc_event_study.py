"""(a) 真实 CPI 核心环比意外、(b) 台积电实际营收−指引中值 → A 股申万一级行业：隔夜/日内/次日/5日(自开盘)超额，扣成本。
口径同 C1（intel_c1_gap_split.py）。研究级，live=false，不开叶，不下单。只用 2024-06 以后数据。"""
import json, resource, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_c1_gap_split as G
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
R = G.R; OUT = G.OUT; CD = R / "data/v2/intel_consensus"
COST = {"30bp": G.cost_rt(30, 600000), "10bp": G.cost_rt(10, 600000)}  # 60万/100万 相同（见 C1）
HAWK = {"银行": 1, "煤炭": 1, "石油石化": 1, "电子": -1, "通信": -1, "计算机": -1, "传媒": -1, "房地产": -1, "有色金属": -1}
TSMC = {"电子": 1, "通信": 1, "计算机": 1}

def study(on, idy, cc, dates, label, dirs):
    sess = on.index; t1s = sorted({sess[sess > pd.Timestamp(d)][0] for d in dates if (sess > pd.Timestamp(d)).any()})
    t1s = [t for t in t1s if sess.get_loc(t) + 4 < len(sess)]
    rows = []
    for k, e in dirs.items():
        o = on.loc[t1s, k] - on.loc[t1s, "_mkt"]; i = idy.loc[t1s, k] - idy.loc[t1s, "_mkt"]; c1 = cc.loc[t1s, k] - cc.loc[t1s, "_mkt"]
        f5 = []
        for t in t1s:
            j = sess.get_loc(t); w = sess[j + 1:j + 5]
            ind = (1 + idy.loc[t, k]) * (1 + cc.loc[w, k]).prod() - 1; mk = (1 + idy.loc[t, "_mkt"]) * (1 + cc.loc[w, "_mkt"]).prod() - 1
            f5.append(ind - mk)
        f5 = pd.Series(f5, index=t1s); n = len(t1s)
        tt = lambda x: float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))) if len(x) > 2 and x.std() > 0 else None
        r = {"event": label, "industry": k, "dir": e, "n": n, "overnight_ex": o.mean() * 100, "intraday_ex": i.mean() * 100, "intraday_ex_t": tt(i),
             "cc1_ex": c1.mean() * 100, "cc1_hit": float((np.sign(c1) == e).mean()), "open5_ex": f5.mean() * 100, "open5_ex_t": tt(f5), "open5_hit": float((np.sign(f5) == e).mean())}
        for cn, cv in COST.items():
            r[f"net1_rot_{cn}"] = e * r["intraday_ex"] - 2 * cv * 100; r[f"net5_rot_{cn}"] = e * r["open5_ex"] - 2 * cv * 100
            if e < 0: r[f"net1_avoid_{cn}"] = -idy.loc[t1s, k].mean() * 100 - cv * 100
        rows.append(r)
    return rows, t1s

def main():
    on, idy, cc = G.legs(with_cc=True)
    cpi = pd.read_csv(CD / "us_cpi_consensus_ff.csv"); cpi = cpi[cpi.indicator == "Core CPI m/m"]
    hawk = cpi[cpi.surprise_pp >= 0.1].release_date.tolist(); dove = cpi[cpi.surprise_pp <= -0.1].release_date.tolist()
    ts = pd.read_csv(CD / "tsmc_revenue_vs_guidance.csv")
    rep = ts.dropna(subset=["surprise_vs_mid_pct"]); med = rep.surprise_vs_mid_pct.median()
    mon = ts.dropna(subset=["surprise_monthly_at_guide_fx_pct"]); medm = mon.surprise_monthly_at_guide_fx_pct.median()
    ev = [("CPI核心意外≥+0.1", hawk, HAWK), ("CPI核心意外≤-0.1", dove, {k: -v for k, v in HAWK.items()}),
          ("TSMC法说:实际−指引中值≥中位", rep[rep.surprise_vs_mid_pct >= med].report_date.tolist(), TSMC),
          ("TSMC法说:实际−指引中值<中位", rep[rep.surprise_vs_mid_pct < med].report_date.tolist(), {k: -1 for k in TSMC}),
          ("TSMC季末月营收:隐含意外≥中位", mon[mon.surprise_monthly_at_guide_fx_pct >= medm].monthly_complete_date.tolist(), TSMC),
          ("TSMC季末月营收:隐含意外<中位", mon[mon.surprise_monthly_at_guide_fx_pct < medm].monthly_complete_date.tolist(), {k: -1 for k in TSMC})]
    allr, used = [], {}
    for lab, ds, dr in ev:
        r, t1 = study(on, idy, cc, ds, lab, dr); allr += r; used[lab] = [str(t.date()) for t in t1]
    df = pd.DataFrame(allr).round(3); df.to_csv(OUT / "cpi_tsmc_event_study.csv", index=False)
    now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M")
    fig, axes = plt.subplots(2, 3, figsize=(16, 8.5))
    for ax, (lab, _, _) in zip(axes.flat, ev):
        q = df[df.event == lab].set_index("industry"); x = np.arange(len(q)); w = .27
        ax.bar(x - w, q.overnight_ex * q.dir, w, label="隔夜超额×方向"); ax.bar(x, q.intraday_ex * q.dir, w, label="日内超额×方向")
        ax.bar(x + w, q.open5_ex * q.dir, w, label="5日(自开盘)超额×方向"); ax.axhline(2 * COST["30bp"] * 100, c="r", ls="--", lw=1, label="轮动成本30bp")
        ax.axhline(2 * COST["10bp"] * 100, c="orange", ls=":", lw=1, label="轮动成本10bp"); ax.axhline(0, c="k", lw=.5)
        ax.set_xticks(x, q.index, fontsize=8, rotation=30); ax.set_title(f"{lab}  n={int(q.n.iloc[0])}", fontsize=10)
    axes.flat[0].legend(fontsize=7); fig.suptitle("真实 CPI 意外 / 台积电营收−指引 → A 股行业超额（正=符合先验方向；2024-06→最新，研究级）", fontsize=11)
    fig.tight_layout(); png = OUT / f"cpi_tsmc_event_study_{now}.png"; fig.savefig(png, dpi=110)
    meta = {"written_et": now, "png": str(png), "events_t1": used, "tsmc_median_surprise_vs_mid": med, "tsmc_median_monthly": medm,
            "cost_roundtrip_pct": {k: v * 100 for k, v in COST.items()}, "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}
    (OUT / "cpi_tsmc_event_study_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "events_t1"}, ensure_ascii=False)); print({k: len(v) for k, v in used.items()})
    pd.set_option("display.width", 250); print(df.drop(columns=[c for c in df if c.startswith("net1_avoid")]).to_string())
    print(df[["event", "industry"] + [c for c in df if c.startswith("net1_avoid")]].dropna().to_string())

if __name__ == "__main__": main()
