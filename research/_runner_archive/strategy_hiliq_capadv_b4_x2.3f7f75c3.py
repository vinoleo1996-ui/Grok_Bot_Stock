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
import json, subprocess, sys, hashlib, time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
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


def load_industry_map() -> dict:
    ind = pd.read_parquet(
        ROOT / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet",
        columns=["ts_code", "l1_name", "in_date", "out_date"],
    )
    ind["in_date"] = pd.to_datetime(ind["in_date"], errors="coerce")
    # last known name per ts_code (approx PIT; same as FULLA helper)
    last = ind.sort_values("in_date").groupby("ts_code").tail(1)
    return dict(zip(last["ts_code"], last["l1_name"]))


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


def build_topn(mix: dict, aum: int, tag: str, ind_map: dict) -> tuple[pd.DataFrame, dict]:
    used = list(mix)
    D = {k: load_leg(P[k]) for k in used}
    common = sorted(set.intersection(*[set(d["session"]) for d in D.values()]))
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
        agg, ic = apply_ind_cap(agg, ind_map, IND_CAP)
        ind_cut += ic
        # track max industry share after
        stock = {i: v for i, v in agg.items() if not _is_etf(i)}
        sleeve = sum(stock.values())
        if sleeve > 0:
            by_ind: dict[str, float] = {}
            for i, v in stock.items():
                by_ind[ind_map.get(i) or "_UNK_"] = by_ind.get(ind_map.get(i) or "_UNK_", 0.0) + v
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
        mean_510300=float(W[W["instrument"] == BAL].groupby("session")["weight"].sum().reindex(common).fillna(0).mean()),
        stock_names_median=float(stocks.groupby("session").size().median()) if len(stocks) else 0,
    )
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
    with open(log, "w") as f:
        r = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, text=True)
    sp = out_dir / "book_smoke_summary.json"
    if not sp.exists():
        return {"ok": False, "returncode": r.returncode, "log": str(log)}
    return {"ok": True, "returncode": r.returncode, "summary": json.loads(sp.read_text()), "log": str(log)}


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


def smallcap_and_industry(W: pd.DataFrame, tag: str) -> dict:
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
    ind = pd.read_parquet(
        ROOT / "data/v2/sw_pit/industry_members_sw_l1_pit.parquet",
        columns=["ts_code", "l1_name", "in_date"],
    )
    ind["in_date"] = pd.to_datetime(ind["in_date"], errors="coerce")
    last = ind.sort_values("in_date").groupby("ts_code").tail(1)[["ts_code", "l1_name"]]
    m2 = Wx.merge(last, left_on="instrument", right_on="ts_code", how="left")
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
        "note_zh": "行业用申万一级最新归属（近似 PIT）；小盘为逐日截面后30%。",
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


def main():
    t0 = time.time()
    print("=== BANNER: transitional Top-N; main path = OPTIMIZER_V1 DRAFT; FROZEN/paper untouched; live=false ===")
    for k, p in P.items():
        assert p.exists(), f"missing leg {k}: {p}"

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
    ind_map = load_industry_map()
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
        arm["ok"] = True
        b4_results[str(aum)] = arm
        print(f"  B4 {aum}: CAGR={arm.get('cagr')} MDD={arm.get('mdd')} breach={arm.get('mdd25_breach')}")

    # 3) smallcap + industry
    print("=== smallcap + industry ===")
    attrs = {}
    # capacity_adv on X2 slice of pos weights
    Wcap = pd.read_parquet(pos)
    if "session" not in Wcap.columns:
        Wcap["session"] = Wcap["date"].astype(str).str[:10]
    attr_cap = smallcap_and_industry(Wcap, "capadv")
    (OUT / "capadv_x2_smallcap_attr.json").write_text(json.dumps(attr_cap, ensure_ascii=False, indent=2))
    pd.DataFrame(attr_cap.get("industry_weight_time_share", [])).to_csv(OUT / "capadv_x2_industry_share.csv", index=False)
    attrs["capadv"] = attr_cap
    print("capadv smallcap", attr_cap.get("mean_smallcap_weight_of_book"), "focus", attr_cap.get("focus_industries"))

    for aum in (600000, 1000000):
        W = pd.read_parquet(weight_files[("B4_50_25_25", aum)])
        attr = smallcap_and_industry(W, f"B4_{aum // 10000}w")
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
        "alpha_diag_note_zh": "Alpha 诊断 HI_LIQ 60万 18.17%/−24.92%、100万 4.52%/−34.82%（不同窗/引擎）；本回执以 book-smoke 为准",
        "charts": fig_paths + extra,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (OUT / "capadv_x2_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    (B4_OUT / "summary.json").write_text(json.dumps({
        "B4": b4_results, "synth_meta": synth_meta, "banner_zh": summary["banner_zh"],
        "live": False, "promotion": False,
    }, ensure_ascii=False, indent=2))
    print("WROTE", OUT / "capadv_x2_summary.json")
    print("elapsed", summary["elapsed_sec"], "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
