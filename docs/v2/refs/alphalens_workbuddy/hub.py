"""市场快照中枢 — 全站唯一的数据出口

问题:每次开页面都现拉数据,NeoData 一批 10 只要 20 次串行请求 → 40 秒白屏。

做法:
- 后台常驻刷新循环,把「行情 / 日线 / 板块资金 / ETF / 量化清单 / 配置」全部算好放内存;
- HTTP 接口只做内存读取 + 序列化,冷启动也不阻塞(返回 warming 状态);
- 量化用内存里的行情+K线重算,不需要任何网络请求 → 可以做到 30-60 秒重算一次;
- 每个快照带 updated_at / age_s / stale,前端可显示"数据 X 秒前",不做假实时。

刷新节奏(交易时段):
  行情 8s · 量化 45s · 板块资金 60s · 日线 180s · ETF 120s · 配置 180s
非交易时段全部降速 4-10 倍,避免无意义的请求。
"""
from __future__ import annotations

import asyncio
import time
import traceback
from datetime import datetime
from typing import Any, Awaitable, Callable

from .. import config
from ..dataflows import kline as kline_df
from ..dataflows import mcp_source as mcp
from ..dataflows import quotes as quote_df
from ..dataflows import tushare_gw as ts_gw
from ..quant import engine

# 大盘 / 风格基准
BENCH_SECID = "1.000300"
INDEX_SECIDS = ["1.000001", "0.399001", "0.399006", "1.000688", "1.000300", "100.HSI", "105.NDX", "105.SPX"]

# 25+ 行业 ETF(覆盖申万一级主要行业,A股)
SECTOR_ETFS: list[dict] = [
    {"id": "semi", "name": "半导体", "secid": "1.512480"},
    {"id": "chip", "name": "芯片", "secid": "0.159995"},
    {"id": "medicine", "name": "医药", "secid": "1.512010"},
    {"id": "medical", "name": "医疗", "secid": "1.512170"},
    {"id": "bank", "name": "银行", "secid": "1.512800"},
    {"id": "broker", "name": "证券", "secid": "1.512880"},
    {"id": "defense", "name": "军工", "secid": "1.512660"},
    {"id": "liquor", "name": "白酒", "secid": "1.512690"},
    {"id": "consumer", "name": "消费", "secid": "0.159928"},
    {"id": "food", "name": "食品饮料", "secid": "1.515170"},
    {"id": "solar", "name": "光伏", "secid": "1.515790"},
    {"id": "ev", "name": "新能源车", "secid": "1.515030"},
    {"id": "newenergy", "name": "新能源", "secid": "1.516160"},
    {"id": "metal", "name": "有色金属", "secid": "1.512400"},
    {"id": "estate", "name": "房地产", "secid": "1.512200"},
    {"id": "coal", "name": "煤炭", "secid": "1.515220"},
    {"id": "steel", "name": "钢铁", "secid": "1.515210"},
    {"id": "material", "name": "建材", "secid": "0.159745"},
    {"id": "chemical", "name": "化工", "secid": "0.159870"},
    {"id": "agri", "name": "农业", "secid": "0.159825"},
    {"id": "appliance", "name": "家电", "secid": "0.159996"},
    {"id": "auto", "name": "汽车", "secid": "1.516110"},
    {"id": "computer", "name": "计算机", "secid": "1.512720"},
    {"id": "telecom", "name": "通信", "secid": "1.515880"},
    {"id": "media", "name": "传媒", "secid": "1.512980"},
    {"id": "env", "name": "环保", "secid": "1.512580"},
    {"id": "power", "name": "电力", "secid": "0.159611"},
    {"id": "infra", "name": "基建", "secid": "1.516950"},
    {"id": "rare", "name": "稀土", "secid": "1.516780"},
    {"id": "robot", "name": "机器人", "secid": "1.562500"},
]

