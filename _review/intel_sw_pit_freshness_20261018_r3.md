# Intel：sw_pit 过期 + 完整性检查 r3（只出 diff，待 Arch 审）
- 时间：2026-10-18 05:32 ET。对应 docs/v2/ARCH_INTEL_SW_PIT_FRESHNESS_R2_REVIEW_ZH.md（sha 6462c137…，已通读）。正式 research/intel 文件**未改**（与基线逐字节 cmp 一致）；正式 ALERTS_latest.json 前后 sha 一致。live=false。
- 已采纳的裁定：方案 A（完整性错误只停行业→个股映射，其余照常）；in_date_range 缺失时硬停。
- 产出：r3.diff（相对正式文件，5 个文件，含新测试；git apply --check 通过）、r3_tests.py（与 diff 中 test_sw_freshness.py 逐字节一致）、本说明；各配 .sha256。
- 临时目录：/tmp/qlrev3，用真实复制，**没有任何软链**（find -type l 为 0）。merge 测试需要的 ALERTS_latest.json 和 event_study_hitrate.json 是复制进去的。
- 解释器：/workspace/qlvenv/bin/python（3.12），PYTHONDONTWRITEBYTECODE=1。跑之前 ps 确认没有其他重任务（94322 处于 T 状态，138MB）。

## 打补丁后的文件 sha（供 .ok pin）
| 文件 | sha256 |
|---|---|
| research/intel/intel_common.py | 25f23dff40e09c1724011bc1bfeb3eefa0bb1a924af67e2ccf27664f65dce74a |
| research/intel/intel_run.py | ecebb10b79790e46e7c645ce75fd4453cf9d79a5c6ef0d5a947bd9cde0fa99d6 |
| research/intel/intel_event_study.py | b211b21120e5f2eca77e283674b87e2bddefd28d990fe2467dfae8cf84d5cb4d |
| research/intel/intel_c1_gap_split.py | a5edf0feed0cb56331b7a0915780ce281f51b6f2771468be6ca746f78466c8a6 |
| research/intel/test_sw_freshness.py | 608219fe65a0699d2629d7a5de7eadf24e2a925205c7c0937e266ab5ebedad33 |

## 逐条对应
- **P2-1 带时区的 built、异常绕过方案 A**：新增 `_parse_built`：无时区时用 `tz_localize(America/New_York, ambiguous=True, nonexistent="raise")`，带时区时用 `tz_convert`，最后都换算到上海。`check_and_load` 把 TypeError、ValueError（包括 AmbiguousTimeError / NonExistentTimeError）、OSError（包括 FileNotFoundError）、KeyError、AttributeError 统一包装成 TableIntegrityError。`industry_stocks` 里再兜一层 `except Exception`，任何异常都按方案 A 处理（空池、source_status 记 error/high），intel_run 不会整体崩掉。
- **P2-2 日历为空或覆盖不到**：去掉所有 `max(..., default=...)`。以下情况一律 raise TableIntegrityError：开市日为空；日历最大日期早于参考日（日历只到 20261231，2027 年以后会硬停）；参考日之前没有开市日；日历覆盖不到 built 日；built 日之前没有开市日、算不出覆盖日。
- **P2-3 完整性错误要醒目**：
  - md 标题下第一行加横幅「> ⚠ HIGH：sw_pit 完整性错误，本轮未输出相关个股（原因）」；
  - 每个行业的「相关个股」行写「（sw_pit 完整性错误，已停：原因）」；
  - json 新增顶层字段 `data_integrity_errors: [{table, severity: high, reason}]`，正常时为 []。merge_prev 不会把旧文件的这个字段带回来。
- **P2-4 测试完全隔离**：
  - 临时目录里搭建 ROOT，用真实文件，不用软链。
  - C.ROOT、S.R、G.R、G.OUT，以及 intel_run 的 OUT/HIST/STATE/STUDY 全部 monkeypatch 到临时目录。
  - C.yahoo_daily、C.fetch_news、S.a_share_industry_returns、S.us_changes、G.legs 替换成抛哨兵异常的函数；intel_run 的 pull_markets 换成假快照。
  - 守卫：builtins.open、io.open、pd.read_parquet 一旦读写真实 /workspace/QuantLab/data 或 /workspace/QuantLab/output 就报错；socket.connect 一旦联网就报错。另有守卫自检用例。
  - 所有还原和 rmtree 都在 finally 里，最后断言没有违规、临时目录已删除。
