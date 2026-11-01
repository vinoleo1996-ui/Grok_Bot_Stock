#!/usr/bin/env python3
"""Leaf24 imax_intraday — g1g5_ashare_imax_intraday_v1 (research leaf, not production; long-only, no short arm). Script r1 (Arch b997cba8 fixes).
Prereg: docs/v2/AI_G1G5_IMAX_OVERNIGHT_WHO_PAYS_PREREG_ZH.md (FROZEN 2026-10-18 01:44:40 ET; sha256 pinned below + in the Arch .ok).
r8 (Arch P2, 2026-10-18 ET, NOT RUN — static checks only): RSS watchdog also checks VmHWM (limit unchanged 1536000 kB) and an explicit
    peak check (VmHWM and ru_maxrss) runs at the end of each build year, each pool_benchmarks year and each universe in eval
    (RSS_GUARD_KILL, os._exit(137)); same code as leaf 23 r2.10 (d). No other change.
r9 (Arch 06:27, folds r8; NOT RUN — static checks only; RSS limit stays 1536000 kB; code kept structurally identical to leaf 23 r2.10):
    (a) eval split into one process per universe (--stage eval --uni HILIQ, then --uni FULLA) + --stage merge (combines the per-universe
        summaries into summary_<stamp>.json and writes eval_meta.json); chain eval_HILIQ ← build_HILIQ+build_FULLA, eval_FULLA ← same
        + eval_HILIQ, merge ← both eval_<uni>; a sensitivity's first stage needs the primary eval_HILIQ, eval_FULLA and eval (merge) metas;
    (b) reads reduced to rows/columns that can matter: build reads the leaf18/18v α files per build year (date in [max(X2 start, Jan 1 y),
        Jan 1 y+1)) instead of the whole X2 range once; eval PX drops logmv/<uni col> (never used from PX); pick_book merges only
        rebalance-day α/gate rows; the overlap section reads the leaf18/18v α files only for the instruments held in their own weight
        file (the merge is a left join on the held rows, so every matched row and every NaN is the same; a rebalance-day-only read
        would turn non-rebalance held rows into NaN and change held_alpha_missing_share); no dtype change;
    (c) build frees Q after the e_id loop, ER after its pivots, Ee/Lu after imax_window, drops P.logmv/adv20_yuan after the style
        pivots; allocator trim (gc + pyarrow pool release_unused + malloc_trim) at segment ends and at the end of every build year;
        pool_benchmarks = leaf 23 r2.10 version (per-year frames freed early + trim); FE return cache loaded once per eval process and
        kept (was cleared and re-read after every book);
    (d) watchdog (VmRSS + VmHWM) and per-segment peak checks as r8.
    No numerical change intended in any stage.
r10 (Arch r9 review b771b4be CONDITIONAL PASS + B3 diagnosis 561219c7; NOT RUN — static checks only):
    P1-1 pool_benchmarks B3 fix byte-identical with leaf 23 r2.11 (4aa19627): carry on every mask-suspended day (no row or restored row),
        mcap anchors follow the same carry, hard stop unless mask suspended <=> row_origin=restored on every panel row (panel row without
        mask row also stops), carried name-days counted on (S & sus==1); every function shared with leaf 23 r2.11 is byte-identical
        (rss_watchdog / peak_check / trim / merge / pick_book / rank_ind docstrings and the read_panel refusal message text made identical —
        comment/message-only changes);
    P2-1 the r9 P.drop(logmv, adv20_yuan) is removed (it freed nothing: pandas 3.0.6 keeps the shared float32 block alive); instead the
        year-y filter (same condition, same .copy()) is taken right after Q is built and before the e_id loop, and the full P is dropped
        at once (P is rebound to the filtered frame);
    P3 watchdog fail-closed (shared code); explicit refusal when a leaf18/18v weight file yields no held names or a NaN instrument.
    No numerical change intended.
Written 2026-10-18 ET by QuantLab AI. NOT RUN at write time (syntax check only). Same guards as leaf 23 r2.1: every stage refuses
to start without an Arch run-auth .ok (quantlab_run_auth_v1) pinning (64-hex, recomputed at runtime) this script, the prereg,
cs_panel_dir + cs_panel_manifest_sha256, the evaluation tools and the leaf18/18v X2 α files.

PRIMARY (prereg §3): r_id = (1+ret)/(1+ret_on) − 1 (overnight component removed); e_id = daily pool OLS residual of r_id on
    SW L1 dummies + logmv_{t−1} (in-mask rows only; resume rows never enter the signal); IMAX_t = mean of the 5 largest e_id over
    [t−19, t] (≥15 valid); signal = −IMAX, within-SW-L1 rank → normal quantile; financials INCLUDED (no ex-fin in primary).
    Residualize (主 Agent 02:23 + ~02:33): SW L1 + Alpha frozen style set (logmv_{t−1}, beta120_{t−1}, mom t−120→t−20 at t−1, logADV20 = mean t−20..t−1) + vol20_{t−1} + leaf18 α + leaf18v α (missing 0); size-domain rank →
    resid on ind + logmv_{t−1} → size-domain rank = base-α. Gate: 3-day ind+logmv_{t−1} residual-return left tail 5% (not in α).
SENSITIVITIES (disclosure only; .ok allow_sensitivity=true): --src total (overnight kept), --k 1, --win 60 (≥45 valid), --ex-fin.
Limit-up: not corrected; the share of limit-up days among each name's IMAX top-k days is stored and MUST be reported (prereg §3.4).
Panel: output/ai_factory/panel_cache_v2_resumefix only; is_resume_day/hiliq_carry never read by build (asserted); eval uses
    is_resume_day only as the no-new-buy entry gate + disclosure, hiliq_carry only for disclosure counts.
Books: top-6 (60万) / top-10 (100万) re-picked from gate=1 list, 6% each, industry ≤25% (Arch leaf-23 review 0d9bd147 l.96, P1-3;
    same as leaf 23 r2.1), remainder 510300; 20%-cap books + 20×4% book disclosure only.
Benchmarks: capadv-HI_LIQ single-leg (filed + recomputed; recomputed decides), HI_LIQ wb (T−1 members/mcap × T ret), 510300; pool EW.
Decisive (§9): HI_LIQ primary; both tiers net CAGR > HI_LIQ wb (else FAIL) and HAC t (lag 19) of daily net excess vs wb ≥ 2.50 in
    both tiers (else ≤ WATCH). X2 only; sealed window not implemented (--sealed exits). Year-chunked; 1.5GB RSS kill; serial.
r1 (Arch b997cba8, 2026-10-18 ET, NOT RUN — py_compile only): B2 only <panel>/manifest.json + step/mode + RECEIPT_D1b_resume_execute.json
    PASS/manifest sha; B3 pool EW/wb carry pre-suspension membership + float mcap through suspension (not after delisting), assert Mp ==
    hiliq_carry/fulla_carry on restored resume rows (stop on mismatch), old no-carry construction disclosed; N1 ic_tstat_hac inlined +
    alpha_decay_gate/leaf_selfcheck_common pinned; N2 leaf18/18v eval_weights, capadv target_weights/nav, etf_daily_adj pinned and re-hashed
    before use; N3 Jaccard ranks leaf18/18v names by their own α; N5 strict .ok parser + explicit keys; N6 non-empty out_dir refused + stage
    meta chain; N7 ret_on missing → r_id NaN (no fillna(0)); N8 ind_names.csv only from the panel dir. File name says IMAX_OVERNIGHT but the
    factor REMOVES the overnight component (intraday IMAX).
fix-2 (Arch 129d67c5, NOT RUN — py_compile only): P1-1 B3 state recursed from 2018, carry only on mask-suspended no-row days, mask pinned
    (data_mask_sha256 == D1b receipt pins.mask_sha256), carried name-days by mask reason must all be suspended; P1-2 variant must be one item of
    sensitivity_specs; P1-3/P2-4 process check (research/ python, scripts/fix_sd1/, scripts_eng/, scripts/nightly_update.py block; scripts/acquire/
    logged; ancestors excluded; niceness ≥ 10; MemAvailable ≥ 2GB; ps snapshot in meta); P2-1 .ok whitelist + fixed values + tool_cmds file;
    P2-2 stage chains across variants (and leaf 24 after leaf 23); P2-3 exclusive create; P2-6 all years 2018–2026 verified;
    P3 asserts → raise, carry_col for FULLA, panel re-hash per stage, limit-up 30*/688/689 (P2-5), rebalance-day limit-up share.
"""
import argparse, hashlib, json, os, re, sys, gc, threading, time, resource, ctypes
import numpy as np, pandas as pd, pyarrow as pa
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
from statistics import NormalDist
from numpy.lib.stride_tricks import sliding_window_view

R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
PREREG = R/"docs/v2/AI_G1G5_IMAX_OVERNIGHT_WHO_PAYS_PREREG_ZH.md"
PREREG_SHA = "c289e77068be607c108359a87e1d17d6b2e8edac9e4cbcca865a9a49430133a8"
PANEL_VERSION = "cs_panel_v2_resumefix"; REJECT_PANELS = {"panel_cache", "panel_cache_v2_fixesnone"}
FORBIDDEN_SIGNAL_COLS = {"is_resume_day", "hiliq_carry"}
L18 = {"HILIQ": R/"output/ai_factory/leaf18_overnight_idio_ivol/alpha_HILIQ_x2_20261014_205327.parquet",
       "FULLA": R/"output/ai_factory/leaf18_overnight_idio_ivol/alpha_FULLA_x2_20261014_205512.parquet"}
L18V = {"HILIQ": R/"output/ai_factory/leaf18v_overnight_idio_ivol_lowto/alpha_HILIQ_x2_20261014_212630.parquet",
        "FULLA": R/"output/ai_factory/leaf18v_overnight_idio_ivol_lowto/alpha_FULLA_x2_20261014_214401.parquet"}
L18_W = {"leaf18": {"HILIQ": R/"output/ai_factory/leaf18_overnight_idio_ivol/eval_weights_HILIQ_x2_20261014_205327.parquet",
                    "FULLA": R/"output/ai_factory/leaf18_overnight_idio_ivol/eval_weights_FULLA_x2_20261014_205512.parquet"},
         "leaf18v": {"HILIQ": R/"output/ai_factory/leaf18v_overnight_idio_ivol_lowto/eval_weights_HILIQ_x2_20261014_212630.parquet",
                     "FULLA": R/"output/ai_factory/leaf18v_overnight_idio_ivol_lowto/eval_weights_FULLA_x2_20261014_214401.parquet"}}
CAPADV = {6: R/"output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK", 10: R/"output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK"}
ETF = R/"data/v2/etf/etf_daily_adj.parquet"; MASK = R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
DELISTED = R/"data/v2/delisted/delisted_master_tushare.parquet"   # Arch bd3abe5c P1-A (63590f23… at review)
L18_A = {"leaf18": L18, "leaf18v": L18V}; L18_KEY = {"leaf18": "l18", "leaf18v": "l18v"}
TOOLS = {"dep_fe_sha256": R/"research/g1g5_fund_resid_alpha.py", "dep_selfcheck_sha256": R/"research/leaf_selfcheck_v3.py",
         "dep_combo_sha256": R/"research/alpha_combo_marginal_v1_1.py", "dep_combo_legacy_sha256": R/"research/alpha_combo_marginal.py",   # CMC v1.1 r3 / legacy bee23019 (comparison column only)
         "dep_adg_sha256": R/"research/alpha_decay_gate.py", "dep_lc_sha256": R/"research/leaf_selfcheck_common.py",   # N1 import closure of leaf_selfcheck_v3
         "dep_l18_hiliq_sha256": L18["HILIQ"], "dep_l18_fulla_sha256": L18["FULLA"],
         "dep_l18v_hiliq_sha256": L18V["HILIQ"], "dep_l18v_fulla_sha256": L18V["FULLA"],
         "dep_l18w_hiliq_sha256": L18_W["leaf18"]["HILIQ"], "dep_l18w_fulla_sha256": L18_W["leaf18"]["FULLA"],           # N2
         "dep_l18vw_hiliq_sha256": L18_W["leaf18v"]["HILIQ"], "dep_l18vw_fulla_sha256": L18_W["leaf18v"]["FULLA"],
         "dep_capadv600_tw_sha256": CAPADV[6]/"target_weights.parquet", "dep_capadv600_nav_sha256": CAPADV[6]/"nav.csv",
         "dep_capadv1000_tw_sha256": CAPADV[10]/"target_weights.parquet", "dep_capadv1000_nav_sha256": CAPADV[10]/"nav.csv",
         "data_etf_daily_adj_sha256": ETF, "data_mask_sha256": MASK, "data_delisted_sha256": DELISTED}
