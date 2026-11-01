"""Research/paper-grade loop entry points (Eng-owned). live=false; NO orders; no daemons; no GP; no evolve writeback.

loop-sync     : read-only leaf status index -> output/loop/leaf_status_index.{json,parquet}
paper-daily   : EOD wrapper: capacity-adv-paper (unchanged code path) then b4-paper forward+monitor; combined recon
alert-ingest  : validate AI intel alerts -> data/v2/alerts/alerts_<YYYYMMDD>.parquet (risk_flag only; weights never touched)
"""
from __future__ import annotations
import glob, json, os, re, subprocess, sys
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LOOP = ROOT / "output/loop"
ALERTS = ROOT / "data/v2/alerts"
PY = sys.executable
FLAGS = dict(live=False, live_orders=False, promotion_approved=False, strategy_promotion_approved=False,
             evolve_writeback="LIMITED: priority/fitness/blacklist only (Leo-approved 2026-10-13); GP banned")


def now_et(fmt="%Y-%m-%dT%H:%M:%S%z"):
    return datetime.now(ZoneInfo("America/New_York")).strftime(fmt)


# ---------------------------------------------------------------- loop-sync (read-only)
def _ledger_rows():
    p = ROOT / "docs/v2/AI_LEAF_LEDGER_ZH.md"
    out = {}
    if not p.exists():
        return out
    for ln in p.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) >= 6 and c[2].startswith("g1g5_"):
            out[c[2]] = dict(ledger_no=c[0], ledger_leaf=c[1], ledger_verdict=c[3], ledger_numbers=c[4], ledger_doc=c[5],
                             ledger_price_basis=c[6] if len(c) > 6 else None)
    return out


def _smoke(d):
    p = d / "book_smoke_summary.json"
    if not p.exists():
        return {}
    s = json.loads(p.read_text())
    r = {}
    for cap, v in s.get("by_capital", {}).items():
        b, c0 = v.get("X2/BOOK", {}), v.get("X2/C0", {})
        if "cagr" in b:
            r[cap] = dict(cagr=b["cagr"], mdd=b["mdd"], sharpe=b.get("sharpe"), cost=b.get("cost_pct_initial"),
                          c0_cagr=c0.get("cagr"), gate=bool(0.12 <= b["cagr"] <= 0.18 and b["mdd"] >= -0.28))
    return dict(run_id=s.get("run_id"), by_capital=r)


def loop_sync(do_writeback=False):
    LOOP.mkdir(parents=True, exist_ok=True)
    led = _ledger_rows()
    leaves = {}
    for f in sorted(glob.glob(str(ROOT / "output/ai_factory/g1g5_*_daily_weights_*.parquet"))):
        m = re.match(r"g1g5_(.+?)_daily_weights_(\d{8}_\d{6})\.parquet$", Path(f).name)
        if not m or m.group(1).startswith("combo_") or m.group(1).startswith("conc4leg"):
            continue
        leaves.setdefault(m.group(1), []).append((m.group(2), f))
    rows = []
    for leaf, fs in sorted(leaves.items()):
        ts, f = sorted(fs)[-1]
        meta_p = ROOT / f"output/ai_factory/g1g5_{leaf}_run_meta_{ts}.json"
        meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
        tag = meta.get("mechanism_tag") or f"g1g5_ashare_{leaf}_v1"
        acc = sorted(glob.glob(str(ROOT / f"docs/v2/AI_G1G5_{leaf.upper()}_WEIGHT_ACCEPT_ZH.md")))
        alpha_label = None
        if acc:
            head = Path(acc[0]).read_text(encoding="utf-8")[:400]
            mm = re.search(r"(RESEARCH_ACCEPT|ACCEPT|WATCH|PASS|FAIL|REJECT|DONE_FAIL)", head)
            alpha_label = mm.group(1) if mm else "see_doc"
        sm = _smoke(ROOT / f"output/v3/book_smoke_g1g5_{leaf}_x2")
        L = led.get(tag, {})
        _a = _alpha_labels(); A = _a.get(leaf) or _a.get(ALPHA_ALIAS.get(leaf, "\0"))
        if A: alpha_label = A.get("label") or A.get("verdict")
        rows.append(dict(leaf=leaf, label_source="alpha_labels.json" if A else "doc_parse_fallback", mechanism_tag=tag, weights=str(Path(f).relative_to(ROOT)), weights_ts=ts,
                         run_meta=str(meta_p.relative_to(ROOT)) if meta_p.exists() else None,
                         alpha_accept_doc=str(Path(acc[0]).relative_to(ROOT)) if acc else None, alpha_label=alpha_label,
                         ledger_verdict=L.get("ledger_verdict"), ledger_price_basis=L.get("ledger_price_basis"),
                         smoke_run=sm.get("run_id"), smoke=json.dumps(sm.get("by_capital", {}), ensure_ascii=False),
                         smoke_gate_both=bool(sm.get("by_capital")) and all(v["gate"] for v in sm["by_capital"].values())))
    combos = []
    for d in sorted(glob.glob(str(ROOT / "output/v3/book_smoke_g1g5_combo_*_x2"))) + sorted(glob.glob(str(ROOT / "output/v3/book_smoke_g1g5_conc4leg_*_x2"))):
        sm = _smoke(Path(d))
        trunk = _smoke(ROOT / "output/v3/book_smoke_g1g5_capacity_adv_x2")["by_capital"]
        beats = {c: bool(v["cagr"] > trunk[c]["cagr"] and v["mdd"] > trunk[c]["mdd"]) for c, v in sm.get("by_capital", {}).items() if c in trunk}
        combos.append(dict(combo=Path(d).name.replace("book_smoke_g1g5_", "").replace("_x2", ""), by_capital=sm.get("by_capital"),
                           beats_trunk=beats, beats_trunk_both=bool(beats) and len(beats) == 2 and all(beats.values())))
    idx = dict(generated_et=now_et(), source_note="read-only; ledger is human-readable only; no writes outside output/loop",
               **FLAGS, leaves=rows, combos=combos)
    new = json.dumps({k: v for k, v in idx.items() if k != "generated_et"}, sort_keys=True, ensure_ascii=False, default=str)
    jp = LOOP / "leaf_status_index.json"
    if jp.exists():
        old = json.loads(jp.read_text()); old.pop("generated_et", None)
        if json.dumps(old, sort_keys=True, ensure_ascii=False, default=str) == new:
            print(json.dumps(dict(status="unchanged", leaves=len(rows), combos=len(combos))))
            return writeback(idx) if do_writeback else 0
    jp.write_text(json.dumps(idx, indent=2, ensure_ascii=False, default=str))
    pd.DataFrame(rows).to_parquet(LOOP / "leaf_status_index.parquet", index=False)
    print(json.dumps(dict(status="written", leaves=len(rows), combos=len(combos), path=str(jp.relative_to(ROOT)))))
    return writeback(idx) if do_writeback else 0


# ---------------------------------------------------------------- approve->evolve writeback (limited scope)
PAPER_TRACKS = {"capacity_adv": "paper_track_1", "B4_conc_50_25_25": "paper_track_2"}
FAIL_RE = re.compile(r"FAIL|REJECT|同构|DONE_FAIL")


ALPHA_IDX = LOOP / "alpha_labels.json"
ALPHA_ALIAS = {"industry_etf_rotation": "etf_rotation", "capacity_adv_negevent": "negevent", "friction_cost_redesign": "friction",
               "indcap_momneut_ocf": "indcap", "northbound_flow": "northbound"}


def _alpha_labels():
    if not ALPHA_IDX.exists():
        return {}
    return {x["leaf_id"]: x for x in json.loads(ALPHA_IDX.read_text()).get("labels", [])}


def _alpha_fitness(a):
    v, l, b = a.get("verdict"), a.get("label"), a.get("book_smoke")
    if v == "REJECT" or (v == "DONE_FAIL" and not l):
        return "fail"
    if l == "RESEARCH_CANDIDATE" and b == "BOOK_SMOKE_PASS":
        return "smoke_pass"
    if l == "WATCH" and b == "DONE_FAIL":
        return "watch_smoke_fail"
    if v == "WATCH" or l == "WATCH":
        return "watch"
    if v == "RESEARCH_ACCEPT":
        return "accept_smoke_pending"
    return "unlabeled"


