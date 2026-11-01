#!/usr/bin/env python3
"""daily_basic incremental rebuild (design v3.1). Eng impl; enable requires Arch .ok.

C-mapping (see also DIFF_C1_C12_ZH.md):
  C1  RAW_NAME_RE / _select_raw_files
  C2  DbIncrSignal + SIGHUP→32 / SIGTERM re-raise → -15
  C3  compute_transform_sha + runtime_versions → exit 28
  C4  transform_daily_basic_one lives in tier1_materialize (hoisted)
  C5  except entry: SIGTERM/SIGHUP → SIG_IGN before cleanup
  C6  os.open O_CREAT|O_EXCL; fstat (st_dev,st_ino) before ParquetWriter
  C7  handlers raise promptly; S5 measured in selftest
  C8  precheck rejects new-product+stale-manifest (exit 20) without baseline
  C9  ref_build_year VmHWM guard (QL_DB_RSS_ABORT_KB)
  C10 fast-screen keys include st_ctime_ns; raw_touched / raw_full_sha_required
  C11 startup: pending → STALE_TMP → precheck
  C12 hardlink backup (second stamp); rollback link; final only os.replace
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import re
import signal
import struct
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import pandas as pd

RAW_NAME_RE = re.compile(r"^\d{8}\.parquet$")  # C1

# Exit codes (design §2.15) — never 2 or 3
OK = 0
EXCEPTION = 1
DB_INCR_PRECOND = 20
DB_INCR_STALE_TMP = 21
DB_INCR_RSS_SELF_ABORT = 22
DB_INCR_OLDYEAR_DIFF = 23
DB_INCR_DUPKEY = 24
DB_INCR_TOO_MANY_YEARS = 25
DB_INCR_END_BEFORE_PREV = 26
DB_INCR_RAW_TMP = 27
DB_INCR_TRANSFORM_CHANGED = 28
DB_INCR_COMMIT_PARTIAL = 30
DB_INCR_PENDING_CONFLICT = 31
DB_INCR_SIGNAL_HUP = 32
SIGNAL_TERM = -15

RG_TARGET = 1_048_576

TRANSFORM_CONSTANTS = {
    "available_at_hours": 18,
    "tz": "Asia/Shanghai",
    "total_mv_scale": 10000.0,
    "float_mktcap_src_col": "circ_mv",
    "float_mktcap_scale": 10000.0,
    "source": "tushare.daily_basic",
    "quality_status": "research",
    "promotion_approved": False,
    "dedup_keys": ["ts_code", "trade_date"],
    "dedup_keep": "last",
    "out_cols": [
        "ts_code", "instrument_id", "trade_date", "close",
        "turnover_rate", "turnover_rate_f", "volume_ratio",
        "pe", "pe_ttm", "pb", "ps", "ps_ttm", "dv_ttm",
        "total_share", "float_share", "free_share",
        "total_mv", "float_mktcap",
        "available_at", "source", "quality_status", "promotion_approved",
    ],
}


class DbIncrError(Exception):
    def __init__(self, code: int, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


class DbIncrSignal(BaseException):
    def __init__(self, signum: int):
        self.signum = signum


def _on_signal(signum, frame):  # C2
    raise DbIncrSignal(signum)


def _vmhwm_kb() -> int:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return 0


def _vmrss_kb() -> int:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return 0


def _guard(res: dict, abort_kb: Optional[int] = None) -> None:
    hwm = _vmhwm_kb()
    rss = _vmrss_kb()
    res["peak_vmhwm_kb"] = max(int(res.get("peak_vmhwm_kb") or 0), hwm)
    phase = res.setdefault("phase_rss_kb", {})
    phase[f"t{len(phase)}"] = {"rss": rss, "hwm": hwm}
    lim = abort_kb
    if lim is None:
        env = os.environ.get("QL_DB_RSS_ABORT_KB")
        lim = int(env) if env else None
    if lim is not None and (rss > lim or hwm > lim):
        raise DbIncrError(DB_INCR_RSS_SELF_ABORT, "DB_INCR_RSS_SELF_ABORT")



HASH_SLICE = 65_536
BANNED_ENVS_INCR = (
    "QL_DB_INCR_ALLOW_STALE_SHA",
    "QL_DB_INCR_LOOSE_READBACK",
    "QL_DB_ALLOW_FULL",
)


def _refuse_banned_envs() -> None:
    """Production incremental entry: banned envs → exit 20 (Arch impl review)."""
    for name in BANNED_ENVS_INCR:
        if os.environ.get(name):
            raise DbIncrError(
                DB_INCR_PRECOND,
                f"DB_INCR_PRECOND: banned env {name} is set (requires Arch full-path .ok)",
            )


def _enter_phase(res: dict, name: str) -> None:
    """Mark pipeline phase for A15 TERM tests; optional sleep / self-TERM via env."""
    res["_phase"] = name
    phase = res.setdefault("phase_rss_kb", {})
    phase[name] = {"rss": _vmrss_kb(), "hwm": _vmhwm_kb()}
    marker = os.environ.get("QL_DB_INCR_PHASE_MARKER")
    if marker:
        try:
            pathlib.Path(marker).write_text(name + "\n", encoding="utf-8")
        except Exception:
            pass
    _guard(res)
    sleep_spec = os.environ.get("QL_DB_INCR_PHASE_SLEEP") or ""
    if sleep_spec.startswith(name + ":"):
        try:
            time.sleep(float(sleep_spec.split(":", 1)[1]))
        except Exception:
            time.sleep(2.0)
    if os.environ.get("QL_DB_INCR_SELF_TERM_PHASE") == name:
        raise DbIncrSignal(signal.SIGTERM)


def _feed_double(h, arr) -> None:
    import pyarrow.compute as pc
    # arr: Float64 / chunked; process ≤ HASH_SLICE
    n = len(arr)
    off = 0
    while off < n:
        sl = arr.slice(off, min(HASH_SLICE, n - off))
        # validity + values via numpy
        np_arr = sl.to_numpy(zero_copy_only=False)
        # null mask
        is_null = pc.is_null(sl).to_numpy(zero_copy_only=False)
        # NaN also invalid per design
        import math
        vals = np.asarray(np_arr, dtype=np.float64)
        # -0.0 → +0.0
        vals = np.where(vals == 0.0, 0.0, vals)
        is_nan = np.isnan(vals)
        valid = ~(is_null | is_nan)
        # pack: for each row 1 byte valid + 8 bytes le
        packed = bytearray()
        for i in range(len(vals)):
            if not valid[i]:
                packed.append(0)
                packed.extend(b"\x00" * 8)
            else:
                packed.append(1)
                packed.extend(struct.pack("<d", float(vals[i])))
        h.update(packed)
        off += HASH_SLICE


def _feed_timestamp_us(h, arr) -> None:
    import pyarrow as pa
    import pyarrow.compute as pc
    import struct as _st
    n = len(arr)
    off = 0
    while off < n:
        sl = arr.slice(off, min(HASH_SLICE, n - off))
        # cast to us if needed
        t = sl.type
        if not pa.types.is_timestamp(t):
            raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: expected timestamp, got {t}")
        if t.unit != "us":
            raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: timestamp unit must be us, got {t.unit}")
        is_null = pc.is_null(sl).to_numpy(zero_copy_only=False)
        # int64 view of us
        try:
            i64 = sl.cast(pa.int64()).to_numpy(zero_copy_only=False)
        except Exception:
            i64 = np.array([0 if v is None else int(v.value if hasattr(v, "value") else v)
                            for v in sl.to_pylist()], dtype=np.int64)
        packed = bytearray()
        for i in range(len(i64)):
            if is_null[i]:
                packed.append(0)
                packed.extend(b"\x00" * 8)
            else:
                packed.append(1)
                packed.extend(_st.pack("<q", int(i64[i])))
        h.update(packed)
        off += HASH_SLICE


def _feed_large_string(h, arr, ascii_only: bool = False) -> None:
    import pyarrow.compute as pc
    import struct as _st
    n = len(arr)
    off = 0
    while off < n:
        sl = arr.slice(off, min(HASH_SLICE, n - off))
        is_null = pc.is_null(sl).to_numpy(zero_copy_only=False)
        # to pylist for strings (batch ≤65k)
        vals = sl.to_pylist()
        packed = bytearray()
        for i, v in enumerate(vals):
            if is_null[i] or v is None:
                packed.append(0)
                packed.extend(_st.pack("<q", 0))
            else:
                b = v.encode("utf-8") if isinstance(v, str) else bytes(v)
                if ascii_only and not b.isascii():
                    raise DbIncrError(DB_INCR_PRECOND, "DB_INCR_PRECOND: non-ASCII in ts_code/instrument_id")
                packed.append(1)
                packed.extend(_st.pack("<q", len(b)))
                packed.extend(b)
        h.update(packed)
        off += HASH_SLICE


def _feed_bool(h, arr) -> None:
    import pyarrow.compute as pc
    n = len(arr)
    off = 0
    while off < n:
        sl = arr.slice(off, min(HASH_SLICE, n - off))
        is_null = pc.is_null(sl).to_numpy(zero_copy_only=False)
        vals = sl.to_numpy(zero_copy_only=False)
        packed = bytearray()
        for i in range(len(vals)):
            if is_null[i]:
                packed.append(0)
                packed.append(0)
            else:
                packed.append(1)
                packed.append(1 if vals[i] else 0)
        h.update(packed)
        off += HASH_SLICE


def _row_group_physical_col_hashes(table) -> dict:
    """§2.8 / D4: physical-order per-column sha256 (no sort)."""
    import pyarrow as pa
    out = {}
    n = table.num_rows
    for name in table.column_names:
        col = table.column(name)
        # combine chunks
        if hasattr(col, "combine_chunks"):
            try:
                col = col.combine_chunks()
            except Exception:
                pass
        h = hashlib.sha256()
        # header: name + arrow type + nrows (design §4.2 content header style; physical uses same normalize)
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(str(col.type).encode("utf-8"))
        h.update(b"\0")
        h.update(str(n).encode("utf-8"))
        h.update(b"\0")
        t = col.type
        if pa.types.is_floating(t):
            _feed_double(h, col)
        elif pa.types.is_timestamp(t):
            _feed_timestamp_us(h, col)
        elif pa.types.is_string(t) or pa.types.is_large_string(t):
            _feed_large_string(h, col, ascii_only=(name in ("ts_code", "instrument_id")))
        elif pa.types.is_boolean(t):
            _feed_bool(h, col)
        elif pa.types.is_integer(t):
            # treat as double-like via cast? design only lists 4 types; cast to double for safety
            import pyarrow.compute as pc
            _feed_double(h, pc.cast(col, pa.float64()))
        else:
            # fallback: string form of type rejection for dictionary etc.
            raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: unsupported col type {name}:{t}")
        out[name] = h.hexdigest()
    return out


def _rg_trade_date_year(table) -> int:
    import pyarrow.compute as pc
    td = table.column("trade_date")
    try:
        years = pc.year(td)
        ymin = pc.min(years).as_py()
        ymax = pc.max(years).as_py()
    except Exception:
        s = pd.to_datetime(td.to_pandas())
        ymin = int(s.dt.year.min()); ymax = int(s.dt.year.max())
    if ymin != ymax:
        raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: row group spans years {ymin}-{ymax}")
    return int(ymin)



def runtime_versions() -> Dict[str, str]:
    import pyarrow
    return {
        "python": sys.version.split()[0],
        "pandas": pd.__version__,
        "pyarrow": pyarrow.__version__,
        "numpy": np.__version__,
    }


def _strip_docstrings(node: ast.AST) -> ast.AST:
    """Remove module/class/function docstrings for stable transform_sha (C3)."""
    for parent in ast.walk(node):
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (
                parent.body
                and isinstance(parent.body[0], ast.Expr)
                and isinstance(getattr(parent.body[0], "value", None), ast.Constant)
                and isinstance(parent.body[0].value.value, str)
            ):
                parent.body = parent.body[1:] or [ast.Pass()]
    return node


def _source_of(obj) -> str:
    import inspect
    return inspect.getsource(obj)


def compute_transform_sha(tier1_mod=None) -> str:
    """C3 / Eng proposal: sha256(ast.dump(normalized, include_attributes=False))
    over transform_daily_basic_one + to_iid + _daily_basic_val_cols, plus
    TRANSFORM_CONSTANTS JSON (sorted keys, separators compact).
    Docstrings stripped. Fingerprint of runtime versions is SEPARATE
    (manifest.build.runtime_versions); mismatch also → exit 28.
    """
    if tier1_mod is None:
        import tier1_materialize as tier1_mod  # type: ignore
    pieces = []
    for name in ("transform_daily_basic_one", "to_iid", "_daily_basic_val_cols"):
        fn = getattr(tier1_mod, name)
        src = _source_of(fn)
        tree = ast.parse(src)
        _strip_docstrings(tree)
        # Normalize: dump without attributes; fix_missing_locations
        ast.fix_missing_locations(tree)
        dump = ast.dump(tree, include_attributes=False, indent=None)
        pieces.append(f"###{name}\n{dump}\n")
    const_blob = json.dumps(TRANSFORM_CONSTANTS, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    pieces.append(f"###CONSTANTS\n{const_blob}\n")
    blob = "".join(pieces).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _sha256_file(path: pathlib.Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def _atomic_write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _result(res: dict, code: int, reason: str) -> int:
    res = dict(res)
    res["exit_code"] = code
    res["reason_code"] = reason
    # Ensure required fields present
    for k in (
        "mode", "rebuilt_years", "copied_years", "prev_sha256", "new_sha256",
        "transform_sha", "runtime_versions", "rows", "rows_by_year",
        "peak_vmhwm_kb", "phase_rss_kb", "history_diff_rows",
        "history_diff_by_year", "raw_inventory_changed_years", "backup_path",
    ):
        res.setdefault(k, None)
    print("DB_INCR_RESULT " + json.dumps(res, ensure_ascii=False, default=str), flush=True)
    return code


def _select_raw_files(raw_dir: pathlib.Path, start: str, end: str, year: Optional[int] = None):
    """C1: only names matching ^\\d{8}\\.parquet$."""
    out = []
    for p in sorted(raw_dir.iterdir()) if raw_dir.exists() else []:
        if not p.is_file():
            continue
        if not RAW_NAME_RE.match(p.name):
            # *.tmp.parquet in an R year → 27 (caller checks)
            continue
        stem = p.name[:8]
        if start <= stem <= end:
            if year is None or stem.startswith(str(year)):
                out.append(p)
    return out


def _year_has_tmp(raw_dir: pathlib.Path, year: int) -> bool:
    if not raw_dir.exists():
        return False
    for p in raw_dir.iterdir():
        if p.name.endswith(".tmp.parquet") and p.name[:4] == str(year):
            return True
    return False


def _fast_screen_key(p: pathlib.Path) -> dict:
    """C10: (name, size, mtime_ns, st_ino, st_ctime_ns)."""
    st = p.stat()
    return {
        "name": p.name,
        "size": int(st.st_size),
        "mtime_ns": int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))),
        "st_ino": int(st.st_ino),
        "st_ctime_ns": int(getattr(st, "st_ctime_ns", int(st.st_ctime * 1e9))),
    }


def _content_sha_inventory(files: Sequence[pathlib.Path]) -> List[dict]:
    inv = []
    for p in sorted(files, key=lambda x: x.name):
        inv.append({"name": p.name, "size": p.stat().st_size, "sha256": _sha256_file(p)})
    return inv


def _inventory_digest(inv: List[dict]) -> str:
    blob = json.dumps(inv, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def _rebuild_years(end: str, prev_manifest: dict, raw_dir: pathlib.Path, res: dict) -> Set[int]:
    """§2.2: R default {Y}; January → {Y-1,Y}; raw changes add old years (cap 2)."""
    Y = int(end[:4])
    R: Set[int] = {Y}
    if end[4:6] == "01":
        R.add(Y - 1)
    force_full = False
    touched = raw_dir.parent / "raw_touched" if raw_dir.name != "daily_basic" else raw_dir.parent.parent / "raw_touched"
    # Convention: marker beside raw_dir or env/ok note
    for cand in (
        raw_dir / "raw_touched",
        raw_dir.parent / "raw_touched",
        pathlib.Path(os.environ.get("QL_DB_RAW_TOUCHED", "/nonexistent")),
    ):
        if cand.exists():
            force_full = True
            break
    if os.environ.get("QL_DB_RAW_FULL_SHA_REQUIRED", "").lower() in ("1", "true", "yes"):
        force_full = True

    prev_inv = (prev_manifest.get("build") or {}).get("raw_inventory") or {}
    changed_old: List[int] = []
    # Group prev inventory by year
    prev_by_year = prev_inv.get("by_year") or {}
    mode = "content" if force_full or os.environ.get("QL_DB_FORCE_CONTENT_SHA") == "1" else "fast"

    for y in range(2014, Y):  # old years only
        files = _select_raw_files(raw_dir, f"{y}0101", f"{y}1231", year=y)
        if _year_has_tmp(raw_dir, y):
            # only fail if this year ends up in R; check later for R years
            pass
        if mode == "content":
            inv = _content_sha_inventory(files)
            dig = _inventory_digest(inv)
            prev_dig = (prev_by_year.get(str(y)) or {}).get("digest")
            keys = None
        else:
            keys = [_fast_screen_key(p) for p in files]
            dig = _inventory_digest(keys)
            prev_dig = (prev_by_year.get(str(y)) or {}).get("fast_digest")
            inv = keys
        if prev_dig is not None and dig != prev_dig:
            changed_old.append(y)
            R.add(y)
            res.setdefault("raw_changed_files", {})[str(y)] = [
                (x.get("name") if isinstance(x, dict) else str(x)) for x in (inv or [])
            ]
    if len(changed_old) > 2:
        raise DbIncrError(DB_INCR_TOO_MANY_YEARS, "DB_INCR_TOO_MANY_YEARS")
    res["raw_inventory_changed_years"] = changed_old
    res["_inv_mode"] = mode
    return R


def _recover_pending(dest, manifest, status, bak_dir, res) -> None:
    """C11 step 1."""
    pending = manifest.with_name(manifest.name.replace(".json", ".pending.json"))
    if not pending.exists():
        # also accept explicit .pending.json suffix pattern from design
        alt = dest.parent / "daily_basic_full_tushare_manifest.pending.json"
        pending = alt if alt.exists() else pending
    if not pending.exists():
        return
    try:
        pend = json.loads(pending.read_text(encoding="utf-8"))
    except Exception as e:
        raise DbIncrError(DB_INCR_PENDING_CONFLICT, f"DB_INCR_PENDING_CONFLICT: bad pending: {e}")
    cur_sha = _sha256_file(dest) if dest.exists() else None
    new_sha = pend.get("new_sha")
    prev_sha = pend.get("prev_sha")
    if cur_sha == new_sha:
        # finish steps 5,6,7 lightly: replace pending→manifest if build present
        build = pend.get("build") or pend
        if "build" in pend:
            man_obj = json.loads(manifest.read_text()) if manifest.exists() else {}
            man_obj.setdefault("build", {}).update(pend["build"])
            _atomic_write_json(manifest, man_obj)
        else:
            _atomic_write_json(manifest, build if isinstance(build, dict) else pend)
        q = pending.parent / "_quarantine"
        # success path: pending consumed via replace
        os.replace(pending, manifest) if False else pending.unlink(missing_ok=True)
        res["pending_recovered"] = "completed_commit"
        return
    if cur_sha == prev_sha:
        q = pending.parent / "_quarantine"
        q.mkdir(parents=True, exist_ok=True)
        dest_q = q / (pending.name + f".{int(time.time())}")
        os.replace(pending, dest_q)
        res["pending_recovered"] = f"quarantined:{dest_q.name}"
        return
    raise DbIncrError(DB_INCR_PENDING_CONFLICT, "DB_INCR_PENDING_CONFLICT")


def _precheck(dest, manifest, end, tier1_mod, res) -> dict:
    """C11 step 3 / §5.4 / C3 / C8."""
    if not dest.exists() or not manifest.exists():
        raise DbIncrError(DB_INCR_PRECOND, "DB_INCR_PRECOND: missing dest or manifest")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    build = man.get("build") or {}
    # C8 / A18: missing new_sha256 OR dest sha mismatch → exit 20 (no silent skip)
    dest_sha = _sha256_file(dest)
    expected = build.get("new_sha256")
    if not expected:
        raise DbIncrError(DB_INCR_PRECOND, "DB_INCR_PRECOND: missing build.new_sha256 (A18)")
    if dest_sha != expected:
        raise DbIncrError(DB_INCR_PRECOND, "DB_INCR_PRECOND: dest sha != manifest.build.new_sha256 (A18)")
    # transform / runtime
    cur_t = compute_transform_sha(tier1_mod)
    cur_r = runtime_versions()
    prev_t = build.get("transform_sha")
    prev_r = build.get("runtime_versions")
    res["transform_sha"] = cur_t
    res["runtime_versions"] = cur_r
    if prev_t and prev_t != cur_t:
        raise DbIncrError(DB_INCR_TRANSFORM_CHANGED, "DB_INCR_TRANSFORM_CHANGED: transform_sha")
    if prev_r and prev_r != cur_r:
        raise DbIncrError(DB_INCR_TRANSFORM_CHANGED, "DB_INCR_TRANSFORM_CHANGED: runtime_versions")
    date_max = (man.get("date_max") or build.get("date_max") or "")[:10].replace("-", "")
    if date_max and end < date_max:
        raise DbIncrError(DB_INCR_END_BEFORE_PREV, "DB_INCR_END_BEFORE_PREV")
    res["prev_sha256"] = dest_sha
    return man


def _df_to_table(df, schema=None):
    import pyarrow as pa
    if schema is not None:
        return pa.Table.from_pandas(df, schema=schema, preserve_index=False)
    return pa.Table.from_pandas(df, preserve_index=False)


def _build_year(y, raw_dir, end, writer, rec, res, tier1_mod, schema):
    import pyarrow as pa
    import pyarrow.parquet as pq
    if res.get("_phase") != "build":
        _enter_phase(res, "build")
    files = _select_raw_files(raw_dir, f"{y}0101", min(f"{y}1231", end), year=y)
    if _year_has_tmp(raw_dir, y):
        raise DbIncrError(DB_INCR_RAW_TMP, "DB_INCR_RAW_TMP")
    if not files and y == int(end[:4]):
        raise DbIncrError(DB_INCR_PRECOND, "DB_INCR_PRECOND: end year has no raw files")
    one = tier1_mod.transform_daily_basic_one
    buf = []
    buf_rows = 0
    year_rows = 0
    seen_keys: Set[Tuple[str, str]] = set()

    def flush(n=None):
        nonlocal buf, buf_rows, year_rows
        if not buf:
            return
        import pyarrow as pa
        t = pa.concat_tables(buf)
        buf = []
        buf_rows = 0
        while len(t) > 0:
            take = len(t) if n is None else min(n, len(t))
            if n is not None:
                take = min(RG_TARGET, len(t))
            piece = t.slice(0, take)
            writer.write_table(piece)
            ph = _row_group_physical_col_hashes(piece)
            rec.append({
                "year": y,
                "rows": piece.num_rows,
                "row_group_physical_col_hashes": ph,
                "copied": False,
            })
            year_rows += piece.num_rows
            t = t.slice(take)
            if n is None:
                break

    for f in files:
        df = one(f)
        if df is None or df.empty:
            continue
        # date match assert
        dmin = df["trade_date"].min()
        dmax = df["trade_date"].max()
        expect = pd.Timestamp(f.name[:8])
        if pd.Timestamp(dmin).normalize() != expect or pd.Timestamp(dmax).normalize() != expect:
            raise DbIncrError(DB_INCR_DUPKEY, "DB_INCR_DATE_MISMATCH")
        # cross-file dup keys
        for ts, td in zip(df["ts_code"].astype(str), df["trade_date"].astype(str)):
            key = (ts, str(td)[:10])
            if key in seen_keys:
                raise DbIncrError(DB_INCR_DUPKEY, "DB_INCR_DUPKEY")
            seen_keys.add(key)
        tbl = _df_to_table(df, schema=schema)
        del df
        buf.append(tbl)
        buf_rows += tbl.num_rows
        if buf_rows >= RG_TARGET:
            flush(RG_TARGET)
        _guard(res)
    flush(None)
    res.setdefault("rows_by_year", {})[str(y)] = year_rows
    res.setdefault("rebuilt_years", []).append(y)
    return year_rows


def _copy_year(y, dest_prev, writer, rec, res):
    """§2.4 single-resident row group copy; only RGs whose trade_date year == y."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    if res.get("_phase") != "copy":
        _enter_phase(res, "copy")
    pf = pq.ParquetFile(dest_prev, pre_buffer=False, buffer_size=1 << 20)
    year_rows = 0
    for i in range(pf.metadata.num_row_groups):
        t = pf.read_row_group(i)
        if "trade_date" not in t.column_names:
            del t
            continue
        # Determine year span of this RG
        td = t.column("trade_date")
        # cast to timestamp if needed
        try:
            years = pc.year(td)
            ymin = pc.min(years).as_py()
            ymax = pc.max(years).as_py()
        except Exception:
            s = td.to_pandas()
            s = pd.to_datetime(s)
            ymin = int(s.dt.year.min()); ymax = int(s.dt.year.max())
        if ymin != ymax:
            raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: row group spans years {ymin}-{ymax}")
        if ymin != y:
            del t
            continue
        # physical hashes on slices ≤65,536 before write (design §2.4)
        ph = _row_group_physical_col_hashes(t)
        writer.write_table(t)
        rec.append({
            "year": y,
            "rows": t.num_rows,
            "row_group_physical_col_hashes": ph,
            "copied": True,
        })
        year_rows += t.num_rows
        del t
        try:
            pa.default_memory_pool().release_unused()
        except Exception:
            pass
        _guard(res)
    res.setdefault("rows_by_year", {})[str(y)] = year_rows
    res.setdefault("copied_years", []).append(y)
    return year_rows


