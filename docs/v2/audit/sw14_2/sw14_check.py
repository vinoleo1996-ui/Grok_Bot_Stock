#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""DIFF C r3b §14② 只读核查（QuantLab Data，2026-10-18 起草，Arch 钉 sha 后在 run .ok 下运行）。

对象：data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet（CLEAN，89d4afa3，manifest 记 7920 行）
      与 data/v2/sw_l1_pit/manifest.json（tushare_candidate 段）；冻结日历 data/v2/calendar/trade_cal_sse_pit.parquet（只读 cal_date、is_open 两列）。
只用标准库 + pandas + pyarrow，不 import 任何项目代码；解释器 /usr/bin/python3。
唯一写入：docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt（新文件，O_EXCL 临时文件 → fsync → os.link，目标已存在即拒绝）。
开头先核 output/ai_factory/ARCH_RUN_AUTH_DATA_SW14_2_READONLY.ok：存在、expires_et 带时区且在未来；
若 .ok 里有 script_sha256 / dep_script_sha256 字段，须等于本脚本 sha256。只解析，不 import 项目 enforce。
RSS 自检：resource.getrusage ru_maxrss > 1484800 KB 即停（退出 3，不写报告）。
退出码：0 完成；2 .ok / 输出路径 / 输入不满足；3 RSS 超线。
"""
import datetime, hashlib, json, os, re, resource, sys
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
ROOT = "/workspace/QuantLab"
OK_PATH = ROOT + "/output/ai_factory/ARCH_RUN_AUTH_DATA_SW14_2_READONLY.ok"
PARQ = ROOT + "/data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
MANI = ROOT + "/data/v2/sw_l1_pit/manifest.json"
CAL = ROOT + "/data/v2/calendar/trade_cal_sse_pit.parquet"
OUT = ROOT + "/docs/v2/audit/sw14_2/sw14_clean_schema_check_20261018.txt"
RSS_STOP_KB = 1484800
LAG_END = "20261016"
# 白名单原样取自 docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r2.md L329-330（sha 482d8a2b…），norm_code 先 strip（L366）
A_DOT = re.compile(r"^(\d{6})\.(SH|SZ|BJ)$", re.I)
A_PFX = re.compile(r"^(SH|SZ|BJ)\.(\d{6})$", re.I)
# Strategy DIFF C r3b 期望的 11 列（r3b.diff L26-27），只作对照，不改判定
R3B_EXPECTED = [("instrument_id", "str"), ("sw_code", "str"), ("sw_name", "str"), ("source", "str"),
                ("quality_status", "str"), ("schema", "str"), ("is_new", "str"), ("in_date", "datetime64[us]"),
                ("out_date", "datetime64[us]"), ("available_at", "datetime64[us]"), ("revision", "int64")]


def now():
    return datetime.datetime.now(ET).isoformat(timespec="seconds")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rss_check(where, L):
    kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    L.append("RSS %s maxrss_kb=%d（停止线 %d）" % (where, kb, RSS_STOP_KB))
    if kb > RSS_STOP_KB:
        print("\n".join(L))
        print("STOP RSS 超过停止线，未写报告")
        sys.exit(3)


def parse_ok(p):
    kv = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+)\s*[:=]\s*(.*)$", ln)
        if m:
            kv[m.group(1)] = m.group(2).strip()
    return kv


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


def ymd(x):
    """把日期类值转成 YYYYMMDD 字符串；无法解析返回 None。"""
    if x is None:
        return None
    s = str(x).strip()
    m = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})", s)
    return (m.group(1) + m.group(2) + m.group(3)) if m else None


def main():
    me = os.path.abspath(__file__)
    my_sha = sha256(me)
    L = ["# DIFF C r3b §14② CLEAN SW L1 只读核查报告（新文件）", "started_et=%s" % now(),
         "script=%s sha256=%s" % (me, my_sha), "python=%s pid=%d" % (sys.executable, os.getpid())]

    # --- .ok
    if not os.path.isfile(OK_PATH):
        print("REFUSED .ok 不存在:", OK_PATH); return 2
    kv = parse_ok(OK_PATH)
    exp = kv.get("expires_et")
    try:
        t_exp = datetime.datetime.fromisoformat(exp)
    except Exception:
        print("REFUSED .ok expires_et 无法解析:", repr(exp)); return 2
    if t_exp.tzinfo is None:
        print("REFUSED .ok expires_et 无时区:", exp); return 2
    if t_exp <= datetime.datetime.now(ET):
        print("REFUSED .ok 已过期:", exp); return 2
    for k in ("script_sha256", "dep_script_sha256"):
        if k in kv and kv[k].lower() != my_sha:
            print("REFUSED .ok %s=%s 与本脚本 sha %s 不符" % (k, kv[k], my_sha)); return 2
    L.append("ok=%s sha256=%s expires_et=%s fields=%s" % (OK_PATH, sha256(OK_PATH), exp, sorted(kv)))

    # --- 输出路径
    if not os.path.isdir(os.path.dirname(OUT)):
        print("REFUSED 输出目录不存在:", os.path.dirname(OUT)); return 2
    if os.path.lexists(OUT):
        print("REFUSED 输出已存在，拒绝覆盖:", OUT); return 2

    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    L.append("pandas=%s pyarrow=%s" % (pd.__version__, pa.__version__))

    # --- (0) sha
    for p in (PARQ, MANI, CAL):
        st = os.stat(p)
        L.append("input %s sha256=%s size=%d mtime_ns=%d inode=%d" % (p, sha256(p), st.st_size, st.st_mtime_ns, st.st_ino))
    rss_check("after_hash", L)

    # --- (1) schema
    pf = pq.ParquetFile(PARQ)
    L.append("")
    L.append("## (1) 列与类型")
    L.append("parquet num_rows(meta)=%d num_columns=%d" % (pf.metadata.num_rows, pf.metadata.num_columns))
    t = pq.read_table(PARQ)
    df = t.to_pandas()
    rss_check("after_read", L)
    got = []
    for i, f in enumerate(t.schema):
        got.append((f.name, str(df[f.name].dtype)))
        L.append("col[%d] name=%r arrow=%s nullable=%s pandas=%s" % (i, f.name, f.type, f.nullable, df[f.name].dtype))
    L.append("列数=%d（Strategy r3b 期望 11）" % len(got))
    L.append("与 r3b SW_L1_CLEAN_COLUMNS 对照（顺序无关，名+pandas dtype）：%s" % ("一致" if sorted(got) == sorted(R3B_EXPECTED) else "不一致"))
    if sorted(got) != sorted(R3B_EXPECTED):
        L.append("  只在表中=%s" % sorted(set(got) - set(R3B_EXPECTED)))
        L.append("  只在 r3b 期望中=%s" % sorted(set(R3B_EXPECTED) - set(got)))

    # --- (2) 白名单外的 instrument_id
    L.append("")
    L.append("## (2) 不符合 Data r2 norm_code 白名单的 instrument_id（strip 后 A_DOT / A_PFX fullmatch；空值也算不符）")
    L.append("A_DOT=%r A_PFX=%r（re.I；出处 docs/v2/plans/DATA_SW_L1_PIT_V2_FIX_PLAN_ZH_r2.md L329-330）" % (A_DOT.pattern, A_PFX.pattern))
    if "instrument_id" not in df.columns:
        L.append("instrument_id 列不存在，跳过 (2)(3) 中依赖它的项")
        ids = None
    else:
        ids = df["instrument_id"]
        def ok(x):
            if x is None or (isinstance(x, float) and x != x):
                return False
            try:
                if pd.isna(x):
                    return False
            except Exception:
                pass
            s = str(x).strip()
            return bool(A_DOT.fullmatch(s) or A_PFX.fullmatch(s))
        cnt = {}
        for x in ids.tolist():
            if not ok(x):
                k = repr(x)
                cnt[k] = cnt.get(k, 0) + 1
        L.append("白名单外：不同值 %d 个，行数合计 %d" % (len(cnt), sum(cnt.values())))
        for k in sorted(cnt):
            L.append("  NONWL %s rows=%d" % (k, cnt[k]))
        sp = {}
        for x in ids.tolist():
            s = "" if x is None else str(x)
            if "00018" in s or s.startswith("T"):
                sp[repr(x)] = sp.get(repr(x), 0) + 1
        L.append("含 \"00018\" 或以 \"T\" 开头的 id：不同值 %d 个" % len(sp))
        for k in sorted(sp):
            L.append("  SPECIAL %s rows=%d whitelist=%s" % (k, sp[k], "否" if k in cnt else "是"))
        styles = {"A_DOT": 0, "A_PFX": 0}
        for x in ids.dropna().astype(str).tolist():
            s = x.strip()
            if A_DOT.fullmatch(s): styles["A_DOT"] += 1
            elif A_PFX.fullmatch(s): styles["A_PFX"] += 1
        L.append("白名单内写法分布（行）：%s；首尾带空白的行数=%d" % (styles, int((ids.dropna().astype(str) != ids.dropna().astype(str).str.strip()).sum())))

    # --- (3) manifest 对照
    L.append("")
    L.append("## (3) manifest tushare_candidate 与实际表对照")
    man = json.load(open(MANI, encoding="utf-8"))
    tc = (man.get("tushare_candidate") or {})
    mt = tc.get("metrics") or {}
    L.append("manifest tushare_candidate.path=%s checked_at=%s blockers=%s" % (tc.get("path"), tc.get("checked_at"), tc.get("blockers")))
    L.append("manifest metrics: rows=%s n_instruments=%s n_l1=%s in_date_min=%s in_date_max=%s available_at_nulls=%s" % (
        mt.get("rows"), mt.get("n_instruments"), mt.get("n_l1"), mt.get("in_date_min"), mt.get("in_date_max"), mt.get("available_at_nulls")))
    act_rows = len(df)
    act_n = int(ids.nunique(dropna=True)) if ids is not None else None
    ind = pd.to_datetime(df["in_date"], errors="coerce") if "in_date" in df.columns else None
    act_min = ind.min().strftime("%Y-%m-%d") if ind is not None and ind.notna().any() else None
    act_max = ind.max().strftime("%Y-%m-%d") if ind is not None and ind.notna().any() else None
    l1col = "sw_code" if "sw_code" in df.columns else None
    act_l1 = int(df[l1col].nunique(dropna=True)) if l1col else None
    act_av_null = int(df["available_at"].isna().sum()) if "available_at" in df.columns else None
    L.append("actual: rows=%d nunique(instrument_id)=%s nunique(%s)=%s in_date_min=%s in_date_max=%s available_at_nulls=%s in_date_unparseable=%s" % (
        act_rows, act_n, l1col, act_l1, act_min, act_max, act_av_null, (int(ind.isna().sum()) if ind is not None else None)))
    def cmp(name, a, b):
        L.append("  %-20s manifest=%r actual=%r %s" % (name, a, b, "一致" if str(a) == str(b) else "不一致"))
    cmp("rows", mt.get("rows"), act_rows)
    cmp("n_instruments", mt.get("n_instruments"), act_n)
    cmp("n_l1", mt.get("n_l1"), act_l1)
    cmp("in_date_min", mt.get("in_date_min"), act_min)
    cmp("in_date_max", mt.get("in_date_max"), act_max)
    cmp("available_at_nulls", mt.get("available_at_nulls"), act_av_null)
    del df, t
    rss_check("after_compare", L)

    # --- (4) 日历滞后
    L.append("")
    L.append("## (4) manifest 时点相对冻结日历的滞后（开市日数，严格晚于基准日、截至 %s 含）" % LAG_END)
    cal = pq.read_table(CAL, columns=["cal_date", "is_open"]).to_pandas()
    cd = cal["cal_date"].astype(str).str.replace("-", "", regex=False).str[:8]
    op = pd.to_numeric(cal["is_open"], errors="coerce").fillna(0).astype(int) == 1
    opens = sorted(cd[op].tolist())
    L.append("calendar rows=%d open_days=%d range=%s..%s" % (len(cal), len(opens), cd.min(), cd.max()))
    def lag(d):
        return sum(1 for x in opens if d < x <= LAG_END)
    def last_open_le(d):
        c = [x for x in opens if x <= d]
        return c[-1] if c else None
    cands = []
    for name, val in (("fetch_time", man.get("fetch_time")), ("tushare_candidate.checked_at", tc.get("checked_at")),
                      ("tushare_candidate.metrics.in_date_max", mt.get("in_date_max")), ("in_date_max(顶层)", man.get("in_date_max"))):
        if val is None:
            L.append("  %s 缺失" % name); continue
        try:
            ts = datetime.datetime.fromisoformat(str(val))
        except Exception:
            ts = None
        if ts is not None and ts.tzinfo is not None:
            shd = ts.astimezone(SH)
            base = shd.strftime("%Y%m%d")
            # 「该时点已收盘的最后一个 SSE 交易日」：上海 15:00 前取前一开市日
            cov = last_open_le(base) if (shd.hour >= 15 or base not in opens) else last_open_le((shd - datetime.timedelta(days=1)).strftime("%Y%m%d"))
            L.append("  %s=%s → 上海 %s；naive 基准日 %s lag=%d；收盘覆盖日 %s lag=%d" % (name, val, shd.isoformat(timespec="seconds"), base, lag(base), cov, lag(cov) if cov else -1))
        else:
            base = ymd(val)
            if base:
                L.append("  %s=%s 基准日 %s lag=%d" % (name, val, base, lag(base)))
            else:
                L.append("  %s=%r 无法解析" % (name, val))
    rss_check("end", L)
    L.append("")
    L.append("finished_et=%s" % now())
    text = "\n".join(L) + "\n"
    write_new(OUT, text)
    print(text)
    print("WROTE %s sha256=%s" % (OUT, sha256(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
