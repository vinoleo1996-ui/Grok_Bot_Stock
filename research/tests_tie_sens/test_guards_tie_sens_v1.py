"""Static guard tests for strategy_tie_sensitivity_prereg_v1 (temp files only; no market data, no returns, no main())."""
import sys, tempfile, hashlib
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import strategy_tie_sensitivity_prereg_v1 as S
assert "pandas" not in S.__dict__ and "ts" not in S.__dict__, "module must not import data deps at top level"
T = Path(tempfile.mkdtemp(prefix="tiesens_"))
for k, rel in S.PINNED.items():
    p = T / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(f"fake {k}".encode())
SH = {k: hashlib.sha256((T / rel).read_bytes()).hexdigest() for k, rel in S.PINNED.items()}
def body(**over):
    d = dict(format="quantlab_run_auth_v1", version="tie_sens_v1", signed_by="arch", signed_et="2026-10-18 01:00 ET",
             allow_full="true", allow_smoke="false", out_dir=S.OUT_REL, **SH); d.update(over)
    return "free text line ignored\n中文说明 ignored\n" + "".join(f"{k}={v}\n" for k, v in d.items() if v is not None)
def tryit(name, f, expect):
    try: f(); got = "ACCEPTED"
    except SystemExit as e: got = "REFUSED"; msg = str(e.code)[:90]
    ok = got == expect; print(f"{'PASS' if ok else 'FAIL'} {name}: {got}" + ("" if got == "ACCEPTED" else f" :: {msg}")); return ok
def okf(name, text): p = T / f"{name}.ok"; p.write_text(text, encoding="utf-8"); return p
res = []
run = lambda p: S.enforce_run_auth(S.parse_run_auth(p), root=T)
res.append(tryit("good", lambda: run(okf("good", body())), "ACCEPTED"))
res.append(tryit("missing_file", lambda: S.parse_run_auth(T / "nope.ok"), "REFUSED"))
for k in S.AUTH_REQUIRED:
    res.append(tryit(f"missing_{k}", lambda k=k: run(okf(f"miss_{k}", body(**{k: None}))), "REFUSED"))
res.append(tryit("empty_value", lambda: run(okf("empty", body(signed_et=""))), "REFUSED"))
res.append(tryit("duplicate", lambda: run(okf("dup", body() + "allow_full=true\n")), "REFUSED"))
res.append(tryit("bool_typo", lambda: run(okf("bt", body(allow_full="yes"))), "REFUSED"))
res.append(tryit("bool_True_case", lambda: run(okf("bc", body(allow_full="True"))), "REFUSED"))
res.append(tryit("allow_full_false", lambda: run(okf("af", body(allow_full="false"))), "REFUSED"))
res.append(tryit("allow_smoke_true", lambda: run(okf("as", body(allow_smoke="true"))), "REFUSED"))
res.append(tryit("bad_format", lambda: run(okf("bf", body(format="x"))), "REFUSED"))
res.append(tryit("bad_version", lambda: run(okf("bv", body(version="v1_3"))), "REFUSED"))
res.append(tryit("signed_by_other", lambda: run(okf("sb", body(signed_by="strategy"))), "REFUSED"))
res.append(tryit("signed_by_ARCH_case", lambda: run(okf("sbc", body(signed_by="ARCH"))), "ACCEPTED"))
res.append(tryit("out_dir_other", lambda: run(okf("od", body(out_dir="output/x"))), "REFUSED"))
res.append(tryit("short_sha", lambda: run(okf("ss", body(script_sha256="abc"))), "REFUSED"))
res.append(tryit("upper_sha", lambda: run(okf("us", body(script_sha256=SH["script_sha256"].upper()))), "REFUSED"))
for k in S.PINNED:
    res.append(tryit(f"sha_mismatch_{k}", lambda k=k: run(okf(f"mm_{k}", body(**{k: "0" * 64}))), "REFUSED"))
victim = T / S.PINNED["audit_csv_sha256"]; orig = victim.read_bytes(); victim.write_bytes(b"tampered")
res.append(tryit("pinned_file_tampered", lambda: run(okf("tamper", body())), "REFUSED")); victim.write_bytes(orig)
victim.unlink(); res.append(tryit("pinned_file_missing", lambda: run(okf("pm", body())), "REFUSED")); victim.write_bytes(orig)
res.append(tryit("out_dir_new", lambda: S.check_out_dir(T / "newdir"), "ACCEPTED"))
(T / "emptydir").mkdir(); res.append(tryit("out_dir_empty", lambda: S.check_out_dir(T / "emptydir"), "ACCEPTED"))
(T / "full").mkdir(); (T / "full" / "x").write_text("1"); res.append(tryit("out_dir_nonempty", lambda: S.check_out_dir(T / "full"), "REFUSED"))
(T / "afile").write_text("1"); res.append(tryit("out_dir_is_file", lambda: S.check_out_dir(T / "afile"), "REFUSED"))
# SPLIT pure function
st = pd.Series({"A": .05, "B": .04, "C": .04, "D": .04, "E": .02})
k = S.select_split(st, 2); ok = set(k.index) == {"A", "B", "C", "D"} and abs(k["B"] - .04 / 3) < 1e-15 and k["A"] == .05
print(("PASS" if ok else "FAIL") + " split_crossing_tie", dict(k)); res.append(ok)
k = S.select_split(st, 4); ok = set(k.index) == {"A", "B", "C", "D"} and k["B"] == .04
print(("PASS" if ok else "FAIL") + " split_no_crossing", dict(k)); res.append(ok)
eq = pd.Series({f"S{i:02d}": .04 for i in range(20)}); k = S.select_split(eq, 6)
ok = len(k) == 20 and abs(k.sum() - 6 * .04) < 1e-12; print(("PASS" if ok else "FAIL") + " split_all_equal", len(k), round(k.sum(), 6)); res.append(ok)
ok = S.SELECTABLE == () and len(S.VARIANTS) == 24 and S.SEEDS == list(range(1, 21)); print(("PASS" if ok else "FAIL") + " variant_list_fixed"); res.append(ok)
print(f"TOTAL {sum(res)}/{len(res)} PASS"); sys.exit(0 if all(res) else 1)
