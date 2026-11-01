# SD1 selftest r3.1 回执（Eng；写于 2026-10-18T03:05:12-04:00，America/New_York）

- 结论：**2 个失败 / 42 个通过 / 1 个跳过**，pytest 返回 1。按指示只跑了一次，没有重跑，也没有改任何钉住的文件。
- 两个失败是同一个原因：r3 测试要求守卫抛出的异常类型**恰好是** PermissionError，而 delist_accounting 222b63ae（r2 起未变）抛的是它的子类 `StrategyLayerDelistAccess(PermissionError)`（delist_accounting.py L64、L87）。守卫本身工作正常：拦住了，抛的不是 TypeError，pytest.raises(PermissionError) 也通过了。属测试断言问题，不是引擎问题。修法待 Arch 裁定（§6）。
- T10 pinned 范围扫描（test_static_check_pinned_scope）和函数白名单（test_static_check_function_whitelist）**都通过**，闭包 156/156 一致。
- 依据：ARCH_SD1_TEST.ok b6a0a3c6e571b45f45c2e75fb56efad9951869577352f869f1084dc916b2c090（signed_et 2026-10-18T03:00:48-04:00，expires_et 2026-10-19T02:56:00-04:00）；Arch 复审 docs/v2/ARCH_SD1_R3_1_REVIEW_ZH.md e2e288bc910a45f7f797c131ca66db7ac3600d5c71c84d3ce1f66505c2c64855。live=false · promotion=false

## 1. 运行前检查（03:02–03:03 ET）
- .ok：docs/v2/eng_sd1/ARCH_SD1_TEST.ok，sha256 b6a0a3c6e571b45f45c2e75fb56efad9951869577352f869f1084dc916b2c090，与指令一致。
- 测试文件：tests/test_sd1_suspend_delist.py 70ddd427cbd8905758ff4b66f934b2155b425fcecdddaf089c826b82b041711a，等于 .ok 里的 runner_sha256_test_sd1_suspend_delist。
- 69 个 dep：从测试文件里用 ast 读出 TEST_DEPS（不 import），逐个重算 sha，与 .ok 的 69 个 dep_sha256_* 一一相等。两边都没有多出来的键，没有不一致。
- 闭包：paper_import_closure.json 6919e7af 中的 156 项逐个重算，156/156 一致。
- 环境：QL_SD1_REAL_DATA 未设置。解释器 /workspace/qlvenv/bin/python，Python 3.12.14（main, Sep 24 2026, 17:57:43）[Clang 22.1.3]；pytest 9.1.1（经 importlib.metadata 读取，没有运行 pytest）。
- 进程检查：
  - 没有 fix_sd1、cs_panel、D-1~D-4 重建在跑，也没有 pytest 或 research 计算进程。
  - 以下 Data 采集进程都处于 S 态，3 秒内 CPU 增量约为 0，判定为不冲突：
    - 94403 relay_outage_backfill，以及它下面的 212762 nightly_update --steps sw 和 212763 sw_pit_refresh
    - 94322 remaining_after_stk_surv
  - 另有 Web 的 server.py 80415，以及另一个 agent 的空闲 `python3 -` 229607（11.7MB，02:37 起等待 stdin，CPU 增量 0）。
  - load 0.91，可用内存约 11.1GB。
- 基线：
  - `ls -d /tmp/sd1_selftest_*` → No such file or directory。
  - 仓内所有 __pycache__ 和 .pytest_cache 的完整清单（含 mtime 和大小）共 1894 行，存于 /workspace/sd1_work/selftest_r3_1/cache_before.txt，sha f97c221d…5ac5。
  - tests/__pycache__ 为空。.pytest_cache 是 01:17:48 的旧目录。

## 2. 命令
```
cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider
```
- 这条命令外面包了一层 /workspace/sd1_work/selftest_r3_1/rss_wrap.py（sha 82b12cc3d5cfd8c1dbc5a02a8792663810c0e51cf41e04a5c8f3a65ce18c4939）。包装器只用标准库，不 import quantlab，由系统 python3 -B 运行。它做三件事：
  - 每 0.1 秒沿 /proc 的 PPid 找出整棵进程树，读每个进程的 VmRSS 和 VmHWM；
  - 树上 VmRSS 之和超过 1536MB 就整树 SIGKILL；
  - 子进程结束后读 getrusage(RUSAGE_CHILDREN).ru_maxrss。
- 开始 2026-10-18T03:03:44-04:00，结束 2026-10-18T03:03:47-04:00，用时 3.55 秒，pytest 返回 1。

