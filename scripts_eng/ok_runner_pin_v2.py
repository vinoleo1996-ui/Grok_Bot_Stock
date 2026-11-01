#!/usr/bin/env python3
"""Runner gate v2 against Arch .ok markers — DRAFT FOR ARCH REVIEW (Eng, 2026-10-18). NOT in use: ok_runner_pin.py
(c7805d9a78e4f5478fa4c9e3becda48e76453ee0889b4f7027009a676c3e2485) stays the gate until Arch reviews this file.
Read-only; never creates or edits a .ok. Self-contained (does not import ok_runner_pin).

Everything ok_runner_pin c7805d9a enforces, unchanged in meaning:
  1. every listed .ok exists and is readable;   2. live=false and promotion=false in every listed .ok;
  3. pins / deps are exactly 64 lowercase hex;   4. no duplicate key with different values;
  5. some listed .ok pins this script (runner_sha256_<stem> or runner_sha256[<rel path|name>]) and every pin matches;
  6. each requested mode has allow_<mode>=true in every pinning .ok and is not allow_<mode>=false in any listed .ok;
  7. each dep declared by the runner is pinned (dep_sha256_<key>) in every pinning .ok and matches the file now.
Added in v2 (docs/v2/ARCH_RUN_AUTH_SELFTEST_SPEC_ZH.md 1aa43bdd §2/§3/§9). r3 (Arch r2 review 73cb88ac P2-V1): checks 8–15
apply ONLY to the "strict" .ok set = the designated ``primary_ok`` when given (it must pin this script), else every .ok
that pins this script. Every other listed .ok (frozen .oks without expires_et, co-listed .oks of multi-.ok runners)
gets exactly the v1 c7805d9a semantics (1, 2, 4, 6-not-false), parsed like v1 (CR tolerated).
  8. encoding: refuse a UTF-8 BOM, any CR (LF only), non-UTF-8 bytes, and inline comments (a value containing '#');
  9. format must be in ALLOWED_FORMATS (allowlist, currently {'quantlab_run_auth_v1'}) and signed_by=arch;
     ok_revision is optional; when present it must be a positive integer ('3') or r<N> ('r3'), N>=1, else refuse;
 10. signed_et present, ISO8601 with an explicit UTC offset, not in the future (5 min skew); expires_et REQUIRED in
     every strict-set .ok for every mode/scope (r2; r3: strict set only), same format, and not yet passed;
 11. scope: when ``scope`` is passed, the .ok scope must equal it; mode 'selftest' implies scope=selftest;
 12. allow_*: every allow_<x> written in the .ok that is not a requested mode must be exactly 'false'; every name in
     ``known_allow`` (the runner's vocabulary) must be written explicitly;
 13. allow_real_data (r3, Arch P2-V2: only when the scope is selftest): must be written and equal 'false' unless
     'real_data' is a requested mode (then 'true' via 6);
 14. out_dir (required when 'selftest' is requested; checked whenever present): 'mkdtemp' or /tmp/<tag>; never under
     output/ or inside the repo. The gate only validates; the caller creates it (mkdtemp / mkdir(exist_ok=False)).
 15. selftest scope (requested scope 'selftest', mode 'selftest', or scope=selftest written in the .ok): the .ok must
     carry gate_ok_runner_pin_sha256=<64 hex> equal to the full sha256 of THIS gate file, computed at call time from
     __file__ (so a selftest .ok binds the exact gate that checks it).
r2 (Eng, 2026-10-18 ~02:1x ET, Arch P3): items 9 (allowlist + ok_revision), 10 (expires_et always required), 15.
r3 (Eng, 2026-10-18 ~02:4x ET): P2-V1 strict set (above); P2-V2 (13 only for scope=selftest); P3-8: in the strict set a
requested mode needs allow_<mode> exactly 'true' (as false must be exactly 'false'), ANY duplicate key is refused
(spec §3), and ``scope`` must be written even when the runner passes none.
There is deliberately no bypass flag, argv switch or environment variable.
"""
from __future__ import annotations
import datetime as _dt
import hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ISO_TZ = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?[+-]\d{2}:\d{2}$")
TMP_TAG = re.compile(r"^/tmp/[A-Za-z0-9._-]+$")
OK_REVISION = re.compile(r"^(r?)[1-9][0-9]*$")
ALLOWED_FORMATS = frozenset({"quantlab_run_auth_v1"})
VERSION = "ok_runner_pin_v2-draft-r3-20261018"


