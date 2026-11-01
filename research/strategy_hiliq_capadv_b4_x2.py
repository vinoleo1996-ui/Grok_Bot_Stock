#!/usr/bin/env python3
"""HI_LIQ_V1.1 transitional Top-N: capacity_adv alone + B4 synthesis + Eng book-smoke X2.

BANNER: transitional Top-N only. Main path = OPTIMIZER_V1 DRAFT (awaiting Leo).
Do NOT touch FROZEN_CONFIG / paper tracks / live / promotion.
Outputs under output/strategy_hiliq/ only.

B4 = capacity_adv / earnings_event / insider_increase 50/25/25
per-leg topN (60万 N=6, 100万 N=10), portfolio single-name ≤6% → 510300
re-apply 申万一 stock-sleeve ≤25% at synthesis (pro-rata scale).
"""
from __future__ import annotations
import json, subprocess, sys, hashlib, time, resource
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.sw_pit_freshness import ensure_checked as sw_pit_ensure_checked, last_result as sw_pit_last_result  # 主 Agent 10-18 05:06; Arch ccc7546f
from research.sw_pit_freshness import SwPitIntegrityError
from research.sw_members_asof import (IndustryAsOf, load_sw_l1, sw_l1_asof_chunked,  # PIT fix (Arch 3f195231 r2)
                                      pitfix_out_dir_guard, SW_L1_REL,
                                      load_trade_cal)  # DIFF C: d-1 = prev SSE open day (主 Agent 10-18 06:01 ET)
from research.sw_members_asof import (sw_pit_required, sw_pit_required_ok,  # C r3: 主 Agent 06:49 ET mandatory fields
                                      OVERLAP_TIEBREAK)
from research.sw_members_asof import (SW_L1_LEGACY_REL, sw_l1_table_check,  # C r3b: default CLEAN + per-table check
                                      sw_l1_table_check_last)
from research.sw_members_asof import check_allow_ok  # r3c: Arch 016ae55e P3-4 key=value .ok parser
OUT = ROOT / "output/strategy_hiliq"
OUT.mkdir(parents=True, exist_ok=True)
LEGS = OUT / "legs"
CAPADV_OUT = OUT / "capadv_x2"
B4_OUT = OUT / "b4"
BAL = "510300.SH"
CAP = 0.06
IND_CAP = 0.25
N_BY_AUM = {600000: 6, 1000000: 10}
X2 = ("2024-06-03", "2026-10-09")
SEALED = ("2018-01-02", "2024-05-31")
FOCUS_INDS = ("电子", "计算机", "通信", "医药生物")
# C r3b (Arch 2026-10-18 ~07:00 ET): synthesis ind cap + industry disclosure read CLEAN by default
# (data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet, the table leaf 23/24 pin); --sw-pit-path overrides.
SW_L1_SHA_PIN = "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"
SW_L1_PATH_DEFAULT = ROOT / SW_L1_REL  # C r3 (Arch 06:50): table path is a parameter; C r3b: SW_L1_REL = CLEAN
# PIT-fix pre/post comparison (PAUSED, 主 Agent 06:49 ET) reads the old sw_pit file (manifest 0b1d3432…, built
# 2026-10-14T04:00:19 ET) in BOTH arms: before = verbatim load_industry_map, after = as-of on the same bytes.
SW_L1_LEGACY_PATH = ROOT / SW_L1_LEGACY_REL
SW_L1_LEGACY_SHA_PIN = "0b1d3432e30f7cdd907df393299cd2f552e1121899239985a00113c4dfcd89f6"
PITFIX_PAUSED = True  # 主 Agent 06:49 ET: paused until sw_l1_pit_v2 is reviewed (re-plan with v2 sha + new .ok)
PITFIX_ALLOW_FIELD = "allow_pitfix_compare"  # r3c: Arch 016ae55e P3-4 (key=value, value true)
ON_OVERLAP_RESEARCH = "count"  # 主 Agent 06:49 ET: research runs disclose overlaps instead of raising


def _sw_path(sw_path=None) -> Path:
    """Resolved sw_pit L1 table path; None -> SW_L1_PATH_DEFAULT; relative -> ROOT / sw_path."""
    p = SW_L1_PATH_DEFAULT if sw_path is None else Path(sw_path)
    return (p if p.is_absolute() else ROOT / p).resolve()


def _check_loaded_pin(ia: IndustryAsOf, pin: str = SW_L1_SHA_PIN) -> IndustryAsOf:
    """C r3: sha pin still enforced on the bytes actually parsed, whatever --sw-pit-path points to."""
    if ia.sha256 != pin:
        raise SwPitIntegrityError(f"sw_pit l1 sha {ia.sha256} ({ia.path}) != pinned {pin}")
    return ia

# T5 (Arch audit 2026-10-14): legs repointed to AI N1 regenerated legs (ind_cap_ok_book=true); old 1953xx-1957xx quarantined in _rejected_ind_cap/.
P = {
    "capacity_adv": LEGS / "g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet",
    "earnings_event": LEGS / "g1g5_earnings_event_hiliq_v1_daily_weights_20261014_202822.parquet",
    "insider_increase": LEGS / "g1g5_insider_increase_hiliq_v1_daily_weights_20261014_202928.parquet",
    "equity_incentive": LEGS / "g1g5_equity_incentive_hiliq_v1_daily_weights_20261014_202436.parquet",
    "report_rc_allup": LEGS / "g1g5_report_rc_allup_hiliq_v1_daily_weights_20261014_203201.parquet",
    "insurer_surv": LEGS / "g1g5_insurer_surv_hiliq_v1_daily_weights_20261014_203108.parquet",
}

GROUPS = {
    "B4_50_25_25": {"capacity_adv": 0.5, "earnings_event": 0.25, "insider_increase": 0.25},
}


def _is_etf(inst: str) -> bool:
    s = str(inst)
    code = s.split(".")[0] if "." in s else s
    return code[:2] in ("51", "56", "58", "15")


def to_id(x: str) -> str:
    if "." in x:
        code, mkt = x.split(".", 1)
        return f"{mkt.lower()}.{code}"
    return x


def load_leg(path: Path) -> pd.DataFrame:
    d = pd.read_parquet(path, columns=["session", "instrument", "instrument_id", "weight"])
    d["session"] = d["session"].astype(str).str[:10]
    d = d[d["weight"] > 0].copy()
    return d


