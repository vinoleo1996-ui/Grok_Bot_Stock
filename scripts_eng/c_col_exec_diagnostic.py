#!/usr/bin/env python3
"""Read-only execution diagnostic for scorecard columns B and C (主 Agent 00:59 ET). NO engine rerun, no returns.

Inputs (read-only): each book's target_weights.parquet / actual_weights.parquet / nav.csv (the run's own outputs) and the
same market panels the book loaded (platform load_execution_panels: open/close/volume/limit/suspended, corporate actions).
The books did not persist fills/orders/events (record_fills=False), so orders are re-derived from the book's own
holdings with the engine's order rules (quantlab/platform/execution.py run_weight_schedule, ExecConfig.strategy_v1 via
v2_multisleeve_book.exec_cfg: next_open fill, 10% of that day's volume cap, unfilled=carry-until-next-signal, target lot
floor, min_trade_value 2000, sells first, buys cash-limited). Filled qty = the book's actual share change; only the
REASON is attributed. Reason per order at the fill session (engine precedence): suspended → limit_up(buy)/limit_down(sell)
→ ADV/participation cap (10% of day volume) on the capped part → remainder: <1 lot = lot rounding at fill, buy ≥1 lot =
cash shortage, sell ≥1 lot = other. End-of-window orders (last signal) never get a fill session.
Idle cash identity per close t+1 (signal t, Σtgt=1):
  idle = Σ(tgt − floored target)        [whole-lot floor at target + min_trade skips]
       + Σ d·(C_t/NAV_t − C_{t+1}/NAV_{t+1})   [intraday drift/cost residual]
       + Σ (d − s_{t+1})·C_{t+1}/NAV_{t+1}       [unfilled, by reason; sells left unfilled count negative]
Usage: c_col_exec_diagnostic.py   (writes core_x2/c_col_exec_diagnostic.{csv,md})
"""
from __future__ import annotations
import json, sys, resource
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import ok_runner_pin  # noqa: E402
# quantlab.platform.execution is imported only AFTER the .ok gate passes (see main) so an unpinned engine never loads.
load_execution_panels = lot_rule_for = corporate_action_arrays = LIMIT_EPS = tick_for_code = None

OUT = ROOT / "output/strategy_optimizer/core_x2"
SRC = {"B": ROOT / "output/v3/book_smoke_g1g5_capacity_adv_x2", "C": ROOT / "output/strategy_hiliq/capadv_x2"}
CORE = "sh.510300"; CAP = 0.10; MIN_TV = 2000.0
REASONS = ["suspended", "limit_up_buy", "limit_down_sell", "participation_cap", "cash_shortage_buy", "lot_round_at_fill",
           "other_sell", "end_of_window"]


