# Arch 重钉：probe5_small 超时加固（2026-10-25）

- 时刻：2026-10-25T05:02:32-04:00（America/New_York）
- 结论：**ACCEPT / 已重钉**
- 主裁：维持 CONSUME_SUSPEND；拒「仅 trade_cal」解冻；moneyflow run.ok 已另签（`68c04741…`）
- live=false

## 变更

| 项 | 旧 | 新 |
|---|---|---|
| 脚本 sha | `1c3999c7…` | `8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554` |
| .ok | `ARCH_RUN_AUTH_PROBE5_SMALL_REPIN_20261025.ok`（`1f0d7f30…`）SUPERSEDED | `ARCH_RUN_AUTH_PROBE5_SMALL_HARDEN_REPIN_20261025.ok` sha `8d5f25765977b4cccf3934c5c661f3a2a9acc207058bc1528fa0217e9c2abab6` |
| 超时实现 | `timeout=(15,115)` 元组 | `urllib3.util.Timeout(connect=15, read=115)` + 行内 `timeouts=15/115/120` |

Eng 慢服务自测：实际 wait≈25s >15 → 旧源码 read 本就不是 15；0455 日志数字属异常/误报。加固便于以后核对。

## Data 下一步

用**仓库路径**复测（父行须含 `timeouts=15/115/120`）：

```bash
install -m 755 docs/v2/audit/relay_probe_20261025/probe5_small.py /tmp/relay_probe/probe5_small.py
nice -n 10 timeout 130 python3 /tmp/relay_probe/probe5_small.py --only trade_cal </dev/null
nice -n 10 timeout 130 python3 /tmp/relay_probe/probe5_small.py --only stock_basic </dev/null
```

两通后再申请解除 CONSUME_SUSPEND。旁证仍：`output/data/ARCH_BACKFILL_1019_1023_CONSUME_SUSPEND_20261025.txt`。
