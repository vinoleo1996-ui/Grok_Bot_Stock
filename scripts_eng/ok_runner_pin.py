#!/usr/bin/env python3
"""Runner gate against Arch .ok markers (Arch audit P1-1; Arch review 4698a2c1 §6/§8 P2-2). Read-only; never creates or edits a .ok.

A runner calls  enforce(script_path, ok_paths, modes=[...], deps={key: path})  before doing anything else.

.ok format (Arch review §8, quantlab_run_auth_v1): one `key=value` per line. Lines without '=' and lines starting with '#'
are ignored (free text allowed). Unknown / extra keys are allowed and ignored. Keys this gate understands:
    runner_sha256_<script_stem>=<64 hex>          or   runner_sha256[<repo-relative path or file name>]=<64 hex>
    dep_sha256_<dep_key>=<64 hex>                  (dep_key as passed by the runner in `deps`)
    allow_<mode>=true|false                        (e.g. allow_disclosure_only, allow_full, allow_smoke, allow_diagnostic)
    live=false   promotion=false

Refuse (SystemExit) when ANY of:
  1. a listed .ok path does not exist (never skipped silently) or cannot be read;
  2. a listed .ok lacks live=false or promotion=false, or has them set to anything else;
  3. a pin / dep value is not exactly 64 hex characters (prefixes are no longer accepted);
  4. the same key appears twice in one .ok with different values;
  5. no listed .ok pins this script, or a pin differs from the script's own sha256 (computed now from its bytes);
  6. a requested mode is not allow_<mode>=true in every .ok that pins the script, or is allow_<mode>=false in any listed .ok;
  7. a dep declared by the runner is not pinned (dep_sha256_<key>) in a pinning .ok, or its file's sha differs.
There is deliberately no bypass flag, argv switch or environment variable.
"""
from __future__ import annotations
import hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(p: str | Path) -> str:
    return hashlib.sha256(Path(p).resolve().read_bytes()).hexdigest()


own_sha = sha256_file  # backward-compatible name


def _refuse(msg: str):
    raise SystemExit(f"REFUSED (ok_runner_pin): {msg}")


def parse_ok(path: Path) -> dict:
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


def _is_false(v: str | None) -> bool:
    return v is not None and v.strip().lower() == "false"


def enforce(script: str | Path, ok_paths, modes=(), deps: dict | None = None) -> dict:
    script = Path(script).resolve(); sha = sha256_file(script)
    oks = [Path(o) for o in ok_paths if o]
    if not oks:
        _refuse(f"{script.name}: no .ok listed")
    parsed = {}
    for o in oks:
        if not o.exists():
            _refuse(f"{script.name}: listed .ok missing: {o}")
        try:
            kv = parse_ok(o)
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
    for o, kv in parsed.items():
        for k, v in _pins(kv, script):
            if not HEX64.fullmatch(v):
                _refuse(f"{o}: {k} must be a full 64-hex lowercase sha256 (got {v!r})")
            if v != sha:
                _refuse(f"{script.name} sha256={sha} != pinned {v} ({k} in {o})")
            pinning[str(o)] = v
    if not pinning:
        _refuse(f"{script.name} sha256={sha} not pinned in any of {[str(o) for o in oks]}; "
                f"Arch must add runner_sha256_{script.stem}=<64 hex>")
    dep_res = {}
    for o in pinning:
        kv = parsed[Path(o)]
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
    return {"runner": _rel(script), "runner_sha256": sha, "pins": pinning, "deps": dep_res, "modes": list(modes),
            "oks": {str(o): sha256_file(o) for o in oks}, "status": "PINNED_MATCH"}
