# 中转探针回执（Data · 08:30 例程）

- 时刻：2026-10-25 08:39:05 ET（America/New_York）
- 例程：中转探针 08:30（10-25）；主裁 00:25 只读通断；live=false
- 脚本路径：`/tmp/relay_probe/probe5_small.py`（与仓库 `docs/v2/audit/relay_probe_20261025/probe5_small.py` 同字节）
- 脚本 sha256 全长：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`
- 钉：`PROBE5_SMALL_PIN.txt` sha `8fe0090f…` **MATCH**（TIMEOUT_HARDEN_ACCEPTED；原例程文案 601a092f… 为 lost pin，已由 Eng 加固钉 supersede）
- 方式：各 API 只跑一次、不重试；nice -n 10；stdin=/dev/null；不写生产；不签补跑 .ok
- hosts：`pcd.mobcvb.cn`（既有）

## 结果

| API | 父行摘要 | HTTP200 | ReadTimeout |
|---|---|---|---|
| trade_cal | `2026-10-25 08:39:01 trade_cal 8.03   SSLError: … SSLEOFError … timeouts=15/115/120 child_pid=466894 rc=0` | **否** | 否（SSL EOF） |
| stock_basic | `2026-10-25 08:39:05 stock_basic 4.22   SSLError: … SSLEOFError … timeouts=15/115/120 child_pid=467055 rc=0 big_page_full=False` | **否** | 否（SSL EOF） |

## 判定

- trade_cal：**不通**（须 HTTP 200 且无 ReadTimeout；本轮 SSLError/SSLEOFError，主已裁定不接受 degraded）
- 总评：**RELAY_DOWN**
- **不申请** 补跑 .ok（目标 20261019–20261023）；今晚仍不申请；等 10:50 例程再探
- SUSPEND 维持；不消费既有补跑包

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_0830.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-25 08:39:01,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",8.03,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/trade_cal?exchange=SSE&start_date=20261019&end_date=20261025 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
2026-10-25 08:39:05,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",4.22,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=100&offset=0 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
```
