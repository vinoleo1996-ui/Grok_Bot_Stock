"""Read-only research-and-development ledger for /rd."""
from __future__ import annotations

import json
from pathlib import Path

from quantlab.config import ROOT

LEDGER = ROOT / "docs" / "rd" / "messages.jsonl"
REQUIRED = ("id", "role", "status", "evidence", "body")
OPEN = {"open"}


def load_messages(path: Path | None = None) -> list[dict]:
    source = path or LEDGER
    if not source.is_file():
        return []
    rows = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        validate_message(row)
        rows.append(row)
    return rows


def validate_message(row: dict) -> None:
    missing = [key for key in REQUIRED if not row.get(key)]
    if missing:
        raise ValueError(f"rd_message_missing:{','.join(missing)}")
    if row["status"] not in {"open", "answered", "rejected"}:
        raise ValueError(f"rd_message_status:{row['status']}")
    if row["status"] != "open" and not str(row["evidence"]).strip():
        raise ValueError("rd_message_closed_without_evidence")


ROLE_ORDER = (
    "product",
    "algo-universe",
    "algo-factor",
    "algo-portfolio",
    "director",
    "test",
    "architect",
    "data",
)


def _article(row: dict) -> str:
    reply = row.get("reply_to") or "—"
    return (
        "<article class=card data-rd-status="
        + _esc(row["status"])
        + " data-rd-role="
        + _esc(row["role"])
        + "><h2>"
        + _esc(row["id"])
        + " · "
        + _esc(row["role"])
        + " · "
        + _esc(row["status"])
        + "</h2><p>"
        + _esc(row["body"])
        + "</p><p>回复 "
        + _esc(reply)
        + "</p><p>证据 "
        + _esc(row["evidence"])
        + "</p></article>"
    )


def _experiments() -> list[str]:
    folder = LEDGER.parent / "experiments"
    if not folder.is_dir():
        return []
    lines = []
    for path in sorted(folder.glob("*.md")):
        title = path.name
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        lines.append(f"{title} · docs/rd/experiments/{path.name}")
    return lines


def render_html(path: Path | None = None) -> str:
    rows = load_messages(path)
    open_rows = [row for row in rows if row["status"] in OPEN]
    parts = [
        "<!doctype html><html lang=zh-CN><head><meta charset=utf-8>",
        "<title>QuantLab · 研发台账</title>",
        "<link rel=stylesheet href=/static/dashboard.css></head><body>",
        "<header class=dash-header><div class=header-inner>",
        "<a class=brand href=/dashboard>QuantLab</a>",
        "<nav class=dash-nav><a href=/dashboard>决策看板</a>",
        "<a href=/research>研究裁决</a><a href=/rd aria-current=page>研发台账</a></nav>",
        "</div></header><main class=dash-main>",
        "<h1>研发台账</h1>",
        "<p>只读。不改策略，不下单。未关闭意见必须带证据路径。</p>",
        f"<p id=rd-open-count>未关闭 {len(open_rows)} / 共 {len(rows)}</p>",
        "<section id=rd-open><h2>未关闭</h2>",
    ]
    if open_rows:
        parts.extend(_article(row) for row in open_rows)
    else:
        parts.append("<p>没有未关闭意见。</p>")
    parts.append("</section><section id=rd-experiments><h2>实验设计</h2>")
    experiments = _experiments()
    if experiments:
        parts.append("<ul>" + "".join(f"<li>{_esc(item)}</li>" for item in experiments) + "</ul>")
    else:
        parts.append("<p>没有实验设计。</p>")
    parts.append("</section>")
    seen = []
    for role in ROLE_ORDER:
        if any(row["role"] == role for row in rows):
            seen.append(role)
    for role in rows:
        if role["role"] not in seen:
            seen.append(role["role"])
    for role in seen:
        parts.append(f"<section id=rd-role-{_esc(role)}><h2>{_esc(role)}</h2>")
        parts.extend(_article(row) for row in rows if row["role"] == role)
        parts.append("</section>")
    parts.append("</main></body></html>")
    return "".join(parts)


def _esc(value) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