CORE_ETFS = [
    {"id": "hs300", "name": "沪深300", "secid": "1.510300", "role": "核心"},
    {"id": "zz500", "name": "中证500", "secid": "1.510500", "role": "核心"},
    {"id": "kc50", "name": "科创50", "secid": "1.588000", "role": "成长"},
    {"id": "cyb", "name": "创业板指", "secid": "0.159915", "role": "成长"},
    {"id": "zz1000", "name": "中证1000", "secid": "1.512100", "role": "小盘"},
    {"id": "zz2000", "name": "中证2000", "secid": "1.563300", "role": "小盘"},
    {"id": "dividend", "name": "红利", "secid": "1.510880", "role": "防守"},
]


def _is_cn_open(now: datetime | None = None) -> bool:
    from ..market import is_open
    return is_open("CN", now)


def _is_us_open(now: datetime | None = None) -> bool:
    from ..market import is_open
    return is_open("US", now)


class Hub:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        self.at: dict[str, float] = {}
        self.ttl: dict[str, float] = {}
        self.err: dict[str, str] = {}
        self.busy: set[str] = set()
        self.task: asyncio.Task | None = None
        self.started_at = time.time()
        self.cycles = 0

    # ---------- 读写 ----------
    def get(self, key: str) -> Any:
        return self.data.get(key)

    def age(self, key: str) -> float | None:
        t = self.at.get(key)
        return None if t is None else round(time.time() - t, 1)

    def put(self, key: str, value: Any, ttl: float = 60) -> None:
        self.data[key] = value
        self.at[key] = time.time()
        self.ttl[key] = ttl
        self.err.pop(key, None)

    def stale(self, key: str) -> bool:
        t = self.at.get(key)
        return t is None or (time.time() - t) > self.ttl.get(key, 60)

    def meta(self, key: str) -> dict:
        return {"updated_at": datetime.fromtimestamp(self.at[key]).strftime("%H:%M:%S") if key in self.at else None,
                "age_s": self.age(key), "stale": self.stale(key)}

    async def refresh(self, key: str, fn: Callable[[], Awaitable[Any]], ttl: float) -> Any:
        if key in self.busy:
            return self.data.get(key)
        self.busy.add(key)
        try:
            val = await fn()
            if val is not None:
                if key in ("bars","flow_stock","sector_flow","quotes","etf_flow_map") and not val:
                    self.err[key]="empty_source_response"
                    return self.data.get(key)
                self.put(key, val, ttl)
            return val
        except Exception as e:  # noqa: BLE001
            self.err[key] = f"{type(e).__name__}: {e}"
            return self.data.get(key)
        finally:
            self.busy.discard(key)

    # ---------- 组合视图 ----------
    def quotes_view(self, secids: list[str]) -> dict:
        qs = self.data.get("quotes") or {}
        out, missing = {}, []
        for s in secids:
            if s in qs:
                from ..market import quote_view
                out[s] = quote_view(qs[s])
            else:
                missing.append(s)
        return {"quotes": out, "missing": missing, **self.meta("quotes")}

    def status(self) -> dict:
        return {
            "uptime_s": round(time.time() - self.started_at, 1),
            "cycles": self.cycles,
            "keys": {k: {**self.meta(k), "ttl": self.ttl.get(k), "error": self.err.get(k)} for k in self.data},
            "market_open": {"cn": _is_cn_open(), "us": _is_us_open()},
        }


hub = Hub()

# CPU 密集任务(量化打分/配置)专用线程池 —— 绝不能跑在事件循环里
_EXEC = __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor(max_workers=2)


# ---------------- 各数据源的刷新逻辑 ----------------

def _universe() -> tuple[list[dict], dict[str, str], dict[str, str]]:
    """返回 (标的清单, 行业标签, 名称);由 warm 阶段填充"""
    return hub.get("universe") or [], hub.get("sector_of") or {}, hub.get("name_of") or {}