def load_industry_map(as_of: str | None = None) -> dict:
    # as_of = max session used in synthesis (main passes it); X2 end only as fallback, disclosed (Arch c432c912)
    sw_pit_ensure_checked(ROOT, as_of=as_of or X2[1], as_of_defaulted=as_of is None)
    ind = pd.read_parquet(
        ROOT / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet",
        columns=["ts_code", "l1_name", "in_date", "out_date"],
    )
    ind["in_date"] = pd.to_datetime(ind["in_date"], errors="coerce")
    # last known name per ts_code (approx PIT; same as FULLA helper)
    # LEGACY — kept verbatim (Arch 3f195231 P2-4): has look-ahead; used by the "before" arm of --pitfix-compare
    # and by importers (tie-sens / leg_review). New decision path: load_industry_asof().
    last = ind.sort_values("in_date").groupby("ts_code").tail(1)
    return dict(zip(last["ts_code"], last["l1_name"]))


def load_industry_asof(as_of: str | None = None, static_map: dict | None = None, *, sw_path=None) -> IndustryAsOf:
    """PIT industry as-of each session (in_date < d, out_date null or >= d) + 主 Agent 10-18 gap carry
    (d-1 = previous SSE open day; calendar passed explicitly, sha pinned in sw_members_asof). sw_path: table file
    (None -> CLEAN default, C r3b); on_overlap='count' (主 Agent 06:49 ET). Integrity/stale check on the table actually
    read (sw_l1_table_check: legacy sw_pit -> sw_pit_freshness; CLEAN -> sw_l1_pit manifest check)."""
    cal = load_trade_cal(ROOT)
    sw = load_sw_l1(ROOT, path=_sw_path(sw_path))
    sw_l1_table_check(ROOT, sw, as_of or X2[1], cal, as_of_defaulted=as_of is None)
    return IndustryAsOf(sw, static_map=static_map, cal=cal, on_overlap=ON_OVERLAP_RESEARCH)


def check_sw_l1_pin(sw_path=None, pin: str = SW_L1_SHA_PIN) -> str:
    """Explicit raise (not assert; survives python -O) — Arch P3-6. Checks the file actually used (C r3)."""
    got = hashlib.sha256(_sw_path(sw_path).read_bytes()).hexdigest()
    if got != pin:
        raise SwPitIntegrityError(f"sw_pit l1 sha {got} != pinned {pin}")
    return got


def apply_ind_cap(agg: dict, ind_map: dict, cap: float = IND_CAP) -> tuple[dict, float]:
    """Iteratively pro-rata scale SW L1 above `cap` of stock-sleeve; excess → BAL.

    One-shot scaling can push other industries over the cap after the sleeve shrinks;
    loop until all industries ≤ cap (or max_iter).
    """
    stock = {i: v for i, v in agg.items() if not _is_etf(i)}
    etf = {i: v for i, v in agg.items() if _is_etf(i)}
    total_cut = 0.0
    for _ in range(20):
        sleeve = sum(stock.values())
        if sleeve <= 1e-12:
            break
        by_ind: dict[str, list[str]] = {}
        for i in stock:
            name = ind_map.get(i) or "_UNK_"
            by_ind.setdefault(name, []).append(i)
        worst_name, worst_share, worst_w = None, 0.0, 0.0
        for name, names in by_ind.items():
            w_ind = sum(stock[i] for i in names)
            share = w_ind / sleeve
            if share > worst_share:
                worst_name, worst_share, worst_w = name, share, w_ind
        if worst_share <= cap + 1e-9:
            break
        target = sleeve * cap
        scale = target / worst_w
        cut = 0.0
        for i in by_ind[worst_name]:
            nw = stock[i] * scale
            cut += stock[i] - nw
            stock[i] = nw
        total_cut += cut
        etf[BAL] = etf.get(BAL, 0.0) + cut
    return {**stock, **etf}, total_cut


def build_topn(mix: dict, aum: int, tag: str, ind_map) -> tuple[pd.DataFrame, dict]:
    """ind_map: IndustryAsOf (PIT, per-session lookup) or legacy static dict."""
    used = list(mix)
    D = {k: load_leg(P[k]) for k in used}
    common = sorted(set.intersection(*[set(d["session"]) for d in D.values()]))
    if isinstance(ind_map, IndustryAsOf):
        pairs = pd.concat([d.loc[~d["instrument"].map(_is_etf), ["instrument", "session"]] for d in D.values()])
        lut = ind_map.by_session(pairs[pairs["session"].isin(set(common))])
        ind_mode = "asof_gap_carry"
    else:
        lut, ind_mode = None, "static_legacy"
    n_ind_cap_sessions = n_ind_cap_x2 = n_unk_over_cap_x2 = 0
    # keep full coverage; book-smoke will slice X2
    G = {k: {s: g.set_index("instrument")["weight"] for s, g in d.groupby("session")} for k, d in D.items()}
    n = N_BY_AUM[aum]
    rows = []
    cap_cut = 0.0
    ind_cut = 0.0
    max_ind_share = 0.0
    for s in common:
        agg: dict[str, float] = {}
        for k, m in mix.items():
            w = G[k].get(s)
            if w is None:
                continue
            w = w * m
            e_mask = [_is_etf(i) for i in w.index]
            e = w[e_mask]
            st = w[[not x for x in e_mask]]
            for i, v in e.items():
                agg[i] = agg.get(i, 0.0) + float(v)
            if len(st) == 0:
                continue
            keep = st.sort_values(ascending=False).head(n)
            keep = keep * (st.sum() / keep.sum()) if keep.sum() > 0 else keep
            for i, v in keep.items():
                agg[i] = agg.get(i, 0.0) + float(v)
        # single-name cap
        for i in list(agg):
            if (not _is_etf(i)) and agg[i] > CAP:
                cap_cut += agg[i] - CAP
                agg[BAL] = agg.get(BAL, 0.0) + agg[i] - CAP
                agg[i] = CAP
        # re-apply IND≤25% of stock sleeve
        im = lut.get(s, {}) if lut is not None else ind_map
        in_x2 = X2[0] <= s <= X2[1]
        st_pre = {i: v for i, v in agg.items() if not _is_etf(i)}
        sl_pre = sum(st_pre.values())
        if in_x2 and sl_pre > 0:  # P3-1: sessions where the _UNK_ bucket alone exceeds the cap (pre-cap)
            n_unk_over_cap_x2 += int(sum(v for i, v in st_pre.items() if not im.get(i)) / sl_pre > IND_CAP + 1e-9)
        agg, ic = apply_ind_cap(agg, im, IND_CAP)
        ind_cut += ic
        n_ind_cap_sessions += int(ic > 1e-12)
        n_ind_cap_x2 += int(ic > 1e-12 and in_x2)
        # track max industry share after
        stock = {i: v for i, v in agg.items() if not _is_etf(i)}
        sleeve = sum(stock.values())
        if sleeve > 0:
            by_ind: dict[str, float] = {}
            for i, v in stock.items():
                by_ind[im.get(i) or "_UNK_"] = by_ind.get(im.get(i) or "_UNK_", 0.0) + v
            max_ind_share = max(max_ind_share, max(by_ind.values()) / sleeve)
        t = sum(agg.values())
        if t <= 0:
            continue
        for i, v in agg.items():
            if v > 0:
                rows.append((s, i, v / t))
    W = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
    W = W.groupby(["session", "instrument"], as_index=False)["weight"].sum()
    assert ((W.groupby("session")["weight"].sum() - 1).abs() < 1e-6).all()
    W["date"] = W["session"]
    W["target_weight"] = W["weight"]
    W["instrument_id"] = W["instrument"].map(to_id)
    W["mechanism_tag"] = f"hiliq_v1_1_{tag}_topN_{aum // 10000}w"
    W["who_pays_zh"] = "HI_LIQ_V1.1 过渡 Top-N（非纸面；主路径=OPTIMIZER DRAFT）"
    W["universe_id"] = "HI_LIQ_V1.1"
    W = W[W["weight"] > 0].copy()
    stocks = W.loc[~W["instrument"].map(_is_etf)]
    meta = dict(
        tag=tag, aum=aum, N=n, sessions=[common[0], common[-1], len(common)],
        rows=len(W),
        max_stock_w=float(stocks["weight"].max()) if len(stocks) else None,
        cap_cut_mean=cap_cut / max(len(common), 1),
        ind_cut_mean=ind_cut / max(len(common), 1),
        max_ind_sleeve_share_after=float(max_ind_share),
        ind_cap=IND_CAP,
        ind_map_mode=ind_mode,
        n_ind_cap_sessions=int(n_ind_cap_sessions),
        n_ind_cap_sessions_x2=int(n_ind_cap_x2),  # sessions in X2 where apply_ind_cap actually cut weight
        n_unk_over_cap_sessions_x2=int(n_unk_over_cap_x2),
        mean_510300=float(W[W["instrument"] == BAL].groupby("session")["weight"].sum().reindex(common).fillna(0).mean()),
        stock_names_median=float(stocks.groupby("session").size().median()) if len(stocks) else 0,
    )
    if isinstance(ind_map, IndustryAsOf):
        hold = W.loc[~W["instrument"].map(_is_etf) & (W["session"] >= X2[0]) & (W["session"] <= X2[1]),
                     ["session", "instrument", "weight"]]
        meta["reclass_share_x2"] = ind_map.reclass_share(hold, weight_col="weight")  # disclosure only
        meta["sw_asof_stats"] = dict(ind_map.stats)
        meta["sw_pit_required"] = sw_pit_required(ind_map, meta["reclass_share_x2"])  # 主 Agent 06:49 ET item 3
    return W, meta


