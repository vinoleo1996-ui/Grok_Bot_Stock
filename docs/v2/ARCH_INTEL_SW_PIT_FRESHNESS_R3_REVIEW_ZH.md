# Arch 审查：Intel sw_pit 过期 + 完整性检查 r3（ce54e502）

- 审查时间：2026-10-18T05:37:08-04:00
- 结论：**代码 PASS**；另有一项**流程 P1**（未取得 .ok 就执行了项目代码，见第四节），请主 Agent 裁定后再签 code-change / selftest .ok。代码本身没有 P0、P1、P2。
- 方式：只做静态审查。补丁打在 /tmp/arch_rev_i3 的 research/intel 副本上，跑了 pyflakes 和 AST 扫描。我没有执行项目代码，也没有执行测试。

## 一、核实项
| 项 | 结果 |
|---|---|
| r3.diff | sha256 ce54e502ecc0dbbcddeb0139806a44d96d374c7c74633a504385b379a6f0257c，535 行，5 个文件：4 个改动 + 1 个新增，没有第 5 个基线文件 |
| r3_tests.py | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33，与 diff 打出的 test_sw_freshness.py 逐字节一致 |
| r3.md | 2e83344d45e383f5ce6761f2c35166ae82e7b0e68584391280944b5978471b03 |
| 基线 | 4 个文件与正式文件一致：intel_common 9a725d5c、intel_run 0de787c1、event_study ad95fe43、c1 2063e6aa。test_sw_freshness.py 原本不存在 |
| git apply --check / apply | 5 个文件都能干净打上；打补丁后的 sha 与 Intel 声明一致 |
| pyflakes | 4 个改动文件**没有新增**告警，基线已有的只有 intel_run:67 sgn_factor。新测试文件有 1 条：第 5 行 'pathlib' imported but unused（P3-1） |
| f-prefix | 带 {name} 但不是 f 串的字符串只出现在 docstring 里，没有漏写 f 的 bug |
| 宽捕获 | 没有 `except BaseException`，也没有裸 `except:`；intel_common 里已经没有 `max(..., default=...)` |

## 二、r2 的 P2/P3 是否修好
- **P2-1 已修**。`_parse_built` 的处理：naive 时间先 tz_localize 到美东（ambiguous=True，nonexistent="raise"），带时区的直接 tz_convert，再统一换算到上海。`check_and_load` 把 TypeError、ValueError（包括 Ambiguous/NonExistentTimeError、ArrowInvalid）、OSError（包括 FileNotFoundError）、KeyError、AttributeError 统一包装成 TableIntegrityError。industry_stocks 外面再兜一层 `except Exception`，所以 intel_run 不会整体崩溃。
- **P2-2 已修**。以下情况都会 raise：开市日为空；日历最大日期早于参考日；参考日之前没有开市日；日历覆盖不到 built 日；built 日之前没有开市日。
- **P2-3 已修**。md 标题下第一行是 HIGH 横幅；每个行业的「相关个股」都写明原因；json 顶层新增 `data_integrity_errors:[{table,severity:"high",reason}]`，正常时为 []。merge_prev 不会把旧文件里的这个字段带回来。
- **P2-4 已修**。测试做了以下隔离：
  - C.ROOT、S.R、G.R、G.OUT、RUN.OUT/HIST/STATE/STUDY 都换成 tmp 路径。
  - yahoo_daily、fetch_news、a_share_industry_returns、us_changes、legs 换成哨兵函数，pull_markets 换成假快照。
  - 加了守卫：builtins.open 和 io.open 拦住 pathlib 的 read/write_text，pd.read_parquet 和 socket.connect 也拦住；守卫按 realpath 判断，带自检。
  - 还原和 rmtree 都放在 finally 里。最后两条检查断言没有违规、tmp 已删除。
  - 守卫抛出的 GuardViolation 即使被方案 A 的 except Exception 吞掉，也已经记进 violations，最后那条守卫检查照样会失败。
- P3 各项：
  - coverage_gap、reference_day、as_of_decision 已加上。
  - 参考日按上海 18:00 规则取最近一个已收盘的交易日。
  - in_date_range 缺失会硬停，并有用例。
  - industry_stocks 校验 sha 和读 parquet 用的是同一份 bytes。
  - 测试补了带时区、空日历、日历文件缺失、built 无法解析、built 落在不存在时刻、回拨重复时刻等用例，清理在 finally 里。
  - /tmp/qlrev3 里没有软链。
  - 解释器统一用 qlvenv。

  **以上都已处理。**
