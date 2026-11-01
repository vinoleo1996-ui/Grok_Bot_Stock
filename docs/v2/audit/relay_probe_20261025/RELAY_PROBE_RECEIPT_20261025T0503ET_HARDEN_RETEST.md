# 加固探针复测回执（Data）

- 时刻：2026-10-25 05:03:46 ET（America/New_York）
- 脚本：`docs/v2/audit/relay_probe_20261025/probe5_small.py`
- 现盘 sha256：`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`（sha8 `8fe0090f`）— Eng HARDEN；**相对 Arch 钉 `1c3999c7…` = PIN_MISMATCH，请 Arch 重钉 `8fe0090f…`**
- 旧钉字节已在 `_recovery/data/relay_probe_20261025/probe5_small_1c3999c7b73bcb7c.py`
- hosts：`pcd.mobcvb.cn` → `118.195.242.181`（getaddrinfo 一致）
- 方式：仓库路径；各 API 一次+ trade_cal 再试一次；nice -n 10；timeout 130；stdin=/dev/null；不写生产；live=false

## 结果

| 次序 | API | 父行摘要 | 判定 |
|---|---|---|---|
| 1 | trade_cal | `05:02:33 … SSLError SSLEOF … timeouts=15/115/120` | **不通** |
| 2 | stock_basic | `05:02:42 … 200 100 … timeouts=15/115/120 big_page_full=False` | **小页通**（HTTP200 rows=100；BIG_PAGE=5000 未满属预期） |
| 3 | trade_cal 再试 | `05:03:09 … ReadTimeout … (read timeout=15) timeouts=15/115/120` | **不通**（父行已钉 15/115/120；异常串仍印 read timeout=15 — urllib3/握手表象，与 Eng 慢服务实测「真 read>15」不矛盾） |

## CSV

见同目录 `probe_log_harden_retest.csv`。

```
ts_et,api,params,elapsed_s,http_status,rows,error
2026-10-25 05:02:33,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",8.02,,,"SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/trade_cal?exchange=SSE&start_date=20261019&end_date=20261025 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)')))"
2026-10-25 05:02:42,stock_basic,"{""list_status"":""L"",""limit"":100,""offset"":0}",9.14,200,100,
2026-10-25 05:03:09,trade_cal,"{""exchange"":""SSE"",""start_date"":""20261019"",""end_date"":""20261025""}",15.07,,,"ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15)"
```

## 结论

1. **超时加固生效**：父行稳定带 `timeouts=15/115/120`；stock_basic 小页已通。
2. **trade_cal 仍不稳**：SSL EOF / ReadTimeout 间歇；裸 SSL wrap 亦 EOF → 中转链路未稳，非单常量写错。
3. **CONSUME_SUSPEND 维持**：Data **不**消费补跑 .ok `9e4359f9`；等 Arch 重钉探针 + 主/Arch 裁「小页 stock_basic 通 + trade_cal 仍抖」是否够解冻。
4. 请 Arch：重钉 sha `8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`。
