"""sw_pit 过期 + 完整性检查自测（r3）。
完全隔离：临时目录自建 ROOT（真实建文件，不软链）；所有模块级 ROOT/R/OUT 都替换到临时目录；
网络（Yahoo、RSS）与数据加载全部 stub；守卫：任何代码读写真实 /workspace/QuantLab/data、/workspace/QuantLab/output 或联网，立即判失败。
运行：cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/intel/test_sw_freshness.py"""
import sys, os, io, json, hashlib, tempfile, shutil, builtins, socket, pathlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import intel_common as C, intel_event_study as S, intel_c1_gap_split as G, intel_run as RUN

REAL = C.ROOT.resolve()
FORBID = [str(REAL / "data"), str(REAL / "output")]
violations = []


class GuardViolation(AssertionError):
    pass


def _bad(path) -> bool:
    try:
        sp = os.path.realpath(os.fspath(path))
    except TypeError:
        return False
    return any(sp == f or sp.startswith(f + os.sep) for f in FORBID)


_open, _io_open, _read_parquet, _connect = builtins.open, io.open, pd.read_parquet, socket.socket.connect


def g_open(f, *a, **k):
    if not isinstance(f, int) and _bad(f):
        violations.append(f"open {f}"); raise GuardViolation(f"guard: 访问真实路径 {f}")
    return _open(f, *a, **k)


def g_read_parquet(path, *a, **k):
    if isinstance(path, (str, os.PathLike)) and _bad(path):
        violations.append(f"read_parquet {path}"); raise GuardViolation(f"guard: read_parquet 真实路径 {path}")
    return _read_parquet(path, *a, **k)


def g_connect(self, addr):
    violations.append(f"connect {addr}"); raise GuardViolation(f"guard: 联网 {addr}")


class Sentinel(Exception):
    pass


def boom(name):
    def f(*a, **k):
        violations.append(f"stub called: {name}"); raise Sentinel(name)
    return f


ok, fails = 0, []


def check(n, c):
    global ok
    if c: ok += 1
    else: fails.append(n)
    print("PASS" if c else "FAIL", n)


def make_root(base: Path, name: str, built="2026-10-14T04:00:00", sha_ok=True, with_manifest=True, with_parquet=True,
              cal="normal", with_range=True, cal_end="2026-10-23"):
    r = base / name
    (r / "data/v2/sw_pit").mkdir(parents=True); (r / "data/v2/calendar").mkdir(parents=True)
    (r / "output/intel").mkdir(parents=True)
    pq = r / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"
    pd.DataFrame({"instrument_id": ["sh.600000"], "name": ["x"], "l1_name": ["银行"],
                  "in_date": pd.to_datetime(["2026-09-24"]), "out_date": pd.to_datetime([None])}).to_parquet(pq)
    sha = hashlib.sha256(pq.read_bytes()).hexdigest() if sha_ok else "0" * 64
    if not with_parquet: pq.unlink()
    days = pd.date_range("2026-10-08", cal_end)
    is_open = [int(d.weekday() < 5) for d in days] if cal == "normal" else [0] * len(days)
    pd.DataFrame({"cal_date": days.strftime("%Y%m%d"), "is_open": is_open, "pretrade_date": "",
                  "available_at": pd.Timestamp("2025-12-31 09:00")}).to_parquet(r / C.TRADE_CAL)
    if with_manifest:
        m = {"built": built, "sha256": {"sw_pit/industry_members_sw_l1_pit.parquet": sha},
             "l1": {"in_date_range": ["1984-05-09", "2026-09-24"]} if with_range else {}}
        (r / "data/v2/sw_pit/manifest.json").write_text(json.dumps(m))
    (r / "data/v2/tushare_raw/daily").mkdir(parents=True)          # 日线故意缺 10-15
    for d in ("20261013", "20261014", "20261016"):
        (r / f"data/v2/tushare_raw/daily/{d}.parquet").write_bytes(b"")
    return r


