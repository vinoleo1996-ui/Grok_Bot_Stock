# Arch 复审：候选3 箱上 port DIFF（只审不签）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch（执行器 port 复审） |
| 时刻 | `2026-10-26T14:08:30-04:00`（America/New_York；墙钟 `2026-10-26 14:08 ET`） |
| **结论** | **PASS_WITH_CONDITIONS** |
| 本回合动作 | **不签**任何 `.ok`；**不挂 QUIET**；**不 apply**；**不改**生产 `quantlab/**`；**不 merge** Origin #6；**不 enable**；≠X2；live=false；promotion=false；**不报 Leo**；**不混** A18 §5.2（14:15 SIGN）与叶25 X2 selfcheck（16:15 SIGN）；勿动叶25 CONSUMED（`3c297052`/`d37a157e`）；禁消费 `9e4359f9` |
| 触发 | 主 ~14:04/14:05 ET priority 令（TEAM_STATE）；Eng port 回执已落盘 |
| 对照意图审 | `ARCH_CAND3_ORIGIN_PR6_INTENT_REVIEW_20261026_ZH.md` sha8 **`c5b0ce67`** |

## 0. 一句话

箱上 port 侧稿落实意图审 §4：DIFF 可解释为「生产钉 → 侧稿」增量（非整文件 stub）；**保留** SSE `trade_cal.parquet` + `CUTOFF_ET=(6,30)` + 纸面 `data_freshness`；settle mock **禁** `pd.bdate_range`；legacy **DeprecationWarning**；sources 可选 **`calendar_required`**；国庆合成测 **9 passed**（本审复跑 OK）。生产四文件+HEAD 仍 MATCH；**建议主令 Eng 按本 DIFF apply 侧稿到生产**；**enable 仍禁**（须 apply 后另轮确认）。本审**不构成** `.ok` / enable / merge 授权。

## 1. 钉表（复审再核）

| 件 | 路径 | 期望 sha8 | 实测 sha8 | 结果 |
|---|---|---|---|---|
| 意图审 | `ARCH_CAND3_ORIGIN_PR6_INTENT_REVIEW_20261026_ZH.md` | `c5b0ce67` | `c5b0ce67…` | **MATCH** |
| DIFF | `DIFF_cand3_box_port_20261026.diff` | `24e055fa` | `24e055fa…` | **MATCH** |
| COVER | `COVER_cand3_box_port_20261026_ZH.md` | `da27e282` | `da27e282…` | **MATCH** |
| Eng port 回执 | `ENG_CAND3_BOX_PORT_RECEIPT_20261026_ZH.md` | `8dface80` | `8dface80…` | **MATCH** |
| tc 侧稿 | `port/trade_calendar.py.port` | `d2b6046c` | `d2b6046c…` | **MATCH** |
| settle 侧稿 | `port/settle.py.port` | `c423e96e` | `c423e96e…` | **MATCH** |
| rl 侧稿 | `port/research_loop.py.port` | `5fe238f2` | `5fe238f2…` | **MATCH** |
| sources 侧稿 | `port/sources.py.port` | `c8102489` | `c8102489…` | **MATCH** |
| 测脚本 | `port/test_trade_calendar_settle_port.py` | `80f8eca9` | `80f8eca9…` | **MATCH** |
| 测日志（Eng） | `port/pytest_cand3_box_port_20261026.log` | `52128d66` | `52128d66…` | **MATCH**（文案 `9 passed`） |
| 生产 research_loop | `quantlab/portfolio/research_loop.py` | `d3ded87e` | `d3ded87e…` | **MATCH**（未改） |
| 生产 trade_calendar | `quantlab/portfolio/trade_calendar.py` | `ef44e7cd` | `ef44e7cd…` | **MATCH**（未改） |
| 生产 settle | `quantlab/agents/trading_loop/settle.py` | `808f77d6` | `808f77d6…` | **MATCH**（未改；仍含 `pd.bdate_range`） |
| 生产 sources | `quantlab/data/sources.py` | `5ee62db0` | `5ee62db0…` | **MATCH**（未改） |
| HEAD | `/workspace/QuantLab` | `da9fde6` | `da9fde6a…` | **MATCH** |

本审复跑：`PYTHONPATH=/workspace/QuantLab /workspace/qlvenv/bin/pytest -q …/port/test_trade_calendar_settle_port.py` → **9 passed**（~0.39s）；复跑后生产四钉仍 MATCH。

## 2. 复审清单（逐项）

