# SD1 selftest 回执（Eng，2026-10-18 02:3x ET）

**结论：唯一的一次运行结果是 4 failed / 31 passed / 1 skipped，退出码 rc=1，未通过。** 按指令没有重试，也没有改任何钉住的文件。下面原样记录，失败原因的静态初判见 §5。live=false，promotion=false；没有跑对拍。

## 1. 授权与预检（运行前，02:20–02:26 ET）
- docs/v2/eng_sd1/ARCH_SD1_TEST.ok = 4975aac8ccb34b90e3ac05a3edddd38629ef523ef6d1e1156a12519a2cdabfdc：实测一致。scope=selftest；allow_selftest=true，allow_real_data 与其余 allow_* 均为 false；out_dir=mkdtemp；expires_et=2026-10-19T02:00:00-04:00。
- docs/v2/eng_sd1/ARCH_SD1_EXEC.ok = eb3c35870e60fd418fcaa977aa695be2c211158185061d64f91ce7d76fa625e5：实测一致，本次未使用。
- 复审文件 docs/v2/ARCH_SD1_R2_REVIEW_ZH.md = 73cb88ac53b96ed7c5905a216d26fe0ecd093e75141bb6f8b16e925f557c3561。
- tests/test_sd1_suspend_delist.py = 8305246bee90fb5fd4da623953b30fa57d6e6559eee7b00b6bb5a0dcf504fa08：与 .ok 的 runner_sha256 一致。
- TEST_DEPS 自检：静态读取测试文件里的 TEST_DEPS 字面量（不 import），共 68 项。每个文件的实测 sha 都同时等于 .ok 里的 dep_sha256_<key> 和 SD1_SHAS.txt（621a7af4b8a6500f81bb0db505836afdab8d9151f0bc6672766d064f2d9d0683）TEST 段的值：68/68 一致，不一致 0。.ok 里也没有多出来的 dep 键（.ok 68 项，SHAS 68 项）。运行时 ok_runner_pin c7805d9a 又独立核了一遍并放行（门禁没有拒绝，测试得以收集）。
- 进程检查（ps，02:2x ET）：没有 fix_sd1、cs_panel 或 D-1~D-4 重建进程，没有研究类 python，也没有其他 pytest 或对拍进程。在跑的有：Web 的 server.py（pid 80415，含一个已知僵尸子进程）、Data 的抓数 remaining_after_stk_surv.py 和 relay_outage_backfill.py、nightly_update --date 20261015 --steps tier3（tier3_daily_snapshot）。Arch 02:01 已认定这些抓数不写重建输入；本测试全部用合成数据，不读它们的产物。MemAvailable 约 11.1GB。
- 另注：scripts/fix_sd1/*.py 的 mtime 是 02:26:20 ET，比本次启动早 4 秒，是 Data 在编辑文件，不是在运行重建（ps 里没有这类进程）。本测试的 dep 不含这些文件。
- QL_SD1_REAL_DATA：本 shell 中未设置，命令里也用 env -u 显式去掉。
- 运行前 `ls -d /tmp/sd1_selftest_*` 的输出：`ls: cannot access '/tmp/sd1_selftest_*': No such file or directory`
- 基线：/workspace/QuantLab 下有 170 个 __pycache__/.pytest_cache 目录（包括 .venv_opt 内的）、1296 个文件，带 mtime 的清单存在 /tmp/sd1_st_run/cache_dirs_before.txt 和 cache_files_before.txt。仓库根目录的 .pytest_cache 是 2026-10-18 01:17:48 ET 已有的，不是 Eng 写的。

## 2. 命令与解释器
- 命令（逐字）：`cd /workspace/QuantLab && env -u QL_SD1_REAL_DATA PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python -m pytest tests/test_sd1_suspend_delist.py -q -p no:cacheprovider`
- 外层包装 /tmp/sd1_st_run/wrap.py：用系统 python3 -B 运行，只用 subprocess、resource、time，不 import quantlab。它按上面同样的 argv 启动一次，等进程结束后读 getrusage(RUSAGE_CHILDREN)。
- 解释器：/workspace/qlvenv/bin/python，Python 3.12.14；pytest 9.1.1。
- 开始 2026-10-18T02:26:24-04:00，结束 02:26:27-04:00，耗时 3.4s，rc=1。只运行了这一次。

## 3. 结果
- **31 passed，4 failed，1 skipped**（skip 的是 T13 真实数据用例，符合预期），耗时 3.13s。
- 失败的 4 项：
  1. T1HaltResumeGap::test_main_engine：复牌日 d[6] 没有卖出成交（`AssertionError: [] is not true`，第 261 行）。
  2. T3BlockedBuyBudget::test_renorm_vs_cash：在 cash 模式下，算出的现金是 399999.9761581421，期望 400000，差 0.0238，超过 delta=1e-3（第 321 行）。
  3. T10PitGuard::test_strategy_caller_raises：`TypeError: load_delist_events() missing 1 required keyword-only argument: 'source'`，没有走到 PermissionError。
  4. T11OptimizeFlag::test_guards_under_python_O：子进程只打印了 'debug False'，GUARD_RAISED、CFG_RAISED、DL_RAISED 都没有打印。
- 完整 pytest 输出见附录 A。

## 4. 资源与清理
- 峰值 RSS，用了两种方法：
  - 外部 bash 采样器（/tmp/sd1_st_run/sampler.sh）每秒读一次 /proc/<pid>/status，记录根进程及其两层子进程的 VmRSS 和 VmHWM。根进程 VmHWM 最大 161560 kB（约 158MB）。最后一次采样（02:26:27）VmHWM 是 161232 kB；这一次采样时进程已经在退出，所以略低于峰值。全进程树 VmRSS 合计最大 253024 kB（约 247MB，02:26:26 那次采样，树里有 2 个进程）。
  - getrusage(RUSAGE_CHILDREN).ru_maxrss = 163088 kB（约 159MB）。
  - 两种方法都远低于 1536MB 的上限。
  - 局限：采样间隔 1s，整个运行只有 3.4s，T10/T11 子进程的瞬时峰值可能没采到。ru_maxrss 给的是单个子进程的最大值，不是全树合计。
- 运行后 `ls -d /tmp/sd1_selftest_*`：`ls: cannot access '/tmp/sd1_selftest_*': No such file or directory`。mkdtemp 建的目录已由 atexit 删除。
- __pycache__ 和 .pytest_cache：运行后按同样方式重新列出，仍是 170 个目录、1296 个文件。前后两份清单（路径、mtime、大小）`diff` 结果为空（rc=0），说明没有新增或变动的 pyc，也没有新的 .pytest_cache。
- 预植文件 research/_sd1_planted_strategy.py、quantlab/strategy/_planted.py、scripts/_optimizer_planted.py 都不存在。测试只是把这些路径作为 compile 的文件名，没有落盘。
- 本次没有写 output/，也没有在仓库里写任何文件（除本回执外）。旧的 cpython-313 pyc 按指令保留未清理。

## 5. T10 静态扫描输出
- 在 -q 模式下，T10 的 test_static_check_catches_planted 通过了。它做了两件事：在 OUT_DIR 下扫描预植文件，正好得到 2 个 VIOLATION；再用子进程运行 scripts_eng/sd1_pit_static_check.py（不带 --json，因此不写文件），rc=0。这个子进程的 stdout 被测试捕获，只在失败时打印，所以这次运行没有可展示的文本。我没有为展示它额外运行任何东西。
- 参考值：r2 交付时（02:0x ET）单独跑过的结果是 rc=0、21 条历史引用、0 违规，见 docs/v2/eng_sd1/pit_static_check.json a3aaefbf…。
- T10 的另一项 test_strategy_caller_raises 失败了，见 §3 第 3 条。

## 6. 失败原因的静态初判（只读代码，没有再运行）
- T10 和 T11 是同一个原因：r2 把 load_delist_events 改成必须显式传 `source`（P2-4），但测试里的 PLANTED 片段仍然是 `load_delist_events()`。参数绑定先于函数体里的 guard_accounting_caller() 执行，所以先抛出 TypeError，没有到 PermissionError。T11 的子进程因此在第一个 exec 就退出了，后面两项检查（CFG、DL）都没有执行。r3 修法：PLANTED 改为 `load_delist_events(source="src_events_v1")`。也可以考虑把调用方检查放到更早的位置，这一点请 Arch 定。
- T3 是测试精度问题：actual_weights 按设计是 float32（execution_sd1 第 755、874 行）。nav 约 1e6 时，float32 的权重误差大约是 1e-7 × nav ≈ 0.02，超过了 delta=1e-3。r3 修法：容差改为相对容差（例如 rtol 1e-6），或者直接用引擎记录的现金来核对。
- T1 需要 r3 排查：在停牌日 d[3] 下调目标权重到 0.5，复牌日 d[6] 应该有卖单，实际没有。目前还不能确定是 CFG0（legacy）还是 CFG1（SD1）不满足，因为两个配置在同一个循环里断言。从静态代码看，下单量是按 Cm[t] 估算的（第 1248 行），Cm 在停牌日为 NaN 时会直接 continue，不产生订单。SD1 依赖 sig_state 在复牌时重新生成订单。r3 先把两个配置拆成两个断言来定位；如果 legacy 本来就不这样做，测试期望应只对 CFG1 成立。这个失败影响 SD1 的核心语义，在 SD0 对拍之前必须先定性。
- 以上 4 项都不涉及 execution.py、__init__.py 或纸面路径。修复需要动测试文件和/或 execution_sd1.py，属于 r3；sha 会变，Arch 需要重新签 TEST.ok。

## 附录 A：pytest 原始输出（含外层包装的 START/END 行）
```
START 2026-10-18T02:26:24-0400
F......F..........FF....s...........                                     [100%]
=================================== FAILURES ===================================
_______________________ T1HaltResumeGap.test_main_engine _______________________

self = <test_sd1_suspend_delist.T1HaltResumeGap testMethod=test_main_engine>

    def test_main_engine(self):
        sched = {self.d[0]: {X: 1.0}, self.d[3]: {X: 0.5}}
        for cfg in (CFG0, CFG1):
            r = _run(self.p, sched, cfg)
            nav = r["nav"].to_numpy()
            self.assertEqual(nav[3], nav[2]); self.assertEqual(nav[4], nav[2]); self.assertEqual(nav[5], nav[2])
            self.assertAlmostEqual(nav[6] - nav[5], 1e5 * (8 - 10), places=6)
            halt_days = {str(x.date()) for x in self.d[3:6]}
            self.assertFalse([f for f in r["fills"] if f["date"] in halt_days])
>           self.assertTrue([f for f in r["fills"] if f["date"] == str(self.d[6].date()) and f["side"] < 0])
E           AssertionError: [] is not true

tests/test_sd1_suspend_delist.py:261: AssertionError
____________________ T3BlockedBuyBudget.test_renorm_vs_cash ____________________

self = <test_sd1_suspend_delist.T3BlockedBuyBudget testMethod=test_renorm_vs_cash>

    def test_renorm_vs_cash(self):
        for mode, want_y, want_cash in (("renorm", 50000, 0.0), ("cash", 30000, 4e5)):
            r = self.run_mode(mode)
            aw = r["actual_weights"].iloc[3]; nav = r["nav"].iloc[3]
            self.assertEqual(round(float(aw[Y] * nav / 10)), want_y)
            self.assertEqual(round(float(aw[X] * nav / 10)), 0)
>           self.assertAlmostEqual(float(nav * (1 - aw.sum())), want_cash, delta=1e-3)
E           AssertionError: 399999.9761581421 != 400000.0 within 0.001 delta (0.02384185791015625 difference)

tests/test_sd1_suspend_delist.py:321: AssertionError
___________________ T10PitGuard.test_strategy_caller_raises ____________________

self = <test_sd1_suspend_delist.T10PitGuard testMethod=test_strategy_caller_raises>

    def test_strategy_caller_raises(self):
        for fake in ("research/_sd1_planted_strategy.py", "quantlab/strategy/_planted.py", "scripts/_optimizer_planted.py"):
            with self.assertRaises(PermissionError):
>               exec(compile(PLANTED, str(ROOT / fake), "exec"), {})

tests/test_sd1_suspend_delist.py:509: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

>   ???
E   TypeError: load_delist_events() missing 1 required keyword-only argument: 'source'

/workspace/QuantLab/research/_sd1_planted_strategy.py:2: TypeError
__________________ T11OptimizeFlag.test_guards_under_python_O __________________

self = <test_sd1_suspend_delist.T11OptimizeFlag testMethod=test_guards_under_python_O>

    def test_guards_under_python_O(self):
        code = "\n".join([
            "import sys", f"sys.path.insert(0, {str(ROOT)!r})",
            "print('debug', __debug__)",
            "try:",
            f"    exec(compile({PLANTED!r}, {str(ROOT / 'research/_sd1_planted_strategy.py')!r}, 'exec'), {{}})",
            "    print('GUARD_NO_RAISE')",
            "except PermissionError:",
            "    print('GUARD_RAISED')",
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
        for k in ("GUARD_RAISED", "CFG_RAISED", "DL_RAISED"):
>           self.assertIn(k, out)
E           AssertionError: 'GUARD_RAISED' not found in 'debug False\n'

tests/test_sd1_suspend_delist.py:553: AssertionError
=========================== short test summary info ============================
FAILED tests/test_sd1_suspend_delist.py::T1HaltResumeGap::test_main_engine - ...
FAILED tests/test_sd1_suspend_delist.py::T3BlockedBuyBudget::test_renorm_vs_cash
FAILED tests/test_sd1_suspend_delist.py::T10PitGuard::test_strategy_caller_raises
FAILED tests/test_sd1_suspend_delist.py::T11OptimizeFlag::test_guards_under_python_O
4 failed, 31 passed, 1 skipped in 3.13s
END 2026-10-18T02:26:27-0400 rc=1 elapsed_s=3.4 ru_children_maxrss_kb=163088
```

## 附录 B：RSS 采样
```
ts root_vmrss_kb root_vmhwm_kb tree_vmrss_kb max_proc_vmhwm_kb nproc
02:26:24 21204 21540 21204 21540 1
02:26:25 160748 160748 160748 160748 1
02:26:26 161560 161560 253024 161560 2
02:26:27 161136 161232 161136 161232 1
```
