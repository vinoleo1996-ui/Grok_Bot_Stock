# Arch 审查：Intel sw_pit 过期 + 完整性检查 r2（0e968759）

- 审查时间：2026-10-18T05:27:17-04:00
- 结论：**有条件通过（conditional）**。本版不签 code-change .ok / selftest .ok，需出 r3 修掉下列 4 个 P2。没有 P0/P1。
- 方式：只做静态审查。diff 打到 /tmp/arch_rev_i2（research/intel/*.py 的副本）上，跑 pyflakes；没有执行项目代码和测试。

## 一、核实项
| 项 | 结果 |
|---|---|
| r2.diff sha256 | 0e968759d390490d625c1a7705fd6505e19aeae968710ecbf6a818439c6da4b5（与声明一致，318 行） |
| r2_tests.py sha256 | 5dfa13b59427d214e4e670e9c98d159ebfbf6c292ad0ac93654e5e7fb1f3a419，与 diff 打出的 research/intel/test_sw_freshness.py 逐字节一致 |
| r2.md sha256 | 005ae544fa537db66e844cb14b14625ca1c36a2911d168e961d27800e5d84151 |
| 基线 | intel_common 9a725d5c…、intel_run 0de787c1…、intel_event_study ad95fe43…、intel_c1_gap_split 2063e6aa…；正式文件未改 |
| git apply --check / apply | 5 个文件全部干净打上 |
| pyflakes（打补丁后 vs 基线） | 无新增告警。基线已有的只有 intel_run.py:67 sgn_factor 未使用 |
| f-prefix | AST 扫描：含 {name} 的非 f 字符串只出现在 docstring，没有漏写 f |
| 元数据 | trade_cal：cal_date 为 str YYYYMMDD，is_open 为 int64，范围 20050101–20261231；manifest.built=2026-10-14T04:00:19.995930（不带时区）；l1.in_date_range=[1984-05-09, 2026-09-24]；parquet 的 in_date/out_date 为 timestamp[us] |
| 现值判定（手算） | built 美东 10-14 04:00 = 上海 16:00，早于 18:00，覆盖到 10-13；参照日 10-16；落后 3 个交易日，判 stale。与 Intel 的说法一致 |

## 二、按统一口径逐条
- R1 ≥3 个开市日判 stale：符合。lag 取区间 (cov, last_td]，没有差一错误。
- R2 built 时区：naive 的情况符合（tz_localize 美东，再 tz_convert 上海，hour≥18 当天覆盖，18:00 整点算覆盖当天），05:59/06:00 边界有测试。**带时区的 built 没有处理（见 P2-1）。**
- R3 完整性硬停：manifest 不可读、parquet 缺失、sha 不一致或未登记、built 缺失，都抛 TableIntegrityError；require_fresh 遇到时报 HARD STOP，--allow-stale 也不放行。符合。**但日历为空或缺失时没有硬停（见 P2-2）。**
- R4 成分 as-of：sw_members_asof 写的是 in_date<d 且 (out_date 为空或 out_date>=d)，符合。event_study、c1 两处都已替换。intel_run 用上海日期，18:00 之后取 +1 天，也符合可用时点。
- R5 coverage_gap：没有单独字段（见 P3-1）。

## 三、发现
### P2（r3 必改）
- **P2-1 带时区的 built 会崩，而且绕过方案 A。** `pd.Timestamp(built).tz_localize(BUILT_TZ)` 遇到带时区的 built 会抛 TypeError，不符合 R2（带时区应该用 astimezone/tz_convert）。另外，industry_stocks 只捕获 TableIntegrityError，所以 TypeError、built 无法解析的 ValueError、日历缺失的 FileNotFoundError、美东夏令时歧义时刻的 AmbiguousTimeError 都会直接冒出去，intel_run 整轮崩掉，实际变成了方案 B。改法：naive 用 tz_localize(…, ambiguous=True/False 明确取一个值)，带时区用 tz_convert；把检查函数内部的 built 解析、日历读取等异常统一包装成 TableIntegrityError。
- **P2-2 日历为空或不覆盖时会静默判 ok。** `max(..., default=asof)` 和 `max(..., default=bd)` 让空日历算出 lag=0，结果是 ok，等于把坏日历当成数据新鲜。改法：开市日为空、找不到 cov 之前的开市日、或者日历最大日期早于参照日时，一律抛 TableIntegrityError（Strategy r4 已经这么做了，团队口径要一致）。注意：现在的日历只到 20261231，2027-01-01 以后会稳定地少算 lag。
- **P2-3 方案 A 的错误不够醒目。** 代码确实只停了行业→个股映射：industry_stocks 返回 {}，各行业 stocks 为空；merge_prev 不会把旧的 stocks 带回来；sw_pit 不产出任何个股级输出。这部分符合要求。但 HIGH 那一行只在 md 最末尾，排在新闻源状态之后；每个行业的「相关个股：」后面是空的，也没有写原因；json 只在 source_status.tables.sw_pit 里有，顶层没有标记，pool_session 显示为 None。r3 要做到：md 标题下第一行加横幅「⚠ HIGH：sw_pit 完整性错误，本轮未输出相关个股」；每个行业的个股行写「（sw_pit 完整性错误，已停）」；json 顶层加 `data_integrity_errors: [{table, severity:"high", disclosure}]`，供 alert-ingest 读取。
- **P2-4 测试在出问题时会碰正式输出、联网。** intel_event_study 和 intel_c1_gap_split 在 import 时就把 `R = C.ROOT`（以及 c1 的 `OUT`）绑定成真实 ROOT。测试只替换了 C.ROOT，所以只要停跑逻辑出了回归，mod.main() 就会接着读真实数据，调 yahoo_daily 联网，并写正式文件 output/intel/event_study_full.csv、event_study_hitrate.json 和 output/intel/pit_candidates/c1_*。改法：测试里同时把 S.R、G.R、G.OUT 替换成 tmp，把 C.yahoo_daily、S.a_share_industry_returns、G.legs 替换成抛哨兵异常的函数，并用 try/finally 清理 tmp 目录。

### P3
- P3-1 R5：没有单独的 coverage_gap 字段。Intel 的 asof 同时充当参照日和决策日，lag_days 已经写进披露，coverage_gap 实际上等价于 lag≥1，所以不阻塞。请在 r3 加 `coverage_gap: bool` 和 `as_of_decision` 字段，和 Strategy 的回执字段对齐。
- P3-2 参照日：默认值用美东日期，没有按上海「已完成交易日」计算。美东 00:00–05:59（夏令时）落在开市日时会多算 1 天，偏保守，可能把 lag 2 误判成 3。建议改成和 Strategy 的 _completed_session 一样的规则。
- P3-3 自加的「缺 in_date_range 也硬停」：**接受**。理由是这个字段缺失说明 manifest 结构损坏，按完整性错误处理合理。Strategy r4 目前对此不停跑，下一版对齐。
- P3-4 检查和读取之间有窗口：sha 校验完以后再单独 read_parquet，中途文件被替换的话会读到未校验的版本。建议校验和读取用同一份 bytes，或者读完再复核一次 mtime。
- P3-5 测试覆盖：缺带时区 built、空日历、缺 in_date_range/built 这三种用例；tmp 清理不在 finally 里。
- P3-6 卫生：Intel 的临时副本 /tmp/qlrev 里，output 和 data 是指向正式目录的符号链接。我按 mtime 查过，05:00 以后 output/intel 没有新文件，这次没有写到正式输出。以后临时副本不要链接 output。
- P3-7 解释器：.venv_opt（3.13.5）没有 matplotlib，也没有 pytest，测试会在 import intel_c1_gap_split 时 ImportError（此前已有 20 条 check 输出）。本机只有 /workspace/qlvenv/bin/python（3.12.14，pandas 3.0.6，pyarrow 25.0.1，matplotlib 3.11.2）能完整跑完。selftest .ok 必须写明这个解释器。

## 四、对 Intel 待定问题的裁定
- **采用方案 A**，前提是 P2-1（非 TableIntegrityError 的异常不能绕过）和 P2-3（醒目披露 + json 顶层标记）都已修好。代码已核实：完整性错误时不产生任何来自 sw_pit 的个股级输出。
- 「缺 in_date_range 也硬停」：接受（P3-3）。

## 五、r3 之后 selftest 的命令（供下一次签 .ok 用，本版不签）
```
cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 /workspace/qlvenv/bin/python research/intel/test_sw_freshness.py
```
- 这是普通脚本，不是 pytest，退出码 0 表示全部通过。
- 会 import：intel_common（pandas，标准库 urllib/xml，import 时不联网）、intel_event_study（numpy、pandas）、intel_c1_gap_split（matplotlib Agg，属于重模块）。
- PYTHONDONTWRITEBYTECODE=1 是为了避免在 research/intel/__pycache__ 写 pyc。

## 六、r2 打补丁后的 sha（仅供参考，r3 会变，不作为 .ok 的 pin）
- intel_common.py：9a725d5c… → f704fedd33223270281ba1da3e8db48b06444714e46103a17a7c4904646ce3fb
- intel_run.py：0de787c1… → ea8ddf771025727b4630499e77f06f1d34d8b15409f5f03ba393b1b6f075a439
- intel_event_study.py：ad95fe43… → 05f1d3160ee4a3216be52bd8b10679115f3829961fd78bb7b3715fea37b44fde
- intel_c1_gap_split.py：2063e6aa… → cde6d09516e92f177f83fcfb0da217ff4adbd72a3d854af0e742d97822d8dee8
- test_sw_freshness.py（新增）→ 5dfa13b59427d214e4e670e9c98d159ebfbf6c292ad0ac93654e5e7fb1f3a419