def sha256_file(p: str | Path) -> str:
    h = hashlib.sha256()
    with open(Path(p).resolve(), "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _refuse(msg: str):
    raise SystemExit(f"REFUSED (ok_runner_pin_v2): {msg}")


def parse_ok(path: Path) -> dict:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        _refuse(f"{path}: UTF-8 BOM not allowed")
    if b"\r" in raw:
        _refuse(f"{path}: CR found (LF line endings only)")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        _refuse(f"{path}: not UTF-8 ({e})")
    kv: dict[str, str] = {}
    for line in text.split("\n"):
        t = line.strip()
        if not t or t.startswith("#") or "=" not in t:
            continue
        k, v = t.split("=", 1); k = k.strip(); v = v.strip()
        if "#" in v:
            _refuse(f"{path}: inline comment in value of {k!r} (put comments on their own '#' line)")
        if k in kv:
            _refuse(f"{path}: duplicate key {k!r} (spec §3: keys must be unique)")
        kv[k] = v
    return kv


def parse_ok_v1(path: Path) -> dict:
    """v1 c7805d9a parsing for non-strict .oks: utf-8 text, splitlines, '#' lines skipped, duplicate key with a
    different value refused."""
    kv: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1); k = k.strip(); v = v.strip()
        if k in kv and kv[k] != v:
            _refuse(f"{path}: duplicate key {k!r} with different values")
        kv[k] = v
    return kv


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p.resolve())


def _pins(kv: dict, script: Path) -> list[tuple[str, str]]:
    out = []
    for k, v in kv.items():
        hit = (k == f"runner_sha256_{script.stem}")
        m = re.fullmatch(r"runner_sha256\[([^\]]+)\]", k)
        if m and m.group(1).strip() in (_rel(script), script.name):
            hit = True
        if hit:
            out.append((k, v))
    return out


def _is_false(v) -> bool:
    return v is not None and v.strip().lower() == "false"


def _ts(o: Path, k: str, v: str | None, required: bool):
    if v is None:
        if required:
            _refuse(f"{o}: {k} is required")
        return None
    if not ISO_TZ.match(v):
        _refuse(f"{o}: {k}={v!r} is not ISO8601 with an explicit UTC offset (e.g. 2026-10-18T02:10:00-04:00)")
    return _dt.datetime.fromisoformat(v)


def check_out_dir(o: Path, v: str | None, required: bool) -> str | None:
    if v is None:
        if required:
            _refuse(f"{o}: out_dir is required (mkdtemp or /tmp/<tag>)")
        return None
    if v == "mkdtemp":
        return v
    if not TMP_TAG.match(v):
        _refuse(f"{o}: out_dir={v!r} must be 'mkdtemp' or /tmp/<tag>")
    r = Path(v).resolve(strict=False)
    if r == ROOT or ROOT in r.parents or "output" in r.parts:
        _refuse(f"{o}: out_dir {r} is inside the repo / output/")
    return v


def _strict_checks(o: Path, kv: dict, modes: list, want_scope, known_allow, now, gate_path: Path, gate_sha: str):
    """Checks 8–15 (8 = strict parse, done by the caller) on one strict-set .ok."""
    selftest = "selftest" in modes
    if kv.get("format") not in ALLOWED_FORMATS:
        _refuse(f"{o}: format must be one of {sorted(ALLOWED_FORMATS)} (got {kv.get('format')!r})")
    if "ok_revision" in kv and not OK_REVISION.fullmatch(kv["ok_revision"]):
        _refuse(f"{o}: ok_revision={kv['ok_revision']!r} must be a positive integer or r<N> (N>=1)")
    if kv.get("signed_by") != "arch":
        _refuse(f"{o}: signed_by must be arch (got {kv.get('signed_by')!r})")
    signed = _ts(o, "signed_et", kv.get("signed_et"), True)
    if signed > now + _dt.timedelta(minutes=5):
        _refuse(f"{o}: signed_et {kv['signed_et']} is in the future")
    exp = _ts(o, "expires_et", kv.get("expires_et"), True)
    if exp <= now:
        _refuse(f"{o}: expired at {kv['expires_et']}")
    if not kv.get("scope"):
        _refuse(f"{o}: scope must be written")
    if want_scope is not None and kv.get("scope") != want_scope:
        _refuse(f"{o}: scope must be {want_scope!r} (got {kv.get('scope')!r})")
    for k, v in kv.items():
        if k.startswith("allow_") and k[len("allow_"):] not in modes and v != "false":
            _refuse(f"{o}: {k}={v!r}; every allow_* that is not a requested mode must be exactly 'false'")
    for m in known_allow:
        if f"allow_{m}" not in kv:
            _refuse(f"{o}: allow_{m} must be written explicitly (true or false)")
    st_scope = want_scope == "selftest" or kv.get("scope") == "selftest"
    if st_scope and "real_data" not in modes and kv.get("allow_real_data") != "false":   # P2-V2: selftest scope only
        _refuse(f"{o}: allow_real_data must be written as false for a selftest that does not request real_data")
    check_out_dir(o, kv.get("out_dir"), selftest)
    if st_scope:
        g = kv.get("gate_ok_runner_pin_sha256")
        if g is None:
            _refuse(f"{o}: selftest scope requires gate_ok_runner_pin_sha256=<64 hex of {_rel(gate_path)}>")
        if not HEX64.fullmatch(g):
            _refuse(f"{o}: gate_ok_runner_pin_sha256 must be full 64-hex lowercase (got {g!r})")
        if g != gate_sha:
            _refuse(f"{o}: gate_ok_runner_pin_sha256={g} != running gate {_rel(gate_path)} sha256={gate_sha}")
    for m in modes:                                   # P3-8: symmetric with 'false'
        if kv.get(f"allow_{m}") != "true":
            _refuse(f"{o}: mode {m!r} needs allow_{m}=true exactly (got {kv.get(f'allow_{m}')!r})")


