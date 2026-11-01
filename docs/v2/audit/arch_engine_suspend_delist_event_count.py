"""Arch 只读审计：X2 内「持仓期间停牌/退市」事件计数（只数次数，不读价格收益、不跑回测）。
输入：各策略已有目标权重（只读）+ tushare suspend_d + data/v2/ref/stock_delisted.parquet + 合并面板最后 20 根收盘（只用于面值退市推断）。
口径：held(t) = 前一交易日收盘目标权重 > 0（next_open 成交，t 日开盘后持有）。
输出：docs/v2/audit/arch_engine_suspend_delist_event_count.json
"""
import json, glob, resource, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
S, E = "2024-06-03", "2026-10-09"
STRATS = {
    "core_v1_3_equity_100_60w": ("core", "output/strategy_optimizer/core_x2/core_equity_100_60w.parquet"),
    "core_v1_3_equity_100_100w": ("core", "output/strategy_optimizer/core_x2/core_equity_100_100w.parquet"),
    "core_v1_3_eq80_etf20_60w": ("core", "output/strategy_optimizer/core_x2/core_equity80_etf20_510300_60w.parquet"),
    "core_v1_3_eq80_etf20_100w": ("core", "output/strategy_optimizer/core_x2/core_equity80_etf20_510300_100w.parquet"),
    "B4_50_25_25_60w": ("tw", "output/strategy_hiliq/b4_leg_review/smoke_B4_50_25_25_60w/aum_600000/X2/BOOK/target_weights.parquet"),
    "B4_50_25_25_100w": ("tw", "output/strategy_hiliq/b4_leg_review/smoke_B4_50_25_25_100w/aum_1000000/X2/BOOK/target_weights.parquet"),
    "capadv_only_60w": ("tw", "output/strategy_hiliq/b4_leg_review/smoke_CAPADV_ONLY/aum_600000/X2/BOOK/target_weights.parquet"),
    "capadv_only_100w": ("tw", "output/strategy_hiliq/b4_leg_review/smoke_CAPADV_ONLY/aum_1000000/X2/BOOK/target_weights.parquet"),
}
def to_ts(i):
    i = str(i)
    if "." in i and i[:2] in ("sh", "sz", "bj"): return i[3:] + "." + i[:2].upper()
    return i
def is_stock(ts):
    c = ts[:6]; return not c.startswith(("51", "56", "58", "15", "16", "11", "12", "13"))

