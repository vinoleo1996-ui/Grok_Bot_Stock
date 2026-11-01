# 中转探针回执（Data · 10:50 例程 / 叶25窗后）

- 时刻：2026-10-25 10:56:17 ET（America/New_York）
- 例程：中转探针 10:50（叶25窗后）；主裁 00:25 只读通断；live=false；无信号；不写生产
- 窗闸：10:00–10:45 已过才开跑（本轮满足）
- 脚本路径：`/tmp/relay_probe/probe5_small.py`（与仓库 `docs/v2/audit/relay_probe_20261025/probe5_small.py` 同字节）
- 脚本 sha256 全长：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`
- 钉：`PROBE5_SMALL_PIN.txt` sha `8fe0090f…` **MATCH**（TIMEOUT_HARDEN_ACCEPTED；例程旧文 601a092f… 已 supersede）
- 方式：各 API 只跑一次、不重试；nice -n 10；stdin=/dev/null；不写生产；不签补跑 .ok
- 前置：最新回执 08:39 `RELAY_PROBE_RECEIPT_20261025T0839ET.md` 为 RELAY_DOWN → 本轮执行探测（不跳过）

## 结果

| API | 父行摘要 | HTTP200 | ReadTimeout |
|---|---|---|---|
| trade_cal | `2026-10-25 10:56:09 trade_cal 15.09   ReadTimeout: … (read timeout=15) timeouts=15/115/120 child_pid=591301 rc=0` | **否** | **是**（表象 read=15；父行已钉 15/115/120） |
| stock_basic | `2026-10-25 10:56:17 stock_basic 7.79 200 100  timeouts=15/115/120 child_pid=591370 rc=0 big_page_full=False` | **是** | 否 |

## 判定

- trade_cal：**不通**（须 HTTP 200 且无 ReadTimeout；本轮 ReadTimeout，主已裁定不接受 degraded）
- stock_basic：小页通（HTTP 200、rows=100；big_page_full=False 属预期 exit 2）
- 总评：**RELAY_DOWN**（补跑前置以 trade_cal 为准）
- **不申请** 补跑 .ok（目标 20261019–20261023）
- SUSPEND 维持；不消费既有补跑包
- 一次性例程本轮后删除

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_1050.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-25 10:56:09,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",15.09,,,"ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15)"
2026-10-25 10:56:17,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",7.79,200,100,
```
