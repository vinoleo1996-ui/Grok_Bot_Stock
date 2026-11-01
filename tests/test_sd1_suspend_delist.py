"""SD1 suspend/delist acceptance tests T1–T13 + E-1 / E-2 / P1-5 / P1-6 / P1-7 (spec
docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md §3.8, sha256 2e428f39…fdbb0b; Arch SD1 review 7f0b4819; run-auth spec
docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md 1aa43bdd). Synthetic data only, except T13's real-data case (opt-in).

GATE (in code, at import/collection time, BEFORE any module under test is imported; 主 Agent 01:59 ruling):
  ok_runner_pin.enforce(__file__, [docs/v2/eng_sd1/ARCH_SD1_TEST.ok], modes=["selftest"] (+ "real_data" when
  QL_SD1_REAL_DATA=1), deps=TEST_DEPS) plus the self-checks ok_runner_pin c7805d9a does not do (scope=selftest, every
  known allow_* explicit, allow_real_data consistent with the mode, out_dir = mkdtemp or /tmp/<tag> (never output/ or
  the repo), no BOM / CR / inline comments, signed_et + expires_et ISO8601 with offset and not expired, format/signer).
  A refusal raises SystemExit (aborts collection); there is no skip path.

Run (qlvenv: system python3 has no pytest), serial, nothing else concurrently, RSS <= 1.5GB:
  PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider
Writes only under the .ok out_dir (removed at exit); never output/. live=false; promotion=false.
"""
from __future__ import annotations

import atexit
import datetime as _dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_OK = ROOT / "docs/v2/eng_sd1/ARCH_SD1_TEST.ok"
REAL_DATA = os.environ.get("QL_SD1_REAL_DATA") == "1"
KNOWN_ALLOW = ("selftest", "real_data", "dryrun", "full", "smoke", "diagnostic", "disclosure_only")
# every project module this file executes (static AST import closure, 2026-10-18); pinned as dep_sha256_<key>
TEST_DEPS = {
    "execution": "quantlab/platform/execution.py",
    "execution_sd1": "quantlab/platform/execution_sd1.py",
    "tradability": "quantlab/platform/tradability.py",
    "delist_accounting": "quantlab/platform/delist_accounting.py",
    "platform_init": "quantlab/platform/__init__.py",
    "ok_runner_pin": "scripts_eng/ok_runner_pin.py",
    "sd1_pit_static_check": "scripts_eng/sd1_pit_static_check.py",
    # r3.1 (Arch 2b8f81c9 §6.1-2): T10 pinned-scope scan reads the paper import closure list (156 entries, each
    # re-verified against its recorded sha256 inside the scan) -> the list itself is a pinned dep
    "paper_import_closure": "docs/v2/eng_sd1/paper_import_closure.json",
    # ---- rest of the static closure (function-level imports included; over-approximation is deliberate)
    "quantlab____init__": "quantlab/__init__.py",
    "quantlab__backtest____init__": "quantlab/backtest/__init__.py",
    "quantlab__backtest__engine": "quantlab/backtest/engine.py",
    "quantlab__backtest__ledger": "quantlab/backtest/ledger.py",
    "quantlab__backtest__tax": "quantlab/backtest/tax.py",
    "quantlab__config": "quantlab/config.py",
    "quantlab__config_validation": "quantlab/config_validation.py",
    "quantlab__data____init__": "quantlab/data/__init__.py",
    "quantlab__data__contracts": "quantlab/data/contracts.py",
    "quantlab__data__eastmoney": "quantlab/data/eastmoney.py",
    "quantlab__data__exchange_rules": "quantlab/data/exchange_rules.py",
    "quantlab__data__industry": "quantlab/data/industry.py",
    "quantlab__data__market": "quantlab/data/market.py",
    "quantlab__data__qualification": "quantlab/data/qualification.py",
    "quantlab__data__sina": "quantlab/data/sina.py",
    "quantlab__data__sources": "quantlab/data/sources.py",
    "quantlab__data__store": "quantlab/data/store.py",
    "quantlab__data__v2_d0_meta": "quantlab/data/v2_d0_meta.py",
    "quantlab__data__v2_readers": "quantlab/data/v2_readers.py",
    "quantlab__factors____init__": "quantlab/factors/__init__.py",
    "quantlab__factors__engine": "quantlab/factors/engine.py",
    "quantlab__factors__neutralize": "quantlab/factors/neutralize.py",
    "quantlab__factors__orthogonalize": "quantlab/factors/orthogonalize.py",
    "quantlab__factors__p1_factor_lib": "quantlab/factors/p1_factor_lib.py",
    "quantlab__factors__p1_pipeline": "quantlab/factors/p1_pipeline.py",
    "quantlab__factors__residual_factory": "quantlab/factors/residual_factory.py",
    "quantlab__factors__v2_min_pipeline": "quantlab/factors/v2_min_pipeline.py",
    "quantlab__factors__walk_forward": "quantlab/factors/walk_forward.py",
    "quantlab__mandate": "quantlab/mandate.py",
    "quantlab__mandate_v2": "quantlab/mandate_v2.py",
    "quantlab__metrics": "quantlab/metrics.py",
    "quantlab__platform__futures": "quantlab/platform/futures.py",
    "quantlab__platform__margin": "quantlab/platform/margin.py",
    "quantlab__platform__strategy_feed": "quantlab/platform/strategy_feed.py",
    "quantlab__portfolio____init__": "quantlab/portfolio/__init__.py",
    "quantlab__portfolio__trade_calendar": "quantlab/portfolio/trade_calendar.py",
    "quantlab__portfolio__v2_constructor": "quantlab/portfolio/v2_constructor.py",
    "quantlab__portfolio__v2_rebalance": "quantlab/portfolio/v2_rebalance.py",
    "quantlab__promotion_gate": "quantlab/promotion_gate.py",
    "quantlab__report____init__": "quantlab/report/__init__.py",
    "quantlab__report__advice": "quantlab/report/advice.py",
    "quantlab__report__capital": "quantlab/report/capital.py",
    "quantlab__report__metrics": "quantlab/report/metrics.py",
    "quantlab__smallcap____init__": "quantlab/smallcap/__init__.py",
    "quantlab__smallcap__sim": "quantlab/smallcap/sim.py",
    "quantlab__strategy____init__": "quantlab/strategy/__init__.py",
    "quantlab__strategy__allocation": "quantlab/strategy/allocation.py",
    "quantlab__strategy__candidates": "quantlab/strategy/candidates.py",
    "quantlab__strategy__crowding": "quantlab/strategy/crowding.py",
    "quantlab__strategy__decision": "quantlab/strategy/decision.py",
    "quantlab__strategy__experts": "quantlab/strategy/experts.py",
    "quantlab__strategy__legacy": "quantlab/strategy/legacy.py",
    "quantlab__strategy__portfolio": "quantlab/strategy/portfolio.py",
    "quantlab__strategy__risk": "quantlab/strategy/risk.py",
    "quantlab__strategy__risk_policy": "quantlab/strategy/risk_policy.py",
    "quantlab__strategy__risk_trades": "quantlab/strategy/risk_trades.py",
    "quantlab__strategy__scoring": "quantlab/strategy/scoring.py",
    "quantlab__universe____init__": "quantlab/universe/__init__.py",
    "quantlab__universe__d1_masks": "quantlab/universe/d1_masks.py",
    "quantlab__universe__mask": "quantlab/universe/mask.py",
    "quantlab__v2_schemas": "quantlab/v2_schemas.py",
}
ISO_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2})$")


def _refuse(msg):
    raise SystemExit(f"REFUSED (test_sd1 selftest gate): {msg}")


