# 中转只读探针回执（2026-10-25）

- 依据：主 Agent 00:22 裁定（P1-1）：今晚只做中转只读探针；不签补跑/nightly 运行 .ok；无信号
- 时刻：2026-10-25 00:24:29 EDT
- 脚本：`/tmp/relay_probe/probe5_small.py` sha256 `601a092fef871e917098cddddeb7c65c17627b804d7e4c2f35f413ef1b5bd77f`（与 10-18 12:50 钉值一致）
- 方式：各 API 只跑一次、不重试；stdin=/dev/null；nice -n 10；不写行情数据文件；不导入项目代码；密钥未打印
- RESEARCH_QUIET.lock：不存在

## 结果

| # | API | 原始输出摘要 | 判定 |
|---|---|---|---|
| 1 | trade_cal | `2026-10-25 00:23:55 trade_cal 15.51   ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15) child_pid=605544 rc=0` | **不通**（ReadTimeout read=15s） |
| 2 | stock_basic | `2026-10-25 00:24:09 stock_basic 14.02 200 100  child_pid=605871 rc=0 big_page_full=False` | **通**（HTTP 200、rows=100、error 空；big_page_full=False 预期 exit 2） |

原始输出：
```
2026-10-25 00:23:55 trade_cal 15.51   ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15) child_pid=605544 rc=0
2026-10-25 00:24:09 stock_basic 14.02 200 100  child_pid=605871 rc=0 big_page_full=False
RESULT stock_basic big_page_full=False
```

## 结论

**部分通（阻断补跑前置）**。trade_cal ReadTimeout(15s)；stock_basic HTTP200 rows=100 error空。大页未测。补跑申请前须 trade_cal 再通或主裁接受 degraded。

补拉目标交易日仍为 **20261019–20261023**（主裁）。流式 v1.1 保持冻结 `4a46df7f`。daily_basic 增量 v3.1 继续写。live=false。