LEAF_NO = "24"; OUT_ROOT = R/"output/ai_factory/leaf24_imax_intraday"; D1B_STEP = "D1b_resume_execute"; PANEL_YEARS = tuple(range(2018, 2027))   # P2-6: every year the B3 recursion reads
CMC_V11_SHA = "5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911"      # Alpha handoff ab6d1e82 r3; passed Arch review bbfcb7ef; full-run .ok not yet signed
CMC_LEGACY_SHA = "bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c"   # old alpha_combo_marginal.py: disclosure-only comparison column
OK_LINE = re.compile(r"^([a-z0-9_]+)=(\S+)$")
AIF = R/"output/ai_factory"; TOOL_CMDS = AIF/f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"   # Alpha 77441f16 P1: f-string (was literal {LEAF_NO})   # Arch 129d67c5 §5-1: tool command lines live in a pinned .cmd file
TOOL_CLOSURE = {"tool_closure_adj_price_sha256": R/"research/adj_price.py", "tool_closure_panel_stitch_sha256": R/"research/g1g5_x2_panel_stitch.py",
                "tool_closure_moneyflow_sha256": R/"research/g1g5_moneyflow_resid_weights.py", "tool_closure_nontextbook_sha256": R/"research/g1g5_nontextbook_weights.py"}
X2S, X2E = "2024-06-03", "2026-10-09"   # Alpha 486496a9 P1-1: assigned before OK_FIXED reads them (values unchanged)
OK_FIXED = {"format": "quantlab_run_auth_v1", "signed_by": "arch", "scope": "X2", "leaf": LEAF_NO, "live": "false", "promotion": "false",
            "promotion_approved": "false", "allow_full": "true", "allow_smoke": "false", "allow_sealed": "false", "cs_panel_build_version": PANEL_VERSION,
            "mechanism_tag": "g1g5_ashare_imax_intraday_v1", "window_start": X2S, "window_end": X2E, "rss_limit_mb": "1500",
            "serial_order": "after_leaf23_complete>build_HILIQ>build_FULLA>eval_HILIQ>eval_FULLA>merge>sensitivities", "sensitivity_specs": "src-total,k1,win60,exfin", "run_niceness": "10",
            "tool_cmds_path": str(TOOL_CMDS), "research_only": "true"}   # N5 / P2-1: explicit, fixed values
OK_REQUIRED = ("script_sha256", "prereg_sha256", "cs_panel_dir", "cs_panel_manifest_sha256", "out_dir", "allow_sensitivity", "tool_cmds_sha256", "issued_at", "expires_et")
BLOCK_CMDS = ("scripts/fix_sd1/", "scripts_eng/", "scripts/nightly_update.py"); LOG_ONLY_CMDS = ("scripts/acquire/",)
MIN_NICE, MIN_MEMAVAIL_KB = 10, 2*1024*1024
TIERS = {6: 600_000, 10: 1_000_000}; TIER_W, TIER_IND_CAP, DISC_N, DISC_W, CORE_IND_CAP = 0.06, 0.25, 20, 0.04, 0.20
YEARS = (2024, 2025, 2026)
RSS_LIMIT_KB, T_DECISIVE, HAC_H, LIMIT_EPS = 1536000, 2.50, 20, 0.002
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ND = NormalDist()


# ---------------------------------------------------------------- guards (same as leaf 23 r2.1)
def vm_status():
    """VmRSS / VmHWM (kB) from /proc/self/status."""
    d = {}
    for l in open("/proc/self/status"):
        if l.startswith(("VmRSS:", "VmHWM:")): d[l.split(":")[0]] = int(l.split()[1])
    return d


def rss_watchdog():
    """Kill on current RSS or on the high-water mark (VmHWM), so a peak between two samples is not missed; any read error also kills (fail-closed)."""
    def loop():
        while True:
            try:
                v = vm_status()
                if v["VmRSS"] > RSS_LIMIT_KB or v["VmHWM"] > RSS_LIMIT_KB:
                    print(f"RSS_GUARD_KILL rss_kb={v['VmRSS']} hwm_kb={v['VmHWM']} (limit {RSS_LIMIT_KB})", flush=True); os._exit(137)
            except Exception as ex:   # r2.11 (P3): fail-closed instead of silently disabling the guard
                print(f"RSS_WATCHDOG_ERROR {type(ex).__name__}: {ex}", flush=True); os._exit(137)
            time.sleep(1)
    threading.Thread(target=loop, daemon=True).start()


def peak_check(tag):
    """Explicit peak check at segment ends (VmHWM and ru_maxrss); over the limit → same kill as the watchdog."""
    v = vm_status(); mx = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if v["VmHWM"] > RSS_LIMIT_KB or mx > RSS_LIMIT_KB:
        print(f"RSS_GUARD_KILL at {tag} hwm_kb={v['VmHWM']} maxrss_kb={mx} (limit {RSS_LIMIT_KB})", flush=True); os._exit(137)
    print(f"peak_check {tag} rss_kb={v['VmRSS']} hwm_kb={v['VmHWM']}", flush=True)


try: _LIBC = ctypes.CDLL("libc.so.6")
except OSError: _LIBC = None


def trim():
    """Hand freed memory back to the OS (gc + pyarrow pool + glibc heap); no effect on any value."""
    gc.collect(); pa.default_memory_pool().release_unused()
    if _LIBC is not None: _LIBC.malloc_trim(0)


def ancestors():
    """own pid + full ancestor chain (Arch P2-4: wrappers carry 'research/' in their cmdline too)."""
    out, p = set(), os.getpid()
    while p > 1 and p not in out:
        out.add(p)
        try: p = int(Path(f"/proc/{p}/stat").read_text().rsplit(")", 1)[1].split()[1])
        except Exception: break
    return out


