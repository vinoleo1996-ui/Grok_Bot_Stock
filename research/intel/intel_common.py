"""AI 情报师公共模块：数据源、规则表、个股映射。研究级，promotion_approved=false，live=false。
不下单、不改权重、禁 GP。只读盘上 sw_pit / mid_large；不读封存窗口（2018→2024-05）数据。"""
from __future__ import annotations
import json, re, urllib.request, urllib.parse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ET_TZ = ZoneInfo("America/New_York")
UA = {"User-Agent": "Mozilla/5.0 (QuantLab intel research)"}

# 行情：Yahoo chart v8（本机验证可用）。stooq 需 JS 校验、FRED CSV 超时 → 不可用（见回执）。
MARKETS = {
    "nasdaq": {"sym": "^IXIC", "name": "纳斯达克综指", "kind": "pct"},
    "sox":    {"sym": "^SOX", "name": "费城半导体", "kind": "pct"},
    "hxc":    {"sym": "^HXC", "name": "纳斯达克中国金龙", "kind": "pct"},
    "kweb":   {"sym": "KWEB", "name": "中概互联ETF(KWEB)", "kind": "pct"},
    "us10y":  {"sym": "^TNX", "name": "美债10年收益率", "kind": "bp"},   # ^TNX = 收益率(%)
    "dxy":    {"sym": "DX-Y.NYB", "name": "美元指数", "kind": "pct"},
    "n225":   {"sym": "^N225", "name": "日经225", "kind": "pct"},
    "kospi":  {"sym": "^KS11", "name": "韩国KOSPI", "kind": "pct"},
}


