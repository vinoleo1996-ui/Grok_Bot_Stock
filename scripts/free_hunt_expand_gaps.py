#!/usr/bin/env python3
"""Free-only gap expansion: re-derive float from asof_extend, page EM EITIME, broaden CNInfo, light ex-rights.
Does NOT write asof_extend panels (enrich_asof_curl owns those).
promotion_approved=false always.
"""
from __future__ import annotations
import hashlib, json, random, subprocess, time, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = Path("/workspace/QuantLab")
NY = ZoneInfo("America/New_York")
SH = ZoneInfo("Asia/Shanghai")
NOW = datetime.now(NY)
PANELS = ROOT / "data/v2/asof_extend_202610/panels"
FH = ROOT / "data/v2/free_hunt"
MKTCAP = FH / "mktcap"
FUND = FH / "fundamentals"
LOG = FH / "logs"
CA = ROOT / "data/v2/corporate_actions"
FIN_PIT = ROOT / "data/v2/financials_pit"
OUT_D1 = ROOT / "output/d1"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def curl_json(url: str, method: str = "GET", data: str | None = None, timeout: int = 40) -> dict:
    cmd = ["curl", "-sS", "-m", str(timeout), "--http1.1", "-A", UA, "-e", "https://data.eastmoney.com/"]
    if method == "POST":
        cmd += ["-X", "POST", "-H", "Content-Type: application/x-www-form-urlencoded"]
        if data:
            cmd += ["--data", data]
    cmd.append(url)
    last = None
    for attempt in range(5):
        proc = subprocess.run(cmd, capture_output=True)
        if proc.returncode == 0 and (proc.stdout or b"").strip():
            try:
                return json.loads(proc.stdout)
            except Exception as e:
                last = repr(e)
        else:
            last = (proc.stderr or b"").decode(errors="replace")[:200] or f"rc={proc.returncode}"
        time.sleep(1.5 * (attempt + 1) + random.random())
    raise RuntimeError(f"curl_fail:{last}")

