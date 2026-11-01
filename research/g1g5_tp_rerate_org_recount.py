"""Leaf15 tp_rerate count review ONLY: org-name normalization recount. No prices/returns read. Verdict/weights/definition unchanged."""
import re, json, sys, resource
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import research.g1g5_tp_rerate_events as ev
from research.g1g5_tp_rerate_weights import mf, HARD_EXCLUDE, SCORE_N, _load_benchmark_closes
ALIAS = {"中金公司": "中金", "申万宏源研究": "申万宏源", "东亚前海证券研究所": "东亚前海", "东亚前海": "东亚前海",
         "高盛集团(goldmansachs)": "高盛", "国泰海通": "国泰海通", "财富证券": "财信", "财信": "财信"}
MERGE = {"国泰君安": "国泰海通", "海通": "国泰海通", "国联": "国联民生", "民生": "国联民生"}  # sensitivity only
def norm(s, merge=False):
    s = str(s).strip().replace("（", "(").replace("）", ")").replace(" ", "").lower()
    s = ALIAS.get(s, s)
    for suf in ["证券股份有限公司", "股份有限公司", "有限公司", "研究所", "研究院", "证券", "公司"]:
        if s.endswith(suf) and len(s) > len(suf) + 1: s = s[: -len(suf)]
    s = ALIAS.get(s, s)
    return MERGE.get(s, s) if merge else s
uni = mf.select_mid_large_topn_light(top_n=SCORE_N)
universe = set(x for x in uni["instruments"] if x not in HARD_EXCLUDE)
sess = pd.DatetimeIndex(_load_benchmark_closes("510300").index)
E0, st0 = ev.events(universe, sess)
raw = pd.read_parquet(ev.RC, columns=["org_name"]).org_name.astype(str).str.strip().unique()
mp = {o: norm(o) for o in raw}; mpm = {o: norm(o, True) for o in raw}
orig_read = pd.read_parquet
def run(m):
    def rp(p, *a, **k):
        df = orig_read(p, *a, **k)
        if "org_name" in df.columns: df["org_name"] = df.org_name.astype(str).str.strip().map(m)
        return df
    ev.pd.read_parquet = rp
    try: return ev.events(universe, sess)
    finally: ev.pd.read_parquet = orig_read
E1, st1 = run(mp); E2, st2 = run(mpm)
W = pd.read_parquet(ROOT / "output/ai_factory/g1g5_tp_rerate_daily_weights_20261014_183329.parquet", columns=["date", "instrument", "target_weight"])
W = W[W.target_weight > 0]; held = set(zip(pd.to_datetime(W.date), W.instrument))
def entered(r):
    k = sess.searchsorted(r.d, side="right"); return k < len(sess) and (sess[k], r.instrument) in held
E0w = E0[E0.d >= "2023-10-01"].copy(); E0w["entered"] = [entered(r) for r in E0w.itertuples()]
def surv(E, Enew):
    key = set(zip(Enew.instrument, Enew.d)); return int(sum((i, d) in key for i, d in zip(E.instrument, E.d)))
res = {"n_raw_orgs": int(len(raw)), "n_norm_orgs": len(set(mp.values())), "n_norm_orgs_merge": len(set(mpm.values())),
       "merged_pairs": {k: v for k, v in mp.items() if k != v},
       "orig": {"full": len(E0), "window": len(E0w), "entered": int(E0w.entered.sum())}}
for tag, En in [("norm", E1), ("norm_plus_merger", E2)]:
    Ew = En[En.d >= "2023-10-01"]
    res[tag] = {"rerun_full": len(En), "rerun_window": len(Ew), "rerun_by_year": {int(k): int(v) for k, v in En.groupby(En.d.dt.year).size().items()},
                "same_event_survive_full": surv(E0, En), "same_event_survive_window": surv(E0w, En),
                "same_event_survive_entered": surv(E0w[E0w.entered], En)}
res["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
out = ROOT / "output/ai_factory/leaf_reports/tp_rerate/org_norm_recount.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=2)); print(json.dumps(res, ensure_ascii=False, indent=1))