- **P3-1 coverage_gap**：返回值新增 `coverage_gap`（lag ≥ 1）、`as_of_decision`（传了 asof 就是该日期，否则为当前美东时刻）和 `reference_day`。
- **P3-2 参考日**：`_reference_day` 取上海时间最近一个已收盘的交易日（当天上海 18:00 以后才算当天已收盘）。传入 asof 时视为该日已收盘。
- **P3-3 in_date_range 缺失硬停**：保留，并补了用例。
- **P3-4 检查和读取之间的窗口**：`check_and_load` 返回校验过的同一份 bytes，industry_stocks 直接用这份 bytes 读 parquet。event_study 和 c1 读完 parquet 后调用 `verify_sha` 再复核一次（见偏离点）。
- **P3-5 测试覆盖**：新增 built 带时区（+08:00、UTC 两例）、日历为空、in_date_range 缺失、参考日超出日历、built 无法解析、built 落在夏令时不存在的时刻、日历文件缺失、夏令时回拨的重复时刻，以及 intel_run 在两类完整性错误下按方案 A 运行。清理放在 finally 里。
- **P3-6 卫生**：/tmp/qlrev3 不含软链。旧的 /tmp/qlrev 不再使用。
- **P3-7 解释器**：全部测试都用 /workspace/qlvenv/bin/python 跑。selftest 命令沿用 Arch 给的那条。

## 偏离点
1. industry_stocks 的兜底是 `except Exception`，比要求列出的异常类型更宽，目的是确保 intel_run 不会因任何原因整体崩掉。check_and_load 本身只包装上面列出的几类异常，另外加了 KeyError 和 AttributeError（manifest 结构异常时会出现）。
2. P3-4 的"同一份 bytes"只在 intel_run（industry_stocks）路径上实现。event_study 和 c1 改为读完再用 verify_sha 复核，没有改它们的读取方式，以保持改动最小。
3. 守卫只拦截 builtins.open、io.open、pd.read_parquet 和 socket.connect。pyarrow.dataset 直接读路径的调用没有拦截，但这些调用只出现在已经被 stub 掉的数据加载函数里，不会被执行到。
4. 夏令时回拨的重复时刻取 ambiguous=True（按夏令时解释，即较早的那一个小时，判定偏保守）。这是我选的，请 Arch 确认。
5. 方案 A 的用例里，"built 为整数"会被 pandas 解析成 1970 年的时间戳，最终以"日历覆盖不到 built 日"硬停，没有走 TypeError 这条路径。TypeError 包装由 check_and_load 的代码覆盖，目前没有专门触发它的用例。

