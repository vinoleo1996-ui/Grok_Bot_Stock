# Strategy SW PIT r3e — /tmp 自测回执（合成数据，2026-10-18 ET）

- 依据：Arch 2026-10-18 12:09 ET 裁定（r3d 自测 8cef6e9d CONSUMED_FAIL：8 failed / 75 passed）。
- 范围：只在 /tmp/swr5/r3e_work 运行；未改真实 repo（本回执与两份 diff 除外，放 docs/v2/audit/）；未 commit；未碰任何 .ok；未读真实数据。
- 主审件：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3e_incremental.diff（sha256 4f1952ef0e278613ec6283ef071ccde6ae2471a35cfb9f65f641c01fd907f670）
- 完整版：docs/v2/audit/STRATEGY_SW_PIT_ASOF_TRADEDAY_PROPOSAL_20261018_r3e.diff（sha256 db151957a9bf17e90284e915edfd3b936c1083545a855b4b9b4171063eab533d）

## 1. 复制与 sha 核对（复制源 /tmp/swr5/c3d = r3d 工作副本；test_sw_pit_freshness.py 取自 /tmp/swr5/tsf_copy.py）
仓库里没有 research/__init__.py 或 conftest.py，测试文件自己 sys.path.insert(parents[2])，所以不需要另外复制。
```
复制前（源）：
research/sw_members_asof.py: OK
research/tests_sw_pit/test_sw_members_asof.py: OK
docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md: OK
research/strategy_hiliq_capadv_b4_x2.py: OK
research/strategy_fulla_b4_x2.py: OK
research/sw_pit_freshness.py: OK
cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e  tsf_copy.py
复制后（/tmp/swr5/r3e_work，sha256sum -c）：
research/sw_members_asof.py: OK
research/tests_sw_pit/test_sw_members_asof.py: OK
docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md: OK
research/strategy_hiliq_capadv_b4_x2.py: OK
research/strategy_fulla_b4_x2.py: OK
research/sw_pit_freshness.py: OK
research/tests_sw_pit/test_sw_pit_freshness.py: OK
EXIT=0
```

## 2. 锁检查与 pgrep
- 每次运行都经过 /tmp/swr5/r3e_work_log/run.sh：开头 set -euo pipefail，cd /tmp/swr5/r3e_work 后核对 pwd；用 `date +%H%M` 判断，落在禁跑时段（12:19–12:21、12:25–12:45、12:49–12:51）就中止；再用 `test -e /workspace/QuantLab/output/loop/RESEARCH_QUIET.lock` 检查锁，锁存在就中止。
- 结果：所有运行都记为 lock=absent，没有一次因禁跑时段中止，见第 3 节每行的 lock 字段。
- 最终运行前跑了 `bash /tmp/swr5/pgrep_check.sh`（2026-10-18 12:15:05 ET），输出：`EXIT=1 `，即 pgrep 没有匹配到任何进程。

## 3. 每次运行（/tmp/swr5/r3e_work_log/runs.md 原文）
环境：PYTHONDONTWRITEBYTECODE=1，PYTHONPATH=/tmp/swr5/r3e_work，nice -n 10，解释器 /workspace/ql-enrich-venv/bin/python（Python 3.13.5，pandas 3.0.6）。退出码用 `cmd; echo EXIT=$?` 记录。
```
# r3e /tmp runs (ET)
- [diag1] start=2026-10-18T12:11:53-04:00 end=2026-10-18T12:11:53-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python /tmp/swr5/r3e_work_log/diag1.py; echo EXIT=$?`
  - result: Series(objarr) str ['a', nan] Series(objarr,dtype=object) object ['a', None] EXIT=0  (full: /tmp/swr5/r3e_work_log/out_diag1.txt)
- [diag2] start=2026-10-18T12:12:10-04:00 end=2026-10-18T12:12:11-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python /tmp/swr5/r3e_work_log/diag2.py; echo EXIT=$?`
  - result: string string -> object ['a', None] [False, True] empty object -> object [] [] EXIT=0  (full: /tmp/swr5/r3e_work_log/out_diag2.txt)
- [run01_import_proof] start=2026-10-18T12:14:16-04:00 end=2026-10-18T12:14:16-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -c import sys, research.sw_members_asof as A, research.sw_pit_freshness as F; print('A', A.__file__); print('F', F.__file__); print('qlpaths', [p for p in sys.path if 'QuantLab' in p]); print('mods_from_QuantLab', [m.__name__ for m in list(sys.modules.values()) if 'QuantLab' in (getattr(m,'__file__','') or '')]); echo EXIT=$?`
  - result: qlpaths [] mods_from_QuantLab [] EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run01_import_proof.txt)