def write_pos_weights(src: Path, dst: Path) -> Path:
    d = pd.read_parquet(src)
    if "weight" not in d.columns and "target_weight" in d.columns:
        d["weight"] = d["target_weight"]
    d = d[d["weight"] > 0].copy()
    if "session" not in d.columns and "date" in d.columns:
        d["session"] = d["date"].astype(str).str[:10]
    if "instrument_id" not in d.columns:
        d["instrument_id"] = d["instrument"].map(to_id)
    if "target_weight" not in d.columns:
        d["target_weight"] = d["weight"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(dst, index=False)
    return dst


def run_smoke(stock_path: Path, out_dir: Path, capitals: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "quantlab.cli", "book-smoke", "--run-nav",
        "--stock-path", str(stock_path.relative_to(ROOT)),
        "--out", str(out_dir.relative_to(ROOT)),
        "--windows", "X2",
        "--capitals", capitals,
        "--sleeves", '{"core":0,"stock":1,"alpha_event":0}',
        "--arms", "BOOK,C0",
    ]
    log = out_dir / "run.log"
    sp = out_dir / "book_smoke_summary.json"
    t_start = time.time()
    pre_mtime = sp.stat().st_mtime if sp.exists() else None
    with open(log, "w") as f:
        r = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, text=True)
    # Arch 3f195231 P2-3: success = returncode 0 AND a summary written by THIS run (not a stale file)
    fresh = sp.exists() and sp.stat().st_mtime >= t_start and (pre_mtime is None or sp.stat().st_mtime > pre_mtime)
    if r.returncode != 0 or not fresh:
        return {"ok": False, "returncode": r.returncode, "summary_fresh": bool(fresh), "log": str(log)}
    return {"ok": True, "returncode": r.returncode, "summary_fresh": True,
            "summary": json.loads(sp.read_text()), "log": str(log)}


def win_rates(nav_csv: Path) -> dict:
    if not nav_csv.exists():
        return {}
    nav = pd.read_csv(nav_csv)
    nav["_et"] = pd.to_datetime(nav["_et"] if "_et" in nav.columns else nav.columns[0])
    nav = nav.sort_values("_et")
    r = nav["nav"].pct_change()
    daily = float((r.dropna() > 0).mean()) if r.notna().any() else None
    nav["ym"] = nav["_et"].dt.to_period("M")
    mret = nav.groupby("ym")["nav"].last().pct_change()
    monthly = float((mret.dropna() > 0).mean()) if mret.notna().any() else None
    yearly = {}
    for y, g in nav.groupby(nav["_et"].dt.year):
        if len(g) < 2:
            continue
        tot = g["nav"].iloc[-1] / g["nav"].iloc[0] - 1
        nd = max((g["_et"].iloc[-1] - g["_et"].iloc[0]).days, 1)
        yearly[str(y)] = float((1 + tot) ** (365.25 / nd) - 1)
    return {"win_rate_daily": daily, "win_rate_monthly": monthly, "yearly_cagr": yearly}


def extract_arm(summary: dict, aum: int, smoke_dir: Path) -> dict:
    by = summary.get("by_capital", {})
    block = by.get(str(aum), {})
    book = None
    for k, v in block.items():
        if "BOOK" in str(k):
            book = v
            break
    if book is None:
        return {"aum": aum, "error": "no_BOOK"}
    nav_csv = smoke_dir / f"aum_{aum}" / "X2" / "BOOK" / "nav.csv"
    wr = win_rates(nav_csv)
    calmar = book.get("calmar")
    if calmar is None and book.get("cagr") is not None and book.get("mdd"):
        calmar = book["cagr"] / abs(book["mdd"]) if book["mdd"] else None
    return {
        "aum": aum,
        "cagr": book.get("cagr"),
        "mdd": book.get("mdd"),
        "calmar": calmar,
        "sharpe": book.get("sharpe"),
        "fill_ratio": book.get("fill_ratio"),
        "cost_pct": book.get("cost_pct_initial"),
        "n_days": book.get("n_signals"),
        **wr,
        "nav_path": str(nav_csv.relative_to(ROOT)) if nav_csv.exists() else None,
        "mdd25_breach": bool(book.get("mdd") is not None and book["mdd"] < -0.25),
    }


