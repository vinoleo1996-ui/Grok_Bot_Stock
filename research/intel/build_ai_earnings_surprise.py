"""AI 链龙头财报意外库：CNBC(LSEG 一致预期) + 公司新闻稿(SEC 8-K EX-99.1) 核对实际值。研究级，live=false。python3。"""
import json, re, subprocess, time, html
from pathlib import Path
import pandas as pd, numpy as np
D = Path("/workspace/QuantLab/data/v2/intel_consensus"); RAW = D / "ai_earn_raw"; PR = RAW / "press"; PR.mkdir(exist_ok=True)
UA = "QuantLab research leo@example.com"
CIK = {"NVDA": 1045810, "AVGO": 1730168, "AMD": 2488, "MU": 723125, "MSFT": 789019, "GOOGL": 1652044, "META": 1326801, "AMZN": 1018724}
G = re.compile(r"(?:expects?|expected|forecast|guid\w*|sees|projected)[^$]{0,80}\$([\d.]+)\s*billion[^$]{0,120}?(?:versus|vs\.?|compared with|while|analysts)[^$]{0,80}\$([\d.]+)\s*billion[^.]{0,80}(?:LSEG|StreetAccount)", re.I)
def press(t, acc):
    if t not in CIK or not isinstance(acc, str): return None, None
    base = f"https://www.sec.gov/Archives/edgar/data/{CIK[t]}/{acc.replace('-', '')}/"
    f = PR / f"{t}_{acc}.htm"
    if not f.exists():
        idx = subprocess.run(["curl", "-s", "-A", UA, base + "index.json"], capture_output=True, text=True).stdout; time.sleep(.3)
        try: items = [i["name"] for i in json.loads(idx)["directory"]["item"]]
        except Exception: return None, None
        ex = [n for n in items if re.search(r"ex-?99|ex99|q\d.*\.htm|earnings|press", n, re.I) and n.endswith(".htm")]
        if not ex: return None, None
        subprocess.run(["curl", "-s", "-A", UA, "-o", str(f), base + ex[0]]); time.sleep(.3)
        (PR / f"{t}_{acc}.url").write_text(base + ex[0])
    return f, (PR / f"{t}_{acc}.url").read_text() if (PR / f"{t}_{acc}.url").exists() else None
def verify(f, rev_bn):
    if f is None or pd.isna(rev_bn): return None
    b = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", f.read_text("utf-8", "ignore"))))
    nums = [float(x.replace(",", "")) for x in re.findall(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\.\d+\b", b)]
    tgt = rev_bn
    for n in nums:
        for scale in (1, 1e-3, 1e-6):  # 十亿/百万/千 表示
            if abs(n * scale - tgt) / tgt < 0.006: return True
    return False
def main():
    d = pd.read_csv(RAW / "parsed_stage1.csv")
    rows = []
    for _, r in d.iterrows():
        if r.ticker == "TSMC" or pd.isna(r.get("rev_actual_bn")) and pd.isna(r.get("eps_actual")): continue
        f, purl = press(r.ticker, r.accession)
        g = G.search(r.guide_text) if isinstance(r.guide_text, str) else None
        rows.append({"ticker": r.ticker, "event_date_et": r.filing_date, "eps_actual": r.eps_actual, "eps_cons_lseg": r.eps_cons,
            "eps_surprise_pct": (r.eps_actual / r.eps_cons - 1) * 100 if r.eps_cons and not pd.isna(r.eps_cons) and r.eps_cons > 0 else np.nan,
            "rev_actual_bn": r.rev_actual_bn, "rev_cons_lseg_bn": r.rev_cons_bn,
            "rev_surprise_pct": (r.rev_actual_bn / r.rev_cons_bn - 1) * 100 if not pd.isna(r.rev_cons_bn) else np.nan,
            "guide_rev_bn": float(g.group(1)) if g else np.nan, "guide_cons_bn": float(g.group(2)) if g else np.nan,
            "guide_surprise_pct": (float(g.group(1)) / float(g.group(2)) - 1) * 100 if g else np.nan,
            "guide_text": r.guide_text if g else None, "capex_text": r.capex_text if r.ticker in ("MSFT", "GOOGL", "META", "AMZN") else None,
            "capex_dir": None, "cnbc_src": r.eps_src if isinstance(r.eps_src, str) else r.rev_src,
            "press_release_src": purl, "actual_rev_in_press_release": verify(f, r.rev_actual_bn)})
    # TSMC：官方指引库（实际−指引中值），不用 CNBC
    ts = pd.read_csv(D / "tsmc_revenue_vs_guidance.csv").dropna(subset=["report_date"])
    for _, r in ts.iterrows():
        rows.append({"ticker": "TSMC", "event_date_et": r.report_date, "rev_actual_bn": r.actual_usd_bn, "rev_cons_lseg_bn": np.nan,
                     "rev_surprise_pct": r.surprise_vs_mid_pct, "cnbc_src": None, "press_release_src": r.actual_source,
                     "actual_rev_in_press_release": True, "note": "TSMC 用实际−官方指引中值，非 LSEG"})
    df = pd.DataFrame(rows).sort_values(["event_date_et", "ticker"])
    df.to_csv(D / "ai_chain_earnings_surprise.csv", index=False)
    print(len(df), df.ticker.value_counts().to_dict()); print("press verified:", df.actual_rev_in_press_release.value_counts(dropna=False).to_dict())
    print("guide parsed:", df.guide_surprise_pct.notna().sum())
    print(df[["ticker", "event_date_et", "eps_surprise_pct", "rev_surprise_pct", "guide_surprise_pct", "actual_rev_in_press_release"]].round(2).to_string())
if __name__ == "__main__": main()