def _fitness(alpha, ledger, gate):
    t = f"{alpha or ''} {ledger or ''}"
    if FAIL_RE.search(t):
        return "fail"
    if "WATCH" in t:
        return "watch"
    if "ACCEPT" in t or "research_candidate" in t:
        return "smoke_pass" if gate else "accept_smoke_fail"
    return "smoke_pass_unlabeled" if gate else "unlabeled"


PRIORITY = {"paper": 100, "smoke_pass": 80, "watch_smoke_fail": 30, "accept_smoke_pending": 35, "smoke_pass_unlabeled": 60, "watch": 40, "accept_smoke_fail": 35, "unlabeled": 20, "fail": 0}


def build_feedback(idx):
    rows, seen = [], set()
    AL = _alpha_labels()
    for r in idx["leaves"]:
        a = AL.get(r["leaf"]) or AL.get(ALPHA_ALIAS.get(r["leaf"], "\0"))
        fit = _alpha_fitness(a) if a else _fitness(r["alpha_label"], r["ledger_verdict"], r["smoke_gate_both"])
        paper = r["leaf"] in PAPER_TRACKS
        bl = fit == "fail"
        reason = None
        if bl and a:
            reason = f"alpha_labels: verdict={a.get('verdict')} label={a.get('label')}"
        elif bl:
            reason = "alpha/ledger FAIL" + ("; isomorphic to failed leaf (ledger 同构)" if "同构" in (r["ledger_verdict"] or "") else "")
        rows.append(dict(leaf_id=r["leaf"], kind="leaf", mechanism_tag=r["mechanism_tag"], fitness_label=("paper_active" if paper else fit),
                         queue_priority=PRIORITY["paper"] if paper else PRIORITY[fit], blacklist=bl, blacklist_reason=reason,
                         source_doc=(a.get("json_path") or a.get("doc_path")) if a else (r["alpha_accept_doc"] or "docs/v2/AI_LEAF_LEDGER_ZH.md"),
                         label_source="alpha_labels.json" if a else "doc_parse_fallback",
                         alpha_verdict=a.get("verdict") if a else None, alpha_label=a.get("label") if a else r["alpha_label"],
                         smoke_run=r["smoke_run"]))
        seen.add(r["mechanism_tag"])
    for tag, L in _ledger_rows().items():   # ledger-only leaves (no weights file), e.g. isomorphic / count-gate fails
        lid = tag.replace("g1g5_ashare_", "").replace("g1g5_", "").replace("_v1", "")
        if tag in seen or lid in {r["leaf_id"] for r in rows}:
            continue
        v = L["ledger_verdict"]; fit = _fitness(None, v, False)
        bl = fit == "fail" or "计数闸" in v
        rows.append(dict(leaf_id=lid, kind="leaf_ledger_only", mechanism_tag=tag,
                         fitness_label="fail" if bl else fit, queue_priority=0 if bl else PRIORITY[fit], blacklist=bl,
                         blacklist_reason=("isomorphic to failed leaf (ledger 同构)" if "同构" in v else ("count gate failed" if "计数闸" in v else ("ledger FAIL" if bl else None))),
                         source_doc="docs/v2/AI_LEAF_LEDGER_ZH.md", smoke_run=None))
        seen.add(tag)
    for c in idx["combos"]:
        ok = c["beats_trunk_both"]
        rows.append(dict(leaf_id="combo:" + c["combo"], kind="combo", mechanism_tag=None, fitness_label="combo_beats_trunk" if ok else "combo_fail_vs_trunk",
                         queue_priority=60 if ok else 0, blacklist=not ok,
                         blacklist_reason=None if ok else "combo does not beat capacity_adv trunk (CAGR higher AND MDD shallower at both AUM)",
                         source_doc="output/v3/book_smoke_g1g5_" + c["combo"] + "_x2/book_smoke_summary.json", smoke_run=None))
    rows.append(dict(leaf_id="B4_conc_50_25_25", kind="combo_paper", mechanism_tag=None, fitness_label="paper_active", queue_priority=100,
                     blacklist=False, blacklist_reason=None, source_doc="docs/v2/STRATEGY_COMBO_CONCLUSION_20261013_ZH.md", smoke_run=None))
    return sorted(rows, key=lambda x: x["leaf_id"])


def writeback(idx):
    rows = build_feedback(idx)
    body = json.dumps(rows, sort_keys=True, ensure_ascii=False, default=str)
    import hashlib
    ver = hashlib.sha256(body.encode()).hexdigest()
    jp = LOOP / "factory_feedback.json"
    if jp.exists() and json.loads(jp.read_text()).get("version_sha256") == ver:
        print(json.dumps(dict(writeback="unchanged", version_sha256=ver[:16], rows=len(rows)))); return 0
    ts = now_et()
    for r in rows: r["updated_at"] = ts
    doc = dict(schema="quantlab.loop.factory_feedback.v1", version_sha256=ver, updated_at=ts,
               scope="queue_priority / fitness_label / blacklist ONLY; GP banned; no structure search; no auto new leaves",
               live=False, promotion_approved=False, reader="QuantLab AI (pull); Eng never writes into AI area", rows=rows)
    jp.write_text(json.dumps(doc, indent=2, ensure_ascii=False, default=str))
    pd.DataFrame(rows).assign(version_sha256=ver).to_parquet(LOOP / "factory_feedback.parquet", index=False)
    print(json.dumps(dict(writeback="written", version_sha256=ver[:16], rows=len(rows), blacklisted=sum(r["blacklist"] for r in rows))))
    return 0


# ---------------------------------------------------------------- alerts
ALERT_COLS = {"alert_id": str, "ts_et": str, "scope": str, "code": str, "severity": str, "severity_source": str, "kind": str,
              "source": str, "expires_et": str, "note": str}
SCOPES = {"stock", "industry", "market"}; SEVS = {"info", "watch", "high"}   # v1.1; legacy "warn" read as "watch"
SEV_ALIAS = {"warn": "watch"}


def validate_alerts(df: pd.DataFrame):
    errs = []
    miss = [c for c in ALERT_COLS if c not in df.columns]
    if miss:
        return [f"missing columns {miss}"]
    if df.alert_id.duplicated().any(): errs.append("duplicate alert_id")
    if not df.scope.isin(SCOPES).all(): errs.append(f"scope must be in {SCOPES}")
    if not df.severity.isin(SEVS).all(): errs.append(f"severity must be in {SEVS}")
    st = df[df.scope == "stock"].code
    if not st.str.match(r"^(sh|sz|bj)\.\d{6}$").all(): errs.append("stock code must be sh./sz./bj.XXXXXX")
    ind = df[df.scope == "industry"].code
    if not ind.str.match(r"^\d{6}$").all(): errs.append("industry code must be SW L1 6-digit sw_code (e.g. 801010)")
    for c in ("ts_et", "expires_et"):
        if pd.to_datetime(df[c], errors="coerce", utc=True).isna().any(): errs.append(f"{c} not ISO8601 with offset")
    return errs


INTEL_LATEST = ROOT / "output/intel/ALERTS_latest.json"