def smallcap_and_industry(W: pd.DataFrame, tag: str, *, sw_path=None) -> dict:
    Wx = W[(W["session"] >= X2[0]) & (W["session"] <= X2[1])].copy()
    Wx = Wx[~Wx["instrument"].map(_is_etf)].copy()
    if Wx.empty:
        return {"tag": tag, "empty": True}
    db = pd.read_parquet(
        ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet",
        columns=["ts_code", "trade_date", "total_mv"],
    )
    db["trade_date"] = db["trade_date"].astype(str).str.replace("-", "").str[:8]
    Wx["td"] = Wx["session"].str.replace("-", "")
    need_dates = set(Wx["td"].unique())
    db = db[db["trade_date"].isin(need_dates)].copy()
    db["q30"] = db.groupby("trade_date")["total_mv"].transform(lambda s: s.quantile(0.30))
    db["med"] = db.groupby("trade_date")["total_mv"].transform("median")
    db["is_small"] = db["total_mv"] <= db["q30"]
    db["below_med"] = db["total_mv"] <= db["med"]
    flags = db[["ts_code", "trade_date", "is_small", "below_med", "total_mv"]]
    merged = Wx.merge(flags, left_on=["instrument", "td"], right_on=["ts_code", "trade_date"], how="left")
    miss = float(merged["is_small"].isna().mean())
    day_w = merged.groupby("session", group_keys=False).apply(
        lambda g: pd.Series({
            "small_w": g.loc[g["is_small"] == True, "weight"].sum(),
            "below_med_w": g.loc[g["below_med"] == True, "weight"].sum(),
            "stock_w": g["weight"].sum(),
        }),
        include_groups=False,
    )
    ia = _check_loaded_pin(load_industry_asof(as_of=str(Wx["session"].max())[:10], sw_path=sw_path))  # C r3b
    m2 = Wx.copy()
    m2["l1_name"] = sw_l1_asof_chunked(ia.sw, Wx, "instrument", "session", cal=ia.cal,  # r3c P3-6: chunk by session
                                       on_overlap=ia.on_overlap).values  # as-of (PIT)
    reclass = ia.reclass_share(Wx, weight_col="weight")  # disclosure only
    ind_share = (m2.groupby("l1_name")["weight"].sum() / m2["weight"].sum()).sort_values(ascending=False)
    ind_share = ind_share[ind_share.index.notna()]
    focus = {name: float(ind_share.get(name, 0.0)) for name in FOCUS_INDS}
    return {
        "tag": tag,
        "window": list(X2),
        "label": "样本内",
        "definition_zh": "PIT total_mv 截面后30%（沪深A）；仅披露，非剔除条件",
        "join_miss_rate": miss,
        "mean_smallcap_weight_of_book": float(day_w["small_w"].mean()),
        "pct_days_any_smallcap_holding": float((day_w["small_w"] > 0).mean()),
        "n_smallcap_holding_rows": int((merged["is_small"] == True).sum()),
        "mean_below_median_mv_weight_of_book": float(day_w["below_med_w"].mean()),
        "industry_weight_time_share": [
            {"sw_name": str(k), "weight_time_share": float(v)} for k, v in ind_share.head(30).items()
        ],
        "focus_industries": focus,
        "reclass_share": reclass,
        "sw_pit_required": sw_pit_required(ia, reclass),  # 主 Agent 06:49 ET item 3
        "note_zh": "行业用申万一级 as-of 归属（in_date<session 且 out_date 空或>=session，对齐 Intel；改分类空档日沿用旧行业 1 天，主 Agent 10-18 ~05:45 ET 裁定）；取不到行业的行不计入行业占比，数量见 reclass_share；小盘为逐日截面后30%。",
    }


def sealed_status(leg_path: Path) -> dict:
    d = load_leg(leg_path)
    lo, hi = d["session"].min(), d["session"].max()
    return {
        "sealed_window": list(SEALED),
        "legs_coverage": [lo, hi],
        "status": "N/A",
        "partial_overlap": ["2024-01-02", "2024-05-31"] if lo <= "2024-05-31" else None,
        "note_zh": (
            "HI_LIQ 腿权重仅自 2024-01-02 起；密封窗 2018-01-02→2024-05-31 无完整权重，"
            "不发明权重。Eng book-smoke 亦拒绝密封窗。2024-01-02→2024-05-31 仅为部分重叠，"
            "不作密封声明。"
        ),
        "book_smoke_note": "sealed refused by book module (WINDOWS has X1/X2/exploration only)",
    }


def make_charts(cap_arms: list, b4_arms: list, attrs: dict) -> list[str]:
    paths = []
    # CAGR/MDD comparison
    fig, ax = plt.subplots(figsize=(11, 5))
    labels, cagrs, mdds = [], [], []
    for lab, m in cap_arms + b4_arms:
        if m.get("cagr") is None:
            continue
        labels.append(lab)
        cagrs.append(m["cagr"] * 100)
        mdds.append(m["mdd"] * 100)
    x = np.arange(len(labels))
    ax.bar(x - 0.2, cagrs, 0.4, label="CAGR%")
    ax.bar(x + 0.2, mdds, 0.4, label="MDD%")
    ax.axhline(-25, color="r", ls="--", lw=1, label="MDD −25%")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend()
    ax.set_title("HI_LIQ_V1.1 transitional Top-N X2 (样本内) — CAGR / MDD\n主路径=OPTIMIZER_V1 DRAFT；未动纸面")
    ax.grid(True, axis="y", alpha=0.3)
    p1 = OUT / "hiliq_cagr_mdd.png"
    fig.tight_layout()
    fig.savefig(p1, dpi=120)
    plt.close()
    paths.append(str(p1.relative_to(ROOT)))

    # yearly
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for lab, m in cap_arms + b4_arms:
        yc = m.get("yearly_cagr") or {}
        if not yc:
            continue
        ys = sorted(yc)
        ax.plot(ys, [yc[y] * 100 for y in ys], marker="o", label=lab)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("年化 %")
    ax.set_title("HI_LIQ X2 分年年化（样本内；过渡 Top-N）")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    p2 = OUT / "hiliq_yearly.png"
    fig.tight_layout()
    fig.savefig(p2, dpi=120)
    plt.close()
    paths.append(str(p2.relative_to(ROOT)))

    # NAV normalize
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for lab, m in cap_arms + b4_arms:
        npth = m.get("nav_path")
        if not npth:
            continue
        nav = pd.read_csv(ROOT / npth)
        et = pd.to_datetime(nav["_et"] if "_et" in nav.columns else nav.columns[0])
        n = nav["nav"] / nav["nav"].iloc[0]
        ax.plot(et, n, label=lab, lw=1.2)
    ax.legend(fontsize=7)
    ax.set_title("HI_LIQ NAV（归一）X2 样本内 — 过渡 Top-N")
    ax.grid(True, alpha=0.3)
    p3 = OUT / "hiliq_nav.png"
    fig.tight_layout()
    fig.savefig(p3, dpi=120)
    plt.close()
    paths.append(str(p3.relative_to(ROOT)))

    # industry for capacity_adv 60w if present
    for key, attr in attrs.items():
        share = attr.get("industry_weight_time_share") or []
        if not share:
            continue
        top = share[:12]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        names = [x["sw_name"] for x in top]
        vals = [x["weight_time_share"] * 100 for x in top]
        colors = ["#e74c3c" if n in FOCUS_INDS else "#3498db" for n in names]
        ax.barh(names[::-1], vals[::-1], color=colors[::-1])
        ax.set_xlabel("权重×时间 %（股票袖）")
        ax.set_title(f"HI_LIQ 申万一 {key}（红=电子/计算机/通信/医药）")
        fig.tight_layout()
        p = OUT / f"hiliq_industry_{key}.png"
        fig.savefig(p, dpi=120)
        plt.close()
        paths.append(str(p.relative_to(ROOT)))
    return paths