| # | 检查项 | 结果 | 证据 |
|---|---|---|---|
| 1 | DIFF 与侧稿 sha MATCH；DIFF=生产→侧稿增量（非整文件 stub） | **PASS** | 侧稿 sha 全 MATCH；prod→port 增量约 tc +37/−0、settle +4/−2、rl +12/−1、sources +15/−3；DIFF 含 `advance_open_days`/`open_day_range`/`DeprecationWarning`/`calendar_required` 与 `- pd.bdate_range` |
| 2 | **保留** SSE `data/v2/tushare_raw/trade_cal.parquet` + `CUTOFF_ET=(6,30)` + 纸面 `data_freshness` | **PASS** | 侧稿 `SRC`/`DATA_CAL`/`CUTOFF_ET`/`cross_check`/`expected_session` 保留；`data_freshness()` 体与生产 **逐行相同**（68 行） |
| 3 | settle：mock `bdate_range`→`open_day_range`；真实 etf 路径未伤 | **PASS** | mock 分支改 `open_day_range`；侧稿无代码态 `pd.bdate_range`；`DEFAULT_ETF_DAILY` / `_load_closes` / `etf_daily_adj` 分支保留 |
| 4 | research_loop：`_legacy_freshness` DeprecationWarning；主 freshness 未改意图 | **PASS** | docstring DEPRECATED + `warnings.warn(..., DeprecationWarning)`；`data_freshness` 同生产 |
| 5 | trade_calendar：仅测钩/advance/open_day_range 增量；读盘/CUTOFF/cross_check 保留 | **PASS** | `_OPEN_DAYS_OVERRIDE` + `_set_open_days_for_test`（注明测用）；`cross_check`/`expected_session`/`prev_trading_day` 体相同；`first_trading_day_on_or_after` 体相同（仅尾空白） |
| 6 | sources：可选 `calendar_required`；无日历不静默 BDay | **PASS** | `_a_daily` 优先 `trade_calendar.expected_session`；失败标 `attrs["freshness"]="calendar_required"`；已去 `BDay`/weekday 默认 |
| 7 | 国庆断言测存在且 9 passed 可信 | **PASS** | 测覆盖 Oct1–7 不落休市、对比 `bdate_range`→10-01、settle mock exit=`2025-10-08`、legacy 警告、sources 文本闸；Eng 日志+本审复跑均为 **9 passed** |
| 8 | 生产四文件+HEAD 仍 MATCH；禁整文件合 #6 | **PASS** | 复审前后钉 MATCH；侧稿在 `port/`；未碰 Origin #6 merge；未改 `quantlab/**` 目标四文件 |

## 3. CONDITIONS（可执行；不挡「建议 apply」）

1. **建议主令 Eng apply 侧稿到生产**——范围仅本包 DIFF/`port/*.py.port`；**禁**整文件用 Origin #6 stub 覆盖箱上模块。
2. **合入顺序**：先 `trade_calendar.py`（引入 `open_day_range`/`advance_open_days`），再 `settle.py`（依赖前者）；`research_loop.py` 与 `sources.py` 可同批或随后。
3. **apply 后 Eng 须交**：四文件新 sha8 + HEAD；最小 `py_compile`/import smoke；可保留/复跑侧稿测；相对 import vs 绝对 import（settle 侧稿为便于加载改为 `quantlab.agents…schemas`——合入生产任选其一，须证明可 import）。
4. **enable 仍禁**：apply ≠ enable；纸面 enable / 签 enable `.ok` / 晋级须 **另轮 Arch**；本审不授权。
5. **隔离**：勿混 A18 §5.2（14:15–16:00 SIGN）与叶25 X2 selfcheck（16:15–17:45 SIGN）；勿动叶25 CONSUMED；禁消费 `9e4359f9`；≠X2；live=false。

## 4. 本回合未做（硬约束复核）

- 未签任何 `.ok`；未挂 QUIET；未 apply 侧稿到生产；未改 `quantlab/**` 生产目标文件；未 merge Origin #6；未 enable；未 SendToUser / SendToAgent；不报 Leo；live=false；promotion=false；≠X2；未混 A18/叶25 签窗。

## 5. 给主的收口

| 项 | 值 |
|---|---|
| 结论 | **PASS_WITH_CONDITIONS** |
| 审回执 | `docs/v2/audit/cand3_sse_calendar_20261026/ARCH_CAND3_BOX_PORT_REVIEW_20261026_ZH.md`（落盘后 sha8 见 SHA256SUMS） |
| 生产未改 | **确认**（四钉+HEAD MATCH） |
| 建议下一手 | 主令 Eng **apply** 本侧稿 DIFF → Eng 交新钉 →（可选）Arch 合入核 → **仍不 enable** 直至另令 |
| 签窗错开 | A18 14:15 / 叶25 16:15 **未动本审** |
