#!/usr/bin/env python3
"""Materialize tier-1 authoritative tables from tushare_raw."""
import sys, os, json, time, pathlib, warnings, glob, shutil, hashlib
warnings.filterwarnings("ignore")
ROOT = pathlib.Path("/workspace/QuantLab"); sys.path.insert(0, str(ROOT))
import pandas as pd, numpy as np

RAW = ROOT / "data/v2/tushare_raw"
LOG = ROOT / "data/_acquire_logs"
DOC = ROOT / "docs/v2"

def to_iid(s):
    # 000001.SZ -> sz.000001
    out = []
    for x in s:
        x = str(x)
        if "." in x:
            code, ex = x.split(".", 1)
            out.append(f"{ex.lower()}.{code}")
        else:
            out.append(x.lower())
    return out

def materialize_bars(start="20260923", end="20261012"):
    """Flat PIT bars for Mac API + append into asof_extend_tushare panels."""
    days = sorted(p.stem for p in (RAW/"daily").glob("*.parquet") if start <= p.stem <= end)
    print("bars days", days, flush=True)
    frames = []
    for d in days:
        daily = pd.read_parquet(RAW/"daily"/f"{d}.parquet")
        if daily.empty: continue
        daily = daily.copy()
        daily["instrument_id"] = to_iid(daily.ts_code.astype(str))
        daily["trade_date"] = pd.to_datetime(daily.trade_date.astype(str))
        daily["open"] = pd.to_numeric(daily.open, errors="coerce")
        daily["high"] = pd.to_numeric(daily.high, errors="coerce")
        daily["low"] = pd.to_numeric(daily.low, errors="coerce")
        daily["close"] = pd.to_numeric(daily.close, errors="coerce")
        daily["pre_close"] = pd.to_numeric(daily.pre_close, errors="coerce")
        daily["volume"] = pd.to_numeric(daily.vol, errors="coerce") * 100.0  # 手→股
        daily["amount"] = pd.to_numeric(daily.amount, errors="coerce") * 1000.0  # 千元→元
        # adj
        af = RAW/"adj_factor"/f"{d}.parquet"
        if af.exists():
            a = pd.read_parquet(af)
            a["instrument_id"] = to_iid(a.ts_code.astype(str))
            a["trade_date"] = pd.to_datetime(a.trade_date.astype(str))
            a["adj_factor"] = pd.to_numeric(a.adj_factor, errors="coerce")
            daily = daily.merge(a[["instrument_id","trade_date","adj_factor"]], on=["instrument_id","trade_date"], how="left")
        else:
            daily["adj_factor"] = np.nan
        # limits
        lf = RAW/"stk_limit"/f"{d}.parquet"
        if lf.exists():
            L = pd.read_parquet(lf)
            L["instrument_id"] = to_iid(L.ts_code.astype(str))
            L["trade_date"] = pd.to_datetime(L.trade_date.astype(str))
            L = L.rename(columns={"up_limit":"limit_up","down_limit":"limit_down"})
            daily = daily.merge(L[["instrument_id","trade_date","limit_up","limit_down"]], on=["instrument_id","trade_date"], how="left")
        else:
            daily["limit_up"] = np.nan; daily["limit_down"] = np.nan
        # suspend
        daily["tradestatus"] = 1
        sf = RAW/"suspend_d"/f"{d}.parquet"
        if sf.exists():
            S = pd.read_parquet(sf)
            if len(S):
                S["instrument_id"] = to_iid(S.ts_code.astype(str))
                S["trade_date"] = pd.to_datetime(S.trade_date.astype(str))
                sus = set(zip(S.instrument_id, S.trade_date))
                mask = [((i,t) in sus) for i,t in zip(daily.instrument_id, daily.trade_date)]
                daily.loc[mask, "tradestatus"] = 0
        # available_at = trade_date 16:00 Asia/Shanghai (post close; bars known)
        daily["available_at"] = daily.trade_date + pd.Timedelta(hours=16)
        daily["available_at"] = daily["available_at"].dt.tz_localize("Asia/Shanghai")
        daily["source"] = "tushare.daily+adj+limit+suspend(datahub)"
        daily["quality_status"] = "research"
        daily["promotion_approved"] = False
        daily["price_basis"] = "raw_unadjusted"
        daily["volume_unit"] = "share"
        daily["amount_unit"] = "CNY"
        cols = ["ts_code","instrument_id","trade_date","open","high","low","close","pre_close",
                "volume","amount","adj_factor","limit_up","limit_down","tradestatus",
                "available_at","price_basis","volume_unit","amount_unit","source","quality_status","promotion_approved"]
        frames.append(daily[cols])
    bars = pd.concat(frames, ignore_index=True)
    out = ROOT/"data/v2/bars"; out.mkdir(parents=True, exist_ok=True)
    dest = out/"daily_ohlcv_raw_pit.parquet"
    # merge with existing if present and overlapping window
    if dest.exists():
        old = pd.read_parquet(dest)
        old["trade_date"] = pd.to_datetime(old.trade_date)
        keep = old[~old.trade_date.isin(set(bars.trade_date.unique()))]
        bars = pd.concat([keep, bars], ignore_index=True)
    bars = bars.sort_values(["trade_date","instrument_id"]).reset_index(drop=True)
    tmp = dest.with_suffix(".tmp.parquet"); bars.to_parquet(tmp, index=False); os.replace(tmp, dest)
    meta = {
        "path": str(dest),
        "rows": len(bars),
        "instruments": int(bars.instrument_id.nunique()),
        "date_min": str(bars.trade_date.min())[:10],
        "date_max": str(bars.trade_date.max())[:10],
        "available_at_rule": "available_at = trade_date 16:00 Asia/Shanghai (post close). Join asof on available_at; do NOT use naked trade_date for same-session open signals.",
        "price_basis": "raw unadjusted OHLCV; adj_factor separate column (Tushare adj_factor)",
        "units": {"volume":"share (vol手*100)", "amount":"CNY (千元*1000)"},
        "promotion_approved": False,
        "includes_delisted": "yes if present in daily that day",
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "schema": "quantlab.v2.bars.daily_ohlcv_raw_pit.v1",
    }
    (out/"daily_ohlcv_raw_pit_manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("BARS", meta, flush=True)

    # Incremental append into asof_extend_tushare panels for new days only
    panel_dir = ROOT/"data/v2/asof_extend_tushare_202610/panels"
    panel_dir.mkdir(parents=True, exist_ok=True)
    # Only append days > existing panel max if possible; here append all bars window rows
    n_upd = 0
    for iid, g in bars.groupby("instrument_id"):
        destp = panel_dir / f"{iid}.parquet"
        g2 = g.copy()
        g2["turnover"] = np.nan
        g2["quality_status"] = "research_tushare"
        g2["is_st_at_open"] = False
        g2["source"] = "tushare_leo"
        # available_at naive for panel compat (existing panels use naive)
        g2["available_at"] = pd.to_datetime(g2.trade_date) + pd.Timedelta(hours=16)
        cols = ["trade_date","open","high","low","close","volume","amount","turnover","limit_up","limit_down",
                "tradestatus","available_at","quality_status","is_st_at_open","source","adj_factor"]
        g2 = g2.rename(columns={"adj_factor":"adj_factor_tushare"})
        cols2 = ["trade_date","open","high","low","close","volume","amount","turnover","limit_up","limit_down",
                "tradestatus","available_at","quality_status","is_st_at_open","source","adj_factor_tushare"]
        for c in cols2:
            if c not in g2.columns: g2[c] = np.nan
        piece = g2[cols2]
        if destp.exists():
            old = pd.read_parquet(destp)
            old["trade_date"] = pd.to_datetime(old.trade_date)
            # drop overlapping dates then concat
            old = old[~old.trade_date.isin(set(piece.trade_date))]
            # align columns
            for c in cols2:
                if c not in old.columns: old[c] = np.nan
            merged = pd.concat([old[cols2], piece], ignore_index=True).sort_values("trade_date")
        else:
            merged = piece.sort_values("trade_date")
        merged.to_parquet(destp, index=False)
        n_upd += 1
        if n_upd % 500 == 0:
            print("panels upd", n_upd, flush=True)
    # update manifest date
    man = ROOT/"data/v2/asof_extend_tushare_202610/manifest.json"
    try:
        m = json.loads(man.read_text())
    except Exception:
        m = {}
    m["as_of_extended"] = str(bars.trade_date.max())[:10]
    m["tier1_extend_note"] = f"appended/refreshed {start}->{end} via tier1; promotion_approved unchanged for overall"
    m["n_panels_written"] = len(list(panel_dir.glob("*.parquet")))
    man.write_text(json.dumps(m, indent=2, ensure_ascii=False))
    print("panels updated", n_upd, flush=True)
    return meta

def _daily_basic_val_cols():
    return ["close","turnover_rate","turnover_rate_f","volume_ratio","pe","pe_ttm","pb","ps","ps_ttm",
            "dv_ttm","total_share","float_share","free_share","total_mv","float_mktcap"]

# --- C4: hoist former materialize_daily_basic._one closure to module level (design v3.1 §2.7b) ---
def transform_daily_basic_one(f):
    """Per-file transform for daily_basic (module-level; shared by full + incremental + ref_build)."""
    x = pd.read_parquet(f)
    if x.empty:
        return None
    y = pd.DataFrame({
        "ts_code": x.ts_code.astype(str),
        "instrument_id": to_iid(x.ts_code.astype(str)),
        "trade_date": pd.to_datetime(x.trade_date.astype(str)),
        "close": pd.to_numeric(x.get("close"), errors="coerce"),
        "turnover_rate": pd.to_numeric(x.get("turnover_rate"), errors="coerce"),
        "turnover_rate_f": pd.to_numeric(x.get("turnover_rate_f"), errors="coerce"),
        "volume_ratio": pd.to_numeric(x.get("volume_ratio"), errors="coerce"),
        "pe": pd.to_numeric(x.get("pe"), errors="coerce"),
        "pe_ttm": pd.to_numeric(x.get("pe_ttm"), errors="coerce"),
        "pb": pd.to_numeric(x.get("pb"), errors="coerce"),
        "ps": pd.to_numeric(x.get("ps"), errors="coerce"),
        "ps_ttm": pd.to_numeric(x.get("ps_ttm"), errors="coerce"),
        "dv_ttm": pd.to_numeric(x.get("dv_ttm"), errors="coerce"),
        "total_share": pd.to_numeric(x.get("total_share"), errors="coerce"),
        "float_share": pd.to_numeric(x.get("float_share"), errors="coerce"),
        "free_share": pd.to_numeric(x.get("free_share"), errors="coerce"),
        "total_mv": pd.to_numeric(x.get("total_mv"), errors="coerce") * 10000.0,  # 万元→元
        "float_mktcap": pd.to_numeric(x.get("circ_mv"), errors="coerce") * 10000.0,
    })
    # available_at: trade_date 18:00 Asia/Shanghai (existing valuation convention)
    y["available_at"] = y.trade_date + pd.Timedelta(hours=18)
    y["available_at"] = y["available_at"].dt.tz_localize("Asia/Shanghai")
    y["source"] = "tushare.daily_basic"
    y["quality_status"] = "research"
    y["promotion_approved"] = False
    # Raw slices on some dates (e.g. 20231024) contain the same ts_code twice
    # (paged re-pull appended); keep the later copy, matching prior full table.
    y = y.drop_duplicates(["ts_code", "trade_date"], keep="last").reset_index(drop=True)
    return y

def _prune_daily_basic_backups(bak_dir, keep=5):
    if os.environ.get("QL_DAILY_BASIC_NO_PRUNE") == "1":
        kept = [p.name for p in sorted(bak_dir.glob("daily_basic_full_tushare.*.parquet"), key=lambda p: p.name)]
        return [], kept
    existing = sorted(bak_dir.glob("daily_basic_full_tushare.*.parquet"), key=lambda p: p.name)
    removed = []
    for p in existing[:-keep]:
        p.unlink(missing_ok=True); removed.append(p.name)
    kept = [p.name for p in sorted(bak_dir.glob("daily_basic_full_tushare.*.parquet"), key=lambda p: p.name)]
    return removed, kept

def _compare_daily_basic_history(old_df, new_df):
    """Count differing rows on overlapping old trade_dates (key=ts_code,trade_date)."""
    key = ["ts_code","trade_date"]
    vals = [c for c in _daily_basic_val_cols() if c in old_df.columns and c in new_df.columns]
    old = old_df[key + vals].copy()
    new = new_df[key + vals].copy()
    for nm, df in (("old", old), ("new", new)):
        nd = int(df.duplicated(key).sum())
        if nd:
            raise ValueError(f"_compare_daily_basic_history: {nm} has {nd} duplicate (ts_code,trade_date) keys")
    old["trade_date"] = pd.to_datetime(old["trade_date"])
    new["trade_date"] = pd.to_datetime(new["trade_date"])
    overlap = set(old["trade_date"].unique()) & set(new["trade_date"].unique())
    if not overlap:
        return 0
    old = old[old["trade_date"].isin(overlap)]
    new = new[new["trade_date"].isin(overlap)]
    m = old.merge(new, on=key, how="outer", suffixes=("_o","_n"), indicator=True)
    side = m["_merge"] != "both"
    both = m.loc[~side]
    if len(both):
        mism = pd.Series(False, index=both.index)
        for c in vals:
            a, b = both[f"{c}_o"], both[f"{c}_n"]
            mism = mism | ((a != b) & ~(a.isna() & b.isna()))
        return int(side.sum() + mism.sum())
    return int(side.sum())

def _compare_daily_basic_files(old_path, new_path):
    """Compare backup vs new by calendar year to keep peak RAM low."""
    cols = ["ts_code", "trade_date"] + _daily_basic_val_cols()
    old_td = pd.read_parquet(old_path, columns=["trade_date"])
    old_td["trade_date"] = pd.to_datetime(old_td["trade_date"])
    years = sorted(int(y) for y in old_td["trade_date"].dt.year.unique())
    del old_td
    diff = 0
    # Year via parquet filters only; whole-table fallback REMOVED (design v3.1 §2.1 / L99).
    # Filter failure → raise (do not read entire old/new into RAM).
    for y in years:
        y0 = pd.Timestamp(f"{y}-01-01")
        y1 = pd.Timestamp(f"{y}-12-31 23:59:59")
        filt = [("trade_date", ">=", y0), ("trade_date", "<=", y1)]
        try:
            old = pd.read_parquet(old_path, columns=cols, filters=filt)
            new = pd.read_parquet(new_path, columns=cols, filters=filt)
        except Exception as e:
            raise RuntimeError(
                f"daily_basic history_diff year={y}: parquet filter failed; "
                f"whole-table fallback banned (design §2.1): {e}"
            ) from e
        old["trade_date"] = pd.to_datetime(old["trade_date"])
        new["trade_date"] = pd.to_datetime(new["trade_date"])
        d = _compare_daily_basic_history(old, new)
        diff += d
        del old, new
        print(f"  history_diff year={y} cumulative={diff}", flush=True)
    return int(diff)

def _patch_daily_basic_status(acc, history_diff_rows, backup_path=None):
    """Merge tables.daily_basic.history_diff_rows into output/daily_update_status.json."""
    status = ROOT/"output/daily_update_status.json"
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        finished = datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    except Exception:
        finished = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    st = json.loads(status.read_text()) if status.exists() else {
        "schema": "quantlab.v2.daily_update_status.v1", "tables": {}, "errors": {},
        "promotion_approved": False, "live": False,
    }
    t = st.setdefault("tables", {}).setdefault("daily_basic", {})
    dest = pathlib.Path(acc["path"])
    sha = None
    if dest.exists():
        h = hashlib.sha256()
        with open(dest, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        sha = h.hexdigest()
    t.update({
        "path": acc["path"],
        "last_date": str(acc.get("date_max", ""))[:10],
        "rows": acc.get("rows"),
        "sha256": sha,
        "history_diff_rows": history_diff_rows,
        "finished_at": finished,
    })
    if backup_path is not None:
        t["backup_path"] = str(backup_path)
    status.parent.mkdir(parents=True, exist_ok=True)
    tmp = status.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=2))
    os.replace(tmp, status)
    return t