async def _build_universe() -> list[dict]:
    from ..dataflows.universe import SECTORS
    from ..quant.rotation import broad_universe

    items: list[dict] = []
    name_of: dict[str, str] = {}
    sector_of: dict[str, str] = {}
    seen: set[str] = set()
    for sec in SECTORS:
        for st in sec["stocks"]:
            if "ETF" in st["name"] or st["secid"] in seen:
                continue
            seen.add(st["secid"])
            items.append({"secid": st["secid"], "name": st["name"], "sector": sec["name"]})
            name_of[st["secid"]] = st["name"]
            sector_of[st["secid"]] = sec["name"]
    try:
        for u in await broad_universe(240):
            if u["secid"] in seen:
                continue
            seen.add(u["secid"])
            items.append({"secid": u["secid"], "name": u["name"], "sector": u["industry"]})
            name_of[u["secid"]] = u["name"]
            sector_of[u["secid"]] = u["industry"]
    except Exception:
        pass
    hub.put("name_of", name_of, 86400)
    hub.put("sector_of", sector_of, 86400)
    return items


async def _refresh_quotes(secids: list[str] | None = None) -> None:
    """行情刷新;两条循环(高频热集 / 低频全量)共用,直接写入 quotes,避免互相覆盖"""
    from ..market import normalize_secid
    uni = hub.get("universe") or []
    if secids is None:
        secids = [u["secid"] for u in uni]
    secids = list(dict.fromkeys(list(secids) + INDEX_SECIDS + [e["secid"] for e in SECTOR_ETFS + CORE_ETFS]))
    fresh = await quote_df.get_quotes([normalize_secid(s) for s in secids])
    merged = dict(hub.get("quotes") or {})
    valid = [q for q in fresh if q.get("price")]
    if not valid:
        hub.err["quotes"] = "empty_source_response"
        return
    from ..market import quote_quality
    fresh = [quote_quality(q) for q in valid]
    for q in fresh:
        if q.get("price"):
            merged[q["secid"]] = q
    hub.put("quotes", merged, 4)


def _hot_secids() -> list[str]:
    """高频刷新集:指数 + 行业/宽基 ETF + 推荐 TOP + 重点池(约 130 只)"""
    uni = hub.get("universe") or []
    focus = [u["secid"] for u in uni if u.get("sector") in ("半导体设备", "科技", "半导体材料", "创新药")]
    top = [r["secid"] for r in ((hub.get("quant") or {}).get("top") or [])[:20]]
    from ..runtime.store import store
    tracked=[p["secid"] for p in store.collection("holdings")+store.collection("watchlist")]
    return list(dict.fromkeys(tracked + focus + top + INDEX_SECIDS + [e["secid"] for e in SECTOR_ETFS + CORE_ETFS]))


def _focus_secids() -> list[str]:
    from ..dataflows.universe import SECTORS
    out = []
    for sec in SECTORS:
        for st in sec["stocks"]:
            if "ETF" not in st["name"]:
                out.append(st["secid"])
    return list(dict.fromkeys(out))


async def _refresh_bars(secids: list[str] | None = None) -> dict:
    """拉日线;传入 secids 时只更新这批(用于分阶段预热),已缓存的继续保留"""
    uni = hub.get("universe") or []
    extra = [BENCH_SECID] + [e["secid"] for e in SECTOR_ETFS + CORE_ETFS] + INDEX_SECIDS
    targets = list(dict.fromkeys((secids or [u["secid"] for u in uni]) + extra))
    batch = await mcp.nd_klines_batch(targets, "day", 260) if mcp.mcp_available("neodata") else {}
    from ..market import normalize_bars
    fetched = {sid: normalize_bars(v["bars"]) for sid, v in batch.items() if v.get("bars")}
    bars = {**(hub.get("bars") or {}), **fetched}

    # 基准指数 + ETF 若没覆盖,单独补
    extra = [BENCH_SECID] + [e["secid"] for e in SECTOR_ETFS + CORE_ETFS] + INDEX_SECIDS
    miss = [s for s in targets if s not in fetched]

    async def one(s: str):
        try:
            k = await asyncio.wait_for(kline_df.get_kline(s, limit=260), timeout=12)
            return s, k["bars"]
        except Exception:
            return s, None

    if miss:
        for s, b in await asyncio.gather(*(one(s) for s in miss)):
            if b:
                bars[s] = b
    return bars


