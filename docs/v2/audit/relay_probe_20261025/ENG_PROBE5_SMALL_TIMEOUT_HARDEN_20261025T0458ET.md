# Eng：probe5_small 超时传参核查与加固

- 时刻：2026-10-25T05:00:51-04:00
- 依据：主 04:55（stock_basic 日志 read timeout=15；钉应为 115）
- live=false；只改探针脚本；不写生产；不消费补跑 .ok

## 核查（旧钉 `1c3999c7…`）

| 检查 | 结果 |
|---|---|
| 源码常量 | `CONNECT_S=15` `READ_S=115` `WALL_S=120`；`timeout=(CONNECT_S, READ_S)` |
| `/tmp` 慢服务（sleep 25s 后 200） | 子进程 **elapsed≈25.1s 成功** → **实际 read 超时 >15**，源码并非 15 |
| 0455 回执 | `Read timed out. (read timeout=15)` + elapsed 15.07 — **与源码不符**；更像当时链路/栈瞬时表现或误报数字，**不是**常量写成 15 |

## 加固（新字节）

路径：`docs/v2/audit/relay_probe_20261025/probe5_small.py`  
sha256：**`8fe0090fc57c91924fbc9e25e0cf3ef15f4d247360965252d26626e0a2567554`**  
已 sync：`/tmp/relay_probe/probe5_small.py` 同字节。

改动：
1. `urllib3.util.Timeout(connect=15, read=115)` 显式对象（不用裸 int）
2. 子进程 `assert` 三常量 == 15/115/120
3. 每行输出带 `timeouts=15/115/120`；child JSON 带 `timeouts` 字段
4. `/tmp` 慢服务自测：child/parent 均绿，`timeouts=15/115/120` 出现在父行

## 请 Arch / Data

- Arch：旧钉 `1c3999c7…` → 请重钉 **`8fe0090f…`**（全长见上）
- Data：重钉后用**仓库路径**复测 stock_basic；父行须含 `timeouts=15/115/120`
- 补跑消费仍 SUSPEND；Eng 包继续

## 包对接

`docs/v2/audit/backfill_1019_1023/` 骨架已在（runner + Data PIN_SHEET/证据/SCOPE_SUPPLEMENT/DRAFT scope）。对钉继续。
