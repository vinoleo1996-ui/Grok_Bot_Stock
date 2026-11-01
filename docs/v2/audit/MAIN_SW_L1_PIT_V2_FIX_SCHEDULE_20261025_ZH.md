# 主裁：申万 L1 PIT v2 实修排期

- 时刻：2026-10-25 12:32 ET（America/New_York）
- 角色：主 Agent → QuantLab Data（Arch 旁收）
- live=false · 禁消费 `9e4359f9` · SUSPEND 维持至双通

## 前置

| 项 | sha8 |
|---|---|
| 方案 | `a390342f` |
| Arch 审 | `32a69e25` PASS_WITH_CONDITIONS |

## 排期

| 步 | 何时 | 做什么 |
|---|---|---|
| **准备** | **即日起**（今日可） | 写 code-change 包 + selftest/dry 计划；**不申**实修 `.ok`；**不**改生产 PIT |
| **P0 双开闭合** | **最早 周一 10-27 双通两轮齐后**（08:30+10:50 ET 皆过）再请 Arch 签 dry→execute | 错开叶25 r3 实峰窗 / 叶27 内存窗 |
| **P1 bak235** | P0 闭合并 Arch 收讫后 | 离线恢复；另签 |
| **P2** | RELAY 解冻后 | 等中转 |

## 红线

- 修 PIT **≠** 解阻叶25 / X2
- 错开纸面与叶内存峰 QUIET 窗
- 2027 日历：ARCHIVE_ONLY；正式 pull 等中转