async def _refresh_sector_flow() -> dict:
    from ..dataflows import sectors as sector_df
    rows = await sector_df.flow_rank("industry", 0, 500)
    by_name = {}
    for r in rows:
        by_name[r["name"]] = dict(r)
    return by_name


async def _refresh_flow_stock() -> dict:
    from ..dataflows import tsboard
    try:
        sf = await tsboard.stock_flow()
        return sf or {}
    except Exception:
        return {}


async def _refresh_etf() -> list[dict]:
    items = SECTOR_ETFS + CORE_ETFS
    bars = hub.get("bars") or {}
    quotes = hub.get("quotes") or {}
    bench = bars.get(BENCH_SECID) or []
    bcl = [b["close"] for b in bench]

    def bret(n: int) -> float:
        return (bcl[-1] / bcl[-n - 1] - 1) * 100 if len(bcl) > n and bcl[-n - 1] else 0.0

    br20, br60, br120 = bret(20), bret(60), bret(120)

    rows = [];crowding_rows=[]
    for it in items:
        b = bars.get(it["secid"]) or []
        f = engine.factors(b, bcl or None) if len(b) >= 30 else None
        q = quotes.get(it["secid"], {})
        if not f:
            continue
        crowding_rows.append({'secid':it['secid'],'name':it['name'],**f})
        rows.append({
            "id": it["id"], "name": it["name"], "secid": it["secid"],
            "role": it.get("role", "行业"),
            "price": round(f["last"], 3),
            "price_as_of": b[-1]['date'],
            "ret20_from": b[-21]['date'] if len(b)>20 else None,
            "pct": q.get("pct"),
            "ret5": f["ret5"], "ret20": f["ret20"], "ret60": f["ret60"], "ret120": f["ret120"],
            "excess20": f['excess20'],
            "excess60": f['excess60'],
            "excess120": f['excess120'],
            "rsi14": round(f["rsi14"], 1) if f["rsi14"] else None,
            "pos120": round(f["pos120"], 1),
            'pos120_partial':f['pos120_partial'],
            "vol_annual": round(f["vol20_annual"], 1) if f["vol20_annual"] else None,
            "atr_pct": round(f["atr_pct"], 2) if f["atr_pct"] else None,
            "vol_ratio": round(f["vol_ratio"], 2) if f["vol_ratio"] else None,
            "trend": f["trend"],
            "ma20": round(f["ma20"], 3) if f["ma20"] else None,
            "ma60": round(f["ma60"], 3) if f["ma60"] else None,
            "bias20": round(f["bias20"], 2) if f["bias20"] else None,
        })

    # 资金面由独立的 etf_flow 循环维护;这里只做合并,避免被重建冲掉
    fmap = hub.get("etf_flow_map") or {}
    for r in rows:
        if r["secid"] in fmap:
            r["flow"] = fmap[r["secid"]]

    # 拥挤度 = 位置 + 相对大盘超额(60/120日)+ 短期乖离 + 放量
    # 旧版只有"位置+乖离",大盘下跌时 BIAS 为负会把拥挤度算低 —— 这是银行被误判为"低拥挤"的原因
    from ..quant.crowding import etf_crowding
    policy=etf_crowding(crowding_rows)
    for r in rows:
        r.update(policy[r['secid']])
    return rows


async def _refresh_etf_flow() -> list[dict]:
    """ETF 资金面单独刷新,不阻塞量化首屏(37 只主力净买 + 7 只宽基份额申赎)"""
    rows = hub.get("etf") or []
    if not rows:
        return rows
    try:
        from . import etf_flow as eflow
        all_ids = [r["secid"] for r in rows]
        main = await eflow.etf_flow(all_ids, bars=hub.get("bars") or {}, with_shares=False)
        shares = await eflow._shares([e["secid"] for e in CORE_ETFS])
        fmap = {}
        for r in rows:
            d = main.get(r["secid"]) or {}
            d = {**d, **(shares.get(r["secid"]) or {})}
            eflow.enrich(d,(hub.get("bars") or {}).get(r["secid"]) or [],(hub.get("quotes") or {}).get(r["secid"]))
            if d:
                fmap[r["secid"]] = d
        if fmap:
            hub.put("etf_flow_map", fmap, 1800)
        for r in rows:
            if r["secid"] in fmap:
                r["flow"] = fmap[r["secid"]]
        hub.put("etf", rows, 120)
    except Exception:
        pass
    return rows