def materialize_daily_basic(start="20140101", end="20261012", dry_run=False):
    """Rebuild daily_basic_full_tushare.parquet from raw day files (FULL path).
    Before rewrite: copy existing dest to backups/valuation/daily_basic_full_tushare.<YYYYMMDD_HHMM>.parquet (keep 5).
    After rewrite: compare overlapping old trade_dates vs backup; write tables.daily_basic.history_diff_rows.
    Year-batched to keep peak RAM low.
    Gate (design v3.1 §2.1): requires QL_DB_ALLOW_FULL=1. Production incremental path
    must NOT set this env (banned in BANNED_ENVS_INCR). Full path needs separate Arch .ok.
    """
    if os.environ.get("QL_DB_ALLOW_FULL") != "1":
        raise RuntimeError(
            "materialize_daily_basic (full) requires QL_DB_ALLOW_FULL=1 "
            "(design v3.1 §2.1); use materialize_daily_basic_cli --mode incremental for nightly"
        )
    files = sorted(p for p in (RAW/"daily_basic").glob("*.parquet") if start <= p.stem <= end)
    print("daily_basic files", len(files), files[0].stem if files else None, files[-1].stem if files else None, flush=True)
    out = ROOT/"data/v2/valuation"; out.mkdir(parents=True, exist_ok=True)
    dest = out/"daily_basic_full_tushare.parquet"
    bak_dir = ROOT/"backups/valuation"; bak_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M")
    bak = bak_dir / f"daily_basic_full_tushare.{stamp}.parquet"
    if dry_run:
        existing = sorted(bak_dir.glob("daily_basic_full_tushare.*.parquet"), key=lambda p: p.name)
        would_have = existing + ([bak] if dest.exists() else [])
        would_remove = [p.name for p in would_have[:-5]] if len(would_have) > 5 else []
        print("DRY_RUN backup", str(dest), "->", str(bak), "dest_exists", dest.exists(), flush=True)
        print("DRY_RUN existing_backups", [p.name for p in existing], "would_remove_after", would_remove, flush=True)
        print("DRY_RUN rebuild start", start, "end", end, "n_files", len(files), flush=True)
        print("DRY_RUN skip copy/rebuild/compare/status write", flush=True)
        return {"dry_run": True, "backup_would_be": str(bak), "n_files": len(files),
                "dest_exists": dest.exists(), "existing_backups": [p.name for p in existing]}

    backup_path = None
    if dest.exists():
        shutil.copy2(dest, bak)
        backup_path = bak
        removed, kept = _prune_daily_basic_backups(bak_dir, keep=5)
        print("BACKUP", str(bak), "removed", removed, "kept", kept, flush=True)

    # C4: use module-level transform_daily_basic_one (former nested _one)
    _one = transform_daily_basic_one

    import pyarrow.parquet as pq
    parts_dir = out / f"_daily_basic_parts_{stamp}"
    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    parts_dir.mkdir(parents=True, exist_ok=True)
    by_year = {}
    for f in files:
        by_year.setdefault(f.stem[:4], []).append(f)
    part_paths = []
    n_rows = 0
    instruments = set()
    date_min = date_max = None
    for yr in sorted(by_year):
        chunk = []
        for f in by_year[yr]:
            y = _one(f)
            if y is None:
                continue
            chunk.append(y)
        if not chunk:
            continue
        m = pd.concat(chunk, ignore_index=True)
        del chunk
        m = m.drop_duplicates(["ts_code", "trade_date"], keep="last").reset_index(drop=True)
        n_rows += len(m)
        instruments.update(m.instrument_id.astype(str).unique().tolist())
        d0, d1 = m.trade_date.min(), m.trade_date.max()
        date_min = d0 if date_min is None or d0 < date_min else date_min
        date_max = d1 if date_max is None or d1 > date_max else date_max
        pp = parts_dir / f"y{yr}.parquet"
        m.to_parquet(pp, index=False)
        del m
        part_paths.append(pp)
        print(f"  year {yr} -> {pp.name} running_rows={n_rows}", flush=True)
    if not part_paths:
        shutil.rmtree(parts_dir, ignore_errors=True)
        raise RuntimeError("no daily_basic rows materialized")
    schema = pq.read_schema(part_paths[0])
    tmp = dest.with_suffix(".tmp.parquet")
    with pq.ParquetWriter(tmp, schema=schema, compression="snappy") as w:
        for pp in part_paths:
            w.write_table(pq.read_table(pp))
    os.replace(tmp, dest)
    shutil.rmtree(parts_dir, ignore_errors=True)

    history_diff_rows = None
    if backup_path is not None and backup_path.exists():
        history_diff_rows = _compare_daily_basic_files(backup_path, dest)
        print("HISTORY_DIFF_ROWS", history_diff_rows, flush=True)

    acc = {
        "path": str(dest),
        "rows": int(n_rows),
        "instruments": int(len(instruments)),
        "date_min": str(date_min)[:10],
        "date_max": str(date_max)[:10],
        "available_at_rule": "available_at = trade_date 18:00 Asia/Shanghai. Tushare daily_basic updates same trade day ~15:00–17:00; 18:00 conservative. asof on available_at; NOT naked trade_date for open signals.",
        "priority_cols": ["turnover_rate_f","volume_ratio"],
        "promotion_approved": False,
        "note": "pb/ps/dv as vendor; Leo prefers recomputing valuation from financials_pit+price for features",
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "schema": "quantlab.v2.daily_basic_full_tushare.v1",
        "history_diff_rows": history_diff_rows,
        "backup_path": str(backup_path) if backup_path is not None else None,
    }
    # Atomic manifest write (design v3.1 §2.1): tmp + os.replace
    _man = out / "daily_basic_full_tushare_manifest.json"
    _man_tmp = pathlib.Path(str(_man) + ".tmp")
    _man_tmp.write_text(json.dumps(acc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(_man_tmp, _man)
    _patch_daily_basic_status(acc, history_diff_rows, backup_path)
    print("DAILY_BASIC", acc, flush=True)
    return acc

def materialize_index():
    files = list((RAW/"index_daily").glob("*.parquet"))
    if not files:
        print("no index_daily raw", flush=True); return None
    parts = []
    for f in files:
        x = pd.read_parquet(f)
        if x.empty: continue
        x = x.copy()
        x["trade_date"] = pd.to_datetime(x.trade_date.astype(str))
        for c in ["open","high","low","close","pre_close","change","pct_chg","vol","amount"]:
            if c in x.columns: x[c] = pd.to_numeric(x[c], errors="coerce")
        x["available_at"] = x.trade_date + pd.Timedelta(hours=16)
        x["available_at"] = x["available_at"].dt.tz_localize("Asia/Shanghai")
        x["source"] = "tushare.index_daily"
        x["quality_status"] = "research"
        x["promotion_approved"] = False
        parts.append(x)
    m = pd.concat(parts, ignore_index=True).drop_duplicates(["ts_code","trade_date"])
    out = ROOT/"data/v2/index"; out.mkdir(parents=True, exist_ok=True)
    dest = out/"index_daily_pit.parquet"
    m.to_parquet(dest, index=False)
    # per-code convenience
    for code, g in m.groupby("ts_code"):
        g.to_parquet(out / f"index_daily_{code.replace('.','_')}.parquet", index=False)
    meta = {
        "path": str(dest),
        "codes": sorted(m.ts_code.unique().tolist()),
        "rows": len(m),
        "date_min": str(m.trade_date.min())[:10],
        "date_max": str(m.trade_date.max())[:10],
        "available_at_rule": "trade_date 16:00 Asia/Shanghai",
        "promotion_approved": False,
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (out/"index_daily_pit_manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("INDEX", meta, flush=True)
    return meta

def materialize_stock_basic():
    parts = []
    for st in ("L","D","P"):
        f = RAW/"stock_basic"/f"{st}.parquet"
        if f.exists() and f.stat().st_size > 0:
            parts.append(pd.read_parquet(f))
    if not parts:
        print("no stock_basic", flush=True); return None
    m = pd.concat(parts, ignore_index=True)
    m["instrument_id"] = to_iid(m.ts_code.astype(str))
    m["list_date"] = pd.to_datetime(m.list_date.astype(str), errors="coerce")
    if "delist_date" in m.columns:
        m["delist_date"] = pd.to_datetime(m.delist_date.astype(str), errors="coerce")
    m["available_at"] = pd.Timestamp("1970-01-01", tz="Asia/Shanghai")  # static meta; always historically known once listed
    m["available_at_rule"] = "static reference; filter by list_date/delist_date for universe"
    m["source"] = "tushare.stock_basic"
    m["quality_status"] = "research"
    m["promotion_approved"] = False
    out = ROOT/"data/v2/meta"; out.mkdir(parents=True, exist_ok=True)
    dest = out/"stock_basic_incl_delisted.parquet"
    m.to_parquet(dest, index=False)
    meta = {
        "path": str(dest),
        "rows": len(m),
        "by_status": m.list_status.value_counts().to_dict() if "list_status" in m.columns else {},
        "list_date_min": str(m.list_date.min())[:10],
        "promotion_approved": False,
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (out/"stock_basic_incl_delisted_manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("STOCK_BASIC", meta, flush=True)
    return meta

def audit_financials_versions():
    f = ROOT/"data/v2/financials_pit/financials_pit_tushare.parquet"
    df = pd.read_parquet(f, columns=["ts_code","end_date","ann_date","f_ann_date","report_type","update_flag","available_at"])
    g = df.groupby(["ts_code","end_date"]).size()
    multi = (g>1).mean()
    # update_flag distribution
    uf = df.update_flag.astype(str).value_counts().to_dict()
    conclusion = (
        f"existing financials_pit_tushare KEEPS multiple versions per (ts_code,end_date): "
        f"multi-row fraction={multi:.3f}, max_versions={int(g.max())}, update_flag_counts={uf}. "
        f"Income+fina_indicator join; raw+revised rows retained via update_flag/report_type."
    )
    print(conclusion, flush=True)
    return conclusion, {"multi_frac": float(multi), "max_versions": int(g.max()), "update_flag": uf}

def materialize_bs_cf_pit():
    """Build balancesheet+cashflow PIT keeping all update_flag/report_type versions."""
    bs_files = list((RAW/"balancesheet").glob("*.parquet"))
    cf_files = list((RAW/"cashflow").glob("*.parquet"))
    print("bs files", len(bs_files), "cf files", len(cf_files), flush=True)
    bs_parts = []
    for f in bs_files:
        x = pd.read_parquet(f)
        if x.empty: continue
        bs_parts.append(x)
    cf_parts = []
    for f in cf_files:
        x = pd.read_parquet(f)
        if x.empty: continue
        # keep key cols
        cols = [c for c in ["ts_code","ann_date","f_ann_date","end_date","report_type","comp_type","update_flag","n_cashflow_act","net_profit"] if c in x.columns]
        cf_parts.append(x[cols])
    if not bs_parts and not cf_parts:
        print("no bs/cf", flush=True); return None
    out_rows = None
    meta = {}
    if bs_parts:
        bs = pd.concat(bs_parts, ignore_index=True)
        bs["instrument_id"] = to_iid(bs.ts_code.astype(str))
        for c in ["report_type","comp_type","update_flag"]:
            if c in bs.columns: bs[c] = bs[c].astype(str).replace({"nan":None,"None":None,"":None})
        for c in ["ann_date","f_ann_date","end_date"]:
            bs[c] = pd.to_datetime(bs[c].astype(str), errors="coerce")
        ad = bs["f_ann_date"].fillna(bs["ann_date"])
        bs["available_at"] = ad + pd.Timedelta(hours=18)
        bs["available_at"] = bs["available_at"].dt.tz_localize("Asia/Shanghai")
        # rename equity
        if "total_hldr_eqy_exc_min_int" in bs.columns:
            bs["equity_parent"] = pd.to_numeric(bs["total_hldr_eqy_exc_min_int"], errors="coerce")
        for c in ["total_assets","total_liab"]:
            if c in bs.columns: bs[c] = pd.to_numeric(bs[c], errors="coerce")
        bs["source"] = "tushare.balancesheet"
        bs["quality_status"] = "research"
        bs["promotion_approved"] = False
        bs["schema"] = "quantlab.v2.balancesheet_pit.v1"
        dest = ROOT/"data/v2/financials_pit/balancesheet_pit_tushare.parquet"
        bs.to_parquet(dest, index=False)
        # version audit
        g = bs.groupby(["ts_code","end_date"]).size()
        meta["balancesheet"] = {
            "path": str(dest),
            "rows": len(bs),
            "instruments": int(bs.instrument_id.nunique()),
            "end_date_min": str(bs.end_date.min())[:10],
            "end_date_max": str(bs.end_date.max())[:10],
            "ann_min": str(bs.ann_date.min())[:10],
            "ann_max": str(bs.ann_date.max())[:10],
            "multi_version_frac": float((g>1).mean()),
            "max_versions": int(g.max()),
            "available_at_rule": "coalesce(f_ann_date,ann_date) 18:00 Asia/Shanghai; all update_flag/report_type versions kept",
            "promotion_approved": False,
        }
        print("BS", meta["balancesheet"], flush=True)
    if cf_parts:
        cf = pd.concat(cf_parts, ignore_index=True)
        cf["instrument_id"] = to_iid(cf.ts_code.astype(str))
        for c in ["report_type","comp_type","update_flag"]:
            if c in cf.columns: cf[c] = cf[c].astype(str).replace({"nan":None,"None":None,"":None})
        for c in ["ann_date","f_ann_date","end_date"]:
            cf[c] = pd.to_datetime(cf[c].astype(str), errors="coerce")
        ad = cf["f_ann_date"].fillna(cf["ann_date"])
        cf["available_at"] = ad + pd.Timedelta(hours=18)
        cf["available_at"] = cf["available_at"].dt.tz_localize("Asia/Shanghai")
        cf["n_cashflow_act"] = pd.to_numeric(cf.get("n_cashflow_act"), errors="coerce")
        cf["source"] = "tushare.cashflow"
        cf["quality_status"] = "research"
        cf["promotion_approved"] = False
        cf["schema"] = "quantlab.v2.cashflow_pit.v1"
        dest = ROOT/"data/v2/financials_pit/cashflow_pit_tushare.parquet"
        cf.to_parquet(dest, index=False)
        g = cf.groupby(["ts_code","end_date"]).size()
        meta["cashflow"] = {
            "path": str(dest),
            "rows": len(cf),
            "instruments": int(cf.instrument_id.nunique()),
            "end_date_min": str(cf.end_date.min())[:10],
            "end_date_max": str(cf.end_date.max())[:10],
            "ann_min": str(cf.ann_date.min())[:10],
            "ann_max": str(cf.ann_date.max())[:10],
            "multi_version_frac": float((g>1).mean()),
            "max_versions": int(g.max()),
            "available_at_rule": "coalesce(f_ann_date,ann_date) 18:00 Asia/Shanghai; all versions kept",
            "promotion_approved": False,
        }
        print("CF", meta["cashflow"], flush=True)
    # combined thin view for Leo's required fields
    if bs_parts and cf_parts:
        bs = pd.read_parquet(ROOT/"data/v2/financials_pit/balancesheet_pit_tushare.parquet")
        cf = pd.read_parquet(ROOT/"data/v2/financials_pit/cashflow_pit_tushare.parquet")
        # merge on ts_code,end_date,report_type,update_flag when possible
        keys = ["ts_code","end_date","report_type","update_flag"]
        for k in keys:
            if k not in bs.columns or k not in cf.columns:
                keys = ["ts_code","end_date"]
                break
        merged = bs.merge(
            cf[keys + [c for c in ["n_cashflow_act","ann_date","f_ann_date","available_at"] if c in cf.columns]].rename(
                columns={"ann_date":"cf_ann_date","f_ann_date":"cf_f_ann_date","available_at":"cf_available_at"}
            ),
            on=keys, how="outer"
        )
        # available_at = max of bs/cf
        if "available_at" in merged.columns and "cf_available_at" in merged.columns:
            merged["available_at"] = merged[["available_at","cf_available_at"]].max(axis=1)
        keep = [c for c in ["ts_code","instrument_id","end_date","ann_date","f_ann_date","report_type","update_flag",
                            "total_assets","total_liab","equity_parent","n_cashflow_act","available_at","source"] if c in merged.columns]
        thin = merged[keep].copy()
        thin["source"] = "tushare.balancesheet+cashflow"
        thin["promotion_approved"] = False
        dest = ROOT/"data/v2/financials_pit/bs_cf_pit_tushare.parquet"
        thin.to_parquet(dest, index=False)
        meta["bs_cf_combined"] = {"path": str(dest), "rows": len(thin), "promotion_approved": False}
        print("BS_CF", meta["bs_cf_combined"], flush=True)
    (ROOT/"data/v2/financials_pit/bs_cf_pit_manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str))
    return meta

# --- daily_basic incremental API (design v3.1); enable requires Arch .ok ---
# Enable-pack: full path gated by QL_DB_ALLOW_FULL; atomic manifest; no whole-table fallback.
# Do NOT edit f99dd11a; new driver filename pins post-change tier1 sha (§6.1).
try:
    from daily_basic_incremental import (  # noqa: E402
        materialize_daily_basic_incremental,
        materialize_daily_basic_cli,
        compute_transform_sha,
        runtime_versions,
        ref_build_year,
        RAW_NAME_RE,
        TRANSFORM_CONSTANTS,
    )
except ImportError:
    import importlib.util as _ilu
    _p = pathlib.Path(__file__).resolve().parent / "daily_basic_incremental.py"
    _spec = _ilu.spec_from_file_location("daily_basic_incremental", _p)
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    materialize_daily_basic_incremental = _mod.materialize_daily_basic_incremental
    materialize_daily_basic_cli = _mod.materialize_daily_basic_cli
    compute_transform_sha = _mod.compute_transform_sha
    runtime_versions = _mod.runtime_versions
    ref_build_year = _mod.ref_build_year
    RAW_NAME_RE = _mod.RAW_NAME_RE
    TRANSFORM_CONSTANTS = _mod.TRANSFORM_CONSTANTS


if __name__ == "__main__":
    args = sys.argv[1:]
    job = args[0] if args else "all"
    dry = "--dry-run" in args
    end = None
    if "--end" in args:
        end = args[args.index("--end") + 1]
    if job in ("bars","all"):
        materialize_bars()
    if job in ("daily_basic","all_db"):
        if "--mode" in args and args[args.index("--mode") + 1] == "incremental":
            # Pass through full argv after job token for materialize_daily_basic_cli
            cli_argv = args[1:] if job in args[:1] or True else args
            # When invoked as: tier1_materialize.py daily_basic --mode incremental ...
            idx = args.index("daily_basic") if "daily_basic" in args else 0
            raise SystemExit(materialize_daily_basic_cli(args[idx + 1:]))
        kw = {}
        if end: kw["end"] = end
        if dry: kw["dry_run"] = True
        materialize_daily_basic(**kw)
    if job in ("index",):
        materialize_index()
    if job in ("stock_basic",):
        materialize_stock_basic()
    if job in ("bs_cf",):
        materialize_bs_cf_pit()
    if job in ("audit_fin",):
        audit_financials_versions()
