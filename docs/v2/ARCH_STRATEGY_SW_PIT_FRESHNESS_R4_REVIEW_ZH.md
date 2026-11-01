# Arch 审查：Strategy sw_pit 自查 r4（1b243992）

- 审查时间：2026-10-18T05:28:47-04:00
- 结论：**PASS**。可以签 code-change .ok（文件和 sha 见第五节）以及 selftest .ok（见第六节）。selftest 不能用 .venv_opt 跑，原因见 P3-1。r3（cd90f2f3）和 r3b（821dcfaa）作废，不审。
- 方式：只做静态审查。diff 打到 /tmp/arch_rev_s4 的基线副本上，跑 pyflakes；没有执行项目代码和测试。

## 一、核实项
| 项 | 结果 |
|---|---|
| r4.diff sha256 | 1b243992a09271462404e7e59dc529ca274909125339258cdf2650d7a572cbad，314 行，与声明一致 |
| 基线 | strategy_fulla_b4_x2.py 77af51e6125dbac662f94d05dae63e0be4bb682719d6ff2eb9f8809be5edb511，strategy_hiliq_capadv_b4_x2.py 4f952de2d2fdf9e30a605916aeb88bc3751afd738264a644640fe2e89ce03c1f，都对得上 |
| git apply --check / apply | 4 个文件干净打上 |
| 打补丁后的 sha | sw_pit_freshness.py 3116e4f6…、test_sw_pit_freshness.py a9b5c3e9…，与 Strategy 声明一致 |
| pyflakes | 无新增告警。基线已有的两条：fulla:164 nav_path、hx2:577 charts2。两个新文件都是 0 条 |
| f-prefix | AST 扫描未发现漏写 f（_finalize 中带占位符的段落都是 f 串） |
| as_of 类型 | load_leg 把 session 转成 str[:10]（YYYY-MM-DD），Wx 也是 str；_d() 用 str(x)[:10] 再 fromisoformat，Timestamp、date、str 都能处理。Python 3.12/3.13 也接受 YYYYMMDD |
| 腿文件 session | 3 条腿都是 large_string，2024-01-02…2026-10-09，所以 syn_as_of=2026-10-09 |

## 二、逐项核对 r4 的必做项
1. 缓存只保存 _integrity 的结果（完整性、built_et/built_sh、coverage、日历、in_date_range、sha），按 (str(root), level) 区分：**符合**。
2. coverage_gap 和 lag 每次调用都在 _evaluate 里重算，ref 按当前时刻重新取：**符合**。
3. 汇总：as_of 取最晚的一次（ISO 字符串比较），更早的不会回退；warns 合并后去重；有 n_calls 和 as_of_all：**符合**。
4. main 把 GROUPS 里各条腿的最大 session 传给 load_industry_map；fulla:253 和 hx2:312 传各自 Wx 的最大 session：**符合**。
5. X2[1] 只作兜底，同时设 as_of_defaulted=True 并加披露「as_of 取默认值（调用方未传）」，_finalize 不把这条算作 stale：**符合**。外部调用方 strategy_b4_hiliq_leg_review.py:142 和 strategy_capadv_topn_tie_sensitivity.py:32 都会带上这条披露。
6. 单测共 6 个，都用 pytest 的 tmp_path，不读真实数据，不联网：**符合**。
7. 带时区的 built：b.tzinfo 不为空时用 astimezone，不用 replace；test 6 用 +08:00 10:30，结果覆盖日为 10-13：**符合**。
- 统一口径：R1 lag 取 (coverage, ref]，≥3 判 stale，无差一错误；R2 naive 当美东，hour≥18 算覆盖当天，18:00 整点也算；R3 manifest 不可读、parquet 缺失、sha 不一致或未登记、built 缺失都 raise，日历里找不到开市日也 raise；R5 coverage_gap 比较 as_of 和 coverage_day。都已核实。
- 手算 6 个用例：NOW=美东 10-18 05:00，即上海周日 17:00，ref=10-16。test3 覆盖日 10-13；test4 lag=3 判 stale，对照组上海 19:00 覆盖 10-14、lag=2；test5 覆盖日 10-16、lag=0，as_of 10-19 报 gap，传入 10-12 不回退，n_calls=3。断言都成立。

