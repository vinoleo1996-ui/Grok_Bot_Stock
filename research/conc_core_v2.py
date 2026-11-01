import sys, json, os
sys.path.insert(0, "research"); sys.path.insert(0, ".")
import pandas as pd
import small_aum_conc_lib as L
sess, s = L.run_group("CORE", {"CORE": {"capacity_adv": 1.0}})
res = {}
for a in (60, 100):
    o = L.OUT / f"CORE_CORE_topN_{a}w.parquet"; n = L.OUT / f"conc_CORE_{a}w.parquet"; os.replace(o, n)
    (L.OUT / f"CORE_CORE_ctrl510300_{a}w.parquet").unlink()
    W = pd.read_parquet(n); sm = W.groupby("session").weight.sum()
    v = s[f"CORE_topN_{a}w"]; v["file"] = str(n.relative_to(L.ROOT))
    v.update(sum_min=float(sm.min()), sum_max=float(sm.max()), n_neg=int((W.weight < 0).sum())); res[f"CORE_topN_{a}w"] = v
    print(a, v)
S = json.load(open(L.OUT / "SUMMARY.json")); S["groups"]["CORE"] = dict(sessions=[sess[0], sess[-1], len(sess)], arms=res)
json.dump(S, open(L.OUT / "SUMMARY.json", "w"), ensure_ascii=False, indent=1)
b = pd.read_parquet("output/ai_factory/g1g5_capacity_adv_daily_weights_20261013_111219.parquet")
print("orig510300", b[b.instrument == "510300.SH"].groupby("session").weight.sum().mean())
