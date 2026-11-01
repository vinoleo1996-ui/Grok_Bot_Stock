# P2-2 修复回执 r6c（2026-10-18 ET，QuantLab Data）
- 范围：只改代码和文档，只做编译。py_compile 输出到 /tmp/pyc_r6c，仓库里没有 __pycache__。
- 没有运行单测，也没有运行任何脚本：单测文件的 sha 已变，需要先拿新的 selftest .ok。
- 改动前的快照：_recovery/data/sd1_r6c_pre_20261018/（SHA256SUMS 的 sha 为 7ccc9ac8c6608fce5720084cbe5821bb9507e02d2428351cbefc95bfbf330d51）
- 改动后的快照：_recovery/data/sd1_r6c_20261018/（SHA256SUMS 的 sha 为 f8e1e854931c74d2549edb8226a7081ee1649a34b7082a6fe98f5bcbffb71911）

## sha 变更（旧 → 新）
| 文件 | 旧 | 新 |
|---|---|---|
| scripts/fix_sd1/sd1_common.py | c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa | 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9 |
| scripts/fix_sd1/build_stock_delisted_v2.py | a641626f42defe2d2ece3b7457ecfa76fac40e460387483dcdcd885e87f0d732 | 34e4689929bc02a42fabdb1642b46e511c61717986179a46c8029d18b2730ba5 |
| scripts/fix_sd1/build_cs_panel_v2_resumefix.py（只改 COMMON_SHA256） | 4b40b6b8b43eef4511aea07343c439a7691dfb23bcf89113432946c5dfb4cd21 | 6e2e127393fed6f089c69041d18e0e4181794de11e63c6174c31a0719e47de27 |
| scripts/fix_sd1/build_suspend_flags_v2.py（只改 COMMON_SHA256） | 53013099315348fd21a12673270aebca2204810f5868653eed22ad4c5e69ce73 | 6b8fd0330b7aa00eccb91a41d6d9da29eaf1eb096abfe12c314f759ac5baaa30 |
| scripts/fix_sd1/test_sd1_common.py | 892401e5ec99e6471f5aa3a18ab68bf9adcd2c28cd1b9cc868f95cbb8cbed32f | 7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325 |
| docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md（追加 r6c 记录） | dd84efe8ff63ae3657d99d31ac3bb39927e80c458df69033bc56012093bf492a | 903e64ef439415c4e7b158e8151985fc309ef288a2f39ec322fc1a66707b89e3 |
| docs/v2/DATA_CS_PANEL_RESUME_REBUILD_PLAN_ZH.md | 362e323994d3e40181ee2f26da3864c5fdf4720c0b1f1a5e35b095652eec3bbe | **未变** |
- 数据 pin 全部未变（mask、9 个 v1 cs_panel、float_mktcap、sw_l1、stock_delisted_v1、namechange_all、delisted_daily）。

## 改动说明
- **P2-2**：原断言 `set(MANUAL_OVERRIDE) != {"002509.SZ"}` 检查的是常量，恒为真，现改为对输出行调用 C.check_manual_override。它要求：
  1. delist_period_source=="manual_override" 的代码集合恰为 {002509.SZ}；
  2. 该行 delist_period_start 为 20200604；
  3. 来源字段（source_ann_no 非空或 override_source_verified=True）只出现在 manual_override 行。
  - 任何一条不满足都 VOID。期望值 {"002509.SZ": "20200604"} 写死在调用处，不从 MANUAL_OVERRIDE 常量派生。
- **第 61 行**：来源字段赋值从 `x.ts_code == c` 改为掩码 `k`（只写被覆盖的行）。002509.SZ 在 namechange 里没有"退"记录，k 只命中它那一行，所以输出与 v3 dry-run 相同。stdout 格式没有改。
- **单测**：新增 6 个合成用例：通过、多代码、缺代码、period_start 错、非覆盖行带 source_ann_no、非覆盖行带 verified。纯函数，不读真实数据。尚未运行。

