"""major_contract_growth event builder (counts only; no prices/returns).
Prereg: docs/v2/AI_G1G5_MAJOR_CONTRACT_GROWTH_WHO_PAYS_PREREG_ZH.md
Leaf 17. promotion=false; live=false.
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANN = [
    ROOT / "data/v2/events/announcements_classified_pit.parquet",
    ROOT / "data/v2/events/announcements_classified_pit_post202406.parquet",
]
SW = ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet"
CAL = ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet"

GROWTH = frozenset({
    "电子", "计算机", "通信", "医药生物", "电力设备", "机械设备",
    "汽车", "国防军工", "传媒", "家用电器",
})
POS = re.compile(r"(重大合同|中标通知|中标公告|签订.{0,6}合同|签署.{0,6}合同|项目合同|中标)")
NEG = re.compile(
    r"(框架|战略合作|进展|补充|更正|终止|关联|担保|保证|借款|租赁|候选人|诉讼|下属|H股|"
    r"废标|流标|意向|备忘录|合作协议|日常经营|采购框架|销售框架)"
)
COOL = 40          # sessions
MAX_PER_YEAR = 4
HOLD = 40          # for documentation; weights script uses same


def _sessions() -> pd.DatetimeIndex:
    cal = pd.read_parquet(CAL)
    cal["cal_date"] = pd.to_datetime(cal["cal_date"].astype(str))
    s = pd.DatetimeIndex(sorted(cal.loc[cal["is_open"].astype(int) == 1, "cal_date"].unique()))
    return s[(s >= "2018-01-01") & (s <= "2026-10-14")]


def _sw_map() -> dict[str, str]:
    sw = pd.read_parquet(SW, columns=["instrument_id", "sw_name", "in_date"])
    def to_ts(x: str) -> str:
        x = str(x)
        if "." in x and x.split(".")[0] in ("sz", "sh", "bj"):
            mkt, code = x.split(".", 1)
            return f"{code}.{mkt.upper()}"
        return x
    sw = sw.copy()
    sw["instrument"] = sw["instrument_id"].map(to_ts)
    sw["in_date"] = pd.to_datetime(sw["in_date"].astype(str), errors="coerce")
    sw = sw.sort_values("in_date").drop_duplicates("instrument", keep="last")
    return dict(zip(sw["instrument"], sw["sw_name"]))


def _load_hits() -> pd.DataFrame:
    parts = []
    for p in ANN:
        d = pd.read_parquet(p, columns=["instrument", "ann_title", "ann_date", "available_at"])
        parts.append(d)
    a = pd.concat(parts, ignore_index=True)
    t = a["ann_title"].fillna("")
    a = a[t.map(lambda x: bool(POS.search(x)) and not bool(NEG.search(x)))].copy()
    a["d_ann"] = pd.to_datetime(a["ann_date"].astype(str))
    a["aa"] = pd.to_datetime(a["available_at"]).dt.tz_localize(None)
    return a


def events_for_mask(mask_path: Path, growth_only: bool = True) -> tuple[pd.DataFrame, dict]:
    """Return event table filtered to PIT universe membership on mapped session."""
    import bisect
    sessions = _sessions()
    swm = _sw_map()
    hits = _load_hits()
    hits["ind"] = hits["instrument"].map(swm)
    if growth_only:
        hits = hits[hits["ind"].isin(GROWTH)].copy()
    # map available_at to next session (tradable after available_at)
    # convention: available_at day (often ann_date 23:59) → first session strictly after aa date
    aa_day = hits["aa"].dt.normalize()
    hits["si"] = sessions.searchsorted(aa_day.values, side="right")
    hits = hits[hits["si"] < len(sessions)].copy()
    hits["sess"] = sessions[hits["si"].to_numpy()]
    hits = hits.sort_values(["instrument", "sess", "aa"]).drop_duplicates(["instrument", "sess"])

    mask = pd.read_parquet(mask_path, columns=["date", "instrument", "in_universe"])
    mask = mask[mask["in_universe"].astype(bool)].copy()
    mask["date"] = pd.to_datetime(mask["date"]).dt.normalize()
    by = {d: set(g["instrument"]) for d, g in mask.groupby("date", sort=False)}
    dates = sorted(by)

    def in_u(inst: str, d) -> bool:
        d = pd.Timestamp(d).normalize()
        if d in by:
            return inst in by[d]
        i = bisect.bisect_right(dates, d) - 1
        if i < 0:
            return False
        return inst in by[dates[i]]

    ever = set(mask["instrument"].unique())
    hits = hits[hits["instrument"].isin(ever)]
    out = []
    for code, g in hits.groupby("instrument"):
        g = g.sort_values("si")
        last = -10**9
        yc: dict[int, int] = {}
        for _, r in g.iterrows():
            if not in_u(code, r["sess"]):
                continue
            y = int(r["sess"].year)
            if yc.get(y, 0) >= MAX_PER_YEAR:
                continue
            if int(r["si"]) - last < COOL:
                continue
            out.append(
                dict(
                    instrument=code,
                    sess=r["sess"],
                    si=int(r["si"]),
                    available_at=r["aa"],
                    ann_date=r["d_ann"],
                    ind=r["ind"],
                    title=r["ann_title"],
                )
            )
            last = int(r["si"])
            yc[y] = yc.get(y, 0) + 1
    E = pd.DataFrame(out)
    st = {
        "n_events": int(len(E)),
        "n_names": int(E["instrument"].nunique()) if len(E) else 0,
        "by_year": {int(k): int(v) for k, v in E.groupby(E["sess"].dt.year).size().items()} if len(E) else {},
        "top_ind": E["ind"].value_counts().head(10).to_dict() if len(E) else {},
        "mask": str(mask_path),
        "mask_span": [str(mask["date"].min().date()), str(mask["date"].max().date())],
        "growth_only": growth_only,
        "cool": COOL,
        "max_per_year": MAX_PER_YEAR,
        "hold": HOLD,
    }
    if len(E):
        sealed = E[(E["sess"] >= "2018-01-01") & (E["sess"] <= "2024-05-31")]
        x2 = E[(E["sess"] >= "2024-06-03") & (E["sess"] <= "2026-10-09")]
        st["sealed"] = {"n": int(len(sealed)), "names": int(sealed["instrument"].nunique()) if len(sealed) else 0}
        st["x2"] = {"n": int(len(x2)), "names": int(x2["instrument"].nunique()) if len(x2) else 0}
        if len(x2):
            months = max((x2["sess"].max() - x2["sess"].min()).days / 30.4, 1)
            st["x2"]["per_month"] = round(len(x2) / months, 2)
    return E, st


if __name__ == "__main__":
    import json
    fulla = ROOT / "output/strategy_fulla/universe_mask_fulla_v1.parquet"
    hiliq = ROOT / "output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
    out = {}
    for name, path in [("FULLA_V1", fulla), ("HI_LIQ_V1_1", hiliq)]:
        E, st = events_for_mask(path, growth_only=True)
        out[name] = st
        print(name, st["n_events"], st["n_names"], "sealed", st.get("sealed"), "x2", st.get("x2"))
    dest = ROOT / "output/ai_factory/major_contract_growth_count_20261014.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", dest)
