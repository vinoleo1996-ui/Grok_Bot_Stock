#!/usr/bin/env python3
"""Process-tree RSS wrapper for Eng gated runs (SD1 selftest, SD0 parity). stdlib only; imports nothing from quantlab.

r3.2: fixes the ad-hoc copies used for SD1 selftest r3.1a and SD0 parity r3.1a into one reviewed script
(Arch ARCH_SD1_R3_1A_RECEIPT_REVIEW_ZH.md d023f517 P3-R1 / P3-R2).

  python3 -B scripts_eng/rss_wrap.py --out-dir DIR [--cap-mb 1536] [--interval 0.1] -- CMD [ARG ...]

* runs CMD once (cwd unchanged, environment inherited unchanged); its stdout+stderr go to DIR/run.log;
* every ``--interval`` s (default 0.1) walks the whole process tree (root + all descendants via /proc PPid) and reads
  VmRSS / VmHWM of each pid; if the SUMMED tree VmRSS exceeds ``--cap-mb`` (default 1536, max 1536) the whole tree is
  SIGKILLed and the status is FAIL_RSS;
* after exit records getrusage(RUSAGE_CHILDREN).ru_maxrss (covers short-lived grandchildren the sampler missed);
* records the relevant environment (ENV_KEYS only; values of other variables, tokens and keys are never read out),
  the wrapper's own os.nice(0), and the nice value of each pid when first seen (a child that calls os.nice later is
  seen at its start value; see the runner's own report for that);
* writes DIR/tmp_before.txt before and DIR/tmp_after.txt after the run (listing of /tmp top level: name, type, size,
  mtime_ns) plus DIR/tmp_diff.json (added / removed / changed names) - P3-R1.
DIR must not exist (created with exist_ok=False); every file is written with open(..., "x"). Exit code = CMD's exit code
(or 1 if killed). live=false.
"""
from __future__ import annotations
import argparse, datetime, json, os, platform, resource, signal, subprocess, sys, time
from pathlib import Path

CAP_MAX_MB = 1536
ENV_KEYS = ("PYTHONDONTWRITEBYTECODE", "PYTHONPATH", "PYTHONHASHSEED", "PYTHONOPTIMIZE", "PYTHONSAFEPATH",
            "QL_SD1_REAL_DATA", "PATH", "VIRTUAL_ENV", "TZ", "LANG", "LC_ALL", "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "PWD")


def _children_map() -> dict:
    m = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open(f"/proc/{d}/stat") as f:
                    s = f.read()
                ppid = int(s[s.rfind(")") + 2:].split()[1])
                m.setdefault(ppid, []).append(int(d))
            except (OSError, ValueError, IndexError):
                pass
    return m


def _tree(root: int) -> list:
    m, out, st = _children_map(), [], [root]
    while st:
        p = st.pop(); out.append(p); st.extend(m.get(p, []))
    return out


def _vm(pid: int):
    rss = hwm = None
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1]) / 1024
                elif line.startswith("VmHWM:"):
                    hwm = int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        pass
    return rss, hwm


def _nice_of(pid: int):
    try:
        with open(f"/proc/{pid}/stat") as f:
            s = f.read()
        return int(s[s.rfind(")") + 2:].split()[16])
    except (OSError, ValueError, IndexError):
        return None


def _tmp_listing() -> dict:
    out = {}
    for e in sorted(os.scandir("/tmp"), key=lambda e: e.name):
        try:
            st = e.stat(follow_symlinks=False)
            kind = "l" if e.is_symlink() else ("d" if e.is_dir(follow_symlinks=False) else "f")
            out[e.name] = [kind, st.st_size, st.st_mtime_ns]
        except OSError:
            out[e.name] = ["?", None, None]
    return out


def _xwrite(path: Path, text: str):
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(text)