## P3-10 结论（只读调查，没有运行项目代码）
- 20261014 来自 sd1_common.mask_last_date() = universe_mask_hiliq_v1.parquet 的最大日期，只被 D1（cs_panel）和 D2（suspend_flags）使用。
- build_stock_delisted_v2.py 里没有任何日期截止（grep CUTOFF、mask_last、cutoff 都为空）。
- D3D4 的覆盖范围完全由冻结的 data/v2/ref/stock_delisted.parquet 决定：339 行，最大 delist_date 20260730；delisted_daily 的最大交易日为 2026-07-29，共 338 个代码。
- 上游 meta/stock_basic_incl_delisted.parquet（10-12 构建）：list_status=D 共 339 个，最大 delist_date 20260730，delist_date>20260730 的为 0 个，D 状态代码全部在 master 里。
- 结论：07-30 到 10-14 之间没有退市记录，是因为源表（10-12 快照）里本来就没有，不是被 20261014 截止排除的。
- 已知缺口：301139.SZ（元道退）。namechange 显示 2026-09-30 已进入退市整理期，但 stock_basic 中仍为 L、没有 delist_date，所以不在 master 里，本版 D3D4 不覆盖。要等 stock_basic 和 stock_delisted 刷新（这需要新的数据 pin）以后另行处理。

## 仍需的新 .ok
1. dry-run v4 .ok（取代 v3 dac5f6dd），代码 pin 更新为：
   - script_cs_panel_sha256=6e2e127393fed6f089c69041d18e0e4181794de11e63c6174c31a0719e47de27
   - script_suspend_flags_sha256=6b8fd0330b7aa00eccb91a41d6d9da29eaf1eb096abfe12c314f759ac5baaa30
   - script_stock_delisted_sha256=34e4689929bc02a42fabdb1642b46e511c61717986179a46c8029d18b2730ba5
   - common_sha256=542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9
   - plan_sd_fix_sha256=903e64ef439415c4e7b158e8151985fc309ef288a2f39ec322fc1a66707b89e3
   - plan_cs_panel_sha256 不变（362e3239…）；test_sd1_common_sha256=7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325
   - 至少需要重跑 D3D4 dry-run，以验证新断言在真实数据上通过。D1、D2 的逻辑没变，但 pin 变了，是否重跑由 Arch 裁定。
2. 新的 selftest .ok（取代 a7159eca），在原路径 output/data/ARCH_RUN_AUTH_SELFTEST_SD1_COMMON.ok 替换：
   - runner test_sd1_common.py=7dbcf5d38e2874c1ccf53614cdae94826b51560056c904e77f4d418d2fcec325
   - dep sd1_common=542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9
3. 之后再签 execute .ok，带两个期望值键：expected_face_value_recategorised=000861.SZ,002505.SZ,002509.SZ,600297.SH；expected_unknown_needs_source_count=56。