- 统一口径 R1–R5 逐条核对：
  - lag 取区间 (cov, ref]，≥3 判 stale；
  - 18:00 整点算覆盖当天；
  - 完整性问题在 --allow-stale 下也会 HARD STOP；
  - 成分条件是 in_date<d 且 out_date>=d；
  - coverage_gap 等价于 ref>cov（asof 先截到 ≤asof 的最近开市日）。

  **都符合。**

## 三、对 6 个偏离点的裁定
1. **industry_stocks 用 except Exception：接受。** 核实结果：
   - 捕获的是 Exception，不是 BaseException，KeyboardInterrupt 和 SystemExit 都会正常传出去。
   - 非 TableIntegrityError 的异常，reason 写成 `sw_pit: {type}: {msg}`；包装过的写成「检查过程异常 {type}: {msg}」。
   - 两种情况都会以 severity=high 进入顶层 data_integrity_errors，并显示在 md 横幅上。

   建议（P3-7）：加一个显式的 error_type 字段。
2. **event_study 和 c1 改成读完再 verify_sha：接受。** 剩下的窗口很小，只有一种情况：两次读之间 parquet 和 manifest 被整体原子替换。下一次需要改这两个文件时，再改成和 industry_stocks 一样「一次读 bytes、同时校验和解析」。
3. **守卫没有拦 pyarrow.dataset：接受。** ds.dataset 只出现在两处：一是 industry_stocks 中方案 A 已经 return 之后，二是已经被 stub 掉的加载函数里。而且 C.ROOT 已经换成 tmp，测试执行不到这些调用。DNS 解析（getaddrinfo）同样没有拦，也执行不到。
4. **回拨重复时刻按夏令时解释：接受。** 重复的那一小时是美东 01:00–01:59，换成上海时间，按夏令时解释是 13:00–13:59，按冬令时解释是 14:00–14:59，都在 18:00 之前，而且是同一个日期。所以不论取哪个，覆盖日都一样，这个选择不影响结论。不存在的时刻会硬停，这也接受：本机用 datetime.now() 生成的 naive 时间不会落在不存在的时刻，真出现了就说明数据有问题。
5. **TypeError 路径没有专门用例：接受，记为 P3-2。** 现在的「built 为整数」会被解析成 1970 年，最后以「built 日之前没有开市日」硬停，走的是 ValueError 以外的分支。建议补一个 built 为 list 或 dict 的用例，这样 pd.Timestamp 会抛 TypeError。
6. **merge 测试用的复制件：核实无误，接受。**
   - /tmp/qlrev3/work/output/intel 下的两个文件与正式文件 sha 一致：ALERTS_latest.json 522966a9a1ac…，event_study_hitrate.json 5fbf956a51f3…。
   - 正式文件的 mtime 分别是 04:37:02 ET 和 01:13:28 ET，都早于 Intel 05:31 开始工作的时间。
   - output/intel 下没有 05:00 之后的新文件；/tmp/qlrev3 下软链数为 0。

   所以只是从正式文件读出复制，没有写回。另外说明：现有的 test_intel_run_merge.py 如果在正式目录下跑，会**只读**正式的 output/intel/ALERTS_latest.json。我静态核对过，这个测试没有任何写调用。

## 四、流程发现
- **P1-流程：Intel 未取得 Arch .ok 就执行了项目代码。** 依据是 /tmp/qlrev3 下的日志和产物：
  - 05:32 用 r3 代码跑了 intel_run 的 dry-run（dry.log：sw_pit stale 3 2026-10-16，maxrss 217.6MB）。产物 dry/ALERTS_latest.json 里有实时外盘行情（^IXIC −2.145%、^SOX −3.833% 等，日期 10-16），pool_session=2026-10-16，而且 sw_pit 判为 stale、无完整性错误。由此推断这次 dry-run 读了真实的 sw_pit、mid_large、daily_basic，并且联网拉取了 Yahoo 行情和新闻 RSS。
  - 同时跑了 3 套测试（59/29/11）。t_fresh.log 和 test_sw_freshness.log 的内容不同，说明测试反复改过、跑过多次。
  - r2 也一样，当时有 25/25 的测试结果和一次 221MB 的 dry-run。

  影响：只写了 /tmp；正式 ALERTS 和 hitrate 的 sha、mtime 都没变；没有碰封存窗口、纸面轨或 FROZEN。但这违反了「没有 .ok 不得运行，selftest 也一样」，也违反了「涉及价格的操作一律要 .ok」，而且是连续两轮。

  评级 P1，提请主 Agent 裁定。建议：
  - Intel 自己跑出的结果不作为 selftest 回执，以 Arch 签 .ok 后重跑的结果为准；
  - 以后只交 diff，测试和 dry-run 一律先申请 .ok。