def _selftest_selfcheck(ok: Path, real_data: bool) -> Path:
    """Checks ok_runner_pin c7805d9a does not do (ARCH_RUN_AUTH_SELFTEST_SPEC §2-§4, §9). Returns the out_dir."""
    raw = ok.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        _refuse(f"{ok}: UTF-8 BOM")
    if b"\r" in raw:
        _refuse(f"{ok}: CR line endings (LF only)")
    kv = {}
    for line in raw.decode("utf-8").split("\n"):
        t = line.strip()
        if not t or t.startswith("#") or "=" not in t:
            continue
        k, v = t.split("=", 1); k, v = k.strip(), v.strip()
        if "#" in v:
            _refuse(f"{ok}: inline comment in {k!r} (spec §3)")
        kv[k] = v
    for k, want in (("format", "quantlab_run_auth_v1"), ("signed_by", "arch"), ("scope", "selftest"),
                    ("live", "false"), ("promotion", "false"), ("allow_selftest", "true")):
        if kv.get(k) != want:
            _refuse(f"{ok}: {k} must be {want!r} (got {kv.get(k)!r})")
    for m in KNOWN_ALLOW:
        if f"allow_{m}" not in kv:
            _refuse(f"{ok}: allow_{m} must be written explicitly")
    if kv["allow_real_data"] != ("true" if real_data else "false"):
        _refuse(f"{ok}: allow_real_data={kv['allow_real_data']} inconsistent with QL_SD1_REAL_DATA={int(real_data)}")
    for k, v in kv.items():
        if k.startswith("allow_") and k not in ("allow_selftest", "allow_real_data") and v != "false":
            _refuse(f"{ok}: {k}={v}; every allow_* other than selftest/real_data must be false")
    now = _dt.datetime.now().astimezone()
    for k in ("signed_et", "expires_et"):
        v = kv.get(k, "")
        if not ISO_TZ.match(v):
            _refuse(f"{ok}: {k}={v!r} is not ISO8601 with a UTC offset")
    if _dt.datetime.fromisoformat(kv["expires_et"]) <= now:
        _refuse(f"{ok}: expired at {kv['expires_et']}")
    if _dt.datetime.fromisoformat(kv["signed_et"]) > now + _dt.timedelta(minutes=5):
        _refuse(f"{ok}: signed_et in the future")
    od = kv.get("out_dir", "")
    if od == "mkdtemp":
        out = Path(tempfile.mkdtemp(prefix="sd1_selftest_"))
    elif re.fullmatch(r"/tmp/[A-Za-z0-9._-]+", od):
        out = Path(od); out.mkdir(exist_ok=False)
    else:
        _refuse(f"{ok}: out_dir must be 'mkdtemp' or /tmp/<tag> (got {od!r})")
    r = out.resolve()
    if r == ROOT or ROOT in r.parents or "output" in r.parts:
        _refuse(f"out_dir {r} is inside the repo / output/")
    atexit.register(shutil.rmtree, str(r), True)
    return r


def _data_manifest_sha(files) -> str:
    """sha256 of `sha256sum`-style lines '<sha>  <repo-rel path>\n' sorted by path (= what Arch pins)."""
    import hashlib
    lines = []
    for f in sorted(files, key=lambda x: str(Path(x).resolve().relative_to(ROOT))):
        h = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        lines.append(f"{h}  {Path(f).resolve().relative_to(ROOT)}\n")
    return hashlib.sha256("".join(lines).encode()).hexdigest()


if not sys.flags.dont_write_bytecode:          # r3 (Arch P3-5): checked BEFORE the gate module is imported
    _refuse("run with PYTHONDONTWRITEBYTECODE=1 (no __pycache__ in the repo)")
sys.path.insert(0, str(ROOT / "scripts_eng"))
import ok_runner_pin as _PIN  # noqa: E402  (the gate itself is a pinned dep; still v1 c7805d9a)
_GATE = _PIN.enforce(__file__, [TEST_OK], modes=["selftest", "real_data"] if REAL_DATA else ["selftest"],
                     deps={k: ROOT / v for k, v in TEST_DEPS.items()})
OUT_DIR = _selftest_selfcheck(TEST_OK, REAL_DATA)
OK_KV = _PIN.parse_ok(TEST_OK)

# ---- gate passed: only now import the modules under test
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402  (exact-type exception checks, Arch ruling 2)

sys.path.insert(0, str(ROOT))
from quantlab.platform import execution_sd1 as E      # noqa: E402  (SD1 side engine; execution.py untouched)
from quantlab.platform import tradability as TB       # noqa: E402
from quantlab.platform import delist_accounting as DA  # noqa: E402

X, Y, Z = "600001.SH", "600002.SH", "600003.SH"
NO_EVENTS = pd.DataFrame(columns=list(DA.EVENT_COLUMNS))


def _dates(n):
    return pd.bdate_range("2024-01-02", periods=n)


def _panels(close: dict, n, *, open_=None, high=None, low=None, vol=None, lu=None, ld=None, susp=None):
    d = _dates(n)
    df = lambda m: pd.DataFrame({k: np.asarray(v, float) for k, v in m.items()}, index=d)
    C = df(close)
    O = df(open_) if open_ else C.copy()
    for k in close:
        if open_ and k not in open_:
            O[k] = C[k]
    V = df(vol) if vol else C.notna().astype(float) * 1e9
    V = V.reindex(columns=C.columns).fillna(C.notna().astype(float) * 1e9)
    V = V.where(C.notna())
    prev = C.ffill().shift(1)
    LU = df(lu).reindex(columns=C.columns) if lu else (prev * 1.1).round(2)
    LD = df(ld).reindex(columns=C.columns) if ld else (prev * 0.9).round(2)
    if lu:
        LU = LU.fillna((prev * 1.1).round(2))
    if ld:
        LD = LD.fillna((prev * 0.9).round(2))
    H = df(high).reindex(columns=C.columns).fillna(pd.concat([O, C]).groupby(level=0).max()) if high else pd.concat([O, C]).groupby(level=0).max()
    L = df(low).reindex(columns=C.columns).fillna(pd.concat([O, C]).groupby(level=0).min()) if low else pd.concat([O, C]).groupby(level=0).min()
    S = df(susp).astype(bool) if susp else None
    return E.ExecPanels(close=C, open=O, high=H.reindex(C.index), low=L.reindex(C.index), volume=V, amount=V * C,
                        limit_up=LU, limit_down=LD, suspended=S)


CFG0 = E.ExecConfig(fill="next_open", commission=0.0, min_commission=0.0, stamp_before=0.0, stamp_after=0.0,
                    lots=False, enforce_limits=True, corporate_actions=False, derive_nonstock_limits=False)
CFG1 = replace(CFG0, halt_policy="freeze_renorm", delist_policy="sd1", delist_force_sell_in_period=True)


def _run(p, sched, cfg, cash=1e6, ev=None, **kw):
    return E.run_weight_schedule(p, sched, initial_cash=cash, config=cfg, record_fills=True,
                                 delist_events=(NO_EVENTS if ev is None else ev) if cfg.delist_policy == "sd1" else ev, **kw)


def _ev(code, ltd, typ, **kw):
    r = {c: None for c in DA.EVENT_COLUMNS}
    r.update(code=code, instrument_id=code, last_trade_date=pd.Timestamp(ltd), type=typ, swap_ratio=np.nan,
             cash_per_share=np.nan, force_sell_from=pd.NaT)
    r.update(kw)
    return pd.DataFrame([r])


class T1HaltResumeGap(unittest.TestCase):
    """r3 diagnosis (selftest 02:26 ET failure; Eng SD1 r3 receipt): NOT an engine bug, in CFG0 or CFG1. The r2 fixture
    builds limit_down from the previous valid close (``_panels``: LD = C.ffill().shift(1) * 0.9), so on the resumption
    day d[6] LD = 10 * 0.9 = 9.0 while the open is 8.0. Under open_touch (spec 3.4 default; pristine execution.py
    373fed30 L754-755, execution_sd1 L913-914) an open at/below limit-down cannot sell -> the carried order
    (unfilled='carry') waits and fills at d[7] (LD = 8 * 0.9 = 7.2). A -20% open on a 10%-limit stock is only possible
    on a no-limit resumption session, which Data encodes as NaN limits. Both readings are now tested, per engine."""
    def setUp(self):
        nan = np.nan
        self.c = [10, 10, 10, nan, nan, nan, 8, 8]
        self.p = _panels({X: self.c}, 8, open_={X: [10, 10, 10, nan, nan, nan, 8, 8]})
        self.d = _dates(8)
        self.sched = {self.d[0]: {X: 1.0}, self.d[3]: {X: 0.5}}   # target cut ON the halt day d[3]

    def _no_limit_resume(self):
        p = _panels({X: self.c}, 8, open_={X: [10, 10, 10, np.nan, np.nan, np.nan, 8, 8]})
        p.limit_down.loc[self.d[6], X] = np.nan   # Data: no price limit on this resumption session
        p.limit_up.loc[self.d[6], X] = np.nan
        return p

    def _common(self, r):
        nav = r["nav"].to_numpy()
        self.assertEqual(nav[3], nav[2]); self.assertEqual(nav[4], nav[2]); self.assertEqual(nav[5], nav[2])
        self.assertAlmostEqual(nav[6] - nav[5], 1e5 * (8 - 10), places=6)   # full gap booked on the resumption day
        halt_days = {str(x.date()) for x in self.d[3:6]}
        self.assertFalse([f for f in r["fills"] if f["date"] in halt_days])

    def _sells(self, r, i):
        return [f for f in r["fills"] if f["date"] == str(self.d[i].date()) and f["side"] < 0 and f["code"] == X]

    def _resume_sell_executes(self, cfg):
        r = _run(self._no_limit_resume(), self.sched, cfg)
        self._common(r)
        s6 = self._sells(r, 6)
        self.assertEqual(len(s6), 1)
        self.assertEqual(s6[0]["qty"], 50000.0)          # 0.5 * NAV_sig(1e6) / mark(10) - 100000 held
        self.assertEqual(s6[0]["ref_price"], 8.0)        # sold at the actual resumption open, not the pre-halt close

    def _resume_limit_down_carries(self, cfg):
        r = _run(self.p, self.sched, cfg)
        self._common(r)
        self.assertEqual(self._sells(r, 6), [])
        d6 = str(self.d[6].date())
        self.assertTrue(any(e.get("reason") == "limit_down" and e.get("code") == X and e.get("date") == d6
                            for e in r["events"]))
        s7 = self._sells(r, 7)
        self.assertEqual(len(s7), 1); self.assertEqual(s7[0]["qty"], 50000.0)

    def test_cfg0_resume_sell_executes(self):        # SD0 semantics = pristine 373fed30
        self._resume_sell_executes(CFG0)

    def test_cfg1_resume_sell_executes(self):        # SD1 (freeze_renorm + sd1 delist)
        self._resume_sell_executes(CFG1)

    def test_cfg0_open_below_limit_down_carries(self):
        self._resume_limit_down_carries(CFG0)

    def test_cfg1_open_below_limit_down_carries(self):
        self._resume_limit_down_carries(CFG1)

    def test_weight_engine_same(self):
        P = pd.DataFrame({X: [1.0]}, index=self.d[:1])
        C = pd.DataFrame({X: self.c}, index=self.d, dtype=float)
        res = TB.weight_book_returns(P, TB.WBPanels(close=C, open=C.copy()), TB.WBPolicy(), delist_events=NO_EVENTS)
        r = res["ret"].to_numpy()
        self.assertTrue(np.all(r[3:6] == 0.0))
        self.assertAlmostEqual(r[6], -0.2, places=12)
        g = TB.weight_book_returns(P, TB.WBPanels(close=C), TB.WBPolicy(fill="close"), delist_events=NO_EVENTS)["gross"]
        self.assertAlmostEqual(float(g.iloc[6]), -0.2, places=12)   # ADG path keeps the resumption gap (spec 3.3)