def diag(col: str, aum: int):
    bd = SRC[col] / f"aum_{aum}/X2/BOOK"
    S = json.loads((bd / "summary.json").read_text(encoding="utf-8"))["metrics"]
    tw = pd.read_parquet(bd / "target_weights.parquet").pivot(index="session", columns="instrument_id", values="weight")
    aw = pd.read_parquet(bd / "actual_weights.parquet").pivot(index="session", columns="instrument_id", values="weight")
    nav = pd.read_csv(bd / "nav.csv", index_col=0, parse_dates=True)["nav"]
    codes = sorted(set(tw.columns) | set(aw.columns) | {CORE})
    p, _ = load_execution_panels(codes, nav.index[0], nav.index[-1], corporate_actions=True)
    p = p.aligned(); idx = p.close.index
    assert len(idx) == len(nav) and (idx == nav.index).all(), "session index mismatch"
    codes = list(p.close.columns)
    tw = tw.reindex(index=pd.to_datetime(tw.index)).reindex(index=idx, columns=codes).fillna(0.0).to_numpy(float)
    aw = aw.reindex(index=pd.to_datetime(aw.index)).reindex(index=idx, columns=codes).fillna(0.0).to_numpy(float)
    C = p.close.to_numpy(float); Cm = p.close.ffill(limit_area="inside").ffill().to_numpy(float)
    O = p.open.to_numpy(float); V = p.volume.to_numpy(float)
    LU = p.limit_up.to_numpy(float) if p.limit_up is not None else np.full_like(C, np.nan)
    LD = p.limit_down.to_numpy(float) if p.limit_down is not None else np.full_like(C, np.nan)
    SUS = (p.suspended.to_numpy() if p.suspended is not None else np.zeros_like(C, bool)) | ~np.isfinite(C)
    _, SR, FR = corporate_action_arrays(p)
    MULT = (1.0 + SR) * FR
    N = nav.to_numpy(float)
    SH = np.where(np.isfinite(Cm) & (Cm > 0), aw * N[:, None] / np.where(Cm > 0, Cm, 1), 0.0)
    STEP = np.array([lot_rule_for(c).step for c in codes], float)
    free = np.array([c == CORE for c in codes])
    eps = np.array([LIMIT_EPS if tick_for_code(c) >= 0.01 else 0.0005 for c in codes])
    T = len(idx)
    req = 0.0; fill_eng = 0.0; unf = dict.fromkeys(REASONS, 0.0); n_ord = dict.fromkeys(REASONS, 0)
    rereq_unf = 0.0; churn_req = 0.0; idle_parts = []
    prev_unf_side = {}
    for t in range(T):
        tgt = tw[t]; ref = Cm[t]; ok = np.isfinite(ref) & (ref > 0)
        des = np.where(tgt > 0, np.floor(tgt * N[t] / np.where(ok, ref, 1) / STEP + 1e-10) * STEP, 0.0)
        keep = np.isclose(tgt * N[t] / np.where(ok, ref, 1), SH[t], rtol=1e-12, atol=1e-8) & (tgt > 0)
        des = np.where(keep, SH[t], des)
        delta = np.where(ok, des - SH[t], 0.0)
        skip = (np.abs(delta) * ref < MIN_TV) & (tgt > 0)
        delta = np.where(skip | (np.abs(delta) < 1e-6), 0.0, delta)
        # shares are re-derived from float32 weights: ignore sub-share noise
        delta = np.where(np.abs(delta) < 0.5, 0.0, delta)
        des_eff = SH[t] + delta
        req_t = np.abs(delta) * np.where(ok, ref, 0)
        req += req_t.sum()
        cur_side = {}
        if t + 1 >= T:
            unf["end_of_window"] += req_t.sum(); n_ord["end_of_window"] += int((delta != 0).sum()); break
        u = t + 1
        base = SH[t] * MULT[u]; rem = delta * MULT[u]
        f = SH[u] - base  # signed actual fill
        for j in np.flatnonzero(delta != 0):
            side = 1 if rem[j] > 0 else -1; q = abs(rem[j]); fq = max(0.0, min(q, side * f[j])) if np.isfinite(f[j]) else 0.0
            if fq > 0 and np.isfinite(O[u, j]):
                fill_eng += fq * O[u, j]
            uq = q - fq
            if uq < 0.5:
                continue
            un = uq * ref[j]
            px0 = O[u, j]
            if SUS[u, j] or not np.isfinite(px0) or px0 <= 0:
                r = "suspended"
            elif (not free[j]) and side > 0 and np.isfinite(LU[u, j]) and px0 >= LU[u, j] - eps[j]:
                r = "limit_up_buy"
            elif (not free[j]) and side < 0 and np.isfinite(LD[u, j]) and px0 <= LD[u, j] + eps[j]:
                r = "limit_down_sell"
            else:
                cap = V[u, j] * CAP if np.isfinite(V[u, j]) else 0.0
                capped = max(0.0, q - cap)
                if capped > 0.5:
                    cp = min(capped, uq); unf["participation_cap"] += cp * ref[j]; n_ord["participation_cap"] += 1
                    uq -= cp; un = uq * ref[j]
                    if uq < 0.5:
                        cur_side[j] = side; continue
                r = "lot_round_at_fill" if uq < STEP[j] - 0.5 else ("cash_shortage_buy" if side > 0 else "other_sell")
            unf[r] += un; n_ord[r] += 1; cur_side[j] = side
        # churn: requested notional on names re-requested after a failed order on the same side yesterday
        for j in np.flatnonzero(delta != 0):
            if prev_unf_side.get(j) == (1 if delta[j] > 0 else -1):
                rereq_unf += req_t[j]
        prev_unf_side = cur_side
        # idle-cash identity at close u
        w_u = np.where(np.isfinite(Cm[u]), SH[u] * Cm[u] / N[u], 0.0)
        floor_gap = np.nansum(tgt - des_eff * np.where(ok, ref, 0) / N[t]) if tgt.sum() > 0 else 0.0
        drift = np.nansum(des_eff * (np.where(ok, ref, 0) / N[t] - np.nan_to_num(Cm[u]) / N[u]))
        unf_gap = np.nansum((des_eff * MULT[u] - SH[u]) * np.nan_to_num(Cm[u]) / N[u])
        idle_parts.append(dict(idle=1 - w_u.sum(), floor=floor_gap, drift=drift, unfilled=unf_gap,
                               unfilled_buy=np.nansum(np.clip(des_eff * MULT[u] - SH[u], 0, None) * np.nan_to_num(Cm[u]) / N[u])))
    tot_unf = sum(unf.values())
    I = pd.DataFrame(idle_parts)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    return dict(col=col, aum=aum, book=str(bd.relative_to(ROOT)), fill_ratio_book=S["fill_ratio"], idle_mean_book=S["idle_cash_mean"],
                gross_book=S["gross_exposure_mean"], n_codes_book=S["n_codes"], requested=req, filled_engine_px=fill_eng,
                fill_ratio_rederived=fill_eng / req if req else np.nan, unfilled_total_refpx=tot_unf,
                unf=unf, n_ord=n_ord, rereq_requested=rereq_unf, idle=I.mean().to_dict(), rss_mb=rss)


