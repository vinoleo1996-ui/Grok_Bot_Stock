# Beta 对 Strategy OPTIMIZER · 集中 Core 共签回批

- **时间**：2026-10-14 08:11 ET（初签）；**≈08:15 ET DRAFT 正文对齐复核 DONE**
- **对象**：Leo ≈08:09 集中 Core 口径；`STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md` ≈08:13–08:15 已写入 Core-concentrate（含 Slack 上限 + §3.5 两步/整手）
- **配套**：`BETA_RISK_BUDGET_LEO_D_PENDING_ZH.md`（历史）· 本文件取代其优化器路径
- **状态**：**CONDITIONAL_COSIGN_CORE_CONC**（结构 ACCEPT + DRAFT 正文对齐 DONE；**仍非** FULL_COSIGN / **仍非** FROZEN；剩余闸仅 Eng 密封窗 λ（NEW HARD）+ Leo/主 Agent 过关）
- **历史**：`BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` → **SUPERSEDED**（仅历史；Strategy ≈08:11 接线确认仍作历史记录有效）
- **原则**：看优化器回测结果前共签；live=false；promotion_approved=false；**不跑**优化器；**不改** FROZEN 纸面

---

## 总裁决

| # | 提案（Leo≈08:09 / Strategy 消息） | Beta 裁决 | 一句话 |
|---|---|---|---|
| (1) | 单票 100万 **5.0%** / 60万 **6.0%**；Neff **20–30** | **ACCEPT** | 与 capacity_adv Top-25 公平对照；宽于 Leo D |
| (2) | 两步截断重解 + 整手（科创板 200 股） | **ACCEPT** | §3.5 已写；支撑集\|w⁰\| ACCEPT；step2 破 HARD 且超 Slack → 失败 |
| (3) | 行业 ±8% vs \(w_b\)、绝对 ≤20%；Size/MidCap ±0.35σ + Slack | **ACCEPT** | Slack 上限 DRAFT 已写死（≈08:15 ACCEPT） |
| (4) | Core 主对标 capacity_adv Top-25；事件/B4 → Full | **ACCEPT** | Core/Full 分臂报告 |
| (R) | 保留：\(w_b\)=float_mktcap_hiliq；仅 L1；β \|β−1\|≤0.10；λ 密封窗；纸面 vs 510300；Path A 桶锁（配合 Size 0.35） | **ACCEPT** | 自 Leo D 结构保留项 |

**整体共签栏**：**CONDITIONAL_COSIGN_CORE_CONC**。① Strategy DRAFT 正文对齐 → **DONE ≈08:15 ET**。**不**升 FULL_COSIGN / **不** FROZEN，直至：Eng 密封窗 \(\lambda_{\mathrm{risk}}/\lambda_{\mathrm{turn}}\) 标定产物落盘（**NEW HARD**）+ Leo/主 Agent 过关。之后按 Leo：**先跑 Core**。

---

## (1) 单票 / 宽度 — **ACCEPT**

| 项 | CONDITIONAL 对齐值 | 相对 Leo D / 纸面 |
|---|---|---|
| 单票上限 | **100万：5.0%**；**60万：6.0%** | Leo D 2.5%/3.0% **作废**；纸面袖套 ≤6% 仍不动 |
| 有效持仓 | \(N_{\mathrm{eff}}\) 或权重大于下限个数 ∈ **[20, 30]** | Leo D 40–70 **作废**；贴近 capacity_adv Top-25 |
| 单票下限（支撑集） | 终解 ≥ **暂定 2.0%**（1.5–2.0% 敏感性；密封窗后钉点）→ **provisional ACCEPT** | DRAFT §3.4/§3.5 |

**理由**：集中 Core 主对标 capacity_adv Top-25，宽度/单票与该纸面袖套同量级才公平；不得用 40–70 / 2.5% 跑完再事后改宽。

---

## (2) 两步截断重解 + 整手 — **ACCEPT**（须书面算法）

**要求写入 Strategy DRAFT 的算法（共签前提）**：