- [run02_collect] start=2026-10-18T12:14:16-04:00 end=2026-10-18T12:14:17-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --co research/tests_sw_pit; echo EXIT=$?`
  - result:  85 tests collected in 0.41s EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run02_collect.txt)
- [run03_full] start=2026-10-18T12:14:17-04:00 end=2026-10-18T12:14:20-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit; echo EXIT=$?`
  - result: .............                                                            [100%] 85 passed in 3.14s EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run03_full.txt)
- [run04_py_compile] start=2026-10-18T12:14:33-04:00 end=2026-10-18T12:14:33-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python /tmp/swr5/r3e_work_log/pycompile.py research/sw_members_asof.py research/sw_pit_freshness.py research/strategy_hiliq_capadv_b4_x2.py research/strategy_fulla_b4_x2.py research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py; echo EXIT=$?`
  - result:     raise FileExistsError(msg.format(cfile)) FileExistsError: /dev/null is a non-regular file and will be changed into a regular one if import writes a byte-compiled file to it EXIT=1  (full: /tmp/swr5/r3e_work_log/out_run04_py_compile.txt)
- [run05_pyflakes] start=2026-10-18T12:14:33-04:00 end=2026-10-18T12:14:33-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pyflakes research/sw_members_asof.py research/sw_pit_freshness.py research/strategy_hiliq_capadv_b4_x2.py research/strategy_fulla_b4_x2.py research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py; echo EXIT=$?`
  - result: /workspace/ql-enrich-venv/bin/python: No module named pyflakes EXIT=1  (full: /tmp/swr5/r3e_work_log/out_run05_pyflakes.txt)
- [run06_full_header] start=2026-10-18T12:14:33-04:00 end=2026-10-18T12:14:36-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -p no:cacheprovider research/tests_sw_pit; echo EXIT=$?`
  - result:  ============================== 85 passed in 3.14s ============================== EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run06_full_header.txt)
- [run07_py_compile] start=2026-10-18T12:14:57-04:00 end=2026-10-18T12:14:57-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python /tmp/swr5/r3e_work_log/pycompile.py research/sw_members_asof.py research/sw_pit_freshness.py research/strategy_hiliq_capadv_b4_x2.py research/strategy_fulla_b4_x2.py research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py; echo EXIT=$?`
  - result: OK research/tests_sw_pit/test_sw_members_asof.py OK research/tests_sw_pit/test_sw_pit_freshness.py EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run07_py_compile.txt)
- [run08_pyflakes] start=2026-10-18T12:14:57-04:00 end=2026-10-18T12:14:57-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 env PYTHONPATH=/tmp/swr5/r3e_work:/tmp/pf /workspace/ql-enrich-venv/bin/python -m pyflakes research/sw_members_asof.py research/sw_pit_freshness.py research/strategy_hiliq_capadv_b4_x2.py research/strategy_fulla_b4_x2.py research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py; echo EXIT=$?`
  - result: research/strategy_hiliq_capadv_b4_x2.py:671:5: local variable 'charts2' is assigned to but never used research/strategy_fulla_b4_x2.py:180:5: local variable 'nav_path' is assigned to but never used EX (full: /tmp/swr5/r3e_work_log/out_run08_pyflakes.txt)
- [run09_py_compile_module] start=2026-10-18T12:15:05-04:00 end=2026-10-18T12:15:05-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python /tmp/swr5/r3e_work_log/pycompile2.py research/sw_members_asof.py research/sw_pit_freshness.py research/strategy_hiliq_capadv_b4_x2.py research/strategy_fulla_b4_x2.py research/tests_sw_pit/test_sw_members_asof.py research/tests_sw_pit/test_sw_pit_freshness.py; echo EXIT=$?`
  - result: py_compile OK research/tests_sw_pit/test_sw_members_asof.py py_compile OK research/tests_sw_pit/test_sw_pit_freshness.py EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run09_py_compile_module.txt)
- [pgrep_check] 2026-10-18T12:15:05-04:00 bash /tmp/swr5/pgrep_check.sh -> EXIT=1 
- [run10_FINAL] start=2026-10-18T12:15:05-04:00 end=2026-10-18T12:15:09-04:00 lock=absent pwd=/tmp/swr5/r3e_work
  - cmd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit; echo EXIT=$?`
  - result: .............                                                            [100%] 85 passed in 3.34s EXIT=0  (full: /tmp/swr5/r3e_work_log/out_run10_FINAL.txt)
```
说明：
- diag1 在改代码之前跑，对象是 r3d 原样副本，用来定位 nan 的来源。
- run04 失败：py_compile 不能把 cfile 设成 /dev/null，属于脚本错误。run07 改用 compile() 重做，run09 用 py_compile 写到 /tmp 的 cfile 再做一次（目录随后删除），两次都是 EXIT=0。
- run05 失败：ql-enrich-venv 里没有装 pyflakes。run08 改为从 /tmp/pf 加载 pyflakes 后重跑。
- 没经过 run.sh、直接用 ql-enrich-venv 跑过两次 python：/tmp/swr5/r3e_work_log/edit_mod.py（12:12:54 ET）和 edit2.py（12:13:33 ET）。这两个是纯文本替换的改码脚本，只读写 /tmp/swr5/r3e_work 下的文件，不 import QuantLab，也没落在禁跑时段。

