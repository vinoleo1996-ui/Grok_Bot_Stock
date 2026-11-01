#!/usr/bin/env python3
"""Leaf23 sue_desens_cs — g1g5_ashare_sue_desens_cs_v1 — script r2.2 (r2.1 + Arch review b997cba8 §8 fixes B1–B4, N1–N8; prereg r2.1 unchanged).
Prereg: docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md (r2.1, supersedes r2; its sha256 is pinned below and must also be in the Arch .ok).
Written 2026-10-18 ET by QuantLab AI. NOT RUN at write time (syntax check only). Every stage refuses to start without an Arch
run-auth .ok (format=quantlab_run_auth_v1) pinning: this script, r2 prereg, cs_panel_dir + cs_panel_manifest_sha256, the
evaluation tools and the leaf19/20 α files (P0-2).

PRIMARY (主 Agent 01:32 ET ruling; prereg r2 §3.4): price-scaled YoY quarterly earnings change
    ΔE/P = (NI_q − NI_{q−4}) / MV_fix,   MV_fix = float mcap on the session BEFORE the earnings record's effective date (fixed
    while the record is current; P1-5 option (a)); |ΔE/P| > 0.5 → NaN; record > 200 calendar days old → NaN; MV_fix missing → no α.
    Cross-sectional rank transform: rank within SW L1 inside the pool → normal quantile (groups < 5 → 0).
SENSITIVITIES (disclosure only, never in the decisive test; need allow_sensitivity=true in the .ok):
    --signal sue      SUE = (NI_q − NI_{q−4}) / std(formal YoY diffs q−8..q−1, ≥6), clipped ±5 (winsorized), same rank transform.
    --denom daily     MV_{t−1} (previous session, updated daily) instead of MV_fix.
    --no-forecast     S_F: forecast branch off (formal reports only) — §6.5a; also the only spec ever allowed on the sealed window.
    --blackout 40     40-session forecast-information blackout.
Residualization (pool, daily OLS; 主 Agent 02:23): SW L1 dummies + Alpha frozen style set (logmv_{t−1}, beta120_{t−1}, mom t−120→t−20 at t−1, logADV20 = mean t−20..t−1) + capacity_adv leg weight_{t−1} + leaf19 α + leaf20 α;
    size-domain rank (logmv_{t−1} P70/P90) → resid on ind + logmv_{t−1} → size-domain rank = base-α. Gate: 3-day ind+logmv_{t−1}
    residual-return left tail 5% → gate 0 (not in α). Financials + 600519/002371 excluded from the factor (benchmarks keep full pool).
Panel (P0-1, prereg §3.7): output/ai_factory/panel_cache_v2_resumefix (build_version cs_panel_v2_resumefix). Signal/selection read
    only v1 mask columns (hiliq/fulla); is_resume_day/hiliq_carry are never read by fund/build (asserted). Booking: suspended holdings
    keep weight with 0 return (no row → 0), resume-day rows book their real ret/ret_on. is_resume_day is used only as a no-new-buy
    entry gate at rebalance and for disclosure; hiliq_carry only for disclosure counts. Benchmarks/quantiles use the same panel+booking.
Books (P1-3): tiers re-pick 6 (60万) / 10 (100万) names from the gate=1 list by α, 6% each, industry ≤25%, remainder 510300 (asserted
    daily; cap 25% per Arch review 0d9bd147 line 96, P1-3). The 20×4% book and 20%-cap top-6/10 books (Core mandate) are disclosure only. Engine = FE.book_ret wb_SD0 (T+1 open, 17.5bp one-sided × Σ|Δw|), SD0 disclosed.
Benchmarks (P1-1): ① capadv-HI_LIQ single-leg book-smoke (Strategy X2 nav as filed + recomputed on this panel; decision uses the
    recomputed value), ② HI_LIQ wb (pool float-mcap weighted, members & weights at T−1, ret at T, same panel), ③ 510300.
    Pool EW (members at T−1 × ret at T, resume rows included, no clipping) disclosed alongside.
Decisive (§9): HI_LIQ, primary, 20-session blackout, 17.5bp, 60万 top-6 & 100万 top-10: both tiers net CAGR > HI_LIQ wb (else FAIL)
    and HAC t (lag 19) of daily net excess vs HI_LIQ wb ≥ 2.50 in both tiers (else at most WATCH). Gate B / GATE_V3 / decay / ρ / Jaccard
    vs leaves 15–22 are computed afterwards with the pinned tools (research/alpha_combo_marginal_v1_1.py --universe hiliq --base capadv --arch-ok <CMC v1.1 .ok> [--legacy-json …]; legacy bee23019 = comparison column only; leaf_selfcheck_v3).
Windows: X2 only. Sealed window not implemented here (--sealed exits): §6.5a, S_F only, once, after all X2 hard gates pass.
Stages: --stage fund | build --uni HILIQ|FULLA | eval --uni HILIQ|FULLA | merge.  Year-chunked; in-process 1.5GB RSS kill; one research job at a time.
r2.10 (Arch 06:03 after the r2.9 X2 stop at stage 04, eval exit 137 RSS guard; NOT RUN — static checks only; RSS limit stays 1.5GB):
    (a) eval split into one process per universe (--stage eval --uni HILIQ, then --uni FULLA) + --stage merge (combines the per-universe
        summaries into summary_<stamp>.json and writes eval_meta.json); chain eval_HILIQ ← fund+build_HILIQ+build_FULLA, eval_FULLA ← same
        + eval_HILIQ, merge ← both eval_<uni>; a sensitivity's first stage needs the primary eval_HILIQ, eval_FULLA and eval (merge) metas;
    (b) eval column reduction only (PX drops logmv/<uni col>; leaf-20 α read only from the first leaf-20 weight date on; pick_book merges
        only rebalance-day α/gate rows); no dtype change (ret/logmv/close stay as stored);
    (c) pool_benchmarks frees per-year frames as soon as they are no longer needed + allocator trim (gc + pyarrow pool release_unused +
        malloc_trim) at segment ends; FE return cache loaded once per eval process and kept (was cleared and re-read after every book);
    (d) watchdog checks VmRSS and VmHWM; explicit peak check (VmHWM and ru_maxrss) at the end of each pool_benchmarks year and each
        uni eval / merge → RSS_GUARD_KILL, os._exit(137);
    Arch r2.9 review P3s: to_session NaT fill uses the calendar's own unit; build casts ev/evo merge keys once, before the year loop.
r2.11 (Arch B3 diagnosis 561219c7 + leaf-24 r9 review b771b4be P1-1; NOT RUN — static checks only): pool_benchmarks membership carry on
    EVERY mask-suspended day, panel row or not: carry_nc = (sus == 1) & (~has | restored) (restored = panel row_origin == "restored");
    float-mcap anchors B / B_dd follow the same carry (restored rows carry the pre-suspension mcap, never their own logmv); A_nc / carry_dd
    derive from the new carry_nc; hard stop unless, on every panel row, mask suspended=True <=> row_origin=restored, and a panel row
    without a mask row also stops; carried name-days by mask reason counted on (S & sus==1). Delist cut, P2-B, cut_fail and both B3
    checks unchanged; no data change, no whitelist. Also r2.10 P3s: watchdog no longer swallows errors (prints RSS_WATCHDOG_ERROR and
    exits 137, fail-closed); resume re-checks the upstream (r2.9) .ok data/panel/fund-build pins against this .ok. Shared functions
    byte-identical with leaf 24 r10 (docstrings of rss_watchdog / peak_check / trim / merge made neutral).
    No numerical change intended in any stage.
    Resume (主 Agent 06:16, primary only, needs Arch sha check of the r2.9 fund/build outputs): .ok keys resume_upstream_script_sha256 /
        resume_upstream_arch_ok_sha256 / resume_{fund,build_hiliq,build_fulla}_meta_sha256 = "none" (fresh chain, default) or the pinned
        r2.9 values; when pinned, the primary eval_HILIQ / eval_FULLA accept exactly those three r2.9 metas (file sha pinned, fields,
        every output sha and upstream sha re-checked by check_meta) in place of same-script metas; primary fund/build refuse to start;
        sensitivities ignore the keys and always run their own fresh chain (fund → build → eval → merge under this script).
r2.2 (Arch b997cba8, 2026-10-18 ET, NOT RUN — py_compile only): B1 FIN is real code + assert len==2; B2 only <panel>/manifest.json + step/mode
    + RECEIPT_D1b_resume_execute.json PASS/manifest sha; B3 pool EW/wb carry pre-suspension membership + float mcap through suspension (not
    after delisting), assert Mp == hiliq_carry/fulla_carry on restored resume rows (stop on mismatch), old no-carry construction disclosed;
    B4 current record = latest end_date first (formal niq NaN included), then d1; d1 NaN → no α (no fallback to an older quarter; forecast
    records whose niq cannot be computed are still not usable records), old-method fallback name-days disclosed; N1 ic_tstat_hac inlined
    (no leaf_selfcheck_v3 import) + alpha_decay_gate/leaf_selfcheck_common pinned; N2 all read inputs pinned and re-hashed before use;
    N4 excluded-name count + wb weight share; N5 strict .ok parser + explicit keys; N6 non-empty out_dir refused + stage meta chain;
    N8 ind_names.csv only from the panel dir.
fix-2 (Arch 129d67c5, NOT RUN — py_compile only): P1-1 B3 state recursed from 2018, carry only on mask-suspended no-row days, mask pinned
    (data_mask_sha256 == D1b receipt pins.mask_sha256), carried name-days by mask reason must all be suspended; P1-2 variant must be one item of
    sensitivity_specs; P1-3/P2-4 process check (research/ python, scripts/fix_sd1/, scripts_eng/, scripts/nightly_update.py block; scripts/acquire/
    logged; ancestors excluded; niceness ≥ 10; MemAvailable ≥ 2GB; ps snapshot in meta); P2-1 .ok whitelist + fixed values + tool_cmds file;
    P2-2 stage chains across variants and leaf 24; P2-3 exclusive create; P2-6 all years 2018–2026 verified;
    P3 asserts → raise, carry_col for FULLA, panel re-hash per stage.
live=false; promotion_approved=false; no GP; no Book-Smoke.
"""
import argparse, hashlib, json, os, re, sys, gc, threading, time, resource, ctypes
import numpy as np, pandas as pd, pyarrow as pa
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
from statistics import NormalDist

