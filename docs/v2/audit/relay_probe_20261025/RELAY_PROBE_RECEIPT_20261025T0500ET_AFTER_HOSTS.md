# 中转只读探针回执（hosts 钉真实 IP 后）

- 时刻：2026-10-25 05:00:05 ET
- 脚本：`docs/v2/audit/relay_probe_20261025/probe5_small.py` sha `1c3999c7…`；重钉 .ok `1f0d7f30`
- 解析：`pcd.mobcvb.cn` → `118.195.242.181`（`/etc/hosts`，Eng 修复）
- 方式：各一次；nice -n 10；不写生产

| API | 输出摘要 | 判定 |
|---|---|---|
| trade_cal | `2026-10-25 04:59:01 trade_cal 6.86 200 7  child_pid=210242 rc=0` | **通** |
| stock_basic | `2026-10-25 04:59:22 stock_basic 15.05 ReadTimeout (read timeout=15) big_page_full=False` | **不通** |

结论：**trade_cal PASS**；stock_basic 仍 FAIL。补跑消费仍待主/Arch 裁。详 `DATA_RELAY_DNS_PROXY_CONFIRM_20261025T0500ET.md`。live=false。
