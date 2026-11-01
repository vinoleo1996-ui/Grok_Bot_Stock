#!/usr/bin/env python3
"""Build QuantLab data download + acceptance dashboard.

Reads logs under data/_acquire_logs/, parquet manifests, PROMOTION_ACCEPTANCE.md.
Writes:
  output/d1/data_progress.json
  output/d1/data_progress.html  (self-contained, meta refresh 15s)
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path("/workspace/QuantLab")
LOGS = ROOT / "data" / "_acquire_logs"
V2 = ROOT / "data" / "v2"
OUT_DIR = ROOT / "output" / "d1"
JSON_OUT = OUT_DIR / "data_progress.json"
HTML_OUT = OUT_DIR / "data_progress.html"
PROMO_MD = ROOT / "docs" / "v2" / "PROMOTION_ACCEPTANCE.md"

PROGRESS_RE = re.compile(
    r"(?P<label>extend|db_hist|fin|div)\s+(?P<done>\d+)\s*/\s*(?P<total>\d+)\s+fail\s+(?P<fail>\d+)",
    re.I,
)
TS_RE = re.compile(r"^(\d{2}:\d{2}:\d{2})\s+")


def now_et_iso() -> str:
    # box clock is America/New_York
    return datetime.now().astimezone().isoformat(timespec="seconds")


def file_mtime(p: Path) -> Optional[str]:
    if not p.exists():
        return None
    return datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat(timespec="seconds")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_progress_log(path: Path, job_id: str) -> Dict[str, Any]:
    """Parse last matching progress line from a text log."""
    out: Dict[str, Any] = {
        "id": job_id,
        "log": str(path),
        "exists": path.exists(),
        "mtime": file_mtime(path),
        "done": None,
        "total": None,
        "fail": None,
        "pct": None,
        "last_line": None,
        "status": "missing",
    }
    if not path.exists():
        return out
    lines = [ln.strip() for ln in read_text(path).splitlines() if ln.strip()]
    if not lines:
        out["status"] = "empty"
        return out
    out["last_line"] = lines[-1]
    matched = None
    for ln in reversed(lines):
        m = PROGRESS_RE.search(ln)
        if m:
            matched = m
            break
    if matched:
        done = int(matched.group("done"))
        total = int(matched.group("total"))
        fail = int(matched.group("fail"))
        out.update(
            {
                "done": done,
                "total": total,
                "fail": fail,
                "pct": round(100.0 * done / total, 2) if total else None,
            }
        )
        if done >= total and total > 0:
            out["status"] = "done" if fail == 0 else "done_with_fail"
        else:
            # stale if mtime older than 10 min
            age = time.time() - path.stat().st_mtime
            out["status"] = "running" if age < 600 else "stale"
    else:
        age = time.time() - path.stat().st_mtime
        out["status"] = "log_only" if age < 600 else "stale"
    return out


def parse_enrich_curl() -> Dict[str, Any]:
    jsonl = LOGS / "asof_enrich_curl_progress.jsonl"
    stdout = LOGS / "asof_enrich_curl_stdout.log"
    out: Dict[str, Any] = {
        "id": "enrich_asof_curl",
        "log": str(jsonl),
        "stdout": str(stdout),
        "exists": jsonl.exists(),
        "mtime": file_mtime(jsonl),
        "done": None,
        "total": None,
        "ok": None,
        "fail": None,
        "pct": None,
        "amount_panels_ok": None,
        "last": None,
        "status": "missing",
    }
    if not jsonl.exists():
        return out
    summary = None
    ok = fail = 0
    for line in read_text(jsonl).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if "done" in o and "todo" in o:
            summary = o
        elif "instrument_id" in o:
            if o.get("ok"):
                ok += 1
            else:
                fail += 1
    # Prefer latest summary; else derive from per-instrument lines.
    # Known universe for asof_extend panels is ~5201.
    default_total = 5201
    if summary:
        done = int(summary.get("done") or 0)
        todo = int(summary.get("todo") or default_total)
        out.update(
            {
                "done": done,
                "total": todo,
                "ok": int(summary.get("ok") if summary.get("ok") is not None else ok),
                "fail": int(summary.get("fail") if summary.get("fail") is not None else fail),
                "pct": round(100.0 * done / todo, 2) if todo else None,
                "last": summary.get("last"),
            }
        )
    else:
        done = ok + fail
        out.update(
            {
                "done": done,
                "ok": ok,
                "fail": fail,
                "total": default_total,
                "pct": round(100.0 * done / default_total, 2),
            }
        )
    # count amount-ok panels from parquet scan is expensive; use summary ok as proxy
    out["amount_panels_ok"] = out.get("ok")
    age = time.time() - jsonl.stat().st_mtime
    # also check process
    running = _pgrep("enrich_asof_curl")
    if running:
        out["status"] = "running"
        out["pid"] = running
    elif out.get("total") and out.get("done") is not None and out["done"] >= out["total"]:
        out["status"] = "done"
    elif age < 600:
        out["status"] = "running"
    else:
        out["status"] = "stale"
    return out


def _pgrep(needle: str) -> Optional[int]:
    try:
        import subprocess

        r = subprocess.run(
            ["pgrep", "-af", needle], capture_output=True, text=True, timeout=5
        )
        for ln in r.stdout.splitlines():
            if "pgrep" in ln:
                continue
            parts = ln.split(None, 1)
            if parts:
                return int(parts[0])
    except Exception:
        return None
    return None


def count_glob(pattern: str) -> int:
    return len(list(Path("/").glob(pattern.lstrip("/"))) if pattern.startswith("/") else list(ROOT.glob(pattern)))


def shard_counts() -> Dict[str, int]:
    raw = V2 / "tushare_raw"
    return {
        "daily_days": len(list((raw / "daily").glob("*.parquet"))) if (raw / "daily").exists() else 0,
        "daily_basic_syms": len(list((raw / "daily_basic").glob("*.parquet"))) if (raw / "daily_basic").exists() else 0,
        "dividend_syms": len(list((raw / "dividend").glob("*.parquet"))) if (raw / "dividend").exists() else 0,
        "fina_indicator_syms": len(list((raw / "fina_indicator").glob("*.parquet"))) if (raw / "fina_indicator").exists() else 0,
        "income_syms": len(list((raw / "income").glob("*.parquet"))) if (raw / "income").exists() else 0,
        "asof_extend_panels": len(list((V2 / "asof_extend_202610" / "panels").glob("*.parquet"))) if (V2 / "asof_extend_202610" / "panels").exists() else 0,
    }


def parquet_info(path: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return info
    info["mtime"] = file_mtime(path)
    info["size_mb"] = round(path.stat().st_size / (1024 * 1024), 3)
    try:
        import pandas as pd

        df = pd.read_parquet(path)
        info["rows"] = int(len(df))
        info["cols"] = list(df.columns)
    except Exception as e:
        info["error"] = str(e)
    return info


def load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def parse_promotion_md() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "path": str(PROMO_MD),
        "exists": PROMO_MD.exists(),
        "items": [],
        "global_promotion_approved": False,
    }
    if not PROMO_MD.exists():
        return out
    text = read_text(PROMO_MD)
    # table rows: | ID | name | status | note |
    for ln in text.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() in {"id", "---"} or set(cells[0]) <= {"-"}:
            continue
        if cells[0].startswith("-"):
            continue
        item = {
            "id": cells[0],
            "name": cells[1] if len(cells) > 1 else "",
            "status": cells[2] if len(cells) > 2 else "",
            "note": cells[3] if len(cells) > 3 else "",
        }
        out["items"].append(item)
    if "promotion_approved` 全局仍为 **false**" in text or "仍为 **false**" in text:
        out["global_promotion_approved"] = False
    if re.search(r"全局仍为\s*\*\*true\*\*", text):
        out["global_promotion_approved"] = True
    return out


def attach_process(job: Dict[str, Any], needles: List[str]) -> None:
    for n in needles:
        pid = _pgrep(n)
        if pid:
            job["pid"] = pid
            if job.get("status") in {"stale", "log_only", "empty"}:
                job["status"] = "running"
            break


def build() -> Dict[str, Any]:
    shards = shard_counts()

    extend = parse_progress_log(LOGS / "extend.log", "extend")
    attach_process(extend, ["tushare_relay_pull.py extend"])
    extend["shards_written"] = shards["daily_days"]
    extend["title"] = "Tushare 日线续窗 (extend)"
    extend["note"] = "按交易日拉 daily(+limit)；目标替换东财 amount"

    db = parse_progress_log(LOGS / "daily_basic_hist.log", "daily_basic_hist")
    attach_process(db, ["tushare_relay_pull.py daily_basic_hist"])
    db["shards_written"] = shards["daily_basic_syms"]
    db["title"] = "日频流通市值 (daily_basic_hist)"
    db["note"] = "按标的拉 daily_basic 长窗"

    fin = parse_progress_log(LOGS / "fin.log", "fin")
    attach_process(fin, ["tushare_relay_pull.py fin"])
    fin["shards_written"] = shards["fina_indicator_syms"]
    fin["income_shards"] = shards["income_syms"]
    fin["title"] = "财务指标 (fin / fina_indicator+income)"
    fin["note"] = "公告日 → available_at 候选"

    div = parse_progress_log(LOGS / "dividend.log", "dividend")
    attach_process(div, ["tushare_relay_pull.py dividend"])
    div["shards_written"] = shards["dividend_syms"]
    div["title"] = "分红/除权 (dividend)"
    div["note"] = "公司行动预热与对账"

    enrich = parse_enrich_curl()
    enrich["title"] = "东财 asof_extend 字段补全 (enrich_asof_curl)"
    enrich["note"] = "amount/turnover/limit/ST；SSL 限流中，将被 Tushare extend 替代"
    enrich["asof_extend_panels"] = shards["asof_extend_panels"]

    # Artifact cards
    sw_tushare = parquet_info(V2 / "sw_l1_pit" / "industry_members_sw_l1_tushare.parquet")
    sw_tushare.update(
        {
            "id": "sw_tushare",
            "title": "申万一级 PIT (Tushare 候选)",
            "manifest": load_json(V2 / "sw_l1_pit" / "manifest.json"),
            "status": "ready" if sw_tushare.get("exists") else "missing",
        }
    )
    if sw_tushare.get("manifest"):
        sw_tushare["promotion_approved"] = bool(
            sw_tushare["manifest"].get("promotion_approved")
        )
    else:
        sw_tushare["promotion_approved"] = False

    etf = {
        "id": "etf_510300",
        "title": "510300 权益 ETF",
        "panel": parquet_info(V2 / "etf_510300" / "panels" / "sh.510300.parquet"),
        "fund_daily_tushare": parquet_info(
            V2 / "etf_510300" / "fund_daily_tushare_510300.parquet"
        ),
        "manifest": load_json(V2 / "etf_510300" / "manifest.json"),
        "validation": load_json(LOGS / "etf_510300_validation.json"),
    }
    etf["status"] = "ready" if etf["panel"].get("exists") else "missing"
    etf["promotion_approved"] = bool(
        (etf.get("manifest") or {}).get("promotion_approved")
    )

    fmc = {
        "id": "float_mktcap",
        "title": "流通市值 float_mktcap",
        "daily": parquet_info(
            V2 / "float_mktcap" / "float_mktcap_daily_20260630_20261009.parquet"
        ),
        "asof": parquet_info(V2 / "float_mktcap" / "float_mktcap_asof_2026-10-09.parquet"),
        "manifest": load_json(V2 / "float_mktcap" / "manifest.json"),
    }
    fmc["status"] = "ready" if fmc["daily"].get("exists") else "missing"
    fmc["promotion_approved"] = bool(
        (fmc.get("manifest") or {}).get("promotion_approved")
    )

    asof_man = load_json(V2 / "asof_extend_202610" / "manifest.json") or {}
    asof_card = {
        "id": "asof_extend_artifact",
        "title": "asof_extend 面板产物",
        "manifest": asof_man,
        "panels": shards["asof_extend_panels"],
        "promotion_approved": bool(asof_man.get("promotion_approved")),
        "status": "ready" if shards["asof_extend_panels"] else "missing",
    }

    promo = parse_promotion_md()

    jobs = [extend, db, fin, div, enrich]
    artifacts = [sw_tushare, etf, fmc, asof_card]

    # overall pct: average of jobs that have pct
    pcts = [j["pct"] for j in jobs if isinstance(j.get("pct"), (int, float))]
    overall_pct = round(sum(pcts) / len(pcts), 2) if pcts else None

    # Prefer the live gate (ENG_PING / promotion_gate) over markdown scrape,
    # which can flip false on stale "仍为 false" dataset notes.
    try:
        from quantlab.promotion_gate import overall_promotion_approved as _gate
        gate_overall = bool(_gate())
    except Exception:
        try:
            gate_overall = bool(json.loads((ROOT / "output/d1/ENG_PING_PATHS.json").read_text(encoding="utf-8")).get("promotion_approved_overall") is True)
        except Exception:
            gate_overall = bool(promo.get("global_promotion_approved", False))
    promo["global_promotion_approved"] = gate_overall

    payload = {
        "generated_at": now_et_iso(),
        "tz": "America/New_York",
        "overall_download_pct": overall_pct,
        "global_promotion_approved": gate_overall,
        "shards": shards,
        "jobs": jobs,
        "artifacts": artifacts,
        "promotion": promo,
        "paths": {
            "logs": str(LOGS),
            "json": str(JSON_OUT),
            "html": str(HTML_OUT),
            "promo_md": str(PROMO_MD),
        },
    }
    return payload


def status_color(status: str) -> str:
    s = (status or "").lower()
    return {
        "running": "#3b82f6",
        "done": "#22c55e",
        "done_with_fail": "#eab308",
        "ready": "#22c55e",
        "research_ok": "#a3e635",
        "pending": "#f59e0b",
        "pass": "#22c55e",
        "blocked": "#ef4444",
        "stale": "#f97316",
        "missing": "#6b7280",
        "empty": "#6b7280",
        "log_only": "#94a3b8",
    }.get(s, "#94a3b8")


def html_escape(s: Any) -> str:
    t = str(s if s is not None else "")
    return (
        t.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_html(data: Dict[str, Any]) -> str:
    jobs_html = []
    for j in data["jobs"]:
        pct = j.get("pct")
        bar = 0 if pct is None else max(0, min(100, pct))
        color = status_color(j.get("status", ""))
        meta_bits = []
        if j.get("done") is not None and j.get("total") is not None:
            meta_bits.append(f"{j['done']} / {j['total']}")
        if j.get("fail") is not None:
            meta_bits.append(f"fail {j['fail']}")
        if j.get("ok") is not None and j.get("id") == "enrich_asof_curl":
            meta_bits.append(f"ok {j['ok']}")
        if j.get("shards_written") is not None:
            meta_bits.append(f"shards {j['shards_written']}")
        if j.get("pid"):
            meta_bits.append(f"pid {j['pid']}")
        jobs_html.append(
            f"""
      <div class="card">
        <div class="card-head">
          <div class="title">{html_escape(j.get('title') or j.get('id'))}</div>
          <span class="badge" style="background:{color}">{html_escape(j.get('status'))}</span>
        </div>
        <div class="bar"><div class="fill" style="width:{bar}%;background:{color}"></div></div>
        <div class="meta">{html_escape(' · '.join(meta_bits))}</div>
        <div class="note">{html_escape(j.get('note') or '')}</div>
        <div class="sub">更新 {html_escape(j.get('mtime') or '—')} · {html_escape((j.get('last_line') or j.get('last') or '')[:120])}</div>
      </div>"""
        )

    art_html = []
    for a in data["artifacts"]:
        color = status_color(a.get("status", ""))
        promo = a.get("promotion_approved")
        promo_badge = (
            '<span class="badge" style="background:#22c55e">promotion true</span>'
            if promo
            else '<span class="badge" style="background:#64748b">promotion false</span>'
        )
        details = []
        if a.get("id") == "sw_tushare":
            details.append(f"rows {a.get('rows', '—')}")
        if a.get("id") == "etf_510300":
            pan = a.get("panel") or {}
            fd = a.get("fund_daily_tushare") or {}
            details.append(f"panel rows {pan.get('rows', '—')}")
            details.append(f"tushare fund_daily {fd.get('rows', '—')}")
        if a.get("id") == "float_mktcap":
            d = a.get("daily") or {}
            asof = a.get("asof") or {}
            details.append(f"daily rows {d.get('rows', '—')}")
            details.append(f"asof rows {asof.get('rows', '—')}")
        if a.get("id") == "asof_extend_artifact":
            details.append(f"panels {a.get('panels', '—')}")
            man = a.get("manifest") or {}
            details.append(f"as_of {man.get('as_of_extended', '—')}")
        art_html.append(
            f"""
      <div class="card">
        <div class="card-head">
          <div class="title">{html_escape(a.get('title') or a.get('id'))}</div>
          <span class="badge" style="background:{color}">{html_escape(a.get('status'))}</span>
        </div>
        <div class="meta">{html_escape(' · '.join(str(x) for x in details))} {promo_badge}</div>
      </div>"""
        )

    promo_rows = []
    for it in data.get("promotion", {}).get("items", []):
        color = status_color(it.get("status", ""))
        promo_rows.append(
            f"<tr><td>{html_escape(it.get('id'))}</td>"
            f"<td>{html_escape(it.get('name'))}</td>"
            f"<td><span class='badge' style='background:{color}'>{html_escape(it.get('status'))}</span></td>"
            f"<td class='note'>{html_escape(it.get('note'))}</td></tr>"
        )

    shards = data.get("shards") or {}
    shard_bits = " · ".join(f"{k}={v}" for k, v in shards.items())

    overall = data.get("overall_download_pct")
    overall_s = "—" if overall is None else f"{overall}%"
    gpromo = data.get("global_promotion_approved")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta http-equiv="refresh" content="15"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>QuantLab 数据进度看板</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    background: #0b1220; color: #e5e7eb; padding: 24px;
  }}
  h1 {{ margin: 0 0 4px; font-size: 22px; }}
  .subhead {{ color: #94a3b8; font-size: 13px; margin-bottom: 18px; }}
  .hero {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px;
  }}
  .hero .stat {{
    background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 14px 16px;
  }}
  .stat .label {{ color: #94a3b8; font-size: 12px; }}
  .stat .value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }}
  .card {{
    background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 14px 16px;
  }}
  .card-head {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 10px; }}
  .title {{ font-weight: 650; font-size: 15px; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; color: #0b1220; font-weight: 700; }}
  .bar {{ height: 10px; background: #1f2937; border-radius: 999px; overflow: hidden; }}
  .fill {{ height: 100%; border-radius: 999px; transition: width .4s ease; }}
  .meta {{ margin-top: 8px; font-size: 13px; color: #cbd5e1; }}
  .note {{ margin-top: 6px; font-size: 12px; color: #94a3b8; }}
  .sub {{ margin-top: 8px; font-size: 11px; color: #64748b; word-break: break-all; }}
  h2 {{ margin: 22px 0 10px; font-size: 16px; color: #cbd5e1; }}
  table {{ width: 100%; border-collapse: collapse; background: #111827; border-radius: 12px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
  th {{ color: #94a3b8; font-weight: 600; background: #0f172a; }}
  footer {{ margin-top: 18px; color: #64748b; font-size: 12px; }}
  code {{ background: #1f2937; padding: 1px 6px; border-radius: 6px; }}
</style>
</head>
<body>
  <h1>QuantLab 数据下载 &amp; 验收看板</h1>
  <div class="subhead">生成时间 {html_escape(data.get('generated_at'))}（ET）· 每 15 秒自动刷新 · 全局 promotion_approved =
    <strong style="color:{'#22c55e' if gpromo else '#f87171'}">{'true' if gpromo else 'false'}</strong>
  </div>

  <div class="hero">
    <div class="stat"><div class="label">下载任务均进度</div><div class="value">{html_escape(overall_s)}</div></div>
    <div class="stat"><div class="label">晋级验收项</div><div class="value">{len(data.get('promotion',{}).get('items',[]))}</div></div>
    <div class="stat"><div class="label">asof_extend 面板数</div><div class="value">{html_escape(shards.get('asof_extend_panels'))}</div></div>
    <div class="stat"><div class="label">Tushare shards</div><div class="value" style="font-size:14px;line-height:1.4;margin-top:8px">{html_escape(shard_bits)}</div></div>
  </div>

  <h2>下载任务</h2>
  <div class="grid">
    {''.join(jobs_html)}
  </div>

  <h2>关键产物</h2>
  <div class="grid">
    {''.join(art_html)}
  </div>

  <h2>晋级验收清单</h2>
  <table>
    <thead><tr><th>ID</th><th>验收项</th><th>状态</th><th>阻塞 / 证据</th></tr></thead>
    <tbody>
      {''.join(promo_rows) if promo_rows else '<tr><td colspan="4">未找到 PROMOTION_ACCEPTANCE.md</td></tr>'}
    </tbody>
  </table>

  <footer>
    JSON: <code>{html_escape(data['paths']['json'])}</code><br/>
    HTML: <code>{html_escape(data['paths']['html'])}</code><br/>
    日志目录: <code>{html_escape(data['paths']['logs'])}</code>
  </footer>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    JSON_OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    HTML_OUT.write_text(render_html(data), encoding="utf-8")
    print(json.dumps({"ok": True, "json": str(JSON_OUT), "html": str(HTML_OUT), "overall_pct": data.get("overall_download_pct")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