def process_check():
    """Arch P1-3/P2-4 (129d67c5 §5-4). Refuse if another process cmdline has 'research/' (python) or scripts/fix_sd1/, scripts_eng/,
    scripts/nightly_update.py; scripts/acquire/ resident fetchers are only logged. Own ancestor chain excluded. Refuse if own niceness < 10
    or MemAvailable < 2GB. Returns the ps snapshot + niceness for the stage meta."""
    anc = ancestors(); busy, logged, snap = [], [], []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit() or int(p.name) in anc: continue
        try:
            cmd = (p/"cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore").strip()
            st = (p/"stat").read_text().rsplit(")", 1)[1].split(); pn = int(st[16]); rkb = int(st[21])*os.sysconf("SC_PAGE_SIZE")//1024
        except Exception: continue
        if not cmd: continue
        hit = ("python" in cmd and "research/" in cmd) or any(t in cmd for t in BLOCK_CMDS); log = any(t in cmd for t in LOG_ONLY_CMDS)
        if hit or log or "python" in cmd: snap.append(dict(pid=int(p.name), nice=pn, rss_mb=round(rkb/1024, 1), cmd=cmd[:200]))
        if hit: busy.append((p.name, cmd[:160]))
        elif log: logged.append((p.name, cmd[:160]))
    mem_kb = int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1]); nice = os.nice(0)
    if busy: raise SystemExit(f"refused: blocking job running {busy[:3]} (one full-window job at a time; nightly/fix_sd1/eng/research)")
    if nice < MIN_NICE: raise SystemExit(f"refused: niceness {nice} < {MIN_NICE} (run under nice -n 10)")
    if mem_kb < MIN_MEMAVAIL_KB: raise SystemExit(f"refused: MemAvailable {mem_kb//1024}MB < 2048MB")
    return dict(niceness=nice, mem_available_mb=mem_kb//1024, log_only_resident=logged, ps_snapshot=snap)


def read_ok(path):
    """Arch N5: strict quantlab_run_auth_v1 parser. Every non-empty line must match ^[a-z0-9_]+=\\S+$ (no BOM, no comments, no spaces,
    no inline comments). BOM, duplicate key, empty value or any malformed line → refuse. Required keys/values are checked in authorize()."""
    raw = Path(path).read_bytes()
    if b"\xef\xbb\xbf" in raw: raise SystemExit("refused: .ok contains a BOM (U+FEFF)")
    kv = {}
    for n, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if line == "": continue
        if "=" in line and line.split("=", 1)[1].strip() == "": raise SystemExit(f"refused: .ok line {n} has an empty value: {line[:60]!r}")
        m = OK_LINE.match(line)
        if not m: raise SystemExit(f"refused: .ok line {n} is not ^[a-z0-9_]+=\\S+$: {line[:60]!r}")
        if m.group(1) in kv: raise SystemExit(f"refused: .ok key {m.group(1)!r} appears more than once (line {n})")
        kv[m.group(1)] = m.group(2)
    return kv


def is_primary(a): return a.src == "intra" and a.k == 5 and a.win == 20 and not a.ex_fin


def variant_tag(a):
    t = [] if a.src == "intra" else ["src-total"]
    if a.k != 5: t.append(f"k{a.k}")
    if a.win != 20: t.append(f"win{a.win}")
    if a.ex_fin: t.append("exfin")
    return "_".join(t) or "primary"


def verify_panel(panel, ok):
    """P0-1/P0-2 + Arch B2 + P2-6: only <panel>/manifest.json, sha == .ok cs_panel_manifest_sha256, step == D1b_resume_execute, mode == execute,
    version/fixes/status; RECEIPT_D1b_resume_execute.json status PASS, manifest_sha256 == .ok value, pins.mask_sha256 == .ok data_mask_sha256;
    every year actually read (2018–2026) sha == manifest + build_version; N8: ind_names.csv only from this panel dir, sha == manifest."""
    if panel.name in REJECT_PANELS: raise SystemExit(f"refused: panel {panel.name} is not the rebuilt {PANEL_VERSION}")
    if Path(ok["cs_panel_dir"]).resolve() != panel: raise SystemExit(f"refused: --panel-dir {panel} != .ok cs_panel_dir {ok['cs_panel_dir']}")
    mf, rf, want = panel/"manifest.json", panel/f"RECEIPT_{D1B_STEP}.json", ok["cs_panel_manifest_sha256"]
    if not mf.is_file(): raise SystemExit(f"refused: {mf} missing (Data D1b execute output required)")
    msha = sha(mf)
    if msha != want: raise SystemExit(f"refused: manifest.json sha {msha[:12]} != .ok cs_panel_manifest_sha256 {want[:12]}")
    man = json.loads(mf.read_text(encoding="utf-8"))
    if man.get("step") != D1B_STEP or man.get("mode") != "execute": raise SystemExit(f"refused: manifest step/mode {man.get('step')}/{man.get('mode')}")
    if man.get("version") != PANEL_VERSION or man.get("fixes") != "resume" or man.get("status") != "PASS":
        raise SystemExit(f"refused: manifest version/fixes/status {man.get('version')}/{man.get('fixes')}/{man.get('status')}")
    if not rf.is_file(): raise SystemExit(f"refused: {rf.name} missing")
    rec = json.loads(rf.read_text(encoding="utf-8"))
    if rec.get("step") != D1B_STEP or rec.get("status") != "PASS" or rec.get("manifest_sha256") != want:
        raise SystemExit(f"refused: {rf.name} step/status/manifest_sha256 {rec.get('step')}/{rec.get('status')}/{str(rec.get('manifest_sha256'))[:12]}")
    if (rec.get("pins") or {}).get("mask_sha256") != ok["data_mask_sha256"]:
        raise SystemExit("refused: .ok data_mask_sha256 != D1b receipt pins.mask_sha256 (Arch P1-1 §3-6)")
    ind = panel/"ind_names.csv"
    if not ind.is_file() or sha(ind) != man.get("ind_names_sha256"): raise SystemExit("refused: <panel>/ind_names.csv missing or sha != manifest ind_names_sha256 (N8: no v1 fallback)")
    years = {}
    for y in PANEL_YEARS:
        f = panel/f"cs_panel_{y}.parquet"; wy = man.get("years", {}).get(str(y), {}).get("sha256")
        if not f.exists() or wy != sha(f): raise SystemExit(f"refused: {f.name} sha does not match manifest")
        bv = pd.read_parquet(f, columns=["build_version"]).build_version.unique()
        if list(bv) != [PANEL_VERSION]: raise SystemExit(f"refused: {f.name} build_version {bv}")
        years[str(y)] = wy
    return dict(manifest=str(mf), manifest_sha256=msha, receipt=str(rf), receipt_sha256=sha(rf), version=man["version"], ind_names_sha256=sha(ind), years=years)


def panel_recheck(auth, panel):
    """Arch P3-5: re-hash every panel year file (and the pinned mask / delisted master) against the manifest right before a stage reads
    them; Arch bd3abe5c P2-A: the .ok must not have expired at the start of any stage."""
    if not not_expired(auth["expires_et"]): raise SystemExit(f"refused: Arch .ok expired (expires_et={auth['expires_et']})")
    for y, h in auth["cs_panel"]["years"].items():
        if sha(panel/f"cs_panel_{y}.parquet") != h: raise SystemExit(f"refused: cs_panel_{y}.parquet changed since authorize")
    repin(auth, "data_mask_sha256", "data_delisted_sha256")


def out_dir(a): return OUT_ROOT if is_primary(a) else OUT_ROOT.with_name(OUT_ROOT.name + "_" + variant_tag(a))


def tz_iso(v):
    try: d = datetime.fromisoformat(v)
    except ValueError: return False
    return d.tzinfo is not None and d.utcoffset() is not None


def not_expired(v):
    """Arch bd3abe5c P2-A: tz-aware expires_et still in the future."""
    if not tz_iso(v): return False
    return datetime.fromisoformat(v) > datetime.now().astimezone()


def cmc_cmd_ok(p):
    """Alpha handoff §5 / Arch: the pinned tool .cmd must run CMC v1.1 with --arch-ok (any legacy bee23019 line = comparison column only)."""
    if not Path(p).is_file(): return False
    ls = [l for l in Path(p).read_text(encoding="utf-8").splitlines() if "alpha_combo_marginal" in l and not l.lstrip().startswith("#")]
    v11 = [l for l in ls if "alpha_combo_marginal_v1_1.py" in l]
    return bool(v11) and all("--arch-ok" in l for l in v11)


def authorize(a):
    panel = Path(a.panel_dir).resolve()
    if not panel.is_dir(): raise SystemExit(f"--panel-dir {panel} not found (rebuilt cs_panel from Data required)")
    if not a.arch_ok or not Path(a.arch_ok).is_file(): raise SystemExit("refused: Arch run-auth .ok required (--arch-ok)")
    ok = read_ok(a.arch_ok); me = sha(__file__); pr = sha(PREREG)
    allowed = set(OK_FIXED) | set(OK_REQUIRED) | set(TOOLS) | set(TOOL_CLOSURE)
    unknown = sorted(set(ok) - allowed)
    if unknown: raise SystemExit(f"refused: .ok has unknown keys {unknown} (P2-1 whitelist)")
    miss = [k for k in sorted(allowed) if k not in ok]
    if miss: raise SystemExit(f"refused: .ok lacks required keys {miss} (N5/P2-1: must be explicit)")
    checks = {k: ok[k] == v for k, v in OK_FIXED.items()}
    checks["script_sha256"] = ok["script_sha256"] == me; checks["prereg_sha256"] = ok["prereg_sha256"] == PREREG_SHA == pr
    checks["out_dir"] = Path(ok["out_dir"]).resolve() == OUT_ROOT.resolve()   # primary dir; sensitivity variants use <out_dir>_<variant>
    checks["allow_sensitivity"] = ok["allow_sensitivity"] in ("true", "false")
    checks["issued_at"] = tz_iso(ok["issued_at"])
    checks["expires_et"] = not_expired(ok["expires_et"]) and checks["issued_at"] and datetime.fromisoformat(ok["expires_et"]) > datetime.fromisoformat(ok["issued_at"])
    checks["tool_cmds_sha256"] = len(ok["tool_cmds_sha256"]) == 64 and TOOL_CMDS.is_file() and ok["tool_cmds_sha256"] == sha(TOOL_CMDS)
    checks["tool_cmds_cmc_v1_1_arch_ok"] = cmc_cmd_ok(TOOL_CMDS)
    checks["dep_combo_is_v1_1_r3"] = ok["dep_combo_sha256"] == CMC_V11_SHA; checks["dep_combo_legacy_is_bee23019"] = ok["dep_combo_legacy_sha256"] == CMC_LEGACY_SHA
    for k, f in {**TOOLS, **TOOL_CLOSURE}.items(): checks[k] = len(ok[k]) == 64 and Path(f).is_file() and ok[k] == sha(f)
    if not is_primary(a):   # P1-2: single-factor variant, exactly one item of sensitivity_specs
        checks["allow_sensitivity_true"] = ok["allow_sensitivity"] == "true"
        checks["variant_in_sensitivity_specs"] = variant_tag(a) in ok["sensitivity_specs"].split(",")
    bad = [k for k, v in checks.items() if not v]
    if bad: raise SystemExit(f"refused: Arch .ok check failed {bad} (script {me[:12]}, prereg {pr[:12]}, variant {variant_tag(a)})")
    pm = verify_panel(panel, ok)
    proc = process_check()
    rss_watchdog()
    AUTH_TOOLS.update({k: sha(f) for k, f in TOOLS.items()})
    return panel, dict(script_sha256=me, prereg_sha256=pr, arch_ok=str(Path(a.arch_ok).resolve()), arch_ok_sha256=sha(a.arch_ok), cs_panel=pm,
                       tools={k: sha(f) for k, f in TOOLS.items()}, tool_closure={k: sha(f) for k, f in TOOL_CLOSURE.items()},
                       tool_cmds=str(TOOL_CMDS), tool_cmds_sha256=sha(TOOL_CMDS), issued_at=ok["issued_at"], expires_et=ok["expires_et"], process=proc,
                       variant=variant_tag(a), primary=is_primary(a), out_dir=str(out_dir(a)))


def repin(auth, *keys):
    """Arch N2: re-hash pinned inputs right before they are read (no gap between authorize and use)."""
    for k in keys:
        if sha(TOOLS[k]) != auth["tools"][k]: raise SystemExit(f"refused: pinned input {k} changed since authorize ({TOOLS[k]})")


def xtext(p, s):
    """Arch P2-3: exclusive create — never overwrite."""
    with open(p, "x", encoding="utf-8") as f: f.write(s)


def xparquet(df, p):
    with open(p, "xb") as f: df.to_parquet(f, index=False)


def write_meta(out, stage, auth, files, upstream, **extra):
    """Arch N6: stage meta = script/.ok/prereg/manifest sha + variant + sha of every output + upstream meta shas (paths relative to
    output/ai_factory) + tool_cmds sha + niceness + ps snapshot (P2-4)."""
    m = dict(stage=stage, script_sha256=auth["script_sha256"], arch_ok_sha256=auth["arch_ok_sha256"], prereg_sha256=auth["prereg_sha256"],
             cs_panel_manifest_sha256=auth["cs_panel"]["manifest_sha256"], variant=auth["variant"], outputs={f: sha(out/f) for f in files},
             upstream=upstream, tool_cmds_sha256=auth["tool_cmds_sha256"], niceness=auth["process"]["niceness"],
             mem_available_mb=auth["process"]["mem_available_mb"], ps_snapshot=auth["process"]["ps_snapshot"],
             log_only_resident=auth["process"]["log_only_resident"], peak_rss_mb=rss(), **extra)
    xtext(out/f"{stage}_meta.json", json.dumps(m, ensure_ascii=False, indent=1, default=float))


def check_meta(mf, want):
    """verify one stage meta: listed fields, every output (relative to the meta's dir) and every upstream meta (relative to output/ai_factory)."""
    if not mf.is_file(): raise SystemExit(f"refused: required stage meta {mf} missing (serial order)")
    m = json.loads(mf.read_text(encoding="utf-8"))
    bad = [k for k, v in want.items() if m.get(k) != v]
    if bad: raise SystemExit(f"refused: {mf} mismatch {bad} (produced by another script/.ok/panel/variant)")
    for f, h in m.get("outputs", {}).items():
        if not (mf.parent/f).is_file() or sha(mf.parent/f) != h: raise SystemExit(f"refused: output {f} of {mf} changed or missing")
    for f, h in m.get("upstream", {}).items():
        if not (AIF/f).is_file() or sha(AIF/f) != h: raise SystemExit(f"refused: upstream {f} of {mf} changed or missing")
    return m


def same_run(auth, **kw):
    return dict(script_sha256=auth["script_sha256"], arch_ok_sha256=auth["arch_ok_sha256"], prereg_sha256=auth["prereg_sha256"],
                cs_panel_manifest_sha256=auth["cs_panel"]["manifest_sha256"], **kw)


def verify_upstream(out, auth, stages):
    up = {}
    for st in stages:
        mf = out/f"{st}_meta.json"; check_meta(mf, same_run(auth, stage=st, variant=auth["variant"])); up[str(mf.relative_to(AIF))] = sha(mf)
    return up


def verify_primary_eval(auth):
    """Arch P2-2 (r2.10 split): a sensitivity variant's first stage requires the primary eval_HILIQ, eval_FULLA and eval (merge) metas
    (same script/.ok/manifest, variant primary) and records their sha."""
    up = {}
    for st in ("eval_HILIQ", "eval_FULLA", "eval"):
        mf = OUT_ROOT/f"{st}_meta.json"; check_meta(mf, same_run(auth, stage=st, variant="primary")); up[str(mf.relative_to(AIF))] = sha(mf)
    return up


def guard_fresh(out, patterns):
    hits = sorted({p.name for pat in patterns for p in out.glob(pat)})
    if hits: raise SystemExit(f"refused: outputs of this stage already exist {hits[:5]} (N6: no silent overwrite; Arch decides on cleanup)")


# ---------------------------------------------------------------- helpers
def read_panel(panel, y, cols, lo=None):
    if set(cols) & FORBIDDEN_SIGNAL_COLS: raise RuntimeError("signal/selection code must not read is_resume_day/hiliq_carry (P2-8)")
    flt = [("date", ">=", pd.Timestamp(lo).to_pydatetime())] if lo is not None else None
    x = pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=cols, filters=flt); x["date"] = pd.to_datetime(x.date); return x


def rank_ind(v, ind):
    """within-SW-L1 rank → normal quantile; groups < 5 or NaN → 0 (prereg r2 §4.2)."""
    out = np.zeros(len(v))
    for k in np.unique(ind):
        i = np.where((ind == k) & np.isfinite(v))[0]
        if len(i) < 5: continue
        r = (pd.Series(v[i]).rank(method="average").to_numpy() - 0.5)/len(i)
        out[i] = [ND.inv_cdf(min(max(p, 1e-6), 1-1e-6)) for p in r]
    return out


