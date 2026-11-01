#!/usr/bin/env python3
"""probe5_small — Tushare relay read-only probe (trade_cal / stock_basic limit=100).

Timeouts (Arch pin): connect 15s / read 115s / per-request wall 120s.
BIG_PAGE=5000 retained for big_page_full judgment; stock_basic uses limit=100.

REBUILT 2026-10-25 after box refresh wiped /tmp/relay_probe/.
HARDEN 2026-10-25T0458ET: emit connect/read/wall on every line; use
urllib3.util.Timeout explicitly (0455 receipt showed read timeout=15 while
source READ_S=115 — /tmp slow-server proved child waited 25s>15).
Original pin sha256 601a092fef871e917098cddddeb7c65c17627b804d7e4c2f35f413ef1b5bd77f
was not recoverable (no copy in repo/_recovery/git/Mac-offline). Behavior
matched from 10-18 selftest + 12:50 receipts; bytes will PIN_MISMATCH.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

BIG_PAGE = 5000
CONNECT_S = 15
READ_S = 115
WALL_S = 120
DEFAULT_BASE = "https://pcd.mobcvb.cn/tushare/pro"
DEFAULT_ENV = "/workspace/QuantLab/.env.datasources"
DEFAULT_LOG = "/tmp/relay_probe/probe_log.csv"
STOCK_BASIC_LIMIT = 100  # small-page probe; probe5 used 5000 at this line

# trade_cal short window (similar to historical 20261014–20261020)
TRADE_CAL_PARAMS = {
    "exchange": "SSE",
    "start_date": "20261019",
    "end_date": "20261025",
}
STOCK_BASIC_PARAMS = {
    "list_status": "L",
    "limit": STOCK_BASIC_LIMIT,
    "offset": 0,
}


def _now_et_str() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S")


def _load_key(env_file: str | None) -> str:
    key = os.environ.get("TSPRO_PROXY_KEY", "").strip()
    if key:
        return key
    path = Path(env_file or DEFAULT_ENV)
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() == "TSPRO_PROXY_KEY":
            return v.strip().strip('"').strip("'")
    return ""


def _count_rows(payload) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return len(items)
        data = payload.get("data")
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return len(data["items"])
    return 0


def _child_request(api: str, base_url: str, key: str) -> None:
    """Child process: one HTTP GET, print one JSON result line, exit 0."""
    import requests  # local import; never import QuantLab project code

    params = dict(TRADE_CAL_PARAMS if api == "trade_cal" else STOCK_BASIC_PARAMS)
    url = base_url.rstrip("/") + "/" + api
    headers = {"X-API-Key": key}
    t0 = time.monotonic()
    http_status = ""
    rows = ""
    error = ""
    # Explicit Timeout object — never a bare int (avoids ambiguous logs).
    from urllib3.util import Timeout as Urllib3Timeout
    req_timeout = Urllib3Timeout(connect=CONNECT_S, read=READ_S)
    assert CONNECT_S == 15 and READ_S == 115 and WALL_S == 120, (
        CONNECT_S, READ_S, WALL_S
    )
    try:
        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=req_timeout,
        )
        http_status = str(r.status_code)
        try:
            payload = r.json()
            rows = str(_count_rows(payload))
        except Exception as je:  # noqa: BLE001
            error = f"JSONError: {je}"[:300]
            rows = ""
    except Exception as e:  # noqa: BLE001
        error = f"{type(e).__name__}: {e}"[:400]
    elapsed = round(time.monotonic() - t0, 2)
    out = {
        "api": api,
        "elapsed_s": elapsed,
        "http_status": http_status,
        "rows": rows,
        "error": error,
        "params": params,
        "timeouts": {"connect_s": CONNECT_S, "read_s": READ_S, "wall_s": WALL_S},
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    # child always exits 0; parent encodes probe outcome
    raise SystemExit(0)


def _append_csv(log_path: str, row: dict) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "ts_et",
                "api",
                "params",
                "elapsed_s",
                "http_status",
                "rows",
                "error",
            ],
        )
        if new:
            w.writeheader()
        w.writerow(row)


def _run_parent(api: str, base_url: str, env_file: str | None, log_path: str) -> int:
    key = _load_key(env_file)
    if not key:
        ts = _now_et_str()
        msg = "BLOCKED_NO_KEY"
        line = f"{ts} {api} 0   {msg} timeouts={CONNECT_S}/{READ_S}/{WALL_S} child_pid=0 rc=1"
        if api == "stock_basic":
            line += " big_page_full=False"
        print(line)
        if api == "stock_basic":
            print("RESULT stock_basic big_page_full=False")
        return 1

    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--as-child",
        "--only",
        api,
        "--base-url",
        base_url,
    ]
    # pass key via env only (never argv / never print)
    child_env = os.environ.copy()
    child_env["TSPRO_PROXY_KEY"] = key
    # drop env-file path from child; key already in env
    t0 = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        env=child_env,
        text=True,
    )
    child_pid = proc.pid
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=WALL_S)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            proc.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            stdout, stderr = proc.communicate()
    rc = proc.returncode
    if rc is None:
        rc = -1
    elapsed_wall = round(time.monotonic() - t0, 2)

    http_status = ""
    rows = ""
    error = ""
    params = dict(TRADE_CAL_PARAMS if api == "trade_cal" else STOCK_BASIC_PARAMS)
    elapsed = elapsed_wall

    if timed_out:
        error = "wall_timeout_120s (term_sent)"
        if rc >= 0:
            # SIGTERM often surfaces as -15
            pass
    else:
        raw = (stdout or "").strip().splitlines()
        parsed = None
        for line in reversed(raw):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
        if parsed is None:
            err_bits = (stderr or "").strip()[:200]
            error = err_bits or "no_child_json"
        else:
            elapsed = parsed.get("elapsed_s", elapsed_wall)
            http_status = str(parsed.get("http_status") or "")
            rows = str(parsed.get("rows") if parsed.get("rows") is not None else "")
            error = str(parsed.get("error") or "")
            if isinstance(parsed.get("params"), dict):
                params = parsed["params"]

    ts = _now_et_str()
    # stdout format aligned with historical receipts:
    # YYYY-mm-dd HH:MM:SS <api> <elapsed> <http> <rows> [error] child_pid=… rc=… [big_page_full=…]
    line = (
        f"{ts} {api} {elapsed} {http_status} {rows} {error} "
        f"timeouts={CONNECT_S}/{READ_S}/{WALL_S} child_pid={child_pid} rc={rc}"
    )

    big_page_full = False
    if api == "stock_basic":
        try:
            big_page_full = bool(rows) and int(rows) >= BIG_PAGE
        except ValueError:
            big_page_full = False
        line += f" big_page_full={big_page_full}"

    print(line)
    if api == "stock_basic":
        print(f"RESULT stock_basic big_page_full={big_page_full}")

    _append_csv(
        log_path,
        {
            "ts_et": ts,
            "api": api,
            "params": json.dumps(params, ensure_ascii=False, separators=(",", ":")),
            "elapsed_s": elapsed,
            "http_status": http_status,
            "rows": rows,
            "error": error,
        },
    )

    if api == "stock_basic":
        return 0 if big_page_full else 2
    # trade_cal: 0 only on clear success
    ok = (
        http_status == "200"
        and rows not in ("", "0")
        and not error
        and not timed_out
    )
    return 0 if ok else 1


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Relay probe5_small: trade_cal / stock_basic(limit=100). "
            f"timeouts connect={CONNECT_S}s read={READ_S}s wall={WALL_S}s; "
            f"BIG_PAGE={BIG_PAGE}."
        )
    )
    p.add_argument(
        "--only",
        choices=("trade_cal", "stock_basic"),
        required=False,
        help="Run a single API once (no retry).",
    )
    p.add_argument("--base-url", default=DEFAULT_BASE, help="Relay base URL")
    p.add_argument(
        "--env-file",
        default=DEFAULT_ENV,
        help="Env file containing TSPRO_PROXY_KEY (never printed)",
    )
    p.add_argument(
        "--log-path",
        default=DEFAULT_LOG,
        help="CSV append path (ts_et,api,params,elapsed_s,http_status,rows,error)",
    )
    p.add_argument(
        "--as-child",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.as_child:
        if not args.only:
            print("child requires --only", file=sys.stderr)
            return 2
        key = os.environ.get("TSPRO_PROXY_KEY", "").strip()
        _child_request(args.only, args.base_url, key)
        return 0
    if not args.only:
        parser.error("--only is required (trade_cal|stock_basic)")
    return _run_parent(args.only, args.base_url, args.env_file, args.log_path)


if __name__ == "__main__":
    raise SystemExit(main())
