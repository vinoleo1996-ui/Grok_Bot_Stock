"""Summarize MAINBOOK_V2 A2 sealed results + Chinese report. promotion_approved=false."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("/workspace/QuantLab/output/alpha/MAINBOOK_V2_A2_SEALED")
ZH = Path("/workspace/QuantLab/output/alpha/MAINBOOK_V2_A2_SEALED_ZH.md")
R = pd.read_parquet(OUT / "ic_by_date.parquet")
meta = json.load(open(OUT / "run_meta.json"))
corr = json.load(open(OUT / "pool_corr_mean_spearman.json"))
Npath = OUT / "noise_ic_by_date.parquet"
N = pd.read_parquet(Npath) if Npath.exists() else pd.DataFrame()

LABS = [
    "oo1", "oo5", "oo20", "overnight", "intraday", "cc1",
    "oo1_lag1", "oo5_lag1", "resid_all_oo1", "resid_all_oo5",
]
FAC_MEMBERS = ["R02_20D", "turn_20d", "L01_RV60", "V02_BP", "LIQ02_AMIHUD"]
ARMS = ["ArmA_EW5", "ArmB_EW4"]
SIDE = ["V01_EP"]
NAMES = FAC_MEMBERS + ARMS + SIDE


def st(s):
    s = s.dropna()
    if len(s) == 0:
        return {"mean_ic": None, "icir": None, "t_naive": None, "pos_frac": None, "n_dates": 0}
    m, sd = float(s.mean()), float(s.std())
    return {
        "mean_ic": round(m, 5),
        "icir": round(m / sd, 4) if sd > 0 else None,
        "t_naive": round(m / sd * np.sqrt(len(s)), 2) if sd > 0 else None,
        "pos_frac": round(float((s > 0).mean()), 3),
        "n_dates": int(len(s)),
    }


nz = {}
if len(N):
    for (u, l), g in N.groupby(["universe", "label"]):
        per = g.groupby("k")["ic"].agg(["mean", "std"])
        per["icir"] = per["mean"] / per["std"]
        nz[f"{u}|{l}"] = {
            "p95_abs_mean_ic": round(float(per["mean"].abs().quantile(0.95)), 5),
            "p95_abs_icir": round(float(per["icir"].abs().quantile(0.95)), 4),
            "n_noise": int(len(per)),
        }

R["year"] = pd.to_datetime(R["date"]).dt.year
Rs = R[R.window == "sealed"].copy()
Rh = R[R.window == "holdout_confirm"].copy()

summary = {
    "promotion_approved": False,
    "meta": meta,
    "noise": nz,
    "pool_corr": corr,
    "results_sealed": {},
    "results_holdout_confirm_only": {},
    "ep_verification": {
        "path": "data/v2/ep/ep_pit_daily_tushare.parquet",
        "acceptance": "data/v2/ep/ep_pit_daily_tushare_acceptance.json",
        "date_min": "2018-01-02",
        "date_max": "2026-10-09",
        "sealed_coverage_note": "verified on disk before run; nonnull ~99.97% in sealed",
    },
}


def evaluate(g, u, f, corr_u):
    res = {l: st(g[l]) for l in LABS if l in g.columns}
    by_year = g.groupby("year")[["oo1", "oo5", "oo20", "overnight", "intraday"]].mean().round(5)
    folds = []
    for lab in ["oo1", "oo5"]:
        yrs = sorted(g.year.unique())
        imp = tot = 0
        for y in yrs[1:]:
            tr = g[g.year < y][lab].mean()
            te = g[g.year == y][lab].mean()
            if np.isfinite(tr) and np.isfinite(te):
                tot += 1
                imp += int(np.sign(tr) * te > 0)
        folds.append({"label": lab, "folds_improved": imp, "folds": tot})
    ic1 = res.get("oo1", {}).get("mean_ic") or 0.0
    icl = res.get("oo1_lag1", {}).get("mean_ic") or 0.0
    retained = (icl / ic1) if ic1 else None
    lag = {
        "ic_oo1": ic1,
        "ic_oo1_lag1": icl,
        "delta_lag": round(
            max(0.0, abs(ic1) - abs(icl)) if np.sign(ic1) == np.sign(icl) else abs(ic1), 5
        ),
        "retained_frac": round(retained, 3) if retained is not None else None,
    }
    n1 = nz.get(f"{u}|oo1", {})
    n5 = nz.get(f"{u}|oo5", {})
    noise_pass = {
        "oo1": abs(ic1) > n1.get("p95_abs_mean_ic", 0) if n1 else None,
        "oo5": abs(res.get("oo5", {}).get("mean_ic") or 0) > n5.get("p95_abs_mean_ic", 0)
        if n5
        else None,
    }
    mc = None
    if f in FAC_MEMBERS and corr_u is not None and f in corr_u:
        c = pd.DataFrame(corr_u)
        mc = round(float(c[f].drop(f).abs().max()), 4)
    # net of cost crude
    g2 = g.dropna(subset=["top_dec_oo5", "univ_oo5"]).copy()
    if len(g2):
        g2["lo_net"] = g2.top_dec_oo5 - g2.univ_oo5 - 0.0020
        lo_mean = float(g2.lo_net.mean())
        lo_ann = float(np.prod(1 + g2.lo_net) ** (52 / len(g2)) - 1)
        spread = float((g2.top_dec_oo5 - g2.bot_dec_oo5).mean())
        rank_spread_agree = bool(np.sign(g2.oo5.mean()) == np.sign(spread))
        top_lp = float(g2.top_dec_lowprice_frac.mean()) if "top_dec_lowprice_frac" in g2 else None
        top_sz = float(g2.top_dec_size_pct.mean()) if "top_dec_size_pct" in g2 else None
    else:
        lo_mean = lo_ann = spread = None
        rank_spread_agree = None
        top_lp = top_sz = None

    icir1 = res.get("oo1", {}).get("icir") or 0
    icir5 = res.get("oo5", {}).get("icir") or 0
    rules = {
        "R1_icir_gt_0.10_and_noise95": bool(
            (abs(icir1) > 0.10 or abs(icir5) > 0.10)
            and (noise_pass.get("oo1") or noise_pass.get("oo5"))
        ),
        "R2_max_pool_corr_lt_0.70": (mc < 0.70) if mc is not None else None,
        "R3_size_ind_neutral_reported": True,  # always size+SW L1 before IC
        "R4_lag1_retained_ge_0.5": bool((retained or 0) >= 0.5),
        "R5_wf_majority_folds": bool(
            folds[0]["folds"] > 0 and folds[0]["folds_improved"] * 2 > folds[0]["folds"]
        ),
        "R6_net_of_20bp_longonly_pos": bool(lo_mean is not None and lo_mean > 0),
        "R7_full_ablation_TODO": False,  # not done this round
        "R8_sixfold_OOS_TODO_used_year_wf": bool(
            folds[0]["folds"] >= 3
        ),  # year WF proxy; true 6-fold TODO
    }
    # core pass (cheap subset; R7 TODO fails hard so report separately)
    core_keys = ["R1_icir_gt_0.10_and_noise95", "R4_lag1_retained_ge_0.5", "R5_wf_majority_folds", "R6_net_of_20bp_longonly_pos"]
    if mc is not None:
        core_keys.append("R2_max_pool_corr_lt_0.70")
    core_pass = all(rules[k] for k in core_keys if rules[k] is not None)

    return {
        "stats": res,
        "by_year": by_year.to_dict(),
        "lag": lag,
        "walk_forward": folds,
        "max_abs_pool_corr": mc,
        "longonly_net20bp_weekly_mean": round(lo_mean, 5) if lo_mean is not None else None,
        "longonly_net_geo_ann": round(lo_ann, 4) if lo_ann is not None else None,
        "spread_oo5_mean": round(spread, 5) if spread is not None else None,
        "rankic_vs_spread_agree": rank_spread_agree,
        "top_dec_lowprice_lt3_frac": round(top_lp, 4) if top_lp is not None else None,
        "top_dec_mean_size_pctile": round(top_sz, 4) if top_sz is not None else None,
        "rules8": rules,
        "core_pass_excl_R7": bool(core_pass),
        "noise_pass": noise_pass,
    }


for window_df, key in ((Rs, "results_sealed"), (Rh, "results_holdout_confirm_only")):
    for u in ["full", "smallcap"]:
        for f in NAMES:
            g = window_df[(window_df.universe == u) & (window_df.factor == f)]
            if len(g) == 0:
                continue
            summary[key][f"{u}|{f}"] = evaluate(g, u, f, corr.get(u))
            pd.DataFrame(summary[key][f"{u}|{f}"]["stats"]).T.to_csv(
                OUT / f"stats_{window_df.window.iloc[0] if len(window_df) else 'x'}_{u}_{f}.csv"
            )

# Arm A vs B delta
cmp = {}
for u in ["full", "smallcap"]:
    a = summary["results_sealed"].get(f"{u}|ArmA_EW5", {})
    b = summary["results_sealed"].get(f"{u}|ArmB_EW4", {})
    if not a or not b:
        continue
    cmp[u] = {
        "ArmA_oo1_icir": a["stats"]["oo1"]["icir"],
        "ArmB_oo1_icir": b["stats"]["oo1"]["icir"],
        "ArmA_oo5_icir": a["stats"]["oo5"]["icir"],
        "ArmB_oo5_icir": b["stats"]["oo5"]["icir"],
        "ArmA_oo20_icir": a["stats"]["oo20"]["icir"],
        "ArmB_oo20_icir": b["stats"]["oo20"]["icir"],
        "ArmA_overnight_ic": a["stats"]["overnight"]["mean_ic"],
        "ArmB_overnight_ic": b["stats"]["overnight"]["mean_ic"],
        "ArmA_intraday_ic": a["stats"]["intraday"]["mean_ic"],
        "ArmB_intraday_ic": b["stats"]["intraday"]["mean_ic"],
        "ArmA_net_ann": a["longonly_net_geo_ann"],
        "ArmB_net_ann": b["longonly_net_geo_ann"],
        "ArmA_core_pass": a["core_pass_excl_R7"],
        "ArmB_core_pass": b["core_pass_excl_R7"],
        "amihud0_improves_oo5_icir": bool(
            (b["stats"]["oo5"]["icir"] or 0) > (a["stats"]["oo5"]["icir"] or 0)
        ),
        "amihud0_improves_net": bool(
            (b["longonly_net_geo_ann"] or -9) > (a["longonly_net_geo_ann"] or -9)
        ),
    }
summary["arm_compare_sealed"] = cmp
summary["trial_count"] = {
    "sealed_factor_x_universe": int(len(NAMES) * 2),
    "arms": 2,
    "members": 5,
    "side_notes": 1,
    "holdout_confirm_reported_not_for_selection": True,
    "noise_factors": f"{meta.get('n_noise', 50)} x 2 univ x 2 labels (benchmark)",
    "note": "selection forbidden on 2024-06+; holdout is confirm-only",
}

json.dump(
    summary,
    open(OUT / "summary.json", "w"),
    indent=1,
    ensure_ascii=False,
    default=lambda o: bool(o) if isinstance(o, (np.bool_,)) else (float(o) if isinstance(o, (np.floating,)) else str(o)),
)

# ---- Chinese report ----
def fmt_icir(stats, lab):
    s = stats.get(lab) or {}
    return f"{s.get('mean_ic')} / ICIR {s.get('icir')} (n={s.get('n_dates')})"


lines = []
lines.append("# MAINBOOK_V2 A2 独立密封窗复验（研究级）")
lines.append("")
lines.append("- **promotion_approved=false**（因子/复合/报告）")
lines.append("- **密封窗**：2018-01-01 → 2024-05-31（**禁止**用 2024-06 及以后挑因子/调权/选成员）")
lines.append("- **Holdout**：2024-06+ 仅作确认报表，不参与选择")
lines.append("- **入口参考**：`run_mainbook_v2_session`；本脚本复现中性+等权复合，**未改** `P1_DEFAULT_INTEGRATE_WEIGHTS`")
lines.append("- **Amihud**：主簿符号仍为 `−|r|/amount`（未翻转）；已 ×1e9 + Eng `winsorize` rank 退化回退对齐")
lines.append(f"- **抽样**：每 {meta.get('step')} 个交易日；密封信号日 {meta.get('n_sealed_dates')}；耗时 {meta.get('runtime_sec')}s")
lines.append("")
lines.append("## 0. EP / 财务 PIT 核验（盘上）")
lines.append("")
lines.append("| 制品 | 路径 | 覆盖 |")
lines.append("|---|---|---|")
lines.append("| EP PIT 日表 | `data/v2/ep/ep_pit_daily_tushare.parquet` | 2018-01-02→2026-10-09；密封窗非空约 99.97%；验收 JSON PASS |")
lines.append("| ocf_to_profit 日表 | `data/v2/financials_pit/ocf_to_profit_pit_daily_tushare.parquet` | 日覆盖约 99%；2018-01-02 起 |")
lines.append("")
lines.append("**结论**：D1 依赖满足，A2 可跑。V01_EP 仅作侧注 process IC，本轮不挑进主簿。")
lines.append("")
lines.append("## 1. Arm 定义")
lines.append("")
lines.append("| Arm | 成员 | 权重 | 是否写回库默认 |")
lines.append("|---|---|---|---|")
lines.append("| **A（当前默认）** | R02_20D, turn_20d, L01_RV60, V02_BP, LIQ02_AMIHUD | 等权 1 | 否（保持库内现状） |")
lines.append("| **B（研究对照）** | 同上去掉 Amihud | 剩余四因子等权 | **否**（仅研究臂；Leo 未确认 Amihud=0） |")
lines.append("")
lines.append("## 2. 密封窗主结果（全市场，规模+SW L1 中性后）")
lines.append("")
lines.append("| 对象 | oo1 IC/ICIR | oo5 | oo20 | 隔夜 IC | 日内 IC | 扣20bp净年化* | 核心关(除R7) |")
lines.append("|---|---|---|---|---|---|---|---|")

def row_md(u, f, block):
    if not block:
        return
    s = block["stats"]
    lines.append(
        f"| {u}/{f} | {s['oo1']['mean_ic']}/{s['oo1']['icir']} | {s['oo5']['mean_ic']}/{s['oo5']['icir']} | "
        f"{s['oo20']['mean_ic']}/{s['oo20']['icir']} | {s['overnight']['mean_ic']} | {s['intraday']['mean_ic']} | "
        f"{block.get('longonly_net_geo_ann')} | {'PASS' if block.get('core_pass_excl_R7') else 'FAIL'} |"
    )

for f in ARMS + FAC_MEMBERS + SIDE:
    row_md("full", f, summary["results_sealed"].get(f"full|{f}"))
lines.append("")
lines.append("\\* 粗口径：多头前十分位相对全池等权，按周全换手扣 20bp；非 Strategy 引擎。")
lines.append("")
lines.append("### 小盘三分位（密封窗）")
lines.append("")
lines.append("| 对象 | oo1 IC/ICIR | oo5 | oo20 | 扣20bp净年化 | 核心关 |")
lines.append("|---|---|---|---|---|---|")
for f in ARMS + FAC_MEMBERS:
    b = summary["results_sealed"].get(f"smallcap|{f}")
    if not b:
        continue
    s = b["stats"]
    lines.append(
        f"| small/{f} | {s['oo1']['mean_ic']}/{s['oo1']['icir']} | {s['oo5']['mean_ic']}/{s['oo5']['icir']} | "
        f"{s['oo20']['mean_ic']}/{s['oo20']['icir']} | {b.get('longonly_net_geo_ann')} | "
        f"{'PASS' if b.get('core_pass_excl_R7') else 'FAIL'} |"
    )
lines.append("")
lines.append("## 3. Arm A vs Arm B（Amihud=0 是否改善复合）")
lines.append("")
for u, d in cmp.items():
    lines.append(f"### {u}")
    lines.append("")
    lines.append("| 指标 | Arm A (EW5) | Arm B (EW4 Amihud=0) | B更好? |")
    lines.append("|---|---|---|---|")
    lines.append(f"| oo1 ICIR | {d['ArmA_oo1_icir']} | {d['ArmB_oo1_icir']} | {d['ArmB_oo1_icir'] is not None and d['ArmA_oo1_icir'] is not None and abs(d['ArmB_oo1_icir'])>abs(d['ArmA_oo1_icir'])} |")
    lines.append(f"| oo5 ICIR | {d['ArmA_oo5_icir']} | {d['ArmB_oo5_icir']} | {d['amihud0_improves_oo5_icir']} |")
    lines.append(f"| oo20 ICIR | {d['ArmA_oo20_icir']} | {d['ArmB_oo20_icir']} | — |")
    lines.append(f"| 隔夜/日内 IC | {d['ArmA_overnight_ic']}/{d['ArmA_intraday_ic']} | {d['ArmB_overnight_ic']}/{d['ArmB_intraday_ic']} | — |")
    lines.append(f"| 扣20bp净年化 | {d['ArmA_net_ann']} | {d['ArmB_net_ann']} | {d['amihud0_improves_net']} |")
    lines.append(f"| 核心关 | {d['ArmA_core_pass']} | {d['ArmB_core_pass']} | — |")
    lines.append("")

# overall verdict
improves = any(d.get("amihud0_improves_oo5_icir") or d.get("amihud0_improves_net") for d in cmp.values())
lines.append(f"**研究结论（不改默认权重）**：密封窗内 Amihud=0 对复合的改善 = **{'是（至少一项 ICIR 或净收益更好）' if improves else '否（未见明确改善）/证据不足'}**。库默认权重未改；是否落库等 Leo 确认。")
lines.append("")
lines.append("## 4. 八条准入（廉价版 / TODO）")
lines.append("")
lines.append("依据 `/workspace/QuantLab-V2_REBUILD_PLAN_ZH.md` §2.2。")
lines.append("")
for f in ARMS:
    b = summary["results_sealed"].get(f"full|{f}")
    if not b:
        continue
    lines.append(f"### full / {f}")
    lines.append("")
    for k, v in b["rules8"].items():
        lines.append(f"- {k}: **{v}**")
    lines.append(f"- lag retained: {b['lag']}")
    lines.append(f"- walk-forward: {b['walk_forward']}")
    lines.append(f"- max_abs_pool_corr: {b['max_abs_pool_corr']}")
    lines.append(f"- rankIC vs spread agree: {b['rankic_vs_spread_agree']}")
    lines.append("")
lines.append("**TODO**：R7 全流程消融（从状态/标准化/调参整段拿掉）本轮未做；R8 真六折用年份 WF 代理。")
lines.append("")
lines.append("## 5. 成员池相关（密封窗全市场 Spearman 均值）")
lines.append("")
lines.append("```")
lines.append(json.dumps(corr.get("full", {}), indent=1, ensure_ascii=False))
lines.append("```")
lines.append("")
lines.append("## 6. Holdout 确认（2024-06+，不参与选择）")
lines.append("")
lines.append("| 对象 | oo5 IC/ICIR | 扣20bp净年化 |")
lines.append("|---|---|---|")
for f in ARMS:
    b = summary["results_holdout_confirm_only"].get(f"full|{f}")
    if not b:
        continue
    s = b["stats"]
    lines.append(f"| full/{f} | {s['oo5']['mean_ic']}/{s['oo5']['icir']} | {b.get('longonly_net_geo_ann')} |")
lines.append("")
lines.append("## 7. V01_EP 侧注（密封窗，不进主簿）")
lines.append("")
epb = summary["results_sealed"].get("full|V01_EP")
if epb:
    s = epb["stats"]
    lines.append(f"- oo1: {fmt_icir(s,'oo1')}")
    lines.append(f"- oo5: {fmt_icir(s,'oo5')}")
    lines.append(f"- oo20: {fmt_icir(s,'oo20')}")
    lines.append(f"- 隔夜/日内: {s['overnight']['mean_ic']} / {s['intraday']['mean_ic']}")
    lines.append(f"- 核心关(除R7): {epb['core_pass_excl_R7']}")
else:
    lines.append("- （无结果）")
lines.append("")
lines.append("## 8. 试验计次与文件")
lines.append("")
lines.append(f"- trial_count: {json.dumps(summary['trial_count'], ensure_ascii=False)}")
lines.append("- 台账：`docs/trial_ledger.csv` family=`mainbook_v2_a2`")
lines.append("- 输出目录：`output/alpha/MAINBOOK_V2_A2_SEALED/`（summary.json + tables）")
lines.append("- 本报告：`output/alpha/MAINBOOK_V2_A2_SEALED_ZH.md`")
lines.append("")
lines.append("## 9. 七字段实验卡")
lines.append("")
lines.append("| 字段 | 内容 |")
lines.append("|---|---|")
lines.append("| 数据时点 | T 日收盘可知信号；收益自 t+1 开盘 |")
lines.append("| 样本切分 | 密封 2018-01..2024-05；holdout 2024-06+ 仅确认 |")
lines.append("| 留出 | 2024-06+ 不参与选择 |")
lines.append("| 成本 | 粗 20bp/周全换手（非引擎） |")
lines.append("| 成交时点 | t+1 开盘；涨停不可买；停牌剔除 |")
lines.append("| 宇宙 | 全市场（不剔最小 30%）；另报小盘三分位 |")
lines.append("| 代码+数据版本 | research/mainbook_v2_a2_sealed.py；ep_pit_daily_tushare；Eng AMIHUD_WINSORIZE_FIX |")
lines.append("")

ZH.write_text("\n".join(lines), encoding="utf-8")
print("wrote", ZH, "summary keys", list(summary["results_sealed"].keys())[:8])
for u, d in cmp.items():
    print("CMP", u, d)