def ic_tstat_hac(ic, h):
    """Arch N1: inlined verbatim from research/leaf_selfcheck_v3.py (ecaa30d8…) so this script no longer imports leaf_selfcheck_v3
    (whose import executes alpha_decay_gate.py / leaf_selfcheck_common.py). Newey-West (Bartlett), lag = h−1 (floor 1)."""
    x = np.asarray(ic, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 10: return None
    lag = max(h - 1, 1); u = x - x.mean(); v = u @ u / n
    for k in range(1, min(lag, n - 1) + 1): v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return float(x.mean() / np.sqrt(v / n)) if v > 0 else None


def hac_t(x, h=HAC_H): return ic_tstat_hac(np.asarray(x, float), h)


def load_fin(panel):
    """B1/N8: SW L1 codes of banks + non-bank financials, from the panel's own ind_names.csv only (sha checked in verify_panel)."""
    names = pd.read_csv(panel/"ind_names.csv").iloc[:, 0].tolist()
    fin = {i for i, n in enumerate(names) if n in ("银行", "非银金融")}
    if len(fin) != 2: raise SystemExit(f"STOP: FIN must hold exactly 2 SW L1 codes, got {fin}")
    return fin


def repin_file(p, key):
    """re-hash a pinned file right before reading it inside a helper that does not see auth (value pinned at authorize via AUTH_TOOLS)."""
    if sha(p) != AUTH_TOOLS.get(key): raise SystemExit(f"refused: pinned input {key} changed since authorize ({p})")


AUTH_TOOLS = {}


def pool_benchmarks(panel, PX, col, carry_col, rr, s, e):
    """Arch P1-1 (129d67c5 §3; replaces the r2.2 'no row = carry'). Membership state S(i,d), recursed year by year from 2018
    (one state vector carried across years, no seed window):
      mask suspended=True (no panel row, or a restored panel row) → S = previous S (carry through the suspension; Arch 561219c7);
      other panel row                            → S = that row's col;
      panel row: mask suspended=True <=> row_origin=restored; panel row without mask row → STOP (hard assert);
      no panel row, mask row with suspended=False (ST / adv / young) → S = False and the carry chain breaks;
      no mask row                                → S = False (defensive only: the mask is a rectangular grid, Arch bd3abe5c §5-1);
      day > delist_date in delisted_master       → S = False and the MV chain breaks (主 Agent 02:44 / Arch spec: PRIMARY cut = delist_date;
                                                   last_trade_date < d <= delist_date stays mask-suspended → carried, return 0, kept in the
                                                   denominator per prereg). Missing delist_date: in X2 → stop, else disclose (no fallback).
                                                   Shadow = last_trade_date cut, disclosure only (EW/wb diffs computed here, into diag).
    Float mcap is carried only inside suspension spans (last panel-row logmv before the span), otherwise follows S.
    Mp = S.shift(1); wv = MV.shift(1)·Mp. Frames on idx × U (U = every name seen). Also returns the old (no carry) and r2.2 (no row = carry)
    constructions for disclosure, carried name-days by mask reason (must all be suspended) and the restored-resume-row check vs carry_col."""
    idx = rr.index   # Alpha P3-2: the caller's return pivot is reused (one idx × U return frame, returned as r0)
    lo = idx[0]; sp, mp_ = pd.Series(dtype="float64"), pd.Series(dtype="float64")
    lr_v, lr_m, lr_i = pd.Series(dtype="float64"), pd.Series(dtype="float64"), pd.Series(dtype="float64")
    parts = defaultdict(list); reasons = defaultdict(int)
    repin_file(DELISTED, "data_delisted_sha256")
    dl = pd.read_parquet(DELISTED, columns=["ts_code", "last_trade_date", "delist_date"])
    cut = pd.to_datetime(dl.delist_date); cut.index = dl.ts_code; cut = cut[~cut.index.duplicated()]   # PRIMARY: delist_date, no fallback
    cut_dd = pd.to_datetime(dl.last_trade_date); cut_dd.index = dl.ts_code; cut_dd = cut_dd[~cut_dd.index.duplicated()]   # SHADOW: last_trade_date (disclosure only)
    no_delist_date = sorted(cut.index[cut.isna()])
    sp_nc = pd.Series(dtype="float64"); dl_cut = defaultdict(int); dl_cut_sh = defaultdict(int); n_bj = 0
    sp_dd, mp_dd = pd.Series(dtype="float64"), pd.Series(dtype="float64")
    for y in PANEL_YEARS:
        if pd.Timestamp(f"{y}-01-01") > idx[-1]: break
        pr = pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=["date", "instrument", col, "logmv", "ind", "row_origin"]); pr["date"] = pd.to_datetime(pr.date)
        pr["_rs"] = pr.row_origin.eq("restored").astype("float64"); pr = pr.drop(columns=["row_origin"])   # Arch 561219c7: restored flag only
        mk = pd.read_parquet(MASK, columns=["date", "instrument", "suspended", "st", "young", "adv_fail"],
                             filters=[("date", ">=", pd.Timestamp(f"{y}-01-01").to_pydatetime()), ("date", "<=", pd.Timestamp(f"{y}-12-31").to_pydatetime())])
        mk["date"] = pd.to_datetime(mk.date)
        n_bj += int((pr.instrument.astype(str).str.endswith(".BJ") & pr[col].fillna(False).astype(bool)).sum())   # Arch P3-D
        days = pd.DatetimeIndex(sorted(pr.date.unique())); days = days[days <= idx[-1]]
        names = pd.Index(sorted(set(pr.instrument) | set(mk.instrument) | set(sp.index)))
        pv = lambda df, v, agg="max": df.pivot_table(index="date", columns="instrument", values=v, aggfunc=agg).reindex(index=days, columns=names)
        has = pv(pr.assign(_h=1.0), "_h").notna()
        val = pv(pr.assign(_v=pr[col].fillna(False).astype("float64")), "_v")
        lmv = pv(pr, "logmv", "mean")
        sus = pv(mk.assign(_s=mk.suspended.astype("float64")), "_s")          # NaN = no mask row
        rst = pv(pr, "_rs").fillna(0.0) == 1.0                                 # restored panel row (Arch 561219c7)
        bad_rs = (has & ((sus == 1.0) != rst)) | (has & sus.isna())            # hard assert: suspended <=> restored; panel row without mask row
        if bool(bad_rs.to_numpy().any()):
            st_b = bad_rs.stack(); st_b = st_b[st_b]
            raise SystemExit(f"STOP (B3 assert, Arch 561219c7): {int(len(st_b))} panel rows in {y} where mask suspended != (row_origin == restored) or no mask row "
                             f"(e.g. {[(str(d_.date()), i_) for d_, i_ in st_b.index[:5]]}) — report to Arch")
        del bad_rs
        pre = pr[pr.date < lo].sort_values("date").groupby("instrument").tail(1).set_index("instrument")   # r2.2 seed / N4 ind seed (r2.10 (c): taken here, then pr freed)
        del pr
        gone = pd.DataFrame(days.values[:, None] > cut.reindex(names).values[None, :], index=days, columns=names)   # NaT → False
        carry_nc = (sus == 1.0) & (~has | rst); carry = carry_nc & ~gone        # every mask-suspended day carries (restored rows too); no carry after delist_date
        del rst
        A_nc = val.where(has, 0.0).mask(carry_nc)                              # r2.3 rule (no delisting cut) — only to count the cut
        gone_dd = pd.DataFrame(days.values[:, None] > cut_dd.reindex(names).values[None, :], index=days, columns=names)
        carry_dd = carry_nc & ~gone_dd                                          # shadow: cut at last_trade_date (disclosure only)
        A_dd = val.where(has, 0.0).mask(carry_dd); B_dd = lmv.where(has & lmv.notna(), -np.inf).mask(carry_dd)
        A = val.where(has, 0.0).mask(carry)                                    # anchors: panel col / False (break) / NaN (carry)
        B = lmv.where(has & lmv.notna(), -np.inf).mask(carry)                  # mcap anchors: -inf = break
        p0 = pd.Timestamp("1970-01-01")
        S = pd.concat([pd.DataFrame([sp.reindex(names).fillna(0.0).to_numpy()], index=[p0], columns=names), A]).ffill().iloc[1:].fillna(0.0)
        MV = pd.concat([pd.DataFrame([mp_.reindex(names).fillna(-np.inf).to_numpy()], index=[p0], columns=names), B]).ffill().iloc[1:]
        S_nc = pd.concat([pd.DataFrame([sp_nc.reindex(names).fillna(0.0).to_numpy()], index=[p0], columns=names), A_nc]).ffill().iloc[1:].fillna(0.0)
        S_dd = pd.concat([pd.DataFrame([sp_dd.reindex(names).fillna(0.0).to_numpy()], index=[p0], columns=names), A_dd]).ffill().iloc[1:].fillna(0.0)
        MV_dd = pd.concat([pd.DataFrame([mp_dd.reindex(names).fillna(-np.inf).to_numpy()], index=[p0], columns=names), B_dd]).ffill().iloc[1:]
        del A, B   # sus kept for the carried-reason count
        sp, mp_, sp_nc = S.iloc[-1], MV.iloc[-1].fillna(-np.inf), S_nc.iloc[-1]
        sp_dd, mp_dd = S_dd.iloc[-1], MV_dd.iloc[-1].fillna(-np.inf); MV_dd = MV_dd.replace(-np.inf, np.nan)
        cx = (S_nc.astype(bool) & ~S.astype(bool) & gone & ~has); cx = cx.loc[(cx.index >= s) & (cx.index <= e)].sum()
        for k_, v_ in cx[cx > 0].items(): dl_cut[k_] += int(v_)
        cy = (S_nc.astype(bool) & ~S_dd.astype(bool) & gone_dd & ~has); cy = cy.loc[(cy.index >= s) & (cy.index <= e)].sum()   # Alpha P3-1: shadow cut
        for k_, v_ in cy[cy > 0].items(): dl_cut_sh[k_] += int(v_)
        del S_nc, A_nc, carry_nc, gone, gone_dd, carry_dd, A_dd, B_dd
        MV = MV.replace(-np.inf, np.nan)
        if len(pre): lr_v = pre[col].fillna(False).astype("float64").combine_first(lr_v); lr_m = pre.logmv.combine_first(lr_m); lr_i = pre.ind.astype("float64").combine_first(lr_i)
        w = (days >= lo)
        if w.any():
            cw = (S.astype(bool) & (sus == 1.0)).loc[w]                         # carried name-days: S & mask-suspended (restored rows included)
            st_ = cw.loc[(cw.index >= s) & (cw.index <= e)].stack(); st_ = st_[st_].reset_index().iloc[:, :2]; st_.columns = ["date", "instrument"]
            if len(st_):
                r = st_.merge(mk, on=["date", "instrument"], how="left")
                reasons["carried_name_days_x2"] += len(r); reasons["suspended"] += int(r.suspended.fillna(False).astype(bool).sum())
                reasons["not_suspended"] += int((~r.suspended.fillna(False).astype(bool)).sum())
                for c_ in ("st", "young", "adv_fail"): reasons[c_] += int(r[c_].fillna(False).astype(bool).sum())
            for k_, f_ in (("S", S), ("MV", MV), ("VAL", val.where(has)), ("LMV", lmv.where(has)), ("S_dd", S_dd), ("MV_dd", MV_dd)): parts[k_].append(f_.loc[w])
        del mk, has, val, lmv, carry, S, MV, S_dd, MV_dd, pre, w, sus; trim(); peak_check(f"pool_benchmarks {carry_col} year {y}")   # r2.10 (c)/(d)

    def cat(k):   # r2.10 (c): pop each key's parts as it is concatenated (no second copy of the per-year frames)
        return pd.concat(parts.pop(k)).reindex(index=idx)
    S, MV, VAL, LMV = cat("S"), cat("MV"), cat("VAL"), cat("LMV"); U = S.columns
    S = S.fillna(0.0).astype(bool); MV = MV.reindex(columns=U); VAL = VAL.reindex(columns=U); LMV = LMV.reindex(columns=U)
    S_dd = cat("S_dd").reindex(columns=U).fillna(0.0).astype(bool); MV_dd = cat("MV_dd").reindex(columns=U)   # r2.10: parts is empty after the pops (no del: cat closes over it)
    # Arch b09901f5 P2-1 (kept; cut = delist_date now): the delisting cut must hold on EVERY X2 day — no S=True after cut
    # for names with cut <= window end (gone rebuilt on the X2 frame, independent of the recursion)
    xd = (idx >= pd.Timestamp(s)) & (idx <= pd.Timestamp(e))
    # missing delist_date: never fall back to last_trade_date; a name present in X2 (member or panel row) → stop, otherwise disclose
    nd_x2 = [n_ for n_ in no_delist_date if n_ in U and (bool(S.loc[xd, n_].any()) or bool(VAL.loc[xd, n_].notna().any()))]
    if nd_x2: raise SystemExit(f"STOP (主 Agent 02:44 item 1): delisted names without delist_date present in X2 {nd_x2[:10]} — report to Arch")
    gone_full = pd.DataFrame(idx.values[:, None] > cut.reindex(U).values[None, :], index=idx, columns=U).loc[xd]   # NaT → False
    cut_fail = (S.loc[xd] & gone_full)
    if bool(cut_fail.to_numpy().any()):
        cf = cut_fail.sum(); cf = cf[cf > 0]
        raise SystemExit(f"STOP (Arch b09901f5 P2-1): delisting cut failed — S=True after cut on {int(cf.sum())} X2 name-days "
                         f"({dict(list(cf.astype(int).items())[:10])}) — report to Arch")
    del gone_full, cut_fail
    end_d = S.loc[:e].index[-1]; end_carry = S.loc[end_d] & VAL.loc[end_d].isna()
    end_carry_names = sorted(U[end_carry.to_numpy()])
    end_after = {n_: str(cut[n_].date()) for n_ in end_carry_names if n_ in cut.index and pd.notna(cut[n_]) and cut[n_] > pd.Timestamp(e)}   # legit, disclosed
    Mp = S.shift(1, fill_value=False); wv = (np.exp(MV).where(S).shift(1)*Mp).fillna(0.0)
    Mp_dd = S_dd.shift(1, fill_value=False); wv_dd = (np.exp(MV_dd).where(S_dd).shift(1)*Mp_dd).fillna(0.0); del S_dd, MV_dd   # shadow (last_trade_date), disclosure only
    Mpo = VAL.fillna(0.0).astype(bool).shift(1, fill_value=False); wvo = (np.exp(LMV).shift(1)*Mpo).fillna(0.0)          # old: no carry
    V2, L2 = VAL.copy(), LMV.copy(); nr = V2.iloc[0].isna()                                                                 # r2.2: no row = carry
    V2.iloc[0] = V2.iloc[0].where(~nr, lr_v.reindex(U)); L2.iloc[0] = L2.iloc[0].where(~nr, lr_m.reindex(U))
    last = pd.Series({c: VAL[c].last_valid_index() for c in U}).reindex(U).fillna(pd.Timestamp("1970-01-01"))
    after = idx.values[:, None] > pd.DatetimeIndex(last.values).values[None, :]
    M2 = V2.ffill().mask(after).fillna(0.0).astype(bool); Mp2 = M2.shift(1, fill_value=False); wv2 = (np.exp(L2.ffill().mask(after)).where(M2).shift(1)*Mp2).fillna(0.0)
    del V2, L2, M2, MV, VAL, LMV, S, last, after; trim()   # r2.10 (c)
    rs = pd.concat([pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=["date", "instrument", carry_col, "row_origin", "restore_reason"],
                                    filters=[("row_origin", "==", "restored"), ("restore_reason", "==", "resume")]) for y in PANEL_YEARS])
    rs["date"] = pd.to_datetime(rs.date); rs = rs[(rs.date > idx[0]) & (rs.date <= idx[-1])]   # idx[0] has no T−1 inside the frame
    ri, ci = idx.get_indexer(rs.date), U.get_indexer(rs.instrument); okk = (ri >= 0) & (ci >= 0)
    mpv = np.zeros(len(rs), bool); mpv[okk] = Mp.to_numpy()[ri[okk], ci[okk]]
    bad = (mpv != rs[carry_col].fillna(False).astype(bool).to_numpy()) | ~okk
    diag = dict(carry_col=carry_col, rule="Arch 561219c7: carry on every mask-suspended day (no row or restored row), recursed from 2018; mask suspended <=> restored asserted",
                resume_rows_checked=int(len(rs)), carry_mismatch=int(bad.sum()), carry_unindexed=int((~okk).sum()),
                mismatch_examples=rs[bad].head(10).astype(str).to_dict("records"), carried_by_mask_reason_x2=dict(reasons),
                not_suspended_note="P3-A: carried name-days are counted on (S & mask suspended), so not_suspended is always 0 (self-consistency only); "
                                   "independent checks are Mp != carry_col and P2-B",
                delisted_cut_name_days_x2=dict(sorted(dl_cut.items())), delisted_cut_total_x2=int(sum(dl_cut.values())), delisted_cut_names_x2=len(dl_cut),
                delisted_cut_name_days_x2_shadow_last_trade_date=dict(sorted(dl_cut_sh.items())),
                delisted_cut_total_x2_shadow_last_trade_date=int(sum(dl_cut_sh.values())), delisted_cut_names_x2_shadow_last_trade_date=len(dl_cut_sh),
                delisted_cut_rule="主 Agent 02:44 / Arch spec: PRIMARY S=False and MV chain broken for d > delist_date (no fallback); "
                                  "last_trade_date < d <= delist_date carried as suspended (return 0, in denominator)",
                delisted_missing_delist_date_outside_x2=no_delist_date, shadow_cut="last_trade_date (disclosure only, not decision, not family count)",
                delisted_master_max_delist_date=str(cut.max().date()),
                carried_to_window_end=end_carry_names, carried_to_window_end_delisted_after_window=end_after,
                cut_failure_check="Arch b09901f5 P2-1: (S & gone).any() over all X2 days must be False (explicit raise above)",
                delisted_master_sha256=AUTH_TOOLS.get("data_delisted_sha256"), delisted_master_max_last_trade_date=str(pd.to_datetime(dl.last_trade_date).max().date()),
                bj_member_rows=n_bj)
    # shadow (last_trade_date cut) vs primary (delist_date cut): EW / wb annualized, disclosure only — computed here so that evaluate() never
    # touches delisting fields (Arch disclosure scan: delisting tokens only inside pool_benchmarks)
    RR = rr.reindex(columns=U).fillna(0.0)   # the only idx × U return frame; returned as r0 for evaluate()
    _ann = lambda r: float((1+r).prod()**(244/len(r))-1)
    _ewf = lambda M, W_: (((RR*M).sum(1)/M.sum(1)).loc[s:e], ((RR*W_).sum(1)/W_.sum(1)).loc[s:e])
    ew_p, wb_p = _ewf(Mp, wv); ew_sh, wb_sh = _ewf(Mp_dd, wv_dd); del Mp_dd, wv_dd
    diag.update(poolEW_cagr244_primary_cut_delist_date=_ann(ew_p), wb_cagr244_primary_cut_delist_date=_ann(wb_p),
                poolEW_cagr244_shadow_cut_last_trade_date=_ann(ew_sh), wb_cagr244_shadow_cut_last_trade_date=_ann(wb_sh),
                poolEW_cagr244_diff_primary_minus_shadow=_ann(ew_p) - _ann(ew_sh), wb_cagr244_diff_primary_minus_shadow=_ann(wb_p) - _ann(wb_sh),
                shadow_note="shadow = last_trade_date cut: disclosure only, not decision, not family count")
    return dict(Mp=Mp, wv=wv, Mpo=Mpo, wvo=wvo, Mp2=Mp2, wv2=wv2, U=U, r0=RR, seed_ind=lr_i.reindex(U), diag=diag)


