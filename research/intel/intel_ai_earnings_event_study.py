"""AI 链龙头财报意外 → A 股电子/通信/计算机：隔夜/日内/次日/5日(自开盘)超额，扣成本。口径同 C1/§8。
意外 = 营收 vs LSEG 一致预期（TSMC 用实际−官方指引中值）；按公司内中位数去均值后分高/低（龙头几乎每季都超预期）。
另记 10-12 CEO 资本约束言论的单事件反应（只描述，不检验）。研究级，live=false，不开叶。只用 2024-06 以后数据。"""
import json, resource, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_c1_gap_split as G, intel_cpi_tsmc_event_study as E
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
CD = G.R / "data/v2/intel_consensus"; OUT = G.OUT
IND = ["电子", "通信", "计算机"]

def main():
    on, idy, cc = G.legs(with_cc=True)
    d = pd.read_csv(CD / "ai_chain_earnings_surprise.csv").dropna(subset=["rev_surprise_pct"])
    d = d[d.event_date_et >= "2024-06-03"].copy()
    d["rel"] = d.rev_surprise_pct - d.groupby("ticker").rev_surprise_pct.transform("median")
    groups = {"全部龙头:相对意外高(>0)": d[d.rel > 0], "全部龙头:相对意外低(≤0)": d[d.rel <= 0],
              "算力链(NVDA/AVGO/TSMC/MU/AMD):高": d[(d.rel > 0) & d.ticker.isin(["NVDA", "AVGO", "TSMC", "MU", "AMD"])],
              "算力链(NVDA/AVGO/TSMC/MU/AMD):低": d[(d.rel <= 0) & d.ticker.isin(["NVDA", "AVGO", "TSMC", "MU", "AMD"])],
              "云厂商(MSFT/GOOGL/META/AMZN):高": d[(d.rel > 0) & d.ticker.isin(["MSFT", "GOOGL", "META", "AMZN"])],
              "云厂商(MSFT/GOOGL/META/AMZN):低": d[(d.rel <= 0) & d.ticker.isin(["MSFT", "GOOGL", "META", "AMZN"])]}
    rows, used = [], {}
    for lab, g in groups.items():
        dirs = {k: (1 if "高" in lab.split(":")[-1] else -1) for k in IND}
        r, t1 = E.study(on, idy, cc, g.event_date_et.tolist(), lab, dirs); rows += r; used[lab] = len(t1)
    df = pd.DataFrame(rows).round(3); df.to_csv(OUT / "ai_earnings_event_study.csv", index=False)
    # 单事件：10-12 CEO 言论 → t1=10-13
    t = pd.Timestamp("2026-10-13"); one = {}
    if t in on.index:
        for k in IND + ["石油石化", "银行", "煤炭"]:
            one[k] = {"overnight_ex": round((on.loc[t, k] - on.loc[t, "_mkt"]) * 100, 2), "intraday_ex": round((idy.loc[t, k] - idy.loc[t, "_mkt"]) * 100, 2),
                      "cc_ex": round((cc.loc[t, k] - cc.loc[t, "_mkt"]) * 100, 2)}
        one["_mkt_cc"] = round(cc.loc[t, "_mkt"] * 100, 2)
    now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M")
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, lab in zip(axes.T.flat, groups):
        q = df[df.event == lab].set_index("industry"); x = np.arange(len(q)); w = .27
        ax.bar(x - w, q.overnight_ex * q.dir, w, label="隔夜超额×方向"); ax.bar(x, q.intraday_ex * q.dir, w, label="日内超额×方向")
        ax.bar(x + w, q.open5_ex * q.dir, w, label="5日(自开盘)超额×方向")
        ax.axhline(2 * E.COST["30bp"] * 100, c="r", ls="--", lw=1, label="轮动成本30bp"); ax.axhline(2 * E.COST["10bp"] * 100, c="orange", ls=":", lw=1, label="轮动成本10bp")
        ax.axhline(0, c="k", lw=.5); ax.set_xticks(x, q.index); ax.set_title(f"{lab}  n={used[lab]}", fontsize=9)
    axes.flat[0].legend(fontsize=7)
    fig.suptitle("AI 链龙头财报相对意外 → A 股科技行业超额（正=符合先验；2024-06→2026-10-15，研究级）", fontsize=11); fig.tight_layout()
    png = OUT / f"ai_earnings_event_study_{now}.png"; fig.savefig(png, dpi=110)
    meta = {"written_et": now, "png": str(png), "n_lib_rows": int(len(pd.read_csv(CD / "ai_chain_earnings_surprise.csv"))), "n_used": int(len(d)),
            "n_t1": used, "ceo_20261012_t1_20261013": one, "a_last": str(on.index.max().date()), "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}
    (OUT / "ai_earnings_event_study_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1)); print(json.dumps(meta, ensure_ascii=False))
    pd.set_option("display.width", 250); print(df.drop(columns=[c for c in df if "avoid" in c]).to_string()); print(df[["event", "industry"] + [c for c in df if "avoid" in c]].dropna().to_string())

if __name__ == "__main__": main()
