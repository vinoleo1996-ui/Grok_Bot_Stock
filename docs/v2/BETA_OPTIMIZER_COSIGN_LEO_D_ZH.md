# Beta 对 Strategy OPTIMIZER Leo D DRAFT 共签回批

- **时间**：2026-10-14 08:06 ET
- **对象**：`docs/v2/STRATEGY_OPTIMIZER_PREREG_DRAFT_ZH.md`（≈08:08 ET Leo D 改写）+ `docs/v2/STRATEGY_OPTIMIZER_VS_B4_CAPADV_ZH.md`
- **配套**：`docs/v2/BETA_RISK_BUDGET_LEO_D_PENDING_ZH.md` · `docs/v2/BETA_RISK_BUDGET_OPTIMIZER_PREREG_ZH.md`
- **状态**：**SUPERSEDED**（2026-10-14 ≈08:11 ET）→ 现行共签见 `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`（**CONDITIONAL_COSIGN_CORE_CONC**）
- **历史备注**：Strategy ≈08:11 接线确认（β HARD |β−1|≤0.10）仍作历史记录；Leo D 数字路径（2.5%/40–70/±5%/±0.25σ）**不再**作为冻结/开跑路径
- **历史**：`BETA_OPTIMIZER_COSIGN_V1_ZH.md`（旧 ±2%/1%/中证全指）**仅作历史**，不构成对本 DRAFT 的共签
- **原则**：看优化器回测结果前共签；live=false；promotion_approved=false；**不跑**优化器；**不改** FROZEN 纸面

---

## 总裁决

| # | Strategy Leo D 提案 | Beta 裁决 | 一句话 |
|---|---|---|---|
| (1) | \(w_b\)=float_mktcap_hiliq；纸面仍报 vs 510300 | **ACCEPT** | 双口径：优化器自基准 / 纸面 Mandate 对照 |
| (2) | Size/MidCap ±0.25σ + Path A（连续 MidCap HARD + 分位桶） | **ACCEPT** | 单位必须 = 相对 \(w_b\) 的主动 z；严于旧 0.30 |
| (3) | 单票 100万 2.5%/60万 3.0%；\(N_{\mathrm{eff}}\) 40–70；行业 ±5% vs \(w_b\)；绝对 ≤35% | **ACCEPT** | Leo D 强制口径，与纸面袖套 6%/±8%/30–60 **分轨** |
| (4) | Σ=行业因子+特异；仅 L1 TC；INFEASIBLE 不松 HARD | **ACCEPT** | 保留降级序；禁 3/2 与双阈进优化器 |
| (5) | 拥挤度缺失 → ν=0；λ 仅密封窗同量纲标定后冻结 | **CONDITIONAL** | 接口 ACCEPT；λ/ν 冻点 = 标定闸通过后 |
| (6) | Core/Full 按 Strategy §5 | **ACCEPT** | Core 无域/快门卫/拥挤；Full 叠加；两臂均报 60万∧100万 |

**整体共签栏**：**SUPERSEDED**（原 CONDITIONAL_COSIGN_LEO_D）。现行见 `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md`。以下正文仅历史。

---

## (1) \(w_b\)=float_mktcap_hiliq；纸面仍报 510300 — **ACCEPT**

| 用途 | 基准 | 约束/报告 |
|---|---|---|
| **优化器 HARD / 主动暴露** | \(w_b\)=HI_LIQ 池内流通市值加权，日度 renormalize；标签 `wb_proxy=float_mktcap_hiliq` | Size/MidCap/行业/β 均相对此 \(w_b\) |
| **纸面轨 / Mandate 对照** | **510300** | 仍报 β∈[0.70, 1.00]、跟踪误差、波动；**不**充当优化器硬约束 |
| **明确不用** | 中证全指官方权、CSI300 权冒充 \(w_b\) | — |

**失败条件**：静默用 CSI300/全指成分权当 \(w_b\)，或用优化器 β 替代纸面 vs 510300 报告 → 本条共签作废。

---

## (2) Size/MidCap ±0.25σ + Path A — **ACCEPT**

