# relay（pcd.mobcvb.cn）配额/限频证据整理（给 Eng 盘中 rt_min/stk_mins）
2026-10-14 06:56 ET，Data。中转当前 TLS 不通，**未实测**，只查本地配置/文档/日志。

## 已知
| 事项 | 证据 |
|---|---|
| rt_k / rt_min / stk_mins / pro_bar(1min) 在 relay 有权限，单票单日各 1 次成功，耗时 1.7–4.8s | `docs/v2/DATA_REALTIME_MIN_PERM_PROBE_ZH.md` |
| datahub 这四个接口 403 api_scope_denied（15000 分档外），不能做备用 | 同上 |
| realtime_quote 在 relay 未登记（404） | 同上 |
| 客户端遇 HTTP 429 会按 Retry-After（默认 5s）等待重试 | `quantlab/data_sources/tushare_proxy.py` `_get` |
| relay 默认超时 180s（全日分页曾在 90s 超时） | 同上 `TSPRO_RELAY_TIMEOUT` |
| 项目逐票请求间隔 0.3s（经验值，"避免被封"） | `quantlab/config.py:70 rate_limiter_sec` |
| datahub 并发 4 时偶发 429 | `docs/v2/CB_ETF_DATA_STATUS.md:13`（datahub，不是 relay） |
| relay 历史故障全部是连接类（Max retries / TLS），**日志里没有找到任何 relay 限频报错**（无 429、无“每分钟最多访问”类文字） | `logs/*.log` 全文检索 |

## 未知（需中转恢复后、经批准再小样本测）
- relay 每分钟/每日调用上限、rt_min/stk_mins 单次最大行数和是否单独计次。
- relay 背后账号的积分档（文档称 "promax"，未见具体额度）。
- 并发上限，以及多 agent 共用同一 TSPRO_PROXY_KEY 时是否共享配额。
- Tushare 官方对 stk_mins 的公开限制（官方分钟权限通常单独开通、按分钟计次）不能直接套到中转上。
## 建议
盘中先按保守值设计：单线程、≥0.3s 间隔、遇 429 退避；中转恢复后由 Eng 申请一次 5 分钟小样本压测确认上限。
