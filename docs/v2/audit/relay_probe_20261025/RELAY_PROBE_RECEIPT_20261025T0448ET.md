# 中转只读探针回执（2026-10-25 启用后）

- 依据：主 Agent 04:37–04:44 编排（enable DONE 后立刻 trade_cal）；Arch 催补跑前置证据；Eng 确认无原钉副本
- 时刻：2026-10-25 04:48:07 ET（America/New_York）
- 脚本：`/tmp/relay_probe/probe5_small.py`
  - 实际 sha256 `1c3999c7b73bcb7c74b9efdfcc568366e148cbac44e1299b11c2e5e06e59ad21`
  - 原钉 sha256 `601a092fef871e917098cddddeb7c65c17627b804d7e4c2f35f413ef1b5bd77f` → **PIN_MISMATCH / REBUILT**（盒刷丢失；Eng 全盘无副本；Mac offline）
  - 口径：connect 15s / read 115s / wall 120s；stock_basic limit=100；BIG_PAGE=5000 保留
- 方式：各 API 只跑一次、不重试；stdin=/dev/null；nice -n 10；timeout 130；密钥自 `.env.datasources` 加载且未打印；不写生产 parquet；不导入项目代码
- RESEARCH_QUIET.lock：不存在
- enable .ok：`4377eb59…` 已由 Eng 消费；本探针不授权补跑

## 结果

| # | API | 原始输出摘要 | 判定 |
|---|---|---|---|
| 1 | trade_cal | `2026-10-25 04:46:29 trade_cal 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/trade_cal?exchange=SSE&start_date=20261019&end_date=20261025 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)'))) child_pid=184834 rc=0` | **不通**（SSLError / UNEXPECTED_EOF；无 HTTP 200、无 rows） |
| 2 | stock_basic | `2026-10-25 04:47:36 stock_basic 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=100&offset=0 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)'))) child_pid=187271 rc=0 big_page_full=False
RESULT stock_basic big_page_full=False` | **不通**（同上 SSLError；非 HTTP 200） |

原始输出：
```
2026-10-25 04:46:29 trade_cal 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/trade_cal?exchange=SSE&start_date=20261019&end_date=20261025 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)'))) child_pid=184834 rc=0
2026-10-25 04:47:36 stock_basic 8.02   SSLError: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Max retries exceeded with url: /tushare/pro/stock_basic?list_status=L&limit=100&offset=0 (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1029)'))) child_pid=187271 rc=0 big_page_full=False
RESULT stock_basic big_page_full=False
```

CSV：`docs/v2/audit/relay_probe_20261025/probe_log.csv`

## 结论

**不通（阻断补跑前置）**。trade_cal 与 stock_basic 均在 ~8s 内 SSL EOF，未取得 HTTP 200。  
→ **不可据此签/跑 1019–23 五日补跑**。请 Arch **暂缓**补跑 .ok；等中转恢复后由 08:30/10:50 例程或主令再探针。  
→ 请 Arch **重钉**重建脚本 sha `1c3999c7…`（全长见上）供后续探针承认。

补拉目标交易日仍为 **20261019–20261023**（主裁 A：专用执行器包，非 nightly 豁免）。live=false。勿与叶25/enable 混签。