def _t2(codes):
    x, y, z = codes
    nan = np.nan
    p = _panels({x: [10, 10, 10, nan, 10, 10], y: [10] * 6, z: [10] * 6}, 6, open_={x: [10, 10, 10, nan, 10, 10]})
    d = _dates(6)
    sched = {d[0]: {x: 0.5, y: 0.25, z: 0.25}, d[2]: {x: 0.2, y: 0.6, z: 0.2}}
    return p, sched, d


class T2FreezeRenorm(unittest.TestCase):
    def shares_after_day3(self, codes, cfg):
        p, s, d = _t2(codes)
        r = _run(p, s, cfg)
        aw = r["actual_weights"].iloc[3] * r["nav"].iloc[3] / 10.0
        return {c: round(float(aw[c])) for c in codes}, r

    def test_frozen_and_prorata(self):
        sh, r = self.shares_after_day3((X, Y, Z), CFG1)
        self.assertEqual(sh, {X: 50000, Y: 37500, Z: 12500})
        self.assertIn("RENORM", set(r["sd1_events"].type))
        self.assertIn("HALT_BLOCKED", set(r["sd1_events"].type))

    def test_rename_invariance(self):
        a, _ = self.shares_after_day3((X, Y, Z), CFG1)
        ren = ("600009.SH", "600001.SH", "600005.SH")
        b, _ = self.shares_after_day3(ren, CFG1)
        self.assertEqual([a[X], a[Y], a[Z]], [b[ren[0]], b[ren[1]], b[ren[2]]])

    def test_sd0_squeezes(self):   # documents the legacy P2 behaviour SD1 fixes
        sh, _ = self.shares_after_day3((X, Y, Z), CFG0)
        self.assertEqual(sh[X], 50000); self.assertNotEqual(sh[Y], 37500)


class T3BlockedBuyBudget(unittest.TestCase):
    def run_mode(self, mode):
        nan = np.nan
        p = _panels({X: [10, 10, 10, nan, 10, 10], Y: [10] * 6, Z: [10] * 6}, 6, open_={X: [10, 10, 10, nan, 10, 10]})
        d = _dates(6)
        s = {d[0]: {Y: 0.5, Z: 0.5}, d[2]: {X: 0.4, Y: 0.3, Z: 0.3}}
        return _run(p, s, replace(CFG1, blocked_buy_budget=mode))

    def test_renorm_vs_cash(self):
        # r3: the r2 gap 0.0238418579 = 1e6 * (0.4 - float32(1 - (float32(0.3) + float32(0.3)))) exactly: weights were
        # stored float32. SD1 weights are float64 now (SD0 stays float32 = pristine); tolerance stays absolute 1e-6.
        # Expected cash (spec 3.2, no costs, lots off): renorm -> 0 (blocked X budget re-spread over Y/Z);
        # cash -> NAV_open(d3) * w_X(0.4) (blocked X budget held as cash).
        for mode, want_y in (("renorm", 50000), ("cash", 30000)):
            r = self.run_mode(mode)
            aw = r["actual_weights"].iloc[3]; nav = r["nav"].iloc[3]
            self.assertEqual(r["actual_weights"].to_numpy().dtype, np.float64)
            nav_open = float(r["nav_open"].iloc[3])
            want_cash = 0.0 if mode == "renorm" else nav_open * 0.4
            self.assertEqual(round(float(aw[Y] * nav / 10)), want_y)
            self.assertEqual(round(float(aw[X] * nav / 10)), 0)
            self.assertAlmostEqual(float(nav * (1 - aw.sum())), want_cash, delta=1e-6)
            self.assertAlmostEqual(float(r["cash"]), want_cash, delta=1e-6)      # engine float64 ledger cash (end = d5)
            ev = r["sd1_events"]
            self.assertTrue(((ev.type == "HALT_BLOCKED") & (ev.code == X) & (ev.budget == mode)).any())

    def test_core_track_ruling(self):
        self.assertEqual(E.ExecConfig.strategy_v1_sd1(track="core").blocked_buy_budget, "cash")
        self.assertEqual(E.ExecConfig.strategy_v1_sd1(track="capacity_adv").blocked_buy_budget, "renorm")
        with self.assertRaises(TypeError):            # Arch P2-2: track is a required keyword
            E.ExecConfig.strategy_v1_sd1()
        for bad in (None, "", "  "):
            with self.assertRaises(ValueError):
                E.sd1_blocked_buy_budget(bad)

    def test_cash_days_recorded(self):              # A2: days the blocked budget stays cash (to next signal)
        r = self.run_mode("cash")
        ev = r["sd1_events"]
        h = ev[ev.type == "BLOCKED_BUDGET_CASH_HELD"]
        self.assertEqual(len(h), 1)
        self.assertEqual(int(h.sessions.iloc[0]), 6 - 3)                      # blocked at d[3] open, no later signal
        self.assertAlmostEqual(float(h.weight.iloc[0]), 0.4, places=12)
        self.assertEqual(r["sd1_summary"]["blocked_budget_cash_held_sessions"], 3)
        rn = ev[ev.type == "RENORM"]
        self.assertTrue((rn.pricing == "exec_day_open").all())               # A3 disclosed in the event row


class T4LimitPolicies(unittest.TestCase):
    def run_case(self, one_price, policy):
        n = 6; d = _dates(n)
        if one_price:
            o, h, l, c = 9.0, 9.0, 9.0, 9.0
        else:
            o, h, l, c = 9.0, 9.8, 9.0, 9.5
        p = _panels({X: [10, 10, 10, c, c, c]}, n, open_={X: [10, 10, 10, o, c, c]},
                    high={X: [10, 10, 10, h, c, c]}, low={X: [10, 10, 10, l, c, c]})
        r = _run(p, {d[0]: {X: 1.0}, d[2]: {}}, replace(CFG0, limit_policy=policy))
        return [f for f in r["fills"] if f["date"] == str(d[3].date()) and f["side"] < 0]

    def test_open_board(self):
        self.assertFalse(self.run_case(False, "open_touch"))
        f = self.run_case(False, "one_price_only")
        self.assertTrue(f); self.assertEqual(f[0]["price"], 9.0)

    def test_one_price_board(self):
        self.assertFalse(self.run_case(True, "open_touch"))
        self.assertFalse(self.run_case(True, "one_price_only"))


class T5ForcedPeriod(unittest.TestCase):
    def test_sell_on_first_unlocked_open(self):
        n = 10; d = _dates(n)
        c = [10, 10, 10, 9.0, 8.1, 7.6, 7.6, 7.6, 7.6, np.nan]
        o = [10, 10, 10, 9.0, 8.1, 7.5, 7.6, 7.6, 7.6, np.nan]
        p = _panels({X: c}, n, open_={X: o}, ld={X: [np.nan, 9, 9, 9.0, 8.1, 7.29, 6.84, 6.84, 6.84, np.nan]})
        ev = _ev(X, d[8], "FORCED_PERIOD", period_start=d[3], force_sell_from=d[3])
        r = _run(p, {d[0]: {X: 1.0}}, CFG1, ev=ev)
        sells = [f for f in r["fills"] if f["side"] < 0]
        self.assertEqual(len(sells), 1)
        self.assertEqual(sells[0]["date"], str(d[5].date())); self.assertEqual(sells[0]["price"], 7.5)
        self.assertNotEqual(sells[0]["price"], 10.0)
        self.assertIn("DELIST_SOLD_IN_PERIOD", set(r["sd1_events"].type))
        self.assertEqual(r["final_shares"].get(X, 0.0), 0.0)