## unified diff
```diff
--- _recovery/data/sd1_r6c_pre_20261018/build_cs_panel_v2_resumefix.py	2026-10-18 02:26:20.884683904 -0400
+++ scripts/fix_sd1/build_cs_panel_v2_resumefix.py	2026-10-18 05:00:27.649122197 -0400
@@ -16,7 +16,7 @@
 import sys, hashlib
 from pathlib import Path
 HERE = Path(__file__).resolve().parent
-COMMON_SHA256 = "c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa"
+COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
 def _sha(p):
     h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
 if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
--- _recovery/data/sd1_r6c_pre_20261018/build_suspend_flags_v2.py	2026-10-18 02:26:20.888683904 -0400
+++ scripts/fix_sd1/build_suspend_flags_v2.py	2026-10-18 05:00:27.653122197 -0400
@@ -27,7 +27,7 @@
 import sys, hashlib
 from pathlib import Path
 HERE = Path(__file__).resolve().parent
-COMMON_SHA256 = "c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa"
+COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
 def _sha(p):
     h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
 if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
--- _recovery/data/sd1_r6c_pre_20261018/build_stock_delisted_v2.py	2026-10-18 02:26:20.888683904 -0400
+++ scripts/fix_sd1/build_stock_delisted_v2.py	2026-10-18 05:00:27.653122197 -0400
@@ -22,7 +22,7 @@
 import sys, hashlib
 from pathlib import Path
 HERE = Path(__file__).resolve().parent
-COMMON_SHA256 = "c275e15250942553529cc101d8302ec641f0b216150649e0a118a71a4b7d07fa"
+COMMON_SHA256 = "542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9"
 def _sha(p):
     h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
 if _sha(HERE / "sd1_common.py") != COMMON_SHA256: raise SystemExit("SD1 gate blocked: sd1_common.py sha256 mismatch")
@@ -58,7 +58,7 @@
         k = (x.ts_code == c) & x.delist_period_start.isna()
         x.loc[k, "delist_period_start"] = o["delist_period_start"]; x.loc[k, "delist_period_ann_date"] = o["delist_period_ann_date"]
         x.loc[k, "delist_period_source"] = "manual_override"
-        for f in ["override_source_verified", "source_ann_no", "source_url", "source_published_date"]: x.loc[x.ts_code == c, f] = o[f]
+        for f in ["override_source_verified", "source_ann_no", "source_url", "source_published_date"]: x.loc[k, f] = o[f]   # r6c P2-2: only on the overridden row(s)
     x["delist_period_end"] = pd.to_datetime(x.last_trade_date).dt.strftime("%Y%m%d")
     g = {k: v for k, v in dd.groupby("ts_code")}
     def ndays(r):
@@ -128,7 +128,9 @@
     if EXPECT["face"] is not None and sorted(set(face)) != EXPECT["face"]: ST.void(f"face-value recategorised {sorted(set(face))} != .ok expected {EXPECT['face']}")
     if EXPECT["unknown_count"] is not None and len(st["unknown_needs_source"]) != EXPECT["unknown_count"]:
         ST.void(f"unknown_needs_source {len(st['unknown_needs_source'])} != .ok expected {EXPECT['unknown_count']}")
-    if set(MANUAL_OVERRIDE) != {"002509.SZ"}: ST.void(f"manual_override must be exactly 002509.SZ, got {sorted(MANUAL_OVERRIDE)}")
+    # r6c Arch P2-2: assert on actual output rows (was a constant check, always true)
+    mo_err = C.check_manual_override(zip(x.ts_code, x.delist_period_source, x.delist_period_start, x.source_ann_no, x.override_source_verified), {"002509.SZ": "20200604"})
+    if mo_err: ST.void("manual_override row check failed: " + "; ".join(mo_err))
     ST.guard("end")
     man = {"step": STEP, "version": "stock_delisted_v2", "mode": "execute" if EXEC else "dryrun", "ok_path": KV["_ok_path"], "ok_sha256": KV["_ok_sha256"],
            "pins": PINS, "prev_receipt_sha256": PREV, "common_sha256": COMMON_SHA256, "join_key": "ts_code", "run_conditions": KV["_run_conditions"], "stats": st, "status": "PASS",
--- _recovery/data/sd1_r6c_pre_20261018/sd1_common.py	2026-10-18 02:26:20.804683904 -0400
+++ scripts/fix_sd1/sd1_common.py	2026-10-18 05:00:27.621122197 -0400
@@ -364,3 +364,22 @@
             raise ValueError(f"resume without prior trade for non-seeded {code} (ResumeState invariant)")
         return False, False, "", "unknown_first_trade_in_data"
     return False, False, "", "unknown_no_normal_session"
+
+def check_manual_override(rows, expected) -> list:
+    """r6c Arch P2-2 (pure): assert manual_override on the ACTUAL D3D4 output rows, not on the constant.
+    rows: iterable of (ts_code, delist_period_source, delist_period_start, source_ann_no, override_source_verified).
+    expected: {ts_code: period_start 'YYYYMMDD'}. Returns a list of violations (empty = pass); caller VOIDs.
+    Rules: codes with source=='manual_override' == set(expected); each such row's period_start == expected[code];
+    override source fields (source_ann_no non-empty or override_source_verified True) only on manual_override rows."""
+    errs, seen = [], set()
+    for code, src, start, ann_no, verified in rows:
+        is_mo = src == "manual_override"
+        if is_mo:
+            seen.add(code)
+            if code in expected and str(start) != expected[code]:
+                errs.append(f"{code} manual_override period_start {start!r} != {expected[code]}")
+        elif (isinstance(ann_no, str) and ann_no) or verified is True or str(verified) == "True":
+            errs.append(f"{code} carries override source fields but delist_period_source={src!r}")
+    if seen != set(expected):
+        errs.append(f"manual_override codes {sorted(seen)} != expected {sorted(expected)}")
+    return errs
--- _recovery/data/sd1_r6c_pre_20261018/test_sd1_common.py	2026-10-18 02:26:20.804683904 -0400
+++ scripts/fix_sd1/test_sd1_common.py	2026-10-18 05:00:27.645122197 -0400
@@ -103,6 +103,15 @@
         try: pe(badkv, ex); raise AssertionError("should block")
         except SystemExit: pass
     C.parse_run_auth(w({**base, **ok2}))                                                               # keys accepted by the parser
+    # r6c Arch P2-2: manual_override row check (pure)
+    cm = C.check_manual_override; E = {"002509.SZ": "20200604"}
+    good = [("002509.SZ", "manual_override", "20200604", "深证上【2020】442号", True), ("600297.SH", "namechange", "20240801", "", False), ("000001.SZ", "", None, "", False)]
+    assert cm(good, E) == [], cm(good, E)
+    assert cm(good + [("000002.SZ", "manual_override", "20200101", "x", True)], E)                    # extra code
+    assert cm([r for r in good if r[0] != "002509.SZ"], E)                                             # missing code
+    assert cm([("002509.SZ", "manual_override", "20200605", "a", True)] + good[1:], E)                 # wrong period_start
+    assert cm(good + [("000003.SZ", "namechange", "20190101", "leaked", False)], E)                    # source field on non-override row
+    assert cm(good + [("000004.SZ", "", None, "", True)], E)                                           # verified flag on non-override row
     import shutil; shutil.rmtree(d)
     print("ALL SYNTHETIC TESTS PASS")
 run()
--- _recovery/data/sd1_r6c_pre_20261018/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md	2026-10-18 02:26:26.808683904 -0400
+++ docs/v2/DATA_SUSPEND_DELIST_FIX_PLAN_ZH.md	2026-10-18 05:00:33.469122197 -0400
@@ -134,3 +134,20 @@
   - 差集内各只和这 4 只的"进入整理期之前 20 个收盘价"窗口：起止日、收盘价个数、最高收盘价、v1/v2 类别、face_flag；
   - UNKNOWN 数与 56 的对账（measured / diag / diff）。
 - **流程**：Arch 按 v3 dry-run 实测清单审定后，把这两个值写进 execute .ok。
+
+## r6c 记录（2026-10-18 ET，QuantLab Data；v3 四步 dry-run 审完之后）
+- **P2-2（Arch r6b）**：manual_override 的断言原先检查的是常量，恒为真，现改为检查实际输出行。
+  - 新增纯函数 sd1_common.check_manual_override，要求：
+    1. delist_period_source=="manual_override" 的代码集合恰为 {002509.SZ}；
+    2. 该行 period_start 为 20200604；
+    3. override 来源字段（source_ann_no 非空或 override_source_verified=True）只出现在 manual_override 行。
+  - 任何一条不满足都 VOID。
+  - build_stock_delisted_v2.py 原第 61 行的来源字段赋值，从"该代码所有行"改为"仅被覆盖的行"（掩码 k）。002509.SZ 在 namechange 中没有"退"记录，所以本次输出不变。
+  - test_sd1_common.py 新增合成用例：通过、多代码、缺代码、period_start 错、非覆盖行带来源字段、非覆盖行带 verified。
+  - sd1_common 的 sha 变为 542dd13650979983f926778d5c7ea39a6f6e7655c2ac40ed1823601eb45ba4b9，三个 build 脚本里写死的 COMMON_SHA256 已同步更新。
+- **P3-10（20261014 截止）**：
+  - 20261014 来自 sd1_common.mask_last_date()，即 output/strategy_hiliq/universe_mask_hiliq_v1.parquet 的最大日期，只用于 D1、D2。
+  - build_stock_delisted_v2.py（D3D4）没有日期截止。它的覆盖范围完全由冻结的 data/v2/ref/stock_delisted.parquet（v1，339 行）决定；v1 表来源是 meta/stock_basic_incl_delisted（10-12 构建，list_status=D 共 339 个，最大 delist_date 20260730）。
+  - 07-30 到 10-14 之间没有记录，是因为源表里本来就没有，不是被截止排除的：stock_basic 中 delist_date>20260730 的为 0 个，D 状态代码全部在 master 里。
+  - 已知待退：301139.SZ（元道退，namechange 2026-09-30 进入整理期，stock_basic 仍为 L），本版不覆盖，需等 stock_basic 刷新以后另行处理。
+- 以上改动使 v3.ok 的 pin（script_cs_panel / script_suspend_flags / script_stock_delisted / common / plan_sd_fix）和单测 .ok（runner、dep）失效，需要 Arch 重签。
```
