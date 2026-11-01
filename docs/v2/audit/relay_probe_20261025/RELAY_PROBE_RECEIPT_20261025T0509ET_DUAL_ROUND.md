# 连续两轮双 API 复测回执（Data）

- 时刻：2026-10-25 05:09:41 ET（America/New_York）
- 依据：主裁 05:04 — 解冻须连续两轮（间隔≥2min）trade_cal∧stock_basic 均 HTTP 200
- 脚本 sha256：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`（钉 `8fe0090f…` MATCH）
- Arch .ok：`ARCH_RUN_AUTH_PROBE5_SMALL_HARDEN_REPIN_20261025.ok` sha `8d5f25765977b4cccf3934c5c661f3a2a9acc207058bc1528fa0217e9c2abab6`（`8d5f2576…`）
- hosts：`pcd.mobcvb.cn` → `118.195.242.181`
- 方式：仓库路径；每轮各 API 一次；nice -n 10；timeout 130；stdin=/dev/null；不写生产；live=false

## 结果

| 轮 | API | 父行摘要 | HTTP200 |
|---|---|---|---|
| 1 | trade_cal | `2026-10-25 05:06:23 trade_cal 8.04 200 7  timeouts=15/115/120 child_pid=225006 rc=0` | ✅ |
| 1 | stock_basic | `2026-10-25 05:06:31 stock_basic 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=10` | **否** |
| 2 | trade_cal | `2026-10-25 05:09:33 trade_cal 3.86 200 7  timeouts=15/115/120 child_pid=229996 rc=0` | ✅ |
| 2 | stock_basic | `2026-10-25 05:09:41 stock_basic 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=10` | **否** |

- R1 结束≈`2026-10-25 05:06:31` ET → R2 开始≈`2026-10-25 05:09:33` ET（间隔≥2min）
- R1 双通：**否**；R2 双通：**否**

## 总评：**DUAL_STABLE_FAIL**

中转仍间歇；**维持 SUSPEND**；不消费 `9e4359f9`。Eng 侧亦复现间歇（笔记已知）。

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_dual_round.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-25 05:06:23,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",8.04,200,7,
2026-10-25 05:06:31,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",8.02,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=100&offset=0 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
2026-10-25 05:09:33,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",3.86,200,7,
2026-10-25 05:09:41,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",8.02,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=100&offset=0 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
```