class T6ForcedNoPeriod(unittest.TestCase):
    def test_writeoff_and_sensitivity(self):
        n = 8; d = _dates(n); nan = np.nan
        c = [10, 10, 9.0, 8.1, 7.29, 6.56, nan, nan]
        p = _panels({X: c}, n, open_={X: [10, 10, 9.0, 8.1, 7.29, 6.56, nan, nan]},
                    high={X: [10, 10, 9.0, 8.1, 7.29, 6.56, nan, nan]}, low={X: [10, 10, 9.0, 8.1, 7.29, 6.56, nan, nan]})
        ev = _ev(X, d[5], "FORCED_NO_PERIOD")
        res = E.run_delist_sensitivity(p, {d[0]: {X: 1.0}}, delist_events=ev, initial_cash=1e6, config=CFG1)
        self.assertEqual(set(res), {0.0, 0.3, 0.7, "unknown_last_close_cash"})
        self.assertEqual(res[0.0]["sd1_summary"]["basis"], "main")
        for rec in (0.0, 0.3, 0.7):
            r = res[rec]
            nav = r["nav"].to_numpy()
            self.assertAlmostEqual(nav[5] - nav[6], 1e5 * 6.56 * (1 - rec), places=4)
            self.assertIn("DELIST_WRITEOFF", set(r["sd1_events"].type))
            if rec:
                self.assertEqual(r["sd1_summary"]["basis"], "sensitivity_disclosure_only")
        r0 = _run(p, {d[0]: {X: 1.0}}, CFG0)
        self.assertAlmostEqual(r0["nav"].iloc[6], 1e5 * 6.56, places=4)   # SD0 legacy last-mark (optimistic)


class T7MergerSwap(unittest.TestCase):
    def setUp(self):
        n = 8; self.d = d = _dates(n); nan = np.nan
        self.p = _panels({X: [10, 10, 10, 10, nan, nan, nan, nan], Y: [20] * n}, n)
        self.cfg = replace(CFG1, lots=True)

    def test_swap(self):
        ev = _ev(X, self.d[3], "MERGER_SWAP", swap_ratio=0.62, acquirer=Y)
        r = _run(self.p, {self.d[0]: {X: 1.0}}, self.cfg, cash=1_001_000.0, ev=ev)
        self.assertEqual(r["final_shares"].get(Y), 62000.0)                   # 100100 x 0.62 = 62062 -> 62000 + 62 odd
        self.assertAlmostEqual(r["nav"].iloc[5], 62000 * 20 + 62 * 20, places=4)
        e = r["sd1_events"]; self.assertIn("DELIST_MA_CONVERT", set(e.type))

    def test_missing_table_fallback(self):
        ev = _ev(X, self.d[3], "MERGER_SWAP")
        r = _run(self.p, {self.d[0]: {X: 1.0}}, self.cfg, cash=1_001_000.0, ev=ev)
        e = r["sd1_events"]
        self.assertTrue(((e.type == "DELIST_FALLBACK") & (e.flag == "MA_FALLBACK_LAST_CLOSE")).any())
        self.assertAlmostEqual(r["cash"], 100100 * 10.0, places=4)


class T8CashOut(unittest.TestCase):
    def test_cash_out_and_fallback(self):
        n = 6; d = _dates(n); nan = np.nan
        p = _panels({X: [10, 10, 10, nan, nan, nan]}, n)
        r = _run(p, {d[0]: {X: 1.0}}, CFG1, ev=_ev(X, d[2], "CASH_OUT", cash_per_share=12.0))
        self.assertAlmostEqual(r["cash"], 1e5 * 12.0, places=4)
        self.assertIn("DELIST_CASH_OUT", set(r["sd1_events"].type))
        r2 = _run(p, {d[0]: {X: 1.0}}, CFG1, ev=_ev(X, d[2], "CASH_OUT"))
        self.assertTrue(((r2["sd1_events"].type == "DELIST_FALLBACK") & (r2["sd1_events"].flag == "MA_FALLBACK_LAST_CLOSE")).any())
        self.assertAlmostEqual(r2["cash"], 1e5 * 10.0, places=4)


PRISTINE_SHA256 = "373fed309f055888e83572d3fbef8f5b5052ebfcb208307962a272bca6fc486c"


def _head_engine():
    """The live, untouched quantlab/platform/execution.py (must still be sha256 373fed30…486c = git HEAD e7b240d)."""
    import hashlib
    path = ROOT / "quantlab/platform/execution.py"
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != PRISTINE_SHA256:
        raise RuntimeError(f"execution.py sha256 {got} != pristine {PRISTINE_SHA256}; parity baseline invalid")
    from quantlab.platform import execution as H
    want = str(ROOT / "quantlab/platform/execution.py")
    if H.run_weight_schedule.__code__.co_filename != want:      # the reference must be the REAL execution.py
        raise RuntimeError(f"reference engine loaded from {H.run_weight_schedule.__code__.co_filename}, not {want}")
    if E.run_weight_schedule.__code__.co_filename != str(ROOT / "quantlab/platform/execution_sd1.py"):
        raise RuntimeError("SD1 side engine not loaded from execution_sd1.py")
    return H


def _fixed_sample(seed=20261018, n=80):
    rng = np.random.default_rng(seed)
    d = _dates(n); codes = ["600001.SH", "000002.SZ", "688003.SH", "300004.SZ", "510300.SH"]
    C = pd.DataFrame(np.round(10 * np.exp(np.cumsum(rng.normal(0, 0.025, (n, len(codes))), axis=0)), 2), index=d, columns=codes)
    C.iloc[20:24, 1] = np.nan                                      # interior halt
    C.iloc[70:, 3] = np.nan                                        # trailing NaN (delist-like tail)
    O = (C.shift(1) * (1 + rng.normal(0, 0.01, C.shape))).round(2).where(C.notna()); O.iloc[0] = C.iloc[0]
    prev = C.ffill().shift(1)
    O.iloc[30, 0] = round(prev.iloc[30, 0] * 1.1, 2); O.iloc[40, 2] = round(prev.iloc[40, 2] * 0.8, 2)   # limit touches
    V = pd.DataFrame(rng.uniform(1e5, 1e6, C.shape), index=d, columns=codes).where(C.notna())
    sus = C.isna()
    p = E.ExecPanels(close=C, open=O, high=pd.concat([O, C]).groupby(level=0).max(), low=pd.concat([O, C]).groupby(level=0).min(),
                     volume=V, amount=V * C, limit_up=(prev * 1.1).round(2), limit_down=(prev * 0.9).round(2), suspended=sus)
    sched = {}
    for t in range(0, n - 1, 5):
        w = rng.dirichlet(np.ones(len(codes))) * rng.uniform(0.8, 1.0)
        sched[d[t]] = {c: float(x) for c, x in zip(codes, w)}
    return p, sched


class T9LegacyBitIdentity(unittest.TestCase):
    def test_sd0_equals_head(self):
        H = _head_engine()
        p, sched = _fixed_sample()
        cfgs = [("strategy_v1", {}, dict(impact_k=1.0)), ("strategy_v1", {}, dict(impact_k=0.0, participation_cap=None)),
                ("strategy_v1", {}, dict(order_rounding="delta")), ("strategy_v1", {}, dict(unfilled="drop")),
                ("plain", dict(fill="close"), {}), ("plain", dict(fill="next_vwap"), {}), ("plain", {}, {})]
        for kind, plain, over in cfgs:
            for cash in (600_000.0, 1_000_000.0):
                new_cfg = E.ExecConfig.strategy_v1(**over) if kind == "strategy_v1" else E.ExecConfig(**plain)
                old_cfg = H.ExecConfig.strategy_v1(**over) if kind == "strategy_v1" else H.ExecConfig(**plain)
                self.assertEqual(new_cfg.engine_version, "exec_SD0")
                pn = E.ExecPanels(**{k: getattr(p, k) for k in H.ExecPanels.__dataclass_fields__})
                po = H.ExecPanels(**{k: getattr(p, k) for k in H.ExecPanels.__dataclass_fields__})
                a = E.run_weight_schedule(pn, sched, initial_cash=cash, config=new_cfg, record_fills=True)
                b = H.run_weight_schedule(po, sched, initial_cash=cash, config=old_cfg, record_fills=True)
                self.assertTrue(np.array_equal(a["nav"].to_numpy(), b["nav"].to_numpy()), (kind, plain, over, cash))
                self.assertTrue(np.array_equal(a["nav_open"].to_numpy(), b["nav_open"].to_numpy()))
                self.assertEqual(a["cash"], b["cash"]); self.assertEqual(a["costs"], b["costs"])
                self.assertEqual(a["final_shares"], b["final_shares"]); self.assertEqual(a["fills"], b["fills"])
                self.assertEqual(a["events"], b["events"])
                self.assertTrue(np.array_equal(a["actual_weights"].to_numpy(), b["actual_weights"].to_numpy()))
                self.assertEqual(a["actual_weights"].to_numpy().dtype, b["actual_weights"].to_numpy().dtype)   # r3
                self.assertEqual(a["target_weights"].to_numpy().dtype, b["target_weights"].to_numpy().dtype)
                self.assertNotIn("sd1_events", a)