def yahoo_daily(sym: str, rng: str = "1mo") -> pd.Series:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range={rng}&interval=1d"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        j = json.load(r)
    res = j["chart"]["result"][0]
    tz = ZoneInfo(res["meta"].get("exchangeTimezoneName", "America/New_York"))
    ts = res.get("timestamp") or []
    cl = res["indicators"]["quote"][0].get("close") or []
    idx = [datetime.fromtimestamp(t, tz).date() for t in ts]
    s = pd.Series(cl, index=pd.to_datetime(idx), dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")]
    meta = res["meta"]
    s.attrs["live_price"] = meta.get("regularMarketPrice")
    s.attrs["market_time"] = meta.get("regularMarketTime")
    return s


# 冲击→申万一级 规则表。sign: 因子"坏消息"(指数跌/收益率升/美元升)时对该行业的预期方向（-1 偏空, +1 偏多）。
SHOCK_RULES = {
    "nasdaq": {"电子": -1, "计算机": -1, "通信": -1, "传媒": -1},
    "sox":    {"电子": -1, "计算机": -1, "通信": -1},
    "hxc":    {"传媒": -1, "商贸零售": -1, "社会服务": -1, "计算机": -1},
    "kweb":   {"传媒": -1, "商贸零售": -1, "社会服务": -1, "计算机": -1},
    "us10y":  {"房地产": -1, "电子": -1, "计算机": -1, "医药生物": -1, "银行": +1},
    "dxy":    {"有色金属": -1, "石油石化": -1, "煤炭": -1},
    "n225":   {"电子": -1, "汽车": -1, "机械设备": -1},
    "kospi":  {"电子": -1, "汽车": -1, "电力设备": -1},
}
# 强度阈值：pct 为单日涨跌%，bp 为单日变动 bp。|x|≥strong→强，≥mid→中，否则弱（弱不出行业冲击）。
THRESH = {"pct": {"mid": 1.0, "strong": 2.0}, "bp": {"mid": 5.0, "strong": 10.0}}
THRESH_OVERRIDE = {"dxy": {"mid": 0.5, "strong": 0.8}}

# 新闻：公开 RSS（Google News 搜索 RSS、CNBC、USTR）
NEWS_FEEDS = [
    ("GoogleNews", "https://news.google.com/rss/search?q=%22Section+337%22+ITC&hl=en-US&gl=US&ceid=US:en"),
    ("GoogleNews", "https://news.google.com/rss/search?q=export+controls+China+chips&hl=en-US&gl=US&ceid=US:en"),
    ("GoogleNews", "https://news.google.com/rss/search?q=tariff+China&hl=en-US&gl=US&ceid=US:en"),
    ("GoogleNews", "https://news.google.com/rss/search?q=%22Entity+List%22+Commerce&hl=en-US&gl=US&ceid=US:en"),
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("USTR", "https://ustr.gov/rss.xml"),
    ("GoogleNews", "https://news.google.com/rss/search?q=Strait+of+Hormuz+oil+Brent&hl=en-US&gl=US&ceid=US:en"),
]
# 关键词→(主题, 行业→方向, 严重度 1-3)
# 2026-10-18 修订：区分施动方向（谁管制谁）与否定/缓和词（暂停、豁免、撤回、延期…）。
#   - 关税：命中缓和词 → 「中美谈判缓和」(偏多)，否则 →「关税」(偏空)。
#   - 出口管制：中国作施动方（China/Beijing/MOFCOM 管制自身技术或商品出口）→「中国自身出口管制」(仅记录、不计分；
#     稀土等关键矿产仍由「稀土/关键矿产」规则单独计分)；美方管制且含缓和词 →「中美谈判缓和」；其余 →「出口管制/实体清单」(偏空)。
RELIEF_RE = (r"\b(pause[sd]?|pausing|suspend(s|ed|ing)?|suspension|waive[sd]?|waiving|waiver|exempt(s|ed|ion|ions)?|relief|relax(es|ed|ing)?|"
             r"withdraw(s|n|ing)?|withdrew|revoke[sd]?|rescind(s|ed)?|roll(s|ed)? back|rollback|scrap(s|ped)?|lift(s|ed|ing)?|"
             r"delay(s|ed)?|postpone[sd]?|extend(s|ed)? (the )?(truce|deadline|pause)|truce|deal|cut(s|ting)?|reduc(e|es|ed|tion)|lower(s|ed)?|ease[sd]?|easing|drop(s|ped)?)\b"
             r"|暂停|豁免|撤回|撤销|延期|推迟|取消|下调|降低|放宽")
CN_ACTOR_RE = (r"^(china|beijing|chinese (government|commerce ministry)|mofcom|china's (commerce|technology) ministr(y|ies))\b[^.]{0,60}?\b(propos|impos|announc|plan|unveil|tighten|"
               r"restrict|curb|ban|add|expand|issu|introduc|draft|mov|weigh|consider|to )"
               r"|^china('s)? (new |proposed |draft |planned )?(tech(nology)? )?export (control|curb|restriction|ban)"
               r"|\b(china|beijing) (proposes|imposes|announces|plans|unveils|tightens|expands|moves to curb)\b.*\bexport"
               r"|(商务部|中方|中国).{0,12}(出口管制|禁止出口|限制出口)")
EXPORT_RE = r"export control|entity list|chip (ban|curb|restriction)|semiconductor (curb|restriction)|bis rule|affiliates rule|出口管制|实体清单"
TARIFF_CN_RE = r"(tariff.*(china|chinese))|((china|chinese).*tariff)|(关税.*(中国|对华))|((中国|对华).*关税)"
NEWS_RULES = [
    ("337调查", r"section 337|\b337\b.*(itc|investigation)|itc .*investigation", {"电子": -1, "家用电器": -1, "机械设备": -1, "医药生物": -1}, 2),
    ("稀土/关键矿产", r"rare earth|critical mineral|gallium|germanium|antimony", {"有色金属": +1}, 2),
    # 2026-10-18 01:20 ET 新增：霍尔木兹/原油；严重度 1 = 仅记录，不单独触发 C 类重大新闻
    ("原油/霍尔木兹", r"hormuz|霍尔木兹|\bbrent\b|\bwti\b|crude|\boil (price|prices|tanker|tankers|supply)|原油|油价", {"石油石化": +1, "交通运输": -1}, 1),
]
EXPORT_US = ("出口管制/实体清单", {"电子": -1, "计算机": -1, "通信": -1}, 3)
EXPORT_CN_SELF = ("中国自身出口管制", {}, 1)
TARIFF_UP = ("关税", {"家用电器": -1, "纺织服饰": -1, "轻工制造": -1, "机械设备": -1, "汽车": -1, "电力设备": -1}, 2)
EASING = ("中美谈判缓和", {"家用电器": +1, "纺织服饰": +1, "电子": +1}, 2)


def fetch_news(max_age_h: float = 36.0) -> tuple[list[dict], dict]:
    now = datetime.now(timezone.utc)
    items, status = [], {}
    for src, url in NEWS_FEEDS:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                root = ET.fromstring(r.read())
            n = 0
            for it in root.iter("item"):
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                pd_ = it.findtext("pubDate")
                try:
                    t = parsedate_to_datetime(pd_) if pd_ else None
                except Exception:
                    t = None
                if t is None or (now - t).total_seconds() / 3600 > max_age_h:
                    continue
                items.append({"source": src, "title": title, "link": link, "published_et": t.astimezone(ET_TZ).strftime("%Y-%m-%d %H:%M")})
                n += 1
            status[url] = f"ok({n})"
        except Exception as e:
            status[url] = f"fail:{type(e).__name__}"
    seen, out = set(), []
    for x in items:
        k = x["title"].lower()[:90]
        if k not in seen:
            seen.add(k); out.append(x)
    return out, status


def classify_title(title: str) -> list[tuple[str, dict, int]]:
    """单条标题 → [(主题, 行业→方向, 严重度)]。同一主题只出一次。"""
    t = title.lower().strip()
    out = []
    relief = re.search(RELIEF_RE, t) is not None
    if re.search(EXPORT_RE, t):
        if re.search(CN_ACTOR_RE, t):
            out.append(EXPORT_CN_SELF)
        elif relief:
            out.append(EASING)
        else:
            out.append(EXPORT_US)
    if re.search(TARIFF_CN_RE, re.sub(r"non-tariff|非关税", " ", t)):
        out.append(EASING if relief else TARIFF_UP)
    elif re.search(r"trade (deal|truce|talks)", t):
        out.append(EASING)
    for theme, pat, inds, sev in NEWS_RULES:
        if re.search(pat, t):
            out.append((theme, inds, sev))
    seen, res = set(), []
    for th in out:
        if th[0] not in seen:
            seen.add(th[0]); res.append(th)
    return res


def classify_news(items: list[dict]) -> list[dict]:
    hits = []
    for x in items:
        for theme, inds, sev in classify_title(x["title"]):
            hits.append({**x, "theme": theme, "industries": inds, "severity": sev})
    return hits


# ---- 2026-10-18（r2，待 Arch 审）：读 sw_pit / cyq / tier3 前的过期 + 完整性检查；申万成分 as-of 取数 ----
# 主 Agent 10-18 05:06 ET 裁定：不得以 freshness overall=ok 为依据（不覆盖这三张表）。
# 只登记盘上确有 manifest 的表；cyq / tier3 目前 research/intel 下没有读取点，未登记（不编造路径）。
import hashlib as _hashlib
FRESHNESS_TABLES = {
    "sw_pit": {"manifest": "data/v2/sw_pit/manifest.json", "manifest_key": "l1",
               "parquet": "data/v2/sw_pit/industry_members_sw_l1_pit.parquet",
               "sha_key": "sw_pit/industry_members_sw_l1_pit.parquet",
               "quarantine_glob": "data/v2/_quarantine/sw_pit_INCOMPLETE_*"},
}
STALE_LAG_TRADING_DAYS = 3   # Arch 10-18 已定：落后 ≥3 个 A 股交易日 → stale（团队统一口径）
TRADE_CAL = "data/v2/calendar/trade_cal_sse_pit.parquet"   # 列：cal_date(str YYYYMMDD)、is_open(int 1=开市/0=休市)、pretrade_date、available_at
BUILT_TZ = ZoneInfo("America/New_York")   # P2-a：manifest.built 由 scripts/acquire/queue_chain_20261014.py 用 datetime.now() 写入，
                                          # 本机时区为美东 → 不带时区的美东时间；先按美东解释，再换算到上海套 18:00 规则
SH_TZ = ZoneInfo("Asia/Shanghai")


class TableIntegrityError(RuntimeError):
    """manifest 读不到 / parquet 缺失 / sha256 不一致 / built 或日历不可用：无条件硬停，--allow-stale 也不放行。"""


def _trading_days(root: Path) -> list:
    """P2-b：A 股交易日以上交所交易日历为准（is_open == 1），不再用日线文件名（中转故障时日线会缺）。"""
    cal = pd.read_parquet(root / TRADE_CAL, columns=["cal_date", "is_open"])
    days = sorted(pd.to_datetime(cal.loc[cal.is_open == 1, "cal_date"], format="%Y%m%d"))
    if not days:
        raise TableIntegrityError(f"交易日历无开市日（{TRADE_CAL}）")
    return days


def _parse_built(v) -> pd.Timestamp:
    """r3 P2-1：naive → 按美东 tz_localize（夏令时回拨的重复小时取夏令时 ambiguous=True，不存在的时刻 raise）；带时区 → tz_convert。"""
    ts = pd.Timestamp(v)
    ts = ts.tz_localize(BUILT_TZ, ambiguous=True, nonexistent="raise") if ts.tzinfo is None else ts.tz_convert(BUILT_TZ)
    return ts.tz_convert(SH_TZ)


def _reference_day(td: list, asof) -> pd.Timestamp:
    """r3 P3-2：参考日 = 上海时间最近一个已收盘的交易日（18:00 规则）。传入 asof（日期）时视为该日已收盘。"""
    if asof is None:
        now_sh = datetime.now(SH_TZ)
        today = pd.Timestamp(now_sh.date())
        cand = [d for d in td if d < today or (d == today and now_sh.hour >= 18)]
        ref_day = today
    else:
        ref_day = pd.Timestamp(asof).normalize()
        cand = [d for d in td if d <= ref_day]
    if td[-1] < ref_day:
        raise TableIntegrityError(f"交易日历只到 {td[-1].date()}，覆盖不到参考日 {ref_day.date()}")
    if not cand:
        raise TableIntegrityError(f"交易日历在参考日 {ref_day.date()} 之前没有开市日")
    return cand[-1]


def verify_sha(table: str, root: Path | None = None) -> str:
    """单独复核 parquet 实算 sha 与 manifest 一致（供读完数据后再查一次，缩小检查-读取窗口）。"""
    root = Path(root or ROOT); cfg = FRESHNESS_TABLES[table]
    try:
        man = json.loads((root / cfg["manifest"]).read_text())
        got = _hashlib.sha256((root / cfg["parquet"]).read_bytes()).hexdigest()
    except Exception as e:
        raise TableIntegrityError(f"{table}: 复核 sha 失败（{type(e).__name__}）")
    if (man.get("sha256") or {}).get(cfg["sha_key"]) != got:
        raise TableIntegrityError(f"{table}: 读后复核 sha256 不一致（实算 {got[:12]}…）")
    return got


def _check(table: str, asof=None, root: Path | None = None) -> tuple[dict, bytes]:
    root = Path(root or ROOT)
    cfg = FRESHNESS_TABLES[table]
    mp, pq = root / cfg["manifest"], root / cfg["parquet"]
    try:
        man = json.loads(mp.read_text())
    except Exception as e:
        raise TableIntegrityError(f"{table}: manifest 读不到（{cfg['manifest']}：{type(e).__name__}）")
    if not pq.exists():
        raise TableIntegrityError(f"{table}: parquet 缺失（{cfg['parquet']}）")
    data = pq.read_bytes()                     # r3 P3-4：校验和读取用同一份 bytes
    want = (man.get("sha256") or {}).get(cfg["sha_key"])
    got = _hashlib.sha256(data).hexdigest()
    if not want or want != got:
        raise TableIntegrityError(f"{table}: sha256 不一致（manifest {str(want)[:12]}… vs 实算 {got[:12]}…）")
    rng = man.get(cfg["manifest_key"], {}).get("in_date_range") or []
    if len(rng) != 2 or not man.get("built"):
        raise TableIntegrityError(f"{table}: manifest 缺 in_date_range 或 built")
    max_date = pd.Timestamp(rng[1])
    built_sh = _parse_built(man["built"])
    td = _trading_days(root)
    ref = _reference_day(td, asof)
    bd = pd.Timestamp(built_sh.date())
    if td[-1] < bd:
        raise TableIntegrityError(f"交易日历只到 {td[-1].date()}，覆盖不到 built 日 {bd.date()}")
    if built_sh.hour >= 18 and bd in td:
        cov = bd
    else:
        prev = [d for d in td if d < bd]
        if not prev:
            raise TableIntegrityError(f"交易日历在 built 日 {bd.date()} 之前没有开市日，无法计算覆盖日")
        cov = prev[-1]
    lag = sum(1 for d in td if cov < d <= ref)
    stale = lag >= STALE_LAG_TRADING_DAYS
    decision = str(pd.Timestamp(asof).date()) if asof is not None else datetime.now(ET_TZ).strftime("%Y-%m-%d %H:%M ET")
    quar = sorted(str(q.relative_to(root)) for q in root.glob(cfg["quarantine_glob"])) if cfg.get("quarantine_glob") else []
    disc = (f"{table}: built={man['built']}（无时区按美东）= {built_sh:%Y-%m-%d %H:%M} 上海，覆盖到 {cov.date()}，"
            f"落后 {lag} 个交易日（参考日 = 上海最近已收盘交易日 {ref.date()}，阈值 ≥{STALE_LAG_TRADING_DAYS}）；"
            f"最后一次成分变动 {max_date.date()}；sha256 校验通过")
    if quar:
        disc += f"；存在未完成刷新隔离目录 {', '.join(quar)}"
    return ({"table": table, "max_date": str(max_date.date()), "built": man["built"],
             "covered_through": str(cov.date()), "reference_day": str(ref.date()), "as_of_decision": decision,
             "lag_days": lag, "coverage_gap": lag >= 1,
             "status": "stale" if stale else "ok", "disclosure": disc + ("（STALE）" if stale else "")}, data)


_WRAP = (TypeError, ValueError, OSError, KeyError, AttributeError)   # AmbiguousTimeError / NonExistentTimeError 为 ValueError 子类；FileNotFoundError 为 OSError 子类


def check_and_load(table: str, asof=None, root: Path | None = None) -> tuple[dict, bytes]:
    """返回 (freshness dict, 已校验的 parquet bytes)。任何解析 / 日历 / IO 异常统一转成 TableIntegrityError。"""
    try:
        return _check(table, asof, root)
    except TableIntegrityError:
        raise
    except _WRAP as e:
        raise TableIntegrityError(f"{table}: 检查过程异常 {type(e).__name__}: {e}")


def check_table_freshness(table: str, asof=None, root: Path | None = None) -> dict:
    """返回 {table, max_date, built, covered_through, reference_day, as_of_decision, lag_days, coverage_gap, status: ok/stale, disclosure}；
    完整性问题抛 TableIntegrityError。"""
    return check_and_load(table, asof, root)[0]


def require_fresh(table: str, asof=None, allow_stale: bool = False, root: Path | None = None) -> dict:
    """事件研究 / 特征构建用：完整性错误无条件停；stale 默认停，allow_stale=True 放行并返回 disclosure 供写回执。"""
    try:
        f = check_table_freshness(table, asof, root)
    except TableIntegrityError as e:
        raise SystemExit(f"HARD STOP（完整性，--allow-stale 不放行）：{e}")
    print("[freshness]", json.dumps(f, ensure_ascii=False))
    if f["status"] != "ok" and not allow_stale:
        raise SystemExit(f"STOP：{f['disclosure']}。如需照跑请加 --allow-stale（disclosure 会写入回执）。")
    return f


def sw_members_asof(sw: pd.DataFrame, d) -> pd.DataFrame:
    """申万一级成分按时点取（as-of）：变动在 available_at（in_date 18:00 上海）之后才可用，
    所以交易日 d 只用 in_date < d 的成分；出表同理，out_date 当天收盘后才知道，d ≤ out_date 仍视为成员。"""
    d = pd.Timestamp(d).normalize()
    return sw[(sw.in_date < d) & (sw.out_date.isna() | (sw.out_date >= d))]


_POOL = None
SW_FRESHNESS = None


def industry_stocks(top_n: int = 5) -> dict[str, list[dict]]:
    """每个申万一级：mid_large 最新 session 中流通市值前 top_n（非小盘）；另附该行业流通市值最大的非池股票 1 只并标注小盘。"""
    global _POOL
    if _POOL is not None:
        return _POOL
    global SW_FRESHNESS
    # 情报预警：stale 不停跑，带 disclosure；完整性错误只停行业映射这一步（返回空池），
    # 并在 source_status 标 high 级错误，其余预警照常输出（全停方案见 _review 说明，待 Arch 定）
    # r3 P2-1：任何异常都不能让 intel_run 整体崩掉 → 统一按完整性错误走方案 A
    try:
        SW_FRESHNESS, _sw_bytes = check_and_load("sw_pit")
        import io as _io
        sw = pd.read_parquet(_io.BytesIO(_sw_bytes), columns=["instrument_id", "name", "l1_name", "in_date", "out_date"])
    except Exception as e:
        reason = str(e) if isinstance(e, TableIntegrityError) else f"sw_pit: {type(e).__name__}: {e}"
        SW_FRESHNESS = {"table": "sw_pit", "status": "error", "severity": "high", "reason": reason,
                        "disclosure": f"{reason}；本轮行业→个股映射已停（相关个股为空），行业预警照常输出"}
        _POOL = {}
        return _POOL
    # 原为 out_date.isna()（表内最新成分）；改为按今天（上海日期）as-of，含当天 18:00 前不可用的变动不计
    _sh = datetime.now(ZoneInfo("Asia/Shanghai"))
    sw = sw_members_asof(sw, pd.Timestamp(_sh.date()) + pd.Timedelta(days=1 if _sh.hour >= 18 else 0))
    sw = sw.drop_duplicates("instrument_id", keep="last")
    import pyarrow.dataset as ds
    mds = ds.dataset(ROOT / "data/v2/universe/mid_large_members_pit.parquet")
    last = max(pd.read_parquet(ROOT / "data/v2/universe/mid_large_members_pit.parquet", columns=["session"],
                               filters=[("session", ">=", "2026-09-01")]).session)
    ml = mds.to_table(columns=["instrument_id", "float_mktcap_basis"], filter=ds.field("session") == last).to_pandas()
    m = sw.merge(ml, on="instrument_id", how="left")
    # 非池股票（小盘）流通市值：用最新 daily_basic
    db_dir = ROOT / "data/v2/tushare_raw/daily_basic"
    small_mc = {}
    try:
        f = sorted(db_dir.glob("*.parquet"))[-1]
        db = pd.read_parquet(f, columns=["ts_code", "circ_mv"])
        for code, mv in zip(db.ts_code, db.circ_mv):
            a, ex = code.split(".")
            small_mc[f"{ex.lower()}.{a}"] = mv * 1e4
    except Exception:
        pass
    out = {}
    for ind, g in m.groupby("l1_name"):
        pool = g.dropna(subset=["float_mktcap_basis"]).sort_values("float_mktcap_basis", ascending=False).head(top_n)
        lst = [{"code": r.instrument_id, "name": r.name, "small_cap": False} for r in pool.itertuples()]
        rest = g[g.float_mktcap_basis.isna() & ~g.name.str.contains("退|ST")].copy()
        rest["mc"] = rest.instrument_id.map(small_mc)
        rest = rest.dropna(subset=["mc"]).sort_values("mc", ascending=False).head(1)
        lst += [{"code": r.instrument_id, "name": r.name, "small_cap": True} for r in rest.itertuples()]
        out[ind] = lst
    out["_pool_session"] = str(pd.Timestamp(last).date())
    _POOL = out
    return out


def alert_severity(call: str, strength: str) -> str:
    """Contract v1.1 explicit severity: 偏空+强 -> high; 观察/偏空(非强) -> watch; else info. Never invents a stance."""
    if call == "偏空" and strength == "强":
        return "high"
    if call in ("观察", "偏空"):
        return "watch"
    return "info"


def apply_alert_severity(alerts: list[dict]) -> list[dict]:
    for a in alerts:
        a["severity"] = alert_severity(a.get("call", ""), a.get("strength", ""))
    return alerts
