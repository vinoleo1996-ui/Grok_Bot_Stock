# Arch SUPERSEDED：A18 §5.3 引导基线 `.ok`（签窗空档不足）

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻（America/New_York） | `2026-10-26T15:18:59-04:00`（墙钟 2026-10-26 15:18 ET） |
| **状态** | **SUPERSEDED**（single_use 未消费） |
| 旧 live 路径 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.ok`（**已不存在**） |
| 旧 `.ok` sha8 / 全长 | **`a158f17a`** / `a158f17a1be1c89c8475f6712294a21cc0cf9dc2907809118415b8704b39a2ff` |
| 旧 SIGNED 回执 | `ARCH_A18_SECTION_5_3_BASELINE_SIGNED_20261026_ZH.md` sha8 **`e2d2b53e`** |
| 审稿（仍有效） | `ARCH_A18_SECTION_5_3_BASELINE_REVIEW_20261026_ZH.md` sha8 **`232a2295`** |
| 归档路径 | `output/data/_consumed/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE.a158f17a.SUPERSEDED.20261026T151859ET.ok` |
| 原因 | 旧票 `expires_et=16:00`；`forbid_overlap` 钉叶25 **16:15–17:45**；墙钟≈15:16 起空档不足逐年 ref_build 2014..2026；Eng **HOLD** |
| 新执行授权 | `output/data/ARCH_RUN_AUTH_DAILY_BASIC_A18_SECTION_5_3_BASELINE_EXEC.ok`（窗 **17:45–23:00 ET**；另票 SIGNED） |
| QUIET | **未挂** |
| 代跑 | **未**跑 ref_build / seed / 物化 |

## 动作

1. 复算 live 全长 sha = `a158f17a1be1c89c8475f6712294a21cc0cf9dc2907809118415b8704b39a2ff` → **MATCH**
2. 原子 `os.replace` 移入 `_consumed/…a158f17a.SUPERSEDED.20261026T151859ET.ok`
3. 确认 live 旧路径 **gone**
4. 同审稿 `232a2295` §3 另签 EXEC 窗（见 EXEC SIGNED 回执）

Eng 仍 HOLD 至新 `.ok` MATCH 且墙钟 ≥17:45；错开 16:15–17:45。≠X2；不报 Leo；live=false。

---
文档结束（Arch A18 §5.3 SUPERSEDED）