PLANTED = "from quantlab.platform.delist_accounting import load_delist_events\nload_delist_events(source='src_events_v1')\n"
PLANTED_NOSRC = "from quantlab.platform.delist_accounting import load_delist_events\nload_delist_events()\n"
FAKE_CALLERS = ("research/_sd1_planted_strategy.py", "quantlab/strategy/_planted.py", "scripts/_optimizer_planted.py")


def _no_real_sources():
    """Point every delist source at a non-existent file under OUT_DIR, so a broken guard cannot read real data
    (it would raise FileNotFoundError, which the exact-type checks below reject)."""
    saved = dict(DA.DELIST_SOURCES)
    for k in list(DA.DELIST_SOURCES):
        DA.DELIST_SOURCES[k] = OUT_DIR / f"_absent_{k}.parquet"
    return saved


class T10PitGuard(unittest.TestCase):
    def setUp(self):
        self.saved = _no_real_sources()

    def tearDown(self):
        DA.DELIST_SOURCES.clear(); DA.DELIST_SOURCES.update(self.saved)

    def test_strategy_caller_raises(self):
        # r3/r3.2: the planted strategy call passes a valid source, so only the PIT guard can stop it -> exactly
        # StrategyLayerDelistAccess (a PermissionError subclass; Arch 03:07 ruling (a))
        for fake in FAKE_CALLERS:
            with pytest.raises(PermissionError) as ei:
                exec(compile(PLANTED, str(ROOT / fake), "exec"), {})
            self.assertIs(type(ei.value), DA.StrategyLayerDelistAccess)  # r3.1a: Arch 03:07 ruling (a)
            self.assertTrue(issubclass(DA.StrategyLayerDelistAccess, PermissionError))
            self.assertFalse(issubclass(DA.StrategyLayerDelistAccess, TypeError))

    def test_no_source_is_type_error(self):
        # r3: a call without source fails at argument binding -> exactly TypeError (for strategy and allowed callers)
        for fake in FAKE_CALLERS + ("tests/test_sd1_suspend_delist.py",):
            with pytest.raises(TypeError) as ei:
                exec(compile(PLANTED_NOSRC, str(ROOT / fake), "exec"), {})
            self.assertIs(type(ei.value), TypeError)
            self.assertIn("source", str(ei.value))

    def test_allowed_caller(self):
        self.assertEqual(DA.guard_accounting_caller(), "tests/test_sd1_suspend_delist.py")

    def test_static_check_catches_planted(self):
        sys.path.insert(0, str(ROOT / "scripts_eng"))
        import sd1_pit_static_check as SC
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:        # only under the .ok out_dir
            f = Path(td) / "planted.py"
            f.write_text('import pandas as pd\nx = pd.read_parquet("data/v2/ref/stock_delisted.parquet")\nb.delist_date\n')
            hits = SC.scan([f], forced_scope=True)
        self.assertEqual(len([h for h in hits if h["status"] == "VIOLATION"]), 2)

    def test_static_check_pinned_scope(self):
        # r3.1 (Arch 2b8f81c9 §6.1-2): ONLY this file's pinned deps + the paper import closure (sha-verified), so the
        # result cannot change when other agents edit other files. The full-repo scan is a disclosure report, not a gate.
        closure = ROOT / TEST_DEPS["paper_import_closure"]
        # r3.2 (Arch e2e288bc P3-2): every --files item carries its .ok sha and is re-hashed inside the scan, so a change
        # between the import-time gate and this subprocess is caught too
        files = sorted({f"{ROOT / v}={OK_KV['dep_sha256_' + k]}" for k, v in TEST_DEPS.items() if v.endswith(".py")}
                       | {f"{Path(__file__).resolve()}={OK_KV['runner_sha256_test_sd1_suspend_delist']}"})
        r = subprocess.run([sys.executable, str(ROOT / "scripts_eng/sd1_pit_static_check.py"), "--mode", "pinned",
                            "--closure", str(closure), "--closure-sha256", OK_KV["dep_sha256_paper_import_closure"],
                            "--require-file-sha", "--files", *files], capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])
        rep = json.loads(r.stdout)
        self.assertEqual(rep["mode"], "pinned")
        self.assertTrue(rep["closure_ok"], rep.get("closure_mismatch"))
        self.assertEqual(rep["n_closure"], 156)
        self.assertTrue(rep["files_ok"], rep.get("files_mismatch"))
        self.assertEqual(rep["n_files_sha_checked"], len(files))
        self.assertEqual(rep["n_violations"], 0)
        self.assertEqual(rep["n_allowed_func"], 0)        # no whitelisted research leaf file is in the pinned scope
        # r3.2 (Arch e2e288bc P3-1): 162 candidates, 77 actually scanned (inside SCOPE, not WHITELISTed); the closure's
        # 16 research/ files ARE scanned and give 0 hits (r3.1 wording "no research file scanned" was wrong)
        self.assertEqual(rep["n_files"], 162)
        self.assertEqual(rep["n_scanned"], 77)
        self.assertEqual(rep["n_scanned_research"], 16)
        research_hits = [h for h in rep["hits"] if h["path"].startswith("research/")]
        self.assertEqual(research_hits, [])

    def test_static_check_cli_and_file_sha(self):
        # r3.2 (Arch e2e288bc P3-4): --mode and --paths are mutually exclusive, bare --paths is an error;
        # (P3-2): a PATH=SHA256 item that does not match -> files_ok=False (early closure-sha return: no repo scan)
        sys.path.insert(0, str(ROOT / "scripts_eng"))
        import sd1_pit_static_check as SC
        import contextlib, io
        for argv in (["--mode", "pinned", "--paths", "x.py"], ["--paths"]):
            with contextlib.redirect_stderr(io.StringIO()), pytest.raises(SystemExit) as ei:
                SC.main(argv)
            self.assertEqual(ei.value.code, 2)
        self.assertEqual(SC._split_file_arg("a/b.py=" + "ab" * 32), ("a/b.py", "ab" * 32))
        self.assertEqual(SC._split_file_arg("a/b=c.py"), ("a/b=c.py", None))
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            f = Path(td) / "x.py"; f.write_text("x = 1\n")
            cl = Path(td) / "closure.json"; cl.write_text("[]")
            r = SC.pinned_scope([f"{f}={'0' * 64}", str(f)], cl, "0" * 64, require_file_sha=True)
        self.assertFalse(r["closure_ok"])
        self.assertFalse(r["files_ok"])
        self.assertEqual(r["n_files_sha_checked"], 1)
        self.assertEqual(len(r["files_mismatch"]), 2)    # wrong sha + missing sha under --require-file-sha

    def test_static_check_function_whitelist(self):
        # r3.1 (Arch 2b8f81c9 §6.1-3): path + function name, never sha; a hit outside that function in the same file
        # stays a VIOLATION. Synthetic content treated as the whitelisted path (no real research file is read).
        sys.path.insert(0, str(ROOT / "scripts_eng"))
        import sd1_pit_static_check as SC
        rel = "research/g1g5_imax_intraday_alpha.py"
        self.assertIn((rel, "pool_benchmarks"), SC.FUNC_WHITELIST)
        self.assertIn("主 Agent 02:44 裁定", SC.FUNC_WHITELIST[(rel, "pool_benchmarks")])
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            f = Path(td) / "leaf.py"
            f.write_text("def pool_benchmarks(dl):\n    def _inner():\n        return dl.delist_date\n"
                         "    return dl.delist_date, _inner\n\n"
                         "def evaluate(dl):\n    return dict(cagr_cut_delist_date=1)\n\nX = 'delist_date'\n")
            hits = SC.scan([f], rel_as={str(f): rel})
            other = SC.scan([f], rel_as={str(f): "research/some_other_leaf.py"})
            forced = SC.scan([f], forced_scope=True, rel_as={str(f): rel})
        st = {(h["line"], h["status"], h["function"]) for h in hits}
        self.assertEqual(st, {(3, "ALLOWED_FUNC", "_inner"), (4, "ALLOWED_FUNC", "pool_benchmarks"),
                              (7, "VIOLATION", "evaluate"), (9, "VIOLATION", "<module>")})
        self.assertEqual([h["status"] for h in other], ["VIOLATION"] * 4)
        self.assertEqual([h["status"] for h in forced], ["VIOLATION"] * 4)