def _verify_readback(tmp, rec, res=None):
    """§2.8 design-level: iter_batches / row-group physical col hashes; no LOOSE bypass."""
    import pyarrow.parquet as pq
    if res is not None:
        _enter_phase(res, "readback")
    pf = pq.ParquetFile(str(tmp), pre_buffer=False, buffer_size=1 << 20)
    nrg = pf.metadata.num_row_groups
    if nrg != len(rec):
        raise DbIncrError(
            DB_INCR_OLDYEAR_DIFF,
            f"DB_INCR_OLDYEAR_DIFF: row_group count {nrg} != recorded {len(rec)}",
        )
    # Read each row group once (iter over RGs; design also allows iter_batches)
    for i, r in enumerate(rec):
        t = pf.read_row_group(i)
        if t.num_rows != r["rows"]:
            raise DbIncrError(
                DB_INCR_OLDYEAR_DIFF,
                f"DB_INCR_OLDYEAR_DIFF: rg[{i}] rows {t.num_rows} != {r['rows']}",
            )
        y = _rg_trade_date_year(t)
        if y != r["year"]:
            raise DbIncrError(
                DB_INCR_OLDYEAR_DIFF,
                f"DB_INCR_OLDYEAR_DIFF: rg[{i}] year {y} != recorded {r['year']}",
            )
        ph = _row_group_physical_col_hashes(t)
        expected = r.get("row_group_physical_col_hashes") or {}
        if ph != expected:
            # pinpoint first differing column
            bad = [c for c in ph if ph.get(c) != expected.get(c)]
            raise DbIncrError(
                DB_INCR_OLDYEAR_DIFF,
                f"DB_INCR_OLDYEAR_DIFF: rg[{i}] physical col hash mismatch cols={bad[:5]}",
            )
        del t
        if res is not None:
            _guard(res)