R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R))
PREREG = R/"docs/v2/AI_G1G5_SUE_DESENS_WHO_PAYS_PREREG_R2_1_ZH.md"
PREREG_SHA = "8f5d8ac43ba49f11b4461a287addae8c0cf247fbe9d8e81d0b339764e843922e"
PANEL_VERSION = "cs_panel_v2_resumefix"; REJECT_PANELS = {"panel_cache", "panel_cache_v2_fixesnone"}
FORBIDDEN_SIGNAL_COLS = {"is_resume_day", "hiliq_carry"}
FP = R/"data/v2/financials_pit"; FC = R/"data/v2/events/forecast_2024plus.parquet"
L19 = {"HILIQ": R/"output/ai_factory/leaf19_cfacc_rnoa/alpha_HILIQ_20261014_213132.parquet",
       "FULLA": R/"output/ai_factory/leaf19_cfacc_rnoa/alpha_FULLA_20261014_213132.parquet"}
L20 = {"HILIQ": R/"output/ai_factory/leaf20_sue_resid/alpha_HILIQ_20261014_220029.parquet",
       "FULLA": R/"output/ai_factory/leaf20_sue_resid/alpha_FULLA_20261014_220029.parquet"}
L20_W = {"HILIQ": R/"output/ai_factory/leaf20_sue_resid/eval_weights_HILIQ_x2_20261014_220029.parquet",
         "FULLA": R/"output/ai_factory/leaf20_sue_resid/eval_weights_FULLA_x2_20261014_220029.parquet"}
CAPADV = {6: R/"output/strategy_hiliq/capadv_x2/aum_600000/X2/BOOK", 10: R/"output/strategy_hiliq/capadv_x2/aum_1000000/X2/BOOK"}
CAPLEG = R/"output/strategy_hiliq/legs/g1g5_capacity_adv_hiliq_v1_1_daily_weights_20261014_195620.parquet"
FIN_PIT = FP/"financials_pit_tushare.parquet"; ETF = R/"data/v2/etf/etf_daily_adj.parquet"; MASK = R/"output/strategy_hiliq/universe_mask_hiliq_v1.parquet"
DELISTED = R/"data/v2/delisted/delisted_master_tushare.parquet"   # Arch bd3abe5c P1-A (63590f23… at review)
TOOLS = {"dep_fe_sha256": R/"research/g1g5_fund_resid_alpha.py", "dep_selfcheck_sha256": R/"research/leaf_selfcheck_v3.py",
         "dep_combo_sha256": R/"research/alpha_combo_marginal_v1_1.py", "dep_combo_legacy_sha256": R/"research/alpha_combo_marginal.py",   # CMC v1.1 r3 / legacy bee23019 (comparison column only)
         "dep_adg_sha256": R/"research/alpha_decay_gate.py", "dep_lc_sha256": R/"research/leaf_selfcheck_common.py",   # N1 import closure of leaf_selfcheck_v3
         "dep_l19_hiliq_sha256": L19["HILIQ"], "dep_l19_fulla_sha256": L19["FULLA"],
         "dep_l20_hiliq_sha256": L20["HILIQ"], "dep_l20_fulla_sha256": L20["FULLA"],
         "dep_l20w_hiliq_sha256": L20_W["HILIQ"], "dep_l20w_fulla_sha256": L20_W["FULLA"],                               # N2
         "dep_capadv600_tw_sha256": CAPADV[6]/"target_weights.parquet", "dep_capadv600_nav_sha256": CAPADV[6]/"nav.csv",
         "dep_capadv1000_tw_sha256": CAPADV[10]/"target_weights.parquet", "dep_capadv1000_nav_sha256": CAPADV[10]/"nav.csv",
         "data_forecast_sha256": FC, "data_financials_sha256": FIN_PIT, "data_etf_daily_adj_sha256": ETF, "data_mask_sha256": MASK, "data_delisted_sha256": DELISTED,
         "dep_capadv_leg_sha256": CAPLEG}   # prereg r2.1 §1/§4: residualize on capacity_adv (HI_LIQ v1.1 leg weights, 3b288c83…)
LEAF_NO = "23"; OUT_ROOT = R/"output/ai_factory/leaf23_sue_desens_cs"; D1B_STEP = "D1b_resume_execute"; PANEL_YEARS = tuple(range(2018, 2027))   # P2-6: every year the B3 recursion reads
CMC_V11_SHA = "5658f612fef313fc5b818fc4cb9d594d757377e0dbf7c7dc86a6e31788b88911"      # Alpha handoff ab6d1e82 r3; passed Arch review bbfcb7ef; full-run .ok not yet signed
CMC_LEGACY_SHA = "bee230199ac27bf9730aa77c63b104a67bb104229622c57524867a9b54a5c51c"   # old alpha_combo_marginal.py: disclosure-only comparison column
OK_LINE = re.compile(r"^([a-z0-9_]+)=(\S+)$")
AIF = R/"output/ai_factory"; TOOL_CMDS = AIF/f"ARCH_TOOL_CMDS_LEAF{LEAF_NO}_X2.cmd"   # Alpha 77441f16 P1: f-string (was literal {LEAF_NO})   # Arch 129d67c5 §5-1: tool command lines live in a pinned .cmd file
TOOL_CLOSURE = {"tool_closure_adj_price_sha256": R/"research/adj_price.py", "tool_closure_panel_stitch_sha256": R/"research/g1g5_x2_panel_stitch.py",
                "tool_closure_moneyflow_sha256": R/"research/g1g5_moneyflow_resid_weights.py", "tool_closure_nontextbook_sha256": R/"research/g1g5_nontextbook_weights.py"}
X2S, X2E = "2024-06-03", "2026-10-09"   # Alpha 486496a9 P1-1: assigned before OK_FIXED reads them (values unchanged)
OK_FIXED = {"format": "quantlab_run_auth_v1", "signed_by": "arch", "scope": "X2", "leaf": LEAF_NO, "live": "false", "promotion": "false",
            "promotion_approved": "false", "allow_full": "true", "allow_smoke": "false", "allow_sealed": "false", "cs_panel_build_version": PANEL_VERSION,
            "mechanism_tag": "g1g5_ashare_sue_desens_cs_v1", "window_start": X2S, "window_end": X2E, "rss_limit_mb": "1500",
            "serial_order": "fund>build_HILIQ>build_FULLA>eval_HILIQ>eval_FULLA>merge>sensitivities>leaf24", "sensitivity_specs": "sig-sue,denom-daily,nofc,bo40", "run_niceness": "10",
            "tool_cmds_path": str(TOOL_CMDS)}   # N5 / P2-1: explicit, fixed values
OK_REQUIRED = ("script_sha256", "prereg_sha256", "cs_panel_dir", "cs_panel_manifest_sha256", "out_dir", "allow_sensitivity", "tool_cmds_sha256", "issued_at", "expires_et")
OK_RESUME = ("resume_upstream_script_sha256", "resume_upstream_arch_ok_sha256", "resume_fund_meta_sha256", "resume_build_hiliq_meta_sha256",
             "resume_build_fulla_meta_sha256")   # r2.10 resume (主 Agent 06:16): all "none" = fresh chain; all 64-hex = primary eval resumes on pinned r2.9 fund/build metas