class T11OptimizeFlag(unittest.TestCase):
    def test_guards_under_python_O(self):
        code = "\n".join([
            "import sys", f"sys.path.insert(0, {str(ROOT)!r})",
            "print('debug', __debug__)",
            "from quantlab.platform import delist_accounting as DA",
            f"for _k in list(DA.DELIST_SOURCES): DA.DELIST_SOURCES[_k] = __import__('pathlib').Path({str(OUT_DIR)!r}) / ('_absent_' + _k)",
            "try:",
            f"    exec(compile({PLANTED!r}, {str(ROOT / 'research/_sd1_planted_strategy.py')!r}, 'exec'), {{}})",
            "    print('GUARD_NO_RAISE')",
            "except BaseException as e:",
            "    print('GUARD_EXC', type(e).__name__)",
            "try:",
            f"    exec(compile({PLANTED_NOSRC!r}, {str(ROOT / 'research/_sd1_planted_strategy.py')!r}, 'exec'), {{}})",
            "    print('NOSRC_NO_RAISE')",
            "except BaseException as e:",
            "    print('NOSRC_EXC', type(e).__name__)",
            "from quantlab.platform import execution_sd1 as E",
            "try:",
            "    E.ExecConfig(halt_policy='bogus'); print('CFG_NO_RAISE')",
            "except ValueError:",
            "    print('CFG_RAISED')",
            "import pandas as pd",
            "try:",
            "    E.run_weight_schedule(E.ExecPanels(close=pd.DataFrame({'600001.SH': [1.0]}, index=pd.bdate_range('2024-01-02', periods=1))), {}, config=E.ExecConfig(delist_policy='sd1'))",
            "    print('DL_NO_RAISE')",
            "except ValueError:",
            "    print('DL_RAISED')",
            ""])
        out = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True, cwd=str(ROOT),
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")).stdout
        self.assertIn("debug False", out)
        lines = out.splitlines()
        self.assertIn("GUARD_EXC StrategyLayerDelistAccess", lines)     # exact type names (Arch ruling 2)
        self.assertIn("NOSRC_EXC TypeError", lines)
        for k in ("CFG_RAISED", "DL_RAISED"):
            self.assertIn(k, lines)


class T12WeightEngineDelistTail(unittest.TestCase):
    def test_tail_not_zero_return(self):
        n = 7; d = _dates(n); nan = np.nan
        C = pd.DataFrame({X: [10, 10, 10, 10, 10, nan, nan]}, index=d, dtype=float)
        P = pd.DataFrame({X: [0.5]}, index=d[:1])
        ev = _ev(X, d[4], "FORCED_NO_PERIOD")
        for rec in (0.0, 0.3, 0.7):
            res = TB.weight_book_returns(P, TB.WBPanels(close=C, open=C.copy()), TB.WBPolicy(delist_forced_recovery=rec),
                                         delist_events=ev)
            self.assertAlmostEqual(float(res["ret"].iloc[5]), -0.5 * (1 - rec), places=12)
            self.assertTrue(np.all(res["ret"].iloc[6:].to_numpy() == 0.0))
            self.assertIn("DELIST_WRITEOFF", set(res["events"].type))
        res = TB.weight_book_returns(P, TB.WBPanels(close=C, open=C.copy()), TB.WBPolicy(), delist_events=NO_EVENTS)
        self.assertEqual(res["flags"][0]["flag"], "TAIL_NAN_NOT_IN_TABLE")   # no inference without the table

    def test_requires_table(self):
        C = pd.DataFrame({X: [10.0, 10.0]}, index=_dates(2))
        with self.assertRaises(ValueError):
            TB.weight_book_returns(C * 0, TB.WBPanels(close=C), TB.WBPolicy())


def check_resume_rows(panel: pd.DataFrame, suspend_d: pd.DataFrame, traded: pd.DataFrame, calendar) -> list:
    """T13 checker: for every full-day S run in suspend_d, the next session with trading must have a panel row.
    panel/traded: columns date, instrument; suspend_d: ts_code, trade_date (Timestamp), suspend_type, suspend_timing."""
    cal = pd.DatetimeIndex(sorted(calendar))
    have = set(zip(pd.to_datetime(panel.date), panel.instrument.astype(str)))
    trd = set(zip(pd.to_datetime(traded.date), traded.instrument.astype(str)))
    s = suspend_d[(suspend_d.suspend_type == "S") & suspend_d.suspend_timing.isna()]
    missing = []
    for code, g in s.groupby("ts_code"):
        days = set(pd.to_datetime(g.trade_date))
        for dd in sorted(days):
            k = cal.searchsorted(dd) + 1
            if k >= len(cal) or cal[k] in days:
                continue
            nxt = cal[k]
            if (nxt, str(code)) in trd and (nxt, str(code)) not in have:
                missing.append((str(code), str(nxt.date())))
    return missing


class T13CsPanelResumeRows(unittest.TestCase):
    def test_checker_synthetic(self):
        cal = _dates(10)
        sd = pd.DataFrame(dict(ts_code=[X, X, X], trade_date=cal[2:5], suspend_type="S", suspend_timing=None))
        traded = pd.DataFrame(dict(date=[cal[5], cal[6]], instrument=[X, X]))
        v1 = pd.DataFrame(dict(date=[cal[0], cal[1], cal[6]], instrument=X))       # D-1: resumption row missing
        v2 = pd.DataFrame(dict(date=[cal[0], cal[1], cal[5], cal[6]], instrument=X))
        self.assertEqual(check_resume_rows(v1, sd, traded, cal), [(X, str(cal[5].date()))])
        self.assertEqual(check_resume_rows(v2, sd, traded, cal), [])

    @unittest.skipUnless(REAL_DATA, "real-data T13 needs QL_SD1_REAL_DATA=1 + allow_real_data=true + pinned data manifest")
    def test_cs_panel_v2_real(self):
        """P1-7: the traded set comes from an INDEPENDENT source (suspend_d R = resumption records), not the panel.
        Every file read is pinned: .ok data_manifest_sha256_t13 = sha256 of sorted `sha256sum` lines (see receipt)."""
        import glob
        pc = ROOT / "output/ai_factory/panel_cache"
        panels = sorted(glob.glob(str(pc / "cs_panel_v2_*.parquet")))
        sds = sorted(glob.glob(str(ROOT / "data/v2/tushare_raw/suspend_d/*.parquet")))
        self.assertTrue(panels and sds, "cs_panel_v2 / suspend_d missing")
        got = _data_manifest_sha(panels + sds)
        self.assertEqual(OK_KV.get("data_manifest_sha256_t13"), got, "real data differs from the pinned manifest")
        miss_total = 0
        for f in panels:                                                 # yearly chunks (RSS)
            y = int(Path(f).stem.rsplit("_", 1)[1])
            files = [x for x in sds if Path(x).name.startswith(str(y))]
            if not files:
                continue
            panel = pd.read_parquet(f, columns=["date", "instrument"])
            sd = pd.concat([pd.read_parquet(x, columns=["ts_code", "trade_date", "suspend_type", "suspend_timing"]) for x in files])
            sd["trade_date"] = pd.to_datetime(sd.trade_date.astype(str), format="%Y%m%d")
            sd["suspend_timing"] = sd.suspend_timing.replace("", None)
            rr = sd[sd.suspend_type == "R"]
            traded = pd.DataFrame(dict(date=rr.trade_date, instrument=rr.ts_code.astype(str)))   # independent of the panel
            cal = sorted(set(pd.to_datetime(panel.date)) | set(traded.date))
            miss_total += len(check_resume_rows(panel, sd, traded, cal))
            del panel, sd, rr, traded
        self.assertEqual(miss_total, 0)

    def test_checker_not_tautological(self):
        """P1-7: with an independent traded set the checker CAN fail (guards against traded = panel)."""
        cal = _dates(8)
        sd = pd.DataFrame(dict(ts_code=[X, X], trade_date=cal[2:4], suspend_type="S", suspend_timing=None))
        panel = pd.DataFrame(dict(date=[cal[0], cal[1], cal[5]], instrument=X))
        self.assertEqual(check_resume_rows(panel, sd, pd.DataFrame(dict(date=[cal[4]], instrument=[X])), cal),
                         [(X, str(cal[4].date()))])
        self.assertEqual(check_resume_rows(panel, sd, panel, cal), [])   # traded = panel would always pass


# ------------------------------------------------------------------ E-1 (主 Agent final 01:53 ET)
def _wo_case(kind_a, w_a, kind_b, w_b):
    """Two names delisting at d[4] (A: kind_a weight w_a, B: kind_b weight w_b), rest cash; main engine, no lots."""
    n = 8; d = _dates(n); nan = np.nan
    A, B = X, Y
    p = _panels({A: [10, 10, 10, 10, 10, nan, nan, nan], B: [10, 10, 10, 10, 10, nan, nan, nan], Z: [10] * n}, n)
    ev = pd.concat([_ev(A, d[4], kind_a), _ev(B, d[4], kind_b)], ignore_index=True)
    sched = {d[0]: {A: w_a, B: w_b, Z: 1.0 - w_a - w_b}}
    return p, sched, ev, d