def _sector_scores(etf_rows: list[dict], flow: dict) -> dict[str, float]:
    """板块评分(0-1):20/60 日动量 + 趋势 + 资金 + 反拥挤。用于给个股的板块因子"""
    if not etf_rows:
        return {}
    r20 = [r["ret20"] for r in etf_rows if r["ret20"] is not None]
    r60 = [r["ret60"] for r in etf_rows if r["ret60"] is not None]
    out = {}
    for r in etf_rows:
        p20 = engine._pct_rank(r20, r["ret20"])
        p60 = engine._pct_rank(r60, r["ret60"])
        trend = 1.0 if r["trend"] == "多头排列" else (0.0 if r["trend"] == "空头排列" else 0.5)
        anti = 1 - r["crowd"]
        flow_s = 0.5
        f = flow.get(r["name"])
        if f:
            flow_s = 0.85 if f["main_net_inflow"] > 0 else 0.35
        out[r["name"]] = round(0.35 * p20 + 0.25 * p60 + 0.2 * trend + 0.12 * anti + 0.08 * flow_s, 3)
        out[r["secid"]] = out[r["name"]]
    return out


async def _settle_memory() -> None:
    """到期结算历史决策 —— 没有这一步,记忆就是只写不读的死账本"""
    try:
        from ..agents import memory
        await memory.settle_pending()
    except Exception:
        pass


