# Arch 审查：Strategy sw_pit 新鲜度自检 r5（DIFF A）

- 审查时间：2026-10-18T05:40:19-04:00（`date +%Y-%m-%dT%H:%M:%S%:z`）
- 审查人：QuantLab Arch。只做静态审查：没有运行项目代码或测试，没有改动 research/、scripts/、data/，也没有写 .ok。
- 提案：docs/v2/audit/STRATEGY_SW_PIT_FRESHNESS_PROPOSAL_20261018_r5.diff，sha256 f7ab3b6216ffc61b7fbaa1984fa7a8ac81cdc4ee41cc0642110994d9b3b9da9d，164 行。实测 sha 与行数都和申报一致。
- 基线：commit 7dd5bea5（HEAD）。

## 结论：PASS（无 P0/P1/P2，3 条 P3，不阻塞）

可以签 code-change .ok 和 selftest .ok。

## 核对方法
- 用 `git archive HEAD` 自建了两份 /tmp 副本（/tmp/archrev/AB、/tmp/archrev/BA），没有用 Strategy 的 /tmp/swr5。
- 两个顺序都试过：先 A 后 B（AB），先 B 后 A（BA）。每一步 `git apply --check` 都通过，两种顺序得到的结果逐文件 sha 完全相同。
- A 只改 sw_pit_freshness.py 和 test_sw_pit_freshness.py，和 B 没有重叠。

## 文件表（old → new，sha256 全文，Arch 自算）

| 文件 | old（7dd5bea5） | new（r5 落地后） |
|---|---|---|
| research/sw_pit_freshness.py | 3116e4f697c887dc2dce27c747fde38691afe0fe2b3c27e6b87c183aa34dbf31 | 5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f |
| research/tests_sw_pit/test_sw_pit_freshness.py | a9b5c3e9825110d0e88e446d7dedd599b1acad023c5de7d3f4fead1be1041ec2 | cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e |

两个 new sha 都和 Strategy 申报的一致。

## 逐项核对
1. **in_date_range**：不是 list/tuple、长度不等于 2、缺失（`{}` 或 None），或者任一端 `date.fromisoformat` 解析失败，都抛 SwPitIntegrityError。✔
2. **built 解析失败**：`fromisoformat` 抛出的 TypeError/ValueError 统一转成 SwPitIntegrityError。built 缺失或为空时，原有的 `if not built` 照样会抛。✔
3. **只有“as_of 取默认”这一条提示时**：前缀改为「【披露】sw_pit 检查：as_of 取默认值（调用方未传），未判过期」，stale=False。同时还有其他告警时，仍用「可能过期」的前缀。✔
4. **日历兜底是否覆盖参照日和覆盖日**：r5 只显式检查了 built 和 now 两处（`_guard_cal`），但这已经足以推出另外两处：
   - 参照日 ref = `_completed_session(now_sh)`，必然 ≤ now_sh.date ≤ cal_end；
   - 覆盖日 coverage = `_completed_session(built_sh)`，必然 ≤ built_sh.date ≤ cal_end；
   - lag 统计的是 (coverage, ref] 里的开市日，这个区间完全落在日历以内；
   - 日历下界方面，`_completed_session` 在找不到更早的开市日时会抛错。
   结论：参照日和覆盖日都不会越出日历末尾，没有漏洞。✔
5. **max(default=)**：全文没有 `default=`。`_calendar` 先判断 `cal.empty` 并 raise，之后才对 cal_date 取 max。开市日为空时（例如 is_open 类型变了），`_completed_session` 会抛“calendar has no open day before”，不会悄悄当成数据是新的。✔
6. **缓存**：cal_end 跟 base 一起按 (root, level) 缓存；now 的兜底检查放在 `_evaluate` 里，每次调用都重新算。✔
7. **单测只用 tmp_path**：新增 4 个测试函数，其中一个参数化为 3 例，实际共 6 例。加上原有 6 例，合计 **12 例**。所有用例都通过 `_root(tmp_path…)` 自己造日历、parquet 和 manifest，没有读真实 data/。`tmp_path / "s"` 和 `tmp_path / "b"` 都是 tmp_path 下的子目录。✔
8. **逐条推演用例**（没有实际运行）：
   - built "14/10/2026 04:00"：Python 3.13 的 fromisoformat 不接受，抛错。
   - built 2026-10-20T01:00 ET：换算为上海 10-20 13:00，晚于日历末日 10-19，抛错。
   - now 2026-10-20 09:00 ET：换算为上海 10-20 21:00，晚于 10-19，抛错。
   - built 10-16T07:00 ET：换算为上海 19:00，覆盖到 10-16，lag 为 0，只剩“as_of 取默认”一条，结果中性。
   以上推演结果都和断言一致。
9. **pyflakes**（`PYTHONPATH=/tmp/pf python3 -m pyflakes`）：两个文件都没有新增警告。
10. **f 前缀**：新增行里带 `{}` 的字符串都有 f 前缀，没有漏写。
11. **off-by-one**：`_guard_cal` 用的是 `>`，日历末日当天本身允许，正确。lag 的区间是左开右闭 (coverage, ref]，保持不变。
12. **as_of 类型**：入参是 str 或 None，由 `_d()` 截前 10 位后转成 date，内部比较都用 date，和 r4 一样。

## 发现
- **P3-1（运维提醒，转 Data / 主 Agent）**：真实日历 trade_cal_sse_pit（fa4260b8）的 cal_date 范围是 20050101–20261231，最后一个开市日也是 20261231。所以从**美东 2026-12-31 11:00 起**（即上海 2027-01-01 00:00），所有调用 sw_pit 自检的地方都会硬停。这是设计如此，但 Data 必须在 12 月中旬前把日历延长到 2027 年。
- **P3-2**：in_date_range 先截前 10 位再解析（`str(x)[:10]`），所以带尾部杂字符的值也能通过；另外没有检查 rng[0] ≤ rng[1]。实际影响可以忽略，下次顺手改即可。
- **P3-3**：日历兜底只检查末端，不检查日历内部有没有缺日（中间漏掉的交易日会让 lag 少算）。目前日历由 Data 维护，sha 已钉住。登记为设计假设：“日历连续”由 Data 的日历 manifest 保证。

## Selftest（供签 .ok 用）
- 命令（解释器 /workspace/ql-enrich-venv/bin/python，Python 3.13.5；该环境装有 pytest 9.1.1、pandas 3.0.6、pyarrow 26.0.0）：
  `cd /workspace/QuantLab && PYTHONDONTWRITEBYTECODE=1 nice -n 10 /workspace/ql-enrich-venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/arch_swpit_r5_selftest research/tests_sw_pit/test_sw_pit_freshness.py`
- 预期结果：**12 passed**，exit 0。
- 测试文件 sha256：cee59fc5b99210f51b78ddde61e9ae5da16ab44bb47da1a1deb5fefb5380fe0e
- 被测文件 sha256：5191997e3a63be758c538c463464038694615f44f195e3f8e74427a9674db43f
- 仓库根目录没有 conftest.py、pytest.ini 或 pyproject 里的 pytest 配置。跑完后删除 basetemp；research/ 下不得新增 __pycache__ 或 .pytest_cache。
