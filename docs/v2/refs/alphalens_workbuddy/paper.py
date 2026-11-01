"""纸面跟踪账本 — 用未来的价格检验模型,而不是用回测自证

为什么要有这个:
回测再严谨,也有幸存者偏差、参数挑选、执行假设。唯一能证明"能不能赚钱"的是:
从今天开始把信号记下来,用之后真实发生的价格结算。

做法:
- 每个交易日首次量化刷新时,把当日 TOP10(含止损/目标)写入 data/paper.jsonl(只写一次,不可改)
- 结算时用快照里的真实日线:建仓价 = 次一交易日开盘价,当前价 = 最新收盘
- 同时记录沪深300 同期涨跌,给出超额
- 只统计已满 5 个交易日的批次,避免"今天的信号今天吹"

诚实边界:这是纸面组合,不含滑点以外的冲击成本、不含分红、不含无法成交的极端情况。
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from .. import config
from .execution import VERSION

LEGACY_LEDGER = config.DATA_DIR / "paper.jsonl"
LEDGER = config.DATA_DIR / f"paper-v{VERSION.removeprefix('alphalens-')}.jsonl"


def _read() -> list[dict]:
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _append(rec: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def record(quant: dict, bars: dict[str, list[dict]]) -> dict | None:
    """把一个交易日的信号落盘(同一日期只记一次)"""
    rows = (quant or {}).get("top") or []
    if not rows or not bars:
        return None
    bench = bars.get("1.000300") or []
    if not bench:
        return None
    trade_date = str(bench[-1].get("date") or "")
    if not trade_date:
        return None
    existing = {r.get("date") for r in _read()}
    if trade_date in existing:
        return None

    picks = []
    for r in rows[:10]:
        if r.get("market", "CN") != "CN":continue
        if r.get("action") not in ("建仓", "左侧试仓"):
            continue  # 只跟踪"该动手的"信号;"持有不追/观察"不是买入建议,不该进账本
        picks.append({
            "secid": r["secid"], "name": r["name"], "sector": r.get("sector"),
            "ref_price": r.get("price"), "score": r.get("score"), "action": r.get("action"),
            "stop": (r.get("plan") or {}).get("stop_loss"),
            "target": ((r.get("plan") or {}).get("targets") or [{}])[0].get("price"),
            "position": (r.get("plan") or {}).get("position_pct"),
        })
    if not picks:
        return None
    rec = {
        "date": trade_date,
        "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "regime": (quant.get("regime") or {}).get("label"),
        "equity": (quant.get("stats") or {}).get("suggested_equity"),
        "bench_close": bench[-1].get("close"),
        "picks": picks,
    }
    _append(rec)
    return rec


def settle(quant: dict, bars: dict[str, list[dict]]) -> dict:
    """按最新收盘价结算历史批次"""
    ledger = _read()
    bench = bars.get("1.000300") or []
    bench_dates = [str(b.get("date")) for b in bench]
    bench_close = {str(b.get("date")): b.get("close") for b in bench}

    batches = []
    all_pnl: list[float] = []
    for rec in ledger[-40:]:
        d0 = rec.get("date")
        idx0 = bench_dates.index(d0) if d0 in bench_dates else -1
        if idx0 < 0 or idx0 + 1 >= len(bench_dates):
            continue
        entry_date = bench_dates[idx0 + 1]  # 次一交易日开盘执行
        holding_days = len(bench_dates) - idx0 - 1
        picks = []
        for p in rec.get("picks") or []:
            b = bars.get(p["secid"]) or []
            dates = [str(x.get("date")) for x in b]
            if entry_date not in dates or not dates:
                continue
            i0 = dates.index(entry_date)
            entry = b[i0].get("open") or b[i0].get("close")
            last = b[-1].get("close")
            if not entry or not last:
                continue
            from .execution import Account, Instrument
            account = Account()
            spec = Instrument.infer(p["secid"], 'etf' if 'ETF' in p.get('name', '') else 'stock')
            weight = p.get("position")
            if weight is None:
                continue  # legacy records without executable weights are not performance
            plan = {"stop_loss": p.get("stop"), "targets": [{"price":p["target"], "reduce":1}] if p.get("target") else []}
            account.submit(p["secid"], 'buy', account.initial * weight / 100 / entry, d0, 'signal', spec, plan)
            for j, day in enumerate(b[i0:], i0):
                day = dict(day)
                day['prev_close'] = b[j-1]['close'] if j else None
                account.process(str(day['date']), {p["secid"]:day})
            executed = [x for x in account.fills if x['side']=='buy']
            if not executed:
                continue
            used = sum(x['qty']*x['price']+x['fee'] for x in executed)
            profit = account.nav()-account.initial
            ret = profit/used*100
            hit_stop = any(x['reason']=='hard_stop' for x in account.fills)
            hit_target = any(x['reason']=='target' for x in account.fills)
            picks.append({**p, "entry":executed[0]['price'], "last":round(last,3),
                          "ret_pct":round(ret,2), "contribution_pct":profit/account.initial*100,
                          "hit_stop":hit_stop,"hit_target":hit_target,"fills":account.fills})
            all_pnl.append(ret)
        if not picks:
            continue
        avg = sum(x["ret_pct"] for x in picks) / len(picks)
        eq = rec.get("equity")
        # 组合口径:按当日建议总仓位投入,其余为现金 —— 这才是"照做"能拿到的收益
        port_ret = sum(x['contribution_pct'] for x in picks)
        b0 = bench_close.get(entry_date)
        b1 = bench[-1].get("close")
        bench_ret = (b1 / b0 - 1) * 100 if b0 and b1 else None
        batches.append({
            "date": d0, "entry_date": entry_date, "holding_days": holding_days,
            "regime": rec.get("regime"), "equity": eq, "n": len(picks),
            "avg_ret_pct": round(avg, 2),
            "portfolio_ret_pct": round(port_ret, 2),
            "bench_ret_pct": round(bench_ret, 2) if bench_ret is not None else None,
            "excess_pct": round(avg - bench_ret, 2) if bench_ret is not None else None,
            "portfolio_excess_pct": round(port_ret - bench_ret, 2) if bench_ret is not None else None,
            "picks": picks,
        })

    mature = [b for b in batches if b["holding_days"] >= 5]
    stats = None
    if mature:
        rets = [b["avg_ret_pct"] for b in mature]
        prets = [b["portfolio_ret_pct"] for b in mature]
        wins = [r for r in rets if r > 0]
        excess = [b["excess_pct"] for b in mature if b["excess_pct"] is not None]
        pexcess = [b["portfolio_excess_pct"] for b in mature if b["portfolio_excess_pct"] is not None]
        stats = {
            "batches": len(mature),
            "avg_ret_pct": round(sum(rets) / len(rets), 2),
            "win_rate_pct": round(len(wins) / len(rets) * 100, 1),
            "avg_excess_pct": round(sum(excess) / len(excess), 2) if excess else None,
            "avg_portfolio_ret_pct": round(sum(prets) / len(prets), 2),
            "avg_portfolio_excess_pct": round(sum(pexcess) / len(pexcess), 2) if pexcess else None,
            "best": round(max(rets), 2), "worst": round(min(rets), 2),
            "avg_hold_days": round(sum(b["holding_days"] for b in mature) / len(mature), 1),
        }
    return {
        "ledger_size": len(ledger),
        "batches": batches[::-1][:20],
        "stats": stats,
        "as_of": bench[-1].get("date") if bench else None,
        "strategy_version": VERSION,
        "legacy_ledger": "paper.jsonl (历史版本，未作为新业绩)",
        "note": "独立信号批次回放，使用真实权重、成交、费用及止损；非连续组合业绩。连续组合见模拟账户。",
    }
