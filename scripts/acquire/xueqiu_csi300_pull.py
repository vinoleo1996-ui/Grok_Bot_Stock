#!/usr/bin/env python3
"""Xueqiu CSI300 discussion pull scaffold (research-grade).

- Polite rate limit (default 2.5-4s jitter)
- WAF/HTML detection -> exit non-zero, no mass crawl
- Checkpoint + append parquet
- available_at = created_at -> Asia/Shanghai; record first_captured_at
- Do NOT claim full history; shallow window only

Usage:
  python3 scripts/acquire/xueqiu_csi300_pull.py --dry-probe
  python3 scripts/acquire/xueqiu_csi300_pull.py --max-symbols 5 --pages 1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
import urllib.request
import http.cookiejar
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data/v2/text/xueqiu"
OUT_PARQUET = OUT_DIR / "csi300_posts_pit.parquet"
CKPT = OUT_DIR / "pull_checkpoint.json"
SYMBOLS = OUT_DIR / "csi300_symbols.txt"
SH = ZoneInfo("Asia/Shanghai")
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def is_waf_or_html(body: bytes, content_type: str) -> bool:
    head = body[:800].decode("utf-8", errors="replace")
    ct = (content_type or "").lower()
    if "text/html" in ct:
        return True
    low = head.lower()
    if low.lstrip().startswith("<!doctype") or "<html" in low[:200]:
        return True
    if "_waf_" in low or "aliyun" in low or "acw_sc" in low:
        return True
    return False


def looks_json(body: bytes) -> bool:
    s = body.lstrip()[:1]
    return s in b"{["


def fetch(opener, url: str, referer: str, timeout: float = 20):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": referer,
            "Origin": "https://xueqiu.com",
        },
    )
    with opener.open(req, timeout=timeout) as r:
        body = r.read()
        ct = r.headers.get("Content-Type", "")
        return r.status, ct, body


def xq_symbol(ts_code: str) -> str:
    code, mkt = ts_code.split(".")
    return ("SH" if mkt == "SH" else "SZ" if mkt == "SZ" else "BJ") + code


def ts_from_xq(sym: str) -> str:
    if sym.startswith("SH"):
        return sym[2:] + ".SH"
    if sym.startswith("SZ"):
        return sym[2:] + ".SZ"
    if sym.startswith("BJ"):
        return sym[2:] + ".BJ"
    return sym


def sleep_polite(lo: float, hi: float):
    time.sleep(random.uniform(lo, hi))


def load_symbols(path: Path) -> list:
    if path.exists():
        return [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    mp = OUT_DIR / "csi300_members_latest.parquet"
    if not mp.exists():
        raise SystemExit("missing symbols: %s and %s" % (path, mp))
    df = pd.read_parquet(mp)
    return [xq_symbol(c) for c in df["con_code"].tolist()]


def parse_statuses(payload: dict, symbol: str, captured_at: datetime) -> list:
    items = (
        payload.get("list")
        or payload.get("statuses")
        or (payload.get("data") or {}).get("list")
        or []
    )
    rows = []
    for it in items:
        if not isinstance(it, dict):
            continue
        pid = it.get("id") or it.get("status_id")
        created_ms = it.get("created_at")
        publish_at = None
        if isinstance(created_ms, (int, float)):
            publish_at = datetime.fromtimestamp(created_ms / 1000.0, tz=timezone.utc).astimezone(SH)
        title = it.get("title") or ""
        text = it.get("text") or it.get("description") or ""
        if "<" in str(text):
            text = re.sub(r"<[^>]+>", " ", str(text))
        body = (text or "")[:8000]
        content = ("%s\n%s" % (title, body)).strip()
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        user = it.get("user") or {}
        url = it.get("target")
        if not url and pid is not None:
            url = "https://xueqiu.com/%s/%s" % (user.get("id") or "", pid)
        rows.append(
            {
                "post_id": str(pid) if pid is not None else None,
                "instrument": ts_from_xq(symbol),
                "symbol": symbol,
                "title": title or None,
                "body_text": body or None,
                "url": url,
                "author": user.get("screen_name") or it.get("user_name"),
                "author_id": str(user.get("id")) if user.get("id") is not None else None,
                "publish_at": publish_at,
                "available_at": publish_at,
                "first_captured_at": captured_at,
                "source": "xueqiu",
                "like_count": it.get("like_count") or it.get("fav_count"),
                "reply_count": it.get("reply_count"),
                "retweet_count": it.get("retweet_count"),
                "fav_count": it.get("fav_count"),
                "feed_type": "symbol_status",
                "captured_at": captured_at,
                "content_sha256": sha,
                "is_deleted": False,
                "promotion_approved": False,
            }
        )
    return rows


def write_blocked(msg: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / "BLOCKED.md"
    p.write_text(
        "# Xueqiu WAF block\n\n%s\n\n@ %s\n"
        % (msg, datetime.now().astimezone().isoformat(timespec="seconds")),
        encoding="utf-8",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-probe", action="store_true")
    ap.add_argument("--max-symbols", type=int, default=0)
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--sleep-lo", type=float, default=2.5)
    ap.add_argument("--sleep-hi", type=float, default=4.0)
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    try:
        st, ct, body = fetch(opener, "https://xueqiu.com/", "https://www.google.com/")
    except Exception as e:
        print("FATAL homepage: %s" % e, file=sys.stderr)
        sys.exit(2)
    sleep_polite(args.sleep_lo, args.sleep_hi)

    try:
        st, ct, body = fetch(
            opener,
            "https://xueqiu.com/statuses/hot/listV2.json?since_id=-1&max_id=-1&size=5",
            "https://xueqiu.com/",
        )
    except Exception as e:
        print("FATAL hot: %s" % e, file=sys.stderr)
        sys.exit(2)

    if is_waf_or_html(body, ct) or not looks_json(body):
        write_blocked("hot status=%s ct=%s head=%r" % (st, ct, body[:200]))
        print("WAF/HTML on hot list — abort (see data/v2/text/xueqiu/BLOCKED.md)", file=sys.stderr)
        sys.exit(3)

    if args.dry_probe:
        print("dry-probe hot OK", st, len(body))
        sym = "SH600519"
        sleep_polite(args.sleep_lo, args.sleep_hi)
        st, ct, body = fetch(
            opener,
            "https://xueqiu.com/query/v1/symbol/search/status.json?symbol=%s&count=3&page=1&sort=time&source=all"
            % sym,
            "https://xueqiu.com/S/%s" % sym,
        )
        if is_waf_or_html(body, ct) or not looks_json(body):
            write_blocked("symbol status=%s ct=%s head=%r" % (st, ct, body[:200]))
            print("WAF on symbol — abort", file=sys.stderr)
            sys.exit(3)
        print("dry-probe symbol OK", st, len(body))
        sys.exit(0)

    symbols = load_symbols(SYMBOLS)
    if args.max_symbols > 0:
        symbols = symbols[: args.max_symbols]

    ckpt = {"done": [], "updated": None}
    if CKPT.exists():
        ckpt = json.loads(CKPT.read_text())
    done = set(ckpt.get("done") or [])

    all_rows = []
    for i, sym in enumerate(symbols):
        if sym in done:
            continue
        for page in range(1, args.pages + 1):
            sleep_polite(args.sleep_lo, args.sleep_hi)
            url = (
                "https://xueqiu.com/query/v1/symbol/search/status.json"
                "?symbol=%s&count=20&page=%d&sort=time&source=all" % (sym, page)
            )
            try:
                st, ct, body = fetch(opener, url, "https://xueqiu.com/S/%s" % sym)
            except Exception as e:
                print("error %s p%d: %s" % (sym, page, e), file=sys.stderr)
                CKPT.write_text(json.dumps(ckpt, ensure_ascii=False, indent=2), encoding="utf-8")
                sys.exit(4)
            if is_waf_or_html(body, ct) or not looks_json(body):
                write_blocked("WAF mid-run %s page=%d head=%r" % (sym, page, body[:180]))
                print("WAF mid-run at %s p%d — stop" % (sym, page), file=sys.stderr)
                CKPT.write_text(json.dumps(ckpt, ensure_ascii=False, indent=2), encoding="utf-8")
                sys.exit(3)
            payload = json.loads(body.decode("utf-8", errors="replace"))
            captured = datetime.now(tz=SH)
            all_rows.extend(parse_statuses(payload, sym, captured))
        done.add(sym)
        ckpt["done"] = sorted(done)
        ckpt["updated"] = datetime.now().astimezone().isoformat(timespec="seconds")
        CKPT.write_text(json.dumps(ckpt, ensure_ascii=False, indent=2), encoding="utf-8")
        print("[%d/%d] %s rows_so_far=%d" % (i + 1, len(symbols), sym, len(all_rows)))

    if not all_rows:
        print("no rows pulled")
        sys.exit(0)

    new_df = pd.DataFrame(all_rows)
    if OUT_PARQUET.exists():
        old = pd.read_parquet(OUT_PARQUET)
        merged = pd.concat([old, new_df], ignore_index=True)
        merged = merged.sort_values("first_captured_at").drop_duplicates(subset=["post_id"], keep="first")
    else:
        merged = new_df
    merged.to_parquet(OUT_PARQUET, index=False)
    print("wrote %s rows=%d" % (OUT_PARQUET, len(merged)))


if __name__ == "__main__":
    main()
