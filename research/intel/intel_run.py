"""AI 情报师主脚本。--mode preopen：A 股开盘前（约 21:00 ET）出完整预警；--mode intraday：仅在重大变化时写新文件。
研究级：不下单、不改权重、禁 GP、live=false。输出 output/intel/ALERTS_latest.{md,json} 与 history/ALERTS_YYYYMMDD_HHMM.md（ET）。

intraday 重大变化阈值（任一满足即写新文件，否则只更新 state 不落盘）：
  A. 任一市场强度等级相对上次落盘升级到「强」（pct |Δ|≥2%，美债 ≥10bp，美元 ≥0.8%）；
  B. 任一市场当日涨跌相对上次落盘再变动 ≥1.0 个百分点（美债 ≥5bp，美元 ≥0.5%）；
  C. 出现上次落盘未见过的、严重度≥2 的政策/贸易新闻（337/出口管制/关税/稀土/谈判）。
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_common as C

OUT = C.ROOT / "output/intel"
HIST = OUT / "history"
STATE = OUT / "intraday_state.json"
STUDY = OUT / "event_study_hitrate.json"


def grade(key, kind, x):
    th = C.THRESH_OVERRIDE.get(key, C.THRESH[kind])
    a = abs(x)
    return "强" if a >= th["strong"] else ("中" if a >= th["mid"] else "弱"), th


def pull_markets():
    snap, status = {}, {}
    for k, m in C.MARKETS.items():
        try:
            s = C.yahoo_daily(m["sym"], "1mo")
            if len(s) < 2:
                raise ValueError("history<2")
            last, prev = s.iloc[-1], s.iloc[-2]
            chg = (last - prev) * 100 if m["kind"] == "bp" else (last / prev - 1) * 100
            # ^TNX 报价单位为收益率%，(last-prev)*100 = bp
            g, th = grade(k, m["kind"], chg)
            bad = (chg > 0) if k in ("us10y", "dxy") else (chg < 0)
            snap[k] = {"name": m["name"], "symbol": m["sym"], "date": str(s.index[-1].date()), "last": round(float(last), 4),
                       "change": round(float(chg), 3), "unit": "bp" if m["kind"] == "bp" else "%", "grade": g, "adverse": bool(bad)}
            status[m["sym"]] = "ok"
        except Exception as e:
            status[m["sym"]] = f"fail:{type(e).__name__}"
    return snap, status


def load_hitrates():
    try:
        return json.loads(STUDY.read_text())
    except Exception:
        return {}


def build_alerts(snap, news_hits):
    pool = C.industry_stocks()
    hr = load_hitrates()
    agg = {}  # industry -> list of contributions

    def add(ind, d, strength, reason, invalid, src):
        agg.setdefault(ind, []).append({"dir": d, "strength": strength, "reason": reason, "invalidation": invalid, "source": src})

    shocks = []
    for k, v in snap.items():
        if v["grade"] == "弱":
            continue
        sgn_factor = -1 if v["adverse"] else +1   # 坏消息→规则方向；好消息→反向
        st = 2 if v["grade"] == "强" else 1
        shocks.append({"type": "market", "key": k, "name": v["name"], "change": v["change"], "unit": v["unit"],
                       "grade": v["grade"], "direction": "利空A股相关行业" if v["adverse"] else "利多A股相关行业"})
        for ind, s in C.SHOCK_RULES.get(k, {}).items():
            d = s * (1 if v["adverse"] else -1)
            inv = f"A股开盘30分钟内{ind}指数与预判方向相反超过1%，或{v['name']}期货/夜盘收复一半以上涨跌幅"
            add(ind, d, st, f"{v['name']} {v['change']:+.2f}{v['unit']}（{v['grade']}）", inv, k)
    themes = {}
    for n in news_hits:
        shocks.append({"type": "news", "theme": n["theme"], "title": n["title"], "source": n["source"],
                       "published_et": n["published_et"], "link": n["link"], "severity": n["severity"]})
        themes.setdefault(n["theme"], []).append(n)
    # 每个主题对每个行业只计一次：严重度3且≥2条→强度2，否则1（避免同题材刷屏放大得分）
    for th, ns in themes.items():
        st = 2 if (ns[0]["severity"] >= 3 and len(ns) >= 2) else 1
        for ind, d in ns[0]["industries"].items():
            add(ind, d, st, f"[{th}] {len(ns)}条，例：{ns[0]['title'][:70]}",
                f"{th}消息官方未落地/被否认，或A股相关行业开盘未跟随", "news:" + th)

    rows = []
    for ind, cs in agg.items():
        score = sum(c["dir"] * c["strength"] for c in cs)
        mkt = [c for c in cs if not c["source"].startswith("news")]
        if score <= -2:
            call = "偏空"
        elif score >= 2:
            call = "偏多"
        else:
            call = "观察"
        # 事件研究命中率背书：若相关冲击的历史命中率<55% 或样本<10，降级为观察
        support = []
        for c in mkt:
            h = hr.get("by_rule", {}).get(f"{c['source']}|{ind}")
            if h:
                support.append(h)
        weak = bool(support) and all((s.get("hit_rate") or 0) < 0.55 or s.get("n", 0) < 10 for s in support)
        if call != "观察" and weak:
            call_note = "（历史命中率不足，降级为观察）"; call = "观察"
        else:
            call_note = ""
        news_only = not mkt
        if news_only and call != "观察":
            call, call_note = "观察", "（仅新闻驱动，未经回测，降级为观察）"
        rows.append({"industry": ind, "score": score, "call": call, "note": call_note,
                     "strength": "强" if abs(score) >= 4 else ("中" if abs(score) >= 2 else "弱"),
                     "reasons": list(dict.fromkeys(c["reason"] for c in cs))[:6],
                     "invalidation": list(dict.fromkeys(c["invalidation"] for c in cs))[:3],
                     "hist_support": support, "stocks": pool.get(ind, [])})
    C.apply_alert_severity(rows)  # contract v1.1 explicit severity
    rows.sort(key=lambda r: (-abs(r["score"]), r["industry"]))
    return shocks, rows, pool.get("_pool_session")


def render_md(p):
    errs = p.get("data_integrity_errors") or []
    L = [f"# AI 情报师预警（{p['mode']}）", ""]
    for e in errs:   # r3 P2-3：完整性错误横幅放在标题下第一行
        L += [f"> ⚠ HIGH：{e['table']} 完整性错误，本轮未输出相关个股（{e['reason']}）", ""]
    L += [
         f"- 生成时间：{p['generated_et']} ET",
         f"- 研究级，live=false，不下单、不改权重；个股池 mid_large session={p['pool_session']}；标「小盘」者不在 mid_large 池，仅作提示。", ""]
    L += ["## 外盘快照", "", "| 市场 | 日期 | 收盘 | 涨跌 | 强度 |", "|---|---|---|---|---|"]
    for k, v in p["markets"].items():
        L.append(f"| {v['name']} ({v['symbol']}) | {v['date']} | {v['last']} | {v['change']:+.2f}{v['unit']} | {v['grade']} |")
    miss = [s for s, st in p["source_status"]["markets"].items() if st != "ok"]
    if miss:
        L.append(f"\n不可用：{', '.join(miss)}")
    L += ["", "## 行业预警", ""]
    if not p["alerts"]:
        L.append("无达到「中」以上强度的冲击，全部观察。")
    for r in p["alerts"]:
        st = "、".join(s["name"] + ("（小盘）" if s["small_cap"] else "") for s in r["stocks"])
        L += [f"### {r['industry']}：{r['call']}{r['note']}（强度 {r['strength']}，得分 {r['score']:+d}）",
              "- 理由：" + "；".join(r["reasons"]),
              "- 失效条件：" + "；".join(r["invalidation"]),
              "- 历史命中率：" + ("；".join(f"{h['rule']} 命中 {h['hit_rate']:.0%}（n={h['n']}，均值 {h['mean_ret_pct']:+.2f}%）" for h in r["hist_support"]) or "无对应回测"),
              f"- 相关个股：{st or ('（' + '；'.join(e['table'] + ' 完整性错误，已停：' + e['reason'] for e in errs) + '）' if errs else st)}", ""]
    news = [s for s in p["shocks"] if s["type"] == "news"]
    L += ["## 政策/贸易新闻命中", ""]
    L += [f"- [{n['theme']}] {n['published_et']} ET {n['source']}：{n['title']}" for n in news] or ["- 无"]
    L += ["", f"新闻源状态：{json.dumps(p['source_status']['news'], ensure_ascii=False)}"]
    for t, f in (p["source_status"].get("tables") or {}).items():
        if f:
            L += [f"数据表新鲜度：{t} {f['status']}——{f['disclosure']}" + ("（行业归属可能未反映最新成分变动，结论照常输出）" if f["status"] == "stale" else ("（HIGH：完整性错误）" if f["status"] == "error" else ""))]
    return "\n".join(L) + "\n"


# ---- 2026-10-18 01:25 ET：写 latest 前合并旧文件的人工字段（manual_review / 人工覆盖分 / events / weekly_report）----
import re as _re
OVR_RE = _re.compile(r"^\s*(?P<ind>[^\s：:\[]+)[：:]\s*机器得分\s*(?P<m>[-+]?\d+)（(?P<ms>[强中弱])）\s*→\s*人工\s*(?P<h>[-+]?\d+)（(?P<hs>[强中弱])）")
_TS_RE = _re.compile(r"\[(\d{2}:\d{2}) ET")


def _norm_review(x, fallback_et):
    """manual_review 条目统一为 dict{text, created_et[, expires_et]}；旧的字符串条目补 created_et。"""
    if isinstance(x, dict):
        d = dict(x); d.setdefault("created_et", fallback_et); return d
    m = _TS_RE.search(str(x))
    ce = (fallback_et[:11] + m.group(1)) if m else fallback_et
    return {"text": str(x), "created_et": ce}


def _expired(d, now_et: str) -> bool:
    e = d.get("expires_et")
    return bool(e) and str(e)[:16] < now_et[:16]


def merge_prev(p: dict, prev: dict) -> dict:
    """把旧 latest 的人工字段并进新结果；只改 p，不改市场或新闻计算。"""
    now_et = p["generated_et"]
    fb = prev.get("generated_et", now_et)
    seen, rv = set(), []
    for x in list(prev.get("manual_review", [])) + list(p.get("manual_review", [])):
        d = _norm_review(x, fb)
        k = d["text"].strip()
        if k in seen or _expired(d, now_et):
            continue
        seen.add(k); rv.append(d)
    if rv:
        p["manual_review"] = rv
    # 人工覆盖：显式 manual_overrides 优先，否则从 manual_review 文本解析“行业：机器得分 a（x）→ 人工 b（y）”
    ovr = {o["industry"]: o for o in prev.get("manual_overrides", []) if not _expired(o, now_et)}
    for d in rv:
        m = OVR_RE.match(d["text"])
        if m and m.group("ind") not in ovr and not _expired(d, now_et):
            ovr[m.group("ind")] = {"industry": m.group("ind"), "manual_score": int(m.group("h")), "manual_strength": m.group("hs"),
                                   "created_et": d["created_et"], **({"expires_et": d["expires_et"]} if d.get("expires_et") else {}),
                                   "reason": d["text"][:200]}
    applied = []
    for a in p.get("alerts", []):
        o = ovr.get(a["industry"])
        if not o:
            continue
        ms, mst = a["score"], a["strength"]
        a["machine_score"], a["machine_strength"] = ms, mst
        a["score"], a["strength"] = int(o["manual_score"]), o["manual_strength"]
        a["call"] = "偏空" if a["score"] < 0 else ("偏多" if a["score"] > 0 else "观察")
        a["manual_override"] = True
        a["note"] = f"（人工覆盖：机器 {ms:+d}（{mst}）→ 人工 {a['score']:+d}（{a['strength']}），{o['created_et']} 起）"
        applied.append({"industry": a["industry"], "machine_score": ms, "manual_score": a["score"]})
    C.apply_alert_severity(p.get("alerts", []))
    if ovr:
        p["manual_overrides"] = list(ovr.values())
        p["manual_overrides_applied"] = applied
    for k in ("events", "weekly_report"):
        if not p.get(k) and prev.get(k):
            p[k] = prev[k]
    return p


def render_extra(p) -> str:
    L = []
    if p.get("manual_review"):
        L += ["", "## 人工复核", ""] + [f"- [{d.get('created_et','')}] {d['text']}" for d in p["manual_review"]]
    if p.get("manual_overrides_applied"):
        L += ["", "## 人工覆盖（已重新套用）", ""] + [f"- {x['industry']}：机器分 {x['machine_score']:+d} → 人工分 {x['manual_score']:+d}" for x in p["manual_overrides_applied"]]
    if p.get("events"):
        L += ["", "## 事件（events[]，契约 v1.1 显式 severity）", ""] + [f"- [{e.get('severity')}] {e.get('time_et')} {e.get('event')}。{e.get('note','')}（{e.get('source','')}；{e.get('url','')}）" for e in p["events"]]
    if p.get("weekly_report"):
        L += ["", f"- 周报：{p['weekly_report']}"]
    return "\n".join(L) + ("\n" if L else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preopen", "intraday"], required=True)
    ap.add_argument("--out-dir", default=None, help="测试用：写到临时目录（不碰正式 latest/state/history）")
    ap.add_argument("--prev", default=None, help="测试用：指定旧 ALERTS json")
    a = ap.parse_args()
    now = datetime.now(C.ET_TZ)
    snap, mstat = pull_markets()
    news, nstat = C.fetch_news(36 if a.mode == "preopen" else 12)
    hits = C.classify_news(news)
    shocks, rows, ps = build_alerts(snap, hits)
    p = {"schema": "quantlab.intel.alerts.v1", "mode": a.mode, "generated_et": now.strftime("%Y-%m-%d %H:%M"),
         "live": False, "promotion_approved": False, "pool_session": ps, "markets": snap, "shocks": shocks,
         "alerts": rows, "source_status": {"markets": mstat, "news": nstat, "tables": {"sw_pit": C.SW_FRESHNESS}}, "news_scanned": len(news)}
    p["data_integrity_errors"] = [{"table": t, "severity": "high", "reason": f.get("reason", f.get("disclosure", ""))}
                                  for t, f in p["source_status"]["tables"].items() if f and f.get("status") == "error"]
    if a.mode == "intraday":
        prev = json.loads(STATE.read_text()) if STATE.exists() else {}
        reasons = []
        for k, v in snap.items():
            pv = prev.get("markets", {}).get(k)
            if not pv:
                continue
            th = C.THRESH_OVERRIDE.get(k, C.THRESH["bp" if v["unit"] == "bp" else "pct"])
            if v["grade"] == "强" and pv["grade"] != "强":
                reasons.append(f"A:{k}升级为强")
            if abs(v["change"] - pv["change"]) >= th["mid"]:
                reasons.append(f"B:{k}变动{v['change'] - pv['change']:+.2f}")
        old = set(prev.get("news_titles", []))
        new = [h["title"] for h in hits if h["severity"] >= 2 and h["title"] not in old]
        if new:
            reasons.append(f"C:新增重大新闻{len(new)}条")
        if prev and not reasons:
            print("intraday: 无重大变化，不写新文件")
            return
        p["trigger"] = reasons or ["首次 intraday 运行"]
    prevf = Path(a.prev) if a.prev else OUT / "ALERTS_latest.json"
    if prevf.exists():
        try:
            p = merge_prev(p, json.loads(prevf.read_text()))
        except Exception as e:
            print("merge_prev 失败，未合并：", type(e).__name__, e)
    md = render_md(p) + render_extra(p)
    if a.out_dir:
        od = Path(a.out_dir); od.mkdir(parents=True, exist_ok=True)
        (od / "ALERTS_latest.md").write_text(md)
        (od / "ALERTS_latest.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
        print("dry-run written", od)
        return
    OUT.mkdir(parents=True, exist_ok=True); HIST.mkdir(parents=True, exist_ok=True)
    (OUT / "ALERTS_latest.md").write_text(md)
    (OUT / "ALERTS_latest.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
    h = HIST / f"ALERTS_{now:%Y%m%d_%H%M}.md"
    h.write_text(md)
    (HIST / f"ALERTS_{now:%Y%m%d_%H%M}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
    STATE.write_text(json.dumps({"markets": snap, "news_titles": [x["title"] for x in hits], "written_et": p["generated_et"]}, ensure_ascii=False))
    print("written", h)


if __name__ == "__main__":
    main()