1. **Step1**：连续权重求解（忽略整手），满足全部 HARD（含 β / Size / MidCap / 行业 / 单票 / Neff）与 L1 换手。
2. **Step2**：按交易所整手规则截断/取整（**科创板 = 200 股**；主板等按现行最小交易单位），对**残差权重**再优化（或投影），目标贴近 step1 解并尽量恢复 HARD。
3. **失败条件**：step2 后仍违反任一 HARD，且超出 **Slack** 预算 → `optimize_status=INFEASIBLE`（或 `LOT_HARD_FAIL`）；**不得**静默接受。
4. **禁止**：只做一次 round-to-lot 不重解；用未来成交价/未来 K 填停牌。

**≈08:15 复核**：DRAFT §3.5 已写两步+整手算法；支撑集主准则 **按 \(|w^{(0)}|\) 降序** → **ACCEPT**。本条算法前提 **CLOSED**。

---

## (3) 行业 / Size / Slack — **ACCEPT**

| 项 | 值 | 备注 |
|---|---|---|
| 行业主动 | 申万一 **±8%** vs \(w_b\)（`wb_proxy=float_mktcap_hiliq`） | Leo D ±5% **作废** |
| 绝对行业帽 | **≤20%** | 严于纸面 HI_LIQ 袖套 25%；优化器兜底 |
| 线性 Size | \(\lvert e_{\mathrm{size}}\rvert\le\mathbf{0.35}\)（active z vs \(w_b\)） | Leo D 0.25 **放宽** |
| MidCap | \(\lvert e_{\mathrm{mid}}\rvert\le\mathbf{0.35}\) | 同上 |
| Path A 桶锁 | **仍建议保留**：\(\min(w_{P20},w_{P80})\le 0.05\)（相对可交易池 mcap 分位） | 与 Size 0.35 并用，防杠铃 |
| **Slack** | DRAFT 已写死；**ACCEPT as written** | Size/MidCap ≤0.05σ；行业 ≤1pp；绝对20%/单票/Neff/β=0；超出 → INFEASIBLE |

**Slack 定义（ACCEPT as written ≈08:15）**：DRAFT §3.4 已写死——Size/MidCap 相对 HARD 额外 **≤0.05σ**（有效至多 ±0.40）；行业相对额外 **≤1pp**（至多 ±9%）；**绝对≤20% / 单票 / Neff / β = 0 Slack**。Slack = step2/数值误差有限软溢出，**不是**第二套更宽 HARD；披露用量；超出仍 INFEASIBLE。

---

## (4) Core / Full 对标 — **ACCEPT**

| 臂 | 范围 | 主对标 |
|---|---|---|
| **Core** | 优化器 + β HARD + 行业 ±8% + Size/MidCap ±0.35σ (+ Path A) + L1 + 两步整手；慢残差 α；**无**域预算 / **无**快门卫 / **无**拥挤（ν 接口可留，标定前 0） | **capacity_adv Top-25**（60万 ∧ 100万；密封窗 + X2） |
| **Full** | Core + 域/快门卫/拥挤/事件与 B4 模块 | 事件轨、B4 等进 Full；与 Core **分开**报告 |

**禁止**：把 Full 增益回贴 Core 选参；用 Leo D 宽度数字冒充本 Core。

---

## 保留项（自 Leo D 结构 · **ACCEPT**）

| 项 | 值 |
|---|---|
| \(w_b\) | HI_LIQ 池内流通市值加权 `float_mktcap_hiliq`；日度 renormalize |
| 纸面报告 | 仍报 vs **510300**；Mandate β 带 [0.70, 1.00] |
| β HARD vs \(w_b\) | \(\lvert\beta(w,w_b)-1\rvert\le\mathbf{0.10}\)（Strategy ≈08:11 已书面采纳；±0.15 仅密封窗系统性 INFEASIBLE 后备） |
| Σ | 行业因子 + 对角特异；禁稠密个股 LW 正式路径 |
| TC | **仅 L1** \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)；无 3/2、无双阈 |
| λ / ν | 密封窗同量纲标定后单点冻结；未标定 ν=0；**禁** X2 收益偷看 |
| INFEASIBLE | 不松 HARD 凑正式解；降级序沿用（软罚→域→降仓→沿用/现金） |

---

## 与 Leo D / 纸面分轨