def intel_to_alerts(js):
    """Map quantlab.intel.alerts.v1 -> alert contract rows. expires = generated + 24h (source has no expiry; Eng assumption)."""
    import hashlib
    gen = pd.Timestamp(js["generated_et"]).tz_localize("America/New_York")
    exp = gen + pd.Timedelta(hours=24)
    sw = pd.read_parquet(ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1.parquet", columns=["sw_code", "sw_name"]).drop_duplicates()
    name2code = dict(zip(sw.sw_name.astype(str), sw.sw_code.astype(str)))
    out, sev_log = [], []

    def _sev(item, derived):
        """v1.1: explicit severity (enum info/watch/high) wins; unknown -> info (logged); missing -> derived."""
        v = item.get("severity")
        if v is None or (isinstance(v, str) and not v.strip()):
            return derived, "derived"
        v2 = SEV_ALIAS.get(str(v).strip().lower(), str(v).strip().lower())
        if v2 not in SEVS:
            sev_log.append(dict(item=item.get("industry") or item.get("event"), value=v, mapped="info")); return "info", "explicit_unknown_mapped_info"
        return v2, "explicit"
    for a in js.get("alerts", []):
        call, strength = a.get("call", ""), a.get("strength", "")
        der = "high" if (call == "偏空" and strength == "强") else ("watch" if call == "偏空" else "info")
        sev, ssrc = _sev(a, der)
        kind = f"intel_{call}_{strength}".strip("_")
        note = (a.get("note") or "") + " | " + "; ".join(a.get("reasons", []))[:300]
        code = name2code.get(a.get("industry", ""))
        base = f"{js['generated_et']}|{a.get('industry')}"
        if code:
            out.append(dict(alert_id="intel-" + hashlib.sha1((base + "|ind").encode()).hexdigest()[:12], scope="industry", code=code,
                            severity=sev, severity_source=ssrc, kind=kind, note=f"{a.get('industry')}: {note}"))
        for s_ in a.get("stocks", []):
            out.append(dict(alert_id="intel-" + hashlib.sha1((base + "|" + s_["code"]).encode()).hexdigest()[:12], scope="stock", code=s_["code"],
                            severity=sev, severity_source=ssrc, kind=kind, note=f"{a.get('industry')}/{s_.get('name')}: {note}"))
    for e in js.get("events", []):   # macro events (CPI/FOMC/TSMC...): market scope, display only (no stock/industry match)
        sev, ssrc = _sev(e, "info")
        out.append(dict(alert_id="intel-" + hashlib.sha1(f"{js['generated_et']}|ev|{e.get('event')}|{e.get('time_et')}".encode()).hexdigest()[:12],
                        scope="market", code="ALL", severity=sev, severity_source=ssrc, kind="intel_event",
                        note=f"{e.get('event')} @ {e.get('time_et')} ET ({e.get('source')})"))
    if sev_log:
        print(json.dumps(dict(severity_unknown_mapped_to_info=sev_log), ensure_ascii=False))
    df = pd.DataFrame(out, columns=["alert_id", "scope", "code", "severity", "severity_source", "kind", "note"])
    df["ts_et"] = gen.isoformat(); df["expires_et"] = exp.isoformat(); df["source"] = f"quantlab_ai_intel:{js.get('mode')}"
    unmapped = [a.get("industry") for a in js.get("alerts", []) if a.get("industry") not in name2code]
    return df, unmapped


def alert_ingest(path=None, date=None):
    src = Path(path) if path else INTEL_LATEST
    unmapped = []
    if src.suffix == ".json" and json.loads(src.read_text()).get("schema") == "quantlab.intel.alerts.v1":
        df, unmapped = intel_to_alerts(json.loads(src.read_text()))
        if df.empty:
            print(json.dumps(dict(status="ok_empty", source=str(src), rows=0))); return 0
    else:
      df = pd.read_json(src, lines=src.suffix == ".jsonl") if src.suffix in (".json", ".jsonl") else (
        pd.read_parquet(src) if src.suffix == ".parquet" else pd.read_csv(src, dtype=str))
    if "severity_source" not in df.columns:
        df["severity_source"] = "explicit"
    if "severity" in df.columns:
        df["severity"] = df.severity.astype(str).str.lower().map(lambda v: SEV_ALIAS.get(v, v))
    df = df.astype({c: str for c in ALERT_COLS if c in df.columns})
    errs = validate_alerts(df)
    if errs:
        print(json.dumps(dict(status="REJECTED", errors=errs), ensure_ascii=False)); return 1
    ALERTS.mkdir(parents=True, exist_ok=True)
    out = ALERTS / f"alerts_{date or now_et('%Y%m%d')}.parquet"
    if out.exists():
        prev = pd.read_parquet(out)
        if "severity_source" not in prev.columns: prev["severity_source"] = "derived_legacy_v1"
        prev["severity"] = prev.severity.map(lambda v: SEV_ALIAS.get(v, v))
        df = pd.concat([prev, df]).drop_duplicates("alert_id", keep="last")
    df[list(ALERT_COLS)].to_parquet(out, index=False)
    print(json.dumps(dict(status="ok", source=str(src), rows=len(df), unmapped_industries=unmapped, path=str(out.relative_to(ROOT))), ensure_ascii=False)); return 0


def active_alerts(asof=None):
    asof = pd.Timestamp(asof or datetime.now(ZoneInfo("America/New_York")))
    if asof.tzinfo is None: asof = asof.tz_localize("America/New_York")
    fs = sorted(glob.glob(str(ALERTS / "alerts_*.parquet")))
    if not fs:
        return pd.DataFrame(columns=list(ALERT_COLS))
    a = pd.concat([pd.read_parquet(f) for f in fs]).drop_duplicates("alert_id", keep="last")
    ts, ex = pd.to_datetime(a.ts_et, utc=True), pd.to_datetime(a.expires_et, utc=True)
    return a[(ts <= asof) & (ex > asof)]


def risk_flags(holdings: pd.DataFrame, asof=None):
    """holdings: instrument_id, weight -> adds risk_flag (str|None). Read-only marker; never modifies weight."""
    a = active_alerts(asof); h = holdings.copy(); h["risk_flag"] = None
    if a.empty:
        return h
    sw = pd.read_parquet(ROOT / "data/v2/sw_l1_pit/industry_members_sw_l1.parquet", columns=["instrument_id", "sw_code", "out_date"])
    sw = sw[sw.out_date.isna()].drop_duplicates("instrument_id").set_index("instrument_id").sw_code.astype(str)
    for i, r in h.iterrows():
        hits = a[((a.scope == "stock") & (a.code == r.instrument_id)) | ((a.scope == "industry") & (a.code == sw.get(r.instrument_id, "?")))]
        if len(hits):
            h.at[i, "risk_flag"] = ";".join(f"{x.severity}:{x.kind}:{x.alert_id}" for x in hits.itertuples())
    return h


# ---------------------------------------------------------------- generic weight gate (capacity_adv etc.)
def weight_gate(old, new, record=None):
    from quantlab.portfolio.b4_paper import check_extension
    import hashlib
    r = check_extension(old, new)
    r.update(old=str(old), new=str(new), new_sha256=hashlib.sha256((ROOT / new if not str(new).startswith("/") else Path(new)).read_bytes()).hexdigest(),
             checked_et=now_et())
    if record:
        hist = json.loads((LOOP / record).read_text()) if (LOOP / record).exists() else {"history": []}
        hist["history"].append(r)
        if r["ok"]:
            hist["accepted"] = dict(path=str(new), sha256=r["new_sha256"], checked_et=r["checked_et"])
        (LOOP / record).write_text(json.dumps(hist, indent=2, ensure_ascii=False, default=str))
    print(json.dumps(r, ensure_ascii=False, default=str))
    return 0 if r["ok"] else 1


def _cap_weights():
    """capacity_adv weights for the bridge: newest gated extension if any (output/loop/capacity_adv_gate.json), else frozen X2 file."""
    g = LOOP / "capacity_adv_gate.json"
    if g.exists():
        a = json.loads(g.read_text()).get("accepted")
        if a and hashlib_ok(a):
            return a["path"], "extended_weights_gated"
    return CAP_WEIGHTS, "frozen_x2"


def hashlib_ok(a):
    import hashlib
    p = ROOT / a["path"]
    return p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == a["sha256"]


# ---------------------------------------------------------------- capacity_adv paper FROZEN_CONFIG (Eng-owned) + recompute hook
CAP_FZ = LOOP / "capacity_adv_FROZEN_CONFIG.json"
CAP_D1_INPUTS = {"d1_valuation": "data/v2/valuation/daily_basic_full_tushare.parquet",
                 "mid_large_members_pit": "data/v2/universe/mid_large_members_pit.parquet"}
KNOWN_RISK = ("capacity_adv full window not reproducible vs frozen: hash-seed dependence fixed by AI (4 seeds identical full-window), "
              "but full-window recompute still differs from frozen on 406 days, so history <=2026-10-09 stays copied verbatim")


def _file_version(p):
    import hashlib, pyarrow.parquet as pq
    h = hashlib.sha256()
    with open(ROOT / p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    md = pq.ParquetFile(str(ROOT / p)).metadata; mx = None
    for i in range(md.num_row_groups):
        rg = md.row_group(i)
        for j in range(rg.num_columns):
            c = rg.column(j)
            if c.path_in_schema in ("trade_date", "session") and c.statistics and c.statistics.has_min_max:
                v = str(pd.Timestamp(c.statistics.max).date()); mx = v if mx is None or v > mx else mx
    st = (ROOT / p).stat()
    return dict(path=p, sha256=h.hexdigest(), rows=md.num_rows, max_date=mx, size=st.st_size,
                mtime=pd.Timestamp(st.st_mtime, unit='s', tz='UTC').tz_convert('America/New_York').isoformat())


SLICE_DATE_COL = {"d1_valuation": "trade_date", "mid_large_members_pit": "session"}


def slice_digest(path, key, pin_date):
    """History-slice hash: rows with date <= pin_date, fixed (sorted) column order, order-independent multiset digest
    (count + sum + xor of per-row uint64 hashes) streamed per row group, so RSS stays low and no global sort is needed.
    Appended rows (date > pin_date) do not change it; any rewrite of history does."""
    import hashlib, time, resource, pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
    pa.set_cpu_count(1); pa.jemalloc_set_decay_ms(0) if hasattr(pa, "jemalloc_set_decay_ms") else None
    t0 = time.time(); f = pq.ParquetFile(str(ROOT / path), buffer_size=1 << 20, pre_buffer=False); dc = SLICE_DATE_COL[key]
    cols = sorted(f.schema_arrow.names); n = 0; s = 0; x = 0; M = (1 << 64) - 1
    for b in f.iter_batches(batch_size=100_000, columns=cols, use_threads=False):
        t = pa.Table.from_batches([b])
        d = t.column(dc)
        lim = pa.scalar(pd.Timestamp(pin_date), type=d.type) if pa.types.is_timestamp(d.type) else pa.scalar(pin_date + "~")
        t = t.filter(pc.less_equal(d, lim) if pa.types.is_timestamp(d.type) else pc.less(d, lim))
        if not t.num_rows: continue
        df = t.to_pandas(); df = df[cols]
        for c in df.columns:
            if str(df[c].dtype).startswith("datetime64") and getattr(df[c].dt, "tz", None) is not None: df[c] = df[c].dt.tz_convert("UTC")
        h = pd.util.hash_pandas_object(df, index=False).to_numpy(dtype="uint64")
        n += len(h); s = (s + int(h.sum(dtype="uint64"))) & M; x ^= int(np.bitwise_xor.reduce(h)) if len(h) else 0
        del t, df, h
    dig = hashlib.sha256(f"{n}|{s}|{x}|{','.join(cols)}".encode()).hexdigest()
    return dict(slice_sha256=dig, slice_rows=n, pin_date=pin_date, columns=cols, method="multiset(count,sum,xor) of hash_pandas_object rows, sorted cols",
                secs=round(time.time() - t0, 1), peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))


def capacity_adv_pin(repin=False):
    cur = {k: _file_version(p) for k, p in CAP_D1_INPUTS.items()}
    pin_date = "2026-10-13"
    for k, p in CAP_D1_INPUTS.items(): cur[k]["slice"] = slice_digest(p, k, pin_date)
    if CAP_FZ.exists() and not repin:
        print(json.dumps(dict(status="exists; use --repin to re-pin after review"))); return 1
    old = json.loads(CAP_FZ.read_text()) if CAP_FZ.exists() else {}
    hist = old.get("pin_history", [])
    if old: hist.append(dict(ts=now_et(), old={k: v["sha256"] for k, v in old["d1_inputs"].items()}, new={k: v["sha256"] for k, v in cur.items()}))
    acc = (json.loads((LOOP / "capacity_adv_gate.json").read_text()).get("accepted") if (LOOP / "capacity_adv_gate.json").exists() else None)
    doc = dict(track="capacity_adv_paper_forward", pinned_et=now_et(), live=False, promotion_approved=False,
               weights=acc or dict(path=CAP_WEIGHTS), d1_inputs=cur, known_risks=[KNOWN_RISK], pin_history=hist,
               rule="daily: history-slice hash (date<=pin_date) must match pin, else PENDING; appended rows pass; whole-file sha recorded for info only")
    CAP_FZ.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    print(json.dumps(dict(status="pinned", d1_inputs={k: (v["sha256"][:12], v["max_date"]) for k, v in cur.items()}), ensure_ascii=False)); return 0


def capacity_adv_pin_check():
    if not CAP_FZ.exists():
        return dict(ok=False, reason="capacity_adv FROZEN_CONFIG not pinned (run quantlab.cli capacity-adv-pin)")
    cfg = json.loads(CAP_FZ.read_text()); pin = cfg["d1_inputs"]; bad = {}; runs = {}
    for k, v in pin.items():
        sl = v.get("slice")
        if not sl:
            bad[k] = "no slice pin (run capacity-adv-pin --repin once)"; continue
        cur = slice_digest(v["path"], k, sl["pin_date"]); runs[k] = dict(secs=cur["secs"], peak_rss_mb=cur["peak_rss_mb"], rows=cur["slice_rows"])
        if cur["slice_sha256"] != sl["slice_sha256"]:
            bad[k] = dict(pinned=(sl["slice_sha256"][:12], sl["slice_rows"]), now=(cur["slice_sha256"][:12], cur["slice_rows"]))
    cfg["last_slice_check"] = dict(ts=now_et(), ok=not bad, runs=runs, changed=bad); CAP_FZ.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    return dict(ok=not bad, changed=bad, runs=runs, reason=("history slice changed (history rewritten) -> PENDING; review" if bad else None))

def cap_content_gate(newp):
    """capacity_adv leg content pin: history <= pinned last_date row-by-row, .check.json present, frozen-script shas equal."""
    from quantlab.portfolio.b4_paper import _hist_rows_equal, _leg_check_json, SHA_FIELD
    k = json.loads(CAP_FZ.read_text()); pin = k.get("leg_pin"); bad = []; miss = []
    h = _hist_rows_equal(pin["path"], newp, pin["last_date"]) if pin else dict(pass_=False)
    if not h["pass_"]: bad.append(f"history differs vs pin <= {pin and pin['last_date']}")
    cj = _leg_check_json(newp)
    if cj is None:
        bad.append(".check.json missing"); miss.append(f"{Path(newp).name} .check.json")
    else:
        got = json.loads(cj.read_text()).get(SHA_FIELD)
        if not isinstance(got, dict):
            bad.append(f"lacks {SHA_FIELD}"); miss.append(f"{cj.name}: {SHA_FIELD}")
        else:
            bad += [f"script changed: {s}" for s, v in k.get("frozen_script_sha256", {}).items() if got.get(s) != v]
    nl = str(pd.read_parquet(ROOT / newp, columns=["session"]).session.astype(str).str[:10].max())
    return dict(pass_=not bad, reason="; ".join(bad) or None, history=h, ai_must_add=miss or None, new_last=nl)


def recompute_hook(cap_path):
    """(c) every new forward rebalance gets a single-day recompute check via AI's --simulate-rebalance (check-only)."""
    w = pd.read_parquet(ROOT / cap_path, columns=["session", "instrument_id", "weight"])
    reb = [d for d in _rebalance_dates(w) if d > pd.Timestamp("2026-10-09")]
    mon_p = LOOP / "capacity_adv_monitor.json"
    mon = json.loads(mon_p.read_text()) if mon_p.exists() else {"recompute_checks": {}}
    PM = ROOT / "output/ai_factory/paper_monitor"
    days = sorted(set(str(d.date()) for d in reb) | {p.stem.split("_")[-1][:4] + "-" + p.stem.split("_")[-1][4:6] + "-" + p.stem.split("_")[-1][6:]
                                                     for p in PM.glob("capacity_adv_rebal_check_*.json")})
    W = w.assign(s=w.session.astype(str).str[:10])
    for k in days:
        tag = k.replace("-", ""); rc = PM / f"capacity_adv_rebal_check_{tag}.json"; sp = PM / f"capacity_adv_simulate_{tag}.parquet"
        rec = dict(scheduled_rebalance=k in {str(d.date()) for d in reb})
        if rc.exists():
            j = json.loads(rc.read_text()); rec.update(ai_check=dict(ok=j.get("ok"), max_abs_diff=j.get("max_abs_diff"), d1=j.get("d1")))
        if sp.exists():   # Eng-side independent deviation: simulate weights vs weights actually used
            S = pd.read_parquet(sp); S["s"] = S.session.astype(str).str[:10] if "session" in S else k
            col = "instrument_id" if "instrument_id" in S else "instrument"
            a = S[S.s == k].groupby(col).weight.sum(); b = W[W.s == k].groupby("instrument_id" if col == "instrument_id" else "instrument").weight.sum() if col in W else W[W.s == k].groupby("instrument_id").weight.sum()
            dv = a.sub(b, fill_value=0).abs()
            rec.update(deviation=float(dv.max()) if len(dv) else None, n_names=int(len(dv)), used_has_day=bool((W.s == k).any()))
        elif rec.get("ai_check") and rec["ai_check"].get("max_abs_diff") is not None:
            # real forward rebalance: AI's extend writes rebal_check (independent full-path recompute) but no simulate parquet
            rec.update(deviation=float(rec["ai_check"]["max_abs_diff"]), deviation_source="ai_rebal_check.max_abs_diff",
                       used_has_day=bool((W.s == k).any()))
        else:
            rec.update(deviation=None, deviation_note="AI simulate parquet and rebal_check both missing"
                       + ("; scheduled rebalance UNCHECKED" if rec["scheduled_rebalance"] else ""))
            if rec["scheduled_rebalance"]: rec["flag"] = "UNCHECKED"
        if rec.get("deviation") is not None and rec["deviation"] > 1e-8:
            rec["flag"] = "DEVIATION" if rec["scheduled_rebalance"] else "INFO_nonrebalance_day"
            if not rec["scheduled_rebalance"]:
                rec["deviation_note"] = "simulated forced rebalance on a carry day vs carried weights: drift indicator, not a check failure"
        mon["recompute_checks"][k] = rec
    mon.update(known_risks=[KNOWN_RISK], updated_et=now_et(), forward_rebalances=[str(d.date()) for d in reb])
    mon_p.write_text(json.dumps(mon, indent=2, ensure_ascii=False, default=str))
    return mon


# ---------------------------------------------------------------- X2H bridge (10-12 .. 11-01), separate segment
BRIDGE_START, BRIDGE_END = "2026-10-12", "2026-11-01"
CAP_WEIGHTS = "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet"


def _calendar():
    c = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date"], filters=[("ts_code", "=", "510300.SH")])
    return sorted(pd.to_datetime(c.trade_date.astype(str)).unique())


def _rebalance_dates(w):
    k = w.session.astype(str).str[:10]
    P = w.assign(k=k).pivot_table(index="k", columns="instrument_id", values="weight", aggfunc="sum").fillna(0)
    return [pd.Timestamp(x) for x in P.index[(P.diff().abs().sum(axis=1) > 1e-9)]]


def _next_month_end(after, cal=None):
    """capacity_adv rebalances on the last SSE trading session of each month (SSE trade_cal; holidays modelled)."""
    from quantlab.portfolio.trade_calendar import next_month_end
    return next_month_end(after)


def _bridge_run(name, wpath, cap, end, out):
    import quantlab.portfolio.v2_multisleeve_book as M
    from quantlab.portfolio.book_smoke import run as bs
    M.WINDOWS["X2H"] = ("2024-06-03", end); M.WINDOW_LABEL["X2H"] = "X2H bridge carrier (X2 frozen; only >=2026-10-12 is reported)"
    bs(["--stock-path", str(wpath), "--sleeves", '{"core":0.0,"stock":1.0,"alpha_event":0.0}', "--windows", "X2H",
        "--capitals", str(cap), "--arms", "BOOK,C0", "--out", str(out), "--receipt", str(Path(out) / "RECEIPT_X2H.md")])
    nav = {}
    for arm in ("BOOK", "C0"):
        n = pd.read_csv(Path(out) / f"aum_{cap}/X2H/{arm}/nav.csv"); n = n.set_index(pd.to_datetime(n.iloc[:, 0])).nav
        nav[arm] = n
    return nav


def bridge(day_dir):
    """Returns per-track bridge result; writes segment NAV csvs labelled segment=X2H_bridge."""
    cal = _calendar(); data_end = cal[-1]
    end = min(pd.Timestamp(BRIDGE_END), data_end)
    res = {}
    if end < pd.Timestamp(BRIDGE_START):
        return dict(status="NOT_STARTED")
    # --- capacity_adv: hold between rebalances, month-end guard
    cap_path, cap_src = _cap_weights()
    pinck = capacity_adv_pin_check()
    if cap_src != "frozen_x2" and not pinck["ok"]:
        cap_path, cap_src = CAP_WEIGHTS, "frozen_x2"
    w = pd.read_parquet(ROOT / cap_path); key = w.session.astype(str).str[:10]
    last = pd.Timestamp(key.max()); nxt = _next_month_end(last, cal)
    hold_days = [d for d in cal if last < d <= end and d < nxt]
    pending = any(d >= nxt for d in cal if last < d <= end)
    tail = w[key == key.max()]
    add = []
    for d in hold_days:
        t = tail.copy(); t["session"] = d if w.session.dtype.kind == "M" else str(d.date()); t["date"] = t["session"]; add.append(t)
    seg = np.where(pd.to_datetime(key) <= pd.Timestamp("2026-10-09"), "X2_frozen", cap_src)
    ext = pd.concat([w.assign(segment=seg)] + [a.assign(segment="hold_extend") for a in add], ignore_index=True)
    bdir = day_dir / "bridge_X2H"; bdir.mkdir(parents=True, exist_ok=True)
    wp = bdir / "capacity_adv_weights_X2H_hold_extend.parquet"; ext.to_parquet(wp, index=False)
    cap_res = dict(source=cap_src, source_path=cap_path, weights=str(wp.relative_to(ROOT)), held_from=str(last.date()), next_scheduled_rebalance=str(nxt.date()),
                   hold_sessions=[str(d.date()) for d in hold_days], status="PENDING" if pending else "OK_HOLD_EXTEND",
                   pending_reason=("scheduled month-end rebalance reached with no newer capacity_adv weights; old weights NOT held past it"
                                   if pending else None), aum={})
    gated_end = last if last >= pd.Timestamp(BRIDGE_START) else None
    run_end = str(hold_days[-1].date()) if hold_days else (str(min(gated_end, end).date()) if gated_end is not None else None)
    for cap in (600000, 1000000):
        if not run_end:
            cap_res["aum"][str(cap)] = dict(status="NO_BRIDGE_SESSIONS"); continue
        nav = _bridge_run("capacity_adv", wp, cap, run_end, bdir / f"capacity_adv_aum_{cap}")
        cap_res["aum"][str(cap)] = _bridge_seg(nav, bdir / f"capacity_adv_{cap}_X2H_nav.csv",
                                               "hold_extend" if (hold_days and cap_src == "frozen_x2") else (cap_src + ("+hold_extend" if hold_days else "")))
    cap_res["pin_check"] = pinck; cap_res["known_risks"] = [KNOWN_RISK]
    if not pinck["ok"]:
        cap_res["status"] = "PENDING"; cap_res["pending_reason"] = pinck["reason"]
    else:
        cap_res["recompute_hook"] = recompute_hook(cap_path).get("recompute_checks")
    res["capacity_adv"] = cap_res
    # --- B4 / S6: official bridge only from rehash-gated weights extending past 2026-10-09 (no holding)
    for key, outdir, why in (("b4", "output/strategy_paper_b4", "frozen B4 weights end {d} (extension produced no new rows); hold not allowed for B4"),
                             ("s6", "output/strategy_paper_s6", "S6 weights end {d}: equity_incentive extension from AI pending; hold not allowed")):
        if not (ROOT / outdir / "FROZEN_CONFIG.json").exists():
            continue
        fz = json.loads((ROOT / outdir / "FROZEN_CONFIG.json").read_text())["weights"]
        tr = dict(aum={})
        for cap in (600000, 1000000):
            p = fz[str(cap)]["path"]
            wl = pd.to_datetime(pd.read_parquet(ROOT / p, columns=["session"]).session.astype(str).str[:10]).max()
            if wl < pd.Timestamp(BRIDGE_START):
                tr["aum"][str(cap)] = dict(status="PENDING", reason=why.format(d=wl.date())); continue
            nav = _bridge_run(key, ROOT / p, cap, str(min(wl, end).date()), bdir / f"{key}_aum_{cap}")
            tr["aum"][str(cap)] = _bridge_seg(nav, bdir / f"{key}_{cap}_X2H_nav.csv", "extended_weights_rehash_gated:" + Path(p).name)
        tr["status"] = "PENDING" if any(v.get("status") == "PENDING" for v in tr["aum"].values()) else "OK"
        res[key] = tr
    return res


def _bridge_seg(nav, path, label):
    b, c = nav["BOOK"], nav["C0"]
    anchor = b.index[b.index < pd.Timestamp(BRIDGE_START)].max()
    sb, sc = b.loc[anchor:], c.loc[anchor:]
    df = pd.DataFrame(dict(nav=sb, c0_nav=sc)); df["segment"] = ["X2_anchor"] + ["X2H_bridge"] * (len(df) - 1); df["label"] = ["frozen"] + [label] * (len(df) - 1)
    df.to_csv(path, index_label="date")
    r = sb.pct_change().dropna()
    return dict(status="OK", nav_csv=str(path.relative_to(ROOT)), anchor=str(anchor.date()), sessions=len(sb) - 1,
                ret=float(sb.iloc[-1] / sb.iloc[0] - 1), c0_ret=float(sc.iloc[-1] / sc.iloc[0] - 1),
                ex_vs_c0=float(sb.iloc[-1] / sb.iloc[0] - sc.iloc[-1] / sc.iloc[0]),
                mdd=float((sb / sb.cummax() - 1).min()), tail=[(str(i.date()), float(v)) for i, v in sb.iloc[-4:].items()],
                note="bridge only; never merged into X2 (frozen) or FWD performance")


# ---------------------------------------------------------------- paper-daily (EOD)
def _cli(args, log):
    r = subprocess.run([PY, "-m", "quantlab.cli", *args], cwd=ROOT, capture_output=True, text=True,
                       env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"})
    log.append(dict(cmd="quantlab.cli " + " ".join(args), exit=r.returncode, tail=(r.stdout + r.stderr)[-600:]))
    return r.returncode


REQUIRED_TABLES = ("etf_daily_adj", "daily_ohlcv_raw_pit", "daily_basic", "mid_large_universe", "etf510300", "asof_ts")


def data_freshness():
    """Freshness gate (arch review Top1): SSE trade_cal; Data marker output/daily_update_status.json must have status==ok,
    target_trade_date == expected session (latest due trading day), and every required table last_date >= target."""
    from quantlab.portfolio import trade_calendar as T
    mk = Path(os.environ.get("QL_STATUS_PATH") or (ROOT / "output/daily_update_status.json"))
    now = T.now_et(); req = str(T.expected_session(now).date()); closed = str(T.latest_closed_session(now).date())
    # 2026-10-14 fix: process Data's target_trade_date when it is a trading day, close passed (not future), >= required session
    tgt = None
    if mk.exists():
        tgt = json.loads(mk.read_text()).get("target_trade_date")
    tgt_ok = bool(tgt) and T.is_trading_day(tgt) and T.close_passed(tgt, now) and tgt >= req
    exp = tgt if tgt_ok else req
    base = dict(marker=str(mk), run_et=now.isoformat(), run_date_trading=T.is_trading_day(now.date()), expected_session=exp,
                required_session=req, latest_closed_session=closed, processed_session=exp,
                cutoff_rule=f"session D required from D {T.CUTOFF_ET[0]:02d}:{T.CUTOFF_ET[1]:02d} ET; Data target accepted if trading day, close passed (15:00 Asia/Shanghai), >= required",
                calendar="SSE trade_cal (data/v2/tushare_raw/trade_cal.parquet), cross-check with Data calendar: " + str(T.cross_check()["agree"]))
    reasons = []
    # Data's per-table freshness file (preferred when present and newer than the completion marker)
    fp = Path(os.environ.get("QL_FRESH_PATH") or (ROOT / "output/data_freshness_status.json"))
    fz = None
    if fp.exists():
        fz = json.loads(fp.read_text())
        mk_ts = pd.Timestamp(json.loads(mk.read_text()).get("finished_at")) if mk.exists() else None
        if mk_ts is not None and pd.Timestamp(fz.get("generated_at")) < mk_ts:
            base["freshness_file_ignored"] = "older than daily_update_status.finished_at"; fz = None
    if fz is not None:
        dd = lambda x: (f"{x[:4]}-{x[4:6]}-{x[6:8]}" if x and len(str(x)) == 8 and "-" not in str(x) else x)
        ftabs = {k: dict(last_date=dd(v.get("last_date")), lag=v.get("lag_trading_days"), stale=v.get("stale")) for k, v in fz.get("tables", {}).items()}
        fexp = dd(fz.get("expected_trade_date"))
        base.update(source="output/data_freshness_status.json", data_fresh_overall=fz.get("overall"), data_stale_tables=fz.get("stale_tables"),
                    data_expected_trade_date=fexp, data_tables=ftabs)
        if fexp != exp:
            base["calendar_mismatch"] = f"Data expected_trade_date {fexp} (20:00 Asia/Shanghai cutoff) != Eng processed session {exp}; info only, Eng rule used"
            print(json.dumps(dict(freshness_calendar_mismatch=base["calendar_mismatch"]), ensure_ascii=False))
        if fz.get("overall") != "ok": reasons.append(f"data_freshness overall={fz.get('overall')} stale_tables={fz.get('stale_tables')}")
        for t in REQUIRED_TABLES:
            v = ftabs.get(t)
            if v is None: continue                      # not covered by Data's file -> checked via daily_update_status below
            if v["stale"] or (v["last_date"] or "") < exp: reasons.append(f"[freshness] table {t} last_date={v['last_date']} stale={v['stale']} < {exp}")
        try:   # calendar cross-check: Data's PIT SSE calendar vs ours
            from quantlab.portfolio.trade_calendar import open_days
            dc = pd.read_parquet(ROOT / "data/v2/calendar/trade_cal_sse_pit.parquet")
            col = "cal_date" if "cal_date" in dc else dc.columns[0]
            if "is_open" in dc: dc = dc[dc.is_open.astype(int) == 1]
            dd_ = pd.DatetimeIndex(pd.to_datetime(dc[col].astype(str))).normalize().unique()
            o = open_days(); lo, hi = max(dd_.min(), o.min()), min(dd_.max(), o.max())
            a, b = dd_[(dd_ >= lo) & (dd_ <= hi)], o[(o >= lo) & (o <= hi)]
            base["data_calendar_check"] = dict(agree=bool(a.sort_values().equals(b)), only_data=len(a.difference(b)), only_eng=len(b.difference(a)))
            if not base["data_calendar_check"]["agree"]:
                print(json.dumps(dict(calendar_disagreement=base["data_calendar_check"])))
        except Exception as e:
            base["data_calendar_check"] = dict(error=repr(e)[:200])
    if not mk.exists():
        return dict(base, fresh=False, reasons=reasons + ["status marker missing"])
    m = json.loads(mk.read_text()); tabs = {k: (v or {}).get("last_date") for k, v in m.get("tables", {}).items()}
    if m.get("status") != "ok": reasons.append(f"status={m.get('status')} (need ok)")
    if not tgt_ok:
        why = ("not a trading day" if tgt and not T.is_trading_day(tgt) else "in the future (close not passed)" if tgt and not T.close_passed(tgt, now)
               else f"older than required session {req}")
        reasons.append(f"target_trade_date={tgt} rejected: {why}")
    for t in REQUIRED_TABLES:
        ld = tabs.get(t)
        if ld is None or ld < exp: reasons.append(f"table {t} last_date={ld} < {exp}")
    return dict(base, marker_status=m.get("status"), target_trade_date=m.get("target_trade_date"), marker_finished_at=m.get("finished_at"),
                tables=tabs, required_tables=list(REQUIRED_TABLES), fresh=not reasons, reasons=reasons,
                etf_daily_adj_ok=not any("etf_daily_adj" in r for r in reasons))


def _legacy_freshness():
    """DEPRECATED — weekday-only freshness; CN holidays not modeled.

    Do NOT use as the default freshness gate. Paper path uses data_freshness()
    (SSE trade_cal + CUTOFF_ET). Kept only for archival/compare; emits DeprecationWarning.
    """
    warnings.warn(
        "_legacy_freshness is deprecated: weekday calendar; CN holidays not modeled. "
        "Use data_freshness() (SSE trade_cal) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    def mx(p, col):
        try: return pd.to_datetime(pd.read_parquet(ROOT / p, columns=[col])[col].astype(str).str[:10]).max()
        except Exception as e: return None
    src = {"510300_panel": mx("data/v2/etf_510300/panels/sh.510300.parquet", "event_time"),
           "etf_daily_adj_510300": None, "x2_asof_extend_sample_600036": mx("data/v2/asof_extend_tushare_202610/panels/sh.600036.parquet", "trade_date")}
    try:
        e = pd.read_parquet(ROOT / "data/v2/etf/etf_daily_adj.parquet", columns=["ts_code", "trade_date"], filters=[("ts_code", "=", "510300.SH")])
        src["etf_daily_adj_510300"] = pd.to_datetime(e.trade_date.astype(str)).max()
    except Exception:
        pass
    now = datetime.now(ZoneInfo("America/New_York"))
    exp = pd.Timestamp(now.date())
    if now.hour < 17: exp -= pd.Timedelta(days=1)     # China close (~03:00 ET) + vendor lag: treat ET evening as cutoff
    while exp.weekday() >= 5: exp -= pd.Timedelta(days=1)
    known = [v for v in src.values() if v is not None]
    latest = min(known) if known else None
    return dict(expected_session=str(exp.date()), latest_common=str(latest.date()) if latest is not None else None,
                sources={k: (str(v.date()) if v is not None else None) for k, v in src.items()},
                fresh=bool(latest is not None and latest >= exp), note="weekday calendar; CN holidays not modeled")


def _latest_b4_extension():
    V = ROOT / "output/small_aum_concentration/v2"
    out = {}
    for t in ("60w", "100w"):
        fs = sorted(V.glob(f"B_B4_50_25_25_topN_{t}_2*.parquet"))
        out[t] = str(fs[-1].relative_to(ROOT)) if fs else None
    return out


BUS_AGENT = "QuantLab Eng"


def _bus(type_, msg, refs=None, **payload):
    """Read-only dashboard bus (/workspace/quantlab-web/ql_bus.py). Never raises: emit failure must not fail paper-daily."""
    try:
        sys.path.insert(0, "/workspace/quantlab-web"); import ql_bus
        return ql_bus.emit(BUS_AGENT, type_, refs=refs or [], msg=msg, live=False, **payload)
    except Exception as e:
        return dict(ok=False, error=repr(e)[:200])


def _bus_after_run(d, recon, br, log):
    out = {}
    try:
        navs = {}
        for k in ("capacity_adv", "b4", "s6"):
            for c, v in (br.get(k, {}).get("aum") or {}).items():
                navs[f"{k}_{c}"] = dict(segment="X2H", status=v.get("status"), date=(v.get("tail") or [[None]])[-1][0],
                                        nav=(v.get("tail") or [[None, None]])[-1][1], ret=v.get("ret"), ex_vs_c0=v.get("ex_vs_c0"))
        navs["FWD"] = "WAITING until 2026-11-02"
        out["nav"] = _bus("nav", "paper NAV (X2H bridge; FWD from 11-02)", [str((d / "paper_daily_recon.json").relative_to(ROOT))], navs=navs)
        hold = {}
        cfgs = {"b4": "output/strategy_paper_b4/FROZEN_CONFIG.json", "s6": "output/strategy_paper_s6/FROZEN_CONFIG.json"}
        srcs = {f"{k}_{c}": v["path"] for k, f in cfgs.items() if (ROOT / f).exists() for c, v in json.loads((ROOT / f).read_text())["weights"].items()}
        cw = br.get("capacity_adv", {}).get("weights")
        if cw: srcs.update({"capacity_adv_600000": cw, "capacity_adv_1000000": cw})
        for k, pth in srcs.items():
            w = pd.read_parquet(ROOT / pth, columns=["session", "instrument_id", "weight"]); w["s"] = w.session.astype(str).str[:10]
            last = w[w.s == w.s.max()].groupby("instrument_id").weight.sum().sort_values(ascending=False).head(8)
            hold[k] = dict(session=w.s.max(), top=[[i, round(float(x), 4)] for i, x in last.items()])
        out["holdings"] = _bus("holdings", "paper top holdings (target weights, last session)", list(set(srcs.values())), holdings=hold)
        gates = [dict(cmd=x.get("cmd"), exit=x.get("exit")) for x in log if any(t in str(x.get("cmd", "")) for t in ("rehash", "weight-gate"))]
        gates += [dict(capacity_adv_content_gate=x["capacity_adv_content_gate"].get("pass_")) for x in log if "capacity_adv_content_gate" in x]
        out["gate"] = _bus("gate", f"freshness PASS (due {recon['freshness'].get('expected_session')}); track status {recon['track_status']}",
                           [str((d / "paper_daily_recon.json").relative_to(ROOT))], freshness="PASS", gates=gates or "no gate run (no new files)",
                           track_status=recon["track_status"], pin_check=br.get("capacity_adv", {}).get("pin_check", {}).get("ok"))
        out["receipt"] = _bus("receipt", f"paper-daily {recon['date_et']} done", [str((d / "scorecard.md").relative_to(ROOT)), "output/loop/scorecard_latest.md"])
    except Exception as e:
        out["error"] = repr(e)[:200]
    return out


def paper_daily(run_nav=False, run_extend=True, force=False):
    from quantlab.portfolio import trade_calendar as T
    LOOP.mkdir(parents=True, exist_ok=True)
    now = T.now_et(); day = now.strftime("%Y%m%d")
    if not T.is_trading_day(now.date()):
        sk = LOOP / "skips.jsonl"
        rec = dict(run_et=now.isoformat(), status="SKIPPED_NON_TRADING_DAY", calendar="SSE trade_cal", **FLAGS)
        with open(sk, "a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if not os.environ.get("QL_BUS_OFF"): _bus("alert", f"paper-daily SKIPPED_NON_TRADING_DAY ({now.date()})", ["output/loop/skips.jsonl"], severity="info", status="SKIPPED_NON_TRADING_DAY")
        print(json.dumps(rec, ensure_ascii=False)); return 0
    # FWD start sanity (B4/S6/capacity_adv share 2026-11-02): must be the first SSE trading day of November
    from quantlab.portfolio.b4_paper import FORWARD_START
    fwd_ok = T.is_trading_day(FORWARD_START) and str(T.first_trading_day_on_or_after("2026-11-01").date()) == FORWARD_START
    d = LOOP / f"paper_daily_{day}"; d.mkdir(exist_ok=True)
    log = []
    fr = data_freshness(); fr["fwd_start_check"] = dict(fwd_start=FORWARD_START, ok=bool(fwd_ok))
    if not fwd_ok: fr.setdefault("reasons", []).append(f"FWD start {FORWARD_START} is not the first SSE trading day of November"); fr["fresh"] = False
    if not fr["fresh"] and not force:
        recon = dict(date_et=day, status="REFUSED_STALE_DATA", freshness=fr, reasons=fr.get("reasons"), **FLAGS,
                     gap="NAV not run: data stale or calendar check failed; QuantLab Data owns the refresh", weights_modified=False)
        (d / "paper_daily_recon.json").write_text(json.dumps(recon, indent=2, ensure_ascii=False, default=str))
        try:
            from quantlab.portfolio.scorecard import write as _sc
            _sc(str(d.relative_to(ROOT)), stale=fr.get("reasons"))
        except Exception as e:
            recon["scorecard_error"] = repr(e)
        if not os.environ.get("QL_BUS_OFF"):
            _bus("alert", "paper-daily REFUSED_STALE_DATA: NAV not run", [str((d / "paper_daily_recon.json").relative_to(ROOT))], severity="high",
                 status="REFUSED_STALE_DATA", reasons=fr.get("reasons"))
        print(json.dumps(dict(status="REFUSED_STALE_DATA", reasons=fr.get("reasons"), dir=str(d.relative_to(ROOT))), ensure_ascii=False))
        return 3
    if run_extend:
        r = subprocess.run(["python3", "research/capacity_adv_paper_extend.py"], cwd=ROOT, capture_output=True, text=True)
        log.append(dict(cmd="research/capacity_adv_paper_extend.py", exit=r.returncode, tail=(r.stdout + r.stderr)[-600:],
                        pending=("ABORT" in (r.stdout + r.stderr)) or r.returncode != 0))
    cfs = sorted((ROOT / "output/ai_factory").glob("g1g5_capacity_adv_daily_weights_paper_2*.parquet"))
    if cfs:
        acc = (json.loads((LOOP / "capacity_adv_gate.json").read_text()).get("accepted", {}) if (LOOP / "capacity_adv_gate.json").exists() else {})
        newest = str(cfs[-1].relative_to(ROOT))
        if acc.get("path") != newest:
            cg = cap_content_gate(newest); log.append(dict(capacity_adv_content_gate=cg))
            if cg["pass_"]:
                if _cli(["weight-gate", "--old", CAP_WEIGHTS, "--new", newest, "--record", "capacity_adv_gate.json"], log) == 0:
                    k = json.loads(CAP_FZ.read_text()); from quantlab.portfolio.b4_paper import _fsha
                    k.setdefault("rehash_history", []).append(dict(ts=now_et(), old=k.get("leg_pin"), new_path=newest, new_sha256=_fsha(newest)))
                    k["leg_pin"] = dict(path=newest, sha256=_fsha(newest), last_date=cg["new_last"]); CAP_FZ.write_text(json.dumps(k, indent=2, ensure_ascii=False))
    b4_pending = None
    if run_extend:   # AI-owned B4 extension (frozen rule)
        r = subprocess.run(["python3", "research/b4_paper_extend.py", "--run-legs"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0: b4_pending = f"b4_paper_extend exit {r.returncode} (bridge stops at last gated weights)"
        log.append(dict(cmd="research/b4_paper_extend.py --run-legs", exit=r.returncode, tail=(r.stdout + r.stderr)[-600:],
                        pending=("ABORT" in (r.stdout + r.stderr)) or r.returncode != 0))
    ext = _latest_b4_extension()
    cfgw = json.loads((ROOT / "output/strategy_paper_b4/FROZEN_CONFIG.json").read_text())["weights"]
    if ext["60w"] and ext["100w"] and (ext["60w"] != cfgw["600000"]["path"] or ext["100w"] != cfgw["1000000"]["path"]):
        rc0 = _cli(["b4-paper", "--mode", "rehash", "--new-60w", ext["60w"], "--new-100w", ext["100w"]], log)
        if rc0 != 0:
            log.append(dict(note="rehash gate REFUSED; B4 continues on previously frozen files"))
            b4_pending = "B4 rehash gate REFUSED; B4 stays on previously frozen files"
    # --- S6 shadow: same pattern as B4 (AI extend -> gated rehash; failure => S6 PENDING, previous frozen files kept)
    s6_pending = None
    if (ROOT / "output/strategy_paper_s6/FROZEN_CONFIG.json").exists():
        if run_extend:
            r = subprocess.run(["python3", "research/s6_paper_extend.py", "--run-legs"], cwd=ROOT, capture_output=True, text=True)
            log.append(dict(cmd="research/s6_paper_extend.py --run-legs", exit=r.returncode, tail=(r.stdout + r.stderr)[-600:],
                            pending=("ABORT" in (r.stdout + r.stderr)) or r.returncode != 0))
            if r.returncode != 0: s6_pending = f"s6_paper_extend exit {r.returncode}"
        s6c = json.loads((ROOT / "output/strategy_paper_s6/FROZEN_CONFIG.json").read_text())["weights"]
        def _s6new(t):
            fs = [f for f in sorted((ROOT / "output/strategy_paper_s6").glob(f"S6_cap50_ee25_eq25_topN_{t}_2*.parquet"))
                  if f.with_suffix(".check.json").exists()]
            return str(fs[-1].relative_to(ROOT)) if fs else None
        n60, n100 = _s6new("60w"), _s6new("100w")
        if n60 and n100 and (n60 != s6c["600000"]["path"] or n100 != s6c["1000000"]["path"]):
            if _cli(["paper-track", "--track", "s6", "--mode", "rehash", "--new-60w", n60, "--new-100w", n100], log) != 0:
                s6_pending = "S6 rehash gate REFUSED (history/rules/cadence/pinned leg); S6 stays on previously frozen files"
                log.append(dict(note=s6_pending))
    cap_args = ["capacity-adv-paper", "--out", str((d / "capacity_adv_paper").relative_to(ROOT)),
                "--receipt", str((d / "capacity_adv_paper_RECEIPT.md").relative_to(ROOT))] + (["--run-nav"] if run_nav else [])
    rc1 = _cli(cap_args, log)                         # capacity_adv: unchanged code path, outputs redirected to loop dir
    rc2 = _cli(["b4-paper", "--mode", "forward"], log)  # B4 forward (WAITING until weights extended)
    rc3 = _cli(["b4-paper", "--mode", "monitor"], log)
    if (ROOT / "output/strategy_paper_s6/FROZEN_CONFIG.json").exists():
        _cli(["paper-track", "--track", "s6", "--mode", "forward"], log)
    br = bridge(d)
    if b4_pending and "b4" in br:
        br["b4"]["status"] = "PENDING"; br["b4"]["pending_reason"] = b4_pending
    if s6_pending and "s6" in br:
        br["s6"]["status"] = "PENDING"; br["s6"]["pending_reason"] = s6_pending
    if (ROOT / "output/strategy_paper_s6/FROZEN_CONFIG.json").exists():
        _cli(["paper-track", "--track", "s6", "--mode", "monitor"], log)   # after bridge so X2H segment is current
    cap_status = json.loads((ROOT / "output/strategy_paper_capacity_adv/STATUS.json").read_text())   # read-only
    b4 = json.loads((ROOT / "output/strategy_paper_b4/monitor.json").read_text())
    flags = {}
    for cap, wf in json.loads((ROOT / "output/strategy_paper_b4/FROZEN_CONFIG.json").read_text())["weights"].items():
        w = pd.read_parquet(ROOT / wf["path"], columns=["session", "instrument_id", "weight"])
        last = w[w.session.astype(str).str[:10] == w.session.astype(str).str[:10].max()]
        flags[f"b4_{cap}"] = risk_flags(last[last.weight > 0][["instrument_id", "weight"]])
    tw = pd.read_parquet(ROOT / "output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet", columns=["session", "instrument_id", "weight"])
    lt = tw[tw.session.astype(str).str[:10] == tw.session.astype(str).str[:10].max()]
    flags["capacity_adv"] = risk_flags(lt[lt.weight > 0][["instrument_id", "weight"]])
    pd.concat([v.assign(track=k) for k, v in flags.items()]).to_parquet(d / "risk_flags.parquet", index=False)
    recon = dict(date_et=day, mode="EOD_only", freshness=fr, forced=force, intraday="GAP: no intraday feed on box (data/v2 has daily bars only)", **FLAGS,
                 steps=log, capacity_adv=dict(status=cap_status.get("status"), headline=cap_status.get("metrics_headline"),
                                              paper_active=cap_status.get("paper_active")),
                 b4=dict(aum={c: dict(book=v["book"], fills=v["fills"], cap_check=v["cap_check"], turnover=v["turnover_one_way_annual"])
                              for c, v in b4["aum"].items()}, paper_segments=b4.get("paper_segments"), segment_finding=b4.get("segment_finding")),
                 segments=dict(X2="frozen research window 2024-06-03..2026-10-09 (metrics from frozen runs; unchanged)",
                               X2H_bridge=br, FWD=dict(start="2026-11-02", b4=b4.get("paper_segments", {}))),
                 track_status=dict(capacity_adv=br.get("capacity_adv", {}).get("status"), b4=br.get("b4", {}).get("status"), s6=br.get("s6", {}).get("status")),
                 risk_flagged_names={k: int(v.risk_flag.notna().sum()) for k, v in flags.items()},
                 weights_modified=False)
    (d / "paper_daily_recon.json").write_text(json.dumps(recon, indent=2, ensure_ascii=False, default=float))
    (LOOP / "paper_status.json").write_text(json.dumps(dict(updated_et=now_et(), date_et=day, **FLAGS,
        tracks=recon["track_status"], capacity_adv_pending_reason=br.get("capacity_adv", {}).get("pending_reason"),
        note="loop-level status only; output/strategy_paper_capacity_adv/STATUS.json untouched"), indent=2, ensure_ascii=False))
    try:
        from quantlab.portfolio.scorecard import write as _sc
        _sc(str(d.relative_to(ROOT))); log.append(dict(scorecard=str((d / "scorecard.md").relative_to(ROOT))))
    except Exception as e:
        log.append(dict(scorecard_error=repr(e)))
    bus = {} if os.environ.get("QL_BUS_OFF") else _bus_after_run(d, recon, br, log)
    print(json.dumps(dict(dir=str(d.relative_to(ROOT)), exits=[rc1, rc2, rc3], flagged=recon["risk_flagged_names"], bus={k: (v.get("ok") if isinstance(v, dict) else v) for k, v in bus.items()})))
    return 0 if rc1 == 0 and rc3 == 0 else 1
