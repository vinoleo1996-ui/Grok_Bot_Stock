#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""10-26 Eng 纸面日历只读比对器（改编自 v1）（QuantLab Data，2026-10-18 起草，待 Arch 审）。

只读两份 parquet（--current 跑后文件、--backup 141078fa 备份），只写 --out 指定的新文本文件，
有差异时另写同名 .diff.csv（新文件）。不 import 项目代码；只用标准库 + pandas + pyarrow。
解释器钉 /usr/bin/python3（pandas 3.0.6 / pyarrow 26.0.0），版本不符只记 WARN，不改判定。

判据（全部满足 = 内容一致，ARCH_DATA_REVISIONS_1040_REVIEW_ZH.md 11cb0690 第 5.3 节）：
  C1 两份都能完整读出（跑后文件损坏、截断 = 不一致）
  C2 schema：列名、列序、每列 arrow 类型与可空性、pandas dtype 全同（以备份为准）
  C3 行数相同（parquet 元数据与实读行数都核）
  C4 两份各自 (exchange, cal_date) 无重复
  C5 两份都按 (exchange, cal_date, 其余列按备份列序) 排序（空值排最后）、重置索引后逐格相同（空与空视为相同）
  C6 两份都有 exchange=SSE 的 20261019、20261020 行各恰好一行且 is_open == 1
