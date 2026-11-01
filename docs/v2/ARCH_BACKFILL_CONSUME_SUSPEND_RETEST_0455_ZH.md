# 补跑消费暂缓 — 0455 复测裁示

- 时刻：2026-10-25T04:58:18-04:00（America/New_York）
- 回执：`docs/v2/audit/relay_probe_20261025/RELAY_PROBE_RECEIPT_20261025T0455ET_REPO_RETEST.md` sha256 `435714f6964ed8862d70fc22480ba102165f902789bb3755cddab11dc1883221`
- live=false

## 裁示：**不解除** `CONSUME_SUSPEND`

| 证据 | 判定 | 对补跑含义 |
|---|---|---|
| trade_cal HTTP 200 / rows=7 | PASS | 仅确认日历窗口可读；**不足以**放行写生产 |
| stock_basic ReadTimeout（报 read timeout=**15**） | FAIL | 中转仍不稳；源码钉 READ_S=115，报错 15 为异常，须 Data/Eng 查清后再探 |
| 补跑窗口授权 `9e4359f9…` | VALID_BUT_NOT_CONSUMABLE | 不改 .ok 字节；Eng 可继续备专用 runner 包 |

恢复条件：钉脚本 `1c3999c7…` 下 **stock_basic 亦 PASS**（HTTP 200、rows=100、无 Timeout；且错误串不再出现 read timeout=15），再由 Arch 改旁证并审 runner 实跑窗。

Data **勿**消费 `9e4359f9`。旁证已更新：`output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt` sha `6fc8708af9da47c2096ba81233bd0636771d692ca8df306bd27b3748fd877829`。