class T14E1WriteoffCategories(unittest.TestCase):
    def test_unknown_separate_category_and_amounts(self):
        p, s, ev, d = _wo_case("FORCED_NO_PERIOD", 0.004, "UNKNOWN", 0.003)
        r = _run(p, s, CFG1, cash=1e6, ev=ev)
        e = r["sd1_events"]
        self.assertEqual(set(e[e.code == X].type) & {"DELIST_WRITEOFF", "DELIST_WRITEOFF_UNKNOWN"}, {"DELIST_WRITEOFF"})
        self.assertEqual(set(e[e.code == Y].type) & {"DELIST_WRITEOFF", "DELIST_WRITEOFF_UNKNOWN"}, {"DELIST_WRITEOFF_UNKNOWN"})
        sm = r["sd1_summary"]
        self.assertEqual((sm["n_writeoff_announced"], sm["n_writeoff_unknown"]), (1, 1))
        self.assertAlmostEqual(sm["writeoff_value_announced"], 400 * 10.0, places=6)
        self.assertAlmostEqual(sm["writeoff_value_unknown"], 300 * 10.0, places=6)
        self.assertAlmostEqual(sm["writeoff_weight_announced"], 0.004, places=6)
        self.assertAlmostEqual(sm["writeoff_weight_unknown"], 0.003, places=6)
        self.assertAlmostEqual(sm["combined_writeoff_weight"], 0.007, places=6)
        self.assertFalse(sm["g2_triggered"])
        g = e[e.type == "G2_CHECK"]
        self.assertEqual(len(g), 1); self.assertAlmostEqual(float(g.weight.iloc[0]), 0.007, places=6)

    def test_g2_rules(self):
        for ka, wa, kb, wb, want in (("FORCED_NO_PERIOD", 0.005, "UNKNOWN", 0.006, True),     # combined >= 1%
                                     ("FORCED_NO_PERIOD", 0.012, "CASH_OUT", 0.001, True),    # announced alone >= 1%
                                     ("UNKNOWN", 0.008, "UNKNOWN", 0.007, False),             # UNKNOWN alone: no G2
                                     ("FORCED_NO_PERIOD", 0.004, "UNKNOWN", 0.005, False)):   # combined < 1%
            p, s, ev, d = _wo_case(ka, wa, kb, wb)
            sm = _run(p, s, CFG1, cash=1e6, ev=ev)["sd1_summary"]
            self.assertEqual(sm["g2_triggered"], want, (ka, wa, kb, wb, sm))
        p, s, ev, d = _wo_case("UNKNOWN", 0.008, "UNKNOWN", 0.007)
        self.assertTrue(_run(p, s, CFG1, cash=1e6, ev=ev)["sd1_summary"]["g2_if_unknown_alone_counted"])

    def test_last_close_comparison_disclosure(self):
        p, s, ev, d = _wo_case("FORCED_NO_PERIOD", 0.004, "UNKNOWN", 0.003)
        res = E.run_delist_sensitivity(p, s, delist_events=ev, initial_cash=1e6, config=CFG1)
        lc = res["unknown_last_close_cash"]
        self.assertEqual(lc["sd1_summary"]["basis"], "sensitivity_disclosure_only")
        self.assertIn("DELIST_UNKNOWN_LAST_CLOSE_CASH", set(lc["sd1_events"].type))
        self.assertEqual(lc["sd1_summary"]["n_writeoff_unknown"], 0)
        self.assertAlmostEqual(lc["nav"].iloc[-1] - res[0.0]["nav"].iloc[-1], 300 * 10.0, places=4)

    def test_weight_engine_same_categories(self):
        n = 7; d = _dates(n); nan = np.nan
        C = pd.DataFrame({X: [10, 10, 10, 10, 10, nan, nan], Y: [10, 10, 10, 10, 10, nan, nan], Z: [10.0] * n}, index=d)
        P = pd.DataFrame({X: [0.006], Y: [0.005], Z: [0.989]}, index=d[:1])
        ev = pd.concat([_ev(X, d[4], "FORCED_NO_PERIOD"), _ev(Y, d[4], "UNKNOWN")], ignore_index=True)
        out = TB.run_wb_delist_sensitivity(P, TB.WBPanels(close=C, open=C.copy()), TB.WBPolicy(), delist_events=ev)
        sm = out[0.0]["summary"]
        self.assertEqual((sm["n_writeoff_announced"], sm["n_writeoff_unknown"]), (1, 1))
        self.assertAlmostEqual(sm["combined_writeoff_weight"], 0.011, places=9)
        self.assertTrue(sm["g2_triggered"])
        self.assertIn("DELIST_WRITEOFF_UNKNOWN", set(out[0.0]["events"].type))
        self.assertIn("DELIST_UNKNOWN_LAST_CLOSE_CASH", set(out["unknown_last_close_cash"]["events"].type))
        self.assertEqual(set(out), {0.0, 0.3, 0.7, "unknown_last_close_cash"})


# ------------------------------------------------------------------ P1-5 needs_manual_source never force-sells
class T15NeedsManualSource(unittest.TestCase):
    def _case(self, manual):
        n = 10; d = _dates(n)
        p = _panels({X: [10.0] * 9 + [np.nan]}, n)
        ev = _ev(X, d[8], "FORCED_PERIOD", period_start=d[3], force_sell_from=d[3], needs_manual_source=manual)
        return p, ev, d

    def test_engines_ignore_force_sell(self):
        for manual, want_sells in ((True, 0), (False, 1)):
            p, ev, d = self._case(manual)
            r = _run(p, {d[0]: {X: 1.0}}, CFG1, ev=ev)
            self.assertEqual(len([f for f in r["fills"] if f["side"] < 0]), want_sells, manual)
            C = p.close
            w = TB.weight_book_returns(pd.DataFrame({X: [1.0]}, index=d[:1]), TB.WBPanels(close=C, open=C.copy()),
                                       TB.WBPolicy(), delist_events=ev)
            self.assertEqual("DELIST_SOLD_IN_PERIOD" in set(w["events"].type), not manual)

    def test_loader_clears_force_sell_from(self):
        """Synthetic v2 table in OUT_DIR (no real data): 002509-like row with needs_manual_source=False keeps its
        2020-06-04 period start (forced sell correct, per Data); a True row gets NaT + NEEDS_MANUAL_SOURCE_NO_FORCE_SELL."""
        f = OUT_DIR / "synthetic_table_v2.parquet"
        pd.DataFrame(dict(ts_code=["002509.SZ", "600999.SH"], instrument_id=["sz.002509", "sh.600999"],
                          last_trade_date=["2020-07-01", "2020-07-01"], delist_reason_category_v2=["强制退市-财务", "强制退市-财务"],
                          delist_period_start=["20200604", "20200604"], entered_delisting_period_v2=[True, True],
                          face_value_delist_flag=[False, False], needs_manual_source=[False, True],
                          last_close=[1.0, 1.0])).to_parquet(f, index=False)
        saved = (dict(DA.DELIST_SOURCES), DA.NAMECHANGE, DA.CONSIDERATION)
        try:
            DA.DELIST_SOURCES["src_table_v2"] = f
            DA.NAMECHANGE = OUT_DIR / "absent_namechange.parquet"; DA.CONSIDERATION = OUT_DIR / "absent_consideration.parquet"
            ev = DA.load_delist_events(source="src_table_v2")
        finally:
            DA.DELIST_SOURCES.clear(); DA.DELIST_SOURCES.update(saved[0]); DA.NAMECHANGE, DA.CONSIDERATION = saved[1], saved[2]
        a = ev.set_index("code")
        self.assertEqual(a.loc["002509.SZ", "force_sell_from"], pd.Timestamp("2020-06-04"))
        self.assertTrue(pd.isna(a.loc["600999.SH", "force_sell_from"]))
        self.assertIn("NEEDS_MANUAL_SOURCE_NO_FORCE_SELL", str(a.loc["600999.SH", "flags"]))
        self.assertEqual(set(ev.source_sha256), {__import__("hashlib").sha256(f.read_bytes()).hexdigest()})

    def test_source_explicit(self):
        with self.assertRaises(TypeError):
            DA.load_delist_events()                                     # source is keyword-required
        with self.assertRaises(ValueError):
            DA.load_delist_events(source="auto")


# ------------------------------------------------------------------ E-2 + P1-6 + P1-7 (FE / ADG adapters)
def _write_panel(dirp: Path, name: str, rows: list, v2: bool):
    df = pd.DataFrame(rows, columns=["date", "instrument", "ret", "ret_on", "is_resume_day", "hiliq_carry"])
    if not v2:
        df = df[["date", "instrument", "ret", "ret_on"]]
    df.to_parquet(dirp / name, index=False)