def _compute_quant() -> dict:
    """同步计算量化快照(CPU 密集:327 只 × 8 因子),丢线程池执行,别占事件循环"""
    quotes = hub.get("quotes") or {}
    bars = hub.get("bars") or {}
    from ..market import bars_quality,market_of
    quality={sid:bars_quality(bs,(quotes.get(sid) or {}).get('market',market_of(sid))) for sid,bs in bars.items()}
    bars={sid:bs for sid,bs in bars.items() if quality[sid]['quality']=='current'}
    hub.put('bar_quality',quality,180)

    etf_rows = hub.get("etf") or []
    flow = hub.get("flow_stock") or {}
    sector_of = hub.get("sector_of") or {}
    name_of = hub.get("name_of") or {}
    sector_flow = hub.get("sector_flow") or {}

    sscore = _sector_scores(etf_rows, sector_flow)
    alias = {
        "半导体设备": "半导体", "半导体材料": "半导体", "科技": "计算机", "创新药": "医药",
        "半导体": "半导体", "元器件": "半导体", "电子元件": "半导体",
        "软件服务": "计算机", "IT设备": "计算机", "通信设备": "通信", "电信运营": "通信",
        "化学制药": "医药", "生物制品": "医药", "中成药": "医药", "医疗服务": "医疗",
        "银行": "银行", "证券": "证券", "保险": "证券",
        "白酒": "白酒", "啤酒": "白酒", "红黄酒": "白酒", "食品": "食品饮料", "软饮料": "食品饮料",
        "普钢": "钢铁", "特种钢": "钢铁", "钢加工": "钢铁",
        "新型电力": "电力", "火力发电": "电力", "水力发电": "电力", "电气设备": "电力",
        "小金属": "有色金属", "铜": "有色金属", "铝": "有色金属", "黄金": "有色金属",
        "化工原料": "化工", "化学制品": "化工", "农药化肥": "化工",
        "建筑施工": "基建", "工程建设": "基建", "水泥": "建材", "玻璃": "建材",
        "种植业": "农业", "养殖业": "农业", "饲料": "农业",
        "汽车整车": "汽车", "汽车配件": "汽车", "汽车服务": "汽车",
        "家用电器": "家电", "家居用品": "家电",
        "影视音像": "传媒", "广告包装": "传媒", "出版业": "传媒",
        "环境保护": "环保", "水务": "环保",
        "房地产": "房地产", "园区开发": "房地产",
        "煤炭开采": "煤炭", "焦炭加工": "煤炭",
        "装修装饰": "建材", "机械基件": "机器人", "专用机械": "机器人", "机床制造": "机器人",
        "电气自控": "机器人", "仪器仪表": "通信", "电子信息": "计算机",
    }
    sector_score = dict(sscore)
    for src, dst in alias.items():
        if dst in sscore:
            sector_score[src] = sscore[dst]

    scrowd = {r["name"]: r["crowd"] for r in etf_rows if r.get("crowd") is not None}
    sector_crowd = dict(scrowd)
    for src, dst in alias.items():
        if dst in scrowd:
            sector_crowd[src] = scrowd[dst]

    # 每个市场用自己的基准算超额:美股用纳指,港股用恒指。
    # 用沪深300 给美股算超额,A 股跌纳指涨时所有美股都"超额 +20pp",排序整个错乱
    bench_by_market = {
        "CN": bars.get(BENCH_SECID) or [],
        "US": bars.get("105.SPX") or [],
        "HK": bars.get("100.HSI") or [],
    }

    res = engine.build_markets(quotes, bars, bench_by_market=bench_by_market, flow=flow,
                                sector_score=sector_score, sector_crowd=sector_crowd,
                                sector_of=sector_of, name_of=name_of,
                                universe={u["secid"] for u in (hub.get("universe") or [])})
    res["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    res["indices"] = [
        {"secid": s, "name": (quotes.get(s) or {}).get("name", s), "price": (quotes.get(s) or {}).get("price"),
         "pct": (quotes.get(s) or {}).get("pct"), "status": (quotes.get(s) or {}).get("market_status")}
        for s in INDEX_SECIDS if (quotes.get(s) or {}).get("price")
    ]
    res["count"] = len(res.get("rows") or [])
    try:
        from ..quant import paper
        paper.record(res, bars)
    except Exception:
        pass
    return res


async def _refresh_macro() -> dict:
    from . import macro as macro_df
    return await macro_df.macro_snapshot()


async def _refresh_flash() -> list:
    from . import news as news_df
    items = await news_df.get_flash(15)
    return items if isinstance(items, list) else (items or {}).get("items") or []


async def _refresh_vitality() -> dict:
    """市场活力:涨跌停/连板/龙虎榜/两融/期指基差(RDS 可用但此前从未接线)"""
    from . import vitality as vit
    return await vit.vitality()


async def _refresh_quant() -> dict:
    """CPU 密集计算丢线程池(实测同步执行会让 /api/health 从 1ms 冻结到 1.2s)"""
    return await asyncio.get_running_loop().run_in_executor(_EXEC, _compute_quant)


async def _refresh_allocation() -> dict:
    from ..quant.allocation import present_allocation

    def _run():
        etfs=hub.get('etf') or [];bars=hub.get('bars') or {};quotes=hub.get('quotes') or {}
        from ..market import bars_quality
        bars={s:b for s,b in bars.items() if bars_quality(b,'CN')['quality']=='current'}
        ids={e['secid'] for e in etfs}
        snapshot=engine.build_etf_universe({sid:quotes.get(sid) or {'price':bars[sid][-1]['close'],'market':'CN','name':next(e['name'] for e in etfs if e['secid']==sid)} for sid in ids if bars.get(sid)},
            bars,bench_bars=bars.get(BENCH_SECID),universe=ids,name_of={e['secid']:e['name'] for e in etfs})
        hub.put('etf_strategy',snapshot,180)
        return present_allocation(etfs,snapshot)

    return await asyncio.get_running_loop().run_in_executor(_EXEC, _run)


# ---------------- 调度 ----------------

