"""PIT 事件特征候选：小样本历史检验（研究级，live=false，不开叶，不下单，禁 GP）。
只用 2024-06 以后数据（封存窗口不读）。复用 intel_event_study 的流式行业收益（RSS<1.5GB）。
检验1：CPI 发布日美债10Y(^TNX)日变动作为「市场隐含 CPI 意外」代理（无历史一致预期库，见文档）。
      发布日来源：BLS CPI 新闻稿归档 https://www.bls.gov/bls/news-release/cpi.htm
检验2：纳指≤-2% 的次日与 5 日行业超额（扩展已有次日结论）。
次日=第一个严格晚于美股事件日的 A 股交易日 t1；5日=t1..t5 累计；超额=行业 − mid_large 等权全市场。"""
from __future__ import annotations
import json, re, resource, sys, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_common as C, intel_event_study as S
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
OUT = C.ROOT / "output/intel/pit_candidates"; OUT.mkdir(parents=True, exist_ok=True)
INDS = ["电子", "通信", "计算机", "传媒", "银行", "煤炭", "石油石化", "有色金属", "房地产", "非银金融"]

def cpi_dates():
    # BLS 拒绝 urllib；用 curl 抓取的归档快照（同目录 bls_cpi_release_archive_*.htm）
    s = sorted(OUT.glob("bls_cpi_release_archive_*.htm"))[-1].read_text("utf-8", "ignore")
    d = sorted({y + m + dd for m, dd, y in re.findall(r"cpi_(\d\d)(\d\d)(\d{4})\.htm", s)})
    return [pd.Timestamp(x) for x in d if x >= "20240603"]

def fwd(ind, mkt, dates, h):
    sess = ind.index; rel = ind.sub(mkt, axis=0); rows = {}
    for d in dates:
        after = sess[sess > d]
        if len(after) < h: continue
        w = after[:h]
        rows[d] = ((1 + rel.loc[w]).prod() - 1) if h > 1 else rel.loc[w[0]]
    return pd.DataFrame(rows).T

def summarize(ev, ind, mkt, label, dirs):
    out = []
    for h in (1, 5):
        f = fwd(ind, mkt, ev, h)
        for k in INDS:
            if k not in f: continue
            r = f[k].dropna(); e = dirs.get(k)
            out.append({"event": label, "h": h, "industry": k, "n": int(len(r)), "mean_excess_pct": round(float(r.mean() * 100), 3),
                        "t": round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2) if len(r) > 2 else None,
                        "prior_dir": e, "hit_rate": round(float((np.sign(r) == e).mean()), 3) if e else None})
    return out

def main():
    ind, mkt = S.a_share_industry_returns()
    tnx = C.yahoo_daily("^TNX", "5y"); dtnx = (tnx.diff() * 100).dropna()
    ixic = C.yahoo_daily("^IXIC", "5y").pct_change().mul(100).dropna()
    cd = [d for d in cpi_dates() if d in dtnx.index]
    cpi = pd.DataFrame({"d10y_bp": dtnx.reindex(cd), "ixic_pct": ixic.reindex(cd)})
    cpi.index.name = "release_date"; cpi.round(2).to_csv(OUT / "cpi_release_day_moves.csv")
    hawk = list(cpi.index[cpi.d10y_bp >= 5]); dove = list(cpi.index[cpi.d10y_bp <= -5])
    hdir = {"银行": 1, "煤炭": 1, "石油石化": 1, "电子": -1, "通信": -1, "计算机": -1, "传媒": -1, "房地产": -1, "有色金属": -1}
    res = summarize(hawk, ind, mkt, "CPI鹰(10Y≥+5bp)", hdir) + summarize(dove, ind, mkt, "CPI鸽(10Y≤-5bp)", {k: -v for k, v in hdir.items()})
    nq = [d for d in ixic.index[ixic <= -2] if d >= S.START_US]
    res += summarize(nq, ind, mkt, "纳指≤-2%", {"电子": -1, "通信": -1, "计算机": -1, "传媒": -1})
    df = pd.DataFrame(res); df.to_csv(OUT / "pit_candidate_study.csv", index=False)
    ts = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M")  # 实际写入时间(ET)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for ax, lab in zip(axes, ["CPI鹰(10Y≥+5bp)", "CPI鸽(10Y≤-5bp)", "纳指≤-2%"]):
        p = df[df.event == lab].pivot(index="industry", columns="h", values="mean_excess_pct").reindex(INDS).dropna(how="all")
        n = int(df[(df.event == lab) & (df.h == 1)].n.max())
        p.plot.barh(ax=ax, color=["#4C72B0", "#DD8452"]); ax.axvline(0, c="k", lw=.6)
        ax.set_title(f"{lab}  n={n}"); ax.set_xlabel("相对全市场超额 %"); ax.legend(ax.containers, ["次日", "5日"], fontsize=8); ax.set_ylabel("")
    fig.suptitle("PIT 事件候选小样本检验（2024-06→最新，mid_large 等权申万一级，研究级）", fontsize=11); fig.tight_layout()
    png = OUT / f"pit_candidates_study_{ts}.png"; fig.savefig(png, dpi=120)
    meta = {"written_et": ts, "png": str(png), "cpi_events": len(cpi), "hawk": len(hawk), "dove": len(dove), "nasdaq_events": len(nq),
            "a_window": f"{ind.index.min().date()}→{ind.index.max().date()}", "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}
    (OUT / "pit_candidate_study_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1)); print(json.dumps(meta, ensure_ascii=False))

if __name__ == "__main__":
    main()
