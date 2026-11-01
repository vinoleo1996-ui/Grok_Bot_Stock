#!/usr/bin/env python3
"""Tiny static server for QuantLab data progress dashboard.

Serves /workspace/QuantLab/output/d1 on 0.0.0.0:8765.
Regenerates the dashboard every refresh if --regen is set (default on).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path("/workspace/QuantLab")
OUT = ROOT / "output" / "d1"
DASH = ROOT / "scripts" / "data_progress_dashboard.py"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/data_progress.html"
        return super().do_GET()


def regen_loop(interval: float, stop: threading.Event):
    while not stop.is_set():
        try:
            subprocess.run([sys.executable, str(DASH)], cwd=str(ROOT), check=False, timeout=120)
        except Exception as e:
            print("regen error:", e, file=sys.stderr)
        stop.wait(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--regen-every", type=float, default=15.0)
    ap.add_argument("--no-regen", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    # initial build
    subprocess.run([sys.executable, str(DASH)], cwd=str(ROOT), check=False)

    stop = threading.Event()
    if not args.no_regen and args.regen_every > 0:
        t = threading.Thread(target=regen_loop, args=(args.regen_every, stop), daemon=True)
        t.start()

    handler = partial(Handler, directory=str(OUT))
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"serving {OUT} on http://{args.host}:{args.port}/  (data_progress.html)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        httpd.server_close()


if __name__ == "__main__":
    main()
