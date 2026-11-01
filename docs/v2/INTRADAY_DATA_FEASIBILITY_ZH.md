# 盘中数据源可行性计划（仅计划；不做实盘、不起常驻轮询）— 2026-10-14 ET

## 现状
- 盒子上只有日线（data/v2/*）。paper-daily 只做 EOD。
- tushare 访问走 `quantlab/data_sources/tushare_proxy`（relay / datahub，经 Mac Clash 代理）。盒子上没有直连 token 文件/环境变量（未打印任何凭据）。

## 轻量探测（2026-10-14 01:4x ET，单进程，每接口 1 次）
| 源 | 接口 | 结果 |
|---|---|---|
| tushare relay/datahub | rt_k / realtime_quote / stk_mins / rt_min / daily | 90s 内无返回（超时被杀），连 daily 也没回来 → 代理当时不可达，**权限无法判定** |
| 新浪 hq.sinajs.cn | list=sh600000 | HTTP 200，1.4s（需 Referer 头） |
| 东方财富 push2 | qt/stock/get | HTTP 502（盒子出口被拒/限流） |
| akshare | — | 未安装（底层也是抓新浪/东财） |

## 选项对比
| 选项 | 延迟 | 限频/权限 | 可靠性 | 备注 |
|---|---|---|---|---|
| tushare `rt_k`/`realtime_quote` | 秒级快照 | 需要单独的实时权限（按积分/付费分档）；realtime_quote 是爬虫型接口 | 取决于 relay 可用性 | 首选，口径和现有数据一致；**需先确认 token 是否有 rt 权限** |
| tushare `stk_mins`/`rt_min` | 分钟线 | 分钟权限需单独开通，有每分钟调用上限 | 中 | 适合盘后补分钟数据、做 VWAP 回测 |
| 新浪 hq.sinajs.cn | 约 3s 快照 | 无官方 SLA，批量查询可一次 ~800 只；高频会被封 IP | 中低 | 已测通；适合每 1-5 分钟查一次持仓 + 510300 |
| 东方财富 push2 | 秒级 | 无官方 SLA；盒子出口当前 502 | 低（当前不可用） | 备选 |
| akshare | 同新浪/东财 | 同上 | 中低 | 只是封装，加依赖意义不大 |

## 建议路径（需 Leo/Strategy 批准后才实施）
1. Data 确认 tushare token 的 rt_k / realtime_quote / stk_mins 权限（他们持有凭据），确认 relay 盘中可用。
2. 只读、按需的快照器 `intraday-snapshot`：只查 paper 持仓（≤20 只）+ 510300，一次批量请求；手动或调度器调用，**不常驻**；写入 `data/v2/intraday/snap_<date>.parquet`，带 source/latency 字段。
3. 用途限于风险监控（盘中回撤、涨跌停、alert 联动），不改权重、不下单；paper NAV 仍按 EOD + T+1 开盘成交。
4. 降级顺序：tushare → 新浪；失败就记 GAP，不重试轰炸。

## 更新（2026-10-14，依据 Data 的 docs/v2/DATA_REALTIME_MIN_PERM_PROBE_ZH.md）
- **可用（仅经 relay/promax）**：`rt_k`（实时日K快照）、`rt_min` 1MIN、`stk_mins` 1min、`pro_bar` 1min。
- **datahub 拒绝**以上接口；`realtime_quote` 不可用。之前 Eng 探测超时是代理当时不可达，不是权限问题。
- 新浪仅作降级备选；东财盒子出口 502。

### 计划（研究级，仅计划，不构建）
- 范围：只做 paper 持仓（capacity_adv / B4 / S6 影子，≤~30 只）+ 510300 的**按需**盘中监控与风险标记。
- 取数：relay/promax `rt_k` 一次批量快照（持仓 + 510300）；需要分钟路径时用 `rt_min`/`stk_mins` 1min 只拉当天这些代码。不走 datahub。
- 触发：手动或外部调度单次调用，**无常驻轮询**；每次调用有限频和超时，失败记 GAP 不重试。
- 产出：`risk_flag` 盘中版（个股盘中跌幅/涨跌停/510300 跌幅阈值 + 与 AI intel alert 联动），只写监控文件，**不改权重、不下单**；paper NAV 仍按 EOD + T+1 开盘成交。
- 前置：Leo/Strategy 批准后才写代码；Data 确认 relay/promax 的调用配额。
