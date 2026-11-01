#!/usr/bin/env python3
"""Independent recount of the 40% one-way turnover over-cap days (Arch audit P2-3; Arch review 4698a2c1 P3).

Independent of scripts_eng/core_x2_scorecard.py: reads only output/strategy_optimizer/core_x2/core_v1_3_disclosure.csv
(manifest sha 9586e5f3…) with the csv module (no pandas, no quantlab imports), recounts per AUM:
  over  = rows with sleeve == equity_100, status in {OK, LOT_CASH_GT2}, one_way_opt > 0.40  (empty one_way_opt = not over)
  denom_all_feasible    = all such HARD-feasible rows               (Arch P2-3 / scorecard: 60万 28/96, 100万 18/81)
  denom_with_turnover   = feasible rows with non-empty one_way_opt  (frozen RESIGN .ok L16: 60w_28/95_100w_18/80)
  rows_without_turnover = the feasible rows excluded by the second denominator (expected: 2018-01-31 per AUM, first
                          feasible row, no prior weights; 2018-01-02 is NO_DATA_CARRY and in neither denominator).
Numerators and both denominators are written verbatim; nothing is reconciled or rounded. X2-only split included.
Writes ONE new file core_x2/overcap_recount_v1_3_<tag>.json with exclusive create (refuses existing / bad tag).
--out-tag must end with _<first 8 hex of this script's own sha256> (Arch appx C P1-3).
Usage (after Arch .ok): python3 scripts_eng/overcap_recount_v1_3.py --out-tag auditfix_20261018_<sha8>
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/strategy_optimizer/core_x2"
SRC = OUT / "core_v1_3_disclosure.csv"
SRC_SHA = "9586e5f3ecde6580c5b232a4823fe167814f49a697c823acaea46be688bc2c1b"   # v1_3_RUN_MANIFEST.json inputs
EXPECT = {"600000": (28, 96), "1000000": (18, 81)}          # Arch P2-3 / scorecard (all feasible rows)
EXPECT_RESIGN_OK = {"600000": (28, 95), "1000000": (18, 80)}  # frozen ARCH_RESIGN_A_v1_3.ok line 16 (verbatim)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out-tag", required=True); a = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_]+", a.out_tag):
        raise SystemExit("REFUSED: bad --out-tag")
    dst = OUT / f"overcap_recount_v1_3_{a.out_tag}.json"
    if dst.exists():
        raise SystemExit(f"REFUSED: {dst} exists")
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import ok_runner_pin
    self_sha = ok_runner_pin.sha256_file(__file__)
    if not a.out_tag.endswith("_" + self_sha[:8]):
        raise SystemExit(f"REFUSED: --out-tag {a.out_tag!r} must end with '_{self_sha[:8]}' (runner sha256 {self_sha})")
    pin = ok_runner_pin.enforce(__file__, [OUT / "ARCH_RUN_AUTH_ENG_AUDITFIX_20261018.ok"], modes=["recount"],
                                deps={"ok_runner_pin": Path(ok_runner_pin.__file__), "v1_3_disclosure": SRC})
    got = hashlib.sha256(SRC.read_bytes()).hexdigest()
    if got != SRC_SHA:
        raise SystemExit(f"REFUSED: {SRC} sha256={got} != manifest {SRC_SHA}")
    res = {}
    with SRC.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sleeve"] != "equity_100" or r["status"] not in ("OK", "LOT_CASH_GT2"):
                continue
            d = res.setdefault(r["aum"].split(".")[0], {"over": 0, "denom_all_feasible": 0, "denom_with_turnover": 0,
                                                         "over_X2": 0, "denom_X2_all_feasible": 0, "denom_X2_with_turnover": 0,
                                                         "rows_without_turnover": []})
            v = r.get("one_way_opt", "").strip()
            over = bool(v) and float(v) > 0.40
            d["denom_all_feasible"] += 1; d["over"] += over; d["denom_with_turnover"] += bool(v)
            if not v:
                d["rows_without_turnover"].append({"date": r["date"], "window": r["window"], "status": r["status"]})
            if r["window"] == "X2":
                d["denom_X2_all_feasible"] += 1; d["over_X2"] += over; d["denom_X2_with_turnover"] += bool(v)
    for k, d in res.items():
        d["ratio_all_feasible"] = f"{d['over']}/{d['denom_all_feasible']}"
        d["ratio_with_turnover"] = f"{d['over']}/{d['denom_with_turnover']}"
        d["expected_scorecard"] = f"{EXPECT[k][0]}/{EXPECT[k][1]}" if k in EXPECT else None
        d["expected_resign_ok_L16"] = f"{EXPECT_RESIGN_OK[k][0]}/{EXPECT_RESIGN_OK[k][1]}" if k in EXPECT_RESIGN_OK else None
        d["match_scorecard"] = k in EXPECT and (d["over"], d["denom_all_feasible"]) == EXPECT[k]
        d["match_resign_ok_L16"] = k in EXPECT_RESIGN_OK and (d["over"], d["denom_with_turnover"]) == EXPECT_RESIGN_OK[k]
    note = ("Frozen ARCH_RESIGN_A_v1_3.ok L16 says 60w_28/95_100w_18/80; scorecard says 28/96, 18/81. Numerators agree. "
            "Likely cause: the first HARD-feasible row per AUM (2018-01-31) has no prior weights, so one_way_opt is empty; "
            "counting only rows with a turnover value gives 95/80, counting all feasible rows (Arch P2-3) gives 96/81. "
            "2018-01-02 is NO_DATA_CARRY and is in neither denominator. See rows_without_turnover for the verbatim rows.")
    doc = dict(out_tag=a.out_tag, runner_sha256=self_sha, source=str(SRC.relative_to(ROOT)), source_sha256=got,
               result=res, discrepancy_note=note, runner_pin=pin, live=False, promotion=False)
    with open(dst, "x", encoding="utf-8") as fh:  # Arch appx C P2-5: exclusive create, never overwrite
        fh.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
