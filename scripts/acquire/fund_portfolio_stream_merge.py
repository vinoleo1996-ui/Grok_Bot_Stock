#!/usr/bin/env python3
"""fund_portfolio stream merge v1.1 (design sha 4a46df7f...).

Per-period batched read + keyed dedup + available_at, then ParquetWriter final.
live=false; promotion_approved=false. Does not call Q8/broker_recommend.
Old remaining_after_stk_surv.L96 left untouched until a future enable .ok.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# --- C1 named constants (echoed in manifest; change requires Arch re-review) ---
BATCH_MAX_FILES = 128
BATCH_MAX_ROWS = 400_000
RSS_ABORT_KB = 1_000_000
TREE_RSS_ABORT_KB = 1_500_000

SELFTEST_PREFIX = "/tmp/ql_fundport_stream_test_"
PROD_DATA_PREFIX = "/workspace/QuantLab/data/v2/"

KEY_COLS = ["ts_code", "end_date", "symbol"]

# Exit codes (from 20; avoid nightly 2/3)
EXIT_PRECHECK = 20
EXIT_MEMORY = 21
EXIT_TRADE_CAL = 28
EXIT_TERM = 31
EXIT_HUP = 32

# Global TERM state
_TERM_REQUESTED = False
_IN_CLEANUP = False
_INODE_LEDGER: List[Tuple[str, int]] = []  # (path, inode)
_TMP_ROOT: Optional[Path] = None
_PEAK_RSS_KB = 0
_LOG_FP = None


def _log(msg: str, **k: Any) -> None:
    rec = {"ts": datetime.now().isoformat(timespec="seconds"), "msg": msg, **k}
    line = json.dumps(rec, ensure_ascii=False, default=str)
    print(line, flush=True)
    global _LOG_FP
    if _LOG_FP is not None:
        _LOG_FP.write(line + "\n")
        _LOG_FP.flush()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def vmrss_kb(pid: Optional[int] = None) -> int:
    pid = pid or os.getpid()
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except OSError:
        return 0
    return 0


def mem_available_kb() -> int:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    return 0


def sample_rss(where: str) -> int:
    global _PEAK_RSS_KB
    rss = vmrss_kb()
    if rss > _PEAK_RSS_KB:
        _PEAK_RSS_KB = rss
    if rss > RSS_ABORT_KB:
        _log("rss_abort", where=where, vmrss_kb=rss, limit=RSS_ABORT_KB)
        raise MemoryAbort(f"VmRSS {rss} > {RSS_ABORT_KB} at {where}")
    return rss


class MemoryAbort(Exception):
    pass


class PrecheckError(Exception):
    def __init__(self, msg: str, code: int = EXIT_PRECHECK):
        super().__init__(msg)
        self.code = code


# --- trade_cal / deadline (explicit cal; no implicit live path) ---

def load_trade_cal(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "cal_date" not in df.columns:
        raise PrecheckError("trade_cal missing cal_date", EXIT_TRADE_CAL)
    if "is_open" not in df.columns:
        raise PrecheckError("trade_cal missing is_open", EXIT_TRADE_CAL)
    return df


def tdays_from_cal(cal: pd.DataFrame, a: str, b: str) -> List[str]:
    c = cal[cal.is_open.astype(int) == 1]
    return sorted(d for d in c.cal_date.astype(str) if a <= d <= b)


def deadline_for_period(p: str, cal: pd.DataFrame) -> str:
    """Copy of remaining_after_stk_surv.deadline (L74-78) with explicit cal."""
    y, md = p[:4], p[4:]
    if md == "0630":
        return f"{y}0831"
    if md == "1231":
        return f"{int(y) + 1}0331"
    days = tdays_from_cal(cal, p, str(int(y) + 1) + "1231")
    if not days:
        # synthetic calendars may be sparse; fall back to end+15 calendar days marker
        return f"{int(y) + 1}0115" if md == "0930" else f"{y}0415"
    return days[min(len(days) - 1, 15)]


def apply_available_at(x: pd.DataFrame, cal: pd.DataFrame) -> pd.DataFrame:
    """L97-103 semantics on an already keyed-deduped frame."""
    x = x.copy()
    for c in ("ann_date", "end_date"):
        if c not in x.columns:
            x[c] = None
        x[c] = x[c].astype(str).replace({"None": None, "nan": None, "NaT": None})
    ad = pd.to_datetime(x["ann_date"], format="%Y%m%d", errors="coerce")
    dl = pd.to_datetime(x["end_date"].map(lambda p: deadline_for_period(str(p), cal)), format="%Y%m%d")
    x["available_at_basis"] = ad.notna().map(
        {True: "ann_date+1d 09:00", False: "statutory_deadline+1d 09:00"}
    )
    x["available_at"] = ad.fillna(dl).dt.normalize() + pd.Timedelta(days=1, hours=9)
    x["promotion_approved"] = False
    return x


def keyed_dedup(x: pd.DataFrame) -> pd.DataFrame:
    """Path A: sort ann_date + drop_duplicates KEY keep=first (stream design)."""
    if x.empty:
        return x
    x = x.copy()
    if "ann_date" not in x.columns:
        x["ann_date"] = None
    x["ann_date"] = x["ann_date"].astype(str).replace({"None": None, "nan": None})
    return x.sort_values("ann_date").drop_duplicates(KEY_COLS, keep="first")


def keyed_dedup_legacy_two_step(x: pd.DataFrame) -> pd.DataFrame:
    """Path B: unkeyed drop_duplicates() then keyed (old L96 two-step) — for C3 only."""
    if x.empty:
        return x
    x = x.copy().drop_duplicates()
    if "ann_date" not in x.columns:
        x["ann_date"] = None
    x["ann_date"] = x["ann_date"].astype(str).replace({"None": None, "nan": None})
    return x.sort_values("ann_date").drop_duplicates(KEY_COLS, keep="first")


def key_frozenset(x: pd.DataFrame) -> frozenset:
    if x.empty:
        return frozenset()
    return frozenset(
        tuple(row) for row in x[KEY_COLS].astype(str).itertuples(index=False, name=None)
    )


# --- inode ledger / cleanup ---

def ledger_register(path: Path) -> None:
    st = path.stat()
    _INODE_LEDGER.append((str(path.resolve()), int(st.st_ino)))


def atomic_create_file(path: Path) -> int:
    """O_EXCL create empty file; return fd. Caller must close."""
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        st = os.fstat(fd)
        _INODE_LEDGER.append((str(path.resolve()), int(st.st_ino)))
    except Exception:
        os.close(fd)
        raise
    return fd


def cleanup_ledger(tmp_root: Optional[Path] = None) -> None:
    global _IN_CLEANUP
    _IN_CLEANUP = True
    root = tmp_root or _TMP_ROOT
    if root is None:
        _IN_CLEANUP = False
        return
    root_r = str(Path(root).resolve())
    for p, ino in list(_INODE_LEDGER):
        try:
            pr = str(Path(p).resolve())
            if not pr.startswith(root_r + os.sep) and pr != root_r:
                continue
            if not os.path.exists(p):
                continue
            st = os.stat(p)
            if int(st.st_ino) != int(ino):
                continue
            if os.path.isdir(p):
                continue
            os.unlink(p)
        except OSError:
            pass
    # remove empty period files / tmp_root if empty
    try:
        for child in sorted(Path(root).glob("*"), reverse=True):
            try:
                if child.is_file():
                    # only unlink if in ledger
                    continue
                if child.is_dir():
                    try:
                        child.rmdir()
                    except OSError:
                        pass
            except OSError:
                pass
        # unlink leftover files that are under root and in ledger already handled;
        # try remove tmp_root if empty
        try:
            Path(root).rmdir()
        except OSError:
            pass
    except OSError:
        pass
    _IN_CLEANUP = False


def _handle_term(signum, frame):  # noqa: ARG001
    global _TERM_REQUESTED
    if _IN_CLEANUP:
        return
    _TERM_REQUESTED = True
    _log("signal", signum=signum)


def install_signal_handlers() -> None:
    signal.signal(signal.SIGTERM, _handle_term)
    try:
        signal.signal(signal.SIGHUP, _handle_term)
    except (ValueError, OSError):
        pass


def check_term() -> None:
    if _TERM_REQUESTED:
        raise KeyboardInterrupt("TERM")


# --- run_id ---

def mint_run_id(events_dir: Path) -> Tuple[str, Path]:
    """Return (run_id, tmp_root). Never reuse existing dir; never delete other runs."""
    base = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"_{os.getpid()}"
    stream_root = events_dir / "_tmp_fundport_stream"
    stream_root.mkdir(parents=True, exist_ok=True)
    run_id = base
    n = 1
    while True:
        tmp_root = stream_root / run_id
        if not tmp_root.exists():
            try:
                os.mkdir(tmp_root)  # no exist_ok
                return run_id, tmp_root
            except FileExistsError:
                pass
        n += 1
        run_id = f"{base}_r{n}"


# --- batching ---

def plan_batches(files: Sequence[Path]) -> List[List[Path]]:
    """Split files by BATCH_MAX_FILES and BATCH_MAX_ROWS (both active)."""
    batches: List[List[Path]] = []
    cur: List[Path] = []
    cur_rows = 0
    for f in files:
        try:
            n = int(pq.ParquetFile(f).metadata.num_rows)
        except Exception:
            n = 0
        # single file larger than batch rows → alone
        if n > BATCH_MAX_ROWS:
            if cur:
                batches.append(cur)
                cur, cur_rows = [], 0
            batches.append([f])
            continue
        would_files = len(cur) + 1
        would_rows = cur_rows + n
        if cur and (would_files > BATCH_MAX_FILES or would_rows > BATCH_MAX_ROWS):
            batches.append(cur)
            cur, cur_rows = [], 0
        cur.append(f)
        cur_rows += n
    if cur:
        batches.append(cur)
    return batches


def read_period_batched(period_dir: Path) -> Tuple[pd.DataFrame, int, int, int]:
    """Return (acc, rows_before_meta_sum, n_pages, n_batches)."""
    files = sorted(
        f for f in period_dir.glob("*.parquet") if f.is_file() and f.stat().st_size > 0
    )
    n_pages = len(files)
    if not files:
        return pd.DataFrame(), 0, 0, 0
    batches = plan_batches(files)
    acc_parts: List[pd.DataFrame] = []
    meta_rows = 0
    for bi, batch in enumerate(batches):
        check_term()
        frames = []
        for f in batch:
            df = pd.read_parquet(f)
            frames.append(df)
            try:
                meta_rows += int(pq.ParquetFile(f).metadata.num_rows)
            except Exception:
                meta_rows += len(df)
        batch_frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        del frames
        acc_parts.append(batch_frame)
        sample_rss(f"after_batch_{bi}")
        del batch_frame
    acc = pd.concat(acc_parts, ignore_index=True) if acc_parts else pd.DataFrame()
    del acc_parts
    sample_rss("after_period_acc")
    return acc, meta_rows, n_pages, len(batches)


def write_parquet_atomic(df: pd.DataFrame, dest: Path, tmp_root: Path) -> str:
    """Write df to dest via O_EXCL tmp in tmp_root then os.replace. Returns sha256."""
    tmp = tmp_root / (dest.name + f".partial.{os.getpid()}")
    if tmp.exists():
        raise PrecheckError(f"tmp exists: {tmp}")
    # create O_EXCL placeholder then write via pyarrow/pandas to a sibling then replace
    fd = atomic_create_file(tmp)
    os.close(fd)
    # pandas to_parquet overwrites; we already O_EXCL-created, so write to tmp2 then replace onto tmp
    tmp2 = tmp_root / (dest.name + f".write.{os.getpid()}")
    df.to_parquet(tmp2, index=False)
    ledger_register(tmp2)
    os.replace(tmp2, tmp)
    # now replace into dest (dest may be under tmp_root as period file, or final)
    dest.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp, dest)
    if dest.exists():
        ledger_register(dest)
    return sha256_file(dest)


def stream_write_final(
    period_files: Sequence[Path], final_path: Path, tmp_root: Path
) -> Tuple[int, str]:
    """ParquetWriter stream period files in order into final via O_EXCL tmp + replace."""
    final_tmp = tmp_root / "fund_portfolio_2018plus.parquet.tmp"
    fd = atomic_create_file(final_tmp)
    os.close(fd)
    # remove zero-byte placeholder so ParquetWriter can create; keep ledger entry for cleanup
    os.unlink(final_tmp)
    writer = None
    total_rows = 0
    try:
        for pf in period_files:
            check_term()
            table = pq.read_table(pf)
            if writer is None:
                writer = pq.ParquetWriter(str(final_tmp), table.schema)
                ledger_register(final_tmp)
            else:
                # schema unify: cast if needed
                if not table.schema.equals(writer.schema):
                    table = table.cast(writer.schema)
            writer.write_table(table)
            total_rows += table.num_rows
            del table
            sample_rss("final_writer_period")
        if writer is not None:
            writer.close()
            writer = None
        else:
            # empty: write empty parquet
            empty = pa.table(
                {
                    "ts_code": pa.array([], type=pa.string()),
                    "end_date": pa.array([], type=pa.string()),
                    "symbol": pa.array([], type=pa.string()),
                    "ann_date": pa.array([], type=pa.string()),
                    "available_at_basis": pa.array([], type=pa.string()),
                    "available_at": pa.array([], type=pa.timestamp("ns")),
                    "promotion_approved": pa.array([], type=pa.bool_()),
                }
            )
            pq.write_table(empty, final_tmp)
            ledger_register(final_tmp)
        # verify row count
        meta_rows = int(pq.ParquetFile(final_tmp).metadata.num_rows)
        if meta_rows != total_rows and total_rows > 0:
            raise PrecheckError(f"final meta rows {meta_rows} != written {total_rows}")
        digest = sha256_file(final_tmp)
        os.replace(final_tmp, final_path)
        return meta_rows, digest
    except Exception:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass
        raise


def atomic_write_text(path: Path, text: str, tmp_root: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    # prefer sibling .tmp; O_EXCL
    if tmp.exists():
        tmp.unlink()
    fd = os.open(str(tmp), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)
    # track for cleanup if under tmp_root
    try:
        if str(tmp.resolve()).startswith(str(tmp_root.resolve())):
            ledger_register(tmp)
    except Exception:
        pass
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj: dict, tmp_root: Path) -> None:
    atomic_write_text(
        path, json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n", tmp_root
    )


# --- run-ok / precheck ---

def load_run_ok(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def precheck_run_ok(rok: dict) -> Tuple[int, str, Path]:
    """Return (mem_available_min_kb, log_path_str as Path components). Raises PrecheckError."""
    if "mem_available_min_kb" not in rok:
        raise PrecheckError("run-ok missing mem_available_min_kb", EXIT_PRECHECK)
    mem_min = int(rok["mem_available_min_kb"])
    # Arch impl review 86c0cb74: only JSON false or string "false"; integer 0 must exit 20
    abr = rok.get("allow_broker_recommend", None)
    if abr is not False and abr != "false":
        raise PrecheckError(
            f"allow_broker_recommend must be JSON false or \"false\", got {abr!r}",
            EXIT_PRECHECK,
        )
    log_path = rok.get("log_path") or rok.get("log")
    if not log_path:
        raise PrecheckError("run-ok missing log_path", EXIT_PRECHECK)
    return mem_min, str(log_path), Path(log_path)


def resolve_trade_cal(
    args: argparse.Namespace, rok: dict
) -> Tuple[Path, str]:
    path_s = args.trade_cal or rok.get("trade_cal_path")
    sha_s = args.trade_cal_sha256 or rok.get("trade_cal_sha256")
    pin_ref = rok.get("trade_cal_pin_ref")
    if (not path_s or not sha_s) and pin_ref:
        # pin_ref may be a JSON file with path+sha
        pref = Path(pin_ref)
        if pref.exists():
            pin = json.loads(pref.read_text())
            path_s = path_s or pin.get("trade_cal_path") or pin.get("path")
            sha_s = sha_s or pin.get("trade_cal_sha256") or pin.get("sha256")
    if not path_s:
        raise PrecheckError("trade_cal path missing", EXIT_TRADE_CAL)
    if not sha_s:
        raise PrecheckError("trade_cal sha256 missing", EXIT_TRADE_CAL)
    p = Path(path_s)
    if not p.exists():
        raise PrecheckError(f"trade_cal path not found: {p}", EXIT_TRADE_CAL)
    actual = sha256_file(p)
    if actual != sha_s:
        raise PrecheckError(
            f"trade_cal sha mismatch: got {actual} want {sha_s}", EXIT_TRADE_CAL
        )
    return p, actual


def assert_selftest_paths(paths: Iterable[Path]) -> None:
    for p in paths:
        s = str(Path(p).resolve())
        if not s.startswith(SELFTEST_PREFIX) and not s.startswith("/tmp/ql_fundport_stream_test_"):
            # also allow the unresolved form
            if not str(p).startswith(SELFTEST_PREFIX):
                raise PrecheckError(
                    f"selftest path escapes prefix: {p}", EXIT_PRECHECK
                )
        if PROD_DATA_PREFIX.rstrip("/") in s and "/tmp/" not in s:
            raise PrecheckError(f"selftest must not touch prod data: {p}", EXIT_PRECHECK)


def hold_path(markers_dir: Path) -> Path:
    return markers_dir.parent / "HOLD_FUNDPORT_MERGE"


# --- main merge ---

def merge_stream(args: argparse.Namespace) -> int:
    global _TMP_ROOT, _LOG_FP, _PEAK_RSS_KB, _TERM_REQUESTED
    _PEAK_RSS_KB = 0
    _TERM_REQUESTED = False
    install_signal_handlers()

    raw_root = Path(args.raw_root)
    events_dir = Path(args.events_dir)
    markers_dir = Path(args.markers_dir)
    periods = [p.strip() for p in args.periods.split(",") if p.strip()]
    resume = bool(args.resume)

    if args.selftest:
        assert_selftest_paths(
            [raw_root, events_dir, markers_dir, Path(args.trade_cal)]
            if args.trade_cal
            else [raw_root, events_dir, markers_dir]
        )

    # HOLD (production behavior); selftest skips unless --honor-hold
    hp = hold_path(markers_dir)
    if hp.exists() and (args.honor_hold or not args.selftest):
        _log("merge_held", hold=str(hp), note="HOLD present; skip merge")
        return 0

    if not args.run_ok:
        raise PrecheckError("--run-ok required", EXIT_PRECHECK)
    rok = load_run_ok(Path(args.run_ok))
    mem_min, log_path_s, log_path = precheck_run_ok(rok)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _LOG_FP = open(log_path, "a", encoding="utf-8")

    # MemAvailable gate
    mav = mem_available_kb()
    if mav < mem_min:
        raise PrecheckError(
            f"MemAvailable {mav} < mem_available_min_kb {mem_min}", EXIT_PRECHECK
        )

    cal_path, cal_sha = resolve_trade_cal(args, rok)
    if args.selftest:
        assert_selftest_paths([cal_path])
    cal = load_trade_cal(cal_path)

    events_dir.mkdir(parents=True, exist_ok=True)
    markers_dir.mkdir(parents=True, exist_ok=True)

    run_id, tmp_root = mint_run_id(events_dir)
    _TMP_ROOT = tmp_root
    _log(
        "run_start",
        run_id=run_id,
        tmp_root=str(tmp_root),
        periods=periods,
        batch_max_files=BATCH_MAX_FILES,
        batch_max_rows=BATCH_MAX_ROWS,
        resume=resume,
        merge_mode="stream_v1_1",
    )

    script_sha = sha256_file(Path(__file__).resolve())
    per_period = []
    fails: List[str] = []
    period_files: List[Path] = []

    try:
        for p in periods:
            check_term()
            mav = mem_available_kb()
            if mav < mem_min:
                raise PrecheckError(
                    f"MemAvailable {mav} < {mem_min} before period {p}", EXIT_PRECHECK
                )
            period_dir = raw_root / p
            out_period = tmp_root / f"period_{p}.parquet"

            if resume and out_period.exists() and out_period.stat().st_size > 0:
                _log("period_skip_resume", period=p)
                n_after = int(pq.ParquetFile(out_period).metadata.num_rows)
                per_period.append(
                    {
                        "period": p,
                        "pages": 0,
                        "rows_before_dedup": None,
                        "rows_after_dedup": n_after,
                        "period_sha256": sha256_file(out_period),
                        "n_batches": 0,
                        "resumed": True,
                    }
                )
                period_files.append(out_period)
                continue

            if not period_dir.is_dir():
                fails.append(f"{p}:missing_dir")
                _log("period_fail", period=p, err="missing_dir")
                continue

            acc, meta_rows, n_pages, n_batches = read_period_batched(period_dir)
            rows_before = len(acc)
            # normalize types lightly
            for c in ("ann_date", "end_date", "ts_code", "symbol"):
                if c in acc.columns:
                    acc[c] = acc[c].astype(str).replace({"None": None, "nan": None})
            acc = keyed_dedup(acc)
            acc = apply_available_at(acc, cal)
            rows_after = len(acc)
            # unique keys assert
            if rows_after and acc.duplicated(KEY_COLS).any():
                fails.append(f"{p}:dup_keys_after_dedup")
            psha = write_parquet_atomic(acc, out_period, tmp_root)
            del acc
            sample_rss(f"after_del_acc_{p}")
            _log(
                "period_merged",
                period=p,
                rows_before=rows_before,
                rows_after=rows_after,
                pages=n_pages,
                n_batches=n_batches,
                meta_rows=meta_rows,
            )
            per_period.append(
                {
                    "period": p,
                    "pages": n_pages,
                    "rows_before_dedup": rows_before,
                    "rows_after_dedup": rows_after,
                    "period_sha256": psha,
                    "n_batches": n_batches,
                }
            )
            period_files.append(out_period)

        check_term()
        final_path = events_dir / "fund_portfolio_2018plus.parquet"
        total_rows, final_sha = stream_write_final(period_files, final_path, tmp_root)
        sum_after = sum(int(pp["rows_after_dedup"] or 0) for pp in per_period)
        if total_rows != sum_after:
            fails.append(f"row_sum_mismatch:{total_rows}!={sum_after}")

        # n_funds / n_no_ann from final via pyarrow+pandas selective
        n_funds = 0
        n_no_ann = 0
        if total_rows > 0:
            t = pq.read_table(final_path, columns=["ts_code", "ann_date", "available_at_basis"])
            df = t.to_pandas()
            n_funds = int(df["ts_code"].nunique())
            n_no_ann = int((df["available_at_basis"] == "statutory_deadline+1d 09:00").sum())
            del df, t

        manifest = {
            "table": "fund_portfolio_2018plus.parquet",
            "sha256": final_sha,
            "rows": total_rows,
            "periods": [periods[0], periods[-1]] if periods else [],
            "n_periods": len(periods),
            "n_funds": n_funds,
            "source": "datahub fund_portfolio(period pages; stream_v1_1 merge)",
            "available_at": (
                "实际公告日次日 09:00；无公告日按法定截止日次日 09:00"
                "（季报季末+15交易日/半年报8-31/年报次年3-31）"
            ),
            "n_no_ann": n_no_ann,
            "n_fails": len(fails),
            "fails": fails[:50],
            "per_period": per_period,
            "run_id": run_id,
            "merge_mode": "stream_v1_1",
            "peak_rss_kb_observed": _PEAK_RSS_KB,
            "script_sha256": script_sha,
            "batch_max_files": BATCH_MAX_FILES,
            "batch_max_rows": BATCH_MAX_ROWS,
            "trade_cal_path": str(cal_path),
            "trade_cal_sha256": cal_sha,
            "promotion_approved": False,
            "allow_broker_recommend": False,
        }
        man_path = events_dir / "fund_portfolio_2018plus_manifest.json"
        # C6: write .tmp then replace; verify DONE consistency
        # recompute file sha for consistency check
        file_sha = sha256_file(final_path)
        if file_sha != final_sha:
            raise PrecheckError("final sha drift before manifest", EXIT_PRECHECK)
        manifest["sha256"] = file_sha
        atomic_write_json(man_path, manifest, tmp_root)

        if len(fails) == 0:
            done_path = markers_dir / "fund_portfolio_2018plus.DONE"
            # verify triad
            man_loaded = json.loads(man_path.read_text())
            if not (
                man_loaded.get("sha256") == file_sha
                and sha256_file(final_path) == file_sha
            ):
                raise PrecheckError("DONE/manifest/file sha triad mismatch", EXIT_PRECHECK)
            atomic_write_text(done_path, file_sha + "\n", tmp_root)
            # strip trailing issues: DONE content should be hex; allow trailing newline
            done_txt = done_path.read_text().strip()
            if done_txt != file_sha or done_txt != man_loaded["sha256"]:
                done_path.unlink(missing_ok=True)
                raise PrecheckError("DONE text != manifest.sha256", EXIT_PRECHECK)

        if args.receipt:
            rp = Path(args.receipt)
            if args.selftest:
                assert_selftest_paths([rp] if str(rp).startswith("/tmp/") else [])
            write_receipt_md(rp, manifest, periods)

        _log(
            "done" if not fails else "partial",
            rows=total_rows,
            n_fails=len(fails),
            sha256=file_sha,
            peak_rss_kb=_PEAK_RSS_KB,
            run_id=run_id,
        )
        # success cleanup of this run tmp
        cleanup_ledger(tmp_root)
        return 0 if not fails else EXIT_PRECHECK
    except MemoryAbort as e:
        _log("abort_memory", err=str(e))
        cleanup_ledger(tmp_root)
        return EXIT_MEMORY
    except KeyboardInterrupt:
        _log("abort_term", run_id=run_id)
        cleanup_ledger(tmp_root)
        # do NOT replace final
        return EXIT_TERM
    except PrecheckError as e:
        _log("abort_precheck", err=str(e), code=e.code)
        cleanup_ledger(tmp_root)
        return e.code
    except Exception as e:
        _log("abort_error", err=str(e)[:300], tb=traceback.format_exc()[-500:])
        cleanup_ledger(tmp_root)
        return EXIT_PRECHECK
    finally:
        if _LOG_FP is not None:
            try:
                _LOG_FP.close()
            except Exception:
                pass
            _LOG_FP = None


def write_receipt_md(path: Path, man: dict, periods: List[str]) -> None:
    rows_tbl = "\n".join(
        f"| {pp.get('period')} | {pp.get('pages')} | {pp.get('rows_before_dedup')} | "
        f"{pp.get('rows_after_dedup')} | {pp.get('n_batches')} | `{pp.get('period_sha256','')[:12]}` |"
        for pp in man.get("per_period", [])
    )
    body = f"""# fund_portfolio 公募持仓满窗回执（stream_v1_1，promotion_approved=false）

