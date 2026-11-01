#!/usr/bin/env python3
"""FULLA_V1 B4 research synthesis + Eng book-smoke X2 (research-only).
Leo 07:42 dual-track: FULLA=research; do NOT touch FROZEN_CONFIG / paper / live.
B4 = capacity_adv/earnings_event/insider_increase 50/25/25
per-leg topN (60万 N=6, 100万 N=10), portfolio single-name ≤6% → 510300.
"""
from __future__ import annotations
import json, subprocess, sys, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# C r3b: sw_pit_freshness (主 Agent 10-18 05:06; Arch ccc7546f) is now reached via sw_members_asof.sw_l1_table_check
from research.sw_members_asof import IndustryAsOf, load_sw_l1, sw_l1_asof_chunked  # PIT fix (Arch 10-18 P2; r2 3f195231)
from research.sw_members_asof import load_trade_cal  # C r2: calendar passed explicitly (no module default; Arch c6f97571 P3-5)
from research.sw_members_asof import SW_L1_REL, sw_pit_required, sw_pit_required_ok  # C r3 (主 Agent 06:49 ET)
from research.sw_members_asof import sw_l1_table_check, sw_l1_table_check_last  # C r3b: check on the table read
from research.sw_pit_freshness import SwPitIntegrityError
OUT = ROOT / "output/strategy_fulla/b4"
OUT.mkdir(parents=True, exist_ok=True)
LEGS = ROOT / "output/strategy_fulla/legs"
BAL = "510300.SH"
CAP = 0.06
N_BY_AUM = {600000: 6, 1000000: 10}
X2 = ("2024-06-03", "2026-10-09")
ANN_DAYS = 244  # Eng standard (report note; book-smoke uses its own)
SW_L1_PATH_DEFAULT = ROOT / SW_L1_REL  # C r3 (Arch 06:50): table path is a parameter; C r3b: SW_L1_REL = CLEAN
# C r3b (Arch 2026-10-18 ~07:00 ET): CLEAN data/v2/sw_l1_pit/industry_members_sw_l1_tushare.parquet (leaf 23/24 pin)
SW_L1_SHA_PIN = "89d4afa337435a2302b5c13fd4cf049b71eda2f20e1d9094f15d62cdb587f66c"  # same pin as hx2
ON_OVERLAP_RESEARCH = "count"  # 主 Agent 06:49 ET: research runs disclose overlaps instead of raising


def _sw_path(sw_path=None) -> Path:
    """Resolved sw_pit L1 table path; None -> SW_L1_PATH_DEFAULT; relative -> ROOT / sw_path."""
    p = SW_L1_PATH_DEFAULT if sw_path is None else Path(sw_path)
    return (p if p.is_absolute() else ROOT / p).resolve()

P = {
    "capacity_adv": LEGS / "g1g5_capacity_adv_fulla_v1_daily_weights_20261014_192953.parquet",
    "earnings_event": LEGS / "g1g5_earnings_event_fulla_v1_daily_weights_20261014_194511.parquet",
    "insider_increase": LEGS / "g1g5_insider_increase_fulla_v1_daily_weights_20261014_194511.parquet",
    "equity_incentive": LEGS / "g1g5_equity_incentive_fulla_v1_daily_weights_20261014_194511.parquet",
    "report_rc_allup": LEGS / "g1g5_report_rc_allup_fulla_v1_daily_weights_20261014_194511.parquet",
    "insurer_surv": LEGS / "g1g5_insurer_surv_fulla_v1_daily_weights_20261014_194511.parquet",
}

# Primary B4 + optional research overlays (cheap)
GROUPS = {
    "B4_50_25_25": {"capacity_adv": 0.5, "earnings_event": 0.25, "insider_increase": 0.25},
    "L11_cap50_rc50": {"capacity_adv": 0.5, "report_rc_allup": 0.5},  # 叶11 satellite
    "L14_cap50_surv50": {"capacity_adv": 0.5, "insurer_surv": 0.5},  # 叶14 satellite
    "S6_cap50_ee25_eq25": {"capacity_adv": 0.5, "earnings_event": 0.25, "equity_incentive": 0.25},  # shadow only
}

etf = lambda x: str(x)[:2] in ("51", "56", "58", "15") or str(x).endswith((".SH", ".SZ")) and str(x)[:2] in ("51", "56", "58", "15")

def _is_etf(inst: str) -> bool:
    s = str(inst)
    code = s.split(".")[0] if "." in s else s
    return code[:2] in ("51", "56", "58", "15")


