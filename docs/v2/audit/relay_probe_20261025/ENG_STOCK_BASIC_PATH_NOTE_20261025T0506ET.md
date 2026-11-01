# Eng：stock_basic 通路追踪（加固重钉后）

- 时刻：2026-10-25T05:07:16-04:00
- 依据：主「继续盯 stock_basic」；Arch 重钉 `8fe0090f…` / `.ok` `8d5f2576…`
- live=false；禁实跑；补跑 SUSPEND

## 钉与脚本

| 项 | 值 |
|---|---|
| script | `8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554` |
| .ok | `8d5f25765977b4cccf3934c5c661f3a2a9acc207058bc1528fa0217e9c2abab6` |
| hosts | `118.195.242.181 pcd.mobcvb.cn` MATCH |
| 父行 | 必含 `timeouts=15/115/120` |

## 观测（同钉、同机）

| 时刻/来源 | API | 结果 |
|---|---|---|
| Eng 05:04 仓库探针 | stock_basic | ReadTimeout **(read timeout=15)** @15.07s；行内仍 `timeouts=15/115/120` |
| Data 复测（报 `2e4637f5…`） | stock_basic | **200 / 100 行**；trade_cal 仍抖 |
| Eng 05:05 直连诊断 | stock_basic×4 | `Timeout(c=15,r=115)`→**200** 9.7s；tuple→**200** 5.1s；再一次同 Timeout→ReadTimeout@15；float115→RemoteDisconnected@63s |

## 结论

1. **不是**脚本常量写错：行内钉 `15/115/120` 已打出；`/tmp` 慢服务曾等满 25s。
2. **中转间歇**：stock_basic / trade_cal 均可在数秒内 200，也可在 ~15s 以 `read timeout=15` 失败或 SSL/断连——与「仅修超时数字」无关。
3. 错误串里的 `read timeout=15` 与成功时 `read=115` 配置并存 → 疑为链路重置/半开连接下 urllib3 报数字异常或握手阶段命中 connect=15；**不能**再当成「传参缺陷」单点修。
4. **维持 SUSPEND**；解冻条件仍须主/Arch 裁（双 API 稳定 PASS 或主改口径）。

## Eng 状态

- 补跑包已交齐（Data PIN_ALIGN_PASS）；Arch 预读中；**不开跑**
- 继续只读盯链路；不改驱动；不消费 9e4359f9