cal = pd.read_parquet(ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet")
cal = pd.DatetimeIndex(sorted(pd.to_datetime(cal[cal.is_open.astype(int) == 1].cal_date.astype(str))))
cal = cal[(cal >= S) & (cal <= E)]
fs = sorted(f for f in glob.glob(str(ROOT / "data/v2/tushare_raw/suspend_d/*.parquet")) if S.replace("-", "") <= Path(f).stem <= E.replace("-", ""))
SD = pd.concat([pd.read_parquet(f) for f in fs]); SD = SD[SD.suspend_type == "S"]
SD["d"] = pd.to_datetime(SD.trade_date.astype(str))
allday = SD[SD.suspend_timing.isna() | (SD.suspend_timing.astype(str).isin(["None", ""]))]
SUS = set(zip(allday.ts_code, allday.d)); SUSP_PART = set(zip(SD.ts_code, SD.d)) - SUS
DL = pd.read_parquet(ROOT / "data/v2/ref/stock_delisted.parquet")
DL["ltd"] = pd.to_datetime(DL.last_trade_date.astype(str), errors="coerce")
DL = DL[(DL.ltd >= S) & (DL.ltd <= E)].set_index("ts_code")

def face_value_inferred(ts):
    from quantlab.data.v2_readers import default_v2_roots, load_merged_panel
    iid = ("sh." if ts.endswith("SH") else "bj." if ts.endswith("BJ") else "sz.") + ts[:6]
    fr = load_merged_panel(iid, roots=default_v2_roots()).frame
    if fr is None or fr.empty: return None
    c = pd.to_numeric(fr.sort_values("event_time").close, errors="coerce").dropna().tail(20)
    return bool(len(c) == 20 and (c < 1.0).all())

out = {"window": [S, E], "n_sessions": len(cal), "suspend_d_files": len(fs),
       "definition": "held(t)=前一交易日收盘目标权重>0；停牌=suspend_d S 类且 suspend_timing 为空(全天)；退市=stock_delisted.last_trade_date 落在 X2",
       "by_strategy": {}}
for name, (kind, p) in STRATS.items():
    d = pd.read_parquet(ROOT / p)
    if kind == "core":
        d = d[d.window == "X2"]; d = d.rename(columns={"instrument": "ts", "target_weight": "w"})[["session", "ts", "w"]]
    else:
        d = d.rename(columns={"weight": "w"}); d["ts"] = d.instrument_id.map(to_ts); d = d[["session", "ts", "w"]]
    d["session"] = pd.to_datetime(d.session); d = d[d.ts.map(is_stock) & (d.w > 1e-7)]
    P = d.pivot_table(index="session", columns="ts", values="w", aggfunc="sum").fillna(0.0)  # 当日有记录而该股缺席 = 0
    P = P.reindex(cal).ffill().fillna(0.0)  # 仅整日缺记录时沿用上一日目标
    H = P.shift(1).fillna(0.0) > 0          # held during day t
    chg = (P.diff().abs() > 1e-6)           # target changed at close t -> order executes t+1
    chg.iloc[0] = P.iloc[0] > 0
    sus_hold_days = 0; episodes = []; part_days = 0; blocked = {"sell_or_reduce": 0, "buy_or_add": 0}
    for ts in P.columns:
        h = H[ts].to_numpy(); run = 0; start = None
        for k, t in enumerate(cal):
            s = (ts, t) in SUS
            if h[k] and (ts, t) in SUSP_PART: part_days += 1
            if h[k] and s:
                sus_hold_days += 1
                if run == 0: start = t
                run += 1
            elif run:
                episodes.append((ts, str(start.date()), run)); run = 0
            if k + 1 < len(cal) and chg[ts].iloc[k] and (ts, cal[k + 1]) in SUS:
                dw = P[ts].iloc[k] - (P[ts].iloc[k - 1] if k else 0.0)
                blocked["sell_or_reduce" if dw < 0 else "buy_or_add"] += 1
        if run: episodes.append((ts, str(start.date()), run))
    dl = []
    for ts in P.columns:
        if ts in DL.index:
            ltd = DL.loc[ts, "ltd"]; held_at_ltd = bool(P[ts].reindex([c for c in cal if c < ltd]).tail(1).gt(0).any()) if ltd in cal else False
            held_any_last20 = bool(P[ts].loc[:ltd].tail(20).gt(0).any())
            if held_at_ltd or held_any_last20:
                dl.append(dict(ts=ts, name=DL.loc[ts, "name"], last_trade_date=str(ltd.date()), category=DL.loc[ts, "delist_reason_category"],
                               held_into_last_trade_date=held_at_ltd, held_within_last20=held_any_last20,
                               face_value_inferred=face_value_inferred(ts)))
    ep_len = [e[2] for e in episodes]
    out["by_strategy"][name] = dict(
        n_stock_names_held=int((H.any()).sum()), stock_holding_days=int(H.to_numpy().sum()),
        suspend_hold_episodes=len(episodes), suspend_hold_days=int(sus_hold_days),
        suspend_episode_len_median=float(np.median(ep_len)) if ep_len else 0.0, suspend_episode_len_max=int(max(ep_len)) if ep_len else 0,
        suspend_partial_day_hold=int(part_days), rebalance_orders_hitting_suspension=blocked,
        delist_events=dl, episodes=[dict(ts=a, start=b, days=c) for a, b, c in episodes])
out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
Path(__file__).with_suffix(".json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
for k, v in out["by_strategy"].items():
    print(k, {kk: vv for kk, vv in v.items() if kk not in ("episodes",)})
print("rss", out["peak_rss_mb"])