async def _loop(name: str, fn: Callable[[], Awaitable[Any]], base_ttl: float, key: str | None = None) -> None:
    key = key or name
    while True:
        try:
            await hub.refresh(key, fn, base_ttl)
            hub.cycles += 1
        except Exception:
            hub.err[key] = traceback.format_exc(limit=1)
        slow = not (_is_cn_open() or _is_us_open())
        await asyncio.sleep(base_ttl * (4 if slow else 1))


async def start() -> None:
    """启动常驻刷新;首次全量预热后进入稳态"""
    if hub.task and not hub.task.done():
        return

    async def supervisor() -> None:
        # 1) 基础清单(需要 RDS,可能失败,失败也要能跑)
        try:
            uni = await asyncio.wait_for(_build_universe(), timeout=30)
            hub.put("universe", uni, 3600)
        except Exception:
            hub.put("universe", [], 300)

        # 2) 行情 + 重点池 K 线(首屏必需的先来)
        await asyncio.gather(
            hub.refresh("quotes", _refresh_quotes, 8),
            hub.refresh("bars", lambda: _refresh_bars(_focus_secids()), 180),
            return_exceptions=True,
        )
        # 3) 量化只需要 etf/flow_stock,其余(含慢的 sector_flow/vitality/macro)全部后台跑,
        #    不要把首屏堵在慢源上 —— 实测全量 gather 会让第一次可用时间从 20s 拉到 76s
        for name, fn, ttl in (
            ("sector_flow", _refresh_sector_flow, 60),
            ("vitality", _refresh_vitality, 900),
            ("macro", _refresh_macro, 600),
            ("flash", _refresh_flash, 45),
            # 全市场个股资金流冷启动要 40-60s,不能让它挡住首屏;量化先按 0.5 中性资金分算
            ("flow_stock", _refresh_flow_stock, 120),
            ("etf_flow", _refresh_etf_flow, 300),
        ):
            asyncio.create_task(hub.refresh(name, fn, ttl))  # noqa: RUF006
        await hub.refresh("etf", _refresh_etf, 120)
        await hub.refresh("quant", _refresh_quant, 45)
        await hub.refresh("allocation", _refresh_allocation, 180)

        # 4) 再补全市场 K 线并重算(不阻塞上面的结果)
        asyncio.create_task(hub.refresh("bars", _refresh_bars, 180))  # noqa: RUF006
        await asyncio.sleep(20)
        await hub.refresh("quant", _refresh_quant, 45)
        await hub.refresh("allocation", _refresh_allocation, 180)

        # 4) 稳态循环
        await asyncio.gather(
            _loop("quotes", lambda: _refresh_quotes(_hot_secids()), 3),
            _loop("quotes_all", _refresh_quotes, 60),
            _loop("bars", _refresh_bars, 180),
            _loop("sector_flow", _refresh_sector_flow, 60),
            _loop("flow_stock", _refresh_flow_stock, 120),
            _loop("etf", _refresh_etf, 120),
            _loop("vitality", _refresh_vitality, 900),
            _loop("etf_flow", _refresh_etf_flow, 300),
            _loop("macro", _refresh_macro, 600),
            _loop("flash", _refresh_flash, 45),
            _loop("quant", _refresh_quant, 45),
            _loop("allocation", _refresh_allocation, 180),
            _loop("memory_settle", _settle_memory, 600),
            _loop("universe", lambda: _build_universe(), 1800),
        )

    hub.task = asyncio.create_task(supervisor())


def ready() -> bool:
    return bool((hub.get("quant") or {}).get("rows") and hub.get("quotes"))


def snapshot() -> dict:
    return {
        "ready": ready(),
        "status": hub.status(),
        "quotes": hub.get("quotes") or {},
        "quant": hub.get("quant") or {},
        "allocation": hub.get("allocation") or {},
        "etf": hub.get("etf") or [],
        "sector_flow": hub.get("sector_flow") or {},
        "meta": {k: hub.meta(k) for k in ("quotes", "bars", "quant", "etf", "sector_flow", "allocation")},
    }