def _iter_monthly_frames(path, years: Set[int], cols: List[str]):
    """Single-pass iter_batches; yield (year, month, df) in order. Peak ≈ one month. §2.9."""
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(str(path), pre_buffer=False, buffer_size=1 << 20)
    cur_ym = None
    buf: List[pd.DataFrame] = []
    for batch in pf.iter_batches(columns=cols, batch_size=HASH_SLICE):
        df = batch.to_pandas()
        if df.empty:
            continue
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["_y"] = df["trade_date"].dt.year.astype(int)
        df["_m"] = df["trade_date"].dt.month.astype(int)
        # keep only target years; preserve encounter order
        for (y, m), g in df.groupby(["_y", "_m"], sort=True):
            y = int(y); m = int(m)
            if y not in years:
                continue
            ym = (y, m)
            if cur_ym is None:
                cur_ym = ym
            if ym != cur_ym:
                if buf:
                    yield cur_ym[0], cur_ym[1], pd.concat(buf, ignore_index=True)
                    buf = []
                cur_ym = ym
            buf.append(g.drop(columns=["_y", "_m"]))
        del df
    if cur_ym is not None and buf:
        yield cur_ym[0], cur_ym[1], pd.concat(buf, ignore_index=True)


def _history_diff_scan(dest, tmp, R, diff_dir, res, tier1_mod=None):
    """§2.9 sequential scan + monthly buckets; no full-table fallback; DupKey→24."""
    _enter_phase(res, "diff")
    if not pathlib.Path(dest).exists():
        res["history_diff_rows"] = 0
        res["history_diff_by_year"] = {}
        return 0
    if tier1_mod is None:
        import tier1_materialize as tier1_mod  # type: ignore
    compare = tier1_mod._compare_daily_basic_history
    val_cols = list(tier1_mod._daily_basic_val_cols())
    cols = ["ts_code", "trade_date"] + val_cols
    years = set(int(y) for y in R)
    if not years:
        res["history_diff_rows"] = 0
        res["history_diff_by_year"] = {}
        return 0

    # Merge two ordered month streams; keep at most one month per side.
    old_it = _iter_monthly_frames(dest, years, cols)
    new_it = _iter_monthly_frames(tmp, years, cols)
    old_n = next(old_it, None)
    new_n = next(new_it, None)
    diff = 0
    by: Dict[str, int] = {}
    empty = pd.DataFrame(columns=cols)
    try:
        while old_n is not None or new_n is not None:
            if old_n is None:
                y, m, n = new_n
                o = empty
                new_n = next(new_it, None)
            elif new_n is None:
                y, m, o = old_n
                n = empty
                old_n = next(old_it, None)
            else:
                oy, om, odf = old_n
                ny, nm, ndf = new_n
                if (oy, om) == (ny, nm):
                    y, m, o, n = oy, om, odf, ndf
                    old_n = next(old_it, None)
                    new_n = next(new_it, None)
                elif (oy, om) < (ny, nm):
                    y, m, o, n = oy, om, odf, empty
                    old_n = next(old_it, None)
                else:
                    y, m, o, n = ny, nm, empty, ndf
                    new_n = next(new_it, None)
            d = int(compare(o, n))
            by[str(y)] = by.get(str(y), 0) + d
            diff += d
            del o, n
            _guard(res)
    except ValueError as e:
        if "duplicate" in str(e).lower():
            raise DbIncrError(DB_INCR_DUPKEY, "DB_INCR_DUPKEY") from e
        raise

    res["history_diff_rows"] = diff
    res["history_diff_by_year"] = by
    if diff_dir is not None:
        diff_dir = pathlib.Path(diff_dir)
        diff_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        end_hint = str((res.get("rebuilt_years") or ["x"])[-1])
        rep = diff_dir / f"{end_hint}_{stamp}.json"
        _atomic_write_json(rep, {"diff": diff, "by_year": by, "years": sorted(years)})
        res["history_diff_report"] = str(rep)
    return diff