def _write_listing(path: Path, lst: dict):
    _xwrite(path, "".join(f"{k}\t{v[0]}\t{v[1]}\t{v[2]}\n" for k, v in lst.items()))


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        raise SystemExit("usage: rss_wrap.py --out-dir DIR [--cap-mb N] [--interval S] -- CMD [ARG ...]")
    i = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--cap-mb", type=int, default=CAP_MAX_MB)
    ap.add_argument("--interval", type=float, default=0.1)
    a = ap.parse_args(argv[:i])
    cmd = argv[i + 1:]
    if not cmd:
        raise SystemExit("rss_wrap: empty command")
    if not (0 < a.cap_mb <= CAP_MAX_MB):
        raise SystemExit(f"rss_wrap: --cap-mb must be in (0, {CAP_MAX_MB}]")
    if not (0 < a.interval <= 0.1):
        raise SystemExit("rss_wrap: --interval must be in (0, 0.1]")
    out = Path(a.out_dir)
    out.mkdir(parents=False, exist_ok=False)
    env_rec = {k: os.environ.get(k) for k in ENV_KEYS}
    wrap_nice = os.nice(0)
    tmp_before = _tmp_listing(); _write_listing(out / "tmp_before.txt", tmp_before)
    t0 = datetime.datetime.now().astimezone()
    peak_sum = peak_hwm = 0.0; nsamp = maxpids = 0; killed = False; seen = set(); nices = {}
    with open(out / "run.log", "x", encoding="utf-8") as fh:
        p = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)
        while p.poll() is None:
            pids = _tree(p.pid); seen.update(pids); s = 0.0
            for q in pids:
                r, h = _vm(q)
                if r:
                    s += r
                if h:
                    peak_hwm = max(peak_hwm, h)
                if q not in nices:
                    n = _nice_of(q)
                    if n is not None:
                        nices[q] = n
            peak_sum = max(peak_sum, s); nsamp += 1; maxpids = max(maxpids, len(pids))
            if s > a.cap_mb:
                for q in reversed(pids):
                    try:
                        os.kill(q, signal.SIGKILL)
                    except OSError:
                        pass
                killed = True; p.wait(); break
            time.sleep(a.interval)
    t1 = datetime.datetime.now().astimezone()
    ru_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
    tmp_after = _tmp_listing(); _write_listing(out / "tmp_after.txt", tmp_after)
    tmp_diff = dict(added=sorted(set(tmp_after) - set(tmp_before)), removed=sorted(set(tmp_before) - set(tmp_after)),
                    changed=sorted(k for k in set(tmp_before) & set(tmp_after) if tmp_before[k] != tmp_after[k]))
    _xwrite(out / "tmp_diff.json", json.dumps(tmp_diff, indent=1))
    over = killed or ru_mb > a.cap_mb
    rep = dict(script="scripts_eng/rss_wrap.py", cmd=cmd, cwd=os.getcwd(), python=platform.python_version(),
               env=env_rec, wrapper_os_nice0=wrap_nice,
               tree_nice_by_pid_first_seen={str(k): v for k, v in sorted(nices.items())},
               started_et=t0.isoformat(timespec="seconds"), finished_et=t1.isoformat(timespec="seconds"),
               elapsed_s=round((t1 - t0).total_seconds(), 2), exit=p.returncode, cap_mb=a.cap_mb,
               interval_s=a.interval, samples=nsamp, max_tree_pids=maxpids, distinct_pids_seen=len(seen),
               peak_tree_vmrss_sum_mb=round(peak_sum, 1), peak_vmhwm_any_pid_mb=round(peak_hwm, 1),
               rusage_children_maxrss_mb=round(ru_mb, 1), killed_over_cap=killed,
               status=("FAIL_RSS" if over else ("OK" if p.returncode == 0 else "EXIT_NONZERO")),
               tmp_added=tmp_diff["added"], tmp_removed=tmp_diff["removed"], tmp_changed=tmp_diff["changed"],
               note="tree VmRSS sampled every interval; grandchildren shorter than one interval are covered only by "
                    "rusage_children_maxrss_mb (largest single reaped descendant).")
    _xwrite(out / "rss.json", json.dumps(rep, indent=1, ensure_ascii=False))
    print(json.dumps(dict(status=rep["status"], exit=rep["exit"], peak_tree_vmrss_sum_mb=rep["peak_tree_vmrss_sum_mb"],
                          peak_vmhwm_any_pid_mb=rep["peak_vmhwm_any_pid_mb"], out_dir=str(out))))
    return 1 if killed else (p.returncode if p.returncode is not None else 1)


if __name__ == "__main__":
    raise SystemExit(main())
