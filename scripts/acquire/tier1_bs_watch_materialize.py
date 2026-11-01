#!/usr/bin/env python3
"""Watch BS shard pullers; when shards exit, fill misses once, materialize PIT, update docs."""
import sys, os, time, pathlib, json, subprocess, warnings, signal
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
RAW = ROOT / "data/v2/tushare_raw/balancesheet"
LOG = ROOT / "data/_acquire_logs"
DOCS = ROOT / "docs/v2"
TARGET = int(os.environ.get("BS_TARGET", "5800"))
POLL = int(os.environ.get("BS_POLL", "180"))

def count_bs():
    return sum(1 for p in RAW.glob("*.parquet") if p.stat().st_size > 0)

def shards_alive():
    try:
        out = subprocess.check_output(["pgrep", "-f", "scripts/acquire/tier1_bs_shard.py"], text=True)
        pids = [int(x) for x in out.split() if x.strip().isdigit()]
        # exclude this process
        return [p for p in pids if p != os.getpid()]
    except subprocess.CalledProcessError:
        return []

def materialize():
    return subprocess.call([sys.executable, "-u", str(ROOT/"scripts/acquire/tier1_materialize.py"), "bs_cf"], cwd=str(ROOT))

def update_docs(meta):
    bs = meta.get("balancesheet") or {}
    receipt = {
        "task": "tier1_balancesheet_continue",
        "promotion_approved": False,
        "path": bs.get("path"),
        "rows": bs.get("rows"),
        "instruments": bs.get("instruments"),
        "end_date_min": bs.get("end_date_min"),
        "end_date_max": bs.get("end_date_max"),
        "ann_min": bs.get("ann_min"),
        "ann_max": bs.get("ann_max"),
        "available_at_rule": bs.get("available_at_rule"),
        "multi_version_frac": bs.get("multi_version_frac"),
        "max_versions": bs.get("max_versions"),
        "raw_files": count_bs(),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (LOG/"tier1_bs_receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    block = (
        f"\n\n## balancesheet_pit (updated {receipt['updated_at']})\n"
        f"- path: `{receipt.get('path')}`\n"
        f"- instruments: {receipt.get('instruments')} / raw_files: {receipt.get('raw_files')}\n"
        f"- rows: {receipt.get('rows')}\n"
        f"- end_date: {receipt.get('end_date_min')} → {receipt.get('end_date_max')}\n"
        f"- ann: {receipt.get('ann_min')} → {receipt.get('ann_max')}\n"
        f"- available_at: {receipt.get('available_at_rule')}\n"
        f"- multi_version_frac: {receipt.get('multi_version_frac')} (max_versions={receipt.get('max_versions')})\n"
        f"- promotion_approved: false\n"
    )
    for name in ("TIER1_DATA_DELIVERY_20261012.md", "TIER1_DATA_PROGRESS_20261012.md"):
        p = DOCS/name
        if not p.exists():
            continue
        text = p.read_text()
        marker = "## balancesheet_pit"
        if marker in text:
            pre, rest = text.split(marker, 1)
            # rest starts with marker content; drop until next top-level ##
            idx = rest.find("\n## ")
            if idx >= 0:
                text = pre + block.lstrip("\n") + rest[idx:]
            else:
                text = pre + block.lstrip("\n")
        else:
            text = text.rstrip() + block
        p.write_text(text)
    return receipt

def run_fill():
    env = os.environ.copy()
    env.update({"SLEEP": "0.55", "BS_TIMEOUT": "25", "BS_RETRIES": "3"})
    with open(LOG/"tier1_bs_fill.log", "a") as fo:
        fo.write(f"\n==== FILL {time.strftime('%Y-%m-%dT%H:%M:%S')} ====\n")
        fo.flush()
        p = subprocess.Popen(
            [sys.executable, "-u", str(ROOT/"scripts/acquire/tier1_bs_shard.py"), "0", "1"],
            cwd=str(ROOT), env=env, stdout=fo, stderr=subprocess.STDOUT,
        )
    return p

def main():
    print("watch start target", TARGET, "poll", POLL, flush=True)
    last = count_bs()
    print("initial", last, "shards", shards_alive(), flush=True)
    while True:
        time.sleep(POLL)
        n = count_bs()
        alive = shards_alive()
        print(time.strftime("%H:%M:%S"), "bs_files", n, "delta", n-last, "shards", alive, flush=True)
        last = n
        if alive:
            continue
        # shards finished
        print("shards finished at", n, flush=True)
        if n < TARGET:
            print("fill pass for remaining", flush=True)
            p = run_fill()
            while p.poll() is None:
                time.sleep(POLL)
                print(time.strftime("%H:%M:%S"), "fill bs_files", count_bs(), flush=True)
            print("fill exit", p.returncode, "n", count_bs(), flush=True)
        print("materialize...", flush=True)
        rc = materialize()
        print("materialize rc", rc, flush=True)
        man = ROOT/"data/v2/financials_pit/bs_cf_pit_manifest.json"
        meta = json.loads(man.read_text()) if man.exists() else {}
        receipt = update_docs(meta)
        print("RECEIPT", json.dumps(receipt, ensure_ascii=False), flush=True)
        for pid in (3062110, 3062103):
            try:
                os.kill(pid, signal.SIGCONT)
            except Exception:
                pass
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