| 项 | Leo D（**SUPERSEDED**） | **本共签 CORE_CONC** | 纸面袖套（仍有效） |
|---|---|---|---|
| 单票 / Neff | 2.5%/3.0% / 40–70 | **5.0%/6.0% / 20–30** | ≤6% / 30–60（诊断） |
| 行业 | ±5%；绝对≤35% | **±8%；绝对≤20%** | ±8% + 绝对 25% |
| Size/MidCap | ±0.25σ Path A | **±0.35σ + Slack**；Path A 仍建议 | 分位桶诊断 |
| 整手 | 未强调两步 | **两步截断重解 + 科创 200** | 引擎 strategy_v1 |
| 共签文件 | `BETA_OPTIMIZER_COSIGN_LEO_D_ZH.md` | **本文件** | `BETA_RISK_BUDGET_OPTIMIZER_PREREG` §2 |

---

## 升 FROZEN / 开跑闸（按 Leo：先 Core）

1. ~~Strategy DRAFT 正文对齐（含两步算法 + Slack 上限）~~ → **DONE ≈08:15 ET**（见下节）。
2. Eng 密封窗 \(\lambda_{\mathrm{risk}}\) / \(\lambda_{\mathrm{turn}}\) 标定产物落盘（**NEW HARD**；同量纲；不偷看 X2 收益）→ **仍 BLOCKING**。
3. Leo / 主 Agent 过关 → **仍 BLOCKING**。
4. 上述齐后升本文件 → 允许 **FROZEN** 后 **先跑 Core**（Full 另计）。Arch CORE_CONC 有条件终签已齐；Beta 不替代。

**当前仍为 CONDITIONAL_COSIGN_CORE_CONC**；**不是** FULL_COSIGN；**未 FROZEN**；**未跑**优化器。

---

## DRAFT 正文对齐 DONE（2026-10-14 ≈08:15 ET）

核验对象：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（mtime ≈08:13–08:15；横幅 Core-concentrate）。

| 项 | DRAFT 落笔 | Beta |
|---|---|---|
| 单票 / Neff | 100万 5.0% / 60万 6.0%；Neff 20–30 | **ACCEPT** |
| 行业 | 相对 \(w_b\) ±8%；绝对 ≤20% | **ACCEPT** |
| Size/MidCap | ±0.35σ HARD | **ACCEPT** |
| **Slack** | Size/MidCap ≤0.05σ（至 ±0.40）；行业 ≤1pp（至 ±9%）；绝对20%/单票/Neff/β = **0 Slack** | **ACCEPT as written** |
| 两步+整手 | §3.5：(a)全池初解 → (b)支撑集按 **\|w⁰\|** 前20–30 且 ≥暂定2.0% → (c)二次重解 → (d)整手（科创200） | **ACCEPT**（支撑集 \|w⁰\| **ACCEPT**） |
| 单票下限 | 暂定 **2.0%**（1.5–2.0% 敏感性；密封窗后钉点） | **provisional ACCEPT** pending sealed nail |
| \(w_b\) / β / L1 / Path A | float_mktcap_hiliq；\|β−1\|≤0.10；仅 L1；Path A 桶锁 | **ACCEPT**（保留） |

**阻塞「DRAFT 仍 Leo D」→ CLOSED。**

**剩余 FROZEN 闸（仅）**：
1. Eng 密封窗 \(\lambda_{\mathrm{risk}}/\lambda_{\mathrm{turn}}\) 标定产物（**NEW HARD**；旧 HARD 标定作废）
2. Leo / 主 Agent 过关

仍 **NOT FULL_COSIGN** / **NOT FROZEN** / **no run**。live=false。

---

## Beta 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **CONDITIONAL_COSIGN_CORE_CONC**（非 FULL_COSIGN） |
| Beta 签字 | QuantLab Beta · 2026-10-14 08:11 ET；对齐复核 ≈08:15 ET |
| Strategy DRAFT 正文对齐 | **DONE ≈08:15 ET**（5%/6%、Neff20–30、±8%/绝对20%、Size±0.35σ+Slack、§3.5 两步/\(|w^{(0)}|\)、下限暂定2.0%） |
| Leo D 共签 | **SUPERSEDED** |
| Strategy 接线确认（β0.10） | DONE ≈08:11 |
| 升 FROZEN 剩余闸 | **仅** Eng 密封窗 λ（NEW HARD）+ Leo/主 Agent 过关 |
| live / promotion | false / false |
| 优化器回测 | **未跑** |
| 纸面 FROZEN | **未改** |