def load_leg(path: Path) -> pd.DataFrame:
    d = pd.read_parquet(path, columns=["session", "instrument", "instrument_id", "weight"])
    d["session"] = d["session"].astype(str).str[:10]
    d = d[d["weight"] > 0].copy()
    return d


def build_topn(mix: dict, aum: int, tag: str) -> pd.DataFrame:
    used = list(mix)
    D = {k: load_leg(P[k]) for k in used}
    common = sorted(set.intersection(*[set(d["session"]) for d in D.values()]))
    # restrict to X2 for book-smoke efficiency (keep full for sealed check)
    G = {}
    for k, d in D.items():
        G[k] = {s: g.set_index("instrument")["weight"] for s, g in d.groupby("session")}
    n = N_BY_AUM[aum]
    rows = []
    cap_cut = 0.0
    for s in common:
        agg = {}
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
            keep = keep * (st.sum() / keep.sum())
            for i, v in keep.items():
                agg[i] = agg.get(i, 0.0) + float(v)
        for i in list(agg):
            if (not _is_etf(i)) and agg[i] > CAP:
                cap_cut += agg[i] - CAP
                agg[BAL] = agg.get(BAL, 0.0) + agg[i] - CAP
                agg[i] = CAP
        t = sum(agg.values())
        if t <= 0:
            continue
        for i, v in agg.items():
            rows.append((s, i, v / t))
    W = pd.DataFrame(rows, columns=["session", "instrument", "weight"])
    W = W.groupby(["session", "instrument"], as_index=False)["weight"].sum()
    assert ((W.groupby("session")["weight"].sum() - 1).abs() < 1e-8).all()
    assert (W["weight"] >= -1e-12).all()
    W["date"] = W["session"]
    W["target_weight"] = W["weight"]
    def to_id(x: str) -> str:
        if "." in x:
            code, mkt = x.split(".", 1)
            return f"{mkt.lower()}.{code}"
        return x
    W["instrument_id"] = W["instrument"].map(to_id)
    W["mechanism_tag"] = f"fulla_v1_{tag}_topN_{aum // 10000}w"
    W["who_pays_zh"] = "FULLA_V1 研究混合（非纸面）"
    W["universe_id"] = "FULLA_V1"
    # drop exact zeros
    W = W[W["weight"] > 0].copy()
    meta = dict(
        tag=tag, aum=aum, N=n, sessions=[common[0], common[-1], len(common)],
        rows=len(W), max_stock_w=float(W.loc[~W["instrument"].map(_is_etf), "weight"].max()) if len(W) else None,
        cap_cut_mean=cap_cut / max(len(common), 1),
        mean_510300=float(W[W["instrument"] == BAL].groupby("session")["weight"].sum().reindex(common).fillna(0).mean()),
        stock_names_median=float(W.loc[~W["instrument"].map(_is_etf)].groupby("session").size().median()),
    )
    return W, meta


def run_book_smoke(stock_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "quantlab.cli", "book-smoke", "--run-nav",
        "--stock-path", str(stock_path.relative_to(ROOT) if stock_path.is_absolute() else stock_path),
        "--out", str(out_dir.relative_to(ROOT)),
        "--windows", "X2",
        "--capitals", "600000,1000000",
        "--sleeves", '{"core":0,"stock":1,"alpha_event":0}',
    ]
    log = out_dir / "run.log"
    with open(log, "w") as f:
        r = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, text=True)
    summary_path = out_dir / "book_smoke_summary.json"
    if not summary_path.exists():
        return {"ok": False, "returncode": r.returncode, "log": str(log)}
    return {"ok": True, "returncode": r.returncode, "summary": json.loads(summary_path.read_text()), "log": str(log)}


def metrics_from_smoke(summary: dict, aum: int) -> dict:
    by = summary.get("by_capital", {})
    key = str(aum)
    book = by.get(key, {}).get("X2/BOOK") or by.get(key, {}).get("BOOK") or {}
    if not book:
        # alternate shape
        for arm, block in by.get(key, {}).items():
            if "BOOK" in arm:
                book = block
                break
    out = {
        "cagr": book.get("cagr"),
        "mdd": book.get("mdd"),
        "calmar": book.get("calmar"),
        "sharpe": book.get("sharpe"),
        "fill_ratio": book.get("fill_ratio"),
        "cost_pct": book.get("cost_pct_initial"),
        "n_days": book.get("n_signals"),
    }
    # win rates from nav
    nav_path = OUT / "smoke" / f"aum_{aum}"  # placeholder; real path below
    return out, book