## 4. 导入路径证明（run01、run06）
```
A /tmp/swr5/r3e_work/research/sw_members_asof.py
F /tmp/swr5/r3e_work/research/sw_pit_freshness.py
qlpaths []
mods_from_QuantLab []
EXIT=0
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/swr5/r3e_work
collected 85 items
```

## 5. nan 根源（diag1：r3d 原样副本，合成数据）
```
module_file /tmp/swr5/r3e_work/research/sw_members_asof.py
pandas 3.0.6 future.infer_string True
norm1 object [nan]
norm2 object [nan, '600018.SH']
init object [nan, nan]
after_empty_assign object [nan]
Series(objarr) str ['a', nan]
Series(objarr,dtype=object) object ['a', None]
EXIT=0
```
结论：pandas 3 默认开启 future.infer_string。
- l1_asof 和 sw_l1_asof_chunked 用 pd.Series(<object ndarray>) 构造返回值，没有指定 dtype，结果被推断成 "str" dtype，缺失值就成了 nan。8 个失败里有 7 个是这个原因。
- pd.Series(None, index=..., dtype=object) 在 pandas 3 下填的是 nan，不是 None，这导致了 _norm_a_share 那 1 个失败。
- out[mask]= 赋值和 merge 都不是原因。

## 6. 最终运行（run10_FINAL）输出原文
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/swr5/r3e_work nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider research/tests_sw_pit; echo EXIT=$?
........................................................................ [ 84%]
.............                                                            [100%]
85 passed in 3.34s
EXIT=0
```
计数：85 passed（原有 83 个加新增 2 个），failed、error、skipped 都是 0。run06 不带 -q 跑了同样的测试，表头显示 rootdir 是 /tmp/swr5/r3e_work，collected 85 items，其中 test_sw_members_asof.py 73 个、test_sw_pit_freshness.py 12 个。

## 7. 静态检查
```
OK research/sw_members_asof.py
OK research/sw_pit_freshness.py
OK research/strategy_hiliq_capadv_b4_x2.py
OK research/strategy_fulla_b4_x2.py
OK research/tests_sw_pit/test_sw_members_asof.py
OK research/tests_sw_pit/test_sw_pit_freshness.py
EXIT=0
research/strategy_hiliq_capadv_b4_x2.py:671:5: local variable 'charts2' is assigned to but never used
research/strategy_fulla_b4_x2.py:180:5: local variable 'nav_path' is assigned to but never used
EXIT=1
```
pyflakes 只报了基线就有的 2 条（hx2 的 charts2、fulla 的 nav_path）。

## 8. diff 验证（分别在两个基线的新副本上 git apply --check 再 apply，然后对 r3e_work 做 diff -r）
- inc 的基线是 /tmp/swr5/c3d。
- full 的基线是 /tmp/swr5/b2，另外补上未改动的 test_sw_pit_freshness.py（cee59fc5）。
```
apply_inc EXIT=0
diff_r_inc EXIT=0
apply_full EXIT=0
diff_r_full EXIT=0
```

## 9. 清理与最终 sha
- /tmp/swr5/r3e_work 里的 __pycache__ 和 .pytest_cache 已经清掉，复查为 0 个。
- 真实 repo 的 research/ 下原本就有 2 个 __pycache__（mtime：research/intel/__pycache__ 06:23 ET，research/__pycache__ 09:06 ET），不是本轮产生的，没有动。
```
28b89a61310a582f34f7447e2695d1698f75ff8e31e39c3e6e08a73b186bd2b5  ./docs/v2/STRATEGY_SW_PIT_ASOF_FIX_PREREG_ZH.md
fa2e4629eea11e81ab9928ef071759e813f50fd0aae162f79f68e44df1b5bf1b  ./research/strategy_fulla_b4_x2.py
7b8235dc75a8003993e155fe28924882e1d112117a2a8542c26e292db66b60a1  ./research/strategy_hiliq_capadv_b4_x2.py
dec73305f8cd49d2c4ad695f72158e10bceb20de83fa19b2a1580be08579a9a7  ./research/sw_members_asof.py
5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f  ./research/sw_pit_freshness.py
e80f98ed778dbb82d096716fc87c76306fe14d887c177015e623e534514794cc  ./research/tests_sw_pit/test_sw_members_asof.py
cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e  ./research/tests_sw_pit/test_sw_pit_freshness.py
```