def enforce(script: str | Path, ok_paths, modes=(), deps: dict | None = None, *, scope: str | None = None,
            known_allow=(), primary_ok: str | Path | None = None, now: _dt.datetime | None = None) -> dict:
    script = Path(script).resolve(); sha = sha256_file(script)
    modes = list(modes)
    now = now or _dt.datetime.now().astimezone()
    gate_path = Path(__file__).resolve(); gate_sha = sha256_file(gate_path)
    selftest = "selftest" in modes
    want_scope = scope or ("selftest" if selftest else None)
    oks = [Path(o) for o in ok_paths if o]
    if not oks:
        _refuse(f"{script.name}: no .ok listed")
    parsed = {}
    for o in oks:                                    # v1 semantics for EVERY listed .ok (1, 2, 4, 6-not-false)
        if not o.exists():
            _refuse(f"{script.name}: listed .ok missing: {o}")
        try:
            kv = parse_ok_v1(o)
        except SystemExit:
            raise
        except Exception as e:  # unreadable
            _refuse(f"{o}: unreadable ({e!r})")
        for flag in ("live", "promotion"):
            if not _is_false(kv.get(flag)):
                _refuse(f"{o}: requires {flag}=false (found {kv.get(flag)!r})")
        for m in modes:
            if _is_false(kv.get(f"allow_{m}")):
                _refuse(f"{o}: allow_{m}=false")
        parsed[o] = kv
    pinning = {}
    for o, kv in parsed.items():                     # 3, 5
        for k, v in _pins(kv, script):
            if not HEX64.fullmatch(v):
                _refuse(f"{o}: {k} must be a full 64-hex lowercase sha256 (got {v!r})")
            if v != sha:
                _refuse(f"{script.name} sha256={sha} != pinned {v} ({k} in {o})")
            pinning[o] = v
    if not pinning:
        _refuse(f"{script.name} sha256={sha} not pinned in any of {[str(o) for o in oks]}; "
                f"Arch must add runner_sha256_{script.stem}=<64 hex>")
    if primary_ok is not None:                       # P2-V1: strict set
        prim = Path(primary_ok)
        match = [o for o in pinning if o.resolve() == prim.resolve()]
        if not match:
            _refuse(f"primary_ok {prim} is not a listed .ok that pins {script.name}")
        strict = match[:1]
    else:
        strict = list(pinning)
    for o in strict:                                 # 8 (strict re-parse) + 9–15
        kv = parse_ok(o)
        if kv != parsed[o]:
            _refuse(f"{o}: strict parse differs from the v1 parse")
        _strict_checks(o, kv, modes, want_scope, known_allow, now, gate_path, gate_sha)
    dep_res = {}
    for o in pinning:                                # 6, 7 in every pinning .ok
        kv = parsed[o]
        for m in modes:
            if kv.get(f"allow_{m}", "").strip().lower() != "true":
                _refuse(f"{o}: mode {m!r} needs allow_{m}=true in the pinning .ok")
        for key, dp in (deps or {}).items():
            want = kv.get(f"dep_sha256_{key}")
            if want is None:
                _refuse(f"{o}: dep {key} ({_rel(Path(dp))}) not pinned (dep_sha256_{key}=<64 hex>)")
            if not HEX64.fullmatch(want):
                _refuse(f"{o}: dep_sha256_{key} must be full 64-hex (got {want!r})")
            got = sha256_file(dp)
            if got != want:
                _refuse(f"dep {key} {_rel(Path(dp))} sha256={got} != pinned {want} in {o}")
            dep_res[key] = got
    first = parsed[strict[0]]
    return {"gate": VERSION, "gate_sha256": gate_sha, "runner": _rel(script), "runner_sha256": sha,
            "pins": {str(o): v for o, v in pinning.items()}, "strict_oks": [str(o) for o in strict],
            "v1_only_oks": [str(o) for o in oks if o not in strict], "deps": dep_res, "modes": modes,
            "scope": first.get("scope"), "out_dir": first.get("out_dir"), "expires_et": first.get("expires_et"),
            "oks": {str(o): sha256_file(o) for o in oks}, "status": "PINNED_MATCH"}