def limit_up(inst, ret):
    """approximate limit-up flag from close return (Arch P2-5): SZ codes starting 30 (ChiNext 300/301/302…) and SH 688/689 (STAR) → 20%,
    else 10% (ST excluded by the universe; .BJ → stop, Arch P3-D)."""
    c = pd.Series(inst).astype(str)
    if c.str.endswith(".BJ").any(): raise SystemExit("STOP (Arch P3-D): .BJ name in limit_up input (BSE limit is 30%) — report to Arch")
    twenty = (c.str[:2].eq("30") & c.str.endswith(".SZ")) | (c.str[:3].isin(["688", "689"]) & c.str.endswith(".SH"))
    lim = np.where(twenty.to_numpy(), 0.20, 0.10)
    return ret >= lim - LIMIT_EPS


L23_ROOT = AIF/"leaf23_sue_desens_cs"; L23_SENS = ("sig-sue", "denom-daily", "nofc", "bo40")


def verify_leaf23_complete(auth):
    """Arch P2-2: leaf 24's first stage requires leaf 23 primary + its 4 sensitivities: eval_meta present, chain intact, same panel manifest,
    all five from one leaf-23 script sha and one leaf-23 .ok sha. Returns their shas for the upstream record."""
    up, ids = {}, set()
    for v in ("primary",) + L23_SENS:
        mf = (L23_ROOT if v == "primary" else L23_ROOT.with_name(L23_ROOT.name + "_" + v))/"eval_meta.json"
        m = check_meta(mf, dict(stage="eval", variant=v, cs_panel_manifest_sha256=auth["cs_panel"]["manifest_sha256"]))
        ids.add((m.get("script_sha256"), m.get("arch_ok_sha256"))); up[str(mf.relative_to(AIF))] = sha(mf)
    if len(ids) != 1: raise SystemExit(f"refused: leaf 23 eval metas come from different script/.ok {sorted(ids)}")
    return up


def imax_window(E, LU, win, k, min_valid, block=800):
    """E, LU: (T, N) arrays (NaN = not in mask). Returns IMAX (T, N) and limit-up share among the top-k days; column blocks for RSS."""
    T, N = E.shape; out = np.full((T, N), np.nan, np.float32); lus = np.full((T, N), np.nan, np.float32)
    if T < win: return out, lus
    for c0 in range(0, N, block):
        e = E[:, c0:c0+block].astype(np.float32); l = LU[:, c0:c0+block].astype(np.float32)
        we = sliding_window_view(e, win, axis=0); wl = sliding_window_view(l, win, axis=0)   # (T−win+1, n, win)
        valid = np.isfinite(we).sum(-1); idx = np.argsort(np.where(np.isfinite(we), we, -np.inf), axis=-1)[..., -k:]
        top = np.take_along_axis(we, idx, -1); lt = np.take_along_axis(wl, idx, -1)
        m = valid >= min_valid
        out[win-1:, c0:c0+block] = np.where(m, np.nanmean(top, -1), np.nan); lus[win-1:, c0:c0+block] = np.where(m, np.nanmean(lt, -1), np.nan)
        del we, wl, idx, top, lt
    return out, lus


def style_feats(RW, LM, AD, bench):
    """主 Agent 02:23 ruling (via Alpha preread 8586ffd0 §4): Alpha's frozen style set, every exposure as of t−1 —
    log float mcap (logmv_{t−1}), beta120 vs 510300 (120-session window, ≥60, same construction as the signal side of research/alpha_hiliq_s8_paradigm_v1_1.py, 455fdf82… — text reference only, not imported, no .ok key),
    momentum t−120→t−20 (cumulative return over sessions t−120..t−21, ≥80 valid), logADV20 = log(adv20_yuan at t), NOT shifted: the panel's
    adv20_yuan is copied from the HI_LIQ mask (research/ai_cs_panel_build.py L18/35), whose writer research/strategy_hiliq_universe_v1.py
    L130–141 builds it at session t as the mean amount of the 20 sessions strictly before t (prior = sess[sess < S][-ADV_WIN:]), i.e. already t−20..t−1 (Alpha 77441f16 §3; the r2.3 extra shift is removed).
    SW L1 dummies are added in the regression. nv120 = valid return days in t−120..t−1 (Arch P3-C disclosure only, not a regressor)."""
    R64 = RW.astype("float64"); b = bench.reindex(RW.index).astype("float64")
    beta = R64.rolling(120, min_periods=60).cov(b).div(b.rolling(120, min_periods=60).var(), axis=0)
    mom = np.expm1(np.log1p(R64).shift(21).rolling(100, min_periods=80).sum())
    return {"lmv1": LM.shift(1), "beta120": beta.shift(1).astype("float32"), "mom_120_20": mom.astype("float32"),
            "ladv1": np.log(AD.clip(lower=1e4)).astype("float32"),   # adv20_yuan at t = mean t−20..t−1 (mask writer strategy_hiliq_universe_v1.py L130–141)
            "nv120": R64.notna().astype("float32").rolling(120, min_periods=1).sum().shift(1).astype("float32")}


def bench_ret():
    e = pd.read_parquet(ETF, columns=["ts_code", "trade_date", "close_hfq"], filters=[("ts_code", "==", "510300.SH")])
    return pd.Series(e.close_hfq.to_numpy(float), index=pd.to_datetime(e.trade_date.astype(str), format="%Y%m%d")).sort_index().pct_change()


