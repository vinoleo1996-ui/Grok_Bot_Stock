"""收集 AI 链龙头财报 CNBC 报道（LSEG 一致预期）。sitemap → 候选文章 → 原文落盘。研究级。python3。"""
import json, re, subprocess, time, html
from pathlib import Path
import pandas as pd
RAW = Path("/workspace/QuantLab/data/v2/intel_consensus/ai_earn_raw"); SM = RAW / "sitemap"; AR = RAW / "cnbc"; SM.mkdir(exist_ok=True); AR.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
NAME = {"NVDA": ["nvidia"], "AVGO": ["broadcom"], "AMD": ["amd", "advanced micro"], "MU": ["micron"], "MSFT": ["microsoft"],
        "GOOGL": ["alphabet", "google"], "META": ["meta"], "AMZN": ["amazon"], "ASML": ["asml"], "TSMC": ["tsmc", "taiwan semi"]}
KW = re.compile(r"earn|results|report|revenue|quarter|guidance|forecast|beats|misses|tops", re.I)
def get(url, f):
    if not f.exists() or f.stat().st_size < 5000:
        subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-A", UA, "-o", str(f), url]); time.sleep(1)
    return f.read_text("utf-8", "ignore") if f.exists() else ""
def sitemap(d):
    s = get(f"https://www.cnbc.com/site-map/articles/{d.year}/{d.strftime('%B')}/{d.day}/", SM / f"{d.date()}.htm")
    s = s.replace("\\u002F", "/")
    return re.findall(r'"title":"([^"]+)","url":"(https://www\.cnbc\.com/\d{4}/\d\d/\d\d/[^"]+)"', s)
def main():
    ev = json.load(open(RAW / "edgar_events.json"))
    ts = pd.read_csv(RAW.parent / "tsmc_revenue_vs_guidance.csv").dropna(subset=["report_date"]).report_date.tolist() + ["2026-07-16"]
    ev["TSMC"] = [(d, None, None) for d in sorted(set(ts)) if d >= "2024-06-01"]
    found = []
    for t, lst in ev.items():
        for d, acc, p in lst:
            d0 = pd.Timestamp(d); cands = []
            for dd in [d0 - pd.Timedelta(days=1), d0, d0 + pd.Timedelta(days=1)]:
                for ti, u in sitemap(dd):
                    tl = ti.lower()
                    if any(n in tl for n in NAME[t]) and KW.search(tl) and "cramer" not in tl and "live" not in u: cands.append((ti, u))
            # 优先标准财报稿：url 含 earnings 且 ticker/公司名
            cands = sorted(set(cands), key=lambda x: (0 if re.search(r"earnings|results", x[1]) else 1, len(x[1])))
            found.append({"ticker": t, "filing_date": d, "accession": acc, "primary_doc": p, "cands": cands[:6]})
    json.dump(found, open(RAW / "cnbc_candidates.json", "w"), ensure_ascii=False, indent=0)
    print(sum(1 for f in found if f["cands"]), "/", len(found))
if __name__ == "__main__": main()
