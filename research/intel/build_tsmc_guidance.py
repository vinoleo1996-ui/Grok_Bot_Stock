"""台积电「实际营收 − 官方指引中值」历史库。来源：SEC EDGAR 6-K（CIK 1046179）：季度财报新闻稿 EX-99.1 与月营收公告。
原始 HTML 落盘 data/v2/intel_consensus/tsmc_raw/。研究级，live=false。python3（标准库 + pandas）。"""
import re, glob, html, json
from pathlib import Path
import pandas as pd
D = Path("/workspace/QuantLab/data/v2/intel_consensus"); RAW = D / "tsmc_raw"
ACC = {}  # 文件日期 → EDGAR 链接
sub = json.load(open("/tmp/tsm_sub.json"))["filings"]["recent"] if Path("/tmp/tsm_sub.json").exists() else None
if sub:
    for d, a, p in zip(sub["filingDate"], sub["accessionNumber"], sub["primaryDocument"]):
        ACC.setdefault(d, []).append(f"https://www.sec.gov/Archives/edgar/data/1046179/{a.replace('-', '')}/")
txt = lambda f: re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", open(f, errors="ignore").read())))
MON = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
QN = {"first": 1, "second": 2, "third": 3, "fourth": 4}
def url(f):
    d, n = Path(f).name.split("_", 1); return next((b + n for b in ACC.get(d, [])), None)
# 月营收
mrev = {}
for f in sorted(RAW.glob("*_tsm-revenue*.htm")):
    t = txt(f); m = re.search(r"revenue for (\w+) (\d{4}) was approximately NT\$([\d,.]+) billion", t)
    if m: mrev[(int(m.group(2)), MON[m.group(1)])] = (float(m.group(3).replace(",", "")), f.name.split("_")[0], url(f))
# 财报：本季实际 USD + 下季指引
calls = []
for f in sorted(RAW.glob("*withguidance*.htm")):
    t = txt(f); d = f.name.split("_")[0]
    a = re.search(r"In US dollars, (\w+) quarter revenue was \$([\d.]+) billion", t)
    g = re.search(r"expects the overall performance for (\w+) quarter (\d{4}).*?between US\$([\d.]+) billion and US\$([\d.]+) billion.*?1 US dollar to ([\d.]+) NT dollars", t)
    calls.append({"call_date": d, "actual_q": QN[a.group(1).lower()], "actual_usd_bn": float(a.group(2)),
                  "guide_q": QN[g.group(1).lower()], "guide_year": int(g.group(2)), "guide_low": float(g.group(3)),
                  "guide_high": float(g.group(4)), "guide_fx": float(g.group(5)), "src": url(f), "raw": f.name})
rows = []
for i, c in enumerate(calls):
    nxt = next((x for x in calls if x["call_date"] > c["call_date"]), None)
    y, q = c["guide_year"], c["guide_q"]; mid = (c["guide_low"] + c["guide_high"]) / 2
    ms = [(y, 3 * q - 2), (y, 3 * q - 1), (y, 3 * q)]
    r = {"guided_quarter": f"{y}Q{q}", "guidance_date": c["call_date"], "guide_low_usd_bn": c["guide_low"], "guide_high_usd_bn": c["guide_high"],
         "guide_mid_usd_bn": mid, "guide_fx_ntd_per_usd": c["guide_fx"], "guidance_source": c["src"]}
    if all(m in mrev for m in ms):
        ntd = sum(mrev[m][0] for m in ms); r.update({"q_ntd_bn_from_monthly": round(ntd, 2), "monthly_complete_date": mrev[ms[2]][1],
              "monthly_source": mrev[ms[2]][2], "surprise_monthly_at_guide_fx_pct": round((ntd / c["guide_fx"] / mid - 1) * 100, 2)})
    if nxt:
        r.update({"report_date": nxt["call_date"], "actual_usd_bn": nxt["actual_usd_bn"], "actual_source": nxt["src"],
                  "surprise_vs_mid_pct": round((nxt["actual_usd_bn"] / mid - 1) * 100, 2),
                  "beat_high": nxt["actual_usd_bn"] > c["guide_high"]})
    rows.append(r)
df = pd.DataFrame(rows); df.to_csv(D / "tsmc_revenue_vs_guidance.csv", index=False)
print(df.drop(columns=[c for c in df if "source" in c]).to_string())