# ---------- 1) float_mktcap_from_asof_extend ----------
def rederive_float_from_asof_extend() -> dict:
    MKTCAP.mkdir(parents=True, exist_ok=True)
    rows = []
    skip = 0
    for path in sorted(PANELS.glob("*.parquet")):
        try:
            df = pd.read_parquet(path)
        except Exception:
            skip += 1
            continue
        need = {"amount", "turnover", "event_time"}
        if not need.issubset(df.columns):
            skip += 1
            continue
        if df["amount"].notna().mean() < 0.5 or df["turnover"].notna().mean() < 0.5:
            skip += 1
            continue
        iid = path.stem
        close_col = "close" if "close" in df.columns else None
        for _, r in df.iterrows():
            amt, turn = r.get("amount"), r.get("turnover")
            if pd.isna(amt) or pd.isna(turn) or float(turn) <= 0:
                continue
            # turnover ALWAYS percent for A-shares
            fm = float(amt) * 100.0 / float(turn)
            rows.append(dict(
                instrument_id=iid,
                session=pd.Timestamp(r["event_time"]).date(),
                close=float(r[close_col]) if close_col and pd.notna(r[close_col]) else np.nan,
                amount=float(amt),
                turnover_pct=float(turn),
                float_mktcap=fm,
                method="amount*100/turnover_pct",
                source="asof_extend_panels_em_enriched",
                promotion_approved=False,
                quality_status="research_not_promotable:derived_proxy_not_official_float",
            ))
    out = MKTCAP / "float_mktcap_from_asof_extend.parquet"
    if not rows:
        meta = dict(promotion_approved=False, built_at=NOW.isoformat(), rows=0, panels_with_amount_turnover=0,
                    panels_skip=skip, note="no enriched panels yet")
        (MKTCAP / "float_mktcap_from_asof_extend_manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
        return meta
    fdf = pd.DataFrame(rows)
    fdf = fdf.drop_duplicates(["instrument_id", "session"], keep="last")
    fdf.to_parquet(out, index=False)
    # compare vs primary daily where overlap
    daily_p = ROOT / "data/v2/float_mktcap/float_mktcap_daily_20260630_20261009.parquet"
    vs = {}
    if daily_p.exists():
        d = pd.read_parquet(daily_p)
        d["session"] = pd.to_datetime(d["session"]).dt.date
        m = fdf.merge(d[["instrument_id", "session", "float_mktcap"]].rename(columns={"float_mktcap": "fm_data"}),
                      on=["instrument_id", "session"], how="inner")
        if len(m):
            rel = (m["float_mktcap"] - m["fm_data"]).abs() / m["fm_data"].abs().clip(lower=1.0)
            vs = dict(n=int(len(m)), within_1pct=float((rel <= 0.01).mean()),
                      within_5pct=float((rel <= 0.05).mean()),
                      median_abs_rel=float(rel.median()))
    meta = dict(
        schema_version="quantlab.v2.free_hunt.float_mktcap_from_asof_extend.v3",
        promotion_approved=False,
        built_at=NOW.isoformat(),
        path=str(out),
        rule="turnover ALWAYS treated as percent",
        panels_with_amount_turnover=int(fdf["instrument_id"].nunique()),
        panels_skip=skip,
        rows=int(len(fdf)),
        n_instruments=int(fdf["instrument_id"].nunique()),
        session_min=str(fdf["session"].min()),
        session_max=str(fdf["session"].max()),
        median_names_per_session=float(fdf.groupby("session")["instrument_id"].nunique().median()),
        vs_data_daily=vs,
        sha256=sha256_file(out),
        coverage_gap_note="Only panels with amount+turnover >=50% fill; climbs with enrich_asof_curl",
    )
    (MKTCAP / "float_mktcap_from_asof_extend_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"float_from_asof": {k: meta[k] for k in ["rows", "n_instruments", "vs_data_daily"]}}), flush=True)
    return meta

# ---------- 2) EM RPT_LICO_FN_CPD paging ----------
def page_em_yjbb(max_pages: int = 250, page_size: int = 50, start_page: int = 1) -> dict:
    FUND.mkdir(parents=True, exist_ok=True)
    all_rows = []
    pages_ok = 0
    pages_fail = 0
    total_pages = None
    for page in range(start_page, start_page + max_pages):
        filt = "(NOTICE_DATE<='2026-06-30')(SECURITY_TYPE=\"A股\")"
        qs = urllib.parse.urlencode({
            "sortColumns": "NOTICE_DATE,SECURITY_CODE",
            "sortTypes": "-1,-1",
            "pageSize": str(page_size),
            "pageNumber": str(page),
            "reportName": "RPT_LICO_FN_CPD",
            "columns": "ALL",
            "filter": filt,
        })
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get?" + qs
        try:
            payload = curl_json(url)
            result = payload.get("result") or {}
            if total_pages is None:
                total_pages = result.get("pages")
            data = result.get("data") or []
            if not data:
                pages_fail += 1
                if pages_fail >= 5:
                    break
                continue
            for item in data:
                code = str(item.get("SECURITY_CODE") or "")
                secu = str(item.get("SECUCODE") or "")
                mkt = "sh"
                if secu.endswith(".SZ"):
                    mkt = "sz"
                elif secu.endswith(".BJ") or code.startswith(("8", "4")):
                    mkt = "bj"
                elif secu.endswith(".SH"):
                    mkt = "sh"
                eitime = item.get("EITIME")
                notice = item.get("NOTICE_DATE")
                available_at = None
                src = None
                if eitime:
                    try:
                        available_at = pd.Timestamp(eitime).tz_localize(SH).isoformat()
                        src = "EITIME"
                    except Exception:
                        available_at = None
                if available_at is None and notice:
                    try:
                        available_at = pd.Timestamp(notice).tz_localize(SH).replace(hour=18).isoformat()
                        src = "NOTICE_DATE@18:00"
                    except Exception:
                        pass
                all_rows.append(dict(
                    instrument_id=f"{mkt}.{code}",
                    code=code,
                    name=item.get("SECURITY_NAME_ABBR"),
                    report_period=item.get("REPORTDATE"),
                    announced_on=notice,
                    eitime=eitime,
                    available_at=available_at,
                    available_at_source=src,
                    net_profit_parent=item.get("PARENT_NETPROFIT"),
                    basic_eps=item.get("BASIC_EPS"),
                    revenue=item.get("TOTAL_OPERATE_INCOME"),
                    roe=item.get("WEIGHTAVG_ROE"),
                    qdate=item.get("QDATE"),
                    source="eastmoney_RPT_LICO_FN_CPD",
                    promotion_approved=False,
                    quality_status="research_proxy_eitimes_or_notice_not_as_filed",
                ))
            pages_ok += 1
            if page % 20 == 0 or page == start_page:
                print(json.dumps({"em_page": page, "pages_ok": pages_ok, "rows": len(all_rows),
                                  "total_pages": total_pages}), flush=True)
            # soft checkpoint every 50 pages
            if page % 50 == 0 and all_rows:
                _write_em_artifacts(all_rows, pages_ok, total_pages, partial=True)
            time.sleep(0.55 + random.random() * 0.35)
        except Exception as e:
            pages_fail += 1
            print(json.dumps({"em_page_fail": page, "err": repr(e)[:160]}), flush=True)
            time.sleep(3 + random.random() * 2)
            if pages_fail >= 15:
                break
    meta = _write_em_artifacts(all_rows, pages_ok, total_pages, partial=False)
    meta["pages_fail"] = pages_fail
    meta["start_page"] = start_page
    meta["max_pages_requested"] = max_pages
    return meta

def _write_em_artifacts(all_rows, pages_ok, total_pages, partial: bool) -> dict:
    if not all_rows:
        return dict(promotion_approved=False, rows=0, pages_ok=pages_ok)
    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(["instrument_id", "report_period", "announced_on", "eitime"], keep="last")
    # merge with prior seed if expanding
    prior = FUND / "em_yjbb_pit_seed_notice_le_20260630.parquet"
    if prior.exists():
        old = pd.read_parquet(prior)
        df = pd.concat([old, df], ignore_index=True)
        df = df.drop_duplicates(["instrument_id", "report_period", "announced_on", "eitime"], keep="last")
    seed_path = FUND / "em_yjbb_pit_seed_notice_le_20260630.parquet"
    df.to_parquet(seed_path, index=False)
    # also 2024plus slice
    df2 = df.copy()
    df2["_rp"] = pd.to_datetime(df2["report_period"], errors="coerce")
    plus = df2[df2["_rp"] >= "2024-01-01"].drop(columns=["_rp"])
    plus_path = FUND / "em_yjbb_pit_seed_2024plus.parquet"
    plus.to_parquet(plus_path, index=False)
    # EP research: latest report per name with notice<=2026-06-30, join float asof 2026-06-30
    asof_fm = ROOT / "data/v2/float_mktcap/float_mktcap_asof_2026-06-30.parquet"
    ep_rows = []
    if asof_fm.exists():
        fm = pd.read_parquet(asof_fm)
        fm = fm[fm["float_mktcap"].notna()][["instrument_id", "float_mktcap"]]
        work = df.copy()
        work["announced_on_dt"] = pd.to_datetime(work["announced_on"], errors="coerce")
        work = work[work["announced_on_dt"] <= "2026-06-30"]
        work = work.sort_values(["instrument_id", "announced_on_dt", "report_period"]).drop_duplicates(
            "instrument_id", keep="last")
        m = work.merge(fm, on="instrument_id", how="inner")
        for _, r in m.iterrows():
            np_ = r.get("net_profit_parent")
            fmv = r.get("float_mktcap")
            if pd.isna(np_) or pd.isna(fmv) or float(fmv) <= 0:
                continue
            ep = float(np_) / float(fmv)
            ep_rows.append(dict(
                instrument_id=r["instrument_id"],
                asof_session="2026-06-30",
                ep=ep,
                net_profit_parent=float(np_),
                float_mktcap=float(fmv),
                report_period=r.get("report_period"),
                available_at=r.get("available_at"),
                available_at_source=r.get("available_at_source"),
                source="em_yjbb_period_profit_over_float_mktcap_proxy",
                promotion_approved=False,
                quality_status="research_not_promotable:period_profit_not_ttm",
            ))
    ep_path = FUND / "ep_from_em_yjbb_asof_20260630.parquet"
    ep_df = pd.DataFrame(ep_rows)
    if len(ep_df):
        ep_df.to_parquet(ep_path, index=False)
    # sync secondary research copies into financials_pit (do NOT touch primary)
    for src, dst_name in [
        (seed_path, "research_em_yjbb_pit_seed_notice_le_20260630.parquet"),
        (plus_path, "research_em_yjbb_pit_seed_2024plus.parquet"),
        (ep_path, "research_ep_from_em_yjbb_asof_20260630.parquet"),
    ]:
        if src.exists():
            FIN_PIT.mkdir(parents=True, exist_ok=True)
            pd.read_parquet(src).to_parquet(FIN_PIT / dst_name, index=False)
    sane = ep_df[(ep_df["ep"] > -1) & (ep_df["ep"] < 1)] if len(ep_df) else ep_df
    meta = dict(
        schema_version="quantlab.v2.free_hunt.em_yjbb_pit.v3",
        promotion_approved=False,
        built_at=NOW.isoformat(),
        path=str(seed_path),
        ep_path=str(ep_path) if ep_path.exists() else None,
        rows=int(len(df)),
        n_instruments=int(df["instrument_id"].nunique()),
        eitime_nonnull=int(df["eitime"].notna().sum()),
        announced_on_nonnull=int(df["announced_on"].notna().sum()),
        ep_rows=int(len(ep_df)),
        ep_sane_neg1_1=int(len(sane)),
        ep_median_sane=float(sane["ep"].median()) if len(sane) else None,
        available_at_source_counts=df["available_at_source"].value_counts(dropna=False).to_dict(),
        pages_ok=pages_ok,
        total_pages_reported=total_pages,
        partial_checkpoint=partial,
        sha256=sha256_file(seed_path),
        limitations=[
            "EITIME is EM ingest time — not exchange filing clock",
            "No restatement value chain",
            "Period profit not TTM",
            "promotion_approved=false",
            "A-share filter; paging incomplete until pages_ok≈total",
        ],
    )
    # vs data EP if present
    data_ep = FIN_PIT / "ep_research_asof_20260630.parquet"
    if data_ep.exists() and len(ep_df):
        dep = pd.read_parquet(data_ep)
        col = "ep" if "ep" in dep.columns else ("EP" if "EP" in dep.columns else None)
        if col:
            mm = ep_df.merge(dep[["instrument_id", col]].rename(columns={col: "ep_data"}), on="instrument_id")
            if len(mm) >= 10:
                corr = float(mm["ep"].corr(mm["ep_data"]))
                rel = (mm["ep"] - mm["ep_data"]).abs() / mm["ep_data"].abs().clip(lower=1e-12)
                meta["vs_data_ep"] = dict(n=int(len(mm)), corr=corr,
                                         median_abs_rel=float(rel.median()))
    (FUND / "em_yjbb_pit_manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str) + "\n")
    sec_manifest = dict(
        promotion_approved=False,
        updated_at=NOW.isoformat(),
        role="SECONDARY research only — do not overwrite financials_available_at.parquet",
        primary_available_at=str(FIN_PIT / "financials_available_at.parquet"),
        primary_ep_research=str(FIN_PIT / "ep_research_asof_20260630.parquet"),
        secondary_em_yjbb_eitimeseed=str(FIN_PIT / "research_em_yjbb_pit_seed_notice_le_20260630.parquet"),
        secondary_ep_em_yjbb=str(FIN_PIT / "research_ep_from_em_yjbb_asof_20260630.parquet"),
        secondary_em_yjbb_2024plus=str(FIN_PIT / "research_em_yjbb_pit_seed_2024plus.parquet"),
        secondary_cninfo_sample=str(FIN_PIT / "research_cninfo_periodic_announcements_sample.parquet"),
        free_hunt_source_dir=str(FUND),
        em_rows=int(len(df)),
        em_instruments=int(df["instrument_id"].nunique()),
        limitations=meta["limitations"],
    )
    (FIN_PIT / "research_free_hunt_secondary_manifest.json").write_text(
        json.dumps(sec_manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"em_write": {"rows": len(df), "n_instruments": int(df["instrument_id"].nunique()),
                                   "ep_rows": int(len(ep_df)), "partial": partial}}), flush=True)
    return meta

# ---------- 3) CNInfo broader sample ----------
def broaden_cninfo(n_names: int = 40) -> dict:
    FUND.mkdir(parents=True, exist_ok=True)
    # pick names from EM seed + liquid SH/SZ
    seed = FUND / "em_yjbb_pit_seed_notice_le_20260630.parquet"
    codes = []
    if seed.exists():
        s = pd.read_parquet(seed)
        codes = list(s["instrument_id"].dropna().astype(str).unique())
    # prioritize liquid
    prefer = ["sh.600519", "sh.601318", "sh.600036", "sz.000001", "sz.000858",
              "sh.600000", "sz.000002", "sh.601166", "sz.300750", "sh.688981",
              "sz.002594", "sh.601012", "sz.000063", "sh.600276", "sz.002415"]
    ordered = []
    for c in prefer + codes:
        if c not in ordered and c.startswith(("sh.", "sz.", "bj.")):
            ordered.append(c)
    ordered = ordered[:n_names]
    # orgId map
    org_map = {}
    try:
        payload = curl_json("https://www.cninfo.com.cn/new/data/szse_stock.json", timeout=60)
        # sometimes returns list under stockList
        items = payload if isinstance(payload, list) else payload.get("stockList") or payload.get("data") or []
        for it in items:
            code = str(it.get("code") or it.get("zwjc") or "")
            org = str(it.get("orgId") or "")
            if code and org:
                org_map[code] = org
    except Exception as e:
        print(json.dumps({"cninfo_orgmap_fail": repr(e)[:160]}), flush=True)
    rows = []
    ok = fail = 0
    for iid in ordered:
        code = iid.split(".", 1)[1]
        org = org_map.get(code) or (f"gssz{code}" if iid.startswith("sz.") else f"gssh{code}")
        column = "szse" if not iid.startswith("sh.") else "sse"
        data = urllib.parse.urlencode({
            "pageNum": "1",
            "pageSize": "30",
            "column": column,
            "tabName": "fulltext",
            "plate": "",
            "stock": f"{code},{org}",
            "searchkey": "",
            "secid": "",
            "category": "category_ndbg_szsh;category_bndbg_szsh;category_yjdbg_szsh;category_sjdbg_szsh",
            "trade": "",
            "seDate": "2024-01-01~2026-10-09",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        })
        try:
            # POST to cninfo
            cmd = ["curl", "-sS", "-m", "35", "--http1.1", "-A", UA,
                   "-e", "https://www.cninfo.com.cn/new/disclosure",
                   "-H", "Content-Type: application/x-www-form-urlencoded",
                   "-X", "POST", "--data", data,
                   "https://www.cninfo.com.cn/new/hisAnnouncement/query"]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode != 0 or not (proc.stdout or b"").strip():
                fail += 1
                time.sleep(1.2)
                continue
            payload = json.loads(proc.stdout)
            anns = payload.get("announcements") or []
            for a in anns:
                ts = a.get("announcementTime")
                try:
                    # ms epoch or already date
                    if isinstance(ts, (int, float)):
                        at = datetime.fromtimestamp(ts / 1000.0, tz=SH)
                        ts_ms = int(ts)
                    else:
                        at = pd.Timestamp(ts).tz_localize(SH)
                        ts_ms = int(at.timestamp() * 1000)
                except Exception:
                    continue
                rows.append(dict(
                    instrument_id=iid,
                    code=code,
                    title=a.get("announcementTitle"),
                    announcement_id=str(a.get("announcementId") or ""),
                    announcement_time_ms=ts_ms,
                    announcement_time=at.isoformat(),
                    adjunct_url=a.get("adjunctUrl"),
                    source="cninfo_hisAnnouncement",
                    promotion_approved=False,
                    quality_status="research_cninfo_announcement_clock",
                ))
            ok += 1
            time.sleep(0.7 + random.random() * 0.4)
        except Exception as e:
            fail += 1
            print(json.dumps({"cninfo_fail": iid, "err": repr(e)[:120]}), flush=True)
            time.sleep(1.5)
    out = FUND / "cninfo_periodic_announcements_sample.parquet"
    cdf = pd.DataFrame(rows)
    if len(cdf):
        # merge prior sample
        if out.exists():
            old = pd.read_parquet(out)
            cdf = pd.concat([old, cdf], ignore_index=True)
            cdf = cdf.drop_duplicates(["instrument_id", "announcement_id"], keep="last")
        cdf.to_parquet(out, index=False)
        FIN_PIT.mkdir(parents=True, exist_ok=True)
        cdf.to_parquet(FIN_PIT / "research_cninfo_periodic_announcements_sample.parquet", index=False)
    # same-day joins vs EM
    joins = 0
    em_p = FUND / "em_yjbb_pit_seed_notice_le_20260630.parquet"
    if em_p.exists() and len(cdf):
        em = pd.read_parquet(em_p)
        em["d"] = pd.to_datetime(em["announced_on"], errors="coerce").dt.date
        cdf2 = cdf.copy()
        cdf2["d"] = pd.to_datetime(cdf2["announcement_time"], errors="coerce").dt.date
        j = cdf2.merge(em[["instrument_id", "d"]], on=["instrument_id", "d"], how="inner")
        joins = int(len(j))
    meta = dict(
        schema_version="quantlab.v2.free_hunt.cninfo_announcements.v2",
        promotion_approved=False,
        built_at=NOW.isoformat(),
        path=str(out),
        rows=int(len(cdf)),
        n_instruments=int(cdf["instrument_id"].nunique()) if len(cdf) else 0,
        names_requested=len(ordered),
        names_ok=ok,
        names_fail=fail,
        same_day_joins_vs_em_yjbb=joins,
        note="CNInfo announcementTime; often date-level midnight — exchange disclosure clock candidate",
        limitations=[
            "Broader sample still not full-market",
            "Title matching not applied — date join only",
            "promotion_approved=false",
        ],
        sha256=sha256_file(out) if out.exists() else None,
    )
    (FUND / "cninfo_periodic_announcements_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cninfo": meta}), flush=True)
    return meta

