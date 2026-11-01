# 研究级盘中分钟数据监控：最小方案（2026-10-14）
live=false；只出风险标记，不改权重、NAV 或任何状态；不设轮询，按需手动触发。
- **数据**：relay/promax 的 `rt_min` 1MIN（备选 `stk_mins` 1min），每批 50 个代码，只拉当天。不走 datahub。调用前请 Data 确认配额。
- **范围**：纸面持仓的最新交易日，即 B4 60/100万、S6 60/100万、capacity_adv leg_pin 的并集（当前 38 个代码），外加 510300.SH。
- **规则**：个股相对昨收 ≤-5% 记 watch，≤-8% 记 high，≤-9.5% 额外标 near_limit_down；510300 ≤-2% 记 watch，≤-3.5% 记 high，scope=market。阈值是研究初值，未经回测。
- **原型**：`python3 scripts_eng/intraday_monitor_dryrun.py`
  - 默认 dry-run：只生成代码清单和请求计划，不联网；
  - `--bars-csv`：用离线 CSV 测试；
  - `--fetch`：发起一次按需 relay 调用，本次未执行。
  - 输出：output/loop/intraday/plan_*.json、flags_*.parquet。flags 的字段沿用 ALERT 合约的 severity/scope，只追加 `risk_flag_only=True`。
- **测试**：dry-run 得 38 个代码；离线 CSV 4 行，-10% 判 high，-5% 判 watch，510300 -3% 判 watch，-1% 判 info，均符合预期。
- **下一步（需批准）**：Data 确认配额后做一次盘中 `--fetch` 实测；再决定是否把 flags 接进 alert-ingest，作为 source=intraday。
