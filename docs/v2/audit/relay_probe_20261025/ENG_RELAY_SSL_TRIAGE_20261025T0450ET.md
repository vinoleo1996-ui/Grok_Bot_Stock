# Eng 中转 SSL 只读排查（2026-10-25）

- 时刻：2026-10-25T04:51:51-04:00
- 依据：主 04:48 令（探针不通后协同查中转/SSL；禁实跑）
- 范围：DNS/TCP/TLS/HTTP 路径探测；**未**读生产 parquet；**未**打印密钥；**未**写 data/

## 现象（与 Data 探针一致）

- Data 回执 `5d208af6…`：trade_cal / stock_basic ~8s **SSL EOF**
- Eng 复现：`openssl s_client` → `unexpected eof while reading`；Cipher=(NONE)
- `curl` 对 `/tushare/pro/trade_cal`：**间歇** SSL EOF / connect timeout / 偶发 **HTTP 401**（无 token 时 401 说明握手偶发成功）

## DNS

| 源 | 结果 |
|---|---|
| getent | `pcd.mobcvb.cn` → **198.18.0.1** |
| 本机路由 | default via 172.30.0.1；**无** tun/clash/mihomo 接口；**无** HTTP(S)_PROXY 环境变量 |
| 说明 | 198.18.0.0/15 常见于 fake-ip；若无本地代理接管，易表现为断流/EOF |

## 本地缓存

- `output/relay_health.json`：`up=false`；`checked_at=2026-10-18T04:59:22-0400`（**陈旧**，非今日）
- `relay_health.py` sha `6d3ea9f5…` MATCH 驱动钉

## 结论（Eng）

1. **中转链路不稳定 / 多数握手失败**（SSL EOF），与「补跑前置不通」一致。
2. Eng **无法在本侧单独修好上游 TLS**；疑点优先：DNS→198.18.0.1（无本地代理）或上游/出口间歇重置。
3. **禁止实跑**直至 Data 复测探针通。补跑执行器包继续落盘供 Arch 审。

## 建议下一步（非 Eng 单方）

- Data：确认中转应解析的真实 IP / 是否必须经本机代理；必要时换解析或恢复代理后复探针。
- 主：维持 9e4359f9 **暂缓消费**。
- Arch：probe5_small 重钉 `1c3999c7…` 已知；等 runner 包。

live=false。
