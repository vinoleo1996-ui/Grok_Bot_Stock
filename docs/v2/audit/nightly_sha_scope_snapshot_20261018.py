#!/usr/bin/env python3
# stdlib only. usage:
#   sha_scope_snapshot.py SCOPE OUT_TMP        -> writes snapshot (sha256sum-format lines + # meta lines) to OUT_TMP
#   sha_scope_snapshot.py --compare SCOPE BEFORE AFTER -> exit 0 ok, 1 MUST_NOT_CHANGE diff, 2 usage/missing
import hashlib, json, os, subprocess, sys, datetime, zoneinfo
ET = zoneinfo.ZoneInfo("America/New_York")
def scope(p):
    cls = None; out = []
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("# =====") and "[EXPECTED_CHANGE]" in ln: cls = "EXPECTED_CHANGE"
        elif ln.startswith("# =====") and "[MUST_NOT_CHANGE]" in ln: cls = "MUST_NOT_CHANGE"
        if not ln or ln.startswith("#"): continue
        out.append((ln, cls))
    return out
def snap(sc, out):
    items = scope(sc)
    paths = [p for p, _ in items]
    t0 = datetime.datetime.now(ET)
    r = subprocess.run(["sha256sum", "--"] + paths, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr); sys.exit(2)
    t1 = datetime.datetime.now(ET)
    L = ["# sha baseline, scope=%s scope_sha256=%s" % (sc, hashlib.sha256(open(sc, "rb").read()).hexdigest()),
         "# started_et=%s finished_et=%s host_tool=sha256sum (coreutils) via stdlib wrapper" % (t0.isoformat(timespec="seconds"), t1.isoformat(timespec="seconds")),
         "# format: sha256sum lines, then one \"# meta\" line per file: class<TAB>size<TAB>mtime_ns<TAB>ctime_ns<TAB>inode<TAB>path"]
    L += r.stdout.rstrip("\n").split("\n")
    tot = 0
    for p, c in items:
        s = os.stat(p); tot += s.st_size
        L.append("# meta\t%s\t%d\t%d\t%d\t%d\t%s" % (c, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino, p))
    L.append("# files=%d total_bytes=%d" % (len(items), tot))
    open(out, "w").write("\n".join(L) + "\n")
    print("files", len(items), "total_bytes", tot, "t0", t0.isoformat(timespec="seconds"), "t1", t1.isoformat(timespec="seconds"))
def load(p):
    h = {}; m = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("# meta\t"):
            f = ln.split("\t"); m[f[6]] = f[1:6]
        elif ln and not ln.startswith("#"):
            s, path = ln.split("  ", 1); h[path] = s
    return h, m
def compare(sc, b, a):
    items = scope(sc); hb, mb = load(b); ha, ma = load(a); bad = 0
    for p, c in items:
        if p not in hb or p not in ha: print("MISSING", p); bad = 2; continue
        same = hb[p] == ha[p]
        if not same:
            print("DIFF", c, p, hb[p][:12], "->", ha[p][:12])
            if c == "MUST_NOT_CHANGE": bad = max(bad, 1)
        elif mb[p][2:5] != ma[p][2:5] and c == "MUST_NOT_CHANGE":
            print("META_ONLY_CHANGE (sha same, mtime/ctime/inode differ)", p)
    print("RESULT", {0: "OK", 1: "MUST_NOT_CHANGE_DIFF_STOP", 2: "MISSING"}[bad]); sys.exit(bad)
if sys.argv[1] == "--compare": compare(sys.argv[2], sys.argv[3], sys.argv[4])
else: snap(sys.argv[1], sys.argv[2])