def win_rates(nav_csv: Path) -> dict:
    if not nav_csv.exists():
        return {}
    nav = pd.read_csv(nav_csv)
    nav["_et"] = pd.to_datetime(nav["_et"])
    nav = nav.sort_values("_et")
    r = nav["nav"].pct_change()
    daily = float((r.dropna() > 0).mean()) if r.notna().any() else None
    nav["ym"] = nav["_et"].dt.to_period("M")
    mret = nav.groupby("ym")["nav"].last().pct_change()
    monthly = float((mret.dropna() > 0).mean()) if mret.notna().any() else None
    # yearly cagr within calendar years (partial years annualized by day count)
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
    }


def smallcap_and_industry(W: pd.DataFrame, tag: str, *, sw_path=None) -> dict:
    """PIT total_mv bottom 30% contribution + SW L1 industry share. Disclosure only."""
    Wx = W[(W["session"] >= X2[0]) & (W["session"] <= X2[1])].copy()
    Wx = Wx[~Wx["instrument"].map(_is_etf)].copy()
    if Wx.empty:
        return {"tag": tag, "empty": True}
    # daily_basic total_mv
    db = pd.read_parquet(
        ROOT / "data/v2/valuation/daily_basic_full_tushare.parquet",
        columns=["ts_code", "trade_date", "total_mv"],
    )
    db["trade_date"] = db["trade_date"].astype(str).str.replace("-", "").str[:8]
    # normalize session to YYYYMMDD
    Wx["td"] = Wx["session"].str.replace("-", "")
    db = db[(db["trade_date"] >= Wx["td"].min()) & (db["trade_date"] <= Wx["td"].max())]
    # cross-section bottom 30%
    need_dates = set(Wx["td"].unique())
    db = db[db["trade_date"].isin(need_dates)].copy()
    # vectorized cross-section quantiles
    db["q30"] = db.groupby("trade_date")["total_mv"].transform(lambda s: s.quantile(0.30))
    db["med"] = db.groupby("trade_date")["total_mv"].transform("median")
    db["is_small"] = db["total_mv"] <= db["q30"]
    db["below_med"] = db["total_mv"] <= db["med"]
    flags = db[["ts_code", "trade_date", "is_small", "below_med", "total_mv"]]
    merged = Wx.merge(flags, left_on=["instrument", "td"], right_on=["ts_code", "trade_date"], how="left")
    miss = float(merged["is_small"].isna().mean())
    day_w = merged.groupby("session").apply(
        lambda g: pd.Series({
            "small_w": g.loc[g["is_small"] == True, "weight"].sum(),
            "below_med_w": g.loc[g["below_med"] == True, "weight"].sum(),
            "stock_w": g["weight"].sum(),
        })
    )
    # industry PIT: as-of join on in_date/out_date
    # PIT fix (Arch 10-18 P2 + R4 口径): as-of session, in_date < session AND (out_date null OR out_date >= session)
    # replaces the previous in_date<=session / static last-known name approximation
    cal = load_trade_cal(ROOT)
    sw = load_sw_l1(ROOT, path=_sw_path(sw_path))
    # C r3b: integrity raises / stale warns on the table actually read (legacy sw_pit or CLEAN manifest)
    sw_l1_table_check(ROOT, sw, str(Wx["session"].max())[:10], cal)
    ia = IndustryAsOf(sw, cal=cal, on_overlap=ON_OVERLAP_RESEARCH)
    if ia.sha256 != SW_L1_SHA_PIN:  # C r3: pin enforced on the bytes actually parsed
        raise SwPitIntegrityError(f"sw_pit l1 sha {ia.sha256} ({ia.path}) != pinned {SW_L1_SHA_PIN}")
    m2 = Wx.copy()
    m2["l1_name"] = sw_l1_asof_chunked(ia.sw, Wx, "instrument", "session", cal=ia.cal,  # r3c P3-6: chunk by session
                                       on_overlap=ia.on_overlap).values  # + 主 Agent 10-18 gap carry
    reclass = ia.reclass_share(Wx, weight_col="weight")  # disclosure only
    ind_share = (
        m2.groupby("l1_name")["weight"].sum() / m2["weight"].sum()
    ).sort_values(ascending=False)
    ind_share = ind_share[ind_share.index.notna()]
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
            {"sw_name": str(k), "weight_time_share": float(v)} for k, v in ind_share.head(25).items()
        ],
        "reclass_share": reclass,
        "sw_pit_required": sw_pit_required(ia, reclass),  # 主 Agent 06:49 ET item 3
        "note_zh": "行业用申万一级 as-of 归属（in_date<session 且 out_date 空或>=session，对齐 Intel；改分类空档日沿用旧行业 1 天，主 Agent 10-18 ~05:45 ET 裁定）；小盘为逐日截面后30%。",
    }