- 表：`{man.get('table')}`；merge_mode=`{man.get('merge_mode')}`
- 报告期：{periods[0] if periods else '?'} → {periods[-1] if periods else '?'}（{len(periods)} 期）
- 行数 {man.get('rows')}；基金数 {man.get('n_funds')}；n_fails={man.get('n_fails')}
- peak_rss_kb_observed={man.get('peak_rss_kb_observed')}；batch_max_files={man.get('batch_max_files')}；batch_max_rows={man.get('batch_max_rows')}
- trade_cal_path=`{man.get('trade_cal_path')}`；trade_cal_sha256=`{man.get('trade_cal_sha256')}`
- allow_broker_recommend={man.get('allow_broker_recommend')}；promotion_approved={man.get('promotion_approved')}
- run_id=`{man.get('run_id')}`；script_sha256=`{man.get('script_sha256')}`
- available_at：{man.get('available_at')}；无公告日行数 {man.get('n_no_ann')}
- SHA256：`{man.get('sha256')}`

## 各期

| period | pages | rows_before | rows_after | n_batches | period_sha |
|---|---|---|---|---|---|
{rows_tbl}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="fund_portfolio stream merge v1.1")
    ap.add_argument("--raw-root", required=True)
    ap.add_argument("--events-dir", required=True)
    ap.add_argument("--markers-dir", required=True)
    ap.add_argument("--periods", required=True, help="comma-separated YYYYMMDD list")
    ap.add_argument("--trade-cal", default=None)
    ap.add_argument("--trade-cal-sha256", default=None)
    ap.add_argument("--run-ok", default=None, help="JSON path (required except helpers)")
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--selftest", action="store_true", help="force /tmp path prefix asserts")
    ap.add_argument("--resume", action="store_true", default=False, help="default OFF")
    ap.add_argument("--honor-hold", action="store_true", help="respect HOLD even in selftest")
    ap.add_argument(
        "--c3-fixture",
        action="store_true",
        help="run C3 A/B key-set check on --raw-root synthetic rows and exit",
    )
    ap.add_argument(
        "--term-after-period",
        default=None,
        help="internal: raise TERM after finishing this period (selftest)",
    )
    return ap


