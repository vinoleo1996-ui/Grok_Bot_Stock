# 主裁：叶25 mem_probe r2 实峰短窗确认

- 时刻：2026-10-25 12:25 ET（America/New_York）
- 角色：主 Agent → QuantLab AI
- live=false · promotion_approved=false · **≠ X2.ok**

## 确认

| 项 | 值 |
|---|---|
| `.ok` | `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.ok` |
| `.ok` sha256 | `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279`（sha8 `cd230f9c`） |
| 审阅 | `1b706f9b…` PASS_WITH_CONDITIONS |
| 窗 | **2026-10-25 12:25–13:05 ET**（expires 13:07 ET） |
| 脚本 | `9dfe173a…` · wrapper v5 `4240ce82…` |
| C4/stop/hard | 1331200 / 1484800 / 1536000 |
| 宇宙/块 | HI_LIQ · month 2024-06-03→2024-06-28 · chunk0 |

## 令 AI（唯一执行）

1. **prelaunch**（`.ok` 钉条）：`RESEARCH_QUIET.lock` 已挂；healthz quiet=true（90s 内）→ wait≥15s → 再检 gen/snapshot/kline 空、MemAvailable≥2.5GiB、script sha MATCH。
2. 仅跑 `.ok` 内 `approved_cmd`（经 wrapper v5）；**单次**；`ai_no_retry`；破帽/ABORT **禁自抬帽重试**。
3. 跑完交回执（peak_kb、exit、日志路径、`.ok` 消费态）；**禁**申 X2.ok；**禁**自 lift QUIET（主/Arch 收尾）。
4. 叶27 分块包 `262f9bf6` **排队**，本窗不抢。

## 红线

- 禁 FULLA / both / 复用 `1c32ab1e` / 抬帽 / 读收益选号
- Arch 不代跑；主不代跑
