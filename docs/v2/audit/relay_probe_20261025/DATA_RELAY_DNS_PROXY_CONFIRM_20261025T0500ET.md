# Data 中转解析/代理确认 + 复测回执

- 时刻：2026-10-25 05:00:05 ET（America/New_York）
- 依据：主 04:52 P0；Eng 排查 `ENG_RELAY_SSL_TRIAGE_20261025T0450ET.md`（sha8 `9c73b965`）与修复 `ENG_RELAY_SSL_FIX_RECEIPT_20261025T0456ET.md`（sha8 `79e1cadc`）
- live=false；未写生产；未消费补跑 .ok

## 1. 真实解析 / 是否要代理

| 项 | 结论 |
|---|---|
| 应解析 IP | **`118.195.242.181`**（公共 DNS；Eng 已钉入 `/etc/hosts`） |
| 错误解析 | `198.18.0.1`（resolver `10.0.0.2` fake-ip，**无本地 Clash/tun 接管**→ SSL EOF） |
| 现盘 getent / python | `118.195.242.181`（hosts 生效；mtime ~04:54 ET） |
| Mac Clash `100.102.49.98:7897` | **不需要**也不通；中转与 datahub 不同——**中转应直连真实 IP** |
| 盒内 `sand-egress-tun` `127.0.0.1:8791` | 非必需；经它 HTTPS 仍可能 EOF，**探针默认直连** |
| HTTP(S)_PROXY | 未设；**不要**为中转强行挂 DATAHUB 代理 |

根因对齐 Eng：**不是证书坏，是 fake-ip 未被代理接管**。hosts 钉真实 IP 后 TLS 可握、trade_cal 可 200。

## 2. 可复测步骤（给主/Eng）

```bash
# 0) 解析须为真实 IP
getent hosts pcd.mobcvb.cn   # 期望 118.195.242.181

# 1) 仓库脚本 = 钉（勿只靠 /tmp）
sha256sum docs/v2/audit/relay_probe_20261025/probe5_small.py
# 期望 1c3999c7b73bcb7c74b9efdfcc568366e148cbac44e1299b11c2e5e06e59ad21

# 2) 只读探针（Arch .ok 1f0d7f30；各一次不重试）
nice -n 10 timeout 130 python3 docs/v2/audit/relay_probe_20261025/probe5_small.py \
  --only trade_cal --env-file .env.datasources \
  --log-path docs/v2/audit/relay_probe_20261025/probe_log.csv </dev/null

nice -n 10 timeout 130 python3 docs/v2/audit/relay_probe_20261025/probe5_small.py \
  --only stock_basic --env-file .env.datasources \
  --log-path docs/v2/audit/relay_probe_20261025/probe_log.csv </dev/null
```

判定：trade_cal **通** = HTTP 200 且 rows>0；stock_basic 小页通 = 200/rows=100（可另裁）。

## 3. Data 复测结果（hosts 修复后）

| 轮 | API | 结果 |
|---|---|---|
| 04:55 仓库复测 | trade_cal | **PASS**（回执 sha8 `435714f6`） |
| 04:55 | stock_basic | FAIL ReadTimeout |
| **04:59**（本轮） | trade_cal | **PASS**（HTTP 200、rows=7、6.86s）`2026-10-25 04:59:01 trade_cal 6.86 200 7  child_pid=210242 rc=0` |
| 04:59 | stock_basic | FAIL ~15s（错误串含 read timeout=15；源码捕获 timeout 元组确为 **(15,115)**——属握手/连接阶段吃 connect=15 的 urllib3 表象，与 10-18 根因同类；Eng 用 read30 亦见 stock_basic 仍慢/超时） |

CSV：`docs/v2/audit/relay_probe_20261025/probe_log_ssl_fix.csv`

## 4. 结论 / 请示

- **解析/代理：已确认**——中转走 **`118.195.242.181` 直连**；勿走死掉的 Mac Clash；hosts 钉由 Eng 已落。
- **trade_cal 正式探针：PASS**（04:55 + 04:59）。
- stock_basic：仍不稳；请主/Arch 裁是否接受「仅 trade_cal 通」解除 `CONSUME_SUSPEND`。
- Data **不**自行消费 `9e4359f9`；等 Eng runner 包 + Arch 审。

live=false。