# ---------------------------------------------------------------- stage build (year chunks)
def build(a, panel, out, auth, up):
    panel_recheck(auth, panel); repin(auth, "dep_fe_sha256", f"dep_l18_{a.uni.lower()}_sha256", f"dep_l18v_{a.uni.lower()}_sha256", "data_etf_daily_adj_sha256")
    import research.g1g5_fund_resid_alpha as FE
    uni = a.uni; col = FE.UCOL[uni]
    FIN = load_fin(panel)   # N8: panel dir only (no v1 fallback); asserts len(FIN) == 2
    written, on_missing, gap_share = [], {}, {}
    lo_x2 = pd.Timestamp(X2S).to_pydatetime()

    def a18_year(path, nm, y):   # r9 (b): leaf18/18v α for build year y only (P holds year-y rows only at the merge; same rows matched)
        f_ = [("date", ">=", max(lo_x2, pd.Timestamp(f"{y}-01-01").to_pydatetime())), ("date", "<", pd.Timestamp(f"{y+1}-01-01").to_pydatetime())]
        x = pd.read_parquet(path, columns=["date", "instrument", "alpha"], filters=f_).rename(columns={"alpha": nm}); x["date"] = pd.to_datetime(x.date)
        return x
    BR = bench_ret(); trim(); tail = defaultdict(lambda: deque(maxlen=3)); cov = []; min_valid = 15 if a.win == 20 else 45
    for y in YEARS:
        lo = pd.Timestamp("2023-06-01") if y == 2024 else pd.Timestamp(f"{y-1}-05-01")   # ≥ 121 sessions (mom t−120→t−20, beta120) and ≥ win
        P = pd.concat([read_panel(panel, yy, ["date", "instrument", "ret", "ret_on", "logmv", "ind", "adv20_yuan", col], lo) for yy in sorted({lo.year, y})])
        P = P[~P.instrument.isin(FE.EXCL)]
        RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index().astype("float32")
        LM = P.pivot_table(index="date", columns="instrument", values="logmv").reindex_like(RW).astype("float32")
        AD = P.pivot_table(index="date", columns="instrument", values="adv20_yuan").reindex_like(RW).astype("float32")
        feats = style_feats(RW, LM, AD, BR); del LM, AD   # Alpha frozen style set, all t−1
        feats["vol20"] = RW.astype("float64").shift(1).rolling(20, min_periods=15).std().astype("float32")   # 主 Agent ~02:33: keep vol20_{t−1} (prereg §4 L50)
        # daily idiosyncratic intraday (or total) return, in-mask rows only (resume rows have mask False → never in the signal)
        Q = P[P[col].fillna(False).astype(bool) & (P.ind >= 0)].join(feats["lmv1"].stack().rename("lmv1"), on=["date", "instrument"]).dropna(subset=["ret", "lmv1"])
        Q["r"] = (1 + Q.ret)/(1 + Q.ret_on) - 1 if a.src == "intra" else Q.ret   # N7: ret_on missing → r_id NaN (no fillna(0))
        on_missing[str(y)] = int(Q.ret_on.isna().sum()) if a.src == "intra" else 0; Q = Q.dropna(subset=["r"])
        Q["lu"] = limit_up(Q.instrument, Q.ret.to_numpy()).astype("float32")
        gstart = pd.Timestamp(X2S) - pd.Timedelta(days=10) if y == 2024 else pd.Timestamp(f"{y}-01-01")
        P = P[(P.date >= gstart) & (P.date.dt.year == y) & (P.date <= X2E) & P[col].fillna(False).astype(bool) & (P.ind >= 0)].copy(); trim()   # r10 P2-1: year filter right after Q, full P dropped (rebound)
        ER = []
        for d, g in Q.groupby("date", sort=True):
            if len(g) < 100: continue
            ind = g.ind.to_numpy(); D = (ind[:, None] == np.unique(ind)[None, :]).astype(float); z = g.lmv1.to_numpy(float); z = (z - z.mean())/z.std()
            ER.append(pd.DataFrame({"date": d, "instrument": g.instrument.to_numpy(), "e": FE.ols_resid(g.r.to_numpy(float).clip(-.3, .3), np.column_stack([D, z])).astype("float32"), "lu": g.lu.to_numpy()}))
        del Q; trim()   # r9 (c): Q not read after the e_id loop
        ER = pd.concat(ER); Ee = ER.pivot_table(index="date", columns="instrument", values="e").reindex(index=RW.index, columns=RW.columns)
        Lu = ER.pivot_table(index="date", columns="instrument", values="lu").reindex(index=RW.index, columns=RW.columns)
        del ER; trim()   # r9 (c)
        IM, LS = imax_window(Ee.to_numpy(), Lu.to_numpy(), a.win, a.k, min_valid); del Ee, Lu   # r9 (c): residual pivots freed right after use
        IMX = pd.DataFrame(IM, index=RW.index, columns=RW.columns); LSX = pd.DataFrame(LS, index=RW.index, columns=RW.columns)
        del IM, LS, RW; trim(); peak_check(f"build {uni} year {y} imax")   # r9 (c)/(d)
        if a.ex_fin: P = P[~P.ind.isin(FIN)]
        for nm, M in list(feats.items()) + [("imax", IMX), ("lu_share", LSX)]: P = P.join(M.stack().rename(nm).astype("float32"), on=["date", "instrument"])
        del feats, IMX, LSX; gc.collect()
        P = P.dropna(subset=["lmv1", "beta120", "mom_120_20", "ladv1", "vol20", "ret"]).sort_values("date")
        gap_share[str(y)] = float((P.loc[P.date >= X2S, "nv120"] < 100).mean()) if (P.date >= X2S).any() else None   # Arch P3-C
        A18, A18v = a18_year(L18[uni], "a18", y), a18_year(L18V[uni], "a18v", y)   # r9 (b)
        P = P.merge(A18, on=["date", "instrument"], how="left").merge(A18v, on=["date", "instrument"], how="left"); P[["a18", "a18v"]] = P[["a18", "a18v"]].fillna(0.0)
        del A18, A18v; trim()   # r9 (c)
        AL, GL = [], []
        for d, g in P.groupby("date", sort=True):
            if len(g) < 100: continue
            ind = g.ind.to_numpy(); D = (ind[:, None] == np.unique(ind)[None, :]).astype(float)
            S = g[["lmv1", "beta120", "mom_120_20", "ladv1", "vol20"]].to_numpy(float); S = (S - S.mean(0))/S.std(0)
            eps = FE.ols_resid(g.ret.to_numpy(float).clip(-.21, .31), np.column_stack([D, S[:, :1]])); qd = np.quantile(eps, .05)
            ins = g.instrument.to_numpy()
            for i_, e_ in zip(ins, eps): tail[i_].append(e_ < qd)
            if d < pd.Timestamp(X2S): continue  # warm-up only; nothing before X2 is written
            GL.append(pd.DataFrame({"date": d, "instrument": ins, "gate": np.array([0 if any(tail[i_]) else 1 for i_ in ins], dtype="int8")}))
            sv = -g.imax.to_numpy(float); ok = np.isfinite(sv)
            if ok.sum() < 50: cov.append((d, int(ok.sum()))); continue
            raw = rank_ind(sv, ind)[ok]
            X = np.column_stack([D, S, g.a18.to_numpy(float) - g.a18.mean(), g.a18v.to_numpy(float) - g.a18v.mean()])
            r1 = FE.ols_resid(raw, X[ok]); mv = g.lmv1.to_numpy(float)[ok]
            al, dom = FE.dom_rank(r1, mv); al = FE.ols_resid(al, np.column_stack([D[ok], S[ok][:, :1]])); al, _ = FE.dom_rank(al, mv)
            AL.append(pd.DataFrame({"date": d, "instrument": ins[ok], "alpha": al.astype("float32"), "size_domain": dom.astype("int8"), "ind": ind[ok],
                                    "raw": raw.astype("float32"), "lu_share": g.lu_share.to_numpy()[ok], "fin": np.isin(ind[ok], list(FIN))}))
            cov.append((d, int(ok.sum())))
        if AL: xparquet(pd.concat(AL), out/f"alpha_{uni}_{y}.parquet"); written.append(f"alpha_{uni}_{y}.parquet")
        if GL: xparquet(pd.concat(GL), out/f"gate_{uni}_{y}.parquet"); written.append(f"gate_{uni}_{y}.parquet")
        print(uni, y, "built", f"rss={rss():.0f}", flush=True); del P, AL, GL; trim(); peak_check(f"build {uni} year {y}")   # r8; r9 (c) trim at year end
    xparquet(pd.DataFrame(cov, columns=["date", "n"]), out/f"coverage_{uni}.parquet"); written.append(f"coverage_{uni}.parquet")
    write_meta(out, f"build_{uni}", auth, written, up, p3c_nv120_lt100_share_x2=gap_share, uni=uni, ret_on_missing_rows_in_mask=on_missing)


# ---------------------------------------------------------------- stage eval (X2 only)
def pick_book(A, G, rd, days, N, w, ind_cap, blocked):
    """Re-pick N names from the gate=1 list by α at rebalance days; w each; industry ≤ ind_cap; rest 510300 (P1-3).
    blocked[d] = names with is_resume_day on d: not newly bought that day (entry gate only; P0-1)."""
    from research.g1g5_fund_resid_alpha import BAL
    Ag = A.merge(G, on=["date", "instrument"], how="left"); Ag["gate"] = Ag.gate.fillna(1)
    byd = {d: g for d, g in Ag[Ag.gate == 1].groupby("date")}; held, rows, cur, skips = set(), [], None, 0
    for d in days:
        if d in byd and d in rd:
            g = byd[d].sort_values("alpha", ascending=False); pk, iw = [], {}
            for i, ind in zip(g.instrument, g.ind):
                if len(pk) >= N: break
                if i in blocked.get(d, ()) and i not in held: skips += 1; continue
                if iw.get(ind, 0) + w > ind_cap + 1e-12: continue
                pk.append(i); iw[ind] = iw.get(ind, 0) + w
            if max(iw.values(), default=0) > ind_cap + 1e-12 or len(pk) > N: raise RuntimeError(f"pick_book: industry cap / N breached on {d}")
            cur = [(i, w) for i in pk] + [(BAL, 1 - w*len(pk))]; held = set(pk)
        if cur is not None: rows += [(d, i, x) for i, x in cur]
    W = pd.DataFrame(rows, columns=["date", "instrument", "target_weight"])
    if not (W[W.instrument != BAL].target_weight <= w + 1e-12).all(): raise RuntimeError("pick_book: single-name weight above cap")
    W.attrs["blocked_skips"] = skips
    return W