## 三、发现（无 P0/P1/P2）
- P3-1 解释器：.venv_opt/bin/python（3.13.5）**没有装 pytest**，系统 python3 也没有。装了 pytest 的有 /workspace/ql-enrich-venv/bin/python（3.13.5，pandas 3.0.6，pyarrow 26.0.0，与 .venv_opt 版本完全相同，pytest 9.1.1），以及 /workspace/qlvenv/bin/python（3.12.14，pytest 9.1.1）。selftest .ok 建议 pin ql-enrich-venv。
- P3-2 日历期限：日历只到 20261231。2027 年以后 ref 会停在 12-31，lag 会少算（_completed_session 只在完全找不到开市日时才 raise）。建议在日历最大日期早于上海今天时 raise。和 Intel P2-2 一并在下一版统一，2026-12 之前必须修。
- P3-3 披露措辞：只有「as_of 取默认值」一条时，disclosure_zh 开头也写「申万 sw_pit 表可能过期」，容易误读。建议对这种情况换一个标题。
- P3-4 缺 in_date_range 不停跑（disclosure 里显示 in_date 最大 None）。Intel 那边硬停，团队要对齐。我倾向于和 Intel 一样硬停，下一版改。
- P3-5 built 无法解析时抛的是 ValueError，不是 SwPitIntegrityError。仍然会停跑，符合 R3，但建议包装成同一类异常。
- P3-6 检查和读取之间有窗口（sha 校验后另外 read_parquet），和 Intel P3-4 同类。
- P3-7 syn_as_of 对每条腿重新 load_leg 一次，取的是各腿最大值中的最大值；build_topn 实际用的是各腿 session 的交集。这样偏保守，现在两者都是 10-09，不阻塞。
- P3-8 测试缺口：没有覆盖 manifest 不可读、parquet 缺失、17:59/18:00 边界，以及「只有 as_of 默认值时不判 stale」这几种情况。ensure_checked 返回的是共享的可变汇总对象。
- P3-9 影响面：optimizer_core_x2_run.py:382 会 import hx2 的 run_smoke，hx2 的 sha 变了以后，凡是 pin 了 hx2 sha 的 .ok 都要更新。纸面轨的 import 闭包不 import fulla 或 hx2（Strategy 的说法已用 rg 核对）。
- 继承项（不属于本次 diff）：P2 行业静态映射的前视仍然没有修。hx2 load_industry_map 和 hx2:312 用的是「最后一次出现的行业」，fulla 的 lookup 用 in_date<=session，不符合 R4（in_date<d）。由单独的 PIT 修复 diff 处理。sw_members_asof 目前**没有落地**，只在 Intel r2 的 diff 里（_review/intel_sw_pit_freshness_20261018_r2.diff，intel_common.py 新增部分）。

## 四、对 r4 的签字条件
- code-change .ok 只覆盖第五节的 4 个文件和 4 个 after-sha；不许顺带改动其他文件。
- 落地后用 sha256sum 做三处核对：草案打补丁的结果、工作区、.ok pin。

## 五、code-change .ok 覆盖的文件（before → after，全 64 位）
- research/strategy_fulla_b4_x2.py：77af51e6125dbac662f94d05dae63e0be4bb682719d6ff2eb9f8809be5edb511 → 7bd657ed936d7adf382e0c30a8537aa3d628dc6eb3e2e65d27b8972abff52316
- research/strategy_hiliq_capadv_b4_x2.py：4f952de2d2fdf9e30a605916aeb88bc3751afd738264a644640fe2e89ce03c1f → 1c51531a12fd720788105d413264f8d00e6598caf075d96184ba30b5d3c69b45
- research/sw_pit_freshness.py（新增）：ABSENT → 3116e4f697c887dc2dce27c747fde38691afe0fe2b3c27e6b87c183aa34dbf31
- research/tests_sw_pit/test_sw_pit_freshness.py（新增）：ABSENT → a9b5c3e9825110d0e88e446d7dedd599b1acad023c5de7d3f4fead1be1041ec2

## 六、selftest
```
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/arch_sw_pit_r4_selftest research/tests_sw_pit/test_sw_pit_freshness.py
```
- 预期结果：6 passed，exit 0。
- 测试文件 sha256：a9b5c3e9825110d0e88e446d7dedd599b1acad023c5de7d3f4fead1be1041ec2；被测模块 sha256：3116e4f697c887dc2dce27c747fde38691afe0fe2b3c27e6b87c183aa34dbf31。
- 会 import：标准库 datetime、hashlib、json、sys、pathlib、zoneinfo，以及 pandas（to_parquet 用 pyarrow）、pytest、research.sw_pit_freshness。不 import fulla 和 hx2，也没有重模块。两个 venv 里都没有同名的 research 包。仓库里没有 conftest.py、pytest.ini 和 pyproject。
- 写入范围：只写 --basetemp 指定的 /tmp 目录。-p no:cacheprovider 避免生成 .pytest_cache，PYTHONDONTWRITEBYTECODE=1 避免在 research/ 下写 pyc。