def render_md(R) -> str:
    """Human-readable table. Reconciliation rule: |rederived − book fill ratio| > 0.02 or idle gap > 1pp → RECON_FAIL
    (attribution then descriptive only)."""
    L = ["# B/C 列执行层诊断（只读既有 book 产物；未重跑引擎；不出收益）", "",
         f"- runner: scripts_eng/c_col_exec_diagnostic.py sha256={ok_runner_pin.own_sha(__file__)}",
         "- 原因优先级（引擎顺序）：停牌 → 涨停买/跌停卖 → 10% 当日成交量参与上限 → 余量：<1 手=整手取整，买≥1手=现金不足，卖≥1手=其他；窗口末单无成交日。",
         "- 名义额按信号日参考价计；成交率 = 引擎开盘价成交额 / 请求额。", "",
         "| 列 | aum | 成交率 book / 重导 | 闲置现金 book / 重导 | 总敞口 | 交易过只数 | 对账 |",
         "|---|---|---|---|---|---|---|"]
    for r in R:
        ok = abs(r["fill_ratio_rederived"] - r["fill_ratio_book"]) <= 0.02 and abs(r["idle"]["idle"] - r["idle_mean_book"]) <= 0.01
        L.append(f"| {r['col']} | {r['aum']} | {r['fill_ratio_book']:.3f} / {r['fill_ratio_rederived']:.3f} | "
                 f"{100*r['idle_mean_book']:.1f}% / {100*r['idle']['idle']:.1f}% | {r['gross_book']:.2f} | {r['n_codes_book']} | "
                 f"{'OK' if ok else 'RECON_FAIL（归因仅作描述）'} |")
    L += ["", "## 未成交额按原因（占请求额 %）", "", "| 列 | aum | " + " | ".join(REASONS) + " | 次日同向重报占请求额 |",
          "|---|---|" + "---|" * (len(REASONS) + 1)]
    for r in R:
        L.append(f"| {r['col']} | {r['aum']} | " + " | ".join(f"{100*r['unf'][k]/r['requested']:.1f}" for k in REASONS)
                 + f" | {100*r['rereq_requested']/r['requested']:.1f} |")
    L += ["", "## 闲置现金分解（均值，pp）", "", "| 列 | aum | 闲置 | 目标整手取整+最小成交额 | 日内漂移/成本 | 未成交（净） | 其中未成交买单 |",
          "|---|---|---|---|---|---|---|"]
    for r in R:
        i = r["idle"]
        L.append(f"| {r['col']} | {r['aum']} | {100*i['idle']:.1f} | {100*i['floor']:.1f} | {100*i['drift']:.1f} | {100*i['unfilled']:.1f} | {100*i['unfilled_buy']:.1f} |")
    L += ["", "live=false · promotion=false · 研究级描述，不调参"]
    return "\n".join(L) + "\n"


def main():
    # DEFERRED (Arch review 4698a2c1 §8 #3): only after SD1 delivery + SD0 parity proof; .ok must also pin execution.py.
    ok_runner_pin.enforce(__file__, [OUT / "ARCH_RESIGN_A_v1_3.ok", OUT / "ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok"], modes=["diagnostic"],
                          deps={"execution": ROOT / "quantlab/platform/execution.py", "platform_init": ROOT / "quantlab/platform/__init__.py",
                                "ok_runner_pin": Path(ok_runner_pin.__file__)})
    global load_execution_panels, lot_rule_for, corporate_action_arrays, LIMIT_EPS, tick_for_code
    from quantlab.platform.execution import (load_execution_panels, lot_rule_for, corporate_action_arrays,  # noqa: E402
                                             LIMIT_EPS, tick_for_code)
    rows, R = [], []
    for col in ("B", "C"):
        for aum in (600000, 1000000):
            r = diag(col, aum); R.append(r)
            for k in REASONS:
                rows.append(dict(col=col, aum=aum, metric="unfilled_by_reason", reason=k, notional=round(r["unf"][k], 2),
                                 share_of_unfilled=round(r["unf"][k] / r["unfilled_total_refpx"], 4) if r["unfilled_total_refpx"] else None,
                                 share_of_requested=round(r["unf"][k] / r["requested"], 4), n_orders=r["n_ord"][k]))
            for k in ("floor", "drift", "unfilled", "unfilled_buy"):
                rows.append(dict(col=col, aum=aum, metric="idle_cash_component_mean", reason=k, notional=None,
                                 share_of_unfilled=None, share_of_requested=None, n_orders=None, idle_pp=round(100 * r["idle"][k], 2)))
            rows.append(dict(col=col, aum=aum, metric="summary", reason="book_vs_rederived", notional=round(r["requested"], 2),
                             fill_ratio_book=round(r["fill_ratio_book"], 4), fill_ratio_rederived=round(r["fill_ratio_rederived"], 4),
                             idle_book_pp=round(100 * r["idle_mean_book"], 2), idle_rederived_pp=round(100 * r["idle"]["idle"], 2),
                             gross_book=round(r["gross_book"], 3), n_codes=r["n_codes_book"],
                             rereq_share_of_requested=round(r["rereq_requested"] / r["requested"], 4)))
    pd.DataFrame(rows).to_csv(OUT / "c_col_exec_diagnostic.csv", index=False)
    (OUT / "c_col_exec_diagnostic.md").write_text(render_md(R), encoding="utf-8")
    (OUT / "_c_col_exec_diagnostic_raw.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