def load_top300_baseline() -> dict:
    # Prefer Eng X2 book-smoke baseline
    p = ROOT / "output/v3/book_smoke_g1g5_capacity_adv_x2/book_smoke_summary.json"
    out = {}
    if p.exists():
        s = json.loads(p.read_text())
        for aum in (600000, 1000000):
            block = s.get("by_capital", {}).get(str(aum), {})
            book = None
            for k, v in block.items():
                if "BOOK" in str(k):
                    book = v
                    break
            if book:
                out[str(aum)] = {
                    "cagr": book.get("cagr"),
                    "mdd": book.get("mdd"),
                    "calmar": book.get("calmar") or (
                        book["cagr"] / abs(book["mdd"]) if book.get("cagr") is not None and book.get("mdd") else None
                    ),
                    "source": "output/v3/book_smoke_g1g5_capacity_adv_x2",
                }
    # hard fallback from FULLA receipt numbers
    if "600000" not in out:
        out["600000"] = {"cagr": 0.1382, "mdd": -0.1007, "calmar": 1.372, "source": "STRATEGY_FULLA_X2_ZH"}
    if "1000000" not in out:
        out["1000000"] = {"cagr": 0.1223, "mdd": -0.1162, "calmar": 1.052, "source": "STRATEGY_FULLA_X2_ZH"}
    return out


