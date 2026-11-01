"""持仓退出状态机 — 买卖分离,卖出不看买入评分

核心思想:买入靠"信号",卖出靠"纪律"。评分掉出榜单不等于该卖,但触发以下任一条件就必须动手:
1. 硬止损(结构性低点 / 2.5ATR),无条件
2. 吊灯止损(持仓期最高价 - k×ATR),锁住利润
3. 均线破位(收盘跌破 MA20 且放量,或跌破 MA60)
4. 分批止盈(到 1.5R / 2.5R 各减一档)
5. 时间止损(持有 N 日未达 1R,资金效率差)
6. 动量衰减(20 日动量分位从高位掉到中位以下 + MACD 死叉)
7. 板块轮动退出(所属板块评分跌出前 50%)

反人性条款(避免"机械止损"被震出局):
- 单日恐慌长下影 + 缩量,且未跌破结构位 → 不砍,但把止损下移一格
- 连涨后乖离过大 → 主动减仓,不等回调
"""
from __future__ import annotations

from . import indicators as ta


def evaluate_exit(
    bars: list[dict],
    entry: float,
    *,
    highest: float | None = None,
    days_held: int = 0,
    stop: float | None = None,
    atr_mult: float = 3.0,
    time_stop_days: int = 20,
    half_sold: bool = False,
    initial_stop: float | None = None,
    managed_targets: bool = False,
    mom_rank: float | None = None,
    sector_rank_pct: float | None = None,
) -> dict:
    """返回 {action: hold|reduce|exit, reason, new_stop}"""
    if not bars or len(bars) < 25:
        return {"action": "hold", "reason": "数据不足", "new_stop": stop}

    cl = ta.closes(bars)
    last = cl[-1]
    a = ta.atr(bars) or last * 0.025
    ma10, ma20, ma60 = ta.sma(cl, 10), ta.sma(cl, 20), ta.sma(cl, 60)
    rsi = ta.rsi(cl, 14) or 50
    macd = ta.macd(cl)
    hi_since = max(highest or entry, max(ta.highs(bars[-max(days_held, 1):]) or [last]))
    vol = ta.volumes(bars)
    v_ratio = (sum(vol[-1:]) / max(sum(vol[-20:]) / 20, 1)) if len(vol) >= 20 else 1.0
    bar = bars[-1]
    lower_shadow = (min(bar.get("open", last), last) - (bar.get("low") or last)) / max(last, 1e-9)

    risk = max(entry - (initial_stop if initial_stop is not None else stop if stop is not None else entry * 0.95), entry * 0.01)
    r_mult = (last - entry) / risk

    # 1 硬止损
    if stop and last <= stop:
        return {"action": "exit", "reason": f"跌破止损 {stop:.2f}", "new_stop": stop, "r": round(r_mult, 2)}

    # 2 吊灯止损
    chandelier = hi_since - atr_mult * a
    if last <= chandelier and r_mult > 0.5:
        return {"action": "exit", "reason": f"吊灯止损 {chandelier:.2f}(高点回落 {atr_mult}ATR)",
                "new_stop": chandelier, "r": round(r_mult, 2)}

    # 3 均线破位
    if ma20 and last < ma20 and v_ratio > 1.3 and r_mult < 0.3:
        return {"action": "reduce", "reason": f"放量跌破 MA20({ma20:.2f})", "new_stop": stop, "r": round(r_mult, 2)}
    if ma60 and last < ma60:
        return {"action": "exit", "reason": f"跌破 MA60({ma60:.2f}),中期趋势破坏", "new_stop": stop, "r": round(r_mult, 2)}

    # 4 分批止盈
    if not managed_targets and not half_sold and r_mult >= 1.5:
        return {"action": "reduce", "reason": f"达到 {r_mult:.1f}R,减半落袋", "new_stop": max(stop or 0, entry),
                "r": round(r_mult, 2)}
    if not managed_targets and half_sold and r_mult >= 2.5 and rsi > 70:
        return {"action": "reduce", "reason": f"{r_mult:.1f}R 且 RSI {rsi:.0f} 超买,再减一档",
                "new_stop": max(stop or 0, last - 2 * a), "r": round(r_mult, 2)}

    # 5 时间止损
    if days_held >= time_stop_days and r_mult < 1.0 and mom_rank is not None and mom_rank < 0.45:
        return {"action": "exit", "reason": f"持有 {days_held} 日未走出趋势,换股", "new_stop": stop, "r": round(r_mult, 2)}

    # 6 动量衰减
    if mom_rank is not None and mom_rank < 0.45 and macd.get("cross") == "死叉" and r_mult > 0:
        return {"action": "reduce", "reason": "动量衰减 + MACD 死叉", "new_stop": max(stop or 0, last - 2.5 * a),
                "r": round(r_mult, 2)}

    # 7 板块轮动退出
    if sector_rank_pct is not None and sector_rank_pct < 0.5 and r_mult < 0.5:
        return {"action": "exit", "reason": "所属板块评分跌出前 50%", "new_stop": stop, "r": round(r_mult, 2)}

    # 反人性:恐慌长下影 + 缩量,不砍但抬高警戒
    if lower_shadow > 0.03 and v_ratio < 0.9 and (stop is None or last > stop):
        return {"action": "hold", "reason": "长下影缩量,恐慌盘释放,暂不砍", "new_stop": stop, "r": round(r_mult, 2)}

    # 正常上移止损(只上不下)
    new_stop = stop or entry - 2.5 * a
    if ma20 and ma20 > new_stop:
        new_stop = ma20 * 0.985
    if r_mult >= 1.0:
        new_stop = max(new_stop, entry)
    return {"action": "hold", "reason": "未触发退出条件", "new_stop": round(new_stop, 3), "r": round(r_mult, 2)}
