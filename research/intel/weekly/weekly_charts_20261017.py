"""10-12至10-17 图文周报：作图 + 指标落盘。研究级，live=false，不下单不改权重。
数据：Yahoo chart v8（weekly_data/yahoo_*.json，本轮 23:53 ET 拉取）、US Treasury 日度曲线、NY Fed EFFR、TSMC 指引库、BLS/Census 公布值（手录，注明来源）。"""
import json, sys, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from datetime import datetime; from zoneinfo import ZoneInfo
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]; plt.rcParams["axes.unicode_minus"] = False
R = "/workspace/QuantLab/"; D = R + "output/intel/weekly_data/"; CH = R + "output/intel/charts/"
TS = datetime.now(ZoneInfo("America/New_York")).strftime("%Y%m%d_%H%M")
y = json.load(open(D + "yahoo_20261017.json")); cn = json.load(open(D + "yahoo_cn_20261017.json"))
def ser(dct, s): return pd.Series({pd.Timestamp(k): v for k, v in dct[s].items()}).sort_index()
def wk(dct, s, start="2026-10-09", end="2026-10-16"):
    x = ser(dct, s); a = x[x.index <= start].iloc[-1]; b = x[x.index <= end].iloc[-1]
    return a, b, (b / a - 1) * 100, str(x[x.index <= start].index[-1].date())
M = {}
rows = [("纳指", y, "^IXIC"), ("费城半导体", y, "^SOX"), ("标普500", y, "^GSPC"), ("日经225", y, "^N225"), ("KOSPI", y, "^KS11"),
        ("恒生指数", y, "^HSI"), ("上证指数", y, "000001.SS"), ("深证成指", cn, "399001.SZ"), ("创业板ETF", cn, "159915.SZ"),
        ("科创50ETF", cn, "588000.SS"), ("美元指数", y, "DX-Y.NYB"), ("COMEX黄金", y, "GC=F"), ("WTI原油", y, "CL=F"), ("VIX", y, "^VIX"),
        ("TSM ADR", y, "TSM"), ("台积电(2330.TW)", y, "2330.TW"), ("NVDA", y, "NVDA"), ("AMD", y, "AMD"), ("AVGO", y, "AVGO"), ("MU", y, "MU"),
        ("ASML ADR", y, "ASML"), ("LRCX", y, "LRCX"), ("INTC", y, "INTC"), ("KWEB", y, "KWEB")]
for n, dd, s in rows:
    a, b, c, d0 = wk(dd, s); x = ser(dd, s); last2 = x[x.index <= "2026-10-16"].iloc[-2:]
    M[n] = dict(sym=s, base_date=d0, base=round(a, 3), last=round(b, 3), wk_pct=round(c, 2), d1016_pct=round((last2.iloc[-1] / last2.iloc[-2] - 1) * 100, 2))
# 美债：Treasury 官方日度曲线
tr = pd.read_csv(D + "treasury_curve_2026.csv"); tr["Date"] = pd.to_datetime(tr["Date"]); tr = tr.set_index("Date").sort_index()
tr = tr[tr.index >= "2026-10-01"]
for k, col in (("美债2Y", "2 Yr"), ("美债10Y", "10 Yr")):
    a = tr.loc["2026-10-09", col]; b = tr.loc["2026-10-16", col]; M[k] = dict(sym="UST " + col, base_date="2026-10-09", base=a, last=b, wk_bp=round((b - a) * 100, 1),
                                                                                   d1016_bp=round((b - tr.loc["2026-10-15", col]) * 100, 1), peak_1014=tr.loc["2026-10-14", col])
