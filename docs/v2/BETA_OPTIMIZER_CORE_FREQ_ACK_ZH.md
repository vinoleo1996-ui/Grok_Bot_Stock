# Beta：OPTIMIZER Core 频率/换手确认（ACK）

- **时间**：2026-10-14 ≈08:24 ET  
- **对象**：`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` ≈08:22 Leo 终签拍板  
- **配套**：Arch `FINAL_COSIGN_PASS` ≈08:23；Beta 浓缩 HARD + §5.1–5.3 双口径共签仍有效  
- **状态**：**ACK / ACCEPT**（不升格替代 FULL；FROZEN 仍卡 Eng λ≥20 落盘）  
- **live=false** · 本文件不触发开跑  

## 一行确认（三项均 ACCEPT）

| # | 项 | Beta |
|---|---|---|
| (1) | 调仓 cadence = `month_end_plus_first_last`（与 capacity_adv 一致；密封窗**禁止**周频/月末双试） | **ACCEPT** |
| (2) | \(\lambda_{\mathrm{turn}}\) 密封窗标定中心 = 月双边 ≈50% 或年化单边 4–6×；**优先**对齐同窗同 AUM capacity_adv 引擎换手中位数 ±20%；X2 实际成本/换手 = **观测非硬保** | **ACCEPT** |
| (3) | 双口径①纯股票 100% + ②80/20+510300；主结论用②；主指标 Sharpe/MDD/IR | **ACCEPT**（不变） |

**开跑闸**：Eng λ（`λ_risk` / `λ_turn`，NEW HARD + 两步 + 本换手中心）产物齐全后，Strategy 可按 Leo 指令盖 **FROZEN** 并开跑 **Core**（Stage1；双口径报告）。Beta 不反对。