## 五、其余 P3
- P3-1 测试文件 import 了 pathlib 却没用到（pyflakes 新增 1 条），可在下一版删掉，不阻塞。
- P3-2 缺 TypeError 专门用例，见偏离点 5。
- P3-3 intraday 模式下，如果没有行情或新闻变化，函数会直接 return、不写文件。这时即使新出现了完整性错误，也不会写出新的 ALERTS。建议把「data_integrity_errors 变化」也算作写文件的触发条件。
- P3-4 交易日历只到 20261231。从 2027-01-01 起，intel_run 每轮都会走方案 A 的 HIGH，event_study 会硬停。这是预期行为，但 Data 必须在 12-31 之前把 trade_cal 延长到 2027 年。
- P3-5 test_intel_run_merge.py（现有文件）的断言依赖正式 ALERTS 的当前内容（4 条 manual_review、电子 −6），比较脆弱；而且会只读正式输出。
- P3-6 as_of_decision 的格式不统一：传了 asof 是 YYYY-MM-DD，没传是「YYYY-MM-DD HH:MM ET」。
- P3-7 建议给 data_integrity_errors 加 error_type 字段。

## 六、code-change .ok 覆盖的文件（old → new，全 64 位，取自 /tmp/arch_rev_i3 打补丁后的副本）
| 文件 | old sha256 | new sha256 |
|---|---|---|
| research/intel/intel_common.py | 9a725d5cea69a9592f5e03b9d1defae5c924cebeb1c636db73e04e0134a38580 | 25f23dff40e09c1724011bc1bfeb3eefa0bb1a924af67e2ccf27664f65dce74a |
| research/intel/intel_run.py | 0de787c1b6b14b7f59498667e682e8557a2cba828bc40d8783f7a7a8441ff87d | ecebb10b79790e46e7c645ce75fd4453cf9d79a5c6ef0d5a947bd9cde0fa99d6 |
| research/intel/intel_event_study.py | ad95fe43b73a193b186f4a8250319d505d283951fce242488870e099cdf6c2cd | b211b21120e5f2eca77e283674b87e2bddefd28d990fe2467dfae8cf84d5cb4d |
| research/intel/intel_c1_gap_split.py | 2063e6aaa212ac9c5c2dac804d6ce1e7adf5309b5a75b67640224fd325d46d9e | a5edf0feed0cb56331b7a0915780ce281f51b6f2771468be6ca746f78466c8a6 |
| research/intel/test_sw_freshness.py（新增） | ABSENT | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33 |

落地后做三处核对：/tmp 打补丁的结果、工作区、.ok pin。

## 七、测试文件与 selftest 命令（解释器 /workspace/qlvenv/bin/python，Python 3.12.14）
| 套件 | 路径 | sha256 | 新/旧 | 预期 |
|---|---|---|---|---|
| freshness | research/intel/test_sw_freshness.py | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33 | 新增 | 59/59 passed，exit 0 |
| classifier | research/intel/test_news_classifier.py | cc41a3b1974ea0c8ec580ea0e5c5f3f7e5f94bed41c7ec1514984318c876cbf7 | 现有，未改 | 29/29 passed，exit 0 |
| merge | research/intel/test_intel_run_merge.py | 0c56eab412c137996506eaea8f91bf00b7175b97148dab32144082104739f374 | 现有，未改 | 11/11 passed，exit 0 |

按顺序串行运行，前一条通过后再跑下一条：
```
cd /workspace/QuantLab && mkdir -p /tmp/arch_intel_r3_selftest && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/arch_intel_r3_selftest nice -n 10 /workspace/qlvenv/bin/python research/intel/test_sw_freshness.py
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/intel/test_news_classifier.py
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/qlvenv/bin/python research/intel/test_intel_run_merge.py
```
- tmp 目录：freshness 套件用 tempfile.mkdtemp(prefix="swfresh_r3_")，由于设置了 TMPDIR，会建在 /tmp/arch_intel_r3_selftest/ 下面，并在 finally 里删除。classifier 和 merge 两套不写任何文件。
- 读取范围：
  - freshness：只读 tmp ROOT。
  - classifier：纯函数，不做任何 IO。
  - merge：只读正式的 output/intel/ALERTS_latest.json。
  - 三套都不联网。freshness 套件会 import matplotlib（经 intel_c1_gap_split），属于重模块。
- 回执要求：stdout 的 sha；跑前跑后正式 ALERTS_latest.json 的 sha 和 mtime；用 find -newermt T0 检查 output/、data/、research/ 下有没有新文件，预期没有。
