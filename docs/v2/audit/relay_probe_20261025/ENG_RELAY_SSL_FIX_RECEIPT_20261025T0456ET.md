# Eng 中转 SSL 排查与修复回执

- 时刻：2026-10-25T04:56:46-04:00（America/New_York）
- 依据：主 04:48/04:52 令（主动查 `pcd.mobcvb.cn:443` SSL EOF；修好是复测前置）
- 旁证：`ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND`（9e4359f9 暂缓消费）
- live=false；**未**写生产 data/；**未**消费补跑 .ok

## 根因

| 项 | 值 |
|---|---|
| 本机解析（修复前） | `pcd.mobcvb.cn` → **198.18.0.1**（resolver `10.0.0.2`，fake-ip 段） |
| 公共 DNS（dns.google） | → **118.195.242.181** |
| 本机代理 | `DATAHUB_HTTP_PROXY`→`100.102.49.98:7897` **TCP 不通**；无 HTTP(S)_PROXY 环境变量；无 tun |
| 直连真实 IP + SNI | `openssl`：**TLSv1.3** `TLS_AES_128_GCM_SHA256`；证书 CN=`pcd.mobcvb.cn`（Let's Encrypt YE2）；Verify **ok** |
| 假 IP 路径 | 多数 **SSL EOF / 超时**（与 Data 探针 `5d208af6…` 一致） |

结论：**不是证书坏，是本机把中转解析到未接管的 fake-ip**，握手被重置/黑洞。

## 已做修复（盒机）

1. 备份：`/etc/hosts.bak_eng_relay_20261025T0454ET`
2. 写入：`118.195.242.181 pcd.mobcvb.cn`
3. 现盘 `getent hosts pcd.mobcvb.cn` → `118.195.242.181`

## 修复后复测（Eng，带密钥不落盘）

| API | 超时 | 结果 |
|---|---|---|
| trade_cal（无 key） | urllib ~12s | HTTP **401**（链路通） |
| trade_cal（有 key） | connect15 / read30 | HTTP **200**，`code=0`，约 **11.3s**，含 1019–25 日历字段 |
| trade_cal（read8） | 8s | ReadTimeout（上游偏慢，短读不够） |
| stock_basic limit=100 | connect15 / read30 | **仍超时**（~44s）— 大页仍不稳 |

## 给 Data 的复测建议

- 脚本：仓库路径 `docs/v2/audit/relay_probe_20261025/probe5_small.py`（sha `1c3999c7…`，Arch 重钉 .ok `1f0d7f30…`）
- 确认本机已解析到 `118.195.242.181` 后再跑
- trade_cal 读超时须 **≥15–30s**（探针原 read115 足够）
- stock_basic 若仍超时：记部分通，由主裁是否接受「仅 trade_cal 通」作补跑前置

## 未改 / 不做

- 不改 `tushare_proxy.py` / 驱动；不消费 `9e4359f9…`；不实跑补跑
- 不依赖已死的 `100.102.49.98:7897` 代理访问中转
- `/etc/hosts` 为盒机持久钉；若将来本机代理/fake-ip 恢复，需协调是否撤回

## 状态

- SSL/解析：**已按真实 IP 钉 hosts；trade_cal 已 200**
- 补跑实跑：**仍冻结**至 Data 正式探针 PASS + Arch 审 runner
- 执行器包：继续准备 `docs/v2/audit/backfill_1019_1023/`

请主+Data 收；Data 请立刻复测探针。