RESUME_META = {"fund": "resume_fund_meta_sha256", "build_HILIQ": "resume_build_hiliq_meta_sha256", "build_FULLA": "resume_build_fulla_meta_sha256"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BLOCK_CMDS = ("scripts/fix_sd1/", "scripts_eng/", "scripts/nightly_update.py"); LOG_ONLY_CMDS = ("scripts/acquire/",)
MIN_NICE, MIN_MEMAVAIL_KB = 10, 2*1024*1024
TIERS = {6: 600_000, 10: 1_000_000}; TIER_W, TIER_IND_CAP, DISC_N, DISC_W, CORE_IND_CAP = 0.06, 0.25, 20, 0.04, 0.20  # 25% = Arch P1-3 (review l.96); 20% = disclosure
FUND_YEARS = (2023, 2024, 2025, 2026)
STALE_DAYS, CLIP_C, SUE_CLIP, RSS_LIMIT_KB, T_DECISIVE, HAC_H = 200, 0.5, 5.0, 1536000, 2.50, 20   # 1536000 KB = rss_limit_mb 1500
rss = lambda: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ND = NormalDist()


# ---------------------------------------------------------------- guards
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


def is_primary(a): return a.signal == "dep" and a.denom == "fixed" and not a.no_forecast and a.blackout == 20


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
    allowed = set(OK_FIXED) | set(OK_REQUIRED) | set(OK_RESUME) | set(TOOLS) | set(TOOL_CLOSURE)
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
    rv = [ok[k] for k in OK_RESUME]; resume = all(HEX64.match(v) for v in rv)
    checks["resume_keys_all_none_or_all_hex"] = resume or all(v == "none" for v in rv)
    if resume:   # applies to the primary variant only (sensitivities ignore it and run their own fresh chain); primary fund/build are not re-run
        checks["resume_upstream_is_other_script"] = ok["resume_upstream_script_sha256"] != me
        checks["resume_no_primary_fund_build"] = not (is_primary(a) and a.stage in ("fund", "build"))
        checks["resume_upstream_ok_pins_equal"] = resume_pins_equal(ok) if is_primary(a) else True   # r2.11 (P3)
    resume = resume and is_primary(a)
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
                       variant=variant_tag(a), primary=is_primary(a), out_dir=str(out_dir(a)),
                       resume={k: ok[k] for k in OK_RESUME} if resume else None)


RESUME_PIN_KEYS = ("prereg_sha256", "cs_panel_dir", "cs_panel_manifest_sha256", "cs_panel_build_version", "data_mask_sha256", "data_delisted_sha256",
                   "data_forecast_sha256", "data_financials_sha256", "data_etf_daily_adj_sha256", "dep_fe_sha256", "dep_l19_hiliq_sha256",
                   "dep_l19_fulla_sha256", "dep_l20_hiliq_sha256", "dep_l20_fulla_sha256", "dep_capadv_leg_sha256")


def resume_pins_equal(ok):
    """r2.11 (r2.10 review P3): the upstream .ok (found by its pinned sha under output/ai_factory or output/ai_factory/_consumed) must carry the
    same data / panel / prereg / fund-build input pins as this .ok; otherwise the resumed fund/build metas were made on other inputs → refuse."""
    want = ok["resume_upstream_arch_ok_sha256"]
    hits = [p for d in (AIF, AIF/"_consumed") for p in sorted(d.glob(f"ARCH_RUN_AUTH_LEAF{LEAF_NO}_*.ok")) if sha(p) == want]
    if not hits: raise SystemExit(f"refused: resume upstream .ok {want[:12]} not found under {AIF} or {AIF/'_consumed'}")
    up = read_ok(hits[0]); bad = [k for k in RESUME_PIN_KEYS if up.get(k) != ok.get(k)]
    if bad: raise SystemExit(f"refused: resume upstream .ok {hits[0].name} pins differ from this .ok {bad}")
    return True


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
    up, rs = {}, auth.get("resume")
    for st in stages:
        mf = out/f"{st}_meta.json"
        if rs and st in RESUME_META:   # r2.10 resume: pinned r2.9 meta (file sha from the .ok; fields + every output sha + upstream shas re-checked)
            if not mf.is_file() or sha(mf) != rs[RESUME_META[st]]: raise SystemExit(f"refused: {mf.name} sha != .ok {RESUME_META[st]} (resume)")
            want = same_run(auth, stage=st, variant=auth["variant"]); want.update(script_sha256=rs["resume_upstream_script_sha256"], arch_ok_sha256=rs["resume_upstream_arch_ok_sha256"])
            check_meta(mf, want)
        else: check_meta(mf, same_run(auth, stage=st, variant=auth["variant"]))
        up[str(mf.relative_to(AIF))] = sha(mf)
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


def variant_tag(a):
    t = [] if a.signal == "dep" else ["sig-sue"]
    if a.denom == "daily": t.append("denom-daily")
    if a.no_forecast: t.append("nofc")
    if a.blackout != 20: t.append(f"bo{a.blackout}")
    return "_".join(t) or "primary"


# ---------------------------------------------------------------- helpers
def ymd(s):
    s = pd.Series(s).astype(str).str.replace("-", "", regex=False).str[:8]
    return pd.to_datetime(s, format="%Y%m%d", errors="coerce")


def read_panel(panel, y, cols, lo=None):
    if set(cols) & FORBIDDEN_SIGNAL_COLS: raise RuntimeError("signal/selection code must not read is_resume_day/hiliq_carry (P2-8)")
    flt = [("date", ">=", pd.Timestamp(lo).to_pydatetime())] if lo is not None else None
    x = pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=cols, filters=flt); x["date"] = pd.to_datetime(x.date); return x


def calendar(panel):
    ds = [read_panel(panel, y, ["date"]).date.unique() for y in FUND_YEARS]
    return pd.DatetimeIndex(sorted(set(pd.to_datetime(np.concatenate(ds)))))


def to_session(cal, d, plus=0):
    d = pd.DatetimeIndex(d); i = cal.searchsorted(d, side="left") + plus
    out = np.full(len(i), np.datetime64("NaT", np.datetime_data(cal.values.dtype)[0]), dtype=cal.values.dtype); ok = (i < len(cal)) & ~d.isna()   # r2.9 Arch P0: calendar resolution; r2.10 P3: NaT in the calendar's own unit
    out[ok] = cal.values[i[ok]]; return pd.DatetimeIndex(out)


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


# ---------------------------------------------------------------- stage fund (PIT event table; reads financials, forecasts, panel logmv only)
def current_records(E):
    """latest quarter; formal beats forecast; latest revision — the 'current record' per name and effective session."""
    key = (E.end_date.map(pd.Timestamp.toordinal).astype("int64")*2 + (E.src == "formal").astype("int64"))*1_000_000 \
        + E.eff.map(pd.Timestamp.toordinal).astype("int64")
    E = E.assign(key=key).sort_values(["eff", "key"])
    return E[E.key == E.groupby("ts_code").key.cummax()].drop_duplicates(["ts_code", "eff"], keep="last")


