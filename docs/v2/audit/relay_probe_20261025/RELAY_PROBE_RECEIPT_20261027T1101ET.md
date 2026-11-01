# 中转探针回执（Data · 10:50 双通第二轮）

- 时刻：2026-10-27 11:01:20 ET（America/New_York）
- 例程：中转双通 10-27 10:50；主裁令文 `docs/v2/audit/MAIN_DATA_DUALPASS_NEXT_WINDOW_20261025_ZH.md`；live=false；无信号；不写生产
- 脚本路径：`/tmp/relay_probe/probe5_small.py`（与仓库 `docs/v2/audit/relay_probe_20261025/probe5_small.py` 同字节）
- 脚本 sha256 全长：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`
- 钉：`PROBE5_SMALL_PIN.txt` sha `8fe0090f…` **MATCH**（TIMEOUT_HARDEN_ACCEPTED；与 PIN/`8d5f2576` 一致）
- 方式：各 API 只跑一次、不重试；nice -n 10；timeout 130；stdin=/dev/null；connect15/read115/wall120；stock_basic limit=100；不写生产；不签/不消费补跑 .ok（含 `9e4359f9`）；不改探针源码
- hosts：`pcd.mobcvb.cn` → `118.195.242.181`
- 对照：当日 08:30 回执 `RELAY_PROBE_RECEIPT_20261027T0839ET.md` sha8 **`f2623f42`**（RELAY_DOWN）

## 结果

| API | 父行摘要 | HTTP200 | ReadTimeout |
|---|---|---|---|
| trade_cal | `2026-10-27 11:01:05 trade_cal 7.72 200 7  timeouts=15/115/120 child_pid=287463 rc=0` | **是** | 否 |
| stock_basic | `2026-10-27 11:01:20 stock_basic 15.07   ReadTimeout: … (read timeout=15) timeouts=15/115/120 child_pid=287499 rc=0 big_page_full=False` | **否** | **是**（error 文案 read=15；父行钉 timeouts=15/115/120；本拍不改源码） |

## 判定

- trade_cal：**通**（HTTP 200、rows=7）
- stock_basic：**不通**（须 HTTP 200 且无 ReadTimeout；本轮 ReadTimeout；不接受 degraded）
- 本轮总评：**RELAY_DOWN**
- 对照 08:30：亦为 **RELAY_DOWN**（trade_cal 通 / stock_basic ReadTimeout）
- **双通总评：DUAL_STABLE_FAIL / RELAY_DOWN**（两轮均未双 API PASS；不可解冻）
- **不申请** 补跑 .ok；**不消费** `9e4359f9`
- SUSPEND 维持至两轮皆通
- 一次性例程本轮后删除

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_1050_20261027.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-27 11:01:05,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",7.72,200,7,
2026-10-27 11:01:20,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",15.07,,,"ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15)"
```