# Back-compat alias (tests / callers)
_history_diff_stub = _history_diff_scan


def _rollback_backup_link(res):
    """C12: unlink newly created backup hardlink if still same inode as recorded."""
    info = res.get("_bak_link")
    if not info:
        return
    bak = pathlib.Path(info["path"])
    if not bak.exists():
        return
    st = bak.stat()
    if (st.st_dev, st.st_ino) == tuple(info["id"]):
        bak.unlink()
        res["backup_link_rolled_back"] = True


def _quarantine_pending_if_unchanged(dest, pending_path, prev_sha, res):
    if pending_path is None or not pending_path.exists():
        return
    if not dest.exists():
        return
    if _sha256_file(dest) == prev_sha:
        q = pending_path.parent / "_quarantine"
        q.mkdir(parents=True, exist_ok=True)
        os.replace(pending_path, q / f"{pending_path.name}.{int(time.time())}")
        res["pending_quarantined_by_self"] = True


def _commit(tmp, dest, manifest, status, bak_dir, res, man_prev, tier1_mod):
    """§2.10 / C12."""
    bak_dir = pathlib.Path(bak_dir)
    bak_dir.mkdir(parents=True, exist_ok=True)
    new_sha = _sha256_file(tmp)
    prev_sha = res.get("prev_sha256")
    stamp = time.strftime("%Y%m%d_%H%M%S")  # C12 seconds
    bak = bak_dir / f"daily_basic_full_tushare.{stamp}.parquet"
    pending = pathlib.Path(manifest).with_name("daily_basic_full_tushare_manifest.pending.json")

    build = {
        "mode": "incremental",
        "rebuilt_years": res.get("rebuilt_years"),
        "copied_years": res.get("copied_years"),
        "rows_by_year": res.get("rows_by_year"),
        "prev_sha256": prev_sha,
        "new_sha256": new_sha,
        "transform_sha": res.get("transform_sha"),
        "runtime_versions": res.get("runtime_versions"),
        "raw_inventory": res.get("raw_inventory"),
        "peak_vmhwm_kb": res.get("peak_vmhwm_kb"),
        "phase_rss_kb": res.get("phase_rss_kb"),
        "history_diff_rows": res.get("history_diff_rows"),
        "history_diff_by_year": res.get("history_diff_by_year"),
        "history_diff_report": res.get("history_diff_report"),
        "backup_path": str(bak),
    }
    pend_obj = {"prev_sha": prev_sha, "new_sha": new_sha, "build": build}
    _atomic_write_json(pending, pend_obj)
    res["_pending_path"] = str(pending)

    # hardlink backup (C12)
    try:
        os.link(dest, bak)
        st = bak.stat()
        res["_bak_link"] = {"path": str(bak), "id": (st.st_dev, st.st_ino)}
        res["backup_path"] = str(bak)
    except OSError as e:
        # rollback: quarantine pending, no replace
        _quarantine_pending_if_unchanged(dest, pending, prev_sha, res)
        raise DbIncrError(DB_INCR_PRECOND, f"DB_INCR_PRECOND: hardlink backup failed: {e}") from e

    # final product ONLY via os.replace (C12)
    os.replace(tmp, dest)
    try:
        dir_fd = os.open(str(dest.parent), os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        pass

    # pending → manifest
    try:
        man_obj = dict(man_prev) if man_prev else {}
        man_obj["build"] = build
        man_obj["rows"] = int(sum((res.get("rows_by_year") or {}).values()))
        man_obj["path"] = str(dest)
        # date_max from end-ish
        _atomic_write_json(manifest, man_obj)
        if pending.exists():
            pending.unlink(missing_ok=True)
    except Exception as e:
        res["new_sha256"] = new_sha
        raise DbIncrError(DB_INCR_COMMIT_PARTIAL, f"DB_INCR_COMMIT_PARTIAL: {e}") from e

    # status patch (best-effort; path-explicit for selftest)
    try:
        if status is not None:
            st_path = pathlib.Path(status)
            st = json.loads(st_path.read_text()) if st_path.exists() else {
                "schema": "quantlab.v2.daily_update_status.v1", "tables": {},
                "promotion_approved": False, "live": False,
            }
            t = st.setdefault("tables", {}).setdefault("daily_basic", {})
            t.update({
                "path": str(dest),
                "rows": man_obj.get("rows"),
                "sha256": new_sha,
                "history_diff_rows": res.get("history_diff_rows"),
                "backup_path": str(bak),
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            })
            _atomic_write_json(st_path, st)
    except Exception:
        pass

    # prune keep=5 after success; never delete just-created bak
    existing = sorted(bak_dir.glob("daily_basic_full_tushare.*.parquet"), key=lambda p: p.name)
    for p in existing[:-5]:
        if p.resolve() != bak.resolve():
            p.unlink(missing_ok=True)

    res["new_sha256"] = new_sha
    res["rows"] = man_obj.get("rows")
    return bak


def _build_raw_inventory(raw_dir, start, end, mode, R):
    by_year = {}
    all_files = _select_raw_files(raw_dir, start, end)
    years = sorted({int(p.name[:4]) for p in all_files})
    for y in years:
        files = [p for p in all_files if p.name.startswith(str(y))]
        if mode == "content":
            inv = _content_sha_inventory(files)
            by_year[str(y)] = {"digest": _inventory_digest(inv), "files": inv}
        else:
            keys = [_fast_screen_key(p) for p in files]
            by_year[str(y)] = {"fast_digest": _inventory_digest(keys), "files": keys}
    return {"mode": mode, "by_year": by_year}


def materialize_daily_basic_incremental(
    *,
    end: str,
    raw_dir,
    dest,
    manifest,
    status,
    bak_dir,
    diff_dir,
    start: str = "20140101",
    tier1_mod=None,
):
    """Incremental rebuild. All paths explicit (P1-8). Does not read module ROOT/RAW."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    raw_dir = pathlib.Path(raw_dir)
    dest = pathlib.Path(dest)
    manifest = pathlib.Path(manifest)
    status = pathlib.Path(status) if status is not None else None
    bak_dir = pathlib.Path(bak_dir)
    diff_dir = pathlib.Path(diff_dir) if diff_dir is not None else dest.parent / "history_diff"
    tmp = dest.with_suffix(".tmp.parquet")

    if tier1_mod is None:
        import tier1_materialize as tier1_mod  # type: ignore

    old_handlers = {}
    for s in (signal.SIGTERM, signal.SIGHUP):
        old_handlers[s] = signal.signal(s, _on_signal)

    tmp_id = None
    w = None
    fd = None
    res: Dict[str, Any] = {
        "mode": "incremental",
        "rebuilt_years": [],
        "copied_years": [],
        "peak_vmhwm_kb": _vmhwm_kb(),
        "phase_rss_kb": {},
    }
    pending_path = dest.parent / "daily_basic_full_tushare_manifest.pending.json"
    prev_sha_for_rollback = None

    try:
        _refuse_banned_envs()
        # C11: pending → STALE_TMP → precheck
        _recover_pending(dest, manifest, status, bak_dir, res)
        if tmp.exists():
            raise DbIncrError(DB_INCR_STALE_TMP, "DB_INCR_STALE_TMP")
        man_prev = _precheck(dest, manifest, end, tier1_mod, res)
        prev_sha_for_rollback = res.get("prev_sha256")

        R = _rebuild_years(end, man_prev, raw_dir, res)
        for y in list(R):
            if _year_has_tmp(raw_dir, y):
                raise DbIncrError(DB_INCR_RAW_TMP, "DB_INCR_RAW_TMP")

        # schema from previous product
        schema = pq.read_schema(dest)

        # C6: O_EXCL + immediate inode, then path-based ParquetWriter.
        # pyarrow 26: ParquetWriter(os.fdopen(...)) leaves 0-byte files; design allows
        # handing fd *or* equivalent — we keep O_EXCL create + inode pin, then reopen by path
        # (same inode on Linux truncate-open).
        fd = os.open(str(tmp), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        st = os.fstat(fd)
        tmp_id = (st.st_dev, st.st_ino)
        os.close(fd)
        fd = None
        w = pq.ParquetWriter(str(tmp), schema, compression="snappy")
        rec = []

        y0 = int(start[:4])
        y1 = int(end[:4])
        # Determine years present in prev product
        pf_prev = pq.ParquetFile(dest)
        prev_years = set()
        # infer from manifest rows_by_year or scan
        rby = (man_prev.get("build") or {}).get("rows_by_year") or man_prev.get("rows_by_year") or {}
        if rby:
            prev_years = {int(k) for k in rby}
        else:
            prev_years = set(range(y0, y1 + 1))

        for y in range(y0, y1 + 1):
            if y in R:
                _build_year(y, raw_dir, end, w, rec, res, tier1_mod, schema)
            elif y in prev_years:
                _copy_year(y, dest, w, rec, res)
            _guard(res)

        w.close()
        w = None
        _verify_readback(tmp, rec, res)
        _history_diff_scan(dest, tmp, R, diff_dir, res, tier1_mod=tier1_mod)

        mode = res.get("_inv_mode") or "fast"
        res["raw_inventory"] = _build_raw_inventory(raw_dir, start, end, mode, R)

        _enter_phase(res, "commit")
        _commit(tmp, dest, manifest, status, bak_dir, res, man_prev, tier1_mod)
        return _result(res, OK, "OK")

    except BaseException as e:
        # C5: ignore signals during cleanup
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        if w is not None:
            try:
                w.close()
            except Exception:
                pass
            w = None
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass
            fd = None
        if tmp_id is not None and tmp.exists():
            try:
                s2 = os.stat(tmp)
                if (s2.st_dev, s2.st_ino) == tmp_id:
                    tmp.unlink()
            except Exception:
                pass
        _rollback_backup_link(res)
        _quarantine_pending_if_unchanged(dest, pending_path, prev_sha_for_rollback, res)

        if isinstance(e, DbIncrSignal):
            if e.signum == signal.SIGHUP:
                _result(res, DB_INCR_SIGNAL_HUP, "DB_INCR_SIGNAL_HUP")
                return DB_INCR_SIGNAL_HUP  # C2: no re-raise
            # SIGTERM: restore default and re-raise to self → -15
            _result(res, SIGNAL_TERM, "SIGNAL_TERM")
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            os.kill(os.getpid(), signal.SIGTERM)
            return SIGNAL_TERM  # unreachable if kill works
        if isinstance(e, DbIncrError):
            return _result(res, e.code, e.reason)
        _result(res, EXCEPTION, "EXCEPTION")
        raise
    finally:
        for s, h in old_handlers.items():
            try:
                signal.signal(s, h)
            except Exception:
                pass


def materialize_daily_basic_cli(argv: Optional[Sequence[str]] = None) -> int:
    """CLI returning int exit code. Incremental only when --mode incremental."""
    argv = list(sys.argv[1:] if argv is None else argv)
    import argparse
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--mode", choices=("incremental", "full"), required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--start", default="20140101")
    ap.add_argument("--raw-dir", required=False, default=None)
    ap.add_argument("--dest", required=False, default=None)
    ap.add_argument("--manifest", required=False, default=None)
    ap.add_argument("--status", required=False, default=None)
    ap.add_argument("--bak-dir", required=False, default=None)
    ap.add_argument("--diff-dir", required=False, default=None)
    ns = ap.parse_args(argv)
    if ns.mode == "full":
        if os.environ.get("QL_DB_ALLOW_FULL") != "1":
            print("DB_INCR_RESULT " + json.dumps({
                "mode": "full", "exit_code": 20, "reason_code": "DB_INCR_PRECOND",
                "detail": "full mode requires QL_DB_ALLOW_FULL=1",
            }), flush=True)
            return DB_INCR_PRECOND
        # Do not run full against implicit ROOT tonight; require explicit paths via legacy API.
        print("full mode: use materialize_daily_basic() under QL_DB_ALLOW_FULL=1; CLI full path not auto-wired", flush=True)
        return DB_INCR_PRECOND
    missing = [k for k in ("raw_dir", "dest", "manifest", "bak_dir") if getattr(ns, k.replace("-", "_") if False else k, None) is None]
    # argparse converts to raw_dir
    for req in ("raw_dir", "dest", "manifest", "bak_dir"):
        if getattr(ns, req) is None:
            print(f"missing --{req.replace('_','-')}", flush=True)
            return DB_INCR_PRECOND
    return materialize_daily_basic_incremental(
        end=ns.end,
        start=ns.start,
        raw_dir=ns.raw_dir,
        dest=ns.dest,
        manifest=ns.manifest,
        status=ns.status or (str(pathlib.Path(ns.dest).parent / "status.json")),
        bak_dir=ns.bak_dir,
        diff_dir=ns.diff_dir,
    )


def ref_build_year(year: int, raw_dir, end: str, tier1_mod=None) -> dict:
    """§4.1 / C9: monthly loop; stream hashes; no full-year resident frame (A13)."""
    import pyarrow as pa
    if tier1_mod is None:
        import tier1_materialize as tier1_mod  # type: ignore
    one = tier1_mod.transform_daily_basic_one
    files = _select_raw_files(pathlib.Path(raw_dir), f"{year}0101", min(f"{year}1231", end), year=year)
    res_g = {"peak_vmhwm_kb": _vmhwm_kb(), "phase_rss_kb": {}}
    by_m: Dict[int, List[pathlib.Path]] = {}
    for f in files:
        by_m.setdefault(int(f.name[4:6]), []).append(f)
    total_rows = 0
    h_keys = hashlib.sha256()
    h_keys.update(b"ts_code,trade_date\n")
    col_hashes: Dict[str, Any] = {}
    out_cols = list(TRANSFORM_CONSTANTS["out_cols"])
    headers_fed = False

    for m in sorted(by_m):
        frames = []
        for f in by_m[m]:
            df = one(f)
            if df is None or df.empty:
                continue
            frames.append(df)
            _guard(res_g)
        if not frames:
            continue
        chunk = pd.concat(frames, ignore_index=True)
        del frames
        chunk = chunk.drop_duplicates(["ts_code", "trade_date"], keep="last")
        chunk = chunk.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
        for ts, td in zip(chunk["ts_code"].astype(str), chunk["trade_date"].astype(str)):
            h_keys.update(f"{ts},{str(td)[:10]}\n".encode())
        tbl = pa.Table.from_pandas(chunk, preserve_index=False)
        if not headers_fed:
            for c in out_cols:
                if c in tbl.column_names:
                    col_hashes[c] = hashlib.sha256()
                    col_hashes[c].update(c.encode("utf-8"))
                    col_hashes[c].update(b"\0")
                    col_hashes[c].update(str(tbl.column(c).type).encode("utf-8"))
                    col_hashes[c].update(b"\0")
            headers_fed = True
        ph = _row_group_physical_col_hashes(tbl)
        for c, dig in ph.items():
            if c not in col_hashes:
                col_hashes[c] = hashlib.sha256()
                col_hashes[c].update(c.encode())
            col_hashes[c].update(bytes.fromhex(dig))
        total_rows += int(len(chunk))
        del chunk, tbl, ph
        try:
            pa.default_memory_pool().release_unused()
        except Exception:
            pass
        _guard(res_g)

    peak = int(res_g.get("peak_vmhwm_kb") or _vmhwm_kb())
    if total_rows == 0:
        return {"year": year, "rows": 0, "peak_vmhwm_kb": peak}
    ysch = {c: h.hexdigest() for c, h in col_hashes.items()}
    return {
        "year": year,
        "rows": int(total_rows),
        "year_sorted_content_col_hashes": ysch,
        "year_sorted_content_col_hashes_stub": h_keys.hexdigest(),
        "peak_vmhwm_kb": peak,
    }


__all__ = [
    "RAW_NAME_RE",
    "TRANSFORM_CONSTANTS",
    "DbIncrError",
    "DbIncrSignal",
    "compute_transform_sha",
    "runtime_versions",
    "materialize_daily_basic_incremental",
    "materialize_daily_basic_cli",
    "ref_build_year",
    "DB_INCR_STALE_TMP",
    "DB_INCR_TRANSFORM_CHANGED",
    "DB_INCR_SIGNAL_HUP",
    "DB_INCR_PRECOND",
    "DB_INCR_RAW_TMP",
]
