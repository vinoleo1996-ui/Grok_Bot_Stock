"""intel_run.merge_prev 自测（不联网、不写正式 latest）。python3 research/intel/test_intel_run_merge.py"""
import sys, json, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intel_run as R

prev = json.loads((R.OUT / "ALERTS_latest.json").read_text())
ok = 0; fails = []
def check(name, cond):
    global ok
    if cond: ok += 1; print("PASS", name)
    else: fails.append(name); print("FAIL", name)

# 模拟新一轮：机器重算后电子回到 -1、无 manual_review/events/weekly_report
new = {k: copy.deepcopy(prev[k]) for k in ("schema", "mode", "live", "promotion_approved", "pool_session", "markets", "shocks", "source_status", "news_scanned")}
new["generated_et"] = "2026-10-18 01:30"
new["alerts"] = copy.deepcopy(prev["alerts"])
for a in new["alerts"]:
    if a["industry"] == "电子":
        a.update(score=-1, strength="弱", call="观察", note="")
    for k in ("machine_score", "machine_strength", "manual_override"):
        a.pop(k, None)
p = R.merge_prev(new, prev)
texts = [d["text"] for d in p["manual_review"]]
check("manual_review 4 条原始条目都在", len(prev["manual_review"]) >= 4 and all((x if isinstance(x, str) else x["text"]) in texts for x in prev["manual_review"]))
check("manual_review 每条有 created_et", all(d.get("created_et") for d in p["manual_review"]))
check("TokenPost 观察项保留", any("TokenPost" in t for t in texts))
check("events 保留", p.get("events") == prev.get("events") and len(p["events"]) > 0)
check("weekly_report 保留", p.get("weekly_report") == prev.get("weekly_report") and p["weekly_report"])
e = [a for a in p["alerts"] if a["industry"] == "电子"][0]
check("电子人工 -6（强）重新套用", e["score"] == -6 and e["strength"] == "强" and e["call"] == "偏空" and e["severity"] == "high")
check("电子输出写明机器分和人工分", e["machine_score"] == -1 and "机器 -1" in e["note"] and "人工 -6" in e["note"])
check("render_extra 可见覆盖", "机器分 -1 → 人工分 -6" in R.render_extra(p))
# 去重：二次合并不增条
p2 = R.merge_prev(copy.deepcopy(p), p)
check("按条目去重（重复合并不增加）", len(p2["manual_review"]) == len(p["manual_review"]))
# 过期丢弃
pv = copy.deepcopy(prev); pv["manual_review"] = list(pv["manual_review"]) + [{"text": "过期测试条", "created_et": "2026-10-17 00:00", "expires_et": "2026-10-17 12:00"}]
p3 = R.merge_prev(copy.deepcopy(new), pv)
check("expires_et 已过期的丢弃", all(d["text"] != "过期测试条" for d in p3["manual_review"]))
# 本轮有新 events 时不被旧值覆盖
n4 = copy.deepcopy(new); n4["events"] = [{"event": "新事件", "severity": "info"}]
check("本轮有新 events 时用新值", R.merge_prev(n4, prev)["events"] == n4["events"])
print(f"\n{ok}/{ok+len(fails)} passed")
sys.exit(1 if fails else 0)
