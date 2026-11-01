"""sw_pit 过期 + 完整性检查自测（r2）：临时目录自建 ROOT（manifest、小 parquet、trade_cal），不依赖线上值、不联网、不写正式输出。"""
import sys, json, hashlib, tempfile, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd, intel_common as C
ok, fails = 0, []
def check(n, c):
    global ok
    if c: ok += 1
    else: fails.append(n)
    print("PASS" if c else "FAIL", n)

def make_root(built="2026-10-14T04:00:00", cal_days=None, sha_ok=True, with_manifest=True, with_parquet=True):
    r = Path(tempfile.mkdtemp(prefix="swfresh_"))
    (r / "data/v2/sw_pit").mkdir(parents=True); (r / "data/v2/calendar").mkdir(parents=True)
    pq = r / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet"
    pd.DataFrame({"instrument_id": ["sh.600000"], "in_date": pd.to_datetime(["2026-09-24"]), "out_date": pd.to_datetime([None])}).to_parquet(pq)
    sha = hashlib.sha256(pq.read_bytes()).hexdigest() if sha_ok else "0" * 64
    if not with_parquet: pq.unlink()
    # 交易日历：2026-10-08 起逐日，周末休市（10-01~07 国庆休市不在范围内）
    days = pd.date_range("2026-10-08", "2026-10-23")
    pd.DataFrame({"cal_date": days.strftime("%Y%m%d"), "is_open": [int(d.weekday() < 5) for d in days],
                  "pretrade_date": "", "available_at": pd.Timestamp("2025-12-31 09:00")}).to_parquet(r / C.TRADE_CAL)
    if with_manifest:
        (r / "data/v2/sw_pit/manifest.json").write_text(json.dumps({"l1": {"in_date_range": ["1984-05-09", "2026-09-24"]}, "built": built,
                                                                   "sha256": {"sw_pit/industry_members_sw_l1_pit.parquet": sha}}))
    # 日线目录故意缺 10-15（中转故障），检查不应受影响
    (r / "data/v2/tushare_raw/daily").mkdir(parents=True)
    for d in ("20261013", "20261014", "20261016"):
        (r / f"data/v2/tushare_raw/daily/{d}.parquet").write_bytes(b"")
    return r

roots = []
def R(**k):
    r = make_root(**k); roots.append(r); return r

r0 = R()
f = C.check_table_freshness("sw_pit", "2026-10-18", r0)
check("返回字段齐全", set(f) == {"table", "max_date", "built", "covered_through", "lag_days", "status", "disclosure"})
check("基准：built 10-14 04:00 美东 = 16:00 上海 → 覆盖到 10-13，asof 10-18 落后 3 → stale",
      f["covered_through"] == "2026-10-13" and f["lag_days"] == 3 and f["status"] == "stale")
check("日线缺 10-15 时落后天数仍为 3（交易日取自 trade_cal）", f["lag_days"] == 3)
check("asof 10-15 → 落后 2 → ok", C.check_table_freshness("sw_pit", "2026-10-15", r0)["status"] == "ok")
# 美东解释跨上海 18:00 边界：05:59 美东 = 17:59 上海（覆盖前一交易日）；06:00 美东 = 18:00 上海（覆盖当日）
a = C.check_table_freshness("sw_pit", "2026-10-18", R(built="2026-10-14T05:59:00"))
b = C.check_table_freshness("sw_pit", "2026-10-18", R(built="2026-10-14T06:00:00"))
check("美东 05:59（上海 17:59）→ 覆盖 10-13、落后 3", a["covered_through"] == "2026-10-13" and a["lag_days"] == 3)
check("美东 06:00（上海 18:00）→ 覆盖 10-14、落后 2、ok", b["covered_through"] == "2026-10-14" and b["lag_days"] == 2 and b["status"] == "ok")
c = C.check_table_freshness("sw_pit", "2026-10-18", R(built="2026-10-13T20:00:00"))
check("美东 10-13 20:00 = 上海 10-14 08:00 → 覆盖 10-13（不是按美东日期算 10-13 收盘后）", c["covered_through"] == "2026-10-13")
def hard(name, root):
    try:
        C.check_table_freshness("sw_pit", "2026-10-18", root); check(name + "：check 抛完整性错误", False)
    except C.TableIntegrityError:
        check(name + "：check 抛完整性错误", True)
    for allow in (False, True):
        try:
            C.require_fresh("sw_pit", "2026-10-18", allow_stale=allow, root=root); check(f"{name}：require_fresh(allow_stale={allow}) 硬停", False)
        except SystemExit as e:
            check(f"{name}：require_fresh(allow_stale={allow}) 硬停", "HARD STOP" in str(e))
hard("sha 不一致", R(sha_ok=False))
hard("manifest 缺失", R(with_manifest=False))
hard("parquet 缺失", R(with_parquet=False))
try:
    C.require_fresh("sw_pit", "2026-10-18", root=r0); check("stale 默认停跑（非硬停）", False)
except SystemExit as e:
    check("stale 默认停跑（非硬停）", str(e).startswith("STOP"))
check("--allow-stale 放行 stale 并带 disclosure", "STALE" in C.require_fresh("sw_pit", "2026-10-18", allow_stale=True, root=r0)["disclosure"])
# 研究脚本入口：在临时 ROOT 上调 main()，应在任何计算前停跑
import intel_event_study as S, intel_c1_gap_split as G
for mod in (S, G):
    old_root, old_argv = C.ROOT, sys.argv
    C.ROOT, sys.argv = r0, [mod.__file__]
    try:
        mod.main(); check(f"{Path(mod.__file__).name} 无 --allow-stale 时停跑", False)
    except SystemExit as e:
        check(f"{Path(mod.__file__).name} 无 --allow-stale 时停跑", str(e).startswith("STOP"))
    C.ROOT = R(sha_ok=False); sys.argv = [mod.__file__, "--allow-stale"]
    try:
        mod.main(); check(f"{Path(mod.__file__).name} sha 不一致 + --allow-stale 仍硬停", False)
    except SystemExit as e:
        check(f"{Path(mod.__file__).name} sha 不一致 + --allow-stale 仍硬停", "HARD STOP" in str(e))
    C.ROOT, sys.argv = old_root, old_argv
# intel_run 用途：完整性错误只停行业映射
C.ROOT, C._POOL = R(sha_ok=False), None
pool = C.industry_stocks()
check("intel_run 路径：完整性错误 → 空池 + source_status high", pool == {} and C.SW_FRESHNESS["status"] == "error" and C.SW_FRESHNESS["severity"] == "high")
sw = pd.DataFrame({"instrument_id": ["a", "b", "c"], "in_date": pd.to_datetime(["2026-09-24", "2026-09-01", "2026-08-01"]),
                   "out_date": pd.to_datetime([None, "2026-09-24", None])})
check("as-of：变动当天不可用、出表当天仍是成员", set(C.sw_members_asof(sw, "2026-09-24").instrument_id) == {"b", "c"})
check("as-of：次日生效", set(C.sw_members_asof(sw, "2026-09-25").instrument_id) == {"a", "c"})
for r in roots: shutil.rmtree(r, ignore_errors=True)
print(f"\n{ok}/{ok+len(fails)} passed"); sys.exit(1 if fails else 0)
