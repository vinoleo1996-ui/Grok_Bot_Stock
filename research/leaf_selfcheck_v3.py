"""Leaf self-check v3: marginal contribution (cap/B4/S6), GATE_V3, hypothesis critique, alphalens-style factor report.
Lookahead check lives in research/leaf_lookahead_check.py. Research-grade; live=false; no Book-Smoke; constants untouched.
Usage: python3 research/leaf_selfcheck_v3.py [--universe HI_LIQ_V1.1|FULLA_V1] <leaf> [<leaf> ...]  (default HI_LIQ_V1.1)"""
from __future__ import annotations
import sys, json, glob, resource
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.alpha_decay_gate as ADG
import research.leaf_selfcheck_common as LC
AF = ROOT / "output/ai_factory"; RPT = AF / "leaf_reports"
BAL = "510300.SH"; etf = LC.etf; NT = {"60w": 6, "100w": 10}
TRACKS = {"B4": {"60w": ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_60w_20261013_r2.parquet",
                 "100w": ROOT / "output/small_aum_concentration/v2/B_B4_50_25_25_topN_100w_20261013_r2.parquet"},
          "S6": {"60w": ROOT / "output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_60w_20261013.parquet",
                 "100w": ROOT / "output/strategy_paper_s6/S6_cap50_ee25_eq25_topN_100w_20261013.parquet"}}
LAG = {"report_rc_allup": "研报 report_date 次一交易日 09:00；定期报告 actual_date", "analyst_recoverage": "研报次一交易日 09:00",
       "stk_surv": "调研日 +25 交易日（Data p95；p95 意味着约 5% 事件实际披露更晚，存在轻微前视风险）",
       "insurer_surv": "调研日 +25 交易日（同 stk_surv）", "tp_rerate": "研报 report_date 次一交易日 09:00；T1 写权重次日开盘成交"}


def wfile(leaf): return Path(sorted(f for f in glob.glob(str(AF / f"g1g5_{leaf}_daily_weights_2*.parquet")))[-1])
def mfile(leaf): return Path(sorted(glob.glob(str(AF / f"g1g5_{leaf}_run_meta_2*.json")))[-1])


def metrics(r):
    nav = (1 + r).cumprod(); c = float(nav.iloc[-1] ** (244 / len(r)) - 1); md = float((nav / nav.cummax() - 1).min())  # AI 2026-10-14: CAGR/Sharpe 年化 244 主报
    return dict(cagr=c, mdd=md, calmar=c / abs(md) if md < 0 else None, sharpe=float(r.mean() / r.std() * np.sqrt(244)))


def leaf_topn(L: pd.DataFrame, N: int) -> dict:
    out = {}
    for d, g in L.groupby("date"):
        w = g.set_index("instrument").target_weight
        e = w[[etf(i) for i in w.index]]; st = w.drop(e.index)
        if len(st):
            k = st.sort_values(ascending=False).head(N); st = k * st.sum() / k.sum()
        out[d] = pd.concat([e, st])
    return out


def stack(base: pd.DataFrame, leafw: dict, share=0.2) -> pd.DataFrame:
    rows = []
    for d, g in base.groupby("date"):
        if d not in leafw: continue
        agg = (g.set_index("instrument").target_weight * (1 - share)).to_dict()
        for i, v in leafw[d].items(): agg[i] = agg.get(i, 0) + share * v
        for i in list(agg):
            if not etf(i) and agg[i] > 0.06: agg[BAL] = agg.get(BAL, 0) + agg[i] - 0.06; agg[i] = 0.06
        t = sum(agg.values()); rows += [(d, i, v / t) for i, v in agg.items()]
    return pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])


def marginal(leaf: str) -> dict:
    L = LC._w(wfile(leaf)); res = {}
    for tier, N in NT.items():
        lt = leaf_topn(L, N)
        LC.WMIX.clear(); LC.WMIX.update(cap=1.0); capw = LC._overlay({"cap": LC.CAP_ADV}, N)
        bases = {"capacity_adv": capw}
        for tk, f in TRACKS.items():
            b = pd.read_parquet(f[tier], columns=["date", "instrument", "target_weight"]); b["date"] = b["date"].astype(str).str[:10]
            bases[tk] = b[b.target_weight > 0]
        for bk, bw in bases.items():
            if bk == "capacity_adv":
                LC.WMIX.clear(); LC.WMIX.update(cap=0.8, leaf=0.2); nw = LC._overlay({"cap": LC.CAP_ADV, "leaf": wfile(leaf)}, N)
            else:
                nw = stack(bw, lt)
            r0, r1 = LC._ret(bw), LC._ret(nw); ix = r0.index.intersection(r1.index)
            m0, m1 = metrics(r0[ix]), metrics(r1[ix])
            res[f"{tier}_{bk}"] = dict(base=m0, with_leaf=m1, span=[str(ix[0].date()), str(ix[-1].date())],
                                       delta={k: (m1[k] - m0[k]) if m1[k] is not None and m0[k] is not None else None for k in m0})
    return res


