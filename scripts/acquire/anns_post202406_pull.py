"""Pull announcements 2024-06-01 → today for priority universe (CSI300/500 hist ∪ float top1500).
Primary: EastMoney (page_size=100, faster). Parallel-friendly cninfo for PDF URLs on CSI subset.
Does NOT touch sealed-window by_stock dirs or v3_queue. Research-only.
Env: EM_SLEEP(0.5) CNINFO_SLEEP(0.8) WORKERS(2) PRIORITY_FILE PRIORITY_ONLY_CSI=0
"""
import os, sys, time, json, random, threading, pathlib, collections, hashlib
import requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

ROOT = pathlib.Path("/workspace/QuantLab")
EM_OUT = ROOT / "data/v2/announcements/eastmoney/by_stock_post202406"
CN_OUT = ROOT / "data/v2/announcements/cninfo/by_stock_post202406"
EM_OUT.mkdir(parents=True, exist_ok=True)
CN_OUT.mkdir(parents=True, exist_ok=True)
LOG = open(ROOT / "logs/anns_post202406.log", "a", buffering=1)
SE_A, SE_B = "2024-06-01", date.today().isoformat()
EM_SLEEP = float(os.environ.get("EM_SLEEP", "0.5"))
CN_SLEEP = float(os.environ.get("CNINFO_SLEEP", "0.8"))
W = int(os.environ.get("WORKERS", "2"))
PF = pathlib.Path(os.environ.get("PRIORITY_FILE", str(ROOT / "data/v2/announcements/cninfo/priority_post202406.txt")))
CSI_ONLY = os.environ.get("PRIORITY_ONLY_CSI", "0") == "1"

H = {"User-Agent": "Mozilla/5.0", "Referer": "https://data.eastmoney.com/"}
H_CN = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
}

def load_ids():
    ids = [x.strip() for x in PF.read_text().split() if x.strip()]
    if CSI_ONLY:
        csi = set()
        iw = ROOT / "data/v2/tushare_raw/index_weight"
        for pat in ("000300_SH_*.parquet", "000905_SH_*.parquet"):
            for f in iw.glob(pat):
                d = pd.read_parquet(f)
                if len(d) == 0:
                    continue
                col = "con_code" if "con_code" in d.columns else "ts_code"
                for c in d[col].astype(str):
                    code, ex = c.split(".")
                    csi.add(f"{ex.lower()}.{code}")
        ids = [i for i in ids if i in csi] or ids
    # CSI first: those in priority_csi300_500 or index_weight style
    pr = set()
    pfold = ROOT / "data/v2/announcements/cninfo/priority_csi300_500.txt"
    if pfold.exists():
        for c in pfold.read_text().split():
            code, ex = c.split(".")
            pr.add(f"{ex.lower()}.{code}")
    ids = [i for i in ids if i in pr] + [i for i in ids if i not in pr]
    return ids

def mem_ok():
    try:
        free = int(open("/proc/meminfo").read().split("MemAvailable:")[1].split()[0])  # kB
        return free / 1024 / 1024  # GB
    except Exception:
        return 4.0

# ---- EastMoney ----
_sess_em = threading.local()
_win_em = collections.deque(maxlen=40)
_lock = threading.Lock()

def sess_em():
    if not hasattr(_sess_em, "s"):
        _sess_em.s = requests.Session()
        _sess_em.s.headers.update(H)
    return _sess_em.s

def em_get(code, page):
    global EM_SLEEP
    for i in range(7):
        ok = False
        try:
            r = sess_em().get(
                "https://np-anotice-stock.eastmoney.com/api/security/ann",
                params=dict(
                    sr=-1, page_size=100, page_index=page, ann_type="A",
                    client_source="web", stock_list=code, f_node=0, s_node=0,
                ),
                timeout=25,
            )
            if r.status_code == 200:
                d = r.json().get("data") or {}
                ok = True
            else:
                LOG.write(f"EM_HTTP {r.status_code} {code} p{page}\n")
                d = {}
        except Exception as e:
            LOG.write(f"EM_ERR {code} p{page} {str(e)[:80]}\n")
            d = {}
        with _lock:
            _win_em.append(ok)
            if len(_win_em) >= 20 and _win_em.count(False) / len(_win_em) > 0.2:
                EM_SLEEP = min(5.0, EM_SLEEP * 2)
                LOG.write(f"EM_BACKOFF sleep={EM_SLEEP}\n")
                _win_em.clear()
                time.sleep(60)
        time.sleep(EM_SLEEP + random.random() * 0.3)
        if ok:
            return d
        time.sleep(min(120, 3 * 2**i))
    raise RuntimeError(f"em giveup {code}")

def pull_em(iid):
    fn = EM_OUT / f"{iid}.parquet"
    if fn.exists() and fn.stat().st_size > 50:
        return "skip", 0
    code = iid.split(".")[1]
    rows, page = [], 1
    while page <= 80:
        d = em_get(code, page)
        L = d.get("list") or []
        for x in L:
            nd = str(x.get("notice_date", ""))[:10]
            if SE_A <= nd <= SE_B:
                rows.append({
                    "title": x.get("title"),
                    "notice_date": nd,
                    "display_time": x.get("display_time"),
                    "art_code": x.get("art_code"),
                    "column": ";".join(c.get("column_name", "") for c in (x.get("columns") or [])),
                    "secName": (x.get("codes") or [{}])[0].get("short_name"),
                })
        if not L:
            break
        last = str(L[-1].get("notice_date", ""))[:10]
        if last < SE_A or len(L) < 100:
            break
        page += 1
    df = pd.DataFrame(rows, columns=["title", "notice_date", "display_time", "art_code", "column", "secName"])
    df["instrument"] = iid
    df.astype(str).to_parquet(fn, index=False)
    return "ok", len(df)

