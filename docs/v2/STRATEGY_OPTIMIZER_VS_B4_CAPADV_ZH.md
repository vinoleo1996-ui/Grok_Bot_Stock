# 优化器路径 vs 现行 B4 / capacity_adv（Strategy，2026-10-14）

- **对标双口径（主 Agent≈08:19 / Arch）**：Core **只**对标 capadv；必报①纯股票 + ②80/20+510300；主指标 **Sharpe/MDD/IR**；禁用①的绝对 MDD 直接比 capadv。
- 依据：Leo 07:56–07:58 范式；≈08:03 Leo D；**≈08:09 ET Leo Core-concentrate（via 主 Agent）** → 配套草稿按集中度改写（`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`，**仍 DRAFT**）。
- 目的：说清「停 Top-N 主路径」后，新构造与现行纸面差在哪里。
- **现行纸面轨不动**。live/promotion=false。

---

## 1. 总览（Leo Core-concentrate 后）

| 维度 | capacity_adv（纸面核心） | B4（纸面第二轨） | OPTIMIZER_V1（拟议；DRAFT） |
|---|---|---|---|
| 候选池 | mid_large **top300** | 同左三腿池 | **HI_LIQ_V1.1**（ADV≥1亿）；裸 FULLA 不进纸面 |
| 构造 | 分数 **Top-N ≈25** + **510300 固定 20%** | **50/25/25** 袖套 + conc Top-N | **二次型优化器** + **两步截断**（全池→支撑集20–30→重解→整手） |
| \(w_b\) | 常对照 510300 | 同左 | **池内流通市值加权**（不用中证全指）；纸面仍**报告** vs 510300 |
| 持仓宽度 | ~25 + ETF | 个位数–十余只 | **Neff 20–30**（公平 vs Top-25） |
| 单票上限 | 袖内 ≤4%；组合实践更宽 | 组合 ≤6% | **100万 5.0% / 60万 6.0%**；支撑集地板 **1.5–2.0%** |
| 行业 | absolute（HI_LIQ 拟 25%） | 随腿漂 | 相对 \(w_b\) **±8%**；**绝对 ≤20%** |
| Size / 防杠铃 | 未系统 | 未系统 | **±0.35σ** 线性+MidCap HARD；**Path A**；**Slack** 防无解（仅 Size/MidCap） |
| 风险 Σ | 隐式 | 隐式 | 行业因子 + 特异风险（禁稠密 LW） |
| 成本（优化内） | 无（引擎事后） | 无 | **仅** \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)（**无** 3/2、**无**双阈） |
| 标定 | 无优化器 λ | 无 | **密封窗先标定**再报 X2；禁盲冻 λ；**NEW HARD** |
| 消融 / 对标 | — | — | **Core↔capadv 双口径**（纯股票 + 80/20+510300）；**Full↔B4 延后**；冻后先只跑 Core |
| 角色 | **冻结纸面核心** | **冻结纸面第二轨** | **研究主路径候选**（未 FROZEN） |

---

## 2. capacity_adv：现行做法

- top300 上按分取前 ≈25；510300 固定 20%；袖内单票 ≤4%。
- FULLA 裸腿 X2 MDD 破 25% → 裸 FULLA 不进纸面（Leo 07:42）。

**与优化器（Core-concentrate）**：不再机械排前 25；α 覆盖 HI_LIQ 全池；经两步截断落到 **Neff 20–30**；单票 **5%/6%**。对标须 **双口径**：①纯股票 100%；②股票 80%+510300 20%（与 capadv 同形，**主结论用②**）；**禁止**满仓 HI_LIQ 取消 510300 的单稿当对标。Stage1 纸面底仓不动。

---

## 3. B4：现行做法

- 50/25/25 = capacity_adv / earnings_event / insider_increase；conc 后纸面确认；后续未稳胜 → **不替换 B4**（直至优化器晋级明示）。

**与优化器（Core-concentrate）**：**Core** 用单一慢残差 α + 约束 + L1 + 两步截断；**事件腿对标 B4 延后到 Full**（门卫，不再固定袖比）；行业 ±8% vs 池内 \(w_b\)、绝对 ≤20%。

---

## 4. 构造公式对照

| | 现行 B4 / capadv | OPTIMIZER_V1（Core-concentrate） |
|---|---|---|
| 权重 | \(w\propto\mathrm{TopN}(\mathrm{score})\) 或 \(\sum_k\pi_k w^{(k)}\) | \(\arg\max_w\,w'\alpha-\lambda_{\mathrm{risk}}(w-w_b)'\Sigma(w-w_b)-\lambda_{\mathrm{turn}}\|w-w_0\|_1\) → 支撑集截断 → 重解 → 整手 |
| \(w_b\) | （对照）510300 | 池内 float_mktcap |
| 行业 | absolute / 袖 | ±8% vs \(w_b\)；绝对 ≤20% |
| 换手惩罚 | 无优化内 | **仅 L1** |
| 宽度 | ~25 / 袖混合 | Neff **20–30** |

---

## 5. Core vs Full（相对纸面）

| 臂 | 做什么 | 相对纸面 |
|---|---|---|
| **Core** | 优化器 + 行业/Size + L1 + 两步截断（20–30） | **主对标并拟取代** capacity_adv Top-25；**冻后先只跑** |
| **Full** | Core + 域预算壳 + 快/慢门卫（事件）+ 拥挤度 | **事件腿 vs B4 延后**；分开报，不回贴选参 |

---

## 6. 迁移原则（未执行）

1. 纸面 B4 / capacity_adv 继续日终，直至 Leo 明示优化器晋级。
2. Leo D 宽度数字（2.5%/3%、40–70、±5%、±0.25）及更旧「中证全指 ±2%/双阈+3/2」**作废**。
3. 优化器确认前：不改冻掩码、不跑优化器 backtest、不计晋级。
4. 晋级若发生：新 FROZEN + 密封窗标定（NEW HARD）+ X2 **Core** + Beta/Arch **按 Core-concentrate 重签** + Eng 退市披露；Full 稍后。

---

## 7. 文件

| 文件 | 用途 |
|---|---|
| `STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` | Core-concentrate 全规格 DRAFT |
| 本文 | vs B4 / capacity_adv |
| `STRATEGY_OPTIMIZER_LAMBDA_CALIB_HANDOFF_ZH.md` | Eng λ 交接（NEW HARD） |
| `STRATEGY_HI_LIQ_SUBSET_PREREG_V1_1_ZH.md` | 可交易池掩码（拟复用） |
| `ARCH_OPTIMIZER_V1_COSIGN_LEO_D_ZH.md` / `BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` | Leo D 共签；**SUPERSEDED，须重签** |

## 修订

| 时间 | 内容 |
|---|---|
| 2026-10-14 ≈08:00 ET | 初版（旧数值）。 |
| 2026-10-14 ≈08:08 ET | Leo D：\(w_b\)/±0.25σ/单票/N_eff/±5%/仅 L1/Core·Full。 |
| **2026-10-14 ≈08:13 ET** | **Core-concentrate**：Neff20–30、单票5%/6%、行业±8%/绝对20%、Size±0.35σ+Slack、两步截断、Core↔capadv、Full↔B4 延后。 |

## 再平衡 / 换手（Leo ≈08:20 终签）

- Core 与 capacity_adv **同日历**：`month_end_plus_first_last`（禁密封窗试周频）。
- \(\lambda_{\mathrm{turn}}\) 标定优先对齐 capacity_adv 同窗换手中位数 ±20%；中心目标月双边≈50%（年化单边 4–6×）；B4 对照。
- 实际换手与成本 = X2 观测，非事前硬保。