## 测试结果（/workspace/qlvenv/bin/python，临时副本 /tmp/qlrev3）
```
test_news_classifier: 29/29 passed
test_intel_run_merge: 11/11 passed
test_sw_freshness（只列 PASS/FAIL 行）:
PASS 守卫自检：读真实 data 会被拦截
PASS 返回字段齐全（含 coverage_gap / as_of_decision / reference_day）
PASS 基准：美东 04:00 = 上海 16:00 → 覆盖 10-13，参考日 10-16，落后 3 → stale，coverage_gap
PASS 日线缺 10-15 时落后天数仍为 3（交易日取自 trade_cal）
PASS asof 10-15 → 落后 2 → ok
PASS 美东 05:59（上海 17:59）→ 覆盖 10-13、落后 3
PASS 美东 06:00（上海 18:00）→ 覆盖 10-14、落后 2、ok
PASS 美东 10-13 20:00 = 上海 10-14 08:00 → 覆盖 10-13
PASS built 带时区 +08:00 18:30 → 用 tz_convert、不抛 TypeError，覆盖 10-14
PASS built 带时区 UTC 09:59（上海 17:59）→ 覆盖 10-13
PASS sha 不一致：check 抛完整性错误
PASS sha 不一致：require_fresh(allow_stale=False) 硬停
PASS sha 不一致：require_fresh(allow_stale=True) 硬停
PASS manifest 缺失：check 抛完整性错误
PASS manifest 缺失：require_fresh(allow_stale=False) 硬停
PASS manifest 缺失：require_fresh(allow_stale=True) 硬停
PASS parquet 缺失：check 抛完整性错误
PASS parquet 缺失：require_fresh(allow_stale=False) 硬停
PASS parquet 缺失：require_fresh(allow_stale=True) 硬停
PASS in_date_range 缺失（P3）：check 抛完整性错误
PASS in_date_range 缺失（P3）：require_fresh(allow_stale=False) 硬停
PASS in_date_range 缺失（P3）：require_fresh(allow_stale=True) 硬停
PASS 日历为空（无开市日，P3）：check 抛完整性错误
PASS 日历为空（无开市日，P3）：require_fresh(allow_stale=False) 硬停
PASS 日历为空（无开市日，P3）：require_fresh(allow_stale=True) 硬停
PASS 参考日超出日历范围（P2-2）：check 抛完整性错误
PASS 参考日超出日历范围（P2-2）：require_fresh(allow_stale=False) 硬停
PASS 参考日超出日历范围（P2-2）：require_fresh(allow_stale=True) 硬停
PASS built 无法解析（ValueError → 完整性错误）：check 抛完整性错误
PASS built 无法解析（ValueError → 完整性错误）：require_fresh(allow_stale=False) 硬停
PASS built 无法解析（ValueError → 完整性错误）：require_fresh(allow_stale=True) 硬停
PASS built 落在美东不存在时刻（夏令时跳变）：check 抛完整性错误
PASS built 落在美东不存在时刻（夏令时跳变）：require_fresh(allow_stale=False) 硬停
PASS built 落在美东不存在时刻（夏令时跳变）：require_fresh(allow_stale=True) 硬停
PASS 日历文件缺失（FileNotFoundError → 完整性错误）：check 抛完整性错误
PASS 日历文件缺失（FileNotFoundError → 完整性错误）：require_fresh(allow_stale=False) 硬停
PASS 日历文件缺失（FileNotFoundError → 完整性错误）：require_fresh(allow_stale=True) 硬停
PASS 美东回拨重复时刻 01:30 不抛错（ambiguous=True 取夏令时）
PASS stale 默认停跑（非硬停）
PASS --allow-stale 放行 stale 并带 disclosure
PASS verify_sha：一致时通过
PASS intel_event_study.py 无参数 → STOP
PASS intel_event_study.py ['--allow-stale'] → HARD STOP
PASS intel_c1_gap_split.py 无参数 → STOP
PASS intel_c1_gap_split.py ['--allow-stale'] → HARD STOP
PASS intel_run 方案 A（sha 不一致）：不崩
PASS intel_run（sha 不一致）：json 顶层 data_integrity_errors 非空且 high
PASS intel_run（sha 不一致）：行业预警照常输出
PASS intel_run（sha 不一致）：md 标题下第一行是 HIGH 横幅
PASS intel_run（sha 不一致）：每条相关个股写明原因
PASS intel_run 方案 A（built 为整数（非法类型））：不崩
PASS intel_run（built 为整数（非法类型））：json 顶层 data_integrity_errors 非空且 high
PASS intel_run（built 为整数（非法类型））：行业预警照常输出
PASS intel_run（built 为整数（非法类型））：md 标题下第一行是 HIGH 横幅
PASS intel_run（built 为整数（非法类型））：每条相关个股写明原因
PASS as-of：变动当天不可用、出表当天仍是成员
PASS as-of：次日生效
PASS 守卫：没有读写真实 data/output、没有联网、没有越过停跑调用数据加载
PASS 临时目录已在 finally 中清理
59/59 passed

intel_run dry-run（r3 代码，只读真实 data，写到 /tmp/qlrev3/dry；正式 ALERTS 的 sha 前后一致）:
dry-run written /tmp/qlrev3/dry
sw_pit: stale 3 2026-10-16 data_integrity_errors= []
maxrss_MB 217.6
```

## sw_pit 当前判定（新规则）
- **stale**：built 10-14 04:00 美东 = 16:00 上海，覆盖到 10-13；参考日 = 上海最近已收盘交易日 10-16；落后 3 个交易日；coverage_gap 为 true；sha 校验通过，data_integrity_errors 为 []。