def main(sw_path=None):
    t0 = time.time()
    print("=== BANNER: transitional Top-N; main path = OPTIMIZER_V1 DRAFT; FROZEN/paper untouched; live=false ===")
    for k, p in P.items():
        if not p.exists():  # r3c: was a bare assert (Arch c72f0856 P3-6; asserts vanish under python -O)
            raise SystemExit(f"missing leg {k}: {p}")
    check_sw_l1_pin(sw_path)  # C r3: pin checked on the table file actually used, before any write

    # 1) capacity_adv pos weights + smoke
    print("=== capacity_adv pos weights ===")
    pos = OUT / "legs" / "g1g5_capacity_adv_hiliq_v1_1_pos_weights.parquet"
    write_pos_weights(P["capacity_adv"], pos)
    print("pos rows", len(pd.read_parquet(pos)))

    print("=== book-smoke capacity_adv X2 ===")
    CAPADV_OUT.mkdir(parents=True, exist_ok=True)
    cap_smoke = run_smoke(pos, CAPADV_OUT, "600000,1000000")
    print("cap smoke ok", cap_smoke.get("ok"), "rc", cap_smoke.get("returncode"))
    cap_results = {}
    if cap_smoke.get("ok"):
        for aum in (600000, 1000000):
            arm = extract_arm(cap_smoke["summary"], aum, CAPADV_OUT)
            arm["ok"] = True
            cap_results[str(aum)] = arm
            print(f"  capadv {aum}: CAGR={arm.get('cagr')} MDD={arm.get('mdd')} breach={arm.get('mdd25_breach')}")

    # 2) B4 synthesize with IND≤25%
    print("=== synthesize B4 + IND≤25% ===")
    syn_as_of = max(str(load_leg(P[k])["session"].max())[:10] for mix in GROUPS.values() for k in mix)
    ind_map = _check_loaded_pin(load_industry_asof(as_of=syn_as_of, sw_path=sw_path))
    B4_OUT.mkdir(parents=True, exist_ok=True)
    synth_meta = {}
    weight_files = {}
    for tag, mix in GROUPS.items():
        for aum in (600000, 1000000):
            W, meta = build_topn(mix, aum, tag, ind_map)
            fp = B4_OUT / f"{tag}_topN_{aum // 10000}w.parquet"
            W.to_parquet(fp, index=False)
            meta["file"] = str(fp.relative_to(ROOT))
            meta["sha256"] = hashlib.sha256(fp.read_bytes()).hexdigest()
            synth_meta[f"{tag}_{aum // 10000}w"] = meta
            weight_files[(tag, aum)] = fp
            print(tag, aum, meta["sessions"], "max_w", round(meta["max_stock_w"] or 0, 4),
                  "ind_cut_mean", round(meta["ind_cut_mean"], 6),
                  "max_ind_share", round(meta["max_ind_sleeve_share_after"], 4))
    (B4_OUT / "synth_meta.json").write_text(json.dumps(synth_meta, ensure_ascii=False, indent=2))

    print("=== book-smoke B4 X2 ===")
    b4_results = {}
    for aum in (600000, 1000000):
        fp = weight_files[("B4_50_25_25", aum)]
        smoke_dir = B4_OUT / f"smoke_B4_{aum // 10000}w"
        print("smoke B4", aum, "...")
        sm = run_smoke(fp, smoke_dir, str(aum))
        if not sm.get("ok"):
            b4_results[str(aum)] = {"ok": False, "returncode": sm.get("returncode"), "log": sm.get("log")}
            print("  FAIL", sm.get("returncode"))
            continue
        arm = extract_arm(sm["summary"], aum, smoke_dir)
        arm["sw_pit_required"] = synth_meta[f"B4_50_25_25_{aum // 10000}w"].get("sw_pit_required")
        arm["ok"] = sw_pit_required_ok(arm["sw_pit_required"])  # C r3: missing mandatory sw_pit field -> arm not OK
        if not arm["ok"]:
            arm["error"] = "sw_pit_required_missing"
        b4_results[str(aum)] = arm
        print(f"  B4 {aum}: CAGR={arm.get('cagr')} MDD={arm.get('mdd')} breach={arm.get('mdd25_breach')}")

    # 3) smallcap + industry
    print("=== smallcap + industry ===")
    attrs = {}
    # capacity_adv on X2 slice of pos weights
    Wcap = pd.read_parquet(pos)
    if "session" not in Wcap.columns:
        Wcap["session"] = Wcap["date"].astype(str).str[:10]
    attr_cap = smallcap_and_industry(Wcap, "capadv", sw_path=sw_path)
    (OUT / "capadv_x2_smallcap_attr.json").write_text(json.dumps(attr_cap, ensure_ascii=False, indent=2))
    pd.DataFrame(attr_cap.get("industry_weight_time_share", [])).to_csv(OUT / "capadv_x2_industry_share.csv", index=False)
    attrs["capadv"] = attr_cap
    print("capadv smallcap", attr_cap.get("mean_smallcap_weight_of_book"), "focus", attr_cap.get("focus_industries"))

    for aum in (600000, 1000000):
        W = pd.read_parquet(weight_files[("B4_50_25_25", aum)])
        attr = smallcap_and_industry(W, f"B4_{aum // 10000}w", sw_path=sw_path)
        (B4_OUT / f"b4_{aum // 10000}w_smallcap_attr.json").write_text(json.dumps(attr, ensure_ascii=False, indent=2))
        pd.DataFrame(attr.get("industry_weight_time_share", [])).to_csv(
            B4_OUT / f"b4_{aum // 10000}w_industry_share.csv", index=False
        )
        attrs[f"B4_{aum // 10000}w"] = attr
        print(f"B4 {aum} smallcap", attr.get("mean_smallcap_weight_of_book"), "focus", attr.get("focus_industries"))

    top300 = load_top300_baseline()
    # also pull nav yearly for top300 if available
    for aum in (600000, 1000000):
        navp = ROOT / f"output/v3/book_smoke_g1g5_capacity_adv_x2/aum_{aum}/X2/BOOK/nav.csv"
        if navp.exists():
            wr = win_rates(navp)
            top300[str(aum)].update(wr)
            top300[str(aum)]["nav_path"] = str(navp.relative_to(ROOT))

    cap_arms = [
        (f"capadv HI_LIQ\n{a//10000}万", cap_results.get(str(a), {})) for a in (600000, 1000000)
    ]
    b4_arms = [
        (f"B4 HI_LIQ\n{a//10000}万", b4_results.get(str(a), {})) for a in (600000, 1000000)
    ]
    # add top300 as reference lines in yearly/nav via synthetic entries
    for a in (600000, 1000000):
        t = top300.get(str(a), {})
        if t.get("nav_path") or t.get("cagr") is not None:
            cap_arms.append((f"capadv top300\n{a//10000}万", t))

    charts = make_charts(cap_arms[:2] + b4_arms, [], attrs)  # main bars: cap+b4 only
    # also yearly/nav with top300
    charts2 = make_charts([], [], {})  # no-op
    # redo yearly+nav with baselines
    fig_paths = charts
    # overwrite yearly/nav including top300
    extra = []
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for lab, m in (cap_arms[:2] + b4_arms + cap_arms[2:]):
        yc = m.get("yearly_cagr") or {}
        if not yc:
            continue
        ys = sorted(yc)
        ax.plot(ys, [yc[y] * 100 for y in ys], marker="o", label=lab.replace("\n", " "))
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("年化 %")
    ax.set_title("HI_LIQ vs top300 X2 分年（样本内；过渡 Top-N）")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    p2 = OUT / "hiliq_yearly.png"
    fig.tight_layout(); fig.savefig(p2, dpi=120); plt.close()
    extra.append(str(p2.relative_to(ROOT)))

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for lab, m in (cap_arms[:2] + b4_arms + cap_arms[2:]):
        npth = m.get("nav_path")
        if not npth:
            continue
        nav = pd.read_csv(ROOT / npth)
        et = pd.to_datetime(nav["_et"] if "_et" in nav.columns else nav.columns[0])
        n = nav["nav"] / nav["nav"].iloc[0]
        ax.plot(et, n, label=lab.replace("\n", " "), lw=1.1)
    ax.legend(fontsize=7)
    ax.set_title("HI_LIQ vs top300 NAV（归一）X2 — 过渡 Top-N；主路径 OPTIMIZER DRAFT")
    ax.grid(True, alpha=0.3)
    p3 = OUT / "hiliq_nav.png"
    fig.tight_layout(); fig.savefig(p3, dpi=120); plt.close()
    extra.append(str(p3.relative_to(ROOT)))

    # table PNG
    fig, ax = plt.subplots(figsize=(12, 3.8))
    ax.axis("off")
    rows = [["臂", "AUM", "CAGR", "MDD", "Calmar", "日胜率", "填单", "MDD≤25%"]]
    for name, by in (("capadv HI_LIQ", cap_results), ("B4 HI_LIQ", b4_results)):
        for aum in (600000, 1000000):
            m = by.get(str(aum), {})
            if m.get("cagr") is None:
                continue
            rows.append([
                name, f"{aum//10000}万",
                f"{m['cagr']*100:.2f}%", f"{m['mdd']*100:.2f}%",
                f"{m.get('calmar') or 0:.2f}",
                f"{(m.get('win_rate_daily') or 0)*100:.1f}%",
                f"{(m.get('fill_ratio') or 0)*100:.1f}%",
                "破" if m.get("mdd25_breach") else "未破",
            ])
    for aum in (600000, 1000000):
        m = top300[str(aum)]
        rows.append([
            "capadv top300", f"{aum//10000}万",
            f"{m['cagr']*100:.2f}%", f"{m['mdd']*100:.2f}%",
            f"{(m.get('calmar') or 0):.2f}", "—", "—",
            "破" if m["mdd"] < -0.25 else "未破",
        ])
    table = ax.table(cellText=rows, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.05, 1.35)
    ax.set_title("HI_LIQ_V1.1 过渡 Top-N X2（样本内）vs top300 — live/promotion=false", fontsize=10)
    p4 = OUT / "hiliq_table.png"
    fig.tight_layout(); fig.savefig(p4, dpi=140); plt.close()
    extra.append(str(p4.relative_to(ROOT)))

    summary = {
        "run_id": f"hiliq_capadv_b4_x2_{time.strftime('%Y%m%d_%H%M%S')}",
        "banner_zh": "过渡 Top-N；主路径 = OPTIMIZER_V1 DRAFT（等 Leo）；未动 FROZEN/纸面轨；live/promotion=false",
        "live": False,
        "promotion": False,
        # C r3b: freshness/integrity of the table actually read (CLEAN -> sw_l1_pit manifest check)
        "sw_pit_freshness": sw_l1_table_check_last(ind_map.path),
        "industry_cap_on_stale_sw_pit": bool((sw_l1_table_check_last(ind_map.path) or {}).get("stale")),
        "sw_l1_stale_lag_only": bool((sw_l1_table_check_last(ind_map.path) or {}).get("stale_lag_only")),
        "disclosure_zh": (sw_l1_table_check_last(ind_map.path) or {}).get("disclosure_zh", ""),
        "frozen_config_touched": False,
        "paper_tracks_touched": False,
        "track": "HI_LIQ_V1.1_TRANSITIONAL_TOPN",
        "window": list(X2),
        "window_label": "样本内",
        "engine": "quantlab.cli book-smoke --run-nav / ExecConfig.strategy_v1",
        "concentration": {"N": {str(k): v for k, v in N_BY_AUM.items()}, "single_name_cap": CAP, "ind_cap_stock_sleeve": IND_CAP, "excess_to": BAL},
        "mix_B4": GROUPS["B4_50_25_25"],
        "sealed": sealed_status(P["capacity_adv"]),
        "capacity_adv": cap_results,
        "B4": b4_results,
        "top300_baseline": top300,
        "synth_meta": synth_meta,
        "smallcap_attr": {
            k: {
                "mean_smallcap_weight_of_book": v.get("mean_smallcap_weight_of_book"),
                "pct_days_any_smallcap_holding": v.get("pct_days_any_smallcap_holding"),
                "mean_below_median_mv_weight_of_book": v.get("mean_below_median_mv_weight_of_book"),
                "focus_industries": v.get("focus_industries"),
                "top_industries": (v.get("industry_weight_time_share") or [])[:8],
            }
            for k, v in attrs.items()
        },
        "alpha_diag_note_zh": "旧 Alpha 18.17%/4.52% capadv 诊断已作废，见 docs/v2/ALPHA_EQUITY_SIGN_RECON_20261018_ZH.md §7；本回执以 book-smoke 为准",
        # C r3 (主 Agent 06:49 ET item 3): mandatory sw_pit fields per industry-using arm / attribution
        "sw_pit_sha256": ind_map.sha256, "sw_pit_path": ind_map.path,
        "sw_pit_required_by_arm": {**{f"B4_{k}": (v or {}).get("sw_pit_required") for k, v in b4_results.items()},
                                   **{f"attr_{k}": v.get("sw_pit_required") for k, v in attrs.items()}},
        "charts": fig_paths + extra,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    summary["sw_pit_required_ok"] = all(sw_pit_required_ok(v) for v in summary["sw_pit_required_by_arm"].values())
    (OUT / "capadv_x2_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    (B4_OUT / "summary.json").write_text(json.dumps({
        "B4": b4_results, "synth_meta": synth_meta, "banner_zh": summary["banner_zh"],
        "live": False, "promotion": False,
    }, ensure_ascii=False, indent=2))
    print("WROTE", OUT / "capadv_x2_summary.json")
    print("elapsed", summary["elapsed_sec"], "s")
    return 0