# 联邦基金期货推算 10-28 加息概率（ZQX26，EFFR 3.88% NY Fed）
zq = ser(y, "ZQX26.CBT"); EFFR = 3.88
fed = pd.DataFrame({"ZQX26": zq, "implied": 100 - zq}); fed["p_hike_pct"] = ((fed.implied - EFFR) / 0.25 * 100).clip(0, 100).round(0)
fed = fed[fed.index >= "2026-10-01"]
cme = {"2026-10-08": 18, "2026-10-15": 34, "2026-10-16": 15.5}  # CNBC 10-15 引 CME：本周四≈34%、一周前<18%；WSJ/Invezz 10-16：≈15–16%
M["fed"] = dict(zq_series={str(k.date()): float(v) for k, v in fed.p_hike_pct.items()}, cme_points=cme, effr=EFFR)
json.dump(M, open(D + f"weekly_metrics_{TS}.json", "w"), ensure_ascii=False, indent=1)
out = []
# 图1 外盘周涨跌
fig, ax = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [3, 1]})
names = ["纳指", "费城半导体", "标普500", "日经225", "KOSPI", "恒生指数", "上证指数", "深证成指", "创业板ETF", "科创50ETF", "美元指数", "COMEX黄金", "WTI原油"]
v = [M[n]["wk_pct"] for n in names]; col = ["#c0392b" if x < 0 else "#27ae60" for x in v]
ax[0].barh(names[::-1], v[::-1], color=col[::-1]); [ax[0].text(x + (0.3 if x >= 0 else -0.3), i, f"{x:+.1f}%", va="center", ha="left" if x >= 0 else "right", fontsize=8) for i, x in enumerate(v[::-1])]
ax[0].axvline(0, color="k", lw=.6); ax[0].set_xlabel("周涨跌 %（10-09收→10-16收；KOSPI 基期10-08，10-09休市）"); ax[0].set_title("本周外盘与A股：半导体链领跌，原油+10%")
ax[0].set_xlim(min(v) - 3, max(v) + 3)
b = [M["美债2Y"]["wk_bp"], M["美债10Y"]["wk_bp"]]; ax[1].bar(["2Y", "10Y"], b, color="#2980b9"); [ax[1].text(i, x - 1, f"{x:+.0f}bp", ha="center", va="top") for i, x in enumerate(b)]
ax[1].axhline(0, color="k", lw=.6); ax[1].set_title("美债周变动（bp）"); ax[1].set_ylim(min(b) - 6, 3)
fig.text(0.01, 0.01, "来源：Yahoo Finance 日收盘（23:53 ET 拉取）；美债为 U.S. Treasury 日度收益率曲线。研究级。", fontsize=8, color="gray")
fig.tight_layout(rect=(0, .03, 1, 1)); p = CH + f"weekly_markets_{TS}.png"; fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
# 图2 半导体链日度路径
fig, ax = plt.subplots(figsize=(12, 5.6))
for n, dd, s in [("费城半导体", y, "^SOX"), ("纳指", y, "^IXIC"), ("KOSPI", y, "^KS11"), ("日经225", y, "^N225"), ("TSM ADR", y, "TSM"), ("台积电2330.TW", y, "2330.TW"),
                 ("A股半导体ETF 512480", cn, "512480.SS"), ("A股通信ETF 515880", cn, "515880.SS"), ("A股银行ETF 512800", cn, "512800.SS")]:
    x = ser(dd, s); x = x[(x.index >= "2026-10-08") & (x.index <= "2026-10-16")]; x = x / x.iloc[0] * 100
    ax.plot(x.index, x.values, marker="o", ms=3, lw=2 if "A股" in n else 1.4, ls="-" if "A股" in n else "--", label=f"{n} {x.iloc[-1]-100:+.1f}%")
for d, t in [("2026-10-12", "Broadcom/Intel CEO\n警示AI融资"), ("2026-10-14", "CPI偏鹰"), ("2026-10-15", "PPI+1.3%/台积电法说\nKOSPI熔断-7.6%"), ("2026-10-16", "费半8连跌\n-3.8%")]:
    ax.axvline(pd.Timestamp(d), color="gray", lw=.5, ls=":"); ax.text(pd.Timestamp(d), 101.5, t, fontsize=7.5, ha="center", va="bottom", color="dimgray")
