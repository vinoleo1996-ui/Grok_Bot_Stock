#!/usr/bin/env python3
"""Core X2 three-column scorecard (research grade; live=false; promotion=false).

A = OPTIMIZER Core (HI_LIQ) book-smoke NAV: output/strategy_optimizer/core_x2/smoke_<sleeve>_<aum>/nav.csv (fallback book_smoke_*)
B = current capacity_adv mid_large paper-style book-smoke (output/v3/book_smoke_g1g5_capacity_adv_x2, read-only)
C = capacity_adv Top-25 on HI_LIQ_V1.1 (output/strategy_hiliq/capadv_x2, read-only)
Sleeves: equity80_etf20_510300 (PRIMARY) and equity_100. Windows: sealed (disclosure) / X2.
Metrics via quantlab.metrics (244). X2 漂亮数不得晋级.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
QM = None  # quantlab.metrics is imported only AFTER the .ok gate passes (Arch appx C P2-6); see main()

OUT = ROOT / "output/strategy_optimizer/core_x2"
WINDOWS = {"sealed": ("2018-01-02", "2024-05-31"), "X2": ("2024-06-03", "2026-10-09")}
AUMS = (600_000, 1_000_000)
SLEEVES = ("equity80_etf20_510300", "equity_100")
SRC = {"B": ROOT / "output/v3/book_smoke_g1g5_capacity_adv_x2", "C": ROOT / "output/strategy_hiliq/capadv_x2"}
ETF = "sh.510300"
LEDGER = "【HARD 违约账本】"
ARCH12 = OUT / "_archive_v1_2"  # Arch P1-K5: v1.2 book_smoke archived here
GATE_V13 = OUT / "ARCH_RESIGN_A_v1_3.ok"  # Eng 不创建；Arch 复签前 v1.3 A 不算收益、不跑 book_smoke


def read_nav(p: Path) -> pd.Series | None:
    if not p.exists():
        return None
    df = pd.read_csv(p)
    s = pd.Series(df["nav"].astype(float).values, index=pd.to_datetime(df.iloc[:, 0].astype(str).str[:10]))
    return s.sort_index()


def etf_share(p: Path) -> pd.Series | None:
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    d = d[d["instrument_id"] == ETF]
    return pd.Series(d["weight"].values, index=pd.to_datetime(d["session"])).groupby(level=0).sum()


def bench_ret(aum: int, wn: str) -> pd.Series | None:
    for k in ("C", "B"):
        n = read_nav(SRC[k] / f"aum_{aum}" / wn / "C0" / "nav.csv")
        if n is not None:
            return QM.returns(n)
    return None


WB = None
def wb_ret():
    global WB
    if WB is None:
        f = OUT / "bench_hiliq_wb_x2.csv"
        WB = pd.read_csv(f, index_col=0, parse_dates=True)["ret"] if f.exists() else pd.Series(dtype=float)
    return WB


def book_dir(col: str, aum: int, wn: str, sleeve: str) -> Path:
    if col == "A":
        return ARCH12 / f"book_smoke_{sleeve}_{aum // 10000}w" / f"aum_{aum}" / wn / "BOOK"
    if col == "A_v1_3":
        return OUT / f"book_smoke_v1_3_{sleeve}_{aum // 10000}w" / f"aum_{aum}" / wn / "BOOK"
    if sleeve == "equity_100":
        return OUT / "t6_native_eq100" / f"{col}_{aum}" / f"aum_{aum}" / wn / "BOOK"
    return SRC[col] / f"aum_{aum}" / wn / "BOOK"


def turn_cost(d: Path) -> dict:
    o = {}
    try:
        aw = pd.read_parquet(d / "actual_weights.parquet", columns=["session", "instrument_id", "weight"])
        W = aw.pivot_table(index="session", columns="instrument_id", values="weight", aggfunc="sum").fillna(0).sort_index()
        o["turnover_ann_oneway"] = float(0.5 * W.diff().abs().sum(axis=1).iloc[1:].mean() * QM.PERIODS)
    except Exception:
        pass
    try:
        js = json.loads((d / "summary.json").read_text())["metrics"]
        o["cost_pct_initial"] = js.get("cost_pct_initial")
    except Exception:
        pass
    return o


def compute(r: pd.Series, b: pd.Series | None) -> dict:
    nav = QM.nav_from_returns(r)
    nav = pd.concat([pd.Series([1.0], index=[r.index[0] - pd.Timedelta(days=1)]), nav])
    out = QM.summary(nav)
    out.pop("monthly_note", None)
    if b is not None:
        bb = b.reindex(r.index).fillna(0.0)
        a = r - bb
        sd = a.std(ddof=1)
        out["ir_vs_510300"] = float(a.mean() / sd * math.sqrt(QM.PERIODS)) if sd > 1e-12 else None
        out["monthly_beat_510300"] = QM.monthly_win_rate(r, bb, nav_base=nav.index[0]).get("monthly_beat")
    w = wb_ret()
    if len(w):
        a = r - w.reindex(r.index).fillna(0.0); sd = a.std(ddof=1)
        out["ir_vs_wb"] = float(a.mean() / sd * math.sqrt(QM.PERIODS)) if sd > 1e-12 else None
    m = out["mdd"]
    out["mdd_breach_25"] = bool(m is not None and m < -0.25)
    out["mdd_breach_15"] = bool(m is not None and m < -0.15)
    return out


def sleeve_returns(col: str, aum: int, wn: str, sleeve: str, b: pd.Series | None):
    """Return (daily returns, provenance label) or (None, reason)."""
    if col == "A":
        # v1.2 A = 已复签(历史)的 book_smoke 产物，列为【HARD 违约账本】；不再受 marker 门控（v1.2 marker 已退役）
        # T1: accept Strategy convention smoke_* (preferred) and legacy Eng book_smoke_*
        tag = f"{sleeve}_{aum // 10000}w"
        n = None
        for cand in (ARCH12 / f"book_smoke_{tag}" / "nav.csv",):  # P1-K5: v1.2 ledger reads archive only
            n = read_nav(cand)
            if n is not None:
                break
        if n is None:
            return None, "PENDING"
        n = n.loc[WINDOWS[wn][0]:WINDOWS[wn][1]]
        return (QM.returns(n), LEDGER + "native_book_smoke_v1_2") if len(n) > 5 else (None, "PENDING_no_window_rows")
    if col == "A_v1_3":
        if not GATE_V13.exists():
            return None, "PENDING_ARCH_RESIGN(v1.3)"
        n = read_nav(OUT / f"book_smoke_v1_3_{sleeve}_{aum // 10000}w" / "nav.csv")
        if n is None:
            return None, "PENDING_v1_3_book_smoke_not_run"
        n = n.loc[WINDOWS[wn][0]:WINDOWS[wn][1]]
        return (QM.returns(n), "native_book_smoke_v1_3(resigned)") if len(n) > 5 else (None, "N/A_no_window_rows")
    derived = col.endswith("_derived_ref")
    col = col.replace("_derived_ref", "")
    if sleeve == "equity_100" and not derived:
        # T6: native pure-equity book (510300 rows dropped, renormalised to 100%; same engine ExecConfig.strategy_v1, X2 only)
        n = read_nav(OUT / "t6_native_eq100" / f"{col}_{aum}" / "nav.csv")
        if n is None:
            return None, "N/A_no_sealed_run(sealed_refused_by_book_module)" if wn == "sealed" else "MISSING_native"
        n = n.loc[WINDOWS[wn][0]:WINDOWS[wn][1]]
        return (QM.returns(n), "native_equity100_book(510300_dropped_renorm;name_cap_scaled_1/0.8)") if len(n) > 5 else (None, "N/A_no_window_rows")
    base = SRC[col] / f"aum_{aum}" / wn / "BOOK"
    n = read_nav(base / "nav.csv")
    if n is None:
        return None, f"N/A_no_{wn}_run(sealed_refused_by_book_module)" if wn == "sealed" else "MISSING"
    r = QM.returns(n)
    sh = etf_share(base / "actual_weights.parquet")
    sh = (sh.reindex(r.index).ffill().fillna(0.0) if sh is not None else pd.Series(0.0, index=r.index))
    if b is None:
        return None, "NO_BENCH"
    bb = b.reindex(r.index).fillna(0.0)
    eq = ((r - sh * bb) / (1 - sh).clip(lower=0.05))  # pure book ex-510300 (incl. cash)
    if sleeve == "equity_100":
        return eq, f"DERIVED_FROM_80_20_NAV_APPROX(reference_only)_ex510300(mean_etf_share={sh.mean():.3f})"
    if abs(float(sh.mean()) - 0.20) <= 0.02:
        return r, f"native_book_nav(mean_510300_share={sh.mean():.3f}≈20%)"
    # 80/20: rebuild from daily 510300 return on the de-ballasted equity book
    return 0.8 * eq + 0.2 * bb, f"derived_80eq_20x510300_daily(native_etf_share={sh.mean():.3f})"


PIN_RULING_ZH = ("100万档两段连续整手失败：2026-03→06，2026-08→2026-10-09。"
                 "X2 严格可行率 ① 17.2%、② 37.9%，只看硬约束 58.6%。")  # 主 Agent 00:31 ET 裁定原文
ENGINE_OPTIMISM_ZH = ("引擎停牌/退市处理（Arch P2-1 核实后改写，取代 00:49 ET 原标注）：本记分卡三列都用 book_smoke 引擎 "
                      "`quantlab/platform/execution.py`，与 FE.book_ret、LC 引擎不是同一套代码，「缺行情按 0 收益、按最后价卖出」不适用于本表。"
                      "实际机制：停牌当天禁止成交，卖单顺延；复牌时一次性实现全部涨跌；没有退市终值。"
                      "X2 内持有停牌票的事件（名·日）：A 60万 15、A 100万 10、B 10、C 13；持有退市票的事件 0。偏差可以忽略。")
ENGINE_OPTIMISM_SUPERSEDED_ZH = ("（00:49 ET 原标注「持仓股停牌或退市后缺行情按 0 收益记…A、B、C 三列都受影响」经 Arch 核实对 book_smoke 不成立，"
                                 "已按 docs/v2/ARCH_V1_3_SCORECARD_AUDIT_ZH.md P2-1 改写；修复规格 SD1 另行实现，不影响本表。）")
PIN_RULING_VALUES = {"strict_1": 17.2, "strict_2": 37.9, "hard": 58.6}
TIER_WARN_ZH = "可行性不足，收益仅供参考"
NOTES_MANUAL = OUT / "scorecard_notes_manual.md"
MD_PATH = OUT / "scorecard_three_col.md"          # manifest-recorded (5b9250d2…): READ-ONLY, never written
MD_GEN = OUT / "scorecard_three_col.md.gen"       # manifest-recorded: READ-ONLY, never written
CSV_PATH = OUT / "scorecard_three_col.csv"        # manifest-recorded: READ-ONLY, never written
PROTECTED = {MD_PATH.resolve(), MD_GEN.resolve(), CSV_PATH.resolve(), NOTES_MANUAL.resolve()}
# Arch appx C P2-7: static closure of `from quantlab import metrics` (+ lazy trade_calendar → quantlab.portfolio package).
# Traced from import statements only (rg), not executed. Eager: quantlab/__init__, metrics; on first metrics calendar call:
# portfolio/__init__ → v2_constructor → mandate_v2 → promotion_gate, config; v2_rebalance; trade_calendar.
# Function-level (lazy) inside v2_constructor: config, strategy/__init__ → scoring, portfolio, risk.
SCORECARD_QUANTLAB_DEPS = {
    "quantlab_init": ROOT / "quantlab/__init__.py",
    "portfolio_init": ROOT / "quantlab/portfolio/__init__.py",
    "v2_constructor": ROOT / "quantlab/portfolio/v2_constructor.py",
    "v2_rebalance": ROOT / "quantlab/portfolio/v2_rebalance.py",
    "mandate_v2": ROOT / "quantlab/mandate_v2.py",
    "promotion_gate": ROOT / "quantlab/promotion_gate.py",
    "quantlab_config": ROOT / "quantlab/config.py",
    "strategy_init": ROOT / "quantlab/strategy/__init__.py",
    "strategy_scoring": ROOT / "quantlab/strategy/scoring.py",
    "strategy_portfolio": ROOT / "quantlab/strategy/portfolio.py",
    "strategy_risk": ROOT / "quantlab/strategy/risk.py",
}
AUDITFIX_OK = OUT / "ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok"   # dedicated pin .ok (Arch review 4698a2c1 §8); Eng never creates it


def out_paths(tag: str):
    """--out-tag TAG → scorecard_three_col_TAG.md / .md.gen (/ .csv for a full run). Refuses protected or existing targets."""
    import re
    if not tag or not re.fullmatch(r"[A-Za-z0-9_]+", tag):
        raise SystemExit("REFUSED: --out-tag TAG is required ([A-Za-z0-9_]+), e.g. --out-tag auditfix_20261018_<runner sha8>")
    md, gen, csv = (OUT / f"scorecard_three_col_{tag}.md", OUT / f"scorecard_three_col_{tag}.md.gen", OUT / f"scorecard_three_col_{tag}.csv")
    for q in (md, gen, csv):
        if q.resolve() in PROTECTED:
            raise SystemExit(f"REFUSED: {q} is manifest-recorded / protected")
        if q.exists():
            raise SystemExit(f"REFUSED: {q} already exists; use a new --out-tag")
    return md, gen, csv


def _feas() -> tuple[pd.DataFrame | None, dict]:
    p = OUT / "c5_feasibility_v1_3.csv"; sp = OUT / "c5_weight_stamp_v1_3.json"
    F = pd.read_csv(p) if p.exists() else None
    st = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    if F is not None and "kind" not in F.columns:
        F = None  # pre-alignment schema; rerun scripts_eng/core_c5_rereport.py
    return F, st


def pinned_block() -> list[str]:
    """主 Agent 00:31 ET 裁定：记分卡头部置顶披露（每次生成都渲染）。数值取自当前 c5_feasibility_v1_3.csv。"""
    F, st = _feas()
    L = ["## 📌 置顶披露（主 Agent 2026-10-18 00:31 / 00:49 ET 裁定）", "",
         "> ⚠️ **" + ENGINE_OPTIMISM_ZH + "**", "> " + ENGINE_OPTIMISM_SUPERSEDED_ZH, ""]
    vals, runs, src = dict(PIN_RULING_VALUES), None, "裁定原文数值"
    if F is not None:
        x = F[(F.window == "X2") & (F.aum == 1_000_000)]
        g = lambda sv, c: float(x[x.sleeve == sv][c].iloc[0]) if len(x[x.sleeve == sv]) else None
        vals = {"strict_1": g("equity_100", "strict_pct"), "strict_2": g("equity80_etf20_510300", "strict_pct"), "hard": g("tier_dedup(both)", "hard_pct")}
        runs = str(x.hard_runs_ge2_from_X2.iloc[0]) if "hard_runs_ge2_from_X2" in x.columns and len(x) else None
        src = "当前权重计算"
    void = bool(st.get("void_pre_K6"))
    fp = "；".join(f"{n.replace('.parquet','')} sha256={i.get('sha256','')[:12]}…" for n, i in (st.get("files") or {}).items() if not i.get("missing"))
    txt = (f"100万档两段连续整手失败：2026-03→06，2026-08→2026-10-09。"
           f"X2 严格可行率 ① {vals['strict_1']:.1f}%、② {vals['strict_2']:.1f}%，只看硬约束 {vals['hard']:.1f}%。")
    L.append(f"1. **{txt}**")
    if F is None or void:
        L.append("   - 数值注：来自 **pre-K6 作废版本**（`_archive_v1_3_pre_ruling`）口径/裁定原文；新 v1.3 权重落盘后由生成器自动改填。")
    else:
        L.append(f"   - 数值注：由生成器从**现行 v1.3 权重（K6 后授权重跑，全池 wb 行业口径）**计算（{src}；{fp}）。"
                 f"严格 = HARD 可行 且 cash≤2%；只看硬约束 = HARD-only；分母剔除 2018-01-02 首日；按档×口径（硬约束两口径相同）。")
    same = all(abs((vals[k] or -1) - PIN_RULING_VALUES[k]) < 0.05 for k in vals)
    L.append(f"   - 与裁定原文数值（① 17.2% / ② 37.9% / 硬约束 58.6%）{'一致' if same else '**不一致**，以上为重算值，待 主 Agent/Strategy 确认'}。")
    if runs:
        L.append(f"   - 生成器核对：X2 内连续 ≥2 个调仓日 HARD 失败（全部 LOT_HARD_FAIL）的区段 = {runs.replace(' ', '、')}"
                 + ("；其中 2025-06→2025-07 一段长度为 2（<k=3），**已确认**（Strategy 10-18 裁定、Arch P2-5）不进置顶「两段连续失败」，列于下一行。" if "2025-06" in runs else "。"))
    L.append("   - 100万 X2 另有长度 2 的失败段（含 2025-06→07），按 Beta M6 全列于停跑规则 §7")
    L += [f"2. **100万列：{TIER_WARN_ZH}。**（下方所有 100万 行/表头均带此标签）", ""]
    return L


def manual_notes() -> list[str]:
    if not NOTES_MANUAL.exists():
        return []
    body = [l for l in NOTES_MANUAL.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("<!--")]
    if not body:
        return []
    return ["## 手工备注（`core_x2/scorecard_notes_manual.md`，生成器原样收录）", "", *body,
            "- （生成器注：v1.3 可行率表现已改读 K6 后授权重跑权重；上条 Strategy 注中「出自 pre-ruling 运行」一句为其写入时状态，原文保留。）"
            if any("pre-ruling" in l for l in body) else "", ""]


def harvest_manual_edits() -> list[str]:
    """Lines present in the current md but absent from the last generated text = manual edits → append to sidecar."""
    if not (MD_PATH.exists() and MD_GEN.exists()):
        return []
    gen = set(MD_GEN.read_text(encoding="utf-8").splitlines())
    side = set(NOTES_MANUAL.read_text(encoding="utf-8").splitlines()) if NOTES_MANUAL.exists() else set()
    new = [l for l in MD_PATH.read_text(encoding="utf-8").splitlines() if l.strip() and l not in gen and l not in side]
    # READ-ONLY since 2026-10-18 (Arch review 4698a2c1 P1-2): never append to scorecard_notes_manual.md; only report.
    return new


def tier_label(aum) -> str:
    return f"{aum}（{TIER_WARN_ZH}）" if int(aum) == 1_000_000 else str(aum)


def feasibility_v13() -> list[str]:
    """v1.3 K2: HARD-only (official) vs STRICT per tier × sleeve (+ tier-dedup reference); cash dist; cash drag (gated).
    Reads c5_feasibility_v1_3.csv from scripts_eng/core_c5_rereport.py (definitions = scripts_eng/core_feas_defs.py,
    aligned with research/optimizer_core_v1_3_stats.py)."""
    F, stamp = _feas()
    if F is None:
        return ["## v1.3 可行率（K2）", "", "c5_feasibility_v1_3.csv 缺失或为旧口径（先跑 scripts_eng/core_c5_rereport.py v1_3）。", ""]
    void = bool(stamp.get("void_pre_K6"))
    fp = [f"{n[:28]}… sha256={i.get('sha256','')[:12]}… mtime={i.get('mtime_et','')}" for n, i in (stamp.get("files") or {}).items() if not i.get("missing")]
    L = ["## v1.3 可行率（K2 HARD-only / STRICT；按资金档×口径，另列档去重参考；λ/参数未动）", "",
         f"**权重指纹**：{'；'.join(fp) if fp else '（无）'}",
         f"**版本标签**：{'作废版本（K6 前），待 Strategy 重跑' if void else stamp.get('label', '')}",
         f"**与 Strategy core_v1_3_stats.json 交叉核对**：{F.stats_crosscheck.iloc[0] if 'stats_crosscheck' in F.columns else '未核对'}", "",
         "| window | aum | 口径 | n(剔除首日) | HARD-only(K2官方) | 严格(HARD 且 现金≤2%) | HARD 可行但现金>2% | 现金 p5/p50/p95/max(档) | 现金>2%占比(档) | 现金拖累(年化pp) |",
         "|" + "---|" * 10]
    for r in F.itertuples():
        drag = r.cash_drag_ann_pp
        try:
            drag = f"{float(drag):.3f}pp"
        except (TypeError, ValueError):
            drag = str(drag)
        L.append(f"| {r.window} | {tier_label(r.aum)} | {r.tag} {r.sleeve} | {r.n_eval} | {r.n_hard}/{r.n_eval}={r.hard_pct}% | {r.n_strict}/{r.n_eval}={r.strict_pct}% | "
                 f"{r.cash_gt2_hard_rows} | {r.cash_p5:.3f}/{r.cash_p50:.3f}/{r.cash_p95:.3f}/{r.cash_max:.3f} | {r.cash_gt2_share:.1%} | {drag} |")
    L += ["",
          "- **定义（对齐 Strategy `research/optimizer_core_v1_3_stats.py`）**：HARD-only = status∈{OK, LOT_CASH_GT2}；严格 = HARD 可行 且 cash≤2%（≡ status==OK）；"
          "分母**剔除** 2018-01-02 NO_DATA_CARRY 首日；主单位 = 资金档×口径，「档去重」行（同日两口径都过才算过）仅作参考。",
          "- **K2**：风格 / β / 行业为 HARD，优先于现金≤2%；现金超标只披露、不判失败。**K6**：行业偏离按全池 wb；指纹命中 `_void_pre_K6_sha.json` 则整段为作废版本。",
          "- 现金分布取整手后权重（调仓日、档内两口径取 max、剔除首日）。现金拖累 = Σ max(cash−0.02,0)×同日池内 wb 收益，年化 pp（×244）；**仅当** `ARCH_RESIGN_A_v1_3.ok` 存在时计算，否则 PENDING（待放行标记）。Eng 不创建该标记。",
          "- 旧文件 `c5_rereport_v1_3_strict.txt` 把 HARD-only 误标为 strict，已标 SUPERSEDED；pre-K6 交叉核对见 `c5_rereport_v1_3_hard_strict_VOID_pre_K6_crosscheck.txt`。", ""]
    return L


def feasibility_section() -> list[str]:
    """可行性披露（v1.2，取自 core_v1_2_disclosure.csv）；仅披露，不调参（Arch 裁定）。"""
    p = ARCH12 / "core_v1_2_disclosure.csv"
    if not p.exists():
        return ["## 可行性披露", "", "core_v1_2_disclosure.csv 缺失。", ""]
    D = pd.read_csv(p); D["m"] = D.date.str[:7]
    D["cls"] = np.where(D.status.isin(["OK", "LOT_CASH_GT2"]), "OK",
                np.where(D.stage.eq("lot"), "LOT_HARD_FAIL", np.where(D.stage.eq("step2"), "step2", "other")))
    L = ["## 可行性披露（v1.2；**【已被 v1.3 取代】**；λ 冻结 risk=117.213 / turn=0.6；未调参、未改 HARD）", "",
         "> 本节为 v1.2 历史口径（入选名单 wb 行业、无一手剔除），**已被上方 v1.3 可行率取代**（Arch P2-4）；其中「100万档 X2 全部可行 / 100%」不再成立，现行 v1.3 100万 X2 见置顶披露。", "",
         "| window | aum | sleeve | 调仓日 | OK | step2 | LOT_HARD_FAIL | other | 可行率 | 单月≥2天 | 连续不可行月 |", "|" + "---|" * 11]
    for (w, a, sv), g in D.groupby(["window", "aum", "sleeve"]):
        inf = g[g.cls != "OK"]; mc = inf.m.value_counts(); ms = sorted(set(inf.m)); runs, cur = [], []
        for m in ms:
            if cur and (pd.Period(m) - pd.Period(cur[-1])).n == 1: cur.append(m)
            else:
                if len(cur) > 1: runs.append(f"{cur[0]}→{cur[-1]}")
                cur = [m]
        if len(cur) > 1: runs.append(f"{cur[0]}→{cur[-1]}")
        c = inf.cls.value_counts()
        L.append(f"| {w} | {a} | {sv} | {len(g)} | {(g.cls=='OK').sum()} | {c.get('step2',0)} | {c.get('LOT_HARD_FAIL',0)} | {c.get('other',0)} | {(g.cls=='OK').mean():.1%} | {','.join(mc[mc>=2].index) or '无'} | {','.join(runs) or '无'} |")
    L += ["", "- other = 2018-01-02 首日 NO_DATA_CARRY（空仓起始）。不可行日一律沿用上期持仓（禁止回退 step1）。",
          "- **60万档结构性限制**：X2 内 2026-04/06/09 三个调仓日口径② 整手后仅 19 只（<20）→ LOT_HARD_FAIL；2026-07 step2 不可行；形成 2026-06→2026-07 连续不可行月。"
          "原因是小资金 + 6% 单票上限 + 100/200 股整手的结构性约束，**仅披露、不调参**（Arch 裁定）。100万档 X2 全部可行（v1.2 口径，已被 v1.3 取代）。",
          "- ① 不可行日（按 AUM 档去重；一口径失败两口径同沿用上期）：60万 SEALED 2019-12-31(step2)；100万 SEALED 2019-10-31(step2)；两档 2018-01-02 首日 NO_DATA；"
          "60万 X2 2026-04-30/06-30/09-30 LOT_HARD_FAIL（口径②触发，整手后 19 只）+ 2026-07-31 step2。**60万档 2026-04→2026-09 六次调仓中 4 次不可行**，属小资金整手结构性问题，未调参。",
          "- ② 漂移分布（disclosure，可行日 post-lot）：β drift p5/p50/p95 ≈ −0.10~−0.14 / +0.03~+0.05 / +0.07~+0.10，min −0.34；MidCap drift p5/p50/p95 ≈ −0.49~−0.53 / −0.18~−0.28 / +0.13~+0.27，min −0.93。"
          "超界>0.05（|β|>0.15 或 |MidCap|>0.35+slack+0.05）共 54 行（档×口径×日），集中在 2025-07 起 X2，尤其 2026-07→10-09（β −0.16~−0.34、MidCap −0.35~−0.93）；明细见 core_v1_2_disclosure.csv（c1_*_breach / LOT_STYLE_DRIFT）。",
          "- ③ slack 顶格：100万档可行日 52.4%（SEALED 52.6% / X2 48.3%）；60万档 29.7%。已由 disclosure 复核。",
          "- X2 仅为入场券，不作晋级依据（晋级看 2026-11-02 起 FWD）；密封窗仅披露，book 模块拒跑密封窗，故无密封业绩。",
          "- **A 列 v1.2 X2 = 【HARD 违约账本】，不作结论**：β/MidCap 超界（上条②）+ 60万档整手失败（上条①），v1.2 未满足冻结 HARD；业绩行仅作违约账本留档。Core 已按 Arch/主 Agent 裁定开 v1.3（求解前剔除一手金额 > name_cap×AUM 的股票再重解，λ/参数不动）。",
          "- **【HARD 违约账本】K6 行业补注（Arch，固定注）**：全池 wb 复核，60万 6–7 、100万 4–5 个档日行业越界，最大 −12.54pp（2026-08-31 电子）。（v1.2 行业约束按支撑集 wb；档日含沿用日；出处 `docs/v2/audit/ARCH_K6_INDUSTRY_FULLPOOL_DISCLOSURE_V0_V1_2_ZH.md`）",
          f"- **v1.3 A 列**：门控 = core_x2/ARCH_RESIGN_A_v1_3.ok，读 book_smoke_v1_3_*/nav.csv（当前{'存在' if GATE_V13.exists() else '不存在'}）；Arch 复签前不算收益、不跑 book_smoke。v1.2 marker 已改名 ARCH_RESIGN_A_v1_2.ok.retired_v1_3。",
          "- **换手口径注**：本表 turnover_ann_oneway = 日度实际权重差（单边）×244，含价格漂移，**与 λ 标定口径（每调仓日优化器单边换手）不可比**。实测每调仓日单边换手 0.38–0.40，标定目标 0.25；仅披露，λ 未重标定。",
          "- IR 主基准为 HI_LIQ 自由流通市值加权 wb（bench_hiliq_wb_x2.csv，已与求解器 wb 口径对齐：≥40 日收益史、去 5 日 carry；旧版存 bench_hiliq_wb_x2_v0.csv），510300 为次基准。", ""]
    return L


RESIGN_DOC = ROOT / "docs/v2/ARCH_OPTIMIZER_CORE_v1_3_RESIGN_ZH.md"


def _overcap_counts() -> dict:
    """40% one-way cap (monitor only): solver one_way_opt > 0.40 on HARD-feasible days (per AUM; first day has no turnover)."""
    D = pd.read_csv(OUT / "core_v1_3_disclosure.csv"); o = {}
    for a in AUMS:
        x = D[(D.aum == a) & (D.sleeve == "equity_100") & D.status.isin(["OK", "LOT_CASH_GT2"])]
        x2 = x[x.window == "X2"]  # denominator = all HARD-feasible rows (Arch P2-3); rows without one_way_opt count as not over cap
        o[a] = (int((x.one_way_opt > 0.40).sum()), len(x), int((x2.one_way_opt > 0.40).sum()), len(x2))
    return o


def release_conditions() -> list[str]:
    """ARCH_RESIGN_A_v1_3.ok 放行条件（主 Agent 00:46 ET 裁定）逐条披露。"""
    if not GATE_V13.exists():
        return []
    import hashlib
    okt = GATE_V13.read_text(encoding="utf-8"); oksha = hashlib.sha256(GATE_V13.read_bytes()).hexdigest()
    oc = _overcap_counts()
    exp = {600_000: (28, 96), 1_000_000: (18, 81)}  # Arch P2-3 (分母=可行行 96/81；主 Agent 裁定原文 95/80 由 Arch 另行更正)
    chk = "；".join(f"{a // 10000}万 {oc[a][0]}/{oc[a][1]}（X2 {oc[a][2]}/{oc[a][3]}）" + ("" if oc[a][:2] == exp[a] else f" ≠ Arch 复算 {exp[a][0]}/{exp[a][1]}") for a in AUMS)
    L = [f"## 放行条件披露（`ARCH_RESIGN_A_v1_3.ok` sha256={oksha[:8]}…，主 Agent 2026-10-18 00:46 ET 裁定；`{RESIGN_DOC.relative_to(ROOT)}`）", "",
         "1. **判定口径 = A**（代码口径：510300 记为基准暴露）。A 在口径②上实际把风格/β 界放宽到 1/0.8 倍。B、C 口径下的越界行数并列如下（取自 Arch 复签 §3，可行行：60万 96、100万 81）：", "",
         "   | 口径 | 60万 ② | 60万 ① | 100万 ② | 100万 ① | 采用后翻成不可行的档日（全样本 / X2） |", "   |---|---|---|---|---|---|",
         "   | A 代码口径（判定） | 0 | 0 | 0 | 0 | 0 |",
         "   | B 股票部分归一 | 52 | 46 | 56 | 60 | 60万 60 / 15；100万 64 / 12 |",
         "   | C 股票袖按预算归一 | 27 | 0 | 18 | 0 | 60万 27 / 10；100万 18 / 5 |", "",
         "2. **按 A 通过只算入场券**；任何晋级讨论之前，必须在 v1.4 用口径 C 复现。",
         f"3. **40% 单边换手硬帽只作监控**。冻结规格 PREREG_FROZEN §3.7 写的是 HARD「≤40% NAV/再平衡」，代码 `TURN_HARD_CAP=0.40` 却是 soft monitor，**规格与代码不一致**。超帽天数（求解权重；分母 = 可行行，与上条「可行行 60万 96、100万 81」一致，Arch P2-3）：{chk}；.ok/裁定原文写的 28/95、18/80 分母差 1（首日无换手行），Arch 另行更正。"
         "**分母差异原因（Arch appx C P3）**：冻结 RESIGN .ok 第 16 行写 `60w_28/95_100w_18/80`，本表 28/96、18/81，分子一致。"
         "原因：两档首个 HARD 可行行都是 **2018-01-31**（60万 OK、100万 LOT_CASH_GT2），这一行没有前一期权重，`one_way_opt` 为空。"
         "只数有换手值的行（dropna）得 95/80；按 Arch P2-3 数全部可行行得 96/81。"
         "2018-01-02 是 NO_DATA_CARRY，不是可行行，两种口径都不计。复算脚本 `scripts_eng/overcap_recount_v1_3.py` 两种分母都原样输出。",
         "4. **00:30–00:44 ET 的 VOID 干跑 / smoke 数字作废，不得引用**（pre-K6 权重、无 Arch .ok；见 `s2_3_v1_3_VOID_dryrun_*/VOID.md`）。",
         "5. S2-3「无带 / 有带」两列并列见下节，**头条取无带列**，有带只作消融。", ""]
    return L


def s2_3_section() -> list[str]:
    rel = OUT / "ARCH_S2_3_RELEASE.ok"
    fs = sorted(OUT.glob("s2_3_v1_3_equity*/exec_metrics.json"))
    if not fs:
        return ["## S2-3 执行层（无带 / 有带）", "", "未运行（需 ARCH_S2_3_RELEASE.ok）。", ""]
    import hashlib
    L = [f"## S2-3 执行层 X2（头条 = 无带；有带只作消融；`ARCH_S2_3_RELEASE.ok` sha256={hashlib.sha256(rel.read_bytes()).hexdigest()[:8]}…）", "",
         "> ✅ **已解除 VOID（第 00:48 前版本为重建件，仅循环验证）**：运行代码 `scripts_eng/s2_3_exec_layer.py` 在放行 .ok（00:47:18 ET）之后于 00:48:19 ET 被改，sha 未钉（Arch P1-1）；"
         "实际运行代码 sha256=3d4b08e31973ad58254714fdfdf699290d7995da4c9461bd48ea13df9d5b2bf4，diff 见 `docs/v2/eng_s2_3/`。Arch 审 diff：只改输入守卫和 meta，不改变 S2-3 数字；"
         "主 Agent 2026-10-18 解除 VOID_PENDING_DIFF。00:48 前版本是由运行版反推的重建件，patch 逐位还原只是循环验证，不能独立证明 00:47:18 ET 的真实状态。"
         "**门槛结论不变：四条无带中位数均 >0.30，S2-3 门槛 FAIL**（预登记预期，未调参）。", "",
         "门槛：X2 有成交调仓日的实际单边换手 TO_d 中位数 ≤0.30（事前登记预计 FAIL，不调参）。整手 = Core v1.3 `lot_round_greedy`（两列相同）；现金偏高只披露，不撤销带。", "",
         "| aum | 口径 | 列 | 调仓/沿用/成交 | **TO_d 中位** | 门槛 ≤0.30 | P3 零成交天数 / 含零中位 | 全调仓日中位 | 年化单边 | 目标对目标中位 | 撤销带天数（原因） | 冻结笔数 | HARD 复核失败 | >40% 天数 | 现金 p50/max | 成本/初始 AUM |",
         "|" + "---|" * 16]
    for f in fs:
        J = json.loads(f.read_text(encoding="utf-8")); m = J["meta"]
        for c in ("nobuf_HEADLINE", "buf_ABLATION"):
            x = J["metrics"][c]["X2"]
            L.append(f"| {tier_label(m['aum'])} | {SLEEVE_TAG_ZH.get(m['sleeve'], m['sleeve'])} | {'**无带（头条）**' if c.startswith('nobuf') else '有带（消融）'} | "
                     f"{x['n_rebal_days']}/{x['n_carry_days']}/{x['n_traded_days']} | **{x['gate_TO_median_traded_days']}** | {'PASS' if x['gate_pass_le_0.30'] else 'FAIL'} | "
                     f"{x['archP3_days_fully_suppressed_zero_trades']} / {x['archP3_median_incl_suppressed_as_0']} | {x['B5_median_all_rebal_days_carry_as_0']} | {x['B5_annual_oneway_sum']} | "
                     f"{x['tt_target_turnover_median_stocknorm']} | {x['B5_band_disable_days']}（{', '.join(f'{k} {v}' for k, v in x['B5_band_disable_reasons'].items()) or '—'}） | "
                     f"{x['band_frozen_orders']} | {x['hard_recheck_fail_days']} | {len(x['days_onew_nav_gt_0.40_cap'])} | {x['cash_post']['p50']:.3f}/{x['cash_post']['max']:.3f} | {x['fill_cost_pct_initial_aum']}% |")
    L += ["", "- B5：追补换手、冻结后 <2% 只数、撤销日期见各目录 exec_metrics.json；B4 510300 滚动 β 未运行（已知缺口）。不出任何收益。", ""]
    return L


SLEEVE_TAG_ZH = {"equity_100": "① 纯股票", "equity80_etf20_510300": "② 80/20"}

BC_BOOKS = {"B": ROOT / "output/v3/book_smoke_g1g5_capacity_adv_x2", "C": ROOT / "output/strategy_hiliq/capadv_x2"}


def audit_disclosures() -> list[str]:
    """Arch v1.3 scorecard audit (docs/v2/ARCH_V1_3_SCORECARD_AUDIT_ZH.md) P1-2, P2-2, P2-6, P2-7. Read-only text; numbers read from book summaries."""
    L = ["## 审计补充披露（Arch v1.3 记分卡审计 P1-2 / P2-2 / P2-6 / P2-7）", "",
         "**P1-2 执行层（X2，BOOK，读各 book summary.json；不重跑）**", "",
         "| 列 | aum | 成交率 | 平均闲置现金 | 平均总敞口 | 交易过只数 |", "|---|---|---|---|---|---|"]
    for c, d in BC_BOOKS.items():
        for a in AUMS:
            f = d / f"aum_{a}/X2/BOOK/summary.json"
            if not f.exists():
                L.append(f"| {c} | {tier_label(a)} | 缺失 | | | |"); continue
            m = json.loads(f.read_text(encoding="utf-8"))["metrics"]
            L.append(f"| {c} | {tier_label(a)} | {m['fill_ratio']:.3f} | {m['idle_cash_mean']:.1%} | {m['gross_exposure_mean']:.2f} | {m['n_codes']} |")
    L += ["", "- C 列成交率低、闲置现金高：原因拆解见 `core_x2/c_col_exec_diagnostic.md`（只读诊断，待 Arch .ok 后运行；未出前不作归因结论）。",
          "- **三列不可比之处**：① A 是月度调仓，B、C 是日度目标；② B 用 top300 静态锚（mid_large），A、C 用 HI_LIQ_V1.1 池；"
          "③ B、C 的引擎代码 sha 没有钉（见下 P2-7）；④ C 的执行层（成交率/闲置现金）明显差于 A、B，C 列收益含大量未投资现金的影响。", "",
          "**P2-2 月胜率口径**：本表月胜率 = 完整自然月（`quantlab.metrics.monthly_returns(complete_only=True)`），X2 计 28 个月："
          "2024-06 以 X2 首日 2024-06-03（当月首个交易日）为 NAV 基点，算完整月计入；2026-10 只到 10-09，不完整，剔除。"
          "Arch 复算按 29 个月（含 2024-06、2026-10 两个不完整月）。两种口径并存，本表取 28 个月口径。", "",
          "**P2-6 A 列 100万档的 sh.511880**：来源是 book 层现金停泊，不是优化器权重。`quantlab/portfolio/v2_multisleeve_book.py` 第 34 行 `CASH_ETF = \"sh.511880\"`，"
          "第 459–460 行把未投资预算（1 − cash_target − 投资额，含整手后剩余现金）停到 511880；行情取自 `data/v2/etf/etf_daily_adj.parquet`（ETF 读取器，第 76 行），"
          "不经股票读取器，所以 Arch 的股票面板事件计数没有覆盖它。",
          "", "**P2-7 B、C 引擎代码与运行时间**：两列都是 `run_weight_schedule + ExecConfig.strategy_v1`（`quantlab/platform/execution.py`）。"
          "B run_id=book_smoke_20261013_111418（2026-10-13 11:14:18 ET），C run_id=book_smoke_20261014_200345（run.log 首行 2026-10-14 20:03:46 ET）。"
          "两次运行**都没有记录引擎代码 sha**，无法事后钉住；现行 execution.py sha 只能作参考，不能证明与当时一致。属已知缺口，B、C 重跑时须按 ok_runner_pin 钉 sha。", ""]
    return L


def headline_table(df: pd.DataFrame) -> list[str]:
    """X2 主对比：口径②，A(v1.3) / B / C，60万 / 100万；244 天年化。"""
    x = df[(df.window == "X2") & (df.sleeve == "equity80_etf20_510300") & df.col.isin(["A_v1_3", "B", "C"])]
    if x.empty or x[x.col == "A_v1_3"].cagr.isna().all():
        return []
    name = {"A_v1_3": "A Core v1.3", "B": "B 现行 capacity_adv", "C": "C capadv Top-25@HI_LIQ"}
    f = lambda v, p=True: ("" if pd.isna(v) else (f"{v:.1%}" if p else f"{v:.2f}"))
    L = ["## 头条：X2 口径②（80/20 510300）三列（年化 244 天；研究级，X2 只作入场门槛）", "",
         "| aum | 列 | CAGR | MDD | Calmar | Sharpe | 日胜率 | 月胜率 | MDD 破 25% | MDD 破 15% |", "|---|---|---|---|---|---|---|---|---|---|"]
    for a in AUMS:
        for c in ("A_v1_3", "B", "C"):
            r = x[(x.aum == a) & (x.col == c)]
            if r.empty: continue
            r = r.iloc[0]
            L.append(f"| {tier_label(a)} | {name[c]} | {f(r.cagr)} | {f(r.mdd)} | {f(r.calmar, False)} | {f(r.sharpe, False)} | {f(r.daily_win)} | {f(r.monthly_win)} | "
                     f"{'是' if r.mdd_breach_25 is True or r.mdd_breach_25 == 'True' else '否'} | {'是' if r.mdd_breach_15 is True or r.mdd_breach_15 == 'True' else '否'} |")
    L.append("")
    return L


def perf_table(df: pd.DataFrame, keep: list[str]) -> list[str]:
    fmt = df.reindex(columns=keep).copy()
    for c in ("cagr", "mdd", "daily_win", "monthly_win", "cost_pct_initial"):
        fmt[c] = fmt[c].map(lambda x: f"{x:.1%}" if pd.notna(x) else "")
    for c in ("calmar", "sharpe", "ir_vs_wb", "ir_vs_510300", "turnover_ann_oneway"):
        fmt[c] = fmt[c].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    L = ["## 三列业绩", ""]
    for aum in AUMS:
        sub = fmt[fmt.aum == aum]
        L += [f"### {aum // 10000}万" + (f"【{TIER_WARN_ZH}】" if aum == 1_000_000 else ""), "",
              "| " + " | ".join(("aum（" + TIER_WARN_ZH + "）") if (c == "aum" and aum == 1_000_000) else c for c in keep) + " |", "|" + "---|" * len(keep)]
        for _, r in sub.iterrows():
            L.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r.values) + " |")
        L.append("")
    return L


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--disclosure-only", action="store_true"); ap.add_argument("--out-tag", required=True)
    a = ap.parse_args()
    disclosure_only = a.disclosure_only
    md_out, gen_out, csv_out = out_paths(a.out_tag)
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import ok_runner_pin
    # Arch appx C P1-3: --out-tag must end with _<first 8 hex of this runner's own sha256>, computed at runtime
    self_sha = ok_runner_pin.sha256_file(__file__)
    if not a.out_tag.endswith("_" + self_sha[:8]):
        raise SystemExit(f"REFUSED: --out-tag {a.out_tag!r} must end with '_{self_sha[:8]}' (runner sha256 {self_sha})")
    ok_runner_pin.enforce(__file__, [GATE_V13, OUT / "ARCH_S2_3_RELEASE.ok", AUDITFIX_OK],
                          modes=["disclosure_only"] if disclosure_only else ["full"],
                          deps={"quantlab_metrics": ROOT / "quantlab/metrics.py",
                                "trade_calendar": ROOT / "quantlab/portfolio/trade_calendar.py",
                                "ok_runner_pin": Path(ok_runner_pin.__file__),
                                **SCORECARD_QUANTLAB_DEPS})
    global QM
    from quantlab import metrics as QM  # noqa: E402  (only after the gate passed)
    keep = ["window", "aum", "sleeve", "col", "cagr", "mdd", "calmar", "sharpe", "ir_vs_wb", "ir_vs_510300", "turnover_ann_oneway", "cost_pct_initial", "daily_win",
            "monthly_win", "mdd_breach_25", "mdd_breach_15", "provenance"]
    if disclosure_only:
        # no return computation: re-render header/pinned/disclosure sections; performance table re-read from the existing csv as-is
        df = pd.read_csv(CSV_PATH)
        print("disclosure-only: no returns computed; performance rows re-read from scorecard_three_col.csv")
    else:
        rows = []
        for wn in WINDOWS:
            for aum in AUMS:
                b = bench_ret(aum, wn)
                for sleeve in SLEEVES:
                    cols = ("A", "A_v1_3", "B", "C") + (("B_derived_ref", "C_derived_ref") if sleeve == "equity_100" else ())
                    for col in cols:
                        r, prov = sleeve_returns(col, aum, wn, sleeve, b)
                        row = dict(window=wn, aum=aum, sleeve=sleeve, primary=(sleeve == SLEEVES[0]), col=col, provenance=prov)
                        if r is not None and len(r) > 5:
                            row.update(compute(r, b))
                            if not col.endswith("_derived_ref"):
                                row.update(turn_cost(book_dir(col, aum, wn, sleeve)))
                        rows.append(row)
        df = pd.DataFrame(rows)
        OUT.mkdir(parents=True, exist_ok=True)
        with open(csv_out, "x", encoding="utf-8", newline="") as fh:  # Arch appx C P2-5: exclusive create
            df.to_csv(fh, index=False)
    harvested = harvest_manual_edits()
    if harvested:
        print(f"WARNING: {len(harvested)} line(s) in scorecard_three_col.md are not in .gen or {NOTES_MANUAL.name}; NOT harvested (read-only)")
    elif not MD_GEN.exists():
        print(f"note: {MD_GEN.name} absent (first run of the preserving generator); manual lines must already be in {NOTES_MANUAL.name}")
    md = ["# Core X2 三列记分卡（研究级；live=false；X2 漂亮数不得晋级）", "",
          *pinned_block(),
          *release_conditions(),
          *headline_table(df),
          *s2_3_section(),
          *audit_disclosures(),
          *manual_notes(),
          "A=OPTIMIZER Core(HI_LIQ) · B=现行 capacity_adv mid_large · C=capacity_adv Top-25@HI_LIQ_V1.1；主口径=equity80_etf20_510300；年化 244（quantlab.metrics）；MDD 对 25%/15% 双线标记。", "",
          "**口径注（Arch P2-T6）**：equity_100 行 B/C = 原生纯股票 book（去 510300 行后按日归一至 100%，同引擎 strategy_v1，仅 X2；单票上限随之放大 1/0.8）；`*_derived_ref` 行 = 由 80/20 净值反推 `(r−sh·r510300)/(1−sh)`，**近似值，仅作参考**。", "",
          *feasibility_v13(),
          *feasibility_section(),
          *perf_table(df, keep)]
    md.append(f"<!-- out_tag={a.out_tag} runner_sha256={self_sha} mode={'disclosure_only' if disclosure_only else 'full'} live=false promotion=false -->")
    text = "\n".join(md) + "\n"
    for dst in (md_out, gen_out):
        with open(dst, "x", encoding="utf-8") as fh:  # Arch appx C P2-5: exclusive create, never overwrite
            fh.write(text)
    print(f"wrote {md_out} + {gen_out.name} ({'disclosure-only' if disclosure_only else 'full'}); protected files untouched")


if __name__ == "__main__":
    main()