def evaluate(a, panel, out, auth, up):
    """r9 (a) = leaf 23 r2.10 (a): one universe per process (a.uni); writes summary_<uni>_<stamp>.json + eval_<uni>_meta.json; --stage merge combines."""
    panel_recheck(auth, panel); repin(auth, "dep_fe_sha256", "data_etf_daily_adj_sha256")
    import research.g1g5_fund_resid_alpha as FE
    ext_out = {}; trim()
    FE.PC = panel; FE._RET.clear()
    FE.rets(range(2024, 2027)); trim()   # r9 (c) = r2.10 (c): FE return cache loaded once at the lowest-memory point and kept for every book_ret (same key (2024, 2025, 2026), same data)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); s, e = X2S, X2E; ann = lambda r: float((1+r).prod()**(244/len(r))-1)
    summ = dict(leaf="imax_intraday", leaf_no=24, stamp=stamp, live=False, promotion_approved=False, research_only=True, short_arm=False,
                sealed_read=False, auth=auth, res={}, engine="FE.book_ret wb_SD0 (SD0) on cs_panel_v2_resumefix",
                note_zh="研究叶，非生产；长仓，无空头腿。X2 只是入场券；唯一晋级测试为 2026-11-02 起 FWD。Gate B/GATE_V3/衰减/ρ/Jaccard(叶15–23) 由钉 sha 的评价工具另算。",
                notes_arch_b997cba8_zh=[
                    "外部工具口径：leaf_selfcheck_v3.py 的 PANEL 仍写死读 v1 panel_cache（池成员与 IC 价格指数）；alpha_combo_marginal_v1_1 / leaf_selfcheck_common 的书收益来自原始复权价，不是 FE.book_ret。Gate B/GATE_V3/衰减/IC 与本脚本判定读数不是同一引擎、同一面板，与叶15–22 相同，可横向比较；以后另提 --panel-dir（新 sha、单独审）。",
                    "beta120 与动量 t−120→t−20 用面板全部行的 ret（t−1，PIT），重建后含复牌补回行收益，与 v1 面板下的叶15–22 不完全可比（规模需授权运行后才能报）。",
                    "补回行 hiliq=False：复牌日的已持仓股不在 α 名单里会被调出，blocked 入场闸门基本不触发（books.*.blocked_skips 计数）；SD0 下属乐观处理。",
                    "N7：ret_on 缺失时 r_id 记 NaN、不进 e_id（缺失行数见 build_*_meta.json）。N3：叶18/18v 判重 Jaccard 按其自身 α 排序取前 N。",
                    "B3（Arch 129d67c5 §3 执行口径）：只在面板无行且 mask 当日停牌时沿用上一状态和停牌前流通市值；ST/成交额不足/次新无行日记 False 并中断沿用；mask 无行（未上市/退市）记 False；自 2018 逐年递推。沿用名·日按 mask 原因计数（必须全为停牌）；旧写法与 r2.2 写法的 EW/wb 年化差只作披露，见 res.*.b3_pool_carry。",
                    "行业帽 25% 的出处是 Arch 审核 0d9bd147 第 96 行（P1-3，叶23 经主 Agent 01:52 认可）；预注册 §0 第 5 行把它归在 01:42 裁定下，但 01:42 原文没有这一项（Arch P3-4，不重新冻结）。",
                    "残差化（主 Agent 02:23 裁定，经 Alpha 预读 8586ffd0；vol20 按主 Agent 约 02:33 ET 裁定保留）：风格集 = Alpha 冻结集（SW L1、logmv_{t−1}、beta120_{t−1}（对 510300）、动量 t−120→t−20（t−1 时点）、logADV20）+ vol20_{t−1}（预注册 c289e770 §4 第 50 行：本叶要的是「波动之外的右尾」，Alpha 77441f16 §6 建议取超集）；替代预注册 §4 的 mom20/mom60 与当日 logADV20（预注册未改，按裁定执行并披露）；叶18/18v α 照旧。","e_id 只对 SW L1 + logmv_{t−1} 回归（Arch bd3abe5c §3.3 裁定）：e_id 是信号构造（预注册 c289e770 §3），不属于 02:23 去敏残差化范围；若把 beta/mom/ADV 放进 e_id 就是另一个因子，需重新冻结、家族次数 +1。",
                    "logADV20 口径（Alpha 77441f16 §3）：面板 adv20_yuan 由 research/ai_cs_panel_build.py 第 18/35 行直接拷贝 HI_LIQ mask；mask 的实际写入方 research/strategy_hiliq_universe_v1.py 第 130–141 行（Arch b09901f5 P3-1）在 t 日取 prior = sess[sess < S][-ADV_WIN:]，adv = 这 20 个交易日成交额均值，即 t 日值已是 t−20..t−1 均值、不含 t 日；所以 ladv1 直接取 t 日 adv20_yuan、不再 shift（r2.3 多滞后一天，已更正），与 Alpha 冻结 s8 一致。",
                    "风格 t−1 与 Alpha 冻结代码的差别（Arch P3-B）：beta120、动量按裁定原文「全部 t−1」与 Alpha s8 v1.1（research/alpha_hiliq_s8_paradigm_v1_1.py，455fdf82…）信号侧一致：beta 用收益 d−120..d−1，动量 C(d−21)/C(d−121)−1，liq = adv20[d]；旧 s8 af48bc05 以 t 为锚、差一日，只作历史对照。叶子不 import s8，无 s8 键。",
                    "CMC v1.1（Alpha 交接 ab6d1e82）：§8 / CMC 读数改用 research/alpha_combo_marginal_v1_1.py（r3 5658f612…，.ok 键 dep_combo_sha256，.cmd 必须带 --arch-ok；r3 已过 Arch 审 bbfcb7ef，selftest .ok fa45bf7f 已签，全量 .ok 未签）。旧版 alpha_combo_marginal.py（bee23019…，dep_combo_legacy_sha256）的结果只作对照披露列，不进判定、不计入家族次数。阈值不变。v1.1 首月行业用 2024-05-31 申万快照、START 当日跳过，与旧版的差异由 legacy 列披露。",
                    "面板缺口（Arch P3-C）：面板只有 fulla|hiliq 行和补回行，ST/成交额不足日无行；beta/动量按有效日滚动，缺口日对动量等于记 0 收益，与连续价格口径不同。build_*_meta.json 的 p3c_nv120_lt100_share_x2 报 X2 回归样本中「t−120..t−1 有效日 <100」的名·日占比。",
                    "退市（主 Agent 02:44 裁定，Arch 口径）：mask 是矩形网格，退市后恒为 suspended=True。基准池主口径按退市日截断：退市日之后记 S=False、市值链断开；最后交易日之后到退市日之间按 mask 停牌沿用，收益记 0、留在分母（预注册「停牌记 0、不剔分母」）。缺退市日的名在 X2 内即停跑、窗口外只披露，不回退到最后交易日。影子口径按最后交易日截断，只作披露，不进判定、不计入家族次数；受影响名数与名·日数以运行时 diag 为准（主口径 delisted_cut_name_days_x2 / delisted_cut_names_x2，影子 delisted_cut_name_days_x2_shadow_last_trade_date / delisted_cut_names_x2_shadow_last_trade_date）；静态参考（Alpha 486496a9）：delisted_master 63590f23 中 X2 窗内退市 93 名，其中 76 名最后交易日与退市日相差超过 1 天；两口径的 EW/wb 年化差由 pool_benchmarks 写入 res.*.b3_pool_carry（*_shadow_cut_last_trade_date）。delisted_master 只在 pool_benchmarks 内读取（data_delisted_sha256，读前 repin）。「mask 无行记 False」分支保留作防御。",
                    "B3 校验（Arch P3-A / b09901f5 P2-1）：沿用名·日按构造必然为 mask 停牌，not_suspended 恒为 0，只是自洽检查；独立校验靠 Mp≠carry 停跑和截断断言：X2 每一日 (S & gone) 必须全为 False（cut = 退市日），否则停跑报 Arch；cut 在窗口末之后、窗口末仍停牌被沿用的名属合法，只列入 carried_to_window_end_delisted_after_window（附 cut 日期）。b3 记 delisted_master sha、最大最后交易日与最大退市日（P3-3）。吸收合并持有人实得换股，两口径都按 0 收益，属已知局限。col 成员出现 .BJ 也停跑（P3-D；mask/FULLA 不含北交所，属已知设计边界，由 Data/主 Agent 跟踪）。",
                    ".ok 有效期（Arch P2-A）：expires_et 必填、带时区，authorize 与每个阶段开始（panel_recheck）各核一次，过期即拒。<out_dir>/tool_run_log.txt 由运行者写（Arch §5-1），脚本不生成。",
                    "涨停识别（Arch P2-5）：深市 30 开头（含 302）与沪市 688/689 用 20%，其余 10%。持仓涨停占比另报再平衡日口径 held_limitup_share_in_imax_sample_rebal（Arch P3-3），原全持有日口径保留。",
                    "家族计数：p1_factor_lib 也有低波因子，家族实际次数可能 > 3；|t|≥2.50 已等于 n=4 门槛，结论不受影响。叶18/18v 已读密封窗，不是干净样本外；引擎 SD0。",
                    "文件名 IMAX_OVERNIGHT，但因子是剔除隔夜分量后的日内 IMAX。"])
    for uni in (a.uni,):   # r9 (a): one universe per process (loop body unchanged)
        col = FE.UCOL[uni]
        A = pd.concat([pd.read_parquet(out/f"alpha_{uni}_{y}.parquet", columns=["date", "instrument", "alpha", "ind", "lu_share", "fin"]) for y in YEARS if (out/f"alpha_{uni}_{y}.parquet").exists()])
        G = pd.concat([pd.read_parquet(out/f"gate_{uni}_{y}.parquet") for y in YEARS if (out/f"gate_{uni}_{y}.parquet").exists()])
        for t in (A, G): t["date"] = pd.to_datetime(t.date)
        A, G = A[(A.date >= s) & (A.date <= e)], G[(G.date >= s) & (G.date <= e)]
        days = sorted(A.date.unique()); rd = set(days[::FE.REBAL])
        A_rd, G_rd = A[A.date.isin(rd)], G[G.date.isin(rd)]; trim()   # r9 (b) = r2.10 (b): pick_book only reads rebalance-day rows (byd used only for d in rd)
        lo_px = pd.Timestamp("2024-05-20"); carry_col = "hiliq_carry" if uni == "HILIQ" else "fulla_carry"
        PX = pd.concat([pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=["date", "instrument", "ret", "close", "is_resume_day", carry_col],   # r9 (b): logmv/<col> were never used from PX
                                        filters=[("date", ">=", lo_px.to_pydatetime())]) for y in YEARS])
        PX["date"] = pd.to_datetime(PX.date); PX = PX[PX.date <= e]
        blocked = {d: set(g.instrument) for d, g in PX[PX.is_resume_day.fillna(False).astype(bool)].groupby("date")}
        rr = PX.pivot_table(index="date", columns="instrument", values="ret").sort_index(); trim()
        # B3 (Arch P1-1, 129d67c5 §3): S carried only on mask-suspended no-row days, recursed from 2018; then T−1; ret at T; suspended → 0, kept
        repin(auth, "data_mask_sha256"); pb = pool_benchmarks(panel, PX, col, carry_col, rr, s, e); b3 = pb["diag"]
        if b3["carry_mismatch"] or b3["carried_by_mask_reason_x2"].get("not_suspended", 0) or b3["bj_member_rows"]:
            xtext(out/f"B3_carry_mismatch_{uni}.json", json.dumps(b3, ensure_ascii=False, indent=1, default=str))
            raise SystemExit(f"STOP (B3): Mp != {carry_col} on {b3['carry_mismatch']} restored resume rows / {b3['carried_by_mask_reason_x2'].get('not_suspended', 0)} carried non-suspended name-days / {b3['bj_member_rows']} .BJ member rows (P3-D) — report to Arch")
        Mp, wv = pb["Mp"], pb["wv"]; r0 = pb["r0"]; del rr   # Alpha P3-2: reuse the single return frame; r7 P3-7 dead U removed; P3-8 drop rr now
        ewf = lambda M, W_, _r=r0: (((_r*M).sum(1)/M.sum(1)).loc[s:e], ((_r*W_).sum(1)/W_.sum(1)).loc[s:e])   # r7 P3-7
        ew, wb = ewf(Mp, wv); ew_o, wb_o = ewf(pb["Mpo"], pb["wvo"]); ew_2, wb_2 = ewf(pb["Mp2"], pb["wv2"])
        cmd_x2 = int((Mp & ~pb["Mpo"]).loc[s:e].to_numpy().sum())
        for k_ in ("Mpo", "wvo", "Mp2", "wv2"): del pb[k_]   # r9 (c) = r2.10 (c): disclosure frames dropped once read
        trim()
        b3.update(carried_member_days_x2=cmd_x2,
                  poolEW_cagr244_old_nocarry=ann(ew_o), wb_cagr244_old_nocarry=ann(wb_o), poolEW_cagr244_r2_2_norowcarry=ann(ew_2), wb_cagr244_r2_2_norowcarry=ann(wb_2),
                  poolEW_cagr244_diff_vs_old=ann(ew) - ann(ew_o), wb_cagr244_diff_vs_old=ann(wb) - ann(wb_o),
                  poolEW_cagr244_diff_vs_r2_2=ann(ew) - ann(ew_2), wb_cagr244_diff_vs_r2_2=ann(wb) - ann(wb_2),
                  note="old / r2.2 / shadow constructions: disclosure only (shadow diffs come from pool_benchmarks diag)")
        del Mp, wv, r0, pb; trim()   # r9 (c) = r2.10 (c): freed before the next allocation (was after the return-cache read)
        repin(auth, "data_etf_daily_adj_sha256"); bal = FE.rets(range(2024, 2027))[0][FE.BAL].loc[s:e].astype(float)

        def vs(r, b):
            b = b.reindex(r.index).fillna(0); x = r - b; be = float(np.cov(r, b)[0, 1]/b.var()); res = r - be*b
            return dict(excess_ann244=float(x.mean()*244), t_hac=hac_t(x), t_naive=float(x.mean()/x.std()*np.sqrt(len(x))), beta=be,
                        resid_alpha244=float(res.mean()*244), resid_t_hac=hac_t(res), by_year={str(k): float(v.mean()*244) for k, v in x.groupby(x.index.year)})
        bench = dict(poolEW_cagr244=ann(ew), wb_cagr244=ann(wb), bal_cagr244=ann(bal))
        cap_ind = TIER_IND_CAP if uni == "HILIQ" else FE.IND_CAP[uni]
        specs = {"top6_60w": (6, TIER_W, cap_ind), "top10_100w": (10, TIER_W, cap_ind), "top20_disclosure": (DISC_N, DISC_W, FE.IND_CAP[uni]),
                 "top6_60w_cap20_disclosure": (6, TIER_W, CORE_IND_CAP), "top10_100w_cap20_disclosure": (10, TIER_W, CORE_IND_CAP)}
        books = {}
        for nm, (N, w, icap) in specs.items():
            W = pick_book(A_rd, G_rd, rd, days, N, w, icap, blocked); xparquet(W, out/f"eval_weights_{uni}_{nm}_x2_{stamp}.parquet")   # r9 (b): rebalance-day rows only (identical picks)
            r, to = FE.book_ret(W, s, e); _c = FE.COST; FE.COST = 0.003; r30, _ = FE.book_ret(W, s, e); FE.COST = _c
            nav = (1+r).cumprod()
            H = W[W.instrument != FE.BAL].merge(PX[["date", "instrument", "is_resume_day", carry_col, "close"]], on=["date", "instrument"], how="left") \
                .merge(A[["date", "instrument", "lu_share", "fin"]], on=["date", "instrument"], how="left")
            b = dict(cagr244=ann(r), cagr252=float(nav.iloc[-1]**(252/len(r))-1), mdd=float((nav/nav.cummax()-1).min()), turnover_1s=to,
                     cagr244_30bp=ann(r30), vs_wb=vs(r, wb), vs_poolEW=vs(r, ew), vs_510300=vs(r, bal), held_name_days=int(len(H)),
                     held_resume_rows=int(H.is_resume_day.fillna(False).astype(bool).sum()), held_resume_rows_carry=int(H[carry_col].fillna(False).astype(bool).sum()),
                     held_limitup_share_in_imax_sample=float(H.lu_share.mean()), held_limitup_share_in_imax_sample_rebal=float(H[H.date.isin(rd)].lu_share.mean()), held_financial_share=float(H.fin.fillna(False).astype(bool).mean()),
                     blocked_skips=int(W.attrs.get("blocked_skips", 0)))
            if N < 20:
                cap = TIERS[N]; Hr = H[H.date.isin(rd)].dropna(subset=["close"])
                fill = (np.floor(cap*Hr.target_weight/(Hr.close*100))*100*Hr.close).groupby(Hr.date).sum()/(cap*Hr.groupby("date").target_weight.sum())
                b["lot_fill_ratio_mean"] = float(fill.mean()); b["lot_cash_drag_mean"] = float(1 - fill.mean())
            books[nm] = b   # r9 (c): return cache kept (was FE._RET.clear())
            if uni == "HILIQ" and nm in ("top6_60w", "top10_100w"):
                tag = f"imax_intraday_{nm}" + ("" if is_primary(a) else f"_{variant_tag(a)}")
                xparquet(W, R/f"output/ai_factory/g1g5_{tag}_daily_weights_{stamp}.parquet")
                xtext(R/f"output/ai_factory/g1g5_{tag}_run_meta_{stamp}.json", json.dumps(dict(mechanism_tag="g1g5_ashare_imax_intraday_v1", universe=uni,
                    tier=nm, variant=variant_tag(a), live=False, promotion_approved=False, research_only=True, stamp=stamp, window="x2",
                    script_sha256=auth["script_sha256"], arch_ok_sha256=auth["arch_ok_sha256"]), ensure_ascii=False))
                for f_ in (f"g1g5_{tag}_daily_weights_{stamp}.parquet", f"g1g5_{tag}_run_meta_{stamp}.json"): ext_out[f_] = sha(R/"output/ai_factory"/f_)
        capadv = {}
        repin(auth, "dep_capadv600_tw_sha256", "dep_capadv600_nav_sha256", "dep_capadv1000_tw_sha256", "dep_capadv1000_nav_sha256")
        for N, d_ in CAPADV.items():
            nv = pd.read_csv(d_/"nav.csv", index_col=0, parse_dates=True).nav; rf = nv.pct_change().dropna().loc[s:e]
            tw = pd.read_parquet(d_/"target_weights.parquet").rename(columns={"session": "date", "weight": "target_weight"})
            tw["instrument"] = tw.instrument_id.str.split(".").map(lambda x: f"{x[1]}.{x[0].upper()}"); tw["date"] = pd.to_datetime(tw.date.astype(str).str[:10])
            rc, _ = FE.book_ret(tw[tw.target_weight > 0][["date", "instrument", "target_weight"]], s, e)   # r9 (c): cache kept
            capadv[N] = dict(filed_cagr244=ann(rf), recomputed_cagr244=ann(rc), recomputed_mdd=float(((1+rc).cumprod()/(1+rc).cumprod().cummax()-1).min()))
        qres = {}
        for k in (5, 10):
            gx = {}
            for q in range(k):
                rows = []
                for d in sorted(rd):
                    x = A[A.date == d]
                    if len(x) < k*5: continue
                    lab = pd.qcut(x.alpha.rank(method="first"), k, labels=False).to_numpy(); sel = x.instrument.to_numpy()[lab == q]
                    rows.append(pd.DataFrame({"date": d, "instrument": sel, "target_weight": 1/len(sel)}))
                Wq = pd.concat(rows); gq = {d: g for d, g in Wq.groupby("date")}; full, cur = [], None
                for d in days:
                    if d in gq: cur = gq[d]
                    if cur is not None: full.append(cur.assign(date=d))
                gx[q], _ = FE.book_ret(pd.concat(full), s, e)   # r9 (c): cache kept
            exc = {q: float((r - ew.reindex(r.index).fillna(0)).mean()*244) for q, r in gx.items()}
            ls = (gx[k-1] - gx[0]).dropna()
            qres[f"q{k}"] = dict(excess_vs_poolEW_ann244=exc, spearman=float(pd.Series(exc).rank().corr(pd.Series(range(k), dtype=float))),
                                 long_short_ann244_descriptive_only=float(ls.mean()*244), long_short_t_hac_lag19=hac_t(ls))
        q5 = qres["q5"]["excess_vs_poolEW_ann244"]
        mono = bool(q5[4] > q5[2] and books["top6_60w"]["vs_poolEW"]["excess_ann244"] >= books["top20_disclosure"]["vs_poolEW"]["excess_ann244"] >= 0)
        # §5 overlap with leaf 18 / 18v on this panel
        ov = {}
        Wm20 = pd.read_parquet(out/f"eval_weights_{uni}_top20_disclosure_x2_{stamp}.parquet"); Wm20["date"] = pd.to_datetime(Wm20.date)
        rt, _ = FE.book_ret(Wm20, s, e); b_ = ew.reindex(rt.index).fillna(0); x1 = rt - np.cov(rt, b_)[0, 1]/b_.var()*b_
        for lf, paths in L18_W.items():
            if not paths[uni].exists(): ov[lf] = "N/A: weights file missing"; continue
            kk = L18_KEY[lf]; repin(auth, f"dep_{kk}w_{uni.lower()}_sha256", f"dep_{kk}_{uni.lower()}_sha256")
            Wl = pd.read_parquet(paths[uni]); Wl["date"] = pd.to_datetime(Wl.date); Wl = Wl[Wl.target_weight > 0]
            # N3: leaf18/18v weights are all 0.04 (nunique=1) → rank their names by their own α file (pinned), as leaf 23 does for leaf 20
            if Wl.instrument.isna().any(): raise SystemExit(f"STOP: {lf} {uni} weight file has NaN instrument rows — report to Arch")   # r10 P3
            held_ = sorted(set(Wl.instrument) - {FE.BAL})   # r9 (b): only rows the held-row left join can match (same matches, same NaNs)
            if not held_: raise SystemExit(f"STOP: {lf} {uni} weight file has no held names (target_weight > 0, not {FE.BAL}) — report to Arch")   # r10 P3
            Al = pd.read_parquet(L18_A[lf][uni], columns=["date", "instrument", "alpha"], filters=[("instrument", "in", held_)]); Al["date"] = pd.to_datetime(Al.date)
            Wls = Wl[Wl.instrument != FE.BAL].merge(Al, on=["date", "instrument"], how="left"); del Al
            rl, _ = FE.book_ret(Wl, s, e); b2 = ew.reindex(rl.index).fillna(0); x2 = rl - np.cov(rl, b2)[0, 1]/b2.var()*b2
            js = {}
            for nm, N in (("top6_60w", 6), ("top10_100w", 10), ("top20_disclosure", 20)):
                Wm = pd.read_parquet(out/f"eval_weights_{uni}_{nm}_x2_{stamp}.parquet"); Wm = Wm[Wm.instrument != FE.BAL]; v = []
                for d in sorted(rd):
                    a_ = set(Wm[Wm.date == d].instrument); bb = set(Wls[Wls.date == d].sort_values("alpha", ascending=False).instrument.head(N))
                    if a_ | bb: v.append(len(a_ & bb)/len(a_ | bb))
                js[nm] = float(np.median(v)) if v else None
            rho = float(pd.concat([x1, x2], axis=1).dropna().corr().iloc[0, 1])
            ov[lf] = dict(rho_excess=rho, jaccard_median=js, jaccard_rank="leaf α (N3)", held_alpha_missing_share=float(Wls.alpha.isna().mean()), duplicate=bool(rho > 0.5 or (js.get("top20_disclosure") or 0) >= 0.5), hard_reject=bool(max([j for j in js.values() if j is not None], default=0) >= 0.7))
        cov = pd.read_parquet(out/f"coverage_{uni}.parquet"); cov["date"] = pd.to_datetime(cov.date); cr = cov[cov.date.isin(rd)].n
        Ar = A[A.date.isin(rd)]
        res = dict(variant=variant_tag(a), coverage_rebal_median=float(cr.median()), coverage_rebal_p10=float(cr.quantile(.1)), n_days=len(days),
                   limitup_share_in_imax_sample_pool=float(Ar.lu_share.mean()), benchmarks=bench, b3_pool_carry=b3, capadv_hiliq=capadv, books=books,
                   quantiles=qres, monotone=mono, overlap_leaf18_family=ov)
        if uni == "HILIQ":
            t6, t10 = books["top6_60w"], books["top10_100w"]
            floor = t6["cagr244"] > bench["wb_cagr244"] and t10["cagr244"] > bench["wb_cagr244"]
            tpass = (t6["vs_wb"]["t_hac"] or 0) >= T_DECISIVE and (t10["vs_wb"]["t_hac"] or 0) >= T_DECISIVE
            beat_ew = t6["vs_poolEW"]["excess_ann244"] > 0 and t10["vs_poolEW"]["excess_ann244"] > 0
            res["decisive"] = dict(is_decisive_spec=is_primary(a), wb_floor_pass=floor, t_hac_ge_2_50=tpass,
                                   beats_capadv_hiliq_recomputed=bool(t6["cagr244"] > capadv[6]["recomputed_cagr244"] and t10["cagr244"] > capadv[10]["recomputed_cagr244"]),
                                   beats_poolEW=beat_ew, report_to_leo_allowed=bool(floor and beat_ew),
                                   verdict_cap=("FAIL" if not floor else ("WATCH" if not tpass else "PENDING_EXTERNAL_GATES")),
                                   note="非判定规格一律「未做多重检验校正，仅披露」" if not is_primary(a) else "判定规格；Gate B/GATE_V3/衰减另由钉 sha 工具出")
        summ["res"][uni] = res
        del A, G, A_rd, G_rd, PX; FE._RET.clear(); trim(); print(uni, "eval done", f"rss={rss():.0f}", flush=True); peak_check(f"eval {uni}")   # r8
    uni = a.uni; summ["uni"] = uni; summ["peak_rss_mb_eval"] = rss()
    xtext(out/f"summary_{uni}_{stamp}.json", json.dumps(summ, ensure_ascii=False, indent=1, default=float))
    write_meta(out, f"eval_{uni}", auth, [f"summary_{uni}_{stamp}.json"] + sorted(p.name for p in out.glob(f"eval_weights_{uni}_*_{stamp}.parquet")), up,
               uni=uni, stamp=stamp, external_outputs=ext_out); print("STAMP", stamp)