# ---- Cninfo (PDF URLs) ----
_sess_cn = threading.local()
_win_cn = collections.deque(maxlen=40)
_om = None

def orgmap():
    global _om
    if _om is not None:
        return _om
    f = ROOT / "data/v2/announcements/cninfo/szse_stock.json"
    if not f.exists():
        f.write_text(requests.get("https://www.cninfo.com.cn/new/data/szse_stock.json", headers=H_CN, timeout=30).text)
    _om = {d["code"]: d["orgId"] for d in json.load(open(f))["stockList"]}
    return _om

def sess_cn():
    if not hasattr(_sess_cn, "s"):
        _sess_cn.s = requests.Session()
        _sess_cn.s.headers.update(H_CN)
    return _sess_cn.s

def cn_page(stock, n):
    global CN_SLEEP
    data = dict(
        pageNum=n, pageSize=30, column="szse", tabName="fulltext", plate="",
        stock=stock, searchkey="", secid="", category="", trade="",
        seDate=f"{SE_A}~{SE_B}", sortName="", sortType="", isHLtitle="false",
    )
    for i in range(7):
        try:
            r = sess_cn().post("https://www.cninfo.com.cn/new/hisAnnouncement/query", data=data, timeout=30)
            time.sleep(CN_SLEEP + random.random() * 0.3)
            ok = r.status_code == 200
            with _lock:
                _win_cn.append(ok)
                if len(_win_cn) >= 20 and _win_cn.count(False) / len(_win_cn) > 0.2:
                    CN_SLEEP = min(5.0, CN_SLEEP * 2)
                    LOG.write(f"CN_BACKOFF sleep={CN_SLEEP}\n")
                    _win_cn.clear()
                    time.sleep(60)
            if ok:
                return r.json()
            LOG.write(f"CN_HTTP {r.status_code} {stock} p{n}\n")
        except Exception as e:
            with _lock:
                _win_cn.append(False)
            LOG.write(f"CN_ERR {stock} p{n} {str(e)[:100]}\n")
        time.sleep(min(120, 3 * 2**i))
    raise RuntimeError(f"cn giveup {stock}")

def pull_cn(iid):
    fn = CN_OUT / f"{iid}.parquet"
    if fn.exists() and fn.stat().st_size > 50:
        return "skip", 0
    om = orgmap()
    ex, code = iid.split(".")
    org = om.get(code) or {"sh": "gssh0", "sz": "gssz0", "bj": "gfbj0"}.get(ex.lower(), "gssz0") + code
    rows, n = [], 1
    while n <= 200:
        d = cn_page(f"{code},{org}", n)
        a = d.get("announcements") or []
        rows += a
        if not d.get("hasMore") or not a:
            break
        n += 1
    df = pd.DataFrame(rows)
    keep = [c for c in ["secCode", "secName", "orgId", "announcementId", "announcementTitle",
                        "announcementTime", "adjunctUrl", "columnId", "pageColumn"] if c in df.columns]
    df = df[keep] if len(df) else pd.DataFrame(columns=keep)
    df["instrument"] = iid
    for c in keep:
        if c != "announcementTime" and c in df.columns:
            df[c] = df[c].astype(str)
    df.to_parquet(fn, index=False)
    return "ok", len(df)

def main():
    mode = os.environ.get("MODE", "em")  # em | cninfo | both
    ids = load_ids()
    print(f"START mode={mode} n={len(ids)} SE={SE_A}~{SE_B} workers={W} mem={mem_ok():.1f}GB", flush=True)
    LOG.write(f"START mode={mode} n={len(ids)} SE={SE_A}~{SE_B}\n")

    def run(fn, label):
        workers = W
        if mem_ok() < 1.5:
            workers = 1
            print(f"LOW_MEM -> workers=1", flush=True)
        ok = skip = fail = rows = 0
        with ThreadPoolExecutor(workers) as ex:
            futs = {ex.submit(fn, i): i for i in ids}
            for k, fut in enumerate(as_completed(futs)):
                iid = futs[fut]
                try:
                    st, n = fut.result()
                    if st == "skip":
                        skip += 1
                    else:
                        ok += 1
                        rows += n
                except Exception as e:
                    fail += 1
                    LOG.write(f"FAIL {label} {iid} {e}\n")
                if k % 25 == 0 or k + 1 == len(ids):
                    print(
                        time.strftime("%H:%M:%S"),
                        f"{label} {k+1}/{len(ids)} ok={ok} skip={skip} fail={fail} rows={rows} mem={mem_ok():.1f}G",
                        flush=True,
                    )
                    if mem_ok() < 1.5:
                        print("LOW_MEM pause 30s", flush=True)
                        time.sleep(30)
        print(f"DONE {label} ok={ok} skip={skip} fail={fail} rows={rows}", flush=True)

    if mode in ("em", "both"):
        run(pull_em, "EM")
    if mode in ("cninfo", "both"):
        run(pull_cn, "CN")
    print("ALL_DONE", flush=True)

if __name__ == "__main__":
    main()