退出码：0 一致；1 不一致（含跑后文件不可读）；2 用法错误 / 输出路径不合规 / 备份不可读 / 意外异常。
"""
import argparse, datetime, hashlib, os, sys, zoneinfo

ET = zoneinfo.ZoneInfo("America/New_York")
ROOT = "/workspace/QuantLab"
OUT_DIRS = (ROOT + "/docs/v2/audit/nightly_20261027/", "/tmp/")
KEY = ["exchange", "cal_date"]
MUST_OPEN = ["20261027", "20261028"]
PIN_PY, PIN_PD, PIN_PA = "/usr/bin/python3", "3.0.6", "26.0.0"


def now():
    return datetime.datetime.now(ET).isoformat(timespec="seconds")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_out(p):
    """--out 必须是全新文件，位于允许目录；.diff.csv 也必须不存在。"""
    if not os.path.isabs(p):
        return "out 必须是绝对路径"
    rp = os.path.join(os.path.realpath(os.path.dirname(p)), os.path.basename(p))
    if not any(rp.startswith(d) for d in OUT_DIRS):
        return "out 不在允许目录 %s" % (OUT_DIRS,)
    if not os.path.isdir(os.path.dirname(rp)):
        return "out 所在目录不存在"
    for q in (p, p + ".diff.csv"):
        if os.path.lexists(q):
            return "目标已存在，拒绝覆盖：" + q
    return None


def write_new(path, text):
    """同目录临时文件（O_EXCL）→ fsync → os.link 到目标（目标存在即失败，不覆盖）→ 删临时文件 → fsync 目录。"""
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


def load(p, pq):
    """返回 (table, df, meta_rows, err)。任何异常都算不可读。"""
    try:
        meta_rows = pq.ParquetFile(p).metadata.num_rows
        t = pq.read_table(p)
        df = t.to_pandas()
        return t, df, meta_rows, None
    except Exception as e:  # 损坏 / 截断 / 不是 parquet
        return None, None, None, "%s: %s" % (type(e).__name__, str(e)[:300])


def schema_desc(t, df):
    return [(f.name, str(f.type), bool(f.nullable), str(df[f.name].dtype)) for f in t.schema]


def sort_cols(cols):
    return [c for c in KEY if c in cols] + [c for c in cols if c not in KEY]


def must_open(df, pd):
    """返回 {日期: 说明}，说明为 "OK" 表示通过。"""
    res = {}
    for d in MUST_OPEN:
        try:
            m = df["cal_date"].astype(str) == d
            if "exchange" in df.columns:
                m = m & (df["exchange"].astype(str) == "SSE")
            sub = df[m]
            if len(sub) != 1:
                res[d] = "行数=%d（应为 1）" % len(sub)
            elif int(pd.to_numeric(sub["is_open"].iloc[0])) != 1:
                res[d] = "is_open=%r" % (sub["is_open"].iloc[0],)
            else:
                res[d] = "OK"
        except Exception as e:
            res[d] = "检查异常 %s: %s" % (type(e).__name__, str(e)[:120])
    return res


def cells_equal(a, b):
    """逐格比较，空与空视为相同；返回布尔 Series。"""
    eq = (a == b)
    try:
        eq = eq.fillna(False)
    except Exception:
        pass
    eq = eq.astype(bool)
    return eq | (a.isna() & b.isna()).astype(bool)


def main():
    ap = argparse.ArgumentParser(description="10-26 Eng 日历只读比对器")
    ap.add_argument("--current", required=True, help="daily_pull 之后的文件（建议用 post_daily_pull 副本）")
    ap.add_argument("--backup", required=True, help="跑前 cp -p 的 141078fa 备份")
    ap.add_argument("--out", required=True, help="新文本文件路径（不得已存在）")
    a = ap.parse_args()

    bad = check_out(a.out)
    if bad:
        print("ERROR", bad)
        return 2

    L = []
    def log(s):
        L.append(s)
        print(s, flush=True)

    t0 = now()
    log("# cal_compare_v1 结果（只读；新文件）")
    log("started_et=%s" % t0)
    log("script=%s sha256=%s" % (os.path.abspath(__file__), sha256(os.path.abspath(__file__))))
    log("python=%s pid=%d" % (sys.executable, os.getpid()))
    try:
        import pandas as pd
        import pyarrow as pa
        import pyarrow.parquet as pq
    except Exception as e:
        log("ERROR 无法 import pandas/pyarrow: %s" % e)
        write_new(a.out, "\n".join(L) + "\n")
        return 2
    log("pandas=%s pyarrow=%s" % (pd.__version__, pa.__version__))
    if sys.executable != PIN_PY or pd.__version__ != PIN_PD or pa.__version__ != PIN_PA:
        log("WARN 解释器或版本与钉值不同（钉 %s / pandas %s / pyarrow %s），只记录，不改判定" % (PIN_PY, PIN_PD, PIN_PA))

    files = {"current": a.current, "backup": a.backup}
    for k, p in files.items():
        if os.path.exists(p):
            st = os.stat(p)
            log("%s path=%s sha256=%s size=%d mtime_ns=%d ctime_ns=%d inode=%d" % (k, p, sha256(p), st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_ino))
        else:
            log("%s path=%s 不存在" % (k, p))

    fails = []
    tb, db, rb, eb = load(a.backup, pq) if os.path.exists(a.backup) else (None, None, None, "不存在")
    if eb:
        log("ERROR 备份不可读（无法作为基准）：%s" % eb)
        log("RESULT ERROR exit=2 finished_et=%s" % now())
        write_new(a.out, "\n".join(L) + "\n")
        return 2
    tc, dc, rc, ec = load(a.current, pq) if os.path.exists(a.current) else (None, None, None, "不存在")
    if ec:
        log("C1 FAIL 跑后文件不可读（损坏 / 截断 / 缺失）：%s" % ec)
        log("C6 backup：%s" % must_open(db, pd))
        log("RESULT MISMATCH exit=1 （C1）finished_et=%s" % now())
        write_new(a.out, "\n".join(L) + "\n")
        return 1
    log("C1 PASS 两份都能完整读出")

    sb, sc = schema_desc(tb, db), schema_desc(tc, dc)
    log("schema backup =%s" % sb)
    log("schema current=%s" % sc)
    if sb != sc:
        fails.append("C2")
        log("C2 FAIL schema（列名 / 列序 / arrow 类型 / 可空性 / pandas dtype）不同")
    else:
        log("C2 PASS schema 全同")
    try:
        mb = (tb.schema.metadata or {}).get(b"pandas", b"")
        mc = (tc.schema.metadata or {}).get(b"pandas", b"")
        log("INFO pandas 元数据%s（只记录，不计入判定）" % ("相同" if mb == mc else "不同"))
    except Exception:
        pass

    log("rows backup meta=%d read=%d ; current meta=%d read=%d" % (rb, len(db), rc, len(dc)))
    if not (rb == rc == len(db) == len(dc)):
        fails.append("C3")
        log("C3 FAIL 行数不同")
    else:
        log("C3 PASS 行数相同")

    for name, df in (("backup", db), ("current", dc)):
        if not all(c in df.columns for c in KEY):
            fails.append("C4")
            log("C4 FAIL %s 缺少键列 %s" % (name, KEY))
            continue
        nd = int(df.duplicated(KEY).sum())
        if nd:
            fails.append("C4")
            log("C4 FAIL %s 有 %d 个重复 (exchange, cal_date)" % (name, nd))
        else:
            log("C4 PASS %s 无重复键" % name)

    diff_n, first_keys = 0, []
    if "C2" not in fails and "C3" not in fails and all(c in db.columns for c in KEY):
        cols = sort_cols(list(db.columns))
        sb_df = db.sort_values(cols, na_position="last", kind="mergesort").reset_index(drop=True)
        sc_df = dc.sort_values(cols, na_position="last", kind="mergesort").reset_index(drop=True)
        rowbad = None
        for c in db.columns:
            ok = cells_equal(sb_df[c], sc_df[c])
            nbad = int((~ok).sum())
            log("C5 列 %s 不同格数=%d" % (c, nbad))
            rowbad = (~ok) if rowbad is None else (rowbad | ~ok)
        diff_n = int(rowbad.sum()) if rowbad is not None else 0
        if diff_n:
            fails.append("C5")
            first_keys = [tuple(str(x) for x in r) for r in sb_df.loc[rowbad, KEY].head(10).itertuples(index=False)]
            log("C5 FAIL 排序后不同行数=%d，前 10 个键（备份侧）=%s" % (diff_n, first_keys))
        else:
            log("C5 PASS 排序后逐格相同")
    else:
        fails.append("C5")
        log("C5 FAIL 未做逐格比对（C2 / C3 / 键列不满足），按不一致处理")

    for name, df in (("backup", db), ("current", dc)):
        r = must_open(df, pd)
        okall = all(v == "OK" for v in r.values())
        log("C6 %s %s %s" % ("PASS" if okall else "FAIL", name, r))
        if not okall:
            fails.append("C6")

    csv_path = None
    if fails:
        try:
            keycols = [c for c in KEY if c in db.columns and c in dc.columns]
            xb = db.astype("string"); xc = dc.astype("string")
            m = xc.merge(xb, on=keycols, how="outer", suffixes=("_current", "_backup"), indicator=True)
            other = [c for c in db.columns if c not in keycols and c in dc.columns]
            sel = m["_merge"] != "both"
            for c in other:
                sel = sel | ~cells_equal(m[c + "_current"], m[c + "_backup"])
            out = m[sel]
            csv_path = a.out + ".diff.csv"
            write_new(csv_path, out.to_csv(index=False))
            log("DIFF_CSV %s rows=%d（按键外连接：only current / only backup / 同键不同值）" % (csv_path, len(out)))
        except Exception as e:
            log("WARN 差异行导出失败 %s: %s" % (type(e).__name__, str(e)[:200]))

    code = 1 if fails else 0
    log("RESULT %s exit=%d fails=%s finished_et=%s" % ("MISMATCH" if fails else "IDENTICAL", code, sorted(set(fails)), now()))
    write_new(a.out, "\n".join(L) + "\n")
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        print("ERROR 意外异常 %s: %s" % (type(e).__name__, e))
        sys.exit(2)