def merge(a, panel, out, auth, up):
    """Combine summary_HILIQ_<s1>.json and summary_FULLA_<s2>.json (both listed and sha-verified in their eval_<uni>_meta,
    already chain-checked by verify_upstream) into summary_<stamp>.json; writes eval_meta.json (stage "eval": what P2-2 / CMC expect)."""
    panel_recheck(auth, panel)
    parts, stamps, metas = {}, {}, {}
    for uni in ("HILIQ", "FULLA"):
        mf = out/f"eval_{uni}_meta.json"; m = json.loads(mf.read_text(encoding="utf-8"))
        f = f"summary_{uni}_{m['stamp']}.json"
        if f not in m.get("outputs", {}) or sha(out/f) != m["outputs"][f]: raise SystemExit(f"refused: {f} not listed in / changed since {mf.name}")
        parts[uni] = json.loads((out/f).read_text(encoding="utf-8")); stamps[uni] = m["stamp"]; metas[uni] = m
        if parts[uni].get("uni") != uni or list(parts[uni].get("res", {})) != [uni]: raise SystemExit(f"refused: {f} does not hold exactly res.{uni}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summ = {k: v for k, v in parts["HILIQ"].items() if k not in ("res", "auth", "stamp", "uni", "peak_rss_mb_eval")}
    summ.update(stamp=stamp, auth=auth, auth_by_uni={u: parts[u]["auth"] for u in parts}, stamps_by_uni=stamps,
                peak_rss_mb_eval={u: parts[u]["peak_rss_mb_eval"] for u in parts}, res={u: parts[u]["res"][u] for u in ("HILIQ", "FULLA")},
                merge_note="r2.10 (a): eval split per universe (one process each, serial HILIQ → FULLA); this file = merge of summary_<uni>_<stamp>.json")
    xtext(out/f"summary_{stamp}.json", json.dumps(summ, ensure_ascii=False, indent=1, default=float))
    ext = {k: v for u in ("HILIQ", "FULLA") for k, v in metas[u].get("external_outputs", {}).items()}
    write_meta(out, "eval", auth, [f"summary_{stamp}.json"], up, stamp=stamp, stamps_by_uni=stamps, external_outputs=ext)
    peak_check("merge"); print("STAMP", stamp)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Leaf24 imax_intraday (requires Arch .ok)")
    ap.add_argument("--stage", required=True, choices=["build", "eval", "merge"])
    ap.add_argument("--uni", choices=["HILIQ", "FULLA"])
    ap.add_argument("--panel-dir", required=True, help="output/ai_factory/panel_cache_v2_resumefix; panel_cache / panel_cache_v2_fixesnone refused")
    ap.add_argument("--arch-ok", required=True)
    ap.add_argument("--src", default="intra", choices=["intra", "total"], help="intra = overnight removed (primary); total = sensitivity A")
    ap.add_argument("--k", type=int, default=5, choices=[5, 1], help="top-k days (5 primary; 1 = sensitivity B)")
    ap.add_argument("--win", type=int, default=20, choices=[20, 60], help="window (20 primary; 60 = sensitivity C)")
    ap.add_argument("--ex-fin", action="store_true", help="sensitivity D: exclude SW L1 banks / non-bank financials")
    ap.add_argument("--sealed", action="store_true")
    a = ap.parse_args()
    if a.sealed: raise SystemExit("sealed window not implemented here (prereg §6.5: once, only after X2 hard gates pass, separate .ok)")
    if a.stage in ("build", "eval") and not a.uni: raise SystemExit(f"--uni required for {a.stage} (r9: eval runs one universe per process)")
    if a.stage == "merge" and a.uni: raise SystemExit("--uni not accepted for merge")
    panel, auth = authorize(a); out = out_dir(a)
    # N6: serial order build HILIQ > build FULLA > eval HILIQ > eval FULLA > merge; first stage needs an empty out_dir; later stages chain-verify upstream metas
    if a.stage == "build" and a.uni == "HILIQ":
        if out.exists() and any(out.iterdir()): raise SystemExit(f"refused: out_dir {out} is not empty (N6: no silent overwrite; Arch decides on cleanup)")
        up = verify_leaf23_complete(auth)                            # P2-2: leaf 24 only after leaf 23 primary + 4 sensitivities
        if not is_primary(a): up.update(verify_primary_eval(auth))   # P2-2: sensitivities only after the primary eval chain
        out.mkdir(parents=True, exist_ok=True)
    else:
        if not out.is_dir(): raise SystemExit(f"refused: out_dir {out} missing (run build --uni HILIQ first)")
        need = {"build": ["build_HILIQ"],
                "eval": ["build_HILIQ", "build_FULLA"] + (["eval_HILIQ"] if a.uni == "FULLA" else []),   # r9 (a): FULLA after HILIQ
                "merge": ["eval_HILIQ", "eval_FULLA"]}[a.stage]
        up = verify_upstream(out, auth, need)
        guard_fresh(out, {"build": [f"alpha_{a.uni}_*", f"gate_{a.uni}_*", f"coverage_{a.uni}.parquet", f"build_{a.uni}_meta.json"],
                          "eval": [f"summary_{a.uni}_*.json", f"eval_weights_{a.uni}_*", f"eval_{a.uni}_meta.json", f"B3_carry_mismatch_{a.uni}.json"],
                          "merge": ["summary_2*.json", "eval_meta.json"]}[a.stage])
    {"build": lambda: build(a, panel, out, auth, up), "eval": lambda: evaluate(a, panel, out, auth, up),
     "merge": lambda: merge(a, panel, out, auth, up)}[a.stage]()
