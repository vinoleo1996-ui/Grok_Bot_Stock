"""解析 CNBC 财报稿：EPS/营收 实际 vs LSEG 预期、指引 vs 预期、资本开支句子。原文落盘 ai_earn_raw/cnbc/。python3。"""
import json, re, subprocess, time, html, hashlib
from pathlib import Path
import pandas as pd
RAW = Path("/workspace/QuantLab/data/v2/intel_consensus/ai_earn_raw"); AR = RAW / "cnbc"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
def fetch(u):
    f = AR / (hashlib.md5(u.encode()).hexdigest()[:12] + ".htm")
    if not f.exists() or f.stat().st_size < 5000:
        subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-A", UA, "-o", str(f), u]); time.sleep(.8)
    s = f.read_text("utf-8", "ignore") if f.exists() else ""
    m = re.search(r'<div class="ArticleBody-articleBody".*?</div>\s*</div>\s*</div>', s, re.S)
    body = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", s)))
    return body, f.name
NUM = r"\$?(-?[\d,]+(?:\.\d+)?)\s*(billion|million|cents)?"
def val(x, unit):
    v = float(x.replace(",", ""))
    return v / 100 if unit == "cents" else (v / 1000 if unit == "million" else v)
EPS = re.compile(r"(?:Earnings per share|Adjusted earnings per share|Earnings|EPS)\s*:\s*" + NUM + r"[ ,]*(?:a share|per share|adj\.?|adjusted)?[ ,]*(?:\([^)]{0,30}\))?\s*(?:vs\.?|versus)\s*" + NUM + r"\s*(?:a share|per share)?\s*(?:adjusted)?\s*(?:expected|estimated)", re.I)
REV = re.compile(r"Revenue\s*:\s*" + NUM + r"[ ,]*(?:\([^)]{0,30}\))?[ ,]*(?:vs\.?|versus)\s*" + NUM + r"\s*(?:expected|estimated)", re.I)
GUIDE = re.compile(r"([^.]{0,220}(?:guid|forecast|outlook|expects?|sees|projected)[^.]{0,220}(?:LSEG|analysts?)[^.]{0,200}\.)", re.I)
CAPEX = re.compile(r"([^.]{0,200}(?:capital expenditure|capex)[^.]{0,250}\.)", re.I)
SENT = lambda b: [x.strip() + "." for x in re.split(r"(?<=[a-z0-9%)])\. ", b)]
def main():
    cands = json.load(open(RAW / "cnbc_candidates.json")); rows = []
    for e in cands:
        r = {k: e[k] for k in ["ticker", "filing_date", "accession", "primary_doc"]}
        for ti, u in e["cands"][:6]:
            body, fn = fetch(u)
            if "eps_actual" not in r:
                m = EPS.search(body)
                if m: r.update(eps_actual=val(m.group(1), m.group(2)), eps_cons=val(m.group(3), m.group(4)), eps_src=u, eps_raw=fn)
            if "rev_actual_bn" not in r:
                m = REV.search(body)
                if m: r.update(rev_actual_bn=val(m.group(1), m.group(2) or "billion"), rev_cons_bn=val(m.group(3), m.group(4) or "billion"), rev_src=u, rev_raw=fn)
            if "guide_text" not in r:
                g = [x for x in SENT(body) if len(x) < 600 and re.search(r"guid|forecast|outlook|expects?|sees", x, re.I) and re.search(r"LSEG|StreetAccount|FactSet", x)]
                if g: r.update(guide_text=g[0].strip()[:500], guide_src=u)
            if "capex_text" not in r:
                c = [x for x in SENT(body) if len(x) < 600 and re.search(r"capital expenditure|capex", x, re.I)]
                if c: r.update(capex_text=" | ".join(x.strip() for x in c[:2])[:600], capex_src=u)
        rows.append(r)
    df = pd.DataFrame(rows); df.to_csv(RAW / "parsed_stage1.csv", index=False)
    print(len(df), df.eps_actual.notna().sum(), df.rev_actual_bn.notna().sum(), df.guide_text.notna().sum(), df.capex_text.notna().sum())
    print(df.groupby("ticker")[["eps_actual", "rev_actual_bn", "guide_text", "capex_text"]].count())
if __name__ == "__main__": main()
