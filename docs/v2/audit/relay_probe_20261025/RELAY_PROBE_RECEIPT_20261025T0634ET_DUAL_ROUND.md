# 连续两轮双 API 复测回执（Data · 06:30 窗）

- 时刻：2026-10-25 06:34:24 ET（America/New_York）
- 依据：主裁 05:04 / 05:16 — 解冻须**连续两轮** trade_cal∧stock_basic 均 HTTP 200；Eng 深挖无杠杆（d25e76ee）；≈06:30 自跑
- 脚本 sha256：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`（钉 `8fe0090f…` MATCH）
- Arch .ok：`ARCH_RUN_AUTH_PROBE5_SMALL_HARDEN_REPIN_20261025.ok` sha `8d5f25765977b4cccf3934c5c661f3a2a9acc207058bc1528fa0217e9c2abab6`（`8d5f2576…`）
- hosts：`pcd.mobcvb.cn` → `118.195.242.181`
- 方式：仓库路径；每轮各 API 一次；nice -n 10；timeout 130；stdin=/dev/null；不写生产；live=false

## 结果

| 轮 | API | 父行摘要 | HTTP200 |
|---|---|---|---|
| 1 | trade_cal | `2026-10-25 06:31:17 trade_cal 8.02   SSLError: … SSLEOFError … timeouts=15/115/120 child_pid=344198 rc=0` | **否** |
| 1 | stock_basic | `2026-10-25 06:31:44 stock_basic 15.08   ReadTimeout: … (read timeout=15) timeouts=15/115/120 child_pid=344641 rc=0 big_page_full=False` | **否** |
| 2 | trade_cal | `2026-10-25 06:33:57 trade_cal 7.26 200 7  timeouts=15/115/120 child_pid=347571 rc=0` | ✅ |
| 2 | stock_basic | `2026-10-25 06:34:07 stock_basic 10.33 200 100  timeouts=15/115/120 child_pid=347770 rc=0 big_page_full=False` | ✅ |

- R1 结束≈`2026-10-25 06:31:44` ET → R2 开始≈`2026-10-25 06:33:49` ET（间隔≥2min）
- R1 双通：**否**；R2 双通：**是**
- 连续两轮双通：**否**（仅第二轮双通，不满足解冻）

## 总评：**DUAL_STABLE_FAIL**

中转仍间歇（R1 双败 / R2 双通）。**维持 SUSPEND**；不消费 `9e4359f9`。旁证 `ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt` 条件未满足。下一探测窗：例程 08:30 / 10:50，或 Eng 通路改动后立刻重测。

## CSV

`docs/v2/audit/relay_probe_20261025/probe_log_dual_0630.csv`

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-25 06:31:17,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",8.02,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/trade_cal?exchange=SSE&start_date=20261019&end_date=20261025 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
2026-10-25 06:31:44,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",15.08,,,"ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15)"
2026-10-25 06:33:57,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",7.26,200,7,
2026-10-25 06:34:07,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",10.33,200,100,
```