def make_charts(results: dict, baselines: dict):
    # table comparison chart
    arms = []
    for tag, by_aum in results.items():
        for aum_s, m in by_aum.items():
            if not isinstance(m, dict) or m.get("cagr") is None:
                continue
            arms.append((tag, int(aum_s), m))
    if not arms:
        return []
    fig, ax = plt.subplots(figsize=(10, 4.5))
    labels, cagrs, mdds = [], [], []
    for tag, aum, m in arms:
        labels.append(f"{tag}\n{aum//10000}万")
        cagrs.append(m["cagr"] * 100)
        mdds.append(m["mdd"] * 100)
    x = np.arange(len(labels))
    ax.bar(x - 0.2, cagrs, 0.4, label="CAGR%")
    ax.bar(x + 0.2, mdds, 0.4, label="MDD%")
    ax.axhline(-25, color="r", ls="--", lw=1, label="MDD −25%")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend()
    ax.set_title("FULLA_V1 research X2 (样本内) — CAGR / MDD")
    ax.grid(True, axis="y", alpha=0.3)
    p1 = OUT / "fulla_b4_cagr_mdd.png"
    fig.tight_layout()
    fig.savefig(p1, dpi=120)
    plt.close(fig)

    # yearly for B4 60/100
    fig, ax = plt.subplots(figsize=(8, 4))
    for aum in (600000, 1000000):
        m = results.get("B4_50_25_25", {}).get(str(aum), {})
        yc = m.get("yearly_cagr") or {}
        if yc:
            ys = sorted(yc)
            ax.plot(ys, [yc[y] * 100 for y in ys], marker="o", label=f"B4 FULLA {aum//10000}万")
    # baselines yearly from capadv summary if present
    ax.set_title("B4 FULLA 分年年化（样本内）")
    ax.set_ylabel("%")
    ax.legend()
    ax.grid(True, alpha=0.3)
    p2 = OUT / "fulla_b4_yearly.png"
    fig.tight_layout()
    fig.savefig(p2, dpi=120)
    plt.close(fig)

    # NAV chart for B4
    fig, ax = plt.subplots(figsize=(9, 4))
    for aum in (600000, 1000000):
        m = results.get("B4_50_25_25", {}).get(str(aum), {})
        npth = m.get("nav_path")
        if not npth:
            continue
        nav = pd.read_csv(ROOT / npth)
        nav["_et"] = pd.to_datetime(nav["_et"])
        ax.plot(nav["_et"], nav["nav"] / nav["nav"].iloc[0], label=f"B4 {aum//10000}万")
    ax.set_title("B4 FULLA NAV（归一）X2 样本内")
    ax.legend()
    ax.grid(True, alpha=0.3)
    p3 = OUT / "fulla_b4_nav.png"
    fig.tight_layout()
    fig.savefig(p3, dpi=120)
    plt.close(fig)

    # industry pie for B4 60w
    attr = json.loads((OUT / "b4_60w_smallcap_attr.json").read_text()) if (OUT / "b4_60w_smallcap_attr.json").exists() else None
    paths = [str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT)), str(p3.relative_to(ROOT))]
    if attr and attr.get("industry_weight_time_share"):
        top = attr["industry_weight_time_share"][:12]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh([t["sw_name"] for t in top][::-1], [t["weight_time_share"] * 100 for t in top][::-1])
        ax.set_xlabel("% weight×time")
        ax.set_title("B4 FULLA 申万一级（60万，股票袖）")
        p4 = OUT / "fulla_b4_industry_sw_l1.png"
        fig.tight_layout()
        fig.savefig(p4, dpi=120)
        plt.close(fig)
        paths.append(str(p4.relative_to(ROOT)))
    return paths


def sealed_status() -> dict:
    # legs start 2024-01-02; sealed window 2018-01-02→2024-05-31
    d = load_leg(P["capacity_adv"])
    lo, hi = d["session"].min(), d["session"].max()
    return {
        "sealed_window": ["2018-01-02", "2024-05-31"],
        "legs_coverage": [lo, hi],
        "status": "N/A",
        "note_zh": "FULLA 腿权重仅自 2024-01-02 起；密封窗 2018-01-02→2024-05-31 无完整权重，不发明权重。仅 2024-01-02→2024-05-31 为部分重叠，不作密封声明。",
    }


