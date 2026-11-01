# DataHub 全量验证摘要（Leo 报告 · 2026-10-10）

云端经 Mac Clash：`DATAHUB_HTTP_PROXY=http://100.102.49.98:7897`（见 `DATAHUB_VIA_MAC_PROXY.md`）。
`promotion_approved=false`；本摘要只指导采集，不晋升。

## 对本项目缺口可用

| API | 用途 |
|-----|------|
| `stock_basic` | 证券主数据 |
| `daily` | OHLC/量额 → asof_extend |
| `daily_basic` | `circ_mv` → 日频 float_mktcap |
| `stk_limit` | 涨跌停 |
| `income` / `balancesheet` / `cashflow` | 财报 + `ann_date`/`f_ann_date` |
| `fina_indicator` | 财务指标（需 `ts_code`） |
| `disclosure_date` | 预约披露 |
| `dividend` | 分红除权对账 |
| `fund_daily` | 510300 交叉校验 |
| `index_classify` | 申万层级 |
| `index_member_all` | 申万成分 PIT（**必须** `l1_code=801010.SI` 风格，禁止 `110000`） |
| `trade_cal` | 交易日历 |

## 注意 / 跳过

- `margin_detail`：本地缓存缺 SZ/BJ → 若用必须强制 `fields=` 绕过缓存
- `index_member_all`：`l1_code` 用 `801010.SI` 等，**不要** `110000`
- 8 个行业专题接口已死 → 跳过
- `pro_bar` 不支持；`stk_factor_pro` 502 → 跳过
- 分页 `limit` 最大 5000；`offset` 配 `limit`
- 优先以 **2026-10-10 在线指南** 为准，旧 Stock.txt 作废
- `namechange`：DataHub 返回 unknown api → 用 PCD relay 或暂缓 ST 名变更

## 双源策略

- **DataHub**（经 Clash）：优先 `daily` / `daily_basic` / `fina*` / `dividend` / `index_member_all`
- **PCD promax**：备用与 `namechange` / 部分 SW `index_member`；IP 约 200 次/分钟

## 独立复测更正（2026-10-10）
见 `DATAHUB_PROBLEM_RECHECK.md`：`stk_factor_pro` 在带 `ts_code` 时可返回数据，不宜一律「别碰」；`pro_bar`/8行业特色/`margin_detail` P0 已确认。