class T16AdaptersE2(unittest.TestCase):
    def setUp(self):
        self.d = _dates(8)
        self.saved = TB._events_for
        TB._events_for = lambda codes, src: NO_EVENTS.copy()          # no real delisting table in a synthetic test
        self.bal = "510300.SH"
        self.bo = pd.Series(1.0, index=self.d); self.bc = pd.Series(1.0, index=self.d)

    def tearDown(self):
        TB._events_for = self.saved

    def _rows(self, v2):
        d = self.d; rows = []
        for t in range(8):
            if t in (3, 4):                                            # Y halted: no row
                rows.append((d[t], X, 0.01, 0.0, False, False))
                continue
            rows.append((d[t], X, 0.01, 0.0, False, False))
            rows.append((d[t], Y, 0.02 if t != 5 else -0.10, 0.0, t == 5, t == 5))
        return rows

    def _W(self):
        return pd.DataFrame(dict(date=[self.d[1], self.d[1], self.d[4], self.d[4], self.d[4]],
                                 instrument=[X, Y, X, Y, Z], target_weight=[0.5, 0.5, 0.4, 0.4, 0.2]))

    def test_refuse_v1_and_tag(self):
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            _write_panel(Path(td), "cs_panel_2024.parquet", self._rows(False), v2=False)
            with self.assertRaises(FileNotFoundError):
                TB.fe_book_ret_sd1(self._W(), "2024-01-02", "2024-01-11", cost=0.0, bal=self.bal, bal_open=self.bo,
                                   bal_close=self.bc, panel_dir=td, track="leaf_test", delist_source="src_table_v2")
            r, to, res = TB.fe_book_ret_sd1(self._W(), "2024-01-02", "2024-01-11", cost=0.0, bal=self.bal, bal_open=self.bo,
                                            bal_close=self.bc, panel_dir=td, allow_cs_panel_v1=True, track="leaf_test",
                                            delist_source="src_table_v2")
            self.assertEqual(res["cs_panel_version"], "cs_panel_v1(D-1 gap)")
            fl = {f["flag"] for f in res["flags"]}
            self.assertIn("OPTIMISTIC_NO_LIMIT", fl); self.assertIn("NO_RESUME_DAY_GATE", fl)
            self.assertFalse(res["summary"]["gate_eligible_alone"])

    W2 = property(lambda self: pd.DataFrame(dict(date=[self.d[1], self.d[4]], instrument=[X, Y], target_weight=[1.0, 0.5])))

    def _fe(self, td, **kw):
        return TB.fe_book_ret_sd1(self.W2, "2024-01-02", "2024-01-11", cost=0.0, bal=self.bal, bal_open=self.bo,
                                  bal_close=self.bc, panel_dir=td, track="leaf_test", delist_source="src_table_v2", **kw)

    def _flags_file(self, td, announced: bool):
        """Synthetic suspend_flags_v2 (ts_code, trade_date, resume_announced, is_resume_day) under OUT_DIR."""
        f = Path(td) / "suspend_flags_v2.parquet"
        pd.DataFrame(dict(ts_code=[Y], instrument_id=["sh.600002"], trade_date=[self.d[5]],
                          resume_announced=[announced], is_resume_day=[True])).to_parquet(f, index=False)
        return f, __import__("hashlib").sha256(f.read_bytes()).hexdigest()

    def test_resume_gate_fallback_disclosed(self):     # r2 behaviour, now explicit + disclosure only (Arch P2-R2)
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            _write_panel(Path(td), "cs_panel_v2_2024.parquet", self._rows(True), v2=True)
            r, to, res = self._fe(td, resume_gate="is_resume_day_fallback")
            ev = res["events"]
            self.assertTrue(((ev.type == "RESUME_DAY_ENTRY_GATE") & (ev.code == Y) & (ev.date == str(self.d[5].date()))).any())
            fl = {f["flag"] for f in res["flags"]}
            self.assertIn("ENTRY_GATE_IS_RESUME_DAY_T1600", fl); self.assertIn("IS_RESUME_DAY_MILD_LOOKAHEAD", fl)
            self.assertEqual(res["summary"]["hiliq_carry_check"]["n_mismatch"], 0)
            self.assertIn("OPTIMISTIC_NO_LIMIT", fl)
            rg = res["summary"]["resume_gate"]
            self.assertEqual(rg["blocked_new_entries_by_year"], {2024: 1})
            self.assertEqual(rg["basis"], "sensitivity_disclosure_only")
            self.assertIsNone(rg["of_which_is_resume_day_without_R_by_year"])   # no resume_announced known here

    def test_resume_gate_requires_announced(self):    # default: no resume_announced source -> refuse
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            _write_panel(Path(td), "cs_panel_v2_2024.parquet", self._rows(True), v2=True)
            with pytest.raises(ValueError):
                self._fe(td)                                          # no resume_flags_sha256
            with pytest.raises(FileNotFoundError):
                self._fe(td, resume_flags_sha256="0" * 64, resume_flags_path=Path(td) / "absent.parquet")
            f, sha = self._flags_file(td, announced=True)
            with pytest.raises(ValueError):
                self._fe(td, resume_flags_sha256="0" * 64, resume_flags_path=f)   # sha mismatch
            with pytest.raises(ValueError):
                self._fe(td, resume_gate="auto")

    def test_resume_gate_joins_suspend_flags(self):
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            _write_panel(Path(td), "cs_panel_v2_2024.parquet", self._rows(True), v2=True)
            f, sha = self._flags_file(td, announced=True)
            r, to, res = self._fe(td, resume_flags_sha256=sha, resume_flags_path=f)
            ev = res["events"]
            self.assertTrue(((ev.type == "RESUME_DAY_ENTRY_GATE") & (ev.code == Y) & (ev.date == str(self.d[5].date()))).any())
            rg = res["summary"]["resume_gate"]
            self.assertEqual((rg["mode"], rg["gate_column"], rg["basis"]), ("require_announced", "resume_announced", "main"))
            self.assertEqual(rg["source"], f"suspend_flags_v2@{sha}")
            self.assertEqual(rg["blocked_new_entries_by_year"], {2024: 1})
            self.assertEqual(rg["of_which_is_resume_day_without_R_by_year"], {2024: 0})
            self.assertNotIn("ENTRY_GATE_IS_RESUME_DAY_T1600", {f_["flag"] for f_ in res["flags"]})
            # is_resume_day without an R record: announced gate does not block; the fallback counts it as without_R
            f2, sha2 = self._flags_file(td, announced=False)
            _, _, res2 = self._fe(td, resume_flags_sha256=sha2, resume_flags_path=f2)
            self.assertEqual(res2["summary"]["resume_gate"]["blocked_new_entries_total"], 0)

    def test_resume_gate_off_sensitivity(self):
        with tempfile.TemporaryDirectory(dir=OUT_DIR) as td:
            _write_panel(Path(td), "cs_panel_v2_2024.parquet", self._rows(True), v2=True)
            f, sha = self._flags_file(td, announced=True)
            out = TB.fe_resume_gate_sensitivity(self.W2, "2024-01-02", "2024-01-11", cost=0.0, bal=self.bal,
                                                bal_open=self.bo, bal_close=self.bc, panel_dir=td, track="leaf_test",
                                                delist_source="src_table_v2", resume_flags_sha256=sha, resume_flags_path=f)
            off = out["gate_off"]
            self.assertFalse((off["events"].type == "RESUME_DAY_ENTRY_GATE").any())
            self.assertIn("RESUME_GATE_OFF_SENSITIVITY", {f_["flag"] for f_ in off["flags"]})
            self.assertEqual(off["summary"]["resume_gate"]["basis"], "sensitivity_disclosure_only")
            self.assertEqual(out["diff"]["n_blocked_main"], 1)
            self.assertEqual(set(out["diff"]["sum_ret_diff_by_year"]), {2024})

    def test_carry_checker_detects_mismatch(self):
        d = self.d
        close = pd.DataFrame({Y: [10, 10, 10, np.nan, np.nan, np.nan, 10, 10]}, index=d, dtype=float)
        ex = pd.DataFrame({Y: [0, 1, 1, 1, 1, 1, 1, 1]}, index=d, dtype=float)
        carry = pd.DataFrame({Y: [False] * 5 + [True, False, False]}, index=d)
        self.assertEqual(TB.check_hiliq_carry(close, ex, carry)["n_mismatch"], 1)
        carry2 = pd.DataFrame({Y: [False] * 6 + [True, False]}, index=d)
        self.assertEqual(TB.check_hiliq_carry(close, ex, carry2)["n_mismatch"], 0)

    def test_adg_tagged_and_track_required(self):
        P = pd.DataFrame({X: [0.5] * 8, Y: [0.5] * 8}, index=self.d)
        cl = lambda i: pd.Series(np.linspace(10, 11, 8), index=self.d)
        g, to, res = TB.adg_gross_and_turnover_sd1(P, cl, track="adg_test", delist_source="src_table_v2")
        self.assertIn("OPTIMISTIC_NO_LIMIT", {f["flag"] for f in res["flags"]})
        self.assertFalse(res["summary"]["gate_eligible_alone"])
        for bad in (dict(track=None, delist_source="src_table_v2"), dict(track="x", delist_source=None)):
            with self.assertRaises(ValueError):
                TB.adg_gross_and_turnover_sd1(P, cl, **bad)


if __name__ == "__main__":
    unittest.main()