def main(sw_path=None):
    print("=== synthesize topN weights ===")
    synth_meta = {}
    weight_files = {}
    for tag, mix in GROUPS.items():
        for aum in (600000, 1000000):
            W, meta = build_topn(mix, aum, tag)
            fp = OUT / f"{tag}_topN_{aum // 10000}w.parquet"
            W.to_parquet(fp, index=False)
            # also write check-ish meta
            h = hashlib.sha256(fp.read_bytes()).hexdigest()
            meta["file"] = str(fp.relative_to(ROOT))
            meta["sha256"] = h
            synth_meta[f"{tag}_{aum // 10000}w"] = meta
            weight_files[(tag, aum)] = fp
            print(tag, aum, meta["sessions"], "max_w", round(meta["max_stock_w"], 4), "names_med", meta["stock_names_median"])

    (OUT / "synth_meta.json").write_text(json.dumps(synth_meta, ensure_ascii=False, indent=2))

    print("=== book-smoke (PRIMARY B4 first) ===")
    results = {}
    # Order: B4, L11, L14, S6
    order = ["B4_50_25_25", "L11_cap50_rc50", "L14_cap50_surv50", "S6_cap50_ee25_eq25"]
    for tag in order:
        # book-smoke takes one stock-path; need separate runs per AUM because topN differs.
        # Engine accepts one path — run each AUM separately with matching weights.
        results[tag] = {}
        for aum in (600000, 1000000):
            fp = weight_files[(tag, aum)]
            smoke_dir = OUT / f"smoke_{tag}_{aum // 10000}w"
            print("smoke", tag, aum, "...")
            # book-smoke runs both capitals from one path; pass only matching aum via capitals
            out_dir = smoke_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                sys.executable, "-m", "quantlab.cli", "book-smoke", "--run-nav",
                "--stock-path", str(fp.relative_to(ROOT)),
                "--out", str(out_dir.relative_to(ROOT)),
                "--windows", "X2",
                "--capitals", str(aum),
                "--sleeves", '{"core":0,"stock":1,"alpha_event":0}',
            ]
            log = out_dir / "run.log"
            with open(log, "w") as f:
                r = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, text=True)
            sp = out_dir / "book_smoke_summary.json"
            if not sp.exists():
                results[tag][str(aum)] = {"ok": False, "returncode": r.returncode, "log": str(log.relative_to(ROOT))}
                print("  FAIL", r.returncode)
                continue
            summary = json.loads(sp.read_text())
            arm = extract_arm(summary, aum, out_dir)
            arm["ok"] = True
            results[tag][str(aum)] = arm
            print("  CAGR/MDD", round(arm["cagr"] * 100, 2) if arm.get("cagr") is not None else None,
                  round(arm["mdd"] * 100, 2) if arm.get("mdd") is not None else None)

    # Reuse capacity_adv FULLA numbers
    cap_sum = json.loads((ROOT / "output/strategy_fulla/capadv_x2_summary.json").read_text())
    cap_by = {str(x["aum"]): x for x in cap_sum["by_aum"]}

    baselines = {
        "capacity_adv_FULLA": {
            "600000": {k: cap_by["600000"][k] for k in ("cagr", "mdd", "calmar", "win_rate_daily", "win_rate_monthly", "fill_ratio")},
            "1000000": {k: cap_by["1000000"][k] for k in ("cagr", "mdd", "calmar", "win_rate_daily", "win_rate_monthly", "fill_ratio")},
        },
        "capacity_adv_top300": {
            "600000": {"cagr": 0.1382, "mdd": -0.1007, "calmar": 1.372},
            "1000000": {"cagr": 0.1223, "mdd": -0.1162, "calmar": 1.052},
        },
        "B4_top300_conc_v2": {
            "600000": {"cagr": 0.1511, "mdd": -0.1385, "note": "BOOK_SMOKE_CONC_V2_SUMMARY"},
            "1000000": {"cagr": 0.1424, "mdd": -0.1317, "note": "BOOK_SMOKE_CONC_V2_SUMMARY"},
        },
    }

    print("=== smallcap + industry for B4 60w/100w ===")
    attrs = {}
    for aum in (600000, 1000000):
        W = pd.read_parquet(weight_files[("B4_50_25_25", aum)])
        attr = smallcap_and_industry(W, f"B4_{aum // 10000}w", sw_path=sw_path)
        ap = OUT / f"b4_{aum // 10000}w_smallcap_attr.json"
        ap.write_text(json.dumps(attr, ensure_ascii=False, indent=2))
        # industry csv
        pd.DataFrame(attr.get("industry_weight_time_share", [])).to_csv(
            OUT / f"b4_{aum // 10000}w_industry_share.csv", index=False
        )
        attrs[str(aum)] = attr
        arm = results.get("B4_50_25_25", {}).get(str(aum))
        if isinstance(arm, dict):  # C r3: missing mandatory sw_pit field -> B4 arm not OK
            arm["sw_pit_required"] = attr.get("sw_pit_required")
            if not sw_pit_required_ok(arm["sw_pit_required"]):
                arm["ok"] = False
                arm["error"] = "sw_pit_required_missing"
        print("smallcap mean_w", attr.get("mean_smallcap_weight_of_book"), "days%", attr.get("pct_days_any_smallcap_holding"))

    charts = make_charts(results, baselines)

    summary = {
        "run_id": "fulla_b4_x2_20261014",
        "live": False,
        "promotion": False,
        "track": "FULLA_V1_RESEARCH",
        "window": list(X2),
        "window_label": "样本内",
        "engine": "quantlab.cli book-smoke --run-nav / ExecConfig.strategy_v1",
        "mix_B4": GROUPS["B4_50_25_25"],
        "concentration": {"N": N_BY_AUM, "single_name_cap": CAP, "excess_to": BAL},
        "sealed": sealed_status(),
        "results": results,
        "baselines": baselines,
        "synth_meta": synth_meta,
        "smallcap_attr": {k: {"mean_smallcap_weight_of_book": v.get("mean_smallcap_weight_of_book"),
                               "pct_days_any_smallcap_holding": v.get("pct_days_any_smallcap_holding"),
                               "n_smallcap_holding_rows": v.get("n_smallcap_holding_rows"),
                               "mean_below_median_mv_weight_of_book": v.get("mean_below_median_mv_weight_of_book"),
                               "top_industries": (v.get("industry_weight_time_share") or [])[:8]}
                          for k, v in attrs.items()},
        "charts": charts,
        "mdd25_flag": {},
        "sw_pit_freshness": sw_l1_table_check_last(_sw_path(sw_path)),  # C r3b: table actually read
        "disclosure_zh": (sw_l1_table_check_last(_sw_path(sw_path)) or {}).get("disclosure_zh", ""),
        "sw_l1_stale_lag_only": bool((sw_l1_table_check_last(_sw_path(sw_path)) or {}).get("stale_lag_only")),
        # C r3 (主 Agent 06:49 ET item 3): mandatory sw_pit fields (sha of the file actually read, unknown, overlap)
        "sw_pit_path": str(_sw_path(sw_path)),
        "sw_pit_required_by_arm": {f"B4_{k}w": v.get("sw_pit_required") for k, v in attrs.items()},
        "note_zh": "FULLA=研究轨；纸面=HI_LIQ（并行）；未动 FROZEN_CONFIG/纸面轨。S6/叶 为影子研究，不晋级。",
    }
    req = summary["sw_pit_required_by_arm"]
    shas = {(v or {}).get("sw_pit_sha256") for v in req.values()}
    summary["sw_pit_sha256"] = next(iter(shas)) if len(shas) == 1 else None  # one table per run, else None (not OK)
    summary["sw_pit_required_ok"] = (bool(req) and summary["sw_pit_sha256"] is not None
                                     and all(sw_pit_required_ok(v) for v in req.values()))
    for tag, by in results.items():
        for aum_s, m in by.items():
            if isinstance(m, dict) and m.get("mdd") is not None:
                summary["mdd25_flag"][f"{tag}_{aum_s}"] = bool(m["mdd"] < -0.25)

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print("WROTE", OUT / "summary.json")
    print("MDD25 flags", summary["mdd25_flag"])
    return 0


def _cli(argv: list) -> int:
    """[--sw-pit-path <file>] (C r3: path parameter; default unchanged)."""
    a, sw_path = list(argv), None
    if "--sw-pit-path" in a:
        i = a.index("--sw-pit-path")
        if i + 1 >= len(a) or a[i + 1].startswith("--"):
            raise SystemExit("usage: --sw-pit-path <file>")
        sw_path = a[i + 1]
        del a[i:i + 2]
    if a:
        raise SystemExit(f"unknown arguments: {a}")
    return main(sw_path=sw_path)


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