def fund(a, panel, out, auth, up):
    panel_recheck(auth, panel); repin(auth, "dep_fe_sha256", "data_financials_sha256", "data_forecast_sha256")
    import research.g1g5_fund_resid_alpha as FE
    cal = calendar(panel)
    fi = FE.first_version(pd.read_parquet(FIN_PIT, columns=["ts_code", "end_date", "available_at", "report_type", "n_income_attr_p"])
                          .query("report_type=='1'"), ["n_income_attr_p"])
    fi = fi[fi.ts_code.str[:1].isin(list("036"))].copy(); fi["end_date"] = pd.to_datetime(fi.end_date.astype(str))
    fi = FE.single_q(fi, "n_income_attr_p").rename(columns={"n_income_attr_p": "ytd", "n_income_attr_p_q": "niq"})
    fi["eff"] = to_session(cal, fi.avail)  # formal: first session ≥ available_at + 1 day, no blackout
    F = fi[["ts_code", "end_date", "eff", "ytd", "niq"]].dropna(subset=["eff"]).sort_values(["ts_code", "end_date"])
    # SUE-sensitivity history: formal YoY diffs with exact 4-quarter lag; std over the 8 quarters ending at this row (≥6)
    g = F.groupby("ts_code"); lagok = g.end_date.shift(4) == F.end_date - pd.DateOffset(years=1)
    F["dq"] = (F.niq - g.niq.shift(4)).where(lagok)
    F["sdq"] = F.groupby("ts_code").dq.transform(lambda s: s.rolling(8, min_periods=6).std())
    parts = [F.assign(src="formal")[["ts_code", "end_date", "eff", "niq", "src"]]]
    bl = []
    if not a.no_forecast:
        fc = pd.read_parquet(FC, columns=["ts_code", "ann_date", "end_date", "net_profit_min", "net_profit_max", "update_flag", "available_at"])
        fc = fc[fc.ts_code.str[:1].isin(list("036"))].copy()
        fc["uf"] = pd.to_numeric(fc.update_flag, errors="coerce").fillna(0)
        fc = fc.sort_values("uf").drop_duplicates(["ts_code", "end_date", "ann_date"], keep="last")
        fc = fc.dropna(subset=["net_profit_min", "net_profit_max"])  # one-sided / type-only rows: not used, not in blackout table
        fc["np_mid"] = (fc.net_profit_min.astype(float) + fc.net_profit_max.astype(float))/2*1e4  # 万元 → 元
        fc["end_date"] = ymd(fc.end_date); fc["day1"] = to_session(cal, ymd(fc.available_at))
        fc["eff"] = to_session(cal, fc.day1, plus=a.blackout)  # day 1 + blackout sessions → first usable session
        fc = fc.dropna(subset=["end_date", "day1"])
        prev = F[["ts_code", "end_date", "eff", "ytd"]].rename(columns={"end_date": "pend", "eff": "peff", "ytd": "pytd"})
        fc = fc.assign(pend=fc.end_date - pd.offsets.QuarterEnd(1)).merge(prev, on=["ts_code", "pend"], how="left")
        q1 = fc.end_date.dt.quarter == 1
        fc["niq"] = np.where(q1, fc.np_mid, np.where(fc.peff < fc.day1, fc.np_mid - fc.pytd, np.nan))
        for t, d1, ef in fc[["ts_code", "day1", "eff"]].itertuples(index=False):  # information blackout (stock not excluded)
            i0 = cal.searchsorted(d1); i1 = cal.searchsorted(ef) if not pd.isna(ef) else len(cal)
            bl.append(pd.DataFrame({"date": cal[i0:i1], "instrument": t}))
        parts.append(fc.dropna(subset=["eff", "niq"]).assign(src="forecast")[["ts_code", "end_date", "eff", "niq", "src"]])
    (pd.concat(bl).drop_duplicates() if bl else pd.DataFrame({"date": pd.DatetimeIndex([]), "instrument": pd.Series([], dtype=str)})
     ).pipe(lambda df_: xparquet(df_, out/"blackout_pairs.parquet"))
    # B4: formal records take part in the current-record choice as soon as they have eff (niq may be NaN); forecast records whose niq
    # cannot be computed were already dropped above (not a usable record — unchanged, stated in the receipt)
    E = pd.concat(parts, ignore_index=True).dropna(subset=["eff"])
    lag4 = F.dropna(subset=["niq"])[["ts_code", "end_date", "eff", "niq"]].rename(columns={"end_date": "e4", "eff": "f4", "niq": "n4"})
    E = E.assign(e4=E.end_date - pd.offsets.QuarterEnd(4)).merge(lag4, on=["ts_code", "e4"], how="left")
    E.loc[~(E.f4 <= E.eff), "n4"] = np.nan                       # NI_{q−4}: formal only, already effective
    sdl = F[["ts_code", "end_date", "eff", "sdq"]].rename(columns={"end_date": "e1", "eff": "f1", "sdq": "sd"})
    E = E.assign(e1=E.end_date - pd.offsets.QuarterEnd(1)).merge(sdl, on=["ts_code", "e1"], how="left")
    E.loc[~(E.f1 <= E.eff), "sd"] = np.nan                       # SUE std uses formal q−8..q−1 only
    E["d1"] = E.niq - E.n4
    Eo = current_records(E.dropna(subset=["d1"]))   # OLD r2.1 order (drop rows, then choose) — kept only to disclose fallback name-days
    xparquet(Eo[["ts_code", "end_date", "eff", "d1"]], out/"event_table_oldsel.parquet"); n_old = int(len(Eo)); del Eo
    E = current_records(E)                          # B4: choose the current record first (latest end_date) …
    n_d1_nan = int(E.d1.isna().sum())               # … then d1 = NI_q − NI_{q−4}; NaN → no α (no fallback to an older quarter)
    # P1-5 (a): fixed denominator = log float mcap on the session before eff (panel logmv, log 元)
    LM = pd.concat([read_panel(panel, y, ["date", "instrument", "logmv"]) for y in FUND_YEARS])
    LM = LM.pivot_table(index="date", columns="instrument", values="logmv").sort_index().astype("float32")
    pi = LM.index.searchsorted(pd.DatetimeIndex(E.eff), side="left") - 1
    ci = LM.columns.get_indexer(E.ts_code); okk = (pi >= 0) & (ci >= 0)
    E["lmv_fix"] = np.nan; E.loc[okk, "lmv_fix"] = LM.to_numpy()[pi[okk], ci[okk]]
    del LM; gc.collect()
    xparquet(E[["ts_code", "end_date", "eff", "src", "d1", "sd", "lmv_fix"]], out/"event_table.parquet")
    write_meta(out, "fund", auth, ["event_table.parquet", "event_table_oldsel.parquet", "blackout_pairs.parquet"], up,
               rows=int(len(E)), rows_current_d1_nan=n_d1_nan, rows_oldsel=n_old,
               input_sha={"forecast": sha(FC), "financials": sha(FIN_PIT)})
    print("fund done", f"rss={rss():.0f}", flush=True)


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
    panel_recheck(auth, panel); repin(auth, "dep_fe_sha256", f"dep_l19_{a.uni.lower()}_sha256", f"dep_l20_{a.uni.lower()}_sha256",
                                     "data_etf_daily_adj_sha256", "dep_capadv_leg_sha256")
    import research.g1g5_fund_resid_alpha as FE
    uni = a.uni; col = FE.UCOL[uni]
    FIN = load_fin(panel)   # B1: real code line (was inside a comment → NameError); asserts len(FIN) == 2; N8: panel dir only
    ev = pd.read_parquet(out/"event_table.parquet").rename(columns={"ts_code": "instrument"}).sort_values("eff")
    evo = pd.read_parquet(out/"event_table_oldsel.parquet").rename(columns={"ts_code": "instrument", "eff": "eff_o", "end_date": "end_o", "d1": "d1_o"}).sort_values("eff_o")
    written, fallback, gap_share = [], {}, {}
    blk = pd.read_parquet(out/"blackout_pairs.parquet").assign(blk=np.int8(1))
    lo_x2 = pd.Timestamp(X2S).to_pydatetime()
    A19 = pd.read_parquet(L19[uni], columns=["date", "instrument", "alpha"], filters=[("date", ">=", lo_x2)]).rename(columns={"alpha": "a19"})
    A20 = pd.read_parquet(L20[uni], columns=["date", "instrument", "alpha"], filters=[("date", ">=", lo_x2)]).rename(columns={"alpha": "a20"})
    # prereg r2.1 §1 "去敏 = residualize on style, capacity_adv, industry, leaf19/20": capacity_adv exposure = its HI_LIQ v1.1 leg target weight
    # lagged one leg session per name (t−1, Alpha 77441f16 §4a; was same-day in r2.3), 0 if not held, 510300 balance row dropped; sparse
    # (~25 non-zero of ~800 HI_LIQ names per day); first-stage OLS regressor only (demeaned), not in the second-stage industry+lmv1 step
    # r2.8 (run stop 05:49, stage 02): leg `date` is stored as string → no pushdown filter; convert first, then cut (same rows as intended)
    CAPW = pd.read_parquet(CAPLEG, columns=["date", "instrument", "target_weight"]).rename(columns={"target_weight": "acap"})
    CAPW["date"] = pd.to_datetime(CAPW.date, format="%Y-%m-%d"); CAPW = CAPW[CAPW.date >= pd.Timestamp(X2S) - pd.Timedelta(days=20)]
    CAPW = CAPW[CAPW.instrument != FE.BAL].sort_values(["instrument", "date"])
    CAPW["acap"] = CAPW.groupby("instrument", sort=False).acap.shift(1); CAPW = CAPW[CAPW.date >= pd.Timestamp(X2S)]
    for t in (A19, A20): t["date"] = pd.to_datetime(t.date)
    pdt = read_panel(panel, 2024, ["date"], pd.Timestamp(X2S)).date.dtype   # r2.10 P3: the loop's P.date dtype (same read_panel conversion), taken once
    ev["eff"] = ev.eff.astype(pdt); evo["eff_o"] = evo.eff_o.astype(pdt)   # r2.9 Arch P0: merge keys share P.date resolution (cast once, outside the loop)
    BR = bench_ret(); tail = defaultdict(lambda: deque(maxlen=3)); cov = []
    for y in (2024, 2025, 2026):
        lo = pd.Timestamp("2023-06-01") if y == 2024 else pd.Timestamp(f"{y-1}-05-01")   # ≥ 121 sessions for mom t−120→t−20 / beta120
        P = pd.concat([read_panel(panel, yy, ["date", "instrument", "ret", "logmv", "ind", "adv20_yuan", col], lo) for yy in sorted({lo.year, y})])
        RW = P.pivot_table(index="date", columns="instrument", values="ret").sort_index().astype("float32")
        LM = P.pivot_table(index="date", columns="instrument", values="logmv").reindex_like(RW).astype("float32")
        AD = P.pivot_table(index="date", columns="instrument", values="adv20_yuan").reindex_like(RW).astype("float32")
        feats = style_feats(RW, LM, AD, BR); del AD   # Alpha frozen style set, all t−1 (lmv1 = previous-session logmv, ε erratum)
        gstart = pd.Timestamp(X2S) - pd.Timedelta(days=10) if y == 2024 else pd.Timestamp(f"{y}-01-01")
        P = P[(P.date >= gstart) & (P.date.dt.year == y) & (P.date <= X2E) & P[col].fillna(False).astype(bool) & (P.ind >= 0) & ~P.ind.isin(FIN)].copy()
        for nm, M in feats.items(): P = P.join(M.stack().rename(nm).astype("float32"), on=["date", "instrument"])
        del RW, LM, feats; gc.collect()
        P = P.dropna(subset=["lmv1", "beta120", "mom_120_20", "ladv1", "ret"]); P = P[~P.instrument.isin(FE.EXCL)].sort_values("date")
        gap_share[str(y)] = float((P.loc[P.date >= X2S, "nv120"] < 100).mean()) if (P.date >= X2S).any() else None   # Arch P3-C
        if P.date.dtype != pdt: raise SystemExit(f"STOP: panel {y} date dtype {P.date.dtype} != {pdt} (merge-key resolution)")
        P = pd.merge_asof(P, ev[["instrument", "eff", "end_date", "src", "d1", "sd", "lmv_fix"]], left_on="date", right_on="eff", by="instrument", direction="backward")
        P = pd.merge_asof(P, evo, left_on="date", right_on="eff_o", by="instrument", direction="backward")   # B4 disclosure only
        fallback[str(y)] = int(((P.date >= X2S) & P.d1.isna() & P.d1_o.notna() & (P.end_o < P.end_date)
                                & ((P.date - P.eff_o).dt.days <= STALE_DAYS)).sum())   # name-days the old order would have filled from an older quarter
        P = P.drop(columns=["eff_o", "end_o", "d1_o"])
        denom = np.exp((P.lmv_fix if a.denom == "fixed" else P.lmv1).astype("float64"))  # logmv = log(float_mktcap, 元)
        if a.signal == "dep": P["sig"] = (P.d1/denom).where(lambda s: s.abs() <= CLIP_C)
        else: P["sig"] = (P.d1/P.sd.where(P.sd > 0)).clip(-SUE_CLIP, SUE_CLIP)
        P.loc[(P.date - P.eff).dt.days > STALE_DAYS, "sig"] = np.nan
        P = P.merge(A19, on=["date", "instrument"], how="left").merge(A20, on=["date", "instrument"], how="left").merge(blk, on=["date", "instrument"], how="left")
        P = P.merge(CAPW, on=["date", "instrument"], how="left")
        P[["a19", "a20", "acap"]] = P[["a19", "a20", "acap"]].fillna(0.0); P["blk"] = P.blk.fillna(0).astype("int8")
        AL, GL = [], []
        for d, g in P.groupby("date", sort=True):
            if len(g) < 100: continue
            ind = g.ind.to_numpy(); D = (ind[:, None] == np.unique(ind)[None, :]).astype(float)
            S = g[["lmv1", "beta120", "mom_120_20", "ladv1"]].to_numpy(float); S = (S - S.mean(0))/S.std(0)
            eps = FE.ols_resid(g.ret.to_numpy(float).clip(-.21, .31), np.column_stack([D, S[:, :1]])); qd = np.quantile(eps, .05)
            ins = g.instrument.to_numpy()
            for i_, e_ in zip(ins, eps): tail[i_].append(e_ < qd)
            if d < pd.Timestamp(X2S): continue  # warm-up: past price features only; nothing written before X2
            GL.append(pd.DataFrame({"date": d, "instrument": ins, "gate": np.array([0 if any(tail[i_]) else 1 for i_ in ins], dtype="int8")}))
            sv = g.sig.to_numpy(float); ok = np.isfinite(sv)
            if ok.sum() < 50: cov.append((d, int(ok.sum()))); continue
            raw = rank_ind(sv, ind)[ok]
            X = np.column_stack([D, S, g.a19.to_numpy(float) - g.a19.mean(), g.a20.to_numpy(float) - g.a20.mean(), g.acap.to_numpy(float) - g.acap.mean()])
            r1 = FE.ols_resid(raw, X[ok]); mv = g.lmv1.to_numpy(float)[ok]
            al, dom = FE.dom_rank(r1, mv); al = FE.ols_resid(al, np.column_stack([D[ok], S[ok][:, :1]])); al, _ = FE.dom_rank(al, mv)
            AL.append(pd.DataFrame({"date": d, "instrument": ins[ok], "alpha": al.astype("float32"), "size_domain": dom.astype("int8"), "ind": ind[ok],
                                    "raw": raw.astype("float32"), "src": g.src.to_numpy()[ok], "blk": g.blk.to_numpy()[ok]}))
            cov.append((d, int(ok.sum())))
        if AL: xparquet(pd.concat(AL), out/f"alpha_{uni}_{y}.parquet"); written.append(f"alpha_{uni}_{y}.parquet")
        if GL: xparquet(pd.concat(GL), out/f"gate_{uni}_{y}.parquet"); written.append(f"gate_{uni}_{y}.parquet")
        print(uni, y, "built", f"rss={rss():.0f}", flush=True); del P, AL, GL; gc.collect()
    xparquet(pd.DataFrame(cov, columns=["date", "n"]), out/f"coverage_{uni}.parquet"); written.append(f"coverage_{uni}.parquet")
    write_meta(out, f"build_{uni}", auth, written, up, uni=uni, b4_oldorder_fallback_name_days_x2=fallback, p3c_nv120_lt100_share_x2=gap_share)


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
    """r2.10 (a): one universe per process (a.uni); writes summary_<uni>_<stamp>.json + eval_<uni>_meta.json; --stage merge combines."""
    panel_recheck(auth, panel); repin(auth, "dep_fe_sha256", "data_etf_daily_adj_sha256")
    import research.g1g5_fund_resid_alpha as FE
    FIN = load_fin(panel); ext_out = {}; trim()
    FE.PC = panel; FE._RET.clear()  # all booking on the rebuilt panel
    FE.rets(range(2024, 2027)); trim()   # r2.10 (c): FE return cache loaded once at the lowest-memory point and kept for every book_ret (same key (2024, 2025, 2026), same data)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S"); s, e = X2S, X2E; ann = lambda r: float((1+r).prod()**(244/len(r))-1)
    summ = dict(leaf="sue_desens_cs", leaf_no=23, stamp=stamp, live=False, promotion_approved=False, sealed_read=False, auth=auth, res={},
                engine="FE.book_ret wb_SD0 (停牌/退市偏乐观, SD0) on cs_panel_v2_resumefix", cost="17.5bp one-sided × Σ|Δw|; 30bp disclosure",
                note_zh="X2 只是入场券；唯一晋级测试为 2026-11-02 起 FWD。Gate B/GATE_V3/衰减/ρ/Jaccard(叶15–22) 由钉 sha 的评价工具另算。",
                notes_arch_b997cba8_zh=[
                    "外部工具口径：leaf_selfcheck_v3.py 的 PANEL 仍写死读 v1 panel_cache（池成员与 IC 价格指数）；alpha_combo_marginal_v1_1 / leaf_selfcheck_common 的书收益来自原始复权价，不是 FE.book_ret。Gate B/GATE_V3/衰减/IC 与本脚本判定读数不是同一引擎、同一面板，与叶15–22 相同，可横向比较；以后另提 --panel-dir（新 sha、单独审）。",
                    "beta120 与动量 t−120→t−20 用面板全部行的 ret（t−1，PIT），重建后含复牌补回行收益，与 v1 面板下的叶15–22 不完全可比（规模需授权运行后才能报）。",
                    "补回行 hiliq=False：复牌日的已持仓股不在 α 名单里会被调出，blocked 入场闸门基本不触发（books.*.blocked_skips 计数）；SD0 下属乐观处理。",
                    "B4：当前记录先按最新 end_date 选（正式报表 niq 为 NaN 也参与），再算 ΔE/P，算不出即无 α；预告记录 niq 算不出的仍不算可用记录。旧写法会退回旧季度的名·日数见 build_*_meta.json。",
                    "B3（Arch 129d67c5 §3 执行口径）：只在面板无行且 mask 当日停牌时沿用上一状态和停牌前流通市值；ST/成交额不足/次新无行日记 False 并中断沿用；mask 无行（未上市/退市）记 False；自 2018 逐年递推。沿用名·日按 mask 原因计数（必须全为停牌）；旧写法（不沿用）与 r2.2 写法（无行即沿用）的 EW/wb 年化差只作披露，见 res.*.b3_pool_carry。",
                    "残差化（主 Agent 02:23 裁定，经 Alpha 预读 8586ffd0）：风格集改为 Alpha 冻结集——SW L1、logmv_{t−1}、beta120_{t−1}（对 510300）、动量 t−120→t−20（t−1 时点）、logADV20；替代预注册 §4 第 3 条的 mom20/mom60/vol20/当日 logADV20（预注册未改，按裁定执行并披露；本叶预注册未给 vol20 机制含义）。叶19/20 α 照旧。","capacity_adv 回归项（预注册 §1；Alpha 77441f16 §4）：取 capacity_adv HI_LIQ v1.1 腿目标权重（3b288c83…），按名滞后一个交易日（t−1；r2.3 为当日，Arch bd3abe5c §3.2 认定当日无前瞻，现按 Alpha 改为 t−1 与风格集统一，事先冻结、不看结果）；未持有记 0。暴露很稀疏（每日约 25 名非零，HI_LIQ 池约 800 名），近似「是否被 capacity_adv 持有」的哑变量，去敏力度弱；只进第一段 OLS，第二段（行业 + lmv1）不含，最终 α 对它不严格正交；判重以 Alpha CMC --base capadv 为准。",
                    "logADV20 口径（Alpha 77441f16 §3）：面板 adv20_yuan 由 research/ai_cs_panel_build.py 第 18/35 行直接拷贝 HI_LIQ mask；mask 的实际写入方 research/strategy_hiliq_universe_v1.py 第 130–141 行（Arch b09901f5 P3-1）在 t 日取 prior = sess[sess < S][-ADV_WIN:]，adv = 这 20 个交易日成交额均值，即 t 日值已是 t−20..t−1 均值、不含 t 日；所以 ladv1 直接取 t 日 adv20_yuan、不再 shift（r2.3 多滞后一天，已更正），与 Alpha 冻结 s8 一致。",
                    "风格 t−1 与 Alpha 冻结代码的差别（Arch P3-B）：beta120、动量按裁定原文「全部 t−1」与 Alpha s8 v1.1（research/alpha_hiliq_s8_paradigm_v1_1.py，455fdf82…）信号侧一致：beta 用收益 d−120..d−1，动量 C(d−21)/C(d−121)−1，liq = adv20[d]；旧 s8 af48bc05 以 t 为锚、差一日，只作历史对照。叶子不 import s8，无 s8 键。",
                    "CMC v1.1（Alpha 交接 ab6d1e82）：§8 / CMC 读数改用 research/alpha_combo_marginal_v1_1.py（r3 5658f612…，.ok 键 dep_combo_sha256，.cmd 必须带 --arch-ok；r3 已过 Arch 审 bbfcb7ef，selftest .ok fa45bf7f 已签，全量 .ok 未签）。旧版 alpha_combo_marginal.py（bee23019…，dep_combo_legacy_sha256）的结果只作对照披露列，不进判定、不计入家族次数。阈值不变。v1.1 首月行业用 2024-05-31 申万快照、START 当日跳过，与旧版的差异由 legacy 列披露。",
                    "面板缺口（Arch P3-C）：面板只有 fulla|hiliq 行和补回行，ST/成交额不足日无行；beta/动量按有效日滚动，缺口日对动量等于记 0 收益，与连续价格口径不同。build_*_meta.json 的 p3c_nv120_lt100_share_x2 报 X2 回归样本中「t−120..t−1 有效日 <100」的名·日占比。",
                    "退市（主 Agent 02:44 裁定，Arch 口径）：mask 是矩形网格，退市后恒为 suspended=True。基准池主口径按退市日截断：退市日之后记 S=False、市值链断开；最后交易日之后到退市日之间按 mask 停牌沿用，收益记 0、留在分母（预注册「停牌记 0、不剔分母」）。缺退市日的名在 X2 内即停跑、窗口外只披露，不回退到最后交易日。影子口径按最后交易日截断，只作披露，不进判定、不计入家族次数；受影响名数与名·日数以运行时 diag 为准（主口径 delisted_cut_name_days_x2 / delisted_cut_names_x2，影子 delisted_cut_name_days_x2_shadow_last_trade_date / delisted_cut_names_x2_shadow_last_trade_date）；静态参考（Alpha 486496a9）：delisted_master 63590f23 中 X2 窗内退市 93 名，其中 76 名最后交易日与退市日相差超过 1 天；两口径的 EW/wb 年化差由 pool_benchmarks 写入 res.*.b3_pool_carry（*_shadow_cut_last_trade_date）。delisted_master 只在 pool_benchmarks 内读取（data_delisted_sha256，读前 repin）。「mask 无行记 False」分支保留作防御。",
                    "B3 校验（Arch P3-A / b09901f5 P2-1）：沿用名·日按构造必然为 mask 停牌，not_suspended 恒为 0，只是自洽检查；独立校验靠 Mp≠carry 停跑和截断断言：X2 每一日 (S & gone) 必须全为 False（cut = 退市日），否则停跑报 Arch；cut 在窗口末之后、窗口末仍停牌被沿用的名属合法，只列入 carried_to_window_end_delisted_after_window（附 cut 日期）。b3 记 delisted_master sha、最大最后交易日与最大退市日（P3-3）。吸收合并持有人实得换股，两口径都按 0 收益，属已知局限。col 成员出现 .BJ 也停跑（P3-D；mask/FULLA 不含北交所，属已知设计边界，由 Data/主 Agent 跟踪）。",
                    ".ok 有效期（Arch P2-A）：expires_et 必填、带时区，authorize 与每个阶段开始（panel_recheck）各核一次，过期即拒。<out_dir>/tool_run_log.txt 由运行者写（Arch §5-1），脚本不生成。",
                    "B4 补充（Arch P3-6）：正式报表 niq 为 NaN 的唯一来源是上一期 ytd 缺失，此时同季预告的 niq 也算不出，所以不存在「正式报表盖掉可用预告」的情况。",
                    "行业帽 25% 的出处是 Arch 审核 0d9bd147 第 96 行（P1-3），并经主 Agent 01:52 认可；不是主 Agent 01:42 裁定。",
                    "密封窗已被叶20 读过，不是干净样本外；引擎 SD0，SD1 合入后是否重算由 Arch 另定。"])
    for uni in (a.uni,):   # r2.10 (a): one universe per process (loop body unchanged)
        col = FE.UCOL[uni]
        A = pd.concat([pd.read_parquet(out/f"alpha_{uni}_{y}.parquet", columns=["date", "instrument", "alpha", "ind", "src", "blk"]) for y in (2024, 2025, 2026) if (out/f"alpha_{uni}_{y}.parquet").exists()])
        G = pd.concat([pd.read_parquet(out/f"gate_{uni}_{y}.parquet") for y in (2024, 2025, 2026) if (out/f"gate_{uni}_{y}.parquet").exists()])
        for t in (A, G): t["date"] = pd.to_datetime(t.date)
        A, G = A[(A.date >= s) & (A.date <= e)], G[(G.date >= s) & (G.date <= e)]
        days = sorted(A.date.unique()); rd = set(days[::FE.REBAL])
        A_rd, G_rd = A[A.date.isin(rd)], G[G.date.isin(rd)]; trim()   # r2.10 (b): pick_book only reads rebalance-day rows (byd used only for d in rd)
        # panel for benchmarks/booking (eval only: may read is_resume_day/hiliq_carry for entry gate + disclosure)
        lo_px = pd.Timestamp("2024-05-20"); carry_col = "hiliq_carry" if uni == "HILIQ" else "fulla_carry"
        PX = pd.concat([pd.read_parquet(panel/f"cs_panel_{y}.parquet", columns=["date", "instrument", "ret", "close", "ind", "is_resume_day", carry_col],   # r2.10 (b): logmv/<col> were never used from PX
                                        filters=[("date", ">=", lo_px.to_pydatetime())]) for y in (2024, 2025, 2026)])
        PX["date"] = pd.to_datetime(PX.date); PX = PX[PX.date <= e]
        blocked = {d: set(g.instrument) for d, g in PX[PX.is_resume_day.fillna(False).astype(bool)].groupby("date")}
        rr = PX.pivot_table(index="date", columns="instrument", values="ret").sort_index()
        IXr = PX.pivot_table(index="date", columns="instrument", values="ind"); trim()   # r2.10 (c): N4 industry pivot taken here (same call), reindexed below
        # B3 (Arch P1-1, 129d67c5 §3): S carried only on mask-suspended no-row days, recursed from 2018; then T−1; ret at T; suspended → 0, kept
        repin(auth, "data_mask_sha256"); pb = pool_benchmarks(panel, PX, col, carry_col, rr, s, e); b3 = pb["diag"]
        if b3["carry_mismatch"] or b3["carried_by_mask_reason_x2"].get("not_suspended", 0) or b3["bj_member_rows"]:
            xtext(out/f"B3_carry_mismatch_{uni}.json", json.dumps(b3, ensure_ascii=False, indent=1, default=str))
            raise SystemExit(f"STOP (B3): Mp != {carry_col} on {b3['carry_mismatch']} restored resume rows / {b3['carried_by_mask_reason_x2'].get('not_suspended', 0)} carried non-suspended name-days / {b3['bj_member_rows']} .BJ member rows (P3-D) — report to Arch")
        U = pb["U"]; Mp, wv = pb["Mp"], pb["wv"]; r0 = pb["r0"]; del rr   # Alpha P3-2: reuse the single return frame; r2.8 P3-8: drop rr now (r0.index == rr.index)
        ewf = lambda M, W_, _r=r0: (((_r*M).sum(1)/M.sum(1)).loc[s:e], ((_r*W_).sum(1)/W_.sum(1)).loc[s:e])   # r2.8 P3-7
        ew, wb = ewf(Mp, wv); ew_o, wb_o = ewf(pb["Mpo"], pb["wvo"]); ew_2, wb_2 = ewf(pb["Mp2"], pb["wv2"])
        cmd_x2 = int((Mp & ~pb["Mpo"]).loc[s:e].to_numpy().sum())
        for k_ in ("Mpo", "wvo", "Mp2", "wv2"): del pb[k_]   # r2.10 (c): disclosure frames dropped once read
        trim()
        b3.update(carried_member_days_x2=cmd_x2,
                  poolEW_cagr244_old_nocarry=ann(ew_o), wb_cagr244_old_nocarry=ann(wb_o), poolEW_cagr244_r2_2_norowcarry=ann(ew_2), wb_cagr244_r2_2_norowcarry=ann(wb_2),
                  poolEW_cagr244_diff_vs_old=ann(ew) - ann(ew_o), wb_cagr244_diff_vs_old=ann(wb) - ann(wb_o),
                  poolEW_cagr244_diff_vs_r2_2=ann(ew) - ann(ew_2), wb_cagr244_diff_vs_r2_2=ann(wb) - ann(wb_2),
                  note="old / r2.2 / shadow constructions: disclosure only (shadow diffs come from pool_benchmarks diag)")
        # N4 (prereg P2-4): factor-applicability exclusions (financials + 600519/002371) — daily count in pool and their share of pool wb weight
        IX = IXr.reindex(index=r0.index, columns=U); del IXr
        IX.iloc[0] = IX.iloc[0].fillna(pb["seed_ind"]); IX = IX.ffill()
        X = IX.isin(list(FIN)) | pd.DataFrame(np.broadcast_to(U.isin(list(FE.EXCL)), IX.shape), index=IX.index, columns=U)
        n_ex = (Mp & X).sum(1).loc[s:e]; sh_ex = ((wv*X).sum(1)/wv.sum(1)).loc[s:e]
        excl = dict(excluded_names_daily_median=float(n_ex.median()), excluded_wb_weight_share_median=float(sh_ex.median()),
                    excluded_wb_weight_share_mean=float(sh_ex.mean()), definition="SW L1 银行/非银金融 + 600519.SH/002371.SZ, pool members at T−1 (B3 state), weight = T−1 float mcap")
        del Mp, wv, r0, pb, IX, X; trim()   # r2.10 (c): freed before the next allocation (was after the return-cache read)
        repin(auth, "data_etf_daily_adj_sha256"); bal = FE.rets(range(2024, 2027))[0][FE.BAL].loc[s:e].astype(float)

        def vs(r, b):
            b = b.reindex(r.index).fillna(0); x = r - b; be = float(np.cov(r, b)[0, 1]/b.var()); res = r - be*b
            return dict(excess_ann244=float(x.mean()*244), t_hac=hac_t(x), t_naive=float(x.mean()/x.std()*np.sqrt(len(x))), beta=be,
                        resid_alpha244=float(res.mean()*244), resid_t_hac=hac_t(res), by_year={str(k): float(v.mean()*244) for k, v in x.groupby(x.index.year)})
        bench = dict(poolEW_cagr244=ann(ew), wb_cagr244=ann(wb), bal_cagr244=ann(bal))
        books, cap_ind = {}, (TIER_IND_CAP if uni == "HILIQ" else FE.IND_CAP[uni])
        specs = {"top6_60w": (6, TIER_W, cap_ind), "top10_100w": (10, TIER_W, cap_ind), "top20_disclosure": (DISC_N, DISC_W, FE.IND_CAP[uni]),
                 "top6_60w_cap20_disclosure": (6, TIER_W, CORE_IND_CAP), "top10_100w_cap20_disclosure": (10, TIER_W, CORE_IND_CAP)}
        for nm, (N, w, icap) in specs.items():
            W = pick_book(A_rd, G_rd, rd, days, N, w, icap, blocked)   # r2.10 (b): rebalance-day rows only (identical picks)
            xparquet(W, out/f"eval_weights_{uni}_{nm}_x2_{stamp}.parquet")
            r, to = FE.book_ret(W, s, e); _c = FE.COST; FE.COST = 0.003; r30, _ = FE.book_ret(W, s, e); FE.COST = _c
            nav = (1+r).cumprod(); H = W[W.instrument != FE.BAL].merge(PX[["date", "instrument", "is_resume_day", carry_col, "close"]], on=["date", "instrument"], how="left")
            H = H.merge(A[["date", "instrument", "src", "blk"]], on=["date", "instrument"], how="left")
            b = dict(cagr244=ann(r), cagr252=float(nav.iloc[-1]**(252/len(r))-1), mdd=float((nav/nav.cummax()-1).min()), turnover_1s=to,
                     cagr244_30bp=ann(r30), vs_wb=vs(r, wb), vs_poolEW=vs(r, ew), vs_510300=vs(r, bal),
                     held_name_days=int(len(H)), held_resume_rows=int(H.is_resume_day.fillna(False).astype(bool).sum()),
                     held_resume_rows_carry=int(H[carry_col].fillna(False).astype(bool).sum()),
                     held_in_fc_blackout=int((H.blk == 1).sum()), held_in_fc_blackout_ratio=float((H.blk == 1).mean()) if len(H) else None,
                     blocked_skips=int(W.attrs.get("blocked_skips", 0)))
            if N < 20:  # P2-6 lot rounding disclosure at the tier's capital (rebalance days, raw close)
                cap = TIERS[N]; Hr = H[H.date.isin(rd)].dropna(subset=["close"])
                fill = (np.floor(cap*Hr.target_weight/(Hr.close*100))*100*Hr.close).groupby(Hr.date).sum()/(cap*Hr.groupby("date").target_weight.sum())
                b["lot_fill_ratio_mean"] = float(fill.mean()); b["lot_cash_drag_mean"] = float(1 - fill.mean())
            books[nm] = b; trim()
            if uni == "HILIQ" and nm in ("top6_60w", "top10_100w"):
                tag = f"sue_desens_cs_{nm}" + ("" if is_primary(a) else f"_{variant_tag(a)}")
                xparquet(W, R/f"output/ai_factory/g1g5_{tag}_daily_weights_{stamp}.parquet")
                xtext(R/f"output/ai_factory/g1g5_{tag}_run_meta_{stamp}.json", json.dumps(dict(mechanism_tag="g1g5_ashare_sue_desens_cs_v1", universe=uni,
                    tier=nm, variant=variant_tag(a), live=False, promotion_approved=False, stamp=stamp, window="x2",
                    script_sha256=auth["script_sha256"], arch_ok_sha256=auth["arch_ok_sha256"]), ensure_ascii=False))
                for f_ in (f"g1g5_{tag}_daily_weights_{stamp}.parquet", f"g1g5_{tag}_run_meta_{stamp}.json"): ext_out[f_] = sha(R/"output/ai_factory"/f_)
        # ① capadv-HI_LIQ single-leg book-smoke: as filed (Strategy nav) and recomputed on this panel (decision uses recomputed)
        capadv = {}
        repin(auth, "dep_capadv600_tw_sha256", "dep_capadv600_nav_sha256", "dep_capadv1000_tw_sha256", "dep_capadv1000_nav_sha256")
        for N, d_ in CAPADV.items():
            nv = pd.read_csv(d_/"nav.csv", index_col=0, parse_dates=True).nav; rf = nv.pct_change().dropna().loc[s:e]
            tw = pd.read_parquet(d_/"target_weights.parquet").rename(columns={"session": "date", "weight": "target_weight"})
            tw["instrument"] = tw.instrument_id.str.split(".").map(lambda x: f"{x[1]}.{x[0].upper()}"); tw["date"] = pd.to_datetime(tw.date.astype(str).str[:10])
            rc, _ = FE.book_ret(tw[tw.target_weight > 0][["date", "instrument", "target_weight"]], s, e)
            capadv[N] = dict(filed_cagr244=ann(rf), recomputed_cagr244=ann(rc), recomputed_mdd=float(((1+rc).cumprod()/(1+rc).cumprod().cummax()-1).min()))
        # §6.7 quantile monotonicity (disclosure)
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
                gx[q], _ = FE.book_ret(pd.concat(full), s, e); del Wq, gq, full; trim()
            exc = {q: float((r - ew.reindex(r.index).fillna(0)).mean()*244) for q, r in gx.items()}
            ls = (gx[k-1] - gx[0]).dropna()
            qres[f"q{k}"] = dict(excess_vs_poolEW_ann244=exc, spearman=float(pd.Series(exc).rank().corr(pd.Series(range(k), dtype=float))),
                                 long_short_ann244=float(ls.mean()*244), long_short_t_hac_lag19=hac_t(ls))
        q5 = qres["q5"]["excess_vs_poolEW_ann244"]
        mono = bool(q5[4] > q5[2] and books["top6_60w"]["vs_poolEW"]["excess_ann244"] >= books["top20_disclosure"]["vs_poolEW"]["excess_ann244"] >= 0)
        # P2-5 overlap with leaf 20 on this panel (ρ_excess de-β vs pool EW; Jaccard top-6/10/20)
        ov = {}
        if L20_W[uni].exists():
            repin(auth, f"dep_l20w_{uni.lower()}_sha256", f"dep_l20_{uni.lower()}_sha256")
            W20 = pd.read_parquet(L20_W[uni]); W20["date"] = pd.to_datetime(W20.date); W20 = W20[W20.target_weight > 0]
            r20, _ = FE.book_ret(W20, s, e)
            A20 = pd.read_parquet(L20[uni], columns=["date", "instrument", "alpha"], filters=[("date", ">=", W20.date.min().to_pydatetime())]); A20["date"] = pd.to_datetime(A20.date)   # r2.10 (b): only rows the W20 merge can match
            W20s = W20[W20.instrument != FE.BAL].merge(A20, on=["date", "instrument"], how="left")
            for nm, N in (("top6_60w", 6), ("top10_100w", 10), ("top20_disclosure", 20)):
                Wm = pd.read_parquet(out/f"eval_weights_{uni}_{nm}_x2_{stamp}.parquet"); Wm = Wm[Wm.instrument != FE.BAL]
                js = []
                for d in sorted(rd):
                    a_ = set(Wm[Wm.date == d].instrument); b_ = set(W20s[W20s.date == d].sort_values("alpha", ascending=False).instrument.head(N))
                    if a_ | b_: js.append(len(a_ & b_)/len(a_ | b_))
                ov[f"jaccard_median_{nm}"] = float(np.median(js)) if js else None
            del A20, W20s; trim()
            rt, _ = FE.book_ret(pd.read_parquet(out/f"eval_weights_{uni}_top20_disclosure_x2_{stamp}.parquet").assign(date=lambda x: pd.to_datetime(x.date)), s, e)
            b_ = ew.reindex(rt.index).fillna(0); x1 = rt - np.cov(rt, b_)[0, 1]/b_.var()*b_; b2 = ew.reindex(r20.index).fillna(0); x2 = r20 - np.cov(r20, b2)[0, 1]/b2.var()*b2
            ov["rho_excess_vs_leaf20"] = float(pd.concat([x1, x2], axis=1).dropna().corr().iloc[0, 1])
            ov["duplicate_of_leaf20"] = bool(ov["rho_excess_vs_leaf20"] > 0.5 or (ov.get("jaccard_median_top20_disclosure") or 0) >= 0.5)
        cov = pd.read_parquet(out/f"coverage_{uni}.parquet"); cov["date"] = pd.to_datetime(cov.date); cr = cov[cov.date.isin(rd)].n
        fc_early = int(((A.src == "forecast") & (A.date <= "2024-08-31")).groupby(A.instrument).any().sum())
        res = dict(variant=variant_tag(a), coverage_rebal_median=float(cr.median()), coverage_rebal_p10=float(cr.quantile(.1)), n_days=len(days),
                   benchmarks=bench, b3_pool_carry=b3, factor_exclusions_N4=excl, capadv_hiliq=capadv, books=books, quantiles=qres, monotone=mono, overlap_leaf20=ov,
                   forecast_branch_names_2024_06_08=fc_early, intel_jaccard="N/A: Intel event product not frozen/pinned")
        if uni == "HILIQ":  # §9 decisive read (only meaningful for the primary variant)
            t6, t10 = books["top6_60w"], books["top10_100w"]
            floor = t6["cagr244"] > bench["wb_cagr244"] and t10["cagr244"] > bench["wb_cagr244"]
            tpass = (t6["vs_wb"]["t_hac"] or 0) >= T_DECISIVE and (t10["vs_wb"]["t_hac"] or 0) >= T_DECISIVE
            beat_cap = t6["cagr244"] > capadv[6]["recomputed_cagr244"] and t10["cagr244"] > capadv[10]["recomputed_cagr244"]
            beat_ew = t6["vs_poolEW"]["excess_ann244"] > 0 and t10["vs_poolEW"]["excess_ann244"] > 0
            res["decisive"] = dict(is_decisive_spec=is_primary(a), wb_floor_pass=floor, t_hac_ge_2_50=tpass, beats_capadv_hiliq_recomputed=beat_cap,
                                   beats_poolEW=beat_ew, report_to_leo_allowed=bool(floor and beat_ew),
                                   verdict_cap=("FAIL" if not floor else ("WATCH" if not tpass else "PENDING_EXTERNAL_GATES")),
                                   note="非判定规格一律「未做多重检验校正，仅披露」" if not is_primary(a) else "判定规格；Gate B/GATE_V3/衰减另由钉 sha 工具出")
        summ["res"][uni] = res
        del A, G, A_rd, G_rd, PX; FE._RET.clear(); trim(); print(uni, "eval done", f"rss={rss():.0f}", flush=True); peak_check(f"eval {uni}")
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
    ap = argparse.ArgumentParser(description="Leaf23 sue_desens_cs r2.2 (requires Arch .ok)")
    ap.add_argument("--stage", required=True, choices=["fund", "build", "eval", "merge"])
    ap.add_argument("--uni", choices=["HILIQ", "FULLA"])
    ap.add_argument("--panel-dir", required=True, help="output/ai_factory/panel_cache_v2_resumefix (rebuilt); panel_cache / panel_cache_v2_fixesnone refused")
    ap.add_argument("--arch-ok", required=True, help="Arch run-auth .ok (quantlab_run_auth_v1) pinning script/prereg/panel-manifest/tool sha")
    ap.add_argument("--signal", default="dep", choices=["dep", "sue"], help="dep = ΔE/P rank (primary); sue = σ-scaled SUE (sensitivity)")
    ap.add_argument("--denom", default="fixed", choices=["fixed", "daily"], help="fixed = MV on session before record eff (primary); daily = MV_{t−1}")
    ap.add_argument("--no-forecast", action="store_true", help="S_F: formal reports only (§6.5a)")
    ap.add_argument("--blackout", type=int, default=20, choices=[20, 40], help="forecast-information blackout sessions (20 = primary)")
    ap.add_argument("--sealed", action="store_true")
    a = ap.parse_args()
    if a.sealed: raise SystemExit("sealed window not implemented here (prereg r2 §6.5a: S_F only, once, after all X2 hard gates pass, separate .ok)")
    if a.stage in ("build", "eval") and not a.uni: raise SystemExit(f"--uni required for {a.stage} (r2.10: eval runs one universe per process)")
    if a.stage in ("fund", "merge") and a.uni: raise SystemExit(f"--uni not accepted for {a.stage}")
    if a.signal == "sue" and a.denom == "daily": raise SystemExit("--denom applies to ΔE/P only")
    panel, auth = authorize(a); out = out_dir(a)
    # N6: serial order fund > build HILIQ > build FULLA > eval HILIQ > eval FULLA > merge; first stage needs an empty out_dir; later stages chain-verify upstream metas
    if a.stage == "fund":
        if out.exists() and any(out.iterdir()): raise SystemExit(f"refused: out_dir {out} is not empty (N6: no silent overwrite; Arch decides on cleanup)")
        up = {} if is_primary(a) else verify_primary_eval(auth)   # P2-2: sensitivities only after the primary eval chain
        out.mkdir(parents=True, exist_ok=True)
    else:
        if not out.is_dir(): raise SystemExit(f"refused: out_dir {out} missing (run fund first)")
        need = {"build": ["fund"] + (["build_HILIQ"] if a.uni == "FULLA" else []),
                "eval": ["fund", "build_HILIQ", "build_FULLA"] + (["eval_HILIQ"] if a.uni == "FULLA" else []),   # r2.10 (a): FULLA after HILIQ
                "merge": ["eval_HILIQ", "eval_FULLA"]}[a.stage]
        up = verify_upstream(out, auth, need)
        guard_fresh(out, {"build": [f"alpha_{a.uni}_*", f"gate_{a.uni}_*", f"coverage_{a.uni}.parquet", f"build_{a.uni}_meta.json"],
                          "eval": [f"summary_{a.uni}_*.json", f"eval_weights_{a.uni}_*", f"eval_{a.uni}_meta.json", f"B3_carry_mismatch_{a.uni}.json"],
                          "merge": ["summary_2*.json", "eval_meta.json"]}[a.stage])
    {"fund": lambda: fund(a, panel, out, auth, up), "build": lambda: build(a, panel, out, auth, up), "eval": lambda: evaluate(a, panel, out, auth, up),
     "merge": lambda: merge(a, panel, out, auth, up)}[a.stage]()