# ---------- 4) Ex-rights light improve ----------
def improve_exrights() -> dict:
    """Free improvement: near-date (±3d) fill proposals + ACK unexplained coverage; optional EM dividend page for only_1c85 sample."""
    CA.mkdir(parents=True, exist_ok=True)
    only_1c85_p = CA / "exrights_only_in_1c85_2024plus.parquet"
    only_em_p = CA / "exrights_only_in_eastmoney_2024plus.parquet"
    if not only_1c85_p.exists() or not only_em_p.exists():
        return dict(promotion_approved=False, note="missing prior reconcile artifacts")
    a = pd.read_parquet(only_1c85_p)
    b = pd.read_parquet(only_em_p)
    # normalize date columns
    def pick_date(df):
        for c in ["ex_date", "exDate", "date", "event_date", "EX_DATE"]:
            if c in df.columns:
                return c
        return None
    def pick_id(df):
        for c in ["instrument_id", "code", "SECURITY_CODE"]:
            if c in df.columns:
                return c
        return None
    ida, idb = pick_id(a), pick_id(b)
    da, db = pick_date(a), pick_date(b)
    proposals = []
    if ida and idb and da and db:
        aa = a.copy(); bb = b.copy()
        aa["_id"] = aa[ida].astype(str)
        bb["_id"] = bb[idb].astype(str)
        # if bb ids are bare codes, map
        if not aa["_id"].str.contains(r"\.").any() and bb["_id"].str.contains(r"\.").any():
            pass
        aa["_d"] = pd.to_datetime(aa[da], errors="coerce")
        bb["_d"] = pd.to_datetime(bb[db], errors="coerce")
        # near-date ±3d within same instrument
        for iid, g in aa.groupby("_id"):
            cand = bb[bb["_id"].str.endswith(iid.split(".")[-1]) | (bb["_id"] == iid)]
            if cand.empty:
                continue
            for _, r in g.iterrows():
                if pd.isna(r["_d"]):
                    continue
                delta = (cand["_d"] - r["_d"]).abs().dt.days
                hit = cand.loc[delta <= 3]
                if hit.empty:
                    continue
                best = hit.iloc[(hit["_d"] - r["_d"]).abs().dt.days.argmin()]
                proposals.append(dict(
                    instrument_id=iid,
                    date_1c85=str(r["_d"].date()),
                    date_em=str(best["_d"].date()),
                    day_delta=int(abs((best["_d"] - r["_d"]).days)),
                    source="near_date_pm3_proposal",
                    promotion_approved=False,
                    quality_status="research_proposal_not_ledger_patch",
                ))
    prop_df = pd.DataFrame(proposals).drop_duplicates() if proposals else pd.DataFrame()
    prop_path = CA / "exrights_near_date_fills_proposed.parquet"
    if len(prop_df):
        # merge prior proposals
        if prop_path.exists():
            old = pd.read_parquet(prop_path)
            prop_df = pd.concat([old, prop_df], ignore_index=True).drop_duplicates(
                subset=[c for c in ["instrument_id", "date_1c85", "date_em"] if c in prop_df.columns], keep="last")
        prop_df.to_parquet(prop_path, index=False)
    # refresh report numbers
    report = dict(
        fetch_time=NOW.isoformat(),
        promotion_approved=False,
        window="ex_date>=2024-01-01",
        near_date_fills_proposed=int(len(prop_df)),
        only_1c85=int(len(a)),
        only_eastmoney=int(len(b)),
        paths=dict(
            near_date_fills=str(prop_path),
            only_1c85=str(only_1c85_p),
            only_eastmoney=str(only_em_p),
        ),
        limitations=[
            "Research-grade reconciliation only — does not auto-patch 1c85 actions ledger",
            "Near-date fills (±3d) are proposals, not confirmed identity",
            "promotion_approved=false; accounting_gaps remain",
            "No free full official CA ledger found this pass",
        ],
        improvement_note="Recomputed ±3d near-date proposals; ledger still not closed",
    )
    # preserve prior intersection stats if present
    old_rep = CA / "exrights_reconcile_report.json"
    if old_rep.exists():
        try:
            prev = json.loads(old_rep.read_text())
            for k in ["1c85_actions_keys", "eastmoney_keys", "intersection_exact",
                      "unexplained_ex_rows_found", "coverage_unexplained_ex_reference_rows_sum",
                      "coverage_instruments_with_unexplained"]:
                if k in prev:
                    report[k] = prev[k]
        except Exception:
            pass
    (CA / "exrights_reconcile_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"exrights": {k: report[k] for k in ["near_date_fills_proposed", "only_1c85", "only_eastmoney"]}}), flush=True)
    return report

def main():
    LOG.mkdir(parents=True, exist_ok=True)
    summary = {"started": NOW.isoformat(), "promotion_approved": False}
    print(json.dumps({"phase": "float_rederive"}), flush=True)
    summary["float_from_asof"] = rederive_float_from_asof_extend()
    print(json.dumps({"phase": "em_paging"}), flush=True)
    # expand: prior was ~60 pages; pull 250 more pages from page 1 (dedupe merges)
    summary["em_yjbb"] = page_em_yjbb(max_pages=250, page_size=50, start_page=1)
    print(json.dumps({"phase": "cninfo"}), flush=True)
    summary["cninfo"] = broaden_cninfo(n_names=40)
    print(json.dumps({"phase": "exrights"}), flush=True)
    summary["exrights"] = improve_exrights()
    summary["finished"] = datetime.now(NY).isoformat()
    (LOG / f"expand_gaps_{NOW.strftime('%Y%m%d_%H%M%S')}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n")
    (LOG / "expand_gaps_latest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n")
    print(json.dumps({"done": True, "summary_keys": list(summary.keys())}), flush=True)

if __name__ == "__main__":
    main()