def gate_v3(marg: dict, v2: dict) -> dict:
    c = {t: marg[f"{t}_capacity_adv"] for t in NT}
    r = dict(mdd_le_25={t: c[t]["with_leaf"]["mdd"] >= -0.25 for t in NT}, mdd_le_15_ref={t: c[t]["with_leaf"]["mdd"] >= -0.15 for t in NT},
             cagr_gt_cap={t: c[t]["with_leaf"]["cagr"] > c[t]["base"]["cagr"] for t in NT},
             decay_keep=v2["decay"]["outcome"] == "KEEP", tradable=not v2["cost"]["untradable"])
    r["pass"] = bool(all(r["mdd_le_25"].values()) and all(r["cagr_gt_cap"].values()) and r["decay_keep"] and r["tradable"])
    r["note_zh"] = "自检估计（复权、T+1 次日开盘、扣成本净收益；审计修复 2026-10-14），终判以 Eng Book-Smoke X2 为准；GATE_V3 仅适用 06:01 ET 冻结后新开叶，叶11–14 为回溯参考"
    return r


# AI 2026-10-14 (Arch P1): 验收池参数化。HI_LIQ_V1.1=纸面路径（默认）；FULLA_V1=研究；
# AI 2026-10-18 (Arch P2 N8): 旧静态 mid_large 前300 池路径已删除；只允许逐日 PIT 池 HI_LIQ_V1.1（默认）/FULLA_V1。旧池输出文件保留不重写。
UNIVERSES = ("HI_LIQ_V1.1", "FULLA_V1")
DEFAULT_UNIVERSE = "HI_LIQ_V1.1"
PANEL = ROOT / "output/ai_factory/panel_cache"