def _arm_ok(sm: dict, m: dict, req: dict | None = None) -> bool:
    """C r3: also requires the mandatory sw_pit fields (sw_pit_required_ok); missing -> arm not OK -> VOID."""
    return bool(sm.get("ok") and sm.get("returncode") == 0 and sm.get("summary_fresh")
                and "error" not in m and m.get("cagr") is not None and m.get("mdd") is not None
                and sw_pit_required_ok(req))


def _pitfix_allow_check(allow_ok) -> dict:
    """While PITFIX_PAUSED, pitfix-compare runs only with --pitfix-allow-ok <path> (C r3b; r3c Arch 016ae55e P3-4):
    research.sw_members_asof.check_allow_ok — key=value only (colon form rejected), exactly
    allow_pitfix_compare=true, live=false, promotion=false, expires_et (with UTC offset) not yet passed, not under
    _consumed/. Checked before any data read or write; path + sha256 + expiry go into summary.json."""
    if allow_ok is None:
        raise SystemExit("pitfix-compare PAUSED (主 Agent 2026-10-18 06:49 ET): pass --pitfix-allow-ok <Arch .ok> with "
                         f"{PITFIX_ALLOW_FIELD}=true, live=false, promotion=false, expires_et=<ISO 8601 with offset>")
    return check_allow_ok(allow_ok, PITFIX_ALLOW_FIELD, root=ROOT, flag="--pitfix-allow-ok")


