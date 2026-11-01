# Beta · Core ACCEPT 过门（PENDING）

- **时间**：2026-10-14 ≈08:22 ET
- **状态**：**PENDING** — **禁止**开跑 / 禁止填结果，直至 **Leo/主 Agent FROZEN** 且 Eng λ 可用后由授权臂执行
- **共签**：`BETA_OPTIMIZER_CORE_FINAL_COSIGN_ZH.md` = **PASS_PENDING_ENG_LAMBDA**
- **HARD**：`BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`（不变）
- **live / promotion**：false / false

> **横幅**：本文只定义 **冻后跑完** 如何判 ACCEPT / FAIL。当前无优化器净值；**不发明** λ 或回测数。

---

## 0. 何时可跑（前置闸）

| # | 条件 | 现状 |
|---|---|---|
| P1 | Strategy DRAFT 规格终签（HARD+双口径+月末调仓+λ_turn 中心） | Beta **PASS_PENDING_ENG_LAMBDA** ✅ |
| P2 | Eng `calib_lambda_*.json` 非 null + meta；密封窗；月末 cadence；未用 X2 收益选参 | **BLOCKED**（FAILED / λ=null） |
| P3 | Leo/主 Agent：**FROZEN** | **待** |
| P4 | Stage1：只跑 Core；纸面底仓不动 | 写死 |

P2∧P3 齐后才进入下列过门计量。

---

## 1. 报告臂与双口径（强制）

对 **60万 ∧ 100万** 各出：

| 口径 | 构造 | 角色 |
|---|---|---|
| **①** | 优化器股票权重 → 100%（无 510300） | 分解；**不得**用其绝对 MDD/Sharpe 比 capadv 总账 |
| **②** | 股票袖 **80%** + **510300 20%** | **主对标表** vs capacity_adv 纸面总账 |

窗口：密封窗 **披露**；正式 ACCEPT 窗 = **X2**（样本内，不作晋级）。年化 **244**。

再平衡：`month_end_plus_first_last`（与 capacity_adv）；禁另试周频。

---

## 2. 主指标过门（相对同口径 capacity_adv）

**主排序 / ACCEPT 核心**：在口径 **②** 上，相对同 AUM capacity_adv：

| 门 | 指标 | ACCEPT（PENDING 定义） | 备注 |
|---|---|---|---|
| G-S | **Sharpe** | Core② Sharpe **≥** capadv 同窗同 AUM Sharpe − **0.05**（容差） | 主 |
| G-M | **MDD** | Core② MDD **不劣于** capadv 同窗同 AUM MDD **超过 2pp**（更负超 2pp → FAIL 关注） | 主；且见 G-M25 |
| G-IR | **IR** | Core② vs 同口径基准的 IR **≥** capadv 同口径 IR − **0.05** | 主；公式须标注 |
| G-C | CAGR | **必报**；**非**主排序；不作单独 ACCEPT 硬切 | 次 |
| G-Cal | Calmar / 胜率 | 必报 | 次 |

α 沟通：抬 Sharpe / 压 MDD（目标带）；**不作** α≥8%+ 硬门槛。

**禁止**：用口径①的绝对 MDD/Sharpe 宣告击败 capadv。

---

## 3. 约束 / 结构硬闸（跑后必须满足）

| 门 | 项 | ACCEPT |
|---|---|---|
| G-N | Neff（或权重大于下限个数） | ∈ **[20, 30]**（再平衡日中位数落带；系统性偏离 → FAIL） |
| G-βw | β vs \(w_b\) | \|β−1\|≤**0.10**（披露 Slack/后备若用） |
| G-βp | 纸面 β vs 510300（口径②组合） | 落在报告带 **[0.70, 1.00]**（越界 → 披露+复核，非自动松 HARD） |
| G-I | 行业 | 相对 \(w_b\) **±8%**；绝对 **≤20%**（Slack 行业 ≤1pp 须披露用量） |
| G-Sz | Size / MidCap | \|e\|≤**0.35σ**（+Slack ≤0.05σ 披露） |
| G-M25 | MDD | **≤25%** 硬关注（破 → FAIL/复核）；另报是否 **≤15%** |
| G-Lot | 两步整手 | 报截断前后持仓数；**LOT_HARD_FAIL = 0** 才可 ACCEPT |
| G-TC | 成本 / 换手 | X2 **观测必报**；**非**事前硬闸；λ_turn 标定中心=月双边≈50% 或年化单边 4–6×（优先对齐 capadv）；≤1.3%/AUM = stretch 观察 |

单票：100万 ≤5% / 60万 ≤6%（终解）。

---

## 4. ACCEPT 汇总规则（冻后）

**ACCEPT（Stage1 Core）** 当且仅当：

1. G-N、G-βw、G-I、G-Sz、G-Lot 全过（HARD 结构）；  
2. G-M25 未破 25%；  
3. 主表口径②上 G-S ∧ G-M ∧ G-IR 按上表容差通过（相对 capadv）；  
4. ①② 双套净值均已落盘；主结论只用②；  
5. 成本/换手已披露（G-TC 观测）。

任一 HARD 结构闸失败 → **FAIL**（不得靠放宽 HARD 补救）。主指标容差边缘 → **CONDITIONAL / 报主 Agent**，不自动晋级纸面。

**明确不做**：替换 FROZEN 纸面；Stage2 Full；Stage3 换垫仓；live=true。

---

## 5. 对照路径

| 路径 | 用途 |
|---|---|
| capacity_adv Top-25 纸面（同 AUM、同窗） | **主对标**（对口径②） |
| Core① | 分解 |
| B4 | **不对标 Core**（Full） |

---

## 6. 修订

| 时间 | 内容 |
|---|---|
| ≈08:16 | 初稿意图（过门预写） |
| ≈08:21 | 双口径 + Sharpe/MDD/IR 主指标 |
| ≈08:22 | 折叠终签：月末 cadence、λ_turn 中心、成本=观测；状态仍 PENDING |

**禁跑至 Leo FROZEN。**