ax.axhline(100, color="k", lw=.5); ax.set_ylabel("10-08 收盘 = 100"); ax.set_ylim(83, 106); ax.legend(fontsize=8, ncol=3, loc="lower left"); ax.set_title("AI/半导体全球去杠杆路径：费半与KOSPI领跌，A股半导体/通信跟跌、银行逆势")
fig.text(0.01, 0.01, "来源：Yahoo Finance 日收盘；事件标注来自 CNBC/Korea Herald/Investing.com 报道。", fontsize=8, color="gray")
fig.tight_layout(rect=(0, .03, 1, 1)); p = CH + f"weekly_semis_path_{TS}.png"; fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
# 图3 台积电营收 vs 指引
g = pd.read_csv(R + "data/v2/intel_consensus/tsmc_revenue_vs_guidance.csv")
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
h = g.dropna(subset=["actual_usd_bn"]); xs = np.arange(len(h))
ax[0].vlines(xs, h.guide_low_usd_bn, h.guide_high_usd_bn, color="#95a5a6", lw=8, label="指引区间")
ax[0].scatter(xs, h.actual_usd_bn, color="#c0392b", zorder=3, label="实际营收"); q4 = g[g.guided_quarter == "2026Q4"].iloc[0]
ax[0].vlines([len(h)], q4.guide_low_usd_bn, q4.guide_high_usd_bn, color="#e67e22", lw=8, label="2026Q4 指引 52.3–54.3")
ax[0].set_xticks(list(xs) + [len(h)]); ax[0].set_xticklabels(list(h.guided_quarter) + ["2026Q4E"], rotation=45, fontsize=8); ax[0].set_ylabel("十亿美元"); ax[0].legend(fontsize=8); ax[0].set_title("台积电季度营收 vs 自家指引")
s = h.surprise_vs_mid_pct.values; c = ["#c0392b" if q == "2026Q3" else "#7f8c8d" for q in h.guided_quarter]
ax[1].bar(xs, s, color=c); med = np.median(s[:-1]); ax[1].axhline(med, color="#2980b9", ls="--", lw=1, label=f"前9季中位数 {med:.2f}%")
[ax[1].text(i, x + .08, f"{x:.2f}", ha="center", fontsize=8) for i, x in enumerate(s)]
ax[1].set_xticks(xs); ax[1].set_xticklabels(h.guided_quarter, rotation=45, fontsize=8); ax[1].set_ylabel("实际 − 指引中值（%）"); ax[1].legend(fontsize=8); ax[1].set_title("2026Q3 超指引中值 +3.36%，高于历史中位")
fig.text(0.01, 0.01, "来源：TSMC SEC 6-K（Management Report/Earnings Release，2026-10-15 等），库：data/v2/intel_consensus/tsmc_revenue_vs_guidance.csv", fontsize=8, color="gray")
fig.tight_layout(rect=(0, .03, 1, 1)); p = CH + f"weekly_tsmc_guidance_{TS}.png"; fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
# 图4 通胀数据 vs 预期 + 利率/加息概率
fig, ax = plt.subplots(1, 3, figsize=(15, 5))
lab = ["CPI环比", "核心CPI环比", "PPI环比", "核心PPI环比", "零售环比", "零售(除汽车/加油)"]
act = [0.6, 0.3, 1.3, 0.7, 0.8, 0.25]; exp = [0.6, 0.2, 0.6, 0.3, 0.4, np.nan]
xx = np.arange(len(lab)); ax[0].bar(xx - .2, act, .4, label="实际", color="#c0392b"); ax[0].bar(xx + .2, exp, .4, label="预期", color="#bdc3c7")
[ax[0].text(i - .2, a + .03, f"{a}", ha="center", fontsize=8) for i, a in enumerate(act)]
ax[0].set_xticks(xx); ax[0].set_xticklabels(lab, rotation=30, fontsize=8); ax[0].set_ylabel("%"); ax[0].legend(fontsize=8); ax[0].set_title("9月美国数据：PPI大幅超预期")
t = tr[(tr.index >= "2026-10-01")]; ax[1].plot(t.index, t["2 Yr"], marker="o", label="2Y"); ax[1].plot(t.index, t["10 Yr"], marker="o", label="10Y")
ax[1].axvspan(pd.Timestamp("2026-10-12"), pd.Timestamp("2026-10-16"), color="#f9e79f", alpha=.4); ax[1].legend(); ax[1].set_title("美债收益率（Treasury 日度）：CPI后反而下行"); ax[1].tick_params(axis="x", rotation=45, labelsize=7)
f = fed[fed.index >= "2026-10-05"]; ax[2].plot(f.index, f.p_hike_pct, marker="o", label="本机：ZQX26−EFFR 推算")
cp = pd.Series({pd.Timestamp(k): v for k, v in cme.items()}); ax[2].scatter(cp.index, cp.values, color="#c0392b", zorder=3, s=50, label="CME FedWatch（媒体引述）")
ax[2].scatter([pd.Timestamp("2026-10-14")], [44], marker="x", color="k", label="10-14 08:46 盘中推算 44%")
ax[2].set_ylim(0, 55); ax[2].set_ylabel("10-28 加息 25bp 概率 %"); ax[2].legend(fontsize=7.5); ax[2].set_title("10月加息概率：22%→44%→16%"); ax[2].tick_params(axis="x", rotation=45, labelsize=7)
fig.text(0.01, 0.01, "来源：BLS CPI/PPI、Census 零售；预期 Dow Jones/WSJ（经 CNBC/WSJ）；Treasury；CBOT ZQX26（Yahoo）、NY Fed EFFR 3.88%；CME 点位引自 CNBC 10-15、WSJ/Invezz 10-16。", fontsize=7.5, color="gray")
fig.tight_layout(rect=(0, .04, 1, 1)); p = CH + f"weekly_macro_fed_{TS}.png"; fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
# 图5 A股行业ETF周表现 + 纸面暴露
ex = json.load(open(D + "paper_exposure_20261014.json"))["exposure"]
etf = [("通信", "515880.SS"), ("半导体/电子", "512480.SS"), ("计算机", "512720.SS"), ("有色", "512400.SS"), ("房地产", "512200.SS"), ("医药", "512010.SS"),
       ("煤炭", "515220.SS"), ("军工", "512660.SS"), ("电力", "159611.SZ"), ("黄金", "518880.SS"), ("消费", "159928.SZ"), ("能源", "159930.SZ"), ("银行", "512800.SS"), ("沪深300", "510300.SS")]