def pitfix_compare(out_dir_arg: str, sw_path=None, allow_ok=None) -> int:
    """PIT-fix before/after (prereg docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md). B4 only; same legs/window/cost;
    only the industry map differs: before = legacy load_industry_map (verbatim), after = as-of + gap carry.
    All checks happen BEFORE any write; any arm failure -> VOID.md + all_ok=false + exit 1. Disclosure only.
    C r3b: PAUSED by default (PITFIX_PAUSED); runs only with an explicit allow .ok (_pitfix_allow_check)."""
    allow = _pitfix_allow_check(allow_ok) if PITFIX_PAUSED else None  # nothing is read or written before this
    t0 = time.time()
    out_dir = pitfix_out_dir_guard(ROOT, out_dir_arg)          # P2-2: under output/strategy_hiliq/, must not exist
    mix = GROUPS["B4_50_25_25"]
    for k in mix:
        if not P[k].exists():
            raise SystemExit(f"missing leg {k}: {P[k]}")
    swp = SW_L1_LEGACY_PATH.resolve() if sw_path is None else _sw_path(sw_path)  # C r3b: pitfix default = legacy
    if swp != SW_L1_LEGACY_PATH.resolve():  # before arm = verbatim legacy load_industry_map (reads the legacy path)
        raise SystemExit(f"--sw-pit-path {swp} != {SW_L1_LEGACY_PATH}: legacy before arm reads that path only "
                         "(parametrize load_industry_map in the v2 round)")
    sha_pin = check_sw_l1_pin(swp, pin=SW_L1_LEGACY_SHA_PIN)    # P3-6: explicit raise; file actually used
    syn_as_of = max(str(load_leg(P[k])["session"].max())[:10] for k in mix)
    legacy = load_industry_map(as_of=syn_as_of)                 # P2-4: verbatim legacy (before arm)
    asof = load_industry_asof(as_of=syn_as_of, static_map=legacy, sw_path=swp)
    if asof.sha256 != SW_L1_LEGACY_SHA_PIN:
        raise SwPitIntegrityError(f"sw_pit l1 sha at as-of load {asof.sha256} != pinned {SW_L1_LEGACY_SHA_PIN}")
    out_dir.mkdir(parents=False, exist_ok=False)                # first write; parent output/strategy_hiliq exists
    res, all_ok = {}, True
    for arm, im in (("before_static", legacy), ("after_asof", asof)):
        for aum in (600000, 1000000):
            W, meta = build_topn(mix, aum, "B4_50_25_25", im)
            fp = out_dir / f"{arm}_B4_{aum // 10000}w.parquet"
            W.to_parquet(fp, index=False)
            sd = out_dir / f"smoke_{arm}_{aum // 10000}w"
            sm = run_smoke(fp, sd, str(aum))
            m = extract_arm(sm["summary"], aum, sd) if sm.get("ok") else {"error": "smoke_failed"}
            hold = W.loc[~W["instrument"].map(_is_etf) & (W["session"] >= X2[0]) & (W["session"] <= X2[1]),
                         ["session", "instrument", "weight"]]
            rs = asof.reclass_share(hold, weight_col="weight")  # same holdings; as-of vs static (legacy) map
            req = sw_pit_required(asof, rs, "n_rows_static_missing" if arm == "before_static" else "n_rows_asof_missing")
            ok = _arm_ok(sm, m, req)
            all_ok &= ok
            row = {k: m.get(k) for k in ("cagr", "mdd", "calmar", "win_rate_daily", "win_rate_monthly", "cost_pct", "error")}
            row.update(ok=ok, returncode=sm.get("returncode"), summary_fresh=sm.get("summary_fresh"), log=sm.get("log"),
                       n_ind_cap_sessions_x2=meta["n_ind_cap_sessions_x2"],
                       n_unk_over_cap_sessions_x2=meta["n_unk_over_cap_sessions_x2"],
                       ind_cut_mean=meta["ind_cut_mean"], max_ind_sleeve_share_after=meta["max_ind_sleeve_share_after"],
                       reclass_share_x2=meta.get("reclass_share_x2"), sw_asof_stats=meta.get("sw_asof_stats"),
                       weights_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(), sw_pit_required=req)
            if arm == "before_static":  # P3-7: before arm vs existing b4 weights — disclosure only, not a gate
                ref = B4_OUT / f"B4_50_25_25_topN_{aum // 10000}w.parquet"
                cmp = {"ref": str(ref.relative_to(ROOT)), "ref_exists": ref.exists()}
                if ref.exists():
                    R0 = pd.read_parquet(ref, columns=["session", "instrument", "weight"])
                    cmp["ref_sha256"] = hashlib.sha256(ref.read_bytes()).hexdigest()
                    j = W[["session", "instrument", "weight"]].merge(R0, on=["session", "instrument"], how="outer",
                                                                    suffixes=("", "_ref")).fillna(0.0)
                    cmp["max_abs_weight_diff"] = float((j["weight"] - j["weight_ref"]).abs().max())
                    cmp["same_sha"] = cmp["ref_sha256"] == row["weights_sha256"]
                row["before_vs_existing_b4"] = cmp
            res[f"{arm}_{aum // 10000}w"] = row
    fr = sw_pit_last_result() or {}
    summ = {"prereg": "docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md", "all_ok": bool(all_ok), "window": list(X2),
            "gap_carry_rule": ("主 Agent 2026-10-18 ~05:45/06:01 ET + C r2 06:16 ET：d 为 SSE 开市日、无有效行，且旧行"
                               "（in_date 可解析且 ≤ out_date）满足 d 之前最近的开市日 ≤ out_date < d 时，沿用旧行业当天；"
                               "不要求有后继行（见 n_rows_gap_carry_no_successor）；out_date 落在非开市日的沿用见 "
                               "n_rows_gap_carry_out_on_closed_day"),
            "trade_cal_sha256": asof.cal.sha256,
            "pitfix_allow": allow,  # C r3b: allow .ok path + sha (None only if PITFIX_PAUSED is False)
            "sw_pit_sha256": asof.sha256, "sw_pit_path": asof.path, "on_overlap": asof.on_overlap,
            "overlap_tiebreak": OVERLAP_TIEBREAK,
            "sw_l1_sha256_pin_check": sha_pin, "sw_l1_sha256_asof_load": asof.sha256,
            "results": res, "sw_pit_freshness": fr, "disclosure_zh": fr.get("disclosure_zh", ""),
            "industry_cap_on_stale_sw_pit": bool(fr.get("stale")), "live": False, "promotion": False,
            "disclosure_only": True, "elapsed_sec": round(time.time() - t0, 1),
            "peak_rss_mb_self": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            "peak_rss_mb_children": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024}
    (out_dir / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=2))
    if not all_ok:
        bad = [k for k, v in res.items() if not v["ok"]]
        (out_dir / "VOID.md").write_text(
            "# VOID — pitfix_compare\n\n按预注册第 3 节：有 arm 未成功（returncode≠0、summary 非本次生成、extract 报错，"
            "或 sw_pit 必报字段缺失），"
            f"整轮作废，不得引用数值。\n\n失败 arm：{', '.join(bad)}\n", encoding="utf-8")
        print("VOID:", bad)
        return 1
    return 0


def _take_opt(a: list, flag: str):
    """Remove `flag <value>` from a (in place) and return value; None if absent."""
    if flag not in a:
        return None
    i = a.index(flag)
    if i + 1 >= len(a) or a[i + 1].startswith("--"):
        raise SystemExit(f"usage: {flag} <file>")
    v = a[i + 1]
    del a[i:i + 2]
    return v


def _cli(argv: list) -> int:
    """[--pitfix-compare <out_dir> --pitfix-allow-ok <Arch .ok>] [--sw-pit-path <file>] (C r3: path parameter;
    C r3b: default CLEAN for main, legacy sw_pit for the paused pitfix-compare, which needs an explicit allow .ok)."""
    a, out_dir = list(argv), None
    sw_path = _take_opt(a, "--sw-pit-path")
    allow_ok = _take_opt(a, "--pitfix-allow-ok")
    if a and a[0] == "--pitfix-compare":
        if len(a) != 2:
            raise SystemExit("usage: --pitfix-compare <out_dir under output/strategy_hiliq/> "
                             "--pitfix-allow-ok <Arch .ok> [--sw-pit-path <file>]")
        out_dir = a[1]
    elif a:
        raise SystemExit(f"unknown arguments: {a}")
    if out_dir is None and allow_ok is not None:
        raise SystemExit("--pitfix-allow-ok is only valid with --pitfix-compare")
    return (pitfix_compare(out_dir, sw_path=sw_path, allow_ok=allow_ok) if out_dir is not None
            else main(sw_path=sw_path))


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