def ic_tstat_hac(ic, h: int) -> float | None:
    """Newey-West (Bartlett) HAC t of mean IC, lag = h-1 (floor 1, same as Alpha alpha_combo_marginal.ic_tstats). 仅披露，不改阈值。"""
    x = np.asarray(ic, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return None
    lag = max(h - 1, 1); u = x - x.mean(); v = u @ u / n
    for k in range(1, min(lag, n - 1) + 1): v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return float(x.mean() / np.sqrt(v / n)) if v > 0 else None


def _check_universe(universe: str) -> str:
    """AI 2026-10-18 (Arch P3-1): 显式校验，不依赖 assert（python -O 下 assert 失效）；在 argparse 与 run() 入口即退出，不跑完整评估。"""
    if universe not in UNIVERSES:
        raise SystemExit(f"leaf_selfcheck_v3: invalid --universe {universe!r}; allowed {UNIVERSES} (legacy mid_large top300 removed per Arch P2 N8)")
    return universe


def _pool_panel(universe: str, dates) -> tuple:
    """Daily PIT pool mask (date x inst, bool) + adj price index from cs_panel cache (ret=close/pre_close-1)."""
    col = {"HI_LIQ_V1.1": "hiliq", "FULLA_V1": "fulla"}[universe]
    d0, d1 = min(dates), max(dates); fr = []
    for y in range(d0.year, d1.year + 1):
        f = PANEL / f"cs_panel_{y}.parquet"
        if f.exists(): fr.append(pd.read_parquet(f, columns=["date", "instrument", "ret", col]))
    X = pd.concat(fr); X = X[X.instrument.str[:1].isin(list("036"))]
    M = X.pivot_table(index="date", columns="instrument", values=col, aggfunc="max").fillna(False).astype(bool)
    Rr = X.pivot_table(index="date", columns="instrument", values="ret").astype("float64")
    P = (1 + Rr.fillna(0)).cumprod().where(Rr.notna())
    return M, P


def factor_report(leaf: str, universe: str = DEFAULT_UNIVERSE) -> dict:
    _check_universe(universe)
    L = LC._w(wfile(leaf)); L = L[~L.instrument.map(etf)]
    S = L.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum")
    S.index = pd.to_datetime(S.index)
    M, P = _pool_panel(universe, S.index)
    # AI 2026-10-18 (Arch P3-2): 池日均成员数 = PIT 池掩码逐日 True 计数（不含仅因持仓加入的代码），按评估日平均
    pool_members = M.reindex(index=S.index).fillna(False).sum(axis=1)
    cols = sorted(set(M.columns) | set(S.columns)); S = S.reindex(columns=cols).fillna(0.0)
    P = P.reindex(index=S.index, columns=cols); M = M.reindex(index=S.index, columns=cols).fillna(False)
    M = M | (S > 0)  # held names always evaluated
    M = M.drop(columns=[c for c in ("600519.SH", "002371.SZ") if c in M.columns], errors="ignore").reindex(columns=cols).fillna(False)
    # AI 2026-10-18 (Arch P3-2): 原字段 "pool" 实为列数（池掩码全部代码 ∪ 持仓代码），改名 n_codes_ever；新增池日均成员数
    out = {"n_days": len(S), "n_codes_ever": len(cols), "pool_mean_daily_members": float(pool_members.mean()),
           "pool_min_daily_members": int(pool_members.min()), "pool_max_daily_members": int(pool_members.max()), "pool_universe": universe}; ic = {}
    for h in (1, 5, 10, 20, 60):
        F = P.shift(-h) / P - 1
        icd, ricd, spr = [], [], []
        for d in S.index[:-h]:
            s, f = S.loc[d], F.loc[d]; ok = f.notna() & M.loc[d]
            s, f = s[ok], f[ok]
            if s.std() == 0 or len(s) < 30: continue
            icd.append(np.corrcoef(s, f)[0, 1]); ricd.append(s.rank().corr(f.rank()))
            spr.append(f[s > 0].mean() - f.mean())
        icd, ricd, spr = map(np.array, (icd, ricd, spr))
        n_eff = max(len(icd) / h, 1)
        ic[f"{h}d"] = dict(ic_mean=float(icd.mean()), ic_t=float(icd.mean() / icd.std() * np.sqrt(n_eff)), rank_ic_mean=float(ricd.mean()),
                           ic_t_naive=float(icd.mean() / icd.std() * np.sqrt(len(icd))), ic_t_hac=ic_tstat_hac(icd, h), ic_hac_lag=max(h - 1, 1), icir=float(icd.mean() / icd.std()), held_minus_pool_mean=float(spr.mean()),
                           held_minus_pool_ann=float(spr.mean() * 244 / h), n=int(len(icd)))  # AI/Eng 2026-10-14: 年化 244，与 metrics()/quantlab.metrics 一致
    out["ic"] = ic
    held = {d: set(S.columns[S.loc[d] > 0]) for d in S.index}; ds = list(S.index); ac = {}
    for h in (1, 5, 20, 60):
        js = [len(held[ds[i]] & held[ds[i + h]]) / len(held[ds[i]] | held[ds[i + h]]) for i in range(len(ds) - h) if held[ds[i]] | held[ds[i + h]]]
        ac[f"{h}d"] = float(np.mean(js)) if js else None
    out["holding_autocorr_jaccard"] = ac
    out["mean_names"] = float(np.mean([len(v) for v in held.values()]))
    return out


def critique(leaf: str, meta: dict, v2: dict, marg: dict) -> str:
    s = meta["selfcheck"]; yr = {y: v["alpha_ann"] for y, v in s["by_year"].items()}
    tot = sum(max(a, 0) for a in yr.values()); top = max(yr, key=yr.get)
    conc = (yr[top] / tot) if tot > 0 else None; neg = [y for y, a in yr.items() if a < 0]
    rhos = {k: (v if isinstance(v, float) else v["rho"]) for k, v in s.get("rho_resid_vs", {}).items()}
    hi = {k: round(v, 3) for k, v in rhos.items() if abs(v) >= 0.35}
    sty = s.get("style_neutral")
    c6 = marg["60w_capacity_adv"]["delta"]; c10 = marg["100w_capacity_adv"]["delta"]
    lines = [f"### {leaf} 假设批判清单（自动生成，供 Alpha 复核）",
             f"- [ ] who_pays 是否仍成立：「{meta.get('who_pays_zh','')[:80]}…」→ **需人工判断**；数据侧提示：残差 α {s['alpha_ann_leaf']*100:+.2f}%/年，衰减门 {v2['decay']['outcome']}（最新滚动 α {v2['decay'].get('latest_resid_alpha', float('nan'))*100:+.2f}%）",
             f"- [{'x' if (conc is not None and conc > 0.6) or len(neg) >= 2 else ' '}] α 是否集中在单一年份：分年 {', '.join(f'{y} {a*100:+.2f}%' for y, a in yr.items())}；最大年份 {top} 占正 α {('%.0f%%' % (conc*100)) if conc else 'n/a'}；负年 {neg or '无'}",
             f"- [{'x' if meta.get('mean_names', 99) < 8 or meta.get('mean_ballast', 0) > 0.7 else ' '}] 容量/稀疏：日均 {meta.get('mean_names', float('nan')):.1f} 名，压舱 {meta.get('mean_ballast', float('nan'))*100:.0f}%，双边换手 {v2['cost']['to_2s_mean']*100:.2f}%/日，{'不可交易' if v2['cost']['untradable'] else '可交易'}",
             f"- [{'x' if hi else ' '}] 与已知风格/旧叶重叠：|ρ|≥0.35 → {hi or '无'}" + (f"；风格回归 α_style {sty['alpha_style_ann']*100:+.2f}%（红利 {sty['load_div_spread']:+.2f}，大盘 {sty['load_big_spread']:+.2f}）" if sty else "；未做风格回归"),
             f"- [ ] 数据滞后风险：{LAG.get(leaf, '?')}",
             f"- 组合边际（+20% 于 capacity_adv）：60万 ΔCAGR {c6['cagr']*100:+.2f}pp / ΔMDD {c6['mdd']*100:+.2f}pp / ΔCalmar {c6['calmar']:+.3f} / ΔSharpe {c6['sharpe']:+.3f}；100万 ΔCAGR {c10['cagr']*100:+.2f}pp / ΔMDD {c10['mdd']*100:+.2f}pp / ΔCalmar {c10['calmar']:+.3f} / ΔSharpe {c10['sharpe']:+.3f}",
             "（[x] = 自动标红，需关注；[ ] = 未触发或需人工）"]
    return "\n".join(lines)


def run(leaf: str, universe: str = DEFAULT_UNIVERSE) -> dict:
    _check_universe(universe)  # Arch P3-1: 入口即校验，坏参数不进入 evaluate/marginal
    o = RPT / leaf; o.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(mfile(leaf)))
    v2 = LC.evaluate(wfile(leaf), gates=False)  # always fresh (audit fix)
    marg = marginal(leaf); g3 = gate_v3(marg, v2); fr = factor_report(leaf, universe)
    res = dict(leaf=leaf, pool_universe=universe, marginal_base="LC.CAP_ADV = 纸面主干 capacity_adv 书（g1g5_capacity_adv_daily_weights_20261013_111219，现行纸面轨本身）；仅作「是否赢主干」对照，不是验收/IC 池", weights=str(wfile(leaf).relative_to(ROOT)), marginal=marg, gate_v3=g3, factor=fr,
               decay=v2["decay"]["outcome"], cost=v2["cost"], peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    # 旧口径输出文件名不变；新池写独立文件，不覆盖旧结论
    suf = f"_pool-{universe}"
    (o / f"selfcheck_v3{suf}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    md = critique(leaf, meta, v2, marg)
    (o / f"hypothesis_critique{suf}.md").write_text(md + "\n")
    return res


if __name__ == "__main__":
    args = sys.argv[1:]; uni = DEFAULT_UNIVERSE
    if "--universe" in args:
        k = args.index("--universe")
        if k + 1 >= len(args): raise SystemExit("leaf_selfcheck_v3: --universe requires a value")
        uni = args[k + 1]; del args[k:k + 2]
    _check_universe(uni)  # Arch P3-1: 参数解析处即退出
    for lf in args:
        r = run(lf, uni); print(lf, "done RSS", round(r["peak_rss_mb"]), "pool", r["pool_universe"])
        for h, v in r["factor"]["ic"].items():
            print(f"  IC {h}: mean {v['ic_mean']:+.4f}  t_naive {v['ic_t_naive']:+.2f}  t_neff {v['ic_t']:+.2f}  t_HAC(lag {v['ic_hac_lag']}) {v['ic_t_hac'] if v['ic_t_hac'] is None else round(v['ic_t_hac'], 2)}  n {v['n']}")