wv = [wk(cn, s)[2] for _, s in etf]; M["a_etf_wk"] = {n: round(v_, 2) for (n, _), v_ in zip(etf, wv)}
fig, ax = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.1, 1]})
o = np.argsort(wv); ax[0].barh([etf[i][0] for i in o], [wv[i] for i in o], color=["#c0392b" if wv[i] < 0 else "#27ae60" for i in o])
[ax[0].text(wv[i] + (.2 if wv[i] >= 0 else -.2), k, f"{wv[i]:+.1f}%", va="center", ha="left" if wv[i] >= 0 else "right", fontsize=8) for k, i in enumerate(o)]
ax[0].axvline(0, color="k", lw=.6); ax[0].set_xlim(min(wv) - 2.5, max(wv) + 2.5); ax[0].set_title("A股行业ETF周涨跌（10-09→10-16，未含周五美股大跌）"); ax[0].set_xlabel("%")
inds = ["银行", "电子", "通信", "计算机", "煤炭", "石油石化", "公用事业", "电力设备", "食品饮料", "家用电器", "非银金融", "未映射"]
tr_ = ["capacity_adv", "b4_600000", "b4_1000000", "s6_60w", "s6_100w"]
mat = np.array([[ex[t].get(i, 0) * 100 for t in tr_] for i in inds]); im = ax[1].imshow(mat, cmap="YlOrRd", aspect="auto")
ax[1].set_xticks(range(len(tr_))); ax[1].set_xticklabels(tr_, fontsize=8); ax[1].set_yticks(range(len(inds))); ax[1].set_yticklabels([i if i != "未映射" else "沪深300ETF" for i in inds], fontsize=8)
[ax[1].text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=8) for i in range(len(inds)) for j in range(len(tr_))]
ax[1].set_title("纸面持仓申万一级暴露 %（10-14 持仓，PIT 映射）")
fig.text(0.01, 0.01, "来源：Yahoo 日收盘（ETF 代理行业）；持仓 output/loop/paper_daily_20261014/risk_flags.parquet、output/strategy_paper_s6/*_20261014.parquet。", fontsize=8, color="gray")
fig.tight_layout(rect=(0, .03, 1, 1)); p = CH + f"weekly_ashare_paper_{TS}.png"; fig.savefig(p, dpi=130); plt.close(fig); out.append(p)
json.dump(M, open(D + f"weekly_metrics_{TS}.json", "w"), ensure_ascii=False, indent=1)
print(TS); print("\n".join(out)); print(json.dumps({k: v for k, v in M.items() if k != "fed"}, ensure_ascii=False)); print(M["fed"])
