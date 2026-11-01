"""美国 CPI 一致预期库（2024-06 起）。来源：ForexFactory 日历日页面（每条带 URL），原始 HTML 落盘可复核。
研究级，live=false。用 python3 运行（仅标准库 + pandas）。"""
import re, subprocess, time, json, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import pandas as pd
R = Path("/workspace/QuantLab"); D = R / "data/v2/intel_consensus"; RAW = D / "raw"; RAW.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
TITLES = ["Core CPI m/m", "Core CPI y/y", "CPI m/m", "CPI y/y"]
def dates():
    s = sorted((R / "output/intel/pit_candidates").glob("bls_cpi_release_archive_*.htm"))[-1].read_text("utf-8", "ignore")
    d = sorted({y + m + dd for m, dd, y in re.findall(r"cpi_(\d\d)(\d\d)(\d{4})\.htm", s)} | {"20261014"})
    return [x for x in d if x >= "20240601"]
def num(x):
    m = re.search(r"-?\d+(\.\d+)?", x or ""); return float(m.group()) if m else None
def main():
    now = datetime.now(ZoneInfo("America/New_York")); recs = []
    for d in dates():
        dt = pd.Timestamp(d); key = dt.strftime("%b").lower() + str(dt.day) + "." + str(dt.year)
        url = f"https://www.forexfactory.com/calendar?day={key}"; f = RAW / f"ff_{d}.htm"
        if not f.exists() or f.stat().st_size < 50000:
            subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", str(f), url], check=True); time.sleep(2)
        s = f.read_text("utf-8", "ignore")
        for tr in re.split(r"<tr data-event-id=", s)[1:]:
            cur = re.search(r'calendar__currency">\s*([A-Z]{3})', tr); t = re.search(r'calendar__event-title">([^<]+)<', tr)
            if not (cur and t and cur.group(1) == "USD" and t.group(1).strip() in TITLES): continue
            g = lambda c: re.sub("<[^>]+>", "", (re.search(rf'calendar__{c}">(.*?)</td>', tr, re.S) or [None, ""])[1]).strip()
            recs.append({"release_date": dt.date().isoformat(), "release_time_et": "08:30", "indicator": t.group(1).strip(),
                         "actual_pct": num(g("actual")), "consensus_pct": num(g("forecast")), "previous_pct": num(g("previous")),
                         "source": "ForexFactory calendar (forecast column)", "source_url": url, "raw_html": str(f.relative_to(R)),
                         "event_id": tr.split('"')[1], "fetched_et": now.strftime("%Y-%m-%d %H:%M")})
    df = pd.DataFrame(recs).drop_duplicates(["release_date", "indicator"])
    df["surprise_pp"] = (df.actual_pct - df.consensus_pct).round(2)
    df.to_csv(D / "us_cpi_consensus_ff.csv", index=False)
    print(len(df), df.release_date.nunique()); print(df[df.indicator == "Core CPI m/m"][["release_date", "actual_pct", "consensus_pct", "surprise_pp"]].to_string())
if __name__ == "__main__": main()