def run_tests(base: Path):
    try:
        open(str(REAL / "data/v2/sw_pit/manifest.json")); check("守卫自检：读真实 data 会被拦截", False)
    except GuardViolation:
        check("守卫自检：读真实 data 会被拦截", True); violations.clear()
    r0 = make_root(base, "r0")
    f = C.check_table_freshness("sw_pit", "2026-10-18", r0)
    check("返回字段齐全（含 coverage_gap / as_of_decision / reference_day）",
          set(f) == {"table", "max_date", "built", "covered_through", "reference_day", "as_of_decision", "lag_days", "coverage_gap", "status", "disclosure"})
    check("基准：美东 04:00 = 上海 16:00 → 覆盖 10-13，参考日 10-16，落后 3 → stale，coverage_gap",
          f["covered_through"] == "2026-10-13" and f["reference_day"] == "2026-10-16" and f["lag_days"] == 3 and f["status"] == "stale" and f["coverage_gap"])
    check("日线缺 10-15 时落后天数仍为 3（交易日取自 trade_cal）", f["lag_days"] == 3)
    g = C.check_table_freshness("sw_pit", "2026-10-15", r0)
    check("asof 10-15 → 落后 2 → ok", g["status"] == "ok" and g["lag_days"] == 2)
    a = C.check_table_freshness("sw_pit", "2026-10-18", make_root(base, "b559", built="2026-10-14T05:59:00"))
    b = C.check_table_freshness("sw_pit", "2026-10-18", make_root(base, "b600", built="2026-10-14T06:00:00"))
    check("美东 05:59（上海 17:59）→ 覆盖 10-13、落后 3", a["covered_through"] == "2026-10-13" and a["lag_days"] == 3)
    check("美东 06:00（上海 18:00）→ 覆盖 10-14、落后 2、ok", b["covered_through"] == "2026-10-14" and b["lag_days"] == 2 and b["status"] == "ok")
    c = C.check_table_freshness("sw_pit", "2026-10-18", make_root(base, "b2000", built="2026-10-13T20:00:00"))
    check("美东 10-13 20:00 = 上海 10-14 08:00 → 覆盖 10-13", c["covered_through"] == "2026-10-13")
    # P3：built 带时区（上海 18:30 → 覆盖当日；UTC 10:00 = 上海 18:00 → 覆盖当日）
    t1 = C.check_table_freshness("sw_pit", "2026-10-18", make_root(base, "btz1", built="2026-10-14T18:30:00+08:00"))
    t2 = C.check_table_freshness("sw_pit", "2026-10-18", make_root(base, "btz2", built="2026-10-14T09:59:00+00:00"))
    check("built 带时区 +08:00 18:30 → 用 tz_convert、不抛 TypeError，覆盖 10-14", t1["covered_through"] == "2026-10-14")
    check("built 带时区 UTC 09:59（上海 17:59）→ 覆盖 10-13", t2["covered_through"] == "2026-10-13")

    def hard(name, root, asof="2026-10-18"):
        try:
            C.check_table_freshness("sw_pit", asof, root); check(name + "：check 抛完整性错误", False)
        except C.TableIntegrityError:
            check(name + "：check 抛完整性错误", True)
        for allow in (False, True):
            try:
                C.require_fresh("sw_pit", asof, allow_stale=allow, root=root); check(f"{name}：require_fresh(allow_stale={allow}) 硬停", False)
            except SystemExit as e:
                check(f"{name}：require_fresh(allow_stale={allow}) 硬停", "HARD STOP" in str(e))
    hard("sha 不一致", make_root(base, "sha", sha_ok=False))
    hard("manifest 缺失", make_root(base, "noman", with_manifest=False))
    hard("parquet 缺失", make_root(base, "nopq", with_parquet=False))
    hard("in_date_range 缺失（P3）", make_root(base, "norange", with_range=False))
    hard("日历为空（无开市日，P3）", make_root(base, "emptycal", cal="empty"))
    hard("参考日超出日历范围（P2-2）", r0, asof="2027-01-04")
    hard("built 无法解析（ValueError → 完整性错误）", make_root(base, "badbuilt", built="not-a-date"))
    hard("built 落在美东不存在时刻（夏令时跳变）", make_root(base, "nonexist", built="2026-03-08T02:30:00"))
    cf = make_root(base, "nocal"); (cf / C.TRADE_CAL).unlink()
    hard("日历文件缺失（FileNotFoundError → 完整性错误）", cf)
    amb = C.check_table_freshness("sw_pit", "2026-11-03", make_root(base, "amb", built="2026-11-01T01:30:00", cal_end="2026-11-06"))
    check("美东回拨重复时刻 01:30 不抛错（ambiguous=True 取夏令时）", amb["status"] in ("ok", "stale"))
    try:
        C.require_fresh("sw_pit", "2026-10-18", root=r0); check("stale 默认停跑（非硬停）", False)
    except SystemExit as e:
        check("stale 默认停跑（非硬停）", str(e).startswith("STOP"))
    check("--allow-stale 放行 stale 并带 disclosure", "STALE" in C.require_fresh("sw_pit", "2026-10-18", allow_stale=True, root=r0)["disclosure"])
    check("verify_sha：一致时通过", len(C.verify_sha("sw_pit", r0)) == 64)
    # 研究脚本入口：模块变量全部指向临时 ROOT，数据加载与联网 stub；应在任何计算前停跑
    for mod in (S, G):
        nm = Path(mod.__file__).name
        for root_name, argv, expect in ((str(r0), [], "STOP"), ("sha_e", ["--allow-stale"], "HARD STOP")):
            root = r0 if root_name == str(r0) else make_root(base, f"{nm}_{root_name}", sha_ok=False)
            C.ROOT = S.R = G.R = root; G.OUT = root / "output/intel/pit_candidates"
            sys.argv = [mod.__file__] + argv
            try:
                mod.main(); check(f"{nm} {argv or '无参数'} → {expect}", False)
            except SystemExit as e:
                check(f"{nm} {argv or '无参数'} → {expect}", str(e).startswith(expect))
            except Sentinel as e:
                check(f"{nm} {argv or '无参数'} → {expect}（实际越过停跑调用了 {e}）", False)
    # intel_run 方案 A：完整性错误只停行业→个股映射；md 横幅、每行原因、json 顶层 data_integrity_errors
    for case, kw in (("sha 不一致", {"sha_ok": False}), ("built 为整数（非法类型）", {"built": 12345})):
        root = make_root(base, "run_" + str(abs(hash(case))), **kw)
        C.ROOT, C._POOL, C.SW_FRESHNESS = root, None, None
        RUN.OUT = root / "output/intel"; RUN.HIST = RUN.OUT / "history"; RUN.STATE = RUN.OUT / "intraday_state.json"; RUN.STUDY = RUN.OUT / "event_study_hitrate.json"
        RUN.pull_markets = lambda: ({"nasdaq": {"name": "纳斯达克综指", "symbol": "^IXIC", "date": "2026-10-16", "last": 1.0, "change": -2.5,
                                                "unit": "%", "grade": "强", "adverse": True}}, {"nasdaq": "ok"})
        C.fetch_news = lambda *a, **k: ([], {})
        out = root / "dry"
        sys.argv = ["intel_run.py", "--mode", "preopen", "--out-dir", str(out), "--prev", str(root / "none.json")]
        try:
            RUN.main(); crashed = None
        except Exception as e:
            crashed = e
        check(f"intel_run 方案 A（{case}）：不崩", crashed is None)
        if crashed is None:
            p = json.loads((out / "ALERTS_latest.json").read_text()); md = (out / "ALERTS_latest.md").read_text()
            check(f"intel_run（{case}）：json 顶层 data_integrity_errors 非空且 high", p["data_integrity_errors"] and p["data_integrity_errors"][0]["severity"] == "high")
            check(f"intel_run（{case}）：行业预警照常输出", len(p["alerts"]) > 0)
            check(f"intel_run（{case}）：md 标题下第一行是 HIGH 横幅", md.splitlines()[2].startswith("> ⚠ HIGH：sw_pit 完整性错误"))
            check(f"intel_run（{case}）：每条相关个股写明原因", all("完整性错误，已停" in l for l in md.splitlines() if l.startswith("- 相关个股")))
    sw = pd.DataFrame({"instrument_id": ["a", "b", "c"], "in_date": pd.to_datetime(["2026-09-24", "2026-09-01", "2026-08-01"]),
                       "out_date": pd.to_datetime([None, "2026-09-24", None])})
    check("as-of：变动当天不可用、出表当天仍是成员", set(C.sw_members_asof(sw, "2026-09-24").instrument_id) == {"b", "c"})
    check("as-of：次日生效", set(C.sw_members_asof(sw, "2026-09-25").instrument_id) == {"a", "c"})


