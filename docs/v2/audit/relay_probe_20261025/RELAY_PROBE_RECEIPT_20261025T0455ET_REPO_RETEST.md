# 中转只读探针回执（仓库路径复测 · Arch 重钉后）

- 时刻：2026-10-25 04:55:15 ET（America/New_York）
- 依据：主/Arch — 中转恢复后用**仓库路径**复测；重钉 .ok sha8 `1f0d7f30`
- 脚本：`docs/v2/audit/relay_probe_20261025/probe5_small.py` sha256 `1c3999c7b73bcb7c74b9efdfcc568366e148cbac44e1299b11c2e5e06e59ad21`（与钉 MATCH）
- 同步：`/tmp/relay_probe/probe5_small.py` 同字节
- 方式：各一次、不重试；nice -n 10；timeout 130；stdin=/dev/null；密钥未打印；不写生产
- RESEARCH_QUIET.lock：不存在

## 结果

| # | API | 原始输出 | 判定 |
|---|---|---|---|
| 1 | trade_cal | `2026-10-25 04:53:54 trade_cal 4.95 200 7  child_pid=201324 rc=0` | **通**（HTTP 200、rows=7、无 Timeout/SSL） |
| 2 | stock_basic | `2026-10-25 04:54:09 stock_basic 15.07   ReadTimeout: HTTPSConnectionPool(host='pcd.mobcvb.cn', port=443): Read timed out. (read timeout=15) child_pid=201512 rc=0 big_page_full=False
RESULT stock_basic big_page_full=False` | **不通**（ReadTimeout **read timeout=15** — 与钉口径 read=115 **不符**；疑脚本/子进程超时传参缺陷） |

## 结论

- **trade_cal：PASS**（补跑前置主探针已满足主令「trade_cal 只读」口径）。
- **stock_basic：FAIL**；且暴露 **read=15** 异常（0448/0024 同源嫌疑）。**请 Arch 裁定**：是否在修脚本并重钉前，仅凭 trade_cal PASS 解除 `CONSUME_SUSPEND`；Data **不**自行消费补跑 .ok。
- CSV：`docs/v2/audit/relay_probe_20261025/probe_log_repo_retest.csv`
- live=false；禁写生产；禁 nightly 硬跑历史日。

