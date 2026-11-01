# 中转探针回执（Data · 08:30 双通第一轮）

- 时刻：2026-10-27 08:39:25 ET（America/New_York）
- 例程：中转双通 10-27 08:30；主裁令文 `docs/v2/audit/MAIN_DATA_DUALPASS_NEXT_WINDOW_20261025_ZH.md`；live=false；无信号；不写生产
- 脚本路径：`/tmp/relay_probe/probe5_small.py`（与仓库 `docs/v2/audit/relay_probe_20261025/probe5_small.py` 同字节）
- 脚本 sha256 全长：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`
- 钉：`PROBE5_SMALL_PIN.txt` sha `8fe0090f…` **MATCH**（TIMEOUT_HARDEN_ACCEPTED；与 PIN/`8d5f2576` 一致）
- 方式：各 API 只跑一次、不重试；nice -n 10；timeout 130；stdin=/dev/null；connect15/read115/wall120；stock_basic limit=100；不写生产；不签/不消费补跑 .ok（含 `9e4359f9`）
- hosts：`pcd.mobcvb.cn` → `118.195.242.181`

## 结果

| API | 父行摘要 | HTTP200 | ReadTimeout |
|---|---|---|---|
| trade_cal | `2026-10-27 08:37:20 trade_cal 7.39 200 7  timeouts=15/115/120 child_pid=82761 rc=0` | **是** | 否 |
| stock_basic | `2026-10-27 08:39:20 stock_basic 119.13   ReadTimeout: … (read timeout=115) timeouts=15/115/120 child_pid=83634 rc=0 big_page_full=False` | **否** | **是**（read=115） |

## 判定

- trade_cal：**通**（HTTP 200、rows=7）
- stock_basic：**不通**（须 HTTP 200 且无 ReadTimeout；本轮 ReadTimeout；不接受 degraded）
- 总评：**RELAY_DOWN**（双通第一轮未齐；补跑前置以两 API 均通为准）
- **不申请** 补跑 .ok；**不消费** `9e4359f9`
- SUSPEND 维持至两轮皆通
- 一次性例程本轮后删除；10:50 第二轮例程仍在

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_0830_20261027.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-27 08:37:20,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",7.39,200,7,
2026-10-27 08:39:20,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",119.13,,,"ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=115)"
```