| 项 | 冻结候选（PENDING→FROZEN 时沿用） |
|---|---|
| 线性 Size | \(e_{\mathrm{size}}=(w-w_b)'z_{\ln\mathrm{mcap}}\)，\(z\)=**可交易池截面** z-score；**\(\lvert e_{\mathrm{size}}\rvert\le 0.25\)** HARD |
| MidCap | \(z_{\mathrm{mid}}\)=截面标准化 \((\ln\mathrm{mcap}-\mu)^2\)；**\(\lvert e_{\mathrm{mid}}\rvert\le 0.25\)** HARD |
| Path A（V1 选用） | **同时**：① MidCap 连续暴露硬盒 ② 分位桶 \(\min(w_{\mathrm{P20}},w_{\mathrm{P80}})\le 0.05\)（相对可交易池 mcap 分位） |
| 相对旧值 | 旧 DRAFT ±0.30 → Leo D **±0.25**（更紧）；Beta 接受 |

**单位条件（共签前提）**：暴露必须是 **active z vs \(w_b\)**，不得改成绝对因子载荷或未减基准的组合加权 z。单位未定义开跑 → 本条视为未共签。

**Path B**：V1 **不启用**（Strategy 已选 Path A）；若日后改 Path B 须 dated + 证明蕴含防杠铃 + 重签。

---

## (3) 单票 / 宽度 / 行业 — **ACCEPT**（Leo D）

| 项 | PENDING 对齐值 | 相对纸面袖套 |
|---|---|---|
| 单票上限 | **100万：2.5%**；**60万：3.0%** | 纸面遗留 ≤6% **不动** |
| 单票下限 | 入选目标 ≥0.20% 否则归零 | — |
| 有效持仓 | \(N_{\mathrm{eff}}=1/\sum w_i^2\) 或权重大于下限的个数 ∈ **[40, 70]** | 纸面 30–60 **分轨** |
| 行业主动 | 申万一 **±5%** vs \(w_b\)；标签 `industry_wb_proxy=float_mktcap_hiliq` | 纸面 ±8% vs CSI300 **分轨** |
| 绝对行业帽 | **≤35%**（优化器兜底） | 纸面 HI_LIQ 袖套仍 ≤25% |

敏感度仅报告：单票统一 2.75%、行业 ±3%/±8%——**不得**用敏感度结果当正式 ACCEPT。

---

## (4) Σ / L1-only / INFEASIBLE 降级 — **ACCEPT**

### Σ
- **ACCEPT**：申万一级行业因子 + 对角特异风险（特异 = LW 对角或 60 日波动）。
- **禁止**：全池个股稠密 LW 无行业结构作正式 Σ。
- 停牌填 0 须披露偏差；不得未来 K 回填。

### TC
- **ACCEPT**：优化内唯一 TC = \(\lambda_{\mathrm{turn}}\|w-w_0\|_1\)。
- **删除**（优化器规格层）：3/2 冲击、双阈死区、staged builds。
- 引擎 `strategy_v1` 终判成本保留；单边换手硬帽 ≤40% NAV/再平衡（Strategy §3.6）可接受。

### INFEASIBLE 降级序（正式结果永不松 HARD）
沿用并确认：

1. 软罚 μ/ν → 临时置 0（`degrade=soft_zero`）。
2. Full 域预算 → 压回 0（贴 \(w_b\) 域份额）。
3. 权益总仓比例降仓 → 现金。
4. 仍不可行 → 该再平衡日沿用上期权重或全现金，`optimize_status=INFEASIBLE`。
5. 月内 INFEASIBLE ≥2 → 停跑升级主 Agent；阈值修订须 dated + 双签，另计试验。

**禁止**把「临时把行业改为 ±8% / Size 改为 0.50 / 单票改为 6%」的解记入正式臂。

---

## (5) 拥挤度 / λ 标定闸 — **CONDITIONAL**

| 项 | 裁决 |
|---|---|
| 拥挤度 schema + `missing_policy`：覆盖不足或缺失 → **ν=0**，打标 `crowd=off` | **ACCEPT** |
| ν 写死单点 | **CONDITIONAL**：仅密封窗 α–风险同量纲标定后；未标定 ν=0 |
| \(\lambda_{\mathrm{risk}}\) / \(\lambda_{\mathrm{turn}}\) | **CONDITIONAL / BLOCKING for FROZEN**：密封窗标定；产物 `calib_lambda_risk.json`、`calib_lambda_turn_{60,100}w.json` |
| 标定偷看 | **禁止**用 X2 收益挑 λ；标定只看约束可行性、换手、暴露 |

未标定就冻 λ/ν → Beta 对本条 **REJECT**（不得升 FULL / 不得 FROZEN）。

---

## (6) Core / Full — **ACCEPT**（对齐 Strategy §5）

| 臂 | 包含 | 报告 |
|---|---|---|
| **Core** | 优化器 + β HARD vs \(w_b\) + 行业 ±5% + Size/MidCap ±0.25σ Path A + L1；慢残差 α；**无**域预算、**无**快门卫、**无**拥挤度 | 60万 ∧ 100万；密封窗 + X2 |
| **Full** | Core + 域预算壳 ±3pp + 快/慢门卫 + 拥挤度接口（ν 按 §5） | 同上；与 Core **分开**报告 |

**禁止**：把 Full 增益回贴 Core 选参；用 Top-N / 50/25/25 作新主路径（纸面对照除外）。

与 Beta 风险预算 PENDING 表述一致：Core = β + Size/MidCap HARD + 行业（+L1）；Full = Core + 软风格/拥挤/域/快门卫（Strategy Full 模块全集）。

---

## B3 · 优化器 β 带宽（Strategy 待 Beta）

Strategy DRAFT 提案 \(\lvert\beta(w,w_b)-1\rvert\le 0.15\)。Beta **PENDING 提案**：

| 项 | 值 | 理由 |
|---|---|---|
| **优选 HARD** | \(\lvert\beta(w,w_b)-1\rvert\le\mathbf{0.10}\) | 自基准下 ±0.10 即可限制相对池的市场倾斜；与旧全指 ±0.10 同形、语义更干净 |
| 可接受备选 | ±0.15（Strategy 现提案） | 若密封窗可行域烟测显示 ±0.10 系统性 INFEASIBLE，dated 改 ±0.15 + 重签一行 |
| 纸面 | 仍报 vs 510300 ∈[0.70, 1.00] | 双口径不变 |

**本共签不把 ±0.15 写成已冻结 HARD**；Strategy 书面采纳 0.10 或说明选 0.15 后，本条升 ACCEPT。

---

## 与旧共签 / 纸面分轨

| 项 | 旧 CONDITIONAL（历史） | Leo D 本共签 | 纸面袖套（仍有效） |
|---|---|---|---|
| \(w_b\) | 中证全指（代理） | **float_mktcap_hiliq** | 报告 510300 |
| 行业 | ±2% | **±5%** | ±8% + 绝对 25% |
| 单票 / 宽度 | 1–1.5% / 100–400 | **2.5%/3.0% / 40–70** | ≤6% / 30–60 |
| Size | ±0.30 | **±0.25 + Path A** | 分位桶诊断 |
| TC | 双阈+3/2 | **仅 L1** | 引擎 strategy_v1 |
| 共签文件 | `BETA_OPTIMIZER_COSIGN_V1_ZH.md` | **本文件** | `BETA_RISK_BUDGET_OPTIMIZER_PREREG` §2 |

---

## 待 Strategy 确认（升 FULL_COSIGN_LEO_D）· **整节作废**：改走 CORE_CONC

1. 接受本文件六项 ACCEPT + β 带宽优选 0.10（或书面选 0.15）。
2. 密封窗标定文件路径写入 DRAFT 修订记录（λ_risk / λ_turn / ν）。
3. Path A 单位 = active z vs \(w_b\) 写死在实现与 DRAFT。
4. Arch 按 Leo D 终签（Beta 不替代）。

---

## Beta 共签栏

| 字段 | 值 |
|---|---|
| 状态 | **SUPERSEDED** → `BETA_OPTIMIZER_COSIGN_CORE_CONC_ZH.md` |
| Beta 签字 | QuantLab Beta · 2026-10-14 08:06 ET |
| Strategy 接线确认 | **DONE** 2026-10-14 ≈08:11 ET（历史；路径已被 CORE_CONC 取代） |
| 升 FULL 条件 | 上文 1–3 + Arch Leo D 终签 |
| live / promotion | false / false |
| 优化器回测 | **未跑** |
| 纸面 FROZEN | **未改** |