def main():
    saved = dict(C_ROOT=C.ROOT, S_R=S.R, G_R=G.R, G_OUT=G.OUT, argv=sys.argv, run=(RUN.OUT, RUN.HIST, RUN.STATE, RUN.STUDY, RUN.pull_markets),
                 yd=C.yahoo_daily, fn=C.fetch_news, sa=S.a_share_industry_returns, su=S.us_changes, gl=G.legs, pool=C._POOL)
    base = Path(tempfile.mkdtemp(prefix="swfresh_r3_"))
    builtins.open, io.open, pd.read_parquet, socket.socket.connect = g_open, g_open, g_read_parquet, g_connect
    C.yahoo_daily = boom("yahoo_daily"); C.fetch_news = boom("fetch_news")
    S.a_share_industry_returns = boom("a_share_industry_returns"); S.us_changes = boom("us_changes"); G.legs = boom("legs")
    try:
        run_tests(base)
    finally:
        builtins.open, io.open, pd.read_parquet, socket.socket.connect = _open, _io_open, _read_parquet, _connect
        C.ROOT, S.R, G.R, G.OUT, sys.argv = saved["C_ROOT"], saved["S_R"], saved["G_R"], saved["G_OUT"], saved["argv"]
        RUN.OUT, RUN.HIST, RUN.STATE, RUN.STUDY, RUN.pull_markets = saved["run"]
        C.yahoo_daily, C.fetch_news, S.a_share_industry_returns, S.us_changes, G.legs, C._POOL = saved["yd"], saved["fn"], saved["sa"], saved["su"], saved["gl"], saved["pool"]
        shutil.rmtree(base, ignore_errors=True)
    check("守卫：没有读写真实 data/output、没有联网、没有越过停跑调用数据加载", not violations)
    if violations: print("  violations:", violations[:10])
    check("临时目录已在 finally 中清理", not base.exists())
    print(f"\n{ok}/{ok+len(fails)} passed"); sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
