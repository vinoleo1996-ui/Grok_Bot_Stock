#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""sha 范围快照 v2（QuantLab Data，2026-10-18；基于 v1 0aa6c650，修 Arch 11cb0690 第 3 节 P2-S1/S2/S3 与 P3）。只用标准库。

用法：
  snap    SCOPE OUT --expect-scope-sha HEX        写快照到全新文件 OUT
  compare SCOPE BEFORE AFTER --expect-scope-sha HEX
范围文件格式同 v1：每行一个绝对路径，# 开头为注释；分类由「# =====」标题行中的
  [EXPECTED_CHANGE] / [MUST_NOT_CHANGE] / [RESTORED_TO_PIN] 决定。
  RESTORED_TO_PIN 行可写成「路径<TAB>pin=<64位sha>」，判据为 AFTER sha == pin（无 pin 时 == BEFORE sha），inode/ctime/mtime 变化允许。
退出码：
  snap   ：0 成功；2 用法 / 输出路径不合规 / 目标已存在 / 范围 sha 不符 / 文件缺失 / 哈希期间文件变化(UNSTABLE)
  compare：0 OK；1 MUST_NOT_CHANGE 内容变化、MUST_NOT_CHANGE 仅元数据变化(META_ONLY_FAIL)、RESTORED_TO_PIN 不符；
           2 用法 / 文件缺失 / 三方范围 sha 不一致（BEFORE 头、AFTER 头、当前范围文件、--expect-scope-sha）
修订点：
  P2-S1 OUT 解析后必须位于 /tmp/arch1018/、docs/v2/audit/sha_snapshots/ 或 docs/v2/audit/nightly_2026*/ 之下，
        不得在范围清单内，不得已存在；同目录临时文件（O_EXCL）→ fsync → os.link（目标存在即失败）→ fsync 目录。
        （用 os.link 而不是 os.replace：os.replace 会覆盖竞态中出现的同名文件，os.link 不会。）
  P2-S2 MUST_NOT_CHANGE 文件 sha 相同但 size/mtime/ctime/inode 任一不同 → 记 META_ONLY_FAIL，退出 1（单独计数）。
  P2-S3 快照头记 scope_sha256；snap 与 compare 都要求 --expect-scope-sha，compare 另要求两份快照头部一致。
  P3    每个文件哈希前后各 stat 一次，不同即 UNSTABLE 退出 2；无参数退出 2；meta 比较含 size；进程内 hashlib，不起子进程。
