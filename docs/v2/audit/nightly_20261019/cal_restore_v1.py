#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""10-19 Eng 纸面日历原子恢复 v1（QuantLab Data，2026-10-18 起草，待 Arch 审）。只用标准库。

步骤（ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md 11cb0690 第 5.4 节 + 主 Agent 书面裁定「一律恢复到 141078fa」）：
  1 校验 --expect-sha 为 64 位小写十六进制；备份 sha256 == expect，否则退出 2，目标不动（P0）
  2 把当前（被重写的）目标复制成 --keep-rewritten-dir 下的新文件（O_EXCL，保留 mtime），留存
  3 备份字节写入目标同目录临时文件（O_EXCL）→ fsync → 校验临时文件 sha == expect（不符：删临时文件、退出 2、目标不动）
  4 os.replace(临时文件, 目标)（同目录 rename，原子，等同 mv -T -f）→ fsync 目录
  5 重新哈希目标，必须 == expect，否则退出 1（报警，停后续步骤）
不对目标做 chmod；备份由例程在 cp -p 之后自行 chmod a-w。无论目标当前 sha 是否已等于 expect，都执行恢复（裁定：一律恢复）。
退出码：0 恢复并核验通过且已留存；1 恢复后 sha 不符；2 前置条件失败，目标未动；3 恢复核验通过但留存失败。
"""
import argparse, datetime, hashlib, os, re, shutil, sys, zoneinfo

ET = zoneinfo.ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
REAL_TARGET = ROOT + "/data/v2/tushare_raw/trade_cal.parquet"
KEEP_DIRS = (ROOT + "/_recovery/data/", "/tmp/")


def now():
    return datetime.datetime.now(ET).isoformat(timespec="microseconds")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def st(p):
    s = os.stat(p)
    return "size=%d mode=%o mtime_ns=%d ctime_ns=%d inode=%d dev=%d" % (s.st_size, s.st_mode & 0o7777, s.st_mtime_ns, s.st_ctime_ns, s.st_ino, s.st_dev)


def fsync_dir(d):
    fd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def copy_new(src, dst):
    """把 src 字节复制到全新文件 dst（O_EXCL，不覆盖），fsync，保留 atime/mtime。"""
    fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with open(src, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                os.write(fd, b)
        os.fsync(fd)
    finally:
        os.close(fd)
    s = os.stat(src)
    os.utime(dst, ns=(s.st_atime_ns, s.st_mtime_ns))


def main():
    ap = argparse.ArgumentParser(description="10-19 Eng 日历原子恢复 v1")
    ap.add_argument("--backup", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--expect-sha", required=True, help="64 位十六进制全长 sha256（141078fa…）")
    ap.add_argument("--keep-rewritten-dir", required=True)
    a = ap.parse_args()
    print("cal_restore_v1 started_et=%s pid=%d python=%s" % (now(), os.getpid(), sys.executable), flush=True)
    me = os.path.abspath(__file__)
    print("script=%s sha256=%s" % (me, sha256(me)), flush=True)

    exp = a.expect_sha.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", exp):
        print("ERROR --expect-sha 必须是 64 位十六进制全长"); return 2
    tgt = os.path.abspath(a.target)
    tdir = os.path.dirname(tgt)
    if not (os.path.realpath(tgt) == REAL_TARGET or tgt.startswith("/tmp/")):
        print("ERROR target 只允许 %s 或 /tmp/ 下（自测）" % REAL_TARGET); return 2
    if not os.path.isdir(tdir):
        print("ERROR target 目录不存在", tdir); return 2
    keep = os.path.abspath(a.keep_rewritten_dir)
    if not (os.path.isdir(keep) and any(os.path.realpath(keep).rstrip("/") + "/" == d or os.path.realpath(keep).startswith(d) for d in KEEP_DIRS)):
        print("ERROR keep 目录须已存在且位于 %s 之下" % (KEEP_DIRS,)); return 2
    if not os.path.isfile(a.backup):
        print("ERROR 备份不存在", a.backup); return 2
    if os.path.exists(tgt) and os.path.samefile(a.backup, tgt):
        print("ERROR 备份与目标是同一个文件（硬链接 / 同路径）"); return 2

    # 1 备份 sha
    bsha = sha256(a.backup)
    print("backup path=%s sha256=%s %s" % (a.backup, bsha, st(a.backup)), flush=True)
    if bsha != exp:
        print("P0 ERROR 备份 sha 与期望不符，目标未动：expect=%s" % exp); return 2

    # 2 留存被重写的目标
    keep_ok = True
    if os.path.lexists(tgt):
        try:
            csha = sha256(tgt)
            print("target_before path=%s sha256=%s %s" % (tgt, csha, st(tgt)), flush=True)
            stamp = datetime.datetime.now(ET).strftime("%Y%m%dT%H%M%S")
            kp = os.path.join(keep, "%s.rewritten_%s_%s" % (os.path.basename(tgt), stamp, csha[:12]))
            copy_new(tgt, kp)
            fsync_dir(keep)
            ksha = sha256(kp)
            print("kept path=%s sha256=%s %s" % (kp, ksha, st(kp)), flush=True)
            if ksha != csha:
                print("WARN 留存副本 sha 与留存前目标不同（复制期间目标被写？）"); keep_ok = False
        except Exception as e:
            keep_ok = False
            print("WARN 留存失败（继续恢复，恢复优先）%s: %s" % (type(e).__name__, e), flush=True)
    else:
        print("target_before 不存在（按缺失处理，继续恢复）", flush=True)

    # 3 同目录临时文件
    tmp = os.path.join(tdir, ".%s.restore_tmp.%d" % (os.path.basename(tgt), os.getpid()))
    try:
        copy_new(a.backup, tmp)
    except Exception as e:
        print("P0 ERROR 写临时文件失败，目标未动 %s: %s" % (type(e).__name__, e))
        if os.path.lexists(tmp):
            os.unlink(tmp)
        return 2
    tsha = sha256(tmp)
    print("tmp path=%s sha256=%s %s" % (tmp, tsha, st(tmp)), flush=True)
    if tsha != exp:
        os.unlink(tmp)
        print("P0 ERROR 临时文件 sha 不符，已删临时文件，目标未动"); return 2

    # 4 原子替换 + fsync 目录
    os.replace(tmp, tgt)
    fsync_dir(tdir)
    print("replaced at_et=%s os.replace(%s -> %s); fsync(dir) done" % (now(), tmp, tgt), flush=True)

    # 5 复核
    asha = sha256(tgt)
    print("target_after path=%s sha256=%s %s" % (tgt, asha, st(tgt)), flush=True)
    if asha != exp:
        print("ALERT 恢复后 sha 不是期望值：停后续步骤并报主 Agent 与 Arch"); return 1
    if not keep_ok:
        print("RESULT RESTORED_OK_KEEP_FAILED exit=3 finished_et=%s" % now()); return 3
    print("RESULT RESTORED_OK exit=0 finished_et=%s" % now())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("ERROR 意外异常 %s: %s" % (type(e).__name__, e))
        sys.exit(2)
