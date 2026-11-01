# Eng 候选3 短回执（alphalens #74 / 60755d1）

- 时间：2026-10-26T13:47:15-04:00（America/New_York）
- 令：主 QUIET lift 后采纳候选3；live=false；promotion*=false；≠X2；勿复跑叶25；不动 CONSUMED `.ok`
- Origin PR：[QuantLab #6](https://cursor.com/codebase/leo-vino/QuantLab/pull/6)
- 分支：`cursor/sse-calendar-freshness-settle-1269` @ `986627db…`
- 云端：`bc-f6cbb47f-6463-5fc7-b05e-d7ce287b1269`
- 测试：云端 `pytest tests/test_trade_calendar_settle.py tests/test_data_execution.py` → **16 passed**；`py_compile` 通过

## Origin 侧做了什么
- 新增/改写 `trade_calendar` API（`open_days` / `expected_session` / …）
- `DataFeed._a_daily` 去掉默认 `BDay` weekday 新鲜度闸；无日历 → `calendar_required`
- 新增 stub `research_loop.py`（re-export）与 `agents/trading_loop/settle.py`（`open_day_range` / `holdings_expiry`，禁 `bdate_range`）
- `_legacy_freshness` 仅 DeprecationWarning
- 合成国庆窗 2025-10-01..10-07 断言

## 箱上对照（重要）
箱上 `/workspace/QuantLab` HEAD `da9fde6` **尚未合入**本 PR，且与 Origin `main`（`7197939d…`）**分叉**：
- 箱上已有完整 `quantlab/portfolio/research_loop.py`（含纸面 `data_freshness` SSE 闸 + `_legacy_freshness` L704）
- 箱上已有完整 `quantlab/portfolio/trade_calendar.py`（读 `data/v2/tushare_raw/trade_cal.parquet`）
- 箱上 `quantlab/agents/trading_loop/settle.py` **仍** `pd.bdate_range`（约 L79）

PR 在 Origin 上是「新增 stub 模块」，**不能直接当箱上生产树的补丁合并**，否则会覆盖/旁路既有纸面闸。

## 建议下一步（Eng→主/Arch）
1. Arch 审 Origin #6 设计意图（国庆断言 / calendar_required / deprecated legacy）PASS 与否
2. Eng 另开 **箱上 port 包**（侧稿 DIFF）：把 #6 的「禁 bdate / 国庆断言 / legacy 废弃」接到现网 `research_loop`/`trade_calendar`/`settle.py`，保留箱上 SSE `trade_cal.parquet` 路径与 cutoff 规则；勿整文件覆盖
3. 合入箱上后再谈 enable；未合入前纸面主路径行为不变

## 未做
禁盲 merge；未动 daily_basic / wrapper / X2 / leaf25；A18 仍等 Arch 方案 A。