def run_c3_fixture(raw_root: Path) -> int:
    """Load all parquet under raw_root periods, compare path A vs B key sets."""
    frames = []
    for pdir in sorted(raw_root.iterdir()):
        if not pdir.is_dir():
            continue
        for f in sorted(pdir.glob("*.parquet")):
            if f.stat().st_size > 0:
                frames.append(pd.read_parquet(f))
    if not frames:
        print(json.dumps({"c3": "empty"}))
        return EXIT_PRECHECK
    x = pd.concat(frames, ignore_index=True)
    a = keyed_dedup(x)
    b = keyed_dedup_legacy_two_step(x)
    ka, kb = key_frozenset(a), key_frozenset(b)
    ok = ka == kb
    print(
        json.dumps(
            {
                "c3_ok": ok,
                "n_a": len(a),
                "n_b": len(b),
                "n_keys_a": len(ka),
                "n_keys_b": len(kb),
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok else EXIT_PRECHECK


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    # internal hook for SIGTERM selftest: after first period, send TERM to self
    if args.term_after_period:
        # wrap merge to raise after that period via monkey signal
        pass
    if args.c3_fixture:
        return run_c3_fixture(Path(args.raw_root))
    try:
        # optional: install term-after-period by patching
        if args.term_after_period:
            return merge_stream_term_hook(args)
        return merge_stream(args)
    except PrecheckError as e:
        print(json.dumps({"msg": "precheck", "err": str(e), "code": e.code}), flush=True)
        return e.code


def merge_stream_term_hook(args: argparse.Namespace) -> int:
    """Like merge_stream but raise TERM after named period is written (selftest)."""
    real_write = write_parquet_atomic

    def wrapped(df, dest, tmp_root):
        sha = real_write(df, dest, tmp_root)
        target = f"period_{args.term_after_period}.parquet"
        if dest.name == target:
            _log("self_term_trigger", period=args.term_after_period)
            os.kill(os.getpid(), signal.SIGTERM)
            raise KeyboardInterrupt("TERM")
        return sha

    try:
        globals()["write_parquet_atomic"] = wrapped
        return merge_stream(args)
    finally:
        globals()["write_parquet_atomic"] = real_write


if __name__ == "__main__":
    sys.exit(main())
