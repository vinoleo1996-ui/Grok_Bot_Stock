# COVER · 候选3 箱上 port 侧稿（禁 enable）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Eng |
| 时刻 | `2026-10-26T14:02:25-04:00`（America/New_York；墙钟 `2026-10-26 14:02 ET`） |
| 对照 Arch | `ARCH_CAND3_ORIGIN_PR6_INTENT_REVIEW_20261026_ZH.md` sha8 **`c5b0ce67`** PASS_WITH_CONDITIONS §4 |
| 箱 HEAD | `da9fde6a`（期望 `da9fde6` → **MATCH**） |
| 结论 | **侧稿 DIFF 已交；生产主干未改；复审前不 enable** |

## 0. 一句话

按 Arch §4 / 主令：把 Origin #6 的意图（禁 `bdate_range`、国庆断言、legacy 废弃、可选 `calendar_required`）接到箱上现网模块的**侧稿副本**；**保留** SSE `trade_cal.parquet` + `CUTOFF_ET` + 纸面 `data_freshness`；**禁整文件合 #6**；**未改** `/workspace/QuantLab/quantlab/**` 生产文件。

## 1. 钉表（改侧稿前核）

| 文件 | 路径 | 期望 sha8 | 实测 sha8 | 结果 |
|---|---|---|---|---|
| research_loop.py | `quantlab/portfolio/research_loop.py` | `d3ded87e` | `d3ded87e` | **MATCH** |
| trade_calendar.py | `quantlab/portfolio/trade_calendar.py` | `ef44e7cd` | `ef44e7cd` | **MATCH** |
| settle.py | `quantlab/agents/trading_loop/settle.py` | `808f77d6` | `808f77d6` | **MATCH** |
| sources.py | `quantlab/data/sources.py` | `5ee62db0` | `5ee62db0` | **MATCH** |
| HEAD | `/workspace/QuantLab` | `da9fde6` | `da9fde6a` | **MATCH** |

## 2. 改了什么（侧稿）

| 侧稿 | 变更 |
|---|---|
| `port/trade_calendar.py.port` | **最小**增量：`_OPEN_DAYS_OVERRIDE` + `_set_open_days_for_test`（仅测）；`advance_open_days(d,n)`；`open_day_range(start,periods)`。**未改** `SRC`/`DATA_CAL`/`CUTOFF_ET`/`cross_check`/`expected_session`/`open_days` 读盘逻辑意图 |
| `port/settle.py.port` | mock 分支 `pd.bdate_range` → `open_day_range`（SSE 开市日）；schemas 改绝对 import（便于侧稿加载；行为不变）；**真实 etf_daily_adj 路径未动** |
| `port/research_loop.py.port` | `_legacy_freshness`：`DeprecationWarning` + DEPRECATED docstring（weekday / CN holidays not modeled）；**`data_freshness` 主路径未改** |
| `port/sources.py.port` | **可选已做**：`_a_daily` 无 `expected_session` 时优先 `trade_calendar.expected_session`；失败则 `attrs["freshness"]="calendar_required"`，**去掉**默认 `BDay`/weekday；其它 DataFeed 行为保留 |

## 3. 保留了什么（硬）

- 箱上 `data/v2/tushare_raw/trade_cal.parquet` 路径与 Data `cross_check`
- `CUTOFF_ET=(6,30)` 与纸面 `research_loop.data_freshness` 闸
- 真实 settle etf 路径意图
- **未** merge Origin #6；**未**整文件覆盖生产模块
- 叶25 CONSUMED / A18 签窗 / `9e4359f9`：**未碰**

## 4. 如何测

```bash
cd /workspace/QuantLab
PYTHONPATH=/workspace/QuantLab /workspace/qlvenv/bin/pytest -q \
  docs/v2/audit/cand3_sse_calendar_20261026/port/test_trade_calendar_settle_port.py
# → 9 passed（合成日历；禁读真实大数据 parquet）
python3 -m py_compile docs/v2/audit/cand3_sse_calendar_20261026/port/*.py.port
```

国庆窗 2025-10-01..10-07：到期/期望日不落休市；对比 `bdate_range` 会落 10-01；settle mock exit=`2025-10-08`。

## 5. 禁 enable

- 本包为 **侧稿**；Arch **port 复审通过前不 enable**、不签纸面 enable `.ok`、不 `git commit`、不改生产 `quantlab/**`
- live=false；promotion*=false；≠X2

## 6. 交付清单（落盘 sha8）

| 件 | sha8 |
|---|---|
| `DIFF_cand3_box_port_20261026.diff` | `24e055fa` |
| `COVER_cand3_box_port_20261026_ZH.md` | （本文件；以 SHA256SUMS 为准） |
| `ENG_CAND3_BOX_PORT_RECEIPT_20261026_ZH.md` | （回执；以 SHA256SUMS 为准） |
| `port/trade_calendar.py.port` | `d2b6046c` |
| `port/settle.py.port` | `c423e96e` |
| `port/research_loop.py.port` | `5fe238f2` |
| `port/sources.py.port` | `c8102489` |
| `port/test_trade_calendar_settle_port.py` | `80f8eca9` |
| `port/pytest_cand3_box_port_20261026.log` | `52128d66` |

完整指纹见 `SHA256SUMS.txt`。