## 3. 内存（方法：/proc 每 0.1 秒采样整棵树，加 VmHWM，加 RUSAGE_CHILDREN）
- 采样 33 次；进程树最多同时 2 个进程，共见到 3 个 pid（pytest，以及 T10/T11 起的子进程）。
- 树上 VmRSS 之和峰值 **272.8 MB**；单进程 VmHWM 峰值 **159.1 MB**；RUSAGE_CHILDREN 的 ru_maxrss 为 **158.6 MB**（单个进程的最大值，包含已回收的孙进程）。
- 远低于 1536MB，没有触发强杀（killed_over_cap=false）。原始数据在 /workspace/sd1_work/selftest_r3_1/rss.json，sha b7f868001c8828d47e7c7f4e83fb4b8cefbb03cdb721c3e6c6447c110a7ea036。

## 4. 运行后清理核对
- `ls -d /tmp/sd1_selftest_*`：运行前没有，运行后也没有（No such file or directory），mkdtemp 目录已被清掉。
- __pycache__ 和 .pytest_cache：运行后的清单 cache_after.txt 共 1894 行，sha f97c221d…5ac5，**与运行前逐字节相同**（diff 为空，没有新增或修改，mtime 也没变）。没有生成任何 cpython-312 的新 pyc。
- 运行期间（03:03:43–03:03:49）仓内其他新写入的文件，都来自别的 agent：Data 的 data/v2/tushare_raw/fund_portfolio_dh/…，以及 research/_runner_archive/MANIFEST.md 和 research/alpha_combo_marginal_v1_1.py。测试只写 mkdtemp 目录，没有写 output/。
- 运行后复核 sha：.ok b6a0a3c6、测试 70ddd427、execution 373fed30、__init__ bfdfa63c、ok_runner_pin c7805d9a、delist_accounting 222b63ae，全部未变。

## 5. 结果
- 通过 42、失败 2、跳过 1。跳过的是 T13 真实数据用例（`@skipUnless(REAL_DATA, …)`，L738），这是预期行为。
- 失败 1：T10PitGuard.test_strategy_caller_raises（测试 L584 `assertIs(type(ei.value), PermissionError)`），实际异常类型是 StrategyLayerDelistAccess。
- 失败 2：T11OptimizeFlag.test_guards_under_python_O（测试 L681 要求出现 'GUARD_EXC PermissionError'），实际输出是 ['debug False', 'GUARD_EXC StrategyLayerDelistAccess', 'NOSRC_EXC TypeError', 'CFG_RAISED', 'DL_RAISED']。这说明在 -O 下守卫照样拦截，不带 source 的调用照样是 TypeError，两个 ExecConfig 校验也都抛了异常，只有类型名对不上。
- r2 时 T1、T3 失败；r3.1 下 T1 拆出的 4 个用例、权重型引擎用例、T3 和 T9 都在这 42 个通过里（-q 模式不逐个打印名字，按测试总数推算）。

## 6. 定性和待裁定（没有修改，等 Arch）
- 根因：r3 把 Arch 裁定 2「用精确类型，不许捕获基类」理解成了异常类型必须恰好是 PermissionError，但守卫按 r2 设计抛的是它的专用子类 StrategyLayerDelistAccess。pytest.raises(PermissionError) 会接受子类，所以 L583 那行通过了，是后面 L584 的类型全等断言失败。TypeError 和 PermissionError 之间仍然互不混淆：NOSRC 用例通过，T11 的 NOSRC 输出也是 TypeError。
- r3.2 的两个修法，请 Arch 选一个：
  - (a) 只改测试：L584 改成 `assertIs(type(ei.value), DA.StrategyLayerDelistAccess)`，再加 `issubclass(…, PermissionError)` 且 `not issubclass(…, TypeError)`；T11 改成期望 'GUARD_EXC StrategyLayerDelistAccess'。只有测试文件的 sha 会变，TEST.ok 只需换 runner_sha256 一个值。
  - (b) 改 delist_accounting，让它直接抛 PermissionError。会改动 dep 222b63ae，不建议。
  - Eng 建议选 (a)。
- 这次不影响纸面：execution.py 仍是 373fed30，SD0 路径没有改动。EXEC.ok 继续作废；SD0 对拍仍要等单测全部通过、Arch 审完回执之后。

