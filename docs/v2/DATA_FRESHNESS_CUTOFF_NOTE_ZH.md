# 新鲜度截止口径对齐说明（只写说明，未改代码）
2026-10-14 06:56 ET，Data。对应审计 #15。

## 现状（三个口径）
| 位置 | 常量 / 环境变量 | 值 | 换算 |
|---|---|---|---|
| `scripts/acquire/data_freshness_status.py:10`（Data 新鲜度文件） | `FRESH_CUTOFF_HOUR`（默认 20），按 Asia/Shanghai 判断 | 上海 20:00 | = **ET 08:00（夏令时 EDT）** / ET 07:00（冬令时 EST，11-01 起） |
| 审计文档引用的 `trade_calendar.py:15 CUTOFF_HOUR_ET=17` | — | ET 17:00 | = 上海次日 05:00（EDT）/ 06:00（EST） |
| **当前代码** `quantlab/portfolio/trade_calendar.py:16`（Eng 06:46 ET 已改） | `CUTOFF_ET=(6,30)`；测试用 `QL_ASOF_ET` 覆盖“现在” | ET 06:30 | = 上海 18:30（EDT）/ 19:30（EST） |
审计里的 ET17 已过时，现在 Eng 门控用 ET 06:30。

## 含义
- 判定“交易日 D 的数据现在是否必须已到”：Data 用上海 20:00，Eng 用 ET 06:30（=上海 18:30）。上海 18:30–20:00（ET 06:30–08:00）这 1.5 小时两边会差一天：Eng 要求 D，Data 文件仍只要求 D-1、报 ok。
- 收盘 15:00 上海 = ET 03:00；Data 日更 05:55 ET 起跑、约 06:07 ET 完成。
- ET 有夏令时，上海没有，所以用 ET 写死的口径在 11 月会整体平移 1 小时。

## 建议的统一口径（需 Eng/主 Agent 拍板后再改代码）
1. 只保留一个常量，放在 `quantlab/portfolio/trade_calendar.py`，**用 Asia/Shanghai 时区定义**（不受夏令时影响），例如 `CUTOFF_SH=(18,30)`（今天等于 ET 06:30，和 Eng 现值一致；冬令时等于 ET 05:30，仍晚于 Data 约 06:07 ET 完成——但冬令时日更若仍按 ET 05:55 起跑则需改为上海 18:55 触发）。
2. `data_freshness_status.py` 改为 import 该常量，`FRESH_CUTOFF_HOUR` 仅保留为覆盖用，写进输出字段 `cutoff_sh`/`cutoff_et` 两个都写。
3. Eng 门控建议同时接受 target_trade_date ≥ expected（解决 Data 早到被拒的问题，见 TEAM_STATE 06:45 Eng 记录）。