"""
import argparse, datetime, fnmatch, hashlib, os, re, sys, zoneinfo

ET = zoneinfo.ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
OUT_PREFIXES = ("/tmp/arch1018/", ROOT + "/docs/v2/audit/sha_snapshots/")
OUT_GLOB_DIRS = (ROOT + "/docs/v2/audit/nightly_2026*",)
CLASSES = ("EXPECTED_CHANGE", "MUST_NOT_CHANGE", "RESTORED_TO_PIN")
HEX64 = re.compile(r"[0-9a-f]{64}")


def now():
    return datetime.datetime.now(ET).isoformat(timespec="seconds")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def meta(s):
    return (s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino)


def parse_scope(p):
    cls, out = None, []
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("# ====="):
            for c in CLASSES:
                if "[" + c + "]" in ln:
                    cls = c
        if not ln.strip() or ln.startswith("#"):
            continue
        path, pin = ln, None
        if "\t" in ln:
            path, rest = ln.split("\t", 1)
            if rest.startswith("pin="):
                pin = rest[4:].strip().lower()
                if not HEX64.fullmatch(pin):
                    raise SystemExit("ERROR 范围文件 pin 格式错误: " + ln)
        if cls is None:
            raise SystemExit("ERROR 路径出现在任何分类标题之前: " + path)
        if not os.path.isabs(path):
            raise SystemExit("ERROR 范围文件里必须是绝对路径: " + path)
        out.append((path, cls, pin))
    return out


def check_scope_sha(scope, expect):
    exp = expect.strip().lower()
    if not HEX64.fullmatch(exp):
        print("ERROR --expect-scope-sha 必须是 64 位十六进制全长"); sys.exit(2)
    cur = sha256(scope)
    if cur != exp:
        print("ERROR 范围文件 sha 不符：当前 %s，期望 %s" % (cur, exp)); sys.exit(2)
    return cur


def out_allowed(out, scope_paths):
    if not os.path.isabs(out):
        return "OUT 必须是绝对路径"
    d = os.path.realpath(os.path.dirname(out))
    rp = os.path.join(d, os.path.basename(out))
    ok = any(rp.startswith(p) for p in OUT_PREFIXES)
    ok = ok or any(fnmatch.fnmatch(d, g) for g in OUT_GLOB_DIRS)
    if not ok:
        return "OUT 不在允许目录 %s / %s" % (OUT_PREFIXES, OUT_GLOB_DIRS)
    if not os.path.isdir(d):
        return "OUT 目录不存在: " + d
    real_scope = set(os.path.realpath(p) for p in scope_paths)
    if rp in real_scope:
        return "OUT 在范围清单内"
    if os.path.lexists(out):
        return "OUT 已存在，拒绝覆盖"
    return None


def write_new(path, text):
    d = os.path.dirname(path)
    tmp = os.path.join(d, ".%s.tmp.%d" % (os.path.basename(path), os.getpid()))
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.link(tmp, path)
    finally:
        os.unlink(tmp)
    dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def snap(a):
    scope_sha = check_scope_sha(a.scope, a.expect_scope_sha)
    items = parse_scope(a.scope)
    bad = out_allowed(a.out, [p for p, _, _ in items])
    if bad:
        print("ERROR", bad); sys.exit(2)
    me = os.path.abspath(__file__)
    t0 = now()
    rows, metas, tot = [], [], 0
    for p, c, pin in items:
        try:
            s1 = os.stat(p)
            h = sha256(p)
            s2 = os.stat(p)
        except FileNotFoundError:
            print("MISSING", p); sys.exit(2)
        if meta(s1) != meta(s2):
            print("UNSTABLE 哈希期间文件变化", p); sys.exit(2)
        tot += s2.st_size
        rows.append("%s  %s" % (h, p))
        metas.append("# meta\t%s\t%d\t%d\t%d\t%d\t%s" % (c, s2.st_size, s2.st_mtime_ns, s2.st_ctime_ns, s2.st_ino, p))
    t1 = now()
    L = ["# sha snapshot v2, scope=%s scope_sha256=%s" % (os.path.abspath(a.scope), scope_sha),
         "# tool=%s tool_sha256=%s python=%s" % (me, sha256(me), sys.executable),
         "# started_et=%s finished_et=%s" % (t0, t1),
         "# format: sha256sum lines, then one \"# meta\" line per file: class<TAB>size<TAB>mtime_ns<TAB>ctime_ns<TAB>inode<TAB>path"]
    L += rows + metas + ["# files=%d total_bytes=%d" % (len(items), tot)]
    write_new(a.out, "\n".join(L) + "\n")
    print("OK files=%d total_bytes=%d out=%s out_sha256=%s scope_sha256=%s t0=%s t1=%s" % (len(items), tot, a.out, sha256(a.out), scope_sha, t0, t1))
    return 0


def load(p):
    h, m, scope_sha = {}, {}, None
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("# sha snapshot") or ln.startswith("# sha baseline"):
            mm = re.search(r"scope_sha256=([0-9a-f]{64})", ln)
            scope_sha = mm.group(1) if mm else None
        elif ln.startswith("# meta\t"):
            f = ln.split("\t")
            m[f[6]] = (int(f[2]), int(f[3]), int(f[4]), int(f[5]))
        elif ln and not ln.startswith("#"):
            s, path = ln.split("  ", 1)
            h[path] = s
    return h, m, scope_sha


def compare(a):
    scope_sha = check_scope_sha(a.scope, a.expect_scope_sha)
    items = parse_scope(a.scope)
    hb, mb, sb = load(a.before)
    ha, ma, sa = load(a.after)
    print("scope_sha256 current=%s before_hdr=%s after_hdr=%s expect=%s" % (scope_sha, sb, sa, a.expect_scope_sha.lower()))
    if not (sb == sa == scope_sha):
        print("RESULT SCOPE_SHA_MISMATCH exit=2"); sys.exit(2)
    n = dict(missing=0, must_diff=0, meta_only_fail=0, pin_fail=0, expected_diff=0, restored_meta=0)
    for p, c, pin in items:
        if p not in hb or p not in ha or p not in mb or p not in ma:
            print("MISSING", p); n["missing"] += 1; continue
        same = hb[p] == ha[p]
        metasame = mb[p] == ma[p]
        if c == "MUST_NOT_CHANGE":
            if not same:
                print("DIFF MUST_NOT_CHANGE", p, hb[p][:12], "->", ha[p][:12]); n["must_diff"] += 1
            elif not metasame:
                print("META_ONLY_FAIL MUST_NOT_CHANGE (sha same; size/mtime/ctime/inode differ)", p, mb[p], "->", ma[p]); n["meta_only_fail"] += 1
        elif c == "RESTORED_TO_PIN":
            want = pin or hb[p]
            if ha[p] != want:
                print("PIN_FAIL RESTORED_TO_PIN", p, "after", ha[p][:12], "want", want[:12]); n["pin_fail"] += 1
            elif not metasame:
                print("RESTORED_META_CHANGE (allowed)", p, mb[p], "->", ma[p]); n["restored_meta"] += 1
        else:
            if not same:
                print("DIFF EXPECTED_CHANGE", p, hb[p][:12], "->", ha[p][:12]); n["expected_diff"] += 1
    code = 2 if n["missing"] else (1 if (n["must_diff"] or n["meta_only_fail"] or n["pin_fail"]) else 0)
    label = {0: "OK", 1: "FAIL_STOP", 2: "MISSING"}[code]
    print("RESULT %s exit=%d counts=%s finished_et=%s" % (label, code, n, now()))
    return code


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 2
    ap = argparse.ArgumentParser(description="sha 范围快照 v2")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s1 = sp.add_parser("snap"); s1.add_argument("scope"); s1.add_argument("out"); s1.add_argument("--expect-scope-sha", required=True)
    s2 = sp.add_parser("compare"); s2.add_argument("scope"); s2.add_argument("before"); s2.add_argument("after"); s2.add_argument("--expect-scope-sha", required=True)
    a = ap.parse_args()
    return snap(a) if a.cmd == "snap" else compare(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("ERROR 意外异常 %s: %s" % (type(e).__name__, e))
        sys.exit(2)
