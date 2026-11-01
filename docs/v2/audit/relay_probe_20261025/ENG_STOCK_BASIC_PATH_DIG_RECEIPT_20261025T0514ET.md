# Eng：stock_basic 专属通路深挖 → **无杠杆**

- 时刻：2026-10-25T05:15:16-04:00
- 依据：主「再挖 basic 专属通路（limit=10 vs 100、路径/SNI/中转对大响应）」；Data 双测 `3397e869`（trade_cal 连 200 / stock_basic 连 SSL EOF）
- live=false；SUSPEND 不变；禁解冻；禁补跑包实跑

## 钉（未改）

| 项 | 值 |
|---|---|
| probe5_small | `8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554` |
| .ok | `8d5f25765977b4cccf3934c5c661f3a2a9acc207058bc1528fa0217e9c2abab6` |
| hosts | `118.195.242.181 pcd.mobcvb.cn` MATCH |
| stock_basic_limit | 100（未改） |

## 本窗结果（JSON `9e0515a9762c…`）

| 用例 | 结果 |
|---|---|
| requests limit=1 | **200** 22.86s / 1 行 |
| requests limit=10 | **200** 4.32s / 10 行 |
| requests limit=50 | ReadTimeout（串报 read=15）@15.01s |
| requests limit=100 | **SSL EOF** @5.06s |
| requests trade_cal | **SSL EOF** @1.99s（同窗对照也炸） |
| session limit=10 复测 | **SSL EOF** @5.6s（刚 200 再炸） |
| raw HTTP/1.0 L10 | SSL EOF |
| raw HTTP/1.1 L10 | 200 |
| raw HTTP/1.0 L100 | 200 ~19KB |
| raw HTTP/1.1 L100 | SSL EOF |

## 结论：**无杠杆**

1. **非确定性大小门限**：同窗内 limit=10 可 200 也可 SSL；trade_cal（小包）同炸 → 不是「降到 10 就稳」。
2. **非路径/SNI 单点**：hosts 已钉真实 IP；无可用中转代理；HTTP/1.0 vs 1.1 / raw vs requests 成败交叉，无稳定胜出实现可落盘。
3. **不改 probe limit**：把探针改成 limit=10 只会稀释健康信号、且须 Arch 重钉，**修不了**生产级大响应/间歇 TLS。
4. **维持 SUSPEND**；不解冻；不动补跑包实跑。

## 建议下一探测窗

**2026-10-25 06:30 ET**（与 Data 自跑窗对齐；Eng 无改动落盘，Data 按原计划自测即可）。

## 产物

- dig JSON：`docs/v2/audit/relay_probe_20261025/ENG_STOCK_BASIC_PATH_DIG_20261025T0511ET.json` sha256=`9e0515a9762cbb6f6c818135a2cd78d0ecf0fd075cdc352c10b6c33b92b9631b`
