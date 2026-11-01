"""Shared weight-book evaluator ``wb_SD1`` (spec docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md §3.0/3.2–3.5,
sha256 2e428f39…bdbb0b). FE.book_ret, LC._ret and ADG gross_and_turnover call this with ``version='wb_SD1'``;
their legacy code is untouched and is the ``wb_SD0`` path (default).

Conventions (identical to the legacy books when nothing is blocked or delisted):
  * ``weights`` row t = target decided at the close of t.
  * fill='next_open' (FE/LC): r_t = NAV_open_t * (1 + sum ex_t * intraday_t) - 1 - cost * TO_t,
    NAV_open_t = 1 + sum ex_{t-1} * (overnight_t); ex_t = weights executed at the t open (= W_{t-1} if tradable).
  * fill='close' (ADG): gross_t = sum ex_{t-1} * cc_t; trade to W_t at the t close (blocked at the close).
  * close_to_close_returns semantics (spec 3.3): an interior halt carries the last close (0 that day); the full move
    lands on the resumption session. Never pct_change(...).fillna(0).
  * Turnover TO_t = sum |ex_t - ex_{t-1}| (legacy: sum |W_{t-1} - W_{t-2}|; equal when nothing is blocked).
  * Halted / no-price / limit-blocked orders freeze the holding (spec 3.2); blocked buys: budget renorm | cash.
  * Delisted names (after last_trade_date) settle on the first later session per spec 3.5 (default recovery 0);
    names absent from ``delist_events`` with trailing NaN keep legacy 0-return and are flagged TAIL_NAN_NOT_IN_TABLE.
  * Ruling 4 (主 Agent 01:03): cs_panel rebuild (resumption-day rows, D-1) is Data P0; the FE adapter refuses
    cs_panel v1 unless allow_cs_panel_v1=True (then tagged 'cs_panel_v1(D-1 gap)').
  * E-1 (主 Agent final 01:53): UNKNOWN delistings are their own category DELIST_WRITEOFF_UNKNOWN (recovery 0 = main
    basis); comparisons 'UNKNOWN at last close -> cash' and recovery 0.3/0.7 are disclosure only. G2 combined weight
    (announced + UNKNOWN) is computed here and written to the events and ``summary`` (see execution_sd1.sd1_delist_summary).
  * E-2 (主 Agent final 01:53): FE and ADG apply NO limit-up/down for now; every FE/ADG output is tagged
    OPTIMISTIC_NO_LIMIT and cannot serve as a gate on its own (book_smoke takes precedence). When cs_panel_v2 carries
    raw limit prices FE switches back to open_touch and the affected leaves are recomputed (disclosure only).
    ADG keeps the frozen-prereg close fills.
  * ``track`` and ``delist_source`` are required in every adapter (Arch P2-2 / P2-4).
  * r3 (Arch P2-R2 / probe 9b81bff1): the FE resume-day entry gate defaults to ``resume_gate='require_announced'``:
    the gate column is ``resume_announced`` (t 09:00 PIT, suspend_d R record), taken from cs_panel_v2 when Data adds it,
    else joined from Data's suspend_flags_v2 at a PINNED sha256 (``resume_flags_sha256``); with neither the FE adapter
    refuses. ``'is_resume_day_fallback'`` (disclosure only) keeps the r2 behaviour and discloses the mild look-ahead;
    ``'off'`` is the gate-off sensitivity. Every FE result carries ``summary['resume_gate']`` with per-year counts of
    blocked new entries (and how many of them are is_resume_day cells without an R record, when both are known).
Research-grade; live=false; promotion_approved=false. Real-data use needs an Arch .ok.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

WB_VERSION = "wb_SD1"
LIMIT_EPS = 0.005
ROOT = Path(__file__).resolve().parents[2]
CS_PANEL_DIR = ROOT / "output/ai_factory/panel_cache"
SUSPEND_FLAGS_V2 = ROOT / "data/v2/suspend_flags/suspend_flags_v2.parquet"   # Data D-2 (same path as delist_accounting)
RESUME_GATES = ("require_announced", "is_resume_day_fallback", "off")
IS_RESUME_DAY_LOOKAHEAD_NOTE = (
    "is_resume_day is derived from same-day (t 16:00, post-close) trading info (vol/amount): a mild look-ahead. It is "
    "used ONLY to block new buys on t (never to buy, sell, size or score), so it can only remove entries "
    "(conservative). The PIT gate is resume_announced (t 09:00, suspend_d R record).")


@dataclass
class WBPanels:
    close: pd.DataFrame                      # total-return (adjusted) close, NaN when no bar
    open: pd.DataFrame | None = None         # same basis as close; None -> open := prev close
    suspended: pd.DataFrame | None = None    # bool halt mask (spec 3.1, composed by the caller)
    limit_up: pd.DataFrame | None = None     # RAW limit prices
    limit_down: pd.DataFrame | None = None
    raw_open: pd.DataFrame | None = None     # RAW prices for the limit test; default = open/close
    raw_high: pd.DataFrame | None = None
    raw_low: pd.DataFrame | None = None
    raw_close: pd.DataFrame | None = None
    entry_block: pd.DataFrame | None = None  # bool: no NEW position may be opened that session (P1-6 resume-day gate)


@dataclass
class WBPolicy:
    version: str = WB_VERSION
    fill: str = "next_open"                  # next_open | close
    limit_policy: str = "open_touch"         # open_touch | one_price_only | off
    blocked_buy_budget: str = "renorm"       # renorm | cash (Core = cash, ruling 1)
    delist_policy: str = "sd1"
    delist_forced_recovery: float = 0.0      # ruling 2
    delist_force_sell_in_period: bool = True  # ruling 3
    cost: float = 0.0                        # per unit two-sided turnover
    no_limit_codes: frozenset = field(default_factory=frozenset)
    cs_panel_version: str = "n/a"
    unknown_policy: str = "writeoff"         # E-1: writeoff (main) | last_close_cash (disclosure)
    g2_threshold: float = 0.01

    def __post_init__(self):
        if self.version != WB_VERSION:
            raise ValueError("weight_book_returns implements wb_SD1 only; wb_SD0 = the legacy functions")
        if self.fill not in ("next_open", "close"):
            raise ValueError(f"bad fill {self.fill}")
        if self.limit_policy not in ("open_touch", "one_price_only", "off"):
            raise ValueError(f"bad limit_policy {self.limit_policy}")
        if self.blocked_buy_budget not in ("renorm", "cash"):
            raise ValueError(f"bad blocked_buy_budget {self.blocked_buy_budget}")
        if self.delist_policy != "sd1":
            raise ValueError("wb_SD1 requires delist_policy='sd1'")
        if not (0.0 <= float(self.delist_forced_recovery) <= 1.0):
            raise ValueError("delist_forced_recovery must be in [0, 1]")
        if self.unknown_policy not in ("writeoff", "last_close_cash"):
            raise ValueError(f"bad unknown_policy {self.unknown_policy}")


def limits_from_ratio(raw_close: pd.DataFrame, ratio, tick: float = 0.01):
    """Limit prices from the previous raw close and a limit ratio (e.g. limit_ratio_at_open), rounded half-up."""
    prev = raw_close.ffill().shift(1)
    r = ratio.reindex_like(raw_close) if isinstance(ratio, pd.DataFrame) else pd.DataFrame(
        float(ratio), index=raw_close.index, columns=raw_close.columns)
    return np.floor(prev * (1 + r) / tick + 0.5) * tick, np.floor(prev * (1 - r) / tick + 0.5) * tick


def _ok(v) -> bool:
    return v is not None and not (isinstance(v, float) and np.isnan(v)) and not (v is pd.NaT) and bool(pd.notna(v))


def _plan(delist_events, idx, cols, C):
    out = {}
    if delist_events is None or len(delist_events) == 0:
        return out
    col = {str(c): i for i, c in enumerate(cols)}
    for r in delist_events.to_dict("records"):
        j = next((col[str(r[k])] for k in ("code", "instrument_id", "ts_code") if _ok(r.get(k)) and str(r[k]) in col), None)
        if j is None:
            continue
        ltd_pos = int(idx.searchsorted(pd.Timestamp(r["last_trade_date"]), side="right")) - 1
        fin = np.flatnonzero(np.isfinite(C[: max(ltd_pos, 0) + 1, j]))
        ff, acq = r.get("force_sell_from"), r.get("acquirer")
        if _ok(r.get("needs_manual_source")) and bool(r.get("needs_manual_source")):
            ff = None   # Arch P1-5: needs_manual_source=True never triggers a forced sell
        out[j] = dict(type=str(r.get("type") or "UNKNOWN"), ltd_pos=ltd_pos, term_pos=ltd_pos + 1,
                      last_pos=int(fin[-1]) if len(fin) else None,
                      force_from=int(idx.searchsorted(pd.Timestamp(ff), side="left")) if _ok(ff) else None,
                      swap_ratio=float(r["swap_ratio"]) if _ok(r.get("swap_ratio")) else None,
                      acq=col.get(str(acq)) if _ok(acq) else None,
                      cps=float(r["cash_per_share"]) if _ok(r.get("cash_per_share")) else None,
                      last_close_raw=float(r["last_close"]) if _ok(r.get("last_close")) else None)
    return out


def weight_book_returns(weights: pd.DataFrame, panels: WBPanels, policy: WBPolicy | None = None, *,
                        delist_events: pd.DataFrame | None = None) -> dict:
    """wb_SD1 daily book -> dict(ret, gross, turnover, events, executed, version, flags, cs_panel_version)."""
    pol = policy or WBPolicy()
    if delist_events is None:
        raise ValueError("wb_SD1 needs delist_events (accounting layer; pass an empty frame to state none)")
    Cdf = panels.close.sort_index().astype(float)
    idx, cols = Cdf.index, list(Cdf.columns)
    n, m = Cdf.shape
    W = weights.reindex(index=idx, columns=cols).ffill().fillna(0.0).to_numpy(float)

    def al(x):
        return x.reindex(index=idx, columns=cols).astype(float).to_numpy() if x is not None else np.full((n, m), np.nan)
    C = Cdf.to_numpy()
    DL = _plan(delist_events, idx, cols, C)
    Cf = Cdf.ffill(limit_area="inside").to_numpy()
    O = al(panels.open)
    SUS = ~np.isfinite(C)
    if panels.suspended is not None:
        SUS |= panels.suspended.reindex(index=idx, columns=cols).fillna(False).astype(bool).to_numpy()
    after = np.zeros((n, m), dtype=bool)
    for j, d in DL.items():
        after[d["ltd_pos"] + 1:, j] = True
    SUS &= ~after
    LU, LD = al(panels.limit_up), al(panels.limit_down)
    rO = al(panels.raw_open) if panels.raw_open is not None else O
    rC = al(panels.raw_close) if panels.raw_close is not None else C
    rH = al(panels.raw_high) if panels.raw_high is not None else None
    rL = al(panels.raw_low) if panels.raw_low is not None else None
    EB = (panels.entry_block.reindex(index=idx, columns=cols).fillna(False).astype(bool).to_numpy()
          if panels.entry_block is not None else np.zeros((n, m), dtype=bool))
    held_cash: dict = {}   # A2: code -> sessions its blocked-buy budget was kept as cash (cash mode)
    free = {j for j, c in enumerate(cols) if c in pol.no_limit_codes}
    events, flags = [], []
    tail = [cols[j] for j in range(m) if j not in DL and np.isfinite(C[:, j]).any() and not np.isfinite(C[-1, j])]
    if tail:
        flags.append(dict(flag="TAIL_NAN_NOT_IN_TABLE", codes=tail))

    def blocked(t, j, side):
        px = rO[t, j] if pol.fill == "next_open" else rC[t, j]
        if SUS[t, j] or after[t, j] or not np.isfinite(C[t, j]) or not np.isfinite(px):
            return "HALT_BLOCKED"
        if pol.limit_policy == "off" or j in free:
            return None
        lim = LU[t, j] if side > 0 else LD[t, j]
        if not np.isfinite(lim):
            return None
        touch = (px >= lim - LIMIT_EPS) if side > 0 else (px <= lim + LIMIT_EPS)
        if pol.limit_policy == "open_touch" or pol.fill == "close" or rH is None or rL is None:
            return "LIMIT_BLOCKED" if touch else None
        one = all(np.isfinite(x) and abs(x - lim) <= LIMIT_EPS for x in (px, rH[t, j], rL[t, j], rC[t, j]))
        return "LIMIT_BLOCKED" if one else None

    post = np.zeros(m)
    ret, gross, TO = np.zeros(n), np.zeros(n), np.zeros(n)
    EX = np.zeros((n, m))
    ar = np.arange(m)
    for t in range(n):
        day = str(idx[t].date())
        rel = np.ones(m)
        if t > 0:
            prev = Cf[t - 1]
            if pol.fill == "next_open":
                cur = np.where(np.isfinite(O[t]) & ~SUS[t], O[t], prev)
            else:
                cur = np.where(np.isfinite(Cf[t]), Cf[t], prev)
            rel = np.where(np.isfinite(cur) & np.isfinite(prev) & (prev > 0), cur / prev, 1.0)
            rel[after[t]] = 1.0
            for j, d in DL.items():   # spec 3.5 step 2 at the first session after last_trade_date
                if t != d["term_pos"] or post[j] <= 0:
                    continue
                typ = d["type"]
                if typ == "UNKNOWN" and pol.unknown_policy == "last_close_cash":   # E-1 disclosure comparison
                    rel[j] = 1.0
                    events.append(dict(date=day, code=cols[j], type="DELIST_UNKNOWN_LAST_CLOSE_CASH", delist_type=typ,
                                       weight=float(post[j]), flag="DISCLOSURE_ONLY_UNKNOWN_AT_LAST_CLOSE"))
                elif typ in ("FORCED_PERIOD", "FORCED_NO_PERIOD", "UNKNOWN"):
                    rel[j] = float(pol.delist_forced_recovery)
                    events.append(dict(date=day, code=cols[j],
                                       type="DELIST_WRITEOFF_UNKNOWN" if typ == "UNKNOWN" else "DELIST_WRITEOFF",
                                       delist_type=typ, weight=float(post[j]), writeoff_value=float(post[j] * (1 - rel[j])),
                                       recovery=rel[j], flag="UNKNOWN_SEPARATE_CATEGORY" if typ == "UNKNOWN" else ""))
                elif typ == "MERGER_SWAP" and d["swap_ratio"] and d["acq"] is not None and d["last_pos"] is not None \
                        and np.isfinite(Cf[t - 1, d["acq"]]):
                    a = d["acq"]
                    conv = d["swap_ratio"] * Cf[t - 1, a] / Cf[d["last_pos"], j]   # value ratio (no lots in a weight book)
                    events.append(dict(date=day, code=cols[j], type="DELIST_MA_CONVERT", weight=float(post[j]),
                                       acquirer=cols[a], value_ratio=float(conv)))
                    post[a] += post[j] * conv; post[j] = 0.0; rel[j] = 1.0
                elif typ == "CASH_OUT" and d["cps"] is not None and d["last_close_raw"]:
                    rel[j] = d["cps"] / d["last_close_raw"]
                    events.append(dict(date=day, code=cols[j], type="DELIST_CASH_OUT", weight=float(post[j]), value_ratio=rel[j]))
                else:
                    rel[j] = 1.0
                    events.append(dict(date=day, code=cols[j], type="DELIST_FALLBACK", delist_type=typ, weight=float(post[j]),
                                       flag="MA_FALLBACK_LAST_CLOSE"))
        leg1 = float(np.sum(post * (rel - 1.0)))
        nav0 = 1.0 + leg1
        pre = post * rel / nav0 if nav0 > 0 else np.zeros(m)
        pre[after[t]] = 0.0   # settled (to cash or acquirer)
        if pol.fill == "next_open":
            tgt = W[t - 1].copy() if t > 0 else np.zeros(m)
        else:
            tgt = W[t].copy()
        period = {j for j, d in DL.items() if pol.delist_force_sell_in_period and d["force_from"] is not None
                  and d["force_from"] <= t}
        pmask = np.isin(ar, list(period))
        F, B = {}, {}
        for j in np.flatnonzero((pre > 1e-12) | (tgt > 1e-12)):
            want = 0.0 if j in period else tgt[j]
            dlt = want - pre[j]
            if abs(dlt) <= 1e-12:
                continue
            if pre[j] > 1e-12:
                why = blocked(t, j, 1 if dlt > 0 else -1)
                if why:
                    F[j] = why
            else:
                why = blocked(t, j, 1) or ("RESUME_DAY_ENTRY_GATE" if EB[t, j] else None) \
                    or ("DELIST_PERIOD" if j in period else None)
                if why:
                    B[j] = why
        bp = [j for j in period if tgt[j] > 0 and j not in F and j not in B]
        ex = np.where(pmask, 0.0, tgt)
        if F or B or bp:
            budget = max(float(tgt.sum()) - float(sum(pre[j] for j in F)), 0.0)
            live = [k for k in np.flatnonzero(tgt > 0) if k not in F and k not in B and k not in period]
            den = sum(tgt[k] for k in live) + (sum(tgt[k] for k in list(B) + bp) if pol.blocked_buy_budget == "cash" else 0.0)
            ex = np.zeros(m)
            for k in live:
                ex[k] = tgt[k] * budget / den if den > 0 else 0.0
            for j, why in F.items():
                ex[j] = pre[j]
                events.append(dict(date=day, code=cols[j], type=why, frozen_weight=float(pre[j]), target_weight=float(tgt[j])))
            for j, why in B.items():
                events.append(dict(date=day, code=cols[j], type=why, frozen_weight=0.0, target_weight=float(tgt[j]),
                                   budget=pol.blocked_buy_budget, cash_held=pol.blocked_buy_budget == "cash"))
                if pol.blocked_buy_budget == "cash":
                    held_cash[cols[j]] = held_cash.get(cols[j], 0) + 1
            events.append(dict(date=day, code="", type="RENORM", n_frozen=len(F), n_blocked_buy=len(B) + len(bp),
                               moved_weight=float(np.abs(ex - np.where(pmask, 0.0, tgt)).sum()), mode=pol.blocked_buy_budget,
                               pricing="exec_day_open"))
        for j in np.flatnonzero(pre > 1e-12):
            if SUS[t, j]:
                events.append(dict(date=day, code=cols[j], type="HALT_HOLD", weight=float(pre[j])))
            if j in period and ex[j] < pre[j] - 1e-12:
                events.append(dict(date=day, code=cols[j], type="DELIST_SOLD_IN_PERIOD", weight=float(pre[j] - ex[j])))
        TO[t] = float(np.abs(ex - (EX[t - 1] if t else 0.0)).sum())
        if pol.fill == "next_open" and t > 0:
            op = np.where(np.isfinite(O[t]) & ~SUS[t], O[t], Cf[t - 1])
            cur = np.where(np.isfinite(Cf[t]), Cf[t], op)
            intra = np.where(np.isfinite(cur) & np.isfinite(op) & (op > 0), cur / op - 1.0, 0.0)
            intra[after[t]] = 0.0
            g = nav0 * (1.0 + float(np.sum(ex * intra))) - 1.0
        else:
            g = leg1
        gross[t] = g
        ret[t] = g - pol.cost * TO[t]
        post = ex.copy(); EX[t] = ex
    for c, k in sorted(held_cash.items()):
        events.append(dict(date="", code=c, type="BLOCKED_BUDGET_CASH_HELD", sessions=int(k),
                           weight=float(np.mean([e["target_weight"] for e in events if e.get("code") == c
                                                 and e.get("cash_held")])),
                           note="A2: blocked-buy budget kept as cash on these sessions (weight = mean target weight)"))
    from quantlab.platform.execution_sd1 import sd1_delist_summary
    summary = sd1_delist_summary(events, delist_events=delist_events, unknown_policy=pol.unknown_policy,
                                 recovery=pol.delist_forced_recovery, threshold=pol.g2_threshold)
    summary.update(a3_renorm_priced_at_exec_open=True)
    events.append(dict(date="", code="", type="G2_CHECK", weight=summary["combined_writeoff_weight"],
                       g2_triggered=summary["g2_triggered"], n_writeoff_announced=summary["n_writeoff_announced"],
                       n_writeoff_unknown=summary["n_writeoff_unknown"], delist_source=summary["delist_source"],
                       source_sha256=summary["source_sha256"]))
    s = lambda a, nm: pd.Series(a, index=idx, name=nm)
    return dict(ret=s(ret, "ret"), gross=s(gross, "gross"), turnover=s(TO, "turnover_2s"),
                events=pd.DataFrame(events), executed=pd.DataFrame(EX, index=idx, columns=cols),
                version=WB_VERSION, flags=flags, cs_panel_version=pol.cs_panel_version, summary=summary)


def run_wb_delist_sensitivity(weights, panels: WBPanels, policy: WBPolicy, *, delist_events,
                              recoveries=(0.0, 0.3, 0.7)) -> dict:
    """E-1 for weight books: {0.0 (main), 0.3, 0.7, "unknown_last_close_cash"}; all but 0.0 are disclosure only."""
    from dataclasses import replace as _rp
    out = {}
    for r in recoveries:
        res = weight_book_returns(weights, panels, _rp(policy, delist_forced_recovery=float(r), unknown_policy="writeoff"),
                                  delist_events=delist_events)
        res["summary"]["basis"] = "main" if float(r) == 0.0 else "sensitivity_disclosure_only"
        out[float(r)] = res
    res = weight_book_returns(weights, panels, _rp(policy, delist_forced_recovery=0.0, unknown_policy="last_close_cash"),
                              delist_events=delist_events)
    res["summary"]["basis"] = "sensitivity_disclosure_only"
    out["unknown_last_close_cash"] = res
    return out


OPTIMISTIC_NO_LIMIT = dict(flag="OPTIMISTIC_NO_LIMIT",
                           note="主 Agent E-2 (01:53 ET): no limit-up/down applied; cannot serve as a gate on its own; "
                                "book_smoke takes precedence. FE -> open_touch once cs_panel_v2 has raw limit prices "
                                "(affected leaves recomputed, disclosure only); ADG keeps frozen-prereg close fills.")


def _tag_optimistic(res: dict) -> dict:
    res["flags"].append(dict(OPTIMISTIC_NO_LIMIT))
    res["summary"]["tags"] = sorted(set(res["summary"].get("tags", [])) | {"OPTIMISTIC_NO_LIMIT"})
    res["summary"]["gate_eligible_alone"] = False
    return res


def check_hiliq_carry(close: pd.DataFrame, executed: pd.DataFrame, carry: pd.DataFrame) -> dict:
    """P1-6: on every hiliq_carry=True cell whose position was HELD into the halt (executed weight > 0 the session
    before), the resumption session must carry a price (row present -> the full gap is booked that day).
    Returns counts; the FE adapter refuses its output on any mismatch."""
    C = close.reindex(index=executed.index, columns=executed.columns)
    K = carry.reindex(index=executed.index, columns=executed.columns).fillna(False).astype(bool)
    EXp = executed.shift(1).fillna(0.0)
    hit = K & (EXp > 1e-12)
    bad = (hit & C.isna()).stack()
    bad = bad[bad]
    return dict(n_carry_cells=int(K.to_numpy().sum()), n_carry_held=int(hit.to_numpy().sum()),
                n_mismatch=int(len(bad)), mismatches=[(str(d.date()), str(c)) for d, c in list(bad.index)[:20]])


# ----------------------------------------------------------------- adapters for the three legacy weight books
def _events_for(codes, delist_source: str):
    from quantlab.platform.delist_accounting import load_delist_events   # accounting layer (guarded; this file is allow-listed)
    return load_delist_events(codes, source=delist_source)


def _need(track, delist_source):
    if track is None or not str(track).strip():
        raise ValueError("track is required (Arch P2-2): e.g. 'core' (blocked budget -> cash) or the leaf/track name")
    if not delist_source:
        raise ValueError("delist_source is required (Arch P2-4): src_events_v1 | src_table_v2 | src_table_v1_d3rule")


def _sha256(path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_resume_flags(codes, years, *, path=None, sha256: str) -> pd.DataFrame:
    """r3 (Arch P2-R2 (a)): (date, instrument, resume_announced, is_resume_day) from Data's suspend_flags_v2 for
    ``codes`` (ts_code, e.g. '000001.SZ' = cs_panel 'instrument') and ``years``. The file must exist and match the
    pinned full sha256 (no unpinned read). Absent row = normal trading day (both False). Read by year chunks."""
    import re
    import pyarrow as pa
    import pyarrow.parquet as pq
    f = Path(path or SUSPEND_FLAGS_V2)
    if not (isinstance(sha256, str) and re.fullmatch(r"[0-9a-f]{64}", sha256)):
        raise ValueError("resume_flags_sha256 must be the full 64-hex sha256 of suspend_flags_v2 (pinned by Arch)")
    if not f.exists():
        raise FileNotFoundError(f"{f} missing: the FE resume gate needs Data's suspend_flags_v2 (D-2) or cs_panel_v2.resume_announced")
    got = _sha256(f)
    if got != sha256:
        raise ValueError(f"{f} sha256={got} != pinned {sha256}")
    names = set(pq.read_schema(f).names)
    miss = {"ts_code", "trade_date", "resume_announced", "is_resume_day"} - names
    if miss:
        raise ValueError(f"{f} lacks {sorted(miss)}")
    td = pq.read_schema(f).field("trade_date").type
    if pa.types.is_integer(td):
        bounds = lambda y: (y * 10000 + 101, y * 10000 + 1231)
    elif pa.types.is_timestamp(td) or pa.types.is_date(td):
        bounds = lambda y: (pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y}-12-31 23:59:59"))
    else:
        bounds = lambda y: (f"{y}0101", f"{y}1231")
    want = sorted(set(map(str, codes))); parts = []
    for y in years:
        lo, hi = bounds(int(y))
        x = pd.read_parquet(f, columns=["ts_code", "trade_date", "resume_announced", "is_resume_day"],
                            filters=[("trade_date", ">=", lo), ("trade_date", "<=", hi), ("ts_code", "in", want)])
        if not x.empty:
            parts.append(x)
    cols = ["date", "instrument", "resume_announced", "is_resume_day"]
    if not parts:
        return pd.DataFrame({"date": pd.Series(dtype="datetime64[ns]"), "instrument": pd.Series(dtype=object),
                             "resume_announced": pd.Series(dtype=bool), "is_resume_day": pd.Series(dtype=bool)})
    x = pd.concat(parts)
    if pa.types.is_integer(td) or pa.types.is_string(td) or pa.types.is_large_string(td):
        x["date"] = pd.to_datetime(x.trade_date.astype(str).str[:8], format="%Y%m%d")
    else:
        x["date"] = pd.to_datetime(x.trade_date)
    x["date"] = x["date"].astype("datetime64[ns]")
    x["instrument"] = x.ts_code.astype(str)
    for c in ("resume_announced", "is_resume_day"):
        x[c] = x[c].astype("boolean").fillna(False).astype(bool)
    return x[cols].drop_duplicates(["date", "instrument"]).reset_index(drop=True)


def _gate_counts(events: pd.DataFrame, ird: pd.DataFrame | None, ann: pd.DataFrame | None) -> dict:
    """Per-year blocked NEW entries (RESUME_DAY_ENTRY_GATE) and how many sit on is_resume_day cells without an R record."""
    if events is None or events.empty or "type" not in events:
        g = pd.DataFrame(columns=["date", "code"])
    else:
        g = events.loc[events.type == "RESUME_DAY_ENTRY_GATE", ["date", "code"]]
    by, wo = {}, {}
    both = ird is not None and ann is not None
    for d, c in zip(pd.to_datetime(g["date"]), g["code"].astype(str)):
        y = int(d.year); by[y] = by.get(y, 0) + 1
        if both:
            a = bool(ann.at[d, c]) if (d in ann.index and c in ann.columns) else False
            r = bool(ird.at[d, c]) if (d in ird.index and c in ird.columns) else False
            if r and not a:
                wo[y] = wo.get(y, 0) + 1
    out = dict(blocked_new_entries_by_year={k: by[k] for k in sorted(by)}, blocked_new_entries_total=int(sum(by.values())))
    if both:
        out["of_which_is_resume_day_without_R_by_year"] = {k: wo.get(k, 0) for k in sorted(by)}
        out["of_which_is_resume_day_without_R_total"] = int(sum(wo.values()))
    else:
        out["of_which_is_resume_day_without_R_by_year"] = None
        out["note_without_R"] = "not computable: needs both is_resume_day and resume_announced"
    return out


def fe_book_ret_sd1(W_long: pd.DataFrame, start, end, *, cost: float, bal: str, bal_open: pd.Series, bal_close: pd.Series,
                    panel_dir: Path | None = None, allow_cs_panel_v1: bool = False, track: str, delist_source: str,
                    resume_gate: str = "require_announced", resume_flags_sha256: str | None = None,
                    resume_flags_path: Path | None = None):
    """FE.book_ret wb_SD1: yearly-chunk read of cs_panel_v2_{y}.parquet (resumption-day rows, D-1 / ruling 4).
    P1-6: no NEW position on a resumption session (B = RESUME_DAY_ENTRY_GATE; gate column = ``resume_announced``
    (t 09:00 PIT) when the panel has it, else ``is_resume_day`` (t 16:00, booking-only -> used only to BLOCK entry,
    conservative, flagged)); ``hiliq_carry`` held-through-halt cells are checked (resumption gap booked) and a
    mismatch refuses the output. E-2: tagged OPTIMISTIC_NO_LIMIT (no limit prices in cs_panel yet).
    r3 ``resume_gate`` (Arch P2-R2): 'require_announced' (default, the only basis for a real FE run): gate =
    resume_announced from cs_panel_v2 if present, else from suspend_flags_v2 at ``resume_flags_sha256`` (pinned;
    ``resume_flags_path`` overrides the path for synthetic tests); neither -> refuse. 'is_resume_day_fallback':
    r2 behaviour, disclosure only, look-ahead note. 'off': gate-off sensitivity (disclosure only).
    Returns (ret Series without the 2 warm-up rows, one-sided mean turnover, full result dict)."""
    _need(track, delist_source)
    if resume_gate not in RESUME_GATES:
        raise ValueError(f"bad resume_gate {resume_gate!r}: one of {RESUME_GATES}")
    import pyarrow.parquet as pq
    pdir = Path(panel_dir or CS_PANEL_DIR)
    years = range(int(str(start)[:4]), int(str(end)[:4]) + 1)
    want = sorted(set(W_long.instrument.astype(str)) - {bal})
    tag = "cs_panel_v2"
    parts = []
    for y in years:
        f = pdir / f"cs_panel_v2_{y}.parquet"
        if not f.exists():
            if not allow_cs_panel_v1:
                raise FileNotFoundError(f"{f} missing: wb_SD1 needs the rebuilt cs_panel_v2 (D-1, Data P0 per ruling 4)")
            f = pdir / f"cs_panel_{y}.parquet"; tag = "cs_panel_v1(D-1 gap)"
        names = set(pq.read_schema(f).names)
        cols_ = ["date", "instrument", "ret", "ret_on"]
        if f.name.startswith("cs_panel_v2_"):
            miss = {"is_resume_day", "hiliq_carry"} - names
            if miss:
                raise ValueError(f"{f} lacks {sorted(miss)}: wb_SD1 FE needs the v2 resumption columns (P1-6)")
            cols_ += ["is_resume_day", "hiliq_carry"] + (["resume_announced"] if "resume_announced" in names else [])
        parts.append(pd.read_parquet(f, columns=cols_, filters=[("instrument", "in", want)]))
    X = pd.concat(parts); del parts
    X["date"] = pd.to_datetime(X["date"]).astype("datetime64[ns]")   # one resolution for the merge below (pandas 3)
    v2_cols = "is_resume_day" in X.columns
    gate_src = None; flags_sha = None
    if resume_gate == "require_announced" and v2_cols and "resume_announced" not in X.columns:
        if resume_flags_sha256 is None:
            raise ValueError("resume_gate='require_announced': cs_panel_v2 has no resume_announced column, so "
                             "resume_flags_sha256 (pinned sha of Data's suspend_flags_v2) is required (Arch P2-R2)")
        fl = load_resume_flags(want, years, path=resume_flags_path, sha256=resume_flags_sha256)
        flags_sha = resume_flags_sha256
        X = X.merge(fl[["date", "instrument", "resume_announced"]], on=["date", "instrument"], how="left")
        gate_src = f"suspend_flags_v2@{resume_flags_sha256}"
    elif "resume_announced" in X.columns:
        gate_src = "cs_panel_v2.resume_announced"
    if v2_cols and resume_gate == "require_announced" and "resume_announced" not in X.columns:
        raise ValueError("resume_gate='require_announced' but no resume_announced column available")
    gate_col = None
    if v2_cols:
        gate_col = {"require_announced": "resume_announced", "is_resume_day_fallback": "is_resume_day", "off": None}[resume_gate]
    gate = carry = ird = ann = None
    if v2_cols:
        X["hiliq_carry"] = X["hiliq_carry"].astype("boolean").fillna(False).astype(bool)
        X["is_resume_day"] = X["is_resume_day"].astype("boolean").fillna(False).astype(bool)
        carry = X.pivot_table(index="date", columns="instrument", values="hiliq_carry", aggfunc="max").fillna(False).astype(bool)
        ird = X.pivot_table(index="date", columns="instrument", values="is_resume_day", aggfunc="max").fillna(False).astype(bool)
        if "resume_announced" in X.columns:
            X["resume_announced"] = X["resume_announced"].astype("boolean").fillna(False).astype(bool)
            ann = X.pivot_table(index="date", columns="instrument", values="resume_announced", aggfunc="max").fillna(False).astype(bool)
        if gate_col is not None:
            gate = ird if gate_col == "is_resume_day" else ann
    rr = X.pivot_table(index="date", columns="instrument", values="ret")
    on = X.pivot_table(index="date", columns="instrument", values="ret_on"); del X
    rr.index = pd.to_datetime(rr.index); on = on.reindex(rr.index); on.index = rr.index
    close = (1 + rr.fillna(0)).cumprod().where(rr.notna())          # total-return index; no row -> NaN (halt/delist)
    open_ = close.ffill().shift(1) * (1 + on)
    close[bal] = bal_close.reindex(close.index); open_[bal] = bal_open.reindex(close.index)
    close = close.loc[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    open_ = open_.reindex(close.index)
    P = W_long.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0)
    P.index = pd.to_datetime(P.index)
    P = P.reindex(close.index).ffill().fillna(0)
    from quantlab.platform.execution_sd1 import sd1_blocked_buy_budget
    pol = WBPolicy(cost=cost, no_limit_codes=frozenset({bal}), cs_panel_version=tag,
                   blocked_buy_budget=sd1_blocked_buy_budget(track), limit_policy="off")
    res = weight_book_returns(P, WBPanels(close=close, open=open_, entry_block=gate), pol,
                              delist_events=_events_for(want, delist_source))
    if not v2_cols:
        res["flags"].append(dict(flag="NO_RESUME_DAY_GATE", note="cs_panel v1 has no resumption columns (D-1 gap)"))
    else:
        if resume_gate == "is_resume_day_fallback":
            res["flags"].append(dict(flag="ENTRY_GATE_IS_RESUME_DAY_T1600",
                                     note="is_resume_day is t-16:00 info: used only to block new entries (conservative)"))
            res["flags"].append(dict(flag="IS_RESUME_DAY_MILD_LOOKAHEAD", note=IS_RESUME_DAY_LOOKAHEAD_NOTE))
        elif resume_gate == "off":
            res["flags"].append(dict(flag="RESUME_GATE_OFF_SENSITIVITY",
                                     note="resume-day entry gate disabled: sensitivity, disclosure only"))
        chk = check_hiliq_carry(close, res["executed"], carry)
        res["summary"]["hiliq_carry_check"] = chk
        if chk["n_mismatch"]:
            raise RuntimeError(f"hiliq_carry check failed (P1-6): {chk}")
    rg = dict(mode=resume_gate, gate_column=gate_col if v2_cols else None,
              source=(gate_src if gate_col == "resume_announced" else ("cs_panel_v2.is_resume_day" if gate_col else None)),
              resume_flags_sha256=flags_sha,
              basis="main" if resume_gate == "require_announced" else "sensitivity_disclosure_only",
              is_resume_day_lookahead_note=IS_RESUME_DAY_LOOKAHEAD_NOTE)
    rg.update(_gate_counts(res["events"], ird, ann))
    res["summary"]["resume_gate"] = rg
    _tag_optimistic(res)
    to = res["turnover"]
    return res["ret"].iloc[2:], float(to.iloc[2:].mean() / 2), res


def fe_resume_gate_sensitivity(W_long: pd.DataFrame, start, end, **kw) -> dict:
    """r3 (Arch P2-R2): main (``resume_gate`` as given, default 'require_announced') vs gate 'off' (disclosure only).
    Returns {'main': result, 'gate_off': result, 'diff': per-year sum of (main - gate_off) daily returns, n_blocked}."""
    kw = dict(kw); main_gate = kw.pop("resume_gate", "require_announced")
    if main_gate == "off":
        raise ValueError("main resume_gate must not be 'off'")
    r0, to0, a = fe_book_ret_sd1(W_long, start, end, resume_gate=main_gate, **kw)
    r1, to1, b = fe_book_ret_sd1(W_long, start, end, resume_gate="off", **kw)
    d = (r0 - r1.reindex(r0.index)).fillna(0.0)
    by = {int(y): float(v) for y, v in d.groupby(d.index.year).sum().items()}
    return dict(main=a, gate_off=b, turnover=dict(main=to0, gate_off=to1),
                diff=dict(sum_ret_diff_by_year=by, n_blocked_main=a["summary"]["resume_gate"]["blocked_new_entries_total"],
                          basis="sensitivity_disclosure_only"))


def lc_ret_sd1(W_long: pd.DataFrame, px_fn, raw_fn, *, cost: float, net: bool = True, track: str, delist_source: str,
               etf=lambda i: False):
    """LC._ret wb_SD1. px_fn(i) -> (adj_open, adj_close); raw_fn(i) -> DataFrame(open, close, volume,
    limit_ratio_at_open) raw (stocks only). Limits = open_touch on raw prices; halt = no bar or volume <= 0
    (P2-3: same-day volume decides fill feasibility only, never selection; disclosed)."""
    _need(track, delist_source)
    P = W_long.pivot_table(index="date", columns="instrument", values="target_weight", aggfunc="sum").fillna(0).sort_index()
    P.index = pd.to_datetime(P.index)
    C = pd.DataFrame({i: px_fn(i)[1] for i in P.columns}).reindex(P.index)
    O = pd.DataFrame({i: px_fn(i)[0] for i in P.columns}).reindex(P.index)
    stocks = [i for i in P.columns if not etf(i)]
    raw = {i: raw_fn(i) for i in stocks}
    rO = pd.DataFrame({i: pd.to_numeric(raw[i]["open"], errors="coerce") for i in stocks}).reindex(P.index)
    rC = pd.DataFrame({i: pd.to_numeric(raw[i]["close"], errors="coerce") for i in stocks}).reindex(P.index)
    vol = pd.DataFrame({i: pd.to_numeric(raw[i]["volume"], errors="coerce") for i in stocks}).reindex(P.index)
    ratio = pd.DataFrame({i: pd.to_numeric(raw[i]["limit_ratio_at_open"], errors="coerce") for i in stocks}).reindex(P.index)
    LU, LD = limits_from_ratio(rC, ratio)
    sus = (vol <= 0).reindex(columns=P.columns).fillna(False)
    from quantlab.platform.execution_sd1 import sd1_blocked_buy_budget
    pol = WBPolicy(cost=cost if net else 0.0, no_limit_codes=frozenset(i for i in P.columns if etf(i)),
                   blocked_buy_budget=sd1_blocked_buy_budget(track))
    res = weight_book_returns(P, WBPanels(close=C, open=O, suspended=sus, limit_up=LU.reindex(columns=P.columns),
                                          limit_down=LD.reindex(columns=P.columns), raw_open=rO.reindex(columns=P.columns),
                                          raw_close=rC.reindex(columns=P.columns)),
                              pol, delist_events=_events_for([i for i in P.columns if not etf(i)], delist_source))
    return res["ret"].iloc[2:], res


def adg_gross_and_turnover_sd1(P: pd.DataFrame, close_fn, *, track: str, delist_source: str, no_limit=frozenset()):
    """ADG gross_and_turnover wb_SD1 (fill at the close, as the frozen ADG prereg). close_fn(i) -> adj close Series.
    E-2: no limits (tagged OPTIMISTIC_NO_LIMIT). Returns (gross, turnover, full result)."""
    _need(track, delist_source)
    C = pd.DataFrame({i: close_fn(i) for i in P.columns}).reindex(P.index)
    from quantlab.platform.execution_sd1 import sd1_blocked_buy_budget
    pol = WBPolicy(fill="close", limit_policy="off", no_limit_codes=frozenset(no_limit),
                   blocked_buy_budget=sd1_blocked_buy_budget(track))
    res = weight_book_returns(P, WBPanels(close=C), pol, delist_events=_events_for(list(P.columns), delist_source))
    _tag_optimistic(res)
    return res["gross"].iloc[1:], res["turnover"].iloc[1:], res
