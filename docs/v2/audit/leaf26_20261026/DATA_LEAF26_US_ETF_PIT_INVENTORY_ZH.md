# Data：叶26 美 ETF PIT 盘点（研究级）

- 角色：QuantLab Data 执行器
- 时刻：2026-10-26 01:17 ET (America/New_York)
- 约束：live=false；禁外网拉取；禁写生产

---

## 1. 盒上检索结论

在 `data/` 与 `data/v2/` 下按名检索：`us_etf` / `kweb` / `sox` / `spy` / `qqq` / `premium`（美股语境）—

**0 命中**带 `available_at` 的美股 ETF parquet。  
与 aaf84d66 §5.2 **无 DELTA**（仍 GAP）。

---

## 2. 现有 Intel ALERTS 旁路（非 PIT 主库）

| 路径 | sha256（本回合） | 备注 |
|---|---|---|
| `output/intel/ALERTS_latest.md` | `5f952e7bf376a25cbf933c5cc62297fa1f6485790362813eb31b7af12e71c88c` | mtime≈2026-10-26 01:01 ET；文内含 **KWEB** / 美股 / yahoo |
| `output/intel/ALERTS_latest.json` | `74b3de45f9a32d483991302a2d01dc3f88e8c0f5e93258bb6f49b4ac5031f441` | 同上 |
| `output/intel/history/ALERTS_*` | （历史快照族） | 事件旁路；**非** `data/v2` PIT |

> DELTA 说明：aaf84d66 未钉 ALERTS 当日 sha（旁路随 Intel 刷新）。本回执记录**当前**旁路 sha，供对照；**不**视为生产表漂移。

---

## 3. 建议时区规则草案（未落地）

```
session_us     = US/Eastern 正则交易日收盘（含夏令时）
raw_available  = US close + buffer（建议 30–60min，覆盖官方结算延迟）
available_at   = 下一 SSE 交易日 09:00 Asia/Shanghai
                 （若 raw_available 已过该 09:00，则再顺延一个 SSE 交易日）
tz 字段        = 同时保留 available_at_tz='Asia/Shanghai' 与 session_us_tz='America/New_York'
stale          = 美股周末/假日无更新时标 stale=true，特征冻结
```

建议研究表路径（待签）：`data/v2/us_etf/us_etf_daily_pit.parquet`  
列草稿：`symbol,session_us,trade_date_us,ret_1d,close,available_at,available_at_tz,stale,source,promotion_approved`。

---

## 4. 状态

**仍 GAP**。除非未来出现现成 PIT 表，否则不可称 OK。  
本回合推进：检索结论复测、ALERTS 旁路路径+sha、时区规则草案。  
**不阻塞**叶26 r2 主规格（Intel 可选外生冲击）。
