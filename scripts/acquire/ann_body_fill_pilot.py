"""Fill body_text for high-value anns from cninfo PDF (poppler) / EM HTML.
Priority: CSI300/500 + event_type in buyback/insider_*/inquiry_*/penalty.
available_at UNCHANGED (disclosure clock). body_source=cninfo_pdf|em_html|pdf_trunc_Nk.
Env: MAX_DOCS(200) SLEEP(0.8) MAX_CHARS(16000)
"""
import os, re, time, json, hashlib, pathlib, subprocess, tempfile, random
import requests, pandas as pd

ROOT = pathlib.Path("/workspace/QuantLab")
CORPUS = ROOT / "data/v2/text/ann_embedding_corpus_pit.parquet"
OUT = ROOT / "data/v2/text/ann_embedding_corpus_pit_with_body.parquet"
COV = ROOT / "output/d1/ANN_BODY_FILL_COVERAGE.md"
LOG = open(ROOT / "logs/ann_body_fill.log", "a", buffering=1)
MAX_DOCS = int(os.environ.get("MAX_DOCS", "200"))
SLEEP = float(os.environ.get("SLEEP", "0.8"))
MAX_CHARS = int(os.environ.get("MAX_CHARS", "16000"))
HI = {"buyback", "insider_decrease", "insider_increase", "inquiry_reply", "inquiry_letter", "penalty", "earnings_beat", "earnings_miss"}
H = {"User-Agent": "Mozilla/5.0"}

def mem_gb():
    return int(open("/proc/meminfo").read().split("MemAvailable:")[1].split()[0]) / 1024 / 1024

def pdf_text(url):
    r = requests.get(url, headers=H, timeout=20)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        p = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=60)
        txt = p.stdout.decode("utf-8", errors="replace")
    finally:
        pathlib.Path(path).unlink(missing_ok=True)
    return txt

def em_html_text(url):
    r = requests.get(url, headers=H, timeout=20)
    r.raise_for_status()
    html = r.text
    # crude strip
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    html = re.sub(r"(?is)<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html).strip()
    return html

def main():
    print(f"START mem={mem_gb():.1f}G MAX_DOCS={MAX_DOCS}", flush=True)
    df = pd.read_parquet(CORPUS)
    # priority members
    pr = set()
    pf = ROOT / "data/v2/announcements/cninfo/priority_csi300_500.txt"
    if pf.exists():
        pr = set(pf.read_text().split())
    need = df[df.body_text.isna() | (df.body_text.astype(str).str.len() == 0)].copy()
    need = need[need.event_type.isin(HI)]
    if pr:
        need = need[need.instrument.isin(pr) | need.ts_code.isin(pr)]
    # prefer cninfo PDF urls
    need["is_pdf"] = need.url.astype(str).str.contains(r"\.PDF|\.pdf|static\.cninfo", regex=True, na=False)
    need["pre_seal"] = pd.to_datetime(need.available_at).dt.tz_localize(None) < pd.Timestamp("2024-06-01")
    need = need.sort_values(["is_pdf", "pre_seal", "available_at"], ascending=[False, False, True]).head(MAX_DOCS)
    print(f"candidates {len(need)}", flush=True)

    filled = 0
    fail_streak = 0
    bodies = {}
    sources = {}
    for i, row in need.iterrows():
        if mem_gb() < 1.5:
            print("LOW_MEM stop", flush=True)
            break
        url = str(row.url)
        if url.startswith("http://static.cninfo.com.cn"):
            url = "https://" + url[len("http://"):]
        eid = row.event_id
        try:
            if "cninfo" in url or url.lower().endswith(".pdf"):
                txt = pdf_text(url)
                src = "cninfo_pdf"
            else:
                txt = em_html_text(url)
                src = "em_html"
            if not txt or len(txt.strip()) < 20:
                raise RuntimeError("empty body")
            if len(txt) > MAX_CHARS:
                txt = txt[:MAX_CHARS]
                src = f"{src}_trunc_{MAX_CHARS//1000}k"
            bodies[eid] = txt
            sources[eid] = src
            filled += 1
            fail_streak = 0
            LOG.write(f"OK {eid} {src} {len(txt)}\n")
        except Exception as e:
            fail_streak += 1
            LOG.write(f"FAIL {eid} {url[:80]} {e}\n")
            if fail_streak >= 15 and filled == 0:
                print("ALL_FAIL early stop", flush=True)
                break
        time.sleep(SLEEP + random.random() * 0.3)
        if filled % 20 == 0 and filled:
            print(f"filled {filled}/{len(need)}", flush=True)

    if not bodies:
        print("NO_BODIES", flush=True)
        return 1

    df = df.copy()
    m = df.event_id.map(bodies)
    s = df.event_id.map(sources)
    df.loc[m.notna(), "body_text"] = m[m.notna()]
    df.loc[s.notna(), "body_source"] = s[s.notna()]
    # do NOT touch available_at
    tmp = pathlib.Path(str(OUT) + ".tmp")
    df.to_parquet(tmp, index=False)
    tmp.replace(OUT)
    # also update main corpus body where filled (optional merge)
    rate = float(df.body_text.notna().mean())
    n_body = int(df.body_text.notna().sum())
    md = f"""# 公告正文补齐试点

| 项 | 值 |
|---|---|
| 本轮尝试 | {len(need)} |
| 成功填入 | {filled} |
| 产出 | `{OUT}` |
| 全表有正文率 | {rate:.4%} ({n_body}/{len(df)}) |
| available_at | **未改**（披露时钟） |

**End.**
"""
    COV.write_text(md)
    print(json.dumps({"filled": filled, "tried": len(need), "body_rate": rate, "out": str(OUT)}, ensure_ascii=False), flush=True)
    print("BODY_PILOT_DONE", flush=True)

if __name__ == "__main__":
    main()