## 7. 排进下一版的 Arch r3.1 P3（这次没做）
- test_static_check_pinned_scope：把 scanned_research 改名为 research_hits；增加 n_scanned（162 个候选文件，按 SCOPE 实际扫了 77 个）。
- pinned 模式要核对 --files 的 sha：传入 sha 列表，或者在 T10 之前重算 deps。
- docstring 写明：只要外层任意一层 def 的名字在白名单里就放行（嵌套函数同样适用）。
- --paths 和 --mode 改成 argparse 的互斥组。
- 订正：闭包里有 16 个 research 文件，都扫过，0 条命中。所以「没有 research 文件被扫到」应改为「research 文件 0 条命中」。r3.1 回执和测试注释里的说法不准确，下一版一并改。

## 8. pytest 原始输出（/workspace/sd1_work/selftest_r3_1/pytest_raw.log，sha 2317b5c7d6ffd801b7db5a66b417a698343cc36d6901fda9b488b07266e234ca）
```
........................FF....s..............                            [100%]
=================================== FAILURES ===================================
___________________ T10PitGuard.test_strategy_caller_raises ____________________

self = <test_sd1_suspend_delist.T10PitGuard testMethod=test_strategy_caller_raises>

    def test_strategy_caller_raises(self):
        # r3: the planted strategy call passes a valid source, so only the PIT guard can stop it -> exactly PermissionError
        for fake in FAKE_CALLERS:
            with pytest.raises(PermissionError) as ei:
                exec(compile(PLANTED, str(ROOT / fake), "exec"), {})
>           self.assertIs(type(ei.value), PermissionError)
E           AssertionError: <class 'quantlab.platform.delist_accounting.StrategyLayerDelistAccess'> is not <class 'PermissionError'>

tests/test_sd1_suspend_delist.py:584: AssertionError
__________________ T11OptimizeFlag.test_guards_under_python_O __________________

self = <test_sd1_suspend_delist.T11OptimizeFlag testMethod=test_guards_under_python_O>

    def test_guards_under_python_O(self):
        code = "\n".join([
            "import sys", f"sys.path.insert(0, {str(ROOT)!r})",
            "print('debug', __debug__)",
            "from quantlab.platform import delist_accounting as DA",
            f"for _k in list(DA.DELIST_SOURCES): DA.DELIST_SOURCES[_k] = __import__('pathlib').Path({str(OUT_DIR)!r}) / ('_absent_' + _k)",
            "try:",
            f"    exec(compile({PLANTED!r}, {str(ROOT / 'research/_sd1_planted_strategy.py')!r}, 'exec'), {{}})",
            "    print('GUARD_NO_RAISE')",
            "except BaseException as e:",
            "    print('GUARD_EXC', type(e).__name__)",
            "try:",
            f"    exec(compile({PLANTED_NOSRC!r}, {str(ROOT / 'research/_sd1_planted_strategy.py')!r}, 'exec'), {{}})",
            "    print('NOSRC_NO_RAISE')",
            "except BaseException as e:",
            "    print('NOSRC_EXC', type(e).__name__)",
            "from quantlab.platform import execution_sd1 as E",
            "try:",
            "    E.ExecConfig(halt_policy='bogus'); print('CFG_NO_RAISE')",
            "except ValueError:",
            "    print('CFG_RAISED')",
            "import pandas as pd",
            "try:",
            "    E.run_weight_schedule(E.ExecPanels(close=pd.DataFrame({'600001.SH': [1.0]}, index=pd.bdate_range('2024-01-02', periods=1))), {}, config=E.ExecConfig(delist_policy='sd1'))",
            "    print('DL_NO_RAISE')",
            "except ValueError:",
            "    print('DL_RAISED')",
            ""])
        out = subprocess.run([sys.executable, "-O", "-c", code], capture_output=True, text=True, cwd=str(ROOT),
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")).stdout
        self.assertIn("debug False", out)
        lines = out.splitlines()
>       self.assertIn("GUARD_EXC PermissionError", lines)     # exact type names (Arch ruling 2)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: 'GUARD_EXC PermissionError' not found in ['debug False', 'GUARD_EXC StrategyLayerDelistAccess', 'NOSRC_EXC TypeError', 'CFG_RAISED', 'DL_RAISED']

tests/test_sd1_suspend_delist.py:681: AssertionError
=========================== short test summary info ============================
FAILED tests/test_sd1_suspend_delist.py::T10PitGuard::test_strategy_caller_raises
FAILED tests/test_sd1_suspend_delist.py::T11OptimizeFlag::test_guards_under_python_O
2 failed, 42 passed, 1 skipped in 3.22s
```
