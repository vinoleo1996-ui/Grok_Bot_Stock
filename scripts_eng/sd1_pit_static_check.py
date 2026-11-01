#!/usr/bin/env python3
"""SD1 PIT static check (spec docs/v2/ARCH_ENGINE_SUSPEND_DELIST_FIX_SPEC_ZH.md §3.6, sha256 2e428f39…bdbb0b).

Strategy layer (research/ + strategy modules) must not reference ex-post delisting info: the tokens
``stock_delisted``, ``delist_date``, ``delist_events`` (also ``delist_accounting``, the guarded loader module).
Whitelist: engine loaders and audit scripts (spec), plus PREEXISTING hits that predate SD1 and are listed
explicitly by (path, stripped line) for Arch review — any new or changed hit fails.
r3.1 (Arch ARCH_SD1_R3_REVIEW_ZH.md 2b8f81c9 §6.1 P1-1): FUNC_WHITELIST allows a token only INSIDE a named function of a
named file (path + function name, never by sha); a hit elsewhere in the same file stays a VIOLATION.
  Matching rule (r3.2, Arch e2e288bc P3-3): a hit is ALLOWED_FUNC when ANY enclosing ``def`` (outermost to innermost,
  incl. nested defs and class methods) has a whitelisted (path, name). So a ``pool_benchmarks`` nested inside
  ``evaluate``, a method named ``pool_benchmarks``, or a second / redefined ``pool_benchmarks`` in that file would also
  pass. The scanner does not police this; the leaf review checks that each whitelisted file has exactly ONE top-level
  ``pool_benchmarks``.
Modes (``--mode`` and ``--paths`` are mutually exclusive, r3.2 P3-4; with neither, the mode is disclosure):

  --mode pinned --closure J --closure-sha256 H --files F[=SHA256]... [--require-file-sha]
        SD1 selftest T10: ONLY the given pinned files + the paper import closure J (every entry's sha256 must still
        match J, J must match H). r3.2 (P3-2): each --files item may carry its expected sha256 as PATH=SHA256 and is then
        re-hashed before the scan (mismatch -> files_ok=false -> exit 1); --require-file-sha makes the sha mandatory
        for every item. Deterministic: other agents' files are not read. Exit 1 on a violation, a closure mismatch or
        a --files mismatch. Report: n_files = candidate files (pinned files ∪ closure), n_scanned = files actually
        read (inside SCOPE and not WHITELISTed), n_scanned_research = scanned files under research/ (r3.2 P3-1).
  --mode disclosure [--json OUT] [--strict]   # full-repo scan (SCOPE): a disclosure report; exit 0 unless --strict.
        Never part of the SD1 test result.
  --paths F [F ...]   # scan given files as if strategy-layer, no whitelist (T10 planted test); exit 1 on a violation
Read-only: plain text + ast scan, imports nothing from quantlab. live=false.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r"stock_delisted|delist_date|delist_events|delist_accounting")
SCOPE = ("research/", "quantlab/strategy/", "quantlab/universe/", "quantlab/factors/",
         "quantlab/portfolio/", "quantlab/beta/", "scripts/")   # Arch SD1 review P2-5 (2026-10-18): + portfolio/, beta/, scripts/
WHITELIST = ("quantlab/platform/execution.py", "quantlab/platform/execution_sd1.py", "quantlab/platform/tradability.py", "quantlab/platform/delist_accounting.py",
             "docs/v2/audit/",
             # Data build / acquisition / survivorship-audit scripts (Arch review §2: not selection; file-level)
             "scripts/build_delisted.py", "scripts/pull_delisted.py", "scripts/build_float_mktcap_from2015.py",
             "scripts/acquire/", "scripts/fix_sd1/", "scripts/smallcap_reconcile.py", "scripts/smallcap_survivorship_b1.py")
# Pre-SD1 references found 2026-10-18 by this script; not strategy-layer use of stock delisting info (Arch to confirm).
PREEXISTING = {
    ("research/ai_hiliq_pool_review_x2.py", 'dm = pd.read_parquet(R/"data/v2/delisted/delisted_master_tushare.parquet", columns=["ts_code","delist_date","last_trade_date","delist_reason_category"])'):
        "AI HI_LIQ pool audit (ex-post review script, not selection)",
    ("research/ai_hiliq_pool_review_x2.py", 'dm["delist_date"] = pd.to_datetime(dm.delist_date.astype(str), errors="coerce"); dm["last_trade_date"] = pd.to_datetime(dm.last_trade_date.astype(str), errors="coerce")'):
        "same audit script",
    ("research/v3_a2_etf_share_demand_report.py", "return m.assign(tracker=label)[['ts_code', 'name', 'benchmark', 'list_date', 'delist_date', 'tracker']]"):
        "ETF fund_basic delist_date (not stock delisting)",
    ("research/v3_a2_etf_share_demand_report.py", "extra = row.assign(tracker=lab)[['ts_code', 'name', 'benchmark', 'list_date', 'delist_date', 'tracker']]"):
        "ETF fund_basic delist_date (not stock delisting)",
    ("research/v3_a4_sealed.py", "for c in ['maturity_date','delist_date','list_date']: b[c]=pd.to_datetime(b[c],errors='coerce',format='%Y%m%d')"):
        "CB basic delist_date (bond maturity/redemption)",
    ("research/v3_a4_sealed.py", "gap=(b.delist_date.reindex(cols)-last).dt.days"): "CB basic delist_date",
    ("research/v3_a4_sealed.py", "live=b.delist_date.reindex(cols).isna()&((END-last).dt.days<=30)"): "CB basic delist_date",
    ("quantlab/universe/mask.py", "is_st, listing_date, delist_date, asset_type, quality_status, ..."):
        "docstring of the instruments contract (field list only); mask code must not use it",
    # ---- P2-5 scope extension (2026-10-18 02:0x ET): pre-SD1 lines in quantlab/portfolio, quantlab/beta, scripts/
    ('quantlab/beta/survivorship.py', 'for c in ("list_date", "delist_date", "last_trade_date"):'):
        'B1 survivorship helper: re-includes later-delisted names (anti-survivorship ranking / terminal sensitivity) - accounting/universe audit, not alpha selection (Arch to confirm)',
    ('quantlab/beta/survivorship.py', 'alive = set(master.index[(master.list_date <= day) & (master.delist_date > day)])'):
        'B1 survivorship helper: re-includes later-delisted names (anti-survivorship ranking / terminal sensitivity) - accounting/universe audit, not alpha selection (Arch to confirm)',
    ('quantlab/beta/survivorship.py', 'alive_later = master[(master.list_date <= day) & (master.delist_date > day)]'):
        'B1 survivorship helper: re-includes later-delisted names (anti-survivorship ranking / terminal sensitivity) - accounting/universe audit, not alpha selection (Arch to confirm)',
    ('quantlab/beta/survivorship.py', '"delist_dates": {i: str(alive_later.loc[i, "delist_date"].date()) for i in hit},'):
        'B1 survivorship helper: re-includes later-delisted names (anti-survivorship ranking / terminal sensitivity) - accounting/universe audit, not alpha selection (Arch to confirm)',
    ('quantlab/beta/survivorship.py', '"delist_date": str(row["delist_date"].date()) if row["delist_date"] == row["delist_date"] else None,'):
        'B1 survivorship helper: re-includes later-delisted names (anti-survivorship ranking / terminal sensitivity) - accounting/universe audit, not alpha selection (Arch to confirm)',
    ('quantlab/portfolio/v2_multisleeve_book.py', 'dl = self.BAS.set_index("code").delist_date.dropna()'):
        'CB basic delist_date -> bond terminal payout (accounting; pre-SD1, in paper closure, unchanged)',
    ('scripts/smallcap_e7.py', "slippage=result['slippage'], turnover=result['turnover'], delist_events=len(result['events']),"):
        'report column label delist_events=len(engine events) (count only; no table read)',
    ('scripts/smallcap_info.py', "slippage=result['slippage'], turnover=result['turnover'], delist_events=len(result['events']),"):
        'report column label delist_events=len(engine events) (count only; no table read)',
    ('scripts/smallcap_audit.py', "delist_events=len(result['events']), median_gross=float(result['gross'][result['gross'] > 0].median()))"):
        'report column label delist_events (count only; no table read)',
    ('scripts/smallcap_audit.py', "columns = ['cagr', 'max_drawdown', *L.SEGMENTS, 'median_gross', 'fees', 'turnover', 'delist_events']"):
        'report column label delist_events (count only; no table read)',
    ('scripts/smallcap_layers.py', "delist_events=len(result['events']),"):
        'report column label delist_events (count only; no table read)',
    ('scripts/smallcap_layers.py', "columns = ['cagr', 'max_drawdown', *SEGMENTS, 'median_gross', 'fees', 'slippage', 'turnover', 'delist_events']"):
        'report column label delist_events (count only; no table read)',
    ('scripts/smallcap_parity.py', "delist_events=len(run['events']))"):
        'report column label delist_events (count only; no table read)',
}


# Research leaf scripts may cut their BENCHMARK POOL at delist_date only inside these functions (path, function name).
FUNC_WHITELIST = {
    ("research/g1g5_imax_intraday_alpha.py", "pool_benchmarks"):
        "主 Agent 02:44 裁定（基准池按 delist_date 截断）; Arch 2b8f81c9 §6.1-3",
    ("research/g1g5_sue_desens_cs_alpha.py", "pool_benchmarks"):
        "主 Agent 02:44 裁定（基准池按 delist_date 截断）; Arch 2b8f81c9 §6.1-3",
}


def _enclosing_functions(text: str) -> list:
    """(start, end, name) of every def; [] when the file does not parse (then no function whitelist applies)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _sha256(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def scan(files, *, forced_scope=False, rel_as: dict | None = None, scanned: list | None = None):
    """rel_as: {file: repo-relative path to treat it as} (synthetic T10 cases only).
    scanned: when a list is given, the repo-relative path of every file actually read is appended (r3.2 n_scanned)."""
    hits = []
    for f in files:
        f = Path(f)
        if rel_as and (str(f) in rel_as or f in rel_as):
            rel = rel_as.get(str(f), rel_as.get(f))
        else:
            try:
                rel = str(f.resolve().relative_to(ROOT))
            except ValueError:
                rel = str(f)
        if not forced_scope:
            if not any(rel == s or (s.endswith("/") and rel.startswith(s)) for s in SCOPE):
                continue
            if any(rel == w or (w.endswith("/") and rel.startswith(w)) for w in WHITELIST):
                continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if scanned is not None:
            scanned.append(rel)
        funcs = None
        for ln, line in enumerate(text.splitlines(), 1):
            if TOKENS.search(line):
                key = (rel, line.strip())
                if funcs is None:
                    funcs = _enclosing_functions(text)
                enc = [n for (a, b, n) in sorted(funcs) if a <= ln <= b]   # outermost first, innermost last
                fw = next((FUNC_WHITELIST[(rel, n)] for n in enc if (rel, n) in FUNC_WHITELIST), None)
                if forced_scope:
                    status, note = "VIOLATION", ""
                elif key in PREEXISTING:
                    status, note = "PREEXISTING", PREEXISTING[key]
                elif fw is not None:
                    status, note = "ALLOWED_FUNC", fw
                else:
                    status, note = "VIOLATION", ""
                hits.append(dict(path=rel, line=ln, text=line.strip()[:200], token=TOKENS.search(line).group(0),
                                 function=(enc[-1] if enc else "<module>"), status=status, note=note))
    return hits


_HEX64 = re.compile(r"[0-9a-f]{64}")


def _split_file_arg(item: str):
    """'PATH=SHA256' -> (PATH, SHA256); 'PATH' -> (PATH, None). Only a trailing '=<64 hex>' counts as a sha."""
    head, sep, tail = str(item).rpartition("=")
    if sep and _HEX64.fullmatch(tail):
        return head, tail
    return str(item), None


def pinned_scope(files, closure_json, closure_sha256: str, *, require_file_sha: bool = False) -> dict:
    """SD1 selftest T10 scope (Arch 2b8f81c9 §6.1-2): the given pinned files + the paper import closure. The closure
    list must match ``closure_sha256`` and every entry its recorded sha256, so the result depends only on pinned bytes.
    r3.2 (Arch e2e288bc P3-2): ``files`` items may be 'PATH=SHA256'; those files are re-hashed here (files_ok)."""
    pairs = [_split_file_arg(f) for f in files]
    files_mism = []
    for path, want in pairs:
        if want is None:
            if require_file_sha:
                files_mism.append(dict(path=str(path), pinned=None, now=None, why="no sha given (--require-file-sha)"))
            continue
        now = _sha256(path) if Path(path).exists() else None
        if now != want:
            files_mism.append(dict(path=str(path), pinned=want, now=now))
    n_sha_checked = sum(w is not None for _, w in pairs)
    files = [p for p, _ in pairs]
    cj = Path(closure_json)
    got = _sha256(cj)
    mism = []
    if got != closure_sha256:
        return dict(mode="pinned", closure_ok=False, closure_sha256=got, error=f"closure list sha256 {got} != {closure_sha256}",
                    files_ok=not files_mism, n_files_sha_checked=n_sha_checked, files_mismatch=files_mism,
                    n_files=0, n_scanned=0, n_scanned_research=0, n_hits=0, n_violations=0, hits=[], closure_mismatch=[])
    entries = json.loads(cj.read_text(encoding="utf-8"))
    for rel, sha in entries:
        f = ROOT / rel
        now = _sha256(f) if f.exists() else None
        if now != sha:
            mism.append(dict(path=rel, pinned=sha, now=now))
    rels = sorted({str(Path(f).resolve().relative_to(ROOT)) for f in files} | {rel for rel, _ in entries})
    read = []
    hits = scan([ROOT / r for r in rels], scanned=read)
    bad = [h for h in hits if h["status"] == "VIOLATION"]
    return dict(mode="pinned", closure_ok=not mism, closure_sha256=got, n_closure=len(entries),
                files_ok=not files_mism, n_files_sha_checked=n_sha_checked, files_mismatch=files_mism,
                n_files=len(rels), n_scanned=len(read), n_scanned_research=sum(r.startswith("research/") for r in read),
                n_hits=len(hits), n_violations=len(bad), n_preexisting=sum(h["status"] == "PREEXISTING" for h in hits),
                n_allowed_func=sum(h["status"] == "ALLOWED_FUNC" for h in hits), closure_mismatch=mism, hits=hits)


SPEC_SHA256 = "2e428f3956fcb6d2de8204a0b7226242763045afdd280a4d1e860bc6d0fbdb0b"


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()          # r3.2 (Arch e2e288bc P3-4)
    g.add_argument("--mode", choices=("disclosure", "pinned"), default=None)
    g.add_argument("--paths", nargs="+", default=None)
    ap.add_argument("--files", nargs="+", default=None)
    ap.add_argument("--require-file-sha", action="store_true")
    ap.add_argument("--closure", default=None)
    ap.add_argument("--closure-sha256", default=None)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    fail = False
    if a.paths is not None:
        hits = scan(a.paths, forced_scope=True)
        rep = dict(mode="paths", n_hits=len(hits), n_violations=sum(h["status"] == "VIOLATION" for h in hits), hits=hits)
        fail = rep["n_violations"] > 0
    elif a.mode == "pinned":
        if not (a.closure and a.closure_sha256 and a.files):
            ap.error("--mode pinned needs --closure, --closure-sha256 and --files")
        rep = pinned_scope(a.files, a.closure, a.closure_sha256, require_file_sha=a.require_file_sha)
        fail = rep["n_violations"] > 0 or not rep["closure_ok"] or not rep["files_ok"]
    else:   # disclosure (default): full-repo report, not a test gate
        files = [p for s in SCOPE for p in ((ROOT / s).rglob("*.py") if s.endswith("/") else [ROOT / s]) if p.exists()]
        read = []
        hits = scan(sorted(set(files)), scanned=read)
        bad = [h for h in hits if h["status"] == "VIOLATION"]
        rep = dict(mode="disclosure", n_files=len(set(files)), n_scanned=len(read), n_hits=len(hits), n_violations=len(bad),
                   n_preexisting=sum(h["status"] == "PREEXISTING" for h in hits),
                   n_allowed_func=sum(h["status"] == "ALLOWED_FUNC" for h in hits),
                   violations_by_file={f: sum(h["path"] == f for h in bad) for f in sorted({h["path"] for h in bad})},
                   note="disclosure only; never part of the SD1 selftest result (Arch 2b8f81c9 §6.1-3)", hits=hits)
        fail = a.strict and bool(bad)
    rep = dict(spec_sha256=SPEC_SHA256, **rep)
    out = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.json:
        Path(a.json).write_text(out, encoding="utf-8")
    print(out)
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
